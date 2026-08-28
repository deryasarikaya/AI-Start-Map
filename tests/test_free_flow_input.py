"""Frei erzählen heisst: so lang, wie jemand reden will.

Die Interview-Seite verspricht ausdrücklich, dass dreissig Sekunden und zehn
Minuten beide in Ordnung sind. Ein Versprechen, das die Technik nicht hält,
ist schlimmer als keins — der Kunde merkt es erst, wenn seine Erzählung
abgeschnitten in der Auswertung landet.

Zehn Minuten Sprechen sind rund achtundzwanzigtausend Zeichen. Was hier
geprüft wird, ist genau das: dass sie ankommen, vollständig gespeichert
werden und dass die Seite keine Grenze einbaut, die sie nicht einhalten kann.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import engine
from app.models import AnalysisSession, InterviewQuestion

#: Ungefähr zehn Minuten gesprochene Sprache.
ZEHN_MINUTEN = (
    "Bei uns klingelt den ganzen Tag das Telefon und die Kunden fragen immer "
    "wieder nach dem Stand ihrer Sache. "
) * 260


def _gespeicherte_erzaehlung() -> str:
    with Session(engine) as sitzung:
        sitzungsnummer = sitzung.scalar(select(func.max(AnalysisSession.session_id)))
        zeilen = sitzung.scalars(
            select(InterviewQuestion).where(
                InterviewQuestion.session_id == sitzungsnummer
            )
        ).all()
    return next((zeile.answer_text or "" for zeile in zeilen), "")


def test_ten_minutes_of_talking_arrive_complete(client: TestClient) -> None:
    """Achtundzwanzigtausend Zeichen, ungekürzt.

    Weder das Feld noch die Route noch die Datenbank dürfen kürzen. Fiele
    hier eine Grenze ein, wäre das Versprechen auf der Seite eine Lüge, und
    zwar eine, die niemand bemerkt.
    """

    client.post("/begin", follow_redirects=False)

    antwort = client.post(
        "/interview",
        data={"free_description": ZEHN_MINUTEN},
        follow_redirects=False,
    )

    assert antwort.status_code == 303
    gespeichert = _gespeicherte_erzaehlung()
    assert len(gespeichert) > 27_000
    assert gespeichert.strip() == ZEHN_MINUTEN.strip()


def test_the_field_sets_no_limit_it_cannot_keep(client: TestClient) -> None:
    """Kein `maxlength` im Eingabefeld.

    Eine Zeichengrenze im Feld schneidet stillschweigend ab: Der Browser
    nimmt das Weitere gar nicht erst an, und wer spricht, merkt es nie.
    """

    client.post("/begin", follow_redirects=False)

    seite = client.get("/interview").text

    assert "maxlength" not in seite


def test_the_page_does_not_ask_for_brevity(client: TestClient) -> None:
    """Kein Wort, das zum Kürzen auffordert.

    „Erzähl mir kurz" stand in der Überschrift und widerspricht allem, was
    diese Seite will: Wer glaubt, er soll sich kurzfassen, lässt genau die
    Nebensätze weg, aus denen die Diagnose lebt.

    Auch die Zeitangabe ist gestrichen: Sie passte zu einer Seite, die
    schnell fertig sein wollte, nicht zu einer, die eine belastbare
    Analyse verspricht. Der Raum wird jetzt anders zugesagt.
    """

    client.post("/begin", follow_redirects=False)

    seite = client.get("/interview").text
    # Zeilenumbrüche in der Vorlage zerreissen sonst jeden Satz, den dieser
    # Test sucht — geprüft wird der Wortlaut, nicht die Formatierung.
    fliess = " ".join(seite.split())

    for auffordernd in ("kurz,", "in wenigen Sätzen", "maximal", "30 Sekunden"):
        assert auffordernd not in fliess, auffordernd
    assert "so ausführlich, wie es für Ihren Betrieb sinnvoll ist" in fliess
    # Statt einer Zeitangabe die Zusage, dass sich Ausführlichkeit lohnt.
    assert "Je konkreter Ihr Einblick, desto passender wird Ihre" in fliess


@pytest.mark.parametrize(
    "thema",
    ["Telefon", "Kunden", "Termine", "Kanäle"],
)
def test_the_page_opens_more_than_the_inbox(client: TestClient, thema: str) -> None:
    """Die Beispiele dürfen nicht auf Ablage eichen.

    Vorher nannte die Seite nur Zeitverlust, Zusammensuchen und
    Mehrfacharbeit — und danach erzählte auch jeder nur davon. Was jemand
    über sein Telefon oder seine wiederkehrenden Fragen gesagt hätte, kam
    nie zur Sprache, und damit war der halbe Katalog unerreichbar.

    Diese Aufgabe trägt jetzt der Leitfaden: sechs Bereiche als
    Orientierung, vom Kundenkontakt bis zu den Grenzen.
    """

    client.post("/begin", follow_redirects=False)

    seite = client.get("/interview").text

    assert thema in seite
