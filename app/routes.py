from __future__ import annotations

import json
import base64
import hashlib
import hmac
import logging
import os
import secrets
from datetime import date
from pathlib import Path
from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.agent_config import AGENT_HEURISTICS
from app.agent_service import (
    ProcessState,
    evaluate_readiness_and_next_action,
    extract_process_state,
    normalized_question_similarity,
    question_can_change_core_output,
    search_diagnostic_knowledge,
)
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
    generate_process_understanding,
    generate_process_suggestions,
    get_embedding_call_count,
    get_openai_call_count,
    reset_openai_call_count,
)
from app.questions import INTRO_QUESTIONS, PROCESS_QUESTIONS
from app.rag_service import RagConfigurationError
from app.rag_service import (
    format_chunks_for_prompt,
    retrieve_agent_patterns,
    retrieve_solution_workflows,
)
from app.llm_classification import classify_narrative
from app.recommendation_service import select_recommendation
from app.solution_knowledge import (
    build_solution_query,
    extract_confirmed_channels,
    find_inference_patterns,
    load_solution_workflows,
    output_structure_context,
    output_structure_for,
    select_solution_workflows,
    solution_workflow_context,
)
from app.schemas import (
    FinalAnalysisResult,
    contains_internal_reference,
    contains_prohibited_customer_language,
)


router = APIRouter()
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
EVALUATION_FILE = ROOT_DIRECTORY / "knowledge" / "evaluation" / "cases_ten_kmu.json"
INTRO_KEYS = tuple(question["key"] for question in INTRO_QUESTIONS)
PROCESS_KEYS = tuple(question["key"] for question in PROCESS_QUESTIONS)
DEMO_EVALUATION_IDS = {
    "massage-salon": "EVAL-M-01",
    "etsy-3d-print": "EVAL-C-02",
    "carpet-cleaning": "EVAL-C-10",
}
DEMO_SESSION_SLUGS: dict[int, str] = {}
SESSION_COOKIE = "ai_start_map_session"
SESSION_SIGNING_KEY = (
    os.getenv("SESSION_SIGNING_KEY", "").encode("utf-8") or secrets.token_bytes(32)
)


