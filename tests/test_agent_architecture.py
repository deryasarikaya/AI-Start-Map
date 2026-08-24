from __future__ import annotations


import json
from pathlib import Path

import pytest

import app.rag_service as rag_service
from app.services import analysis_service
from app.agent_config import AGENT_HEURISTICS
from app.agent_service import (
    FactRecord,
    RagEvidence,
    evaluate_research_trace,
    extract_process_state,
)


ROOT = Path(__file__).resolve().parents[1]


def _confirmed_fact(value: str) -> FactRecord:
    return FactRecord(
        value=value,
        status="confirmed",
        origin="user_confirmation",
        turn_id="test",
    )


def test_diagnostic_and_agent_corpora_are_separate_and_complete() -> None:
    curated = rag_service.load_curated_chunks()
    diagnostic = rag_service.load_diagnostic_chunks()
    agent = rag_service.load_agent_pattern_chunks()
    assert len(curated) == 103
    assert len(diagnostic) == 626
    assert len(agent) == 205
    assert not {chunk.chunk_id for chunk in diagnostic} & {
        chunk.chunk_id for chunk in agent
    }


def test_all_indexable_chunks_keep_normalized_metadata() -> None:
    required = {
        "batch_id",
        "source_ids",
        "source_strength",
        "content_origin",
        "is_primary_evidence",
        "industry",
        "process_type",
        "digital_maturity_level",
        "pattern_ids",
        "guardrail_ids",
    }
    for chunk in [
        *rag_service.load_diagnostic_chunks(),
        *rag_service.load_agent_pattern_chunks(),
    ]:
        assert required <= chunk.metadata.keys()
        assert "evaluation" not in chunk.source_file.casefold()


def test_all_91_evaluations_are_outside_indexes() -> None:
    legacy = json.loads(
        (ROOT / "knowledge/evaluation/cases_ten_kmu.json").read_text(encoding="utf-8")
    )["cases"]
    batch_03 = json.loads(
        (
            ROOT
            / "knowledge/evaluation/cases_rb03.json"
        ).read_text(encoding="utf-8")
    )
    batch_04_root = json.loads(
        (
            ROOT
            / "knowledge/evaluation/cases_rb04_agent.json"
        ).read_text(encoding="utf-8")
    )
    batch_07_root = json.loads(
        (ROOT / "knowledge/evaluation/cases_rb07_guardrail.json").read_text(
            encoding="utf-8"
        )
    )
    batch_07 = batch_07_root["cases"]
    indexed_text = " ".join(
        chunk.content
        for chunk in [
            *rag_service.load_diagnostic_chunks(),
            *rag_service.load_agent_pattern_chunks(),
        ]
    )
    assert (
        len(legacy) + len(batch_03) + len(batch_04_root["cases"]) + len(batch_07)
        == 90
    )
    assert batch_04_root["indexing_policy"] == "NEVER_INDEX"
    for evaluation_id in [
        *(item["evaluation_id"] for item in legacy),
        *(item["evaluation_id"] for item in batch_03),
        *(item["case_id"] for item in batch_04_root["cases"]),
        *(item["id"] for item in batch_07),
    ]:
        assert evaluation_id not in indexed_text


def test_duplicate_audit_has_no_duplicate_ids_or_exact_content() -> None:
    diagnostic = rag_service.audit_duplicates(rag_service.load_diagnostic_chunks())
    agent = rag_service.audit_duplicates(rag_service.load_agent_pattern_chunks())
    assert diagnostic.duplicate_ids == ()
    assert diagnostic.exact_content_duplicates == ()
    assert agent.duplicate_ids == ()
    assert agent.exact_content_duplicates == ()
    assert agent.near_duplicates


