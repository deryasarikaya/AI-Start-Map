# Known Issues

**Last Updated:** 2026-08-06

Diese Datei enthält alle bestätigten aktuell nicht funktionierenden, unzureichenden oder noch nicht eingebundenen Punkte: technische Probleme, fachliche Qualitätsprobleme, UX-Probleme und inaktive Komponenten.

Ein Problem darf erst entfernt werden, wenn:

1. es technisch oder fachlich behoben wurde,
2. ein passender Test erfolgreich war,
3. die Änderung in `docs/CHANGELOG.md` dokumentiert wurde.

Offene oder teilweise gelöste Probleme bleiben mit einem der Statuswerte `Open`, `Investigating`, `In Progress`, `Partially Fixed`, `Blocked` oder `Verified Fixed` enthalten.

## SEC-001 – Historische PyCharm-Artefakte bleiben in der Git-Historie erreichbar

- **Status:** Open
- **Beobachtung:** Die sieben `.idea`-Dateien sind aus dem aktuellen Feature-Branch entfernt und werden künftig ignoriert. Frühere Commits enthalten weiterhin PyCharm-Arbeitsbereichsdaten und lokale absolute Pfade. `origin/main` enthält die Dateien bis zu einem geprüften Merge ebenfalls im aktuellen Stand.
- **Erwartetes Verhalten:** Private IDE-Artefakte sind weder im aktuellen Default-Branch noch unbeabsichtigt über die erreichbare Projekthistorie verfügbar.
- **Mögliche Ursachen:** `.idea/` wurde am 2026-07-17 committed; die spätere `.gitignore`-Regel beendet die Verfolgung bereits versionierter Dateien nicht automatisch.
- **Nächster Prüfschritt:** Den Removal-Commit reviewen und freigegeben nach `main` mergen. Danach separat entscheiden, ob die historischen lokalen Pfade einen koordinierten History-Rewrite rechtfertigen; dieser ist nach den aktuellen Repositoryregeln nicht zulässig und würde alle betroffenen Branches und Klone betreffen.
- **Betroffene Dateien:** Git-Historie von `.idea/V2_AI_Start_Map.iml`, `.idea/inspectionProfiles/Project_Default.xml`, `.idea/inspectionProfiles/profiles_settings.xml`, `.idea/misc.xml`, `.idea/modules.xml`, `.idea/vcs.xml` und `.idea/workspace.xml`; `.gitignore` enthält bereits `.idea/`.

## KI-001 – Recommendation-Auswahl braucht noch reale Kalibrierung

- **Status:** Partially Fixed
- **Beobachtung:** Katalog, sechs Gates und Selector wählen die Lösung nun außerhalb des Diagnose-Top-k. Ein reproduzierbares Harness misst 91 getrennte Evaluationsfälle; seine 40 vorbelegten PF-/SP-Zuordnungen sind jedoch noch unbestätigte Vorschläge. Die vier verbindlichen Referenzfälle bestehen; reale Interviews können dennoch weitere Klassifikations- und Priorisierungsfehler zeigen.
- **Erwartetes Verhalten:** Aus bestätigtem Problem, Ursache, Reifegrad und Voraussetzungen wird ein kleiner, konkreter und betrieblich passender erster Workflow gewählt.
- **Mögliche Ursachen:** Die deterministische Klassifikation verwendet bewusst kleine Wortmarker; branchenspezifische Umschreibungen und widersprüchliche reale Angaben sind noch nicht ausreichend kalibriert.
- **Nächster Prüfschritt:** Vorgeschlagene Labels fachlich prüfen, erst danach als Ground Truth bestätigen, und zusätzlich reale Interviews anonymisiert gegen Katalog, Gates und sichtbaren Output auswerten.
- **Betroffene Dateien:** `app/recommendation_service.py`, `app/openai_service.py`, `tests/test_recommendation_catalog.py`, `tests/test_recommendation_experience.py`.

## KI-002 – Hausmeisterfall empfiehlt teilweise zu viel manuelle Ablage

