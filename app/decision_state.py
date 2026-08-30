"""Die Entscheidung eines Laufs an einer Stelle zusammenführen.

**Wozu.** Nach Aufruf 2 liegt alles fachlich Entschiedene vor — die
gewählten Familien, die Abdeckung je Signal, der Ausbaupfad, die
Nicht-Empfehlungen. Es liegt nur an fünf verschiedenen Stellen und in
einer Form, aus der eine Vorlage sich zusammenreimen müsste, was der
Einstieg ist und was das Zielbild.

Genau das darf keine Vorlage tun. Wer sich das zusammenreimt, trifft eine
fachliche Entscheidung — und zwei Vorlagen reimen es verschieden
zusammen. Web und PDF zeigten dann aus demselben Lauf verschiedene
Empfehlungen, ohne dass jemand etwas geändert hätte.

**Kein zusätzlicher Modellaufruf.** Hier wird nichts entschieden, nur
gelesen und geprüft. Was hier herauskommt, steht bereits in Aufruf 1 und
2; neu ist allein die Stelle, an der es zusammenkommt.
"""

from __future__ import annotations

import logging

from app.result_schema import (
    Coverage,
    DecisionState,
    Diagnose,
    Zielarchitektur,
)

logger = logging.getLogger(__name__)


def _familien_der_dispositionen(
    coverage: Coverage | None, *dispositionen: str
) -> list[str]:
    """Alle Familien, die unter einer dieser Entscheidungen stehen.

    Reihenfolge nach erstem Auftreten, damit derselbe Lauf zweimal
    dieselbe Liste ergibt.
    """

    gefunden: list[str] = []
    for eintrag in (coverage.items if coverage is not None else []):
        if eintrag.disposition not in dispositionen:
            continue
        for kennung in eintrag.family_refs:
            if kennung not in gefunden:
                gefunden.append(kennung)
    return gefunden


def _signale_der_disposition(coverage: Coverage | None, disposition: str) -> list[str]:
    """Die Signalkennungen, die diese eine Entscheidung bekommen haben."""

    return [
        eintrag.signal_id
        for eintrag in (coverage.items if coverage is not None else [])
        if eintrag.disposition == disposition
    ]


def _einstieg(gewaehlt: Zielarchitektur) -> list[str]:
    """Womit angefangen wird — in dieser Reihenfolge der Quellen.

    1. **Was der Planner ausdrücklich `start` genannt hat.** Das ist eine
       Entscheidung und schlägt jede Ableitung.
    2. **Die Familien der Module auf Stufe `jetzt`.** Der Planner hat den
       Einstieg dann nicht benannt, aber gebaut.
    3. **Das ganze Zielbild.** Ein Betrieb, dessen Lösung aus einer
       Familie besteht, fängt mit dieser einen an.

    Ohne die dritte Stufe stünde am Ende ein Zielbild ohne ersten Schritt,
    und der Vertrag würde es zurückweisen — an einer Stelle, an der nichts
    falsch ist ausser der Ableitung.
    """

    benannt = _familien_der_dispositionen(gewaehlt.coverage, "start")
    if benannt:
        return benannt
    gebaut: list[str] = []
    for modul in gewaehlt.module:
        if modul.stufe != "jetzt":
            continue
        for kennung in modul.solution_family_ids:
            if kennung not in gebaut:
                gebaut.append(kennung)
    if gebaut:
        return gebaut
    return list(gewaehlt.selected_solution_family_ids)


def _spaeter(gewaehlt: Zielarchitektur, zielbild: list[str]) -> list[str]:
    """Was bewusst später kommt — und nicht schon im Zielbild steht.

    Zwei Quellen: die Ausbaustufen und alles, was die Abdeckung `future`
    genannt hat. Beide meinen dasselbe, und der Planner benutzt mal die
    eine, mal die andere.

    Was bereits im Zielbild steht, fällt heraus. Eine Familie, die
    empfohlen **und** als Später geführt wird, ist kein Später — sie
    stünde auf der Karte zweimal, in zwei verschiedenen Zuständen.
    """

    spaeter: list[str] = []
    for stufe in gewaehlt.ausbaupfad:
        for kennung in stufe.solution_family_ids:
            if kennung not in spaeter and kennung not in zielbild:
                spaeter.append(kennung)
    for kennung in _familien_der_dispositionen(gewaehlt.coverage, "future"):
        if kennung not in spaeter and kennung not in zielbild:
            spaeter.append(kennung)
    return spaeter


def aus_lauf(diagnose: Diagnose, gewaehlt: Zielarchitektur) -> DecisionState:
    """Die Entscheidung dieses Laufs, geprüft und an einem Ort.

    Ohne Katalogtreffer bleibt fast alles leer — das ist ein gültiges
    Ergebnis und kein Sonderfall. Der Speicher und die Belege gehen
    trotzdem mit: Sie sagen, was verstanden wurde, auch wenn nichts
    empfohlen wird.
    """

    zielbild = list(gewaehlt.selected_solution_family_ids)
    zustand = DecisionState(
        evidence=list(diagnose.evidence_items),
        signals=list(diagnose.decision_signals),
        coverage=gewaehlt.coverage,
        why_not=list(gewaehlt.why_not),
        target_family_ids=zielbild,
        start_family_ids=_einstieg(gewaehlt) if zielbild else [],
        future_family_ids=_spaeter(gewaehlt, zielbild),
        open_signal_ids=_signale_der_disposition(gewaehlt.coverage, "open"),
    )
    logger.info(
        "decision_state.built zielbild=%s einstieg=%s spaeter=%s offen=%s "
        "why_not=%d signale=%d belege=%d",
        zustand.target_family_ids,
        zustand.start_family_ids,
        zustand.future_family_ids,
        zustand.open_signal_ids or "keine",
        len(zustand.why_not),
        len(zustand.signals),
        len(zustand.evidence),
    )
    return zustand
