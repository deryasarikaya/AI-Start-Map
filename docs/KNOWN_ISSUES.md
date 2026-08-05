# Known Issues

**Last Updated:** 2026-08-05

Diese Datei enthält alle bestätigten aktuell nicht funktionierenden, unzureichenden oder noch nicht eingebundenen Punkte: technische Probleme, fachliche Qualitätsprobleme, UX-Probleme und inaktive Komponenten.

Ein Problem darf erst entfernt werden, wenn:

1. es technisch oder fachlich behoben wurde,
2. ein passender Test erfolgreich war,
3. die Änderung in `CHANGELOG.md` dokumentiert wurde.

Offene oder teilweise gelöste Probleme bleiben mit einem der Statuswerte `Open`, `Investigating`, `In Progress`, `Partially Fixed`, `Blocked` oder `Verified Fixed` enthalten.

## KI-001 – Recommendation Layer liefert noch keine durchgehend gute Auswahl

- **Status:** Open
- **Beobachtung:** Der aktuelle Recommendation Layer ist fachlich noch nicht zufriedenstellend. Er erkennt den Engpass häufig plausibel, priorisiert aber nicht in jedem Fall den besten konkreten nächsten KI-Workflow.
- **Erwartetes Verhalten:** Aus bestätigtem Problem, Ursache, Reifegrad und Voraussetzungen wird ein kleiner, konkreter und betrieblich passender erster Workflow gewählt.
- **Mögliche Ursachen:** Noch zu verifizieren. Prüfhypothesen sind fehlende explizite Solution Patterns, zu breite RAG-Treffer und eine zu große Auswahlverantwortung im finalen Modellprompt.
- **Nächster Prüfschritt:** Fehlentscheidungen aus Hausmeister, Schuhmacher und Massagesalon mit erwarteten Zielworkflows vergleichen und nach Problemfamilie klassifizieren.
- **Betroffene Dateien:** `app/openai_service.py`, `app/rag_service.py`, `app/schemas.py`, `tests/test_product_finalization.py`, `tests/test_quality_pass.py`.

## KI-002 – Hausmeisterfall empfiehlt teilweise zu viel manuelle Ablage

- **Status:** Investigating
- **Beobachtung:** Im Hausmeisterfall wird teilweise manuelle Ablage priorisiert, obwohl konkretere digitale oder KI-gestützte Unterstützung geprüft werden sollte.
- **Erwartetes Verhalten:** Das System berücksichtigt den vorhandenen digitalen Reifegrad und wählt den kleinsten sinnvollen digitalen oder KI-gestützten Workflow, sofern die Voraussetzungen bereits bestehen.
- **Mögliche Ursachen:** Noch zu verifizieren. Der aktuelle RAG-Korpus enthält für den Fall sowohl Minimalverbesserungen als auch Automationsmuster; Auswahl und Gewichtung könnten die Minimalverbesserung überbetonen.
- **Nächster Prüfschritt:** Einen festen Hausmeister-Evaluationsfall mit Retrievaltreffern, Modelloutput und erwarteter Empfehlung ausführen und dokumentieren.
- **Betroffene Dateien:** `knowledge/research_batches/batch_03_diagnostic_depth/02_rag_corpus.jsonl`, `app/rag_service.py`, `app/openai_service.py`. Ein spezifischer automatisierter Hausmeister-Qualitätstest ist noch zu verifizieren beziehungsweise anzulegen.

## KI-003 – „Ordnung vor Automatisierung“ wird teilweise zu stark angewandt

- **Status:** Open
- **Beobachtung:** Die bestehende Regel kann dazu führen, dass Ordnung oder manuelle Standardisierung empfohlen wird, obwohl ein Betrieb bereits ausreichend digital arbeitsfähig ist.
- **Erwartetes Verhalten:** Ordnung ist Voraussetzung, wenn sie tatsächlich fehlt; sie ersetzt aber keine passende KI-Unterstützung. Nicht jeder Betrieb beginnt auf Reifegrad 1.
- **Mögliche Ursachen:** Noch zu verifizieren. Reifegradmuster im RAG, Promptformulierungen und manuelle Qualitätsregeln könnten zusammen eine konservative Auswahl verstärken.
- **Nächster Prüfschritt:** Das geplante vierstufige Reifegradmodell auf repräsentative Fälle anwenden und die Auswahlgrenze zwischen Ordnung, Digitalisierung, KI-Unterstützung und Automatisierung festlegen.
- **Betroffene Dateien:** `app/openai_service.py`, `app/schemas.py`, `app/agent_service.py`, `knowledge/research_batches/batch_03_diagnostic_depth/02_rag_corpus.jsonl`.

## KI-004 – Strukturierter Solution-Pattern-Katalog fehlt

