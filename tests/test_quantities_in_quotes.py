"""Welche Zahl im Zitat gross erscheinen darf.

Auf der Seite steht über jedem Beleg die Menge, die darin vorkommt — „70
oder 80 neue E-Mails" gross, darunter sein Satz, darunter, was das bedeutet.
Das wirkt nur, solange dort wirklich eine Menge steht.

Nicht jede Zahl in einem Satz ist eine: „in zwei Minuten draufgucken" ist
eine Redewendung, „Kurse, die in zwei Tagen stattfinden" ein Zeitpunkt.
Gross gesetzt behaupteten beide, hier sei etwas gemessen worden — und genau
dieses Vortäuschen einer Messung ist das, was diese Auswertung von den
Punkteständen der Konkurrenz unterscheiden soll.
"""

from __future__ import annotations

import pytest

from app.web.responses import zahl_im_satz


@pytest.mark.parametrize(
    ("satz", "zahl", "wort"),
    [
        (
            "Wenn morgens jemand sein Outlook öffnet, sind da teilweise "
            "70 oder 80 neue E-Mails.",
            "70 oder 80",
            "neue E-Mails",
        ),
        (
            "Sie hat in einer normalen Woche ungefähr 70 Minuten nur mit "
            "Erinnerungen verbracht.",
            "70",
            "Minuten",
        ),
        (
            "Wir verwalten ungefähr 450 Einheiten, hauptsächlich Wohnungen.",
            "450",
            "Einheiten",
        ),
        (
            "Wir sind insgesamt fünf Leute, also ich und drei Mitarbeiter.",
            "fünf",
            "Leute",
        ),
    ],
)
def test_a_real_quantity_is_lifted_out(satz: str, zahl: str, wort: str) -> None:
    """Zahl und Bezeichnung kommen wörtlich aus seinem Satz."""

    treffer = zahl_im_satz(satz)

    assert treffer == {"zahl": zahl, "wort": wort}
    assert zahl in satz
    assert wort in satz


@pytest.mark.parametrize(
    "satz",
    [
        # Ein Zeitpunkt, keine Menge.
        "Sie schaut, welche Kurse in zwei Tagen stattfinden.",
        "Aber nicht so, dass ich in zwei Minuten drauf gucke.",
        # Gar keine Zahl.
        "Und genau diese Kette macht mich wahnsinnig.",
        "Ich habe da Spalten mit Kunde, Thema und wer dran ist.",
        # „eine" ist ein Artikel, keine Menge.
        "Ich führe eine Liste, damit nichts untergeht.",
    ],
)
def test_what_is_not_a_quantity_stays_out(satz: str) -> None:
    """Kommt nichts zurück, steht auf der Karte einfach keine Zahl.

    Der Beleg bleibt vollständig stehen — er verliert nur die grosse
    Überschrift, die er nie verdient hatte.
    """

    assert zahl_im_satz(satz) is None


def test_a_verb_is_never_what_gets_counted() -> None:
    """Gezählt wird ein Substantiv, und im Deutschen erkennt man das.

    Ohne diese Regel entstand „zwei Minuten draufgucke" — grammatisch
    hilflos und inhaltlich falsch.
    """

    assert zahl_im_satz("Das dauert zwei Minuten zusammensuchen.") == {
        "zahl": "zwei",
        "wort": "Minuten",
    }
