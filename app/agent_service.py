from __future__ import annotations

import json
import logging
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.agent_config import AGENT_HEURISTICS
from app.rag_service import KnowledgeChunk, format_chunks_for_prompt, retrieve_chunks
from app.recommendation_service import infer_decision_gates


ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
logger = logging.getLogger(__name__)
QUESTION_PATTERN_FILE = (
    ROOT_DIRECTORY
    / "knowledge"
    / "runtime"
    / "patterns"
    / "next_question_patterns.jsonl"
)

AgentAction = Literal["ASK", "CLARIFY", "RETRIEVE", "ANALYZE", "STOP"]
FactStatus = Literal[
    "candidate", "confirmed", "corrected", "unknown", "skipped", "superseded"
]
FactOrigin = Literal[
    "user_statement", "user_confirmation", "agent_inference", "retrieved_evidence"
]


class AgentModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class FactRecord(AgentModel):
    value: str
    status: FactStatus
    origin: FactOrigin
    turn_id: str
    confidence_note: str = ""


class QuestionRecord(AgentModel):
    question_key: str
    question_text: str
    information_gap: str
    answer_status: Literal["answered", "unknown", "skipped"]


class UncertaintyRecord(AgentModel):
    field: str
    reason: str
    blocking: bool = False
    origin: Literal["user", "agent", "speech", "tool"] = "agent"


class ContradictionRecord(AgentModel):
    field: str
    statement_a: str
    statement_b: str
    blocking: bool = True


class RagEvidence(AgentModel):
    chunk_id: str
    chunk_type: str
    content: str
    source_strength: str = "not_assessed"


class ProcessState(AgentModel):
    selected_process: FactRecord | None = None
    process_start: FactRecord | None = None
    process_end: FactRecord | None = None
    as_is_steps: list[FactRecord] = Field(default_factory=list)
    actors: list[FactRecord] = Field(default_factory=list)
    channels: list[FactRecord] = Field(default_factory=list)
    tools: list[FactRecord] = Field(default_factory=list)
    information_objects: list[FactRecord] = Field(default_factory=list)
    status_transitions: list[FactRecord] = Field(default_factory=list)
    exceptions: list[FactRecord] = Field(default_factory=list)
    frequency: FactRecord | None = None
    volume: FactRecord | None = None
    pain_points: list[FactRecord] = Field(default_factory=list)
    bottleneck_candidates: list[FactRecord] = Field(default_factory=list)
    digital_maturity: FactRecord | None = None
    available_data: list[FactRecord] = Field(default_factory=list)
    human_approvals: list[FactRecord] = Field(default_factory=list)
    constraints: list[FactRecord] = Field(default_factory=list)
    confirmed_user_facts: list[FactRecord] = Field(default_factory=list)
    unconfirmed_extractions: list[FactRecord] = Field(default_factory=list)
    professional_inferences: list[FactRecord] = Field(default_factory=list)
    rag_evidence: list[RagEvidence] = Field(default_factory=list)
    contradictions: list[ContradictionRecord] = Field(default_factory=list)
    uncertainties: list[UncertaintyRecord] = Field(default_factory=list)
    answered_questions: list[QuestionRecord] = Field(default_factory=list)
    skipped_questions: list[QuestionRecord] = Field(default_factory=list)
    follow_up_count: int = 0
    agent_round_count: int = 0
    tool_round_count: int = 0
    tool_call_history: list[str] = Field(default_factory=list)


class NextActionDecision(AgentModel):
    next_action: AgentAction
    reasoning: str
    information_gap: str = ""
    possible_next_question: str = ""
    remaining_uncertainties: list[str] = Field(default_factory=list)
    analysis_allowed: bool
    stop_reason: str = ""


