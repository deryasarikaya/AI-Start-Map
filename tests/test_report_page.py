"""Die vollständige Auswertung zum Ausdrucken.

Die Ergebnisseite zeigt vier von elf Abschnitten. Was hier abgesichert wird,
ist, dass die anderen sieben im Ausdruck wirklich ankommen — sonst wäre die
Kürzung der Seite ein Verlust statt einer Verlagerung.
"""

from __future__ import annotations

import io

import pytest

from pathlib import Path

from fastapi.testclient import TestClient

from app import bericht_pdf, routes
from tests.conftest import walk_to_the_result

ERZAEHLT = "Wir sind zu dritt und suchen ständig Unterlagen zusammen."


def test_the_report_opens_the_solution_space_but_does_not_plan_it(client: TestClient) -> None:
    """**Der Bericht stellt fest. Die Route entscheidet das Gespräch.**

    Vorher trug er hinten einen Anhang: Kurzfassung, Reihenfolge,
    Begründung, Hebel, Wert, Systeme, Architektur, Umsetzungsschritte.
    Fünf zusätzliche Seiten, die eine Umsetzung durchplanten, die noch
    niemand besprochen hatte — und damit dem Gespräch den Anlass nahmen.

    Was bleibt, ist die Feststellung und der geöffnete Lösungsraum. Was
    geht, ist die Planung. Der Test hält beide Seiten fest, denn ohne die
    zweite wächst der Anhang wieder nach.
    """

    walk_to_the_result(client, ERZAEHLT)

    bericht = client.get("/report")

    assert bericht.status_code == 200
    # Der Befund und der Lösungsraum — das gehört hinein.
    for ueberschrift in (
        "Ihre AI Start Map",
        "Ihre Aussagen tragen die Entscheidung",
        "Ein verlässlicher Ablauf statt verstreuter Einzelinformationen",
        "Das kann die Lösung übernehmen. Das entscheidet weiterhin Ihr Team.",
    ):
        assert ueberschrift in bericht.text, ueberschrift

    # Die Planung — das gehört ins Gespräch, nicht auf Papier.
    for anhang in (
        "Anhang",
        "Kurzfassung",
        "Warum diese Lösung zu Ihnen passt",
        "Welche Ihrer Systeme verbunden würden",
        "So wäre die Technik dahinter ungefähr aufgebaut",
        "Was dadurch wegfällt und wofür Zeit entsteht",
    ):
        assert anhang not in bericht.text, anhang

def test_the_report_reads_the_stored_result(client: TestClient) -> None:
    """Gelesen wird dasselbe Ergebnis wie auf der Seite, nichts Neues."""

    walk_to_the_result(client, ERZAEHLT)

    seite = client.get("/results").text
    bericht = client.get("/report").text

    # Der Engpass-Satz steht auf beiden und stammt aus derselben Quelle.
    # Der Bericht erzählt in acht Seiten, jede mit einem eigenen Umbruch.
    for ueberschrift in (
        "AI Start Map · Ihre Auswertung",
        "Ihre AI Start Map",
        "Ihre Aussagen tragen die Entscheidung",
        "Ein verlässlicher Ablauf statt verstreuter Einzelinformationen",
        "Startpunkt gemeinsam prüfen",
    ):
        assert ueberschrift in bericht, ueberschrift
    # Der Anhang ist weg: Der Bericht stellt fest, das Gespräch plant.
    assert "Anhang" not in bericht
    assert "results_v1.css" in bericht
    # Die Karte steht ohne Skript vollständig im Dokument.
    assert "Betriebs-Lösungsraum" in bericht
    # Die Überschrift taugt nicht als Anker: Auf der Tafel steht dort
    # eine feste Zeile, kein Kundenwort. Der Engpass-Satz ist beides —
    # Kundenwort, und er steht auf beiden Seiten.
    #
    # Aus dem Bericht gelesen: Dort trägt der Satz eine eigene Klasse.
    # Ein Anker auf „das erste h1" wäre falsch — das ist seit dem
    # Deckblatt der Titel des Berichts, nicht sein Befund.
    engpass = bericht.split("<h1>")[1].split("</h1>")[0].strip()
    assert engpass
    assert engpass in seite


