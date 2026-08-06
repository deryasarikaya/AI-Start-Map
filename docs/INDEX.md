# Dokumentationsregister

**Status:** Active
**Letzte Aktualisierung:** 2026-08-06
**Letzte Prüfung:** 2026-08-06

Dieses Register ist die verbindliche Übersicht der Projekt-, Produkt- und Entwicklungsdokumentation. Es muss aktualisiert werden, wenn ein Dokument erstellt, verschoben, umbenannt, ersetzt, archiviert oder wieder aktiviert wird.

## Sources of Truth

| Dokument | Zweck | Status | Source of Truth | Letzte Aktualisierung | Letzte Prüfung | Ersetzt durch / Verwandt mit |
|---|---|---|---|---|---|---|
| `README.md` | Öffentliche Projektübersicht, Installation und Einstieg | Active | Öffentlicher Projektüberblick | 2026-08-06 | 2026-08-06 | `docs/INDEX.md`, `docs/PROJECT_STATE.md` |
| `AGENTS.md` | Globale Arbeitsregeln für Coding Agents | Active | Repositoryweite Agentenregeln | 2026-08-06 | 2026-08-06 | `.agents/skills/documentation-update/SKILL.md` |
| `.agents/skills/documentation-update/SKILL.md` | Wiederverwendbarer Ablauf für Dokumentationsprüfung und -pflege | Active | Detaillierter Documentation-Update-Workflow für Coding Agents | 2026-08-05 | 2026-08-05 | `AGENTS.md`, `docs/DOCUMENTATION_GUIDE.md` |
| `docs/INDEX.md` | Register, Status und Zuständigkeit aller wichtigen Dokumente | Active | Dokumentationsstruktur und Dokumentstatus | 2026-08-06 | 2026-08-06 | `docs/DOCUMENTATION_GUIDE.md` |
| `docs/PROJECT_STATE.md` | Ausschließlich bestätigter heutiger Projektstand | Active | Aktueller Produkt-, Technik-, RAG-, Agenten- und Teststand | 2026-08-06 | 2026-08-06 | `docs/ARCHITECTURE.md`, `docs/KNOWN_ISSUES.md` |
| `docs/ROADMAP.md` | Geplante fachliche, technische und produktbezogene Arbeit | Active | Priorisierte Zukunftsarbeit | 2026-08-06 | 2026-08-06 | aktive Feature-Specs |
| `docs/KNOWN_ISSUES.md` | Bestätigte offene oder unzureichende Punkte | Active | Offene technische, fachliche und UX-Probleme | 2026-08-06 | 2026-08-06 | `docs/CHANGELOG.md` |
| `docs/DECISIONS.md` | Bestätigte Entscheidungen und Begründungen | Active | Produkt- und Architekturentscheidungen | 2026-08-06 | 2026-08-06 | aktive Feature-Specs |
| `docs/CHANGELOG.md` | Tatsächlich ausgeführte und verifizierte Änderungen | Active | Änderungshistorie auf Dokumentebene; Git bleibt verbindliche technische Historie | 2026-08-06 | 2026-08-06 | Git-Historie |
| `docs/ARCHITECTURE.md` | Verifizierte Ist-Architektur und klar getrennte Zielarchitektur | Active | Aktuelle technische Architektur | 2026-08-06 | 2026-08-06 | `knowledge/archive/notes/AGENT_ARCHITECTURE.md`, `knowledge/archive/notes/RAG_MERGE_PLAN.md` ersetzt |
| `docs/DOCUMENTATION_GUIDE.md` | Cheat Sheet und Pflegeprozess | Active | Detaillierte Dokumentationspflege | 2026-08-05 | 2026-08-05 | `.agents/skills/documentation-update/SKILL.md` |
| `docs/product/AI_Start_Map_Fachgrundlage_Painpoints_Solutions_2026-08-05.md` | Fachliche Pain-Point-, Reifegrad- und Solution-Pattern-Grundlage | Active | Fachliche Grundlage für Pain Points, Reifegrad und Solution Patterns; keine Laufzeitlogik | 2026-08-05 | 2026-08-05 | `docs/specs/solution-pattern-recommendation/` |
| `knowledge/runtime/recommendation_catalog.json` | Maschinenlesbare Problemfamilien, Solution Patterns und Matrix | Active | Direkt geladener, nicht indexierter Recommendation-Katalog | 2026-08-06 | 2026-08-06 | Fachgrundlage und Recommendation-Spec |
| `docs/flows/UX_FLOW.md` | Sichtbarer Nutzerflow und UX-Verträge | Active | Verbindliche Recommendation-Zielreise; Ist-Status im Projektstand | 2026-08-06 | 2026-08-06 | Product-Output- und Recommendation-Spec |
| `docs/flows/PROCESSING_FLOW.md` | Processing-Zustände, Fehler- und Retry-Verhalten | Active | Aktueller Processing-Flow | 2026-08-06 | 2026-08-06 | `docs/ARCHITECTURE.md` |
| `docs/specs/product-output/requirements.md` | Verbindlicher Product-Output-Vertrag | Active | Neuer kompakter Kundenoutput und Kompatibilitätsregeln | 2026-08-06 | 2026-08-06 | Recommendation-Spec und Fachgrundlage |
| `docs/specs/solution-pattern-recommendation/requirements.md` | Anforderungen des Recommendation-Layers | Active | Verbindlicher Feature-Scope; Ist-Status getrennt | 2026-08-06 | 2026-08-06 | Fachgrundlage |
| `docs/specs/solution-pattern-recommendation/design.md` | Fachlich-technisches Design | Active | Verbindliches Feature-Design; Ist-Status getrennt | 2026-08-06 | 2026-08-06 | Fachgrundlage, `docs/ARCHITECTURE.md` |
| `docs/specs/solution-pattern-recommendation/tasks.md` | Aufteilbare Umsetzungsaufgaben | Active | Aufgabenstatus und Nachweise des Features | 2026-08-06 | 2026-08-06 | `docs/ROADMAP.md` |
| `docs/specs/solution-pattern-recommendation/acceptance-criteria.md` | Fachlich bestätigte Abnahmekriterien | Active | Verbindliche Feature-Abnahme; Nachweisstatus getrennt | 2026-08-06 | 2026-08-06 | Fachgrundlage |

