# Backlog — was jetzt, was später

Stand: 2026-08-11

Sammelstelle für alles, was besprochen und noch nicht umgesetzt ist. Damit
nichts verlorengeht und nichts zu früh angefangen wird.

---

## Erledigt

Vertragsmigration, Ausbau Blöcke 0 bis 6, Abschlusslauf. 268 Tests grün.
Vorher-Nachher-Vergleich liegt als `lauf_vorher.md` und `lauf_nachher.md` vor.

Ein Befund daraus, der eine frühere Annahme widerlegt: Die Langsamkeit kam
nicht von der Ausgabelänge, sondern davon, dass die Verbotsliste im Code und
die im Prompt auseinandergelaufen waren. Das Modell wusste nicht, welche
Wörter es vermeiden soll, schrieb sie, und die fertige Analyse wurde
verworfen — jedes Mal eine komplette zweite Erzeugung. Die Liste steht jetzt
einmal zentral und wird zur Laufzeit in den Prompt gegeben.

---

## Jetzt — vor dem Merge nach `main`

### Ein Testfall, der auf „ordnung" landen muss

Alle drei Fälle landen auf `reifestufe: genai`. Das ist für diese drei
richtig — aber es heißt, dass dein eigentliches Alleinstellungsmerkmal
ungetestet ist: „Hier hilft KI noch nicht, das musst du zuerst ordnen."

`TESTFAELLE_ZIELGRUPPE.md` braucht einen Fall, der zwingend auf `ordnung`
oder `digitalisierung` landet. Zum Beispiel ein Betrieb, der Aufträge
telefonisch annimmt und nirgends festhält — es gibt schlicht keine digitale
Spur, mit der eine KI arbeiten könnte.

Ohne diesen Fall ist nicht belegt, dass das System den ehrlichen Ausgang
überhaupt findet.

### Eine austauschbare Überschrift

„Wichtiges taucht erst bei der Rechnung auf" (Handwerksbetrieb) enthält
weder Gegenstand noch Kanal dieses Falls und würde genauso auf den Fotografen
passen. Fünf von sechs Überschriften sitzen, diese nicht.

Prompt schärfen: Die Überschrift muss mindestens einen Gegenstand oder Kanal
aus der Erzählung enthalten.

### Abgeschnittener Satz im Ablauf

Beim Blumenladen endet ein `ablauf_kuenftig`-Schritt auf „…und gewünschte/ü"
— exakt bei 180 Zeichen, dem Deckel des Feldes. Das Modell schreibt bis an die
Grenze.

Ein Deckel ist hier das falsche Werkzeug. Er muss so hoch liegen, dass er nie
erreicht wird; die Kürze kommt aus dem Prompt: „höchstens fünfzehn Wörter pro
Schritt". Aktuell sieht ein Kunde einen mitten im Wort abgeschnittenen Satz.

### Zuordnungstabelle Betriebstyp zu Betriebsart

Derzeit finden nur `fotograf`, `blumenladen` und `hausmeisterservice` ihre
Wissensdatei — die Zuordnung läuft über `business_example`. Die übrigen 21
bekannten Typen laden nichts.

Das war die richtige konservative Entscheidung (kein Nachbargewerbe raten),
braucht aber eine ausdrückliche Liste, die Derya festlegt. Kein Raten, eine
Tabelle:

```
A: hausmeisterservice, elektriker, maler, sanitaer, dachdecker,
   reinigungsservice, mobiler_reparaturdienst, gartenpflege
B: kfz_werkstatt, fahrradwerkstatt, schuhmacher, schneiderei
C: friseur, kosmetik, massage, fitnessstudio, fahrschule, physiotherapie
D: fotograf, architekturbuero, kreativagentur, kleine_agentur, freelancer,
   designer
E: blumenladen, konditorei, einzelhandel, onlinehandel, manufaktur, catering
F: coach, mentor, berater, beratungsteam, virtuelle_assistenz
G: hausverwaltung, immobilienmakler, kfz_gutachter, ferienwohnung
```

Was nicht in der Tabelle steht, lädt weiterhin nichts.

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

## Als Nächstes

### Darstellungsart `liste` ist ungeprüft

Keiner der drei Fälle hat sie gewählt. Sie ist nur im Template-Test belegt,
nie an echten Modelldaten. Zusätzlich weicht die Umsetzung von der Anweisung
ab: Sie füllt die Zeilen aus `daraus_wird` (Beschriftung, Wert, Status), die
Anweisung beschreibt eine echte Terminübersicht mit Zeit in fester Breite.

Erst prüfen, wenn ein Fall sie tatsächlich wählt — etwa ein Terminbetrieb.

### Interviewpfad für das Betriebsartenwissen

Die Tabelle in `BRANCHENWISSEN.md` sieht vor, dass der Interview-Agent
`diagnostically_relevant_questions`, `typical_exceptions` und
`required_information` bekommt. Nicht verkabelt, weil der Betriebstyp erst in
der Klassifikation während der Analyse entsteht — davor ist er unbekannt.

Der Lader und die Feldliste stehen fertig in `business_patterns.py`, nur der
Aufruf fehlt. Braucht einen zusätzlichen Modellaufruf im Interview. Eigene
Entscheidung, eigener Aufwand.

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
