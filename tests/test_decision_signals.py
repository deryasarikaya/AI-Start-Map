"""Der Entscheidungsvertrag: Signalspeicher und Abdeckung.

**Wogegen diese Tests gebaut sind.** Seit der Breitensuche wurde die
Morgenübersicht in drei von drei Läufen gefunden und dem Planner
angeboten — und in drei von drei Läufen fallengelassen, ohne dass
irgendwo stand, dass sie fallengelassen wurde. Die Antwort darauf ist nicht, sie zu erzwingen,
sondern eine Stelle zu schaffen, an der ihr Verschwinden auffällt.

Deshalb prüfen die Tests hier zwei verschiedene Dinge, und die Trennung
ist der eigentliche Punkt:

1. **Was in sich nicht stimmt, scheitert.** Eine erfundene Belegkennung,
   ein Signal, das es nicht gibt, ein Einstieg auf einer Familie, aus der
   nichts gebaut wird.
2. **Was nur fehlt, wird sichtbar.** Ein übergangenes kritisches Signal
   lässt den Lauf nicht scheitern — es bekommt serverseitig ein `open` und
   steht in `uncovered_critical_signal_ids`. Sonst hinge die Auswertung
   eines Kunden an einer internen Zeile.

Keiner dieser Tests verlangt eine bestimmte Lösungsfamilie. Ein Vertrag,
der „Signal X also Familie Y" erzwingt, wäre genau die starre Zuordnung,
gegen die dieser Weg gebaut ist.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.result_schema import (
    Coverage,
    Diagnose,
    Zielarchitektur,
    narrative,
    signalregister,
    validation_context,
)

ERZAEHLUNG = (
    "Ich habe eine kleine Hausverwaltung mit drei Leuten. Mieter melden Schäden "
    "per Telefon, per Mail und manchmal über WhatsApp. Wenn der Mieter nach zwei "
    "Wochen nachfragt, muss ich erst suchen, wo die Meldung liegt. "
    "Morgens hätte ich gern eine Übersicht, was neu und was dringend ist. "
    "Eine Buchhaltungssoftware will ich nicht ersetzen."
)


def _kontext() -> dict[str, str]:
    return validation_context(ERZAEHLUNG)


def _diagnose(**overrides: object) -> dict[str, object]:
    """Eine Diagnose mit Ledger — zwei Belege, drei Signale, zwei kritisch."""

    daten: dict[str, object] = {
        "engpass_satz": "Meldungen werden nicht einheitlich festgehalten.",
        "verstanden": {
            "engpass_absatz": "Meldungen werden nicht einheitlich festgehalten.",
            "belege": [
                {
                    "zitat": "per Telefon, per Mail und manchmal über WhatsApp",
                    "bedeutung": "Die Meldungen kommen über drei Wege.",
                },
                {
                    "zitat": "muss ich erst suchen, wo die Meldung liegt",
                    "bedeutung": "Der aktuelle Stand ist nicht abrufbar.",
                },
            ],
            "eckdaten": ["Drei Personen", "Drei Eingangswege", "Kein Ort"],
        },
        "vergleich_heute": [
            "Die Meldung kommt per Telefon",
            "Jemand schreibt sie auf einen Zettel",
            "Beim Nachfragen wird gesucht",
        ],
        "rueckfrage": None,
        "evidence_items": [
            {
                "id": "B1",
                "zitat": "per Telefon, per Mail und manchmal über WhatsApp",
                "bedeutung": "Drei getrennte Eingangswege.",
            },
            {
                "id": "B2",
                "zitat": "Morgens hätte ich gern eine Übersicht",
                "bedeutung": "Er wünscht sich eine Tagesübersicht.",
            },
        ],
        "decision_signals": [
            {
                "id": "S1",
                "kind": "primary_pain",
                "statement": "Meldungen kommen über drei Wege herein.",
                "status": "confirmed",
                "critical": True,
                "evidence_refs": ["B1"],
            },
            {
                "id": "S2",
                "kind": "explicit_goal",
                "statement": "Morgens soll sichtbar sein, was neu und dringend ist.",
                "status": "confirmed",
                "critical": True,
                "evidence_refs": ["B2"],
            },
            {
                "id": "S3",
                "kind": "existing_system",
                "statement": "Die Buchhaltung bleibt, wie sie ist.",
                "status": "inferred",
                "critical": False,
                "evidence_refs": [],
            },
        ],
    }
    daten.update(overrides)
    return daten


def _familien() -> list[object]:
    from app import solution_catalog

    return list(solution_catalog.katalog().values())[:3]


def _zielarchitektur(**overrides: object) -> dict[str, object]:
    """Eine gültige Auswahl aus dem echten Katalog, mit Abdeckung."""

    familien = _familien()
    daten: dict[str, object] = {
        "catalog_fit": True,
        "recommend_new_technology": True,
        "begruendung": "Gemockte Begründung für die Auswahl.",
        "selected_solution_family_ids": [f.kennung for f in familien],
        "loesungsname": "Zentrale Vorgangsstelle",
        "relevante_module": ["Eingang", "Vorgangsakte"],
        "warum_diese_loesung": "Der Engpass liegt an der Erfassung.",
        "zielbild": {
            "name": "Zentrale Vorgangsstelle",
            "beschreibung": "Alle Meldungen laufen an einer Stelle zusammen.",
            "ablauf": [
                {
                    "art": "eingang",
                    "label": "Was hereinkommt",
                    "knoten": [{"text": "Telefon", "kategorie": "Kanal"}],
                }
            ],
        },
        "vergleich_kuenftig": [
            "Die Meldung landet an einer Stelle",
            "Sie wird dem Objekt zugeordnet",
            "Der Stand ist sichtbar",
        ],
        "module": [
            {
                "gruppe": "Eingang",
                "name": f"Baustein aus {familie.name}",
                "beschreibung": "Tut für diesen Betrieb, was nötig ist.",
                "stufe": ["jetzt", "danach", "spaeter"][platz],
                "solution_family_ids": [familie.kennung],
                "baustein_refs": [familie.bausteine[0]],
            }
            for platz, familie in enumerate(familien)
        ],
        "coverage": {
            "items": [
                {
                    "signal_id": "S1",
                    "disposition": "start",
                    "family_refs": [familien[0].kennung],
                    "explanation": "Der Eingang trägt den Einstieg.",
                },
                {
                    "signal_id": "S2",
                    "disposition": "future",
                    "family_refs": [familien[2].kennung],
                    "explanation": "Die Übersicht lohnt sich später.",
                },
            ],
            "uncovered_critical_signal_ids": [],
        },
    }
    daten.update(overrides)
    return daten


def _gepruefte_signale() -> list[object]:
    with narrative(ERZAEHLUNG):
        return Diagnose.model_validate(_diagnose()).decision_signals


# --- Der Speicher: Kennungen, Belege, Verweise -----------------------------


def test_ledger_is_accepted() -> None:
    """Ein Speicher mit gültigen Kennungen und wörtlichen Belegen geht durch."""

    diagnose = Diagnose.model_validate(_diagnose(), context=_kontext())

    assert [beleg.id for beleg in diagnose.evidence_items] == ["B1", "B2"]
    assert [signal.id for signal in diagnose.decision_signals] == ["S1", "S2", "S3"]
    assert [s.id for s in diagnose.decision_signals if s.critical] == ["S1", "S2"]


def test_ledger_quote_must_be_verbatim() -> None:
    """Ein umformulierter Beleg fliegt raus — dieselbe Regel wie überall.

    Nicht der ganze Lauf scheitert daran: Der Beleg fällt, der Rest bleibt.
    """

    belege = [
        {
            "id": "B1",
            "zitat": "Meldungen erreichen den Betrieb über verschiedene Kanäle",
            "bedeutung": "Umformuliert, steht so nicht da.",
        },
    ]
    diagnose = Diagnose.model_validate(
        _diagnose(
            evidence_items=belege,
            decision_signals=[
                {
                    "id": "S1",
                    "kind": "primary_pain",
                    "statement": "Meldungen kommen über drei Wege herein.",
                    "status": "confirmed",
                    "critical": True,
                    "evidence_refs": ["B1"],
                }
            ],
        ),
        context=_kontext(),
    )

    assert diagnose.evidence_items == []
    # Das Signal bleibt, der Verweis ist gelöst: Der Fehler steckte im
    # Zitat, nicht im Signal.
    assert diagnose.decision_signals[0].evidence_refs == []


def test_invented_evidence_reference_fails() -> None:
    """Ein Verweis auf eine nie geschriebene Kennung ist ein Fehler.

    Der Unterschied zum Test darüber: Dort gab es den Beleg, sein Zitat
    war nur falsch. Hier gab es ihn nie — dann behauptet das Signal einen
    Beleg, den niemand nachlesen kann.
    """

    with pytest.raises(ValidationError, match="Belege, die es nicht gibt"):
        Diagnose.model_validate(
            _diagnose(
                decision_signals=[
                    {
                        "id": "S1",
                        "kind": "primary_pain",
                        "statement": "Meldungen kommen über drei Wege herein.",
                        "status": "confirmed",
                        "critical": True,
                        "evidence_refs": ["B9"],
                    }
                ]
            ),
            context=_kontext(),
        )


def test_duplicate_signal_id_fails() -> None:
    """Zwei Signale mit derselben Kennung machen jeden Verweis mehrdeutig."""

    signal = {
        "id": "S1",
        "kind": "primary_pain",
        "statement": "Meldungen kommen über drei Wege herein.",
        "status": "inferred",
        "critical": False,
        "evidence_refs": [],
    }
    with pytest.raises(ValidationError, match="steht zweimal"):
        Diagnose.model_validate(
            _diagnose(decision_signals=[signal, dict(signal)]),
            context=_kontext(),
        )


def test_duplicate_evidence_id_fails() -> None:
    """Dasselbe für die Belegkennungen."""

    beleg = {
        "id": "B1",
        "zitat": "muss ich erst suchen, wo die Meldung liegt",
        "bedeutung": "Der Stand ist nicht abrufbar.",
    }
    with pytest.raises(ValidationError, match="steht zweimal"):
        Diagnose.model_validate(
            _diagnose(evidence_items=[beleg, dict(beleg)], decision_signals=[]),
            context=_kontext(),
        )


def test_identifier_shape_is_checked() -> None:
    """Eine Kennung ist kurz und maschinenlesbar, kein Satz."""

    with pytest.raises(ValidationError, match="ist keine Kennung"):
        Diagnose.model_validate(
            _diagnose(
                evidence_items=[
                    {
                        "id": "Der Beleg über die drei Eingangswege",
                        "zitat": "muss ich erst suchen, wo die Meldung liegt",
                        "bedeutung": "Der Stand ist nicht abrufbar.",
                    }
                ],
                decision_signals=[],
            ),
            context=_kontext(),
        )


@pytest.mark.parametrize("feld,wert", [("kind", "gefuehl"), ("status", "vielleicht")])
def test_only_known_kinds_and_states(feld: str, wert: str) -> None:
    """Arten und Zustände kommen aus der festen Liste, nicht aus der Fantasie."""

    signal = {
        "id": "S1",
        "kind": "primary_pain",
        "statement": "Meldungen kommen über drei Wege herein.",
        "status": "confirmed",
        "critical": True,
        "evidence_refs": ["B1"],
    }
    signal[feld] = wert
    with pytest.raises(ValidationError):
        Diagnose.model_validate(
            _diagnose(decision_signals=[signal]), context=_kontext()
        )


def test_ledger_without_narrative_fails() -> None:
    """Ohne Erzähltext lässt sich kein Beleg prüfen — also wird auch keiner geglaubt."""

    with pytest.raises(ValidationError, match="ohne den Erzähltext"):
        Diagnose.model_validate(_diagnose())


def test_older_diagnoses_stay_readable() -> None:
    """Eine gespeicherte Diagnose ohne Ledger bleibt gültig.

    Sonst wäre jeder Lauf von vor dieser Änderung beim Nachladen kaputt.
    """

    ohne = _diagnose()
    del ohne["evidence_items"]
    del ohne["decision_signals"]

    diagnose = Diagnose.model_validate(ohne, context=_kontext())

    assert diagnose.decision_signals == []
    assert diagnose.evidence_items == []


# --- Die Abdeckung: jede Entscheidung wird nachgehalten --------------------


def test_coverage_is_accepted() -> None:
    """Beide kritischen Signale entschieden — nichts bleibt offen."""

    with signalregister(_gepruefte_signale()), narrative(ERZAEHLUNG):
        gewaehlt = Zielarchitektur.model_validate(_zielarchitektur())

    assert gewaehlt.coverage is not None
    assert gewaehlt.coverage.uncovered_critical_signal_ids == []
    assert {e.signal_id for e in gewaehlt.coverage.items} == {"S1", "S2"}


def test_skipped_critical_signal_becomes_visible() -> None:
    """Der Kernfall: Ein übergangenes kritisches Signal verschwindet nicht mehr.

    Der Lauf scheitert daran nicht — daran ist die Antwort nicht falsch,
    nur unvollständig, und ein Kunde soll dafür keine Fehlermeldung sehen.
    Er bekommt serverseitig ein `open`, und die Kennung steht in der Liste,
    an der sich später ablesen lässt, wie oft der Planner es selbst nicht
    geschafft hat.
    """

    familien = _familien()
    nur_eins = {
        "items": [
            {
                "signal_id": "S1",
                "disposition": "start",
                "family_refs": [familien[0].kennung],
                "explanation": "Der Eingang trägt den Einstieg.",
            }
        ],
        "uncovered_critical_signal_ids": [],
    }
    with signalregister(_gepruefte_signale()), narrative(ERZAEHLUNG):
        gewaehlt = Zielarchitektur.model_validate(_zielarchitektur(coverage=nur_eins))

    assert gewaehlt.coverage is not None
    assert gewaehlt.coverage.uncovered_critical_signal_ids == ["S2"]
    nachgetragen = [e for e in gewaehlt.coverage.items if e.signal_id == "S2"]
    assert len(nachgetragen) == 1
    assert nachgetragen[0].disposition == "open"


def test_missing_coverage_is_filled_for_every_critical_signal() -> None:
    """Auch gar keine Abdeckung lässt kein kritisches Signal verschwinden."""

    with signalregister(_gepruefte_signale()), narrative(ERZAEHLUNG):
        gewaehlt = Zielarchitektur.model_validate(_zielarchitektur(coverage=None))

    assert gewaehlt.coverage is not None
    assert gewaehlt.coverage.uncovered_critical_signal_ids == ["S1", "S2"]
    assert all(e.disposition == "open" for e in gewaehlt.coverage.items)


def test_unknown_signal_id_fails() -> None:
    """Eine Entscheidung zu einem Signal, das es nicht gibt, ist ein Fehler."""

    familien = _familien()
    erfunden = {
        "items": [
            {
                "signal_id": "S9",
                "disposition": "target",
                "family_refs": [familien[0].kennung],
                "explanation": "Zu einem Signal, das niemand geschrieben hat.",
            }
        ],
        "uncovered_critical_signal_ids": [],
    }
    with signalregister(_gepruefte_signale()), narrative(ERZAEHLUNG):
        with pytest.raises(ValidationError, match="in der Diagnose nicht gibt"):
            Zielarchitektur.model_validate(_zielarchitektur(coverage=erfunden))


def test_one_signal_gets_one_decision() -> None:
    """Zwei Entscheidungen zu demselben Signal sind keine Entscheidung."""

    familien = _familien()
    doppelt = {
        "items": [
            {
                "signal_id": "S1",
                "disposition": "start",
                "family_refs": [familien[0].kennung],
                "explanation": "Der Eingang trägt den Einstieg.",
            },
            {
                "signal_id": "S1",
                "disposition": "future",
                "family_refs": [familien[2].kennung],
                "explanation": "Und gleichzeitig doch später.",
            },
        ],
        "uncovered_critical_signal_ids": [],
    }
    with signalregister(_gepruefte_signale()), narrative(ERZAEHLUNG):
        with pytest.raises(ValidationError, match="Genau eine je Signal"):
            Zielarchitektur.model_validate(_zielarchitektur(coverage=doppelt))


def test_unknown_family_in_coverage_fails() -> None:
    """Der Katalog gilt hier genauso wie bei den Modulen."""

    kaputt = {
        "items": [
            {
                "signal_id": "S1",
                "disposition": "future",
                "family_refs": ["SF-99"],
                "explanation": "Eine Familie, die es nicht gibt.",
            }
        ],
        "uncovered_critical_signal_ids": [],
    }
    with signalregister(_gepruefte_signale()), narrative(ERZAEHLUNG):
        with pytest.raises(ValidationError, match="Familie, die es nicht gibt"):
            Zielarchitektur.model_validate(_zielarchitektur(coverage=kaputt))


def test_start_must_point_at_a_family_that_is_built() -> None:
    """Ein Einstieg auf einer Familie ohne Modul ist eine Absichtserklärung.

    Die Familie ist ausgewählt — aber es entsteht kein Modul daraus. Wer
    das „Start" nennt, verspricht etwas, das niemand baut.
    """

    from app import solution_catalog

    familien = _familien()
    ohne_modul = list(solution_catalog.katalog().values())[3]
    auswahl = [f.kennung for f in familien] + [ohne_modul.kennung]
    falsch = {
        "items": [
            {
                "signal_id": "S1",
                "disposition": "start",
                "family_refs": [ohne_modul.kennung],
                "explanation": "Steht in der Auswahl, wird aber nicht gebaut.",
            }
        ],
        "uncovered_critical_signal_ids": [],
    }
    with signalregister(_gepruefte_signale()), narrative(ERZAEHLUNG):
        with pytest.raises(ValidationError, match="entsteht kein Modul"):
            Zielarchitektur.model_validate(
                _zielarchitektur(
                    selected_solution_family_ids=auswahl, coverage=falsch
                )
            )


def test_target_must_stay_inside_the_selection() -> None:
    """Was zum Zielbild gehört, gehört zu einer gewählten Familie."""

    from app import solution_catalog

    nicht_gewaehlt = list(solution_catalog.katalog().values())[4]
    falsch = {
        "items": [
            {
                "signal_id": "S1",
                "disposition": "target",
                "family_refs": [nicht_gewaehlt.kennung],
                "explanation": "Gehört zum Zielbild, ist aber nicht gewählt.",
            }
        ],
        "uncovered_critical_signal_ids": [],
    }
    with signalregister(_gepruefte_signale()), narrative(ERZAEHLUNG):
        with pytest.raises(ValidationError, match="nicht ausgewählt"):
            Zielarchitektur.model_validate(_zielarchitektur(coverage=falsch))


def test_future_may_leave_the_selection() -> None:
    """`future` darf auf eine Familie zeigen, die heute nicht gewählt ist.

    Das ist der ganze Sinn: Ein erkannter Bedarf, der jetzt nicht dran
    ist, bekommt eine ehrliche Antwort statt eines Platzes in der Auswahl.
    """

    from app import solution_catalog

    nicht_gewaehlt = list(solution_catalog.katalog().values())[4]
    familien = _familien()
    spaeter = {
        "items": [
            {
                "signal_id": "S1",
                "disposition": "start",
                "family_refs": [familien[0].kennung],
                "explanation": "Der Eingang trägt den Einstieg.",
            },
            {
                "signal_id": "S2",
                "disposition": "future",
                "family_refs": [nicht_gewaehlt.kennung],
                "explanation": "Lohnt sich, sobald die Vorgänge stehen.",
            },
        ],
        "uncovered_critical_signal_ids": [],
    }
    with signalregister(_gepruefte_signale()), narrative(ERZAEHLUNG):
        gewaehlt = Zielarchitektur.model_validate(_zielarchitektur(coverage=spaeter))

    assert gewaehlt.coverage is not None
    assert gewaehlt.coverage.uncovered_critical_signal_ids == []
    assert nicht_gewaehlt.kennung not in gewaehlt.selected_solution_family_ids


def test_not_recommended_needs_a_real_reason() -> None:
    """„Passt nicht" ist keine Begründung.

    Eine Nicht-Empfehlung ohne tragenden Grund ist dasselbe wie stilles
    Weglassen, nur mit einem Wort davor.
    """

    familien = _familien()
    duenn = {
        "items": [
            {
                "signal_id": "S1",
                "disposition": "start",
                "family_refs": [familien[0].kennung],
                "explanation": "Der Eingang trägt den Einstieg.",
            },
            {
                "signal_id": "S2",
                "disposition": "not_recommended",
                "family_refs": [],
                "explanation": "Passt nicht.",
            },
        ],
        "uncovered_critical_signal_ids": [],
    }
    with signalregister(_gepruefte_signale()), narrative(ERZAEHLUNG):
        with pytest.raises(ValidationError, match="nachvollziehbare Begründung"):
            Zielarchitektur.model_validate(_zielarchitektur(coverage=duenn))


def test_a_signal_never_forces_a_family() -> None:
    """Fünf kritische Signale, eine gebaute Familie — das ist erlaubt.

    Der Vertrag verlangt eine Entscheidung, keine Empfehlung. Träte hier
    eine Familie hinzu, wäre die Abdeckung ein Mechanismus zur
    Mengenmaximierung geworden statt einer Prüfung auf Bewusstsein.
    """

    familien = _familien()
    sparsam = {
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
    with signalregister(_gepruefte_signale()), narrative(ERZAEHLUNG):
        gewaehlt = Zielarchitektur.model_validate(_zielarchitektur(coverage=sparsam))

    assert len(gewaehlt.selected_solution_family_ids) == 3
    assert gewaehlt.coverage is not None
    assert gewaehlt.coverage.uncovered_critical_signal_ids == []


def test_coverage_without_the_ledger_fails() -> None:
    """Eine Abdeckung ohne die Signale lässt sich nicht prüfen — also gilt sie nicht.

    Dieselbe Haltung wie bei der Zitatprüfung: lieber ein Fehler als eine
    Prüfung, die stillschweigend übersprungen wird.
    """

    with narrative(ERZAEHLUNG):
        with pytest.raises(ValidationError, match="ohne die Signale"):
            Zielarchitektur.model_validate(_zielarchitektur())


def test_older_solutions_stay_readable() -> None:
    """Eine Auswahl ohne Abdeckung bleibt gültig, solange kein Ledger da ist."""

    ohne = _zielarchitektur()
    del ohne["coverage"]

    with narrative(ERZAEHLUNG):
        gewaehlt = Zielarchitektur.model_validate(ohne)

    assert gewaehlt.coverage is None


def test_empty_ledger_needs_no_coverage() -> None:
    """Ohne kritische Signale bleibt nichts offen — und nichts wird erfunden."""

    ohne = _zielarchitektur()
    del ohne["coverage"]

    with signalregister([]), narrative(ERZAEHLUNG):
        gewaehlt = Zielarchitektur.model_validate(ohne)

    assert gewaehlt.coverage is not None
    assert gewaehlt.coverage.items == []
    assert gewaehlt.coverage.uncovered_critical_signal_ids == []


def test_a_safety_boundary_survives_as_a_decision() -> None:
    """Eine Sicherheitsgrenze wird entschieden, nicht wegautomatisiert.

    `not_recommended` mit tragendem Grund ist die richtige Antwort auf
    „das darf das System nicht" — und der Punkt bleibt danach lesbar im
    Speicher stehen, statt zu verschwinden.
    """

    familien = _familien()
    grenze = {
        "id": "S4",
        "kind": "safety_boundary",
        "statement": "Verbindliche Preise nennt weiterhin ein Mensch.",
        "status": "confirmed",
        "critical": True,
        "evidence_refs": [],
    }
    with narrative(ERZAEHLUNG):
        signale = Diagnose.model_validate(
            _diagnose(
                decision_signals=[
                    *_diagnose()["decision_signals"],
                    grenze,
                ]
            )
        ).decision_signals

    entschieden = {
        "items": [
            {
                "signal_id": "S1",
                "disposition": "start",
                "family_refs": [familien[0].kennung],
                "explanation": "Der Eingang trägt den Einstieg.",
            },
            {
                "signal_id": "S2",
                "disposition": "future",
                "family_refs": [familien[2].kennung],
                "explanation": "Die Übersicht lohnt sich später.",
            },
            {
                "signal_id": "S4",
                "disposition": "not_recommended",
                "family_refs": [],
                "explanation": (
                    "Preise sind eine verbindliche Zusage und bleiben "
                    "deshalb beim Menschen."
                ),
            },
        ],
        "uncovered_critical_signal_ids": [],
    }
    with signalregister(signale), narrative(ERZAEHLUNG):
        gewaehlt = Zielarchitektur.model_validate(
            _zielarchitektur(coverage=entschieden)
        )

    assert gewaehlt.coverage is not None
    assert gewaehlt.coverage.uncovered_critical_signal_ids == []
    grenzeintrag = next(
        e for e in gewaehlt.coverage.items if e.signal_id == "S4"
    )
    assert grenzeintrag.disposition == "not_recommended"
    assert grenzeintrag.family_refs == []


def test_coverage_defaults_are_independent() -> None:
    """Zwei leere Abdeckungen teilen sich keine Liste."""

    eine, andere = Coverage(), Coverage()
    eine.uncovered_critical_signal_ids.append("S1")

    assert andere.uncovered_critical_signal_ids == []
