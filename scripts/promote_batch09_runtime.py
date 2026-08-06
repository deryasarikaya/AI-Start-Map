from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIRECTORY))

from app.recommendation_service import load_recommendation_catalog  # noqa: E402


CANDIDATE_DIRECTORY = ROOT_DIRECTORY / "knowledge" / "candidates" / "batch_09"
RUNTIME_DIRECTORY = ROOT_DIRECTORY / "knowledge" / "runtime"
EVALUATION_DIRECTORY = ROOT_DIRECTORY / "knowledge" / "evaluation"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def source_ids(path: Path) -> set[str]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return {row["source_id"] for row in csv.DictReader(stream)}


def validate_source_refs(records: list[dict[str, Any]], known_sources: set[str]) -> None:
    missing = sorted(
        {
            source_ref
            for record in records
            for source_ref in record.get("source_refs", [])
            if source_ref not in known_sources
        }
    )
    if missing:
        raise ValueError(f"Unbekannte source_refs: {missing}")


def build_runtime_payloads() -> dict[Path, list[dict[str, Any]]]:
    patterns = read_jsonl(CANDIDATE_DIRECTORY / "01_customer_inference_patterns.jsonl")
    workflows = read_jsonl(CANDIDATE_DIRECTORY / "02_solution_workflows.jsonl")
    outputs = read_jsonl(CANDIDATE_DIRECTORY / "03_output_structures.jsonl")
    evaluations = read_jsonl(CANDIDATE_DIRECTORY / "04_evaluation_cases.jsonl")
    if (len(patterns), len(workflows), len(outputs), len(evaluations)) != (27, 28, 10, 30):
        raise ValueError("Batch-09-Mengen entsprechen nicht der geprüften Lieferung.")
    known_sources = source_ids(CANDIDATE_DIRECTORY / "05_source_register.csv")
    if len(known_sources) != 20:
        raise ValueError("Das Batch-09-Quellenregister muss 20 Quellen enthalten.")
    for records in (patterns, workflows, outputs):
        validate_source_refs(records, known_sources)

    catalog = load_recommendation_catalog()
    channels_by_solution = {
        item.solution_id: item.input_channels for item in catalog.solution_patterns
    }

    runtime_patterns = [
        {**record, "source_batch": "batch_09", "quality_status": "runtime_approved"}
        for record in patterns
    ]
    runtime_workflows: list[dict[str, Any]] = []
    for record in workflows:
        steps = [
            {
                **step,
                "actor": "software_rule" if step["actor"] == "system" else step["actor"],
            }
            for step in record["target_workflow"]
        ]
        runtime_workflows.append(
            {
                "chunk_id": record["workflow_id"],
                "chunk_type": "solution_workflow",
                **record,
                "channels": channels_by_solution[record["solution_pattern_id"]],
                "maturity": [2, 3],
                "target_workflow": steps,
                "source_strength": "reviewed_synthesis",
                "source_batch": "batch_09",
                "quality_status": "runtime_approved",
            }
        )
    runtime_outputs: list[dict[str, Any]] = []
    for record in outputs:
        fields = [dict(field) for field in record["fields"]]
        if record["solution_pattern_id"] == "SP-04":
            for field in fields:
                field["requires_human_input"] = True
        runtime_outputs.append(
            {
                **record,
                "fields": fields,
                "source_batch": "batch_09",
                "quality_status": "runtime_approved",
            }
        )

    return {
        RUNTIME_DIRECTORY / "patterns" / "inference_patterns.jsonl": runtime_patterns,
        RUNTIME_DIRECTORY / "solution_knowledge" / "solution_workflows.jsonl": runtime_workflows,
        RUNTIME_DIRECTORY / "output_structures.jsonl": runtime_outputs,
        EVALUATION_DIRECTORY / "batch_09_evaluation_cases.jsonl": evaluations,
    }


def write_payloads(payloads: dict[Path, list[dict[str, Any]]]) -> None:
    for path, records in payloads.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
            encoding="utf-8",
        )


def main() -> None:
    payloads = build_runtime_payloads()
    write_payloads(payloads)
    for path, records in payloads.items():
        print(f"{path.relative_to(ROOT_DIRECTORY)}: {len(records)}")


if __name__ == "__main__":
    main()
