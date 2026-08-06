from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
CATALOG_FILE = ROOT_DIRECTORY / "knowledge" / "runtime" / "recommendation_catalog.json"
Confidence = Literal["low", "medium", "high"]
GateLevel = Literal["unknown", "low", "medium", "high"]
GateStatus = Literal["pass", "fail", "unknown"]
AutonomyLevelId = Literal["A0", "A1", "A2", "A3", "A4", "A5"]


class CatalogModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ProblemFamily(CatalogModel):
    problem_family_id: str
    name: str
    definition: str
    typical_statements: list[str] = Field(min_length=1)
    symptoms: list[str] = Field(min_length=1)
    common_causes: list[str] = Field(min_length=1)
    processes: list[str] = Field(min_length=1)
    industries: list[str] = Field(min_length=1)
    channels: list[str] = Field(min_length=1)
    digital_starting_state: str
    consequences: list[str] = Field(min_length=1)
    boundaries: list[str] = Field(min_length=1)
    evidence_refs: list[str] = Field(min_length=1)
    confidence: Confidence
    # Batch 05/Forschungsgrundlage Abschnitt 6: Was GenAI hier leisten kann,
    # was ohne GenAI hergestellt werden muss, und wo der Mensch entscheidet.
    genai_role: str
    non_genai_requirement: str
    human_boundary: str


class PilotDefinition(CatalogModel):
    scope: str
    output: str
    no_action: str


class SolutionPattern(CatalogModel):
    solution_id: str
    name: str
    problem_family_ids: list[str] = Field(min_length=1)
    applicable_if: list[str] = Field(min_length=1)
    not_applicable_if: list[str] = Field(min_length=1)
    suitable_industries: list[str] = Field(min_length=1)
    suitable_processes: list[str] = Field(min_length=1)
    input_channels: list[str] = Field(min_length=1)
    minimum_information: list[str] = Field(min_length=1)
    user_action: str
    ai_task: str
    visible_output: str
    human_check: str
    technical_prerequisites: list[str] = Field(min_length=1)
    organizational_prerequisites: list[str] = Field(min_length=1)
    security_guardrails: list[str] = Field(min_length=1)
    smallest_entry: str
    later_stage: str
    failure_modes: list[str] = Field(min_length=1)
    evidence_refs: list[str] = Field(min_length=1)
    customer_language: str
    sample_output_type: str
    # Batch 06: validierte Umsetzungs- und Abgrenzungsfelder.
    genai_capability_ids: list[str] = Field(min_length=1)
    deterministic_components: list[str] = Field(min_length=1)
    human_decisions: list[str] = Field(min_length=1)
    positive_variants: list[str] = Field(min_length=1)
    counterexample: str
    pilot: PilotDefinition
    metrics: list[str] = Field(min_length=1)
    stop_conditions: list[str] = Field(min_length=1)
    # Untergrenze kann A0 sein: manche Muster sind bewusst zuerst eine Regel
    # oder Kennzeichnung und erst danach KI-gestuetzt.
    autonomy_level_min: AutonomyLevelId
    autonomy_level_max: AutonomyLevelId


class GenAiCapability(CatalogModel):
    capability_id: str
    name: str
    input_modalities: list[str] = Field(min_length=1)
    output_type: str
    suitable_tasks: list[str] = Field(min_length=1)
    required_process_foundation: list[str] = Field(min_length=1)
    human_review: list[str] = Field(min_length=1)
    failure_modes: list[str] = Field(min_length=1)
    measurement: list[str] = Field(min_length=1)
    autonomy_ceiling: AutonomyLevelId
    evidence_refs: list[str] = Field(min_length=1)
    customer_language: str


class DecisionGate(CatalogModel):
    gate_id: str
    name: str
    question: str
    on_pass: str
    on_fail: str


class FailurePattern(CatalogModel):
    failure_id: str
    name: str
    trigger: str
    harm: str
    detection: str
    guardrail: str
    blocks_autonomy: list[AutonomyLevelId] = Field(min_length=1)
    customer_language: str


class AutonomyLevel(CatalogModel):
    level: AutonomyLevelId
    name: str
    description: str
    recommend: str


