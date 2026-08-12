# Backlog — was jetzt, was später

Stand: 2026-08-11

Sammelstelle für alles, was besprochen und noch nicht umgesetzt ist. Damit
nichts verlorengeht und nichts zu früh angefangen wird.

---

## Läuft gerade

Prompt-Runde und Wortfilter sind durch. Offen bei Claude Code:

1. Builder auf `conftest.spec_payload()` ziehen
2. `test_output_contract_v3.py` neu aus den Abnahmebedingungen
3. Committen und pushen
4. Danach: `max_length` auf den Fließtextfeldern, damit das Zeitbudget von
   240 wieder auf 180 kann

**Bis das durch ist, kommt nichts Neues dazu.**

---

## Jetzt — klein, geht mit der nächsten Runde

### Zusammenlauf statt Kanalzahl

Die wichtigste Umdeutung aus der Wettbewerbsanalyse:

> Viele Eingangskanäle sind nicht das Problem. Problematisch wird es, wenn sie
> später nicht in einen gemeinsamen Vorgang münden.

Heute behandelt das System „fünf Kanäle" als Engpass. Ein Betrieb darf aber
beliebig viele Kanäle haben — der Engpass ist, dass nichts zusammenläuft.

**Als Prompt-Regel:**

```
Nenne nie die Anzahl der Kanäle als Engpass. Der Engpass ist, ob die
Informationen aus diesen Kanälen am Ende einem gemeinsamen Vorgang zugeordnet
werden.

Falsch:  "Bestellungen kommen über fünf verschiedene Wege"
Richtig: "Fünf Wege rein, keiner, auf dem sie zusammenkommen"
```

**Als Diagnosefrage in allen sieben Betriebsart-Dateien:**

```
Wo laufen diese Informationen heute am Ende zusammen?
```

Signalantworten für einen strukturellen Engpass: „nirgendwo", „in meinem
Kopf", „später beim Rechnungsschreiben", „ich suche sie zusammen".

### Bestehendes nicht ersetzen

**Als Prompt-Regel:**

```
Prüfe vor jeder Empfehlung, was der Betrieb bereits nutzt und was davon
bleiben kann. Schlag ein neues System nur vor, wenn eine Anbindung
nachweislich nicht genügt.

Wenn nichts Neues nötig ist, ist das ein gutes Ergebnis — kein Mangel.
```

### Der Automatisieren-Test

**Als Prompt-Regel:**

```
Übertragen, zuordnen, erinnern, bestätigen, standardisiert weiterleiten
→ Automatisierung prüfen.

Fachlich bewerten, Preis entscheiden, freigeben, Ausnahme entscheiden,
Verantwortung tragen
→ bleibt beim Menschen.
```

### Reifestufen

Aus der Wissensarchitektur-Analyse. Ein Feld `reifestufe` in `loesung`, plus
Prompt-Regel:

```
Ordnung → Digitalisierung → regelbasierte Automatisierung → GenAI → agentisch

Wähle die kleinste Stufe, die den Engpass löst. Ist die richtige Stufe
"Ordnung", empfiehl keine KI — und sag warum.
```

Das ersetzt nicht die Autonomiestufen A0–A5. Die beschreiben, wie
selbständig die KI arbeitet; die Reifestufe beschreibt, welche Art Lösung
überhaupt richtig ist.

---

## Als Nächstes — je ein halber Tag

### Darstellungsarten für den Beispielblock

Feld `beispiel.darstellung` mit `nachricht | karte | liste`, später `dokument`.
Das Modell wählt, das Template rendert. Entwurf liegt vor.

**Warum:** Derselbe Inhalt in drei Formen statt einer grauen Feldtabelle. Eine
Einsatznotiz sieht aus wie eine Notiz, eine Rückfrage wie eine Nachricht, eine
Tagesübersicht wie eine Liste.

### Zweispalter heute gegen künftig

`ablauf_heute` und `ablauf_kuenftig` nebeneinander statt untereinander, in
getönten Flächen.

### Stylesheet-Runde

