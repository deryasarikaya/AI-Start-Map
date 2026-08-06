from __future__ import annotations

import json

from app import openai_service
from app.models import Analysis, AutomationOpportunity
from app.recommendation_service import load_recommendation_catalog
from app.routes import _result_view
from app.schemas import FinalAnalysisResult
from app.solution_knowledge import output_structure_context, output_structure_for


def _new_payload() -> dict[str, object]:
    return {
        "primary_recommendation": "Einsatznotiz aus Sprache, Foto und Bon vorbereiten",
        "promise": "Du erhältst eine prüfbare Einsatznotiz als Rechnungsgrundlage.",
        "short_reason": "Sprache, Fotos und Bon werden heute erst abends zusammengeführt.",
        "before_process": [
            "Du führst den Einsatz aus.",
            "Du sendest Sprache, Fotos und Bon digital.",
            "Du schreibst abends den Bericht.",
        ],
        "future_process": [
            "Du leitest Sprache, Fotos und Bon für einen Einsatz weiter.",
            "Die KI ordnet die bestätigten Angaben in einen Entwurf.",
            "Eine Regel markiert fehlende Pflichtangaben.",
            "Du prüfst die Einsatznotiz und verwendest sie weiter.",
        ],
        "sample_output": {
            "title": "Einsatznotiz",
            "fields": [
                {"label": "Einsatz", "value": "noch offen"},
                {"label": "Material", "value": "Beispiel: Position aus Bon"},
            ],
            "open_items": ["Einsatznummer noch offen"],
            "attachments": ["Foto", "Bon"],
            "preview_notice": "Vorschau – die endgültigen Angaben prüfst du selbst.",
        },
        "user_action": "Du leitest Sprache, Fotos und Bon weiter.",
        "ai_task": "Die KI erstellt daraus einen strukturierten Entwurf.",
        "software_rule": "Pflichtfelder und Status werden nach festen Regeln geprüft.",
        "visible_result": "Du erhältst eine prüfbare Einsatznotiz.",
        "human_check": "Du prüfst Zuordnung, Zeit, Material und Zusatzarbeit.",
        "customer_benefits": ["Du findest die Rechnungsgrundlage an einer Stelle."],
        "required_prerequisites": ["Ein bestätigter Einsatzanker"],
        "implementation_path": [
            "Pflichtfelder für die Einsatznotiz festlegen.",
            "Den Entwurf mit neuen Einsätzen erproben.",
        ],
        "later_stage": "Nach deiner Freigabe kann ein Rechnungsentwurf vorbereitet werden.",
        "open_details": ["Einsatznummer noch offen"],
        "smallest_usable_version": "Mit einer geprüften Einsatznotiz für neue Einsätze beginnen.",
        "not_automated": ["Rechnungsfreigabe", "Preisentscheidung", "Versand"],
        "autonomy_level": "A2",
        "secondary_opportunities": [],
        "error_boundaries": ["Unklare Zuordnungen bleiben offen."],
        "process_summary": "Nach dem Einsatz werden digitale Spuren für den Bericht zusammengeführt.",
        "as_is_steps": [
            "Einsatz ausführen.",
            "Sprache, Fotos und Bon senden.",
            "Bericht abends schreiben.",
        ],
        "core_bottleneck": "Die digitalen Einsatzspuren werden manuell nachbearbeitet.",
        "bottleneck_symptom": "Der Bericht entsteht erst abends.",
        "bottleneck_cause": "Die digitalen Spuren liegen noch nicht als Einsatznotiz vor.",
        "bottleneck_effect": "Die Rechnungsgrundlage muss manuell zusammengestellt werden.",
        "as_is_problem_step_indexes": [1, 2],
        "to_be_steps": [
            "Digitale Spuren weiterleiten.",
            "Entwurf erzeugen.",
            "Pflichtangaben prüfen.",
            "Einsatznotiz freigeben.",
        ],
        "uncertainties": ["Die Einsatznummer ist noch offen."],
    }


