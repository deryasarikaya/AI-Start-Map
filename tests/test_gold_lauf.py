"""Der Trockenlauf des Goldläufers.

**Ohne diesen Test weiss niemand, ob die Zahlen stimmen** — und eine falsche
Kennzahl ist schlimmer als keine. Deshalb zwei erfundene Fälle mit bekannter
Antwort: einer, der bestehen muss, und einer, der durchfallen muss.

Kein Modellaufruf. Die Anwendung wird durch eine Attrappe ersetzt, die ein
festes Ergebnis zurückgibt.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import gold_lauf  # noqa: E402

GOLD = Path(__file__).resolve().parents[1] / "knowledge/evaluation/gold"


def _ergebnis(
    loesungsname: str,
    module: list[str],
    *,
    jetzt: list[str] | None = None,
    **weitere: object,
) -> dict:
    """Ein Ergebnis, wie die Anwendung es speichert — nur die Felder, die zählen.

    Die Stufe steht am Modul. Ohne ausdrückliche Angabe trägt das erste Modul
    `jetzt`; der Fehlstart misst genau gegen diese Stufe und nicht gegen das
    ganze Ergebnis.
    """

    erster_schritt = module[:1] if jetzt is None else jetzt

    def stufe(name: str, platz: int) -> str:
        if name in erster_schritt:
            return "jetzt"
        return "danach" if platz < 3 else "spaeter"

    return {
        "kurzfassung": {"loesungsname": loesungsname},
        "module": [
            {"name": name, "gruppe": "Eine Gruppe", "stufe": stufe(name, platz)}
            for platz, name in enumerate(module)
        ],
        **weitere,
    }


DER_GUTE_FALL = {
    "fall_id": "test_gut",
    "titel": "Ein Fall, der bestehen muss",
    "erzaehlung": "Wir sind zu dritt und suchen ständig Unterlagen zusammen.",
    "bewertung": {
        "startpunkt": "verbundenes_system",
        "module_anzahl_von": 3,
        "module_anzahl_bis": 5,
        "muss_vorkommen": ["Vorgang"],
        "darf_nicht_vorkommen": ["Portal", "Marketing"],
        "betriebsart": ["G"],
    },
}

DER_SCHLECHTE_FALL = {
    "fall_id": "test_schlecht",
    "titel": "Ein Fall, der durchfallen muss",
    "erzaehlung": "Ich bin Maler und schreibe mir nichts auf.",
    "bewertung": {
        "startpunkt": "aufbau",
        "module_anzahl_von": 0,
        "module_anzahl_bis": 3,
        "muss_vorkommen": ["Notiz"],
        "darf_nicht_vorkommen": ["Portal"],
        "betriebsart": ["A"],
    },
}


# --- Der gute Fall besteht ------------------------------------------------


def test_a_good_case_passes_every_measure() -> None:
    """Alles richtig: Grösse passt, nichts Verbotenes, Pflichtbegriff da."""

    treffer = gold_lauf.bewerte_fall(
        DER_GUTE_FALL,
        _ergebnis(
            "Vorgangszentrale",
            ["Vorgangsakte", "Posteingang", "Übersicht"],
            jetzt=["Vorgangsakte", "Posteingang"],
        ),
        sekunden=42.0,
    )

    assert treffer.durchgekommen is True
    assert treffer.fehlstart == []
    assert treffer.fehlende_pflichtbegriffe == []
    assert treffer.groesse_passt is True
    assert treffer.startpunkt_passt is True
    assert treffer.abgeschrieben == []


# --- Der schlechte Fall fällt durch, und zwar an jeder einzelnen Stelle ----


def test_a_false_start_is_caught() -> None:
    """Die eine Zahl, die zählt: Als **erster Schritt** steht etwas Falsches."""

    treffer = gold_lauf.bewerte_fall(
        DER_SCHLECHTE_FALL,
        _ergebnis("Vorgangszentrale", ["Portal für Kunden", "Auftragsliste"]),
    )

    assert treffer.fehlstart == ["Portal"]


def test_a_forbidden_module_later_in_the_order_is_no_false_start() -> None:
    """Ein Portal darf im Zielbild stehen — nur nicht als erster Schritt.

    Genau hier hat sich die Kennzahl geändert: Früher hätte das ganze Ergebnis
    als überzogen gegolten. Jeder Betrieb bekommt jetzt das vollständige Bild;
    falsch wäre nur der Anfang.
    """

    treffer = gold_lauf.bewerte_fall(
        DER_SCHLECHTE_FALL,
        _ergebnis(
            "Vorgangszentrale",
            ["Zettelersatz", "Auftragsliste", "Portal für Kunden"],
            jetzt=["Zettelersatz"],
        ),
    )

    assert treffer.fehlstart == []
    assert "Portal für Kunden" in treffer.modulnamen


def test_a_wrong_size_is_caught() -> None:
    """Vier Module sprengen die hinterlegte Spanne von null bis drei."""

    treffer = gold_lauf.bewerte_fall(
        DER_SCHLECHTE_FALL,
        _ergebnis("Irgendwas", ["Eins", "Zwei", "Drei", "Vier"]),
    )

    assert treffer.groesse_passt is False


def test_a_wrong_starting_point_is_caught() -> None:
    """Der Fall steht auf `aufbau` — dann ist genau ein erster Schritt richtig.

    Gemessen wird nicht mehr, ob eine Empfehlung ausbleibt, sondern ob der
    Anfang zur Ausgangslage passt.
    """

    treffer = gold_lauf.bewerte_fall(
        DER_SCHLECHTE_FALL,
        _ergebnis("Irgendwas", ["Eins", "Zwei"], jetzt=["Eins", "Zwei"]),
    )

    assert treffer.startpunkt_passt is False


def test_a_missing_required_word_is_caught() -> None:
    treffer = gold_lauf.bewerte_fall(
        DER_SCHLECHTE_FALL, _ergebnis("Irgendwas", ["Eins"])
    )

    assert treffer.fehlende_pflichtbegriffe == ["Notiz"]


def test_a_matching_starting_point_passes() -> None:
    """Ein einzelner erster Schritt passt zu `aufbau`."""

    treffer = gold_lauf.bewerte_fall(
        DER_SCHLECHTE_FALL,
        _ergebnis("Irgendwas", ["Eins", "Zwei"], jetzt=["Eins"]),
    )

    assert treffer.startpunkt_passt is True


# --- Die Abschreibquote ---------------------------------------------------


def test_a_copied_phrase_is_found() -> None:
    """Genau das ist schon passiert — ein Name kam wörtlich aus dem Prompt."""

    gefunden = gold_lauf.abgeschriebene_wendungen(
        json.dumps(
            _ergebnis("Digitaler Kunden- und Auftrags-Hub", ["Eins"]),
            ensure_ascii=False,
        ),
        ["Beispiele: Digitaler Kunden- und Auftrags-Hub, Zentrale Vorgangsakte"],
    )

    assert gefunden == ["digitaler kunden und auftrags hub"]


def test_a_short_overlap_is_not_counted() -> None:
    """Vier gemeinsame Wörter sind Zufall, fünf nicht mehr."""

    gefunden = gold_lauf.abgeschriebene_wendungen(
        "Eine zentrale Übersicht für alles",
        ["Eine zentrale Übersicht für"],
    )

    assert gefunden == []


def test_the_narrative_is_not_a_source_of_copying() -> None:
    """Aus der Erzählung zu zitieren ist erwünscht und wird sogar erzwungen."""

    quellen = gold_lauf.abgeschriebene_wendungen(
        "Mieter melden Schäden per Telefon und per Mail",
        [],
    )

    assert quellen == []


# --- Die Kennzahlen über den ganzen Lauf ----------------------------------


def test_the_metrics_over_a_whole_run() -> None:
    """Ein Lauf aus einem guten und einem schlechten Fall, von Hand nachgerechnet."""

    ergebnisse = [
        gold_lauf.bewerte_fall(
            DER_GUTE_FALL,
            _ergebnis(
                "Vorgangszentrale",
                ["Vorgangsakte", "Posteingang", "Übersicht"],
                jetzt=["Vorgangsakte", "Posteingang"],
            ),
            sekunden=40.0,
        ),
        gold_lauf.bewerte_fall(
            DER_SCHLECHTE_FALL,
            _ergebnis(
                "Vorgangszentrale",
                ["Portal für Kunden", "Auftragsliste", "Drei", "Vier"],
                jetzt=["Portal für Kunden", "Auftragsliste"],
            ),
            sekunden=60.0,
        ),
    ]

    kennzahlen = gold_lauf.bewerte_lauf(ergebnisse)

    # Einer von zwei hat etwas Verbotenes: die Hälfte.
    assert kennzahlen["fehlstart_quote"] == 0.5
    assert kennzahlen["groessentreffer"] == 0.5
    assert kennzahlen["startpunkt_treffer"] == 0.5
    assert kennzahlen["pflichtbegriffe"] == 0.5
    assert kennzahlen["durchkommensquote"] == 1.0
    assert kennzahlen["sekunden_schnellster"] == 40.0
    assert kennzahlen["sekunden_langsamster"] == 60.0


def test_an_unfilled_field_is_left_out_instead_of_guessed() -> None:
    """Ein Feld ohne hinterlegte Referenzantwort wird nicht bewertet.

    Eine erfundene Bewertung wäre schlimmer als eine fehlende.
    """

    ohne_bewertung = {
        "fall_id": "test_leer",
        "titel": "Noch nicht ausgefüllt",
        "erzaehlung": "Etwas.",
        "bewertung": {
            "startpunkt": None,
            "module_anzahl_von": None,
            "module_anzahl_bis": None,
            "muss_vorkommen": [],
            "darf_nicht_vorkommen": [],
        },
    }

    treffer = gold_lauf.bewerte_fall(ohne_bewertung, _ergebnis("Irgendwas", ["Eins"]))
    kennzahlen = gold_lauf.bewerte_lauf([treffer])

    assert treffer.groesse_passt is None
    assert treffer.startpunkt_passt is None
    assert kennzahlen["groessentreffer"] is None
    assert kennzahlen["groessentreffer_basis"] == 0
    # Der Fehlstart ist trotzdem bestimmbar: nichts verboten, nichts gefunden.
    assert kennzahlen["fehlstart_quote"] == 0.0


# --- Der Läufer selbst, mit Attrappe --------------------------------------


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


def test_the_runner_skips_cases_without_a_narrative(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ein halber Bestand ist messbar — die fehlenden werden benannt."""

    attrappe = _Attrappe()
    monkeypatch.setattr(
        gold_lauf, "_gespeichert", lambda _client: _ergebnis("Etwas", ["Eins"])
    )
    monkeypatch.setattr(gold_lauf, "_prompt_quellen", lambda _erzaehlung: [])

    ergebnisse = gold_lauf.fahre_lauf(
        [DER_GUTE_FALL, {"fall_id": "test_leer", "titel": "Leer", "erzaehlung": ""}],
        client=attrappe,
    )

    assert [e.fall_id for e in ergebnisse] == ["test_gut", "test_leer"]
    assert ergebnisse[1].durchgekommen is False
    assert "keine Erzählung" in ergebnisse[1].ursache
    # Für den leeren Fall wurde nichts gerufen — also auch nichts bezahlt.
    assert attrappe.aufrufe.count("/analyze") == 2


