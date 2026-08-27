"""„Passt das so?" — die Bestätigung zwischen Erzählung und Ergebnis.

Diese Seite hatte ein Problem, das keine Fehlermeldung erzeugt: Sie fragte
„Möchten Sie noch etwas ergänzen?" und stellte darunter ein offenes
Textfeld. Ein offenes Textfeld ist eine Frage, auch ohne Fragezeichen — und
damit gab die Seite dem Kunden wieder Arbeit, statt ihm eine Antwort zu
geben. Er will an dieser Stelle sein Ergebnis, nicht einen zweiten Aufsatz.

Geprüft wird deshalb beides: dass die Zustimmung der erste und breiteste
Weg ist, und dass die Korrektur trotzdem vollständig erreichbar bleibt —
auch ohne JavaScript.

Der zweite Teil betrifft die Rückfrage des Modells. Sie kommt selten, und
das ist Absicht. Weil Absicht und Versehen von aussen gleich aussehen, ist
hier festgehalten, *wo* die Entscheidung fällt: nicht im Server, sondern im
Prompt. Der Server begrenzt nur die Anzahl der Runden.

Alles mit Attrappen — kein echter Aufruf.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.result_schema import Diagnose, narrative
from app.services import analysis_service
from tests.test_result_contract import _diagnose

ERZAEHLT = "Wir sind zu dritt und suchen ständig Unterlagen zusammen."

FRAGE = {
    "frage": "Wer gibt bei Ihnen die Rechnungen frei — Sie selbst?",
    "warum": "Davon hängt ab, wie weit die Vorbereitung gehen darf.",
}


def _teil_eins(rueckfrage: dict[str, str] | None) -> Diagnose:
    payload = _diagnose()
    payload["rueckfrage"] = rueckfrage
    payload["verstanden"]["belege"] = [
        {"zitat": "Wir sind zu dritt", "bedeutung": "Ein kleiner Betrieb."},
    ]
    with narrative(ERZAEHLT):
        return Diagnose.model_validate(payload)


@pytest.fixture
def ohne_rueckfrage(monkeypatch: pytest.MonkeyPatch) -> None:
    """Der Normalfall: Das Modell fragt nicht."""

    monkeypatch.setattr(
        analysis_service, "generate_diagnosis", lambda **_k: _teil_eins(None)
    )


def _bis_zur_seite(client: TestClient) -> None:
    client.post("/begin", follow_redirects=False)
    client.post(
        "/interview", data={"free_description": ERZAEHLT}, follow_redirects=False
    )
    assert client.post("/analyze").json()["redirect_url"] == "/verstanden"


def test_the_page_asks_for_agreement_not_for_more_work(
    client: TestClient, ohne_rueckfrage: None
) -> None:
    """Die Seite fragt, ob es passt — nicht, was noch fehlt.

    „Möchten Sie noch etwas ergänzen?" klingt höflich und ist trotzdem eine
    Aufgabe: Der Kunde muss seine eigene Erzählung noch einmal durchgehen,
    um sie zu beantworten. „Passt das so?" beantwortet er mit einem Blick.
    """

    _bis_zur_seite(client)

    seite = client.get("/verstanden").text

    assert "Passt das so?" in seite
    assert "Möchten Sie noch etwas ergänzen?" not in seite


def test_saying_yes_is_the_first_and_widest_way(
    client: TestClient, ohne_rueckfrage: None
) -> None:
    """Die Zustimmung steht vor der Korrektur und trägt die volle Schaltfläche.

    Standen beide gleich gross nebeneinander, las sich das wie eine echte
    Wahl zwischen zwei Wegen. Es ist keine: Der eine ist der Normalfall,
    der andere die Ausnahme.
    """

    _bis_zur_seite(client)

    seite = client.get("/verstanden").text

    ja = seite.index("Ja, Auswertung erstellen")
    korrektur = seite.index("Etwas korrigieren oder ergänzen")
    assert ja < korrektur
    assert re.search(r'<button class="btn"[^>]*>Ja, Auswertung erstellen', seite)


def test_the_correction_field_is_out_of_the_way_until_it_is_wanted(
    client: TestClient, ohne_rueckfrage: None
) -> None:
    """Das Textfeld steht zugeklappt, nicht offen.

    Ein offenes Feld auf einer Bestätigungsseite ist eine unausgesprochene
    Aufforderung. Wer einverstanden ist, soll an nichts vorbei müssen.
    """

    _bis_zur_seite(client)

    seite = client.get("/verstanden").text

    assert '<details class="korrektur">' in seite
    assert '<details class="korrektur" open' not in seite
    innen = seite.split('<details class="korrektur">', 1)[1].split("</details>", 1)[0]
    assert "<textarea" in innen


def test_the_correction_works_without_javascript(
    client: TestClient, ohne_rueckfrage: None
) -> None:
    """Aufklappen und Abschicken brauchen kein Skript.

    `<details>` klappt der Browser selbst auf, und das Feld liegt im
    Formular. Ein Kunde mit blockiertem JavaScript verliert hier nichts —
    und die Seite lädt ohnehin kein eigenes Skript.
    """

    _bis_zur_seite(client)
    seite = client.get("/verstanden").text
    assert "<script" not in seite

    antwort = client.post(
        "/verstanden",
        data={"antwort": "Die Unterlagen liegen bei mir im Büro.", "weiter": "nein"},
        follow_redirects=False,
    )

    assert antwort.status_code == 303
    assert antwort.headers["location"] == "/processing"


def test_a_question_from_the_model_keeps_its_open_field(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Wurde gefragt, steht das Feld offen da.

    Der Unterschied ist der Grund: Unter einer gestellten Frage ist ein
    offenes Feld die Antwort, nicht eine Aufgabe. Nur ohne Frage war es
    eine.
    """

    monkeypatch.setattr(
        analysis_service, "generate_diagnosis", lambda **_k: _teil_eins(FRAGE)
    )
    _bis_zur_seite(client)

    seite = client.get("/verstanden").text

    assert FRAGE["frage"] in seite
    assert "<textarea" in seite
    assert '<details class="korrektur">' not in seite
    assert "<h2>Passt das so?</h2>" not in seite


