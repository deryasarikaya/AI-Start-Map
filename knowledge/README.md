# AI Start Map Knowledge

## Ordner

- `raw/`: unveränderte Ausgangsquellen zur Kontrolle und Nachvollziehbarkeit.
- `curated/`: semantisch getrennte RAG-Chunks mit stabilen IDs und Metadaten.
- `evaluation/`: erwartete Ergebnisse und verbotene Empfehlungen für Tests. Nicht indexieren.

## Dateien für den ersten FAISS-Index

Nur diese Dateien indexieren:

- `curated/ten_cases_rag_corpus.md`
- `curated/massage_rag_corpus.md`
- `curated/additional_kmu_rag_corpus.md`

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
