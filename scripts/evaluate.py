"""Messschleife fuer die Recommendation-Auswahl.

Schickt alle vorhandenen Evaluationsfaelle durch die produktive Kette
    Klassifikation -> Gates -> select_recommendation
und misst, wie gut sie trifft.

Zwei Klassifikator-Modi:
    --classifier keyword   deterministische Stichwort-Logik (Baseline,
                           kein LLM-Aufruf, kostet nichts, laeuft in Sekunden)
    --classifier llm       Structured-Output-Klassifikator aus
                           app/llm_classification.py (echte OpenAI-Aufrufe,
                           ein Aufruf pro Fall; --workers parallelisiert)

Ohne bestaetigte Labels werden nur die labelfreien Kennzahlen ausgegeben
(Default-Quote, Gate-Streuung, verbotene Inhalte). Sobald in
knowledge/evaluation/expected_labels.json Faelle auf "confirmed": true stehen,
kommen Trefferquoten fuer Problemfamilie und Solution Pattern dazu.

Aufruf:
    python scripts/evaluate.py
    python scripts/evaluate.py --classifier llm --workers 8
    python scripts/evaluate.py --json ergebnis.json
    python scripts/evaluate.py --show-misses
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIRECTORY))

from app.recommendation_service import (  # noqa: E402
    classify_problem_families,
    infer_decision_gates,
    load_recommendation_catalog,
    select_recommendation,
)

EVALUATION_DIRECTORY = ROOT_DIRECTORY / "knowledge" / "evaluation"
LABEL_FILE = EVALUATION_DIRECTORY / "expected_labels.json"
BATCH_09_FILE = EVALUATION_DIRECTORY / "batch_09_evaluation_cases.jsonl"

CASE_FILES = {
    "EVAL-C": EVALUATION_DIRECTORY / "cases_ten_kmu.json",
    "RB03": EVALUATION_DIRECTORY / "cases_rb03.json",
    "RB04": EVALUATION_DIRECTORY / "cases_rb04_agent.json",
    "RB07": EVALUATION_DIRECTORY / "cases_rb07_guardrail.json",
}


@dataclass
class EvaluationCase:
    case_id: str
    source: str
    text: str
    forbidden: list[str] = field(default_factory=list)
    required: list[str] = field(default_factory=list)
    expected_verdict: str = ""
    dataset: str = "legacy_91"
    expected_families: list[str] = field(default_factory=list)
    expected_solutions: list[str] = field(default_factory=list)
    label_status: str = "unlabelled"


def _read_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def load_cases() -> list[EvaluationCase]:
    """Lädt Legacy- und Batch-09-Fälle mit strikt getrennten Datensatzrollen."""

    cases: list[EvaluationCase] = []

    path = CASE_FILES["EVAL-C"]
    if path.is_file():
        for case in _read_json(path)["cases"]:
            cases.append(
                EvaluationCase(
                    case_id=case["evaluation_id"],
                    source="EVAL-C",
                    text=" ".join(
                        filter(
                            None,
                            [
                                str(case.get("expected_core_process", "")),
                                str(case.get("expected_core_bottleneck", "")),
                            ],
                        )
                    ),
                    forbidden=list(case.get("forbidden_recommendations", [])),
                    required=list(case.get("required_questions", [])),
                )
            )

    path = CASE_FILES["RB03"]
    if path.is_file():
        payload = _read_json(path)
        for case in payload["cases"] if isinstance(payload, dict) else payload:
            cases.append(
                EvaluationCase(
                    case_id=case["evaluation_id"],
                    source="RB03",
                    text=str(case.get("scenario", "")),
                    forbidden=list(case.get("forbidden_behaviors", [])),
                    required=list(case.get("required_questions_or_checks", [])),
                    expected_verdict=str(case.get("expected_gate", "")),
                )
            )

    path = CASE_FILES["RB04"]
    if path.is_file():
        for case in _read_json(path)["cases"]:
            state = case.get("current_agent_state", {})
            cases.append(
                EvaluationCase(
                    case_id=case["case_id"],
                    source="RB04",
                    text=" ".join(
                        filter(
                            None,
                            [
                                str(state.get("selected_process", "")),
                                " ".join(state.get("as_is_steps", []) or []),
                                str(case.get("latest_user_message", "")),
                            ],
                        )
                    ),
                    forbidden=list(case.get("unacceptable_next_questions", [])),
                    expected_verdict=str(case.get("expected_next_action", "")),
                )
            )

    path = CASE_FILES["RB07"]
    if path.is_file():
        for case in _read_json(path)["cases"]:
            cases.append(
                EvaluationCase(
                    case_id=case["id"],
                    source="RB07",
                    text=str(case["input"]),
                    forbidden=list(case.get("must_not_include", [])),
                    required=list(case.get("must_include", [])),
                    expected_verdict=str(case.get("expected", "")),
                )
            )
    if BATCH_09_FILE.is_file():
        for line in BATCH_09_FILE.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            case = json.loads(line)
            cases.append(
                EvaluationCase(
                    case_id=case["case_id"],
                    source="BATCH-09",
                    dataset="batch_09",
                    text=str(case["customer_statement"]),
                    forbidden=list(case.get("forbidden_answer_elements", [])),
                    required=list(case.get("expected_answer_elements", [])),
                    expected_families=list(case["expected_problem_family_ids"]),
                    expected_solutions=list(case["expected_solution_pattern_ids"]),
                    label_status=str(case["label_status"]),
                )
            )
    return cases


def load_labels() -> dict[str, dict]:
    if not LABEL_FILE.is_file():
        return {}
    return {item["case_id"]: item for item in _read_json(LABEL_FILE)["labels"]}


def selection_text(selection) -> str:
    """Alle Texte, die aus der Auswahl beim Kunden sichtbar werden koennen."""

    parts: list[str] = []
    patterns = ([selection.primary] if selection.primary is not None else []) + list(
        selection.secondary
    )
    for pattern in patterns:
        parts.extend(
            [
                pattern.name,
                pattern.user_action,
                pattern.ai_task,
                pattern.visible_output,
                pattern.human_check,
                pattern.smallest_entry,
                pattern.later_stage,
                pattern.customer_language,
            ]
        )
    parts.extend(selection.required_prerequisites)
    parts.extend(selection.human_approval_boundaries)
    if selection.a0_recommendation:
        parts.append(selection.a0_recommendation)
    return " ".join(parts).casefold()


MAXIMUM_LLM_ATTEMPTS = 5
RATE_LIMIT_BACKOFF_SECONDS = 15.0


def _error_chain(error: BaseException) -> str:
    parts: list[str] = []
    current: BaseException | None = error
    while current is not None and len(parts) < 4:
        parts.append(f"{type(current).__name__}: {current}")
        current = current.__cause__
    return " <- ".join(parts)


def _is_rate_limited(error: BaseException) -> bool:
    current: BaseException | None = error
    while current is not None:
        name = type(current).__name__
        if name in {"RateLimitError", "APITimeoutError", "APIConnectionError"}:
            return True
        if getattr(current, "status_code", None) in {408, 429, 500, 502, 503}:
            return True
        current = current.__cause__
    return False


def _classify(case: EvaluationCase, classifier: str, catalog) -> dict:
    """Klassifiziert einen Fall im gewaehlten Modus."""

    if classifier == "llm":
        import time

        from app.llm_classification import classify_with_llm
        from app.openai_service import AIServiceError

        last_error: Exception | None = None
        for attempt in range(MAXIMUM_LLM_ATTEMPTS):
            try:
                outcome = classify_with_llm(case.text, catalog=catalog)
                return {
                    "families": outcome.problem_family_ids,
                    "gates": outcome.gates,
                    "classifier_error": None,
                }
            except AIServiceError as error:
                last_error = error
                if (
                    attempt + 1 < MAXIMUM_LLM_ATTEMPTS
                    and _is_rate_limited(error)
                ):
                    time.sleep(RATE_LIMIT_BACKOFF_SECONDS * (attempt + 1))
                    continue
                break
        return {
            "families": ["PF-01"],
            "gates": infer_decision_gates(case.text),
            "classifier_error": _error_chain(last_error)
            if last_error is not None
            else "unbekannt",
        }
    return {
        "families": classify_problem_families(case.text),
        "gates": infer_decision_gates(case.text),
        "classifier_error": None,
    }


def run(*, classifier: str = "keyword", workers: int = 1) -> dict:
    catalog = load_recommendation_catalog()
    cases = load_cases()
    labels = load_labels()

    if classifier == "llm" and workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            classifications = list(
                pool.map(lambda case: _classify(case, classifier, catalog), cases)
            )
    else:
        classifications = [_classify(case, classifier, catalog) for case in cases]

    results: list[dict] = []
    for case, classification in zip(cases, classifications):
        families = classification["families"]
        gates = classification["gates"]
        selection = select_recommendation(
            families, gates, catalog=catalog, confirmed_text=case.text
        )
        visible = selection_text(selection)
        label = labels.get(case.case_id, {})
        expected_families = case.expected_families or list(
            filter(None, [label.get("problem_family")])
        )
        expected_solutions = case.expected_solutions or list(
            filter(None, [label.get("solution_pattern")])
        )
        primary_id = selection.primary.solution_id if selection.primary else "A0"
        results.append(
            {
                "case_id": case.case_id,
                "source": case.source,
                "dataset": case.dataset,
                "text": case.text,
                "families": families,
                "gates": gates.model_dump(),
                "gate_assessments": [
                    item.model_dump() for item in selection.gate_assessments
                ],
                "primary": primary_id,
                "secondary": [item.solution_id for item in selection.secondary],
                "autonomy_level": selection.autonomy_level,
                "is_default_fallback": families == ["PF-01"],
                "classifier_error": classification["classifier_error"],
                "forbidden_hits": [
                    term for term in case.forbidden if term.casefold() in visible
                ],
                "expected_families": expected_families,
                "expected_solutions": expected_solutions,
                "label_status": (
                    case.label_status
                    if case.dataset == "batch_09"
                    else "confirmed"
                    if label.get("confirmed")
                    else "review_proposed"
                    if expected_families
                    else "unlabelled"
                ),
            }
        )
    return {
        "classifier": classifier,
        "case_count": len(results),
        "dataset_counts": dict(Counter(item["dataset"] for item in results)),
        "results": results,
    }


def report(payload: dict, *, show_misses: bool) -> None:
    results = payload["results"]
    if not results:
        print("Keine Evaluationsfaelle gefunden.")
        return

    print("=" * 66)
    print(
        "AI Start Map - Recommendation Evaluation "
        f"(Klassifikator: {payload.get('classifier', 'keyword')})"
    )
    print("=" * 66)
    print(f"Datensaetze: {payload['dataset_counts']}")

    def dataset_report(dataset: str, title: str) -> None:
        items = [item for item in results if item["dataset"] == dataset]
        count = len(items)
        if not count:
            return
        print(f"\n--- {title} ({count}) " + "-" * max(1, 43 - len(title)))
        for source, source_count in sorted(
            Counter(item["source"] for item in items).items()
        ):
            print(f"  {source}: {source_count}")
        errors = [item for item in items if item.get("classifier_error")]
        fallback = [item for item in items if item["is_default_fallback"]]
        print(f"Klassifikator-Fehler: {len(errors)}/{count}")
        print(
            f"Nur PF-01: {len(fallback)}/{count} = "
            f"{100 * len(fallback) / count:.0f}%"
        )
        reached = {family for item in items for family in item["families"]}
        never = sorted({f"PF-{index:02d}" for index in range(1, 13)} - reached)
        print(f"Nie erreichte Problemfamilien: {never or 'keine'}")
        primaries = Counter(item["primary"] for item in items)
        print(
            "Primaere Auswahl: "
            + ", ".join(f"{key}:{value}" for key, value in primaries.most_common())
        )
        autonomy = Counter(item["autonomy_level"] for item in items)
        print(f"Autonomiestufen: {dict(autonomy)}")
        violations = [item for item in items if item["forbidden_hits"]]
        print(f"Verbotene Inhalte in Auswahltexten: {len(violations)}/{count}")

        labelled = [item for item in items if item["expected_families"]]
        if labelled:
            family_top1 = sum(
                bool(item["families"])
                and item["families"][0] in item["expected_families"]
                for item in labelled
            )
            family_any = sum(
                bool(set(item["families"]) & set(item["expected_families"]))
                for item in labelled
            )
            solution_top1 = sum(
                item["primary"] in item["expected_solutions"] for item in labelled
            )
            print(
                f"Vorgeschlagene Labels ({len(labelled)}, nicht Ground Truth):\n"
                f"  PF Top-1 passend: {family_top1}/{len(labelled)} = "
                f"{100 * family_top1 / len(labelled):.0f}%\n"
                f"  PF irgendein Treffer: {family_any}/{len(labelled)} = "
                f"{100 * family_any / len(labelled):.0f}%\n"
                f"  SP Top-1 passend: {solution_top1}/{len(labelled)} = "
                f"{100 * solution_top1 / len(labelled):.0f}%"
            )
            if show_misses:
                for item in labelled:
                    if item["primary"] not in item["expected_solutions"]:
                        print(
                            f"  {item['case_id']}: erwartet {item['expected_solutions']}, "
                            f"bekommen {item['primary']} ({item['families']})"
                        )
        if show_misses and fallback:
            print("PF-01-Fälle:")
            for item in fallback:
                print(f"  {item['case_id']:<12} {item['text'][:80]}")

    dataset_report("legacy_91", "Alter Datensatz – Zielgruppe überwiegend historisch")
    dataset_report("batch_09", "Batch 09 – neue Zielgruppe, research_proposed")
    print("\nDie Kennzahlen beider Datensätze werden bewusst nicht gemittelt.\n")
    print()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, help="Ergebnis zusaetzlich als JSON ablegen")
    parser.add_argument("--show-misses", action="store_true", help="Einzelfaelle zeigen")
    parser.add_argument(
        "--classifier",
        choices=("keyword", "llm"),
        default="keyword",
        help="keyword = deterministische Baseline, llm = Structured-Output-Klassifikator",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Parallele Aufrufe im llm-Modus (Empfehlung: 8)",
    )
    arguments = parser.parse_args()

    payload = run(classifier=arguments.classifier, workers=arguments.workers)
    report(payload, show_misses=arguments.show_misses)
    if arguments.json:
        arguments.json.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"JSON geschrieben: {arguments.json}")


if __name__ == "__main__":
    main()
