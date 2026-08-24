"""Antworten und Vorlagen.

Die Jinja2-Konfiguration, die Weiterleitung und die Fehlerseite. Unverändert
aus `routes.py` hierher verschoben.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.schemas import customer_plain_text

templates = Jinja2Templates(directory=Path(__file__).resolve().parents[1] / "templates")
templates.env.filters["customer_text"] = customer_plain_text

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
