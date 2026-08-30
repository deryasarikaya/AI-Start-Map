"""Was der Mensch am Ende vor sich sieht — genau eine Hauptansicht.

**Wogegen das gebaut ist.** Der Ansichtsaufruf wählte frei aus neun
Typen, und eine Übersicht passt immer irgendwie. Das Ergebnis: Ein
Telefonbetrieb und ein Ingenieurbüro bekamen dasselbe Dashboard. Wer zwei
Auswertungen nebeneinander legt, merkt das sofort.

Die Tests halten drei Dinge fest: Der Zieltyp folgt aus dem *Einstieg*,
nicht aus dem Geschmack des Aufrufs. Es gibt genau eine Hauptansicht.
Und eine Ansicht ohne Bezug zu einem Bereich dieses Betriebs zählt nicht
— dieselbe Regel wie für ein Modul ohne Familie.
"""

from __future__ import annotations

from dataclasses import dataclass

from app import experiences
from app.experiences import BEGLEITEND_HOECHSTENS
from app.result_schema import DecisionState


@dataclass
class _Ansicht:
    """So viel von einer Ansicht, wie die Auswahl braucht."""

    typ: str
    titel: str


def _telefonbetrieb() -> DecisionState:
    return DecisionState.model_validate(
        {
            "target_family_ids": ["SF-15", "SF-01", "SF-02"],
            "start_family_ids": ["SF-15", "SF-01"],
        }
    )


def _wissensbetrieb() -> DecisionState:
    return DecisionState.model_validate(
        {
            "target_family_ids": ["SF-11", "SF-05", "SF-02"],
            "start_family_ids": ["SF-11"],
        }
    )


# --- Die Kandidaten --------------------------------------------------------


def test_candidates_come_from_the_start_first() -> None:
    """Was zuerst gebaut wird, bestimmt, was zuerst gezeigt wird."""

    moegliche = experiences.kandidaten(_telefonbetrieb())

    assert moegliche[0].rang == 0
    assert moegliche[0].bereich == "kundenzugang_intake"
    # Genau die Typen der **gewählten** Familien: SF-15 trägt den
    # Sprachassistenten, SF-01 den Posteingang. `guided_intake` gehört zu
    # SF-14 und SF-16 — die stehen nicht in der Auswahl.
    assert [k.typ for k in moegliche if k.rang == 0] == [
        "voice_assistant",
        "ai_inbox",
    ]


def test_the_family_decides_the_type_not_the_area() -> None:
    """Der Kundenzugang trägt Telefon und Posteingang — nur eines davon zählt.

    Hingen die Zieltypen am Bereich, bekäme eine Hausverwaltung ohne
    Telefonfamilie einen Sprachassistenten als Hauptansicht. Gemessen,
    nicht vermutet: Genau das trat auf, solange der Bereich entschied.
    """

    ohne_telefon = DecisionState.model_validate(
        {
            "target_family_ids": ["SF-01", "SF-02"],
            "start_family_ids": ["SF-01", "SF-02"],
        }
    )

    moegliche = experiences.kandidaten(ohne_telefon)

    assert "voice_assistant" not in {k.typ for k in moegliche}
    assert moegliche[0].typ == "ai_inbox"


def test_the_order_of_affinities_is_a_statement() -> None:
    """Beim Kundenzugang kommt der Sprachassistent vor dem Posteingang.

    Sortierte die Auswahl nach Typnamen, gewänne `ai_inbox` alphabetisch
    gegen `voice_assistant` — und ein Telefonbetrieb bekäme einen
    Posteingang als Hauptansicht.
    """

    erlaubt = experiences.erlaubte_ansichtstypen(_telefonbetrieb())

    assert erlaubt[0] == "telefonassistent"


def test_a_type_appears_only_once() -> None:
    """Derselbe Typ zweimal wäre zweimal dasselbe Bild."""

    moegliche = experiences.kandidaten(_telefonbetrieb())

    assert len({k.typ for k in moegliche}) == len(moegliche)


def test_nothing_from_the_later_becomes_a_view() -> None:
    """Eine Ansicht zeigt, was gebaut wird — nicht, was bewusst später kommt.

    Sonst stünde im selben Dokument ein Versprechen und seine Rücknahme.
    """

    zustand = DecisionState.model_validate(
        {
            "target_family_ids": ["SF-15"],
            "start_family_ids": ["SF-15"],
            "future_family_ids": ["SF-11"],
        }
    )

    moegliche = experiences.kandidaten(zustand)

    assert "knowledge_assistant" not in {k.typ for k in moegliche}


def test_without_a_recommendation_there_are_no_candidates() -> None:
    """Ohne Zielbild wird keine Ansicht behauptet."""

    assert experiences.kandidaten(DecisionState()) == []
    assert experiences.auswahl(DecisionState()).primary is None


