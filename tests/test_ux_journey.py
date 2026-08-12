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
from tests.conftest import spec_payload


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
    return FinalAnalysisResult.model_validate(
        spec_payload(as_is_steps=_understanding().as_is_steps)
    )
@pytest.fixture(autouse=True)
def mock_retrieval(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(routes, "_retrieval_context", lambda _query, _phase: ["Internes Muster"])
    monkeypatch.setattr(routes, "_agent_pattern_context", lambda _query: ([], []))


def test_landing_voice_fallback_and_mobile_assets(client: TestClient) -> None:
    landing = client.get("/")
    assert landing.status_code == 200
    for text in (
        "FÜR SELBSTSTÄNDIGE UND KLEINE BETRIEBE",
        "Wo könnte KI dir im Alltag wirklich Arbeit abnehmen?",
        "Informationen kommen über mehrere digitale Kanäle.",
        "Drei einfache Schritte",
        "Meinen Ablauf beschreiben",
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
    assert "--ink: #183b32" in styles
    assert "@media (max-width: 42.99rem)" in styles
    assert "min-height: 3.35rem" in styles
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
    assert "Diesen Ablauf nehmen" in options_page.text
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
    assert "So habe ich deinen Ablauf verstanden." in summary.text
    assert "process-strip" in summary.text
    assert "data-diagram-steps" not in summary.text
    assert "Korrektur einsprechen" in summary.text
    assert "Dein eigentliches Problem" not in summary.text

    monkeypatch.setattr(
        routes,
        "generate_follow_up_questions",
        lambda **_kwargs: FollowUpResult(questions=[]),
    )
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
    assert confirmed.headers["location"] == "/processing"
    processing = client.get(confirmed.headers["location"])
    assert "Ich prüfe, welcher KI-Schritt zu deinem Ablauf passt." in processing.text
    assert "Deine Angaben sind gespeichert" in processing.text
    assert "data-retry-analysis" in processing.text

    monkeypatch.setattr(routes, "generate_final_analysis", lambda **_kwargs: _final_result())
    analyzed = client.post("/analyze")
    assert analyzed.status_code == 200, analyzed.text
    assert analyzed.json()["redirect_url"] == "/results"
    results = client.get("/results")
    for text in (
        "DEINE AUSWERTUNG",
        "So habe ich deinen heutigen Ablauf verstanden",
        "Hier lässt sich Arbeit aus deinem Ablauf nehmen",
        "SO WÜRDE DEINE LÖSUNG AUSSEHEN",
        "NACH DER EINRICHTUNG",
        "Das behältst du, das kommt dazu",
        "Das würde ich für dich bauen oder verbinden",
        "Das bleibt bei dir",
        "PDF speichern",
        "Umsetzung besprechen",
    ):
        assert text in results.text
    assert "/sessions/" not in results.text
    assert "chunk" not in results.text.casefold()

    report = client.get("/report")
    assert report.status_code == 200
    for text in (
        "AI START MAP",
        "Das ist der Engpass",
        "WO ARBEIT WEGFÄLLT",
        "SO WÜRDE DEINE LÖSUNG AUSSEHEN",
        "NACH DER EINRICHTUNG",
        "Was ich dafür einrichte",
        "Das bleibt bei dir",
        "PDF speichern",
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
    ux_flow = (root / "docs/flows/UX_FLOW.md").read_text(encoding="utf-8")
    assert "Minimal-Change-Plan" in ux_flow
    assert "MediaRecorder" in ux_flow
    assert "window.print()" in ux_flow
    assert "keine Migration" in ux_flow
