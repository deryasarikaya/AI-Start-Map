"""Fährt den Goldbestand durch die Anwendung und misst, was herauskommt.

**Dieses Skript macht echte Modellaufrufe und kostet Geld.** Zwei Aufrufe je
Fall — bei zwölf gefüllten Fällen also 24. Fälle ohne Erzählung werden
übersprungen und gemeldet, nicht gerechnet.

    .venv/Scripts/python.exe scripts/gold_lauf.py

Zwei Läufe vergleichen — **das ist der eigentliche Zweck**, nicht eine Zahl,
sondern die Frage, ob eine Änderung geholfen hat:

    .venv/Scripts/python.exe scripts/gold_lauf.py \\
        --vergleiche messungen/gold_A messungen/gold_B

Die Kennzahlen stehen in `KENNZAHLEN` und werden in `bewerte_lauf` berechnet.
Beides ist ohne Modellaufruf testbar — siehe `tests/test_gold_lauf.py`. Eine
falsche Kennzahl wäre schlimmer als keine.
"""

from __future__ import annotations

import argparse
import json
import logging
import pathlib
import re
import statistics
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from time import perf_counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WURZEL = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WURZEL))

GOLD_VERZEICHNIS = WURZEL / "knowledge/evaluation/gold"
MESSUNGEN = WURZEL / "messungen"

#: Wie lang eine wörtlich übernommene Wortfolge sein muss, damit sie zählt.
#: Fünf Wörter sind kein Zufall mehr — „Digitaler Kunden- und Auftrags-Hub"
#: kam so aus einer Beispielliste zurück.
ABSCHREIB_FENSTER = 5

KENNZAHLEN = (
    "fehlstart_quote",
    "groessentreffer",
    "startpunkt_treffer",
    "pflichtbegriffe",
    "durchkommensquote",
    "abschreibquote",
)


@dataclass
class Fallergebnis:
    """Was bei einem Fall herauskam, roh und bewertet."""

    fall_id: str
    titel: str
    durchgekommen: bool
    sekunden: float = 0.0
    ursache: str = ""
    loesungsname: str = ""
    modulnamen: list[str] = field(default_factory=list)
    #: Der ganze sichtbare Text des Ergebnisses, für die Wortprüfungen.
    ergebnistext: str = ""
    #: Die Module mit `stufe == "jetzt"` — daran misst sich der Fehlstart.
    jetzt: list[str] = field(default_factory=list)
    fehlstart: list[str] = field(default_factory=list)
    #: Begriffe, die **nirgends** im Ergebnis stehen dürfen — nicht nur
    #: nicht auf `jetzt`. Gemeint sind Themen, zu denen der Betrieb gar
    #: nicht gefragt hat — etwa Bezahlung oder Abrechnung, wenn es um
    #: den Auftragseingang ging. Ein gut gemeinter Hinweis dazu ist eine
    #: Belehrung und beschädigt den Rest der Auswertung.
    belehrung: list[str] = field(default_factory=list)
    fehlende_pflichtbegriffe: list[str] = field(default_factory=list)
    groesse_passt: bool | None = None
    startpunkt_passt: bool | None = None
    abgeschrieben: list[str] = field(default_factory=list)


def _woerter(text: str) -> list[str]:
    """Die Wörter eines Textes, klein und ohne Satzzeichen."""

    return re.findall(r"[\wäöüß]+", text.casefold())


def abgeschriebene_wendungen(
    ergebnistext: str, quellen: list[str], *, fenster: int = ABSCHREIB_FENSTER
) -> list[str]:
    """Wortfolgen, die wörtlich aus Prompt oder abgerufenem Wissen stammen.

    Genau das haben wir schon gemessen: „Digitaler Kunden- und Auftrags-Hub"
    kam wörtlich aus einer Beispielliste zurück.
    """

    aus_quellen: set[tuple[str, ...]] = set()
    for quelle in quellen:
        woerter = _woerter(quelle)
        for start in range(len(woerter) - fenster + 1):
            aus_quellen.add(tuple(woerter[start : start + fenster]))
    if not aus_quellen:
        return []
    gefunden: list[str] = []
    ergebnis_woerter = _woerter(ergebnistext)
    for start in range(len(ergebnis_woerter) - fenster + 1):
        folge = tuple(ergebnis_woerter[start : start + fenster])
        if folge in aus_quellen:
            wendung = " ".join(folge)
            if wendung not in gefunden:
                gefunden.append(wendung)
    return gefunden


