"""Ein gescheiterter Lauf muss sichtbar bleiben.

Solange die Analyse im Request lief, stand der Fehler in der Antwort auf
`POST /analyze` — der Browser wartete ohnehin darauf. Seit sie im Worker
läuft, ist diese Antwort längst weg, wenn etwas schiefgeht. Ohne einen
Vermerk fragt der Warteschirm neunzig Mal nach und zeigt danach eine
Zeitüberschreitung, obwohl der Grund schon lange feststeht.

Die Spalte hängt an der **Sitzung** und nicht am Zwischenstand: Der erste
Modellaufruf kann scheitern, bevor es einen Zwischenstand gibt.

Rückwärts fällt sie ersatzlos weg. Ein Fehlervermerk ist kein Kundeninhalt;
er beschreibt einen Lauf, den es dann nicht mehr gibt.

Revision ID: 20260828_01
Revises: 20260819_03
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260828_01"
down_revision = "20260819_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sessions",
        sa.Column("lauf_fehler", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("sessions", "lauf_fehler")