def test_new_contract_requires_and_preserves_all_customer_roles() -> None:
    schema = FinalAnalysisResult.model_json_schema()
    required = set(schema["required"])
    assert {
        "software_rule",
        "open_details",
        "smallest_usable_version",
        "not_automated",
        "autonomy_level",
    } <= required
    assert "legacy_filled_fields" not in schema["properties"]

    result = FinalAnalysisResult.model_validate(_new_payload())
    assert result.autonomy_level == "A2"
    assert result.software_rule.startswith("Pflichtfelder")
    assert result.not_automated == ["Rechnungsfreigabe", "Preisentscheidung", "Versand"]
    assert result.legacy_filled_fields == []


def test_missing_direct_address_is_repaired_without_rejecting_the_analysis() -> None:
    payload = _new_payload()
    payload["user_action"] = "Vorhandene Nachrichten und Belege weiterleiten."
    payload["human_check"] = "Preis, Inhalt und verbindliche Freigabe kontrollieren."

    result = FinalAnalysisResult.model_validate(payload)

    assert result.user_action == "Du übernimmst: Vorhandene Nachrichten und Belege weiterleiten."
    assert result.human_check == "Du prüfst: Preis, Inhalt und verbindliche Freigabe kontrollieren."
    assert result.primary_recommendation == payload["primary_recommendation"]


def test_direct_address_repair_respects_field_length_limits() -> None:
    payload = _new_payload()
    payload["user_action"] = "A" * 180
    payload["human_check"] = "B" * 200

    result = FinalAnalysisResult.model_validate(payload)

    assert len(result.user_action) == 180
    assert len(result.human_check) == 200


def test_user_word_example_word_and_future_workflow_are_allowed() -> None:
    normalized = openai_service._normalize_final_analysis_payload(
        {"promise": "Das Mapping erzeugt eine Foto-Übersicht."},
        allowed_user_text="der nutzer nennt mapping und foto",
    )
    assert normalized == {"promise": "Das Mapping erzeugt eine Foto-Übersicht."}

    result = FinalAnalysisResult.model_validate(_new_payload())
    assert "Beispiel" in result.sample_output.fields[1].value
    assert any("Foto" in step for step in result.future_process)


def test_invented_current_fact_is_neutralized_without_losing_analysis() -> None:
    payload = _new_payload()
    payload["as_is_steps"] = [
        *payload["as_is_steps"],
        "Bei der Übergabe wird ein Ausweis geprüft.",
    ]
    result = FinalAnalysisResult.model_validate(payload)
    grounded = openai_service._validate_final_grounding(
        result,
        answers={"actual_steps": "Sprache, Fotos und Bon werden gesendet."},
        selected_process={
            "process_name": "Einsatz bis Bericht",
            "start_event": "Der Einsatz endet",
            "end_event": "Der Bericht liegt vor",
        },
    )
    assert all("ausweis" not in step.casefold() for step in grounded.as_is_steps)
    assert grounded.primary_recommendation
    assert any("nicht belegtes Detail" in item for item in grounded.uncertainties)


def test_internal_reference_neutralizes_only_affected_field() -> None:
    payload = _new_payload()
    payload["sample_output"]["fields"][0]["value"] = "Aus RB03-C01 übernommen"
    result = FinalAnalysisResult.model_validate(payload)
    assert result.sample_output.fields[0].value == "noch offen"
    assert result.primary_recommendation
    assert any("internes" in item for item in result.uncertainties)


def test_output_structure_and_boundaries_are_applied_deterministically() -> None:
    result = FinalAnalysisResult.model_validate(_new_payload())
    pattern = next(
        item
        for item in load_recommendation_catalog().solution_patterns
        if item.solution_id == "SP-03"
    )
    contracted = openai_service._apply_recommendation_contract(
        result,
        {
            "autonomy_level": "A1",
            "primary": pattern.model_dump(),
            "output_structure": output_structure_context(output_structure_for("SP-03")),
        },
        user_fact_text="sprache fotos bon material",
    )
    assert [item.label for item in contracted.sample_output.fields] == [
        "Kunde oder Objekt",
        "Durchgeführte Tätigkeit",
        "Arbeitszeit",
        "Material",
        "Besonderheiten",
        "Offene Punkte",
    ]
    values = {item.label: item.value for item in contracted.sample_output.fields}
    assert values["Material"].startswith("Beispiel:")
    assert all(
        value == "noch offen"
        for label, value in values.items()
        if label != "Material"
    )
    assert contracted.autonomy_level == "A1"
    assert contracted.primary_recommendation == pattern.name
    assert "SP-" not in contracted.primary_recommendation
    assert contracted.smallest_usable_version == pattern.smallest_entry
    assert contracted.software_rule
    assert contracted.not_automated


