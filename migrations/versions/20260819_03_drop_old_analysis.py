"""Die Tabellen des alten Ergebnisvertrags fallen.

Seit Schritt 2 schreibt nichts mehr in `analyses`, und seit die Druckansicht
aus `results` liest, liest auch nichts mehr daraus. Belegt in
der Aufraeumrunde vom 19.08.

Rückwärts werden die Tabellen wieder angelegt, aber nicht gefüllt: Die Daten
sind mit dem Vertrag weg, nicht nur die Struktur.

Revision ID: 20260819_03
Revises: 20260819_02
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260819_03"
down_revision = "20260819_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("automation_opportunities")
    op.drop_table("analyses")


def downgrade() -> None:
    op.create_table(
        "analyses",
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("process_summary", sa.Text(), nullable=False),
        sa.Column("as_is_steps", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("core_bottleneck", sa.Text(), nullable=False),
        sa.Column(
            "uncertainties", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
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
        sa.Column("opportunity_id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("problem", sa.Text(), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("benefit", sa.Text(), nullable=False),
        sa.Column("human_approval", sa.Text(), nullable=False),
        sa.Column("first_step", sa.Text(), nullable=False),
        sa.Column(
            "blueprint_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["analyses.session_id"],
            name="fk_automation_opportunities_session_id_analyses",
            ondelete="CASCADE",
        ),
    )