# --- Die Auswahl -----------------------------------------------------------


def test_exactly_one_primary_experience() -> None:
    """Drei gleichrangige Bilder sind keine Empfehlung, sondern eine Auswahl."""

    gewaehlt = experiences.auswahl(
        _telefonbetrieb(),
        [
            _Ansicht("telefonassistent", "Anruf aufgenommen"),
            _Ansicht("vorgangsakte", "Heizungsausfall bei Frau Müller"),
            _Ansicht("uebersicht", "Heute im Blick"),
        ],
    )

    assert gewaehlt.primary is not None
    assert gewaehlt.primary.typ == "voice_assistant"
    assert len(gewaehlt.supporting) <= BEGLEITEND_HOECHSTENS
    # Die Übersicht fällt heraus: Sie gehört zu SF-09 und SF-12, und
    # keine der beiden steht in der Auswahl dieses Betriebs.
    assert [e.typ for e in gewaehlt.alle] == ["voice_assistant", "case_workspace"]


def test_the_primary_follows_the_start_not_the_order_of_delivery() -> None:
    """Der Aufruf liefert in seiner Reihenfolge — die zählt nicht.

    Hier steht die Übersicht vorn und der Telefonassistent hinten. Der
    Einstieg ist trotzdem das Telefon, also ist es auch die Hauptansicht.
    """

    gewaehlt = experiences.auswahl(
        _telefonbetrieb(),
        [
            _Ansicht("uebersicht", "Heute im Blick"),
            _Ansicht("telefonassistent", "Anruf aufgenommen"),
        ],
    )

    assert gewaehlt.primary.typ == "voice_assistant"


def test_a_different_business_gets_a_different_primary() -> None:
    """Der Kern der Sache: nicht für jeden dasselbe Dashboard."""

    telefon = experiences.auswahl(
        _telefonbetrieb(), [_Ansicht("telefonassistent", "Anruf aufgenommen")]
    )
    wissen = experiences.auswahl(
        _wissensbetrieb(), [_Ansicht("aussenansicht", "Auskunft für Kunden")]
    )

    assert telefon.primary.typ == "voice_assistant"
    assert wissen.primary.typ == "customer_self_service"
    assert telefon.primary.typ != wissen.primary.typ


def test_an_ungrounded_view_does_not_count() -> None:
    """Eine Ansicht ohne Bezug zu einem Bereich dieses Betriebs zählt nicht.

    Dieselbe Regel wie für ein Modul ohne Familie: Was sich nicht
    zurückführen lässt, ist eine Erfindung.
    """

    gewaehlt = experiences.auswahl(
        _telefonbetrieb(),
        [
            _Ansicht("dokumentenablage", "Unterlagen"),
            _Ansicht("telefonassistent", "Anruf aufgenommen"),
        ],
    )

    assert gewaehlt.primary.typ == "voice_assistant"
    assert "document_flow" not in {e.typ for e in gewaehlt.alle}


def test_the_same_type_twice_is_shown_once() -> None:
    """Zwei Ansichten desselben Typs sind zweimal dasselbe Bild."""

    gewaehlt = experiences.auswahl(
        _telefonbetrieb(),
        [
            _Ansicht("vorgangsakte", "Ein Vorgang"),
            _Ansicht("kundenakte", "Ein Kunde"),
        ],
    )

    assert [e.typ for e in gewaehlt.alle] == ["case_workspace"]


def test_at_most_two_supporting_views() -> None:
    """Bis zu zwei daneben — mehr ist keine Hervorhebung mehr."""

    gewaehlt = experiences.auswahl(
        _telefonbetrieb(),
        [
            _Ansicht("telefonassistent", "Anruf"),
            _Ansicht("eingangspruefung", "Neue Anfragen"),
            _Ansicht("vorgangsakte", "Ein Vorgang"),
            _Ansicht("uebersicht", "Heute im Blick"),
        ],
    )

    assert len(gewaehlt.supporting) == BEGLEITEND_HOECHSTENS


def test_a_frame_without_content_is_honest() -> None:
    """Lieferte der Aufruf nichts Passendes, steht der Rahmen leer.

    Das ist ehrlicher, als eine unpassende Ansicht zur Hauptansicht zu
    erklären, nur damit die Seite voll wird.
    """

    gewaehlt = experiences.auswahl(_telefonbetrieb(), [])

    assert gewaehlt.primary is not None
    assert gewaehlt.primary.inhalt_ref is None
    assert gewaehlt.supporting == ()


