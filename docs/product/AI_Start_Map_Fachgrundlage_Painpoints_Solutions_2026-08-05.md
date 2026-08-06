# AI Start Map – Fachgrundlage für Pain Points, Reifegrad und Solution Patterns

**Status:** Active – Fachgrundlage
**Datum:** 2026-08-05
**Zweck:** Brücke von Nutzererzählung über Symptom, Ursache und Problemfamilie zur realistischen nächsten Lösung.
**Source of Truth:** Fachliche Grundlage für Pain Points, Reifegrad und Solution Patterns.
**Laufzeitstatus:** Noch keine implementierte oder integrierte Laufzeitlogik; keine Änderung an Produktionscode, Prompts, FAISS-Indizes oder Embeddings.
**RAG-Status:** Produkt- und Entscheidungsgrundlage, kein produktiver RAG-Korpus; nicht indexieren.
**Verwandte Dokumente:** `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/KNOWN_ISSUES.md`.
**Spätere Feature-Spec:** `docs/specs/solution-pattern-recommendation/`.

---

## 1. Bestandsaufnahme der verwendeten Wissensquellen

### 1.1 Tatsächlich vorhandener Bestand

| Bereich | Dateien / Inhalt | tatsächlicher Umfang | Verwendung in dieser Analyse |
|---|---|---:|---|
| `knowledge/archive/raw/` | zehn KMU-Fälle, zusätzliche KMU-Recherche, Massagesalon-Analyse und Transkript | 4 Dateien | Herkunft und Kontext prüfen; nicht direkt als fertige Taxonomie übernehmen |
| `knowledge/archive/curated/` | `ten_cases_rag_corpus.md`, `massage_rag_corpus.md`, `additional_kmu_rag_corpus.md` | 111 Chunks | Quellenbasis des bestehenden Diagnoseindex; keine neue fachliche Runtime-Quelle |
| `knowledge/evaluation/` | `cases_ten_kmu.json` | 25 Evaluationen | ausschließlich Qualitätsprüfung; niemals Produktwissen |
| Batch 02 `analog_reality` | Research-Bericht, 162 JSONL-Chunks, Quellenregister, Merge-Gate | 35 Fälle / 162 Chunks | produktives Diagnosewissen im gelieferten 634er-Index |
| Batch 03 `diagnostic_depth` | Research-Bericht, RAG-Korpus, Pattern-Katalog, Legal Guardrails, Evaluationen | 46 Fälle / 361 Chunks / 49 Patterns / 12 Guardrails | produktives Diagnosewissen; 14 Evaluationen ausgeschlossen |
| Batch 04 `agentic_interview` | Entscheidungs-, Frage-, Klärungs-, Stop-, Tool- und Guardrail-Patterns | 205 Patterns | Agentenwissen; nicht als Betriebs- oder Solution-Evidenz verwendet |
| Batch-04-Evaluation | `09_evaluation_cases.json` | 40 Evaluationen | ausschließlich Qualitätsprüfung |
| Diagnoseindex | FAISS, `chunks.json`, `manifest.json` | 634 Einträge | bestätigt: 111 + 162 + 361; `text-embedding-3-small`; Evaluationen ausgeschlossen |
| Agentenindex | FAISS, `chunks.json`, `manifest.json` | 205 Einträge | technisch vorhanden, aber laut vorliegendem Laufzeitcode nicht aktiv abgefragt |
| RAG-/Laufzeitcode | `rag_service.py`, `openai_service.py`, `agent_service.py`, `routes.py`, Schemas und Tests | wesentliche Dateien vorhanden | Analyse von Retrieval, Prompt, Validierung und Entscheidungspfaden |

Die 79 Evaluationen setzen sich aus 25 Grundkorpus-, 14 Batch-03- und 40 Batch-04-Fällen zusammen. Sie wurden nur verwendet, um erwartete Grenzen und Fehlentscheidungen zu prüfen. Ihre erwarteten Lösungen werden nicht als Beleg für die Taxonomie oder den Solution-Katalog ausgegeben.

### 1.2 Abgrenzung der Wissensarten

- **Produktives Diagnosewissen:** 634 Chunks aus Grundkorpus, Batch 02 und Batch 03. Dazu gehören Quellenfälle, diagnostische Muster, Prozessmuster, Fragen, Minimalverbesserungen, Automationsmuster, Reifegradmuster, Voraussetzungen und Guardrails.
- **Agentenwissen:** 205 Batch-04-Patterns für `ASK`, `CLARIFY`, `RETRIEVE`, `ANALYZE`, `STOP`, Fragenwahl, Widerspruchsprüfung, Stop-Regeln, Tool-Auswahl und Agenten-Guardrails.
- **Evaluation:** 79 strikt ausgeschlossene Testfälle. Sie prüfen das System, dürfen ihm aber keine Lösung vorsagen.
- **Nutzerfakten:** stammen ausschließlich aus der jeweiligen Nutzererzählung. Weder Quellenfälle noch Patterns dürfen fehlende Details eines Betriebs ergänzen.

### 1.3 Gefundene Inkonsistenzen und fehlende Daten

1. `knowledge/README.md` bezeichnet Batch 02–04 noch als nicht indexiert. Die gelieferten Manifeste und `chunks.json`-Dateien belegen dagegen einen Diagnoseindex mit 634 und einen Agentenindex mit 205 Einträgen. Die README ist daher nicht mehr auf dem aktuellen Laufzeitstand.
2. Der Hausmeister-Testfall mit Sprachnachricht, Fotos und Bon stammt aus dem Projektkontext, ist aber nicht als eigener Quellenfall mit stabiler Chunk-ID im Diagnosekorpus vorhanden. Verwandte Evidenz existiert in `C-01`, `C-07`, `K-12`, `RB03-C22`, `RB03-C25`, `RB03-C26`, `RB03-C45` sowie `RB03-P10` und `RB03-P12`.
3. Für einen klassischen lokalen Schuhmacher mit Papierzettel, Regalplatz und Drittabholung fehlt laut Batch-03-Merge-Gate ein vollständiges Vor-Ort-Primärinterview. `RB03-C01` belegt einen realen deutschen Versand-Reparaturprozess, aber nicht jedes angenommene analoge Detail.
4. Die vorhandenen `automation_pattern`-Chunks haben kein einheitliches, maschinenlesbares Solution-Pattern-Schema. Teilweise sind drei Lösungen in einem langen Chunk gebündelt; Batch 02 und 03 verwenden andere Felder.
5. Digitale Reife, organisatorische Prozessreife und Eignung eines vorhandenen Kanals werden teilweise in einem einzigen Reifegrad vermischt. Das ist für die Empfehlung nicht ausreichend.

---

## 2. Executive Summary

Das Korpus trägt eine belastbare Taxonomie mit **zwölf wiederkehrenden Problemfamilien**. Die wichtigste Erkenntnis lautet: Die richtige nächste Lösung hängt nicht von einer pauschalen Digitalisierungsstufe ab, sondern von fünf Entscheidungsfragen:

1. Gibt es einen stabilen Anker für den Vorgang – etwa Auftrag, Kunde, Objekt, Standort oder Datum?
2. Entstehen die benötigten Informationen bereits in einem nutzbaren Kanal – etwa Smartphone, E-Mail, Formular, Foto oder Sprache?
3. Sind Pflichtangaben, Status und Verantwortlichkeit ausreichend klar?
4. Wie schwer wäre eine Fehlzuordnung oder Fehlentscheidung?
5. Muss ein Mensch Preis, Termin, Leistung, Qualität, Zahlung, Sicherheit oder Herausgabe freigeben?

Damit ist „Ordnung vor Automatisierung“ keine starre Treppe. **Ordnung ist nur dort zwingend vorgeschaltet, wo Identität, physischer Ort, Zuständigkeit oder Freigabe nicht zuverlässig feststehen.** KI-Unterstützung kann dagegen früh sinnvoll sein, wenn sie unstrukturierte, bereits digital entstehende Informationen in einen prüfbaren Entwurf umwandelt. Genau das gilt für den Hausmeisterfall: Sprache, Fotos und Bon sind schon digital vorhanden; notwendig ist kein zusätzlicher Papierordner, sondern ein gemeinsamer mobiler Eingang mit einer eindeutigen Einsatzzuordnung und menschlicher Bestätigung.

Die derzeit zu defensiven Empfehlungen entstehen nicht primär aus einer falschen Diagnose. Die wahrscheinliche Fehlerkette ist:

```text
richtiger Engpass
→ Reifegrad und Kanaleignung nicht getrennt
→ defensive Minimalverbesserung wird abgerufen
→ kein konkretes Solution Pattern ist im Retrieval zwingend
→ Prompt erlaubt Ordnung als erste Lösung
→ generische oder analoge Empfehlung
```

Für die nächste Produktstufe braucht AI Start Map daher vier getrennte Komponenten:

- eine deterministische Entscheidungsschicht für harte Voraussetzungen und Freigabegrenzen,
- Diagnose-RAG für Vergleichswissen, Ursachen, Risiken und entscheidungsrelevante Fragen,
- einen kleinen strukturierten Solution-Katalog für konkrete Zielabläufe,
- Evaluationen, die Diagnose, Lösungsfit, Kundensprache und Überautomatisierung getrennt messen.

---

## 3. Pain-Point-Taxonomie

### PF-01 – Vorgangsbezogene Informationen sind über mehrere Kanäle verteilt

- **Definition:** Angaben, Medien und Entscheidungen zu demselben Auftrag liegen in Chats, E-Mail, Fotos, Notizen, Tabellen, Papier oder im Gedächtnis, ohne gemeinsamen Vorgangsanker.
- **Typische Unternehmeraussagen:** „Ich muss alles zusammensuchen.“ „Ein Teil steht in WhatsApp, der Rest in den Fotos.“ „Ich weiß nicht, was der aktuelle Stand ist.“
- **Symptome:** Suche vor Angebot oder Rechnung; fehlende Anhänge; widersprüchliche Stände; Rückfragen; verspäteter Abschluss.
- **Häufige Ursachen:** kein gemeinsamer Auftragsschlüssel; persönliche Konten; mehrere parallele Ablagen; Medien werden unabhängig gespeichert.
- **Prozesse:** Anfrage, Auftrag, Außeneinsatz, Inspektion, Angebot, Reklamation, Rechnung.
- **Branchen:** Handwerk, Außendienst, Social-Commerce, Hausverwaltung, Reparatur, Beratung.
- **Kanäle/Werkzeuge:** WhatsApp, Instagram, E-Mail, Smartphone-Fotos, Notizen, Papier, Tabellen.
- **Digitaler Ausgangszustand:** häufig bereits teilweise digital, aber nicht vorgangsbezogen verbunden.
- **Folgen:** Suchzeit, vergessene Leistungen, fehlerhafte Übergaben, verspätete Rechnung, Inhaberabhängigkeit.
- **Abgrenzung:** PF-03 betrifft die wiederholte Übertragung; PF-04 den fehlenden Status; PF-05 physische Objekte und Orte.
- **Belege:** `K-04_case_evidence`, `K-05_case_evidence`, `K-12_case_evidence`, `C-01_case_evidence`, `RB02-C14-E01`, `RB03-C41-01`, `RB03-C45-01`, `RB03-P12`.
- **Sicherheit:** hoch.

### PF-02 – Eingehende Anfragen werden nicht zuverlässig erfasst und qualifiziert

