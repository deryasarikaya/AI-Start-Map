"""Die fachlichen Regeln stehen im Prompt, den die Anwendung wirklich lädt.

Kein Modellaufruf. Diese Tests halten fest, was inhaltlich zugesagt ist —
nicht wie es formuliert ist. Sie laden die Prompts über dieselbe Funktion wie
der Produktionspfad: Wird eine Datei umbenannt oder ein Aufruf umgehängt,
werden sie rot statt still zu einem anderen Text zu greifen.

Der Anlass: Ein sehr kleiner Automationsfall bekam fünf Lösungsfamilien,
drei erzwungene Beispielansichten und einen Hebel, der genau die morgendliche
Handarbeit vorschlug, die die Lösung gerade abschafft. Nichts davon war ein
Fehler im Code — alles stand so im Prompt.
"""

from __future__ import annotations

import pytest

from app.openai_service import _prompt

AUSWAHL = "zielarchitektur"
ANSICHTEN = "ergebnis_teil2a"
REST = "ergebnis_teil2b"


# --- Die kleinste Lösung, die den Engpass löst ----------------------------


def test_the_selection_asks_for_the_smallest_sufficient_set() -> None:
    """Die Auswahlregel steht da, und sie steht als Frage."""

    prompt = _prompt(AUSWAHL)

    assert "kleinste Menge" in prompt
    assert "Würde die Lösung ohne diese Familie weiterhin funktionieren" in prompt
    assert "Ist die Antwort ja, wähle sie nicht" in prompt


def test_a_mention_is_not_a_recommendation() -> None:
    """Dass jemand E-Mails erwähnt, begründet keine Marketingautomation."""

    prompt = _prompt(AUSWAHL)

    assert "Eine Erwähnung ist keine Empfehlung" in prompt
    assert "nicht automatisieren will" in prompt


def test_the_selection_forces_no_minimum() -> None:
    """Null Familien sind eine richtige Antwort.

    Eine Untergrenze im Prompt macht jede Grenze im Schema wirkungslos: Das
    Modell füllt dann auf, und der Server lässt es durch, weil nichts
    verletzt ist.
    """

    prompt = _prompt(AUSWAHL)

    assert "Es gibt keine Mindestzahl" in prompt
    assert "drei bis neun" not in prompt
    assert "drei bis fünf Kurznamen" not in prompt


# --- Ansichten nur, wenn ein Mensch etwas ansehen muss --------------------


def test_views_are_only_created_when_someone_must_look(  ) -> None:
    """Null Ansichten sind gültig, wenn die Lösung im Hintergrund läuft."""

    prompt = _prompt(ANSICHTEN)

    assert "null Ansichten die richtige Antwort" in prompt
    assert "Was müsste der Mensch künftig tatsächlich sehen?" in prompt


def test_no_screen_is_drawn_for_a_system_that_stays() -> None:
    """Bleibt der Kalender, wird er nicht als neue Anwendung nachgebaut."""

    prompt = _prompt(ANSICHTEN)

    assert "Baue keine Oberfläche für ein System, das bleibt" in prompt
    assert "keine erfundene Anwendung" in prompt


# --- Hebel, die nicht die Handarbeit verstärken ---------------------------


def test_a_lever_may_not_reinforce_the_manual_work_being_removed() -> None:
    """**Der Widerspruch, der im Live-Lauf sichtbar wurde.**

    Eine Automation empfehlen und daneben eine tägliche Kontrollrunde von
    Hand hebt die eigene Empfehlung auf.
    """

    prompt = _prompt(REST)

    assert "darf nicht die Handarbeit verstärken" in prompt
    assert "manuelle Prüfliste" in prompt


def test_no_lever_is_a_valid_answer() -> None:
    """Kein Hebel ist besser als ein erfundener."""

    prompt = _prompt(REST)

    assert "gern **keiner**" in prompt


# --- Jedes Feld hat genau eine Aufgabe ------------------------------------


@pytest.mark.parametrize("name", [AUSWAHL, REST])
def test_each_field_has_one_job(name: str) -> None:
    """Sonst liest der Kunde dieselbe Empfehlung sieben Mal."""

    prompt = _prompt(name)

    assert "Jeder Abschnitt hat genau eine Aufgabe" in prompt
    assert "kurze vollständige Sätze" in prompt


def test_the_two_explaining_fields_are_kept_apart() -> None:
    """„Warum diese Lösung" und das Zielbild beantworten verschiedene Fragen."""

    prompt = _prompt(AUSWAHL)

    assert "Warum löst genau diese Zusammenstellung den diagnostizierten" in prompt
    assert "Was passiert künftig als zusammenhängendes System?" in prompt
