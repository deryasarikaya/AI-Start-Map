from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas import FinalAnalysisResult


def _result(case: str) -> FinalAnalysisResult:
    cases = {
        "hausmeister": {
            "primary_recommendation": "Einsätze mobil dokumentieren und zur Abrechnung vorbereiten",
            "promise": (
                "Aus deiner Sprachnachricht, deinen Fotos und dem Bon entsteht eine "
                "fertige Einsatznotiz."
            ),
            "short_reason": (
                "Die Angaben zu einem Einsatz liegen später verteilt. Vor der Rechnung "
                "musst du sie wieder zusammensuchen."
            ),
            "before_process": [
                "Du erledigst den Einsatz.",
                "Sprachnachricht, Fotos und Bon liegen getrennt.",
                "Du stellst die Angaben vor der Rechnung zusammen.",
            ],
            "future_process": [
                "Du vergibst einen einfachen Einsatzanker.",
                "Du sendest Sprachnachricht, Fotos und Bon.",
                "Die KI erstellt eine Einsatznotiz.",
                "Du prüfst die Angaben und gibst sie frei.",
            ],
            "sample_output": {
                "title": "Einsatznotiz",
                "fields": [
                    {"label": "Einsatz", "value": "noch offen"},
                    {"label": "Zeit", "value": "noch offen"},
                    {"label": "Material", "value": "noch offen"},
                ],
                "open_items": ["Zusatzarbeit bestätigen"],
                "attachments": ["Fotos", "Bon"],
            },
            "user_action": "Du sendest nach dem Einsatz Sprachnachricht, Fotos und Bon.",
            "ai_task": "Die KI ordnet alle Angaben demselben Einsatz zu und markiert Lücken.",
            "visible_result": "Du erhältst eine prüfbare Einsatznotiz mit Anhängen.",
            "human_check": (
                "Du prüfst Zuordnung, Zeit, Material und Zusatzarbeit vor der Freigabe."
            ),
            "required_prerequisites": ["Ein einfacher Einsatzanker"],
            "later_stage": (
                "Nach deiner Bestätigung kann daraus ein Rechnungsentwurf vorbereitet werden."
            ),
        },
        "schuhmacher": {
            "primary_recommendation": "Schuhe eindeutig zuordnen und Aufträge digital vorbereiten",
            "promise": (
                "Aus deinen Angaben entsteht eine Auftragskarte mit Objekt-ID, Wunsch und offenem Ort."
            ),
            "short_reason": (
                "Auftrag, Schuh und realer Ablageort sind nicht sicher verbunden. "
                "Dadurch bleibt die Herausgabe riskant."
            ),
            "before_process": [
                "Du nimmst Schuh und Reparaturwunsch an.",
                "Du notierst Angaben und Preisgrenze.",
                "Du legst den Schuh an einem realen Ort ab.",
            ],
            "future_process": [
                "Du vergibst dieselbe Kennung für Schuh und Auftrag.",
                "Die KI ordnet Wunsch, Preisgrenze und offene Angaben.",
                "Du trägst den tatsächlichen Ablageort ein.",
                "Du prüfst Auftrag und Herausgabe.",
            ],
            "sample_output": {
                "title": "Auftragskarte",
                "fields": [
                    {"label": "Objekt-ID", "value": "noch offen"},
                    {"label": "Reparaturwunsch", "value": "noch offen"},
                    {"label": "Realer Ablageort", "value": "noch offen"},
                ],
                "open_items": ["Preisgrenze bestätigen"],
            },
            "user_action": "Du kennzeichnest Schuh und Auftrag gleich und trägst den realen Ort ein.",
            "ai_task": "Die KI ordnet Wünsche und offene Angaben, aber errät niemals den Ablageort.",
            "visible_result": "Du erhältst eine Auftragskarte mit eindeutiger Objektzuordnung.",
            "human_check": (
                "Du prüfst Zustand, Preisgrenze, Ort, Freigabe und Herausgabe."
            ),
            "required_prerequisites": ["Dieselbe Kennung auf Schuh und Auftrag"],
            "later_stage": "Nach deiner Fertigprüfung kann eine Abholnachricht vorbereitet werden.",
        },
        "blumenladen": {
            "primary_recommendation": "Freie Bestellnachrichten in klare Bestellkarten verwandeln",
            "promise": (
                "Aus deiner freien Nachricht entsteht eine Bestellkarte mit allen offenen Angaben."
            ),
            "short_reason": (
                "Anlass, Budget, Farben, Ausschlüsse, Abholzeit und Kartentext kommen frei an. "
                "Einzelne Angaben fehlen."
            ),
            "before_process": [
                "Du erhältst eine freie Bestellnachricht.",
                "Du suchst Anlass, Budget und Wünsche heraus.",
                "Du fragst fehlende Angaben nach.",
            ],
            "future_process": [
                "Du leitest die Bestellnachricht weiter.",
                "Die KI ordnet Wünsche und fehlende Angaben.",
                "Du prüfst Kapazität und offene Punkte.",
                "Du entscheidest über Annahme und Antwort.",
            ],
            "sample_output": {
                "title": "Bestellkarte",
                "fields": [
                    {"label": "Anlass", "value": "noch offen"},
                    {"label": "Budget", "value": "noch offen"},
                    {"label": "Abholzeit", "value": "noch offen"},
                    {"label": "Kartentext", "value": "noch offen"},
                ],
                "open_items": ["Farben und Ausschlüsse klären"],
            },
            "user_action": "Du leitest die freie Bestellnachricht an einen festen Eingang weiter.",
            "ai_task": "Die KI ordnet die Angaben und bereitet eine Rückfrage als Entwurf vor.",
            "visible_result": "Du erhältst eine Bestellkarte mit sichtbaren Lücken.",
            "human_check": "Du prüfst Kapazität, Annahme, Abholzeit und Antwort.",
            "required_prerequisites": [],
            "later_stage": "Nach deiner Annahme kann eine Bestätigung vorbereitet werden.",
        },
        "massagesalon": {
            "primary_recommendation": "Terminanfragen bündeln und Kapazität sicher prüfen",
            "promise": (
                "Aus deiner Nachricht entsteht eine Terminanfrage mit sichtbarem Kapazitätsstatus."
            ),
            "short_reason": (
                "Wunschzeiten und reale Personalverfügbarkeit sind nicht gemeinsam sichtbar. "
                "Eine Zusage braucht deshalb deine Prüfung."
            ),
            "before_process": [
                "Du erhältst eine Terminanfrage.",
                "Du vergleichst Wunschzeit und Personal.",
                "Du sagst den Termin zu oder fragst nach.",
            ],
            "future_process": [
                "Du leitest die Terminanfrage weiter.",
                "Die KI ordnet Leistung, Dauer und Wunschzeit.",
                "Du prüfst Personal und Kapazität.",
                "Du bestätigst oder änderst den Termin.",
            ],
            "sample_output": {
                "title": "Terminanfrage",
                "fields": [
                    {"label": "Leistung", "value": "noch offen"},
                    {"label": "Wunschzeit", "value": "noch offen"},
                    {"label": "Kapazitätsstatus", "value": "zu prüfen"},
                ],
                "open_items": ["Verfügbares Personal bestätigen"],
            },
            "user_action": "Du leitest die Nachricht weiter und hältst die Verfügbarkeit aktuell.",
            "ai_task": "Die KI ordnet die Anfrage und schlägt nur prüfbare Optionen vor.",
            "visible_result": "Du erhältst eine Terminanfrage mit Kapazitätsstatus.",
            "human_check": "Du prüfst Personal und bestätigst jeden verbindlichen Termin.",
            "required_prerequisites": ["Aktuell gepflegte Personalverfügbarkeit"],
            "later_stage": "Nach deiner Zusage kann eine Bestätigungsnachricht vorbereitet werden.",
        },
    }
    values = cases[case]
    return FinalAnalysisResult(
        **values,
        software_rule="Pflichtfelder und Status werden nach festen Regeln geführt.",
        open_details=list(values["sample_output"].get("open_items", [])),
        smallest_usable_version="Mit neuen Vorgängen und einem prüfbaren Entwurf beginnen.",
        not_automated=["Verbindliche Freigabe", "Geschäftliche Entscheidung"],
        autonomy_level="A2",
        customer_benefits=[
            "Du erkennst fehlende Angaben früher.",
            "Du erhältst ein einheitliches Arbeitsergebnis.",
        ],
        implementation_path=[
            "Benötigte Eingaben und Freigabe festlegen.",
            "Die strukturierte Vorschau und menschliche Prüfung einrichten.",
        ],
        secondary_opportunities=[],
        error_boundaries=["Unklare Angaben bleiben offen und werden nicht freigegeben."],
        process_summary="Der bestätigte Ablauf wird aus den vorhandenen Angaben bearbeitet.",
        as_is_steps=values["before_process"],
        core_bottleneck=values["short_reason"],
        to_be_steps=values["future_process"],
        uncertainties=[],
    )


