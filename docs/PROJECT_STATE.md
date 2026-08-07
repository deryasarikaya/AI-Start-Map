# AI Start Map – Projektstand

**Last Updated:** 2026-08-07
**Verifizierter Code-Stand:** Branch `feature/gate-cascade-quality`; semantische Problemklassifikation, deterministische Ausschlüsse und fallbezogene Rangfolge der zulässigen Muster aktiv
**Pflegehinweis:** Diese Datei beschreibt den bestätigten heutigen Stand. Planung, offene Probleme, Entscheidungen und Änderungshistorie stehen in den übrigen Dokumenten unter `docs/`.

## Produktstand

AI Start Map ist als diagnostische Webanwendung für Solo-Selbstständige und kleine Betriebe implementiert. Die Anwendung betrachtet einen konkreten Geschäftsprozess, trennt bestätigte Fakten von fachlicher Ableitung und Vergleichswissen und liefert genau eine dominante Hauptempfehlung.

Das Kundenergebnis basiert intern weiterhin auf `recommendation-v3`, zeigt aber sieben verständliche Kernblöcke: Engpass, bestätigter heutiger Ablauf, Empfehlung, drei bis sechs Zukunftsschritte, durchgespielte Veranschaulichung, menschliche Kontrolle und kleinster Einstieg. Interne Rollen-, Technik- und Autonomiefelder bleiben gespeichert, werden Kunden jedoch nicht roh gezeigt. Voraussetzungen, höchstens drei wichtige offene Fragen, Grenzen und späterer Ausbau stehen ausschließlich im Bericht; sekundäre Möglichkeiten werden auf der Hauptseite nicht gezeigt.

AI Start Map führt keine Unternehmensprozesse autonom aus. Preis-, Vertrags-, Zahlungs-, Qualitäts-, Personal-, Sicherheits-, Herausgabe- und Freigabeentscheidungen bleiben beim Menschen.

## Sichtbarer Nutzerflow

1. Landingpage und freie Erzählung per Text oder optionaler Browser-Spracherkennung.
2. Auswahl eines erkannten Prozesses.
3. Bestätigung oder Korrektur einer kurzen vertikalen HTML-/CSS-Prozesslinie.
4. Normal null bis zwei, bei komplexen Fällen höchstens drei und technisch maximal vier entscheidungsrelevante Rückfragen.
5. Sichtbarer Analysezustand mit Statusabfrage und Retry.
6. Eine kompakte Hauptlösung mit sieben sichtbaren Blöcken: Engpass, bestätigter Ist-Ablauf, Empfehlung, zukünftiger Ablauf, Veranschaulichung, menschliche Kontrolle und kleinster Einstieg.
7. Kompakter Kontakt am Ende und ein Druckbericht mit höchstens zwei Seiten.

Texteingabe bleibt immer verfügbar. Die numerische Session-ID wird in der öffentlichen Journey nicht angezeigt. Alle sichtbaren Ergebnistexte verwenden direkte Du-Ansprache.

## Recommendation Layer

