"""Einmaliger Merge: Recommendation-Katalog v1 + Research Batches 05-07 -> v2.

Additiv. Bestehende Felder werden nicht ueberschrieben; ergaenzt werden
GenAI-Faehigkeiten, Failure Patterns, Entscheidungs-Gates, die Nicht-GenAI-
Gegenliste sowie je Solution Pattern und Problemfamilie die neuen Spalten aus
der Forschungsgrundlage vom 2026-08-06.

Aufruf:
    python scripts/merge_catalog_v2.py            # schreibt v2 und zeigt Diff
    python scripts/merge_catalog_v2.py --dry-run  # zeigt nur den Diff
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "knowledge" / "structured" / "recommendation_catalog.json"
BATCHES = ROOT / "knowledge" / "research_batches"
RESEARCH_MD = (
    ROOT
    / "knowledge"
    / "raw"
    / "AI_Start_Map_Research_GenAI_Unterstuetzung_Kleinunternehmen_2026-08-06.md"
)

CAPABILITY_FILE = BATCHES / "batch_05_genai_capability_evidence" / "01_capability_catalog.jsonl"
GATE_FILE = BATCHES / "batch_05_genai_capability_evidence" / "02_decision_gates.jsonl"
SOLUTION_FILE = BATCHES / "batch_06_solution_pattern_validation" / "01_solution_pattern_catalog.jsonl"
FAILURE_FILE = BATCHES / "batch_07_failure_and_overautomation" / "01_failure_patterns.jsonl"

# Felder aus Batch 06, die je Solution Pattern uebernommen werden.
SOLUTION_FIELDS = (
    "genai_capability_ids",
    "deterministic_components",
    "human_decisions",
    "positive_variants",
    "counterexample",
    "pilot",
    "metrics",
    "stop_conditions",
    "autonomy_level_min",
    "autonomy_level_max",
)


def read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        raise SystemExit(f"Datei fehlt: {path}")
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def markdown_table(marker: str, expected_columns: int) -> list[list[str]]:
    """Liest die erste Markdown-Tabelle nach einer Ueberschrift."""

    text = RESEARCH_MD.read_text(encoding="utf-8")
    start = text.index(marker)
    rows: list[list[str]] = []
    for line in text[start:].splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if rows:
                break
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        if len(cells) == expected_columns:
            rows.append(cells)
    return rows[1:]  # Kopfzeile entfernen


def problem_family_roles() -> dict[str, dict[str, str]]:
    """Abschnitt 6: PF -> GenAI-Rolle, Nicht-GenAI-Anteil, menschliche Grenze."""

    roles: dict[str, dict[str, str]] = {}
    for cells in markdown_table(
        "## 6. Zuordnung der 12 Problemfamilien", expected_columns=4
    ):
        match = re.match(r"(PF-\d{2})\s*(.*)", cells[0])
        if match is None:
            continue
        roles[match.group(1)] = {
            "genai_role": cells[1],
            "non_genai_requirement": cells[2],
            "human_boundary": cells[3],
        }
    return roles


def non_genai_mechanisms() -> list[dict[str, str]]:
    """Abschnitt 5: Aufgaben, die bewusst nicht mit GenAI geloest werden."""

    return [
        {"task": cells[0], "mechanism": cells[1]}
        for cells in markdown_table("## 5. Was nicht primär GenAI ist", expected_columns=2)
    ]


AUTONOMY_LEVELS = [
    {
        "level": "A0",
        "name": "Keine KI",
        "description": "Eine klare Regel oder Standardsoftware loest das Problem besser.",
        "recommend": "ausdruecklich empfehlen, wenn passend",
    },
    {
        "level": "A1",
        "name": "Persoenliche Assistenz",
        "description": "Du gibst etwas ein, die KI erstellt einen einmaligen Entwurf.",
        "recommend": "niedrigster Einstieg",
    },
    {
        "level": "A2",
        "name": "Eingebetteter Entwurf",
        "description": "Die KI verarbeitet Vorgangsdaten, ein Mensch bestaetigt jeden Output.",
        "recommend": "Standardziel fuer AI Start Map",
    },
    {
        "level": "A3",
        "name": "Kontrollierter Workflow",
        "description": "Ein bestaetigter Output loest regelbasierte Folgeaktionen aus.",
        "recommend": "erst nach Pilot und Messung",
    },
    {
        "level": "A4",
        "name": "Begrenzte Agentenaktion",
        "description": "Die KI waehlt Werkzeuge in engen Grenzen, Freigabe vor Aussenwirkung.",
        "recommend": "nur bei stabilen Prozessen",
    },
    {
        "level": "A5",
        "name": "Autonome Aussenwirkung",
        "description": "Die KI sendet, bucht, bezahlt oder entscheidet selbst.",
        "recommend": "nicht als Einstieg empfehlen",
    },
]


def build() -> tuple[dict, list[str]]:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    changes: list[str] = []

    capabilities = read_jsonl(CAPABILITY_FILE)
    gates = read_jsonl(GATE_FILE)
    failures = read_jsonl(FAILURE_FILE)
    validated = {item["solution_id"]: item for item in read_jsonl(SOLUTION_FILE)}
    narrowed_pairs: set[tuple[str, str]] = set()

    catalog["version"] = "2026-08-06-v2"
    catalog["source"] = (
        "docs/product/AI_Start_Map_Fachgrundlage_Painpoints_Solutions_2026-08-05.md; "
        "knowledge/raw/AI_Start_Map_Research_GenAI_Unterstuetzung_Kleinunternehmen_2026-08-06.md"
    )

    catalog["genai_capabilities"] = [
        {
            "capability_id": item["capability_id"],
            "name": item["name"],
            "input_modalities": item["input_modalities"],
            "output_type": item["output_type"],
            "suitable_tasks": item["suitable_tasks"],
            "required_process_foundation": item["required_process_foundation"],
            "human_review": item["human_review"],
            "failure_modes": item["failure_modes"],
            "measurement": item["measurement"],
            "autonomy_ceiling": item["autonomy_ceiling"],
            "evidence_refs": item["source_refs"],
            "customer_language": item["text"],
        }
        for item in capabilities
    ]
    changes.append(f"+ genai_capabilities: {len(capabilities)} Eintraege")

    catalog["decision_gates"] = [
        {
            "gate_id": item["gate_id"],
            "name": item["name"],
            "question": item["question"],
            "on_pass": item["pass"],
            "on_fail": item["fail"],
        }
        for item in gates
    ]
    changes.append(f"+ decision_gates: {len(gates)} Eintraege")

    catalog["failure_patterns"] = [
        {
            "failure_id": item["failure_id"],
            "name": item["name"],
            "trigger": item["trigger"],
            "harm": item["harm"],
            "detection": item["detection"],
            "guardrail": item["guardrail"],
            "blocks_autonomy": item["blocks_autonomy"],
            "customer_language": item["text"],
        }
        for item in failures
    ]
    changes.append(f"+ failure_patterns: {len(failures)} Eintraege")

    catalog["autonomy_levels"] = AUTONOMY_LEVELS
    changes.append(f"+ autonomy_levels: {len(AUTONOMY_LEVELS)} Stufen A0-A5")

    mechanisms = non_genai_mechanisms()
    catalog["non_genai_mechanisms"] = mechanisms
    changes.append(f"+ non_genai_mechanisms: {len(mechanisms)} Aufgaben (A0-Pfad)")

    roles = problem_family_roles()
    for family in catalog["problem_families"]:
        role = roles.get(family["problem_family_id"])
        if role is None:
            changes.append(f"! {family['problem_family_id']}: keine Rolle in Abschnitt 6 gefunden")
            continue
        family.update(role)
    changes.append(f"~ problem_families: 3 neue Felder fuer {len(roles)} Familien")

    for pattern in catalog["solution_patterns"]:
        source = validated.get(pattern["solution_id"])
        if source is None:
            changes.append(f"! {pattern['solution_id']}: nicht in Batch 06 enthalten")
            continue
        pattern["genai_capability_ids"] = source["genai_capabilities"]
        pattern["deterministic_components"] = source["deterministic_components"]
        pattern["human_decisions"] = source["human_decisions"]
        pattern["positive_variants"] = source["positive_variants"]
        pattern["counterexample"] = source["counterexample"]
        pattern["pilot"] = source["pilot"]
        pattern["metrics"] = source["metrics"]
        pattern["stop_conditions"] = source["stop_conditions"]
        # Batch 06 notiert teils eine Spanne ("A0-A2"). Getrennt speichern,
        # damit die Untergrenze (auch A0 = bewusst keine KI) auswertbar bleibt.
        raw_level = str(source["autonomy_level"]).strip()
        levels = re.findall(r"A\d", raw_level)
        pattern["autonomy_level_min"] = levels[0]
        pattern["autonomy_level_max"] = levels[-1]

        old_families = list(pattern["problem_family_ids"])
        new_families = [item for item in old_families if item in source["problem_families"]]
        added = [item for item in source["problem_families"] if item not in old_families]
        if added:
            changes.append(
                f"! {pattern['solution_id']}: Batch 06 nennt zusaetzlich {added} "
                "- nicht uebernommen, bitte fachlich pruefen"
            )
        if new_families != old_families:
            removed = [item for item in old_families if item not in new_families]
            narrowed_pairs.update((pattern["solution_id"], item) for item in removed)
            pattern["problem_family_ids"] = new_families
            changes.append(
                f"~ {pattern['solution_id']}: Zuordnung verengt, entfernt {removed}"
            )
    changes.append(f"~ solution_patterns: {len(SOLUTION_FIELDS)} neue Felder je Pattern")

    # Matrix nur dort angleichen, wo Batch 06 eine Zuordnung tatsaechlich
    # entfernt hat. Bereits vorher abweichende supplementary-Eintraege bleiben
    # unveraendert und werden nur als Hinweis gemeldet.
    for mapping in catalog["matrix"]:
        family_id = mapping["problem_family_id"]
        for key in ("primary_solution_ids", "supplementary_solution_ids"):
            kept = [
                item for item in mapping[key] if (item, family_id) not in narrowed_pairs
            ]
            dropped = [item for item in mapping[key] if item not in kept]
            if dropped:
                changes.append(f"~ Matrix {family_id}.{key}: entfernt {dropped}")
            mapping[key] = kept
        if not mapping["primary_solution_ids"]:
            changes.append(
                f"! Matrix {family_id}: keine primaere Solution mehr - bitte pruefen"
            )

    # Vorbestehende Inkonsistenzen sichtbar machen, ohne sie zu aendern.
    families_by_solution = {
        pattern["solution_id"]: set(pattern["problem_family_ids"])
        for pattern in catalog["solution_patterns"]
    }
    for mapping in catalog["matrix"]:
        family_id = mapping["problem_family_id"]
        for key in ("primary_solution_ids", "supplementary_solution_ids"):
            for solution_id in mapping[key]:
                if family_id not in families_by_solution.get(solution_id, set()):
                    changes.append(
                        f"? Hinweis: Matrix {family_id}.{key} nennt {solution_id}, "
                        f"aber {solution_id} listet {family_id} nicht - unveraendert gelassen"
                    )
    return catalog, changes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    arguments = parser.parse_args()

    catalog, changes = build()
    for line in changes:
        print(line)
    if arguments.dry_run:
        print("\n--dry-run: nichts geschrieben.")
        return
    CATALOG.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\nGeschrieben: {CATALOG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