## Reviews, Audits und zeitgebundene Arbeitsdokumente

| Dokument | Zweck | Status | Source of Truth | Letzte Aktualisierung | Letzte Prüfung | Ersetzt durch / Verwandt mit |
|---|---|---|---|---|---|---|
| `docs/CODE_REVIEW_2026-08-06.md` | Externe technische und fachliche Review des damaligen Stands | Historical Snapshot | Keine aktuelle Source of Truth | 2026-08-06 | 2026-08-06 | `docs/PROJECT_STATE.md`, `docs/ARCHITECTURE.md`, Git-Historie |
| `docs/RAG_AUDIT_2026-08-06.md` | Zeitgebundene Prüfung von RAG, Indizes und Research-Integration | Historical Snapshot with Update | Keine aktuelle Source of Truth | 2026-08-06 | 2026-08-06 | `docs/ARCHITECTURE.md`, `docs/KNOWN_ISSUES.md` |
| `docs/RESEARCH_BATCHES_05_08_INTEGRATION.md` | Bewertung und teilweise umgesetzter Einbauplan für Research 05–08 | Partially Implemented Historical Plan | Keine aktuelle Source of Truth | 2026-08-06 | 2026-08-06 | Recommendation-Spec, `docs/PROJECT_STATE.md` |
| `docs/BRIEFING_ZWEITMEINUNG.md` | Historisches Briefing für externe Einschätzung | Historical Snapshot | Keine aktuelle Source of Truth | 2026-08-06 | 2026-08-06 | `docs/PROJECT_STATE.md`, `docs/CODE_REVIEW_2026-08-06.md` |
| `docs/WETTBEWERB_KIHELFER24.md` | Zeitgebundene Wettbewerbsanalyse | Historical Market Review | Keine Implementierungs-Source-of-Truth | 2026-08-06 | 2026-08-06 | `docs/PROJECT_STATE.md`, Recommendation-Spec |

