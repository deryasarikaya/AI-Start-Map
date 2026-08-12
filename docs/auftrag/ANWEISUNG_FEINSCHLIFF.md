# Anweisung: Feinschliff vor dem Merge

Sechs kleine Punkte aus Deryas Durchsicht von `lauf_nachher.md`, plus ein
neuer Testfall. Danach ist der Merge nach `main` freigegeben — sofern die
Bedingung unten erfüllt ist.

Branch `feature/customer-output`. Autor `Derya <deryaxsarikaya@gmail.com>`.
Kein Merge nach `main` ohne die Bedingung am Ende.

---

## 1 — Abgeschnittener Satz

Beim Blumenladen endet ein `ablauf_kuenftig`-Schritt auf „…und gewünschte/ü",
exakt bei 180 Zeichen.

Ein Deckel ist hier das falsche Werkzeug. Setz ihn auf einen Wert, der nie
erreicht wird, und hol die Kürze aus dem Prompt:

```
Jeder Schritt in ablauf_heute und ablauf_kuenftig ist ein kurzer, vollständiger
Satz von höchstens fünfzehn Wörtern. Lieber zwei Schritte als einer, der zu
lang wird.
```

Prüf danach an allen vier Fällen, dass kein Feld mehr an seiner Grenze endet.
Ein Satz, der mitten im Wort abbricht, ist für einen Kunden schlimmer als jedes
Fachwort.

---

## 2 — Überschrift Handwerksbetrieb

„Wichtiges taucht erst bei der Rechnung auf" ist zu allgemein und würde
genauso auf den Fotografen passen.

Derya schlägt vor: **„Du baust jeden Einsatz bei der Rechnung wieder
zusammen."** Das ist die Zielrichtung — nicht wörtlich hartkodieren, sondern
den Prompt so schärfen, dass solche Überschriften entstehen:

```
Die Überschrift muss mindestens einen Gegenstand, einen Kanal oder eine
Tätigkeit aus der Erzählung enthalten. Eine Überschrift, die auf einen
beliebigen anderen Betrieb passen würde, ist falsch.

Prüf sie selbst: Würde dieser Satz auch für einen völlig anderen Betrieb
stimmen? Dann schreib ihn neu.
```

---

## 3 — „KI trainieren" ist fachlich falsch

Kommt beim Fotografen vor. Es wird kein Modell trainiert — es werden
Anweisungen, Regeln und Erkennung angepasst.

Auf die Verbotsliste, als Wortstamm: `trainier`, `antrainier`, `anlernen`,
`Modell trainieren`, `Lernphase`.

Ersatzformulierungen für den Prompt:

```
Statt "die KI trainieren":
  "ich stelle ein, worauf sie achten soll"
  "ich passe an, welche Angaben erkannt werden"
  "ich korrigiere an deinen echten Fällen nach"
```

Das ist keine Kosmetik. Ein Kunde, dem Training versprochen wird, erwartet
etwas anderes als das, was tatsächlich passiert.

---

## 4 — Widerspruch in `ai_capabilities` bei SP-01

Im Katalog steht bei SP-01 die Fähigkeit:

```
- erkennt, ob die Anfrage zu einem bestehenden Kunden gehört
```

Das setzt eine gepflegte Kundenliste voraus. In
`knowledge/business_patterns/E_orders_goods.yaml` steht aber unter
`do_not_assume`:

```
- dass ein Kundenverwaltungssystem sinnvoll ist
```

Beides zusammen ist ein Widerspruch. Ändere den Katalogeintrag zu:

```
- erkennt, wenn mehrere Nachrichten zur selben Anfrage gehören
```

Das ist ohne Kundenliste möglich und deckt den eigentlichen Nutzen ab.

Prüf die übrigen `ai_capabilities` auf denselben Fehler: Jede Fähigkeit muss
ohne Voraussetzungen funktionieren, die in `do_not_assume` ausgeschlossen
sind. Was eine Voraussetzung braucht, gehört in `voraussetzungen`, nicht in
die Fähigkeitenliste.

---

## 5 — Zuordnung: Workflow, nicht Unternehmen

**Wichtige Korrektur an der Tabelle im Backlog.** Die Betriebsart hängt am
gewählten Prozess, nicht am Unternehmen.

Derselbe Fotograf fällt beim Kundenprojekt unter D — Briefing und Freigaben —
und beim Beratungsgespräch unter F — Gespräch als Leistung. Ein
Hausmeisterservice mit vielen Terminanfragen kann bei diesem Prozess C sein
statt A.

Umsetzung:

1. Der Betriebstyp aus der Klassifikation ist ein **Hinweis**, keine
   Festlegung.
2. Die Betriebsart wird aus **Betriebstyp und gewähltem Prozess zusammen**
   bestimmt.
3. Die Tabelle unten ist die Vorauswahl. Wenn der gewählte Prozess erkennbar
   zu einer anderen Betriebsart gehört, gilt die Betriebsart des Prozesses.
4. Ist die Zuordnung nicht eindeutig: **keine Datei laden.** Kein
   Nachbargewerbe, keine Näherung.

