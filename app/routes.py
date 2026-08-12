from __future__ import annotations

import json
import base64
import hashlib
import hmac
import logging
import os
import re
import secrets
from datetime import date
from difflib import SequenceMatcher
from html import unescape
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
    question_reason_for_pattern,
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
from app.llm_classification import classify_narrative, rank_candidates
from app.recommendation_service import (
    RecommendationRankingError,
    load_recommendation_catalog,
    select_recommendation,
)
from app.solution_knowledge import (
    build_solution_query,
    extract_confirmed_channels,
    find_inference_patterns,
    load_solution_workflows,
    match_business_type,
    output_structure_context,
    output_structure_for,
    select_solution_workflows,
    solution_workflow_context,
)
from app.schemas import (
    CUSTOMER_TEXT_FIELDS,
    FinalAnalysisResult,
    contains_forbidden_customer_term,
    contains_internal_reference,
    contains_prohibited_customer_language,
    customer_plain_text,
    sanitize_customer_payload,
)


router = APIRouter()
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
templates.env.filters["customer_text"] = customer_plain_text
ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
EVALUATION_FILE = ROOT_DIRECTORY / "knowledge" / "evaluation" / "cases_ten_kmu.json"
INTRO_KEYS = tuple(question["key"] for question in INTRO_QUESTIONS)
PROCESS_KEYS = tuple(question["key"] for question in PROCESS_QUESTIONS)
DEMO_EVALUATION_IDS = {
    "massage-salon": "EVAL-M-01",
    "etsy-3d-print": "EVAL-C-02",
    "carpet-cleaning": "EVAL-C-10",
}
SESSION_COOKIE = "ai_start_map_session"
SESSION_SIGNING_KEY = (
    os.getenv("SESSION_SIGNING_KEY", "").encode("utf-8") or secrets.token_bytes(32)
)

PREVIEW_NOTICE = (
    "Beispielangaben zur Veranschaulichung \u2013 hier stehen sp\u00e4ter deine "
    "tats\u00e4chlichen Angaben."
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
                    "Wir konnten den Ablauf gerade nicht sicher erkennen. "
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
            "Das hat gerade nicht geklappt. Versuch es bitte noch einmal.",
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
            question_reason_for_pattern(current_question.question_text)
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
    *,
    business_type: str | None = None,
    candidate_ranking: list[dict[str, object]] | None = None,
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
                "to_be_steps": result.to_be_steps or result.loesung.ablauf_kuenftig,
            },
            core_bottleneck=result.core_bottleneck,
            uncertainties={
                "items": result.uncertainties,
                "business_type": business_type,
                "candidate_ranking": candidate_ranking or [],
                "bottleneck": {
                    "symptom": result.bottleneck_symptom,
                    "cause": result.bottleneck_cause or result.core_bottleneck,
                    "effect": result.bottleneck_effect,
                },
                "core_output": {
                    "contract_version": "ergebnis-spec-v5",
                    "engpass_titel": result.engpass_titel,
                    "engpass_text": result.engpass_text,
                    "moeglichkeiten": [
                        item.model_dump() for item in result.moeglichkeiten
                    ],
                    "loesung": result.loesung.model_dump(),
                    "beispiel": (
                        result.beispiel.model_dump()
                        if result.beispiel is not None
                        else None
                    ),
                    "voraussetzungen": result.voraussetzungen.model_dump(),
                    "umsetzung": result.umsetzung.model_dump(),
                    "bleibt_bei_dir": result.bleibt_bei_dir,
                    "grenzen": result.grenzen,
                    "spaeter": result.spaeter,
                    "not_automated": result.not_automated,
                    "error_boundaries": result.error_boundaries,
                    "autonomy_level": result.autonomy_level,
                },
            },
        )
    )
    # Der neue Kundenvertrag kennt genau eine Empfehlung. Sekundaere
    # Moeglichkeiten entfallen; die Tabelle behaelt dafuer eine Zeile.
    database_session.add(
        AutomationOpportunity(
            session_id=session_id,
            rank=1,
            title=result.loesung.titel,
            problem=result.engpass_text,
            recommendation=result.loesung.was_dabei_rauskommt,
            benefit=result.loesung.was_die_ki_macht,
            human_approval=result.bleibt_bei_dir,
            first_step=result.umsetzung.erster_schritt,
            blueprint_json={
                "contract_version": "ergebnis-spec-v5",
                "ergebnis_art": result.loesung.ergebnis_art,
                "spaeter": result.spaeter,
            },
        )
    )
    database_session.commit()


