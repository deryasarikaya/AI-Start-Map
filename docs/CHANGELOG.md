# Changelog

**Last Updated:** 2026-08-07

Diese Datei dokumentiert nur tatsächlich ausgeführte und verifizierte Änderungen. Roadmap-Punkte gelten nicht als umgesetzt.

## 2026-08-07 – Musterauswahl fallbezogen bewertet und Ergebnis veranschaulicht

- Die Auswahl unter den durch Matrix und Python-Gates zugelassenen Solution Patterns von Listenreihenfolge auf einen strukturierten Modellvergleich umgestellt. Das Modell muss genau alle zugelassenen IDs mit Begründung ordnen; fremde, doppelte oder unvollständige Rangfolgen werden nicht ausgeliefert.
- Das physische Gate auf Kundengegenstände in betrieblicher Obhut begrenzt. Belege, Kassenzettel, Rechnungen, Fotos, Notizen und eigenes Einsatzmaterial lösen SP-04 nicht mehr aus; der Schuhmacherfall bleibt als positiver Obhutfall abgesichert.
- Den vom Modell erkannten Betriebstyp gegen die vorhandenen Runtime-Typen abgeglichen, persistiert und an Workflow-Auswahl und Retrieval weitergereicht. Ohne eindeutigen Treffer wird kein fremdes Branchenbeispiel gewählt.
- Die SP-03-spezifische Textverzweigung vollständig entfernt. Alle Muster nutzen denselben katalog- und promptgesteuerten Pfad mit `deterministic_components`, `human_decisions`, `pilot`, `metrics` und `stop_conditions` als interner Bauanleitung.
- Die Feldtabelle durch eine gekennzeichnete Vorher/Nachher-Veranschaulichung ersetzt: realistische Eingangsnachricht, daraus abgeleiteter Eintrag, bewusst fehlende Angaben und vorbereitete Rückfrage. Zahlen in ausgefüllten Feldern müssen aus der Beispielnachricht stammen; Katalogwerte bleiben nur protokollierter Rückfall.
- Den bestätigten Ist-Ablauf offen und auf fünf Schritte direkt unter den Engpass verschoben. Ergebnis, Bericht und Kontakt folgen der neuen Leserichtung; sekundäre Vorschläge werden nicht mehr auf der Hauptseite gezeigt.
- Keyword-Klassifikation aus dem Produktivpfad entfernt. API-, Rangfolge- und kritische Textfehler führen zur sichtbaren Fehlerseite mit erhaltenen Angaben; Verarbeitung zeigt nach 20 Sekunden einen Verzögerungshinweis und nach 60 Sekunden einen Abbrechen-Link.
- Rückfragebegründungen an das tatsächlich gewählte Fragepattern gebunden, Freigabefragen für Solo-Fälle gesperrt und die unabhängigen Stichwortlisten entfernt.
- Sprachschutz um technische Begriffe und unbelegte Nutzenbehauptungen erweitert. Fertige Wörter werden nicht mehr einzeln ersetzt; betroffene generierte Felder werden einmal vollständig neu formuliert und danach ausgelassen beziehungsweise bei kritischen Feldern nicht ausgeliefert.
- Browserprüfung bei 1440 × 900 und 390 × 844 ohne horizontalen Überlauf abgeschlossen. Der geprüfte Blumenladenbericht umfasst zwei A4-Seiten; die automatisierte PDF-Ausgabe ohne Browser-Kopfzeilen enthält keine lokale URL. Die Oberfläche weist ehrlich auf die notwendige Druckdialog-Option hin.
- Vier neue, von allen Indizes ausgeschlossene reale Auswahlfälle ergänzt. Vollständige Suite: `214 passed`; Keyword-Vergleich Legacy 91: PF Top-1 28 %, SP Top-1 25 %, PF-01 48 %; neue vier Qualitätsfälle: PF Top-1 50 %, SP Top-1 75 %, PF-01 0 %.
- Live-Modellprüfung: langer Blumenladenfall SP-01, Hausmeister SP-03, Fotograf SP-02 und Coach SP-01. Der kurze Blumenladen-Demolauf und A0 blieben in der Wiederholung wegen Modellvalidierung beziehungsweise API-Timeout nicht auslieferbar; eine vollständige 125-Fälle-LLM-Messung war unter dem Projektlimit von fünf Requests pro Minute nicht belastbar ausführbar.