def test_the_document_is_measured_here_not_in_a_print_dialog(client: TestClient) -> None:
    """**Das Format steht in der Vorlage, nicht in fremden Einstellungen.**

    Vorher rief die Seite `window.print()` auf und bat um „Strg+P". Was
    dabei herauskam, hing vom Dialog des Kunden ab: Kopfzeilen mit der
    `localhost`-Adresse, ein Skalierungsfaktor, abgeschaltete
    Hintergrundfarben. Drei Kunden bekamen drei Dokumente — und dieses
    Dokument ist das, was er an uns zurückschickt.

    Jetzt entsteht es auf dem Server, und A4 samt Rändern steht hier.
    """

    walk_to_the_result(client, ERZAEHLT)

    bericht = client.get("/report").text

    assert "@page { size: A4; margin: 14mm; }" in bericht
    # Niemand wird mehr um einen Tastendruck gebeten.
    assert "window.print()" not in bericht
    assert "Strg+P" not in bericht

def test_views_are_not_torn_across_pages(client: TestClient) -> None:
    """Eine halbe Ansicht über zwei Seiten wäre unlesbar."""

    walk_to_the_result(client, ERZAEHLT)

    bericht = client.get("/report").text

    assert "break-inside: avoid" in bericht
    # **Aber kein Umbruch pro Abschnitt.** Der zwang elf Abschnitte auf elf
    # Seiten, die meisten zu zwei Dritteln leer. Zusammenhalten ist die
    # Regel, die gebraucht wird; eine neue Seite pro Überschrift nicht.
    assert "section { break-before: page; }" not in bericht


def test_without_a_result_there_is_no_report(client: TestClient) -> None:
    """Wer noch kein Ergebnis hat, wird zurückgeschickt statt bedient."""

    client.post("/begin", follow_redirects=False)
    client.post("/interview", data={"free_description": ERZAEHLT}, follow_redirects=False)

    antwort = client.get("/report", follow_redirects=False)

    assert antwort.status_code == 303
    assert antwort.headers["location"] == "/processing"


def test_the_result_page_links_to_the_report(client: TestClient) -> None:
    """Die Schaltfläche auf der Ergebnisseite führt nicht mehr ins Leere."""

    walk_to_the_result(client, ERZAEHLT)

    seite = client.get("/results").text

    assert "Auswertung als PDF" in seite
    # „Enthält mehr Details als diese Zusammenfassung" ist gestrichen:
    # Seit das PDF dieselbe Auswertung mit Deckblatt ist, war der Satz ein
    # Versprechen, das die Datei nicht einlöst.
    assert "mehr Details als diese Zusammenfassung" not in seite
    assert "/report" in seite


def test_the_module_card_leads_with_the_benefit(client: TestClient) -> None:
    """Oben steht, was er davon hat — der technische Name darunter.

    Andersherum las sich die Reihe als Softwarekatalog: erst ein Name, den
    er nicht kennt, und ganz unten klein, warum ihn das interessieren
    sollte. Die Reihenfolge der Bauphasen ist von der Karte verschwunden;
    womit angefangen wird, gehört ins Gespräch und in den Ausdruck, nicht
    auf die Seite, auf der er noch entscheidet, ob er überhaupt will.
    """

    walk_to_the_result(client, ERZAEHLT)

    seite = client.get("/results").text

    for bauphase in ("Darauf baut auf", "Wo das hinführt"):
        assert bauphase not in seite, bauphase

    # Trägt ein Modul einen Nutzen, führt er die Karte und der Name rückt
    # darunter; fehlt er, führt der Name. Erfunden wird nichts — deshalb
    # steht die Reihenfolge in der Vorlage und wird dort geprüft.
    vorlage = (
        Path(__file__).resolve().parents[1] / "app/templates/ergebnis.html"
    ).read_text(encoding="utf-8")
    entlastung = vorlage.index("<h3>{{ modul.nutzen }}</h3>")
    produkt = vorlage.index('<p class="bausteinname">')
    erklaerung = vorlage.index('<p class="bausteintext">')
    assert entlastung < produkt < erklaerung