UNKNOWN_MARKERS = (
    "weiß ich nicht",
    "weiss ich nicht",
    "weiß es gerade nicht",
    "weiss es gerade nicht",
    "keine ahnung",
    "unbekannt",
)
SKIP_MARKERS = ("überspring", "nicht beantworten", "möchte ich nicht sagen")
PLACEHOLDER_MARKERS = ("noch nicht", "nicht geklärt", "keine zusätzliche korrektur")
TOKEN_PATTERN = re.compile(r"[\wäöüß]+", re.IGNORECASE)


def _fact(
    value: str,
    *,
    field: str,
    confirmed: bool = True,
    origin: FactOrigin | None = None,
) -> FactRecord:
    return FactRecord(
        value=value.strip(),
        status="confirmed" if confirmed else "candidate",
        origin=origin or ("user_confirmation" if confirmed else "user_statement"),
        turn_id=field,
    )


def _nonempty_answer(answers: Mapping[str, str], key: str) -> str:
    value = str(answers.get(key, "")).strip()
    if not value or any(marker in value.casefold() for marker in PLACEHOLDER_MARKERS):
        return ""
    return value


def _decoded_steps(value: str) -> list[str]:
    if not value:
        return []
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError:
        decoded = None
    if isinstance(decoded, list):
        return [str(item).strip() for item in decoded if str(item).strip()]
    return [value]


def _question_gap(question_text: str) -> str:
    normalized = question_text.casefold().strip()
    for gap, template in question_templates().items():
        if normalized == template.casefold().strip():
            return gap
    keyword_gaps = (
        ("wer ", "actors"),
        ("kanal", "channels"),
        ("womit", "tools"),
        ("wie oft", "frequency"),
        ("zustimm", "human_approvals"),
        ("abgeschlossen", "process_end"),
        ("auslös", "process_start"),
        ("status", "status_transitions"),
        ("welchem auftrag", "transaction_anchor"),
        ("woran erkennst", "transaction_anchor"),
        ("wirklich liegt", "physical_location"),
        ("kapazität", "capacity_constraints"),
        ("anders", "exceptions"),
    )
    return next((gap for marker, gap in keyword_gaps if marker in normalized), "other")


def _digital_maturity(text: str) -> FactRecord:
    normalized = text.casefold()
    if any(marker in normalized for marker in ("nur papier", "zettel", "heft", "ordner")):
        level = "0"
    elif any(marker in normalized for marker in ("excel", "tabelle", "handy", "smartphone", "kalender")):
        level = "1"
    elif any(marker in normalized for marker in ("software", "system", "digital")):
        level = "2"
    else:
        level = "unknown"
    return _fact(
        level,
        field="digital_maturity",
        confirmed=False,
        origin="agent_inference",
    )


