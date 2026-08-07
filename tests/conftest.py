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
