"""Der Erzeugungsdienst des kurzen Wegs.

Zwei Modellaufrufe, ein gespeichertes Ergebnis. Geprüft wird der vollständige
Durchlauf und der Fall, dass der zweite Aufruf scheitert — dann darf nichts in
der Datenbank landen.
"""

from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from app import repository
from app.models import AnalysisSession
from app.openai_service import AIServiceError
from app.result_schema import Diagnose, ResultPartTwo, narrative
from app.services import analysis_service
from tests.test_result_contract import (
    ERZAEHLUNG,
    _diagnose,
    _part_two,
    _zielarchitektur,
)


def _session(database_session: Session) -> int:
    """Legt eine leere Sitzung an und gibt ihre Nummer zurück."""

    sitzung = AnalysisSession()
    database_session.add(sitzung)
    database_session.commit()
    _erzaehlung_ablegen(database_session, sitzung.session_id)
    return sitzung.session_id


def _ganzer_lauf(session_id: int, database_session: Session):
    """Beide Schritte hintereinander, wie der Warteschirm sie auslöst.

    Seit dem Agentenschritt liegt zwischen ihnen die Verstandenseite; für die
    Zusagen hier ist nur wichtig, dass beide Schritte gelaufen sind.
    """

    analysis_service.run_first_call(session_id, database_session)
    analysis_service.move_on(database_session, session_id)
    return analysis_service.run_second_call(session_id, database_session)


def _erzaehlung_ablegen(database_session: Session, session_id: int) -> None:
    """Legt die Erzählung so ab, wie der Einstieg sie ablegen würde."""

    from app.questions import INTRO_QUESTIONS
    from app.models import InterviewQuestion

    database_session.add_all(
        [
            InterviewQuestion(
                session_id=session_id,
                question_phase=frage["phase"],
                question_order=frage["order"],
                question_key=frage["key"],
                question_text=frage["text"],
                answer_text=ERZAEHLUNG,
            )
            for frage in INTRO_QUESTIONS
        ]
    )
    database_session.commit()


def _teil_eins() -> Diagnose:
    with narrative(ERZAEHLUNG):
        return Diagnose.model_validate(_diagnose())


def _teil_zwei() -> ResultPartTwo:
    with narrative(ERZAEHLUNG):
        return ResultPartTwo.model_validate(_part_two())


def test_full_run_stores_the_result(
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Beide Aufrufe gelingen, das Ergebnis liegt in der Datenbank."""

    session_id = _session(database_session)
    monkeypatch.setattr(
        analysis_service, "generate_diagnosis", lambda **_kwargs: _teil_eins()
    )
    monkeypatch.setattr(
        analysis_service, "generate_result_part_two", lambda **_kwargs: _teil_zwei()
    )

    gespeichert = _ganzer_lauf(session_id, database_session)

    assert gespeichert.session_id == session_id
    assert gespeichert.narrative == ERZAEHLUNG
    assert gespeichert.payload["contract_version"] == "ergebnis-v6"
    # Beide Hälften stehen im selben Datensatz.
    assert gespeichert.payload["kurzfassung"]["loesungsname"]
    assert len(gespeichert.payload["ansichten"]) >= 2


def test_stored_result_is_checked_against_the_contract(
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Was gelesen wird, geht noch einmal durch den Vertrag."""

    session_id = _session(database_session)
    monkeypatch.setattr(
        analysis_service, "generate_diagnosis", lambda **_kwargs: _teil_eins()
    )
    monkeypatch.setattr(
        analysis_service, "generate_result_part_two", lambda **_kwargs: _teil_zwei()
    )
    _ganzer_lauf(session_id, database_session)

    gelesen = analysis_service.stored_result(database_session, session_id)

    assert gelesen is not None
    assert gelesen.kurzfassung.engpass_satz
    assert len(gelesen.verstanden.belege) >= 2


def test_missing_result_reads_as_none(database_session: Session) -> None:
    """Ohne Ergebnis kommt None zurück, keine Ausnahme."""

    assert analysis_service.stored_result(database_session, _session(database_session)) is None


def test_failing_second_call_stores_nothing(
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Scheitert der zweite Aufruf, bleibt die Datenbank leer.

    Ein halbes Ergebnis wäre schlimmer als keins: Die Seite würde es anzeigen.
    """

    session_id = _session(database_session)
    monkeypatch.setattr(
        analysis_service, "generate_diagnosis", lambda **_kwargs: _teil_eins()
    )

    def scheitert(**_kwargs: object) -> ResultPartTwo:
        raise AIServiceError("Die KI-Antwort konnte nicht verarbeitet werden.")

    monkeypatch.setattr(analysis_service, "generate_result_part_two", scheitert)

    with pytest.raises(AIServiceError):
        _ganzer_lauf(session_id, database_session)

    database_session.rollback()
    assert repository.get_result(database_session, session_id) is None


def test_second_run_replaces_the_first(
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ein zweiter Durchlauf ersetzt das Ergebnis, statt zu scheitern."""

    session_id = _session(database_session)
    monkeypatch.setattr(
        analysis_service, "generate_diagnosis", lambda **_kwargs: _teil_eins()
    )
    monkeypatch.setattr(
        analysis_service, "generate_result_part_two", lambda **_kwargs: _teil_zwei()
    )
    _ganzer_lauf(session_id, database_session)

    # Der Name der Lösung entsteht jetzt bei der Auswahl, nicht in der
    # Diagnose — der zweite Lauf ersetzt deshalb dort.
    anderer_name = _zielarchitektur()
    anderer_name["loesungsname"] = "Ein anderer Name"
    anderer_name["zielbild"]["name"] = "Ein anderer Name"

    def zweiter_lauf(**_kwargs: object) -> object:
        from app.result_schema import Zielarchitektur

        with narrative(ERZAEHLUNG):
            return Zielarchitektur.model_validate(anderer_name)

    monkeypatch.setattr(
        analysis_service, "generate_target_architecture", zweiter_lauf
    )
    _ganzer_lauf(session_id, database_session)

    gespeichert = repository.get_result(database_session, session_id)
    assert gespeichert is not None
    assert gespeichert.payload["kurzfassung"]["loesungsname"] == "Ein anderer Name"
