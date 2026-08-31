"""Was die Ergebnisseite braucht, ohne selbst nachzuschlagen.

**Wogegen das gebaut ist.** Ein Renderer, der nur den Vertrag liest,
konnte die Seite nicht zeichnen: Er hätte selbst herleiten müssen, wie es
heute ist, was ein Einstieg bringt, worauf eine spätere Möglichkeit
aufbaut und welche Punkte überhaupt zusammenhängen. Jede dieser
Herleitungen ist eine fachliche Entscheidung, und zwei Renderer treffen
sie verschieden.

Die Tests hier halten vor allem eines fest: **Nichts davon ist erfunden.**
Jeder Anker steht auf einem geprüften Zitat, jeder Outcome auf einem
geprüften Modulsatz, jede Abhängigkeit auf einer kuratierten Angabe im
Katalog — und wo nichts Belastbares vorliegt, bleibt das Feld leer.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app import operating_model, results_dto
from app.result_schema import Result, narrative
from app.results_dto import ANKER_ARTEN, ANKER_HOECHSTENS

WURZEL = Path(__file__).resolve().parents[1]
BEISPIEL = WURZEL / "knowledge/examples/hausverwaltung.json"
ALTLAUF = Path(__file__).resolve().parent / "data/hausverwaltung_v6.json"


def _dto_aus(datei: Path) -> results_dto.ResultDTO:
    inhalt = json.loads(datei.read_text(encoding="utf-8"))
    with narrative(inhalt["erzaehlung"]):
        return results_dto.von_ergebnis(Result.model_validate(inhalt["ergebnis"]))


@pytest.fixture(scope="module")
def beispiel() -> results_dto.ResultDTO:
    return _dto_aus(BEISPIEL)


# --- Der eingecheckte Beispiellauf -----------------------------------------


def test_the_stored_example_is_a_real_results_v1_run() -> None:
    """Der Vorführfall liegt im Projekt, nicht nur in einer lokalen Datenbank.

    Ein Beispiel, das an einer Sitzungsnummer auf einem Rechner hängt,
    ist am Vorführtag auf jedem anderen Rechner weg.
    """

    dto = _dto_aus(BEISPIEL)

    assert dto.herkunft == results_dto.VERTRAG
    assert not dto.ist_angepasst
    assert dto.entscheidung.contract_version == "results-v1"
    assert dto.entscheidung.signals and dto.entscheidung.evidence
    assert dto.entscheidung.start_family_ids
    assert dto.ansichten.primary is not None and dto.ansichten.primary.hat_inhalt


def test_the_legacy_run_still_adapts() -> None:
    """Derselbe Fall von vor dem Entscheidungsvertrag bleibt darstellbar.

    Nicht an einer Vorrichtung geprüft, sondern am echten alten Lauf —
    eine Vorrichtung hätte nur bewiesen, dass die Vorrichtung passt.
    """

    dto = _dto_aus(ALTLAUF)

    assert dto.ist_angepasst
    assert dto.herkunft == "ergebnis-v6-adaptiert"
    assert len(dto.module) == 14
    # Und nichts wird ihm angedichtet.
    assert dto.anker == ()
    assert dto.belege == ()


# --- Wie es heute ist ------------------------------------------------------


def test_anchors_are_between_one_and_three(beispiel: results_dto.ResultDTO) -> None:
    """Ein bis drei — mehr ist keine Zuspitzung, sondern eine Nacherzählung."""

    assert 1 <= len(beispiel.anker) <= ANKER_HOECHSTENS


def test_every_anchor_stands_on_a_real_quote(
    beispiel: results_dto.ResultDTO,
) -> None:
    """Ohne Beleg kein Anker.

    Ein Punkt über den Ist-Zustand, den niemand gesagt hat, wäre eine
    Behauptung über einen fremden Betrieb.
    """

    vorhanden = {beleg.id for beleg in beispiel.belege}

    for anker in beispiel.anker:
        assert anker.evidence_refs
        assert set(anker.evidence_refs) <= vorhanden
        assert anker.customer_label and anker.short_description


def test_anchors_describe_today_not_a_wish(
    beispiel: results_dto.ResultDTO,
) -> None:
    """Ein Ziel sagt, wo es hingehen soll — nicht, wie es ist."""

    arten = {
        signal.kind
        for signal in beispiel.entscheidung.signals
        if signal.id in {anker.id for anker in beispiel.anker}
    }

    assert arten <= set(ANKER_ARTEN)
    assert "explicit_goal" not in arten


def test_an_anchor_area_is_a_real_area(beispiel: results_dto.ResultDTO) -> None:
    """Der Bereich eines Ankers existiert — oder es steht keiner da."""

    schluessel = {bereich.schluessel for bereich in operating_model.BEREICHE}

    for anker in beispiel.anker:
        assert anker.business_area_ref is None or anker.business_area_ref in schluessel


def test_anchors_are_not_invented_without_a_ledger() -> None:
    """Ein Lauf ohne Speicher bekommt keine Anker angedichtet."""

    assert _dto_aus(ALTLAUF).anker == ()


# --- Was der Einstieg bringt -----------------------------------------------


def test_every_start_module_answers_what_it_brings(
    beispiel: results_dto.ResultDTO,
) -> None:
    """Jeder Start-Knoten beantwortet: Was bringt mir genau dieser Einstieg?

    Eine Fähigkeitenliste beantwortet das nicht — sie sagt, was das
    System kann, und nicht, welche Arbeit vom Tisch verschwindet.
    """

    starts = [m for m in beispiel.module if m.state == "start"]

    assert starts
    for modul in starts:
        assert modul.business_outcome
        assert modul.outcomes
        assert modul.why_now
        assert modul.capability_refs
        assert modul.evidence_refs
        assert modul.boundary_refs


def test_the_outcome_is_a_checked_sentence_from_the_result(
    beispiel: results_dto.ResultDTO,
) -> None:
    """Der Satz steht schon im Ergebnis — hier wird er nur zugeordnet.

    Damit kann er keine Marketingbehauptung sein: Er ist bereits durch
    die Prüfung gegen erfundene Ersparnisse gegangen.
    """

    inhalt = json.loads(BEISPIEL.read_text(encoding="utf-8"))
    aus_dem_ergebnis = {
        str(modul.get("nutzen") or "").strip()
        for modul in inhalt["ergebnis"]["module"]
    }

    for modul in beispiel.module:
        for satz in modul.outcomes:
            assert satz in aus_dem_ergebnis


def test_why_now_only_where_the_start_is(beispiel: results_dto.ResultDTO) -> None:
    """„Warum jetzt" gehört zum Einstieg, nicht zu jedem Bereich."""

    for modul in beispiel.module:
        if modul.state != "start":
            assert modul.why_now == ()


