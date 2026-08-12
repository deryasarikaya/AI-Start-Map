# Anweisung: Ausbau Ergebnisseite — Inhalt und Darstellung

Derya ist einige Stunden nicht erreichbar. Arbeite eigenständig, ohne
Rückfragen. Wenn eine Entscheidung wirklich offen ist, wähle die
konservativere Variante und vermerke sie im Abschlussbericht.

Grundlage: `ERGEBNIS_SPEC.md`, `BRANCHENWISSEN.md`, `BACKLOG.md`,
`TESTFAELLE_ZIELGRUPPE.md`, `START_HIER.md`.

---

## Rahmen

- Branch `feature/customer-output`. Vor jedem Commit `git branch --show-current`
  prüfen.
- Autor und Committer: `Derya <deryaxsarikaya@gmail.com>`. Kein Claude-Name,
  kein `Co-Authored-By`, kein Hinweis auf ein KI-Werkzeug in der
  Commit-Nachricht.
- **Kein Merge und kein Push nach `main`.** Der Abschluss-Merge wartet auf
  Deryas Freigabe.
- Nach jedem Block: Tests grün, committen, pushen. Ein Kontextabbruch darf
  höchstens einen Block kosten.
- `eval_llm_batch09.json` bleibt uncommitted.
- Keine fallbezogene Hartkodierung. Kein `if solution_id == ...` im
  Kundentextpfad.

**Prioritätsreihenfolge.** Arbeite Block 0 bis 6 in dieser Ordnung. Wenn die
Zeit oder der Kontext nicht reicht, brich nach einem abgeschlossenen Block ab
statt einen halb fertigen zu hinterlassen. Block 6 ist der verzichtbarste.

---

## Block 0 — Ausgangsaufnahme

Bevor du etwas änderst: Lass die drei Fälle aus `TESTFAELLE_ZIELGRUPPE.md`
durchlaufen — Blumenladen, Fotograf, Handwerksbetrieb — und sichere je Fall:

- den vollständigen gerenderten Text der Ergebnisseite
- `ergebnis_art`
- `engpass_titel` und `loesung.titel`
- die gemessene Dauer der Endanalyse

Leg das als `docs/auftrag/lauf_vorher.md` ab und committe es. Das ist der
Vergleichsstand, an dem Derya nach ihrer Rückkehr sieht, was die Änderungen
bewirkt haben.

Wenn ein Fall nicht durchläuft: den Fehler beheben, erneut laufen, im Bericht
vermerken.

---

## Block 1 — Schema: beide Vertragsänderungen zusammen

**Wichtig: Es gibt zwei neue Felder. Setz sie in EINEM Durchgang um**, sonst
migrierst du die Tests zweimal. Das ist die Lehre aus dieser Woche.

### 1a — `reifestufe` in `loesung`

```
reifestufe   str   "ordnung" | "digitalisierung" | "regelautomatisierung"
                   | "genai" | "agentisch"
```

Prompt-Regel:

```
## Die Reifeleiter

Prüfe in dieser Reihenfolge, welche Stufe den Engpass löst:

1. ordnung             ein fester Handgriff, eine Kennzeichnung, eine Regel
2. digitalisierung     etwas wird überhaupt erst festgehalten
3. regelautomatisierung  wenn X passiert, mache Y — ohne Verstehen
4. genai               etwas Unstrukturiertes muss verstanden werden
5. agentisch           mehrere Schritte werden selbständig verkettet

Wähle die KLEINSTE Stufe, die den Engpass tatsächlich löst.

Ist die richtige Stufe "ordnung" oder "digitalisierung", empfiehl keine KI —
und sag klar, warum nicht. Das ist ein vollwertiges Ergebnis, kein Mangel.
```

Die Reifestufe ersetzt nicht die Autonomiestufen A0–A5. Die beschreiben, wie
selbständig die KI arbeitet; die Reifestufe, welche Art Lösung überhaupt
richtig ist. Beide bleiben.

Auf der Seite wird die Reifestufe **nicht als Fachbegriff angezeigt.** Sie
steuert den Text. Wenn sie „ordnung" ist, muss der Abschnitt „Was ich dafür
einrichte" das widerspiegeln — dann richtest du zuerst nichts mit KI ein.

