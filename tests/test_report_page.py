"""Die vollständige Auswertung zum Ausdrucken.

Die Ergebnisseite zeigt vier von elf Abschnitten. Was hier abgesichert wird,
ist, dass die anderen sieben im Ausdruck wirklich ankommen — sonst wäre die
Kürzung der Seite ein Verlust statt einer Verlagerung.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import walk_to_the_result

ERZAEHLT = "Wir sind zu dritt und suchen ständig Unterlagen zusammen."


def test_the_report_carries_all_eleven_sections(client: TestClient) -> None:
    """Alles, was von der Seite gewandert ist, steht im Ausdruck."""

    walk_to_the_result(client, ERZAEHLT)

    bericht = client.get("/report")

    assert bericht.status_code == 200
    for ueberschrift in (
        "Warum diese Lösung zu Ihnen passt",
        "So arbeitet das System zusammen",
        "Derselbe Vorgang, heute und künftig",
        "Aus diesen Modulen besteht Ihre Lösung",
        "Was das System übernimmt",
        "Was dadurch wegfällt und wofür Zeit entsteht",
        "Welche Ihrer Systeme verbunden würden",
        "So wäre die Technik dahinter ungefähr aufgebaut",
        "Was daraus gebaut werden kann",
        "So könnte Ihr Alltag aussehen",
        "Kurzfassung",
    ):
        assert ueberschrift in bericht.text, ueberschrift


def test_the_report_reads_the_stored_result(client: TestClient) -> None:
    """Gelesen wird dasselbe Ergebnis wie auf der Seite, nichts Neues."""

    walk_to_the_result(client, ERZAEHLT)

    seite = client.get("/results").text
    bericht = client.get("/report").text

    # Der Engpass-Satz steht auf beiden und stammt aus derselben Quelle.
    assert "AI Start Map · Vollständige Auswertung" in bericht
    # Die Überschrift taugt nicht als Anker: Auf der Tafel steht dort
    # eine feste Zeile, kein Kundenwort. Der Engpass-Satz ist beides —
    # Kundenwort, und er steht auf beiden Seiten.
    engpass = seite.split('class="befund">')[1].split("</p>")[0].strip()
    assert engpass
    assert engpass in bericht


def test_the_print_hint_is_hidden_when_printing(client: TestClient) -> None:
    """Der Hinweis „Strg+P" gehört auf den Bildschirm, nicht ins Papier."""

    walk_to_the_result(client, ERZAEHLT)

    bericht = client.get("/report").text

    assert "Strg+P" in bericht
    assert "noprint" in bericht
    assert ".noprint { display: none; }" in bericht


def test_views_are_not_torn_across_pages(client: TestClient) -> None:
    """Eine halbe Ansicht über zwei Seiten wäre unlesbar."""

    walk_to_the_result(client, ERZAEHLT)

    bericht = client.get("/report").text

    assert "break-inside: avoid" in bericht
    assert "section { break-before: page; }" in bericht


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

    assert "Vollständige Auswertung als PDF" in seite
    assert "/report" in seite


def test_the_order_is_shown_on_the_page(client: TestClient) -> None:
    """Drei Zeilen unter den Modulen: womit angefangen wird und wie es weitergeht."""

    walk_to_the_result(client, ERZAEHLT)

    seite = client.get("/results").text

    # Früher ein eigener Abschnitt unter den Modulen; auf der Tafel
    # steht die Reihenfolge an der Karte selbst.
    for beschriftung in ("Jetzt", "Darauf baut auf", "Wo das hinführt"):
        assert beschriftung in seite
    # Eigene Klassen: `.step` gehört den nummerierten Umsetzungsschritten.
    assert 'class="stufe">' in seite



def test_the_order_is_also_in_the_report(client: TestClient) -> None:
    """Was auf der Seite steht, steht auch im Ausdruck."""

    walk_to_the_result(client, ERZAEHLT)

    bericht = client.get("/report").text

    assert "Womit wir anfangen" in bericht
    assert "Wo das hinführt" in bericht


def test_the_page_holds_without_an_order(client: TestClient, monkeypatch) -> None:
    """Ein älteres Ergebnis ohne Reihenfolge zeigt die Seite trotzdem.

    Der hinterlegte Beispiellauf ist genau so einer — er ist die
    Rückfallebene für die Vorführung und darf an einem neuen Feld nicht
    zerbrechen.
    """

    antwort = client.get("/beispiel/hausverwaltung")

    assert antwort.status_code == 200
    assert "Womit wir anfangen" not in antwort.text
    assert "So könnte das bei Ihnen aussehen" in antwort.text
def test_the_pdf_button_opens_the_print_dialog(client: TestClient) -> None:
    """Der Knopf führt zu einer Seite, die von selbst zu drucken beginnt.

    Vorher lag der Weg beim Kunden: Er musste die Druckansicht sehen und
    von allein an Strg+P denken. Der Knopf verspricht ein PDF — also muss
    der Dialog kommen, ohne dass jemand nachhilft.
    """

    walk_to_the_result(client, ERZAEHLT)

    seite = client.get("/results").text
    assert '/report?drucken=1' in seite

    druckansicht = client.get("/report?drucken=1")

    assert druckansicht.status_code == 200
    assert "window.print()" in druckansicht.text


def test_the_report_without_the_flag_stays_a_page_to_read(
    client: TestClient,
) -> None:
    """Dieselbe Adresse ohne `?drucken=1` druckt nicht von selbst.

    Wer den Link weitergibt oder ihn aus dem Verlauf wieder aufruft, will
    lesen. Ein Druckdialog vor der Nase wäre dort ein Fehler.
    """

    walk_to_the_result(client, ERZAEHLT)

    druckansicht = client.get("/report")

    assert druckansicht.status_code == 200
    assert "window.print()" not in druckansicht.text


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
    assert "Gespr%C3%A4ch%20zu%20meiner%20Auswertung" in seite
    # Kaufmännisches Und als `&amp;`: So gehört es im HTML, der Browser
    # macht daraus wieder ein einfaches Zeichen.
    assert "&amp;body=" in seite
    # Kein leerer Knopf mehr: `mailto:` allein war der alte Zustand.
    assert 'href="mailto:"' not in seite


def test_the_conversation_button_holds_without_a_configured_address(
    client: TestClient, monkeypatch
) -> None:
    """Ohne hinterlegte Adresse bleibt der Knopf brauchbar.

    Erfunden wird nichts — eine ausgedachte Adresse schickte die Anfragen
    des Kunden ins Leere. Das Mailprogramm öffnet sich trotzdem, mit
    Betreff und Text und leerem Empfängerfeld.
    """

    monkeypatch.delenv("KONTAKT_ADRESSE", raising=False)
    walk_to_the_result(client, ERZAEHLT)

    seite = client.get("/results").text

    assert 'href="mailto:?subject=' in seite
    # Kaufmännisches Und als `&amp;`: So gehört es im HTML, der Browser
    # macht daraus wieder ein einfaches Zeichen.
    assert "&amp;body=" in seite