- **Definition:** Neue Anfragen kommen über mehrere oder unterbrechende Kanäle und werden nicht zuverlässig zu einem prüfbaren Vorgang mit Mindestinformationen.
- **Typische Aussagen:** „Ich verliere E-Mails.“ „Kunden rufen trotzdem an.“ „DMs gehen unter.“ „Ich beantworte dieselben Fragen immer wieder.“
- **Symptome:** verpasste Leads, doppelte Bearbeitung, Rückrufstapel, unvollständige Anfragen, langsame Reaktion.
- **Ursachen:** Postfach oder persönliches Telefon dient als Aufgabenliste; keine Deduplizierung; Pflichtangaben fehlen; ungeeignete Selbstbuchung.
- **Prozesse:** Lead-to-order, Serviceanfrage, Rechts-/Praxisintake, Reparaturannahme, Support.
- **Branchen:** Solo-Kanzlei, Reparatur, Social-Commerce, Dienstleistung, Salon, Hausgeräte-Service.
- **Kanäle:** E-Mail, Telefon, Webformular, WhatsApp, Instagram, persönliches Handy.
- **Digitaler Ausgangszustand:** digitaler Kanal ist oft vorhanden, aber noch kein verlässliches Vorgangsregister.
- **Folgen:** Umsatzverlust, Unterbrechungen, unklare Priorität, unnötige Rückfragen.
- **Abgrenzung:** PF-01 umfasst Medien innerhalb eines bestehenden Vorgangs; PF-02 betrifft den Übergang von Kontakt zu belastbarem Vorgang.
- **Belege:** `K-01_case_evidence`, `K-04_case_evidence`, `C-06_case_evidence`, `C-08_case_evidence`, `RB02-C15-E01`, `RB02-C33-E01`, `RB03-PP04`.
- **Sicherheit:** hoch.

### PF-03 – Daten werden mehrfach übertragen oder abgeschrieben

- **Definition:** Dieselbe Information wird aus Nachricht, Dokument, Papier oder Fachsystem manuell in eine andere Liste oder Anwendung übertragen.
- **Typische Aussagen:** „Ich kopiere jede Bestellung in Excel.“ „Nach dem Einsatz tippe ich alles noch einmal ab.“ „Ich suche die Position und übernehme sie ins Angebot.“
- **Symptome:** Copy-paste, Mehrfacheingabe, Tippfehler, Rückstände, unterschiedliche Versionen.
- **Ursachen:** fehlende Schnittstelle; keine strukturierte Erfassung am Ursprung; unklare führende Quelle; Dokumente ohne einheitliche Felder.
- **Prozesse:** Bestellung, Angebot, Produktionsliste, Rechnung, Belegverarbeitung, Lohnvorbereitung.
- **Branchen:** Bäckerei, Werkstatt, Beschaffung, Fertigung, Dienstleistungen, Handel.
- **Kanäle/Werkzeuge:** PDF, E-Mail, Papier, Tabellen, Buchhaltung, Projektsoftware.
- **Digitaler Ausgangszustand:** meist digital fragmentiert oder analog-digital gemischt.
- **Folgen:** Zeitverlust, Fehler, veraltete Daten, verzögerte Bearbeitung.
- **Abgrenzung:** PF-01 ist Verteilung; PF-03 ist der konkrete Übertragungsaufwand zwischen Quellen.
- **Belege:** `K-02_case_evidence`, `K-03_case_evidence`, `K-12_case_evidence`, `C-09_case_evidence`, `RB02-C11-E01`, `RB02-C13-E01`, `RB02-C26-E01`, `RB03-P16`.
- **Sicherheit:** hoch.

### PF-04 – Aufträge, Übergaben und offene Schritte haben keinen verlässlichen Status

- **Definition:** Es ist nicht sichtbar, in welcher Phase ein Vorgang steht, wer als Nächstes handelt und welche Ausnahme ihn blockiert.
- **Typische Aussagen:** „Ich verliere den Überblick.“ „Ich weiß nicht, ob das schon erledigt ist.“ „Alles hängt am Zettel oder an mir.“
- **Symptome:** vergessene Arbeit, Rückfragen, Doppelarbeit, verspätete Lieferung, unklare Vertretung.
- **Ursachen:** Status nur im Kopf, Papier oder Chat; zu viele Statuswerte; Status wird nicht am realen Ereignis aktualisiert; keine Verantwortlichkeit.
- **Prozesse:** Reparatur, Produktion, Service, Bestellung, Kundenabholung, Reklamation.
- **Branchen:** Werkstätten, Druck, Textil, Eventvermietung, Handel, mobile Dienste.
- **Kanäle/Werkzeuge:** Papierkarte, physische Zone, Board, Tabellen, Chat, Fachsoftware.
- **Digitaler Ausgangszustand:** reicht von analog bis zu mehreren unverbundenen Tools.
- **Folgen:** Durchlaufzeit, Qualitätsfehler, Kundenrückfragen, Inhaberabhängigkeit.
- **Abgrenzung:** PF-05 fragt „welches Objekt und wo?“; PF-04 fragt „welcher Bearbeitungsstand und wer handelt?“
- **Belege:** `C-02_case_evidence`, `C-10_case_evidence`, `RB02-C02-E01`, `RB02-C05-E01`, `RB03-C44-01`, `RB03-P05`, `RB03-IP03`.
- **Sicherheit:** hoch.

### PF-05 – Physischer Gegenstand, Auftrag und Ablageort sind nicht stabil verbunden

- **Definition:** Ein reales Objekt kann nicht zweifelsfrei dem richtigen Auftrag, Kunden, Status oder physischen Ort zugeordnet werden.
- **Typische Aussagen:** „Der Zettel ist weg.“ „Ich finde den Gegenstand nicht.“ „Im System steht abgeholt, aber er liegt noch hier.“
- **Symptome:** verlorene Objekte, falsche Herausgabe, lange Suche, Orts-/Statuskonflikt, unklare Drittabholung.
- **Ursachen:** Kennung nur auf losem Zettel; kein zweites Suchmerkmal; kein belegbarer Regal-/Zonenort; Status ohne reales Ereignis.
- **Prozesse:** Reparaturannahme, Reinigung, Vermietung, Abholung, Lagerung.
- **Branchen:** Schuh-, Fahrrad-, Handy- und Kfz-Reparatur, Teppichreinigung, Änderungsschneiderei, Eventvermietung.
- **Kanäle/Werkzeuge:** Anhänger, Ticket, Regal, Fach, Stange, Zone, Auftragssystem.
- **Digitaler Ausgangszustand:** unabhängig vom Digitalgrad zwingend an physische Kennzeichnung gekoppelt.
- **Folgen:** Haftung, Kundenvertrauen, Suchzeit, falsche Herausgabe, gebundener Platz.
- **Abgrenzung:** PF-04 betrifft Bearbeitungsstatus; PF-05 die überprüfbare Identität und physische Wahrheit.
- **Belege:** `RB02-C01-E01`, `RB02-C02-E01`, `C-10_case_evidence`, `RB03-C01-01` bis `RB03-C01-06`, `RB03-P01` bis `RB03-P05`, `RB03-IP05`.
- **Sicherheit:** hoch für die Problemfamilie; mittel für den speziellen lokalen Schuhmacherablauf.

### PF-06 – Termine und Kapazitäten werden ohne reale Constraints koordiniert

- **Definition:** Termin- oder Lieferzusagen berücksichtigen Personal, Qualifikation, Ort, Weg, Material, Dauer oder Ausnahmen nicht zuverlässig.
- **Typische Aussagen:** „Der Kalender zeigt frei, aber ich habe niemanden.“ „Fahrzeiten passen nicht.“ „Ich kann die Buchung erst manuell bestätigen.“
- **Symptome:** Doppelbuchung, Ablehnung trotz Nachfrage, Leerlauf, Überlastung, manuelle Umplanung.
- **Ursachen:** Kalender bildet nur Zeitfenster ab; wechselnde Personalverfügbarkeit; Mehrpersonenleistung; geografische oder materielle Constraints fehlen.
- **Prozesse:** Terminbuchung, Disposition, Touren, Personalplanung, Liefertermin.
- **Branchen:** Massage, Reinigung, mobile Hundepflege, Fahrschule, Außendienst, Fertigung.
- **Kanäle/Werkzeuge:** Papierkalender, Onlinebuchung, WhatsApp, Telefon, Planungssoftware.
- **Digitaler Ausgangszustand:** häufig digitale Buchung, aber unvollständiges Kapazitätsmodell.
- **Folgen:** Kundenfrust, Kulanz, Umsatzverlust, Überstunden, unproduktive Zeit.
- **Abgrenzung:** PF-02 betrifft vollständige Anfrageerfassung; PF-06 die Machbarkeit einer Zusage.
- **Belege:** `M-01_appointment_capacity_evidence`, `M-01_staff_planning_evidence`, `K-06_case_evidence`, `C-03_case_evidence`, `RB02-C16-E01`, `RB02-C20-E01`, `RB03-P13`, `RB03-PP05`.
- **Sicherheit:** hoch.

### PF-07 – Änderungen, Zusatzarbeit und Freigaben blockieren oder entkoppeln den Prozess

- **Definition:** Ein Vorgang ändert sich nach Annahme; Befund, Preis, Version und Zustimmung bleiben nicht als zusammenhängender Freigabeschritt dokumentiert.
- **Typische Aussagen:** „Der Aufwand war höher.“ „Der Kunde hat etwas geändert.“ „Die alte Version war noch in der Werkstatt.“
- **Symptome:** Arbeit ohne Freigabe, Preisstreit, falsche Version, Produktionsstopp, fehlende Rechnungsposten.
- **Ursachen:** freie Wünsche ohne Spezifikation; Freigabe über separaten Kanal; kein Änderungsprotokoll; kein Arbeitsstopp bei Abweichung.
- **Prozesse:** Reparatur, individuelles Angebot, Druck/Fertigung, Zusatzschaden, Kundenabnahme.
- **Branchen:** Werkstatt, Schuhreparatur, Textildruck, Möbelbau, technische Dienste.
- **Kanäle/Werkzeuge:** E-Mail, Chat, Papier, Angebot, Foto, Signatur, Produktionsunterlage.
- **Digitaler Ausgangszustand:** häufig digital vorhanden, aber Version und Zustimmung nicht gekoppelt.
- **Folgen:** Marge, Haftung, Nacharbeit, Kundenkonflikt, Umsatzverlust.
- **Abgrenzung:** PF-04 betrifft normalen Status; PF-07 den kontrollierten Ausnahme- und Entscheidungsweg.
- **Belege:** `C-09_automation_patterns`, `RB03-C01-03`, `RB03-C35-01`, `RB03-C46-01`, `RB03-P06`, `RB03-P14`, `RB03-IP07`, `RB03-IP09`.
- **Sicherheit:** hoch.

### PF-08 – Außendienstnachweise erreichen Rechnung und Büro nicht vollständig

