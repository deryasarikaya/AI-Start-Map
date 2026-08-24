# AI Start Map – kuratierter RAG-Korpus Massagesalon

Die Prozessbereiche wurden semantisch getrennt. Die Budgetangabe bleibt ausdrücklich als ungeklärter Widerspruch erhalten.

**Quellenhinweis:** Im Originalgespräch lautet die Passage sinngemäß: Budget für beide Filialen ungefähr 800 EUR, möglicherweise jeweils 400 oder 500 EUR, zusätzlich 300 EUR Instagram; unmittelbar danach wird von fast 1.200 EUR nur für Google-Werbung gesprochen. Deshalb darf kein eindeutiger Betrag als gesicherter Fakt gespeichert werden.

**Prompt-Guardrail:** Keine Daten dieses Salons als Fakten über einen aktuell analysierten Betrieb übernehmen.

## Chunk: M-01_case_overview – Thai-Massagesalon – Betriebsüberblick

```yaml
chunk_id: M-01_case_overview
document_id: massage_01
case_id: M-01
chunk_type: case_evidence
pattern_id: P-01
pattern_ids: ["P-01", "P-03", "P-04", "P-05", "P-06"]
process_tags: ["multichannel_intake", "scheduling", "capacity", "staff_planning", "payment", "operations"]
pain_tags: ["double_booking", "staff_shortage", "manual_confirmation", "missing_time_records"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: massage_case_interview
language: de
```

- Thai-Massagesalon mit zwei Filialen: Feuerbach und Cannstatt.
- Insgesamt vier Massagebetten, jedoch nicht dauerhaft vier verfügbare Masseurinnen.
- Beide Filialen liegen im Obergeschoss und haben dadurch geringe Sichtbarkeit für Laufkundschaft.
- Arbeitszeit und Terminvergabe: Montag bis Sonntag, 10:00 bis 20:00 Uhr.
- Das Geschäft befindet sich noch in einer Aufbauphase und wird von der Inhaberin als Zweitgeschäft geführt; sie ist deshalb nicht immer vor Ort.

### Ist-Ablauf

1. Neue Kunden werden vor allem durch Google Ads gewonnen; zusätzlich laufen Instagram Ads, Instagram-Content und Angebotsaktionen.
2. Teilweise kommen Kunden durch Kundenstopper, Mundpropaganda und Stammkundschaft.
3. Die Auslastung ist saisonal und stark schwankend: im Winter besonders Freitag bis Sonntag, im Sommer nicht verlässlich am Wochenende.
4. In guten Zeiten sind drei bis fünf Mitarbeitende nötig; die tatsächliche Verfügbarkeit ist aber geringer.

### Relevante Details

- Im Gespräch wurden unterschiedliche ungefähre Angaben zum Werbebudget genannt; der aktuelle Gesamtbetrag und die Aufteilung je Kanal und Filiale müssen noch geklärt werden.
- Geringe Laufkundschaft, besonders in Feuerbach; Kundenstopper in Cannstatt wurden beschädigt und müssen erneuert werden.
- Neukunden erhalten 10 % Rabatt; Gutscheine im Wert von 25, 50 und 100 EUR sind online kaufbar.

### Prozessrisiko

Marketing erzeugt Anfragen, aber die Kapazität ist nicht zuverlässig verfügbar. Die Inhaberin kann besonders spontane Paar-/Partnermassagen häufig nicht annehmen.

## Chunk: M-01_appointment_capacity_evidence – Terminvereinbarung und Kapazitätsprüfung

```yaml
chunk_id: M-01_appointment_capacity_evidence
document_id: massage_01
case_id: M-01
chunk_type: case_evidence
pattern_id: P-01
pattern_ids: ["P-01", "P-03"]
process_tags: ["multichannel_intake", "scheduling", "capacity"]
pain_tags: ["double_booking", "manual_confirmation", "staff_shortage"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: massage_case_interview
language: de
```

