# Batch 10 · Lösungsarchitektur-Wissen — Spezifikation

Was diesem RAG bisher fehlt: **Wissen darüber, welche größeren Lösungen es
überhaupt gibt.** Der vorhandene Bestand hilft, Probleme zu erkennen. Er
enthält nichts darüber, wie ein zusammenhängendes System aussieht.

Deshalb kam bei der Hausverwaltung „Erfassungsformular" und „Zustandsanzeige"
statt „KI-Posteingang" und „Vorgangsakte". Das Modell kannte die Kategorien
nicht. Wir haben das mit Beispielen im Prompt geflickt — und gemessen, dass die
Beispiele wörtlich abgeschrieben werden.

**Abgerufenes Wissen färbt nicht ab. Es begründet.** Das ist der Zweck dieses
Batches.

---

## Was hier NICHT hineingehört

Diese drei Verbote sind wichtiger als alles andere in dieser Datei.

**Keine Regeln.** „Bei Unsicherheit nicht zuordnen", „Preise brauchen
menschliche Freigabe", „erst Ist-Prozess verstehen" — das sind Zusicherungen,
die **immer** gelten müssen. Eine Regel, die nur greift, wenn der Abruf sie
zufällig findet, ist keine Regel. Sie gehören in `app/prompts/grundregeln.md`
und in die Prüfungen in `app/schemas.py`.

**Keine Gestaltung.** Farben, Abschnittsreihenfolge, Schaltflächen,
Seitenaufbau. Das steht in den Vorlagen und im Stylesheet.

**Keine fremden Werbetexte.** Nichts aus AutomationsManufaktur oder anderen
Anbietern im Wortlaut. Abstrahieren zu einem eigenen Muster ist erlaubt und
erwünscht — abschreiben nicht.

**Und keine Kundenfakten.** Kein Satz aus einem der Testfälle. Beispiele in
Feldern werden ausdrücklich als Beispiel gekennzeichnet.

---

## Ablage und Format

```
knowledge/candidates/batch_10/
  README.md
  01_business_patterns.jsonl        7 Datensätze
  02_diagnostic_patterns.jsonl     12 Datensätze
  03_solution_families.jsonl       15 Datensätze
  04_automation_capabilities.jsonl 12 Datensätze
  05_target_architectures.jsonl     6 Datensätze
  06_source_register.csv
```

**JSONL: ein Datensatz je Zeile, kein Zeilenumbruch innerhalb eines
Datensatzes.** Das ist die häufigste Fehlerquelle. Schreib die Dateien mit
einem Skript, nicht von Hand.

### Pflichtfelder in jedem Datensatz

Ohne diese beiden bricht der Indexer mit `RagConfigurationError` ab:

| Feld | Bedeutung |
|---|---|
| `chunk_id` | eindeutig über den **ganzen** Wissensbestand |
| `chunk_type` | der Typ, siehe je Datei unten |

Dazu in jedem Datensatz:

| Feld | Wert |
|---|---|
| `title` | kurzer sprechender Name |
| `batch_id` | `batch_10` |
| `source_strength` | `derived` |
| `content_origin` | `synthesized_from_research` |
| `is_primary_evidence` | `false` |
| `process_type` | Liste der Betriebsarten-Buchstaben, für die es gilt, z. B. `["A","D","G"]` |

**Wichtig zum Verständnis:** Wenn ein Datensatz **kein** Feld `content` hat,
baut der Indexer den durchsuchbaren Text aus **allen** übrigen Feldern
zusammen, im Format `feldname: wert`. Die Feldnamen werden also mitdurchsucht.
Deshalb sind sprechende deutsche Feldnamen wichtig — sie helfen beim Finden.

**Setz kein `content`-Feld.** Lass den Indexer den Text aus den Feldern bauen.

### Was NICHT in den Suchtext gehört

Der Indexer schließt heute nur `chunk_id`, `chunk_type`, `batch_id`,
`source_ids`, `source_strength` und `content_origin` aus. Alles andere landet
im durchsuchbaren Text — auch das hier:

```
passende_loesungsfamilien: ["SF-02", "SF-03", "SF-04"]
is_primary_evidence: false
process_type: ["A", "G"]
```

Das ist Rauschen. IDs und Verwaltungsangaben helfen beim Filtern, nicht beim
Finden.

