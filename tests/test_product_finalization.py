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
)


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


def test_final_analysis_uses_dedicated_sixty_second_timeout() -> None:
    assert openai_service.FINAL_ANALYSIS_TIMEOUT_SECONDS == 60.0


def _fact(value: str) -> FactRecord:
    return FactRecord(
        value=value,
        status="confirmed",
        origin="user_confirmation",
        turn_id="test",
    )


def _analysis_result(
    *,
    core_problem: str,
    first_change: str,
    ai_support: str,
    ai_input: str,
    ai_task: str,
    ai_output: str,
    human_check: str,
    later_automation: str,
) -> FinalAnalysisResult:
    opportunities = [
        AutomationOpportunityResult(
            rank=rank,
            title=title,
            problem=core_problem,
            recommendation=first_change,
            benefit="Der aktuelle Stand wird verlässlich nachvollziehbar.",
            human_approval=human_check,
            first_step="Den kleinen Test mit neuen Vorgängen beginnen.",
            category=category,
            prerequisite="Die benötigten Angaben sind einheitlich benannt.",
            mini_test=["Neue Vorgänge einheitlich erfassen."],
            effort="niedrig" if rank == 1 else "mittel",
            acceptance_risk="Ausnahmen werden im Test sichtbar gehalten.",
        )
        for rank, title, category in (
            (1, "Einheitlich beginnen", "Ordnung und Standardisierung"),
            (2, "KI-Unterstützung erproben", "KI-Unterstützung"),
            (3, "Bestätigten Schritt vorbereiten", "regelbasierte Automatisierung"),
        )
    ]
    return FinalAnalysisResult(
        core_problem=core_problem,
        first_change=first_change,
        ai_support=ai_support,
        ai_input=ai_input,
        ai_task=ai_task,
        ai_output=ai_output,
        human_check=human_check,
        weekly_test=[
            "Nur neue Vorgänge einheitlich erfassen.",
            "Fehlende Angaben sichtbar markieren.",
            "Am Ende der Woche die Auffindbarkeit prüfen.",
        ],
        weekly_test_success="Jeder neue Vorgang ist ohne zusätzliche Suche auffindbar.",
        later_automation=later_automation,
        why_this_first="Ohne verlässliche Zuordnung würde Technik das heutige Durcheinander nur übernehmen.",
        required_prerequisites=["Eine gemeinsame Bezeichnung für die Pflichtangaben."],
        human_decisions=[human_check],
        current_process_summary="Angaben kommen an, werden notiert, bearbeitet und nach menschlicher Prüfung abgeschlossen.",
        optional_details=OptionalAnalysisDetails(
            current_difficulties=[core_problem],
            additional_prerequisites=[],
            later_possibilities=[later_automation],
        ),
        process_summary="Angaben kommen an, werden notiert, bearbeitet und nach menschlicher Prüfung abgeschlossen.",
        as_is_steps=["Angaben annehmen", "Notieren", "Bearbeiten", "Prüfen"],
        core_bottleneck=core_problem,
        bottleneck_symptom="Der aktuelle Stand muss gesucht werden.",
        bottleneck_cause=core_problem,
        bottleneck_effect="Rückfragen und Suchaufwand entstehen.",
        as_is_problem_step_indexes=[1],
        to_be_steps=["Erfassen", "Prüfen", "Bestätigen"],
        uncertainties=["Das genaue Wochenvolumen ist unbekannt."],
        opportunities=opportunities,
        blueprint=AutomationBlueprint(
            objective="Neue Vorgänge verlässlich zuordnen.",
            trigger="Ein neuer Vorgang kommt an.",
            required_inputs=["Pflichtangaben"],
            workflow_steps=["Vorgang erfassen", "Angaben prüfen", "Ergebnis bestätigen"],
            human_review_point=human_check,
            output="Ein bestätigter, auffindbarer Vorgang.",
            exceptions=["Eine Angabe bleibt unklar."],
        ),
    )


def test_structured_output_requires_the_new_customer_core() -> None:
    required = set(FinalAnalysisResult.model_json_schema()["required"])
    assert {
        "core_problem",
        "first_change",
        "ai_support",
        "ai_input",
        "ai_task",
        "ai_output",
        "human_check",
        "weekly_test",
        "weekly_test_success",
        "later_automation",
        "why_this_first",
        "required_prerequisites",
        "human_decisions",
        "current_process_summary",
        "optional_details",
    } <= required


def test_generic_ai_claim_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _analysis_result(
            core_problem="Der aktuelle Stand ist verteilt.",
            first_change="Eine gemeinsame Übersicht anlegen.",
            ai_support="KI kann deinen Prozess optimieren.",
            ai_input="Eine Nachricht",
            ai_task="Angaben ordnen",
            ai_output="Ein Entwurf",
            human_check="Ein Mensch bestätigt den Entwurf.",
            later_automation="Nach der Bestätigung kann eine Nachricht vorbereitet werden.",
        )


