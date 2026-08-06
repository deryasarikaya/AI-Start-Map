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
- **Konsequenzen:** Der fachlich geprüfte Katalog liegt versioniert unter `knowledge/runtime/`; ein späterer Variantenindex darf seine Entscheidungshoheit nicht ersetzen.
- **Alternativen:** Sofortige automatische Generierung und Indexierung vieler Solution Patterns wurde nicht gewählt.
- **Status:** Implemented and tested

## DEC-013 – Diagnose-RAG und Solution-Katalog werden getrennt

- **Datum:** 2026-08-05
- **Entscheidung:** Diagnose-RAG liefert Problem- und Bedingungsevidenz. Die Solution-Auswahl verwendet zunächst einen separaten strukturierten Katalog und deterministische Gates. Im ersten Schritt wird kein neuer FAISS-Solution-Index eingeführt.
- **Grund:** Zehn strukturierte Patterns lassen sich nachvollziehbarer filtern und testen als über einen weiteren semantischen Top-k; ein zusätzlicher Index löst die belegte Konkurrenz defensiver Treffer nicht automatisch.
- **Konsequenzen:** Der Diagnoseindex bleibt unverändert. Der JSON-Katalog wird direkt geladen und seine Auswahl getrennt als Recommendation-Kontext an die finale Analyse übergeben.
- **Alternativen:** Neuer Solution-FAISS-Index oder unmittelbare Auswahl allein aus Diagnose-Top-k wurden für den ersten Schritt nicht gewählt.
- **Status:** Teilweise superseded durch DEC-021; die Trennung und deterministische Entscheidungshoheit bleiben gültig

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
- **Konsequenzen:** Der Katalog und die Gates wählen weiterhin die Lösung. Ein später ergänzter Solution-Workflow-Index darf nur Varianten innerhalb des bereits gewählten Patterns ranken; keine Migration.
- **Status:** Implemented, integrated, tested and documented

## DEC-018 – HTML/CSS-Prozesslinie bleibt verbindlich

- **Datum:** 2026-08-06
- **Entscheidung:** Mermaid wird nicht wieder eingeführt; validierte Schritte bleiben als vertikale HTML-/CSS-Linie sichtbar.
- **Grund:** Zuverlässige deutsche Umbrüche, Mobile, Druck und Sicherheit.
- **Status:** Implemented, visually checked and documented

## DEC-019 – Semantische Klassifikation vor deterministischer Auswahl

- **Datum:** 2026-08-06
- **Entscheidung:** Die bestätigte Nutzererzählung wird primär per Structured Output null bis drei gültigen Problemfamilien und den typisierten Gate-Rohwerten zugeordnet. Der Katalog begrenzt die IDs; der Selector und alle Sicherheitsgrenzen bleiben deterministisch.
- **Grund:** Die gemessene Keyword-Baseline erreicht nur 28 % PF Top-1 und fällt in 48 % der Fälle auf `PF-01` zurück. Freie Erzählungen benötigen semantische Zuordnung, ohne die Entscheidungshoheit des Selectors an das Modell abzugeben.
- **Konsequenzen:** Bei `AIServiceError` bleiben Keyword-Klassifikation und Gate-Inferenz der Fallback. Die nachgelagerte fachliche GATE-01-bis-GATE-06-Kaskade und A0 sind durch DEC-022 ergänzt.
- **Alternativen:** Keyword-Matching als primärer Pfad und freie Solution-Auswahl durch das LLM wurden nicht gewählt.
- **Status:** Implemented, integrated, tested and documented

## DEC-020 – Knowledge nach technischem Status trennen

- **Datum:** 2026-08-06
- **Entscheidung:** Direkt geladene Dateien liegen unter `knowledge/runtime/`, noch nicht integrierte Fachkandidaten unter `knowledge/candidates/`, Test- und Demo-Fälle unter `knowledge/evaluation/` und Herkunftsartefakte unter `knowledge/archive/`.
- **Grund:** Dateistatus und technische Verwendung müssen erkennbar sein; Evaluationen dürfen nie als Produktwissen oder Indexquelle behandelt werden.
- **Konsequenzen:** Bestehende Loaderpfade werden angepasst. Der produktive Diagnoseindex wird nicht neu gebaut und bleibt vorübergehend auf seiner bisherigen, jetzt archivierten Quellenbasis. Archivquellen dürfen für diese Übergangskompatibilität weiter gelesen werden, ohne dadurch neue fachliche Runtime-Quellen zu werden.
- **Alternativen:** Eine gemeinsame Ablage nach Research-Batch oder die unzutreffende Behauptung, das Archiv werde technisch gar nicht verwendet, wurden verworfen.
- **Status:** Implemented and tested