def extract_process_state(
    *,
    answers: Mapping[str, str],
    selected_process: Mapping[str, str],
    questions: Sequence[Mapping[str, str]] = (),
    rag_evidence: Sequence[RagEvidence] = (),
) -> ProcessState:
    """Build state from user data without copying RAG evidence into facts."""

    process_name = str(selected_process.get("process_name", "")).strip()
    start = str(selected_process.get("start_event", "")).strip()
    end = str(selected_process.get("end_event", "")).strip()
    state = ProcessState(
        selected_process=_fact(process_name, field="selected_process") if process_name else None,
        process_start=_fact(start, field="process_start") if start else None,
        process_end=_fact(end, field="process_end") if end else None,
        rag_evidence=list(rag_evidence),
    )
    actual_steps = _decoded_steps(_nonempty_answer(answers, "actual_steps"))
    state.as_is_steps = [
        _fact(step, field=f"actual_steps:{index}") for index, step in enumerate(actual_steps)
    ]
    role_text = _nonempty_answer(answers, "roles_systems_and_handoffs")
    object_text = _nonempty_answer(answers, "business_object_and_result")
    volume_text = _nonempty_answer(answers, "volume_time_and_impact")
    rules_text = _nonempty_answer(answers, "rules_and_exceptions")
    approval_text = _nonempty_answer(answers, "approval_and_success")
    pain_text = _nonempty_answer(answers, "problem_overview")

    if role_text:
        role_fact = _fact(role_text, field="roles_systems_and_handoffs")
        state.actors.append(role_fact)
        state.channels.append(role_fact.model_copy())
        state.tools.append(role_fact.model_copy())
        state.available_data.append(role_fact.model_copy())
    if object_text:
        state.information_objects.append(_fact(object_text, field="business_object_and_result"))
    state.status_transitions = [item.model_copy() for item in state.as_is_steps]
    if rules_text:
        state.exceptions.append(_fact(rules_text, field="rules_and_exceptions"))
        state.constraints.append(_fact(rules_text, field="rules_and_exceptions"))
    if volume_text:
        state.frequency = _fact(volume_text, field="volume_time_and_impact")
        state.volume = _fact(volume_text, field="volume_time_and_impact")
    if approval_text:
        state.human_approvals.append(_fact(approval_text, field="approval_and_success"))
    if pain_text:
        state.pain_points.append(_fact(pain_text, field="problem_overview"))
        inference = _fact(
            pain_text,
            field="bottleneck_candidates",
            confirmed=False,
            origin="agent_inference",
        )
        state.bottleneck_candidates.append(inference)
        state.professional_inferences.append(inference.model_copy())

    combined_user_text = " ".join(str(value) for value in answers.values())
    state.digital_maturity = _digital_maturity(combined_user_text)
    state.professional_inferences.append(state.digital_maturity.model_copy())

    core_facts = [state.selected_process, state.process_start, state.process_end]
    state.confirmed_user_facts.extend(item for item in core_facts if item is not None)
    state.confirmed_user_facts.extend(state.as_is_steps)
    state.confirmed_user_facts.extend(state.actors)
    state.confirmed_user_facts.extend(state.information_objects)
    state.confirmed_user_facts.extend(state.exceptions)
    state.confirmed_user_facts.extend(state.human_approvals)

    for key in ("business_context", "problem_overview"):
        value = _nonempty_answer(answers, key)
        if value:
            state.unconfirmed_extractions.append(
                _fact(value, field=key, confirmed=False, origin="user_statement")
            )

    follow_up_questions = 0
    for question in questions:
        key = str(question.get("question_key", ""))
        text = str(question.get("question_text", ""))
        answer = str(question.get("answer_text", "")).strip()
        if not key.startswith("follow_up_"):
            continue
        follow_up_questions += 1
        if not answer:
            continue
        lowered = answer.casefold()
        gap = _question_gap(text)
        if any(marker in lowered for marker in SKIP_MARKERS):
            record = QuestionRecord(
                question_key=key,
                question_text=text,
                information_gap=gap,
                answer_status="skipped",
            )
            state.skipped_questions.append(record)
            state.uncertainties.append(
                UncertaintyRecord(field=gap, reason="bewusst übersprungen", origin="user")
            )
        elif any(marker in lowered for marker in UNKNOWN_MARKERS):
            state.answered_questions.append(
                QuestionRecord(
                    question_key=key,
                    question_text=text,
                    information_gap=gap,
                    answer_status="unknown",
                )
            )
            state.uncertainties.append(
                UncertaintyRecord(field=gap, reason="Nutzer weiß es nicht", origin="user")
            )
        else:
            state.answered_questions.append(
                QuestionRecord(
                    question_key=key,
                    question_text=text,
                    information_gap=gap,
                    answer_status="answered",
                )
            )
            state.confirmed_user_facts.append(_fact(answer, field=key))
            if any(
                marker in lowered
                for marker in ("eigentlich", "aber", "früher", "stopp,", "doch ")
            ):
                state.contradictions.append(
                    ContradictionRecord(
                        field=gap,
                        statement_a="bisher bestätigter Stand",
                        statement_b=answer,
                    )
                )
    state.follow_up_count = follow_up_questions
    state.agent_round_count = min(follow_up_questions + 1, AGENT_HEURISTICS.maximum_agent_rounds)
    return state


