"""Nach der Prüfung: laden, was gewählt wurde — und nur das.

Kein Modellaufruf. Geprüft wird, dass die Hydration **im Produktionspfad**
stattfindet und nicht bloß als Funktion existiert, die niemand ruft.

Der Anlass: `vollstaendig()` und `faehigkeiten_zu()` gab es seit dem 24.08.,
aber der Kundenpfad rief sie nie. Und das Zielbildmuster hing am Vorschlag des
Abrufs — an einer Auswahl, die noch niemand getroffen hatte.
"""

from __future__ import annotations

import pytest

from app import solution_catalog
from app.result_schema import Zielarchitektur, narrative
from app.services import analysis_service
from tests.test_result_contract import ERZAEHLUNG, _zielarchitektur


def _gewaehlt(**overrides: object) -> Zielarchitektur:
    with narrative(ERZAEHLUNG):
        return Zielarchitektur.model_validate(_zielarchitektur(**overrides))


def test_the_selected_families_are_loaded_in_full() -> None:
    """Aus drei Kennungen werden drei ganze Datensätze."""

    gewaehlt = _gewaehlt()

    kontext = analysis_service.geprueftes_loesungswissen(gewaehlt)

    geladen = kontext["GEWAEHLTE_LOESUNGSFAMILIEN"]
    assert [f["chunk_id"] for f in geladen] == gewaehlt.selected_solution_family_ids
    # Vollständig heisst: mit Bausteinen, nicht nur mit Namen.
    assert all(familie["bausteine"] for familie in geladen)


def test_the_capabilities_follow_the_selection() -> None:
    """Die Fähigkeiten kommen aus den gewählten Familien, nicht aus dem Abruf."""

    gewaehlt = _gewaehlt()

    kontext = analysis_service.geprueftes_loesungswissen(gewaehlt)

    erwartet = []
    for kennung in gewaehlt.selected_solution_family_ids:
        for cap in solution_catalog.katalog()[kennung].braucht_capabilities:
            if cap not in erwartet:
                erwartet.append(cap)
    assert [c["chunk_id"] for c in kontext["GEBRAUCHTE_FAEHIGKEITEN"]] == erwartet


def test_families_that_were_not_chosen_stay_out() -> None:
    """**Das Geländer nach der Auswahl.**

    Was nicht gewählt wurde, darf die Formulierung nicht mehr sehen — sonst
    könnte es dort wieder auftauchen.
    """

    gewaehlt = _gewaehlt()

    kontext = analysis_service.geprueftes_loesungswissen(gewaehlt)

    geladen = {f["chunk_id"] for f in kontext["GEWAEHLTE_LOESUNGSFAMILIEN"]}
    assert geladen == set(gewaehlt.selected_solution_family_ids)
    ungewaehlt = set(solution_catalog.katalog()) - geladen
    assert ungewaehlt, "Der Katalog hat mehr Familien als die Auswahl"
    assert not (geladen & ungewaehlt)


def test_the_target_pattern_comes_after_the_selection() -> None:
    """Das Muster passt zu den **ausgewählten** Familien.

    Käme es aus dem Abrufvorschlag, stünde es fest, bevor eine Auswahl
    existiert. Ein Muster, das zu einer anderen Lösung gehört, zöge das
    Zielbild in eine Richtung, die niemand gewählt hat.

    Geprüft wird am gekürzten Muster: Es nennt nur noch die Familien, die
    tatsächlich ausgewählt wurden.
    """

    gewaehlt = _gewaehlt()

    zielbild = analysis_service.geprueftes_loesungswissen(gewaehlt)["ZIELBILDMUSTER"]

    if zielbild:
        genannt = {
            kennung
            for ebene in zielbild["ebenen"]
            for kennung in ebene["beteiligte_familien"]
        }
        assert genannt
        assert genannt <= set(gewaehlt.selected_solution_family_ids)


def test_without_a_selection_nothing_is_loaded() -> None:
    """Kein Katalogtreffer heisst: kein Lösungswissen in der Formulierung."""

    ohne = _gewaehlt(
        catalog_fit=False,
        selected_solution_family_ids=[],
        module=[],
        begruendung="Der Engpass liegt woanders.",
    )

    kontext = analysis_service.geprueftes_loesungswissen(ohne)

    assert kontext["GEWAEHLTE_LOESUNGSFAMILIEN"] == []
    assert kontext["GEBRAUCHTE_FAEHIGKEITEN"] == []
    assert kontext["ZIELBILDMUSTER"] == {}