## Archiv und ersetzte Dokumente

| Dokument | Zweck | Status | Source of Truth | Letzte Aktualisierung | Letzte Prüfung | Ersetzt durch / Verwandt mit |
|---|---|---|---|---|---|---|
| `docs/archive/UI_REDESIGN_NOTES_2026-07-26.md` | Historische UI-Redesign-Notizen | Archived | Keine aktuelle Source of Truth | 2026-07-26 | 2026-08-05 | `docs/flows/UX_FLOW.md`, `docs/ARCHITECTURE.md`, `docs/CHANGELOG.md` |
| `docs/archive/TODO_2026-07-26.md` | Historischer Umsetzungsstand und offene Liste | Archived | Keine aktive Aufgabenliste | 2026-07-26 | 2026-08-05 | `docs/ROADMAP.md`, `docs/KNOWN_ISSUES.md`, Feature-Specs |
| `knowledge/archive/notes/AGENT_ARCHITECTURE.md` | Frühere Agentenarchitektur | Superseded | Keine aktuelle Source of Truth | 2026-07-26 | 2026-08-06 | `docs/ARCHITECTURE.md` |
| `knowledge/archive/notes/AGENT_EVALUATION_REPORT.md` | Historischer Evaluationsbericht | Archived | Historischer Nachweis, nicht heutiger Teststand | 2026-07-26 | 2026-08-06 | `docs/PROJECT_STATE.md`, Tests |
| `knowledge/archive/notes/RAG_INVENTORY.md` | RAG-Inventar vom 26.07.2026 | Archived | Historisches Inventar; aktueller Laufzeitstand in `docs/ARCHITECTURE.md` | 2026-07-26 | 2026-08-06 | Fachgrundlage, `docs/ARCHITECTURE.md` |
| `knowledge/archive/notes/RAG_MERGE_PLAN.md` | Früherer Merge- und Build-Plan | Superseded | Keine aktuelle Planungs-Source-of-Truth | 2026-07-26 | 2026-08-06 | `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` |
| `knowledge/candidates/batch_09/RESEARCH_AUFTRAG.md` | Research-Auftrag für einen möglichen späteren Zielkorpus | Planned Candidate | Keine integrierte Runtime-Quelle | 2026-08-06 | 2026-08-06 | `docs/ROADMAP.md`, `docs/KNOWN_ISSUES.md` |
| `knowledge/README.md` | Verzeichnisführer für Knowledge-Artefakte | Active | Status und Grenzen der Knowledge-Ordner | 2026-08-06 | 2026-08-06 | `docs/ARCHITECTURE.md`, `docs/PROJECT_STATE.md` |

## Bewusst außerhalb von `docs/`

`knowledge/runtime/` enthält ausschließlich direkt geladene Produktdateien. `knowledge/candidates/` enthält noch nicht integrierte Fachkandidaten, `knowledge/evaluation/` ausschließlich niemals indexierbare Test- und Demo-Fälle und `knowledge/archive/` Herkunftsartefakte. Das Archiv ist keine neue fachliche Runtime-Quelle, wird aber für die alte Indexquellenbasis und den reproduzierbaren Katalog-Merge technisch noch gelesen. Der genaue Übergangsstatus steht in `knowledge/README.md` und `docs/ARCHITECTURE.md`.

## Pflegeregel

Bei Widersprüchen gilt nicht automatisch das jüngste Datum. Zuerst tatsächlichen Code, Tests und bestätigte Produktentscheidungen prüfen; danach den Status im Register und die betroffene Source of Truth aktualisieren. Geplante, beschlossene, implementierte, integrierte, getestete und dokumentierte Zustände dürfen nicht gleichgesetzt werden.