- **Status:** Verified Fixed
- **Beobachtung:** Der Hausmeisterfall priorisiert `SP-03` mobile Einsatzdokumentation mit Einsatznotiz. Der leichte Einsatzanker ist Teil derselben Einstiegslösung; Album oder Umschlag werden nicht zur Kernlösung.
- **Erwartetes Verhalten:** Das System berücksichtigt den vorhandenen digitalen Reifegrad und wählt den kleinsten sinnvollen digitalen oder KI-gestützten Workflow, sofern die Voraussetzungen bereits bestehen.
- **Historische Ursache:** Kanaleignung und Gesamt-Prozessreife waren vermischt; der normalisierte Katalog und der Anker-/Kanal-Gegencheck fehlten.
- **Nächster Prüfschritt:** Im Rahmen der allgemeinen realen Kalibrierung beobachten; keine offene Codekorrektur für den Referenzfall.
- **Betroffene Dateien:** `knowledge/structured/recommendation_catalog.json`, `app/recommendation_service.py`, `tests/test_recommendation_catalog.py`, `tests/test_recommendation_experience.py`.

## KI-003 – „Ordnung vor Automatisierung“ wird teilweise zu stark angewandt

- **Status:** Verified Fixed
- **Beobachtung:** Die bestehende Regel kann dazu führen, dass Ordnung oder manuelle Standardisierung empfohlen wird, obwohl ein Betrieb bereits ausreichend digital arbeitsfähig ist.
- **Erwartetes Verhalten:** Ordnung ist Voraussetzung, wenn sie tatsächlich fehlt; sie ersetzt aber keine passende KI-Unterstützung. Nicht jeder Betrieb beginnt auf Reifegrad 1.
- **Historische Ursache:** Kanaleignung, Prozess-/Datenreife und Automationsreife waren vermischt; Voraussetzungen konnten eine allgemeine Ordnungsphase aufblähen.
- **Nächster Prüfschritt:** Die sechs Gates mit realen Interviews kalibrieren; die technische Vermischung ist behoben.
- **Betroffene Dateien:** `app/openai_service.py`, `app/schemas.py`, `app/agent_service.py`, `knowledge/research_batches/batch_03_diagnostic_depth/02_rag_corpus.jsonl`.

## KI-004 – Strukturierter Solution-Pattern-Katalog fehlte

- **Status:** Verified Fixed
- **Beobachtung:** Katalog, Loader, Matrix und Selector sind implementiert, in den Analysepfad integriert und automatisiert getestet.
- **Erwartetes Verhalten:** Der Recommendation Layer wählt aus einem fachlich freigegebenen strukturierten Katalog über Applicability- und Exclusion-Gates passende konkrete Workflows aus und begründet sie.
- **Historische Ursache:** Die fachliche Grundlage wurde zunächst vor die technische Integration gestellt; der normalisierte Katalog fehlte deshalb im früheren Laufzeitpfad.
- **Nächster Prüfschritt:** Inhalt nur bei fachlich bestätigten Änderungen versioniert weiterpflegen.
- **Betroffene Dateien:** `knowledge/structured/recommendation_catalog.json`, `app/recommendation_service.py`, `app/routes.py` und Katalogtests.

## KI-005 – Kundensprache ist teilweise zu technisch oder zu lang

- **Status:** Partially Fixed
- **Beobachtung:** Der neue Vertrag begrenzt Titel, Listen und Textfelder, erzwingt direkte Du-Ansprache und zeigt eine konkrete Vorschau. Die tatsächliche Modellformulierung muss im Betrieb weiter beobachtet werden.
- **Erwartetes Verhalten:** Kurze deutsche Sätze, ein klarer nächster Schritt und konkrete Beschreibung von Eingabe, KI-Aufgabe, Ergebnis und menschlicher Kontrolle.
- **Mögliche Ursachen:** Noch zu verifizieren. Lange Structured Outputs, interne Fachbegriffe im Ausgangswissen und begrenzte sprachliche Normalisierung sind mögliche Faktoren.
- **Nächster Prüfschritt:** Sichtbare Ausgaben der vier Referenzfälle und neuer realer Fälle weiter gegen die bestehenden Längen- und Verständlichkeitskriterien prüfen.
- **Betroffene Dateien:** `app/openai_service.py`, `app/schemas.py`, `app/templates/results.html`, `app/templates/report.html`, `tests/test_product_finalization.py`.

