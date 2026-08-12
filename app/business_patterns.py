"""Betriebsartenwissen laden und je Aufruf zuschneiden.

Die Dateien unter ``knowledge/business_patterns/`` sagen dem Modell, worauf es
bei einer Betriebsart achten kann — nie, welche Loesung der Betrieb braucht.

Welches Feld an welchen Aufruf geht, steht als Tabelle in
``docs/auftrag/BRANCHENWISSEN.md``. Sie ist hier abgebildet: die Dateien sind
umfangreich, und das Zeitbudget der Endanalyse ist knapp.
"""

from __future__ import annotations

import logging
import re
from functools import lru_cache
from pathlib import Path

import yaml


logger = logging.getLogger(__name__)

PATTERN_DIRECTORY = (
    Path(__file__).resolve().parents[1] / "knowledge" / "business_patterns"
)

#: Felder fuer den Interviewpfad - worauf sich Rueckfragen stuetzen duerfen.
INTERVIEW_FIELDS: tuple[str, ...] = (
    "diagnostic_focus",
    "typical_workflows",
    "channels",
    "diagnostic_signals",
    "do_not_assume",
    "diagnostically_relevant_questions",
    "typical_exceptions",
    "required_information",
)

#: Felder fuer die Endanalyse - Wortschatz und typische Engpaesse.
FINAL_ANALYSIS_FIELDS: tuple[str, ...] = (
    "diagnostic_focus",
    "typical_workflows",
    "channels",
    "diagnostic_signals",
    "do_not_assume",
    "domain_vocabulary",
    "important_entities",
    "typical_statuses",
    "typical_handoffs",
    "typical_bottlenecks",
    "realistic_customer_language",
    "realistic_worker_language",
)


def _normalize(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9äöüß]+", value.casefold().replace("_", " ")))


@lru_cache(maxsize=1)
def _patterns_by_business_example() -> dict[str, dict[str, object]]:
    """Alle Musterdateien, verschluesselt ueber ihr business_example."""

    patterns: dict[str, dict[str, object]] = {}
    if not PATTERN_DIRECTORY.is_dir():
        return patterns
    for path in sorted(PATTERN_DIRECTORY.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            logger.warning("business_pattern.unreadable file=%s", path.name)
            continue
        if not isinstance(data, dict):
            continue
        beispiel = _normalize(str(data.get("business_example") or ""))
        if beispiel:
            patterns[beispiel] = data
    return patterns


def load_business_pattern(business_type: str | None) -> dict[str, object] | None:
    """Genau die Datei zur Betriebsart, oder keine.

    Es wird ausschliesslich auf ``business_example`` abgeglichen. Passt nichts
    eindeutig, wird nichts geladen — lieber kein Branchenwissen als das eines
    Nachbargewerbes.
    """

    gesucht = _normalize(business_type or "")
    if not gesucht:
        return None
    treffer = _patterns_by_business_example().get(gesucht)
    if treffer is None:
        logger.info("business_pattern.no_match business_type=%s", business_type)
        return None
    logger.info(
        "business_pattern.matched business_type=%s pattern=%s",
        business_type,
        treffer.get("business_pattern"),
    )
    return treffer


def pattern_context(
    business_type: str | None,
    *,
    fields: tuple[str, ...],
) -> dict[str, object]:
    """Die Musterdatei auf die Felder eines Aufrufs zugeschnitten."""

    pattern = load_business_pattern(business_type)
    if pattern is None:
        return {}
    zugeschnitten = {
        name: pattern[name]
        for name in fields
        if pattern.get(name) not in (None, "", [], {})
    }
    if zugeschnitten:
        zugeschnitten["business_pattern"] = pattern.get("business_pattern", "")
    return zugeschnitten