- `knowledge/runtime/recommendation_catalog.json` enthält exakt zwölf Problemfamilien `PF-01` bis `PF-12`, zehn Solution Patterns `SP-01` bis `SP-10` und die vollständige Zuordnungsmatrix.
- `app/recommendation_service.py` validiert Anzahl, IDs, Referenzen, Kernfelder und Evaluationstrennung.
- `app/llm_classification.py` klassifiziert die bestätigte Erzählung per Structured Output in null bis drei Katalog-Problemfamilien und die bestehenden sechs Rohsignale. Eine leere Familienliste ist die belegbare A0-Entscheidung „keine KI nötig“. Bei `AIServiceError` wird keine Keyword-Empfehlung ausgeliefert; die Nutzerin sieht eine Wiederholen-Seite und behält ihre bestätigten Angaben.
- `app/recommendation_service.py` übersetzt die Rohsignale deterministisch in `GATE-01` bis `GATE-06` mit `pass`, `fail` oder `unknown` und deutscher Begründung. Zielgruppenfit, Fehlerfolgen und menschliche Prüfung werden gesondert bewertet.
- Der Selector bildet aus der Matrix eine Kandidatenmenge und wendet Gates und Ausschlüsse vollständig in Python an. Nur diese zugelassenen Muster werden danach vom Modell anhand Kurzbeschreibung, positiven Varianten und Gegenbeispiel vollständig geordnet; eine unvollständige oder fremde Rangfolge ist ein sichtbarer Fehler. SP-04 ist ohne bestätigten Kundengegenstand in betrieblicher Obhut ausgeschlossen; Informationsträger und eigenes Einsatzmaterial zählen nicht.
- Der Selector ist in den produktiven Analysepfad integriert. Seine Vorauswahl, Output-Struktur, Stop Conditions und die zwölf katalogbasierten Failure Guardrails werden dem finalen Structured-Output-Aufruf getrennt von Nutzerfakten und RAG-Evidenz übergeben.
- Der finale Prompt enthält 15 inhaltliche Kernregeln statt wiederholter Schema- und Längenvorgaben. `gpt-5-mini` läuft für `FinalAnalysisResult` mit `reasoning_effort=medium`, maximal zwei Versuchen und 120 Sekunden Gesamtbudget.
- OUT-Feldnamen, Human Review, Nicht-Automationen und Sicherheitsgrenzen werden nach dem Modellaufruf aus Runtime-Kontext und Katalog nachgeführt. Die Veranschaulichung erfindet ausschließlich in ihrem klar gekennzeichneten Block eine zum Betrieb passende Eingangsnachricht und leitet daraus den fertigen Eintrag sowie fehlende Angaben ab. Katalog-Beispielwerte sind nur ein protokollierter Rückfall und gelten in der Evaluation als Fehlschlag.
- Der freie Betriebstyp aus der Klassifikation wird nur bei eindeutiger Übereinstimmung mit einem vorhandenen Runtime-Typ übernommen, persistiert und an Workflow-Auswahl und Retrieval weitergegeben. Ohne Treffer bleibt der Betriebstyp leer; ein fremdes Branchenbeispiel wird nicht angenähert.
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

- Die Hauptseite zeigt genau eine dominante Empfehlung und sieben sichtbare Kernblöcke. Der bereits bestätigte Ist-Ablauf steht offen direkt unter dem Engpass; wer was künftig tut, steht in den kurzen Zukunftsschritten. Eine rohe Rollentabelle und sichtbare sekundäre Vorschläge gibt es nicht mehr.
- Die Vorschau zeigt realistische, ausdrücklich als Beispiel gekennzeichnete deutsche Werte. Offene Angaben werden semantisch entdoppelt, auf drei begrenzt und nur im Bericht ausgegeben.
- Weitere Möglichkeiten und der bestätigte heutige Ablauf bleiben nachgeordnet und geschlossen; ein leerer Vorschlag wird nicht gerendert.
- Mermaid bleibt ausgeschlossen. Validierte strukturierte Schritte werden als responsive HTML-/CSS-Darstellung gerendert.
- Der Browserbericht umfasst höchstens zwei Seiten. Seite 1 enthält Diagnosehinweis, Engpass, Empfehlung, Zukunftsablauf und dieselbe gekennzeichnete Veranschaulichung. Seite 2 enthält menschliche Kontrolle, höchstens drei Voraussetzungen, höchstens drei echte Fragen, kleinsten Einstieg, späteren Ausbau und Kontakt. Browser-Kopf- und Fußzeilen lassen sich nicht per Seiten-CSS abschalten; der Druckhinweis nennt deshalb die notwendige Option.
- PDF-Speicherung erfolgt weiterhin über `window.print()`; Kontakt bleibt ein normaler `mailto:`-Link ohne behaupteten automatischen Anhang.

## Verifikation

