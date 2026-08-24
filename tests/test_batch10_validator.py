"""Das Prüfskript für Batch 10.

Jede der acht Prüfungen bekommt hier einen Fall, der sie auslöst, und die
Gegenprobe: ein sauberer Batch geht durch. Ein Prüfskript, das nichts findet,
ist schlimmer als keins — es macht ruhig.

Geschrieben wird nur in einen Testordner, nie in
`knowledge/candidates/batch_10/`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import pruefe_batch10  # noqa: E402

SPEZIFIKATION = (
    Path(__file__).resolve().parents[1]
    / "knowledge/candidates/batch_10/SPEZIFIKATION.md"
)


def _gemeinsam(kennung: str, typ: str) -> dict[str, object]:
    """Die acht Felder, die in jedem Datensatz stehen müssen."""

    return {
        "chunk_id": kennung,
        "chunk_type": typ,
        "title": f"Titel zu {kennung}",
        "batch_id": "batch_10",
        "source_strength": "derived",
        "content_origin": "synthesized_from_research",
        "is_primary_evidence": False,
        "process_type": ["A", "G"],
    }


def _solution_family(kennung: str, **abweichungen: object) -> dict[str, object]:
    """Eine gültige Lösungsfamilie nach der Spezifikation."""

    datensatz = _gemeinsam(kennung, "solution_family") | {
        "familie_name": "E-Mail- und Nachrichtenverarbeitung",
        "worum_es_geht": "Eingehende Nachrichten werden gelesen und zugeordnet.",
        "geeignet_wenn": ["a", "b", "c", "d", "e"],
        "nicht_geeignet_wenn": ["x", "y", "z"],
        "bausteine": ["eins", "zwei", "drei", "vier"],
        "braucht_capabilities": ["CAP-01"],
        "bleibt_beim_menschen": ["Freigabe", "Ausnahmen"],
        "setzt_voraus": ["Postfach", "Zugang"],
        # Leer, damit die Vorlage selbst nirgendwohin verweist. Wer den
        # Verweisprüfer testen will, setzt das Feld im Test.
        "typische_kombination": [],
        "reihenfolge_hinweis": "Kommt früh.",
        "kundennaher_name": "Posteingang, der mitdenkt",
        "gilt_fuer_betriebsarten": ["A", "G"],
    }
    datensatz.update(abweichungen)
    return datensatz


def _capability(kennung: str) -> dict[str, object]:
    return _gemeinsam(kennung, "automation_capability") | {
        "faehigkeit_name": "Klassifikation",
        "worum_es_geht": "Worum geht es in dieser Nachricht.",
        "braucht_als_eingabe": ["Text", "Kanal"],
        "liefert": ["Kategorie"],
        "zuverlaessigkeit": "Geht gut, solange die Kategorien klar sind.",
        "typische_fehler": ["Randfälle", "Mischformen"],
        "menschliche_pruefung": "bei Unsicherheit",
        "gehoert_zu_familien": ["SF-01"],
    }


@pytest.fixture
def batch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Ein leerer Batchordner mit der echten Spezifikation daneben.

    Der Bestand wird dabei leer gehalten. Der Testordner liegt ausserhalb von
    `knowledge/candidates/batch_10/`, also zählt der echte Batchordner selbst
    als Bestand — und dort arbeitet Derya. Sobald sie eine Kennung einträgt,
    die eine Vorlage hier auch benutzt, fällt ein halbes Dutzend Tests aus
    einem Grund um, der mit dem Geprüften nichts zu tun hat. Dass die
    Bestandsprüfung greift, sichert
    `test_an_id_already_taken_in_the_corpus_is_found` mit einem eigenen,
    gesetzten Bestand.
    """

    ordner = tmp_path / "batch_10"
    ordner.mkdir()
    monkeypatch.setattr(pruefe_batch10, "bestehende_kennungen", lambda _batch: {})
    (ordner / "SPEZIFIKATION.md").write_text(
        SPEZIFIKATION.read_text(encoding="utf-8"), encoding="utf-8"
    )
    return ordner


def _schreibe(ordner: Path, name: str, datensaetze: list[dict]) -> None:
    ordner.joinpath(name).write_text(
        "\n".join(json.dumps(d, ensure_ascii=False) for d in datensaetze) + "\n",
        encoding="utf-8",
    )


