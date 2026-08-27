"""Die lange Arbeit verlässt den Request.

Ein Sprachmodell hat keine zugesagte Laufzeit. Solange die vollständige
Analyse in `POST /analyze` lief, blieb die Verbindung zum Browser rund
achtzig Sekunden offen — und im Betrieb schneiden Reverse Proxies solche
Requests ab. Dann stirbt die Arbeit mitten drin, und niemand weiss, wie
weit sie kam.

Wichtig ist der Unterschied, den Slawa gemacht hat: **Eine lange Analyse
ist aus Kundensicht in Ordnung. Ein minutenlang offener HTTP-Request ist
es nicht.**

In den Tests läuft Celery im Sofortmodus (`task_always_eager`, gesetzt in
`conftest`). Dadurch führt `.delay()` die Aufgabe an Ort und Stelle aus —
derselbe Code, nur an derselben Stelle. Was hier geprüft wird, ist der
Produktionspfad; nur der zweite Prozess fehlt.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import repository
from app.hintergrund import auswertung_erzeugen, celery_app
from app.services import analysis_service
from tests.conftest import the_current_session

ERZAEHLT = (
    "Kunden rufen den ganzen Tag an und fragen nach dem Stand ihrer Reparatur. "
    "Ich muss dann jedes Mal in die Werkstatt laufen und nachsehen."
)


def _bis_zur_analyse(client: TestClient) -> None:
    client.post("/begin", follow_redirects=False)
    client.post(
        "/interview", data={"free_description": ERZAEHLT}, follow_redirects=False
    )


def test_the_route_hands_the_work_to_the_queue(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """**Die Route rechnet nicht mehr selbst.**

    Das ist der ganze Punkt: Sie legt den Auftrag hin und ist fertig. Ob
    ihn ein Worker abholt oder der Sofortmodus ihn gleich ausführt, ändert
    daran nichts — der Aufruf geht über die Warteschlange.
    """

    eingestellt: list[int] = []
    echt = auswertung_erzeugen.delay

    def merken(session_id: int):
        eingestellt.append(session_id)
        return echt(session_id)

    monkeypatch.setattr(auswertung_erzeugen, "delay", merken)
    _bis_zur_analyse(client)

    client.post("/analyze")

    assert len(eingestellt) == 1


def test_the_worker_writes_where_the_page_reads(
    client: TestClient, database_session: Session
) -> None:
    """Der Worker legt das Ergebnis dort ab, wo die Seite es sucht.

    Deshalb braucht Celery kein Ergebnis-Backend: Der Zustand steht in
    PostgreSQL, und ein zweiter Speicher für dieselbe Information wäre
    eine zweite Wahrheit.
    """

    _bis_zur_analyse(client)
    sitzungsnummer = the_current_session(client)

    auswertung_erzeugen(sitzungsnummer)

    database_session.expire_all()
    zwischenstand = repository.get_partial_result(database_session, sitzungsnummer)
    assert zwischenstand is not None
    assert zwischenstand.payload is not None


def test_the_state_is_read_without_computing(
    client: TestClient, database_session: Session
) -> None:
    """`stand_der_auswertung` sagt, wo es steht — ohne ein Modell zu fragen.

    Seit die Analyse im Worker läuft, muss die Route antworten können,
    ohne selbst etwas anzustossen. Liefe hier noch ein Modellaufruf, wäre
    der Request wieder so lang wie vorher.
    """

    _bis_zur_analyse(client)
    sitzungsnummer = the_current_session(client)

    nutzlast, code = analysis_service.stand_der_auswertung(
        sitzungsnummer, database_session
    )

    assert code == 200
    # Nichts liegt vor, nichts wurde gerechnet: Der Auftrag ist unterwegs.
    assert nutzlast["state"] == "processing"
    assert repository.get_partial_result(database_session, sitzungsnummer) is None


def test_a_failed_run_is_visible_afterwards(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """**Der Grund überlebt den Worker.**

    Solange die Analyse im Request lief, stand der Fehler in dessen
    Antwort — der Browser wartete ohnehin darauf. Jetzt ist diese Antwort
    längst weg, wenn etwas schiefgeht. Ohne den Vermerk fragte der
    Warteschirm neunzig Mal nach und meldete eine Zeitüberschreitung,
    obwohl der Grund seit Sekunden feststand.
    """

    from app.openai_service import AIServiceError

    def scheitert(**_kwargs: object) -> None:
        raise AIServiceError("Der Modelldienst antwortet nicht.")

    monkeypatch.setattr(analysis_service, "generate_diagnosis", scheitert)
    _bis_zur_analyse(client)
    sitzungsnummer = the_current_session(client)

    auswertung_erzeugen(sitzungsnummer)

    database_session.expire_all()
    sitzung = repository.get_session(database_session, sitzungsnummer)
    assert sitzung is not None
    assert sitzung.lauf_fehler

    stand = client.get("/analysis-status").json()
    assert stand["state"] == "failed"
    assert stand["message"] == sitzung.lauf_fehler


def test_a_new_attempt_clears_the_old_reason(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ein neuer Versuch löscht den alten Vermerk.

    Sonst zeigte der Warteschirm sofort wieder den Fehler von vorhin, und
    die Schaltfläche zum Wiederholen wäre wirkungslos.
    """

    from app.openai_service import AIServiceError

    # Der erste Versuch scheitert, der zweite läuft durch. Die Attrappe aus
    # `conftest` wird dafür gemerkt und wieder eingesetzt — `monkeypatch.undo()`
    # würde auch sie entfernen und den Test ans echte Modell schicken.
    funktionierend = analysis_service.generate_diagnosis

    def scheitert(**_kwargs: object) -> None:
        raise AIServiceError("Der Modelldienst antwortet nicht.")

    monkeypatch.setattr(analysis_service, "generate_diagnosis", scheitert)
    _bis_zur_analyse(client)
    sitzungsnummer = the_current_session(client)
    auswertung_erzeugen(sitzungsnummer)
    database_session.expire_all()
    assert repository.get_session(database_session, sitzungsnummer).lauf_fehler

    monkeypatch.setattr(analysis_service, "generate_diagnosis", funktionierend)
    auswertung_erzeugen(sitzungsnummer)

    database_session.expire_all()
    assert repository.get_session(database_session, sitzungsnummer).lauf_fehler is None


def test_the_broker_is_one_configuration_line() -> None:
    """**Celery war das Beispiel, nicht das Lernziel.**

    Das Muster ist die Trennung von kurzem Request und langer Arbeit. Wo
    die Aufträge liegen, ist eine Einstellung: heute das Dateisystem, weil
    es ohne laufenden Dienst auskommt, im Betrieb `redis://…`.

    Und es gibt bewusst **kein Ergebnis-Backend** — der Zustand steht in
    PostgreSQL.
    """

    assert celery_app.conf.result_backend is None
    assert "ai_start_map.auswertung" in celery_app.tasks