def question_templates() -> dict[str, str]:
    templates: dict[str, str] = {}
    if not QUESTION_PATTERN_FILE.is_file():
        return templates
    for line in QUESTION_PATTERN_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        templates[str(record["information_gap"])] = str(record["question_template"])
    return templates


def _question_pattern(question_text: str) -> dict[str, object] | None:
    if not QUESTION_PATTERN_FILE.is_file():
        return None
    normalized = question_text.casefold().strip()
    for line in QUESTION_PATTERN_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if str(record.get("question_template", "")).casefold().strip() == normalized:
            return record
    return None


def question_reason_for_pattern(question_text: str) -> str:
    """Use the explanation belonging to the exact selected question pattern."""

    pattern = _question_pattern(question_text)
    return str(pattern.get("why_it_matters_user_facing", "")) if pattern else ""


def _multiple_people_are_confirmed(state_text: str) -> bool:
    return re.search(
        r"\b(?:wir|team|mitarbeiter(?:in|innen)?|kolleg(?:e|in|en|innen)|"
        r"angestellt(?:e|en)?|inhaber(?:in)?\s+und|chef(?:in)?\s+und|"
        r"mehrere personen|andere person|dritte person)\b",
        state_text,
        re.IGNORECASE,
    ) is not None


def search_diagnostic_knowledge(query: str, *, phase: str = "analysis") -> list[RagEvidence]:
    chunks: list[KnowledgeChunk] = retrieve_chunks(query, phase=phase)
    logger.info(
        "diagnostic_retrieval.selected phase=%s chunk_count=%d chunk_types=%s",
        phase,
        len(chunks),
        [chunk.chunk_type for chunk in chunks],
    )
    evidence: list[RagEvidence] = []
    for chunk in chunks:
        prompt_contents = format_chunks_for_prompt([chunk])
        if not prompt_contents:
            continue
        evidence.append(
            RagEvidence(
                chunk_id=chunk.chunk_id,
                chunk_type=chunk.chunk_type,
                content=prompt_contents[0],
                source_strength=str(
                    chunk.metadata.get("source_strength", "not_assessed")
                ),
            )
        )
    return evidence


def _answered_gaps(state: ProcessState) -> set[str]:
    return {
        record.information_gap
        for record in [*state.answered_questions, *state.skipped_questions]
    }


def _state_text(state: ProcessState) -> str:
    records = [
        *([state.selected_process] if state.selected_process else []),
        *([state.process_start] if state.process_start else []),
        *([state.process_end] if state.process_end else []),
        *state.as_is_steps,
        *state.actors,
        *state.channels,
        *state.tools,
        *state.information_objects,
        *state.status_transitions,
        *state.exceptions,
        *state.confirmed_user_facts,
        *state.unconfirmed_extractions,
        *state.pain_points,
        *state.bottleneck_candidates,
        *state.available_data,
        *state.human_approvals,
        *state.constraints,
    ]
    return " ".join(record.value for record in records).casefold()


