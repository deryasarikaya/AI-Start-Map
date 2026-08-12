# Stand nach dem Feinschliff

Alle vier Fälle aus `TESTFAELLE_ZIELGRUPPE.md`, komplett durch die echte App.
Vergleichsstand: `lauf_nachher.md`.

## Übersicht

| Fall | reifestufe | ergebnis_art | darstellung | Dauer |
|---|---|---|---|---|
| Blumenladen | genai | Karte | karte | 133.4 s |
| Fotograf | genai | Anfragekarte | karte | 82.0 s |
| Handwerksbetrieb | genai | Einsatznotiz | nachricht | 165.2 s |
| Malerbetrieb (Fall 8) | digitalisierung | Auftragskarte | nachricht | 106.3 s |

## Überschriften — vorher und nachher

| Fall | vorher | nachher |
|---|---|---|
| Blumenladen | Du arbeitest zweimal für Bestellungen | Du suchst Bestellinfos in Chats und Zetteln |
| Fotograf | Du bist die Suchmaschine deiner Shootings | Du baust jedes Briefing neu zusammen |
| Handwerksbetrieb | Wichtiges taucht erst bei der Rechnung auf | Du suchst rechnungsfähige Leistungen in Fotos und Bons |
| Malerbetrieb (Fall 8) | — (neuer Fall) | Telefonaufträge bleiben nur im Kopf |

| Fall | loesung.titel |
|---|---|
| Blumenladen | Eine Bestellkarte aus WhatsApp, Anruf und Shop |
| Fotograf | Eine Anfragekarte für jedes Shooting |
| Handwerksbetrieb | Mobile Einsatznotiz aus Sprache, Foto und Bon |
| Malerbetrieb (Fall 8) | Aus einem Anruf wird eine Auftragskarte |

## Was sich belegen lässt

`reifestufe` ist nicht mehr überall gleich: der Malerbetrieb landet auf
`digitalisierung`, die übrigen drei auf `genai`. Damit ist erstmals belegt,
dass das System auch „hier hilft KI noch nicht" sagen kann.

Kein Feld endet mehr an seiner Grenze oder mitten im Wort. Die Ablaufschritte
sind von 180 Zeichen und 23 Wörtern auf 82 bis 92 Zeichen und 12 bis 15 Wörter
gefallen — die Fünfzehn-Wörter-Regel wirkt, ohne dass ein Deckel greift.

„trainier", „anlern" und „Lernphase" kommen in keinem der vier Fälle vor.

## Zur Laufzeit — kontrolliert gemessen

Die Vermutung, die zusätzlich geladene Wissensdatei mache den Handwerksfall
langsam, ist widerlegt. Zwei Läufe desselben Falls:

| | Dauer | Kundentext | `was_die_ki_macht` |
|---|---|---|---|
| mit Wissensdatei | 87,1 s | 4933 Zeichen | 427 Zeichen |
| ohne Wissensdatei | 245,3 s | 5309 Zeichen | 439 Zeichen |

Der Lauf mit der größeren Eingabe war dreimal schneller und erzeugte weniger
Text. Die Streuung kommt von der API, nicht von der Eingabe- oder
Ausgabelänge. Nichts wurde gekürzt; stattdessen liegt das Budget bei 300
Sekunden und ein Zeitablauf bekommt genau einen zweiten Versuch.

---

## Blumenladen — gerenderte Ergebnisseite

**reifestufe:** genai · **ergebnis_art:** Karte · **darstellung:** karte · **Dauer:** 133.4 s

