from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


ROOT = Path(__file__).resolve().parents[1]


def _result(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "short_reason": "Digitale Angaben liegen verteilt und werden manuell nachbearbeitet.",
        "bottleneck": {"cause": "Die Angaben werden nicht in einem Vorgang zusammengeführt."},
        "autonomy_level": "A2",
        "primary_recommendation": "Digitale Angaben in einem prüfbaren Entwurf zusammenführen",
        "promise": "Du erhältst ein konkretes, prüfbares Arbeitsergebnis.",
        "future_process": [
            "Du leitest vorhandene digitale Angaben weiter.",
            "Die KI erstellt einen strukturierten Entwurf.",
            "Feste Regeln markieren fehlende Pflichtangaben.",
            "Du prüfst und bestätigst das Ergebnis.",
        ],
        "user_action": "Du leitest die vorhandenen Angaben weiter.",
        "ai_task": "Die KI ordnet die Angaben in einen Entwurf.",
        "software_rule": "Pflichtfelder und Status werden nach festen Regeln geprüft.",
        "human_check": "Du prüfst Inhalt und Freigabe.",
        "sample_output": {
            "title": "Vorgangsübersicht",
            "fields": [{"label": "Status", "value": "noch offen"}],
            "open_items": ["Verantwortliche Person noch offen"],
            "attachments": [],
            "preview_notice": "Vorschau – die endgültigen Angaben prüfst du selbst.",
        },
        "smallest_usable_version": "Mit einem Entwurf für neue Vorgänge beginnen.",
        "implementation_path": ["Pflichtfelder festlegen.", "Neue Vorgänge prüfen."],
        "required_prerequisites": ["Ein eindeutiger Vorgangsanker"],
        "not_automated": ["Freigabe", "Verbindliche Entscheidung"],
        "open_details": ["Zielstatus noch offen"],
        "uncertainties": ["Das Volumen ist nicht angegeben."],
        "error_boundaries": ["Unklare Angaben bleiben offen."],
        "later_stage": "Später kann ein Folgeschritt vorbereitet werden.",
        "secondary_opportunities": [],
    }
    result.update(overrides)
    return result


def _render(result: dict[str, object]) -> str:
    environment = Environment(
        loader=FileSystemLoader(ROOT / "app" / "templates"),
        autoescape=select_autoescape(("html",)),
    )
    environment.globals["url_for"] = lambda name, **_kwargs: f"/{name}"
    return environment.get_template("report.html").render(
        result=result,
        process={"process_name": "Anfrage bis Freigabe"},
        analysis_date="06.08.2026",
    )


def test_report_contains_the_complete_customer_contract() -> None:
    html = _render(_result())
    for text in (
        "Diagnose und ein möglicher Umsetzungsweg",
        "DAS IST DER ERKANNTE ENGPASS",
        "DAS IST DIE EMPFOHLENE LÖSUNG",
        "DAS KÖNNTE DEIN ZUKÜNFTIGER ABLAUF SEIN",
        "Software / Regeln",
        "BEISPIELAUSGABE · VORSCHAU",
        "DAS PRÜFST DU SELBST",
        "Kleinste nutzbare Version",
        "Voraussetzungen",
        "Wird nicht automatisiert",
        "Autonomiestufe A2",
        "Offene Angaben und Unsicherheiten",
        "SPÄTERE AUSBAUSTUFE",
    ):
        assert text in html
    assert "/sessions/" not in html
    assert "session_id" not in html
    assert "pattern_id" not in html


def test_a0_report_says_that_the_first_step_is_not_an_ai_solution() -> None:
    html = _render(
        _result(
            autonomy_level="A0",
            primary_recommendation="Vorhandene Kalenderregel konsequent nutzen",
            promise="Für diesen Schritt ist keine KI notwendig.",
            ai_task="Für diesen ersten Schritt ist keine KI-Aufgabe notwendig.",
        )
    )
    assert "EINFACHER NÄCHSTER SCHRITT" in html
    assert "Autonomiestufe A0" in html
    assert "keine KI notwendig" in html


def test_missing_fields_remain_open_and_do_not_create_customer_facts() -> None:
    html = _render(
        _result(
            software_rule="",
            sample_output={
                "title": "",
                "fields": [],
                "open_items": [],
                "attachments": [],
                "preview_notice": "",
            },
            smallest_usable_version="",
            implementation_path=[],
            required_prerequisites=[],
            not_automated=[],
            open_details=[],
            uncertainties=[],
            error_boundaries=[],
            later_stage="",
        )
    )
    assert "keine belastbare Vorschau gespeichert" in html
    assert "noch kein belastbarer Einstieg gespeichert" in html
    assert "Keine zusätzlichen Voraussetzungen angegeben" in html
    assert "keine eigenen Grenzen gespeichert" in html
    assert "Beispielkunde" not in html
    assert "OBJ-001" not in html


def test_long_report_content_stays_structured_for_page_breaks() -> None:
    long_items = [f"Offene Angabe {index}: " + ("längerer prüfbarer Inhalt " * 8) for index in range(1, 13)]
    html = _render(
        _result(
            future_process=[f"Schritt {index}: " + ("konkreter Ablauf " * 8) for index in range(1, 7)],
            implementation_path=long_items[:4],
            open_details=long_items,
            error_boundaries=long_items[:3],
        )
    )
    assert "Offene Angabe 12" in html
    assert html.count('class="report-page ') == 2
    css = (ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8")
    assert "@page { size: A4; margin: 11mm 13mm 12mm; }" in css
    assert ".report-page { width: auto; min-height: 0;" in css
    assert ".report-flow li, .report-plan li, .report-boundaries li { break-inside: avoid; }" in css


def test_optional_third_page_is_only_rendered_for_real_secondary_options() -> None:
    base_html = _render(_result())
    extended_html = _render(
        _result(
            secondary_opportunities=[
                {"title": "Spätere Möglichkeit", "description": "Erst nach dem sicheren Einstieg prüfen."}
            ]
        )
    )
    assert base_html.count('class="report-page ') == 2
    assert extended_html.count('class="report-page ') == 3
    assert "OPTIONALE WEITERE MÖGLICHKEITEN" in extended_html
