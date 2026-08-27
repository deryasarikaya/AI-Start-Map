"""Nicht jede Lösung ist ein Bildschirm.

Acht Ansichtstypen deckten Dashboard, Chat, Kundenakte, Kalender, Portal,
Dokumente, Posteingang und Fallakte ab — alles Oberflächen. Für einen
Betrieb, dessen Engpass das Telefon ist, hiess das: Er sah schon wieder ein
Dashboard, obwohl seine Lösung ein Assistent ist, der ans Telefon geht.

Was hier festgehalten wird, ist die eine Zusage, die diesen Typ trägt: Aus
einem Anruf entsteht ohne Zutun ein fertiger Vorgang.
"""

from __future__ import annotations

import pytest

from app.result_schema import View, narrative
from app.web.responses import automatisiert, templates

ERZAEHLT = (
    "Morgens klingelt bei uns ständig das Telefon. Frau Keller ruft an, weil "
    "die Heizung ausgefallen ist. Wir kommen kaum dazu, alles aufzunehmen."
)


def _anruf(**abweichend: object) -> dict[str, object]:
    daten: dict[str, object] = {
        "name": "Anruf · Frau Keller · 09:12",
        "blasen": [
            {
                "seite": "kunde",
                "text": "Meine Heizung ist heute Nacht ausgefallen.",
                "zeit": "09:12",
            },
            {
                "seite": "betrieb",
                "text": "Verstanden. Um welche Adresse geht es?",
                "zeit": "09:12",
            },
        ],
        "felder": [
            {"label": "Anliegen", "wert": "Heizung ausgefallen"},
            {"label": "Objekt", "wert": "Musterstraße 8"},
        ],
        "statussatz": "Vorgang angelegt — Rückruf vorbereitet",
    }
    daten.update(abweichend)
    return {
        "typ": "telefonassistent",
        "titel": "Eingehender Anruf",
        "beschreibung": "Der Assistent nimmt das Anliegen auf",
        "daten": daten,
        "module_refs": [],
    }


def _gerendert(nutzlast: dict[str, object]) -> str:
    with narrative(ERZAEHLT):
        ansicht = View.model_validate(nutzlast)
    return templates.env.get_template("ansichten.html").module.ansicht(ansicht)


def test_a_call_becomes_a_finished_case() -> None:
    """Anruf, Mitschnitt, Erkanntes, Ergebnis — die ganze Kette.

    Ohne das Ergebnis am Ende wäre es nur ein Gesprächsprotokoll. Der Satz
    darunter ist der Grund, warum der Anruf niemanden mehr aufhält.
    """

    html = _gerendert(_anruf())

    assert "Frau Keller" in html
    assert "Meine Heizung ist heute Nacht ausgefallen." in html
    assert "Daraus erkannt" in html
    assert "Musterstraße 8" in html
    assert "Vorgang angelegt" in html


def test_the_two_sides_are_named_for_a_call() -> None:
    """Am Telefon gibt es keinen „Betrieb", sondern einen Assistenten.

    Der Mitschnitt nutzt dieselben Sprechblasen wie ein Chatverlauf — dort
    heissen die Seiten „Kunde" und „Ihr Betrieb". Bei einem Anruf, den
    niemand annimmt, wäre das falsch.
    """

    html = _gerendert(_anruf())

    assert "Anrufer" in html
    assert "Assistent" in html
    assert "Ihr Betrieb" not in html


def test_a_call_without_a_transcript_is_rejected() -> None:
    """Ohne Mitschnitt hätte das Makro nichts zu zeigen.

    Genau wie jede andere Ansicht ohne ihr Pflichtfeld: Ein leeres Fenster
    ist als Beweis wertlos, und ein erfundenes Gespräch wäre schlimmer.
    """

    with narrative(ERZAEHLT), pytest.raises(ValueError):
        View.model_validate(_anruf(blasen=[]))


def test_the_hint_says_what_this_kind_of_solution_does() -> None:
    """Der Hinweis hängt am Typ, nicht an einem Satz für alle.

    „Vom System vorbereitet" behauptete für den Telefonassistenten dasselbe
    wie für eine Dokumentenablage — und warf beim Kunden mehr Fragen auf,
    als es beantwortete.
    """

    assert automatisiert("telefonassistent") == "Der Assistent nimmt den Anruf auf"
    assert automatisiert("dokumentenablage") != automatisiert("telefonassistent")
    # Ein Typ, den hier jemand vergessen hat, bekommt lieber etwas
    # Unspezifisches als etwas Falsches.
    assert automatisiert("gibtesnicht") == "Automatisch vorbereitet"
