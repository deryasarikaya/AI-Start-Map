"""Der festgehaltene Entscheidungszustand — Einstieg, Zielbild, Später, Absagen.

**Wogegen das gebaut ist.** Die Ergebnisseite muss wissen, was zum
Einstieg gehört und was zum Zielbild. Bisher liess sich das nur erraten:
aus Modulstufen, aus dem Ausbaupfad, aus der Reihenfolge der Familien.
Jede Vorlage, die das selbst zusammenreimt, trifft eine fachliche
Entscheidung — und zwei Vorlagen reimen es verschieden zusammen. Web und
PDF zeigten dann aus demselben Lauf verschiedene Empfehlungen.

Diese Tests halten fest, dass die Entscheidung **einmal** getroffen,
geprüft und mitgespeichert wird — und dass ein Lauf von vor diesem
Vertrag deswegen nicht kaputtgeht.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app import decision_state
from app.result_schema import (
    DecisionState,
    Diagnose,
    Zielarchitektur,
    narrative,
    signalregister,
)

from tests.test_decision_signals import (
    ERZAEHLUNG,
    _diagnose,
    _familien,
    _zielarchitektur,
)


def _gepruefte_diagnose(**overrides: object) -> Diagnose:
    with narrative(ERZAEHLUNG):
        return Diagnose.model_validate(_diagnose(**overrides))


def _gepruefte_auswahl(diagnose: Diagnose, **overrides: object) -> Zielarchitektur:
    with signalregister(
        diagnose.decision_signals, diagnose.evidence_items
    ), narrative(ERZAEHLUNG):
        return Zielarchitektur.model_validate(_zielarchitektur(**overrides))


def _nicht_gewaehlt(anzahl: int = 1) -> list[object]:
    from app import solution_catalog

    return list(solution_catalog.katalog().values())[4 : 4 + anzahl]


# --- Die Ableitung ---------------------------------------------------------


def test_start_target_and_future_are_written_down() -> None:
    """Aus einem Lauf entsteht genau ein geprüfter Entscheidungszustand."""

    diagnose = _gepruefte_diagnose()
    gewaehlt = _gepruefte_auswahl(diagnose)

    zustand = decision_state.aus_lauf(diagnose, gewaehlt)

    familien = _familien()
    assert zustand.contract_version == "results-v1"
    assert zustand.target_family_ids == [f.kennung for f in familien]
    # Der Planner hat S1 ausdrücklich `start` genannt — das schlägt jede
    # Ableitung aus den Modulstufen.
    assert zustand.start_family_ids == [familien[0].kennung]
    assert [b.id for b in zustand.evidence] == ["B1", "B2"]
    assert [s.id for s in zustand.signals] == ["S1", "S2", "S3"]


def test_the_start_falls_back_to_what_is_actually_built() -> None:
    """Ohne benannten Einstieg gilt, was auf Stufe `jetzt` gebaut wird.

    Der Planner hat den Einstieg dann nicht benannt, aber er hat ihn
    gebaut. Das ist eine Aussage, und sie ist besser als keine.
    """

    diagnose = _gepruefte_diagnose()
    familien = _familien()
    ohne_start = {
        "items": [
            {
                "signal_id": "S1",
                "disposition": "target",
                "family_refs": [familien[1].kennung],
                "explanation": "Gehört zum Zielbild, ist aber kein Einstieg.",
            }
        ],
        "uncovered_critical_signal_ids": [],
    }
    gewaehlt = _gepruefte_auswahl(diagnose, coverage=ohne_start)

    zustand = decision_state.aus_lauf(diagnose, gewaehlt)

    # Genau das Modul mit Stufe `jetzt` — nicht das ganze Zielbild.
    assert zustand.start_family_ids == [familien[0].kennung]


def test_future_never_repeats_the_target() -> None:
    """Was empfohlen ist, ist kein Später.

    Der Ausbaupfad beginnt regelmässig mit der Familie, die gerade
    empfohlen wurde. Stünde sie danach auch als Später da, läge sie auf
    der Karte zweimal — in zwei verschiedenen Zuständen.
    """

    diagnose = _gepruefte_diagnose()
    familien = _familien()
    spaeter = _nicht_gewaehlt()[0]
    pfad = [
        {
            "stufe": "jetzt",
            "name": "Anfragen gemeinsam führen",
            "nutzen": "Sie sammeln Anfragen nicht mehr von Hand ein.",
            "bausteine": ["Ein Eingang", "Ein Stand"],
            "solution_family_ids": [familien[0].kennung],
        },
        {
            "stufe": "danach",
            "name": "Kunden selbst informieren",
            "nutzen": "Sie beantworten Standfragen nicht mehr selbst.",
            "bausteine": ["Stand ansehen", "Rückfragen stellen"],
            "solution_family_ids": [spaeter.kennung],
        },
    ]
    gewaehlt = _gepruefte_auswahl(diagnose, ausbaupfad=pfad)

    zustand = decision_state.aus_lauf(diagnose, gewaehlt)

    assert zustand.future_family_ids == [spaeter.kennung]
    assert familien[0].kennung not in zustand.future_family_ids


def test_open_signals_stay_visible() -> None:
    """Ein offener Punkt bleibt ein offener Punkt, kein Leerraum."""

    diagnose = _gepruefte_diagnose()
    familien = _familien()
    offen = {
        "items": [
            {
                "signal_id": "S1",
                "disposition": "start",
                "family_refs": [familien[0].kennung],
                "explanation": "Der Eingang trägt den Einstieg.",
            },
            {
                "signal_id": "S2",
                "disposition": "open",
                "family_refs": [],
                "explanation": "Aus der Erzählung nicht belastbar entscheidbar.",
            },
        ],
        "uncovered_critical_signal_ids": [],
    }
    gewaehlt = _gepruefte_auswahl(diagnose, coverage=offen)

    zustand = decision_state.aus_lauf(diagnose, gewaehlt)

    # S3 wurde vom Server als `open` nachgetragen und zählt genauso.
    assert set(zustand.open_signal_ids) == {"S2", "S3"}


def test_without_a_catalogue_hit_nothing_is_invented() -> None:
    """Ohne Katalogtreffer bleibt der Zustand leer — und die Belege bleiben."""

    diagnose = _gepruefte_diagnose()
    leer = _zielarchitektur(
        catalog_fit=False,
        selected_solution_family_ids=[],
        module=[],
        ausbaupfad=[],
        coverage={
            "items": [
                {
                    "signal_id": kennung,
                    "disposition": "open",
                    "family_refs": [],
                    "explanation": "Der Katalog hat dafür nichts Passendes.",
                }
                for kennung in ("S1", "S2", "S3")
            ],
            "uncovered_critical_signal_ids": [],
        },
    )
    with signalregister(
        diagnose.decision_signals, diagnose.evidence_items
    ), narrative(ERZAEHLUNG):
        gewaehlt = Zielarchitektur.model_validate(leer)

    zustand = decision_state.aus_lauf(diagnose, gewaehlt)

    assert zustand.target_family_ids == []
    assert zustand.start_family_ids == []
    # Was verstanden wurde, geht trotzdem mit.
    assert len(zustand.evidence) == 2
    assert len(zustand.signals) == 3


def test_the_same_run_yields_the_same_state() -> None:
    """Zweimal dieselbe Eingabe, zweimal dasselbe Ergebnis.

    Ohne diese Zusage könnte die Karte bei jedem Seitenaufruf anders
    aussehen, obwohl sich nichts geändert hat.
    """

    diagnose = _gepruefte_diagnose()
    gewaehlt = _gepruefte_auswahl(diagnose)

    erst = decision_state.aus_lauf(diagnose, gewaehlt).model_dump(mode="json")
    nochmal = decision_state.aus_lauf(diagnose, gewaehlt).model_dump(mode="json")

    assert erst == nochmal


# --- Die Invarianten -------------------------------------------------------


def test_the_start_must_lie_inside_the_target() -> None:
    """Womit man anfängt, ist ein Teil dessen, wohin man will."""

    familien = _familien()
    fremd = _nicht_gewaehlt()[0]
    with pytest.raises(ValidationError, match="nicht zum Zielbild"):
        DecisionState.model_validate(
            {
                "target_family_ids": [familien[0].kennung],
                "start_family_ids": [fremd.kennung],
            }
        )


def test_a_target_without_a_start_is_refused() -> None:
    """Eine Empfehlung ohne ersten Schritt ist keine."""

    familien = _familien()
    with pytest.raises(ValidationError, match="keinen Einstieg"):
        DecisionState.model_validate(
            {"target_family_ids": [familien[0].kennung], "start_family_ids": []}
        )


def test_unknown_families_are_refused() -> None:
    """Der Katalog gilt auch hier — fail-closed wie überall."""

    with pytest.raises(ValidationError, match="Katalog nicht gibt"):
        DecisionState.model_validate(
            {"target_family_ids": ["SF-99"], "start_family_ids": ["SF-99"]}
        )


def test_an_open_signal_must_exist() -> None:
    """Offen gemeldet wird nur, was es auch gibt."""

    with pytest.raises(ValidationError, match="Signale, die es nicht gibt"):
        DecisionState.model_validate({"open_signal_ids": ["S9"]})


# --- Das ausdrückliche Why-not ---------------------------------------------


def _absage(**overrides: object) -> dict[str, object]:
    daten: dict[str, object] = {
        "titel": "Termine automatisch vergeben",
        "family_refs": [_nicht_gewaehlt()[0].kennung],
        "grund": "missing_prerequisite",
        "erlaeuterung": (
            "Ein Termin ist nur so verlässlich wie die Kapazität dahinter, "
            "und die steht heute in keinem System."
        ),
        "evidence_refs": [],
        "fehlende_voraussetzung": "Eine verlässliche Auskunft über freie Zeit",
    }
    daten.update(overrides)
    return daten


def test_a_refusal_is_accepted() -> None:
    """Eine begründete Absage auf eine nicht gewählte Familie geht durch."""

    diagnose = _gepruefte_diagnose()
    gewaehlt = _gepruefte_auswahl(diagnose, why_not=[_absage()])

    zustand = decision_state.aus_lauf(diagnose, gewaehlt)

    assert len(zustand.why_not) == 1
    assert zustand.why_not[0].grund == "missing_prerequisite"


def test_a_refusal_may_not_contradict_the_recommendation() -> None:
    """Etwas empfehlen und gleichzeitig absagen ist keine Abwägung."""

    diagnose = _gepruefte_diagnose()
    with pytest.raises(ValidationError, match="aber diese Familie wurde empfohlen"):
        _gepruefte_auswahl(
            diagnose, why_not=[_absage(family_refs=[_familien()[0].kennung])]
        )


def test_a_refusal_needs_a_family_from_the_catalogue() -> None:
    """Auch eine Absage bleibt am Katalog festgemacht."""

    diagnose = _gepruefte_diagnose()
    with pytest.raises(ValidationError, match="Familie, die es nicht gibt"):
        _gepruefte_auswahl(diagnose, why_not=[_absage(family_refs=["SF-99"])])


def test_a_refusal_needs_a_real_reason() -> None:
    """„Passt nicht" ist auch hier keine Begründung."""

    diagnose = _gepruefte_diagnose()
    with pytest.raises(ValidationError, match="nachvollziehbare Begründung"):
        _gepruefte_auswahl(diagnose, why_not=[_absage(erlaeuterung="Passt nicht.")])