## 2026-08-07 – Kundenoberfläche und Ergebnis auf Klartext reduziert

- Landingpage, freie Erzählung, Prozesswahl, Bestätigung und Verarbeitungszustand mit kleineren Überschriften, kompakteren Abständen und den freigegebenen kurzen Kundentexten überarbeitet; den früheren Ordnungs-Slogan vollständig entfernt.
- Die Ergebnisseite auf genau sechs sichtbare Kernblöcke reduziert: Engpass, Empfehlung, künftiger Ablauf, Beispielausgabe, menschliche Kontrolle und kleinster Einstieg. Interne Rollen-, Technik- und Autonomieangaben werden nicht mehr roh gerendert.
- Einen rekursiven Kundenpayload-Filter mit Protokollierung ergänzt. Verbotene interne Begriffe werden durch vorhandenen Klartext ersetzt oder das betroffene Feld entfällt; fünf Demofälle sichern HTML und Bericht dagegen ab.
- Die freigegebenen Output-Strukturen um kundengerechte deutsche Labels und realistische Beispielwerte ergänzt. Diese Werte werden erst nach der Modellantwort eingesetzt und erscheinen ausschließlich im eindeutig gekennzeichneten Vorschaubereich.
- Den Bericht auf genau zwei kompakte A4-Seiten festgelegt. Die erste Seite zeigt Ergebnis und Vorschau, die zweite Kontrolle, Voraussetzungen, höchstens drei offene Fragen, Einstieg, Ausbau und Kontakt. Druck-URLs und Browser-Kopf-/Fußzeilen werden unterdrückt.
- Desktop- und Mobile-Darstellung in Chrome bei 1440 und 390 Pixeln für Landingpage, Interview, Prozesswahl, Bestätigung, Verarbeitung und Ergebnis geprüft; Hausmeister, Fotograf und A0 wurden sichtbar kontrolliert. Der Hausmeisterbericht umfasst genau zwei Seiten ohne localhost-URL.
- Vollständige automatisierte Suite nach Umsetzung und Dokumentationsabgleich: `188 passed`; `python -m compileall app scripts` und `git diff --check` bestanden.

## 2026-08-07 – Fünf Mentor-Demofälle live geprüft und Laufzeitblocker behoben

- Hausmeister, Fotograf, Blumenladen, Coach und einen ausdrücklichen A0-Kalenderfall mit echten Modellaufrufen bis Ergebnis und Bericht durchlaufen; wörtliche Eingaben und Befunde in `docs/MENTOR_DEMO_2026-08-07.md` dokumentiert.
- Den A0-Selector gegen eine irrtümliche semantische Familienzuordnung abgesichert und die Kundenausgabe deterministisch auf vorhandene Funktion/einfache Regel ohne KI-Empfehlung gesetzt.
- Die semantische PF-02-Abgrenzung für kanalübergreifende neue Anfragen geschärft; der wiederholte Blumenladenlauf wählte danach den gemeinsamen Anfrageeingang statt Dokument-zu-Datensatz.
- Direkte Nutzer- und Human-Check-Felder lokal reparierbar gemacht, Zukunftsschritte für vollständige Sätze auf 220 Zeichen erweitert und einzelne distanzierte Rollenformulierungen in Du-Sprache normalisiert.
- Haupt- und sekundäre Empfehlungstitel deterministisch aus dem Katalog gesetzt; PF-/SP-/OUT-IDs in neuen und bereits gespeicherten Kundensichten unterdrückt.
- Fünf finale Browser-Renders und PDFs geprüft: Ergebnis und Bericht jeweils HTTP 200, A0 auf zwei und vier A1-Fälle auf je drei nichtleeren Seiten, keine internen IDs oder Sitzungs-URLs.
- Solution-Retrieval gegen direkte Auswahl verglichen: in allen vier KI-Fällen dieselben zwei von drei zulässigen Workflows; kein messbarer fachlicher Mehrwert in dieser Stichprobe.
- Vollständige automatisierte Suite nach allen Live-Funden und Dokumentationsanpassungen: `176 passed`.

