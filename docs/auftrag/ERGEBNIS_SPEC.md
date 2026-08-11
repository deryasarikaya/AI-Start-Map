# Ergebnisobjekt und Ergebnisseite — verbindliche Vorlage

**Diese Datei ersetzt den Schema-Teil von `ANWEISUNG_ENDANALYSE.md`.** Der
Prompt-Wortlaut in `EXPERIMENT_FREIER_PROMPT.md` bleibt Grundlage, wird aber um
die hier beschriebenen Abschnitte erweitert.

---

## Der Denkfehler, der behoben wird

Das bisherige Ergebnisobjekt hat flache Textfelder — `engpass`, `vorschlag`,
`das_nimmt_die_ki_ab`. Damit lässt sich nur ein einziger Ergebnistyp
darstellen, und jeder Fall wird in dieselbe Form gepresst.

Tatsächlich braucht ein Hausmeister eine Einsatznotiz, ein Coach eine
Terminvorbereitung, ein Laden eine Bestellübersicht, jemand mit vielen Anrufen
einen Telefonassistenten — und mancher überhaupt keine sichtbare Oberfläche,
weil die Automatisierung im Hintergrund läuft.

**Das Ausgabeformat entsteht aus dem Fall, nicht aus dem Template.**

Zweiter Punkt: Die Auswertung ist eine **Diagnose plus Lösungskonzept**. Der
Kunde hat danach kein laufendes System. Das muss auf der Seite unmissverständlich
sein, sonst verspricht sie etwas, das nicht existiert.

---

## Das neue Ergebnisobjekt

Alle Feldnamen deutsch, passend zum restlichen Kundenmodell.

```
engpass_titel            str   Überschrift, trägt selbst Inhalt (siehe unten)
engpass_text             str   2–3 Sätze

moeglichkeiten           list  1–3 Einträge, absteigend nach Hebel
  rang                   str   "groesster_hebel" | "danach" | "spaeter"
  titel                  str
  begruendung            str   ein Satz

loesung
  titel                  str   Überschrift, trägt Inhalt
  ablauf_heute           list  3–6 kurze Schritte, wie es heute läuft
  ablauf_kuenftig        list  3–6 kurze Schritte, wie es danach läuft
  was_reinkommt          str   Kanäle und Quellen, unverändert benannt
  was_die_ki_macht       str   konkrete Handgriffe, keine Abstraktion
  was_du_machst          str   Prüfen, Freigeben, Entscheiden
  was_dabei_rauskommt    str   das konkrete Arbeitsergebnis
  ergebnis_art           str   frei: "Bestellkarte", "Einsatznotiz",
                               "Rechnungsentwurf", "Antwortentwurf",
                               "Freigabestand", "Kundenakte",
                               "Telefonprotokoll", "Terminübersicht",
                               "Aufgabenliste", "CRM-Eintrag",
                               "kein sichtbares Ergebnis" …

beispiel                 optional, aber im Regelfall gesetzt
  titel                  str   z.B. "Was aus einer WhatsApp-Nachricht wird"
  kanal                  str
  nachricht              str   erfundene, realistische Eingangsnachricht
  daraus_wird            list  {label, wert}
  fehlt                  list  0–3
  rueckfrage             str   vorbereitete Rückfrage

voraussetzungen
  vorhandene_werkzeuge   list  was bleibt und unverändert weiter genutzt wird
  neu_hinzukommend       list  was tatsächlich dazukommt, leer wenn nichts
  geraete_und_zugang     str   welche Geräte reichen und wie die Lösung
                               erreichbar ist — konkret beantwortet, nicht
                               als pauschale Zusicherung
  musst_du_besorgen      list  0–3, mit Begründung warum es beim Kunden liegt

umsetzung
  hinweis                str   dass dies eine Diagnose ist, noch nichts gebaut
  einrichtungsschritte   list  3–5, was Derya tut
  erster_schritt         str   ein Absatz: womit die Umsetzung beginnt,
                               wie lange die Probe läuft, woran man Erfolg sieht

bleibt_bei_dir           str   1–2 Sätze
grenzen                  optional str  ehrliche Einschränkung, wenn es eine gibt
spaeter                  optional list  max 3
```

`moeglichkeiten` ist neu und wichtig: Die Auswertung zeigt damit, dass mehrere
Stellen erkannt wurden und eine bewusst ausgewählt ist. Das war bisher
unsichtbar.