**Das ist eine Änderung am Indexer, nicht an deinen Dateien.** Schreib die
JSONL-Dateien genau wie hier beschrieben — der Indexer sorgt dafür, dass
Verwaltungsfelder und Querverweise aus dem Einbettungstext herausfallen. Steht
in der Beschreibung des Abrufwegs (`docs/RAG.md`).

Für dich heißt das nur: **Die Querverweisfelder trotzdem sorgfältig füllen.**
Sie werden gebraucht — aber zum Nachschlagen, nicht zum Suchen.

---

# Datei 1 · `01_business_patterns.jsonl` — 7 Datensätze

Die sieben Betriebsarten. **Nicht nach Branche**, sondern danach, wie Arbeit
durch den Betrieb fließt. Ein Friseur und eine Physiotherapie sind dieselbe
Betriebsart.

`chunk_type`: `business_pattern`
`chunk_id`: `BP-A` bis `BP-G`

| ID | Betriebsart | Beispielbetriebe |
|---|---|---|
| BP-A | Außeneinsatz | Hausmeister, Handwerk vor Ort, Wartung |
| BP-B | Werkstatt und Gegenstand | Kfz, Reparatur, Schneiderei |
| BP-C | Terminbetrieb | Friseur, Kosmetik, Physiotherapie, Praxis |
| BP-D | Projekt mit Briefing und Freigabe | Agentur, Planung, Bau |
| BP-E | Bestellung und Ware | Blumen, Konditorei, Onlinehandel |
| BP-F | Gespräch und Beratung | Beratung, Vermittlung, Vertrieb |
| BP-G | Objekt, Dokument und Frist | Hausverwaltung, Steuerkanzlei, Kanzlei |

### Felder je Datensatz

```
chunk_id, chunk_type, title, batch_id, source_strength,
content_origin, is_primary_evidence, process_type

betriebsart_buchstabe      "A"
worum_es_geht              2–3 Sätze: wie Arbeit hier fließt
typische_betriebe          Liste, 4–6
was_durch_den_betrieb_laeuft   das zentrale Objekt, z. B. "der Einsatz"
typische_kanaele           Liste, 4–8
wichtige_gegenstaende      Liste, 6–12 (Auftrag, Objekt, Beleg, …)
notwendige_angaben         Liste, 8–15
typische_uebergaben        Liste, 4–8: von wem an wen
typische_zustaende         Liste, 8–15
typische_ausnahmen         Liste, 8–15
engpasssignale             Liste, 6–12: woran man den Engpass erkennt
fachbegriffe               Liste, 15–30: die Wörter dieser Betriebsart
nicht_annehmen             Liste, 5–10: was man NICHT voraussetzen darf
```

**Vorlage vorhanden:** `knowledge/business_patterns/A_field_service.yaml` und
`E_orders_goods.yaml` haben genau diesen Aufbau. Übernimm sie inhaltlich, sie
sind gut. Fünf fehlen noch.

Das Feld `nicht_annehmen` endet in jedem Datensatz mit
`"dass KI die erste sinnvolle Lösung ist"`.

---

# Datei 2 · `02_diagnostic_patterns.jsonl` — 12 Datensätze

Was hinter einer Erzählung steckt. Diese Muster helfen dem Modell, vom Symptom
zur Ursache zu kommen.

`chunk_type`: `diagnostic_pattern`
`chunk_id`: `DP-01` bis `DP-12`

| ID | Muster |
|---|---|
| DP-01 | Fragmentierter Informationsfluss — dieselbe Sache liegt an mehreren Orten |
| DP-02 | Mehrfacherfassung — dieselbe Angabe wird mehrfach eingetippt |
| DP-03 | Wissen hängt an einer Person — nur eine weiß den Stand |
| DP-04 | Zuordnung geht verloren — Dokument und Vorgang finden nicht zusammen |
| DP-05 | Statusfrage kostet Zeit — die Antwort existiert, muss aber gesucht werden |
| DP-06 | Rückfrageschleifen — Angaben fehlen, es wird mehrfach nachgefragt |
| DP-07 | Medienbruch — von Papier zu Bildschirm und zurück |
| DP-08 | Fristenrisiko — Termine fallen erst auf, wenn sie knapp sind |
| DP-09 | Übergabeverlust — beim Wechsel zwischen Personen geht etwas verloren |
| DP-10 | Nachfassen unterbleibt — niemand ist dafür zuständig |
| DP-11 | Fertigung startet unvollständig — Arbeit beginnt, bevor alles da ist |
| DP-12 | Priorisierung fehlt — man sieht nicht, was zuerst dran ist |