def test_a_refusal_may_not_invent_evidence() -> None:
    """Ein Beleg, den es nicht gibt, ist auch hier eine Erfindung."""

    diagnose = _gepruefte_diagnose()
    with pytest.raises(ValidationError, match="Belege, die es nicht gibt"):
        _gepruefte_auswahl(diagnose, why_not=[_absage(evidence_refs=["B9"])])


def test_at_most_two_refusals() -> None:
    """Eine Reihe von Absagen liest sich als Verteidigung, nicht als Beratung."""

    diagnose = _gepruefte_diagnose()
    drei = _nicht_gewaehlt(3)
    with pytest.raises(ValidationError):
        _gepruefte_auswahl(
            diagnose,
            why_not=[
                _absage(titel=f"Absage {nummer}", family_refs=[familie.kennung])
                for nummer, familie in enumerate(drei)
            ],
        )


def test_the_same_family_is_refused_only_once() -> None:
    """Zweimal dieselbe Absage ist eine Absage und ein Fehler."""

    diagnose = _gepruefte_diagnose()
    eine = _nicht_gewaehlt()[0]
    with pytest.raises(ValidationError, match="ein zweites Mal ab"):
        _gepruefte_auswahl(
            diagnose,
            why_not=[
                _absage(family_refs=[eine.kennung]),
                _absage(titel="Noch einmal dasselbe", family_refs=[eine.kennung]),
            ],
        )


