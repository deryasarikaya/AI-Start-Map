"""Der Demopfad.

`/demo/{slug}` legt aus einem gespeicherten Evaluationsfall eine fertige
Sitzung an - für Vorführungen, nicht für Nutzer. Unverändert aus
`routes.py` hierher verschoben.
"""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import AnalysisSession, InterviewQuestion, ProcessOption
from app.questions import INTRO_QUESTIONS, PROCESS_QUESTIONS
from app.rag_service import RagConfigurationError

ROOT_DIRECTORY = Path(__file__).resolve().parents[2]
EVALUATION_FILE = ROOT_DIRECTORY / "knowledge" / "evaluation" / "cases_ten_kmu.json"
DEMO_EVALUATION_IDS = {
    "massage-salon": "EVAL-M-01",
    "etsy-3d-print": "EVAL-C-02",
    "carpet-cleaning": "EVAL-C-10",
}


def load_evaluation_case(evaluation_id: str) -> dict[str, object]:
    """Holt einen Evaluationsfall aus der Falldatei."""

    if not EVALUATION_FILE.is_file():
        raise RagConfigurationError("Die vorbereiteten Demo-Daten wurden nicht gefunden.")
    try:
        evaluation_data = json.loads(EVALUATION_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        raise RagConfigurationError(
            "Die vorbereiteten Demo-Daten konnten nicht gelesen werden."
        ) from error
    evaluation_case = next(
        (
            case
            for case in evaluation_data.get("cases", [])
            if case.get("evaluation_id") == evaluation_id
        ),
        None,
    )
    if evaluation_case is None:
        raise RagConfigurationError("Die vorbereiteten Demo-Daten sind unvollständig.")
    return evaluation_case


def _list_text(value: object, prefix: str) -> str:
    """Macht aus einer Liste einen Satz, oder 'Unbekannt' wenn sie leer ist."""

    if not isinstance(value, list) or not value:
        return "Unbekannt"
    items = [str(item).strip() for item in value if str(item).strip()]
    if not items:
        return "Unbekannt"
    return f"{prefix}: " + "; ".join(items)


def create_demo_session(
    database_session: Session,
    evaluation_case: dict[str, object],
) -> int:
    """Legt aus einem Evaluationsfall eine fertig ausgefüllte Sitzung an.

    Alles, was der Fall nicht hergibt, steht als 'Unbekannt' drin - der
    Demofall soll nicht mehr wissen als ein echter Kunde.
    """

    process_name = str(
        evaluation_case.get("expected_core_process") or "Unbekannter Prozess"
    ).strip()
    bottleneck = str(
        evaluation_case.get("expected_core_bottleneck") or "Unbekannt"
    ).strip()
    clarification_topics = _list_text(
        evaluation_case.get("required_questions"),
        "Noch zu klären",
    )
    approval_gates = _list_text(
        evaluation_case.get("human_approval_gates"),
        "Menschliche Prüfungen",
    )
    forbidden_actions = _list_text(
        evaluation_case.get("forbidden_recommendations"),
        "Nicht autonom ausführen",
    )
    process_answers = {
        "process_boundary": "Unbekannt",
        "actual_steps": "Unbekannt",
        "business_object_and_result": (
            "Weitere Angaben zum Gegenstand und Ergebnis sind unbekannt."
        ),
        "roles_systems_and_handoffs": "Unbekannt",
        "volume_time_and_impact": "Unbekannt",
        "rules_and_exceptions": clarification_topics,
        "approval_and_success": f"{approval_gates}. {forbidden_actions}.",
    }
    analysis_session = AnalysisSession()
    database_session.add(analysis_session)
    database_session.flush()
    context_answers = {
        "business_context": "Weitere Unternehmensangaben sind unbekannt.",
        "problem_overview": bottleneck,
    }
    database_session.add_all(
        [
            InterviewQuestion(
                session_id=analysis_session.session_id,
                question_phase=question["phase"],
                question_order=question["order"],
                question_key=question["key"],
                question_text=question["text"],
                answer_text=context_answers[question["key"]],
            )
            for question in INTRO_QUESTIONS
        ]
    )
    database_session.add(
        ProcessOption(
            session_id=analysis_session.session_id,
            option_order=1,
            process_name=process_name,
            start_event="Unbekannt",
            end_event="Unbekannt",
            reason=bottleneck,
            is_selected=True,
        )
    )
    database_session.add_all(
        [
            InterviewQuestion(
                session_id=analysis_session.session_id,
                question_phase=question["phase"],
                question_order=question["order"],
                question_key=question["key"],
                question_text=question["text"],
                answer_text=process_answers[question["key"]],
            )
            for question in PROCESS_QUESTIONS
        ]
    )
    database_session.commit()
    return analysis_session.session_id