def test_a0_contract_removes_ai_recommendation_and_secondary_options() -> None:
    payload = _new_payload()
    result = FinalAnalysisResult.model_validate(payload)
    contracted = openai_service._apply_recommendation_contract(
        result,
        {
            "autonomy_level": "A0",
            "a0_recommendation": (
                "Nutze zuerst die vorhandene Kalenderfunktion. "
                "KI ist dafür nicht notwendig."
            ),
        },
        user_fact_text="vorhandene kalenderfunktion",
    )
    assert contracted.autonomy_level == "A0"
    assert contracted.primary_recommendation == (
        "Vorhandene Funktion oder einfache Regel zuerst nutzen"
    )
    assert contracted.ai_task == (
        "Für diesen ersten Schritt ist keine KI-Aufgabe notwendig."
    )
    assert "an einem konkreten Beispiel" in contracted.human_check
    assert contracted.secondary_opportunities == []


def test_future_step_can_finish_a_customer_sentence_beyond_140_characters() -> None:
    payload = _new_payload()
    payload["future_process"][0] = (
        "Du wählst die vorhandenen digitalen Angaben für den Vorgang aus; "
        "danach werden Sprache, Fotos und Beleg gemeinsam und mit sichtbaren "
        "offenen Punkten als Entwurf angezeigt."
    )
    result = FinalAnalysisResult.model_validate(payload)
    assert len(result.future_process[0]) > 140
    assert result.future_process[0].endswith("angezeigt.")


def test_internal_solution_ids_are_neutralized_and_future_grammar_is_repaired() -> None:
    payload = _new_payload()
    payload["short_reason"] = "Das Muster SP-03 passt zu den Angaben."
    payload["future_process"][0] = "Du wählt die vorhandenen Angaben aus."
    result = FinalAnalysisResult.model_validate(payload)
    assert result.short_reason == "noch offen"
    assert result.future_process[0] == "Du wählst die vorhandenen Angaben aus."
    assert any("internes" in item for item in result.uncertainties)

    payload = _new_payload()
    payload["future_process"][0] = (
        "Nutzer wählt oder übermittelt die vorhandenen Angaben."
    )
    result = FinalAnalysisResult.model_validate(payload)
    assert result.future_process[0] == (
        "Du wählst oder übermittelst die vorhandenen Angaben."
    )


def test_legacy_shim_logs_placeholders_and_keeps_new_fields_empty(monkeypatch) -> None:
    logged: list[tuple[object, ...]] = []
    monkeypatch.setattr(
        "app.schemas.logger.info",
        lambda *args, **_kwargs: logged.append(args),
    )
    legacy_payload = {
        "process_summary": "Eine Anfrage kommt an und wird bearbeitet.",
        "as_is_steps": ["Anfrage annehmen", "Anfrage bearbeiten"],
        "core_bottleneck": "Der aktuelle Stand ist verteilt.",
        "uncertainties": [],
        "opportunities": [
            {
                "rank": 1,
                "title": "Anfragen ordnen",
                "problem": "Der Stand ist verteilt.",
                "recommendation": "Eine Übersicht verwenden.",
                "benefit": "Der Stand wird sichtbar.",
                "human_approval": "Du prüfst die Übersicht.",
                "first_step": "Pflichtangaben festlegen.",
            }
        ],
    }
    result = FinalAnalysisResult.model_validate(legacy_payload)
    assert result.legacy_filled_fields
    assert result.software_rule == ""
    assert result.smallest_usable_version == ""
    assert result.not_automated == []
    assert result.autonomy_level is None
    visible = result.customer_visible_dump()
    for field_name in result.legacy_filled_fields:
        assert visible[field_name] in ("", [])
    assert logged and logged[0][0] == "final_analysis.legacy_fields_filled fields=%s"
    assert "Die KI erkennt und ordnet die relevanten Angaben." not in str(visible)


