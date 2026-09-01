"""Ein Vertrag für Web und PDF — und ein Weg zurück für alte Läufe.

**Wogegen das gebaut ist.** Die Vorlagen hingen direkt am gespeicherten
Ergebnis und mussten sich daraus selbst zusammensuchen, was der Einstieg
ist und welche Grenze vom Kunden stammt. Das sind fachliche
Entscheidungen, und zwei Vorlagen treffen sie verschieden.

Der heikelste Teil ist die Herkunft der Grenzen: „Sie wollen keine
Preiszusagen" ist eine Aussage über diesen Kunden, „Preise bleiben beim
Menschen" eine Eigenschaft unseres Katalogs. Beides als seine Entscheidung
auszugeben, legt ihm Sätze in den Mund, die er nie gesagt hat.
"""

from __future__ import annotations

from app import decision_state, results_dto
from app.result_schema import Result

from tests.test_decision_state import (
    _absage,
    _gepruefte_auswahl,
    _gepruefte_diagnose,
)
from tests.test_result_contract import _division, _kontext, _part_one, _part_two


def _ergebnis(entscheidung: dict[str, object] | None = None, **overrides: object):
    daten: dict[str, object] = {**_part_one(), **_part_two()}
    daten.update(overrides)
    if entscheidung is not None:
        daten["entscheidung"] = entscheidung
    return Result.model_validate(daten, context=_kontext())


#: Was der Kunde in der Erzählung von test_result_contract ausgeschlossen
#: hat. Der Vertrag lässt eine selbst genannte Grenze nur zu, wenn dort
#: wirklich ein Ausschluss steht — hier steht er.
SELBST_GENANNT = {
    "titel": "Die Buchhaltung bleibt",
    "erlaeuterung": "Eine Buchhaltungssoftware soll nicht ersetzt werden.",
}


def _lauf_mit_entscheidung(ergebnis_felder: dict | None = None, **auswahl: object):
    """Ein Ergebnis mit allem, was der neue Vertrag hergibt.

    Ausbaupfad und Grenzen stehen **im Ergebnis**, nicht in der Auswahl:
    Der Vertrag liest den Ausblick dort, wo `nutzen` und `name` stehen,
    und die selbst genannten Grenzen dort, wo die Zitatprüfung sie
    zugelassen hat.
    """

    diagnose = _gepruefte_diagnose()
    gewaehlt = _gepruefte_auswahl(diagnose, **auswahl)
    zustand = decision_state.aus_lauf(diagnose, gewaehlt)
    felder: dict[str, object] = {
        "aufgabenteilung": _division(grenzen=[SELBST_GENANNT]),
    }
    felder.update(ergebnis_felder or {})
    return _ergebnis(zustand.model_dump(mode="json"), **felder)


# --- Der neue Weg ----------------------------------------------------------


def test_a_run_with_a_decision_carries_everything() -> None:
    """Ein vollständiger Lauf ergibt einen vollständigen Vertrag."""

    dto = results_dto.von_ergebnis(_lauf_mit_entscheidung(why_not=[_absage()]))

    assert dto.contract_version == results_dto.VERTRAG
    assert dto.herkunft == results_dto.VERTRAG
    assert not dto.ist_angepasst
    assert dto.uebersicht.engpass
    assert dto.karte.knoten
    assert len(dto.nicht_empfohlen) == 1


def test_the_evidence_of_the_start_reaches_the_first_screen() -> None:
    """Der Beleg neben der Empfehlung ist ihr Grund, nicht ein hübsches Zitat.

    Er kommt aus dem Signal, das zum Einstieg wurde — nicht aus der
    Reihenfolge irgendeiner Liste.
    """

    dto = results_dto.von_ergebnis(_lauf_mit_entscheidung())

    # S1 wurde `start` und beruft sich auf B1.
    assert dto.uebersicht.beleg_refs == ("B1",)
    assert {b.id for b in dto.belege} == {"B1", "B2"}


