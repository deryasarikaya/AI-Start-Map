from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session


ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIRECTORY / ".env")

test_database_url = os.getenv("TEST_DATABASE_URL")
if not test_database_url:
    raise RuntimeError(
        "TEST_DATABASE_URL ist nicht gesetzt. Verwende eine separate "
        "PostgreSQL-Testdatenbank."
    )

os.environ["DATABASE_URL"] = test_database_url

from app.database import SessionFactory, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def migrate_test_database() -> None:
    alembic_config = Config(str(ROOT_DIRECTORY / "alembic.ini"))
    command.upgrade(alembic_config, "head")


@pytest.fixture(autouse=True)
def clear_test_database(migrate_test_database: None) -> None:
    table_names = (
        "automation_opportunities, analyses, process_options, "
        "interview_questions, sessions"
    )
    with engine.begin() as connection:
        connection.execute(
            text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE")
        )


@pytest.fixture(autouse=True)
def mock_product_classification_and_ranking(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep external model calls mocked in HTTP tests unless a test overrides them."""

    from app import routes
    from app.llm_classification import ClassificationOutcome
    from app.recommendation_service import (
        CandidateRankingItem,
        classify_problem_families,
        infer_decision_gates,
    )

    def classify(text: str, **_kwargs: object) -> ClassificationOutcome:
        return ClassificationOutcome(
            problem_family_ids=classify_problem_families(text),
            gates=infer_decision_gates(text),
            method="llm",
            business_type_guess="",
        )

    def rank(_text, candidates):
        return [
            CandidateRankingItem(
                solution_id=item.solution_id,
                reason="Gemockte fallbezogene Rangfolge",
            )
            for item in candidates
        ]

    monkeypatch.setattr(routes, "classify_narrative", classify)
    monkeypatch.setattr(routes, "rank_candidates", rank)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def database_session() -> Generator[Session, None, None]:
    with SessionFactory() as session:
        yield session


# ---------------------------------------------------------------------------
# Kanonischer Vertrag nach docs/auftrag/ERGEBNIS_SPEC.md
#
# Ein Bauplan fuer alle Tests. Wer eine Abweichung braucht, uebergibt sie als
# override - damit steht der Vertrag genau an einer Stelle.
# ---------------------------------------------------------------------------


def spec_payload(**overrides: object) -> dict[str, object]:
    """Gueltige Modellausgabe nach der Ergebnis-Spec."""

    payload: dict[str, object] = {
        "engpass_titel": "Du suchst deine Bestellungen in vier Chats",
        "engpass_text": (
            "Bestellungen kommen über WhatsApp, Instagram, Mail und den Shop "
            "herein. Beim Vorbereiten schaust du jedes Mal in mehreren Chats "
            "nach, was jemand wollte."
        ),
        "moeglichkeiten": [
            {
                "rang": "groesster_hebel",
                "titel": "Ein Eingang für alle Bestellungen",
                "begruendung": "Hier geht heute die meiste Zeit verloren.",
            },
            {
                "rang": "danach",
                "titel": "Fehlende Angaben früh erkennen",
                "begruendung": "Rückfragen kosten dich später einen zweiten Anlauf.",
            },
        ],
        "loesung": {
            "titel": "Ein Eingang für alles was reinkommt",
            "ablauf_heute": [
                "Du liest die Nachricht im jeweiligen Chat.",
                "Du schreibst dir die Angaben auf einen Zettel.",
                "Du suchst beim Binden noch einmal alles zusammen.",
            ],
            "ablauf_kuenftig": [
                "Die Nachricht landet in einem gemeinsamen Eingang.",
                "Die Angaben stehen schon zusammengefasst da.",
                "Du prüfst kurz und gibst frei.",
            ],
            "was_reinkommt": "WhatsApp, Instagram, E-Mail und dein Onlineshop.",
            "was_die_ki_macht": (
                "Liest heraus, wann der Strauß fertig sein soll, für wen er ist, "
                "welche Farben gewünscht sind und wohin er geliefert wird."
            ),
            "was_du_machst": "Du prüfst die Angaben und gibst die Bestellung frei.",
            "was_dabei_rauskommt": "Eine Bestellkarte mit allen Angaben an einer Stelle.",
            "ergebnis_art": "Bestellkarte",
        },
        "beispiel": {
            "titel": "Was aus einer WhatsApp-Nachricht wird",
            "kanal": "WhatsApp",
            "nachricht": (
                "Hallo, ich bräuchte einen Strauß für Samstag, gerne in Rosa "
                "und Weiß. Für meine Mutter zum Geburtstag. Können Sie den "
                "liefern?"
            ),
            "daraus_wird": [
                {"label": "Für wen", "wert": "Mutter der Kundin, Geburtstag"},
                {"label": "Bis wann", "wert": "Samstag"},
                {"label": "Farben", "wert": "Rosa und Weiß"},
            ],
            "fehlt": ["Lieferadresse", "Preisrahmen"],
            "rueckfrage": "Wohin sollen wir liefern, und was darf der Strauß kosten?",
        },
        "voraussetzungen": {
            "vorhandene_werkzeuge": ["WhatsApp", "Instagram", "dein Onlineshop"],
            "neu_hinzukommend": ["eine gemeinsame Bestellübersicht"],
            "geraete_und_zugang": (
                "Dein Smartphone und der Laden-Laptop reichen. Die Bestellungen "
                "siehst du über eine Seite im Browser."
            ),
            "musst_du_besorgen": [],
        },
        "umsetzung": {
            "hinweis": "Das hier ist die Diagnose. Gebaut ist noch nichts.",
            "einrichtungsschritte": [
                "Ich verbinde deine Kanäle mit einem gemeinsamen Eingang.",
                "Ich richte die Übersicht mit deinen Angaben ein.",
                "Ich prüfe das an deinen echten Bestellungen nach.",
            ],
            "erster_schritt": (
                "Wir fangen mit WhatsApp an, weil dort die meisten Bestellungen "
                "hereinkommen. Nach zwei Wochen sehen wir, ob du beim Binden "
                "noch einmal nachschauen musst."
            ),
        },
        "bleibt_bei_dir": (
            "Du entscheidest über Preis, Liefertermin und was du zusagst."
        ),
        "grenzen": "",
        "spaeter": [],
        "process_summary": "Bestellungen kommen über mehrere Kanäle herein.",
        "as_is_steps": [
            "Du liest die Nachricht im jeweiligen Chat.",
            "Du notierst die Angaben auf einem Zettel.",
            "Du suchst beim Binden noch einmal alles zusammen.",
        ],
        "as_is_problem_step_indexes": [2],
        "to_be_steps": [],
        "core_bottleneck": "Die Angaben liegen über mehrere Kanäle verteilt.",
        "bottleneck_symptom": "Du schaust mehrfach nach.",
        "bottleneck_cause": "Es gibt keinen gemeinsamen Eingang.",
        "bottleneck_effect": "Beim Binden fehlt dir die Übersicht.",
        "uncertainties": [],
        "autonomy_level": "A2",
        "not_automated": ["Preisentscheidung", "Liefertermin"],
        "error_boundaries": ["Keine Zusage ohne deine Freigabe."],
    }
    payload.update(overrides)
    return payload


def spec_view(**overrides: object) -> dict[str, object]:
    """Kundenpayload so, wie ihn _result_view an die Templates gibt."""

    payload = spec_payload()
    beispiel = dict(payload["beispiel"])  # type: ignore[arg-type]
    beispiel["hinweis"] = "Beispielangaben zur Veranschaulichung."
    view: dict[str, object] = {
        "is_non_ai": False,
        "engpass_titel": payload["engpass_titel"],
        "engpass_text": payload["engpass_text"],
        "as_is_steps": payload["as_is_steps"],
        "problem_step_indexes": payload["as_is_problem_step_indexes"],
        "moeglichkeiten": payload["moeglichkeiten"],
        "loesung": payload["loesung"],
        "beispiel": beispiel,
        "voraussetzungen": payload["voraussetzungen"],
        "umsetzung": payload["umsetzung"],
        "bleibt_bei_dir": payload["bleibt_bei_dir"],
        "grenzen": "",
        "current_process_summary": payload["process_summary"],
        "contact_recommendation": payload["loesung"]["titel"],  # type: ignore[index]
    }
    view.update(overrides)
    return view
