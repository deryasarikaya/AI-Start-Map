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
    assert "So könnte das bei Ihnen aussehen" in antwort.text


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


def test_the_section_shows_what_costs_nothing(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Idee, Begründung und der Satz, aus dem sie folgt — alle drei sichtbar.

    Ohne den Satz wäre der Vorschlag ein Ratschlag für irgendeinen Betrieb;
    er ist der Beleg und gehört deshalb auf die Seite, nicht nur ins PDF.
    """

    seite = _mit_hebeln(client, monkeypatch, _hebel())

    assert "ohne Technik ändern könnten" in seite
    assert "Halten Sie jede Zusage noch im Gespräch fest." in seite
    assert "Dann muss sie später niemand zusammensuchen." in seite
    assert "Jeder arbeitet ein bisschen anders." in seite


def test_without_levers_there_is_no_empty_heading(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ohne Hebel entfällt der Abschnitt ganz.

    Die Hebel werden hier ausdrücklich geleert, statt sich darauf zu
    verlassen, dass der hinterlegte Beispiellauf gerade keine hat. Er wird
    ersetzt, sobald ein besserer entsteht — die Zusage bleibt.
    """

    seite = _mit_hebeln(client, monkeypatch)

    assert "ohne Technik ändern könnten" not in seite


def test_the_stored_example_carries_a_full_result(client: TestClient) -> None:
    """Der hinterlegte Lauf zeigt die Tafel vollständig.

    Er ist die Rückfallebene für eine Vorführung ohne Netz. Fehlt ihm ein
    Bereich, fehlt er genau dann, wenn jemand zuschaut.
    """

    seite = client.get("/beispiel/hausverwaltung").text

    for abschnitt in (
        "Das haben wir verstanden",
        "Was sich dadurch ändert",
        "So könnte das bei Ihnen aussehen",
        "Darauf bauen wir auf",
        "Das würden wir für Sie ergänzen",
        "Was automatisch läuft",
        "So würden wir anfangen",
    ):
        assert abschnitt in seite, abschnitt


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


def test_the_page_shows_exactly_one_lever(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Die Seite zeigt den ersten Hebel, nicht mehr.

    Vorher standen zwei da. Der zweite war fast immer der schwächere und
    schnitt sich mit dem, was die Lösung ohnehin übernimmt — ein Vorschlag,
    der Einrichtung braucht, ist kein Vorschlag „ohne Technik" mehr. Ein
    starker Hebel überzeugt; ein starker und ein fadenscheiniger nicht.
    """

    seite = _mit_hebeln(
        client,
        monkeypatch,
        _hebel(idee="Erster Hebel."),
        _hebel(idee="Zweiter Hebel."),
        _hebel(idee="Dritter Hebel."),
    )

    assert "Erster Hebel." in seite
    assert "Zweiter Hebel." not in seite
    assert "Dritter Hebel." not in seite
    assert "Eine Sache, die Sie ohne Technik ändern könnten" in seite
    # Was hier wegfällt, ist nicht verloren. Die Beispielseite hat keine
    # Sitzung und damit keinen Ausdruck — geprüft wird deshalb an der
    # Druckvorlage selbst, dass sie über alle Hebel läuft und keinen
    # abschneidet.
    druckvorlage = (
        Path(__file__).resolve().parents[1]
        / "app/templates/ergebnis_teile.html"
    ).read_text(encoding="utf-8")
    assert '{% for h in e.hebel %}' in druckvorlage


def test_the_page_promises_nothing_about_cost_or_speed(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Kein „kostet Sie nichts und wirkt sofort".

    Was eine Umstellung im Betrieb des Kunden kostet und wann sie wirkt,
    lässt sich von hier aus nicht wissen. Der Satz stand als feste
    Behauptung in der Vorlage und galt damit für jeden Betrieb.
    """

    seite = _mit_hebeln(client, monkeypatch, _hebel(idee="Erster Hebel."))

    assert "kostet Sie nichts" not in seite
    assert "wirkt sofort" not in seite