def test_a_clean_batch_passes(batch: Path) -> None:
    """Die Gegenprobe: Was der Spezifikation folgt, geht durch."""

    _schreibe(batch, "03_solution_families.jsonl", [_solution_family("SF-01")])
    _schreibe(batch, "04_automation_capabilities.jsonl", [_capability("CAP-01")])

    befund = pruefe_batch10.pruefe(batch)

    assert befund.fehler == []
    assert befund.gelesen["03_solution_families.jsonl"] == 1


def test_a_broken_line_names_file_line_and_text(batch: Path) -> None:
    """Bei kaputtem JSON steht da, wo es steht und wie es anfängt."""

    batch.joinpath("03_solution_families.jsonl").write_text(
        json.dumps(_solution_family("SF-01"), ensure_ascii=False)
        + "\n{ das ist kein JSON, sondern ein angefangener Satz\n",
        encoding="utf-8",
    )

    befund = pruefe_batch10.pruefe(batch)

    assert any("03_solution_families.jsonl:2" in f for f in befund.fehler)
    assert any("das ist kein JSON" in f for f in befund.fehler)


def test_a_missing_chunk_id_is_an_error(batch: Path) -> None:
    """Ohne chunk_id bricht der Indexer ab — also fällt es hier auf."""

    ohne = _solution_family("SF-01")
    ohne["chunk_id"] = ""
    _schreibe(batch, "03_solution_families.jsonl", [ohne])

    befund = pruefe_batch10.pruefe(batch)

    assert any("chunk_id fehlt oder ist leer" in f for f in befund.fehler)


def test_a_duplicate_id_inside_the_batch_is_found(batch: Path) -> None:
    _schreibe(
        batch,
        "03_solution_families.jsonl",
        [_solution_family("SF-01"), _solution_family("SF-01")],
    )

    befund = pruefe_batch10.pruefe(batch)

    assert any("gibt es schon in" in f for f in befund.fehler)


