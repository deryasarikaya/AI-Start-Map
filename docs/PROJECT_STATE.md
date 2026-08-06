# AI Start Map – Projektstand

**Last Updated:** 2026-08-07
**Verifizierter Code-Stand:** Branch `feature/gate-cascade-quality`; Batch-09-Knowledge-Rollen kontrolliert integriert; semantische Problemklassifikation und deterministischer Selector aktiv
**Pflegehinweis:** Diese Datei beschreibt den bestätigten heutigen Stand. Planung, offene Probleme, Entscheidungen und Änderungshistorie stehen in den übrigen Dokumenten unter `docs/`.

## Produktstand

AI Start Map ist als diagnostische Webanwendung für Solo-Selbstständige und kleine Betriebe implementiert. Die Anwendung betrachtet einen konkreten Geschäftsprozess, trennt bestätigte Fakten von fachlicher Ableitung und Vergleichswissen und liefert genau eine dominante Hauptempfehlung.

Das Kundenergebnis basiert auf `recommendation-v3` und zeigt Engpass, Begründung, konkrete Empfehlung, drei bis sechs Zukunftsschritte, getrennte Rollen für Nutzer, KI, normale Software/Regeln und Mensch, sichtbares Ergebnis, Vorschau, offene Angaben, Voraussetzungen, kleinste nutzbare Version, späteren Ausbau, Nicht-Automationen, Autonomiestufe und Unsicherheiten. Es gibt keinen Wochentest. Weitere Möglichkeiten sind optional und auf zwei begrenzt.

AI Start Map führt keine Unternehmensprozesse autonom aus. Preis-, Vertrags-, Zahlungs-, Qualitäts-, Personal-, Sicherheits-, Herausgabe- und Freigabeentscheidungen bleiben beim Menschen.

## Sichtbarer Nutzerflow

1. Landingpage und freie Erzählung per Text oder optionaler Browser-Spracherkennung.
2. Auswahl eines erkannten Prozesses.
3. Bestätigung oder Korrektur einer kurzen vertikalen HTML-/CSS-Prozesslinie.
4. Normal null bis zwei, bei komplexen Fällen höchstens drei und technisch maximal vier entscheidungsrelevante Rückfragen.
5. Sichtbarer Analysezustand mit Statusabfrage und Retry.
6. Eine kompakte Hauptlösung in der festen Reihenfolge Engpass, Empfehlung, zukünftiger Ablauf, konkretes Ergebnis, menschliche Prüfung, kleinster Einstieg, Voraussetzungen und Grenzen sowie späterer Ausbau.
7. Optionale weitere Möglichkeiten, Druckbericht, neuer Ablauf und Kontakt per `mailto:`.

Texteingabe bleibt immer verfügbar. Die numerische Session-ID wird in der öffentlichen Journey nicht angezeigt. Alle sichtbaren Ergebnistexte verwenden direkte Du-Ansprache.

## Recommendation Layer

