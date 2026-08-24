"""Erzählung, Fragen und Antworten.

Aus `routes.py` unverändert hierher verschoben. Kein HTTP, kein SQL - die
Datenbankabfragen laufen über `app.repository`.
"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app import repository
from app.agent_service import ProcessState, extract_process_state
from app.models import InterviewQuestion, ProcessOption

logger = logging.getLogger(__name__)



def all_answered(questions: list[InterviewQuestion]) -> bool:
    """Ob jede dieser Fragen eine nicht-leere Antwort hat."""

    return bool(questions) and all(
        question.answer_text and question.answer_text.strip()
        for question in questions
    )


def narrative_text(questions: list[InterviewQuestion]) -> str:
    """Die Erzählung des Kunden in seinen eigenen Worten.

    Wer das große Textfeld benutzt oder einspricht, dessen Text landet in allen
    Einstiegsantworten. Wer die Felder einzeln ausfüllt, hat verschiedene.
    Deshalb wird jede Antwort nur einmal genommen: sonst stünde die Erzählung
    doppelt im Prompt und in der Zitatprüfung.
    """

    gesehen: list[str] = []
    for question in questions:
        antwort = (question.answer_text or "").strip()
        if antwort and antwort not in gesehen:
            gesehen.append(antwort)
    return "\n\n".join(gesehen)
