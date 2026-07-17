from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.database import get_db_session
from app.models import (
    Analysis,
    AnalysisSession,
    AutomationOpportunity,
    InterviewQuestion,
    ProcessOption,
)
from app.openai_service import (
    AIServiceError,
    generate_custom_process_boundary,
    generate_final_analysis,
    generate_follow_up_questions,
    generate_process_suggestions,
)
from app.questions import INTRO_QUESTIONS, PROCESS_QUESTIONS
from app.rag_service import (
    RagConfigurationError,
    format_chunks_for_prompt,
    retrieve_chunks,
)
from app.schemas import (
    FinalAnalysisResult,
    contains_internal_reference,
    contains_prohibited_customer_language,
)


router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
EVALUATION_FILE = ROOT_DIRECTORY / "knowledge" / "evaluation" / "evaluation_cases.json"
INTRO_KEYS = tuple(question["key"] for question in INTRO_QUESTIONS)
PROCESS_KEYS = tuple(question["key"] for question in PROCESS_QUESTIONS)
DEMO_EVALUATION_IDS = {
    "massage-salon": "EVAL-M-01",
    "etsy-3d-print": "EVAL-C-02",
    "carpet-cleaning": "EVAL-C-10",
}


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
    *,
    phase: str | None = None,
) -> list[InterviewQuestion]:
    statement = select(InterviewQuestion).where(
        InterviewQuestion.session_id == session_id
    )
    if phase is not None:
        statement = statement.where(InterviewQuestion.question_phase == phase)
        statement = statement.order_by(InterviewQuestion.question_order)
    else:
        statement = statement.order_by(InterviewQuestion.question_id)
    return list(database_session.scalars(statement))


def _selected_process(
    database_session: Session,
    session_id: int,
) -> ProcessOption | None:
    return database_session.scalar(
        select(ProcessOption).where(
            ProcessOption.session_id == session_id,
            ProcessOption.is_selected.is_(True),
        )
    )


def _process_options(
    database_session: Session,
    session_id: int,
) -> list[ProcessOption]:
    return list(
        database_session.scalars(
            select(ProcessOption)
            .where(ProcessOption.session_id == session_id)
            .order_by(ProcessOption.option_order)
        )
    )


def _all_answered(questions: list[InterviewQuestion]) -> bool:
    return bool(questions) and all(
        question.answer_text and question.answer_text.strip()
        for question in questions
    )


def _answer_payload(questions: list[InterviewQuestion]) -> dict[str, str]:
    return {
        question.question_key: (
            f"Frage: {question.question_text}\nAntwort: {question.answer_text}"
        )
        for question in questions
        if question.answer_text
    }


def _process_payload(process: ProcessOption) -> dict[str, str]:
    return {
        "process_name": process.process_name,
        "start_event": process.start_event,
        "end_event": process.end_event,
    }


def _query_text(
    questions: list[InterviewQuestion],
    process: ProcessOption | None = None,
) -> str:
    parts = [
        f"{question.question_text}\n{question.answer_text}"
        for question in questions
        if question.answer_text
    ]
    if process is not None:
        parts.insert(
            0,
            f"{process.process_name}\n{process.start_event}\n{process.end_event}",
        )
    return "\n\n".join(parts)


def _redirect(path: str) -> RedirectResponse:
    return RedirectResponse(path, status_code=status.HTTP_303_SEE_OTHER)


def _next_valid_path(database_session: Session, session_id: int) -> str:
    if database_session.get(Analysis, session_id) is not None:
        return f"/sessions/{session_id}/results"
    context_questions = _get_questions(
        database_session,
        session_id,
        phase="context",
    )
    if not _all_answered(context_questions):
        return f"/sessions/{session_id}/interview"
    options = _process_options(database_session, session_id)
    if not options:
        return f"/sessions/{session_id}/saved"
    if _selected_process(database_session, session_id) is None:
        return f"/sessions/{session_id}/process-options"
    process_questions = _get_questions(
        database_session,
        session_id,
        phase="process",
    )
    if len(process_questions) != len(PROCESS_QUESTIONS) or not _all_answered(
        process_questions
    ):
        return f"/sessions/{session_id}/process-details"
    follow_up_questions = _get_questions(
        database_session,
        session_id,
        phase="follow_up",
    )
    if follow_up_questions:
        if _all_answered(follow_up_questions):
            return f"/sessions/{session_id}/processing"
        return f"/sessions/{session_id}/follow-ups"
    return f"/sessions/{session_id}/processing"