### 1b — `beispiel.darstellung`

```
darstellung   str   "nachricht" | "karte" | "liste"
```

Das Modell wählt die Form, die zum `ergebnis_art` passt:

- **nachricht** — für Rückfragen, Bestätigungen, Erinnerungen, Antwortentwürfe
- **karte** — für Einsatznotiz, Bestellkarte, Kundenakte, Freigabestand,
  Rechnungsentwurf
- **liste** — für Tagesübersicht, offene Vorgänge, Terminübersicht

Prompt-Regel:

```
beispiel.darstellung richtet sich danach, was der Betrieb tatsächlich in der
Hand hält. Eine Rückfrage ist eine Nachricht. Eine Einsatznotiz ist eine
Karte. Eine Tagesübersicht ist eine Liste.

Wenn ergebnis_art "kein sichtbares Ergebnis" lautet, wähle "nachricht" und
zeig, was im Hintergrund passiert und wo der Betrieb es merkt.
```

### 1c — Tests

Nach der Schemaänderung die Suite einmal auf den neuen Vertrag ziehen. Die
kanonischen Bauhelfer in `tests/conftest.py` sind der Ansatzpunkt — dort
ergänzen, dann laufen die abhängigen Dateien mit.

Commit: `Add maturity level and example presentation type`

---

## Block 2 — Prompt-Regeln aus dem Backlog

Drei Regeln, alle in `docs/prompts/endanalyse_system.md`.

### 2a — Zusammenlauf statt Kanalzahl

```
Nenne nie die Anzahl der Kanäle als Engpass. Ein Betrieb darf beliebig viele
Kanäle haben. Der Engpass ist, ob die Informationen aus diesen Kanälen am Ende
einem gemeinsamen Vorgang zugeordnet werden.

Falsch:  "Bestellungen kommen über fünf verschiedene Wege"
Richtig: "Fünf Wege rein, keiner, auf dem sie zusammenkommen"
```

### 2b — Bestehendes nicht ersetzen

```
Prüfe vor jeder Empfehlung, was der Betrieb bereits nutzt und was davon
bleiben kann. Schlag ein neues System nur vor, wenn eine Anbindung
nachweislich nicht genügt.

Wenn nichts Neues nötig ist, ist das ein gutes Ergebnis — kein Mangel.
```

### 2c — Der Automatisieren-Test

```
Übertragen, zuordnen, erinnern, bestätigen, standardisiert weiterleiten
→ automatisierbar.

Fachlich bewerten, Preis entscheiden, freigeben, Ausnahme entscheiden,
Verantwortung tragen
→ bleibt beim Menschen.

Prüfe jeden Schritt in was_die_ki_macht gegen diese beiden Listen. Was in die
zweite fällt, gehört nach was_du_machst.
```

Commit: `Add convergence, preservation and automation rules to prompt`

---

## Block 3 — Betriebsartenwissen anschließen

### 3a — Dritte Datei anlegen

`knowledge/business_patterns/D_project_briefing_approval.yaml`

Vierzehn Felder nach `BRANCHENWISSEN.md`, Vorbild sind die vorhandenen
`E_orders_goods.yaml` und `A_field_service.yaml`.

Inhalt für Betriebsart D — Fotograf, Architekturbüro, Designer, Agentur,
Freelancer. Der diagnostische Kern:

```
diagnostic_focus: >
  Steht an einer Stelle, welche Fassung gerade gilt und was schon freigegeben
  ist? Anforderungen und Änderungen kommen über Wochen und über mehrere
  Kanäle. Der Engpass ist selten die Menge, sondern die fehlende gemeinsame
  Fassung.
```

Leite den Rest aus der Fotografen-Erzählung in `TESTFAELLE_ZIELGRUPPE.md`, den
vorhandenen Batch-09-Workflows für SP-02 und SP-07 und den beiden bestehenden
Dateien als Formvorlage ab. `realistic_worker_language` bleibt leer.
`do_not_assume` muss den Eintrag „dass KI die erste sinnvolle Lösung ist"
enthalten.

### 3b — Gemeinsame Diagnosefrage

