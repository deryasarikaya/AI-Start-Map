# Architektur

**Last Updated:** 2026-08-05

Diese Datei beschreibt die verifizierte aktuelle Architektur und trennt sie ausdrücklich von der geplanten Zielarchitektur.

## Sichtbarer Nutzerflow

```text
Landingpage
→ freie Erzählung per Text oder optionaler Browser-Spracherkennung
→ OpenAI-Prozesserkennung und höchstens drei Prozessoptionen
→ Auswahl eines Prozesses
→ kurze Ist-Zusammenfassung mit vertikaler HTML-/CSS-Prozesslinie
→ Bestätigung oder Korrektur
→ Python-Agentenentscheidung
→ optional einzelne relevante Rückfrage(n)
→ sichtbare Analyseverarbeitung
→ Diagnose-Retrieval und finale Structured-Output-Analyse
→ Ergebnis
→ optional Startplan, Details, Druck/PDF und Mailkontakt
```

Die öffentliche Journey nutzt ein signiertes Sitzungscookie. Die interne numerische Session-ID wird nicht im sichtbaren Seiteninhalt und nicht in den öffentlichen URLs verwendet.

## Backend-Komponenten

| Komponente | Zuständigkeit |
|---|---|
| `app/main.py` | FastAPI-Anwendung, statische Dateien, Router und 404-Handler |
| `app/routes.py` | HTTP-Flow, Sessionzugriff, Orchestrierung von Agent, Retrieval, OpenAI, Persistenz und Templates |
| `app/questions.py` | Feste Einführungs- und Prozessfragen |
| `app/agent_config.py` | Zentrale Rückfrage-, Agenten- und Toolbudgets |
| `app/agent_service.py` | Getrennter Process State, drei interne Werkzeuge und deterministische Aktionsentscheidung |
| `app/rag_service.py` | Korpusladen, Indexbau/-validierung, FAISS-Retrieval, Ranking und Promptbereinigung |
| `app/openai_service.py` | OpenAI Structured Outputs, Embeddings, Prompts, Normalisierung und Grounding |
| `app/schemas.py` | Pydantic-Schemas und sichtbare Sicherheits-/Qualitätsvalidierung |
| `app/models.py` | SQLAlchemy-Modelle der fünf Tabellen |
| `app/database.py` | PostgreSQL-Engine und SessionFactory |
| `app/templates/` | Serverseitig gerenderte Nutzerreise, Ergebnis und Bericht |
| `app/static/` | Gemeinsame Browserinteraktionen, Spracheingabe, Responsive- und Print-CSS |

## Aktuelle Ablaufsteuerung

Nach der Prozessbestätigung rekonstruiert `_diagnostic_agent_state()` aus Prozesswahl und gespeicherten Antworten einen `ProcessState`. Danach läuft die aktuelle Entscheidungskette:

```text
extract_process_state()
→ evaluate_readiness_and_next_action()
→ ASK / CLARIFY / RETRIEVE / ANALYZE / STOP
```

Bei `RETRIEVE` ruft `search_diagnostic_knowledge()` den produktiven Diagnoseindex auf. Der State wird mit getrennt gespeicherter `RagEvidence` erneut bewertet. Bei `ASK` oder `CLARIFY` kann `generate_follow_up_questions()` Kandidaten erzeugen; Python filtert Wiederholungen, irrelevante Fragen und Budgetüberschreitungen. `ANALYZE` beziehungsweise ein analysierbarer `STOP` führt zur Processing-Seite und finalen Analyse.

Die finale Analyse läuft über:

```text
_generate_and_persist_final_analysis()
→ _retrieval_context(..., "analysis")
→ _diagnostic_agent_state()
→ generate_final_analysis()
→ FinalAnalysisResult-Validierung
→ _validate_final_grounding()
→ _persist_final_analysis()
→ _result_view()
```

## Diagnose-RAG

### Quellen und Indizes

- Produktiver Diagnoseindex: `data/vector_index/`.
- Manifest: 634 Chunks, `text-embedding-3-small`, Evaluationen ausgeschlossen.
- Quellen: kuratierte Markdown-Korpora sowie die explizit erlaubten Batch-02- und Batch-03-`02_rag_corpus.jsonl`-Dateien.
- Produktiver Agent-Pattern-Index: `data/agent_pattern_index/`.
- Manifest: 205 Patterns, `text-embedding-3-small`, Evaluationen ausgeschlossen.

`app/rag_service.py` verwendet explizite Allow-Lists. Pfade oder Inhalte mit `evaluation`, `evaluation_cases` oder `never_index` werden abgewiesen. Testindizes werden getrennt gebaut und erst nach Validierung bewusst promoviert.

