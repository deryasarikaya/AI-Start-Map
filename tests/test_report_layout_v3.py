import re
import subprocess
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.schemas import customer_plain_text
from tests.conftest import spec_view


ROOT = Path(__file__).resolve().parents[1]


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
        analysis_date="12.08.2026",
    )


def test_report_contains_exactly_the_two_approved_pages() -> None:
    html = _render(spec_view(grenzen="Ein nicht dokumentiertes Gespräch bleibt weg."))
    for text in (
        "Diagnose und noch keine fertige Einrichtung",
        "Das ist der Engpass",
        "WO ARBEIT WEGFÄLLT",
        "SO WÜRDE DEINE LÖSUNG AUSSEHEN",
        "Nach der Einrichtung",
        "BEISPIEL",
        "Das behältst du, das kommt dazu",
        "Was ich dafür einrichte",
        "Das bleibt bei dir",
        "Eine Grenze",
        "Möchtest du das umsetzen?",
    ):
        assert text in html, text
    assert html.count('class="report-page ') == 2
    assert "report-page-three" not in html
    assert "Autonomiestufe" not in html
    assert "/sessions/" not in html
    assert "session_id" not in html


def test_report_keeps_two_pages_without_optional_sections() -> None:
    """Auch ohne Beispiel und ohne Grenze bleiben es genau zwei Seiten."""

    html = _render(spec_view(beispiel=None, grenzen=""))
    assert html.count('class="report-page ') == 2
    assert "BEISPIEL" not in html
    assert "Eine Grenze" not in html


def test_print_hint_stays_out_of_the_printed_document() -> None:
    """Der Hinweis auf die Kopfzeilen gehoert auf die Seite, nicht ins PDF."""

    html = _render(spec_view())
    assert "Kopf- und Fußzeilen" in html
    assert "print-toolbar" in html
    css = (ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8")
    assert ".print-toolbar" in css


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
    html = _render(spec_view(grenzen="Ein nicht dokumentiertes Gespräch bleibt weg."))
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