#: Welche Startpunkte es gibt, und wie viele Module mit `stufe == "jetzt"`
#: dazu passen. Nicht wie viel der Betrieb verträgt — womit er anfängt.
STARTPUNKTE = {
    # Es gibt noch nichts Digitales. Der Aufbau selbst ist der erste Schritt.
    "aufbau": (1, 1),
    # Ein oder zwei Bausteine, die für sich stehen.
    "einzelne_automation": (1, 2),
    # Mehrere Bausteine, die ineinandergreifen.
    "verbundenes_system": (2, 2),
}


class Aufrufzaehler(logging.Handler):
    """Zählt jeden Modellaufruf mit, auch jede Wiederholung.

    Wiederholungen zählen mit, weil sie die Kosten eines Laufs bestimmen:
    Ein geplanter Lauf über 22 Aufrufe verbraucht 30, sobald einige davon
    einmal wiederholt werden. Ohne Mitzählen steht diese Zahl erst
    hinterher im Protokoll.

    Gezählt wird die Zeile, die `openai_service` ohnehin vor jedem Versuch
    schreibt — nicht ein eigener Zähler, der auseinanderlaufen kann.
    """

    def __init__(self) -> None:
        super().__init__(level=logging.INFO)
        self.modellaufrufe = 0
        self.einbettungen = 0

    def emit(self, record: logging.LogRecord) -> None:  # noqa: D102
        try:
            zeile = record.getMessage()
        except Exception:  # pragma: no cover - eine kaputte Zeile zählt nicht
            return
        if zeile.startswith("openai.structured_output.start"):
            self.modellaufrufe += 1
        elif zeile.startswith("openai.embeddings.start"):
            self.einbettungen += 1


def bewerte_fall(
    fall: dict,
    ergebnis: dict | None,
    *,
    sekunden: float = 0.0,
    ursache: str = "",
    quellen: list[str] | None = None,
) -> Fallergebnis:
    """Vergleicht ein Ergebnis mit den hinterlegten richtigen Antworten.

    Ein Feld ohne hinterlegte Referenzantwort wird nicht bewertet — dann steht
    dort `None` und die Kennzahl lässt den Fall aus. Eine erfundene Bewertung
    wäre schlimmer als eine fehlende.
    """

    bewertung = fall.get("bewertung") or {}
    treffer = Fallergebnis(
        fall_id=str(fall.get("fall_id") or "?"),
        titel=str(fall.get("titel") or ""),
        durchgekommen=ergebnis is not None,
        sekunden=sekunden,
        ursache=ursache,
    )
    if ergebnis is None:
        return treffer

    treffer.loesungsname = str(
        (ergebnis.get("kurzfassung") or {}).get("loesungsname") or ""
    )
    treffer.modulnamen = [
        str(modul.get("name") or "") for modul in ergebnis.get("module") or []
    ]
    # Der erste Schritt sind die Module mit `stufe == "jetzt"`. Die Stufe steht
    # am Modul, nicht in einer Liste daneben.
    treffer.jetzt = [
        str(modul.get("name") or "")
        for modul in ergebnis.get("module") or []
        if modul.get("stufe") == "jetzt"
    ]
    treffer.ergebnistext = json.dumps(ergebnis, ensure_ascii=False)

    # Der Fehlstart wird **nur gegen die Module auf `jetzt`** geprüft, nicht
    # gegen das ganze Ergebnis. Ein Portal darf im Zielbild eines
    # Zweipersonenbetriebs vorkommen — nur nicht als erster Schritt.
    jetzt_text = " ".join(treffer.jetzt).casefold()
    treffer.fehlstart = [
        begriff
        for begriff in bewertung.get("darf_nicht_vorkommen") or []
        if str(begriff).casefold() in jetzt_text
    ]
    # `darf_nirgends_vorkommen` gilt für **alle** Textfelder, nicht nur für
    # den ersten Schritt. Der Unterschied ist der Zweck: Ein Portal darf im
    # Zielbild stehen und nur nicht sofort kommen — ein Ratschlag zur
    # Beschäftigungsform darf überhaupt nirgends stehen.
    ganzes_ergebnis = treffer.ergebnistext.casefold()
    treffer.belehrung = [
        begriff
        for begriff in bewertung.get("darf_nirgends_vorkommen") or []
        if str(begriff).casefold() in ganzes_ergebnis
    ]
    treffer.fehlende_pflichtbegriffe = [
        begriff
        for begriff in bewertung.get("muss_vorkommen") or []
        if str(begriff).casefold() not in treffer.ergebnistext.casefold()
    ]

    von, bis = bewertung.get("module_anzahl_von"), bewertung.get("module_anzahl_bis")
    if von is not None and bis is not None:
        treffer.groesse_passt = von <= len(treffer.modulnamen) <= bis

    startpunkt = bewertung.get("startpunkt")
    if startpunkt in STARTPUNKTE and treffer.jetzt:
        untere, obere = STARTPUNKTE[startpunkt]
        treffer.startpunkt_passt = untere <= len(treffer.jetzt) <= obere

    treffer.abgeschrieben = abgeschriebene_wendungen(
        treffer.ergebnistext, quellen or []
    )
    return treffer


