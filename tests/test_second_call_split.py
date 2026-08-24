"""Der untere Teil entsteht in zwei Aufrufen.

Kein Modellaufruf. Geprüft wird, dass wirklich geteilt wird — und dass das
Zusammensetzen nichts durchrutschen lässt.

Der Anlass: Aufruf 1 schaffte zehn von zehn, der ungeteilte Aufruf 2 sieben von
zwölf. Er hatte 65 Felder und Schachtelungstiefe acht, doppelt so viel wie
Aufruf 1. Wenn die Teilung nicht wirklich teilt, misst der nächste Goldlauf
dasselbe wie vorher und sagt es nicht.
"""

from __future__ import annotations

import pytest

from app import openai_service
from app.result_schema import (
    ResultPartOne,
    ResultPartTwo,
    ResultPartTwoRest,
    ResultPartTwoViews,
    narrative,
)
from tests.test_result_contract import ERZAEHLUNG, _part_one, _part_two


def _teil_eins() -> ResultPartOne:
    with narrative(ERZAEHLUNG):
        return ResultPartOne.model_validate(_part_one())


class _Zwei:
    """Merkt sich, womit gerufen wurde, und antwortet passend zum Schema."""

    def __init__(self, *, scheitert_bei: type | None = None) -> None:
        self.aufrufe: list[tuple[str, type]] = []
        self._scheitert_bei = scheitert_bei

    def __call__(
        self, *, system_prompt: str, payload: dict, result_type: type
    ) -> object:
        self.aufrufe.append((system_prompt, result_type))
        if result_type is self._scheitert_bei:
            raise openai_service.AIServiceError("So tut ein gescheiterter Aufruf.")
        daten = _part_two()
        if result_type is ResultPartTwoViews:
            return ResultPartTwoViews.model_validate(
                {"ansichten": daten["ansichten"]}
            )
        return ResultPartTwoRest.model_validate(
            {k: v for k, v in daten.items() if k != "ansichten"}
        )


def _erzeuge(zwei: _Zwei, monkeypatch: pytest.MonkeyPatch) -> ResultPartTwo:
    monkeypatch.setattr(openai_service, "parse_structured_output", zwei)
    return openai_service.generate_result_part_two(
        narrative_text=ERZAEHLUNG, part_one=_teil_eins(), knowledge_chunks=[]
    )


def test_the_lower_part_is_written_in_two_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Erst die Ansichten, dann der Rest — mit je eigenem Schema."""

    zwei = _Zwei()

    _erzeuge(zwei, monkeypatch)

    assert [typ for _prompt, typ in zwei.aufrufe] == [
        ResultPartTwoViews,
        ResultPartTwoRest,
    ]


def test_each_call_gets_its_own_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sonst bekäme jeder Aufruf wieder die Beschreibung von allem."""

    zwei = _Zwei()

    _erzeuge(zwei, monkeypatch)

    ansichten_prompt, rest_prompt = (p for p, _typ in zwei.aufrufe)
    assert "Beispielansichten" in ansichten_prompt
    assert "aufgabenteilung.system" not in ansichten_prompt
    assert "aufgabenteilung.system" in rest_prompt
    assert "vorgangsakte" not in rest_prompt


def test_both_halves_end_up_in_one_result(monkeypatch: pytest.MonkeyPatch) -> None:
    """Was gespeichert und gezeigt wird, hat weiterhin alle sieben Bereiche."""

    teil_zwei = _erzeuge(_Zwei(), monkeypatch)

    assert len(teil_zwei.ansichten) >= 2
    assert teil_zwei.aufgabenteilung.system
    assert teil_zwei.systeme and teil_zwei.architektur and teil_zwei.umsetzung
    assert teil_zwei.wert.faellt_weg


def test_the_views_are_handed_to_the_second_half(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """2b soll zu dem passen, was der Kunde gezeigt bekommt."""

    gesehen: list[dict] = []

    class _Merker(_Zwei):
        def __call__(self, *, system_prompt: str, payload: dict, result_type: type):
            gesehen.append(payload)
            return super().__call__(
                system_prompt=system_prompt, payload=payload, result_type=result_type
            )

    _erzeuge(_Merker(), monkeypatch)

    assert "BEREITS_GESCHRIEBENE_ANSICHTEN" not in gesehen[0]
    assert "BEREITS_GESCHRIEBENE_ANSICHTEN" in gesehen[1]


@pytest.mark.parametrize("stirbt", [ResultPartTwoViews, ResultPartTwoRest])
def test_a_failing_half_leaves_no_half_result(
    stirbt: type, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scheitert 2a oder 2b, kommt nichts zurück — auch kein Teilergebnis.

    Der Aufrufer speichert erst, wenn er ein vollständiges Ergebnis hat. Ein
    halbes wäre schlimmer als keins: Die Seite zeigt dann einen Hinweis statt
    einer Lücke.
    """

    with pytest.raises(openai_service.AIServiceError):
        _erzeuge(_Zwei(scheitert_bei=stirbt), monkeypatch)


def test_the_levers_are_still_checked_in_the_second_half() -> None:
    """Die Prüfung sitzt bei 2b, weil die Hebel dort entstehen."""

    daten = {k: v for k, v in _part_two().items() if k != "ansichten"}
    daten["hebel"] = [
        {
            "idee": "Erhöhen Sie Ihre Preise.",
            "woraus": "Das hat der Betrieb nie gesagt.",
            "warum": "Steht nicht in seiner Erzählung.",
            "ohne_technik": True,
        }
    ]

    from app.result_schema import validation_context

    uebriges = ResultPartTwoRest.model_validate(
        daten, context=validation_context(ERZAEHLUNG)
    )

    assert uebriges.hebel == []


def test_the_second_half_is_the_flat_one() -> None:
    """Der Schnitt verläuft bei den Ansichten — sie sind das Verschachtelte.

    Gemessen: das ungeteilte Schema 11.503 Zeichen und Tiefe acht,
    Aufruf 1 zum Vergleich 5.269. Danach sieht 2b noch 3.934 Zeichen bei Tiefe
    sechs — flacher und kleiner als Aufruf 1, der zehn von zehn schaffte. 2a
    bleibt gross, aber kein Aufruf sieht mehr das Ganze.
    """

    import json

    ganz = len(json.dumps(ResultPartTwo.model_json_schema()))
    ansichten = len(json.dumps(ResultPartTwoViews.model_json_schema()))
    uebriges = len(json.dumps(ResultPartTwoRest.model_json_schema()))
    aufruf_eins = len(json.dumps(ResultPartOne.model_json_schema()))

    assert ansichten < ganz * 0.75
    # Der flache Teil ist kleiner als Aufruf 1 — der stirbt nie.
    assert uebriges < aufruf_eins
