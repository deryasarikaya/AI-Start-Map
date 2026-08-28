"""Die AI Start Map: eine Landkarte, für jeden Betrieb dieselbe.

**Warum sie nicht erzeugt wird.**

Alles andere in der Auswertung entsteht aus der Erzählung. Genau das war
beim Ausblick das Problem: Ein Modell, das eine Zukunft erfinden soll,
bleibt auf der Schiene, über die es gerade geschrieben hat — auf „ein
gemeinsamer Fahrzeugstand" folgte „Statusfragen automatisch beantworten".
Dieselbe Sache, ein Merkmal weiter.

Die Karte dreht es um. Sie liegt **fest**: sechs Gebiete um einen
gemeinsamen Kern, und jede der freigegebenen Lösungsfamilien hat darauf
einen festen Platz. Pro Kunde wird nur markiert — wo er heute steht, wo
wir anfangen würden, was von dort erreichbar ist.

Damit kann die Vision nicht zu klein ausfallen, weil sie nicht erzeugt
wird. Und nichts halluziniert werden, weil nichts geschrieben wird.

**Das Modell liefert nur Kennungen.** Keine Koordinaten, keine Zonen,
keine Beschriftungen. Die Geometrie steht hier, die Namen stehen im
Katalog (`kundennaher_name`, `was_danach_im_betrieb_anders_ist` — beide
seit Batch 10 vorhanden und bis vor Kurzem nirgends benutzt).

**Die sechs Gebiete sind universell, die Punkte darin nicht.** Jeder
Betrieb hat Kunden, die kommen, Arbeit, die läuft, und etwas, das danach
passiert. Aber ein Fotograf allein hat kein Lager. Die Karte behält
deshalb für alle dieselbe Form und dieselbe Grösse; was darin steht, ist
gefiltert.
"""

from __future__ import annotations

from dataclasses import dataclass

from app import solution_catalog

#: Die Zeichenfläche. Alle Koordinaten unten beziehen sich darauf.
BREITE, HOEHE = 1200, 780

#: Die Mitte. Bewusst breiter benannt als „Kundenakte": Sie ist der Ort, an
#: dem alles zusammenläuft, und fast jede Familie im Katalog setzt sie
#: voraus. Die Karte behauptet das nicht — sie liest es ab.
MITTE = "Ihr gemeinsamer Arbeitsstand"
MITTE_X, MITTE_Y, MITTE_R = 600, 392, 96


@dataclass(frozen=True)
class Zone:
    """Ein Gebiet der Karte — eine weiche Fläche, kein Kasten.

    `pfad` ist eine SVG-Kurve. Von Hand gesetzt und nicht berechnet: Sechs
    gleichmässige Kreissegmente sähen aus wie ein Tortendiagramm, und
    genau das soll es nicht sein. Eine Landschaft hat ungleiche Felder.
    """

    kennung: str
    name: str
    pfad: str
    #: Wo die Gebietsbeschriftung sitzt.
    text_x: int
    text_y: int
    #: Für die Handy-Fassung: Reihenfolge im Auftragslauf.
    reihenfolge: int


ZONEN: tuple[Zone, ...] = (
    Zone(
        "erreichen",
        "Wie Kunden Sie erreichen",
        "M70 205 Q225 92 400 175 L372 372 Q210 402 78 322 Z",
        96, 168, 1,
    ),
    Zone(
        "auftrag",
        "Wie Anfragen zu Aufträgen werden",
        "M92 430 Q240 372 386 428 L410 648 Q232 722 86 612 Z",
        112, 418, 2,
    ),
    Zone(
        "ueberblick",
        "Wie Ihr Team den Überblick behält",
        "M452 566 Q612 512 782 578 L738 742 Q568 782 428 706 Z",
        468, 606, 3,
    ),
    Zone(
        "kundensicht",
        "Was Ihre Kunden selbst sehen können",
        "M812 176 Q1030 128 1132 254 L1098 428 Q938 388 796 344 Z",
        836, 166, 4,
    ),
    Zone(
        "danach",
        "Was nach dem Auftrag weiterläuft",
        "M818 462 Q972 418 1126 508 L1090 690 Q930 748 790 638 Z",
        838, 476, 5,
    ),
    Zone(
        "wissen",
        "Was Ihr Betrieb über sich selbst weiß",
        "M436 66 Q616 18 790 88 L744 258 Q604 232 462 272 Z",
        498, 74, 6,
    ),
)

