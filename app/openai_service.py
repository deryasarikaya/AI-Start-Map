from __future__ import annotations

import contextvars
import json
import logging
import os
import re
from collections.abc import Sequence
from pathlib import Path
from time import perf_counter
from typing import TypeVar

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, ValidationError

from app.schemas import (
    AS_IS_META_PATTERN,
    CURRENT_PROCESS_PATTERN,
    FOLLOW_UP_SOLUTION_PATTERN,
    FinalAnalysisResult,
    FollowUpQuestion,
    FollowUpResult,
    ProcessBoundaryResult,
    ProcessSuggestionResult,
    ProcessUnderstandingResult,
    contains_forbidden_customer_term,
)


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

ENDANALYSE_SYSTEM_PROMPT_FILE = (
    Path(__file__).resolve().parents[1] / "docs" / "prompts" / "endanalyse_system.md"
)


def _endanalyse_system_prompt() -> str:
    """Laedt den Briefing-Prompt fuer die Endanalyse aus der Prompt-Datei."""

    try:
        return ENDANALYSE_SYSTEM_PROMPT_FILE.read_text(encoding="utf-8").strip()
    except OSError as error:
        raise AIServiceError(
            "Der Systemprompt für die Endanalyse konnte nicht geladen werden."
        ) from error


class AIServiceError(RuntimeError):
    pass


StructuredResult = TypeVar("StructuredResult", bound=BaseModel)
logger = logging.getLogger(__name__)
OPENAI_REQUEST_TIMEOUT_SECONDS = 45.0
FINAL_ANALYSIS_TIMEOUT_SECONDS = 120.0
OPENAI_RETRIEVAL_TIMEOUT_SECONDS = 6.0
_openai_call_count: contextvars.ContextVar[int] = contextvars.ContextVar(
    "openai_call_count",
    default=0,
)
_embedding_call_count: contextvars.ContextVar[int] = contextvars.ContextVar(
    "embedding_call_count",
    default=0,
)


def reset_openai_call_count() -> None:
    _openai_call_count.set(0)
    _embedding_call_count.set(0)


def get_openai_call_count() -> int:
    return _openai_call_count.get()


def get_embedding_call_count() -> int:
    return _embedding_call_count.get()


def _record_openai_call() -> int:
    call_count = _openai_call_count.get() + 1
    _openai_call_count.set(call_count)
    return call_count


def _record_embedding_call() -> int:
    call_count = _embedding_call_count.get() + 1
    _embedding_call_count.set(call_count)
    return call_count


def _validation_error_fields(error: ValidationError) -> list[str]:
    return [
        ".".join(str(part) for part in item.get("loc", ())) or "<root>"
        for item in error.errors(include_input=False)
    ]


CUSTOMER_LANGUAGE_REPLACEMENTS = {
    "intake-kit": "Erfassung",
    "intake": "Aufnahme",
    "audit-track": "Prüfübersicht",
    "wip": "aktueller Arbeitsstand",
    "mapping": "Zuordnung",
    "lookup": "Suche",
    "semi-automatisiert": "teilweise vorbereitet",
    "formulardoppie": "doppelte Erfassung",
    "nachschlageort": "gemeinsame Übersicht",
    "übergabevermerkgabel": "Übergabevermerk",
    "handschriftenkapazität": "Kapazität für handschriftliche Erfassung",
}


def _normalize_customer_language(
    value: object,
    *,
    allowed_user_text: str = "",
) -> object:
    """Replace known internal jargon without changing factual content."""

    if isinstance(value, str):
        normalized = value
        for term, replacement in CUSTOMER_LANGUAGE_REPLACEMENTS.items():
            if term in allowed_user_text:
                continue
            normalized = re.sub(
                rf"\b{re.escape(term)}\b",
                replacement,
                normalized,
                flags=re.IGNORECASE,
            )
        normalized = re.sub(
            r"\b(?:der Nutzer|die Nutzerin|der Unternehmer|der Mitarbeiter|die Person)\b",
            "Du",
            normalized,
            flags=re.IGNORECASE,
        )
        normalized = re.sub(
            r"\bman sollte\b",
            "Du solltest",
            normalized,
            flags=re.IGNORECASE,
        )
        return normalized
    if isinstance(value, list):
        return [
            _normalize_customer_language(item, allowed_user_text=allowed_user_text)
            for item in value
        ]
    if isinstance(value, dict):
        return {
            key: _normalize_customer_language(
                item,
                allowed_user_text=allowed_user_text,
            )
            for key, item in value.items()
        }
    return value