```
Deine Empfehlung · AI Start Map
AI
AI START MAP
Erzählen ✓ Verstehen ✓ Ergebnis ●
DEINE AUSWERTUNG · Zentrale Auftragserfassung für alle Bestellkanäle
Du suchst Bestellinfos in Chats und Zetteln
Bestellungen kommen bei dir über WhatsApp, Instagram, E‑Mail, Anrufe und den Onlineshop rein. Die Details liegen verteilt in Chats, Fotos und auf Zetteln, so dass ihr beim Vorbereiten oft in mehreren Quellen nachsehen oder nochmals nachfragen müsst.
SO LÄUFT ES HEUTE
So habe ich deinen heutigen Ablauf verstanden
1 Bestellung kommt über einen der Kanäle rein (WhatsApp, Instagram, E‑Mail, Anruf, Onlineshop).
2 Während des Tages notiert die Inhaberin Informationen informell: auf Zetteln, in der Foto‑Galerie oder merkt sich Details kurz.
3 Fotos, Lieferadressen und Sonderwünsche bleiben verteilt in Chats, Galerie oder auf dem Block neben der Kasse liegen.
4 Beim Vorbereiten oder Ausliefern durchsucht die Inhaberin mehrere Chats/Galerie/Notizen, um Details zur Bestellung zu klären.
5 Bei Anrufen sind oft hinterher keine schriftlichen Informationen vorhanden, daher muss nachgefragt oder geraten werden.
WO ARBEIT WEGFÄLLT
Hier lässt sich Arbeit aus deinem Ablauf nehmen
Größter Hebel
Ein Eingang, der alle Bestellungen sammelt
Wenn alle Nachrichten an einer Sammelstelle ankommen, lässt sich daraus eine einheitliche Bestellkarte erzeugen.
Danach
Anrufkurzregeln für fehlende Notizen
Telefonate verursachen die meisten Lücken; eine kurze Routine reduziert Nachfragen erheblich.
Später
Automatische Übergabe an Tagesplanung
Bestätigte Bestellungen könnten später direkt in die Lieferliste laufen.
SO WÜRDE DEINE LÖSUNG AUSSEHEN
Eine Bestellkarte aus WhatsApp, Anruf und Shop
Was reinkommt
WhatsApp, Instagram, E‑Mail, Telefon, Onlineshop
Was die KI macht
Die KI liest heraus, was bestellt wurde, wann geliefert werden soll, wohin geliefert wird und wer der Empfänger ist. Sie hängt das mitgeschickte Foto an die passende Bestellung, aus der Sprachnachricht wird Text, sie erkennt, wenn mehrere Nachrichten zur selben Bestellung gehören, markiert fehlende Angaben (z. B. Lieferadresse, Zahlungsart) und bereitet eine kurze Rückfrage sowie einen Antwortvorschlag vor.
Was du machst
Du prüfst und bestätigst jede Bestellkarte, entscheidest Preis, Lieferdatum und Zahlungsstatus und beantwortest Sonderwünsche.
Was dabei rauskommt
Eine Bestellkarte mit Status, offenen Angaben und Antwortentwurf
Heute und nach der Einrichtung
So läuft es heute
Bestellung kommt über WhatsApp, Instagram, E‑Mail, Telefon oder Shop rein.
Du notierst Infos informell auf Zetteln oder merkst sie dir nur kurz.
Fotos, Adressen und Sonderwünsche bleiben in Chats, Galerie oder auf dem Block.
Beim Vorbereiten suchst du in mehreren Quellen nach Details und fragst nach.
Nach der Einrichtung
Die eingehende Nachricht landet in einer Sammelstelle an einer Stelle.
Die KI liest die Nachricht und hängt angehängte Fotos an die Anfrage.
Aus Sprachnachrichten wird Text, und die KI liest die wichtigen Angaben heraus.
Fehlende Angaben werden markiert und ein kurzer Rückfrageentwurf erzeugt.
Du prüfst die Bestellkarte, bestätigst Preis und Lieferzeit, und setzt den Status.
DEIN KONKRETES ERGEBNIS
Was aus einer WhatsApp‑Nachricht wird
Beispielangaben zur Veranschaulichung – hier stehen später deine tatsächlichen Angaben.
Karte
zu prüfen
Name
Anna Weber
Telefon
0176 5551234
Gewünschter Strauß
rosa/weiß wie auf dem Foto
Lieferzeit
Dienstag 18.8. vormittags
Foto
angehängt
Fehlt noch: Lieferadresse · Zahlungsart
geht erst nach deiner Freigabe raus
Vorbereitete Rückfrage: „Welche Lieferadresse? Und wie möchtest du zahlen (Bar, Karte oder Überweisung)?“
So kommt es heute bei dir an — WhatsApp Hi, für meine Mutter bitte einen Strauß in rosa/weiß wie auf dem Foto. Lieferung Dienstag 18.8. vormittags. Schickst du mir den Preis? LG Anna Weber 0176 5551234
WAS DU DAFÜR BRAUCHST
Das behältst du, das kommt dazu
Das bleibt
WhatsApp
Instagram
E‑Mail
Telefon
Onlineshop
Foto‑Galerie
Zettel/Block neben der Kasse
Das kommt dazu
eine Sammelstelle, an die eingehende Nachrichten weitergeleitet werden
eine Seite, auf der alle Bestellungen untereinander stehen
die Anbindung, die Nachrichten liest und Bestellkarten vorschlägt
Dein Smartphone und dein Laptop reichen. Die Bestellkarten siehst du auf einer Seite im Internet, die du auf den Startbildschirm legen kannst.
WAS ICH DAFÜR EINRICHTE
Das würde ich für dich bauen oder verbinden
Dies ist die Diagnose. Gebaut ist noch nichts.
Ich richte eine Sammelstelle ein, die Nachrichten aus WhatsApp, Instagram, E‑Mail und dem Shop annimmt.
Ich passe an, welche Angaben erkannt werden: Name, Adresse, Lieferzeit, Strauß, Foto, Zahlung.
Ich stelle ein, dass aus einer Sprachnachricht Text wird und Fotos an die richtige Anfrage gehängt werden.
Ich teste an echten Bestellungen und korrigiere, worauf die KI achten soll.
Ich lege kurze Vorlagen für Rückfragen und Bestätigungen an.
Ich starte mit einer einwöchigen Probe, prüfe fünf reale Bestellungen und passe die Erkennung an.
DEINE SICHERHEIT
Das bleibt bei dir
Du prüfst und bestätigst jede Bestellkarte. Du entscheidest Preis, Lieferdatum und Sonderwünsche.
EHRLICH GESAGT
Eine Grenze
Unaufgezeichnete Telefonate kann niemand später vollständig rekonstruieren; die Lösung markiert fehlende Angaben und fragt nach oder sie müssen kurz protokolliert werden.
Einen anderen Ablauf ansehen
GEMEINSAM UMSETZEN
Möchtest du das umsetzen?
Ich bin Derya. Genau das würde ich für dich einrichten: Eine Bestellkarte aus WhatsApp, Anruf und Shop. Du schickst weiter wie bisher, ich baue den Rest.
PDF speichern Umsetzung besprechen
Im Druckdialog bitte „Kopf- und Fußzeilen“ abwählen.
Ich prüfe deine Angaben.
Du musst nichts weiter tun. Gleich geht es automatisch weiter.
```

