"""LLM-Klassifikation von Problemfamilien und Entscheidungs-Gates.

Primärer Klassifikationspfad laut Spec
`docs/specs/solution-pattern-recommendation/design.md`: Ein
Structured-Output-Aufruf erhält die bestätigte Erzählung sowie die zwölf
Problemfamilien- und sechs Gate-Definitionen aus Katalog v2 als Kontext und
liefert ein bis drei Problemfamilien-IDs mit wörtlichem Belegzitat sowie
typisierte Gate-Werte.

Die deterministischen Stichwort-Funktionen `classify_problem_families()` und
`infer_decision_gates()` bleiben für Tests und Baseline-Messungen erhalten. Der
Produktivpfad fällt bei API-Fehlern nicht auf sie zurück.
"""

from __future__ import annotations

import logging
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, create_model

from app.openai_service import AIServiceError, _parse_structured_output
from app.recommendation_service import (
    CandidateRankingItem,
    DecisionGates,
    GateLevel,
    RecommendationCatalog,
    SolutionPattern,
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

Abgrenzung PF-02/PF-03/PF-12: Wenn neue Anfragen oder Bestellwünsche aus
mehreren digitalen Kanälen nicht zuverlässig mit Status und Mindestangaben
erfasst werden, ist PF-02 dominant. PF-03 ist nur dominant, wenn die manuelle
Übertragung derselben Information das Kernproblem ist; PF-12 nur, wenn das
Auslesen unstrukturierter Inhalte in einen Datensatz das Kernproblem ist.

Aufgabe 2 – Gates: Bewerte die sechs Gates ausschließlich anhand der
Erzählung. Der Wert "unknown" ist ausdrücklich erlaubt und korrekt, wenn die
Erzählung keine Aussage dazu enthält. Rate nicht und leite nichts aus
Branchenwissen ab. Setze `physical_object` nur, wenn ein konkreter physischer
Kundengegenstand in der Obhut des Betriebs Teil des Problems ist: Er wurde
angenommen, wird gelagert oder bearbeitet oder später zurückgegeben oder
abgeholt. Belege, Kassenzettel, Rechnungen, Lieferscheine, Zettel, Notizen,
Fotos, Ausdrucke und eingekauftes Material für den eigenen Einsatz sind keine
solchen Kundengegenstände. Setze `real_location_known` nur, wenn die Erzählung
einen dokumentierten festen Ablage- oder Lagerort bestätigt.

Aufgabe 3 – Betriebstyp: Beschreibe den Betriebstyp aus der Erzählung in einem
kurzen freien deutschen Begriff. Nutze keine Auswahlliste und rate nicht. Wenn
der Betriebstyp nicht eindeutig aus der Erzählung hervorgeht, gib einen leeren
Text zurück.

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
    business_type_guess: str = ""


class ClassificationOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    problem_family_ids: list[str]
    gates: DecisionGates
    method: Literal["llm"]
    business_type_guess: str = ""


class LlmCandidateRankingItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    solution_id: Literal[
        "SP-01", "SP-02", "SP-03", "SP-04", "SP-05",
        "SP-06", "SP-07", "SP-08", "SP-09", "SP-10",
    ]
    reason: str


class LlmCandidateRankingResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ranking: list[LlmCandidateRankingItem]


CANDIDATE_RANKING_SYSTEM_PROMPT = """
Du ordnest bereits durch feste Sicherheitsregeln zugelassene Lösungsmuster für
die bestätigte Prozessbeschreibung. Entscheide nur, welches zugelassene Muster
das konkret beschriebene Kernproblem am direktesten löst. Beurteile Bedeutung
und Ablauf, nicht einzelne Stichwörter.

Gib jedes zugelassene Muster genau einmal zurück, passendstes zuerst. Nutze nur
die mitgelieferten IDs. Ein Gegenbeispiel zeigt, wann ein Muster gerade nicht
passt; positive Varianten zeigen typische passende Fälle. Begründe jede
Position kurz anhand der bestätigten Beschreibung. Hebe keine Ausschlüsse auf
und erfinde keine Betriebsangaben.
""".strip()


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
        business_type_guess=result.business_type_guess.strip(),
    )


def classify_narrative(
    text: str,
    *,
    catalog: RecommendationCatalog | None = None,
) -> ClassificationOutcome:
    """Classify with the model; API failures stay visible to the product flow."""

    outcome = classify_with_llm(text, catalog=catalog)
    logger.info(
        "classification.completed method=llm problem_families=%s",
        outcome.problem_family_ids,
    )
    return outcome


def rank_candidates(
    text: str,
    candidates: list[SolutionPattern],
) -> list[CandidateRankingItem]:
    """Rank only the candidates already admitted by deterministic Python rules."""

    if not candidates:
        return []
    allowed_ids = {item.solution_id for item in candidates}
    payload: dict[str, object] = {
        "bestaetigte_prozessbeschreibung": text,
        "zugelassene_muster": [
            {
                "solution_id": item.solution_id,
                "name": item.name,
                "kurzbeschreibung": item.customer_language,
                "positive_variants": item.positive_variants,
                "counterexample": item.counterexample,
            }
            for item in candidates
        ],
    }
    allowed_solution_id = Literal.__getitem__(tuple(sorted(allowed_ids)))
    ranking_item_type = create_model(
        f"AllowedCandidateRankingItem{len(candidates)}",
        __config__=ConfigDict(extra="forbid"),
        solution_id=(allowed_solution_id, ...),
        reason=(str, ...),
    )
    ranking_result_type = create_model(
        f"AllowedCandidateRankingResult{len(candidates)}",
        __config__=ConfigDict(extra="forbid"),
        ranking=(
            Annotated[
                list[ranking_item_type],
                Field(min_length=len(candidates), max_length=len(candidates)),
            ],
            ...,
        ),
    )
    result = _parse_structured_output(
        system_prompt=CANDIDATE_RANKING_SYSTEM_PROMPT,
        payload=payload,
        result_type=ranking_result_type,
    )
    ranked: list[CandidateRankingItem] = []
    seen: set[str] = set()
    for item in result.ranking:
        if item.solution_id not in allowed_ids or item.solution_id in seen:
            continue
        reason = item.reason.strip()
        if not reason:
            continue
        ranked.append(CandidateRankingItem(solution_id=item.solution_id, reason=reason))
        seen.add(item.solution_id)
    if seen != allowed_ids:
        logger.error(
            "candidate_ranking.invalid allowed=%s returned=%s",
            sorted(allowed_ids),
            [item.solution_id for item in ranked],
        )
        raise AIServiceError(
            "Die passenden Lösungen konnten gerade nicht sicher verglichen werden."
        )
    logger.info(
        "candidate_ranking.completed ranking=%s",
        [item.solution_id for item in ranked],
    )
    return ranked
