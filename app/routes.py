from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db_session
from app.models import AnalysisSession, InterviewQuestion
from app.questions import INTRO_QUESTIONS


router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def _get_session_or_404(
    database_session: Session,
    session_id: int,
) -> AnalysisSession:
    analysis_session = database_session.scalar(
        select(AnalysisSession).where(AnalysisSession.session_id == session_id)
    )
    if analysis_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return analysis_session


def _get_questions(
    database_session: Session,
    session_id: int,
) -> list[InterviewQuestion]:
    return list(
        database_session.scalars(
            select(InterviewQuestion)
            .where(InterviewQuestion.session_id == session_id)
            .order_by(InterviewQuestion.question_order)
        )
    )


@router.get("/", response_class=HTMLResponse, name="landing")
def show_landing(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="landing.html")


@router.post("/start", name="start_session")
def start_session(database_session: Session = Depends(get_db_session)) -> RedirectResponse:
    analysis_session = AnalysisSession()
    try:
        database_session.add(analysis_session)
        database_session.flush()
        database_session.add_all(
            [
                InterviewQuestion(
                    session_id=analysis_session.session_id,
                    question_phase=question["phase"],
                    question_order=question["order"],
                    question_key=question["key"],
                    question_text=question["text"],
                )
                for question in INTRO_QUESTIONS
            ]
        )
        database_session.commit()
    except Exception:
        database_session.rollback()
        raise

    return RedirectResponse(
        url=f"/sessions/{analysis_session.session_id}/interview",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get(
    "/sessions/{session_id}/interview",
    response_class=HTMLResponse,
    name="show_interview",
)
def show_interview(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> HTMLResponse:
    _get_session_or_404(database_session, session_id)
    questions = _get_questions(database_session, session_id)
    answers = {
        question.question_key: question.answer_text or "" for question in questions
    }
    return templates.TemplateResponse(
        request=request,
        name="interview_start.html",
        context={
            "session_id": session_id,
            "questions": questions,
            "answers": answers,
            "error_message": None,
        },
    )


@router.post(
    "/sessions/{session_id}/interview",
    response_class=HTMLResponse,
    name="save_interview",
)
def save_interview(
    request: Request,
    session_id: int,
    business_context: str = Form(default=""),
    problem_overview: str = Form(default=""),
    database_session: Session = Depends(get_db_session),
) -> Response:
    _get_session_or_404(database_session, session_id)
    questions = _get_questions(database_session, session_id)
    answers = {
        "business_context": business_context.strip(),
        "problem_overview": problem_overview.strip(),
    }

    if not all(answers.values()):
        return templates.TemplateResponse(
            request=request,
            name="interview_start.html",
            context={
                "session_id": session_id,
                "questions": questions,
                "answers": answers,
                "error_message": "Bitte beantworte beide Fragen.",
            },
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )

    questions_by_key = {question.question_key: question for question in questions}
    for question_key, answer_text in answers.items():
        questions_by_key[question_key].answer_text = answer_text

    try:
        database_session.commit()
    except Exception:
        database_session.rollback()
        raise

    return RedirectResponse(
        url=f"/sessions/{session_id}/saved",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get(
    "/sessions/{session_id}/saved",
    response_class=HTMLResponse,
    name="show_saved_interview",
)
def show_saved_interview(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> HTMLResponse:
    _get_session_or_404(database_session, session_id)
    questions = _get_questions(database_session, session_id)
    return templates.TemplateResponse(
        request=request,
        name="interview_saved.html",
        context={"questions": questions},
    )
