from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import repository
from app.web import session

def test_landing_voice_fallback_and_mobile_assets(client: TestClient) -> None:
    landing = client.get("/")
    assert landing.status_code == 200
    for text in (
        "Kostenlose individuelle KI-Analyse für kleine Betriebe",
        "Erzählen Sie, wie Ihr Betrieb wirklich läuft.",
        "Das sehen Sie nach Ihrer Analyse",
        "KI kann heute weit mehr als Texte schreiben",
        "So entsteht Ihre persönliche AI Start Map",
        "Meine persönliche AI Start Map erstellen",
    ):
        assert text in landing.text
    # **Die Startseite duzt nicht mehr.** Sie war die letzte Stelle, an der
    # die Anrede zwischen Eingang und Auswertung kippte.
    for du in (" du ", " dir ", " dich ", "dein", "euch"):
        assert du not in landing.text.lower(), du
    # Und sie fordert nirgends zur Kürze auf - wer glaubt, er solle sich
    # kurzfassen, lässt genau die Nebensätze weg, aus denen die Diagnose lebt.
    assert "kurz" not in landing.text.lower()
    assert "RAG" not in landing.text
    assert "LLM" not in landing.text
    # Die Startseite zeigt kein Eingabefeld - erzählt wird erst danach.
    assert "business_context" not in landing.text

    interview_start = client.post("/begin", follow_redirects=False)
    assert interview_start.headers["location"] == "/interview"
    assert session.SESSION_COOKIE in interview_start.headers["set-cookie"]
    interview = client.get("/interview")
    assert "Aufnahme starten" in interview.text
    assert "Stattdessen schreiben" in interview.text
    # Der Leitfaden steht vor dem Feld und ist keine Auswahl: keine
    # Kästchen, keine Pflichtangaben — nur Orientierung beim Erzählen.
    assert "Was uns hilft, Ihren Betrieb wirklich zu verstehen" in interview.text
    assert 'type="checkbox"' not in interview.text
    assert 'type="radio"' not in interview.text
    assert "contenteditable" not in interview.text
    assert 'name="free_description"' in interview.text
    assert "/sessions/" not in interview.text

    script = client.get("/static/app.js").text
    assert "window.SpeechRecognition || window.webkitSpeechRecognition" in script
    assert 'recognition.lang = "de-DE"' in script
    assert "Ihr Browser unterstützt die Spracheingabe" in script
    for state in ("recording", "processing", "done", "error"):
        assert state in script

    styles = client.get("/static/styles.css").text
    # Die eingefrorene Palette (28.08.) ist die eine Quelle. `--ink` zeigt
    # nur noch darauf, damit die alten Regeln sich von selbst umfärben.
    assert "--tinte: #18332c" in styles
    assert "--ink: var(--tinte)" in styles
    assert "@media (max-width: 42.99rem)" in styles
    assert "min-height: 3.35rem" in styles
    assert "overflow-x: hidden" in styles
    assert "table" not in styles


def test_complete_public_journey(
    client: TestClient,
    database_session: Session,
) -> None:
    """Der ganze Weg des Kunden: erzählen, warten, Ergebnis.

    Drei Stationen statt sieben. Geprüft wird, was der Kunde sieht — und dass
    keine Sitzungsnummer und kein interner Begriff nach aussen dringt.
    """

    client.post("/begin", follow_redirects=False)
    erzaehlung = (
        "Kunden rufen an oder schreiben. Ich notiere Aufträge auf Zetteln und muss "
        "bei Rückfragen oft suchen, wo der Auftrag liegt und wie weit er ist."
    )

    gespeichert = client.post(
        "/interview",
        data={"free_description": erzaehlung},
        follow_redirects=False,
    )
    assert gespeichert.headers["location"] == "/processing"

    warteschirm = client.get("/processing")
    assert "Ihre Auswertung entsteht gerade." in warteschirm.text
    assert "Ihre Beschreibung ist weiterhin vorhanden" in warteschirm.text
    assert "data-retry-analysis" in warteschirm.text
    # Abbrechen und "Erzählung bearbeiten" müssen auf eine Seite führen, die
    # es noch gibt - sonst läuft der Ausstieg ins Leere.
    assert "/process-options" not in warteschirm.text
    assert "/saved" not in warteschirm.text
    assert "/interview" in warteschirm.text

    erster_aufruf = client.post("/analyze")
    assert erster_aufruf.status_code == 200, erster_aufruf.text
    assert erster_aufruf.json()["redirect_url"] == "/verstanden"

    verstanden = client.get("/verstanden")
    assert "Das habe ich verstanden" in verstanden.text
    assert "/sessions/" not in verstanden.text

    client.post("/verstanden", data={"weiter": "ja"}, follow_redirects=False)
    ausgewertet = client.post("/analyze")
    assert ausgewertet.status_code == 200, ausgewertet.text
    assert ausgewertet.json()["redirect_url"] == "/results"

    ergebnis = client.get("/results")
    for text in (
        "AI Start Map · Auswertung",
        "So könnte Ihre Lösung konkret aussehen",
        "Das würden wir für Sie umsetzen",
        "Genau so möchte ich arbeiten",
    ):
        assert text in ergebnis.text
    assert "/sessions/" not in ergebnis.text
    assert "chunk" not in ergebnis.text.casefold()

    # Die Adressen des alten Wegs gibt es nicht mehr - weder die Seite noch
    # ein Verweis darauf im ausgelieferten Text.
    for weg in ("/saved", "/process-options", "/follow-ups", "/vorschau/ergebnis"):
        assert client.get(weg, follow_redirects=False).status_code == 404
        assert weg not in ergebnis.text

    # Das Ergebnis bleibt stehen - es gibt keinen Weg mehr, es zu verwerfen.
    session_id = int(
        client.cookies.get("session_id") or 0
    ) or database_session.scalar(__import__("sqlalchemy").select(
        __import__("app.models", fromlist=["AnalysisSession"]).AnalysisSession.session_id
    ))
    assert repository.get_result(database_session, session_id) is not None


def test_the_two_ui_decisions_still_hold() -> None:
    """Spracheingabe und Druckansicht sind Entscheidungen, keine Zufälle.

    Sie standen früher in einem Flussdokument. Ein Dokument veraltet, ohne
    dass es jemand merkt — die Vorlagen nicht. Geprüft wird deshalb dort,
    wo die Entscheidung tatsächlich umgesetzt ist.
    """

    root = Path(__file__).resolve().parents[1]
    interview = (root / "app/templates/interview_start.html").read_text(
        encoding="utf-8"
    )
    report = (root / "app/templates/report.html").read_text(encoding="utf-8")

    # Erzählen statt tippen: Start und Stopp gehören zusammen.
    assert "data-voice-start" in interview
    assert "data-voice-stop" in interview
    # Gedruckt wird über den Browser, deshalb ein Druck-Stylesheet.
    assert '@media print' in report
    # Von selbst druckt die Seite nur auf dem Weg vom Knopf. Wer die
    # Adresse ohne `?drucken=1` aufruft, will lesen und nicht drucken —
    # `window.print()` steht deshalb hinter der Bedingung und nicht frei
    # im Dokument.
    assert 'window.print()' in report
    assert '{% if sofort_drucken %}' in report
    vor_der_bedingung = report.split('{% if sofort_drucken %}')[0]
    assert 'window.print()' not in vor_der_bedingung