- `knowledge/runtime/recommendation_catalog.json` enthält exakt zwölf Problemfamilien `PF-01` bis `PF-12`, zehn Solution Patterns `SP-01` bis `SP-10` und die vollständige Zuordnungsmatrix.
- `app/recommendation_service.py` validiert Anzahl, IDs, Referenzen, Kernfelder und Evaluationstrennung.
- `app/llm_classification.py` klassifiziert die bestätigte Erzählung primär per Structured Output in null bis drei Katalog-Problemfamilien und die bestehenden sechs Rohsignale. Eine leere Familienliste ist die belegbare A0-Entscheidung „keine KI nötig“. Bei `AIServiceError` bleiben Keyword-Klassifikation und Gate-Inferenz der konservative Fallback.
- `app/recommendation_service.py` übersetzt die Rohsignale deterministisch in `GATE-01` bis `GATE-06` mit `pass`, `fail` oder `unknown` und deutscher Begründung. Zielgruppenfit, Fehlerfolgen und menschliche Prüfung werden gesondert bewertet.
- Der deterministische Selector liefert A0 oder eine Hauptlösung, höchstens zwei sekundäre Kandidaten, Ausschlussgründe, Voraussetzungen, Stop Conditions, Autonomiestufe und Freigabegrenzen. SP-04 ist ohne bestätigten angenommenen, gelagerten, bearbeiteten oder abgeholten Gegenstand ausgeschlossen.
- Der Selector ist in den produktiven Analysepfad integriert. Seine Vorauswahl, Output-Struktur, Stop Conditions und die zwölf katalogbasierten Failure Guardrails werden dem finalen Structured-Output-Aufruf getrennt von Nutzerfakten und RAG-Evidenz übergeben.
- Der finale Prompt enthält 15 inhaltliche Kernregeln statt wiederholter Schema- und Längenvorgaben. `gpt-5-mini` läuft für `FinalAnalysisResult` mit `reasoning_effort=medium`, maximal zwei Versuchen und 120 Sekunden Gesamtbudget.
- OUT-Feldnamen, Human Review, Nicht-Automationen, Autonomiestufe, kleinste Version und regelbasierte Komponenten werden nach dem Modellaufruf deterministisch aus Runtime-Kontext und Katalog nachgeführt. Nicht belegte Vorschauwerte werden als Beispiel markiert oder bleiben „noch offen“.
- Eine ausdrücklich genannte ausreichende vorhandene Funktion oder einfache Regel mit „keine KI nötig“ setzt den Selector auch bei einer abweichenden semantischen Familienzuordnung deterministisch auf A0. Der Kundenvertrag entfernt dann KI-Empfehlung und sekundäre Möglichkeiten.
- Kundenüberschriften werden aus dem Katalognamen nachgeführt. Interne PF-/SP-/OUT-IDs werden sowohl bei neuen Outputs als auch in der View bereits gespeicherter Analysen unterdrückt. Einzelne Zukunftsschritte dürfen bis 220 Zeichen lang sein, damit vollständige Sätze nicht an der früheren 140-Zeichen-Grenze in neue Listenpunkte zerfallen.
- Breite Lösungswortfilter verwerfen keine Analyse mehr. Erfundene Ist-Fakten in den weiterhin begrenzt geprüften Risikobegriffen und interne Referenzen neutralisieren nur das betroffene Feld und ergänzen einen offenen Hinweis.
- Der neue Kernoutput wird ohne Migration in bestehendem JSONB gespeichert. Alte Analysen mit früherem Kernoutput bleiben über die View-Abbildung lesbar.

## Diagnose-RAG und Agent

- Der Diagnoseindex umfasst laut Manifest 634 Chunks; der getrennte Agent-Pattern-Index umfasst 205 Patterns.
- Die Knowledge-Struktur trennt direkt geladene Dateien unter `knowledge/runtime/`, noch nicht integrierte Fachkandidaten unter `knowledge/candidates/`, niemals indexierbare Test- und Demo-Fälle unter `knowledge/evaluation/` und Herkunftsartefakte unter `knowledge/archive/`.
- Der bestehende Diagnoseindex wurde nicht neu gebaut und basiert weiterhin auf dem bisherigen Korpus, dessen Quellen jetzt archiviert sind. `app/rag_service.py` liest diese Archivquellen vorübergehend weiter, damit Indexprüfung und bestehende Buildpfade funktionieren; `archive/` ist daher noch nicht technisch unbenutzt.
- Die vollständige Batch-09-Lieferung bleibt unverändert als Kandidat erhalten. Kontrolliert generierte Runtime-Kopien enthalten 27 Inference Patterns, 28 Solution Workflows und 10 Output-Strukturen; 30 Evaluationen liegen ausschließlich unter `knowledge/evaluation/`. Herkunft, Normalisierungen und Reviewgrenzen stehen in `docs/BATCH_09_FACHPRUEFUNG.md`.
- `app/solution_knowledge.py` validiert und lädt die drei Runtime-Rollen. Output-Beispielwerte werden nicht in den Modell- oder Kundenkontext weitergegeben; SP-04 bleibt ein dokumentarischer Ausschluss.
- Der getrennte Solution-Workflow-Index enthält 27 positive Workflows. Eine Anfrage wird aus bestätigter Problemfamilie, ausgewähltem Solution Pattern, konkretem Engpass und erkannten digitalen Kanälen gebildet. Fehlt der Index, bleibt die deterministische Auswahl innerhalb desselben Patterns arbeitsfähig.
- Diagnose- und Agentenindex werden pro Prozess und Indexverzeichnis im Speicher wiederverwendet. Ändert sich die mtime der FAISS- oder Metadatendatei, wird der betroffene Cache beim nächsten Abruf neu geladen; fehlende Dateien bleiben ein Konfigurationsfehler.
- Vor jeder Übernahme validierter Testindizes werden beide aktuellen Produktionsindizes vollständig unter `data/index_backups/<timestamp>/diagnostic/` und `data/index_backups/<timestamp>/agent/` gesichert. Jeder Promote erzeugt ein neues Backup; das historische Pre-Batch-04-Archiv bleibt unverändert.
- Die Analyse-Retrieval-Auswahl reserviert Diagnosemuster, konkretes Automationsmuster, Implementierungsvoraussetzung und Guardrail, bevor weitere Treffer auffüllen.
- Chunks, deren Inhalt nach der Promptbereinigung leer ist, werden einzeln übersprungen; gültige Chunks behalten ihre Originalzuordnung.
- Konkrete Solution-Auswahl erfolgt nicht aus zufälligem Top-k, sondern aus Problemfamilien, Gates und Katalog.
- `retrieve_agent_patterns()` wird im Interviewpfad kontrolliert aufgerufen. Erlaubte Entscheidungs-, Frage-, Widerspruchs-, Stop-, Werkzeug- und Guardrail-Muster unterstützen den internen Fragekontext.
- Budgets, No-Repeat, Schleifenstopp, Fact-Immutability, Stopwunsch, Verbot autonomer Ausführung und kritische Freigabegrenzen bleiben deterministisch in Python.
- Echtes OpenAI Function Calling ist nicht integriert. Der bestehende sichere Controller mit optionalem Pattern-Retrieval wurde bewusst beibehalten; Function Calling bleibt ein getrennt zu evaluierender Schritt.
- Evaluationen bleiben außerhalb aller drei Indizes. RAG-, Agenten- und Solution-Wissen werden niemals zu Nutzerfakten.