## KI-006 – Ergebnisansicht und PDF waren zu groß oder textlastig

- **Status:** Verified Fixed
- **Beobachtung:** Hauptseite und Bericht nutzen den kompakten Vertrag. Desktop, schmale Mobile-Ansicht und der zweiseitige Bericht ohne sekundäre Möglichkeit wurden visuell geprüft.
- **Erwartetes Verhalten:** Der Kernoutput ist schnell scanbar; Vertiefungen bleiben optional; eine dritte Seite entsteht nur bei echten weiteren Möglichkeiten.
- **Mögliche Ursachen:** Noch zu verifizieren. Viele strukturierte Pflichtfelder, lange Modellausgaben und feste Berichtssektionen können sich kumulieren.
- **Nächster Prüfschritt:** Browserübergreifende Geräte- und Druckmatrix bleibt unter UX-001 offen.
- **Betroffene Dateien:** `app/templates/results.html`, `app/templates/report.html`, `app/static/styles.css`, `app/routes.py`.

## KI-007 – Problem erkannt, konkreter KI-Workflow nicht immer optimal

- **Status:** Partially Fixed
- **Beobachtung:** Die Diagnose kann Symptom und Engpass korrekt benennen, während `ai_support`, `first_change` oder die erste Opportunity zu allgemein beziehungsweise nicht die beste konkrete Lösung ist.
- **Erwartetes Verhalten:** Der gewählte Workflow passt zur Ursache, nutzt vorhandene Eingaben, erzeugt einen prüfbaren Output und benennt die menschliche Kontrolle.
- **Mögliche Ursachen:** Die strukturelle Ursache ist behoben; verbleibendes Risiko liegt in heuristischer Problemfamilienklassifikation und Modellformulierung bei bisher ungesehenen Fällen.
- **Nächster Prüfschritt:** Neue reale Fehlfälle als getrennte Diagnose- und Solution-Auswahltests ergänzen.
- **Betroffene Dateien:** `app/openai_service.py`, `app/rag_service.py`, `app/schemas.py`, `tests/test_quality_pass.py`, `tests/test_product_finalization.py`.

## TECH-001 – Agent-Pattern-Index war nicht in der Laufzeit aktiv

- **Status:** Verified Fixed
- **Beobachtung:** `_agent_pattern_context()` ruft `retrieve_agent_patterns()` im Interviewpfad kontrolliert auf und begrenzt Typen sowie Trefferzahl. Python-Guardrails bleiben maßgeblich.
- **Erwartetes Verhalten:** Falls fachlich freigegeben, beeinflusst gezieltes Agent-Pattern-Retrieval die Agentenentscheidung nachvollziehbar, ohne deterministische Sicherheitsregeln zu ersetzen.
- **Historische Ursache:** Die Retrieval-Funktion war vorbereitet, besaß aber keinen kontrollierten Laufzeitaufruf.
- **Nächster Prüfschritt:** Nutzen und Trefferqualität mit realen Interviews beobachten.
- **Betroffene Dateien:** `app/rag_service.py`, `app/agent_service.py`, `app/routes.py`, `tests/test_agent_architecture.py`.

## TECH-002 – Kein echtes LLM-Function-Calling und kein vollständig dynamischer Interview-Agent

