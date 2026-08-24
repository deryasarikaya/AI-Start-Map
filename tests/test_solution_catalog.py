"""Das Geländer: Empfohlen wird nur, was im freigegebenen Katalog steht.

Kein Modellaufruf. Geprüft wird die Stelle, an der eine erfundene Lösung
scheitern muss — vor der Datenbank, vor der Seite, vor dem Kunden.

Bis zum 24.08. gab es diese Stelle nicht. Das Modell schrieb Module als vier
freie Texte, und keine Zeile im Projekt prüfte, ob es sie gibt.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app import solution_catalog
from app.result_schema import Zielarchitektur, narrative
from tests.test_result_contract import ERZAEHLUNG, _zielarchitektur


def _gewaehlt(**overrides: object) -> Zielarchitektur:
    with narrative(ERZAEHLUNG):
        return Zielarchitektur.model_validate(_zielarchitektur(**overrides))


# --- Der Katalog selbst ----------------------------------------------------


def test_only_released_families_are_offered() -> None:
    """Die Freigabeliste entscheidet, nicht der Ordnerinhalt.

    Drei Familien sind am 21.08. aus einem Produktvergleich ins Repository
    gekommen — von einem Agenten geschrieben, von niemandem freigegeben. Sie
    lagen im Index und wären empfehlbar gewesen.
    """

    erlaubt = solution_catalog.katalog()

    assert len(erlaubt) == 24
    for erfunden in ("SF-25", "SF-26", "SF-27"):
        assert erfunden not in erlaubt


def test_the_whole_catalogue_is_offered_for_selection() -> None:
    """Das Modell sieht alle erlaubten Familien, nicht nur die abgerufenen.

    Sonst entscheidet ein Abruftreffer, was überhaupt wählbar ist — und ein
    schlechter Treffer macht die richtige Familie unerreichbar.
    """

    liste = solution_catalog.zur_auswahl(["SF-06"])

    assert len(liste) == 24
    # Der Vorschlag steht oben, ist aber nur ein Vorschlag.
    assert liste[0]["id"] == "SF-06"
    assert liste[0]["vom_abruf_vorgeschlagen"] is True
    assert sum(1 for eintrag in liste if eintrag["vom_abruf_vorgeschlagen"]) == 1
    for eintrag in liste:
        assert eintrag["worum_es_geht"]
        assert eintrag["nicht_geeignet_wenn"]


def test_an_invented_identifier_is_rejected() -> None:
    """`pruefe_auswahl` trennt Katalog von Erfindung."""

    gueltig, ungueltig = solution_catalog.pruefe_auswahl(
        ["SF-01", "SF-99", "SF-25", "Autonomer Einkaufsagent"]
    )

    assert gueltig == ["SF-01"]
    assert ungueltig == ["SF-99", "SF-25", "Autonomer Einkaufsagent"]


def test_a_baustein_belongs_to_its_family_or_to_none() -> None:
    """Ein Baustein zählt nur bei der Familie, die ihn führt."""

    erster = solution_catalog.katalog()["SF-01"].bausteine[0]

    assert solution_catalog.pruefe_baustein(erster, ["SF-01"]) == "SF-01"
    assert solution_catalog.pruefe_baustein(erster, ["SF-02"]) is None
    assert solution_catalog.pruefe_baustein("Autonomer Agent", ["SF-01"]) is None
    # Gross- und Kleinschreibung entscheidet nicht, der Wortlaut schon.
    assert solution_catalog.pruefe_baustein(erster.upper(), ["SF-01"]) == "SF-01"


def test_every_baustein_survives_the_language_check() -> None:
    """Ein Baustein muss zitierbar sein, ohne die Sprachprüfung auszulösen.

    `baustein_refs` werden wörtlich aus dem Katalog übernommen und laufen
    danach durch dieselbe Prüfung wie der Kundentext. Ein Katalogeintrag mit
    „Software" oder „Schnittstelle" darin würde jede Erzeugung scheitern
    lassen — und zwar mit einer Meldung, die woanders hinzeigt.
    """

    from app.schemas import (
        contains_internal_reference,
        contains_prohibited_customer_language,
    )

    for familie in solution_catalog.katalog().values():
        for baustein in familie.bausteine:
            assert not contains_prohibited_customer_language(baustein), (
                f"{familie.kennung}: {baustein}"
            )
            assert not contains_internal_reference(baustein), (
                f"{familie.kennung}: {baustein}"
            )


# --- Der Vertrag lässt nichts Erfundenes durch -----------------------------


def test_a_valid_selection_passes() -> None:
    """Die Gegenprobe: Was aus dem Katalog kommt, geht durch."""

    gewaehlt = _gewaehlt()

    assert len(gewaehlt.selected_solution_family_ids) == 3
    assert all(modul.solution_family_ids for modul in gewaehlt.module)
    assert all(modul.baustein_refs for modul in gewaehlt.module)


def test_an_invented_family_never_reaches_the_customer() -> None:
    """Eine Kennung, die es nicht gibt, bricht den ganzen Aufruf ab."""

    with pytest.raises(ValidationError, match="freigegebenen Katalog"):
        _gewaehlt(selected_solution_family_ids=["SF-01", "SF-99"])


def test_a_family_that_is_not_released_is_rejected() -> None:
    """SF-25 existiert im Repository, aber nicht in der Freigabe."""

    with pytest.raises(ValidationError, match="freigegebenen Katalog"):
        _gewaehlt(selected_solution_family_ids=["SF-25"])


def test_a_module_must_name_a_selected_family() -> None:
    """Ein Modul darf nicht auf eine Familie zeigen, die niemand gewählt hat."""

    daten = _zielarchitektur()
    daten["module"][0]["solution_family_ids"] = ["SF-24"]

    with pytest.raises(ValidationError, match="nicht ausgewählt"):
        with narrative(ERZAEHLUNG):
            Zielarchitektur.model_validate(daten)


def test_a_module_without_a_real_baustein_is_rejected() -> None:
    """**Der wichtigste Test.**

    „Autonomer KI-Einkaufsagent" mit der Kennung SF-01 danebengesetzt ist
    genau die Lücke, die eine blosse Kennungsprüfung offen lässt. Der Inhalt
    muss zu einem Baustein dieser Familie gehören.
    """

    daten = _zielarchitektur()
    daten["module"][0]["name"] = "Autonomer KI-Einkaufsagent"
    daten["module"][0]["baustein_refs"] = ["Autonomer Einkauf ohne Rückfrage"]

    with pytest.raises(ValidationError, match="keinen Baustein"):
        with narrative(ERZAEHLUNG):
            Zielarchitektur.model_validate(daten)


def test_the_customer_wording_stays_free() -> None:
    """Der Name darf klingen wie der Betrieb — nur die Funktion ist gebunden."""

    daten = _zielarchitektur()
    daten["module"][0]["name"] = "Ihr Eingang für Telefon und WhatsApp"

    with narrative(ERZAEHLUNG):
        gewaehlt = Zielarchitektur.model_validate(daten)

    assert gewaehlt.module[0].name == "Ihr Eingang für Telefon und WhatsApp"
    assert gewaehlt.module[0].baustein_refs


# --- Wenn nichts passt -----------------------------------------------------


def test_no_catalog_fit_is_a_valid_answer() -> None:
    """Ein ehrliches Nein ist besser als eine erfundene Lösung."""

    with narrative(ERZAEHLUNG):
        gewaehlt = Zielarchitektur.model_validate(
            _zielarchitektur(
                catalog_fit=False,
                selected_solution_family_ids=[],
                module=[],
                begruendung="Der Engpass liegt im Personal, dafür gibt es nichts.",
            )
        )

    assert gewaehlt.catalog_fit is False
    assert gewaehlt.module == []


def test_no_fit_and_modules_at_the_same_time_is_rejected() -> None:
    """Entweder es passt nichts — oder es stehen Familien da. Nicht beides."""

    with pytest.raises(ValidationError, match="Beides zusammen"):
        _gewaehlt(catalog_fit=False)


def test_a_fit_without_families_is_rejected() -> None:
    """Wer `catalog_fit` bejaht, muss auch etwas gewählt haben."""

    with pytest.raises(ValidationError, match="setze catalog_fit auf false"):
        _gewaehlt(selected_solution_family_ids=[], module=[])


def test_existing_software_may_need_no_new_technology() -> None:
    """Wer ein geeignetes System hat und es nur nicht nutzt, braucht keins.

    Das Feld steht im Vertrag, damit dieser Fall eine Antwort hat, statt zur
    nächstbesten Empfehlung zu führen.
    """

    gewaehlt = _gewaehlt(recommend_new_technology=False)

    assert gewaehlt.recommend_new_technology is False
    # Familien darf er trotzdem haben: „das Vorhandene konsequent nutzen" ist
    # auch eine Lösung aus dem Katalog.
    assert gewaehlt.selected_solution_family_ids


def test_too_many_families_are_rejected() -> None:
    """Over-Solution: Acht ist die Grenze, mehr ist eine Aufzählung."""

    erlaubt = list(solution_catalog.katalog())[:9]

    with pytest.raises(ValidationError):
        _gewaehlt(selected_solution_family_ids=erlaubt)


def test_a_target_picture_needs_at_least_three_modules() -> None:
    """Unter drei Modulen ist es kein Zielbild, sondern eine Einzelautomation."""

    daten = _zielarchitektur()
    daten["module"] = daten["module"][:2]

    with pytest.raises(ValidationError, match="ab drei Modulen"):
        with narrative(ERZAEHLUNG):
            Zielarchitektur.model_validate(daten)


# --- Was danach geladen wird ----------------------------------------------


def test_the_full_records_come_only_after_the_check() -> None:
    """Erst prüfen, dann laden — und nur das Geprüfte."""

    voll = solution_catalog.vollstaendig(["SF-01", "SF-25"])

    assert [datensatz["chunk_id"] for datensatz in voll] == ["SF-01"]


def test_capabilities_follow_the_selected_families() -> None:
    """CAP konkretisiert eine gewählte Familie — es erzeugt keine neue."""

    faehigkeiten = solution_catalog.faehigkeiten_zu(["SF-01"])
    gebraucht = solution_catalog.katalog()["SF-01"].braucht_capabilities

    assert [f["chunk_id"] for f in faehigkeiten] == list(gebraucht)


def test_the_target_pattern_covers_the_selection() -> None:
    """Das Zielbildmuster mit der grössten Überdeckung, oder keines."""

    getroffen = solution_catalog.zielbild_zu(["SF-01", "SF-02", "SF-03"])

    assert getroffen is not None
    assert getroffen["chunk_id"].startswith("TA-")
    assert solution_catalog.zielbild_zu([]) is None
