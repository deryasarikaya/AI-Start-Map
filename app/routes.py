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
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, Response
from sqlalchemy.orm import Session

from app import bericht_pdf, repository, results_dto
from app.hintergrund import auswertung_erzeugen
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


def start_session(database_session: Session) -> int:
    """Legt eine neue Sitzung mit den Einstiegsfragen an und gibt ihre Nummer.

    **Keine Route mehr.** Unter `POST /start` stand hier einmal eine eigene
    Adresse, die im Betrieb niemand aufrief — kein Formular, kein Link,
    keine Weiterleitung. Am Leben hielten sie nur ihre eigenen Tests. Die
    gehen jetzt über `/begin`, also über den Weg, den es wirklich gibt.

    Ohne Route gibt sie auch keine Weiterleitung mehr zurück: `begin_journey`
    musste die Sitzungsnummer vorher aus der Adresse in `location` wieder
    herausschneiden, um sie ins Cookie zu legen. Die Nummer direkt.
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
    return analysis_session.session_id


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

    session_id = start_session(database_session)
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
                "error_message": (
                    "Bitte beschreiben Sie, wie Ihr Betrieb heute läuft. "
                    "Sie können frei sprechen oder schreiben."
                ),
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
    """Sagt dem wartenden Browser, wie weit die Auswertung ist.

    Diese Adresse ruft kein Mensch auf, sondern das Skript auf dem
    Warteschirm. Die Antwort ist JSON, keine Seite. Steht dort „complete",
    leitet der Browser selbst zum Ergebnis weiter.

    **`phase` sagt, welcher Aufruf gerade läuft.** Ablesbar ist das am
    Zwischenstand, den der Lauf zwischen den beiden Modellaufrufen
    ablegt — ohne eine einzige zusätzliche Spalte:

    * kein Zwischenstand → der erste Aufruf läuft (`verstehen`)
    * Zwischenstand da   → der zweite Aufruf läuft (`loesung`)
    * Ergebnis da        → `complete`

    Mehr ist heute nicht belegbar. Der Warteschirm zeigt deshalb auch
    nicht mehr: Ein Fortschritt, der nur so tut, ist schlechter als
    keiner.
    """

    sitzung = repository.get_session_or_404(database_session, session_id)
    complete = repository.get_result(database_session, session_id) is not None
    # **Ein gescheiterter Lauf meldet sich sofort.** Ohne diesen Vermerk
    # fragte der Warteschirm neunzig Mal nach und zeigte danach eine
    # Zeitüberschreitung, obwohl der Grund seit Sekunden feststand.
    if not complete and sitzung.lauf_fehler:
        return JSONResponse(
            {
                "state": "failed",
                "phase": "failed",
                "message": sitzung.lauf_fehler,
                "redirect_url": None,
            }
        )
    zwischenstand = repository.get_partial_result(database_session, session_id)
    if complete:
        phase = "complete"
    elif zwischenstand is not None and zwischenstand.payload:
        phase = "loesung"
    else:
        phase = "verstehen"
    return JSONResponse(
        {
            "state": "complete" if complete else "pending",
            "phase": phase,
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
    """Stellt die Auswertung in die Warteschlange und antwortet sofort.

    Aufgerufen vom Skript auf dem Warteschirm. **Gerechnet wird nicht mehr
    hier.** Vorher lief die vollständige Analyse in diesem Request — drei
    Modellaufrufe, rund achtzig Sekunden, in denen die Verbindung zum
    Browser offen blieb. Ein Sprachmodell hat keine zugesagte Laufzeit, und
    Reverse Proxies im Betrieb schneiden lange Requests ab; dann stirbt die
    Arbeit mitten drin, und niemand weiß, wie weit sie kam.

    Jetzt legt die Route den Auftrag hin und ist fertig. Den Rest macht der
    Worker, und der Warteschirm fragt über `/analysis-status` nach.

    Die Antwort sagt trotzdem, wohin es geht, wenn schon etwas vorliegt:
    Ist das Ergebnis fertig — oder läuft Celery im Sofortmodus, wie in den
    Tests —, geht es direkt weiter statt über eine Warteschleife.
    """

    repository.get_session_or_404(database_session, session_id)

    # Erst einstellen, dann nachsehen. In der Reihenfolge, weil im
    # Sofortmodus (Tests) die Arbeit während `delay()` schon passiert.
    auswertung_erzeugen.delay(session_id)
    database_session.expire_all()
    payload, status_code = analysis_service.stand_der_auswertung(
        session_id, database_session
    )
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


def kartenkontext(ergebnis: object) -> dict[str, object]:
    """Die Landschaft mit den Markierungen dieses Betriebs.

    **Erzeugt wird hier nichts.** Die Karte steht fest; aus dem Ergebnis
    kommen nur zwei Listen von Kennungen — die Familien der empfohlenen
    Module und die des Ausbaupfads. Genau deshalb kann dieser Abschnitt
    weder halluzinieren noch zu klein ausfallen.
    """

    from app import karte as kartenmodul

    def kennungen(eintraege: object) -> list[str]:
        """Die Familienkennungen — egal ob Modell oder Wörterbuch.

        Gespeicherte Ergebnisse kommen als geprüfte Objekte, Testaufbauten
        als einfache Wörterbücher. Die Karte darf an dieser Kleinigkeit
        nicht scheitern: Sie zeigt eine feste Landschaft und ist der
        letzte Ort, an dem eine Ausnahme etwas verbessern würde.
        """

        gesammelt: list[str] = []
        for eintrag in eintraege or []:
            roh = (
                eintrag.get("solution_family_ids")
                if isinstance(eintrag, dict)
                else getattr(eintrag, "solution_family_ids", None)
            )
            gesammelt.extend(roh or [])
        return gesammelt

    beginnt = kennungen(getattr(ergebnis, "module", None))
    daneben = kennungen(getattr(ergebnis, "ausbaupfad", None))
    return {"k": kartenmodul.landschaft(beginnt, daneben), "karte": True}


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
        name="results_v1.html",
        context={
            "session_id": session_id,
            "result": results_dto.von_ergebnis(ergebnis),
        },
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
    """Die vollständige Auswertung als Seite zum Lesen.

    Dieselben Daten wie die Ergebnisseite, in der Reihenfolge des Berichts.
    Es wird nichts nachgeladen und nichts neu gerechnet.

    Der Knopf auf der Ergebnisseite führt nicht mehr hierher, sondern auf
    `report.pdf`: Was der Kunde weiterleitet, soll ein Dokument sein und
    nicht das, was ein fremder Druckdialog daraus macht.
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
            **kartenkontext(ergebnis),
            "auswertungsdatum": date.today().strftime("%d.%m.%Y"),
        },
    )


