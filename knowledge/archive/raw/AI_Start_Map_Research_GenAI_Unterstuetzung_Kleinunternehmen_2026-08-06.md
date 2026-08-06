# AI Start Map – Forschungsgrundlage: Wie GenAI Kleinunternehmen konkret unterstützen kann

**Stand:** 6. August 2026
**Zweck:** Zweite fachliche Wissensschicht nach der Pain-Point-Analyse
**Bezugsrahmen:** 12 Problemfamilien und 10 Solution Patterns der AI Start Map

---

## 1. Forschungsfrage

Die vorausgehende Recherche hat gezeigt, **welche wiederkehrenden Prozessprobleme Kleinunternehmen haben**. Diese zweite Recherche beantwortet die Anschlussfrage:

> Welche Aufgaben kann generative KI innerhalb dieser realen Arbeitsabläufe sinnvoll übernehmen, welche Voraussetzungen müssen dafür erfüllt sein, was muss deterministisch oder menschlich bleiben und wie kann die AI Start Map daraus eine belastbare Startempfehlung ableiten?

Die Untersuchung verfolgt ausdrücklich nicht das Ziel, möglichst viele KI-Ideen oder Tools zu sammeln. Gesucht werden wiederverwendbare, produktneutrale Unterstützungsmuster, die sich einem konkreten Engpass zuordnen und als kleiner Pilot überprüfen lassen.

---

## 2. Methodik und Quellenlage

### 2.1 Verwendete Wissensschichten

Die Auswertung verbindet vier Ebenen:

1. **Interne Prozessevidenz:** die bereits recherchierten KMU-Fälle, diagnostischen Muster und zwölf Problemfamilien der AI Start Map.
2. **Aktuelle SME-Evidenz:** OECD- und Eurostat-Daten zur tatsächlichen Nutzung, zu wahrgenommenem Nutzen und zu Hemmnissen.
3. **Wirkungsforschung:** experimentelle Studien zu Produktivität, Qualität und den Grenzen von GenAI bei klar abgegrenzten Aufgaben.
4. **Sicherheits- und Rechtsrahmen:** NIST, EDPB, BSI und EU-Kommission zu Risiko, Datenschutz, menschlicher Aufsicht und KI-Kompetenz.

### 2.2 Wichtige Einschränkung

„SME/KMU“ umfasst in vielen Studien Betriebe bis 249 Beschäftigte. Eurostat erfasst in seiner Unternehmensstatistik zudem erst Unternehmen ab zehn Beschäftigten. Die Ergebnisse dürfen daher **nicht ungeprüft als exakte Statistik für Solo- und Kleinstunternehmen** ausgegeben werden. Für AI Start Map dienen sie als belastbare Richtungsevidenz. Besonders relevant ist, dass die OECD in ihrer GenAI-Erhebung auch Ein-Personen-Unternehmen betrachtet und berichtet, dass diese den Nutzen oft positiver einschätzen als größere SMEs.

### 2.3 Zentrale empirische Befunde

