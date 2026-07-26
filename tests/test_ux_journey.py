from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

import app.routes as routes
from app.models import Analysis, ProcessOption
from app.schemas import (
    AutomationBlueprint,
    AutomationOpportunityResult,
    FinalAnalysisResult,
    FollowUpQuestion,
    FollowUpResult,
    ProcessSuggestion,
    ProcessSuggestionResult,
    ProcessUnderstandingResult,
)


def _suggestions() -> ProcessSuggestionResult:
    return ProcessSuggestionResult(
        suggestions=[
            ProcessSuggestion(
                process_name="Anfrage bis fertiger Auftrag",
                start_event="Eine Anfrage kommt an",
                end_event="Der fertige Auftrag wird übergeben",
                reason="Anfragen und Auftragsstände kommen über mehrere Wege zusammen.",
            ),
            ProcessSuggestion(
                process_name="Fertigmeldung bis Abholung",
                start_event="Ein Auftrag ist fertig",
                end_event="Der Auftrag wurde abgeholt",
                reason="Bei fertigen Aufträgen wird gesucht und nachgefragt.",
            ),
        ]
    )


def _understanding() -> ProcessUnderstandingResult:
    return ProcessUnderstandingResult(
        process_name="Anfrage bis fertiger Auftrag",
        start_event="Eine Anfrage kommt an",
        end_event="Der fertige Auftrag wird übergeben",
        as_is_steps=[
            "Anfrage über Telefon oder Nachricht annehmen",
            "Angaben auf einem Zettel notieren",
            "Auftrag zur Bearbeitung ablegen",
            "Aktuellen Stand bei Bedarf zusammensuchen",
            "Fertigen Auftrag an den Kunden übergeben",
        ],
        confirmed_facts=[
            "Anfragen kommen über mehrere Wege.",
            "Angaben werden heute auf Zetteln notiert.",
        ],
        difficult_points=["Der aktuelle Stand muss bei Bedarf zusammengesucht werden."],
        problem_step_indexes=[3],
        open_points=["Wie die Ablage heute gekennzeichnet ist, ist noch nicht klar."],
    )


def _final_result() -> FinalAnalysisResult:
    return FinalAnalysisResult(
        process_summary="Anfragen werden aufgenommen, auf Papier notiert, bearbeitet und nach einer Suche nach dem aktuellen Stand übergeben.",
        as_is_steps=_understanding().as_is_steps,
        core_bottleneck="Auftrag und aktueller Stand sind nicht zuverlässig verbunden.",
        bottleneck_symptom="Bei Rückfragen muss der aktuelle Stand zusammengesucht werden.",
        bottleneck_cause="Auftrag und aktueller Stand sind nicht zuverlässig verbunden.",
        bottleneck_effect="Es entstehen Suchaufwand, Rückfragen und Unsicherheit.",
        as_is_problem_step_indexes=[3],
        to_be_steps=[
            "Anfrage annehmen",
            "Eindeutige Auftragsnummer vergeben",
            "Auftrag und Ablageort gemeinsam notieren",
            "Status nach der Bearbeitung aktualisieren",
            "Geprüften Auftrag übergeben",
        ],
        uncertainties=["Die Zahl gleichzeitig offener Aufträge ist noch nicht klar."],
        opportunities=[
            AutomationOpportunityResult(
                rank=1,
                title="Auftrag und Ablageort eindeutig verbinden",
                problem="Bei Rückfragen muss der aktuelle Stand zusammengesucht werden.",
                recommendation="Zuerst eine eindeutige Nummer für Auftrag und Ablage verwenden.",
                benefit="Der aktuelle Auftrag lässt sich ohne mehrere Suchwege zuordnen.",
                human_approval="Eine Person bestätigt Status und Übergabe.",
                first_step="Eine einfache Nummernfolge festlegen.",
                category="Ordnung und Standardisierung",
                prerequisite="Ein gemeinsames Nummernschema ist festgelegt.",
                mini_test=[
                    "Eine Nummernfolge festlegen",
                    "Nummer auf Auftrag und Ablage verwenden",
                    "Eine Woche mit wenigen Aufträgen testen",
                ],
                effort="niedrig",
                acceptance_risk="Die Nummer muss bei jeder Ablage konsequent notiert werden.",
            ),
            AutomationOpportunityResult(
                rank=2,
                title="Status an einer Stelle sichtbar machen",
                problem="Der aktuelle Stand ist verteilt.",
                recommendation="Nach dem Nummerntest eine gemeinsame Statusübersicht erproben.",
                benefit="Rückfragen lassen sich schneller beantworten.",
                human_approval="Eine Person setzt den Status bewusst.",
                first_step="Wenige verständliche Statuswerte festlegen.",
                category="einfache Digitalisierung",
                prerequisite="Nummern und Statuswerte werden einheitlich verwendet.",
                effort="mittel",
                acceptance_risk="Die Übersicht hilft nur, wenn Änderungen zeitnah eingetragen werden.",
            ),
            AutomationOpportunityResult(
                rank=3,
                title="Fertigmeldung vorbereiten",
                problem="Fertige Aufträge werden nicht immer mitgeteilt.",
                recommendation="Nach menschlicher Fertigmeldung einen Hinweis vorbereiten lassen.",
                benefit="Kunden erhalten verlässlicher eine Nachricht.",
                human_approval="Eine Person bestätigt die Fertigstellung und den Versand.",
                first_step="Einen verständlichen Nachrichtentext festlegen.",
                category="regelbasierte Automatisierung",
                prerequisite="Fertigstatus und Kontaktdaten sind zuverlässig vorhanden.",
                effort="mittel",
                acceptance_risk="Vor dem Versand muss der Kontaktweg geprüft werden.",
            ),
        ],
        blueprint=AutomationBlueprint(
            objective="Auftrag und Ablageort eindeutig zuordnen.",
            trigger="Eine neue Anfrage wird zum Auftrag.",
            required_inputs=["Auftragsnummer", "Ablagebereich"],
            workflow_steps=[
                "Auftragsnummer vergeben",
                "Nummer am Auftrag verwenden",
                "Ablagebereich notieren",
                "Status durch eine Person aktualisieren",
            ],
            human_review_point="Vor der Übergabe bestätigt eine Person Auftrag und Status.",
            output="Ein eindeutig zugeordneter Auftrag.",
            exceptions=["Ein Auftrag wechselt den Ablagebereich."],
        ),
    )


