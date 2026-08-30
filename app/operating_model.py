"""Wie der Betrieb künftig arbeitet — in seiner Sprache, nicht in unserer.

**Was das ist und was es ausdrücklich nicht ist.**

Der Lösungskatalog hat fünfundzwanzig Familien mit Kennungen wie `SF-15`.
Das ist die fachliche Wahrheit dieses Produkts: Was empfohlen werden darf,
steht dort und nirgends sonst. Die Kennungen sind aber nichts, was ein
Betrieb lesen will — und „Sprach- und Telefonworkflow" auch nicht.

Diese Datei legt eine **Darstellungsschicht** darüber: vierzehn Bereiche
mit kundennahen Namen, jeder aus einer oder mehreren Familien
zusammengesetzt. Sie enthält deshalb bewusst **nichts Fachliches**:

- keine Eignung und keine Nicht-Eignung,
- keine Fähigkeiten,
- keine Voraussetzungen,
- keine menschlichen Grenzen,
- keine Empfehlungslogik.

All das steht im Katalog und wird von dort gelesen. Stünde es hier auch,
gäbe es zwei Wahrheiten, die auseinanderlaufen — und die Frage „welche
gilt?" hätte keine gute Antwort.

**Die Gebiete sind die der Karte.** `app/karte.py` teilt den Betrieb seit
Langem in sechs Gebiete und gibt jeder Familie darauf einen festen Platz.
Ein zweites Gebietsschema danebenzustellen hiesse, dieselbe Landschaft
zweimal zu beschreiben. Also werden die sechs übernommen.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Literal

from app import karte, solution_catalog

logger = logging.getLogger(__name__)

#: Die kanonischen Zieltypen. Eine Experience ist das, was der Mensch
#: **vor sich sieht** — nicht das Programm dahinter. Für jeden Typ gibt es
#: später genau eine geprüfte Darstellung; ein unbekannter Typ kommt gar
#: nicht erst durch.
ExperienceType = Literal[
    "voice_assistant",
    "guided_intake",
    "ai_inbox",
    "case_workspace",
    "document_flow",
    "customer_self_service",
    "knowledge_assistant",
    "management_overview",
    "automation_flow",
]

#: Wie ein heutiger Ansichtstyp auf einen Zieltyp fällt. Gespeicherte
#: Läufe sollen lesbar bleiben — ein Ergebnis von gestern darf nicht
#: unlesbar werden, nur weil die Sprache heute anders ist.
ANSICHT_ZU_EXPERIENCE: dict[str, ExperienceType] = {
    "telefonassistent": "voice_assistant",
    "eingangspruefung": "ai_inbox",
    "vorgangsakte": "case_workspace",
    "kundenakte": "case_workspace",
    "dokumentenablage": "document_flow",
    "aussenansicht": "customer_self_service",
    "uebersicht": "management_overview",
    # Ein Nachrichtenverlauf ist das, was in einem Posteingang steht —
    # er zeigt dieselbe Arbeit, nur aus der Nähe.
    "nachrichtenverlauf": "ai_inbox",
    # Eine Terminübersicht ist eine Steuerungsansicht: Sie zeigt, was
    # ansteht, und nicht, wie ein einzelner Fall aussieht.
    "terminuebersicht": "management_overview",
}


@dataclass(frozen=True)
class Bereich:
    """Ein Bereich des Betriebs, wie der Kunde ihn benennen würde.

    `familien` ist die einzige Verbindung nach unten. Was ein Bereich
    kann, wofür er taugt und was er dem Menschen lässt, steht in diesen
    Familien — hier steht nur, wie er heisst und wo er liegt.
    """

    #: Maschinenlesbar, stabil. Kommt nie vor die Augen eines Kunden.
    schluessel: str
    #: Der Name, den der Kunde liest.
    name: str
    #: Eines der sechs Gebiete aus `karte.ZONEN`.
    gebiet: str
    #: Die Familien, aus denen dieser Bereich besteht.
    familien: tuple[str, ...]
    #: Welche Zieltypen zu diesem Bereich passen. Ein Vorschlagsraum,
    #: keine Zuweisung — was tatsächlich gezeigt wird, entscheidet sich
    #: später aus dem Einstieg.
    experience_affinitaeten: tuple[ExperienceType, ...] = ()
    #: Reihenfolge im Arbeitslauf: erst wie Arbeit hereinkommt, zuletzt,
    #: was der Betrieb über sich selbst weiss.
    reihenfolge: int = 0


#: **Die vierzehn Bereiche.** Von Hand gesetzt, nicht berechnet: Welche
#: Familien ein Kunde als *einen* Bereich erlebt, ergibt sich aus keiner
#: Eigenschaft im Katalog. „Termine buchen" und „Kapazität planen" sind
#: fachlich zwei Familien und im Kopf eines Handwerkers eine Sache.
BEREICHE: tuple[Bereich, ...] = (
    Bereich(
        "kundenzugang_intake",
        "Kundenzugang & Anfrageaufnahme",
        "erreichen",
        ("SF-15", "SF-01", "SF-14", "SF-16"),
        ("voice_assistant", "guided_intake", "ai_inbox"),
        1,
    ),
    Bereich(
        "termine_kapazitaet",
        "Termine & Kapazität",
        "auftrag",
        ("SF-06", "SF-18"),
        ("automation_flow", "management_overview"),
        2,
    ),
    Bereich(
        "angebot_uebergabe",
        "Angebot, Auswahl & Übergabe",
        "auftrag",
        ("SF-07", "SF-22"),
        ("case_workspace", "document_flow"),
        3,
    ),
    Bereich(
        "vorgaenge_aufgaben",
        "Vorgänge & Aufgaben",
        "ueberblick",
        ("SF-02", "SF-12"),
        ("case_workspace", "management_overview"),
        4,
    ),
    Bereich(
        "material_beschaffung",
        "Material & Beschaffung",
        "ueberblick",
        ("SF-20",),
        ("automation_flow", "management_overview"),
        5,
    ),
    Bereich(
        "menschen_qualifikation",
        "Menschen & Qualifikation",
        "ueberblick",
        ("SF-21",),
        ("guided_intake", "knowledge_assistant"),
        6,
    ),
    Bereich(
        "service_selfservice",
        "Service & Selbstauskunft",
        "kundensicht",
        ("SF-10", "SF-05"),
        ("customer_self_service", "knowledge_assistant"),
        7,
    ),
    Bereich(
        "dokumente_pruefpfad",
        "Dokumente & Prüfpfad",
        "kundensicht",
        ("SF-03", "SF-19"),
        ("document_flow",),
        8,
    ),
    Bereich(
        "finanzieller_abschluss",
        "Rechnung & Zahlung",
        "danach",
        ("SF-08", "SF-23"),
        ("document_flow", "automation_flow"),
        9,
    ),
    Bereich(
        "wachstum_bindung",
        "Wachstum & Kundenbindung",
        "danach",
        ("SF-17", "SF-13"),
        ("automation_flow",),
        10,
    ),
    Bereich(
        "kunden_objektkontext",
        "Kunden- & Objektkontext",
        "wissen",
        ("SF-24",),
        ("case_workspace",),
        11,
    ),
    Bereich(
        "steuerung_vorschau",
        "Steuerung & Vorschau",
        "wissen",
        ("SF-09", "SF-25"),
        ("management_overview",),
        12,
    ),
    Bereich(
        "wissen_zugaenglich",
        "Wissen zugänglich machen",
        "wissen",
        ("SF-11",),
        ("knowledge_assistant",),
        13,
    ),
    Bereich(
        "daten_systemverbund",
        "Daten- & Systemverbund",
        "wissen",
        ("SF-04",),
        ("automation_flow",),
        14,
    ),
)


#: **Welcher Zieltyp zu welcher Familie gehört.**
#:
#: Eine Ebene feiner als der Bereich, und das ist nötig. „Kundenzugang &
#: Anfrageaufnahme" enthält den Telefonworkflow und den Nachrichten-
#: eingang; nur der erste rechtfertigt einen Sprachassistenten. Hingen die
#: Zieltypen am Bereich, bekäme eine Hausverwaltung ohne Telefonfamilie
#: einen Telefonassistenten als Hauptansicht — gemessen, nicht vermutet.
#:
#: Die Reihenfolge je Familie ist eine Aussage: Was vorn steht, zeigt den
#: Kern dieser Familie am deutlichsten.
FAMILIEN_AFFINITAETEN: dict[str, tuple[ExperienceType, ...]] = {
    "SF-01": ("ai_inbox",),
    "SF-02": ("case_workspace",),
    "SF-03": ("document_flow",),
    "SF-04": ("automation_flow",),
    "SF-05": ("knowledge_assistant", "customer_self_service"),
    "SF-06": ("automation_flow",),
    "SF-07": ("case_workspace", "document_flow"),
    "SF-08": ("document_flow", "automation_flow"),
    "SF-09": ("management_overview",),
    "SF-10": ("customer_self_service",),
    "SF-11": ("knowledge_assistant",),
    "SF-12": ("management_overview", "case_workspace"),
    "SF-13": ("automation_flow",),
    "SF-14": ("guided_intake", "customer_self_service"),
    "SF-15": ("voice_assistant",),
    "SF-16": ("guided_intake",),
    "SF-17": ("automation_flow",),
    "SF-18": ("management_overview", "automation_flow"),
    "SF-19": ("document_flow",),
    "SF-20": ("automation_flow", "management_overview"),
    "SF-21": ("guided_intake", "knowledge_assistant"),
    "SF-22": ("document_flow", "case_workspace"),
    "SF-23": ("automation_flow", "document_flow"),
    "SF-24": ("case_workspace",),
    "SF-25": ("management_overview",),
}


def affinitaeten_von(kennungen: Sequence[str]) -> tuple[ExperienceType, ...]:
    """Die Zieltypen, die genau diese Familien rechtfertigen.

    In der Reihenfolge der Familien, dann der Typen — beides sind
    Aussagen und keine Sortierhilfen. Eine unbekannte Familie trägt
    nichts bei, statt eine Ausnahme zu werfen: Der laute Fall ist
    `pruefe_vollstaendigkeit`.
    """

    gefunden: list[ExperienceType] = []
    for kennung in kennungen:
        for typ in FAMILIEN_AFFINITAETEN.get(str(kennung).strip().upper(), ()):
            if typ not in gefunden:
                gefunden.append(typ)
    return tuple(gefunden)


class BereichsLuecke(RuntimeError):
    """Eine Familie hat keinen Bereich — oder einen Bereich zweimal.

    Ein harter Fehler, kein stiller Ausfall: Eine Familie ohne Bereich
    wäre auf der Ergebnisseite unsichtbar, obwohl sie empfohlen wurde.
    """


def _index() -> dict[str, Bereich]:
    """Familie zu Bereich — und die Prüfung, dass die Tabelle aufgeht.

    Sie läuft bei jedem Zugriff und ist billig. Der Katalog ist eine
    Datei, die sich ändern kann; fällt dabei eine Familie aus der
    Zuordnung, soll es hier auffallen und nicht erst beim Kunden.
    """

    zuordnung: dict[str, Bereich] = {}
    for bereich in BEREICHE:
        for kennung in bereich.familien:
            if kennung in zuordnung:
                raise BereichsLuecke(
                    f"{kennung} steht in zwei Bereichen: "
                    f"{zuordnung[kennung].schluessel} und {bereich.schluessel}."
                )
            zuordnung[kennung] = bereich
    return zuordnung


def bereich_von(kennung: str) -> Bereich | None:
    """Der Bereich, in dem diese Familie sichtbar wird."""

    return _index().get(str(kennung).strip().upper())


def bereiche_fuer(kennungen: list[str]) -> list[Bereich]:
    """Die Bereiche zu diesen Familien, in der Reihenfolge des Arbeitslaufs.

    Mehrere Familien fallen regelmässig in denselben Bereich — genau
    dafür ist er da. Telefon und Anfrageeingang sind zwei Familien und
    für den Betrieb eine Sache.
    """

    gefunden: dict[str, Bereich] = {}
    for kennung in kennungen:
        bereich = bereich_von(kennung)
        if bereich is not None:
            gefunden[bereich.schluessel] = bereich
    return sorted(gefunden.values(), key=lambda b: b.reihenfolge)


def familien_im_bereich(bereich: Bereich, kennungen: list[str]) -> list[str]:
    """Welche der genannten Familien zu diesem Bereich gehören."""

    gesucht = {str(k).strip().upper() for k in kennungen}
    return [k for k in bereich.familien if k in gesucht]


def pruefe_vollstaendigkeit() -> None:
    """Jede freigegebene Familie hat genau einen Bereich.

    Wird beim Start des Zusammenbaus aufgerufen und von einem Test
    geprüft. Ohne diese Zusage könnte eine empfohlene Familie auf der
    Ergebnisseite schlicht fehlen — sichtbar wäre davon nichts.
    """

    zuordnung = _index()
    freigegeben = solution_catalog.freigegebene_kennungen()
    ohne_bereich = sorted(freigegeben - set(zuordnung))
    if ohne_bereich:
        raise BereichsLuecke(
            f"Diese Familien haben keinen Bereich: {ohne_bereich}."
        )
    unbekannt = sorted(set(zuordnung) - freigegeben)
    if unbekannt:
        raise BereichsLuecke(
            f"Diese Bereiche nennen Familien, die es nicht gibt: {unbekannt}."
        )
    ohne_zieltyp = sorted(freigegeben - set(FAMILIEN_AFFINITAETEN))
    if ohne_zieltyp:
        raise BereichsLuecke(
            f"Diese Familien haben keinen Zieltyp: {ohne_zieltyp}."
        )
    gebiete = {zone.kennung for zone in karte.ZONEN}
    fremde = sorted({b.gebiet for b in BEREICHE} - gebiete)
    if fremde:
        raise BereichsLuecke(
            f"Diese Bereiche liegen in keinem Gebiet der Karte: {fremde}."
        )


# --------------------------------------------------------- Das Operating Center


#: Wie die Arbeit zusammenläuft. Nicht jeder Betrieb hat einen
#: gemeinsamen Vorgang: Ein Ingenieurbüro hat einen Wissensraum, ein
#: reiner Durchlaufbetrieb hat eine Strecke.
Zusammenlauf = Literal[
    "shared_work_context",
    "direct_flow",
    "knowledge_space",
    "decision_space",
]

#: Woran die Arbeit hängt. `none` ist eine gültige Antwort — es gibt
#: Betriebe, bei denen nichts gesammelt wird, weil nichts zu sammeln ist.
Bezugsgegenstand = Literal[
    "case",
    "order",
    "customer",
    "asset",
    "project",
    "document_set",
    "knowledge_space",
    "none",
]


@dataclass(frozen=True)
class OperatingCenter:
    """Die Stelle, an der die Arbeit dieses Betriebs zusammenläuft.

    **Warum nicht einfach „gemeinsame Akte".** Der erste Entwurf hatte ein
    festes `shared_work_object`, und für einen Handwerksbetrieb stimmt das
    auch. Für ein Ingenieurbüro nicht: Dort läuft nichts in einer Akte
    zusammen, sondern in einem verlässlichen Projekt- und Wissenskontext.
    Ein Modell, das für jeden Betrieb eine Akte behauptet, beschreibt den
    halben Markt falsch.

    Abgeleitet, nicht erzeugt: aus den Bereichen, die zum Zielbild
    gehören. Kein Modellaufruf, keine erfundene Mitte.
    """

    art: Zusammenlauf
    #: Die Überschrift, die der Kunde liest. Bewusst zurückhaltend
    #: formuliert — die kundennahe Zuspitzung macht später der Aufruf,
    #: der ohnehin ausformuliert.
    label: str
    #: Wozu es da ist, in einem Satz.
    zweck: str
    bezug: Bezugsgegenstand
    #: Die Bereiche, die daran hängen.
    bereich_refs: tuple[str, ...] = field(default_factory=tuple)


#: **Woran die Arbeit hängt, in dieser Reihenfolge.** Der erste Bereich
#: aus dem Zielbild, der hier auftaucht, bestimmt den Bezug. Die Ordnung
#: ist eine fachliche Aussage: Wer Vorgänge führt, sammelt an Vorgängen —
#: auch wenn er nebenbei Dokumente ablegt.
_BEZUG_REIHENFOLGE: tuple[tuple[str, Zusammenlauf, Bezugsgegenstand, str, str], ...] = (
    (
        "vorgaenge_aufgaben",
        "shared_work_context",
        "case",
        "Gemeinsamer Arbeitsstand je Anfrage",
        "Jede Anfrage hat einen Stand, den alle sehen.",
    ),
    (
        "angebot_uebergabe",
        "shared_work_context",
        "order",
        "Gemeinsamer Stand je Auftrag",
        "Vom Angebot bis zur Übergabe hängt alles am selben Auftrag.",
    ),
    (
        "kunden_objektkontext",
        "shared_work_context",
        "customer",
        "Gemeinsamer Kunden- und Objektstand",
        "Was zu einem Kunden oder Objekt gehört, steht an einer Stelle.",
    ),
    (
        "dokumente_pruefpfad",
        "shared_work_context",
        "document_set",
        "Nachvollziehbarer Unterlagenstand",
        "Unterlagen und Freigaben bleiben später nachvollziehbar.",
    ),
    (
        "wissen_zugaenglich",
        "knowledge_space",
        "knowledge_space",
        "Verlässlicher Wissenskontext",
        "Was der Betrieb weiss, ist auffindbar statt nur vorhanden.",
    ),
    (
        "steuerung_vorschau",
        "decision_space",
        "none",
        "Gemeinsame Entscheidungsgrundlage",
        "Was Aufmerksamkeit braucht, ist sichtbar, bevor jemand fragt.",
    ),
)


def operating_center(zielbild_familien: list[str]) -> OperatingCenter:
    """Wo die Arbeit dieses Betriebs zusammenläuft — abgeleitet, nicht geraten.

    Ohne Zielbild oder ohne einen der oben genannten Bereiche bleibt eine
    **Strecke**: Arbeit kommt herein, wird bearbeitet, geht hinaus, und
    nichts sammelt sich dazwischen. Das ist kein Mangel — es gibt
    Betriebe, bei denen genau das stimmt.
    """

    bereiche = {b.schluessel for b in bereiche_fuer(zielbild_familien)}
    for schluessel, art, bezug, label, zweck in _BEZUG_REIHENFOLGE:
        if schluessel in bereiche:
            mitte = OperatingCenter(
                art=art,
                label=label,
                zweck=zweck,
                bezug=bezug,
                bereich_refs=tuple(
                    b.schluessel for b in bereiche_fuer(zielbild_familien)
                ),
            )
            break
    else:
        mitte = OperatingCenter(
            art="direct_flow",
            label="Ein durchgehender Weg",
            zweck="Arbeit läuft ohne Zwischenstopp von vorn nach hinten durch.",
            bezug="none",
            bereich_refs=tuple(
                b.schluessel for b in bereiche_fuer(zielbild_familien)
            ),
        )
    logger.info(
        "operating_center.derived art=%s bezug=%s bereiche=%d",
        mitte.art,
        mitte.bezug,
        len(mitte.bereich_refs),
    )
    return mitte