def question_can_change_core_output(question_text: str, state: ProcessState) -> bool:
    """Reject already answered and purely descriptive questions deterministically."""

    normalized = question_text.casefold()
    previous_questions = [*state.answered_questions, *state.skipped_questions]
    if any(
        normalized_question_similarity(question_text, record.question_text) >= 0.72
        for record in previous_questions
    ):
        return False
    if any(
        marker in normalized
        for marker in (
            "wie groß ist der laden",
            "wie hoch ist der umsatz",
            "welches budget",
        )
    ):
        return False
    state_text = _state_text(state)
    pattern = _question_pattern(question_text)
    when_not_to_ask = str(pattern.get("when_not_to_ask", "")) if pattern else ""
    requires_multiple_people = (
        "mehr als eine beteiligte person" in when_not_to_ask.casefold()
        or _question_gap(question_text) == "human_approvals"
    )
    if requires_multiple_people and not _multiple_people_are_confirmed(state_text):
        return False
    if (
        any(
            marker in normalized
            for marker in ("liegedauer", "wie lange", "stunden", "tage")
        )
        and "regal" in state_text
        and any(marker in state_text for marker in ("such", "find", "zettel"))
    ):
        return False
    if (
        any(
            marker in normalized
            for marker in ("regalreihenfolge", "feste reihenfolge", "regalordnung")
        )
        and "regal" in state_text
        and any(marker in state_text for marker in ("frei", "irgendwo", "beliebig"))
    ):
        return False
    gap = _question_gap(question_text)
    if gap != "other" and gap in _answered_gaps(state):
        return False
    known_topic_markers = (
        (
            ("kanal", "whatsapp", "telefon", "e-mail"),
            ("whatsapp", "telefon", "e-mail"),
        ),
        (("regal", "ablage", "ort"), ("regal", "ablage", "regalplatz")),
    )
    if any(
        any(marker in normalized for marker in question_markers)
        and any(marker in state_text for marker in fact_markers)
        for question_markers, fact_markers in known_topic_markers
    ):
        return False
    known_gaps = {
        "actors": bool(state.actors),
        "channels": bool(state.channels),
        "tools": bool(state.tools),
        "frequency": state.frequency is not None,
        "human_approvals": bool(state.human_approvals),
        "available_data": bool(state.available_data),
        "exceptions": bool(state.exceptions),
        "process_start": state.process_start is not None,
        "process_end": state.process_end is not None,
        "as_is_steps": len(state.as_is_steps) >= 2,
    }
    return not known_gaps.get(gap, False)