- **Status:** Open
- **Beobachtung:** Diagnose-, Reifegrad- und Automationswissen ist vorhanden, aber es gibt noch keinen kleinen, fachlich freigegebenen Katalog konkreter Solution Patterns mit Eignung, Voraussetzungen und Ausschlusskriterien.
- **Erwartetes Verhalten:** Der Recommendation Layer kann aus einem geprüften Katalog passende konkrete Workflows auswählen und begründen.
- **Mögliche Ursachen:** Dies ist noch nicht umgesetzt; die fachliche Strukturierung wurde bewusst vor die technische Integration gestellt.
- **Nächster Prüfschritt:** Pain-Point-Taxonomie, Problemfamilien und Reifegradmodell fertigstellen; danach Solution Patterns fachlich prüfen.
- **Betroffene Dateien:** Noch keine neue Zieldatei beschlossen. Spätere Integrationspunkte sind voraussichtlich `app/rag_service.py`, `app/openai_service.py` und die Tests; genaue Pfade sind noch zu entscheiden.

## KI-005 – Kundensprache ist teilweise zu technisch oder zu lang

- **Status:** Open
- **Beobachtung:** Einzelne Ergebnisse enthalten zu technische, abstrakte oder lange Formulierungen, obwohl die Oberfläche Alltagssprache für kleine Betriebe verlangt.
- **Erwartetes Verhalten:** Kurze deutsche Sätze, ein klarer nächster Schritt und konkrete Beschreibung von Eingabe, KI-Aufgabe, Ergebnis und menschlicher Kontrolle.
- **Mögliche Ursachen:** Noch zu verifizieren. Lange Structured Outputs, interne Fachbegriffe im Ausgangswissen und begrenzte sprachliche Normalisierung sind mögliche Faktoren.
- **Nächster Prüfschritt:** Sichtbare Ausgaben der drei Zielbeispiele markieren, Längen- und Verständlichkeitskriterien festlegen und daraus Tests ableiten.
- **Betroffene Dateien:** `app/openai_service.py`, `app/schemas.py`, `app/templates/results.html`, `app/templates/report.html`, `tests/test_product_finalization.py`.

## KI-006 – Ergebnisansicht und PDF sind teilweise zu groß oder textlastig

- **Status:** Open
- **Beobachtung:** Ergebnis und dreiseitige Druckansicht können trotz Priorisierung zu viel Text enthalten oder visuell zu groß wirken.
- **Erwartetes Verhalten:** Der Kernoutput ist schnell scanbar; Vertiefungen bleiben optional; die normale Druckansicht nutzt drei A4-Seiten ohne überladene Textblöcke.
- **Mögliche Ursachen:** Noch zu verifizieren. Viele strukturierte Pflichtfelder, lange Modellausgaben und feste Berichtssektionen können sich kumulieren.
- **Nächster Prüfschritt:** Reale Beispielberichte rendern und in Zielbrowsern auf Seitenumbrüche, Textmenge und mobile Scanbarkeit prüfen.
- **Betroffene Dateien:** `app/templates/results.html`, `app/templates/report.html`, `app/static/styles.css`, `app/routes.py`.

## KI-007 – Problem erkannt, konkreter KI-Workflow nicht immer optimal

- **Status:** Open
- **Beobachtung:** Die Diagnose kann Symptom und Engpass korrekt benennen, während `ai_support`, `first_change` oder die erste Opportunity zu allgemein beziehungsweise nicht die beste konkrete Lösung ist.
- **Erwartetes Verhalten:** Der gewählte Workflow passt zur Ursache, nutzt vorhandene Eingaben, erzeugt einen prüfbaren Output und benennt die menschliche Kontrolle.
- **Mögliche Ursachen:** Noch zu verifizieren. Aktuell werden Diagnosewissen und ein breiter finaler Prompt genutzt; eine explizite Zuordnung Problemfamilie → Solution Pattern fehlt.
- **Nächster Prüfschritt:** Für jede Ziel-Evaluation getrennt Diagnosequalität und Solution-Auswahl bewerten.
- **Betroffene Dateien:** `app/openai_service.py`, `app/rag_service.py`, `app/schemas.py`, `tests/test_quality_pass.py`, `tests/test_product_finalization.py`.

## TECH-001 – Agent-Pattern-Index ist gebaut, aber nicht in der Laufzeit aktiv