def bewerte_lauf(ergebnisse: list[Fallergebnis]) -> dict[str, object]:
    """Die Kennzahlen über alle Fälle.

    Ein Anteil wird nur über die Fälle gebildet, für die er überhaupt
    bestimmbar ist. Steht bei zehn von zwölf Fällen keine Modulzahl, misst
    der Grössentreffer die zwei — und sagt auch, dass es zwei waren.
    """

    durchgekommen = [e for e in ergebnisse if e.durchgekommen]
    zeiten = [e.sekunden for e in durchgekommen if e.sekunden > 0]

    def anteil(treffer: list[bool]) -> float | None:
        return sum(treffer) / len(treffer) if treffer else None

    # Nur Fälle, für die überhaupt etwas verboten wurde, können einen
    # Fehlstart haben. Sonst misst die Quote leere Vorgaben.
    fehlstart = [
        bool(e.fehlstart)
        for e in durchgekommen
        if e.jetzt
    ]
    groesse = [e.groesse_passt for e in durchgekommen if e.groesse_passt is not None]
    start = [
        e.startpunkt_passt for e in durchgekommen if e.startpunkt_passt is not None
    ]
    pflicht = [not e.fehlende_pflichtbegriffe for e in durchgekommen]
    abgeschrieben = [bool(e.abgeschrieben) for e in durchgekommen]

    return {
        "faelle_gesamt": len(ergebnisse),
        "fehlstart_quote": anteil(fehlstart),
        "fehlstart_basis": len(fehlstart),
        "belehrungsquote": anteil([bool(e.belehrung) for e in durchgekommen]),
        "belehrungsbasis": len(durchgekommen),
        "groessentreffer": anteil(groesse),
        "groessentreffer_basis": len(groesse),
        "startpunkt_treffer": anteil(start),
        "startpunkt_basis": len(start),
        "pflichtbegriffe": anteil(pflicht),
        "pflichtbegriffe_basis": len(pflicht),
        "durchkommensquote": (
            len(durchgekommen) / len(ergebnisse) if ergebnisse else None
        ),
        "abschreibquote": anteil(abgeschrieben),
        "abschreibquote_basis": len(abgeschrieben),
        "sekunden_schnellster": min(zeiten) if zeiten else None,
        "sekunden_langsamster": max(zeiten) if zeiten else None,
        "sekunden_mittlerer": statistics.median(zeiten) if zeiten else None,
    }


def lade_faelle(verzeichnis: pathlib.Path = GOLD_VERZEICHNIS) -> list[dict]:
    """Alle Golddateien, nach Dateinamen sortiert."""

    return [
        json.loads(pfad.read_text(encoding="utf-8"))
        for pfad in sorted(verzeichnis.glob("*.json"))
    ]


def _prozent(wert: float | None) -> str:
    return "—" if wert is None else f"{wert * 100:.0f} %"


