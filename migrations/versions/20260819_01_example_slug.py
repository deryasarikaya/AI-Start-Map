"""Eine Sitzung kann ein hinterlegter Beispiellauf sein.

Die Spalte traegt den Namen, unter dem der Beispiellauf abrufbar ist. Eine
echte Kundensitzung laesst sie leer. Eindeutig, damit dasselbe Beispiel nicht
zweimal angelegt werden kann.

Revision ID: 20260819_01
Revises: 20260817_02
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260819_01"
down_revision = "20260817_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sessions",
        sa.Column("example_slug", sa.Text(), nullable=True),
    )
    op.create_unique_constraint(
        "uq_sessions_example_slug", "sessions", ["example_slug"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_sessions_example_slug", "sessions", type_="unique")
    op.drop_column("sessions", "example_slug")