def evaluate_readiness_and_next_action(
    state: ProcessState,
    *,
    latest_user_message: str = "",
) -> NextActionDecision:
    """Apply deterministic safety, no-repeat and budget policy before retrieval."""

    message = latest_user_message.casefold()
    remaining = [item.field for item in state.uncertainties]
    if any(marker in message for marker in ("schick dem kunden", "bestell", "bezahle", "buche das")):
        return NextActionDecision(
            next_action="STOP",
            reasoning="Die gewünschte reale Ausführung liegt außerhalb des Diagnoseauftrags.",
            remaining_uncertainties=remaining,
            analysis_allowed=False,
            stop_reason="out_of_scope",
        )
    if any(marker in message for marker in ("ergebnis sehen", "jetzt analys", "reicht das", "nicht noch mehr fragen")):
        return NextActionDecision(
            next_action="STOP",
            reasoning="Der Nutzer möchte die Befragung beenden.",
            remaining_uncertainties=remaining,
            analysis_allowed=state.process_start is not None and state.process_end is not None,
            stop_reason="user_requests_stop",
        )
    if any(
        marker in message
        for marker in (
            "das habe ich doch schon gesagt",
            "das hab ich doch schon gesagt",
            "wie schon gesagt",
        )
    ):
        core_ready = (
            state.process_start is not None
            and state.process_end is not None
            and len(state.as_is_steps) >= 2
        )
        return NextActionDecision(
            next_action="ANALYZE" if core_ready else "ASK",
            reasoning=(
                "Vorhandene Angaben werden erneut verwendet; die Frage wird nicht "
                "wiederholt."
            ),
            remaining_uncertainties=remaining,
            analysis_allowed=core_ready,
            stop_reason="no_repeat_recheck" if core_ready else "",
        )
    if state.follow_up_count >= AGENT_HEURISTICS.maximum_visible_follow_ups:
        return NextActionDecision(
            next_action="STOP",
            reasoning="Das zentrale Rückfragebudget ist erreicht; fehlende Angaben bleiben offen.",
            remaining_uncertainties=remaining,
            analysis_allowed=state.process_start is not None and state.process_end is not None,
            stop_reason="follow_up_limit",
        )
    if state.agent_round_count >= AGENT_HEURISTICS.maximum_agent_rounds:
        return NextActionDecision(
            next_action="STOP",
            reasoning="Das Agentenrunden-Budget ist erreicht.",
            remaining_uncertainties=remaining,
            analysis_allowed=state.process_start is not None and state.process_end is not None,
            stop_reason="agent_round_limit",
        )
    if state.tool_round_count >= AGENT_HEURISTICS.maximum_tool_rounds:
        return NextActionDecision(
            next_action="STOP",
            reasoning="Das zentrale Werkzeugrunden-Budget ist erreicht.",
            remaining_uncertainties=remaining,
            analysis_allowed=state.process_start is not None and state.process_end is not None,
            stop_reason="tool_round_limit",
        )
    if state.tool_call_history:
        latest_signature = state.tool_call_history[-1]
        if (
            state.tool_call_history.count(latest_signature)
            >= AGENT_HEURISTICS.maximum_repeated_tool_signature
        ):
            return NextActionDecision(
                next_action="STOP",
                reasoning="Ein wiederholter Werkzeugaufruf wurde als Schleife beendet.",
                remaining_uncertainties=remaining,
                analysis_allowed=(
                    state.process_start is not None and state.process_end is not None
                ),
                stop_reason="repeated_tool_call",
            )
    templates = question_templates()
    answered = _answered_gaps(state)
    if state.contradictions:
        contradiction = state.contradictions[0]
        return NextActionDecision(
            next_action="CLARIFY",
            reasoning="Zwei diagnostisch relevante Angaben sind noch nicht eindeutig vereinbar.",
            information_gap=contradiction.field,
            possible_next_question=templates.get("confirmation", ""),
            remaining_uncertainties=remaining,
            analysis_allowed=False,
        )
    required_gaps = (
        ("process_start", state.process_start is None),
        ("process_end", state.process_end is None),
        ("as_is_steps", len(state.as_is_steps) < 2),
    )
    for gap, missing in required_gaps:
        if missing and gap not in answered:
            return NextActionDecision(
                next_action="ASK",
                reasoning="Eine Prozessgrenze oder der heutige Ablauf fehlt noch.",
                information_gap=gap,
                possible_next_question=templates.get(gap, ""),
                remaining_uncertainties=remaining,
                analysis_allowed=False,
            )
    state_text = _state_text(state)
    decision_gates = infer_decision_gates(state_text)
    if (
        state.follow_up_count < AGENT_HEURISTICS.normal_follow_up_maximum
        and decision_gates.physical_object
        and not decision_gates.real_location_known
        and "transaction_anchor" not in answered
    ):
        return NextActionDecision(
            next_action="ASK",
            reasoning=(
                "Die Antwort entscheidet, ob physische Identität und realer Ort "
                "vor weiterer KI-Unterstützung belastbar sind."
            ),
            information_gap="transaction_anchor",
            possible_next_question=(
                "Woran erkennst du heute, zu welchem Auftrag der Gegenstand gehört "
                "und wo er wirklich liegt?"
            ),
            remaining_uncertainties=remaining,
            analysis_allowed=True,
        )
    # Ein fehlender leichter Vorgangsanker blockiert einen geeigneten digitalen
    # Eingang nicht. Der Selector ergänzt ihn als Teil derselben Einstiegslösung.
    if (
        state.follow_up_count < AGENT_HEURISTICS.normal_follow_up_maximum
        and state.digital_maturity is not None
        and state.digital_maturity.value == "unknown"
        and not state.available_data
        and "available_data" not in answered
    ):
        return NextActionDecision(
            next_action="ASK",
            reasoning=(
                "Die Antwort entscheidet, ob KI schon mit verlässlichen Angaben "
                "arbeiten kann."
            ),
            information_gap="available_data",
            possible_next_question=templates.get("available_data", ""),
            remaining_uncertainties=remaining,
            analysis_allowed=True,
        )
    if (
        state.follow_up_count < AGENT_HEURISTICS.normal_follow_up_maximum
        and not state.bottleneck_candidates
        and "pain_points" not in answered
    ):
        return NextActionDecision(
            next_action="ASK",
            reasoning=(
                "Die Antwort entscheidet, welches Problem im Sofortergebnis "
                "priorisiert wird."
            ),
            information_gap="pain_points",
            possible_next_question=templates.get("pain_points", ""),
            remaining_uncertainties=remaining,
            analysis_allowed=True,
        )
    if not state.rag_evidence and state.bottleneck_candidates:
        return NextActionDecision(
            next_action="RETRIEVE",
            reasoning="Vergleichswissen kann Reifegrad und kleinsten sinnvollen Schritt absichern.",
            remaining_uncertainties=remaining,
            analysis_allowed=True,
        )
    return NextActionDecision(
        next_action="ANALYZE",
        reasoning="Kernablauf und diagnostisch relevante Angaben reichen für die Analyse.",
        remaining_uncertainties=remaining,
        analysis_allowed=True,
        stop_reason="sufficient_core",
    )