def test_today_context_items_expose_deterministic_semantic_types() -> None:
    """Today-Karten übernehmen die geprüfte Signalart ohne Textheuristik."""

    dto = results_dto.von_ergebnis(_lauf_mit_entscheidung())

    assert [anker.type for anker in dto.anker] == [
        "current_friction",
        "existing_foundation",
        "solution_requirement",
    ]
    assert [anker.type_label for anker in dto.anker] == [
        "Heutige Reibung",
        "Bestehende Grundlage",
        "Anforderung an die Lösung",
    ]


def test_the_start_of_the_overview_is_the_start_of_the_map() -> None:
    """Beide lesen dieselbe Entscheidung — sonst wäre nichts gewonnen."""

    dto = results_dto.von_ergebnis(_lauf_mit_entscheidung())

    assert dto.uebersicht.einstieg_refs == dto.karte.start


def test_boundaries_keep_their_origin_apart() -> None:
    """Was er gesagt hat und was unser Katalog ohnehin nicht übernimmt.

    Der Unterschied verschwindet leicht und ist genau der, der zählt:
    Eine Katalogeigenschaft als seine Entscheidung auszugeben, legt ihm
    Sätze in den Mund.
    """

    dto = results_dto.von_ergebnis(_lauf_mit_entscheidung())

    herkuenfte = {g.herkunft for g in dto.grenzen}
    assert "kunde" in herkuenfte
    for grenze in dto.grenzen:
        if grenze.herkunft == "katalog":
            assert grenze.familie in dto.entscheidung.target_family_ids
        else:
            assert grenze.familie is None


def test_the_outlook_never_repeats_what_is_being_built() -> None:
    """Die erste Ausbaustufe ist die Grundlage, die gerade empfohlen wurde."""

    familien = _lauf_mit_entscheidung().entscheidung.target_family_ids
    pfad = [
        {
            "stufe": "jetzt",
            "name": "Anfragen gemeinsam führen",
            "nutzen": "Sie sammeln Anfragen nicht mehr von Hand ein.",
            "bausteine": ["Ein Eingang"],
            "solution_family_ids": [familien[0]],
        },
        {
            "stufe": "danach",
            "name": "Kunden selbst informieren",
            "nutzen": "Sie beantworten Standfragen nicht mehr selbst.",
            "bausteine": ["Stand ansehen"],
            "solution_family_ids": ["SF-10"],
        },
    ]
    dto = results_dto.von_ergebnis(
        _lauf_mit_entscheidung({"ausbaupfad": pfad}, ausbaupfad=pfad)
    )

    assert len(dto.ausblicke) == 1
    assert dto.ausblicke[0].familien == ("SF-10",)
    assert dto.ausblicke[0].outcome


def test_open_questions_stay_in_the_contract() -> None:
    """Ein erkannter, nicht entscheidbarer Punkt verschwindet nicht."""

    dto = results_dto.von_ergebnis(_lauf_mit_entscheidung())

    # S3 wurde vom Server als `open` nachgetragen und steht als Frage da.
    assert dto.offene_fragen
    assert any("Buchhaltung" in frage for frage in dto.offene_fragen)


def test_exactly_one_primary_view_reaches_the_contract() -> None:
    """Der Vertrag reicht keine drei gleichrangigen Bilder weiter."""

    dto = results_dto.von_ergebnis(_lauf_mit_entscheidung())

    assert len(dto.ansichten.alle) <= 3
    if dto.ansichten.primary is not None:
        assert dto.uebersicht.primary_experience == dto.ansichten.primary.typ


def test_the_same_run_yields_the_same_contract() -> None:
    """Zweimal derselbe Lauf, zweimal derselbe Vertrag."""

    lauf = _lauf_mit_entscheidung()

    assert results_dto.von_ergebnis(lauf) == results_dto.von_ergebnis(lauf)


# --- Der Weg zurück --------------------------------------------------------