- **Definition:** Zeit, Material, Fotos, Beleg, Abnahme und Zusatzarbeit entstehen im Einsatz, gelangen aber verspätet, unvollständig oder unverbunden zur Rechnungsvorbereitung.
- **Typische Aussagen:** „Ich suche vor der Rechnung alles zusammen.“ „Der Zettel kommt erst später ins Büro.“ „Material und Foto liegen getrennt.“
- **Symptome:** verspätete Rechnung, vergessene Positionen, unvollständiger Nachweis, Rückfahrt ins Büro, Streit über Leistung.
- **Ursachen:** kein gemeinsamer Einsatzdatensatz; Erfassung erst nachträglich; ungeeignete mobile Oberfläche; Netz-/Umgebungsprobleme; keine Bestätigung.
- **Prozesse:** Einsatz, Wartung, Inspektion, Reparatur, Abnahme, Rechnungsgrundlage.
- **Branchen:** Hausmeister, Monteure, HVAC, mobile Kfz-Reparatur, Reinigung, Hausverwaltung.
- **Kanäle/Werkzeuge:** Smartphone, Sprache, Fotos, Papier, Bon, Unterschrift, Tabellen.
- **Digitaler Ausgangszustand:** oft smartphonefähig; Prozessverknüpfung fehlt.
- **Folgen:** Liquiditätsverzögerung, Umsatzverlust, Suchzeit, schlechter Kundennachweis.
- **Abgrenzung:** PF-01 ist allgemeine Informationsverteilung; PF-08 ist der konkrete Übergang vom Feld zur abrechenbaren Leistung.
- **Belege:** `C-01_automation_patterns`, `C-07_automation_patterns`, `K-12_case_evidence`, `RB03-C26-01` bis `RB03-C26-06`, `RB03-C45-01` bis `RB03-C45-06`, `RB03-P10`, `RB03-P12`, `RB03-PP02`.
- **Sicherheit:** hoch.

### PF-09 – Zahlung, Beleg und offener Vorgang werden nicht zuverlässig abgeglichen

- **Definition:** Rechnung, Zahlung, Beleg, Fälligkeit und Ausnahme liegen getrennt oder erfordern manuelles Nachfassen.
- **Typische Aussagen:** „Ich vergesse Erinnerungen.“ „Ich muss Zahlungen manuell prüfen.“ „Der Bon ist da, aber nicht dem Auftrag zugeordnet.“
- **Symptome:** verspätete Zahlung, fehlender Beleg, falscher offener Status, wiederkehrende manuelle Erinnerung.
- **Ursachen:** keine eindeutige Zuordnung; mehrere Zahlungswege; Fälligkeit nicht als Aufgabe; Originalbeleg und extrahierte Daten nicht getrennt.
- **Prozesse:** Rechnung, Zahlungseingang, Belegverarbeitung, Mahnung, Jobkosten.
- **Branchen:** Reinigung, Salon, Sanitär, Reparatur, kleine Praxen, Handel.
- **Kanäle/Werkzeuge:** Bargeld, Überweisung, PayPal, E-Mail, Foto, Buchhaltung, Tabellen.
- **Digitaler Ausgangszustand:** gemischt; häufig digitale Zahlung plus manueller Abgleich.
- **Folgen:** Liquidität, Steuer-/Nachweislücke, Verwaltungsaufwand, Kundenkonflikt.
- **Abgrenzung:** PF-08 erzeugt die Rechnungsgrundlage; PF-09 beginnt bei Beleg, Rechnung, Zahlung und Nachverfolgung.
- **Belege:** `K-07_case_evidence`, `K-08_case_evidence`, `K-12_case_evidence`, `M-01_payment_receipts_evidence`, `RB02-C28-E01`, `RB03-PP08`, `RB03-L08`.
- **Sicherheit:** hoch.

### PF-10 – Material, Bestand, Charge oder Produktionsfortschritt sind nicht rückverfolgbar

- **Definition:** Materialbedarf, Bestand, Charge, Variante, Zwischenstufe und Auftrag sind nicht konsistent verbunden.
- **Typische Aussagen:** „Ich weiß nicht, in welcher Stufe der Auftrag ist.“ „Der Bestand stimmt nicht.“ „Die Variante verbraucht andere Teile.“
- **Symptome:** Fehlteile, falsche Zusage, WIP-Verlust, Nachkalkulationsfehler, unklare Charge.
- **Ursachen:** fehlende Stückliste oder Variantenlogik; manuelle Bestandsabgänge; getrennte Systeme; Prozessstufen nicht sichtbar.
- **Prozesse:** Beschaffung, Fertigung, Kommissionierung, Produktionsauftrag, Qualität, Versand.
- **Branchen:** Textil, Lebensmittel, Druck, kleine Fertigung, Lager, 3D-Druck.
- **Kanäle/Werkzeuge:** Sheets, QuickBooks, Shopify, Papierjobtaschen, Fotos, Fachsoftware.
- **Digitaler Ausgangszustand:** oft digital, aber fachlich unpassend oder fragmentiert.
- **Folgen:** Lieferverzug, Qualitätsfehler, Kapitalbindung, falsche Kosten, Compliance-Risiken.
- **Abgrenzung:** PF-05 verfolgt ein individuelles physisches Kundenobjekt; PF-10 verfolgt Material, Bestand und Produktionszustand.
- **Belege:** `C-02_case_evidence`, `RB02-C08-E01` bis `RB02-C12-E01`, `RB02-C14-E01`, `RB03-C40-01`, `RB03-PP03`, `RB03-PP06`.
- **Sicherheit:** hoch.

### PF-11 – Inhaber oder Einzelperson ist der einzige Wissens- und Koordinationspunkt

- **Definition:** Telefon, Priorisierung, Kundenwissen, Planung, Ausnahmen und Abrechnung sind an eine Person gebunden und nicht vertretbar.
- **Typische Aussagen:** „Ohne mich geht nichts.“ „Alles läuft über mein privates Handy.“ „Wenn jemand geht, geht das Kundenwissen mit.“
- **Symptome:** dauernde Unterbrechung, lange Arbeitstage, Ausfallrisiko, schlechte Übergabe, Wachstumsgrenze.
- **Ursachen:** persönliche Kanäle; Entscheidungen nicht dokumentiert; kein gemeinsamer Status; Wissen im Gedächtnis.
- **Prozesse:** Anfrage, Disposition, Kundenbeziehung, Ausnahme, Abrechnung, Personalübergabe.
- **Branchen:** fast alle Solo-/Mikrobetriebe; besonders Handwerk, Handel, Reparatur und Verwaltung.
- **Kanäle/Werkzeuge:** privates Telefon, WhatsApp, Gedächtnis, Einzeldateien, Papier.
- **Digitaler Ausgangszustand:** kann hoch oder niedrig sein; das Problem ist Eigentum und Zugriff, nicht nur Technik.
- **Folgen:** Überlastung, fehlende Vertretbarkeit, verlorenes Wissen, begrenztes Wachstum.
- **Abgrenzung:** PF-04 ist fehlender Vorgangsstatus; PF-11 ist die organisatorische Abhängigkeit von einer Person.
- **Belege:** `RB02-C29-E01`, `RB02-C32-E01`, `RB02-C33-E01`, `RB03-C22-01`, `RB03-C28-01`, `RB03-C42-01`, `RB03-P15`, `RB03-PP10`.
- **Sicherheit:** hoch.

### PF-12 – Eingehende Dokumente und freie Texte werden nicht zu prüfbaren Datensätzen

- **Definition:** PDF, E-Mail, Formular, Bon, Diktat oder freie Nachricht enthalten benötigte Angaben, die manuell gelesen, übertragen und geprüft werden.
- **Typische Aussagen:** „Jedes PDF sieht anders aus.“ „Ich tippe die Daten aus dem Bon ab.“ „Aus dem Diktat muss ich später einen Bericht schreiben.“
- **Symptome:** manuelle Extraktion, fehlende Pflichtfelder, Übertragungsfehler, lange Dokumentbearbeitung.
- **Ursachen:** unstrukturierter Eingang; variierende Formate; kein Ziel-Schema; keine Unsicherheitsmarkierung und Bestätigung.
- **Prozesse:** Auftragseingang, Beleg, Bericht, Angebot, Bestellung, Datenübernahme.
- **Branchen:** Schilderhersteller, Hausverwaltung, Handwerk, Buchhaltung, Fertigung.
- **Kanäle/Werkzeuge:** PDF, OCR-fähiges Foto, E-Mail, Sprache, Formular.
- **Digitaler Ausgangszustand:** digitaler Rohinhalt ist vorhanden; strukturierte, bestätigte Daten fehlen.
- **Folgen:** Zeitverlust, Fehler, unvollständige Vorgänge, falsche Folgeaktionen.
- **Abgrenzung:** PF-03 beschreibt den Medienbruch; PF-12 die fachliche Aufgabe, Inhalte zu erkennen, zu strukturieren und mit Unsicherheit zu prüfen.
- **Belege:** `RB02-C26-E01`, `K-12_automation_pattern`, `C-07_automation_patterns`, `RB03-C26-05`, `RB03-C32-01`, `RB03-C41-01`.
- **Sicherheit:** hoch.

---

## 4. Symptom–Ursache–Problemfamilien-Matrix

| sichtbares Symptom | wahrscheinliche Ursache | Problemfamilie | entscheidungsrelevante Rückfrage | Konsequenz für die Empfehlung |
|---|---|---|---|---|
| Fotos, Notizen und Belege müssen vor der Rechnung gesucht werden | Medien besitzen keinen gemeinsamen Einsatzanker | PF-01 / PF-08 | Woran kann ein Einsatz heute eindeutig erkannt werden: Auftrag, Kunde, Objekt und Datum? | Bei stabilem Anker direkt mobiler KI-Eingang; ohne Anker zuerst minimale Einsatz-ID |
| Kunden-E-Mails oder DMs gehen unter | Kommunikationskanal dient zugleich als Aufgabenliste | PF-02 | Wird jede relevante Anfrage heute als eigener Vorgang bestätigt? | Gemeinsamer Anfrageeingang mit Status und Missing-Info-Prüfung |
| Daten werden aus PDF oder Nachricht in mehrere Systeme kopiert | kein strukturiertes Zielschema oder keine geprüfte Übergabe | PF-03 / PF-12 | Welche Felder werden wirklich benötigt und welches System ist führend? | Extraktionsentwurf plus Bestätigung; erst später Übertragung automatisieren |
| Niemand weiß, ob ein Auftrag fertig, blockiert oder abgeholt ist | Status wird nicht am realen Ereignis geführt | PF-04 | Welche wenigen Ereignisse ändern den Status und wer bestätigt sie? | Statuskarte mit Verantwortlichem; Benachrichtigung erst nach bestätigtem Ereignis |
| Gegenstand ist nicht auffindbar oder falsch zugeordnet | Kennung fehlt direkt am Objekt bzw. Ortswechsel wird nicht erfasst | PF-05 | Welche Kennung steht am Gegenstand und welcher reale Ort wird dokumentiert? | Objekt-ID und Standort zwingend vor KI oder Automatisierung |
| Onlinekalender ist frei, Leistung kann aber nicht erbracht werden | relevante Kapazitätsconstraints fehlen | PF-06 | Welche Information kann eine Zusage noch verhindern: Personal, Qualifikation, Ort, Dauer, Material? | Anfrage statt Auto-Zusage; Planvorschlag mit menschlicher Bestätigung |
| Zusatzarbeit wird gemacht, aber nicht freigegeben oder berechnet | Befund, Preisänderung und Zustimmung sind getrennt | PF-07 | Bei welchem Ereignis muss Arbeit stoppen und wer darf freigeben? | dokumentierter Änderungs- und Freigabeschritt; keine autonome Entscheidung |
| Papiernachweis erreicht das Büro spät | Erfassung ist nicht am Arbeitsort nutzbar | PF-08 | Ist Smartphone/Offline-Erfassung im realen Umfeld praktikabel? | mobile Erfassung, sonst robustes Papier mit ID und späterer geprüfter Übernahme |
| Fällige Rechnungen werden vergessen | Zahlungseingang und offene Aufgabe werden nicht verknüpft | PF-09 | Welche Quelle zeigt verbindlich Rechnung, Fälligkeit und Zahlung? | Abgleichliste und Erinnerungsentwurf; Versand/Eskalation menschlich freigeben |
| Bestand stimmt nicht oder WIP ist unsichtbar | Verbrauch, Variante und Produktionsstufe sind nicht auftragsbezogen gebucht | PF-10 | Welche Bewegung verändert Bestand oder Status und wer bestätigt sie? | wenige kontrollierte Buchungsereignisse vor Forecast oder KI-Vorschlag |
| Betrieb stoppt bei Abwesenheit einer Person | Wissen, Kanal und Entscheidungen sind personengebunden | PF-11 | Was kann niemand zuverlässig übernehmen, wenn diese Person morgen fehlt? | gemeinsamer Eingang, Status, Entscheidungsnotiz und Vertretungsregel |
| Freie Texte/Diktate müssen später in Berichte umgeschrieben werden | unstrukturierter Inhalt wird nicht in ein geprüftes Schema überführt | PF-12 | Welche Zielfelder sind Pflicht und welche Fehler wären kritisch? | KI erstellt Entwurf und markiert Unsicherheit; Mensch bestätigt vor Folgeaktion |

