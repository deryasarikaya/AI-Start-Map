from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


NonEmptyText = Annotated[str, Field(min_length=1)]

INTERNAL_REFERENCE_PATTERN = re.compile(
    r"\b(?:bekannter\s+testfall|testfall|rag[-\s]?fall|referenzfall|"
    r"evaluationsfall|chunk(?:-id)?|content_origin|pattern_ids?|case_id|"
    r"document_id|source_url|is_primary_evidence)\b",
    re.IGNORECASE,
)
INTERNAL_IDENTIFIER_PATTERN = re.compile(
    r"\b(?:(?:EVAL-)?[MCKP]-\d{2}(?:[_-][A-Z0-9_]+)*|"
    r"RB(?:02|03|04)-[A-Z0-9]+(?:-[A-Z0-9]+)*)\b",
    re.IGNORECASE,
)
INTERNAL_FILE_PATTERN = re.compile(
    r"(?:knowledge[/\\](?:curated|raw|evaluation)|"
    r"(?:original_[\w-]+|[\w-]+_rag_corpus|evaluation_cases)"
    r"\.(?:md|pdf|json))",
    re.IGNORECASE,
)
PROHIBITED_CUSTOMER_LANGUAGE_PATTERN = re.compile(
    r"\b(?:intake(?:-kit)?|audit-track|wip|mapping|lookup|semi-automatisiert|"
    r"formulardoppie|nachschlageort|übergabevermerkgabel|"
    r"handschriftenkapazität)\b",
    re.IGNORECASE,
)
FOLLOW_UP_SOLUTION_PATTERN = re.compile(
    r"\b(?:sollte|sollten|könnte|könnten|würde|würden|empfehlen|"
    r"automatisier\w*|software|app|schnittstelle|api|zum beispiel|"
    r"verbindliche regel|nach \w+ tagen)\b",
    re.IGNORECASE,
)
CURRENT_PROCESS_PATTERN = re.compile(
    r"\b(?:heute|aktuell|derzeit|momentan|bisher|tatsächlich)\b",
    re.IGNORECASE,
)
SUMMARY_META_PATTERN = re.compile(
    r"^(?:prozessname:|ausgewählter prozess:|der prozess heißt|"
    r"aus den vorliegenden angaben|auf grundlage der daten|quelle:|"
    r"die rekonstruktion bleibt unsicher)",
    re.IGNORECASE,
)
AS_IS_META_PATTERN = re.compile(
    r"\b(?:unbekannt|nicht beschrieben|detaillierte schritte fehlen|"
    r"laut prozessname|bekannte einschränkung)\b",
    re.IGNORECASE,
)


