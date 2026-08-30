"""Die Darstellungsschicht über dem Katalog — Bereiche und Zusammenlauf.

**Was hier geprüft wird und was ausdrücklich nicht.**

Die Bereiche sind kein zweiter Lösungskatalog. Sie sagen nur, wie ein
Betrieb die fünfundzwanzig Familien benennen würde und wo sie auf der
Karte liegen. Deshalb prüfen diese Tests **Abdeckung und Stabilität** —
nicht Fachlichkeit. Ob eine Familie für einen Betrieb taugt, steht im
Katalog und wird dort geprüft.

Der wichtigste Test ist der langweiligste: Jede freigegebene Familie hat
genau einen Bereich. Ohne ihn könnte eine empfohlene Familie auf der
Ergebnisseite schlicht fehlen, und sichtbar wäre davon nichts.
"""

from __future__ import annotations

import pytest

from app import karte, operating_model, solution_catalog
from app.operating_model import ANSICHT_ZU_EXPERIENCE, BEREICHE, BereichsLuecke


def test_every_released_family_has_exactly_one_area() -> None:
    """Fünfundzwanzig Familien, fünfundzwanzig Plätze, keiner doppelt."""

    operating_model.pruefe_vollstaendigkeit()

    zugeordnet = [k for bereich in BEREICHE for k in bereich.familien]
    assert sorted(zugeordnet) == sorted(solution_catalog.freigegebene_kennungen())
    assert len(zugeordnet) == len(set(zugeordnet)) == 25


def test_every_area_lies_in_a_region_of_the_map() -> None:
    """Die Gebiete sind die der Karte — nicht ein zweites Schema daneben."""

    gebiete = {zone.kennung for zone in karte.ZONEN}

    assert {bereich.gebiet for bereich in BEREICHE} <= gebiete


def test_area_keys_and_order_are_unique() -> None:
    """Schlüssel und Reihenfolge sind Adressen — Adressen sind eindeutig."""

    schluessel = [bereich.schluessel for bereich in BEREICHE]
    reihenfolgen = [bereich.reihenfolge for bereich in BEREICHE]

    assert len(schluessel) == len(set(schluessel))
    assert len(reihenfolgen) == len(set(reihenfolgen))


def test_areas_carry_no_professional_judgement() -> None:
    """Diese Schicht sagt nichts darüber, ob etwas passt.

    Stünden Eignung, Fähigkeiten oder Grenzen auch hier, gäbe es zwei
    Wahrheiten, die auseinanderlaufen — und die Frage, welche gilt, hätte
    keine gute Antwort.
    """

    felder = set(BEREICHE[0].__dataclass_fields__)

    assert felder == {
        "schluessel",
        "name",
        "gebiet",
        "familien",
        "experience_affinitaeten",
        "reihenfolge",
    }


def test_areas_are_returned_in_the_order_of_the_working_day() -> None:
    """Erst wie Arbeit hereinkommt, zuletzt was der Betrieb über sich weiss."""

    bereiche = operating_model.bereiche_fuer(["SF-09", "SF-15", "SF-02"])

    assert [b.schluessel for b in bereiche] == [
        "kundenzugang_intake",
        "vorgaenge_aufgaben",
        "steuerung_vorschau",
    ]


def test_several_families_collapse_into_one_area() -> None:
    """Telefon und Anfrageeingang sind zwei Familien und für ihn eine Sache.

    Genau dafür gibt es diese Schicht: Die Karte soll nicht vier Punkte
    zeigen, wo der Betrieb einen Vorgang sieht.
    """

    bereiche = operating_model.bereiche_fuer(["SF-15", "SF-01", "SF-14"])

    assert len(bereiche) == 1
    assert bereiche[0].schluessel == "kundenzugang_intake"
    assert operating_model.familien_im_bereich(
        bereiche[0], ["SF-15", "SF-01", "SF-14"]
    ) == ["SF-15", "SF-01", "SF-14"]


def test_an_unknown_family_has_no_area() -> None:
    """Was es nicht gibt, bekommt auch keinen Platz — still, nicht laut.

    Der laute Fall ist `pruefe_vollstaendigkeit`. Hier geht es um einen
    einzelnen Nachschlag, und der darf keine Ausnahme werfen.
    """

    assert operating_model.bereich_von("SF-99") is None
    assert operating_model.bereiche_fuer(["SF-99"]) == []


def test_a_gap_in_the_table_is_a_hard_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Eine Familie ohne Bereich fällt auf, statt unsichtbar zu werden."""

    verkuerzt = tuple(b for b in BEREICHE if b.schluessel != "wissen_zugaenglich")
    monkeypatch.setattr(operating_model, "BEREICHE", verkuerzt)

    with pytest.raises(BereichsLuecke, match="keinen Bereich"):
        operating_model.pruefe_vollstaendigkeit()


def test_every_view_type_of_today_maps_to_a_target_type() -> None:
    """Gespeicherte Läufe bleiben lesbar.

    Ein Ergebnis von gestern darf nicht unlesbar werden, nur weil die
    Sprache heute anders ist.
    """

    from app.result_schema import REQUIRED_VIEW_FIELDS

    assert set(ANSICHT_ZU_EXPERIENCE) == set(REQUIRED_VIEW_FIELDS)


# --- Wo die Arbeit zusammenläuft -------------------------------------------


def test_a_trade_business_gets_a_shared_state_per_request() -> None:
    """Wer Vorgänge führt, sammelt an Vorgängen."""

    mitte = operating_model.operating_center(["SF-15", "SF-01", "SF-02"])

    assert mitte.art == "shared_work_context"
    assert mitte.bezug == "case"
    assert "kundenzugang_intake" in mitte.bereich_refs


def test_a_knowledge_business_gets_a_knowledge_context() -> None:
    """Nicht jeder Betrieb hat eine Akte.

    Ein Ingenieurbüro sammelt nichts in einem Vorgang — es braucht einen
    verlässlichen Wissenskontext. Ein Modell, das für jeden Betrieb eine
    Akte behauptet, beschreibt den halben Markt falsch.
    """

    mitte = operating_model.operating_center(["SF-11", "SF-05"])

    assert mitte.art == "knowledge_space"
    assert mitte.bezug == "knowledge_space"


def test_a_pure_flow_gets_no_invented_middle() -> None:
    """Wo sich nichts sammelt, wird auch nichts behauptet."""

    mitte = operating_model.operating_center(["SF-13"])

    assert mitte.art == "direct_flow"
    assert mitte.bezug == "none"


def test_without_a_target_there_is_still_an_answer() -> None:
    """Ohne Katalogtreffer bleibt eine Strecke — kein Absturz, keine Erfindung."""

    mitte = operating_model.operating_center([])

    assert mitte.art == "direct_flow"
    assert mitte.bereich_refs == ()


def test_the_same_target_yields_the_same_centre() -> None:
    """Zweimal dasselbe Zielbild, zweimal dieselbe Mitte."""

    erst = operating_model.operating_center(["SF-02", "SF-15", "SF-11"])
    nochmal = operating_model.operating_center(["SF-11", "SF-15", "SF-02"])

    assert erst == nochmal
