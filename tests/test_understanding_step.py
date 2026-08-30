"""Der Agentenschritt zwischen Erzählung und Ergebnis.

Die Anwendung zeigt hier, dass sie zugehört hat, und stellt höchstens eine
Frage. Was hier abgesichert wird, ist vor allem das, was der Kunde nicht sehen
soll: eine Frage in der letzten Runde, eine dritte Runde, oder einen
Modellaufruf, den niemand ausgelöst hat.

Alles mit Attrappen — kein echter Aufruf.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import repository
from app.result_schema import Diagnose, narrative
from app.services import analysis_service
from tests.conftest import the_current_session
from tests.test_result_contract import _diagnose

ERZAEHLT = "Wir sind zu dritt und suchen ständig Unterlagen zusammen."

def _teil_eins(rueckfrage: dict[str, str] | None) -> Diagnose:
    """Ein gültiger oberer Teil mit oder ohne Rückfrage.

    Die Belege müssen aus **dieser** Erzählung stammen, sonst sortiert die
    Zitatprüfung sie aus und die Seite zeigt gar keins.
    """

    payload = _diagnose()
    payload["rueckfrage"] = rueckfrage
    payload["verstanden"]["belege"] = [
        {"zitat": "Wir sind zu dritt", "bedeutung": "Ein kleiner Betrieb."},
        {
            "zitat": "suchen ständig Unterlagen zusammen",
            "bedeutung": "Die Ablage trägt nicht.",
        },
    ]
    with narrative(ERZAEHLT):
        return Diagnose.model_validate(payload)


FRAGE = {
    "frage": "Wer gibt bei Ihnen die Rechnungen frei — Sie selbst?",
    "warum": "Davon hängt ab, wie weit die Vorbereitung gehen darf.",
}


@pytest.fixture
def mit_rueckfrage(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Das Modell liefert jedes Mal dieselbe Rückfrage. Zählt die Aufrufe."""

    erzaehlungen: list[str] = []

    def antworte(*, narrative_text: str, **_kwargs: object) -> Diagnose:
        erzaehlungen.append(narrative_text)
        return _teil_eins(FRAGE)

    monkeypatch.setattr(analysis_service, "generate_diagnosis", antworte)
    return erzaehlungen


def _bis_zur_verstandenseite(client: TestClient) -> None:
    client.post("/begin", follow_redirects=False)
    client.post("/interview", data={"free_description": ERZAEHLT}, follow_redirects=False)
    assert client.post("/analyze").json()["redirect_url"] == "/verstanden"


def test_a_follow_up_question_is_shown(
    client: TestClient, mit_rueckfrage: list[str]
) -> None:
    """Liefert das Modell eine Frage, steht sie auf der Seite."""

    _bis_zur_verstandenseite(client)

    seite = client.get("/verstanden")

    assert seite.status_code == 200
    assert FRAGE["frage"] in seite.text
    assert FRAGE["warum"] in seite.text
    assert "Diese Information würde Ihre Empfehlung tatsächlich verändern" in seite.text
    assert "Warum wir fragen:" in seite.text


