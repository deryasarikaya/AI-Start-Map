# Stand nach dem Ausbau

Alle drei Fälle aus `TESTFAELLE_ZIELGRUPPE.md`, komplett durch die echte App.
Vergleichsstand: `lauf_vorher.md`.

## Übersicht

| Fall | ergebnis_art | reifestufe | darstellung | Dauer | Autonomie |
|---|---|---|---|---|---|
| Blumenladen | Anfragekarte | genai | nachricht | 106.5 s | A1 |
| Fotograf | Briefing-Karte | genai | nachricht | 118.2 s | A1 |
| Handwerksbetrieb | Einsatznotiz | genai | karte | 89.3 s | A1 |

## Überschriften

| Fall | engpass_titel | loesung.titel |
|---|---|---|
| Blumenladen | Du arbeitest zweimal für Bestellungen | Eine Anfragekarte für jede Blumenbestellung |
| Fotograf | Du bist die Suchmaschine deiner Shootings | Ein Eingang, der Briefings fertigstellt |
| Handwerksbetrieb | Wichtiges taucht erst bei der Rechnung auf | Einsatznotiz aus Sprachnachricht, Foto und Bon |

## Fallübergreifende Abnahmebedingungen

| Bedingung | Ergebnis |
|---|---|
| `ergebnis_art` unterscheidet sich zwischen den drei Fällen | erfüllt — Anfragekarte, Briefing-Karte, Einsatznotiz |
| `beispiel.darstellung` ist nicht bei allen drei gleich | erfüllt — nachricht, nachricht, karte |
| `reifestufe` ist nicht bei allen drei dieselbe | NICHT erfüllt — genai, genai, genai |
| Keine Überschrift passt unverändert auf einen anderen Fall | teilweise, siehe unten |

**Nicht erfüllt: `reifestufe` ist in allen drei Fällen `genai`.** Alle drei
Erzählungen drehen sich darum, dass etwas Unstrukturiertes verstanden werden
muss — freie Nachrichten, Sprachnachrichten, Fotos, Bons. Für diese drei Fälle
ist `genai` jeweils die kleinste Stufe, die den Engpass löst. Die Stufe
unterscheidet also korrekt, nur decken die drei Testfälle die unteren Sprossen
nicht ab. Ein Fall, der auf `ordnung` oder `digitalisierung` landen müsste,
fehlt in `TESTFAELLE_ZIELGRUPPE.md`.

**Teilweise: die Überschrift des Handwerksfalls.** „Wichtiges taucht erst bei
der Rechnung auf" trägt keinen Gegenstand und keinen Kanal aus seiner
Erzählung und würde so auch auf den Fotografen passen, der ebenfalls von der
Rechnung erzählt. Die anderen fünf Überschriften sind fallgebunden.

---

## Blumenladen — gerenderte Ergebnisseite

**ergebnis_art:** Anfragekarte · **reifestufe:** genai · **darstellung:** nachricht · **Dauer:** 106.5 s

