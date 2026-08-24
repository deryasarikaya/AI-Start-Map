"""Alle Datenbankabfragen der Anwendung.

Hier steht, was die Anwendung aus der Datenbank liest und was sie darin
anlegt oder löscht — sonst nichts. Kein HTTP, keine Ablauflogik, keine
Modellaufrufe.

Die Transaktionsgrenze bleibt bewusst ausserhalb: `commit` und `rollback`
gehören dorthin, wo über den Ausgang einer Anfrage entschieden wird, also in
die Route. Dieses Modul ändert nur den Inhalt der Sitzung.

Die Funktionen wurden unverändert aus `routes.py` hierher verschoben; die
Namen ohne führenden Unterstrich sind dieselben Funktionen.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models import (
    AnalysisSession,
    InterviewQuestion,
    PartialResult,
    Result,
)


def get_session(
    database_session: Session,
    session_id: int,
) -> AnalysisSession | None:
    return database_session.scalar(
        select(AnalysisSession).where(AnalysisSession.session_id == session_id)
    )


def get_questions(
    database_session: Session,
    session_id: int,
    *,
    phase: str | None = None,
) -> list[InterviewQuestion]:
    """Die Fragen einer Sitzung, wahlweise nur einer Phase.

    Die drei Phasen heißen `context` (die zwei Einstiegsfragen),
    `process` (die sieben Prozessfragen) und `follow_up` (null bis vier
    Rückfragen).
    """

    statement = select(InterviewQuestion).where(
        InterviewQuestion.session_id == session_id
    )
    if phase is not None:
        statement = statement.where(InterviewQuestion.question_phase == phase)
        statement = statement.order_by(InterviewQuestion.question_order)
    else:
        statement = statement.order_by(InterviewQuestion.question_id)
    return list(database_session.scalars(statement))


def acquire_session_write_lock(
    database_session: Session,
    session_id: int,
) -> bool:
    """Verhindert, dass zwei Anfragen dieselbe Sitzung gleichzeitig schreiben.

    Die Sperre hält bis zum Ende der Transaktion und wird von PostgreSQL
    selbst wieder freigegeben.
    """

    return bool(
        database_session.scalar(
            text("SELECT pg_try_advisory_xact_lock(:session_id)"),
            params={"session_id": session_id},
        )
    )


def get_session_or_404(
    database_session: Session,
    session_id: int,
) -> AnalysisSession:
    """Die Sitzung oder eine 404-Antwort.

    Aus `routes.py` hierher verschoben. Der einzige Ort in diesem Modul, der
    eine HTTP-Antwort kennt - dafür steht die Prüfung jetzt neben der
    Abfrage, die sie braucht.
    """

    analysis_session = get_session(database_session, session_id)
    if analysis_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return analysis_session


def get_result(
    database_session: Session,
    session_id: int,
) -> Result | None:
    """Das Ergebnis nach dem Vertrag `ergebnis-v6`, oder None."""

    return database_session.get(Result, session_id)


def save_result(
    database_session: Session,
    session_id: int,
    *,
    payload: dict[str, object],
    narrative: str,
) -> Result:
    """Schreibt das Ergebnis und die Erzählung, aus der es entstand.

    Ein vorhandenes Ergebnis wird ersetzt. Die Transaktionsgrenze bleibt
    ausserhalb: `commit` gehört dorthin, wo über den Ausgang der Anfrage
    entschieden wird.
    """

    vorhanden = database_session.get(Result, session_id)
    if vorhanden is not None:
        vorhanden.payload = payload
        vorhanden.narrative = narrative
        return vorhanden
    result = Result(
        session_id=session_id,
        payload=payload,
        narrative=narrative,
    )
    database_session.add(result)
    return result


def get_example_session(
    database_session: Session, example_slug: str
) -> AnalysisSession | None:
    return database_session.scalar(
        select(AnalysisSession).where(AnalysisSession.example_slug == example_slug)
    )


def create_example_session(
    database_session: Session, example_slug: str
) -> AnalysisSession:
    session = AnalysisSession(example_slug=example_slug)
    database_session.add(session)
    database_session.flush()
    return session


def get_partial_result(
    database_session: Session, session_id: int
) -> PartialResult | None:
    return database_session.get(PartialResult, session_id)


def save_partial_result(
    database_session: Session,
    session_id: int,
    *,
    payload: dict[str, object] | None,
    narrative: str,
    rounds: int,
    moving_on: bool,
) -> PartialResult:
    """Legt den Zwischenstand an oder schreibt ihn fort."""

    vorhanden = database_session.get(PartialResult, session_id)
    if vorhanden is None:
        vorhanden = PartialResult(session_id=session_id, narrative=narrative)
        database_session.add(vorhanden)
    vorhanden.payload = payload
    vorhanden.narrative = narrative
    vorhanden.rounds = rounds
    vorhanden.moving_on = moving_on
    return vorhanden
