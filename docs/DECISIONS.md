# Entscheidungen

**Last Updated:** 2026-08-06

Diese Datei hält bestätigte Produkt-, Fach- und Architekturentscheidungen fest. Wenn das ursprüngliche Entscheidungsdatum nicht getrennt dokumentiert wurde, ist das Datum als Aufnahmedatum gekennzeichnet.

## DEC-001 – Diagnose vor Empfehlung

- **Datum:** 2026-07-26
- **Entscheidung:** AI Start Map diagnostiziert zuerst den konkreten Ist-Prozess und empfiehlt erst danach einen nächsten Schritt.
- **Grund:** Ohne bestätigten Ablauf, Engpass und Reifegrad wären Empfehlungen generisch oder könnten fremde Annahmen übernehmen.
- **Konsequenzen:** Prozessgrenzen, Ist-Schritte, Unsicherheiten und menschliche Entscheidungen werden vor dem Recommendation Layer erfasst beziehungsweise validiert.
- **Alternativen:** Direkte Ideengenerierung oder allgemeiner KI-Chat wurden nicht gewählt.
- **Status:** Implemented

## DEC-002 – Diagnosewissen und Agentenwissen bleiben getrennt

- **Datum:** 2026-07-26
- **Entscheidung:** Es gibt einen produktiven Diagnoseindex und einen separaten optionalen Agent-Pattern-Index.
- **Grund:** Fachliches Vergleichswissen und Agentenentscheidungsmuster haben unterschiedliche Aufgaben und dürfen nicht unkontrolliert vermischt werden.
- **Konsequenzen:** Getrennte Korpora, Verzeichnisse, Manifeste, Testindizes und Validierungen.
- **Alternativen:** Ein gemeinsamer Vektorindex wurde verworfen.
- **Status:** Implemented and integrated; Agent-Pattern-Retrieval unterstützt den Interviewpfad kontrolliert

## DEC-003 – Evaluationen sind niemals Produktwissen

- **Datum:** 2026-07-26
- **Entscheidung:** Evaluationsdateien dürfen nicht indexiert oder als RAG-Wissen an Produktprompts übergeben werden.
- **Grund:** Sonst könnten erwartete Antworten, Testmarker oder verbotene Empfehlungen in Kundenausgaben leaken und die Evaluation verfälschen.
- **Konsequenzen:** Separate Evaluationsverzeichnisse, `NEVER_INDEX`-Marker, Pfadprüfungen und automatisierte Tests.
- **Alternativen:** Evaluationen im gemeinsamen Korpus mit Metadatenfilter wurden nicht akzeptiert.
- **Status:** Implemented

## DEC-004 – Nutzerfakten, Ableitungen und RAG-Evidenz bleiben getrennt

- **Datum:** 2026-07-26
- **Entscheidung:** Nur Nutzerangaben und bestätigte Extraktionen gelten als Fakten über den aktuellen Betrieb. RAG-Inhalte bleiben internes Vergleichswissen.
- **Grund:** Fremde Fälle dürfen nicht als Eigenschaften des aktuellen Nutzers erscheinen.
- **Konsequenzen:** Getrennte Pydantic-State-Felder, Promptbereiche A–D, Grounding-Prüfungen und Filter für interne Referenzen.
- **Alternativen:** Ein gemeinsamer untypisierter Kontextblock wurde nicht gewählt.
- **Status:** Implemented

## DEC-005 – Sicherheits- und Budgetregeln bleiben deterministisch

- **Datum:** 2026-07-26
- **Entscheidung:** Rückfragebudgets, No-Repeat, Schleifenstopp, Faktenintegrität und das Verbot autonomer Ausführung werden in Python erzwungen und hängen nicht allein von Retrieval oder LLM-Selbsteinschätzung ab.
- **Grund:** Sicherheitsgrenzen und kontrollierbares Verhalten müssen reproduzierbar sein.
- **Konsequenzen:** `app/agent_config.py` und `evaluate_readiness_and_next_action()` steuern die aktuelle Agentenaktion überwiegend deterministisch.
- **Alternativen:** Ein vollständig autonom entscheidender LLM-Agent wurde für den aktuellen Stand nicht gewählt.
- **Status:** Implemented

## DEC-006 – Begrenzte, schrittweise Nutzerreise

- **Datum:** 2026-07-27
- **Entscheidung:** Die Oberfläche zeigt einen klaren Schritt nach dem anderen, bevorzugt null bis zwei Rückfragen und begrenzt die sichtbare Zahl technisch auf vier.
- **Grund:** Kleine Betriebe sollen schnell zu einem verständlichen, handlungsfähigen Ergebnis kommen.
- **Konsequenzen:** Einzelne Rückfrageseiten, sichtbarer Processing-Zustand und ein kompakter Recommendation-Vertrag mit einer Hauptlösung.
- **Alternativen:** Langer Fragebogen und mehrere gleichzeitig sichtbare Detailformulare wurden nicht gewählt.
- **Status:** Implemented; Heuristiken müssen mit echten Interviews kalibriert werden

