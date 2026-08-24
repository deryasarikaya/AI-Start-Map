"""Fährt den vollständigen Durchlauf zehnmal und zählt, was dabei passiert.

**Dieses Skript macht echte Modellaufrufe und kostet Geld.** Zehn Durchläufe
mit je zwei Aufrufen der grossen Hausverwaltungserzählung, dazu die
Wiederholungen, die dabei anfallen. Es startet nichts von allein — es läuft
nur, wenn es jemand aufruft.

    .venv/Scripts/python.exe scripts/zehn_laeufe.py [--laeufe N] [--ziel PFAD]

Es berichtet, wie viele Läufe durchkamen, die Zeiten, die Ursache jedes
gescheiterten Laufs, wie oft ein Zitat verworfen wurde und wie oft ein zweiter
Versuch nach einem Zeitablauf ausgelöst hat.

Die Zahlen kommen aus dem Protokoll der Anwendung, nicht aus einer Schätzung:
Das Skript hängt sich als Log-Handler ein und liest die Zeilen mit, die
`openai_service` und `analysis_service` ohnehin schreiben.
"""

from __future__ import annotations

import argparse
import json
import logging
import pathlib
import statistics
import sys
from dataclasses import dataclass, field
from time import perf_counter, sleep

# Die Windows-Konsole spricht cp1252. Ein verworfenes Zitat mit geschütztem
# Bindestrich hat den ganzen Lauf beim Drucken abstürzen lassen, nachdem alle
# zehn Durchläufe schon bezahlt waren.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

WURZEL = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WURZEL))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(WURZEL / ".env")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.openai_service import (  # noqa: E402
    get_openai_call_count,
    reset_openai_call_count,
)

# Dieselbe Quelle wie beim Goldlauf: Was gemessen wird, ist der Text,
# gegen den auch bewertet wird.
ERZAEHLUNG_DATEI = WURZEL / "knowledge/evaluation/gold/03_hausverwaltung_gross.json"


@dataclass
class Lauf:
    """Was bei einem einzelnen Durchlauf herausgekommen ist."""

    nummer: int
    geschafft: bool
    sekunden: float
    modellaufrufe: int
    ursache: str = ""
    verworfene_zitate: list[str] = field(default_factory=list)
    zweiter_versuch_nach_zeitablauf: int = 0
    belege_auf_der_seite: int = -1


class Mitschrift(logging.Handler):
    """Liest die Protokollzeilen mit, die für die Auswertung zählen.

    Kein Nachbauen der Zählung: Es werden genau die Zeilen gelesen, die die
    Anwendung im Betrieb auch schreibt. Was hier nicht ankommt, ist auch im
    Betrieb nicht sichtbar.
    """

    def __init__(self) -> None:
        super().__init__(level=logging.INFO)
        self.verworfene_zitate: list[str] = []
        self.zeitablaeufe = 0
        self.zweite_versuche = 0
        self.letzter_fehler = ""

    def leeren(self) -> None:
        self.verworfene_zitate = []
        self.zeitablaeufe = 0
        self.zweite_versuche = 0
        self.letzter_fehler = ""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            zeile = record.getMessage()
        except Exception:  # pragma: no cover - eine kaputte Zeile stoppt nichts
            return
        if zeile.startswith("result.quote_rejected"):
            self.verworfene_zitate.append(zeile.split("zitat=", 1)[1].split(" grund=")[0])
        elif zeile.startswith("openai.structured_output.start") and "attempt=2" in zeile:
            self.zweite_versuche += 1
        elif "APITimeoutError" in zeile or "Zeitlimit" in zeile:
            self.zeitablaeufe += 1
        elif zeile.startswith("openai.structured_output.failed"):
            self.letzter_fehler = zeile


def _ursache(mitschrift: Mitschrift, antwort_text: str) -> str:
    """Sagt in einem Satz, woran ein Lauf gescheitert ist."""

    if mitschrift.zeitablaeufe:
        return f"Zeitablauf ({mitschrift.zeitablaeufe}x)"
    if "wörtlich in der Erzählung" in mitschrift.letzter_fehler:
        return "Zitat nicht wörtlich, auch nach dem zweiten Versuch"
    if mitschrift.letzter_fehler:
        teil = mitschrift.letzter_fehler.split("exception_type=", 1)
        return teil[1].split(" ")[0] if len(teil) > 1 else mitschrift.letzter_fehler
    return antwort_text[:160]


