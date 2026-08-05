# AI Start Map – Projektstand

**Last Updated:** 2026-08-05
**Verifizierter Code-Stand:** Branch `agent/complete-diagnostic-architecture`, Commit `6320ad0`
**Pflegehinweis:** Diese Datei beschreibt ausschließlich den bestätigten heutigen Stand. Planung, offene Probleme, Entscheidungen und Änderungshistorie stehen in `docs/`.

## Produktstand

AI Start Map ist als diagnostische Webanwendung für Solo-Selbstständige und kleine Betriebe implementiert. Die Anwendung betrachtet einen konkreten Geschäftsprozess, diagnostiziert den Engpass und erzeugt einen priorisierten ersten Schritt, konkrete KI-Unterstützung, einen Wochentest und eine spätere Automatisierungsmöglichkeit.

Der vollständige Kernflow ist implementiert und automatisiert getestet. Die fachliche Qualität des Recommendation Layers ist jedoch noch nicht zufriedenstellend. Insbesondere werden nicht in jedem Fall die besten konkreten KI-Workflows gewählt. Der aktuelle Stand ist deshalb ein funktionsfähiger Diagnose- und Ergebnisflow, aber noch kein fachlich finalisierter Recommendation Layer.

Die Fachanalyse vom 2026-08-05 hat zwölf Problemfamilien analysiert und zehn Solution Patterns fachlich definiert. Die vollständige Grundlage liegt unter `docs/product/AI_Start_Map_Fachgrundlage_Painpoints_Solutions_2026-08-05.md`; die technische Vorbereitung steht unter `docs/specs/solution-pattern-recommendation/`. Diese Inhalte sind dokumentiert, aber weder implementiert noch in den Laufzeitpfad integriert. Der Recommendation Layer ist technisch unverändert.

AI Start Map führt keine Unternehmensprozesse autonom aus. Preis-, Vertrags-, Zahlungs-, Qualitäts- und Freigabeentscheidungen bleiben beim Menschen.

## Sichtbarer Nutzerflow

Der implementierte Flow lautet:

1. Landingpage.
2. Freie Erzählung per Text oder optionaler Browser-Spracherkennung.
3. Erkennung von höchstens drei Prozessoptionen.
4. Auswahl genau eines Prozesses.
5. Kurze Zusammenfassung des heutigen Prozesses als vertikale HTML-/CSS-Prozesslinie.
6. Bestätigung oder Korrektur.
7. Null bis wenige relevante Rückfragen, einzeln angezeigt.
8. Sichtbarer Analysezustand mit Statusabfrage und Retry.
9. Ergebnis in der Reihenfolge Problem, erste Änderung, konkrete KI-Unterstützung, Wochentest und spätere Automatisierung.
10. Optionaler Startplan, Details, Druck-/PDF-Bericht, weiterer Prozess und Kontakt per `mailto:`.

Texteingabe bleibt immer verfügbar. Die numerische Session-ID wird in der öffentlichen Journey nicht angezeigt.

## Technischer Stand

- Backend: Python, FastAPI und Jinja2.
- Datenbank: PostgreSQL mit SQLAlchemy 2.x und Alembic.
- Validierung: Pydantic Structured Outputs.
- Persistenz: die fünf Tabellen `sessions`, `interview_questions`, `process_options`, `analyses` und `automation_opportunities`.
- Variable Ergebnisdaten liegen in den vorhandenen JSONB-Feldern; für den aktuellen Kernoutput war keine zusätzliche Tabelle erforderlich.
- Frontend: serverseitig gerenderte Templates, CSS und kleines Browser-JavaScript ohne Frontend-Framework.
- Spracheingabe: `SpeechRecognition`/`webkitSpeechRecognition` als optionale Browser-Erweiterung.
- PDF: kundenseitige Druckansicht mit drei HTML-Seiten und `window.print()`; keine PDF-Bibliothek.
- OpenAI: Structured Outputs für Prozesserkennung, Prozessverständnis, Rückfragen und finale Analyse; Embeddings für semantisches Retrieval.
- Die finale Analyse läuft in einem synchronen FastAPI-Request. Eine Queue oder ein Background-Worker ist nicht implementiert.

## Diagnose-RAG

- Ein produktiver Diagnoseindex ist lokal unter `data/vector_index/` vorhanden.
- Das verifizierte Manifest nennt 634 Diagnose-Chunks und `text-embedding-3-small`.
- Diagnosewissen und Agentenwissen sind in getrennten FAISS-Indizes gespeichert.
- Die Diagnose-Retrieval-Kette ist aktiv: `search_diagnostic_knowledge()` ruft `retrieve_chunks()` auf; die Ergebnisse werden bereinigt und als internes Vergleichswissen an Rückfrage- beziehungsweise Analyseprompts übergeben.
- Evaluationen sind ausdrücklich vom Indexieren ausgeschlossen. Das wird durch Pfad-/Markerprüfungen und Tests abgesichert.
- RAG-Evidenz bleibt technisch getrennt von Nutzerfakten und darf nicht als Tatsache über den aktuellen Betrieb erscheinen.
- Interne Chunk-IDs, Batch-IDs, Dateinamen, URLs und Metadaten werden vor der Promptübergabe beziehungsweise sichtbaren Ausgabe gefiltert und zusätzlich validiert.
- Die erzeugten Verzeichnisse unter `data/` werden von Git ignoriert. Ob und wie ein sauberer Checkout die produktiven Indizes in jeder Zielumgebung erhält, ist noch zu verifizieren.

