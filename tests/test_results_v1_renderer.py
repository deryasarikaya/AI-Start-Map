"""Sichert den schmalen, DTO-only Schnitt der sichtbaren Results V1."""

from pathlib import Path


def test_results_v1_template_has_no_legacy_result_dependency() -> None:
    """Die sichtbare Darstellung liest den vorbereiteten Vertrag, nie `e`."""

    template = (
        Path(__file__).resolve().parents[1] / "app/templates/results_v1.html"
    ).read_text(encoding="utf-8")

    assert "result." in template
    assert "{{ e." not in template
    assert "tafel" not in template
    assert "karte.html" not in template


def test_results_v1_has_a_separate_controlled_experience_library() -> None:
    """Experience-Typen werden kontrolliert dargestellt, nicht frei gerendert."""

    library = (
        Path(__file__).resolve().parents[1]
        / "app/templates/results_experiences.html"
    ).read_text(encoding="utf-8")

    for experience_type in (
        "voice_assistant",
        "ai_inbox",
        "case_workspace",
        "document_flow",
        "customer_self_service",
        "management_overview",
        "automation_flow",
    ):
        assert experience_type in library
