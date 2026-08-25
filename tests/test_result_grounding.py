"""Das Geländer reicht bis zur Ergebnisseite.

Kein Modellaufruf. Geprüft wird, dass die späteren Aufrufe nichts hinzufügen
können: Jede Ansicht, jedes System, jede Architekturebene und jeder
Umsetzungsschritt muss sich auf ein bereits geprüftes Modul berufen.

Das ist Herkunftskontrolle, kein Textverständnis. Formuliert wird frei — nur
die zugrunde liegende Funktion muss schon freigegeben sein.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.result_schema import (
    ResultPartOne,
    ResultPartTwoRest,
    ResultPartTwoViews,
    freigegebene_module,
    narrative,
)
from tests.test_result_contract import ERZAEHLUNG, _kontext, _part_two

MODULE = ("Sammelstelle", "Vorgangsakte")


def _ansichten(**overrides: object) -> dict:
    daten = _part_two()
    return {"ansichten": overrides.get("ansichten", daten["ansichten"])}


def _rest(**overrides: object) -> dict:
    daten = {k: v for k, v in _part_two().items() if k != "ansichten"}
    daten.update(overrides)
    return daten


# --- Der Regelfall --------------------------------------------------------


def test_parts_that_name_a_module_pass() -> None:
    """Wer sich auf ein freigegebenes Modul beruft, kommt durch."""

    with narrative(ERZAEHLUNG), freigegebene_module(MODULE):
        ansichten = ResultPartTwoViews.model_validate(_ansichten())
        rest = ResultPartTwoRest.model_validate(_rest())

    assert all(ansicht.module_refs for ansicht in ansichten.ansichten)
    assert all(system.module_refs for system in rest.systeme)
    assert all(ebene.module_refs for ebene in rest.architektur)
    assert all(schritt.module_refs for schritt in rest.umsetzung)


def test_the_wording_stays_free() -> None:
    """Der Titel darf klingen wie der Betrieb — die Herkunft bleibt gebunden."""

    daten = _ansichten()
    daten["ansichten"][0]["titel"] = "Ihr Morgenblick auf offene Fälle"

    with narrative(ERZAEHLUNG), freigegebene_module(MODULE):
        ansichten = ResultPartTwoViews.model_validate(daten)

    assert ansichten.ansichten[0].titel == "Ihr Morgenblick auf offene Fälle"
    assert ansichten.ansichten[0].module_refs == ["Sammelstelle"]


# --- Was nicht durchkommt -------------------------------------------------


def test_a_view_for_an_unknown_module_is_rejected() -> None:
    """Eine Ansicht zu einem Modul, das niemand freigegeben hat.

    So entstünde eine Funktion nachträglich: erst gibt es die Ansicht, dann
    glaubt der Kunde, es gäbe die Sache dahinter.
    """

    daten = _ansichten()
    daten["ansichten"][0]["module_refs"] = ["Autonomer Einkaufsagent"]

    with pytest.raises(ValidationError, match="kein Modul dieser Lösung"):
        with narrative(ERZAEHLUNG), freigegebene_module(MODULE):
            ResultPartTwoViews.model_validate(daten)


def test_a_view_without_any_module_is_rejected() -> None:
    """Kein Bezug ist auch ein Bezug — nämlich keiner."""

    daten = _ansichten()
    daten["ansichten"][0]["module_refs"] = []

    with pytest.raises(ValidationError, match="nennt kein Modul"):
        with narrative(ERZAEHLUNG), freigegebene_module(MODULE):
            ResultPartTwoViews.model_validate(daten)


def test_an_invented_system_is_rejected() -> None:
    """Ein System, das zu keinem Modul gehört, gehört nicht ins Ergebnis."""

    daten = _rest()
    daten["systeme"][0]["module_refs"] = ["Ein Modul, das es nicht gibt"]

    with pytest.raises(ValidationError, match="kein Modul dieser Lösung"):
        with narrative(ERZAEHLUNG), freigegebene_module(MODULE):
            ResultPartTwoRest.model_validate(daten)


def test_an_invented_implementation_step_is_rejected() -> None:
    """Ein Schritt, der etwas einführt, das niemand ausgewählt hat."""

    daten = _rest()
    daten["umsetzung"][0] = {
        "text": "Einen autonomen Einkaufsagenten anbinden",
        "module_refs": ["Autonomer Einkaufsagent"],
    }

    with pytest.raises(ValidationError, match="kein Modul dieser Lösung"):
        with narrative(ERZAEHLUNG), freigegebene_module(MODULE):
            ResultPartTwoRest.model_validate(daten)


def test_an_architecture_layer_needs_a_module() -> None:
    """Auch eine Ebene ist eine Zusage — sie braucht ihren Ursprung."""

    daten = _rest()
    daten["architektur"][0]["module_refs"] = []

    with pytest.raises(ValidationError, match="nennt kein Modul"):
        with narrative(ERZAEHLUNG), freigegebene_module(MODULE):
            ResultPartTwoRest.model_validate(daten)


# --- Ohne Rahmen wird nicht geprüft ---------------------------------------


def test_a_stored_result_stays_readable() -> None:
    """Ein gespeichertes Ergebnis wird gelesen, nicht neu verhandelt.

    Der hinterlegte Beispiellauf kennt keine Herkunft. Ihm nachträglich eine
    anzudichten hiesse, einen geprüften Durchlauf zu fälschen.
    """

    daten = _rest()
    for system in daten["systeme"]:
        system.pop("module_refs", None)
    daten["umsetzung"] = ["Sammelstelle einrichten", "Eingangswege umleiten"]

    rest = ResultPartTwoRest.model_validate(daten, context=_kontext())

    assert rest.systeme[0].module_refs == []
    assert rest.umsetzung[0].text == "Sammelstelle einrichten"


# --- SF-25: keine erfundenen Beträge --------------------------------------


def test_money_in_the_result_is_rejected_when_the_forecast_is_chosen() -> None:
    """**Der SF-25-Schutz.**

    Die Familie sagt zu, Deckungsbeitrag und Liquidität später aus den Daten
    des Betriebs zu rechnen. Ein Betrag im Ergebnistext wäre keine Rechnung,
    sondern eine Behauptung.
    """

    # Im Systemabschnitt: Die ältere Regel gegen Ersparnisversprechen prüft
    # den Wertabschnitt, dieser Schutz prüft das ganze Ergebnis.
    daten = _rest()
    daten["systeme"][0]["umgang"] = "Zeigt den Deckungsbeitrag von 1.240 €"

    with pytest.raises(ValidationError, match="Geldbetrag"):
        with narrative(ERZAEHLUNG), freigegebene_module(MODULE, ["SF-25"]):
            ResultPartTwoRest.model_validate(daten)


def test_a_view_may_not_show_invented_amounts_for_the_forecast() -> None:
    """Auch in einer Beispielansicht steht kein Eurobetrag."""

    daten = _ansichten()
    daten["ansichten"][0]["daten"]["kennzahlen"] = [
        {"label": "Deckungsbeitrag", "wert": "1.240 EUR"}
    ]

    with pytest.raises(ValidationError, match="Geldbetrag"):
        with narrative(ERZAEHLUNG), freigegebene_module(MODULE, ["SF-25"]):
            ResultPartTwoViews.model_validate(daten)


def test_describing_the_calculation_stays_allowed() -> None:
    """Was die Lösung tun wird, darf dastehen — nur die Zahl nicht."""

    daten = _rest()
    daten["systeme"][0]["umgang"] = (
        "Liefert Deckungsbeitrag und Auslastung aus den erfassten Aufträgen"
    )

    with narrative(ERZAEHLUNG), freigegebene_module(MODULE, ["SF-25"]):
        rest = ResultPartTwoRest.model_validate(daten)

    assert rest.systeme[0].umgang


def test_without_the_forecast_family_amounts_are_not_this_check() -> None:
    """Der Schutz hängt an SF-25, nicht an jedem Ergebnis.

    Für andere Familien gilt weiterhin die ältere Regel gegen Zeit- und
    Geldersparnis; sie prüft etwas anderes und bleibt unberührt.
    """

    daten = _rest()
    daten["systeme"][0]["umgang"] = "Rechnungen über 500 € werden vorgelegt"

    with narrative(ERZAEHLUNG), freigegebene_module(MODULE, ["SF-01"]):
        rest = ResultPartTwoRest.model_validate(daten)

    assert rest.systeme[0].umgang


# --- Der gekuerzte Modulname ----------------------------------------------
#
# Aus einem echten Lauf: Das Modul heisst "Morgenliste mit
# Verantwortlichkeiten", die Ansicht berief sich auf "Morgenliste". Der
# exakte Zeichenvergleich hat daran den ganzen Durchlauf zerrissen -- an
# einer Schreibweise, nicht an einer erfundenen Funktion.

LANGE_MODULE = ("Morgenliste mit Verantwortlichkeiten", "Terminsync")


def test_a_shortened_module_name_still_points_at_its_module() -> None:
    """Ein gekuerzter Name bezeichnet dasselbe Modul."""

    daten = _ansichten()
    for ansicht in daten["ansichten"]:
        ansicht["module_refs"] = ["Terminsync"]
    daten["ansichten"][0]["module_refs"] = ["Morgenliste"]

    with narrative(ERZAEHLUNG), freigegebene_module(LANGE_MODULE):
        ansichten = ResultPartTwoViews.model_validate(daten)

    # Gespeichert wird der volle Name, nicht die Abkuerzung.
    assert ansichten.ansichten[0].module_refs == [
        "Morgenliste mit Verantwortlichkeiten"
    ]


def test_a_longer_wording_of_the_same_module_is_accepted() -> None:
    """Auch andersherum: Der Bezug darf den Modulnamen enthalten."""

    daten = _ansichten()
    for ansicht in daten["ansichten"]:
        ansicht["module_refs"] = ["Terminsync"]
    daten["ansichten"][0]["module_refs"] = ["Terminsync fuer Termine"]

    with narrative(ERZAEHLUNG), freigegebene_module(LANGE_MODULE):
        ansichten = ResultPartTwoViews.model_validate(daten)

    assert ansichten.ansichten[0].module_refs == ["Terminsync"]


def test_an_invented_module_is_still_rejected_under_the_looser_match() -> None:
    """**Die Lockerung darf kein Schlupfloch sein.**

    Ein erfundenes Modul enthaelt keinen freigegebenen Namen und ist in
    keinem enthalten -- es faellt weiterhin durch.
    """

    daten = _ansichten()
    daten["ansichten"][0]["module_refs"] = ["Autonomer Einkaufsagent"]

    with pytest.raises(ValidationError, match="kein Modul dieser"):
        with narrative(ERZAEHLUNG), freigegebene_module(LANGE_MODULE):
            ResultPartTwoViews.model_validate(daten)


def test_an_ambiguous_short_name_is_rejected() -> None:
    """Passt der Bezug auf zwei Module, war er keine Abkuerzung, sondern unklar.

    Unklarheit gilt hier als Fehler: Ein Ergebnis, das nicht sagt, welches
    Modul es meint, laesst sich nicht pruefen.
    """

    daten = _ansichten()
    daten["ansichten"][0]["module_refs"] = ["Liste"]

    with pytest.raises(ValidationError, match="kein Modul dieser"):
        with narrative(ERZAEHLUNG), freigegebene_module(
            ("Liste der Termine", "Liste der Aufgaben")
        ):
            ResultPartTwoViews.model_validate(daten)


# --- Die Nummer statt des Namens ------------------------------------------
#
# Aus dem dritten echten Lauf: Das Modell schrieb die langen Modulnamen nicht
# ab, es benannte sie um -- "Faelligkeitslogik" fuer "Regel fuer faellige
# Kurskontakte". Kein Zeichenvergleich rettet das. Deshalb tragen die
# Bezuege jetzt Nummern, so wie die Katalogauswahl Kennungen traegt.


def test_a_module_number_points_at_that_module() -> None:
    """Die Nummer aus MODULE_DIESER_LOESUNG bezeichnet das Modul."""

    daten = _ansichten()
    for ansicht in daten["ansichten"]:
        ansicht["module_refs"] = ["1"]
    daten["ansichten"][0]["module_refs"] = ["2"]

    with narrative(ERZAEHLUNG), freigegebene_module(MODULE):
        ansichten = ResultPartTwoViews.model_validate(daten)

    # Gespeichert wird der Name, nicht die Nummer.
    assert ansichten.ansichten[0].module_refs == ["Vorgangsakte"]
    assert ansichten.ansichten[1].module_refs == ["Sammelstelle"]


def test_a_number_outside_the_list_is_rejected() -> None:
    """Eine Nummer, die es nicht gibt, ist ein erfundenes Modul."""

    daten = _ansichten()
    daten["ansichten"][0]["module_refs"] = ["9"]

    with pytest.raises(ValidationError, match="kein Modul dieser"):
        with narrative(ERZAEHLUNG), freigegebene_module(MODULE):
            ResultPartTwoViews.model_validate(daten)


def test_zero_is_not_a_module() -> None:
    """Gezaehlt wird ab eins. Null ist keine Stelle in der Liste."""

    daten = _ansichten()
    daten["ansichten"][0]["module_refs"] = ["0"]

    with pytest.raises(ValidationError, match="kein Modul dieser"):
        with narrative(ERZAEHLUNG), freigegebene_module(MODULE):
            ResultPartTwoViews.model_validate(daten)


def test_the_payload_of_the_later_calls_numbers_the_modules() -> None:
    """Die Nummern stehen im Aufruf, nicht nur im Vertrag.

    Ohne diese Liste haette das Modell nichts, worauf es sich beziehen kann.
    """

    from app import openai_service
    from tests.test_result_contract import _part_one

    with narrative(ERZAEHLUNG):
        oben = ResultPartOne.model_validate(_part_one())

    payload = openai_service._part_two_payload(
        ERZAEHLUNG, oben, [], None, None
    )

    module = payload["MODULE_DIESER_LOESUNG"]
    assert [eintrag["nr"] for eintrag in module] == list(
        range(1, len(oben.module) + 1)
    )
    assert [eintrag["name"] for eintrag in module] == [
        modul.name for modul in oben.module
    ]
