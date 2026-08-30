"""Die Karte als Daten — vier Zustände über einer festen Landschaft.

**Der wichtigste Test hier ist der auf Bestimmtheit.** Eine Karte, die
bei jedem Seitenaufruf anders aussieht, obwohl sich nichts geändert hat,
ist keine Karte. Deshalb: keine erzeugten Koordinaten, keine
kundenabhängige Landschaft, kein Modellaufruf.

Der zweitwichtigste ist der auf Widerspruchsfreiheit: Derselbe Bereich
darf nicht gleichzeitig Einstieg und Später sein. Ohne diese Rangfolge
zeigte die Karte ihn zweimal, in zwei verschiedenen Zuständen.
"""

from __future__ import annotations

from app import karte, map_state, operating_model
from app.map_state import EINSTIEG_HOECHSTENS, SPAETER_HOECHSTENS
from app.result_schema import DecisionState


def _zustand(**overrides: object) -> DecisionState:
    daten: dict[str, object] = {
        "target_family_ids": ["SF-15", "SF-01", "SF-02"],
        "start_family_ids": ["SF-15", "SF-01"],
        "future_family_ids": ["SF-10", "SF-09"],
    }
    daten.update(overrides)
    return DecisionState.model_validate(daten)


def test_the_landscape_is_the_same_for_everyone() -> None:
    """Sechs Gebiete, vierzehn Bereiche — bei jedem Betrieb.

    Eine Karte, die nur zeigt, was empfohlen wird, ist keine Landschaft,
    sondern eine Angebotsliste. Der Betrieb soll sehen, wie weit das
    gehen kann.
    """

    zustand = map_state.aus_entscheidung(_zustand())

    assert zustand.gebiete == karte.ZONEN
    assert len(zustand.knoten) == len(operating_model.BEREICHE) == 14


def test_the_states_do_not_overlap() -> None:
    """Einstieg, Zielbild, Später — jeder Bereich in genau einem Zustand."""

    zustand = map_state.aus_entscheidung(_zustand())

    assert set(zustand.start) <= set(zustand.target)
    assert not set(zustand.future) & set(zustand.target)
    zustaende = {k.schluessel: k.zustand for k in zustand.knoten}
    for schluessel in zustand.start:
        assert zustaende[schluessel] == "start"
    for schluessel in zustand.future:
        assert zustaende[schluessel] == "future"


def test_the_start_stays_narrow() -> None:
    """Ein Einstieg, der überall gleichzeitig anfängt, ist keiner.

    Was nicht mehr hineinpasst, bleibt Zielbild und verschwindet nicht —
    die Grenze ist eine der Darstellung, nicht der Fachlichkeit.
    """

    breit = _zustand(
        target_family_ids=["SF-15", "SF-02", "SF-06", "SF-11", "SF-08"],
        start_family_ids=["SF-15", "SF-02", "SF-06", "SF-11"],
        future_family_ids=[],
    )

    zustand = map_state.aus_entscheidung(breit)

    assert len(zustand.start) == EINSTIEG_HOECHSTENS
    # Nichts geht verloren: Der Rest steht weiter im Zielbild.
    verdraengt = set(
        b.schluessel
        for b in operating_model.bereiche_fuer(["SF-06", "SF-11"])
    )
    assert verdraengt <= set(zustand.target)


def test_later_is_capped_but_never_padded() -> None:
    """Vier höchstens — und weniger, wenn es weniger gibt.

    Auffüllen hiesse, einem Betrieb einen Ausblick zu erfinden, den
    niemand für ihn abgeleitet hat.
    """

    viele = _zustand(
        future_family_ids=["SF-10", "SF-09", "SF-11", "SF-17", "SF-20", "SF-04"]
    )
    wenige = _zustand(future_family_ids=["SF-10"])

    assert len(map_state.aus_entscheidung(viele).future) == SPAETER_HOECHSTENS
    assert len(map_state.aus_entscheidung(wenige).future) == 1


def test_today_is_read_not_guessed() -> None:
    """„Heute" steht nur da, wo der Betrieb selbst ein System genannt hat."""

    mit_bestand = DecisionState.model_validate(
        {
            "target_family_ids": ["SF-15", "SF-01"],
            "start_family_ids": ["SF-15"],
            "signals": [
                {
                    "id": "S1",
                    "kind": "existing_system",
                    "statement": "Ein digitaler Kalender ist vorhanden.",
                    "status": "confirmed",
                    "critical": False,
                    "evidence_refs": [],
                }
            ],
            "coverage": {
                "items": [
                    {
                        "signal_id": "S1",
                        "disposition": "supporting",
                        "family_refs": ["SF-06"],
                        "explanation": "Der vorhandene Kalender bleibt bestehen.",
                    }
                ],
                "uncovered_critical_signal_ids": [],
            },
        }
    )

    zustand = map_state.aus_entscheidung(mit_bestand)

    assert zustand.heute == ("termine_kapazitaet",)
    assert zustand.knoten_von("termine_kapazitaet").zustand == "heute"


def test_without_a_named_system_today_stays_empty() -> None:
    """Aus einer beiläufigen Erwähnung wird keine Bestandsaufnahme."""

    assert map_state.aus_entscheidung(_zustand()).heute == ()


def test_the_map_carries_no_identifiers_on_its_surface() -> None:
    """Was der Kunde liest, sind Bereichsnamen — nie Kennungen.

    Die Familien hängen daran, aber innen: Sie tragen die Details im
    Seitenpanel.
    """

    zustand = map_state.aus_entscheidung(_zustand())

    for knoten in zustand.knoten:
        assert "SF-" not in knoten.name
        assert knoten.familien  # innen sind sie da


def test_coordinates_come_from_the_fixed_map() -> None:
    """Kein Modell setzt einen Punkt — der Ort folgt aus der bestehenden Karte."""

    zustand = map_state.aus_entscheidung(_zustand())
    eingang = zustand.knoten_von("kundenzugang_intake")

    plaetze = [karte.PLAETZE[k] for k in ("SF-15", "SF-01", "SF-14", "SF-16")]
    assert eingang.x == round(sum(x for _, x, _ in plaetze) / 4)
    assert eingang.y == round(sum(y for _, _, y in plaetze) / 4)


def test_the_same_decision_yields_the_same_map() -> None:
    """Zweimal dieselbe Entscheidung, zweimal dieselbe Karte."""

    erst = map_state.aus_entscheidung(_zustand())
    nochmal = map_state.aus_entscheidung(_zustand())

    assert erst == nochmal


def test_a_run_without_a_recommendation_still_has_a_map() -> None:
    """Ohne Katalogtreffer bleibt die Landschaft — nur nichts markiert."""

    zustand = map_state.aus_entscheidung(DecisionState())

    assert len(zustand.knoten) == 14
    assert zustand.start == () and zustand.target == ()
    assert all(k.zustand == "still" for k in zustand.knoten)
    assert zustand.mitte.art == "direct_flow"