def test_a_run_from_before_the_contract_is_adapted_not_dropped() -> None:
    """Ein alter Lauf bleibt darstellbar — und sagt, dass er angepasst ist."""

    dto = results_dto.von_ergebnis(_ergebnis())

    assert dto.ist_angepasst
    assert dto.herkunft == "ergebnis-v6-adaptiert"
    assert dto.uebersicht.engpass
    # Die Landschaft steht auch für ihn.
    assert len(dto.karte.knoten) == 14


def test_an_adapted_run_invents_nothing() -> None:
    """Was der alte Lauf nicht enthält, steht auch im Vertrag nicht.

    Ihm eine Entscheidung anzudichten hiesse, einen geprüften Durchlauf
    zu fälschen.
    """

    dto = results_dto.von_ergebnis(_ergebnis())

    assert dto.entscheidung.signals == []
    assert dto.belege == ()
    assert dto.nicht_empfohlen == ()
    assert dto.offene_fragen == ()
    assert dto.uebersicht.beleg_refs == ()


def test_an_adapted_run_reads_the_families_it_does_have() -> None:
    """Stehen Familien an den Modulen, werden sie gelesen — mehr nicht."""

    module = [
        {
            "gruppe": "Eingang",
            "name": "Ein gemeinsamer Anfrageeingang",
            "beschreibung": "Alle Wege laufen an einer Stelle zusammen.",
            "stufe": "jetzt",
            "solution_family_ids": ["SF-01"],
            "baustein_refs": [],
        },
        {
            "gruppe": "Überblick",
            "name": "Gemeinsamer Vorgangsstand",
            "beschreibung": "Jeder sieht, wo eine Meldung steht.",
            "stufe": "danach",
            "solution_family_ids": ["SF-02"],
            "baustein_refs": [],
        },
    ]
    dto = results_dto.von_ergebnis(_ergebnis(module=module))

    assert dto.entscheidung.target_family_ids == ["SF-01", "SF-02"]
    # Nur das Modul auf Stufe `jetzt` ist der Einstieg.
    assert dto.entscheidung.start_family_ids == ["SF-01"]
    assert dto.karte.start == ("kundenzugang_intake",)


def test_an_adapted_run_without_families_shows_a_quiet_map() -> None:
    """Der hinterlegte Beispiellauf kennt die Kennungen nicht — das ist in Ordnung."""

    dto = results_dto.von_ergebnis(_ergebnis())

    assert dto.entscheidung.target_family_ids == []
    assert dto.karte.start == ()
    assert all(k.zustand == "still" for k in dto.karte.knoten)
    assert dto.ansichten.primary is None


def test_the_outlook_says_whether_it_is_inside_the_target() -> None:
    """Der Ausbaupfad mischt zwei Dinge — der Vertrag trennt sie.

    Ein Bereich, der zum Zielbild gehört und nur nicht zuerst kommt, ist
    etwas anderes als einer, der darüber hinausgeht. Auf der Karte sind
    das zwei Zustände. Ohne dieses Feld nennte die Karte einen Bereich
    „später" und die Ausblicksliste vier — und Web und PDF zeigten wieder
    Verschiedenes.
    """

    familien = _lauf_mit_entscheidung().entscheidung.target_family_ids
    pfad = [
        {
            "stufe": "danach",
            "name": "Vorgänge überblicken",
            "nutzen": "Sie suchen den Stand nicht mehr zusammen.",
            "bausteine": ["Ein Stand"],
            "solution_family_ids": [familien[1]],
        },
        {
            "stufe": "spaeter",
            "name": "Kunden selbst informieren",
            "nutzen": "Sie beantworten Standfragen nicht mehr selbst.",
            "bausteine": ["Stand ansehen"],
            "solution_family_ids": ["SF-10"],
        },
    ]
    dto = results_dto.von_ergebnis(
        _lauf_mit_entscheidung({"ausbaupfad": pfad}, ausbaupfad=pfad)
    )

    nach_phase = {a.phase: a for a in dto.ausblicke}
    assert set(nach_phase) == {"target", "future"}
    assert nach_phase["target"].familien == (familien[1],)
    assert nach_phase["future"].familien == ("SF-10",)
    # Und was die Karte „später" nennt, ist genau die future-Zeile.
    assert nach_phase["future"].bereich in dto.karte.future


