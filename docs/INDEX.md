# Dokumentationsregister

**Status:** Active
**Letzte Aktualisierung:** 2026-08-05
**Letzte Prüfung:** 2026-08-05

Dieses Register ist die verbindliche Übersicht der Projekt-, Produkt- und Entwicklungsdokumentation. Es muss aktualisiert werden, wenn ein Dokument erstellt, verschoben, umbenannt, ersetzt, archiviert oder wieder aktiviert wird.

## Sources of Truth

| Dokument | Zweck | Status | Source of Truth | Letzte Aktualisierung | Letzte Prüfung | Ersetzt durch / Verwandt mit |
|---|---|---|---|---|---|---|
| `README.md` | Öffentliche Projektübersicht, Installation und Einstieg | Active | Öffentlicher Projektüberblick | 2026-08-05 | 2026-08-05 | `docs/INDEX.md`, `docs/PROJECT_STATE.md` |
| `AGENTS.md` | Globale Arbeitsregeln für Coding Agents | Active | Repositoryweite Agentenregeln | 2026-08-05 | 2026-08-05 | `.agents/skills/documentation-update/SKILL.md` |
| `docs/INDEX.md` | Register, Status und Zuständigkeit aller wichtigen Dokumente | Active | Dokumentationsstruktur und Dokumentstatus | 2026-08-05 | 2026-08-05 | `docs/DOCUMENTATION_GUIDE.md` |
| `docs/PROJECT_STATE.md` | Ausschließlich bestätigter heutiger Projektstand | Active | Aktueller Produkt-, Technik-, RAG-, Agenten- und Teststand | 2026-08-05 | 2026-08-05 | `docs/ARCHITECTURE.md`, `docs/KNOWN_ISSUES.md` |
| `docs/ROADMAP.md` | Geplante fachliche, technische und produktbezogene Arbeit | Active | Priorisierte Zukunftsarbeit | 2026-08-05 | 2026-08-05 | aktive Feature-Specs |
| `docs/KNOWN_ISSUES.md` | Bestätigte offene oder unzureichende Punkte | Active | Offene technische, fachliche und UX-Probleme | 2026-08-05 | 2026-08-05 | `docs/CHANGELOG.md` |
| `docs/DECISIONS.md` | Bestätigte Entscheidungen und Begründungen | Active | Produkt- und Architekturentscheidungen | 2026-08-05 | 2026-08-05 | aktive Feature-Specs |
| `docs/CHANGELOG.md` | Tatsächlich ausgeführte und verifizierte Änderungen | Active | Änderungshistorie auf Dokumentebene; Git bleibt verbindliche technische Historie | 2026-08-05 | 2026-08-05 | Git-Historie |
| `docs/ARCHITECTURE.md` | Verifizierte Ist-Architektur und klar getrennte Zielarchitektur | Active | Aktuelle technische Architektur | 2026-08-05 | 2026-08-05 | `knowledge/AGENT_ARCHITECTURE.md`, `knowledge/RAG_MERGE_PLAN.md` ersetzt |
| `docs/DOCUMENTATION_GUIDE.md` | Cheat Sheet und Pflegeprozess | Active | Detaillierte Dokumentationspflege | 2026-08-05 | 2026-08-05 | `.agents/skills/documentation-update/SKILL.md` |
| `docs/flows/UX_FLOW.md` | Sichtbarer Nutzerflow und bestehende UX-Verträge | Needs Review | Aktuell implementierter Flow; Outputvertrag wird fachlich geprüft | 2026-07-26 | 2026-08-05 | Product-Output- und Recommendation-Spec |
| `docs/flows/PROCESSING_FLOW.md` | Processing-Zustände, Fehler- und Retry-Verhalten | Active | Aktueller Processing-Flow | 2026-07-26 | 2026-08-05 | `docs/ARCHITECTURE.md` |
| `docs/specs/product-output/requirements.md` | Bestehender Product-Output-Vertrag | Needs Review | Aktuell implementierter Vertrag, bis Review abgeschlossen ist | 2026-07-26 | 2026-08-05 | Recommendation-Spec und Fachgrundlage |

## Archiv und ersetzte Dokumente