---

## Reihenfolge der Ergebnisseite

Feste Reihenfolge, optionale Abschnitte entfallen, wenn ihr Feld leer ist.

| # | Abschnitt | Quelle | Pflicht |
|---|---|---|---|
| 1 | Überschrift + Engpass | `engpass_titel`, `engpass_text` | ja |
| 2 | So läuft es heute | `as_is_steps` (bestehend, max 5) | ja |
| 3 | Hier lässt sich Arbeit aus deinem Ablauf nehmen | `moeglichkeiten` | ja |
| 4 | So würde deine Lösung aussehen | `loesung` | ja |
| 4b | Heute / Nach der Einrichtung | `ablauf_heute`, `ablauf_kuenftig` | ja |
| 5 | Beispiel | `beispiel` | wenn gesetzt |
| 6 | Was du dafür brauchst | `voraussetzungen` | ja |
| 7 | Was ich dafür einrichte | `umsetzung` | ja |
| 8 | Was bei dir bleibt | `bleibt_bei_dir` | ja |
| 9 | Eine Grenze | `grenzen` | wenn gesetzt |
| 10 | Kontakt | fest | ja |

`spaeter` erscheint nicht als eigener Block, sondern ist bereits in
`moeglichkeiten` mit Rang „spaeter" abgedeckt. Doppelt zeigen ist verboten.

---

## Überschriften tragen Inhalt

Das ist die auffälligste Änderung. Überschriften sind heute Etiketten, die sich
selbst ankündigen. Ab jetzt kommen `engpass_titel` und `loesung.titel` aus dem
Modell und sind für diesen einen Fall geschrieben.

| verboten | erwartet |
|---|---|
| Das ist der Engpass | Du bist die Suchmaschine deines eigenen Ladens |
| Das schlage ich dir vor | Ein Eingang für alles, was reinkommt |
| Das nimmt dir die KI ab | Was aus einer WhatsApp-Nachricht wird |

Regel für den Prompt:

```
Die Überschriften "engpass_titel", "loesung.titel" und "beispiel.titel"
schreibst du für diesen einen Betrieb. Sie enthalten seine Gegenstände, seine
Kanäle, seine Arbeit.

Eine Überschrift, die auf jeden anderen Betrieb genauso passen würde, ist
falsch. Kündige nie einen Abschnitt an, sondern sag etwas.

Höchstens acht Wörter. Kein Doppelpunkt, kein Fragezeichen.
```

Die übrigen Abschnittsüberschriften bleiben fest im Template.

---

## Regeln für `was_die_ki_macht`

Der häufigste Fehler bisher: „liest Nachrichten, extrahiert relevante Angaben
und markiert Unsicherheiten." Das erklärt niemandem etwas.

```
Beschreibe, was die KI mit SEINEN Gegenständen tut. Nenne die Angaben beim
Namen, die in seinem Gewerbe vorkommen.

Falsch:  extrahiert relevante Felder aus eingehenden Nachrichten
Richtig: liest heraus, wann der Strauß fertig sein soll, für wen er ist,
         welche Farben gewünscht sind, wohin er geliefert wird und was auf
         die Karte soll

Nutze die Fähigkeiten aus `ai_capabilities` des gewählten Musters als
Wortschatz. Übersetze sie, schreib sie nicht ab. Lass weg, was auf diesen
Betrieb nicht zutrifft.
```

---

## Regeln für `voraussetzungen`

Der Kunde fragt sich: Was bleibt, was kommt dazu? Bekomme ich eine App?
Brauche ich ein neues Handy? Wo sehe ich das überhaupt?

Die Trennung zwischen **bleibt** und **kommt dazu** ist für ihn wichtiger als
jede technische Bezeichnung. Der Unterschied zwischen

> „WhatsApp und deine Buchhaltungssoftware bleiben. Dazu kommt eine kleine
> Automatisierung, die im Hintergrund läuft."

und

> „Du bekommst zusätzlich eine Oberfläche im Browser."

entscheidet, ob er sich das zutraut.