def test_the_runner_skips_the_agent_step(monkeypatch: pytest.MonkeyPatch) -> None:
    """Damit die Fälle vergleichbar bleiben und kein dritter Aufruf kommt."""

    attrappe = _Attrappe()
    monkeypatch.setattr(
        gold_lauf, "_gespeichert", lambda _client: _ergebnis("Etwas", ["Eins"])
    )
    monkeypatch.setattr(gold_lauf, "_prompt_quellen", lambda _erzaehlung: [])

    gold_lauf.fahre_lauf([DER_GUTE_FALL], client=attrappe)

    assert "/verstanden" in attrappe.aufrufe
    assert attrappe.aufrufe.count("/analyze") == 2


# --- Der Vergleich zweier Läufe -------------------------------------------


def test_two_runs_are_compared_in_the_right_direction(tmp_path: Path) -> None:
    """Bei der Over-Solution Rate ist weniger besser, bei den anderen mehr."""

    vorher, nachher = tmp_path / "gold_A", tmp_path / "gold_B"
    for ordner, werte in (
        (vorher, {"fehlstart_quote": 0.5, "groessentreffer": 0.4}),
        (nachher, {"fehlstart_quote": 0.2, "groessentreffer": 0.8}),
    ):
        ordner.mkdir()
        (ordner / "kennzahlen.json").write_text(
            json.dumps(werte), encoding="utf-8"
        )

    tabelle = gold_lauf.vergleiche(vorher, nachher)

    assert "| fehlstart_quote | 50 % | 20 % | besser |" in tabelle
    assert "| groessentreffer | 40 % | 80 % | besser |" in tabelle


