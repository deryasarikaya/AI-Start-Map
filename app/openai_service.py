"""Alle Aufrufe des Sprachmodells.

Jede Stelle, an der die Anwendung mit OpenAI spricht, geht durch dieses Modul.
Es lädt die Prompttexte aus `app/prompts/`, schickt die Anfrage los und gibt
eine geprüfte Antwort zurück — oder einen `AIServiceError`.

Drei Dinge, die hier absichtlich zusammenliegen:

- **Zeitgrenzen.** Kleine Aufrufe haben ein knappes Budget, die Endanalyse ein
  großes. Ohne Grenze wartet der Kunde unbegrenzt.
- **Aufrufzähler.** Damit lässt sich in Tests prüfen, dass nicht versehentlich
  echte Aufrufe hinausgehen.
- **Sprachliche Nachbesserung.** Ein paar Wendungen werden vereinheitlicht,
  bevor der Text weitergereicht wird.

Die Prompttexte selbst stehen nicht hier, sondern als eigene Dateien in
`app/prompts/`. So kann man sie ändern, ohne Code anzufassen.
"""

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

from app.result_schema import (
    freigegebene_module,
    MINIMUM_EVIDENCE,
    Diagnose,
    ResultPartOne,
    ResultPartTwo,
    ResultPartTwoRest,
    ResultPartTwoViews,
    Zielarchitektur,
    narrative,
    rejected_quotes,
)
from app.schemas import (
    AS_IS_META_PATTERN,
    CURRENT_PROCESS_PATTERN,
    FOLLOW_UP_SOLUTION_PATTERN,
    FinalAnalysisResult,
    FollowUpQuestion,
    FollowUpResult,
    FORBIDDEN_CUSTOMER_TERMS,
)


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

PROMPT_DIRECTORY = Path(__file__).resolve().parent / "prompts"


def _prompt(name: str) -> str:
    """Lädt einen Prompttext aus `app/prompts/`.

    Die Prompttexte liegen als eigene Dateien, damit man sie ändern kann,
    ohne Python anzufassen.
    """

    try:
        return (PROMPT_DIRECTORY / f"{name}.md").read_text(encoding="utf-8").strip()
    except OSError as error:
        raise AIServiceError(
            f"Der Prompttext „{name}“ konnte nicht geladen werden."
        ) from error


class AIServiceError(RuntimeError):
    pass


StructuredResult = TypeVar("StructuredResult", bound=BaseModel)
logger = logging.getLogger(__name__)
OPENAI_REQUEST_TIMEOUT_SECONDS = 45.0
# Die Streuung kommt von der API, nicht von der Eingabe- oder Ausgabelänge.
# Kontrolliert am Handwerksfall gemessen: mit Wissensdatei 87,1 s bei 4933
# Zeichen Kundentext, ohne Wissensdatei 245,3 s bei 5309 Zeichen. Der Lauf mit
# der größeren Eingabe war dreimal schneller und erzeugte weniger Text.
# Derselbe Fall lief an anderer Stelle in 89,3 s und in 289,7 s.
FINAL_ANALYSIS_TIMEOUT_SECONDS = 300.0
# Die beiden Teile der neuen Ergebnisseite liegen dazwischen: groesser als
# eine Rueckfrage, kleiner als die alte Endanalyse. Gemessen: Teil 1 rund
# 20 Sekunden, Teil 2 laeuft mit 45 Sekunden ins Limit.
RESULT_TIMEOUT_SECONDS = 180.0
OPENAI_RETRIEVAL_TIMEOUT_SECONDS = 6.0
class CallCountUnavailable(RuntimeError):
    """Der Zähler wurde gelesen, wo er nichts weiß.

    Wird geworfen, statt still eine Null zu liefern. Eine stille Null ist die
    schlechteste Antwort: Sie sieht aus wie „keine Aufrufe" und heißt in
    Wahrheit „hier wurde nicht gezählt".
    """


# Die Zähler stehen in einer *veränderlichen* Zelle, nicht als Zahl direkt in
# der Kontextvariablen. Der Grund: Eine Route läuft im Threadpool, also in
# einer Kopie des Kontexts. Eine Zahl darin zu ersetzen wirkt nur in der
# Kopie — wer von aussen liest, sähe immer 0. Die Kopie zeigt
# aber auf dieselbe Liste, und was hineingeschrieben wird, sehen beide.
_openai_calls: contextvars.ContextVar[list[int] | None] = contextvars.ContextVar(
    "openai_call_count",
    default=None,
)
_embedding_calls: contextvars.ContextVar[list[int] | None] = contextvars.ContextVar(
    "embedding_call_count",
    default=None,
)