def test_the_report_leaves_the_order_to_the_conversation(client: TestClient) -> None:
    """Kein Fahrplan auf Papier.

    „Womit wir anfangen" und „Wo das hinführt" waren eine Reihenfolge,
    die der Bericht allein festlegte. Welche Möglichkeit für diesen
    Betrieb zuerst Sinn ergibt, entscheidet sich im Gespräch — und dazu
    lädt der Schluss ausdrücklich ein.
    """

    walk_to_the_result(client, ERZAEHLT)

    bericht = client.get("/report").text

    assert "Womit wir anfangen" not in bericht
    assert "Wo das hinführt" not in bericht
    assert "Startpunkt gemeinsam prüfen" in bericht

def test_the_page_holds_without_an_order(client: TestClient, monkeypatch) -> None:
    """Ein älteres Ergebnis ohne Reihenfolge zeigt die Seite trotzdem.

    Der hinterlegte Beispiellauf ist genau so einer — er ist die
    Rückfallebene für die Vorführung und darf an einem neuen Feld nicht
    zerbrechen.
    """

    antwort = client.get("/beispiel/hausverwaltung")

    assert antwort.status_code == 200
    assert "Womit wir anfangen" not in antwort.text
    assert "Ihre AI Start Map" in antwort.text
def test_the_pdf_button_returns_a_real_document(client: TestClient) -> None:
    """**Der Knopf verspricht ein PDF — also kommt eines zurück.**

    Vorher führte er auf eine Seite, die den Druckdialog öffnete. Der
    Kunde bekam damit kein Dokument, sondern eine Aufgabe.

    Steht der Browser für die Erzeugung nicht zur Verfügung, läuft
    niemand ins Leere: Dann führt der Weg zurück auf die Seite mit
    denselben Inhalten. Auch das wird hier geprüft.
    """

    walk_to_the_result(client, ERZAEHLT)

    seite = client.get("/results").text
    assert "/report.pdf" in seite
    assert "?drucken=1" not in seite

    antwort = client.get("/report.pdf", follow_redirects=False)

    if antwort.status_code in (302, 303, 307):
        # Kein Browser zur Hand — dann aber auf die lesbare Seite.
        assert "/report" in antwort.headers["location"]
        return

    assert antwort.status_code == 200
    assert antwort.headers["content-type"].startswith("application/pdf")
    assert antwort.content.startswith(b"%PDF")
    assert "AI-Start-Map-Auswertung" in antwort.headers["content-disposition"]


def test_the_document_stays_within_eight_pages(client: TestClient) -> None:
    """**Acht Seiten, nicht dreizehn.**

    Mit dem Anhang war der Bericht dreizehn Seiten lang, und die letzten
    fünf las niemand. Acht Seiten sind das, was jemand in einer Sitzung
    durchsieht und weiterleitet.

    Gezählt wird am fertigen Dokument, nicht an den Abschnitten der
    Vorlage: Ob ein Abschnitt auf ein Blatt passt, entscheidet der Umbruch
    und nicht die Absicht.
    """

    pypdf = pytest.importorskip("pypdf")

    walk_to_the_result(client, ERZAEHLT)
    antwort = client.get("/report.pdf", follow_redirects=False)
    if antwort.status_code != 200:
        pytest.skip("kein Browser fuer die PDF-Erzeugung vorhanden")

    seiten = len(pypdf.PdfReader(io.BytesIO(antwort.content)).pages)

    assert 0 < seiten <= 8, f"{seiten} Seiten"