Eine Rückfrage ist nur dann sinnvoll, wenn unterschiedliche Antworten zu unterschiedlichen Wegen führen. „Wie oft passiert das?“ hilft bei der Priorität. „Gibt es einen stabilen Einsatzanker?“ verändert unmittelbar die Lösungsstufe. Eine Frage nach zusätzlichen Details ohne Einfluss auf Diagnose, Freigabe oder Lösung wird nicht gestellt.

---

## 5. Reifegrad- und Entscheidungsmodell

### 5.1 Vier Ebenen

| Ebene | Bedeutung | notwendig, wenn | Voraussetzungen | typische Maßnahmen | gehört nicht dazu | kann übersprungen werden, wenn | muss vorgeschaltet werden, wenn | Risiken |
|---|---|---|---|---|---|---|---|---|
| **1 Ordnung** | Vorgang, Objekt, Status, Verantwortung und Freigabe sind in der realen Arbeit eindeutig | Identität, physischer Ort, Pflichtfeld oder Zuständigkeit fehlen | keine Technik nötig; Regeln müssen im Alltag ausführbar sein | ID, wenige Pflichtfelder, Zonen, Statusauslöser, Verantwortlicher, Fallback | vollständige Prozessdokumentation, neue Ordner um ihrer selbst willen, Softwareauswahl | der vorhandene digitale Kanal bereits einen eindeutigen Vorgang erzeugt und Zuordnung zuverlässig ist | physisches Objekt sonst verloren/falsch herausgegeben würde; Preis/Freigabe unklar ist; Daten keiner Quelle gehören | Bürokratie, Akzeptanzverlust, Ordnung als Selbstzweck |
| **2 Digitalisierung** | Ein verbindlicher Datensatz ist zentral auffindbar und am Arbeitsort nutzbar | Papier/Chat/Gedächtnis keine verlässliche gemeinsame Sicht bieten | stabiler Anker, minimale Felder, Zugriffs- und Korrekturregel | mobiles Formular, gemeinsame Auftragskarte, Statusliste, Scan/Foto mit Zuordnung | KI-Deutung, autonome Entscheidung, zwangsläufig papierlos | ein vorhandener digitaler Kanal direkt in einen bestätigten Datensatz überführt werden kann | Folgeautomation auf Status/Daten zugreifen soll | falsche Daten werden schneller verteilt; ungeeignete Oberfläche |
| **3 KI-Unterstützung** | KI wandelt freie Sprache, Texte oder Bilder in einen prüfbaren Entwurf, sucht Wissen oder macht Vorschläge | Informationen unstrukturiert, aber digital verfügbar sind; menschliche Prüfung möglich ist | eindeutiger Zielvorgang, Zielschema, Unsicherheitsanzeige, Datenschutz, Human Check | Diktat strukturieren, Bonfelder vorschlagen, Anfrage zusammenfassen, Bericht/Angebot entwerfen, Ausnahmen markieren | Preis-, Sicherheits-, Vertrags-, Personal- oder Herausgabeentscheidung; ungeprüfte Verbuchung | Stufe 2 kann teilweise parallel entstehen, wenn KI selbst den ersten strukturierten Entwurf erzeugt und der Nutzer ihn bestätigt | ohne stabilen Anker eine Fehlzuordnung wahrscheinlich ist oder das Ergebnis sofort irreversibel weiterläuft | Halluzination, Fehlzuordnung, zu viel Vertrauen, sensible Daten |
| **4 Automatisierung** | Bestätigte Ereignisse lösen regelbasierte Folgeaktionen aus; KI kann vorbereiten, Regeln steuern den Ablauf | wiederholbare Schritte, stabile Daten und klare Ausnahmen bestehen | System of Record, erlaubte Trigger, Fehlerpfad, Monitoring, Audit, Freigabegrenze | nach bestätigter Einsatznotiz Rechnungsentwurf anlegen; Statusmeldung nach Fertigfreigabe; Fälligkeit in Arbeitsliste setzen | autonome Hochrisikoentscheidung; Vollautomation ohne Ausnahmeweg | nicht sinnvoll zu überspringen; sie setzt mindestens lokale Ordnung und verlässliche digitale Zustände voraus | immer bei extern wirksamen Folgeaktionen | Kaskadenfehler, falscher Versand, stille Schnittstellenfehler, Kontrollverlust |

### 5.2 Das eigentliche Entscheidungsmodell

Die vier Ebenen sind kein linearer Digitalisierungslehrplan. Die Auswahl erfolgt über Gates:

1. **Anker-Gate:** Kann jeder Vorgang eindeutig an Auftrag, Kunde, Objekt, Standort oder Datum gebunden werden?
   - Nein: minimale Ordnung ist zwingend.
   - Ja: direkt Kanaleignung prüfen.
2. **Kanal-Gate:** Entstehen die Informationen bereits digital und am Arbeitsort nutzbar?
   - Ja: KI-Unterstützung kann direkt sinnvoll sein.
   - Nein: digitale oder robuste analoge Erfassung wählen.
3. **Struktur-Gate:** Sind die wenigen Zielfelder bekannt?
   - Nein: zunächst Minimalfelder durch reale Fälle bestimmen.
   - Ja: Entwurf/Extraktion möglich.
4. **Risiko-Gate:** Welche Folge hätte ein falsches Feld?
   - Niedrig und reversibel: KI-Vorschlag mit schneller Bestätigung.
   - Hoch oder extern wirksam: starke Prüfung; keine autonome Aktion.
5. **Regel-Gate:** Ist der Folgeschritt deterministisch und gibt es einen Ausnahmeweg?
   - Nein: nur Vorschlag.
   - Ja: nach bestätigtem Trigger automatisierbar.

### 5.3 Prüfentscheidungen an den vorhandenen Fällen

- **Hausmeisterservice:** Sprache, Fotos und Bon entstehen bereits auf dem Smartphone. Der Kanal ist geeignet. Zwingend ist nur ein leichter Einsatzanker, etwa Kunde + Objekt + Datum oder Auftragsnummer. Danach ist Stufe 3 direkt möglich: KI erstellt die Einsatznotiz, der Nutzer bestätigt. Ein manueller Album-/Umschlag-Zwischenschritt ist nicht erforderlich.
- **Schuhreparatur:** Die KI kann Sonderwünsche strukturieren und Statusmeldungen vorbereiten. Wenn aber Paar, Auftrag und Regalplatz nicht sicher verbunden sind, müssen Objekt-ID und physischer Ort zuerst gelöst werden. Stufe 1 ist hier für die physische Wahrheit zwingend.
- **Massagesalon:** Digitale Anfragekanäle sind vorhanden. Das Kernproblem ist nicht fehlende Digitalisierung, sondern unstabile Personal-/Kapazitätsinformation. KI kann Anfragen vereinheitlichen; eine verbindliche Terminbestätigung bleibt bei der Inhaberin, bis Kapazitätsregeln belastbar sind.
- **HVAC-Fall `RB03-C26`:** Bei vorhandenem Smartphone ist ein Offline-Minimalformular oder Foto/OCR mit Bestätigung möglich. Bei schmutziger Umgebung, leerem Telefon oder Papierpflicht bleibt ein nummerierter Papierfallback sinnvoll. Das ist Kanalpassung, keine pauschale Ablehnung von KI.

---

## 6. Stabile Lösungskategorien

Die im Auftrag genannten Kandidaten lassen sich zu zehn stabilen Kategorien verdichten:

| ID | Lösungskategorie | zusammengeführt / abgegrenzt |
|---|---|---|
| LK-01 | Anfrageeingang und Qualifizierung | bündelt Anfragen erfassen, Telefon-/Chat-Inhalte übernehmen und fehlende Angaben erkennen; keine automatische Annahme |
| LK-02 | Vorgangsakte, Status und Übergabe | bündelt Auftragssichtbarkeit, offene Schritte, Verantwortlichkeit und Teamübergabe |
| LK-03 | Mobile Einsatz- und Inspektionsdokumentation | bündelt Außeneinsatz, Fotos, Sprache, Belege und Rechnungsgrundlage |
| LK-04 | Physische Objekt- und Ortszuordnung | bleibt separat, weil digitale Statuslogik allein die physische Wahrheit nicht löst |
| LK-05 | Constraint-basierte Termin- und Kapazitätsplanung | bündelt Termine, Personal, Route und Material; unterscheidet Anfrage von Zusage |
| LK-06 | Dokument- und Datenerfassung mit Prüfung | bündelt PDFs, Bons, E-Mails, Formulare und Diktate; Ziel ist ein bestätigter Datensatz |
| LK-07 | Änderungs-, Freigabe- und Ausnahmeprozess | bündelt Zusatzarbeit, Versionen, Preise, Kundenzustimmung und Arbeitsstopp |
| LK-08 | Material-, Bestands- und Produktionsfluss | bündelt Beschaffung, WIP, Varianten, Chargen und Qualitätsstatus |
| LK-09 | Rechnungsgrundlage, Zahlungsabgleich und Nachfassen | bündelt Angebote/Rechnungen vorbereiten, Belege zuordnen, offene Zahlung verfolgen; Versand/Eskalation getrennt freigeben |
| LK-10 | Wissens-, Antwort- und Vertretungsunterstützung | bündelt Standardantworten, Fallhistorie, Entscheidungsnotizen und Übergaben; kein freier Chatbot ohne Vorgangskontext |

„Kunden informieren“ und „offene Vorgänge nachfassen“ sind keine eigenständigen universellen Kategorien. Sie sind Folgehandlungen aus LK-02, LK-07 oder LK-09 und dürfen nur nach einem bestätigten Status ausgelöst werden.

---

## 7. Vollständiger Solution-Pattern-Katalog

### SP-01 – Gemeinsamer Anfrageeingang mit Missing-Info-Prüfung