def _normalize_final_analysis_payload(
    value: object,
    *,
    allowed_user_text: str = "",
) -> object:
    normalized = _normalize_customer_language(
        value,
        allowed_user_text=allowed_user_text,
    )
    if not isinstance(normalized, dict):
        return normalized
    steps = normalized.get("as_is_steps")
    if not isinstance(steps, list):
        return normalized
    kept_steps: list[object] = []
    index_map: dict[int, int] = {}
    for old_index, step in enumerate(steps):
        if isinstance(step, str) and AS_IS_META_PATTERN.search(step) is not None:
            continue
        index_map[old_index] = len(kept_steps)
        kept_steps.append(step)
    normalized["as_is_steps"] = kept_steps
    problem_indexes = normalized.get("as_is_problem_step_indexes")
    if isinstance(problem_indexes, list):
        normalized["as_is_problem_step_indexes"] = [
            index_map[index]
            for index in problem_indexes
            if isinstance(index, int) and index in index_map
        ]
    summary = normalized.get("process_summary")
    if isinstance(summary, str) and re.search(
        r"^(?:aus den vorliegenden angaben|auf grundlage der daten|quelle:)",
        summary,
        re.IGNORECASE,
    ):
        normalized["process_summary"] = (
            " ".join(str(item) for item in kept_steps)
            or "Der heutige Ablauf bleibt an dieser Stelle noch offen."
        )
    return normalized


def _normalize_current_process_question(question: str) -> str:
    normalized = " ".join(question.strip().split()).rstrip(".?!")
    if not normalized:
        return ""
    if CURRENT_PROCESS_PATTERN.search(normalized) is not None:
        return f"{normalized}?"
    conditional = re.match(r"^(wenn|falls)\s+([^,]+),\s*(.+)$", normalized, re.IGNORECASE)
    if conditional is not None:
        condition_word, condition, question_body = conditional.groups()
        question_body = question_body[0].upper() + question_body[1:]
        return (
            f"{question_body} heute, {condition_word.casefold()} "
            f"{condition}?"
        )
    return f"{normalized} – bezogen auf den Ablauf heute?"


