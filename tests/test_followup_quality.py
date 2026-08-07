from __future__ import annotations

import json

from app.agent_service import (
    QUESTION_PATTERN_FILE,
    FactRecord,
    ProcessState,
    RagEvidence,
    evaluate_readiness_and_next_action,
    question_can_change_core_output,
    question_reason_for_pattern,
)


def _fact(value: str, turn_id: str) -> FactRecord:
    return FactRecord(
        value=value,
        status="confirmed",
        origin="user_statement",
        turn_id=turn_id,
    )


def test_question_reason_comes_from_the_exact_pattern() -> None:
    question = "Wer muss zustimmen, bevor es weitergehen darf?"
    patterns = [
        json.loads(line)
        for line in QUESTION_PATTERN_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    pattern = next(item for item in patterns if item["question_template"] == question)
    assert question_reason_for_pattern(question) == pattern["why_it_matters_user_facing"]
    assert question_reason_for_pattern("Eine frei erzeugte Frage?") == ""


def test_all_question_patterns_are_audited_for_solo_businesses() -> None:
    patterns = [
        json.loads(line)
        for line in QUESTION_PATTERN_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(patterns) == 40
    multi_party = [
        item
        for item in patterns
        if item["information_gap"] in {"human_approvals", "third_party_pickup"}
    ]
    assert len(multi_party) == 2
    assert all(
        "mehr als eine beteiligte Person" in item["when_not_to_ask"]
        for item in multi_party
    )


def test_solo_business_is_not_asked_for_an_approval_role() -> None:
    state = ProcessState(
        selected_process=_fact("Anfrage bearbeiten", "selected_process"),
        process_start=_fact("Eine Anfrage kommt an", "process_start"),
        process_end=_fact("Die Antwort ist geprüft", "process_end"),
        as_is_steps=[_fact("Anfrage lesen", "step_1"), _fact("Antwort senden", "step_2")],
        actors=[_fact("Ich allein", "actors")],
        confirmed_user_facts=[_fact("Ich arbeite allein", "solo")],
    )
    assert not question_can_change_core_output(
        "Wer muss zustimmen, bevor es weitergehen darf?",
        state,
    )


def test_complete_flower_shop_narrative_needs_zero_followups() -> None:
    narrative = (
        "Ich habe einen kleinen Blumenladen und wir bekommen Bestellungen über "
        "WhatsApp, Instagram, E-Mail, Telefon und Onlineshop. Fotos von Sträußen, "
        "Lieferadressen und Sonderwünsche liegen verteilt. Beim Vorbereiten muss "
        "ich in mehreren Chats nachsehen, was der Kunde wollte."
    )
    state = ProcessState(
        selected_process=_fact("Bestellung annehmen und vorbereiten", "selected_process"),
        process_start=_fact("Eine Bestellung kommt an", "process_start"),
        process_end=_fact("Die Bestellung ist vorbereitet", "process_end"),
        as_is_steps=[
            _fact("Bestellung lesen", "step_1"),
            _fact("Angaben in mehreren Chats suchen", "step_2"),
            _fact("Bestellung vorbereiten", "step_3"),
        ],
        channels=[_fact("WhatsApp, Instagram, E-Mail, Telefon und Onlineshop", "channels")],
        information_objects=[_fact("Fotos, Lieferadresse und Sonderwünsche", "objects")],
        available_data=[_fact("Bestellnachrichten und Fotos", "available_data")],
        pain_points=[_fact("Angaben liegen verteilt", "pain")],
        bottleneck_candidates=[_fact("Suche in mehreren Chats", "bottleneck")],
        digital_maturity=_fact("digitale Kanäle vorhanden", "maturity"),
        confirmed_user_facts=[_fact(narrative, "narrative")],
        rag_evidence=[
            RagEvidence(
                chunk_id="internal",
                chunk_type="diagnostic_pattern",
                content="Interner Vergleich",
            )
        ],
    )
    decision = evaluate_readiness_and_next_action(state)
    assert decision.next_action == "ANALYZE"
    assert decision.possible_next_question == ""
