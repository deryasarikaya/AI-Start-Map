from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

import app.routes as routes
from app.models import (
    Analysis,
    AnalysisSession,
    AutomationOpportunity,
    InterviewQuestion,
    ProcessOption,
)
from app.questions import INTRO_QUESTIONS, PROCESS_QUESTIONS
from app.rag_service import load_curated_chunks
from app.schemas import (
    AutomationBlueprint,
    AutomationOpportunityResult,
    FinalAnalysisResult,
    FollowUpQuestion,
    FollowUpResult,
    ProcessSuggestion,
    ProcessSuggestionResult,
)


def _start_and_answer_intro(client: TestClient) -> int:
    response = client.post("/start", follow_redirects=False)
    session_id = int(response.headers["location"].split("/")[2])
    response = client.post(
        f"/sessions/{session_id}/interview",
        data={
            "business_context": "Kleiner regionaler Handwerksbetrieb.",
            "problem_overview": "Auftragsdaten werden mehrfach übertragen.",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    return session_id


def _suggestions() -> ProcessSuggestionResult:
    return ProcessSuggestionResult(
        suggestions=[
            ProcessSuggestion(
                process_name="Kundenanfrage bis bestätigter Auftrag",
                start_event="Eine Kundenanfrage geht ein",
                end_event="Der Auftrag ist bestätigt",
                reason="Angaben werden heute mehrfach übertragen.",
            ),
            ProcessSuggestion(
                process_name="Auftrag bis vollständige Arbeitsunterlage",
                start_event="Ein Auftrag ist bestätigt",
                end_event="Die Arbeitsunterlage liegt vollständig vor",
                reason="Informationen liegen an mehreren Stellen.",
            ),
        ]
    )


def _final_result() -> FinalAnalysisResult:
    return FinalAnalysisResult(
        process_summary="Eine Anfrage wird aufgenommen, geprüft und bestätigt.",
        as_is_steps=["Anfrage aufnehmen", "Angaben prüfen", "Auftrag bestätigen"],
        core_bottleneck="Die Auftragsangaben werden mehrfach manuell übertragen.",
        uncertainties=["Die tatsächliche Fallzahl ist unbekannt."],
        opportunities=[
            AutomationOpportunityResult(
                rank=1,
                title="Auftragsangaben einmalig strukturiert erfassen",
                problem="Dieselben Angaben werden wiederholt übertragen.",
                recommendation="Eine gemeinsame strukturierte Erfassung vorbereiten.",
                benefit="Weniger Übertragungsfehler und ein klarer Ausgangspunkt.",
                human_approval="Der Auftrag wird vor der Bestätigung geprüft.",
                first_step="Pflichtangaben für einen Auftrag festlegen.",
            ),
            AutomationOpportunityResult(
                rank=2,
                title="Vollständigkeit vor der Bearbeitung prüfen",
                problem="Fehlende Angaben führen zu Rückfragen.",
                recommendation="Fehlende Pflichtangaben sichtbar markieren.",
                benefit="Rückfragen werden früher erkannt.",
                human_approval="Eine Person entscheidet über Ausnahmen.",
                first_step="Häufig fehlende Angaben sammeln.",
            ),
            AutomationOpportunityResult(
                rank=3,
                title="Geprüfte Arbeitsunterlage erzeugen",
                problem="Informationen werden für die Ausführung neu zusammengestellt.",
                recommendation="Aus freigegebenen Angaben einen Entwurf erstellen.",
                benefit="Die Übergabe wird nachvollziehbarer.",
                human_approval="Die Unterlage wird vor der Nutzung freigegeben.",
                first_step="Die heutige Arbeitsunterlage dokumentieren.",
            ),
        ],
        blueprint=AutomationBlueprint(
            objective="Auftragsangaben einmalig und vollständig erfassen.",
            trigger="Eine neue Kundenanfrage geht ein.",
            required_inputs=["Kundenanfrage", "festgelegte Pflichtangaben"],
            workflow_steps=[
                "Anfrage erfassen",
                "Pflichtangaben prüfen",
                "Prüfung durch eine Person anfordern",
            ],
            human_review_point="Vor der verbindlichen Auftragsbestätigung.",
            output="Ein geprüfter Auftragsdatensatz.",
            exceptions=["Unvollständige oder widersprüchliche Angaben"],
        ),
    )


@pytest.fixture(autouse=True)
def mock_retrieval(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        routes,
        "_retrieval_context",
        lambda _query, _phase: ["Vergleichsmuster ohne Nutzerfakten"],
    )


def _generate_options_and_select(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> int:
    session_id = _start_and_answer_intro(client)
    monkeypatch.setattr(
        routes,
        "generate_process_suggestions",
        lambda _answers, _knowledge: _suggestions(),
    )
    response = client.post(
        f"/sessions/{session_id}/process-options/generate",
        follow_redirects=False,
    )
    assert response.status_code == 303
    process_id = database_session.scalar(
        select(ProcessOption.process_id)
        .where(ProcessOption.session_id == session_id)
        .order_by(ProcessOption.option_order)
    )
    response = client.post(
        f"/sessions/{session_id}/process-options",
        data={"process_id": str(process_id)},
        follow_redirects=False,
    )
    assert response.status_code == 303
    return session_id


def _process_answers() -> dict[str, str]:
    return {
        question["key"]: f"Konkrete Antwort für {question['key']}"
        for question in PROCESS_QUESTIONS
    }


def _complete_analysis(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> int:
    session_id = _generate_options_and_select(
        client,
        database_session,
        monkeypatch,
    )
    monkeypatch.setattr(
        routes,
        "generate_follow_up_questions",
        lambda **_kwargs: FollowUpResult(questions=[]),
    )
    monkeypatch.setattr(
        routes,
        "generate_final_analysis",
        lambda **_kwargs: _final_result(),
    )
    response = client.post(
        f"/sessions/{session_id}/process-details",
        data=_process_answers(),
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == f"/sessions/{session_id}/results"
    return session_id


def test_saved_intro_answers_cannot_be_overwritten(
    client: TestClient,
    database_session: Session,
) -> None:
    session_id = _start_and_answer_intro(client)
    client.post(
        f"/sessions/{session_id}/interview",
        data={
            "business_context": "Geänderter Betrieb",
            "problem_overview": "Geändertes Problem",
        },
        follow_redirects=False,
    )
    stored = dict(
        database_session.execute(
            select(InterviewQuestion.question_key, InterviewQuestion.answer_text).where(
                InterviewQuestion.session_id == session_id,
                InterviewQuestion.question_phase == "context",
            )
        ).all()
    )
    assert stored == {
        "business_context": "Kleiner regionaler Handwerksbetrieb.",
        "problem_overview": "Auftragsdaten werden mehrfach übertragen.",
    }


def test_process_suggestions_are_stored(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id = _start_and_answer_intro(client)
    monkeypatch.setattr(
        routes,
        "generate_process_suggestions",
        lambda _answers, _knowledge: _suggestions(),
    )
    response = client.post(
        f"/sessions/{session_id}/process-options/generate",
        follow_redirects=False,
    )
    stored = list(
        database_session.scalars(
            select(ProcessOption)
            .where(ProcessOption.session_id == session_id)
            .order_by(ProcessOption.option_order)
        )
    )
    assert response.status_code == 303
    assert [option.process_name for option in stored] == [
        suggestion.process_name for suggestion in _suggestions().suggestions
    ]


def test_exactly_one_process_option_remains_selected(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id = _generate_options_and_select(
        client,
        database_session,
        monkeypatch,
    )
    second_id = database_session.scalar(
        select(ProcessOption.process_id).where(
            ProcessOption.session_id == session_id,
            ProcessOption.option_order == 2,
        )
    )
    client.post(
        f"/sessions/{session_id}/process-options",
        data={"process_id": str(second_id)},
        follow_redirects=False,
    )
    selected = list(
        database_session.scalars(
            select(ProcessOption).where(
                ProcessOption.session_id == session_id,
                ProcessOption.is_selected.is_(True),
            )
        )
    )
    assert len(selected) == 1
    assert selected[0].option_order == 1


def test_seven_process_questions_are_created_exactly_once(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id = _generate_options_and_select(
        client,
        database_session,
        monkeypatch,
    )
    selected_id = database_session.scalar(
        select(ProcessOption.process_id).where(
            ProcessOption.session_id == session_id,
            ProcessOption.is_selected.is_(True),
        )
    )
    client.post(
        f"/sessions/{session_id}/process-options",
        data={"process_id": str(selected_id)},
        follow_redirects=False,
    )
    keys = list(
        database_session.scalars(
            select(InterviewQuestion.question_key)
            .where(
                InterviewQuestion.session_id == session_id,
                InterviewQuestion.question_phase == "process",
            )
            .order_by(InterviewQuestion.question_order)
        )
    )
    assert keys == [question["key"] for question in PROCESS_QUESTIONS]


def test_no_old_v1_questions_are_created(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id = _generate_options_and_select(
        client,
        database_session,
        monkeypatch,
    )
    keys = set(
        database_session.scalars(
            select(InterviewQuestion.question_key).where(
                InterviewQuestion.session_id == session_id
            )
        )
    )
    expected = {
        question["key"] for question in INTRO_QUESTIONS + PROCESS_QUESTIONS
    }
    assert keys == expected


def test_dynamic_questions_receive_only_app_assigned_keys(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id = _generate_options_and_select(
        client,
        database_session,
        monkeypatch,
    )
    monkeypatch.setattr(
        routes,
        "generate_follow_up_questions",
        lambda **_kwargs: FollowUpResult(
            questions=[
                FollowUpQuestion(question=f"Rückfrage {number}?", issue_type="missing")
                for number in range(1, 4)
            ]
        ),
    )
    client.post(
        f"/sessions/{session_id}/process-details",
        data=_process_answers(),
        follow_redirects=False,
    )
    keys = list(
        database_session.scalars(
            select(InterviewQuestion.question_key)
            .where(
                InterviewQuestion.session_id == session_id,
                InterviewQuestion.question_phase == "follow_up",
            )
            .order_by(InterviewQuestion.question_order)
        )
    )
    assert keys == ["follow_up_1", "follow_up_2", "follow_up_3"]


def test_at_most_three_follow_up_questions_are_stored(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    test_dynamic_questions_receive_only_app_assigned_keys(
        client,
        database_session,
        monkeypatch,
    )
    count = database_session.scalar(
        select(func.count())
        .select_from(InterviewQuestion)
        .where(InterviewQuestion.question_phase == "follow_up")
    )
    assert count == 3


def test_final_analysis_stores_exactly_three_opportunities(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id = _complete_analysis(client, database_session, monkeypatch)
    count = database_session.scalar(
        select(func.count())
        .select_from(AutomationOpportunity)
        .where(AutomationOpportunity.session_id == session_id)
    )
    assert count == 3


def test_opportunity_ranks_are_one_two_and_three(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id = _complete_analysis(client, database_session, monkeypatch)
    ranks = list(
        database_session.scalars(
            select(AutomationOpportunity.rank)
            .where(AutomationOpportunity.session_id == session_id)
            .order_by(AutomationOpportunity.rank)
        )
    )
    assert ranks == [1, 2, 3]


def test_blueprint_is_stored_only_for_rank_one(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id = _complete_analysis(client, database_session, monkeypatch)
    blueprints = dict(
        database_session.execute(
            select(
                AutomationOpportunity.rank,
                AutomationOpportunity.blueprint_json,
            ).where(AutomationOpportunity.session_id == session_id)
        ).all()
    )
    assert blueprints[1] is not None
    assert blueprints[2] is None
    assert blueprints[3] is None


def test_failed_analysis_leaves_no_partial_results(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id = _generate_options_and_select(
        client,
        database_session,
        monkeypatch,
    )
    monkeypatch.setattr(
        routes,
        "generate_follow_up_questions",
        lambda **_kwargs: FollowUpResult(questions=[]),
    )
    monkeypatch.setattr(
        routes,
        "generate_final_analysis",
        lambda **_kwargs: _final_result(),
    )

    def fail_during_persistence(
        session: Session,
        current_session_id: int,
        _result: FinalAnalysisResult,
    ) -> None:
        session.add(
            Analysis(
                session_id=current_session_id,
                process_summary="Unvollständig",
                as_is_steps=["Ein Schritt"],
                core_bottleneck="Unvollständig",
                uncertainties=[],
            )
        )
        session.flush()
        raise RuntimeError("simulierter Speicherfehler")

    monkeypatch.setattr(routes, "_persist_final_analysis", fail_during_persistence)
    response = client.post(
        f"/sessions/{session_id}/process-details",
        data=_process_answers(),
    )
    assert response.status_code == 500
    assert "keine Teilergebnisse" in response.text
    assert database_session.get(Analysis, session_id) is None
    opportunity_count = database_session.scalar(
        select(func.count())
        .select_from(AutomationOpportunity)
        .where(AutomationOpportunity.session_id == session_id)
    )
    assert opportunity_count == 0


def test_evaluation_directory_is_not_indexed() -> None:
    chunks = load_curated_chunks()
    assert all("evaluation" not in chunk.source_file for chunk in chunks)


def test_rag_chunks_are_loaded_only_from_curated_files() -> None:
    chunks = load_curated_chunks()
    curated_names = {
        path.name for path in Path("knowledge/curated").glob("*.md")
    }
    assert len(chunks) == 111
    assert {chunk.source_file for chunk in chunks} == curated_names
    assert all("content_origin" in chunk.metadata for chunk in chunks)
    assert all("is_primary_evidence" in chunk.metadata for chunk in chunks)


@pytest.mark.parametrize(
    "demo_slug",
    ["massage-salon", "etsy-3d-print", "carpet-cleaning"],
)
def test_demo_route_creates_session_and_redirects_to_real_results(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    demo_slug: str,
) -> None:
    monkeypatch.setattr(
        routes,
        "generate_final_analysis",
        lambda **_kwargs: _final_result(),
    )
    response = client.get(f"/demo/{demo_slug}", follow_redirects=False)
    assert response.status_code == 303
    session_id = int(response.headers["location"].split("/")[2])
    assert database_session.get(AnalysisSession, session_id) is not None
    assert database_session.get(Analysis, session_id) is not None
    opportunity_count = database_session.scalar(
        select(func.count())
        .select_from(AutomationOpportunity)
        .where(AutomationOpportunity.session_id == session_id)
    )
    assert opportunity_count == 3
    result_response = client.get(response.headers["location"])
    assert result_response.status_code == 200
    assert "Kernengpass" in result_response.text


def test_follow_up_answers_complete_the_analysis(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id = _generate_options_and_select(
        client,
        database_session,
        monkeypatch,
    )
    monkeypatch.setattr(
        routes,
        "generate_follow_up_questions",
        lambda **_kwargs: FollowUpResult(
            questions=[
                FollowUpQuestion(
                    question="Wer prüft die Auftragsangaben?",
                    issue_type="missing",
                ),
                FollowUpQuestion(
                    question="Wie viele Aufträge entstehen pro Woche?",
                    issue_type="critical_unknown",
                ),
            ]
        ),
    )
    monkeypatch.setattr(
        routes,
        "generate_final_analysis",
        lambda **_kwargs: _final_result(),
    )
    details_response = client.post(
        f"/sessions/{session_id}/process-details",
        data=_process_answers(),
        follow_redirects=False,
    )
    assert details_response.headers["location"] == (
        f"/sessions/{session_id}/follow-ups"
    )
    response = client.post(
        f"/sessions/{session_id}/follow-ups",
        data={
            "follow_up_1": "Die Inhaberin prüft die Angaben.",
            "unknown_follow_up_2": "yes",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == f"/sessions/{session_id}/results"
    answers = dict(
        database_session.execute(
            select(InterviewQuestion.question_key, InterviewQuestion.answer_text).where(
                InterviewQuestion.session_id == session_id,
                InterviewQuestion.question_phase == "follow_up",
            )
        ).all()
    )
    assert answers == {
        "follow_up_1": "Die Inhaberin prüft die Angaben.",
        "follow_up_2": "Ich weiß es nicht",
    }
    assert database_session.get(Analysis, session_id) is not None


def test_all_workflow_pages_render_without_template_errors(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id = _start_and_answer_intro(client)
    monkeypatch.setattr(
        routes,
        "generate_process_suggestions",
        lambda _answers, _knowledge: _suggestions(),
    )
    client.post(
        f"/sessions/{session_id}/process-options/generate",
        follow_redirects=False,
    )
    assert client.get(f"/sessions/{session_id}/process-options").status_code == 200
    process_id = database_session.scalar(
        select(ProcessOption.process_id)
        .where(ProcessOption.session_id == session_id)
        .order_by(ProcessOption.option_order)
    )
    client.post(
        f"/sessions/{session_id}/process-options",
        data={"process_id": str(process_id)},
        follow_redirects=False,
    )
    assert client.get(f"/sessions/{session_id}/process-details").status_code == 200
    monkeypatch.setattr(
        routes,
        "generate_follow_up_questions",
        lambda **_kwargs: FollowUpResult(
            questions=[
                FollowUpQuestion(
                    question="Wer prüft den fertigen Auftrag?",
                    issue_type="missing",
                )
            ]
        ),
    )
    client.post(
        f"/sessions/{session_id}/process-details",
        data=_process_answers(),
        follow_redirects=False,
    )
    assert client.get(f"/sessions/{session_id}/follow-ups").status_code == 200
    monkeypatch.setattr(
        routes,
        "generate_final_analysis",
        lambda **_kwargs: _final_result(),
    )
    client.post(
        f"/sessions/{session_id}/follow-ups",
        data={"follow_up_1": "Die Inhaberin prüft den Auftrag."},
        follow_redirects=False,
    )
    results = client.get(f"/sessions/{session_id}/results")
    assert results.status_code == 200
    assert "Blueprint für Chance 1" in results.text
