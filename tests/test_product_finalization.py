from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app import openai_service
from app.agent_service import (
    FactRecord,
    ProcessState,
    RagEvidence,
    evaluate_readiness_and_next_action,
    question_can_change_core_output,
)
from app.schemas import (
    AutomationBlueprint,
    AutomationOpportunityResult,
    FinalAnalysisResult,
    OptionalAnalysisDetails,
    ProcessUnderstandingResult,
    customer_plain_text,
)
from tests.conftest import spec_payload


ROOT = Path(__file__).resolve().parents[1]


def test_final_payload_normalization_removes_internal_jargon_and_meta_steps() -> None:
    normalized = openai_service._normalize_final_analysis_payload(
        {
            "as_is_steps": [
                "Die genaue Reihenfolge ist unbekannt.",
                "Die Kundin sendet eine Anfrage.",
            ],
            "as_is_problem_step_indexes": [0, 1],
            "opportunities": [
                {"title": "WIP-Mapping", "recommendation": "Formulardoppie vermeiden"}
            ],
        }
    )

    assert isinstance(normalized, dict)
    assert normalized["as_is_steps"] == ["Die Kundin sendet eine Anfrage."]
    assert normalized["as_is_problem_step_indexes"] == [0]
    opportunity = normalized["opportunities"][0]
    assert opportunity["title"] == "aktueller Arbeitsstand-Zuordnung"
    assert opportunity["recommendation"] == "doppelte Erfassung vermeiden"


def test_follow_up_payload_is_normalized_to_today_without_repair_call() -> None:
    normalized = openai_service._normalize_follow_up_payload(
        {
            "questions": [
                {
                    "question": (
                        "Wenn du abrechnest, welche Informationen brauchst du?"
                    ),
                    "issue_type": "critical_unknown",
                },
                {
                    "question": "Welche Software sollte eingeführt werden?",
                    "issue_type": "missing",
                },
            ]
        }
    )

    assert normalized == {
        "questions": [
            {
                "question": (
                    "Welche Informationen brauchst du heute, wenn du abrechnest?"
                ),
                "issue_type": "critical_unknown",
            }
        ]
    }


def test_final_analysis_allows_two_medium_reasoning_attempts() -> None:
    assert openai_service.FINAL_ANALYSIS_TIMEOUT_SECONDS == 240.0


def _fact(value: str) -> FactRecord:
    return FactRecord(
        value=value,
        status="confirmed",
        origin="user_confirmation",
        turn_id="test",
    )


def test_structured_output_requires_the_whole_customer_contract() -> None:
    """Structured Outputs verlangt jede Eigenschaft in required."""

    schema = FinalAnalysisResult.model_json_schema()
    required = set(schema["required"])
    assert {
        "engpass_titel",
        "engpass_text",
        "moeglichkeiten",
        "loesung",
        "beispiel",
        "voraussetzungen",
        "umsetzung",
        "bleibt_bei_dir",
        "grenzen",
    } <= required
    assert set(schema["properties"]) <= required
    for entfallen in ("primary_recommendation", "promise", "sample_output",
                      "secondary_opportunities", "weekly_test"):
        assert entfallen not in schema["properties"]


def test_unsubstantiated_benefit_claims_do_not_reach_the_customer() -> None:
    """Eine Ersparnis ohne Grundlage wird ausgelassen, nicht umformuliert."""

    behauptung = (
        "Du sammelst alles an einer Stelle. Das reduziert deine Suchzeit deutlich."
    )
    bereinigt = customer_plain_text(behauptung, "test")
    assert "Du sammelst alles an einer Stelle." in bereinigt
    assert "Suchzeit" not in bereinigt


def test_ai_is_not_recommended_when_nothing_is_written_down_yet() -> None:
    """A0: Wenn KI hier noch nicht hilft, sagt das Ergebnis genau das."""

    result = FinalAnalysisResult.model_validate(
        spec_payload(
            autonomy_level="A0",
            engpass_titel="Du hältst Telefonbestellungen nirgends fest",
            engpass_text=(
                "Bestellungen am Telefon schreibst du nicht auf. Was nirgends steht, "
                "kann später niemand wiederfinden."
            ),
            bleibt_bei_dir=(
                "Du entscheidest über Preis und Zusage. Zuerst brauchst du eine feste "
                "kleine Gewohnheit, sonst hilft dir hier noch keine KI."
            ),
        )
    )
    assert result.autonomy_level == "A0"
    assert "noch keine KI" in result.bleibt_bei_dir