def test_every_experience_names_its_families() -> None:
    """Jede Ansicht lässt sich auf den Katalog zurückführen."""

    gewaehlt = experiences.auswahl(
        _telefonbetrieb(), [_Ansicht("telefonassistent", "Anruf aufgenommen")]
    )

    assert gewaehlt.primary.familien
    assert set(gewaehlt.primary.familien) <= {"SF-15", "SF-01"}


def test_the_same_decision_yields_the_same_selection() -> None:
    """Zweimal dieselbe Entscheidung, zweimal dieselbe Auswahl."""

    ansichten = [_Ansicht("telefonassistent", "Anruf"), _Ansicht("uebersicht", "Heute")]

    erst = experiences.auswahl(_telefonbetrieb(), ansichten)
    nochmal = experiences.auswahl(_telefonbetrieb(), ansichten)

    assert erst == nochmal


def test_the_allowed_view_types_reach_the_call_in_order() -> None:
    """Was der Aufruf wählen darf, steht fest, bevor er beginnt.

    Ohne diese Liste wählte er frei, die Auswahl verwarf danach das
    Unpassende — bezahlte Arbeit für nichts, und im schlechten Fall eine
    Seite ohne Vorschau.
    """

    erlaubt = experiences.erlaubte_ansichtstypen(_telefonbetrieb())

    assert erlaubt[0] == "telefonassistent"
    assert "dokumentenablage" not in erlaubt
    # Jeder erlaubte Typ lässt sich auf einen Kandidaten zurückführen.
    typen = {k.typ for k in experiences.kandidaten(_telefonbetrieb())}
    from app.operating_model import ANSICHT_ZU_EXPERIENCE

    assert all(ANSICHT_ZU_EXPERIENCE[a] in typen for a in erlaubt)


def test_a_business_without_a_matching_view_gets_no_restriction() -> None:
    """Drei Zieltypen haben heute keine Ansicht — das darf keine leere Seite geben.

    Leer heisst deshalb „keine Einschränkung", nicht „nichts erlaubt".
    """

    nur_ohne_ansicht = DecisionState.model_validate(
        {"target_family_ids": ["SF-04"], "start_family_ids": ["SF-04"]}
    )

    assert experiences.kandidaten(nur_ohne_ansicht)[0].typ == "automation_flow"
    assert experiences.erlaubte_ansichtstypen(nur_ohne_ansicht) == []


# --- Die Durchsetzung im Vertrag -------------------------------------------


def test_a_view_outside_the_scope_is_refused() -> None:
    """Der Aufruf darf nur füllen, was freigegeben ist — hart geprüft.

    Ohne diese Prüfung bliebe die Liste ein Vorschlag. Ein Modell, dem
    eine Übersicht besser gefällt, lieferte weiter eine, die Auswahl
    verwürfe sie danach, und der Betrieb sähe eine Seite ohne Vorschau.
    """

    import pytest
    from pydantic import ValidationError

    from app.result_schema import View, freigegebene_ansichten

    uebersicht = {
        "typ": "uebersicht",
        "titel": "Heute im Blick",
        "beschreibung": "Die offenen Vorgänge auf einen Blick.",
        "module_refs": [],
        "daten": {"zeilen": [{"text": "Ein Vorgang", "status": "rot"}]},
    }
    with freigegebene_ansichten(["telefonassistent", "eingangspruefung"]):
        with pytest.raises(ValidationError, match="gehört nicht zum empfohlenen"):
            View.model_validate(uebersicht)


def test_an_allowed_view_passes_the_scope() -> None:
    """Was freigegeben ist, geht durch — sonst hätte die Prüfung keinen Sinn."""

    from app.result_schema import View, freigegebene_ansichten

    eingang = {
        "typ": "eingangspruefung",
        "titel": "Neue Anfragen",
        "beschreibung": "Was heute hereinkam.",
        "module_refs": [],
        "daten": {
            "nachrichten": [
                {
                    "absender": "Frau Müller",
                    "zeit": "08:14",
                    "text": "Heizung ausgefallen",
                    "marken": ["Störung"],
                }
            ]
        },
    }
    with freigegebene_ansichten(["telefonassistent", "eingangspruefung"]):
        assert View.model_validate(eingang).typ == "eingangspruefung"


def test_without_a_scope_nothing_is_restricted() -> None:
    """Ein gespeichertes Ergebnis darf beim Nachlesen nicht an einer
    Auswahl scheitern, die es zu seiner Zeit nie gab."""

    from app.result_schema import View

    uebersicht = {
        "typ": "uebersicht",
        "titel": "Heute im Blick",
        "beschreibung": "Die offenen Vorgänge auf einen Blick.",
        "module_refs": [],
        "daten": {"zeilen": [{"text": "Ein Vorgang", "status": "rot"}]},
    }

    assert View.model_validate(uebersicht).typ == "uebersicht"
