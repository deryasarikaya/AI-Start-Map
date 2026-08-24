"""Die Sitzung im Browser.

Jede Seite gibt es zweimal: einmal mit der Sitzungs-ID im Pfad
(`/sessions/17/interview`) und einmal ohne (`/interview`). Die öffentliche
Variante liest die ID aus einem signierten Cookie und schreibt sie aus der
Weiterleitung wieder heraus. Genau das steht hier.

Unverändert aus `routes.py` hierher verschoben.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import inspect
import os
import secrets
from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session

from app.database import get_db_session

SESSION_COOKIE = "ai_start_map_session"
SESSION_SIGNING_KEY = (
    os.getenv("SESSION_SIGNING_KEY", "").encode("utf-8") or secrets.token_bytes(32)
)


def _session_cookie_value(session_id: int) -> str:
    """Signiert die Sitzungsnummer für das Cookie.

    Ohne Signatur könnte jemand die Nummer im Cookie ändern und in
    einer fremden Sitzung landen.
    """

    payload = str(session_id).encode("ascii")
    signature = hmac.new(SESSION_SIGNING_KEY, payload, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(payload + b"." + signature).decode("ascii")


def session_id_from_cookie(request: Request) -> int:
    """Liest die Sitzungsnummer aus dem Cookie.

    Fälscht jemand das Cookie oder fehlt es, gibt es eine 404 - keine
    Fehlermeldung, die verrät, woran es lag.
    """

    encoded = request.cookies.get(SESSION_COOKIE, "")
    try:
        raw = base64.urlsafe_b64decode(encoded.encode("ascii"))
        payload, signature = raw.split(b".", 1)
        expected = hmac.new(SESSION_SIGNING_KEY, payload, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        return int(payload.decode("ascii"))
    except (ValueError, UnicodeError, TypeError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None


def set_session_cookie(response: Response, request: Request, session_id: int) -> None:
    """Legt das signierte Sitzungscookie in die Antwort."""

    response.set_cookie(
        SESSION_COOKIE,
        _session_cookie_value(session_id),
        httponly=True,
        samesite="lax",
        secure=request.url.scheme == "https",
    )


def publicize_redirect(response: Response, session_id: int) -> Response:
    """Nimmt die Sitzungsnummer aus einer Weiterleitung heraus.

    Aus `/sessions/12/results` wird `/results`. Nur Weiterleitungen
    werden angefasst; alles andere geht unverändert durch.
    """

    if not isinstance(response, RedirectResponse):
        return response
    location = response.headers.get("location", "")
    prefix = f"/sessions/{session_id}"
    if not location.startswith(prefix):
        return response
    suffix = location[len(prefix):]
    # Der Weg hat fünf Stationen. Was nicht darunter steht, bleibt mit
    # Sitzungsnummer stehen - eine unbekannte Adresse wird nicht geraten.
    public_paths = {
        "/interview",
        "/verstanden",
        "/processing",
        "/results",
        "/report",
    }
    if suffix in public_paths:
        response.headers["location"] = suffix
    return response


def register_public_route(
    router: APIRouter,
    *,
    method: str,
    path: str,
    name: str,
    session_route: Callable[..., object],
    response_class: type | None = None,
) -> None:
    """Erzeugt aus einer Sitzungsroute die öffentliche Variante.

    Die öffentliche Variante tut immer dasselbe: Sitzungs-ID aus dem Cookie
    lesen, die Sitzungsroute aufrufen, die Sitzungs-ID aus der Weiterleitung
    wieder herausnehmen. Vorher stand das achtzehnmal untereinander.

    Sitzungsrouten haben zwei Formen - mit und ohne `request`. Welche es ist,
    wird an der Signatur abgelesen, damit die Aufrufe unverändert bleiben.
    """

    needs_request = "request" in inspect.signature(session_route).parameters
    is_async = inspect.iscoroutinefunction(session_route)

    if is_async:
        async def public_route(
            request: Request,
            database_session: Session = Depends(get_db_session),
        ) -> Response:
            """Die öffentliche Variante: Sitzung aus dem Cookie, dann weiter."""
            session_id = session_id_from_cookie(request)
            if needs_request:
                result = await session_route(request, session_id, database_session)
            else:
                result = await session_route(session_id, database_session)
            return publicize_redirect(result, session_id)
    else:
        def public_route(
            request: Request,
            database_session: Session = Depends(get_db_session),
        ) -> Response:
            """Die öffentliche Variante: Sitzung aus dem Cookie, dann weiter."""
            session_id = session_id_from_cookie(request)
            if needs_request:
                result = session_route(request, session_id, database_session)
            else:
                result = session_route(session_id, database_session)
            return publicize_redirect(result, session_id)

    public_route.__name__ = name
    extra = {"response_class": response_class} if response_class is not None else {}
    router.add_api_route(
        path,
        public_route,
        methods=[method],
        name=name,
        **extra,
    )
