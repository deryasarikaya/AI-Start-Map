"""Add initial database schema.

Revision ID: 20260717_01
Revises:
Create Date: 2026-07-17
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260717_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("session_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("session_id", name="pk_sessions"),
    )

    op.create_table(
        "interview_questions",
        sa.Column("question_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("question_phase", sa.Text(), nullable=False),
        sa.Column("question_order", sa.Integer(), nullable=False),
        sa.Column("question_key", sa.Text(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.session_id"],
            name="fk_interview_questions_session_id_sessions",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("question_id", name="pk_interview_questions"),
        sa.UniqueConstraint(
            "session_id",
            "question_key",
            name="uq_interview_questions_session_key",
        ),
        sa.UniqueConstraint(
            "session_id",
            "question_phase",
            "question_order",
            name="uq_interview_questions_session_phase_order",
        ),
    )

    op.create_table(
        "process_options",
        sa.Column("process_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("option_order", sa.Integer(), nullable=False),
        sa.Column("process_name", sa.Text(), nullable=False),
        sa.Column("start_event", sa.Text(), nullable=False),
        sa.Column("end_event", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "is_selected",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.session_id"],
            name="fk_process_options_session_id_sessions",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("process_id", name="pk_process_options"),
        sa.UniqueConstraint(
            "session_id",
            "option_order",
            name="uq_process_options_session_order",
        ),
    )
    op.create_index(
        "uq_process_options_selected_session",
        "process_options",
        ["session_id"],
        unique=True,
        postgresql_where=sa.text("is_selected = true"),
    )

    op.create_table(
        "analyses",
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("process_summary", sa.Text(), nullable=False),
        sa.Column("as_is_steps", postgresql.JSONB(), nullable=False),
        sa.Column("core_bottleneck", sa.Text(), nullable=False),
        sa.Column("uncertainties", postgresql.JSONB(), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.session_id"],
            name="fk_analyses_session_id_sessions",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("session_id", name="pk_analyses"),
    )

    op.create_table(
        "automation_opportunities",
        sa.Column("opportunity_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("problem", sa.Text(), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("benefit", sa.Text(), nullable=False),
        sa.Column("human_approval", sa.Text(), nullable=False),
        sa.Column("first_step", sa.Text(), nullable=False),
        sa.Column("blueprint_json", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["analyses.session_id"],
            name="fk_automation_opportunities_session_id_analyses",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "opportunity_id",
            name="pk_automation_opportunities",
        ),
        sa.UniqueConstraint(
            "session_id",
            "rank",
            name="uq_automation_opportunities_session_rank",
        ),
    )


def downgrade() -> None:
    op.drop_table("automation_opportunities")
    op.drop_table("analyses")
    op.drop_index(
        "uq_process_options_selected_session",
        table_name="process_options",
    )
    op.drop_table("process_options")
    op.drop_table("interview_questions")
    op.drop_table("sessions")
