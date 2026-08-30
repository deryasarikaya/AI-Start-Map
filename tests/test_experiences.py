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
    assert {k.typ for k in moegliche if k.rang == 0} == {
        "voice_assistant",
        "guided_intake",
        "ai_inbox",
    }


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
    assert len(gewaehlt.alle) == 3


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
