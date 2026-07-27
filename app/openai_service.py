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
    FinalAnalysisResult,
    FollowUpResult,
    ProcessBoundaryResult,
    ProcessSuggestionResult,
    ProcessUnderstandingResult,
)


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


class AIServiceError(RuntimeError):
    pass


StructuredResult = TypeVar("StructuredResult", bound=BaseModel)
logger = logging.getLogger(__name__)
OPENAI_REQUEST_TIMEOUT_SECONDS = 26.0
OPENAI_RETRIEVAL_TIMEOUT_SECONDS = 6.0
_openai_call_count: contextvars.ContextVar[int] = contextvars.ContextVar(
    "openai_call_count",
    default=0,
)


def reset_openai_call_count() -> None:
    _openai_call_count.set(0)


def get_openai_call_count() -> int:
    return _openai_call_count.get()


def _record_openai_call() -> int:
    call_count = _openai_call_count.get() + 1
    _openai_call_count.set(call_count)
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


def _normalize_customer_language(value: object) -> object:
    """Replace known internal jargon without changing factual content."""

    if isinstance(value, str):
        normalized = value
        for term, replacement in CUSTOMER_LANGUAGE_REPLACEMENTS.items():
            normalized = re.sub(
                rf"\b{re.escape(term)}\b",
                replacement,
                normalized,
                flags=re.IGNORECASE,
            )
        return normalized
    if isinstance(value, list):
        return [_normalize_customer_language(item) for item in value]
    if isinstance(value, dict):
        return {
            key: _normalize_customer_language(item)
            for key, item in value.items()
        }
    return value


def _normalize_final_analysis_payload(value: object) -> object:
    normalized = _normalize_customer_language(value)
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
    if kept_steps:
        normalized["as_is_steps"] = kept_steps
        problem_indexes = normalized.get("as_is_problem_step_indexes")
        if isinstance(problem_indexes, list):
            normalized["as_is_problem_step_indexes"] = [
                index_map[index]
                for index in problem_indexes
                if isinstance(index, int) and index in index_map
            ]
    return normalized


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
    call_number = _record_openai_call()
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
    maximum_attempts = 1 if is_final_analysis else 2
    request_deadline = perf_counter() + OPENAI_REQUEST_TIMEOUT_SECONDS
    client = OpenAI(
        api_key=_api_key(),
        timeout=OPENAI_REQUEST_TIMEOUT_SECONDS,
        max_retries=0,
    )
    model_options: dict[str, object] = {}
    if model.casefold().startswith("gpt-5"):
        model_options = {"reasoning_effort": "minimal", "verbosity": "low"}
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
                response_payload = _normalize_final_analysis_payload(response_payload)
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
    "fotograf",
    "identitätsprüf",
    "ringordner",
    "unterschrift",
    "verwechslung",
)
SOLUTION_ONLY_UNCERTAINTY_TERMS = (
    "auftragskarte",
    "automatis",
    "digital",
    "fotodokument",
    "software",
    "statusübersicht",
)


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
) -> None:
    user_facts = _combined_user_facts(answers)
    for follow_up in result.questions:
        question = follow_up.question.casefold()
        for term in SPECULATIVE_PROCESS_TERMS:
            if term in question and term not in user_facts:
                raise AIServiceError(
                    "Die Rückfragen konnten nicht sicher aus deinen Angaben "
                    "abgeleitet werden."
                )


