# Plan für Diagnose- und Agenten-RAG

**Status:** Superseded
**Hinweis:** Historischer Umsetzungsplan. Der aktuelle Zustand steht in `docs/ARCHITECTURE.md` und `docs/PROJECT_STATE.md`; offene Arbeit steht in `docs/ROADMAP.md`.

## Zielbild

Es werden zwei logisch und physisch getrennte Indizes verwendet:

1. Der Diagnoseindex enthält geeignete Chunks aus `knowledge/curated/`, Batch 02
   und `batch_03_diagnostic_depth/02_rag_corpus.jsonl`.
2. Der Agent-Pattern-Index enthält optional abrufbare Patterns aus den Batch-04-
   Dateien 02 bis 06 und 08.

Evaluationen, Research-Berichte, Coverage-Matrizen, Quellenregister, State-Dokument
und Merge-Gates gelangen in keinen Index.

## Einheitliches Metadatenschema

Jeder indexierbare Chunk behält mindestens:

- `chunk_id`, `chunk_type`, `batch_id`
- `source_ids`, `source_strength`, `content_origin`, `is_primary_evidence`
- `industry`, `process_type`, `digital_maturity_level`
- `pattern_ids`, `guardrail_ids`
- alle zusätzlichen Originalmetadaten

Fehlende Altmetadaten werden nicht erfunden: unbekannte Werte werden als
`unknown` oder `not_assessed` gekennzeichnet. URLs beziehungsweise vorhandene lokale
Quellenreferenzen werden als `source_ids` erhalten.

## Auswahl Diagnoseindex

Aufgenommen werden die 111 kuratierten Chunks, alle 162 Batch-02-Chunks und alle
361 Chunks aus Batch 03 Datei 02. Der separate Batch-03-Pattern-Katalog wird nicht
zusätzlich aufgenommen, weil er eine kompakte zweite Darstellung bereits im
RAG-Korpus enthaltener generalisierter Muster ist. Die 12 Legal Guardrails bleiben
Dokumentations- und Prüfmaterial; sie werden ohne eigene Aktualisierungsroutine
nicht als dauerhafte Produktwahrheit indexiert.

Retrieval bevorzugt bei Reifegrad 0–1 Minimalverbesserungen, Voraussetzungen und
Ordnung vor Automationsmustern. Niedrige Quellenstärke darf nie allein eine
Empfehlung tragen. Maximal zwei Fallbelege je Muster bleiben zulässig.

## Auswahl Agent-Pattern-Index

Optional abrufbar sind `agent_decision_pattern`, `next_question_pattern`,
`contradiction_pattern`, `agent_stop_rule`, `tool_selection_pattern` und
`agent_guardrail`. Retrieval ergänzt nur die deterministische Policy. Es entscheidet
nie allein über Budgets, Wiederholungen, Schutz bestätigter Fakten oder Schleifen.

## Dublettenprüfung

Vor jedem Build werden doppelte IDs, normalisierte exakte Inhaltsdubletten und
Near-Duplicates innerhalb desselben Chunk-Typs geprüft. Fachlich ähnliche
Sicherheitsregeln bleiben zulässig, wenn Auslöser oder Fallbacks verschieden sind.
Der Batch-03-Pattern-Katalog wird als bekannte strukturelle Überlappung ausgeschlossen.

## Sicherer Build und Austausch

Zuerst entstehen `data/vector_index_test/` und `data/agent_pattern_index_test/`.
Integritätstests prüfen Chunkzahlen, Metadaten, FAISS-`ntotal`, Retrieval-Typvielfalt
und den Ausschluss sämtlicher Evaluationen. Erst nach erfolgreichen Vergleichstests
wird der bisherige Index unverändert nach
`data/vector_index_backup_pre_batch04/` kopiert und der getestete Diagnoseindex
atomar nach `data/vector_index/` übernommen. Der Agent-Index wird separat unter
`data/agent_pattern_index/` veröffentlicht.

## Abbruchbedingungen

Der Build bricht ab bei Evaluationspfaden, `NEVER_INDEX`, doppelten Chunk-IDs,
fehlenden Pflichtmetadaten, abweichenden Vektor-/Metadatenzahlen oder einem nicht
lesbaren Testindex. Der vorhandene Produktionsindex bleibt dann unverändert.

## Ausführungsergebnis

Der Plan wurde am 26. Juli 2026 ausgeführt. Die Diagnoseprüfung ergab 634 Datensätze
ohne doppelte IDs, exakte Inhaltsdubletten oder Near-Duplicates beim Schwellwert
0,92. Der Agent-Korpus ergab 205 Datensätze ohne doppelte IDs oder exakte
Inhaltsdubletten und 66 fachlich ähnliche Paare; sie betreffen absichtlich eng
verwandte ASK- und Guardrail-Auslöser und wurden nicht automatisch entfernt.

Beide Testindizes bestanden Hash-, Metadaten- und FAISS-Prüfung. Alle 111 bisherigen
Chunk-IDs blieben erhalten. Drei Vergleichsabfragen zu Papierzettel/Regalsuche,
Mehrkanal-Terminen und menschlicher Preisfreigabe lieferten passende Diagnose- und
Guardrail-Treffer. Danach wurden die Testindizes promotet und der 111er-Altindex
gesichert. Niedrige Quellenstärke wird im Retrieval deterministisch herabgewichtet.