## 2026-08-06 – Druckbericht an den Kundenvertrag angeglichen

- Den Browserbericht auf denselben fachlichen Inhalt wie die Ergebnisansicht umgestellt: Engpass, Empfehlung, Zukunftsablauf, vier Rollen, Beispielausgabe, Human Check, kleinste Version, Voraussetzungen, Nicht-Automationen, offene Angaben, Fehlergrenzen und spätere Ausbaustufe.
- Die erste Seite als Diagnose und mögliche Umsetzung statt fertiger Implementierung gekennzeichnet; A0 erhält einen eigenen, nicht als KI-Lösung formulierten Einstieg.
- Drucktypografie, A4-Ränder und Seitenumbrüche verdichtet; interne IDs, URLs und unbelegte Beispielkunden bleiben ausgeschlossen.
- Einen normalen Altanalysefall tatsächlich als PDF gerendert und visuell auf genau zwei vollständigen Seiten geprüft. Ein absichtlich langer Prüffall lief über sechs nichtleere Seiten ohne abgeschnittene Karten oder überlagerte Inhalte.
- Vollständige automatisierte Suite nach der Berichtsanpassung: `169 passed`.

## 2026-08-06 – Ergebnisansicht lesbarer gegliedert

- Die Kundenseite in eine feste Reihenfolge aus Engpass, Empfehlung, Zukunftsablauf, konkretem Ergebnis, menschlicher Prüfung, kleinstem Einstieg, Voraussetzungen und Grenzen sowie späterem Ausbau gebracht.
- H1 auf 34–40 Pixel am Desktop und 28–32 Pixel auf schmalen Viewports begrenzt, Textbreite auf etwa 72 Zeichen reduziert und Kartenhierarchie zugunsten ruhiger, scanbarer Abschnitte zurückgenommen.
- Rollen, Zielworkflow und Ergebnisvorschau responsiv und ohne interne IDs dargestellt; fehlende v3-Felder älterer Analysen bleiben als ehrlich gekennzeichnete Altanalyse-Lücken sichtbar.
- Im echten Browser bei Desktop- und Mobile-Breite geprüft: kein horizontaler Überlauf, lange Texte brechen um, relevante Aktionen sind 48–55 Pixel hoch.

## 2026-08-06 – Konkreten Kundenoutput und Grounding verbessert

- `recommendation-v3` um normale Software-/Regelaufgabe, offene Angaben, kleinste nutzbare Version, Nicht-Automationen und Autonomiestufe erweitert und ohne Migration im bestehenden JSONB gespeichert.
- OUT-Feldnamen, Human Review, Kataloggrenzen, A0–A2, kleinste Version und regelbasierte Komponenten nach der Modellantwort deterministisch angewendet; unbelegte Vorschauwerte bleiben offen oder werden als Beispiel markiert.
- Finalen Prompt auf 15 Kernregeln gekürzt; `gpt-5-mini` für den finalen Output auf `medium`, maximal zwei Versuche und 120 Sekunden Gesamtbudget gestellt.
- Breite Lösungswortliste entfernt und Ist-Fakt-, interne Referenz-, Meta- und Kundensprachfilter feldbezogen gemacht. Ein einzelnes unsicheres Feld verwirft nicht mehr die vollständige Analyse.
- 15 alte und zwei neue lokale `core_output`-Payloads nachgewiesen; Legacy-Shim beibehalten, Platzhalter protokolliert und aus der Kundensicht entfernt, ohne neue v3-Felder zu erfinden.
- Kontrollierter Live-Hausmeisteraufruf bestand beim ersten Versuch in 60,141 Sekunden. Vollständige automatisierte Suite: `157 passed`.

## 2026-08-06 – Begründete Gate-Kaskade und A0 integriert