def _validate_final_grounding(
    result: FinalAnalysisResult,
    answers: dict[str, str],
    selected_process: dict[str, str],
) -> None:
    user_facts = _combined_user_facts(answers, selected_process)
    existing_process_text = " ".join(
        [result.process_summary, *result.as_is_steps, *result.uncertainties]
    ).casefold()
    for term in SPECULATIVE_PROCESS_TERMS:
        if term in existing_process_text and term not in user_facts:
            raise AIServiceError(
                "Die Analyse enthielt eine nicht belegte Aussage zum heutigen Ablauf."
            )
    uncertainty_text = " ".join(result.uncertainties).casefold()
    for term in SOLUTION_ONLY_UNCERTAINTY_TERMS:
        if term in uncertainty_text and term not in user_facts:
            raise AIServiceError(
                "Die Unsicherheiten bezogen sich auf eine erst vorgeschlagene Lösung."
            )
    process_name = selected_process["process_name"].strip().casefold()
    summary_start = result.process_summary.strip().casefold()
    summary_without_quote = summary_start.lstrip("„\"'")
    quoted_name = re.compile(rf"^{re.escape(process_name)}[“\"']?(?:\s|[:–-])")
    if (
        summary_start.startswith(process_name)
        or quoted_name.search(summary_without_quote)
    ):
        raise AIServiceError(
            "Die Zusammenfassung wiederholte den Prozessnamen anstelle der Analyse."
        )


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
            "Ergebnisfelder verändern können: core_problem, first_change, ai_support, "
            "weekly_test, later_automation, zwingende menschliche Freigabe, kritische "
            "Voraussetzung oder die Entscheidung, ob KI heute sinnvoll ist. "
            "Wiederhole keine beantwortete Frage und behandle je Frage genau ein "
            "Thema. Frage nichts erneut, was in Ursprungserzählung, bestätigtem "
            "Ablauf oder Korrektur bereits eindeutig steht. Fragen, die den Ablauf "
            "nur ausführlicher machen, aber keine Entscheidung verändern, entfallen. "
            "Schlage weder eine Lösung noch eine neue Geschäftsregel vor. "
            "Erfinde keine Gefahr, keine Kontrollmaßnahme und kein Sicherheitsrisiko. "
            "Setze keine Fotos, Identitätsprüfung, Software oder Automatisierung "
            "voraus. Frage offen danach, was heute passiert. Wenn die fünf Kernfelder "
            "sicher erzeugt werden können, gib eine leere Liste zurück."
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
    _validate_follow_up_grounding(result, answers)
    return result


