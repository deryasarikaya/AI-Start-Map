# Mentor-Demo 2026-08-07

**Status:** Reproduzierbarer Live-Nachweis auf `feature/gate-cascade-quality`

**Prüfdatum:** 2026-08-07

**Zweck:** Fünf konkrete Fälle der neuen Zielgruppe gegen die vollständige Nutzerreise, tatsächlichen Modelloutput, Ergebnisansicht und Druckbericht prüfen.

## Prüfmethode und Grenzen

Die Anwendung lief lokal mit der konfigurierten PostgreSQL-Datenbank und der vorhandenen OpenAI-Konfiguration. Der komplette Weg wurde zunächst in einem JavaScript-deaktivierten Chromium durchlaufen; die schreibenden Formulare wurden dabei genau einmal über den zum Browserkontext gehörenden Request-Client gesendet. Damit wurde zugleich der vorgesehene Fallback ohne JavaScript geprüft. Eine zweite kontrollierte Wiederholung über die realen HTTP-Endpunkte verwendete die unten wörtlich dokumentierten Unicode-Eingaben. Die finalen Ergebnis- und Berichtseiten wurden danach für jeden Fall erneut in Chromium gerendert und der Bericht als PDF gedruckt.

Die angemeldete Browser-Erweiterungssteuerung war in dieser Sitzung instabil und lief in Timeouts. Sie wurde nicht als Nachweis verwendet. Die ersatzweise Chromium-Prüfung war lokal reproduzierbar, testete aber weder Safari noch ein physisches Mobilgerät. Problemfamilien und Gates werden derzeit nicht persistiert; die unten genannten Werte wurden unmittelbar nach den Läufen mit demselben semantischen Klassifikator und Selector aus den exakt gespeicherten Eingaben rekonstruiert. Sie sind deshalb nachvollziehbare Rekonstruktion, aber kein persistierter Entscheidungstrace.

Alle Beispielwerte stehen ausschließlich in sichtbar als Vorschau oder Beispiel gekennzeichneten Bereichen. Sie wurden nicht als Nutzerfakten dargestellt.

## Gesamtbefund

| Fall | Laufstatus | Hauptmuster | Autonomie | Rückfragen | PDF | Fachlicher Befund |
|---|---|---|---|---:|---:|---|
| Hausmeisterservice | vollständig | SP-03 | A1 | 1 | 2 Seiten | passend |
| Fotograf | vollständig | SP-02 | A1 | 1 | 2 Seiten | passend |
| Blumenladen | vollständig | SP-01 | A1 | 1 | 2 Seiten | passend nach PF-02-Abgrenzung |
| Coach | vollständig | SP-02 | A1 | 0 | 2 Seiten | passend |
| vorhandene Kalenderfunktion | vollständig | kein KI-Muster | A0 | 0 | 2 Seiten | passend |

Alle zehn finalen Seitenaufrufe (`results` und `report`) antworteten mit HTTP 200. Nach der Klartext-Überarbeitung wurden alle fünf gespeicherten Fälle erneut als PDF gerendert: jeder Bericht umfasst genau zwei nichtleere Seiten, zeigt keine localhost-URL und enthält keinen Begriff aus der Kunden-Verbotsliste. Die fachliche Auswahl der ursprünglichen Live-Läufe wurde dafür nicht erneut ausgeführt oder verändert.

## Fall 1 – Hausmeisterservice

**Tatsächliche Eingabe**

> Ich betreibe einen kleinen Hausmeisterservice. Nach jedem Außeneinsatz spreche ich eine kurze Sprachnachricht, mache Fotos von der erledigten Arbeit und fotografiere den Kassenbon für Material. Diese digitalen Angaben liegen danach getrennt auf dem Handy und müssen abends manuell zu einer Einsatznotiz und einer Rechnungsgrundlage zusammengeführt werden. Preise und Rechnungsfreigabe prüfe ich immer selbst.