- `GATE-01` bis `GATE-06` werden nach der Klassifikation deterministisch als `pass`, `fail` oder `unknown` mit Begründung ausgewertet.
- A0 ist erreichbar, wenn keine KI nötig ist, der Fall außerhalb der digitalen Zielgruppe liegt oder kritische autonome Entscheidungen beziehungsweise fehlende Prüfgrenzen die Lösung blockieren.
- SP-04 setzt nun zwingend einen echten angenommenen, gelagerten, bearbeiteten oder abgeholten Gegenstand voraus; Gebäude, Einsatzorte und Kundenadressen reichen nicht. Der digitale Hausmeisterfall bleibt SP-03.
- `scripts/evaluate.py` misst 91 Legacy-Fälle und 30 Batch-09-Fälle getrennt und mittelt sie nicht. `confirmed: false` und `research_proposed` bleiben erhalten.
- Vierzehn neue Gate-/A0-/Zielgruppen- und Datensatztrennungstests ergänzen die Regression; vollständige Suite `149 passed`.

## 2026-08-06 – Batch-09-Knowledge-Rollen integriert

- Kontrollierte Runtime-Kopien für 27 Inference Patterns, 28 Solution Workflows und 10 Output-Strukturen reproduzierbar aus dem unveränderten Kandidaten-Batch erzeugt und mit Pydantic validiert.
- 30 Batch-09-Evaluationen ausschließlich unter `knowledge/evaluation/` abgelegt und ihren Indexausschluss getestet.
- Beispielwerte aus dem Runtime-Kontext entfernt, den SP-04-Workflow als dokumentarischen Ausschluss belassen und seine physischen Pflichtfelder auf menschliche Bestätigung verschärft.
- Einen getrennten Solution-Workflow-Index mit 27 positiven Workflows gebaut; harte Filterung nur nach ausgewähltem Solution Pattern, kleine Soft-Boosts für sichere Metadaten und deterministischer Fallback bei fehlendem Index.
- Den unkalibrierten Source-Strength-Abzug von 0,15/0,08 neutralisiert und als reine Transparenzmetadaten beibehalten.
- Batch-09-Inference-Patterns in den Interviewkontext eingebunden, ohne Hypothesen zu Nutzerfakten zu machen oder Fragebudgets zu erweitern.
- Vollständige Suite mit 135 Tests bestanden; der separate 27-Chunk-Solution-Index wurde gebaut und validiert.

## 2026-08-06 – Batch 09 fachlich geprüft

- Die vollständige Kandidatenlieferung formal auf 27 Inference Patterns, 28 Workflows, 10 Output-Strukturen, 30 Evaluationen, 20 Quellen, eindeutige IDs, gültige PF-/SP-Referenzen und vollständige `source_refs` geprüft.
- Neun Inference Patterns, zehn Workflows, alle zehn Output-Strukturen und zwölf Evaluationen fachlich näher gelesen.
- Rollen-Normalisierung, dokumentarischen SP-04-Ausschluss, strengere menschliche Bestätigung der physischen Zuordnung und ein fragliches Evaluationslabel als Bedingungen vor Runtime-Übernahme dokumentiert.
- Keine Kandidatendatei still verändert und noch keine Batch-09-Datei in einen Runtime-Loader oder Index aufgenommen.

## 2026-08-06 – Klickbaren Ergebnisprototyp als Idee festgehalten

- Das unveränderte Ideenpapier unter `docs/future-features/clickable-result-prototype.md` abgelegt und im Dokumentationsregister als nicht geplant und nicht umgesetzt verlinkt.
- Nur einen späteren Backlog-Hinweis ergänzt; keine Route, kein Template, kein JavaScript und keine Runtime-, Prompt-, Schema-, Datenbank- oder RAG-Änderung vorgenommen.

## 2026-08-06 – Knowledge für den Zielgruppenübergang geordnet

- Direkt geladene Dateien unter `knowledge/runtime/`, noch nicht integrierte Fachkandidaten unter `knowledge/candidates/`, 91 Test- und Demo-Fälle unter `knowledge/evaluation/` und Herkunftsartefakte unter `knowledge/archive/` getrennt.
- Katalog-, Fragepattern-, Demo-, Evaluation-, Merge- und bisherige RAG-Quellenpfade angepasst; Evaluationen bleiben durch Allow-Lists und Indexmarker ausgeschlossen.
- Produktive FAISS-Artefakte weder verschoben noch neu gebaut. Der bestehende Diagnoseindex bleibt lauffähig, basiert aber weiterhin auf dem bisherigen archivierten Korpus; die bestehenden Loader lesen diese Quellen für Übergangskompatibilität noch.
- Den Batch-09-Research-Auftrag nur als nicht integrierten Kandidaten eingeordnet. Keine Batch-09-Ergebnisse, Gate-Kaskade oder neue RAG-Logik integriert.
- 121 Tests, `python -m compileall app scripts`, App-Import, Pfad-/Katalog-/Pattern-/Indexprüfung und der kostenlose 91-Fälle-Keyword-Eval bestanden; Baseline unverändert bei 28 % PF Top-1, 30 % SP Top-1 und 48 % PF-01-Default.

