"""Antworten und Vorlagen.

Die Jinja2-Konfiguration, die Weiterleitung und die Fehlerseite. Unverändert
aus `routes.py` hierher verschoben.
"""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote

from fastapi import Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.schemas import customer_plain_text

templates = Jinja2Templates(directory=Path(__file__).resolve().parents[1] / "templates")
templates.env.filters["customer_text"] = customer_plain_text

GESPRAECHS_BETREFF = 'AI Start Map – Gespräch zu meiner Auswertung'
GESPRAECHS_TEXT = (
    'Guten Tag,\n'
    '\n'
    'ich habe meine Auswertung gesehen und möchte über die Umsetzung\n'
    'sprechen.\n'
    '\n'
    'Mein Betrieb:\n'
    'Womit ich anfangen möchte:\n'
    'So bin ich erreichbar:\n'
    '\n'
    'Freundliche Grüße\n'
)


def gespraechs_adresse() -> str:
    """Der Knopf „Genau so möchte ich arbeiten" als fertige mailto-Adresse.

    Betreff und ein vorgeschriebener Text hängen mit dran: Wer auf den
    Knopf drückt, hat gerade seine eigene Auswertung gelesen und soll
    nicht vor einem leeren Fenster sitzen.

    Die Empfängeradresse steht in der Umgebungsvariable
    `KONTAKT_ADRESSE` und **nicht** im Code — eine erfundene Adresse
    würde die Anfragen ins Leere schicken. Fehlt sie, öffnet sich das
    Mailprogramm trotzdem, nur mit leerem Empfängerfeld.
    """

    empfaenger = os.getenv('KONTAKT_ADRESSE', '').strip()
    return (
        f'mailto:{quote(empfaenger, safe="@")}'
        f'?subject={quote(GESPRAECHS_BETREFF)}'
        f'&body={quote(GESPRAECHS_TEXT)}'
    )


templates.env.globals['gespraechs_adresse'] = gespraechs_adresse

PREVIEW_NOTICE = (
    "Beispielangaben zur Veranschaulichung \u2013 hier stehen sp\u00e4ter deine "
    "tats\u00e4chlichen Angaben."
)


def redirect_response(path: str) -> RedirectResponse:
    """Eine Weiterleitung mit Statuscode 303.

    303 und nicht 302, damit der Browser nach einem Formular einen GET
    schickt und ein Neuladen nichts doppelt abschickt.
    """

    return RedirectResponse(path, status_code=status.HTTP_303_SEE_OTHER)


def render_error(
    request: Request,
    message: str,
    *,
    status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
    retry_path: str | None = None,
) -> HTMLResponse:
    """Die Fehlerseite mit einer Meldung und optional einem Weg zurück."""

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "error_title": "Die Analyse konnte nicht fortgesetzt werden.",
            "error_message": message,
            "retry_path": retry_path,
            "error_code": status_code,
        },
        status_code=status_code,
    )
