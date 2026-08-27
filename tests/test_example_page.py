"""Die Rückfallebene für die Vorführung.

Ein hinterlegter Beispiellauf unter eigener Adresse, ohne Modellaufruf. Was
hier geprüft wird, ist vor allem, dass er sich **nicht** als echtes Ergebnis
ausgibt und dass kein Weg aus dem Kundenablauf dorthin führt.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import repository
from app.services import example_service


def test_the_example_is_available_without_a_model_call(
    client: TestClient,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Die Seite kommt, auch wenn jeder Modellaufruf scheitern würde."""

    def niemals(**_kwargs: object) -> None:
        raise AssertionError("Der Beispiellauf darf das Modell nicht rufen.")

    from app import openai_service

    monkeypatch.setattr(openai_service, "parse_structured_output", niemals)

    antwort = client.get("/beispiel/hausverwaltung")

    assert antwort.status_code == 200
    assert "Das hätten Sie künftig vor sich" in antwort.text


def test_the_example_says_that_it_is_an_example(client: TestClient) -> None:
    """Der Hinweis steht auf der Seite, nicht nur im Code."""

    antwort = client.get("/beispiel/hausverwaltung")

    assert "Gespeicherter Beispiellauf" in antwort.text
    assert "beschreibt nicht Ihren" in antwort.text


def test_a_real_result_carries_no_example_notice(client: TestClient) -> None:
    """Ein echtes Ergebnis sieht nicht aus wie ein Beispiel."""

    client.post("/begin", follow_redirects=False)
    client.post(
        "/interview",
        data={"free_description": "Wir sind zu dritt und suchen ständig Unterlagen."},
        follow_redirects=False,
    )
    assert client.post("/analyze").json()["state"] == "complete"

    antwort = client.get("/results")

    assert antwort.status_code == 200
    assert "Gespeicherter Beispiellauf" not in antwort.text