def test_the_page_to_read_survives_a_missing_browser(
    client: TestClient, monkeypatch
) -> None:
    """**Fällt die Erzeugung aus, läuft niemand ins Leere.**

    Vorher prüfte hier ein Test, dass `/report` ohne `?drucken=1` nicht von
    selbst druckt. Den Schalter gibt es nicht mehr — aber die Seite gibt es,
    und sie ist jetzt der Rückfall, wenn kein Browser für das PDF da ist.

    Dabei darf die Sitzungsnummer nicht sichtbar werden. Sie stand es
    einmal: Der Rückfall baute die Adresse mit `url_for` und damit
    vollständig samt Rechnernamen, und `publicize_redirect` erkennt nur die
    relative Form. Ab `/begin` soll sie in keiner Adresse mehr auftauchen.
    """

    async def kein_browser(html: str) -> bytes:
        raise bericht_pdf.PdfNichtVerfuegbar("kein Browser vorhanden")

    monkeypatch.setattr(routes.bericht_pdf, "aus_html", kein_browser)
    walk_to_the_result(client, ERZAEHLT)

    ausweich = client.get("/report.pdf", follow_redirects=False)

    assert ausweich.status_code in (302, 303, 307)
    ziel = ausweich.headers["location"]
    assert "/sessions/" not in ziel, f"Sitzungsnummer in der Adresse: {ziel}"
    assert ziel.endswith("/report")
    # Und dort steht die vollstaendige Auswertung zum Lesen.
    seite = client.get("/report")
    assert seite.status_code == 200
    assert "window.print()" not in seite.text

def test_the_conversation_button_carries_subject_and_text(
    client: TestClient, monkeypatch
) -> None:
    """Der Gesprächsknopf öffnet eine vorbereitete Mail, kein leeres Fenster.

    Empfänger, Betreff und ein vorgeschriebener Text stehen in der Adresse
    und sind ordentlich kodiert — ein rohes Leerzeichen oder Umlaut darin
    bricht den Link in manchen Mailprogrammen.
    """

    monkeypatch.setenv("KONTAKT_ADRESSE", "hallo@example.org")
    walk_to_the_result(client, ERZAEHLT)

    seite = client.get("/results").text

    assert 'href="mailto:hallo@example.org?subject=' in seite
    assert "AI%20Start%20Map" in seite
    assert "Interesse%20an%20meiner%20Auswertung" in seite
    # Die Nachricht bittet um die PDF: Ein `mailto:` kann nichts anhängen,
    # und ohne diese Bitte kommt eine Anfrage an, zu der niemand die
    # Auswertung findet.
    assert "h%C3%A4nge%20die%20PDF" in seite
    # Kaufmännisches Und als `&amp;`: So gehört es im HTML, der Browser
    # macht daraus wieder ein einfaches Zeichen.
    assert "&amp;body=" in seite
    # Kein leerer Knopf mehr: `mailto:` allein war der alte Zustand.
    assert 'href="mailto:"' not in seite


def test_without_an_address_there_is_no_button(
    client: TestClient, monkeypatch
) -> None:
    """**Ohne hinterlegte Adresse gibt es keinen Knopf.**

    Vorher öffnete sich das Mailprogramm trotzdem — mit Betreff, Text und
    leerem Empfängerfeld. Das ist auf dem wichtigsten Knopf der Seite der
    teuerste denkbare Fehler, weil ihn niemand meldet: Der Kunde schreibt,
    schickt ab, und die Anfrage landet nirgends.

    Ein fehlender Knopf fällt auf. Ein Knopf ins Leere nicht.
    """

    monkeypatch.delenv("KONTAKT_ADRESSE", raising=False)
    walk_to_the_result(client, ERZAEHLT)

    seite = client.get("/results").text

    assert "mailto:" not in seite
    assert "Ja, ich möchte das umsetzen" not in seite
    assert "Die Kontaktadresse ist auf diesem Server nicht hinterlegt." in seite