- **Problemfamilien:** PF-01, PF-02, PF-03, PF-11, PF-12.
- **Geeignete Branchen/Prozesse:** Solo-Dienstleister, Reparatur, Kanzlei, Social-Commerce, Serviceanfragen; Kontakt bis qualifizierter Vorgang.
- **Ungeeignet:** Notfallbewertung ohne feste Regeln; automatische Auftragsannahme bei unklarer Kapazität oder Haftung.
- **Eingangskanäle:** E-Mail, Webformular, WhatsApp/Chat, Telefonnotiz oder Transkript, Instagram-DM.
- **Mindestinformationen:** Kontakt, Anliegen, gewünschte Leistung, Ort/Objekt soweit relevant, Rückkanal; ein Deduplizierungsmerkmal.
- **Nutzerhandlung:** Der Betrieb leitet Anfragen an einen festen Eingang oder erfasst einen Anruf in einer kurzen Maske.
- **KI-Aufgabe:** Kerndaten vorschlagen, ähnliche Doppelanfrage markieren, fehlende Pflichtangaben nennen und eine Antwort vorbereiten.
- **Sichtbares Ergebnis:** Neue Anfragekarte mit Status „neu“, fehlenden Angaben und Antwortentwurf.
- **Menschliche Prüfung:** Identität, Dringlichkeit, Annahme/Ablehnung, Termin und verbindliche Antwort.
- **Technische Voraussetzungen:** zugelassener Kanalzugriff oder Weiterleitung; strukturierter Zieldatensatz; Korrekturmöglichkeit.
- **Organisatorische Voraussetzungen:** eine verantwortliche Inbox und klare Reaktions-/Vertretungsregel.
- **Datenschutz/Sicherheit:** nur notwendige Inhalte; private und betriebliche Konten trennen; sensible Anfragen rollenbasiert.
- **Kleinster Einstieg:** ein gemeinsames Minimalformular plus tägliche Sichtung; KI fasst nur Text zusammen.
- **Ausbaustufe:** bestätigte Anfragen werden an Planung oder Auftragsakte übergeben.
- **Typische Fehler:** Chatnachricht als verbindlicher Auftrag behandeln; doppelte Personen zusammenführen; Notfall falsch priorisieren.
- **Belege:** `K-01_case_evidence`, `K-04_case_evidence`, `C-08_case_evidence`, `RB02-C15-E01`, `RB02-C33-E01`, `RB03-PP04`.
- **Kundensprache:** „Alle Anfragen landen an einer Stelle. Die KI übernimmt die wichtigsten Angaben und zeigt dir, was noch fehlt. Du entscheidest, welche Anfrage du annimmst.“

### SP-02 – Einfache Vorgangsakte mit Status und nächstem Schritt

- **Problemfamilien:** PF-01, PF-04, PF-11.
- **Geeignete Branchen/Prozesse:** Dienstleistung, Reparatur, Handel, kleine Produktion; Auftrag von Annahme bis Abschluss.
- **Ungeeignet:** Prozesse ohne klaren einzelnen Vorgang oder physische Objekte ohne Kennzeichnung.
- **Eingangskanäle:** bestätigte Anfrage, manuelle Kurzerfassung, importierter Auftrag.
- **Mindestinformationen:** Vorgangs-ID, Kunde/Objekt, aktueller Status, Verantwortlicher, nächster Schritt.
- **Nutzerhandlung:** Mitarbeitende ändern den Status nur bei einem realen Ereignis und hinterlassen bei Übergabe eine kurze Notiz.
- **KI-Aufgabe:** Notizen zusammenfassen, offene Punkte erkennen, Übergabetext oder Kundenstatus vorbereiten.
- **Sichtbares Ergebnis:** Eine aktuelle Karte zeigt Stand, Verantwortlichen, Blockade und nächste Aktion.
- **Menschliche Prüfung:** Statusänderung, Abschluss, Kundenmeldung und Ausnahmeentscheidung.
- **Technische Voraussetzungen:** gemeinsame Liste oder leichtes Vorgangsboard; Rollen und Änderungsprotokoll.
- **Organisatorische Voraussetzungen:** wenige verständliche Statuswerte und klarer Auslöser je Status.
- **Datenschutz/Sicherheit:** Zugriffe nach Rolle; keine unnötigen Kundendetails in Teamansichten.
- **Kleinster Einstieg:** fünf Statuswerte und ein Verantwortlicher pro offenem Vorgang.
- **Ausbaustufe:** Erinnerungen und Statusmeldungen nach bestätigten Ereignissen.
- **Typische Fehler:** zu viele Status; Status per Vermutung; automatische Fertigmeldung ohne reale Prüfung.
- **Belege:** `RB02-C02-E01`, `RB02-C05-E01`, `RB03-C44-01`, `RB03-P05`, `RB03-P15`, `RB03-IP03`.
- **Kundensprache:** „Du siehst bei jedem Auftrag sofort: Wo steht er, wer ist dran und was fehlt noch. Die KI fasst lange Notizen kurz zusammen.“

### SP-03 – Mobile Einsatzdokumentation aus Sprache, Fotos und Bon

- **Problemfamilien:** PF-01, PF-03, PF-08, PF-09, PF-12.
- **Geeignete Branchen/Prozesse:** Hausmeister, Monteure, Reinigung, mobile Werkstatt, Inspektion, Außendienst; Einsatz bis Rechnungsvorbereitung.
- **Ungeeignet:** Einsatz lässt sich keinem Kunden/Objekt/Datum zuordnen; Smartphone ist im Umfeld nicht nutzbar und kein Offline-/Papierfallback existiert.
- **Eingangskanäle:** Smartphone-Sprachnachricht, Fotos, Bonfoto, kurzes mobiles Formular.
- **Mindestinformationen:** Einsatzanker, Datum, Ort, Tätigkeit; für Rechnung später bestätigte Zeit, Material, Zusatzarbeit und Abnahme soweit erforderlich.
- **Nutzerhandlung:** Nach dem Einsatz sendet der Nutzer eine kurze Sprachnachricht, Fotos und optional einen Bon an einen festen mobilen Eingang.
- **KI-Aufgabe:** Sprache in Felder überführen, Fotos/Bon dem Einsatz zuordnen, Betrag/Datum/Material vorschlagen, Unsicherheiten markieren.
- **Sichtbares Ergebnis:** Auf dem Handy erscheint eine fertige, prüfbare Einsatznotiz mit Anhängen und offenen Angaben.
- **Menschliche Prüfung:** Einsatz, Mengen, Zeit, Material, Zusatzarbeit, Belegzuordnung und Freigabe für Rechnung.
- **Technische Voraussetzungen:** mobile Uploadmöglichkeit, sichere Dateiablage, strukturierter Datensatz, Offline-/Retry-Mechanismus, Originalbeleg getrennt erhalten.
- **Organisatorische Voraussetzungen:** leichter Einsatzanker und wenige Pflichtfelder; klare Regel, wann ein Einsatz abgeschlossen ist.
- **Datenschutz/Sicherheit:** Fotos auf Personen/sensible Orte prüfen; Audio möglichst nicht dauerhaft speichern, wenn bestätigter Text genügt; GoBD-relevante Originale nicht durch KI-Ausgabe ersetzen.
- **Kleinster Einstieg:** fünf echte Einsätze lang nur Einsatznotiz erzeugen und manuell prüfen; noch keine Rechnung auslösen.
- **Ausbaustufe:** aus bestätigter Notiz einen Rechnungsentwurf und eine Missing-Info-Liste vorbereiten.
- **Typische Fehler:** Medien dem falschen Einsatz zuordnen; undeutliche Sprache; Bonbetrag falsch lesen; Zusatzleistung ohne Freigabe übernehmen.
- **Belege:** `C-01_automation_patterns`, `C-07_automation_patterns`, `K-12_case_evidence`, `RB03-C26-01` bis `RB03-C26-06`, `RB03-C45-01` bis `RB03-C45-06`, `RB03-P10`, `RB03-P12`, `RB03-L10`.
- **Kundensprache:** „Du sprichst nach dem Einsatz kurz ins Handy und schickst Fotos und den Bon dazu. Die KI erstellt daraus eine fertige Einsatznotiz. Du prüfst sie und gibst sie für die Rechnung frei.“

### SP-04 – Objekt-ID und echter Ablageort

- **Problemfamilien:** PF-04, PF-05.
- **Geeignete Branchen/Prozesse:** Schuh-, Fahrrad-, Handy- und Kfz-Reparatur, Änderung, Reinigung, Vermietung; Annahme bis Rückgabe.
- **Ungeeignet:** reine digitale Dienstleistungen ohne physisches Kundenobjekt.
- **Eingangskanäle:** Annahmeformular, Etikett/Anhänger, Barcode/QR optional, Papierbeleg.
- **Mindestinformationen:** stabile Objekt-/Auftrags-ID, Kunde, Objektmerkmal, realer Ort/Zone, Status, Herausgaberegel.
- **Nutzerhandlung:** Bei Annahme erhält Objekt und Auftrag dieselbe Kennung; bei Ortswechsel wird Fach/Zone aktualisiert.
- **KI-Aufgabe:** Sonderwünsche strukturieren, unvollständige Angaben markieren, Suchvorschläge machen; nie Standort erraten.
- **Sichtbares Ergebnis:** Auftrag zeigt eindeutig, welches Objekt gemeint ist und wo es tatsächlich liegt.
- **Menschliche Prüfung:** Kennzeichnung, Zustand, Ortswechsel, Fertigmeldung und berechtigte Herausgabe.
- **Technische Voraussetzungen:** robustes Label oder Papieranhänger; digitale Karte optional; zweite Suchkennung.
- **Organisatorische Voraussetzungen:** Zonen/Fächer und Ereignisse für Ortswechsel festlegen.
- **Datenschutz/Sicherheit:** Drittabholung separat autorisieren; keine Herausgabe nur aufgrund einer Telefonnummer.
- **Kleinster Einstieg:** fortlaufende Nummer auf Objekt, Beleg und Auftragsliste plus festes Ortsfeld.
- **Ausbaustufe:** Scan beim Übergang und Kundenmeldung nach menschlicher Fertigprüfung.
- **Typische Fehler:** Label löst sich; Objekt und Verpackung erhalten verschiedene Nummern; Systemstatus ersetzt Ortsprüfung.
- **Belege:** `RB02-C01-E01`, `RB02-C02-E01`, `C-10_automation_patterns`, `RB03-C01-01` bis `RB03-C01-06`, `RB03-P01` bis `RB03-P05`, `RB03-L11`.
- **Kundensprache:** „Jeder Gegenstand bekommt bei der Annahme eine eindeutige Nummer. Du siehst sofort, zu welchem Auftrag er gehört und in welchem Fach oder Regal er liegt.“

### SP-05 – Termin-Anfrage mit Kapazitätsprüfung statt blinder Sofortbuchung

- **Problemfamilien:** PF-02, PF-06.
- **Geeignete Branchen/Prozesse:** Massage, mobile Dienste, Reinigung, Fahrschule, mehrpersonige Leistungen; Anfrage bis bestätigter Termin.
- **Ungeeignet:** einfache Einzelressource mit stabilen Öffnungszeiten und ohne relevante Constraints – dort reicht reguläre Buchung.
- **Eingangskanäle:** Webanfrage, WhatsApp, Telefon, E-Mail, Kalender.
- **Mindestinformationen:** Leistung, Dauer, Personen/Ressourcen, Ort, Wunschzeit; relevante Qualifikation/Material soweit notwendig.
- **Nutzerhandlung:** Kunde stellt eine Anfrage; Betrieb sieht alle relevanten Constraints und bestätigt oder schlägt Alternativen vor.
- **KI-Aufgabe:** Anfragen zusammenfassen, fehlende Angaben erkennen, passende Slots/Alternativen vorschlagen, Antwort entwerfen.
- **Sichtbares Ergebnis:** prüfbare Terminoption mit Begründung und Kapazitätsstatus, keine automatische Zusage.
- **Menschliche Prüfung:** Personalverfügbarkeit, Ausnahme, verbindliche Zusage und Umplanung.
- **Technische Voraussetzungen:** aktuelle Kapazitätsdaten oder bewusst manueller Bestätigungsschritt; Kalenderzugriff nur bei verlässlicher Quelle.
- **Organisatorische Voraussetzungen:** definieren, welche Constraints eine Zusage verhindern.
- **Datenschutz/Sicherheit:** Mitarbeitendenverfügbarkeit nur zweckgebunden; keine verdeckte Leistungsbewertung.
- **Kleinster Einstieg:** alle Kanäle in eine Anfrageliste; Felder Leistung, Ort, Dauer, Wunschzeit, Personen.
- **Ausbaustufe:** regelbasierte Slotvorschläge und bestätigte Kalenderübernahme.
- **Typische Fehler:** Anfrage als Buchung anzeigen; veraltete Personaldaten; Wegzeit ignorieren; Mehrpersonenleistung falsch rechnen.
- **Belege:** `M-01_appointment_capacity_evidence`, `M-01_staff_planning_evidence`, `K-06_case_evidence`, `RB02-C16-E01`, `RB02-C20-E01`, `RB03-P13`, `RB03-PP05`.
- **Kundensprache:** „Alle Terminwünsche landen in einer Liste. Die KI prüft, welche Angaben fehlen und schlägt passende Zeiten vor. Du bestätigst den Termin erst, wenn Personal und Kapazität wirklich passen.“

