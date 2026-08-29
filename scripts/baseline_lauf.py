"""Denselben Fall mehrfach fahren und festhalten, was dabei passiert.

**Wozu.** Bevor am Entscheidungsweg etwas geaendert wird, muss feststehen,
was der heutige Stand tatsaechlich liefert - und wie sehr er zwischen zwei
Laeufen schwankt. Eine Verbesserung laesst sich sonst nicht von Rauschen
unterscheiden.

**Was dieses Skript nicht ist.** Keine Goldbewertung. Es vergleicht nichts
mit einer Sollantwort, es stellt nur fest, was herauskommt. Welche Antwort
fachlich richtig waere, entscheidet ein Mensch an anderer Stelle.

**Der Produktionspfad bleibt unberuehrt.** Gemessen wird auf drei Wegen,
die alle nichts veraendern:

1. Die Protokollzeilen, die `openai_service`, `rag_service` und
   `analysis_service` ohnehin schreiben - daraus kommen die Laufzeiten je
   Aufruf, die Abrufmengen und die getroffene Auswahl.
2. Zwei Durchreicher um `retrieve_solution_context` und
   `generate_target_architecture`. Sie schreiben mit, was hinein- und was
   herausgeht, und geben unveraendert weiter. Ohne sie waeren die
   Suchanfrage und die rohe Planner-Ausgabe nicht sichtbar: Beide werden
   heute nirgends gespeichert.
3. Das gespeicherte Ergebnis aus der Datenbank.

**Was heute nicht messbar ist.** Tokenzahlen und Kosten. Die Antwort wird
ueber `with_raw_response.parse` gelesen, und die Verbrauchsdaten werden
dabei verworfen. Das ohne Aenderung am Produktionspfad nachzuruesten geht
nicht - es steht als Luecke im Bericht.

    python scripts/baseline_lauf.py --laeufe 3

Jeder Lauf kostet vier Modellaufrufe, mit Belegwiederholung fuenf, dazu
Einbettungen fuer den Abruf.
"""

from __future__ import annotations

import argparse
import json
import logging
import pathlib
import re
import sys
from datetime import datetime
from time import perf_counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WURZEL = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WURZEL))

MESSUNGEN = WURZEL / "messungen"
FALLDATEI = WURZEL / "knowledge/evaluation/entwurf_heizung_sanitaer.json"


class Mitschrift(logging.Handler):
    """Liest die Protokollzeilen mit, die die Anwendung ohnehin schreibt.

    Kein eigener Zaehler neben dem Code, der auseinanderlaufen kann -
    sondern genau die Zeilen, die im Betrieb auch im Protokoll stehen.
    """

    #: Was aus welcher Zeile gelesen wird. Alles andere wird nur gesammelt.
    AUFRUF_ENDE = re.compile(
        r"openai\.structured_output\.response section=(\S+) call=(\d+) "
        r"status=(\d+) duration_seconds=([\d.]+)"
    )
    EINBETTUNG_ENDE = re.compile(
        r"openai\.embeddings\.response section=(\S+) call=(\d+) "
        r"status=(\d+) duration_seconds=([\d.]+)"
    )
    ABRUF = re.compile(r"solution_architecture\.retrieved seconds=([\d.]+) (.*)")
    ABSAETZE = re.compile(r"solution_architecture\.absaetze anzahl=(\d+) zeichen=(\d+)")
    AUSWAHL = re.compile(r"solution\.selected familien=(\[.*?\]) module=(\d+) (.*)")
    ABDECKUNG = re.compile(r"solution\.coverage stufen=(\d+) offen=(\S+)")
    VERSTANDEN = re.compile(
        r"understanding\.written session=(\d+) runde=(\d+) rueckfrage=(\S+) seconds=([\d.]+)"
    )

    def __init__(self) -> None:
        super().__init__(level=logging.INFO)
        self.zeilen: list[str] = []
        self.aufrufe: list[dict[str, object]] = []
        self.einbettungen: list[dict[str, object]] = []
        self.abrufe: list[dict[str, object]] = []
        self.absaetze: list[dict[str, int]] = []
        self.auswahl: dict[str, object] = {}
        self.abdeckung: dict[str, object] = {}
        self.verstanden: dict[str, object] = {}
        self.gefiltert: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:  # noqa: D102
        try:
            zeile = record.getMessage()
        except Exception:  # pragma: no cover - eine kaputte Zeile zaehlt nicht
            return
        self.zeilen.append(zeile)

        if (treffer := self.AUFRUF_ENDE.match(zeile)) is not None:
            self.aufrufe.append(
                {
                    "abschnitt": treffer.group(1),
                    "nummer": int(treffer.group(2)),
                    "status": int(treffer.group(3)),
                    "sekunden": float(treffer.group(4)),
                }
            )
        elif (treffer := self.EINBETTUNG_ENDE.match(zeile)) is not None:
            self.einbettungen.append(
                {"status": int(treffer.group(3)), "sekunden": float(treffer.group(4))}
            )
        elif (treffer := self.ABRUF.match(zeile)) is not None:
            self.abrufe.append(
                {"sekunden": float(treffer.group(1)), "mengen": treffer.group(2).strip()}
            )
        elif (treffer := self.ABSAETZE.match(zeile)) is not None:
            self.absaetze.append(
                {"anzahl": int(treffer.group(1)), "zeichen": int(treffer.group(2))}
            )
        elif (treffer := self.AUSWAHL.match(zeile)) is not None:
            self.auswahl = {
                "familien": treffer.group(1),
                "module": int(treffer.group(2)),
                "rest": treffer.group(3).strip(),
            }
        elif (treffer := self.ABDECKUNG.match(zeile)) is not None:
            self.abdeckung = {
                "stufen": int(treffer.group(1)),
                "offen": treffer.group(2),
            }
        elif (treffer := self.VERSTANDEN.match(zeile)) is not None:
            self.verstanden = {
                "runde": int(treffer.group(2)),
                "rueckfrage": treffer.group(3) == "True",
                "sekunden": float(treffer.group(4)),
            }
        elif zeile.startswith("solution_architecture.family_filtered"):
            self.gefiltert.append(zeile)