# --- Der echte Goldbestand ------------------------------------------------


def test_every_gold_file_has_the_full_structure() -> None:
    """Alle dreizehn Dateien haben dieselben Felder — nur eingesetzt wird noch.

    Fall 13 ist mit Schritt 8 dazugekommen. `darf_nirgends_vorkommen` gilt
    für **alle** Textfelder, nicht nur für den ersten Schritt: Ein Portal
    darf im Zielbild stehen und nur nicht sofort kommen — ein Ratschlag zu
    einem Thema, nach dem niemand gefragt hat, darf nirgends stehen.
    """

    faelle = gold_lauf.lade_faelle(GOLD)

    assert len(faelle) == 13
    for fall in faelle:
        assert set(fall) == {"fall_id", "titel", "erzaehlung", "quelle", "bewertung"}
        assert set(fall["bewertung"]) == {
            "engpass_in_einem_satz",
            "startpunkt",
            "module_anzahl_von",
            "module_anzahl_bis",
            "muss_vorkommen",
            "darf_nicht_vorkommen",
            "darf_nirgends_vorkommen",
            "betriebsart",
            "notiz",
        }


def test_the_starting_point_only_holds_known_values() -> None:
    """`startpunkt` ist leer oder einer von drei Werten — nie ein Tippfehler.

    Geprueft wird der Wertebereich, nicht die Leere: Eine fruehere Fassung
    verlangte, dass **alle** Bewertungsfelder leer sind. Das war als
    einmalige Zusicherung gedacht und stand dem Eintragen der
    Referenzantworten im Weg.
    """

    for fall in gold_lauf.lade_faelle(GOLD):
        startpunkt = fall["bewertung"]["startpunkt"]
        assert startpunkt is None or startpunkt in gold_lauf.STARTPUNKTE, (
            fall["fall_id"],
            startpunkt,
        )


