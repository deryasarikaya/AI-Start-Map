"""Rückfragen, Analyse und Ergebnis.

Aus `routes.py` unverändert hierher verschoben. Kein HTTP - die Routen
reichen nur durch. `retrieval_context` und `agent_pattern_context` sind die
beiden Stellen, an denen die Anwendung im Suchindex nachschlägt.
"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.agent_service import search_diagnostic_knowledge
from fastapi import status

from app.openai_service import AIServiceError
from app.rag_service import (
    RagConfigurationError,
    format_chunks_for_prompt,
    retrieve_agent_patterns,
    retrieve_solution_context,
)
from pydantic import ValidationError

from app import solution_catalog
from app.result_schema import (
    Diagnose,
    Result,
    ResultPartOne,
    Zielarchitektur,
    narrative,
)

logger = logging.getLogger(__name__)


from time import perf_counter

from app.openai_service import (
    generate_diagnosis,
    generate_result_part_two,
    generate_target_architecture,
    counted_calls_for_logging,
    reset_openai_call_count,
)
from app import repository


def retrieval_context(query: str, phase: str) -> list[str]:
    """Sucht Vergleichswissen im Diagnoseindex.

    Eine von zwei Stellen, an denen die Anwendung nachschlägt. Was
    zurückkommt, ist Vergleichswissen und niemals ein Fakt über
    diesen Betrieb.
    """

    return [
        evidence.content
        for evidence in search_diagnostic_knowledge(query, phase=phase)
    ]


def agent_pattern_context(query: str) -> tuple[list[str], list[str]]:
    """Retrieve optional interview patterns without weakening Python guardrails."""

    try:
        patterns = retrieve_agent_patterns(
            query,
            allowed_types={
                "agent_decision_pattern",
                "next_question_pattern",
                "contradiction_pattern",
                "agent_stop_rule",
                "tool_selection_pattern",
                "agent_guardrail",
            },
            top_k=3,
        )
    except (AIServiceError, RagConfigurationError):
        logger.warning("agent_pattern_retrieval.fallback pattern_count=0")
        return [], []
    pattern_types = [pattern.chunk_type for pattern in patterns]
    logger.info(
        "agent_pattern_retrieval.selected pattern_count=%d pattern_types=%s",
        len(patterns),
        pattern_types,
    )
    return format_chunks_for_prompt(patterns), pattern_types


MAXIMUM_ROUNDS = 2

#: Was der Kunde bei einem gescheiterten Lauf liest. Als Konstante, weil
#: derselbe Text an zwei Stellen gebraucht wird: in der Antwort des Laufs
#: und später aus dem Vermerk an der Sitzung.
MELDUNG_LAUF = "Das hat gerade nicht geklappt. Bitte versuchen Sie es noch einmal."
MELDUNG_UNVOLLSTAENDIG = (
    "Die Auswertung konnte nicht vollständig erstellt werden. "
    "Es wurde nichts halb Fertiges übernommen."
)
"""Wie oft der erste Aufruf höchstens läuft.