- In der OECD-Erhebung 2024 nutzten 30,7 % der befragten SMEs GenAI; für Deutschland wurde ein höherer Wert berichtet. 91,6 % der GenAI-Nutzer verwendeten sie zur Texterzeugung. Nur 29 % setzten sie in Kernaktivitäten ein; verbreiteter waren einfache, einmalige und eher randständige Aufgaben. [OECD: How are SMEs using generative AI?](https://www.oecd.org/en/publications/generative-ai-and-the-sme-workforce_2d08b99d-en/full-report/component-4.html)
- 65,1 % der nutzenden SMEs berichteten eine verbesserte Arbeitsleistung, 45,2 % Kosteneinsparungen und 35,1 % die Fähigkeit, zuvor nicht mögliche Aufgaben auszuführen. Die OECD warnt zugleich, dass daraus weder die Größe noch die Kausalität des Nutzens für jeden Betrieb abgeleitet werden kann. [OECD: Generative AI and the SME Workforce](https://www.oecd.org/en/publications/generative-ai-and-the-sme-workforce_2d08b99d-en.html)
- Unter Nichtnutzern waren die häufigsten Hemmnisse: vermutete fehlende Eignung für die eigene Arbeit, rechtliche und urheberrechtliche Bedenken, Sorgen um eingegebene Informationen sowie fehlende Kompetenzen. [OECD: Are SMEs prepared for generative AI?](https://www.oecd.org/en/publications/generative-ai-and-the-sme-workforce_2d08b99d-en/full-report/component-6.html)
- Eurostat meldete für 2025 eine KI-Nutzung von 17 % bei kleinen Unternehmen mit 10–49 Beschäftigten. Marketing/Vertrieb und Geschäftsadministration gehörten zu den häufigsten Zwecken. Fehlende Expertise, unklare Rechtsfolgen und Datenschutzbedenken waren die wichtigsten Gründe gegen eine Einführung. Diese Statistik erfasst keine Unternehmen unter zehn Beschäftigten. [Eurostat: Use of artificial intelligence in enterprises](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Use_of_artificial_intelligence_in_enterprises)
- Experimentelle Ergebnisse zeigen deutliche Gewinne bei eng abgegrenzten, zur Technologie passenden Aufgaben. Dieselbe Forschung zeigt aber eine „jagged frontier“: Bei Aufgaben außerhalb der Modellfähigkeit können Menschen mit KI schlechtere Lösungen produzieren als ohne KI. [OECD Review zur Wirkungsforschung](https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/06/the-effects-of-generative-ai-on-productivity-innovation-and-entrepreneurship_da1d085d/b21df222-en.pdf), [Harvard Business School: Navigating the Jagged Technological Frontier](https://www.hbs.edu/faculty/Pages/item.aspx?num=64700)

### 2.4 Konsequenz für die AI Start Map

Die AI Start Map darf nicht fragen: „Wo könnte man irgendwie ChatGPT einsetzen?“ Sie muss feststellen:

1. Welche konkrete Aufgabe verursacht Reibung?
2. Besteht diese Aufgabe überwiegend aus Sprache, Text, Bild, Dokument oder Wissenssuche?
3. Gibt es einen eindeutigen Vorgang und ein definiertes Zielergebnis?
4. Wie wird ein Fehler erkannt?
5. Welche Entscheidung oder Aktion darf erst nach menschlicher Freigabe erfolgen?
6. Lässt sich der Nutzen mit wenigen echten Fällen messen?

---

## 3. Was GenAI für Kleinunternehmen tatsächlich ist

GenAI ist für Kleinunternehmen am wertvollsten als **Übersetzungs- und Vorbereitungsschicht zwischen unstrukturierter Realität und einem strukturierten Geschäftsprozess**.

```text
Alltagsinput
Sprache · E-Mail · Chat · Foto · Bon · PDF · freie Notiz
                              ↓
GenAI
verstehen · extrahieren · ordnen · zusammenfassen · entwerfen · Lücken markieren
                              ↓
Prüfbarer Datensatz oder Entwurf
                              ↓
Regeln und Fachsoftware
validieren · berechnen · Status setzen · speichern · Frist auslösen
                              ↓
Mensch
prüfen · entscheiden · freigeben · verantworten
```

Diese Architektur ist für kleine Betriebe geeigneter als eine pauschale Vollautomatisierung, weil ihre Abläufe oft viele Ausnahmen, persönliche Kommunikation und unvollständige Eingangsdaten enthalten.

---

## 4. Die neun belastbaren GenAI-Fähigkeitsmuster

### GAI-01 – Freie Sprache in Struktur überführen

**Aufgabe:** Eine Sprachnachricht, E-Mail oder Chatnachricht in definierte Felder überführen.
**Beispiele:** Tätigkeit, Ort, Material, Kundenwunsch, nächster Schritt, offene Angabe.
**Wert:** Der Nutzer muss seinen Alltag nicht an eine starre Maske anpassen.
**Voraussetzung:** Zielschema, Vorgangsanker und Pflichtfelder sind definiert.
**Grenze:** Die KI darf fehlende Fakten nicht erfinden.

### GAI-02 – Multimodale Inhalte gemeinsam auswerten

**Aufgabe:** Text, Sprache, Bilder und Dokumente zu einem Vorgang gemeinsam verarbeiten.
**Beispiele:** Sprachnachricht + Einsatzfotos + Bonfoto.
**Wert:** Informationen, die ohnehin mobil entstehen, werden verbunden.
**Voraussetzung:** Medien können eindeutig demselben Einsatz oder Auftrag zugeordnet werden.
**Grenze:** Bildinhalt und Belegwerte sind Vorschläge mit Unsicherheitsprüfung, keine gesicherte Wahrheit.

### GAI-03 – Klassifizieren und vorsortieren

**Aufgabe:** Anfrageart, Dokumenttyp, Thema oder vermutete Dringlichkeit vorschlagen.
**Beispiele:** Neuanfrage, Reklamation, Terminwunsch, Beleg, Zusatzbefund.
**Wert:** Eine gemeinsame Inbox wird trotz verschiedener Eingänge bearbeitbar.
**Voraussetzung:** Kleine, verständliche Kategorien und eine Fallback-Kategorie.
**Grenze:** Notfall, Rechtsfolge oder verbindliche Priorität nicht autonom bestimmen.

### GAI-04 – Zusammenfassen und Übergaben vorbereiten

**Aufgabe:** Lange Verläufe in aktuellen Stand, Entscheidung, Blockade und nächsten Schritt verdichten.
**Wert:** Weniger Suchzeit und geringere Abhängigkeit vom Inhaber.
**Voraussetzung:** bestätigte Historie und klare Aktualitätslogik.
**Grenze:** Alte oder fremde Vorgänge dürfen nicht vermischt werden.

### GAI-05 – Fehlende oder widersprüchliche Angaben markieren

**Aufgabe:** Gegen ein definiertes Schema prüfen, was fehlt oder nicht zusammenpasst.
**Beispiele:** Einsatzort fehlt; Summe ist unleserlich; Termin passt nicht zur Dauer; Zusatzarbeit hat keine Freigabe.
**Wert:** Weniger Rückläufer und vollständigere Vorgänge.
**Voraussetzung:** Pflichtfelder, Wertebereiche und fachliche Prüfregeln.
**Grenze:** Harte Prüfungen sollten deterministisch erfolgen; GenAI liefert ergänzende Hinweise.

### GAI-06 – Entwürfe erzeugen

**Aufgabe:** Kundenantwort, Einsatzbericht, Angebotsbaustein, Rechnungsposition oder Übergabetext vorbereiten.
**Wert:** Schnellere Kommunikation und konsistentere Dokumente.
**Voraussetzung:** bestätigte Eingangsdaten, Tonalität und zulässige Vorlagen.
**Grenze:** Versand, Preis, Vertrag, Mahnung und rechtliche Aussage bleiben freigabepflichtig.

### GAI-07 – Wissensassistenz mit RAG

**Aufgabe:** Aus bestätigten internen Dokumenten passende Informationen finden und mit Quellenbezug beantworten.
**Beispiele:** „Was wurde vereinbart?“, „Welche Arbeitsanweisung gilt?“, „Welche Schritte sind bei dieser Reklamation offen?“
**Wert:** Wissen wird auffindbar, ohne dass der Inhaber jede Frage selbst beantworten muss.
**Voraussetzung:** gepflegte, berechtigte und versionierte Wissensquellen.
**Grenze:** RAG verbessert Grounding, garantiert aber keine Fehlerfreiheit. Quelle und Aktualität müssen sichtbar bleiben.

### GAI-08 – Optionen und nächste Schritte vorschlagen

**Aufgabe:** Mögliche Terminfenster, Rückfragen, Bearbeitungsschritte oder Antwortvarianten vorschlagen.
**Wert:** Reduziert Denk- und Koordinationslast.
**Voraussetzung:** valide Daten und klarer Entscheidungsrahmen.
**Grenze:** Vorschlag ist keine Zusage oder Entscheidung.

### GAI-09 – Übersetzen und an Zielgruppen anpassen

**Aufgabe:** Verständliche, mehrsprachige oder adressatengerechte Fassungen erzeugen.
**Wert:** Kleine Betriebe können professionelle Kommunikation ohne eigene Sprach- oder Redaktionsteams leisten.
**Voraussetzung:** bestätigte Sachinformation und fachliche Prüfung bei kritischen Inhalten.
**Grenze:** Übersetzung kann Bedeutung verschieben; Vertrags- und Sicherheitstexte benötigen Fachprüfung.

---

## 5. Was nicht primär GenAI ist

Viele wertvolle Verbesserungen sind keine GenAI-Aufgaben. Die AI Start Map muss sie trotzdem empfehlen können.

| Aufgabe | Passender Mechanismus |
|---|---|
| Eindeutige Auftrags- oder Objekt-ID | Datenmodell / Barcode / QR / klare Arbeitsregel |
| Statuswechsel nach realem Ereignis | Workflow-Regel und menschliche Bestätigung |
| Preis-, Steuer- oder Summenberechnung | deterministische Berechnung |
| Terminprüfung gegen Personal, Dauer und Fahrtzeit | Constraint-Logik / Kalenderdaten |
| Fälligkeit und Erinnerungstermin | Regel / Scheduler |
| Zahlungseingang zuordnen | strukturierter Abgleich mit Toleranz- und Ausnahmefällen |
| Zugriffsrechte | Rollen- und Berechtigungssystem |
| Originalbeleg erhalten | Dokumentenablage und Aufbewahrungsregel |
| Nachricht tatsächlich senden | freigegebene Systemaktion |
| Physischer Lagerort | Kennzeichnung und bestätigtes Scan-/Buchungsereignis |

Die stärkste Lösung ist daher oft:

> GenAI für Verständnis und Entwurf + deterministische Logik für Wahrheit und Aktion + Mensch für Freigabe und Verantwortung.

---

## 6. Zuordnung der 12 Problemfamilien zu sinnvoller KI-Unterstützung

| Problemfamilie | Sinnvolle GenAI-Rolle | Was ohne GenAI gelöst werden muss | Menschliche Grenze |
|---|---|---|---|
| PF-01 Verteilte Vorgangsinformationen | Inhalte zuordnen, Verlauf zusammenfassen, offene Punkte extrahieren | gemeinsamer Vorgangsanker und Ablage | Zuordnung und aktueller Stand bestätigen |
| PF-02 Anfragen gehen unter | klassifizieren, Kerndaten extrahieren, Missing Info und Antwortentwurf | verantwortlicher Eingang, Deduplizierung, Status | Annahme, Ablehnung, Priorität, Zusage |
| PF-03 Mehrfachübertragung | Dokument/Nachricht in Zielstruktur überführen | führende Quelle, Schnittstelle, Validierungsregeln | kritische Felder bestätigen |
| PF-04 Status und Übergaben unklar | Historie zusammenfassen, nächste Aktion und Blockade vorschlagen | wenige Statuswerte, Ereignislogik, Verantwortlicher | Status und Abschluss bestätigen |
| PF-05 Objekt/Auftrag/Ort nicht verbunden | Sonderwünsche strukturieren, Suchhinweise aus bestätigten Daten | physische ID, echter Ablageort, Scan-/Buchungsregel | Identität, Ort und Herausgabe prüfen |
| PF-06 Termine ohne Constraints | Anfrage verstehen, fehlende Daten erkennen, Optionen formulieren | aktuelle Kapazitäts- und Kalenderlogik | verbindlichen Termin zusagen |
| PF-07 Änderungen/Freigaben | Befund strukturieren, Soll/Ist erklären, Kundenfrage entwerfen | Versionierung, Stoppstatus, Freigabeberechtigung | Technik, Preis, Termin und Zustimmung |
| PF-08 Feldnachweis fehlt | Sprache/Fotos/Bon zu Einsatznotiz verbinden | Einsatzanker, mobile Ablage, Rechnungsregeln | Zeit, Material, Leistung und Abnahme |
| PF-09 Zahlung/Beleg offen | Belege auslesen, Erinnerungen formulieren, Ausnahme zusammenfassen | Rechnungs-/Zahlungsquelle, Fristen, GoBD-Prozess | Betrag, Zuordnung, Versand, Eskalation |
| PF-10 Material/WIP unklar | Auftrag in Aufgaben/Stücklistenvorschlag zerlegen, Widersprüche markieren | Artikel-/Variantenlogik, Bestandsereignisse | Mengen, Qualität, Charge, Versand |
| PF-11 Inhaber ist Wissenszentrum | Übergaben, Q&A über bestätigtes Wissen, Standardantwortentwürfe | gemeinsamer Zugriff, Rollen, Dokumentationsregel | Ausnahmen und sensible Entscheidungen |
| PF-12 Dokumente/freie Texte | OCR/Verstehen, Felder extrahieren, Unsicherheit markieren | Zielschema, Originalablage, harte Validierung | kritische Daten und Weiterverarbeitung |

### Kernerkenntnis der Matrix

GenAI löst selten eine Problemfamilie allein. Sie bearbeitet vor allem den **unstrukturierten Informationsanteil**. Die organisatorische und technische Prozesswahrheit muss separat hergestellt werden.

---

## 7. Vertiefung der 10 Solution Patterns durch die GenAI-Recherche

### SP-01 – Gemeinsamer Anfrageeingang mit Missing-Info-Prüfung

- **GenAI-Aufgabe:** Anfrage verstehen, Kategorie und Kerndaten vorschlagen, fehlende Angaben benennen, Rückfrage entwerfen.
- **Deterministischer Kern:** Anfrage-ID, Deduplizierungsmerkmale, Status, Verantwortlichkeit, SLA/Frist.
- **Nicht autonom:** Dringlichkeit bei Notfällen, verbindliche Annahme, Termin, Preis.
- **Pilot:** 30 echte Anfragen eines Kanals; KI erzeugt nur Anfragekarte und Missing-Info-Liste.
- **Messung:** Erfassungszeit, Anteil vollständiger Anfragen, übersehene Anfragen, Korrekturquote der Felder.
- **Abbruchkriterium:** häufige falsche Zuordnung oder mehr Nacharbeit als Zeitersparnis.

### SP-02 – Einfache Vorgangsakte mit Status und nächstem Schritt

- **GenAI-Aufgabe:** Verlauf verdichten, Entscheidungen und offene Punkte extrahieren, Übergabe formulieren.
- **Deterministischer Kern:** Vorgangs-ID, Statuswerte, Verantwortlicher, Zeitstempel, Audit Trail.
- **Nicht autonom:** Status auf „fertig“ setzen, Blockade aufheben, Kundeninformation senden.
- **Pilot:** 20 laufende Vorgänge mit einer automatisch vorbereiteten Tagesübersicht.
- **Messung:** Suchzeit, Rückfragen, vergessene Schritte, Richtigkeit des vorgeschlagenen nächsten Schritts.

### SP-03 – Mobile Einsatzdokumentation aus Sprache, Fotos und Bon

- **GenAI-Aufgabe:** Audio transkribieren, Tätigkeit/Material/Zeitvorschläge extrahieren, Fotos und Bon beschreiben, eine Einsatznotiz erzeugen.
- **Deterministischer Kern:** Einsatz-ID, Upload-Zuordnung, Pflichtfelder, Preisquelle, Speicherung der Originale.
- **Nicht autonom:** Zusatzleistung anerkennen, Zeit/Menge endgültig setzen, Rechnung erzeugen oder senden.
- **Pilot:** fünf bis zehn echte Einsätze; nur Notizentwurf, keine nachgelagerte Buchung.
- **Messung:** Dokumentationszeit, Vollständigkeit, Korrekturen pro Feld, Tage bis Rechnungsbereitschaft, vergessene Positionen.
- **Besondere Eignung:** sehr hoch, weil Input bereits smartphonefähig und unstrukturiert ist.

### SP-04 – Objekt-ID und echter Ablageort

- **GenAI-Aufgabe:** freie Kundenwünsche strukturieren, Objektbeschreibung vereinheitlichen, fehlende Annahmeangaben markieren.
- **Deterministischer Kern:** robuste Kennung am Gegenstand, Auftrags-ID, physischer Ort, Scan-/Buchungsereignis.
- **Nicht autonom:** Standort raten, Objekt freigeben oder Abholberechtigung entscheiden.
- **Pilot:** ID und Ortsfeld ohne KI einführen; GenAI erst für Annahmenotiz testen.
- **Messung:** Suchzeit, Fehlzuordnungen, fehlende Angaben, Korrekturquote.
- **Entscheidung:** Hier ist Ordnung zwingend vor KI. Ein KI-first-Versprechen wäre irreführend.

### SP-05 – Termin-Anfrage mit Kapazitätsprüfung

- **GenAI-Aufgabe:** Wunsch verstehen, Leistung/Dauer/Ort extrahieren, Rückfrage und Alternativen formulieren.
- **Deterministischer Kern:** Kalender, Personal, Qualifikation, Dauer, Wegzeit, Material, Sperrzeiten.
- **Nicht autonom:** verbindlich buchen, Personal bewerten, Ausnahmen zusagen.
- **Pilot:** KI bereitet drei Optionen vor; Inhaber prüft jede Option.
- **Messung:** Abstimmungsschleifen, Fehlbuchungen, Zeit bis Bestätigung, manuelle Korrekturquote.
- **Abbruchkriterium:** Kapazitätsdaten sind nicht aktuell; dann kann die KI keine belastbaren Slots vorschlagen.

### SP-06 – Dokument-zu-Datensatz mit Unsicherheitsprüfung

- **GenAI-Aufgabe:** Dokumenttyp und Felder erkennen, strukturierte Ausgabe erzeugen, Unsicherheit und Widerspruch markieren.
- **Deterministischer Kern:** Zielschema, Datentypen, Wertebereiche, Summenprüfung, Originalbezug, Version.
- **Nicht autonom:** buchen, zahlen, Vertragsinhalt verbindlich interpretieren.
- **Pilot:** ein Dokumenttyp, maximal zehn Felder, 50 repräsentative Dokumente.
- **Messung:** Feldgenauigkeit, kritische Fehler, manuelle Bearbeitungszeit, Anteil „nicht sicher“.
- **Abbruchkriterium:** kritische Fehler werden nicht zuverlässig markiert.

### SP-07 – Zusatzarbeit und dokumentierte Freigabe

- **GenAI-Aufgabe:** Befund aus Sprache/Fotos strukturieren, Auswirkungen verständlich erklären, Kundenanfrage entwerfen.
- **Deterministischer Kern:** Version, Stoppstatus, Berechtigung, Freigabeereignis, Zeitstempel.
- **Nicht autonom:** technische Diagnose, Preis, Fortsetzung, Zustimmung.
- **Pilot:** nur Änderungsnotiz und Kommunikationsentwurf; bestehender Freigabekanal bleibt erhalten.
- **Messung:** Zeit bis Freigabe, Streitfälle, fehlende Nachweise, Nacharbeit.

### SP-08 – Material- und Produktionsboard

- **GenAI-Aufgabe:** freie Aufträge in Aufgabenvorschläge zerlegen, Variantenhinweise und mögliche Fehlteile markieren, Schichtübergaben zusammenfassen.
- **Deterministischer Kern:** Artikel, Varianten, Stückliste, Bestand, Charge, Qualitätsstatus.
- **Nicht autonom:** Bestand korrigieren, Charge freigeben, Qualitätsentscheidung treffen.
- **Pilot:** eine Produktfamilie; KI nur für Auftragszerlegung und Missing-Info.
- **Messung:** Planungszeit, Fehlteile, Variantenfehler, Korrekturquote.
- **Entscheidung:** Bei fehlender Stammdatenqualität zuerst fachliche Struktur, nicht GenAI.

### SP-09 – Rechnungsgrundlage und Zahlungsnachverfolgung

- **GenAI-Aufgabe:** bestätigte Leistungsdaten in Rechnungspositionsentwurf übersetzen, offene Informationen und Belege markieren, Zahlungserinnerung formulieren.
- **Deterministischer Kern:** Preis- und Steuerlogik, Rechnungsnummer, Fälligkeit, Zahlungseingang, GoBD-konforme Ablage.
- **Nicht autonom:** Preis festlegen, Rechnung versenden, Zahlung rechtlich eskalieren.
- **Pilot:** aus zehn bestätigten Leistungsnachweisen ausschließlich Entwürfe erzeugen.
- **Messung:** Zeit bis Rechnungsentwurf, Korrekturen, vergessene Leistungen, Days-to-Invoice.

### SP-10 – Übergabe- und Wissensnotiz

- **GenAI-Aufgabe:** Diktat/Notiz in „Was passiert? Was offen? Wer übernimmt?“ strukturieren; bestätigte Historie mit RAG zusammenfassen.
- **Deterministischer Kern:** Vorgangszuordnung, Berechtigung, Aktualität, Verantwortungsübernahme.
- **Nicht autonom:** fachliche Ausnahme entscheiden, sensible Informationen breit zugänglich machen.
- **Pilot:** zwei Wochen lang nur Übergaben für einen Prozess erzeugen.
- **Messung:** Rückfragen, Suchzeit, Übernahmefehler, Aktualitätsfehler, Nutzungsquote.

---

## 8. Neue fachliche Entscheidungsmatrix für AI Start Map

Die Empfehlung sollte nicht allein aus Problemfamilie und Digitalreife entstehen. Sie benötigt sechs Gates.

### Gate 1 – Aufgabenfit

Enthält der Engpass eine Aufgabe, die GenAI gut bearbeiten kann: verstehen, extrahieren, klassifizieren, zusammenfassen, entwerfen, suchen oder übersetzen?

- **Nein:** klassische Prozessverbesserung oder Automation empfehlen.
- **Ja:** Gate 2.

### Gate 2 – Vorgangsanker

Kann jeder Input eindeutig einem Kunden, Auftrag, Objekt, Einsatz oder Datum zugeordnet werden?

- **Nein:** zuerst minimalen Anker schaffen.
- **Ja:** Gate 3.

### Gate 3 – Zieloutput

Ist festgelegt, wie ein brauchbares Ergebnis aussieht: Felder, Vorlage, Kategorien, nächster Schritt?

- **Nein:** Zielschema oder Muster definieren.
- **Ja:** Gate 4.

### Gate 4 – Prüfbarkeit

Kann ein Mensch schnell erkennen, ob der Output korrekt ist, und ihn korrigieren?

- **Nein:** kein operativer GenAI-Einsatz oder nur risikoarmer Test.
- **Ja:** Gate 5.

### Gate 5 – Fehlerfolgen

Was passiert bei einem Fehler?

- **Niedrig:** Entwurf kann mit Stichproben geprüft werden.
- **Mittel:** jede Ausgabe vor Nutzung prüfen.
- **Hoch:** GenAI nur unterstützend, mit Fachprüfung, harten Regeln und gegebenenfalls ohne nachgelagerte Aktion.

### Gate 6 – Daten und Berechtigung

Dürfen die Informationen verarbeitet werden, ist der Anbieter freigegeben und sind Zugriff, Speicherung und Löschung geklärt?

- **Nein:** keine Einführung vor Klärung.
- **Ja:** Pilot definieren.

---

## 9. Welche Autonomiestufe ist für Kleinunternehmen passend?

| Stufe | Beschreibung | Geeignete Beispiele | Empfehlung |
|---|---|---|---|
| A0 Keine KI | klare Regel oder Standardsoftware reicht | ID, Statusliste, Frist | ausdrücklich empfehlen, wenn besser |
| A1 Persönliche Assistenz | Nutzer gibt Input ein, KI erstellt einmaligen Entwurf | Text, Zusammenfassung, Ideen | niedrigster Einstieg |
| A2 Eingebetteter Entwurf | KI verarbeitet Vorgangsdaten, Mensch bestätigt jeden Output | Einsatznotiz, Anfragekarte, Rechnungsentwurf | Standardziel für viele KU |
| A3 Kontrollierter Workflow | bestätigter Output löst regelbasierte Folgeaktionen aus | Ablage, Aufgabe, vorbereitete Nachricht | erst nach Pilot und Messung |
| A4 Begrenzte Agentenaktion | KI wählt Werkzeuge innerhalb enger Grenzen, Freigabe vor Außenwirkung | interne Recherche, Zusammenstellung | nur bei stabilen Prozessen |
| A5 Autonome Außenwirkung | KI sendet, bucht, bezahlt oder entscheidet selbst | Preis, Termin, Mahnung, Herausgabe | für typische AI-Start-Map-Fälle nicht als Start empfehlen |

Der Regelfall für AI Start Map sollte **A2** sein. Das ist konkret genug, um Nutzen zu erzeugen, aber kontrolliert genug, um Fehler und Vertrauensverlust zu begrenzen.

---

## 10. Risiken und notwendige Schutzmaßnahmen

### 10.1 Sachlich falsche, aber plausible Ausgaben

GenAI kann überzeugend formulieren, obwohl eine Angabe falsch oder erfunden ist. Die Wirkungsforschung zeigt, dass der Nutzen stark vom Aufgabenfit abhängt und KI bei ungeeigneten Aufgaben sogar die menschliche Trefferquote verschlechtern kann. Deshalb:

- keine fehlenden Nutzerfakten ergänzen,
- Unsicherheit sichtbar machen,
- Original und KI-Ausgabe nebeneinander erhalten,
- kritische Felder deterministisch validieren,
- Außenwirkung erst nach Freigabe.

### 10.2 Datenschutz und vertrauliche Informationen

Die OECD nennt Sorgen um eingegebene Informationen als eines der häufigsten Hemmnisse. Der EDPB empfiehlt eine systematische Risikoanalyse und technische sowie organisatorische Maßnahmen für LLM-Systeme. [EDPB: AI Privacy Risks & Mitigations](https://www.edpb.europa.eu/documents/support-pool-of-experts/ai-privacy-risks-mitigations-large-language-models-llms_en)

Für KU bedeutet das mindestens:

- nur erforderliche Daten verarbeiten,
- private und betriebliche Konten trennen,
- keine Gesundheits-, Finanz-, Personal- oder Vertragsdaten in nicht freigegebene Consumer-Tools kopieren,
- Anbieter, Speicherung, Training mit Eingaben und Löschregeln prüfen,
- Rollen und Zugriff begrenzen,
- sensible Bilder und Audios besonders behandeln.

### 10.3 Sicherheitsrisiken

Das BSI weist darauf hin, dass generative Modelle neue IT-Sicherheitsrisiken schaffen und bekannte Risiken verstärken können. Für kleine Betriebe sind insbesondere Schatten-IT, Datenabfluss, schädliche Inhalte in Dokumenten und unkontrollierte Tool-Aktionen relevant. [BSI: Generative KI-Modelle – Chancen und Risiken](https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/KI/Generative_KI-Modelle.html), [BSI: Sichere generative KI in Organisationen](https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/Publikationen/Broschueren/Management_Blitzlicht/Management_Blitzlicht_Generative-KI.pdf?__blob=publicationFile&v=3)

### 10.4 KI-Kompetenz

Nach Artikel 4 des EU AI Act müssen Anbieter und Betreiber von KI-Systemen Maßnahmen zur Förderung der KI-Kompetenz der mit den Systemen arbeitenden Personen treffen. Die EU-Kommission betont einen risikobasierten, kontextabhängigen Ansatz; ein bestimmtes Zertifikat ist nicht vorgeschrieben. [EU-Kommission: AI Literacy Q&A](https://digital-strategy.ec.europa.eu/en/faqs/ai-literacy-questions-answers)

Eine kleine Einführung sollte daher mindestens vermitteln:

- wofür das System eingesetzt werden darf,
- welche Daten nicht eingegeben werden dürfen,
- welche Fehler typisch sind,
- was geprüft werden muss,
- wer bei einem Fehler entscheidet,
- wie eine KI-Ausgabe korrigiert oder verworfen wird.

### 10.5 Proportionalität

NIST empfiehlt, Risiken über den gesamten Lebenszyklus zu identifizieren, zu messen, zu steuern und zu überwachen. Für ein Kleinunternehmen muss das nicht zu einem Großkonzern-Prozess werden. Ein angemessenes Minimum ist: Use-Case-Steckbrief, Datenklassen, Freigabegrenze, Testset, Fehlerlog und verantwortliche Person. [NIST AI RMF – Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)

---

## 11. Messmodell: Woran erkennt man echten Nutzen?

Die AI Start Map sollte keine unprüfbaren Versprechen wie „30 % effizienter“ ausgeben. Sie sollte pro empfohlenem Pilot zwei bis vier konkrete Messgrößen auswählen.

### 11.1 Zeit

- Minuten pro Anfrage, Einsatz, Dokument oder Übergabe
- Tage vom Einsatz bis zur Rechnungsbereitschaft
- Suchzeit pro Vorgang
- Anzahl Abstimmungsschleifen

### 11.2 Qualität

- Anteil vollständiger Datensätze
- Korrekturen pro kritischem Feld
- vergessene Leistungen oder Anhänge
- Fehlzuordnungen
- Anteil korrekt markierter Unsicherheiten

### 11.3 Prozesswirkung

- unbearbeitete Anfragen nach 24/48 Stunden
- offene Vorgänge ohne nächsten Schritt
- Terminumbuchungen
- Zeit bis Freigabe
- Rechnungen ohne bestätigte Grundlage

### 11.4 Akzeptanz

- Anteil der Fälle, in denen der Entwurf verwendet wird
- subjektive Entlastung
- Gründe für Verwerfen oder Nachbearbeiten
- Nutzungsabbrüche wegen zu vieler Schritte

### 11.5 Sicherheitsindikatoren

- kritische Fehler
- falsch ausgelöste Aktionen
- Datenschutzvorfälle
- Ausgaben ohne ausreichende Quelle
- Umgehung des vorgesehenen Freigabeschritts

---

## 12. Pilotmethode für Kleinunternehmen

Ein sinnvoller Pilot ist klein, echt und rückbaubar.

1. **Einen Engpass wählen**, nicht den gesamten Betrieb.
2. **Eine Ausgabe definieren**, zum Beispiel eine Einsatznotiz.
3. **10–50 repräsentative echte Fälle** auswählen; bei häufigen Vorgängen eher mehr.
4. **Baseline messen:** Zeit, Fehler, fehlende Angaben.
5. **KI nur als Entwurfsschicht** einsetzen.
6. **Jeden Output prüfen** und Korrekturen protokollieren.
7. **Nutzen und Risiken vergleichen.**
8. Erst danach entscheiden: stoppen, verbessern oder eine regelbasierte Folgeaktion ergänzen.

Für seltene, hochriskante Prozesse sind zehn Fälle möglicherweise zu wenig. Dann ist ein sicherer Pilot unter Umständen nicht wirtschaftlich; AI Start Map sollte das offen sagen.

---

## 13. Was Kleinunternehmen wirklich brauchen

Aus der kombinierten Pain-Point- und GenAI-Recherche ergeben sich acht Bedürfnisse:

1. **Problemklarheit statt Tool-Shopping.**
2. **Eine Lösung, die mit bestehenden Kanälen beginnt**, besonders Smartphone, E-Mail und vorhandenen Dokumenten.
3. **So wenig zusätzliche Erfassung wie möglich.**
4. **Ein sichtbares Ergebnis**, das sofort verständlich ist.
5. **Klare menschliche Kontrolle**, ohne unklare Automatisierung.
6. **Einen kleinen Pilot mit Messgrößen**, statt eines großen Transformationsprojekts.
7. **Datenschutz- und Sicherheitsgrenzen in Alltagssprache.**
8. **Eine Ausbaureihenfolge**, die erst nach bewiesenem Nutzen automatisiert.

Der Bedarf ist damit nicht „mehr KI-Wissen“ im abstrakten Sinn, sondern eine konkrete Übersetzung:

```text
mein Problem
→ geeignete KI-Fähigkeit
→ notwendige Prozessbasis
→ zukünftiger Ablauf
→ menschliche Grenze
→ kleiner Test
→ messbarer Erfolg
```

---

## 14. Die spezifische Rolle der AI Start Map

### 14.1 Sie identifiziert die richtige Aufgabe

Ein Unternehmer beschreibt Symptome. AI Start Map rekonstruiert Prozess, Engpass, Ursache und betroffene Problemfamilie. Erst danach prüft sie, ob ein GenAI-Fähigkeitsmuster passt.

### 14.2 Sie trennt KI, Automation und Ordnung

Sie muss sichtbar sagen können:

- „Hier hilft GenAI sofort beim Strukturieren.“
- „Hier braucht es zuerst eine eindeutige Objekt-ID.“
- „Hier reicht eine normale Kalenderregel.“
- „Hier kann ein bestätigter KI-Entwurf später eine Automation auslösen.“

### 14.3 Sie entwirft den Zielworkflow

Die Empfehlung soll nicht bei „Nutze KI für Dokumentation“ enden, sondern konkret zeigen:

```text
Nutzer sendet Sprache + Fotos + Bon
→ System ordnet alles dem Einsatz zu
→ GenAI erstellt eine Einsatznotiz
→ Regeln prüfen Pflichtfelder
→ Nutzer korrigiert und bestätigt
→ bestätigte Daten werden gespeichert
→ optional entsteht ein Rechnungsentwurf
```

### 14.4 Sie macht die Rollen sichtbar

Jede Empfehlung sollte vier Spalten enthalten:

| Nutzer tut | GenAI tut | System/Regeln tun | Mensch prüft/entscheidet |
|---|---|---|---|

Damit wird Überautomatisierung schon in der Darstellung verhindert.

### 14.5 Sie liefert einen umsetzbaren Einstieg

Die Start Map braucht pro Empfehlung:

- einen 1–2-Satz-Nutzen,
- einen anschaulichen Vorher-/Nachher-Ablauf,
- benötigte Eingänge,
- Minimalvoraussetzungen,
- menschliche Freigaben,
- einen Pilotumfang,
- zwei bis vier Messgrößen,
- eine klare nächste Ausbaustufe.

### 14.6 Sie schützt vor dem falschen Tool

Erst wenn der Zielworkflow klar ist, darf die Frage nach Werkzeugen kommen. Ein CRM, Chatbot, OCR-Service, Automationswerkzeug oder agentisches System ist Mittel, nicht Diagnose.

---

## 15. Konsequenzen für die Wissens- und Produktarchitektur

### 15.1 Neue Wissensart: GenAI Capability Patterns

Die neun GAI-Muster sollten als eigene strukturierte Wissensart gepflegt werden. Sie sind weder reale Fälle noch Solution Patterns.

Empfohlene Felder:

```json
{
  "capability_id": "GAI-01",
  "name": "Freie Sprache in Struktur überführen",
  "input_modalities": ["text", "audio"],
  "output_type": "structured_draft",
  "suitable_tasks": [],
  "required_process_foundation": [],
  "human_review": [],
  "failure_modes": [],
  "measurement": [],
  "source_refs": []
}
```

### 15.2 Solution Patterns erweitern

Jedes SP sollte künftig zusätzliche maschinenlesbare Felder besitzen:

- `genai_capabilities`
- `deterministic_components`
- `human_decisions`
- `input_modalities`
- `target_output_schema`
- `autonomy_level`
- `risk_level`
- `pilot_design`
- `success_metrics`
- `stop_conditions`

### 15.3 Harte Regeln gehören nicht ins semantische Retrieval

Deterministisch im Code oder strukturierten Katalog sollten bleiben:

- Mindestvoraussetzungen,
- Ausschlussgründe,
- zulässige Autonomiestufe,
- kritische Freigaben,
- Pflichtbestandteile der Empfehlung,
- Priorisierungslogik.

RAG kann ergänzen:

- ähnliche Prozessevidenz,
- typische Symptome und Ursachen,
- gute Rückfragen,
- Umsetzungsvarianten,
- bekannte Fehlerbilder,
- Quellen- und Risikohinweise.

### 15.4 Keine Tooldaten in die stabile fachliche Schicht mischen

Toolnamen, Preise und Produktfunktionen ändern sich schnell. Die stabile Architektur sollte zuerst Fähigkeit und Zielworkflow auswählen. Ein separater, aktualisierbarer Tool-Layer kann später prüfen, welches Produkt die Anforderungen erfüllt.

---

## 16. Empfohlene neue Research-Batches

### Batch 05 – GenAI Capability Evidence

Ziel: Die neun Fähigkeiten mit belastbaren Quellen, realen KU-Szenarien, Grenzen und Metriken hinterlegen.

Ergebnis:

- Capability-Katalog,
- pro Fähigkeit positive und negative Einsatzbeispiele,
- Aufgabenfit- und Risiko-Gates,
- Quellennachweise.

### Batch 06 – Solution Pattern Validation

Ziel: Die zehn Solution Patterns mit echten Kleinunternehmensfällen testen.

Pro SP:

- mindestens drei Branchenvarianten,
- ein ungeeigneter Gegenfall,
- Minimalvoraussetzungen,
- Pilotdesign,
- menschliche Freigabe,
- messbare Erfolgskriterien.

### Batch 07 – Failure and Overautomation Cases

Ziel: Fälle sammeln, in denen GenAI falsch, unnötig oder zu autonom eingesetzt wurde.

Schwerpunkte:

- falsche Vorgangszuordnung,
- erfundene Pflichtangaben,
- falsche Belegwerte,
- Terminversprechen ohne Kapazität,
- veraltete RAG-Quelle,
- autonome Kundenkommunikation,
- Datenschutz und Schatten-IT.

### Batch 08 – Tool and Implementation Layer

Erst danach: aktuelle Produkte und technische Referenzarchitekturen. Diese Wissensschicht muss zeitlich versioniert und häufiger aktualisiert werden als Prozess- und Capability-Wissen.

---

## 17. Akzeptanzkriterien für eine gute AI-Start-Map-Empfehlung

Eine Empfehlung ist fachlich überzeugend, wenn sie:

1. auf bestätigten Nutzerfakten beruht,
2. eine primäre Problemfamilie benennt,
3. den tatsächlichen Engpass erklärt,
4. ein konkretes Solution Pattern auswählt,
5. GenAI-, Regel- und Menschenrolle trennt,
6. notwendige Ordnung nur dort vorschaltet, wo sie wirklich nötig ist,
7. keine autonome Außenwirkung als ersten Schritt empfiehlt,
8. einen kleinen Pilot nennt,
9. messbare Erfolgskriterien enthält,
10. Risiken und Stop-Bedingungen verständlich macht,
11. keine Toolmarke mit der Lösung verwechselt,
12. keine fremden Vergleichsfälle als Nutzerfakten ausgibt.

---

## 18. Schlussfolgerung

Die Recherche bestätigt die Grundidee der AI Start Map, präzisiert aber ihren eigentlichen Wert:

> AI Start Map soll Kleinunternehmen nicht zeigen, wo generative KI theoretisch möglich ist. Sie soll erkennen, welche unstrukturierte Aufgabe im realen Ablauf GenAI sinnvoll übernehmen kann, welche Prozesswahrheit vorher oder parallel geschaffen werden muss und an welcher Stelle der Mensch die Kontrolle behält.

Für viele Kleinunternehmen ist der beste erste Schritt kein Chatbot und kein autonomer Agent. Es ist ein **prüfbarer KI-Entwurf innerhalb eines konkreten Vorgangs**:

- aus einer Anfrage wird eine vollständige Anfragekarte,
- aus Sprache, Fotos und Bon wird eine Einsatznotiz,
- aus einem Dokument wird ein geprüfter Datensatz,
- aus einem Verlauf wird eine Übergabe,
- aus bestätigten Leistungen wird ein Rechnungsentwurf.

Die übergreifende Produktregel lautet:

> Nutze GenAI früh für unstrukturierte Informationen. Nutze Regeln für eindeutige Wahrheit und Aktionen. Lass Menschen dort entscheiden, wo Fehler Geld, Rechte, Sicherheit, Vertrauen oder reale Gegenstände betreffen.

Damit wird aus der Pain-Point-Diagnose eine belastbare Lösungslogik – und aus der AI Start Map ein System, das nicht nur KI-Potenzial verspricht, sondern einen sicheren, kleinen und messbaren Einstieg in einen besseren Arbeitsablauf zeigt.

---

## 19. Kernquellen

1. [OECD – Generative AI and the SME Workforce (2025)](https://www.oecd.org/en/publications/generative-ai-and-the-sme-workforce_2d08b99d-en.html)
2. [OECD – How are SMEs using generative AI?](https://www.oecd.org/en/publications/generative-ai-and-the-sme-workforce_2d08b99d-en/full-report/component-4.html)
3. [OECD – Are SMEs prepared for generative AI?](https://www.oecd.org/en/publications/generative-ai-and-the-sme-workforce_2d08b99d-en/full-report/component-6.html)
4. [OECD – AI adoption by small and medium-sized enterprises (2025)](https://www.oecd.org/en/publications/ai-adoption-by-small-and-medium-sized-enterprises_426399c1-en.html)
5. [OECD – The effects of generative AI on productivity, innovation and entrepreneurship (2025)](https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/06/the-effects-of-generative-ai-on-productivity-innovation-and-entrepreneurship_da1d085d/b21df222-en.pdf)
6. [Eurostat – Use of artificial intelligence in enterprises (2025 data)](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Use_of_artificial_intelligence_in_enterprises)
7. [Harvard Business School – Navigating the Jagged Technological Frontier](https://www.hbs.edu/faculty/Pages/item.aspx?num=64700)
8. [NIST – AI RMF: Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)
9. [EDPB – AI Privacy Risks & Mitigations for LLMs](https://www.edpb.europa.eu/documents/support-pool-of-experts/ai-privacy-risks-mitigations-large-language-models-llms_en)
10. [EDPB – Data protection guide for small business](https://www.edpb.europa.eu/sme_en)
11. [EU-Kommission – AI Literacy Q&A](https://digital-strategy.ec.europa.eu/en/faqs/ai-literacy-questions-answers)
12. [BSI – Künstliche Intelligenz: Informationen und Empfehlungen](https://www.bsi.bund.de/DE/Themen/Unternehmen-und-Organisationen/Informationen-und-Empfehlungen/Kuenstliche-Intelligenz/kuenstliche-intelligenz_node.html)
