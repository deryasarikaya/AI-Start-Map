# Qualitätsprüfung und Merge-Gate – Research-Batch 03

## Validierter Umfang

- 46 neue Fall-IDs (`RB03-C01` bis `RB03-C46`)
- 361 RAG-Chunks mit getrennten Fakten, Fragen, Minimalverbesserungen, Automation und Guardrails
- 18 generalisierte Diagnosemuster, 12 Prozessmuster, 5 Reifegradmuster
- 10 Implementierungsvoraussetzungen und 4 Priorisierungsmuster
- 12 versionierbare Rechts-/Datenschutz-Guardrails
- 14 separate Evaluationen; sie dürfen nicht indexiert werden

## Kategorien

- physische Annahme-/Reparaturfälle: 20 (Ziel mindestens 15)
- Außeneinsatzfälle: 15 (Ziel mindestens 10)
- Auftragsfertigung/Kleinproduktion: 19 (Ziel mindestens 10)

Kategorien überlappen bewusst. Ein Reparaturbetrieb kann zugleich Außendienst oder Kleinproduktion sein.

## Quellenprofil

- hoch: 30
- mittel: 15
- niedrig: 1

`is_primary_evidence=true` bedeutet öffentliche Selbstauskunft einer beteiligten Betriebs-/Mitarbeitendenperson oder offizielle Unternehmens-/Projektbeschreibung, nicht unabhängige Prüfung. Anbieterfälle und sekundäre Berichte sind gesondert markiert.

## Chunk-Profil

- `automation_guardrail`: 46
- `automation_pattern`: 46
- `case_evidence`: 46
- `diagnostic_pattern`: 64
- `diagnostic_question_set`: 64
- `digital_readiness_pattern`: 5
- `implementation_prerequisite`: 10
- `minimal_viable_improvement`: 64
- `prioritization_pattern`: 4
- `process_pattern`: 12

## Merge-Gate

Vor Zusammenführung mit Batch 01/02:

1. URLs und semantische Fallnähe erneut gegen bestehende Korpora prüfen.
2. `batch_id`, `source_strength`, `content_origin`, `company_size` und `is_primary_evidence` erhalten.
3. Fälle mit `company_size=small_25` nur ergänzend verwenden; sie zählen nicht zum Kernsegment 1–20.
4. `source_strength=low` ausschließlich für Hypothesen/Rückfragen zulassen.
5. Maximal zwei `case_evidence` je Pattern; zusätzlich Frage-/Diagnosechunk und Guardrail laden.
6. Bei Reifegrad 0–1 `minimal_viable_improvement` vor `automation_pattern` ranken.
7. Arbeitsumgebung (`smartphone`, `dirty`, `noisy`, `mobile`, `offline`) als Retrievalfilter berücksichtigen.
8. Evaluation und Legal-Update-Log nie in denselben produktiven Fallindex mischen.

## Spezifische Retrieval-Regeln

- Quellenfälle sind Vergleichsmuster; keine Mengen, Tools, Risiken oder Abläufe als Nutzerfakten übernehmen.
- Objekt-ID, physischer Ort, Status, verantwortliche Person und Freigabe werden getrennt geprüft.
- Bei Preis, Zusatzarbeit, Termin, Zahlung, Vertrag, Qualität, Abholung oder Personal ist menschliche Freigabe zwingend.
- Schwache Quellen nie allein als Begründung einer Empfehlung.
- Bei fehlender digitaler Grundlage zuerst Ordnung/Standardisierung, nicht KI empfehlen.

## Bekannte Restlücken

- Ein öffentliches Vor-Ort-Primärinterview eines klassischen lokalen Schuhmachers mit Regal-, Zettel- und Drittabholprozess wurde nicht gefunden. Shoedoc belegt einen realen deutschen Schuhreparaturprozess, aber nicht alle analogen Detailprobleme.
- Drittabholung wird stark durch Trommel-, Schmuck- und allgemeine Abholfälle belegt, jedoch nicht durch einen deutschen Schuhmacher-Primärbericht.
- Deutsche Rechtsfragen zu Eigentum, Lagergebühr, Verwertung und Abholung sind bewusst nicht abschließend beantwortet und benötigen juristische Prüfung.
- Interview-Agent-Steuerung ist ausdrücklich nicht Teil dieses Batchs; dafür ist `batch_04_agentic_interview` vorgesehen.