### SP-06 – Dokument-zu-Datensatz mit Unsicherheitsprüfung

- **Problemfamilien:** PF-03, PF-09, PF-12.
- **Geeignete Branchen/Prozesse:** PDF-Aufträge, Bons, Lieferdokumente, Inspektionsdiktate, Bestellungen; Eingang bis geprüfte Erfassung.
- **Ungeeignet:** unleserliche oder rechtlich hochkritische Dokumente ohne fachliche Prüfung; kein definiertes Zielschema.
- **Eingangskanäle:** PDF, E-Mail-Anhang, Foto, Scan, Sprache.
- **Mindestinformationen:** Dokumenttyp, Zielvorgang, benötigte Felder, erlaubte Werte, Prüfregeln.
- **Nutzerhandlung:** Dokument hochladen oder fotografieren; vorgeschlagene Angaben prüfen.
- **KI-Aufgabe:** Felder extrahieren, Unsicherheit markieren, fehlende Pflichtangaben und mögliche Widersprüche anzeigen.
- **Sichtbares Ergebnis:** bestätigbarer Datensatz neben Originaldokument.
- **Menschliche Prüfung:** alle kritischen Felder, Zuordnung, Beträge, Mengen, Steuer-/Vertragsdetails.
- **Technische Voraussetzungen:** sichere Ablage, Version/Originalbezug, Zielschema, Validierung.
- **Organisatorische Voraussetzungen:** definieren, welche Felder kritisch und wer prüfberechtigt ist.
- **Datenschutz/Sicherheit:** Datenminimierung; Originalaufbewahrung; keine Buchung allein aus KI-Ausgabe.
- **Kleinster Einstieg:** ein Dokumenttyp und maximal zehn Zielfelder in einem Pilot.
- **Ausbaustufe:** bestätigte Daten an Auftrags- oder Buchhaltungssystem übergeben; Abweichungen protokollieren.
- **Typische Fehler:** falscher Dokumenttyp; Dezimal-/Datumsfehler; falscher Auftrag; Original wird überschrieben.
- **Belege:** `RB02-C26-E01`, `K-12_case_evidence`, `C-07_automation_patterns`, `RB03-C26-05`, `RB03-L08`, `RB03-L10`.
- **Kundensprache:** „Du lädst das Dokument hoch oder fotografierst es. Die KI übernimmt die wichtigen Angaben und markiert unsichere Stellen. Du prüfst, bevor etwas weiterverarbeitet wird.“

### SP-07 – Zusatzarbeit und Änderung mit dokumentierter Freigabe

- **Problemfamilien:** PF-04, PF-07, PF-08.
- **Geeignete Branchen/Prozesse:** Reparatur, Handwerk, individuelle Produktion, Druck, Bau; Befund bis freigegebene Änderung.
- **Ungeeignet:** vollständig standardisierte Aufträge ohne relevante Abweichung.
- **Eingangskanäle:** Werkstatt-/Einsatzmeldung, Foto, Diktat, Angebot, Kundenkanal.
- **Mindestinformationen:** Auftrag, Abweichung, Auswirkung auf Preis/Termin/Leistung, freigabeberechtigte Person.
- **Nutzerhandlung:** Mitarbeitender meldet Zusatzbefund; Arbeit pausiert, bis die richtige Person entscheidet.
- **KI-Aufgabe:** Befund strukturieren, Änderungsentwurf und Kundenfrage vorbereiten, Soll/Ist-Differenz anzeigen.
- **Sichtbares Ergebnis:** Änderungsfall mit Version, Status, Entscheidung und Zeitstempel.
- **Menschliche Prüfung:** technische Bewertung, Preis, Termin, Kundenzustimmung, Wiederaufnahme der Arbeit.
- **Technische Voraussetzungen:** versionierte Auftragsakte, Kommunikationsnachweis, Sperr-/Freigabestatus.
- **Organisatorische Voraussetzungen:** klare Schwellen und Berechtigungen; manueller Fallback.
- **Datenschutz/Sicherheit:** nur berechtigte Ansprechpartner; Zustimmung nachvollziehbar; keine autonome Preisentscheidung.
- **Kleinster Einstieg:** standardisierte Änderungsnotiz mit drei Optionen: freigeben, ablehnen, Rückfrage.
- **Ausbaustufe:** nach Freigabe Auftrag und Rechnungsentwurf synchron aktualisieren.
- **Typische Fehler:** falsche Kontaktperson; Arbeit läuft trotz Stopp; alte Version bleibt aktiv; Zustimmung ist unklar.
- **Belege:** `C-09_automation_patterns`, `RB03-C35-01`, `RB03-C46-01`, `RB03-P06`, `RB03-P14`, `RB03-IP07`, `RB03-IP09`.
- **Kundensprache:** „Wenn beim Auftrag etwas Neues auftaucht, wird die Arbeit an dieser Stelle gestoppt. Die KI bereitet die Änderung verständlich vor. Du und der Kunde entscheiden, bevor es weitergeht.“

### SP-08 – Einfaches Material- und Produktionsboard

- **Problemfamilien:** PF-04, PF-10.
- **Geeignete Branchen/Prozesse:** kleine Fertigung, Druck, Textil, Lebensmittel, 3D-Druck; Auftrag bis Fertigstellung.
- **Ungeeignet:** hochregulierte Chargenführung ohne validiertes Fachsystem; Betrieb kennt Varianten/Stücklisten noch nicht.
- **Eingangskanäle:** Auftrag, Stückliste, Materialeingang, Shopfloor-Ereignis, Qualitätsprüfung.
- **Mindestinformationen:** Auftrag/Variante, benötigtes Material, wenige Produktionsstufen, Verantwortlicher, Qualitätsfreigabe.
- **Nutzerhandlung:** Team bestätigt Materialentnahme und Stufenwechsel an klaren Übergaben.
- **KI-Aufgabe:** Auftrag in vorgeschlagene Aufgaben/Stückliste zerlegen, fehlendes Material oder widersprüchliche Variante markieren.
- **Sichtbares Ergebnis:** Board mit Auftrag, Materialstatus, aktuellem Schritt und Blockade.
- **Menschliche Prüfung:** Stückliste, Menge, Priorität, Qualitäts- und Versandfreigabe.
- **Technische Voraussetzungen:** Artikel-/Variantenidentität und kontrollierte Buchungsereignisse.
- **Organisatorische Voraussetzungen:** reale Shopfloor-Arbeit darf durch Erfassung nicht behindert werden; Papierbegleiter kann bleiben.
- **Datenschutz/Sicherheit:** Rollen; Audit bei Qualitäts-/Chargendaten; KI ersetzt keine regulatorische Freigabe.
- **Kleinster Einstieg:** eine Produktfamilie, wenige Status und manueller Soll/Ist-Abgleich.
- **Ausbaustufe:** Kapazitäts- und Materialvorschläge; bestätigte Bestandsbewegungen.
- **Typische Fehler:** falsche Variante; Papier und System divergieren; zu viele Klicks; automatische Bestandskorrektur.
- **Belege:** `C-02_automation_patterns`, `RB02-C08-E01` bis `RB02-C12-E01`, `RB03-C36-01`, `RB03-C40-01`, `RB03-PP03`, `RB03-PP06`.
- **Kundensprache:** „Du siehst bei jedem Auftrag, welches Material fehlt und welcher Schritt als Nächstes kommt. Die KI bereitet Aufgaben vor; dein Team bestätigt, was wirklich gemacht wurde.“

### SP-09 – Geprüfte Rechnungsgrundlage und Zahlungsnachverfolgung

- **Problemfamilien:** PF-03, PF-08, PF-09.
- **Geeignete Branchen/Prozesse:** wiederkehrende Dienste, Außendienst, Reparatur, kleine Praxen; Leistung bis Zahlung.
- **Ungeeignet:** Leistungsumfang, Preisregeln oder Zahlungszuordnung sind ungeklärt; rechtliche Eskalation ohne Fachprüfung.
- **Eingangskanäle:** bestätigter Leistungsnachweis, Rechnungssystem, Bank-/Zahlungsstatus, Beleg.
- **Mindestinformationen:** Kunde, Leistung, Datum, bestätigte Mengen/Zeiten, Preisquelle, Rechnung, Fälligkeit, eindeutige Zahlung.
- **Nutzerhandlung:** Nutzer gibt Leistungsnachweis frei; prüft Rechnungsentwurf und später fällige Fälle.
- **KI-Aufgabe:** Rechnungspositionen aus bestätigten Daten vorschlagen, fehlende Belege markieren, Erinnerungsentwurf erstellen.
- **Sichtbares Ergebnis:** prüfbarer Rechnungsentwurf bzw. Arbeitsliste mit offenen Zahlungen und nächstem Schritt.
- **Menschliche Prüfung:** Preis, Steuer, Leistung, Versand, Ausnahme und Eskalation.
- **Technische Voraussetzungen:** führende Rechnungs-/Zahlungsquelle, Statusabgleich, Änderungsprotokoll.
- **Organisatorische Voraussetzungen:** Fälligkeiten und Ausnahmebehandlung festgelegt.
- **Datenschutz/Sicherheit:** Finanzdaten schützen; GoBD; keine autonome Mahnung oder rechtliche Entscheidung.
- **Kleinster Einstieg:** aus bestätigter Einsatznotiz nur einen Entwurf erzeugen oder offene Rechnungen einmal pro Woche prüfen.
- **Ausbaustufe:** Zahlungseingang abgleichen und Erinnerungsentwurf zur Freigabe vorlegen.
- **Typische Fehler:** Zahlung falscher Rechnung zuordnen; unbestätigte Arbeit berechnen; doppelte Erinnerung.
- **Belege:** `K-07_case_evidence`, `K-08_case_evidence`, `C-09_automation_patterns`, `RB03-C45-05`, `RB03-PP08`, `RB03-L08`.
- **Kundensprache:** „Aus den bestätigten Leistungsdaten entsteht ein Rechnungsentwurf. Du prüfst ihn. Später zeigt dir das System, welche Zahlungen offen sind, und bereitet eine passende Erinnerung vor.“

### SP-10 – Übergabe- und Wissensnotiz im Vorgang