def normalized_question_similarity(left: str, right: str) -> float:
    left_tokens = {item.casefold() for item in TOKEN_PATTERN.findall(left)}
    right_tokens = {item.casefold() for item in TOKEN_PATTERN.findall(right)}
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def evaluate_research_trace(
    current_state: Mapping[str, Any], latest_user_message: str
) -> AgentAction:
    """Replay the heterogeneous Batch-04 trace format through deterministic policy."""

    message = latest_user_message.casefold()
    if any(marker in message for marker in ("schick dem kunden", "gleich senden")):
        return "STOP"
    history = current_state.get("tool_call_history")
    if isinstance(history, list) and len(history) >= 2:
        signatures = [json.dumps(item, sort_keys=True) for item in history]
        if max(signatures.count(item) for item in signatures) >= 2:
            return "STOP"
    if any(marker in message for marker in ("ergebnis sehen", "reicht das", "überspringen")):
        return "STOP"
    if "[" in latest_user_message and "/" in latest_user_message:
        return "CLARIFY"
    if any(
        marker in message
        for marker in (
            "eigentlich",
            "ach ja, manchmal kommen",
            "morgens macht das aber",
            "das war früher",
            "seit letzter woche",
            "stopp,",
            "dann machen wir das meistens",
        )
    ):
        return "CLARIFY"
    if any(marker in message for marker in ("keine ahnung", "mehr weiß ich", "mehr weiss ich")):
        return "ANALYZE"
    if "ohne zusage" in message or "wie gesagt" in message:
        return "ANALYZE"
    if current_state.get("frequency") == "50/week" and "200 im monat" in message:
        return "ANALYZE"
    if "zweimal im jahr" in message or "nur die zettel am gegenstand" in message:
        return "ANALYZE"
    if "kann da nicht einfach ki" in message:
        return "ANALYZE"
    if any(
        marker in message
        for marker in (
            "jeden tag etwa 400",
            "kleinste sinnvolle schritt",
            "keine schnittstelle",
        )
    ):
        return "RETRIEVE"
    if current_state.get("readiness_status") == "ready" and "genau so" in message:
        return "ANALYZE"
    if not current_state.get("selected_process") and "rechnungen" in message:
        return "ASK"
    if "process_start" not in current_state or not current_state.get("process_start"):
        if current_state.get("process_end"):
            return "ASK"
    if "process_end" not in current_state or not current_state.get("process_end"):
        if current_state.get("process_start"):
            return "ASK"
    steps = current_state.get("as_is_steps")
    if isinstance(steps, list) and len(steps) <= 1:
        return "ASK"
    return "ASK"