def _forbidden_customer_fields(
    value: object,
    field_path: str = "",
) -> list[dict[str, str]]:
    """Locate whole generated fields that must be regenerated or omitted."""

    if isinstance(value, str):
        if value.strip() and contains_forbidden_customer_term(value):
            return [{"field": field_path, "rejected_text": value}]
        return []
    if isinstance(value, dict):
        hits: list[dict[str, str]] = []
        for key, item in value.items():
            child_path = f"{field_path}.{key}" if field_path else str(key)
            hits.extend(_forbidden_customer_fields(item, child_path))
        return hits
    if isinstance(value, list):
        hits = []
        for index, item in enumerate(value):
            hits.extend(_forbidden_customer_fields(item, f"{field_path}[{index}]"))
        return hits
    return []


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
        all_solution_workflows = load_solution_workflows()
        business_type = match_business_type(
            getattr(classification, "business_type_guess", ""),
            workflows=all_solution_workflows,
        )
        logger.info(
            "analysis.classification method=%s problem_families=%s business_type=%s",
            classification.method,
            problem_family_ids,
            business_type or "none",
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
        recommendation_catalog = load_recommendation_catalog()
        recommendation = select_recommendation(
            problem_family_ids,
            gates,
            catalog=recommendation_catalog,
            confirmed_text=query_text,
            candidate_ranker=rank_candidates,
        )
        confirmed_channels = extract_confirmed_channels(query_text)
        primary_solution_id = (
            recommendation.primary.solution_id if recommendation.primary else None
        )
        selected_workflows = []
        solution_query = ""
        solution_retrieval_method = "not_applicable_a0"
        if primary_solution_id:
            selected_workflows = select_solution_workflows(
                primary_solution_id,
                business_type=business_type,
                channels=confirmed_channels,
                limit=2,
                workflows=all_solution_workflows,
            )
            solution_query = build_solution_query(
                problem_family_ids=problem_family_ids,
                solution_pattern_id=primary_solution_id,
                bottleneck=process.process_name,
                channels=confirmed_channels,
                business_type=business_type,
            )
            solution_retrieval_method = "deterministic"
            try:
                semantic_chunks = retrieve_solution_workflows(
                    solution_query,
                    solution_pattern_id=primary_solution_id,
                    business_type=business_type,
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
        recommendation_context["software_not_ai"] = list(
            recommendation_catalog.software_not_ai
        )
        recommendation_context["failure_guardrails"] = [
            {
                "trigger": item.trigger,
                "guardrail": item.guardrail,
                "customer_language": item.customer_language,
            }
            for item in recommendation_catalog.failure_patterns
        ]
        recommendation_context["output_structure"] = output_structure_context(
            output_structure_for(primary_solution_id) if primary_solution_id else None
        )
        recommendation_context["solution_workflows"] = solution_workflow_context(
            selected_workflows
        )
        recommendation_context["solution_retrieval"] = {
            "query": solution_query,
            "eligible_count": sum(
                item.solution_pattern_id == primary_solution_id
                and item.batch_scope == "in_scope"
                for item in all_solution_workflows
            ),
            "returned_count": len(selected_workflows),
            "method": solution_retrieval_method,
        }
        recommendation_context["business_type"] = business_type
        logger.info(
            "recommendation.selected problem_families=%s primary_solution=%s "
            "secondary_solutions=%s excluded_solutions=%s gates=%s",
            problem_family_ids,
            primary_solution_id or "A0",
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
        # Die eine erlaubte Neuerzeugung bei einem Fachwort-Treffer macht
        # generate_final_analysis selbst. Hier wird nur noch geprueft - es wird
        # nichts ersetzt und nichts geloescht.
        result = generate_final_analysis(
            answers=_answer_payload(all_questions),
            selected_process=_process_payload(process),
            knowledge_chunks=knowledge,
            agent_state=agent_state,
            recommendation_context=recommendation_context,
        )
        remaining_hits = _forbidden_customer_fields(
            result.model_dump(
                include=CUSTOMER_TEXT_FIELDS
            )
        )
        for hit in remaining_hits:
            logger.warning(
                "customer_output.field_rejected field=customer_output.%s text=%r",
                hit["field"],
                hit["rejected_text"],
            )
        if remaining_hits:
            raise AIServiceError(
                "Die verständliche Ergebnisfassung konnte nicht sicher erstellt werden."
            )
        logger.info(
            "recommendation.output_validated validation_result=passed "
            "primary_solution=%s ergebnis_art=%s",
            primary_solution_id or "A0",
            result.loesung.ergebnis_art,
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
        _persist_final_analysis(
            database_session,
            session_id,
            result,
            business_type=business_type,
            candidate_ranking=[
                item.model_dump() for item in recommendation.candidate_ranking
            ],
        )
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
    except (AIServiceError, RecommendationRankingError) as error:
        database_session.rollback()
        return JSONResponse(
            {
                "state": "error",
                "message": "Das hat gerade nicht geklappt. Versuch es bitte noch einmal.",
                "redirect_url": None,
            },
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
    if (
        not result_view
        or contains_internal_reference(result_view)
        or contains_prohibited_customer_language(result_view)
        or contains_forbidden_customer_term(result_view)
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
            "result": result_view,
        },
    )


def _customer_recommendation_title(value: object) -> str:
    title = str(value or "").strip()
    match = re.search(r"\bSP-\d{2}\b", title, re.IGNORECASE)
    catalog = load_recommendation_catalog()
    if match is not None:
        solution_id = match.group(0).upper()
        pattern = next(
            (item for item in catalog.solution_patterns if item.solution_id == solution_id),
            None,
        )
        return pattern.customer_title if pattern is not None else ""
    pattern = next(
        (
            item
            for item in catalog.solution_patterns
            if item.name.casefold() == title.casefold()
        ),
        None,
    )
    if pattern is not None:
        return pattern.customer_title
    return customer_plain_text(title, "customer_output.primary_recommendation")


def _solution_id_for_title(value: object) -> str:
    title = str(value or "").strip()
    match = re.search(r"\bSP-\d{2}\b", title, re.IGNORECASE)
    if match is not None:
        return match.group(0).upper()
    customer_match = next(
        (
            item.solution_id
            for item in load_recommendation_catalog().solution_patterns
            if item.customer_title.casefold() == title.casefold()
        ),
        "",
    )
    if customer_match:
        return customer_match
    catalog = load_recommendation_catalog()
    pattern = next(
        (
            item
            for item in catalog.solution_patterns
            if item.name.casefold() == title.casefold()
        ),
        None,
    )
    return pattern.solution_id if pattern is not None else ""


def _customer_future_steps(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [
        re.sub(
            r"^(?:Der )?Nutzer wählt oder übermittelt\b",
            "Du wählst oder übermittelst",
            re.sub(r"\bDu wählt\b", "Du wählst", str(item)),
            flags=re.IGNORECASE,
        )
        for item in value
    ]


def _question_from_open_detail(value: object) -> str:
    text = customer_plain_text(value, "customer_output.open_question").strip()
    if not text:
        return ""
    text = re.sub(
        r"\s*\((?:noch\s+)?offen\)\s*\??$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    lowered = text.casefold()
    generic_markers = (
        "ein nicht belegtes detail",
        "ein internes oder nicht belegtes detail",
        "bleibt noch offen",
        "rekonstruktion",
    )
    statistical_markers = (
        "wie viele auftr\u00e4ge",
        "wie viele bestellungen",
        "pro tag",
        "pro woche",
        "fallzahl",
        "volumen",
        "zahl gleichzeitig",
        "anzahl der",
    )
    if any(marker in lowered for marker in (*generic_markers, *statistical_markers)):
        return ""
    if "rechnung" in lowered and any(
        marker in lowered for marker in ("sofort", "wöchentlich", "monatlich")
    ):
        return ""
    if text.endswith("?"):
        return text
    if re.match(r"^(?:wie|wer|was|wo|wann|welche|welcher|woran)\b", text, re.IGNORECASE):
        return text.rstrip(".!") + "?"
    return ""


def _normalized_similarity(left: str, right: str) -> float:
    normalize = lambda value: re.sub(
        r"[^a-z0-9äöüß]+", " ", value.casefold()
    ).strip()
    return SequenceMatcher(None, normalize(left), normalize(right)).ratio()


def _same_required_topic(question: str, prerequisite: str) -> bool:
    stop_words = {
        "diese", "dieser", "diesem", "deine", "deinen", "einem", "einer",
        "heute", "klar", "welche", "welchem", "woran", "gehört", "wird",
        "werden", "kann", "können", "noch", "nicht", "muss", "sein",
    }
    tokens = lambda value: {
        item for item in re.findall(r"[a-zäöüß]+", value.casefold())
        if len(item) >= 5 and item not in stop_words
    }
    shared = tokens(question) & tokens(prerequisite)
    shared_assignment_topic = bool(
        shared & {"auftrag", "einsatz", "bestellung", "termin", "gegenstand"}
    ) and all(
        any(marker in value.casefold() for marker in ("gehör", "zuord", "erkenn", "klar"))
        for value in (question, prerequisite)
    )
    return (
        _normalized_similarity(question, prerequisite) >= 0.7
        or len(shared) >= 2
        or shared_assignment_topic
    )


def _deduplicate_open_questions(*groups: object) -> list[str]:
    questions: list[str] = []
    normalized: list[str] = []
    for group in groups:
        if not isinstance(group, list):
            continue
        for item in group:
            question = _question_from_open_detail(item)
            if not question:
                continue
            key = re.sub(r"[^a-z0-9\u00e4\u00f6\u00fc\u00df]+", " ", question.casefold()).strip()
            if any(
                SequenceMatcher(None, key, previous).ratio() >= 0.68
                for previous in normalized
            ):
                continue
            questions.append(question)
            normalized.append(key)
            if len(questions) == 3:
                return questions
    return questions


def _customer_secondary_opportunities(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    visible: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            continue
        title = customer_plain_text(
            item.get("title"),
            f"customer_output.secondary_opportunities[{index}].title",
        )
        description = customer_plain_text(
            item.get("description"),
            f"customer_output.secondary_opportunities[{index}].description",
        )
        if not title or not description or title.casefold() == "noch offen":
            continue
        visible.append({"title": title, "description": description})
        if len(visible) == 2:
            break
    return visible


def _result_view(
    analysis: Analysis,
    opportunities: list[AutomationOpportunity],
) -> dict[str, object]:
    """Reicht den geschriebenen Kundentext durch.

    Es wird nichts mehr in eine feste Ausgabestruktur umgeschrieben und nichts
    aus Katalog-Beispielwerten aufgefuellt. Was das Modell geschrieben hat, geht
    so heraus - geprueft, aber nicht umsortiert.
    """

    step_data = analysis.as_is_steps
    if isinstance(step_data, dict):
        as_is_steps = [str(item) for item in step_data.get("steps", [])]
        problem_indexes = [
            int(index)
            for index in step_data.get("problem_step_indexes", [])
            if isinstance(index, int)
        ]
    else:
        as_is_steps = [str(item) for item in step_data]
        problem_indexes = []

    uncertainty_data = analysis.uncertainties
    if isinstance(uncertainty_data, dict):
        raw_core_output = uncertainty_data.get("core_output", {})
        core_output = raw_core_output if isinstance(raw_core_output, dict) else {}
    else:
        core_output = {}

    # Analysen aus einem aelteren Feldvertrag koennen den neuen Kundentext nicht
    # liefern. Sie werden nicht rekonstruiert und nicht erfunden.
    if core_output.get("contract_version") != "ergebnis-spec-v5":
        logger.info("customer_output.legacy_analysis_not_rendered")
        return {}

    loesung = core_output.get("loesung") or {}
    beispiel = core_output.get("beispiel")
    voraussetzungen = core_output.get("voraussetzungen") or {}
    umsetzung = core_output.get("umsetzung") or {}

    # Reihenfolge nach docs/auftrag/ERGEBNIS_SPEC.md. "spaeter" steckt bereits
    # in moeglichkeiten mit Rang "spaeter" und wird nicht zweimal gezeigt.
    customer_payload = {
        "is_non_ai": core_output.get("autonomy_level") == "A0",
        "engpass_titel": str(core_output.get("engpass_titel") or ""),
        "engpass_text": str(core_output.get("engpass_text") or ""),
        "as_is_steps": as_is_steps[:5],
        "problem_step_indexes": problem_indexes,
        "moeglichkeiten": [
            {
                "rang": str(item.get("rang") or ""),
                "titel": str(item.get("titel") or ""),
                "begruendung": str(item.get("begruendung") or ""),
            }
            for item in core_output.get("moeglichkeiten", [])
            if isinstance(item, dict) and item.get("titel")
        ],
        "loesung": {
            "titel": str(loesung.get("titel") or ""),
            "ablauf_heute": [str(item) for item in loesung.get("ablauf_heute", [])],
            "ablauf_kuenftig": [str(item) for item in loesung.get("ablauf_kuenftig", [])],
            "was_reinkommt": str(loesung.get("was_reinkommt") or ""),
            "was_die_ki_macht": str(loesung.get("was_die_ki_macht") or ""),
            "was_du_machst": str(loesung.get("was_du_machst") or ""),
            "was_dabei_rauskommt": str(loesung.get("was_dabei_rauskommt") or ""),
            "ergebnis_art": str(loesung.get("ergebnis_art") or ""),
        },
        "beispiel": (
            {
                "titel": str(beispiel.get("titel") or ""),
                "kanal": str(beispiel.get("kanal") or ""),
                # Steuert, in welcher Form das Beispiel gerendert wird.
                "darstellung": str(beispiel.get("darstellung") or "karte"),
                "nachricht": str(beispiel.get("nachricht") or ""),
                "daraus_wird": [
                    {"label": str(feld.get("label") or ""), "wert": str(feld.get("wert") or "")}
                    for feld in beispiel.get("daraus_wird", [])
                    if isinstance(feld, dict) and feld.get("label") and feld.get("wert")
                ],
                "fehlt": [str(item) for item in beispiel.get("fehlt", [])],
                "rueckfrage": str(beispiel.get("rueckfrage") or ""),
                "hinweis": PREVIEW_NOTICE,
            }
            if isinstance(beispiel, dict)
            else None
        ),
        "voraussetzungen": {
            "vorhandene_werkzeuge": [
                str(item) for item in voraussetzungen.get("vorhandene_werkzeuge", [])
            ],
            "neu_hinzukommend": [
                str(item) for item in voraussetzungen.get("neu_hinzukommend", [])
            ],
            "geraete_und_zugang": str(voraussetzungen.get("geraete_und_zugang") or ""),
            "musst_du_besorgen": [
                str(item) for item in voraussetzungen.get("musst_du_besorgen", [])
            ],
        },
        "umsetzung": {
            "hinweis": str(umsetzung.get("hinweis") or ""),
            "einrichtungsschritte": [
                str(item) for item in umsetzung.get("einrichtungsschritte", [])
            ],
            "erster_schritt": str(umsetzung.get("erster_schritt") or ""),
        },
        "bleibt_bei_dir": str(core_output.get("bleibt_bei_dir") or ""),
        "grenzen": str(core_output.get("grenzen") or ""),
        "current_process_summary": analysis.process_summary,
        "contact_recommendation": str(loesung.get("titel") or ""),
    }
    sanitized = sanitize_customer_payload(customer_payload)
    if contains_forbidden_customer_term(sanitized):
        logger.error("customer_output.sanitization_failed")
        return {}
    return sanitized


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
    if (
        not result
        or contains_internal_reference(result)
        or contains_prohibited_customer_language(result)
        or contains_forbidden_customer_term(result)
    ):
        return _render_error(request, "Der Bericht konnte nicht sicher angezeigt werden.", status_code=status.HTTP_409_CONFLICT)
    response = templates.TemplateResponse(
        request=request,
        name="report.html",
        context={
            "process": process,
            "analysis": analysis,
            "result": result,
            "analysis_date": date.today().strftime("%d.%m.%Y"),
        },
    )
    rendered_pdf_text = unescape(
        re.sub(r"<[^>]+>", " ", response.body.decode("utf-8"))
    )
    if contains_forbidden_customer_term(rendered_pdf_text):
        logger.error("customer_output.pdf_forbidden_term")
        return _render_error(
            request,
            "Der Bericht konnte nicht sicher angezeigt werden.",
            status_code=status.HTTP_409_CONFLICT,
        )
    return response


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