## Technik und Persistenz

- Python, FastAPI, Jinja2, PostgreSQL, SQLAlchemy 2.x, Alembic und Pydantic.
- Die fünf Tabellen `sessions`, `interview_questions`, `process_options`, `analyses` und `automation_opportunities` bleiben unverändert.
- Neue Analysen speichern eine primäre Opportunity-Zeile und null bis zwei optionale sekundäre Zeilen; `recommendation-v3` bleibt in bestehendem JSONB.
- Vor den Mentor-Läufen wurden 35 Analysen gefunden: 17 mit `core_output`, davon 15 im alten und zwei im neuen Format. Nach den kontrollierten QA-Läufen liegen lokal 48 Analysen vor; 30 besitzen `core_output`, davon unverändert 15 im alten und 15 im neuen Format. Deshalb bleibt der Legacy-Shim aktiv. Er protokolliert nur erfundene Platzhalter, die Kundensicht unterdrückt sie, und kein v3-Feld wird für Altanalysen erfunden.
- Keine Datenbankmigration und keine neue Produktionsabhängigkeit wurden benötigt. Der kleine Solution-FAISS-Index wurde getrennt mit 27 Workflows und `text-embedding-3-small` gebaut; seine generierten Artefakte bleiben gitignoriert.
- Die finale Analyse läuft weiterhin synchron im FastAPI-Request; Queue oder Background-Worker sind nicht implementiert.

## Ergebnisoberfläche und Bericht

- Die Hauptseite zeigt genau eine dominante Empfehlung und führt in acht scanbaren Abschnitten von Engpass und Zukunftsablauf über Ergebnisvorschau und Human Check bis zum kleinsten Einstieg, Grenzen und späteren Ausbau.
- Nutzer-, KI-, Software-/Regel- und Menschenrolle stehen direkt am zukünftigen Ablauf; fehlende Angaben werden in der Vorschau und unter den Grenzen sichtbar offen gehalten.
- Weitere Möglichkeiten und Diagnosekontext bleiben nachgeordnet.
- Mermaid bleibt ausgeschlossen. Validierte strukturierte Schritte werden als responsive HTML-/CSS-Darstellung gerendert.
- Der Browserbericht spiegelt den v3-Vertrag: Seite 1 enthält Diagnosehinweis, Engpass, Empfehlung, Zukunftsablauf, Rollen und gekennzeichnete Vorschau; Seite 2 Human Check, kleinsten Einstieg, Voraussetzungen, Grenzen, offene Angaben und späteren Ausbau. Seite 3 wird nur bei mindestens einer sekundären Möglichkeit gerendert.
- PDF-Speicherung erfolgt weiterhin über `window.print()`; Kontakt bleibt ein normaler `mailto:`-Link ohne behaupteten automatischen Anhang.

## Verifikation