def test_shoe_repair_output_is_concrete_and_grounded() -> None:
    result = _analysis_result(
        core_problem="Auftrag, Schuh und Regalplatz sind nicht zuverlässig verbunden.",
        first_change="Vergib eine einheitliche Nummer und dokumentiere den Regalplatz.",
        ai_support="Mitarbeitende sprechen oder schreiben neue Aufträge ein; KI ordnet die Angaben und markiert Lücken.",
        ai_input="Name, Telefonnummer, Reparaturwunsch und Regalplatz als Sprache oder Text.",
        ai_task="Die KI extrahiert die vier Angaben und weist auf fehlende Angaben hin.",
        ai_output="Ein strukturierter Auftragsentwurf mit eindeutiger Nummer und Regalplatz.",
        human_check="Ein Mensch prüft Auftrag, Preis, Regalplatz und Fertigstellung.",
        later_automation="Wenn Zuordnung und Status verlässlich sind, kann eine Fertigmeldung vorbereitet werden.",
    )
    visible = " ".join(
        (result.core_problem, result.first_change, result.ai_support, result.later_automation)
    ).casefold()
    assert "auftrag, schuh und regalplatz" in visible
    assert "sprache oder text" in result.ai_input.casefold()
    assert "fertigmeldung" in result.later_automation.casefold()
    assert not any(term in visible for term in ("chatbot", "qr-code", "sicherheitsvorfall"))


def test_massage_output_keeps_appointment_confirmation_human() -> None:
    result = _analysis_result(
        core_problem="Anfragen, Verfügbarkeit und Bestätigung liegen über mehrere Kanäle verteilt.",
        first_change="Führe alle Anfragen in einer Übersicht mit klaren Statuswerten zusammen.",
        ai_support="KI liest oder hört Anfragen und bereitet passende Terminoptionen vor.",
        ai_input="Behandlung, Dauer, Personenzahl und Wunschzeit aus Nachricht oder Sprache.",
        ai_task="Die KI extrahiert die Angaben und gleicht sie mit der gepflegten Verfügbarkeit ab.",
        ai_output="Prüfbare Terminoptionen mit sichtbar fehlenden Angaben.",
        human_check="Ein Mensch wählt und bestätigt den Termin.",
        later_automation="Nach menschlicher Terminbestätigung kann die bestätigte Nachricht zum Versand vorbereitet werden.",
    )
    assert "mehrere kanäle" in result.core_problem.casefold()
    assert all(term in result.ai_input.casefold() for term in ("behandlung", "dauer", "personenzahl", "wunschzeit"))
    assert "mensch" in result.human_check.casefold()


def test_no_digital_foundation_states_that_ai_is_not_first() -> None:
    result = _analysis_result(
        core_problem="Auftragsdaten werden uneinheitlich und nur auf losen Zetteln festgehalten.",
        first_change="Lege zuerst ein einheitliches Auftragsblatt mit wenigen Pflichtangaben fest.",
        ai_support="KI ist heute noch nicht der erste Schritt. Sobald Auftragsdaten einheitlich erfasst werden, kann KI gesprochene Angaben ordnen.",
        ai_input="Einheitlich erfasste oder eingesprochene Auftragsangaben.",
        ai_task="Die KI überträgt Angaben in einen prüfbaren Entwurf.",
        ai_output="Ein vollständiger Auftragsentwurf.",
        human_check="Ein Mensch prüft Preis, Inhalt und Freigabe.",
        later_automation="Nach einem stabilen Test kann eine bestätigte Statusmeldung vorbereitet werden.",
    )
    assert result.ai_support.startswith("KI ist heute noch nicht der erste Schritt.")
    assert "preis" in result.human_check.casefold()


def test_agent_can_analyze_without_a_follow_up_and_rejects_repeats() -> None:
    state = ProcessState(
        process_start=_fact("Ein Schuh wird angenommen."),
        process_end=_fact("Der Schuh wird übergeben."),
        as_is_steps=[_fact("Zettel schreiben"), _fact("Schuh frei ins Regal stellen")],
        pain_points=[_fact("Wir suchen oft Zettel und Regalplatz.")],
        bottleneck_candidates=[_fact("Zuordnung fehlt.")],
        available_data=[_fact("Papierzettel")],
        rag_evidence=[RagEvidence(chunk_id="x", chunk_type="pattern", content="Vergleichswissen")],
    )
    assert evaluate_readiness_and_next_action(state).next_action == "ANALYZE"
    assert not question_can_change_core_output(
        "Wie lange bleiben die Schuhe heute liegen?", state
    )
    assert not question_can_change_core_output(
        "Gibt es heute eine feste Regalreihenfolge?", state
    )
    assert not question_can_change_core_output(
        "Wie wird heute festgehalten, an welchem Ort der Schuh liegt?", state
    )
    repeated = evaluate_readiness_and_next_action(
        state, latest_user_message="Das habe ich doch schon gesagt."
    )
    assert repeated.next_action == "ANALYZE"
    assert repeated.stop_reason == "no_repeat_recheck"


def test_process_summary_and_report_use_safe_vertical_structures() -> None:
    details = (ROOT / "app/templates/process_details.html").read_text(encoding="utf-8")
    results = (ROOT / "app/templates/results.html").read_text(encoding="utf-8")
    report = (ROOT / "app/templates/report.html").read_text(encoding="utf-8")
    assert "process-strip" in details and "mermaid" not in details.casefold()
    assert "process-strip" in results and "mermaid" not in results.casefold()
    assert report.count('class="report-page ') == 3
    assert "mermaid" not in report.casefold()
    assert "session_id" not in report
    assert "Prozessdiagnostik und Entscheidungsvorbereitung" not in report


def test_landing_processing_and_mobile_contract(client: TestClient) -> None:
    landing = client.get("/").text
    assert "FÜR SELBSTSTÄNDIGE UND KLEINE BETRIEBE" in landing
    assert "Dein Betrieb läuft. Aber vieles läuft nur, weil du ständig alles zusammenhältst." in landing
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
