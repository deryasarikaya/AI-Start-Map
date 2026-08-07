from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

import app.routes as routes
from app.agent_service import NextActionDecision
from app.openai_service import AIServiceError
from app.models import (
    Analysis,
    AnalysisSession,
    AutomationOpportunity,
    InterviewQuestion,
    ProcessOption,
)
from app.questions import INTRO_QUESTIONS, PROCESS_QUESTIONS
from app.rag_service import format_chunks_for_prompt, load_curated_chunks
from app.recommendation_service import DecisionGates
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
        software_rule="Pflichtangaben und Freigabestatus werden regelbasiert geprüft.",
        smallest_usable_version="Neue Anfragen in einem einheitlichen Entwurf erfassen.",
        not_automated=["Auftragsbestätigung", "Ausnahmeentscheidung"],
        autonomy_level="A2",
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
            output="Eine geprüfte Auftragsübersicht.",
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
    monkeypatch.setattr(routes, "_agent_pattern_context", lambda _query: ([], []))


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
    answers = {
        question["key"]: f"Konkrete Antwort für {question['key']}"
        for question in PROCESS_QUESTIONS
    }
    answers["actual_steps"] = (
        '["Anfrage aufnehmen", "Angaben prüfen", "Auftrag bestätigen"]'
    )
    return answers


def _complete_analysis(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    final_result: FinalAnalysisResult | None = None,
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
        lambda **_kwargs: final_result or _final_result(),
    )
    response = client.post(
        f"/sessions/{session_id}/process-details",
        data=_process_answers(),
        follow_redirects=False,
    )
    assert response.status_code == 303
    stored_follow_ups = list(
        database_session.scalars(
            select(InterviewQuestion.question_text).where(
                InterviewQuestion.session_id == session_id,
                InterviewQuestion.question_phase == "follow_up",
            )
        )
    )
    assert response.headers["location"] == f"/sessions/{session_id}/processing", stored_follow_ups
    assert client.get(response.headers["location"]).status_code == 200
    analysis_response = client.post(f"/sessions/{session_id}/analyze")
    assert analysis_response.status_code == 200
    assert analysis_response.json() == {
        "state": "complete",
        "redirect_url": f"/sessions/{session_id}/results",
    }
    return session_id


