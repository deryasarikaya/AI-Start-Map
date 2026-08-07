from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.recommendation_service import (
    CandidateRankingItem,
    DecisionGates,
    infer_decision_gates,
    select_recommendation,
)
from app.solution_knowledge import load_solution_workflows, match_business_type


ROOT = Path(__file__).resolve().parents[1]
CASES_FILE = ROOT / "knowledge" / "evaluation" / "quality_selection_cases.jsonl"


def _cases() -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in CASES_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _rank_with(preferred: str):
    def rank(_text, candidates):
        ordered = sorted(
            candidates,
            key=lambda item: item.solution_id != preferred,
        )
        return [
            CandidateRankingItem(
                solution_id=item.solution_id,
                reason="Das Muster trifft den beschriebenen Ablauf am direktesten.",
            )
            for item in ordered
        ]

    return rank


def test_quality_cases_are_explicitly_excluded_from_every_index() -> None:
    assert len(_cases()) == 4
    assert {item["index_policy"] for item in _cases()} == {
        "exclude_from_all_rag_indexes"
    }


def test_receipts_and_own_material_are_not_custody_objects() -> None:
    for text in (
        "Kassenzettel liegen im Handschuhfach und werden abends einem Auftrag zugeordnet.",
        "Ich fotografiere Rechnungen, Lieferscheine, Notizen und eingekauftes Material.",
    ):
        assert infer_decision_gates(text).physical_object is False


def test_shoes_held_by_the_workshop_remain_a_custody_object() -> None:
    text = "Angenommene Schuhe werden in der Werkstatt repariert und aus dem Regal abgeholt."
    assert infer_decision_gates(text).physical_object is True


def test_business_type_matching_requires_one_clear_runtime_match() -> None:
    workflows = load_solution_workflows()
    assert match_business_type("kleiner Blumenladen", workflows=workflows) == "blumenladen"
    assert match_business_type("Hausmeisterservice", workflows=workflows) == "hausmeisterservice"
    assert match_business_type("kleiner Betrieb", workflows=workflows) is None


@pytest.mark.parametrize(
    ("case_id", "families", "preferred"),
    [
        ("QUALITY-FLOWER-MULTICHANNEL", ["PF-01"], "SP-01"),
        ("QUALITY-HOUSEKEEPER-RECEIPTS", ["PF-09", "PF-08"], "SP-03"),
        ("QUALITY-HOUSEKEEPER-VISIT", ["PF-08"], "SP-03"),
        ("QUALITY-SHOEMAKER-CUSTODY", ["PF-05"], "SP-04"),
    ],
)
def test_case_specific_ranking_only_orders_python_allowed_candidates(
    case_id: str,
    families: list[str],
    preferred: str,
) -> None:
    case = next(item for item in _cases() if item["case_id"] == case_id)
    text = str(case["customer_statement"])
    gates = infer_decision_gates(text)
    if case_id == "QUALITY-SHOEMAKER-CUSTODY":
        gates = gates.model_copy(
            update={
                "channel_suitability": "medium",
                "process_data_maturity": "low",
                "error_impact": "high",
                "human_approval": "high",
            }
        )
    selection = select_recommendation(
        families,
        gates,
        confirmed_text=text,
        candidate_ranker=_rank_with(preferred),
    )
    assert selection.primary is not None
    assert selection.primary.solution_id == preferred
    forbidden = set(case["forbidden_solution_pattern_ids"])
    assert selection.primary.solution_id not in forbidden
    assert selection.primary.solution_id not in forbidden