def contains_internal_reference(value: Any) -> bool:
    if isinstance(value, str):
        return any(
            pattern.search(value) is not None
            for pattern in (
                INTERNAL_REFERENCE_PATTERN,
                INTERNAL_IDENTIFIER_PATTERN,
                INTERNAL_FILE_PATTERN,
            )
        )
    if isinstance(value, BaseModel):
        return contains_internal_reference(value.model_dump())
    if isinstance(value, Mapping):
        return any(contains_internal_reference(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(contains_internal_reference(item) for item in value)
    return False


def contains_prohibited_customer_language(value: Any) -> bool:
    if isinstance(value, str):
        return PROHIBITED_CUSTOMER_LANGUAGE_PATTERN.search(value) is not None
    if isinstance(value, BaseModel):
        return contains_prohibited_customer_language(value.model_dump())
    if isinstance(value, Mapping):
        return any(
            contains_prohibited_customer_language(item) for item in value.values()
        )
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(contains_prohibited_customer_language(item) for item in value)
    return False


class StrictResultModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @model_validator(mode="after")
    def reject_internal_references(self) -> StrictResultModel:
        if contains_internal_reference(self.model_dump()):
            raise ValueError(
                "Interne Wissensreferenzen dürfen nicht ausgegeben werden."
            )
        if contains_prohibited_customer_language(self.model_dump()):
            raise ValueError("Die Ausgabe enthält unverständliche Fachbegriffe.")
        return self


class ProcessBoundaryResult(StrictResultModel):
    process_name: NonEmptyText
    start_event: NonEmptyText
    end_event: NonEmptyText

    @model_validator(mode="after")
    def reject_general_category(self) -> ProcessBoundaryResult:
        if self.process_name.casefold() in {
            "marketing",
            "organisation",
            "kundenkommunikation",
        }:
            raise ValueError("Die Beschreibung muss ein konkreter Ablauf sein.")
        return self


class ProcessSuggestion(StrictResultModel):
    process_name: NonEmptyText
    start_event: NonEmptyText
    end_event: NonEmptyText
    reason: NonEmptyText

    @model_validator(mode="after")
    def reject_general_category(self) -> ProcessSuggestion:
        if self.process_name.casefold() in {
            "marketing",
            "organisation",
            "kundenkommunikation",
        }:
            raise ValueError("Der Vorschlag muss ein konkreter Prozess sein.")
        return self


class ProcessSuggestionResult(StrictResultModel):
    suggestions: list[ProcessSuggestion] = Field(min_length=1, max_length=3)


class ProcessUnderstandingResult(StrictResultModel):
    process_name: NonEmptyText
    start_event: NonEmptyText
    end_event: NonEmptyText
    as_is_steps: list[NonEmptyText] = Field(min_length=2, max_length=7)
    confirmed_facts: list[NonEmptyText] = Field(max_length=6)
    difficult_points: list[NonEmptyText] = Field(max_length=4)
    problem_step_indexes: list[int] = Field(default_factory=list, max_length=4)
    open_points: list[NonEmptyText] = Field(max_length=4)

    @model_validator(mode="after")
    def validate_problem_step_indexes(self) -> ProcessUnderstandingResult:
        if len(set(self.problem_step_indexes)) != len(self.problem_step_indexes):
            raise ValueError("Problemstellen dürfen nicht doppelt markiert werden.")
        if any(index < 0 or index >= len(self.as_is_steps) for index in self.problem_step_indexes):
            raise ValueError("Eine markierte Problemstelle liegt außerhalb des Ablaufs.")
        return self


class FollowUpQuestion(StrictResultModel):
    question: NonEmptyText
    issue_type: Literal[
        "missing",
        "ambiguous",
        "approximate",
        "self_correction",
        "contradiction",
        "critical_unknown",
    ]

    @model_validator(mode="after")
    def validate_current_process_question(self) -> FollowUpQuestion:
        if not self.question.endswith("?"):
            raise ValueError("Eine Rückfrage muss als einzelne Frage formuliert sein.")
        if CURRENT_PROCESS_PATTERN.search(self.question) is None:
            raise ValueError("Eine Rückfrage muss nach dem heutigen Ablauf fragen.")
        if FOLLOW_UP_SOLUTION_PATTERN.search(self.question) is not None:
            raise ValueError("Eine Rückfrage darf keine Lösung oder Regel vorschlagen.")
        return self


class FollowUpResult(StrictResultModel):
    questions: list[FollowUpQuestion] = Field(max_length=4)

    @model_validator(mode="after")
    def validate_unique_questions(self) -> FollowUpResult:
        normalized = {question.question.casefold().rstrip(" ?!.") for question in self.questions}
        if len(normalized) != len(self.questions):
            raise ValueError("Rückfragen dürfen nicht doppelt vorkommen.")
        return self


class AutomationOpportunityResult(StrictResultModel):
    rank: int = Field(ge=1, le=3)
    title: NonEmptyText
    problem: NonEmptyText
    recommendation: NonEmptyText
    benefit: NonEmptyText
    human_approval: NonEmptyText
    first_step: NonEmptyText
    category: Literal[
        "Ordnung und Standardisierung",
        "einfache Digitalisierung",
        "regelbasierte Automatisierung",
        "KI-Unterstützung",
    ] = "einfache Digitalisierung"
    prerequisite: str = ""
    mini_test: list[NonEmptyText] = Field(default_factory=list, max_length=5)
    effort: Literal["niedrig", "mittel", "hoch"] = "mittel"
    acceptance_risk: str = ""


class AutomationBlueprint(StrictResultModel):
    objective: NonEmptyText
    trigger: NonEmptyText
    required_inputs: list[NonEmptyText]
    workflow_steps: list[NonEmptyText] = Field(min_length=1)
    human_review_point: NonEmptyText
    output: NonEmptyText
    exceptions: list[NonEmptyText]


class FinalAnalysisResult(StrictResultModel):
    process_summary: NonEmptyText
    as_is_steps: list[NonEmptyText] = Field(min_length=1)
    core_bottleneck: NonEmptyText
    bottleneck_symptom: str = ""
    bottleneck_cause: str = ""
    bottleneck_effect: str = ""
    as_is_problem_step_indexes: list[int] = Field(default_factory=list, max_length=4)
    to_be_steps: list[NonEmptyText] = Field(default_factory=list, max_length=7)
    uncertainties: list[NonEmptyText] = Field(max_length=4)
    opportunities: list[AutomationOpportunityResult] = Field(
        min_length=3,
        max_length=3,
    )
    blueprint: AutomationBlueprint

    @model_validator(mode="after")
    def validate_unique_ranks(self) -> FinalAnalysisResult:
        ranks = sorted(opportunity.rank for opportunity in self.opportunities)
        if ranks != [1, 2, 3]:
            raise ValueError("Die Chancen müssen genau die Ränge 1, 2 und 3 haben.")
        if SUMMARY_META_PATTERN.search(self.process_summary) is not None:
            raise ValueError("Die Zusammenfassung darf keine Meta-Einleitung enthalten.")
        if any(AS_IS_META_PATTERN.search(step) is not None for step in self.as_is_steps):
            raise ValueError("Der Ist-Ablauf darf keine Meta- oder Fehlangaben enthalten.")
        normalized_uncertainties = {
            uncertainty.casefold().rstrip(".?!") for uncertainty in self.uncertainties
        }
        if len(normalized_uncertainties) != len(self.uncertainties):
            raise ValueError("Unsicherheiten dürfen nicht doppelt vorkommen.")
        if any(index < 0 or index >= len(self.as_is_steps) for index in self.as_is_problem_step_indexes):
            raise ValueError("Eine markierte Problemstelle liegt außerhalb des Ist-Ablaufs.")
        combined_opportunities = " ".join(
            f"{opportunity.title} {opportunity.recommendation}"
            for opportunity in self.opportunities
        ).casefold()
        manual_markers = ("papierformular", "ringordner", "stempel", "wand-board")
        useful_markers = (
            "digital",
            "automatisch",
            "automatisiert",
            "automatisierung",
            "statusübersicht",
        )
        if (
            sum(marker in combined_opportunities for marker in manual_markers) >= 2
            and not any(marker in combined_opportunities for marker in useful_markers)
        ):
            raise ValueError(
                "Die Chancen dürfen nicht ausschließlich manuelle Hilfsmittel sein."
            )
        return self