def _berichtsdaten(database_session: Session, session_id: int) -> dict[str, object] | None:
    """Der Zusammenhang, aus dem der Bericht entsteht — Seite wie Dokument.

    Beide bauen auf demselben Stand auf. Stünde er zweimal da, liefen die
    gedruckte und die gelesene Fassung irgendwann auseinander.
    """

    repository.get_session_or_404(database_session, session_id)
    ergebnis = analysis_service.stored_result(database_session, session_id)
    if ergebnis is None:
        return None
    return {
        "e": ergebnis,
        **kartenkontext(ergebnis),
        "auswertungsdatum": date.today().strftime("%d.%m.%Y"),
    }


@router.get(
    "/sessions/{session_id}/report.pdf",
    name="show_report_pdf",
)
async def show_report_pdf(
    request: Request,
    session_id: int,
    database_session: Session = Depends(get_db_session),
) -> Response:
    """Die Auswertung als fertiges PDF.

    **Warum das hier entsteht und nicht im Browser des Kunden.** Vorher
    öffnete der Knopf den Druckdialog. Was dabei herauskam, hing von den
    Einstellungen des Kunden ab: Kopfzeilen mit `localhost`, ein
    Skalierungsfaktor, abgeschaltete Hintergrundfarben. Drei Kunden
    bekamen drei verschiedene Dokumente — und dieses Dokument ist das,
    was er an uns zurückschickt.

    Fehlt der Browser für die Erzeugung, ist das kein Grund, den Kunden
    ins Leere laufen zu lassen: Dann führt der Weg zurück auf die Seite,
    die dieselben Inhalte trägt.
    """

    daten = _berichtsdaten(database_session, session_id)
    if daten is None:
        return redirect_response(next_valid_path(database_session, session_id))

    html = templates.get_template("report.html").render(
        request=request, pdf=True, **daten
    )
    try:
        dokument = await bericht_pdf.aus_html(html)
    except bericht_pdf.PdfNichtVerfuegbar:
        logger.exception("PDF konnte nicht erzeugt werden, Sitzung %s", session_id)
        # **Relativ, nicht über `url_for`.** Das lieferte eine vollständige
        # Adresse samt Rechnernamen, und `publicize_redirect` erkennt nur
        # die relative Form — die Sitzungsnummer stand danach im Browser
        # des Kunden, obwohl sie ab `/begin` in keiner Adresse mehr
        # auftauchen soll.
        return redirect_response(f"/sessions/{session_id}/report")

    name = bericht_pdf.dateiname(str(daten["auswertungsdatum"]))
    return Response(
        content=dokument,
        media_type="application/pdf",
        # `inline`: Der Kunde soll es zuerst sehen. Speichern kann er es
        # aus der Ansicht heraus immer noch.
        headers={"Content-Disposition": f'inline; filename="{name}"'},
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
        name="results_v1.html",
        context={
            "result": results_dto.von_ergebnis(ergebnis),
            "beispiel": True,
        },
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
    # Die vollstaendige Auswertung als Seite
    ("GET", "/report.pdf", "show_report_pdf_public", show_report_pdf, Response),
    # Dieselbe Auswertung als Dokument
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
