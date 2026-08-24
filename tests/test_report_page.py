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
    for zeile in seite.split("<h1>")[1].split("</h1>")[0].strip().split("\n"):
        assert zeile.strip() in bericht


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

    assert "Womit wir anfangen" in seite
    for beschriftung in ("Jetzt", "Darauf baut auf", "Wo das hinführt"):
        assert beschriftung in seite
    # Eigene Klassen: `.step` gehört den nummerierten Umsetzungsschritten.
    assert 'class="folge"' in seite
    assert seite.count('class="stufe"') == 3


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