## DEC-007 – Bestehende fünf Tabellen und JSONB weiterverwenden

- **Datum:** 2026-07-26
- **Entscheidung:** Der aktuelle Agentenstate und variable Ergebnisdetails werden aus den bestehenden fünf Tabellen rekonstruiert beziehungsweise in bestehenden JSONB-Feldern gespeichert.
- **Grund:** Der aktuelle Flow benötigt keine zusätzlichen eigenständig verwalteten Entitäten.
- **Konsequenzen:** Keine zusätzliche Migration für Agentenstate oder Kernoutput; `analyses.uncertainties` enthält `core_output`, `automation_opportunities.blueprint_json` die Präsentations- und Blueprintdetails.
- **Alternativen:** Neue Agent-State-, Trace- oder Recommendation-Tabellen wurden für den aktuellen Stand nicht eingeführt.
- **Status:** Implemented

## DEC-008 – Browserbasierte Spracheingabe mit Textfallback

- **Datum:** 2026-07-27
- **Entscheidung:** Die erste Voice-Version nutzt `SpeechRecognition`/`webkitSpeechRecognition`; editierbare Texteingabe bleibt immer verfügbar.
- **Grund:** Sprache soll eine optionale Verbesserung sein und darf den Flow in nicht unterstützten Browsern nicht blockieren.
- **Konsequenzen:** Keine serverseitige Audioaufnahme oder Transkriptionspipeline im aktuellen Produkt.
- **Alternativen:** `MediaRecorder` plus serverseitige Transkription ist nicht umgesetzt.
- **Status:** Implemented

## DEC-009 – PDF über Druckansicht und Kontakt über `mailto:`

- **Datum:** 2026-07-27
- **Entscheidung:** Der Bericht wird als zweiseitige Kernausgabe mit optionaler dritter Seite und `window.print()` bereitgestellt; Kontakt erfolgt über einen normalen `mailto:`-Link.
- **Grund:** Kleine, wartbare Implementierung ohne schwere PDF-Abhängigkeit oder falsche Browserzusagen.
- **Konsequenzen:** Nutzer speichern die PDF selbst und hängen sie selbst an die E-Mail an.
- **Alternativen:** Serverseitige PDF-Erzeugung und automatischer E-Mail-Versand wurden nicht gewählt.
- **Status:** Implemented

## DEC-010 – Vierstufige fachliche Richtung

- **Datum:** 2026-08-05 (Aufnahmedatum)
- **Entscheidung:** Das Reifegradmodell unterscheidet Ordnung, Digitalisierung, KI-Unterstützung und Automatisierung. Nicht jeder Betrieb muss bei Ordnung beginnen.
- **Grund:** Der nächste Schritt muss zur tatsächlichen digitalen Reife passen und darf KI nicht unnötig auf später verschieben.
- **Konsequenzen:** Pain-Point-Taxonomie, Problemursache und Reifegrad sollen künftig die Solution-Auswahl explizit steuern.
- **Alternativen:** Eine lineare Regel, nach der jeder Betrieb zwingend bei Ordnung beginnt, wurde abgelehnt.
- **Status:** Implemented, integrated and tested

## DEC-011 – Leitregel für die Recommendation-Auswahl

- **Datum:** 2026-08-05 (Aufnahmedatum)
- **Entscheidung:** **„So wenig Ordnung wie zwingend nötig, so früh konkrete KI-Unterstützung wie realistisch möglich, Automatisierung erst nach bestätigten Daten und klaren Freigaben.“** Die Kurzform „Ordnung vor Automatisierung, aber nicht Ordnung statt KI“ bleibt erläuternd gültig.
- **Grund:** Fehlende Grundlagen müssen ehrlich benannt werden; vorhandene digitale Voraussetzungen sollen gleichzeitig zu konkreter KI-Unterstützung führen können.
- **Konsequenzen:** Die derzeitige Überbetonung manueller Ordnung wird als Known Issue behandelt und anhand gezielter Evaluationen korrigiert.
- **Alternativen:** „Immer zuerst Ordnung“ und „immer sofort KI“ wurden beide abgelehnt.
- **Status:** Implemented in Selector, Outputvertrag und Kundendarstellung; Kalibrierung mit realen Interviews bleibt offen

## DEC-012 – Solution Patterns erst fachlich prüfen, dann technisch integrieren

- **Datum:** 2026-08-05 (Aufnahmedatum)
- **Entscheidung:** Zuerst entsteht ein kleiner, hochwertiger und fachlich geprüfter Solution-Pattern-Katalog. Erst danach wird er technisch durch Codex integriert.
- **Grund:** Ungeprüfte Lösungsmuster würden die Recommendation-Qualität nicht verlässlich verbessern und könnten neue Fehlentscheidungen erzeugen.
- **Konsequenzen:** Der fachlich geprüfte Katalog liegt versioniert unter `knowledge/structured/`; ein zusätzlicher Solution-Index bleibt ausgeschlossen.
- **Alternativen:** Sofortige automatische Generierung und Indexierung vieler Solution Patterns wurde nicht gewählt.
- **Status:** Implemented and tested