def _normalize_follow_up_payload(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or not isinstance(value.get("questions"), list):
        return {"questions": []}
    normalized_questions: list[dict[str, object]] = []
    seen: set[str] = set()
    for item in value["questions"][:4]:
        if not isinstance(item, dict):
            continue
        question = _normalize_current_process_question(str(item.get("question", "")))
        if not question or FOLLOW_UP_SOLUTION_PATTERN.search(question) is not None:
            continue
        candidate = {**item, "question": question}
        try:
            validated = FollowUpQuestion.model_validate(candidate)
        except ValidationError:
            continue
        key = validated.question.casefold().rstrip(" ?!.")
        if key in seen:
            continue
        seen.add(key)
        normalized_questions.append(validated.model_dump())
    return {"questions": normalized_questions}


def _api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or api_key == "your_openai_api_key":
        raise AIServiceError(
            "Der KI-Zugang ist noch nicht eingerichtet. Trage OPENAI_API_KEY "
            "lokal in der .env-Datei ein."
        )
    return api_key


def _structured_output_model() -> str:
    model = os.getenv("OPENAI_MODEL", "").strip()
    if not model or model == "your_structured_output_model":
        raise AIServiceError(
            "Das KI-Modell ist noch nicht eingerichtet. Trage OPENAI_MODEL "
            "lokal in der .env-Datei ein."
        )
    return model


def get_embedding_model() -> str:
    return (
        os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small").strip()
        or "text-embedding-3-small"
    )


def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    if not texts:
        return []
    call_number = _record_embedding_call()
    call_started = perf_counter()
    logger.info(
        "openai.embeddings.start section=retrieval call=%d timeout_seconds=%.1f",
        call_number,
        OPENAI_RETRIEVAL_TIMEOUT_SECONDS,
    )
    try:
        raw_response = OpenAI(
            api_key=_api_key(),
            timeout=OPENAI_RETRIEVAL_TIMEOUT_SECONDS,
            max_retries=0,
        ).embeddings.with_raw_response.create(
            model=get_embedding_model(),
            input=list(texts),
            timeout=OPENAI_RETRIEVAL_TIMEOUT_SECONDS,
        )
        logger.info(
            "openai.embeddings.response section=retrieval call=%d status=%d "
            "duration_seconds=%.3f",
            call_number,
            raw_response.status_code,
            perf_counter() - call_started,
        )
        response = raw_response.parse()
    except OpenAIError as error:
        logger.exception(
            "openai.embeddings.failed section=retrieval call=%d exception_type=%s "
            "exception_message=%s response_status=%s duration_seconds=%.3f",
            call_number,
            type(error).__name__,
            str(error),
            getattr(error, "status_code", None),
            perf_counter() - call_started,
        )
        raise AIServiceError(
            "Die Wissenssuche konnte gerade nicht vorbereitet werden."
        ) from error
    return [item.embedding for item in response.data]


def _parse_structured_output(
    *,
    system_prompt: str,
    payload: dict[str, object],
    result_type: type[StructuredResult],
) -> StructuredResult:
    last_error: Exception | None = None
    model = _structured_output_model()
    is_final_analysis = result_type is FinalAnalysisResult
    is_follow_up = result_type is FollowUpResult
    maximum_attempts = 1 if is_follow_up else 2
    request_timeout = (
        FINAL_ANALYSIS_TIMEOUT_SECONDS
        if is_final_analysis
        else OPENAI_REQUEST_TIMEOUT_SECONDS
    )
    request_deadline = perf_counter() + request_timeout
    client = OpenAI(
        api_key=_api_key(),
        timeout=request_timeout,
        max_retries=0,
    )
    model_options: dict[str, object] = {}
    if model.casefold().startswith("gpt-5"):
        model_options = {
            "reasoning_effort": "medium" if is_final_analysis else "minimal",
            "verbosity": "low",
        }
    for attempt in range(maximum_attempts):
        retry_instruction = (
            "\n\nDie vorherige Ausgabe war nicht vollständig regelkonform. "
            "Prüfe jetzt jedes Feld erneut gegen das Ausgabeschema und alle "
            "inhaltlichen Verbote."
            if attempt
            else ""
        )
        remaining_seconds = request_deadline - perf_counter()
        if remaining_seconds <= 0:
            last_error = TimeoutError("Zeitlimit vor dem Modellaufruf erreicht")
            break
        call_number = _record_openai_call()
        call_started = perf_counter()
        logger.info(
            "openai.structured_output.start section=%s call=%d attempt=%d timeout_seconds=%.1f",
            result_type.__name__,
            call_number,
            attempt + 1,
            remaining_seconds,
        )
        try:
            raw_response = client.chat.completions.with_raw_response.parse(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt + retry_instruction,
                    },
                    {
                        "role": "user",
                        "content": json.dumps(payload, ensure_ascii=False),
                    },
                ],
                response_format=result_type,
                timeout=remaining_seconds,
                **model_options,
            )
            logger.info(
                "openai.structured_output.response section=%s call=%d status=%d duration_seconds=%.3f",
                result_type.__name__,
                call_number,
                raw_response.status_code,
                perf_counter() - call_started,
            )
            response_body = json.loads(raw_response.text)
            choice = response_body["choices"][0]
            if choice.get("finish_reason") != "stop":
                raise ValueError(
                    f"Unvollständige Modellantwort: {choice.get('finish_reason')}"
                )
            message = choice["message"]
            if message.get("refusal"):
                raise ValueError("Das Modell hat die strukturierte Antwort abgelehnt")
            response_payload = json.loads(message.get("content") or "")
            if is_final_analysis:
                user_fact_text = json.dumps(
                    payload.get("A_USER_FACTS", {}),
                    ensure_ascii=False,
                ).casefold()
                response_payload = _normalize_final_analysis_payload(
                    response_payload,
                    allowed_user_text=user_fact_text,
                )
            elif is_follow_up:
                response_payload = _normalize_follow_up_payload(response_payload)
            validation_started = perf_counter()
            parsed_result = result_type.model_validate(response_payload)
            logger.info(
                "openai.structured_output.validated section=%s call=%d "
                "validation_seconds=%.3f duration_seconds=%.3f",
                result_type.__name__,
                call_number,
                perf_counter() - validation_started,
                perf_counter() - call_started,
            )
            return parsed_result
        except (
            OpenAIError,
            ValidationError,
            ValueError,
            IndexError,
            KeyError,
            TypeError,
            json.JSONDecodeError,
        ) as error:
            last_error = error
            validation_fields = (
                _validation_error_fields(error)
                if isinstance(error, ValidationError)
                else []
            )
            logger.exception(
                "openai.structured_output.failed section=%s call=%d exception_type=%s "
                "exception_message=%s response_status=%s validation_fields=%s "
                "duration_seconds=%.3f",
                result_type.__name__,
                call_number,
                type(error).__name__,
                str(error),
                getattr(error, "status_code", None),
                validation_fields,
                perf_counter() - call_started,
            )
    if is_follow_up:
        logger.warning(
            "openai.structured_output.fallback section=FollowUpResult questions=0 "
            "exception_type=%s",
            type(last_error).__name__ if last_error is not None else "UnknownError",
        )
        return result_type.model_validate({"questions": []})
    raise AIServiceError(
        "Die KI-Antwort konnte nicht zuverlässig verarbeitet werden."
    ) from last_error


