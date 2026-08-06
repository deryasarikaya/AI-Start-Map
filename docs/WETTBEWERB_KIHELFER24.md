# Wettbewerbsanalyse: kihelfer24

**Status:** Historical Market Review Snapshot – kein Beleg für den aktuellen Produktstand und keine Source of Truth für Implementierung oder Rechtslage. Der A0-Pfad ist weiterhin nur Katalogbestand und noch nicht in der Laufzeit integriert.

Stand: 2026-08-06
Grundlage: Landingpage, drei Produktseiten, eine automatisch erzeugte
Erstanalyse („Schühchen", 2026-07-28) und die zugehörige Akquise-E-Mail.

Einschränkung: Bewertet wird ausschließlich das öffentlich sichtbare Material
und eine einzelne automatisch erzeugte Analyse. Die tatsächlich gelieferte
Umsetzungsarbeit kann besser sein als das, was der automatisierte Vorprozess
zeigt.

---

## 1. Was kihelfer24 macht

**Positionierung:** „KI-Automatisierung für kleine Betriebe". Bild dazu: ein Rohr
mit drei Verstopfungen — Anfragen, Büro, Follow-up. Kernsatz: „Mehr Werbung
bringt nichts, wenn intern alles hängen bleibt."

**Drei Produkte:**

1. Angebots-Automatisierung — Anfrage rein, Angebotsentwurf raus, Freigabe per
   Telegram aufs Handy, danach automatischer Versand
2. KI-Telefonassistent — nimmt ab, legt das Anliegen strukturiert ins System
3. Rechnungen und Belege — fotografieren statt abtippen, Übergabe an Lexoffice,
   sevdesk, DATEV

**Funnel:** Chat auf der Landingpage („Schreiben Sie kurz, wo es bei Ihnen
klemmt — oder wählen Sie unten einen der fünf Engpässe") mit Texteingabe und
Mikrofon → einige kurze Fragen → Engpass-Audit als PDF per E-Mail →
20-Minuten-Gespräch → Festpreisangebot.

**Kommerziell:** 800 EUR einmalig, Werkvertrag, kein Abo, kein Lock-in, 12 Monate
Gewährleistung, das System gehört dem Kunden. Laufende Kosten werden offen
genannt: 25 bis 80 EUR pro Monat direkt an den KI-Anbieter, optional
Wartungspauschale ab 50 EUR.

---

## 2. Was sie gut machen — und was AI Start Map davon lernen sollte

**Der Funnel ist vollständig.** Von „ich habe von KI gehört" bis „hier ist ein
Festpreis" gibt es keine Lücke.

AI Start Map endet bewusst bei einem `mailto:`-Link. Das Projekt läuft im Rahmen
eines Masterschool-Programms, ohne Impressum und ohne Datenschutzerklärung.
Kontaktdaten oder Betriebsangaben zu erheben und zu speichern, wäre in dieser
Konstellation nicht zulässig. Der `mailto:`-Link speichert nichts: Der Nutzer
entscheidet selbst, ob und was er sendet. Das ist kein Rückstand, sondern die
korrekte Lösung für den aktuellen Rahmen — und passt zur Datensparsamkeit des
übrigen Systems.

Für einen späteren produktiven Betrieb bleibt der Funnel dennoch der Punkt, an
dem sich entscheidet, ob aus einer Diagnose ein Auftrag wird. Diese Frage ist
verschoben, nicht erledigt.

**Das Preismodell nimmt genau die richtigen Ängste weg.** Kein Abo, kein
Lock-in, Eigentum am System, Gewährleistung, offengelegte Fremdkosten. Für einen
Betrieb, der schon einmal in einem Softwarevertrag festhing, ist das stärker als
jedes Funktionsversprechen.

**Die Sprache trifft.** „Abende und Wochenenden gehören wieder Ihnen." „Ihre
Mitarbeiter müssen keine neuen Programme lernen." Kein Fachbegriff, keine
KI-Begeisterung, nur Alltag.

**Die Angebots-Automatisierung ist fachlich sauber.** Anfrage rein, KI erstellt
Entwurf, Entwurf landet auf dem Handy, Mensch gibt frei, dann erst Versand.
Ausdrücklich: „Kein Angebot verlässt Ihren Betrieb ohne Ihre Freigabe. Das
System erstellt — Sie entscheiden." Das ist exakt Autonomiestufe A2 mit
menschlicher Freigabe vor Außenwirkung. Dieses Produkt ist gut gedacht.

**Wichtig für die eigene Positionierung:** „Wir bauen auf dem auf, was Sie schon
haben" ist **nicht** das Alleinstellungsmerkmal von AI Start Map. Kihelfer24
sagt genau dasselbe, prominent und besser formuliert: „Ihre Werkzeuge — endlich
vernetzt. Sie behalten alles, was Sie schon haben. Wir legen eine intelligente
KI-Schicht über Ihre bestehenden Programme."

---

## 3. Wo es bricht: der Fall Schühchen

Das ist der wertvollste Teil des Materials, weil er die Grenze des Ansatzes
dokumentiert.

**Der erkannte Engpass** ist richtig beschrieben: Kunde wartet am Tresen, Suche
zwischen Schuhstapeln und handgeschriebenen Zetteln, Unklarheit, ob der Kunde
schon über die Fertigstellung informiert wurde.

**Die Empfehlung lautet:**

> „Schuh-Finder statt Zettel-Suchen. Nachher: Ein kurzer Blick auf den
> Platzhalter im Regal verrät Ihnen sofort, wo der Schuh liegt und ob er fertig
> ist."
>
> „Automatische Info statt Telefon-Marathon. Nachher: Der Kunde bekommt
> automatisch Bescheid, sobald der Schuh im Regal steht."

Beide Sätze setzen etwas voraus, das im Betrieb nicht existiert:

1. Es gibt keine eindeutige Kennzeichnung am Schuh. Ohne die kann kein
   „Platzhalter" auf irgendetwas verweisen.
2. Es gibt kein Ereignis „Schuh ist fertig und liegt an Platz X". Ohne dieses
   Ereignis kann nichts „automatisch" ausgelöst werden. Irgendjemand muss es
   erfassen — genau das ist die eigentliche Arbeit, und sie wird übersprungen.

In der Sprache des eigenen Katalogs: `GATE-02 Vorgangsanker` ist nicht bestanden,
und `FAIL-12 Automation vor Prozessbasis` liegt vor. Die richtige Empfehlung
wäre eine A0- beziehungsweise Vorstufe: erst eindeutige Kennzeichnung und
fester Ablageort, danach ist die Benachrichtigung trivial.

**Erfundene Zahlen.** Aus einem 20-Minuten-Gespräch werden abgeleitet:
3 bis 5 Stunden pro Woche, 400 bis 600 EUR pro Monat, Umsetzung in 2 bis 3
Wochen. Nichts davon ist gemessen. Auf der Landingpage steht dieselbe Mechanik
in größerem Maßstab: „200 Belege/Woche, Bearbeitungszeit sinkt von 15 auf 2
Minuten, über 45 Stunden pro Woche, mehr als 70.000 EUR jährlich." Die Rechnung
ist in sich stimmig, unterstellt aber, dass jede eingesparte Stunde in
zusätzlichen Umsatz umgewandelt wird — und ein Betrieb mit 200 Belegen pro Woche
ist nicht derselbe Kunde wie Schühchen.

**Personalisierungsfehler.** Die E-Mail geht an Silke, betrifft den Betrieb
Schühchen und beginnt mit „Ihre persönliche Analyse ist fertig, Caro". In einem
Geschäft, dessen Währung Vertrauen ist, verrät das mehr als ein Tippfehler: Der
Text wird zusammengesetzt, nicht verstanden.

**Die Analyse ist ein Verkaufsdokument.** Jeder Abschnitt endet beim selben
20-Minuten-Gespräch und denselben 800 EUR. Ein Ergebnis „hier hilft Ihnen
zuerst etwas anderes" ist in dieser Struktur nicht vorgesehen.

---

## 4. Was daraus für AI Start Map folgt

### Das Alleinstellungsmerkmal muss neu formuliert werden

Nicht: „Wir bauen auf dem auf, was Sie schon haben." Das sagen sie auch.

Sondern: **Wir sagen Ihnen, was zuerst fehlt — auch wenn wir Ihnen dann
zunächst keine KI verkaufen.** Kihelfer24 kann das strukturell nicht, weil jeder
Pfad in einem von drei Produkten enden muss. AI Start Map kann es, weil A0 ein
gültiges Ergebnis im Katalog ist.

Zweites, belegbares Unterscheidungsmerkmal: **keine erfundenen Zahlen.** Die
eigene Forschungsgrundlage verbietet das ausdrücklich. Das ist selten und
nachprüfbar.

### Jetzt übernehmbar, ohne Rechtsrahmen

- Die Alltagssprache ohne KI-Vokabular.
- Die Zweistufigkeit im Ergebnistext: „Sie brauchen zuerst eine eindeutige
  Kennzeichnung und einen festen Ablageort" ist kein verlorener Kunde, sondern
  ein kleineres erstes Projekt — und danach der naheliegende zweite Auftrag.
  Wenn das im Ergebnis nicht sichtbar wird, liest sich der ehrliche Befund wie
  eine Absage. Das ist reine Formulierungsarbeit und kostet nichts.

### Erst bei produktivem Betrieb relevant

Setzt Impressum, Datenschutzerklärung und eine Rechtsform voraus und ist im
Studienprojekt bewusst nicht umgesetzt:

- Festpreis, Werkvertrag, kein Abo, offengelegte laufende Fremdkosten,
  Eigentum am Ergebnis.
- Das Audit als PDF per E-Mail statt nur als Bildschirmseite.
- Terminbuchung und Erstgespräch.

---

## 5. Schühchen als Referenzfall

Der Fall eignet sich als verbindlicher Testfall, weil das falsche Ergebnis
dokumentiert vorliegt.

**Eingabe (sinngemäß aus der Analyse rekonstruiert):**

> Ich habe eine Schuhmacherei. Kunden bringen Schuhe zur Reparatur, ich schreibe
> den Auftrag auf einen Zettel und stelle die Schuhe ins Regal. Wenn der Kunde
> kommt, suche ich zwischen den Stapeln und den Zetteln nach dem richtigen Paar.
> Manchmal weiß ich nicht mehr, ob ich schon per WhatsApp Bescheid gegeben habe,
> dass die Schuhe fertig sind.

**Erwartetes Verhalten:**

- Problemfamilie `PF-05` (fehlende Objekt- und Ortszuordnung)
- Lösungsmuster `SP-04` (Objekt-ID und echter Ablageort)
- `GATE-02 Vorgangsanker` schlägt fehl; Voraussetzung wird ausdrücklich genannt
- Autonomiestufe beginnt bei `A0`
- Keine automatische Kundenbenachrichtigung als Kernlösung
- Keine Zeit- oder Geldangabe, die nicht aus der Erzählung stammt

**Verbotene Ausgaben:** „automatisch Bescheid", „Platzhalter im Regal" ohne
vorherige Kennzeichnung, jede Stunden- oder Euro-Schätzung.

Der Fall gehört in `knowledge/evaluation/` und wird über `scripts/evaluate.py`
mitgemessen.
