"""Der hinterlegte Beispiellauf.

Eine Rückfallebene für die Vorführung: ein echtes, von Hand geprüftes Ergebnis,
das unter einer eigenen Adresse abrufbar ist und **keinen** Modellaufruf
braucht. Wenn der Modelldienst am Vorführtag hängt, gibt es trotzdem etwas zu
zeigen.

Zwei Dinge, die hier absichtlich so sind:

- **Kein stiller Rückfall.** Scheitert ein echter Lauf, bleibt es beim Fehler.
  Ein Kunde bekäme sonst ein fremdes Ergebnis als sein eigenes gezeigt — genau
  die Schummelei, die der Vertrag überall sonst verhindert. Auf diese Seite
  kommt nur, wer ihre Adresse aufruft.
- **Es liegt in `results`, nicht im Speicher.** Die Seite liest denselben Weg
  wie ein echtes Ergebnis und geht durch dieselbe Vertragsprüfung. Ein Beispiel,
  das an der Prüfung vorbeiginge, wäre als Vorführung wertlos.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app import repository
from app.result_schema import Result, narrative

logger = logging.getLogger(__name__)

# Der Beispiellauf gehoert zum Wissen, nicht zu den Arbeitsunterlagen: Er
# ist die Rueckfallebene fuer eine Vorfuehrung und muss dort liegen, wo die
# Anwendung ihr Wissen sucht.
BEISPIEL_VERZEICHNIS = Path(__file__).resolve().parents[2] / "knowledge/examples"


class ExampleNotFound(LookupError):
    """Unter diesem Namen ist kein Beispiellauf hinterlegt."""


def available_examples() -> list[str]:
    if not BEISPIEL_VERZEICHNIS.is_dir():
        return []
    return sorted(datei.stem for datei in BEISPIEL_VERZEICHNIS.glob("*.json"))


def example_result(database_session: Session, example_slug: str) -> Result:
    """Das hinterlegte Ergebnis, gelesen aus `results`.

    Beim ersten Aufruf wird die Datei aus dem Projekt in die Datenbank
    geschrieben; danach kommt sie von dort. Das Prüfen findet in beiden Fällen
    statt, damit ein Beispiel nicht unbemerkt veraltet, wenn sich der Vertrag
    ändert.
    """

    if example_slug not in available_examples():
        raise ExampleNotFound(example_slug)

    session = repository.get_example_session(database_session, example_slug)
    if session is None or repository.get_result(database_session, session.session_id) is None:
        return _store_the_example(database_session, example_slug, session)

    gespeichert = repository.get_result(database_session, session.session_id)
    with narrative(gespeichert.narrative):
        return Result.model_validate(gespeichert.payload)


def _store_the_example(
    database_session: Session,
    example_slug: str,
    session: object | None,
) -> Result:
    inhalt = json.loads(
        (BEISPIEL_VERZEICHNIS / f"{example_slug}.json").read_text(encoding="utf-8")
    )
    erzaehlung = str(inhalt["erzaehlung"])
    with narrative(erzaehlung):
        geprueft = Result.model_validate(inhalt["ergebnis"])

    if session is None:
        session = repository.create_example_session(database_session, example_slug)
    repository.save_result(
        database_session,
        session.session_id,
        payload=geprueft.model_dump(mode="json"),
        narrative=erzaehlung,
    )
    database_session.commit()
    logger.info(
        "example.stored slug=%s session=%s", example_slug, session.session_id
    )
    return geprueft