def test_prerequisites_keep_their_origin_apart(
    beispiel: results_dto.ResultDTO,
) -> None:
    """Was er gesagt hat und was der Katalog verlangt, bleibt unterscheidbar."""

    for modul in beispiel.module:
        for voraussetzung in modul.prerequisites:
            assert voraussetzung.herkunft in ("kunde", "katalog")
            if voraussetzung.herkunft == "katalog":
                assert voraussetzung.familie in modul.family_refs
            else:
                assert voraussetzung.familie is None


def test_a_quiet_area_promises_nothing(beispiel: results_dto.ResultDTO) -> None:
    """Ein Bereich, der kein Thema ist, verspricht auch nichts."""

    for modul in beispiel.module:
        if modul.state == "still":
            assert modul.outcomes == ()
            assert modul.why_now == ()
            assert modul.prerequisites == ()


# --- Worauf ein Später aufbaut ---------------------------------------------


def test_dependencies_point_at_real_modules(
    beispiel: results_dto.ResultDTO,
) -> None:
    """Eine Abhängigkeit zeigt auf einen Bereich, der jetzt entsteht."""

    jetzt = {m.module_key for m in beispiel.module if m.state in ("start", "target")}

    for ausblick in beispiel.ausblicke:
        assert set(ausblick.depends_on_module_refs) <= jetzt


def test_a_dependency_never_points_at_itself(
    beispiel: results_dto.ResultDTO,
) -> None:
    """„Baut auf sich selbst auf" ist keine Aussage.

    Der Ausbaupfad öffnet regelmässig einen Bereich weiter, in dem schon
    etwas steht — an einem echten Lauf trat genau das auf.
    """

    for ausblick in beispiel.ausblicke:
        assert ausblick.bereich not in ausblick.depends_on_module_refs


def test_an_empty_dependency_is_allowed(beispiel: results_dto.ResultDTO) -> None:
    """Ohne kuratierte Angabe bleibt die Liste leer statt erfunden.

    `grund_fuer_spaeter` erklärt es dann in Worten — das ist besser als
    eine Kante, die niemand geprüft hat.
    """

    for ausblick in beispiel.ausblicke:
        assert ausblick.grund_fuer_spaeter
        if not ausblick.depends_on_module_refs:
            assert isinstance(ausblick.depends_on_module_refs, tuple)


# --- Die Linien zwischen den Punkten ---------------------------------------


def test_relations_only_connect_visible_modules(
    beispiel: results_dto.ResultDTO,
) -> None:
    """Keine Linie zu einem Punkt, über den nichts gesagt wird."""

    sichtbar = {m.module_key for m in beispiel.sichtbare_module}

    assert beispiel.karte.beziehungen
    for beziehung in beispiel.karte.beziehungen:
        assert beziehung.von in sichtbar
        assert beziehung.nach in sichtbar


def test_relations_are_curated_not_derived_from_co_occurrence() -> None:
    """Keine Kante entsteht daraus, dass zwei Punkte im Ergebnis vorkommen.

    Die Probe: Zwei Bereiche, die gemeinsam empfohlen werden, für die der
    Katalog aber keine allgemeingültige Beziehung kennt, bleiben ohne
    Linie.
    """

    from app.result_schema import DecisionState
    from app import map_state

    zustand = DecisionState.model_validate(
        {
            "target_family_ids": ["SF-11", "SF-21"],
            "start_family_ids": ["SF-11", "SF-21"],
        }
    )
    karte = map_state.aus_entscheidung(zustand)

    assert {k.schluessel for k in karte.knoten if k.zustand != "still"} == {
        "wissen_zugaenglich",
        "menschen_qualifikation",
    }
    assert karte.beziehungen == ()


