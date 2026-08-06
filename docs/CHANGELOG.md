# Changelog

**Last Updated:** 2026-08-06

Diese Datei dokumentiert nur tatsächlich ausgeführte und verifizierte Änderungen. Roadmap-Punkte gelten nicht als umgesetzt.

## 2026-08-06 – Begründete Gate-Kaskade und A0 integriert

- `GATE-01` bis `GATE-06` werden nach der Klassifikation deterministisch als `pass`, `fail` oder `unknown` mit Begründung ausgewertet.
- A0 ist erreichbar, wenn keine KI nötig ist, der Fall außerhalb der digitalen Zielgruppe liegt oder kritische autonome Entscheidungen beziehungsweise fehlende Prüfgrenzen die Lösung blockieren.
- SP-04 setzt nun zwingend einen echten angenommenen, gelagerten, bearbeiteten oder abgeholten Gegenstand voraus; Gebäude, Einsatzorte und Kundenadressen reichen nicht. Der digitale Hausmeisterfall bleibt SP-03.
- `scripts/evaluate.py` misst 91 Legacy-Fälle und 30 Batch-09-Fälle getrennt und mittelt sie nicht. `confirmed: false` und `research_proposed` bleiben erhalten.
- Vierzehn neue Gate-/A0-/Zielgruppen- und Datensatztrennungstests ergänzen die Regression; vollständige Suite `149 passed`.

## 2026-08-06 – Batch-09-Knowledge-Rollen integriert

- Kontrollierte Runtime-Kopien für 27 Inference Patterns, 28 Solution Workflows und 10 Output-Strukturen reproduzierbar aus dem unveränderten Kandidaten-Batch erzeugt und mit Pydantic validiert.
- 30 Batch-09-Evaluationen ausschließlich unter `knowledge/evaluation/` abgelegt und ihren Indexausschluss getestet.
- Beispielwerte aus dem Runtime-Kontext entfernt, den SP-04-Workflow als dokumentarischen Ausschluss belassen und seine physischen Pflichtfelder auf menschliche Bestätigung verschärft.
- Einen getrennten Solution-Workflow-Index mit 27 positiven Workflows gebaut; harte Filterung nur nach ausgewähltem Solution Pattern, kleine Soft-Boosts für sichere Metadaten und deterministischer Fallback bei fehlendem Index.
- Den unkalibrierten Source-Strength-Abzug von 0,15/0,08 neutralisiert und als reine Transparenzmetadaten beibehalten.
- Batch-09-Inference-Patterns in den Interviewkontext eingebunden, ohne Hypothesen zu Nutzerfakten zu machen oder Fragebudgets zu erweitern.
- Vollständige Suite mit 135 Tests bestanden; der separate 27-Chunk-Solution-Index wurde gebaut und validiert.

## 2026-08-06 – Batch 09 fachlich geprüft

- Die vollständige Kandidatenlieferung formal auf 27 Inference Patterns, 28 Workflows, 10 Output-Strukturen, 30 Evaluationen, 20 Quellen, eindeutige IDs, gültige PF-/SP-Referenzen und vollständige `source_refs` geprüft.
- Neun Inference Patterns, zehn Workflows, alle zehn Output-Strukturen und zwölf Evaluationen fachlich näher gelesen.
- Rollen-Normalisierung, dokumentarischen SP-04-Ausschluss, strengere menschliche Bestätigung der physischen Zuordnung und ein fragliches Evaluationslabel als Bedingungen vor Runtime-Übernahme dokumentiert.
- Keine Kandidatendatei still verändert und noch keine Batch-09-Datei in einen Runtime-Loader oder Index aufgenommen.

## 2026-08-06 – Klickbaren Ergebnisprototyp als Idee festgehalten

- Das unveränderte Ideenpapier unter `docs/future-features/clickable-result-prototype.md` abgelegt und im Dokumentationsregister als nicht geplant und nicht umgesetzt verlinkt.
- Nur einen späteren Backlog-Hinweis ergänzt; keine Route, kein Template, kein JavaScript und keine Runtime-, Prompt-, Schema-, Datenbank- oder RAG-Änderung vorgenommen.

## 2026-08-06 – Knowledge für den Zielgruppenübergang geordnet