- **Status:** Open
- **Beobachtung:** `data/agent_pattern_index/` enthält laut Manifest 205 Patterns. `retrieve_agent_patterns()` existiert, wird aber außerhalb seiner Definition nirgends aufgerufen.
- **Erwartetes Verhalten:** Falls fachlich freigegeben, beeinflusst gezieltes Agent-Pattern-Retrieval die Agentenentscheidung nachvollziehbar, ohne deterministische Sicherheitsregeln zu ersetzen.
- **Mögliche Ursachen:** Die Retrieval-Funktion wurde vorbereitet, aber noch nicht in `routes.py` oder `agent_service.py` integriert.
- **Nächster Prüfschritt:** Nutzen, Aufrufpunkt, erlaubte Pattern-Typen, Fallback und Evaluation definieren, bevor die Funktion aktiviert wird.
- **Betroffene Dateien:** `app/rag_service.py`, `app/agent_service.py`, `app/routes.py`, `tests/test_agent_architecture.py`.

## TECH-002 – Kein echtes LLM-Function-Calling und kein vollständig dynamischer Interview-Agent

- **Status:** Open
- **Beobachtung:** Die drei sogenannten Agentenwerkzeuge sind interne Python-Funktionen. Die Aktion wird überwiegend deterministisch durch `evaluate_readiness_and_next_action()` gewählt; das LLM ruft keine Tools über Function Calling auf.
- **Erwartetes Verhalten:** In der geplanten Zielarchitektur wählt ein begrenzter LLM-Agent typisierte Werkzeuge, während Python Budgets, Sicherheit, No-Repeat und Faktenintegrität durchsetzt.
- **Mögliche Ursachen:** Noch nicht implementiert; die aktuelle regelbasierte Architektur war die sichere erste Ausbaustufe.
- **Nächster Prüfschritt:** Tool-Schemas, Agentenschleife, Abbruchbedingungen und Offline-Evaluation spezifizieren.
- **Betroffene Dateien:** `app/agent_service.py`, `app/routes.py`, `app/openai_service.py`, `app/agent_config.py`.

## TECH-003 – End-to-End-Observability und Tracing fehlen

- **Status:** Open
- **Beobachtung:** Es gibt Laufzeit-Logs für einzelne OpenAI-, Retrieval- und Analysephasen, aber kein durchgängiges Trace-Modell für Session, Agentenentscheidung, Retrievaltreffer, Validierung und Recommendation-Auswahl.
- **Erwartetes Verhalten:** Eine Diagnose lässt sich intern über Phasen und Entscheidungen nachvollziehen, ohne vollständige Nutzerantworten unnötig zu protokollieren.
- **Mögliche Ursachen:** Observability wurde bisher nicht als eigener technischer Baustein implementiert.
- **Nächster Prüfschritt:** Datenschutzarme Trace-Felder, Korrelation und Aufbewahrung definieren.
- **Betroffene Dateien:** `app/routes.py`, `app/openai_service.py`, `app/rag_service.py`, `app/agent_service.py`.

## TECH-004 – Bereitstellung der produktiven Indizes aus einem frischen Checkout ist nicht verifiziert

- **Status:** Investigating
- **Beobachtung:** Die produktiven FAISS-Dateien existieren lokal, werden aber zusammen mit `chunks.json` und `manifest.json` durch `.gitignore` ausgeschlossen. Im Repository ist kein bestätigter Deployment-Schritt dokumentiert, der sie automatisch bereitstellt.
- **Erwartetes Verhalten:** Jede Zielumgebung erhält reproduzierbar genau die validierten produktiven Diagnose- und Agentenindizes.
- **Mögliche Ursachen:** Die generierten Artefakte wurden bewusst nicht versioniert; ein separater Artefakt- oder Build-Prozess ist noch zu verifizieren.
- **Nächster Prüfschritt:** Aktuelles Deployment prüfen und eine eindeutige, getestete Bereitstellungsstrategie dokumentieren.
- **Betroffene Dateien:** `.gitignore`, `README.md`, `app/rag_service.py`, `scripts/build_index.py`, `scripts/compare_indexes.py`.

## UX-001 – Reale Geräte- und Druckabnahme ist noch nicht vollständig bestätigt

- **Status:** Investigating
- **Beobachtung:** Automatisierte Tests prüfen Templates, mobile CSS-Verträge und drei Berichtsseiten. Eine vollständige visuelle Freigabe in Chrome/Android, Safari/iPhone und unterschiedlichen Druckdialogen ist laut bestehender Projektdokumentation noch offen.
- **Erwartetes Verhalten:** Mobile Karten stapeln sauber, Touch-Ziele bleiben nutzbar und der normale Bericht bleibt ohne abgeschnittene Inhalte auf drei A4-Seiten.
- **Mögliche Ursachen:** Browser- und Druckengine-Unterschiede können nur begrenzt durch strukturelle Tests abgedeckt werden.
- **Nächster Prüfschritt:** Definierte Browser-/Gerätematrix manuell prüfen und Ergebnisse dokumentieren.
- **Betroffene Dateien:** `app/templates/results.html`, `app/templates/report.html`, `app/static/styles.css`, `tests/test_ux_journey.py`, `tests/test_product_finalization.py`.