In alle drei vorhandenen Dateien ergänzen, unter
`diagnostically_relevant_questions`:

```
- Wo laufen diese Informationen heute am Ende zusammen?
```

### 3c — Laden und zuschneiden

Die Datei wird über den bereits verkabelten Betriebstyp ausgewählt. Welches
Feld an welchen Aufruf geht, steht als Tabelle in `BRANCHENWISSEN.md` —
halte dich daran, gib nicht alles an alles.

Passt keine Betriebsart eindeutig: **keine Datei laden.** Kein
Nachbargewerbe.

Prompt-Regel für das Vokabular:

```
Verwende aus domain_vocabulary nur Wörter, die zum tatsächlich beschriebenen
Fall passen. Die Liste ist kein Inhaltsverzeichnis, das abgearbeitet wird.
```

Commit: `Add project pattern knowledge and convergence question`

---

## Block 4 — Darstellung: Templates

Alles in `results.html` und `report.html`. Keine Logikänderung.

### 4a — Die drei Darstellungsarten

**nachricht** — Sprechblasen, abwechselnd. Eingang links, Antwort rechts.
Absenderzeile darüber klein und gedämpft. Unter der letzten Blase eine kleine
Zeile, was mit der Antwort passiert („Antwort wurde der Bestellung
zugeordnet"). Blasen mit `border-radius: 12px`, jeweils eine Ecke auf `4px`
zur Sprecherseite. Maximal 82 Prozent Breite.

**karte** — Umrandeter Block. Kopfzeile mit Bezeichnung links und Statuspunkt
rechts. Darunter eine Feldtabelle mit Trennlinie darüber, Beschriftung in
`--text-secondary`, Wert in `--text-primary`, Spaltenbreite der Beschriftung
etwa 38 Prozent. Fußzeile mit Trennlinie: fehlende Angaben in
`--text-danger`, rechts die Freigabe-Andeutung.

**liste** — Umrandeter Block, Kopfzeile mit Zeitraum. Darunter Zeilen mit
Trennlinie: Zeit links in fester Mindestbreite, Beschreibung mittig
ausgedehnt, Statuspunkt rechts. Statuspunkte als kleine Pille:
`--bg-success`/`--text-success` für bereit, `--bg-danger`/`--text-danger` für
fehlend, `--bg-warning`/`--text-warning` für prüfen.

Alle drei tragen oben denselben kleinen Hinweis, dass es sich um erfundene
Beispielangaben handelt.

### 4b — Zweispalter heute gegen künftig

`ablauf_heute` und `ablauf_kuenftig` nebeneinander statt untereinander.

Zwei Flächen mit `border-radius: 12px`, links `--bg-danger`, rechts
`--bg-success`. Kleine Kopfzeile in der jeweiligen Textfarbe: „So läuft es
heute" und „Nach der Einrichtung". Darunter die Schritte als Zeilen, kein
Kartenrahmen um die einzelnen Punkte.

Raster: `grid-template-columns: repeat(auto-fit, minmax(240px, 1fr))` mit
`gap: 12px`. Damit stapelt es auf dem Handy von selbst.

### 4c — `moeglichkeiten` als Kacheln

Statt drei Textzeilen ein Kachelraster:
`repeat(auto-fit, minmax(180px, 1fr))`, `gap: 12px`.

Jede Kachel: Rang oben klein und gedämpft mit leichter Sperrung, dann Titel in
15px/500, dann Begründung in 13px `--text-secondary`. Weißer Grund, halbe
Haarlinie als Rahmen, `border-radius: 12px`.

Bei nur einem oder zwei Einträgen wird auch nur einer oder zwei gerendert. Es
wird nichts aufgefüllt.

Commit: `Render example presentation types and side-by-side workflow`

---

## Block 5 — Stylesheet

Nur `app/static/styles.css`. Keine Logik, kein Template.

### 5a — Kacheln beim Überfahren

```css
transition: transform .18s ease, border-color .18s ease;
```
und im Hover-Zustand `transform: translateY(-3px)` plus
`border-color: var(--border-strong)`. Kein Schatten, kein Farbwechsel der
Fläche.

### 5b — Sanftes Einblenden beim Scrollen

`IntersectionObserver`, etwa fünfzehn Zeilen. Elemente starten mit
`opacity: .001` und `transform: translateY(8px)`, gehen bei Sichtbarkeit auf
`opacity: 1` und `translateY(0)` über `.35s ease`.

**Zwei Bedingungen, die zwingend sind:**

1. **Ohne JavaScript muss alles sichtbar sein.** Setz den Startzustand über
   eine Klasse, die das Skript selbst hinzufügt — nicht im Stylesheet
   voreingestellt. Sonst ist die Seite ohne JavaScript leer.
2. **Im Druck ist alles sichtbar.** In `@media print` alle Deckkraft- und
   Verschiebungsregeln zurücksetzen. Sonst ist das PDF leer oder halb leer.

Prüf beides ausdrücklich: einmal die Seite mit abgeschaltetem JavaScript, und
einmal die Druckansicht.

Wenn du an dieser Stelle unsicher bist: **lass das Einblenden weg.** Eine
statische Seite ist unendlich besser als ein leeres PDF.

### 5c — `prefers-reduced-motion`

```css
@media (prefers-reduced-motion: reduce) { alle Übergänge auf none }
```

Commit: `Add hover and reveal transitions with print and no-script fallback`

---

## Block 6 — Feldlängen und Zeitbudget

Zuletzt, weil es die Ausgabe verändert.

`max_length` ergänzen auf: `was_die_ki_macht`, `was_dabei_rauskommt`,
`erster_schritt`, `engpass_text`, `bleibt_bei_dir`.

Orientiere dich an dem, was in den guten Läufen tatsächlich erzeugt wurde,
plus etwa 20 Prozent Luft. Nicht knapper.

**`beispiel.nachricht` vorsichtig behandeln.** Zwei bis vier Sätze müssen
hineinpassen. Ein zu enger Deckel macht die Nachricht wieder zu einem
Formular, und die Umgangssprachlichkeit war schwer erarbeitet.

Danach den Handwerksfall messen. Wenn er zuverlässig unter 150 Sekunden
bleibt, `FINAL_ANALYSIS_TIMEOUT_SECONDS` auf 180 zurücksetzen. Wenn nicht, bei
240 lassen und die gemessene Zeit berichten.

Commit: `Cap free-text field lengths`

---

## Abschlusslauf

Nach Block 6 — oder nach dem letzten Block, den du geschafft hast:

Die drei Fälle erneut komplett durchlaufen lassen. Ergebnis als
`docs/auftrag/lauf_nachher.md` ablegen und committen, im gleichen Format wie
`lauf_vorher.md`.

Prüf dabei die Abnahmebedingungen aus `ERGEBNIS_SPEC.md`, besonders die, die
nur fallübergreifend prüfbar sind:

- `ergebnis_art` unterscheidet sich zwischen den drei Fällen
- keine der Überschriften würde unverändert auf einen der anderen Fälle passen
- `beispiel.darstellung` ist nicht bei allen drei gleich
- `reifestufe` ist begründet und nicht bei allen drei dieselbe

Wenn eine dieser Bedingungen nicht erfüllt ist: **melden, nicht als erledigt
ausgeben.**

---

## Abschlussbericht

1. Welche Blöcke sind fertig, welche nicht
2. Geänderte Dateien je Block, mit Commit-Hash
3. Testergebnis am Ende
4. Für alle drei Fälle: `ergebnis_art`, `reifestufe`,
   `beispiel.darstellung`, `engpass_titel`, `loesung.titel`, Dauer
5. Der vollständige gerenderte Kundentext des Blumenladen-Falls
6. Welche Abnahmebedingungen **nicht** erfüllt sind
7. Ergebnis der Druckprüfung und der Prüfung ohne JavaScript
8. Bestätigung: Branch war `feature/customer-output`, Autor war Derya, kein
   Merge nach `main`
9. **Was nicht geklappt hat oder wo du unsicher bist.** Nicht optional.

Wenn du an einer Stelle nicht weiterkommst: stoppen, sichern, melden. Nicht
raten und nicht ersatzweise etwas anderes bauen.
