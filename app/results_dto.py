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
class Faehigkeit:
    """Was die Lösung an dieser Stelle können muss.

    `ref` ist die Katalogkennung und bleibt innen; `label` ist der Satz,
    den der Katalog bereits kundenverständlich führt („Eingänge nach
    Anliegen einordnen"). Die Darstellung zeigt `label` und nie `ref`.
    """

    ref: str
    label: str


@dataclass(frozen=True)
class OperatingModul:
    """Ein Bereich des Betriebs, fertig zum Anzeigen.

    **Warum das im Vertrag steht und nicht in der Darstellung entsteht.**
    Ohne dieses Feld müsste jede Darstellung selbst nachschlagen, welche
    Familien zu einem Bereich gehören, welche Fähigkeiten die brauchen,
    welche Belege dahinterstehen und welche Grenze dazu gehört. Das sind
    vier Nachschläge in drei Quellen — und zwei Darstellungen machen sie
    verschieden.

    Alles hier ist aus bereits geprüften Daten abgeleitet. Es entsteht
    keine neue Empfehlung: `state` kommt aus der Karte, `family_refs` aus
    der Entscheidung, die Fähigkeiten aus dem Katalog.
    """

    module_key: str
    customer_label: str
    #: Gebietskennung aus `karte.ZONEN` und ihr Name.
    business_area: str
    business_area_label: str
    #: Derselbe Zustand, den auch die Karte zeigt.
    state: str
    #: Die Familien dieses Bereichs, die zu diesem Betrieb gehören —
    #: Zielbild **und** Späteres, genau wie der Knoten auf der Karte.
    #: Ein Bereich kann deshalb `start` sein und eine Familie führen, die
    #: erst später kommt; `capability_refs` bleibt davon unberührt und
    #: nennt nur, was wirklich empfohlen ist.
    #: **Intern** — der Kunde sieht `customer_label`.
    family_refs: tuple[str, ...]
    #: Nur bei Bereichen, die zum Zielbild gehören: Was die Lösung hier
    #: können muss. Für einen stillen Bereich steht hier nichts — sonst
    #: behauptete der Vertrag Fähigkeiten für etwas, das nicht empfohlen
    #: wurde.
    capability_refs: tuple[Faehigkeit, ...] = field(default_factory=tuple)
    #: Die Belege, die diesen Bereich tragen.
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    #: Stellen in `ResultDTO.grenzen`, die zu diesem Bereich gehören.
    #: Als Index, damit dieselbe Grenze nicht zweimal im Vertrag steht.
    boundary_refs: tuple[int, ...] = field(default_factory=tuple)
    #: Reihenfolge im Arbeitslauf.
    map_order: int = 0

    @property
    def ist_sichtbar(self) -> bool:
        """Ob dieser Bereich für diesen Betrieb überhaupt ein Thema ist."""

        return self.state != "still"


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
    #: **Alle vierzehn Bereiche, jeder mit seinem Zustand.** Die stillen
    #: gehen mit: Die Karte zeigt die ganze Landschaft, und wer nur das
    #: Empfohlene ausliefert, kann sie nicht zeichnen.
    module: tuple[OperatingModul, ...]
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

    @property
    def sichtbare_module(self) -> tuple[OperatingModul, ...]:
        """Die Bereiche, die für diesen Betrieb ein Thema sind."""

        return tuple(m for m in self.module if m.ist_sichtbar)

    def modul(self, schluessel: str) -> OperatingModul | None:
        """Ein Bereich über seinen Schlüssel."""

        return next((m for m in self.module if m.module_key == schluessel), None)


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


def _belege_je_familie(zustand: DecisionState) -> dict[str, list[str]]:
    """Welche Belegkennungen hinter welcher Familie stehen.

    Der Weg ist zweistufig und beide Stufen sind bereits geprüft: Die
    Abdeckung sagt, welches Signal zu welcher Familie führte; das Signal
    sagt, auf welchen Zitaten es steht. Hier wird nichts zugeordnet, was
    nicht schon zugeordnet war — nur nachgeschlagen.
    """

    nach_signal = {s.id: s.evidence_refs for s in zustand.signals}
    gefunden: dict[str, list[str]] = {}
    for eintrag in zustand.coverage.items if zustand.coverage is not None else []:
        for kennung in eintrag.family_refs:
            fuer_familie = gefunden.setdefault(kennung, [])
            for bezug in nach_signal.get(eintrag.signal_id, []):
                if bezug not in fuer_familie:
                    fuer_familie.append(bezug)
    return gefunden