def test_no_refusal_is_a_valid_answer() -> None:
    """Null ist richtig, wenn nichts Naheliegendes ausgeschlossen wurde."""

    diagnose = _gepruefte_diagnose()
    gewaehlt = _gepruefte_auswahl(diagnose)

    assert gewaehlt.why_not == []


# --- Persistenz und Rückwärtsverträglichkeit -------------------------------


def _ergebnis_mit(entscheidung: dict[str, object] | None) -> dict[str, object]:
    """Ein vollständiges Ergebnis, mit oder ohne festgehaltene Entscheidung."""

    from tests.test_result_contract import _part_one, _part_two

    daten = {**_part_one(), **_part_two()}
    if entscheidung is not None:
        daten["entscheidung"] = entscheidung
    return daten


def test_the_decision_survives_being_stored_and_read_back() -> None:
    """Was gespeichert wird, kommt geprüft wieder heraus.

    Der Weg, den die Ergebnisseite geht: Ergebnis validieren, als JSON
    ablegen, später erneut durch denselben Vertrag lesen. Ginge die
    Entscheidung dabei verloren, müsste die Seite sie wieder erraten.
    """

    from app.result_schema import Result
    from tests.test_result_contract import ERZAEHLUNG as HAUSVERWALTUNG, _kontext

    diagnose = _gepruefte_diagnose()
    gewaehlt = _gepruefte_auswahl(diagnose, why_not=[_absage()])
    zustand = decision_state.aus_lauf(diagnose, gewaehlt)

    ergebnis = Result.model_validate(
        _ergebnis_mit(zustand.model_dump(mode="json")), context=_kontext()
    )
    abgelegt = ergebnis.model_dump(mode="json")
    gelesen = Result.model_validate(abgelegt, context=_kontext())

    assert gelesen.entscheidung is not None
    assert gelesen.entscheidung.target_family_ids == zustand.target_family_ids
    assert gelesen.entscheidung.start_family_ids == zustand.start_family_ids
    # Die Belegkennungen tragen durch — daran hängt die ganze Beweiskette.
    assert [b.id for b in gelesen.entscheidung.evidence] == ["B1", "B2"]
    assert gelesen.entscheidung.coverage is not None
    assert [e.signal_id for e in gelesen.entscheidung.coverage.items] == [
        "S1",
        "S2",
        "S3",
    ]
    assert gelesen.entscheidung.why_not[0].family_refs == zustand.why_not[0].family_refs


def test_a_run_from_before_this_contract_still_reads() -> None:
    """Ein gespeichertes Ergebnis ohne Entscheidung bleibt gültig.

    Es gibt hinterlegte Beispielläufe und echte alte Sitzungen. Ihnen eine
    Entscheidung anzudichten hiesse, einen geprüften Durchlauf zu
    fälschen — also bleibt das Feld leer, und wer damit umgeht, entscheidet
    der Aufrufer.
    """

    from app.result_schema import Result
    from tests.test_result_contract import _kontext

    gelesen = Result.model_validate(_ergebnis_mit(None), context=_kontext())

    assert gelesen.entscheidung is None