- **Status:** Partially Fixed
- **Beobachtung:** Die drei sogenannten Agentenwerkzeuge sind interne Python-Funktionen. Die Aktion wird überwiegend deterministisch durch `evaluate_readiness_and_next_action()` gewählt; das LLM ruft keine Tools über Function Calling auf.
- **Erwartetes Verhalten:** In der geplanten Zielarchitektur wählt ein begrenzter LLM-Agent typisierte Werkzeuge, während Python Budgets, Sicherheit, No-Repeat und Faktenintegrität durchsetzt.
- **Mögliche Ursachen:** Noch nicht implementiert; die aktuelle regelbasierte Architektur war die sichere erste Ausbaustufe.
- **Nächster Prüfschritt:** Tool-Schemas, Agentenschleife, Abbruchbedingungen und Offline-Evaluation spezifizieren.
- **Betroffene Dateien:** `app/agent_service.py`, `app/routes.py`, `app/openai_service.py`, `app/agent_config.py`.

## TECH-003 – End-to-End-Observability und Tracing fehlen

- **Status:** Open
- **Beobachtung:** Datenschutzarme strukturierte Logs decken Chunktypen, Agent-Pattern-Typen, Agentenaktion, Fragezahl, Problemfamilien, Gates, ausgewählte und ausgeschlossene Solutions sowie Validierung ab. Ein persistiertes End-to-End-Trace-Modell existiert nicht.
- **Erwartetes Verhalten:** Eine Diagnose lässt sich intern über Phasen und Entscheidungen nachvollziehen, ohne vollständige Nutzerantworten unnötig zu protokollieren.
- **Mögliche Ursachen:** Observability wurde bisher nicht als eigener technischer Baustein implementiert.
- **Nächster Prüfschritt:** Erst Datenschutz, Korrelation und Aufbewahrung für persistente Traces entscheiden; keine neue Plattform ohne Bedarf.
- **Betroffene Dateien:** `app/routes.py`, `app/openai_service.py`, `app/rag_service.py`, `app/agent_service.py`.

## TECH-004 – Bereitstellung der produktiven Indizes aus einem frischen Checkout ist nicht verifiziert

- **Status:** Investigating
- **Beobachtung:** Die produktiven FAISS-Dateien existieren lokal, werden aber zusammen mit `chunks.json` und `manifest.json` durch `.gitignore` ausgeschlossen. Im Repository ist kein bestätigter Deployment-Schritt dokumentiert, der sie automatisch bereitstellt. Promote-Backups und Laufzeit-Caching sind inzwischen technisch abgesichert, lösen aber die Bereitstellung in einer frischen Zielumgebung nicht.
- **Erwartetes Verhalten:** Jede Zielumgebung erhält reproduzierbar genau die validierten produktiven Diagnose- und Agentenindizes.
- **Mögliche Ursachen:** Die generierten Artefakte wurden bewusst nicht versioniert; ein separater Artefakt- oder Build-Prozess ist noch zu verifizieren.
- **Nächster Prüfschritt:** Aktuelles Deployment prüfen und eine eindeutige, getestete Bereitstellungsstrategie dokumentieren.
- **Betroffene Dateien:** `.gitignore`, `README.md`, `app/rag_service.py`, `scripts/build_index.py`, `scripts/compare_indexes.py`.

## UX-001 – Reale Geräte- und Druckabnahme ist noch nicht vollständig bestätigt

- **Status:** Investigating
- **Beobachtung:** Desktop, schmaler Mobile-Viewport und zweiseitiger Bericht wurden am 2026-08-06 in Chrome visuell geprüft. Eine vollständige Freigabe auf physischem Android/iPhone, Safari und unterschiedlichen Druckdialogen bleibt offen.
- **Erwartetes Verhalten:** Mobile Karten stapeln sauber, Touch-Ziele bleiben nutzbar und der variable Bericht bleibt ohne abgeschnittene Inhalte auf zwei beziehungsweise optional drei A4-Seiten.
- **Mögliche Ursachen:** Browser- und Druckengine-Unterschiede können nur begrenzt durch strukturelle Tests abgedeckt werden.
- **Nächster Prüfschritt:** Definierte Browser-/Gerätematrix manuell prüfen und Ergebnisse dokumentieren.
- **Betroffene Dateien:** `app/templates/results.html`, `app/templates/report.html`, `app/static/styles.css`, `tests/test_ux_journey.py`, `tests/test_product_finalization.py`.
