"""Verbindung zur Datenbank.

Zwei Aufgaben: die Adresse der Datenbank aus der Umgebung lesen und je Anfrage
eine Sitzung bereitstellen, die danach sicher geschlossen wird. Sonst nichts.
"""

from __future__ import annotations

import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


load_dotenv()


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL ist nicht gesetzt. Kopiere .env.example nach .env "
            "und trage dort die PostgreSQL-Verbindung ein."
        )
    return database_url


engine: Engine = create_engine(get_database_url(), pool_pre_ping=True)
SessionFactory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def get_db_session() -> Generator[Session, None, None]:
    """Eine Datenbanksitzung für die Dauer einer Anfrage.

    FastAPI ruft das je Anfrage; am Ende wird die Sitzung geschlossen.
    """

    with SessionFactory() as database_session:
        yield database_session