- Erkannte Problemfamilien: PF-08, ergänzend PF-03 und PF-12.
- Ausgewähltes Solution Pattern: SP-03, mobile Einsatzdokumentation aus Sprache, Fotos und Bon; SP-04 wurde nicht gewählt, weil kein angenommener oder gelagerter Gegenstand beschrieben ist.
- Gates: GATE-01 pass, GATE-02 pass, GATE-03 fail, GATE-04 pass, GATE-05 pass, GATE-06 unknown. Der noch nicht ausreichend strukturierte Zieloutput und offene Berechtigungen begrenzen auf A1.
- Rückfrage: „Wer muss zustimmen, bevor es weitergehen darf?“ – „Ich weiß es gerade nicht“.
- Sichtbarer Zielworkflow: Medien einem Einsatzanker zuordnen, Angaben auslesen, Pflichtfelder und Zuordnung regelbasiert prüfen, Einsatznotizentwurf anzeigen und erst nach menschlicher Prüfung speichern beziehungsweise einen Rechnungsentwurf vorbereiten.
- Beispieloutput: klar als Vorschau markierte Einsatznotiz mit Kunde/Objekt, Tätigkeit, Arbeitszeit, Material, Besonderheiten, offenen Punkten und möglichen Anhängen.
- Offene Angaben: Fallzahl, konkrete Freigaberolle, heutige Handy-Ablage und dauerhafte Originalbelegablage.
- PDF: drei nichtleere Seiten, keine internen IDs, Diagnosehinweis vorhanden.
- Fachlicher Befund: passend. Preis und Rechnungsfreigabe bleiben ausdrücklich menschlich; Beispielwerte wurden nicht als Tatsachen ausgegeben.
- Laufzeit der Unicode-End-to-End-Wiederholung: 83,968 Sekunden.

## Fall 2 – Fotograf

**Tatsächliche Eingabe**

> Ich arbeite als Fotograf. Briefings und Änderungswünsche kommen per E-Mail, WhatsApp und manchmal als Sprachnachricht. Für jeden Auftrag muss ich alles manuell in einer Vorgangsakte sammeln und nachhalten, welche Bildauswahl der Kunde freigegeben hat. Die endgültige Freigabe und Herausgabe entscheide immer ich.

- Erkannte Problemfamilien: PF-01, ergänzend PF-03 und PF-11.
- Ausgewähltes Solution Pattern: SP-02, einfache Vorgangsakte mit Status und nächstem Schritt.
- Gates: GATE-01 pass, GATE-02 fail, GATE-03 fail, GATE-04 pass, GATE-05 pass, GATE-06 unknown. Der gemeinsame Vorgangsanker und ein vollständig strukturierter Zieloutput sind noch nicht bestätigt; deshalb A1.
- Rückfrage: „Wer muss zustimmen, bevor es weitergehen darf?“ – „Ich weiß es gerade nicht“.
- Sichtbarer Zielworkflow: relevante Quellen auswählen, Kerndaten und Unsicherheiten extrahieren, Pflichtfelder prüfen, Vorgangskarte erzeugen und Status beziehungsweise Abschluss nur nach menschlicher Bestätigung speichern.
- Beispieloutput: als Vorschau gekennzeichnete Vorgangsakte mit Referenz, Status, nächstem Schritt, Verantwortung, Fälligkeit, offenen Punkten und Beispielanhängen.
- Offene Angaben: Umgang mit Sprachnachrichten, vorhandene Benennungsroutine und genaue Freigaberollen.
- PDF: drei nichtleere Seiten, keine internen IDs.
- Fachlicher Befund: passend. Bildfreigabe und Herausgabe bleiben beim Fotografen. Die Formulierung „Nutzer wählt“ wurde in der Kundensicht zu direkter Du-Sprache normalisiert.
- Laufzeit der Unicode-End-to-End-Wiederholung: 99,154 Sekunden.

## Fall 3 – Blumenladen

**Tatsächliche Eingabe**

> Ich betreibe einen Blumenladen. Anfragen und Bestellwünsche kommen digital über WhatsApp, Instagram und E-Mail. Ich übertrage sie manuell in eine gemeinsame Übersicht und verliere dabei manchmal den Status oder offene Angaben. Preis, Machbarkeit und die verbindliche Annahme jeder Bestellung prüfe ich selbst.