class NonGenAiMechanism(CatalogModel):
    task: str
    mechanism: str


class ProblemSolutionMapping(CatalogModel):
    problem_family_id: str
    primary_solution_ids: list[str] = Field(min_length=1)
    supplementary_solution_ids: list[str]
    hard_prerequisite: str


class RecommendationCatalog(CatalogModel):
    version: str
    source: str
    problem_families: list[ProblemFamily]
    solution_patterns: list[SolutionPattern]
    matrix: list[ProblemSolutionMapping]
    genai_capabilities: list[GenAiCapability]
    decision_gates: list[DecisionGate]
    failure_patterns: list[FailurePattern]
    autonomy_levels: list[AutonomyLevel]
    non_genai_mechanisms: list[NonGenAiMechanism] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_catalog(self) -> "RecommendationCatalog":
        family_ids = [item.problem_family_id for item in self.problem_families]
        solution_ids = [item.solution_id for item in self.solution_patterns]
        expected_families = [f"PF-{index:02d}" for index in range(1, 13)]
        expected_solutions = [f"SP-{index:02d}" for index in range(1, 11)]
        if family_ids != expected_families or len(set(family_ids)) != 12:
            raise ValueError("Der Katalog muss PF-01 bis PF-12 genau einmal enthalten.")
        if solution_ids != expected_solutions or len(set(solution_ids)) != 10:
            raise ValueError("Der Katalog muss SP-01 bis SP-10 genau einmal enthalten.")
        family_set, solution_set = set(family_ids), set(solution_ids)
        if {item.problem_family_id for item in self.matrix} != family_set:
            raise ValueError("Die Matrix muss jede Problemfamilie genau einmal abdecken.")
        for pattern in self.solution_patterns:
            if not set(pattern.problem_family_ids) <= family_set:
                raise ValueError(f"Ungültige Problemfamilie in {pattern.solution_id}.")
        for mapping in self.matrix:
            if not set(mapping.primary_solution_ids + mapping.supplementary_solution_ids) <= solution_set:
                raise ValueError(f"Ungültige Solution-ID in {mapping.problem_family_id}.")
        capability_ids = [item.capability_id for item in self.genai_capabilities]
        gate_ids = [item.gate_id for item in self.decision_gates]
        failure_ids = [item.failure_id for item in self.failure_patterns]
        if capability_ids != [f"GAI-{index:02d}" for index in range(1, 10)]:
            raise ValueError("Der Katalog muss GAI-01 bis GAI-09 genau einmal enthalten.")
        if gate_ids != [f"GATE-{index:02d}" for index in range(1, 7)]:
            raise ValueError("Der Katalog muss GATE-01 bis GATE-06 genau einmal enthalten.")
        if failure_ids != [f"FAIL-{index:02d}" for index in range(1, 13)]:
            raise ValueError("Der Katalog muss FAIL-01 bis FAIL-12 genau einmal enthalten.")
        if [item.level for item in self.autonomy_levels] != [
            f"A{index}" for index in range(6)
        ]:
            raise ValueError("Der Katalog muss die Autonomiestufen A0 bis A5 enthalten.")
        capability_set = set(capability_ids)
        for pattern in self.solution_patterns:
            if not set(pattern.genai_capability_ids) <= capability_set:
                raise ValueError(f"Ungültige GenAI-Fähigkeit in {pattern.solution_id}.")
            ceilings = [
                item.autonomy_ceiling
                for item in self.genai_capabilities
                if item.capability_id in pattern.genai_capability_ids
            ]
            if pattern.autonomy_level_min > pattern.autonomy_level_max:
                raise ValueError(
                    f"{pattern.solution_id} hat eine ungültige Autonomiespanne."
                )
            if ceilings and pattern.autonomy_level_max > min(ceilings):
                raise ValueError(
                    f"{pattern.solution_id} überschreitet die Autonomiegrenze "
                    f"seiner Fähigkeiten ({min(ceilings)})."
                )
        if "evaluation" in self.source.casefold():
            raise ValueError("Evaluationen dürfen kein Produktwissen sein.")
        return self


