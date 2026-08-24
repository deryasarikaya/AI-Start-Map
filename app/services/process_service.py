"""Der Wegweiser durch den Ablauf.

Von der Prozesserkennung ist nach dem kurzen Weg nichts übrig: Es gibt keine
Ablaufvorschläge, keine Auswahl und keine Rückfragen mehr. Geblieben ist die
eine Frage, die der Ablauf noch stellt - wo steht der Kunde gerade.
"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app import repository
from app.services.interview_service import all_answered

logger = logging.getLogger(__name__)


def next_valid_path(database_session: Session, session_id: int) -> str:
    """Sagt, wo der Kunde im Ablauf tatsächlich steht.

    Der Türsteher: Wer eine Seite aufruft, für die er noch nicht so weit ist,
    wird hierhin geschickt. Vier Stationen — Erzählung, Warteschirm,
    „Das habe ich verstanden", Ergebnis. Der Warteschirm steht zweimal im Weg,
    einmal vor und einmal nach der Verstandenseite.
    """

    if repository.get_result(database_session, session_id) is not None:
        return f"/sessions/{session_id}/results"
    context_questions = repository.get_questions(
        database_session,
        session_id,
        phase="context",
    )
    if not all_answered(context_questions):
        return f"/sessions/{session_id}/interview"
    zwischenstand = repository.get_partial_result(database_session, session_id)
    if (
        zwischenstand is not None
        and zwischenstand.payload is not None
        and not zwischenstand.moving_on
    ):
        return f"/sessions/{session_id}/verstanden"
    return f"/sessions/{session_id}/processing"