```
Deine Empfehlung · AI Start Map
AI
AI START MAP
Erzählen ✓ Verstehen ✓ Ergebnis ●
DEINE AUSWERTUNG · Kundenbestellung erfassen und bestätigen
Du arbeitest zweimal für Bestellungen
Bestellungen und Fotos landen in Chats, Galerie und auf Zetteln. Telefonische Bestellungen werden oft gar nicht festgehalten, sodass du beim Fertigen oder Liefern noch einmal alles zusammensuchen oder nachfragen musst.
SO LÄUFT ES HEUTE
So habe ich deinen heutigen Ablauf verstanden
1 Bestellung kommt ein (WhatsApp, Instagram, E‑Mail, Anruf oder Onlineshop).
2 Zwischennotizen handschriftlich oder im Kopf.
3 Informationen verteilt in Chats, Galerie, Zettel.
4 Beim Fertigen/Liefern wird gesucht und nachgefragt.
5 Telefonbestellungen bleiben oft unvollständig.
WO ARBEIT WEGFÄLLT
Hier lässt sich Arbeit aus deinem Ablauf nehmen
Größter Hebel
Eine Sammelstelle für alle Bestellungen
Wenn alle eingehenden Nachrichten an einer Stelle landen, lässt sich die Nacharbeit stark verringern.
Danach
Ein kurzes Erfassungsfeld für Telefonate
Ein kleiner Handgriff nach jedem Anruf verhindert, dass Informationen fehlen.
SO WÜRDE DEINE LÖSUNG AUSSEHEN
Eine Anfragekarte für jede Blumenbestellung
Was reinkommt
WhatsApp, Instagram, E‑Mail, Anruf, Onlineshop
Was die KI macht
Sie liest heraus, wann die Lieferung/Abholung sein soll, für wen die Blumen sind, welche Farben und welcher Stil gewünscht sind, ob eine Karte gewünscht wird, wohin geliefert werden soll und ob ein Referenzfoto dabei ist; aus einer Sprachnachricht wird Text; sie hängt angehängte Fotos an die richtige Anfrage; sie erkennt, ob es ein bestehender Kunde ist; sie fasst mehrere Nachrichten zur selben Bestellung zusammen; sie markiert, welche Angaben noch fehlen und bereitet eine kurze Rückfrage sowie einen zweiseitigen Zusammenfassungs- oder Antwortentwurf vor.
Was du machst
Du entscheidest, ob die Bestellung angenommen wird, bestätigst Preis und Lieferzeit, prüfst Verfügbarkeit und Zahlungsweise und gibst die endgültige Bestätigung frei.
Was dabei rauskommt
Eine Anfragekarte mit Status, offenen Angaben und Antwortentwurf.
Heute und nach der Einrichtung
So läuft es heute
Bestellung kommt per WhatsApp, Instagram, E‑Mail, Anruf oder Onlineshop rein.
Du schreibst dir Dinge auf einen Zettel oder merkst sie dir.
Fotos, Adressen und Sonderwünsche liegen in verschiedenen Chats/Galerie/Zettel.
Beim Vorbereiten suchst du in mehreren Quellen nach der richtigen Information.
Bei unklaren Telefonbestellungen rufst du den Kunden nochmal an.
Nach der Einrichtung
Alle eingehenden Nachrichten laufen in eine Sammelstelle zusammen.
Die KI liest Nachrichten, aus der Sprachnachricht wird Text und sie liest heraus: Besteller, Empfänger, Adresse, Lieferdatum/-zeit, Farb- und Stilangaben, Grußtext und gewünschte/ü
Die KI hängt mitgeschickte Fotos zur richtigen Anfrage, erkennt Stammkunden und fasst mehrere Nachrichten zur gleichen Bestellung zusammen.
Fehlende Angaben werden markiert und die KI bereitet eine kurze Rückfrage vor.
Du prüfst Dringlichkeit, Preis und Verfügbarkeit, gibst die Bestellung frei und verschickst die Bestätigung; die Anfrage erhält Status und eine Aufgabe zur Vorbereitung.
DEIN KONKRETES ERGEBNIS
Was aus einer WhatsApp-Nachricht wird
Beispielangaben zur Veranschaulichung – hier stehen später deine tatsächlichen Angaben.
WhatsApp · Kundennachricht
Hi, braucht meine Mama was zum Geburtstag, rosa-weiß bitte, so wie ihr das letztens gemacht habt. Morgen wäre super. Könnt ihr liefern? Danke, Anna
Vorbereitet für dich
Lieferadresse? Telefonnummer? Welche Uhrzeit morgen passt?
Die Antwort wird dem Vorgang zugeordnet — abgeschickt wird sie erst, wenn du sie freigibst.
So kommt es heute bei dir an — WhatsApp Hi, braucht meine Mama was zum Geburtstag, rosa-weiß bitte, so wie ihr das letztens gemacht habt. Morgen wäre super. Könnt ihr liefern? Danke, Anna
WAS DU DAFÜR BRAUCHST
Das behältst du, das kommt dazu
Das bleibt
WhatsApp
Instagram
E‑Mail
Telefon/Anrufe
Onlineshop
Galerie und Zettel am Laden
Das kommt dazu
eine Sammelstelle, an die eure Nachrichten weitergeleitet werden
ein kurzes Formular zum Erfassen der wichtigsten Angaben (Name, Telefonnummer, Adresse, Lieferdatum/-zeit, Zahlungsart)
die Einrichtung, die eingehende Nachrichten liest und offene Angaben markiert
Dein Smartphone und ein Laptop reichen. Die Sammelstelle ist als Seite erreichbar, die du auf dem Startbildschirm ablegen kannst; ihr greift alle über dieselbe Seite darauf zu.
Das müsstest du besorgen
Wenn WhatsApp/Instagram aktuell auf privaten Handys liegen: weiterleiten der Bestellungen an die Sammelstelle oder Zugang zu einem gemeinsamen Konto
eine kurze Regel: nach jedem telefonischen Auftrag kurz die wichtigsten Angaben in die Sammelstelle notieren
WAS ICH DAFÜR EINRICHTE
Das würde ich für dich bauen oder verbinden
Dies ist die Diagnose. Gebaut ist noch nichts.
Ich richte die Sammelstelle ein und verbinde die vorhandenen Kanäle so weit möglich, dass Nachrichten dorthin laufen.
Ich erstelle das kurze Formular mit den Angaben, die nicht fehlen dürfen.
Ich trainiere und stelle die KI so ein, dass sie Nachrichten liest, Fotos zuordnet, Stammkunden erkennt und fehlende Angaben markiert.
Ich teste das System an echten Bestellungen und passe die Rückfrageformulierungen an eure Sprache an.
Ich richte die Ausgabe als Anfragekarte mit Status, offenen Angaben und Antwortentwurf ein.
Nach Auftrag richte ich in einer Woche eine zweiwöchige Probephase ein, in der echte Nachrichten in die Sammelstelle laufen; ich prüfe an euren Fällen, ob die KI die Angaben korrekt herausliest und ihr bekommt täglich die Liste offener Angaben, an der ihr merkt, ob es funktioniert.
DEINE SICHERHEIT
Das bleibt bei dir
Du entscheidest über Annahme, Preis, Freigabe von Lieferzeiten und Zahlungsart. Du prüfst und verschickst die finale Bestätigung an den Kunden.
EHRLICH GESAGT
Eine Grenze
Wenn bei einem telefonischen Auftrag hinterher gar nichts notiert wurde, kann die KI fehlende Angaben nicht ergänzen; eine kurze Nachfrage bleibt nötig.
Einen anderen Ablauf ansehen
GEMEINSAM UMSETZEN
Möchtest du das umsetzen?
Ich bin Derya. Genau das würde ich für dich einrichten: Eine Anfragekarte für jede Blumenbestellung. Du schickst weiter wie bisher, ich baue den Rest.
PDF speichern Umsetzung besprechen
Im Druckdialog bitte „Kopf- und Fußzeilen“ abwählen.
Ich prüfe deine Angaben.
Du musst nichts weiter tun. Gleich geht es automatisch weiter.
```

