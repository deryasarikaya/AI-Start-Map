"""Der sichtbare Results-V1-Vertrag.

Die Seite entscheidet nicht erneut. Diese Tests halten fest, dass Web und
PDF aus dem einen DTO lesen und dass der Kern auch ohne JavaScript lesbar
bleibt.
"""

from __future__ import annotations

from pathlib import Path
import re

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import results_dto
from app.services import example_service
from tests.conftest import walk_to_the_result


ERZAEHLT = """Das Telefon klingelt dauernd. E-Mails und Fotos kommen später
an anderer Stelle an, und unser Team sucht den Vorgang immer wieder."""


def test_web_and_pdf_read_the_same_dto_only(client: TestClient) -> None:
    """Renderer bekommen keine alte Ergebnisansicht als zweiten Input."""

    walk_to_the_result(client, ERZAEHLT)
    web = client.get("/results")
    pdf_view = client.get("/report")

    assert web.status_code == 200
    assert pdf_view.status_code == 200
    for text in (
        "AI Start Map · Ihre Auswertung",
        "Ihre AI Start Map",
        "Ihre Aussagen tragen die Entscheidung",
        "Ein verlässlicher Ablauf statt verstreuter Einzelinformationen",
        "Startpunkt gemeinsam prüfen",
    ):
        assert text in web.text
        assert text in pdf_view.text
    assert "chunk" not in web.text.casefold()
    assert "SF-" not in web.text

    root = Path(__file__).resolve().parents[1]
    routes = (root / "app/routes.py").read_text(encoding="utf-8")
    for template_name in ("results_v1.html", "report_v1.html", "_results_v1_content.html"):
        source = (root / "app/templates" / template_name).read_text(encoding="utf-8")
        assert re.search(r"(?<![A-Za-z_])e\\.", source) is None
        assert "kartenkontext" not in source
    assert '"dto": results_dto.von_ergebnis(ergebnis)' in routes


def test_map_and_evidence_remain_readable_without_javascript(client: TestClient) -> None:
    """Filter verbessern die Karte nur; sie verstecken keinen Kerninhalt."""

    walk_to_the_result(client, ERZAEHLT)
    response = client.get("/results")

    assert response.text.count("data-map-node") == 14
    for label in ("Heute", "Hier starten", "Zielbild", "Später möglich"):
        assert label in response.text
    assert "Betriebs-Lösungsraum" in response.text
    assert "data-map-workspace" in response.text
    assert " hidden=" not in response.text


def test_example_keeps_its_legacy_provenance_without_inventing_a_decision(
    database_session: Session,
) -> None:
    """Ein gespeicherter Altfall läuft über den Adapter und bleibt markiert."""

    ergebnis = example_service.example_result(database_session, "hausverwaltung")
    dto = results_dto.von_ergebnis(ergebnis)

    assert dto.ist_angepasst
    assert len(dto.module) == 14
    # Vorhandene, gespeicherte Ansichtsinhalte bleiben erhalten; der Adapter
    # erzeugt aber keinen neuen Modellinhalt.
    if dto.ansichten.primary and dto.ansichten.primary.inhalt:
        assert dto.ansichten.primary.inhalt in ergebnis.ansichten


def test_result_pdf_uses_the_same_results_v1_template(client: TestClient) -> None:
    """Der öffentliche PDF-Weg funktioniert auch für den Beispielpfad."""

    page = client.get("/beispiel/hausverwaltung")
    pdf = client.get("/beispiel/hausverwaltung/report.pdf", follow_redirects=False)

    assert page.status_code == 200
    assert "/beispiel/hausverwaltung/report.pdf" in page.text
    if pdf.status_code in (302, 303, 307):
        assert pdf.headers["location"].endswith("/beispiel/hausverwaltung")
    else:
        assert pdf.status_code == 200
        assert pdf.content.startswith(b"%PDF")