## 2026-08-06 – Recommendation-Reviews versioniert

- Code-Review, RAG-Audit, Research-Integrationsplan, Zweitmeinungs-Briefing und Wettbewerbsanalyse als zeitgebundene Review-Dokumente aufgenommen.
- Jedes Dokument ist gegenüber den aktuellen Sources of Truth abgegrenzt; der RAG-Audit-Nachtrag markiert die inzwischen behobenen Phase-1-Befunde und die weiterhin offenen Gate-/A0-Punkte.
- Die fünf Dokumente sind im Dokumentationsregister eingetragen.

## 2026-08-06 – Semantische Problemklassifikation integriert

- `app/llm_classification.py` klassifiziert die bestätigte Erzählung per Structured Output in ein bis drei gültige Problemfamilien und die bestehenden sechs typisierten Gates; Katalogdefinitionen dienen als Kontext.
- `app/routes.py` verwendet diesen Klassifikator vor dem unveränderten deterministischen Selector. Bei `AIServiceError` greifen ausschließlich die bestehenden Keyword-Funktionen und die alte Gate-Inferenz als Fallback.
- Selector, Sicherheitsgrenzen, Agent-Layer, UI, Regex-Filter und produktive Indizes bleiben unverändert.
- Zehn Klassifikator- und drei parametrisierte Demo-Tests verwenden ausschließlich Mocks und bestanden.
- Der bereits vorhandene, nicht erneut kostenpflichtig ausgeführte LLM-Eval-Stand umfasst 91 Fälle: PF Top-1 65 %, PF Top-3 85 %, SP Top-1 70 % und PF-01-Default 3 %. Das Artefakt enthält zwei Klassifikatorfehler und einen Treffer eines verbotenen Begriffs; die zugrunde liegenden Labels bleiben unbestätigte Vorschläge.

## 2026-08-06 – Recommendation-Evaluation reproduzierbar gemacht

- `scripts/evaluate.py` führt die 91 getrennten Evaluationsfälle standardmäßig ohne LLM-Kosten durch `classify_problem_families` → `infer_decision_gates` → `select_recommendation` und misst Default-Quote, Gate-Streuung, verbotene Inhalte und Trefferquoten.
- Die gespeicherte Keyword-Baseline ergibt PF Top-1 28 Prozent, PF Top-3 38 Prozent, SP Top-1 30 Prozent, PF-01-Default 48 Prozent und null Treffer verbotener Inhalte.
- `knowledge/evaluation/expected_labels.json` enthält 91 Einträge. Alle stehen auf `confirmed: false`; die 40 vorbelegten Zuordnungen sind ausschließlich Vorschläge aus der Review und keine bestätigte Ground Truth.
- Evaluationsdateien bleiben vollständig außerhalb der produktiven Wissensindizes.

## 2026-08-06 – Katalog v2 und Research-Grundlage aufgenommen