---

## Fotograf — gerenderte Ergebnisseite

**ergebnis_art:** Briefing-Karte · **reifestufe:** genai · **darstellung:** nachricht · **Dauer:** 118.2 s

```
Deine Empfehlung · AI Start Map
AI
AI START MAP
Erzählen ✓ Verstehen ✓ Ergebnis ●
DEINE AUSWERTUNG · Kundenbriefing vor dem Shooting zusammenführen
Du bist die Suchmaschine deiner Shootings
Informationen für ein Shooting kommen über Wochen verteilt in Instagram, die Website und E‑Mail an. Deshalb musst du jedes Mal Nachrichten zusammensuchen und weißt nicht sicher, welche Fassung gilt.
SO LÄUFT ES HEUTE
So habe ich deinen heutigen Ablauf verstanden
1 Eingehende Nachrichten sammeln: Der Fotograf liest Instagram, Website und E‑Mail.
2 Briefing erstellen: Der Fotograf schreibt aus den Nachrichten ein einzelnes Briefing zusammen.
3 Briefing vor dem Shooting prüfen: Kurz vor dem Termin ergänzt der Fotograf fehlende Details.
4 Shooting durchführen: Mit dem erstellten Briefing fährt der Fotograf zum Shooting.
WO ARBEIT WEGFÄLLT
Hier lässt sich Arbeit aus deinem Ablauf nehmen
Größter Hebel
Eine Sammelstelle für alle Anfragen
Sammelt alle Nachrichten an einer Stelle, so entfällt das manuelle Zusammensuchen.
Danach
KI fasst Nachrichten zusammen und zeigt Lücken
Die KI liest heraus Was, Wann, Wo, Wer und markiert, welche Angaben fehlen, damit du nur noch prüfen musst.
SO WÜRDE DEINE LÖSUNG AUSSEHEN
Ein Eingang, der Briefings fertigstellt
Was reinkommt
Instagram, Website, E‑Mail
Was die KI macht
Sie liest aus den Nachrichten heraus, um welche Art Shooting es geht, welche Stilwünsche oder Beispielbilder genannt werden, welchen Zeitraum oder welches Datum der Kunde nennt, wo das Shooting sein soll, wer teilnimmt und ob Preis/Leistung angesprochen wurden. Sie hängt erwähnte Fotos und Dateien an die passende Anfrage, erkennt, ob es ein bekannter Kunde ist, fasst mehrere Nachrichten zur selben Anfrage zusammen, markiert fehlende Angaben und erstellt einen kurzen Antwortentwurf.
Was du machst
Du prüfst die Angaben, entscheidest über Annahme, Termin, Preis und Sonderwünsche und gibst das Briefing frei.
Was dabei rauskommt
Eine Anfragekarte mit Status, offenen Angaben und Antwortentwurf.
Heute und nach der Einrichtung
So läuft es heute
Du liest Instagram, Website und E‑Mail einzeln durch.
Du kopierst relevante Sätze und Bilder per Hand in ein Briefing-Dokument.
Kurz vor dem Termin ergänzt du fehlende Details per Nachricht.
Mit dem zusammengeschriebenen Briefing fährst du zum Shooting.
Nach der Einrichtung
Alle eingehenden Anfragen landen in einer Sammelstelle.
Die KI fasst alle Nachrichten einer Anfrage zu einer Anfragekarte zusammen.
Die Karte zeigt herausgelesene Angaben und markiert fehlende Details.
Die Karte enthält einen Antwortentwurf; du prüfst, entscheidest und gibst das Briefing frei.
Nach Freigabe wird das Briefing als endgültig festgehalten und kann in deinen Kalender übertragen werden.
DEIN KONKRETES ERGEBNIS
Was aus einer Instagram-Nachricht wird
Beispielangaben zur Veranschaulichung – hier stehen später deine tatsächlichen Angaben.
Instagram · Kundennachricht
Hi, wir würden gern ein Familienshooting machen, Ende Juni wär super. Oma ist dabei. Schicke dir gleich ein paar Bilder. Wo können wir uns treffen? LG Anna
Vorbereitet für dich
Wann genau passt euch (Datum und Uhrzeit)? An welchem Treffpunkt/Adresse sollen wir uns treffen? Welche Paket/Leistung wollt ihr, oder soll ich ein Angebot schicken?
Die Antwort wird dem Vorgang zugeordnet — abgeschickt wird sie erst, wenn du sie freigibst.
So kommt es heute bei dir an — Instagram Hi, wir würden gern ein Familienshooting machen, Ende Juni wär super. Oma ist dabei. Schicke dir gleich ein paar Bilder. Wo können wir uns treffen? LG Anna
WAS DU DAFÜR BRAUCHST
Das behältst du, das kommt dazu
Das bleibt
Instagram
Website-Kontaktbereich
E‑Mail
Bildergalerie für die Auswahl
Das kommt dazu
Eine Sammelstelle, an die deine Nachrichten zusammenlaufen
Eine Seite, auf der für jede Anfrage eine Karte mit den offenen Angaben angezeigt wird
Eine KI, die Nachrichten zusammenfasst, Fotos zuordnet und fehlende Angaben anzeigt
Dein Smartphone und dein Laptop reichen. Die Anfragekarte siehst du über eine Seite, die du im Browser öffnest und auf dem Startbildschirm ablegen kannst.
Das müsstest du besorgen
Zugriff auf deine Instagram-Nachrichten oder die Bereitschaft, DMs kurz an die Sammelstelle weiterzuleiten
Bei der Galerie: die Möglichkeit, Kommentare oder Hinweise einzusehen, damit Änderungswünsche zugeordnet werden können
WAS ICH DAFÜR EINRICHTE
Das würde ich für dich bauen oder verbinden
Dies ist die Diagnose. Gebaut ist noch nichts.
Ich richte die Sammelstelle ein und verbinde E‑Mail und deine Website-Eingaben mit ihr.
Ich stelle ein, wie Nachrichten zur richtigen Anfragekarte zusammengeführt werden und wie angehängte Fotos angeordnet werden.
Ich trainiere die KI an drei echten Fällen von dir und passe die Regeln für fehlende Angaben an.
Ich lege Antwortvorlagen und die Sichtprüfung so an, dass du schnell prüfen und freigeben kannst.
Ich teste die Lösung an deinen Fällen und passe sie mit dir an.
Ich sammle drei offene Anfragen von dir, richte die Sammelstelle und teste sie an diesen Fällen; gemeinsam prüfen wir, ob die Karten vollständige Briefings liefern.
DEINE SICHERHEIT
Das bleibt bei dir
Du entscheidest über Annahme, Termin, Preis und Sonderwünsche. Du gibst jede finale Fassung und jede Abschlags-/Rechnungsangabe frei.
Einen anderen Ablauf ansehen
GEMEINSAM UMSETZEN
Möchtest du das umsetzen?
Ich bin Derya. Genau das würde ich für dich einrichten: Ein Eingang, der Briefings fertigstellt. Du schickst weiter wie bisher, ich baue den Rest.
PDF speichern Umsetzung besprechen
Im Druckdialog bitte „Kopf- und Fußzeilen“ abwählen.
Ich prüfe deine Angaben.
Du musst nichts weiter tun. Gleich geht es automatisch weiter.
```