COMMON_GROUNDING_RULES = """
Du unterstützt eine Prozessdiagnose für ein kleines Unternehmen. Verwende nur die
als Nutzerangaben markierten Inhalte als Fakten über diesen Betrieb. Die
internen Wissensauszüge dienen ausschließlich dazu, fachliche Muster zu erkennen.
Erwähne, zitiere oder beschreibe diese Wissensauszüge niemals in der Antwort und
übernimm daraus niemals Mengen, Programme, Schnittstellen, Rollen oder Abläufe als
Nutzerfakt. Gib insbesondere keine Fall-, Dokument-, Datei-, Chunk- oder
Musterbezeichnungen und keine Metadaten aus. Formulierungen wie „Testfall“,
„RAG-Fall“, „Referenzfall“ oder „Evaluationsfall“ sind in jeder Ausgabe unzulässig.
Jeder ausgegebene Text beschreibt ausschließlich den konkreten Nutzerprozess.
Erfinde keine fehlenden Angaben und lasse Unsicherheit sichtbar. Setze keine
vorhandene Softwarefunktion oder API voraus. Verwende klare deutsche Begriffe.
Unzulässig sind insbesondere: Intake, Intake-Kit, Audit-Track, WIP, Mapping,
Lookup, semi-automatisiert, Formulardoppie, Nachschlageort,
Übergabevermerkgabel und Handschriftenkapazität. Verwende stattdessen natürliche,
für kleine Betriebe verständliche Formulierungen.
""".strip()

SPECULATIVE_PROCESS_TERMS = (
    "abholnummer",
    "ausweis",
    "falschübergab",
    "foto",
    "identitätsprüf",
    "ringordner",
    "unterschrift",
    "verwechslung",
)
SOLUTION_ONLY_UNCERTAINTY_TERMS: tuple[str, ...] = ()


def _combined_user_facts(
    answers: dict[str, str],
    selected_process: dict[str, str] | None = None,
) -> str:
    values = list(answers.values())
    if selected_process:
        values.extend(selected_process.values())
    return " ".join(values).casefold()


def _validate_follow_up_grounding(
    result: FollowUpResult,
    answers: dict[str, str],
) -> FollowUpResult:
    user_facts = _combined_user_facts(answers)
    grounded_questions: list[FollowUpQuestion] = []
    for follow_up in result.questions:
        question = follow_up.question.casefold()
        if any(
            term in question and term not in user_facts
            for term in SPECULATIVE_PROCESS_TERMS
        ):
            continue
        grounded_questions.append(follow_up)
    return FollowUpResult(questions=grounded_questions)


