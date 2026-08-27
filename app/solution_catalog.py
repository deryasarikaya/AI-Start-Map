"""Der Lösungskatalog — die Menge dessen, was AI Start Map anbieten darf.

**Hier sitzt das Geländer.** Nicht der Abruf: Der schlägt vor, was zur Diagnose
passt, aber er begrenzt nichts. Begrenzt wird hier, und zwar serverseitig:

1. `zur_auswahl()` gibt dem Modell **alle** freigegebenen Familien kompakt zur
   Auswahl — Kennung, Name, worum es geht, wofür sie taugt und wofür nicht.
2. Das Modell antwortet mit Kennungen, nicht mit erfundenen Modulen.
3. `pruefe_auswahl()` prüft jede Kennung gegen die Freigabeliste.
4. `pruefe_baustein()` prüft, dass ein Modul auf einen Baustein **dieser**
   Familie zurückgeht — sonst könnte „Autonomer KI-Einkaufsagent" mit der
   Kennung SF-01 durchrutschen.
5. `vollstaendig()` lädt danach die ganzen Datensätze für die Formulierung.

Freigegeben ist, was in `knowledge/catalog/FREIGABE.json` steht. Eine Familie
abschalten heißt: aus dieser Liste nehmen. Kein Codeeingriff, kein Umbau der
Pipeline.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

WURZEL = Path(__file__).resolve().parents[1]
KATALOG_DATEI = WURZEL / "knowledge/candidates/batch_10/03_solution_families.jsonl"
FAEHIGKEITEN_DATEI = WURZEL / "knowledge/candidates/batch_10/04_automation_capabilities.jsonl"
ZIELBILDER_DATEI = WURZEL / "knowledge/candidates/batch_10/05_target_architectures.jsonl"
FREIGABE_DATEI = WURZEL / "knowledge/catalog/FREIGABE.json"


class KatalogFehlt(RuntimeError):
    """Ohne Katalog gibt es keine erlaubte Lösungsmenge — und keine Empfehlung.

    Lieber laut scheitern als still alles erlauben: Ein leerer Katalog, der wie
    ein voller behandelt wird, wäre genau das Loch, das dieser Modul schliesst.
    """


@dataclass(frozen=True)
class Familie:
    """Eine freigegebene Lösungsfamilie, so wie das Modell sie sehen darf."""

    kennung: str
    name: str
    worum_es_geht: str
    geeignet_wenn: tuple[str, ...] = ()
    nicht_geeignet_wenn: tuple[str, ...] = ()
    bausteine: tuple[str, ...] = ()
    braucht_capabilities: tuple[str, ...] = ()
    bleibt_beim_menschen: tuple[str, ...] = ()
    setzt_voraus: tuple[str, ...] = ()
    kundennaher_name: str = ""
    gilt_fuer_betriebsarten: tuple[str, ...] = ()
    #: **Wann diese Familie im Ausbau an der Reihe ist.**
    #:
    #: Der Katalog weiss, dass ein Kundenportal nicht der erste Schritt
    #: ist und eine Nachfass-Automatik eine Historie braucht. Ohne
    #: dieses Feld muss das Modell die Reihenfolge raten - und rat es,
    #: bleibt es bei der Familie, die es schon gewaehlt hat.
    reihenfolge_hinweis: str = ""
    #: Welche Familien ueblicherweise daneben stehen. Der Faden, an dem
    #: entlang ein Ausbaupfad ueberhaupt entsteht.
    typische_kombination: tuple[str, ...] = ()
    voller_datensatz: dict = field(default_factory=dict, repr=False)


def _zeilen(pfad: Path) -> list[dict]:
    if not pfad.is_file():
        return []
    datensaetze: list[dict] = []
    for zeile in pfad.read_text(encoding="utf-8").splitlines():
        if not zeile.strip():
            continue
        try:
            datensatz = json.loads(zeile)
        except json.JSONDecodeError:
            logger.warning("catalog.broken_line datei=%s", pfad.name)
            continue
        if isinstance(datensatz, dict):
            datensaetze.append(datensatz)
    return datensaetze


def _texte(datensatz: dict, feld: str) -> tuple[str, ...]:
    wert = datensatz.get(feld) or []
    if isinstance(wert, str):
        return (wert,)
    return tuple(str(eintrag) for eintrag in wert if str(eintrag).strip())


@lru_cache(maxsize=1)
def freigegebene_kennungen() -> frozenset[str]:
    """Welche Familien empfohlen werden dürfen.

    Aus `FREIGABE.json`. Fehlt die Datei, ist nichts freigegeben — nicht alles.
    """

    if not FREIGABE_DATEI.is_file():
        raise KatalogFehlt(
            f"Die Freigabeliste fehlt: {FREIGABE_DATEI}. Ohne sie steht nicht "
            "fest, was empfohlen werden darf."
        )
    daten = json.loads(FREIGABE_DATEI.read_text(encoding="utf-8"))
    return frozenset(str(kennung).strip() for kennung in daten.get("erlaubt") or [])


@lru_cache(maxsize=1)
def katalog() -> dict[str, Familie]:
    """Alle freigegebenen Familien, nach Kennung.

    Eine Familie im Bestand, die nicht freigegeben ist, kommt hier nicht vor —
    auch dann nicht, wenn sie im Index liegt und der Abruf sie findet. Der
    Abruf darf vorschlagen; erlauben tut nur diese Liste.
    """

    erlaubt = freigegebene_kennungen()
    gefunden: dict[str, Familie] = {}
    uebergangen: list[str] = []
    for datensatz in _zeilen(KATALOG_DATEI):
        kennung = str(datensatz.get("chunk_id") or "").strip()
        if not kennung:
            continue
        if kennung not in erlaubt or datensatz.get("enabled_for_recommendation") is False:
            uebergangen.append(kennung)
            continue
        gefunden[kennung] = Familie(
            kennung=kennung,
            name=str(datensatz.get("familie_name") or datensatz.get("title") or kennung),
            worum_es_geht=str(datensatz.get("worum_es_geht") or ""),
            geeignet_wenn=_texte(datensatz, "geeignet_wenn"),
            nicht_geeignet_wenn=_texte(datensatz, "nicht_geeignet_wenn"),
            bausteine=_texte(datensatz, "bausteine"),
            braucht_capabilities=_texte(datensatz, "braucht_capabilities"),
            bleibt_beim_menschen=_texte(datensatz, "bleibt_beim_menschen"),
            setzt_voraus=_texte(datensatz, "setzt_voraus"),
            kundennaher_name=str(datensatz.get("kundennaher_name") or ""),
            gilt_fuer_betriebsarten=_texte(datensatz, "gilt_fuer_betriebsarten"),
            reihenfolge_hinweis=str(datensatz.get("reihenfolge_hinweis") or ""),
            typische_kombination=_texte(datensatz, "typische_kombination"),
            voller_datensatz=datensatz,
        )
    if not gefunden:
        raise KatalogFehlt(
            f"Aus {KATALOG_DATEI.name} kam keine freigegebene Familie. Entweder "
            "fehlt die Datei, oder die Freigabeliste passt nicht zu ihr."
        )
    if uebergangen:
        logger.info(
            "catalog.not_released ids=%s anzahl_freigegeben=%d",
            sorted(uebergangen),
            len(gefunden),
        )
    return gefunden


def zur_auswahl(bevorzugt: list[str] | None = None) -> list[dict[str, object]]:
    """Der ganze erlaubte Katalog, kompakt, für die Auswahlentscheidung.

    Vierundzwanzig kurze Einträge passen in einen Prompt. Deshalb bekommt das
    Modell **alle** und nicht nur die abgerufenen: Ein schlechter Treffer im
    Abruf soll nicht verhindern, dass die richtige Familie überhaupt wählbar
    ist. Was der Abruf gefunden hat, steht als Hinweis dabei.

    **Mit Reihenfolge.** `reihenfolge_hinweis` und `typische_kombination`
    stehen dabei, weil der Ausbaupfad sonst geraten wird. Ein Modell, das
    nicht weiss, was worauf aufbaut, hängt an die gewählte Familie noch
    eine Variante derselben Familie — und der Ausblick zeigt zum dritten
    Mal dasselbe Thema.
    """

    vorne = list(bevorzugt or [])
    eintraege = [
        {
            "id": familie.kennung,
            "name": familie.name,
            "worum_es_geht": familie.worum_es_geht,
            "geeignet_wenn": list(familie.geeignet_wenn),
            "nicht_geeignet_wenn": list(familie.nicht_geeignet_wenn),
            "reihenfolge_hinweis": familie.reihenfolge_hinweis,
            "typische_kombination": list(familie.typische_kombination),
            "vom_abruf_vorgeschlagen": familie.kennung in vorne,
        }
        for familie in katalog().values()
    ]
    # Die vorgeschlagenen zuerst, sonst nach Kennung — eine feste Reihenfolge
    # macht zwei Läufe vergleichbar.
    eintraege.sort(key=lambda eintrag: (not eintrag["vom_abruf_vorgeschlagen"], eintrag["id"]))
    return eintraege


def pruefe_auswahl(kennungen: list[str]) -> tuple[list[str], list[str]]:
    """Trennt die gültigen Kennungen von den erfundenen.

    Zurück kommen zwei Listen: was im freigegebenen Katalog steht, und was
    nicht. Die zweite ist der Grund, warum es diese Funktion gibt.
    """

    erlaubt = katalog()
    gueltig: list[str] = []
    ungueltig: list[str] = []
    for roh in kennungen:
        kennung = str(roh).strip().upper()
        if kennung in erlaubt and kennung not in gueltig:
            gueltig.append(kennung)
        elif kennung not in erlaubt:
            ungueltig.append(str(roh))
    return gueltig, ungueltig


def _vergleichbar(text: str) -> str:
    """Macht zwei Bausteinnamen vergleichbar, ohne sie zu verändern."""

    return re.sub(r"[^a-zäöüß0-9 ]+", " ", str(text).casefold()).strip()


def pruefe_baustein(baustein: str, kennungen: list[str]) -> str | None:
    """Gehört dieser Baustein zu einer der genannten Familien?

    Zurück kommt die Kennung der Familie, zu der er gehört — oder `None`.
    Verglichen wird ohne Rücksicht auf Gross- und Kleinschreibung und
    Satzzeichen: Der Wortlaut muss stimmen, die Schreibweise nicht.
    """

    gesucht = _vergleichbar(baustein)
    if not gesucht:
        return None
    erlaubt = katalog()
    for kennung in kennungen:
        familie = erlaubt.get(str(kennung).strip().upper())
        if familie is None:
            continue
        if any(_vergleichbar(eigener) == gesucht for eigener in familie.bausteine):
            return familie.kennung
    return None


def bausteine_von(kennungen: list[str]) -> dict[str, list[str]]:
    """Die zulässigen Bausteine der genannten Familien, je Kennung."""

    erlaubt = katalog()
    return {
        kennung: list(erlaubt[kennung].bausteine)
        for kennung in kennungen
        if kennung in erlaubt
    }


def vollstaendig(kennungen: list[str]) -> list[dict]:
    """Die ganzen Datensätze der ausgewählten Familien.

    Erst nach der Prüfung: Was hier herauskommt, geht in die Formulierung, und
    was in die Formulierung geht, darf beim Kunden landen.
    """

    erlaubt = katalog()
    return [
        erlaubt[kennung].voller_datensatz
        for kennung in kennungen
        if kennung in erlaubt
    ]


def faehigkeiten_zu(kennungen: list[str]) -> list[dict]:
    """Die Capabilities, die die ausgewählten Familien brauchen.

    CAP sagt, **wie** eine Familie technisch funktioniert. Eine Capability
    ersetzt keine Familie und erzeugt keine — sie konkretisiert eine bereits
    ausgewählte.
    """

    erlaubt = katalog()
    gebraucht: list[str] = []
    for kennung in kennungen:
        familie = erlaubt.get(kennung)
        if familie is None:
            continue
        for cap in familie.braucht_capabilities:
            if cap not in gebraucht:
                gebraucht.append(cap)
    nach_kennung = {
        str(datensatz.get("chunk_id")): datensatz
        for datensatz in _zeilen(FAEHIGKEITEN_DATEI)
    }
    return [nach_kennung[cap] for cap in gebraucht if cap in nach_kennung]


def _qualifiziert(treffer: int, ausgewaehlt: int) -> bool:
    """Ob eine Überdeckung gross genug ist, um ein Zielbild zu tragen.

    Zwei Bedingungen, beide müssen gelten:

    1. **Mindestens zwei** ausgewählte Familien liegen im Zielbild. Ein
       Zielbild sagt, wie Familien zusammenspielen — bei einer einzigen gibt
       es kein Zusammenspiel, nur eine Lösung.
    2. **Mindestens die Hälfte** der Auswahl liegt darin. Trifft ein Zielbild
       zwei von sechs gewählten Familien, beschreibt es nicht diese Lösung,
       sondern eine andere, an der die Lösung zufällig streift.

    Eine einzelne Familie bleibt eine vollkommen gültige Lösung. Sie bekommt
    nur kein Mehrfamilien-Zielbild.
    """

    return treffer >= 2 and treffer * 2 >= ausgewaehlt


def _auf_die_auswahl_gekuerzt(datensatz: dict, ausgewaehlt: set[str]) -> dict:
    """Macht aus dem Zielbild einen reinen Kompositionshinweis.

    **Ein Zielbild darf strukturieren, nicht erweitern.** Der volle Datensatz
    nennt Familien, die dieser Betrieb nicht bekommt, dazu eine kleinste und
    eine grösste Ausbaustufe. Ginge das so in die Formulierung, stünde am Ende
    beim Kunden eine Lösung, die niemand ausgewählt und niemand geprüft hat.

    Übrig bleiben deshalb nur: Kennung, Titel und die Ebenen, in denen
    mindestens eine **ausgewählte** Familie liegt — und in diesen Ebenen auch
    nur die ausgewählten Kennungen. Eine Ebene, von der danach nichts übrig
    ist, fällt ganz weg.
    """

    ebenen: list[dict] = []
    for ebene in datensatz.get("ebenen") or []:
        beteiligt = [
            str(kennung)
            for kennung in ebene.get("beteiligte_familien") or []
            if str(kennung) in ausgewaehlt
        ]
        if not beteiligt:
            continue
        ebenen.append(
            {
                "ebene": ebene.get("ebene", ""),
                "was_dort_passiert": ebene.get("was_dort_passiert", ""),
                "beteiligte_familien": beteiligt,
            }
        )
    return {
        "chunk_id": datensatz.get("chunk_id", ""),
        "title": datensatz.get("title", ""),
        "ebenen": ebenen,
    }


def zielbild_zu(kennungen: list[str]) -> dict | None:
    """Das Kompositionsmuster zur Auswahl — gekürzt auf die Auswahl.

    Zielbilder sagen, wie mehrere Familien zu einem grösseren Ganzen
    zusammengehen, damit nicht fünf kleine Einzelautomationen herauskommen.
    Sie sind ein **interner** Hinweis für die Formulierung und stehen nie so
    beim Kunden.

    Gewählt wird das Zielbild mit der grössten Überdeckung, das
    `_qualifiziert` besteht; passt keines, gibt es keines. Bei Gleichstand
    gewinnt das erste in der Reihenfolge der Katalogdatei — dieselbe Auswahl
    führt so immer zum selben Zielbild.

    Enthält ein Zielbild eine nicht freigegebene Familie, zählt sie nicht mit.
    """

    ausgewaehlt = set(kennungen)
    bestes: tuple[int, dict] | None = None
    for datensatz in _zeilen(ZIELBILDER_DATEI):
        enthalten = {
            str(kennung)
            for kennung in datensatz.get("enthaltene_familien") or []
            if str(kennung) in katalog()
        }
        ueberdeckung = len(enthalten & ausgewaehlt)
        if not _qualifiziert(ueberdeckung, len(ausgewaehlt)):
            continue
        # Echt groesser: Bei Gleichstand bleibt das frueher gelesene stehen.
        if bestes is None or ueberdeckung > bestes[0]:
            bestes = (ueberdeckung, datensatz)
    if bestes is None:
        return None
    return _auf_die_auswahl_gekuerzt(bestes[1], ausgewaehlt)