### Felder je Datensatz

```
chunk_id, chunk_type, title, batch_id, … (Pflichtfelder)

muster_name                "fragmentierter_informationsfluss"
worum_es_geht              2–3 Sätze
signale_in_der_erzaehlung  Liste, 6–12 — wie Menschen es beschreiben,
                           in ihrer Sprache, nicht in Fachsprache
moegliche_ursachen         Liste, 3–6
was_es_kostet              2–3 Sätze, ohne Zahlen
gilt_besonders_fuer        Betriebsarten-Buchstaben
verwechselbar_mit          Liste anderer DP-IDs, die ähnlich aussehen
was_es_nicht_ist           2–3 Sätze — wann dieses Muster NICHT vorliegt
passende_loesungsfamilien  Liste von SF-IDs
klaerende_fragen           Liste, 3–5
```

**`signale_in_der_erzaehlung` ist das wichtigste Feld dieser Datei.** Danach
wird gesucht. Schreib dort, wie ein Betrieb es tatsächlich sagt — nicht
„fragmentierte Informationsflüsse", sondern „ich muss erst suchen, wo das
liegt".

`verwechselbar_mit` und `was_es_nicht_ist` verhindern, dass alles auf DP-01
gezogen wird.

---

# Datei 3 · `03_solution_families.jsonl` — 15 Datensätze

**Die wichtigste Datei des Batches.** Hier steht, welche größeren Lösungen es
gibt. Genau dieses Wissen fehlt heute.

`chunk_type`: `solution_family`
`chunk_id`: `SF-01` bis `SF-15`

| ID | Lösungsfamilie |
|---|---|
| SF-01 | E-Mail- und Nachrichtenverarbeitung |
| SF-02 | Vorgangs- und Fallmanagement |
| SF-03 | Dokumentenautomation |
| SF-04 | Daten- und Systemabgleich |
| SF-05 | Kundenservice-Assistent |
| SF-06 | Termin- und Buchungsautomation |
| SF-07 | Angebots- und Auftragsautomation |
| SF-08 | Rechnungs- und Finanzvorbereitung |
| SF-09 | Management-Übersicht |
| SF-10 | Kunden- und Partnerportal |
| SF-11 | Wissensassistent |
| SF-12 | Aufgaben- und Fristensteuerung |
| SF-13 | Marketing- und Inhaltsautomation |
| SF-14 | Website und Web-Anwendung |
| SF-15 | Sprach- und Telefonworkflow |

### Felder je Datensatz

```
chunk_id, chunk_type, title, batch_id, … (Pflichtfelder)

familie_name          "E-Mail- und Nachrichtenverarbeitung"
worum_es_geht         2–3 Sätze, ohne Fachsprache
geeignet_wenn         Liste, 5–10 — beobachtbare Bedingungen aus der
                      Erzählung, nicht Wünsche
nicht_geeignet_wenn   Liste, 3–6
bausteine             Liste, 4–8 — was die Familie enthält
braucht_capabilities  Liste von CAP-IDs
bleibt_beim_menschen  Liste, 2–5
setzt_voraus          Liste, 2–5 — was vorhanden sein muss
typische_kombination  Liste anderer SF-IDs, mit denen sie zusammen auftritt
reihenfolge_hinweis   1 Satz: kommt sie früh oder spät
kundennaher_name      wie es auf der Ergebnisseite heißen könnte —
                      **eine Formulierungshilfe, keine Vorgabe**
was_danach_im_betrieb_anders_ist
                      Liste, 3–5 — was der Betrieb merkt, nicht was
                      die Technik tut
gilt_fuer_betriebsarten  Buchstaben
```

**`was_danach_im_betrieb_anders_ist` ist die Brücke zur Ergebnisseite.** Ohne
dieses Feld muss das Modell die Übersetzung von „Fallmanagement" zu etwas
Verständlichem jedes Mal neu erfinden — und genau dabei entstehen die
technischen Formulierungen, die niemand versteht.

Beispiel für SF-02:

```json
"was_danach_im_betrieb_anders_ist": [
  "Der aktuelle Stand ist ohne Rückfrage sichtbar.",
  "Eine Vertretung kann einen Fall übernehmen.",
  "Später eintreffende Dokumente bleiben beim selben Vorgang.",
  "Offene nächste Schritte fallen auf, bevor jemand nachfragt."
]
```

Kein Werbetext. Nur, was im Betrieb tatsächlich anders wäre.

**`geeignet_wenn` entscheidet über die Qualität dieser Datei.** Schreib
beobachtbare Bedingungen, keine Wünsche.

Gut: „Nachrichten kommen über drei oder mehr Kanäle herein"
Schlecht: „Der Betrieb möchte effizienter arbeiten"

**`nicht_geeignet_wenn` ist genauso wichtig.** Ohne dieses Feld empfiehlt das
Modell jedem alles. Beispiel für SF-10 Portal: „weniger als etwa fünfzig
Kunden", „der Betrieb hat noch keinen verlässlichen internen Stand — dann gibt
es nichts zu zeigen".

`typische_kombination` ist das, was aus Einzelbausteinen ein System macht. Ohne
dieses Feld bekommst du wieder eine Liste statt eines Hubs.

---

# Datei 4 · `04_automation_capabilities.jsonl` — 12 Datensätze

Die technische Ebene darunter. Was ein System **können** muss.

`chunk_type`: `automation_capability`
`chunk_id`: `CAP-01` bis `CAP-12`

| ID | Fähigkeit |
|---|---|
| CAP-01 | Klassifikation — worum geht es in dieser Nachricht |
| CAP-02 | Informationsextraktion — Angaben aus Freitext ziehen |
| CAP-03 | Zusammenfassung |
| CAP-04 | Entitätszuordnung — welcher Kunde, welches Objekt, welcher Vorgang |
| CAP-05 | Dokumentenverständnis — PDF, Foto, Scan lesen |
| CAP-06 | Semantische Suche |
| CAP-07 | Entwurfserzeugung — Antwort oder Nachricht vorbereiten |
| CAP-08 | Änderungserkennung — was ist neu, was weicht ab |
| CAP-09 | Datenabgleich zwischen Systemen |
| CAP-10 | Weiterleitung — wer ist zuständig |
| CAP-11 | Menschliche Freigabe |
| CAP-12 | Auslöser und Aktion — was passiert automatisch, wann |

### Felder je Datensatz

```
chunk_id, chunk_type, title, batch_id, … (Pflichtfelder)

faehigkeit_name       "Entitätszuordnung"
worum_es_geht         2 Sätze
braucht_als_eingabe   Liste, 2–4
liefert               Liste, 1–3
zuverlaessigkeit      1–2 Sätze, ehrlich: wie gut geht das heute wirklich
typische_fehler       Liste, 2–5
menschliche_pruefung  "immer" | "bei Unsicherheit" | "stichprobenartig"
gehoert_zu_familien   Liste von SF-IDs
```

**`zuverlaessigkeit` und `typische_fehler` sind der Grund, warum diese Datei
existiert.** Sie hindern das Modell daran, Fähigkeiten zu versprechen, die
unzuverlässig sind. Bei CAP-04 gehört ausdrücklich hin, dass die Zuordnung
scheitert, wenn jemand von einer unbekannten Adresse schreibt oder mehrere
Objekte besitzt.

---

# Datei 5 · `05_target_architectures.jsonl` — 6 Datensätze

Verallgemeinerte Zielbilder. **Nicht** „Hausverwaltung bekommt einen Hub",
sondern: bei dieser Ausgangslage sieht ein tragfähiges System so aus.

`chunk_type`: `target_architecture`
`chunk_id`: `TA-01` bis `TA-06`

| ID | Zielbild |
|---|---|
| TA-01 | Eingang → Vorgang → Dokumente → Übersicht |
| TA-02 | Anfrage → Qualifizierung → Termin → Kundenakte |
| TA-03 | Auftrag → Einsatz → Nachweis → Rechnung |
| TA-04 | Bestellung → Vollständigkeit → Fertigung → Übergabe |
| TA-05 | Anfrage → Angebot → Freigabe → Projekt |
| TA-06 | **Ordnung und Bestandssystem vor neuer Technik** |

### Felder je Datensatz