def test_every_case_has_a_narrative() -> None:
    """Die zwölf gelieferten Fälle sind messbar.

    Fall 13 wartet noch auf seine Erzählung. Er ist der einzige, der fehlen
    darf; jeder weitere leere Fall wäre ein Fehler und keine Wartezeit.
    """

    faelle = gold_lauf.lade_faelle(GOLD)
    ohne = [f["fall_id"] for f in faelle if not f["erzaehlung"].strip()]

    assert ohne in ([], ["13_massagesalon"]), ohne
    for fall in faelle:
        assert fall["quelle"].strip(), fall["fall_id"]


def test_no_case_appears_twice() -> None:
    """Zwölf Kennungen, zwölf verschiedene Erzählungen.

    Beim Einsetzen der gelieferten Fälle hiessen die Dateien anders als hier.
    Ein Kopierfehler haette zwei Faelle mit demselben Text erzeugt — und die
    Kennzahlen still verzerrt.
    """

    faelle = gold_lauf.lade_faelle(GOLD)

    assert len({fall["fall_id"] for fall in faelle}) == len(faelle)
    assert len({fall["erzaehlung"] for fall in faelle}) == len(faelle)

# --- Was nirgends stehen darf ---------------------------------------------


DER_SALON = {
    "fall_id": "13_massagesalon",
    "titel": "Ein Betrieb, der nach etwas anderem gefragt hat",
    "erzaehlung": "Wir arbeiten mit zwei Standorten und viel Laufkundschaft.",
    "bewertung": {
        "darf_nicht_vorkommen": ["Kartenzahlung", "Bargeld"],
        "darf_nirgends_vorkommen": ["Kartenzahlung", "Bargeld"],
        "betriebsart": ["C"],
    },
}


def test_a_lecture_anywhere_in_the_result_is_found() -> None:
    """Der Fehlstart schaut nur auf `jetzt` — diese Prüfung auf alles.

    Der Betrieb zahlt bewusst bar. Ein gut gemeinter Hinweis dazu ist eine
    Belehrung, egal in welchem Abschnitt er steht — und er beschädigt den
    Rest der Auswertung.
    """

    treffer = gold_lauf.bewerte_fall(
        DER_SALON,
        _ergebnis(
            "Terminzentrale",
            ["Terminannahme", "Auslastung", "Erinnerung"],
            warum_diese_loesung=(
                "Eine Kartenzahlung würde Ihnen die Abrechnung erleichtern."
            ),
        ),
    )

    assert treffer.belehrung == ["Kartenzahlung"]
    # Und der Fehlstart bleibt sauber: Auf `jetzt` steht nichts Verbotenes.
    assert treffer.fehlstart == []