### Eingangskanäle

- Website / Kontaktformular / E-Mail
- WhatsApp über einen Website-Button
- Telefon
- Instagram Messenger
- Persönliche bzw. spontane Anfragen

### Ist-Ablauf

1. Kunde fragt über einen der Kanäle einen Termin an oder bucht über die Website.
2. Über die Website wählt der Kunde Dauer (30, 60 oder 120 Minuten) und eine Uhrzeit in 30-Minuten-Schritten.
3. Die Online-Buchung ist zunächst nur eine Anfrage, keine verbindliche Zusage.
4. Die Inhaberin prüft manuell, ob die gewünschte Zeit und ausreichendes Personal verfügbar sind.
5. Sie versendet die Terminbestätigung separat.
6. Der Termin muss manuell im Überblick/Kalender nachgeführt werden.

### Warum keine automatische Sofortbuchung genutzt wird

- Die verfügbare Zahl der Masseurinnen ändert sich.
- Würden nur feste Fenster für eine Masseurin geöffnet, könnten weitere mögliche Termine verloren gehen, falls kurzfristig doch noch eine zweite Masseurin organisiert werden kann.
- Die Inhaberin möchte Kapazitätsentscheidungen daher manuell treffen.

### Probleme und Folgen

- Mehrere Kanäle führen zu Unterbrechungen und fehlendem Gesamtüberblick.
- Termine werden gelegentlich nicht eingetragen.
- Es kam bereits dreimal zu Doppel- bzw. Mehrfachbelegungen: zwei oder drei Kunden zur selben Zeit bei nur einer Masseurin.
- Folgen: unangenehme Kundensituationen, Ausgabe eines Gutscheins für die nächste Massage als Kulanz.
- Spontane Paar-/Partnermassagen werden wegen fehlender Kapazität meist abgelehnt.

### Prozessdaten, die für eine Diagnose fehlen

- In welchem Kalender oder welcher Liste werden bestätigte Termine heute geführt?
- Welche Daten werden bei einer Anfrage erfasst (Filiale, gewünschte Leistung, Dauer, Anzahl Personen, Kontakt, Zahlungsart)?
- Wie schnell werden Anfragen üblicherweise beantwortet?
- Wie oft treten Doppelbuchungen, abgesagte oder nicht bestätigte Anfragen tatsächlich auf?
- Nach welchen Regeln entscheidet die Inhaberin, ob Personal kurzfristig organisiert wird?

## Chunk: M-01_staff_planning_evidence – Personalplanung, Einsatz und Vergütung

```yaml
chunk_id: M-01_staff_planning_evidence
document_id: massage_01
case_id: M-01
chunk_type: case_evidence
pattern_id: P-03
pattern_ids: ["P-03", "P-05"]
process_tags: ["staff_planning", "time_tracking", "payroll_prep"]
pain_tags: ["demand_capacity_mismatch", "missing_time_records"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: employee_and_financial_data
evidence_scope: source_reported_current_process
source_url: massage_case_interview
language: de
```

### Ist-Situation

- Personalengpass ist das zentrale Problem.
- Die Saloninhaberin verliert Masseurinnen, wenn zu wenige Massagen vorhanden sind.
- Gleichzeitig erzeugt zu viel eingeplantes Personal bei zu geringer Nachfrage Verluste.
- Für eine tragfähige Auslastung erwarten Masseurinnen nach Aussage der Inhaberin ungefähr vier bis fünf Massagen bzw. einen ausreichend gefüllten Acht-Stunden-Tag.

### Vergütungslogik (laut Gespräch, noch zu klären)

- Teilweise Abrechnung pro Massage: etwa 25 EUR pro Massage unter der Woche.
- Wenn die Vergütung daraus den Mindestlohn nicht erreicht, wird auf Stundenlohn aufgefüllt (Beispiel: acht Stunden x 14 EUR = ca. 100 EUR).
- Eine Vollzeitmitarbeiterin erhält ein fest vereinbartes Grundgehalt und soll fünf bis sechs Massagen pro Tag leisten; bei nur drei Massagen entsteht für die Inhaberin Verlust.
- Es gibt mindestens eine fest angestellte Mitarbeiterin sowie weitere Einsatz-/Aushilfskräfte.