- Research Batches 05 bis 08 und die zugehörige Forschungsgrundlage unter `knowledge/` abgelegt. Keine Datei wurde in einen Vektorindex aufgenommen; `DIAGNOSTIC_JSONL_FILES` und `AGENT_PATTERN_FILES` bleiben unverändert.
- Batch 08 bleibt unveränderte, zeitkritische Tool- und Architektur-Researchgrundlage und ist weder in den Laufzeitkatalog noch in einen produktiven Index integriert.
- `knowledge/structured/recommendation_catalog.json` auf `2026-08-06-v2` gehoben: neue Blöcke `genai_capabilities` (GAI-01…09), `decision_gates` (GATE-01…06), `failure_patterns` (FAIL-01…12), `autonomy_levels` (A0…A5) und `non_genai_mechanisms`; je Solution Pattern zehn neue Felder aus Batch 06; je Problemfamilie `genai_role`, `non_genai_requirement` und `human_boundary`.
- Vier durch Batch 06 verengte Zuordnungen übernommen: `SP-01` ohne `PF-11`/`PF-12`, `SP-04` und `SP-07` ohne `PF-04`. Sieben bereits vorher abweichende `supplementary`-Einträge wurden nur gemeldet, nicht geändert.
- `app/recommendation_service.py` um die entsprechenden Modelle und Referenzprüfungen erweitert, inklusive Autonomiegrenze je Solution Pattern gegen die Obergrenze seiner GenAI-Fähigkeiten.
- Der Laufzeitpfad nutzt die neuen Felder noch nicht; `select_recommendation` ist unverändert. Die LLM-gestützte Gate-Kaskade ist bewusst ein getrennter nächster Schritt.
- `scripts/merge_catalog_v2.py` als nachvollziehbarer, wiederholbarer Merge abgelegt (`--dry-run` zeigt den Diff).
- Reproduzierbarer Dry-Run, Katalog-Ladeprüfung, Python-Kompilierung und 21 Katalog-/Referenzfalltests erfolgreich ausgeführt.

## 2026-08-06 – Recommendation Experience integriert und geprüft

- Integrations-Commit `4ed51ab` auf `origin/feature/recommendation-experience` veröffentlicht.
- Neuen `FinalAnalysisResult`-Vertrag mit einer Hauptlösung, Promise, Heute/Mit KI, typisierter Ergebnisvorschau, Du/KI/Ergebnis/Human-Check, begrenzten Nutzen- und Voraussetzungenlisten, Umsetzungsweg, optionalem Ausbau und null bis zwei sekundären Möglichkeiten integriert.
- Wochentest und Pflicht zu genau drei Opportunities aus neuen Analysen und sichtbaren Seiten entfernt; alte JSONB-Analysen bleiben über die Legacy-Abbildung lesbar.
- Problemfamilien, sechs getrennte Gates und deterministischen Solution-Selector in den produktiven Analysepfad eingebunden; Auswahl, Ausschlüsse, Gates und Validierung werden datensparsam strukturiert geloggt.
- Analyse-Retrieval reserviert nun Diagnose-, Automations-, Voraussetzungs- und Guardrail-Muster, sodass ein konkretes Lösungsmuster nicht zufällig vollständig fehlt.
- Agent-Pattern-Index mit kontrollierten Typen, drei Treffern und sicherem Fallback im Interviewpfad aktiviert. Budgets, No-Repeat, Schleifenstopp, Faktenintegrität und Freigabegrenzen bleiben deterministisch.
- Echtes OpenAI Function Calling bewusst nicht integriert; ein sicherer Tool-Calling-Loop bleibt ein getrennt zu evaluierender Schritt.
- Ergebnisoberfläche auf eine dominante Hauptlösung, Vorher/Nachher, Vier-Schritt-Ablauf, zentrale Musterkarte und progressive Details umgebaut.
- Bericht auf zwei Kernseiten reduziert; Seite 3 erscheint nur bei fachlich vorhandenen sekundären Möglichkeiten. Browserdruck und `window.print()` bleiben bestehen.
- Mermaid nicht eingeführt; die validierte HTML-/CSS-Darstellung war bei Desktop, schmalem Mobile-Viewport und Bericht stabiler.
- Referenzfälle für Hausmeister, Schuhmacher, Blumenladen und Massagesalon sowie Sprach-, Längen-, Grounding-, Retrieval- und Agent-Pattern-Prüfungen ergänzt beziehungsweise angepasst.
- `python -m compileall -q app`, App-Start mit HTTP 200 und vollständige Testsuite mit `107 passed` erfolgreich ausgeführt.
- Visuell in Chrome geprüft: Desktop, schmale Mobile-Ansicht, 48–58-Pixel-Touchziele, lange deutsche Texte, fehlender horizontaler Überlauf und zweiseitiger Bericht ohne künstliche dritte Seite.
- Superseded Root-Kompatibilitätsdatei `UX_FLOW.md` entfernt und den Dokumentationstest auf die aktive Source of Truth unter `docs/flows/UX_FLOW.md` umgestellt.

