from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
RUNTIME_DIRECTORY = ROOT_DIRECTORY / "knowledge" / "runtime"
OUTPUT_STRUCTURES_FILE = RUNTIME_DIRECTORY / "output_structures.jsonl"
INFERENCE_PATTERNS_FILE = (
    RUNTIME_DIRECTORY / "patterns" / "inference_patterns.jsonl"
)
SOLUTION_WORKFLOWS_FILE = (
    RUNTIME_DIRECTORY / "solution_knowledge" / "solution_workflows.jsonl"
)

ProblemFamilyId = Literal[
    "PF-01", "PF-02", "PF-03", "PF-04", "PF-05", "PF-06",
    "PF-07", "PF-08", "PF-09", "PF-10", "PF-11", "PF-12",
]
SolutionPatternId = Literal[
    "SP-01", "SP-02", "SP-03", "SP-04", "SP-05",
    "SP-06", "SP-07", "SP-08", "SP-09", "SP-10",
]
RuntimeQualityStatus = Literal["runtime_approved"]
WorkflowActor = Literal["user", "ai", "software_rule", "human"]


class KnowledgeModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class OutputFieldDefinition(KnowledgeModel):
    field_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    data_type: str = Field(min_length=1)
    required: bool
    example_value: str = Field(min_length=1)
    source_types: list[str] = Field(min_length=1)
    requires_human_input: bool


class OutputStructure(KnowledgeModel):
    output_id: str
    name: str
    solution_pattern_id: SolutionPatternId
    description: str
    fields: list[OutputFieldDefinition] = Field(min_length=1)
    typical_missing_information: list[str]
    attachments: list[str]
    human_review: str
    system_must_not_decide: list[str] = Field(min_length=1)
    placeholder_notice: str
    source_refs: list[str] = Field(min_length=1)
    content_origin: Literal["expert_derived"]
    scope: Literal["base"]
    source_batch: Literal["batch_09"]
    quality_status: RuntimeQualityStatus

    @model_validator(mode="after")
    def validate_fields(self) -> "OutputStructure":
        field_ids = [field.field_id for field in self.fields]
        if len(field_ids) != len(set(field_ids)):
            raise ValueError(f"Doppelte Feld-ID in {self.output_id}.")
        if any("kein kundenfakt" not in field.example_value.casefold() for field in self.fields):
            raise ValueError("Beispielwerte müssen ausdrücklich als Nicht-Kundenfakt markiert sein.")
        return self


class PatternApplicability(KnowledgeModel):
    maturity_min: int = Field(ge=0, le=4)
    maturity_max: int = Field(ge=0, le=4)
    channels: list[str]
    business_types: list[str]


class AnswerBranch(KnowledgeModel):
    answer_pattern: str
    diagnostic_effect: str


class InferencePattern(KnowledgeModel):
    pattern_id: str
    name: str
    customer_phrasings: list[str] = Field(min_length=1)
    hypothesis: str
    hypothesis_status: Literal["must_be_confirmed"]
    mechanism: str
    verification_question: str
    answer_branches: list[AnswerBranch] = Field(min_length=2, max_length=2)
    minimum_foundation: str
    smallest_ai_step: str
    later_stage: str
    applies_to: PatternApplicability
    problem_family_ids: list[ProblemFamilyId] = Field(min_length=1)
    solution_pattern_ids: list[SolutionPatternId] = Field(min_length=1)
    evidence_type: str
    source_count: int = Field(ge=1)
    source_refs: list[str] = Field(min_length=1)
    source_strength: str
    content_origin: Literal["source_synthesized"]
    source_batch: Literal["batch_09"]
    quality_status: RuntimeQualityStatus


class WorkflowStep(KnowledgeModel):
    step: int = Field(ge=1)
    actor: WorkflowActor
    action: str