```
vorhandene_werkzeuge nennt namentlich, was er weiter benutzt — seine Kanäle,
seine Programme, seine Geräte. Alles, was bleibt, gehört hierher.

neu_hinzukommend nennt nur, was wirklich dazukommt. Wenn nichts dazukommt,
bleibt die Liste leer — und das ist ein starkes Ergebnis, kein Mangel.

geraete_und_zugang beantwortet konkret für diesen Fall: welche Geräte reichen,
und worüber die Lösung erreichbar ist.

Beispiel: "Dein Smartphone und dein Laptop reichen. Die Bestellungen siehst du
über eine Seite im Browser, die du dir auf den Startbildschirm legen kannst."

Behaupte NICHT pauschal, dass nie eine App oder zusätzliche Software nötig
wäre. In manchen Fällen ist eine App oder ein bestimmtes Programm die richtige
Lösung. Sag, was in DIESEM Fall gilt.

Wenn keine eigene Oberfläche nötig ist, sag das ausdrücklich — wenn das
Ergebnis als Nachricht zurückkommt oder in vorhandener Software landet, ist
das meist die bessere Lösung.

musst_du_besorgen nur, wenn es wirklich etwas gibt, und immer mit Begründung,
warum es beim Kunden liegt und nicht bei Derya.
```

---

## Regeln für `umsetzung`

Die Auswertung darf nicht so klingen, als könne der Kunde nächste Woche selbst
loslegen.

```
hinweis macht klar: Dies ist die Diagnose. Gebaut ist noch nichts.

einrichtungsschritte sind DERYAS Arbeit, in der Ich-Form: "Ich verbinde…",
"Ich richte ein…", "Ich prüfe an deinen echten Fällen…"

erster_schritt beschreibt den ersten Umsetzungsschritt NACH einer Beauftragung.
Nicht "Probier es nächste Woche aus". Sondern: womit angefangen würde, wie
lange die Probe läuft, woran der Betrieb merkt, dass es funktioniert.

Sag außerdem, dass nicht alles neu gebaut wird: Wo bereits gute Software
existiert, wird sie eingebunden. Wo eine kleine eigene Lösung sinnvoll ist,
wird sie gebaut. Das ist ehrlicher und für einen kleinen Betrieb beruhigender
als ein Rundum-Neubau.
```

---

## Zugekaufte Werkzeuge sind Lösungen, keine Einschränkungen

Bisher wurde alles als Eigenbau dargestellt, und was nicht selbst baubar war,
landete unter „Grenzen". Das ist falsch herum.

**Beispiel Telefon.** Ein Anruf, bei dem nichts festgehalten wird, ist kein
Grund zu sagen „hier hilft KI nicht". Es gibt zwei echte Wege:

```
Variante 1 — bestehender Ablauf
Nach dem Telefonat sprichst du die wichtigsten Angaben kurz ein. Die KI macht
daraus denselben Vorgang wie aus einer Nachricht.

Variante 2 — Telefonassistent
Ein externer KI-Telefonassistent nimmt Anrufe an, fragt die wichtigsten
Angaben ab und legt den Vorgang selbst an.
```

Beides gehört in `moeglichkeiten` oder in die `loesung` — **nicht** in
`grenzen`. Unter `grenzen` steht nur, was tatsächlich niemand lösen kann.

```
Wenn ein fertiges Werkzeug die bessere Lösung ist, nenn es als Möglichkeit,
mit grober Größenordnung und dem Hinweis, dass es zugekauft und von Derya
ausgewählt, eingerichtet und angebunden wird.

Deryas Aufgabe ist dann nicht, eine Telefonplattform zu entwickeln, sondern
einen passenden Dienst auszuwählen und mit dem restlichen Ablauf zu verbinden.
Das gehört so in den Text.

Keine Produktnamen. Keine exakten Preise. "So etwas kostet um die 30 Euro im
Monat" ist zulässig, "Anbieter X für 29 €" nicht.

Erfinde keine Kosten für Werkzeuge, bei denen du keine Größenordnung kennst.
```

---

## Das Beispiel zeigt genau das, was der Kunde bekommt

`beispiel` ist keine feste Kartenform. Es ist eine Instanz von `ergebnis_art`.

```
Was du im Beispiel zeigst, muss dasselbe sein, was in
loesung.was_dabei_rauskommt steht.

Ist ergebnis_art ein Rechnungsentwurf, zeigt das Beispiel einen
Rechnungsentwurf. Ist es ein Freigabestand, zeigt es einen Freigabestand. Ist
es ein Telefonprotokoll, zeigt es Anrufer, Anliegen, Dringlichkeit, was fehlt
und den nächsten Schritt.

Wenn ergebnis_art "kein sichtbares Ergebnis" lautet, zeigt das Beispiel, was
stattdessen im Hintergrund passiert und wo der Betrieb es merkt — dann entfällt
die Feldliste.
```