#: Wo jede Lösungsfamilie auf der Karte liegt. **Fest.** Nicht das Modell
#: entscheidet die Koordinaten, sondern diese Tabelle — sonst springt die
#: Karte bei jedem Lauf, und dieselbe Familie läge zweimal woanders.
#:
#: Die Zahlen sind so gesetzt, dass verwandte Familien beieinander liegen
#: und der Kern in der Mitte frei bleibt.
PLAETZE: dict[str, tuple[str, int, int]] = {
    # Wie Kunden Sie erreichen
    "SF-15": ("erreichen", 178, 232),   # Telefon- und Sprachworkflow
    "SF-01": ("erreichen", 296, 196),   # Nachrichten- und Anfrageeingang
    "SF-14": ("erreichen", 148, 316),   # Website und digitaler Zugang
    "SF-16": ("erreichen", 312, 320),   # Vorqualifizierung
    # Wie Anfragen zu Aufträgen werden
    "SF-07": ("auftrag", 176, 476),     # Angebot, Auftrag, Freigabe
    "SF-06": ("auftrag", 300, 466),     # Termin- und Buchungssteuerung
    "SF-18": ("auftrag", 162, 570),     # Disposition und Kapazität
    "SF-22": ("auftrag", 300, 588),     # Auswahl, Freigabe, Übergabe
    # Wie Ihr Team den Überblick behält
    "SF-02": ("ueberblick", 520, 626),  # Vorgangs- und Fallmanagement
    "SF-12": ("ueberblick", 646, 640),  # Aufgaben, Fristen, Eskalation
    "SF-20": ("ueberblick", 500, 700),  # Material und Beschaffung
    "SF-21": ("ueberblick", 660, 712),  # Personal und Onboarding
    # Was Ihre Kunden selbst sehen können
    "SF-10": ("kundensicht", 906, 232), # Kunden- und Mandantenportal
    "SF-05": ("kundensicht", 1024, 268),# Kundenservice- und Auskunftsassistent
    "SF-03": ("kundensicht", 880, 322), # Dokumenten- und Nachweisverarbeitung
    "SF-19": ("kundensicht", 1016, 348),# Compliance und Prüfpfad
    # Was nach dem Auftrag weiterläuft
    "SF-08": ("danach", 884, 528),      # Rechnungs- und Finanzvorbereitung
    "SF-23": ("danach", 1010, 544),     # Zahlung, Abo, Zusatzverkauf
    "SF-17": ("danach", 872, 620),      # Kundenbindung und Nachfassen
    "SF-13": ("danach", 1004, 636),     # Marketing und Bewertungen
    # Was Ihr Betrieb über sich selbst weiß
    "SF-24": ("wissen", 512, 138),      # Kunden-, Objekt- und Historienakte
    "SF-09": ("wissen", 640, 118),      # Management-Übersicht
    "SF-11": ("wissen", 706, 190),      # Wissens- und Rechercheassistent
    "SF-25": ("wissen", 580, 216),      # Wirtschaftlichkeitsvorschau
    "SF-04": ("wissen", 486, 180),      # Daten- und Systemabgleich
}

#: **Wie ein Punkt auf der Karte heisst.**
#:
#: Der Katalog hat zwei Namen, und keiner passt auf eine Landkarte.
#: `familie_name` ist Fachsprache und bis zu siebenundfuenfzig Zeichen lang
#: („Personalgewinnung, Onboarding und Qualifikationssteuerung“).
#: `kundennaher_name` ist ein ganzer Satz — nachgemessen bis 497 Pixel
#: breit. Beides nebeneinander ergab auf der Karte 23 sich ueberlappende
#: Beschriftungen: unlesbar.
#:
#: Deshalb hier ein dritter, kurzer Name — zwei bis drei Woerter, wie eine
#: Ortsangabe. Er steht **fest im Code**, genau wie die Koordinaten: Er
#: wird nicht erzeugt, nicht pro Kunde gewaehlt und behauptet nichts ueber
#: einen Betrieb. Er benennt nur die Familie kuerzer.
#:
#: Der volle Satz aus dem Katalog geht nicht verloren — er steht in der
#: Legende unter der Karte und in der Liste.
MARKEN: dict[str, str] = {
    "SF-15": "Telefon & Sprache",
    "SF-01": "Anfrage-Eingang",
    "SF-14": "Website & Zugang",
    "SF-16": "Vorqualifizierung",
    "SF-07": "Angebot & Auftrag",
    "SF-06": "Termine & Buchung",
    "SF-18": "Disposition & Kapazität",
    "SF-22": "Freigabe & Übergabe",
    "SF-02": "Vorgänge & Fälle",
    "SF-12": "Aufgaben & Fristen",
    "SF-20": "Material & Lager",
    "SF-21": "Personal & Einarbeitung",
    "SF-10": "Kundenportal",
    "SF-05": "Auskunft & Service",
    "SF-03": "Dokumente & Nachweise",
    "SF-19": "Signatur & Prüfpfad",
    "SF-08": "Rechnung & Finanzen",
    "SF-23": "Zahlung & Abo",
    "SF-17": "Nachfassen & Bindung",
    "SF-13": "Marketing & Bewertungen",
    "SF-24": "Kundenakte & Historie",
    "SF-09": "Auswertung & Übersicht",
    "SF-11": "Wissen & Recherche",
    "SF-25": "Zahlen-Vorschau",
    "SF-04": "Datenabgleich",
}


