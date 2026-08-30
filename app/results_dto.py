"""Ein Vertrag für alles, was die Ergebnisseite zeigt — Web wie PDF.

**Warum das nötig ist.** Die Vorlagen hingen bisher direkt am gespeicherten
Ergebnis. Jede musste sich daraus selbst zusammensuchen, was der Einstieg
ist, welche Ansicht die wichtigste, welche Grenze vom Kunden stammt und
welche aus dem Katalog. Das sind fachliche Entscheidungen, und zwei
Vorlagen treffen sie verschieden — Web und PDF zeigten aus demselben Lauf
verschiedene Empfehlungen, ohne dass jemand etwas geändert hätte.

Hier steht es einmal, geprüft. Beide lesen dasselbe.

**Kein weiterer Modellaufruf.** Alles hier ist bereits entschieden. Was
fehlte, war die Stelle, an der es zusammenkommt.

**Und ein Lauf von gestern geht nicht verloren.** Ergebnisse aus der Zeit
vor dem Entscheidungsvertrag haben keine festgehaltene Entscheidung. Sie
werden angepasst, so weit sie es hergeben, und das Ergebnis sagt
ausdrücklich, dass es angepasst ist. Was ein alter Lauf nicht enthält,
wird nicht erfunden.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

from app import experiences, map_state, operating_model, solution_catalog
from app.experiences import ExperienceAuswahl
from app.map_state import MapState
from app.result_schema import DecisionState, Result

logger = logging.getLogger(__name__)

VERTRAG = "results-v1"

#: Woher eine Grenze kommt. **Der Unterschied ist wichtig genug für ein
#: eigenes Feld:** „Sie wollen keine Preiszusagen" ist eine Aussage über
#: diesen Kunden. „Preise bleiben beim Menschen" ist eine Eigenschaft
#: unseres Katalogs. Beides nebeneinander als seine Entscheidung
#: auszugeben, legt ihm Sätze in den Mund, die er nie gesagt hat.
GrenzenHerkunft = Literal["kunde", "katalog"]


@dataclass(frozen=True)
class Beleg:
    """Ein wörtliches Zitat mit seiner Adresse."""

    id: str
    zitat: str
    bedeutung: str


@dataclass(frozen=True)
class Grenze:
    """Was beim Menschen bleibt — und woher wir das wissen."""

    titel: str
    erlaeuterung: str
    herkunft: GrenzenHerkunft
    #: Nur bei `katalog` gefüllt: aus welcher Familie die Grenze stammt.
    familie: str | None = None


@dataclass(frozen=True)
class Ausblick:
    """Ein Bereich, der nach dem Einstieg dazukommt.

    **Keine Roadmap.** Kein Zeitraum, keine Reihenfolgenummer, keine
    Schätzung. Nur: was dadurch möglich wird und warum es nicht jetzt ist.

    **`phase` ist nicht dekorativ.** Der Ausbaupfad mischt zwei Dinge:
    Bereiche, die zum empfohlenen Zielbild gehören und nur nicht zuerst
    kommen — und Bereiche, die darüber hinausgehen. Auf der Karte sind
    das zwei verschiedene Zustände. Ohne dieses Feld nennte die Karte
    einen Bereich „später" und die Ausblicksliste vier, drei davon im
    Zielbild: genau die Uneinigkeit zwischen zwei Darstellungen, gegen
    die dieser Vertrag gebaut ist.
    """

    outcome: str
    grund_fuer_spaeter: str
    familien: tuple[str, ...]
    #: `target` — gehört zum Zielbild, kommt nur nicht zuerst.
    #: `future` — geht über das Zielbild hinaus.
    phase: Literal["target", "future"]
    bereich: str | None = None
    beleg_refs: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class NichtEmpfohlen:
    """Etwas Naheliegendes, das bewusst nicht kommt."""

    titel: str
    grund: str
    erlaeuterung: str
    familien: tuple[str, ...]
    fehlende_voraussetzung: str | None = None
    beleg_refs: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Uebersicht:
    """Was der Betrieb in den ersten Sekunden verstehen soll.

    Vier Sätze und ein Beleg. Die Ausformulierung macht die Vorlage — hier
    steht, **worauf** sie sich beziehen darf.
    """

    engpass: str
    zielbild_name: str
    zielbild_satz: str
    #: Die Bereiche, mit denen angefangen wird — höchstens zwei.
    einstieg_refs: tuple[str, ...]
    primary_experience: str | None
    #: Die Belege, die den Einstieg tragen.
    beleg_refs: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ResultDTO:
    """Alles, was die Ergebnisseite zeigt — und nichts darüber hinaus."""

    contract_version: str
    #: `results-v1` für einen Lauf mit festgehaltener Entscheidung,
    #: `ergebnis-v6-adaptiert` für einen von vorher.
    herkunft: str
    uebersicht: Uebersicht
    belege: tuple[Beleg, ...]
    entscheidung: DecisionState
    karte: MapState
    ansichten: ExperienceAuswahl
    grenzen: tuple[Grenze, ...]
    mensch_behaelt: tuple[str, ...]
    ausblicke: tuple[Ausblick, ...]
    nicht_empfohlen: tuple[NichtEmpfohlen, ...]
    offene_fragen: tuple[str, ...]

    @property
    def ist_angepasst(self) -> bool:
        """Ob dieser Lauf von vor dem Entscheidungsvertrag stammt."""

        return self.herkunft != VERTRAG


def _entscheidung_aus_altlauf(ergebnis: Result) -> DecisionState:
    """Was sich aus einem Lauf ohne festgehaltene Entscheidung ablesen lässt.

    Genau das und nicht mehr: die Familien der Module als Zielbild, die
    Module auf Stufe `jetzt` als Einstieg, die Ausbaustufen als Späteres.
    Ein Lauf, dem auch das fehlt, ergibt einen leeren Zustand — und dann
    zeigt die Karte eben nichts. Ihm eine Entscheidung anzudichten hiesse,
    einen geprüften Durchlauf zu fälschen.
    """

    zielbild: list[str] = []
    einstieg: list[str] = []
    for modul in ergebnis.module:
        for kennung in modul.solution_family_ids:
            if kennung not in zielbild:
                zielbild.append(kennung)
            if modul.stufe == "jetzt" and kennung not in einstieg:
                einstieg.append(kennung)
    spaeter = [
        kennung
        for stufe in ergebnis.ausbaupfad
        for kennung in stufe.solution_family_ids
        if kennung not in zielbild
    ]
    if zielbild and not einstieg:
        # Ohne Stufenangabe ist das ganze Zielbild der Einstieg. Der
        # Vertrag weist ein Zielbild ohne ersten Schritt sonst zurück.
        einstieg = list(zielbild)
    return DecisionState(
        target_family_ids=zielbild,
        start_family_ids=einstieg,
        future_family_ids=list(dict.fromkeys(spaeter)),
    )


def _grenzen(ergebnis: Result, zielbild: list[str]) -> list[Grenze]:
    """Die Grenzen, nach Herkunft getrennt.

    Vom Kunden zuerst: Was er selbst ausgeschlossen hat, wiegt schwerer
    als das, was unser Katalog ohnehin nicht übernimmt — und der Vertrag
    lässt eine selbst genannte Grenze nur zu, wenn in seiner Erzählung
    wirklich ein Ausschluss steht.
    """

    gefunden = [
        Grenze(g.titel, g.erlaeuterung, "kunde")
        for g in ergebnis.aufgabenteilung.grenzen
    ]
    katalog = solution_catalog.katalog()
    for kennung in zielbild:
        familie = katalog.get(kennung)
        if familie is None:
            continue
        for satz in familie.bleibt_beim_menschen:
            if any(g.titel == satz for g in gefunden):
                continue
            gefunden.append(Grenze(satz, satz, "katalog", kennung))
    return gefunden


def _ausblicke(
    ergebnis: Result, zustand: DecisionState, karte: MapState
) -> list[Ausblick]:
    """Zwei bis vier Bereiche, die später möglich werden — **nie aufgefüllt**.

    Quelle ist der Ausbaupfad: Dort steht bereits, welcher Bereich
    dazukommt und was der Betrieb dann nicht mehr selbst macht. Die
    Begründung „warum später" nimmt, wenn vorhanden, die Abdeckung dazu —
    dort hat der Planner sie in einem Satz geschrieben.
    """

    gruende = {
        kennung: eintrag.explanation
        for eintrag in (
            zustand.coverage.items if zustand.coverage is not None else []
        )
        if eintrag.disposition == "future"
        for kennung in eintrag.family_refs
    }
    gefunden: list[Ausblick] = []
    for stufe in ergebnis.ausbaupfad:
        if stufe.stufe == "jetzt":
            # Die erste Stufe ist die Grundlage, die gerade empfohlen
            # wurde. Sie als Ausblick zu zeigen, wäre eine Wiederholung.
            continue
        familien = tuple(stufe.solution_family_ids)
        bereiche = operating_model.bereiche_fuer(list(familien))
        grund = next(
            (gruende[k] for k in familien if k in gruende),
            "Setzt auf dem auf, was jetzt entsteht.",
        )
        gefunden.append(
            Ausblick(
                outcome=stufe.nutzen or stufe.name,
                grund_fuer_spaeter=grund,
                familien=familien,
                # **Die Karte ist die Quelle, nicht eine zweite Rechnung.**
                # Ob eine Familie im Zielbild steht, ist nicht dieselbe
                # Frage: Eine neue Familie kann in einem Bereich liegen,
                # der schon leuchtet. Gemessen am Heizungsfall trat genau
                # das ein — der Ausblick nannte den Eingang „später",
                # während er auf der Karte der Einstieg war.
                phase=(
                    "future"
                    if bereiche and bereiche[0].schluessel in karte.future
                    else "target"
                ),
                bereich=bereiche[0].schluessel if bereiche else None,
            )
        )
    return gefunden[:4]


def _uebersicht(
    ergebnis: Result,
    zustand: DecisionState,
    karte: MapState,
    ansichten: ExperienceAuswahl,
) -> Uebersicht:
    """Der erste Bildschirm — worauf er sich berufen darf.

    Die Belege sind die des Einstiegs: die Signale, die `start` geworden
    sind, und ihre Zitate. Ohne diese Verbindung wäre der Beleg neben der
    Empfehlung ein hübsches Zitat und kein Grund.
    """

    einstiegssignale = {
        eintrag.signal_id
        for eintrag in (zustand.coverage.items if zustand.coverage is not None else [])
        if eintrag.disposition == "start"
    }
    belege = [
        bezug
        for signal in zustand.signals
        if signal.id in einstiegssignale
        for bezug in signal.evidence_refs
    ]
    return Uebersicht(
        engpass=ergebnis.kurzfassung.engpass_satz,
        zielbild_name=ergebnis.zielbild.name,
        zielbild_satz=ergebnis.zielbild.beschreibung,
        einstieg_refs=karte.start,
        primary_experience=(
            ansichten.primary.typ if ansichten.primary is not None else None
        ),
        beleg_refs=tuple(dict.fromkeys(belege)),
    )


def von_ergebnis(ergebnis: Result) -> ResultDTO:
    """Der Vertrag zu einem gespeicherten Lauf — für Web und PDF derselbe."""

    angepasst = ergebnis.entscheidung is None
    zustand = (
        _entscheidung_aus_altlauf(ergebnis)
        if angepasst
        else ergebnis.entscheidung
    )
    karte = map_state.aus_entscheidung(zustand)
    ansichten = experiences.auswahl(zustand, list(ergebnis.ansichten))
    dto = ResultDTO(
        contract_version=VERTRAG,
        herkunft="ergebnis-v6-adaptiert" if angepasst else VERTRAG,
        uebersicht=_uebersicht(ergebnis, zustand, karte, ansichten),
        belege=tuple(
            Beleg(b.id, b.zitat, b.bedeutung) for b in zustand.evidence
        ),
        entscheidung=zustand,
        karte=karte,
        ansichten=ansichten,
        grenzen=tuple(_grenzen(ergebnis, zustand.target_family_ids)),
        mensch_behaelt=tuple(ergebnis.aufgabenteilung.mensch),
        ausblicke=tuple(_ausblicke(ergebnis, zustand, karte)),
        nicht_empfohlen=tuple(
            NichtEmpfohlen(
                titel=absage.titel,
                grund=absage.grund,
                erlaeuterung=absage.erlaeuterung,
                familien=tuple(absage.family_refs),
                fehlende_voraussetzung=absage.fehlende_voraussetzung,
                beleg_refs=tuple(absage.evidence_refs),
            )
            for absage in zustand.why_not
        ),
        offene_fragen=tuple(
            signal.statement
            for signal in zustand.signals
            if signal.id in zustand.open_signal_ids
        ),
    )
    logger.info(
        "results_dto.built herkunft=%s einstieg=%s primary=%s ausblicke=%d "
        "grenzen=%d nicht_empfohlen=%d offen=%d",
        dto.herkunft,
        dto.uebersicht.einstieg_refs,
        dto.uebersicht.primary_experience,
        len(dto.ausblicke),
        len(dto.grenzen),
        len(dto.nicht_empfohlen),
        len(dto.offene_fragen),
    )
    return dto


__all__ = [
    "Ausblick",
    "Beleg",
    "Grenze",
    "NichtEmpfohlen",
    "ResultDTO",
    "Uebersicht",
    "VERTRAG",
    "von_ergebnis",
]
