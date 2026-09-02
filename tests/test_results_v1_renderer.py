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
        "knowledge_assistant",
        "guided_intake",
        "management_overview",
        "automation_flow",
    ):
        assert experience_type in library


def test_results_v1_renders_the_selected_experiences_in_web_and_pdf() -> None:
    """Die konkrete Vorschau nutzt denselben DTO-Auswahlpunkt in beiden Medien."""

    root = Path(__file__).resolve().parents[1]
    web_template = (root / "app/templates/results_v1.html").read_text(
        encoding="utf-8"
    )
    pdf_template = (root / "app/templates/results_pdf.html").read_text(
        encoding="utf-8"
    )
    library = (root / "app/templates/results_experiences.html").read_text(
        encoding="utf-8"
    )

    assert "result.ansichten.primary" in web_template
    assert "result.ansichten.primary" in pdf_template
    assert "experiences.render(primary)" in web_template
    assert "experiences.render(primary)" in pdf_template
    assert "experiences.render_compact(experience)" in pdf_template
    assert "So könnte Ihre Lösung konkret aussehen" in web_template
    assert "So könnte Ihre Lösung konkret aussehen" in pdf_template
    assert "experience-empty" not in library


def test_results_v1_keeps_the_experience_section_in_the_approved_order() -> None:
    """Die Vorschau steht zwischen künftigem Alltag und Verantwortung."""

    template = (
        Path(__file__).resolve().parents[1] / "app/templates/results_v1.html"
    ).read_text(encoding="utf-8")

    assert template.index("So liefe Ihr Alltag künftig") < template.index(
        "So könnte Ihre Lösung konkret aussehen"
    ) < template.index("Das läuft künftig automatisch")


def test_results_v1_projects_the_approved_four_stage_map() -> None:
    """Die freigegebene Landkarte bleibt DTO-only und ohne Karten-Inspector."""

    template = (
        Path(__file__).resolve().parents[1] / "app/templates/results_v1.html"
    ).read_text(encoding="utf-8")
    assert "result.anker" in template
    assert "result.karte.start" in template
    assert "result.karte.mitte.label" in template
    assert "future.depends_on_module_refs" in template
    assert 'class="approved-map"' in template
    assert "Was verbindet" in template
    assert "Neuer Arbeitsstand" in template
    assert 'data-map-filter' not in template
    assert 'data-map-popup' not in template
    assert 'data-map-detail-close' not in template


def test_results_v1_contains_the_new_full_pdf_flow() -> None:
    """Die PDF nutzt dieselbe Result-Darstellung mit eigenem Deckblatt."""

    template = (
        Path(__file__).resolve().parents[1] / "app/templates/results_v1.html"
    ).read_text(encoding="utf-8")

    assert "pdf-cover" in template
    assert "{{ stil('results-v1.css') }}" in template
    assert "{{ stil('results-final.css') }}" in template
    assert "@page { size: A4;" in template
