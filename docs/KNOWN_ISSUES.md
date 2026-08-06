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
- **Beobachtung:** Katalog, begründete GATE-01…06-Kaskade und Selector wählen A0 bis A2 beziehungsweise die Lösung außerhalb des Diagnose-Top-k. Die semantische Klassifikation erreicht im vorhandenen unbestätigten Eval-Artefakt PF Top-1 65 %, PF Top-3 85 %, SP Top-1 70 % und 3 % PF-01-Default, enthält aber zwei Klassifikatorfehler und einen Treffer eines verbotenen Begriffs. Die 40 vorbelegten Legacy- und alle Batch-09-Zuordnungen bleiben unbestätigte Vorschläge. Reale Interviews können weitere Fehler zeigen.
- **Erwartetes Verhalten:** Aus bestätigtem Problem, Ursache, Reifegrad und Voraussetzungen wird ein kleiner, konkreter und betrieblich passender erster Workflow gewählt.
- **Mögliche Ursachen:** Semantische Klassifikation und Gate-Schwellen sind noch nicht anhand bestätigter Ground Truth und realer Interviews kalibriert; API-Fehler fallen bewusst auf die schwächere Keyword-Heuristik zurück.
- **Nächster Prüfschritt:** Vorgeschlagene Labels fachlich prüfen, erst danach als Ground Truth bestätigen, und zusätzlich reale Interviews anonymisiert gegen Katalog, Gates und sichtbaren Output auswerten.
- **Betroffene Dateien:** `app/recommendation_service.py`, `app/openai_service.py`, `tests/test_recommendation_catalog.py`, `tests/test_recommendation_experience.py`.

## KI-002 – Hausmeisterfall empfiehlt teilweise zu viel manuelle Ablage

- **Status:** Verified Fixed
- **Beobachtung:** Der Hausmeisterfall priorisiert `SP-03` mobile Einsatzdokumentation mit Einsatznotiz. Der leichte Einsatzanker ist Teil derselben Einstiegslösung; Album oder Umschlag werden nicht zur Kernlösung.
- **Erwartetes Verhalten:** Das System berücksichtigt den vorhandenen digitalen Reifegrad und wählt den kleinsten sinnvollen digitalen oder KI-gestützten Workflow, sofern die Voraussetzungen bereits bestehen.
- **Historische Ursache:** Kanaleignung und Gesamt-Prozessreife waren vermischt; der normalisierte Katalog und der Anker-/Kanal-Gegencheck fehlten.
- **Nächster Prüfschritt:** Im Rahmen der allgemeinen realen Kalibrierung beobachten; keine offene Codekorrektur für den Referenzfall.
- **Betroffene Dateien:** `knowledge/runtime/recommendation_catalog.json`, `app/recommendation_service.py`, `tests/test_recommendation_catalog.py`, `tests/test_recommendation_experience.py`.

## KI-003 – „Ordnung vor Automatisierung“ wird teilweise zu stark angewandt

- **Status:** Verified Fixed
- **Beobachtung:** Die bestehende Regel kann dazu führen, dass Ordnung oder manuelle Standardisierung empfohlen wird, obwohl ein Betrieb bereits ausreichend digital arbeitsfähig ist.
- **Erwartetes Verhalten:** Ordnung ist Voraussetzung, wenn sie tatsächlich fehlt; sie ersetzt aber keine passende KI-Unterstützung. Nicht jeder Betrieb beginnt auf Reifegrad 1.
- **Historische Ursache:** Kanaleignung, Prozess-/Datenreife und Automationsreife waren vermischt; Voraussetzungen konnten eine allgemeine Ordnungsphase aufblähen.
- **Nächster Prüfschritt:** Die sechs Gates mit realen Interviews kalibrieren; die technische Vermischung ist behoben.
- **Betroffene Dateien:** `app/openai_service.py`, `app/schemas.py`, `app/agent_service.py`, `knowledge/archive/research_batches/batch_03_diagnostic_depth/02_rag_corpus.jsonl`.

## KI-004 – Strukturierter Solution-Pattern-Katalog fehlte

