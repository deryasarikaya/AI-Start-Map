"""Der Ausblick — und warum er nie erfunden sein darf.

Bis zu diesem Abschnitt sagt die Auswertung: Das können wir vereinfachen.
Hier sagt sie: Und das wäre für Ihren Betrieb ausserdem möglich. Das ist der
Unterschied zwischen jemandem, der aufräumt, und jemandem, der zeigt, wohin
es gehen kann.

Genau deshalb ist er die gefährlichste Stelle der Seite. Ein Ausblick lädt
zum Träumen ein, und Träume lassen sich leicht erfinden. Was hier
festgehalten wird, ist die Grenze: Gezeigt wird nur, was das Modell selbst
auf `spaeter` gesetzt hat — aus dem freigegebenen Katalog, gebunden an einen
Engpass, den der Kunde beschrieben hat.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.services import example_service


def _mit_stufen(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, *stufen: str | None
) -> str:
    """Dieselbe Beispielseite, nur mit gesetzten Stufen an den Modulen."""

    echt = example_service.example_result

    def ersatz(db: object, slug: str) -> object:
        ergebnis = echt(db, slug)
        module = [
            modul.model_copy(update={"stufe": stufe})
            for modul, stufe in zip(ergebnis.module, stufen)
        ]
        return ergebnis.model_copy(update={"module": module})

    monkeypatch.setattr(example_service, "example_result", ersatz)
    return client.get("/beispiel/hausverwaltung").text


def test_the_outlook_shows_what_comes_later(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ein Modul auf `spaeter` bekommt seinen eigenen Abschnitt.

    Der Kunde muss nicht morgen eine grosse Lösung kaufen. Aber er soll
    wissen, dass es sie gibt — sonst erfährt er von einem Assistenten, der
    ans Telefon geht, nie etwas.
    """

    seite = _mit_stufen(client, monkeypatch, "jetzt", "jetzt", "danach", "spaeter")

    assert "Was darüber hinaus für Sie möglich wäre" in seite


def test_without_a_later_stage_the_section_disappears(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Kein `spaeter`, kein Ausblick.

    Ein erfundener Ausblick wäre schlimmer als keiner: Er verspricht etwas,
    das im geprüften Katalog keine Entsprechung hat, und genau daran
    zerbricht das Vertrauen, das die Seite vorher aufgebaut hat.
    """

    seite = _mit_stufen(client, monkeypatch, "jetzt", "jetzt", "danach", "danach")

    assert "Was darüber hinaus für Sie möglich wäre" not in seite


def test_a_later_module_is_not_shown_twice(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Was im Ausblick steht, steht nicht auch bei den Bausteinen.

    Sonst liest der Kunde dasselbe zweimal — einmal als Angebot und einmal
    als Aussicht — und weiss am Ende nicht, was er nun bekommt.
    """

    seite = _mit_stufen(client, monkeypatch, "jetzt", "jetzt", "danach", "spaeter")

    bausteine, _, ausblick = seite.partition("Was darüber hinaus für Sie möglich wäre")
    ausblicksname = "Abgleich mit der Hausverwaltungssoftware"
    assert ausblicksname in ausblick
    assert ausblicksname not in bausteine


def test_the_outlook_says_that_it_is_not_the_offer(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Der Satz, der den Ausblick ehrlich hält.

    Ohne ihn liest sich der Abschnitt wie ein Angebot, das niemand gemacht
    hat — und der erste Schritt, um den es eigentlich geht, verliert daneben
    an Gewicht.
    """

    seite = _mit_stufen(client, monkeypatch, "jetzt", "jetzt", "danach", "spaeter")

    assert "Das gehört nicht zum ersten Schritt" in seite
