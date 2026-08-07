from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIRECTORY))

from app.recommendation_service import load_recommendation_catalog  # noqa: E402


CANDIDATE_DIRECTORY = ROOT_DIRECTORY / "knowledge" / "candidates" / "batch_09"
RUNTIME_DIRECTORY = ROOT_DIRECTORY / "knowledge" / "runtime"
EVALUATION_DIRECTORY = ROOT_DIRECTORY / "knowledge" / "evaluation"

CUSTOMER_OUTPUT_NAMES = {
    "SP-01": "Anfrage\u00fcbersicht",
    "SP-02": "Auftrags\u00fcbersicht",
    "SP-03": "Einsatznotiz",
    "SP-04": "Gegenstand und Ablageort",
    "SP-05": "Terminanfrage",
    "SP-06": "Gelesene Dokumentangaben",
    "SP-07": "\u00c4nderungsnotiz",
    "SP-08": "Material- und Arbeits\u00fcbersicht",
    "SP-09": "Rechnungs\u00fcbersicht",
    "SP-10": "\u00dcbergabenotiz",
}

CUSTOMER_OUTPUT_FIELDS: dict[str, dict[str, tuple[str, str]]] = {
    "SP-01": {
        "contact": ("Von wem", "Anna Berger \u00b7 WhatsApp"),
        "request_type": ("Worum es geht", "Blumenstrau\u00df zur Abholung"),
        "requested_service": ("Gew\u00fcnschte Leistung", "Geburtstagsstrau\u00df in Rosa und Wei\u00df"),
        "place": ("Ort oder \u00dcbergabe", "Abholung im Laden"),
        "desired_date": ("Gew\u00fcnschter Termin", "Freitag, 16:30 Uhr"),
        "missing_items": ("Noch zu kl\u00e4ren", "Preisrahmen und Gru\u00dfkartentext"),
    },
    "SP-02": {
        "case_ref": ("Auftrag", "Fotoshooting Familie Neumann"),
        "current_status": ("Aktueller Stand", "Bildauswahl erhalten"),
        "next_step": ("N\u00e4chster Schritt", "Finale Auswahl best\u00e4tigen"),
        "owner": ("Wer k\u00fcmmert sich", "Mara Neumann"),
        "due_date": ("Bis wann", "Freitag, 14. August"),
        "open_questions": ("Noch zu kl\u00e4ren", "D\u00fcrfen zwei Bilder zus\u00e4tzlich bearbeitet werden?"),
    },
    "SP-03": {
        "customer_or_object": ("F\u00fcr wen", "Hausverwaltung Nord \u00b7 Lindenstra\u00dfe 12"),
        "activity": ("Was gemacht wurde", "Waschbecken-Dichtung getauscht"),
        "working_time": ("Wie lange", "45 Minuten"),
        "materials": ("Material", "Dichtungssatz, 12,40 \u20ac"),
        "special_events": ("Besonderheiten", "Zugang nur \u00fcber die Hausverwaltung"),
        "open_items": ("Noch zu kl\u00e4ren", "Der Mieter wollte noch die T\u00fcr nachstellen \u2013 abrechnen?"),
    },
    "SP-04": {
        "object_id": ("Gegenstand", "Braune Lederschuhe \u00b7 Reparatur 18"),
        "physical_location": ("Wo liegt er", "Regal B \u00b7 Fach 3"),
        "assignment_checked_by": ("Gepr\u00fcft von", "Werkstattannahme"),
    },
    "SP-05": {
        "requester": ("Wer fragt an", "Leonie Hartmann"),
        "time_window": ("Gew\u00fcnschte Zeit", "Dienstag zwischen 15 und 17 Uhr"),
        "duration": ("Geplante Dauer", "60 Minuten"),
        "service_type": ("Terminart", "Erstgespr\u00e4ch"),
        "resource_needs": ("Was gebraucht wird", "Ein freier Behandlungsraum"),
        "valid_options": ("M\u00f6gliche Termine", "Dienstag 16:00 oder Mittwoch 11:30"),
    },
    "SP-06": {
        "document_ref": ("Dokument", "Lieferantenrechnung vom 5. August"),
        "document_type": ("Art des Dokuments", "Materialrechnung"),
        "extracted_fields": ("Gelesene Angaben", "Lieferant, Datum, Betrag und Rechnungsnummer"),
        "source_locations": ("Wo es steht", "Kopfzeile und Rechnungssumme"),
        "uncertainties": ("Unsicher erkannt", "Die zweite Materialposition"),
        "review_status": ("Deine Pr\u00fcfung", "Noch nicht best\u00e4tigt"),
    },
    "SP-07": {
        "case_ref": ("Auftrag", "Website Familie Roth"),
        "baseline": ("Bisher vereinbart", "Startseite und Kontaktformular"),
        "requested_change": ("Gew\u00fcnschte \u00c4nderung", "Zus\u00e4tzliche Seite f\u00fcr Leistungen"),
        "affected_version": ("Betroffener Stand", "Entwurf vom 6. August"),
        "approval_status": ("Freigabe", "Noch nicht best\u00e4tigt"),
        "open_impacts": ("Auswirkung", "Der Liefertermin verschiebt sich m\u00f6glicherweise um zwei Tage"),
    },
    "SP-08": {
        "order_ref": ("Auftrag", "12 Kerzenhalter in Eiche"),
        "item_and_quantity": ("Produkt und Menge", "12 Kerzenhalter"),
        "due_date": ("Fertig bis", "Freitag, 21. August"),
        "material_needs": ("Ben\u00f6tigtes Material", "Eichenholz, \u00d6l und Verpackung"),
        "production_status": ("Arbeitsstand", "8 fertig, 4 in Bearbeitung"),
        "next_step": ("Als N\u00e4chstes", "Restliche Teile \u00f6len und verpacken"),
    },
    "SP-09": {
        "invoice_or_case_ref": ("Rechnung oder Auftrag", "Rechnung f\u00fcr Hausverwaltung Nord \u00b7 August"),
        "confirmed_services": ("Abgerechnete Arbeit", "Dichtung am Waschbecken getauscht"),
        "quantities_or_time": ("Zeit und Menge", "45 Minuten \u00b7 1 Dichtungssatz"),
        "expenses": ("Auslagen", "Material 12,40 \u20ac"),
        "due_date": ("Zahlbar bis", "28. August 2026"),
        "payment_status": ("Zahlungsstand", "Rechnung vorbereitet, noch nicht versendet"),
    },
    "SP-10": {
        "case_ref": ("Auftrag", "Fotoshooting Familie Neumann"),
        "current_state": ("Aktueller Stand", "Bildauswahl ist abgeschlossen"),
        "confirmed_decisions": ("Was entschieden ist", "20 Bilder werden final bearbeitet"),
        "open_items": ("Noch zu kl\u00e4ren", "Freigabe f\u00fcr zwei zus\u00e4tzliche Bilder"),
        "next_actions": ("Als N\u00e4chstes", "Auswahl best\u00e4tigen und Bearbeitung starten"),
        "source_refs": ("Dabei ber\u00fccksichtigt", "Briefing, E-Mail und Kundenkommentar"),
    },
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def source_ids(path: Path) -> set[str]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return {row["source_id"] for row in csv.DictReader(stream)}


def validate_source_refs(records: list[dict[str, Any]], known_sources: set[str]) -> None:
    missing = sorted(
        {
            source_ref
            for record in records
            for source_ref in record.get("source_refs", [])
            if source_ref not in known_sources
        }
    )
    if missing:
        raise ValueError(f"Unbekannte source_refs: {missing}")


def build_runtime_payloads() -> dict[Path, list[dict[str, Any]]]:
    patterns = read_jsonl(CANDIDATE_DIRECTORY / "01_customer_inference_patterns.jsonl")
    workflows = read_jsonl(CANDIDATE_DIRECTORY / "02_solution_workflows.jsonl")
    outputs = read_jsonl(CANDIDATE_DIRECTORY / "03_output_structures.jsonl")
    evaluations = read_jsonl(CANDIDATE_DIRECTORY / "04_evaluation_cases.jsonl")
    if (len(patterns), len(workflows), len(outputs), len(evaluations)) != (27, 28, 10, 30):
        raise ValueError("Batch-09-Mengen entsprechen nicht der geprüften Lieferung.")
    known_sources = source_ids(CANDIDATE_DIRECTORY / "05_source_register.csv")
    if len(known_sources) != 20:
        raise ValueError("Das Batch-09-Quellenregister muss 20 Quellen enthalten.")
    for records in (patterns, workflows, outputs):
        validate_source_refs(records, known_sources)

    catalog = load_recommendation_catalog()
    channels_by_solution = {
        item.solution_id: item.input_channels for item in catalog.solution_patterns
    }

    runtime_patterns = [
        {**record, "source_batch": "batch_09", "quality_status": "runtime_approved"}
        for record in patterns
    ]
    runtime_workflows: list[dict[str, Any]] = []
    for record in workflows:
        steps = [
            {
                **step,
                "actor": "software_rule" if step["actor"] == "system" else step["actor"],
            }
            for step in record["target_workflow"]
        ]
        runtime_workflows.append(
            {
                "chunk_id": record["workflow_id"],
                "chunk_type": "solution_workflow",
                **record,
                "channels": channels_by_solution[record["solution_pattern_id"]],
                "maturity": [2, 3],
                "target_workflow": steps,
                "source_strength": "reviewed_synthesis",
                "source_batch": "batch_09",
                "quality_status": "runtime_approved",
            }
        )
    runtime_outputs: list[dict[str, Any]] = []
    for record in outputs:
        solution_id = record["solution_pattern_id"]
        customer_fields = CUSTOMER_OUTPUT_FIELDS[solution_id]
        fields = []
        for source_field in record["fields"]:
            field = dict(source_field)
            field["label"], field["example_value"] = customer_fields[field["field_id"]]
            fields.append(field)
        if solution_id == "SP-03":
            fields.append(
                {
                    "field_id": "included_files",
                    "label": "Dabei",
                    "data_type": "list",
                    "required": False,
                    "example_value": "2 Fotos, 1 Bon, deine Sprachnachricht",
                    "source_types": ["sprache", "foto", "bon"],
                    "requires_human_input": False,
                }
            )
        if solution_id == "SP-04":
            for field in fields:
                field["requires_human_input"] = True
        runtime_outputs.append(
            {
                **record,
                "name": CUSTOMER_OUTPUT_NAMES[solution_id],
                "fields": fields,
                "typical_missing_information": [
                    field["label"] for field in fields if field["required"]
                ],
                "human_review": (
                    "Du schaust einmal dr\u00fcber, korrigierst was nicht stimmt, "
                    "und gibst das Ergebnis frei."
                ),
                "placeholder_notice": (
                    "Beispielangaben zur Veranschaulichung \u2013 hier stehen "
                    "sp\u00e4ter deine tats\u00e4chlichen Angaben."
                ),
                "source_batch": "batch_09",
                "quality_status": "runtime_approved",
            }
        )

    return {
        RUNTIME_DIRECTORY / "patterns" / "inference_patterns.jsonl": runtime_patterns,
        RUNTIME_DIRECTORY / "solution_knowledge" / "solution_workflows.jsonl": runtime_workflows,
        RUNTIME_DIRECTORY / "output_structures.jsonl": runtime_outputs,
        EVALUATION_DIRECTORY / "batch_09_evaluation_cases.jsonl": evaluations,
    }


def write_payloads(payloads: dict[Path, list[dict[str, Any]]]) -> None:
    for path, records in payloads.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
            encoding="utf-8",
        )


def main() -> None:
    payloads = build_runtime_payloads()
    write_payloads(payloads)
    for path, records in payloads.items():
        print(f"{path.relative_to(ROOT_DIRECTORY)}: {len(records)}")


if __name__ == "__main__":
    main()