- **Status:** Verified Fixed
- **Beobachtung:** Katalog, Loader, Matrix und Selector sind implementiert, in den Analysepfad integriert und automatisiert getestet.
- **Erwartetes Verhalten:** Der Recommendation Layer wählt aus einem fachlich freigegebenen strukturierten Katalog über Applicability- und Exclusion-Gates passende konkrete Workflows aus und begründet sie.
- **Historische Ursache:** Die fachliche Grundlage wurde zunächst vor die technische Integration gestellt; der normalisierte Katalog fehlte deshalb im früheren Laufzeitpfad.
- **Nächster Prüfschritt:** Inhalt nur bei fachlich bestätigten Änderungen versioniert weiterpflegen.
- **Betroffene Dateien:** `knowledge/runtime/recommendation_catalog.json`, `app/recommendation_service.py`, `app/routes.py` und Katalogtests.

## KI-005 – Kundensprache ist teilweise zu technisch oder zu lang

- **Status:** Partially Fixed
- **Beobachtung:** `recommendation-v3` trennt Nutzer, KI, Regeln und Mensch, übernimmt OUT-Feldnamen deterministisch und zeigt offene Angaben, kleinste Version, Nicht-Automationen und Autonomiestufe. Der Prompt wurde auf 15 Kernregeln gekürzt; ein kontrollierter Live-Hausmeisteraufruf bestand. Die tatsächliche Modellformulierung muss über mehrere reale Fälle weiter beobachtet werden.
- **Erwartetes Verhalten:** Kurze deutsche Sätze, ein klarer nächster Schritt und konkrete Beschreibung von Eingabe, KI-Aufgabe, Ergebnis und menschlicher Kontrolle.
- **Mögliche Ursachen:** Noch zu verifizieren. Trotz kürzerem Prompt bleibt der Structured Output umfangreich; Katalogformulierungen können ohne UI-Hierarchie weiterhin dicht wirken.
- **Nächster Prüfschritt:** Die fünf Mentor-Demofälle vollständig im Browser gegen Verständlichkeit, erfundene Fakten und offene Angaben prüfen.
- **Betroffene Dateien:** `app/openai_service.py`, `app/schemas.py`, `app/templates/results.html`, `app/templates/report.html`, `tests/test_product_finalization.py`.

## KI-006 – Ergebnisansicht und PDF waren zu groß oder textlastig

- **Status:** Verified Fixed
- **Beobachtung:** Die Hauptseite folgt einer festen achtteiligen Leserichtung von Engpass bis späterer Ausbaustufe. Desktop und ein schmaler Mobile-Viewport wurden im echten Browser geprüft: lange Überschriften und Ablauftexte brechen um, die Seite hat keinen horizontalen Überlauf, H1 liegt bei 40 beziehungsweise 32 Pixeln und die Hauptaktionen bei 48–55 Pixeln Höhe. Der Bericht enthält denselben fachlichen Vertrag und wurde als echtes PDF geprüft: ein normaler Fall umfasst zwei vollständige A4-Seiten; ein absichtlich langer Fall bricht ohne leere oder abgeschnittene Seiten über sechs Seiten um.
- **Erwartetes Verhalten:** Der Kernoutput ist schnell scanbar; Vertiefungen bleiben optional; eine dritte Seite entsteht nur bei echten weiteren Möglichkeiten.
- **Mögliche Ursachen:** Noch zu verifizieren. Viele strukturierte Pflichtfelder, lange Modellausgaben und feste Berichtssektionen können sich kumulieren.
- **Nächster Prüfschritt:** Die browserübergreifende Geräte- und Druckmatrix bleibt unter UX-001 offen; die Mentor-Demofälle müssen den Bericht noch mit ihren tatsächlichen Laufzeitdaten prüfen.
- **Betroffene Dateien:** `app/templates/results.html`, `app/templates/report.html`, `app/static/styles.css`, `app/routes.py`.

## KI-007 – Problem erkannt, konkreter KI-Workflow nicht immer optimal

