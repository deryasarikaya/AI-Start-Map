"""Was passiert, wenn ein Lauf nicht glatt durchgeht.

Zwei Fehlerbilder haben in echten Läufen etwa jeden zweiten Durchlauf gekostet:
ein Zitat, das nicht wörtlich in der Erzählung steht, und ein Zeitablauf, nach
dem der zweite Versuch nie ausgelöst hat. Für beide steht hier, was gelten
soll.
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context

import pytest
from openai import APITimeoutError

from app import openai_service
from app.result_schema import (
    MINIMUM_EVIDENCE,
    Diagnose,
    ResultPartOne,
    ResultPartTwo,
    narrative,
)
from tests.test_result_contract import ERZAEHLUNG, _diagnose, _part_one


def _teil_eins(zitate: list[str]) -> ResultPartOne:
    """Ein gültiger oberer Teil mit genau diesen Zitaten.

    Ohne eigenen `narrative()`-Block: Die Prüfung soll im Kontext des Aufrufers
    laufen, so wie im Betrieb auch. Ein eigener Block würde die Meldung über
    aussortierte Zitate mit sich nehmen, statt sie weiterzureichen.
    """

    payload = _part_one()
    payload["verstanden"]["belege"] = [
        {"zitat": zitat, "bedeutung": "Gemockte Bedeutung."} for zitat in zitate
    ]
    return ResultPartOne.model_validate(payload)


def _diagnose_mit(zitate: list[str]) -> Diagnose:
    """Eine gültige Diagnose mit genau diesen Zitaten.

    Ohne eigenen `narrative()`-Block, aus demselben Grund wie oben: Die
    Meldung über aussortierte Zitate soll den Aufrufer erreichen.
    """

    payload = _diagnose()
    payload["verstanden"] = {
        **payload["verstanden"],
        "belege": [
            {"zitat": zitat, "bedeutung": "Gemockte Bedeutung."}
            for zitat in zitate
        ],
    }
    return Diagnose.model_validate(payload)


ECHT = "per Telefon, per Mail und manchmal über WhatsApp"
ECHT_ZWEI = "muss ich erst suchen, wo die Meldung liegt"
ERFUNDEN = "Das hat der Kunde so nie gesagt"


# --- A: ein schlechtes Zitat toetet nicht den ganzen Lauf ------------------


def test_two_good_quotes_need_no_second_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Bleiben zwei Belege übrig, wird nicht nachgefragt."""

    aufrufe: list[str] = []

    def antworte(*, system_prompt: str, payload: object, result_type: object):
        aufrufe.append(system_prompt)
        return _diagnose_mit([ECHT, ERFUNDEN, ECHT_ZWEI])

    monkeypatch.setattr(openai_service, "parse_structured_output", antworte)

    with narrative(ERZAEHLUNG):
        ergebnis = openai_service._diagnosis_with_enough_evidence({})

    assert len(aufrufe) == 1
    assert len(ergebnis.verstanden.belege) == MINIMUM_EVIDENCE
    assert ERFUNDEN not in [beleg.zitat for beleg in ergebnis.verstanden.belege]


def test_too_few_quotes_trigger_one_targeted_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Bleibt zu wenig übrig, wird genau einmal nachgefragt — mit Hinweis."""

    aufrufe: list[str] = []
    zitate = [[ECHT, ERFUNDEN], [ECHT, ECHT_ZWEI]]

    def antworte(*, system_prompt: str, payload: object, result_type: object):
        aufrufe.append(system_prompt)
        return _diagnose_mit(zitate[len(aufrufe) - 1])

    monkeypatch.setattr(openai_service, "parse_structured_output", antworte)

    with narrative(ERZAEHLUNG):
        ergebnis = openai_service._diagnosis_with_enough_evidence({})

    assert len(aufrufe) == 2
    # Der zweite Aufruf nennt das abgelehnte Zitat wörtlich. Ohne das wäre es
    # blindes Neuwürfeln.
    assert ERFUNDEN in aufrufe[1]
    assert "wörtlich" in aufrufe[1]
    assert aufrufe[1].startswith(aufrufe[0])
    assert len(ergebnis.verstanden.belege) == MINIMUM_EVIDENCE


def test_a_hopeless_case_continues_without_the_evidence_section(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Hilft auch die Nachfrage nicht, entfällt der Abschnitt — nicht die Seite.

    Eine schwächere Seite ist besser als fünfzig Sekunden Arbeit, die im
    Papierkorb landen. Der Kunde bekommt eine Verstandenseite ohne Zitate,
    keinen Fehler — und es gibt keinen dritten Aufruf.
    """

    aufrufe: list[str] = []

    def antworte(*, system_prompt: str, payload: object, result_type: object):
        aufrufe.append(system_prompt)
        return _diagnose_mit([ERFUNDEN, "Auch das steht nirgends"])

    monkeypatch.setattr(openai_service, "parse_structured_output", antworte)

    with narrative(ERZAEHLUNG):
        ergebnis = openai_service._diagnosis_with_enough_evidence({})

    assert len(aufrufe) == 2
    assert ergebnis.verstanden.belege == []
    # Alles andere steht unverändert: Es geht weiter, nicht kaputt.
    assert ergebnis.engpass_satz
    assert ergebnis.vergleich_heute