---

## Handwerksbetrieb — gerenderte Ergebnisseite

**ergebnis_art:** Einsatznotiz · **reifestufe:** genai · **darstellung:** karte · **Dauer:** 89.3 s

```
Deine Empfehlung · AI Start Map
AI
AI START MAP
Erzählen ✓ Verstehen ✓ Ergebnis ●
DEINE AUSWERTUNG · Auftragsdokumentation vom Einsatz bis zur Rechnung
Wichtiges taucht erst bei der Rechnung auf
Deine Leute dokumentieren sehr unterschiedlich und Fotos sowie Bons bleiben auf den Handys. Am Monatsende setzt du alles zusammen und entdeckst Zusatzarbeiten oder fehlende Belege erst beim Rechnungslegen.
SO LÄUFT ES HEUTE
So habe ich deinen heutigen Ablauf verstanden
1 Techniker dokumentiert vor Ort handschriftlich unterschiedlich vollständig
2 Fotos bleiben auf den Handys
3 Materialbons werden gesammelt und später übergeben
4 Geschäftsführung setzt alles zusammen und erstellt Rechnungen
WO ARBEIT WEGFÄLLT
Hier lässt sich Arbeit aus deinem Ablauf nehmen
Größter Hebel
Sammelstelle für jede Einsatzmeldung
Wenn jede Nachmeldung sofort an einem Ort landet, ist das Zusammensetzen später erledigbar.
Danach
Automatisches Lesen von Sprachnachrichten und Bons
Aus Sprache, Foto und Bon werden die Fakten herausgelesen und vorgefüllt, so dass du weniger nachfragen musst.
Später
Teamregel und kurzes Training
Klare Regel, wie kurz nach Einsatz gemeldet wird, reduziert fehlende Angaben langfristig.
SO WÜRDE DEINE LÖSUNG AUSSEHEN
Einsatznotiz aus Sprachnachricht, Foto und Bon
Was reinkommt
Telefon, E‑Mail, WhatsApp
Was die KI macht
aus der Sprachnachricht wird Text; liest den Bon: Lieferant, Datum, Betrag, Positionen; erkennt Tätigkeit, geschätzte Dauer, verwendetes Material und zusätzlich ausgeführte Arbeiten; ordnet Fotos dem Einsatz zu; markiert unsichere oder fehlende Angaben; erstellt die Einsatznotiz als Entwurf.
Was du machst
Du prüfst Zuordnung, Zeiten, Materialmengen, Zusatzarbeiten und Belegbeträge; du entscheidest Preise und gibst die Notiz frei für die Rechnung.
Was dabei rauskommt
Eine prüfbare Einsatznotiz mit Anhängen und offenen Angaben.
Heute und nach der Einrichtung
So läuft es heute
Techniker macht handschriftliche Notiz, Fotos und kauft Material; alles bleibt verstreut auf Handys.
Geschäftsführung sammelt am Monatsende Notizen, Fotos und Bons zusammen.
Aus den verstreuten Angaben wird die Rechnung manuell erstellt; Zusatzarbeiten fallen oft erst jetzt auf.
Nach der Einrichtung
Nach dem Einsatz schickt der Techniker eine kurze Sprachnachricht, Fotos und ein Foto des Bons an die Sammelstelle.
Ein KI-Dienst macht aus der Sprachnachricht Text, liest den Bon (Lieferant, Datum, Betrag, Positionen) und ordnet die Fotos zu.
Die KI markiert unsichere oder fehlende Angaben und erzeugt eine Entwurf-Einsatznotiz mit Anhängen.
Du prüfst die Notiz, bestätigst Zeit, Material und Zusatzarbeit; nach Bestätigung bereitet das System einen Rechnungsentwurf vor.
DEIN KONKRETES ERGEBNIS
Was aus einer WhatsApp-Sprachnachricht wird
Beispielangaben zur Veranschaulichung – hier stehen später deine tatsächlichen Angaben.
Einsatznotiz
zu prüfen
Kunde
Hausverwaltung Müller
Ort
Lindenstr. 12, Wohnung 3B
Tätigkeit
Lampenwechsel Flur 3. OG
Dauer
etwa 30 min
Material
2x LED
Anhänge
Foto, Bon
Fehlt noch: genaue Start- und Endzeit · Einzelpreise der gekauften Teile · Ob Zusatzarbeit vorher freigegeben war
geht erst nach deiner Freigabe raus
Vorbereitete Rückfrage: „Wann genau hast du angefangen/aufgehört? Was hat die LED pro Stück gekostet? Wurde die Zusatzarbeit schriftlich freigegeben?“
So kommt es heute bei dir an — WhatsApp Alles fertig. Lampenwechsel Flur 3. OG, war etwa 30 min. 2x LED eingebaut. Foto vom Altlicht und neue Lampe anbei. Bon vom Baumarkt häng ich an. Kunde: Hausverwaltung Müller, Lindenstr. 12, Wohnung 3B. Sag Bescheid wg. Rechnung.
WAS DU DAFÜR BRAUCHST
Das behältst du, das kommt dazu
Das bleibt
Diensthandys der Mitarbeitenden
gemeinsamer Kalender
Rechnungssoftware
WhatsApp
E‑Mail
Telefon
Das kommt dazu
eine Sammelstelle, an die Einsatzmeldungen geschickt werden (eine Seite, auf der die Meldungen untereinander stehen)
ein KI-Dienst, der aus Sprachnachrichten Text macht und Bons liest sowie Fotos dem Einsatz zuordnet
Dein Diensthandy und dein Laptop reichen. Die Einsatznotizen siehst du über eine Seite im Browser, die du auf dem Startbildschirm ablegen kannst.
Das müsstest du besorgen
kurze Vereinbarung mit den Technikern, dass sie sofort nach dem Einsatz Sprachnachricht, Fotos und Bon an die Sammelstelle senden
WAS ICH DAFÜR EINRICHTE
Das würde ich für dich bauen oder verbinden
Das ist die Diagnose und das Lösungskonzept. Gebaut ist noch nichts.
Ich richte die Sammelstelle als zentrale Seite ein und lege Versandregeln fest, wie Meldungen dort hinkommen.
Ich verbinde den KI-Dienst, der aus der Sprachnachricht Text macht, den Bon liest und Fotos zuordnet, und lasse ihn Entwurf-Einsatznotizen erzeugen.
Ich sorge dafür, dass die Entwürfe als prüfbare Einsatznotizen mit Anhängen sichtbar sind und eine Markierung für fehlende Angaben zeigen.
Ich teste die Lösung an echten Einsätzen und passe die Erkennungsregeln an, bis die Notizen brauchbar sind.
Ich stelle die Sammelstelle bereit und führe eine einwöchige Probe mit 5–10 Einsätzen durch; erfolgreich, wenn für diese Einsätze komplette Entwurf-Notizen mit Foto und Bon vorliegen.
DEINE SICHERHEIT
Das bleibt bei dir
Du entscheidest Preise, bestätigst Zusatzarbeiten und schickst die Rechnungen ab. Du sorgst dafür, dass die Techniker die Nachmeldung machen.
EHRLICH GESAGT
Eine Grenze
Wenn Techniker keine Nachricht, kein Foto oder keinen Bon schicken, kann das System fehlende Fakten nicht nachträglich rekonstruieren. Die KI liefert nur Entwürfe; du prüfst und verschickst Rechnungen.
Einen anderen Ablauf ansehen
GEMEINSAM UMSETZEN
Möchtest du das umsetzen?
Ich bin Derya. Genau das würde ich für dich einrichten: Einsatznotiz aus Sprachnachricht, Foto und Bon. Du schickst weiter wie bisher, ich baue den Rest.
PDF speichern Umsetzung besprechen
Im Druckdialog bitte „Kopf- und Fußzeilen“ abwählen.
Ich prüfe deine Angaben.
Du musst nichts weiter tun. Gleich geht es automatisch weiter.
```
