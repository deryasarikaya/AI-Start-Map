"""Die AI Start Map: eine Landschaft, für jeden Betrieb dieselbe.

**Warum sie nicht erzeugt wird.**

Bis hierher entsteht jede Aussage der Auswertung aus der Erzählung. Genau
das war beim Ausblick das Problem: Ein Modell, das eine Zukunft erfinden
soll, bleibt auf der Schiene, über die es gerade geschrieben hat — auf
„ein gemeinsamer Fahrzeugstand" folgte „Statusfragen automatisch
beantworten". Dieselbe Sache, ein Merkmal weiter.

Die Karte dreht das um. Sie ist **fest** und zeigt das ganze Gelände eines
kleinen Betriebs. Erzeugt wird pro Kunde nur dreierlei: wo er heute steht,
wo wir anfangen würden, und was von dort aus erreichbar ist. Damit kann
die Vision nicht zu klein ausfallen, weil sie nicht erzeugt wird — und
nichts halluziniert werden, weil nichts geschrieben wird.

**Die Punkte sind der Katalog, nicht eine Erfindung daneben.** Jeder Punkt
ist eine freigegebene Lösungsfamilie. Name und Nutzensatz kommen aus
`kundennaher_name` und `was_danach_im_betrieb_anders_ist` — beide seit
Batch 10 vorhanden und bis jetzt nirgends benutzt.

**Die sechs Gebiete sind universell, die Punkte darin nicht.** Jeder
Betrieb hat Kunden, die kommen, Arbeit, die läuft, und etwas, das danach
passiert. Aber ein Fotograf allein hat kein Lager und keine Disposition.
Die Karte behält deshalb für alle dieselbe Form und dieselbe Grösse; was
darin steht, ist gefiltert.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app import solution_catalog

#: Die sechs Gebiete, in der Reihenfolge, in der ein Auftrag durch einen
#: Betrieb läuft — und im Kreis, weil der Kunde wiederkommt.
#:
#: Benannt aus **Betriebssicht**, nicht aus Systemsicht: „Wie Kunden Sie
#: erreichen" statt „Kundenkontakt". Wer das erste liest, denkt an seinen
#: Betrieb; wer das zweite liest, an Software.
GEBIETE: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "erreichen",
        "Wie Kunden Sie erreichen",
        ("SF-14", "SF-01", "SF-15", "SF-16"),
    ),
    (
        "auftrag",
        "Wie Anfragen zu Aufträgen werden",
        ("SF-07", "SF-06", "SF-18", "SF-22"),
    ),
    (
        "ueberblick",
        "Wie Ihr Team den Überblick behält",
        ("SF-02", "SF-12", "SF-20", "SF-21"),
    ),
    (
        "kundensicht",
        "Was Ihre Kunden selbst sehen können",
        ("SF-10", "SF-05", "SF-03", "SF-19"),
    ),
    (
        "danach",
        "Was nach dem Auftrag weiterläuft",
        ("SF-08", "SF-23", "SF-17", "SF-13"),
    ),
    (
        "wissen",
        "Was Ihr Betrieb über sich selbst weiß",
        ("SF-24", "SF-09", "SF-25", "SF-11", "SF-04"),
    ),
)

#: Die Mitte. Bewusst breiter benannt als „Kundenakte": Sie ist der Ort, an
#: dem alles zusammenläuft, und fast jede Familie im Katalog setzt sie
#: voraus. Die Karte behauptet das nicht — sie liest es ab.
MITTE = "Ihr gemeinsamer Arbeitsstand"


@dataclass(frozen=True)
class Punkt:
    """Eine Lösungsfamilie, so wie der Kunde sie auf der Karte sieht."""

    kennung: str
    name: str
    nutzen: str
    #: `start` — hier würden wir anfangen. `nah` — liegt in der Nähe.
    #: `still` — gibt es auch.
    zustand: str = "still"


@dataclass(frozen=True)
class Gebiet:
    """Eines der sechs Gebiete mit seinen Punkten."""

    kennung: str
    name: str
    punkte: list[Punkt] = field(default_factory=list)

    @property
    def hat_markierung(self) -> bool:
        return any(p.zustand != "still" for p in self.punkte)

    @property
    def stille(self) -> int:
        return sum(1 for p in self.punkte if p.zustand == "still")


def _kundennah(familie: solution_catalog.Familie) -> tuple[str, str]:
    """Name und Nutzensatz, wie der Katalog sie schon hergibt.

    Beide Felder stehen seit Batch 10 in jeder Familie und wurden bis jetzt
    nirgends gezeigt. Für die Karte ist damit nichts zu erfinden.
    """

    voll = familie.voller_datensatz
    name = familie.kundennaher_name or familie.name
    saetze = voll.get("was_danach_im_betrieb_anders_ist") or []
    nutzen = str(saetze[0]) if saetze else ""
    return name, nutzen


def landschaft(
    startpunkte: list[str] | None = None,
    nachbarn: list[str] | None = None,
) -> list[Gebiet]:
    """Die Karte mit markierten Punkten.

    `startpunkte` sind die Familien der empfohlenen Lösung, `nachbarn` die
    des Ausbaupfads. Alles andere bleibt still — sichtbar, lesbar, aber
    ruhig.

    Ohne Argumente kommt die leere Landschaft heraus. Das ist kein
    Sonderfall, sondern die Karte selbst: Sie steht auch ohne Auswertung.
    """

    beginnt = {k.strip().upper() for k in (startpunkte or [])}
    daneben = {k.strip().upper() for k in (nachbarn or [])} - beginnt
    katalog = solution_catalog.katalog()

    gebiete: list[Gebiet] = []
    for kennung, name, familien in GEBIETE:
        punkte: list[Punkt] = []
        for familienkennung in familien:
            familie = katalog.get(familienkennung)
            if familie is None:
                # Nicht freigegeben: Dann steht sie auch nicht auf der Karte.
                continue
            beschriftung, nutzen = _kundennah(familie)
            if familienkennung in beginnt:
                zustand = "start"
            elif familienkennung in daneben:
                zustand = "nah"
            else:
                zustand = "still"
            punkte.append(
                Punkt(familienkennung, beschriftung, nutzen, zustand)
            )
        gebiete.append(Gebiet(kennung, name, punkte))
    return gebiete
