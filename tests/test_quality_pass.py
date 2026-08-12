from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

import app.openai_service as openai_service
import app.routes as routes
from app.agent_service import NextActionDecision
from app.models import Analysis, AutomationOpportunity, InterviewQuestion, ProcessOption
from app.questions import PROCESS_QUESTIONS
from app.schemas import (
    AutomationBlueprint,
    AutomationOpportunityResult,
    FinalAnalysisResult,
    FollowUpQuestion,
    FollowUpResult,
    ProcessBoundaryResult,
    ProcessSuggestion,
    ProcessSuggestionResult,
)
from tests.conftest import spec_payload


@pytest.fixture(autouse=True)
def mock_retrieval(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        routes,
        "_retrieval_context",
        lambda _query, _phase: ["Internes Vergleichswissen ohne Nutzerfakten"],
    )
    monkeypatch.setattr(routes, "_agent_pattern_context", lambda _query: ([], []))


def _start_with_context(
    client: TestClient,
    business_context: str,
    problem_overview: str,
) -> int:
    response = client.post("/start", follow_redirects=False)
    session_id = int(response.headers["location"].split("/")[2])
    response = client.post(
        f"/sessions/{session_id}/interview",
        data={
            "business_context": business_context,
            "problem_overview": problem_overview,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    return session_id


def _select_suggested_process(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    session_id: int,
    suggestion: ProcessSuggestion,
) -> None:
    monkeypatch.setattr(
        routes,
        "generate_process_suggestions",
        lambda _answers, _knowledge: ProcessSuggestionResult(
            suggestions=[suggestion]
        ),
    )
    client.post(
        f"/sessions/{session_id}/process-options/generate",
        follow_redirects=False,
    )
    process_id = database_session.scalar(
        select(ProcessOption.process_id).where(
            ProcessOption.session_id == session_id
        )
    )
    response = client.post(
        f"/sessions/{session_id}/process-options",
        data={"process_id": str(process_id)},
        follow_redirects=False,
    )
    assert response.headers["location"] == f"/sessions/{session_id}/process-details"


def _shoe_answers() -> dict[str, str]:
    return {
        "process_boundary": (
            "Der Ablauf beginnt mit der Annahme eines Reparaturgegenstands und "
            "endet mit der Abholung durch den Kunden."
        ),
        "actual_steps": (
            "Der Gegenstand wird angenommen. Angaben kommen auf einen Papierzettel "
            "und in ein Heft. Eine lose Nummer wird zugeordnet. Danach wird repariert. "
            "Kunden fragen häufig nach dem Status. Fertige Aufträge werden nicht "
            "immer mitgeteilt und später abgeholt."
        ),
        "business_object_and_result": (
            "Ein Reparaturgegenstand mit Kundenangaben und Arbeitsauftrag; am Ende "
            "liegt der fertig reparierte Gegenstand bereit."
        ),
        "roles_systems_and_handoffs": (
            "Der Inhaber nimmt an, notiert auf Papierzettel und im Heft und führt "
            "die Reparatur aus."
        ),
        "volume_time_and_impact": (
            "Die genaue Menge ist unbekannt. Statusfragen unterbrechen die Arbeit."
        ),
        "rules_and_exceptions": (
            "Weitere Schäden werden mit dem Kunden geklärt; der heutige Ablauf bei "
            "Nichterreichbarkeit ist nicht eindeutig."
        ),
        "approval_and_success": (
            "Zusatzarbeiten und Preise bestätigt der Inhaber erst nach Zustimmung "
            "des Kunden."
        ),
    }


def _shoe_result() -> FinalAnalysisResult:
    """Fallbezogener Ist-Ablauf auf dem kanonischen Ergebnisvertrag."""

    return FinalAnalysisResult.model_validate(
        spec_payload(
            process_summary=(
            "Reparaturgegenstände werden mit handschriftlichen Angaben angenommen, "
            "über lose Nummern zugeordnet, repariert und zur Abholung bereitgelegt."
        ),
            as_is_steps=[
            "Reparaturgegenstand und Kundenangaben annehmen.",
            "Arbeitsauftrag auf einem Papierzettel und im Heft notieren.",
            "Eine lose Nummer dem Gegenstand zuordnen.",
            "Reparatur ausführen und den fertigen Auftrag bereitlegen.",
            "Statusfragen beantworten; die Fertigmeldung erfolgt nicht immer.",
            "Fertigen Gegenstand an den Kunden übergeben.",
        ],
            core_bottleneck=(
            "Auftragsangaben, Zuordnung und Bearbeitungsstand liegen nicht an einer "
            "gemeinsamen verlässlichen Stelle."
        ),
            not_automated=["Preisfreigabe", "Zusatzarbeit", "Fertigstellung", "Herausgabe"],
            autonomy_level="A2",
            uncertainties=[
            "Die Zahl der gleichzeitig offenen Reparaturaufträge ist unbekannt.",
            "Der heutige Ablauf bei nicht erreichbaren Kunden ist nicht eindeutig.",
        ],
        )
    )
def _carpentry_answers() -> dict[str, str]:
    return {
        "process_boundary": (
            "Der Ablauf beginnt mit dem freigegebenen Auftrag und endet mit den "
            "geprüften Unterlagen für die Arbeitsvorbereitung."
        ),
        "actual_steps": (
            "Maße, Zeichnungen und Änderungen kommen per E-Mail, Nachricht und "
            "Gespräch. Die Angaben werden für die Arbeitsvorbereitung zusammengesucht."
        ),
        "business_object_and_result": (
            "Ein freigegebener Auftrag mit aktuellen Maßen, Zeichnungen und "
            "Änderungen; am Ende liegen geprüfte Arbeitsunterlagen vor."
        ),
        "roles_systems_and_handoffs": (
            "Büro, Kunde und Werkstatt tauschen Angaben über mehrere Kanäle aus."
        ),
        "volume_time_and_impact": (
            "Der Aufwand schwankt. Veraltete Angaben können Nacharbeit verursachen."
        ),
        "rules_and_exceptions": (
            "Änderungen werden je nach Auftrag geklärt; technische Entscheidungen "
            "brauchen Erfahrung."
        ),
        "approval_and_success": (
            "Technische und konstruktive Freigaben erfolgen immer durch eine Person."
        ),
    }


def _carpentry_result() -> FinalAnalysisResult:
    """Fallbezogener Ist-Ablauf auf dem kanonischen Ergebnisvertrag."""

    return FinalAnalysisResult.model_validate(
        spec_payload(
            process_summary=(
            "Nach der Auftragsfreigabe werden Maße, Zeichnungen und Änderungen aus "
            "mehreren Kanälen für die Arbeitsvorbereitung zusammengeführt."
        ),
            as_is_steps=[
            "Freigegebenen Auftrag übernehmen.",
            "Maße, Zeichnungen und Änderungen aus mehreren Kanälen zusammensuchen.",
            "Angaben für die Arbeitsvorbereitung zusammenstellen.",
            "Technische Unterlagen durch eine Person prüfen und freigeben.",
        ],
            core_bottleneck=(
            "Aktuelle und veraltete Informationen sind über mehrere Kanäle verteilt."
        ),
            not_automated=["Technische Bewertung", "Konstruktive Freigabe"],
            bleibt_bei_dir=(
                "Du behältst die technische oder konstruktive Freigabe. Die KI "
                "bereitet nur vor, entschieden wird von dir."
            ),
            autonomy_level="A2",
            uncertainties=[
            "Es ist unbekannt, wie Änderungen heute eindeutig als aktuell markiert werden."
        ],
        )
    )
def _run_quality_case(
    *,
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    business_context: str,
    problem_overview: str,
    suggestion: ProcessSuggestion,
    answers: dict[str, str],
    follow_up: FollowUpQuestion,
    follow_up_answer: str,
    final_result: FinalAnalysisResult,
) -> tuple[int, str]:
    session_id = _start_with_context(client, business_context, problem_overview)
    _select_suggested_process(
        client,
        database_session,
        monkeypatch,
        session_id,
        suggestion,
    )
    monkeypatch.setattr(
        routes,
        "generate_follow_up_questions",
        lambda **_kwargs: FollowUpResult(questions=[follow_up]),
    )
    response = client.post(
        f"/sessions/{session_id}/process-details",
        data=answers,
        follow_redirects=False,
    )
    assert response.headers["location"] == f"/sessions/{session_id}/follow-ups"
    monkeypatch.setattr(
        routes,
        "generate_final_analysis",
        lambda **_kwargs: final_result,
    )
    response = client.post(
        f"/sessions/{session_id}/follow-ups",
        data={"follow_up_1": follow_up_answer},
        follow_redirects=False,
    )
    assert response.headers["location"] == f"/sessions/{session_id}/processing"
    processing = client.get(response.headers["location"])
    assert processing.status_code == 200
    assert "Ich prüfe, welcher KI-Schritt zu deinem Ablauf passt." in processing.text
    status_before = client.get(f"/sessions/{session_id}/analysis-status").json()
    assert status_before["state"] == "pending"
    analyze = client.post(f"/sessions/{session_id}/analyze")
    assert analyze.status_code == 200
    assert analyze.json()["state"] == "complete"
    result_page = client.get(f"/sessions/{session_id}/results")
    assert result_page.status_code == 200
    return session_id, result_page.text


def test_custom_process_uses_one_description_and_confirmation(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id = _start_with_context(
        client,
        "Ein kleiner Reparaturbetrieb.",
        "Aufträge sind schwer nachzuverfolgen.",
    )
    _select_suggested_process(
        client,
        database_session,
        monkeypatch,
        session_id,
        ProcessSuggestion(
            process_name="Anfrage bis Angebot",
            start_event="Eine Anfrage kommt an",
            end_event="Das Angebot ist versendet",
            reason="Anfragen werden mehrfach bearbeitet.",
        ),
    )
    options_page = client.get(f"/sessions/{session_id}/process-options")
    assert "Nichts Passendes dabei?" in options_page.text
    assert "custom_process_name" not in options_page.text
    assert "custom_start_event" not in options_page.text
    assert "custom_end_event" not in options_page.text
    monkeypatch.setattr(
        routes,
        "generate_custom_process_boundary",
        lambda **_kwargs: ProcessBoundaryResult(
            process_name="Reparaturannahme bis Abholung",
            start_event="Ein Reparaturgegenstand wird angenommen",
            end_event="Der Kunde holt den fertigen Gegenstand ab",
        ),
    )
    response = client.post(
        f"/sessions/{session_id}/process-options/custom",
        data={
            "custom_process_description": (
                "Von der Annahme einer Reparatur bis der Kunde sie abholt."
            )
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    confirmation = client.get(response.headers["location"])
    assert confirmation.status_code == 200
    assert "Passt dieser erkannte Ablauf?" in confirmation.text
    assert "Reparaturannahme bis Abholung" in confirmation.text
    custom_process_id = int(response.headers["location"].split("/")[-1])
    monkeypatch.setattr(
        routes,
        "generate_custom_process_boundary",
        lambda **_kwargs: ProcessBoundaryResult(
            process_name="Reparaturannahme bis fertige Übergabe",
            start_event="Der Gegenstand wird im Betrieb abgegeben",
            end_event="Der fertige Gegenstand wird übergeben",
        ),
    )
    response = client.post(
        f"/sessions/{session_id}/process-options/custom",
        data={
            "custom_process_id": str(custom_process_id),
            "custom_process_description": (
                "Von der Abgabe im Betrieb bis zur fertigen Übergabe."
            ),
        },
        follow_redirects=False,
    )
    assert response.headers["location"].endswith(f"/{custom_process_id}")
    custom_count = database_session.scalar(
        select(func.count())
        .select_from(ProcessOption)
        .where(ProcessOption.session_id == session_id)
    )
    assert custom_count == 2
    response = client.post(
        f"/sessions/{session_id}/process-options",
        data={"process_id": str(custom_process_id)},
        follow_redirects=False,
    )
    assert response.headers["location"] == f"/sessions/{session_id}/process-details"
    assert database_session.scalar(
        select(func.count())
        .select_from(InterviewQuestion)
        .where(
            InterviewQuestion.session_id == session_id,
            InterviewQuestion.question_phase == "process",
        )
    ) == 7


def test_follow_up_validation_rejects_solutions_rules_and_new_risks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(ValidationError):
        FollowUpQuestion(
            question=(
                "Welche verbindliche Regel sollte heute gelten, zum Beispiel nach "
                "drei Tagen selbst entscheiden?"
            ),
            issue_type="critical_unknown",
        )
    speculative = FollowUpResult(
        questions=[
            FollowUpQuestion(
                question="Was passiert heute bei einer Falschübergabe?",
                issue_type="critical_unknown",
            )
        ]
    )
    monkeypatch.setattr(
        openai_service,
        "_parse_structured_output",
        lambda **_kwargs: speculative,
    )
    result = openai_service.generate_follow_up_questions(
        answers={"actual_steps": "Auftrag wird im Heft notiert."},
        selected_process={
            "process_name": "Reparaturannahme bis Abholung",
            "start_event": "Gegenstand wird angenommen",
            "end_event": "Gegenstand wird abgeholt",
        },
        knowledge_chunks=[],
    )
    assert result.questions == []


def test_final_grounding_removes_unsupported_current_process_detail() -> None:
    result = _shoe_result()
    result.as_is_steps.insert(1, "Der Schuh wird heute fotografiert.")
    result.as_is_problem_step_indexes = [1, 2]

    openai_service._validate_final_grounding(
        result,
        answers={"actual_steps": "Der Schuh kommt mit einem Papierzettel ins Regal."},
        selected_process={
            "process_name": "Reparaturannahme bis Abholung",
            "start_event": "Ein Schuh wird angenommen",
            "end_event": "Der Schuh wird abgeholt",
        },
    )

    assert all("foto" not in step.casefold() for step in result.as_is_steps)
    assert result.as_is_problem_step_indexes == [1]


def test_shoe_repair_quality_flow_contains_only_grounded_current_steps(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id, result_text = _run_quality_case(
        client=client,
        database_session=database_session,
        monkeypatch=monkeypatch,
        business_context="Ein Schuhmacherbetrieb mit einem Inhaber.",
        problem_overview=(
            "Papierzettel, Heft und lose Nummern erschweren den Status. Kunden fragen "
            "nach und fertige Aufträge werden nicht immer kommuniziert."
        ),
        suggestion=ProcessSuggestion(
            process_name="Reparaturannahme bis Abholung",
            start_event="Ein Reparaturgegenstand wird angenommen",
            end_event="Der Kunde holt den fertigen Gegenstand ab",
            reason="Zuordnung, Status und Fertigmeldung sind nicht verlässlich zentral.",
        ),
        answers=_shoe_answers(),
        follow_up=FollowUpQuestion(
            question=(
                "Was passiert heute, wenn während der Reparatur weitere Schäden "
                "entdeckt werden und der Kunde nicht erreichbar ist?"
            ),
            issue_type="critical_unknown",
        ),
        follow_up_answer="Die Reparatur wartet heute, bis der Kunde erreicht wird.",
        final_result=_shoe_result(),
    )
    lower_text = result_text.casefold()
    for forbidden in (
        "foto",
        "ausweis",
        "falschübergabe",
        "abholnummer",
        "unterschrift",
        "ringordner",
        "m-01",
        "intake",
        "mapping",
    ):
        assert forbidden not in lower_text
    assert "Beim Vorbereiten schaust du jedes Mal in mehreren Chats" in result_text
    assert "Kunden nach Fertigmeldung benachrichtigen" not in result_text
    assert "Nach der Einrichtung" in result_text
    assert database_session.scalar(
        select(func.count())
        .select_from(AutomationOpportunity)
        .where(AutomationOpportunity.session_id == session_id)
    ) == 1


def test_carpentry_quality_flow_keeps_technical_approval_human(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id, result_text = _run_quality_case(
        client=client,
        database_session=database_session,
        monkeypatch=monkeypatch,
        business_context="Eine kleine Schreinerei mit Büro und Werkstatt.",
        problem_overview=(
            "Maße, Zeichnungen und Änderungen kommen über mehrere Kanäle. Veraltete "
            "Informationen können in die Arbeitsvorbereitung gelangen."
        ),
        suggestion=ProcessSuggestion(
            process_name="Auftragsfreigabe bis Arbeitsvorbereitung",
            start_event="Ein Auftrag ist freigegeben",
            end_event="Geprüfte Arbeitsunterlagen liegen vor",
            reason="Aktuelle Informationen sind über mehrere Kanäle verteilt.",
        ),
        answers=_carpentry_answers(),
        follow_up=FollowUpQuestion(
            question="Wie wird heute erkennbar, welche Änderung aktuell freigegeben ist?",
            issue_type="missing",
        ),
        follow_up_answer=(
            "Eine fachkundige Person bestätigt heute die gültige Änderung."
        ),
        final_result=_carpentry_result(),
    )
    lower_text = result_text.casefold()
    for forbidden in (
        "reparaturgegenstand",
        "schuh",
        "m-01",
        "automatische technische freigabe",
        "intake-kit",
        "audit-track",
        "wip",
    ):
        assert forbidden not in lower_text
    assert "Das bleibt bei dir" in result_text
    assert "technische oder konstruktive Freigabe" in result_text
    blueprints = dict(
        database_session.execute(
            select(
                AutomationOpportunity.rank,
                AutomationOpportunity.blueprint_json,
            ).where(AutomationOpportunity.session_id == session_id)
        ).all()
    )
    human_approval = database_session.scalar(
        select(AutomationOpportunity.human_approval).where(
            AutomationOpportunity.session_id == session_id,
            AutomationOpportunity.rank == 1,
        )
    )
    assert human_approval is not None
    assert "technische oder konstruktive Freigabe" in human_approval
    # Genau eine Empfehlung, und sie traegt die Ergebnisart des Falls.
    assert set(blueprints) == {1}
    assert blueprints[1]["contract_version"] == "ergebnis-spec-v5"
    assert blueprints[1]["ergebnis_art"]


def test_unmentioned_current_fact_is_removed_but_solution_uncertainty_remains() -> None:
    payload = _shoe_result().model_dump()
    payload["as_is_steps"].append("Bei der Abholung werden Ausweisdaten geprüft.")
    unsafe_result = FinalAnalysisResult.model_validate(payload)
    openai_service._validate_final_grounding(
        unsafe_result,
        answers={"actual_steps": _shoe_answers()["actual_steps"]},
        selected_process={
            "process_name": "Reparaturannahme bis Abholung",
            "start_event": "Ein Gegenstand wird angenommen",
            "end_event": "Ein Gegenstand wird abgeholt",
        },
    )
    assert all("ausweis" not in step.casefold() for step in unsafe_result.as_is_steps)
    solution_payload = _shoe_result().model_dump()
    solution_payload["uncertainties"].append(
        "Es ist unbekannt, ob eine digitale Auftragskarte verwendet werden kann."
    )
    solution_uncertainty = FinalAnalysisResult.model_validate(solution_payload)
    openai_service._validate_final_grounding(
        solution_uncertainty,
        answers={"actual_steps": _shoe_answers()["actual_steps"]},
        selected_process={
            "process_name": "Reparaturannahme bis Abholung",
            "start_event": "Ein Gegenstand wird angenommen",
            "end_event": "Ein Gegenstand wird abgeholt",
        },
    )
    assert any(
        "auftragskarte" in uncertainty.casefold()
        for uncertainty in solution_uncertainty.uncertainties
    )


def test_processing_status_and_completed_analysis_are_idempotent(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id, _result_text = _run_quality_case(
        client=client,
        database_session=database_session,
        monkeypatch=monkeypatch,
        business_context="Eine kleine Schreinerei.",
        problem_overview="Unterlagen sind verteilt.",
        suggestion=ProcessSuggestion(
            process_name="Auftragsfreigabe bis Arbeitsvorbereitung",
            start_event="Auftrag ist freigegeben",
            end_event="Arbeitsunterlagen liegen vor",
            reason="Informationen sind verteilt.",
        ),
        answers=_carpentry_answers(),
        follow_up=FollowUpQuestion(
            question="Wie wird heute die aktuelle Zeichnung erkannt?",
            issue_type="missing",
        ),
        follow_up_answer="Eine fachkundige Person prüft heute die Zeichnung.",
        final_result=_carpentry_result(),
    )
    second_call = client.post(f"/sessions/{session_id}/analyze")
    assert second_call.status_code == 200
    assert second_call.json()["state"] == "complete"
    assert database_session.scalar(
        select(func.count())
        .select_from(AutomationOpportunity)
        .where(AutomationOpportunity.session_id == session_id)
    ) == 1
    assert client.get(f"/sessions/{session_id}/analysis-status").json()[
        "state"
    ] == "complete"


def test_completed_analysis_blocks_all_input_updates(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id, _result_text = _run_quality_case(
        client=client,
        database_session=database_session,
        monkeypatch=monkeypatch,
        business_context="Ein Schuhmacherbetrieb.",
        problem_overview="Aufträge stehen auf Papierzetteln.",
        suggestion=ProcessSuggestion(
            process_name="Reparaturannahme bis Abholung",
            start_event="Gegenstand wird angenommen",
            end_event="Gegenstand wird abgeholt",
            reason="Der Auftragsstand ist schwer erkennbar.",
        ),
        answers=_shoe_answers(),
        follow_up=FollowUpQuestion(
            question="Wie wird heute ein fertiger Auftrag festgehalten?",
            issue_type="missing",
        ),
        follow_up_answer="Der fertige Auftrag wird heute im Heft markiert.",
        final_result=_shoe_result(),
    )
    original_answers = dict(
        database_session.execute(
            select(InterviewQuestion.question_key, InterviewQuestion.answer_text).where(
                InterviewQuestion.session_id == session_id
            )
        ).all()
    )
    update_response = client.post(
        f"/sessions/{session_id}/interview",
        data={"business_context": "Neu", "problem_overview": "Neu"},
        follow_redirects=False,
    )
    assert update_response.headers["location"] == f"/sessions/{session_id}/results"
    detail_response = client.post(
        f"/sessions/{session_id}/process-details",
        data={key: "Geändert" for key in _shoe_answers()},
        follow_redirects=False,
    )
    assert detail_response.headers["location"] == f"/sessions/{session_id}/results"
    process_id = database_session.scalar(
        select(ProcessOption.process_id).where(
            ProcessOption.session_id == session_id,
            ProcessOption.is_selected.is_(True),
        )
    )
    selection_response = client.post(
        f"/sessions/{session_id}/process-options",
        data={"process_id": str(process_id)},
        follow_redirects=False,
    )
    assert selection_response.headers["location"] == (
        f"/sessions/{session_id}/results"
    )
    follow_up_response = client.post(
        f"/sessions/{session_id}/follow-ups",
        data={"follow_up_1": "Geändert"},
        follow_redirects=False,
    )
    assert follow_up_response.headers["location"] == (
        f"/sessions/{session_id}/results"
    )
    stored_answers = dict(
        database_session.execute(
            select(InterviewQuestion.question_key, InterviewQuestion.answer_text).where(
                InterviewQuestion.session_id == session_id
            )
        ).all()
    )
    assert stored_answers == original_answers
    assert database_session.get(Analysis, session_id) is not None


def test_detail_help_and_back_navigation_are_visible(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id = _start_with_context(
        client,
        "Ein kleiner Betrieb.",
        "Ein Ablauf ist unübersichtlich.",
    )
    _select_suggested_process(
        client,
        database_session,
        monkeypatch,
        session_id,
        ProcessSuggestion(
            process_name="Anfrage bis Abschluss",
            start_event="Eine Anfrage kommt an",
            end_event="Der Auftrag ist abgeschlossen",
            reason="Der Ablauf soll untersucht werden.",
        ),
    )
    selection_page = client.get(f"/sessions/{session_id}/process-options")
    assert "Diese Abläufe habe ich aus deiner Beschreibung erkannt." in selection_page.text
    details_page = client.get(f"/sessions/{session_id}/process-details")
    assert "So habe ich deinen Ablauf verstanden." in details_page.text
    assert "Was sollen wir ändern?" in details_page.text
    assert "data-diagram-steps" not in details_page.text


def test_process_answers_can_be_edited_without_duplicate_questions(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id = _start_with_context(
        client,
        "Ein kleiner Reparaturbetrieb.",
        "Auftragsangaben sind verteilt.",
    )
    _select_suggested_process(
        client,
        database_session,
        monkeypatch,
        session_id,
        ProcessSuggestion(
            process_name="Annahme bis fertiger Auftrag",
            start_event="Ein Auftrag wird angenommen",
            end_event="Der Auftrag ist fertig",
            reason="Der Bearbeitungsstand ist nicht zentral sichtbar.",
        ),
    )
    monkeypatch.setattr(
        routes,
        "generate_follow_up_questions",
        lambda **_kwargs: FollowUpResult(
            questions=[
                FollowUpQuestion(
                    question="Wie wird heute ein fertiger Auftrag erkannt?",
                    issue_type="missing",
                )
            ]
        ),
    )
    monkeypatch.setattr(
        routes,
        "evaluate_readiness_and_next_action",
        lambda _state: NextActionDecision(
            next_action="ASK",
            reasoning="Testet die idempotente Speicherung einer relevanten Rückfrage.",
            information_gap="status_transitions",
            analysis_allowed=True,
        ),
    )
    first_answers = {
        question["key"]: f"Heutige Antwort {question['order']}"
        for question in PROCESS_QUESTIONS
    }
    first_answers["actual_steps"] = (
        '["Auftrag annehmen", "Angaben prüfen", "Auftrag fertigstellen"]'
    )
    client.post(
        f"/sessions/{session_id}/process-details",
        data=first_answers,
        follow_redirects=False,
    )
    follow_up_page = client.get(f"/sessions/{session_id}/follow-ups")
    assert "Eine Sache möchten wir noch verstehen" in follow_up_page.text
    assert "Weiß ich gerade nicht" in follow_up_page.text
    edited_answers = dict(first_answers)
    edited_answers["actual_steps"] = (
        '["Ablauf neu beschreiben", "Bearbeitung bewusst fortsetzen"]'
    )
    response = client.post(
        f"/sessions/{session_id}/process-details",
        data=edited_answers,
        follow_redirects=False,
    )
    assert response.headers["location"] == f"/sessions/{session_id}/follow-ups"
    process_questions = list(
        database_session.scalars(
            select(InterviewQuestion).where(
                InterviewQuestion.session_id == session_id,
                InterviewQuestion.question_phase == "process",
            )
        )
    )
    follow_ups = list(
        database_session.scalars(
            select(InterviewQuestion).where(
                InterviewQuestion.session_id == session_id,
                InterviewQuestion.question_phase == "follow_up",
            )
        )
    )
    assert len(process_questions) == 7
    assert len(follow_ups) == 1
    assert next(
        question.answer_text
        for question in process_questions
        if question.question_key == "actual_steps"
    ) == edited_answers["actual_steps"]


def test_final_prompt_separates_facts_patterns_inferences_and_recommendations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def parse(**kwargs: object) -> FinalAnalysisResult:
        captured.update(kwargs)
        return _carpentry_result()

    monkeypatch.setattr(openai_service, "_parse_structured_output", parse)
    openai_service.generate_final_analysis(
        answers={"actual_steps": _carpentry_answers()["actual_steps"]},
        selected_process={
            "process_name": "Auftragsfreigabe bis Arbeitsvorbereitung",
            "start_event": "Ein Auftrag ist freigegeben",
            "end_event": "Geprüfte Arbeitsunterlagen liegen vor",
        },
        knowledge_chunks=["Internes Vergleichswissen"],
    )
    prompt = str(captured["system_prompt"])
    payload = captured["payload"]
    # Der Briefing-Prompt beschreibt Haltung und Felder; die Trennung von
    # Nutzerfakten, Vergleichswissen, Ableitungen und gewaehltem Muster
    # passiert im Payload, nicht mehr ueber Abschnittsbuchstaben im Text.
    assert "Das gewählte Lösungsmuster" in prompt
    assert "max_length" not in prompt
    assert "min_length" not in prompt
    assert isinstance(payload, dict)
    assert set(payload) == {
        "SO_ERZAEHLT_ES_DER_BETRIEB",
        "GEWAEHLTES_MUSTER",
        "SOFTWARE_STATT_KI",
        "VERBOTENE_WOERTER",
        "WORAUF_DU_BEI_DIESER_BETRIEBSART_ACHTEN_KANNST",
        "NUR_INTERNES_VERGLEICHSWISSEN_NIE_AUSGEBEN",
        "FACHLICHE_ABLEITUNGEN",
    }
    # Die geprueften Begriffe gehen als Liste mit, damit Prompt und Filter
    # nicht auseinanderlaufen.
    assert "Minimalformular" in payload["VERBOTENE_WOERTER"]
    assert "extrahieren" in payload["VERBOTENE_WOERTER"]


def test_process_summary_is_neutralized_without_discarding_analysis() -> None:
    meta_payload = _carpentry_result().model_dump()
    meta_payload["process_summary"] = (
        "Aus den vorliegenden Angaben ergibt sich ein verteilter Ablauf."
    )
    meta_result = FinalAnalysisResult.model_validate(meta_payload)
    assert "Aus den vorliegenden Angaben" not in meta_result.process_summary
    assert meta_result.loesung.titel

    repeated_payload = _carpentry_result().model_dump()
    repeated_payload["process_summary"] = (
        "„Auftragsfreigabe bis Arbeitsvorbereitung“ umfasst mehrere Schritte."
    )
    repeated_result = FinalAnalysisResult.model_validate(repeated_payload)
    grounded = openai_service._validate_final_grounding(
        repeated_result,
        answers={"actual_steps": _carpentry_answers()["actual_steps"]},
        selected_process={
            "process_name": "Auftragsfreigabe bis Arbeitsvorbereitung",
            "start_event": "Ein Auftrag ist freigegeben",
            "end_event": "Geprüfte Arbeitsunterlagen liegen vor",
        },
    )
    assert not grounded.process_summary.startswith("„Auftragsfreigabe")
    assert grounded.loesung.titel