- Das reproduzierbare Evaluation-Harness weist 91 Legacy-Fälle und 30 Batch-09-Fälle getrennt aus und mittelt ihre Werte nicht. Alle 40 vorbelegten Legacy-Zuordnungen stehen auf `confirmed: false`; Batch 09 bleibt `research_proposed`.
- Vollständige Testsuite am 2026-08-07: `176 passed` in 260,08 Sekunden.
- Die fünf Mentor-Demofälle Hausmeister, Fotograf, Blumenladen, Coach und A0 liefen mit echten Modellaufrufen bis Ergebnis und Bericht durch. Der finale Blumenladenlauf wählte nach geschärfter PF-02-Abgrenzung SP-01; der Hausmeister blieb SP-03 und der Nicht-KI-Fall A0. Details und wörtliche Eingaben stehen in `docs/MENTOR_DEMO_2026-08-07.md`.
- Phase-1-RAG-Regression: vier isolierte Tests für leere Chunks, zwei vollständige Promote-Backups, mtime-Cache-Invalidierung und fehlende Dateien bestanden.
- Keyword-Evaluation nach Phase 1: PF Top-1 28 %, PF Top-3 38 %, SP Top-1 30 %, PF-01-Default 48 %, verbotene Inhalte 0 von 91; damit gegenüber der Keyword-Baseline fachlich unverändert.
- Aktuelle Keyword-Messung mit Gate-Kaskade: Legacy 91 weiterhin PF Top-1 28 %, irgendein PF-Treffer 38 %, SP Top-1 30 %, PF-01 48 %, verbotene Auswahltexte 0/91. Batch 09 getrennt: 25 Fälle mit vorgeschlagenen nicht bestätigten Labels, PF Top-1 40 %, irgendein PF-Treffer 48 %, SP Top-1 36 %, PF-01 33 %, verbotene Auswahltexte 0/30. Die schwache Keyword-Baseline bleibt nur Fallback.
- Vorhandenes LLM-Eval-Artefakt: PF Top-1 65 %, PF Top-3 85 %, SP Top-1 70 %, PF-01-Default 3 %, zwei Klassifikatorfehler und ein Treffer eines verbotenen Begriffs. Dieser kostenpflichtige Lauf wurde in der aktuellen Sicherungsarbeit nicht wiederholt; seine Labels sind weiterhin unbestätigte Vorschläge.
- Kontrollierter Live-Vertragstest für den Hausmeisterfall: `gpt-5-mini`, `medium`, ein Versuch, 60,141 Sekunden, kein Retry, validiertes Ergebnis mit A1 und den sechs deterministischen OUT-SP03-Feldern. Diese Einzelbeobachtung ist keine belastbare Fehler- oder Latenzstatistik.
- Vier finale Unicode-End-to-End-Wiederholungen benötigten 83,968 bis 138,469 Sekunden einschließlich vorgelagerter Modellschritte. Eine exakte erfolgreiche Retry-Zahl wird nicht persistiert. Drei vorangegangene FinalAnalysis-Fehler nach jeweils beiden Versuchen deckten eine zu strikte Du-Validierung auf; betroffene Felder werden nun lokal repariert, ohne die Analyse zu verwerfen.
- Python-Kompilierung: `python -m compileall app scripts` bestanden.
- App-Start gegen die separate Testdatenbank geprüft; Landingpage antwortete mit HTTP 200.
- Visuell geprüft: überarbeitete Ergebnisansicht bei Desktop- und schmalem Mobile-Viewport; H1 40/32 Pixel, H2 24 Pixel mobil, Karten und Rollen stapeln, lange Texte brechen um, kein horizontaler Seitenüberlauf, Hauptaktionen 48–55 Pixel.
- Visuell geprüft: Bericht ohne sekundäre Möglichkeit rendert zwei vollständige A4-Seiten und hält den späteren Ausbau auf Seite 2. Ein künstlich langer Sechs-Seiten-Fall enthielt keine leere Seite, abgeschnittene Karte oder Überlagerung.
- Visuell und textuell geprüft: die fünf finalen Mentor-Berichte umfassen zwei Seiten bei A0 und jeweils drei Seiten bei den vier A1-Fällen. Keine Seite war leer; HTML und PDF enthielten keine internen IDs oder Sitzungs-URLs.
- Solution-Retrieval-Vergleich: je ausgewähltem Pattern waren drei Workflows zulässig und zwei wurden geliefert. Semantik und deterministische Auswahl lieferten in allen vier KI-Fällen dieselben zwei Workflows, nur in zwei Fällen in anderer Reihenfolge. Ein fachlicher Mehrwert des 27-Chunk-Indexes ist damit noch nicht belegt.
- Nicht behauptet: vollständige Freigabe auf physischem Android/iPhone, Safari sowie allen nativen Druckdialogen.

## Weiterhin offen

- Echtes Function Calling und ein LLM-gesteuerter Tool-Loop.
- Kalibrierung von Klassifikationsheuristiken, Gates und Fragezahl mit realen AI-Start-Map-Interviews.
- Vollständige geräte- und browserübergreifende Druckabnahme.
- Verteilung beziehungsweise Bereitstellung der gitignorierten produktiven Indexartefakte in einer sauberen Zielumgebung.
