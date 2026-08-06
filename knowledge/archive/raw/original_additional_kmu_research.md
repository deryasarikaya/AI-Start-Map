# AI Start Map – RAG-Quellenkorpus: reale Prozessschwachstellen kleiner Unternehmen

**Erstellt:** 16.07.2026  
**Zweck:** Ergänzender, kuratierter Quellenkorpus für die RAG-Pipeline von AI Start Map. Er erweitert die vorhandenen zehn ausführlichen Fallbeispiele und die Prozessanalyse des Massagesalons.  
**Abgrenzung:** Dies ist keine Sammlung fertiger Produktlösungen. Sie liefert reale, öffentlich geschilderte Ist-Prozesse, typische Engpässe und die Bedingungen, die vor einer Automation geprüft werden müssen.

## 1. Warum dieser Korpus für AI Start Map wichtig ist

Die Fälle zeigen wiederkehrende Muster in Solo- und Kleinstbetrieben:

- Arbeit beginnt in E-Mail, WhatsApp, Instagram-DMs, Telefonaten oder Papier.
- Informationen werden manuell in Notizen, Tabellen oder mehrere Tools übertragen.
- Der Unternehmer ist die zentrale Schaltstelle für Prüfung, Priorisierung und Freigabe.
- Das sichtbare Problem (z. B. „Ich brauche einen Kalender“) ist oft nur ein Symptom eines unstrukturierten Eingangs, fehlender Kapazitätsdaten oder fehlender Zuständigkeiten.

Für die Diagnose darf die Pipeline daher nicht direkt von „Problem“ auf „Tool“ springen. Sie muss zunächst Prozess, Daten, Ausnahmen und menschliche Entscheidungen rekonstruieren.

## 2. Quellen- und Verwendungsregeln

### Was als Fakt gilt

Die in Abschnitt 3 beschriebenen Ist-Abläufe stammen aus dem jeweiligen öffentlichen Erstbeitrag. Sie sind pseudonyme Selbstberichte und keine unabhängig geprüften Unternehmensdaten.

### Was als Analyse markiert ist

Die möglichen Automationsmuster und Diagnosefragen sind fachliche Ableitungen für AI Start Map. Sie sind **keine Aussage**, dass der jeweilige Betrieb diese Lösung eingeführt hat oder dass sie ohne Prüfung passend wäre.

### Was nicht in Antworten geraten darf

- konkrete Zeit- oder Geldeinsparungen, wenn keine Messwerte vorliegen;
- pauschale Aussagen wie „vollautomatisiere Terminbuchungen“;
- Speicherung oder Verarbeitung sensibler Daten ohne Datenschutz- und Berechtigungsprüfung;
- der Eindruck, einzelne Reddit-Fälle seien statistisch repräsentativ.

## 3. Ergänzende reale Fälle

### K-01 – Kunden-E-Mails werden manuell in eine Tabelle kopiert