def _umbrechen(text: str, breite: int = 13) -> tuple[str, ...]:
    """Der Name als Zeilen. SVG bricht Text nicht selbst um.

    Hoechstens zwei Zeilen: Was darunter nicht passt, gehoert nicht auf
    eine Landkarte.
    """

    worte, zeilen, laufend = text.split(), [], ""
    for wort in worte:
        versuch = f"{laufend} {wort}".strip()
        if len(versuch) <= breite or not laufend:
            laufend = versuch
        else:
            zeilen.append(laufend)
            laufend = wort
    if laufend:
        zeilen.append(laufend)
    if len(zeilen) > 2:
        zeilen = [zeilen[0], " ".join(zeilen[1:])]
    return tuple(zeilen)


@dataclass(frozen=True)
class Punkt:
    """Eine Lösungsfamilie, so wie der Kunde sie auf der Karte sieht."""

    kennung: str
    #: Der kurze Kartenname — zwei bis drei Woerter.
    name: str
    #: Der volle Satz aus dem Katalog. Auf der Karte steht er nicht; er
    #: traegt die Legende darunter und die Liste.
    nutzen: str
    x: int
    y: int
    zone: str
    #: `start` — hier würden wir anfangen. `nah` — liegt in der Nähe.
    #: `still` — gibt es auch.
    zustand: str = "still"

    @property
    def zeilen(self) -> tuple[str, ...]:
        """Der Name, umgebrochen — SVG kann das nicht selbst."""

        return _umbrechen(self.name)

    @property
    def hoch(self) -> int:
        """Wie weit der Text ueber dem Punkt beginnt.

        **Unter dem Punkt, mittig — nicht seitlich.** Seitliche Texte
        liefen bei fuenfundzwanzig Punkten ineinander, weil ihre Breite
        vom Wort abhaengt. Mittig unter dem Punkt ist die Breite
        symmetrisch, und der Abstand zum Nachbarn bleibt der, den die
        Koordinaten vorgeben.
        """

        return {"start": 30, "nah": 25}.get(self.zustand, 20)


@dataclass(frozen=True)
class Weg:
    """Eine Verbindung von der Mitte zu einem markierten Punkt.

    Eine geschwungene Linie, keine gerade: Gerade Linien mit Pfeilspitzen
    lesen sich als Organigramm, und genau das soll die Karte nicht sein.
    """

    pfad: str
    art: str


def _kundennah(kennung: str, familie: solution_catalog.Familie) -> tuple[str, str]:
    """Kartenname und der volle Satz des Katalogs.

    Auf der Karte steht der kurze Name aus `MARKEN`. Der Satz aus
    `kundennaher_name` bleibt daneben erhalten — fuer die Liste und die
    Legende.
    """

    kurz = MARKEN.get(kennung) or familie.kundennaher_name or familie.name
    return kurz, familie.kundennaher_name or familie.name


def _bogen(x: int, y: int) -> str:
    """Eine weiche Kurve vom Kern zu einem Punkt."""

    # Der Kontrollpunkt liegt auf halber Strecke, seitlich versetzt —
    # daher die Wölbung. Ohne sie wären es Speichen eines Rades.
    mx, my = (MITTE_X + x) / 2, (MITTE_Y + y) / 2
    versatz = (y - MITTE_Y) * 0.18
    return f"M{MITTE_X} {MITTE_Y} Q{mx + versatz:.0f} {my - versatz:.0f} {x} {y}"


def landschaft(
    startpunkte: list[str] | None = None,
    nachbarn: list[str] | None = None,
) -> dict[str, object]:
    """Die Karte mit den Markierungen dieses Betriebs.

    `startpunkte` sind die Familien der empfohlenen Lösung, `nachbarn` die
    des Ausbaupfads. Alles andere bleibt still — sichtbar, lesbar, ruhig.

    Ohne Argumente kommt die leere Landschaft heraus. Das ist kein
    Sonderfall, sondern die Karte selbst: Sie steht auch ohne Auswertung.
    """

    beginnt = {k.strip().upper() for k in (startpunkte or [])}
    daneben = {k.strip().upper() for k in (nachbarn or [])} - beginnt
    katalog = solution_catalog.katalog()

    punkte: list[Punkt] = []
    wege: list[Weg] = []
    for kennung, (zone, x, y) in PLAETZE.items():
        familie = katalog.get(kennung)
        if familie is None:
            # Nicht freigegeben: Dann steht sie auch nicht auf der Karte.
            continue
        name, nutzen = _kundennah(kennung, familie)
        if kennung in beginnt:
            zustand = "start"
        elif kennung in daneben:
            zustand = "nah"
        else:
            zustand = "still"
        punkte.append(Punkt(kennung, name, nutzen, x, y, zone, zustand))
        if zustand != "still":
            wege.append(Weg(_bogen(x, y), zustand))

    return {
        "breite": BREITE,
        "hoehe": HOEHE,
        "mitte": MITTE,
        "mitte_x": MITTE_X,
        "mitte_y": MITTE_Y,
        "mitte_r": MITTE_R,
        "zonen": ZONEN,
        "punkte": punkte,
        "wege": wege,
        #: Für die Handy-Fassung: dieselben Punkte, nach Gebiet gruppiert.
        "gebiete": [
            (zone, [p for p in punkte if p.zone == zone.kennung])
            for zone in sorted(ZONEN, key=lambda z: z.reihenfolge)
        ],
    }
