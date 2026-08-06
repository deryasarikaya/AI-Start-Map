# AI Start Map – Projektstand

**Last Updated:** 2026-08-06
**Verifizierter Code-Stand:** Branch `feature/gate-cascade-quality`; Knowledge nach Runtime, Candidates, Evaluation und Archive geordnet; Phase-1-RAG-Zuverlässigkeit und semantische Problemklassifikation integriert; vollständige Suite mit 121 Tests grün
**Pflegehinweis:** Diese Datei beschreibt den bestätigten heutigen Stand. Planung, offene Probleme, Entscheidungen und Änderungshistorie stehen in den übrigen Dokumenten unter `docs/`.

## Produktstand

AI Start Map ist als diagnostische Webanwendung für Solo-Selbstständige und kleine Betriebe implementiert. Die Anwendung betrachtet einen konkreten Geschäftsprozess, trennt bestätigte Fakten von fachlicher Ableitung und Vergleichswissen und liefert genau eine dominante Hauptempfehlung.

Das Kundenergebnis zeigt den besten KI-Hebel, einen kurzen Grund, Heute/Mit KI, Eingabe, KI-Aufgabe, sichtbares Ergebnis, menschliche Prüfung, eine konkrete Ergebnisvorschau, bis zu drei Nutzenpunkte, nur echte Voraussetzungen und einen Umsetzungsweg. Es gibt keinen Wochentest. Weitere Möglichkeiten sind optional und auf zwei begrenzt.

AI Start Map führt keine Unternehmensprozesse autonom aus. Preis-, Vertrags-, Zahlungs-, Qualitäts-, Personal-, Sicherheits-, Herausgabe- und Freigabeentscheidungen bleiben beim Menschen.

## Sichtbarer Nutzerflow

1. Landingpage und freie Erzählung per Text oder optionaler Browser-Spracherkennung.
2. Auswahl eines erkannten Prozesses.
3. Bestätigung oder Korrektur einer kurzen vertikalen HTML-/CSS-Prozesslinie.
4. Normal null bis zwei, bei komplexen Fällen höchstens drei und technisch maximal vier entscheidungsrelevante Rückfragen.
5. Sichtbarer Analysezustand mit Statusabfrage und Retry.
6. Eine kompakte Hauptlösung mit Vorher/Nachher, Vier-Schritt-KI-Ablauf und greifbarer Vorschau.
7. Eingeklappter Umsetzungsweg, optionale weitere Möglichkeiten, Details, Druckbericht und Kontakt per `mailto:`.

Texteingabe bleibt immer verfügbar. Die numerische Session-ID wird in der öffentlichen Journey nicht angezeigt. Alle sichtbaren Ergebnistexte verwenden direkte Du-Ansprache.

## Recommendation Layer

- `knowledge/runtime/recommendation_catalog.json` enthält exakt zwölf Problemfamilien `PF-01` bis `PF-12`, zehn Solution Patterns `SP-01` bis `SP-10` und die vollständige Zuordnungsmatrix.
- `app/recommendation_service.py` validiert Anzahl, IDs, Referenzen, Kernfelder und Evaluationstrennung.
- `app/llm_classification.py` klassifiziert die bestätigte Erzählung primär per Structured Output in ein bis drei Katalog-Problemfamilien und die bestehenden sechs Gate-Werte. Bei `AIServiceError` bleiben Keyword-Klassifikation und alte Gate-Inferenz der konservative Fallback.
- Vorgangsanker, Kanaleignung, Prozess-/Datenreife, Fehlerauswirkung, Regelstabilität und menschliche Freigabe bleiben getrennte typisierte Gates.
- Der deterministische Selector liefert Hauptlösung, höchstens zwei sekundäre Kandidaten, Ausschlussgründe, Voraussetzungen und Freigabegrenzen.
- Der Selector ist in den produktiven Analysepfad integriert. Seine Vorauswahl wird dem finalen Structured-Output-Aufruf getrennt von Nutzerfakten und RAG-Evidenz übergeben.
- Der neue Kernoutput wird ohne Migration in bestehendem JSONB gespeichert. Alte Analysen mit früherem Kernoutput bleiben über die View-Abbildung lesbar.

## Diagnose-RAG und Agent