def test_legacy_database_view_does_not_show_generic_placeholders() -> None:
    analysis = Analysis(
        session_id=1,
        process_summary="Eine Anfrage kommt an und wird bearbeitet.",
        as_is_steps={"steps": ["Anfrage annehmen", "Anfrage bearbeiten"]},
        core_bottleneck="Der aktuelle Stand ist verteilt.",
        uncertainties={"items": [], "core_output": {}},
    )
    opportunity = AutomationOpportunity(
        opportunity_id=1,
        session_id=1,
        rank=1,
        title="Anfragen ordnen",
        problem="Der aktuelle Stand ist verteilt.",
        recommendation="Eine Übersicht verwenden.",
        benefit="Der Stand wird sichtbar.",
        human_approval="Eine Person prüft die Übersicht.",
        first_step="Pflichtangaben festlegen.",
        blueprint_json=None,
    )
    view = _result_view(analysis, [opportunity])
    assert view["ai_task"] == ""
    assert view["user_action"] == ""
    assert view["sample_output"]["fields"] == []
    assert "Angaben erkennen und ordnen" not in str(view)
    assert "Ein prüfbarer Entwurf" not in str(view)


def test_database_view_maps_internal_solution_id_to_customer_title() -> None:
    analysis = Analysis(
        session_id=1,
        process_summary="Eine Nachricht wird geprüft.",
        as_is_steps={"steps": ["Nachricht annehmen", "Inhalt prüfen"]},
        core_bottleneck="Angaben werden manuell übertragen.",
        uncertainties={
            "items": [],
            "core_output": {
                "primary_recommendation": "Dokumente ordnen (SP-06)",
                "secondary_opportunities": [
                    {
                        "title": "Einsatznotiz (SP-03)",
                        "description": "Eine weitere geprüfte Möglichkeit.",
                    }
                ],
            },
        },
    )
    opportunity = AutomationOpportunity(
        opportunity_id=1,
        session_id=1,
        rank=1,
        title="Dokumente ordnen (SP-06)",
        problem="Angaben werden manuell übertragen.",
        recommendation="Angaben als Entwurf strukturieren.",
        benefit="Offene Angaben werden sichtbar.",
        human_approval="Du prüfst den Entwurf.",
        first_step="Pflichtangaben festlegen.",
        blueprint_json=None,
    )
    view = _result_view(analysis, [opportunity])
    assert view["primary_recommendation"] == (
        "Dokument-zu-Datensatz mit Unsicherheitsprüfung"
    )
    assert view["secondary_opportunities"][0]["title"] == (
        "Mobile Einsatzdokumentation aus Sprache, Fotos und Bon"
    )
    assert "SP-" not in str(view)


def test_final_parse_uses_medium_reasoning_and_retries_once(monkeypatch) -> None:
    payloads = [{}, _new_payload()]
    calls: list[dict[str, object]] = []

    class RawResponse:
        status_code = 200

        def __init__(self, content: dict[str, object]) -> None:
            self.text = json.dumps(
                {
                    "choices": [
                        {
                            "finish_reason": "stop",
                            "message": {"content": json.dumps(content)},
                        }
                    ]
                }
            )

    class Parser:
        def parse(self, **kwargs: object) -> RawResponse:
            calls.append(kwargs)
            return RawResponse(payloads.pop(0))

    class FakeClient:
        def __init__(self, **_: object) -> None:
            parser = Parser()
            self.chat = type(
                "Chat",
                (),
                {
                    "completions": type(
                        "Completions",
                        (),
                        {"with_raw_response": parser},
                    )()
                },
            )()

    monkeypatch.setattr(openai_service, "OpenAI", FakeClient)
    monkeypatch.setattr(openai_service, "_api_key", lambda: "configured-for-test")
    monkeypatch.setattr(openai_service, "_structured_output_model", lambda: "gpt-5-mini")

    result = openai_service._parse_structured_output(
        system_prompt="Test",
        payload={"A_USER_FACTS": {}},
        result_type=FinalAnalysisResult,
    )
    assert result.autonomy_level == "A2"
    assert len(calls) == 2
    assert all(call["reasoning_effort"] == "medium" for call in calls)
    assert all(float(call["timeout"]) <= 120.0 for call in calls)
