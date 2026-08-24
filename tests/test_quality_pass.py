"""Zwei Zusagen, die der kurze Weg von seinem Vorgänger erbt.

Der alte Ablauf hat sie über sieben Modellaufrufe hinweg eingelöst, dieser
über zwei. Die Behauptungen sind wörtlich dieselben geblieben — nur der Weg
dorthin ist kürzer:

1. Ein zweiter `POST /analyze` erzeugt nichts noch einmal.
2. Ist die Auswertung fertig, ändert eine erneut abgeschickte Erzählung nichts
   mehr.
"""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import repository
from app.models import InterviewQuestion
from tests.conftest import the_current_session, walk_to_the_result


ERZAEHLUNG = (
    "Wir sind eine kleine Schreinerei mit vier Leuten. Aufträge kommen per "
    "Telefon und per Mail herein, die Unterlagen liegen in drei Ordnern. Wenn "
    "jemand nach dem Stand fragt, muss ich erst zusammensuchen, wo die Sache "
    "gerade steht."
)


def _bis_zum_ergebnis(client: TestClient) -> int:
    """Den ganzen Kundenweg ab, bis das Ergebnis steht."""

    walk_to_the_result(client, ERZAEHLUNG)
    return the_current_session(client)


def test_a_second_analyze_call_changes_nothing(
    client: TestClient,
    database_session: Session,
) -> None:
    """Der Warteschirm darf zweimal anfragen, ohne zweimal zu bezahlen."""

    session_id = _bis_zum_ergebnis(client)
    erstes = repository.get_result(database_session, session_id)
    assert erstes is not None
    zuerst_erzeugt = erstes.created_at

    zweiter_aufruf = client.post(f"/sessions/{session_id}/analyze")

    assert zweiter_aufruf.status_code == 200
    assert zweiter_aufruf.json()["state"] == "complete"
    assert (
        zweiter_aufruf.json()["redirect_url"] == f"/sessions/{session_id}/results"
    )
    database_session.expire_all()
    danach = repository.get_result(database_session, session_id)
    assert danach is not None
    # Dasselbe Ergebnis, nicht ein zweites: Sonst waeren zwei Modellaeufe
    # fuer dieselbe Sitzung bezahlt worden.
    assert danach.created_at == zuerst_erzeugt
    assert client.get(f"/sessions/{session_id}/analysis-status").json()[
        "state"
    ] == "complete"


def test_a_finished_result_blocks_a_second_narrative(
    client: TestClient,
    database_session: Session,
) -> None:
    """Wer nach dem Ergebnis noch einmal erzählt, sieht sein Ergebnis."""

    session_id = _bis_zum_ergebnis(client)
    vorher = dict(
        database_session.execute(
            select(InterviewQuestion.question_key, InterviewQuestion.answer_text).where(
                InterviewQuestion.session_id == session_id
            )
        ).all()
    )

    erneut = client.post(
        f"/sessions/{session_id}/interview",
        data={"free_description": "Etwas ganz anderes."},
        follow_redirects=False,
    )

    assert erneut.headers["location"] == f"/sessions/{session_id}/results"
    database_session.expire_all()
    nachher = dict(
        database_session.execute(
            select(InterviewQuestion.question_key, InterviewQuestion.answer_text).where(
                InterviewQuestion.session_id == session_id
            )
        ).all()
    )
    assert nachher == vorher