def test_the_server_never_swallows_a_question_in_the_first_round(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """**Wo die Entscheidung fällt.**

    Dass die Rückfrage selten kommt, liegt nicht am Server: In der ersten
    Runde reicht er jede Frage durch, die das Modell stellt. Die Auswahl
    trifft allein der Prompt. Wer die Frage häufiger sehen will, muss dort
    ansetzen — nicht hier.

    Dieser Test hält diese Arbeitsteilung fest. Fällt er, hat jemand eine
    zweite, unsichtbare Hürde eingebaut.
    """

    monkeypatch.setattr(
        analysis_service, "generate_diagnosis", lambda **_k: _teil_eins(FRAGE)
    )
    _bis_zur_seite(client)

    seite = client.get("/verstanden").text

    assert FRAGE["frage"] in seite
    assert FRAGE["warum"] in seite


def test_the_prompt_names_when_a_question_is_worth_it() -> None:
    """**Woran der Prompt die Frage misst.**

    Der Prompt sagt ausdrücklich, dass die Rückfrage meistens leer bleibt.
    Das ist eine Entscheidung, keine Panne — aber sie ist nur so lange
    eine, wie auch die Bedingung dabeisteht, unter der gefragt werden
    *soll*. Ohne sie bliebe nur „meistens leer", und dann fiele die Frage
    still ganz weg.
    """

    prompt = Path("app/prompts/diagnose.md").read_text(encoding="utf-8")

    abschnitt = prompt.split("## Die Rückfrage", 1)[1].split("\n## ", 1)[0]
    assert "ein Modul hinzufügt oder streicht" in abschnitt
    assert "Aufgabenteilung verschiebt" in abschnitt
    assert "Engpass anders setzt" in abschnitt
    assert "die man jedem Betrieb" in abschnitt