Reine `styles.css`-Arbeit, keine Logik:
- Übergänge auf Kacheln beim Überfahren
- sanftes Einblenden beim Scrollen
- Statuspunkte in Farbe
- `moeglichkeiten` als Kacheln statt Textzeilen

### Dritte Betriebsart-Datei

`D_project_briefing_approval` für den Fotografen. Struktur steht, `E` und `A`
liegen als Vorlage vor.

### Erwartungen pro Prozess statt pro Fall

In `TESTFAELLE_ZIELGRUPPE.md` steht die erwartete Musterzuordnung am ganzen
Fall. Der Fotograf hat aber zwei Engpässe in einer Erzählung — Briefing
vorher, Freigaben nachher — und je nach gewähltem Prozess ist ein anderes
Muster richtig. Die Erwartung gehört an den Prozess.

---

## Später — nach der Präsentation

### `main` aufgeräumt halten

Nach Abschluss von `feature/customer-output`: Merge nach `main`, alte Branches
löschen. Dann ein Hauptzweig, ein Arbeitszweig.

### `routes.py` in Services und Repository zerlegen

Mentorenauftrag. 2796 Zeilen mit Routing, Datenbankzugriff, Ablauflogik und
Textaufbereitung durcheinander. Routen sollen dünn sein. Eine Route ruft nie
eine andere Route auf — kommt aktuell vor. Die Tests sind das Sicherheitsnetz.

### Restliche vier Betriebsart-Dateien

`B_workshop_customer_item`, `C_appointment_participant_service`,
`F_conversation_service`, `G_objects_cases_deadlines`.

### Getrennter Diagnose- und Lösungsaufruf

Aus der Wissensarchitektur-Analyse. Konzeptionell sauber, praktisch ein Umbau
der Pipeline plus doppelte Laufzeit. Erst sinnvoll, wenn die Ausgabe stabil
ist.

### Kontext pro Aufruf zuschneiden

Nicht jeder Aufruf bekommt alles. Die Tabelle in `BRANCHENWISSEN.md` legt das
für die Betriebsart-Dateien bereits fest; für Katalog und RAG steht es noch
aus.

### Klickbarer Ergebnisprototyp

Steht bereits in `docs/ROADMAP.md` unter Backlog-Ideen.

### BAFA-Beratungsförderung prüfen

Nicht Produkt, sondern Geschäft. Der Bund übernimmt je nach Region 50 oder 80
Prozent der Beratungskosten bei höchstens 3.500 Euro förderfähigen Kosten,
wenn der Berater gelistet ist. Für einen kleinen Betrieb verändert das die
Rechnung vollständig. Relevant nach der Gewerbeanmeldung, nicht davor.

---

## Bewusst nicht

**Stackwechsel auf Next.js.** Die Lebendigkeit fremder Seiten ist CSS, kein
Framework. Ein Wechsel drei Wochen vor der Präsentation kostet alles und
bringt nichts, was eine Stylesheet-Datei nicht auch kann.

**Zweite Taxonomie neben den zehn Solution Patterns.** Weder die acht
KI-Anwendungsfelder noch die fünf Meta-Muster aus der Wettbewerbsanalyse. Die
Inhalte sind teilweise richtig und gehören als Prompt-Regeln in den Ablauf —
nicht als neue Auswahlebene. Zehn Muster sind bereits schwer genug zuverlässig
zu treffen.

**Readiness-Score, ROI-Rechnung, Break-even, Change Management.** Ein
Konzernrahmen. Für einen Betrieb mit drei Leuten überdimensioniert, und der
halbe Apparat verlangt Zahlen, die nicht erfunden werden dürfen.

**Dreißig Branchendateien.** Sieben Betriebsarten decken alle genannten Berufe
ab. Ein Maler und ein Elektriker haben denselben Informationsfluss.

**Fremde Prompt-Texte übernehmen.** Themen als Anhaltspunkt ja,
Formulierungen nein, fertige Lösungssprünge der Art „Branche X → Werkzeug Y"
schon gar nicht.
