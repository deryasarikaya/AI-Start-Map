"""Die Diagnose bestimmt die Größe der Lösung — auch nach unten.

Kein Modellaufruf. Geprüft wird, dass ein kleiner Fall klein bleiben darf und
dass „keine neue Technik nötig" ein Ergebnis ist und kein Fehler.

Der Anlass: Das Schema verlangte einmal sechs Module, dann drei, dazu zwei
Ansichten, vier Systeme, vier Architekturebenen und sechs Umsetzungsschritte.
Ein Zweipersonenbetrieb mit einem Telefon bekam damit dieselbe Menge wie eine
Verwaltung mit 450 Einheiten — und was fehlte, musste erfunden werden.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.result_schema import (
    Diagnose,
    ResultPartOne,
    ResultPartTwo,
    Zielarchitektur,
    narrative,
)
from app.services import analysis_service
from tests.test_result_contract import (
    ERZAEHLUNG,
    _diagnose,
    _kontext,
    _part_one,
    _part_two,
    _zielarchitektur,
)


# --- Kleine Ergebnisse ----------------------------------------------------


def test_a_result_with_one_module_is_valid() -> None:
    """Ein Modul, wenn ein Modul die Antwort ist."""

    daten = _part_one()
    daten["module"] = daten["module"][:1]

    teil = ResultPartOne.model_validate(daten, context=_kontext())

    assert len(teil.module) == 1


def test_a_result_without_views_is_valid() -> None:
    """Eine Ansicht entsteht, wenn sie etwas erklärt — sonst nicht."""

    teil = ResultPartTwo.model_validate(
        _part_two(ansichten=[]), context=_kontext()
    )

    assert teil.ansichten == []


def test_a_result_without_systems_is_valid() -> None:
    """Systeme kommen aus der Erzählung. Wer keine nennt, bekommt keine."""

    teil = ResultPartTwo.model_validate(
        _part_two(systeme=[]), context=_kontext()
    )

    assert teil.systeme == []


def test_a_short_comparison_is_valid() -> None:
    """Ein einfacher Ablauf hat drei Schritte, nicht fünf."""

    daten = _part_one()
    daten["vergleich"] = {
        "heute": ["Der Anruf kommt", "Jemand merkt es sich", "Später fehlt es"],
        "kuenftig": ["Der Anruf kommt", "Er wird festgehalten", "Er ist auffindbar"],
    }

    teil = ResultPartOne.model_validate(daten, context=_kontext())

    assert len(teil.vergleich.heute) == 3


def test_the_page_hides_what_is_empty(client) -> None:  # type: ignore[no-untyped-def]
    """Keine Überschrift über nichts.

    Ohne Ansichten und ohne Module entfallen die beiden Abschnitte. Eine
    Überschrift, unter der nichts steht, ist die Ankündigung von etwas, das
    nicht kommt.
    """

    from app.services import example_service

    echt = example_service.example_result

    def ohne(db, slug):  # type: ignore[no-untyped-def]
        return echt(db, slug).model_copy(update={"ansichten": [], "module": []})

    example_service.example_result = ohne
    try:
        seite = client.get("/beispiel/hausverwaltung").text
    finally:
        example_service.example_result = echt

    assert "So würde der Einstieg im Alltag aussehen" not in seite
    assert "Das kann die Lösung übernehmen" not in seite
    # Die Diagnose steht weiterhin als Decision Hero da.
    assert "AI Start Map · Ihre Auswertung" in seite
    assert "Informationen zu einem Fall liegen verstreut" in seite


# --- Keine neue Technik ---------------------------------------------------


def test_no_new_technology_needs_no_modules() -> None:
    """Wer ein geeignetes System hat und es nur nicht nutzt, braucht keins.

    `catalog_fit=false` heisst: null Familien, null Module. Das Schema darf
    dann nichts erzwingen — sonst entstünde „wir müssen wenigstens irgendetwas
    empfehlen".
    """

    with narrative(ERZAEHLUNG):
        gewaehlt = Zielarchitektur.model_validate(
            _zielarchitektur(
                catalog_fit=False,
                recommend_new_technology=False,
                selected_solution_family_ids=[],
                module=[],
                begruendung=(
                    "Die vorhandene Software deckt den Ablauf ab, sie wird nur "
                    "uneinheitlich genutzt."
                ),
            )
        )

    assert gewaehlt.module == []
    assert gewaehlt.recommend_new_technology is False


def test_existing_software_may_still_use_the_catalogue() -> None:
    """„Das Vorhandene konsequent nutzen" ist auch eine Lösung.

    `recommend_new_technology=false` schliesst Familien nicht aus: Der
    Unterschied liegt darin, ob etwas Neues gebaut oder etwas Vorhandenes
    geordnet wird.
    """

    with narrative(ERZAEHLUNG):
        gewaehlt = Zielarchitektur.model_validate(
            _zielarchitektur(recommend_new_technology=False)
        )

    assert gewaehlt.recommend_new_technology is False
    assert gewaehlt.selected_solution_family_ids


def test_no_catalogue_fit_loads_no_solution_knowledge() -> None:
    """Ohne Auswahl bekommt die Formulierung kein Lösungswissen."""

    with narrative(ERZAEHLUNG):
        ohne = Zielarchitektur.model_validate(
            _zielarchitektur(
                catalog_fit=False,
                selected_solution_family_ids=[],
                module=[],
                begruendung="Der Engpass liegt im Personal.",
            )
        )

    kontext = analysis_service.geprueftes_loesungswissen(ohne)

    assert kontext["GEWAEHLTE_LOESUNGSFAMILIEN"] == []
    assert kontext["ZIELBILDMUSTER"] == {}


def test_a_diagnosis_without_a_solution_still_assembles() -> None:
    """Der obere Teil entsteht auch ohne ein einziges Modul."""

    with narrative(ERZAEHLUNG):
        diagnose = Diagnose.model_validate(_diagnose())
        ohne = Zielarchitektur.model_validate(
            _zielarchitektur(
                catalog_fit=False,
                recommend_new_technology=False,
                selected_solution_family_ids=[],
                module=[],
                begruendung="Das vorhandene System reicht.",
            )
        )
        part_one = analysis_service.zusammengesetzt(diagnose, ohne)

    assert part_one.module == []
    assert part_one.kurzfassung.engpass_satz
    assert part_one.verstanden.engpass_absatz


def test_a_module_still_needs_its_catalogue_entry() -> None:
    """Die Untergrenzen sind weg — das Geländer nicht."""

    daten = _zielarchitektur()
    daten["module"][0]["baustein_refs"] = ["Etwas, das im Katalog nicht steht"]

    with pytest.raises(ValidationError, match="keinen Baustein"):
        with narrative(ERZAEHLUNG):
            Zielarchitektur.model_validate(daten)
