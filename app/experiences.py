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
from app.result_schema import DecisionState, View

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
    #: Die Stelle in der fachlichen Ordnung. **Nicht dekorativ:** Die
    #: Affinitäten eines Bereichs stehen in einer Reihenfolge, und die
    #: ist eine Aussage — beim Kundenzugang kommt der Sprachassistent vor
    #: dem Posteingang. Sortierte man stattdessen nach Typnamen, gewänne
    #: `ai_inbox` alphabetisch gegen `voice_assistant`, und ein
    #: Telefonbetrieb bekäme einen Posteingang als Hauptansicht.
    ordnung: int = 0


@dataclass(frozen=True)
class Experience:
    """Eine ausgewählte Ansicht mit ihrer Herkunft **und ihrem Inhalt**.

    **Warum der Inhalt hier hängt und nicht nur ein Verweis darauf.** Eine
    Auswahl, die nur sagt „nimm den Sprachassistenten", zwingt jede
    Darstellung, sich den passenden Eintrag aus der Ansichtsliste selbst
    herauszusuchen. Das ist eine Zuordnung, und zwei Darstellungen treffen
    sie verschieden — genau die Uneinigkeit, gegen die der ganze Vertrag
    gebaut ist. Also wird sie einmal getroffen, hier.

    `inhalt` ist leer, wenn der Aufruf für diesen Typ nichts Zulässiges
    geliefert hat. Dann steht der Rahmen ohne Inhalt. Das ist ehrlicher,
    als einen Inhalt zu erfinden — und die Darstellung sieht es an einem
    Feld statt an einer fehlenden Zeile.
    """

    typ: ExperienceType
    bereich: str
    familien: tuple[str, ...]
    #: Die geprüfte Ansicht aus Aufruf 3 — oder nichts.
    inhalt: View | None = None

    @property
    def hat_inhalt(self) -> bool:
        """Ob für diese Ansicht wirklich etwas zu zeigen ist."""

        return self.inhalt is not None

    @property
    def titel(self) -> str | None:
        """Die Überschrift der Ansicht, falls es eine gibt."""

        return None if self.inhalt is None else self.inhalt.titel


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
    ordnung = 0
    for rang, kennungen in enumerate(
        (zustand.start_family_ids, zustand.target_family_ids)
    ):
        # `bereiche_fuer` liefert bereits in der Reihenfolge des
        # Arbeitslaufs; innerhalb eines Bereichs gilt die Reihenfolge
        # seiner Affinitäten. Beides zusammen ist die fachliche Ordnung,
        # und genau die soll die Sortierung erhalten.
        for bereich in operating_model.bereiche_fuer(kennungen):
            familien = tuple(
                operating_model.familien_im_bereich(bereich, kennungen)
            )
            # **Die Familien entscheiden, nicht der Bereich.** Der
            # Kundenzugang trägt Telefon und Posteingang; nur wer die
            # Telefonfamilie gewählt hat, bekommt einen Sprachassistenten.
            for typ in operating_model.affinitaeten_von(familien):
                if typ in gefunden:
                    continue
                gefunden[typ] = Kandidat(
                    typ, bereich.schluessel, familien, rang, ordnung
                )
                ordnung += 1
    return sorted(gefunden.values(), key=lambda k: (k.rang, k.ordnung))


def erlaubte_ansichtstypen(zustand: DecisionState) -> list[str]:
    """Welche Ansichtstypen dieser Betrieb überhaupt bekommen kann.

    **Wozu.** Der Ansichtsaufruf wählte bisher frei aus allen neun Typen.
    Was nicht zum Einstieg gehört, verwirft die Auswahl danach ohnehin —
    aber erst nach bezahlter Arbeit, und die Seite steht dann ohne
    Vorschau da. Diese Liste geht deshalb **vorher** in den Aufruf.

    Die Reihenfolge ist die der Kandidaten: Was am nächsten am Einstieg
    liegt, steht vorn. Drei Zieltypen haben heute keine Ansicht
    (`guided_intake`, `knowledge_assistant`, `automation_flow`); für sie
    kann der Aufruf nichts liefern, und sie fallen hier still heraus.
    """

    rang = {k.typ: nummer for nummer, k in enumerate(kandidaten(zustand))}
    passende = [
        (rang[ziel], ansicht)
        for ansicht, ziel in ANSICHT_ZU_EXPERIENCE.items()
        if ziel in rang
    ]
    return [ansicht for _, ansicht in sorted(passende)]


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

    getroffen: list[tuple[Kandidat, View | None]] = []
    verworfen: list[str] = []
    for ansicht in ansichten or []:
        typ = _zieltyp(getattr(ansicht, "typ", None) or "")
        kandidat = nach_typ.get(typ) if typ is not None else None
        if kandidat is None:
            verworfen.append(
                f"{getattr(ansicht, 'typ', '?')}/{getattr(ansicht, 'titel', '')}"
            )
            continue
        if any(k.typ == kandidat.typ for k, _ in getroffen):
            continue
        # **Nur eine echte, geprüfte Ansicht wird zum Inhalt.** Die
        # Auswahl wird auch mit leichteren Vorrichtungen aufgerufen; was
        # kein `View` ist, trägt den Rahmen, aber keinen Inhalt.
        getroffen.append((kandidat, ansicht if isinstance(ansicht, View) else None))
    if verworfen:
        logger.info(
            "experiences.ungegroundet verworfen=%s moeglich=%s",
            verworfen,
            [k.typ for k in moegliche],
        )

    getroffen.sort(key=lambda paar: (paar[0].rang, paar[0].ordnung))
    if getroffen:
        kandidat, inhalt = getroffen[0]
        primary = Experience(kandidat.typ, kandidat.bereich, kandidat.familien, inhalt)
        begleitend = tuple(
            Experience(k.typ, k.bereich, k.familien, i)
            for k, i in getroffen[1 : 1 + BEGLEITEND_HOECHSTENS]
        )
    else:
        erster = moegliche[0]
        primary = Experience(erster.typ, erster.bereich, erster.familien, None)
        begleitend = ()

    gewaehlt = ExperienceAuswahl(primary=primary, supporting=begleitend)
    logger.info(
        "experiences.selected primary=%s bereich=%s inhalt=%s begleitend=%s "
        "aus_kandidaten=%d",
        primary.typ,
        primary.bereich,
        primary.hat_inhalt,
        [(e.typ, e.hat_inhalt) for e in begleitend] or "keine",
        len(moegliche),
    )
    return gewaehlt