def test_saved_intro_answers_can_be_edited_before_analysis(
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
        "business_context": "Geänderter Betrieb",
        "problem_overview": "Geändertes Problem",
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
    assert selected[0].option_order == 2


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
                FollowUpQuestion(
                    question=f"Was fehlt heute bei Punkt {number}?",
                    issue_type="missing",
                )
                for number in range(1, 4)
            ]
        ),
    )
    monkeypatch.setattr(
        routes,
        "evaluate_readiness_and_next_action",
        lambda _state: NextActionDecision(
            next_action="ASK",
            reasoning="Testet das Fragebudget.",
            information_gap="other",
            analysis_allowed=True,
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
    assert keys == ["follow_up_1", "follow_up_2"]


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
    assert count == 2


def test_final_analysis_stores_one_primary_and_at_most_two_secondary_opportunities(
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


def test_primary_and_optional_secondary_opportunity_ranks_are_contiguous(
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


def test_analysis_can_store_only_the_primary_opportunity(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _final_result().model_copy(update={"secondary_opportunities": []})
    session_id = _complete_analysis(
        client,
        database_session,
        monkeypatch,
        final_result=result,
    )
    ranks = list(
        database_session.scalars(
            select(AutomationOpportunity.rank).where(
                AutomationOpportunity.session_id == session_id
            )
        )
    )
    assert ranks == [1]


def test_concise_output_and_presentation_metadata_are_stored(
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
    assert blueprints[1]["contract_version"] == "recommendation-v3"
    assert blueprints[1]["sample_output"] is not None
    assert blueprints[1]["implementation_path"]
    assert blueprints[2]["sample_output"] is None
    assert blueprints[3]["sample_output"] is None


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
        **_kwargs: object,
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
        follow_redirects=False,
    )
    assert response.headers["location"] == f"/sessions/{session_id}/processing"
    response = client.post(f"/sessions/{session_id}/analyze")
    assert response.status_code == 500
    assert "keine Teilergebnisse" in response.json()["message"]
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
        path.name for path in Path("knowledge/archive/curated").glob("*.md")
    }
    assert len(chunks) == 111
    assert {chunk.source_file for chunk in chunks} == curated_names
    assert all("content_origin" in chunk.metadata for chunk in chunks)
    assert all("is_primary_evidence" in chunk.metadata for chunk in chunks)


def test_model_prompt_context_contains_no_internal_metadata() -> None:
    prompt_context = "\n".join(format_chunks_for_prompt(load_curated_chunks()))
    forbidden_markers = (
        "M-01",
        "Testfall",
        "Chunk",
        "pattern_id",
        "content_origin",
        "original_massage_transcript.pdf",
        "massage_rag_corpus.md",
    )
    assert all(
        marker.casefold() not in prompt_context.casefold()
        for marker in forbidden_markers
    )


@pytest.mark.parametrize(
    ("field_name", "marker"),
    [
        ("process_summary", "Bekannter Testfall M-01"),
        ("process_summary", "Interner Fall RB03-C01-01"),
        ("as_is_steps", "Interner Chunk wurde verwendet"),
        ("core_bottleneck", "Ableitung aus pattern_id"),
        ("primary_recommendation", "Quelle content_origin"),
        ("sample_output", "Aus einem Referenzfall übernommen"),
    ],
)
def test_visible_analysis_fields_neutralize_internal_references(
    field_name: str,
    marker: str,
) -> None:
    payload = _final_result().model_dump()
    if field_name == "as_is_steps":
        payload[field_name][0] = marker
    elif field_name == "sample_output":
        payload[field_name]["fields"][0]["value"] = marker
    else:
        payload[field_name] = marker

    result = FinalAnalysisResult.model_validate(payload)
    if field_name == "as_is_steps":
        assert result.as_is_steps[0] == "noch offen"
    elif field_name == "sample_output":
        assert result.sample_output.fields[0].value == "noch offen"
    else:
        assert getattr(result, field_name) == "noch offen"
    assert result.visible_result
    assert any("internes" in item for item in result.uncertainties)


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
    def generate_clean_demo_analysis(**kwargs: object) -> FinalAnalysisResult:
        model_input = str(kwargs).casefold()
        for marker in ("m-01", "c-02", "c-10", "testfall", "content_origin"):
            assert marker not in model_input
        return _final_result()

    monkeypatch.setattr(
        routes,
        "generate_final_analysis",
        generate_clean_demo_analysis,
    )
    monkeypatch.setattr(
        routes,
        "classify_narrative",
        lambda _text: SimpleNamespace(
            problem_family_ids=["PF-01"],
            gates=DecisionGates(),
            method="test",
        ),
        raising=False,
    )
    response = client.get(f"/demo/{demo_slug}", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"].endswith("/processing")
    assert response.headers["location"] == "/processing"
    session_id = database_session.scalar(select(func.max(AnalysisSession.session_id)))
    assert session_id is not None
    assert database_session.get(AnalysisSession, session_id) is not None
    assert database_session.get(Analysis, session_id) is None
    processing_response = client.get(response.headers["location"])
    assert processing_response.status_code == 200
    analysis_response = client.post(f"/sessions/{session_id}/analyze")
    assert analysis_response.status_code == 200
    assert database_session.get(Analysis, session_id) is not None
    opportunity_count = database_session.scalar(
        select(func.count())
        .select_from(AutomationOpportunity)
        .where(AutomationOpportunity.session_id == session_id)
    )
    assert opportunity_count == 3
    result_response = client.get(f"/sessions/{session_id}/results")
    assert result_response.status_code == 200
    assert "Das ist der Engpass" in result_response.text
    visible_text = result_response.text.casefold()
    for marker in ("m-01", "testfall", "chunk", "pattern_id", "content_origin"):
        assert marker not in visible_text


def test_massage_demo_shows_service_failure_without_fixed_fallback(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_analysis(**_kwargs: object) -> FinalAnalysisResult:
        raise AIServiceError("vorübergehender Modelldienstfehler")

    monkeypatch.setattr(routes, "generate_final_analysis", fail_analysis)
    response = client.get("/demo/massage-salon", follow_redirects=False)
    assert response.status_code == 303

    analysis_response = client.post("/analyze")
    assert analysis_response.status_code == 503
    assert analysis_response.json()["state"] == "error"
    assert analysis_response.json()["message"] == (
        "Das hat gerade nicht geklappt. Versuch es bitte noch einmal."
    )
    assert client.get("/analysis-status").json()["state"] == "pending"

    session_id = database_session.scalar(select(func.max(AnalysisSession.session_id)))
    assert session_id is not None
    assert database_session.get(Analysis, session_id) is None


def test_stored_internal_reference_is_not_rendered(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id = _complete_analysis(client, database_session, monkeypatch)
    analysis = database_session.get(Analysis, session_id)
    assert analysis is not None
    analysis.process_summary = "Bekannter Testfall M-01: interner Inhalt"
    database_session.commit()

    response = client.get(f"/sessions/{session_id}/results")

    assert response.status_code == 409
    assert "M-01" not in response.text
    assert "Testfall" not in response.text


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
                            question="Welche Angabe verändert heute die Hauptempfehlung?",
                        issue_type="missing",
                    ),
                    FollowUpQuestion(
                            question="Was ist heute bei der Zuordnung noch ungeklärt?",
                        issue_type="critical_unknown",
                    ),
            ]
        ),
    )
    monkeypatch.setattr(
        routes,
        "evaluate_readiness_and_next_action",
        lambda _state: NextActionDecision(
            next_action="ASK",
            reasoning="Testet beantwortete und unbekannte Rückfragen.",
            information_gap="other",
            analysis_allowed=True,
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
    assert response.headers["location"] == f"/sessions/{session_id}/processing"
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
        "follow_up_2": "Ich weiß es gerade nicht",
    }
    assert database_session.get(Analysis, session_id) is None
    analysis_response = client.post(f"/sessions/{session_id}/analyze")
    assert analysis_response.status_code == 200
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
                    question="Wer prüft heute den fertigen Auftrag?",
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
    processing = client.get(f"/sessions/{session_id}/processing")
    assert processing.status_code == 200
    assert "Ich prüfe, welcher KI-Schritt zu deinem Ablauf passt." in processing.text
    client.post(f"/sessions/{session_id}/analyze")
    results = client.get(f"/sessions/{session_id}/results")
    assert results.status_code == 200
    assert "So klein fängst du an" in results.text