- Direkt geladene Dateien unter `knowledge/runtime/`, noch nicht integrierte Fachkandidaten unter `knowledge/candidates/`, 91 Test- und Demo-Fälle unter `knowledge/evaluation/` und Herkunftsartefakte unter `knowledge/archive/` getrennt.
- Katalog-, Fragepattern-, Demo-, Evaluation-, Merge- und bisherige RAG-Quellenpfade angepasst; Evaluationen bleiben durch Allow-Lists und Indexmarker ausgeschlossen.
- Produktive FAISS-Artefakte weder verschoben noch neu gebaut. Der bestehende Diagnoseindex bleibt lauffähig, basiert aber weiterhin auf dem bisherigen archivierten Korpus; die bestehenden Loader lesen diese Quellen für Übergangskompatibilität noch.
- Den Batch-09-Research-Auftrag nur als nicht integrierten Kandidaten eingeordnet. Keine Batch-09-Ergebnisse, Gate-Kaskade oder neue RAG-Logik integriert.
- 121 Tests, `python -m compileall app scripts`, App-Import, Pfad-/Katalog-/Pattern-/Indexprüfung und der kostenlose 91-Fälle-Keyword-Eval bestanden; Baseline unverändert bei 28 % PF Top-1, 30 % SP Top-1 und 48 % PF-01-Default.

## 2026-08-06 – Recommendation-Reviews versioniert

- Code-Review, RAG-Audit, Research-Integrationsplan, Zweitmeinungs-Briefing und Wettbewerbsanalyse als zeitgebundene Review-Dokumente aufgenommen.
- Jedes Dokument ist gegenüber den aktuellen Sources of Truth abgegrenzt; der RAG-Audit-Nachtrag markiert die inzwischen behobenen Phase-1-Befunde und die weiterhin offenen Gate-/A0-Punkte.
- Die fünf Dokumente sind im Dokumentationsregister eingetragen.

## 2026-08-06 – Semantische Problemklassifikation integriert

- `app/llm_classification.py` klassifiziert die bestätigte Erzählung per Structured Output in ein bis drei gültige Problemfamilien und die bestehenden sechs typisierten Gates; Katalogdefinitionen dienen als Kontext.
- `app/routes.py` verwendet diesen Klassifikator vor dem unveränderten deterministischen Selector. Bei `AIServiceError` greifen ausschließlich die bestehenden Keyword-Funktionen und die alte Gate-Inferenz als Fallback.
- Selector, Sicherheitsgrenzen, Agent-Layer, UI, Regex-Filter und produktive Indizes bleiben unverändert.
- Zehn Klassifikator- und drei parametrisierte Demo-Tests verwenden ausschließlich Mocks und bestanden.
- Der bereits vorhandene, nicht erneut kostenpflichtig ausgeführte LLM-Eval-Stand umfasst 91 Fälle: PF Top-1 65 %, PF Top-3 85 %, SP Top-1 70 % und PF-01-Default 3 %. Das Artefakt enthält zwei Klassifikatorfehler und einen Treffer eines verbotenen Begriffs; die zugrunde liegenden Labels bleiben unbestätigte Vorschläge.

## 2026-08-06 – Recommendation-Evaluation reproduzierbar gemacht

- `scripts/evaluate.py` führt die 91 getrennten Evaluationsfälle standardmäßig ohne LLM-Kosten durch `classify_problem_families` → `infer_decision_gates` → `select_recommendation` und misst Default-Quote, Gate-Streuung, verbotene Inhalte und Trefferquoten.
- Die gespeicherte Keyword-Baseline ergibt PF Top-1 28 Prozent, PF Top-3 38 Prozent, SP Top-1 30 Prozent, PF-01-Default 48 Prozent und null Treffer verbotener Inhalte.
- `knowledge/evaluation/expected_labels.json` enthält 91 Einträge. Alle stehen auf `confirmed: false`; die 40 vorbelegten Zuordnungen sind ausschließlich Vorschläge aus der Review und keine bestätigte Ground Truth.
- Evaluationsdateien bleiben vollständig außerhalb der produktiven Wissensindizes.

## 2026-08-06 – Katalog v2 und Research-Grundlage aufgenommen

