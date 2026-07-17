from __future__ import annotations

import json
import os
import re
from collections.abc import Sequence
from pathlib import Path
from typing import TypeVar

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, ValidationError

from app.schemas import (
    FinalAnalysisResult,
    FollowUpResult,
    ProcessBoundaryResult,
    ProcessSuggestionResult,
)


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


class AIServiceError(RuntimeError):
    pass


StructuredResult = TypeVar("StructuredResult", bound=BaseModel)


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
    try:
        response = OpenAI(api_key=_api_key()).embeddings.create(
            model=get_embedding_model(),
            input=list(texts),
        )
    except OpenAIError as error:
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
    for attempt in range(2):
        retry_instruction = (
            "\n\nDie vorherige Ausgabe war nicht vollständig regelkonform. "
            "Prüfe jetzt jedes Feld erneut gegen das Ausgabeschema und alle "
            "inhaltlichen Verbote."
            if attempt
            else ""
        )
        try:
            completion = OpenAI(api_key=_api_key()).chat.completions.parse(
                model=_structured_output_model(),
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
            )
            parsed_result = completion.choices[0].message.parsed
            if parsed_result is not None:
                return parsed_result
            last_error = ValueError("Keine auswertbare Antwort")
        except (OpenAIError, ValidationError, ValueError, IndexError) as error:
            last_error = error
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
            + "\n\nErzeuge ein bis drei konkrete End-to-End-Prozesse. Jeder hat "
            "einen klaren Beginn und ein klares Ende. Allgemeine Kategorien wie "
            "Marketing, Organisation oder Kundenkommunikation sind unzulässig. "
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


def generate_follow_up_questions(
    *,
    answers: dict[str, str],
    selected_process: dict[str, str],
    knowledge_chunks: Sequence[str],
) -> FollowUpResult:
    result = _parse_structured_output(
        system_prompt=(
            COMMON_GROUNDING_RULES
            + "\n\nErzeuge null bis höchstens drei entscheidende Rückfragen zum "
            "heutigen tatsächlichen Ablauf. Jede Rückfrage muss unmittelbar auf "
            "einer belegten Nutzerangabe oder einer darin erkennbaren Lücke beruhen. "
            "Wiederhole keine beantwortete Frage und behandle je Frage genau ein "
            "Thema. Schlage weder eine Lösung noch eine neue Geschäftsregel vor. "
            "Erfinde keine Gefahr, keine Kontrollmaßnahme und kein Sicherheitsrisiko. "
            "Setze keine Fotos, Identitätsprüfung, Software oder Automatisierung "
            "voraus. Frage offen danach, was heute passiert. Wenn die Informationen "
            "ausreichen, gib eine leere Liste zurück."
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
            "Rekonstruiere den Ist-Ablauf, benenne den Kernengpass und "
            "erzeuge exakt drei prozessbezogene Automatisierungschancen mit den "
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
            "Einfache Prozessstandardisierung darf vor einer komplexen Lösung stehen, "
            "aber die drei Chancen sollen nachvollziehbar zwischen Standardisierung, "
            "einfacher Digitalisierung und Automatisierung unterscheiden. Wenn "
            "physische Gegenstände bearbeitet werden, prüfe insbesondere eine zentrale "
            "digitale Auftragskarte, eindeutige Zuordnung, Status und Ablageort, eine "
            "Benachrichtigung nach menschlicher Fertigmeldung sowie dokumentierte "
            "Änderungen und Kundenfreigaben. Fotos sind höchstens eine optionale "
            "Ergänzung und niemals ungefragt Pflicht oder Kernlösung. "
            "Medizinische, rechtliche, finanzielle, technische und kreative "
            "Entscheidungen dürfen nicht autonom automatisiert werden. Erzeuge "
            "einen Blueprint ausschließlich für Chance 1. Prüfe vor der Ausgabe "
            "jedes sichtbare Feld erneut darauf, dass es nur den Nutzerprozess "
            "beschreibt und keinerlei interne Wissensreferenz enthält. Beginne die "
            "Zusammenfassung direkt mit dem Ablauf und wiederhole weder den Titel "
            "noch eine Meta-Einleitung. Verwende klare deutsche Alltagssprache."
        ),
        payload={
            "A_USER_FACTS": {
                "ausgewaehlter_ablauf": selected_process,
                "antworten": answers,
            },
            "B_RETRIEVED_PATTERNS_INTERNAL_ONLY": list(knowledge_chunks),
            "C_ALLOWED_INFERENCES": (
                "Nur logisch zwingende Verbindungen; unbekannte Details bleiben "
                "Unsicherheiten."
            ),
            "D_RECOMMENDATIONS": (
                "Nur in opportunities und blueprint; nie im bestehenden Ablauf."
            ),
        },
        result_type=FinalAnalysisResult,
    )
    _validate_final_grounding(result, answers, selected_process)
    return result