def _validate_final_grounding(
    result: FinalAnalysisResult,
    answers: dict[str, str],
    selected_process: dict[str, str],
) -> FinalAnalysisResult:
    user_facts = _combined_user_facts(answers, selected_process)
    unsupported_terms = {
        term for term in SPECULATIVE_PROCESS_TERMS if term not in user_facts
    }
    if unsupported_terms:
        original_steps = list(result.as_is_steps)
        kept_step_indexes = [
            index
            for index, step in enumerate(original_steps)
            if not any(term in step.casefold() for term in unsupported_terms)
        ]
        if kept_step_indexes:
            index_map = {
                old_index: new_index
                for new_index, old_index in enumerate(kept_step_indexes)
            }
            result.as_is_steps = [
                original_steps[index] for index in kept_step_indexes
            ]
            result.as_is_problem_step_indexes = [
                index_map[index]
                for index in result.as_is_problem_step_indexes
                if index in index_map
            ]
        else:
            result.as_is_steps = []
            result.as_is_problem_step_indexes = []
        result.uncertainties = [
            uncertainty
            for uncertainty in result.uncertainties
            if not any(
                term in uncertainty.casefold() for term in unsupported_terms
            )
        ]
        if any(term in result.process_summary.casefold() for term in unsupported_terms):
            result.process_summary = (
                " ".join(result.as_is_steps)
                or "Der heutige Ablauf bleibt an dieser Stelle noch offen."
            )
        warning = "Ein nicht belegtes Detail im heutigen Ablauf bleibt noch offen."
        if warning not in result.uncertainties:
            result.uncertainties = [*result.uncertainties[:3], warning]
    process_name = selected_process["process_name"].strip().casefold()
    summary_start = result.process_summary.strip().casefold()
    summary_without_quote = summary_start.lstrip("„\"'")
    quoted_name = re.compile(rf"^{re.escape(process_name)}[“\"']?(?:\s|[:–-])")
    if (
        summary_start.startswith(process_name)
        or quoted_name.search(summary_without_quote)
    ):
        result.process_summary = (
            " ".join(result.as_is_steps)
            or "Der heutige Ablauf bleibt an dieser Stelle noch offen."
        )
    return result


def _selected_pattern_briefing(
    recommendation_context: dict[str, object] | None,
) -> dict[str, object]:
    """Das bereits gewaehlte Muster als Briefing, nicht als Käfig.

    Nur die Felder, die der Kundentext braucht. Die Auswahl selbst ist zu
    diesem Zeitpunkt getroffen und wird dem Modell nicht mehr zur Wahl gestellt.
    """

    context = recommendation_context or {}
    primary = context.get("primary")
    if not isinstance(primary, dict):
        return {}
    briefing: dict[str, object] = {}
    for field_name in (
        "customer_title",
        "user_action",
        "ai_task",
        "ai_capabilities",
        "ai_capabilities_exclusion",
        "visible_output",
        "human_check",
        "smallest_entry",
        "later_stage",
        "counterexample",
    ):
        value = primary.get(field_name)
        if value:
            briefing[field_name] = value
    return briefing


def _apply_safety_contract(
    result: FinalAnalysisResult,
    recommendation_context: dict[str, object] | None,
) -> FinalAnalysisResult:
    """Setzt die Sicherheitsfelder deterministisch aus Katalog und Gates.

    Der Kundentext selbst wird hier nicht mehr angefasst. Die frühere
    positionsbasierte Umschreibung der Beispielfelder ist ersatzlos entfallen -
    sie war die Ursache dafür, dass ein Datum unter "Wer kümmert sich" landete
    und dass Katalog-Beispielwerte in fremde Branchen wanderten.
    """

    context = recommendation_context or {}
    autonomy_level = context.get("autonomy_level")
    if autonomy_level in {"A0", "A1", "A2", "A3", "A4", "A5"}:
        result.autonomy_level = autonomy_level

    primary = context.get("primary")
    if isinstance(primary, dict):
        human_decisions = primary.get("human_decisions")
        if isinstance(human_decisions, list) and human_decisions:
            result.not_automated = [
                str(item)[:160] for item in human_decisions[:5]
            ]
        stop_conditions = primary.get("stop_conditions")
        if isinstance(stop_conditions, list) and stop_conditions:
            result.error_boundaries = [
                str(item)[:160] for item in stop_conditions[:3]
            ]
    return result


def generate_process_suggestions(
    answers: dict[str, str],
    knowledge_chunks: Sequence[str],
) -> ProcessSuggestionResult:
    return _parse_structured_output(
        system_prompt=(
            COMMON_GROUNDING_RULES
            + "\n\nErzeuge ein bis drei konkrete End-to-End-Prozesse und sortiere "
            "den wahrscheinlich relevantesten zuerst. Jeder hat "
            "einen klaren Beginn und ein klares Ende. Allgemeine Kategorien wie "
            "Marketing, Organisation oder Kundenkommunikation sind unzulässig. "
            "reason ist genau ein kurzer Satz zum erkennbaren Alltagsproblem. "
            "Empfehle in diesem Schritt noch keine Automatisierung."
        ),
        payload={
            "nutzerangaben": answers,
            "internes_vergleichswissen_nicht_ausgeben": list(knowledge_chunks),
        },
        result_type=ProcessSuggestionResult,
    )


