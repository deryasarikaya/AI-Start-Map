"""Was der Mensch am Ende vor sich sieht — und warum genau das.

**Das Problem, gegen das das gebaut ist.** Bisher wählte der
Ansichtsaufruf frei aus neun Ansichtstypen. Das Ergebnis: Fast jeder
Betrieb bekam dieselbe Übersicht mit denselben Zeilen, weil eine
Übersicht immer irgendwie passt. Ein Telefonbetrieb und ein
Ingenieurbüro sahen dasselbe Dashboard — und wer zwei Auswertungen
nebeneinander legt, merkt es sofort.

**Was sich ändert.** Die Zieltypen werden nicht mehr frei gewählt,
sondern aus dem *empfohlenen Einstieg* abgeleitet. Wer mit dem Telefon
anfängt, bekommt einen Sprachassistenten zu sehen; wer mit dem Wissen
anfängt, einen Auskunftsassistenten. Der Aufruf füllt danach nur noch
Inhalte.

**Genau eine Hauptansicht.** Drei gleichrangige Bilder nebeneinander
sind keine Empfehlung, sondern eine Auswahl — und der Betrieb soll
sehen, was zuerst entsteht. Bis zu zwei begleitende dürfen daneben
stehen, wenn sie etwas anderes zeigen.

Alles hier ist abgeleitet und geprüft, nichts erzeugt.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from app import operating_model
from app.operating_model import ANSICHT_ZU_EXPERIENCE, ExperienceType
from app.result_schema import DecisionState

logger = logging.getLogger(__name__)

#: Wie viele begleitende Ansichten höchstens danebenstehen. Zwei, und
#: keine davon darf dasselbe zeigen wie die Hauptansicht.
BEGLEITEND_HOECHSTENS = 2


@dataclass(frozen=True)
class Kandidat:
    """Ein Zieltyp, der zu diesem Betrieb passt — und woher er kommt.

    `rang` ist der Abstand zum Einstieg: 0 heisst, er gehört zu dem
    Bereich, mit dem angefangen wird. Daran entscheidet sich, was die
    Hauptansicht wird.
    """

    typ: ExperienceType
    bereich: str
    familien: tuple[str, ...]
    rang: int


@dataclass(frozen=True)
class Experience:
    """Eine ausgewählte Ansicht mit ihrer Herkunft.

    `inhalt_ref` zeigt auf die Ansicht aus dem Ergebnis, die sie füllt —
    oder ist leer, wenn der Aufruf für diesen Typ nichts geliefert hat.
    Dann steht der Rahmen ohne Inhalt, und das ist ehrlicher, als einen
    Inhalt zu erfinden.
    """

    typ: ExperienceType
    bereich: str
    familien: tuple[str, ...]
    inhalt_ref: str | None = None


@dataclass(frozen=True)
class ExperienceAuswahl:
    """Genau eine Hauptansicht, bis zu zwei begleitende."""

    primary: Experience | None
    supporting: tuple[Experience, ...] = ()

    @property
    def alle(self) -> tuple[Experience, ...]:
        return ((self.primary,) if self.primary else ()) + self.supporting


def kandidaten(zustand: DecisionState) -> list[Kandidat]:
    """Welche Zieltypen dieser Betrieb überhaupt bekommen kann.

    Zuerst die Typen der Bereiche, mit denen angefangen wird; danach die
    des übrigen Zielbilds. Ein Typ kommt nur einmal vor — und mit dem
    besten Rang, den er erreicht.

    **Nichts aus dem Späteren.** Eine Ansicht zeigt, was gebaut wird.
    Etwas zu zeigen, das bewusst später kommt, wäre ein Versprechen, das
    im selben Dokument zurückgenommen wird.
    """

    gefunden: dict[ExperienceType, Kandidat] = {}
    for rang, kennungen in enumerate(
        (zustand.start_family_ids, zustand.target_family_ids)
    ):
        for bereich in operating_model.bereiche_fuer(kennungen):
            familien = tuple(
                operating_model.familien_im_bereich(bereich, kennungen)
            )
            for typ in bereich.experience_affinitaeten:
                if typ in gefunden:
                    continue
                gefunden[typ] = Kandidat(typ, bereich.schluessel, familien, rang)
    return sorted(gefunden.values(), key=lambda k: (k.rang, k.bereich, k.typ))


def _zieltyp(ansichtstyp: str) -> ExperienceType | None:
    """Der Zieltyp zu einem heutigen Ansichtstyp."""

    return ANSICHT_ZU_EXPERIENCE.get(str(ansichtstyp))


def auswahl(
    zustand: DecisionState, ansichten: list[object] | None = None
) -> ExperienceAuswahl:
    """Die Ansichten dieses Laufs — abgeleitet, geprüft, höchstens drei.

    **Die Reihenfolge der Quellen.** Was der Ansichtsaufruf geliefert
    hat, wird bevorzugt: Dort steckt der Inhalt. Es zählt aber nur, wenn
    es sich auf einen Bereich zurückführen lässt, der zu diesem Betrieb
    gehört — eine Ansicht ohne Bezug ist eine Erfindung, und dieselbe
    Regel gilt für sie wie für ein Modul ohne Familie.

    Bleibt danach nichts übrig, steht der erste Kandidat ohne Inhalt da.
    Das ist ehrlicher, als eine unpassende Ansicht zur Hauptansicht zu
    erklären, nur damit die Seite voll wird.
    """

    moegliche = kandidaten(zustand)
    if not moegliche:
        return ExperienceAuswahl(primary=None)
    nach_typ = {k.typ: k for k in moegliche}

    getroffen: list[tuple[Kandidat, str]] = []
    verworfen: list[str] = []
    for ansicht in ansichten or []:
        typ = _zieltyp(getattr(ansicht, "typ", None) or "")
        titel = str(getattr(ansicht, "titel", "") or "")
        kandidat = nach_typ.get(typ) if typ is not None else None
        if kandidat is None:
            verworfen.append(f"{getattr(ansicht, 'typ', '?')}/{titel}")
            continue
        if any(k.typ == kandidat.typ for k, _ in getroffen):
            continue
        getroffen.append((kandidat, titel))
    if verworfen:
        logger.info(
            "experiences.ungegroundet verworfen=%s moeglich=%s",
            verworfen,
            [k.typ for k in moegliche],
        )

    getroffen.sort(key=lambda paar: (paar[0].rang, paar[0].bereich, paar[0].typ))
    if getroffen:
        kandidat, titel = getroffen[0]
        primary = Experience(kandidat.typ, kandidat.bereich, kandidat.familien, titel)
        begleitend = tuple(
            Experience(k.typ, k.bereich, k.familien, t)
            for k, t in getroffen[1 : 1 + BEGLEITEND_HOECHSTENS]
        )
    else:
        erster = moegliche[0]
        primary = Experience(erster.typ, erster.bereich, erster.familien, None)
        begleitend = ()

    gewaehlt = ExperienceAuswahl(primary=primary, supporting=begleitend)
    logger.info(
        "experiences.selected primary=%s bereich=%s begleitend=%s aus_kandidaten=%d",
        primary.typ,
        primary.bereich,
        [e.typ for e in begleitend] or "keine",
        len(moegliche),
    )
    return gewaehlt
