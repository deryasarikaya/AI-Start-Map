# AI Start Map – zehn reale KMU-Fallbeispiele für Prozessdiagnostik, Playbooks und Tests

**Recherchezeitpunkt:** 16. Juli 2026  
**Quellentyp:** öffentlich zugängliche, pseudonyme Erstberichte auf Reddit; ergänzend offizielle technische Dokumentation für die Machbarkeit der n8n-Prototypen.

## Methodik und Genauigkeit

Die zehn Fälle sind **keine eigenen Kundeninterviews**. Es handelt sich um öffentlich beschriebene Betriebe. Die Identitäten bleiben anonym; die Testpersonas am Ende jedes Falls sind synthetische Ableitungen. Jeder Fall enthält mindestens drei modellierbare Prozesse. Wo die Quelle nur Teilstrecken beschreibt, sind Rekonstruktionsschritte ausdrücklich als Analyse und nicht als Tatsache gekennzeichnet.

Kennzeichnung:

- **[Quelle]**: vom Unternehmer bzw. der Unternehmerin selbst öffentlich beschrieben.
- **[Analyse]**: daraus abgeleitete Prozessrekonstruktion oder wirtschaftliche Einordnung.
- **[Unbekannt]**: in der Quelle nicht genannt und bewusst nicht ergänzt.
- **[Testannahme]**: ausschließlich für einen reproduzierbaren Produkttest gesetzter Wert; keine Behauptung über den realen Betrieb.

Reddit-Erstberichte sind wertvoll für konkrete Arbeitsabläufe, aber nicht unabhängig verifiziert. Zahlen und Aussagen werden deshalb als Selbstauskünfte behandelt.

| Fall | Branche | Kernprozess | Hauptproblem | Wichtigstes Automatisierungspotenzial |
| --- | --- | --- | --- | --- |
| 1 | Elektro-/technischer Servicebetrieb | Vor-Ort-Aufnahme bis Angebot und Arbeitsunterlage | Notizen, Pläne, Fotos und Angebot liegen auf drei Geräten in inkompatiblen Systemen | Strukturierte mobile Auftragsaufnahme mit automatisch erzeugtem Angebots- und Job-Datensatz |
| 2 | Etsy-Shop mit 3D-Druck-Fertigung | Bestellung bis vollständig produzierter und geprüfter Auftrag | Positionen und Einzelteile verlieren sich über mehrere Druck-, Reinigungs- und Prüfphasen | Etsy-Aufträge in Stücklisten und statusfähige Produktionsaufgaben zerlegen |
| 3 | Kleiner Reinigungsbetrieb | Wochenplanung und laufende Umplanung von 160 Einsätzen | Termin-, Wiederholungs-, Gebiets- und Personalrestriktionen machen die Planung zum manuellen „Tetris“ | Regel- und distanzbasierte Planungsvorschläge mit menschlicher Freigabe |
| 4 | Medizinische Solo-Praxis | Leistung bis Versicherungs- und Patientenzahlung | Zuzahlungen werden erst nach dem Besuch berechnet; Forderungen und ein Versicherungsfall bleiben offen | Regelbasierte Revenue-Cycle-Arbeitsliste mit Freigaben und datenschutzkonformer Mahnkaskade |
| 5 | Maßmöbel-/Metallbaubetrieb | Lead bis Projekt bzw. Konsignationsverkauf | Frühere Großkunden brechen weg; kleine Serien sind bei Material- und Zeitkosten kaum tragfähig | Pipeline-, Nachkalkulations- und Konsignationsdaten zu einer belastbaren Go/No-go-Entscheidung verbinden |
| 6 | Tattoo-Solo-Studio | Bücheröffnung bis Termin und Anzahlung | Sehr viele Anfragen konzentrieren sich auf 24 Stunden und müssen kreativ priorisiert werden | Vollständigkeitsprüfung, transparentes Review-Board und Square-Terminübergabe |
| 7 | Solo-Objektverwaltung | Meldung/Inspektion bis Handwerkerauftrag und Abschluss | 47 Einheiten erzeugen zufällige Ereignisse; der Betrieb darf nicht vom Gedächtnis einer Person abhängen | Wartungstriage und Inspektionsbefunde als nachverfolgte Aufgaben mit Eskalation |
| 8 | Ein-Personen-Kanzlei | Erstkontakt und Mandatsstatuskommunikation | Telefonate unterbrechen Facharbeit; Intake und Statusanfragen sind nicht strukturiert nachverfolgbar | Vertraulicher Intake mit Konflikt-/Freigabegate und geprüften Statusentwürfen |
| 9 | Unabhängige Kfz-Werkstatt | Fahrzeugaufnahme bis Kostenvoranschlag und Mechanikerauftrag | Teile und Arbeitszeiten werden zwischen drei Programmen manuell übertragen | VIN-basierter Angebotsentwurf mit Quellenbeleg und Werkstattleiterfreigabe |
| 10 | Teppichreinigungsfabrik | Abholung/Annahme bis vollständige Rückgabe | Kundendaten und Teppiche werden in editierbaren Tabellen geführt; Löschung und Bestandsdifferenzen sind riskant | Manipulationssicheres ID-/Barcode-Tracking pro Teppich und Übergabekontrolle |

---

# Fall 1: Kleiner Elektro-/technischer Servicebetrieb mit drei Fahrzeugen

## Quellenbasis

