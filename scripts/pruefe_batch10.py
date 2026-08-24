"""Prüft die Wissensdateien von Batch 10, bevor sie in den Index gehen.

Ein Fehler in einer JSONL-Zeile fällt sonst erst beim Indexaufbau auf — also
nach Stunden Arbeit. Dieses Skript macht **keine** Modellaufrufe und kostet
nichts; es liest nur Dateien.

    .venv/Scripts/python.exe scripts/pruefe_batch10.py

Es läuft auch mit unvollständigem Batch: Fehlende Dateien werden gemeldet,
nicht als Fehler gewertet. Wer nacheinander schreibt, kann nach jeder Datei
prüfen.

Die Feldlisten stehen **nicht** hier, sondern werden aus
`knowledge/candidates/batch_10/SPEZIFIKATION.md` gelesen. Eine zweite Kopie
wäre nach der ersten Änderung falsch. Findet das Einlesen für einen Typ keine
Felder, sagt das Skript das laut — eine stille Prüfung, die nichts prüft, wäre
schlimmer als keine.

Zusätzlich wird jedes `signale_in_der_erzaehlung` gegen die Erzählungen des
Goldbestands gehalten. Fünf gleiche Wörter hintereinander sind ein Fehler:
Wissen, das aus einem Messfall abgeschrieben ist, findet genau diesen Fall
wieder und macht die spätere Messung wertlos.

Rückgabewert: 0, wenn nichts zu beanstanden ist (Warnungen zählen nicht als
Fehler), sonst 1.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from dataclasses import dataclass, field

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WURZEL = pathlib.Path(__file__).resolve().parents[1]
BATCH = WURZEL / "knowledge/candidates/batch_10"
SPEZIFIKATION = BATCH / "SPEZIFIKATION.md"
BESTAND = (WURZEL / "knowledge/runtime", WURZEL / "knowledge/candidates")
#: Die Erzählungen, gegen die später gemessen wird.
GOLDBESTAND = WURZEL / "knowledge/evaluation/gold"

# Damit `app` auch beim Aufruf aus `scripts/` gefunden wird.
sys.path.insert(0, str(WURZEL))

from app.result_schema import normalize_for_quote_match  # noqa: E402

#: Was am Wortrand wegfällt, bevor Wortfolgen verglichen werden. Die
#: Zitatprüfung braucht das nicht — sie vergleicht ganze Zitate. Hier stünde
#: sonst ein Komma zwischen zwei Texten, die Wort für Wort gleich sind.
SATZZEICHEN = ".,;:!?()[]{}\"'„“”‚‘’«»…"

#: Ab wie vielen gleichen Wörtern hintereinander eine Formulierung als
#: abgeschrieben gilt. Vier Wörter treffen sich in zwei Texten über
#: dasselbe Thema von allein; fünf tun das nicht mehr.
ZIRKEL_FENSTER = 5

#: Welcher Typ in welche Datei gehört. Aus der Spezifikation, Abschnitt
#: „Ablage und Format".
#:
#: Die Nummer zählt, nicht der Unterstrich: `03b_..._ergaenzung.jsonl`
#: gehört zu denselben Lösungsfamilien wie `03_...`. Eine Ergänzung, die
#: das Prüfskript stillschweigend überginge, wäre schlimmer als keine —
#: sie sähe geprüft aus.
TYP_JE_DATEI = {
    "01": "business_pattern",
    "02": "diagnostic_pattern",
    "03": "solution_family",
    "04": "automation_capability",
    "05": "target_architecture",
}

#: Die Felder, die in **jedem** Datensatz stehen müssen.
GEMEINSAME_FELDER = (
    "chunk_id",
    "chunk_type",
    "title",
    "batch_id",
    "source_strength",
    "content_origin",
    "is_primary_evidence",
    "process_type",
)

#: Wie eine Kennung aussieht: BP-A, DP-01, SF-15, CAP-12, TA-06.
KENNUNG = re.compile(r"^(?:BP-[A-G]|(?:DP|SF|CAP|TA)-\d{2})$")


@dataclass
class Befund:
    """Was bei der Prüfung herauskam."""

    fehler: list[str] = field(default_factory=list)
    warnungen: list[str] = field(default_factory=list)
    fehlende_dateien: list[str] = field(default_factory=list)
    #: Datei -> Anzahl gelesener Datensätze
    gelesen: dict[str, int] = field(default_factory=dict)
    #: Wie viele Signale gegen wie viele Erzählungen geprüft wurden. Eine
    #: Prüfung, die nichts zu prüfen hatte, soll das sagen können.
    signale_geprueft: int = 0
    goldfaelle: int = 0


def felder_aus_der_spezifikation(batch: pathlib.Path = BATCH) -> dict[str, dict[str, int]]:
    """Liest je Typ die erwarteten Felder und ihre Mindestlängen.

    Aus den eingerückten Blöcken der Spezifikation. Ein Eintrag wie
    `typische_kanaele  Liste, 4–8` wird zu `{"typische_kanaele": 4}`; Felder
    ohne Mengenangabe bekommen 0.
    """

    spezifikation = batch / "SPEZIFIKATION.md"
    if not spezifikation.is_file():
        return {}
    text = spezifikation.read_text(encoding="utf-8")
    je_typ: dict[str, dict[str, int]] = {}
    # Jeder Dateiabschnitt beginnt mit `# Datei N · ...` und nennt darin
    # seinen chunk_type.
    for abschnitt in re.split(r"\n# Datei ", text)[1:]:
        typ = re.search(r"`chunk_type`:\s*`([a-z_]+)`", abschnitt)
        if typ is None:
            continue
        felder: dict[str, int] = {}
        for block in re.findall(r"```\n(.*?)```", abschnitt, re.DOTALL):
            for zeile in block.split("\n"):
                treffer = re.match(r"^([a-zäöüß_]+)\s{2,}(.*)$", zeile.rstrip())
                if treffer is None:
                    continue
                menge = re.search(r"Liste,\s*(\d+)", treffer.group(2))
                felder[treffer.group(1)] = int(menge.group(1)) if menge else 0
        if felder:
            je_typ[typ.group(1)] = felder
    return je_typ


def bestehende_kennungen(batch: pathlib.Path = BATCH) -> dict[str, str]:
    """Alle schon vergebenen `chunk_id` im Bestand, mit ihrer Herkunft."""

    vergeben: dict[str, str] = {}
    for wurzel in BESTAND:
        for pfad in sorted(wurzel.rglob("*.jsonl")):
            if batch in pfad.parents:
                continue
            for zeile in pfad.read_text(encoding="utf-8", errors="replace").splitlines():
                if not zeile.strip():
                    continue
                try:
                    datensatz = json.loads(zeile)
                except json.JSONDecodeError:
                    continue
                kennung = str(datensatz.get("chunk_id") or datensatz.get("id") or "").strip()
                if kennung:
                    vergeben.setdefault(kennung, pfad.relative_to(WURZEL).as_posix())
    return vergeben


def verweise(datensatz: dict[str, object]) -> set[str]:
    """Jede Kennung, die im Datensatz auf einen anderen zeigt.

    Die eigene `chunk_id` zählt nicht als Verweis auf sich selbst.
    """

    gefunden: set[str] = set()

    def geh(wert: object) -> None:
        if isinstance(wert, str):
            if KENNUNG.match(wert.strip()):
                gefunden.add(wert.strip())
        elif isinstance(wert, dict):
            for schluessel, inhalt in wert.items():
                if schluessel != "chunk_id":
                    geh(inhalt)
        elif isinstance(wert, list):
            for inhalt in wert:
                geh(inhalt)

    geh({k: v for k, v in datensatz.items() if k != "chunk_id"})
    return gefunden


def wortfolge(text: str) -> list[str]:
    """Zerlegt einen Text in vergleichbare Wörter.

    Normalisiert wie bei der Zitatprüfung — dieselbe Funktion, nicht eine
    zweite Fassung davon —, danach fallen Satzzeichen am Wortrand weg.
    „suchen," und „suchen" sind dasselbe Wort; ohne diesen Schritt endet
    eine abgeschriebene Stelle am nächsten Komma und rutscht unter fünf
    Wörter durch. Bindestriche mitten im Wort bleiben stehen, sonst zerfiele
    „E-Mail".
    """

    return [
        wort
        for roh in normalize_for_quote_match(text).split()
        if (wort := roh.strip(SATZZEICHEN))
    ]


def erzaehlungen(
    ordner: pathlib.Path = GOLDBESTAND,
) -> dict[str, set[tuple[str, ...]]]:
    """Je Goldfall alle Wortfolgen der Länge `ZIRKEL_FENSTER` seiner Erzählung.

    Normalisiert wie bei der Zitatprüfung — dieselbe Funktion, nicht eine
    zweite Fassung davon. Anführungszeichen und Bindestriche dürfen ein
    Abschreiben nicht verstecken.

    Fehlt der Ordner, kommt ein leeres Ergebnis zurück.
    """

    gefunden: dict[str, set[tuple[str, ...]]] = {}
    if not ordner.is_dir():
        return gefunden
    for pfad in sorted(ordner.glob("*.json")):
        try:
            fall = json.loads(pfad.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(fall, dict):
            continue
        erzaehlung = str(fall.get("erzaehlung") or "").strip()
        if not erzaehlung:
            continue
        woerter = wortfolge(erzaehlung)
        gefunden[str(fall.get("fall_id") or pfad.stem)] = {
            tuple(woerter[stelle : stelle + ZIRKEL_FENSTER])
            for stelle in range(len(woerter) - ZIRKEL_FENSTER + 1)
        }
    return gefunden


def abgeschrieben(
    signal: str, aus: dict[str, set[tuple[str, ...]]]
) -> tuple[str, str] | None:
    """Die erste Wortfolge des Signals, die wörtlich in einer Erzählung steht.

    Zurück kommen die Wortfolge und der Fall, in dem sie steht — sonst
    `None`. Gefundene Folgen werden nach rechts verlängert, solange auch
    das nächste Fenster in derselben Erzählung vorkommt; die Meldung nennt
    dann die ganze Strecke statt der ersten fünf Wörter.
    """

    woerter = wortfolge(signal)
    for stelle in range(len(woerter) - ZIRKEL_FENSTER + 1):
        folge = tuple(woerter[stelle : stelle + ZIRKEL_FENSTER])
        for fall, folgen in sorted(aus.items()):
            if folge not in folgen:
                continue
            ende = stelle + ZIRKEL_FENSTER
            while (
                ende < len(woerter)
                and tuple(woerter[ende - ZIRKEL_FENSTER + 1 : ende + 1]) in folgen
            ):
                ende += 1
            return " ".join(woerter[stelle:ende]), fall
    return None


def lies_datei(pfad: pathlib.Path, befund: Befund) -> list[tuple[int, dict]]:
    """Liest eine JSONL-Datei zeilenweise und meldet kaputte Zeilen."""

    datensaetze: list[tuple[int, dict]] = []
    for nummer, zeile in enumerate(
        pfad.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
    ):
        if not zeile.strip():
            continue
        try:
            datensatz = json.loads(zeile)
        except json.JSONDecodeError as fehler:
            befund.fehler.append(
                f"{pfad.name}:{nummer}  kein gültiges JSON ({fehler.msg})\n"
                f"      {zeile.strip()[:80]}"
            )
            continue
        if not isinstance(datensatz, dict):
            befund.fehler.append(
                f"{pfad.name}:{nummer}  kein JSON-Objekt, sondern "
                f"{type(datensatz).__name__}"
            )
            continue
        datensaetze.append((nummer, datensatz))
    return datensaetze


def pruefe(batch: pathlib.Path = BATCH) -> Befund:
    """Prüft den ganzen Batch und sammelt alles ein, was auffällt."""

    befund = Befund()
    spezifikation = felder_aus_der_spezifikation(batch)
    if not spezifikation:
        befund.fehler.append(
            "Aus SPEZIFIKATION.md liessen sich keine Feldlisten lesen. Entweder "
            "fehlt die Datei, oder ihr Aufbau hat sich geändert — dann prüft "
            "dieses Skript die Pflichtfelder nicht mehr und muss nachgezogen "
            "werden."
        )

    vergeben = bestehende_kennungen(batch)
    gold = erzaehlungen(GOLDBESTAND)
    befund.goldfaelle = len(gold)
    im_batch: dict[str, str] = {}
    alle_verweise: dict[str, list[str]] = {}

    for praefix, erwarteter_typ in sorted(TYP_JE_DATEI.items()):
        treffer = sorted(batch.glob(f"{praefix}*.jsonl"))
        if not treffer:
            befund.fehlende_dateien.append(f"{praefix}*.jsonl  ({erwarteter_typ})")
            continue
        for pfad in treffer:
            datensaetze = lies_datei(pfad, befund)
            befund.gelesen[pfad.name] = len(datensaetze)
            erwartete_felder = spezifikation.get(erwarteter_typ, {})

            for nummer, datensatz in datensaetze:
                ort = f"{pfad.name}:{nummer}"
                kennung = str(datensatz.get("chunk_id") or "").strip()
                typ = str(datensatz.get("chunk_type") or "").strip()

                if not kennung:
                    befund.fehler.append(f"{ort}  chunk_id fehlt oder ist leer")
                if not typ:
                    befund.fehler.append(f"{ort}  chunk_type fehlt oder ist leer")
                if typ and typ != erwarteter_typ:
                    befund.fehler.append(
                        f"{ort}  chunk_type ist „{typ}“, diese Datei verlangt "
                        f"„{erwarteter_typ}“"
                    )
                if "content" in datensatz:
                    befund.fehler.append(
                        f"{ort}  hat ein content-Feld. Die Spezifikation "
                        "verlangt, dass der Indexer den Text aus den Feldern "
                        "baut."
                    )
                if kennung:
                    if kennung in im_batch:
                        befund.fehler.append(
                            f"{ort}  chunk_id „{kennung}“ gibt es schon in "
                            f"{im_batch[kennung]}"
                        )
                    elif kennung in vergeben:
                        befund.fehler.append(
                            f"{ort}  chunk_id „{kennung}“ ist im Bestand schon "
                            f"vergeben ({vergeben[kennung]})"
                        )
                    else:
                        im_batch[kennung] = ort

                fehlend = [
                    feld
                    for feld in (*GEMEINSAME_FELDER, *erwartete_felder)
                    if feld not in datensatz
                ]
                if fehlend:
                    befund.fehler.append(
                        f"{ort}  Pflichtfelder fehlen: {', '.join(sorted(fehlend))}"
                    )
                for feld, mindestens in erwartete_felder.items():
                    wert = datensatz.get(feld)
                    if mindestens and isinstance(wert, list) and len(wert) < mindestens:
                        befund.warnungen.append(
                            f"{ort}  {feld} hat {len(wert)} Einträge, die "
                            f"Spezifikation nennt mindestens {mindestens}"
                        )

                # Der Zirkelschluss: ein Signal, das aus einer der
                # Erzählungen abgeschrieben ist, findet später genau den
                # Messfall wieder, aus dem es stammt. Die Messung sagt dann
                # nur noch, dass zwei Kopien derselben Zeile zueinander
                # passen. Deshalb Fehler und keine Warnung.
                for signal in datensatz.get("signale_in_der_erzaehlung") or []:
                    if not isinstance(signal, str) or not signal.strip():
                        continue
                    befund.signale_geprueft += 1
                    treffer = abgeschrieben(signal, gold)
                    if treffer is None:
                        continue
                    folge, fall = treffer
                    befund.fehler.append(
                        f"{ort}  signale_in_der_erzaehlung: „{folge}“ steht "
                        f"wörtlich in der Erzählung von {fall}. Aus einem "
                        "Messfall abgeschrieben — damit misst der Batch "
                        "später sich selbst."
                    )

                for ziel in verweise(datensatz):
                    alle_verweise.setdefault(ziel, []).append(ort)

    if befund.signale_geprueft and not gold:
        befund.fehler.append(
            f"Der Goldbestand unter {GOLDBESTAND.name}/ liess sich nicht "
            f"lesen, aber es gibt {befund.signale_geprueft} Signale zu "
            "prüfen. Ohne Erzählungen kann der Zirkelschluss nicht "
            "auffallen — die Prüfung wäre still durchgelaufen."
        )

    # Die wichtigste Prüfung zuletzt: Verweise ins Leere.
    for ziel, orte in sorted(alle_verweise.items()):
        if ziel in im_batch or ziel in vergeben:
            continue
        stellen = ", ".join(orte[:4]) + (" …" if len(orte) > 4 else "")
        befund.fehler.append(
            f"Verweis ins Leere: „{ziel}“ wird genannt in {stellen}, "
            "aber es gibt keinen Datensatz dazu"
        )

    return befund


def berichte(befund: Befund, batch: pathlib.Path = BATCH) -> int:
    """Schreibt das Ergebnis so, dass ein Mensch es lesen kann."""

    print(f"Batch 10 in {batch}\n")
    for praefix, typ in sorted(TYP_JE_DATEI.items()):
        # **Alle** Dateien einer Nummer, nicht nur die erste: Zu `03_`
        # gehört auch `03b_..._ergaenzung.jsonl`. Wer nur die erste
        # zeigt, liest einen Bericht, in dem die Ergänzung fehlt,
        # obwohl sie geprüft wurde.
        namen = sorted(n for n in befund.gelesen if n.startswith(praefix))
        if not namen:
            print(f"  {praefix}*.jsonl".ljust(38) + "— noch nicht da")
            continue
        for name in namen:
            eigene = [f for f in befund.fehler if f.startswith(name)]
            zustand = "in Ordnung" if not eigene else f"{len(eigene)} Fehler"
            print(
                f"  {name}".ljust(38)
                + f"{befund.gelesen[name]:3} Datensätze  {zustand}"
            )

    if befund.signale_geprueft:
        print(
            f"\n  {befund.signale_geprueft} Signale gegen "
            f"{befund.goldfaelle} Erzählungen des Goldbestands geprüft"
        )

    if befund.fehlende_dateien:
        print("\nNoch nicht geschrieben (kein Fehler):")
        for eintrag in befund.fehlende_dateien:
            print(f"  {eintrag}")

    if befund.fehler:
        print(f"\n{len(befund.fehler)} Fehler:\n")
        for eintrag in befund.fehler:
            print(f"  {eintrag}")

    if befund.warnungen:
        print(f"\n{len(befund.warnungen)} Warnungen (kein Grund zum Abbrechen):\n")
        for eintrag in befund.warnungen:
            print(f"  {eintrag}")

    if not befund.fehler and befund.gelesen:
        print("\nKeine Fehler. Der Batch kann in den Index.")
    elif not befund.gelesen:
        print("\nNoch keine Datensätze zu prüfen.")
    return 1 if befund.fehler else 0


def main() -> int:
    zerleger = argparse.ArgumentParser(description=__doc__)
    zerleger.add_argument(
        "--batch",
        type=pathlib.Path,
        default=BATCH,
        help="Ein anderer Ordner statt knowledge/candidates/batch_10.",
    )
    batch = zerleger.parse_args().batch
    return berichte(pruefe(batch), batch)


if __name__ == "__main__":
    raise SystemExit(main())
