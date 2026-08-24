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
        "results, partial_results, process_options, "
        "interview_questions, sessions"
    )
    with engine.begin() as connection:
        connection.execute(
            text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE")
        )


@pytest.fixture(autouse=True)
def mock_the_two_model_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    """Haelt die beiden Modellaufrufe des kurzen Wegs aus den Tests heraus.

    Ohne diese Attrappe geht jeder Test, der `POST /analyze` ausloest, mit
    echtem Geld ans Netz. Ersetzt wird in `analysis_service`, weil dort das
    Modul seine eigene Bindung haelt - eine Attrappe an `openai_service`
    wuerde daran vorbeigehen.

    Die Zitate werden aus der uebergebenen Erzaehlung geschnitten, nicht fest
    eingetippt: Der Vertrag prueft sie woertlich gegen genau diese Erzaehlung.
    """

    from app.rag_service import RetrievedKnowledge
    from app.result_schema import (
        Diagnose,
        ResultPartTwo,
        Zielarchitektur,
        narrative,
    )
    from app.services import analysis_service
    from tests.test_result_contract import _diagnose, _part_two, _zielarchitektur

    def diagnose(*, narrative_text: str, **_kwargs: object) -> Diagnose:
        payload = _diagnose()
        payload["verstanden"]["belege"] = [
            {"zitat": zitat, "bedeutung": "Gemockte Bedeutung."}
            for zitat in _zwei_zitate(narrative_text)
        ]
        with narrative(narrative_text):
            return Diagnose.model_validate(payload)

    def zielarchitektur(*, narrative_text: str, **_kwargs: object) -> Zielarchitektur:
        with narrative(narrative_text):
            return Zielarchitektur.model_validate(_zielarchitektur())

    def teil_zwei(*, narrative_text: str, **_kwargs: object) -> ResultPartTwo:
        with narrative(narrative_text):
            return ResultPartTwo.model_validate(_part_two())

    monkeypatch.setattr(analysis_service, "generate_diagnosis", diagnose)
    monkeypatch.setattr(
        analysis_service, "generate_target_architecture", zielarchitektur
    )
    monkeypatch.setattr(analysis_service, "generate_result_part_two", teil_zwei)
    # Und der Abruf bleibt offline: Seit der Index gebaut ist, würde jeder
    # Testlauf sonst einbetten — das kostet Geld und dauert.
    monkeypatch.setattr(
        analysis_service,
        "retrieve_solution_context",
        lambda _text: RetrievedKnowledge(),
    )


def _zwei_zitate(erzaehlung: str) -> list[str]:
    """Zwei woertliche Ausschnitte aus der Erzaehlung.

    Genommen werden die zwei laengsten Saetze; der Vertrag verlangt genau zwei
    bis drei Belege und prueft sie Zeichen fuer Zeichen.
    """

    saetze = [teil.strip() for teil in erzaehlung.replace(chr(10), ". ").split(".")]
    lang = sorted((s for s in saetze if len(s) > 12), key=len, reverse=True)[:2]
    while len(lang) < 2:
        lang.append(erzaehlung.strip()[:40] or "Erzaehlung")
    return lang


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def database_session() -> Generator[Session, None, None]:
    with SessionFactory() as session:
        yield session


# ---------------------------------------------------------------------------
# Kanonischer Vertrag - siehe app/result_schema.py
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
            "darstellung": "karte",
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
        "not_automated": ["Preisentscheidung", "Liefertermin"],
        "error_boundaries": ["Keine Zusage ohne deine Freigabe."],
    }
    payload.update(overrides)
    return payload


def spec_core_output(**overrides: object) -> dict[str, object]:
    """Der Kernoutput so, wie _persist_final_analysis ihn in JSONB ablegt.

    Wer die Wortfilter oder die View-Abbildung prueft, baut damit einen
    gespeicherten Stand, ohne die Ablageform ein zweites Mal abzuschreiben.
    """

    payload = spec_payload()
    core: dict[str, object] = {
        "contract_version": "ergebnis-spec-v5",
        "engpass_titel": payload["engpass_titel"],
        "engpass_text": payload["engpass_text"],
        "moeglichkeiten": payload["moeglichkeiten"],
        "loesung": payload["loesung"],
        "beispiel": payload["beispiel"],
        "voraussetzungen": payload["voraussetzungen"],
        "umsetzung": payload["umsetzung"],
        "bleibt_bei_dir": payload["bleibt_bei_dir"],
        "grenzen": payload["grenzen"],
        "spaeter": payload["spaeter"],
        "not_automated": payload["not_automated"],
        "error_boundaries": payload["error_boundaries"],
    }
    core.update(overrides)
    return core


def spec_view(**overrides: object) -> dict[str, object]:
    """Kundenpayload so, wie ihn result_view an die Templates gibt."""

    payload = spec_payload()
    beispiel = dict(payload["beispiel"])  # type: ignore[arg-type]
    beispiel["hinweis"] = "Beispielangaben zur Veranschaulichung."
    view: dict[str, object] = {
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


def walk_to_the_result(client: TestClient, erzaehlung: str) -> None:
    """Geht den ganzen Kundenweg ab: erzählen, verstehen, auswerten.

    Seit dem Agentenschritt liegt zwischen Erzählung und Ergebnis die Seite
    „Das habe ich verstanden". Der Warteschirm wird deshalb zweimal
    durchlaufen — einmal davor, einmal danach.
    """

    client.post("/begin", follow_redirects=False)
    client.post(
        "/interview", data={"free_description": erzaehlung}, follow_redirects=False
    )
    erster = client.post("/analyze")
    assert erster.json()["redirect_url"].endswith("/verstanden"), erster.text
    client.post("/verstanden", data={"weiter": "ja"}, follow_redirects=False)
    zweiter = client.post("/analyze")
    assert zweiter.json()["redirect_url"].endswith("/results"), zweiter.text


def the_current_session(client: TestClient) -> int:
    """Die Sitzungsnummer aus dem Cookie des Browsers."""

    from app.web.session import SESSION_COOKIE, session_id_from_cookie

    class _Anfrage:
        cookies = {SESSION_COOKIE: client.cookies[SESSION_COOKIE]}

    nummer = session_id_from_cookie(_Anfrage())
    assert nummer is not None
    return nummer
