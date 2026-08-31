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
        "Kostenlose, individuelle Analyse für kleine Betriebe",
        "Finden Sie heraus, wo KI Ihnen wirklich Arbeit abnehmen kann.",
        "Beschreiben Sie einfach Ihren Arbeitsalltag.",
        "wo heute unnötiger Aufwand entsteht",
        "Und wie Ihre Abläufe künftig besser zusammenspielen könnten.",
        "Das sehen Sie, bevor Sie über den nächsten Schritt entscheiden",
        "Sie müssen Ihr Problem nicht in KI-Sprache erklären",
        "Nicht möglichst viele Ideen. Ein begründeter Start.",
        "Kostenlose Analyse starten",
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
    assert "Beschreibung analysieren" in interview.text
    assert "Danach sehen Sie zuerst, was AI Start Map verstanden hat." in interview.text
    # Der Leitfaden steht vor dem Feld und ist keine Auswahl: keine
    # Kästchen, keine Pflichtangaben — nur Orientierung beim Erzählen.
    assert "Damit wir Ihren Betrieb wirklich verstehen" in interview.text
    # Eingabe und Leitfaden stehen nebeneinander, nicht übereinander:
    # zwei breite Blöcke machten die Seite lang und trotz Fläche leer.
    assert 'class="erhebung-spalten"' in interview.text
    # **Nur ein Leitfaden.** Chips unter dem Textfeld waren eine zweite
    # Orientierung — erst sechs Themen, dann sechs Fragen, und aus der
    # freien Erzählung wird ein Fragebogen.
    assert 'aria-label="Gedankenstützen"' not in interview.text
    # Der Datenschutzhinweis ist raus — er unterbrach den Erzählfluss,
    # bevor er begann.
    assert "privacy-banner" not in interview.text
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
    # Die eine Palette ist die Quelle. `--ink` zeigt nur noch darauf, damit
    # die alten Regeln sich von selbst umfärben.
    #
    # Und der Grund ist **warm**: Pfirsich, nicht Weiss und nicht Grau. Eine
    # erste Fassung stand auf einem kühlen Off-White und nahm damit jeder
    # Seite ausser dem Ergebniskopf die Wärme.
    assert "--grund: #FFF8F0" in styles
    assert "--tinte: #173D35" in styles
    assert "--ink: var(--tinte)" in styles
    for token in (
        "--page-bg",
        "--page-bg-gradient",
        "--page-bg-position",
        "--page-bg-size",
        "--page-bg-repeat",
        "--page-bg-height",
        "--page-bg-glow",
        "--surface-elevated",
        "--surface-accent",
        "--radius-card",
        "--radius-control",
        "--shadow-card",
        "--content-width",
        "--motion-standard",
    ):
        assert token in styles
    # Der Results-Hintergrund ist die eine Quelle fuer den gesamten Funnel:
    # exakt dieselben Layer, dieselbe Geometrie und dieselbe Bewegung.
    assert "linear-gradient(180deg, #fbfbf8 0%, var(--page-bg) 100%)" in styles
    assert "radial-gradient(90% 130% at 88% -20%" in styles
    assert "rgb(63 167 163 / .12)" in styles
    assert "page-background-atem" in styles
    assert "grund-atem" not in styles
    assert 'class="page-backdrop"' in landing.text

    result_template = (
        Path(__file__).resolve().parents[1] / "app/templates/ergebnis.html"
    ).read_text(encoding="utf-8")
    example_result = client.get("/beispiel/hausverwaltung")
    tafel_styles = client.get("/static/tafel.css").text
    assert '{% include "_page_background.html" %}' in result_template
    assert example_result.status_code == 200
    assert example_result.text.count('class="page-backdrop"') == 1
    assert "tafel-atem" not in tafel_styles
    assert "radial-gradient(90% 130% at 88% -20%" not in tafel_styles
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
    assert "Das ist noch keine Empfehlung" in verstanden.text
    assert 'class="understanding-summary card card--elevated"' in verstanden.text
    assert "/sessions/" not in verstanden.text

    client.post("/verstanden", data={"weiter": "ja"}, follow_redirects=False)
    ausgewertet = client.post("/analyze")
    assert ausgewertet.status_code == 200, ausgewertet.text
    assert ausgewertet.json()["redirect_url"] == "/results"

    ergebnis = client.get("/results")
    for text in (
        "AI Start Map · Ihre Auswertung",
        "Hier würden wir anfangen",
        "Der Lösungsraum für Ihren Betrieb",
        "Startpunkt gemeinsam prüfen",
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
    # **Das Dokument entsteht auf dem Server, nicht im Druckdialog.**
    # Vorher rief die Vorlage `window.print()` auf, und was herauskam,
    # hing von den Einstellungen des Kunden ab — Kopfzeilen, Skalierung,
    # abgeschaltete Hintergrundfarben. Jetzt steht das Format hier.
    assert '@page { size: A4;' in report
    assert '@media print' in report
    assert 'window.print()' not in report
    # Die Stilvorlagen werden ins Dokument geschrieben, nicht verlinkt:
    # Der Renderer bekommt eine Zeichenkette und lädt nichts nach.
    assert "{{ stil('styles.css') }}" in report
    assert "{{ stil('tafel.css') }}" in report