class Durchreicher:
    """Schreibt mit, was durch eine Funktion geht - und aendert nichts.

    Suchanfrage und rohe Planner-Ausgabe werden heute nirgends
    gespeichert. Ohne dieses Mitschreiben liesse sich nicht sagen, womit
    der Abruf ueberhaupt gesucht hat.
    """

    def __init__(self) -> None:
        self.abrufanfragen: list[str] = []
        self.abruftreffer: list[dict[str, object]] = []
        self.planner: dict[str, object] = {}

    def um_abruf(self, echt):
        def gemessen(query: str):
            self.abrufanfragen.append(query)
            ergebnis = echt(query)
            try:
                self.abruftreffer.append(
                    {
                        "betriebsarten": [c.chunk_id for c in ergebnis.betriebsarten],
                        "diagnosemuster": [c.chunk_id for c in ergebnis.diagnosemuster],
                        "loesungsfamilien": [
                            c.chunk_id for c in ergebnis.loesungsfamilien
                        ],
                    }
                )
            except Exception:  # pragma: no cover - Form kann abweichen
                self.abruftreffer.append({"unlesbar": True})
            return ergebnis

        return gemessen

    def um_planner(self, echt):
        def gemessen(**kwargs):
            ergebnis = echt(**kwargs)
            try:
                self.planner = ergebnis.model_dump(mode="json")
            except Exception:  # pragma: no cover
                self.planner = {"unlesbar": True}
            return ergebnis

        return gemessen


def _fachliche_felder(ergebnis: dict) -> dict[str, object]:
    """Die Felder, an denen sich fachliche Qualitaet ablesen laesst."""

    verstanden = ergebnis.get("verstanden") or {}
    aufgaben = ergebnis.get("aufgabenteilung") or {}
    return {
        "engpass_satz": (ergebnis.get("kurzfassung") or {}).get("engpass_satz"),
        "engpass_absatz": verstanden.get("engpass_absatz"),
        "eckdaten": verstanden.get("eckdaten"),
        "belege": [b.get("zitat") for b in (verstanden.get("belege") or [])],
        "familien": sorted(
            {
                kennung
                for modul in (ergebnis.get("module") or [])
                for kennung in (modul.get("solution_family_ids") or [])
            }
        ),
        "module": [m.get("name") for m in (ergebnis.get("module") or [])],
        "ausbaupfad": [
            {"stufe": a.get("stufe"), "name": a.get("name")}
            for a in (ergebnis.get("ausbaupfad") or [])
        ],
        "system_uebernimmt": list(aufgaben.get("system") or []),
        "mensch_behaelt": list(aufgaben.get("mensch") or []),
        "grenzen": [g.get("titel") for g in (aufgaben.get("grenzen") or [])],
        "ansichten": [v.get("titel") for v in (ergebnis.get("ansichten") or [])],
    }


