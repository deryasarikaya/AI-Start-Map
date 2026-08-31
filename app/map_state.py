"""Die Karte als Daten: vier Zustände über einer festen Landschaft.

**Die Karte wird nicht erzeugt, sie wird markiert.** Das ist die alte
Entscheidung aus `app/karte.py` und sie gilt weiter: Die Landschaft liegt
fest, für jeden Betrieb dieselbe. Pro Kunde wird nur gesagt, wo er heute
steht, wo angefangen wird, was zum Zielbild gehört und was danach möglich
ist. Damit kann die Vision nicht zu klein ausfallen — sie wird nicht
geschrieben — und nichts halluziniert werden.

**Was hier neu ist gegenüber `karte.py`.** Dort ist ein Punkt eine
Lösungsfamilie. Fünfundzwanzig Punkte sind eine Fachlandkarte, keine
Kundenansicht: Telefon und Anfrageeingang liegen als zwei Punkte
nebeneinander, obwohl der Betrieb eine Sache sieht. Hier ist ein Punkt
ein **Bereich** — vierzehn statt fünfundzwanzig, in seiner Sprache.

Die Familien bleiben daran hängen, aber innen. Der Kunde sieht sie nie.

**Kein Modellaufruf, keine erzeugten Koordinaten.** Der Ort eines
Bereichs ist der Schwerpunkt seiner Familienpunkte auf der bestehenden
Karte. Zweimal dieselbe Entscheidung ergibt zweimal dieselbe Karte.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

from app import karte, operating_model
from app.operating_model import Bereich, Beziehung, OperatingCenter
from app.result_schema import DecisionState

logger = logging.getLogger(__name__)

#: Der Zustand eines Bereichs auf der Karte.
#:
#: `heute` heisst: Dafür hat der Betrieb schon etwas. `still` heisst: Es
#: gibt diesen Bereich, er ist für ihn gerade kein Thema. Die stillen
#: Bereiche bleiben sichtbar — eine Karte, die nur zeigt, was empfohlen
#: wird, ist keine Landschaft, sondern eine Angebotsliste.
Knotenzustand = Literal["start", "target", "future", "heute", "still"]

#: **Wie viele Bereiche der Einstieg zeigen darf.**
#:
#: Eine Präsentationsgrenze, keine fachliche: Wählt der Planner mehr, wird
#: die Auswahl dadurch nicht falsch — sie ist nur kein Einstieg mehr,
#: wenn drei Bereiche gleichzeitig aufleuchten. Was nicht mehr in den
#: Einstieg passt, bleibt im Zielbild und verschwindet nicht.
EINSTIEG_HOECHSTENS = 2

#: Wie viele Bereiche als Späteres gezeigt werden. **Nicht aufgefüllt**:
#: Sind es weniger, sind es weniger.
SPAETER_HOECHSTENS = 4


@dataclass(frozen=True)
class Knoten:
    """Ein Bereich des Betriebs auf der Karte."""

    schluessel: str
    name: str
    gebiet: str
    zustand: Knotenzustand
    x: int
    y: int
    #: Die Familien dahinter. **Intern** — sie tragen die Details im
    #: Seitenpanel und stehen nie als Kennung auf der Karte.
    familien: tuple[str, ...]


@dataclass(frozen=True)
class MapState:
    """Die Karte eines Laufs, fertig zum Zeichnen und ohne Layoutwissen."""

    #: Die sechs Gebiete, für jeden Betrieb dieselben.
    gebiete: tuple[karte.Zone, ...]
    #: Alle vierzehn Bereiche, jeder mit seinem Zustand.
    knoten: tuple[Knoten, ...]
    #: Bereichsschlüssel je Zustand — die Umschaltung der Seite.
    heute: tuple[str, ...]
    start: tuple[str, ...]
    target: tuple[str, ...]
    future: tuple[str, ...]
    mitte: OperatingCenter
    #: **Die Linien zwischen den Punkten.** Kuratiert und nur zwischen
    #: Bereichen, die für diesen Betrieb ein Thema sind. Keine Kante
    #: entsteht daraus, dass zwei Punkte im selben Ergebnis vorkommen.
    beziehungen: tuple[Beziehung, ...] = ()

    def knoten_von(self, schluessel: str) -> Knoten | None:
        """Ein Bereich über seinen Schlüssel."""

        return next((k for k in self.knoten if k.schluessel == schluessel), None)


def _ort(bereich: Bereich) -> tuple[int, int]:
    """Der Schwerpunkt der Familienpunkte dieses Bereichs.

    Die Koordinaten stehen in `karte.PLAETZE` und sind von Hand gesetzt,
    damit verwandte Familien beieinanderliegen. Der Mittelwert davon
    liegt deshalb dort, wo der Bereich hingehört — ohne dass eine zweite
    Koordinatentabelle gepflegt werden müsste, die mit der ersten
    auseinanderläuft.
    """

    punkte = [
        (x, y)
        for kennung in bereich.familien
        if (platz := karte.PLAETZE.get(kennung)) is not None
        for _, x, y in [platz]
    ]
    if not punkte:  # pragma: no cover - von pruefe_vollstaendigkeit verhindert
        return karte.MITTE_X, karte.MITTE_Y
    return (
        round(sum(x for x, _ in punkte) / len(punkte)),
        round(sum(y for _, y in punkte) / len(punkte)),
    )


def _bestandsbereiche(zustand: DecisionState) -> list[str]:
    """Wo der Betrieb heute schon etwas hat.

    Abgelesen, nicht geraten: Ein Signal der Art `existing_system` sagt,
    dass er ein System nennt; die Entscheidung dazu sagt, welchem Bereich
    es zugerechnet wurde. Ohne beides bleibt „heute" leer — und das ist
    besser, als aus einer beiläufigen Erwähnung eine Bestandsaufnahme zu
    machen.
    """

    bestand = {
        signal.id
        for signal in zustand.signals
        if signal.kind == "existing_system"
    }
    if not bestand or zustand.coverage is None:
        return []
    kennungen = [
        kennung
        for eintrag in zustand.coverage.items
        if eintrag.signal_id in bestand
        for kennung in eintrag.family_refs
    ]
    return [b.schluessel for b in operating_model.bereiche_fuer(kennungen)]


def aus_entscheidung(zustand: DecisionState) -> MapState:
    """Die Karte zu einer geprüften Entscheidung.

    Die Reihenfolge der Zuweisung ist die Rangfolge der Zustände: Was
    Einstieg ist, ist nicht mehr nur Zielbild; was Zielbild ist, ist kein
    Später. Ohne diese Ordnung läge derselbe Bereich in zwei Zuständen
    und die Karte zeigte ihn zweimal verschieden.
    """

    ziel = [b.schluessel for b in operating_model.bereiche_fuer(zustand.target_family_ids)]
    einstieg_alle = [
        b.schluessel for b in operating_model.bereiche_fuer(zustand.start_family_ids)
    ]
    einstieg = einstieg_alle[:EINSTIEG_HOECHSTENS]
    if len(einstieg_alle) > EINSTIEG_HOECHSTENS:
        # Kein fachlicher Eingriff: Der Rest bleibt Zielbild und ist
        # weiterhin sichtbar. Nur der hervorgehobene Einstieg wird
        # schmaler, damit er einer bleibt.
        logger.info(
            "map_state.start_trimmed von=%d auf=%d rest=%s",
            len(einstieg_alle),
            EINSTIEG_HOECHSTENS,
            einstieg_alle[EINSTIEG_HOECHSTENS:],
        )
    spaeter = [
        b.schluessel
        for b in operating_model.bereiche_fuer(zustand.future_family_ids)
        if b.schluessel not in ziel
    ][:SPAETER_HOECHSTENS]
    bestand = [
        schluessel
        for schluessel in _bestandsbereiche(zustand)
        if schluessel not in ziel and schluessel not in spaeter
    ]

    knoten: list[Knoten] = []
    for bereich in sorted(operating_model.BEREICHE, key=lambda b: b.reihenfolge):
        if bereich.schluessel in einstieg:
            art: Knotenzustand = "start"
        elif bereich.schluessel in ziel:
            art = "target"
        elif bereich.schluessel in spaeter:
            art = "future"
        elif bereich.schluessel in bestand:
            art = "heute"
        else:
            art = "still"
        x, y = _ort(bereich)
        knoten.append(
            Knoten(
                schluessel=bereich.schluessel,
                name=bereich.name,
                gebiet=bereich.gebiet,
                zustand=art,
                x=x,
                y=y,
                familien=tuple(
                    operating_model.familien_im_bereich(
                        bereich, zustand.target_family_ids + zustand.future_family_ids
                    )
                )
                or bereich.familien,
            )
        )

    karte_zustand = MapState(
        gebiete=karte.ZONEN,
        knoten=tuple(knoten),
        heute=tuple(bestand),
        start=tuple(einstieg),
        target=tuple(ziel),
        future=tuple(spaeter),
        mitte=operating_model.operating_center(zustand.target_family_ids),
        beziehungen=tuple(
            operating_model.beziehungen_zwischen(
                [k.schluessel for k in knoten if k.zustand != "still"]
            )
        ),
    )
    logger.info(
        "map_state.built heute=%s start=%s target=%s future=%s mitte=%s "
        "beziehungen=%d",
        karte_zustand.heute or "keine",
        karte_zustand.start,
        karte_zustand.target,
        karte_zustand.future or "keine",
        karte_zustand.mitte.art,
        len(karte_zustand.beziehungen),
    )
    return karte_zustand