- **Status:** Partially Fixed
- **Beobachtung:** Die Diagnose kann Symptom und Engpass korrekt benennen, während `ai_support`, `first_change` oder die erste Opportunity zu allgemein beziehungsweise nicht die beste konkrete Lösung ist.
- **Erwartetes Verhalten:** Der gewählte Workflow passt zur Ursache, nutzt vorhandene Eingaben, erzeugt einen prüfbaren Output und benennt die menschliche Kontrolle.
- **Mögliche Ursachen:** Die strukturelle Ursache ist behoben; verbleibendes Risiko liegt in semantischer Klassifikation, Keyword-Fallback und Modellformulierung bei bisher ungesehenen Fällen.
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

## TECH-005 – Diagnoseindex basiert noch auf dem archivierten bisherigen Korpus

- **Status:** Investigating
- **Beobachtung:** Die produktiven FAISS-Artefakte wurden bei der Knowledge-Umordnung nicht verändert. Der Diagnoseindex bleibt lauffähig, basiert aber weiterhin auf dem bisherigen Korpus. Dessen Quellen liegen nun unter `knowledge/archive/` und werden von den bestehenden Loadern für Kompatibilität und reproduzierbare Indexprüfungen weiter gelesen.
- **Erwartetes Verhalten:** Ein späterer, fachlich freigegebener Zielkorpus besitzt einen reproduzierbar gebauten und validierten Diagnoseindex; Evaluationen bleiben ausgeschlossen.
- **Mögliche Ursachen:** Der Legacy-Index enthält weiterhin frühere Zielgruppenbeispiele; Batch 09 liefert bewusst Lösungs- statt vollständiges Diagnosewissen.
- **Nächster Prüfschritt:** Im finalen Analysepfad messen, ob Legacy-Diagnose-Retrieval noch einen sicheren Mehrwert liefert; andernfalls auf klaren Fallback reduzieren oder entfernen.
- **Betroffene Dateien:** `app/rag_service.py`, `knowledge/archive/`, `knowledge/candidates/batch_09/RESEARCH_AUFTRAG.md`, `data/vector_index/`.

## KI-008 – Batch-09-Antwortzweige und Branchenvarianten sind noch nicht real kalibriert

- **Status:** Investigating
- **Beobachtung:** Formale Prüfung und Fachstichprobe sind bestanden. Die Antwortzweige der Inference Patterns sind jedoch schematisch, und die konkreten Branchenworkflows sind quellenbasierte Synthesen statt bestätigte Beobachtungen realer AI-Start-Map-Betriebe.
- **Erwartetes Verhalten:** Patterns steuern nur überprüfbare Hypothesen und notwendige Rückfragen; Runtime-Auswahl und sichtbarer Output bleiben an bestätigte Nutzerfakten und deterministische Grenzen gebunden.
- **Nächster Prüfschritt:** Die integrierten Runtime-Kopien mit den fünf Mentor-Demofällen sowie späteren echten Interviews getrennt auswerten.
- **Betroffene Dateien:** `knowledge/candidates/batch_09/`, `docs/BATCH_09_FACHPRUEFUNG.md`.

## UX-001 – Reale Geräte- und Druckabnahme ist noch nicht vollständig bestätigt

- **Status:** Investigating
- **Beobachtung:** Desktop, schmaler Mobile-Viewport und zweiseitiger Bericht wurden am 2026-08-06 in Chrome visuell geprüft. Eine vollständige Freigabe auf physischem Android/iPhone, Safari und unterschiedlichen Druckdialogen bleibt offen.
- **Erwartetes Verhalten:** Mobile Karten stapeln sauber, Touch-Ziele bleiben nutzbar und der variable Bericht bleibt ohne abgeschnittene Inhalte auf zwei beziehungsweise optional drei A4-Seiten.
- **Mögliche Ursachen:** Browser- und Druckengine-Unterschiede können nur begrenzt durch strukturelle Tests abgedeckt werden.
- **Nächster Prüfschritt:** Definierte Browser-/Gerätematrix manuell prüfen und Ergebnisse dokumentieren.
- **Betroffene Dateien:** `app/templates/results.html`, `app/templates/report.html`, `app/static/styles.css`, `tests/test_ux_journey.py`, `tests/test_product_finalization.py`.
