from pathlib import Path

from fastapi.testclient import TestClient

from app import openai_service
from app.agent_service import FactRecord
from app.schemas import FinalAnalysisResult, customer_plain_text


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
    assert openai_service.FINAL_ANALYSIS_TIMEOUT_SECONDS == 300.0


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


def test_landing_processing_and_mobile_contract(client: TestClient) -> None:
    landing = client.get("/").text
    assert "Finden Sie heraus, wo KI Ihnen wirklich Arbeit abnehmen kann." in landing
    assert "Beschreiben Sie einfach Ihren Arbeitsalltag." in landing
    assert "Und wie Ihre Abläufe künftig besser zusammenspielen könnten." in landing
    # „dauert wenige Minuten" ist raus: Die Seite will, dass er sich Zeit
    # nimmt, und darf ihn nicht gleichzeitig zur Eile mahnen.
    assert "Kostenlos · per Sprache oder Text · keine KI-Vorkenntnisse" in landing
    assert landing.count('<section class="landing-section') <= 8
    base = (ROOT / "app/templates/base.html").read_text(encoding="utf-8")
    app_js = (ROOT / "app/static/app.js").read_text(encoding="utf-8")
    styles = (ROOT / "app/static/styles.css").read_text(encoding="utf-8")
    assert "data-processing-layer" in base
    assert "button.disabled = true" in app_js
    assert "event.preventDefault()" in app_js
    assert "overflow-x: hidden" in styles
    assert "@media (max-width: 42.99rem)" in styles