def test_a_failed_run_does_not_fall_back_to_the_example(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Scheitert ein echter Lauf, bleibt es beim Fehler.

    Ein stiller Rückfall würde dem Kunden ein fremdes Ergebnis als sein
    eigenes zeigen — genau die Schummelei, die der Vertrag sonst überall
    verhindert.
    """

    from app.openai_service import AIServiceError
    from app.services import analysis_service

    def scheitert(**_kwargs: object) -> None:
        raise AIServiceError("Der Modelldienst antwortet nicht.")

    monkeypatch.setattr(analysis_service, "generate_diagnosis", scheitert)
    client.post("/begin", follow_redirects=False)
    client.post(
        "/interview",
        data={"free_description": "Wir sind zu dritt und suchen ständig Unterlagen."},
        follow_redirects=False,
    )

    antwort = client.post("/analyze")

    assert antwort.status_code == 503
    assert antwort.json()["state"] == "error"
    assert antwort.json()["redirect_url"] is None
    assert "beispiel" not in antwort.text.casefold()


def test_the_example_is_stored_in_the_database(
    client: TestClient,
    database_session: Session,
) -> None:
    """Gelesen wird aus `results`, wie bei jedem echten Ergebnis auch."""

    client.get("/beispiel/hausverwaltung")

    database_session.expire_all()
    sitzung = repository.get_example_session(database_session, "hausverwaltung")
    assert sitzung is not None
    gespeichert = repository.get_result(database_session, sitzung.session_id)
    assert gespeichert is not None
    assert gespeichert.payload["contract_version"] == "ergebnis-v6"


def test_calling_it_twice_creates_only_one_session(
    client: TestClient,
    database_session: Session,
) -> None:
    """Der zweite Aufruf liest, statt noch einmal anzulegen."""

    client.get("/beispiel/hausverwaltung")
    database_session.expire_all()
    zuerst = repository.get_example_session(database_session, "hausverwaltung")

    client.get("/beispiel/hausverwaltung")

    database_session.expire_all()
    danach = repository.get_example_session(database_session, "hausverwaltung")
    assert danach is not None
    assert danach.session_id == zuerst.session_id


def test_an_unknown_example_is_a_404(client: TestClient) -> None:
    """Kein erfundener Beispielname erzeugt eine Seite."""

    assert client.get("/beispiel/gibtesnicht").status_code == 404


def test_the_stored_example_still_matches_the_contract(
    database_session: Session,
) -> None:
    """Das hinterlegte Beispiel geht durch dieselbe Prüfung wie ein echtes.

    Ändert sich der Vertrag, wird dieser Test rot — und nicht erst die Seite
    mitten in der Vorführung.
    """

    ergebnis = example_service.example_result(database_session, "hausverwaltung")

    assert ergebnis.contract_version == "ergebnis-v6"
    assert len(ergebnis.verstanden.belege) >= 2
    assert ergebnis.kurzfassung.loesungsname


def test_the_example_is_not_reachable_from_the_customer_path(
    client: TestClient,
) -> None:
    """Es führt kein Verweis aus dem Ablauf auf den Beispiellauf."""

    client.post("/begin", follow_redirects=False)
    for pfad in ("/", "/interview"):
        assert "/beispiel/" not in client.get(pfad).text

# --- Der Abschnitt, der nichts kostet -------------------------------------


def _mit_hebeln(client: TestClient, monkeypatch: pytest.MonkeyPatch, *hebel: object) -> str:
    """Dieselbe Beispielseite, nur mit Hebeln im Ergebnis."""

    echt = example_service.example_result
    monkeypatch.setattr(
        example_service,
        "example_result",
        lambda db, slug: echt(db, slug).model_copy(update={"hebel": list(hebel)}),
    )
    return client.get("/beispiel/hausverwaltung").text


def _hebel(**overrides: object) -> object:
    from app.result_schema import Lever

    daten: dict[str, object] = {
        "idee": "Halten Sie jede Zusage noch im Gespräch fest.",
        "woraus": "Jeder arbeitet ein bisschen anders.",
        "warum": "Dann muss sie später niemand zusammensuchen.",
        "ohne_technik": True,
    }
    daten.update(overrides)
    return Lever(**daten)  # type: ignore[arg-type]


def test_the_board_carries_no_free_advice(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Auf der Verkaufsseite steht nicht, was er umsonst selbst ändern kann.

    Die Seite zeigt, was wir für ihn bauen würden. Daneben zu erklären, was
    er ohne uns hinbekommt, ist eine Ausfahrt aus genau dem Gespräch, das
    die Seite eröffnen soll. Die Hebel sind deshalb nicht gestrichen — sie
    stehen vollständig im Ausdruck, wo die Beratung stattfindet.
    """

    seite = _mit_hebeln(
        client,
        monkeypatch,
        _hebel(idee="Erster Hebel."),
        _hebel(idee="Zweiter Hebel."),
    )

    assert "ohne Technik" not in seite
    assert "Erster Hebel." not in seite
    assert "Zweiter Hebel." not in seite
    # Und der Ausdruck trägt sie weiterhin alle: Die Druckvorlage läuft über
    # `e.hebel` und schneidet nichts ab.
    druckvorlage = (
        Path(__file__).resolve().parents[1] / "app/templates/ergebnis_teile.html"
    ).read_text(encoding="utf-8")
    assert "{% for h in e.hebel %}" in druckvorlage



def test_the_stored_example_carries_a_full_result(client: TestClient) -> None:
    """Der hinterlegte Lauf zeigt die Tafel vollständig.

    Er ist die Rückfallebene für eine Vorführung ohne Netz. Fehlt ihm ein
    Bereich, fehlt er genau dann, wenn jemand zuschaut.
    """

    seite = client.get("/beispiel/hausverwaltung").text

    for abschnitt in (
        "Das haben wir verstanden",
        "Was bei Ihnen gerade den Aufwand erzeugt",
        "Das würde sich für Sie verändern",
        "Das hätten Sie künftig vor sich",
        "Das würden wir für Sie umsetzen",
        "Das läuft künftig automatisch",
        "Möchten Sie so arbeiten?",
    ):
        assert abschnitt in seite, abschnitt

    # **Und was nicht mehr daraufgehört.** Die Bestandsliste zeigt ihm, wie
    # viel er schon hat — auf der Seite, auf der er entscheidet, ob er weiter
    # schaut. Der Startplan erklärt unser Vorgehen, bevor er überhaupt will.
    # Beides ist nicht gestrichen, sondern in den Ausdruck gewandert.
    for verschoben in ("Darauf bauen wir auf", "So würden wir anfangen"):
        assert verschoben not in seite, verschoben


def test_a_lever_that_needs_technology_is_not_promised_as_free(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Die Überschrift verspricht „ohne Technik" — dann muss das auch gelten."""

    seite = _mit_hebeln(
        client,
        monkeypatch,
        _hebel(idee="Führen Sie eine Sammelstelle ein.", ohne_technik=False),
    )

    assert "ohne Technik ändern könnten" not in seite
    assert "Führen Sie eine Sammelstelle ein." not in seite