Primärquelle ist der Erstbericht eines Verantwortlichen in einem Elektro-/Servicebetrieb: [„What kind of tablet/laptop do you guys carry in the field?“](https://www.reddit.com/r/electricians/comments/1ai9ya1/what_kind_of_tabletlaptop_do_you_guys_carry_in/). Als Branchenabgleich dient ein zweiter, nicht mit dem ersten Betrieb vermischter Bericht eines Solo-Elektrikers: [„What’s the best way to keep track of customers and jobs as a solo electrician?“](https://www.reddit.com/r/electricians/comments/1lblm8r/whats_the_best_way_to_keep_track_of_customers_and/).

## 1. Unternehmenskontext

- **[Quelle] Branche/Angebot:** Elektro- und technischer Außendienst mit allgemeiner Fehlersuche, Umbauten und einzelnen Geräteinstallationen. Der Verantwortliche übernimmt zusätzlich Niederspannungsarbeiten.
- **[Quelle] Größe:** Drei Servicefahrzeuge werden gesteuert. Es gibt „office/service guys“ und Crews; die genaue Zahl der Beschäftigten ist nicht genannt.
- **[Quelle] Arbeitsform:** Hybrid. Der Verantwortliche arbeitet im Büro und fährt mehrmals pro Woche selbst zu Serviceeinsätzen oder hilft auf Baustellen.
- **[Quelle] Kundentypen:** Nicht ausdrücklich genannt.
- **[Unbekannt]** Rechtsform, Umsatz, Region, Privat-/Gewerbekundenanteil, Auftragsvolumen und saisonale Schwankungen.

## 2. Typischer Arbeitsalltag

**Belegte wiederkehrende Aufgaben:** Angebote erstellen, Pläne zeichnen, Material bestellen, telefonischen Support für Büro und Außendienst leisten, Termine planen, Rechnungen erstellen, Niederspannungsarbeiten ausführen und weiterhin selbst Einsätze fahren.

**Belegbare Arbeitsfolge eines typischen Auftrags:**

```text
Vor-Ort-Begehung oder Serviceeinsatz
    ↓
Materialliste auf dem Samsung-Smartphone notieren
    ↓
Pläne und handschriftliche Skizzen auf dem iPad erstellen
    ↓
Fotos erhalten oder aufnehmen und zur Crew-Anweisung annotieren
    ↓
Notizen/Pläne als Screenshot oder PDF über Google Drive/Google Photos übertragen
    ↓
Am Windows-Desktop im Büro das Angebot erstellen
    ↓
Informationen für Crew, Materialbestellung, Termin und Rechnung weiterverwenden
```

- **[Quelle] Parallelität:** Während Angebote und Pläne vorbereitet werden, laufen Telefon-Support, Terminplanung, Materialbestellung und operative Einsätze weiter.
- **[Quelle] Nachträgliche Arbeit:** Der Unternehmer beschreibt ausdrücklich, dass die Angebotsdatei erst am Büro-PC entsteht. Ob dies abends geschieht, ist **nicht** genannt.
- **[Analyse] Engpass:** Nicht die einzelne Notiz-App ist das Kernproblem, sondern dass derselbe Auftrag über mehrere unverbundene Artefakte und Geräte rekonstruiert werden muss.

## 3. Drei konkrete problematische Prozesse

### Prozess 1: Kundenanfrage bis disponierter Serviceeinsatz

```text
Auslöser: Kunde meldet Störung, Umbau oder Installation
    ↓
Anliegen, Ort und Dringlichkeit aufnehmen
    ↓
Entscheidung: telefonisch lösbar oder Vor-Ort-Termin nötig?
    ├─ telefonisch → Verantwortlicher unterstützt Büro/Außendienst
    └─ vor Ort → Fahrzeug/Crew und Termin zuweisen
        ↓
Ergebnis: disponierter Einsatz mit Arbeitsauftrag
```

**[Quelle]** Telefon-Support, Terminplanung und eigene Servicefahrten gehören zum Aufgabenmix. **[Analyse]** Intake-Felder, Dringlichkeitsprüfung und genaue Dispositionsfolge sind nicht beschrieben; gerade deshalb müssen sie im Interview erhoben werden.

### Prozess 2: Begehung bis einsatzfähiges Angebot

```text
Auslöser: Ein Kunde benötigt Fehlersuche, Umbau oder Installation
    ↓
Vor-Ort-Termin / Walkthrough
    ↓
Erfassung von Material auf dem Smartphone
    ↓
Erstellung von Skizze/Plan auf dem iPad
    ↓
Fotos und visuelle Hinweise erfassen
    ↓
Entscheidung: Reichen die Informationen für Kalkulation und Ausführung?
    ├─ Nein → Rückfrage, weitere Messung oder erneuter Informationsabruf
    └─ Ja
        ↓
Manueller Export/Transfer zwischen Samsung, Apple und Windows
        ↓
Angebot am Desktop erstellen
        ↓
Material bestellen, Einsatz planen und Jobinformationen an die Crew geben
        ↓
Ergebnis: Angebot plus verteilte Arbeitsunterlagen
```

Die Schritte bis zum Desktop sind quellenbasiert. Die explizite Vollständigkeitsentscheidung ist **[Analyse]**, weil jeder belastbare Angebotsprozess eine solche Prüfung benötigt, sie aber im Beitrag nicht formal beschrieben wird.

### Prozess 3: Angenommener Auftrag bis Crew-Unterlage und Rechnung

```text
Auslöser: Angebot wird angenommen / Arbeit soll ausgeführt werden
    ↓
Material aus Notizen und Angebot bestimmen und bestellen
    ↓
Plan, Fotos und Annotationen für die Crew zusammenstellen
    ↓
Einsatz terminieren und Rückfragen telefonisch klären
    ↓
Arbeit ausführen und Leistungsinformationen zurückmelden
    ↓
Rechnung erstellen
    ↓
Ergebnis: ausgeführter und fakturierter Auftrag
```

**[Quelle]** Materialbestellung, Crew-Unterstützung, Terminierung, annotierte Fotos und Rechnungsstellung werden genannt. **[Unbekannt]** Annahmekanal, Leistungsrückmeldung, Abnahme und Rechnungssoftware. Die dargestellte Kette ist daher eine **[Analyse]** des End-to-End-Prozesses, keine Behauptung über einzelne Masken oder Rollen.

## 4. Probleme und Engpässe

- **[Quelle] Größter Zeitfresser:** Manuelle Übertragung und Zusammenführung von Materialliste, Plan, Fotos und Angebot.
- **[Quelle] Medienbruch:** Samsung Notes ↔ Apple Notes/iPad ↔ Google Drive/Photos ↔ Windows-Desktop.
- **[Quelle] Mehrfachformate:** Screenshots und PDFs werden erzeugt, nur um Informationen auf dem nächsten Gerät nutzbar zu machen.
- **[Quelle] Verteilte Auftragsakte:** Materialliste auf dem Telefon, Plan auf dem Tablet, Angebot auf dem PC.
- **[Quelle] Personenabhängigkeit:** Der Verantwortliche erstellt Angebote, Pläne, Bestellungen, Support, Planung und Rechnungen selbst.
- **[Analyse] Fehlerquellen:** Veraltete Versionen, verlorene Zuordnung von Foto zu Auftrag, unvollständige Materialpositionen und Übertragungsfehler.
- **[Analyse] Wirtschaftliche Folgen:** Längere Angebotsdurchlaufzeit, weniger verfügbare Zeit für abrechenbare Arbeit, Verzögerungen bei Material und Einsatz, hoher Schlüsselpersonen-Risikoanteil.
- **[Unbekannt]** Tatsächliche Fehlerhäufigkeit, Angebotsquote, durchschnittliche Angebotsdauer und monetärer Schaden.

Der Branchenabgleich zeigt, dass das Muster nicht exotisch ist: Der Solo-Elektriker berichtet von Textnachrichten, Anrufen, zufälligen Notizen und halbfertigen Angeboten in E-Mails sowie vergessenen Follow-ups. Das ist **kein zusätzlicher Fakt über Fall 1**, sondern ein Hinweis auf ein wiederverwendbares Branchenmuster.

## 5. Verwendete Tools

| Tool/Hilfsmittel | Belegt? | Verwendung |
| --- | --- | --- |
| iPad mit Tastatur und Pencil | Ja | Handschriftliche Notizen, Pläne, Bildannotation |
| Samsung S22 Ultra | Ja | Materiallisten, Notizen, Fotos |
| Windows-Desktop | Ja | Angebot und Büroarbeit |
| Samsung Notes | Ja | Notizen auf dem Smartphone |
| Apple Notes/Standard-Notizen-App | Ja | Zeichnen/Notizen auf dem iPad |
| Google Drive | Ja | Manueller Dateitransfer |
| Google Photos | Ja | Fotoübertragung |
| E-Mail, CRM, Buchhaltung, Kalender | Nicht aus der Primärquelle ersichtlich | Nicht ergänzen |

## 6. Vorhandene Lösungen und Workarounds

- **[Quelle]** Screenshots und PDFs dienen als kleinstes gemeinsames Austauschformat.
- **[Quelle]** Google Drive und Google Photos werden als Transferstrecke benutzt.
- **[Quelle]** Annotierte Fotos ersetzen längere telefonische Erklärungen an die Crew und funktionieren gut für visuelle Anweisungen.
- **[Quelle]** Der Unternehmer hat verschiedene Zeichen-Apps getestet, empfindet sie aber als nicht flüssig oder unpräzise.
- **[Quelle]** OneNote wurde erwogen, wirkte für ihn jedoch eher auf Unterricht ausgerichtet.
- **[Analyse] Warum es nicht reicht:** Dateisynchronisation löst nur den Transport. Sie erzeugt noch keinen einheitlichen Auftragsdatensatz mit Material, Fotos, Versionen, Zuständigkeiten und Freigabestatus.

## 7. Fehlende Informationen vor einer Automation

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

## 8. Drei realistische Automatisierungschancen

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

## 9. Eignung für AI Start Map

### Was ein allgemeiner aktueller Fragebogen wahrscheinlich erfasst

- Beruf/Angebot, Mitarbeiter, wiederkehrende Aufgaben, Zeitfresser, Fehler, aktuelle Tools und gewünschte Verbesserung.
- Damit würden „zu viele Tools“, „manuelle Übertragung“ und „Angebote dauern“ sichtbar.

### Was er wahrscheinlich übersieht

- Welches **Artefakt** auf welchem **Gerät/System** entsteht.
- Wie Job-IDs und Versionen heute gebildet werden.
- Ob der eigentliche Engpass Datenerfassung, Datentransfer, Kalkulation oder Freigabe ist.
- Offline-Anforderungen, Bild-/Plangrößen, Rollen und technische Haftung.
- Den Unterschied zwischen „Dateien synchronisieren“ und „prozessfähige strukturierte Daten erzeugen“.

### Notwendige dynamische KI-Rückfragen

1. „Du nennst Telefon, iPad und Desktop: Welche Information entsteht zuerst auf welchem Gerät?“
2. „Welche Daten tippst du für ein Angebot ein zweites Mal ein?“
3. „Was muss zwingend vorhanden sein, bevor du einen Preis nennen kannst?“
4. „Welche Entscheidungen darf nur eine fachlich verantwortliche Person treffen?“
5. „Wie erkennt die Crew, ob ein Plan die neueste Version ist?“
6. „Kann ein Auftrag ohne Netzverbindung aufgenommen werden müssen?“

### Wiederverwendbares Playbook

**Field Intake → Structured Job Record → Human-approved Quote → Versioned Job Pack**

### n8n-Showcase

**Geeignet, aber erst nach Standardisierung des Eingangs.** n8n kann einen Webhook als Eingang bereitstellen und Daten an weitere Systeme verteilen; der n8n-Webhook kann externe Daten empfangen und einen Workflow starten ([offizielle n8n-Dokumentation](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook)).

```text
Mobiles Formular / Webhook
    → Job-ID erzeugen
    → Sprache/Freitext in definiertes Schema extrahieren
    → Pflichtfelder und Konfidenz prüfen
    → Fotos/Plan unter Job-ID speichern
    → Angebotsentwurf erzeugen
    → Freigabeaufgabe an Verantwortlichen
    → nach Freigabe Job-Paket/Entwurf an Büro oder Crew übergeben
```

Nicht sinnvoll wäre ein Showcase, der versucht, Samsung Notes und Apple Notes im Nachhinein zuverlässig „zusammenzuscrapen“. Der bessere Blueprint ändert den Erfassungspunkt.

## 10. Strukturierter Testfall

**Testpersona:** „Elektroservice Nord – Betriebsleiter Emir“ (anonymisiert/synthetisch)  
**Branche:** Elektro-/technischer Außendienst  
**Unternehmensbeschreibung:** Kleiner Hybridbetrieb mit drei Servicefahrzeugen; der Betriebsleiter übernimmt Angebote, Pläne, Material, Support und teilweise Außendienst.

**Antworten auf mögliche Interviewfragen:**

| Frage | Testantwort |
| --- | --- |
| Was bietest du an? | Fehlersuche, Umbauten, einzelne Installationen und Niederspannungsarbeiten. |
| Wie sieht deine Woche aus? | Ich koordiniere drei Fahrzeuge, fahre selbst Einsätze und erledige Angebote, Pläne, Material, Support, Termine und Rechnungen. |
| Wie kommen Kunden? | Unbekannt; muss nachgefragt werden. |
| Wie kommuniziert ihr? | Fotos und visuelle Hinweise mit der Crew; weitere Kanäle unbekannt. |
| Mitarbeiter? | Mehrere Crews/Bürokräfte vorhanden; genaue Zahl unbekannt. |
| Größter Zeitfresser? | Informationen von Smartphone und iPad auf den Büro-PC bringen und für das Angebot zusammensetzen. |
| Wiederholung? | Begehungsdaten, Materiallisten, Fotos und Pläne immer wieder in Angebote/Jobunterlagen übertragen. |
| Fehler/Missverständnisse? | Quelle nennt Synchronisationsprobleme; konkrete Fehlerrate unbekannt. |
| Tools? | Samsung S22 Ultra/Notes, iPad/Pencil/Notes, Windows-Desktop, Google Drive, Google Photos. |
| Wunsch? | Eine portable, robuste Lösung, die Zeichnen erlaubt und mit Telefon und Windows synchronisiert. |

- **Erwartetes Kernproblem:** Fragmentierte Auftragsdaten und doppelte Übertragung – nicht primär „fehlendes CRM“.
- **Erwartete Top 3:** strukturierte Vor-Ort-Aufnahme; Angebotsentwurf mit Freigabe; versioniertes Crew-Job-Paket.
- **Zu vermeidende Fehlentscheidung:** Nur ein neues Tablet oder einen generischen Chatbot empfehlen. Das würde den geräteübergreifenden Datenprozess nicht lösen.

---

# Fall 2: Etsy-Shop für 3D-gedruckte Tabletop-Modelle

## Quellenbasis

Primärquelle ist der detaillierte Erstbericht eines Etsy-Verkäufers: [„Open order management“](https://www.reddit.com/r/EtsySellers/comments/1bgzbtr/open_order_management/). Ein weiterer Etsy-Erstbericht belegt als Branchenabgleich das Skalierungsproblem individueller Auftragsdateien, wird aber nicht als derselbe Betrieb behandelt: [„How do you keep track of your orders?“](https://www.reddit.com/r/EtsySellers/comments/16gxrmo/how_do_you_keep_track_of_your_orders/).

## 1. Unternehmenskontext

- **[Quelle] Branche/Angebot:** 3D-Druck von Tabletop-Wargaming-Teilen, verkauft über Etsy.
- **[Quelle] Produktstruktur:** Ein Auftrag kann bis zu 20 Positionen enthalten; gleiche Teile können in mehreren Aufträgen vorkommen. Manche Produkte bestehen aus mehreren Einzelteilen.
- **[Quelle] Arbeitsform:** Produktion in/bei einer Garage mit Regal und Auftragsboxen; Verkauf online.
- **[Quelle] Team:** Der Beitrag ist in Ich-Form. Ob die Person vollständig allein arbeitet, ist **unbekannt**.
- **[Quelle] Fertigungslogik:** Kleine Teile laufen am Wochenende tagsüber, hohe Teile über Nacht; kleine häufig verkaufte Teile werden teilweise auf Vorrat produziert.
- **[Unbekannt]** Umsatz, durchschnittliche Bestellmenge, Lieferländer, Versanddienst, Rücksendungen, Saisonspitzen und Mitarbeiterzahl.

## 2. Typischer Arbeitsalltag

**Belegte operative Aufgaben:** Etsy-Aufträge prüfen, Aufträge ausdrucken, jedem Auftrag eine Box zuweisen, Drucke anhand der Etsy-Orders-Seite einrichten, Fertigteile abhaken, Resin-Teile reinigen und trocknen, auf kleine Fehler prüfen und mehrteilige Produkte vollständig zusammenstellen.

```text
Neue/offene Etsy-Aufträge prüfen
    ↓
Auftrag ausdrucken und in eine eigene Box am Regal legen
    ↓
Druckläufe über mehrere Aufträge und Bauteile planen
    ├─ kleine Teile tagsüber/am Wochenende
    └─ hohe Teile über Nacht
    ↓
Teil drucken
    ↓
Teil reinigen und trocknen
    ↓
Teil auf kleine Druckfehler prüfen
    ↓
Auf Papier abhaken und in die Auftragsbox legen
    ↓
Vollständigkeit aller Positionen und Unterteile prüfen
    ↓
Auftrag ist produktionsseitig fertig
```

- **[Quelle] Parallelität:** Mehrere Drucker/Druckläufe, unterschiedliche Bauteilgrößen und mehrere Aufträge mit gleichen Teilen laufen parallel.
- **[Quelle] Nachlauf:** Fehlende Kleinteile können einen gesamten Auftrag einen weiteren Tag blockieren.
- **[Unbekannt]** Verpackungs-, Etikettierungs-, Versand- und Kundenkommunikationsschritte sind im Fall nicht beschrieben.

## 3. Drei konkrete problematische Prozesse

### Prozess 1: Etsy-Bestellung bis Stückliste

```text
Auslöser: Etsy-Auftrag mit 1 bis 20 Positionen
    ↓
Auftragsausdruck und physische Box anlegen
    ↓
Positionen aus Etsy lesen und Drucke planen
    ↓
Für jede Position: notwendige Einzelteile bestimmen
    ↓
Drucken → Reinigen → Trocknen → Prüfen
    ↓
Entscheidung: Teil fehlerfrei?
    ├─ Nein → neu drucken; Auftrag verzögert sich
    └─ Ja → abhaken und in Auftragsbox legen
    ↓
Entscheidung: alle Positionen und Unterteile vollständig?
    ├─ Nein → fehlendes Teil suchen/produzieren
    └─ Ja → produktionsfertig
```

### Prozess 2: Produktionsplanung und mehrstufige Fertigung

```text
Auslöser: Offene Teile aus mehreren Aufträgen
    ↓
Gleiche Teile und geeignete Druckjobs gruppieren
    ↓
Entscheidung nach Geometrie/Laufzeit
    ├─ kleine Teile → tagsüber bzw. am Wochenende
    └─ hohe Teile → über Nacht
        ↓
Drucken → Reinigen → Trocknen
    ↓
Status je Einzelteil aktualisieren
    ↓
Ergebnis: prüffähige Teile in den Auftragsboxen
```

### Prozess 3: Qualitäts- und Vollständigkeitsprüfung bis Versandbereitschaft

```text
Auslöser: Ein Teil ist gereinigt und trocken
    ↓
Auf kleine Druckfehler prüfen
    ↓
Entscheidung: Nachdruck erforderlich?
    ├─ ja → neues Druckticket; Auftrag bleibt blockiert
    └─ nein → Teil der richtigen Auftragsbox zuordnen
        ↓
Soll-/Ist-Prüfung aller Positionen und Unterteile
    ↓
Entscheidung: Auftrag vollständig?
    ├─ nein → fehlendes Teil erzeugen oder Lagerbestand suchen
    └─ ja → versandbereit markieren
```

**[Unbekannt]** Verpackung, Versandlabel und tatsächliche Übergabe an den Versanddienst sind nicht beschrieben. Die Prozessgrenze endet deshalb belastbar bei „versandbereit“.

## 4. Probleme und Engpässe

- **[Quelle] Größter Zeitfresser:** Wechsel zwischen Regal/Boxen in der Garage und Etsy-Orders-Seite am Computer.
- **[Quelle] Granularitätsproblem:** Eine Auftragsposition kann selbst aus mehreren Teilen bestehen; „Position gedruckt“ ist kein ausreichend genauer Status.
- **[Quelle] Fehler:** Kleines Teil vergessen; Teil doppelt drucken; kleiner Druckfehler erst spät erkannt.
- **[Quelle] Wartezeit:** Ein fehlendes Teil hält den kompletten Auftrag einen zusätzlichen Tag zurück.
- **[Quelle] Medienbruch:** Etsy digital → Papierausdruck → manuelles Abhaken → physische Box.
- **[Quelle] Kapazitätsproblem:** Unterschiedliche Teile passen in unterschiedliche Zeitfenster; hohe Teile werden nachts, kleine tagsüber produziert.
- **[Analyse] Wirtschaftliche Folgen:** Unproduktive Maschinenbelegung, Materialverbrauch durch Doppel-/Fehldrucke, längere Durchlaufzeit und potenziell verspätete Lieferung.
- **[Unbekannt]** Ausschussquote, Materialkosten, zugesagte Etsy-Bearbeitungszeit und tatsächliche Verspätungen.

## 5. Verwendete Tools

| Tool/Hilfsmittel | Belegt? | Verwendung |
| --- | --- | --- |
| Etsy / Etsy Orders Page | Ja | Quelle der offenen Aufträge und Positionen |
| 3D-/Resindrucker | Ja | Produktion |
| Papierausdrucke | Ja | Auftragsübersicht und Abhaken |
| Regal in der Garage | Ja | Physische Auftragsorganisation |
| Eine Box pro Auftrag | Ja | Sammlung produzierter Teile |
| Spreadsheet | Nur als gewünschte Lösung erwähnt | Soll möglichst mit offenen Etsy-Aufträgen synchronisieren |
| Shop-/Buchhaltungs-/Versandsoftware | Nicht ersichtlich | Nicht ergänzen |

## 6. Vorhandene Lösungen und Workarounds

- **[Quelle]** Jeder Auftrag erhält Ausdruck und passende Box.
- **[Quelle]** Produzierte Teile werden auf dem Papier markiert.
- **[Quelle]** Häufig benötigte Kleinteile werden bei freier Druckkapazität vorproduziert und in einer separaten Box gelagert.
- **[Quelle]** Tag-/Nacht-Trennung erhöht die Maschinenauslastung.
- **[Analyse] Warum es nicht reicht:** Papier bildet keine verschachtelte Stückliste, keinen mehrstufigen Status und keine gemeinsame Nachfrage über mehrere Aufträge ab. Die Vorratsbox hilft nur bei vorhersehbaren Teilen und kann ohne Bestandsbuchung selbst zur Unsicherheit werden.

## 7. Fehlende Informationen vor einer Automation

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

## 8. Drei realistische Automatisierungschancen

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

## 9. Eignung für AI Start Map

### Was ein allgemeiner Fragebogen erfasst

- Online-Shop, wiederkehrende Bestellbearbeitung, Papier/Etsy als Tools, Fehler und den Wunsch nach besserer Übersicht.

### Was er übersieht

- Unterschied zwischen Auftrag, Position, Produkt, Einzelteil und Druckbatch.
- Die vier Fertigungszustände Druck → Reinigung → Trocknung → Prüfung.
- Gemeinsame Teile über mehrere Aufträge, make-to-order vs. Lagerteil und Nachdruckschleifen.
- Dass „Bestellung bis Versand“ hier zunächst ein Produktionssteuerungsproblem ist, kein Versandetikettenproblem.

### Notwendige dynamische KI-Rückfragen

1. „Kann eine verkaufte Position aus mehreren physischen Teilen bestehen?“
2. „Welche Zustände durchläuft jedes Teil, bevor es als fertig gilt?“
3. „Welche Teile kommen in mehreren Aufträgen oder Produkten vor?“
4. „Was löst einen Nachdruck aus und wie wird er heute erkannt?“
5. „Welche Deadline bestimmt die Produktionspriorität?“
6. „Welche Schritte kann Etsy liefern und welche existieren nur in deiner Werkstatt?“

### Wiederverwendbares Playbook

**Order Intake → BOM Explosion → WIP Stage Tracking → QC Gate → Ready-to-Ship**

### n8n-Showcase

**Sehr gut geeignet.** Etsy Open API v3 verwendet API-Key plus OAuth 2.0 für private bzw. schreibende Endpunkte ([offizielle Etsy-Authentifizierung](https://developer.etsy.com/documentation/essentials/authentication)). Die API kann nach dem realen Versand Trackingdaten an einen Beleg anhängen; Etsy weist aber ausdrücklich darauf hin, dass der Kauf von Etsy-Versandlabels nicht per Open API möglich ist ([offizielles Fulfillment-Tutorial](https://developer.etsy.com/documentation/tutorials/fulfillment/).)

```text
Zeitplan-Trigger in n8n
    → Etsy Open API: offene Aufträge abrufen
    → neue/änderte Aufträge erkennen
    → Positionen normalisieren
    → Stückliste aus PostgreSQL laden
    → Teilebedarf und Aufgaben erzeugen
    → Web-Board/Sheet aktualisieren
    → QR-/Status-Webhook verarbeitet Produktionsfortschritt
    → IF: alle Teile QC-passed?
        ├─ Nein → Blocker/Nachdruck melden
        └─ Ja → Betreiber bestätigt „ready to ship“
    → nach realem Versand optional Tracking an Etsy übertragen
```

Für einen ersten Showcase sollten Etsy-Antworten als gespeicherte Test-JSONs simuliert werden. Erst danach echte OAuth-Verbindung. n8n kann Google-Sheets-Zeilen lesen und aktualisieren, falls ein Sheet als sichtbares MVP-Board dient ([offizielle n8n-Sheets-Dokumentation](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.googlesheets/sheet-operations)).

## 10. Strukturierter Testfall

**Testpersona:** „LayerForge Tabletop – Betreiberin Lina“ (anonymisiert/synthetisch)  
**Branche:** Onlinehandel plus 3D-Kleinserienfertigung  
**Unternehmensbeschreibung:** Etsy-Shop für Tabletop-Teile mit auftragsbezogener Resin-Produktion und kleinem Vorrat häufig verkaufter Teile.

| Frage | Testantwort |
| --- | --- |
| Was bietest du an? | 3D-gedruckte Wargaming-Modelle und Fahrzeugteile auf Etsy. |
| Wie sieht dein Alltag aus? | Aufträge prüfen, Drucke planen, drucken, reinigen, trocknen, prüfen und Teile pro Auftrag sammeln. |
| Wie kommen Kunden? | Über Etsy; weitere Kanäle unbekannt. |
| Kundenkommunikation? | Nicht aus der Quelle ersichtlich. |
| Mitarbeiter? | Unbekannt; Beitrag in Ich-Form. |
| Größter Zeitfresser? | Zwischen Etsy am Computer und den Auftragsboxen in der Garage wechseln und den Teilefortschritt abgleichen. |
| Wiederholung? | Jede Position und jedes Einzelteil durch Druck, Reinigung, Trocknung und Prüfung führen. |
| Fehler? | Kleinteile fehlen, Teile werden doppelt gedruckt, kleine Druckfehler führen zu Nachdruck und Verzögerung. |
| Tools? | Etsy Orders, Papierausdrucke, Regal, Boxen, Resin-/3D-Drucker. |
| Wunsch? | Offene Etsy-Positionen synchron sehen und erledigte Teile abhaken können. |

- **Erwartetes Kernproblem:** Fehlende auftragsübergreifende Produktions- und Stücklistensteuerung.
- **Erwartete Top 3:** BOM-Aufgaben aus Etsy; mehrstufiges Teiltracking; priorisierte Druckbatch-Vorschläge.
- **Zu vermeidende Fehlentscheidung:** Als wichtigste Empfehlung Versandlabel oder Social-Media-Automation ausgeben. Der Engpass liegt vor dem Versand in der mehrstufigen Fertigung.

---

# Fall 3: Reinigungsbetrieb mit fünf Auftragnehmern und rund 160 Einsätzen pro Monat

## Quellenbasis

Primärquelle ist der öffentliche Erstbericht: [„Cleaning Company Owners – what’s your process for scheduling jobs?“](https://www.reddit.com/r/sweatystartup/comments/1hbic3f/cleaning_company_owners_whats_your_process_for/). Die Antworten des Accounts im selben Thread werden demselben Fall zugerechnet. Eine ältere, separate Reinigungsfirma beschreibt ergänzend, welche Daten beim Kunden-Onboarding fehlen; sie dient nur als Branchenabgleich: [„Looking for a software solution for our cleaning biz“](https://www.reddit.com/r/smallbusiness/comments/72irfr/looking_for_a_software_solution_for_our_cleaning/).

## 1. Unternehmenskontext

- **[Quelle] Branche/Angebot:** Reinigungsbetrieb mit Vor-Ort-Einsätzen.
- **[Quelle] Größe:** Fünf selbstständige Auftragnehmer/Contractors und rund 160 Jobs pro Monat.
- **[Quelle] Auftragsmix:** 35 % wiederkehrend, 65 % Erst- oder Einmalaufträge.
- **[Quelle] Gebiet:** Radius von 25 Meilen um eine Großstadt. Alle Reinigungskräfte wohnen im Süden; viele neue Kunden kommen aus dem Norden, teilweise etwa eine Stunde Fahrt entfernt.
- **[Quelle] Personal:** Rekrutierung im Norden wurde versucht, bisher ohne Erfolg. Auftragnehmer tragen ihre Kilometerkosten selbst; der Betrieb versucht trotzdem, Fahrtzeiten zu reduzieren.
- **[Quelle] Saison:** Feiertage verschärfen Abwesenheiten und Terminänderungen.
- **[Unbekannt]** Privat-/Gewerbekundenanteil, genaue Leistungspakete, Rechtsform, Umsatz, Schichtmodelle und garantierte Zeitfenster.

## 2. Typischer Arbeitsalltag

- **[Quelle] Wöchentlich:** Der Betreiber verbringt mehrere Stunden damit, ca. 160 monatliche Einsätze auf fünf Auftragnehmer zu verteilen.
- **[Quelle] Wiederkehrende Entscheidungen:** Wiederkehrende vs. einmalige Kunden, individuelle Rhythmen, konkrete Wochentage, Fahrtwege, Wohnorte der Cleaner und Reschedules.
- **[Quelle] Parallel:** Während laufende Aufträge geplant werden, versucht das Unternehmen, im nördlichen Gebiet Personal einzustellen.
- **[Analyse] Tagesgeschäft:** Kurzfristige Ausfälle und Kundenänderungen erzeugen Reparaturplanung; die genaue Kommunikations- und Tagesroutine ist nicht beschrieben.
- **[Unbekannt]** Ob Planung abends stattfindet, wann Kunden bestätigt werden und wie die Contractor-Verfügbarkeit eingeholt wird.

## 3. Drei konkrete problematische Prozesse

### Prozess 1: Neue Kundenanfrage bis planbarer Job-Datensatz

```text
Auslöser: Erst- oder Einmalauftrag / neuer wiederkehrender Kunde
    ↓
Adresse, Leistung, Dauer und gewünschten Rhythmus erfassen
    ↓
Harte und flexible Zeitfenster unterscheiden
    ↓
Zugang, Qualifikation und bevorzugte Reinigungskraft prüfen
    ↓
Entscheidung: Auftrag im Gebiet und mit Zielmarge planbar?
    ├─ nein → Kondition/Termin/Gebiet verhandeln
    └─ ja → planbaren Job in Jobber anlegen
```

Nur Jobber, der Auftragsmix und die Terminrestriktionen sind **[Quelle]**. Intake-Kanal, Felder und Margenprüfung sind **[Analyse]** und zentrale Interviewlücken.

### Prozess 2: Wochenplan erstellen

```text
Auslöser: Neue Woche, neuer Auftrag oder Terminänderung
    ↓
Alle offenen und wiederkehrenden Jobs sammeln
    ↓
Kundenregel prüfen: einmalig / zweiwöchentlich / monatlich / Sonderrhythmus
    ↓
Zulässige Tage und Zeitfenster bestimmen
    ↓
Verfügbare Auftragnehmer prüfen
    ↓
Entfernung und Nachbarschaftsbündelung berücksichtigen
    ↓
Entscheidung: konfliktfreier, praktikabler Slot vorhanden?
    ├─ Nein → Kunde verschieben, Route verschlechtern oder neu verhandeln
    └─ Ja → Auftrag zuweisen
        ↓
Plan in Jobber pflegen
        ↓
Änderung/Ausfall?
    ├─ Ja → betroffene Folgejobs neu planen
    └─ Nein
        ↓
Ergebnis: ausführbarer Wochenplan
```

„Plan in Jobber pflegen“ ist quellenbasiert; die genaue Eingabereihenfolge ist **[Analyse]**.

### Prozess 3: Ausfall oder Kundenänderung bis stabiler Ersatzplan

```text
Auslöser: Feiertag, Abwesenheit, Kundenverschiebung oder Reschedule
    ↓
Betroffenen Auftrag und nachgelagerte Route identifizieren
    ↓
Ersatzkraft, zulässige Tage und räumliche Bündelung prüfen
    ↓
Entscheidung: Änderung ohne Folgekollision möglich?
    ├─ nein → mehrere Jobs neu bewerten und Kundenoptionen erzeugen
    └─ ja → Ersatzzuweisung vorschlagen
        ↓
Betreiber gibt Änderung frei
    ↓
Jobber aktualisieren und Beteiligte bestätigen lassen
```

**[Quelle]** Feiertage, Abwesenheiten, Reschedules und manuelle Umplanung sind belegt. **[Unbekannt]** Kommunikationskanal, Bestätigungslogik und Stornoregeln.

## 4. Probleme und Engpässe

- **[Quelle] Größter Zeitfresser:** Mehrere Stunden pro Woche manuelles „Tetris“.
- **[Quelle] Regelkomplexität:** Kunden wünschen Sonderrhythmen wie alle drei Wochen mittwochs oder jeden dritten Freitag.
- **[Quelle] Routing:** 25-Meilen-Gebiet, Personal im Süden, Nachfrage im Norden, bis zu einer Stunde Fahrt.
- **[Quelle] Kapazität:** Fünf Auftragnehmer für ca. 160 Jobs; fehlendes Personal im Nachfragegebiet.
- **[Quelle] Instabilität:** Feiertage, Urlaub/Abwesenheit und Kundenwünsche verändern den Plan.
- **[Quelle] Einschränkung der Standardlösung:** Jobber ist vorhanden, aber das Problem bleibt.
- **[Analyse] Wirtschaftliche Folgen:** Eigentümerzeit, nicht abrechenbare Fahrtzeit der Auftragnehmer, geringere Attraktivität weit entfernter Jobs, mögliche Ablehnung profitabler Nachfrage und erhöhtes Abwanderungsrisiko bei schlechten Touren.
- **[Unbekannt]** No-show-Rate, Reklamationen, durchschnittliche Fahrzeit, Marge pro Auftrag und Zahl abgelehnter Jobs.

## 5. Verwendete Tools

| Tool/Hilfsmittel | Belegt? | Verwendung |
| --- | --- | --- |
| Jobber | Ja | internes Job-/Planungssystem |
| Manuelle Planung | Ja | Betreiber beschreibt sie als „Tetris“ |
| E-Mail/WhatsApp/Telefon | Nicht ersichtlich | Nicht ergänzen |
| Karten-/Routingsoftware | Nicht ersichtlich | Routing ist Problem, Tool unbekannt |
| Excel/Google Sheets | Nicht ersichtlich | Nur Ideen im Thread, nicht als aktuelles Tool des Betriebs belegt |

## 6. Vorhandene Lösungen und Workarounds

- **[Quelle]** Jobber wird bereits eingesetzt.
- **[Quelle]** Betreiber versucht, Jobs nach Nachbarschaft zu bündeln.
- **[Quelle]** Erwogene Regeln: feste Teams für wiederkehrende Kunden; andere Teams für Erst-/Einmalaufträge; zweiwöchentliche Jobs Montag/Dienstag; monatliche Mittwoch/Donnerstag; Freitag für Reschedules.
- **[Quelle]** Rekrutierung im Norden wurde versucht.
- **[Analyse] Warum es nicht reicht:** Starre Wochentagsregeln kollidieren mit individuellen Kundenrhythmen. Ein vorhandenes Jobmanagementsystem garantiert noch keine Optimierung nach Geografie, Flexibilität und Contractor-Verfügbarkeit.

## 7. Fehlende Informationen vor einer Automation

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

## 8. Drei realistische Automatisierungschancen

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

## 9. Eignung für AI Start Map

### Was ein allgemeiner Fragebogen erfasst

- Fünf Contractors, Planung als Zeitfresser, Jobber, Fehler-/Überlastungsgefühl und Wunsch nach einfacherer Einsatzplanung.

### Was er übersieht

- Anteil wiederkehrender vs. einmaliger Jobs.
- Harte/weiche Constraints, geografische Verteilung und Startorte.
- Jobdauer, Skills, Kunden-Cleaner-Kontinuität und Änderungsrate.
- Ob das Problem Datenerfassung, Optimierung, Veröffentlichung oder Änderungsmanagement ist.
- Dass „bereits Software vorhanden“ nicht bedeutet, dass deren Daten sauber oder Optimierungsmöglichkeiten aktiv sind.

### Notwendige dynamische KI-Rückfragen

1. „Welche Terminregeln sind unverhandelbar und welche nur Wünsche?“
2. „Wie lange dauert ein Job und woher stammt diese Dauer?“
3. „Von wo startet jede Reinigungskraft und wie viel Fahrt ist akzeptabel?“
4. „Welche Kunden müssen bei derselben Reinigungskraft bleiben?“
5. „Wie häufig ändert sich ein bereits veröffentlichter Plan?“
6. „Was kann Jobber in eurem konkreten Tarif importieren/exportieren?“

### Wiederverwendbares Playbook

**Structured Service Intake → Constraint Model → Ranked Schedule → Human Approval → Change Propagation**

### n8n-Showcase

**Gut geeignet als Orchestrierungs-Showcase, nicht als alleiniger Optimierer.** n8n kann Kalenderverfügbarkeit prüfen sowie Events erstellen und aktualisieren ([Google-Calendar-Node](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.googlecalendar), [Availability-Operation](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.googlecalendar/calendar-operations)). Die eigentliche Touren-/Constraint-Optimierung sollte in einem separaten FastAPI-Dienst laufen.

```text
Wöchentlicher Trigger oder „Plan neu berechnen“-Webhook
    → Jobs/Verfügbarkeiten aus validierter Datenquelle laden
    → Adressen normalisieren/geokodieren
    → FastAPI-Planungsservice aufrufen
    → Vorschläge und Konflikte in Review-Ansicht schreiben
    → Betreiber wählt/freigibt
    → Termine im Zielsystem erstellen/aktualisieren
    → Contractor-Bestätigung abwarten
    → erst danach Kundenbestätigung senden
    → Änderungen und nicht bestätigte Einsätze eskalieren
```

Ohne geprüfte Jobber-Schnittstelle sollte der Showcase mit CSV/Testdaten oder eigener Intake-Datenbank laufen. Eine nicht belegte API darf AI Start Map nicht voraussetzen.

## 10. Strukturierter Testfall

**Testpersona:** „KlarRaum Services – Inhaber Jonas“ (anonymisiert/synthetisch)  
**Branche:** Mobiler Reinigungsdienst  
**Unternehmensbeschreibung:** Fünf Contractors, ca. 160 Jobs/Monat, Großstadtradius, gemischte wiederkehrende und einmalige Aufträge.

| Frage | Testantwort |
| --- | --- |
| Was bietest du an? | Vor-Ort-Reinigungsleistungen; genaue Pakete unbekannt. |
| Wie sieht deine Woche aus? | Mehrere Stunden Einsatzplanung, laufende Reschedules und Versuch, Jobs geografisch zu bündeln. |
| Wie kommen Kunden? | Nicht aus der Quelle ersichtlich. |
| Kundenkommunikation? | Nicht aus der Quelle ersichtlich. |
| Mitarbeiter? | Fünf Contractors. |
| Größter Zeitfresser? | Rund 160 Jobs mit individuellen Rhythmen, Verfügbarkeit und Fahrtwegen planen. |
| Wiederholung? | Wiederkehrende Kunden einplanen, Einmaljobs ergänzen, Änderungen reparieren. |
| Fehler/Engpass? | Plan ist schwer stabil zu halten; Nord-Nachfrage passt nicht zum Personalstandort im Süden. |
| Tools? | Jobber plus manuelle Planungsarbeit. |
| Wunsch? | Weniger manuelles Termin-Tetris bei vertretbaren Fahrtzeiten. |

- **Erwartetes Kernproblem:** Mehrkriterielle Einsatzplanung mit unvollständigen/individuellen Constraints.
- **Erwartete Top 3:** strukturierter Constraint-Intake; rangierter Wochenplan; Ausfall-/Änderungsworkflow.
- **Zu vermeidende Fehlentscheidung:** Einfach „Google Calendar automatisieren“ oder autonom den Plan veröffentlichen. Kalender speichert Termine, löst aber nicht die Optimierung und menschlichen Ausnahmen.

---

# Fall 4: Medizinische Solo-Praxis mit offenen Patientenforderungen

## Quellenbasis

Primärquelle ist der öffentliche Erstbericht einer Praxisinhaberin: [„Is it worth the effort?“](https://www.reddit.com/r/smallbusiness/comments/1rf1ng8/is_it_worth_the_effort/). Die Kommentare liefern mögliche Vorgehensweisen, sind aber keine Fakten über den Betrieb. Für den Datenschutzrahmen dient die offizielle [HIPAA Privacy Rule des US-Gesundheitsministeriums](https://www.hhs.gov/hipaa/for-professionals/privacy/index.html): Sie schützt medizinische Akten und andere individuell identifizierbare Gesundheitsinformationen bei erfassten Leistungserbringern.

## 1. Unternehmenskontext

- **[Quelle] Branche/Angebot:** kleine medizinische Praxis; die Inhaberin erwähnt auch einen chirurgischen Fall. Fachgebiet und konkrete Leistungen bleiben unbekannt.
- **[Quelle] Größe:** seit drei Jahren in Betrieb, noch nicht profitabel und nach eigener Aussage „nur ich“; eine Sekretariatskraft kann sie sich derzeit nicht leisten.
- **[Quelle] Arbeitsform:** medizinische Leistung vor Ort; Abrechnung/Kommunikation wahrscheinlich hybrid, Kanäle jedoch nicht genannt.
- **[Quelle] Kundentyp:** Patientinnen und Patienten, teils mit Versicherung und Eigenanteilen.
- **[Unbekannt]** Standort, Zahl der Termine, Versicherermix, Saison, Praxissoftware, externe Abrechnung und Rechtsform.

## 2. Typischer Arbeitsalltag

**[Quelle]** Die Inhaberin behandelt selbst und übernimmt zugleich die kaufmännische Seite. Sie stellt Zuzahlungen häufig erst in Rechnung, nachdem die Person die Praxis verlassen hat, weil ihr das Zahlungsgespräch unangenehm ist. Es bestehen Forderungen von 120 bis 700 US-Dollar und insgesamt mehrere Tausend Dollar Außenstand. Ein Versicherungsfall wurde abgelehnt, weil die Person zuvor wegen desselben Problems zu viele Ärzte aufgesucht habe; die Person verweigert nun die Zahlung.

**[Analyse]** Klinische Arbeit und Revenue-Cycle-Aufgaben konkurrieren unmittelbar um die Zeit derselben Person. Ob Abrechnung abends erfolgt, ist nicht belegt. Der kritische Punkt liegt vor der Mahnung: Finanzverantwortung, Versicherungsstatus und Zahlungsregel werden offenbar nicht zuverlässig vor oder beim Termin abgeschlossen.

## 3. Drei konkrete problematische Prozesse

### Prozess 1: Terminvorbereitung bis bekannter Eigenanteil

```text
Auslöser: Termin ist vereinbart
    ↓
Versicherungs- und Patientendaten prüfen
    ↓
Zuzahlung, Selbstbehalt oder Mitversicherung ermitteln
    ↓
Entscheidung: Betrag ausreichend sicher bekannt?
    ├─ nein → Klärungsaufgabe / transparente Schätzung
    └─ ja → Patient vor dem Termin informieren
        ↓
Menschliche Prüfung besonderer Fälle
    ↓
Ergebnis: dokumentierte finanzielle Erwartung
```

Nur das Vorhandensein von Eigenanteilen und die nachträgliche Berechnung sind **[Quelle]**. Eine vorgelagerte Eligibility-/Estimate-Prüfung ist **[Analyse]** und muss mit Versicherern, Vertrag und Rechtslage validiert werden.

### Prozess 2: Leistung bis Versicherungsentscheidung

```text
Auslöser: Medizinische Leistung wurde erbracht
    ↓
Abrechnungsdaten/Claim einreichen
    ↓
Versicherungsantwort empfangen
    ↓
Entscheidung: bezahlt, Rückfrage oder abgelehnt?
    ├─ bezahlt → Restverantwortung bestimmen
    ├─ Rückfrage → Unterlagen prüfen und fristgerecht antworten
    └─ abgelehnt → Ablehnungsgrund und Einspruchsmöglichkeit prüfen
        ↓
Inhaberin gibt Korrektur/Einspruch oder Patientenzuordnung frei
    ↓
Ergebnis: geklärter Versicherungsanteil
```

Der einzelne Ablehnungsfall ist **[Quelle]**. System, Codes, Fristen und Einspruchsprozess sind **[Unbekannt]**.

### Prozess 3: Offener Patientensaldo bis Zahlung oder begründeter Abschluss

```text
Auslöser: Patientensaldo nach Leistung/Versicherungsabrechnung
    ↓
Rechnung mit Betrag, Grundlage und Zahlungsweg erstellen
    ↓
Fälligkeit überwachen
    ↓
Gestufte, dokumentierte Erinnerung
    ↓
Entscheidung: bezahlt, strittig, Härtefall oder weiter offen?
    ├─ bezahlt → Saldo schließen
    ├─ strittig/Härtefall → persönliche Prüfung und Vereinbarung
    └─ weiter offen → Inkasso-/Abschreibungsentscheidung freigeben
```

## 4. Probleme und Engpässe

- **[Quelle] Zeit-/Verhaltensengpass:** Die Inhaberin vermeidet das Zahlungsgespräch und berechnet Copays erst nach dem Besuch.
- **[Quelle] Liquidität:** mehrere Tausend Dollar offen; Einzelrechnungen zwischen 120 und 700 Dollar; Betrieb noch nicht profitabel.
- **[Quelle] Rollenabhängigkeit:** Behandlung, Abrechnung und Forderungsmanagement hängen an einer Person.
- **[Quelle] Ausnahme:** mindestens ein Versicherungs-Denial erzeugt Streit darüber, wer zahlen muss.
- **[Analyse] Fehlerquellen:** unklare Zuständigkeit, verspätete Nachverfolgung, verpasste Frist, uneinheitliche Kommunikation und fehlende Begründungsakte.
- **[Analyse] Wirtschaftliche Folge:** erbrachte Leistung wird nicht oder spät zu Cash; zugleich kann unpassendes Mahnen die Patientenbeziehung schädigen.
- **[Unbekannt]** Altersstruktur der Forderungen, Erfolgsquote, Claim-Durchlaufzeiten, tatsächliche Fristen und Anteil fehlerhafter Claims.

## 5. Verwendete Tools

| Tool/Hilfsmittel | Belegt? | Verwendung |
| --- | --- | --- |
| Praxis-/EHR-/Billing-System | Nicht aus der Quelle ersichtlich | Nicht ergänzen |
| Telefon, E-Mail, Brief, Zahlungsportal | Nicht ersichtlich | Kanäle der Rechnungen/Mahnungen unbekannt |
| Versicherungssystem/Portal | Nicht ersichtlich | Claim-Verarbeitung unbekannt |
| CPA | Ja | Sie/er kennt die Höhe der Außenstände und ist darüber erstaunt |
| Sekretariat/Billing-Service | Nein | Inhaberin hat aktuell keine bezahlbare Sekretariatskraft; externe Abrechnung unbekannt |

## 6. Vorhandene Lösungen und Workarounds

- **[Quelle]** Copays werden nachträglich berechnet statt beim Besuch erhoben.
- **[Quelle]** Die Inhaberin erwägt Inkasso und möchte Unterstützung für die Verwaltungsaufgabe.
- **[Quelle]** Der CPA sieht die offenen Beträge, löst den Prozess aber nicht.
- **[Analyse] Warum es nicht reicht:** Eine spätere Rechnung behandelt das Symptom. Ohne klare Vorabinformation, Claim-Status und Ausnahmeregeln lässt sich nicht bestimmen, wann welcher Betrag legitim und kommunizierbar ist.

## 7. Fehlende Informationen vor einer Automation

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

## 8. Drei realistische Automatisierungschancen

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

## 9. Eignung für AI Start Map

- **Erfasst ein Standardfragebogen:** Solo-Größe, Abrechnung als Zeitfresser, offene Rechnungen, Wunsch nach Erinnerung.
- **Übersieht wahrscheinlich:** Claim vor Patientensaldo, Denial-Fristen, Unterschied Schätzung/finaler Betrag, Datenschutzvertrag, Härtefall und Inkassoentscheidung.
- **Dynamische Rückfragen:** „Ist der Saldo final oder hängt er von einer Versicherungsantwort ab?“, „Welche Fälle dürfen nie automatisch erinnert werden?“, „Welche Daten verlassen die Praxissoftware?“
- **Playbook:** `Service delivered → payer adjudication → approved balance → staged collection with exception gates`.
- **n8n:** Nur als kontrollierter Showcase mit synthetischen Daten geeignet: Terminliste → Prüfstatus → freigegebener Saldo → Erinnerung → Zahlungswebhook → Stop/Eskalation. Für echte Gesundheitsdaten braucht es vorab Architektur-, Vertrags- und Sicherheitsprüfung; ein generisches Cloud-Blueprint ist unzureichend.

## 10. Strukturierter Testfall

- **Persona:** „Dr. M., medizinische Solo-Praxis“
- **Beschreibung:** Drei Jahre am Markt, keine Assistenz, mehrere Tausend Dollar offene Eigenanteile.
- **Mögliche Interviewantworten:** „Ich behandle allein“; „Copays stelle ich oft erst später in Rechnung“; „einige Salden hängen an Versicherungsentscheidungen“; „meine Systeme und Fristen muss ich noch nennen“.
- **Kernproblem:** fehlende Trennung zwischen Versicherungs-, Patientensaldo- und Inkassoprozess.
- **Top 3:** Vor-Termin-Worklist; Denial-Queue; freigegebene Mahnkaskade.
- **Fehlentscheidung:** Das System darf nicht ungeprüft alle offenen Beträge automatisch mahnen oder Patientendaten an ein beliebiges KI-Modell senden.

---

# Fall 5: Solo-Betrieb für maßgefertigte Möbel und Metallarbeiten

## Quellenbasis

Primärquelle ist der ausführliche Erstbericht [„I make furniture for a living. But I’m thinking of throwing in the towel“](https://www.reddit.com/r/smallbusiness/comments/aqfkc1/i_make_furniture_for_a_living_but_im_thinking_of/). Kommentare werden nur dann als Betriebsfakt verwendet, wenn der ursprüngliche Autor selbst antwortet; fremde Strategievorschläge sind keine Quelle für seinen Ist-Prozess.

## 1. Unternehmenskontext

- **[Quelle] Angebot:** Entwurf und Bau kundenspezifischer Möbel, vor allem Metallarbeit/Schweißen, ergänzt um Holz, Fasern und Kunststoffe.
- **[Quelle] Größe/Ort:** Inhaber arbeitet aus der Garage; rund 30.000 US-Dollar stecken in Maschinen und Werkzeugen. Mitarbeiter werden nicht genannt, daher Solo nur als vorsichtige Arbeitshypothese.
- **[Quelle] Kunden:** Unternehmen/professionelle Auftraggeber und private Käufer.
- **[Quelle] Reife:** drittes Jahr in Vollzeit; vorher zwei Jahre parallel zu einer anderen Arbeit. Erstes Jahr okay, zweites stark, drittes „crippling“.
- **[Quelle] Vertrieb:** Magazinberichte, kostenintensive Messestände, Designausstellungen und professionelle Stammkunden.
- **[Unbekannt]** Region, Website-/Shop-System, Saison, Zahl paralleler Projekte, Lieferprozess und Mitarbeiter.

## 2. Typischer Arbeitsalltag

**[Quelle]** Der Unternehmer entwirft und fertigt, schreibt frühere Großkunden per E-Mail an, lädt zu Mittagessen ein und versucht neue Marktwege. Frühere Projekte lagen bei 30.000–50.000 Dollar. Gleichzeitig ist das Kleinproduktgeschäft wirtschaftlich eng: Eine 300-Dollar-Couchtisch-Referenz enthält 120 Dollar Material und einen ganzen Arbeitstag. Der Betreiber berichtet außerdem von Konsignation über zeitweise sechs Läden; Stücke können Monate bis zu einem Jahr liegen und beschädigt zurückkommen. Typische genannte Verkaufspreise waren etwa 300 Dollar für einen Tisch und 450 Dollar für einen Stuhl.

**[Analyse]** Akquise, Design, Beschaffung, Fertigung und Bestandsrisiko laufen parallel. Der eigentliche Diagnosebedarf ist nicht „Büroarbeit automatisieren“, sondern pro Kanal und Projekt zu erkennen, ob Nachfrage, Preis und Kapazität zusammenpassen.

## 3. Drei konkrete problematische Prozesse

### Prozess 1: Früherer Kontakt bis qualifizierte Projektchance

```text
Auslöser: Pipeline für größere Aufträge wird dünn
    ↓
Frühere professionelle Kunden identifizieren
    ↓
E-Mail oder Einladung zum Austausch senden
    ↓
Reaktion und Bedarf dokumentieren
    ↓
Entscheidung: konkrete Chance, späterer Bedarf oder verloren?
    ├─ Chance → Projektbrief anlegen
    ├─ später → zulässiges Follow-up terminieren
    └─ verloren → Grund erfassen
```

Kontaktversuche und ehemalige Großkunden sind **[Quelle]**; Pipeline-Status und Verlustgründe sind **[Analyse]**.

### Prozess 2: Kundenidee bis Bau- und Preisentscheidung

```text
Auslöser: Anfrage für ein individuelles Möbelstück
    ↓
Anforderung, Maße, Material, Nutzung und Zieltermin klären
    ↓
Entwurf und Fertigungsweg bestimmen
    ↓
Material, Maschinenzeit, Arbeitszeit und Risiko kalkulieren
    ↓
Entscheidung: Preis deckt Kosten und Zielmarge?
    ├─ nein → Umfang/Material/Preis neu verhandeln oder ablehnen
    └─ ja → Angebot freigeben und nach Annahme fertigen
        ↓
Ergebnis: lieferbares Unikat mit dokumentierter Nachkalkulation
```

Entwurf/Bau und Kostenbeispiel sind **[Quelle]**; Angebots-, Freigabe- und Abnahmefolge ist **[Analyse]**.

### Prozess 3: Konsignationsstück bis Verkauf oder Rücknahme

```text
Auslöser: Stück wird einem Retail-Partner übergeben
    ↓
Stück, Preis, Laden und Übergabezustand dokumentieren
    ↓
Monatlichen Status/Verkauf abgleichen
    ↓
Entscheidung: verkauft, weiter ausgestellt oder Rückgabe?
    ├─ verkauft → Abrechnung prüfen
    ├─ weiter → Liegedauer und Opportunitätskosten bewerten
    └─ Rückgabe → Zustand mit Übergabe vergleichen
        ↓
Ergebnis: Erlös oder verfügbarer/beschädigter Bestand
```

Sechs Läden, lange Liegedauer und beschädigte Rückgaben sind **[Quelle]**. Vertrags- und Abrechnungsdetails sind unbekannt.

## 4. Probleme und Engpässe

- **[Quelle] Nachfrage:** frühere 30–50-Tsd.-Dollar-Projekte brechen weg.
- **[Quelle] Preis/Kosten:** ein ganzer Arbeitstag plus 120 Dollar Material trifft auf geringe Zahlungsbereitschaft bei 300 Dollar Verkaufspreis.
- **[Quelle] Kanalrisiko:** Konsignationsware bindet Bestand monatelang bis zu einem Jahr und kann beschädigt zurückkommen.
- **[Quelle] Akquisekosten:** Messestände waren teuer; die wirksame Attribution fehlt.
- **[Analyse] Informationslücke:** keine sichtbare Verbindung zwischen Leadquelle, Angebot, tatsächlicher Arbeitszeit, Material, Verkauf und Folgeauftrag.
- **[Analyse] Wirtschaftliche Folge:** Auslastung mit margenschwachen Stücken kann die knappe Zeit stärker schädigen als Leerlauf.
- **[Unbekannt]** Angebotsquote, Stundensatz, Fixkosten, Lieferkosten, Zahlungskonditionen und reale Deckungsbeiträge.

## 5. Verwendete Tools

| Tool/Hilfsmittel | Belegt? | Verwendung |
| --- | --- | --- |
| E-Mail | Ja | Reaktivierung früherer Kunden |
| Persönliche Mittagessen/Meetings | Ja | Beziehungsaktivierung |
| Magazine, Trade Shows, Designausstellungen | Ja | Reichweite und Leadgewinnung |
| Garage, Maschinen, Schweiß-/Metallwerkzeuge | Ja | Fertigung |
| Retail-Stores/Konsignation | Ja | Verkaufskanal |
| Website, CRM, Kalkulation, Buchhaltung | Nicht aus der Quelle ersichtlich | Nicht ergänzen |

## 6. Vorhandene Lösungen und Workarounds

- **[Quelle]** Direkte Reaktivierung per E-Mail und Einladung zum Lunch.
- **[Quelle]** Hohe Investition in Messen, Magazinpräsenz und verschiedene Retail-Partner.
- **[Quelle]** Versuch, vom kreativen Großprojektgeschäft in andere Produkt-/Vertriebspfade zu pivotieren.
- **[Analyse] Warum es nicht reicht:** Mehr Aktivität ohne Kanal- und Projektökonomie kann Verluste skalieren. Der Betrieb braucht zuerst Messbarkeit und Entscheidungsregeln.

## 7. Fehlende Informationen vor einer Automation

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

## 8. Drei realistische Automatisierungschancen

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

## 9. Eignung für AI Start Map

- **Erfasst:** Branche, Solo-/Kleinbetrieb, Akquiseproblem, Fertigung, Vertriebskanäle.
- **Übersieht:** Unterschied zwischen Nachfrageproblem und Prozessproblem, Deckungsbeitrag pro Kanal, Konsignationsalter, Kapazitätswert der Inhaberzeit.
- **Dynamische Rückfragen:** „Welche Aufträge waren tatsächlich profitabel?“, „Was ist nach der letzten Übergabe im Store passiert?“, „Welche Entscheidung soll automatisiert werden – erinnern, kalkulieren oder annehmen?“
- **Playbook:** `Lead attribution → structured scope → cost floor → human go/no-go → actual-vs-plan review` plus `consignment custody ledger`.
- **n8n:** Gute Demo für Intake → Kalkulationsblatt → Angebotsentwurf → Freigabe → Follow-up; die kreative Konstruktion bleibt ein individueller Blueprint. Eine Automation kann fehlende Marktnachfrage nicht reparieren.

## 10. Strukturierter Testfall

- **Persona:** „Alex M., Maßmöbel- und Metallbauer“
- **Beschreibung:** Garage, hohe Werkzeuginvestition, frühere B2B-Großaufträge, aktuell schwache Pipeline und riskante Konsignation.
- **Interviewantworten:** „Ich entwerfe und baue selbst“; „frühere Kunden reagieren kaum“; „ein 300-Dollar-Stück kann einen ganzen Tag plus 120 Dollar Material kosten“; „Ware liegt bis zu einem Jahr im Laden“.
- **Kernproblem:** unklare Kanal- und Projektökonomie, nicht bloß zu wenig Marketingautomation.
- **Top 3:** Pipeline/Attribution; kalkulatorischer Go/No-go; Konsignationsregister.
- **Fehlentscheidung:** Das System darf nicht mehr Leads oder Social Posts priorisieren, bevor Preisuntergrenze, Kapazität und profitable Kundensegmente geklärt sind.

---

# Fall 6: Tattoo-Artist mit periodisch geöffneten Büchern

## Quellenbasis

Primärfall ist der detaillierte Workflow eines praktizierenden Artists im Thread [„Best booking method?“](https://www.reddit.com/r/TattooArtists/comments/15pcaw6/best_booking_method_looking_to_get_more/). Ein separater Thread [über Tattoo-Assistenz](https://www.reddit.com/r/TattooArtists/comments/1elkjbw/artists_that_have_assistants_to_help_with/) dient nur als Branchenabgleich: Dort reduziert strukturierter Intake plus Assistenz den wöchentlichen Angebotscheck einer Künstlerin von einem ganzen Tag auf 15–20 Minuten. Square dokumentiert offiziell, dass seine [Bookings API Termine erstellen, lesen, ändern und stornieren kann](https://developer.squareup.com/docs/bookings-api/what-it-is); konkrete Berechtigungen/Tarife müssen geprüft werden.

## 1. Unternehmenskontext

- **[Quelle] Angebot:** individuelle Tattoo-Projekte; Auswahl nach Idee, Platzierung, Größe, Stil, Budget und künstlerischem Interesse.
- **[Quelle] Größe:** der beschriebene Workflow ist personenzentriert; Team-/Studioform unbekannt.
- **[Quelle] Arbeitsform:** vor Ort tätowieren, online über Website, Mailingliste und Instagram akquirieren/kommunizieren.
- **[Quelle] Kapazität:** Bücher öffnen alle drei bis vier Monate und werden für ungefähr denselben Zeitraum gefüllt.
- **[Quelle] Nachfrage:** Formular ist 24 Stunden offen; danach Auswahl und Terminierung in wenigen stressigen Tagen.
- **[Unbekannt]** Standort, Preise, durchschnittliche Anfragen, No-shows, Saison, Datenschutz-/Einwilligungsprozess und weitere Mitarbeitende.

## 2. Typischer Arbeitsalltag

**[Quelle]** Vor einer Öffnung kündigt der Artist Datum/Uhrzeit über Mailingliste und Instagram an. Zur Öffnung wird 24 Stunden lang ein Websiteformular publiziert. Danach werden Einreichungen geprüft, besonders große/spannende Projekte zuerst ausgewählt und kleinere Lücken gefüllt. Ausgewählte Personen erhalten einen Kalenderlink, wählen Zeit und zahlen über Square eine Anzahlung. Ist der Zeitraum voll, informiert der Artist die Mailingliste. E-Mails und DMs während geschlossener Bücher werden ignoriert; Hinweise stehen in Instagram-Highlights und auf der Website.

**[Analyse]** Tattooausführung und Zeichnung laufen nach der Buchung parallel zum nächsten Kommunikationszyklus, sind aber im Primärworkflow nicht detailliert beschrieben. Die Quelle belegt einen ausgeprägten Last-Peak statt gleichmäßiger Administration.

## 3. Drei konkrete problematische Prozesse

### Prozess 1: Bücheröffnung bis vollständige Einreichung

```text
Auslöser: neuer Buchungszeitraum steht an
    ↓
Öffnung an Mailingliste und Instagram ankündigen
    ↓
Websiteformular 24 Stunden aktivieren
    ↓
Idee, Platzierung, Größe, Stil und Budget erfassen
    ↓
Entscheidung: Pflichtinformationen vollständig?
    ├─ nein → gezielte Rückfrage / nicht reviewfähig markieren
    └─ ja → Review-Board
```

### Prozess 2: Einreichung bis kreative Auswahl

```text
Auslöser: Formular schließt
    ↓
Einreichungen nach Machbarkeit und persönlicher Passung prüfen
    ↓
Große/spannende Projekte priorisieren
    ↓
Kleinere Projekte auf Kalenderlücken abstimmen
    ↓
Entscheidung durch Artist: auswählen, Rückfrage oder nicht in dieser Runde
    ↓
Ergebnis: begründbare Shortlist; keine automatische kreative Ablehnung
```

### Prozess 3: Auswahl bis bestätigter Termin/Abschluss der Runde

```text
Auslöser: Projekt ausgewählt
    ↓
Kalenderlink senden
    ↓
Kunde wählt Termin und zahlt Anzahlung in Square
    ↓
Entscheidung: Deposit fristgerecht eingegangen?
    ├─ nein → Erinnerung / Slot zurückgeben
    └─ ja → Termin bestätigt
        ↓
Kapazität voll → Mailingliste informieren; übrige Anfragen schließen
```

Deposit-Frist und Slot-Rückgabe sind **[Analyse]**; die Quelle nennt Terminwahl und Anzahlung, aber keine Fristregel.

## 4. Probleme und Engpässe

- **[Quelle] Lastspitze:** Buchung erledigt sich in wenigen stressigen Tagen.
- **[Quelle] Selektionsarbeit:** kreative Passung, Projektgröße und Kalenderlücken müssen gemeinsam bewertet werden.
- **[Quelle] Kanalbruch:** Mailingliste/Instagram → Websiteformular → manuelle Auswahl → Square.
- **[Quelle] Kommunikation:** nicht ausgewählte Personen hören gegebenenfalls nichts und sollen es später erneut versuchen; DMs/E-Mails bei geschlossenen Büchern werden ignoriert.
- **[Analyse] Fehlerquellen:** unvollständige Angaben, Doppelkontakt, verlorene Auswahlentscheidung, Termin ohne Deposit oder unbeantwortete Ausnahme.
- **[Analyse] Wirtschaftliche Folge:** Admin-Peak verdrängt Zeichnen/Tätowieren; schlecht gefüllte Lücken reduzieren Auslastung.
- **[Unbekannt]** reale Anzahl Anfragen, Antwortzeit, Konversionsquote und Deposit-Ausfälle.

## 5. Verwendete Tools

| Tool/Hilfsmittel | Belegt? | Verwendung |
| --- | --- | --- |
| Mailingliste | Ja | Ankündigung und Vollmeldung |
| Instagram/IG Highlights und DMs | Ja | Ankündigung, Regeln; DMs nicht als Buchungskanal |
| Websiteformular | Ja | 24-Stunden-Intake; konkreter Builder unbekannt |
| Google Forms | Nur als mögliche Alternative genannt | Nicht als Ist-Tool behaupten |
| Square | Ja | Terminwahl und Anzahlung |
| E-Mail | Ja | Anfragen bzw. Kontakt mit ausgewählten Kunden |
| CRM/Spreadsheet | Nicht im Primärfall ersichtlich | Nur im separaten Branchenabgleich |

## 6. Vorhandene Lösungen und Workarounds

- **[Quelle]** Zeitlich begrenztes Formular bündelt Nachfrage.
- **[Quelle]** Klare Hinweise in Website und Instagram schützen geschlossene Bücher.
- **[Quelle]** Square verbindet Selbstterminierung und Anzahlung.
- **[Quelle]** Große Projekte werden zuerst, kleine als Lückenfüller bearbeitet.
- **[Analyse] Warum es nicht reicht:** Intake ist strukturiert, aber Review, Entscheidungskommunikation und Übergabe an Square bleiben ein manueller Peak. Eine Standard-Priorisierung kann die künstlerische Entscheidung nicht ersetzen.

## 7. Fehlende Informationen vor einer Automation

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

## 8. Drei realistische Automatisierungschancen

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

## 9. Eignung für AI Start Map

- **Erfasst:** Terminbetrieb, Onlineanfragen, saisonale/periodische Peaks, Deposits.
- **Übersieht:** Bücher-offen-Zustandsmaschine, kreative Selektion, Kalenderlücken, Nicht-Antwort-Policy und Unterschied zwischen objektiver Machbarkeit und Geschmack.
- **Dynamische Rückfragen:** „Wer darf Projekte ablehnen?“, „Welche Information fehlt am häufigsten?“, „Was passiert mit vollständigen, aber nicht ausgewählten Anfragen?“
- **Playbook:** `Campaign window → validated intake → human curation → booking/deposit → capacity closure`.
- **n8n:** Sehr geeignet: Cron öffnet/schließt Form; Webhook validiert; Board; Artist setzt `selected`; Square-Link; Booking-/Payment-Event; Statusmail. Visuelle/kreative Auswahl bleibt außerhalb automatischer Entscheidung.

## 10. Strukturierter Testfall

- **Persona:** „Sam K., Tattoo-Artist“
- **Beschreibung:** Bücher alle drei bis vier Monate; 24 Stunden Intake; persönliche Projektauswahl; Square für Termin und Anzahlung.
- **Interviewantworten:** „Ich will große, passende Projekte zuerst“; „kleine füllen Lücken“; „bei geschlossenen Büchern ignoriere ich DMs“; „ich entscheide selbst“.
- **Kernproblem:** konzentrierter Review- und Übergabe-Peak.
- **Top 3:** validierter Intake; Review-Board; Square-/Deposit-Orchestrierung.
- **Fehlentscheidung:** Das System darf nicht anhand eines KI-Scores autonom Tattoos annehmen/ablehnen oder einen generischen Chatbot als Hauptlösung empfehlen.

---

# Fall 7: Solo-Verwaltung von 47 Wohneinheiten

## Quellenbasis

Primärquelle ist der öffentliche, inzwischen unter gelöschtem Nutzernamen stehende Erstbericht [„Managing 47 units solo and these are the systems that keep me from drowning“](https://www.reddit.com/r/PropertyManagement/comments/1rz0zjx/managing_47_units_solo_and_these_are_the_systems/). Der Inhalt ist weiterhin öffentlich, aber nicht unabhängig verifiziert. Kommentare anderer Verwalter werden nur als Branchenabgleich, nicht als Fakten über diesen Bestand behandelt.

## 1. Unternehmenskontext

- **[Quelle] Angebot/Bestand:** selbstverwaltetes Wohnportfolio mit 47 Einheiten in sechs Immobilien.
- **[Quelle] Größe:** keine Mitarbeiter; Inhaber plus einige verlässliche Auftragnehmer.
- **[Quelle] Arbeitsform:** hybrid – Mieterportal und Buchhaltung digital, Inspektionen und Wohnungswechsel vor Ort.
- **[Quelle] Kundentyp:** Wohnungsmieter; ob für Dritte oder nur eigener Bestand verwaltet wird, ist nicht eindeutig.
- **[Quelle] Wirtschaftlicher Rahmen:** externe Verwaltung würde nach Aussage des Autors 8–10 % der Bruttomiete kosten; deshalb baut er eigene Systeme.
- **[Unbekannt]** Region, Belegung, Mietpreis, Saison, Frequenz von Turns/Inspektionen und Zahl der Handwerkerfälle.

## 2. Typischer Arbeitsalltag

**[Quelle]** AppFolio dient für Mieterkommunikation, Mieteinzug, Wartungsanfragen und Buchhaltung. Mieter reichen Reparaturmeldungen mit Fotos im Portal ein; der Inhaber weist einen passenden Auftragnehmer zu, die Kommunikation bleibt dokumentiert. Investitionsgüter wie Dach, HVAC und Warmwasserbereiter werden in Google Sheets mit Einbau- und erwartetem Austauschzeitpunkt verfolgt. Bei Inspektionen und Wohnungswechseln diktiert der Inhaber Beobachtungen in Willow Voice; das Transkript wird Inspektionsbericht und Arbeitsauftrag. Für Mietrechtsfragen nutzt er Perplexity als Ausgangspunkt und prüft Hochrisikofragen mit einem Anwalt.

**[Analyse]** Ereignisse treten unplanbar neben Buchhaltung, Inspektionen und Kapitalplanung auf. Die vom Autor formulierte Betriebsregel lautet sinngemäß: Wenn ein Prozess vom Erinnern abhängt, bricht er bei wachsendem Bestand.

## 3. Drei konkrete problematische Prozesse

### Prozess 1: Mieter-Reparaturmeldung bis Abschluss

```text
Auslöser: Mieter reicht Portal-Anfrage mit Fotos ein
    ↓
Problem, Einheit und Dringlichkeit prüfen
    ↓
Entscheidung: Notfall, regulär oder Rückfrage?
    ├─ Notfall → sofortige menschliche Eskalation
    ├─ Rückfrage → fehlende Informationen anfordern
    └─ regulär → passenden Auftragnehmer auswählen
        ↓
Auftrag zuweisen und Kommunikation dokumentieren
    ↓
Erledigungsnachweis prüfen
    ↓
Ergebnis: geschlossener Fall mit Audit-Trail
```

Portal, Fotos, Zuweisung und dokumentierte Kommunikation sind **[Quelle]**. Notfallkriterien und Erledigungsnachweis sind **[Analyse]** und müssen konkretisiert werden.

### Prozess 2: Inspektion/Turnover bis Bericht und Work Order

```text
Auslöser: Inspektion oder Wohnungswechsel vor Ort
    ↓
Befunde raumweise diktieren
    ↓
Willow Voice transkribiert
    ↓
Befunde nach Einheit/Bauteil/Verantwortung strukturieren
    ↓
Entscheidung: Wartung, normale Abnutzung oder möglicher Mieterschaden?
    ↓
Inhaber prüft Bericht und Aufträge
    ↓
Ergebnis: Inspektionsakte plus freigegebene Arbeitsaufträge
```

Die Quelle nennt ausdrücklich ein Diktat mit Scharnier, Dichtung, Fuge und Teppichfleck sowie die Doppelnutzung als Bericht/Work Order. Die rechtliche/finanzielle Zuordnung erfordert menschliche Prüfung.

### Prozess 3: Anlagegut bis Reserve- und Austauschplanung

```text
Auslöser: Einbau, Inspektion oder periodische Planungsrunde
    ↓
Bauteil, Immobilie, Einbaudatum und erwartete Lebensdauer erfassen
    ↓
Erwartetes Austauschjahr und Kostenschätzung aktualisieren
    ↓
Kapitalbedarf je Zeitraum/Immobilie aggregieren
    ↓
Entscheidung: beobachten, inspizieren oder Budget reservieren?
    ↓
Ergebnis: aktualisierte Reserveplanung
```

Asset-Daten und Nutzung für Reserveberechnung sind **[Quelle]**; Kosten-/Entscheidungsstufen sind **[Analyse]**.

## 4. Probleme und Engpässe

- **[Quelle] Schlüsselperson:** 47 Einheiten, keine Mitarbeiter.
- **[Quelle] Gedächtnisrisiko:** Prozesse müssen ohne persönliche Erinnerung funktionieren.
- **[Quelle] Systemgrenzen:** AppFolio, Sheets, Voice-App und Rechtsrecherche sind getrennte Arbeitsräume.
- **[Analyse] Wartungsrisiko:** falsche Dringlichkeit, unvollständige Fotos, unklarer Zugang, Auftrag ohne Nachweis oder zu früh geschlossener Vorgang.
- **[Analyse] Inspektionsrisiko:** Diktatfehler oder unzulässige automatische Schuld-/Kautionszuordnung.
- **[Analyse] Wirtschaftliche Folge:** verzögerte Reparaturen, Doppelkoordination, Compliance-/Haftungsrisiko und unzureichende Reserven.
- **[Unbekannt]** tatsächliche Stunden, Ticketvolumen, Fristen, Bußgelder, Contractor-SLAs und API-Zugang.

## 5. Verwendete Tools

| Tool/Hilfsmittel | Belegt? | Verwendung |
| --- | --- | --- |
| AppFolio | Ja | Mieterkommunikation, Mieteinzug, Wartung, Buchhaltung |
| Buildium | Ja, früher getestet | Autor bevorzugte AppFolio-Wartungsworkflow |
| Google Sheets | Ja | Capex-/Lebenszyklusplanung |
| Willow Voice | Ja | Diktat bei Inspektion/Turnover |
| Perplexity | Ja | erste, quellenorientierte Mietrechtsrecherche |
| Anwalt | Ja | Prüfung hochriskanter Rechtsfragen |
| SMS/WhatsApp/E-Mail außerhalb AppFolio | Nicht aus Primärquelle ersichtlich | Nicht ergänzen |

## 6. Vorhandene Lösungen und Workarounds

- **[Quelle]** Mieterportal erzwingt Foto-/Ticketdokumentation.
- **[Quelle]** Diktat verhindert nachträgliches Rekonstruieren von Feldnotizen.
- **[Quelle]** Google Sheets schafft eine separate Langfristperspektive für Anlagen.
- **[Quelle]** KI-Recherche wird nicht als Rechtsfreigabe behandelt; Hochrisiko wird anwaltlich geprüft.
- **[Analyse] Grenze:** gute Einzellösungen ergeben noch kein End-to-End-Monitoring. Vor allem Übergaben und Ausnahmen müssen zuverlässig werden.

## 7. Fehlende Informationen vor einer Automation

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

## 8. Drei realistische Automatisierungschancen

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

## 9. Eignung für AI Start Map

- **Erfasst:** Solo, viele Objekte, Wartung, Portal, wiederkehrende Inspektionen.
- **Übersieht:** Notfallmatrix, Zugangs-/Datenschutzregeln, Abschlussnachweis, Kautionsentscheidung, Capex-Verknüpfung.
- **Dynamische Rückfragen:** „Was darf niemals bis morgen warten?“, „Wann ist ein Ticket wirklich erledigt?“, „Welche Entscheidung braucht Anwalt oder Eigentümer?“
- **Playbook:** `Event intake → severity gate → accountable assignment → evidence → verified closure` und `field observation → reviewed report → task/asset update`.
- **n8n:** Sehr guter Showcase mit synthetischen Tickets: AppFolio-Webhook/Export → Pflichtfeldprüfung → regelbasierte Kategorie → Freigabe → Contractor-Brief → Reminder → Foto-/Rechnungsnachweis → Abschluss. Bei fehlender AppFolio-Schnittstelle ist ein individueller Import-/RPA-Blueprint nötig.

## 10. Strukturierter Testfall

- **Persona:** „Robin L., Solo-Objektverwalter“
- **Beschreibung:** 47 Einheiten/6 Objekte, keine Angestellten, einige Handwerker, AppFolio plus Sheets plus Sprach-App.
- **Interviewantworten:** „Mieter senden Portal-Tickets mit Fotos“; „ich weise Handwerker zu“; „Inspektionen diktiere ich“; „nichts darf von meinem Gedächtnis abhängen“.
- **Kernproblem:** verlässliche Ereignis-, Ausnahme- und Abschlusssteuerung.
- **Top 3:** Wartungstriage; Diktatbericht; Capex-Frühwarnung.
- **Fehlentscheidung:** Das System darf keinen vermeintlich harmlosen Notfall automatisch zurückstellen oder Mieterschäden/Kautionsabzüge aus einem Transkript entscheiden.

---

# Fall 8: Ein-Personen-Kanzlei mit hohem Telefonaufwand

## Quellenbasis

Primärquelle ist die konkrete Wortmeldung eines Kanzleiinhabers im Thread [„Virtual Receptionists?“](https://www.reddit.com/r/smallbusiness/comments/103frfv/virtual_receptionists/). Sie ist kürzer als die anderen Quellen, benennt aber drei präzise Arbeitsziele. Für den Risikorahmen dient die [ABA Model Rule 1.6](https://www.americanbar.org/groups/professional_responsibility/publications/model_rules_of_professional_conduct/rule_1_6_confidentiality_of_information/), nach der Rechtsanwälte angemessene Anstrengungen gegen unbefugte Offenlegung oder Zugriff auf Mandatsinformationen unternehmen müssen. Lokale Berufsregeln sind **unbekannt** und gehen vor.

## 1. Unternehmenskontext

- **[Quelle] Angebot/Größe:** Single-member law firm, also Ein-Personen-Kanzlei.
- **[Quelle] Kundentyp:** potenzielle Mandanten sowie bestehende Mandanten, die nach dem Stand ihrer „claims“ fragen; Rechtsgebiet nicht eindeutig.
- **[Quelle] Arbeitsform:** Telefon als Eingang; gewünschtes Ziel sind Intake-Formulare, E-Mail und Terminierung.
- **[Quelle] Problem:** viel Zeitverlust am Telefon; Schriftform wird für Nachverfolgung bevorzugt.
- **[Unbekannt]** Land/Bundesstaat, Fallzahlen, Saison, Kanzleisoftware, Mitarbeiter, Gebührenmodell und rechtliche Fristen.

## 2. Typischer Arbeitsalltag

**[Quelle]** Potenzielle Mandanten sollen durch ein Intake-Formular geführt und anschließend zu einem Beratungsgespräch terminiert werden. Bestandsmandanten rufen für Claim-Updates an; gewünscht ist, dass der Inhalt als E-Mail diktiert und an den Anwalt zur Bearbeitung übergeben wird. Telefonate verbrauchen viel Zeit, während der Anwalt E-Mails/Formulare für Tracking bevorzugt.

**[Analyse]** Anrufe unterbrechen juristische Facharbeit. Die Quelle belegt nicht, ob nach Feierabend nachgearbeitet wird, doch die Warteschlange wird heute offenbar nicht als strukturierter Datensatz erzeugt.

## 3. Drei konkrete problematische Prozesse

### Prozess 1: Erstkontakt bis reviewfähiger Intake

```text
Auslöser: potenzieller Mandant ruft an
    ↓
Identität, Gegenparteien, Angelegenheit und Fristen erfassen
    ↓
Entscheidung: sofortiger Notfall/Fristsache?
    ├─ ja → Anwalt alarmieren
    └─ nein → Intake vervollständigen
        ↓
Konfliktprüfung durch zugelassenen Prozess
    ↓
Ergebnis: prüfen, ablehnen oder Consult anbieten
```

Das Ziel „durch Intake führen“ ist **[Quelle]**; Konflikt-/Fristgate ist zwingende **[Analyse]**, deren konkrete Regeln lokal erhoben werden müssen.

### Prozess 2: Freigegebener Interessent bis Beratungstermin

```text
Auslöser: Anwalt gibt Consult frei
    ↓
Geeignete Terminarten und Verfügbarkeit anbieten
    ↓
Interessent wählt Slot und erhält Hinweise/Unterlagenliste
    ↓
Bestätigung und Erinnerung
    ↓
Ergebnis: vorbereiteter Beratungstermin
```

Terminierung nach Intake ist **[Quelle]**; Kalender, Zahlung und Erinnerungsregeln sind unbekannt.

### Prozess 3: Mandantenanruf zum Status bis geprüfte Antwort

```text
Auslöser: bestehender Mandant ruft wegen Claim-Status an
    ↓
Identität/Berechtigung verifizieren
    ↓
Anliegen und gewünschte Rückmeldung strukturiert aufnehmen
    ↓
E-Mail-/Aufgabenentwurf an Anwalt erzeugen
    ↓
Anwalt prüft Akte und formuliert/freigibt Antwort
    ↓
Ergebnis: dokumentierte Statuskommunikation
```

## 4. Probleme und Engpässe

- **[Quelle] Zeitfresser:** viel Telefonzeit.
- **[Quelle] Medienproblem:** mündliche Informationen sind schlechter nachzuverfolgen als gewünschte Formulare/E-Mails.
- **[Quelle] Personenabhängigkeit:** alle fachlichen Entscheidungen hängen am Einzelanwalt.
- **[Analyse] Risiken:** Interessenkonflikt vor vertraulichem Detail, verpasste Frist, falsche Identität, unautorisierte Statusauskunft, versprochene Mandatsannahme.
- **[Analyse] Wirtschaftliche Folge:** Unterbrechungen reduzieren abrechenbare/fachliche Zeit; schlechte Erreichbarkeit kann geeignete Mandate verlieren.
- **[Unbekannt]** verpasste Calls, Konversionsrate, durchschnittliche Dauer, Fehler-/Beschwerdequote.

## 5. Verwendete Tools

| Tool/Hilfsmittel | Belegt? | Verwendung |
| --- | --- | --- |
| Telefon | Ja | Erstkontakte und Statusanfragen |
| E-Mail | Ja, als Zielkanal | Tracking und Übergabe an den Anwalt |
| Intake-Formular | Als gewünschte Lösung | noch nicht als Ist-System belegt |
| Terminbuchung/Kalender | Gewünscht, konkretes Tool unbekannt | Consult Scheduling |
| Kanzleisoftware/DMS/CRM | Nicht aus der Quelle ersichtlich | Nicht ergänzen |
| Virtuelle Rezeption | Gesucht, nicht als bestehend belegt | keine Ist-Lösung behaupten |

## 6. Vorhandene Lösungen und Workarounds

- **[Quelle]** Der Anwalt nimmt Telefonate selbst entgegen bzw. trägt deren Zeitlast.
- **[Quelle]** Er formuliert bereits ein gewünschtes Receptionsmodell: Intake, Consult, diktierte Status-E-Mail.
- **[Analyse] Warum Standard-Rezeption nicht automatisch reicht:** Eine Person kann Anrufe annehmen, aber ohne Konflikt-, Identitäts-, Frist- und Berechtigungsregeln weiterhin riskante oder unvollständige Vorgänge erzeugen.

## 7. Fehlende Informationen vor einer Automation

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

## 8. Drei realistische Automatisierungschancen

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

## 9. Eignung für AI Start Map

- **Erfasst:** Solo-Dienstleister, Telefonlast, Intake, Termine, Statuskommunikation.
- **Übersieht:** Konfliktprüfung vor Details, Fristnotfall, Mandatsannahme-Sprache, Identitätsprüfung und anwaltliche Vertraulichkeit.
- **Dynamische Rückfragen:** „Welche Information darf die Rezeption geben?“, „Was muss sofort zum Anwalt?“, „Wann gilt ein Interessent als Mandant?“
- **Playbook:** `Untrusted inquiry → minimal intake → risk/conflict gate → professional approval → scheduling` und `verified status request → draft → professional release`.
- **n8n:** Mit synthetischen Daten gut: Voice/Form-Webhook → minimale Felder → Fristkeyword-Alarm → Konfliktprüf-Aufgabe → Anwaltstatus → Kalenderlink. Für reale Mandatsdaten individueller, sicherheitsgeprüfter Blueprint; kein autonomer Rechts-Chatbot.

## 10. Strukturierter Testfall

- **Persona:** „Pat R., Einzelanwalt“
- **Beschreibung:** Einzelkanzlei, viele Telefonunterbrechungen durch Interessenten und Claim-Statusfragen.
- **Interviewantworten:** „Ich will Formulare/E-Mail für Tracking“; „nach Intake soll ein Consult gebucht werden“; „Statusantworten will ich als Entwurf sehen“; „meine Kanzleisoftware ist noch unbekannt“.
- **Kernproblem:** sichere Intake-/Kommunikationsübergaben, nicht bloß Erreichbarkeit.
- **Top 3:** Minimal-Intake mit Gates; Consult-Orchestrierung; geprüfter Statusentwurf.
- **Fehlentscheidung:** Das System darf keine Rechtsberatung, Mandatsannahme oder Fallstatusantwort autonom ausgeben.

---

# Fall 9: Unabhängige Kfz-Werkstatt mit sechs Mechanikern

## Quellenbasis

Primärquelle ist der Erstbericht [„What shop software are you guys using?“](https://www.reddit.com/r/mechanics/comments/1mcnemb/what_shop_software_are_you_guys_using/): unabhängige Werkstatt, 28 Jahre am Standort, sechs Mechaniker und elf Hebebühnen/Arbeitsplätze. Ein separater Werkstattbericht [„Automotive Shop Management Software“](https://www.reddit.com/r/mechanics/comments/1eyyhye/automotive_shop_management_software/) liefert die detaillierte Medienbruchstrecke RepairLink → Mitchell → AllData/ProDemand. Dieser zweite Bericht ist **kein Fakt über dieselbe Werkstatt**, sondern Prozessabgleich für ein wiederkehrendes Branchenproblem.

## 1. Unternehmenskontext

- **[Quelle] Branche:** unabhängige Kfz-Reparaturwerkstatt.
- **[Quelle] Größe:** sechs Mechaniker, elf Bays, seit 28 Jahren am selben Standort.
- **[Quelle] Arbeitsform:** Reparatur vor Ort; Software für Verwaltung und Mechaniker-Arbeitsblätter.
- **[Quelle] Systemwechsel:** von veraltetem Autos2000 zu Mitchell1; ProDemand war bereits abonniert.
- **[Quelle] Problem:** Mitchell1 gilt als zu kompliziert; zu viel Dateneingabe für ein Mechaniker-Worksheet.
- **[Unbekannt]** Eigentümer-/Serviceberaterzahl, Kundenmix, Termin-/Saisonspitzen, Teilelager, Durchsatz und Abrechnung.

## 2. Typischer Arbeitsalltag

**[Quelle]** In der Primärwerkstatt müssen Auftragsdaten so erfasst werden, dass Mechaniker Arbeitsblätter erhalten; die Mannschaft ist nach eigener Aussage zu beschäftigt für umfangreiche Pflichtfelder. Im Vergleichsbetrieb werden Teile in RepairLink gefunden, manuell in Mitchell-Angebote übertragen, Arbeitszeiten aus AllData oder ProDemand gesucht und erneut manuell eingegeben. Drei Programme laufen parallel, um Estimate oder Invoice zu erzeugen. CCC One wird als positives Vergleichsmuster genannt: VIN eingeben, Teile-/Arbeitskatalog zuordnen, Positionen auswählen, Sonderfälle ergänzen.

**Analyse:** Fahrzeugannahme, Diagnose, Angebot/Freigabe, Reparatur und Rechnung sind miteinander gekoppelt. Schnelligkeit allein darf nicht zur falschen Teile- oder Arbeitszeitübernahme führen.

## 3. Drei konkrete problematische Prozesse

### Prozess 1: Kunden-/Fahrzeugannahme bis Mechaniker-Worksheet

```text
Auslöser: Fahrzeug kommt mit Beanstandung
    ↓
Kunde, Fahrzeug/VIN, Kilometerstand und Symptom erfassen
    ↓
Auftrag und Priorität anlegen
    ↓
Pflichtinformationen auf Vollständigkeit prüfen
    ↓
Mechaniker/Bay zuweisen
    ↓
Ergebnis: verständliches Arbeitsblatt
```

Worksheet und Werkstattgröße sind **[Quelle]**; konkrete Intake-Felder/Zuweisung sind **[Analyse]**.

### Prozess 2: Diagnose bis Kostenvoranschlag

```text
Auslöser: benötigte Reparatur ist diagnostiziert
    ↓
VIN/Fahrzeugkonfiguration bestätigen
    ↓
Passende Teile im Katalog suchen
    ↓
Arbeitszeit aus verlässlicher Quelle bestimmen
    ↓
Teile, Menge, Aufschlag und Labor in Estimate übertragen
    ↓
Sonderfälle wie festgerostete Hardware ergänzen
    ↓
Serviceberater prüft Passung, Preis und Umfang
    ↓
Ergebnis: freigabefähiger Kostenvoranschlag
```

Diese Strecke ist im Vergleichsbetrieb konkret belegt; für die Primärwerkstatt ist nur Mitchell1/ProDemand plus zu viel Eingabe belegt.

### Prozess 3: Kundenfreigabe bis Reparatur und Rechnung

```text
Auslöser: Kostenvoranschlag wird genehmigt
    ↓
Teile bestellen/reservieren und Auftrag freigeben
    ↓
Mechaniker führt Arbeit aus und dokumentiert Abweichungen
    ↓
Entscheidung: Zusatzarbeit nötig?
    ├─ ja → neuen Estimate/Freigabeprozess auslösen
    └─ nein → Abschlussprüfung
        ↓
Ist-Teile und Ist-Zeit in Rechnung übernehmen
    ↓
Ergebnis: repariertes Fahrzeug und nachvollziehbare Rechnung
```

Estimate/Invoice sind quellenbelegt; Bestellung, Freigabe- und QC-Regeln sind unbekannt.

## 4. Probleme und Engpässe

- **[Quelle] Zeitfresser:** umfangreiche Eingabe, obwohl Werkstatt ausgelastet ist.
- **[Quelle] Medienbruch (Vergleichsbetrieb):** Teile, Arbeitszeiten und Estimate in drei Programmen.
- **[Quelle] doppelte Eingabe:** Teile und Labor werden manuell in Mitchell übertragen.
- **[Quelle] Usability:** ein vorhandenes umfassendes System kann zu kompliziert für den tatsächlichen Shopfloor sein.
- **[Analyse] Fehlerquellen:** falsche VIN-Variante, Teilenummer, Menge, Laborzeit, Aufschlag oder nicht übernommene Zusatzarbeit.
- **[Analyse] wirtschaftliche Folge:** längere Angebotszeit, wartende Fahrzeuge/Bays, Unterberechnung und Mechaniker ohne klare Aufgabe.
- **[Unbekannt]** tatsächliche Minuten pro Estimate, Fehlerquote, Teilemarge, Comebacks und API-Lizenzen.

## 5. Verwendete Tools

| Tool/Hilfsmittel | Primärfall | Vergleichsbetrieb |
| --- | --- | --- |
| Autos2000 | früheres System | nicht genannt |
| Mitchell1 | aktuelles System | Mitchell Shop Manager |
| ProDemand | bereits abonniert | Arbeitszeitquelle |
| RepairLink | nicht belegt | Teilesuche |
| AllData | nicht belegt | Arbeitszeitquelle |
| CCC One | nicht belegt | positives früheres Vergleichssystem |
| Papier | nicht aus Primärquelle ersichtlich | nicht ergänzen |

## 6. Vorhandene Lösungen und Workarounds

- **[Quelle]** Primärbetrieb migrierte vom veralteten Autos2000 zu Mitchell1, weil ProDemand ohnehin bezahlt wurde.
- **[Quelle]** Vergleichsbetrieb arbeitet mit drei gleichzeitig geöffneten Programmen und manueller Übertragung.
- **[Analyse] Warum es nicht reicht:** Funktionsumfang ohne einfache Rollenoberfläche erhöht Eingabelast. Ein Systemwechsel ohne Daten-/Lizenzprüfung kann das Problem nur verschieben.

## 7. Fehlende Informationen vor einer Automation

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

## 8. Drei realistische Automatisierungschancen

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

## 9. Eignung für AI Start Map

- **Erfasst:** Werkstatt, sechs Mechaniker, vorhandene Software, doppelte Eingabe, Estimate/Invoice.
- **Übersieht:** Datenlizenzen, VIN-Variante, Rollenoberfläche, Kundenfreigabe, Bay-/Teileverfügbarkeit und Soll-Ist-Abgleich.
- **Dynamische Rückfragen:** „Welche Zeile wird wo zuerst erzeugt?“, „Welche Quelle ist für Labor verbindlich?“, „Was darf ein Mechaniker ändern?“
- **Playbook:** `Asset/VIN intake → licensed catalog enrichment → human estimate approval → exception authorization → actual-to-invoice reconciliation`.
- **n8n:** Als Showcase nur mit Mock-Katalog: VIN-Webhook → Decoder → Teile-/Laborvorschlag → Freigabe → PDF/Shop-Import. Wegen Lizenz- und proprietärer Systemgrenzen ist für einen echten Betrieb wahrscheinlich ein individueller Blueprint sinnvoller.

## 10. Strukturierter Testfall

- **Persona:** „Chris W., unabhängige Werkstatt“
- **Beschreibung:** 28 Jahre am Standort, sechs Mechaniker, elf Bays, Mitchell1/ProDemand, Eingabe zu komplex.
- **Interviewantworten:** „Wir brauchen schnell ein Worksheet“; „Teile und Labor dürfen nicht falsch sein“; „unsere Schnittstellen/Lizenzen sind noch zu klären“.
- **Kernproblem:** sichere Reduktion von Mehrfacheingabe zwischen Fahrzeug-, Katalog- und Auftragsdaten.
- **Top 3:** Quick-Intake; VIN-/Katalogentwurf; Zusatzarbeits-/Rechnungsabgleich.
- **Fehlentscheidung:** Das System darf keine frei erfundenen Arbeitszeiten/Teilenummern erzeugen oder einen kompletten Softwarewechsel empfehlen, ohne Rollen, Datenrechte und reale Eingabewege zu prüfen.

---

# Fall 10: Teppichreinigungsfabrik mit Abholservice

## Quellenbasis

Primärquelle ist der Erstbericht [„Software for carpet cleaning factory. Ideas?“](https://www.reddit.com/r/smallbusiness/comments/1cj8xi0/software_for_carpet_cleaning_factory_ideas/). Der Eigentümer beschreibt Annahme/Abholung, Kundennummer, Auftragsdaten, aktuelle Tabellen und die Sorge, dass Mitarbeitende Aufträge löschen oder verändern könnten. Vorschläge anderer Nutzer (Barcode, ClickUp, Housecall Pro, Google Forms) werden als Optionen, nicht als vorhandene Systeme behandelt.

## 1. Unternehmenskontext

- **[Quelle] Angebot:** Teppiche werden in einer Fabrik gereinigt.
- **[Quelle] Kanäle:** Kunden bringen Teppiche oder der Betrieb holt sie mit einem Bus ab.
- **[Quelle] Team:** Es gibt „workers“/Mitarbeitende; Anzahl und Rollen unbekannt.
- **[Quelle] Arbeitsform:** vor Ort in der Fabrik plus mobiler Abhol-/Rückgabedienst.
- **[Quelle] Auftragsdaten:** Kunden-ID, Anzahl Teppiche, Abholadresse, Fertigdatum und Gesamtpreis.
- **[Unbekannt]** Region, Saison, Kundentyp, Durchsatz, Reinigungsstufen, Lieferroute, Zahlung und Reklamationen.

## 2. Typischer Arbeitsalltag

**[Quelle]** Teppiche kommen per Selbstanlieferung oder Bus in die Fabrik. Bei Abholung soll eine Kunden-ID vergeben und zusammen mit Zahl der Teppiche, Adresse, Fertigtermin und Gesamtpreis erfasst werden. Aktuell arbeitet der Betrieb mit Tabellen. Der Inhaber möchte Bearbeitungs-/Löschrechte einschränken, ausdrücklich um Diebstahl durch Mitarbeiter zu verhindern. Housecall Pro wäre nach seiner Aussage interessant, ist aber in seiner Region nicht verfügbar.

**[Analyse]** Mehrere physische Objekte eines Auftrags bewegen sich durch Annahme, Reinigung, Lager und Rückgabe. Eine Auftragszeile „3 Teppiche“ reicht nicht, wenn einzelne Teppiche getrennt oder fehlerhaft verarbeitet werden. Die internen Reinigungsstufen sind jedoch nicht belegt.

## 3. Drei konkrete problematische Prozesse

### Prozess 1: Abholauftrag/Selbstanlieferung bis eindeutige Annahme

```text
Auslöser: Kunde bringt Teppiche oder Bus holt sie ab
    ↓
Kunde/Adresse und Auftrags-ID erfassen
    ↓
Jeden Teppich zählen, beschreiben und eindeutig markieren
    ↓
Fertigtermin und Gesamtpreis dokumentieren
    ↓
Kunde bestätigt Anzahl/Zustand/Übergabe
    ↓
Ergebnis: nachweisbarer Auftrag mit Objektliste
```

Kunden-ID, Anzahl, Adresse, Datum, Preis und zwei Eingangskanäle sind **[Quelle]**. Einzel-ID, Zustand und Bestätigung sind notwendige **[Analyse]**.

### Prozess 2: Angenommener Teppich bis fertig/gelagert

```text
Auslöser: markierter Teppich trifft in Fabrik ein
    ↓
Eingang scannen/buchen
    ↓
Reinigungsstufen durchlaufen
    ↓
Qualität und Beschädigung prüfen
    ↓
Entscheidung: Nacharbeit nötig?
    ├─ ja → Status Nacharbeit; Fertigtermin neu bewerten
    └─ nein → fertig und Lagerplatz zuordnen
        ↓
Ergebnis: rückgabefähiger Teppich mit Statushistorie
```

**[Unbekannt]** Die tatsächlichen Reinigungsstufen, Qualitätskriterien und Lagerstruktur. Die Kette ist ein Diagnosemodell, das im Interview ersetzt/präzisiert werden muss.

### Prozess 3: Fertigmeldung bis vollständige Rückgabe

```text
Auslöser: Auftrag soll abgeholt oder ausgeliefert werden
    ↓
Soll-Anzahl und IDs des Auftrags laden
    ↓
Jeden ausgehenden Teppich scannen
    ↓
Entscheidung: Soll = Ist und Preis/Zahlungsstatus geklärt?
    ├─ nein → Übergabe sperren und Differenz klären
    └─ ja → Übergabe/Busroute freigeben
        ↓
Kunde bestätigt Empfang
    ↓
Ergebnis: vollständig geschlossener Auftrag
```

Der in den Kommentaren vorgeschlagene Grundsatz „wenn drei hineingingen, müssen drei hinaus“ ist kein Ist-Fakt, passt aber direkt zum belegten Mengenproblem.

## 4. Probleme und Engpässe

- **[Quelle] Datenintegrität:** Tabellen werden bereits genutzt; Inhaber möchte Löschung/Änderung durch Mitarbeitende beschränken.
- **[Quelle] Verlust-/Diebstahlrisiko:** ausdrücklich als Sorge genannt.
- **[Quelle] Objektzuordnung:** mehrere Teppiche pro Kunde/Auftrag.
- **[Quelle] Verfügbarkeitsgrenze:** gewünschte Standardsoftware ist in der Region nicht verfügbar.
- **[Analyse] Medien-/Prozessbruch:** physisches Objekt bewegt sich, während Status nur in editierbarer Zeile lebt.
- **[Analyse] Fehlerquellen:** falscher Kunde, fehlender Teppich, falsche Anzahl, verlorener Lagerort, veralteter Fertigtermin, unberechtigte Änderung.
- **[Analyse] wirtschaftliche Folge:** Ersatz/Erstattung, Reklamation, Suchzeit, Umsatzverlust und Vertrauensschaden.
- **[Unbekannt]** tatsächliche Verlustquote, Zahl der Nutzer, Offline-/Netzabdeckung, Zahlungsdifferenzen und Durchlaufzeit.

## 5. Verwendete Tools

| Tool/Hilfsmittel | Belegt? | Verwendung |
| --- | --- | --- |
| Spreadsheet/Tabellen | Ja | aktuelles Auftrags-/Datensystem |
| Bus | Ja | Abholung/Transport |
| Kundennummer | Als gewünschte/benötigte Logik | Zuordnung bei Pickup |
| Housecall Pro | geprüft, aber regional nicht verfügbar | keine Ist-Nutzung |
| Barcode/Scanner | nur Community-Vorschlag | nicht als vorhanden behaupten |
| ClickUp/Google Forms | nur Community-Vorschlag | nicht als vorhanden behaupten |
| Rechnung/Kasse/Buchhaltung | Nicht aus Quelle ersichtlich | Nicht ergänzen |

## 6. Vorhandene Lösungen und Workarounds

- **[Quelle]** Tabellen bilden den aktuellen Datenbestand ab.
- **[Quelle]** Die gewünschte Datensammlung umfasst ID, Menge, Adresse, Termin und Preis.
- **[Quelle]** Der Inhaber sucht Rechtebeschränkung; eine vorgeschlagene Tabellenlösung wäre ein geschütztes Sheet mit nur einer editierenden Person und Leserechten für andere.
- **[Analyse] Warum es nicht reicht:** ein zentraler Editor kann Diebstahl erschweren, wird aber Bottleneck und Single Point of Failure. Tabellen liefern ohne unveränderliches Ereignisprotokoll keine belastbare Chain of Custody.

## 7. Fehlende Informationen vor einer Automation

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

## 8. Drei realistische Automatisierungschancen

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

## 9. Eignung für AI Start Map

- **Erfasst:** produkt-/objektbasierter Betrieb, Mitarbeiter, Tabelle, Abholung, Termin/Preis.
- **Übersieht:** Objekt- statt Auftragsgranularität, Rechte/Audit, Offlinefähigkeit, Chain of Custody, Soll-Ist-Gate.
- **Dynamische Rückfragen:** „Was kann verloren gehen – Auftrag oder einzelner Teppich?“, „Wer darf löschen?“, „An welchem physischen Übergabepunkt entsteht der Nachweis?“
- **Playbook:** `Physical custody intake → unique ID → stage events → exception/rework → count-controlled release`.
- **n8n:** Guter Showcase: mobiles Intake → ID/QR erzeugen → Status-Scan-Webhooks → Reminder bei überfälligem Status → Ausgangs-Soll-Ist → Manifest/Kundenbestätigung. Für echtes Offline-Scanning und manipulationssichere Rollen ist neben n8n eine kleine Fachanwendung/Datenbank nötig.

## 10. Strukturierter Testfall

- **Persona:** „Nuri A., Teppichreinigungsbetrieb“
- **Beschreibung:** Fabrik, mehrere Mitarbeitende, Selbstanlieferung und Busabholung, aktuelle Tabellen.
- **Interviewantworten:** „Wir erfassen Kunde, Anzahl, Adresse, Fertigdatum und Preis“; „Mitarbeitende sollen Aufträge nicht löschen können“; „Standardsoftware ist in meiner Region nicht verfügbar“.
- **Kernproblem:** physische Chain of Custody und Datenintegrität.
- **Top 3:** Objekt-ID/Übergabebeleg; rollenbasiertes Audit-Log; Soll-Ist-Ausgangskontrolle.
- **Fehlentscheidung:** Das System darf nicht nur eine schönere Tabelle oder einen Chatbot empfehlen; es muss einzelne Teppiche, Berechtigungen und physische Scans modellieren.

---

# Gemeinsame Auswertung für AI Start Map

## 1. Fragen, die immer gestellt werden müssen

1. **Prozessanker:** Welcher konkrete Prozess soll untersucht werden – mit Start- und Endereignis?
2. **Volumen:** Wie oft läuft er pro Tag/Woche/Monat und wie stark schwankt das Volumen?
3. **Schritte:** Was geschieht tatsächlich in Reihenfolge, einschließlich Nacharbeit und Ausnahmen?
4. **Rollen:** Wer führt aus, entscheidet, prüft, genehmigt und wird informiert?
5. **Inputs/Outputs:** Welche Informationen/Dokumente kommen hinein; welches Ergebnis muss herauskommen?
6. **System of Record:** Wo liegt heute die verlässlichste Version jedes Datums bzw. Dokuments?
7. **Medienbrüche:** Was wird kopiert, neu getippt, fotografiert, exportiert oder per Nachricht weitergegeben?
8. **Regeln vs. Einzelfall:** Welche Entscheidungen folgen festen Regeln, welche benötigen Erfahrung?
9. **Ausnahmen:** Was geht am häufigsten schief und wie wird der Fall dann repariert?
10. **Zeit und Folgen:** Bearbeitungszeit, Wartezeit, Fehlerrate und wirtschaftliche Wirkung.
11. **Technische Zugänglichkeit:** API, Export, Webhook, E-Mail, Datei oder nur manuelle Oberfläche?
12. **Freigabe:** Was darf niemals ohne menschliche Prüfung gesendet, gebucht oder geändert werden?
13. **Datenschutz/Sicherheit:** Personen-, Adress-, Zahlungs-, Gesundheits-, Zugangs- oder Sicherheitsdaten?
14. **Physisches Geschäftsobjekt:** Geht es um Auftrag, Termin, Person, Fahrzeug, Teil, Teppich, Akte oder Forderung – und braucht jedes Objekt eine eigene ID?
15. **Datenherkunft und Beweis:** Welche Quelle ist verbindlich; welcher Nachweis schließt den Vorgang?
16. **Erfolgskriterium:** Woran ist nach vier Wochen messbar, dass die Automation hilft?

## 2. Fragen, die nur dynamisch gestellt werden sollten

| Erkannter Kontext | Dynamische Vertiefung |
| --- | --- |
| Außendienst/Handwerk | Geräte, Offline-Bedarf, Fotos/Skizzen, Material, Vor-Ort-Pflichtfelder, technische Freigabe, Versionen |
| Produkt/Fertigung | SKU/Variante, Stückliste, Chargen, Teilstatus, Maschinenkapazität, Ausschuss, QC, Deadline |
| Termine/Personal | harte/weiche Zeitfenster, Dauer, Skills, Startort, Fahrtzeit, Kontinuität, Ausfälle, Fairness |
| Mehrere Kommunikationskanäle | Eingangskanal, Zusammenführung, Identität/Dubletten, Antwort-SLA, Opt-in |
| Vorhandene Software | konkret genutzte Funktionen, Tarif, Datenqualität, API/Export, Eigentümer der Daten |
| KI-Extraktion vorgesehen | Quellformat, Konfidenz, Pflichtfelder, Korrekturschritt, erlaubte/unerlaubte Ableitungen |
| Gesundheit/Zahlung | Versicherungsentscheidung vor Patientensaldo, Schutzdaten, Härtefall, Fristen, zugelassene Dienstleister |
| Recht/Kanzlei | Konfliktcheck, Identität, Fristen, Mandatsannahme, zulässige Statusauskunft, Vertraulichkeit |
| Kreative Auswahl | objektive Machbarkeit vs. persönliche Präferenz, Erklärbarkeit, Rechte an Bildern, kein Auto-Reject |
| Physische Fremdobjekte | Einzel-ID, Zustand, Chain of Custody, Rollenrechte, Scanpunkte, Soll-Ist-Übergabe |
| Reparatur/Wartung | Asset-/VIN-Identität, Dringlichkeit, Teile/Laborquelle, Zusatzfreigabe, Abschlussnachweis |
| Pipeline/Projektgeschäft | Leadquelle, Verlustgrund, Preisuntergrenze, Kapazität, Nachkalkulation, Kanalprofitabilität |

Die Diagnose sollte nicht alle Fragen als starre Liste zeigen. Sie sollte nach „mehrteilige Produkte“ sofort in Stückliste und Prozessstufen verzweigen; nach „fünf mobile Mitarbeiter“ in Verfügbarkeit, Route und Zuweisungsregeln; nach „Patientenrechnung“ zuerst fragen, ob der Saldo final ist; und nach „Mandantenanruf“ Identitäts-, Konflikt- und Vertraulichkeitsregeln klären.

## 3. Wiederkehrende Playbook-Muster

1. **Unstrukturierter Eingang → strukturierter Fall/Job:** Informationen werden einmal erfasst, validiert und mit stabiler ID versehen.
2. **Viele Artefakte → eine Prozessakte:** Dateien bleiben möglich, werden aber einem Auftrag, Status und einer Version zugeordnet.
3. **Komplexes Objekt → Teilaufgaben:** Auftrag wird in Positionen, Teile oder Arbeitsschritte zerlegt.
4. **Vorschlag → menschliches Gate:** System entwirft Angebot, Batch oder Plan; Fachperson veröffentlicht.
5. **Statusänderung → Folgeaktionen:** Fortschritt, Ausnahme oder Absage aktualisiert abhängige Aufgaben und Benachrichtigungen.
6. **Standardpfad plus Ausnahme-Queue:** Automatisiert wird der häufige, regelklare Teil; unvollständige oder riskante Fälle landen sichtbar bei Menschen.
7. **Physisches Objekt → digitale Chain of Custody:** ID, Übergabe, Statusereignis, Abweichung und Abschlussnachweis.
8. **Schätzung/Entwurf → belegte Quelle:** Preise, Arbeitszeiten, Rechts-/Versicherungsstatus oder Dringlichkeit dürfen nicht aus freier KI-Erzeugung stammen.
9. **Planwert → Ist-Rückkopplung:** Angebot, Zeit, Material, Reparatur oder Capex wird nach Ausführung mit dem tatsächlichen Ergebnis abgeglichen.
10. **Kapazitätsfenster → kontrollierte Nachfrage:** Bücheröffnung, Terminangebot oder Gebietszusage wird an reale Kapazität gebunden.

## 4. Die ersten fünf Playbooks

### Priorität 1: Structured Intake to Job Record

Breitester Nutzen in allen zehn Fällen. Schema, stabile Objekt-/Job-ID, Pflichtfeldprüfung, Anhänge, Datenquelle, Konfidenz, Einwilligung und Korrektur. Varianten: Field Intake, Legal Minimal Intake, Booking Window, Physical Custody Intake.

### Priorität 2: Human-approved Document/Quote Draft

Aus strukturierten, belegten Daten einen Angebots-, Bericht-, Status- oder Nachrichtentwurf erzeugen. Preis, technische Aussage, medizinischer Saldo, juristische Antwort und kreative Auswahl bleiben hinter einem rollenspezifischen Gate.

### Priorität 3: Order-to-Production / BOM and Stage Tracking

Für Produkt- und Objektbetriebe: Auftrag → Position/Einzelobjekt → Prozessstufe → Nacharbeit → QC/Soll-Ist → nachgewiesene Übergabe. Gilt für 3D-Druck, Teppiche, Reparaturen und Teile von Handwerksaufträgen.

### Priorität 4: Constraint-based Scheduling and Rescheduling

Für mobile Services und kapazitätsgebundene Kreativ-/Beratungsbetriebe: harte/weiche Regeln, Dauer, Skills, Geografie, Deposit, Kontinuität, Vorschläge, Freigabe und Auswirkungsanalyse bei Änderungen.

### Priorität 5: Exception, Reminder and Escalation

Fehlende Information, Denial, Frist, Notfall, Nachdruck, Zusatzarbeit, unbestätigter Termin, Bestandsdifferenz oder gefährdete Deadline sichtbar machen. Dieses Playbook benötigt Stop-Bedingung, Owner, SLA, Eskalationsgrund und Abschlussbeleg.

## 5. Beste n8n-Showcases

| Rang | Fall | Eignung | Begründung |
| --- | --- | --- | --- |
| 1 | Etsy-3D-Druck | Sehr hoch | Klarer Event-Input, verschachtelte Stückliste, sichtbarer Statusfluss und QC-Gate; mit Testdaten sehr anschaulich |
| 2 | Teppichreinigungsfabrik | Sehr hoch | ID, Scan-Events, Rollen, Ausnahme und Soll-Ist-Ausgang ergeben einen verständlichen End-to-End-Flow; Fach-App bleibt nötig |
| 3 | Tattoo-Booking | Hoch | Zeitfenster, Form-Webhook, Human Selection, Square-Übergabe und Deposit-Event zeigen Orchestrierung ohne Auto-Entscheidung |
| 4 | Reinigungsplanung | Hoch | Starker Vorher/Nachher-Effekt; n8n orchestriert Intake, Optimierungsservice, Freigabe und Benachrichtigung |
| 5 | Objektwartung | Hoch | Ticket, Triage, Contractor, Reminder und Abschlussnachweis; Notfall-Gate demonstriert verantwortliche Automation |
| 6 | Elektroservice | Mittel bis hoch | Stark nach Einführung eines einheitlichen mobilen Intake; reine Synchronisation der Alt-Apps wäre fragil |
| 7 | Maßmöbel | Mittel | Pipeline/Angebot gut, aber Nachfrage- und Kreativproblem wird nicht durch n8n gelöst |
| 8 | Kfz-Werkstatt | Mittel | Attraktiver Flow, jedoch proprietäre Kataloge und Lizenzrechte begrenzen einen realen Plug-and-play-Demoaufbau |
| 9 | Kanzlei | Nur kontrolliert | Gute Gate-Demo mit synthetischen Daten; reale Mandatsdaten benötigen individuellen Sicherheits- und Berufsrechtsrahmen |
| 10 | Medizinische Praxis | Nur kontrolliert | Revenue-Cycle-Logik wertvoll, echte Gesundheitsdaten und Versicherungsregeln erfordern einen spezialisierten Blueprint |

## 6. Notwendige Negativ- und Guardrail-Tests

1. **Symptom statt Engpass:** Bei 3D-Druck darf das System nicht Versand/Social Media priorisieren, wenn fehlende Teile die Durchlaufzeit bestimmen.
2. **Tool-Bias:** Bei vorhandenen Tools darf es nicht reflexhaft „neues CRM“ empfehlen, ohne aktuelle Nutzung und fehlende Funktion zu prüfen.
3. **API-Halluzination:** Keine Integration als machbar darstellen, bevor konkrete Schnittstelle, Tarif und Berechtigung verifiziert sind.
4. **Unzulässige Autonomie:** Angebot, technischer Plan, Qualitätsfreigabe oder Kunden-Umbuchung niemals ohne definiertes Human Gate.
5. **Falsche Prozessebene:** „Auftrag abhaken“ ist unzureichend, wenn Positionen aus mehreren Teilen und Stufen bestehen.
6. **Geografie ignoriert:** Ein Terminplan ist falsch, wenn er nur Kalenderfreiheit und nicht Fahrt, Startort und Jobdauer berücksichtigt.
7. **Unbekanntes erfinden:** Fehlende Mitarbeiterzahl, Kommunikationskanäle oder Software müssen Rückfragen auslösen, nicht Annahmen.
8. **Ausnahmeblindheit:** Der Happy Path allein reicht nicht; Nachdruck, Absage, fehlende Pflichtdaten und neue Variante benötigen eigene Testpfade.
9. **Schlechte Priorisierung:** Empfehlung muss nach Zeit-/Fehlerwirkung, Machbarkeit, Risiko und Datenreife rangieren – nicht nach „höchstem KI-Anteil“.
10. **Overengineering:** Bei geringem Volumen muss ein einfaches Formular/Board gegen individuellen Softwarebau bestehen können.
11. **Falscher Forderungsstatus:** Keine Patientenmahnung, solange Versicherungsanteil, Denial oder Streit nicht geklärt/freigegeben ist.
12. **Vertraulichkeitsbruch:** Kein Kanzlei-/Gesundheitsdatensatz in ein unfreigegebenes Modell oder Consumer-Tool.
13. **Auto-Reject kreativer Arbeit:** Tattoo-/Designanfragen nicht allein nach KI-Score ablehnen.
14. **Marktproblem als Prozessproblem:** Beim Möbelbauer nicht „mehr Marketing automatisieren“, wenn Preis und Deckungsbeitrag ungeklärt sind.
15. **Notfall falsch normalisieren:** Wartungsmeldung mit Gefahrindikator nie automatisch in eine normale Queue legen.
16. **Unbelegte Fachwerte:** Keine VIN-Teile, Laborzeiten, Rechtslage, medizinische Verantwortung oder Kosten aus Modellwissen erfinden.
17. **Auftrags- statt Objektgranularität:** Drei Teppiche oder zwanzig Order Lines benötigen Einzelobjekt-/Teilstatus, nicht nur einen Auftrags-Haken.
18. **Manipulierbare Historie:** Bei Fremdeigentum/Bestand keine harte Löschung; Korrektur als neues Ereignis mit Nutzer und Grund.

## Konkrete Konsequenz für das Datenmodell von AI Start Map

Mindestens folgende Entitäten sollten Diagnose und RAG-Playbooks unterscheiden:

- `process`: Trigger, Ergebnis, Frequenz, Owner, SLA
- `step`: Reihenfolge, Rolle, System, Dauer, Input, Output
- `decision`: Regel, benötigte Daten, menschliche Autorität
- `artifact`: Dokument/Foto/Notiz/Datensatz, Speicherort, Version
- `handoff`: Sender, Empfänger, Kanal, Wartezeit
- `exception`: Auslöser, Reparaturweg, Häufigkeit, Schaden
- `constraint`: hart/weich, Wert, Quelle, Gültigkeit
- `integration`: System, Zugriffsmethode, verifiziert ja/nein
- `object_instance`: physisches/digitales Einzelobjekt, Parent-Auftrag, ID/Label, Zustand, Standort
- `status_event`: vorher/nachher, Zeit, Akteur, Quelle, Beleg, Korrekturgrund
- `approval`: Entscheidungstyp, befugte Rolle, Status, Zeitpunkt, Evidenz
- `evidence`: Foto, Claim-Antwort, Kundenfreigabe, Rechnung, Scan oder Bericht; Herkunft und Integrität
- `data_classification`: Sensibilität, zulässige Systeme/Kanäle, Aufbewahrung, Einwilligung/Vertrag
- `economics`: Plan-/Ist-Zeit, Material, Preis, Marge, Opportunitätskosten
- `automation_candidate`: Nutzen, Aufwand, Risiko, Freigabe, Datenreife
- `test_case`: Eingang, erwartete Diagnose, verbotene Empfehlung, Erfolgsbedingung

## Abschließendes Urteil

Die zehn Fälle zeigen, dass AI Start Map nicht mit der Frage „Welche Aufgabe nervt?“ enden darf. Es muss die **Granularität des Geschäftsobjekts**, die **Zustände**, die **Systemgrenzen**, die **Entscheidungsrechte**, die **Belege**, die **Wirtschaftlichkeit** und die **Ausnahmen** rekonstruieren.

Die wichtigste Produktlogik lautet deshalb:

```text
Problemäußerung
    → konkreten Prozess auswählen
    → Ist-Ablauf und Artefakte rekonstruieren
    → fehlende Prozessdaten dynamisch erfragen
    → Engpass und Automatisierungsreife bewerten
    → passende Playbooks abrufen
    → fallbezogene Chancen mit Human Gates rangieren
    → Negativtests gegen generische Empfehlungen ausführen
```

So wird aus einem allgemeinen Interview ein belastbarer Automation Blueprint.

### Benötigte übergreifende Produkttests

1. Derselbe Satz „Rechnungen bleiben offen“ muss bei Elektroservice zu Angebots-/Leistungsdaten, bei der Arztpraxis aber zuerst zu Versicherungsentscheidung, Datenschutz und Patientensaldo führen.
2. „Viele Anfragen“ muss bei Tattoo zu Kapazitätsfenster und Human Selection, bei Möbelbau zu Leadqualität/Deckungsbeitrag und bei Kanzlei zu Konflikt-/Fristgate führen.
3. „Wir nutzen schon Software“ darf weder bei Jobber noch AppFolio, Mitchell1 oder Square automatisch einen Systemwechsel auslösen; zuerst ist die konkrete Funktions- und Schnittstellenlücke zu beweisen.
4. „Ein Auftrag“ muss bei Etsy in Positionen/Teile und bei Teppichen in physische Einzelobjekte zerfallen.
5. „KI kann vorsortieren“ muss je Domäne verschiedene Stop-Gates erzeugen: Notfall, Mandatsvertraulichkeit, Patientensaldo, kreative Auswahl, technische Teilepassung.
6. Ein Low-Volume-Fall muss eine einfache Checkliste/Formularlösung höher ranken können als RAG, Agent oder individuelle App.
7. Jede Empfehlung muss einen messbaren Vorher-/Nachher-Wert nennen können: Minuten, Fehler/Nachdruck, offene Salden, Fahrzeit, Durchlaufzeit, Bestandsdifferenz oder Deckungsbeitrag.