def ein_lauf(nummer: int, erzaehlung: str) -> dict[str, object]:
    """Ein vollstaendiger Durchlauf, mit allem, was dabei sichtbar wird."""

    from fastapi.testclient import TestClient
    from sqlalchemy import func, select
    from sqlalchemy.orm import Session

    from app.database import engine
    from app.main import app
    from app.models import AnalysisSession
    from app.services import analysis_service

    mitschrift = Mitschrift()
    durchreicher = Durchreicher()

    # Nur fuer diesen Lauf umgehaengt, danach wieder zurueck.
    echt_abruf = analysis_service.retrieve_solution_context
    echt_planner = analysis_service.generate_target_architecture
    analysis_service.retrieve_solution_context = durchreicher.um_abruf(echt_abruf)
    analysis_service.generate_target_architecture = durchreicher.um_planner(echt_planner)

    protokoll = logging.getLogger("app")
    protokoll.addHandler(mitschrift)
    protokoll.setLevel(logging.INFO)

    bericht: dict[str, object] = {"lauf": nummer}
    begonnen = perf_counter()
    try:
        with TestClient(app) as client:
            client.post("/begin", follow_redirects=False)
            client.post(
                "/interview",
                data={"free_description": erzaehlung},
                follow_redirects=False,
            )
            erster = client.post("/analyze", headers={"Accept": "application/json"})
            bericht["diagnose_status"] = erster.json().get("state")
            nach_diagnose = perf_counter() - begonnen

            # Die Verstandenseite wird bestaetigt, nicht ergaenzt - sonst
            # laeuft die Diagnose ein zweites Mal und die Laeufe sind nicht
            # mehr vergleichbar.
            client.post("/verstanden", data={"weiter": "ja"}, follow_redirects=False)
            zweiter = client.post("/analyze", headers={"Accept": "application/json"})
            bericht["loesung_status"] = zweiter.json().get("state")

            with Session(engine) as datenbank:
                sitzung = datenbank.scalar(select(func.max(AnalysisSession.session_id)))
                ergebnis = analysis_service.stored_result(datenbank, sitzung)
            bericht["sitzung"] = sitzung
    finally:
        protokoll.removeHandler(mitschrift)
        analysis_service.retrieve_solution_context = echt_abruf
        analysis_service.generate_target_architecture = echt_planner

    bericht["sekunden_gesamt"] = round(perf_counter() - begonnen, 1)
    bericht["sekunden_bis_diagnose"] = round(nach_diagnose, 1)
    bericht["modellaufrufe"] = mitschrift.aufrufe
    bericht["einbettungen"] = mitschrift.einbettungen
    bericht["abruf_protokoll"] = mitschrift.abrufe
    bericht["abruf_absaetze"] = mitschrift.absaetze
    bericht["abruf_anfragen"] = durchreicher.abrufanfragen
    bericht["abruf_treffer"] = durchreicher.abruftreffer
    bericht["gefilterte_familien"] = mitschrift.gefiltert
    bericht["auswahl_protokoll"] = mitschrift.auswahl
    bericht["abdeckung_protokoll"] = mitschrift.abdeckung
    bericht["rueckfrage_gestellt"] = mitschrift.verstanden.get("rueckfrage")
    bericht["planner_ausgabe"] = durchreicher.planner
    bericht["tokens"] = "nicht erfasst - siehe Kopf dieser Datei"
    if ergebnis is not None:
        roh = ergebnis.model_dump(mode="json")
        bericht["ergebnis"] = _fachliche_felder(roh)
        bericht["ergebnis_vollstaendig"] = roh
    else:
        bericht["ergebnis"] = None
    return bericht


def main() -> int:
    zerleger = argparse.ArgumentParser(description=__doc__)
    zerleger.add_argument("--laeufe", type=int, default=3)
    zerleger.add_argument("--fall", type=pathlib.Path, default=FALLDATEI)
    argumente = zerleger.parse_args()

    from dotenv import load_dotenv

    load_dotenv(WURZEL / ".env")

    from app.hintergrund import celery_app

    # Dieselbe Aufgabe, derselbe Analyseweg, ein Prozess weniger. Nur so
    # sind Laufzeiten und Aufrufe ueberhaupt sichtbar.
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = False

    from app.database import engine
    from app.models import Base

    Base.metadata.create_all(bind=engine)
    logging.basicConfig(level=logging.WARNING, format="%(message)s")

    fall = json.loads(argumente.fall.read_text(encoding="utf-8"))
    erzaehlung = str(fall["erzaehlung"]).strip()

    from scripts.laufstempel import stempel

    lauf_stempel = stempel()
    print(f"Fall    : {fall.get('titel')}")
    print(f"Zeichen : {len(erzaehlung)}")
    print(f"Commit  : {lauf_stempel['code']['commit']}  sauber={lauf_stempel['code']['sauber']}")
    print(f"Laeufe  : {argumente.laeufe}  (je 4 Modellaufrufe)\n")
    if not lauf_stempel["code"]["sauber"]:
        print("ACHTUNG: Arbeitsbaum nicht sauber - Messung gehoert zu keinem Commit.\n")

    ziel = MESSUNGEN / f"baseline_heizung_{datetime.now():%Y%m%d_%H%M}"
    ziel.mkdir(parents=True, exist_ok=True)
    (ziel / "laufstempel.json").write_text(
        json.dumps(lauf_stempel, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    for nummer in range(1, argumente.laeufe + 1):
        print(f"Lauf {nummer} laeuft ...", flush=True)
        bericht = ein_lauf(nummer, erzaehlung)
        # Sofort schreiben: Ein Absturz im dritten Lauf darf die ersten
        # beiden nicht mitnehmen - sie sind bezahlt.
        (ziel / f"lauf_{nummer}.json").write_text(
            json.dumps(bericht, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        erg = bericht.get("ergebnis") or {}
        print(
            f"  {bericht['sekunden_gesamt']}s | "
            f"{len(bericht['modellaufrufe'])} Aufrufe | "
            f"Rueckfrage={bericht['rueckfrage_gestellt']} | "
            f"Familien={erg.get('familien')}",
            flush=True,
        )

    print(f"\n{ziel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
