"""Die Tabellen der Datenbank.

Vier Tabellen bilden einen Durchlauf ab:

- `AnalysisSession` — ein Besuch eines Betriebs, alles andere hängt daran
- `InterviewQuestion` — die Erzählung des Kunden, aufgeteilt auf die
  Einstiegsfragen
- `PartialResult` — der halbe Lauf, während der Kunde auf der Seite
  „Das habe ich verstanden" steht
- `Result` — das fertige Ergebnis nach dem Vertrag `ergebnis-v6`

Wer wissen will, was von einem Gespräch übrig bleibt, liest diese Datei.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class AnalysisSession(Base):
    __tablename__ = "sessions"

    session_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    #: Nur gesetzt, wenn diese Sitzung ein hinterlegter Beispiellauf ist.
    #: Eine echte Kundensitzung hat hier None. Der Name ist eindeutig, damit
    #: ein Beispiel nicht zweimal angelegt werden kann.
    example_slug: Mapped[str | None] = mapped_column(
        Text, nullable=True, unique=True, default=None
    )
    #: **Warum der letzte Lauf gescheitert ist** — leer, solange alles gut
    #: ging.
    #:
    #: Solange die Analyse im Request lief, stand der Fehler in der Antwort,
    #: auf die der Browser ohnehin wartete. Seit sie im Worker läuft, ist
    #: diese Antwort längst weg, wenn etwas schiefgeht. Ohne diesen Vermerk
    #: fragt der Warteschirm neunzig Mal nach und meldet danach eine
    #: Zeitüberschreitung, obwohl der Grund seit Sekunden feststeht.
    #:
    #: An der Sitzung und nicht am Zwischenstand, weil der erste
    #: Modellaufruf scheitern kann, bevor es einen Zwischenstand gibt.
    lauf_fehler: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None
    )

    interview_questions: Mapped[list[InterviewQuestion]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    process_options: Mapped[list[ProcessOption]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    partial_result: Mapped[PartialResult | None] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    result: Mapped[Result | None] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "question_key",
            name="uq_interview_questions_session_key",
        ),
        UniqueConstraint(
            "session_id",
            "question_phase",
            "question_order",
            name="uq_interview_questions_session_phase_order",
        ),
    )

    question_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        nullable=False,
    )
    question_phase: Mapped[str] = mapped_column(Text, nullable=False)
    question_order: Mapped[int] = mapped_column(Integer, nullable=False)
    question_key: Mapped[str] = mapped_column(Text, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    answer_text: Mapped[str | None] = mapped_column(Text)

    session: Mapped[AnalysisSession] = relationship(
        back_populates="interview_questions"
    )


class ProcessOption(Base):
    __tablename__ = "process_options"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "option_order",
            name="uq_process_options_session_order",
        ),
        Index(
            "uq_process_options_selected_session",
            "session_id",
            unique=True,
            postgresql_where=text("is_selected = true"),
        ),
    )

    process_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        nullable=False,
    )
    option_order: Mapped[int] = mapped_column(Integer, nullable=False)
    process_name: Mapped[str] = mapped_column(Text, nullable=False)
    start_event: Mapped[str] = mapped_column(Text, nullable=False)
    end_event: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    is_selected: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    session: Mapped[AnalysisSession] = relationship(back_populates="process_options")


class PartialResult(Base):
    """Der halbe Lauf zwischen Erzählung und Ergebnis.

    Der erste Modellaufruf ist fertig, der zweite noch nicht — dazwischen
    steht die Seite „Das habe ich verstanden". Weil der Kunde dort etwas
    ergänzen kann, muss beides den Neuladen überleben: was schon geschrieben
    wurde, und die Erzählung, aus der es entstand.

    `payload` ist leer, wenn der erste Aufruf noch einmal laufen soll — das
    ist der Zustand nach einer Ergänzung.
    """

    __tablename__ = "partial_results"

    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        primary_key=True,
    )
    payload: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    #: Die Erzählung einschliesslich der Ergänzungen des Kunden.
    narrative: Mapped[str] = mapped_column(Text, nullable=False)
    #: Wie oft der erste Aufruf gelaufen ist. Bei zwei ist Schluss.
    rounds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    #: Der Kunde ist weitergegangen; der zweite Aufruf darf laufen.
    moving_on: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )

    session: Mapped[AnalysisSession] = relationship(back_populates="partial_result")


class Result(Base):
    """Das fertige Ergebnis nach dem Vertrag `ergebnis-v6`.

    Das ganze Ergebnis liegt als ein JSONB-Feld, nicht in Spalten. Der Vertrag
    ist verschachtelt und ändert sich noch; jede Änderung wäre sonst eine
    Migration.

    Die Erzählung wird mitgespeichert, weil die Zitatprüfung im Vertrag sie
    braucht: Ohne sie ließe sich ein gespeichertes Ergebnis später nicht erneut
    prüfen.
    """

    __tablename__ = "results"

    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        primary_key=True,
    )
    payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    narrative: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    session: Mapped[AnalysisSession] = relationship(back_populates="result")
