# AI Start Map – kuratierter RAG-Korpus aus zehn realen KMU-Fällen

Jeder Chunk ist semantisch getrennt. `case_evidence` enthält ausschließlich quellenbasierten Ist-Zustand. Fragen, Automationsmuster und Guardrails sind fachliche Ableitungen und entsprechend markiert.

**Prompt-Guardrail:** Gefundene Fälle dienen nur als Vergleichsmuster. Mengen, Tools, Abläufe, Risiken oder Geschäftsdaten dürfen niemals als Fakten über das aktuell analysierte Unternehmen übernommen werden.

## Chunk: C-01_case_evidence – Kleiner Elektro-/technischer Servicebetrieb mit drei Fahrzeugen

```yaml
chunk_id: C-01_case_evidence
document_id: ten_cases_01
case_id: C-01
chunk_type: case_evidence
pattern_id: P-01
pattern_ids: ["P-01", "P-02"]
process_tags: ["field_service", "quote_creation", "job_handoff"]
pain_tags: ["media_break", "manual_transfer", "fragmented_job_record"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/electricians/comments/1ai9ya1/what_kind_of_tabletlaptop_do_you_guys_carry_in/
language: de
```

### Quellenbasis

Primärquelle ist der Erstbericht eines Verantwortlichen in einem Elektro-/Servicebetrieb: [„What kind of tablet/laptop do you guys carry in the field?“](https://www.reddit.com/r/electricians/comments/1ai9ya1/what_kind_of_tabletlaptop_do_you_guys_carry_in/). Als Branchenabgleich dient ein zweiter, nicht mit dem ersten Betrieb vermischter Bericht eines Solo-Elektrikers: [„What’s the best way to keep track of customers and jobs as a solo electrician?“](https://www.reddit.com/r/electricians/comments/1lblm8r/whats_the_best_way_to_keep_track_of_customers_and/).

## Chunk: C-01_interview_questions – Diagnosefragen zu Kleiner Elektro-/technischer Servicebetrieb mit drei Fahrzeugen

```yaml
chunk_id: C-01_interview_questions
document_id: ten_cases_01
case_id: C-01
chunk_type: interview_question_set
pattern_id: P-01
pattern_ids: ["P-01", "P-02"]
process_tags: ["field_service", "quote_creation", "job_handoff"]
pain_tags: ["media_break", "manual_transfer", "fragmented_job_record"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

1. Wie viele Begehungen, Angebote und Serviceaufträge entstehen pro Woche?
2. Welche Angaben sind für jedes Angebot zwingend: Kunde, Standort, Leistungsart, Maße, Lastdaten, Material, Stunden, Marge, Steuer, Genehmigung?
3. Welche Angaben können vor Ort strukturiert werden und welche bleiben Freitext, Skizze oder Foto?
4. Gibt es wiederkehrende Leistungen und eine gepflegte Material-/Preisbibliothek?
5. Wer darf Preise, Materialmengen und endgültige Angebote freigeben?
6. Wie werden Auftrag, Foto, Notiz, Plan und Angebot heute eindeutig miteinander verknüpft?
7. Welche Software erstellt Angebote, Rechnungen und Termine tatsächlich?
8. Müssen Techniker offline arbeiten können?
9. Welche Geräte nutzt die Crew und wie erhält sie Arbeitsunterlagen?
10. Welche Informationen ändern sich nach Angebotsannahme und wie werden Änderungen dokumentiert?
11. Welche Fotos oder Pläne enthalten personenbezogene Daten, Sicherheitsinformationen oder Gebäudezugänge?
12. Gibt es APIs oder zumindest CSV-/PDF-Exporte der eingesetzten Bürosoftware?

### Zusätzliche dynamische Rückfragen

1. „Du nennst Telefon, iPad und Desktop: Welche Information entsteht zuerst auf welchem Gerät?“
2. „Welche Daten tippst du für ein Angebot ein zweites Mal ein?“
3. „Was muss zwingend vorhanden sein, bevor du einen Preis nennen kannst?“
4. „Welche Entscheidungen darf nur eine fachlich verantwortliche Person treffen?“
5. „Wie erkennt die Crew, ob ein Plan die neueste Version ist?“
6. „Kann ein Auftrag ohne Netzverbindung aufgenommen werden müssen?“

## Chunk: C-01_automation_patterns – Mögliche Automationsmuster zu Kleiner Elektro-/technischer Servicebetrieb mit drei Fahrzeugen

```yaml
chunk_id: C-01_automation_patterns
document_id: ten_cases_01
case_id: C-01
chunk_type: automation_pattern
pattern_id: P-01
pattern_ids: ["P-01", "P-02"]
process_tags: ["field_service", "quote_creation", "job_handoff"]
pain_tags: ["media_break", "manual_transfer", "fragmented_job_record"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

### A. Strukturierte mobile Vor-Ort-Aufnahme

- **Problem:** Informationen entstehen getrennt als Telefonnotiz, Skizze, Foto und Materialliste.
- **Idee:** Ein mobiles Auftragsformular legt pro Begehung einen Job-Datensatz an; Spracheingabe wird strukturiert, Fotos und Skizzen erhalten dieselbe Job-ID.
- **Eingaben:** Kunde/Standort, Leistungsart, Diktat, Maße, Material, Fotos, Skizze, offene Punkte.
- **Ausgabe:** Vollständigkeitsgeprüfter Begehungsdatensatz plus Liste fehlender Pflichtfelder.
- **Mögliche Integration:** Mobile Web-App/FastAPI, PostgreSQL, Dateiablage, n8n-Webhook, optional Structured Outputs für das Diktat.
- **Freigabe:** Techniker bestätigt die extrahierten Felder vor dem Speichern.
- **Nutzen:** Ein Auftrag statt mehrerer unverbundener Dateien; weniger Nacharbeit.
- **Aufwand:** Mittel.
- **Risiken:** Schlechte Spracherkennung, falsche Zuordnung, Offline-Nutzung, sensible Standortdaten.
- **Warum passend:** Der Betrieb arbeitet bereits stark visuell und mobil; das Problem ist die Zusammenführung, nicht fehlende Datenerfassung.

### B. Angebotsentwurf aus Begehungsdaten

- **Problem:** Daten werden am Desktop erneut zusammengesucht und übertragen.
- **Idee:** Nach bestätigter Aufnahme erzeugt das System einen Angebotsentwurf aus Leistungsbausteinen, Materialliste und internen Preisregeln.
- **Eingaben:** Freigegebene Begehungsdaten, Preis-/Materialbibliothek, Stundensätze, Steuer- und Margenregeln.
- **Ausgabe:** Kalkulationsentwurf, offene Preispositionen, kundenfähiger Angebotsentwurf.
- **Mögliche Integration:** FastAPI-Backend, PostgreSQL, Dokumenttemplate, n8n für Orchestrierung und Benachrichtigung.
- **Freigabe:** Betriebsverantwortlicher prüft Mengen, Preis, Leistungsumfang und Ausschlüsse; kein automatischer Versand.
- **Nutzen:** Kürzere Durchlaufzeit und konsistentere Angebote.
- **Aufwand:** Mittel bis hoch, weil Kalkulationsregeln branchenspezifisch validiert werden müssen.
- **Risiken:** Falsche Preise oder technische Mengen; Haftung bei unklarer Leistungsbeschreibung.
- **Warum passend:** Genau die Material-, Plan- und Fotodaten, die heute manuell übertragen werden, speisen den Entwurf.

### C. Versioniertes Job-Paket für die Crew

- **Problem:** Crew-Anweisungen, Pläne, Fotos und Materialänderungen können auseinanderlaufen.
- **Idee:** Nach Angebotsannahme wird automatisch ein Job-Paket mit aktueller Version, Materialliste, annotierten Fotos, offenen Punkten und Änderungsprotokoll erstellt.
- **Eingaben:** Angenommenes Angebot, freigegebene Medien, Termin, Crew, Materialstatus.
- **Ausgabe:** Mobile Jobansicht/PDF, Aufgabenliste und Änderungsbenachrichtigung.
- **Mögliche Integration:** PostgreSQL, Dateiablage, Kalender/Jobsoftware – nur nach Prüfung der realen Schnittstellen.
- **Freigabe:** Verantwortlicher veröffentlicht jede neue Version.
- **Nutzen:** Weniger telefonische Rückfragen und geringeres Risiko veralteter Arbeitsunterlagen.
- **Aufwand:** Mittel.
- **Risiken:** Mitarbeiter verwenden weiterhin lokale Altdateien; Zugriffsrechte; fehlende Netzabdeckung.
- **Warum passend:** Visuelle Crew-Kommunikation funktioniert bereits und wird lediglich in einen kontrollierten Auftragskontext gebracht.

### Wiederverwendbares Muster

**Field Intake → Structured Job Record → Human-approved Quote → Versioned Job Pack**

## Chunk: C-01_guardrails – Grenzen und Freigaben zu Kleiner Elektro-/technischer Servicebetrieb mit drei Fahrzeugen

```yaml
chunk_id: C-01_guardrails
document_id: ten_cases_01
case_id: C-01
chunk_type: automation_guardrail
pattern_id: P-01
pattern_ids: ["P-01", "P-02"]
process_tags: ["field_service", "quote_creation", "job_handoff"]
pain_tags: ["media_break", "manual_transfer", "fragmented_job_record"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Angebote, Materialbestellungen und verbindliche Einsatztermine dürfen nicht ohne menschliche Vollständigkeits- und Preisprüfung ausgelöst werden.

## Chunk: C-02_case_evidence – Etsy-Shop für 3D-gedruckte Tabletop-Modelle

```yaml
chunk_id: C-02_case_evidence
document_id: ten_cases_01
case_id: C-02
chunk_type: case_evidence
pattern_id: P-02
pattern_ids: ["P-02"]
process_tags: ["ecommerce_order", "production_planning", "quality_control"]
pain_tags: ["order_complexity", "missing_parts", "manual_stage_tracking"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/EtsySellers/comments/1bgzbtr/open_order_management/
language: de
```

### Quellenbasis

Primärquelle ist der detaillierte Erstbericht eines Etsy-Verkäufers: [„Open order management“](https://www.reddit.com/r/EtsySellers/comments/1bgzbtr/open_order_management/). Ein weiterer Etsy-Erstbericht belegt als Branchenabgleich das Skalierungsproblem individueller Auftragsdateien, wird aber nicht als derselbe Betrieb behandelt: [„How do you keep track of your orders?“](https://www.reddit.com/r/EtsySellers/comments/16gxrmo/how_do_you_keep_track_of_your_orders/).

## Chunk: C-02_interview_questions – Diagnosefragen zu Etsy-Shop für 3D-gedruckte Tabletop-Modelle

```yaml
chunk_id: C-02_interview_questions
document_id: ten_cases_01
case_id: C-02
chunk_type: interview_question_set
pattern_id: P-02
pattern_ids: ["P-02"]
process_tags: ["ecommerce_order", "production_planning", "quality_control"]
pain_tags: ["order_complexity", "missing_parts", "manual_stage_tracking"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

1. Wie viele offene Aufträge und Positionen gibt es durchschnittlich und in Spitzenzeiten?
2. Besitzt jedes Etsy-Listing eine stabile SKU/Varianten-ID?
3. Wo ist hinterlegt, aus welchen Einzelteilen ein Produkt besteht?
4. Wie viele Drucker gibt es, mit welchen Technologien, Bauvolumen und Laufzeiten?
5. Welche Teile können gemeinsam auf einer Druckplatte produziert werden?
6. Welche Statusstufen gelten genau: queued, printing, washing, drying, inspection, reprint, complete?
7. Wer darf einen Auftrag nach Qualitätsprüfung freigeben?
8. Wie werden Ausschuss, Nachdruck und Materialcharge dokumentiert?
9. Welche Teile werden make-to-order und welche auf Lager produziert?
10. Welche Etsy-Bearbeitungsfrist gilt pro Auftrag?
11. Wo und wie werden Versandlabel erstellt? Dieser Schritt fehlt in der Quelle.
12. Ist der Shop bereit und berechtigt, Etsy Open API v3 per OAuth zu verwenden?

### Zusätzliche dynamische Rückfragen

1. „Kann eine verkaufte Position aus mehreren physischen Teilen bestehen?“
2. „Welche Zustände durchläuft jedes Teil, bevor es als fertig gilt?“
3. „Welche Teile kommen in mehreren Aufträgen oder Produkten vor?“
4. „Was löst einen Nachdruck aus und wie wird er heute erkannt?“
5. „Welche Deadline bestimmt die Produktionspriorität?“
6. „Welche Schritte kann Etsy liefern und welche existieren nur in deiner Werkstatt?“

## Chunk: C-02_automation_patterns – Mögliche Automationsmuster zu Etsy-Shop für 3D-gedruckte Tabletop-Modelle

```yaml
chunk_id: C-02_automation_patterns
document_id: ten_cases_01
case_id: C-02
chunk_type: automation_pattern
pattern_id: P-02
pattern_ids: ["P-02"]
process_tags: ["ecommerce_order", "production_planning", "quality_control"]
pain_tags: ["order_complexity", "missing_parts", "manual_stage_tracking"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

### A. Etsy-Auftrag automatisch in Stückliste und Produktionsaufgaben zerlegen

- **Problem:** Aufträge mit vielen Positionen und mehrteiligen Produkten werden manuell gelesen und abgehakt.
- **Idee:** Offene Etsy-Aufträge abrufen, Listing/Variante einer gepflegten Stückliste zuordnen und pro benötigtem Teil eine Produktionsaufgabe erzeugen.
- **Eingaben:** Etsy-Auftrag, Listing-/Varianten-ID, Menge, Personalisierung, interne Stückliste.
- **Ausgabe:** Offene Teile je Auftrag, aggregierter Teilebedarf über alle Aufträge, Priorität nach Versandfrist.
- **Mögliche Integration:** Etsy Open API v3 via n8n HTTP Request, FastAPI/PostgreSQL, Web-Board.
- **Freigabe:** Betreiber bestätigt unbekannte Varianten und neue/änderte Stücklisten.
- **Nutzen:** Keine manuelle Übertragung; gemeinsame Teile werden gebündelt sichtbar.
- **Aufwand:** Mittel; hoch, falls Listings keine sauberen IDs/Stücklisten besitzen.
- **Risiken:** Falsche Variantenabbildung, API-Limits/Auth, Personalisierung im Freitext.
- **Warum passend:** Das Kernproblem ist die Zerlegung von bis zu 20 Positionen und mehrteiligen Modellen.

### B. Statusverfolgung auf Teil- und Prozessstufenebene

- **Problem:** Ein Haken auf Papier zeigt nicht, ob ein Teil gedruckt, gereinigt, getrocknet oder geprüft ist.
- **Idee:** Auftrag/Box und Teil erhalten QR-Code; an jeder Station wird der Status per Mobilgerät aktualisiert.
- **Eingaben:** Job-ID, Teil-ID, Status, Drucker, Zeit, Fehlergrund, optional Foto.
- **Ausgabe:** Aktueller WIP-Status, fehlende Teile, blockierte Aufträge, Nachdruckliste.
- **Mögliche Integration:** Mobile Web-App, Webhook, PostgreSQL, Dashboard.
- **Freigabe:** Qualitätsstatus „passed“ muss manuell gesetzt werden.
- **Nutzen:** Weniger vergessene oder doppelt gedruckte Teile; schnelleres Auffinden von Blockern.
- **Aufwand:** Mittel.
- **Risiken:** Scan-Disziplin, zu viele Klicks, Etiketten/QR-Codes in Resin-Umgebung.
- **Warum passend:** Die Quelle nennt exakt die mehrstufige Resin-Fertigung und fehlende Kleinteile als Engpass.

### C. Druckwarteschlange mit Prioritäts- und Bündelungsvorschlägen

- **Problem:** Kleine, hohe, häufige und auftragsbezogene Teile konkurrieren um Druckkapazität.
- **Idee:** Das System schlägt Druckbatches anhand von Versandfrist, Teilehöhe/Laufzeit, Druckertyp, vorhandenen Beständen und gemeinsamen Bedarfen vor.
- **Eingaben:** Offener Bedarf, Druckdauer, Geometrie-/Kompatibilitätsmerkmale, Druckerkapazität, Bestand, Deadline.
- **Ausgabe:** Rangierte Batch-Vorschläge und Warnung vor gefährdeten Aufträgen.
- **Mögliche Integration:** Eigenes Optimierungsmodul/FastAPI; n8n orchestriert Daten und Benachrichtigungen.
- **Freigabe:** Betreiber wählt und startet den tatsächlichen Druckbatch.
- **Nutzen:** Bessere Auslastung und weniger verspätete Aufträge.
- **Aufwand:** Hoch, wenn Slicer-/Geometriedaten einbezogen werden; mittel für einfache heuristische Regeln.
- **Risiken:** Ein mathematisch guter Batch kann praktisch schlecht druckbar sein; Geräte-/Materialbesonderheiten.
- **Warum passend:** Der Betreiber plant bereits manuell nach Tageszeit und Teilehöhe; die Automation formalisiert vorhandene Regeln.

### Wiederverwendbares Muster

**Order Intake → BOM Explosion → WIP Stage Tracking → QC Gate → Ready-to-Ship**

## Chunk: C-02_guardrails – Grenzen und Freigaben zu Etsy-Shop für 3D-gedruckte Tabletop-Modelle

```yaml
chunk_id: C-02_guardrails
document_id: ten_cases_01
case_id: C-02
chunk_type: automation_guardrail
pattern_id: P-02
pattern_ids: ["P-02"]
process_tags: ["ecommerce_order", "production_planning", "quality_control"]
pain_tags: ["order_complexity", "missing_parts", "manual_stage_tracking"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Produktionsprioritäten, Qualitätsfreigaben und Versandbereitschaft dürfen nicht allein aus einem Modellvorschlag abgeleitet werden.

## Chunk: C-03_case_evidence – Reinigungsbetrieb mit fünf Auftragnehmern und rund 160 Einsätzen pro Monat

```yaml
chunk_id: C-03_case_evidence
document_id: ten_cases_01
case_id: C-03
chunk_type: case_evidence
pattern_id: P-03
pattern_ids: ["P-03"]
process_tags: ["customer_intake", "workforce_scheduling", "rescheduling"]
pain_tags: ["constraint_conflict", "travel_time", "manual_rescheduling"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/sweatystartup/comments/1hbic3f/cleaning_company_owners_whats_your_process_for/
language: de
```

### Quellenbasis

Primärquelle ist der öffentliche Erstbericht: [„Cleaning Company Owners – what’s your process for scheduling jobs?“](https://www.reddit.com/r/sweatystartup/comments/1hbic3f/cleaning_company_owners_whats_your_process_for/). Die Antworten des Accounts im selben Thread werden demselben Fall zugerechnet. Eine ältere, separate Reinigungsfirma beschreibt ergänzend, welche Daten beim Kunden-Onboarding fehlen; sie dient nur als Branchenabgleich: [„Looking for a software solution for our cleaning biz“](https://www.reddit.com/r/smallbusiness/comments/72irfr/looking_for_a_software_solution_for_our_cleaning/).

## Chunk: C-03_interview_questions – Diagnosefragen zu Reinigungsbetrieb mit fünf Auftragnehmern und rund 160 Einsätzen pro Monat

```yaml
chunk_id: C-03_interview_questions
document_id: ten_cases_01
case_id: C-03
chunk_type: interview_question_set
pattern_id: P-03
pattern_ids: ["P-03"]
process_tags: ["customer_intake", "workforce_scheduling", "rescheduling"]
pain_tags: ["constraint_conflict", "travel_time", "manual_rescheduling"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

1. Wie lange dauert jeder Job realistisch und wie stark schwankt die Dauer?
2. Welche Kundenzeitfenster sind hart und welche verhandelbar?
3. Wie wird Contractor-Verfügbarkeit erfasst und wann ist sie verbindlich?
4. Welche Cleaner dürfen welche Kunden/Leistungen übernehmen?
5. Gibt es feste Teams, bevorzugte Kunden-Cleaner-Zuordnungen oder Schlüssel-/Zugangsabhängigkeiten?
6. Welche Start-/Endorte und maximalen Fahrzeiten gelten je Contractor?
7. Werden Fahrtzeit oder Kilometer vergütet?
8. Welche Mindestmarge bzw. maximale Fahrtzeit macht einen Auftrag wirtschaftlich?
9. Wie viele Änderungen treten nach Veröffentlichung des Wochenplans auf?
10. Wer darf einen Plan final freigeben und Kunden umterminieren?
11. Welche Jobber-Funktionen, Exporte, Webhooks oder API-Rechte stehen im konkreten Tarif zur Verfügung?
12. Welche personenbezogenen Daten, Adressen, Zugangscodes oder Schlüsselhinweise werden verarbeitet?

### Zusätzliche dynamische Rückfragen

1. „Welche Terminregeln sind unverhandelbar und welche nur Wünsche?“
2. „Wie lange dauert ein Job und woher stammt diese Dauer?“
3. „Von wo startet jede Reinigungskraft und wie viel Fahrt ist akzeptabel?“
4. „Welche Kunden müssen bei derselben Reinigungskraft bleiben?“
5. „Wie häufig ändert sich ein bereits veröffentlichter Plan?“
6. „Was kann Jobber in eurem konkreten Tarif importieren/exportieren?“

## Chunk: C-03_automation_patterns – Mögliche Automationsmuster zu Reinigungsbetrieb mit fünf Auftragnehmern und rund 160 Einsätzen pro Monat

```yaml
chunk_id: C-03_automation_patterns
document_id: ten_cases_01
case_id: C-03
chunk_type: automation_pattern
pattern_id: P-03
pattern_ids: ["P-03"]
process_tags: ["customer_intake", "workforce_scheduling", "rescheduling"]
pain_tags: ["constraint_conflict", "travel_time", "manual_rescheduling"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

### A. Strukturierter Kunden- und Job-Intake mit planbaren Constraints

- **Problem:** Sonderrhythmen und Zeitrestriktionen werden erst beim Planen sichtbar.
- **Idee:** Bei Buchung/Onboarding werden Rhythmus, Dauer, Adresse, harte/weiche Zeitfenster, Zugang und Flexibilität als strukturierte Felder erfasst.
- **Eingaben:** Adresse, Leistung, Dauer, Frequenz, frühester/spätester Termin, bevorzugter Tag, Flexibilität, Zugang, Sonderanforderungen.
- **Ausgabe:** Planbarer Job-Datensatz; fehlende oder widersprüchliche Angaben werden markiert.
- **Mögliche Integration:** Webformular, n8n-Webhook, PostgreSQL; Jobber nur nach Schnittstellenprüfung.
- **Freigabe:** Büro bestätigt Preis, Dauer und Rhythmus.
- **Nutzen:** Weniger Rückfragen und weniger implizite Regeln im Kopf des Betreibers.
- **Aufwand:** Niedrig bis mittel.
- **Risiken:** Kunden geben unrealistische Dauer an; sensible Zugangsdaten.
- **Warum passend:** Gerade individuelle Wiederholungsmuster brechen die bisher erwogenen starren Regeln.

### B. Constraint- und distanzbasierter Wochenplan-Vorschlag

- **Problem:** Der Betreiber kombiniert Volumen, Wiederholungen, individuelle Tage, Personal und Routing manuell.
- **Idee:** Ein Planungsdienst erzeugt mehrere rangierte Vorschläge unter harten und weichen Constraints.
- **Eingaben:** Jobs, Dauer, Zeitfenster, Adresse/Koordinaten, Contractor-Verfügbarkeit, Skills/Präferenzen, Startorte, bestehende Zuweisungen.
- **Ausgabe:** Vorschlag je Contractor, Fahrtzeit, Konflikte, unzugewiesene Jobs und Begründung für Regelverletzungen.
- **Mögliche Integration:** FastAPI/PostgreSQL plus Routing-/Optimierungsbibliothek; n8n stößt Berechnung an und verteilt das Ergebnis.
- **Freigabe:** Betreiber prüft und veröffentlicht den Plan.
- **Nutzen:** Weniger Planungszeit und transparentere Trade-offs.
- **Aufwand:** Hoch für echte Optimierung; mittel für ein regelbasiertes MVP.
- **Risiken:** Falsche Fahrzeiten, unvollständige Verfügbarkeit, Scheingenauigkeit, unfaire Touren.
- **Warum passend:** Der Fall enthält echte konkurrierende Constraints; ein einfacher Kalender löst das Problem nicht.

### C. Änderungs- und Ausfall-Workflow mit Auswirkungsanalyse

- **Problem:** Eine Änderung kann weitere Termine und Routen destabilisieren.
- **Idee:** Absage/Ausfall startet einen Workflow, der betroffene Jobs ermittelt, Ersatzoptionen rangiert und erst nach Freigabe Contractor und Kunde informiert.
- **Eingaben:** Betroffener Job/Contractor, Änderungsgrund, neues Zeitfenster, aktuelle Woche.
- **Ausgabe:** Ersatzvorschläge, betroffene Folgejobs, Nachrichtentwürfe und bestätigter Änderungsstatus.
- **Mögliche Integration:** Webhook/Formular, Planungsservice, Kalender/Jobber nach technischer Prüfung, E-Mail/SMS nur mit bestätigten Kanälen.
- **Freigabe:** Betreiber wählt Option; Contractor bestätigt; danach Kundeninformation.
- **Nutzen:** Schnellere Reaktion, weniger vergessene Folgeänderungen.
- **Aufwand:** Mittel bis hoch.
- **Risiken:** Automatische Nachrichten vor interner Klärung, Doppelbuchung, Datenschutz.
- **Warum passend:** Feiertage und individuelle Terminänderungen sind ausdrücklich als wiederkehrender Schmerz genannt.

### Wiederverwendbares Muster

**Structured Service Intake → Constraint Model → Ranked Schedule → Human Approval → Change Propagation**

## Chunk: C-03_guardrails – Grenzen und Freigaben zu Reinigungsbetrieb mit fünf Auftragnehmern und rund 160 Einsätzen pro Monat

```yaml
chunk_id: C-03_guardrails
document_id: ten_cases_01
case_id: C-03
chunk_type: automation_guardrail
pattern_id: P-03
pattern_ids: ["P-03"]
process_tags: ["customer_intake", "workforce_scheduling", "rescheduling"]
pain_tags: ["constraint_conflict", "travel_time", "manual_rescheduling"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Eine Planung darf nur vorgeschlagen werden; Verfügbarkeit, Qualifikation, Fahrtzeit und betroffene Kundenzusagen müssen vor Bestätigung geprüft werden.

## Chunk: C-04_case_evidence – Medizinische Solo-Praxis mit offenen Patientenforderungen

```yaml
chunk_id: C-04_case_evidence
document_id: ten_cases_01
case_id: C-04
chunk_type: case_evidence
pattern_id: P-04
pattern_ids: ["P-04"]
process_tags: ["medical_billing", "insurance_followup", "payment_collection"]
pain_tags: ["open_claims", "unclear_patient_balance", "high_sensitivity"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: health_and_financial_data
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/smallbusiness/comments/1rf1ng8/is_it_worth_the_effort/
language: de
```

### Quellenbasis

Primärquelle ist der öffentliche Erstbericht einer Praxisinhaberin: [„Is it worth the effort?“](https://www.reddit.com/r/smallbusiness/comments/1rf1ng8/is_it_worth_the_effort/). Die Kommentare liefern mögliche Vorgehensweisen, sind aber keine Fakten über den Betrieb. Für den Datenschutzrahmen dient die offizielle [HIPAA Privacy Rule des US-Gesundheitsministeriums](https://www.hhs.gov/hipaa/for-professionals/privacy/index.html): Sie schützt medizinische Akten und andere individuell identifizierbare Gesundheitsinformationen bei erfassten Leistungserbringern.

### Quellenbasierte Aussagen zum Unternehmen und Ist-Prozess

**[Quelle]** Die Inhaberin behandelt selbst und übernimmt zugleich die kaufmännische Seite. Sie stellt Zuzahlungen häufig erst in Rechnung, nachdem die Person die Praxis verlassen hat, weil ihr das Zahlungsgespräch unangenehm ist. Es bestehen Forderungen von 120 bis 700 US-Dollar und insgesamt mehrere Tausend Dollar Außenstand. Ein Versicherungsfall wurde abgelehnt, weil die Person zuvor wegen desselben Problems zu viele Ärzte aufgesucht habe; die Person verweigert nun die Zahlung.

## Chunk: C-04_interview_questions – Diagnosefragen zu Medizinische Solo-Praxis mit offenen Patientenforderungen

```yaml
chunk_id: C-04_interview_questions
document_id: ten_cases_01
case_id: C-04
chunk_type: interview_question_set
pattern_id: P-04
pattern_ids: ["P-04"]
process_tags: ["medical_billing", "insurance_followup", "payment_collection"]
pain_tags: ["open_claims", "unclear_patient_balance", "high_sensitivity"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: health_and_financial_data
evidence_scope: expert_derived_from_case
language: de
```

1. In welchem Land/Bundesstaat gilt welcher Abrechnungs-, Inkasso- und Datenschutzrahmen?
2. Welche Termin-, EHR-, Claim- und Zahlungssoftware wird verwendet?
3. Wer prüft Eligibility, Prior Authorization, Codes und Denials?
4. Welche Beträge sind vor dem Termin sicher bekannt und welche nur Schätzungen?
5. Welche Fristen gelten je Versicherer für Korrektur und Einspruch?
6. Wie werden Erklärungen der Leistungsabrechnung mit Patientensalden abgeglichen?
7. Welche Zahlungspläne, Härtefälle und Kulanzregeln existieren?
8. Ab welchem Alter/Betrag wird persönlich geprüft, abgeschrieben oder an Inkasso übergeben?
9. Welche Kanäle dürfen für geschützte Gesundheits- und Zahlungsdaten verwendet werden?
10. Kann ein Automationsanbieter einen erforderlichen Auftragsverarbeitungs-/Business-Associate-Vertrag und passende Sicherheitskontrollen erfüllen?

## Chunk: C-04_automation_patterns – Mögliche Automationsmuster zu Medizinische Solo-Praxis mit offenen Patientenforderungen

```yaml
chunk_id: C-04_automation_patterns
document_id: ten_cases_01
case_id: C-04
chunk_type: automation_pattern
pattern_id: P-04
pattern_ids: ["P-04"]
process_tags: ["medical_billing", "insurance_followup", "payment_collection"]
pain_tags: ["open_claims", "unclear_patient_balance", "high_sensitivity"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: health_and_financial_data
evidence_scope: expert_derived_from_case
language: de
```

### A. Vor-Termin-Arbeitsliste für Versicherungs- und Eigenanteilsklärung

- **Problem:** finanzielle Verantwortung wird zu spät sichtbar.
- **Idee:** Für kommende Termine werden fehlende Versicherungsprüfung, Genehmigung und Zahlungsinformation als Aufgaben erzeugt; das System formuliert nur eine Schätzung/Erklärung.
- **Eingaben:** Termin, Versicherungsdaten, Leistungskategorie, Vertragsregeln, Prüfstatus.
- **Ausgabe:** Ampel „klar/unklar/prüfen“, dokumentierte Schätzung und Gesprächsleitfaden.
- **Tools/Integrationen:** Praxissoftware/Eligibility-Portal nur bei verifizierter Schnittstelle; sonst datensparsamer Import.
- **Freigabe:** Inhaberin prüft unklare oder hohe Beträge vor Kommunikation.
- **Nutzen:** weniger Überraschungen und weniger nachträgliche Forderungen.
- **Aufwand:** mittel bis hoch.
- **Risiken:** falsche Kostengarantie, Datenschutz, Versicherungsregeln.
- **Fallpassung:** greift den belegten Copay-nach-dem-Besuch-Engpass an.

### B. Denial- und Fristen-Workqueue

- **Problem:** Versicherungsablehnungen können zwischen Behandlung und Verwaltung liegen bleiben.
- **Idee:** Antwortdokumente klassifizieren, Ablehnungsgrund/Frist extrahieren und eine prüfbare Aufgabe mit vollständigen Belegen anlegen.
- **Eingaben:** Claim-ID, Versicherungsantwort, Patientenkonto, Fristenkalender.
- **Ausgabe:** priorisierte Queue, fehlende Unterlagen, Entwurf für Korrektur/Einspruch.
- **Tools/Integrationen:** Dokumenteingang, gesichertes DMS/EHR, Aufgabenliste; nur zugelassene Infrastruktur.
- **Freigabe:** medizinische und abrechnungsbezogene Entscheidung immer durch die Praxis.
- **Nutzen:** weniger Fristverlust, nachvollziehbare Verantwortlichkeit.
- **Aufwand:** hoch.
- **Risiken:** Fehlklassifikation und unzulässige Offenlegung.
- **Fallpassung:** ein realer Denial mit ungeklärter Patientenzahlung ist belegt.

### C. Patientenfreundliche Mahn- und Ausnahme-Kaskade

- **Problem:** offene Salden werden ungern und uneinheitlich verfolgt.
- **Idee:** Nach finaler Saldo-Freigabe gestufte Rechnungen/Erinnerungen mit Stop bei Widerspruch, Härtefall oder Zahlung.
- **Eingaben:** freigegebener Saldo, Fälligkeit, Kontaktpräferenz, Regelwerk, Zahlungsstatus.
- **Ausgabe:** protokollierte Nachricht, Zahlungslink/Anweisung, Eskalationsaufgabe.
- **Tools/Integrationen:** bestehendes Billing-/Payment-System; keine privaten Consumer-Kanäle ohne Freigabe.
- **Freigabe:** erste Vorlage, jeder Streitfall sowie Inkasso/Abschreibung.
- **Nutzen:** regelmäßige Nachverfolgung ohne jedes Gespräch persönlich initiieren zu müssen.
- **Aufwand:** mittel.
- **Risiken:** falscher Betrag, unzulässiger Kanal, Reputationsschaden.
- **Fallpassung:** adressiert die erklärte emotionale und operative Blockade.

## Chunk: C-04_guardrails – Grenzen und Freigaben zu Medizinische Solo-Praxis mit offenen Patientenforderungen

```yaml
chunk_id: C-04_guardrails
document_id: ten_cases_01
case_id: C-04
chunk_type: automation_guardrail
pattern_id: P-04
pattern_ids: ["P-04"]
process_tags: ["medical_billing", "insurance_followup", "payment_collection"]
pain_tags: ["open_claims", "unclear_patient_balance", "high_sensitivity"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: health_and_financial_data
evidence_scope: expert_derived_from_case
language: de
```

Keine autonome medizinische, versicherungsrechtliche oder rechtliche Entscheidung; Patientenkommunikation, Mahnstufen und sensible Daten benötigen strikte Rollen- und Freigaberegeln.

## Chunk: C-05_case_evidence – Solo-Betrieb für maßgefertigte Möbel und Metallarbeiten

```yaml
chunk_id: C-05_case_evidence
document_id: ten_cases_01
case_id: C-05
chunk_type: case_evidence
pattern_id: P-01
pattern_ids: ["P-01", "P-02"]
process_tags: ["lead_followup", "custom_quote", "consignment_tracking"]
pain_tags: ["lost_leads", "pricing_uncertainty", "missing_status"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/smallbusiness/comments/aqfkc1/i_make_furniture_for_a_living_but_im_thinking_of/
language: de
```

### Quellenbasis

Primärquelle ist der ausführliche Erstbericht [„I make furniture for a living. But I’m thinking of throwing in the towel“](https://www.reddit.com/r/smallbusiness/comments/aqfkc1/i_make_furniture_for_a_living_but_im_thinking_of/). Kommentare werden nur dann als Betriebsfakt verwendet, wenn der ursprüngliche Autor selbst antwortet; fremde Strategievorschläge sind keine Quelle für seinen Ist-Prozess.

### Quellenbasierte Aussagen zum Unternehmen und Ist-Prozess

**[Quelle]** Der Unternehmer entwirft und fertigt, schreibt frühere Großkunden per E-Mail an, lädt zu Mittagessen ein und versucht neue Marktwege. Frühere Projekte lagen bei 30.000–50.000 Dollar. Gleichzeitig ist das Kleinproduktgeschäft wirtschaftlich eng: Eine 300-Dollar-Couchtisch-Referenz enthält 120 Dollar Material und einen ganzen Arbeitstag. Der Betreiber berichtet außerdem von Konsignation über zeitweise sechs Läden; Stücke können Monate bis zu einem Jahr liegen und beschädigt zurückkommen. Typische genannte Verkaufspreise waren etwa 300 Dollar für einen Tisch und 450 Dollar für einen Stuhl.

Sechs Läden, lange Liegedauer und beschädigte Rückgaben sind **[Quelle]**. Vertrags- und Abrechnungsdetails sind unbekannt.

## Chunk: C-05_interview_questions – Diagnosefragen zu Solo-Betrieb für maßgefertigte Möbel und Metallarbeiten

```yaml
chunk_id: C-05_interview_questions
document_id: ten_cases_01
case_id: C-05
chunk_type: interview_question_set
pattern_id: P-01
pattern_ids: ["P-01", "P-02"]
process_tags: ["lead_followup", "custom_quote", "consignment_tracking"]
pain_tags: ["lost_leads", "pricing_uncertainty", "missing_status"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

1. Welche Leadquellen erzeugten die profitablen Projekte der ersten zwei Jahre?
2. Welche Kontakte dürfen erneut angesprochen werden und mit welcher Frequenz?
3. Welche Pflichtfelder braucht ein belastbarer Designbrief?
4. Wie werden Arbeitsstunden, Material, Ausschuss, Fremdleistung und Lieferung kalkuliert?
5. Welche Mindestmarge bzw. Preisuntergrenze gilt?
6. Wer außer dem Inhaber kann Entwurf oder Angebot freigeben?
7. Wie viele Projekte können parallel gebaut werden und welcher Engpass bestimmt Kapazität?
8. Welche Konsignationsverträge, Provisionen, Inventurlisten und Haftungsregeln existieren?
9. Wie oft melden Stores Bestand und Verkauf?
10. Sind historische Bank-, Angebots-, Kontakt- und Fotodaten digital auswertbar?

## Chunk: C-05_automation_patterns – Mögliche Automationsmuster zu Solo-Betrieb für maßgefertigte Möbel und Metallarbeiten

```yaml
chunk_id: C-05_automation_patterns
document_id: ten_cases_01
case_id: C-05
chunk_type: automation_pattern
pattern_id: P-01
pattern_ids: ["P-01", "P-02"]
process_tags: ["lead_followup", "custom_quote", "consignment_tracking"]
pain_tags: ["lost_leads", "pricing_uncertainty", "missing_status"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

### A. Kontakt- und Chancenpipeline mit Verlustgrund

- **Problem:** wertvolle Beziehungen werden punktuell per E-Mail reaktiviert, ohne lernfähige Historie.
- **Idee:** Kontakte, frühere Projekte, letzte Interaktion, erwarteter Bedarf und Follow-up als Pipeline; keine Massenmail.
- **Eingaben:** Kontakt, Projektwert/-art, Datum, Quelle, Antwort, nächster Schritt.
- **Ausgabe:** priorisierte persönliche Follow-ups und Kanalbericht.
- **Tools:** E-Mail-Import/CRM oder Airtable; konkrete vorhandene Systeme unbekannt.
- **Freigabe:** jede persönliche Nachricht durch den Inhaber.
- **Nutzen:** weniger vergessene Kontakte, sichtbarere Leadqualität.
- **Aufwand:** niedrig bis mittel.
- **Risiken:** aufdringliche Ansprache, schlechte Alt-Daten.
- **Passung:** bildet die belegten E-Mail-/Lunch-Versuche systematisch ab.

### B. Projektbrief, Angebotsentwurf und Preisuntergrenze

- **Problem:** individuelle Projekte können trotz Umsatz unprofitabel sein.
- **Idee:** strukturierter Brief erzeugt Material-/Zeitfragen und einen Kalkulationsentwurf; Regel blockiert Angebote unter der freigegebenen Untergrenze.
- **Eingaben:** Maße, Material, Komplexität, Lieferort, Stundenannahmen, Einkaufspreise.
- **Ausgabe:** Lückenliste, Angebot, Szenarien und erwarteter Deckungsbeitrag.
- **Tools:** Formular, Kalkulation, Dokumentvorlage; Integrationen erst nach Systeminventur.
- **Freigabe:** Design, Stunden und Endpreis bleiben beim Handwerker.
- **Nutzen:** schützt knappe Fertigungszeit.
- **Aufwand:** mittel.
- **Risiken:** Unikate lassen sich nicht vollständig standardisieren.
- **Passung:** reagiert auf das konkrete 120-Dollar-plus-Arbeitstag-Beispiel.

### C. Konsignationsregister mit Alterung und Zustandsbeleg

- **Problem:** Ware liegt lange extern und kommt teils beschädigt zurück.
- **Idee:** jedes Stück erhält ID, Übergabefotos, Store, Preis, Provision, Alter und monatliche Bestätigung; überfällige Bestände werden zur Entscheidung vorgelegt.
- **Eingaben:** Stückdaten, Fotos, Vertrag, Übergabe-/Verkaufs-/Rückgabestatus.
- **Ausgabe:** Bestandsabgleich, Aging-Liste, Abrechnung und Schadensfallpaket.
- **Tools:** mobiles Formular, Datenbank, E-Mail-Reminder; Barcode optional.
- **Freigabe:** Rückholung, Preisänderung und Schadensforderung.
- **Nutzen:** weniger gebundenes Inventar und bessere Beweislage.
- **Aufwand:** mittel.
- **Risiken:** Stores pflegen Status nicht; Vertragslage uneinheitlich.
- **Passung:** sechs Stores und monatelange Liegedauer sind quellenbelegt.

## Chunk: C-05_guardrails – Grenzen und Freigaben zu Solo-Betrieb für maßgefertigte Möbel und Metallarbeiten

```yaml
chunk_id: C-05_guardrails
document_id: ten_cases_01
case_id: C-05
chunk_type: automation_guardrail
pattern_id: P-01
pattern_ids: ["P-01", "P-02"]
process_tags: ["lead_followup", "custom_quote", "consignment_tracking"]
pain_tags: ["lost_leads", "pricing_uncertainty", "missing_status"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Preisuntergrenzen, Annahme individueller Projekte und Zustands-/Haftungsentscheidungen bleiben beim Inhaber.

## Chunk: C-06_case_evidence – Tattoo-Artist mit periodisch geöffneten Büchern

```yaml
chunk_id: C-06_case_evidence
document_id: ten_cases_01
case_id: C-06
chunk_type: case_evidence
pattern_id: P-01
pattern_ids: ["P-01", "P-03"]
process_tags: ["booking_intake", "creative_selection", "deposit_booking"]
pain_tags: ["submission_burst", "subjective_selection", "channel_break"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/TattooArtists/comments/15pcaw6/best_booking_method_looking_to_get_more/
language: de
```

### Quellenbasis

Primärfall ist der detaillierte Workflow eines praktizierenden Artists im Thread [„Best booking method?“](https://www.reddit.com/r/TattooArtists/comments/15pcaw6/best_booking_method_looking_to_get_more/). Ein separater Thread [über Tattoo-Assistenz](https://www.reddit.com/r/TattooArtists/comments/1elkjbw/artists_that_have_assistants_to_help_with/) dient nur als Branchenabgleich: Dort reduziert strukturierter Intake plus Assistenz den wöchentlichen Angebotscheck einer Künstlerin von einem ganzen Tag auf 15–20 Minuten. Square dokumentiert offiziell, dass seine [Bookings API Termine erstellen, lesen, ändern und stornieren kann](https://developer.squareup.com/docs/bookings-api/what-it-is); konkrete Berechtigungen/Tarife müssen geprüft werden.

### Quellenbasierte Aussagen zum Unternehmen und Ist-Prozess

**[Quelle]** Vor einer Öffnung kündigt der Artist Datum/Uhrzeit über Mailingliste und Instagram an. Zur Öffnung wird 24 Stunden lang ein Websiteformular publiziert. Danach werden Einreichungen geprüft, besonders große/spannende Projekte zuerst ausgewählt und kleinere Lücken gefüllt. Ausgewählte Personen erhalten einen Kalenderlink, wählen Zeit und zahlen über Square eine Anzahlung. Ist der Zeitraum voll, informiert der Artist die Mailingliste. E-Mails und DMs während geschlossener Bücher werden ignoriert; Hinweise stehen in Instagram-Highlights und auf der Website.

## Chunk: C-06_interview_questions – Diagnosefragen zu Tattoo-Artist mit periodisch geöffneten Büchern

```yaml
chunk_id: C-06_interview_questions
document_id: ten_cases_01
case_id: C-06
chunk_type: interview_question_set
pattern_id: P-01
pattern_ids: ["P-01", "P-03"]
process_tags: ["booking_intake", "creative_selection", "deposit_booking"]
pain_tags: ["submission_burst", "subjective_selection", "channel_break"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

1. Wie viele Einreichungen treffen in 24 Stunden ein?
2. Welche Felder und Referenzbilder sind Pflicht, welche sensibel?
3. Welche Ausschluss-/Machbarkeitskriterien sind objektiv, welche rein kreativ?
4. Welche Projektarten, Körperstellen oder Stile werden nicht angeboten?
5. Wie werden Dauer, Preis und Zahl der Sitzungen geschätzt?
6. Wie lang bleibt ein angebotener Square-Slot ohne Anzahlung reserviert?
7. Welche Storno-, Deposit- und Umbuchungsregeln gelten?
8. Soll jede nicht ausgewählte Person eine Nachricht erhalten?
9. Gibt es Waitlist/Carry-over oder muss neu eingereicht werden?
10. Welche Square-Berechtigungen und API-Funktionen stehen im konkreten Tarif zur Verfügung?

## Chunk: C-06_automation_patterns – Mögliche Automationsmuster zu Tattoo-Artist mit periodisch geöffneten Büchern

```yaml
chunk_id: C-06_automation_patterns
document_id: ten_cases_01
case_id: C-06
chunk_type: automation_pattern
pattern_id: P-01
pattern_ids: ["P-01", "P-03"]
process_tags: ["booking_intake", "creative_selection", "deposit_booking"]
pain_tags: ["submission_burst", "subjective_selection", "channel_break"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

### A. Intake-Qualität und kontrollierte Öffnungs-/Schließlogik

- **Problem:** viele Anfragen in kurzer Zeit; fehlende Daten verursachen Rückfragen.
- **Idee:** zeitgesteuertes Formular validiert Pflichtfelder/Referenzen, bestätigt Eingang und schließt exakt nach Regel.
- **Eingaben:** Öffnungszeit, Pflichtfelder, Dateiregeln, Einwilligung.
- **Ausgabe:** vollständiger Datensatz, Missing-Info-Queue, Empfangsbestätigung.
- **Tools:** Websiteformular/Webhook, Datenspeicher, E-Mail.
- **Freigabe:** Änderungen am Formular und Sonderanfragen.
- **Nutzen:** reviewfähigere Einreichungen.
- **Aufwand:** niedrig bis mittel.
- **Risiken:** Bilder/gesundheitsbezogene Angaben; Spam; Zeitzone.
- **Passung:** 24-Stunden-Fenster ist belegt.

### B. Explainable Review-Board statt Auto-Auswahl

- **Problem:** Artist muss zahlreiche Projekte nach mehreren Kriterien sichten.
- **Idee:** Board gruppiert nach Größe, Stil, Budget, Rückfragebedarf und möglicher Kalenderlänge; KI fasst Ideen zusammen, entscheidet aber nicht.
- **Eingaben:** Intake, artist-definierte Regeln, Kalenderkapazität.
- **Ausgabe:** sortierbare Karten mit fehlenden Angaben und nachvollziehbaren Hinweisen.
- **Tools:** Datenbank/Board, optional LLM für Zusammenfassung.
- **Freigabe:** jede Auswahl/Ablehnung ausschließlich durch den Artist.
- **Nutzen:** schnelleres Review ohne Verlust kreativer Autonomie.
- **Aufwand:** mittel.
- **Risiken:** Bias, unangemessene Bildanalyse, falsche Machbarkeit.
- **Passung:** kreative Priorisierung ist der Kernprozess.

### C. Auswahl-zu-Square-Übergabe und Runde schließen

- **Problem:** Kalenderlink, Deposit-Status und Vollmeldung sind mehrere manuelle Schritte.
- **Idee:** nach Freigabe personalisierten Buchungslink senden, Deposit/Booking-Status überwachen, Erinnerungs-/Ablaufregel anwenden und bei voller Kapazität Statusnachrichten erzeugen.
- **Eingaben:** Auswahl, zulässige Services/Slots, Deposit-Regel, Kontaktdaten.
- **Ausgabe:** bestätigter Termin oder zurückgegebener Slot; Audit-Log.
- **Tools:** Square Bookings/Payments je Berechtigung, E-Mail/Mailingliste.
- **Freigabe:** Projektannahme, Sondertermine, Rückerstattung.
- **Nutzen:** weniger Pingpong, bessere Slot-Auslastung.
- **Aufwand:** mittel.
- **Risiken:** API-/Tarifgrenzen, doppelte Buchung, falsche Deposit-Kommunikation.
- **Passung:** Square wird bereits genutzt.

## Chunk: C-06_guardrails – Grenzen und Freigaben zu Tattoo-Artist mit periodisch geöffneten Büchern

```yaml
chunk_id: C-06_guardrails
document_id: ten_cases_01
case_id: C-06
chunk_type: automation_guardrail
pattern_id: P-01
pattern_ids: ["P-01", "P-03"]
process_tags: ["booking_intake", "creative_selection", "deposit_booking"]
pain_tags: ["submission_burst", "subjective_selection", "channel_break"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Die kreative Projektauswahl darf nicht automatisiert werden. Die KI darf Einreichungen strukturieren, aber keine Kundenzusage oder Ablehnung eigenständig senden.

## Chunk: C-07_case_evidence – Solo-Verwaltung von 47 Wohneinheiten

```yaml
chunk_id: C-07_case_evidence
document_id: ten_cases_01
case_id: C-07
chunk_type: case_evidence
pattern_id: P-01
pattern_ids: ["P-01", "P-05"]
process_tags: ["maintenance_intake", "inspection_reporting", "asset_planning"]
pain_tags: ["emergency_risk", "manual_documentation", "asset_data_gap"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/PropertyManagement/comments/1rz0zjx/managing_47_units_solo_and_these_are_the_systems/
language: de
```

### Quellenbasis

Primärquelle ist der öffentliche, inzwischen unter gelöschtem Nutzernamen stehende Erstbericht [„Managing 47 units solo and these are the systems that keep me from drowning“](https://www.reddit.com/r/PropertyManagement/comments/1rz0zjx/managing_47_units_solo_and_these_are_the_systems/). Der Inhalt ist weiterhin öffentlich, aber nicht unabhängig verifiziert. Kommentare anderer Verwalter werden nur als Branchenabgleich, nicht als Fakten über diesen Bestand behandelt.

### Quellenbasierte Aussagen zum Unternehmen und Ist-Prozess

**[Quelle]** AppFolio dient für Mieterkommunikation, Mieteinzug, Wartungsanfragen und Buchhaltung. Mieter reichen Reparaturmeldungen mit Fotos im Portal ein; der Inhaber weist einen passenden Auftragnehmer zu, die Kommunikation bleibt dokumentiert. Investitionsgüter wie Dach, HVAC und Warmwasserbereiter werden in Google Sheets mit Einbau- und erwartetem Austauschzeitpunkt verfolgt. Bei Inspektionen und Wohnungswechseln diktiert der Inhaber Beobachtungen in Willow Voice; das Transkript wird Inspektionsbericht und Arbeitsauftrag. Für Mietrechtsfragen nutzt er Perplexity als Ausgangspunkt und prüft Hochrisikofragen mit einem Anwalt.

## Chunk: C-07_interview_questions – Diagnosefragen zu Solo-Verwaltung von 47 Wohneinheiten

```yaml
chunk_id: C-07_interview_questions
document_id: ten_cases_01
case_id: C-07
chunk_type: interview_question_set
pattern_id: P-01
pattern_ids: ["P-01", "P-05"]
process_tags: ["maintenance_intake", "inspection_reporting", "asset_planning"]
pain_tags: ["emergency_risk", "manual_documentation", "asset_data_gap"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

1. Welche Reparaturen gelten nach Ort/Jahreszeit als Notfall und welche Reaktionsfristen gelten?
2. Welche Mieter-/Zugangsinformationen dürfen an welchen Auftragnehmer gehen?
3. Nach welchem Trade, Gebiet, Preis und SLA wird zugewiesen?
4. Wer darf Kosten oberhalb welcher Schwelle freigeben?
5. Welcher Nachweis schließt einen Auftrag: Foto, Mieterbestätigung, Rechnung, Inspektion?
6. Wie werden Inspektionsfotos mit Diktatstellen verknüpft?
7. Wer entscheidet über Mieterschaden, Kaution und rechtliche Mitteilung?
8. Welche AppFolio-Export-/API-/Webhook-Rechte bestehen?
9. Wie werden Capex-Schätzungen und tatsächliche Kosten abgeglichen?
10. Welche Daten dürfen ein Sprach- oder KI-System verarbeiten und wie lange gespeichert werden?

## Chunk: C-07_automation_patterns – Mögliche Automationsmuster zu Solo-Verwaltung von 47 Wohneinheiten

```yaml
chunk_id: C-07_automation_patterns
document_id: ten_cases_01
case_id: C-07
chunk_type: automation_pattern
pattern_id: P-01
pattern_ids: ["P-01", "P-05"]
process_tags: ["maintenance_intake", "inspection_reporting", "asset_planning"]
pain_tags: ["emergency_risk", "manual_documentation", "asset_data_gap"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

### A. Wartungstriage mit Notfall-Gate

- **Problem:** Meldungen benötigen rasche, konsistente Einordnung und Rückfragen.
- **Idee:** Ticket/Fotos auf fehlende Pflichtdaten prüfen, regelbasiert vorsortieren und nur reguläre Fälle zur Zuweisung vorschlagen.
- **Eingaben:** Einheit, Problemart, Text/Fotos, Zeit, Notfallregeln, Contractor-Matrix.
- **Ausgabe:** Dringlichkeitsvorschlag, Rückfrage oder Zuweisungsvorschlag.
- **Tools:** AppFolio-Schnittstelle/Export, n8n, gesicherte Bild-/Textverarbeitung.
- **Freigabe:** Notfälle, unklare Fälle und kostenrelevante Zuweisungen.
- **Nutzen:** schnellere Reaktion und weniger Gedächtnisabhängigkeit.
- **Aufwand:** mittel bis hoch.
- **Risiken:** falsch negativer Notfall, Datenschutz, API-Grenzen.
- **Passung:** Portalworkflow und Solobetrieb sind belegt.

### B. Diktat-zu-Inspektionsbericht mit Review

- **Problem:** Befunde müssen konsistent zu Einheit, Raum und Aufgabe werden.
- **Idee:** Transkript in Berichtsschema strukturieren, Unsicherheiten markieren und freigegebene Befunde in Work Orders überführen.
- **Eingaben:** Diktat, Einheit, Rundgangsvorlage, Fotos.
- **Ausgabe:** Berichtsentwurf, Befundliste, Wartungsaufgaben.
- **Tools:** Willow-Export, DMS, AppFolio je Schnittstelle.
- **Freigabe:** jeder Bericht; besonders Schaden-/Kautionszuordnung.
- **Nutzen:** der vorhandene Workaround wird belastbarer.
- **Aufwand:** mittel.
- **Risiken:** Transkriptionsfehler und rechtlich problematische Schlussfolgerungen.
- **Passung:** Voice-to-report wird bereits praktiziert.

### C. Capex-Frühwarnung mit Ist-Kosten-Rückkopplung

- **Problem:** Sheets plant Lebenszyklen, reagiert aber nicht automatisch auf Befunde und tatsächliche Reparaturen.
- **Idee:** Inspektions-/Wartungsereignisse aktualisieren Asset-Zustand; bevorstehende Ersatzjahre und Reservelücken werden angezeigt.
- **Eingaben:** Assetregister, Lebensdauer, Befunde, Kosten, Reserveplan.
- **Ausgabe:** 12/24/60-Monats-Vorschau, Prüfliste, Plan-Ist-Abweichung.
- **Tools:** Google Sheets/API, Wartungsexport, Dashboard.
- **Freigabe:** jede Budget- oder Austauschentscheidung.
- **Nutzen:** verbindet Tagesereignisse mit langfristiger Liquidität.
- **Aufwand:** mittel.
- **Risiken:** Lebensdauer ist Schätzung; falsche Kostendaten.
- **Passung:** genau diese Assetdaten treiben laut Quelle die Reserveberechnung.

## Chunk: C-07_guardrails – Grenzen und Freigaben zu Solo-Verwaltung von 47 Wohneinheiten

```yaml
chunk_id: C-07_guardrails
document_id: ten_cases_01
case_id: C-07
chunk_type: automation_guardrail
pattern_id: P-01
pattern_ids: ["P-01", "P-05"]
process_tags: ["maintenance_intake", "inspection_reporting", "asset_planning"]
pain_tags: ["emergency_risk", "manual_documentation", "asset_data_gap"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Notfälle müssen über feste Regeln eskaliert werden; KI-Triage ersetzt keine Sicherheitsbewertung. Berichte und Investitionsentscheidungen brauchen Freigabe.

## Chunk: C-08_case_evidence – Ein-Personen-Kanzlei mit hohem Telefonaufwand

```yaml
chunk_id: C-08_case_evidence
document_id: ten_cases_01
case_id: C-08
chunk_type: case_evidence
pattern_id: P-01
pattern_ids: ["P-01", "P-05"]
process_tags: ["legal_intake", "appointment_scheduling", "status_response"]
pain_tags: ["phone_interruptions", "conflict_risk", "confidentiality"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: legal_and_personal_data
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/smallbusiness/comments/103frfv/virtual_receptionists/
language: de
```

### Quellenbasis

Primärquelle ist die konkrete Wortmeldung eines Kanzleiinhabers im Thread [„Virtual Receptionists?“](https://www.reddit.com/r/smallbusiness/comments/103frfv/virtual_receptionists/). Sie ist kürzer als die anderen Quellen, benennt aber drei präzise Arbeitsziele. Für den Risikorahmen dient die [ABA Model Rule 1.6](https://www.americanbar.org/groups/professional_responsibility/publications/model_rules_of_professional_conduct/rule_1_6_confidentiality_of_information/), nach der Rechtsanwälte angemessene Anstrengungen gegen unbefugte Offenlegung oder Zugriff auf Mandatsinformationen unternehmen müssen. Lokale Berufsregeln sind **unbekannt** und gehen vor.

### Quellenbasierte Aussagen zum Unternehmen und Ist-Prozess

**[Quelle]** Potenzielle Mandanten sollen durch ein Intake-Formular geführt und anschließend zu einem Beratungsgespräch terminiert werden. Bestandsmandanten rufen für Claim-Updates an; gewünscht ist, dass der Inhalt als E-Mail diktiert und an den Anwalt zur Bearbeitung übergeben wird. Telefonate verbrauchen viel Zeit, während der Anwalt E-Mails/Formulare für Tracking bevorzugt.

Terminierung nach Intake ist **[Quelle]**; Kalender, Zahlung und Erinnerungsregeln sind unbekannt.

## Chunk: C-08_interview_questions – Diagnosefragen zu Ein-Personen-Kanzlei mit hohem Telefonaufwand

```yaml
chunk_id: C-08_interview_questions
document_id: ten_cases_01
case_id: C-08
chunk_type: interview_question_set
pattern_id: P-01
pattern_ids: ["P-01", "P-05"]
process_tags: ["legal_intake", "appointment_scheduling", "status_response"]
pain_tags: ["phone_interruptions", "conflict_risk", "confidentiality"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: legal_and_personal_data
evidence_scope: expert_derived_from_case
language: de
```

1. Welche Jurisdiktion und Berufs-/Datenschutzregeln gelten?
2. Welche Rechtsgebiete, Falltypen und Ausschlusskriterien bestehen?
3. Welche minimale Information darf vor Konfliktprüfung aufgenommen werden?
4. Welche Namen/Parteien müssen für Konfliktprüfung erfasst werden?
5. Welche Ereignisse sind fristkritisch oder echte Notfälle?
6. Wer darf ein Mandat annehmen/ablehnen und welche Sprache darf das System verwenden?
7. Wie wird Identität bei Bestandsmandanten verifiziert?
8. Wo liegt der aktuelle Claim-/Fallstatus und ist eine sichere Schnittstelle vorhanden?
9. Welche Statusinformationen sind rein administrativ, welche benötigen juristische Bewertung?
10. Welche Aufzeichnung-/Transkriptions- und Einwilligungsregeln gelten für Telefonate?

## Chunk: C-08_automation_patterns – Mögliche Automationsmuster zu Ein-Personen-Kanzlei mit hohem Telefonaufwand

```yaml
chunk_id: C-08_automation_patterns
document_id: ten_cases_01
case_id: C-08
chunk_type: automation_pattern
pattern_id: P-01
pattern_ids: ["P-01", "P-05"]
process_tags: ["legal_intake", "appointment_scheduling", "status_response"]
pain_tags: ["phone_interruptions", "conflict_risk", "confidentiality"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: legal_and_personal_data
evidence_scope: expert_derived_from_case
language: de
```

### A. Telefon-/Web-Intake mit Frist- und Konfliktgate

- **Problem:** unstrukturierte Erstgespräche unterbrechen und sind schlecht trackbar.
- **Idee:** begrenzter Intake erfasst sichere Pflichtdaten, erkennt Fristindikatoren und stoppt vor Mandatszusage; Konfliktprüfung bleibt autorisiert.
- **Eingaben:** Kontaktdaten, Parteien, Sachgebiet, Termine/Fristen, Kurzbeschreibung.
- **Ausgabe:** strukturierter Intake, Alarm oder Review-Aufgabe.
- **Tools:** sichere Telefonie/Form, Kanzleisystem nur bei geprüfter Integration.
- **Freigabe:** Konfliktprüfung und jede Annahme/Ablehnung durch Anwalt.
- **Nutzen:** weniger Unterbrechung, vollständigere Datensätze.
- **Aufwand:** mittel bis hoch.
- **Risiken:** Vertraulichkeit, Rechtsrat, Fristfehler.
- **Passung:** entspricht dem expliziten Intake-Wunsch.

### B. Freigabe-zu-Consult-Orchestrierung

- **Problem:** Terminierung bindet Zeit nach erfolgreichem Intake.
- **Idee:** nur nach Status `consult approved` einen passenden Kalenderlink, Unterlagenliste und Reminder auslösen.
- **Eingaben:** Freigabe, Terminart, Dauer, Zeitzone, Kontakt.
- **Ausgabe:** bestätigter Termin und Vorbereitungscheckliste.
- **Tools:** Kalender/Booking, E-Mail; aktuelle Tools unbekannt.
- **Freigabe:** Sondertermine und kosten-/mandatsrelevante Kommunikation.
- **Nutzen:** kürzere Übergabe ohne versehentliche Mandatsannahme.
- **Aufwand:** niedrig bis mittel.
- **Risiken:** falscher Slot, vertrauliche Kalenderdetails.
- **Passung:** Consult Scheduling ist ausdrücklich gewünscht.

### C. Statusanfrage zu Antwortentwurf

- **Problem:** wiederholte Anrufe müssen in schriftlich prüfbare Aufgaben überführt werden.
- **Idee:** nach Identitätsprüfung Anliegen zusammenfassen, Fall-ID zuordnen und Antwortentwurf nur aus freigegebenem Fallstatus erzeugen.
- **Eingaben:** verifizierte Identität, Fall-ID, Frage, erlaubte Statusfelder.
- **Ausgabe:** Aufgabe/E-Mail-Entwurf mit Quellenverweis auf Akte.
- **Tools:** Telefonie, DMS/Kanzleisoftware, E-Mail-Entwürfe.
- **Freigabe:** jede externe Antwort durch den Anwalt.
- **Nutzen:** weniger Telefonzeit, besserer Audit-Trail.
- **Aufwand:** mittel bis hoch.
- **Risiken:** falscher Mandant, Halluzination, Offenlegung.
- **Passung:** bildet exakt den gewünschten diktierten E-Mail-Übergang ab.

## Chunk: C-08_guardrails – Grenzen und Freigaben zu Ein-Personen-Kanzlei mit hohem Telefonaufwand

```yaml
chunk_id: C-08_guardrails
document_id: ten_cases_01
case_id: C-08
chunk_type: automation_guardrail
pattern_id: P-01
pattern_ids: ["P-01", "P-05"]
process_tags: ["legal_intake", "appointment_scheduling", "status_response"]
pain_tags: ["phone_interruptions", "conflict_risk", "confidentiality"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: legal_and_personal_data
evidence_scope: expert_derived_from_case
language: de
```

Keine Rechtsberatung, Mandatsannahme, Konfliktentscheidung oder verbindliche Statusauskunft ohne anwaltliche Prüfung.

## Chunk: C-09_case_evidence – Unabhängige Kfz-Werkstatt mit sechs Mechanikern

```yaml
chunk_id: C-09_case_evidence
document_id: ten_cases_01
case_id: C-09
chunk_type: case_evidence
pattern_id: P-01
pattern_ids: ["P-01", "P-02"]
process_tags: ["vehicle_intake", "diagnosis_quote", "repair_invoice"]
pain_tags: ["duplicate_entry", "parts_lookup", "approval_mismatch"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/mechanics/comments/1mcnemb/what_shop_software_are_you_guys_using/
language: de
```

### Quellenbasis

Primärquelle ist der Erstbericht [„What shop software are you guys using?“](https://www.reddit.com/r/mechanics/comments/1mcnemb/what_shop_software_are_you_guys_using/): unabhängige Werkstatt, 28 Jahre am Standort, sechs Mechaniker und elf Hebebühnen/Arbeitsplätze. Ein separater Werkstattbericht [„Automotive Shop Management Software“](https://www.reddit.com/r/mechanics/comments/1eyyhye/automotive_shop_management_software/) liefert die detaillierte Medienbruchstrecke RepairLink → Mitchell → AllData/ProDemand. Dieser zweite Bericht ist **kein Fakt über dieselbe Werkstatt**, sondern Prozessabgleich für ein wiederkehrendes Branchenproblem.

### Quellenbasierte Aussagen zum Unternehmen und Ist-Prozess

**[Quelle]** In der Primärwerkstatt müssen Auftragsdaten so erfasst werden, dass Mechaniker Arbeitsblätter erhalten; die Mannschaft ist nach eigener Aussage zu beschäftigt für umfangreiche Pflichtfelder. Im Vergleichsbetrieb werden Teile in RepairLink gefunden, manuell in Mitchell-Angebote übertragen, Arbeitszeiten aus AllData oder ProDemand gesucht und erneut manuell eingegeben. Drei Programme laufen parallel, um Estimate oder Invoice zu erzeugen. CCC One wird als positives Vergleichsmuster genannt: VIN eingeben, Teile-/Arbeitskatalog zuordnen, Positionen auswählen, Sonderfälle ergänzen.

## Chunk: C-09_interview_questions – Diagnosefragen zu Unabhängige Kfz-Werkstatt mit sechs Mechanikern

```yaml
chunk_id: C-09_interview_questions
document_id: ten_cases_01
case_id: C-09
chunk_type: interview_question_set
pattern_id: P-01
pattern_ids: ["P-01", "P-02"]
process_tags: ["vehicle_intake", "diagnosis_quote", "repair_invoice"]
pain_tags: ["duplicate_entry", "parts_lookup", "approval_mismatch"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

1. Wer nimmt Fahrzeuge an, diagnostiziert, kalkuliert und gibt final frei?
2. Welche Mindestfelder braucht der Mechaniker wirklich und welche nur die Verwaltung?
3. Wie wird VIN eingelesen und Fahrzeugvariante verifiziert?
4. Welche Teile-/Labor-Datenbanken sind lizenziert und erlauben API-/Exportnutzung?
5. Welche Lieferanten, Preislisten, Aufschläge und Kernpfandregeln gelten?
6. Wie werden Diagnosezeit und nicht genehmigte Arbeit berechnet?
7. Wie gibt der Kunde Zusatzarbeit frei und wie wird dies beweissicher dokumentiert?
8. Welche Ist-Daten melden Mechaniker zurück?
9. Wie werden Garantie/Comeback und Qualitätsprüfung behandelt?
10. Welche Mitchell1-/ProDemand-Schnittstellen und Vertragsgrenzen bestehen?

## Chunk: C-09_automation_patterns – Mögliche Automationsmuster zu Unabhängige Kfz-Werkstatt mit sechs Mechanikern

```yaml
chunk_id: C-09_automation_patterns
document_id: ten_cases_01
case_id: C-09
chunk_type: automation_pattern
pattern_id: P-01
pattern_ids: ["P-01", "P-02"]
process_tags: ["vehicle_intake", "diagnosis_quote", "repair_invoice"]
pain_tags: ["duplicate_entry", "parts_lookup", "approval_mismatch"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

### A. Rollenbezogener Quick-Intake zum Worksheet

- **Problem:** zu viele Felder verzögern ein einfaches Arbeitsblatt.
- **Idee:** Annahmemaske erfasst zuerst nur sichere Pflichtdaten; fehlende Verwaltungsfelder werden separat nachgefordert.
- **Eingaben:** Kunde, VIN, Kilometer, Symptom, Termin/Priorität.
- **Ausgabe:** Mechaniker-Worksheet plus Missing-Info-Aufgabe.
- **Tools:** Mitchell1 je Schnittstelle, Tablet/Scanner, Webformular.
- **Freigabe:** Serviceberater prüft Fahrzeug und Auftrag.
- **Nutzen:** Mechaniker starten früher, ohne Datenqualität zu opfern.
- **Aufwand:** mittel.
- **Risiken:** notwendiges Pflichtfeld zu spät; Doppelstammsatz.
- **Passung:** Primärquelle beklagt genau die Eingabe bis zum Worksheet.

### B. VIN-basierter Teile-/Labor-Entwurf mit Beleg

- **Problem:** Positionen werden aus mehreren Katalogen abgetippt.
- **Idee:** nach verifizierter VIN lizenzierte Katalogdaten abrufen und als Vorschlag mit Quelle/Version in den Estimate legen.
- **Eingaben:** VIN, Reparaturposition, Lieferant, Laborquelle, Preisregeln.
- **Ausgabe:** Teile-/Laborzeilen mit Herkunft, Verfügbarkeit und Unsicherheiten.
- **Tools:** nur lizenzierte APIs/Exporte von Mitchell/ProDemand/RepairLink o. ä.; konkrete Rechte unbekannt.
- **Freigabe:** Teilepassung, Menge, Zeit, Preis durch Serviceberater.
- **Nutzen:** weniger Tippen und Übertragungsfehler.
- **Aufwand:** hoch.
- **Risiken:** falsche Konfiguration, Lizenzverstoß, veralteter Preis.
- **Passung:** Vergleichsbetrieb beschreibt diese Dreifacharbeit ausdrücklich.

### C. Zusatzarbeits- und Rechnungsabgleich

- **Problem:** ungeplante Befunde können ohne neue Freigabe oder ohne Rechnungsübernahme bleiben.
- **Idee:** Mechaniker meldet Abweichung strukturiert; Workflow stoppt Arbeit, erzeugt Zusatzestimate und vergleicht am Ende Soll/Ist.
- **Eingaben:** Auftrag, Befund/Fotos, neue Teile/Labor, Kundengenehmigung, Ist-Verbrauch.
- **Ausgabe:** Freigabeprotokoll, aktualisierter Auftrag, Rechnungsdifferenzliste.
- **Tools:** Shopsoftware, SMS/E-Mail/Portal nur je bestehendem Kanal.
- **Freigabe:** Kunde für Zusatzarbeit; Serviceberater vor Rechnung.
- **Nutzen:** weniger Umsatzverlust und Streit.
- **Aufwand:** mittel bis hoch.
- **Risiken:** Arbeit ohne Freigabe, falsche Kontaktperson, rechtliche Dokumentation.
- **Passung:** Sonderpositionen und Estimate/Invoice sind im Quellenmuster zentral.

## Chunk: C-09_guardrails – Grenzen und Freigaben zu Unabhängige Kfz-Werkstatt mit sechs Mechanikern

```yaml
chunk_id: C-09_guardrails
document_id: ten_cases_01
case_id: C-09
chunk_type: automation_guardrail
pattern_id: P-01
pattern_ids: ["P-01", "P-02"]
process_tags: ["vehicle_intake", "diagnosis_quote", "repair_invoice"]
pain_tags: ["duplicate_entry", "parts_lookup", "approval_mismatch"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Diagnose, Sicherheitsentscheidung, Teilefreigabe, Zusatzarbeit und Preis bleiben fachlich bzw. menschlich zu bestätigen.

## Chunk: C-10_case_evidence – Teppichreinigungsfabrik mit Abholservice

```yaml
chunk_id: C-10_case_evidence
document_id: ten_cases_01
case_id: C-10
chunk_type: case_evidence
pattern_id: P-02
pattern_ids: ["P-02", "P-05"]
process_tags: ["pickup_intake", "item_tracking", "return_control"]
pain_tags: ["deletion_risk", "lost_item", "weak_audit_trail"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/smallbusiness/comments/1cj8xi0/software_for_carpet_cleaning_factory_ideas/
language: de
```

### Quellenbasis

Primärquelle ist der Erstbericht [„Software for carpet cleaning factory. Ideas?“](https://www.reddit.com/r/smallbusiness/comments/1cj8xi0/software_for_carpet_cleaning_factory_ideas/). Der Eigentümer beschreibt Annahme/Abholung, Kundennummer, Auftragsdaten, aktuelle Tabellen und die Sorge, dass Mitarbeitende Aufträge löschen oder verändern könnten. Vorschläge anderer Nutzer (Barcode, ClickUp, Housecall Pro, Google Forms) werden als Optionen, nicht als vorhandene Systeme behandelt.

### Quellenbasierte Aussagen zum Unternehmen und Ist-Prozess

**[Quelle]** Teppiche kommen per Selbstanlieferung oder Bus in die Fabrik. Bei Abholung soll eine Kunden-ID vergeben und zusammen mit Zahl der Teppiche, Adresse, Fertigtermin und Gesamtpreis erfasst werden. Aktuell arbeitet der Betrieb mit Tabellen. Der Inhaber möchte Bearbeitungs-/Löschrechte einschränken, ausdrücklich um Diebstahl durch Mitarbeiter zu verhindern. Housecall Pro wäre nach seiner Aussage interessant, ist aber in seiner Region nicht verfügbar.

## Chunk: C-10_interview_questions – Diagnosefragen zu Teppichreinigungsfabrik mit Abholservice

```yaml
chunk_id: C-10_interview_questions
document_id: ten_cases_01
case_id: C-10
chunk_type: interview_question_set
pattern_id: P-02
pattern_ids: ["P-02", "P-05"]
process_tags: ["pickup_intake", "item_tracking", "return_control"]
pain_tags: ["deletion_risk", "lost_item", "weak_audit_trail"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

1. Wie viele Aufträge/Teppiche gehen täglich ein und aus?
2. Braucht jeder Teppich eine eigene ID oder genügt eine Auftrags-ID plus laufende Nummer?
3. Welche Merkmale/Fotos dokumentieren Zustand und Identität?
4. Welche Reinigungs-, Trocknungs-, Nacharbeits- und Lagerstatus existieren real?
5. Wer darf anlegen, Status ändern, Preis ändern, stornieren oder löschen?
6. Müssen Änderungen revisionssicher mit Nutzer, Zeit und Grund protokolliert werden?
7. Gibt es WLAN/Mobilfunk an Pickup, Fabrik und Lager; ist Offline-Modus nötig?
8. Wie werden Busroute, Abholfenster und Rücklieferung geplant?
9. Wann und wie wird bezahlt; sind Teilzahlungen/Nachpreise möglich?
10. Welche regional verfügbaren Systeme/APIs, Sprachen, Währungen und Datenschutzregeln gelten?

## Chunk: C-10_automation_patterns – Mögliche Automationsmuster zu Teppichreinigungsfabrik mit Abholservice

```yaml
chunk_id: C-10_automation_patterns
document_id: ten_cases_01
case_id: C-10
chunk_type: automation_pattern
pattern_id: P-02
pattern_ids: ["P-02", "P-05"]
process_tags: ["pickup_intake", "item_tracking", "return_control"]
pain_tags: ["deletion_risk", "lost_item", "weak_audit_trail"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

### A. Mobiler Intake mit Objekt-ID und Übergabebeleg

- **Problem:** Auftragsmenge und physische Teppiche können auseinanderlaufen.
- **Idee:** bei Pickup/Annahme Auftrag anlegen, jeden Teppich mit fortlaufender ID/Barcode und Foto erfassen, Kunde bestätigt digital.
- **Eingaben:** Kunde, Adresse, Teppichzahl/IDs, Fotos, Termin, Preis.
- **Ausgabe:** Etiketten, Übergabebeleg, vollständige Objektliste.
- **Tools:** mobile Web-App/Form, Etikettendrucker, Barcode; konkrete Ist-Systeme unbekannt.
- **Freigabe:** Preis-/Zustandsabweichungen durch autorisierte Person.
- **Nutzen:** klare Chain of Custody ab dem ersten Kontakt.
- **Aufwand:** mittel.
- **Risiken:** Etikett löst sich, Offline-Probleme, Foto-/Datenschutz.
- **Passung:** bildet genau die genannten ID-/Mengen-/Adressfelder ab.

### B. Rollenbasiertes Statusbuch mit unveränderlichem Audit-Log

- **Problem:** Mitarbeitende könnten Aufträge löschen oder manipulieren.
- **Idee:** keine physische Löschung; Statusänderungen nur rollenbasiert, mit Zeit/Nutzer/Grund und Korrekturbuchung.
- **Eingaben:** Scan, Auftrag, Nutzerrolle, neuer Status, Abweichungsgrund.
- **Ausgabe:** aktuelle Position/Status, Historie, Ausnahmealarm.
- **Tools:** kleine Datenbank/PWA; ggf. vorhandene Tabelle nur als Export.
- **Freigabe:** Storno, Preisänderung und Bestandskorrektur durch Inhaber.
- **Nutzen:** Schutz und Nachvollziehbarkeit ohne einen einzigen Dateneingeber.
- **Aufwand:** mittel bis hoch.
- **Risiken:** gemeinsame Logins, Umgehung ohne Scan, unklare Arbeitsrechte.
- **Passung:** löst die ausdrücklich genannte Rechte-/Diebstahlsorge.

### C. Soll-Ist-Ausgangskontrolle und Tourfreigabe

- **Problem:** falsche/unvollständige Teppiche können ausgegeben werden.
- **Idee:** vor Abholung/Lieferung alle IDs scannen; System sperrt bei Differenz und erstellt Busmanifest/Empfangsbeleg.
- **Eingaben:** Auftragssoll, Fertigstatus, Scans, Adresse, Zahlungsstatus.
- **Ausgabe:** Differenzliste oder freigegebenes Manifest.
- **Tools:** Scanner/PWA, optional Routing-/Zahlungssystem nach Klärung.
- **Freigabe:** Differenzen und Ausnahmen durch Inhaber/Schichtleitung.
- **Nutzen:** weniger Verlust, Suchzeit und Falschübergabe.
- **Aufwand:** mittel.
- **Risiken:** falscher Scan, defektes Etikett, Prozess wird umgangen.
- **Passung:** mehrere Teppiche je Auftrag und Buslogistik sind belegt.

## Chunk: C-10_guardrails – Grenzen und Freigaben zu Teppichreinigungsfabrik mit Abholservice

```yaml
chunk_id: C-10_guardrails
document_id: ten_cases_01
case_id: C-10
chunk_type: automation_guardrail
pattern_id: P-02
pattern_ids: ["P-02", "P-05"]
process_tags: ["pickup_intake", "item_tracking", "return_control"]
pain_tags: ["deletion_risk", "lost_item", "weak_audit_trail"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Statusänderungen und Auslieferungen benötigen Rollenrechte und nachvollziehbare Freigaben; ein Modell darf keine Datensätze löschen oder Übergaben bestätigen.