def test_a_rejected_quote_never_survives_the_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Auch der zweite Versuch kommt nicht mit einem erfundenen Zitat durch.

    Der Retry ist eine zweite Chance auf **wörtliche** Belege, keine Amnestie.
    Sonst wäre die Nachfrage ein Weg, die Zitatprüfung zu umgehen.
    """

    aufrufe: list[str] = []
    zitate = [[ERFUNDEN], [ECHT, ERFUNDEN, ECHT_ZWEI]]

    def antworte(*, system_prompt: str, payload: object, result_type: object):
        aufrufe.append(system_prompt)
        return _diagnose_mit(zitate[len(aufrufe) - 1])

    monkeypatch.setattr(openai_service, "parse_structured_output", antworte)

    with narrative(ERZAEHLUNG):
        ergebnis = openai_service._diagnosis_with_enough_evidence({})

    assert len(aufrufe) == 2
    behalten = [beleg.zitat for beleg in ergebnis.verstanden.belege]
    assert ERFUNDEN not in behalten
    assert behalten == [ECHT, ECHT_ZWEI]


def test_no_third_call_is_ever_made(monkeypatch: pytest.MonkeyPatch) -> None:
    """Einmal nachfragen, nicht zweimal. Sonst wächst die Rechnung still."""

    aufrufe: list[str] = []

    def antworte(*, system_prompt: str, payload: object, result_type: object):
        aufrufe.append(system_prompt)
        return _diagnose_mit([ERFUNDEN])

    monkeypatch.setattr(openai_service, "parse_structured_output", antworte)

    with narrative(ERZAEHLUNG):
        openai_service._diagnosis_with_enough_evidence({})

    assert len(aufrufe) == 2


# --- B: der zweite Versuch nach Zeitablauf ---------------------------------


def test_a_timeout_gets_a_second_attempt_with_its_own_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ein Zeitablauf im ersten Versuch löst einen zweiten aus.

    Gälte das Zeitbudget für beide Versuche zusammen, bliebe für den zweiten
    nichts übrig, sobald der erste hineinläuft — er bräche ab, bevor er das
    Modell überhaupt gerufen hat.
    """

    # Das Modell muss gesetzt sein, sonst bricht der Aufruf ab, bevor er die
    # Attrappe erreicht — und der Test prüfte am Ende eine leere Liste.
    monkeypatch.setenv("OPENAI_MODEL", "gpt-5-mini")
    versuche: list[float] = []
    # Eine Uhr, die beim Zeitablauf wirklich weiterläuft. Ohne sie verbraucht
    # die Attrappe kein Budget, und der Defekt zeigt sich gar nicht.
    jetzt = [0.0]

    class Attrappe:
        def __init__(self, **_kwargs: object) -> None:
            self.chat = self

        @property
        def completions(self) -> Attrappe:
            return self

        @property
        def with_raw_response(self) -> Attrappe:
            return self

        def parse(self, *, timeout: float, **_kwargs: object) -> object:
            versuche.append(timeout)
            jetzt[0] += timeout
            raise APITimeoutError(request=None)

    monkeypatch.setattr(openai_service, "OpenAI", Attrappe)
    monkeypatch.setattr(openai_service, "perf_counter", lambda: jetzt[0])

    with pytest.raises(openai_service.AIServiceError):
        with narrative(ERZAEHLUNG):
            openai_service.parse_structured_output(
                system_prompt="egal",
                payload={},
                result_type=ResultPartOne,
            )

    assert len(versuche) == 2, "Der zweite Versuch hat nicht ausgelöst"
    # Der zweite bekommt das volle Budget, nicht den Rest des ersten. Ein
    # Anteil davon hat in zehn gemessenen Läufen mehr Läufe gekostet als
    # gerettet — die Antwortzeit des Modells schwankt zu stark.
    assert versuche == [
        openai_service.RESULT_TIMEOUT_SECONDS,
        openai_service.RESULT_TIMEOUT_SECONDS,
    ]