### Laufzeit-Retrieval

`retrieve_chunks()`:

1. lädt FAISS-Index und `chunks.json`,
2. erzeugt ein Query-Embedding,
3. normalisiert den Vektor,
4. führt eine FAISS-Ähnlichkeitssuche aus,
5. filtert Chunk-Typen passend zur Phase `suggestion`, `follow_up` oder `analysis`,
6. berücksichtigt Quellenstärke,
7. erzwingt eine diverse Auswahl,
8. entfernt über `format_chunks_for_prompt()` interne IDs, YAML-Metadaten, URLs und Quellenmarker.

RAG-Evidenz wird im Agentenstate als eigener Typ geführt und niemals in bestätigte Nutzerfakten kopiert. Die OpenAI-Prompts trennen Nutzerfakten, internes Vergleichswissen, erlaubte Ableitungen und Empfehlungen in benannte Bereiche.

### Agent-Pattern-Index

`retrieve_agent_patterns()` kann den separaten Agent-Pattern-Index lesen und nach erlaubten Pattern-Typen filtern. Eine Repository-Suche bestätigt jedoch ausschließlich die Funktionsdefinition; es gibt keinen Laufzeitaufruf. Der Index beeinflusst die aktuelle Aktionsentscheidung nicht.

Die Fragevorlagen aus `knowledge/research_batches/batch_04_agentic_interview/03_next_question_patterns.jsonl` werden direkt durch `question_templates()` gelesen. Dies ist von semantischem Agent-Pattern-Retrieval zu unterscheiden.

## Agentenlogik

### Aktuell: Python-Regeln plus interne Python-Funktionen

Die aktuelle Agentenlogik ist ein begrenzter, überwiegend deterministischer Controller. `evaluate_readiness_and_next_action()` prüft unter anderem:

- autonome Ausführungswünsche,
- Nutzerwunsch zu stoppen,
- No-Repeat,
- Rückfrage-, Agenten- und Toolbudgets,
- wiederholte Tool-Signaturen,
- Widersprüche,
- fehlende Prozessgrenzen und Ist-Schritte,
- menschliche Freigaben bei kritischen Themen,
- verfügbare Daten und digitalen Reifegrad,
- Engpasskandidaten,
- Bedarf für Diagnose-Retrieval.

Sicherheitsregeln sind nicht vom semantischen Retrieval abhängig. Der aktuelle Agent ist kein frei planender LLM-Agent.

### Agentenwerkzeuge

Die drei Werkzeuge sind aktuell interne Python-Funktionen, keine über ein LLM aufgerufenen Function-Calling-Tools:

| Werkzeug | Aufgabe |
|---|---|
| `extract_process_state` | Rekonstruiert den typisierten State aus Prozesswahl, Antworten und Fragehistorie; trennt Fakten, Ableitungen, Widersprüche, Unsicherheiten und RAG-Evidenz. |
| `search_diagnostic_knowledge` | Ruft bereinigtes Diagnosewissen aus dem produktiven FAISS-Index ab und liefert `RagEvidence`. |
| `evaluate_readiness_and_next_action` | Wendet deterministische Regeln und Budgets an und liefert die nächste Aktion. |

## Datenhaltung

PostgreSQL enthält genau fünf Tabellen:

| Tabelle | Inhalt |
|---|---|
| `sessions` | technische Sitzung |
| `interview_questions` | feste und dynamische Fragen, Reihenfolge und Antworten |
| `process_options` | erkannte Prozessoptionen und genau eine Auswahl pro Session |
| `analyses` | Zusammenfassung, Ist-/Soll-Schritte, Kernengpass, Unsicherheiten und variabler Kernoutput in JSONB |
| `automation_opportunities` | genau drei gerankte Chancen sowie variable Kategorie-, Test- und Blueprintdaten in JSONB |

Die Beziehungen verwenden echte Foreign Keys mit kaskadierendem Löschen. Das Schema wird durch Alembic verwaltet. Die Anwendung erzeugt keine Produktionstabellen über `Base.metadata.create_all()`.

Der Process State wird derzeit bei Bedarf aus den bestehenden Tabellen rekonstruiert; es gibt keine eigene persistierte Agent-State- oder Trace-Tabelle.

## OpenAI-Integration

`app/openai_service.py` verwendet:

- Structured Outputs für Prozessoptionen, benutzerdefinierte Prozessgrenzen, Prozessverständnis, Rückfragen und finale Analyse,
- Pydantic-Modelle als erwartete Ergebnisstruktur,
- Embeddings für Diagnose- und optionales Agent-Pattern-Retrieval,
- getrennte Timeouts für Standardanfragen, finale Analyse und Retrieval,
- Normalisierung, Kundensprachfilter und Grounding-Prüfungen.

