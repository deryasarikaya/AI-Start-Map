"""Die Adressen der Anwendung.

In dieser Datei steht ausschließlich, welche Adresse zu welcher Funktion
gehört. Jede Funktion nimmt die Eingabe entgegen, ruft einen Dienst und gibt
eine Seite oder eine Weiterleitung zurück — gerechnet und entschieden wird
woanders:

- `app/services/` — die Ablauflogik
- `app/repository.py` — alle Datenbankzugriffe
- `app/web/` — Sitzung, Weiterleitungen, Vorlagen

Am Ende der Datei steht `PUBLIC_ROUTES`. Die Anwendung ist unter zwei Adressen
erreichbar: mit Sitzungsnummer im Pfad (`/sessions/12/interview`) und ohne
(`/interview`). Ohne Nummer wird die Sitzung aus dem Cookie gelesen. Die
Tabelle erzeugt die zweite Form aus der ersten, damit jede Route nur einmal
geschrieben werden muss.
"""

import json
import logging
import re
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

from app import repository
from app.database import get_db_session
from app.models import AnalysisSession, InterviewQuestion
from app.questions import INTRO_KEYS, INTRO_QUESTIONS
from app.rag_service import RagConfigurationError
from app.services import analysis_service, example_service
from app.services.example_service import ExampleNotFound
from app.services.demo_service import (
    DEMO_EVALUATION_IDS,
    create_demo_session,
    load_evaluation_case,
)
from app.services.process_service import next_valid_path
from app.web.responses import redirect_response, render_error, templates
from app.web.session import (
    publicize_redirect,
    register_public_route,
    session_id_from_cookie,
    set_session_cookie,
)


router = APIRouter()
logger = logging.getLogger(__name__)



@router.get("/", response_class=HTMLResponse, name="landing")
def show_landing(request: Request) -> HTMLResponse:
    """Zeigt die Startseite.

    Der Knopf darauf schickt an POST /begin, wo die Sitzung angelegt wird.
    """

    return templates.TemplateResponse(request=request, name="landing.html")


@router.post("/start", name="start_session")
def start_session(database_session: Session = Depends(get_db_session)) -> RedirectResponse:
    """Legt eine neue Sitzung mit den Einstiegsfragen an.

    Aufgerufen wird sie von `begin_journey`. Die Adresse POST /start selbst
    ruft im Betrieb nichts auf — nur die Tests benutzen sie direkt.
    """

    analysis_session = AnalysisSession()
    try:
        database_session.add(analysis_session)
        database_session.flush()
        database_session.add_all(
            [
                InterviewQuestion(
                    session_id=analysis_session.session_id,
                    question_phase=question["phase"],
                    question_order=question["order"],
                    question_key=question["key"],
                    question_text=question["text"],
                )
                for question in INTRO_QUESTIONS
            ]
        )
        database_session.commit()
    except Exception:
        database_session.rollback()
        raise
    return redirect_response(f"/sessions/{analysis_session.session_id}/interview")


@router.post("/begin", name="begin_journey")
def begin_journey(
    request: Request,
    database_session: Session = Depends(get_db_session),
) -> Response:
    """Startet den Ablauf für einen neuen Kunden.

    Legt über `start_session` die Sitzung an, merkt sich ihre Nummer im
    Cookie des Browsers und schickt den Kunden ins Erzählfeld. Ab hier
    steht die Sitzungsnummer in keiner Adresse mehr.
    """

    response = start_session(database_session)
    session_id = int(response.headers["location"].split("/")[2])
    public_response = redirect_response("/interview")
    set_session_cookie(public_response, request, session_id)
    return public_response