def test_without_a_question_the_page_says_so(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ohne Frage wird der Kunde nur um seine Zustimmung gebeten.

    Das ist der Normalfall. Ein Agent, der nur fragt, wenn er etwas braucht,
    wirkt klüger als einer, der immer fragt — und die Seite gibt ihm dann
    auch nichts zu tun ausser weiterzugehen.
    """

    monkeypatch.setattr(
        analysis_service, "generate_diagnosis", lambda **_k: _teil_eins(None)
    )
    _bis_zur_verstandenseite(client)

    seite = client.get("/verstanden")

    assert "Passt das so?" in seite.text
    assert "Eine Information fehlt mir noch" not in seite.text


def test_skipping_goes_straight_to_the_result(
    client: TestClient, mit_rueckfrage: list[str]
) -> None:
    """Wer überspringt, bekommt das Ergebnis — ohne dass Aufruf 1 erneut läuft."""

    _bis_zur_verstandenseite(client)
    assert len(mit_rueckfrage) == 1

    client.post("/verstanden", data={"weiter": "ja"}, follow_redirects=False)
    zweiter = client.post("/analyze")

    assert zweiter.json()["redirect_url"] == "/results"
    # Der erste Aufruf ist genau einmal gelaufen, nicht zweimal.
    assert len(mit_rueckfrage) == 1
    assert client.get("/results").status_code == 200


def test_an_answer_reruns_the_first_call_with_it(
    client: TestClient,
    database_session: Session,
    mit_rueckfrage: list[str],
) -> None:
    """Antwortet der Kunde, läuft Aufruf 1 erneut — mit der Antwort darin."""

    _bis_zur_verstandenseite(client)

    client.post(
        "/verstanden",
        data={"antwort": "Die Rechnungen gebe ich selbst frei.", "weiter": "nein"},
        follow_redirects=False,
    )
    assert client.post("/analyze").json()["redirect_url"] == "/verstanden"

    assert len(mit_rueckfrage) == 2
    zweite_erzaehlung = mit_rueckfrage[1]
    assert "Die Rechnungen gebe ich selbst frei." in zweite_erzaehlung
    # Deutlich getrennt, damit im Prompt erkennbar bleibt, was nachgereicht
    # wurde.
    assert "Auf Nachfrage ergänzt:" in zweite_erzaehlung
    assert zweite_erzaehlung.startswith(ERZAEHLT)


def test_the_answer_survives_a_reload(
    client: TestClient,
    database_session: Session,
    mit_rueckfrage: list[str],
) -> None:
    """Die Ergänzung liegt in der Datenbank, nicht nur im Speicher."""

    _bis_zur_verstandenseite(client)
    client.post(
        "/verstanden",
        data={"antwort": "Ich gebe selbst frei.", "weiter": "nein"},
        follow_redirects=False,
    )

    database_session.expire_all()
    zwischenstand = repository.get_partial_result(
        database_session, the_current_session(client)
    )
    assert zwischenstand is not None
    assert "Ich gebe selbst frei." in zwischenstand.narrative
    # Leer heisst: Der obere Teil muss noch einmal geschrieben werden.
    assert zwischenstand.payload is None


def test_there_is_no_third_round(
    client: TestClient, mit_rueckfrage: list[str]
) -> None:
    """Nach der zweiten Runde ist Schluss, auch wenn das Modell wieder fragt.

    Die Attrappe liefert in jeder Runde eine Rückfrage. Genau dagegen ist die
    Grenze gebaut: Sonst hinge der Kunde in einer Schleife, die nur der Agent
    beendet.
    """

    _bis_zur_verstandenseite(client)
    client.post(
        "/verstanden", data={"antwort": "Noch etwas.", "weiter": "nein"},
        follow_redirects=False,
    )
    client.post("/analyze")

    zweite_runde = client.get("/verstanden")

    assert len(mit_rueckfrage) == 2
    assert FRAGE["frage"] not in zweite_runde.text
    assert "Ich habe alles, was ich brauche" in zweite_runde.text
    # Eine Schaltfläche zum Weitergehen, kein Textfeld mehr.
    assert zweite_runde.text.count("<button") == 1
    assert "<textarea" not in zweite_runde.text

    # Und eine erneut geschickte Antwort löst keinen dritten Aufruf aus.
    client.post(
        "/verstanden", data={"antwort": "Und noch etwas.", "weiter": "nein"},
        follow_redirects=False,
    )
    assert client.post("/analyze").json()["redirect_url"] == "/results"
    assert len(mit_rueckfrage) == 2


def test_the_normal_case_costs_two_model_calls(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ohne Ergänzung bleibt es bei zwei Aufrufen, mit Ergänzung sind es drei."""

    aufrufe: list[str] = []
    monkeypatch.setattr(
        analysis_service,
        "generate_diagnosis",
        lambda **_k: (aufrufe.append("eins"), _teil_eins(None))[1],
    )
    echt_teil_zwei = analysis_service.generate_result_part_two
    monkeypatch.setattr(
        analysis_service,
        "generate_result_part_two",
        lambda **kwargs: (aufrufe.append("zwei"), echt_teil_zwei(**kwargs))[1],
    )

    _bis_zur_verstandenseite(client)
    client.post("/verstanden", data={"weiter": "ja"}, follow_redirects=False)
    client.post("/analyze")

    assert aufrufe == ["eins", "zwei"]


def test_the_understanding_page_shows_one_quote_not_three(
    client: TestClient, mit_rueckfrage: list[str]
) -> None:
    """Die Seite zeigt, dass zugehört wurde — sie spielt nicht alles zurück."""

    _bis_zur_verstandenseite(client)

    seite = client.get("/verstanden")

    assert seite.text.count('<blockquote class="evidence-card">') == 1


def test_the_page_is_not_reachable_before_the_first_call(client: TestClient) -> None:
    """Ohne Zwischenstand geht es zurück auf den Warteschirm."""

    client.post("/begin", follow_redirects=False)
    client.post("/interview", data={"free_description": ERZAEHLT}, follow_redirects=False)

    antwort = client.get("/verstanden", follow_redirects=False)

    assert antwort.status_code == 303
    assert antwort.headers["location"] == "/processing"
