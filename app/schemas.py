from __future__ import annotations

import logging
import re
from collections.abc import Mapping, Sequence
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


logger = logging.getLogger(__name__)


def _final_analysis_json_schema(schema: dict[str, Any]) -> None:
    """Keep legacy bookkeeping private and require the current runtime contract."""

    properties = schema.get("properties", {})
    if isinstance(properties, dict):
        properties.pop("legacy_filled_fields", None)
    required = schema.setdefault("required", [])
    if isinstance(required, list):
        for field_name in (
            "software_rule",
            "open_details",
            "smallest_usable_version",
            "not_automated",
            "autonomy_level",
        ):
            if field_name not in required:
                required.append(field_name)


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
    r"(?:knowledge[/\\](?:runtime|candidates|evaluation|archive|curated|raw|patterns)|"
    r"(?:original_[\w-]+|[\w-]+_rag_corpus|evaluation_cases)"
    r"\.(?:md|pdf|json))",
    re.IGNORECASE,
)
PROHIBITED_CUSTOMER_LANGUAGE_PATTERN = re.compile(
    r"\b(?:formulardoppie|nachschlageort|übergabevermerkgabel|"
    r"handschriftenkapazität)\b",
    re.IGNORECASE,
)
DISTANT_CUSTOMER_LANGUAGE_PATTERN = re.compile(
    r"\b(?:der Nutzer|die Nutzerin|der Unternehmer|der Mitarbeiter|"
    r"die Person|man sollte)\b",
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


def _neutralize_internal_reference_fields(value: Any) -> tuple[Any, bool]:
    if isinstance(value, str):
        if contains_internal_reference(value):
            return "noch offen", True
        return value, False
    if isinstance(value, Mapping):
        changed = False
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            normalized_item, item_changed = _neutralize_internal_reference_fields(item)
            normalized[str(key)] = normalized_item
            changed = changed or item_changed
        return normalized, changed
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        changed = False
        normalized_items: list[Any] = []
        for item in value:
            normalized_item, item_changed = _neutralize_internal_reference_fields(item)
            normalized_items.append(normalized_item)
            changed = changed or item_changed
        return normalized_items, changed
    return value, False


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
    as_is_steps: list[NonEmptyText] = Field(min_length=2, max_length=5)
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
    workflow_steps: list[NonEmptyText] = Field(min_length=3, max_length=5)
    human_review_point: NonEmptyText
    output: NonEmptyText
    exceptions: list[NonEmptyText]


class OptionalAnalysisDetails(StrictResultModel):
    current_difficulties: list[NonEmptyText] = Field(default_factory=list, max_length=4)
    additional_prerequisites: list[NonEmptyText] = Field(
        default_factory=list, max_length=4
    )
    later_possibilities: list[NonEmptyText] = Field(default_factory=list, max_length=3)


class SampleOutputField(StrictResultModel):
    label: Annotated[str, Field(min_length=1, max_length=45)]
    value: Annotated[str, Field(min_length=1, max_length=140)]


class SampleOutput(StrictResultModel):
    title: Annotated[str, Field(min_length=1, max_length=80)]
    fields: list[SampleOutputField] = Field(min_length=1, max_length=6)
    open_items: list[Annotated[str, Field(min_length=1, max_length=120)]] = Field(
        default_factory=list, max_length=4
    )
    attachments: list[Annotated[str, Field(min_length=1, max_length=80)]] = Field(
        default_factory=list, max_length=3
    )
    preview_notice: Annotated[str, Field(min_length=1, max_length=100)] = (
        "Vorschau – die endgültigen Angaben prüfst du selbst."
    )


class SecondaryOpportunity(StrictResultModel):
    title: Annotated[str, Field(min_length=1, max_length=90)]
    description: Annotated[str, Field(min_length=1, max_length=220)]


class FinalAnalysisResult(StrictResultModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra=_final_analysis_json_schema,
    )

    primary_recommendation: Annotated[str, Field(min_length=1, max_length=110)]
    promise: Annotated[str, Field(min_length=1, max_length=220)]
    short_reason: Annotated[str, Field(min_length=1, max_length=300)]
    before_process: list[Annotated[str, Field(min_length=1, max_length=140)]] = Field(
        min_length=1, max_length=3
    )
    future_process: list[Annotated[str, Field(min_length=1, max_length=140)]] = Field(
        min_length=3, max_length=6
    )
    sample_output: SampleOutput
    user_action: Annotated[str, Field(min_length=1, max_length=180)]
    ai_task: Annotated[str, Field(min_length=1, max_length=180)]
    visible_result: Annotated[str, Field(min_length=1, max_length=180)]
    human_check: Annotated[str, Field(min_length=1, max_length=200)]
    software_rule: Annotated[str, Field(max_length=180)] = ""
    customer_benefits: list[Annotated[str, Field(min_length=1, max_length=140)]] = Field(
        min_length=1, max_length=3
    )
    required_prerequisites: list[
        Annotated[str, Field(min_length=1, max_length=140)]
    ] = Field(default_factory=list, max_length=3)
    implementation_path: list[
        Annotated[str, Field(min_length=1, max_length=160)]
    ] = Field(min_length=2, max_length=4)
    later_stage: Annotated[str, Field(max_length=220)] = ""
    open_details: list[
        Annotated[str, Field(min_length=1, max_length=140)]
    ] = Field(default_factory=list, max_length=6)
    smallest_usable_version: Annotated[str, Field(max_length=220)] = ""
    not_automated: list[
        Annotated[str, Field(min_length=1, max_length=160)]
    ] = Field(default_factory=list, max_length=5)
    autonomy_level: Literal["A0", "A1", "A2", "A3", "A4", "A5"] | None = None
    secondary_opportunities: list[SecondaryOpportunity] = Field(
        default_factory=list, max_length=2
    )
    error_boundaries: list[
        Annotated[str, Field(min_length=1, max_length=160)]
    ] = Field(default_factory=list, max_length=3)
    process_summary: NonEmptyText
    as_is_steps: list[NonEmptyText]
    core_bottleneck: NonEmptyText
    bottleneck_symptom: str = ""
    bottleneck_cause: str = ""
    bottleneck_effect: str = ""
    as_is_problem_step_indexes: list[int] = Field(default_factory=list, max_length=4)
    to_be_steps: list[NonEmptyText] = Field(default_factory=list, max_length=6)
    uncertainties: list[NonEmptyText] = Field(max_length=4)
    legacy_filled_fields: list[str] = Field(
        default_factory=list,
        exclude=True,
        repr=False,
    )

    @model_validator(mode="before")
    @classmethod
    def neutralize_internal_references(cls, value: Any) -> Any:
        if not isinstance(value, Mapping):
            return value
        payload, changed = _neutralize_internal_reference_fields(dict(value))
        if not changed or not isinstance(payload, dict):
            return payload
        uncertainties = payload.get("uncertainties")
        warning = "Ein internes oder nicht belegtes Detail wurde als noch offen markiert."
        if isinstance(uncertainties, list) and warning not in uncertainties:
            payload["uncertainties"] = [*uncertainties[:3], warning]
        logger.warning("final_analysis.internal_reference_neutralized")
        return payload

    @model_validator(mode="before")
    @classmethod
    def fill_legacy_core_output(cls, value: Any) -> Any:
        """Map legacy model/test payloads to the concise customer contract."""

        if not isinstance(value, Mapping):
            return value
        payload = dict(value)
        if "primary_recommendation" in payload:
            return payload
        generated_fields: set[str] = set()
        opportunities = payload.get("opportunities")
        primary_value = (
            opportunities[0]
            if isinstance(opportunities, list) and opportunities
            else {}
        )
        primary = (
            primary_value.model_dump()
            if isinstance(primary_value, BaseModel)
            else primary_value
            if isinstance(primary_value, Mapping)
            else {}
        )
        blueprint = payload.get("blueprint")
        blueprint_data = (
            blueprint.model_dump()
            if isinstance(blueprint, BaseModel)
            else blueprint
            if isinstance(blueprint, Mapping)
            else {}
        )
        process_summary = str(payload.get("process_summary") or "Der Ablauf bleibt noch offen.")
        if not payload.get("process_summary"):
            generated_fields.add("process_summary")
        core_problem = str(
            payload.get("core_bottleneck")
            or primary.get("problem")
            or "Der aktuelle Ablauf ist nicht eindeutig verbunden."
        )
        if not payload.get("core_bottleneck") and not primary.get("problem"):
            generated_fields.update({"short_reason", "core_bottleneck"})
        first_change = str(
            primary.get("recommendation")
            or primary.get("first_step")
            or "Die wichtigsten Angaben einheitlich erfassen."
        )
        if not primary.get("recommendation") and not primary.get("first_step"):
            generated_fields.update(
                {
                    "primary_recommendation",
                    "promise",
                    "customer_benefits",
                    "implementation_path",
                }
            )
        human_check = str(
            primary.get("human_approval")
            or blueprint_data.get("human_review_point")
            or "Ein Mensch prüft und bestätigt das Ergebnis."
        )
        if not primary.get("human_approval") and not blueprint_data.get("human_review_point"):
            generated_fields.add("human_check")
        mini_test = primary.get("mini_test")
        if not isinstance(mini_test, list) or not mini_test:
            mini_test = [str(primary.get("first_step") or first_change)]
        required_inputs = blueprint_data.get("required_inputs")
        input_text = (
            ", ".join(str(item) for item in required_inputs)
            if isinstance(required_inputs, list) and required_inputs
            else "Die bereits vorhandenen Auftragsangaben"
        )
        if not isinstance(required_inputs, list) or not required_inputs:
            generated_fields.add("user_action")
        as_is_steps = [str(item) for item in payload.get("as_is_steps", [])]
        future_steps = [str(item) for item in payload.get("to_be_steps", [])]
        if not future_steps:
            future_steps = [str(item) for item in blueprint_data.get("workflow_steps", [])]
        future_steps_were_padded = len(future_steps) < 3
        while len(future_steps) < 3:
            future_steps.append(("Du prüfst das Ergebnis." if len(future_steps) == 2 else first_change))
        if future_steps_were_padded:
            generated_fields.update({"future_process", "to_be_steps"})
        legacy_human_check = str(payload.get("human_check") or human_check)
        if re.search(r"\bdu\b", legacy_human_check, re.IGNORECASE) is None:
            legacy_human_check = f"Du prüfst und bestätigst: {legacy_human_check}"
        payload.setdefault("primary_recommendation", str(primary.get("title") or first_change))
        payload.setdefault("promise", str(payload.get("ai_support") or primary.get("benefit") or first_change))
        payload.setdefault("short_reason", core_problem)
        payload.setdefault("before_process", as_is_steps[:3] or [process_summary])
        payload.setdefault("future_process", future_steps[:4])
        payload["to_be_steps"] = future_steps[:4]
        output_text = str(payload.get("ai_output") or blueprint_data.get("output") or "Ein prüfbarer Entwurf")
        if not payload.get("ai_output") and not blueprint_data.get("output"):
            generated_fields.update({"sample_output", "visible_result"})
        payload.setdefault("sample_output", {
            "title": output_text[:80],
            "fields": [{"label": "Ergebnis", "value": output_text[:140]}],
            "open_items": [],
            "attachments": [],
            "preview_notice": "Vorschau – die endgültigen Angaben prüfst du selbst.",
        })
        user_action = str(payload.get("ai_input") or input_text)
        if re.search(r"\bdu\b", user_action, re.IGNORECASE) is None:
            user_action = f"Du gibst ein: {user_action}."
        payload.setdefault("user_action", user_action)
        if "ai_task" not in payload:
            generated_fields.add("ai_task")
        payload.setdefault("ai_task", "Die KI erkennt und ordnet die relevanten Angaben.")
        payload.setdefault("visible_result", output_text)
        payload["human_check"] = legacy_human_check
        payload.setdefault("customer_benefits", [str(primary.get("benefit") or first_change)])
        old_prerequisites = payload.get("required_prerequisites", [])
        payload["required_prerequisites"] = list(old_prerequisites)[:3] if isinstance(old_prerequisites, list) else []
        payload.setdefault("implementation_path", [str(item) for item in mini_test[:4]])
        while len(payload["implementation_path"]) < 2:
            payload["implementation_path"].append(first_change)
            generated_fields.add("implementation_path")
        payload.setdefault("later_stage", str(payload.get("later_automation") or ""))
        old_opportunities = payload.get("opportunities", [])
        legacy_secondary: list[dict[str, str]] = []
        if isinstance(old_opportunities, list):
            for item in old_opportunities[1:3]:
                item_data = item.model_dump() if isinstance(item, BaseModel) else item
                if isinstance(item_data, Mapping):
                    legacy_secondary.append({
                        "title": str(item_data.get("title", "")),
                        "description": str(item_data.get("benefit", "")),
                    })
        payload.setdefault("secondary_opportunities", legacy_secondary)
        legacy_error = str(primary.get("acceptance_risk") or "").strip()
        payload.setdefault("error_boundaries", [legacy_error] if legacy_error else [])
        for legacy_key in (
            "core_problem", "first_change", "ai_support", "ai_input", "ai_output",
            "weekly_test", "weekly_test_success", "later_automation", "why_this_first",
            "human_decisions", "current_process_summary", "optional_details",
            "opportunities", "blueprint",
        ):
            payload.pop(legacy_key, None)
        payload["legacy_filled_fields"] = sorted(generated_fields)
        if generated_fields:
            logger.info(
                "final_analysis.legacy_fields_filled fields=%s",
                sorted(generated_fields),
            )
        return payload

    @model_validator(mode="after")
    def validate_concise_customer_output(self) -> FinalAnalysisResult:
        if not self.legacy_filled_fields:
            missing_new_fields = [
                name
                for name, value in (
                    ("software_rule", self.software_rule),
                    ("smallest_usable_version", self.smallest_usable_version),
                    ("not_automated", self.not_automated),
                    ("autonomy_level", self.autonomy_level),
                )
                if not value
            ]
            if missing_new_fields:
                raise ValueError(
                    "Der neue Kundenvertrag ist unvollständig: "
                    + ", ".join(missing_new_fields)
                )
        if len(re.findall(r"[\wÄÖÜäöüß]+", self.primary_recommendation)) > 14:
            raise ValueError("Die Hauptempfehlung darf höchstens 14 Wörter enthalten.")
        if SUMMARY_META_PATTERN.search(self.process_summary) is not None:
            self.process_summary = (
                " ".join(self.as_is_steps)
                or "Der heutige Ablauf bleibt an dieser Stelle noch offen."
            )
        if any(AS_IS_META_PATTERN.search(step) is not None for step in self.as_is_steps):
            original_steps = list(self.as_is_steps)
            kept_indexes = [
                index
                for index, step in enumerate(original_steps)
                if AS_IS_META_PATTERN.search(step) is None
            ]
            index_map = {
                old_index: new_index
                for new_index, old_index in enumerate(kept_indexes)
            }
            self.as_is_steps = [original_steps[index] for index in kept_indexes]
            self.as_is_problem_step_indexes = [
                index_map[index]
                for index in self.as_is_problem_step_indexes
                if index in index_map
            ]
        normalized_uncertainties = {
            uncertainty.casefold().rstrip(".?!") for uncertainty in self.uncertainties
        }
        if len(normalized_uncertainties) != len(self.uncertainties):
            raise ValueError("Unsicherheiten dürfen nicht doppelt vorkommen.")
        if any(index < 0 or index >= len(self.as_is_steps) for index in self.as_is_problem_step_indexes):
            raise ValueError("Eine markierte Problemstelle liegt außerhalb des Ist-Ablaufs.")
        direct_fields = (self.user_action, self.human_check)
        if any(re.search(r"\b(?:du|dein|deine|dir)\b", item, re.IGNORECASE) is None for item in direct_fields):
            raise ValueError("Nutzerhandlung und menschliche Prüfung müssen direkt mit du formuliert sein.")
        customer_output = self.model_dump(exclude={"process_summary", "as_is_steps", "core_bottleneck", "bottleneck_symptom", "bottleneck_cause", "bottleneck_effect", "as_is_problem_step_indexes", "to_be_steps", "uncertainties"})
        distant_matches = {
            match.group(0).casefold()
            for match in DISTANT_CUSTOMER_LANGUAGE_PATTERN.finditer(str(customer_output))
        }
        grounded_role_text = " ".join(
            [self.process_summary, *self.as_is_steps]
        ).casefold()
        ungrounded_matches = distant_matches - {"der mitarbeiter"}
        if "der mitarbeiter" in distant_matches and "mitarbeiter" not in grounded_role_text:
            ungrounded_matches.add("der mitarbeiter")
        if ungrounded_matches:
            raise ValueError("Die Kundenausgabe enthält distanzierte Ansprache.")
        generic_ai_phrases = (
            "ki kann deinen prozess optimieren",
            "ki kann den prozess optimieren",
            "ki kann dabei helfen",
        )
        if any(phrase in self.promise.casefold() for phrase in generic_ai_phrases):
            raise ValueError("Die KI-Unterstützung muss konkret beschrieben werden.")
        return self

    def customer_visible_dump(self) -> dict[str, Any]:
        """Unterdrückt ausschließlich vom Legacy-Shim erfundene Platzhalter."""

        payload = self.model_dump()
        for field_name in self.legacy_filled_fields:
            if field_name not in payload:
                continue
            payload[field_name] = [] if isinstance(payload[field_name], list) else ""
        return payload