def test_the_outlook_and_the_map_never_disagree() -> None:
    """Was der Ausblick „später" nennt, nennt die Karte auch so.

    Eine Familie ausserhalb des Zielbilds kann in einem Bereich liegen,
    der bereits leuchtet. An einem echten Lauf trat genau das ein: Der
    Ausblick nannte den Eingang „später", während er auf der Karte der
    Einstieg war. Die Karte entscheidet, weil sie in Bereichen denkt.
    """

    familien = _lauf_mit_entscheidung().entscheidung.target_family_ids
    pfad = [
        {
            "stufe": "danach",
            "name": "Vor dem Termin klarer werden",
            "nutzen": "Sie fragen Angaben nicht mehr mehrfach nach.",
            "bausteine": ["Angaben vorab"],
            # SF-16 steht nicht im Zielbild, liegt aber im selben Bereich
            # wie SF-01 — und der ist der Einstieg.
            "solution_family_ids": ["SF-16"],
        },
    ]
    dto = results_dto.von_ergebnis(
        _lauf_mit_entscheidung({"ausbaupfad": pfad}, ausbaupfad=pfad)
    )

    for ausblick in dto.ausblicke:
        if ausblick.phase == "future":
            assert ausblick.bereich in dto.karte.future
        else:
            assert ausblick.bereich not in dto.karte.future


# --- Die Bereichsprojektion ------------------------------------------------


def test_every_area_reaches_the_contract_with_its_state() -> None:
    """Alle vierzehn Bereiche, jeder mit dem Zustand der Karte.

    Die stillen gehen mit: Die Karte zeigt die ganze Landschaft, und wer
    nur das Empfohlene ausliefert, kann sie nicht zeichnen.
    """

    dto = results_dto.von_ergebnis(_lauf_mit_entscheidung())

    assert len(dto.module) == 14
    for modul in dto.module:
        knoten = dto.karte.knoten_von(modul.module_key)
        assert knoten is not None
        # Ein zweiter Rechenweg für dieselbe Frage wäre eine zweite
        # Gelegenheit, sich zu widersprechen.
        assert modul.state == knoten.zustand
    assert dto.sichtbare_module
    assert all(m.state != "still" for m in dto.sichtbare_module)


def test_areas_are_ordered_and_addressable() -> None:
    """Reihenfolge des Arbeitslaufs, und jeder Bereich einzeln erreichbar."""

    dto = results_dto.von_ergebnis(_lauf_mit_entscheidung())

    reihenfolgen = [m.map_order for m in dto.module]
    assert reihenfolgen == sorted(reihenfolgen)
    assert dto.modul("kundenzugang_intake") is not None
    assert dto.modul("gibt-es-nicht") is None


def test_areas_name_no_unknown_families() -> None:
    """Jede Kennung im Vertrag steht im freigegebenen Katalog."""

    from app import solution_catalog

    dto = results_dto.von_ergebnis(_lauf_mit_entscheidung())
    freigegeben = solution_catalog.freigegebene_kennungen()

    for modul in dto.module:
        assert set(modul.family_refs) <= freigegeben


def test_a_quiet_area_claims_nothing() -> None:
    """Ein Bereich, der kein Thema ist, behauptet keine Fähigkeiten.

    Sonst stünde im Vertrag, was die Lösung an einer Stelle können müsse,
    an der gar nichts empfohlen wurde.
    """

    dto = results_dto.von_ergebnis(_lauf_mit_entscheidung())

    for modul in dto.module:
        if modul.state == "still":
            assert modul.capability_refs == ()
            assert modul.evidence_refs == ()


def test_a_recommended_area_carries_capabilities_and_evidence() -> None:
    """Was empfohlen ist, sagt auch, was es können muss und woher es kommt."""

    dto = results_dto.von_ergebnis(_lauf_mit_entscheidung())
    einstieg = dto.modul(dto.karte.start[0])

    assert einstieg.capability_refs
    assert all(f.ref and f.label for f in einstieg.capability_refs)
    # Die Belege stammen aus den Signalen, die zu diesen Familien führten.
    assert set(einstieg.evidence_refs) <= {b.id for b in dto.belege}