class DecisionGates(CatalogModel):
    transaction_anchor: GateLevel = "unknown"
    channel_suitability: GateLevel = "unknown"
    process_data_maturity: GateLevel = "unknown"
    error_impact: GateLevel = "unknown"
    rule_stability: GateLevel = "unknown"
    human_approval: GateLevel = "unknown"
    physical_object: bool = False
    real_location_known: bool = False


class GateAssessment(CatalogModel):
    gate_id: Literal[
        "GATE-01", "GATE-02", "GATE-03", "GATE-04", "GATE-05", "GATE-06"
    ]
    status: GateStatus
    reason: str


class RecommendationSelection(CatalogModel):
    problem_family_ids: list[str]
    primary: SolutionPattern | None
    secondary: list[SolutionPattern] = Field(max_length=2)
    excluded_reasons: dict[str, list[str]]
    required_prerequisites: list[str] = Field(max_length=3)
    human_approval_boundaries: list[str]
    gate_assessments: list[GateAssessment] = Field(min_length=6, max_length=6)
    autonomy_level: AutonomyLevelId
    recommendation_mode: Literal["ai_assisted", "non_ai_first"]
    a0_recommendation: str = ""
    stop_conditions: list[str]
    target_fit: GateStatus
    target_fit_reason: str


def load_recommendation_catalog(path: Path = CATALOG_FILE) -> RecommendationCatalog:
    if "evaluation" in str(path).casefold():
        raise ValueError("Evaluationen dürfen nicht als Produktwissen geladen werden.")
    return RecommendationCatalog.model_validate_json(path.read_text(encoding="utf-8"))


def classify_problem_families(text: str) -> list[str]:
    value = text.casefold()
    if any(
        marker in value
        for marker in (
            "kein engpass",
            "keine probleme",
            "bestehende softwarefunktion reicht aus",
            "einfache regel reicht aus",
        )
    ):
        return []
    rules = (
        ("PF-08", ("sprachnachricht", "bon", "einsatz", "rechnung")),
        ("PF-05", ("schuh", "gegenstand", "regal", "ablageort")),
        ("PF-06", ("termin", "personal", "kapazität", "verfügbarkeit")),
        ("PF-02", ("anfrage", "bestellung", "instagram", "whatsapp")),
        ("PF-12", ("pdf", "dokument", "diktat", "freie nachricht")),
        ("PF-10", ("material", "bestand", "produktion")),
        ("PF-09", ("zahlung", "rechnung", "fälligkeit")),
        ("PF-07", ("zusatzarbeit", "änderung", "freigabe")),
        ("PF-04", ("status", "übergabe", "offen")),
        ("PF-01", ("verteilt", "zusammensuchen", "mehrere kanäle")),
    )
    matches = [family for family, markers in rules if any(marker in value for marker in markers)]
    return list(dict.fromkeys(matches))[:3] or ["PF-01"]


def infer_decision_gates(text: str) -> DecisionGates:
    value = text.casefold()
    physical_object = re.search(
        r"\b(?:schuh|schuhe|gegenstand|gegenstände|gerät|geräte|paket|pakete|"
        r"fahrrad|fahrräder|reparaturstück|ware|warenstück|regal|regalplatz)\b",
        value,
    ) is not None
    real_location_known = any(
        marker in value
        for marker in ("regalplatz wird", "ort wird dokumentiert", "festes fach")
    )
    anchor = "high" if any(
        marker in value for marker in ("auftragsnummer", "einsatznummer", "vorgangs-id")
    ) else "low" if physical_object or any(
        marker in value for marker in ("verteilt", "zusammensuchen", "lose nummer")
    ) else "medium"
    channel = "high" if any(
        marker in value
        for marker in ("smartphone", "handy", "whatsapp", "e-mail", "foto", "sprache", "nachricht")
    ) else "low" if any(marker in value for marker in ("nur papier", "nur zettel")) else "medium"
    maturity = "high" if any(
        marker in value for marker in ("pflichtfeld", "statuswert", "zielschema", "system")
    ) else "low" if any(
        marker in value for marker in ("unbekannt", "nicht geklärt", "lose zettel")
    ) else "medium"
    error = "high" if any(
        marker in value
        for marker in ("preis", "vertrag", "zahlung", "termin", "qualität", "herausgabe", "personal")
    ) else "medium"
    rules = "low" if any(
        marker in value for marker in ("wechselnd", "ausnahme", "unklar", "je nach")
    ) else "medium"
    approval = "high" if error == "high" or any(
        marker in value for marker in ("freigabe", "bestätigt", "zustimmung")
    ) else "medium"
    return DecisionGates(
        transaction_anchor=anchor,
        channel_suitability=channel,
        process_data_maturity=maturity,
        error_impact=error,
        rule_stability=rules,
        human_approval=approval,
        physical_object=physical_object,
        real_location_known=real_location_known,
    )


