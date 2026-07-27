from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import AnalysisSession, InterviewQuestion, ProcessOption
from app.questions import INTRO_QUESTIONS


def start_session(client: TestClient) -> int:
    response = client.post("/start", follow_redirects=False)
    assert response.status_code == 303
    return int(response.headers["location"].split("/")[2])


def test_landing_page_returns_200(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Mein Problem erzählen" in response.text
    assert "Dein Betrieb läuft. Aber vieles läuft nur" in response.text
    assert "business_context" not in response.text


def test_start_creates_exactly_one_session(
    client: TestClient,
    database_session: Session,
) -> None:
    start_session(client)

    session_count = database_session.scalar(
        select(func.count()).select_from(AnalysisSession)
    )
    assert session_count == 1


def test_start_stores_exactly_two_questions(
    client: TestClient,
    database_session: Session,
) -> None:
    session_id = start_session(client)

    question_count = database_session.scalar(
        select(func.count())
        .select_from(InterviewQuestion)
        .where(InterviewQuestion.session_id == session_id)
    )
    assert question_count == 2


def test_start_stores_expected_question_keys(
    client: TestClient,
    database_session: Session,
) -> None:
    session_id = start_session(client)

    question_keys = list(
        database_session.scalars(
            select(InterviewQuestion.question_key)
            .where(InterviewQuestion.session_id == session_id)
            .order_by(InterviewQuestion.question_order)
        )
    )
    assert question_keys == ["business_context", "problem_overview"]


def test_same_question_key_cannot_be_stored_twice(
    database_session: Session,
) -> None:
    analysis_session = AnalysisSession()
    database_session.add(analysis_session)
    database_session.flush()
    database_session.add_all(
        [
            InterviewQuestion(
                session_id=analysis_session.session_id,
                question_phase="context",
                question_order=1,
                question_key="business_context",
                question_text=INTRO_QUESTIONS[0]["text"],
            ),
            InterviewQuestion(
                session_id=analysis_session.session_id,
                question_phase="context",
                question_order=2,
                question_key="business_context",
                question_text=INTRO_QUESTIONS[0]["text"],
            ),
        ]
    )

    with pytest.raises(IntegrityError):
        database_session.commit()


def test_empty_answers_are_rejected(
    client: TestClient,
    database_session: Session,
) -> None:
    session_id = start_session(client)

    response = client.post(
        f"/sessions/{session_id}/interview",
        data={"business_context": "   ", "problem_overview": ""},
        follow_redirects=False,
    )

    assert response.status_code == 422
    assert "Bitte erzähl uns kurz, was dich im Alltag beschäftigt." in response.text
    answers = list(
        database_session.scalars(
            select(InterviewQuestion.answer_text).where(
                InterviewQuestion.session_id == session_id
            )
        )
    )
    assert answers == [None, None]


def test_valid_answers_are_stored_on_matching_questions(
    client: TestClient,
    database_session: Session,
) -> None:
    session_id = start_session(client)

    response = client.post(
        f"/sessions/{session_id}/interview",
        data={
            "business_context": "Eine kleine Fahrradwerkstatt.",
            "problem_overview": "Terminwünsche kommen über mehrere Kanäle.",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    stored_answers = dict(
        database_session.execute(
            select(InterviewQuestion.question_key, InterviewQuestion.answer_text)
            .where(InterviewQuestion.session_id == session_id)
        ).all()
    )
    assert stored_answers == {
        "business_context": "Eine kleine Fahrradwerkstatt.",
        "problem_overview": "Terminwünsche kommen über mehrere Kanäle.",
    }


def test_unknown_session_returns_controlled_404(client: TestClient) -> None:
    response = client.get("/sessions/999999/interview")

    assert response.status_code == 404
    assert "Das hat gerade nicht geklappt" in response.text


def test_saved_page_shows_questions_and_answers(client: TestClient) -> None:
    session_id = start_session(client)
    client.post(
        f"/sessions/{session_id}/interview",
        data={
            "business_context": "Ein regionaler Reparaturbetrieb.",
            "problem_overview": "Anfragen müssen mehrfach übertragen werden.",
        },
    )

    response = client.get(f"/sessions/{session_id}/saved")

    assert response.status_code == 200
    assert "Wir erkennen die wichtigsten Abläufe" in response.text
    assert "Gleich kannst du auswählen" in response.text
    assert "Abläufe jetzt erkennen" not in response.text
    assert "requestSubmit" in response.text


def test_only_one_process_option_can_be_selected_per_session(
    database_session: Session,
) -> None:
    analysis_session = AnalysisSession()
    database_session.add(analysis_session)
    database_session.flush()
    database_session.add(
        ProcessOption(
            session_id=analysis_session.session_id,
            option_order=1,
            process_name="Prozess A",
            start_event="Start A",
            end_event="Ende A",
            is_selected=True,
        )
    )
    database_session.commit()
    database_session.add(
        ProcessOption(
            session_id=analysis_session.session_id,
            option_order=2,
            process_name="Prozess B",
            start_event="Start B",
            end_event="Ende B",
            is_selected=True,
        )
    )

    with pytest.raises(IntegrityError):
        database_session.commit()