```
chunk_id, chunk_type, title, batch_id, … (Pflichtfelder)

ausgangslage          3–5 Sätze: wann dieses Zielbild passt
ebenen                Liste von Objekten:
                        { ebene, was_dort_passiert, beteiligte_familien }
enthaltene_familien   Liste von SF-IDs
kleinste_fassung      2–3 Sätze: wie es für einen sehr kleinen Betrieb aussieht
groesste_fassung      2–3 Sätze: wie für einen mit vielen Mitarbeitenden
gilt_fuer_betriebsarten
passt_nicht_wenn      Liste, 3–5
```

**TA-06 ist der wichtigste Datensatz des ganzen Batches.** Er ist das
Alleinstellungsmerkmal von AI Start Map. Ohne ihn empfiehlt das System jedem
eine Lösung — und ist damit ein Verkaufstrichter statt einer Diagnose.

Er deckt **zwei** Fälle ab, und der zweite ist der, den man leicht übersieht:

**Fall 1 — Ordnung fehlt.** Arbeit läuft mündlich, auf Zetteln, in
persönlichen Notizen. Es gibt keine digitalen Daten zum Verbinden. Zusätzliche
Technik würde nur eine ungeklärte Arbeitsweise automatisieren.

**Fall 2 — Die Software ist da, wird aber nicht genutzt.** Der Betrieb hat
bereits ein System, das das Problem lösen könnte, nutzt es uneinheitlich oder
hat es nie richtig eingerichtet. Dann ist die richtige Antwort weder „erst
Papier digitalisieren" noch „ein neues System bauen", sondern: **das
Bestandssystem sauber nutzen.**

Fall 2 trifft auf sehr viele Betriebe zu — auch auf die Hausverwaltung mit
ihrer vorhandenen Verwaltungssoftware. Und es ist das stärkste
Vertrauenssignal, das dieses Produkt aussenden kann:

> „Ihr Problem lässt sich wahrscheinlich zuerst mit dem System lösen, das Sie
> bereits bezahlen."

Für TA-06:

- `ausgangslage`: beide Fälle beschreiben
- `ebenen`: was **vor** neuer Technik kommt — an einer Stelle sammeln,
  einheitliche Mindestangaben, gemeinsamer Status, und erst danach verbinden
- `enthaltene_familien`: **leer**
- `passt_nicht_wenn`: mehrere Personen brauchen bereits regelmäßig denselben
  digitalen Stand · wiederkehrendes Volumen erzeugt sichtbare Handarbeit ·
  digitale Daten und stabile Abläufe sind vorhanden

---

# Datei 6 · `06_source_register.csv`

Spalten wie in den vorhandenen Batches:

```
source_id,title,url_or_reference,accessed_on,source_strength,used_for_chunks
```

Für abgeleitete Muster ohne Fremdquelle:
`source_strength = derived`, `url_or_reference = interne Fallanalyse`.

---

# Prüfen, bevor du zufrieden bist

1. **Jede Zeile ist gültiges JSON.**
   `python -c "import json,sys; [json.loads(l) for l in open(f,encoding='utf-8') if l.strip()]"`
2. **Alle `chunk_id` sind eindeutig**, auch gegen den vorhandenen Bestand.
3. **Jeder `chunk_type` ist gesetzt.** Sonst bricht der Indexer ab.
4. **Jede SF-ID, die in `passende_loesungsfamilien` oder
   `braucht_capabilities` vorkommt, existiert auch.** Schreib dafür ein
   kleines Prüfskript — Querverweise ins Leere sind der häufigste Fehler in
   solchen Beständen.
5. **Kein Satz stammt wörtlich aus einem Testfall.**
6. **Keine Regel, keine Farbe, kein Werbetext.**

---

# Die Reihenfolge, wenn die Zeit knapp wird

Wenn du nicht alles schaffst, ist **Datei 3 die eine**, die zählt. Sie
schließt genau die Lücke, die wir gemessen haben.

1. `03_solution_families.jsonl` — ohne sie bringt der Rest wenig
2. `05_target_architectures.jsonl`, mindestens TA-06
3. `02_diagnostic_patterns.jsonl`
4. `04_automation_capabilities.jsonl`
5. `01_business_patterns.jsonl` — hier gibt es schon zwei fertige YAML-Dateien

Fünfzehn Lösungsfamilien mit je zehn Feldern sind ein Abend, wenn du sie
diktierst statt tippst.