def einen_lauf(client: TestClient, erzaehlung: str, mitschrift: Mitschrift, nummer: int) -> Lauf:
    """Erzählen, auswerten, Seite holen — einmal von vorn."""

    mitschrift.leeren()
    client.cookies.clear()
    client.post("/begin", follow_redirects=False)
    reset_openai_call_count()

    begonnen = perf_counter()
    gespeichert = client.post(
        "/interview", data={"free_description": erzaehlung}, follow_redirects=False
    )
    if gespeichert.headers.get("location") != "/processing":
        return Lauf(nummer, False, perf_counter() - begonnen, 0, "Erzählung nicht angenommen")

    # **Beide** Aufrufe, nicht nur der erste.
    #
    # Zwischen den beiden Aufrufen liegt die Verstandenseite, und
    # `/analyze` macht je Anfrage genau einen Modellaufruf. Wer `/analyze`
    # nur einmal ruft, misst zehnmal den halben Durchlauf: In der Spalte
    # „Aufrufe" stünde überall 1 statt 2, und „Belege" zeigte die
    # Verstandenseite mit ihrem einen Zitat. Beide Zahlen wären nicht
    # kaputt — sie mässen etwas anderes als das, was darübersteht.
    erster = client.post("/analyze")
    aufrufe = get_openai_call_count()
    if erster.status_code != 200:
        return Lauf(
            nummer,
            False,
            perf_counter() - begonnen,
            aufrufe,
            "Aufruf 1: " + _ursache(mitschrift, erster.text),
            list(mitschrift.verworfene_zitate),
            mitschrift.zweite_versuche if mitschrift.zeitablaeufe else 0,
        )

    # Der Kunde geht weiter, ohne etwas zu ergänzen. Der Agentenschritt
    # bleibt damit aus dem Spiel, und die Läufe sind untereinander gleich.
    client.post("/verstanden", data={"weiter": "ja"}, follow_redirects=False)
    zweiter = client.post("/analyze")
    dauer = perf_counter() - begonnen
    # `/analyze` setzt den Zähler zu Beginn jeder Anfrage zurück. Wer erst
    # am Ende liest, bekommt nur den letzten Aufruf.
    aufrufe += get_openai_call_count()
    if zweiter.status_code != 200:
        return Lauf(
            nummer,
            False,
            dauer,
            aufrufe,
            "Aufruf 2: " + _ursache(mitschrift, zweiter.text),
            list(mitschrift.verworfene_zitate),
            mitschrift.zweite_versuche if mitschrift.zeitablaeufe else 0,
        )

    seite = client.get("/results")
    return Lauf(
        nummer,
        seite.status_code == 200,
        perf_counter() - begonnen,
        aufrufe,
        "" if seite.status_code == 200 else f"Seite antwortete {seite.status_code}",
        list(mitschrift.verworfene_zitate),
        mitschrift.zweite_versuche if mitschrift.zeitablaeufe else 0,
        seite.text.count('<div class="q">'),
    )


def bericht(laeufe: list[Lauf]) -> str:
    """Fasst die Läufe zu dem zusammen, was im Bericht stehen muss."""

    geschafft = [lauf for lauf in laeufe if lauf.geschafft]
    zeiten = [lauf.sekunden for lauf in geschafft]
    zeilen = [
        f"{len(geschafft)} von {len(laeufe)} Läufen sind durchgekommen.",
        "",
        "| # | Ergebnis | Sekunden | Aufrufe | Belege | Ursache |",
        "|---|---|---|---|---|---|",
    ]
    for lauf in laeufe:
        zeilen.append(
            f"| {lauf.nummer} | {'durch' if lauf.geschafft else 'gescheitert'} "
            f"| {lauf.sekunden:.1f} | {lauf.modellaufrufe} "
            f"| {lauf.belege_auf_der_seite if lauf.geschafft else '—'} "
            f"| {lauf.ursache or '—'} |"
        )
    if zeiten:
        zeilen += [
            "",
            f"Schnellster Lauf: {min(zeiten):.1f} s",
            f"Langsamster Lauf: {max(zeiten):.1f} s",
            f"Mittlerer Lauf:   {statistics.median(zeiten):.1f} s",
        ]
    verworfen = [zitat for lauf in laeufe for zitat in lauf.verworfene_zitate]
    zeilen += [
        "",
        f"Verworfene Zitate insgesamt: {len(verworfen)}",
    ]
    zeilen += [f"  - {zitat}" for zitat in verworfen]
    zeilen += [
        "",
        "Zweiter Versuch nach Zeitablauf ausgelöst: "
        f"{sum(lauf.zweiter_versuch_nach_zeitablauf for lauf in laeufe)}x",
    ]
    return "\n".join(zeilen)


def main() -> int:
    zerleger = argparse.ArgumentParser(description=__doc__)
    zerleger.add_argument("--laeufe", type=int, default=10)
    zerleger.add_argument("--ziel", type=pathlib.Path, default=None)
    # Pause zwischen den Läufen. Zehn Durchläufe ohne Luft dazwischen sind
    # kein Betrieb, sondern Dauerfeuer — und die Antwortzeiten wurden von Lauf
    # zu Lauf schlechter.
    zerleger.add_argument("--pause", type=float, default=0.0)
    argumente = zerleger.parse_args()

    mitschrift = Mitschrift()
    logging.getLogger().addHandler(mitschrift)
    logging.getLogger().setLevel(logging.INFO)

    erzaehlung = str(json.loads(ERZAEHLUNG_DATEI.read_text(encoding="utf-8"))["erzaehlung"])
    laeufe: list[Lauf] = []
    with TestClient(app) as client:
        for nummer in range(1, argumente.laeufe + 1):
            lauf = einen_lauf(client, erzaehlung, mitschrift, nummer)
            laeufe.append(lauf)
            print(
                f"Lauf {nummer:2d}: {'durch' if lauf.geschafft else 'GESCHEITERT'} "
                f"in {lauf.sekunden:5.1f} s, {lauf.modellaufrufe} Aufrufe"
                + (f" — {lauf.ursache}" if lauf.ursache else ""),
                flush=True,
            )
            if argumente.pause and nummer < argumente.laeufe:
                sleep(argumente.pause)

    text = bericht(laeufe)
    # Erst schreiben, dann drucken. Zehn bezahlte Durchläufe dürfen nicht an
    # der Zeichenkodierung einer Konsole verloren gehen.
    if argumente.ziel is not None:
        argumente.ziel.write_text(text, encoding="utf-8")
        argumente.ziel.with_suffix(".json").write_text(
            json.dumps([lauf.__dict__ for lauf in laeufe], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    print("\n" + text)
    if argumente.ziel is not None:
        print(f"\ngeschrieben: {argumente.ziel}")
    return 0 if sum(lauf.geschafft for lauf in laeufe) >= 9 else 1


if __name__ == "__main__":
    raise SystemExit(main())