@pytest.fixture(autouse=True)
def mock_retrieval(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(routes, "_retrieval_context", lambda _query, _phase: ["Internes Muster"])


def test_landing_voice_fallback_and_mobile_assets(client: TestClient) -> None:
    landing = client.get("/")
    assert landing.status_code == 200
    for text in (
        "Was läuft in deinem Betrieb immer wieder unnötig kompliziert?",
        "Kommt dir das bekannt vor?",
        "Nicht noch mehr Ideen",
        "Jetzt meinen Ablauf ansehen",
    ):
        assert text in landing.text
    assert "RAG" not in landing.text
    assert "LLM" not in landing.text

    interview_start = client.post("/begin", follow_redirects=False)
    assert interview_start.headers["location"] == "/interview"
    assert routes.SESSION_COOKIE in interview_start.headers["set-cookie"]
    interview = client.get("/interview")
    assert "Aufnahme starten" in interview.text
    assert "Lieber schreiben" in interview.text
    assert "contenteditable" not in interview.text
    assert 'name="free_description"' in interview.text
    assert "/sessions/" not in interview.text

    script = client.get("/static/app.js").text
    assert "window.SpeechRecognition || window.webkitSpeechRecognition" in script
    assert 'recognition.lang = "de-DE"' in script
    assert "Dein Browser unterstützt die Spracheingabe" in script
    for state in ("recording", "processing", "done", "error"):
        assert state in script

    styles = client.get("/static/styles.css").text
    assert "--green-dark: #2F4A3A" in styles
    assert "@media (max-width: 42.99rem)" in styles
    assert "min-height: 3.25rem" in styles
    assert "overflow-x: hidden" in styles
    assert "table" not in styles


def test_complete_public_journey_and_customer_report(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client.post("/begin", follow_redirects=False)
    narration = (
        "Kunden rufen an oder schreiben. Ich notiere Aufträge auf Zetteln und muss "
        "bei Rückfragen oft suchen, wo der Auftrag liegt und wie weit er ist."
    )
    saved = client.post("/interview", data={"free_description": narration}, follow_redirects=False)
    assert saved.headers["location"] == "/saved"

    monkeypatch.setattr(routes, "generate_process_suggestions", lambda *_args: _suggestions())
    generated = client.post("/process-options/generate", follow_redirects=False)
    assert generated.headers["location"] == "/process-options"
    options_page = client.get("/process-options")
    assert "Diesen Ablauf ansehen" in options_page.text
    assert "Einen anderen Ablauf beschreiben" in options_page.text
    assert "/sessions/" not in options_page.text

    process_id = database_session.scalar(
        select(ProcessOption.process_id).order_by(ProcessOption.option_order)
    )
    monkeypatch.setattr(routes, "generate_process_understanding", lambda **_kwargs: _understanding())
    selected = client.post(
        "/process-options",
        data={"process_id": str(process_id), "prepare_summary": "yes"},
        follow_redirects=False,
    )
    assert selected.headers["location"] == "/process-details"
    summary = client.get("/process-details")
    assert "So haben wir deinen Ablauf verstanden" in summary.text
    assert "process-fallback" in summary.text
    assert "data-diagram-steps" in summary.text
    assert "Freie Korrektur einsprechen" in summary.text
    assert "Damit solltest du anfangen" not in summary.text

    diagram_script = client.get("/static/diagrams.js").text
    assert 'securityLevel: "strict"' in diagram_script
    assert "flowchart TD" in diagram_script
    assert "cleanLabel" in diagram_script

    follow_ups = FollowUpResult(
        questions=[
            FollowUpQuestion(
                question="Wie wird heute festgehalten, an welchem Ort ein Auftrag liegt?",
                issue_type="missing",
            ),
            FollowUpQuestion(
                question="Wer bestätigt heute, dass ein Auftrag fertig ist?",
                issue_type="critical_unknown",
            ),
        ]
    )
    monkeypatch.setattr(routes, "generate_follow_up_questions", lambda **_kwargs: follow_ups)
    confirmed = client.post(
        "/process-details",
        data={
            "summary_confirmed": "yes",
            "process_title": _understanding().process_name,
            "start_event": _understanding().start_event,
            "end_event": _understanding().end_event,
            "steps": _understanding().as_is_steps,
            "correction": "Vor der Übergabe wird der Auftrag geprüft.",
        },
        follow_redirects=False,
    )
    assert confirmed.headers["location"] == "/follow-ups"

    first_question = client.get("/follow-ups")
    assert follow_ups.questions[0].question in first_question.text
    assert follow_ups.questions[1].question not in first_question.text
    assert "Antwort einsprechen" in first_question.text
    assert "Weiß ich gerade nicht" in first_question.text
    answered = client.post(
        "/follow-ups",
        data={"follow_up_1": "Der Ort steht heute auf dem Auftragszettel."},
        follow_redirects=False,
    )
    assert answered.headers["location"] == "/follow-ups"
    second_question = client.get("/follow-ups")
    assert follow_ups.questions[1].question in second_question.text
    finished = client.post(
        "/follow-ups",
        data={"unknown_follow_up_2": "yes"},
        follow_redirects=False,
    )
    assert finished.headers["location"] == "/processing"
    processing = client.get("/processing")
    assert "Wir bringen deinen Ablauf gerade in ein klares Bild" in processing.text
    assert "Deine Angaben sind gespeichert" in processing.text
    assert "data-retry-analysis" in processing.text

    monkeypatch.setattr(routes, "generate_final_analysis", lambda **_kwargs: _final_result())
    analyzed = client.post("/analyze")
    assert analyzed.status_code == 200
    assert analyzed.json()["redirect_url"] == "/results"
    results = client.get("/results")
    for text in (
        "Jetzt ist klar, wo du am sinnvollsten anfangen kannst",
        "Heute sichtbar",
        "Ursache",
        "Folge",
        "Damit solltest du anfangen",
        "So läuft es heute",
        "So könnte der nächste, einfachere Ablauf aussehen",
        "Zwei weitere Möglichkeiten",
        "Das ist noch nicht ganz klar",
        "Ergebnis als PDF speichern",
        "Auswertung mit Derya besprechen",
    ):
        assert text in results.text
    assert "/sessions/" not in results.text
    assert "chunk" not in results.text.casefold()

    report = client.get("/report")
    assert report.status_code == 200
    for text in (
        "AI START MAP",
        "Derya Sarikaya",
        "deryaxsarikaya@gmail.com",
        "Bestätigter Ist-Prozess",
        "Größter Engpass",
        "Hauptempfehlung",
        "Nächster realistischer Soll-Prozess",
        "Drucken / als PDF speichern",
    ):
        assert text in report.text
    assert "/sessions/" not in report.text
    assert "session_id" not in report.text
    assert "RAG" not in report.text

    changed = client.post("/another-process", follow_redirects=False)
    assert changed.headers["location"] == "/process-options"
    assert database_session.scalar(select(Analysis)) is None


def test_follow_up_schema_allows_four_but_rejects_duplicates() -> None:
    four = FollowUpResult(
        questions=[
            FollowUpQuestion(
                question=f"Was passiert heute an Stelle {number}?",
                issue_type="missing",
            )
            for number in range(1, 5)
        ]
    )
    assert len(four.questions) == 4
    with pytest.raises(ValueError):
        FollowUpResult(questions=[four.questions[0], four.questions[0]])


def test_documented_decisions_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    ux_flow = (root / "UX_FLOW.md").read_text(encoding="utf-8")
    assert "Minimal-Change-Plan" in ux_flow
    assert "MediaRecorder" in ux_flow
    assert "window.print()" in ux_flow
    assert "keine Migration" in ux_flow
