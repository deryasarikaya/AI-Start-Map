from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, Integer, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class AnalysisSession(Base):
    __tablename__ = "sessions"

    session_id: Mapped[int] = mapped_column(Integer, primary_key=True)

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
    analysis: Mapped[Analysis | None] = relationship(
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


class Analysis(Base):
    __tablename__ = "analyses"

    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        primary_key=True,
    )
    process_summary: Mapped[str] = mapped_column(Text, nullable=False)
    as_is_steps: Mapped[list[object] | dict[str, object]] = mapped_column(
        JSONB,
        nullable=False,
    )
    core_bottleneck: Mapped[str] = mapped_column(Text, nullable=False)
    uncertainties: Mapped[list[object] | dict[str, object]] = mapped_column(
        JSONB,
        nullable=False,
    )

    session: Mapped[AnalysisSession] = relationship(back_populates="analysis")
    automation_opportunities: Mapped[list[AutomationOpportunity]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class AutomationOpportunity(Base):
    __tablename__ = "automation_opportunities"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "rank",
            name="uq_automation_opportunities_session_rank",
        ),
    )

    opportunity_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.session_id", ondelete="CASCADE"),
        nullable=False,
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    problem: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    benefit: Mapped[str] = mapped_column(Text, nullable=False)
    human_approval: Mapped[str] = mapped_column(Text, nullable=False)
    first_step: Mapped[str] = mapped_column(Text, nullable=False)
    blueprint_json: Mapped[dict[str, object] | list[object] | None] = mapped_column(JSONB)

    analysis: Mapped[Analysis] = relationship(
        back_populates="automation_opportunities"
    )
