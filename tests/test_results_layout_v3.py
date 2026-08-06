from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape


ROOT = Path(__file__).resolve().parents[1]


def _result(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "short_reason": "Digitale Angaben liegen verteilt und werden manuell nachbearbeitet.",
        "bottleneck": {"cause": "Die Angaben werden nicht in einem Vorgang zusammengeführt."},
        "autonomy_level": "A2",
        "primary_recommendation": "Digitale Angaben in einem prüfbaren Entwurf zusammenführen",
        "promise": "Du erhältst ein konkretes, prüfbares Arbeitsergebnis.",
        "customer_benefits": ["Du erkennst offene Angaben früher."],
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
        "visible_result": "Du erhältst eine Vorgangsübersicht.",
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
        "later_stage": "Später kann nach deiner Freigabe ein Folgeschritt vorbereitet werden.",
        "secondary_opportunities": [],
        "as_is_steps": ["Angaben empfangen.", "Angaben manuell übertragen."],
        "problem_step_indexes": [1],
    }
    result.update(overrides)
    return result


def _render(result: dict[str, object]) -> str:
    environment = Environment(
        loader=FileSystemLoader(ROOT / "app" / "templates"),
        autoescape=select_autoescape(("html",)),
    )
    environment.globals["url_for"] = lambda name, **_kwargs: f"/{name}"
    return environment.get_template("results.html").render(
        result=result,
        process={"process_name": "Anfrage bis Freigabe"},
    )


def test_results_follow_the_approved_information_order() -> None:
    html = _render(_result())
    headings = [
        "Das ist der erkannte Engpass",
        "EMPFOHLENE LÖSUNG",
        "DAS KÖNNTE DEIN ZUKÜNFTIGER ABLAUF SEIN",
        "DIESES KONKRETE ERGEBNIS ERHÄLTST DU",
        "DAS PRÜFST DU SELBST",
        "SO KLEIN KANN DER ERSTE SCHRITT SEIN",
        "VORAUSSETZUNGEN UND GRENZEN",
        "SPÄTERE AUSBAUSTUFE",
    ]
    positions = [html.index(heading) for heading in headings]
    assert positions == sorted(positions)
    assert "Normale Software oder Regeln" in html
    assert "Autonomiestufe A2" in html
    assert "/sessions/" not in html


def test_a0_result_uses_non_ai_heading_and_remains_complete() -> None:
    html = _render(
        _result(
            autonomy_level="A0",
            primary_recommendation="Vorhandene Kalenderregel konsequent nutzen",
            promise="Für diesen Schritt ist keine KI notwendig.",
            ai_task="Für diesen ersten Schritt ist keine KI-Aufgabe notwendig.",
            not_automated=["Terminentscheidung"],
        )
    )
    assert "EINFACHER NÄCHSTER SCHRITT" in html
    assert "Autonomiestufe A0" in html
    assert "keine KI notwendig" in html


def test_missing_legacy_fields_and_many_open_points_render_safely() -> None:
    html = _render(
        _result(
            sample_output={
                "title": "",
                "fields": [],
                "open_items": [],
                "attachments": [],
                "preview_notice": "",
            },
            software_rule="",
            smallest_usable_version="",
            not_automated=[],
            open_details=[f"Offener Punkt {index}" for index in range(1, 7)],
            uncertainties=["Zusätzliche Unsicherheit"],
        )
    )
    assert "keine belastbare Vorschau gespeichert" in html
    assert "Offener Punkt 6" in html
    assert "keine eigenen Grenzen gespeichert" in html
    assert "Pflichtfelder festlegen" in html


@pytest.mark.parametrize(
    ("recommendation", "output"),
    [
        ("Einsatznotiz aus Sprache, Fotos und Bon vorbereiten", "Einsatznotiz"),
        ("Freigaben aus E-Mail und WhatsApp in einer Vorgangsakte bündeln", "Freigabestatus"),
    ],
)
def test_mentor_cases_keep_long_specific_content_scanable(
    recommendation: str,
    output: str,
) -> None:
    html = _render(
        _result(
            primary_recommendation=recommendation,
            visible_result=f"Du erhältst {output} mit allen offenen Angaben.",
        )
    )
    assert recommendation in html
    assert output in html
    assert "future-process-line" in html


def test_result_typography_is_bounded_for_desktop_and_mobile() -> None:
    css = (ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8")
    assert ".result-intro h1" in css
    assert "font-size: clamp(2.1rem, 4vw, 2.5rem)" in css
    assert "font-size: clamp(1.85rem, 8vw, 2rem)" in css
    assert "max-width: 72ch" in css
    assert ".boundary-columns" in css
    assert "overflow-wrap: anywhere" in css


def test_error_state_keeps_a_clear_retry_action() -> None:
    environment = Environment(
        loader=FileSystemLoader(ROOT / "app" / "templates"),
        autoescape=select_autoescape(("html",)),
    )
    environment.globals["url_for"] = lambda name, **_kwargs: f"/{name}"
    html = environment.get_template("error.html").render(
        error_title="Die Analyse konnte nicht fortgesetzt werden.",
        error_message="Bitte versuche es erneut.",
        retry_path="/processing",
    )
    assert "Deine bisherigen Angaben bleiben gespeichert" in html
    assert "Noch einmal versuchen" in html
    assert 'href="/processing"' in html