def test_a_result_that_keeps_quiet_is_clean() -> None:
    """Die Gegenprobe: Wer nichts dazu sagt, wird nicht bestraft."""

    treffer = gold_lauf.bewerte_fall(
        DER_SALON,
        _ergebnis("Terminzentrale", ["Terminannahme", "Auslastung"]),
    )

    assert treffer.belehrung == []


def test_the_other_cases_do_not_forbid_anything_everywhere() -> None:
    """Für die zwölf anderen Fälle bleibt die Liste leer.

    Sonst würde ein Begriff, der im Zielbild stehen darf, plötzlich überall
    verboten — das ist eine andere Frage als die nach dem ersten Schritt.
    """

    for fall in gold_lauf.lade_faelle(GOLD):
        if fall["fall_id"] == "13_massagesalon":
            continue
        assert fall["bewertung"]["darf_nirgends_vorkommen"] == [], fall["fall_id"]


def test_the_lecture_rate_is_reported() -> None:
    """Zwei Fragen, zwei Zahlen — die Quote steht neben dem Fehlstart."""

    mit = gold_lauf.bewerte_fall(
        DER_SALON,
        _ergebnis(
            "Terminzentrale",
            ["Terminannahme", "Auslastung"],
            warum_diese_loesung="Denken Sie an die Kartenzahlung.",
        ),
    )
    ohne = gold_lauf.bewerte_fall(
        DER_SALON,
        _ergebnis("Terminzentrale", ["Terminannahme", "Auslastung"]),
    )

    kennzahlen = gold_lauf.bewerte_lauf([mit, ohne])

    assert kennzahlen["belehrungsquote"] == 0.5
    assert kennzahlen["belehrungsbasis"] == 2
    assert "Belehrungsquote" in gold_lauf.berichte([mit, ohne], kennzahlen)

def test_the_runner_stops_at_its_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    """Angehalten wird vor einem Fall, nicht mittendrin.

    Ohne Mitzaehlen ist die Grenze nicht einzuhalten: geplant 22 Aufrufe,
    verbraucht 30. Ein abgebrochener Durchlauf hat Kosten verursacht und
    liefert nichts — deshalb wird vorher entschieden.
    """

    attrappe = _Attrappe()
    monkeypatch.setattr(
        gold_lauf, "_gespeichert", lambda _client: _ergebnis("Etwas", ["Eins"])
    )
    monkeypatch.setattr(gold_lauf, "_prompt_quellen", lambda _erzaehlung: [])

    zweiter = {**DER_SCHLECHTE_FALL}
    ergebnisse = gold_lauf.fahre_lauf(
        [DER_GUTE_FALL, zweiter], client=attrappe, hoechstens=0
    )

    assert all(not e.durchgekommen for e in ergebnisse)
    assert all("Budget" in e.ursache for e in ergebnisse)
    # Kein einziger Aufruf — auch nicht der erste.
    assert attrappe.aufrufe.count("/analyze") == 0


def test_the_counter_does_not_silence_the_log(monkeypatch: pytest.MonkeyPatch) -> None:
    """Der Zaehler haengt am `app`-Logger — und darf ihn nicht stummschalten.

    Sobald ein Handler am Logger haengt, greift Pythons `lastResort` nicht
    mehr. Der Zaehler allein verschluckt dadurch jede Warnung und jeden
    Fehler; das Protokoll bleibt leer, obwohl Aufrufe wiederholt werden.
    """

    import logging

    attrappe = _Attrappe()
    monkeypatch.setattr(
        gold_lauf, "_gespeichert", lambda _client: _ergebnis("Etwas", ["Eins"])
    )
    monkeypatch.setattr(gold_lauf, "_prompt_quellen", lambda _erzaehlung: [])

    gold_lauf.fahre_lauf([DER_GUTE_FALL], client=attrappe)

    handler = logging.getLogger("app").handlers
    assert any(isinstance(h, gold_lauf.Aufrufzaehler) for h in handler)
    # Und es gibt weiterhin einen Weg nach draussen.
    assert logging.getLogger().handlers, "Ohne Wurzel-Handler bleibt alles stumm"