### Probleme und Folgen

- Nachfrage und Personalbestand passen zeitlich nicht zuverlässig zusammen.
- Bei drei Massagen und zwei bezahlten Masseurinnen entsteht laut Inhaberin ein deutlicher Verlust.
- Arbeitszeiten von Mitarbeitenden werden aktuell nicht dokumentiert.
- Die fehlende Dokumentation erschwert den Überblick für Lohn, Mindestlohn und Finanzamt.

### Prozessdaten, die für eine Diagnose fehlen

- Vollständige Rollen, Vertragsarten und Verfügbarkeiten aller Mitarbeitenden.
- Verbindliche Regeln für Provision, Grundgehalt, Mindestlohnaufstockung und Zuschläge.
- Tatsächliche Stunden, Auslastung und Umsatz je Filiale / Mitarbeiterin / Tag.
- Wer erstellt Dienstpläne und wie werden Änderungen kommuniziert?

## Chunk: M-01_payment_receipts_evidence – Zahlung, Kasse und Belege

```yaml
chunk_id: M-01_payment_receipts_evidence
document_id: massage_01
case_id: M-01
chunk_type: case_evidence
pattern_id: P-04
pattern_ids: ["P-04", "P-06"]
process_tags: ["payment", "cash_register", "receipt_processing"]
pain_tags: ["manual_entry", "missing_payment_integration"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: financial_data
evidence_scope: source_reported_current_process
source_url: massage_case_interview
language: de
```

### Ist-Ablauf

- Aktuell: Barzahlung oder Echtzeitüberweisung.
- Website-Zahlung: PayPal; online buchbar sind insbesondere Gutscheine und Neukundenaktionen.
- Andere Massagearten werden wegen PayPal-Gebühren nicht online angeboten.
- Kunden erhalten bei Bedarf eine Quittung; ansonsten muss die Zahlung dennoch manuell als Quittung erfasst werden.
- Ein Kassensystem mit integrierter Kartenzahlung ist bestellt, aber noch nicht aufgebaut.
- Abrechnung erfolgt über den Steuerberater.

### Einschränkungen und Probleme

- Kartenakzeptanz besteht aktuell noch nicht, obwohl sie geplant ist.
- Der Betrieb braucht weiterhin Bargeld, unter anderem für Barauszahlungen an Personal.
- Die Inhaberin muss Zahlungen und Belege manuell erfassen.
- Zahlungserfassung, Mitarbeiterzeiten und steuerrelevante Übersicht sind noch nicht durchgängig organisiert.

## Chunk: M-01_operations_quality_evidence – Salonbetrieb und Qualitätssicherung

```yaml
chunk_id: M-01_operations_quality_evidence
document_id: massage_01
case_id: M-01
chunk_type: case_evidence
pattern_id: P-05
pattern_ids: ["P-05"]
process_tags: ["quality_control", "inventory", "opening_closing"]
pain_tags: ["owner_absence", "service_interruption", "missing_routine"]
content_origin: source_reported
is_primary_evidence: true
sensitivity: business_operations
evidence_scope: source_reported_current_process
source_url: massage_case_interview
language: de
```

### Ist-Situation

- Weil die Inhaberin nicht dauerhaft vor Ort ist, bestehen Risiken bei Hygiene, Reinigung von Tischen und Empfangsqualität.
- Kommt der nächste Kunde, muss eine Masseurin teils die Behandlung unterbrechen, um die Tür zu öffnen.
- Fehlende Empfangsrolle oder zu wenig paralleles Personal stört dadurch die eigentliche Dienstleistung.
- Laufende Beschaffung: Handtücher, Decken, Öl und Wasser für Mitarbeitende.