- Erkannte Problemfamilien: PF-02, ergänzend PF-03 und PF-11.
- Ausgewähltes Solution Pattern: SP-01, gemeinsamer Anfrageeingang mit Missing-Info-Prüfung.
- Gates: GATE-01 pass, GATE-02 fail, GATE-03 fail, GATE-04 pass, GATE-05 pass, GATE-06 unknown. Ein fester Vorgangsanker und vollständiger Zieloutput fehlen noch; deshalb A1.
- Rückfrage: „Wer muss zustimmen, bevor es weitergehen darf?“ – „Ich weiß es gerade nicht“.
- Sichtbarer Zielworkflow: Nachricht einem gemeinsamen Eingang zuordnen, eine Anfragekarte mit erkannten und fehlenden Angaben als Entwurf erzeugen und Annahme, Preis sowie Termin erst nach menschlicher Prüfung speichern.
- Beispieloutput: als Vorschau markierte Anfragekarte mit Kontakt, Anliegen, Kanal, Eingangszeit, fehlenden Angaben und Status.
- Offene Angaben: Aufbau der heutigen Übersicht, verbindliche Freigaberolle, Verantwortung für Rückfragen und typische Mindestangaben.
- PDF: drei nichtleere Seiten, keine internen IDs.
- Fachlicher Befund: passend nach einer gezielten semantischen Abgrenzung. Der erste Lauf priorisierte wegen der manuellen Übertragung PF-03 und lieferte SP-06. Der Klassifikationsprompt stellt nun klar, dass neue kanalübergreifende Anfragen mit verlorenem Status und fehlenden Angaben PF-02 dominieren; der Wiederholungslauf lieferte SP-01. Keine Bestellung wird automatisch angenommen.
- Laufzeit des finalen Unicode-End-to-End-Laufs: 138,469 Sekunden.

## Fall 4 – Coach

**Tatsächliche Eingabe**

> Ich bin selbstständiger Coach. Vor Terminen liegen Kundenanfrage, meine digitalen Notizen und Kalendereintrag getrennt vor. Ich sammle die Informationen jedes Mal manuell für eine strukturierte Gesprächsvorbereitung. Die fachliche Bewertung und alle Entscheidungen im Gespräch bleiben bei mir.

- Erkannte Problemfamilien: PF-01, ergänzend PF-03 und PF-11.
- Ausgewähltes Solution Pattern: SP-02, einfache Vorgangsakte mit Status und nächstem Schritt.
- Gates: GATE-01 pass, GATE-02 fail, GATE-03 fail, GATE-04 pass, GATE-05 pass, GATE-06 unknown; deshalb A1.
- Rückfrage: keine. Die bestehende Beschreibung reichte für eine sichere A1-Empfehlung.
- Sichtbarer Zielworkflow: Terminquellen zuordnen, Kernaussagen und Unsicherheiten extrahieren, Pflichtfelder prüfen, Vorbereitung als Entwurf erzeugen und erst nach fachlicher Bestätigung speichern.
- Beispieloutput: als Vorschau gekennzeichnete Vorgangsakte mit Status, nächstem Schritt, Verantwortung, Fälligkeit und offenen Punkten.
- Offene Angaben: Volumen, konkrete Systeme/Formate, vorhandene Vorbereitungsvorlage und Berechtigungen/Einwilligungen.
- PDF: drei nichtleere Seiten, keine internen IDs.
- Fachlicher Befund: passend. Die KI strukturiert nur die Vorbereitung; fachliche Bewertung und Gesprächsentscheidungen bleiben beim Coach.
- Laufzeit der Unicode-End-to-End-Wiederholung: 73,416 Sekunden.

## Fall 5 – A0: vorhandene Kalenderfunktion reicht

**Tatsächliche Eingabe**

> Alle Termine stehen bereits vollständig in meinem digitalen Kalender. Es gibt keine verteilten Nachrichten, Dokumente oder Notizen und ich brauche keine Zusammenfassung oder Texterkennung. Ich möchte nur die vorhandene Erinnerungsfunktion des Kalenders einschalten und eine feste Farbe für neue Termine verwenden. Dafür ist keine KI nötig.

- Erkannte Problemfamilien: keine.
- Ausgewähltes Solution Pattern: keines; Modus `non_ai_first`.
- Gates: GATE-01 fail, GATE-02 fail, GATE-03 pass, GATE-04 pass, GATE-05 pass, GATE-06 unknown. Der fehlende KI-Engpass führt ausdrücklich zu A0.
- Rückfrage: keine.
- Sichtbarer Zielworkflow: vorhandene Kalender-Standardeinstellungen setzen, an einem konkreten Beispiel prüfen und bei Bedarf zentral anpassen.
- Beispieloutput: deutlich als Orientierung markierte Kalender-Einstellungsvorschau; Plattform, Erinnerungsart und Farbe bleiben offen und werden nicht als Nutzerwerte behauptet.
- PDF: zwei nichtleere Seiten, keine internen IDs.
- Fachlicher Befund: passend nach einem Live-Fund. Der erste Lauf wurde trotz ausdrücklichem „keine KI nötig“ als A1/SP-02 formuliert. Der Selector erkennt jetzt die ausdrücklich gewünschte vorhandene Funktion deterministisch als A0; der Kundenvertrag entfernt KI-Empfehlungen und sekundäre Möglichkeiten.
- Latenz: Der komplette Lauf endete serverseitig erfolgreich; der erste Erfassungsclient beendete sich beim lokalen PDF-Capture nicht sauber, daher ist keine belastbare Gesamtzeit vorhanden. Der isolierte finale A0-Bericht wurde nach Bereinigung des Capture-Prozesses in Chromium erfolgreich erzeugt.

