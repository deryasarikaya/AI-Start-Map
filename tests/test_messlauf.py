"""Der Trockenlauf des Messskripts.

Kein Modellaufruf. Geprüft wird, dass die beiden Schalter wirklich schalten
und wieder aufräumen, und dass die Wortlautprüfung wörtliche Übernahmen
findet.

Ein Messskript, dessen Schalter nicht schalten, misst zweimal dasselbe und
sagt es nicht.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import messlauf  # noqa: E402

from app import rag_service  # noqa: E402


# --- Die zwei Schalter ----------------------------------------------------


def test_the_retrieval_switch_hides_the_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Abruf aus heisst: den Index beiseite, für die Dauer des Laufs."""

    index = tmp_path / "solution_architecture_index"
    index.mkdir()
    (index / "knowledge.faiss").write_bytes(b"tut so")
    monkeypatch.setattr(
        rag_service, "SOLUTION_ARCHITECTURE_INDEX_DIRECTORY", index
    )

    with messlauf.konfiguriert(abruf=False, prompt="ergebnis_teil1"):
        assert not index.is_dir()
        # Und der Abruf liefert damit nichts, ohne dass Code geändert wurde.
        assert rag_service.retrieve_solution_context("Etwas").all_chunks() == []

    assert index.is_dir(), "Der Index muss danach wieder dastehen"


def test_the_index_returns_even_if_the_run_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ein gescheiterter Lauf darf den Index nicht verschwinden lassen."""

    index = tmp_path / "solution_architecture_index"
    index.mkdir()
    monkeypatch.setattr(
        rag_service, "SOLUTION_ARCHITECTURE_INDEX_DIRECTORY", index
    )

    with pytest.raises(RuntimeError):
        with messlauf.konfiguriert(abruf=False, prompt="ergebnis_teil1"):
            raise RuntimeError("etwas ging schief")

    assert index.is_dir()


def test_the_prompt_switch_reaches_the_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prompt B muss beim Aufruf ankommen, nicht nur in einer Variablen stehen."""

    from app import openai_service

    monkeypatch.delenv("OPENAI_RESULT_PROMPT", raising=False)
    assert openai_service._result_prompt_name() == "ergebnis_teil1"

    with messlauf.konfiguriert(abruf=True, prompt="ergebnis_teil1_schlank"):
        assert openai_service._result_prompt_name() == "ergebnis_teil1_schlank"

    assert openai_service._result_prompt_name() == "ergebnis_teil1"


def test_both_prompt_versions_exist_and_differ() -> None:
    """Fassung B ist wirklich schlanker — sonst misst Lauf 3 nichts."""

    from app.openai_service import _prompt

    voll = _prompt("ergebnis_teil1")
    schlank = _prompt("ergebnis_teil1_schlank")

    assert len(schlank) < len(voll) / 1.5
    # Die fünf harten Zusicherungen stehen in beiden.
    for zusicherung in (
        "Erfinde keine Fakten",
        "wörtlich in der\nErzählung stehen",
        "Keine Zeit- oder Geldersparnis",
        "Du lieferst ausschließlich Daten",
        "ausdrücklich ausgeschlossen hat, steht nie auf `jetzt`",
    ):
        assert zusicherung in voll, zusicherung
        assert zusicherung in schlank, zusicherung
    # Das Kalibrierende steht nur in A.
    for geruest in (
        "höchstens fünfzehn Wörter",
        "Digitaler Schüler- und Ausbildungs-Hub",
        "Höchstens drei Gruppen",
        "Beschriftung eines Knopfes",
    ):
        assert geruest in voll, geruest
        assert geruest not in schlank, geruest


# --- Die Wortlautprüfung --------------------------------------------------


