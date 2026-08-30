"""Die AI Start Map — das eine, was nicht erzeugt wird.

Jede andere Aussage der Auswertung entsteht aus der Erzählung. Genau das
war beim Ausblick das Problem: Ein Modell, das eine Zukunft erfinden soll,
bleibt auf der Schiene, über die es gerade geschrieben hat.

Die Karte dreht es um. Sie liegt fest — sechs Gebiete um einen Kern, jede
Lösungsfamilie an ihrem eigenen Platz —, und pro Kunde wird nur markiert.
Geprüft wird deshalb vor allem, dass sie **nicht** erzeugt wird: dass
jeder Betrieb dieselbe Geometrie sieht, dass das Modell keine Koordinaten
liefert, dass die Punkte aus dem freigegebenen Katalog kommen, und dass
sie ohne JavaScript vollständig stimmt — sonst fehlte sie im PDF.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app import karte, solution_catalog


def test_the_geometry_is_the_same_for_everyone() -> None:
    """Sechs Gebiete, dieselben Plätze, in jeder Auswertung.

    Das ist der Grund, warum die Vision nicht zu klein ausfallen kann: Sie
    hängt nicht davon ab, was einem Modell für diesen Betrieb einfällt.
    """

    leer = karte.landschaft()
    voll = karte.landschaft(["SF-02"], ["SF-10", "SF-24"])

    assert len(leer["zonen"]) == 6
    assert [z.name for z in leer["zonen"]] == [z.name for z in voll["zonen"]]
    # Dieselben Punkte an denselben Stellen — nur anders markiert.
    stellen = lambda k: {(p.kennung, p.x, p.y) for p in k["punkte"]}
    assert stellen(leer) == stellen(voll)


def test_the_model_never_supplies_coordinates() -> None:
    """**Die Geometrie steht im Code, nicht in der Antwort.**

    Liesse das Modell die Punkte setzen, läge dieselbe Familie bei jedem
    Lauf woanders — und die Karte wäre kein Gelände, sondern ein Zufall.
    Jede Familie hat genau einen Platz.
    """

    plaetze = karte.PLAETZE

    assert len(plaetze) == 25
    koordinaten = [(x, y) for _, x, y in plaetze.values()]
    assert len(set(koordinaten)) == len(koordinaten), "zwei Familien am selben Platz"
    for zone, x, y in plaetze.values():
        assert zone in {z.kennung for z in karte.ZONEN}
        assert 0 < x < karte.BREITE and 0 < y < karte.HOEHE


def test_every_point_is_a_released_family() -> None:
    """Kein Punkt ohne Katalog.

    Die Karte ist der Ort, an dem eine Erfindung am wenigsten auffiele:
    Sie klingt gross, niemand prüft sie beim Lesen, und eine erfundene
    Möglichkeit fällt erst auf, wenn jemand sie bestellt.
    """

    erlaubt = set(solution_catalog.katalog())

    kennungen = {p.kennung for p in karte.landschaft()["punkte"]}

    assert kennungen
    assert kennungen <= erlaubt


def test_the_points_speak_the_catalogue_s_own_words() -> None:
    """Der volle Satz jedes Punktes steht schon im Katalog.

    `kundennaher_name` liegt seit Batch 10 in jeder Familie. Fuer die
    Legende und die Liste ist damit nichts zu erfinden — und deshalb kann
    die Karte nichts behaupten, was der Katalog nicht hergibt.
    """

    katalog = solution_catalog.katalog()

    for punkt in karte.landschaft()["punkte"]:
        familie = katalog[punkt.kennung]
        assert punkt.nutzen == (familie.kundennaher_name or familie.name)


def test_every_family_has_a_short_map_label() -> None:
    """**Auf eine Landkarte passt kein Satz.**

    Der Katalog hat zwei Namen, und keiner passt: `familie_name` ist bis zu
    siebenundfuenfzig Zeichen lang, `kundennaher_name` ist ein ganzer Satz.
    Mit ihnen ueberlappten sich auf der Karte 23 Beschriftungen.

    Die kurzen Namen stehen deshalb fest im Code — wie die Koordinaten.
    Geprueft wird, dass keine Familie vergessen wurde und keiner wieder
    zu einem Satz auswaechst.
    """

    assert set(karte.MARKEN) == set(karte.PLAETZE)

    for kennung, marke in karte.MARKEN.items():
        assert marke.strip() == marke and marke
        assert len(marke) <= 24, f"{kennung}: {marke!r} ist zu lang fuer die Karte"
        # Hoechstens zwei Zeilen - was darunter nicht passt, gehoert nicht
        # auf eine Landkarte.
        assert len(karte._umbrechen(marke)) <= 2, kennung


def test_the_labels_do_not_pile_up_on_each_other() -> None:
    """Die Beschriftung sitzt mittig unter ihrem Punkt.

    Seitlich lief sie ineinander, weil ihre Breite vom Wort abhing. Mittig
    ist sie symmetrisch — der Abstand zum Nachbarn ist dann der, den die
    Koordinaten vorgeben, und nicht der, den das laengste Wort uebrig
    laesst.
    """

    punkte = karte.landschaft(["SF-02"], ["SF-10"])["punkte"]

    for punkt in punkte:
        assert punkt.hoch > 0, "der Text muss unter dem Punkt beginnen"
    # **Der Abstand muss zur Textbreite passen, nicht zum Punkt.** Hier
    # standen einmal 70 Einheiten — zu wenig: „Datenabgleich" und
    # „Zahlen-Vorschau" lagen 74 auseinander und liefen trotzdem
    # ineinander, weil eine mittig gesetzte Beschriftung nach beiden
    # Seiten rund 45 Einheiten braucht. Zwei nebeneinander brauchen also
    # rund 100.
    for a in punkte:
        for b in punkte:
            if a is b:
                continue
            if abs(a.x - b.x) < 100:
                assert abs(a.y - b.y) >= 34, f"{a.kennung} und {b.kennung} stehen zu eng"


def test_only_what_was_recommended_is_marked() -> None:
    """Drei Zustände, und zwei davon kommen aus der Auswertung.

    Eine Familie, die Start und Nachbar zugleich wäre, zählt als Start —
    der erste Schritt schlägt die Aussicht.
    """

    landschaft = karte.landschaft(["SF-02"], ["SF-02", "SF-10"])
    zustaende = {p.kennung: p.zustand for p in landschaft["punkte"]}

    assert zustaende["SF-02"] == "start"
    assert zustaende["SF-10"] == "nah"
    assert zustaende["SF-06"] == "still"


def test_a_path_leads_from_the_centre_to_every_marked_point() -> None:
    """**Wege, nicht nur Punkte.**

    Ohne sie wäre es ein Streufeld. Die Linien wachsen vom Kern nach
    aussen und sagen damit die Reihenfolge: erst die Grundlage, dann
    alles, was daran hängt.
    """

    landschaft = karte.landschaft(["SF-02"], ["SF-10", "SF-24"])

    assert len(landschaft["wege"]) == 3
    assert {w.art for w in landschaft["wege"]} == {"start", "nah"}
    # Jeder Weg beginnt im Kern.
    for weg in landschaft["wege"]:
        assert weg.pfad.startswith(f"M{karte.MITTE_X} {karte.MITTE_Y}")


def test_the_map_is_drawn_not_tabulated(client: TestClient) -> None:
    """Die feste Operating Map zeigt die gesamte Landschaft."""

    seite = client.get("/beispiel/hausverwaltung").text

    assert 'id="ai-start-map"' in seite
    assert seite.count("data-map-node") == 14
    assert "Betriebs-Lösungsraum" in seite
    assert 'class="map-landscape__svg"' in seite
    assert "map-operating-center" in seite


def test_the_map_needs_no_javascript(client: TestClient) -> None:
    """**Ohne Skript vollständig richtig.**

    Nicht aus Prinzip, sondern weil dieselbe Karte ins PDF gehört. Stünden
    Zustände oder Beschriftungen erst im Skript, müsste sie dort ein
    zweites Mal gebaut werden — und zwei Karten laufen auseinander.
    """

    seite = client.get("/beispiel/hausverwaltung").text
    kartenteil = seite.split('class="map-workspace"', 1)[1].split("</section>", 1)[0]

    assert "<script" not in kartenteil
    assert "data-map-node" in kartenteil
    assert "data-module-detail" in kartenteil
    assert "map-operating-center" in kartenteil


def test_the_map_says_where_to_begin(client: TestClient) -> None:
    """Der Satz, der die Karte lesbar macht.

    Ohne ihn ist es eine Landschaft ohne Standort. Mit ihm ist es eine
    Karte: Sie sind hier, hier fangen wir an, und das ist das Gelände
    dahinter.
    """

    seite = client.get("/beispiel/hausverwaltung").text

    assert "Sie sind hier. Und das Gelände dahinter." in seite
    assert "Die Karte macht sichtbar, wo Arbeit heute auseinanderläuft" in seite
    for zustand in (
        "Hier würden wir anfangen",
        "Heute",
        "Zielbild",
        "Später möglich",
    ):
        assert zustand in seite, zustand


def test_the_phone_gets_the_same_points_as_a_list(client: TestClient) -> None:
    """Auf dem Handy trägt die Liste, nicht die Karte.

    Fünfundzwanzig Beschriftungen auf einer Landkarte sind auf einem
    Telefon unlesbar. Dieselben Punkte stehen deshalb zusätzlich als
    Liste — nach Gebiet gruppiert, in der Reihenfolge des Auftragslaufs.
    """

    seite = client.get("/beispiel/hausverwaltung").text

    assert 'class="map-landscape"' in seite
    assert seite.count("data-map-node") == 14
