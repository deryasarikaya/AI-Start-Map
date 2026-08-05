# Documentation Guide

**Status:** Active
**Last Updated:** 2026-08-05
**Source of Truth für Dokumentationspflege:** Dieses Dokument zusammen mit `docs/INDEX.md` und `.agents/skills/documentation-update/SKILL.md`.

## Schnellübersicht

| Datei | Frage |
|---|---|
| `docs/PROJECT_STATE.md` | Wo stehen wir heute? |
| `docs/ROADMAP.md` | Was wollen wir noch machen? |
| `docs/KNOWN_ISSUES.md` | Was funktioniert nicht? |
| `docs/DECISIONS.md` | Was haben wir entschieden und warum? |
| `docs/CHANGELOG.md` | Was wurde tatsächlich verändert? |
| `docs/ARCHITECTURE.md` | Wie funktioniert das System technisch? |
| `docs/INDEX.md` | Welche Dokumente gelten und welchen Status haben sie? |
| `docs/specs/` | Was muss ein konkretes Feature leisten und wie wird es abgenommen? |
| `docs/flows/` | Wie laufen sichtbare und technische Abläufe? |
| `docs/product/` | Welche fachlichen Grundlagen tragen Produktentscheidungen? |
| `docs/archive/` | Welche historischen Dokumente werden nur noch nachvollziehbar aufbewahrt? |

## Kerndokumente

### `docs/PROJECT_STATE.md`

- **Hinein:** ausschließlich der bestätigte heutige Produkt-, Technik-, RAG-, Agenten- und Teststand sowie bekannte Einschränkungen.
- **Nicht hinein:** Wunschfeatures, ungeprüfte Annahmen oder ausführliche Historie.
- **Aktualisieren:** nach jeder verifizierten Änderung des Ist-Stands.
- **Verantwortlich:** Abschluss eines Implementierungs-, Integrations- oder Release-Schritts.

### `docs/ROADMAP.md`

- **Hinein:** geplante fachliche, technische und produktbezogene Arbeit unter `Now`, `Next`, `Later` und `Not planned yet`.
- **Nicht hinein:** bereits umgesetzte Änderungen oder Implementierungsbehauptungen.
- **Aktualisieren:** bei bestätigten Prioritäts- oder Statusänderungen.
- **Verantwortlich:** Produktplanung und fachlich-technische Priorisierung.

### `docs/KNOWN_ISSUES.md`

- **Hinein:** alle bestätigten technischen, fachlichen und UX-Probleme sowie gebaute, aber nicht eingebundene Komponenten.
- **Nicht hinein:** bloße Ideen, unbestätigte Behauptungen oder nachweislich abgeschlossene Probleme.
- **Aktualisieren:** bei Bestätigung, Untersuchung, Teilfix und Verifikation.
- **Verantwortlich:** Diagnose/QA, Implementierung und abschließende Verifikation.

Ein Problem darf erst entfernt werden, wenn es technisch oder fachlich behoben, durch einen passenden erfolgreichen Test verifiziert und in `docs/CHANGELOG.md` dokumentiert wurde. Offene oder teilweise gelöste Probleme bleiben mit `Open`, `Investigating`, `In Progress`, `Partially Fixed`, `Blocked` oder `Verified Fixed` enthalten.

### `docs/DECISIONS.md`

- **Hinein:** bestätigte Entscheidungen mit Datum, Grund, Konsequenzen, Alternativen und Status.
- **Nicht hinein:** lose Ideen oder unbeschlossene Optionen.
- **Aktualisieren:** wenn eine Entscheidung getroffen, geändert oder aufgehoben wird.
- **Verantwortlich:** Entscheidungs- oder Review-Schritt.

### `docs/CHANGELOG.md`

- **Hinein:** tatsächlich umgesetzte und verifizierte Änderungen.
- **Nicht hinein:** Roadmap-Punkte, Absichten oder offene Arbeiten.
- **Aktualisieren:** nach erfolgreicher Verifikation, spätestens vor Commit, PR oder Release.
- **Verantwortlich:** Abschluss des logisch vollständigen Änderungspakets.

### `docs/ARCHITECTURE.md`

- **Hinein:** bestätigte Komponenten, Datenflüsse, Persistenz, Integrationen und eine ausdrücklich geplante Zielarchitektur.
- **Nicht hinein:** ungeprüfte Komponenten oder geplante Architektur als aktiver Zustand.
- **Aktualisieren:** bei Änderungen an Komponenten, Aufrufketten, Datenmodell, RAG, Agent, OpenAI, PDF oder Evaluation.
- **Verantwortlich:** Architektur- und Implementierungsreview.

