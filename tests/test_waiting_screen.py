"""Der Warteschirm darf nur zeigen, was er weiss.

Eine Minute vor einem Bildschirm, der sich nicht bewegt, fuehlt sich an wie
ein Fehler. Deshalb erzaehlt diese Seite, was gerade geschieht.

Genau darin liegt aber die Versuchung: Ein Balken, der gleichmaessig
waechst, sieht besser aus als die Wahrheit -- und ist erfunden. Belegbar
sind zwei Dinge, naemlich welcher der beiden Modellaufrufe laeuft. Was hier
geprueft wird, ist beides: dass die Seite diese zwei Zustaende wirklich
meldet, und dass sie ueber den Rest schweigt.
"""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import repository
from app.database import SessionFactory


def _sitzung_beginnen(client: TestClient) -> int:
    client.post("/begin", follow_redirects=False)
    client.post(
        "/interview",
        data={
            "free_description": (
                "Kunden rufen den ganzen Tag an und fragen nach dem Stand. "
                "Ich muss jedes Mal in der Werkstatt nachsehen."
            )
        },
        follow_redirects=False,
    )
    with SessionFactory() as datenbank:
        return _letzte_sitzungsnummer(datenbank)


def _letzte_sitzungsnummer(datenbank: Session) -> int:
    from sqlalchemy import func, select

    from app.models import AnalysisSession

    return int(datenbank.scalar(select(func.max(AnalysisSession.session_id))))


def test_the_first_call_is_reported_as_the_first_phase(client: TestClient) -> None:
    """Ohne Zwischenstand laeuft der erste Aufruf.

    Der Lauf legt seinen Zwischenstand erst zwischen den beiden Aufrufen ab.
    Ist keiner da, steht die Auswertung also noch am Anfang -- und genau das
    soll der Warteschirm sagen, statt eine Zahl zu raten.
    """

    _sitzung_beginnen(client)

    stand = client.get("/analysis-status").json()

    assert stand["state"] == "pending"
    assert stand["phase"] == "verstehen"


def test_the_second_call_is_reported_as_the_second_phase(client: TestClient) -> None:
    """Mit Zwischenstand laeuft der zweite Aufruf.

    Das ist der einzige Uebergang, den die Datenbank hergibt. Faellt er weg,
    steht der Kunde wieder eine ganze Minute vor demselben Bild.
    """

    sitzungsnummer = _sitzung_beginnen(client)
    with SessionFactory() as datenbank:
        repository.save_partial_result(
            datenbank,
            sitzungsnummer,
            payload={"diagnose": "steht"},
            narrative="Kunden rufen den ganzen Tag an.",
            rounds=1,
            moving_on=True,
        )
        datenbank.commit()

    stand = client.get("/analysis-status").json()

    assert stand["state"] == "pending"
    assert stand["phase"] == "loesung"


def test_the_screen_names_every_station_of_the_way(client: TestClient) -> None:
    """Vier Stationen, und alle vier sind benannt.

    Der Kunde soll sehen, dass hier mehr passiert als Lesen: dass auch nach
    spaeteren Moeglichkeiten gesucht wird. Wer das nicht liest, haelt die
    Wartezeit fuer eine Textverarbeitung.
    """

    _sitzung_beginnen(client)

    seite = client.get("/processing").text

    for station in (
        "Ihre Beschreibung verstehen",
        "Potenziale erkennen",
        "Passende Ansätze prüfen",
        "Auswertung vorbereiten",
    ):
        assert station in seite, station
    # Die Seite nennt ausdrücklich auch das Spätere, nicht nur den ersten
    # Schritt — sonst liest sich das Warten wie eine Textverarbeitung.
    assert "späteren Möglichkeiten" in seite


def test_the_screen_invents_no_progress(client: TestClient) -> None:
    """Kein Prozentwert, kein Balken.

    Eine erfundene Prozentzahl ist die bequemste Luege einer Warteseite: Sie
    beruhigt, bis sie bei 90 Prozent stehen bleibt. Was nicht messbar ist,
    wird auch nicht gezeigt.
    """

    _sitzung_beginnen(client)

    seite = client.get("/processing").text

    for erfunden in ("progress-bar", "%\"", "Prozent", 'role="progressbar"'):
        assert erfunden not in seite, erfunden


def test_only_the_proven_station_starts_marked(client: TestClient) -> None:
    """Beim Laden traegt genau eine Station einen Haken.

    Uebernommen ist die Erzaehlung wirklich -- sie steht in der Datenbank.
    Alles Weitere haengt am Lauf, und ein Haken ohne Grund ist schlimmer als
    keiner.
    """

    _sitzung_beginnen(client)

    seite = client.get("/processing").text

    assert seite.count("phase phase--fertig") == 1
    assert 'data-phase="uebernommen"' in seite


def test_the_error_keeps_the_customers_words(client: TestClient) -> None:
    """Der Fehlerfall sagt zuerst, dass nichts verloren ist.

    Wer eine Minute gewartet hat und dann eine Stoerung liest, fuerchtet als
    Erstes um seine Erzaehlung. Diese Sorge muss der Text beantworten, bevor
    er zum Wiederholen einlaedt.
    """

    _sitzung_beginnen(client)

    seite = client.get("/processing").text

    assert "Die Auswertung konnte gerade nicht abgeschlossen werden." in seite
    assert "Ihre Beschreibung ist weiterhin vorhanden." in seite
    assert "Erneut versuchen" in seite