def _render_error(
    request: Request,
    message: str,
    *,
    status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
    retry_path: str | None = None,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "error_title": "Die Analyse konnte nicht fortgesetzt werden.",
            "error_message": message,
            "retry_path": retry_path,
            "error_code": status_code,
        },
        status_code=status_code,
    )


def _retrieval_context(query: str, phase: str) -> list[str]:
    return format_chunks_for_prompt(retrieve_chunks(query, phase=phase))


def _ensure_process_questions(
    database_session: Session,
    session_id: int,
) -> None:
    existing_keys = {
        question.question_key
        for question in _get_questions(database_session, session_id, phase="process")
    }
    database_session.add_all(
        [
            InterviewQuestion(
                session_id=session_id,
                question_phase=question["phase"],
                question_order=question["order"],
                question_key=question["key"],
                question_text=question["text"],
            )
            for question in PROCESS_QUESTIONS
            if question["key"] not in existing_keys
        ]
    )


def _delete_follow_ups(database_session: Session, session_id: int) -> None:
    for question in _get_questions(
        database_session,
        session_id,
        phase="follow_up",
    ):
        database_session.delete(question)


def _acquire_session_write_lock(
    database_session: Session,
    session_id: int,
) -> bool:
    return bool(
        database_session.scalar(
            text("SELECT pg_try_advisory_xact_lock(:session_id)"),
            params={"session_id": session_id},
        )
    )


def _process_options_context(
    *,
    session_id: int,
    options: list[ProcessOption],
    selected_process: ProcessOption | None,
    error_message: str | None = None,
    custom_description: str = "",
) -> dict[str, object]:
    return {
        "session_id": session_id,
        "options": options,
        "selected_process_id": (
            selected_process.process_id if selected_process is not None else None
        ),
        "error_message": error_message,
        "custom_description": custom_description,
    }


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
    return _redirect(f"/sessions/{analysis_session.session_id}/interview")


