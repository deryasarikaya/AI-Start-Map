# Batch 03 – Diagnostic Depth

Dieser Ordner ist ein eigenständiger Research-Batch für AI Start Map.

## Dateien

- `01_research_report.md`: lesbarer Forschungsbericht mit allen Fällen
- `00_research_specification.md`: verbindlicher Scope, Quellenstandard und Ausschlüsse
- `02_rag_corpus.jsonl`: produktionsnah getrennte RAG-Chunks
- `03_source_register.csv`: Quellen, Herkunft und Belegstärke
- `04_pattern_catalog.jsonl`: Diagnose-, Prozess-, Reifegrad-, Voraussetzung- und Priorisierungsmuster
- `05_legal_guardrails.jsonl`: aktuelle deutsche/EU-Primärquellen und Produktgrenzen
- `06_evaluation_cases.json`: separate Tests, nicht indexieren
- `07_coverage_matrix.csv`: Fall- und Lückenabdeckung
- `08_quality_and_merge_gate.md`: Validierung, Retrieval-Policy und Merge-Bedingungen

## Index-Regel

Nicht ungeprüft mit den 111 oder 162 bestehenden Chunks mischen. Vorher semantische Deduplizierung, Metadaten-Mapping und technische Kompatibilitätsprüfung durchführen.

## Abgrenzung zum geplanten Interview Agent

Dieser Batch liefert offene fachliche Prozessinformationen, aber keine Dialog- oder Auswahlpolicy. Welche Frage der Interview Agent als Nächstes auswählt, wann er stoppt und wie er Widersprüche gewichtet, wird separat in `batch_04_agentic_interview` recherchiert.