### Prozessdaten, die für eine Diagnose fehlen

- Gibt es feste Reinigungs-, Öffnungs- und Schließroutinen?
- Wie wird Materialbestand heute kontrolliert und nachbestellt?
- Welche Aufgaben sollen Masseurinnen, Empfang und Inhaberin jeweils übernehmen?

## Chunk: M-01_diagnostic_pattern – Terminproblem ist ein gekoppeltes Kapazitätsproblem

```yaml
chunk_id: M-01_diagnostic_pattern
document_id: massage_01
case_id: M-01
chunk_type: diagnostic_pattern
pattern_id: P-01
pattern_ids: ["P-01", "P-03"]
process_tags: ["scheduling", "capacity", "multichannel_intake"]
pain_tags: ["double_booking", "staff_shortage"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: business_operations
evidence_scope: expert_derived_from_case
language: de
```

Das sichtbare Terminproblem hängt mit variabler Personalverfügbarkeit, mehreren Eingangskanälen, manueller Bestätigung und fehlender gemeinsamer Datenbasis zusammen. Retrieval darf deshalb nicht ausschließlich ein Kalender-Playbook liefern.

## Chunk: M-01_guardrails – Grenzen und Freigaben

```yaml
chunk_id: M-01_guardrails
document_id: massage_01
case_id: M-01
chunk_type: automation_guardrail
pattern_id: P-01
pattern_ids: ["P-01", "P-03", "P-04", "P-05", "P-06"]
process_tags: ["multichannel_intake", "scheduling", "capacity", "staff_planning", "payment", "operations"]
pain_tags: ["double_booking", "staff_shortage", "manual_confirmation", "missing_time_records"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: employee_customer_and_financial_data
evidence_scope: expert_derived_from_case
language: de
```

Keine automatische Sofortbestätigung, solange die reale Personalverfügbarkeit nicht verlässlich vorliegt. Keine autonome Vergütungs-, Lohn-, Steuer- oder arbeitsrechtliche Entscheidung. Buchungs-, Zahlungs- und Mitarbeiterdaten benötigen Rollen- und Zugriffsschutz. Hygiene- oder Qualitätskontrolle darf nicht allein aus einer digitalen Checkliste als erfüllt gelten.

## Chunk: M-01_interview_questions – Noch notwendige Diagnosefragen

```yaml
chunk_id: M-01_interview_questions
document_id: massage_01
case_id: M-01
chunk_type: interview_question_set
pattern_id: P-01
pattern_ids: ["P-01", "P-03", "P-04", "P-05", "P-06"]
process_tags: ["multichannel_intake", "scheduling", "capacity", "staff_planning", "payment", "operations"]
pain_tags: ["double_booking", "staff_shortage", "manual_confirmation", "missing_time_records"]
content_origin: expert_derived
is_primary_evidence: false
sensitivity: employee_customer_and_financial_data
evidence_scope: expert_derived_from_case
language: de
```

- In welchem Kalender oder welcher Liste werden bestätigte Termine geführt?
- Welche Pflichtdaten werden je Anfrage erfasst: Filiale, Leistung, Dauer, Personenzahl, Kontakt und Zahlungsart?
- Welche Regeln bestimmen, ob zusätzliches Personal organisiert wird?
- Welche Rollen, Vertragsarten und Verfügbarkeiten bestehen?
- Wie werden Arbeitszeiten, Vergütungsgrundlagen und Planänderungen dokumentiert?
- Wie werden Zahlungen, Quittungen und steuerrelevante Daten zusammengeführt?
- Welche Öffnungs-, Reinigungs-, Schließ- und Nachbestellroutinen sind verbindlich?
- Im Gespräch wurden unterschiedliche ungefähre Angaben zum Werbebudget genannt; wie hoch sind die aktuellen Budgets je Kanal und Filiale tatsächlich?
