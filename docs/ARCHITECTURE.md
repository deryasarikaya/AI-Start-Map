# Architektur

**Last Updated:** 2026-08-07

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
→ Diagnose-Retrieval, gated Solution-Auswahl und finale Structured-Output-Analyse
→ eine Hauptlösung mit Ergebnisvorschau
→ optional Umsetzung, weitere Möglichkeiten, Details, Druck/PDF und Mailkontakt
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
| `app/recommendation_service.py` | Validiert den Recommendation-Katalog, hält den Keyword-Fallback, übersetzt Rohsignale in die begründete GATE-01…06-Kaskade und liefert A0 oder die deterministische Vorauswahl. |
| `app/solution_knowledge.py` | Validiert Batch-09-Output-Strukturen, Inference Patterns und Solution Workflows; entfernt Beispielwerte aus dem Laufzeitkontext und bietet deterministische Fallback-Auswahl. |
| `app/llm_classification.py` | Ordnet die bestätigte Erzählung per Structured Output Problemfamilien und bestehenden Gate-Werten zu; bei API-Fehlern nutzt es die unveränderte Keyword-/Gate-Heuristik als Fallback. |
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
→ classify_narrative()
  → Structured Output oder bei AIServiceError Keyword-/Gate-Fallback
→ _retrieval_context(..., "analysis")
→ _diagnostic_agent_state()
→ select_recommendation()
→ generate_final_analysis()
→ FinalAnalysisResult-Validierung
→ deterministische OUT-/Katalog-Anwendung
→ _validate_final_grounding()
→ _persist_final_analysis()
→ _result_view() mit kundensicherer Abbildung interner Katalog-IDs
```

## Diagnose-RAG

### Quellen und Indizes

- Produktiver Diagnoseindex: `data/vector_index/`.
- Manifest: 634 Chunks, `text-embedding-3-small`, Evaluationen ausgeschlossen.
- Quellenbasis des bestehenden Index: kuratierte Markdown-Korpora sowie die explizit erlaubten Batch-02- und Batch-03-`02_rag_corpus.jsonl`-Dateien; diese bisherigen Quellen liegen jetzt unter `knowledge/archive/`.
- Produktiver Agent-Pattern-Index: `data/agent_pattern_index/`.
- Manifest: 205 Patterns, `text-embedding-3-small`, Evaluationen ausgeschlossen.

`app/rag_service.py` verwendet explizite Allow-Lists. Pfade oder Inhalte mit `evaluation`, `evaluation_cases` oder `never_index` werden abgewiesen. Testindizes werden getrennt gebaut und erst nach Validierung bewusst promoviert.

Bei der vorherigen Umordnung wurden die damaligen produktiven FAISS-Artefakte nicht verändert. Der bestehende Diagnoseindex bleibt vorübergehend lauffähig, basiert jedoch weiterhin auf dem alten, archivierten Korpus. Die Archivquellen werden von den bisherigen Diagnose- und Agent-Pattern-Loadern für Kompatibilität und reproduzierbare Indexprüfungen noch gelesen. Ein Ersatz oder Neubau dieses Diagnoseindex ist weiterhin nicht integriert.

Der neue `data/solution_workflow_index/` ist davon getrennt. Er enthält 27 runtime-freigegebene Batch-09-Workflows; der dokumentarische SP-04-Ausschluss und alle Evaluationen fehlen. Das harte Filter ist ausschließlich das bereits deterministisch ausgewählte Solution Pattern. Betriebstyp und bestätigte Kanäle wirken nur als kleine Soft-Boosts. Der frühere unkalibrierte pauschale Source-Strength-Abzug wurde neutralisiert; Quellenstärke bleibt Metadatum.

### Laufzeit-Retrieval

`retrieve_chunks()`:

1. lädt FAISS-Index und `chunks.json` beim ersten Abruf je Indexverzeichnis in einen Prozess-Cache,
2. erzeugt ein Query-Embedding,
3. normalisiert den Vektor,
4. führt eine FAISS-Ähnlichkeitssuche aus,
5. filtert Chunk-Typen passend zur Phase `suggestion`, `follow_up` oder `analysis`,
6. berücksichtigt Quellenstärke,
7. reserviert in der Analyse je ein Diagnose-, Automations-, Voraussetzungs- und Guardrail-Muster und füllt danach divers auf,
8. entfernt über `format_chunks_for_prompt()` interne IDs, YAML-Metadaten, URLs und Quellenmarker.

Der Cache prüft vor jedem Abruf die mtimes von FAISS- und Metadatendatei. Bei
einer Änderung wird der betroffene Index neu geladen; fehlende Dateien und
inkonsistente Index-/Metadatenpaare behalten ihre bisherigen
`RagConfigurationError`-Pfade. Ein nach der Bereinigung leerer Chunk wird im
Diagnosewerkzeug übersprungen, ohne die Zuordnung der verbleibenden Chunks zu
verschieben.

`promote_test_indexes()` validiert vor dem Promote beide Test- und beide
Produktionsindizes. Anschließend sichert es den vollständigen Diagnose- und
Agentenindex getrennt unter `data/index_backups/<timestamp>/` und validiert die
promovierten Produktionsindizes erneut. Zeitstempel und Kollisionssuffix
verhindern das Überschreiben bestehender Backups; das historische Verzeichnis
`data/vector_index_backup_pre_batch04/` wird nicht verändert.

RAG-Evidenz wird im Agentenstate als eigener Typ geführt und niemals in bestätigte Nutzerfakten kopiert. Die OpenAI-Prompts trennen Nutzerfakten, internes Vergleichswissen, erlaubte Ableitungen und Empfehlungen in benannte Bereiche.

### Agent-Pattern-Index

`retrieve_agent_patterns()` liest im Interviewpfad den separaten Agent-Pattern-Index. `_agent_pattern_context()` begrenzt die Suche auf Entscheidungs-, Frage-, Widerspruchs-, Stop-, Werkzeug- und Guardrail-Muster und auf drei Treffer. Die bereinigten Inhalte unterstützen den Kontext einer tatsächlich zulässigen Rückfrage; bei Retrievalfehlern bleibt der deterministische Controller arbeitsfähig. Die Patterns ersetzen keine Python-Sicherheitsregel und wählen die finale Recommendation nicht.

Die Fragevorlagen aus `knowledge/runtime/patterns/next_question_patterns.jsonl` werden direkt durch `question_templates()` gelesen. Dies ist von semantischem Agent-Pattern-Retrieval zu unterscheiden. Weitere Quellen des bestehenden Agent-Pattern-Korpus liegen vorübergehend unter `knowledge/archive/research_batches/batch_04_agentic_interview/`.

Die 27 Batch-09-Inference-Patterns werden typisiert direkt geladen. Nach der semantischen Problemfamilienklassifikation können sie eine beobachtbare Rückfrage oder klar als unbestätigt markierten Fragekontext liefern. Sie werden weder in `confirmed_user_facts` kopiert noch als Ground Truth behandelt.

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
| `automation_opportunities` | eine primäre und null bis zwei optionale sekundäre Möglichkeiten; variable Präsentationsdaten in JSONB |

Die Beziehungen verwenden echte Foreign Keys mit kaskadierendem Löschen. Das Schema wird durch Alembic verwaltet. Die Anwendung erzeugt keine Produktionstabellen über `Base.metadata.create_all()`.

Der Process State wird derzeit bei Bedarf aus den bestehenden Tabellen rekonstruiert; es gibt keine eigene persistierte Agent-State- oder Trace-Tabelle.

## OpenAI-Integration

`app/openai_service.py` verwendet:

- Structured Outputs für die semantische Problemfamilien- und Gate-Klassifikation,
- Structured Outputs für Prozessoptionen, benutzerdefinierte Prozessgrenzen, Prozessverständnis, Rückfragen und finale Analyse,
- Pydantic-Modelle als erwartete Ergebnisstruktur,
- Embeddings für Diagnose- und optionales Agent-Pattern-Retrieval,
- getrennte Timeouts für Standardanfragen, finale Analyse und Retrieval; die finale Analyse hat 120 Sekunden Gesamtbudget, `medium` Reasoning und maximal zwei Versuche,
- feldbezogene Normalisierung und Grounding-Prüfungen, die einen betroffenen Wert neutralisieren, ohne die übrige Analyse zu verwerfen.

Der finale Prompt erhält neben Nutzerfakten, getrennten Ableitungen und Diagnosewissen die deterministische Recommendation-Auswahl einschließlich Gates, Stop Conditions, Failure Guardrails, OUT-Struktur und Workflowkontext. Er enthält 15 inhaltliche Kernregeln; Typen, Längen und Listenbegrenzungen bleiben im Pydantic-Schema. `recommendation-v3` ergänzt die bisherige Empfehlung um normale Software-/Regelaufgabe, offene Angaben, kleinste nutzbare Version, Nicht-Automationen und Autonomiestufe. OUT-Feldnamen, Human Review, Kataloggrenzen, Autonomiestufe und kleinste Version werden nach der Modellantwort deterministisch angewendet. Nicht belegte Vorschauwerte werden „noch offen“ oder klar als Beispiel markiert.

Der Legacy-Shim bleibt erforderlich, weil die lokal konfigurierte Anwendungsdatenbank 15 ältere `core_output`-Payloads enthält. Er protokolliert nur erfundene Platzhalter; die Kundensicht unterdrückt sie. Neue v3-Felder werden für alte Analysen nicht erzeugt. Es war keine Migration und keine neue Tabelle nötig.

Der Selector besitzt zusätzlich eine enge A0-Sicherung: Nennt der Nutzer ausdrücklich eine ausreichende vorhandene Funktion oder einfache Regel und dass keine KI nötig ist, kann eine vorgeschlagene Problemfamilie diese Entscheidung nicht wieder zu A1 machen. Für neue kanalübergreifende Anfragen mit verlorenem Status oder fehlenden Mindestangaben grenzt der semantische Prompt PF-02 ausdrücklich von reiner Mehrfachübertragung (PF-03) und Dokumentauslesung (PF-12) ab.

Es existiert kein echtes OpenAI Function Calling. Das Modell erhält Daten und internes Vergleichswissen als strukturierte Prompt-Payload, ruft aber keine Agentenwerkzeuge selbst auf.

## Ergebnisdarstellung

`app/templates/results.html` rendert den validierten Kernoutput in einer festen achtteiligen Leserichtung: Engpass, Empfehlung, Zukunftsablauf, konkretes Ergebnis, Human Check, kleinster Einstieg, Voraussetzungen und Grenzen sowie späterer Ausbau. Die Darstellung erfindet keine eigene fachliche Struktur, sondern verwendet die gespeicherten v3-Felder und unterdrückt Legacy-Shim-Platzhalter über die View-Abbildung. `app/static/styles.css` begrenzt Text auf ungefähr 72 Zeichen, hält den Ablauf vertikal und stapelt Rollen und Aktionen auf schmalen Viewports.

`_result_view()` bildet interne SP-Titel aus bereits gespeicherten Analysen auf den freigegebenen Katalognamen ab und normalisiert begrenzte direkte Rollenformulierungen. PF-, SP-, OUT- und Sitzungskennungen bleiben außerhalb der Kundensicht. Neue Outputs erhalten den Haupttitel bereits nach dem Modellaufruf deterministisch aus dem ausgewählten Katalogmuster.

## PDF-Erstellung

`app/templates/report.html` rendert denselben strukturierten v3-Inhalt wie die Ergebnisansicht in zwei logischen Kernseiten. Seite 1 enthält Diagnosehinweis, Engpass, Hauptempfehlung, Zukunftsablauf, Rollen und gekennzeichnete Vorschau. Seite 2 enthält Human Check, kleinsten Einstieg, Umsetzungsweg, Voraussetzungen, Nicht-Automationen, offene Angaben, Fehlergrenzen und späteren Ausbau. Eine dritte logische Seite wird nur bei mindestens einer fachlich vorhandenen sekundären Möglichkeit erzeugt. Sehr lange Inhalte dürfen innerhalb einer logischen Seite auf weitere physische A4-Seiten umbrechen; Listenelemente und kompakte Karten bleiben dabei möglichst zusammen.

`app/static/styles.css` setzt A4-Ränder, kompakte Drucktypografie und kontrollierte `break-inside`-Grenzen. Der Browser öffnet mit `window.print()` den Druckdialog; der Nutzer speichert dort selbst als PDF.

Es gibt keine serverseitige PDF-Bibliothek. Der `mailto:`-Kontakt hängt den Bericht nicht automatisch an und behauptet dies auch nicht.

## Evaluationen und Tests

- Alle produktseitig ausgeführten Test- und Demo-Fälle liegen getrennt unter `knowledge/evaluation/`.
- Historische Originale in archivierten Research-Batches sind Provenienzartefakte und werden nicht indexiert.
- Das Repository dokumentiert und testet 91 Legacy-Evaluationen sowie 30 getrennte Batch-09-Evaluationen außerhalb der Indizes.
- `scripts/evaluate.py` führt beide Datensätze reproduzierbar durch Klassifikation, Gate-Kaskade und Selector. Legacy 91 und Batch 09 werden in getrennten Abschnitten ausgewiesen und nie gemittelt; `confirmed: false` und `research_proposed` bleiben sichtbar.
- `tests/test_agent_architecture.py` prüft Korpustrennung, Indexausschluss, Agentenpolicy, Budgets und Evidenztrennung.
- `tests/test_analysis_flow.py` prüft Journey, RAG-Bereinigung, Persistenz, Opportunities und Blueprint.
- `tests/test_product_finalization.py` prüft Kernoutput, konkrete KI-Hilfe, Reifegradfälle und Berichtsstruktur.
- `tests/test_quality_pass.py` prüft Grounding, menschliche Freigaben, Prompttrennung und Qualitätsfälle.
- `tests/test_ux_journey.py` prüft die vollständige sichtbare Journey und den Kundenbericht.
- `tests/test_recommendation_catalog.py` und `tests/test_recommendation_experience.py` prüfen Katalog, Selector, vier Referenzfälle, direkte Ansprache und Feldgrenzen.
- `tests/test_llm_classification.py` prüft Katalogkontext, typisierte Ergebnisse, Begrenzung auf drei Familien und den unveränderten Keyword-Fallback ausschließlich mit gemockten OpenAI-Aufrufen.
- Fünf echte Mentor-Läufe, finale Chromium-Ergebnis-/Berichtsrenders und PDF-Prüfung sind unter `docs/MENTOR_DEMO_2026-08-07.md` dokumentiert. Problemfamilien und Gates werden derzeit nicht persistiert und wurden für den Bericht unmittelbar aus den gespeicherten Eingaben rekonstruiert.
- Letzter vollständiger Lauf am 2026-08-07: 176 Tests bestanden.

## Aktuelle Architektur

```text
Jinja2/FastAPI UI
→ Python-Routen
→ deterministische Agentenregeln
→ kontrolliertes Agent-Pattern-Retrieval bei Rückfragen
→ aktives Diagnose-RAG mit reservierten Analyse-Typen
→ semantische Problemklassifikation mit deterministischem Fallback
→ strukturierter Katalog und sechs Gates
→ deterministische Solution-Vorauswahl
→ OpenAI Structured Output mit 15 Kernregeln
→ Pydantic-, OUT-, Katalog- und feldbezogene Grounding-Validierung
→ PostgreSQL
→ HTML-Ergebnis und Browser-PDF
```

Kernmerkmal: **Deterministische Sicherheits- und Recommendation-Entscheidungen plus getrenntes Vergleichswissen.** Der Agent-Pattern-Index unterstützt Rückfragen kontrolliert; er ersetzt weder Sicherheitsregeln noch den Selector.

## Geplante Zielarchitektur

```text
Jinja2/FastAPI UI
→ persistierter, nachvollziehbarer Agentenstate
→ begrenzter LLM-Interview-Agent
→ echtes Function Calling für typisierte Werkzeuge
→ persistierter Laufzeit-Trace nach eigener Datenschutzentscheidung
→ Pydantic-/Guardrail-Validierung
→ Observability und Tracing
→ PostgreSQL und Kundenausgabe
```

Der verbleibende Zielpunkt ist ein begrenzter, sicher evaluierter Function-Calling-Loop. Er ist nicht Teil des aktuellen integrierten Stands. Deterministische Sicherheits-, Budget-, Fakten- und Freigaberegeln bleiben auch bei einer späteren Einführung verbindlich. Der kleine Solution-Workflow-Index ergänzt den deterministischen Selector nur um die Auswahl einer passenden Workflowvariante. Er besitzt keine Entscheidungshoheit; bei fehlendem Index ist die direkte Auswahl innerhalb desselben Solution Patterns der sichere Fallback.