- **Problemfamilien:** PF-01, PF-04, PF-11.
- **Geeignete Branchen/Prozesse:** kleine Teams, Solo-Betriebe mit Vertretung, Kundenservice, Werkstatt, Disposition; Ereignis bis Übergabe.
- **Ungeeignet:** sensible Fachentscheidung soll ungeprüft aus alten Fällen beantwortet werden; kein Vorgangskontext.
- **Eingangskanäle:** kurze Notiz, Diktat, E-Mail, bestätigte Entscheidung.
- **Mindestinformationen:** zugehöriger Vorgang, Ereignis/Entscheidung, Verantwortlicher, nächster Schritt.
- **Nutzerhandlung:** Nach wichtiger Entscheidung wird kurz gesprochen oder notiert; Vertretung bestätigt Übernahme.
- **KI-Aufgabe:** Notiz strukturieren, offene Aufgabe und betroffene Person vorschlagen, relevante bestätigte Historie zusammenfassen.
- **Sichtbares Ergebnis:** kompakte Übergabe im richtigen Vorgang statt Wissen im privaten Chat oder Kopf.
- **Menschliche Prüfung:** Entscheidung, Zugriff, Verantwortlicher und Übernahme.
- **Technische Voraussetzungen:** Vorgangsakte, Rollen, Suche in bestätigten internen Notizen.
- **Organisatorische Voraussetzungen:** definieren, welche Entscheidungen dokumentiert werden müssen.
- **Datenschutz/Sicherheit:** keine unkontrollierte Sammlung privater Chats; Beschäftigtendaten minimieren.
- **Kleinster Einstieg:** drei Pflichtfelder: Was ist passiert? Was ist offen? Wer übernimmt?
- **Ausbaustufe:** vertretungsfähige Standardantworten und Übergabeübersicht.
- **Typische Fehler:** KI vermischt fremde Vorgänge; veraltete Notiz wird als aktuelle Entscheidung gezeigt; sensible Daten werden breit sichtbar.
- **Belege:** `RB02-C29-E01`, `RB02-C32-E01`, `RB03-C22-01`, `RB03-P15`, `RB03-PP10`, `RB03-L07`.
- **Kundensprache:** „Wichtige Absprachen bleiben direkt beim Auftrag. Die KI fasst sie kurz zusammen und zeigt, was offen ist. So kann jemand anderes übernehmen, ohne alles neu zu erfragen.“

---

## 8. Problemfamilie-zu-Lösung-Matrix

| Problemfamilie | primäres Solution Pattern | mögliche Ergänzung | harte Voraussetzung |
|---|---|---|---|
| PF-01 verteilte Vorgangsinformation | SP-02 oder SP-03 | SP-01, SP-10 | gemeinsamer Vorgangsanker |
| PF-02 unzuverlässige Anfrageerfassung | SP-01 | SP-05 | Mindestfelder und verantwortlicher Eingang |
| PF-03 Mehrfachübertragung | SP-06 | SP-03, SP-09 | führende Quelle und Zielschema |
| PF-04 unsichtbarer Status/Übergabe | SP-02 | SP-07, SP-10 | wenige Statuswerte mit realem Auslöser |
| PF-05 Objekt-/Ortszuordnung | SP-04 | SP-02 | ID direkt am Objekt und überprüfbarer Ort |
| PF-06 Termin-/Kapazitätskonflikt | SP-05 | SP-01 | relevante Constraints und manuelle Zusagegrenze |
| PF-07 Änderung/Freigabe | SP-07 | SP-02, SP-09 | Stop-Ereignis und freigabeberechtigte Person |
| PF-08 Feld-zu-Rechnung | SP-03 | SP-09, SP-06 | Einsatzanker und mobile/robuste Erfassung |
| PF-09 Zahlung/Beleg/Nachfassen | SP-09 | SP-06 | eindeutige Rechnung-/Zahlungszuordnung |
| PF-10 Material/WIP | SP-08 | SP-02, SP-07 | Artikel/Variante und kontrollierte Ereignisse |
| PF-11 Personenabhängigkeit | SP-10 | SP-01, SP-02 | gemeinsamer Zugriff und Vertretungsregel |
| PF-12 unstrukturierte Dokumente | SP-06 | SP-01, SP-03 | Ziel-Schema und Human Check |

---

## 9. Analyse der aktuellen Fehlentscheidungen

### 9.1 Hausmeisterservice

**Nutzerfakten des Testfalls:** Nach Einsätzen entstehen Fotos, Handynotizen/Sprachnachrichten und Belege. Vor Rechnungen werden WhatsApp, Bilder, Zettel und Bons zusammengesucht. Gewünscht ist eine vollständige Einsatznotiz aus Sprache, Fotos und Bon.

| Prüffrage | Ergebnis |
|---|---|
| War die Diagnose falsch? | überwiegend nein; verteilte vorgangsbezogene Information und Feld-zu-Rechnung-Lücke sind korrekt |
| War die Ursache falsch? | teilweise zu oberflächlich; „fehlende Ordnung“ ist nur ein Oberbegriff. Die konkrete Ursache ist fehlende gemeinsame Einsatzzuordnung und fehlende Transformation in eine bestätigte Einsatznotiz |
| War die Problemfamilie falsch? | wenn nur „Organisation“ oder „Ablage“ gewählt wurde: ja. Richtig sind PF-01 + PF-08 + PF-12, optional PF-09 |
| Wurde der digitale Ausgang falsch eingeschätzt? | ja; Smartphone, Sprache, Fotos und Bonfoto sind bereits geeignete digitale Rohkanäle. Niedrige Prozessreife bedeutet hier nicht niedrige Kanaleignung |
| Fehlte ein Solution Pattern? | ja; SP-03 muss als eigenständiges, konkretes Muster existieren und priorisiert werden |
| War „Ordnung vor Automatisierung“ zu stark? | ja. Notwendig ist nur ein leichter Einsatzanker, kein vorgelagertes Album-/Ordner-/Umschlagsystem |
| War der Prompt zu offen? | ja. Er erlaubt Ordnung ausdrücklich, verlangt aber keinen Vergleich „bereits digitaler Input vs. fehlender Prozessanker“ |
| Könnte der RAG-Kontext zu defensiv sein? | ja. Analyse-Retrieval erlaubt Minimalverbesserung, Reifegrad, analoge Workarounds und Voraussetzungen; ein konkretes Automationsmuster ist nicht zwingend enthalten |
| Fehlten Few-shots? | wahrscheinlich. Es fehlt ein sichtbares Kontrastpaar: Smartphone-Rohdaten → direkte KI-Unterstützung versus unmarkiertes physisches Objekt → Ordnung zuerst |
| War die Formulierung schlecht? | ja, wenn Album/Ordner/Umschlag als Kernlösung erscheint. Das beschreibt Aufbewahrung, nicht den gewünschten Arbeitsablauf |

**Realistische Grenze:** Die KI darf Kunde, Ort, Datum, Tätigkeit, Material und Bonangaben vorschlagen. Der Nutzer muss Zuordnung, Zeit/Menge, Zusatzarbeit und Beleg prüfen. Ein Rechnungsentwurf ist erst die Ausbaustufe nach bestätigter Einsatznotiz. Originalbeleg und relevante Fotos bleiben erhalten; Audio kann nach bestätigtem Text nach Datenschutzregel gelöscht werden.

### 9.2 Schuhmacher / Schuhreparatur

**Evidenzlage:** `RB03-C01` belegt Versand-Reparatur, individuelle Wünsche und knappen Lagerplatz. Interne Regal-, Zettel- und Drittabholungsdetails sind laut Merge-Gate nicht vollständig durch einen lokalen Primärbericht belegt.

| Prüffrage | Ergebnis |
|---|---|
| Diagnose | Objekt-Auftrag-Zuordnung, Sonderwünsche und Zusatzschaden sind plausible, teils gut belegte Problemachsen |
| Ursache | bei einem tatsächlich unmarkierten Paar ist fehlende stabile Objekt-ID die Ursache; KI kann keinen realen Ort rekonstruieren |
| Problemfamilie | PF-05 primär; PF-07 für Zusatzarbeit; PF-04 für Status |
| Digitaler Ausgang | darf nicht pauschal angenommen werden; der belegte Shoedoc-Prozess besitzt bereits digitale Auswahl/Versandanteile |
| Passende Lösung | SP-04 zuerst für Identität/Ort; danach KI für Sonderwunsch-Extraktion, Klärfälle und Statuskommunikation |
| Stärke von „Ordnung zuerst“ | hier fachlich berechtigt, aber nur für Objektidentität und physischen Ort – nicht als generelle Ablehnung von KI |
| Formulierung | statt „erst Ordner führen“: „Jedes Paar erhält dieselbe Nummer auf Paar, Auftrag und Verpackung. Danach kann die KI Wünsche ordnen und Klärfälle vorbereiten.“ |

**Wichtige Unsicherheit:** Das Produkt darf den angenommenen verlorenen Kundenzettel oder Drittabholprozess nicht als Tatsache über einen konkreten Schuhmacher ausgeben, solange der Nutzer ihn nicht genannt hat.

### 9.3 Massagesalon

**Nutzer-/Quellenfakten:** mehrere Anfragekanäle; Onlinebuchung ist nur Anfrage; Inhaberin prüft Personal manuell; schwankende Verfügbarkeit; dokumentierte Doppel-/Mehrfachbelegungen; Arbeitszeiten fehlen; Zahlungen und Belege werden manuell erfasst.

| Prüffrage | Ergebnis |
|---|---|
| Diagnose | richtig, wenn Kern als gekoppeltes Anfrage-, Personal- und Kapazitätsproblem beschrieben wird; falsch, wenn nur „mehrere Kanäle“ genannt werden |
| Ursache | Onlinekalender kennt die tatsächliche Personalverfügbarkeit und Mehrpersonenleistung nicht zuverlässig |
| Problemfamilie | PF-06 primär, PF-02 sekundär; PF-09 und Zeitdokumentation sind getrennte weitere Prozesse |
| Digitaler Ausgang | bereits digital in mehreren Kanälen; das Problem ist nicht Papiermangel, sondern fehlende gemeinsame Anfrage-/Kapazitätssicht |
| Passende Lösung | SP-05: zentrale Termin-Anfrageliste, fehlende Angaben, Alternativvorschläge; Inhaberin bestätigt verbindlich |
| Stärke von „Ordnung zuerst“ | Minimalfelder und aktueller Personalstatus sind nötig. Ein umfangreiches manuelles Vorprojekt ist nicht nötig |
| Fehlendes Pattern | klare Trennung zwischen „Anfrage“, „vorläufig möglich“ und „bestätigt“ sowie Paarmassage als Mehrressourcenfall |
| Formulierung | „Alle Terminwünsche landen in einer Liste. Die KI zeigt passende Optionen. Du bestätigst erst, wenn wirklich genug Personal da ist.“ |

### 9.4 Systemische Ursachen im aktuellen RAG- und Recommendation-Layer

1. **Kein zwingendes Solution-Pattern im Analyse-Retrieval:** `analysis` verlangt `diagnostic_pattern` und `automation_guardrail`, aber nicht `automation_pattern`.
2. **Defensive Chunk-Typen konkurrieren im selben Top-k:** `minimal_viable_improvement`, `digital_readiness_pattern`, `implementation_prerequisite`, `analog_workaround` und `adoption_risk` können konkrete Zielbilder verdrängen.
3. **Diversität wird nur begrenzt erzwungen:** Es gibt einen Deckel für `case_evidence` je Pattern, aber keine feste Balance zwischen Ursache, Voraussetzung, Solution Pattern und Guardrail.
4. **Reifegrad ist eindimensional:** organisatorische Ordnung, technische Digitalisierung und Kanaleignung werden nicht separat bewertet.
5. **Prompt-Bias:** Der finale Prompt sagt, Ordnung und Standardisierung dürften vor Digitalisierung stehen. Er verlangt nicht die Gegenprüfung, ob der Nutzer bereits digital geeignete Eingaben erzeugt.
6. **Schema-Bias:** Jede Analyse muss exakt drei Opportunities enthalten. Das kann schwächere oder generische Vorschläge erzwingen. `required_prerequisites` verlangt mindestens einen Eintrag, selbst wenn nur eine leichte Zuordnung nötig ist.
7. **Kategorien sind grob:** `Ordnung und Standardisierung`, `einfache Digitalisierung`, `regelbasierte Automatisierung`, `KI-Unterstützung` bilden kombinierte Lösungen wie „KI-gestützte mobile Erfassung mit minimaler ID“ nur unzureichend ab.
8. **Kein normalisierter Solution-Katalog:** Gute Lösungen sind im Korpus vorhanden, aber uneinheitlich in langen `automation_pattern`-Chunks eingebettet.
9. **Agentenindex noch nicht laufzeitaktiv:** Die 205 Agentenpatterns beeinflussen die Entscheidung derzeit nicht über semantisches Retrieval; wesentliche Entscheidungen bleiben deterministische Python-Regeln.

