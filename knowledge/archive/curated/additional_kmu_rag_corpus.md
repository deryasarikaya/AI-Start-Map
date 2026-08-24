# AI Start Map – kuratierter zusätzlicher KMU-RAG-Korpus

Die 14 Quellenfälle wurden in getrennte Evidence-, Frage-, Automations- und Guardrail-Chunks überführt.

**Prompt-Guardrail:** Die gefundenen Fälle dienen nur als Vergleichsmuster. Übernimm keine Mengen, Tools, Abläufe, Risiken oder Geschäftsdaten als Fakten über das aktuell analysierte Unternehmen.

**Retrieval-Regel:** Maximal zwei `case_evidence`-Chunks je `pattern_id`; zusätzlich mindestens ein `diagnostic_pattern`- und ein `automation_guardrail`-Chunk laden.

## Chunk: K-01_case_evidence – Kunden-E-Mails werden manuell in eine Tabelle kopiert

```yaml
chunk_id: K-01_case_evidence
document_id: additional_kmu_01
case_id: K-01
chunk_type: case_evidence
pattern_id: P-01
pattern_ids: ["P-01"]
process_tags: ["email_intake", "case_tracking"]
pain_tags: ["missed_requests", "copy_paste"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/smallbusiness/comments/1ogmune/anyone_else_manually_logging_customer_emails_to_a/
language: de
```

**Betriebsart:** nicht näher spezifiziertes kleines Unternehmen.

