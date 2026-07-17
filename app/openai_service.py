from __future__ import annotations

import json
import os
from collections.abc import Sequence
from pathlib import Path
from typing import TypeVar

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, ValidationError

from app.schemas import FinalAnalysisResult, FollowUpResult, ProcessSuggestionResult


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
    try:
        completion = OpenAI(api_key=_api_key()).chat.completions.parse(
            model=_structured_output_model(),
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(payload, ensure_ascii=False),
                },
            ],
            response_format=result_type,
        )
        parsed_result = completion.choices[0].message.parsed
    except (OpenAIError, ValidationError, ValueError, IndexError) as error:
        raise AIServiceError(
            "Die KI-Antwort konnte nicht zuverlässig verarbeitet werden."
        ) from error
    if parsed_result is None:
        raise AIServiceError("Die KI hat keine auswertbare Antwort geliefert.")
    return parsed_result


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
vorhandene Softwarefunktion oder API voraus.
""".strip()


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


def generate_follow_up_questions(
    *,
    answers: dict[str, str],
    selected_process: dict[str, str],
    knowledge_chunks: Sequence[str],
) -> FollowUpResult:
    return _parse_structured_output(
        system_prompt=(
            COMMON_GROUNDING_RULES
            + "\n\nErzeuge null bis höchstens drei entscheidende Rückfragen. "
            "Wiederhole keine beantwortete Frage. Jede Frage behandelt genau ein "
            "Thema. Stelle keine neue allgemeine Unternehmensfrage. Widersprüche "
            "dürfen ausdrücklich angesprochen werden. Wenn die Informationen "
            "ausreichen, gib eine leere Liste zurück."
        ),
        payload={
            "ausgewaehlter_prozess": selected_process,
            "nutzerangaben": answers,
            "internes_vergleichswissen_nicht_ausgeben": list(knowledge_chunks),
        },
        result_type=FollowUpResult,
    )


def generate_final_analysis(
    *,
    answers: dict[str, str],
    selected_process: dict[str, str],
    knowledge_chunks: Sequence[str],
) -> FinalAnalysisResult:
    return _parse_structured_output(
        system_prompt=(
            COMMON_GROUNDING_RULES
            + "\n\nRekonstruiere den Ist-Prozess, benenne den Kernengpass und "
            "erzeuge exakt drei prozessbezogene Automatisierungschancen mit den "
            "Rängen 1, 2 und 3. Keine generischen CRM- oder Chatbot-Empfehlungen, "
            "keine erfundenen Geld- oder Zeitwerte und keine erfundenen APIs. "
            "Einfache Lösungen dürfen vor komplexen KI-Systemen stehen. "
            "Medizinische, rechtliche, finanzielle, technische und kreative "
            "Entscheidungen dürfen nicht autonom automatisiert werden. Erzeuge "
            "einen Blueprint ausschließlich für Chance 1. Prüfe vor der Ausgabe "
            "jedes sichtbare Feld erneut darauf, dass es nur den Nutzerprozess "
            "beschreibt und keinerlei interne Wissensreferenz enthält."
        ),
        payload={
            "ausgewaehlter_prozess": selected_process,
            "nutzerangaben": answers,
            "internes_vergleichswissen_nicht_ausgeben": list(knowledge_chunks),
        },
        result_type=FinalAnalysisResult,
    )