## Agentenstand

- Zulässige Aktionen: `ASK`, `CLARIFY`, `RETRIEVE`, `ANALYZE`, `STOP`.
- Die Entscheidungen erfolgen aktuell überwiegend deterministisch in Python über `evaluate_readiness_and_next_action()`.
- Die drei internen Agentenwerkzeuge sind Python-Funktionen:
  - `extract_process_state`
  - `search_diagnostic_knowledge`
  - `evaluate_readiness_and_next_action`
- Es existiert noch kein echtes LLM-Function-Calling.
- Budgets, No-Repeat, Schleifenstopp, Fact-Immutability und das Verbot autonomer Ausführung werden deterministisch durch Python-Regeln durchgesetzt.
- Normal sind null bis zwei Rückfragen; drei sind für komplexe Fälle vorgesehen; vier sind die technische sichtbare Obergrenze.
- Der Agent-Pattern-Index ist gebaut. Sein Manifest nennt 205 Patterns und `text-embedding-3-small`.
- `retrieve_agent_patterns()` existiert in `app/rag_service.py`, wird aber im Repository nirgends aufgerufen.
- Der Agent-Pattern-Index beeinflusst die Laufzeitentscheidung daher derzeit nicht.
- Die Batch-04-Datei `03_next_question_patterns.jsonl` wird direkt für Fragevorlagen gelesen; dies ist kein semantisches Agent-Pattern-Retrieval.

## Gebaut, aber noch nicht aktiv

- Agent-Pattern-Index mit 205 Patterns.
- `retrieve_agent_patterns()` als Retrieval-Funktion für diesen Index.
- Weitere Batch-04-Agentenpatterns, die derzeit vor allem als Forschungs-, Index- und Policy-Testmaterial dienen.
- Strukturierter Recommendation-Katalog mit zwölf Problemfamilien, zehn Solution Patterns und vollständiger Matrix unter `knowledge/structured/`.
- Typisierter Loader, sechs Decision Gates und deterministischer Selector in `app/recommendation_service.py`; die Laufzeitintegration in Analyse und Kundenausgabe ist noch nicht abgeschlossen.

Nicht implementiert sind echtes Function Calling, ein LLM-gesteuerter dynamischer Agent und End-to-End-Tracing.

## Fachlich definiert, aber noch nicht implementiert

- Zwölf voneinander abgegrenzte Problemfamilien (`PF-01` bis `PF-12`).
- Zehn Solution Patterns (`SP-01` bis `SP-10`).
- Getrennte Gates für Vorgangsanker, Kanaleignung, Prozess-/Datenreife, Risiko, Regelstabilität und menschliche Freigabe.
- Trennung von Diagnose-RAG und strukturiertem Solution-Katalog.
- Recommendation-Feature-Spec mit Requirements, Design, Tasks und Acceptance Criteria.

## Bekannte Einschränkungen

- Der Recommendation Layer ist fachlich noch nicht zufriedenstellend.
- Der Hausmeisterfall empfiehlt teilweise zu viel manuelle Ablage.
- „Ordnung vor Automatisierung“ wird teilweise zu stark angewandt.
- Ein kuratierter Solution-Pattern-Katalog fehlt.
- Kundensprache ist teilweise zu technisch oder zu lang.
- Ergebnisansicht und PDF sind teilweise zu groß oder textlastig.
- Das System erkennt Probleme teilweise korrekt, wählt aber nicht immer den besten konkreten KI-Workflow.
- Agent-Pattern-Retrieval ist nicht in die Laufzeit eingebunden.
- Die visuelle Abnahme auf realen mobilen Browsern und in unterschiedlichen Druckdialogen ist noch nicht vollständig verifiziert.

Die vollständige, pflegbare Liste steht in `docs/KNOWN_ISSUES.md`.

## Letzter verifizierter Teststand

- Datum: 2026-08-05.
- Befehl: `.venv\Scripts\python.exe -m pytest -q`.
- Ergebnis: **83 Tests bestanden in 12,64 Sekunden**.
- Laut Testkonfiguration und README werden OpenAI- und Embedding-Aufrufe in den automatisierten Tests gemockt; bei diesem Lauf wurden keine externen API- oder Embedding-Aufrufe ausgeführt.
- Nicht Bestandteil dieser Verifikation: vollständige manuelle Browser-/Geräteabnahme sowie ein Deployment aus einem frischen Checkout.
