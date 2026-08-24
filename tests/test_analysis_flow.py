from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.services import analysis_service
from app.openai_service import AIServiceError
from app.models import (
    AnalysisSession,
    InterviewQuestion,
    ProcessOption,
)
from app.questions import PROCESS_QUESTIONS
from app.rag_service import format_chunks_for_prompt, load_curated_chunks
from app.schemas import (
    FinalAnalysisResult,
    FollowUpQuestion,
    FollowUpResult,
    ProcessSuggestion,
    ProcessSuggestionResult,
    ProcessUnderstandingResult,
)
from app import repository
from tests.conftest import spec_payload

ROOT = Path(__file__).resolve().parents[1]


def _start_and_answer_intro(client: TestClient) -> int:
    response = client.post("/start", follow_redirects=False)
    session_id = int(response.headers["location"].split("/")[2])
    response = client.post(
        f"/sessions/{session_id}/interview",
        data={
            "business_context": "Kleiner regionaler Handwerksbetrieb.",
            "problem_overview": "Auftragsdaten werden mehrfach übertragen.",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    return session_id
@pytest.fixture(autouse=True)
def mock_retrieval(monkeypatch: pytest.MonkeyPatch) -> None:
    """Haelt die Wissenssuche aus den Tests heraus.

    Seit dem kurzen Weg gibt es nur noch eine Bindung: Der Prozessdienst
    schlaegt nicht mehr nach.
    """

    monkeypatch.setattr(
        analysis_service,
        "retrieval_context",
        lambda _query, _phase: ["Vergleichsmuster ohne Nutzerfakten"],
    )


def test_intro_answers_can_be_edited_before_the_result(
    client: TestClient,
    database_session: Session,
) -> None:
    session_id = _start_and_answer_intro(client)
    client.post(
        f"/sessions/{session_id}/interview",
        data={
            "business_context": "Geänderter Betrieb",
            "problem_overview": "Geändertes Problem",
        },
        follow_redirects=False,
    )
    stored = dict(
        database_session.execute(
            select(InterviewQuestion.question_key, InterviewQuestion.answer_text).where(
                InterviewQuestion.session_id == session_id,
                InterviewQuestion.question_phase == "context",
            )
        ).all()
    )
    assert stored == {
        "business_context": "Geänderter Betrieb",
        "problem_overview": "Geändertes Problem",
    }


def test_evaluation_directory_is_not_indexed() -> None:
    chunks = load_curated_chunks()
    assert all("evaluation" not in chunk.source_file for chunk in chunks)


def test_rag_chunks_are_loaded_only_from_curated_files() -> None:
    chunks = load_curated_chunks()
    curated_names = {
        path.name for path in Path("knowledge/archive/curated").glob("*.md")
    }
    assert len(chunks) == 111
    assert {chunk.source_file for chunk in chunks} == curated_names
    assert all("content_origin" in chunk.metadata for chunk in chunks)
    assert all("is_primary_evidence" in chunk.metadata for chunk in chunks)


def test_model_prompt_context_contains_no_internal_metadata() -> None:
    prompt_context = "\n".join(format_chunks_for_prompt(load_curated_chunks()))
    forbidden_markers = (
        "M-01",
        "Testfall",
        "Chunk",
        "pattern_id",
        "content_origin",
        "original_massage_transcript.pdf",
        "massage_rag_corpus.md",
    )
    assert all(
        marker.casefold() not in prompt_context.casefold()
        for marker in forbidden_markers
    )


@pytest.mark.parametrize(
    ("field_name", "marker"),
    [
        ("process_summary", "Bekannter Testfall M-01"),
        ("process_summary", "Interner Fall RB03-C01-01"),
        ("core_bottleneck", "Ableitung aus pattern_id"),
        ("engpass_titel", "Quelle content_origin"),
        ("engpass_text", "Aus einem Referenzfall übernommen"),
    ],
)
def test_internal_references_are_rejected_not_rewritten(
    field_name: str,
    marker: str,
) -> None:
    """Eine interne Referenz verwirft die Analyse, statt das Feld zu ersetzen.

    Frueher wurde das betroffene Feld auf "noch offen" gesetzt. Der
    Ergebnisvertrag ersetzt nichts mehr - ein Treffer ist ein Fehler.
    """

    with pytest.raises(ValidationError, match="Interne Wissensreferenzen"):
        FinalAnalysisResult.model_validate(spec_payload(**{field_name: marker}))


def test_internal_reference_inside_the_current_flow_is_rejected() -> None:
    payload = spec_payload()
    payload["as_is_steps"][0] = "Interner Chunk wurde verwendet"
    with pytest.raises(ValidationError, match="Interne Wissensreferenzen"):
        FinalAnalysisResult.model_validate(payload)


@pytest.mark.parametrize(
    "demo_slug", ["massage-salon", "etsy-3d-print", "carpet-cleaning"]
)
def test_demo_route_creates_session_and_reaches_the_result(
    client: TestClient,
    database_session: Session,
    demo_slug: str,
) -> None:
    """Die Vorführfälle laufen denselben kurzen Weg wie ein echter Kunde.

    Geprüft wird zusätzlich, dass aus einem Vorführfall keine internen
    Kennungen ins Modell und auf die Seite gelangen — die Fälle tragen sie in
    ihren Quelldateien.
    """

    antwort = client.get(f"/demo/{demo_slug}", follow_redirects=False)

    assert antwort.status_code == 303
    assert antwort.headers["location"] == "/processing"
    session_id = database_session.scalar(select(func.max(AnalysisSession.session_id)))
    assert session_id is not None
    assert repository.get_result(database_session, session_id) is None
    assert client.get("/processing").status_code == 200

    assert client.post(f"/sessions/{session_id}/analyze").status_code == 200
    client.post(f"/sessions/{session_id}/verstanden", data={"weiter": "ja"},
                follow_redirects=False)
    assert client.post(f"/sessions/{session_id}/analyze").status_code == 200

    assert repository.get_result(database_session, session_id) is not None
    seite = client.get(f"/sessions/{session_id}/results")
    assert seite.status_code == 200
    sichtbar = seite.text.casefold()
    for kennung in ("m-01", "testfall", "chunk", "pattern_id", "content_origin"):
        assert kennung not in sichtbar


def test_a_failing_second_call_shows_an_error_and_stores_nothing(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Scheitert der zweite Aufruf, sieht der Kunde einen Fehler — kein halbes
    Ergebnis.

    Der Warteschirm bleibt auf „pending" stehen, damit die Schaltfläche zum
    Wiederholen greift.
    """

    def scheitert(**_kwargs: object) -> None:
        raise AIServiceError("vorübergehender Modelldienstfehler")

    monkeypatch.setattr(analysis_service, "generate_result_part_two", scheitert)
    assert client.get("/demo/massage-salon", follow_redirects=False).status_code == 303
    # Erst der obere Teil, dann die Verstandenseite - der zweite Aufruf kommt
    # danach, und genau der scheitert hier.
    assert client.post("/analyze").json()["redirect_url"] == "/verstanden"
    client.post("/verstanden", data={"weiter": "ja"}, follow_redirects=False)

    antwort = client.post("/analyze")

    assert antwort.status_code == 503
    assert antwort.json()["state"] == "error"
    assert antwort.json()["message"] == (
        "Das hat gerade nicht geklappt. Versuch es bitte noch einmal."
    )
    assert client.get("/analysis-status").json()["state"] == "pending"
    session_id = database_session.scalar(select(func.max(AnalysisSession.session_id)))
    assert repository.get_result(database_session, session_id) is None