def test_boundaries_are_referenced_not_repeated() -> None:
    """Eine Grenze steht einmal im Vertrag und wird sonst nur adressiert."""

    dto = results_dto.von_ergebnis(_lauf_mit_entscheidung())

    for modul in dto.module:
        for stelle in modul.boundary_refs:
            grenze = dto.grenzen[stelle]
            assert grenze.herkunft == "katalog"
            assert grenze.familie in modul.family_refs


def test_the_experience_content_reaches_the_contract() -> None:
    """Der Renderer bekommt die Ansichtsdaten, ohne sie selbst zu suchen."""

    from app.operating_model import ANSICHT_ZU_EXPERIENCE

    dto = results_dto.von_ergebnis(_lauf_mit_entscheidung())
    primary = dto.ansichten.primary

    assert primary is not None and primary.hat_inhalt
    assert primary.inhalt.titel and primary.inhalt.daten is not None
    # Der Inhalt gehört zu genau dieser Experience, nicht zu irgendeiner.
    assert ANSICHT_ZU_EXPERIENCE[primary.inhalt.typ] == primary.typ
    assert len(dto.ansichten.supporting) <= 2
    assert all(
        ANSICHT_ZU_EXPERIENCE[e.inhalt.typ] == e.typ
        for e in dto.ansichten.alle
        if e.hat_inhalt
    )


def test_a_view_the_business_may_not_have_is_not_projected() -> None:
    """Eine unzulässige Ansicht aus Aufruf 3 erreicht den Vertrag nicht.

    Der Vertrag weist sie beim Erzeugen bereits zurück. Käme sie aus einem
    älteren gespeicherten Lauf, an dem diese Prüfung noch nicht hing, darf
    sie hier trotzdem nicht durchrutschen.
    """

    from tests.test_experiences import _Ansicht

    lauf = _lauf_mit_entscheidung(
        {"ansichten": [_Ansicht("terminuebersicht", "Termine").model_dump()]}
    )
    dto = results_dto.von_ergebnis(lauf)

    # Termine gehören zu SF-06 und SF-18 — beide nicht in dieser Auswahl.
    assert all(
        not e.hat_inhalt or e.inhalt.typ != "terminuebersicht"
        for e in dto.ansichten.alle
    )
    assert dto.ansichten.primary is not None
    assert not dto.ansichten.primary.hat_inhalt


def test_a_missing_content_is_reported_not_invented() -> None:
    """Liefert Aufruf 3 nichts Zulässiges, bleibt der Rahmen erkennbar leer."""

    dto = results_dto.von_ergebnis(_lauf_mit_entscheidung({"ansichten": []}))

    assert dto.ansichten.primary is not None
    assert not dto.ansichten.primary.hat_inhalt
    assert dto.ansichten.primary.inhalt is None
    assert dto.ansichten.primary.titel is None
    # Der Rahmen selbst bleibt gegroundet — er weiss, wofür er steht.
    assert dto.ansichten.primary.familien


def test_an_adapted_run_still_gets_the_full_landscape() -> None:
    """Auch ein alter Lauf bekommt alle Bereiche — nur still."""

    dto = results_dto.von_ergebnis(_ergebnis())

    assert len(dto.module) == 14
    assert dto.sichtbare_module == ()
    assert all(m.capability_refs == () for m in dto.module)


def test_web_and_pdf_would_read_the_same_contract() -> None:
    """Derselbe Lauf, zweimal gelesen, ergibt denselben Vertrag.

    Das ist die ganze Zusage: Zwei Darstellungen, die hieraus lesen,
    können sich nicht widersprechen.
    """

    lauf = _lauf_mit_entscheidung()
    erst, nochmal = results_dto.von_ergebnis(lauf), results_dto.von_ergebnis(lauf)

    assert erst.module == nochmal.module
    assert erst.ansichten == nochmal.ansichten
    assert erst == nochmal
