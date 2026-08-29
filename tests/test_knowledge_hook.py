"""Die Anschlussstelle für das neue Wissen aus Batch 10.

Wenn der Batch fertig ist, soll das Anschließen ein Befehl sein und keine
Bauarbeit. Was hier geprüft wird, ist der Weg bis unmittelbar vor den
Einbettungsaufruf — **einbetten kostet Geld und passiert hier nicht.**

Der Abruf sucht nur oben und schlägt darunter über Kennungen nach. Genau das
ist es, was hier abgesichert wird: dass keine Lösungsfamilie auf die Seite
kommt, zu der kein Diagnosemuster geführt hat.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

from app import rag_service
from app.rag_service import KnowledgeChunk
from app.services import analysis_service

ERZAEHLT = "Mieter melden Schäden per Mail, ich suche dann lange."


def _abschnitt(kennung: str, typ: str, **metadaten: object) -> KnowledgeChunk:
    return KnowledgeChunk(
        chunk_id=kennung,
        chunk_type=typ,
        title=f"Titel {kennung}",
        content=f"Inhalt zu {kennung}",
        source_file="knowledge/candidates/batch_10/03_solution_families.jsonl",
        metadata={"batch_id": "batch_10", "source_strength": "derived", **metadaten},
    )


# --- C1: der Indexaufbau kennt den Batch ----------------------------------


def test_the_loader_reads_every_jsonl_in_the_batch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Alle fünf Dateien, nicht nur eine bestimmte."""

    ordner = tmp_path / "batch_10"
    ordner.mkdir()
    for name, kennung, typ in (
        ("03_solution_families.jsonl", "SF-01", "solution_family"),
        ("05_target_architectures.jsonl", "TA-01", "target_architecture"),
    ):
        ordner.joinpath(name).write_text(
            json.dumps(
                {
                    "chunk_id": kennung,
                    "chunk_type": typ,
                    "title": kennung,
                    "worum_es_geht": "Ein Satz dazu.",
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
    monkeypatch.setattr(rag_service, "SOLUTION_ARCHITECTURE_DIRECTORY", ordner)

    abschnitte = rag_service.load_solution_architecture_chunks()

    assert {chunk.chunk_id for chunk in abschnitte} == {"SF-01", "TA-01"}


def test_an_empty_batch_is_not_an_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ein Batch im Entstehen ist leer — das darf nichts abbrechen."""

    leer = tmp_path / "batch_10"
    leer.mkdir()
    monkeypatch.setattr(rag_service, "SOLUTION_ARCHITECTURE_DIRECTORY", leer)

    assert rag_service.load_solution_architecture_chunks() == []


def test_the_builder_walks_up_to_the_embedding_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Der ganze Weg läuft — nur das Einbetten selbst ist eine Attrappe.

    Damit ist belegt, dass am Tag mit Guthaben nichts mehr zu bauen ist.
    """

    ordner = tmp_path / "batch_10"
    ordner.mkdir()
    ordner.joinpath("03_solution_families.jsonl").write_text(
        "\n".join(
            json.dumps(
                {
                    "chunk_id": f"SF-{nummer:02d}",
                    "chunk_type": "solution_family",
                    "title": f"Familie {nummer}",
                    "worum_es_geht": "Ein Satz dazu.",
                },
                ensure_ascii=False,
            )
            for nummer in (1, 2)
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(rag_service, "SOLUTION_ARCHITECTURE_DIRECTORY", ordner)

    eingebettet: list[list[str]] = []

    def attrappe(texte: list[str]) -> list[list[float]]:
        eingebettet.append(list(texte))
        return [[0.1, 0.2, 0.3] for _ in texte]

    monkeypatch.setattr(rag_service, "embed_texts", attrappe)
    monkeypatch.setattr(rag_service, "get_embedding_model", lambda: "attrappe")

    gebaut = rag_service.build_vector_index(
        force=True,
        index_kind="architecture",
        output_directory=tmp_path / "index",
    )

    assert gebaut is True
    assert len(eingebettet[0]) == 2
    assert "Familie 1" in eingebettet[0][0]
    assert (tmp_path / "index" / rag_service.MANIFEST_FILE_NAME).is_file()


def test_an_empty_batch_is_refused_by_the_builder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ein leerer Index wäre schlimmer als keiner — er sähe fertig aus."""

    leer = tmp_path / "batch_10"
    leer.mkdir()
    monkeypatch.setattr(rag_service, "SOLUTION_ARCHITECTURE_DIRECTORY", leer)

    with pytest.raises(rag_service.RagConfigurationError, match="noch leer"):
        rag_service.build_vector_index(
            force=True,
            index_kind="architecture",
            output_directory=tmp_path / "index",
        )


# --- C2b: was in den Suchtext gehört --------------------------------------


def test_cross_references_stay_out_of_the_search_text() -> None:
    """Nach Kennungen sucht niemand — sie verwässern nur die Ähnlichkeit."""

    text = rag_service._jsonl_content(
        {
            "chunk_id": "DP-01",
            "chunk_type": "diagnostic_pattern",
            "is_primary_evidence": False,
            "process_type": ["A", "G"],
            "muster_name": "fragmentierter_informationsfluss",
            "signale_in_der_erzaehlung": ["ich muss erst suchen, wo das liegt"],
            "passende_loesungsfamilien": ["SF-01", "SF-02"],
            "verwechselbar_mit": ["DP-04"],
        }
    )

    assert "signale_in_der_erzaehlung" in text
    assert "ich muss erst suchen" in text
    assert "SF-01" not in text
    assert "DP-04" not in text
    assert "is_primary_evidence" not in text
    assert "process_type" not in text


def test_an_older_corpus_keeps_its_search_text() -> None:
    """Der Bestand darf sich nicht verändern.

    Ein älterer Datensatz kann denselben Typnamen tragen und ganz andere
    Felder haben. Dann würde die Feldliste alles wegfiltern, und der Suchtext
    wäre leer — das wäre ein stiller Datenverlust.
    """

    text = rag_service._jsonl_content(
        {
            "pattern_id": "RB03-P01",
            "pattern_type": "diagnostic_pattern",
            "diagnostic_pattern": "Physisches Objekt und Auftrag bleiben verbunden.",
            "minimal_signal": "ja",
        }
    )

    assert "diagnostic_pattern: Physisches Objekt" in text
    assert "minimal_signal: ja" in text


def test_a_content_field_still_wins() -> None:
    """Wer `content` setzt, bekommt genau das — unverändert."""

    assert (
        rag_service._jsonl_content(
            {"chunk_id": "X", "chunk_type": "solution_family", "content": " Fester Text "}
        )
        == "Fester Text"
    )


# --- C2: suchen oben, nachschlagen unten ----------------------------------


def _bestand() -> list[KnowledgeChunk]:
    """Ein kleiner Wissensbestand mit Kanten, in Ähnlichkeitsreihenfolge."""

    return [
        _abschnitt("BP-G", "business_pattern", betriebsart_buchstabe="G"),
        _abschnitt(
            "DP-01", "diagnostic_pattern", passende_loesungsfamilien=["SF-02", "SF-01"]
        ),
        _abschnitt(
            "DP-04", "diagnostic_pattern", passende_loesungsfamilien=["SF-03"]
        ),
        _abschnitt(
            "SF-02",
            "solution_family",
            braucht_capabilities=["CAP-04"],
            gilt_fuer_betriebsarten=["G"],
        ),
        _abschnitt(
            "SF-01",
            "solution_family",
            braucht_capabilities=["CAP-01", "CAP-02"],
            gilt_fuer_betriebsarten=["A", "G"],
        ),
        # Gilt nur für Terminbetriebe — darf bei Betriebsart G nicht kommen.
        _abschnitt(
            "SF-03", "solution_family", gilt_fuer_betriebsarten=["C"]
        ),
        # Semantisch ganz oben, aber kein Muster führt hin.
        _abschnitt("SF-13", "solution_family", gilt_fuer_betriebsarten=["G"]),
        _abschnitt("CAP-04", "automation_capability"),
        _abschnitt("CAP-01", "automation_capability"),
        _abschnitt("CAP-02", "automation_capability"),
        _abschnitt("TA-01", "target_architecture", enthaltene_familien=["SF-01", "SF-02"]),
        _abschnitt("TA-03", "target_architecture", enthaltene_familien=["SF-09"]),
    ]


@pytest.fixture
def mit_index(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tut so, als läge ein gebauter Index vor, ohne einzubetten."""

    monkeypatch.setattr(
        rag_service,
        "_rank_solution_architecture",
        lambda _q: rag_service.Rangergebnis(rangfolge=_bestand()),
    )
    monkeypatch.setattr(rag_service.Path, "is_file", lambda _self: True)


def test_only_two_types_are_searched(mit_index: None) -> None:
    """Gesucht wird oben, alles darunter hängt an Kennungen."""

    gefunden = rag_service.retrieve_solution_context(ERZAEHLT)

    assert [c.chunk_id for c in gefunden.betriebsarten] == ["BP-G"]
    assert [c.chunk_id for c in gefunden.diagnosemuster] == ["DP-01", "DP-04"]


def test_families_come_from_the_patterns_not_from_the_search(
    mit_index: None,
) -> None:
    """SF-13 steht semantisch weit oben — aber kein Muster führt dorthin.

    Genau das verhindert Empfehlungen ohne diagnostischen Weg: Wer viele
    E-Mails hat, bekäme sonst Marketing-Automation vorgeschlagen, weil das
    semantisch in die Nähe rückt.
    """

    gefunden = rag_service.retrieve_solution_context(ERZAEHLT)

    kennungen = [c.chunk_id for c in gefunden.loesungsfamilien]
    assert "SF-13" not in kennungen
    # Reihum: DP-01 liefert seine erste, DP-04 seine erste (die an der
    # Betriebsart scheitert), dann DP-01 seine zweite.
    assert kennungen == ["SF-02", "SF-01"]


def test_a_family_for_another_business_type_is_dropped(mit_index: None) -> None:
    """SF-03 gilt nur für Terminbetriebe, erkannt wurde aber G."""

    gefunden = rag_service.retrieve_solution_context(ERZAEHLT)

    assert "SF-03" not in [c.chunk_id for c in gefunden.loesungsfamilien]


def test_capabilities_are_looked_up_from_the_families(mit_index: None) -> None:
    """Die Fähigkeiten hängen an den Familien, nicht an der Erzählung."""

    gefunden = rag_service.retrieve_solution_context(ERZAEHLT)

    assert [c.chunk_id for c in gefunden.faehigkeiten] == ["CAP-04", "CAP-01", "CAP-02"]


def test_the_target_picture_with_the_widest_overlap_wins(mit_index: None) -> None:
    """TA-01 deckt beide Familien ab, TA-03 keine."""

    gefunden = rag_service.retrieve_solution_context(ERZAEHLT)

    assert gefunden.zielbild is not None
    assert gefunden.zielbild.chunk_id == "TA-01"


def test_nothing_is_returned_twice(mit_index: None) -> None:
    """Zwei Muster können auf dieselbe Familie zeigen."""

    gefunden = rag_service.retrieve_solution_context(ERZAEHLT)

    kennungen = [chunk.chunk_id for chunk in gefunden.all_chunks()]
    assert len(kennungen) == len(set(kennungen))


def test_the_amounts_are_named_constants() -> None:
    """Die Mischung ist eine Entscheidung, keine Zufallszahl."""

    assert set(rag_service.CHUNKS_PER_SEARCHED_TYPE) == {
        "business_pattern",
        "diagnostic_pattern",
    }
    assert rag_service.MAXIMUM_SOLUTION_FAMILIES > 0
    assert rag_service.MAXIMUM_CAPABILITIES > 0


@pytest.fixture
def ohne_index(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Zeigt auf einen Ordner, in dem kein Index liegt.

    Vorher verliessen sich die beiden Tests darauf, dass es den echten
    Index nicht gibt. Seit er gebaut ist, prüften sie nicht mehr „ohne
    Index", sondern riefen das Modell — mit ungültigem Schlüssel also einen
    401. Der Zustand „noch kein Batch indexiert" muss hergestellt werden,
    nicht vorausgesetzt.
    """

    monkeypatch.setattr(
        rag_service,
        "SOLUTION_ARCHITECTURE_INDEX_DIRECTORY",
        tmp_path / "noch-kein-index",
    )


def test_without_an_index_nothing_is_retrieved(ohne_index: None) -> None:
    """Solange kein Batch indexiert ist, wird nichts abgerufen — und nichts kaputt."""

    gefunden = rag_service.retrieve_solution_context(ERZAEHLT)

    assert gefunden.all_chunks() == []


# --- C3: der Platz im Prompt ----------------------------------------------


def test_the_prompt_section_is_empty_without_knowledge(ohne_index: None) -> None:
    """Ohne Index bleibt der Abschnitt leer, und der Lauf geht trotzdem."""

    assert analysis_service.diagnose_context(ERZAEHLT) == []


def test_a_failing_retrieval_does_not_take_the_run_down(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Hintergrundwissen ist Beiwerk. Die Erzählung ist die Grundlage."""

    def scheitert(_query: str) -> object:
        raise rag_service.RagConfigurationError("Index kaputt")

    monkeypatch.setattr(analysis_service, "retrieve_solution_context", scheitert)

    assert analysis_service.diagnose_context(ERZAEHLT) == []


def test_only_diagnostic_knowledge_reaches_the_first_call(
    mit_index: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Was abgerufen wurde, steht im Prompt — in der Reihenfolge des Wegs.

    Die Sammelattrappe aus `conftest` hält den Abruf offline, damit kein
    Test einbettet. Dieser hier will ihn — deshalb holt er die echte
    Funktion zurück; gesucht wird trotzdem nur im gemockten Bestand.
    """

    from app import rag_service

    monkeypatch.setattr(
        analysis_service,
        "retrieve_solution_context",
        rag_service.retrieve_solution_context,
    )

    aufbereitet = analysis_service.diagnose_context(ERZAEHLT)

    zusammen = "\n".join(aufbereitet)
    # Was die Diagnose einordnen hilft, kommt an.
    assert "Inhalt zu BP-G" in zusammen
    assert "Inhalt zu DP-01" in zusammen
    # **Und kein Lösungswissen.** Wer die Lösung kennt, diagnostiziert auf
    # sie hin — aus „der Kunde erwähnt Termine" würde „wir verkaufen
    # Terminbuchung".
    for loesung in ("SF-", "CAP-", "TA-"):
        assert loesung not in zusammen, loesung


def test_the_prompt_says_what_the_knowledge_is_and_is_not() -> None:
    """Die Ansage steht im Prompt, nicht nur im Kopf des Entwicklers."""

    prompt = (
        Path(__file__).resolve().parents[1] / "app/prompts/diagnose.md"
    ).read_text(encoding="utf-8")

    assert "VERGLEICHSWISSEN_DIAGNOSE_NIE_AUSGEBEN" in prompt
    assert "kein Fakt über diesen Betrieb" in prompt
    assert "tauchen in deiner Antwort nirgends" in prompt
    assert "Lösungen stehen dort nicht" in prompt


def test_the_retrieval_logs_its_seconds_and_counts(
    mit_index: None, caplog: pytest.LogCaptureFixture
) -> None:
    """Ohne diese Zahl liesse sich der Zeitanteil des Abrufs nur raten.

    Der Abruf kostet eine Einbettung plus die Suche. Bei zuletzt 43 Prozent
    Zeitabläufen ist das keine Nebensache — gemessen wird der ganze Abruf,
    die Einbettung eingeschlossen.
    """

    caplog.set_level(logging.INFO)
    rag_service.retrieve_solution_context(ERZAEHLT)

    (zeile,) = [
        eintrag.getMessage()
        for eintrag in caplog.records
        if eintrag.getMessage().startswith("solution_architecture.retrieved")
    ]
    assert "seconds=" in zeile
    # Je Wissenstyp die Anzahl, damit im Bericht steht, was der Abruf gefunden
    # hat und nicht nur, dass er lief.
    for typ in (
        "business_pattern=1",
        "diagnostic_pattern=2",
        "solution_family=2",
        "automation_capability=3",
        "target_architecture=1",
    ):
        assert typ in zeile, zeile
    assert "gesamt=9" in zeile

def test_every_pattern_contributes_a_family(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reihum, nicht der Reihe nach — sonst zaehlt nur das erste Muster.

    Der Reihe nach nimmt die Schleife alles, was das erstplatzierte Muster
    nennt, bis die Grenze voll ist. DP-06 fuehrt fuenf Familien; liegt die
    Grenze bei vier, werden Muster zwei und drei gesucht, gerankt und
    protokolliert — und tragen nichts bei. Malerbetrieb und
    450-Einheiten-Verwaltung bekaemen dieselben vier Familien.
    """

    bestand = [
        _abschnitt("BP-G", "business_pattern", betriebsart_buchstabe="G"),
        _abschnitt(
            "DP-01",
            "diagnostic_pattern",
            passende_loesungsfamilien=["SF-01", "SF-02", "SF-03", "SF-04"],
        ),
        _abschnitt(
            "DP-04", "diagnostic_pattern", passende_loesungsfamilien=["SF-05"]
        ),
    ]
    bestand += [
        _abschnitt(
            f"SF-0{nummer}", "solution_family", gilt_fuer_betriebsarten=["G"]
        )
        for nummer in range(1, 6)
    ]
    monkeypatch.setattr(
        rag_service,
        "_rank_solution_architecture",
        lambda _q: rag_service.Rangergebnis(rangfolge=bestand),
    )
    monkeypatch.setattr(rag_service.Path, "is_file", lambda _self: True)

    gefunden = rag_service.retrieve_solution_context(ERZAEHLT)

    kennungen = [c.chunk_id for c in gefunden.loesungsfamilien]
    # Das zweite Muster kommt an zweiter Stelle zum Zug, nicht als letztes.
    assert kennungen[:2] == ["SF-01", "SF-05"]
    assert "SF-05" in kennungen


def test_six_families_fit_a_target_picture() -> None:
    """Sechs, nicht vier. Vier war eine Zahl ohne Begruendung."""

    assert rag_service.MAXIMUM_SOLUTION_FAMILIES == 6
