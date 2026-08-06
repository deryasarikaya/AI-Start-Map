# RAG-Inventar

**Status:** Needs Review
**Hinweis:** Historisches Inventar vom 26. Juli 2026. Aktuelle Laufzeitaussagen und Indexstände sind gegen `docs/ARCHITECTURE.md`, `docs/PROJECT_STATE.md` und die jeweiligen Manifeste zu prüfen.

Stand: 26. Juli 2026. Dieses Inventar trennt produktives Wissen, Research und Evaluation.

## Kuratierter Ausgangsbestand

Der bestehende Markdown-Loader liest ausschließlich `knowledge/curated/*.md`:

| Datei | Chunks |
|---|---:|
| `ten_cases_rag_corpus.md` | 40 |
| `massage_rag_corpus.md` | 8 |
| `additional_kmu_rag_corpus.md` | 63 |
| Gesamt | 111 |

Chunk-Typen: 29 `case_evidence`, 25 `interview_question_set`, 25
`automation_guardrail`, 24 `automation_pattern` und 8 `diagnostic_pattern`.
Der vor dem Merge verwendete FAISS-Index enthielt ebenfalls 111 Vektoren und war
mit diesem Korpus synchron. Er liegt jetzt unter
`data/vector_index_backup_pre_batch04/` als Sicherung.

## Aktueller Produktionsstand

Der produktive Diagnoseindex unter `data/vector_index/` enthält 634 Vektoren:
111 kuratierte Chunks, 162 Chunks aus Batch 02 und 361 Chunks aus Batch 03. Der
separate Agent-Pattern-Index unter `data/agent_pattern_index/` enthält 205
Batch-04-Patterns. Beide Manifeste verwenden `text-embedding-3-small`, stimmen mit
FAISS und Metadaten überein und tragen `excluded_evaluations=true`.

## Research-Batch 02

Batch 02 enthält 35 Quellenfälle, 35 Quellenregisterzeilen und 162 JSONL-Chunks:
35 Fallbelege, 38 Fragemuster, 38 Guardrails, 35 Minimalverbesserungen sowie 16
weitere Prozess-, Reifegrad-, Voraussetzung- und Risikomuster. 22 generalisierte,
als `expert_derived` markierte Datensätze besitzen keine direkte URL. Es gibt keine
separate Evaluationsdatei.

## Research-Batch 03

Batch 03 enthält 46 Quellenfälle und 361 RAG-Chunks: je 46 Fallbelege,
Automationsmuster und Guardrails, je 64 Diagnosemuster, Fragesets und
Minimalverbesserungen sowie 31 Reifegrad-, Prozess-, Voraussetzung- und
Priorisierungsmuster. Hinzu kommen ein separater Katalog mit 49 Patterns, 12 Legal
Guardrails und 14 Evaluationen. Die 49 Katalogeinträge überlappen fachlich mit den
generalisierten Einträgen des RAG-Korpus und werden deshalb nicht zusätzlich in den
Diagnoseindex aufgenommen.

## Research-Batch 04

Batch 04 enthält 205 maschinenlesbare Agenten-Patterns: 60 Entscheidungen, 40
Fragemuster, 25 Widerspruchsmuster, 25 Stop-Regeln, 25 Tool-Muster und 30
Guardrails. Alle 205 Datensätze referenzieren gültige Einträge des Registers mit 40
Quellen. Hinzu kommen State-Modell, Coverage-Matrix, Merge-Gate und 40 getrennte
Evaluationen. Das Gate lautet `READY WITH CONDITIONS`.

## Evaluationen: niemals indexieren

| Datei | Fälle | Trennung |
|---|---:|---|
| `knowledge/evaluation/evaluation_cases.json` | 25 | eigener Ordner und Zweckhinweis |
| `batch_03_diagnostic_depth/06_evaluation_cases.json` | 14 | separate Datei; README/Gate verbieten Indexierung |
| `batch_04_agentic_interview/09_evaluation_cases.json` | 40 | `indexing_policy=NEVER_INDEX` |

Keine Evaluations-ID kommt in einem vorgesehenen Wissens- oder Pattern-Korpus vor.

## Architektur vor dem Merge

`scripts/build_index.py` lädt bisher nur den kuratierten Markdown-Korpus. Der Loader
kennt weder JSONL noch die erweiterten Batch-Metadaten. Speicherung und Laden
verwenden `data/vector_index/{knowledge.faiss,chunks.json,manifest.json}` und ein
normalisiertes `IndexFlatIP`. Retrieval erzwingt je Phase erlaubte Typen, Typvielfalt
und höchstens zwei Fallbelege je Muster. Das konfigurierte Embedding-Modell ist
`text-embedding-3-small`.

Die bestehende Rückfragelogik erzeugt per Structured Output null bis vier Fragen in
einem Aufruf und zeigt sie einzeln. Sie besitzt noch keinen expliziten Agent-State,
keine Aktionen `ASK/CLARIFY/RETRIEVE/ANALYZE/STOP` und keine zentralen Tool- oder
Rundenbudgets.

Dieser Ausgangspunkt wurde erweitert: JSONL-Loader, einheitliches Metadatenschema,
zwei getrennte Indizes, zentral konfigurierte Budgets und der explizite Agent-State
sind jetzt implementiert. Die fünf Datenbanktabellen blieben unverändert.

## Datenqualität und bekannte Abweichungen

- Alle Primär-IDs der kuratierten Basis und der drei Batches sind eindeutig.
- Alle JSON-, JSONL- und CSV-Dateien sind syntaktisch valide.
- 85 generalisierte Batch-03-Chunks und 22 generalisierte Batch-02-Chunks besitzen
  bewusst keine direkte Fall-URL; ihre Herkunft lautet `expert_derived`.
- Fünf kuratierte Massage-Fallbelege referenzieren eine vorhandene lokale PDF im
  Feld `source_url`.
- Konkrete Frage-, Agenten- und Toolbudgets sind Projektheuristiken. Sie müssen mit
  echten AI-Start-Map-Interviews kalibriert werden.