def reset_openai_call_count() -> None:
    """Setzt die Zähler für Modell- und Einbettungsaufrufe zurück.

    Eine vorhandene Zelle wird geleert, nicht ersetzt. Sonst bekäme ein
    Zurücksetzen innerhalb der Route wieder eine eigene Zelle, und der Aufrufer
    von aussen läse weiter seine alte.
    """

    for zelle, variable in (
        (_openai_calls.get(), _openai_calls),
        (_embedding_calls.get(), _embedding_calls),
    ):
        if zelle is None:
            variable.set([0])
        else:
            zelle[0] = 0


def get_openai_call_count() -> int:
    """Wie viele Modellaufrufe dieser Durchlauf bisher gebraucht hat.

    Wer ohne vorheriges `reset_openai_call_count()` liest, bekommt eine
    Ausnahme statt einer Null — dann hat hier nie eine Zählung begonnen.
    """

    zelle = _openai_calls.get()
    if zelle is None:
        raise CallCountUnavailable(
            "Hier wurde nichts gezählt. Ruf reset_openai_call_count() auf, "
            "bevor der Durchlauf beginnt — und zwar in demselben Kontext, in "
            "dem du später liest."
        )
    return zelle[0]


def counted_calls_for_logging() -> object:
    """Der Zählerstand für eine Protokollzeile, oder das Wort dafür, dass keiner da ist.

    Eine Protokollzeile darf keinen Durchlauf abbrechen. Sie darf aber auch
    keine Null erfinden — deshalb steht dort dann `ungezaehlt` und nicht `0`.
    """

    try:
        return get_openai_call_count()
    except CallCountUnavailable:
        return "ungezaehlt"


def _record_openai_call() -> int:
    """Zählt einen Modellaufruf und gibt die laufende Nummer zurück."""

    return _zaehle(_openai_calls)


def _record_embedding_call() -> int:
    """Zählt einen Einbettungsaufruf und gibt die laufende Nummer zurück."""

    return _zaehle(_embedding_calls)


def _zaehle(variable: contextvars.ContextVar[list[int] | None]) -> int:
    """Erhöht den Zähler in seiner Zelle und gibt den neuen Stand zurück.

    Legt notfalls eine Zelle an: Ein Aufruf darf nie daran scheitern, dass
    niemand zurückgesetzt hat. Das Lesen scheitert dann trotzdem — sichtbar.
    """

    zelle = variable.get()
    if zelle is None:
        zelle = [0]
        variable.set(zelle)
    zelle[0] += 1
    return zelle[0]


def _validation_error_fields(error: ValidationError) -> list[str]:
    """Welche Felder die Schemaprüfung bemängelt hat - fürs Protokoll."""

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
    """Räumt die Modellantwort auf, bevor sie geprüft wird.

    Entfernt Meta-Sätze aus den Ist-Schritten und zieht die
    Positionsangaben der Problemschritte mit, damit sie weiter auf die
    richtigen Schritte zeigen.
    """

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
    """Formt eine Rückfrage so um, dass sie nach dem heutigen Ablauf fragt."""

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
    """Bringt die Rückfrage-Antwort in die erwartete Form."""

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
    """Der API-Schlüssel aus der Umgebung, sonst ein sprechender Fehler."""

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or api_key == "your_openai_api_key":
        raise AIServiceError(
            "Der KI-Zugang ist noch nicht eingerichtet. Trage OPENAI_API_KEY "
            "lokal in der .env-Datei ein."
        )
    return api_key