Hart begrenzt, damit ein Gespräch nicht endlos wird — und weil jede Runde
einen Modellaufruf kostet. Nach der zweiten geht es immer weiter zum Ergebnis,
auch wenn das Modell noch etwas wissen möchte.
"""


def vorgeschlagene_familien(diagnose: Diagnose) -> list[str]:
    """Welche Familien der Abruf zur Diagnose für passend hält.

    **Ein Vorschlag, keine Vorauswahl.** Wählbar ist der ganze
    freigegebene Katalog; hier steht nur, was der Abruf für am ehesten
    passend hält. Damit kann ein schlechter Treffer die richtige Familie
    nicht mehr unerreichbar machen — vorher entschied allein das
    erstplatzierte Diagnosemuster, was überhaupt zur Wahl stand.

    Gesucht wird mit dem Engpass-Satz und dem Diagnoseabsatz, nicht mit
    der ganzen Erzählung. Gemessen: Der Engpass-Satz spreizt die
    Trefferliste mehr als doppelt so weit wie die rohe Erzählung, weil er
    in der Sprache der Muster geschrieben ist.

    **Diese Sicht allein reicht nicht.** In drei Messläufen über denselben
    Text fand dieser Abruf dreimal etwas anderes, während der Abruf über
    die Erzählung dreimal dasselbe fand. Schärfer heisst nicht
    zuverlässiger. Deshalb geht er zusammen mit `familien_aus_erzaehlung`
    an den Planner — als zweite Sicht, nicht als Ersatz.
    """

    suchtext = f"{diagnose.engpass_satz} {diagnose.verstanden.engpass_absatz}"
    return _abgerufene_familien(suchtext)


def familien_aus_erzaehlung(narrative_text: str) -> list[str]:
    """Was der Abruf über die **ganze Erzählung** für passend hält.

    Die breite Sicht: Sie kennt auch, was neben dem einen diagnostizierten
    Engpass liegt — Statusfragen, Kapazität, Portale.

    **Gemessen, warum es sie braucht.** Dreimal derselbe Heizungsfall: Der
    Abruf über die Erzählung schlug jedes Mal dieselben sechs Familien vor,
    der Abruf über die Diagnose jedes Mal andere. Zwei davon — Portal und
    Kapazität — wurden dabei jedes Mal gefunden und kein einziges Mal
    gewählt, weil sie in der verdichteten Diagnose nicht mehr vorkamen.
    """

    return _abgerufene_familien(narrative_text)


def _abgerufene_familien(suchtext: str) -> list[str]:
    """Die Kennungen, die ein Abruf für passend hält — oder nichts.

    Beide Sichten kommen mit: die des Fokus und die der Breitensuche. Sie
    sind Vorschläge, keine Auswahl — der ganze freigegebene Katalog
    bleibt dem Planner ohnehin offen.
    """

    try:
        gefunden = retrieve_solution_context(suchtext)
    except (AIServiceError, RagConfigurationError):
        logger.warning("solution_architecture.retrieval_failed")
        return []
    kennungen = [familie.chunk_id for familie in gefunden.loesungsfamilien]
    for familie in gefunden.breite_familien:
        if familie.chunk_id not in kennungen:
            kennungen.append(familie.chunk_id)
    return kennungen


def diagnose_context(narrative_text: str) -> list[str]:
    """Vergleichswissen für die **Diagnose** — Betriebsarten und Muster.

    **Ohne Lösungswissen.** Familien, Fähigkeiten und Zielbild dürfen dem
    Diagnoseaufruf nicht vorliegen: Wer die Lösung kennt, diagnostiziert
    auf sie hin —
    und aus „der Kunde erwähnt Termine" wird „wir verkaufen
    Terminbuchung".

    Ein Muster ist Vergleichsmaterial, nie ein Beleg über diesen Betrieb.
    Was über ihn gesagt wird, steht in seiner Erzählung.

    Leer, solange kein Batch indexiert ist — der Prompt muss auch ohne
    dieses Wissen vollständig funktionieren. Ein Abruf, der scheitert,
    darf den Lauf nicht mitreissen.
    """

    try:
        gefunden = retrieve_solution_context(narrative_text)
    except (AIServiceError, RagConfigurationError):
        logger.warning("solution_architecture.retrieval_failed")
        return []
    abschnitte = [*gefunden.betriebsarten, *gefunden.diagnosemuster]
    return format_chunks_for_prompt(abschnitte) if abschnitte else []


def run_first_call(session_id: int, database_session: Session) -> Diagnose:
    """Schreibt die **Diagnose** und legt sie als Zwischenstand ab.

    Läuft ein zweites Mal, wenn der Kunde auf der Verstandenseite etwas
    ergänzt hat — dann mit der erweiterten Erzählung.

    Hier entsteht keine Lösung mehr. Was empfohlen wird, wird im zweiten
    Aufruf aus dem freigegebenen Katalog **ausgewählt** und serverseitig
    geprüft.
    """

    zwischenstand = repository.get_partial_result(database_session, session_id)
    erzaehlung = (
        zwischenstand.narrative
        if zwischenstand is not None
        else narrative_from_session(database_session, session_id)
    )
    runde = (zwischenstand.rounds if zwischenstand is not None else 0) + 1

    begonnen = perf_counter()
    diagnose = generate_diagnosis(
        narrative_text=erzaehlung,
        # Nur Betriebsarten und Diagnosemuster. Lösungswissen kommt erst
        # nach der Diagnose, und dann als Katalogauswahl.
        knowledge_chunks=diagnose_context(erzaehlung),
    )
    repository.save_partial_result(
        database_session,
        session_id,
        payload=diagnose.model_dump(mode="json"),
        narrative=erzaehlung,
        rounds=runde,
        moving_on=False,
    )
    database_session.commit()
    logger.info(
        "understanding.written session=%s runde=%d rueckfrage=%s seconds=%.1f",
        session_id,
        runde,
        diagnose.rueckfrage is not None,
        perf_counter() - begonnen,
    )
    return diagnose


def geprueftes_loesungswissen(gewaehlt: Zielarchitektur) -> dict[str, object]:
    """Lädt die vollständigen Datensätze der **ausgewählten** Familien.

    Erst prüfen, dann laden: Was hier herauskommt, geht in die
    Formulierung, und was in die Formulierung geht, darf beim Kunden
    landen. Familien, die nicht gewählt wurden, kommen hier nicht mehr
    vor — auch nicht als Hintergrundwissen.

    Das Zielbildmuster wird **hier** bestimmt, nach der Prüfung. Vorher
    hing es am Vorschlag des Abrufs, also an einer Auswahl, die noch
    niemand getroffen hatte. Passt keines, bleibt es leer — ein Muster
    wird nicht erzwungen.
    """

    kennungen = list(gewaehlt.selected_solution_family_ids)
    if not kennungen:
        # Kein Katalogtreffer oder keine neue Technik nötig: Dann gibt es
        # nichts zu hydratisieren, und die Formulierung bekommt nichts.
        return {
            "GEWAEHLTE_LOESUNGSFAMILIEN": [],
            "GEBRAUCHTE_FAEHIGKEITEN": [],
            "ZIELBILDMUSTER": {},
        }
    zielbild = solution_catalog.zielbild_zu(kennungen)
    kontext: dict[str, object] = {
        "GEWAEHLTE_LOESUNGSFAMILIEN": solution_catalog.vollstaendig(kennungen),
        "GEBRAUCHTE_FAEHIGKEITEN": solution_catalog.faehigkeiten_zu(kennungen),
        "ZIELBILDMUSTER": zielbild or {},
    }
    logger.info(
        "solution.hydrated familien=%d faehigkeiten=%d zielbild=%s",
        len(kontext["GEWAEHLTE_LOESUNGSFAMILIEN"]),
        len(kontext["GEBRAUCHTE_FAEHIGKEITEN"]),
        (zielbild or {}).get("chunk_id", "keines"),
    )
    return kontext


def zusammengesetzt(diagnose: Diagnose, gewaehlt: Zielarchitektur) -> ResultPartOne:
    """Fügt Diagnose und geprüfte Auswahl zu dem zusammen, was die Seite zeigt.

    Der Vertrag nach aussen bleibt unberührt: `ResultPartOne` behält seine
    Felder, Vorlagen und gespeicherte Läufe merken nichts davon. Anders ist
    nur, **woher** die Lösungsseite kommt.
    """

    return ResultPartOne.model_validate(
        {
            "kurzfassung": {
                "engpass_satz": diagnose.engpass_satz,
                "loesungsname": gewaehlt.loesungsname,
                "relevante_module": gewaehlt.relevante_module,
            },
            "verstanden": diagnose.verstanden.model_dump(),
            "warum_diese_loesung": gewaehlt.warum_diese_loesung,
            "zielbild": gewaehlt.zielbild.model_dump(),
            "vergleich": {
                "heute": diagnose.vergleich_heute,
                "kuenftig": gewaehlt.vergleich_kuenftig,
            },
            "module": [modul.model_dump() for modul in gewaehlt.module],
            # Der Ausbaupfad steht neben den Modulen, nicht in ihnen: Die
            # Module sind die Lösung, der Pfad ist das, was danach möglich
            # wird.
            "ausbaupfad": [
                schritt.model_dump() for schritt in gewaehlt.ausbaupfad
            ],
            "rueckfrage": (
                diagnose.rueckfrage.model_dump()
                if diagnose.rueckfrage is not None
                else None
            ),
        }
    )


def run_second_call(session_id: int, database_session: Session) -> Result:
    """Schreibt den unteren Teil und speichert das fertige Ergebnis.

    Nimmt den oberen Teil aus dem Zwischenstand, nicht aus einem neuen Aufruf:
    Die Seite soll dasselbe zeigen, was der Kunde eben gesehen hat.
    """

    zwischenstand = repository.get_partial_result(database_session, session_id)
    if zwischenstand is None or zwischenstand.payload is None:
        raise ValueError("Der obere Teil fehlt noch.")

    erzaehlung = zwischenstand.narrative
    begonnen = perf_counter()
    with narrative(erzaehlung):
        diagnose = Diagnose.model_validate(zwischenstand.payload)

    # **Auswählen statt erfinden.** Der Abruf schlägt vor, das Modell wählt
    # Kennungen, der Vertrag prüft sie gegen den freigegebenen Katalog.
    # **Beide Abrufsichten.** Die Erzählung liefert den breiten Raum, die
    # Diagnose den Fokus auf den Engpass. Keine ersetzt die andere.
    aus_erzaehlung = familien_aus_erzaehlung(erzaehlung)
    aus_diagnose = vorgeschlagene_familien(diagnose)
    logger.info(
        "solution_architecture.zwei_sichten erzaehlung=%s diagnose=%s nur_erzaehlung=%s",
        aus_erzaehlung,
        aus_diagnose,
        [k for k in aus_erzaehlung if k not in aus_diagnose],
    )
    gewaehlt = generate_target_architecture(
        narrative_text=erzaehlung,
        diagnose=diagnose,
        vorgeschlagene_familien=aus_diagnose,
        familien_aus_erzaehlung=aus_erzaehlung,
    )
    # Im Erzählkontext: Das Zusammensetzen prüft die Zitate erneut, und
    # ohne den Text lässt sich das nicht prüfen.
    with narrative(erzaehlung):
        part_one = zusammengesetzt(diagnose, gewaehlt)
    # Erst jetzt, nach der Prüfung: die vollen Datensätze, die
    # gebrauchten Fähigkeiten und das passende Zielbildmuster.
    part_two = generate_result_part_two(
        narrative_text=erzaehlung,
        part_one=part_one,
        knowledge_chunks=[],
        loesungswissen=geprueftes_loesungswissen(gewaehlt),
    )
    with narrative(erzaehlung):
        ergebnis = Result.model_validate(
            {**part_one.model_dump(), **part_two.model_dump()}
        )
    gespeichert = repository.save_result(
        database_session,
        session_id,
        payload=ergebnis.model_dump(mode="json"),
        narrative=erzaehlung,
    )
    database_session.commit()
    logger.info(
        "result.generated session=%s runden=%d teil2_seconds=%.1f openai_calls=%s",
        session_id,
        zwischenstand.rounds,
        perf_counter() - begonnen,
        counted_calls_for_logging(),
    )
    return gespeichert


def stored_part_one(
    database_session: Session, session_id: int
) -> Diagnose | None:
    """Die abgelegte Diagnose, erneut gegen den Vertrag geprüft."""

    zwischenstand = repository.get_partial_result(database_session, session_id)
    if zwischenstand is None or zwischenstand.payload is None:
        return None
    with narrative(zwischenstand.narrative):
        return Diagnose.model_validate(zwischenstand.payload)


def follow_up_is_offered(database_session: Session, session_id: int) -> bool:
    """Ob dem Kunden jetzt noch eine Rückfrage gezeigt werden darf.

    In der letzten Runde nicht mehr — auch dann nicht, wenn das Modell wieder
    eine geliefert hat. Sonst hinge der Kunde in einer Schleife, die nur der
    Agent beendet.
    """

    zwischenstand = repository.get_partial_result(database_session, session_id)
    return zwischenstand is not None and zwischenstand.rounds < MAXIMUM_ROUNDS


def add_to_the_narrative(
    database_session: Session, session_id: int, addition: str
) -> None:
    """Hängt die Antwort des Kunden an die Erzählung und fordert Aufruf 1 neu an.

    Deutlich getrennt, damit im Prompt erkennbar bleibt, was nachgereicht
    wurde. `payload` wird geleert — das ist das Zeichen, dass der obere Teil
    noch einmal geschrieben werden muss.
    """

    zwischenstand = repository.get_partial_result(database_session, session_id)
    if zwischenstand is None:
        return
    getrennt = "\n\nAuf Nachfrage ergänzt: " + addition.strip()
    repository.save_partial_result(
        database_session,
        session_id,
        payload=None,
        narrative=zwischenstand.narrative + getrennt,
        rounds=zwischenstand.rounds,
        moving_on=False,
    )
    database_session.commit()
    logger.info(
        "understanding.extended session=%s zeichen=%d", session_id, len(addition)
    )


def move_on(database_session: Session, session_id: int) -> None:
    """Merkt, dass der Kunde weitergegangen ist — der zweite Aufruf darf laufen."""

    zwischenstand = repository.get_partial_result(database_session, session_id)
    if zwischenstand is None:
        return
    zwischenstand.moving_on = True
    database_session.commit()


def stored_result(
    database_session: Session,
    session_id: int,
) -> Result | None:
    """Das gespeicherte Ergebnis, erneut gegen den Vertrag geprüft.

    Die Prüfung beim Lesen kostet fast nichts und stellt sicher, dass die Seite
    nur anzeigt, was auch durch den Erzeugungspfad gekommen wäre — etwa nachdem
    sich der Vertrag geändert hat.
    """

    gespeichert = repository.get_result(database_session, session_id)
    if gespeichert is None:
        return None
    with narrative(gespeichert.narrative):
        return Result.model_validate(gespeichert.payload)


def stand_der_auswertung(
    session_id: int,
    database_session: Session,
) -> tuple[dict[str, object], int]:
    """Wo die Auswertung steht — **ohne zu rechnen**.

    Seit die Analyse im Worker läuft, muss die Route sagen können, wohin es
    geht, ohne selbst etwas anzustossen. Genau dieselben Wegweiser wie in
    `run_generation`, nur ohne den teuren Teil dazwischen.

    Der Warteschirm fragt danach weiter über `/analysis-status`; diese
    Antwort ist die erste, unmittelbar nach dem Einstellen des Auftrags.
    """

    from app.services.process_service import next_valid_path

    if repository.get_result(database_session, session_id) is not None:
        return (
            {"state": "complete", "redirect_url": f"/sessions/{session_id}/results"},
            status.HTTP_200_OK,
        )

    # **Ein gescheiterter Lauf meldet sich hier.** Im Sofortmodus ist der
    # Vermerk schon da, wenn diese Zeile läuft; im Betrieb setzt ihn der
    # Worker, und der Warteschirm liest ihn über `/analysis-status`.
    sitzung = repository.get_session(database_session, session_id)
    if sitzung is not None and sitzung.lauf_fehler:
        return (
            {
                "state": "error",
                "message": sitzung.lauf_fehler,
                "redirect_url": None,
            },
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    zwischenstand = repository.get_partial_result(database_session, session_id)
    if zwischenstand is not None and zwischenstand.payload and not zwischenstand.moving_on:
        # Der obere Teil steht, der Kunde ist noch nicht weitergegangen.
        return (
            {
                "state": "complete",
                "redirect_url": f"/sessions/{session_id}/verstanden",
            },
            status.HTTP_200_OK,
        )

    naechster = next_valid_path(database_session, session_id)
    if naechster == f"/sessions/{session_id}/interview":
        return (
            {
                "state": "error",
                "message": "Bitte beschreiben Sie zuerst, wie Ihr Betrieb läuft.",
                "redirect_url": naechster,
            },
            status.HTTP_409_CONFLICT,
        )

    # Der Auftrag liegt in der Warteschlange oder wird gerade bearbeitet.
    return {"state": "processing", "redirect_url": None}, status.HTTP_200_OK


def run_generation(
    session_id: int,
    database_session: Session,
) -> tuple[dict[str, object], int]:
    """Bringt den Durchlauf einen Schritt weiter und sagt, wohin es geht.

    Der Warteschirm ruft diese Adresse und wird zweimal durchlaufen: einmal
    vor der Verstandenseite, einmal danach. Welcher Schritt ansteht, ergibt
    sich aus dem Zwischenstand — die Route entscheidet nichts.

    Ein zweiter Aufruf, während der erste noch läuft, bekommt „processing" und
    erzeugt nichts: Sonst liefen zwei Modellläufe für dieselbe Sitzung.
    """

    # Hier lokal importiert: der Prozessdienst braucht diesen Dienst schon beim
    # Laden, ein Import auf Modulebene wäre ein Kreis.
    from app.services.process_service import next_valid_path

    reset_openai_call_count()
    results_path = f"/sessions/{session_id}/results"
    understanding_path = f"/sessions/{session_id}/verstanden"
    if repository.get_result(database_session, session_id) is not None:
        return {"state": "complete", "redirect_url": results_path}, status.HTTP_200_OK
    next_path = next_valid_path(database_session, session_id)
    if next_path == f"/sessions/{session_id}/interview":
        database_session.rollback()
        return (
            {
                "state": "error",
                "message": "Bitte erzähl uns zuerst, was dich im Alltag beschäftigt.",
                "redirect_url": next_path,
            },
            status.HTTP_409_CONFLICT,
        )
    # Ein neuer Versuch löscht den alten Vermerk: Sonst zeigt der
    # Warteschirm sofort wieder den Fehler von vorhin.
    repository.merke_lauf_fehler(database_session, session_id, None)
    if not repository.acquire_session_write_lock(database_session, session_id):
        database_session.rollback()
        return (
            {"state": "processing", "redirect_url": None},
            status.HTTP_409_CONFLICT,
        )
    if repository.get_result(database_session, session_id) is not None:
        database_session.rollback()
        return {"state": "complete", "redirect_url": results_path}, status.HTTP_200_OK

    zwischenstand = repository.get_partial_result(database_session, session_id)
    try:
        if zwischenstand is None or zwischenstand.payload is None:
            run_first_call(session_id, database_session)
            return (
                {"state": "complete", "redirect_url": understanding_path},
                status.HTTP_200_OK,
            )
        if not zwischenstand.moving_on:
            # Der Kunde steht noch auf der Verstandenseite. Nichts zu tun.
            database_session.rollback()
            return (
                {"state": "complete", "redirect_url": understanding_path},
                status.HTTP_200_OK,
            )
        run_second_call(session_id, database_session)
    except (AIServiceError, ValidationError, ValueError) as error:
        database_session.rollback()
        logger.exception(
            "result.failed session=%s exception_type=%s exception_message=%s",
            session_id,
            type(error).__name__,
            str(error),
        )
        # **Der Vermerk überlebt den Worker.** Seit die Analyse dort läuft,
        # ist die Antwort auf `POST /analyze` längst weg, wenn etwas
        # schiefgeht — ohne diesen Eintrag fragt der Warteschirm neunzig Mal
        # nach und meldet eine Zeitüberschreitung statt des Grundes.
        repository.merke_lauf_fehler(database_session, session_id, MELDUNG_LAUF)
        return (
            {
                "state": "error",
                "message": MELDUNG_LAUF,
                "redirect_url": None,
            },
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception as error:
        database_session.rollback()
        logger.exception(
            "result.failed session=%s exception_type=%s exception_message=%s",
            session_id,
            type(error).__name__,
            str(error),
        )
        repository.merke_lauf_fehler(database_session, session_id, MELDUNG_UNVOLLSTAENDIG)
        return (
            {
                "state": "error",
                "message": MELDUNG_UNVOLLSTAENDIG,
                "redirect_url": None,
            },
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return {"state": "complete", "redirect_url": results_path}, status.HTTP_200_OK


def narrative_from_session(database_session: Session, session_id: int) -> str:
    from app.services.interview_service import narrative_text

    return narrative_text(
        repository.get_questions(database_session, session_id, phase="context")
    )