@router.get(
    "/sessions/{session_id}/interview",
    response_class=HTMLResponse,
    name="show_interview",
)
def show_interview(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    """Zeigt das Feld, in dem der Kunde von seinem Betrieb erzählt.

    Gibt es für diese Sitzung schon ein fertiges Ergebnis, wird stattdessen
    das gezeigt. Eine abgeschlossene Auswertung wird nicht überschrieben.
    """

    repository.get_session_or_404(database_session, session_id)
    if repository.get_result(database_session, session_id) is not None:
        return redirect_response(f"/sessions/{session_id}/results")
    questions = repository.get_questions(database_session, session_id, phase="context")
    return templates.TemplateResponse(
        request=request,
        name="interview_start.html",
        context={
            "session_id": session_id,
            "questions": questions,
            "answers": {
                question.question_key: question.answer_text or ""
                for question in questions
            },
            "error_message": None,
        },
    )


@router.post(
    "/sessions/{session_id}/interview",
    response_class=HTMLResponse,
    name="save_interview",
)
async def save_interview(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    """Speichert die Erzählung des Kunden.

    Der Text kommt entweder aus dem großen Textfeld oder aus der
    Spracherkennung im Browser. Ist nichts eingetragen, wird dieselbe Seite
    noch einmal mit einem Hinweis gezeigt. Sonst geht es direkt zum
    Warteschirm, auf dem die Auswertung entsteht.
    """

    repository.get_session_or_404(database_session, session_id)
    if repository.get_result(database_session, session_id) is not None:
        return redirect_response(f"/sessions/{session_id}/results")
    if not repository.acquire_session_write_lock(database_session, session_id):
        database_session.rollback()
        return redirect_response(f"/sessions/{session_id}/processing")
    questions = repository.get_questions(database_session, session_id, phase="context")
    form = await request.form()
    free_description = str(form.get("free_description", "")).strip()
    submitted = (
        {key: free_description for key in INTRO_KEYS}
        if free_description
        else {key: str(form.get(key, "")).strip() for key in INTRO_KEYS}
    )
    if not all(submitted.values()):
        return templates.TemplateResponse(
            request=request,
            name="interview_start.html",
            context={
                "session_id": session_id,
                "questions": questions,
                "answers": submitted,
                "error_message": "Bitte erzähl uns kurz, was dich im Alltag beschäftigt.",
            },
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    for question in questions:
        question.answer_text = submitted[question.question_key]
    try:
        database_session.commit()
    except Exception:
        database_session.rollback()
        raise
    return redirect_response(f"/sessions/{session_id}/processing")


@router.get(
    "/sessions/{session_id}/processing",
    response_class=HTMLResponse,
    name="show_processing",
)
def show_processing(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    """Zeigt den Warteschirm, während die Auswertung entsteht.

    Die Seite startet die Auswertung per Skript und fragt danach im
    Sekundentakt nach, ob sie fertig ist. Geht etwas schief, erscheint der
    Fehler auf dieser Seite mit einer Schaltfläche zum Wiederholen.
    """

    repository.get_session_or_404(database_session, session_id)
    if repository.get_result(database_session, session_id) is not None:
        return redirect_response(f"/sessions/{session_id}/results")
    next_path = next_valid_path(database_session, session_id)
    if next_path != f"/sessions/{session_id}/processing":
        return redirect_response(next_path)
    return templates.TemplateResponse(
        request=request,
        name="processing.html",
        context={"session_id": session_id},
    )


@router.get(
    "/sessions/{session_id}/analysis-status",
    name="analysis_status",
)
def analysis_status(
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> JSONResponse:
    """Sagt dem wartenden Browser, ob die Auswertung fertig ist.

    Diese Adresse ruft kein Mensch auf, sondern das Skript auf dem
    Warteschirm. Die Antwort ist JSON, keine Seite. Steht dort „complete",
    leitet der Browser selbst zum Ergebnis weiter.
    """

    repository.get_session_or_404(database_session, session_id)
    complete = repository.get_result(database_session, session_id) is not None
    return JSONResponse(
        {
            "state": "complete" if complete else "pending",
            "redirect_url": (
                f"/sessions/{session_id}/results" if complete else None
            ),
        }
    )


@router.post("/sessions/{session_id}/analyze", name="analyze_session")
def analyze_session(
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> JSONResponse:
    """Startet die Auswertung und meldet, wie sie ausgegangen ist.

    Aufgerufen vom Skript auf dem Warteschirm. Gerechnet wird in
    `analysis_service.run_generation` — zwei Modellaufrufe aus der Erzählung.
    Die Antwort ist JSON und sagt, ob es geklappt hat; bei einem Fehler zeigt
    der Warteschirm ihn an.
    """

    repository.get_session_or_404(database_session, session_id)
    payload, status_code = analysis_service.run_generation(session_id, database_session)
    return JSONResponse(payload, status_code=status_code)


@router.get(
    "/sessions/{session_id}/verstanden",
    response_class=HTMLResponse,
    name="show_understanding",
)
def show_understanding(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    """Zeigt, was aus der Erzählung verstanden wurde — und fragt höchstens einmal.

    Steht der Zwischenstand noch nicht, geht es zurück auf den Warteschirm.
    """

    repository.get_session_or_404(database_session, session_id)
    part_one = analysis_service.stored_part_one(database_session, session_id)
    if part_one is None:
        return redirect_response(next_valid_path(database_session, session_id))
    darf_fragen = analysis_service.follow_up_is_offered(database_session, session_id)
    return templates.TemplateResponse(
        request=request,
        name="verstanden.html",
        context={
            "e": part_one,
            "rueckfrage": part_one.rueckfrage if darf_fragen else None,
            "letzte_runde": not darf_fragen,
        },
    )


@router.post(
    "/sessions/{session_id}/verstanden",
    response_class=HTMLResponse,
    name="save_understanding",
)
async def save_understanding(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    """Nimmt die Antwort des Kunden entgegen — oder sein Weitergehen.

    Ergänzt er etwas, läuft der erste Aufruf mit der erweiterten Erzählung
    erneut; das entscheidet der Warteschirm. Geht er weiter, folgt der zweite
    Aufruf. In der letzten Runde wird eine Ergänzung nicht mehr angenommen,
    damit aus zwei Runden keine dritte wird.
    """

    repository.get_session_or_404(database_session, session_id)
    if repository.get_result(database_session, session_id) is not None:
        return redirect_response(f"/sessions/{session_id}/results")
    form = await request.form()
    antwort = str(form.get("antwort", "")).strip()
    geht_weiter = str(form.get("weiter", "")) == "ja"
    darf_fragen = analysis_service.follow_up_is_offered(database_session, session_id)
    if antwort and not geht_weiter and darf_fragen:
        analysis_service.add_to_the_narrative(database_session, session_id, antwort)
    else:
        analysis_service.move_on(database_session, session_id)
    return redirect_response(f"/sessions/{session_id}/processing")


@router.get(
    "/sessions/{session_id}/results",
    response_class=HTMLResponse,
    name="show_results",
)
def show_results(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    """Zeigt das fertige Ergebnis.

    Liegt keins vor, geht es zurück an die Stelle, an der der Kunde
    tatsächlich steht. Was vorliegt, ist bereits beim Lesen gegen den Vertrag
    geprüft — er verbietet Fachsprache, erfundene Zahlen und Zitate, die so
    nicht in der Erzählung stehen. Eine zweite Prüfung hier wäre dieselbe
    Prüfung zweimal.
    """

    repository.get_session_or_404(database_session, session_id)
    ergebnis = analysis_service.stored_result(database_session, session_id)
    if ergebnis is None:
        return redirect_response(next_valid_path(database_session, session_id))
    return templates.TemplateResponse(
        request=request,
        name="ergebnis.html",
        context={"session_id": session_id, "e": ergebnis},
    )


@router.get(
    "/sessions/{session_id}/report",
    response_class=HTMLResponse,
    name="show_report",
)
def show_report(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    """Zeigt die vollständige Auswertung zum Ausdrucken.

    Aufgerufen über „Vollständige Auswertung als PDF" auf der Ergebnisseite;
    gedruckt wird im Browser. Dieselben Daten wie die Ergebnisseite, nur alle
    elf Abschnitte statt vier — es wird nichts nachgeladen und nichts neu
    gerechnet.

    Mit `?drucken=1` öffnet die Seite den Druckdialog von selbst; das ist
    der Weg vom Knopf. Ohne den Zusatz bleibt sie eine Seite zum Lesen.
    """

    repository.get_session_or_404(database_session, session_id)
    ergebnis = analysis_service.stored_result(database_session, session_id)
    if ergebnis is None:
        return redirect_response(next_valid_path(database_session, session_id))
    return templates.TemplateResponse(
        request=request,
        name="report.html",
        context={
            "e": ergebnis,
            "auswertungsdatum": date.today().strftime("%d.%m.%Y"),
            "sofort_drucken": request.query_params.get("drucken") == "1",
        },
    )


@router.get("/analysis-status", name="analysis_status_public")
def analysis_status_public(request: Request, database_session: Session = Depends(get_db_session)) -> JSONResponse:
    """Die öffentliche Variante der Statusabfrage.

    Sie steht ausgeschrieben da, weil die Antwort JSON ist: Die Sitzungsnummer
    muss aus der `redirect_url` im Antwortinhalt heraus, nicht aus einem
    Weiterleitungskopf."""

    session_id = session_id_from_cookie(request)
    response = analysis_status(session_id, database_session)
    payload = json.loads(response.body)
    if payload.get("redirect_url"):
        payload["redirect_url"] = "/results"
    return JSONResponse(payload, status_code=response.status_code)


@router.post("/analyze", name="analyze_session_public")
def analyze_session_public(request: Request, database_session: Session = Depends(get_db_session)) -> JSONResponse:
    """Die öffentliche Variante des Analysestarts.

    Wie `analysis_status_public`: Die Adresse im JSON-Inhalt wird umgeschrieben,
    damit die Sitzungsnummer nicht im Browser landet."""

    session_id = session_id_from_cookie(request)
    response = analyze_session(session_id, database_session)
    payload = json.loads(response.body)
    if payload.get("redirect_url"):
        payload["redirect_url"] = publicize_redirect(redirect_response(payload["redirect_url"]), session_id).headers["location"]
    return JSONResponse(payload, status_code=response.status_code)


@router.get(
    "/beispiel/{example_slug}",
    response_class=HTMLResponse,
    name="show_example",
)
def show_example(
    request: Request,
    example_slug: str,
    database_session: Session = Depends(get_db_session),
) -> Response:
    """Zeigt einen hinterlegten Beispiellauf ohne Modellaufruf.

    Die Rückfallebene für eine Vorführung. Die Seite ist als Beispiel
    gekennzeichnet, und es führt kein Weg aus dem Kundenablauf hierher — wer
    sie sehen will, gibt die Adresse ein.
    """

    try:
        ergebnis = example_service.example_result(database_session, example_slug)
    except ExampleNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None
    return templates.TemplateResponse(
        request=request,
        name="ergebnis.html",
        context={"e": ergebnis, "beispiel": True},
    )


@router.get("/demo/{demo_slug}", name="run_demo")
def run_demo(
    request: Request,
    demo_slug: str,
    database_session: Session = Depends(get_db_session),
) -> Response:
    """Legt aus einem gespeicherten Evaluationsfall eine fertige Sitzung an.

    Für Vorführungen gedacht und nur über einen von Hand eingegebenen Link
    erreichbar. Die Sitzung ist sofort vollständig, die Analyse startet
    direkt. Welche Fälle es gibt, steht in
    `demo_service.DEMO_EVALUATION_IDS`.
    """

    evaluation_id = DEMO_EVALUATION_IDS.get(demo_slug)
    if evaluation_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    try:
        evaluation_case = load_evaluation_case(evaluation_id)
        session_id = create_demo_session(database_session, evaluation_case)
    except RagConfigurationError as error:
        database_session.rollback()
        return render_error(
            request,
            str(error),
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    except Exception:
        database_session.rollback()
        raise
    response = redirect_response("/processing")
    set_session_cookie(response, request, session_id)
    return response


# Die Anwendung ist unter zwei Adressen erreichbar. Mit Sitzungsnummer im Pfad
# (/sessions/12/interview) und ohne (/interview). Ohne Nummer wird die Sitzung
# aus dem Cookie im Browser gelesen. Beide führen dieselbe Funktion aus - die
# Tabelle sagt nur, welche Adresse zu welcher Funktion gehört.
PUBLIC_ROUTES = (
    ("GET", "/interview", "show_interview_public", show_interview, HTMLResponse),
    # Der Kunde erzählt von seinem Betrieb
    ("POST", "/interview", "save_interview_public", save_interview, HTMLResponse),
    # Speichert das Erzählte
    ("GET", "/verstanden", "show_understanding_public", show_understanding, HTMLResponse),
    # Was aus der Erzählung verstanden wurde
    ("POST", "/verstanden", "save_understanding_public", save_understanding, HTMLResponse),
    # Die Antwort darauf, oder das Weitergehen
    ("GET", "/processing", "show_processing_public", show_processing, HTMLResponse),
    # Warteschirm, während die Auswertung entsteht
    ("GET", "/results", "show_results_public", show_results, HTMLResponse),
    # Das fertige Ergebnis
    ("GET", "/report", "show_report_public", show_report, HTMLResponse),
    # Die Druckansicht
)

for _method, _path, _name, _session_route, _response_class in PUBLIC_ROUTES:
    register_public_route(
        router,
        method=_method,
        path=_path,
        name=_name,
        session_route=_session_route,
        response_class=_response_class,
    )
