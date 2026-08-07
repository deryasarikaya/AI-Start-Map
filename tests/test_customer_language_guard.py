from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.models import Analysis, AutomationOpportunity
from app.recommendation_service import load_recommendation_catalog
from app.routes import _result_view
from app.schemas import contains_forbidden_customer_term, customer_plain_text


ROOT = Path(__file__).resolve().parents[1]
CASES = (
    ("Hausmeister", "SP-03", "A1"),
    ("Fotograf", "SP-02", "A1"),
    ("Blumenladen", "SP-01", "A1"),
    ("Coach", "SP-02", "A1"),
    ("Kalender", "", "A0"),
)


def _catalog_title(solution_id: str) -> str:
    catalog = load_recommendation_catalog()
    return next(
        item.name
        for item in catalog.solution_patterns
        if item.solution_id == solution_id
    )


def _view(case_name: str, solution_id: str, level: str) -> dict[str, object]:
    primary_title = (
        _catalog_title(solution_id)
        if solution_id
        else "Vorhandene Funktion oder einfache Regel zuerst nutzen"
    )
    core_output = {
        "primary_recommendation": primary_title,
        "promise": "Du erh\u00e4ltst ein verst\u00e4ndliches Ergebnis, das du selbst pr\u00fcfst.",
        "short_reason": "Einsatzanker, Pflichtfelder und Upload-Zuordnung fehlen heute.",
        "future_process": [
            "Du schickst die vorhandenen Angaben.",
            "Die KI bereitet einen Entwurf vor.",
            "Softwareregeln pr\u00fcfen Pflichtfelder und Formate.",
            "Du pr\u00fcfst und best\u00e4tigst das Ergebnis.",
        ],
        "sample_output": {
            "title": "[Preview] Musterhaus",
            "fields": [
                {"label": "Einsatz-ID", "value": "Beispiel: [Preview] Musterhaus"},
                {"label": "Pflichtfeld", "value": "noch offen"},
            ],
            "open_items": [
                "Wie erkennst du heute, zu welchem Auftrag ein Bon geh\u00f6rt?",
                "Wie erkennst du heute, zu welchem Auftrag ein Bon geh\u00f6rt?",
                "Wie viele Auftr\u00e4ge pro Woche gibt es?",
                "Ein nicht belegtes Detail im heutigen Ablauf bleibt noch offen.",
            ],
        },
        "visible_result": "Ein pr\u00fcfbarer Entwurf.",
        "human_check": "Du pr\u00fcfst und best\u00e4tigst das Ergebnis.",
        "smallest_usable_version": "Starte einen Pilot und konfiguriere Pflichtfelder.",
        "implementation_path": ["Pilot starten.", "Rollout vorbereiten."],
        "required_prerequisites": ["Ein eindeutiger Vorgangsanker", "Ein mobiler Eingang"],
        "open_details": [
            "Die Freigaberolle ist noch offen.",
            "Wie die Ablage heute funktioniert, ist noch nicht klar.",
        ],
        "later_stage": "Sp\u00e4ter kann ein Rechnungsentwurf vorbereitet werden.",
        "secondary_opportunities": [
            {"title": "noch offen", "description": "Noch keine Beschreibung"},
            {"title": "", "description": "Ohne Titel"},
        ],
        "autonomy_level": level,
    }
    analysis = Analysis(
        session_id=1,
        process_summary=f"Der heutige Ablauf f\u00fcr {case_name} wurde best\u00e4tigt.",
        as_is_steps={
            "steps": ["Angaben annehmen", "Informationen zusammensuchen"],
            "problem_step_indexes": [1],
        },
        core_bottleneck="Informationen liegen an mehreren Stellen.",
        uncertainties={
            "items": ["Die Freigabe ist noch offen."],
            "core_output": core_output,
        },
    )
    opportunity = AutomationOpportunity(
        opportunity_id=1,
        session_id=1,
        rank=1,
        title=primary_title,
        problem="Informationen liegen an mehreren Stellen.",
        recommendation="Einen Entwurf vorbereiten.",
        benefit="Du musst weniger zusammensuchen.",
        human_approval="Du pr\u00fcfst das Ergebnis.",
        first_step="Mit f\u00fcnf Beispielen beginnen.",
        blueprint_json=None,
    )
    return _result_view(analysis, [opportunity])


def _render(template_name: str, result: dict[str, object], case_name: str) -> str:
    environment = Environment(
        loader=FileSystemLoader(ROOT / "app" / "templates"),
        autoescape=select_autoescape(("html",)),
    )
    environment.globals["url_for"] = lambda name, **_kwargs: f"/{name}"
    environment.filters["customer_text"] = customer_plain_text
    return environment.get_template(template_name).render(
        result=result,
        process={"process_name": case_name},
        analysis_date="07.08.2026",
    )


@pytest.mark.parametrize(("case_name", "solution_id", "level"), CASES)
def test_five_mentor_cases_have_no_forbidden_language_in_html_or_report(
    case_name: str,
    solution_id: str,
    level: str,
) -> None:
    result = _view(case_name, solution_id, level)
    results_html = _render("results.html", result, case_name)
    report_html = _render("report.html", result, case_name)
    assert not contains_forbidden_customer_term(result)
    assert not contains_forbidden_customer_term(results_html)
    assert not contains_forbidden_customer_term(report_html)
    assert "Autonomiestufe" not in results_html + report_html


@pytest.mark.parametrize(("case_name", "solution_id", "level"), CASES)
def test_example_values_only_appear_inside_the_marked_preview(
    case_name: str,
    solution_id: str,
    level: str,
) -> None:
    result = _view(case_name, solution_id, level)
    for template_name in ("results.html", "report.html"):
        html = _render(template_name, result, case_name)
        marker = html.index("data-customer-example-block")
        block_end = html.index("</section>", marker)
        outside = html[:marker] + html[block_end:]
        for field in result["sample_output"]["fields"]:
            assert field["value"] in html[marker:block_end]
            assert field["value"] not in outside


def test_open_questions_are_concrete_deduplicated_and_limited() -> None:
    result = _view("Hausmeister", "SP-03", "A1")
    questions = result["open_questions"]
    assert len(questions) <= 3
    assert len(questions) == len({item.casefold() for item in questions})
    assert all(item.endswith("?") for item in questions)
    assert all("pro Woche" not in item for item in questions)


def test_empty_secondary_suggestions_are_not_returned() -> None:
    result = _view("Hausmeister", "SP-03", "A1")
    assert result.get("secondary_opportunities", []) == []


def test_old_slogan_and_wrong_name_are_absent_from_tracked_files() -> None:
    slogan = subprocess.run(
        [
            "git",
            "grep",
            "-n",
            "Ordnen · mit KI unterst\u00fctzen · sp\u00e4ter automatisieren",
            "--",
            "app/templates",
        ],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    wrong_name = subprocess.run(
        ["git", "grep", "-ni", "-w", "Da" + "ria"],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    assert slogan.returncode == 1, slogan.stdout
    assert wrong_name.returncode == 1, wrong_name.stdout