---

## Fotograf — gerenderte Ergebnisseite

**reifestufe:** genai · **ergebnis_art:** Anfragekarte · **darstellung:** karte · **Dauer:** 82.0 s

```
Deine Empfehlung · AI Start Map
AI
AI START MAP
Erzählen ✓ Verstehen ✓ Ergebnis ●
DEINE AUSWERTUNG · Kundenbriefing vor Shooting zusammenstellen
Du baust jedes Briefing neu zusammen
Die Infos für ein Shooting kommen über Wochen verteilt in Instagram, über die Website und per Mail. Weil nichts an einer Stelle steht, musst du die Nachrichten jedes Mal manuell zu einem Briefing zusammensetzen und übersiehst leicht Angaben oder die aktuelle Fassung.
SO LÄUFT ES HEUTE
So habe ich deinen heutigen Ablauf verstanden
1 Nachrichten in Instagram, Website und Mail lesen
2 Informationen über Wochen sammeln
3 Notizen zusammenführen und Briefing schreiben
4 Briefing finalisieren
WO ARBEIT WEGFÄLLT
Hier lässt sich Arbeit aus deinem Ablauf nehmen
Größter Hebel
Zentrale Anfragekarte pro Shooting
Sammelst du alle Nachrichten an einer Stelle, lassen sie sich automatisch zusammenführen und prüfen.
Danach
Kurzes Eingangsformular auf der Website
Ein knappes Formular fängt die wichtigsten Angaben sofort ein und reduziert Rückfragen.
Später
Übernahme bestätigter Briefings in Kalender
Bestätigte Termine automatisch an deinen Kalender zu hängen spart manuelle Übertragung.
SO WÜRDE DEINE LÖSUNG AUSSEHEN
Eine Anfragekarte für jedes Shooting
Was reinkommt
Instagram, Website, Mail
Was die KI macht
Die KI erkennt, welche Nachrichten zur selben Anfrage gehören, liest heraus Datum und Uhrzeit, Ort, wer teilnimmt, Stilwunsch und welche Beispielbilder angehängt wurden. Sie hängt gefundene Bilder an die richtige Anfrage, markiert, welche Angaben noch fehlen, und schreibt eine zweizeilige Zusammenfassung sowie einen Antwortentwurf.
Was du machst
Du entscheidest Dringlichkeit, bestätigst Annahme und Termin, prüfst fehlende Angaben und gibst das finale Briefing frei.
Was dabei rauskommt
Eine Anfragekarte mit Status, offenen Angaben und Antwortentwurf.
Heute und nach der Einrichtung
So läuft es heute
Du liest Nachrichten von Instagram, der Website und per Mail.
Über Wochen ergänzt der Kunde Infos in verschiedenen Nachrichten.
Du suchst die Angaben zusammen und schreibst ein Briefing.
Du finalisierst das Briefing manuell und merkst dir die Fassung.
Nach der Einrichtung
Eingehende Nachrichten werden an eine Sammelstelle weitergeleitet.
Die KI fasst zugehörige Nachrichten zu einer Anfragekarte zusammen.
Die KI liest heraus Datum, Ort, Teilnehmende, Stilwunsch und angehängte Bilder.
Die KI markiert fehlende Angaben und erstellt einen kurzen Antwortentwurf.
Du prüfst die Karte, ergänzt fehlende Angaben und bestätigst das Briefing.
DEIN KONKRETES ERGEBNIS
Was aus einer Instagram-Nachricht wird
Beispielangaben zur Veranschaulichung – hier stehen später deine tatsächlichen Angaben.
Anfragekarte
zu prüfen
Kunde
Unbekannt (Instagram-Nutzer)
Wunsch
Familienshooting am See, Sommer
Beispielbild
Verweis auf Feed
Fehlt noch: genaues Datum oder Zeit · wer genau kommt und wie viele Personen
geht erst nach deiner Freigabe raus
Vorbereitete Rückfrage: „Welcher Monat und welche Uhrzeit passt? Wer kommt genau (Anzahl und Name der Teilnehmenden)?“
So kommt es heute bei dir an — Instagram Hi! Wir würden gern ein Familienshooting am See machen, nächstes Jahr im Sommer. Mit Oma vielleicht. Habt ihr da Termine? Hab schon ein paar Bilder in eurem Feed gesehen, gefällt uns. Schick mal Preise :)
WAS DU DAFÜR BRAUCHST
Das behältst du, das kommt dazu
Das bleibt
Instagram
Website (Kontaktformular/Anfrage)
E-Mail
Bildergalerie für Kunden
Das kommt dazu
Eine Sammelstelle, an die eingehende Nachrichten weitergeleitet werden
Ein Dienst, der Nachrichten zusammenführt und die Angaben liest
Dein Smartphone und dein Laptop reichen. Du öffnest eine Seite im Browser, auf der jede Anfrage als Karte steht; die Seite lässt sich als Startbildschirm speichern.
Das müsstest du besorgen
Weiterleitung oder Freigabe für deine E‑Mail und die Bereitschaft, Instagram‑Nachrichten an die Sammelstelle weiterzuleiten
Zugriff auf Beispielbilder in deiner Galerie, damit sie automatisch angehängt werden können
WAS ICH DAFÜR EINRICHTE
Das würde ich für dich bauen oder verbinden
Das ist die Diagnose und der Plan. Gebaut ist noch nichts.
Ich richte die Sammelstelle ein und verbinde die Kanäle, die weitergeleitet werden können.
Ich stelle die Regeln so ein, dass zusammengehörige Nachrichten zu einer Anfragekarte gebündelt werden.
Ich passe an, welche Angaben erkannt werden und markiert werden sollen.
Ich teste das System an deinen echten Fällen und korrigiere die Erkennung an deinen Beispielen.
Ich sammle mit dir zusammen Zugangsdaten oder Weiterleitungen und teste die Sammelstelle an den letzten eingegangenen Anfragen; nach wenigen Testfällen zeige ich dir die erzeugten Karten zur Freigabe.
DEINE SICHERHEIT
Das bleibt bei dir
Du prüfst und bestätigst die Dringlichkeit, Termine, Preise und das finale Briefing. Rechnungen und rechtliche Zusagen machst du weiterhin selbst.
EHRLICH GESAGT
Eine Grenze
Fehlende Angaben, die nie schriftlich genannt wurden, kann die KI nicht zuverlässig ergänzen. Die KI erstellt nur Entwürfe; versenden, Preise festlegen oder Rechnungen auslösen bleibt deine Entscheidung.
Einen anderen Ablauf ansehen
GEMEINSAM UMSETZEN
Möchtest du das umsetzen?
Ich bin Derya. Genau das würde ich für dich einrichten: Eine Anfragekarte für jedes Shooting. Du schickst weiter wie bisher, ich baue den Rest.
PDF speichern Umsetzung besprechen
Im Druckdialog bitte „Kopf- und Fußzeilen“ abwählen.
Ich prüfe deine Angaben.
Du musst nichts weiter tun. Gleich geht es automatisch weiter.
```