- Research Batches 05 bis 08 und die zugehörige Forschungsgrundlage unter `knowledge/` abgelegt. Keine Datei wurde in einen Vektorindex aufgenommen; `DIAGNOSTIC_JSONL_FILES` und `AGENT_PATTERN_FILES` bleiben unverändert.
- Batch 08 bleibt unveränderte, zeitkritische Tool- und Architektur-Researchgrundlage und ist weder in den Laufzeitkatalog noch in einen produktiven Index integriert.
- `knowledge/structured/recommendation_catalog.json` auf `2026-08-06-v2` gehoben: neue Blöcke `genai_capabilities` (GAI-01…09), `decision_gates` (GATE-01…06), `failure_patterns` (FAIL-01…12), `autonomy_levels` (A0…A5) und `non_genai_mechanisms`; je Solution Pattern zehn neue Felder aus Batch 06; je Problemfamilie `genai_role`, `non_genai_requirement` und `human_boundary`.
- Vier durch Batch 06 verengte Zuordnungen übernommen: `SP-01` ohne `PF-11`/`PF-12`, `SP-04` und `SP-07` ohne `PF-04`. Sieben bereits vorher abweichende `supplementary`-Einträge wurden nur gemeldet, nicht geändert.
- `app/recommendation_service.py` um die entsprechenden Modelle und Referenzprüfungen erweitert, inklusive Autonomiegrenze je Solution Pattern gegen die Obergrenze seiner GenAI-Fähigkeiten.
- Der Laufzeitpfad nutzt die neuen Felder noch nicht; `select_recommendation` ist unverändert. Die LLM-gestützte Gate-Kaskade ist bewusst ein getrennter nächster Schritt.
- `scripts/merge_catalog_v2.py` als nachvollziehbarer, wiederholbarer Merge abgelegt (`--dry-run` zeigt den Diff).
- Reproduzierbarer Dry-Run, Katalog-Ladeprüfung, Python-Kompilierung und 21 Katalog-/Referenzfalltests erfolgreich ausgeführt.

## 2026-08-06 – Recommendation Experience integriert und geprüft

- Integrations-Commit `4ed51ab` auf `origin/feature/recommendation-experience` veröffentlicht.
- Neuen `FinalAnalysisResult`-Vertrag mit einer Hauptlösung, Promise, Heute/Mit KI, typisierter Ergebnisvorschau, Du/KI/Ergebnis/Human-Check, begrenzten Nutzen- und Voraussetzungenlisten, Umsetzungsweg, optionalem Ausbau und null bis zwei sekundären Möglichkeiten integriert.
- Wochentest und Pflicht zu genau drei Opportunities aus neuen Analysen und sichtbaren Seiten entfernt; alte JSONB-Analysen bleiben über die Legacy-Abbildung lesbar.
- Problemfamilien, sechs getrennte Gates und deterministischen Solution-Selector in den produktiven Analysepfad eingebunden; Auswahl, Ausschlüsse, Gates und Validierung werden datensparsam strukturiert geloggt.
- Analyse-Retrieval reserviert nun Diagnose-, Automations-, Voraussetzungs- und Guardrail-Muster, sodass ein konkretes Lösungsmuster nicht zufällig vollständig fehlt.
- Agent-Pattern-Index mit kontrollierten Typen, drei Treffern und sicherem Fallback im Interviewpfad aktiviert. Budgets, No-Repeat, Schleifenstopp, Faktenintegrität und Freigabegrenzen bleiben deterministisch.
- Echtes OpenAI Function Calling bewusst nicht integriert; ein sicherer Tool-Calling-Loop bleibt ein getrennt zu evaluierender Schritt.
- Ergebnisoberfläche auf eine dominante Hauptlösung, Vorher/Nachher, Vier-Schritt-Ablauf, zentrale Musterkarte und progressive Details umgebaut.
- Bericht auf zwei Kernseiten reduziert; Seite 3 erscheint nur bei fachlich vorhandenen sekundären Möglichkeiten. Browserdruck und `window.print()` bleiben bestehen.
- Mermaid nicht eingeführt; die validierte HTML-/CSS-Darstellung war bei Desktop, schmalem Mobile-Viewport und Bericht stabiler.
- Referenzfälle für Hausmeister, Schuhmacher, Blumenladen und Massagesalon sowie Sprach-, Längen-, Grounding-, Retrieval- und Agent-Pattern-Prüfungen ergänzt beziehungsweise angepasst.
- `python -m compileall -q app`, App-Start mit HTTP 200 und vollständige Testsuite mit `107 passed` erfolgreich ausgeführt.
- Visuell in Chrome geprüft: Desktop, schmale Mobile-Ansicht, 48–58-Pixel-Touchziele, lange deutsche Texte, fehlender horizontaler Überlauf und zweiseitiger Bericht ohne künstliche dritte Seite.
- Superseded Root-Kompatibilitätsdatei `UX_FLOW.md` entfernt und den Dokumentationstest auf die aktive Source of Truth unter `docs/flows/UX_FLOW.md` umgestellt.