def test_an_id_already_taken_in_the_corpus_is_found(
    batch: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Die Kennung muss über den **ganzen** Bestand eindeutig sein."""

    monkeypatch.setattr(
        pruefe_batch10,
        "bestehende_kennungen",
        lambda _batch: {"SF-01": "knowledge/runtime/irgendwas.jsonl"},
    )
    _schreibe(batch, "03_solution_families.jsonl", [_solution_family("SF-01")])

    befund = pruefe_batch10.pruefe(batch)

    assert any("im Bestand schon vergeben" in f for f in befund.fehler)


def test_the_wrong_type_in_a_file_is_found(batch: Path) -> None:
    """Ein Diagnosemuster in der Lösungsfamiliendatei fällt auf."""

    falsch = _solution_family("SF-01", chunk_type="diagnostic_pattern")
    _schreibe(batch, "03_solution_families.jsonl", [falsch])

    befund = pruefe_batch10.pruefe(batch)

    assert any("diese Datei verlangt" in f for f in befund.fehler)


def test_a_dangling_reference_is_found(batch: Path) -> None:
    """Die wichtigste Prüfung: ein Verweis, zu dem es keinen Datensatz gibt."""

    _schreibe(
        batch,
        "03_solution_families.jsonl",
        [_solution_family("SF-01", braucht_capabilities=["CAP-01", "CAP-99"])],
    )
    _schreibe(batch, "04_automation_capabilities.jsonl", [_capability("CAP-01")])

    befund = pruefe_batch10.pruefe(batch)

    assert any("Verweis ins Leere" in f and "CAP-99" in f for f in befund.fehler)
    # CAP-01 gibt es, also wird es nicht gemeldet.
    assert not any("CAP-01" in f and "Verweis ins Leere" in f for f in befund.fehler)


def test_a_record_does_not_dangle_on_its_own_id(batch: Path) -> None:
    """Die eigene chunk_id ist kein Verweis auf sich selbst."""

    _schreibe(batch, "03_solution_families.jsonl", [_solution_family("SF-01")])
    _schreibe(batch, "04_automation_capabilities.jsonl", [_capability("CAP-01")])

    befund = pruefe_batch10.pruefe(batch)

    assert not any("SF-01" in f and "Verweis ins Leere" in f for f in befund.fehler)


def test_a_missing_required_field_is_found(batch: Path) -> None:
    """Die Pflichtfelder kommen aus der Spezifikation, nicht aus dem Skript."""

    unvollstaendig = _solution_family("SF-01")
    del unvollstaendig["nicht_geeignet_wenn"]
    del unvollstaendig["source_strength"]
    _schreibe(batch, "03_solution_families.jsonl", [unvollstaendig])
    _schreibe(batch, "04_automation_capabilities.jsonl", [_capability("CAP-01")])

    befund = pruefe_batch10.pruefe(batch)

    (meldung,) = [f for f in befund.fehler if "Pflichtfelder fehlen" in f]
    assert "nicht_geeignet_wenn" in meldung
    assert "source_strength" in meldung


def test_a_content_field_is_rejected(batch: Path) -> None:
    """Der Indexer soll den Text aus den Feldern bauen."""

    _schreibe(
        batch,
        "03_solution_families.jsonl",
        [_solution_family("SF-01", content="Vorgekauter Text")],
    )
    _schreibe(batch, "04_automation_capabilities.jsonl", [_capability("CAP-01")])

    befund = pruefe_batch10.pruefe(batch)

    assert any("hat ein content-Feld" in f for f in befund.fehler)


def test_a_short_list_is_a_warning_not_an_error(batch: Path) -> None:
    """Zu wenige Einträge halten den Batch nicht auf, werden aber gesagt."""

    _schreibe(
        batch,
        "03_solution_families.jsonl",
        [_solution_family("SF-01", geeignet_wenn=["nur eins"])],
    )
    _schreibe(batch, "04_automation_capabilities.jsonl", [_capability("CAP-01")])

    befund = pruefe_batch10.pruefe(batch)

    assert befund.fehler == []
    assert any(
        "geeignet_wenn hat 1 Einträge" in w and "mindestens 5" in w
        for w in befund.warnungen
    )


def test_missing_files_are_reported_not_failed(batch: Path) -> None:
    """Derya schreibt nacheinander — ein halber Batch ist kein Fehler."""

    _schreibe(batch, "03_solution_families.jsonl", [_solution_family("SF-01")])
    _schreibe(batch, "04_automation_capabilities.jsonl", [_capability("CAP-01")])

    befund = pruefe_batch10.pruefe(batch)

    assert befund.fehler == []
    assert len(befund.fehlende_dateien) == 3
    # Gemeldet wird der Dateianfang, nicht der ganze Name: „01*.jsonl".
    assert any(eintrag.startswith("01") for eintrag in befund.fehlende_dateien)


def test_an_unreadable_specification_says_so_loudly(tmp_path: Path) -> None:
    """Eine Prüfung, die nichts prüft, wäre schlimmer als keine."""

    ordner = tmp_path / "ohne_spezifikation"
    ordner.mkdir()
    _schreibe(ordner, "03_solution_families.jsonl", [_solution_family("SF-01")])

    befund = pruefe_batch10.pruefe(ordner)

    assert any("SPEZIFIKATION.md" in f for f in befund.fehler)


def test_the_specification_still_yields_all_five_types() -> None:
    """Ändert sich der Aufbau der Spezifikation, fällt es hier auf.

    Das Skript liest die Feldlisten aus ihr. Wenn sie sich anders liest,
    prüft es plötzlich weniger — ohne dass jemand etwas merkt.
    """

    felder = pruefe_batch10.felder_aus_der_spezifikation(SPEZIFIKATION.parent)

    assert set(felder) == set(pruefe_batch10.TYP_JE_DATEI.values())
    assert felder["solution_family"]["geeignet_wenn"] == 5
    assert felder["business_pattern"]["fachbegriffe"] == 15

# --- Der Zirkelschluss ----------------------------------------------------


ERZAEHLUNG = (
    "Ich muss jedes Mal erst suchen, wo die Absprache eigentlich liegt, "
    "und frage dann meinen Bruder."
)


def _diagnosemuster(*signale: str) -> dict[str, object]:
    """Ein Diagnosemuster mit den Signalen, um die es hier geht."""

    return _gemeinsam("DP-01", "diagnostic_pattern") | {
        "muster_name": "fragmentierter_informationsfluss",
        "worum_es_geht": "Angaben liegen an verschiedenen Stellen.",
        "signale_in_der_erzaehlung": list(signale),
        "moegliche_ursachen": ["a", "b", "c"],
        "was_es_kostet": "Es kostet Aufmerksamkeit.",
        "gilt_besonders_fuer": ["A"],
        "verwechselbar_mit": [],
        "was_es_nicht_ist": "Kein Kapazitätsproblem.",
        "passende_loesungsfamilien": [],
        "klaerende_fragen": ["Wo steht es?", "Wer trägt es ein?", "Wann?"],
    }


@pytest.fixture
def goldbestand(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Ein Goldbestand aus einem Fall, dessen Erzählung wir kennen."""

    ordner = tmp_path / "gold"
    ordner.mkdir()
    ordner.joinpath("01_malerbetrieb.json").write_text(
        json.dumps(
            {"fall_id": "01_malerbetrieb", "erzaehlung": ERZAEHLUNG},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(pruefe_batch10, "GOLDBESTAND", ordner)
    return ordner


def test_a_signal_copied_from_a_narrative_is_an_error(
    batch: Path, goldbestand: Path
) -> None:
    """Fünf gleiche Wörter machen die spätere Messung wertlos.

    Wer das Wissen aus den Messfällen abschreibt, findet hinterher genau
    diese Fälle wieder und misst nichts als seine eigene Kopie. Deshalb
    Fehler, nicht Warnung.
    """

    _schreibe(
        batch,
        "02_diagnostic_patterns.jsonl",
        [_diagnosemuster("ich muss jedes Mal erst suchen")],
    )

    befund = pruefe_batch10.pruefe(batch)

    (fehler,) = [f for f in befund.fehler if "signale_in_der_erzaehlung" in f]
    assert "01_malerbetrieb" in fehler
    assert "ich muss jedes mal erst suchen" in fehler


def test_a_signal_in_its_own_words_passes(
    batch: Path, goldbestand: Path
) -> None:
    """Die Gegenprobe: Dasselbe Thema, eigene Worte — das ist der Sinn.

    Vier gemeinsame Wörter treffen sich in zwei Texten über denselben
    Alltag von allein. Erst bei fünf ist es abgeschrieben.
    """

    _schreibe(
        batch,
        "02_diagnostic_patterns.jsonl",
        [
            _diagnosemuster(
                "ich muss jedes Mal nachfragen",
                "keiner weiß, was vereinbart wurde",
            )
        ],
    )

    befund = pruefe_batch10.pruefe(batch)

    assert [f for f in befund.fehler if "signale_in_der_erzaehlung" in f] == []
    assert befund.signale_geprueft == 2


def test_other_quotation_marks_do_not_hide_the_copy(
    batch: Path, goldbestand: Path
) -> None:
    """Normalisiert wird wie bei der Zitatprüfung."""

    _schreibe(
        batch,
        "02_diagnostic_patterns.jsonl",
        [_diagnosemuster("„Ich muss jedes Mal erst suchen“")],
    )

    befund = pruefe_batch10.pruefe(batch)

    assert any("signale_in_der_erzaehlung" in f for f in befund.fehler)


def test_the_missing_second_file_is_no_obstacle(
    batch: Path, goldbestand: Path
) -> None:
    """Datei 2 gibt es noch nicht — geprüft wird trotzdem, nur nichts."""

    _schreibe(batch, "03_solution_families.jsonl", [_solution_family("SF-01")])
    _schreibe(batch, "04_automation_capabilities.jsonl", [_capability("CAP-01")])

    befund = pruefe_batch10.pruefe(batch)

    assert befund.fehler == []
    assert befund.signale_geprueft == 0
    assert any(eintrag.startswith("02") for eintrag in befund.fehlende_dateien)


def test_a_check_that_could_not_check_says_so(
    batch: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ohne Erzählungen liefe die Prüfung still durch — das wäre schlimmer.

    Ein leerer oder verschobener Goldbestand darf nicht wie ein sauberer
    Batch aussehen.
    """

    monkeypatch.setattr(
        pruefe_batch10, "GOLDBESTAND", tmp_path / "gibt-es-nicht"
    )
    _schreibe(
        batch,
        "02_diagnostic_patterns.jsonl",
        [_diagnosemuster("irgendein Signal in eigenen Worten")],
    )

    befund = pruefe_batch10.pruefe(batch)

    assert any("Goldbestand" in f for f in befund.fehler)


def test_the_real_gold_narratives_are_readable() -> None:
    """Die zwölf Fälle müssen sich lesen lassen, sonst prüft nichts."""

    gefunden = pruefe_batch10.erzaehlungen()

    assert len(gefunden) == 12
    assert all(folgen for folgen in gefunden.values())