def test_test_indexes_build_without_touching_production(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ein Testindex darf den produktiven nicht anfassen.

    Der produktive Index ist ein gebautes Artefakt und liegt nicht im
    Repository. Wo es ihn nicht gibt, gibt es auch nichts zu beschädigen —
    dann hat dieser Test nichts zu prüfen und sagt das, statt an einer
    fehlenden Datei zu scheitern.
    """

    if not rag_service.INDEX_FILE.is_file():
        pytest.skip(
            "Kein gebauter Produktionsindex vorhanden — "
            "scripts/build_index.py baut ihn."
        )
    production_mtime = rag_service.INDEX_FILE.stat().st_mtime_ns

    def fake_embeddings(texts: list[str]) -> list[list[float]]:
        return [
            [float((index % 7) + 1), float((len(text) % 11) + 1), 1.0]
            for index, text in enumerate(texts)
        ]

    monkeypatch.setattr(rag_service, "embed_texts", fake_embeddings)
    diagnostic_directory = tmp_path / "diagnostic"
    agent_directory = tmp_path / "agent"
    rag_service.build_vector_index(
        force=True,
        index_kind="diagnostic",
        output_directory=diagnostic_directory,
    )
    rag_service.build_vector_index(
        force=True,
        index_kind="agent",
        output_directory=agent_directory,
    )
    assert rag_service.validate_index(
        diagnostic_directory, expected_kind="diagnostic"
    )["chunk_count"] == 634
    assert rag_service.validate_index(
        agent_directory, expected_kind="agent"
    )["chunk_count"] == 205
    assert rag_service.INDEX_FILE.stat().st_mtime_ns == production_mtime


def test_state_keeps_user_facts_inferences_and_rag_evidence_separate() -> None:
    state = extract_process_state(
        answers={
            "actual_steps": json.dumps(["Annehmen", "Bearbeiten", "Übergeben"]),
            "problem_overview": "Wir suchen oft nach dem Zettel.",
            "roles_systems_and_handoffs": "Die Inhaberin nutzt Papierzettel.",
            "business_object_and_result": "Ein Reparaturauftrag.",
            "rules_and_exceptions": "Bei Zusatzarbeit wird nachgefragt.",
            "approval_and_success": "Den Preis gibt die Inhaberin frei.",
        },
        selected_process={
            "process_name": "Annahme bis Übergabe",
            "start_event": "Ein Gegenstand kommt an",
            "end_event": "Der Gegenstand wird übergeben",
        },
        rag_evidence=[
            RagEvidence(
                chunk_id="internal-pattern",
                chunk_type="diagnostic_pattern",
                content="Ein Vergleichsmuster, kein Nutzerfakt.",
            )
        ],
    )
    confirmed_values = {fact.value for fact in state.confirmed_user_facts}
    assert "Ein Vergleichsmuster, kein Nutzerfakt." not in confirmed_values
    assert state.rag_evidence[0].chunk_id == "internal-pattern"
    assert state.professional_inferences
    assert state.digital_maturity is not None
    assert state.digital_maturity.value == "0"


def test_central_demo_heuristics_are_bounded() -> None:
    assert AGENT_HEURISTICS.normal_follow_up_minimum == 0
    assert AGENT_HEURISTICS.normal_follow_up_maximum == 2
    assert AGENT_HEURISTICS.complex_follow_up_maximum == 3
    assert AGENT_HEURISTICS.maximum_visible_follow_ups == 4
    assert AGENT_HEURISTICS.maximum_agent_rounds > 4
    assert AGENT_HEURISTICS.maximum_tool_rounds > 0


def test_all_batch_04_evaluation_actions_match_policy() -> None:
    evaluation_root = json.loads(
        (
            ROOT
            / "knowledge/evaluation/cases_rb04_agent.json"
        ).read_text(encoding="utf-8")
    )
    mismatches = []
    for case in evaluation_root["cases"]:
        actual = evaluate_research_trace(
            case["current_agent_state"], case["latest_user_message"]
        )
        if actual != case["expected_next_action"]:
            mismatches.append((case["case_id"], actual, case["expected_next_action"]))
    assert mismatches == []


@pytest.mark.parametrize(
    ("description", "expected_level"),
    [
        ("Wir haben nur Papierzettel und keine Auftragsdaten.", "0"),
        ("Der Monteur hat nur ein Smartphone und einen Kalender.", "1"),
        ("Die Aufträge stehen in einer zentralen Software.", "2"),
    ],
)
def test_digital_maturity_is_inferred_without_becoming_a_user_fact(
    description: str, expected_level: str
) -> None:
    state = extract_process_state(
        answers={"roles_systems_and_handoffs": description},
        selected_process={
            "process_name": "Auftrag",
            "start_event": "Auftrag kommt an",
            "end_event": "Auftrag ist abgeschlossen",
        },
    )
    assert state.digital_maturity is not None
    assert state.digital_maturity.value == expected_level
    assert state.digital_maturity.origin == "agent_inference"


def test_uncalibrated_source_strength_penalty_is_neutralized() -> None:
    high = rag_service.KnowledgeChunk(
        chunk_id="high",
        chunk_type="diagnostic_pattern",
        title="High",
        content="High",
        source_file="test",
        metadata={"source_strength": "high"},
    )
    low = rag_service.KnowledgeChunk(
        chunk_id="low",
        chunk_type="diagnostic_pattern",
        title="Low",
        content="Low",
        source_file="test",
        metadata={"source_strength": "low"},
    )
    ranked = rag_service._rank_with_source_strength(
        [0.80, 0.85], [0, 1], [high, low]
    )
    assert [chunk.chunk_id for chunk in ranked] == ["low", "high"]


def _retrieval_chunk(chunk_id: str, chunk_type: str) -> rag_service.KnowledgeChunk:
    return rag_service.KnowledgeChunk(
        chunk_id=chunk_id,
        chunk_type=chunk_type,
        title=chunk_id,
        content=f"Vergleichswissen für {chunk_type}",
        source_file="knowledge/test.jsonl",
        metadata={"source_strength": "high"},
    )


def test_analysis_retrieval_reserves_each_decision_relevant_chunk_type() -> None:
    required = rag_service.PHASE_TYPES["analysis"]["required"]
    assert required == (
        "diagnostic_pattern",
        "automation_pattern",
        "implementation_prerequisite",
        "automation_guardrail",
    )
    ranked = [
        _retrieval_chunk("case-1", "case_evidence"),
        _retrieval_chunk("guard", "automation_guardrail"),
        _retrieval_chunk("case-2", "case_evidence"),
        _retrieval_chunk("solution", "automation_pattern"),
        _retrieval_chunk("diagnosis", "diagnostic_pattern"),
        _retrieval_chunk("prerequisite", "implementation_prerequisite"),
    ]
    selected = rag_service._diverse_selection(
        ranked,
        required_types=required,
        top_k=6,
    )
    assert set(required) <= {chunk.chunk_type for chunk in selected}


def test_interview_path_retrieves_controlled_agent_patterns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_retrieve(
        query: str,
        *,
        allowed_types: set[str] | None = None,
        top_k: int = 5,
    ) -> list[rag_service.KnowledgeChunk]:
        captured.update(query=query, allowed_types=allowed_types, top_k=top_k)
        return [
            _retrieval_chunk("question", "next_question_pattern"),
            _retrieval_chunk("guardrail", "agent_guardrail"),
        ]

    # agent_pattern_context liegt jetzt im Analysedienst; dort wird auch
    # nachgeschlagen. Die Behauptungen darunter sind unveraendert.
    monkeypatch.setattr(analysis_service, "retrieve_agent_patterns", fake_retrieve)
    context, pattern_types = analysis_service.agent_pattern_context(
        "Auftrag und Zuordnung sind heute noch unklar."
    )
    assert captured["top_k"] == 3
    assert {
        "agent_decision_pattern",
        "next_question_pattern",
        "contradiction_pattern",
        "agent_stop_rule",
        "tool_selection_pattern",
        "agent_guardrail",
    } == captured["allowed_types"]
    assert pattern_types == ["next_question_pattern", "agent_guardrail"]
    assert len(context) == 2


def test_batch_identifiers_are_removed_from_prompt_and_visible_results() -> None:
    formatted = "\n".join(
        rag_service.format_chunks_for_prompt(rag_service.load_diagnostic_chunks())
    )
    assert "RB02-C01-E01" not in formatted
    assert "RB03-C01-01" not in formatted