**Primärquelle:** [Reddit: „Anyone else manually logging customer emails to a spreadsheet?“](https://www.reddit.com/r/smallbusiness/comments/1ogmune/anyone_else_manually_logging_customer_emails_to_a/)

**Belegter Ist-Prozess:** Wichtige Kunden-E-Mails zu Bestellungen, Anfragen und Angeboten werden aus Gmail per Copy-paste in eine Tabelle übertragen, weil sonst Dinge übersehen wurden.

**Belegter Engpass:** Der Vorgang ist mühsam; der Auslöser ist, dass E-Mails im Postfach verloren gehen bzw. nicht zuverlässig nachverfolgt werden.

## Chunk: K-01_interview_questions – Diagnosefragen zu Kunden-E-Mails werden manuell in eine Tabelle kopiert

```yaml
chunk_id: K-01_interview_questions
document_id: additional_kmu_01
case_id: K-01
chunk_type: interview_question_set
pattern_id: P-01
pattern_ids: ["P-01"]
process_tags: ["email_intake", "case_tracking"]
pain_tags: ["missed_requests", "copy_paste"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Welche E-Mail-Typen sollen erfasst werden? Welche Felder sind pro Vorgang Pflicht? Wann gilt ein Vorgang als erledigt? Gibt es personenbezogene oder vertrauliche Anhänge?

## Chunk: K-01_automation_pattern – Mögliches Automationsmuster zu Kunden-E-Mails werden manuell in eine Tabelle kopiert

```yaml
chunk_id: K-01_automation_pattern
document_id: additional_kmu_01
case_id: K-01
chunk_type: automation_pattern
pattern_id: P-01
pattern_ids: ["P-01"]
process_tags: ["email_intake", "case_tracking"]
pain_tags: ["missed_requests", "copy_paste"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

`Nachricht → Klassifikation → strukturierter Vorgang → Status/Fälligkeit → menschliche Bearbeitung`.

## Chunk: K-01_guardrail – Grenzen zu Kunden-E-Mails werden manuell in eine Tabelle kopiert

```yaml
chunk_id: K-01_guardrail
document_id: additional_kmu_01
case_id: K-01
chunk_type: automation_guardrail
pattern_id: P-01
pattern_ids: ["P-01"]
process_tags: ["email_intake", "case_tracking"]
pain_tags: ["missed_requests", "copy_paste"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Angebotsfreigabe, Preis, verbindliche Kundenzusage.

## Chunk: K-02_case_evidence – Beschaffung aus großer Tabelle und E-Mail-Bestellung

```yaml
chunk_id: K-02_case_evidence
document_id: additional_kmu_01
case_id: K-02
chunk_type: case_evidence
pattern_id: P-07
pattern_ids: ["P-07"]
process_tags: ["procurement", "vendor_order"]
pain_tags: ["manual_lookup", "copy_paste"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/smallbusiness/comments/1kc5ksw/program_for_managing_equipment_and_ordering/
language: de
```

**Betriebsart:** kleiner Betrieb mit Geräten/Materialien und mehreren Lieferanten.

**Primärquelle:** [Reddit: „Program for managing equipment and ordering“](https://www.reddit.com/r/smallbusiness/comments/1kc5ksw/program_for_managing_equipment_and_ordering/)

**Belegter Ist-Prozess:** Geräte- und Preisinformationen liegen in einer Tabelle. Bestellungen erfolgen meist per E-Mail, teils über Webshops. Für jede Bestellung werden Artikelnummern aus der großen Tabelle gesucht, kopiert und je Lieferant in eine E-Mail übertragen.

**Belegter Engpass:** Wiederholtes Suchen, Kopieren und manuelles Formulieren der Bestellungen.

## Chunk: K-02_interview_questions – Diagnosefragen zu Beschaffung aus großer Tabelle und E-Mail-Bestellung

```yaml
chunk_id: K-02_interview_questions
document_id: additional_kmu_01
case_id: K-02
chunk_type: interview_question_set
pattern_id: P-07
pattern_ids: ["P-07"]
process_tags: ["procurement", "vendor_order"]
pain_tags: ["manual_lookup", "copy_paste"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Wer darf bestellen? Gibt es Mindestbestände, Rahmenverträge oder Preisänderungen? Ist ein eindeutiger Artikel- und Lieferantenstamm vorhanden?

## Chunk: K-02_automation_pattern – Mögliches Automationsmuster zu Beschaffung aus großer Tabelle und E-Mail-Bestellung

```yaml
chunk_id: K-02_automation_pattern
document_id: additional_kmu_01
case_id: K-02
chunk_type: automation_pattern
pattern_id: P-07
pattern_ids: ["P-07"]
process_tags: ["procurement", "vendor_order"]
pain_tags: ["manual_lookup", "copy_paste"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

`Bedarf → Artikel-/Lieferantenprüfung → Bestellentwurf → Freigabe → Versand → Bestellstatus`.

## Chunk: K-02_guardrail – Grenzen zu Beschaffung aus großer Tabelle und E-Mail-Bestellung

```yaml
chunk_id: K-02_guardrail
document_id: additional_kmu_01
case_id: K-02
chunk_type: automation_guardrail
pattern_id: P-07
pattern_ids: ["P-07"]
process_tags: ["procurement", "vendor_order"]
pain_tags: ["manual_lookup", "copy_paste"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Bestellung auslösen, Mengen ändern oder Lieferant auswählen ohne Freigaberegel.

## Chunk: K-03_case_evidence – Bäckerei: Bestellung, Abschrift und Produktionsliste

```yaml
chunk_id: K-03_case_evidence
document_id: additional_kmu_01
case_id: K-03
chunk_type: case_evidence
pattern_id: P-02
pattern_ids: ["P-02"]
process_tags: ["order_intake", "production_planning"]
pain_tags: ["duplicate_entry", "capacity_gap"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/smallbusiness/comments/nznglv/looking_for_simple_ordering_takingproduction/
language: de
```

**Betriebsart:** kleine Bäckerei.

**Primärquelle:** [Reddit: „Looking for simple ordering taking/production creation“](https://www.reddit.com/r/smallbusiness/comments/nznglv/looking_for_simple_ordering_takingproduction/)

**Belegter Ist-Prozess:** Bestellungen kommen per E-Mail und Telefon. Sie werden auf ein Auftragsblatt geschrieben, anschließend geprüft, nach Backwaren gruppiert und in eine gedruckte Tabelle übertragen. Diese Tabelle bildet die Grundlage der wöchentlichen Backliste.

**Belegter Engpass:** Mehrfaches manuelles Schreiben derselben Bestellung, bevor daraus eine Produktionsplanung entsteht.

## Chunk: K-03_interview_questions – Diagnosefragen zu Bäckerei: Bestellung, Abschrift und Produktionsliste

```yaml
chunk_id: K-03_interview_questions
document_id: additional_kmu_01
case_id: K-03
chunk_type: interview_question_set
pattern_id: P-02
pattern_ids: ["P-02"]
process_tags: ["order_intake", "production_planning"]
pain_tags: ["duplicate_entry", "capacity_gap"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Welche Varianten, Allergene, Liefertermine und Mengen sind Pflicht? Wie werden Änderungen und Stornierungen behandelt? Welche Kapazitätsgrenzen gelten pro Tag?

## Chunk: K-03_automation_pattern – Mögliches Automationsmuster zu Bäckerei: Bestellung, Abschrift und Produktionsliste

```yaml
chunk_id: K-03_automation_pattern
document_id: additional_kmu_01
case_id: K-03
chunk_type: automation_pattern
pattern_id: P-02
pattern_ids: ["P-02"]
process_tags: ["order_intake", "production_planning"]
pain_tags: ["duplicate_entry", "capacity_gap"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

`Bestellung → strukturierte Positionen → Prüfung von Termin/Kapazität → Aggregation nach Produkt → Produktionsliste`.

## Chunk: K-03_guardrail – Grenzen zu Bäckerei: Bestellung, Abschrift und Produktionsliste

```yaml
chunk_id: K-03_guardrail
document_id: additional_kmu_01
case_id: K-03
chunk_type: automation_guardrail
pattern_id: P-02
pattern_ids: ["P-02"]
process_tags: ["order_intake", "production_planning"]
pain_tags: ["duplicate_entry", "capacity_gap"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Machbarkeitszusage bei Sonderanfertigungen oder Überkapazität.

## Chunk: K-04_case_evidence – Instagram-Kuchenverkauf: DMs, Notizen, Zahlungshistorie und WhatsApp-Merkliste

```yaml
chunk_id: K-04_case_evidence
document_id: additional_kmu_01
case_id: K-04
chunk_type: case_evidence
pattern_id: P-01
pattern_ids: ["P-01", "P-02", "P-04"]
process_tags: ["social_order", "payment_matching", "delivery"]
pain_tags: ["fragmented_data", "missing_status"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/smallbusiness/comments/1tjqb5n/my_mother_sells_homemade_cakes_on_instagram_and/
language: de
```

**Betriebsart:** hausbasierte Kleinstbäckerei.

**Primärquelle:** [Reddit: „My mother sells homemade cakes on Instagram and her…“](https://www.reddit.com/r/smallbusiness/comments/1tjqb5n/my_mother_sells_homemade_cakes_on_instagram_and/)

**Belegter Ist-Prozess:** Bestellungen kommen über Instagram-DMs und Story-Antworten. Lieferadressen liegen in einer Notiz-App; der Zahlungseingang wird am Tagesende in der Zahlungshistorie geprüft; offene Bestellungen stehen in einer WhatsApp-Nachricht an sich selbst.

**Belegter Engpass:** Mit steigendem Bestellvolumen „fällt das System auseinander“; Auftrags-, Adress-, Zahlungs- und Statusinformationen sind getrennt.

## Chunk: K-04_interview_questions – Diagnosefragen zu Instagram-Kuchenverkauf: DMs, Notizen, Zahlungshistorie und WhatsApp-Merkliste

```yaml
chunk_id: K-04_interview_questions
document_id: additional_kmu_01
case_id: K-04
chunk_type: interview_question_set
pattern_id: P-01
pattern_ids: ["P-01", "P-02", "P-04"]
process_tags: ["social_order", "payment_matching", "delivery"]
pain_tags: ["fragmented_data", "missing_status"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Gibt es feste Produktkataloge oder individuelle Torten? Was ist der Zahlungsnachweis? Wie werden Allergene, Abholung/Lieferung und Datenschutz der Adressen gehandhabt?

## Chunk: K-04_automation_pattern – Mögliches Automationsmuster zu Instagram-Kuchenverkauf: DMs, Notizen, Zahlungshistorie und WhatsApp-Merkliste

```yaml
chunk_id: K-04_automation_pattern
document_id: additional_kmu_01
case_id: K-04
chunk_type: automation_pattern
pattern_id: P-01
pattern_ids: ["P-01", "P-02", "P-04"]
process_tags: ["social_order", "payment_matching", "delivery"]
pain_tags: ["fragmented_data", "missing_status"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

`DM → Auftrag mit Pflichtfeldern → Zahlungsabgleich → Produktions-/Lieferstatus → Kundeninformation`.

## Chunk: K-04_guardrail – Grenzen zu Instagram-Kuchenverkauf: DMs, Notizen, Zahlungshistorie und WhatsApp-Merkliste

```yaml
chunk_id: K-04_guardrail
document_id: additional_kmu_01
case_id: K-04
chunk_type: automation_guardrail
pattern_id: P-01
pattern_ids: ["P-01", "P-02", "P-04"]
process_tags: ["social_order", "payment_matching", "delivery"]
pain_tags: ["fragmented_data", "missing_status"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Annahme eines Auftrags ohne Kapazitäts- und Preiskontrolle.

## Chunk: K-05_case_evidence – Instagram-Direktnachrichten als Shop- und Auftragskanal

```yaml
chunk_id: K-05_case_evidence
document_id: additional_kmu_01
case_id: K-05
chunk_type: case_evidence
pattern_id: P-01
pattern_ids: ["P-01", "P-02"]
process_tags: ["social_order", "status_tracking"]
pain_tags: ["fragmented_data", "tool_cost"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/smallbusiness/comments/1oz0v1u/anyone_else_overwhelmed_by_tracking_client_orders/
language: de
```

**Betriebsart:** kleines DM-basiertes Produktgeschäft.

**Primärquelle:** [Reddit: „Anyone else overwhelmed by tracking client orders through DMs?“](https://www.reddit.com/r/smallbusiness/comments/1oz0v1u/anyone_else_overwhelmed_by_tracking_client_orders/)

**Belegter Ist-Prozess:** Aufträge kommen hauptsächlich über Instagram-DMs. Bestellungen, Zahlungen, Terminierung und Follow-ups werden über DMs, Notizen und verstreute Tabellen nachgehalten.

**Belegter Engpass:** Fehlender Gesamtüberblick; gängige Shop-Systeme werden als zu komplex bzw. zu teuer für den kleinen, DM-basierten Betrieb wahrgenommen.

## Chunk: K-05_interview_questions – Diagnosefragen zu Instagram-Direktnachrichten als Shop- und Auftragskanal

```yaml
chunk_id: K-05_interview_questions
document_id: additional_kmu_01
case_id: K-05
chunk_type: interview_question_set
pattern_id: P-01
pattern_ids: ["P-01", "P-02"]
process_tags: ["social_order", "status_tracking"]
pain_tags: ["fragmented_data", "tool_cost"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Wie viele Aufträge pro Woche? Welche DMs sind nur Fragen, welche echte Aufträge? Welche Informationen fehlen typischerweise? Gibt es ein erlaubtes/technisch zugängliches Eingangssystem?

## Chunk: K-05_automation_pattern – Mögliches Automationsmuster zu Instagram-Direktnachrichten als Shop- und Auftragskanal

```yaml
chunk_id: K-05_automation_pattern
document_id: additional_kmu_01
case_id: K-05
chunk_type: automation_pattern
pattern_id: P-01
pattern_ids: ["P-01", "P-02"]
process_tags: ["social_order", "status_tracking"]
pain_tags: ["fragmented_data", "tool_cost"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

`unstrukturierte Anfrage → Auftragssatz → Statusboard → Zahlung/Erfüllung → Follow-up`.

## Chunk: K-05_guardrail – Grenzen zu Instagram-Direktnachrichten als Shop- und Auftragskanal

```yaml
chunk_id: K-05_guardrail
document_id: additional_kmu_01
case_id: K-05
chunk_type: automation_guardrail
pattern_id: P-01
pattern_ids: ["P-01", "P-02"]
process_tags: ["social_order", "status_tracking"]
pain_tags: ["fragmented_data", "tool_cost"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Kundenkommunikation mit verbindlichen Liefer- oder Verfügbarkeitsaussagen.

## Chunk: K-06_case_evidence – Mobiler Dienstleister: Terminplanung scheitert an realen Fahrzeiten

```yaml
chunk_id: K-06_case_evidence
document_id: additional_kmu_01
case_id: K-06
chunk_type: case_evidence
pattern_id: P-03
pattern_ids: ["P-03"]
process_tags: ["field_service", "scheduling", "routing"]
pain_tags: ["travel_time", "manual_coordination"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/smallbusiness/comments/1m0u4qc/for_service_pros_who_travel_to_clients_homes_what/
language: de
```

**Betriebsart:** Dienstleister mit Einsätzen bei Kundinnen und Kunden vor Ort.

**Primärquelle:** [Reddit: „For service pros who travel to clients’ homes, what scheduling software do you use?“](https://www.reddit.com/r/smallbusiness/comments/1m0u4qc/for_service_pros_who_travel_to_clients_homes_what/)

**Belegter Ist-Prozess:** Der Betreiber plant Termine und kommuniziert erwartete Ankunftszeiten. Eine getestete Terminsoftware mit Pufferzeiten berücksichtigte keine tatsächlichen, standortabhängigen Fahrzeiten.

**Belegter Engpass:** Hoher Koordinationsaufwand und ein Kalender, der die geografische Realität nicht abbildet.

## Chunk: K-06_interview_questions – Diagnosefragen zu Mobiler Dienstleister: Terminplanung scheitert an realen Fahrzeiten

```yaml
chunk_id: K-06_interview_questions
document_id: additional_kmu_01
case_id: K-06
chunk_type: interview_question_set
pattern_id: P-03
pattern_ids: ["P-03"]
process_tags: ["field_service", "scheduling", "routing"]
pain_tags: ["travel_time", "manual_coordination"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Einzelperson oder Team? Servicegebiet? feste Zeitfenster? benötigte Skills/Materialien? Wie teuer sind Verspätungen oder Umplanungen?

## Chunk: K-06_automation_pattern – Mögliches Automationsmuster zu Mobiler Dienstleister: Terminplanung scheitert an realen Fahrzeiten

```yaml
chunk_id: K-06_automation_pattern
document_id: additional_kmu_01
case_id: K-06
chunk_type: automation_pattern
pattern_id: P-03
pattern_ids: ["P-03"]
process_tags: ["field_service", "scheduling", "routing"]
pain_tags: ["travel_time", "manual_coordination"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

`Anfrage mit Ort → Dauer-/Fahrzeit-Schätzung → Vorschlag → menschliche Prüfung → Bestätigung`.

## Chunk: K-06_guardrail – Grenzen zu Mobiler Dienstleister: Terminplanung scheitert an realen Fahrzeiten

```yaml
chunk_id: K-06_guardrail
document_id: additional_kmu_01
case_id: K-06
chunk_type: automation_guardrail
pattern_id: P-03
pattern_ids: ["P-03"]
process_tags: ["field_service", "scheduling", "routing"]
pain_tags: ["travel_time", "manual_coordination"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Routen- oder Terminoptimierung bei unvollständigen Orts-, Prioritäts- oder Qualifikationsdaten.

## Chunk: K-07_case_evidence – Wiederkehrende Rechnungen eines Reinigungs-Solo-Betriebs

```yaml
chunk_id: K-07_case_evidence
document_id: additional_kmu_01
case_id: K-07
chunk_type: case_evidence
pattern_id: P-04
pattern_ids: ["P-04"]
process_tags: ["recurring_invoice", "payment_followup"]
pain_tags: ["late_payment", "manual_reminder"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/smallbusiness/comments/1b3j8r6/can_someone_help_me_word_a_polite_request_to/
language: de
```

**Betriebsart:** selbstständige Reinigungskraft mit wöchentlichen bzw. zweiwöchentlichen Kundenterminen.

**Primärquelle:** [Reddit: „Can someone help me word a polite request to clients, to pay their invoice?“](https://www.reddit.com/r/smallbusiness/comments/1b3j8r6/can_someone_help_me_word_a_polite_request_to/)

**Belegter Ist-Prozess:** Nach der letzten Reinigung eines Monats wird eine Rechnung versendet. Die Zahlung wird bis Monatsende erbeten. Seit sechs Monaten müssen einzelne Kunden jeden Monat manuell zur Zahlung erinnert werden.

**Belegter Engpass:** Wiederholte, unangenehme manuelle Zahlungserinnerung bei einem standardisierten, wiederkehrenden Prozess.

## Chunk: K-07_interview_questions – Diagnosefragen zu Wiederkehrende Rechnungen eines Reinigungs-Solo-Betriebs

```yaml
chunk_id: K-07_interview_questions
document_id: additional_kmu_01
case_id: K-07
chunk_type: interview_question_set
pattern_id: P-04
pattern_ids: ["P-04"]
process_tags: ["recurring_invoice", "payment_followup"]
pain_tags: ["late_payment", "manual_reminder"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Wie wird Zahlungseingang erkannt? Gibt es Teilzahlungen, Streitfälle oder unterschiedliche Zahlungsziele? Welcher Kommunikationskanal ist vereinbart?

## Chunk: K-07_automation_pattern – Mögliches Automationsmuster zu Wiederkehrende Rechnungen eines Reinigungs-Solo-Betriebs

```yaml
chunk_id: K-07_automation_pattern
document_id: additional_kmu_01
case_id: K-07
chunk_type: automation_pattern
pattern_id: P-04
pattern_ids: ["P-04"]
process_tags: ["recurring_invoice", "payment_followup"]
pain_tags: ["late_payment", "manual_reminder"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

`Leistung abgeschlossen → Rechnung → Fälligkeit → Zahlungseingang → gestufter Erinnerungsentwurf → Eskalation`.

## Chunk: K-07_guardrail – Grenzen zu Wiederkehrende Rechnungen eines Reinigungs-Solo-Betriebs

```yaml
chunk_id: K-07_guardrail
document_id: additional_kmu_01
case_id: K-07
chunk_type: automation_guardrail
pattern_id: P-04
pattern_ids: ["P-04"]
process_tags: ["recurring_invoice", "payment_followup"]
pain_tags: ["late_payment", "manual_reminder"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Mahnung, Leistungssperre oder rechtliche Schritte ohne eine vom Betrieb festgelegte Regel und Freigabe.

## Chunk: K-08_case_evidence – Rechnungsnachverfolgung beansprucht messbar Zeit

```yaml
chunk_id: K-08_case_evidence
document_id: additional_kmu_01
case_id: K-08
chunk_type: case_evidence
pattern_id: P-04
pattern_ids: ["P-04"]
process_tags: ["open_invoices", "payment_followup"]
pain_tags: ["forgotten_followup", "time_loss"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/smallbusiness/comments/1tuyjyn/what_is_your_process_for_following_up_on_unpaid/
language: de
```

**Betriebsart:** kleiner Dienstleistungsbetrieb.

**Primärquelle:** [Reddit: „What is your process for following up on unpaid invoices?“](https://www.reddit.com/r/smallbusiness/comments/1tuyjyn/what_is_your_process_for_following_up_on_unpaid/)

**Belegter Ist-Prozess:** Bei ungefähr 15–20 aktiven Rechnungen werden Zahlungserinnerungen manuell per E-Mail gesendet; der Unternehmer berichtet, dies koste schätzungsweise zwei bis drei Stunden pro Woche und werde vergessen.

**Belegter Engpass:** Fälligkeiten und Follow-ups sind nicht verlässlich in einem Ablauf verankert.

## Chunk: K-08_interview_questions – Diagnosefragen zu Rechnungsnachverfolgung beansprucht messbar Zeit

```yaml
chunk_id: K-08_interview_questions
document_id: additional_kmu_01
case_id: K-08
chunk_type: interview_question_set
pattern_id: P-04
pattern_ids: ["P-04"]
process_tags: ["open_invoices", "payment_followup"]
pain_tags: ["forgotten_followup", "time_loss"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Welche Datenquelle ist führend: Rechnungssystem oder Bank? Wie wird eine Zahlung eindeutig einer Rechnung zugeordnet? Welche Erinnerungsstufen sind zulässig?

## Chunk: K-08_automation_pattern – Mögliches Automationsmuster zu Rechnungsnachverfolgung beansprucht messbar Zeit

```yaml
chunk_id: K-08_automation_pattern
document_id: additional_kmu_01
case_id: K-08
chunk_type: automation_pattern
pattern_id: P-04
pattern_ids: ["P-04"]
process_tags: ["open_invoices", "payment_followup"]
pain_tags: ["forgotten_followup", "time_loss"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

wie K-07, zusätzlich `Offene-Posten-Liste → Priorisierung → Entwurf → menschliche Freigabe/Versand`.

## Chunk: K-08_guardrail – Grenzen zu Rechnungsnachverfolgung beansprucht messbar Zeit

```yaml
chunk_id: K-08_guardrail
document_id: additional_kmu_01
case_id: K-08
chunk_type: automation_guardrail
pattern_id: P-04
pattern_ids: ["P-04"]
process_tags: ["open_invoices", "payment_followup"]
pain_tags: ["forgotten_followup", "time_loss"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Kontodaten/Banktransaktionen ohne sichere Integration und Kontrolllogik abgleichen.

## Chunk: K-09_case_evidence – Nagelstudio: No-Shows sind messbar, Slots sind nicht gleich Personen

```yaml
chunk_id: K-09_case_evidence
document_id: additional_kmu_01
case_id: K-09
chunk_type: case_evidence
pattern_id: P-03
pattern_ids: ["P-03"]
process_tags: ["appointment", "no_show", "resource_booking"]
pain_tags: ["metric_mismatch", "lost_capacity"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/smallbusiness/comments/1tfgi54/how_do_you_deal_with_noshows/
language: de
```

**Betriebsart:** Nagelstudio mit Terminbuchungen.

**Primärquelle:** [Reddit: „How Do You Deal with No-Shows?“](https://www.reddit.com/r/smallbusiness/comments/1tfgi54/how_do_you_deal_with_noshows/)

**Belegter Ist-Prozess:** Das Studio nutzt ein CRM und berichtet für einen Monat 23 No-Shows bei 1.388 Buchungen (1,6 % nach CRM-Zählung). Die Inhaber weisen darauf hin, dass ein CRM-Konto teilweise zwei Personen für zwei Leistungen bucht; dadurch unterschätzt die kontobasierte Kennzahl die blockierten Slots.

**Belegter Engpass:** Die operative Auswirkung und die Kennzahl sind nicht identisch, wenn ein Buchungskonto mehrere Ressourcen/Personen bindet.

## Chunk: K-09_interview_questions – Diagnosefragen zu Nagelstudio: No-Shows sind messbar, Slots sind nicht gleich Personen

```yaml
chunk_id: K-09_interview_questions
document_id: additional_kmu_01
case_id: K-09
chunk_type: interview_question_set
pattern_id: P-03
pattern_ids: ["P-03"]
process_tags: ["appointment", "no_show", "resource_booking"]
pain_tags: ["metric_mismatch", "lost_capacity"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Wird pro Konto, Termin, Leistung oder Ressource gemessen? Welche Slots können kurzfristig wieder vergeben werden? Welche No-show-Policy besteht?

## Chunk: K-09_automation_pattern – Mögliches Automationsmuster zu Nagelstudio: No-Shows sind messbar, Slots sind nicht gleich Personen

```yaml
chunk_id: K-09_automation_pattern
document_id: additional_kmu_01
case_id: K-09
chunk_type: automation_pattern
pattern_id: P-03
pattern_ids: ["P-03"]
process_tags: ["appointment", "no_show", "resource_booking"]
pain_tags: ["metric_mismatch", "lost_capacity"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

`Buchung → Ressourcen-/Slotanzahl → Bestätigung/Erinnerung → Status → No-show-Auswertung`.

## Chunk: K-09_guardrail – Grenzen zu Nagelstudio: No-Shows sind messbar, Slots sind nicht gleich Personen

```yaml
chunk_id: K-09_guardrail
document_id: additional_kmu_01
case_id: K-09
chunk_type: automation_guardrail
pattern_id: P-03
pattern_ids: ["P-03"]
process_tags: ["appointment", "no_show", "resource_booking"]
pain_tags: ["metric_mismatch", "lost_capacity"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Überbuchung oder Gebühren ohne transparente Geschäftsregeln und Kundeneinwilligung.

## Chunk: K-10_case_evidence – Saisonbetrieb: Arbeitszeiterfassung für 1–4 Teilzeitkräfte

```yaml
chunk_id: K-10_case_evidence
document_id: additional_kmu_01
case_id: K-10
chunk_type: case_evidence
pattern_id: P-05
pattern_ids: ["P-05"]
process_tags: ["employee_time", "approval", "payroll_prep"]
pain_tags: ["manual_entry", "change_control"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/smallbusiness/comments/sb2xb0/time_tracking_with_google_sheets/
language: de
```

**Betriebsart:** kleine Landschaftsbaufirma mit ein bis vier Teilzeit- und Saisonkräften.

**Primärquelle:** [Reddit: „Time Tracking with Google Sheets?“](https://www.reddit.com/r/smallbusiness/comments/sb2xb0/time_tracking_with_google_sheets/)

**Belegter Ist-Prozess:** Der Inhaber erwägt eine Google-Tabelle, in die Mitarbeitende Start- und Endzeiten eintragen. Nach Ende des Abrechnungszeitraums sollen die Zeiten freigegeben und gegen spätere Änderungen gesperrt werden.

**Belegter Engpass:** Nachvollziehbare Erfassung, Freigabe und Unveränderbarkeit von Zeiten ohne teures System.

## Chunk: K-10_interview_questions – Diagnosefragen zu Saisonbetrieb: Arbeitszeiterfassung für 1–4 Teilzeitkräfte

```yaml
chunk_id: K-10_interview_questions
document_id: additional_kmu_01
case_id: K-10
chunk_type: interview_question_set
pattern_id: P-05
pattern_ids: ["P-05"]
process_tags: ["employee_time", "approval", "payroll_prep"]
pain_tags: ["manual_entry", "change_control"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Muss der Einsatzort erfasst werden? Wer korrigiert Fehler? Welche arbeitsrechtlichen und datenschutzrechtlichen Regeln gelten lokal? Welches Lohnsystem erhält den Export?

## Chunk: K-10_automation_pattern – Mögliches Automationsmuster zu Saisonbetrieb: Arbeitszeiterfassung für 1–4 Teilzeitkräfte

```yaml
chunk_id: K-10_automation_pattern
document_id: additional_kmu_01
case_id: K-10
chunk_type: automation_pattern
pattern_id: P-05
pattern_ids: ["P-05"]
process_tags: ["employee_time", "approval", "payroll_prep"]
pain_tags: ["manual_entry", "change_control"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

`Clock-in/out → Plausibilitätsprüfung → Mitarbeitendenbestätigung → Freigabe durch Inhaber → Export für Lohn`.

## Chunk: K-10_guardrail – Grenzen zu Saisonbetrieb: Arbeitszeiterfassung für 1–4 Teilzeitkräfte

```yaml
chunk_id: K-10_guardrail
document_id: additional_kmu_01
case_id: K-10
chunk_type: automation_guardrail
pattern_id: P-05
pattern_ids: ["P-05"]
process_tags: ["employee_time", "approval", "payroll_prep"]
pain_tags: ["manual_entry", "change_control"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Arbeitszeitkorrekturen, Pausenverstöße oder Lohnabrechnung.

## Chunk: K-11_case_evidence – Mobiler Mechaniker stellt ersten Mitarbeiter ein

```yaml
chunk_id: K-11_case_evidence
document_id: additional_kmu_01
case_id: K-11
chunk_type: case_evidence
pattern_id: P-05
pattern_ids: ["P-05"]
process_tags: ["field_staff_time", "payroll_prep"]
pain_tags: ["manual_entry", "growth_admin"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/smallbusiness/comments/jsm4az/just_hired_my_first_employee_how_do_i_track_their/
language: de
```

**Betriebsart:** mobiler Mechaniker; zweiter Transporter und erste Einstellung.

**Primärquelle:** [Reddit: „Just hired my first employee. How do I track their hours?“](https://www.reddit.com/r/smallbusiness/comments/jsm4az/just_hired_my_first_employee_how_do_i_track_their/)

**Belegter Ist-Prozess:** Nach Kauf eines zweiten Vans und Einstellung einer Person wird die Arbeitszeit bisher vollständig von Hand nachgehalten. Der Inhaber sucht einen Weg, Zeiten zu verfolgen und korrekt zu bezahlen.

**Belegter Engpass:** Wachstum erzeugt unmittelbar einen personengebundenen Verwaltungsprozess mit Fehlerrisiko.

## Chunk: K-11_interview_questions – Diagnosefragen zu Mobiler Mechaniker stellt ersten Mitarbeiter ein

```yaml
chunk_id: K-11_interview_questions
document_id: additional_kmu_01
case_id: K-11
chunk_type: interview_question_set
pattern_id: P-05
pattern_ids: ["P-05"]
process_tags: ["field_staff_time", "payroll_prep"]
pain_tags: ["manual_entry", "growth_admin"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Wird nur Anwesenheit oder auch Zeit je Auftrag benötigt? Wie werden Fahrzeit, Notdienst, Material und Mehrarbeit behandelt?

## Chunk: K-11_automation_pattern – Mögliches Automationsmuster zu Mobiler Mechaniker stellt ersten Mitarbeiter ein

```yaml
chunk_id: K-11_automation_pattern
document_id: additional_kmu_01
case_id: K-11
chunk_type: automation_pattern
pattern_id: P-05
pattern_ids: ["P-05"]
process_tags: ["field_staff_time", "payroll_prep"]
pain_tags: ["manual_entry", "growth_admin"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

wie K-10; bei Außeneinsätzen zusätzlich `Auftrag ↔ Teammitglied ↔ Arbeitszeit ↔ abrechenbare Leistung`.

## Chunk: K-11_guardrail – Grenzen zu Mobiler Mechaniker stellt ersten Mitarbeiter ein

```yaml
chunk_id: K-11_guardrail
document_id: additional_kmu_01
case_id: K-11
chunk_type: automation_guardrail
pattern_id: P-05
pattern_ids: ["P-05"]
process_tags: ["field_staff_time", "payroll_prep"]
pain_tags: ["manual_entry", "growth_admin"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Payroll-Auszahlung oder automatische Lohnkorrekturen.

## Chunk: K-12_case_evidence – Belege: Foto, E-Mail, Cloud-Ordner, Tabellen-Nacharbeit

```yaml
chunk_id: K-12_case_evidence
document_id: additional_kmu_01
case_id: K-12
chunk_type: case_evidence
pattern_id: P-06
pattern_ids: ["P-06"]
process_tags: ["receipt_ocr", "expense_prep"]
pain_tags: ["media_break", "manual_entry"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/smallbusiness/comments/187lgba/cheap_or_free_app_for_saving_receiptsexpenses/
language: de
```

**Betriebsart:** nicht näher spezifiziertes kleines Unternehmen.

**Primärquelle:** [Reddit: „Cheap or free app for saving receipts/expenses?“](https://www.reddit.com/r/smallbusiness/comments/187lgba/cheap_or_free_app_for_saving_receiptsexpenses/)

**Belegter Ist-Prozess:** Belege werden fotografiert, per E-Mail an sich selbst gesendet, in OneDrive abgelegt und ihre Details anschließend manuell in eine Tabelle eingetragen.

**Belegter Engpass:** Viele Übergaben für einen einzelnen Beleg; der Prozess wird als aufwändig beschrieben.

## Chunk: K-12_interview_questions – Diagnosefragen zu Belege: Foto, E-Mail, Cloud-Ordner, Tabellen-Nacharbeit

```yaml
chunk_id: K-12_interview_questions
document_id: additional_kmu_01
case_id: K-12
chunk_type: interview_question_set
pattern_id: P-06
pattern_ids: ["P-06"]
process_tags: ["receipt_ocr", "expense_prep"]
pain_tags: ["media_break", "manual_entry"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Welche Felder sind notwendig? Welche Belegarten sind schwer lesbar? Welches Buchhaltungs-/Steuerberaterformat wird benötigt? Wo dürfen Originale gespeichert werden?

## Chunk: K-12_automation_pattern – Mögliches Automationsmuster zu Belege: Foto, E-Mail, Cloud-Ordner, Tabellen-Nacharbeit

```yaml
chunk_id: K-12_automation_pattern
document_id: additional_kmu_01
case_id: K-12
chunk_type: automation_pattern
pattern_id: P-06
pattern_ids: ["P-06"]
process_tags: ["receipt_ocr", "expense_prep"]
pain_tags: ["media_break", "manual_entry"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

`Belegbild → OCR/Extraktion → Kategorie-/Plausibilitätsvorschlag → menschliche Prüfung → Ablage/Export`.

## Chunk: K-12_guardrail – Grenzen zu Belege: Foto, E-Mail, Cloud-Ordner, Tabellen-Nacharbeit

```yaml
chunk_id: K-12_guardrail
document_id: additional_kmu_01
case_id: K-12
chunk_type: automation_guardrail
pattern_id: P-06
pattern_ids: ["P-06"]
process_tags: ["receipt_ocr", "expense_prep"]
pain_tags: ["media_break", "manual_entry"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

steuerliche Kategorie, Vorsteuerabzug, Aufbewahrungsfrist oder Buchungssatz ohne fachliche Kontrolle.

## Chunk: K-13_case_evidence – Solo-Berater: Zeit wird nachträglich rekonstruiert

```yaml
chunk_id: K-13_case_evidence
document_id: additional_kmu_01
case_id: K-13
chunk_type: case_evidence
pattern_id: P-05
pattern_ids: ["P-05"]
process_tags: ["consulting_time", "billing_prep"]
pain_tags: ["memory_gap", "late_entry"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/smallbusiness/comments/no1ixt/as_a_contractorconsultant_how_do_you_track_your/
language: de
```

**Betriebsart:** selbstständiger Berater/Auftragnehmer.

**Primärquelle:** [Reddit: „As a contractor/consultant, how do you track your hours?“](https://www.reddit.com/r/smallbusiness/comments/no1ixt/as_a_contractorconsultant_how_do_you_track_your/)

**Belegter Ist-Prozess:** Arbeitszeiten werden in Excel erfasst und mit einer Pivot-Tabelle ausgewertet. An vollen Tagen wird die Erfassung in Echtzeit vergessen; danach entstehen Lücken, bei denen nicht mehr klar ist, was getan wurde.

**Belegter Engpass:** Nachträgliche Erinnerung ist eine schlechte Datenquelle für abrechenbare oder analysierbare Zeit.

## Chunk: K-13_interview_questions – Diagnosefragen zu Solo-Berater: Zeit wird nachträglich rekonstruiert

```yaml
chunk_id: K-13_interview_questions
document_id: additional_kmu_01
case_id: K-13
chunk_type: interview_question_set
pattern_id: P-05
pattern_ids: ["P-05"]
process_tags: ["consulting_time", "billing_prep"]
pain_tags: ["memory_gap", "late_entry"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Wird minutengenau abgerechnet? Gibt es feste Projektcodes? Welche Tätigkeiten sind nicht abrechenbar? Muss der Kunde Details sehen?

## Chunk: K-13_automation_pattern – Mögliches Automationsmuster zu Solo-Berater: Zeit wird nachträglich rekonstruiert

```yaml
chunk_id: K-13_automation_pattern
document_id: additional_kmu_01
case_id: K-13
chunk_type: automation_pattern
pattern_id: P-05
pattern_ids: ["P-05"]
process_tags: ["consulting_time", "billing_prep"]
pain_tags: ["memory_gap", "late_entry"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

`niedrigschwelliger Zeiteintrag → Zuordnung zu Kunde/Aufgabe → Tagesrückblick bei Lücke → Freigabe → Auswertung/Rechnungsgrundlage`.

## Chunk: K-13_guardrail – Grenzen zu Solo-Berater: Zeit wird nachträglich rekonstruiert

```yaml
chunk_id: K-13_guardrail
document_id: additional_kmu_01
case_id: K-13
chunk_type: automation_guardrail
pattern_id: P-05
pattern_ids: ["P-05"]
process_tags: ["consulting_time", "billing_prep"]
pain_tags: ["memory_gap", "late_entry"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Abrechenbarkeit oder Projektzuordnung aus bloßen Kalender-/Aktivitätsdaten.

## Chunk: K-14_case_evidence – Kleines Bekleidungslabel ohne Website nutzt Google Forms

```yaml
chunk_id: K-14_case_evidence
document_id: additional_kmu_01
case_id: K-14
chunk_type: case_evidence
pattern_id: P-02
pattern_ids: ["P-02"]
process_tags: ["order_form", "fulfillment"]
pain_tags: ["weak_customer_flow", "missing_status"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: https://www.reddit.com/r/smallbusiness/comments/1c6db7o/keeping_track_of_orders/
language: de
```

**Betriebsart:** Ein-Personen-Bekleidungsmarke in der Startphase.

**Primärquelle:** [Reddit: „Keeping Track of orders“](https://www.reddit.com/r/smallbusiness/comments/1c6db7o/keeping_track_of_orders/)

**Belegter Ist-Prozess:** Eingehende Bestellungen werden über Google Forms nachgehalten. Der Betreiber möchte eine leichter zugängliche Lösung für sich und Kunden, hat aber noch keine Website.

**Belegter Engpass:** Ein Erfassungswerkzeug ersetzt nicht automatisch einen verständlichen Kundenweg oder ein zentrales Statusmanagement.

## Chunk: K-14_interview_questions – Diagnosefragen zu Kleines Bekleidungslabel ohne Website nutzt Google Forms

```yaml
chunk_id: K-14_interview_questions
document_id: additional_kmu_01
case_id: K-14
chunk_type: interview_question_set
pattern_id: P-02
pattern_ids: ["P-02"]
process_tags: ["order_form", "fulfillment"]
pain_tags: ["weak_customer_flow", "missing_status"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Gibt es Varianten/Größen? Wie werden Zahlungen und Versandstatus erfasst? Sind Vorbestellungen möglich? Wie oft ändern Kunden Bestellungen?

## Chunk: K-14_automation_pattern – Mögliches Automationsmuster zu Kleines Bekleidungslabel ohne Website nutzt Google Forms

```yaml
chunk_id: K-14_automation_pattern
document_id: additional_kmu_01
case_id: K-14
chunk_type: automation_pattern
pattern_id: P-02
pattern_ids: ["P-02"]
process_tags: ["order_form", "fulfillment"]
pain_tags: ["weak_customer_flow", "missing_status"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

`Bestellformular → Validierung → Auftragsbestätigung → Zahlungs-/Fulfillmentstatus → Versandinformation`.

## Chunk: K-14_guardrail – Grenzen zu Kleines Bekleidungslabel ohne Website nutzt Google Forms

```yaml
chunk_id: K-14_guardrail
document_id: additional_kmu_01
case_id: K-14
chunk_type: automation_guardrail
pattern_id: P-02
pattern_ids: ["P-02"]
process_tags: ["order_form", "fulfillment"]
pain_tags: ["weak_customer_flow", "missing_status"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Verfügbarkeit, Liefertermin oder Ersatzprodukt ohne Lager- und Produktionsdaten.

## Chunk: P-01_diagnostic_pattern – Unstrukturierter Eingang

```yaml
chunk_id: P-01_diagnostic_pattern
document_id: additional_kmu_01
case_id: MULTI
chunk_type: diagnostic_pattern
pattern_id: P-01
pattern_ids: ["P-01"]
process_tags: ["inquiry_intake", "multichannel"]
pain_tags: []
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Nachrichten strukturiert erfassen; verbindliche Inhalte erst nach Prüfung senden.

## Chunk: P-02_diagnostic_pattern – Auftrag zu Produktion oder Erfüllung

```yaml
chunk_id: P-02_diagnostic_pattern
document_id: additional_kmu_01
case_id: MULTI
chunk_type: diagnostic_pattern
pattern_id: P-02
pattern_ids: ["P-02"]
process_tags: ["order_management", "production_planning"]
pain_tags: []
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Auftragsdaten standardisieren und Status sichtbar machen; Kapazitäts- und Qualitätsfreigaben beibehalten.

## Chunk: P-03_diagnostic_pattern – Termin und reale Kapazität

```yaml
chunk_id: P-03_diagnostic_pattern
document_id: additional_kmu_01
case_id: MULTI
chunk_type: diagnostic_pattern
pattern_id: P-03
pattern_ids: ["P-03"]
process_tags: ["scheduling", "capacity"]
pain_tags: []
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Termine und Ressourcen als Vorschlag koordinieren; keine Zusage ohne reale Kapazitätsprüfung.

## Chunk: P-04_diagnostic_pattern – Zahlung und offene Posten

```yaml
chunk_id: P-04_diagnostic_pattern
document_id: additional_kmu_01
case_id: MULTI
chunk_type: diagnostic_pattern
pattern_id: P-04
pattern_ids: ["P-04"]
process_tags: ["invoicing", "payment_followup"]
pain_tags: []
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Fälligkeiten erkennen und Erinnerungen vorbereiten; Streitfälle und Eskalation menschlich entscheiden.

## Chunk: P-05_diagnostic_pattern – Arbeitszeit und Abrechnungsvorbereitung

```yaml
chunk_id: P-05_diagnostic_pattern
document_id: additional_kmu_01
case_id: MULTI
chunk_type: diagnostic_pattern
pattern_id: P-05
pattern_ids: ["P-05"]
process_tags: ["time_tracking", "approval"]
pain_tags: []
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Zeiten erfassen und plausibilisieren; Korrektur und Abrechnung freigeben lassen.

## Chunk: P-06_diagnostic_pattern – Belege und Buchhaltungsvorbereitung

```yaml
chunk_id: P-06_diagnostic_pattern
document_id: additional_kmu_01
case_id: MULTI
chunk_type: diagnostic_pattern
pattern_id: P-06
pattern_ids: ["P-06"]
process_tags: ["receipt_processing", "ocr"]
pain_tags: []
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Daten extrahieren und zur Prüfung vorlegen; keine autonome steuerliche Einordnung.

## Chunk: P-07_diagnostic_pattern – Einkauf und Beschaffung

```yaml
chunk_id: P-07_diagnostic_pattern
document_id: additional_kmu_01
case_id: MULTI
chunk_type: diagnostic_pattern
pattern_id: P-07
pattern_ids: ["P-07"]
process_tags: ["procurement", "vendor_data"]
pain_tags: []
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Bedarf in Bestellentwürfe umsetzen; Bestellung nur nach Berechtigungs- und Freigaberegel.

## Bewertungsregel

Nutzen, Häufigkeit, Standardisierbarkeit, Datenreife, Integrationsaufwand, Datenschutz und Umfang menschlicher Entscheidungen werden **hybrid und evidenzbasiert anhand transparenter Rubrics und belegter Eingaben** bewertet. Eine Formel kann regelbasiert sein; nicht messbare Eingaben dürfen nicht als objektive Fakten behandelt werden.
