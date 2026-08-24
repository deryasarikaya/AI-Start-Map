"""Abnahmebedingungen an das Ergebnis.

Neufassung: die frueheren Pruefungen des Feldvertrags sind entfallen, sie
betrafen Felder, die es nicht mehr gibt.

Nicht hier geprueft, weil bereits Schema-Validator (siehe
test_recommendation_experience.py): Rang-Eindeutigkeit, Ueberschneidung von
vorhandene_werkzeuge und neu_hinzukommend, Unterschied zwischen ablauf_heute
und ablauf_kuenftig, Widersprueche im Beispiel, distanzierte Ansprache, der
Kunde als Umsetzer.

Nicht hier pruefbar, weil fallübergreifend: dass sich `ergebnis_art` und die
drei Ueberschriften zwischen Blumenladen, Fotograf und Handwerksbetrieb
unterscheiden. Das zeigt sich erst im Live-Lauf ueber alle drei Faelle.
"""

from __future__ import annotations

import re

import pytest

from app.schemas import (
    CUSTOMER_TEXT_FIELDS,
    FinalAnalysisResult,
    contains_forbidden_customer_term,
)
from tests.conftest import spec_payload


def _result(**overrides: object) -> FinalAnalysisResult:
    return FinalAnalysisResult.model_validate(spec_payload(**overrides))


# ---------------------------------------------------------------------------
# Was ich einrichte — Ich-Form, und der Kunde baut nicht selbst
# ---------------------------------------------------------------------------


def test_setup_steps_are_written_in_first_person() -> None:
    """einrichtungsschritte sind Deryas Arbeit, nicht die des Kunden."""

    schritte = _result().umsetzung.einrichtungsschritte
    assert schritte
    for schritt in schritte:
        assert schritt.startswith("Ich "), schritt


def test_setup_notice_says_nothing_is_built_yet() -> None:
    hinweis = _result().umsetzung.hinweis
    assert hinweis
    assert "Diagnose" in hinweis


# ---------------------------------------------------------------------------
# Voraussetzungen — konkret statt pauschal
# ---------------------------------------------------------------------------


def test_devices_and_access_are_concrete_and_not_a_blanket_promise() -> None:
    """geraete_und_zugang nennt Geraete und sagt, worueber es erreichbar ist."""

    zugang = _result().voraussetzungen.geraete_und_zugang
    assert zugang
    assert any(geraet in zugang for geraet in ("Smartphone", "Handy", "Laptop", "Rechner"))
    # Keine pauschale Zusicherung, dass nie etwas Neues noetig waere.
    for pauschal in ("keine neue App", "keine zusätzliche Software", "nichts Neues"):
        assert pauschal not in zugang


def test_nothing_new_is_a_valid_and_visible_answer() -> None:
    """Eine leere Liste ist ein starkes Ergebnis, kein Mangel."""

    voraussetzungen = dict(spec_payload()["voraussetzungen"])  # type: ignore[arg-type]
    voraussetzungen["neu_hinzukommend"] = []
    result = _result(voraussetzungen=voraussetzungen)
    assert result.voraussetzungen.neu_hinzukommend == []
    assert result.voraussetzungen.vorhandene_werkzeuge


# ---------------------------------------------------------------------------
# Moeglichkeiten — mindestens zwei, kein erfundener dritter
# ---------------------------------------------------------------------------


def test_at_least_two_opportunities_with_different_ranks() -> None:
    moeglichkeiten = _result().moeglichkeiten
    assert len(moeglichkeiten) >= 2
    assert len({item.rang for item in moeglichkeiten}) == len(moeglichkeiten)


def test_two_opportunities_are_enough() -> None:
    """Es wird kein dritter Eintrag erfunden, wenn nur zwei tragen."""

    result = _result()
    assert len(result.moeglichkeiten) == 2


def test_an_invented_rung_is_rejected() -> None:
    loesung = dict(spec_payload()["loesung"])  # type: ignore[arg-type]
    loesung["reifestufe"] = "digitalisierungsoffensive"
    with pytest.raises(Exception):
        _result(loesung=loesung)


def test_the_maturity_level_is_never_a_word_in_the_customer_text() -> None:
    """Die Stufe steuert den Text, sie erscheint nicht darin."""

    kundentext = str(_result().model_dump(include=CUSTOMER_TEXT_FIELDS))
    for stufe in ("regelautomatisierung", "agentisch", "Reifestufe", "Reifeleiter"):
        assert stufe not in kundentext


