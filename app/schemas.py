from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


NonEmptyText = Annotated[str, Field(min_length=1)]


class StrictResultModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


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


class FollowUpResult(StrictResultModel):
    questions: list[FollowUpQuestion] = Field(max_length=3)


class AutomationOpportunityResult(StrictResultModel):
    rank: int = Field(ge=1, le=3)
    title: NonEmptyText
    problem: NonEmptyText
    recommendation: NonEmptyText
    benefit: NonEmptyText
    human_approval: NonEmptyText
    first_step: NonEmptyText


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
    uncertainties: list[NonEmptyText]
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
        return self
