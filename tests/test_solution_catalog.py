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

    Drei Familien kamen aus einem Produktvergleich ins Repository, von
    niemandem freigegeben. Eine davon — die Wirtschaftlichkeitsvorschau —
    hat Derya danach geprüft und aufgenommen; die beiden anderen sind als
    Bausteine in SF-21 und SF-13 aufgegangen und bleiben keine eigenen
    Familien.
    """

    erlaubt = solution_catalog.katalog()

    assert len(erlaubt) == 25
    assert "SF-25" in erlaubt
    for aufgegangen in ("SF-26", "SF-27"):
        assert aufgegangen not in erlaubt


def test_the_whole_catalogue_is_offered_for_selection() -> None:
    """Das Modell sieht alle erlaubten Familien, nicht nur die abgerufenen.

    Sonst entscheidet ein Abruftreffer, was überhaupt wählbar ist — und ein
    schlechter Treffer macht die richtige Familie unerreichbar.
    """

    liste = solution_catalog.zur_auswahl(["SF-06"])

    assert len(liste) == 25
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
        ["SF-01", "SF-99", "SF-26", "Autonomer Einkaufsagent"]
    )

    assert gueltig == ["SF-01"]
    assert ungueltig == ["SF-99", "SF-26", "Autonomer Einkaufsagent"]


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
    """SF-26 ist in SF-21 aufgegangen und keine eigene Familie mehr.

    Wer die alte Kennung nennt, bekommt sie nicht — auch nicht, weil es
    sie einmal gab.
    """

    with pytest.raises(ValidationError, match="freigegebenen Katalog"):
        _gewaehlt(selected_solution_family_ids=["SF-26"])


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


def test_one_module_is_a_valid_solution() -> None:
    """Eine Einzelautomation ist eine Lösung, wenn der Fall eine ist."""

    daten = _zielarchitektur()
    daten["module"] = daten["module"][:1]
    daten["selected_solution_family_ids"] = daten["module"][0][
        "solution_family_ids"
    ]

    with narrative(ERZAEHLUNG):
        gewaehlt = Zielarchitektur.model_validate(daten)

    assert len(gewaehlt.module) == 1


def test_families_without_a_module_are_rejected() -> None:
    """Wer Familien wählt, muss auch etwas daraus bauen.

    Sonst stünde eine Auswahl da, die auf der Seite nirgends ankommt —
    und niemand könnte sagen, was empfohlen wurde.
    """

    daten = _zielarchitektur()
    daten["module"] = []

    with pytest.raises(ValidationError, match="kein Modul daraus"):
        with narrative(ERZAEHLUNG):
            Zielarchitektur.model_validate(daten)


# --- Was danach geladen wird ----------------------------------------------


def test_the_full_records_come_only_after_the_check() -> None:
    """Erst prüfen, dann laden — und nur das Geprüfte."""

    voll = solution_catalog.vollstaendig(["SF-01", "SF-26"])

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

# --- Was der kuratierte Katalog enthaelt ----------------------------------


def test_the_new_family_carries_its_limits() -> None:
    """SF-25 zeigt Zahlen — entscheiden darf sie nichts.

    Preise, Loehne und Zahlungen bleiben beim Menschen, und die Zahlen
    kommen aus strukturierten Daten statt aus einer Schaetzung des
    Modells. Beides steht im Datensatz, nicht nur im Prompt.
    """

    familie = solution_catalog.katalog()["SF-25"]

    assert familie.name == "Wirtschaftlichkeits- und Liquiditätsvorschau"
    for baustein in (
        "Deckungsbeitrag je Leistung oder Auftrag",
        "Auslastungsvorschau",
        "kurzfristige Liquiditätsvorschau",
        "Warnung bei festgelegten Schwellen",
    ):
        assert baustein in familie.bausteine, baustein
    beim_menschen = " ".join(familie.bleibt_beim_menschen).casefold()
    for entscheidung in ("preise", "löhne", "zahlungen"):
        assert entscheidung in beim_menschen, entscheidung
    ausgeschlossen = " ".join(familie.nicht_geeignet_wenn).casefold()
    assert "steuer" in ausgeschlossen


def test_recruiting_lives_in_the_onboarding_family() -> None:
    """SF-26 ist keine eigene Familie — ihre Bausteine stecken in SF-21."""

    familie = solution_catalog.katalog()["SF-21"]

    assert "Personalgewinnung" in familie.name
    for baustein in (
        "Entwurf der Stellenanzeige",
        "Bewerbungen bündeln",
        "Gesprächsplanung",
        "Übergabe ins Onboarding",
    ):
        assert baustein in familie.bausteine, baustein
    # Die alten Onboarding-Bausteine bleiben.
    assert "Onboarding-Checkliste" in familie.bausteine
    # Und wer eingestellt wird, entscheidet ein Mensch.
    assert any(
        "auswähl" in eintrag.casefold() or "einstell" in eintrag.casefold()
        for eintrag in familie.bleibt_beim_menschen
    )


def test_feedback_evaluation_lives_in_the_marketing_family() -> None:
    """SF-27 ist keine eigene Familie — SF-13 wertet jetzt selbst aus."""

    familie = solution_catalog.katalog()["SF-13"]

    for baustein in (
        "Rückmeldungen bündeln",
        "Themen erkennen",
        "Häufigkeiten und Trends erkennen",
        "Übergabe an den zuständigen betrieblichen Prozess",
    ):
        assert baustein in familie.bausteine, baustein
    assert "Bewertungsanfrage" in familie.bausteine
    # Keine Bewertung einzelner Personen.
    ausgeschlossen = " ".join(familie.nicht_geeignet_wenn).casefold()
    assert "mitarbeitende" in ausgeschlossen or "personen" in ausgeschlossen


def test_every_cross_reference_points_at_something() -> None:
    """DP zu SF, SF zu CAP, TA zu SF — kein Verweis darf ins Leere gehen.

    Beim Zusammenlegen von SF-26 und SF-27 blieb ein Verweis stehen, der
    auf eine Familie zeigte, die es nicht mehr gibt. Ein Abruf haette ihn
    stillschweigend uebergangen.
    """

    import json

    ordner = solution_catalog.KATALOG_DATEI.parent

    def lies(name: str) -> list[dict]:
        return [
            json.loads(zeile)
            for zeile in (ordner / name).read_text(encoding="utf-8").splitlines()
            if zeile.strip()
        ]

    familien = {x["chunk_id"] for x in lies("03_solution_families.jsonl")}
    faehigkeiten = {x["chunk_id"] for x in lies("04_automation_capabilities.jsonl")}

    for muster in lies("02_diagnostic_patterns.jsonl"):
        for kennung in muster["passende_loesungsfamilien"]:
            assert kennung in familien, f"{muster['chunk_id']} -> {kennung}"
    for familie in lies("03_solution_families.jsonl"):
        for kennung in familie["braucht_capabilities"]:
            assert kennung in faehigkeiten, f"{familie['chunk_id']} -> {kennung}"
        for kennung in familie.get("typische_kombination") or []:
            assert kennung in familien, f"{familie['chunk_id']} -> {kennung}"
    for zielbild in lies("05_target_architectures.jsonl"):
        for kennung in zielbild.get("enthaltene_familien") or []:
            assert kennung in familien, f"{zielbild['chunk_id']} -> {kennung}"
