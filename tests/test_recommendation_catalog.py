from pathlib import Path

import pytest
from pydantic import ValidationError

from app.recommendation_service import (
    DecisionGates,
    classify_problem_families,
    load_recommendation_catalog,
    select_recommendation,
)


def test_catalog_contains_exact_stable_ids_and_valid_references() -> None:
    catalog = load_recommendation_catalog()
    assert [item.problem_family_id for item in catalog.problem_families] == [
        f"PF-{index:02d}" for index in range(1, 13)
    ]
    assert [item.solution_id for item in catalog.solution_patterns] == [
        f"SP-{index:02d}" for index in range(1, 11)
    ]
    assert all(item.human_check for item in catalog.solution_patterns)
    assert all(item.failure_modes for item in catalog.solution_patterns)
    assert all(item.smallest_entry for item in catalog.solution_patterns)
    assert "evaluation" not in catalog.source.casefold()


def test_evaluation_path_is_never_loadable_as_product_knowledge(tmp_path: Path) -> None:
    path = tmp_path / "evaluation_catalog.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="Evaluationen"):
        load_recommendation_catalog(path)


def test_housekeeper_selects_mobile_job_documentation_with_anchor_in_entry() -> None:
    text = "Nach dem Einsatz kommen Sprachnachricht, Fotos und Bon; vor der Rechnung ist alles verteilt."
    families = classify_problem_families(text)
    selection = select_recommendation(
        families,
        DecisionGates(
            transaction_anchor="low",
            channel_suitability="high",
            process_data_maturity="medium",
            error_impact="medium",
            rule_stability="medium",
            human_approval="high",
        ),
    )
    assert selection.primary.solution_id == "SP-03"
    assert selection.primary.sample_output_type == "Einsatznotiz"
    assert any("Einsatzanker" in item for item in selection.required_prerequisites)
    assert "Zeit" in selection.primary.human_check
    assert "Rechnungsentwurf" in selection.primary.later_stage


def test_shoemaker_never_skips_physical_identity_and_location() -> None:
    families = classify_problem_families("Schuhe, Auftrag und Regalplatz sind nicht sicher verbunden.")
    selection = select_recommendation(
        families,
        DecisionGates(
            transaction_anchor="low",
            channel_suitability="medium",
            process_data_maturity="low",
            error_impact="high",
            rule_stability="medium",
            human_approval="high",
            physical_object=True,
            real_location_known=False,
        ),
    )
    assert selection.primary.solution_id == "SP-04"
    assert selection.primary.sample_output_type == "Auftragskarte"
    assert "errät nie den Ort" in selection.primary.ai_task
    assert "Herausgabe" in selection.primary.human_check


def test_flower_shop_selects_structured_order_intake_without_auto_acceptance() -> None:
    families = classify_problem_families(
        "Eine Bestellung kommt als freie Nachricht mit Anlass, Budget, Farben, Abholzeit und fehlenden Angaben."
    )
    selection = select_recommendation(
        families,
        DecisionGates(
            transaction_anchor="medium",
            channel_suitability="high",
            process_data_maturity="medium",
            error_impact="medium",
            rule_stability="medium",
            human_approval="high",
        ),
    )
    assert selection.primary.solution_id == "SP-01"
    assert selection.primary.sample_output_type == "Anfragekarte"
    assert "keine automatische Annahme" in " ".join(selection.primary.security_guardrails)


def test_massage_salon_keeps_capacity_confirmation_human() -> None:
    families = classify_problem_families(
        "Terminanfragen kommen über mehrere Kanäle; Personal und Kapazität sind unsicher."
    )
    selection = select_recommendation(
        families,
        DecisionGates(
            transaction_anchor="high",
            channel_suitability="high",
            process_data_maturity="medium",
            error_impact="high",
            rule_stability="low",
            human_approval="high",
        ),
    )
    assert selection.primary.solution_id == "SP-05"
    assert selection.primary.sample_output_type == "Terminanfrage"
    assert "verbindlichen Termin" in selection.primary.human_check
    assert "keine automatische Zusage" in " ".join(selection.primary.security_guardrails)


def test_catalog_schema_rejects_missing_core_fields() -> None:
    payload = load_recommendation_catalog().model_dump()
    del payload["solution_patterns"][0]["failure_modes"]
    with pytest.raises(ValidationError):
        type(load_recommendation_catalog()).model_validate(payload)
