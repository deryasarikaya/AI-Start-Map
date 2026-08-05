# Known Issues

**Last Updated:** 2026-08-05

Diese Datei enthält alle bestätigten aktuell nicht funktionierenden, unzureichenden oder noch nicht eingebundenen Punkte: technische Probleme, fachliche Qualitätsprobleme, UX-Probleme und inaktive Komponenten.

Ein Problem darf erst entfernt werden, wenn:

1. es technisch oder fachlich behoben wurde,
2. ein passender Test erfolgreich war,
3. die Änderung in `docs/CHANGELOG.md` dokumentiert wurde.

Offene oder teilweise gelöste Probleme bleiben mit einem der Statuswerte `Open`, `Investigating`, `In Progress`, `Partially Fixed`, `Blocked` oder `Verified Fixed` enthalten.

## KI-001 – Recommendation Layer liefert noch keine durchgehend gute Auswahl

- **Status:** Open
- **Beobachtung:** Der aktuelle Recommendation Layer ist fachlich noch nicht zufriedenstellend. Er erkennt den Engpass häufig plausibel, priorisiert aber nicht in jedem Fall den besten konkreten nächsten KI-Workflow.
- **Erwartetes Verhalten:** Aus bestätigtem Problem, Ursache, Reifegrad und Voraussetzungen wird ein kleiner, konkreter und betrieblich passender erster Workflow gewählt.
- **Mögliche Ursachen:** Die Fachanalyse belegt mehrere zusammenwirkende Ursachen: Kanaleignung und Prozess-/Datenreife werden vermischt; `automation_pattern` ist im Analyse-Retrieval nicht verpflichtend; defensive Chunktypen konkurrieren im selben Top-k; der Prompt verlangt keinen systematischen Anker-/Kanal-Gegencheck; genau drei Opportunities können schwächere Empfehlungen erzwingen; `required_prerequisites` kann Voraussetzungen aufblähen; ein normalisierter Solution-Katalog fehlt.
- **Nächster Prüfschritt:** Die vorbereitete Recommendation-Spec fachlich freigeben und anschließend Gates, Katalogvertrag und reproduzierbare Auswahltests technisch spezifizieren.
- **Betroffene Dateien:** `app/openai_service.py`, `app/rag_service.py`, `app/schemas.py`, `tests/test_product_finalization.py`, `tests/test_quality_pass.py`.

## KI-002 – Hausmeisterfall empfiehlt teilweise zu viel manuelle Ablage

- **Status:** Investigating
- **Beobachtung:** Im Hausmeisterfall wird teilweise manuelle Ablage priorisiert, obwohl konkretere digitale oder KI-gestützte Unterstützung geprüft werden sollte.
- **Erwartetes Verhalten:** Das System berücksichtigt den vorhandenen digitalen Reifegrad und wählt den kleinsten sinnvollen digitalen oder KI-gestützten Workflow, sofern die Voraussetzungen bereits bestehen.
- **Mögliche Ursachen:** Kanaleignung und Gesamt-Prozessreife werden vermischt. Defensive Minimalverbesserungen konkurrieren mit konkreten Mustern im selben Top-k, der Prompt erzwingt keinen Anker-/Kanal-Gegencheck und es fehlt ein normalisierter Katalog, der `SP-03` als eigenständige mobile Einsatzdokumentation priorisiert.
- **Nächster Prüfschritt:** Den fachlich bestätigten Hausmeister-Akzeptanzfall technisch als reproduzierbaren Auswahltest spezifizieren; Implementierung erst nach Review der Gates und des Katalogvertrags.
- **Betroffene Dateien:** `knowledge/research_batches/batch_03_diagnostic_depth/02_rag_corpus.jsonl`, `app/rag_service.py`, `app/openai_service.py`. Ein spezifischer automatisierter Hausmeister-Qualitätstest ist noch zu verifizieren beziehungsweise anzulegen.

## KI-003 – „Ordnung vor Automatisierung“ wird teilweise zu stark angewandt

- **Status:** Open
- **Beobachtung:** Die bestehende Regel kann dazu führen, dass Ordnung oder manuelle Standardisierung empfohlen wird, obwohl ein Betrieb bereits ausreichend digital arbeitsfähig ist.
- **Erwartetes Verhalten:** Ordnung ist Voraussetzung, wenn sie tatsächlich fehlt; sie ersetzt aber keine passende KI-Unterstützung. Nicht jeder Betrieb beginnt auf Reifegrad 1.
- **Mögliche Ursachen:** Die Fachanalyse belegt eine Vermischung von Kanaleignung, Prozess-/Datenreife und Automationsreife. Defensive Chunktypen konkurrieren im selben Top-k; `required_prerequisites` kann Mindestvoraussetzungen zu einer allgemeinen Ordnungsphase aufblähen; ein expliziter Gegencheck auf einen bereits vorhandenen oder leicht herstellbaren Vorgangsanker fehlt.
- **Nächster Prüfschritt:** Die getrennten Reife- und Eignungsgates fachlich freigeben und danach gegen Fälle mit bereits ausreichender digitaler Reife testen.
- **Betroffene Dateien:** `app/openai_service.py`, `app/schemas.py`, `app/agent_service.py`, `knowledge/research_batches/batch_03_diagnostic_depth/02_rag_corpus.jsonl`.

## KI-004 – Strukturierter Solution-Pattern-Katalog fehlt

- **Status:** Open
- **Beobachtung:** Zwölf Problemfamilien und zehn Solution Patterns sind inzwischen fachlich dokumentiert. Ein normalisierter, validierter Katalog ist jedoch weder als strukturierte Produktionsdatei umgesetzt noch in die Laufzeit integriert.
- **Erwartetes Verhalten:** Der Recommendation Layer wählt aus einem fachlich freigegebenen strukturierten Katalog über Applicability- und Exclusion-Gates passende konkrete Workflows aus und begründet sie.
- **Mögliche Ursachen:** Die fachliche Grundlage wurde bewusst vor die technische Integration gestellt. Der aktuelle Laufzeitpfad besitzt deshalb weiterhin keinen normalisierten Solution-Katalog.
- **Nächster Prüfschritt:** Fachreview abschließen, minimales Schema und Speicherformat beschließen und erst danach die strukturierte Katalogdatei implementieren.
- **Betroffene Dateien:** `docs/product/AI_Start_Map_Fachgrundlage_Painpoints_Solutions_2026-08-05.md`, `docs/specs/solution-pattern-recommendation/`; mögliche spätere Codepunkte `app/rag_service.py`, `app/openai_service.py`, `app/schemas.py` und Tests sind noch technisch zu verifizieren.

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
- **Mögliche Ursachen:** Es fehlt eine integrierte Zuordnung Problemfamilie → Solution Pattern. `automation_pattern` ist im Analyse-Retrieval nicht verpflichtend, defensive Chunktypen konkurrieren im selben Top-k und genau drei Opportunities können schwächere Empfehlungen erzwingen. Der Prompt fordert keinen systematischen Anker-/Kanal-Gegencheck.
- **Nächster Prüfschritt:** Für Hausmeister, Schuhmacher und Massagesalon getrennte Diagnose- und Solution-Auswahltests aus den fachlich bestätigten Acceptance Criteria ableiten.
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