@pytest.mark.parametrize(
    ("case", "solution_term", "sample_title"),
    [
        ("hausmeister", "mobil dokumentieren", "Einsatznotiz"),
        ("schuhmacher", "eindeutig zuordnen", "Auftragskarte"),
        ("blumenladen", "Bestellnachrichten", "Bestellkarte"),
        ("massagesalon", "Kapazität sicher prüfen", "Terminanfrage"),
    ],
)
def test_reference_cases_produce_one_concrete_customer_result(
    case: str,
    solution_term: str,
    sample_title: str,
) -> None:
    result = _result(case)
    assert solution_term in result.primary_recommendation
    assert result.sample_output.title == sample_title
    assert result.secondary_opportunities == []
    assert "du" in result.user_action.casefold()
    assert "du" in result.human_check.casefold()


def test_housekeeper_anchor_and_invoice_boundary_are_explicit() -> None:
    result = _result("hausmeister")
    assert any("Einsatzanker" in item for item in result.required_prerequisites)
    assert all(
        term in result.human_check
        for term in ("Zuordnung", "Zeit", "Material", "Zusatzarbeit")
    )
    assert "Nach deiner Bestätigung" in result.later_stage


def test_physical_location_and_capacity_are_never_invented_or_auto_approved() -> None:
    shoe = _result("schuhmacher")
    massage = _result("massagesalon")
    flower = _result("blumenladen")
    assert "errät niemals den Ablageort" in shoe.ai_task
    assert "Herausgabe" in shoe.human_check
    assert "bestätigst jeden verbindlichen Termin" in massage.human_check
    assert "Du entscheidest über Annahme" in flower.future_process[-1]