| Dokument | Zweck | Status | Source of Truth | Letzte Aktualisierung | Letzte Prüfung | Ersetzt durch / Verwandt mit |
|---|---|---|---|---|---|---|
| `docs/archive/UI_REDESIGN_NOTES_2026-07-26.md` | Historische UI-Redesign-Notizen | Archived | Keine aktuelle Source of Truth | 2026-07-26 | 2026-08-05 | `docs/flows/UX_FLOW.md`, `docs/ARCHITECTURE.md`, `docs/CHANGELOG.md` |
| `docs/archive/TODO_2026-07-26.md` | Historischer Umsetzungsstand und offene Liste | Archived | Keine aktive Aufgabenliste | 2026-07-26 | 2026-08-05 | `docs/ROADMAP.md`, `docs/KNOWN_ISSUES.md`, Feature-Specs |
| `UX_FLOW.md` | Temporärer Root-Kompatibilitätsverweis für bestehenden Test | Superseded | Keine; aktiver Inhalt liegt unter `docs/flows/UX_FLOW.md` | 2026-08-05 | 2026-08-05 | `docs/flows/UX_FLOW.md` |
| `knowledge/AGENT_ARCHITECTURE.md` | Frühere Agentenarchitektur | Superseded | Keine aktuelle Source of Truth | 2026-07-26 | 2026-08-05 | `docs/ARCHITECTURE.md` |
| `knowledge/AGENT_EVALUATION_REPORT.md` | Historischer Evaluationsbericht | Archived | Historischer Nachweis, nicht heutiger Teststand | 2026-07-26 | 2026-08-05 | `docs/PROJECT_STATE.md`, Tests |
| `knowledge/RAG_INVENTORY.md` | RAG-Inventar vom 26.07.2026 | Needs Review | Historisches Inventar; aktueller Laufzeitstand in `docs/ARCHITECTURE.md` | 2026-07-26 | 2026-08-05 | Fachgrundlage, `docs/ARCHITECTURE.md` |
| `knowledge/RAG_MERGE_PLAN.md` | Früherer Merge- und Build-Plan | Superseded | Keine aktuelle Planungs-Source-of-Truth | 2026-07-26 | 2026-08-05 | `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` |
| `knowledge/README.md` | Verzeichnisführer für Knowledge-Artefakte | Needs Review | Ordnerstruktur; Laufzeitstatus ausschließlich in `docs/ARCHITECTURE.md` | 2026-07-26 | 2026-08-05 | Fachgrundlage, `docs/ARCHITECTURE.md` |

## Bewusst außerhalb von `docs/`

`knowledge/curated/`, `knowledge/raw/` und `knowledge/research_batches/` bleiben an ihren vorhandenen Pfaden. Sie sind produktive Wissensquellen, Rohquellen oder unveränderliche Research-/Provenienzartefakte und keine parallel gepflegte allgemeine Projektdokumentation. Pfade werden durch Allow-Lists, Tests, Quellenreferenzen und die Fachgrundlage verwendet. Dieser Dokumentationsauftrag verändert diese Knowledge-Quelldateien nicht.

## Dokumentierte technische Ausnahme im Repository-Root

`tests/test_ux_journey.py::test_documented_decisions_exist` liest derzeit `UX_FLOW.md` direkt im Repository-Root. Tests dürfen in diesem Auftrag nicht geändert werden. Deshalb bleibt dort vorübergehend ein kurzer, ausdrücklich als `Superseded` markierter Kompatibilitätsverweis mit den vom Test geprüften Entscheidungsmarkern. Der vollständige aktive Inhalt existiert nur unter `docs/flows/UX_FLOW.md`. Die spätere Entfernung des Root-Verweises benötigt einen getrennt freigegebenen Testpfad-Commit.

## Pflegeregel

Bei Widersprüchen gilt nicht automatisch das jüngste Datum. Zuerst tatsächlichen Code, Tests und bestätigte Produktentscheidungen prüfen; danach den Status im Register und die betroffene Source of Truth aktualisieren. Geplante, beschlossene, implementierte, integrierte, getestete und dokumentierte Zustände dürfen nicht gleichgesetzt werden.
