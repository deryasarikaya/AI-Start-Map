"""Der Trockenlauf des Zehn-Läufe-Skripts.

Kein Modellaufruf. Geprüft wird die eine Sache, an der es zehn bezahlte Läufe
lang vorbeigemessen hat: dass **beide** Modellaufrufe stattfinden und beide
gezählt werden.

Seit Schritt 2 liegt die Verstandenseite zwischen den Aufrufen. Der Läufer rief
`/analyze` einmal, bekam eine 200 zurück und meldete „durchgekommen" — gemessen
war aber nur der halbe Durchlauf. Ein Instrument, das falsch misst, ist
schlimmer als keins.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import zehn_laeufe  # noqa: E402


class _Antwort:
    def __init__(self, status: int = 200, text: str = "", ziel: str = "") -> None:
        self.status_code = status
        self.text = text
        self.headers = {"location": ziel} if ziel else {}


class _Attrappe:
    """Tut so, als wäre sie die Anwendung. Ruft nichts und kostet nichts."""

    #: Die Ergebnisseite zeigt zwei Belege, die Verstandenseite genau einen.
    ERGEBNISSEITE = '<div class="q">eins</div><div class="q">zwei</div>'

    def __init__(self, *, zweiter_status: int = 200) -> None:
        self.cookies = _Kekse()
        self.pfade: list[str] = []
        self._zweiter_status = zweiter_status

    def post(self, pfad: str, **_kwargs: object) -> _Antwort:
        self.pfade.append(pfad)
        if pfad == "/interview":
            return _Antwort(ziel="/processing")
        if pfad == "/analyze":
            erster = self.pfade.count("/analyze") == 1
            return _Antwort(200 if erster else self._zweiter_status, text="{}")
        return _Antwort()

    def get(self, _pfad: str) -> _Antwort:
        return _Antwort(text=self.ERGEBNISSEITE)


class _Kekse:
    def clear(self) -> None:
        return None


def _lauf(attrappe: _Attrappe, monkeypatch: pytest.MonkeyPatch) -> zehn_laeufe.Lauf:
    """Ein Lauf mit gezähltem Modellaufruf je `/analyze`-Anfrage."""

    gezaehlt = iter([1, 1, 1, 1])
    monkeypatch.setattr(zehn_laeufe, "reset_openai_call_count", lambda: None)
    monkeypatch.setattr(zehn_laeufe, "get_openai_call_count", lambda: next(gezaehlt))
    return zehn_laeufe.einen_lauf(
        attrappe, "Eine Erzählung.", zehn_laeufe.Mitschrift(), 1
    )


def test_a_run_makes_both_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    """Erst auswerten, dann weitergehen, dann noch einmal auswerten."""

    attrappe = _Attrappe()

    lauf = _lauf(attrappe, monkeypatch)

    assert attrappe.pfade.count("/analyze") == 2
    assert "/verstanden" in attrappe.pfade
    assert lauf.geschafft is True


def test_both_calls_are_counted(monkeypatch: pytest.MonkeyPatch) -> None:
    """`/analyze` setzt den Zähler je Anfrage zurück — also zweimal lesen.

    Wer erst am Ende liest, bekommt eine 1 und glaubt, ein Durchlauf koste
    einen Aufruf. Er kostet zwei, und das Budget rechnet damit.
    """

    lauf = _lauf(_Attrappe(), monkeypatch)

    assert lauf.modellaufrufe == 2


def test_the_evidence_is_counted_on_the_result_page(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Zwei Belege stehen auf der Ergebnisseite, einer auf der Verstandenseite.

    Solange der Läufer nach dem ersten Aufruf stehen blieb, zählte er die
    Verstandenseite und meldete überall genau einen Beleg.
    """

    lauf = _lauf(_Attrappe(), monkeypatch)

    assert lauf.belege_auf_der_seite == 2


def test_a_failing_second_call_says_which_call_failed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Scheitert Aufruf 2, steht das in der Ursache — nicht nur „gescheitert"."""

    lauf = _lauf(_Attrappe(zweiter_status=503), monkeypatch)

    assert lauf.geschafft is False
    assert lauf.ursache.startswith("Aufruf 2:")
    # Auch ein gescheiterter Lauf ist bezahlt — beide Aufrufe zählen mit.
    assert lauf.modellaufrufe == 2