Der finale Prompt verlangt die sichtbare Reihenfolge:

1. `core_problem`,
2. `first_change`,
3. `ai_support` plus Eingabe, Aufgabe, Ergebnis und menschliche Kontrolle,
4. `weekly_test` plus Erfolgskriterium,
5. `later_automation`.

Zusätzlich erzeugt er genau drei gerankte Opportunities und einen Blueprint für Rang 1. Empfehlungen dürfen nicht rückwirkend als heutiger Ablauf dargestellt werden.

Es existiert kein echtes OpenAI Function Calling. Das Modell erhält Daten und internes Vergleichswissen als strukturierte Prompt-Payload, ruft aber keine Agentenwerkzeuge selbst auf.

## PDF-Erstellung

`app/templates/report.html` rendert normalerweise drei HTML-Berichtsseiten. `app/static/styles.css` enthält Print-Regeln. Der Browser öffnet mit `window.print()` den Druckdialog; der Nutzer speichert dort selbst als PDF.

Es gibt keine serverseitige PDF-Bibliothek. Der `mailto:`-Kontakt hängt den Bericht nicht automatisch an und behauptet dies auch nicht.

## Evaluationen und Tests

- Produkt-Evaluationen liegen getrennt unter `knowledge/evaluation/`.
- Batch-spezifische Evaluationen liegen in den Research-Batches und werden nicht indexiert.
- Das Repository dokumentiert und testet insgesamt 79 getrennte Evaluationen außerhalb der Indizes.
- `tests/test_agent_architecture.py` prüft Korpustrennung, Indexausschluss, Agentenpolicy, Budgets und Evidenztrennung.
- `tests/test_analysis_flow.py` prüft Journey, RAG-Bereinigung, Persistenz, Opportunities und Blueprint.
- `tests/test_product_finalization.py` prüft Kernoutput, konkrete KI-Hilfe, Reifegradfälle und Berichtsstruktur.
- `tests/test_quality_pass.py` prüft Grounding, menschliche Freigaben, Prompttrennung und Qualitätsfälle.
- `tests/test_ux_journey.py` prüft die vollständige sichtbare Journey und den Kundenbericht.
- Letzter vollständiger Lauf am 2026-08-05: 83 Tests bestanden.

## Aktuelle Architektur

```text
Jinja2/FastAPI UI
→ Python-Routen
→ deterministische Agentenregeln
→ interne Python-Funktionen
→ aktives Diagnose-RAG
→ OpenAI Structured Output
→ Pydantic- und Grounding-Validierung
→ PostgreSQL
→ HTML-Ergebnis und Browser-PDF
```

Kernmerkmal: **Python-Regeln plus interne Python-Funktionen.** Der separate Agent-Pattern-Index ist gebaut, aber nicht in die Laufzeitentscheidung eingebunden.

## Geplante Zielarchitektur

```text
Jinja2/FastAPI UI
→ persistierter, nachvollziehbarer Agentenstate
→ begrenzter LLM-Interview-Agent
→ echtes Function Calling für typisierte Werkzeuge
→ Diagnose-RAG plus kontrolliertes Agent-Pattern-Retrieval
→ strukturierte Symptom-, Ursachen- und Problemfamilienklassifikation
→ Diagnose-RAG für Problem- und Bedingungsevidenz
→ strukturierter Solution-Pattern-Katalog
→ deterministische Applicability- und Exclusion-Gates
→ Recommendation-Auswahl außerhalb eines zufälligen semantischen Top-k
→ Pydantic-/Guardrail-Validierung
→ Observability und Tracing
→ PostgreSQL und Kundenausgabe
```

Kernmerkmal: **LLM-Agent plus echtes Function Calling und Agent-Pattern-Retrieval.** Diese Zielarchitektur ist geplant, aber nicht implementiert. Deterministische Sicherheits-, Budget- und Faktenregeln bleiben auch in der Zielarchitektur verbindlich.

Für den Recommendation Layer ist als erster geplanter Schritt ausdrücklich kein neuer Solution-FAISS-Index vorgesehen. Die zwölf Problemfamilien und zehn Solution Patterns sollen strukturiert repräsentiert werden. Diagnose-RAG liefert Evidenz zu Problem, Ursache und Bedingungen; der Katalog liefert Kandidaten. Vorgangsanker, Kanaleignung, Prozess-/Datenreife, Risiko, Regelstabilität und menschliche Freigabe begrenzen und priorisieren diese Kandidaten deterministisch. Exakte Integrationspunkte, Schemas und Aufrufketten sind noch technisch zu verifizieren.
