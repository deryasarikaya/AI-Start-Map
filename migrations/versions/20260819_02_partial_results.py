"""Der halbe Lauf zwischen Erzählung und Ergebnis.

Der erste Modellaufruf ist fertig, der zweite noch nicht — dazwischen steht
die Seite „Das habe ich verstanden". Weil der Kunde dort ergänzen kann, muss
der Zwischenstand einen Neuladen überleben.

Revision ID: 20260819_02
Revises: 20260819_01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260819_02"
down_revision = "20260819_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "partial_results",
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("narrative", sa.Text(), nullable=False),
        sa.Column("rounds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "moving_on", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.session_id"],
            name="fk_partial_results_session_id_sessions",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("session_id", name="pk_partial_results"),
    )


def downgrade() -> None:
    op.drop_table("partial_results")