def _module(
    zustand: DecisionState, karte: MapState, grenzen: list[Grenze]
) -> list[OperatingModul]:
    """Die vierzehn Bereiche, fertig zum Anzeigen.

    **Alle vierzehn, nicht nur die empfohlenen.** Die Karte zeigt die
    ganze Landschaft; wer nur das Empfohlene ausliefert, kann sie nicht
    zeichnen. Was für diesen Betrieb kein Thema ist, trägt `still` und
    bekommt weder Fähigkeiten noch Belege — ein stiller Bereich soll
    nichts behaupten.

    Der Zustand wird **von der Karte übernommen**, nicht neu gerechnet.
    Zwei Rechenwege für dieselbe Frage sind zwei Gelegenheiten, sich zu
    widersprechen.
    """

    belege = _belege_je_familie(zustand)
    im_zielbild = set(zustand.target_family_ids)
    gefunden: list[OperatingModul] = []
    for bereich in sorted(operating_model.BEREICHE, key=lambda b: b.reihenfolge):
        knoten = karte.knoten_von(bereich.schluessel)
        zustand_des_bereichs = knoten.zustand if knoten is not None else "still"
        eigene = list(knoten.familien) if knoten is not None else []
        # Fähigkeiten und Belege nur für das, was wirklich empfohlen ist.
        empfohlen = [k for k in eigene if k in im_zielbild]
        faehigkeiten = (
            tuple(
                Faehigkeit(
                    str(datensatz.get("chunk_id") or ""),
                    str(datensatz.get("title") or datensatz.get("faehigkeit_name") or ""),
                )
                for datensatz in solution_catalog.faehigkeiten_zu(empfohlen)
                if datensatz.get("chunk_id")
            )
            if empfohlen
            else ()
        )
        gesehen: list[str] = []
        for kennung in empfohlen:
            for bezug in belege.get(kennung, []):
                if bezug not in gesehen:
                    gesehen.append(bezug)
        gefunden.append(
            OperatingModul(
                module_key=bereich.schluessel,
                customer_label=bereich.name,
                business_area=bereich.gebiet,
                business_area_label=next(
                    (z.name for z in karte.gebiete if z.kennung == bereich.gebiet),
                    bereich.gebiet,
                ),
                state=zustand_des_bereichs,
                family_refs=tuple(eigene),
                capability_refs=faehigkeiten,
                evidence_refs=tuple(gesehen),
                boundary_refs=tuple(
                    stelle
                    for stelle, grenze in enumerate(grenzen)
                    if grenze.familie is not None and grenze.familie in eigene
                ),
                map_order=bereich.reihenfolge,
            )
        )
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
    grenzen = _grenzen(ergebnis, zustand.target_family_ids)
    dto = ResultDTO(
        contract_version=VERTRAG,
        herkunft="ergebnis-v6-adaptiert" if angepasst else VERTRAG,
        uebersicht=_uebersicht(ergebnis, zustand, karte, ansichten),
        belege=tuple(
            Beleg(b.id, b.zitat, b.bedeutung) for b in zustand.evidence
        ),
        entscheidung=zustand,
        karte=karte,
        module=tuple(_module(zustand, karte, grenzen)),
        ansichten=ansichten,
        grenzen=tuple(grenzen),
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
        "results_dto.built herkunft=%s einstieg=%s primary=%s inhalt=%s "
        "module_sichtbar=%d ausblicke=%d grenzen=%d nicht_empfohlen=%d offen=%d",
        dto.herkunft,
        dto.uebersicht.einstieg_refs,
        dto.uebersicht.primary_experience,
        dto.ansichten.primary.hat_inhalt if dto.ansichten.primary else False,
        len(dto.sichtbare_module),
        len(dto.ausblicke),
        len(dto.grenzen),
        len(dto.nicht_empfohlen),
        len(dto.offene_fragen),
    )
    return dto


__all__ = [
    "Ausblick",
    "Beleg",
    "Faehigkeit",
    "Grenze",
    "OperatingModul",
    "NichtEmpfohlen",
    "ResultDTO",
    "Uebersicht",
    "VERTRAG",
    "von_ergebnis",
]