def berichte(ergebnisse: list[Fallergebnis], kennzahlen: dict[str, object]) -> str:
    """Die Tabelle, die ein Mensch liest."""

    zeilen = [
        "## Die eine Zahl",
        "",
        f"**Fehlstart-Quote: {_prozent(kennzahlen['fehlstart_quote'])}** "
        f"({kennzahlen['fehlstart_basis']} bewertete Fälle)",
        "",
        "Anteil der Fälle, in denen **als erster Schritt** etwas steht, das "
        "dort nicht stehen darf. Im Zielbild darf es vorkommen — in `jetzt` "
        "nicht.",
        "",
        "Die Belehrungsquote daneben ist die schärfere Prüfung: Sie fragt, "
        "ob ein Thema **irgendwo** im Ergebnis auftaucht, zu dem der Betrieb "
        "nicht gefragt hat.",
        "",
        "## Je Fall",
        "",
        "| Fall | Ergebnis | s | Module | Jetzt | Fehlstart | Belehrung "
        "| Fehlend | Abgeschr. |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for e in ergebnisse:
        if not e.durchgekommen:
            zeilen.append(
                f"| {e.fall_id} | — | — | — | — | — | — | — "
                f"| {e.ursache or 'nicht gelaufen'} |"
            )
            continue
        groesse = {True: "✓", False: "✗", None: "—"}[e.groesse_passt]
        start = {True: "✓", False: "✗", None: "—"}[e.startpunkt_passt]
        zeilen.append(
            f"| {e.fall_id} | durch | {e.sekunden:.0f} "
            f"| {len(e.modulnamen)} {groesse} "
            f"| {', '.join(e.jetzt) or '—'} {start} "
            f"| {', '.join(e.fehlstart) or '—'} "
            f"| {', '.join(e.belehrung) or '—'} "
            f"| {', '.join(e.fehlende_pflichtbegriffe) or '—'} "
            f"| {len(e.abgeschrieben)} |"
        )
    zeilen += [
        "",
        "## Zusammenfassung",
        "",
        "| Kennzahl | Wert | Basis |",
        "|---|---|---|",
        f"| Fehlstart-Quote | {_prozent(kennzahlen['fehlstart_quote'])} "
        f"| {kennzahlen['fehlstart_basis']} |",
        f"| Belehrungsquote | {_prozent(kennzahlen['belehrungsquote'])} "
        f"| {kennzahlen['belehrungsbasis']} |",
        f"| Grössentreffer | {_prozent(kennzahlen['groessentreffer'])} "
        f"| {kennzahlen['groessentreffer_basis']} |",
        f"| Startpunkt getroffen | {_prozent(kennzahlen['startpunkt_treffer'])} "
        f"| {kennzahlen['startpunkt_basis']} |",
        f"| Pflichtbegriffe | {_prozent(kennzahlen['pflichtbegriffe'])} "
        f"| {kennzahlen['pflichtbegriffe_basis']} |",
        f"| Durchkommensquote | {_prozent(kennzahlen['durchkommensquote'])} "
        f"| {kennzahlen['faelle_gesamt']} |",
        f"| Abschreibquote | {_prozent(kennzahlen['abschreibquote'])} "
        f"| {kennzahlen['abschreibquote_basis']} |",
        f"| Modellaufrufe, Wiederholungen eingeschlossen "
        f"| {kennzahlen.get('modellaufrufe', '—')} | |",
    ]
    zeiten = kennzahlen["sekunden_schnellster"], kennzahlen["sekunden_mittlerer"], kennzahlen["sekunden_langsamster"]
    if all(wert is not None for wert in zeiten):
        zeilen.append(
            f"| Zeit schnellster / mittlerer / langsamster "
            f"| {zeiten[0]:.0f} / {zeiten[1]:.0f} / {zeiten[2]:.0f} s | |"
        )
    ohne = [e.fall_id for e in ergebnisse if not e.durchgekommen and "Erzählung" in e.ursache]
    if ohne:
        zeilen += ["", f"**Ohne Erzählung übersprungen:** {', '.join(ohne)}"]
    return "\n".join(zeilen)


def vergleiche(vorher: pathlib.Path, nachher: pathlib.Path) -> str:
    """Zwei Läufe je Kennzahl nebeneinander.

    Der eigentliche Zweck: nicht eine Zahl, sondern ob eine Änderung geholfen
    hat.
    """

    a = json.loads((vorher / "kennzahlen.json").read_text(encoding="utf-8"))
    b = json.loads((nachher / "kennzahlen.json").read_text(encoding="utf-8"))
    zeilen = [
        f"Vergleich {vorher.name} → {nachher.name}",
        "",
        "| Kennzahl | vorher | nachher | |",
        "|---|---|---|---|",
    ]
    # Bei der Fehlstart-Quote und der Abschreibquote ist weniger besser.
    weniger_ist_besser = {"fehlstart_quote", "abschreibquote"}
    for name in KENNZAHLEN:
        alt, neu = a.get(name), b.get(name)
        if alt is None and neu is None:
            richtung = "—"
        elif alt is None or neu is None:
            richtung = "?"
        elif alt == neu:
            richtung = "gleich"
        else:
            besser = (neu < alt) if name in weniger_ist_besser else (neu > alt)
            richtung = "besser" if besser else "schlechter"
        zeilen.append(
            f"| {name} | {_prozent(alt)} | {_prozent(neu)} | {richtung} |"
        )
    return "\n".join(zeilen)


#: Der Zähler des letzten Laufs. Eine Liste, damit `main` ihn sieht, ohne
#: dass `fahre_lauf` seine Signatur ändern muss — der Trockenlauf ruft sie.
verbrauch: list[object] = []


def fahre_lauf(
    faelle: list[dict], *, client=None, hoechstens: int | None = None
) -> list[Fallergebnis]:
    """Fährt jeden Fall mit einer Erzählung durch die Anwendung.

    `client` wird für den Trockenlauf hereingereicht. Ohne ihn wird die
    Anwendung geladen — und dann kostet es Geld.
    """

    if client is None:  # pragma: no cover - im Test immer gesetzt
        from dotenv import load_dotenv

        load_dotenv(WURZEL / ".env")
        from fastapi.testclient import TestClient

        from app.main import app

        with TestClient(app) as echter_client:
            return fahre_lauf(
                faelle, client=echter_client, hoechstens=hoechstens
            )

    zaehler = Aufrufzaehler()
    # **Erst ein sichtbarer Handler, dann der Zähler.**
    #
    # Ohne eigenen Handler schreibt Python Warnungen über `lastResort`
    # nach stderr. Sobald irgendein Handler am Logger hängt, hört das auf
    # — der Zähler allein verschluckt dann jede Warnung und jeden Fehler.
    # Ein Instrument, das die Anzeige abschaltet, ist schlimmer als keins.
    logging.basicConfig(level=logging.WARNING, format="%(message)s")
    app_logger = logging.getLogger("app")
    app_logger.addHandler(zaehler)
    app_logger.setLevel(logging.INFO)
    ergebnisse: list[Fallergebnis] = []
    verbrauch.append(zaehler)
    for fall in faelle:
        vorher = zaehler.modellaufrufe
        # Ein Fall kostet drei Aufrufe, kann aber mit Wiederholungen mehr
        # kosten. Angehalten wird **vor** dem Fall: Ein abgebrochener
        # Durchlauf ist bezahlt und liefert nichts.
        if hoechstens is not None and zaehler.modellaufrufe + 3 > hoechstens:
            ergebnisse.append(
                Fallergebnis(
                    fall_id=str(fall.get("fall_id") or "?"),
                    titel=str(fall.get("titel") or ""),
                    durchgekommen=False,
                    ursache=f"nicht gefahren — Budget {hoechstens} erreicht",
                )
            )
            print(
                f"  {fall.get('fall_id')}: nicht gefahren, Budget erreicht "
                f"({zaehler.modellaufrufe} Aufrufe)",
                flush=True,
            )
            continue
        erzaehlung = str(fall.get("erzaehlung") or "").strip()
        if not erzaehlung:
            ergebnisse.append(
                Fallergebnis(
                    fall_id=str(fall.get("fall_id") or "?"),
                    titel=str(fall.get("titel") or ""),
                    durchgekommen=False,
                    ursache="keine Erzählung hinterlegt",
                )
            )
            print(f"  {fall.get('fall_id')}: übersprungen — keine Erzählung", flush=True)
            continue

        client.cookies.clear()
        client.post("/begin", follow_redirects=False)
        begonnen = perf_counter()
        client.post(
            "/interview", data={"free_description": erzaehlung}, follow_redirects=False
        )
        erster = client.post("/analyze")
        if erster.status_code != 200:
            ergebnisse.append(
                bewerte_fall(fall, None, ursache=f"Aufruf 1: {erster.status_code}")
            )
            print(f"  {fall.get('fall_id')}: GESCHEITERT bei Aufruf 1, "
                  f"{zaehler.modellaufrufe - vorher} Aufrufe", flush=True)
            continue
        # Der Agentenschritt wird übersprungen, damit die Fälle vergleichbar
        # bleiben und kein dritter Aufruf dazwischenkommt.
        client.post("/verstanden", data={"weiter": "ja"}, follow_redirects=False)
        zweiter = client.post("/analyze")
        dauer = perf_counter() - begonnen
        if zweiter.status_code != 200:
            ergebnisse.append(
                bewerte_fall(
                    fall, None, sekunden=dauer, ursache=f"Aufruf 2: {zweiter.status_code}"
                )
            )
            print(f"  {fall.get('fall_id')}: GESCHEITERT bei Aufruf 2, "
                  f"{zaehler.modellaufrufe - vorher} Aufrufe", flush=True)
            continue

        ergebnis = _gespeichert(client)
        treffer = bewerte_fall(
            fall, ergebnis, sekunden=dauer, quellen=_prompt_quellen(erzaehlung)
        )
        ergebnisse.append(treffer)
        print(
            f"  {fall.get('fall_id')}: durch in {dauer:.0f} s, "
            f"{len(treffer.modulnamen)} Module, "
            f"{zaehler.modellaufrufe - vorher} Aufrufe"
            + (f", FEHLSTART: {', '.join(treffer.fehlstart)}" if treffer.fehlstart else ""),
            flush=True,
        )
    return ergebnisse


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


def _prompt_quellen(erzaehlung: str) -> list[str]:
    """Woraus abgeschrieben werden könnte: der Prompt und das abgerufene Wissen.

    Die Erzählung gehört **nicht** dazu — aus ihr zu zitieren ist erwünscht
    und wird an anderer Stelle sogar erzwungen.
    """

    from app.services.analysis_service import diagnose_context

    prompts = [
        (WURZEL / f"app/prompts/{name}.md").read_text(encoding='utf-8')
        for name in (
            "diagnose",
            "zielarchitektur",
            "ergebnis_teil2a",
            "ergebnis_teil2b",
        )
    ]
    return [*prompts, *diagnose_context(erzaehlung)]


def main() -> int:
    zerleger = argparse.ArgumentParser(description=__doc__)
    zerleger.add_argument(
        "--vergleiche",
        nargs=2,
        type=pathlib.Path,
        metavar=("VORHER", "NACHHER"),
        default=None,
    )
    zerleger.add_argument("--gold", type=pathlib.Path, default=GOLD_VERZEICHNIS)
    zerleger.add_argument(
        "--hoechstens",
        type=int,
        default=None,
        help="Höchstens so viele Modellaufrufe, Wiederholungen mitgezählt.",
    )
    argumente = zerleger.parse_args()

    if argumente.vergleiche:
        print(vergleiche(*argumente.vergleiche))
        return 0

    faelle = lade_faelle(argumente.gold)
    if not faelle:
        print(f"Keine Golddateien in {argumente.gold}.")
        return 1
    mit_erzaehlung = sum(1 for fall in faelle if str(fall.get("erzaehlung") or "").strip())
    print(
        f"{len(faelle)} Fälle, davon {mit_erzaehlung} mit Erzählung. "
        f"Das kostet {mit_erzaehlung * 2} Modellaufrufe.\n"
    )

    ergebnisse = fahre_lauf(faelle, hoechstens=argumente.hoechstens)
    kennzahlen = bewerte_lauf(ergebnisse)
    # Was der Lauf wirklich gekostet hat, Wiederholungen eingeschlossen.
    if verbrauch:
        kennzahlen["modellaufrufe"] = verbrauch[-1].modellaufrufe
        kennzahlen["einbettungen"] = verbrauch[-1].einbettungen
    text = berichte(ergebnisse, kennzahlen)

    # Datum **und Uhrzeit**: Zwei Läufe am selben Tag sind der Regelfall.
    # Ohne Uhrzeit überschreibt der zweite den ersten, bevor ihn jemand
    # gelesen hat — ein Lauf, der API-Kosten verursacht hat, darf nicht
    # an einem Ordnernamen sterben.
    ziel = MESSUNGEN / f"gold_{datetime.now():%Y%m%d_%H%M}"
    ziel.mkdir(parents=True, exist_ok=True)
    (ziel / "kennzahlen.json").write_text(
        json.dumps(kennzahlen, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (ziel / "faelle.json").write_text(
        json.dumps([asdict(e) for e in ergebnisse], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (ziel / "bericht.md").write_text(text, encoding="utf-8")
    print("\n" + text)
    print(f"\ngeschrieben: {ziel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
