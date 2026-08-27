"""Eine Zahl im Nutzen: nur seine eigene.

Die Regel war lange schlicht — jede Zahl fliegt raus. Das war richtig gegen
ausgedachte Ersparnisse und falsch gegenüber dem Kunden, der seinen Aufwand
selbst beziffert hat. Was hier festgehalten wird, ist die Grenze zwischen
beidem.
"""

from __future__ import annotations

import pytest

from app.result_schema import Module, narrative

ERZAEHLT = (
    "Sie hat in einer normalen Woche ungefähr 70 Minuten nur mit Erinnerungen "
    "verbracht. Und dafür muss nicht jedes Mal jemand 15 Minuten eine E-Mail "
    "schreiben."
)


def _modul(nutzen: str) -> Module:
    return Module(
        name="Automatische Terminerinnerung",
        beschreibung="Erinnert vor dem Termin, ohne dass jemand daran denkt.",
        gruppe="Terminfluss",
        nutzen=nutzen,
    )


@pytest.mark.parametrize(
    "nutzen",
    [
        "70 Minuten pro Woche",
        "15 Minuten je E-Mail",
        "70 Minuten pro Woche weniger",
    ],
)
def test_his_own_figure_survives(nutzen: str) -> None:
    """Was er selbst gesagt hat, darf ihm zurückgegeben werden."""

    with narrative(ERZAEHLT):
        assert _modul(nutzen).nutzen == nutzen


@pytest.mark.parametrize(
    "nutzen",
    [
        "Spart 4 Stunden pro Woche",
        "Spart Stunden",
        "90 Prozent weniger Aufwand",
        "70 Minuten und 3 Stunden",
        "täglich weniger Aufwand",
    ],
)
def test_an_invented_saving_is_dropped(nutzen: str) -> None:
    """Alles, was er nicht gesagt hat, fällt weg — auch wenn es plausibel klingt.

    Besonders die vierte Zeile: Eine echte Angabe schützt nicht die
    erfundene daneben.
    """

    with narrative(ERZAEHLT):
        assert _modul(nutzen).nutzen == ""


def test_without_a_narrative_nothing_is_believed() -> None:
    """Ohne Erzählung im Kontext bleibt es beim Wegwerfen.

    Was sich nicht prüfen lässt, wird nicht geglaubt — sonst wäre die
    Beweispflicht davon abhängig, ob jemand den Kontext gesetzt hat.
    """

    assert _modul("70 Minuten pro Woche").nutzen == ""


def test_a_benefit_without_figures_is_untouched() -> None:
    """Der Normalfall bleibt, wie er war."""

    with narrative(ERZAEHLT):
        assert _modul("Weniger Nachfragen").nutzen == "Weniger Nachfragen"