## 2026-08-06 – RAG-Index-Zuverlässigkeit abgesichert

- Diagnosewissen überspringt nach der Promptbereinigung leere Chunks einzeln; gültige Chunks bleiben ihrem ursprünglichen Datensatz zugeordnet.
- Jeder Index-Promote validiert Test und Produktion, sichert Diagnose- und Agentenindex vollständig in einem neuen Zeitstempelordner und validiert die promovierte Produktion erneut. Das historische Pre-Batch-04-Archiv bleibt unverändert.
- Diagnose- und Agentenindex werden pro Prozess und Indexverzeichnis gecacht und nach einer mtime-Änderung der FAISS- oder Metadatendatei neu geladen. Fehlende Dateien bleiben ein Konfigurationsfehler.
- Vier neue RAG-Regressionstests bestanden; `python -m compileall app scripts`, App-Import und die Keyword-Evaluation mit unveränderten 28 % PF Top-1, 30 % SP Top-1 und 48 % PF-01-Default bestanden.
- Die vollständige Suite im vorhandenen uncommittierten Klassifikations-Arbeitsstand ergab `119 passed, 2 failed`; beide Fehler betreffen Demo-Tests ohne Mock für den bereits vorgeschalteten LLM-Klassifikator und wurden in dieser Phase nicht verändert.

## 2026-08-06 – Kompakten Recommendation-Vertrag beschlossen

- Wochentest und Pflicht zu genau drei Opportunities aus dem verbindlichen Zielvertrag entfernt.
- Genau eine dominante Hauptlösung, konkrete Ergebnisvorschau, direkte Du-Ansprache, variable Voraussetzungen und null bis zwei optionale weitere Möglichkeiten festgelegt.
- Strukturierter Katalog, sechs getrennte Gates, rückwärtskompatible JSONB-View und HTML-/CSS-Prozesslinie als verbindliches Design dokumentiert.
- Blumenladen als vierten Referenzfall ergänzt; Implementierung, Integration und Tests sind mit diesem Dokumentationsschritt noch nicht behauptet.

## 2026-08-06 – Strukturiertes Solution-Wissen implementiert

- Versionierten Katalog mit exakt zwölf Problemfamilien, zehn Solution Patterns und vollständiger Problemfamilie-zu-Lösung-Matrix angelegt.
- Typisierte Pydantic-Loader, sechs getrennte Decision Gates, deterministische Klassifikation und nachvollziehbaren Selector implementiert.
- Evaluationpfade explizit vom Loader ausgeschlossen; kein neuer Index, keine Embeddings und keine Datenbankmigration eingeführt.
- Sieben Katalog- und Referenzfalltests für Hausmeister, Schuhmacher, Blumenladen und Massagesalon erfolgreich ausgeführt.
- Katalog und Selector sind mit diesem Paket implementiert und getestet, aber noch nicht in den produktiven Analysepfad integriert.

## 2026-08-06 – Private IDE-Artefakte aus der Versionskontrolle entfernt

- Sieben bereits versionierte PyCharm-Dateien unter `.idea/` aus dem Git-Index entfernt; die lokalen Dateien bleiben auf dem Entwicklungsrechner erhalten.
- Die bestehende `.gitignore`-Regel `.idea/` verhindert, dass diese Dateien erneut aufgenommen werden.
- Alle verfolgten Dateinamen und Textdateien auf typische private Artefakte und hochwahrscheinliche Secret-Signaturen geprüft; keine weiteren privaten Dateien oder Secrets bestätigt.
- `.env.example` bewusst als sichere Platzhaltervorlage beibehalten.
- Keine Produktionslogik, Prompts, Indizes, Datenbankmodelle, Tests oder Nutzeroberflächen verändert.
- Frühere `.idea`-Versionen bleiben ohne ausdrücklich untersagten History-Rewrite in der Git-Historie; der Restpunkt ist in `docs/KNOWN_ISSUES.md` dokumentiert.

## 2026-08-05 – Recommendation-Fachgrundlage und Feature-Spec aufgenommen