## 2026-08-06 – RAG-Index-Zuverlässigkeit abgesichert

- Diagnosewissen überspringt nach der Promptbereinigung leere Chunks einzeln; gültige Chunks bleiben ihrem ursprünglichen Datensatz zugeordnet.
- Jeder Index-Promote validiert Test und Produktion, sichert Diagnose- und Agentenindex vollständig in einem neuen Zeitstempelordner und validiert die promovierte Produktion erneut. Das historische Pre-Batch-04-Archiv bleibt unverändert.
- Diagnose- und Agentenindex werden pro Prozess und Indexverzeichnis gecacht und nach einer mtime-Änderung der FAISS- oder Metadatendatei neu geladen. Fehlende Dateien bleiben ein Konfigurationsfehler.
- Vier neue RAG-Regressionstests bestanden; `python -m compileall app scripts`, App-Import und die Keyword-Evaluation mit unveränderten 28 % PF Top-1, 30 % SP Top-1 und 48 % PF-01-Default bestanden.
- Die vollständige Suite im vorhandenen uncommittierten Klassifikations-Arbeitsstand ergab `119 passed, 2 failed`; beide Fehler betreffen Demo-Tests ohne Mock für den bereits vorgeschalteten LLM-Klassifikator und wurden in dieser Phase nicht verändert.

## 2026-08-06 – Kompakten Recommendation-Vertrag beschlossen

- Wochentest und Pflicht zu genau drei Opportunities aus dem verbindlichen Zielvertrag entfernt.
- Genau eine dominante Hauptlösung, konkrete Ergebnisvorschau, direkte Du-Ansprache, variable Voraussetzungen und null bis zwei optionale weitere Möglichkeiten festgelegt.
- Strukturierter Katalog, sechs getrennte Gates, rückwärtskompatible JSONB-View und HTML-/CSS-Prozesslinie als verbindliches Design dokumentiert.
- Blumenladen als vierten Referenzfall ergänzt; Implementierung, Integration und Tests sind mit diesem Dokumentationsschritt noch nicht behauptet.

## 2026-08-06 – Strukturiertes Solution-Wissen implementiert

- Versionierten Katalog mit exakt zwölf Problemfamilien, zehn Solution Patterns und vollständiger Problemfamilie-zu-Lösung-Matrix angelegt.
- Typisierte Pydantic-Loader, sechs getrennte Decision Gates, deterministische Klassifikation und nachvollziehbaren Selector implementiert.
- Evaluationpfade explizit vom Loader ausgeschlossen; kein neuer Index, keine Embeddings und keine Datenbankmigration eingeführt.
- Sieben Katalog- und Referenzfalltests für Hausmeister, Schuhmacher, Blumenladen und Massagesalon erfolgreich ausgeführt.
- Katalog und Selector sind mit diesem Paket implementiert und getestet, aber noch nicht in den produktiven Analysepfad integriert.

## 2026-08-06 – Private IDE-Artefakte aus der Versionskontrolle entfernt

- Sieben bereits versionierte PyCharm-Dateien unter `.idea/` aus dem Git-Index entfernt; die lokalen Dateien bleiben auf dem Entwicklungsrechner erhalten.
- Die bestehende `.gitignore`-Regel `.idea/` verhindert, dass diese Dateien erneut aufgenommen werden.
- Alle verfolgten Dateinamen und Textdateien auf typische private Artefakte und hochwahrscheinliche Secret-Signaturen geprüft; keine weiteren privaten Dateien oder Secrets bestätigt.
- `.env.example` bewusst als sichere Platzhaltervorlage beibehalten.
- Keine Produktionslogik, Prompts, Indizes, Datenbankmodelle, Tests oder Nutzeroberflächen verändert.
- Frühere `.idea`-Versionen bleiben ohne ausdrücklich untersagten History-Rewrite in der Git-Historie; der Restpunkt ist in `docs/KNOWN_ISSUES.md` dokumentiert.

