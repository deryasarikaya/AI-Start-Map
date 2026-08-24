"""Fährt vier Konfigurationen gegeneinander: Abruf an/aus, Prompt A/B.

**Dieses Skript macht echte Modellaufrufe und kostet Geld.** Zwei Aufrufe je
Lauf. Ein vollständiger Durchgang über alle drei Läufe des Messplans sind
**zwölf Läufe, also 24 Modellaufrufe** — dazu die Einbettung der Erzählung bei
jedem Lauf mit Abruf.

    .venv/Scripts/python.exe scripts/messlauf.py --lauf 1
    .venv/Scripts/python.exe scripts/messlauf.py --lauf 3
    .venv/Scripts/python.exe scripts/messlauf.py --alle

Anders als `zehn_laeufe.py`, das zehnmal dasselbe fährt, stellt dieses Skript
**verschiedene Konfigurationen gegeneinander**. Zwei Schalter:

- **Abruf an/aus** — aus heisst: der Indexordner wird für die Dauer des Laufs
  umbenannt, dann liefert `retrieve_solution_context` leere Listen und der
  Prompt läuft wie vor Batch 10.
- **Prompt A/B** — A ist `ergebnis_teil1.md`, B die schlanke Fassung
  `ergebnis_teil1_schlank.md`.

Erhoben wird alles, was der Messplan unter „Was je Lauf berichtet wird"
nennt, einschliesslich der Wortlautprüfung gegen das abgerufene Wissen und
der Dauer des Abrufs.

Geschrieben wird nach `messungen/messlauf_<datum>/` — je Lauf eine JSON-Datei
mit dem vollständigen Ergebnis, dazu eine Übersicht als Markdown. Derya liest
die Ergebnisse nebeneinander; die Kennzahlen ordnen nur vor.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import re
import sys
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime
from time import perf_counter
from typing import Iterator

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

WURZEL = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WURZEL))

# **Eine Quelle für die Erzählungen: der Goldbestand.**
#
# Sie lagen doppelt — einmal hier, einmal als Markdown unter den
# Arbeitsunterlagen. Zwei Kopien laufen auseinander, und gemessen
# würde dann etwas anderes als bewertet.
ERZAEHLUNGEN = WURZEL / "knowledge/evaluation/gold"
MESSUNGEN = WURZEL / "messungen"

#: Ab wie vielen gleichen Wörtern eine Übernahme keine sein kann.
#: Der Messplan nennt „mehr als etwa acht Wörter".
UEBERNAHME_FENSTER = 8

FAELLE = {
    "malerbetrieb": ERZAEHLUNGEN / "01_malerbetrieb.json",
    "hausverwaltung_gross": ERZAEHLUNGEN / "03_hausverwaltung_gross.json",
}

#: Die Läufe des Messplans. Je Lauf: Fall, Abruf, Promptfassung.
LAEUFE: dict[str, tuple[tuple[str, str, bool, str], ...]] = {
    "1": (
        ("1a", "malerbetrieb", False, "ergebnis_teil1"),
        ("1b", "malerbetrieb", True, "ergebnis_teil1"),
    ),
    "2": (
        ("2a", "hausverwaltung_gross", False, "ergebnis_teil1"),
        ("2b", "hausverwaltung_gross", True, "ergebnis_teil1"),
    ),
    # Lauf 3 stellt die Promptfassungen gegeneinander. Der Abruf ist in allen
    # vier **gleich** eingestellt — sonst misst man zwei Dinge auf einmal.
    "3": (
        ("3a", "malerbetrieb", True, "ergebnis_teil1"),
        ("3b", "malerbetrieb", True, "ergebnis_teil1_schlank"),
        ("3c", "hausverwaltung_gross", True, "ergebnis_teil1"),
        ("3d", "hausverwaltung_gross", True, "ergebnis_teil1_schlank"),
    ),
}


@dataclass
class Messung:
    """Was ein einzelner Lauf hergegeben hat."""

    kennung: str
    fall: str
    abruf: bool
    prompt: str
    geschafft: bool = False
    ursache: str = ""
    sekunden: float = 0.0
    modellaufrufe: object = 0
    # Was der Messplan je Lauf sehen will
    loesungsname: str = ""
    modulnamen: list[str] = field(default_factory=list)
    modulanzahl: int = 0
    gruppen: list[str] = field(default_factory=list)
    stufe_jetzt: list[str] = field(default_factory=list)
    engpass_satz: str = ""
    engpass_woerter: int = 0
    uebernommen: list[str] = field(default_factory=list)
    # Die Zeitfrage
    abruf_sekunden: float | None = None
    abgerufene_abschnitte: int = 0
    aufruf_eins_sekunden: list[float] = field(default_factory=list)
    prompt_zeichen: int = 0
    zeitablaeufe: int = 0
    vertragsfehler: list[str] = field(default_factory=list)
    #: Das ganze Ergebnis. Derya liest es, keine Kennzahl ersetzt das.
    ergebnis: dict | None = None


class Mitschrift(logging.Handler):
    """Liest mit, was die Anwendung ohnehin protokolliert."""

    def __init__(self) -> None:
        super().__init__(level=logging.INFO)
        self.leeren()

    def leeren(self) -> None:
        self.abruf_sekunden: float | None = None
        self.abgerufene_abschnitte = 0
        self.aufruf_eins_sekunden: list[float] = []
        self.zeitablaeufe = 0
        self.vertragsfehler: list[str] = []
        self.modellaufrufe: object = 0

    def emit(self, record: logging.LogRecord) -> None:
        try:
            zeile = record.getMessage()
        except Exception:  # pragma: no cover - eine kaputte Zeile stoppt nichts
            return
        if zeile.startswith("solution_architecture.retrieved"):
            self.abruf_sekunden = float(zeile.split("seconds=")[1].split()[0])
            self.abgerufene_abschnitte = int(zeile.split("gesamt=")[1].split()[0])
        elif zeile.startswith("openai.structured_output.response") and (
            "section=ResultPartOne" in zeile
        ):
            self.aufruf_eins_sekunden.append(
                float(zeile.split("duration_seconds=")[1].split()[0])
            )
        elif zeile.startswith("openai.structured_output.failed"):
            teil = zeile.split("validation_fields=", 1)
            if len(teil) > 1:
                self.vertragsfehler.append(teil[1].split(" duration")[0])
        elif "APITimeoutError" in zeile or "Zeitlimit" in zeile:
            self.zeitablaeufe += 1
        elif zeile.startswith("result.generated"):
            self.modellaufrufe = zeile.split("openai_calls=")[1].split()[0]


@contextmanager
def konfiguriert(*, abruf: bool, prompt: str) -> Iterator[None]:
    """Stellt die beiden Schalter für die Dauer eines Laufs.

    Der Abruf wird abgeschaltet, indem der Indexordner umbenannt wird — genau
    so, wie der Messplan es beschreibt. Danach steht er wieder da, auch wenn
    der Lauf scheitert.
    """

    from app import rag_service

    vorher = os.environ.get("OPENAI_RESULT_PROMPT")
    os.environ["OPENAI_RESULT_PROMPT"] = prompt

    index = rag_service.SOLUTION_ARCHITECTURE_INDEX_DIRECTORY
    beiseite = index.with_name(index.name + "_beiseite")
    verschoben = False
    if not abruf and index.is_dir():
        index.rename(beiseite)
        verschoben = True
    try:
        yield
    finally:
        if verschoben:
            beiseite.rename(index)
        if vorher is None:
            os.environ.pop("OPENAI_RESULT_PROMPT", None)
        else:
            os.environ["OPENAI_RESULT_PROMPT"] = vorher


def _woerter(text: str) -> list[str]:
    """Die Wörter eines Textes, vergleichbar gemacht.

    Über dieselbe Normalisierung wie die Zitatprüfung: Dann fällt eine
    Übernahme auch auf, wenn Anführungszeichen oder Bindestriche abweichen.
    """

    from app.result_schema import normalize_for_quote_match

    return re.findall(r"[\wäöüß]+", normalize_for_quote_match(text))


def uebernommene_wendungen(
    ergebnis: dict, quellen: list[str], *, fenster: int = UEBERNAHME_FENSTER
) -> list[str]:
    """Wortfolgen, die wörtlich aus dem abgerufenen Wissen stammen.

    Die wichtigste Erhebung des Messplans. Besonders im Verdacht steht das
    Feld `kundennaher_name` der Lösungsfamilien — laut Spezifikation „eine
    Formulierungshilfe, keine Vorgabe".
    """

    aus_quellen: set[tuple[str, ...]] = set()
    for quelle in quellen:
        woerter = _woerter(quelle)
        for start in range(len(woerter) - fenster + 1):
            aus_quellen.add(tuple(woerter[start : start + fenster]))
    if not aus_quellen:
        return []
    gefunden: list[str] = []
    ergebnis_woerter = _woerter(json.dumps(ergebnis, ensure_ascii=False))
    for start in range(len(ergebnis_woerter) - fenster + 1):
        folge = tuple(ergebnis_woerter[start : start + fenster])
        if folge in aus_quellen:
            wendung = " ".join(folge)
            if wendung not in gefunden:
                gefunden.append(wendung)
    return gefunden


def einen_lauf(
    client,
    kennung: str,
    fall: str,
    abruf: bool,
    prompt: str,
    mitschrift: Mitschrift,
) -> Messung:
    """Fährt einen Lauf in genau einer Konfiguration."""

    messung = Messung(kennung=kennung, fall=fall, abruf=abruf, prompt=prompt)
    # Aus dem Goldfall kommt nur die Erzählung — die Bewertung daneben
    # ist Deryas Antwort und hat im Suchtext nichts zu suchen.
    erzaehlung = str(
        json.loads(FAELLE[fall].read_text(encoding="utf-8"))["erzaehlung"]
    ).strip()
    mitschrift.leeren()

    with konfiguriert(abruf=abruf, prompt=prompt):
        messung.prompt_zeichen = _prompt_zeichen(erzaehlung, abruf, prompt)
        client.cookies.clear()
        client.post("/begin", follow_redirects=False)
        begonnen = perf_counter()
        client.post(
            "/interview", data={"free_description": erzaehlung}, follow_redirects=False
        )
        erster = client.post("/analyze")
        if erster.status_code != 200:
            messung.sekunden = perf_counter() - begonnen
            messung.ursache = f"Aufruf 1: {erster.status_code}"
            messung.zeitablaeufe = mitschrift.zeitablaeufe
            messung.vertragsfehler = list(mitschrift.vertragsfehler)
            return messung
        # Der Agentenschritt wird übersprungen, damit die Läufe vergleichbar
        # bleiben und kein dritter Aufruf dazwischenkommt.
        client.post("/verstanden", data={"weiter": "ja"}, follow_redirects=False)
        zweiter = client.post("/analyze")
        messung.sekunden = perf_counter() - begonnen
        if zweiter.status_code != 200:
            messung.ursache = f"Aufruf 2: {zweiter.status_code}"
            messung.zeitablaeufe = mitschrift.zeitablaeufe
            messung.vertragsfehler = list(mitschrift.vertragsfehler)
            return messung
        ergebnis = _gespeichert(client)
        abgerufen = _abgerufenes_wissen(erzaehlung) if abruf else []

    messung.geschafft = ergebnis is not None
    messung.ergebnis = ergebnis
    messung.abruf_sekunden = mitschrift.abruf_sekunden
    messung.abgerufene_abschnitte = mitschrift.abgerufene_abschnitte
    messung.aufruf_eins_sekunden = list(mitschrift.aufruf_eins_sekunden)
    messung.zeitablaeufe = mitschrift.zeitablaeufe
    messung.vertragsfehler = list(mitschrift.vertragsfehler)
    messung.modellaufrufe = mitschrift.modellaufrufe
    if ergebnis is None:
        messung.ursache = "kein gespeichertes Ergebnis"
        return messung

    messung.loesungsname = str((ergebnis.get("kurzfassung") or {}).get("loesungsname") or "")
    module = ergebnis.get("module") or []
    messung.modulnamen = [str(m.get("name") or "") for m in module]
    messung.modulanzahl = len(module)
    messung.gruppen = sorted({str(m.get("gruppe") or "") for m in module})
    messung.stufe_jetzt = [
        str(m.get("name") or "") for m in module if m.get("stufe") == "jetzt"
    ]
    messung.engpass_satz = str((ergebnis.get("kurzfassung") or {}).get("engpass_satz") or "")
    messung.engpass_woerter = len(messung.engpass_satz.split())
    messung.uebernommen = uebernommene_wendungen(ergebnis, abgerufen)
    return messung


def _prompt_zeichen(erzaehlung: str, abruf: bool, prompt: str) -> int:
    """Wie lang der Prompt in dieser Konfiguration wird, in Zeichen."""

    from app.openai_service import _prompt as lade_prompt

    laenge = len(lade_prompt(prompt)) + len(erzaehlung)
    if abruf:
        laenge += sum(len(teil) for teil in _abgerufenes_wissen(erzaehlung))
    return laenge


def _abgerufenes_wissen(erzaehlung: str) -> list[str]:
    """Die Abschnitte, die der Abruf zu dieser Erzählung findet."""

    from app.services.analysis_service import diagnose_context

    return diagnose_context(erzaehlung)


def _gespeichert(client) -> dict | None:
    """Das gespeicherte Ergebnis der laufenden Sitzung, als reine Daten."""

    from app.database import SessionFactory
    from app.services import analysis_service
    from app.web.session import SESSION_COOKIE, session_id_from_cookie

    class _Anfrage:
        cookies = {SESSION_COOKIE: client.cookies.get(SESSION_COOKIE, "")}

    session_id = session_id_from_cookie(_Anfrage())
    if session_id is None:
        return None
    with SessionFactory() as datenbank:
        ergebnis = analysis_service.stored_result(datenbank, session_id)
    return None if ergebnis is None else ergebnis.model_dump(mode="json")


def berichte(messungen: list[Messung]) -> str:
    """Die Übersicht. Die Entscheidung trifft Derya beim Lesen der Ergebnisse."""

    zeilen = [
        "| # | Fall | Abruf | Prompt | s | Module | Gruppen | Jetzt | Übernommen |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for m in messungen:
        if not m.geschafft:
            zeilen.append(
                f"| {m.kennung} | {m.fall} | {'an' if m.abruf else 'aus'} "
                f"| {'B' if 'schlank' in m.prompt else 'A'} | {m.sekunden:.0f} "
                f"| — | — | — | {m.ursache} |"
            )
            continue
        zeilen.append(
            f"| {m.kennung} | {m.fall} | {'an' if m.abruf else 'aus'} "
            f"| {'B' if 'schlank' in m.prompt else 'A'} | {m.sekunden:.0f} "
            f"| {m.modulanzahl} | {len(m.gruppen)} "
            f"| {', '.join(m.stufe_jetzt) or '—'} "
            f"| {len(m.uebernommen)} |"
        )

    zeilen += ["", "## Je Lauf", ""]
    for m in messungen:
        zeilen += [
            f"### {m.kennung} · {m.fall} · Abruf {'an' if m.abruf else 'aus'} · "
            f"Prompt {'B (schlank)' if 'schlank' in m.prompt else 'A (vollständig)'}",
            "",
        ]
        if not m.geschafft:
            zeilen += [f"**Gescheitert:** {m.ursache}", ""]
            if m.vertragsfehler:
                zeilen += [f"Vertragsprüfung: {', '.join(m.vertragsfehler)}", ""]
            continue
        zeilen += [
            f"- **Lösungsname:** {m.loesungsname}",
            f"- **Engpass-Satz** ({m.engpass_woerter} Wörter): {m.engpass_satz}",
            f"- **Module** ({m.modulanzahl}): {' · '.join(m.modulnamen)}",
            f"- **Gruppen** ({len(m.gruppen)}): {' · '.join(m.gruppen)}",
            f"- **Stufe jetzt:** {', '.join(m.stufe_jetzt) or '—'}",
            f"- **Modellaufrufe:** {m.modellaufrufe}",
            f"- **Prompt-Länge:** {m.prompt_zeichen} Zeichen",
        ]
        if m.abruf:
            zeilen.append(
                f"- **Abruf:** {m.abruf_sekunden if m.abruf_sekunden is not None else '—'} s, "
                f"{m.abgerufene_abschnitte} Abschnitte"
            )
        if m.aufruf_eins_sekunden:
            zeilen.append(
                "- **Aufruf 1:** "
                + ", ".join(f"{s:.0f} s" for s in m.aufruf_eins_sekunden)
            )
        if m.uebernommen:
            zeilen += ["- **Wörtlich übernommen:**"]
            zeilen += [f"  - {w}" for w in m.uebernommen]
        else:
            zeilen.append("- **Wörtlich übernommen:** nichts gefunden")
        zeilen.append("")

    zeitablaeufe = sum(m.zeitablaeufe for m in messungen)
    durch = sum(m.geschafft for m in messungen)
    zeilen += [
        "## Zusammen",
        "",
        f"- Durchgekommen: {durch} von {len(messungen)}",
        f"- Zeitabläufe insgesamt: {zeitablaeufe}",
        "",
        "**Ein ausgefallener Lauf wird wiederholt, nicht als Ergebnis gewertet.**",
        "Wie oft wiederholt wurde, gehört in den Bericht.",
    ]
    return "\n".join(zeilen)


def main() -> int:
    zerleger = argparse.ArgumentParser(description=__doc__)
    zerleger.add_argument("--lauf", choices=sorted(LAEUFE), action="append")
    zerleger.add_argument("--alle", action="store_true")
    zerleger.add_argument("--ziel", type=pathlib.Path, default=None)
    argumente = zerleger.parse_args()

    gewaehlt = sorted(LAEUFE) if argumente.alle else (argumente.lauf or ["1"])
    aufgaben = [eintrag for nummer in gewaehlt for eintrag in LAEUFE[nummer]]
    fehlend = sorted({FAELLE[a[1]].name for a in aufgaben if not FAELLE[a[1]].is_file()})
    if fehlend:
        print("Erzählung fehlt: " + ", ".join(fehlend))
        return 1

    print(
        f"{len(aufgaben)} Läufe, {len(aufgaben) * 2} Modellaufrufe. "
        "Das kostet Geld.\n"
    )

    mitschrift = Mitschrift()
    logging.getLogger().addHandler(mitschrift)
    logging.getLogger().setLevel(logging.INFO)

    from dotenv import load_dotenv

    load_dotenv(WURZEL / ".env")
    from fastapi.testclient import TestClient

    from app.main import app

    messungen: list[Messung] = []
    # Mit Uhrzeit, damit zwei Läufe am selben Tag nebeneinander liegen
    # statt übereinander — siehe `gold_lauf.py`.
    ziel = argumente.ziel or MESSUNGEN / f"messlauf_{datetime.now():%Y%m%d_%H%M}"
    ziel.mkdir(parents=True, exist_ok=True)
    with TestClient(app) as client:
        for kennung, fall, abruf, prompt in aufgaben:
            print(
                f"  {kennung}: {fall}, Abruf {'an' if abruf else 'aus'}, "
                f"Prompt {'B' if 'schlank' in prompt else 'A'} …",
                flush=True,
            )
            messung = einen_lauf(client, kennung, fall, abruf, prompt, mitschrift)
            messungen.append(messung)
            # Nach jedem Lauf schreiben: Ein Absturz im letzten darf die
            # bezahlten davor nicht mitnehmen.
            (ziel / f"{kennung}.json").write_text(
                json.dumps(asdict(messung), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(
                f"     {'durch' if messung.geschafft else 'GESCHEITERT'} "
                f"in {messung.sekunden:.0f} s"
                + (f" — {messung.ursache}" if messung.ursache else ""),
                flush=True,
            )

    text = berichte(messungen)
    (ziel / "uebersicht.md").write_text(text, encoding="utf-8")
    print("\n" + text)
    print(f"\ngeschrieben: {ziel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