- Das reproduzierbare Evaluation-Harness weist 91 Legacy-Fälle und 30 Batch-09-Fälle getrennt aus und mittelt ihre Werte nicht. Alle 40 vorbelegten Legacy-Zuordnungen stehen auf `confirmed: false`; Batch 09 bleibt `research_proposed`.
- Vollständige Testsuite am 2026-08-07 nach der Qualitätsüberarbeitung: `214 passed` in 27,57 Sekunden.
- Die fünf Mentor-Demofälle Hausmeister, Fotograf, Blumenladen, Coach und A0 liefen mit echten Modellaufrufen bis Ergebnis und Bericht durch. Der finale Blumenladenlauf wählte nach geschärfter PF-02-Abgrenzung SP-01; der Hausmeister blieb SP-03 und der Nicht-KI-Fall A0. Details und wörtliche Eingaben stehen in `docs/MENTOR_DEMO_2026-08-07.md`.
- Phase-1-RAG-Regression: vier isolierte Tests für leere Chunks, zwei vollständige Promote-Backups, mtime-Cache-Invalidierung und fehlende Dateien bestanden.
- Keyword-Evaluation nach Phase 1: PF Top-1 28 %, PF Top-3 38 %, SP Top-1 30 %, PF-01-Default 48 %, verbotene Inhalte 0 von 91; damit gegenüber der Keyword-Baseline fachlich unverändert.
- Aktuelle Keyword-Vergleichsmessung: Legacy 91 PF Top-1 28 %, irgendein PF-Treffer 38 %, SP Top-1 25 %, PF-01 48 %, verbotene Auswahltexte 0/91. Batch 09 getrennt: PF Top-1 40 %, irgendein Treffer 48 %, SP Top-1 36 %, PF-01 33 %. Die vier neuen bestätigten Auswahlfälle erreichen in dieser Vergleichsmessung PF Top-1 50 %, irgendein Treffer 75 %, SP Top-1 75 % und PF-01 0 %. Diese Heuristik ist kein Produktivpfad.
- Vorhandenes LLM-Eval-Artefakt: PF Top-1 65 %, PF Top-3 85 %, SP Top-1 70 %, PF-01-Default 3 %, zwei Klassifikatorfehler und ein Treffer eines verbotenen Begriffs. Dieser kostenpflichtige Lauf wurde in der aktuellen Sicherungsarbeit nicht wiederholt; seine Labels sind weiterhin unbestätigte Vorschläge.
- Kontrollierter Live-Vertragstest für den Hausmeisterfall: `gpt-5-mini`, `medium`, ein Versuch, 60,141 Sekunden, kein Retry, validiertes Ergebnis mit A1 und den sechs deterministischen OUT-SP03-Feldern. Diese Einzelbeobachtung ist keine belastbare Fehler- oder Latenzstatistik.
- Vier finale Unicode-End-to-End-Wiederholungen benötigten 83,968 bis 138,469 Sekunden einschließlich vorgelagerter Modellschritte. Eine exakte erfolgreiche Retry-Zahl wird nicht persistiert. Drei vorangegangene FinalAnalysis-Fehler nach jeweils beiden Versuchen deckten eine zu strikte Du-Validierung auf; betroffene Felder werden nun lokal repariert, ohne die Analyse zu verwerfen.
- Python-Kompilierung: `python -m compileall app scripts` bestanden.
- App-Start gegen die separate Testdatenbank geprüft; Landingpage antwortete mit HTTP 200.
- Die überarbeitete Oberfläche wurde in Chrome bei 1440 × 900 und 390 × 844 Pixeln auf Landingpage, Interview, Prozesswahl, Bestätigung, Verarbeitung und Ergebnis geprüft. Alle H1 lagen bei höchstens 42 Pixeln auf Desktop und 31,2 Pixeln mobil; keine Seite hatte horizontalen Überlauf.
- Landingpage, Interview, Prozessauswahl, Bestätigung, Verarbeitung, Blumenladen-Ergebnis und Bericht wurden bei 1440 × 900 und 390 × 844 geprüft: H1 maximal 42 beziehungsweise 31,2 Pixel, keine horizontale Scrollbar und kein alter Slogan. Der automatisiert mit ausgeschalteten Kopf-/Fußzeilen erzeugte Blumenladenbericht umfasst zwei Seiten ohne lokale URL. Hausmeister, Fotograf und Coach lieferten im aktuellen Modellpfad SP-03, SP-02 und SP-01; der kurze Blumenladen-Demolauf und A0 scheiterten in der Wiederholung an Modellvalidierung beziehungsweise Timeout und sind nicht als erfolgreich geprüft dokumentiert.
- Solution-Retrieval-Vergleich: je ausgewähltem Pattern waren drei Workflows zulässig und zwei wurden geliefert. Semantik und deterministische Auswahl lieferten in allen vier KI-Fällen dieselben zwei Workflows, nur in zwei Fällen in anderer Reihenfolge. Ein fachlicher Mehrwert des 27-Chunk-Indexes ist damit noch nicht belegt.
- Nicht behauptet: vollständige Freigabe auf physischem Android/iPhone, Safari sowie allen nativen Druckdialogen.

## Weiterhin offen

- Echtes Function Calling und ein LLM-gesteuerter Tool-Loop.
- Kalibrierung von Klassifikationsheuristiken, Gates und Fragezahl mit realen AI-Start-Map-Interviews.
- Vollständige geräte- und browserübergreifende Druckabnahme.
- Verteilung beziehungsweise Bereitstellung der gitignorierten produktiven Indexartefakte in einer sauberen Zielumgebung.