## Register, Specs, Flows und Grundlagen

### `docs/INDEX.md`

- **Hinein:** alle wichtigen aktiven, zu prüfenden, ersetzten und archivierten Dokumente mit Status, Source of Truth und Prüfdatum.
- **Nicht hinein:** lange Fachinhalte oder eine zweite Version des jeweiligen Dokuments.
- **Aktualisieren:** bei jeder Erstellung, Verschiebung, Umbenennung, Ersetzung, Archivierung oder Reaktivierung.
- **Verantwortlich:** derselbe Arbeitsschritt, der den Dokumentstatus verändert.

### Feature-Specs unter `docs/specs/`

- **Hinein:** Requirements, Design, Tasks und Acceptance Criteria eines abgegrenzten Features; Status von Beschluss, Umsetzung, Integration und Test bleibt getrennt.
- **Nicht hinein:** allgemeiner Projektstand oder ungeprüfte Zielarchitektur als Beschluss.
- **Aktualisieren:** bei Änderungen an Scope, Anforderungen, Design, Aufgaben oder Abnahmekriterien.
- **Verantwortlich:** Feature-Planung, Umsetzung, Review und Abnahme.

### Flows unter `docs/flows/`

- **Hinein:** bestätigte sichtbare Journey beziehungsweise technische Zustands- und Fehlerabläufe.
- **Nicht hinein:** historische UI-Ideen oder unbeschlossene Features.
- **Aktualisieren:** wenn ein Flow beschlossen oder tatsächlich verändert wird.
- **Verantwortlich:** Produkt-/UX-Review und Implementierungsabschluss.

### Product Foundations unter `docs/product/`

- **Hinein:** fachlich geprüfte Analyse- und Entscheidungsgrundlagen mit klarer Abgrenzung zur Laufzeitlogik.
- **Nicht hinein:** Behauptungen über bereits integrierte Features oder produktive RAG-Quellen ohne Freigabe.
- **Aktualisieren:** nach fachlichem Review oder einer bestätigten Grundlagenentscheidung.
- **Verantwortlich:** fachlicher Review; technische Arbeit verweist darauf, verändert sie aber nicht stillschweigend.

### Archiv unter `docs/archive/`

- **Hinein:** historische Dokumente, deren relevante aktive Inhalte zugeordnet oder übernommen wurden.
- **Nicht hinein:** offene Punkte ohne Zielzuordnung oder weiterhin verbindliche Sources of Truth.
- **Aktualisieren:** beim Archivieren um Status, Zweck und Nachfolger; danach nur für historische Korrekturen.
- **Verantwortlich:** Dokumentationsreview.

Archivieren ist dem Löschen vorzuziehen, wenn ein Dokument Entscheidungen oder Projektgeschichte nachvollziehbar macht. Ein archiviertes Dokument darf erst nach erneuter Inhaltsprüfung, Konfliktauflösung, Statusänderung und Aktualisierung von `docs/INDEX.md` reaktiviert werden.

## Statusdefinitionen

- `Active`: aktuell geprüft und verbindlich für den ausgewiesenen Zweck.
- `Draft`: Arbeitsgrundlage, noch nicht vollständig freigegeben.
- `Needs Review`: enthält relevante Inhalte, aber mindestens eine Aussage oder Verbindlichkeit muss geprüft werden.
- `Superseded`: durch ein benanntes anderes Dokument ersetzt.
- `Archived`: ausschließlich historischer Nachweis, keine aktuelle Source of Truth.

## Source-of-Truth- und Konfliktregeln

- Für jeden Zweck wird genau eine Source of Truth in `docs/INDEX.md` benannt.
- Bei Widersprüchen gilt nicht automatisch die neuere Datei: Code, Tests, Entscheidungen und aktuelle Anforderungen werden geprüft.
- Konfliktbehaftete Dokumente werden sichtbar als `Needs Review` oder `Superseded` markiert und mit dem Konflikt beziehungsweise Nachfolger verknüpft.
- `planned`, `decided`, `implemented`, `integrated`, `tested` und `documented` sind unterschiedliche Zustände.
- Nach jeder relevanten Änderung müssen alle betroffenen Kerndokumente, die aktive Feature-Spec und `docs/INDEX.md` geprüft werden; nicht jede geprüfte Datei muss geändert werden.
- Der vollständige Ablauf steht in `.agents/skills/documentation-update/SKILL.md`.