def evaluate_gate_cascade(
    problem_family_ids: list[str],
    gates: DecisionGates,
    *,
    confirmed_text: str = "",
) -> list[GateAssessment]:
    """Übersetzt Rohsignale nachvollziehbar in GATE-01 bis GATE-06."""

    value = confirmed_text.casefold()
    no_ai_needed = any(
        marker in value
        for marker in (
            "kein engpass",
            "keine probleme",
            "bestehende softwarefunktion reicht aus",
            "einfache regel reicht aus",
        )
    )
    if no_ai_needed or not problem_family_ids:
        task_fit: GateStatus = "fail"
        task_reason = "Es ist kein belegter Engpass erkennbar, für den KI nötig wäre."
    elif "PF-05" in problem_family_ids and not gates.physical_object:
        task_fit = "unknown"
        task_reason = "Ein echter physischer Gegenstand ist noch nicht bestätigt."
    else:
        task_fit = "pass"
        task_reason = "Der beschriebene Engpass passt zu einer abgegrenzten Unterstützungsaufgabe."

    def level_status(level: GateLevel) -> GateStatus:
        if level in {"medium", "high"}:
            return "pass"
        if level == "low":
            return "fail"
        return "unknown"

    anchor_status = level_status(gates.transaction_anchor)
    output_status = level_status(gates.process_data_maturity)
    if any(
        marker in value
        for marker in ("ohne prüfung", "ohne freigabe", "vollautomatisch entscheiden")
    ):
        review_status: GateStatus = "fail"
        review_reason = "Eine notwendige menschliche Prüfung wird ausdrücklich ausgeschlossen."
    elif gates.human_approval == "unknown":
        review_status = "unknown"
        review_reason = "Die verantwortliche menschliche Prüfung ist noch nicht bestätigt."
    else:
        review_status = "pass"
        review_reason = "Eine menschliche Prüfung kann als verbindliche Grenze vorgesehen werden."

    if gates.error_impact == "high" and review_status != "pass":
        impact_status: GateStatus = "fail"
        impact_reason = "Hohe Fehlerfolgen sind ohne bestätigte menschliche Prüfung nicht vertretbar."
    elif gates.error_impact == "unknown":
        impact_status = "unknown"
        impact_reason = "Die möglichen Fehlerfolgen sind noch nicht angegeben."
    else:
        impact_status = "pass"
        impact_reason = "Die Fehlerfolgen bleiben mit menschlicher Prüfung begrenzbar."

    permission_fail = any(
        marker in value
        for marker in ("keine berechtigung", "nicht erlaubt", "ohne einwilligung")
    )
    permission_pass = any(
        marker in value
        for marker in (
            "berechtigung liegt vor",
            "einwilligung liegt vor",
            "zugriff ist erlaubt",
        )
    )
    if permission_fail:
        permission_status: GateStatus = "fail"
        permission_reason = "Die notwendige Berechtigung oder Einwilligung fehlt ausdrücklich."
    elif permission_pass:
        permission_status = "pass"
        permission_reason = "Die notwendige Berechtigung oder Einwilligung ist bestätigt."
    else:
        permission_status = "unknown"
        permission_reason = "Berechtigungen und Einwilligungen sind noch nicht angegeben."

    return [
        GateAssessment(gate_id="GATE-01", status=task_fit, reason=task_reason),
        GateAssessment(
            gate_id="GATE-02",
            status=anchor_status,
            reason=(
                "Ein eindeutiger Vorgangsanker ist vorhanden."
                if anchor_status == "pass"
                else "Ein eindeutiger Vorgangsanker fehlt."
                if anchor_status == "fail"
                else "Der Vorgangsanker ist noch nicht angegeben."
            ),
        ),
        GateAssessment(
            gate_id="GATE-03",
            status=output_status,
            reason=(
                "Ein prüfbarer Zieloutput lässt sich festlegen."
                if output_status == "pass"
                else "Ein prüfbarer Zieloutput ist noch nicht ausreichend strukturiert."
                if output_status == "fail"
                else "Der prüfbare Zieloutput ist noch nicht angegeben."
            ),
        ),
        GateAssessment(gate_id="GATE-04", status=review_status, reason=review_reason),
        GateAssessment(gate_id="GATE-05", status=impact_status, reason=impact_reason),
        GateAssessment(gate_id="GATE-06", status=permission_status, reason=permission_reason),
    ]