def _session_cookie_value(session_id: int) -> str:
    payload = str(session_id).encode("ascii")
    signature = hmac.new(SESSION_SIGNING_KEY, payload, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(payload + b"." + signature).decode("ascii")


def _session_id_from_cookie(request: Request) -> int:
    encoded = request.cookies.get(SESSION_COOKIE, "")
    try:
        raw = base64.urlsafe_b64decode(encoded.encode("ascii"))
        payload, signature = raw.split(b".", 1)
        expected = hmac.new(SESSION_SIGNING_KEY, payload, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        return int(payload.decode("ascii"))
    except (ValueError, UnicodeError, TypeError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None


def _set_session_cookie(response: Response, request: Request, session_id: int) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        _session_cookie_value(session_id),
        httponly=True,
        samesite="lax",
        secure=request.url.scheme == "https",
    )


def _publicize_redirect(response: Response, session_id: int) -> Response:
    if not isinstance(response, RedirectResponse):
        return response
    location = response.headers.get("location", "")
    prefix = f"/sessions/{session_id}"
    if not location.startswith(prefix):
        return response
    suffix = location[len(prefix):]
    public_paths = {
        "/interview": "/interview",
        "/saved": "/saved",
        "/process-options": "/process-options",
        "/process-details": "/process-details",
        "/follow-ups": "/follow-ups",
        "/processing": "/processing",
        "/results": "/results",
        "/report": "/report",
    }
    if suffix.startswith("/process-options/custom/"):
        response.headers["location"] = "/process-options/custom/confirm"
    elif suffix in public_paths:
        response.headers["location"] = public_paths[suffix]
    return response


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


def _diagnostic_agent_state(
    database_session: Session,
    session_id: int,
    process: ProcessOption,
) -> ProcessState:
    questions = _get_questions(database_session, session_id)
    answers = {
        question.question_key: question.answer_text or "" for question in questions
    }
    question_records = [
        {
            "question_key": question.question_key,
            "question_text": question.question_text,
            "answer_text": question.answer_text or "",
        }
        for question in questions
    ]
    return extract_process_state(
        answers=answers,
        selected_process=_process_payload(process),
        questions=question_records,
    )


def _is_repeated_follow_up(
    question_text: str,
    existing_questions: list[InterviewQuestion],
) -> bool:
    return any(
        normalized_question_similarity(question_text, existing.question_text) >= 0.8
        for existing in existing_questions
    )


def _question_reason(question_text: str) -> str:
    normalized = question_text.casefold()
    reasons = (
        (
            ("regal", "ablage", "platz"),
            "So erkennen wir, ob die Suche durch die Zuordnung zum Ablageplatz entsteht.",
        ),
        (
            ("preis", "freigabe", "bestätig", "entscheid"),
            "So bleibt klar, welche Entscheidung zwingend bei einem Menschen bleibt.",
        ),
        (
            ("daten", "angaben", "erfasst", "notiert"),
            "So erkennen wir, ob KI schon mit verlässlichen Angaben arbeiten kann.",
        ),
        (
            ("wer ", "zuständig"),
            "So erkennen wir, an welcher Übergabe der aktuelle Stand verloren geht.",
        ),
        (
            ("ausnahme", "abweich", "anders"),
            "So bleibt der erste Test auch bei den häufigsten Ausnahmen realistisch.",
        ),
    )
    for markers, reason in reasons:
        if any(marker in normalized for marker in markers):
            return reason
    return ""


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
    return [
        evidence.content
        for evidence in search_diagnostic_knowledge(query, phase=phase)
    ]


def _agent_pattern_context(query: str) -> tuple[list[str], list[str]]:
    """Retrieve optional interview patterns without weakening Python guardrails."""

    try:
        patterns = retrieve_agent_patterns(
            query,
            allowed_types={
                "agent_decision_pattern",
                "next_question_pattern",
                "contradiction_pattern",
                "agent_stop_rule",
                "tool_selection_pattern",
                "agent_guardrail",
            },
            top_k=3,
        )
    except (AIServiceError, RagConfigurationError):
        logger.warning("agent_pattern_retrieval.fallback pattern_count=0")
        return [], []
    pattern_types = [pattern.chunk_type for pattern in patterns]
    logger.info(
        "agent_pattern_retrieval.selected pattern_count=%d pattern_types=%s",
        len(patterns),
        pattern_types,
    )
    return format_chunks_for_prompt(patterns), pattern_types


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


@router.post("/begin", name="begin_journey")
def begin_journey(
    request: Request,
    database_session: Session = Depends(get_db_session),
) -> Response:
    response = start_session(database_session)
    session_id = int(response.headers["location"].split("/")[2])
    public_response = _redirect("/interview")
    _set_session_cookie(public_response, request, session_id)
    return public_response


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
    free_description = str(form.get("free_description", "")).strip()
    submitted = (
        {key: free_description for key in INTRO_KEYS}
        if free_description
        else {key: str(form.get(key, "")).strip() for key in INTRO_KEYS}
    )
    if not all(submitted.values()):
        return templates.TemplateResponse(
            request=request,
            name="interview_start.html",
            context={
                "session_id": session_id,
                "questions": questions,
                "answers": submitted,
                "error_message": "Bitte erzähl uns kurz, was dich im Alltag beschäftigt.",
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
        if str(form.get("prepare_summary", "")) == "yes":
            database_session.flush()
            context_questions = _get_questions(database_session, session_id, phase="context")
            understanding = generate_process_understanding(
                answers=_answer_payload(context_questions),
                selected_process=_process_payload(selected_option),
            )
            selected_option.process_name = understanding.process_name
            selected_option.start_event = understanding.start_event
            selected_option.end_event = understanding.end_event
            process_answers = {
                "process_boundary": json.dumps(
                    {
                        "process_name": understanding.process_name,
                        "start_event": understanding.start_event,
                        "end_event": understanding.end_event,
                    },
                    ensure_ascii=False,
                ),
                "actual_steps": json.dumps(understanding.as_is_steps, ensure_ascii=False),
                "business_object_and_result": json.dumps(understanding.confirmed_facts, ensure_ascii=False),
                "roles_systems_and_handoffs": json.dumps(
                    {
                        "difficult_points": understanding.difficult_points,
                        "problem_step_indexes": understanding.problem_step_indexes,
                    },
                    ensure_ascii=False,
                ),
                "volume_time_and_impact": json.dumps(understanding.open_points, ensure_ascii=False),
                "rules_and_exceptions": "Noch keine Korrektur ergänzt.",
                "approval_and_success": "Noch nicht aus der freien Beschreibung geklärt.",
            }
            for question in _get_questions(database_session, session_id, phase="process"):
                question.answer_text = process_answers[question.question_key]
        database_session.commit()
    except AIServiceError:
        database_session.rollback()
        return templates.TemplateResponse(
            request=request,
            name="process_options.html",
            context=_process_options_context(
                session_id=session_id,
                options=options,
                selected_process=previous_selection,
                error_message=(
                    "Wir konnten den Ablauf gerade nicht sicher ordnen. "
                    "Deine Erzählung ist gespeichert – bitte versuche es noch einmal."
                ),
            ),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
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
    answer_map = {
        question.question_key: question.answer_text or "" for question in questions
    }

    def parsed_json(key: str, fallback: object) -> object:
        value = answer_map.get(key, "")
        if not value:
            return fallback
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return fallback

    boundary = parsed_json("process_boundary", {})
    stored_steps = parsed_json("actual_steps", [])
    stored_facts = parsed_json("business_object_and_result", [])
    difficulty_data = parsed_json("roles_systems_and_handoffs", {})
    stored_open_points = parsed_json("volume_time_and_impact", [])
    steps = (
        [str(step) for step in stored_steps]
        if isinstance(stored_steps, list) and stored_steps
        else [process.start_event, process.end_event]
    )
    facts = [str(item) for item in stored_facts] if isinstance(stored_facts, list) else []
    difficult_points = (
        [str(item) for item in difficulty_data.get("difficult_points", [])]
        if isinstance(difficulty_data, dict)
        else []
    )
    problem_indexes = (
        [int(index) for index in difficulty_data.get("problem_step_indexes", []) if isinstance(index, int)]
        if isinstance(difficulty_data, dict)
        else []
    )
    open_points = (
        [str(item) for item in stored_open_points]
        if isinstance(stored_open_points, list)
        else []
    )
    return {
        "session_id": session_id,
        "process": process,
        "questions": questions,
        "answers": answers or answer_map,
        "process_title": (
            str(boundary.get("process_name", process.process_name))
            if isinstance(boundary, dict)
            else process.process_name
        ),
        "start_event": process.start_event,
        "end_event": process.end_event,
        "steps": steps[:5],
        "confirmed_facts": facts,
        "difficult_points": difficult_points,
        "problem_step_indexes": problem_indexes,
        "open_points": open_points,
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
    if str(form.get("summary_confirmed", "")) == "yes":
        process_title = str(form.get("process_title", "")).strip()
        start_event = str(form.get("start_event", "")).strip()
        end_event = str(form.get("end_event", "")).strip()
        steps = [str(step).strip() for step in form.getlist("steps") if str(step).strip()]
        correction = str(form.get("correction", "")).strip()
        if not process_title or not start_event or not end_event or len(steps) < 2:
            return templates.TemplateResponse(
                request=request,
                name="process_details.html",
                context=_process_form_context(
                    session_id=session_id,
                    process=process,
                    questions=questions,
                    error_message="Bitte lass mindestens zwei konkrete Ablaufschritte stehen.",
                ),
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            )
        process.process_name = process_title
        process.start_event = start_event
        process.end_event = end_event
        updates = {
            "process_boundary": json.dumps(
                {"process_name": process_title, "start_event": start_event, "end_event": end_event},
                ensure_ascii=False,
            ),
            "actual_steps": json.dumps(steps, ensure_ascii=False),
            "rules_and_exceptions": correction or "Keine zusätzliche Korrektur angegeben.",
        }
        for question in questions:
            if question.question_key in updates:
                question.answer_text = updates[question.question_key]
        _delete_follow_ups(database_session, session_id)
        try:
            database_session.commit()
        except Exception:
            database_session.rollback()
            raise
        return _continue_after_process_answers(request, session_id, database_session)
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
    if existing_follow_ups and not _all_answered(existing_follow_ups):
        return _redirect(f"/sessions/{session_id}/follow-ups")
    if existing_follow_ups:
        return _redirect(f"/sessions/{session_id}/processing")
    process = _selected_process(database_session, session_id)
    if process is None:
        return _redirect(_next_valid_path(database_session, session_id))
    agent_state = _diagnostic_agent_state(database_session, session_id, process)
    decision = evaluate_readiness_and_next_action(agent_state)
    logger.info(
        "interview_agent.policy action=%s follow_up_count=%d information_gap=%s",
        decision.next_action,
        agent_state.follow_up_count,
        decision.information_gap or "none",
    )
    if decision.next_action in {"ANALYZE", "STOP"}:
        return _redirect(f"/sessions/{session_id}/processing")
    remaining_budget = (
        AGENT_HEURISTICS.maximum_visible_follow_ups - len(existing_follow_ups)
    )
    if remaining_budget <= 0:
        return _redirect(f"/sessions/{session_id}/processing")
    all_questions = _get_questions(database_session, session_id)
    try:
        query = _query_text(all_questions, process)
        interview_classification = classify_narrative(query)
        inference_patterns = find_inference_patterns(
            interview_classification.problem_family_ids,
            channels=extract_confirmed_channels(query),
            limit=2,
        )
        agent_pattern_knowledge, agent_pattern_types = _agent_pattern_context(query)
        if decision.next_action == "RETRIEVE":
            agent_state.rag_evidence = search_diagnostic_knowledge(
                query, phase="follow_up"
            )
            decision = evaluate_readiness_and_next_action(agent_state)
            if decision.next_action in {"ANALYZE", "STOP", "RETRIEVE"}:
                return _redirect(f"/sessions/{session_id}/processing")
            knowledge = [evidence.content for evidence in agent_state.rag_evidence]
        else:
            knowledge = _retrieval_context(query, "follow_up")
        knowledge.extend(
            [
                (
                    "Unbestätigte Hypothese aus geprüftem Interviewwissen: "
                    f"{pattern.hypothesis}\n"
                    f"Beobachtbare Prüffrage: {pattern.verification_question}\n"
                    "Diese Hypothese ist kein Nutzerfakt."
                )
                for pattern in inference_patterns
            ]
        )
        knowledge.extend(agent_pattern_knowledge)
        logger.info(
            "interview_agent.decision action=%s follow_up_count=%d "
            "information_gap=%s agent_pattern_types=%s",
            decision.next_action,
            agent_state.follow_up_count,
            decision.information_gap or "none",
            agent_pattern_types,
        )
        result = generate_follow_up_questions(
            answers=_answer_payload(all_questions),
            selected_process=_process_payload(process),
            knowledge_chunks=knowledge,
        )
        generated_candidate_texts = [
            follow_up.question
            for follow_up in result.questions
            if not _is_repeated_follow_up(follow_up.question, existing_follow_ups)
            and question_can_change_core_output(follow_up.question, agent_state)
        ]
        candidate_texts = []
        if (
            decision.possible_next_question
            and not _is_repeated_follow_up(
                decision.possible_next_question, existing_follow_ups
            )
            and question_can_change_core_output(
                decision.possible_next_question, agent_state
            )
        ):
            candidate_texts.append(decision.possible_next_question)
        candidate_texts.extend(
            item for item in generated_candidate_texts if item not in candidate_texts
        )
        if not candidate_texts:
            candidate_texts.extend(
                pattern.verification_question
                for pattern in inference_patterns
                if not _is_repeated_follow_up(
                    pattern.verification_question, existing_follow_ups
                )
                and question_can_change_core_output(
                    pattern.verification_question, agent_state
                )
            )
        preferred_limit = (
            AGENT_HEURISTICS.complex_follow_up_maximum
            if decision.next_action == "CLARIFY"
            else AGENT_HEURISTICS.normal_follow_up_maximum
        )
        candidate_texts = candidate_texts[: min(remaining_budget, preferred_limit)]
        next_order = len(existing_follow_ups) + 1
        database_session.add_all(
            [
                InterviewQuestion(
                    session_id=session_id,
                    question_phase="follow_up",
                    question_order=next_order + offset,
                    question_key=f"follow_up_{next_order + offset}",
                    question_text=question_text,
                )
                for offset, question_text in enumerate(candidate_texts)
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
    if candidate_texts:
        return _redirect(f"/sessions/{session_id}/follow-ups")
    return _redirect(f"/sessions/{session_id}/processing")


def _follow_up_context(
    *,
    session_id: int,
    questions: list[InterviewQuestion],
    answers: dict[str, str] | None = None,
    error_message: str | None = None,
) -> dict[str, object]:
    current_question = next(
        (question for question in questions if not (question.answer_text or "").strip()),
        None,
    )
    unanswered_count = sum(not (question.answer_text or "").strip() for question in questions)
    return {
        "session_id": session_id,
        "questions": questions,
        "answers": answers
        or {
            question.question_key: question.answer_text or ""
            for question in questions
        },
        "error_message": error_message,
        "current_question": current_question,
        "is_last_question": unanswered_count == 1,
        "answered_count": len(questions) - unanswered_count,
        "question_reason": (
            _question_reason(current_question.question_text)
            if current_question is not None
            else ""
        ),
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
    if _all_answered(questions):
        return _redirect(f"/sessions/{session_id}/processing")
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
    submitted: dict[str, str] = {
        question.question_key: question.answer_text or "" for question in questions
    }
    for question in questions:
        unknown = str(form.get(f"unknown_{question.question_key}", "")) == "yes"
        supplied_answer = str(form.get(question.question_key, "")).strip()
        if unknown or supplied_answer:
            submitted[question.question_key] = "Ich weiß es gerade nicht" if unknown else supplied_answer
    current_question = next(
        (question for question in questions if not (question.answer_text or "").strip()),
        None,
    )
    if current_question is not None and not submitted[current_question.question_key]:
        return templates.TemplateResponse(
            request=request,
            name="follow_ups.html",
            context=_follow_up_context(
                session_id=session_id,
                questions=questions,
                answers=submitted,
                error_message=(
                    "Bitte antworte kurz oder wähle „Weiß ich gerade nicht“ aus."
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
    remaining = [
        question for question in questions if not (question.answer_text or "").strip()
    ]
    answered_follow_ups = len(questions) - len(remaining)
    if remaining and answered_follow_ups >= AGENT_HEURISTICS.normal_follow_up_minimum:
        process = _selected_process(database_session, session_id)
        if process is not None:
            decision = evaluate_readiness_and_next_action(
                _diagnostic_agent_state(database_session, session_id, process)
            )
            if decision.next_action not in {"ASK", "CLARIFY"}:
                for question in remaining:
                    database_session.delete(question)
                database_session.commit()
                remaining = []
    if remaining:
        return _redirect(f"/sessions/{session_id}/follow-ups")
    return _continue_after_process_answers(request, session_id, database_session)


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
            as_is_steps={
                "steps": result.as_is_steps,
                "problem_step_indexes": result.as_is_problem_step_indexes,
                "to_be_steps": result.to_be_steps or result.future_process,
            },
            core_bottleneck=result.core_bottleneck,
            uncertainties={
                "items": result.uncertainties,
                "bottleneck": {
                    "symptom": result.bottleneck_symptom,
                    "cause": result.bottleneck_cause or result.core_bottleneck,
                    "effect": result.bottleneck_effect,
                },
                "core_output": {
                    "primary_recommendation": result.primary_recommendation,
                    "promise": result.promise,
                    "short_reason": result.short_reason,
                    "before_process": result.before_process,
                    "future_process": result.future_process,
                    "sample_output": result.sample_output.model_dump(),
                    "user_action": result.user_action,
                    "ai_task": result.ai_task,
                    "visible_result": result.visible_result,
                    "human_check": result.human_check,
                    "customer_benefits": result.customer_benefits,
                    "required_prerequisites": result.required_prerequisites,
                    "implementation_path": result.implementation_path,
                    "later_stage": result.later_stage,
                    "secondary_opportunities": [
                        item.model_dump() for item in result.secondary_opportunities
                    ],
                    "error_boundaries": result.error_boundaries,
                },
            },
        )
    )
    stored_opportunities = [
        {
            "title": result.primary_recommendation,
            "description": result.short_reason,
            "benefit": result.customer_benefits[0],
        },
        *[item.model_dump() | {"benefit": item.description} for item in result.secondary_opportunities],
    ]
    for rank, opportunity in enumerate(stored_opportunities, start=1):
        database_session.add(
            AutomationOpportunity(
                session_id=session_id,
                rank=rank,
                title=str(opportunity["title"]),
                problem=result.short_reason,
                recommendation=str(opportunity.get("description") or result.primary_recommendation),
                benefit=str(opportunity["benefit"]),
                human_approval=result.human_check,
                first_step=result.implementation_path[0],
                blueprint_json={
                    "contract_version": "recommendation-v2",
                    "sample_output": result.sample_output.model_dump() if rank == 1 else None,
                    "implementation_path": result.implementation_path if rank == 1 else [],
                    "later_stage": result.later_stage if rank == 1 else "",
                },
            )
        )
    database_session.commit()


def _massage_demo_fallback_result() -> FinalAnalysisResult:
    """Fixed result used only after an explicit massage demo service failure."""

    return FinalAnalysisResult(
        primary_recommendation="Terminanfragen mit KI ordnen und Kapazität sicher prüfen",
        promise=(
            "Aus jeder Nachricht entsteht eine vollständige Terminanfrage mit "
            "sichtbarem Kapazitätsstatus."
        ),
        short_reason=(
            "Anfragen und Verfügbarkeiten liegen verteilt. Dadurch fehlt ein "
            "verlässlicher gemeinsamer Stand."
        ),
        before_process=[
            "Eine Anfrage kommt über einen vorhandenen Kanal an.",
            "Du gleichst Wunschzeit und verfügbare Besetzung ab.",
            "Du bestätigst oder korrigierst den Termin.",
        ],
        future_process=[
            "Du leitest die geschriebene oder gesprochene Anfrage weiter.",
            "Die KI ordnet Behandlung, Dauer, Personenzahl und Wunschzeit.",
            "Du prüfst Kapazität und offene Angaben.",
            "Du bestätigst den Termin und aktualisierst den Status.",
        ],
        sample_output={
            "title": "Terminanfrage",
            "fields": [
                {"label": "Behandlung", "value": "noch offen"},
                {"label": "Wunschzeit", "value": "noch offen"},
                {"label": "Kapazitätsstatus", "value": "zu prüfen"},
            ],
            "open_items": ["Verfügbare Person bestätigen"],
            "preview_notice": "Vorschau – die endgültigen Angaben prüfst du selbst.",
        },
        user_action="Du gibst die geschriebene oder gesprochene Terminanfrage ein.",
        ai_task=(
            "Die KI ordnet die Angaben und markiert fehlende oder unklare Werte."
        ),
        visible_result="Du erhältst eine Terminanfrage mit eindeutigem Prüfstatus.",
        human_check=(
            "Du prüfst die tatsächliche Verfügbarkeit und bestätigst jeden Termin."
        ),
        customer_benefits=[
            "Du siehst den aktuellen Stand ohne Suche.",
            "Fehlende Angaben fallen vor der Bestätigung auf.",
            "Jede Anfrage folgt demselben übersichtlichen Aufbau.",
        ],
        required_prerequisites=[
            "Eine gemeinsame Anfrageübersicht",
            "Klare Statuswerte",
            "Aktuell gepflegte Personalverfügbarkeit",
        ],
        implementation_path=[
            "Pflichtangaben und Statuswerte für Terminanfragen festlegen.",
            "Einen gemeinsamen Eingang mit der Anfrageübersicht verbinden.",
            "KI-Entwurf und menschliche Kapazitätsfreigabe einrichten.",
        ],
        later_stage=(
            "Nach bestätigter Kapazität kann die KI eine Nachricht zur manuellen "
            "Freigabe vorbereiten."
        ),
        secondary_opportunities=[],
        error_boundaries=[
            "Fehlende Angaben bleiben sichtbar und verhindern eine verbindliche Zusage.",
            "Unklare Personalverfügbarkeit wird nicht automatisch aufgelöst.",
        ],
        process_summary=(
            "Eine Anfrage kommt über einen der vorhandenen Kanäle an, wird mit der "
            "verfügbaren Besetzung abgeglichen und anschließend bestätigt."
        ),
        as_is_steps=[
            "Eine Terminanfrage geht über einen vorhandenen Kanal ein.",
            "Behandlung, Wunschzeit und verfügbare Besetzung werden abgeglichen.",
            "Ein Mensch bestätigt oder korrigiert den Termin.",
        ],
        core_bottleneck=(
            "Mehrere Kanäle, wechselnde Verfügbarkeit und manuelle Bestätigung "
            "erzeugen keinen gemeinsamen aktuellen Stand."
        ),
        bottleneck_symptom="Anfragen und Terminstatus sind verteilt.",
        bottleneck_cause="Es fehlt eine gemeinsame Übersicht mit klaren Statuswerten.",
        bottleneck_effect="Abgleich und Bestätigung erfordern wiederholte Rückfragen.",
        as_is_problem_step_indexes=[0, 1],
        to_be_steps=[
            "Anfrage in einer gemeinsamen Übersicht erfassen.",
            "Fehlende Angaben sichtbar markieren.",
            "Verfügbarkeit durch einen Menschen prüfen.",
            "Termin bestätigen und Status aktualisieren.",
        ],
        uncertainties=[
            "Wegen eines vorübergehenden KI-Dienstfehlers wird hier das fest "
            "vorbereitete Ergebnis der Massage-Demo gezeigt."
        ],
    )


def _persist_explicit_demo_fallback(
    database_session: Session,
    session_id: int,
) -> bool:
    if DEMO_SESSION_SLUGS.get(session_id) != "massage-salon":
        return False
    try:
        _persist_final_analysis(
            database_session,
            session_id,
            _massage_demo_fallback_result(),
        )
    except Exception as error:
        database_session.rollback()
        logger.exception(
            "analysis.demo_fallback_failed exception_type=%s exception_message=%s",
            type(error).__name__,
            str(error),
        )
        return False
    return True


def _generate_and_persist_final_analysis(
    session_id: int,
    database_session: Session,
) -> None:
    total_started = perf_counter()
    stage = "state_load"
    try:
        stage_started = perf_counter()
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
        logger.info(
            "analysis.stage_complete stage=state_load duration_seconds=%.3f",
            perf_counter() - stage_started,
        )

        stage = "retrieval"
        stage_started = perf_counter()
        query_text = _query_text(all_questions, process)
        classification = classify_narrative(query_text)
        problem_family_ids = classification.problem_family_ids
        gates = classification.gates
        logger.info(
            "analysis.classification method=%s problem_families=%s",
            classification.method,
            problem_family_ids,
        )
        retrieval_query = (
            f"{query_text}\n\nDiagnostischer Fokus: Ursache, Problemfamilie, "
            "konkretes Lösungsmuster, Voraussetzung und Guardrail; Kanaleignung, "
            "Prozess-/Datenreife und menschliche Freigabe getrennt prüfen."
        )
        knowledge = _retrieval_context(retrieval_query, "analysis")
        logger.info(
            "analysis.stage_complete stage=retrieval duration_seconds=%.3f",
            perf_counter() - stage_started,
        )

        stage = "agent_state"
        stage_started = perf_counter()
        agent_state = _diagnostic_agent_state(
            database_session,
            session_id,
            process,
        ).model_dump()
        logger.info(
            "analysis.stage_complete stage=agent_state duration_seconds=%.3f",
            perf_counter() - stage_started,
        )

        stage = "recommendation_selection"
        stage_started = perf_counter()
        recommendation = select_recommendation(problem_family_ids, gates)
        confirmed_channels = extract_confirmed_channels(query_text)
        all_solution_workflows = load_solution_workflows()
        deterministic_workflows = select_solution_workflows(
            recommendation.primary.solution_id,
            channels=confirmed_channels,
            limit=2,
            workflows=all_solution_workflows,
        )
        solution_query = build_solution_query(
            problem_family_ids=problem_family_ids,
            solution_pattern_id=recommendation.primary.solution_id,
            bottleneck=process.process_name,
            channels=confirmed_channels,
        )
        solution_retrieval_method = "deterministic"
        selected_workflows = deterministic_workflows
        try:
            semantic_chunks = retrieve_solution_workflows(
                solution_query,
                solution_pattern_id=recommendation.primary.solution_id,
                channels=confirmed_channels,
                top_k=2,
            )
            by_workflow_id = {
                item.workflow_id: item for item in all_solution_workflows
            }
            semantic_workflows = [
                by_workflow_id[chunk.chunk_id]
                for chunk in semantic_chunks
                if chunk.chunk_id in by_workflow_id
            ]
            if semantic_workflows:
                selected_workflows = semantic_workflows
                solution_retrieval_method = "semantic"
        except (AIServiceError, RagConfigurationError) as error:
            logger.warning(
                "solution_retrieval.fallback method=deterministic "
                "exception_type=%s exception_message=%s",
                type(error).__name__,
                str(error),
            )
        recommendation_context = recommendation.model_dump()
        recommendation_context["output_structure"] = output_structure_context(
            output_structure_for(recommendation.primary.solution_id)
        )
        recommendation_context["solution_workflows"] = solution_workflow_context(
            selected_workflows
        )
        recommendation_context["solution_retrieval"] = {
            "query": solution_query,
            "eligible_count": sum(
                item.solution_pattern_id == recommendation.primary.solution_id
                and item.batch_scope == "in_scope"
                for item in all_solution_workflows
            ),
            "returned_count": len(selected_workflows),
            "method": solution_retrieval_method,
        }
        logger.info(
            "recommendation.selected problem_families=%s primary_solution=%s "
            "secondary_solutions=%s excluded_solutions=%s gates=%s",
            problem_family_ids,
            recommendation.primary.solution_id,
            [item.solution_id for item in recommendation.secondary],
            recommendation.excluded_reasons,
            gates.model_dump(),
        )
        logger.info(
            "analysis.stage_complete stage=recommendation_selection duration_seconds=%.3f",
            perf_counter() - stage_started,
        )

        stage = "final_openai_call"
        stage_started = perf_counter()
        result = generate_final_analysis(
            answers=_answer_payload(all_questions),
            selected_process=_process_payload(process),
            knowledge_chunks=knowledge,
            agent_state=agent_state,
            recommendation_context=recommendation_context,
        )
        logger.info(
            "recommendation.output_validated validation_result=passed "
            "primary_solution=%s secondary_count=%d",
            recommendation.primary.solution_id,
            len(result.secondary_opportunities),
        )
        logger.info(
            "analysis.stage_complete stage=final_openai_call duration_seconds=%.3f "
            "openai_calls=%d retrieval_embedding_calls=%d",
            perf_counter() - stage_started,
            get_openai_call_count(),
            get_embedding_call_count(),
        )

        stage = "jsonb_persistence"
        stage_started = perf_counter()
        _persist_final_analysis(database_session, session_id, result)
        logger.info(
            "analysis.stage_complete stage=jsonb_persistence duration_seconds=%.3f",
            perf_counter() - stage_started,
        )
    except Exception as error:
        logger.exception(
            "analysis.failed section=%s exception_type=%s exception_message=%s "
            "duration_seconds=%.3f openai_calls=%d retrieval_embedding_calls=%d",
            stage,
            type(error).__name__,
            str(error),
            perf_counter() - total_started,
            get_openai_call_count(),
            get_embedding_call_count(),
        )
        raise
    logger.info(
        "analysis.completed duration_seconds=%.3f openai_calls=%d "
        "retrieval_embedding_calls=%d",
        perf_counter() - total_started,
        get_openai_call_count(),
        get_embedding_call_count(),
    )


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
    reset_openai_call_count()
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
    except AIServiceError as error:
        database_session.rollback()
        if _persist_explicit_demo_fallback(database_session, session_id):
            DEMO_SESSION_SLUGS.pop(session_id, None)
            logger.warning(
                "analysis.demo_fallback_used demo=massage-salon exception_type=%s",
                type(error).__name__,
            )
            return JSONResponse(
                {
                    "state": "complete",
                    "redirect_url": results_path,
                    "demo_fallback": True,
                }
            )
        return JSONResponse(
            {"state": "error", "message": str(error), "redirect_url": None},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except RagConfigurationError as error:
        database_session.rollback()
        logger.exception(
            "analysis.failed section=retrieval exception_type=%s exception_message=%s",
            type(error).__name__,
            str(error),
        )
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
    except Exception as error:
        database_session.rollback()
        logger.exception(
            "analysis.failed section=request exception_type=%s exception_message=%s",
            type(error).__name__,
            str(error),
        )
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
    DEMO_SESSION_SLUGS.pop(session_id, None)
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
    if not 1 <= len(opportunities) <= 3:
        return _render_error(
            request,
            "Die Ergebnisse sind unvollständig.",
            status_code=status.HTTP_409_CONFLICT,
        )
    result_view = _result_view(analysis, opportunities)
    blueprint = result_view["blueprint"]
    visible_result = {
        "process_name": process.process_name,
        "result": result_view,
        "stored_analysis": {
            "process_summary": analysis.process_summary,
            "as_is_steps": analysis.as_is_steps,
            "core_bottleneck": analysis.core_bottleneck,
            "uncertainties": analysis.uncertainties,
        },
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
            "result": result_view,
        },
    )


def _result_view(
    analysis: Analysis,
    opportunities: list[AutomationOpportunity],
) -> dict[str, object]:
    step_data = analysis.as_is_steps
    if isinstance(step_data, dict):
        as_is_steps = [str(item) for item in step_data.get("steps", [])]
        problem_indexes = [
            int(index)
            for index in step_data.get("problem_step_indexes", [])
            if isinstance(index, int)
        ]
        to_be_steps = [str(item) for item in step_data.get("to_be_steps", [])]
    else:
        as_is_steps = [str(item) for item in step_data]
        problem_indexes = []
        to_be_steps = []

    uncertainty_data = analysis.uncertainties
    if isinstance(uncertainty_data, dict):
        uncertainties = [str(item) for item in uncertainty_data.get("items", [])]
        raw_bottleneck = uncertainty_data.get("bottleneck", {})
        bottleneck = raw_bottleneck if isinstance(raw_bottleneck, dict) else {}
        raw_core_output = uncertainty_data.get("core_output", {})
        core_output = raw_core_output if isinstance(raw_core_output, dict) else {}
    else:
        uncertainties = [str(item) for item in uncertainty_data]
        bottleneck = {}
        core_output = {}

    opportunity_views: list[dict[str, object]] = []
    blueprint: dict[str, object] | None = None
    for opportunity in opportunities:
        stored_meta = opportunity.blueprint_json
        if isinstance(stored_meta, dict) and "category" in stored_meta:
            meta = stored_meta
            if opportunity.rank == 1 and isinstance(meta.get("blueprint"), dict):
                blueprint = meta["blueprint"]
        else:
            meta = {}
            if opportunity.rank == 1 and isinstance(stored_meta, dict):
                blueprint = stored_meta
        opportunity_views.append(
            {
                "rank": opportunity.rank,
                "title": opportunity.title,
                "problem": opportunity.problem,
                "recommendation": opportunity.recommendation,
                "benefit": opportunity.benefit,
                "human_approval": opportunity.human_approval,
                "first_step": opportunity.first_step,
                "category": meta.get("category") or _opportunity_category(opportunity),
                "prerequisite": meta.get("prerequisite") or opportunity.first_step,
                "mini_test": meta.get("mini_test") or [opportunity.first_step],
                "effort": meta.get("effort") or ("niedrig" if opportunity.rank == 1 else "mittel"),
                "acceptance_risk": meta.get("acceptance_risk") or "Im kleinen Test mit den beteiligten Personen prüfen.",
            }
        )
    if not to_be_steps and blueprint:
        to_be_steps = [str(item) for item in blueprint.get("workflow_steps", [])]
    first = opportunity_views[0]
    blueprint_steps = (
        [str(item) for item in blueprint.get("workflow_steps", [])]
        if isinstance(blueprint, dict)
        else []
    )
    primary_mini_test = [str(item) for item in first["mini_test"]][:4]
    is_new_contract = bool(core_output.get("primary_recommendation"))
    legacy_human_check = str(core_output.get("human_check") or first["human_approval"])
    if not any(marker in legacy_human_check.casefold() for marker in ("du ", "dein", "dir ")):
        legacy_human_check = f"Du prüfst und bestätigst: {legacy_human_check}"
    secondary = core_output.get("secondary_opportunities")
    if not isinstance(secondary, list):
        secondary = [
            {"title": item["title"], "description": item["benefit"]}
            for item in opportunity_views[1:3]
        ]
    sample_output = core_output.get("sample_output")
    if not isinstance(sample_output, dict):
        legacy_output = str(core_output.get("ai_output") or "Ein prüfbarer Entwurf")
        sample_output = {
            "title": legacy_output,
            "fields": [{"label": "Ergebnis", "value": legacy_output}],
            "open_items": [],
            "attachments": [],
            "preview_notice": "Vorschau – die endgültigen Angaben prüfst du selbst.",
        }
    user_action = str(core_output.get("user_action") or core_output.get("ai_input") or "Vorhandene Angaben eingeben")
    if not any(marker in user_action.casefold() for marker in ("du ", "dein", "dir ")):
        user_action = f"Du gibst ein: {user_action}."
    implementation_path = core_output.get("implementation_path")
    if not isinstance(implementation_path, list) or len(implementation_path) < 2:
        implementation_path = core_output.get("weekly_test") or blueprint_steps or primary_mini_test
    stored_error_boundaries = core_output.get("error_boundaries")
    if not isinstance(stored_error_boundaries, list):
        stored_error_boundaries = [] if is_new_contract else [str(first["acceptance_risk"])]
    return {
        "as_is_steps": as_is_steps,
        "problem_step_indexes": problem_indexes,
        "to_be_steps": to_be_steps,
        "uncertainties": uncertainties,
        "bottleneck": {
            "symptom": bottleneck.get("symptom") or first["problem"],
            "cause": bottleneck.get("cause") or analysis.core_bottleneck,
            "effect": bottleneck.get("effect") or first["benefit"],
        },
        "opportunities": opportunity_views,
        "blueprint": blueprint,
        "primary_recommendation": core_output.get("primary_recommendation") or first["title"],
        "promise": core_output.get("promise") or core_output.get("ai_support") or first["benefit"],
        "short_reason": core_output.get("short_reason") or core_output.get("core_problem") or analysis.core_bottleneck,
        "before_process": core_output.get("before_process") or as_is_steps[:3],
        "future_process": core_output.get("future_process") or to_be_steps[:4],
        "sample_output": sample_output,
        "user_action": user_action,
        "ai_task": core_output.get("ai_task") or "Angaben erkennen und ordnen",
        "visible_result": core_output.get("visible_result") or core_output.get("ai_output") or sample_output["title"],
        "human_check": legacy_human_check,
        "customer_benefits": core_output.get("customer_benefits") or [first["benefit"]],
        "required_prerequisites": core_output.get("required_prerequisites")
        or ([] if is_new_contract else [first["prerequisite"]]),
        "implementation_path": [str(item) for item in implementation_path][:4],
        "later_stage": core_output.get("later_stage") or core_output.get("later_automation") or "",
        "secondary_opportunities": secondary[:2],
        "human_decisions": [legacy_human_check],
        "error_boundaries": [str(item) for item in stored_error_boundaries][:3],
        "current_process_summary": analysis.process_summary,
    }


@router.get(
    "/sessions/{session_id}/report",
    response_class=HTMLResponse,
    name="show_report",
)
def show_report(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    _get_session_or_404(database_session, session_id)
    analysis = database_session.get(Analysis, session_id)
    process = _selected_process(database_session, session_id)
    opportunities = list(
        database_session.scalars(
            select(AutomationOpportunity)
            .where(AutomationOpportunity.session_id == session_id)
            .order_by(AutomationOpportunity.rank)
        )
    )
    if analysis is None or process is None or not 1 <= len(opportunities) <= 3:
        return _redirect(_next_valid_path(database_session, session_id))
    result = _result_view(analysis, opportunities)
    if contains_internal_reference(result):
        return _render_error(request, "Der Bericht konnte nicht sicher angezeigt werden.", status_code=status.HTTP_409_CONFLICT)
    return templates.TemplateResponse(
        request=request,
        name="report.html",
        context={
            "process": process,
            "analysis": analysis,
            "result": result,
            "analysis_date": date.today().strftime("%d.%m.%Y"),
        },
    )


@router.post("/sessions/{session_id}/another-process", name="analyze_another_process")
def analyze_another_process(
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    _get_session_or_404(database_session, session_id)
    if not _acquire_session_write_lock(database_session, session_id):
        database_session.rollback()
        return _redirect(f"/sessions/{session_id}/results")
    analysis = database_session.get(Analysis, session_id)
    if analysis is not None:
        database_session.delete(analysis)
    selected = _selected_process(database_session, session_id)
    if selected is not None:
        selected.is_selected = False
    _delete_follow_ups(database_session, session_id)
    database_session.commit()
    return _redirect(f"/sessions/{session_id}/process-options")


@router.get("/interview", response_class=HTMLResponse, name="show_interview_public")
def show_interview_public(request: Request, database_session: Session = Depends(get_db_session)) -> Response:
    session_id = _session_id_from_cookie(request)
    return _publicize_redirect(show_interview(request, session_id, database_session), session_id)


@router.post("/interview", response_class=HTMLResponse, name="save_interview_public")
async def save_interview_public(request: Request, database_session: Session = Depends(get_db_session)) -> Response:
    session_id = _session_id_from_cookie(request)
    return _publicize_redirect(await save_interview(request, session_id, database_session), session_id)


@router.get("/saved", response_class=HTMLResponse, name="show_saved_public")
def show_saved_public(request: Request, database_session: Session = Depends(get_db_session)) -> Response:
    session_id = _session_id_from_cookie(request)
    return _publicize_redirect(show_saved_interview(request, session_id, database_session), session_id)


@router.post("/process-options/generate", name="generate_process_options_public")
def generate_process_options_public(request: Request, database_session: Session = Depends(get_db_session)) -> Response:
    session_id = _session_id_from_cookie(request)
    return _publicize_redirect(create_process_options(request, session_id, database_session), session_id)


@router.get("/process-options", response_class=HTMLResponse, name="show_process_options_public")
def show_process_options_public(request: Request, database_session: Session = Depends(get_db_session)) -> Response:
    session_id = _session_id_from_cookie(request)
    return _publicize_redirect(show_process_options(request, session_id, database_session), session_id)


@router.post("/process-options", response_class=HTMLResponse, name="select_process_public")
async def select_process_public(request: Request, database_session: Session = Depends(get_db_session)) -> Response:
    session_id = _session_id_from_cookie(request)
    return _publicize_redirect(await select_process(request, session_id, database_session), session_id)


@router.post("/process-options/custom", response_class=HTMLResponse, name="recognize_custom_process_public")
async def recognize_custom_process_public(request: Request, database_session: Session = Depends(get_db_session)) -> Response:
    session_id = _session_id_from_cookie(request)
    return _publicize_redirect(await recognize_custom_process(request, session_id, database_session), session_id)


@router.get("/process-options/custom/confirm", response_class=HTMLResponse, name="confirm_custom_process_public")
def confirm_custom_process_public(request: Request, database_session: Session = Depends(get_db_session)) -> Response:
    session_id = _session_id_from_cookie(request)
    options = _process_options(database_session, session_id)
    if not options:
        return _redirect("/process-options")
    return confirm_custom_process(request, session_id, options[-1].process_id, database_session)


@router.get("/process-details", response_class=HTMLResponse, name="show_process_details_public")
def show_process_details_public(request: Request, database_session: Session = Depends(get_db_session)) -> Response:
    session_id = _session_id_from_cookie(request)
    return _publicize_redirect(show_process_details(request, session_id, database_session), session_id)


@router.post("/process-details", response_class=HTMLResponse, name="save_process_details_public")
async def save_process_details_public(request: Request, database_session: Session = Depends(get_db_session)) -> Response:
    session_id = _session_id_from_cookie(request)
    return _publicize_redirect(await save_process_details(request, session_id, database_session), session_id)


@router.get("/follow-ups", response_class=HTMLResponse, name="show_follow_ups_public")
def show_follow_ups_public(request: Request, database_session: Session = Depends(get_db_session)) -> Response:
    session_id = _session_id_from_cookie(request)
    return _publicize_redirect(show_follow_ups(request, session_id, database_session), session_id)


@router.post("/follow-ups", response_class=HTMLResponse, name="save_follow_ups_public")
async def save_follow_ups_public(request: Request, database_session: Session = Depends(get_db_session)) -> Response:
    session_id = _session_id_from_cookie(request)
    return _publicize_redirect(await save_follow_ups(request, session_id, database_session), session_id)


@router.get("/processing", response_class=HTMLResponse, name="show_processing_public")
def show_processing_public(request: Request, database_session: Session = Depends(get_db_session)) -> Response:
    session_id = _session_id_from_cookie(request)
    return _publicize_redirect(show_processing(request, session_id, database_session), session_id)


@router.get("/analysis-status", name="analysis_status_public")
def analysis_status_public(request: Request, database_session: Session = Depends(get_db_session)) -> JSONResponse:
    session_id = _session_id_from_cookie(request)
    response = analysis_status(session_id, database_session)
    payload = json.loads(response.body)
    if payload.get("redirect_url"):
        payload["redirect_url"] = "/results"
    return JSONResponse(payload, status_code=response.status_code)


@router.post("/analyze", name="analyze_session_public")
def analyze_session_public(request: Request, database_session: Session = Depends(get_db_session)) -> JSONResponse:
    session_id = _session_id_from_cookie(request)
    response = analyze_session(session_id, database_session)
    payload = json.loads(response.body)
    if payload.get("redirect_url"):
        payload["redirect_url"] = _publicize_redirect(_redirect(payload["redirect_url"]), session_id).headers["location"]
    return JSONResponse(payload, status_code=response.status_code)


@router.get("/results", response_class=HTMLResponse, name="show_results_public")
def show_results_public(request: Request, database_session: Session = Depends(get_db_session)) -> Response:
    session_id = _session_id_from_cookie(request)
    return _publicize_redirect(show_results(request, session_id, database_session), session_id)


@router.get("/report", response_class=HTMLResponse, name="show_report_public")
def show_report_public(request: Request, database_session: Session = Depends(get_db_session)) -> Response:
    session_id = _session_id_from_cookie(request)
    return _publicize_redirect(show_report(request, session_id, database_session), session_id)


@router.post("/another-process", name="analyze_another_process_public")
def analyze_another_process_public(request: Request, database_session: Session = Depends(get_db_session)) -> Response:
    session_id = _session_id_from_cookie(request)
    return _publicize_redirect(analyze_another_process(session_id, database_session), session_id)


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
        return "regelbasierte Automatisierung"
    if any(marker in opportunity_text for marker in digital_markers):
        return "einfache Digitalisierung"
    return "Ordnung und Standardisierung"


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
        DEMO_SESSION_SLUGS[session_id] = demo_slug
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
    response = _redirect("/processing")
    _set_session_cookie(response, request, session_id)
    return response
