# Wissensbasis

Die Wissensdateien sind nach ihrem aktuellen technischen Status getrennt. Die
Einordnung beschreibt keine neue fachliche Integration.

## Struktur

```text
knowledge/
├── README.md
├── runtime/
│   ├── recommendation_catalog.json
│   └── patterns/next_question_patterns.jsonl
├── candidates/
│   ├── diagnostic_patterns_rb03.jsonl
│   ├── legal_guardrails.jsonl
│   └── batch_09/
├── evaluation/
│   ├── expected_labels.json
│   └── cases_*.json
└── archive/
    ├── curated/
    ├── raw/
    ├── notes/
    └── research_batches/
```

## `runtime/`

Hier liegen ausschließlich Dateien, die das Produkt direkt lädt:

- `recommendation_catalog.json`: validierter Katalog mit zwölf
  Problemfamilien, zehn Solution Patterns, GAI-01 bis GAI-09, GATE-01 bis
  GATE-06, FAIL-01 bis FAIL-12 und Autonomiestufen A0 bis A5; geladen durch
  `app/recommendation_service.py`.
- `patterns/next_question_patterns.jsonl`: direkt geladene Fragevorlagen;
  verwendet durch `app/agent_service.py` und als eine Quelle des bestehenden
  Agent-Pattern-Korpus.

## `candidates/`

Diese Dateien sind fachlich relevant, aber nicht als neue Produktquelle
integriert und nicht indexiert:

- `diagnostic_patterns_rb03.jsonl`: 49 Diagnosemuster aus Research Batch 03.
- `legal_guardrails.jsonl`: zwölf rechtliche Leitplanken aus Batch 03.
- `batch_09/`: vollständige unveränderte Research-Lieferung mit 27 Inference
  Patterns, 28 Workflows, 10 Output-Strukturen, 30 Evaluationen und 20 Quellen.
  Die Lieferung wurde formal und stichprobenartig fachlich geprüft, ist aber
  noch keine Runtime-Quelle. Reviewstatus und Grenzen stehen in
  `docs/BATCH_09_FACHPRUEFUNG.md`.

## `evaluation/`

`expected_labels.json` und die vier Dateien `cases_*.json` bilden zusammen 91
Test- und Demo-Fälle. Sie sind ausschließlich für Evaluation und Demo-Fixtures
bestimmt und dürfen niemals indexiert werden. `scripts/evaluate.py` und die
Demo-Route lesen sie direkt; sie sind kein Produktwissen.

## `archive/`

- `curated/`: drei kuratierte Korpora des bisherigen Diagnosewissens.
- `raw/`: unveränderte Ausgangsquellen und Belege.
- `notes/`: frühere Architektur-, Inventar- und Evaluationsnotizen.
- `research_batches/`: vollständige Research-Batches 02 bis 08 einschließlich
  Quellenregistern, Quality Gates und historischen Evaluationen.

`archive/` ist keine neue fachliche Runtime-Quelle. Es ist derzeit jedoch noch
nicht technisch unbenutzt: `app/rag_service.py` lädt für Reproduzierbarkeit und
Übergangskompatibilität weiterhin die archivierten kuratierten Korpora sowie
freigegebene Dateien aus Batch 02, 03 und 04, falls Diagnose- oder
Agent-Pattern-Indizes gebaut beziehungsweise geprüft werden. Auch
`scripts/merge_catalog_v2.py` liest seine historischen Merge-Quellen dort.

## Bestehende FAISS-Indizes

Die produktiven Artefakte unter `data/vector_index/` und
`data/agent_pattern_index/` wurden bei dieser Umordnung weder verschoben noch
neu gebaut. Der bestehende Diagnoseindex bleibt vorübergehend lauffähig, basiert
aber weiterhin auf dem bisherigen Korpus, dessen Quellen jetzt unter
`archive/` liegen. Eine spätere Batch-09-Prüfung und ein ausdrücklich
freigegebener Ersatz oder Neubau sind getrennte Vorhaben und nicht Teil dieser
Änderung.

Evaluationsdateien bleiben durch explizite Allow-Lists und verbotene
Indexmarker außerhalb beider Indizes.
