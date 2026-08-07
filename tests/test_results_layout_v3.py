from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.schemas import customer_plain_text


ROOT = Path(__file__).resolve().parents[1]


def _result(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "is_non_ai": False,
        "short_reason": "Fotos, Notizen und Bons liegen heute an verschiedenen Stellen.",
        "bottleneck": {"cause": "Beim Rechnungsschreiben musst du alles wieder zusammensuchen."},
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
            "input_context": "Sprachnachricht nach dem Einsatz",
            "incoming_message": "Die Dichtung am Waschbecken ist getauscht. Der Einsatz dauerte 45 Minuten.",
            "incoming_note": "Mit zwei Fotos und einem Bon",
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
            "missing_details": ["Tür nachstellen abrechnen"],
            "clarification_question": "Soll das Nachstellen der Tür mit abgerechnet werden?",
        },
        "first_step_text": "Probier es bei den n\u00e4chsten f\u00fcnf Eins\u00e4tzen aus.",
        "first_step_follow_up": "Erst danach lohnt sich der n\u00e4chste Schritt.",
        "contact_recommendation": "Mobile Einsatzdokumentation aus Sprache, Fotos und Bon",
        "secondary_opportunities": [],
        "as_is_steps": ["Angaben auf dem Handy sammeln.", "Abends alles zusammensuchen."],
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
    environment.filters["customer_text"] = customer_plain_text
    return environment.get_template("results.html").render(
        result=result,
        process={"process_name": "Einsatz bis Rechnung"},
    )


def test_results_have_seven_visible_blocks_in_the_approved_order() -> None:
    html = _render(_result())
    headings = [
        "Das ist der Engpass",
        "So habe ich deinen heutigen Ablauf verstanden",
        "Das schlage ich dir vor".upper(),
        "So w\u00fcrde es k\u00fcnftig laufen",
        "So sieht die Hilfe konkret aus",
        "Nichts geht ohne dich raus",
        "So klein f\u00e4ngst du an",
        "M\u00f6chtest du das umsetzen?",
    ]
    positions = [html.index(heading) for heading in headings]
    assert positions == sorted(positions)
    assert html.count("data-result-block") == 7
    assert "Normale Software oder Regeln" not in html
    assert "Autonomiestufe" not in html
    assert "/sessions/" not in html


def test_non_ai_result_has_no_visible_internal_level() -> None:
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


def test_example_is_central_and_technical_detail_sections_are_hidden() -> None:
    html = _render(_result())
    assert "Beispiel \u2014 so k\u00f6nnte deine Einsatznotiz aussehen" in html
    assert "Hausverwaltung Nord" in html
    assert "Voraussetzungen und Grenzen" not in html
    assert "Fehler- und Pr\u00fcfgrenzen" not in html
    assert "Sp\u00e4tere Ausbaustufe" not in html
    assert "So habe ich deinen heutigen Ablauf verstanden" in html


def test_secondary_item_without_complete_content_is_not_rendered() -> None:
    html = _render(
        _result(secondary_opportunities=[])
    )
    assert "Weitere M\u00f6glichkeiten" not in html


def test_result_typography_is_bounded_for_desktop_and_mobile() -> None:
    css = (ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8")
    assert "font-size: clamp(2.25rem, 4vw, 2.625rem)" in css
    assert "font-size: clamp(1.75rem, 8vw, 2.125rem)" in css
    assert "max-width: 72ch" in css
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