def _target_fit(gates: DecisionGates, confirmed_text: str) -> tuple[GateStatus, str]:
    value = confirmed_text.casefold()
    if any(
        marker in value
        for marker in ("nur papier", "rein analog", "keinen digitalen kanal")
    ):
        return "fail", "Der Fall hat noch keinen digitalen Ausgangskanal."
    if gates.physical_object and any(
        marker in value
        for marker in ("lagerordnung", "regalordnung", "objektkennzeichnung")
    ):
        return "fail", "Das Hauptproblem ist physische Lagerung oder Kennzeichnung."
    if any(
        marker in value
        for marker in (
            "preis automatisch",
            "zahlung automatisch",
            "personal automatisch",
            "ohne freigabe entscheiden",
        )
    ):
        return (
            "fail",
            "Die gewünschte autonome Geschäftsentscheidung liegt außerhalb des sicheren Zielbereichs.",
        )
    if gates.channel_suitability in {"medium", "high"}:
        return "pass", "Mindestens ein digitaler Arbeitskanal ist vorhanden."
    if gates.channel_suitability == "low":
        return "fail", "Ein geeigneter digitaler Arbeitskanal ist nicht erkennbar."
    return "unknown", "Ein geeigneter digitaler Arbeitskanal ist noch nicht bestätigt."


def _determine_autonomy(
    assessments: list[GateAssessment], target_fit: GateStatus
) -> AutonomyLevelId:
    statuses = {item.gate_id: item.status for item in assessments}
    if target_fit == "fail" or statuses["GATE-01"] == "fail":
        return "A0"
    if any(
        statuses[gate] == "fail" for gate in ("GATE-04", "GATE-05", "GATE-06")
    ):
        return "A0"
    if target_fit == "unknown" or any(
        statuses[gate] != "pass"
        for gate in ("GATE-02", "GATE-03", "GATE-04", "GATE-05", "GATE-06")
    ):
        return "A1"
    return "A2"


def _explicit_non_ai_first(confirmed_text: str) -> bool:
    """Honor an explicit, grounded choice to use an existing simple function."""

    value = confirmed_text.casefold()
    no_ai_markers = (
        "keine ki nötig",
        "keine ki notwendig",
        "ki ist nicht nötig",
        "ki ist nicht notwendig",
        "dafür ist keine ki nötig",
        "dafür ist keine ki notwendig",
    )
    simple_solution_markers = (
        "bestehende funktion",
        "bestehende softwarefunktion",
        "vorhandene funktion",
        "vorhandene softwarefunktion",
        "erinnerungsfunktion",
        "einfache regel",
    )
    rejection_markers = (
        "reicht nicht aus",
        "genügt nicht",
        "funktioniert nicht",
    )
    return (
        any(marker in value for marker in no_ai_markers)
        and any(marker in value for marker in simple_solution_markers)
        and not any(marker in value for marker in rejection_markers)
    )