class SolutionWorkflow(KnowledgeModel):
    chunk_id: str
    chunk_type: Literal["solution_workflow"]
    workflow_id: str
    solution_pattern_id: SolutionPatternId
    title: str
    business_type: str
    channels: list[str]
    maturity: list[int] = Field(min_length=2, max_length=2)
    starting_situation: str
    required_inputs: list[str] = Field(min_length=1)
    minimum_foundation: list[str] = Field(min_length=1)
    target_workflow: list[WorkflowStep] = Field(min_length=3, max_length=6)
    visible_output: str
    human_checks: list[str] = Field(min_length=1)
    not_automated: list[str] = Field(min_length=1)
    smallest_usable_version: str
    later_stage: str
    failure_modes: list[str] = Field(min_length=1)
    success_signals: list[str] = Field(min_length=1)
    source_refs: list[str] = Field(min_length=1)
    source_strength: Literal["reviewed_synthesis"]
    content_origin: Literal["source_synthesized"]
    batch_scope: Literal["in_scope", "documentary_only"]
    source_batch: Literal["batch_09"]
    quality_status: RuntimeQualityStatus

    @model_validator(mode="after")
    def validate_steps(self) -> "SolutionWorkflow":
        if self.chunk_id != self.workflow_id:
            raise ValueError("Chunk-ID und Workflow-ID müssen identisch sein.")
        expected = list(range(1, len(self.target_workflow) + 1))
        if [step.step for step in self.target_workflow] != expected:
            raise ValueError(f"Ungültige Schrittfolge in {self.workflow_id}.")
        if self.batch_scope == "documentary_only" and self.solution_pattern_id != "SP-04":
            raise ValueError("Nur SP-04 darf im Batch dokumentarisch bleiben.")
        return self


def _read_jsonl(path: Path, result_type: type[KnowledgeModel]) -> list[Any]:
    if "evaluation" in str(path).casefold():
        raise ValueError("Evaluationen dürfen nicht als Runtime-Wissen geladen werden.")
    rows: list[Any] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(result_type.model_validate_json(line))
        except Exception as error:
            raise ValueError(f"Ungültiges Runtime-Wissen in {path}:{line_number}.") from error
    return rows


def load_output_structures(path: Path = OUTPUT_STRUCTURES_FILE) -> list[OutputStructure]:
    structures = _read_jsonl(path, OutputStructure)
    expected = [f"SP-{index:02d}" for index in range(1, 11)]
    if [item.solution_pattern_id for item in structures] != expected:
        raise ValueError("Output-Strukturen müssen SP-01 bis SP-10 genau einmal abdecken.")
    return structures


def output_structure_for(
    solution_pattern_id: str,
    *,
    structures: list[OutputStructure] | None = None,
) -> OutputStructure | None:
    return next(
        (
            item
            for item in (structures or load_output_structures())
            if item.solution_pattern_id == solution_pattern_id
        ),
        None,
    )


def output_structure_context(structure: OutputStructure | None) -> dict[str, object]:
    if structure is None:
        return {
            "status": "missing",
            "notice": "Für dieses Lösungsmuster ist noch keine freigegebene Ergebnisstruktur vorhanden.",
            "fields": [],
            "required_fields": [],
            "human_review": "noch offen",
            "system_must_not_decide": [],
        }
    fields = [
        {
            "field_id": field.field_id,
            "label": field.label,
            "data_type": field.data_type,
            "required": field.required,
            "source_types": field.source_types,
            "requires_human_input": field.requires_human_input,
        }
        for field in structure.fields
    ]
    return {
        "status": structure.quality_status,
        "name": structure.name,
        "fields": fields,
        "required_fields": [field["label"] for field in fields if field["required"]],
        "typical_missing_information": structure.typical_missing_information,
        "attachments": structure.attachments,
        "human_review": structure.human_review,
        "system_must_not_decide": structure.system_must_not_decide,
        "placeholder_notice": structure.placeholder_notice,
    }


def load_inference_patterns(path: Path = INFERENCE_PATTERNS_FILE) -> list[InferencePattern]:
    patterns = _read_jsonl(path, InferencePattern)
    expected = [f"IP-{index:02d}" for index in range(1, 28)]
    if [item.pattern_id for item in patterns] != expected:
        raise ValueError("Inference Patterns müssen IP-01 bis IP-27 genau einmal enthalten.")
    return patterns


