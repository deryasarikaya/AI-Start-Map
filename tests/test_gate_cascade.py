from app.recommendation_service import (
    CandidateRankingItem,
    DecisionGates,
    evaluate_gate_cascade,
    infer_decision_gates,
    select_recommendation as _select_recommendation,
)
from scripts.evaluate import load_cases, run


def _catalog_order_ranker(_text, candidates):
    return [
        CandidateRankingItem(solution_id=item.solution_id, reason="Testreihenfolge")
        for item in candidates
    ]


def select_recommendation(*args, **kwargs):
    kwargs.setdefault("candidate_ranker", _catalog_order_ranker)
    return _select_recommendation(*args, **kwargs)


def _digital_gates(**overrides: object) -> DecisionGates:
    values: dict[str, object] = {
        "transaction_anchor": "medium",
        "channel_suitability": "high",
        "process_data_maturity": "medium",
        "error_impact": "medium",
        "rule_stability": "medium",
        "human_approval": "high",
    }
    values.update(overrides)
    return DecisionGates.model_validate(values)


def test_gate_cascade_returns_all_six_explained_statuses() -> None:
    assessments = evaluate_gate_cascade(
        ["PF-08"],
        _digital_gates(),
        confirmed_text="Die Berechtigung liegt vor.",
    )
    assert [item.gate_id for item in assessments] == [
        f"GATE-{index:02d}" for index in range(1, 7)
    ]
    assert {item.status for item in assessments} == {"pass"}
    assert all(item.reason for item in assessments)


def test_digital_housekeeper_selects_sp03_not_physical_sp04() -> None:
    text = (
        "Nach dem Einsatz kommen Sprachnachricht, Fotos und Bon. "
        "Daraus soll nach meiner Prüfung eine Einsatznotiz als Rechnungsgrundlage werden."
    )
    selection = select_recommendation(
        ["PF-08", "PF-12"], _digital_gates(), confirmed_text=text
    )
    assert selection.primary is not None
    assert selection.primary.solution_id == "SP-03"
    assert "SP-04" not in [item.solution_id for item in selection.secondary]
    assert selection.autonomy_level in {"A1", "A2"}


def test_photographer_keeps_approval_status_in_a_human_checked_record() -> None:
    selection = select_recommendation(
        ["PF-04", "PF-01"],
        _digital_gates(error_impact="high"),
        confirmed_text=(
            "Freigaben kommen per E-Mail, WhatsApp und Sprachnachricht. "
            "Der Fotograf prüft den Freigabestatus selbst."
        ),
    )
    assert selection.primary is not None
    assert selection.primary.solution_id == "SP-02"
    assert selection.human_approval_boundaries


def test_flower_shop_combines_digital_requests_without_auto_acceptance() -> None:
    selection = select_recommendation(
        ["PF-02"],
        _digital_gates(),
        confirmed_text="Anfragen kommen über WhatsApp, Instagram und E-Mail.",
    )
    assert selection.primary is not None
    assert selection.primary.solution_id == "SP-01"
    assert "keine automatische Annahme" in " ".join(
        selection.primary.security_guardrails
    )


def test_coach_preparation_never_becomes_an_autonomous_decision() -> None:
    selection = select_recommendation(
        ["PF-03"],
        _digital_gates(),
        confirmed_text="Anfrage, eigene Notizen und Kalender dienen der Vorbereitung.",
    )
    assert selection.primary is not None
    assert selection.primary.solution_id == "SP-06"
    assert selection.autonomy_level in {"A1", "A2"}


def test_online_retailer_complaints_and_pdfs_use_document_extraction() -> None:
    selection = select_recommendation(
        ["PF-12", "PF-04"],
        _digital_gates(),
        confirmed_text="Reklamationen und Belege kommen als E-Mail und PDF.",
    )
    assert selection.primary is not None
    assert selection.primary.solution_id == "SP-06"


