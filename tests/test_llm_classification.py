"""Tests fuer die LLM-Klassifikation und fallbezogene Musterrangfolge.

Kein Test ruft die echte OpenAI-API auf; der Structured-Output-Aufruf wird
gemockt. API-Fehler müssen im Produktpfad sichtbar bleiben.
"""

from __future__ import annotations

import app.llm_classification as llm_classification
from app.llm_classification import (
    CLASSIFICATION_SYSTEM_PROMPT,
    ClassificationOutcome,
    FamilyAssessment,
    LlmClassificationResult,
    LlmDecisionGates,
    LlmCandidateRankingItem,
    LlmCandidateRankingResult,
    classify_narrative,
    classify_with_llm,
    rank_candidates,
    _family_context,
    _gate_context,
)
from app.openai_service import AIServiceError
from app.recommendation_service import load_recommendation_catalog


HAUSMEISTER_TEXT = (
    "Ich fahre zum Kunden, kaufe Material ein und schicke danach eine "
    "Sprachnachricht mit Foto und Bon. Die Rechnung schreibe ich abends."
)


def _llm_result(
    family_ids: list[str],
    *,
    anchor: str = "medium",
) -> LlmClassificationResult:
    return LlmClassificationResult(
        families=[
            FamilyAssessment(
                problem_family_id=family_id,
                evidence_quote="Ich fahre zum Kunden",
            )
            for family_id in family_ids
        ],
        gates=LlmDecisionGates(
            transaction_anchor=anchor,
            channel_suitability="high",
            process_data_maturity="unknown",
            error_impact="medium",
            rule_stability="unknown",
            human_approval="medium",
            physical_object=False,
            real_location_known=False,
        ),
    )


def test_family_context_contains_all_twelve_definitions() -> None:
    catalog = load_recommendation_catalog()
    context = _family_context(catalog)
    assert [item["problem_family_id"] for item in context] == [
        f"PF-{index:02d}" for index in range(1, 13)
    ]
    for item in context:
        assert item["definition"]
        assert item["typical_statements"]


def test_gate_context_contains_all_six_gates() -> None:
    catalog = load_recommendation_catalog()
    context = _gate_context(catalog)
    assert [item["gate_id"] for item in context] == [
        f"GATE-{index:02d}" for index in range(1, 7)
    ]


def test_system_prompt_allows_unknown_and_requires_evidence() -> None:
    assert "unknown" in CLASSIFICATION_SYSTEM_PROMPT
    assert "Belegzitat" in CLASSIFICATION_SYSTEM_PROMPT
    assert "Abgrenzung PF-02/PF-03/PF-12" in CLASSIFICATION_SYSTEM_PROMPT


def test_classify_with_llm_maps_families_and_gates(monkeypatch) -> None:
    monkeypatch.setattr(
        llm_classification,
        "_parse_structured_output",
        lambda **_: _llm_result(["PF-08", "PF-03"], anchor="low"),
    )
    outcome = classify_with_llm(HAUSMEISTER_TEXT)
    assert outcome.method == "llm"
    assert outcome.problem_family_ids == ["PF-08", "PF-03"]
    assert outcome.gates.transaction_anchor == "low"
    assert outcome.gates.process_data_maturity == "unknown"


def test_classify_with_llm_reaches_previously_unreachable_families(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        llm_classification,
        "_parse_structured_output",
        lambda **_: _llm_result(["PF-03", "PF-11"]),
    )
    outcome = classify_with_llm("Nur ich weiss, wie alles laeuft.")
    assert outcome.problem_family_ids == ["PF-03", "PF-11"]


def test_classify_with_llm_deduplicates_and_limits_to_three(monkeypatch) -> None:
    monkeypatch.setattr(
        llm_classification,
        "_parse_structured_output",
        lambda **_: _llm_result(["PF-02", "PF-02", "PF-04", "PF-05", "PF-06"]),
    )
    outcome = classify_with_llm(HAUSMEISTER_TEXT)
    assert outcome.problem_family_ids == ["PF-02", "PF-04", "PF-05"]


def test_classify_with_llm_allows_empty_family_list_for_a0(monkeypatch) -> None:
    monkeypatch.setattr(
        llm_classification,
        "_parse_structured_output",
        lambda **_: LlmClassificationResult(
            families=[],
            gates=_llm_result(["PF-01"]).gates,
        ),
    )
    outcome = classify_with_llm("Die vorhandene Kalenderfunktion reicht aus.")
    assert outcome.problem_family_ids == []
    assert outcome.method == "llm"


def test_classify_narrative_uses_llm_when_available(monkeypatch) -> None:
    monkeypatch.setattr(
        llm_classification,
        "_parse_structured_output",
        lambda **_: _llm_result(["PF-08"]),
    )
    outcome = classify_narrative(HAUSMEISTER_TEXT)
    assert outcome.method == "llm"
    assert outcome.problem_family_ids == ["PF-08"]


def test_classify_narrative_propagates_service_failure(monkeypatch) -> None:
    def _raise(**_: object) -> None:
        raise AIServiceError("API nicht erreichbar")

    monkeypatch.setattr(llm_classification, "_parse_structured_output", _raise)
    import pytest

    with pytest.raises(AIServiceError):
        classify_narrative(HAUSMEISTER_TEXT)


def test_rank_candidates_filters_foreign_ids_and_requires_complete_ranking(
    monkeypatch,
) -> None:
    candidates = load_recommendation_catalog().solution_patterns[:2]
    monkeypatch.setattr(
        llm_classification,
        "_parse_structured_output",
        lambda **_: LlmCandidateRankingResult(
            ranking=[
                LlmCandidateRankingItem(solution_id="SP-09", reason="Fremd"),
                LlmCandidateRankingItem(solution_id="SP-01", reason="Passt"),
            ]
        ),
    )
    import pytest

    with pytest.raises(AIServiceError):
        rank_candidates("Anfragen kommen über mehrere Kanäle.", candidates)


def test_rank_candidates_returns_only_allowed_candidates_in_model_order(monkeypatch) -> None:
    candidates = load_recommendation_catalog().solution_patterns[:2]
    monkeypatch.setattr(
        llm_classification,
        "_parse_structured_output",
        lambda **_: LlmCandidateRankingResult(
            ranking=[
                LlmCandidateRankingItem(solution_id="SP-02", reason="Zweiter Ablauf"),
                LlmCandidateRankingItem(solution_id="SP-01", reason="Direkter Eingang"),
            ]
        ),
    )
    ranking = rank_candidates("Anfragen kommen über mehrere Kanäle.", candidates)
    assert [item.solution_id for item in ranking] == ["SP-02", "SP-01"]


def test_classify_narrative_result_is_serializable(monkeypatch) -> None:
    monkeypatch.setattr(
        llm_classification,
        "_parse_structured_output",
        lambda **_: _llm_result(["PF-08"]),
    )
    outcome = classify_narrative(HAUSMEISTER_TEXT)
    assert isinstance(outcome, ClassificationOutcome)
    payload = outcome.model_dump()
    assert payload["method"] == "llm"
    assert payload["gates"]["channel_suitability"] == "high"
