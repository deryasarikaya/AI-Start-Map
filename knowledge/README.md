# AI Start Map Knowledge

**Status:** Needs Review
**Hinweis:** Ordnerübersicht und Provenienz bleiben relevant. Aussagen zum aktuellen Indexstand sind gegen `docs/ARCHITECTURE.md`, `docs/PROJECT_STATE.md` und die produktiven Manifeste zu prüfen. Dieses Dokument ist kein Ersatz für das zentrale Register `docs/INDEX.md`.

## Ordner

- `raw/`: unveränderte Ausgangsquellen zur Kontrolle und Nachvollziehbarkeit.
- `curated/`: semantisch getrennte RAG-Chunks mit stabilen IDs und Metadaten.
- `evaluation/`: erwartete Ergebnisse und verbotene Empfehlungen für Tests. Nicht indexieren.
- `research_batches/`: getrennte Forschungsstände, die vor einer Übernahme geprüft, bereinigt und freigegeben werden müssen.

## Research-Batches

- `batch_02_analog_reality/`: 162 fallbezogene Chunks im produktiven Diagnoseindex.
- `batch_03_diagnostic_depth/`: 361 Chunks im produktiven Diagnoseindex; 49 Pattern-Katalogeinträge, 12 Legal Guardrails und 14 Evaluationen bleiben getrennte Prüf- und Dokumentationsdateien.
- `batch_04_agentic_interview/`: 205 Entscheidungs-, Frage-, Klärungs-, Stop-, Tool- und Guardrail-Patterns im separaten Agent-Pattern-Index sowie 40 niemals indexierte Evaluationen.

Die Research-Dateien werden über explizite Allow-Lists geladen. Evaluationsdateien sind immer getrennt und mit `NEVER_INDEX` zu behandeln.

## Produktive FAISS-Indizes

Diagnoseindex mit 634 Chunks:

- `curated/ten_cases_rag_corpus.md`
- `curated/massage_rag_corpus.md`
- `curated/additional_kmu_rag_corpus.md`
- `research_batches/batch_02_analog_reality/02_rag_corpus.jsonl`
- `research_batches/batch_03_diagnostic_depth/02_rag_corpus.jsonl`

Separater Agent-Pattern-Index mit 205 Patterns:

- Batch 04, Dateien `02` bis `06` sowie `08`

Nicht indexieren: `raw/`, `evaluation/`, alle Batch-Evaluationen, Reports, Spezifikationen, Quellenregister, Coverage-Matrizen, Merge-Gates, Batch-03-Pattern-Katalog und Legal-Guardrail-Datei sowie das Batch-04-State-Schema.

## Chunk-Typen

- `case_evidence`: nur quellenbasierter Ist-Prozess und belegter Engpass.
- `diagnostic_pattern`: fachlich generalisiertes Prozessmuster.
- `interview_question_set`: noch notwendige Rückfragen.
- `automation_pattern`: möglicher Zielablauf, keine bereits umgesetzte Lösung.
- `automation_guardrail`: Grenzen und menschliche Freigaben.

## Verbindliche Retrieval-Regeln

1. Maximal zwei `case_evidence`-Chunks je `pattern_id` in einem Retrieval-Ergebnis.
2. Zusätzlich mindestens einen passenden `diagnostic_pattern`-Chunk laden.
3. Zusätzlich mindestens einen passenden `automation_guardrail`-Chunk laden.
4. Fragen gezielt aus `interview_question_set` abrufen.
5. Quellenfälle sind Vergleichsmuster. Keine Mengen, Tools, Abläufe, Risiken oder Geschäftsdaten als Nutzerfakten übernehmen.
6. `evaluation/evaluation_cases.json` niemals in den produktiven Vektorindex aufnehmen.

## Bewertungslogik

Nutzen, Häufigkeit, Standardisierbarkeit, Datenreife, Integrationsaufwand, Datenschutz und menschliche Entscheidung werden hybrid und evidenzbasiert anhand transparenter Rubrics und belegter Eingaben bewertet. Eine regelbasierte Formel darf nur mit nachvollziehbar erhobenen Eingaben arbeiten.