def test_every_curated_relation_names_real_areas() -> None:
    """Die Tabelle selbst kennt keine Phantom-Knoten."""

    operating_model.pruefe_vollstaendigkeit()
    schluessel = {bereich.schluessel for bereich in operating_model.BEREICHE}

    for beziehung in operating_model.BEZIEHUNGEN:
        assert beziehung.von in schluessel
        assert beziehung.nach in schluessel
        assert beziehung.von != beziehung.nach
        assert beziehung.art in (
            "feeds_into",
            "enables",
            "shared_state_for",
            "extends_to",
        )


# --- Web und PDF ------------------------------------------------------------


def test_the_contract_stays_readable_twice(beispiel: results_dto.ResultDTO) -> None:
    """Zweimal derselbe Lauf, zweimal derselbe Vertrag — Web wie PDF."""

    nochmal = _dto_aus(BEISPIEL)

    assert beispiel.anker == nochmal.anker
    assert beispiel.module == nochmal.module
    assert beispiel.karte.beziehungen == nochmal.karte.beziehungen
    assert beispiel.ausblicke == nochmal.ausblicke


# --- Woraus ein Später folgt -----------------------------------------------


def test_an_outlook_carries_the_evidence_of_its_own_families(
    beispiel: results_dto.ResultDTO,
) -> None:
    """Ein Ausblick steht auf den Zitaten seiner eigenen Familien.

    Die Kette lag schon bereit — Abdeckung, Signal, Zitat —, nur abgefragt
    hatte sie hier niemand. Ein Ausblick ohne Beleg liest sich wie eine
    Idee statt wie eine Folge aus dem, was er erzählt hat.
    """

    nach_bereich = {a.bereich: a for a in beispiel.ausblicke}

    assert nach_bereich["steuerung_vorschau"].beleg_refs == ("B4",)
    assert nach_bereich["service_selfservice"].beleg_refs == ("B6",)


def test_an_outlook_without_evidence_stays_empty(
    beispiel: results_dto.ResultDTO,
) -> None:
    """Wo nichts belegt ist, wird nichts geliehen.

    SF-04 und SF-12 haben in diesem Fall kein Signal, das auf ein Zitat
    zeigt. Ihnen eines der Nachbarn zu geben, sähe genauso überzeugend
    aus wie ein echter Beleg — und wäre eine Verbindung, die niemand
    geprüft hat.
    """

    nach_bereich = {a.bereich: a for a in beispiel.ausblicke}

    assert nach_bereich["daten_systemverbund"].familien == ("SF-04",)
    assert nach_bereich["daten_systemverbund"].beleg_refs == ()
    assert nach_bereich["vorgaenge_aufgaben"].familien == ("SF-12",)
    assert nach_bereich["vorgaenge_aufgaben"].beleg_refs == ()


def test_every_outlook_reference_exists(beispiel: results_dto.ResultDTO) -> None:
    """Jede Kennung zeigt auf einen Beleg, den es wirklich gibt."""

    vorhanden = {beleg.id for beleg in beispiel.belege}

    for ausblick in beispiel.ausblicke:
        assert set(ausblick.beleg_refs) <= vorhanden


def test_an_outlook_borrows_no_foreign_evidence(
    beispiel: results_dto.ResultDTO,
) -> None:
    """Kein Zitat aus einer Familie, die zu diesem Ausblick nicht gehört.

    Die Probe geht über dieselbe Zuordnung, die auch die Bereiche
    benutzen: Was dort nicht unter einer der eigenen Familien steht, darf
    hier nicht auftauchen.
    """

    zuordnung = results_dto._belege_je_familie(beispiel.entscheidung)

    for ausblick in beispiel.ausblicke:
        erlaubt = {
            bezug
            for familie in ausblick.familien
            for bezug in zuordnung.get(familie, [])
        }
        assert set(ausblick.beleg_refs) <= erlaubt


def test_outlook_evidence_is_free_of_duplicates_and_stable(
    beispiel: results_dto.ResultDTO,
) -> None:
    """Keine Kennung zweimal, und zweimal derselbe Lauf ergibt dasselbe."""

    nochmal = _dto_aus(BEISPIEL)

    for ausblick, wieder in zip(beispiel.ausblicke, nochmal.ausblicke):
        assert len(ausblick.beleg_refs) == len(set(ausblick.beleg_refs))
        assert ausblick.beleg_refs == wieder.beleg_refs


def test_a_run_without_a_ledger_gets_no_outlook_evidence() -> None:
    """Ein Lauf ohne Speicher bekommt auch hier nichts angedichtet."""

    for ausblick in _dto_aus(ALTLAUF).ausblicke:
        assert ausblick.beleg_refs == ()
