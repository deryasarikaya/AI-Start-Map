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
BATCH_DIRECTORY = ROOT_DIRECTORY / "knowledge" / "research_batches"
LABEL_FILE = EVALUATION_DIRECTORY / "expected_labels.json"


@dataclass
class EvaluationCase:
    case_id: str
    source: str
    text: str
    forbidden: list[str] = field(default_factory=list)
    required: list[str] = field(default_factory=list)
    expected_verdict: str = ""


def _read_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def load_cases() -> list[EvaluationCase]:
    """Sammelt alle Evaluationsfaelle aus den vier vorhandenen Quellen."""

    cases: list[EvaluationCase] = []

    path = EVALUATION_DIRECTORY / "evaluation_cases.json"
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

    path = BATCH_DIRECTORY / "batch_03_diagnostic_depth" / "06_evaluation_cases.json"
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

    path = BATCH_DIRECTORY / "batch_04_agentic_interview" / "09_evaluation_cases.json"
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

    path = (
        BATCH_DIRECTORY
        / "batch_07_failure_and_overautomation"
        / "02_evaluation_cases.json"
    )
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
    return cases


def load_labels() -> dict[str, dict]:
    if not LABEL_FILE.is_file():
        return {}
    return {item["case_id"]: item for item in _read_json(LABEL_FILE)["labels"]}


def selection_text(selection) -> str:
    """Alle Texte, die aus der Auswahl beim Kunden sichtbar werden koennen."""

    parts: list[str] = []
    for pattern in [selection.primary, *selection.secondary]:
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
        selection = select_recommendation(families, gates, catalog=catalog)
        visible = selection_text(selection)
        label = labels.get(case.case_id, {})
        results.append(
            {
                "case_id": case.case_id,
                "source": case.source,
                "text": case.text,
                "families": families,
                "gates": gates.model_dump(),
                "primary": selection.primary.solution_id,
                "secondary": [item.solution_id for item in selection.secondary],
                "autonomy_max": selection.primary.autonomy_level_max,
                "is_default_fallback": families == ["PF-01"],
                "classifier_error": classification["classifier_error"],
                "forbidden_hits": [
                    term for term in case.forbidden if term.casefold() in visible
                ],
                "expected_family": label.get("problem_family"),
                "expected_solution": label.get("solution_pattern"),
                "label_confirmed": bool(label.get("confirmed")),
            }
        )
    return {
        "classifier": classifier,
        "case_count": len(results),
        "results": results,
    }


def report(payload: dict, *, show_misses: bool) -> None:
    results = payload["results"]
    total = len(results)
    if not total:
        print("Keine Evaluationsfaelle gefunden.")
        return

    print("=" * 66)
    print(
        "AI Start Map - Recommendation Evaluation "
        f"(Klassifikator: {payload.get('classifier', 'keyword')})"
    )
    print("=" * 66)
    print(f"Faelle gesamt: {total}")
    classifier_errors = [
        item for item in results if item.get("classifier_error")
    ]
    if classifier_errors:
        print(
            f"Klassifikator-Fehler (als PF-01 gezaehlt): "
            f"{len(classifier_errors)}/{total}"
        )
    for source, count in sorted(Counter(item["source"] for item in results).items()):
        print(f"  {source}: {count}")

    print("\n--- Labelfreie Kennzahlen -------------------------------------")
    fallback = [item for item in results if item["is_default_fallback"]]
    print(
        f"Nur PF-01 (Default-Fallback): {len(fallback)}/{total} "
        f"= {100 * len(fallback) / total:.0f}%"
    )

    reached = {family for item in results for family in item["families"]}
    never = sorted({f"PF-{index:02d}" for index in range(1, 13)} - reached)
    print(f"Nie erreichte Problemfamilien: {never or 'keine'}")

    primaries = Counter(item["primary"] for item in results)
    print(f"Verschiedene primaere Solutions: {len(primaries)}/10")
    print("  " + ", ".join(f"{key}:{value}" for key, value in primaries.most_common()))

    print("\nGate-Streuung (wie oft welcher Wert):")
    gate_names = [
        "transaction_anchor",
        "channel_suitability",
        "process_data_maturity",
        "error_impact",
        "rule_stability",
        "human_approval",
    ]
    for name in gate_names:
        counter = Counter(item["gates"][name] for item in results)
        dominant, dominant_count = counter.most_common(1)[0]
        print(
            f"  {name:<22} {dict(counter)}   "
            f"-> {100 * dominant_count / total:.0f}% auf '{dominant}'"
        )

    violations = [item for item in results if item["forbidden_hits"]]
    print(
        f"\nVerbotene Inhalte in der Auswahl: {len(violations)}/{total} Faelle"
    )
    for item in violations[:10]:
        print(f"  {item['case_id']:<12} {item['forbidden_hits']}")

    confirmed = [item for item in results if item["label_confirmed"]]
    proposed = [
        item
        for item in results
        if item["expected_family"] and not item["label_confirmed"]
    ]

    def accuracy(items: list[dict], title: str) -> None:
        count = len(items)
        if not count:
            return
        family_top1 = sum(
            1
            for item in items
            if item["families"] and item["families"][0] == item["expected_family"]
        )
        family_any = sum(
            1 for item in items if item["expected_family"] in item["families"]
        )
        solution_top1 = sum(
            1 for item in items if item["expected_solution"] == item["primary"]
        )
        print(f"{title}: {count} Faelle")
        print(f"  PF Top-1 korrekt:      {family_top1}/{count} = {100 * family_top1 / count:.0f}%")
        print(f"  PF irgendwo getroffen: {family_any}/{count} = {100 * family_any / count:.0f}%")
        print(f"  SP Top-1 korrekt:      {solution_top1}/{count} = {100 * solution_top1 / count:.0f}%")
        if show_misses:
            print("  Fehltreffer:")
            for item in items:
                if item["expected_solution"] != item["primary"]:
                    print(
                        f"    {item['case_id']:<12} erwartet {item['expected_solution']} "
                        f"({item['expected_family']}), bekommen {item['primary']} "
                        f"({item['families']})"
                    )
                    print(f"      {item['text'][:88]}")

    print("\n--- Trefferquoten --------------------------------------------")
    if not confirmed and not proposed:
        print(
            "Keine Labels vorhanden. Trage erwartete Problemfamilie und Solution\n"
            "Pattern in knowledge/evaluation/expected_labels.json ein."
        )
    accuracy(confirmed, "Bestaetigte Labels (verbindlich)")
    if proposed:
        if confirmed:
            print()
        accuracy(proposed, "Vorgeschlagene Labels (noch nicht bestaetigt)")
        print(
            "\n  Hinweis: Diese Labels sind ein Vorschlag und keine bestaetigte\n"
            "  Wahrheit. Nach fachlicher Pruefung \"confirmed\": true setzen."
        )

    if show_misses:
        print("\n--- Alle Default-Fallback-Faelle ------------------------------")
        for item in fallback:
            print(f"  {item['case_id']:<12} {item['text'][:80]}")
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