def test_a0_is_reachable_when_existing_function_is_enough() -> None:
    text = "Die bestehende Kalenderfunktion reicht aus; es gibt keinen Engpass."
    selection = select_recommendation(
        [], infer_decision_gates(text), confirmed_text=text
    )
    assert selection.primary is None
    assert selection.autonomy_level == "A0"
    assert selection.recommendation_mode == "non_ai_first"
    assert "KI ist" in selection.a0_recommendation


def test_explicit_non_ai_first_overrides_semantic_problem_family() -> None:
    text = (
        "Alle Termine stehen bereits vollständig im digitalen Kalender. "
        "Ich will nur die vorhandene Erinnerungsfunktion einschalten; "
        "dafür ist keine KI nötig."
    )
    selection = select_recommendation(
        ["PF-01"], infer_decision_gates(text), confirmed_text=text
    )
    assert selection.primary is None
    assert selection.autonomy_level == "A0"
    assert selection.recommendation_mode == "non_ai_first"


def test_rule_that_does_not_suffice_does_not_trigger_a0() -> None:
    text = "Eine einfache Regel reicht nicht aus; E-Mails müssen weiter übertragen werden."
    selection = select_recommendation(
        ["PF-03"], _digital_gates(), confirmed_text=text
    )
    assert selection.primary is not None
    assert selection.recommendation_mode == "ai_assisted"


def test_ambiguous_case_stays_a1_until_missing_gates_are_answered() -> None:
    selection = select_recommendation(
        ["PF-01"],
        DecisionGates(channel_suitability="high"),
        confirmed_text="Informationen kommen digital, der genaue Ablauf ist noch offen.",
    )
    assert selection.primary is not None
    assert selection.autonomy_level == "A1"
    statuses = {item.gate_id: item.status for item in selection.gate_assessments}
    assert statuses["GATE-02"] == "unknown"
    assert statuses["GATE-04"] == "unknown"


def test_real_physical_object_can_select_sp04() -> None:
    text = "Angenommene Schuhe werden bearbeitet und später aus einem Regal abgeholt."
    gates = _digital_gates(
        physical_object=True,
        real_location_known=False,
        transaction_anchor="low",
        process_data_maturity="low",
        error_impact="high",
    )
    selection = select_recommendation(["PF-05"], gates, confirmed_text=text)
    assert selection.primary is not None
    assert selection.primary.solution_id == "SP-04"


def test_building_and_customer_address_are_not_physical_objects() -> None:
    gates = infer_decision_gates(
        "Der Hausmeister fährt zu einem Gebäude an der Kundenadresse und sendet ein Foto."
    )
    assert gates.physical_object is False


def test_purely_analog_business_is_outside_target_and_a0() -> None:
    text = "Wir arbeiten rein analog und haben keinen digitalen Kanal, nur Papier."
    selection = select_recommendation(
        ["PF-01"], infer_decision_gates(text), confirmed_text=text
    )
    assert selection.primary is None
    assert selection.target_fit == "fail"
    assert selection.autonomy_level == "A0"


def test_forbidden_autonomous_price_decision_is_blocked() -> None:
    text = "Die KI soll den Preis automatisch ohne Freigabe entscheiden."
    selection = select_recommendation(
        ["PF-09"],
        _digital_gates(error_impact="high", human_approval="low"),
        confirmed_text=text,
    )
    assert selection.primary is None
    assert selection.autonomy_level == "A0"
    assert selection.target_fit == "fail"
    statuses = {item.gate_id: item.status for item in selection.gate_assessments}
    assert statuses["GATE-04"] == "fail"
    assert statuses["GATE-05"] == "fail"


def test_evaluation_datasets_and_label_statuses_stay_separate() -> None:
    cases = load_cases()
    legacy = [item for item in cases if item.dataset == "legacy_91"]
    batch_09 = [item for item in cases if item.dataset == "batch_09"]
    assert len(legacy) == 91
    assert len(batch_09) == 30
    assert {item.label_status for item in batch_09} == {"research_proposed"}

    payload = run()
    assert payload["dataset_counts"] == {
        "legacy_91": 91,
        "batch_09": 30,
        "quality_selection": 4,
    }
    assert {
        item["label_status"]
        for item in payload["results"]
        if item["dataset"] == "batch_09"
    } == {"research_proposed"}