# Die vier Stellschrauben des Modellaufrufs. Sie stehen hier, damit eine Messung
# genau eine Sache ändern kann, ohne dass jemand Code anfasst — und weil ein
# Wert, den man umstellen kann, ehrlicher ist als eine Zahl mitten im Aufruf.
# Ohne gesetzte Umgebungsvariable gilt jeweils das, was im Betrieb gelten soll.
def _reasoning_effort(*, gruendlich: bool, fuellt_nur: bool = False) -> str:
    """Wie viel das Modell nachdenken soll.

    Wörtlich abschreiben aus einem langen Text ist genau die Aufgabe, bei der
    minimales Nachdenken schludert. Die Ergebnisteile müssen deshalb
    ausdrücklich in den gründlichen Zweig fallen: Zeigt die Bedingung am
    Vertrag vorbei, läuft die wichtigste Ausgabe der Anwendung auf der
    niedrigsten Stufe.

    **Teil 2 denkt weniger.** Er diagnostiziert nicht, er füllt Ansichten und
    Listen aus einem Befund, der schon feststeht. Auf `medium` scheiterten
    drei von zwölf Evaluationsfällen an `finish_reason=length`. Gemessen an
    einem der drei: Die Denk-Token zählen gegen dieselbe Grenze wie die
    Ausgabe, und auf `medium` waren sie 2.432 von 5.284 Token — auf `low`
    noch 576, bei gleich langer und vollständiger Antwort. Wer 16.000
    Token füllt, denkt sich fest; mehr Platz zu geben verlängert das nur.
    """

    if not gruendlich:
        return "minimal"
    if fuellt_nur:
        return os.getenv("OPENAI_REASONING_EFFORT_TEIL2", "").strip() or "low"
    return os.getenv("OPENAI_REASONING_EFFORT", "").strip() or "medium"


def _verbosity() -> str:
    return os.getenv("OPENAI_VERBOSITY", "").strip() or "low"


def _max_completion_tokens() -> int:
    """Die Obergrenze für eine Antwort, Denkschritte eingerechnet.

    Vorher unbegrenzt. Eine Obergrenze deckelt nicht die übliche Antwort — die
    liegt weit darunter —, sondern den Fall, in dem eine Erzeugung nicht mehr
    zum Ende kommt.
    """

    return int(os.getenv("OPENAI_MAX_COMPLETION_TOKENS", "").strip() or 16000)


def _strict_schema_is_used() -> bool:
    """Ob die Ausgabe an das Pydantic-Schema gebunden wird.

    Bei `parse` baut OpenAI aus dem Modell eine Grammatik, an die jeder Token
    gebunden ist. Die Gegenprobe ist der JSON-Modus mit dem Schema als Text im
    Prompt: dieselbe Aufgabe, ohne Grammatik.
    """

    return (os.getenv("OPENAI_STRUCTURED_MODE", "").strip() or "strict") == "strict"


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
    """Bettet Texte für die Wissenssuche ein.

    Muss dasselbe Modell benutzen, mit dem der Index gebaut wurde -
    sonst passen die Vektoren nicht zusammen.
    """

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


def _ask_the_model(
    client: OpenAI,
    *,
    model: str,
    system_prompt: str,
    payload: dict[str, object],
    result_type: type[StructuredResult],
    timeout: float,
    model_options: dict[str, object],
) -> object:
    """Stellt die Frage — mit strengem Schema oder im JSON-Modus.

    Der Unterschied: Bei `parse` baut OpenAI aus dem Pydantic-Modell eine
    Grammatik, an die jeder erzeugte Token gebunden wird. Im JSON-Modus steht
    dasselbe Schema nur als Text im Prompt, und die Ausgabe muss lediglich
    gültiges JSON sein.

    Beide Wege liefern eine Antwort in derselben Form, und beide werden danach
    gegen den Vertrag geprüft — der JSON-Modus ist also kein Loch in der
    Prüfung, nur ein anderer Weg zur Antwort.
    """

    nachrichten: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]
    if _strict_schema_is_used():
        return client.chat.completions.with_raw_response.parse(
            model=model,
            messages=nachrichten,
            response_format=result_type,
            timeout=timeout,
            **model_options,
        )
    nachrichten[0]["content"] += (
        "\n\nAntworte ausschließlich mit einem JSON-Objekt nach genau diesem "
        "Schema. Keine Erklärung davor oder danach, kein Markdown:\n"
        + json.dumps(result_type.model_json_schema(), ensure_ascii=False)
    )
    return client.chat.completions.with_raw_response.create(
        model=model,
        messages=nachrichten,
        response_format={"type": "json_object"},
        timeout=timeout,
        **model_options,
    )


