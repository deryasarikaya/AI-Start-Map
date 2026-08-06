# Changelog

**Last Updated:** 2026-08-06

Diese Datei dokumentiert nur tatsächlich ausgeführte und verifizierte Änderungen. Roadmap-Punkte gelten nicht als umgesetzt.

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
