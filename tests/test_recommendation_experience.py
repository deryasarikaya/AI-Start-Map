"""Was der Kunde am Ergebnis erlebt — Sprache, Grenzen, Widerspruchsfreiheit.

Alle Faelle bauen auf conftest.spec_payload(); Abweichungen werden als
override uebergeben, damit der Vertrag genau an einer Stelle steht.

Die frueheren Faelle "schuhmacher" und "massagesalon" sind entfallen: SP-04 ist
laut Uebergabe kein Demofall und kein Testanker mehr, und die dort geprueften
Felder gibt es im Ergebnisvertrag nicht mehr.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas import FinalAnalysisResult
from tests.conftest import spec_payload


def _valid(**overrides: object) -> FinalAnalysisResult:
    return FinalAnalysisResult.model_validate(spec_payload(**overrides))


def _rejected(match: str, **overrides: object) -> None:
    with pytest.raises(ValidationError, match=match):
        FinalAnalysisResult.model_validate(spec_payload(**overrides))


# ---------------------------------------------------------------------------
# Genau ein konkretes Ergebnis
# ---------------------------------------------------------------------------


def test_reference_case_produces_one_concrete_customer_result() -> None:
    result = _valid()
    assert result.loesung.ergebnis_art
    assert result.beispiel is not None
    assert result.loesung.was_dabei_rauskommt
    assert "du" in result.bleibt_bei_dir.casefold()


def test_example_shows_the_result_type_the_solution_promises() -> None:
    """Was das Beispiel zeigt, muss dasselbe sein wie ergebnis_art."""

    result = _valid()
    assert result.loesung.ergebnis_art == "Bestellkarte"
    assert result.beispiel is not None
    assert result.beispiel.daraus_wird


def test_today_and_future_flow_must_differ() -> None:
    loesung = dict(spec_payload()["loesung"])  # type: ignore[arg-type]
    loesung["ablauf_kuenftig"] = list(loesung["ablauf_heute"])  # type: ignore[index]
    _rejected("erkennbar unterscheiden", loesung=loesung)


# ---------------------------------------------------------------------------
# Ansprache
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "forbidden",
    (
        "der Nutzer",
        "die Nutzerin",
        "der Unternehmer",
        "der Mitarbeiter",
        "die Person",
        "man sollte",
    ),
)
def test_distant_customer_language_is_rejected(forbidden: str) -> None:
    _rejected(
        "distanzierte Ansprache",
        engpass_text=f"{forbidden} bekommt heute keine vollständige Bestellung.",
    )


def test_real_employee_role_is_allowed_only_when_grounded() -> None:
    """Eine echte Rolle darf vorkommen, wenn sie im Ist-Ablauf belegt ist."""

    result = _valid(
        process_summary="Du nimmst Bestellungen an; der Mitarbeiter bereitet sie vor.",
        as_is_steps=[
            "Du liest die Nachricht im jeweiligen Chat.",
            "Der Mitarbeiter prüft heute Farben und Ausschlüsse.",
            "Du suchst beim Binden noch einmal alles zusammen.",
        ],
        engpass_text="Der Mitarbeiter erhält einzelne Angaben erst später.",
    )
    assert "Der Mitarbeiter" in result.engpass_text


# ---------------------------------------------------------------------------
# Ueberschriften
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "feld", ("engpass_titel",),
)
def test_headings_stay_within_eight_words(feld: str) -> None:
    _rejected("höchstens 8 Wörter", **{feld: " ".join(["Wort"] * 9)})


def test_headings_carry_no_colon_or_question_mark() -> None:
    _rejected("Doppelpunkt", engpass_titel="Dein Engpass: die Suche")
    _rejected("Fragezeichen", engpass_titel="Wo verlierst du Zeit?")


def test_hyphenated_compound_counts_as_one_word() -> None:
    """Shop-Bestellung ist ein Wort, nicht zwei."""

    result = _valid(engpass_titel="Du suchst jede Shop-Bestellung mehrfach zusammen")
    assert "Shop-Bestellung" in result.engpass_titel


# ---------------------------------------------------------------------------
# Moeglichkeiten
# ---------------------------------------------------------------------------


def test_each_rank_appears_at_most_once() -> None:
    _rejected(
        "nur einmal vorkommen",
        moeglichkeiten=[
            {
                "rang": "groesster_hebel",
                "titel": "Ein Eingang für alle Bestellungen",
                "begruendung": "Hier geht heute die meiste Zeit verloren.",
            },
            {
                "rang": "groesster_hebel",
                "titel": "Fehlende Angaben früh erkennen",
                "begruendung": "Rückfragen kosten dich einen zweiten Anlauf.",
            },
        ],
    )


def test_at_most_three_opportunities() -> None:
    with pytest.raises(ValidationError):
        FinalAnalysisResult.model_validate(
            spec_payload(
                moeglichkeiten=[
                    {
                        "rang": rang,
                        "titel": f"Stelle {index}",
                        "begruendung": "Hier geht Zeit verloren.",
                    }
                    for index, rang in enumerate(
                        ("groesster_hebel", "danach", "spaeter", "danach")
                    )
                ]
            )
        )


# ---------------------------------------------------------------------------
# Beispiel — keine Widersprueche
# ---------------------------------------------------------------------------


def test_duplicate_labels_are_rejected() -> None:
    beispiel = dict(spec_payload()["beispiel"])  # type: ignore[arg-type]
    beispiel["daraus_wird"] = [
        {"label": "Bis wann", "wert": "Samstag"},
        {"label": "Bis wann", "wert": "Rosa und Weiß"},
    ]
    _rejected("keine Beschriftung doppelt", beispiel=beispiel)


def test_a_field_cannot_be_filled_and_missing_at_once() -> None:
    beispiel = dict(spec_payload()["beispiel"])  # type: ignore[arg-type]
    beispiel["fehlt"] = ["Bis wann"]
    _rejected("gleichzeitig ausgefüllt", beispiel=beispiel)


def test_missing_detail_must_not_appear_in_the_message() -> None:
    """Der Fehler aus dem Handwerkslauf: Rueckfrage nach dem schon gelieferten Foto."""

    beispiel = dict(spec_payload()["beispiel"])  # type: ignore[arg-type]
    beispiel["fehlt"] = ["Geburtstag"]
    _rejected("steht aber in der Nachricht", beispiel=beispiel)


# ---------------------------------------------------------------------------
# Voraussetzungen und Umsetzung
# ---------------------------------------------------------------------------


def test_a_tool_cannot_stay_and_arrive_at_the_same_time() -> None:
    voraussetzungen = dict(spec_payload()["voraussetzungen"])  # type: ignore[arg-type]
    voraussetzungen["neu_hinzukommend"] = ["WhatsApp"]
    _rejected("gleichzeitig unter", voraussetzungen=voraussetzungen)


def test_first_step_must_not_turn_the_customer_into_the_implementer() -> None:
    umsetzung = dict(spec_payload()["umsetzung"])  # type: ignore[arg-type]
    umsetzung["erster_schritt"] = (
        "Probier es nächste Woche selbst aus und richte den Eingang ein."
    )
    _rejected("zum Umsetzer", umsetzung=umsetzung)