---

## Warum feste Reihenfolge statt freier Abschnittsliste

Eine frei erzeugte `sections`-Liste wäre flexibler, aber das Modell würde
Reihenfolge, Anzahl und Benennung pro Lauf variieren — nicht prüfbar, nicht
gestaltbar, nicht vergleichbar.

Die Flexibilität liegt deshalb an den drei Stellen, an denen sie zählt:
**generierte Überschriften**, **freies `ergebnis_art`**, **optionale
Abschnitte, die entfallen wenn leer**. Reihenfolge und Zweck der Abschnitte
bleiben fest.

---

## Die Geschichte, die die Seite erzählt

Zur Kontrolle beim Lesen — so muss sich die fertige Seite lesen lassen:

> So arbeitest du heute. → Hier entsteht unnötige Arbeit. → An diesen Stellen
> lässt sich Arbeit rausnehmen, und diese eine lohnt sich zuerst. → So würde
> der Ablauf danach funktionieren. → Das würdest du tatsächlich bekommen. →
> Das behältst du, das kommt dazu. → Das würde ich für dich einrichten oder
> verbinden. → Das entscheidest weiterhin du.

Erst danach der Kontakt.

Die späteren Erweiterungen erscheinen **nicht** als eigene Station — sie sind
in `moeglichkeiten` mit Rang „spaeter" bereits gesagt. Zweimal zeigen ist ein
Fehler.

---

## Abnahmebedingungen

Alle drei Fälle aus `TESTFAELLE_ZIELGRUPPE.md` (Blumenladen, Fotograf,
Handwerksbetrieb) müssen durchlaufen und erfüllen:

- `engpass_titel` und `loesung.titel` enthalten mindestens einen Gegenstand
  oder Kanal aus der Erzählung des Betriebs
- keine der drei Überschriften würde unverändert auf einen der anderen beiden
  Fälle passen
- `moeglichkeiten` hat mindestens zwei Einträge mit verschiedenen Rängen
- `was_die_ki_macht` nennt mindestens drei Angaben, die in diesem Gewerbe
  tatsächlich vorkommen
- `voraussetzungen.geraete_und_zugang` ist gesetzt, nennt konkrete Geräte und
  sagt, worüber die Lösung erreichbar ist — keine pauschale Zusicherung
- `vorhandene_werkzeuge` und `neu_hinzukommend` überschneiden sich nicht; was
  in beiden Listen stünde, ist ein Fehler
- `moeglichkeiten` erfindet keinen dritten Eintrag, wenn nur zwei tragen
- `umsetzung.einrichtungsschritte` stehen in der Ich-Form
- `umsetzung.erster_schritt` enthält nicht die Formulierung „probier",
  „teste ab morgen", „fang nächste Woche an" oder Ähnliches, das den Kunden
  zum Umsetzer macht
- `ergebnis_art` unterscheidet sich zwischen den drei Fällen
- das Beispiel zeigt genau das, was in `ergebnis_art` steht — keine
  Bestellkarte bei einem Rechnungsentwurf
- `ablauf_heute` und `ablauf_kuenftig` unterscheiden sich erkennbar und
  beschreiben denselben Vorgang
- wenn im Fall Telefon vorkommt: es steht in `moeglichkeiten` oder `loesung`,
  nicht in `grenzen`
- durchgehend Anrede „du", nie „der Betrieb", „die Inhaberin", „der Fotograf"
- keines der verbotenen Fachwörter aus `EXPERIMENT_FREIER_PROMPT.md`
- keine Zahl, die nicht aus der Erzählung oder der erfundenen Beispielnachricht
  folgt — Ausnahme: grobe Größenordnung für ein zugekauftes Werkzeug

Wenn eine Bedingung nicht erfüllt ist: melden, nicht als fertig ausgeben.

---

## Was das PDF bekommt

Dieselbe Reihenfolge, derselbe Inhalt. Der heutige Ablauf gehört auch ins PDF.
Der Druckhinweis erscheint nur auf der Seite, nie im Dokument.