## 2026-08-05 – Recommendation-Fachgrundlage und Feature-Spec aufgenommen

- Vollständige Fachgrundlage mit zwölf Problemfamilien, zehn Solution Patterns, Reifegrad-/Gate-Modell und drei Referenzfallanalysen unter `docs/product/` aufgenommen.
- Strukturierte Recommendation-Feature-Spec mit Requirements, Design, Aufgaben und Acceptance Criteria angelegt.
- Projektstand, Known Issues, Roadmap, Entscheidungen, Architektur und Dokumentenregister an den dokumentierten fachlichen Stand angepasst.
- Fachliche Analyse ausdrücklich von implementierter und integrierter Laufzeitlogik getrennt.
- Keine Produktionslogik, Prompts, RAG-Indizes, Embeddings, Datenbankmodelle, Tests oder Nutzeroberflächen verändert.

## 2026-08-05 – Projektdokumentation konsolidiert

- Interne Projekt- und Entwicklungsdokumente unter `docs/` organisiert und in `docs/INDEX.md` mit Status und Source of Truth registriert.
- Projektstand, UX- und Processing-Flows sowie Product-Output-Anforderungen an ihre verbindlichen Zielpfade verschoben.
- UI-Redesign-Notizen und die frühere TODO-Liste nach Inhaltsprüfung und Zuordnung offener Punkte archiviert.
- Dokumentationspflege in `AGENTS.md`, `docs/DOCUMENTATION_GUIDE.md` und `.agents/skills/documentation-update/SKILL.md` verbindlich beschrieben.
- `README.md` mit dem zentralen Dokumentationsregister verknüpft.
- Keine Produktionslogik, Prompts, RAG-Indizes, Embeddings, Datenbankmodelle, Tests oder Nutzeroberflächen verändert.

## 2026-08-05 – Grounded Analysis Output normalisiert

**Commit:** `6320ad0` (`Normalize grounded analysis output`)

- Grounding und Normalisierung der finalen Analyse und Rückfragen erweitert.
- Embedding-Aufrufe getrennt von Structured-Output-Aufrufen gezählt.
- Eigener Timeout für die finale Analyse eingeführt.
- Zugehörige Produktfinalisierungs- und Qualitätsprüfungen ergänzt beziehungsweise angepasst.

## 2026-07-27 – Finale Analysevalidierung und Laufzeitverhalten verbessert

**Commit:** `8f369f4` (`Fix final analysis validation and latency`)

- Finale Analysevalidierung und Fehlerbehandlung erweitert.
- Analysefluss, Status- und Latenzverhalten überarbeitet.
- Zugehörige Analyse- und Produktfinalisierungstests ergänzt.

## 2026-07-27 – Kundenorientierte Diagnosejourney finalisiert

**Commit:** `73bf7fb` (`Finalize customer-first diagnostic journey`)

- Sichtbare Journey, Processing, Ergebnis- und Berichtsdarstellung überarbeitet.
- Agentenheuristiken, Structured-Output-Schema und Ergebnisaufbereitung erweitert.
- Produkt-, UX- und Processing-Spezifikationen sowie automatisierte Tests aktualisiert.

## 2026-07-26 – Diagnose- und Agentenarchitektur implementiert und dokumentiert

**Commits:** `6267589` (`Complete diagnostic demo architecture`), `b6c7a87` (`Document diagnostic architecture`)

- Begrenzten Diagnostic Interview Agent mit internem State, Regeln und drei Python-Werkzeugen implementiert.
- Diagnose- und Agent-Pattern-Indizes technisch getrennt.
- Indexbau, Vergleich, Validierung und Promotion ergänzt.
- RAG-, Agenten-, Journey- und Qualitätsprüfungen erweitert.
- Bestehende Diagnosearchitektur, RAG-Inventar, Merge-Plan und Evaluationsergebnisse dokumentiert.

## 2026-07-26 – Research-Batches ergänzt

**Commit:** `4ae2b21` (`Add diagnostic research batches`)

- Batch 02 für analoge Realität, Batch 03 für diagnostische Tiefe und Batch 04 für agentische Interviewmuster hinzugefügt.
- Korpora, Quellenregister, Patternkataloge, Guardrails, Evaluationen und Quality Gates getrennt abgelegt.
