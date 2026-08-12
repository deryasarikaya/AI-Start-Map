"""Betriebsartenwissen: laden, zuschneiden, und die Schutzregel.

Grundlage: docs/auftrag/BRANCHENWISSEN.md, Abschnitt "Welches Feld geht an
welchen Aufruf" und "Die Schutzregel".
"""

from __future__ import annotations

import pytest
import yaml

from app.business_patterns import (
    FINAL_ANALYSIS_FIELDS,
    INTERVIEW_FIELDS,
    PATTERN_DIRECTORY,
    load_business_pattern,
    pattern_context,
)


PFLICHTFELDER = (
    "business_pattern",
    "business_example",
    "diagnostic_focus",
    "typical_workflows",
    "channels",
    "domain_vocabulary",
    "important_entities",
    "required_information",
    "typical_handoffs",
    "typical_statuses",
    "typical_bottlenecks",
    "typical_exceptions",
    "realistic_customer_language",
    "realistic_worker_language",
    "diagnostically_relevant_questions",
    "diagnostic_signals",
    "do_not_assume",
)


def _alle_dateien() -> list[dict[str, object]]:
    return [
        yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(PATTERN_DIRECTORY.glob("*.yaml"))
    ]


def test_every_pattern_file_carries_the_same_fields() -> None:
    dateien = _alle_dateien()
    assert len(dateien) >= 3
    for daten in dateien:
        assert set(daten) == set(PFLICHTFELDER), daten.get("business_pattern")


def test_every_pattern_asks_where_the_information_converges() -> None:
    """Die gemeinsame Diagnosefrage steht in jeder Datei."""

    for daten in _alle_dateien():
        fragen = daten["diagnostically_relevant_questions"]
        assert "Wo laufen diese Informationen heute am Ende zusammen?" in fragen


def test_no_pattern_assumes_that_ai_comes_first() -> None:
    """do_not_assume haelt die Schutzregel fest."""

    for daten in _alle_dateien():
        assert "dass KI die erste sinnvolle Lösung ist" in daten["do_not_assume"]


@pytest.mark.parametrize(
    ("business_type", "erwartet"),
    [
        ("fotograf", "D_project_briefing_approval"),
        ("blumenladen", "E_orders_goods"),
        ("hausmeisterservice", "A_field_service"),
        ("Fotograf", "D_project_briefing_approval"),
    ],
)
def test_a_known_business_type_finds_its_pattern(
    business_type: str,
    erwartet: str,
) -> None:
    pattern = load_business_pattern(business_type)
    assert pattern is not None
    assert pattern["business_pattern"] == erwartet


@pytest.mark.parametrize(
    "business_type",
    ("kreativagentur", "catering", "fahrschule", "", None, "blumen"),
)
def test_an_unclear_business_type_loads_nothing(business_type: str | None) -> None:
    """Lieber kein Branchenwissen als das eines Nachbargewerbes."""

    assert load_business_pattern(business_type) is None
    assert pattern_context(business_type, fields=FINAL_ANALYSIS_FIELDS) == {}


def test_the_final_analysis_gets_vocabulary_but_not_the_interview_questions() -> None:
    kontext = pattern_context("fotograf", fields=FINAL_ANALYSIS_FIELDS)
    assert "domain_vocabulary" in kontext
    assert "typical_bottlenecks" in kontext
    assert "diagnostically_relevant_questions" not in kontext
    assert "required_information" not in kontext


def test_the_interview_gets_questions_but_not_the_vocabulary() -> None:
    kontext = pattern_context("fotograf", fields=INTERVIEW_FIELDS)
    assert "diagnostically_relevant_questions" in kontext
    assert "required_information" in kontext
    assert "domain_vocabulary" not in kontext
    assert "typical_statuses" not in kontext


def test_empty_fields_are_left_out_instead_of_sent_as_empty() -> None:
    """realistic_worker_language ist in D leer und faellt weg."""

    kontext = pattern_context("fotograf", fields=FINAL_ANALYSIS_FIELDS)
    assert "realistic_worker_language" not in kontext
