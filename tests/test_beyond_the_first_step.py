"""Der Ausbaupfad — und warum er weder erfunden noch klein sein darf.

Bis zu diesem Abschnitt sagt die Auswertung: Das können wir vereinfachen.
Hier sagt sie: Und so weit kann das gehen. Das ist der Unterschied zwischen
jemandem, der aufräumt, und jemandem, der zeigt, wohin es führt.

**Der Abschnitt war einmal eine Karte.** Eine einzige, mit einem Satz
darauf: „Sie müssen einfache Statusfragen nicht mehr selbst beantworten."
Das kam so zustande, dass der Ausblick ein Modul mit `stufe: spaeter` war —
also ein Eintrag in derselben Liste wie die Lösung. Und was in derselben
Liste steht, wird auch so geschrieben: als eine Funktion neben den anderen.
Auf „ein gemeinsamer Fahrzeugstand" folgte „Statusfragen automatisch
beantworten". Dieselbe Schiene, ein Merkmal weiter.

Jetzt ist es ein eigenes Feld und ein Weg mit mehreren Stationen, von denen
jede einen Bereich öffnet, den die vorige nicht berührt hat. Zwei Grenzen
werden hier festgehalten: dass keine Station eine schon geöffnete Familie
wiederholt — sonst wäre es wieder eine Karte in Serie —, und dass ein
fehlender Pfad den Abschnitt verschwinden lässt statt ihn zu erfinden.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.result_schema import Zielarchitektur
from app.services import example_service

#: Ein Weg, wie er sein soll: vier Bereiche, vier verschiedene Familien.
#: SF-02 Vorgangsmanagement → SF-01 Anfrageeingang → SF-10 Kundenportal →
#: SF-24 Kunden- und Objekthistorie.
PFAD = [
    {
        "stufe": "jetzt",
        "name": "Alle Vorgänge an einem Ort",
        "nutzen": "Sie müssen den Stand nicht mehr zusammensuchen.",
        "bausteine": ["Stand je Vorgang", "nächster Schritt"],
        "solution_family_ids": ["SF-02"],
    },
    {
        "stufe": "danach",
        "name": "Anfragen automatisch zuordnen",
        "nutzen": "Sie müssen eingehende Nachrichten nicht mehr selbst sortieren.",
        "bausteine": ["gemeinsamer Eingang", "Zuordnung zum Vorgang"],
        "solution_family_ids": ["SF-01"],
    },
    {
        "stufe": "danach",
        "name": "Kunden sehen selbst nach",
        "nutzen": "Sie müssen einfache Rückfragen nicht mehr selbst beantworten.",
        "bausteine": ["Stand des Auftrags", "Freigaben online", "Termine"],
        "solution_family_ids": ["SF-10"],
    },
    {
        "stufe": "spaeter",
        "name": "Kunden- und Objekthistorie",
        "nutzen": "Sie müssen Vorgeschichten nicht mehr aus dem Kopf holen.",
        "bausteine": ["frühere Aufträge", "Dokumente", "Kommunikation"],
        "solution_family_ids": ["SF-24"],
    },
]


def _mit_pfad(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, pfad: list[dict]
) -> str:
    """Dieselbe Beispielseite, nur mit einem gesetzten Ausbaupfad.

    Der hinterlegte Beispiellauf stammt von vor diesem Feld und bringt
    keinen mit. Das ist kein Mangel des Beispiels, sondern der Grund für
    den Vorgabewert: Ein alter Lauf soll lesbar bleiben und den Abschnitt
    weglassen, statt einen Pfad zu behaupten, den niemand erzeugt hat.
    """

    echt = example_service.example_result

    def ersatz(db: object, slug: str) -> object:
        return echt(db, slug).model_copy(update={"ausbaupfad": pfad})

    monkeypatch.setattr(example_service, "example_result", ersatz)
    return client.get("/beispiel/hausverwaltung").text


def test_the_path_gets_its_own_section(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Der Weg bekommt seinen eigenen Abschnitt, nicht eine vierte Kachel.

    Der Kunde muss nicht morgen eine grosse Lösung kaufen. Aber er soll
    sehen, dass aus dem ersten Schritt etwas wird — sonst kauft er eine
    Funktion und keine Richtung.
    """

    seite = _mit_pfad(client, monkeypatch, PFAD)

    assert "So könnte Ihre Lösung mit Ihrem Betrieb wachsen" in seite
    assert "Sie müssen nicht alles auf einmal umsetzen" in seite