def parse_structured_output(
    *,
    system_prompt: str,
    payload: dict[str, object],
    result_type: type[StructuredResult],
) -> StructuredResult:
    """Ruft das Modell und lässt es direkt ins Zielschema antworten.

    Zwei Versuche: Fällt der erste durch die Schemaprüfung, bekommt der
    zweite den Hinweis, jedes Feld erneut zu prüfen.

    **Jeder Versuch hat sein eigenes Zeitbudget.** Ein gemeinsames Budget
    macht den zweiten Versuch wertlos: Läuft der erste in die Zeitgrenze,
    bleibt für den zweiten nichts übrig — er bricht ab, bevor er das Modell
    überhaupt gerufen hat. Der Schutz gegen Zeitüberschreitungen wäre damit
    genau in dem Fall wirkungslos, für den er gebaut ist.
    """

    last_error: Exception | None = None
    model = _structured_output_model()
    is_final_analysis = result_type is FinalAnalysisResult
    # Seit dem 21.08. entsteht der untere Teil in zwei Aufrufen. Beide
    # sind Ergebnisteile und bekommen dasselbe Zeitbudget wie vorher der
    # eine.
    zweiter_teil = (ResultPartTwoViews, ResultPartTwoRest, ResultPartTwo)
    is_result_part = result_type in (
        ResultPartOne,
        Diagnose,
        Zielarchitektur,
        *zweiter_teil,
    )
    is_follow_up = result_type is FollowUpResult
    maximum_attempts = 1 if is_follow_up else 2
    request_timeout = (
        RESULT_TIMEOUT_SECONDS
        if is_result_part
        else FINAL_ANALYSIS_TIMEOUT_SECONDS
        if is_final_analysis
        else OPENAI_REQUEST_TIMEOUT_SECONDS
    )
    # Jeder Versuch bekommt das volle Budget, nicht einen Anteil davon.
    #
    # Zuerst hatte ich das Budget auf die Versuche aufgeteilt, damit die
    # Obergrenze für den ganzen Aufruf gleich bleibt. Zehn gemessene Läufe
    # haben das widerlegt: Die Antwortzeit des Modells schwankt stark, ein
    # Aufruf braucht mal 25 und mal 150 Sekunden. Mit halbem Budget starben
    # genau die Aufrufe, die vorher noch durchkamen — vier von sechs Läufen
    # gingen an einem Zeitablauf verloren. Lieber ein langer Lauf als keiner.
    attempt_timeout = request_timeout
    client = OpenAI(
        api_key=_api_key(),
        timeout=attempt_timeout,
        max_retries=0,
    )
    model_options: dict[str, object] = {
        "max_completion_tokens": _max_completion_tokens()
    }
    if model.casefold().startswith("gpt-5"):
        model_options |= {
            # Die Ergebnisteile gehören dazu: Sie sind die wichtigste
            # Ausgabe der Anwendung.
            "reasoning_effort": _reasoning_effort(
                gruendlich=is_final_analysis or is_result_part,
                fuellt_nur=result_type in zweiter_teil,
            ),
            "verbosity": _verbosity(),
        }
    for attempt in range(maximum_attempts):
        retry_instruction = (
            "\n\nDie vorherige Ausgabe war nicht vollständig regelkonform. "
            "Prüfe jetzt jedes Feld erneut gegen das Ausgabeschema und alle "
            "inhaltlichen Verbote."
            if attempt
            else ""
        )
        remaining_seconds = attempt_timeout
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
            raw_response = _ask_the_model(
                client,
                model=model,
                system_prompt=system_prompt + retry_instruction,
                payload=payload,
                result_type=result_type,
                timeout=remaining_seconds,
                model_options=model_options,
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


COMMON_GROUNDING_RULES = _prompt("grundregeln")

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


def _selected_pattern_briefing(
    recommendation_context: dict[str, object] | None,
) -> dict[str, object]:
    """Das bereits gewählte Muster als Briefing, nicht als Käfig.

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


def generate_diagnosis(
    *,
    narrative_text: str,
    knowledge_chunks: Sequence[str],
) -> Diagnose:
    """Aufruf 1: Was ist hier los? **Ohne jede Lösung.**

    Lösungsname, Module und Zielbild entstehen bewusst **nicht** hier.
    Stünden sie schon in der Diagnose, wäre die Lösung fest, bevor
    irgendein Katalog gefragt ist — und niemand könnte prüfen, ob es sie
    überhaupt gibt.
    """

    payload: dict[str, object] = {
        "SO_ERZAEHLT_ES_DER_BETRIEB": {"erzaehlung": narrative_text},
        "VERBOTENE_WOERTER": list(FORBIDDEN_CUSTOMER_TERMS),
        "VERGLEICHSWISSEN_DIAGNOSE_NIE_AUSGEBEN": list(knowledge_chunks),
    }
    with narrative(narrative_text):
        return _diagnosis_with_enough_evidence(payload)


def _diagnosis_with_enough_evidence(payload: dict[str, object]) -> Diagnose:
    """Holt die Diagnose und sorgt für genug wörtliche Belege.

    Die Zitatprüfung im Vertrag sortiert einzeln aus, statt das ganze
    Ergebnis an einem ungenauen Zitat scheitern zu lassen. Bleiben danach
    zu wenige übrig, wird genau **einmal** nachgefragt — mit den
    abgelehnten Zitaten im Prompt, damit das Modell weiß, woran es lag.
    Ein blindes Neuwürfeln würde denselben Fehler noch einmal machen.

    Bleibt es auch danach zu wenig, geht es **ohne** Belegabschnitt
    weiter. Die Verstandenseite ist dann schwächer, aber sie existiert —
    das ist besser, als einen Kunden wegen eines Wortes vor einen Fehler
    zu setzen. Ein dritter Aufruf findet nicht statt.
    """

    erster = parse_structured_output(
        system_prompt=_prompt("diagnose"),
        payload=payload,
        result_type=Diagnose,
    )
    if len(erster.verstanden.belege) >= MINIMUM_EVIDENCE:
        return erster

    abgelehnt = rejected_quotes()
    logger.warning(
        "diagnosis.evidence_too_thin belege=%d abgelehnt=%d wortlaut=%s "
        "aktion=zweiter_versuch",
        len(erster.verstanden.belege),
        len(abgelehnt),
        abgelehnt,
    )
    zweiter = parse_structured_output(
        system_prompt=_prompt("diagnose") + _quote_retry_hint(abgelehnt),
        payload=payload,
        result_type=Diagnose,
    )
    if len(zweiter.verstanden.belege) >= MINIMUM_EVIDENCE:
        logger.info(
            "diagnosis.evidence_recovered belege=%d",
            len(zweiter.verstanden.belege),
        )
        return zweiter

    logger.warning(
        "diagnosis.evidence_dropped belege=%d aktion=ohne_belegabschnitt",
        len(zweiter.verstanden.belege),
    )
    return zweiter.model_copy(
        update={
            "verstanden": zweiter.verstanden.model_copy(update={"belege": []})
        }
    )


def generate_target_architecture(
    *,
    narrative_text: str,
    diagnose: Diagnose,
    vorgeschlagene_familien: Sequence[str] = (),
) -> Zielarchitektur:
    """Aufruf 2: Welche Familien aus dem Katalog — und wie heißen sie hier?

    Das Modell sieht **den ganzen freigegebenen Katalog**, nicht nur das
    Abgerufene: Ein schlechter Treffer im Abruf soll nicht verhindern, dass
    die richtige Familie überhaupt wählbar ist. Was der Abruf gefunden hat,
    steht als Vorschlag dabei.

    Geprüft wird danach serverseitig, im Vertrag: jede Kennung gegen die
    Freigabeliste, jedes Modul gegen die Bausteine seiner Familien. Ein
    Verstoß ist ein Fehler und löst den eingebauten zweiten Versuch aus.
    """

    from app import solution_catalog

    katalog = solution_catalog.zur_auswahl(list(vorgeschlagene_familien))
    bausteine = solution_catalog.bausteine_von([e["id"] for e in katalog])
    payload: dict[str, object] = {
        "DIAGNOSE": diagnose.model_dump(mode="json"),
        "LOESUNGSKATALOG": [
            {**eintrag, "bausteine": bausteine.get(eintrag["id"], [])}
            for eintrag in katalog
        ],
        "ABRUF_SCHLAEGT_VOR": list(vorgeschlagene_familien),
        # **Kein Zielbildmuster.** Es hier aus dem Abrufvorschlag zu
        # bestimmen hiesse, es an Familien zu hängen, die noch niemand
        # gewählt hat. Das Muster folgt nach der Prüfung aus den
        # **ausgewählten** Familien.
        "VERBOTENE_WOERTER": list(FORBIDDEN_CUSTOMER_TERMS),
    }
    with narrative(narrative_text):
        gewaehlt = parse_structured_output(
            system_prompt=_prompt("zielarchitektur"),
            payload=payload,
            result_type=Zielarchitektur,
        )
    logger.info(
        "solution.selected familien=%s module=%d katalogtreffer=%s neue_technik=%s",
        gewaehlt.selected_solution_family_ids,
        len(gewaehlt.module),
        gewaehlt.catalog_fit,
        gewaehlt.recommend_new_technology,
    )
    return gewaehlt


def _quote_retry_hint(abgelehnte_zitate: Sequence[str]) -> str:
    """Sagt dem Modell, welche Zitate abgelehnt wurden und warum."""

    if not abgelehnte_zitate:
        return (
            "\n\nZWEITER VERSUCH — DIE BELEGE: Der vorherige Versuch hatte zu "
            "wenige verwertbare Zitate. Wähle zwei bis drei Stellen aus der "
            "Erzählung und kopiere sie Zeichen für Zeichen."
        )
    aufzaehlung = "\n".join(f"- {zitat!r}" for zitat in abgelehnte_zitate)
    return (
        "\n\nZWEITER VERSUCH — DIE BELEGE: Diese Zitate wurden abgelehnt, weil "
        "sie nicht wörtlich in der Erzählung stehen:\n"
        f"{aufzaehlung}\n"
        "Ein Beleg muss Zeichen für Zeichen aus der Erzählung kopiert sein: "
        "nicht umformulieren, nicht zusammenfassen, nicht glätten, keine Wörter "
        "ergänzen oder weglassen. Suche zwei bis drei Stellen, die wirklich so "
        "dastehen, und übernimm sie unverändert."
    )


def _part_two_payload(
    narrative_text: str,
    part_one: ResultPartOne,
    knowledge_chunks: Sequence[str],
    recommendation_context: dict[str, object] | None,
    loesungswissen: dict[str, object] | None = None,
) -> dict[str, object]:
    """Was beide Hälften des unteren Teils mitbekommen — dasselbe.

    Darin steckt das Geländer bis zur Seite: die geprüften Module aus
    dem oberen Teil und **nur** die ausgewählten Familien samt ihrer
    Fähigkeiten. Was nicht gewählt wurde, steht hier nicht — es kann
    also auch nicht in die Formulierung geraten.
    """

    return {
        **(loesungswissen or {}),
        "SO_ERZAEHLT_ES_DER_BETRIEB": {"erzaehlung": narrative_text},
        "BEREITS_GESCHRIEBENER_OBERER_TEIL": part_one.model_dump(),
        "GEWAEHLTES_MUSTER": _selected_pattern_briefing(recommendation_context),
        "VERBOTENE_WOERTER": list(FORBIDDEN_CUSTOMER_TERMS),
        "NUR_INTERNES_VERGLEICHSWISSEN_NIE_AUSGEBEN": list(knowledge_chunks),
    }


def generate_result_part_two(
    *,
    narrative_text: str,
    part_one: ResultPartOne,
    knowledge_chunks: Sequence[str],
    recommendation_context: dict[str, object] | None = None,
    loesungswissen: dict[str, object] | None = None,
) -> ResultPartTwo:
    """Erzeugt den unteren Teil der Ergebnisseite — in zwei Aufrufen.

    **2a schreibt die Ansichten, 2b alles Übrige.** Getrennt, weil der
    ungeteilte Aufruf mit 65 Feldern und Schachtelungstiefe acht doppelt so
    groß war wie Aufruf 1 — und in fast der Hälfte der Läufe nicht mehr
    antwortete, während Aufruf 1 zehn von zehn schaffte.

    Beide bekommen denselben oberen Teil mit, damit sie dieselbe Lösung
    beschreiben. Scheitert einer von beiden, wirft er — und der Aufrufer
    speichert nichts. Ein halbes Ergebnis gibt es nicht, weder hier noch
    aus Beispieldaten.
    """

    payload = _part_two_payload(
        narrative_text,
        part_one,
        knowledge_chunks,
        recommendation_context,
        loesungswissen,
    )
    # **Der Geltungsbereich für Aufruf 3 und 4.** Innerhalb dieses Rahmens
    # muss sich jede Ansicht, jedes System, jede Ebene und jeder Schritt
    # auf eines der geprüften Module berufen. Was sich auf nichts beruft,
    # kommt nicht durch.
    module = [modul.name for modul in part_one.module]
    familien = [
        kennung for modul in part_one.module for kennung in modul.solution_family_ids
    ]
    with narrative(narrative_text), freigegebene_module(module, familien):
        ansichten = parse_structured_output(
            system_prompt=_prompt("ergebnis_teil2a"),
            payload=payload,
            result_type=ResultPartTwoViews,
        )
        # Die Ansichten gehen in den zweiten Aufruf mit: Aufgabenteilung
        # und Wert sollen zu dem passen, was der Kunde gezeigt bekommt.
        uebriges = parse_structured_output(
            system_prompt=_prompt("ergebnis_teil2b"),
            payload={**payload, "BEREITS_GESCHRIEBENE_ANSICHTEN": ansichten.model_dump()},
            result_type=ResultPartTwoRest,
        )
        return ResultPartTwo.model_validate(
            {**ansichten.model_dump(), **uebriges.model_dump()}
        )