@pytest.mark.parametrize(
    "forbidden",
    (
        "der Nutzer",
        "die Nutzerin",
        "der Unternehmer",
        "der Mitarbeiter",
        "die Person",
        "man sollte",
    ),
)
def test_distant_customer_language_is_rejected(forbidden: str) -> None:
    payload = _result("blumenladen").model_dump()
    payload["promise"] = f"{forbidden} erhält eine Bestellkarte."
    with pytest.raises(ValidationError, match="distanzierte Ansprache"):
        FinalAnalysisResult.model_validate(payload)


def test_real_employee_role_is_allowed_only_when_grounded() -> None:
    payload = _result("blumenladen").model_dump()
    payload["process_summary"] = "Du nimmst Bestellungen an; der Mitarbeiter bereitet sie vor."
    payload["as_is_steps"][1] = "Der Mitarbeiter prüft heute Farben und Ausschlüsse."
    payload["short_reason"] = "Der Mitarbeiter erhält heute einzelne Angaben erst später."
    result = FinalAnalysisResult.model_validate(payload)
    assert "Der Mitarbeiter" in result.short_reason


def test_customer_contract_enforces_length_and_count_limits() -> None:
    payload = _result("hausmeister").model_dump()
    payload["primary_recommendation"] = " ".join(["Wort"] * 15)
    with pytest.raises(ValidationError, match="14 Wörter"):
        FinalAnalysisResult.model_validate(payload)

    payload = _result("hausmeister").model_dump()
    payload["customer_benefits"] = ["Nutzen"] * 4
    with pytest.raises(ValidationError):
        FinalAnalysisResult.model_validate(payload)

    payload = _result("hausmeister").model_dump()
    payload["required_prerequisites"] = ["Voraussetzung"] * 4
    with pytest.raises(ValidationError):
        FinalAnalysisResult.model_validate(payload)

    payload = _result("hausmeister").model_dump()
    payload["secondary_opportunities"] = [
        {"title": f"Möglichkeit {index}", "description": "Nur wenn sie fachlich passt."}
        for index in range(3)
    ]
    with pytest.raises(ValidationError):
        FinalAnalysisResult.model_validate(payload)