def test_without_a_path_the_section_disappears(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Kein Pfad, kein Abschnitt.

    Ein erfundener Ausblick wäre schlimmer als keiner: Er verspricht etwas,
    das im geprüften Katalog keine Entsprechung hat, und genau daran
    zerbricht das Vertrauen, das die Seite vorher aufgebaut hat.
    """

    seite = _mit_pfad(client, monkeypatch, [])

    assert "So könnte Ihre Lösung mit Ihrem Betrieb wachsen" not in seite


def test_every_station_is_visible_as_a_step(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Vier Stationen, nummeriert, mit ihren Teilen.

    Nebeneinander gestellte Kacheln sind eine Sammlung, und eine Sammlung
    hat keine Richtung. Die Ordnungszahlen und die Reihenfolge sind der
    Unterschied zwischen „hier ist noch etwas" und „so weit geht das".
    """

    seite = _mit_pfad(client, monkeypatch, PFAD)

    for schritt in PFAD:
        assert schritt["name"] in seite, schritt["name"]
        assert schritt["nutzen"] in seite, schritt["nutzen"]
    assert seite.count('class="station station--') == 4
    # Die Teile eines Bereichs zeigen, woraus so ein Schritt besteht.
    assert "Freigaben online" in seite


def test_the_foundation_is_marked_as_the_one_being_built(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Die erste Station ist die Grundlage, nicht die erste Aussicht.

    Ohne diesen Unterschied liest sich alles gleich weit weg — auch das,
    was gerade angeboten wird. Der Kunde soll sehen, wo er einsteigt.
    """

    seite = _mit_pfad(client, monkeypatch, PFAD)

    assert "station station--jetzt" in seite
    assert "Die Grundlage" in seite
    assert "Ausbau" in seite


def test_the_section_says_that_the_path_is_not_yet_decided(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Der Satz, der den Weg ehrlich hält.

    Ohne ihn liest sich der Abschnitt wie ein Angebot über fünf Stufen,
    das niemand gemacht hat — und der erste Schritt, um den es eigentlich
    geht, verliert daneben an Gewicht.
    """

    seite = _mit_pfad(client, monkeypatch, PFAD)

    assert "hängt von Ihren bestehenden Systemen" in seite
    assert "Das klären wir gemeinsam." in seite


def _auswahl(pfad: list[dict]) -> dict[str, object]:
    """Eine gültige Auswahl mit einem gegebenen Ausbaupfad.

    Die Vorlage kommt aus dem Vertragstest, damit hier nur der Pfad zur
    Debatte steht — und nicht daneben eine zweite, veraltende Kopie der
    ganzen Zielarchitektur entsteht.
    """

    from tests.test_result_contract import _zielarchitektur

    return _zielarchitektur(ausbaupfad=pfad)


def test_a_station_may_not_open_a_door_that_is_already_open() -> None:
    """**Die Regel, an der der alte Ausblick gescheitert wäre.**

    „Gemeinsamer Fahrzeugstand" und danach „Statusauskunft zum
    Fahrzeugstand" sind zwei Kacheln und ein Thema. Solange nichts das
    verbietet, ist es der bequemste Weg für das Modell: Es kennt die
    Familie schon, es hat gerade darüber geschrieben, und die nächste
    Stufe schreibt sich fast von selbst.

    Der Server lässt es nicht durch. Ein Weg, der zweimal dieselbe Tür
    öffnet, führt nirgendwohin.
    """

    doppelt = [
        dict(PFAD[0]),
        dict(PFAD[1]),
        {**PFAD[2], "solution_family_ids": ["SF-02"]},
    ]

    with pytest.raises(ValidationError) as fehler:
        Zielarchitektur.model_validate(_auswahl(doppelt))

    assert "denselben Bereich noch einmal" in str(fehler.value)


def test_a_station_without_a_catalogue_family_is_rejected() -> None:
    """Auch der Ausblick kommt aus dem freigegebenen Katalog.

    Gerade hier wäre das Erfinden verlockend: Ein Ausblick klingt gross,
    niemand prüft ihn beim Lesen, und eine erfundene Stufe fällt erst auf,
    wenn jemand sie bestellt.
    """

    erfunden = [{**PFAD[0], "solution_family_ids": ["SF-99"]}]

    with pytest.raises(ValidationError) as fehler:
        Zielarchitektur.model_validate(_auswahl(erfunden))

    assert "die es nicht gibt" in str(fehler.value)