@router.get(
    "/sessions/{session_id}/interview",
    response_class=HTMLResponse,
    name="show_interview",
)
def show_interview(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    _get_session_or_404(database_session, session_id)
    if database_session.get(Analysis, session_id) is not None:
        return _redirect(f"/sessions/{session_id}/results")
    questions = _get_questions(database_session, session_id, phase="context")
    return templates.TemplateResponse(
        request=request,
        name="interview_start.html",
        context={
            "session_id": session_id,
            "questions": questions,
            "answers": {
                question.question_key: question.answer_text or ""
                for question in questions
            },
            "error_message": None,
        },
    )


@router.post(
    "/sessions/{session_id}/interview",
    response_class=HTMLResponse,
    name="save_interview",
)
async def save_interview(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    _get_session_or_404(database_session, session_id)
    if database_session.get(Analysis, session_id) is not None:
        return _redirect(f"/sessions/{session_id}/results")
    if not _acquire_session_write_lock(database_session, session_id):
        database_session.rollback()
        return _redirect(f"/sessions/{session_id}/processing")
    questions = _get_questions(database_session, session_id, phase="context")
    form = await request.form()
    submitted = {key: str(form.get(key, "")).strip() for key in INTRO_KEYS}
    if not all(submitted.values()):
        return templates.TemplateResponse(
            request=request,
            name="interview_start.html",
            context={
                "session_id": session_id,
                "questions": questions,
                "answers": submitted,
                "error_message": "Bitte beantworte beide Fragen.",
            },
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    for question in questions:
        question.answer_text = submitted[question.question_key]
    try:
        database_session.commit()
    except Exception:
        database_session.rollback()
        raise
    if _process_options(database_session, session_id):
        return _redirect(f"/sessions/{session_id}/process-options")
    return _redirect(f"/sessions/{session_id}/saved")


@router.get(
    "/sessions/{session_id}/saved",
    response_class=HTMLResponse,
    name="show_saved_interview",
)
def show_saved_interview(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    _get_session_or_404(database_session, session_id)
    questions = _get_questions(database_session, session_id, phase="context")
    if not _all_answered(questions):
        return _redirect(f"/sessions/{session_id}/interview")
    if _process_options(database_session, session_id):
        return _redirect(_next_valid_path(database_session, session_id))
    return templates.TemplateResponse(
        request=request,
        name="interview_saved.html",
        context={"questions": questions, "session_id": session_id},
    )


@router.post(
    "/sessions/{session_id}/process-options/generate",
    name="generate_process_options",
)
def create_process_options(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    _get_session_or_404(database_session, session_id)
    context_questions = _get_questions(
        database_session,
        session_id,
        phase="context",
    )
    if not _all_answered(context_questions):
        return _redirect(f"/sessions/{session_id}/interview")
    if _process_options(database_session, session_id):
        return _redirect(f"/sessions/{session_id}/process-options")
    try:
        knowledge = _retrieval_context(
            _query_text(context_questions),
            "suggestion",
        )
        result = generate_process_suggestions(
            _answer_payload(context_questions),
            knowledge,
        )
        database_session.add_all(
            [
                ProcessOption(
                    session_id=session_id,
                    option_order=option_order,
                    process_name=suggestion.process_name,
                    start_event=suggestion.start_event,
                    end_event=suggestion.end_event,
                    reason=suggestion.reason,
                )
                for option_order, suggestion in enumerate(result.suggestions, start=1)
            ]
        )
        database_session.commit()
    except (AIServiceError, RagConfigurationError) as error:
        database_session.rollback()
        return _render_error(
            request,
            str(error),
            retry_path=f"/sessions/{session_id}/saved",
        )
    except Exception:
        database_session.rollback()
        raise
    return _redirect(f"/sessions/{session_id}/process-options")


@router.get(
    "/sessions/{session_id}/process-options",
    response_class=HTMLResponse,
    name="show_process_options",
)
def show_process_options(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    _get_session_or_404(database_session, session_id)
    if database_session.get(Analysis, session_id) is not None:
        return _redirect(f"/sessions/{session_id}/results")
    options = _process_options(database_session, session_id)
    if not options:
        return _redirect(f"/sessions/{session_id}/saved")
    return templates.TemplateResponse(
        request=request,
        name="process_options.html",
        context=_process_options_context(
            session_id=session_id,
            options=options,
            selected_process=_selected_process(database_session, session_id),
        ),
    )


@router.post(
    "/sessions/{session_id}/process-options",
    response_class=HTMLResponse,
    name="select_process",
)
async def select_process(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    _get_session_or_404(database_session, session_id)
    if database_session.get(Analysis, session_id) is not None:
        return _redirect(f"/sessions/{session_id}/results")
    if not _acquire_session_write_lock(database_session, session_id):
        database_session.rollback()
        return _redirect(f"/sessions/{session_id}/processing")
    options = _process_options(database_session, session_id)
    if not options:
        return _redirect(f"/sessions/{session_id}/saved")
    form = await request.form()
    selected_option: ProcessOption | None = None
    raw_process_id = str(form.get("process_id", "")).strip()
    if raw_process_id.isdigit():
        process_id = int(raw_process_id)
        selected_option = next(
            (option for option in options if option.process_id == process_id),
            None,
        )
    if selected_option is None:
        return templates.TemplateResponse(
            request=request,
            name="process_options.html",
            context=_process_options_context(
                session_id=session_id,
                options=options,
                selected_process=_selected_process(database_session, session_id),
                error_message="Bitte wähle genau einen Ablauf aus.",
            ),
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    previous_selection = _selected_process(database_session, session_id)
    try:
        selection_changed = (
            previous_selection is None
            or previous_selection.process_id != selected_option.process_id
        )
        if selection_changed and previous_selection is not None:
            previous_selection.is_selected = False
            database_session.flush()
        selected_option.is_selected = True
        if selection_changed:
            _delete_follow_ups(database_session, session_id)
        _ensure_process_questions(database_session, session_id)
        database_session.commit()
    except Exception:
        database_session.rollback()
        raise
    return _redirect(f"/sessions/{session_id}/process-details")


@router.post(
    "/sessions/{session_id}/process-options/custom",
    response_class=HTMLResponse,
    name="recognize_custom_process",
)
async def recognize_custom_process(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    _get_session_or_404(database_session, session_id)
    if database_session.get(Analysis, session_id) is not None:
        return _redirect(f"/sessions/{session_id}/results")
    if not _acquire_session_write_lock(database_session, session_id):
        database_session.rollback()
        return _redirect(f"/sessions/{session_id}/processing")
    options = _process_options(database_session, session_id)
    if not options:
        return _redirect(f"/sessions/{session_id}/saved")
    form = await request.form()
    description = str(form.get("custom_process_description", "")).strip()
    if not description:
        return templates.TemplateResponse(
            request=request,
            name="process_options.html",
            context=_process_options_context(
                session_id=session_id,
                options=options,
                selected_process=_selected_process(database_session, session_id),
                error_message="Bitte beschreibe kurz den Ablauf, den du untersuchen möchtest.",
            ),
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    context_questions = _get_questions(database_session, session_id, phase="context")
    try:
        boundary = generate_custom_process_boundary(
            description=description,
            context_answers=_answer_payload(context_questions),
        )
        raw_custom_id = str(form.get("custom_process_id", "")).strip()
        custom_option = next(
            (
                option
                for option in options
                if raw_custom_id.isdigit()
                and option.process_id == int(raw_custom_id)
            ),
            None,
        )
        if custom_option is None:
            custom_option = ProcessOption(
                session_id=session_id,
                option_order=max(option.option_order for option in options) + 1,
                process_name=boundary.process_name,
                start_event=boundary.start_event,
                end_event=boundary.end_event,
                reason=description,
            )
            database_session.add(custom_option)
        else:
            custom_option.process_name = boundary.process_name
            custom_option.start_event = boundary.start_event
            custom_option.end_event = boundary.end_event
            custom_option.reason = description
        database_session.commit()
    except AIServiceError as error:
        database_session.rollback()
        return templates.TemplateResponse(
            request=request,
            name="process_options.html",
            context=_process_options_context(
                session_id=session_id,
                options=options,
                selected_process=_selected_process(database_session, session_id),
                error_message=str(error),
                custom_description=description,
            ),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception:
        database_session.rollback()
        raise
    return _redirect(
        f"/sessions/{session_id}/process-options/custom/{custom_option.process_id}"
    )


@router.get(
    "/sessions/{session_id}/process-options/custom/{process_id}",
    response_class=HTMLResponse,
    name="confirm_custom_process",
)
def confirm_custom_process(
    request: Request,
    session_id: int,
    process_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    _get_session_or_404(database_session, session_id)
    if database_session.get(Analysis, session_id) is not None:
        return _redirect(f"/sessions/{session_id}/results")
    process = database_session.scalar(
        select(ProcessOption).where(
            ProcessOption.session_id == session_id,
            ProcessOption.process_id == process_id,
        )
    )
    if process is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return templates.TemplateResponse(
        request=request,
        name="process_confirm.html",
        context={
            "session_id": session_id,
            "process": process,
            "description": process.reason or "",
        },
    )


def _process_form_context(
    *,
    session_id: int,
    process: ProcessOption,
    questions: list[InterviewQuestion],
    answers: dict[str, str] | None = None,
    error_message: str | None = None,
) -> dict[str, object]:
    return {
        "session_id": session_id,
        "process": process,
        "questions": questions,
        "answers": answers
        or {
            question.question_key: question.answer_text or ""
            for question in questions
        },
        "question_help": {
            question["key"]: question["help"] for question in PROCESS_QUESTIONS
        },
        "error_message": error_message,
    }


@router.get(
    "/sessions/{session_id}/process-details",
    response_class=HTMLResponse,
    name="show_process_details",
)
def show_process_details(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    _get_session_or_404(database_session, session_id)
    if database_session.get(Analysis, session_id) is not None:
        return _redirect(f"/sessions/{session_id}/results")
    process = _selected_process(database_session, session_id)
    if process is None:
        return _redirect(_next_valid_path(database_session, session_id))
    questions = _get_questions(database_session, session_id, phase="process")
    if len(questions) != len(PROCESS_QUESTIONS):
        return _render_error(
            request,
            "Die Prozessfragen sind unvollständig.",
            status_code=status.HTTP_409_CONFLICT,
        )
    return templates.TemplateResponse(
        request=request,
        name="process_details.html",
        context=_process_form_context(
            session_id=session_id,
            process=process,
            questions=questions,
        ),
    )


@router.post(
    "/sessions/{session_id}/process-details",
    response_class=HTMLResponse,
    name="save_process_details",
)
async def save_process_details(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    _get_session_or_404(database_session, session_id)
    if database_session.get(Analysis, session_id) is not None:
        return _redirect(f"/sessions/{session_id}/results")
    if not _acquire_session_write_lock(database_session, session_id):
        database_session.rollback()
        return _redirect(f"/sessions/{session_id}/processing")
    process = _selected_process(database_session, session_id)
    if process is None:
        return _redirect(_next_valid_path(database_session, session_id))
    questions = _get_questions(database_session, session_id, phase="process")
    if len(questions) != len(PROCESS_QUESTIONS):
        return _render_error(
            request,
            "Die Prozessfragen sind unvollständig.",
            status_code=status.HTTP_409_CONFLICT,
        )
    form = await request.form()
    submitted = {key: str(form.get(key, "")).strip() for key in PROCESS_KEYS}
    if not all(submitted.values()):
        return templates.TemplateResponse(
            request=request,
            name="process_details.html",
            context=_process_form_context(
                session_id=session_id,
                process=process,
                questions=questions,
                answers=submitted,
                error_message="Bitte beantworte alle sieben Fragen.",
            ),
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    answers_changed = any(
        (question.answer_text or "") != submitted[question.question_key]
        for question in questions
    )
    for question in questions:
        question.answer_text = submitted[question.question_key]
    try:
        if answers_changed:
            _delete_follow_ups(database_session, session_id)
        database_session.commit()
    except Exception:
        database_session.rollback()
        raise
    return _continue_after_process_answers(
        request,
        session_id,
        database_session,
    )


def _continue_after_process_answers(
    request: Request,
    session_id: int,
    database_session: Session,
) -> Response:
    existing_follow_ups = _get_questions(
        database_session,
        session_id,
        phase="follow_up",
    )
    if existing_follow_ups:
        return _redirect(f"/sessions/{session_id}/follow-ups")
    process = _selected_process(database_session, session_id)
    if process is None:
        return _redirect(_next_valid_path(database_session, session_id))
    all_questions = _get_questions(database_session, session_id)
    try:
        knowledge = _retrieval_context(
            _query_text(all_questions, process),
            "follow_up",
        )
        result = generate_follow_up_questions(
            answers=_answer_payload(all_questions),
            selected_process=_process_payload(process),
            knowledge_chunks=knowledge,
        )
        database_session.add_all(
            [
                InterviewQuestion(
                    session_id=session_id,
                    question_phase="follow_up",
                    question_order=question_order,
                    question_key=f"follow_up_{question_order}",
                    question_text=follow_up.question,
                )
                for question_order, follow_up in enumerate(
                    result.questions,
                    start=1,
                )
            ]
        )
        database_session.commit()
    except (AIServiceError, RagConfigurationError) as error:
        database_session.rollback()
        return _render_error(
            request,
            str(error),
            retry_path=f"/sessions/{session_id}/process-details",
        )
    except Exception:
        database_session.rollback()
        raise
    if result.questions:
        return _redirect(f"/sessions/{session_id}/follow-ups")
    return _redirect(f"/sessions/{session_id}/processing")


def _follow_up_context(
    *,
    session_id: int,
    questions: list[InterviewQuestion],
    answers: dict[str, str] | None = None,
    error_message: str | None = None,
) -> dict[str, object]:
    return {
        "session_id": session_id,
        "questions": questions,
        "answers": answers
        or {
            question.question_key: question.answer_text or ""
            for question in questions
        },
        "error_message": error_message,
    }


@router.get(
    "/sessions/{session_id}/follow-ups",
    response_class=HTMLResponse,
    name="show_follow_ups",
)
def show_follow_ups(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    _get_session_or_404(database_session, session_id)
    if database_session.get(Analysis, session_id) is not None:
        return _redirect(f"/sessions/{session_id}/results")
    process_questions = _get_questions(
        database_session,
        session_id,
        phase="process",
    )
    if not _all_answered(process_questions):
        return _redirect(_next_valid_path(database_session, session_id))
    questions = _get_questions(database_session, session_id, phase="follow_up")
    if not questions:
        return _redirect(f"/sessions/{session_id}/process-details")
    return templates.TemplateResponse(
        request=request,
        name="follow_ups.html",
        context=_follow_up_context(session_id=session_id, questions=questions),
    )


@router.post(
    "/sessions/{session_id}/follow-ups",
    response_class=HTMLResponse,
    name="save_follow_ups",
)
async def save_follow_ups(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    _get_session_or_404(database_session, session_id)
    if database_session.get(Analysis, session_id) is not None:
        return _redirect(f"/sessions/{session_id}/results")
    if not _acquire_session_write_lock(database_session, session_id):
        database_session.rollback()
        return _redirect(f"/sessions/{session_id}/processing")
    questions = _get_questions(database_session, session_id, phase="follow_up")
    if not questions:
        return _redirect(f"/sessions/{session_id}/process-details")
    form = await request.form()
    submitted: dict[str, str] = {}
    for question in questions:
        unknown = str(form.get(f"unknown_{question.question_key}", "")) == "yes"
        submitted[question.question_key] = (
            "Ich weiß es nicht"
            if unknown
            else str(form.get(question.question_key, "")).strip()
        )
    if not all(submitted.values()):
        return templates.TemplateResponse(
            request=request,
            name="follow_ups.html",
            context=_follow_up_context(
                session_id=session_id,
                questions=questions,
                answers=submitted,
                error_message=(
                    "Bitte beantworte jede Rückfrage oder wähle „Ich weiß es nicht“ aus."
                ),
            ),
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    for question in questions:
        question.answer_text = submitted[question.question_key]
    try:
        database_session.commit()
    except Exception:
        database_session.rollback()
        raise
    return _redirect(f"/sessions/{session_id}/processing")


def _persist_final_analysis(
    database_session: Session,
    session_id: int,
    result: FinalAnalysisResult,
) -> None:
    if contains_internal_reference(result):
        raise ValueError("Die Analyse enthält eine interne Wissensreferenz.")
    database_session.add(
        Analysis(
            session_id=session_id,
            process_summary=result.process_summary,
            as_is_steps=result.as_is_steps,
            core_bottleneck=result.core_bottleneck,
            uncertainties=result.uncertainties,
        )
    )
    for opportunity in result.opportunities:
        database_session.add(
            AutomationOpportunity(
                session_id=session_id,
                rank=opportunity.rank,
                title=opportunity.title,
                problem=opportunity.problem,
                recommendation=opportunity.recommendation,
                benefit=opportunity.benefit,
                human_approval=opportunity.human_approval,
                first_step=opportunity.first_step,
                blueprint_json=(
                    result.blueprint.model_dump() if opportunity.rank == 1 else None
                ),
            )
        )
    database_session.commit()


def _generate_and_persist_final_analysis(
    session_id: int,
    database_session: Session,
) -> None:
    process = _selected_process(database_session, session_id)
    if process is None:
        raise ValueError("Für die Analyse fehlt der ausgewählte Ablauf.")
    all_questions = _get_questions(database_session, session_id)
    process_questions = [
        question
        for question in all_questions
        if question.question_phase == "process"
    ]
    follow_ups = [
        question
        for question in all_questions
        if question.question_phase == "follow_up"
    ]
    if not _all_answered(process_questions) or (
        follow_ups and not _all_answered(follow_ups)
    ):
        raise ValueError("Bitte vervollständige zuerst die offenen Angaben.")
    knowledge = _retrieval_context(
        _query_text(all_questions, process),
        "analysis",
    )
    result = generate_final_analysis(
        answers=_answer_payload(all_questions),
        selected_process=_process_payload(process),
        knowledge_chunks=knowledge,
    )
    _persist_final_analysis(database_session, session_id, result)


@router.get(
    "/sessions/{session_id}/processing",
    response_class=HTMLResponse,
    name="show_processing",
)
def show_processing(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    _get_session_or_404(database_session, session_id)
    if database_session.get(Analysis, session_id) is not None:
        return _redirect(f"/sessions/{session_id}/results")
    next_path = _next_valid_path(database_session, session_id)
    if next_path != f"/sessions/{session_id}/processing":
        return _redirect(next_path)
    return templates.TemplateResponse(
        request=request,
        name="processing.html",
        context={"session_id": session_id},
    )


@router.get(
    "/sessions/{session_id}/analysis-status",
    name="analysis_status",
)
def analysis_status(
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> JSONResponse:
    _get_session_or_404(database_session, session_id)
    complete = database_session.get(Analysis, session_id) is not None
    return JSONResponse(
        {
            "state": "complete" if complete else "pending",
            "redirect_url": (
                f"/sessions/{session_id}/results" if complete else None
            ),
        }
    )


@router.post("/sessions/{session_id}/analyze", name="analyze_session")
def analyze_session(
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> JSONResponse:
    _get_session_or_404(database_session, session_id)
    results_path = f"/sessions/{session_id}/results"
    if database_session.get(Analysis, session_id) is not None:
        return JSONResponse({"state": "complete", "redirect_url": results_path})
    next_path = _next_valid_path(database_session, session_id)
    if next_path != f"/sessions/{session_id}/processing":
        database_session.rollback()
        return JSONResponse(
            {
                "state": "error",
                "message": "Bitte vervollständige zuerst die offenen Angaben.",
                "redirect_url": next_path,
            },
            status_code=status.HTTP_409_CONFLICT,
        )
    lock_acquired = _acquire_session_write_lock(database_session, session_id)
    if not lock_acquired:
        database_session.rollback()
        return JSONResponse(
            {"state": "processing", "redirect_url": None},
            status_code=status.HTTP_409_CONFLICT,
        )
    if database_session.get(Analysis, session_id) is not None:
        database_session.rollback()
        return JSONResponse({"state": "complete", "redirect_url": results_path})
    try:
        _generate_and_persist_final_analysis(session_id, database_session)
    except (AIServiceError, RagConfigurationError) as error:
        database_session.rollback()
        return JSONResponse(
            {"state": "error", "message": str(error), "redirect_url": None},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except ValueError as error:
        database_session.rollback()
        return JSONResponse(
            {"state": "error", "message": str(error), "redirect_url": None},
            status_code=status.HTTP_409_CONFLICT,
        )
    except Exception:
        database_session.rollback()
        return JSONResponse(
            {
                "state": "error",
                "message": (
                    "Die Ergebnisse konnten nicht vollständig erstellt werden. "
                    "Es wurden keine Teilergebnisse übernommen."
                ),
                "redirect_url": None,
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return JSONResponse({"state": "complete", "redirect_url": results_path})


@router.get(
    "/sessions/{session_id}/results",
    response_class=HTMLResponse,
    name="show_results",
)
def show_results(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    _get_session_or_404(database_session, session_id)
    analysis = database_session.get(Analysis, session_id)
    if analysis is None:
        return _redirect(_next_valid_path(database_session, session_id))
    process = _selected_process(database_session, session_id)
    if process is None:
        return _render_error(
            request,
            "Für diese Analyse fehlt der ausgewählte Prozess.",
            status_code=status.HTTP_409_CONFLICT,
        )
    opportunities = list(
        database_session.scalars(
            select(AutomationOpportunity)
            .where(AutomationOpportunity.session_id == session_id)
            .order_by(AutomationOpportunity.rank)
        )
    )
    if len(opportunities) != 3:
        return _render_error(
            request,
            "Die Ergebnisse sind unvollständig.",
            status_code=status.HTTP_409_CONFLICT,
        )
    blueprint = next(
        (
            opportunity.blueprint_json
            for opportunity in opportunities
            if opportunity.rank == 1
        ),
        None,
    )
    visible_result = {
        "process_name": process.process_name,
        "process_summary": analysis.process_summary,
        "as_is_steps": analysis.as_is_steps,
        "core_bottleneck": analysis.core_bottleneck,
        "uncertainties": analysis.uncertainties,
        "opportunities": [
            {
                "title": opportunity.title,
                "problem": opportunity.problem,
                "recommendation": opportunity.recommendation,
                "benefit": opportunity.benefit,
                "human_approval": opportunity.human_approval,
                "first_step": opportunity.first_step,
            }
            for opportunity in opportunities
        ],
        "blueprint": blueprint,
    }
    summary_start = analysis.process_summary.strip().casefold()
    process_name = process.process_name.strip().casefold()
    summary_repeats_title = summary_start.startswith(
        (
            process_name,
            "prozessname:",
            "ausgewählter prozess:",
            "der prozess heißt",
            "aus den vorliegenden angaben",
            "auf grundlage der daten",
            "quelle:",
            "die rekonstruktion bleibt unsicher",
        )
    )
    if (
        contains_internal_reference(visible_result)
        or contains_prohibited_customer_language(visible_result)
        or summary_repeats_title
    ):
        return _render_error(
            request,
            "Die Ergebnisse konnten nicht sicher angezeigt werden. Bitte starte "
            "eine neue Analyse.",
            status_code=status.HTTP_409_CONFLICT,
        )
    opportunity_categories = {
        opportunity.rank: _opportunity_category(opportunity)
        for opportunity in opportunities
    }
    return templates.TemplateResponse(
        request=request,
        name="results.html",
        context={
            "session_id": session_id,
            "process": process,
            "analysis": analysis,
            "opportunities": opportunities,
            "opportunity_categories": opportunity_categories,
            "blueprint": blueprint,
        },
    )


def _opportunity_category(opportunity: AutomationOpportunity) -> str:
    opportunity_text = (
        f"{opportunity.title} {opportunity.recommendation} "
        f"{opportunity.benefit}"
    ).casefold()
    automation_markers = (
        "automatisch",
        "automatisiert",
        "automatisierung",
        "benachrichtigung auslösen",
        "selbstständig übertragen",
    )
    digital_markers = (
        "digital",
        "zentrale auftragskarte",
        "statusübersicht",
        "zentraler auftragsstatus",
        "gemeinsame strukturierte erfassung",
    )
    if any(marker in opportunity_text for marker in automation_markers):
        return "Automatisierung"
    if any(marker in opportunity_text for marker in digital_markers):
        return "Einfache Digitalisierung"
    return "Prozessstandardisierung"


def _load_evaluation_case(evaluation_id: str) -> dict[str, object]:
    if not EVALUATION_FILE.is_file():
        raise RagConfigurationError("Die vorbereiteten Demo-Daten wurden nicht gefunden.")
    try:
        evaluation_data = json.loads(EVALUATION_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        raise RagConfigurationError(
            "Die vorbereiteten Demo-Daten konnten nicht gelesen werden."
        ) from error
    evaluation_case = next(
        (
            case
            for case in evaluation_data.get("cases", [])
            if case.get("evaluation_id") == evaluation_id
        ),
        None,
    )
    if evaluation_case is None:
        raise RagConfigurationError("Die vorbereiteten Demo-Daten sind unvollständig.")
    return evaluation_case


def _list_text(value: object, prefix: str) -> str:
    if not isinstance(value, list) or not value:
        return "Unbekannt"
    items = [str(item).strip() for item in value if str(item).strip()]
    if not items:
        return "Unbekannt"
    return f"{prefix}: " + "; ".join(items)


def _create_demo_session(
    database_session: Session,
    evaluation_case: dict[str, object],
) -> int:
    process_name = str(
        evaluation_case.get("expected_core_process") or "Unbekannter Prozess"
    ).strip()
    bottleneck = str(
        evaluation_case.get("expected_core_bottleneck") or "Unbekannt"
    ).strip()
    clarification_topics = _list_text(
        evaluation_case.get("required_questions"),
        "Noch zu klären",
    )
    approval_gates = _list_text(
        evaluation_case.get("human_approval_gates"),
        "Menschliche Prüfungen",
    )
    forbidden_actions = _list_text(
        evaluation_case.get("forbidden_recommendations"),
        "Nicht autonom ausführen",
    )
    process_answers = {
        "process_boundary": "Unbekannt",
        "actual_steps": "Unbekannt",
        "business_object_and_result": (
            "Weitere Angaben zum Gegenstand und Ergebnis sind unbekannt."
        ),
        "roles_systems_and_handoffs": "Unbekannt",
        "volume_time_and_impact": "Unbekannt",
        "rules_and_exceptions": clarification_topics,
        "approval_and_success": f"{approval_gates}. {forbidden_actions}.",
    }
    analysis_session = AnalysisSession()
    database_session.add(analysis_session)
    database_session.flush()
    context_answers = {
        "business_context": "Weitere Unternehmensangaben sind unbekannt.",
        "problem_overview": bottleneck,
    }
    database_session.add_all(
        [
            InterviewQuestion(
                session_id=analysis_session.session_id,
                question_phase=question["phase"],
                question_order=question["order"],
                question_key=question["key"],
                question_text=question["text"],
                answer_text=context_answers[question["key"]],
            )
            for question in INTRO_QUESTIONS
        ]
    )
    database_session.add(
        ProcessOption(
            session_id=analysis_session.session_id,
            option_order=1,
            process_name=process_name,
            start_event="Unbekannt",
            end_event="Unbekannt",
            reason=bottleneck,
            is_selected=True,
        )
    )
    database_session.add_all(
        [
            InterviewQuestion(
                session_id=analysis_session.session_id,
                question_phase=question["phase"],
                question_order=question["order"],
                question_key=question["key"],
                question_text=question["text"],
                answer_text=process_answers[question["key"]],
            )
            for question in PROCESS_QUESTIONS
        ]
    )
    database_session.commit()
    return analysis_session.session_id


@router.get("/demo/{demo_slug}", name="run_demo")
def run_demo(
    request: Request,
    demo_slug: str,
    database_session: Session = Depends(get_db_session),
) -> Response:
    evaluation_id = DEMO_EVALUATION_IDS.get(demo_slug)
    if evaluation_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    try:
        evaluation_case = _load_evaluation_case(evaluation_id)
        session_id = _create_demo_session(database_session, evaluation_case)
    except RagConfigurationError as error:
        database_session.rollback()
        return _render_error(
            request,
            str(error),
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    except Exception:
        database_session.rollback()
        raise
    return _redirect(f"/sessions/{session_id}/processing")
