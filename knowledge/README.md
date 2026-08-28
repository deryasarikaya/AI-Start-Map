# Die Wissensbasis

Was hier liegt, entscheidet, was AI Start Map empfehlen darf. Der Code
entscheidet es nicht.

```
knowledge/
├── catalog/FREIGABE.json        die erlaubte Lösungsmenge
├── candidates/batch_10/         der Wissensbestand
├── business_patterns/           Betriebsarten fürs Interview
├── runtime/                     Rückfragemuster, Lösungsabläufe
├── examples/                    ein gespeicherter Lauf, ohne Modellaufruf
├── evaluation/                  synthetische Fälle für die Regression
└── archive/curated/             Diagnosekorpus für den Index
```

---

## `catalog/FREIGABE.json` — die Erlaubnis

Nur was hier steht, darf empfohlen werden.

```json
{ "erlaubt": ["SF-01", "SF-02", "…", "SF-25"] }
```

Eine Familie deaktivieren heißt: Zeile entfernen. Kein Codeeingriff, kein
Umbau. Fehlt die Datei, ist **nichts** erlaubt — nicht alles.

**Bestand ist nicht Erlaubnis.** Eine Familie kann in `candidates/batch_10/`
liegen, im Index auftauchen, vom Abruf gefunden werden — und trotzdem nicht
empfehlbar sein.

---

## `candidates/batch_10/` — der Bestand

| Datei | | Inhalt |
|---|---:|---|
| `01_business_patterns.jsonl` | 7 | Betriebsarten: Außeneinsatz, Werkstatt, Termin, Objekt … |
| `02_diagnostic_patterns.jsonl` | 23 | Engpassmuster mit den Sätzen, an denen man sie erkennt |
| `03_solution_families.jsonl` | 25 | **der Katalog** — was gebaut werden kann, mit Bausteinen |

Der Katalog ist kuratiert: SF-25 (Wirtschaftlichkeits- und
Liquiditätsvorschau) wurde aufgenommen, weil keine andere Familie die
Frage nach dem Geld beantwortet. Personalgewinnung und das Auswerten von
Rückmeldungen wurden **keine** eigenen Familien — sie sind Bausteine in
SF-21 und SF-13 geworden.
| `04_automation_capabilities.jsonl` | 14 | technische Fähigkeiten: Klassifikation, Extraktion, Routing … |
| `05_target_architectures.jsonl` | 9 | Kompositionsmuster für mehrere Familien |
| `SPEZIFIKATION.md` | | welche Felder ein Datensatz haben muss |

Geprüft mit `python scripts/pruefe_batch10.py` — Pflichtfelder, doppelte
Kennungen, Verweise ins Leere, und ob ein Abschnitt aus einem Evaluationsfall
abgeschrieben wurde.

Die Verbindung zwischen den Dateien ist der Abrufweg:
`Diagnosemuster → passende_loesungsfamilien → braucht_capabilities`. Eine
Familie, auf die kein Muster zeigt, wird vom Abruf nie vorgeschlagen — wählbar
bleibt sie trotzdem, weil das Modell den ganzen erlaubten Katalog sieht.

---

## `evaluation/` — synthetische Fälle

**Synthetic / fictional evaluation cases used for regression and quality
evaluation.**

Die Betriebe, Namen, Straßen und Situationen in `gold/` sind **erfunden**. Es
sind keine echten Kundendaten und keine Aufzeichnungen realer Gespräche. Sie
existieren, damit sich Änderungen messen lassen: dieselben dreizehn Fälle vor
und nach einem Umbau.

| | |
|---|---|
| `gold/01…13_*.json` | je eine Erzählung und die hinterlegte Erwartung |
| `cases_ten_kmu.json` | Fälle für die `/demo`-Routen |
| `cases_rb03.json`, `cases_rb04_agent.json`, `cases_rb07_guardrail.json` | von Tests gelesen |

Ein Goldfall sieht so aus:

```json
{
  "fall_id": "01_malerbetrieb",
  "erzaehlung": "Wir sind ein kleiner Malerbetrieb, mein Bruder und ich …",
  "bewertung": {
    "engpass_in_einem_satz": "Es gibt keinen Ort, an dem ein Auftrag entsteht.",
    "startpunkt": "aufbau",
    "module_anzahl_von": 5, "module_anzahl_bis": 8,
    "muss_vorkommen": ["Auftrag", "Absprache"],
    "darf_nicht_vorkommen": ["Posteingang", "Portal", "Dashboard"]
  }
}
```

`darf_nicht_vorkommen` ist das wichtigste Feld: Es prüft gegen den **ersten
Schritt**, nicht gegen das ganze Ergebnis. Ein Portal darf im Zielbild eines
Zweipersonenbetriebs stehen — als erster Schritt darf es das nicht.

---

## `runtime/` und `business_patterns/`

Wird zur Laufzeit gelesen:

| Datei | von wem |
|---|---|
| `business_patterns/*.yaml` | Interview, Betriebsart erkennen |
| `runtime/patterns/next_question_patterns.jsonl` | Rückfragen |
| `runtime/solution_knowledge/solution_workflows.jsonl` | zweiter Index |

## `archive/curated/`

Der ältere Diagnosekorpus. Er geht in `data/vector_index/` und wird von
`scripts/build_index.py` gelesen — nicht direkt zur Laufzeit.

## `examples/`

Ein vollständiges, gespeichertes Ergebnis. `/beispiel/hausverwaltung` zeigt es
**ohne jeden Modellaufruf** — die Rückfallebene für eine Vorführung ohne Netz.