def test_a_copied_phrase_from_the_retrieved_knowledge_is_found() -> None:
    """Die wichtigste Erhebung des Messskripts."""

    ergebnis = {
        "kurzfassung": {
            "loesungsname": (
                "Ein schlanker zentraler Ort, der eingehende Nachrichten "
                "einem Objekt zuordnet"
            )
        }
    }
    wissen = [
        "kundennaher_name: Ein schlanker zentraler Ort, der eingehende "
        "Nachrichten einem Objekt zuordnet und Dokumente anhängt"
    ]

    gefunden = messlauf.uebernommene_wendungen(ergebnis, wissen)

    assert gefunden
    assert "schlanker zentraler ort" in gefunden[0]


def test_a_shorter_overlap_is_not_counted() -> None:
    """Sieben gemeinsame Wörter sind noch kein Abschreiben, acht schon."""

    sieben = "eins zwei drei vier fünf sechs sieben"

    assert messlauf.uebernommene_wendungen({"a": sieben}, [sieben]) == []
    assert messlauf.uebernommene_wendungen({"a": sieben + " acht"}, [sieben + " acht"])


def test_different_dashes_do_not_hide_a_copy() -> None:
    """Dieselbe Normalisierung wie die Zitatprüfung — sonst rutscht es durch."""

    quelle = "der eingehende E-Mails einem Vorgang zuordnet und Dokumente anhängt"
    ergebnis = {"a": "der eingehende E‑Mails einem Vorgang zuordnet und Dokumente anhängt"}

    assert messlauf.uebernommene_wendungen(ergebnis, [quelle])


def test_without_retrieved_knowledge_nothing_is_flagged() -> None:
    """Ohne Abruf gibt es keine Quelle, aus der abgeschrieben werden könnte."""

    assert messlauf.uebernommene_wendungen({"a": "Irgendein Text"}, []) == []


# --- Ein ganzer Lauf, mit Attrappe ----------------------------------------


class _Attrappe:
    """Tut so, als wäre sie die Anwendung. Ruft nichts und kostet nichts."""

    def __init__(self) -> None:
        self.cookies: dict[str, str] = {}
        self.aufrufe: list[str] = []

    def post(self, pfad: str, **_kwargs: object) -> _Attrappe:
        self.aufrufe.append(pfad)
        return self

    @property
    def status_code(self) -> int:
        return 200


def _ergebnis() -> dict:
    return {
        "kurzfassung": {
            "loesungsname": "Zentrale Auftragsstelle",
            "engpass_satz": "Aufträge werden nirgends festgehalten",
        },
        "module": [
            {"gruppe": "Eingang", "name": "Auftragsaufnahme", "stufe": "jetzt"},
            {"gruppe": "Eingang", "name": "Einordnung", "stufe": "danach"},
            {"gruppe": "Arbeit", "name": "Vorgangsakte", "stufe": "spaeter"},
        ],
    }