## DEC-021 – Batch-09-Rollen getrennt laden und Solution-Retrieval begrenzen

- **Datum:** 2026-08-06
- **Entscheidung:** Output-Strukturen werden deterministisch geladen, Inference Patterns bleiben unbestätigtes Rückfragewissen und 27 positive Solution Workflows liegen in einem eigenen kleinen Index. Der dokumentarische SP-04-Eintrag und Evaluationen werden nicht indexiert.
- **Grund:** Die drei Datentypen besitzen unterschiedliche Vertrauens- und Laufzeitrollen. Semantische Suche kann eine Branchenvariante auswählen, darf aber weder Gates noch den Katalog-Selector ersetzen.
- **Konsequenzen:** Harte Filterung nur nach dem bereits gewählten Solution Pattern; Kanäle und Betriebstyp nur als Soft-Boost. Bei fehlendem Index greift direkte deterministische Auswahl. Der ungemessene Source-Strength-Abzug von 0,15/0,08 ist neutralisiert.
- **Status:** Implemented, integrated and tested; fachliche Kalibrierung mit echten Betrieben bleibt offen

## DEC-022 – Gate-Kaskade entscheidet vor der Darstellung über A0 bis A2

- **Datum:** 2026-08-06
- **Entscheidung:** Die Klassifikations-Rohsignale werden deterministisch in `GATE-01` bis `GATE-06` mit `pass`, `fail` oder `unknown` und nachvollziehbarer Begründung übersetzt. Der Selector liefert A0, A1 oder A2; höhere Autonomie wird für die aktuelle Empfehlung nicht gewählt. Eine leere Problemfamilienliste ist zulässig und bedeutet nicht automatisch Klassifikationsfehler.
- **Grund:** Die richtige und sichere Lösung muss vor der Modellformulierung feststehen. Unbekannte Fakten dürfen weder still als erfüllt gelten noch pauschal die ganze Diagnose verwerfen.
- **Konsequenzen:** Kein KI-Bedarf, rein analoge Ausgangslage, fehlende kritische Prüfung oder gewünschte autonome Preis-, Zahlungs- oder Personalentscheidung führen konservativ zu A0. Unbekannte Voraussetzungen begrenzen auf A1. SP-04 erfordert einen echten physischen Gegenstand; Gebäude, Einsatzorte und Adressen gelten nicht als Objektfall. Hausmeister mit Sprache, Foto und Bon wird als SP-03 behandelt.
- **Alternativen:** Ein einzelner Reifegradwert, automatisches PF-01 bei fehlendem Engpass und Auswahl hoher Autonomie wurden verworfen.
- **Status:** Implemented, integrated and tested

## DEC-023 – Feldbezogene Grounding-Filter ersetzen pauschales Verwerfen

