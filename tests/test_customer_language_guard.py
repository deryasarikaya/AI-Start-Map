from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.models import Analysis, AutomationOpportunity
from app.recommendation_service import load_recommendation_catalog
from app.routes import _result_view
from app.schemas import contains_forbidden_customer_term, customer_plain_text
from app.routes import _question_from_open_detail, _same_required_topic


ROOT = Path(__file__).resolve().parents[1]
CASES = (
    ("Hausmeister", "SP-03", "A1"),
    ("Fotograf", "SP-02", "A1"),
    ("Blumenladen", "SP-01", "A1"),
    ("Coach", "SP-02", "A1"),
    ("Kalender", "", "A0"),
)


from tests.conftest import spec_core_output, spec_payload


def _catalog_title(solution_id: str) -> str:
    catalog = load_recommendation_catalog()
    return next(
        item.name
        for item in catalog.solution_patterns
        if item.solution_id == solution_id
    )


def _view(case_name: str, solution_id: str, level: str) -> dict[str, object]:
    """Ein gespeicherter Stand, in den absichtlich Fachwoerter gestreut sind.

    Geprueft wird, dass davon nichts in der gerenderten Seite ankommt.
    """

    primary_title = (
        _catalog_title(solution_id)
        if solution_id
        else "Vorhandene Funktion oder einfache Regel zuerst nutzen"
    )
    loesung = dict(spec_payload()["loesung"])
    loesung["titel"] = primary_title
    loesung["was_die_ki_macht"] = (
        "Softwareregeln pruefen Pflichtfelder und Formate; der Upload wird "
        "dem Einsatzanker zugeordnet."
    )
    beispiel = dict(spec_payload()["beispiel"])
    beispiel["titel"] = "Was aus einer Nachricht wird"
    beispiel["daraus_wird"] = [
        {"label": "Einsatz-ID", "wert": "Beispiel: Musterhaus"},
        {"label": "Pflichtfeld", "wert": "noch offen"},
    ]
    umsetzung = dict(spec_payload()["umsetzung"])
    umsetzung["erster_schritt"] = (
        "Wir starten einen Pilot und konfigurieren die Pflichtfelder; nach zwei "
        "Wochen sehen wir, ob die Angaben vollstaendig ankommen."
    )
    voraussetzungen = dict(spec_payload()["voraussetzungen"])
    voraussetzungen["neu_hinzukommend"] = [
        "Ein eindeutiger Vorgangsanker",
        "Ein mobiler Eingang",
    ]
    core_output = spec_core_output(
        loesung=loesung,
        beispiel=beispiel,
        umsetzung=umsetzung,
        voraussetzungen=voraussetzungen,
        grenzen="Der Datensatz bleibt ohne Zielschema unvollstaendig.",
        autonomy_level=level,
    )
    analysis = Analysis(
        session_id=1,
        process_summary=f"Der heutige Ablauf für {case_name} wurde bestätigt.",
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
        human_approval="Du prüfst das Ergebnis.",
        first_step="Mit fünf Beispielen beginnen.",
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
def test_runtime_workflow_wording_never_reaches_customer_templates(
    case_name: str,
    solution_id: str,
    level: str,
) -> None:
    rendered = _render("results.html", _view(case_name, solution_id, level), case_name)
    rendered += _render("report.html", _view(case_name, solution_id, level), case_name)
    for internal_phrase in (
        "extrahiert",
        "Pflichtfelder",
        "deterministisch",
        "Quellenbezug",
        "für den Fall",
    ):
        assert internal_phrase.casefold() not in rendered.casefold()


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
        block_end = (
            html.index('data-result-block aria-labelledby="check-title"', marker)
            if template_name == "results.html"
            else html.index('class="report-page report-page-two"', marker)
        )
        outside = html[:marker] + html[block_end:]
        for feld in result["beispiel"]["daraus_wird"]:
            assert feld["wert"] in html[marker:block_end]
            assert feld["wert"] not in outside


def test_missing_details_never_repeat_what_the_message_already_says() -> None:
    """Was als fehlend markiert ist, darf nicht in der Beispielnachricht stehen."""

    result = _view("Hausmeister", "SP-03", "A1")
    beispiel = result["beispiel"]
    nachricht = beispiel["nachricht"].casefold()
    for eintrag in beispiel["fehlt"]:
        assert eintrag.casefold() not in nachricht


def test_unsubstantiated_benefit_claim_is_removed_without_word_replacement() -> None:
    text = (
        "Eine Vorgangsakte reduziert Suchzeit und Nacharbeit. "
        "Du siehst danach den geprüften Eintrag."
    )
    assert customer_plain_text(text) == "Du siehst danach den geprüften Eintrag."


def test_real_address_with_musterstrasse_is_not_confused_with_pattern_language() -> None:
    text = "Lieferung an Frau Müller, Musterstraße 5."
    assert customer_plain_text(text) == text


def test_open_question_conflicting_with_prerequisite_is_detected() -> None:
    assert _same_required_topic(
        "Wie erkennst du heute, zu welchem Auftrag ein Bon gehört?",
        "Es ist klar, zu welchem Auftrag der Einsatz gehört.",
    )


def test_non_question_open_detail_is_not_rewritten_into_a_different_question() -> None:
    assert _question_from_open_detail(
        "Berechtigungen für Fotos und Sprachnachrichten sind nicht geklärt."
    ) == ""


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
    # docs/auftrag/ ist ausgenommen: dort steht die Schreibweise ausdruecklich
    # als Gegenbeispiel in der Regel, die sie verbietet.
    wrong_name = subprocess.run(
        [
            "git", "grep", "-ni", "-w", "Da" + "ria",
            "--", ":(exclude)docs/auftrag",
        ],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    assert slogan.returncode == 1, slogan.stdout
    assert wrong_name.returncode == 1, wrong_name.stdout