def generate_custom_process_boundary(
    *,
    description: str,
    context_answers: dict[str, str],
) -> ProcessBoundaryResult:
    return _parse_structured_output(
        system_prompt=(
            COMMON_GROUNDING_RULES
            + "\n\nLeite aus der eigenen Beschreibung genau einen konkreten, "
            "wiederkehrenden Ablauf ab. Formuliere einen kurzen verständlichen "
            "Namen sowie den konkreten Beginn und das konkrete Ende. Ergänze keine "
            "nicht genannte Tätigkeit und empfehle noch keine Lösung."
        ),
        payload={
            "eigene_beschreibung": description,
            "unternehmensangaben": context_answers,
        },
        result_type=ProcessBoundaryResult,
    )


def generate_process_understanding(
    *,
    answers: dict[str, str],
    selected_process: dict[str, str],
) -> ProcessUnderstandingResult:
    return _parse_structured_output(
        system_prompt=(
            COMMON_GROUNDING_RULES
            + "\n\nRekonstruiere ausschließlich aus den Nutzerangaben den heute "
            "tatsächlich ausgeführten Ablauf. Erzeuge möglichst vier bis fünf, "
            "mindestens aber zwei und niemals mehr als fünf kurze, "
            "konkrete Prozessaktionen in zeitlicher Reihenfolge. as_is_steps darf "
            "nur Handlungen enthalten, niemals Empfehlungen, fehlende Angaben oder "
            "Formulierungen wie unbekannt. Trenne bestätigte Fakten, schwierige "
            "Stellen und offene Punkte. problem_step_indexes enthält nullbasierte "
            "Positionen der Schritte, an denen laut Nutzerangabe gesucht, gewartet, "
            "nachgefragt oder Information verloren wird. Erfinde keine Zwischenschritte. "
            "Empfehle noch keine Lösung."
        ),
        payload={
            "nutzerangaben": answers,
            "ausgewaehlter_ablauf": selected_process,
        },
        result_type=ProcessUnderstandingResult,
    )


def generate_follow_up_questions(
    *,
    answers: dict[str, str],
    selected_process: dict[str, str],
    knowledge_chunks: Sequence[str],
) -> FollowUpResult:
    result = _parse_structured_output(
        system_prompt=(
            COMMON_GROUNDING_RULES
            + "\n\nErzeuge bevorzugt null, normalerweise höchstens zwei und nur bei "
            "einem wirklich komplexen Widerspruch drei entscheidende Rückfragen zum "
            "heutigen tatsächlichen Ablauf. Die technische Obergrenze ist vier. "
            "Jede Rückfrage muss unmittelbar auf einer belegten Nutzerangabe oder "
            "einer darin erkennbaren Lücke beruhen und mindestens eines dieser "
            "Entscheidungen verändern können: Problemfamilie, Ursache, Vorgangsanker, "
            "Kanaleignung, Prozess-/Datenreife, Risiko, Human Check, zulässiges "
            "Solution Pattern oder primäre Empfehlung. "
            "Wiederhole keine beantwortete Frage und behandle je Frage genau ein "
            "Thema. Frage nichts erneut, was in Ursprungserzählung, bestätigtem "
            "Ablauf oder Korrektur bereits eindeutig steht. Fragen, die den Ablauf "
            "nur ausführlicher machen, aber keine Entscheidung verändern, entfallen. "
            "Schlage weder eine Lösung noch eine neue Geschäftsregel vor. "
            "Erfinde keine Gefahr, keine Kontrollmaßnahme und kein Sicherheitsrisiko. "
            "Setze keine Fotos, Identitätsprüfung, Software oder Automatisierung "
            "voraus. Frage offen danach, was heute passiert. Wenn die "
            "Entscheidungsgrundlage sicher ausreicht, gib eine leere Liste zurück."
        ),
        payload={
            "A_USER_FACTS": {
                "ausgewaehlter_ablauf": selected_process,
                "antworten": answers,
            },
            "B_RETRIEVED_PATTERNS_INTERNAL_ONLY": list(knowledge_chunks),
            "C_ALLOWED_USE": (
                "Nur Lücken in den Nutzerangaben erkennen; keine fremden Fakten "
                "oder Risiken übernehmen."
            ),
        },
        result_type=FollowUpResult,
    )
    return _validate_follow_up_grounding(result, answers)