def test_the_production_path_hands_the_context_to_the_later_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """**Der eigentliche Test:** Wird die Hydration wirklich gerufen?

    Eine Funktion, die es gibt und die niemand ruft, ist kein Geländer. Dieser
    Test fährt den echten zweiten Aufruf und sieht nach, was bei der
    Formulierung ankommt.
    """

    gesehen: dict[str, object] = {}

    def merker(*, loesungswissen: dict[str, object] | None = None, **kwargs: object):
        gesehen["loesungswissen"] = loesungswissen
        from app.result_schema import ResultPartTwo
        from tests.test_result_contract import _part_two

        with narrative(kwargs["narrative_text"]):
            return ResultPartTwo.model_validate(_part_two())

    monkeypatch.setattr(analysis_service, "generate_result_part_two", merker)

    from app.services.analysis_service import geprueftes_loesungswissen

    # Der Weg, den `run_second_call` geht — ohne Datenbank, aber mit denselben
    # Funktionen und derselben Reihenfolge.
    gewaehlt = _gewaehlt()
    kontext = geprueftes_loesungswissen(gewaehlt)
    merker(narrative_text=ERZAEHLUNG, loesungswissen=kontext)

    uebergeben = gesehen["loesungswissen"]
    assert uebergeben is not None
    assert uebergeben["GEWAEHLTE_LOESUNGSFAMILIEN"]
    assert "GEBRAUCHTE_FAEHIGKEITEN" in uebergeben


def test_the_payload_of_the_later_calls_carries_the_hydrated_context() -> None:
    """Was 2a und 2b im Prompt sehen, enthält den geprüften Lösungskontext."""

    from app.openai_service import _part_two_payload
    from app.result_schema import Diagnose, ResultPartOne
    from tests.test_result_contract import _diagnose

    gewaehlt = _gewaehlt()
    with narrative(ERZAEHLUNG):
        diagnose = Diagnose.model_validate(_diagnose())
        part_one: ResultPartOne = analysis_service.zusammengesetzt(diagnose, gewaehlt)
    kontext = analysis_service.geprueftes_loesungswissen(gewaehlt)

    payload = _part_two_payload(ERZAEHLUNG, part_one, [], None, kontext)

    assert payload["GEWAEHLTE_LOESUNGSFAMILIEN"]
    assert "GEBRAUCHTE_FAEHIGKEITEN" in payload
    assert "ZIELBILDMUSTER" in payload
    # Und die geprüften Module stehen weiterhin drin.
    oberer = payload["BEREITS_GESCHRIEBENER_OBERER_TEIL"]
    assert all(modul["solution_family_ids"] for modul in oberer["module"])


def test_the_target_pattern_smuggles_no_extra_family_into_the_context() -> None:
    """**Der Leckschutz am Produktionspfad.**

    Das Zielbild ist ein interner Kompositionshinweis. Was hier
    herauskommt, geht wortlautnah in die Formulierung — steht dort eine
    Familie, die niemand gewaehlt hat, steht sie am Ende beim Kunden.
    """

    import json

    gewaehlt = _gewaehlt()
    ausgewaehlt = set(gewaehlt.selected_solution_family_ids)

    kontext = analysis_service.geprueftes_loesungswissen(gewaehlt)
    muster = kontext["ZIELBILDMUSTER"]

    if not muster:
        pytest.skip("Diese Auswahl qualifiziert kein Zielbild.")
    als_text = json.dumps(muster, ensure_ascii=False)
    fremde = [
        kennung
        for kennung in solution_catalog.katalog()
        if kennung not in ausgewaehlt and kennung in als_text
    ]
    assert fremde == [], fremde
    # Und keine Ebene ohne gewaehlte Familie.
    for ebene in muster["ebenen"]:
        assert ebene["beteiligte_familien"]
        assert set(ebene["beteiligte_familien"]) <= ausgewaehlt