def select_recommendation(
    problem_family_ids: list[str],
    gates: DecisionGates,
    *,
    catalog: RecommendationCatalog | None = None,
    confirmed_text: str = "",
) -> RecommendationSelection:
    data = catalog or load_recommendation_catalog()
    by_id = {item.solution_id: item for item in data.solution_patterns}
    mappings = {item.problem_family_id: item for item in data.matrix}
    unknown_family_ids = sorted(set(problem_family_ids) - set(mappings))
    if unknown_family_ids:
        raise ValueError(f"Unbekannte Problemfamilien: {', '.join(unknown_family_ids)}")
    assessments = evaluate_gate_cascade(
        problem_family_ids, gates, confirmed_text=confirmed_text
    )
    target_fit, target_fit_reason = _target_fit(gates, confirmed_text)
    autonomy_level = _determine_autonomy(assessments, target_fit)
    if _explicit_non_ai_first(confirmed_text):
        autonomy_level = "A0"
    if autonomy_level == "A0" or not problem_family_ids:
        return RecommendationSelection(
            problem_family_ids=problem_family_ids,
            primary=None,
            secondary=[],
            excluded_reasons={},
            required_prerequisites=[],
            human_approval_boundaries=[],
            gate_assessments=assessments,
            autonomy_level="A0",
            recommendation_mode="non_ai_first",
            a0_recommendation=(
                "Nutze zuerst eine einfache Regel, klare Ablage oder eine vorhandene "
                "Softwarefunktion. KI ist für den beschriebenen Stand nicht notwendig."
            ),
            stop_conditions=[],
            target_fit=target_fit,
            target_fit_reason=target_fit_reason,
        )
    candidates: list[str] = []
    prerequisites: list[str] = []
    for family_id in problem_family_ids:
        mapping = mappings[family_id]
        candidates.extend(mapping.primary_solution_ids + mapping.supplementary_solution_ids)
        if gates.transaction_anchor in {"unknown", "low"}:
            prerequisites.append(mapping.hard_prerequisite)
    candidates = list(dict.fromkeys(candidates))
    excluded: dict[str, list[str]] = {}
    if not gates.physical_object and "SP-04" in candidates:
        excluded.setdefault("SP-04", []).append(
            "Kein angenommener, gelagerter, bearbeiteter oder abgeholter Gegenstand ist bestätigt."
        )
    if gates.physical_object and not gates.real_location_known:
        for candidate in candidates:
            if candidate != "SP-04":
                excluded.setdefault(candidate, []).append("Physische Identität und realer Ort sind noch nicht bestätigt.")
        candidates = ["SP-04", *[item for item in candidates if item != "SP-04"]]
    if "PF-08" in problem_family_ids and gates.channel_suitability in {"medium", "high"}:
        candidates = ["SP-03", *[item for item in candidates if item != "SP-03"]]
    if "PF-06" in problem_family_ids:
        candidates = ["SP-05", *[item for item in candidates if item != "SP-05"]]
    allowed = [item for item in candidates if item not in excluded]
    if not allowed:
        return RecommendationSelection(
            problem_family_ids=problem_family_ids,
            primary=None,
            secondary=[],
            excluded_reasons=excluded,
            required_prerequisites=list(dict.fromkeys(prerequisites))[:3],
            human_approval_boundaries=[],
            gate_assessments=assessments,
            autonomy_level="A0",
            recommendation_mode="non_ai_first",
            a0_recommendation=(
                "Kläre zuerst den Vorgangsanker und den realen Prozess. "
                "Eine KI-Empfehlung wäre derzeit nicht fachlich belastbar."
            ),
            stop_conditions=[],
            target_fit=target_fit,
            target_fit_reason=target_fit_reason,
        )
    primary_id = allowed[0]
    secondary_ids = [item for item in allowed[1:] if item != primary_id][:2]
    approval_boundaries = [by_id[primary_id].human_check]
    if gates.error_impact == "high" or gates.human_approval in {"medium", "high"}:
        approval_boundaries.extend(by_id[primary_id].security_guardrails)
    return RecommendationSelection(
        problem_family_ids=problem_family_ids,
        primary=by_id[primary_id],
        secondary=[by_id[item] for item in secondary_ids],
        excluded_reasons=excluded,
        required_prerequisites=list(dict.fromkeys(prerequisites))[:3],
        human_approval_boundaries=list(dict.fromkeys(approval_boundaries)),
        gate_assessments=assessments,
        autonomy_level=autonomy_level,
        recommendation_mode="ai_assisted",
        a0_recommendation="",
        stop_conditions=by_id[primary_id].stop_conditions,
        target_fit=target_fit,
        target_fit_reason=target_fit_reason,
    )