# --- D: der Zaehler, der von aussen log -----------------------------------


def test_the_counter_survives_a_thread_boundary() -> None:
    """Von aussen gelesen zeigt der Zähler, was drinnen passiert ist.

    Die Route läuft im Threadpool, und eine Zahl in einer Kontextvariablen
    wirkt nur in der Kopie. Von aussen stünde dort immer 0 — was aussieht
    wie „keine Aufrufe" und heisst „hier wurde nicht gezählt".
    """

    openai_service.reset_openai_call_count()

    def im_anderen_faden() -> None:
        # So, wie die Route es tut: erst zuruecksetzen, dann zaehlen.
        openai_service.reset_openai_call_count()
        openai_service._record_openai_call()
        openai_service._record_openai_call()

    with ThreadPoolExecutor(max_workers=1) as pool:
        pool.submit(copy_context().run, im_anderen_faden).result()

    assert openai_service.get_openai_call_count() == 2


def test_reading_without_a_reset_says_so_out_loud() -> None:
    """Ohne Zählbeginn kommt eine Ausnahme, keine stille Null."""

    def ohne_zaehlung() -> None:
        with pytest.raises(openai_service.CallCountUnavailable, match="gezählt"):
            openai_service.get_openai_call_count()

    # In einem frischen Kontext, damit ein Zuruecksetzen aus einem anderen
    # Test nicht hineinwirkt.
    copy_context().run(
        lambda: (
            openai_service._openai_calls.set(None),
            ohne_zaehlung(),
        )
    )


def test_the_narrative_is_sent_only_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Die Erzählung steht genau einmal im Prompt, nicht zweimal.

    Ginge sie zusätzlich als einzige „Antwort" mit, verdoppelte das den
    Prompt und spiegelte dem Modell zwei Quellen vor, wo es nur eine gibt.
    """

    gesehen: list[dict[str, object]] = []

    def antworte(*, system_prompt: str, payload: dict[str, object], result_type: object):
        gesehen.append(payload)
        return _diagnose_mit([ECHT, ECHT_ZWEI])

    monkeypatch.setattr(openai_service, "parse_structured_output", antworte)
    monkeypatch.setattr(
        openai_service, "generate_result_part_two", lambda **_kwargs: None, raising=False
    )

    openai_service.generate_diagnosis(
        narrative_text=ERZAEHLUNG,
        knowledge_chunks=[],
    )

    (payload,) = gesehen
    als_text = json.dumps(payload, ensure_ascii=False)
    assert als_text.count(ERZAEHLUNG) == 1


# --- 3b/A1: die Denkstufe der Ergebnisteile -------------------------------


class _Mitschreiber:
    """Fängt ab, womit das Modell tatsächlich gerufen wird."""

    def __init__(self) -> None:
        self.aufrufe: list[dict[str, object]] = []
        self.chat = self
        self.completions = self
        self.with_raw_response = self

    def __call__(self, **_kwargs: object) -> _Mitschreiber:
        return self

    def parse(self, **kwargs: object) -> object:
        kwargs["_weg"] = "parse"
        self.aufrufe.append(kwargs)
        raise APITimeoutError(request=None)

    def create(self, **kwargs: object) -> object:
        kwargs["_weg"] = "create"
        self.aufrufe.append(kwargs)
        raise APITimeoutError(request=None)


def _erster_aufruf(
    monkeypatch: pytest.MonkeyPatch, result_type: type = ResultPartOne
) -> dict[str, object]:
    """Ruft das Modell einmal und gibt zurück, womit es gerufen wurde."""

    mitschreiber = _Mitschreiber()
    monkeypatch.setattr(openai_service, "OpenAI", lambda **_kwargs: mitschreiber)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-5-mini")
    with pytest.raises(openai_service.AIServiceError):
        with narrative(ERZAEHLUNG):
            openai_service.parse_structured_output(
                system_prompt="egal", payload={}, result_type=result_type
            )
    return mitschreiber.aufrufe[0]


def test_the_result_parts_think_before_they_write(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Die Ergebnisteile laufen nicht auf der niedrigsten Denkstufe.

    Zeigt die Bedingung am Vertrag vorbei, läuft die wichtigste Ausgabe der
    Anwendung mit `reasoning_effort: minimal`. Wörtlich abschreiben ist
    genau die Aufgabe, bei der das schludert.
    """

    assert _erster_aufruf(monkeypatch)["reasoning_effort"] == "medium"


