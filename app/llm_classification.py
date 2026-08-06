"""LLM-Klassifikation von Problemfamilien und Entscheidungs-Gates.

Primärer Klassifikationspfad laut Spec
`docs/specs/solution-pattern-recommendation/design.md`: Ein
Structured-Output-Aufruf erhält die bestätigte Erzählung sowie die zwölf
Problemfamilien- und sechs Gate-Definitionen aus Katalog v2 als Kontext und
liefert ein bis drei Problemfamilien-IDs mit wörtlichem Belegzitat sowie
typisierte Gate-Werte.

Die deterministischen Stichwort-Funktionen `classify_problem_families()` und
`infer_decision_gates()` bleiben unverändert erhalten und dienen ausschließlich
als Fallback bei API-Fehlern. Selector, Agent-Layer, UI und Indizes werden von
diesem Modul nicht berührt.
"""

from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.openai_service import AIServiceError, _parse_structured_output
from app.recommendation_service import (
    DecisionGates,
    GateLevel,
    RecommendationCatalog,
    classify_problem_families,
    infer_decision_gates,
    load_recommendation_catalog,
)


logger = logging.getLogger(__name__)

ProblemFamilyId = Literal[
    "PF-01",
    "PF-02",
    "PF-03",
    "PF-04",
    "PF-05",
    "PF-06",
    "PF-07",
    "PF-08",
    "PF-09",
    "PF-10",
    "PF-11",
    "PF-12",
]

MAXIMUM_FAMILY_COUNT = 3

CLASSIFICATION_SYSTEM_PROMPT = """
Du klassifizierst die bestätigte Erzählung eines sehr kleinen Betriebs für eine
Prozessdiagnose. Die Nutzdaten enthalten die Erzählung, zwölf definierte
Problemfamilien und sechs Entscheidungs-Gates.

Aufgabe 1 – Problemfamilien: Wähle null bis höchstens drei Problemfamilien,
die das erzählte Kernproblem am besten treffen, geordnet nach Dominanz. Die
dominante Familie steht an erster Stelle. Wähle nur Familien, für die es eine
konkrete Textstelle in der Erzählung gibt, und gib diese Textstelle wörtlich
als Belegzitat an. Wähle keine Familie auf Verdacht. Nutze die Definitionen,
typischen Aussagen, Symptome und Ursachen der Familien als Maßstab, nicht
einzelne Stichwörter. Gib eine leere Liste zurück, wenn kein belegter Engpass
vorliegt oder eine einfache bestehende Funktion ohne KI ausreicht.

Aufgabe 2 – Gates: Bewerte die sechs Gates ausschließlich anhand der
Erzählung. Der Wert "unknown" ist ausdrücklich erlaubt und korrekt, wenn die
Erzählung keine Aussage dazu enthält. Rate nicht und leite nichts aus
Branchenwissen ab. Setze `physical_object` nur, wenn ein konkreter physischer
Gegenstand Teil des Problems ist, und `real_location_known` nur, wenn die
Erzählung einen dokumentierten festen Ablage- oder Lagerort bestätigt.

Antworte ausschließlich im vorgegebenen Ausgabeschema. Erfinde keine Angaben
und keine IDs.
""".strip()


class FamilyAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    problem_family_id: ProblemFamilyId
    evidence_quote: str


class LlmDecisionGates(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_anchor: GateLevel
    channel_suitability: GateLevel
    process_data_maturity: GateLevel
    error_impact: GateLevel
    rule_stability: GateLevel
    human_approval: GateLevel
    physical_object: bool
    real_location_known: bool


class LlmClassificationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    families: list[FamilyAssessment]
    gates: LlmDecisionGates


class ClassificationOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    problem_family_ids: list[str]
    gates: DecisionGates
    method: Literal["llm", "keyword_fallback"]


def _family_context(catalog: RecommendationCatalog) -> list[dict[str, object]]:
    return [
        {
            "problem_family_id": family.problem_family_id,
            "name": family.name,
            "definition": family.definition,
            "typical_statements": family.typical_statements,
            "symptoms": family.symptoms,
            "common_causes": family.common_causes,
        }
        for family in catalog.problem_families
    ]


def _gate_context(catalog: RecommendationCatalog) -> list[dict[str, object]]:
    return [
        {
            "gate_id": gate.gate_id,
            "name": gate.name,
            "question": gate.question,
        }
        for gate in catalog.decision_gates
    ]


def classify_with_llm(
    text: str,
    *,
    catalog: RecommendationCatalog | None = None,
) -> ClassificationOutcome:
    """Klassifiziert per Structured Output; wirft AIServiceError bei API-Fehlern."""

    data = catalog or load_recommendation_catalog()
    payload: dict[str, object] = {
        "erzaehlung": text,
        "problemfamilien": _family_context(data),
        "gates": _gate_context(data),
    }
    result = _parse_structured_output(
        system_prompt=CLASSIFICATION_SYSTEM_PROMPT,
        payload=payload,
        result_type=LlmClassificationResult,
    )
    family_ids = list(
        dict.fromkeys(item.problem_family_id for item in result.families)
    )[:MAXIMUM_FAMILY_COUNT]
    gates = DecisionGates.model_validate(result.gates.model_dump())
    return ClassificationOutcome(
        problem_family_ids=family_ids,
        gates=gates,
        method="llm",
    )


def classify_narrative(
    text: str,
    *,
    catalog: RecommendationCatalog | None = None,
) -> ClassificationOutcome:
    """Primär LLM-Klassifikation; Keyword-Logik nur als Fallback bei API-Fehlern."""

    try:
        outcome = classify_with_llm(text, catalog=catalog)
        logger.info(
            "classification.completed method=llm problem_families=%s",
            outcome.problem_family_ids,
        )
        return outcome
    except AIServiceError as error:
        logger.warning(
            "classification.fallback method=keyword_fallback exception_type=%s "
            "exception_message=%s",
            type(error).__name__,
            str(error),
        )
        return ClassificationOutcome(
            problem_family_ids=classify_problem_families(text),
            gates=infer_decision_gates(text),
            method="keyword_fallback",
        )