def test_a_whole_run_collects_what_the_plan_asks_for(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Alles aus „Was je Lauf berichtet wird" landet in der Messung."""

    monkeypatch.setattr(messlauf, "_gespeichert", lambda _client: _ergebnis())
    monkeypatch.setattr(messlauf, "_abgerufenes_wissen", lambda _text: [])
    monkeypatch.setattr(messlauf, "_prompt_zeichen", lambda *_a: 12345)

    messung = messlauf.einen_lauf(
        _Attrappe(),
        "1a",
        "malerbetrieb",
        abruf=False,
        prompt="ergebnis_teil1",
        mitschrift=messlauf.Mitschrift(),
    )

    assert messung.geschafft is True
    assert messung.loesungsname == "Zentrale Auftragsstelle"
    assert messung.modulanzahl == 3
    assert messung.gruppen == ["Arbeit", "Eingang"]
    assert messung.stufe_jetzt == ["Auftragsaufnahme"]
    assert messung.engpass_woerter == 4
    assert messung.prompt_zeichen == 12345
    # Das ganze Ergebnis bleibt erhalten — für die qualitative Durchsicht,
    # die keine Kennzahl ersetzt.
    assert messung.ergebnis == _ergebnis()


def test_a_run_skips_the_agent_step(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sonst käme ein dritter Aufruf dazwischen und die Läufe wären ungleich."""

    monkeypatch.setattr(messlauf, "_gespeichert", lambda _client: _ergebnis())
    monkeypatch.setattr(messlauf, "_abgerufenes_wissen", lambda _text: [])
    monkeypatch.setattr(messlauf, "_prompt_zeichen", lambda *_a: 0)
    attrappe = _Attrappe()

    messlauf.einen_lauf(
        attrappe, "1a", "malerbetrieb", abruf=False,
        prompt="ergebnis_teil1", mitschrift=messlauf.Mitschrift(),
    )

    assert "/verstanden" in attrappe.aufrufe
    assert attrappe.aufrufe.count("/analyze") == 2


def test_the_log_is_read_for_seconds_and_counts() -> None:
    """Dauer und Aufrufzahl hängen an diesen Protokollzeilen."""

    mitschrift = messlauf.Mitschrift()

    class _Zeile:
        def __init__(self, text: str) -> None:
            self._text = text

        def getMessage(self) -> str:
            return self._text

    mitschrift.emit(
        _Zeile(
            "solution_architecture.retrieved seconds=1.42 betriebsart=['A'] "
            "business_pattern=1 diagnostic_pattern=3 solution_family=4 "
            "automation_capability=6 target_architecture=1 gesamt=15"
        )
    )
    mitschrift.emit(
        _Zeile(
            "openai.structured_output.response section=ResultPartOne call=1 "
            "status=200 duration_seconds=23.500"
        )
    )
    mitschrift.emit(_Zeile("result.generated session=1 runden=1 teil2_seconds=9.0 openai_calls=2"))

    assert mitschrift.abruf_sekunden == 1.42
    assert mitschrift.abgerufene_abschnitte == 15
    assert mitschrift.aufruf_eins_sekunden == [23.5]
    assert mitschrift.modellaufrufe == "2"


def test_the_overview_names_both_configurations() -> None:
    """Die Übersicht muss zeigen, was gegeneinander stand."""

    messungen = [
        messlauf.Messung(
            kennung="3a", fall="malerbetrieb", abruf=True, prompt="ergebnis_teil1",
            geschafft=True, loesungsname="Eins", modulanzahl=6, gruppen=["A", "B"],
            stufe_jetzt=["Auftragsaufnahme"], engpass_satz="Kurz", engpass_woerter=1,
        ),
        messlauf.Messung(
            kennung="3b", fall="malerbetrieb", abruf=True,
            prompt="ergebnis_teil1_schlank", geschafft=False,
            ursache="Aufruf 1: 503",
        ),
    ]

    text = messlauf.berichte(messungen)

    assert "| 3a | malerbetrieb | an | A |" in text
    assert "| 3b | malerbetrieb | an | B |" in text
    assert "Aufruf 1: 503" in text
    assert "Durchgekommen: 1 von 2" in text


def test_every_case_of_the_plan_has_its_narrative() -> None:
    """Alle vier Konfigurationen lesen aus einer Quelle."""

    import json

    for pfad in messlauf.FAELLE.values():
        assert pfad.is_file(), pfad
        # Der Goldbestand ist die einzige Quelle: Was gemessen wird,
        # ist derselbe Text, gegen den bewertet wird.
        fall = json.loads(pfad.read_text(encoding="utf-8"))
        assert fall["erzaehlung"].strip(), pfad


def test_the_runs_of_the_plan_are_complete() -> None:
    """Drei Läufe, acht Konfigurationen — und Lauf 3 hält den Abruf gleich."""

    assert set(messlauf.LAEUFE) == {"1", "2", "3"}
    dritter = messlauf.LAEUFE["3"]
    assert len(dritter) == 4
    # Sonst misst man zwei Dinge auf einmal.
    assert len({abruf for _k, _f, abruf, _p in dritter}) == 1
    assert {prompt for _k, _f, _a, prompt in dritter} == {
        "ergebnis_teil1",
        "ergebnis_teil1_schlank",
    }
