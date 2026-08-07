from __future__ import annotations

import json
from pathlib import Path

import pytest

from app import rag_service
from app.solution_knowledge import (
    OUTPUT_STRUCTURES_FILE,
    build_solution_query,
    find_inference_patterns,
    load_inference_patterns,
    load_output_structures,
    load_solution_workflows,
    output_structure_context,
    output_structure_for,
    select_solution_workflows,
    solution_workflow_context,
)
from scripts.promote_batch09_runtime import (
    build_runtime_payloads,
    validate_source_refs,
)


def _jsonl_records(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_runtime_payloads_are_reproducible_from_candidate_batch() -> None:
    generated = build_runtime_payloads()
    for path, expected_records in generated.items():
        assert _jsonl_records(path) == expected_records


def test_output_structures_are_valid_and_map_each_solution_once() -> None:
    structures = load_output_structures()
    assert len(structures) == 10
    assert [item.solution_pattern_id for item in structures] == [
        f"SP-{index:02d}" for index in range(1, 11)
    ]
    assert output_structure_for("SP-03", structures=structures).name == "Einsatznotiz"
    assert output_structure_for("SP-99", structures=structures) is None


def test_output_context_never_forwards_example_values() -> None:
    context = output_structure_context(output_structure_for("SP-03"))
    assert context["status"] == "runtime_approved"
    assert context["human_review"]
    assert "example_value" not in json.dumps(context, ensure_ascii=False)
    assert context["required_fields"] == [
        "Für wen",
        "Was gemacht wurde",
        "Wie lange",
    ]


def test_missing_output_structure_has_safe_visible_fallback() -> None:
    context = output_structure_context(None)
    assert context["status"] == "missing"
    assert context["fields"] == []
    assert "noch keine freigegebene" in context["notice"]


def test_physical_assignment_fields_require_human_confirmation() -> None:
    structure = output_structure_for("SP-04")
    assert structure is not None
    assert all(field.requires_human_input for field in structure.fields)


def test_inference_pattern_remains_an_unconfirmed_hypothesis() -> None:
    patterns = load_inference_patterns()
    selected = find_inference_patterns(
        ["PF-08"], channels={"sprache", "foto", "bon"}, patterns=patterns
    )
    assert selected
    assert all(item.hypothesis_status == "must_be_confirmed" for item in selected)
    assert selected[0].verification_question.endswith("?")
    assert not hasattr(selected[0], "confirmed_user_fact")


def test_solution_workflows_separate_roles_and_exclude_sp04_as_positive() -> None:
    workflows = load_solution_workflows()
    assert len(workflows) == 28
    assert {
        step.actor for workflow in workflows for step in workflow.target_workflow
    } <= {"user", "ai", "software_rule", "human"}
    assert select_solution_workflows("SP-04", workflows=workflows) == []
    selected = select_solution_workflows(
        "SP-03",
        business_type="hausmeisterservice",
        channels={"sprache", "foto", "bon"},
        workflows=workflows,
    )
    assert selected[0].workflow_id == "SW-SP03-01"


def test_solution_context_does_not_leak_internal_ids_or_sources() -> None:
    context = solution_workflow_context(select_solution_workflows("SP-03"))
    rendered = json.dumps(context, ensure_ascii=False)
    assert "SW-SP" not in rendered
    assert "SRC-" not in rendered
    assert "source_refs" not in rendered


def test_solution_query_uses_only_targeted_confirmed_dimensions() -> None:
    query = build_solution_query(
        problem_family_ids=["PF-08", "PF-12"],
        solution_pattern_id="SP-03",
        bottleneck="Einsatzdaten werden erst abends zusammengeführt",
        channels={"sprache", "foto", "bon"},
        business_type="hausmeisterservice",
    )
    assert "PF-08" in query and "SP-03" in query
    assert "Einsatzdaten" in query
    assert "bon, foto, sprache" in query
    assert "hausmeisterservice" in query


def test_solution_index_contains_only_runtime_approved_positive_workflows() -> None:
    chunks = rag_service.load_solution_workflow_chunks()
    assert len(chunks) == 27
    assert all(chunk.chunk_type == "solution_workflow" for chunk in chunks)
    assert all(chunk.metadata["quality_status"] == "runtime_approved" for chunk in chunks)
    assert all(chunk.metadata["solution_pattern_id"] != "SP-04" for chunk in chunks)
    assert all("evaluation" not in chunk.source_file.casefold() for chunk in chunks)


def test_evaluation_file_cannot_be_loaded_as_runtime_knowledge() -> None:
    evaluation_path = (
        Path(__file__).resolve().parents[1]
        / "knowledge"
        / "evaluation"
        / "batch_09_evaluation_cases.jsonl"
    )
    with pytest.raises(ValueError, match="Evaluationen"):
        load_output_structures(evaluation_path)


def test_batch09_evaluations_stay_research_proposed_and_excluded() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "knowledge"
        / "evaluation"
        / "batch_09_evaluation_cases.jsonl"
    )
    records = _jsonl_records(path)
    assert len(records) == 30
    assert {record["label_status"] for record in records} == {"research_proposed"}
    assert {record["index_policy"] for record in records} == {
        "exclude_from_all_rag_indexes"
    }


def test_false_source_reference_is_rejected() -> None:
    with pytest.raises(ValueError, match="SRC-999"):
        validate_source_refs([{"source_refs": ["SRC-999"]}], {"SRC-001"})


def test_output_structure_loader_rejects_unknown_solution_pattern(tmp_path: Path) -> None:
    record = _jsonl_records(OUTPUT_STRUCTURES_FILE)[0]
    record["solution_pattern_id"] = "SP-99"
    path = tmp_path / "outputs.jsonl"
    path.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Ungültiges Runtime-Wissen"):
        load_output_structures(path)