- **Betriebsart:** nicht näher spezifiziertes kleines Unternehmen.
- **Primärquelle:** [Reddit: „Anyone else manually logging customer emails to a spreadsheet?“](https://www.reddit.com/r/smallbusiness/comments/1ogmune/anyone_else_manually_logging_customer_emails_to_a/)
- **Belegter Ist-Prozess:** Wichtige Kunden-E-Mails zu Bestellungen, Anfragen und Angeboten werden aus Gmail per Copy-paste in eine Tabelle übertragen, weil sonst Dinge übersehen wurden.
- **Belegter Engpass:** Der Vorgang ist mühsam; der Auslöser ist, dass E-Mails im Postfach verloren gehen bzw. nicht zuverlässig nachverfolgt werden.
- **Analyse – wiederverwendbares Muster:** `Nachricht → Klassifikation → strukturierter Vorgang → Status/Fälligkeit → menschliche Bearbeitung`.
- **Nicht automatisch entscheiden:** Angebotsfreigabe, Preis, verbindliche Kundenzusage.
- **Diagnosefragen:** Welche E-Mail-Typen sollen erfasst werden? Welche Felder sind pro Vorgang Pflicht? Wann gilt ein Vorgang als erledigt? Gibt es personenbezogene oder vertrauliche Anhänge?

### K-02 – Beschaffung aus großer Tabelle und E-Mail-Bestellung

- **Betriebsart:** kleiner Betrieb mit Geräten/Materialien und mehreren Lieferanten.
- **Primärquelle:** [Reddit: „Program for managing equipment and ordering“](https://www.reddit.com/r/smallbusiness/comments/1kc5ksw/program_for_managing_equipment_and_ordering/)
- **Belegter Ist-Prozess:** Geräte- und Preisinformationen liegen in einer Tabelle. Bestellungen erfolgen meist per E-Mail, teils über Webshops. Für jede Bestellung werden Artikelnummern aus der großen Tabelle gesucht, kopiert und je Lieferant in eine E-Mail übertragen.
- **Belegter Engpass:** Wiederholtes Suchen, Kopieren und manuelles Formulieren der Bestellungen.
- **Analyse – wiederverwendbares Muster:** `Bedarf → Artikel-/Lieferantenprüfung → Bestellentwurf → Freigabe → Versand → Bestellstatus`.
- **Nicht automatisch entscheiden:** Bestellung auslösen, Mengen ändern oder Lieferant auswählen ohne Freigaberegel.
- **Diagnosefragen:** Wer darf bestellen? Gibt es Mindestbestände, Rahmenverträge oder Preisänderungen? Ist ein eindeutiger Artikel- und Lieferantenstamm vorhanden?

### K-03 – Bäckerei: Bestellung, Abschrift und Produktionsliste

- **Betriebsart:** kleine Bäckerei.
- **Primärquelle:** [Reddit: „Looking for simple ordering taking/production creation“](https://www.reddit.com/r/smallbusiness/comments/nznglv/looking_for_simple_ordering_takingproduction/)
- **Belegter Ist-Prozess:** Bestellungen kommen per E-Mail und Telefon. Sie werden auf ein Auftragsblatt geschrieben, anschließend geprüft, nach Backwaren gruppiert und in eine gedruckte Tabelle übertragen. Diese Tabelle bildet die Grundlage der wöchentlichen Backliste.
- **Belegter Engpass:** Mehrfaches manuelles Schreiben derselben Bestellung, bevor daraus eine Produktionsplanung entsteht.
- **Analyse – wiederverwendbares Muster:** `Bestellung → strukturierte Positionen → Prüfung von Termin/Kapazität → Aggregation nach Produkt → Produktionsliste`.
- **Nicht automatisch entscheiden:** Machbarkeitszusage bei Sonderanfertigungen oder Überkapazität.
- **Diagnosefragen:** Welche Varianten, Allergene, Liefertermine und Mengen sind Pflicht? Wie werden Änderungen und Stornierungen behandelt? Welche Kapazitätsgrenzen gelten pro Tag?

### K-04 – Instagram-Kuchenverkauf: DMs, Notizen, Zahlungshistorie und WhatsApp-Merkliste

- **Betriebsart:** hausbasierte Kleinstbäckerei.
- **Primärquelle:** [Reddit: „My mother sells homemade cakes on Instagram and her…“](https://www.reddit.com/r/smallbusiness/comments/1tjqb5n/my_mother_sells_homemade_cakes_on_instagram_and/)
- **Belegter Ist-Prozess:** Bestellungen kommen über Instagram-DMs und Story-Antworten. Lieferadressen liegen in einer Notiz-App; der Zahlungseingang wird am Tagesende in der Zahlungshistorie geprüft; offene Bestellungen stehen in einer WhatsApp-Nachricht an sich selbst.
- **Belegter Engpass:** Mit steigendem Bestellvolumen „fällt das System auseinander“; Auftrags-, Adress-, Zahlungs- und Statusinformationen sind getrennt.
- **Analyse – wiederverwendbares Muster:** `DM → Auftrag mit Pflichtfeldern → Zahlungsabgleich → Produktions-/Lieferstatus → Kundeninformation`.
- **Nicht automatisch entscheiden:** Annahme eines Auftrags ohne Kapazitäts- und Preiskontrolle.
- **Diagnosefragen:** Gibt es feste Produktkataloge oder individuelle Torten? Was ist der Zahlungsnachweis? Wie werden Allergene, Abholung/Lieferung und Datenschutz der Adressen gehandhabt?

### K-05 – Instagram-Direktnachrichten als Shop- und Auftragskanal

- **Betriebsart:** kleines DM-basiertes Produktgeschäft.
- **Primärquelle:** [Reddit: „Anyone else overwhelmed by tracking client orders through DMs?“](https://www.reddit.com/r/smallbusiness/comments/1oz0v1u/anyone_else_overwhelmed_by_tracking_client_orders/)
- **Belegter Ist-Prozess:** Aufträge kommen hauptsächlich über Instagram-DMs. Bestellungen, Zahlungen, Terminierung und Follow-ups werden über DMs, Notizen und verstreute Tabellen nachgehalten.
- **Belegter Engpass:** Fehlender Gesamtüberblick; gängige Shop-Systeme werden als zu komplex bzw. zu teuer für den kleinen, DM-basierten Betrieb wahrgenommen.
- **Analyse – wiederverwendbares Muster:** `unstrukturierte Anfrage → Auftragssatz → Statusboard → Zahlung/Erfüllung → Follow-up`.
- **Nicht automatisch entscheiden:** Kundenkommunikation mit verbindlichen Liefer- oder Verfügbarkeitsaussagen.
- **Diagnosefragen:** Wie viele Aufträge pro Woche? Welche DMs sind nur Fragen, welche echte Aufträge? Welche Informationen fehlen typischerweise? Gibt es ein erlaubtes/technisch zugängliches Eingangssystem?

### K-06 – Mobiler Dienstleister: Terminplanung scheitert an realen Fahrzeiten

- **Betriebsart:** Dienstleister mit Einsätzen bei Kundinnen und Kunden vor Ort.
- **Primärquelle:** [Reddit: „For service pros who travel to clients’ homes, what scheduling software do you use?“](https://www.reddit.com/r/smallbusiness/comments/1m0u4qc/for_service_pros_who_travel_to_clients_homes_what/)
- **Belegter Ist-Prozess:** Der Betreiber plant Termine und kommuniziert erwartete Ankunftszeiten. Eine getestete Terminsoftware mit Pufferzeiten berücksichtigte keine tatsächlichen, standortabhängigen Fahrzeiten.
- **Belegter Engpass:** Hoher Koordinationsaufwand und ein Kalender, der die geografische Realität nicht abbildet.
- **Analyse – wiederverwendbares Muster:** `Anfrage mit Ort → Dauer-/Fahrzeit-Schätzung → Vorschlag → menschliche Prüfung → Bestätigung`.
- **Nicht automatisch entscheiden:** Routen- oder Terminoptimierung bei unvollständigen Orts-, Prioritäts- oder Qualifikationsdaten.
- **Diagnosefragen:** Einzelperson oder Team? Servicegebiet? feste Zeitfenster? benötigte Skills/Materialien? Wie teuer sind Verspätungen oder Umplanungen?

### K-07 – Wiederkehrende Rechnungen eines Reinigungs-Solo-Betriebs

- **Betriebsart:** selbstständige Reinigungskraft mit wöchentlichen bzw. zweiwöchentlichen Kundenterminen.
- **Primärquelle:** [Reddit: „Can someone help me word a polite request to clients, to pay their invoice?“](https://www.reddit.com/r/smallbusiness/comments/1b3j8r6/can_someone_help_me_word_a_polite_request_to/)
- **Belegter Ist-Prozess:** Nach der letzten Reinigung eines Monats wird eine Rechnung versendet. Die Zahlung wird bis Monatsende erbeten. Seit sechs Monaten müssen einzelne Kunden jeden Monat manuell zur Zahlung erinnert werden.
- **Belegter Engpass:** Wiederholte, unangenehme manuelle Zahlungserinnerung bei einem standardisierten, wiederkehrenden Prozess.
- **Analyse – wiederverwendbares Muster:** `Leistung abgeschlossen → Rechnung → Fälligkeit → Zahlungseingang → gestufter Erinnerungsentwurf → Eskalation`.
- **Nicht automatisch entscheiden:** Mahnung, Leistungssperre oder rechtliche Schritte ohne eine vom Betrieb festgelegte Regel und Freigabe.
- **Diagnosefragen:** Wie wird Zahlungseingang erkannt? Gibt es Teilzahlungen, Streitfälle oder unterschiedliche Zahlungsziele? Welcher Kommunikationskanal ist vereinbart?

### K-08 – Rechnungsnachverfolgung beansprucht messbar Zeit

- **Betriebsart:** kleiner Dienstleistungsbetrieb.
- **Primärquelle:** [Reddit: „What is your process for following up on unpaid invoices?“](https://www.reddit.com/r/smallbusiness/comments/1tuyjyn/what_is_your_process_for_following_up_on_unpaid/)
- **Belegter Ist-Prozess:** Bei ungefähr 15–20 aktiven Rechnungen werden Zahlungserinnerungen manuell per E-Mail gesendet; der Unternehmer berichtet, dies koste schätzungsweise zwei bis drei Stunden pro Woche und werde vergessen.
- **Belegter Engpass:** Fälligkeiten und Follow-ups sind nicht verlässlich in einem Ablauf verankert.
- **Analyse – wiederverwendbares Muster:** wie K-07, zusätzlich `Offene-Posten-Liste → Priorisierung → Entwurf → menschliche Freigabe/Versand`.
- **Nicht automatisch entscheiden:** Kontodaten/Banktransaktionen ohne sichere Integration und Kontrolllogik abgleichen.
- **Diagnosefragen:** Welche Datenquelle ist führend: Rechnungssystem oder Bank? Wie wird eine Zahlung eindeutig einer Rechnung zugeordnet? Welche Erinnerungsstufen sind zulässig?

### K-09 – Nagelstudio: No-Shows sind messbar, Slots sind nicht gleich Personen

- **Betriebsart:** Nagelstudio mit Terminbuchungen.
- **Primärquelle:** [Reddit: „How Do You Deal with No-Shows?“](https://www.reddit.com/r/smallbusiness/comments/1tfgi54/how_do_you_deal_with_noshows/)
- **Belegter Ist-Prozess:** Das Studio nutzt ein CRM und berichtet für einen Monat 23 No-Shows bei 1.388 Buchungen (1,6 % nach CRM-Zählung). Die Inhaber weisen darauf hin, dass ein CRM-Konto teilweise zwei Personen für zwei Leistungen bucht; dadurch unterschätzt die kontobasierte Kennzahl die blockierten Slots.
- **Belegter Engpass:** Die operative Auswirkung und die Kennzahl sind nicht identisch, wenn ein Buchungskonto mehrere Ressourcen/Personen bindet.
- **Analyse – wiederverwendbares Muster:** `Buchung → Ressourcen-/Slotanzahl → Bestätigung/Erinnerung → Status → No-show-Auswertung`.
- **Nicht automatisch entscheiden:** Überbuchung oder Gebühren ohne transparente Geschäftsregeln und Kundeneinwilligung.
- **Diagnosefragen:** Wird pro Konto, Termin, Leistung oder Ressource gemessen? Welche Slots können kurzfristig wieder vergeben werden? Welche No-show-Policy besteht?

### K-10 – Saisonbetrieb: Arbeitszeiterfassung für 1–4 Teilzeitkräfte

- **Betriebsart:** kleine Landschaftsbaufirma mit ein bis vier Teilzeit- und Saisonkräften.
- **Primärquelle:** [Reddit: „Time Tracking with Google Sheets?“](https://www.reddit.com/r/smallbusiness/comments/sb2xb0/time_tracking_with_google_sheets/)
- **Belegter Ist-Prozess:** Der Inhaber erwägt eine Google-Tabelle, in die Mitarbeitende Start- und Endzeiten eintragen. Nach Ende des Abrechnungszeitraums sollen die Zeiten freigegeben und gegen spätere Änderungen gesperrt werden.
- **Belegter Engpass:** Nachvollziehbare Erfassung, Freigabe und Unveränderbarkeit von Zeiten ohne teures System.
- **Analyse – wiederverwendbares Muster:** `Clock-in/out → Plausibilitätsprüfung → Mitarbeitendenbestätigung → Freigabe durch Inhaber → Export für Lohn`.
- **Nicht automatisch entscheiden:** Arbeitszeitkorrekturen, Pausenverstöße oder Lohnabrechnung.
- **Diagnosefragen:** Muss der Einsatzort erfasst werden? Wer korrigiert Fehler? Welche arbeitsrechtlichen und datenschutzrechtlichen Regeln gelten lokal? Welches Lohnsystem erhält den Export?

### K-11 – Mobiler Mechaniker stellt ersten Mitarbeiter ein

- **Betriebsart:** mobiler Mechaniker; zweiter Transporter und erste Einstellung.
- **Primärquelle:** [Reddit: „Just hired my first employee. How do I track their hours?“](https://www.reddit.com/r/smallbusiness/comments/jsm4az/just_hired_my_first_employee_how_do_i_track_their/)
- **Belegter Ist-Prozess:** Nach Kauf eines zweiten Vans und Einstellung einer Person wird die Arbeitszeit bisher vollständig von Hand nachgehalten. Der Inhaber sucht einen Weg, Zeiten zu verfolgen und korrekt zu bezahlen.
- **Belegter Engpass:** Wachstum erzeugt unmittelbar einen personengebundenen Verwaltungsprozess mit Fehlerrisiko.
- **Analyse – wiederverwendbares Muster:** wie K-10; bei Außeneinsätzen zusätzlich `Auftrag ↔ Teammitglied ↔ Arbeitszeit ↔ abrechenbare Leistung`.
- **Nicht automatisch entscheiden:** Payroll-Auszahlung oder automatische Lohnkorrekturen.
- **Diagnosefragen:** Wird nur Anwesenheit oder auch Zeit je Auftrag benötigt? Wie werden Fahrzeit, Notdienst, Material und Mehrarbeit behandelt?

### K-12 – Belege: Foto, E-Mail, Cloud-Ordner, Tabellen-Nacharbeit

- **Betriebsart:** nicht näher spezifiziertes kleines Unternehmen.
- **Primärquelle:** [Reddit: „Cheap or free app for saving receipts/expenses?“](https://www.reddit.com/r/smallbusiness/comments/187lgba/cheap_or_free_app_for_saving_receiptsexpenses/)
- **Belegter Ist-Prozess:** Belege werden fotografiert, per E-Mail an sich selbst gesendet, in OneDrive abgelegt und ihre Details anschließend manuell in eine Tabelle eingetragen.
- **Belegter Engpass:** Viele Übergaben für einen einzelnen Beleg; der Prozess wird als aufwändig beschrieben.
- **Analyse – wiederverwendbares Muster:** `Belegbild → OCR/Extraktion → Kategorie-/Plausibilitätsvorschlag → menschliche Prüfung → Ablage/Export`.
- **Nicht automatisch entscheiden:** steuerliche Kategorie, Vorsteuerabzug, Aufbewahrungsfrist oder Buchungssatz ohne fachliche Kontrolle.
- **Diagnosefragen:** Welche Felder sind notwendig? Welche Belegarten sind schwer lesbar? Welches Buchhaltungs-/Steuerberaterformat wird benötigt? Wo dürfen Originale gespeichert werden?

### K-13 – Solo-Berater: Zeit wird nachträglich rekonstruiert

- **Betriebsart:** selbstständiger Berater/Auftragnehmer.
- **Primärquelle:** [Reddit: „As a contractor/consultant, how do you track your hours?“](https://www.reddit.com/r/smallbusiness/comments/no1ixt/as_a_contractorconsultant_how_do_you_track_your/)
- **Belegter Ist-Prozess:** Arbeitszeiten werden in Excel erfasst und mit einer Pivot-Tabelle ausgewertet. An vollen Tagen wird die Erfassung in Echtzeit vergessen; danach entstehen Lücken, bei denen nicht mehr klar ist, was getan wurde.
- **Belegter Engpass:** Nachträgliche Erinnerung ist eine schlechte Datenquelle für abrechenbare oder analysierbare Zeit.
- **Analyse – wiederverwendbares Muster:** `niedrigschwelliger Zeiteintrag → Zuordnung zu Kunde/Aufgabe → Tagesrückblick bei Lücke → Freigabe → Auswertung/Rechnungsgrundlage`.
- **Nicht automatisch entscheiden:** Abrechenbarkeit oder Projektzuordnung aus bloßen Kalender-/Aktivitätsdaten.
- **Diagnosefragen:** Wird minutengenau abgerechnet? Gibt es feste Projektcodes? Welche Tätigkeiten sind nicht abrechenbar? Muss der Kunde Details sehen?

### K-14 – Kleines Bekleidungslabel ohne Website nutzt Google Forms

- **Betriebsart:** Ein-Personen-Bekleidungsmarke in der Startphase.
- **Primärquelle:** [Reddit: „Keeping Track of orders“](https://www.reddit.com/r/smallbusiness/comments/1c6db7o/keeping_track_of_orders/)
- **Belegter Ist-Prozess:** Eingehende Bestellungen werden über Google Forms nachgehalten. Der Betreiber möchte eine leichter zugängliche Lösung für sich und Kunden, hat aber noch keine Website.
- **Belegter Engpass:** Ein Erfassungswerkzeug ersetzt nicht automatisch einen verständlichen Kundenweg oder ein zentrales Statusmanagement.
- **Analyse – wiederverwendbares Muster:** `Bestellformular → Validierung → Auftragsbestätigung → Zahlungs-/Fulfillmentstatus → Versandinformation`.
- **Nicht automatisch entscheiden:** Verfügbarkeit, Liefertermin oder Ersatzprodukt ohne Lager- und Produktionsdaten.
- **Diagnosefragen:** Gibt es Varianten/Größen? Wie werden Zahlungen und Versandstatus erfasst? Sind Vorbestellungen möglich? Wie oft ändern Kunden Bestellungen?

## 4. Übergreifende Prozessmuster für Retrieval

| Muster-ID | Wiederkehrendes Problem | Fälle | RAG-Labels | Typische Automation – nur nach Prüfung |
| --- | --- | --- | --- | --- |
| P-01 | Unstrukturierter Eingang | K-01, K-04, K-05 | `inquiry_intake`, `multichannel`, `manual_entry` | Nachricht klassifizieren, Pflichtfelder extrahieren, Vorgang anlegen |
| P-02 | Auftrag zu Produktion/Erfüllung | K-03, K-04, K-14 | `order_management`, `production_planning`, `status_tracking` | Positionen standardisieren, Listen aggregieren, Status sichtbar machen |
| P-03 | Termin und reale Kapazität | K-06, K-09 | `scheduling`, `capacity`, `no_show`, `field_service` | Vorschlag/Erinnerung; finale Zusage bleibt regel- oder menschlich gesteuert |
| P-04 | Zahlung und offene Posten | K-07, K-08 | `invoicing`, `payment_followup`, `cashflow` | Fälligkeiten überwachen, Entwürfe/Erinnerungen vorbereiten |
| P-05 | Personalzeit und Abrechnungsvorbereitung | K-10, K-11, K-13 | `time_tracking`, `payroll_prep`, `approval` | Zeit erfassen, plausibilisieren, zur Freigabe vorlegen |
| P-06 | Belege und Buchhaltungsvorbereitung | K-12 | `receipt_processing`, `ocr`, `expense_tracking` | Daten extrahieren und zur Prüfung ablegen |
| P-07 | Einkauf und Beschaffung | K-02 | `procurement`, `vendor_data`, `approval` | Bestellentwurf aus Bedarf und Stammdaten erzeugen |

## 5. RAG-taugliche Chunk-Struktur

Nicht die gesamte Datei als einen Vektor ablegen. Jeder Fall und jedes Prozessmuster soll getrennt chunkbar sein.

### Empfohlene Dokumenttypen

1. **`case_evidence`** – jeweils ein Fall K-01 bis K-14: nur belegter Betrieb, Ist-Prozess, Engpass und Quellenlink.
2. **`diagnostic_pattern`** – die Muster P-01 bis P-07: generalisierte, quellenübergreifende Muster ohne Branchenbehauptung.
3. **`automation_guardrail`** – Grenzen, Datenvoraussetzungen und menschliche Freigabepunkte.
4. **`interview_question_set`** – Diagnosefragen je Muster, damit die App aus der Lücke eine gezielte Rückfrage formulieren kann.

### Metadaten pro Chunk

```json
{
  "document_id": "kmuprozesstest_k01",
  "chunk_type": "case_evidence",
  "case_id": "K-01",
  "source_type": "public_first_person_forum_post",
  "source_url": "https://www.reddit.com/r/smallbusiness/comments/1ogmune/anyone_else_manually_logging_customer_emails_to_a/",
  "business_size": "unknown_micro_or_small",
  "industry": "unspecified",
  "process_tags": ["inquiry_intake", "email", "manual_entry"],
  "pain_tags": ["missed_requests", "copy_paste", "no_central_status"],
  "automation_stage": "assistive_with_human_review",
  "sensitivity": "unknown",
  "evidence_scope": "self_reported_current_process",
  "language": "de"
}
```

### Retrieval-Regeln

- Zuerst nach `process_tags`, `pain_tags`, `business_size` und `sensitivity` filtern; danach semantisch suchen.
- Ein Fall dient als **Musterbeleg**, nie als Beweis, dass dieselbe Lösung beim aktuellen Nutzer passt.
- Bei mehreren passenden Fällen soll die Antwort Gemeinsamkeiten und Unterschiede nennen, nicht Fälle vermischen.
- `automation_guardrail` immer gemeinsam mit Lösungschunks abrufen.
- Quellenlinks und die Markierung „realer Selbstbericht“ bleiben im Kontext, damit der LLM keine nicht belegten Details erfindet.

## 6. Einsatz in der AI-Start-Map-Pipeline

1. **Interview extrahieren:** Trigger, Schritte, Kanäle, Daten, Beteiligte, Frequenz, Entscheidungspunkte und Fehlerquellen als strukturiertes Prozessmodell erfassen.
2. **Lücken erkennen:** Fehlen z. B. Kapazitätsregeln, führende Datenquelle, Zahlungsabgleich oder Freigaberegeln, noch keine Lösung ausgeben.
3. **Retrieval:** Prozessmodell gegen `diagnostic_pattern` und passende `case_evidence`-Chunks suchen; dann die zugehörigen Guardrails laden.
4. **Rückfragen stellen:** Nur Fragen ausgeben, die die Eignung, das Risiko oder die Umsetzungslogik tatsächlich verändern.
5. **Empfehlung erzeugen:** Ausgangsproblem, heutiger Ablauf, kleinster sinnvoller Zielablauf, Datenvoraussetzungen, menschliche Kontrolle und Testfall transparent darstellen.
6. **Ranking:** Nutzen, Häufigkeit, Standardisierbarkeit, Datenreife, Integrationsaufwand, Datenschutz und Umfang der menschlichen Entscheidung deterministisch bewerten.

## 7. Qualitäts- und Sicherheitscheck vor einer Empfehlung

Eine Automation darf erst als belastbar eingestuft werden, wenn diese Punkte geklärt sind:

- Gibt es einen eindeutigen Trigger und einen führenden Speicherort?
- Welche Angaben sind Pflicht und wie werden fehlende Angaben behandelt?
- Welche Ausnahmen passieren real (Sonderauftrag, Storno, Teillieferung, mehrere Personen, Zahlungsstreit)?
- Was darf die Automation vorbereiten und was muss ein Mensch verbindlich entscheiden?
- Sind Personen-, Gesundheits-, Finanz- oder Beschäftigtendaten beteiligt?
- Woran wird Erfolg gemessen: weniger Nacharbeit, kürzere Durchlaufzeit, weniger Fehler, mehr bestätigte Termine oder bessere Nachverfolgbarkeit?

## 8. Priorität für die nächste Wissensausbaustufe

Diese Sammlung ergänzt die vorhandenen Fälle gut, bleibt aber überwiegend englischsprachig und forum-basiert. Für die nächste RAG-Ausbaustufe sollten zusätzlich gezielt gesammelt werden:

- deutsche Erstberichte von Solo-Selbstständigen und Handwerks-/Dienstleistungsbetrieben;
- Fälle mit vollständigem Vorher-Nachher-Verlauf und messbaren Ergebnissen;
- Fälle zu Angebotsfreigabe, Reklamationen, Mitarbeiterübergaben und wiederkehrendem Marketing;
- deutsche Rechts-/Datenschutzquellen als **separate Guardrail-Dokumente**, niemals vermischt mit Erfahrungsfällen.