## DEC-013 – Diagnose-RAG und Solution-Katalog werden getrennt

- **Datum:** 2026-08-05
- **Entscheidung:** Diagnose-RAG liefert Problem- und Bedingungsevidenz. Die Solution-Auswahl verwendet zunächst einen separaten strukturierten Katalog und deterministische Gates. Im ersten Schritt wird kein neuer FAISS-Solution-Index eingeführt.
- **Grund:** Zehn strukturierte Patterns lassen sich nachvollziehbarer filtern und testen als über einen weiteren semantischen Top-k; ein zusätzlicher Index löst die belegte Konkurrenz defensiver Treffer nicht automatisch.
- **Konsequenzen:** Der Diagnoseindex bleibt unverändert. Der JSON-Katalog wird direkt geladen und seine Auswahl getrennt als Recommendation-Kontext an die finale Analyse übergeben.
- **Alternativen:** Neuer Solution-FAISS-Index oder unmittelbare Auswahl allein aus Diagnose-Top-k wurden für den ersten Schritt nicht gewählt.
- **Status:** Implemented, integrated and tested

## DEC-014 – Solution-Auswahl nutzt getrennte Gates

- **Datum:** 2026-08-05
- **Entscheidung:** Vorgangsanker, Kanaleignung, Prozess-/Datenreife, Risiko, Regelstabilität und menschliche Freigabe werden getrennt bewertet. Kanaleignung, Prozess-/Datenreife und Automationsreife dürfen nicht zu einer einzigen konservativen Reifestufe zusammenfallen.
- **Grund:** Ein ungeeigneter Kanal ist nicht automatisch ein unreifer Gesamtprozess; passende KI-Unterstützung darf durch defensive Voraussetzungen nicht unbegründet verdrängt werden.
- **Konsequenzen:** Applicability, Exclusion, Voraussetzungen und Human-Approval-Grenzen werden vor der finalen Kundenausgabe deterministisch ausgewertet und strukturiert geloggt.
- **Alternativen:** Ein einziges lineares Reifegrad-Gate wurde verworfen.
- **Status:** Implemented, integrated and tested

## DEC-015 – Genau drei Opportunities werden erneut geprüft

- **Datum:** 2026-08-05
- **Entscheidung:** Der bestehende Vertrag mit genau drei Opportunities bleibt vorläufig implementierter Ist-Stand, wird aber fachlich erneut geprüft und durch diese Entscheidung nicht automatisch aufgehoben.
- **Grund:** Die feste Anzahl kann schwächere Empfehlungen erzwingen; eine Änderung berührt jedoch Schema, Persistenz, Templates und Tests und benötigt eine eigene Freigabe.
- **Konsequenzen:** Product-Output- und UX-Flow-Dokumente bleiben `Needs Review`. Keine Laufzeitänderung in diesem Dokumentationsauftrag.
- **Alternativen:** Sofortige Abschaffung oder unveränderte dauerhafte Bestätigung wurden noch nicht beschlossen.
- **Status:** Superseded durch DEC-016

## DEC-016 – Eine Hauptlösung statt Wochentest und Pflicht-Chancen

- **Datum:** 2026-08-06
- **Entscheidung:** Genau eine dominante Hauptlösung; kein Wochentest; null bis zwei optionale sekundäre Möglichkeiten; ein Umsetzungsweg ersetzt die Hausaufgabe.
- **Grund:** Kunden sollen Veränderung, Ergebnis, KI-Aufgabe und eigene Kontrolle sofort verstehen.
- **Konsequenzen:** Neuer Structured Output, variable Opportunity-Anzahl, kompakte Hauptseite, optionale dritte Druckseite und rückwärtskompatible View alter Analysen.
- **Status:** Implemented, integrated, tested and documented

## DEC-017 – Katalog und deterministische Gates wählen die Lösung

- **Datum:** 2026-08-06
- **Entscheidung:** Zwölf Problemfamilien und zehn Solution Patterns werden direkt aus validierten Dateien geladen; sechs getrennte Gates filtern und priorisieren. Diagnose-RAG entscheidet nicht allein.
- **Grund:** Semantisches Top-k kann konkrete Lösungen verdrängen und vermischt heute Reifedimensionen.
- **Konsequenzen:** Kein Solution-FAISS-Index, keine Embeddings, keine Migration.
- **Status:** Implemented, integrated, tested and documented

## DEC-018 – HTML/CSS-Prozesslinie bleibt verbindlich

- **Datum:** 2026-08-06
- **Entscheidung:** Mermaid wird nicht wieder eingeführt; validierte Schritte bleiben als vertikale HTML-/CSS-Linie sichtbar.
- **Grund:** Zuverlässige deutsche Umbrüche, Mobile, Druck und Sicherheit.
- **Status:** Implemented, visually checked and documented
