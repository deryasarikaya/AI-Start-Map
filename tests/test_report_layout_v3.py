import re
import subprocess
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.schemas import customer_plain_text


ROOT = Path(__file__).resolve().parents[1]


def _result(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "is_non_ai": False,
        "short_reason": "Fotos, Notizen und Bons liegen heute an verschiedenen Stellen. Beim Rechnungsschreiben musst du alles wieder zusammensuchen.",
        "primary_recommendation": "Mobile Einsatzdokumentation aus Sprache, Fotos und Bon",
        "promise": "Nach jedem Einsatz hast du eine fertige Notiz mit Zeit, Material und Fotos.",
        "future_process": [
            "Nach dem Einsatz sendest du Sprache, Fotos und Bon.",
            "Die KI liest T\u00e4tigkeit, Zeit und Material heraus.",
            "Fehlende oder unsichere Angaben werden markiert.",
            "Eine Einsatznotiz entsteht als Entwurf.",
            "Du pr\u00fcfst und best\u00e4tigst sie.",
            "Danach kann sie als Grundlage f\u00fcr die Rechnung dienen.",
        ],
        "sample_heading": "Beispiel \u2014 so k\u00f6nnte deine Einsatznotiz aussehen",
        "sample_output": {
            "fields": [
                {"label": "F\u00fcr wen", "value": "Hausverwaltung Nord \u00b7 Lindenstra\u00dfe 12"},
                {"label": "Was gemacht wurde", "value": "Waschbecken-Dichtung getauscht"},
                {"label": "Wie lange", "value": "45 Minuten"},
                {"label": "Material", "value": "Dichtungssatz, 12,40 \u20ac"},
                {"label": "Besonderheiten", "value": "Zugang nur \u00fcber die Hausverwaltung"},
                {"label": "Noch zu kl\u00e4ren", "value": "T\u00fcr nachstellen \u2013 abrechnen?"},
                {"label": "Dabei", "value": "2 Fotos, 1 Bon, deine Sprachnachricht"},
            ],
            "preview_notice": "Beispielangaben zur Veranschaulichung \u2013 hier stehen sp\u00e4ter deine tats\u00e4chlichen Angaben.",
        },
        "required_prerequisites": ["Ein fester Weg zum Senden der Angaben"],
        "open_questions": ["Wie erkennst du heute, zu welchem Auftrag ein Bon geh\u00f6rt?"],
        "first_step_text": "Probier es bei den n\u00e4chsten f\u00fcnf Eins\u00e4tzen aus.",
        "first_step_follow_up": "Erst danach lohnt sich der n\u00e4chste Schritt.",
        "later_stage": "Sp\u00e4ter kann ein Rechnungsentwurf vorbereitet werden.",
        "contact_recommendation": "Mobile Einsatzdokumentation aus Sprache, Fotos und Bon",
    }
    result.update(overrides)
    return result


def _render(result: dict[str, object]) -> str:
    environment = Environment(
        loader=FileSystemLoader(ROOT / "app" / "templates"),
        autoescape=select_autoescape(("html",)),
    )
    environment.globals["url_for"] = lambda name, **_kwargs: f"/{name}"
    environment.filters["customer_text"] = customer_plain_text
    return environment.get_template("report.html").render(
        result=result,
        process={"process_name": "Einsatz bis Rechnung"},
        analysis_date="07.08.2026",
    )


def test_report_contains_exactly_the_two_approved_pages() -> None:
    html = _render(_result())
    for text in (
        "Diagnose und noch keine fertige Einrichtung",
        "DAS IST DER ENGPASS",
        "DAS SCHLAGE ICH DIR VOR",
        "So w\u00fcrde es k\u00fcnftig laufen",
        "BEISPIELAUSGABE",
        "Nichts geht ohne dich raus",
        "Das entscheidest weiterhin du",
        "Was vorher da sein muss",
        "Diese Fragen sind noch zu kl\u00e4ren",
        "So klein f\u00e4ngst du an",
        "Was sp\u00e4ter m\u00f6glich wird",
        "M\u00f6chtest du das umsetzen?",
    ):
        assert text in html
    assert html.count('class="report-page ') == 2
    assert "report-page-three" not in html
    assert "Autonomiestufe" not in html
    assert "/sessions/" not in html
    assert "session_id" not in html


def test_non_ai_report_uses_plain_language_without_internal_level() -> None:
    html = _render(
        _result(
            is_non_ai=True,
            primary_recommendation="Vorhandene Kalenderfunktion nutzen",
            promise="F\u00fcr diesen Schritt ist keine KI notwendig.",
            contact_recommendation="die vorhandene Kalenderfunktion passend einstellen",
        )
    )
    assert "keine KI notwendig" in html
    assert "Autonomiestufe" not in html
    assert "A0" not in html


def test_optional_secondary_content_never_creates_a_third_page() -> None:
    html = _render(
        _result(
            secondary_opportunities=[
                {"title": "Sp\u00e4tere M\u00f6glichkeit", "description": "Erst nach dem sicheren Einstieg pr\u00fcfen."}
            ]
        )
    )
    assert html.count('class="report-page ') == 2
    assert "OPTIONALE WEITERE M\u00d6GLICHKEITEN" not in html


def test_print_css_suppresses_urls_and_forces_two_compact_pages() -> None:
    css = (ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8")
    assert "@page { size: A4; margin: 9mm 11mm; }" in css
    assert "height: 277mm" in css
    assert "a[href]::after { content: none !important; }" in css


def test_housekeeper_pdf_has_exactly_two_pages(tmp_path: Path) -> None:
    chrome = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    if not chrome.exists():
        pytest.skip("Chrome is required for the local print regression.")
    css = (ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8")
    html = _render(_result())
    html = re.sub(
        r'<link rel="stylesheet"[^>]+>',
        f"<style>{css}</style>",
        html,
        count=1,
    )
    html_path = tmp_path / "housekeeper-report.html"
    pdf_path = tmp_path / "housekeeper-report.pdf"
    html_path.write_text(html, encoding="utf-8")
    completed = subprocess.run(
        [
            str(chrome),
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--user-data-dir={tmp_path / 'chrome-profile'}",
            f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ],
        capture_output=True,
        check=False,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr.decode(errors="replace")
    pdf_bytes = pdf_path.read_bytes()
    assert len(re.findall(rb"/Type\s*/Page\b", pdf_bytes)) == 2
    assert b"127.0.0.1" not in pdf_bytes