- Vollständige Fachgrundlage mit zwölf Problemfamilien, zehn Solution Patterns, Reifegrad-/Gate-Modell und drei Referenzfallanalysen unter `docs/product/` aufgenommen.
- Strukturierte Recommendation-Feature-Spec mit Requirements, Design, Aufgaben und Acceptance Criteria angelegt.
- Projektstand, Known Issues, Roadmap, Entscheidungen, Architektur und Dokumentenregister an den dokumentierten fachlichen Stand angepasst.
- Fachliche Analyse ausdrücklich von implementierter und integrierter Laufzeitlogik getrennt.
- Keine Produktionslogik, Prompts, RAG-Indizes, Embeddings, Datenbankmodelle, Tests oder Nutzeroberflächen verändert.

## 2026-08-05 – Projektdokumentation konsolidiert

- Interne Projekt- und Entwicklungsdokumente unter `docs/` organisiert und in `docs/INDEX.md` mit Status und Source of Truth registriert.
- Projektstand, UX- und Processing-Flows sowie Product-Output-Anforderungen an ihre verbindlichen Zielpfade verschoben.
- UI-Redesign-Notizen und die frühere TODO-Liste nach Inhaltsprüfung und Zuordnung offener Punkte archiviert.
- Dokumentationspflege in `AGENTS.md`, `docs/DOCUMENTATION_GUIDE.md` und `.agents/skills/documentation-update/SKILL.md` verbindlich beschrieben.
- `README.md` mit dem zentralen Dokumentationsregister verknüpft.
- Keine Produktionslogik, Prompts, RAG-Indizes, Embeddings, Datenbankmodelle, Tests oder Nutzeroberflächen verändert.

## 2026-08-05 – Grounded Analysis Output normalisiert

**Commit:** `6320ad0` (`Normalize grounded analysis output`)

- Grounding und Normalisierung der finalen Analyse und Rückfragen erweitert.
- Embedding-Aufrufe getrennt von Structured-Output-Aufrufen gezählt.
- Eigener Timeout für die finale Analyse eingeführt.
- Zugehörige Produktfinalisierungs- und Qualitätsprüfungen ergänzt beziehungsweise angepasst.

## 2026-07-27 – Finale Analysevalidierung und Laufzeitverhalten verbessert

**Commit:** `8f369f4` (`Fix final analysis validation and latency`)

- Finale Analysevalidierung und Fehlerbehandlung erweitert.
- Analysefluss, Status- und Latenzverhalten überarbeitet.
- Zugehörige Analyse- und Produktfinalisierungstests ergänzt.

## 2026-07-27 – Kundenorientierte Diagnosejourney finalisiert

**Commit:** `73bf7fb` (`Finalize customer-first diagnostic journey`)

- Sichtbare Journey, Processing, Ergebnis- und Berichtsdarstellung überarbeitet.
- Agentenheuristiken, Structured-Output-Schema und Ergebnisaufbereitung erweitert.
- Produkt-, UX- und Processing-Spezifikationen sowie automatisierte Tests aktualisiert.

## 2026-07-26 – Diagnose- und Agentenarchitektur implementiert und dokumentiert

**Commits:** `6267589` (`Complete diagnostic demo architecture`), `b6c7a87` (`Document diagnostic architecture`)

- Begrenzten Diagnostic Interview Agent mit internem State, Regeln und drei Python-Werkzeugen implementiert.
- Diagnose- und Agent-Pattern-Indizes technisch getrennt.
- Indexbau, Vergleich, Validierung und Promotion ergänzt.
- RAG-, Agenten-, Journey- und Qualitätsprüfungen erweitert.
- Bestehende Diagnosearchitektur, RAG-Inventar, Merge-Plan und Evaluationsergebnisse dokumentiert.

## 2026-07-26 – Research-Batches ergänzt

**Commit:** `4ae2b21` (`Add diagnostic research batches`)

- Batch 02 für analoge Realität, Batch 03 für diagnostische Tiefe und Batch 04 für agentische Interviewmuster hinzugefügt.
- Korpora, Quellenregister, Patternkataloge, Guardrails, Evaluationen und Quality Gates getrennt abgelegt.