## Latenz, Fehler und Retries

- Ein früher kontrollierter Hausmeister-Finalaufruf benötigte 60,141 Sekunden und keinen Retry.
- Die finalen Unicode-End-to-End-Läufe benötigten 83,968 Sekunden (Hausmeister), 99,154 Sekunden (Fotograf), 138,469 Sekunden (Blumenladen) und 73,416 Sekunden (Coach). Diese Zeiten enthalten mehrere Modellschritte und sind keine reine FinalAnalysis-Latenz.
- Vor der Reparatur direkter Kundensprache scheiterten Fotograf, Blumenladen und A0 jeweils nach beiden FinalAnalysis-Versuchen, weil `user_action` oder `human_check` kein wörtliches „du“ enthielt. Danach wurden die betroffenen Felder deterministisch repariert, statt die gesamte Analyse zu verwerfen; alle finalen Wiederholungen liefen durch.
- Die erfolgreiche Retry-Anzahl wird derzeit nicht pro Analyse persistiert. Aus dem HTTP-Ergebnis lässt sich deshalb keine belastbare Quote ableiten. Kein final dokumentierter Lauf endete mit 503.

## Solution-Retrieval-Vergleich

Je Demo und ausgewähltem Solution Pattern waren drei positive Workflows zulässig; zwei wurden zur Anreicherung zurückgegeben. Beim Hausmeister und Fotografen entsprach die semantische Reihenfolge exakt der deterministischen Kanalreihenfolge. Beim Blumenladen und Coach wurden dieselben zwei Workflows nur umgekehrt sortiert. Bei insgesamt 28 Workflows beziehungsweise 27 positiven Index-Chunks ist damit in dieser Fünferprobe kein messbarer fachlicher Mehrwert gegenüber der deterministischen Auswahl belegt. Der Index bleibt ein begrenzter Varianten-Ranker mit deterministischem Fallback, nicht die Entscheidungsebene.

## Mentor-Demo-Anleitung

1. PostgreSQL und die lokale `.env` mit `DATABASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL` und optional `SESSION_SIGNING_KEY` bereitstellen.
2. `alembic upgrade head` ausführen.
3. Mit `uvicorn app.main:app --reload` starten und `http://127.0.0.1:8000` öffnen.
4. Einen der oben wörtlich dokumentierten Texte einfügen.
5. Die erste erkannte Prozessoption auswählen, die Ist-Zusammenfassung prüfen und bestätigen.
6. Falls die Freigabefrage erscheint, ehrlich antworten oder „Weiß ich gerade nicht“ wählen.
7. Analyse abwarten. Nicht mehrfach absenden; die Seite wechselt selbstständig zum Ergebnis.
8. Auf der Ergebnisansicht Engpass, Empfehlung, Zukunftsablauf, Rollen, Beispielvorschau, Human Check, kleinsten Einstieg und Grenzen zeigen.
9. „Bericht drucken / als PDF speichern“ öffnen und im Browserdruckdialog als PDF speichern. Der Browser hängt die Datei nicht automatisch an eine E-Mail an.
10. Für die fachliche Kernbotschaft zuerst Hausmeister, Blumenladen und A0 zeigen: konkreter KI-Workflow, kanalübergreifende Anfrageerfassung und ehrlicher Nicht-KI-Fall.

## Bekannte verbleibende Einschränkungen

- Problemfamilien, Gates, Retrieval-IDs und Retry-Zahl werden nicht persistiert; eine spätere datenschutzarme Trace-Entscheidung bleibt offen.
- Vier KI-gestützte Demofälle endeten wegen offener Voraussetzungen konservativ auf A1. Das ist kein Fehler, aber die Gate-Schwellen müssen mit echten Interviews kalibriert werden.
- Der alte Diagnoseindex bleibt Legacy-Vergleichswissen aus dem archivierten früheren Korpus.
- Die vollständige Freigabe auf Safari, physischem Android/iPhone und verschiedenen nativen Druckdialogen ist nicht erfolgt.
- Die Modellausgabe kann weiter sprachlich dicht sein. Feldlängen, interne IDs, direkte Ansprache und unvollständig abgeschnittene Zukunftsschritte sind nun technisch abgesichert; fachliche Verständlichkeit benötigt weiterhin reale Nutzerbeobachtung.