---

## Handwerksbetrieb — gerenderte Ergebnisseite

**reifestufe:** genai · **ergebnis_art:** Einsatznotiz · **darstellung:** nachricht · **Dauer:** 165.2 s

```
Deine Empfehlung · AI Start Map
AI
AI START MAP
Erzählen ✓ Verstehen ✓ Ergebnis ●
DEINE AUSWERTUNG · Auftragsdokumentation vor Ort bis Rechnung
Du suchst rechnungsfähige Leistungen in Fotos und Bons
Vor Ort entstehen Sprachnotizen, Fotos und Bons, aber sie bleiben auf den Handys der Kollegen. Erst beim Rechnungsschreiben setzt die Leitung alles zusammen und entdeckt oft Zusatzarbeiten und fehlendes Material. Dadurch gehen Leistungen verloren und die Abrechnung dauert lange.
SO LÄUFT ES HEUTE
So habe ich deinen heutigen Ablauf verstanden
1 Techniker notiert vor Ort handschriftlich oder gar nicht, welche Arbeiten durchgeführt wurden
2 Techniker macht meist Fotos mit dem Diensthandy, die auf dem Gerät verbleiben
3 Materialkäufe tätigt der Techniker selbst und sammelt Kassenbons
4 Auftragsdaten und Fotos werden nicht konsequent zentral übergeben; Informationen bleiben verteilt oder fehlen
5 Am Monatsende setzt die Leitung alle Notizen, Bons und Fotos zusammen und erstellt die Rechnung in der Buchhaltungssoftware
WO ARBEIT WEGFÄLLT
Hier lässt sich Arbeit aus deinem Ablauf nehmen
Größter Hebel
Ein kurzes Abschluss-Paket pro Einsatz
Wenn nach jedem Einsatz eine kurze Einsatznummer mit Sprachnachricht, Fotos und Bon kommt, lässt sich später alles zuordnen.
Danach
Bons sofort lesen und zuordnen
Wenn der Bon automatisch Lieferant, Datum, Betrag und Positionen meldet, lassen sich Materialkosten direkt einem Einsatz zuweisen.
SO WÜRDE DEINE LÖSUNG AUSSEHEN
Mobile Einsatznotiz aus Sprache, Foto und Bon
Was reinkommt
Telefon, E‑Mail, WhatsApp
Was die KI macht
wandelt die Sprachnachricht nach dem Einsatz in Text um; liest den Bon und nennt Lieferant, Datum, Betrag und Positionen; ordnet Fotos dem richtigen Einsatz zu; erkennt Tätigkeit, Arbeitsdauer und verwendetes Material; erkennt zusätzlich ausgeführte Arbeiten; markiert unsichere oder fehlende Angaben; erstellt die Einsatznotiz als Entwurf; bereitet eine Rückfrage an den Techniker oder Kunden vor.
Was du machst
Du prüfst die Zuordnung von Foto, Text und Bon. Du bestätigst Arbeitszeit, Material und Zusatzarbeit. Du gibst die Einsatznotiz frei für die Rechnungserstellung.
Was dabei rauskommt
Eine prüfbare Einsatznotiz mit Anhängen und offenen Angaben.
Heute und nach der Einrichtung
So läuft es heute
Techniker notiert handschriftlich oder gar nicht, was gemacht wurde.
Fotos bleiben auf den Diensthandys liegen.
Materialbons werden gesammelt und später abgegeben.
Die Leitung sammelt alles am Monatsende und erstellt die Rechnung.
Nach der Einrichtung
Techniker schickt nach dem Einsatz eine kurze Sprachnachricht, Fotos und den Bon an die Sammeladresse.
Die KI wandelt die Sprachnachricht in Text um und liest den Bon aus.
Die KI ordnet Fotos, Text und Bon einer Einsatznummer zu und erzeugt eine Entwurf-Einsatznotiz.
Offene oder unsichere Angaben werden markiert und als Rückfrage vorbereitet.
Du prüfst die Einsatznotiz; nach Bestätigung wird ein Rechnungsentwurf vorbereitet.
DEIN KONKRETES ERGEBNIS
Was aus einer WhatsApp-Nachricht wird
Beispielangaben zur Veranschaulichung – hier stehen später deine tatsächlichen Angaben.
WhatsApp · Kundennachricht
Bin fertig bei Müllerstraße 12, 3. OG rechts. Lampe im Treppenhaus gemacht, Tür im Bad eingestellt. Fotos anbei. Hab Dichtung und Schrauben gekauft, Bon schicke ich noch. Dauert ungefähr 1 Std.
Vorbereitet für dich
Bitte schick den Bon als Foto und bestätige, ob der Kunde die Zusatzarbeit freigegeben hat.
Die Antwort wird dem Vorgang zugeordnet — abgeschickt wird sie erst, wenn du sie freigibst.
So kommt es heute bei dir an — WhatsApp Bin fertig bei Müllerstraße 12, 3. OG rechts. Lampe im Treppenhaus gemacht, Tür im Bad eingestellt. Fotos anbei. Hab Dichtung und Schrauben gekauft, Bon schicke ich noch. Dauert ungefähr 1 Std.
WAS DU DAFÜR BRAUCHST
Das behältst du, das kommt dazu
Das bleibt
Rechnungssoftware
gemeinsamer Kalender
Diensthandys
WhatsApp
E‑Mail
Telefon
Das kommt dazu
eine Sammeladresse im Internet, an die WhatsApp, E‑Mail und Fotos geschickt werden
ein Dienst, der aus Sprachnachricht Text macht, den Bon liest und Fotos einem Einsatz zuordnet
ein einfaches Nummernsystem für jeden Einsatz, sichtbar in Nachrichten
Dein Smartphone und dein Laptop reichen. Du greifst auf eine Seite im Internet zu, die du als Verknüpfung speichern kannst.
Das müsstest du besorgen
Die Mitarbeitenden müssen nach jedem Einsatz Sprachnachricht, Fotos und Bon an die Sammeladresse schicken, damit Zuordnung klappt.
WAS ICH DAFÜR EINRICHTE
Das würde ich für dich bauen oder verbinden
Das ist eine Diagnose. Gebaut ist noch nichts.
Ich richte die Sammeladresse ein, an die Nachrichten und Fotos laufen.
Ich verbinde den Kalender und die Rechnungssoftware, damit Einsätze erkennbar sind.
Ich stelle ein, worauf die KI achten soll und welche Angaben sie melden soll.
Ich teste an echten Einsätzen und passe an, welche Angaben erkannt werden.
Ich beginne mit einer zweiwöchigen Probe, in der jeder Techniker nach dem Einsatz Sprachnachricht, Fotos und Bons an die Sammeladresse schickt; ich prüfe fünf Fälle und passe die Erkennung an.
DEINE SICHERHEIT
Das bleibt bei dir
Du prüfst und bestätigst jede Einsatznotiz. Du gibst die Angaben frei, bevor eine Rechnung erzeugt wird.
EHRLICH GESAGT
Eine Grenze
Wenn vor Ort gar nichts festgehalten wird, lässt sich später keine lückenlose Dokumentation erzeugen; die KI liefert nur Entwürfe, du bestätigst Preise und Rechnungen.
Einen anderen Ablauf ansehen
GEMEINSAM UMSETZEN
Möchtest du das umsetzen?
Ich bin Derya. Genau das würde ich für dich einrichten: Mobile Einsatznotiz aus Sprache, Foto und Bon. Du schickst weiter wie bisher, ich baue den Rest.
PDF speichern Umsetzung besprechen
Im Druckdialog bitte „Kopf- und Fußzeilen“ abwählen.
Ich prüfe deine Angaben.
Du musst nichts weiter tun. Gleich geht es automatisch weiter.
```