```
A  hausmeisterservice, elektriker, maler, sanitaer, dachdecker,
   reinigungsservice, mobiler_reparaturdienst, gartenpflege,
   physischer_servicebetrieb, mobiler_servicebetrieb
B  kfz_werkstatt, fahrradwerkstatt, schuhmacher, schneiderei
C  friseur, kosmetik, massage, fitnessstudio, fahrschule, physiotherapie
D  fotograf, architekturbuero, kreativagentur, kleine_agentur, freelancer,
   b2b_agentur, designer
E  blumenladen, konditorei, einzelhandel, onlinehandel, kleine_manufaktur,
   catering, veranstaltungsdienstleister
F  coach, mentor, berater, beratungsteam, b2b_dienstleister,
   virtuelle_assistenz
G  hausverwaltung, immobilienmakler, kfz_gutachter, ferienwohnung
```

Nur `A`, `D` und `E` haben derzeit eine Wissensdatei. Die übrigen laden nichts
— das ist richtig und bleibt so, bis die Dateien geschrieben sind.

---

## 6 — Vierter Testfall: der Betrieb, für den KI noch nicht passt

Der wichtigste Punkt dieser Runde. Bisher landen alle drei Fälle auf
`reifestufe: genai`. Dass das System auch „hier hilft KI noch nicht" sagen
kann, ist an keinem Fall belegt.

Ergänze in `TESTFAELLE_ZIELGRUPPE.md` als achten Fall:

### 8 — Malerbetrieb, überwiegend telefonisch

> Wir sind ein kleiner Malerbetrieb, mein Bruder und ich. Die meisten Aufträge
> kommen übers Telefon rein oder die Leute sprechen mich direkt an, wenn ich
> irgendwo auf der Baustelle bin. Ich hab dann meistens keinen Zettel dabei
> und merk es mir einfach. Manchmal schreib ich es abends auf, manchmal nicht.
> Eine richtige Auftragsnummer haben wir nicht, wir sagen einfach „die Frau
> Schneider in der Bahnhofstraße". Wenn dann drei Wochen später jemand anruft
> und fragt, wann wir kommen, muss ich erstmal überlegen, wer das war und was
> genau ausgemacht war. Bei den Preisen ist es das Gleiche — ich hab was
> gesagt, aber es steht nirgends. Und wenn mein Bruder anfängt und ich war
> beim Kunden, dann erzähl ich ihm das eben schnell im Auto. Es geht meistens
> gut, aber manchmal machen wir was doppelt oder es fehlt Material, weil
> keiner mehr weiß, was vereinbart war.

**Erwartet:**

- `reifestufe`: `ordnung` oder `digitalisierung` — **nicht** `genai`
- die Empfehlung enthält keine KI-Lösung als ersten Schritt
- der erste Schritt ist eine einfache, verbindliche Erfassung: nach jedem
  Anruf oder Gespräch eine kurze Notiz mit Kunde, Anliegen, Termin und Stand
- `moeglichkeiten` darf einen späteren KI-Schritt nennen, aber nicht als
  größten Hebel
- der Text sagt ausdrücklich, warum KI hier noch nicht greift: Es gibt keine
  Aufzeichnung, aus der eine KI etwas machen könnte

Verbotene Formulierungen für diesen Fall: alles, was so klingt, als wäre der
Betrieb zu rückständig oder als hätte er etwas falsch gemacht. Er arbeitet
so, wie es funktioniert hat. Der Ton bleibt sachlich und respektvoll.

---

## Ablauf

1. Punkte 1 bis 5 umsetzen
2. Testfall 8 ergänzen
3. Tests laufen lassen — müssen grün bleiben
4. **Alle vier Fälle** live durchlaufen lassen
5. Ergebnis als `docs/auftrag/lauf_nachher_2.md` ablegen, gleiches Format
6. Committen und pushen

Commit: `Refine customer wording and add non-AI test case`

---

## Merge-Bedingung

Derya hat den Merge nach `main` unter genau dieser Bedingung freigegeben:

> Wenn der vierte Fall wirklich auf `ordnung` oder eine entsprechend niedrige
> Reifestufe kommt **und** die anderen drei nicht schlechter werden, kann nach
> `main` gemergt werden.

Prüf das ausdrücklich, indem du `lauf_nachher_2.md` gegen `lauf_nachher.md`
hältst:

- landet Fall 8 auf `ordnung` oder `digitalisierung`?
- sind `engpass_titel` und `loesung.titel` der ersten drei Fälle unverändert
  gut oder besser?
- ist der abgeschnittene Satz weg?
- kommt „trainier" nirgends mehr vor?
- sind alle Tests grün?

**Fünfmal ja:** Merge nach `main` wie in `START_HIER.md` Schritt D, dann den
Arbeitsbranch löschen.

**Einmal nein:** nicht mergen, melden, stoppen.

---

## Bericht

Kurz halten:

1. Was geändert wurde, je Punkt
2. Für alle vier Fälle: `reifestufe`, `engpass_titel`, `loesung.titel`
3. Der vollständige Text von Fall 8
4. Die fünf Merge-Prüfungen mit ja oder nein
5. Gemergt oder nicht, mit Begründung
6. Was nicht geklappt hat