def test_agent_asks_only_for_solution_changing_anchor_and_rejects_repeats() -> None:
    state = ProcessState(
        process_start=_fact("Ein Schuh wird angenommen."),
        process_end=_fact("Der Schuh wird übergeben."),
        as_is_steps=[_fact("Zettel schreiben"), _fact("Schuh frei ins Regal stellen")],
        pain_points=[_fact("Wir suchen oft Zettel und Regalplatz.")],
        bottleneck_candidates=[_fact("Zuordnung fehlt.")],
        available_data=[_fact("Papierzettel")],
        rag_evidence=[RagEvidence(chunk_id="x", chunk_type="pattern", content="Vergleichswissen")],
    )
    anchor_decision = evaluate_readiness_and_next_action(state)
    assert anchor_decision.next_action == "ASK"
    assert anchor_decision.information_gap == "transaction_anchor"
    assert anchor_decision.possible_next_question.startswith("Woran erkennst du heute")
    assert not question_can_change_core_output(
        "Wie lange bleiben die Schuhe heute liegen?", state
    )
    assert not question_can_change_core_output(
        "Gibt es heute eine feste Regalreihenfolge?", state
    )
    assert not question_can_change_core_output(
        "Wie wird heute festgehalten, an welchem Ort der Schuh liegt?", state
    )
    grounded_state = state.model_copy(deep=True)
    grounded_state.as_is_steps = [
        _fact("Auftragsnummer am Schuh anbringen"),
        _fact("Schuh in ein festes Fach legen"),
    ]
    assert evaluate_readiness_and_next_action(grounded_state).next_action == "ANALYZE"
    repeated = evaluate_readiness_and_next_action(grounded_state, latest_user_message="Das habe ich doch schon gesagt.")
    assert repeated.next_action == "ANALYZE"
    assert repeated.stop_reason == "no_repeat_recheck"


def test_process_summary_and_report_use_safe_vertical_structures() -> None:
    details = (ROOT / "app/templates/process_details.html").read_text(encoding="utf-8")
    results = (ROOT / "app/templates/results.html").read_text(encoding="utf-8")
    report = (ROOT / "app/templates/report.html").read_text(encoding="utf-8")
    assert "process-strip" in details and "mermaid" not in details.casefold()
    assert "process-strip" in results and "mermaid" not in results.casefold()
    assert report.count('class="report-page ') == 2
    assert "report-page--third" not in report
    assert "result.secondary_opportunities" not in report
    assert "mermaid" not in report.casefold()
    assert "weekly_test" not in results
    assert "weekly_test" not in report
    assert "session_id" not in report
    assert "Prozessdiagnostik und Entscheidungsvorbereitung" not in report


def test_landing_processing_and_mobile_contract(client: TestClient) -> None:
    landing = client.get("/").text
    assert "Wo könnte KI dir im Alltag wirklich Arbeit abnehmen?" in landing
    assert "Per Sprache oder Text · dauert wenige Minuten" in landing
    assert landing.count('<section class="landing-section') <= 5
    base = (ROOT / "app/templates/base.html").read_text(encoding="utf-8")
    app_js = (ROOT / "app/static/app.js").read_text(encoding="utf-8")
    styles = (ROOT / "app/static/styles.css").read_text(encoding="utf-8")
    assert "data-processing-layer" in base
    assert "button.disabled = true" in app_js
    assert "event.preventDefault()" in app_js
    assert "overflow-x: hidden" in styles
    assert "@media (max-width: 42.99rem)" in styles


def test_process_understanding_is_limited_to_five_visible_steps() -> None:
    schema = ProcessUnderstandingResult.model_json_schema()
    assert schema["properties"]["as_is_steps"]["maxItems"] == 5
