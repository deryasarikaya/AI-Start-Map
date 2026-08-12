from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.schemas import customer_plain_text
from tests.conftest import spec_view


ROOT = Path(__file__).resolve().parents[1]


def _render(result: dict[str, object]) -> str:
    environment = Environment(
        loader=FileSystemLoader(ROOT / "app" / "templates"),
        autoescape=select_autoescape(("html",)),
    )
    environment.globals["url_for"] = lambda name, **_kwargs: f"/{name}"
    environment.filters["customer_text"] = customer_plain_text
    return environment.get_template("results.html").render(
        result=result,
        process={"process_name": "Einsatz bis Rechnung"},
    )


def test_results_follow_the_binding_section_order() -> None:
    """Reihenfolge nach ERGEBNIS_SPEC, Abschnitt "Reihenfolge der Ergebnisseite"."""

    html = _render(spec_view(grenzen="Ein nicht dokumentiertes Gespräch bleibt weg."))
    abschnitte = [
        "DEINE AUSWERTUNG",                              # 1 Engpass
        "So habe ich deinen heutigen Ablauf verstanden",  # 2 heute
        "Hier lässt sich Arbeit aus deinem Ablauf nehmen",  # 3 moeglichkeiten
        "SO WÜRDE DEINE LÖSUNG AUSSEHEN",                # 4 loesung
        "NACH DER EINRICHTUNG",                          # 4b Vergleich
        "DEIN KONKRETES ERGEBNIS",                       # 5 beispiel
        "Das behältst du, das kommt dazu",               # 6 voraussetzungen
        "Das würde ich für dich bauen oder verbinden",   # 7 umsetzung
        "Das bleibt bei dir",                            # 8 bleibt_bei_dir
        "Eine Grenze",                                   # 9 grenzen
        "Möchtest du das umsetzen?",                     # 10 Kontakt
    ]
    positionen = [html.index(text) for text in abschnitte]
    assert positionen == sorted(positionen)
    assert "Autonomiestufe" not in html
    assert "/sessions/" not in html


def test_optional_sections_disappear_when_their_field_is_empty() -> None:
    """Beispiel und Grenze entfallen, wenn ihr Feld leer ist."""

    html = _render(spec_view(beispiel=None, grenzen=""))
    assert "DEIN KONKRETES ERGEBNIS" not in html
    assert "Eine Grenze" not in html
    assert "SO WÜRDE DEINE LÖSUNG AUSSEHEN" in html


def test_later_rank_is_shown_once_and_not_as_its_own_block() -> None:
    """spaeter steckt in moeglichkeiten und darf nicht doppelt erscheinen."""

    view = spec_view()
    view["moeglichkeiten"] = [
        {"rang": "groesster_hebel", "titel": "Ein Eingang für alles",
         "begruendung": "Hier geht die meiste Zeit verloren."},
        {"rang": "spaeter", "titel": "Bestätigte Anfragen übergeben",
         "begruendung": "Erst wenn die Aufnahme zuverlässig läuft."},
    ]
    html = _render(view)
    assert html.count("Bestätigte Anfragen übergeben") == 1
    assert html.count(">Später<") == 1


def test_example_values_stay_inside_the_marked_block() -> None:
    html = _render(spec_view())
    marker = html.index("data-customer-example-block")
    ende = html.index('data-result-block aria-labelledby="prerequisites-title"', marker)
    assert "Rosa und Weiß" in html[marker:ende]
    assert "Rosa und Weiß" not in html[:marker] + html[ende:]


def test_result_typography_is_bounded_for_desktop_and_mobile() -> None:
    css = (ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8")
    assert "font-size: clamp(2.25rem, 4vw, 2.625rem)" in css
    assert "font-size: clamp(1.75rem, 8vw, 2.125rem)" in css
    assert "max-width: 72ch" in css
    assert "overflow-wrap: anywhere" in css


def test_error_state_keeps_a_clear_retry_action() -> None:
    environment = Environment(
        loader=FileSystemLoader(ROOT / "app" / "templates"),
        autoescape=select_autoescape(("html",)),
    )
    environment.globals["url_for"] = lambda name, **_kwargs: f"/{name}"
    html = environment.get_template("error.html").render(
        error_title="Die Analyse konnte nicht fortgesetzt werden.",
        error_message="Bitte versuche es erneut.",
        retry_path="/processing",
    )
    assert "Deine bisherigen Angaben bleiben gespeichert" in html
    assert "Noch einmal versuchen" in html
    assert 'href="/processing"' in html