- Der Diagnoseindex umfasst laut Manifest 634 Chunks; der getrennte Agent-Pattern-Index umfasst 205 Patterns.
- Die Knowledge-Struktur trennt direkt geladene Dateien unter `knowledge/runtime/`, noch nicht integrierte Fachkandidaten unter `knowledge/candidates/`, niemals indexierbare Test- und Demo-Fälle unter `knowledge/evaluation/` und Herkunftsartefakte unter `knowledge/archive/`.
- Der bestehende Diagnoseindex wurde nicht neu gebaut und basiert weiterhin auf dem bisherigen Korpus, dessen Quellen jetzt archiviert sind. `app/rag_service.py` liest diese Archivquellen vorübergehend weiter, damit Indexprüfung und bestehende Buildpfade funktionieren; `archive/` ist daher noch nicht technisch unbenutzt.
- Der Batch-09-Research-Auftrag liegt nur als Kandidat vor. Es sind keine Batch-09-Ergebnisse, Loader oder Indexinhalte integriert.
- Diagnose- und Agentenindex werden pro Prozess und Indexverzeichnis im Speicher wiederverwendet. Ändert sich die mtime der FAISS- oder Metadatendatei, wird der betroffene Cache beim nächsten Abruf neu geladen; fehlende Dateien bleiben ein Konfigurationsfehler.
- Vor jeder Übernahme validierter Testindizes werden beide aktuellen Produktionsindizes vollständig unter `data/index_backups/<timestamp>/diagnostic/` und `data/index_backups/<timestamp>/agent/` gesichert. Jeder Promote erzeugt ein neues Backup; das historische Pre-Batch-04-Archiv bleibt unverändert.
- Die Analyse-Retrieval-Auswahl reserviert Diagnosemuster, konkretes Automationsmuster, Implementierungsvoraussetzung und Guardrail, bevor weitere Treffer auffüllen.
- Chunks, deren Inhalt nach der Promptbereinigung leer ist, werden einzeln übersprungen; gültige Chunks behalten ihre Originalzuordnung.
- Konkrete Solution-Auswahl erfolgt nicht aus zufälligem Top-k, sondern aus Problemfamilien, Gates und Katalog.
- `retrieve_agent_patterns()` wird im Interviewpfad kontrolliert aufgerufen. Erlaubte Entscheidungs-, Frage-, Widerspruchs-, Stop-, Werkzeug- und Guardrail-Muster unterstützen den internen Fragekontext.
- Budgets, No-Repeat, Schleifenstopp, Fact-Immutability, Stopwunsch, Verbot autonomer Ausführung und kritische Freigabegrenzen bleiben deterministisch in Python.
- Echtes OpenAI Function Calling ist nicht integriert. Der bestehende sichere Controller mit optionalem Pattern-Retrieval wurde bewusst beibehalten; Function Calling bleibt ein getrennt zu evaluierender Schritt.
- Evaluationen bleiben außerhalb beider Indizes. RAG- und Agentenwissen werden niemals zu Nutzerfakten.

## Technik und Persistenz

- Python, FastAPI, Jinja2, PostgreSQL, SQLAlchemy 2.x, Alembic und Pydantic.
- Die fünf Tabellen `sessions`, `interview_questions`, `process_options`, `analyses` und `automation_opportunities` bleiben unverändert.
- Neue Analysen speichern eine primäre Opportunity-Zeile und null bis zwei optionale sekundäre Zeilen.
- Keine Datenbankmigration, kein Solution-FAISS-Index, keine neuen Embeddings und keine neue Produktionsabhängigkeit wurden benötigt.
- Die finale Analyse läuft weiterhin synchron im FastAPI-Request; Queue oder Background-Worker sind nicht implementiert.

## Ergebnisoberfläche und Bericht

- Die Hauptseite zeigt genau eine dominante Empfehlung, kurze Begründung, Heute/Mit KI, vier Rollen im KI-Ablauf, konkrete Musterkarte, Nutzen, optionale Voraussetzungen und eine klare Umsetzungsaktion.
- Weitere Möglichkeiten und Diagnosekontext sind progressiv eingeklappt.
- Mermaid bleibt ausgeschlossen. Validierte strukturierte Schritte werden als responsive HTML-/CSS-Darstellung gerendert.
- Der Browserbericht nutzt zwei Kernseiten. Seite 3 wird nur bei mindestens einer sekundären Möglichkeit gerendert; ein alleiniger späterer Ausbau bleibt auf Seite 2.
- PDF-Speicherung erfolgt weiterhin über `window.print()`; Kontakt bleibt ein normaler `mailto:`-Link ohne behaupteten automatischen Anhang.

## Verifikation

- Das reproduzierbare Evaluation-Harness umfasst 91 getrennte Fälle. Alle 91 Label-Einträge stehen auf `confirmed: false`; 40 vorbelegte PF-/SP-Zuordnungen sind Vorschläge und keine bestätigte Ground Truth.
- Vollständige Testsuite: `121 passed` am 2026-08-06; die Demo-Tests mocken den vorgeschalteten Klassifikator.
- Phase-1-RAG-Regression: vier isolierte Tests für leere Chunks, zwei vollständige Promote-Backups, mtime-Cache-Invalidierung und fehlende Dateien bestanden.
- Keyword-Evaluation nach Phase 1: PF Top-1 28 %, PF Top-3 38 %, SP Top-1 30 %, PF-01-Default 48 %, verbotene Inhalte 0 von 91; damit gegenüber der Keyword-Baseline fachlich unverändert.
- Vorhandenes LLM-Eval-Artefakt: PF Top-1 65 %, PF Top-3 85 %, SP Top-1 70 %, PF-01-Default 3 %, zwei Klassifikatorfehler und ein Treffer eines verbotenen Begriffs. Dieser kostenpflichtige Lauf wurde in der aktuellen Sicherungsarbeit nicht wiederholt; seine Labels sind weiterhin unbestätigte Vorschläge.
- Python-Kompilierung: `python -m compileall app scripts` bestanden.
- App-Start gegen die separate Testdatenbank geprüft; Landingpage antwortete mit HTTP 200.
- Visuell geprüft: Ergebnis bei Desktop- und schmalem Mobile-Viewport; Karten stapeln, lange Texte brechen um, kein horizontaler Seitenüberlauf, Touch-Ziele 48–58 Pixel.
- Visuell geprüft: Bericht ohne sekundäre Möglichkeit rendert zwei Seiten und verschiebt den späteren Ausbau auf Seite 2.
- Nicht behauptet: vollständige Freigabe auf physischem Android/iPhone, Safari sowie allen nativen Druckdialogen.

## Weiterhin offen

- Echtes Function Calling und ein LLM-gesteuerter Tool-Loop.
- Kalibrierung von Klassifikationsheuristiken, Gates und Fragezahl mit realen AI-Start-Map-Interviews.
- Vollständige geräte- und browserübergreifende Druckabnahme.
- Verteilung beziehungsweise Bereitstellung der gitignorierten produktiven Indexartefakte in einer sauberen Zielumgebung.