# ---------------------------------------------------------------------------
# Darstellung — die Form richtet sich nach dem Ergebnis
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("form", ("nachricht", "karte", "liste"))
def test_every_presentation_type_is_allowed(form: str) -> None:
    beispiel = dict(spec_payload()["beispiel"])  # type: ignore[arg-type]
    beispiel["darstellung"] = form
    result = _result(beispiel=beispiel)
    assert result.beispiel is not None
    assert result.beispiel.darstellung == form


def test_an_invented_presentation_type_is_rejected() -> None:
    beispiel = dict(spec_payload()["beispiel"])  # type: ignore[arg-type]
    beispiel["darstellung"] = "tabelle"
    with pytest.raises(Exception):
        _result(beispiel=beispiel)


# ---------------------------------------------------------------------------
# Beispiel — keine Zahl ohne Grundlage
# ---------------------------------------------------------------------------


def test_no_number_appears_that_the_message_does_not_contain() -> None:
    """Jede Zahl im Beispiel muss in der erfundenen Nachricht stehen."""

    beispiel = _result().beispiel
    assert beispiel is not None
    in_nachricht = set(re.findall(r"(?<!\w)\d+(?:[.,]\d+)?", beispiel.nachricht))
    in_feldern = {
        zahl
        for feld in beispiel.daraus_wird
        for zahl in re.findall(r"(?<!\w)\d+(?:[.,]\d+)?", feld.wert)
    }
    assert in_feldern <= in_nachricht


def test_example_shows_what_the_result_type_promises() -> None:
    result = _result()
    assert result.beispiel is not None
    assert result.loesung.ergebnis_art
    assert result.loesung.was_dabei_rauskommt


# ---------------------------------------------------------------------------
# Sprache
# ---------------------------------------------------------------------------


def test_customer_text_uses_direct_address() -> None:
    result = _result()
    ansprache = " ".join(
        [
            result.loesung.was_du_machst,
            result.bleibt_bei_dir,
            result.voraussetzungen.geraete_und_zugang,
        ]
    ).casefold()
    assert re.search(r"\b(?:du|dein|deine|dir)\b", ansprache)


@pytest.mark.parametrize(
    "fachwort",
    (
        "Pflichtfelder",
        "Pflichtfragen",
        "Pflichtangaben",
        "Minimalformular",
        "Inbox",
        "Posteingang",
        "Webhook",
        "Extraktion",
        "Transkription",
        "Prozessregel",
        "Belegerkennung",
        "browser-basierte Ansicht",
        "Rechnungsentwurfs-Layout",
        "konfiguriere",
        "Vorgangsakte",
        "Autonomiestufe",
    ),
)
def test_forbidden_jargon_is_detected(fachwort: str) -> None:
    """Der Wortfilter prueft Wortstaemme, nicht exakte Wortformen."""

    assert contains_forbidden_customer_term(fachwort)


def test_plain_replacements_stay_allowed() -> None:
    """Was den Fachbegriff ersetzt, darf nicht mitgesperrt werden."""

    for erlaubt in (
        "eine Sammelstelle für deine Nachrichten",
        "aus der Sprachnachricht wird Text",
        "eine Seite, auf der alle Bestellungen untereinander stehen",
    ):
        assert not contains_forbidden_customer_term(erlaubt)


def test_the_canonical_contract_carries_no_forbidden_word() -> None:
    result = _result()
    assert not contains_forbidden_customer_term(
        result.model_dump(include=CUSTOMER_TEXT_FIELDS)
    )


# ---------------------------------------------------------------------------
# Was der Wortfilter prueft — und was ausdruecklich nicht
# ---------------------------------------------------------------------------


def test_word_filter_covers_every_customer_field_and_spares_the_rest() -> None:
    """Katalogfelder sind ausgenommen: sie enthalten zwangslaeufig Fachsprache.

    Wurden sie mitgeprueft, loeste jede Analyse eine zweite Erzeugung aus.
    """

    alle = set(FinalAnalysisResult.model_fields)
    assert CUSTOMER_TEXT_FIELDS <= alle
    for intern in ("not_automated", "error_boundaries", "as_is_steps",
                   "process_summary", "uncertainties", "autonomy_level"):
        assert intern not in CUSTOMER_TEXT_FIELDS


def test_catalog_safety_fields_do_not_trigger_the_filter() -> None:
    """Ein Katalogbegriff in not_automated verwirft die Analyse nicht."""

    result = _result(not_automated=["Freigabe-Gate vor der Herausgabe"])
    assert not contains_forbidden_customer_term(
        result.model_dump(include=CUSTOMER_TEXT_FIELDS)
    )