def generate_final_analysis(
    *,
    answers: dict[str, str],
    selected_process: dict[str, str],
    knowledge_chunks: Sequence[str],
    agent_state: dict[str, object] | None = None,
    recommendation_context: dict[str, object] | None = None,
    _quality_retry: bool = False,
) -> FinalAnalysisResult:
    """Erzeugt den Kundentext aus einem Briefing statt aus festen Feldern."""

    context = recommendation_context or {}
    payload: dict[str, object] = {
        "SO_ERZAEHLT_ES_DER_BETRIEB": {
            "ausgewaehlter_ablauf": selected_process,
            "antworten": answers,
            "bestaetigte_fakten": (agent_state or {}).get("confirmed_user_facts", []),
        },
        "GEWAEHLTES_MUSTER": _selected_pattern_briefing(recommendation_context),
        "SOFTWARE_STATT_KI": list(context.get("software_not_ai") or []),
        "NUR_INTERNES_VERGLEICHSWISSEN_NIE_AUSGEBEN": list(knowledge_chunks),
        "FACHLICHE_ABLEITUNGEN": {
            "regel": (
                "Nur logisch zwingende Verbindungen; unbekannte Details bleiben "
                "Unsicherheiten."
            ),
            "ableitungen": (agent_state or {}).get("professional_inferences", []),
            "offene_unsicherheiten": (agent_state or {}).get("uncertainties", []),
            "widersprueche": (agent_state or {}).get("contradictions", []),
        },
    }
    if _quality_retry:
        payload["ERNEUT_SCHREIBEN"] = {
            "grund": (
                "Der vorige Entwurf enthielt ein internes Fachwort. Formuliere die "
                "betroffene Aussage vollständig neu in Alltagssprache. Ersetze "
                "keine einzelnen Wörter im alten Satz."
            ),
        }

    result = _parse_structured_output(
        system_prompt=_endanalyse_system_prompt(),
        payload=payload,
        result_type=FinalAnalysisResult,
    )
    result = _apply_safety_contract(result, recommendation_context)
    result = _validate_final_grounding(result, answers, selected_process)

    # Der Wortfilter prueft nur. Bei einem Treffer wird genau einmal neu
    # erzeugt - es wird nichts ersetzt und nichts geloescht.
    if contains_forbidden_customer_term(result.model_dump()):
        logger.warning(
            "final_analysis.forbidden_term_detected retry=%s", _quality_retry
        )
        if not _quality_retry:
            return generate_final_analysis(
                answers=answers,
                selected_process=selected_process,
                knowledge_chunks=knowledge_chunks,
                agent_state=agent_state,
                recommendation_context=recommendation_context,
                _quality_retry=True,
            )
        logger.error("final_analysis.forbidden_term_persisted")

    # Jede Zahl im Beispiel muss in der erfundenen Nachricht stehen.
    beispiel = result.beispiel
    incoming_numbers = (
        set(re.findall(r"(?<!\w)\d+(?:[.,]\d+)?", beispiel.nachricht))
        if beispiel is not None
        else set()
    )
    field_numbers = {
        number
        for item in (beispiel.daraus_wird if beispiel is not None else [])
        for number in re.findall(r"(?<!\w)\d+(?:[.,]\d+)?", item.wert)
    }
    unsupported_sample_numbers = sorted(field_numbers - incoming_numbers)
    if unsupported_sample_numbers:
        logger.warning(
            "final_analysis.sample_numbers_unsupported retry=%s numbers=%s",
            _quality_retry,
            unsupported_sample_numbers,
        )
        if not _quality_retry:
            retry_context = dict(context)
            retry_context["beispiel_retry"] = {
                "verworfene_zahlen": unsupported_sample_numbers,
                "anforderung": (
                    "Schreibe die Veranschaulichung vollständig neu. Jede Zahl in "
                    "beispiel_daraus_wird muss wörtlich in beispiel_nachricht "
                    "vorkommen."
                ),
            }
            return generate_final_analysis(
                answers=answers,
                selected_process=selected_process,
                knowledge_chunks=knowledge_chunks,
                agent_state=agent_state,
                recommendation_context=retry_context,
                _quality_retry=True,
            )
        raise AIServiceError(
            "Die Veranschaulichung konnte nicht widerspruchsfrei erstellt werden."
        )
    return result