def find_inference_patterns(
    problem_family_ids: list[str],
    *,
    channels: set[str] | None = None,
    limit: int = 3,
    patterns: list[InferencePattern] | None = None,
) -> list[InferencePattern]:
    if limit < 1:
        raise ValueError("limit muss positiv sein.")
    confirmed_channels = {item.casefold() for item in channels or set()}
    candidates = [
        item
        for item in (patterns or load_inference_patterns())
        if set(item.problem_family_ids) & set(problem_family_ids)
    ]
    return sorted(
        candidates,
        key=lambda item: (
            -len(confirmed_channels & {channel.casefold() for channel in item.applies_to.channels}),
            item.pattern_id,
        ),
    )[:limit]


def load_solution_workflows(path: Path = SOLUTION_WORKFLOWS_FILE) -> list[SolutionWorkflow]:
    workflows = _read_jsonl(path, SolutionWorkflow)
    if len(workflows) != 28 or len({item.workflow_id for item in workflows}) != 28:
        raise ValueError("Die Runtime muss 28 eindeutige Batch-09-Workflows enthalten.")
    if sum(item.batch_scope == "documentary_only" for item in workflows) != 1:
        raise ValueError("Genau der dokumentarische SP-04-Eintrag muss ausgeschlossen bleiben.")
    return workflows


def select_solution_workflows(
    solution_pattern_id: str,
    *,
    business_type: str | None = None,
    channels: set[str] | None = None,
    limit: int = 2,
    workflows: list[SolutionWorkflow] | None = None,
) -> list[SolutionWorkflow]:
    if limit < 1:
        raise ValueError("limit muss positiv sein.")
    confirmed_channels = {item.casefold() for item in channels or set()}
    normalized_business = (business_type or "").casefold()
    candidates = [
        item
        for item in (workflows or load_solution_workflows())
        if item.solution_pattern_id == solution_pattern_id
        and item.batch_scope == "in_scope"
    ]
    return sorted(
        candidates,
        key=lambda item: (
            -(3 if normalized_business and item.business_type == normalized_business else 0),
            -len(confirmed_channels & {channel.casefold() for channel in item.channels}),
            item.workflow_id,
        ),
    )[:limit]


def solution_workflow_context(
    workflows: list[SolutionWorkflow],
) -> list[dict[str, object]]:
    return [
        {
            "starting_situation": item.starting_situation,
            "required_inputs": item.required_inputs,
            "minimum_foundation": item.minimum_foundation,
            "target_workflow": [step.model_dump() for step in item.target_workflow],
            "visible_output": item.visible_output,
            "human_checks": item.human_checks,
            "not_automated": item.not_automated,
            "smallest_usable_version": item.smallest_usable_version,
            "later_stage": item.later_stage,
            "failure_modes": item.failure_modes,
        }
        for item in workflows
    ]


def extract_confirmed_channels(text: str) -> set[str]:
    value = text.casefold()
    aliases = {
        "whatsapp": ("whatsapp",),
        "email": ("e-mail", "email", "mail"),
        "instagram": ("instagram",),
        "pdf": ("pdf",),
        "foto": ("foto", "bilder"),
        "sprache": ("sprache", "sprachnachricht", "audio"),
        "kalender": ("kalender",),
        "formular": ("formular",),
        "tabelle": ("tabelle", "excel"),
        "bon": ("bon", "beleg"),
    }
    return {
        channel
        for channel, markers in aliases.items()
        if any(marker in value for marker in markers)
    }


def build_solution_query(
    *,
    problem_family_ids: list[str],
    solution_pattern_id: str,
    bottleneck: str,
    channels: set[str],
    business_type: str | None = None,
) -> str:
    parts = [
        f"Bestätigte Problemfamilien: {', '.join(problem_family_ids)}",
        f"Ausgewähltes Lösungsmuster: {solution_pattern_id}",
        f"Konkreter Engpass: {bottleneck}",
    ]
    if channels:
        parts.append(f"Bestätigte digitale Kanäle: {', '.join(sorted(channels))}")
    if business_type:
        parts.append(f"Betriebstyp: {business_type}")
    return "\n".join(parts)