---

## Malerbetrieb (Fall 8) — gerenderte Ergebnisseite

**reifestufe:** digitalisierung · **ergebnis_art:** Auftragskarte · **darstellung:** nachricht · **Dauer:** 106.3 s

```
Deine Empfehlung · AI Start Map
AI
AI START MAP
Erzählen ✓ Verstehen ✓ Ergebnis ●
DEINE AUSWERTUNG · Auftrag aufnehmen und eindeutig kennzeichnen
Telefonaufträge bleiben nur im Kopf
Anrufe oder kurze Absprachen vor Ort werden meist nur gemerkt, nicht gleich festgehalten. Es gibt keine eindeutliche Kennzeichnung, Entscheidungen und Preise stehen nirgends schriftlich, deshalb fehlen Material oder Informationen später.
SO LÄUFT ES HEUTE
So habe ich deinen heutigen Ablauf verstanden
1 Kunde meldet Auftrag telefonisch oder persönlich auf der Baustelle
2 Auftrag wird mündlich gemerkt; häufig kein Zettel vorhanden
3 Gegebenenfalls wird der Auftrag abends handschriftlich notiert, manchmal bleibt er ungeschrieben
4 Es wird keine Auftragsnummer vergeben; Kunden werden mit Namen und Straße bezeichnet
5 Wenn das Team losfährt, werden Absprachen mündlich im Auto weitergegeben
WO ARBEIT WEGFÄLLT
Hier lässt sich Arbeit aus deinem Ablauf nehmen
Größter Hebel
Eine Sammelstelle für alle eingehenden Aufträge
Wenn alle Aufträge an einer Stelle landen, lassen sie sich eindeutig benennen und nachverfolgen.
Danach
Kurznotiz direkt nach dem Anruf
Ein schneller Eintrag nach jedem Anruf verhindert, dass Absprachen im Kopf verloren gehen.
Später
Später: Übergabe an Planung und Dokumentation
Ist die Erfassung stabil, kann die Auftragskarte an Terminplanung und Abrechnung weitergegeben werden.
SO WÜRDE DEINE LÖSUNG AUSSEHEN
Aus einem Anruf wird eine Auftragskarte
Was reinkommt
Telefon, persönlich vor Ort
Was die KI macht
Aus einer kurzen Sprachnachricht wird Text. Sie liest heraus: Kundenname, Adresse, was gemacht werden soll, gewünschten Zeitpunkt und ob nach einem Preis gefragt wurde. Sie hängt vorhandene Fotos an die richtige Karte, erkennt gleiche Kunden und markiert, welche Angaben noch fehlen. Sie fasst die Anfrage in zwei Zeilen und bereitet eine passende Rückfrage vor.
Was du machst
Du prüfst und bestätigst Preis, Leistungsumfang und Termin. Du entscheidest, ob der Auftrag angenommen wird und gibst die Kennzeichnung frei. Du ergänzt fehlende Angaben und gibst die Karte an deinen Bruder frei.
Was dabei rauskommt
Eine Auftragskarte mit Status, offenen Angaben und einem Antwortentwurf
Heute und nach der Einrichtung
So läuft es heute
Kunde ruft an oder spricht dich auf der Baustelle an.
Du merkst dir den Auftrag im Kopf, oft ohne Zettel.
Manchmal notierst du abends handschriftlich, manchmal nicht.
Es gibt keine Nummer; Kunden werden mit Namen und Straße genannt.
Bruder und du geben Absprachen mündlich im Auto weiter.
Nach der Einrichtung
Du leitest den Anruf kurz an die Sammelstelle weiter oder nimmst eine kurze Notiz auf.
Für jede Anfrage entsteht sofort eine Auftragskarte mit Namen und Adresse.
Die KI liest aus der Notiz die Kernangaben und zeigt fehlende Informationen an.
Du prüfst Preis und Umfang, bestätigst die Karte und vergibst eine eindeutige Kennzeichnung.
Dein Bruder sieht die bestätigte Karte vor Arbeitsbeginn und nimmt die Aufgaben mit.
DEIN KONKRETES ERGEBNIS
Was aus einem Anruf wird
Beispielangaben zur Veranschaulichung – hier stehen später deine tatsächlichen Angaben.
Telefon · Kundennachricht
Hallo, hier Frau Schneider, Bahnhofstraße 12. Wohnzimmer streichen, am liebsten nächste Woche. Was würde das kosten ungefähr?
Vorbereitet für dich
Kannst du mir bitte die Telefonnummer, die Größe des Zimmers in m² und die gewünschte Farbe nennen?
Die Antwort wird dem Vorgang zugeordnet — abgeschickt wird sie erst, wenn du sie freigibst.
So kommt es heute bei dir an — Telefon Hallo, hier Frau Schneider, Bahnhofstraße 12. Wohnzimmer streichen, am liebsten nächste Woche. Was würde das kosten ungefähr?
WAS DU DAFÜR BRAUCHST
Das behältst du, das kommt dazu
Das bleibt
Telefon
mündliche Notizen
gelegentliches handschriftliches Notizbuch
Das kommt dazu
eine einfache Seite, auf der neue Anfragen als Auftragskarten untereinander stehen
Dein Smartphone reicht. Die Auftragsliste öffnest du im normalen Internet-Browser und legst die Seite als Verknüpfung auf den Startbildschirm ab.
Das müsstest du besorgen
die Regel, nach jedem Auftrag kurz eine Notiz aufzunehmen oder den Anruf an die Sammelstelle weiterzuleiten
WAS ICH DAFÜR EINRICHTE
Das würde ich für dich bauen oder verbinden
Das ist eine Diagnose und ein Lösungskonzept. Angelegt ist noch nichts.
Ich richte eine einfache Auftragskarten-Seite ein, auf der jede Anfrage untereinander erscheint.
Ich passe an, welche Angaben die KI aus einer Notiz herauslesen soll und wie fehlende Angaben markiert werden.
Ich verbinde die Anzeige so, dass bestätigte Karten direkt für euch sichtbar sind.
Ich prüfe und korrigiere die Erkennung an echten Anrufen von euch.
Ich stelle einen kurzen Ablauf bereit, wie ihr Anrufe oder Notizen dorthin übertragt.
Ich starte mit einer einwöchigen Probe: Ich richte die Seite ein und teste sie an euren realen Fällen; ich passe an, welche Angaben erkannt werden.
DEINE SICHERHEIT
Das bleibt bei dir
Du entscheidest über Annahme, Preis, Termine und ob ein Auftrag ausgeführt wird. Du prüfst die vorgeschlagenen Angaben und ergänzt ggf. fehlende Informationen.
EHRLICH GESAGT
Eine Grenze
Telefonate oder Absprachen, die nie aufgezeichnet oder notiert wurden, kann niemand hinterher korrekt rekonstruieren. Fehlende Fakten musst du bestätigen.
Einen anderen Ablauf ansehen
GEMEINSAM UMSETZEN
Möchtest du das umsetzen?
Ich bin Derya. Genau das würde ich für dich einrichten: Aus einem Anruf wird eine Auftragskarte. Du schickst weiter wie bisher, ich baue den Rest.
PDF speichern Umsetzung besprechen
Im Druckdialog bitte „Kopf- und Fußzeilen“ abwählen.
Ich prüfe deine Angaben.
Du musst nichts weiter tun. Gleich geht es automatisch weiter.
```