def test_the_second_part_thinks_less_than_the_first(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Teil 2 diagnostiziert nicht, er füllt aus.

    Auf `medium` scheiterten drei von zwölf Evaluationsfällen an
    `finish_reason=length`. Gemessen an einem der drei: Die Denk-Token
    zählen gegen dieselbe Grenze wie die Ausgabe — auf `medium` 2.432 von
    5.284 Token, auf `low` noch 576 bei gleich langer, vollständiger Antwort.
    """

    erster = _erster_aufruf(monkeypatch, ResultPartOne)
    zweiter = _erster_aufruf(monkeypatch, ResultPartTwo)

    assert erster["reasoning_effort"] == "medium"
    assert zweiter["reasoning_effort"] == "low"
    # Und beide denken überhaupt — der alte Fehler war `minimal`.
    assert zweiter["reasoning_effort"] != "minimal"


def test_every_call_has_an_upper_bound(monkeypatch: pytest.MonkeyPatch) -> None:
    """Eine Antwort darf nicht unbegrenzt weiterlaufen."""

    assert _erster_aufruf(monkeypatch)["max_completion_tokens"] > 0


def test_the_strict_schema_is_the_normal_way(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ohne Umstellung wird die Ausgabe an das Schema gebunden."""

    aufruf = _erster_aufruf(monkeypatch)

    assert aufruf["_weg"] == "parse"
    assert aufruf["response_format"] is ResultPartOne


def test_json_mode_carries_the_schema_in_the_prompt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Im JSON-Modus steht das Schema im Prompt statt in der Grammatik."""

    monkeypatch.setenv("OPENAI_STRUCTURED_MODE", "json")

    aufruf = _erster_aufruf(monkeypatch)

    assert aufruf["_weg"] == "create"
    assert aufruf["response_format"] == {"type": "json_object"}
    system = aufruf["messages"][0]["content"]
    assert "kurzfassung" in system
    assert "verstanden" in system


# --- Die niedrigste Denkstufe heisst nicht ueberall gleich ----------------


def test_the_lowest_effort_level_follows_the_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """**Ein unbekannter Wert laesst jeden Aufruf scheitern.**

    Die gpt-5-Modelle nennen die niedrigste Denkstufe `minimal`, ab
    gpt-5.6 heisst dieselbe Stufe `none`. Wer den falschen Namen schickt,
    bekommt keinen schlechteren Lauf, sondern gar keinen.
    """

    monkeypatch.setenv("OPENAI_MODEL", "gpt-5-mini")
    assert openai_service._reasoning_effort(gruendlich=False) == "minimal"

    monkeypatch.setenv("OPENAI_MODEL", "gpt-5.6-terra")
    assert openai_service._reasoning_effort(gruendlich=False) == "none"


def test_the_thorough_levels_are_named_the_same_everywhere(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`low` und `medium` gibt es in beiden Familien — die bleiben."""

    monkeypatch.delenv("OPENAI_REASONING_EFFORT", raising=False)
    monkeypatch.delenv("OPENAI_REASONING_EFFORT_TEIL2", raising=False)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-5.6-terra")

    assert openai_service._reasoning_effort(gruendlich=True) == "medium"
    assert openai_service._reasoning_effort(gruendlich=True, fuellt_nur=True) == "low"