- **Datum:** 2026-08-06
- **Entscheidung:** Ein Filterfehler verwirft nicht mehr die gesamte finale Analyse. Nicht belegte Ist-Details oder interne Referenzen werden nur im betroffenen Feld entfernt beziehungsweise als „noch offen“ neutralisiert; eine Unsicherheit wird ergänzt. Nutzerwörter sind erlaubt, Begriffe aus OUT-Vorschauen bleiben als Beispiel erlaubt und Katalogbegriffe sind im ausdrücklich zukünftigen Workflow zulässig. FAIL-01 bis FAIL-12 und die Stop Conditions der vorausgewählten Lösung werden als begründete Guardrails an den finalen Aufruf übergeben.
- **Geänderte Wortlisten:** `SPECULATIVE_PROCESS_TERMS` bleibt ausschließlich als enger Ist-Fakt-Schutz für `abholnummer`, `ausweis`, `falschübergab`, `foto`, `identitätsprüf`, `ringordner`, `unterschrift` und `verwechslung`; `fotograf` wurde entfernt. Ein Treffer wird immer zugelassen, wenn der Nutzer den Begriff selbst verwendet hat. `SOLUTION_ONLY_UNCERTAINTY_TERMS` wurde vollständig geleert, weil `auftragskarte`, `automatis*`, `digital`, `fotodokument`, `software` und `statusübersicht` berechtigte Zukunfts-, Voraussetzungen- oder Unsicherheitsbegriffe sein können. `CUSTOMER_LANGUAGE_REPLACEMENTS` bleibt für nicht vom Nutzer verwendete Fachwörter aktiv; Nutzerwörter werden nicht ersetzt. Die Schema-Sperre wurde auf die vier nachweislich künstlichen Wörter `formulardoppie`, `nachschlageort`, `übergabevermerkgabel` und `handschriftenkapazität` reduziert. Distanzierte Rollen werden vor Validierung in Du-Sprache normalisiert.
- **Regex-Änderungen:** `SUMMARY_META_PATTERN` und `AS_IS_META_PATTERN` neutralisieren oder entfernen nur betroffene Felder. `INTERNAL_REFERENCE_PATTERN`, interne IDs und interne Dateipfade werden feldweise zu „noch offen“. Die übrigen internen Referenzmuster und der konkrete Ist-Fakt-Schutz bleiben erhalten.
- **Grund:** Pauschale Wortlisten entfernten berechtigte Spezifität und konnten nach einer einzigen problematischen Formulierung einen ansonsten verwertbaren Output als `AIServiceError` verwerfen.
- **Konsequenzen:** Sicherheitsgrenzen bleiben erhalten, sind aber kontext- und feldbezogen. Die automatisierte Suite enthält getrennte Fälle für Nutzerwort, Beispielwort, Zukunftsformulierung, erfundenen Ist-Fakt, interne Referenz und fortgesetzte Restanalyse.
- **Status:** Implemented and tested; reale Modellbeobachtung bleibt erforderlich

## DEC-024 – Legacy-Shim bleibt, erzeugte Platzhalter bleiben unsichtbar

- **Datum:** 2026-08-06
- **Entscheidung:** `fill_legacy_core_output()` bleibt bestehen. In der lokal konfigurierten Datenbank `ai_start_map` wurden 35 Analysen gefunden, 17 davon mit `core_output`: 15 im alten und zwei im aktuellen Format. Der Shim protokolliert die Namen erfundener Felder ohne Inhalte; `customer_visible_dump()` und die Datenbank-View unterdrücken diese Platzhalter. Die v3-Felder `software_rule`, `open_details`, `smallest_usable_version`, `not_automated` und `autonomy_level` werden für Altanalysen nicht erfunden.
- **Grund:** Entfernen würde vorhandene Altanalysen unlesbar machen; generische Sätze würden zugleich eine fachliche Präzision vortäuschen, die nicht gespeichert ist.
- **Konsequenzen:** Neue Structured Outputs müssen den v3-Vertrag erfüllen. Alte Daten bleiben lesbar, können aber leere neue Abschnitte haben. Keine Datenmigration wurde ausgeführt.
- **Status:** Implemented and tested

## DEC-025 – FinalAnalysisResult nutzt medium Reasoning und zwei Versuche

- **Datum:** 2026-08-06
- **Entscheidung:** Für das konfigurierte `gpt-5-mini` verwendet nur `FinalAnalysisResult` `reasoning_effort=medium`, maximal zwei Anwendungsversuche und ein gemeinsames Zeitbudget von 120 Sekunden. Andere GPT-5-Aufrufe bleiben bei `minimal`; Follow-up bleibt bei einem Versuch. Der finale Prompt enthält genau 15 inhaltliche Kernregeln und wiederholt keine Pydantic-Längen- oder Typvorgaben.
- **Grund:** Der umfangreichere Kundenvertrag benötigt mehr Sorgfalt; ein zweiter Versuch soll einen einzelnen Schema- oder Groundingfehler reparieren können.
- **Messung:** Ein kontrollierter echter Hausmeister-Aufruf bestand am ersten Versuch in 60,141 Sekunden, ohne Retry, mit den sechs deterministischen OUT-SP03-Feldern. Stichprobe `n=1`; daraus wird weder eine belastbare Fehlerquote noch eine allgemeine Latenzzusage abgeleitet.
- **Status:** Implemented, API-kompatibel live geprüft und automatisiert getestet