---

## 10. Lücken im bestehenden Wissen

1. Ein sauber dokumentierter Hausmeister-/Außendienst-Primärfall mit Smartphone, Sprache, Fotos, Bon, Rechnungsübergabe und tatsächlichen Ausnahmen fehlt als eigener Quellenfall.
2. Für klassische lokale Reparaturannahme fehlen in einzelnen Branchen Vor-Ort-Primärberichte, besonders Schuhmacher mit Regal, losem Ticket und Drittabholung.
3. Wirkung nach Umsetzung ist selten neutral belegt. Viele Quellen beschreiben Probleme oder Anbietererfolge, aber keine unabhängige Vorher-/Nachher-Qualität.
4. Es fehlt eine kanonische Zuordnung `Problemfamilie → Ursache → Entscheidungsfrage → zulässige Reifestufe → Solution Pattern`.
5. Solution Patterns besitzen kein einheitliches Schema und keine stabilen IDs über alle Batches.
6. Digitaler Ausgangszustand sollte mindestens in drei Achsen getrennt werden: **Kanaleignung**, **Prozess-/Datenreife**, **Automationsreife**.
7. Es fehlen gezielte Retrieval-Evaluationen für „zu defensiv“, „zu früh automatisiert“, „richtig diagnostiziert, falsche Lösung“ und „richtige Lösung, schlechte Kundensprache“.
8. Es fehlen Kontrastfälle, die denselben Schmerz mit unterschiedlicher Voraussetzung zeigen, zum Beispiel:
   - Smartphone + eindeutiges Objekt → KI jetzt;
   - Smartphone + kein Vorgangsanker → leichte ID zuerst;
   - physisches Objekt ohne Kennung → Ordnung zwingend;
   - stabile Daten + reversible Regel → Automation möglich.
9. Rechtliche Guardrails sind vorhanden, benötigen aber periodische Aktualisierung und dürfen nicht als pauschales Produkthemmnis wirken.
10. Es fehlt ein getrenntes Qualitätsmaß für Diagnose-Richtigkeit, Lösungsfit, Reifegrad-Fit, Umsetzbarkeit, Kundensprache und menschliche Freigabe.

---

## 11. Empfohlene fachliche Speicher- und Entscheidungsarchitektur

### 11.1 Deterministisch im Code

Diese Regeln sollten nicht von semantischer Ähnlichkeit abhängen:

- Evaluationen und `raw/` niemals indexieren.
- Nutzerfakten strikt von RAG-Evidenz und Ableitungen trennen.
- Harte Gates: stabile Vorgangs-/Objekt-ID, physischer Ort, System of Record, Freigabeberechtigung, Hochrisikoentscheidungen.
- Keine autonome Preis-, Vertrags-, Zahlungs-, Personal-, Sicherheits-, Qualitäts- oder Herausgabeentscheidung.
- Reifeentscheidung über getrennte Achsen: Kanaleignung, Daten-/Prozessreife, Regelstabilität, Fehlerfolge.
- Solution Pattern erst nach Applicability- und Exclusion-Gates zulassen.
- Ein Solution Pattern muss konkrete Eingabe, KI-Aufgabe, Ergebnis und Human Check besitzen.
- No-Repeat, Fragebudget und „0 Rückfragen möglich“.
- Output-Validierung, verbotene interne Referenzen, Logging und Zähler.

### 11.2 Im Diagnose-RAG

- reale Quellenfälle und belegte Ist-Prozesse,
- diagnostische Muster und Ursachen,
- entscheidungsrelevante Fragen,
- Branchen-/Umgebungsvarianten,
- Reife- und Implementierungsvoraussetzungen als Evidenz,
- Guardrails und bekannte Ausnahmen,
- Quellenstärke und Herkunft.

Das Diagnose-RAG soll sagen: **„Welche Problemfamilie und welche Bedingungen sind wahrscheinlich relevant?“** Es soll nicht allein die sichtbare Kundenlösung formulieren.

### 11.3 Im strukturierten Solution-Katalog

Die zehn Solution Patterns aus Abschnitt 7 sollten als kleine, versionierte, maschinenlesbare Datensätze gespeichert werden. Pflichtfelder:

```text
solution_id
name
problem_family_ids
applicable_if
not_applicable_if
input_channels
minimum_information
user_action
ai_task
visible_output
human_check
technical_prerequisites
organizational_prerequisites
security_guardrails
smallest_entry
later_stage
failure_modes
evidence_refs
customer_language
```

Der Katalog ist kein Toolverzeichnis. Er beschreibt den Arbeitsalltag nach der Veränderung.

### 11.4 Separater Solution-Index – eventuell später

Für den kleinen kuratierten Katalog ist zunächst **kein weiterer FAISS-Index notwendig**. Deterministische Filterung nach Problemfamilie, Branche, Prozess, Kanal, Voraussetzungen und Ausschlüssen ist transparenter. Ein separater Solution-Index wird erst sinnvoll, wenn:

- der Katalog deutlich größer und sprachlich vielfältiger wird,
- mehrere passende Muster nach semantischer Absicht gerankt werden müssen,
- die deterministischen Applicability-Gates weiterhin vor dem Ranking laufen,
- eigene Retrieval-Evaluationen belegen, dass semantische Suche besser ist als direkte strukturierte Auswahl.

Diagnose- und Solution-Wissen sollten nicht ungefiltert in einem gemeinsamen Pool konkurrieren.

---

## 12. Präziser Handoff für Codex

### Ziel

Die fachliche Grundlage in ein testbares Recommendation Design überführen, ohne bestehende Nutzerfakten-, Guardrail- und Evaluationsschutzmaßnahmen zu schwächen.

### Arbeitsreihenfolge

1. **Noch keine Laufzeitänderung:** diese Fachgrundlage reviewen und Problemfamilien/Solution Patterns fachlich freigeben.
2. **Strukturierte Artefakte entwerfen:** JSON-Schemas für `problem_families` und `solution_patterns`; Evaluationen bleiben separat.
3. **Deterministische Decision Gates spezifizieren:** Vorgangsanker, physischer Ort, Kanaleignung, Datenreife, Regelstabilität, Fehlerfolge und Human-Approval.
4. **Retrieval-Vertrag definieren:** Diagnose-Retrieval liefert mindestens Ursache/Problemfamilie, passenden Fall oder Prozesspattern, Voraussetzung und Guardrail. Konkrete Lösung wird nicht allein aus zufälligem Top-k generiert.
5. **Solution-Auswahl:** Problemfamilie + Gates filtern den kleinen Katalog; danach höchstens wenige passende Lösungen ranken.
6. **Recommendation-Output:** für Rang 1 genau `user_action`, `ai_task`, `visible_output`, `human_check`, `smallest_entry`, `later_stage` ausgeben; Kundensprache getrennt von technischer Begründung.
7. **Evaluation ergänzen:** Hausmeister, Schuhmacher und Massagesalon als Kontrasttests; zusätzlich Tests für zu defensiv, zu früh automatisiert, falsche Zuordnung und generische Sprache.
8. **Erst danach Code/Prompt ändern:** kleine, isolierte Änderungen mit der dann aktuellen vollständigen Testsuite plus neuen Recommendation-Tests.

### Konkrete Akzeptanzkriterien

- Hausmeister: Rang 1 ist mobile Einsatzdokumentation, sofern ein leichter Einsatzanker vorhanden oder im selben Mini-Test ergänzt werden kann; kein Album/Umschlag als Kernlösung.
- Schuhmacher: Ohne Objekt-ID/Ort keine KI- oder Automationsbehauptung über Auffindbarkeit; mit ID darf KI Sonderwünsche und Klärfälle unterstützen.
- Massagesalon: keine automatische Terminbestätigung bei unsicherer Personalverfügbarkeit; zentrale Anfrage- und Kapazitätssicht mit menschlicher Zusage.
- Jede Empfehlung benennt konkrete Nutzerhandlung, konkrete KI-Aufgabe, sichtbares Ergebnis und Human Check.
- RAG-Evidenz wird nie als Nutzerfakt ausgegeben.
- Evaluationen bleiben vollständig außerhalb aller produktiven Indizes.
- Ein defensiver Guardrail darf ein geeignetes KI-Muster begrenzen, aber nicht ohne Begründung verdrängen.
- Fehlende Information führt nur dann zu einer Rückfrage, wenn die Antwort Problemfamilie, Reifestufe, Lösung oder Freigabe verändert.

### Technische Punkte aus dem Ist-Code, die gezielt überprüft werden müssen

- In `PHASE_TYPES["analysis"]` ist `automation_pattern` erlaubt, aber nicht erforderlich.
- `_diverse_selection()` balanciert nur erforderliche Typen und Fallbelege, nicht Diagnose vs. Solution vs. Voraussetzung.
- Der Standard `RAG_TOP_K` ist 6; bei 634 heterogenen Chunks kann ein passendes Solution Pattern fehlen.
- Der finale Prompt enthält einen ausdrücklichen Ordnung-vor-Digitalisierung-Hinweis, aber kein Kanal-/Anker-Gegencheck.
- `AutomationOpportunityResult` erzwingt exakt eine grobe Kategorie und die Gesamtanalyse exakt drei Opportunities.
- `required_prerequisites` verlangt mindestens einen Eintrag; Voraussetzungen dürfen dadurch nicht künstlich aufgebläht werden.
- `retrieve_agent_patterns()` existiert, wird im vorliegenden Laufzeitpfad aber nicht aufgerufen.

### Nicht tun

- keinen neuen Index bauen, bevor Schema und Evaluation freigegeben sind,
- die zehn Solution Patterns nicht als lange freie Promptliste einfügen,
- Diagnose-RAG und Solution-Katalog nicht ungefiltert zusammenwerfen,
- Guardrails nicht entfernen, um „mehr KI“ zu erzeugen,
- keinen Anbieter oder Tool als Standardlösung festschreiben,
- keine Evaluation in Produktwissen umwandeln.

---

## Schlussfolgerung

Die AI Start Map braucht nicht mehr allgemeines KMU-Wissen, sondern eine klarere fachliche Entscheidungsbrücke. Die wichtigste Produktregel lautet:

> **So wenig Ordnung wie zwingend nötig, so früh konkrete KI-Unterstützung wie realistisch möglich, und Automatisierung erst nach bestätigten Daten und klaren Freigaben.**

Beim Hausmeister ist die leichte Einsatzzuordnung Teil der KI-Lösung, nicht ein separates monatelanges Ordnungsvorhaben. Beim Schuhmacher ist die physische Kennzeichnung eine echte Vorbedingung. Beim Massagesalon ist die menschliche Kapazitätsbestätigung die Grenze. Diese drei Kontrastfälle sollten künftig die Recommendation-Logik und ihre Evaluation prägen.
