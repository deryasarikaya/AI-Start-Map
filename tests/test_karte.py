"""Die AI Start Map — das eine, was nicht erzeugt wird.

Jede andere Aussage der Auswertung entsteht aus der Erzählung. Genau das
war beim Ausblick das Problem: Ein Modell, das eine Zukunft erfinden soll,
bleibt auf der Schiene, über die es gerade geschrieben hat.

Die Karte dreht es um. Sie liegt fest, zeigt das ganze Gelände, und pro
Kunde wird nur markiert. Was hier geprüft wird, ist deshalb vor allem,
dass sie **nicht** erzeugt wird: dass jeder Betrieb dieselbe Form und
dieselbe Grösse sieht, dass die Punkte aus dem freigegebenen Katalog
kommen, und dass sie ohne JavaScript vollständig stimmt — sonst fehlte sie
im PDF.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import karte, solution_catalog


def test_the_map_is_the_same_landscape_for_everyone() -> None:
    """Sechs Gebiete, immer dieselben, in jeder Auswertung.

    Das ist der Grund, warum die Vision nicht zu klein ausfallen kann: Sie
    hängt nicht davon ab, was ein Modell für diesen Betrieb einfällt.
    """

    leer = karte.landschaft()
    voll = karte.landschaft(["SF-02"], ["SF-10", "SF-24"])

    assert [g.name for g in leer] == [g.name for g in voll]
    assert len(leer) == 6
    assert [len(g.punkte) for g in leer] == [len(g.punkte) for g in voll]


def test_every_point_is_a_released_family() -> None:
    """Kein Punkt ohne Katalog.

    Die Karte ist der Ort, an dem eine Erfindung am wenigsten auffiele:
    Sie klingt gross, niemand prüft sie beim Lesen, und eine erfundene
    Möglichkeit fällt erst auf, wenn jemand sie bestellt.
    """

    erlaubt = set(solution_catalog.katalog())

    kennungen = {p.kennung for g in karte.landschaft() for p in g.punkte}

    assert kennungen
    assert kennungen <= erlaubt


def test_the_points_speak_the_catalogue_s_own_words() -> None:
    """Name und Nutzen stehen schon im Katalog.

    `kundennaher_name` und `was_danach_im_betrieb_anders_ist` liegen seit
    Batch 10 in jeder Familie und wurden nirgends gezeigt. Für die Karte
    ist damit nichts zu erfinden — und deshalb kann sie auch nichts
    behaupten, was der Katalog nicht hergibt.
    """

    katalog = solution_catalog.katalog()

    for gebiet in karte.landschaft():
        for punkt in gebiet.punkte:
            familie = katalog[punkt.kennung]
            erwartet = familie.kundennaher_name or familie.name
            assert punkt.name == erwartet


def test_only_what_was_recommended_is_marked() -> None:
    """Drei Zustände, und zwei davon kommen aus der Auswertung.

    `start` sind die Familien der empfohlenen Module, `nah` die des
    Ausbaupfads, alles andere bleibt still. Eine Familie, die beides wäre,
    zählt als Start — der erste Schritt schlägt die Aussicht.
    """

    gebiete = karte.landschaft(["SF-02"], ["SF-02", "SF-10"])
    zustaende = {p.kennung: p.zustand for g in gebiete for p in g.punkte}

    assert zustaende["SF-02"] == "start"
    assert zustaende["SF-10"] == "nah"
    assert zustaende["SF-06"] == "still"


def test_the_quiet_points_stay_readable_not_hidden(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Was still ist, bleibt erreichbar — und zugeklappt.

    Fünfundzwanzig gleich laute Punkte wären wieder „viel Zeug". Aber wer
    entdeckt, dass hinter seinem ersten Schritt noch fünf Gebiete liegen,
    ruft an; genau das soll er. Deshalb eine stille Zahl, die sich öffnen
    lässt, statt einer Auslassung.
    """

    seite = client.get("/beispiel/hausverwaltung").text

    assert '<details class="stille">' in seite
    assert 'class="stille" open' not in seite
    assert "weitere Möglichkeiten" in seite


def test_the_map_needs_no_javascript(client: TestClient) -> None:
    """**Ohne Skript vollständig richtig.**

    Nicht aus Prinzip, sondern weil dieselbe Karte ins PDF gehört. Stünden
    Zustände oder Beschriftungen erst im Skript, müsste sie dort ein
    zweites Mal gebaut werden — und zwei Karten laufen auseinander.
    """

    seite = client.get("/beispiel/hausverwaltung").text
    kartenteil = seite.split('<div class="karte">', 1)[1].split("</section>", 1)[0]

    assert "<script" not in kartenteil
    assert "punkt--start" in kartenteil or "punkt--nah" in kartenteil
    assert "Ihr gemeinsamer Arbeitsstand" in kartenteil


def test_the_map_says_where_to_begin(client: TestClient) -> None:
    """Der Satz, der die Karte lesbar macht.

    Ohne ihn ist es eine Landschaft ohne Standort. Mit ihm ist es eine
    Karte: Sie sind hier, hier fangen wir an, und das ist das Gelände
    dahinter.
    """

    seite = client.get("/beispiel/hausverwaltung").text

    assert "Sie sind hier. Und das ist das Gelände dahinter." in seite
    assert "Hervorgehoben ist, wo ein sinnvoller Startpunkt liegt." in seite
    for zustand in (
        "Hier würden wir anfangen",
        "Das liegt in der Nähe",
        "Das gibt es auch",
    ):
        assert zustand in seite, zustand