def generate_final_analysis(
    *,
    answers: dict[str, str],
    selected_process: dict[str, str],
    knowledge_chunks: Sequence[str],
    agent_state: dict[str, object] | None = None,
) -> FinalAnalysisResult:
    result = _parse_structured_output(
        system_prompt=(
            COMMON_GROUNDING_RULES
            + "\n\nTrenne strikt: A. USER FACTS sind die einzigen Fakten über "
            "den Betrieb. B. RETRIEVED PATTERNS sind internes Vergleichswissen und "
            "dürfen nie als bestehender Ablauf erscheinen. C. ALLOWED INFERENCES "
            "sind nur logisch zwingende Verbindungen zwischen belegten Schritten; "
            "kennzeichne fehlende Details stattdessen als Unsicherheit. D. "
            "RECOMMENDATIONS gehören nur in Chancen und Blueprint.\n\n"
            "Rekonstruiere den Ist-Ablauf, benenne Symptom, Ursache und Auswirkung "
            "des Kernengpasses getrennt. Erzeuge zuerst den verbindlichen Kernoutput: "
            "core_problem ist genau ein verständlicher Satz zum eigentlichen Problem; "
            "first_change ist genau eine kleine, konkrete priorisierte Maßnahme; "
            "ai_support beschreibt einen konkreten KI-Einsatz und wird zusätzlich in "
            "ai_input, ai_task, ai_output und human_check zerlegt; weekly_test enthält "
            "höchstens drei klar ausführbare Schritte für diese Woche und "
            "weekly_test_success ein beobachtbares Erfolgskriterium; later_automation "
            "nennt genau einen realistischen Ausbau nach erfüllter Voraussetzung. "
            "Wenn KI heute noch nicht sinnvoll ist, sage ausdrücklich: ‚KI ist heute "
            "noch nicht der erste Schritt.‘ und beschreibe, wobei sie nach einheitlicher "
            "Datenerfassung konkret unterstützen kann. Keine generischen Aussagen wie "
            "‚KI kann deinen Prozess optimieren‘. Erzeuge zusätzlich für die interne "
            "Vertiefung exakt drei realistische Startpunkte mit den "
            "Rängen 1, 2 und 3. Keine generischen CRM- oder Chatbot-Empfehlungen, "
            "keine erfundenen Geld- oder Zeitwerte und keine erfundenen APIs. "
            "In process_summary und as_is_steps dürfen nur USER FACTS und logisch "
            "zwingende Verbindungen stehen. Baue keine vorgeschlagenen Tools, "
            "Dokumente, Prüfungen oder Kontrollen rückwirkend in den Ist-Ablauf ein. "
            "Behaupte kein Sicherheitsproblem, das nicht genannt wurde. "
            "Unsicherheiten betreffen nur entscheidende fehlende Angaben zum heutigen "
            "Ablauf oder zur Bewertung einer Empfehlung; gib höchstens vier aus. "
            "Eine Unsicherheit darf keine erst vorgeschlagene Software, Dokumentation, "
            "Kontrolle oder andere Lösung als bestehenden Ablauf voraussetzen. "
            "Ordnung und Standardisierung darf ausdrücklich vor Digitalisierung "
            "oder Automatisierung stehen. Ordne jeden Startpunkt genau einer der "
            "vorgegebenen Kategorien zu und nenne Voraussetzung, Mini-Test, Aufwand "
            "sowie ein konkretes Akzeptanzrisiko ohne Prozentwert. Erzeuge außerdem "
            "einen kurzen Soll-Ablauf, der nur die nächste realistische Reifestufe "
            "abbildet. Markiere belegte Problemstellen im Ist-Ablauf über ihre "
            "nullbasierten Schrittpositionen. Wenn "
            "physische Gegenstände bearbeitet werden, prüfe insbesondere eine zentrale "
            "digitale Auftragskarte, eindeutige Zuordnung, Status und Ablageort, eine "
            "Benachrichtigung nach menschlicher Fertigmeldung sowie dokumentierte "
            "Änderungen und Kundenfreigaben. Fotos sind höchstens eine optionale "
            "Ergänzung und niemals ungefragt Pflicht oder Kernlösung. "
            "Medizinische, rechtliche, finanzielle, technische und kreative "
            "Entscheidungen dürfen nicht autonom automatisiert werden. Erzeuge "
            "einen Blueprint ausschließlich für Chance 1 mit drei bis fünf konkreten "
            "Schritten. required_prerequisites und human_decisions enthalten nur "
            "wirklich notwendige Grundlagen und menschliche Entscheidungen. "
            "current_process_summary fasst den bestätigten heutigen Ablauf kurz "
            "zusammen; optional_details bündelt nur vertiefende Informationen. "
            "Prüfe vor der Ausgabe "
            "jedes sichtbare Feld erneut darauf, dass es nur den Nutzerprozess "
            "beschreibt und keinerlei interne Wissensreferenz enthält. Beginne die "
            "Zusammenfassung direkt mit dem Ablauf und wiederhole weder den Titel "
            "noch eine Meta-Einleitung. Verwende klare deutsche Alltagssprache."
        ),
        payload={
            "A_USER_FACTS": {
                "ausgewaehlter_ablauf": selected_process,
                "antworten": answers,
                "bestaetigte_fakten": (agent_state or {}).get(
                    "confirmed_user_facts", []
                ),
            },
            "B_RETRIEVED_PATTERNS_INTERNAL_ONLY": list(knowledge_chunks),
            "C_ALLOWED_INFERENCES": {
                "regel": (
                    "Nur logisch zwingende Verbindungen; unbekannte Details bleiben "
                    "Unsicherheiten."
                ),
                "fachliche_ableitungen": (agent_state or {}).get(
                    "professional_inferences", []
                ),
                "offene_unsicherheiten": (agent_state or {}).get(
                    "uncertainties", []
                ),
                "widersprueche": (agent_state or {}).get("contradictions", []),
            },
            "D_RECOMMENDATIONS": (
                "Nur in opportunities und blueprint; nie im bestehenden Ablauf."
            ),
        },
        result_type=FinalAnalysisResult,
    )
    _validate_final_grounding(result, answers, selected_process)
    return result
