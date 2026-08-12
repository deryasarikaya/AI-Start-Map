# Branchenwissen — sieben Betriebsarten

## Warum nicht dreißig Dateien

Ein Malerbetrieb und ein Elektrobetrieb haben denselben Informationsfluss:
Anfrage kommt rein, Termin, vor Ort passiert etwas, Fotos und Material fallen
an, oft kommt Zusatzarbeit dazu, am Ende die Rechnung. Die Begriffe
unterscheiden sich, der Ablauf nicht.

Ein Friseur und ein Kosmetikstudio sind derselbe Fall. Ein Coach und ein
Berater auch. Ein Blumenladen und ein kleiner Onlinehandel weitgehend.

Deshalb: **sieben Betriebsarten, sieben Wissensdateien.** Jeder Beruf wird
einer Art zugeordnet. Neue Berufe kommen später dazu, ohne dass eine neue
Datei entsteht.

Das entspricht auch der Vorgabe aus dem Mentorengespräch: Workflows werden
nicht an einzelne Berufe gebunden.

---

## Die sieben Arten

### A — Einsatz beim Kunden

Dachdecker · Elektriker · Maler und Lackierer · Sanitär, Heizung, Klima ·
Reinigungsfirma · Hausmeisterservice · Gartenpflege · mobiler Reparaturdienst

**Ablauf:** Anfrage → Termin → vor Ort → Sprache, Fotos, Material → oft
Zusatzarbeit → Rechnung

**Typische Reibung:** Was vor Ort passiert ist, wird unterschiedlich gut
festgehalten. Belege und Fotos bleiben auf dem Handy. Zusatzarbeit fällt erst
beim Rechnungschreiben auf, oder gar nicht.

---

### B — Werkstatt mit Kundengegenstand

KFZ-Werkstatt · Fahrradwerkstatt · Schuhmacher · Schneiderei ·
Reparaturservice

**Ablauf:** Annahme → Gegenstand kennzeichnen → Befund → Freigabe für Mehrarbeit
→ fertig → Abholung → Zahlung

**Typische Reibung:** Der Gegenstand ist da, aber die Zuordnung zum Auftrag
und der reale Ablageort sind es nicht. Rückfragen zu Mehrarbeit bleiben
unbeantwortet, die Arbeit läuft trotzdem weiter.

**Hinweis:** Bei dieser Art muss oft zuerst eine Kennzeichnung entstehen,
bevor KI hilft. Das ist der ehrliche Ausgang — nicht der Regelfall, aber hier
häufiger als anderswo.

---

### C — Termin- und Teilnehmerbetrieb mit wiederkehrender Leistung

Friseur · Kosmetik · Massage · Fitnessstudio · Fahrschule · Physiotherapie ·
mobile Fußpflege

**Ablauf:** Anfrage → Termin → Erinnerung → Durchführung → Nachsorge →
Wiederbuchung

Der Name ist bewusst länger als „Terminbetrieb". Bei Fitnessstudio und
Fahrschule geht der Lebenszyklus deutlich über den einzelnen Termin hinaus —
Anmeldung, Aktivität, Inaktivität, Reaktivierung, Prüfung, Abschluss. Wer hier
nur den Kalender sieht, übersieht den größeren Teil der Arbeit.

**Typische Reibung:** Terminwünsche kommen über mehrere Kanäle und müssen von
Hand gegen den Kalender geprüft werden. Ausfälle und Verschiebungen kosten
Zeit. Wiederkehrende Kunden werden nicht systematisch zurückgeholt.

---

### D — Auftrag mit Briefing und Freigaben

Fotograf · Architekturbüro · Designer · kleine Agentur · Freelancer ·
Videograf · Texter

**Ablauf:** Anfrage → Angebot → Briefing → Arbeit → Änderungswünsche →
Freigabe → Rechnung

**Typische Reibung:** Wünsche und Änderungen kommen über Wochen und über
mehrere Kanäle. Welche Fassung gerade gilt und was schon freigegeben ist,
steht nirgends zusammen. Zusagen sind später strittig.

---

### E — Bestellung und Ware

Blumenladen · Konditorei · Einzelhandel · kleiner Onlinehandel ·
Schmuckherstellung · Manufaktur · Catering

**Ablauf:** Bestellung über mehrere Kanäle → Vorbereitung → Abholung oder
Lieferung → Zahlung → Nachbestellung

**Typische Reibung:** Bestellungen kommen über fünf Wege und laufen nirgends
zusammen. Angaben fehlen und fallen erst beim Vorbereiten auf. Fotos und
Sonderwünsche liegen getrennt vom Auftrag.

---

### F — Gespräch als Leistung

Coach · Mentor · Berater · Trainer · Kundenbetreuung · virtuelle Assistenz

**Ablauf:** Anfrage → Termin → Vorbereitung → Gespräch → Notiz → Aufgaben →
Nachfassen

**Typische Reibung:** Vor jedem Termin muss zusammengesucht werden, was beim
letzten Mal war. Interessenten, die sich nicht mehr melden, gehen verloren.
Notizen liegen in drei Programmen.

---

### G — Objekte, Verträge und Fristen

Hausverwaltung · WG-Verwaltung · Immobilienmakler · KFZ-Gutachter ·
Vermietung · Ferienwohnung · Gerätevermietung

**Ablauf:** Meldung oder Anfrage → Objekt zuordnen → Dokument oder Gutachten →
Frist → Abrechnung oder Bericht

**Typische Reibung:** Meldungen kommen von vielen Seiten und müssen dem
richtigen Objekt zugeordnet werden. Dokumente liegen verstreut. Fristen und
wiederkehrende Termine hängen im Kopf einer Person.

---

## Was in jede Wissensdatei gehört

Vierzehn Felder. **Keine Prompts, keine Marketingtexte, keine
Lösungsempfehlungen.** Dateiformat YAML, Ablage in
`knowledge/business_patterns/`.

```
business_pattern              Kennung, z.B. E_orders_goods
business_example              ein typischer Vertreter, z.B. Blumenladen

typical_workflows             die übliche Kette vom Eingang bis zum Abschluss
channels                      worüber Anfragen und Aufträge hereinkommen
domain_vocabulary             die Gegenstände und Wörter des Gewerbes
important_entities            was in dieser Arbeit miteinander verbunden wird
required_information          was in einem Vorgang drinstehen muss
typical_handoffs              wo etwas von einer Stelle zur nächsten geht
typical_statuses              die Zustände, die ein Vorgang durchläuft
typical_bottlenecks           wo es erfahrungsgemäß klemmt
typical_exceptions            was regelmäßig anders läuft als der Normalfall
realistic_customer_language   wie Kunden dieser Art wirklich schreiben
realistic_worker_language     wie Mitarbeiter berichten, wo das relevant ist
diagnostically_relevant_questions   Fragen, die diesen Ablauf aufschließen
diagnostic_signals            woran man den Engpass äußerlich erkennt
do_not_assume                 was man über diese Betriebsart NICHT annehmen darf
diagnostic_focus              die eine Frage, auf die das Modell zusteuert
```

`realistic_worker_language` bleibt leer, wo es keine Rolle spielt — bei einem
Ladengeschäft etwa. Bei Betriebsart A ist es der wichtigere der beiden
Sprachblöcke, weil dort die Sprachnotiz des Mitarbeiters der eigentliche
Eingang ist, nicht die Kundennachricht.

### Die vier wichtigsten davon

**`beispielnachrichten`.** Die erfundene Nachricht im Ergebnis war zu perfekt,
weil das Modell nicht weiß, wie Kunden einer Branche tatsächlich schreiben.
Zwei bis drei echte Muster pro Betriebsart lösen das direkt.

**`begriffe`.** Daraus entsteht der Unterschied zwischen „Vorgangsübersicht"
und „Straußgröße".

**`wichtige_objekte`.** Das ist das Datenmodell des Gewerbes — woraus ein
Vorgang in dieser Welt besteht. Beispiel Werkstatt:

```
Kunde · Fahrzeug · Kennzeichen · Auftrag · Reparatur · Ersatzteil ·
Freigabe · Standort · Status
```

Ohne dieses Wissen weiß das Modell nicht, was es überhaupt zusammenführen
soll.

**`typische_uebergaben`.** Das ist die Landkarte der Stellen, an denen
Information verloren geht — also genau das, wonach die Diagnose sucht.
Beispiel Einsatz beim Kunden:

```
Kunde → Büro → Mitarbeiter → Einsatz → Dokumentation → Rechnung
```

### `do_not_assume` — die wirksamste Bremse

Das Feld sagt ausdrücklich, was man über diese Betriebsart **nicht** annehmen
darf: dass ein Onlineshop existiert, dass geliefert wird, dass eine
Rechnungssoftware vorhanden ist, dass mehrere Mitarbeiter da sind, dass KI
überhaupt die richtige Antwort ist.

Das ist wirksamer als jede Verbotsliste, weil es den eigentlichen Fehler
adressiert: Das Modell füllt Lücken mit Plausiblem. Ein Satz, der sagt „das
weißt du nicht", verhindert genau das.

Jede Datei muss den Eintrag „dass KI die erste sinnvolle Lösung ist"
enthalten.

### Welches Feld geht an welchen Aufruf

Nicht alles gehört in jeden Prompt. Die Dateien sind umfangreich, und das
Zeitbudget der Endanalyse ist ohnehin knapp.

| Feld | Interview | Endanalyse |
|---|---|---|
| `typical_workflows` | ja | ja |
| `channels` | ja | ja |
| `diagnostic_signals` | ja | ja |
| `diagnostic_focus` | ja | ja |
| `do_not_assume` | ja | ja |
| `diagnostically_relevant_questions` | ja | nein |
| `typical_exceptions` | ja | nein |
| `required_information` | ja | nein |
| `domain_vocabulary` | nein | ja |
| `important_entities` | nein | ja |
| `typical_statuses` | nein | ja |
| `typical_handoffs` | nein | ja |
| `realistic_customer_language` | nein | ja |
| `realistic_worker_language` | nein | ja |
| `typical_bottlenecks` | nein | ja |

### Vokabular ist kein Inhaltsverzeichnis

Regel für den Prompt:

```
Verwende aus domain_vocabulary nur Wörter, die zum tatsächlich beschriebenen
Fall passen. Die Liste ist kein Inhaltsverzeichnis, das abgearbeitet wird.

Falsch wäre, bei einer Kundin, die von Sträußen und Lieferadressen erzählt
hat, plötzlich von Gestecken, Trauerbinderei und Saisonblumen zu schreiben.
```

### Die Schutzregel

> **Branchenwissen sagt dem Modell, worauf es achten kann. Nicht, welche
> Lösung der Betrieb braucht.**

Kein Eintrag in diesen Dateien darf eine Empfehlung enthalten. Nicht
„Dachdecker sollten die Schadendokumentation automatisieren", sondern
„bei Schäden fallen typischerweise an: Schadenart, Ursache, Ausmaß, Fotos,
Maßreferenz".

Was tatsächlich der Fall ist, sagt allein der Kunde. Das Branchenwissen ist
Vergleichswissen, nie Nutzerfakt.

---

## Wie es angeschlossen wird

Der Betriebstyp wird bereits vom Modell als freier Text bestimmt (siehe
`ERGEBNIS_SPEC.md` und die vorhandene `business_type`-Verkabelung). Dieser
Text wird auf eine der sieben Arten abgebildet. Die zugehörige Datei geht als
Kontext in die Endanalyse.

Passt keine Art eindeutig, wird **keine** Datei geladen. Dann arbeitet das
Modell nur mit der Erzählung — das ist besser als das Vokabular einer fremden
Betriebsart.

Die vorhandenen Batch-09-Workflows behalten ihren eigenen `business_type` und
bleiben unverändert. Das Branchenwissen ergänzt sie, es ersetzt sie nicht.

---

## Herkunft der Inhalte

Selbst geschrieben. Fremde Prompt-Sammlungen und Anbieterinhalte dürfen als
Anhaltspunkt dienen, welche Themen in einer Branche vorkommen — Formulierungen
werden nicht übernommen, und fertige Lösungssprünge der Art „Branche X →
Werkzeug Y" schon gar nicht.

**Wo fremde Quellen tragen und wo nicht.** Eine Auswertung der verfügbaren
Anbieterinhalte hat ergeben: Brauchbares Prozessmaterial gibt es zu
Autowerkstatt, Hausverwaltung, KFZ-Gutachter, Architekturbüro, Fotograf,
Elektriker, Dachdecker, SHK, Maler, Reinigung, Friseur, Kosmetik, Fitness,
Fahrschule.

**Nicht abgedeckt:** Blumenladen, Hausmeisterservice, Schuhmacher,
Fahrradwerkstatt, Massage, Schmuckherstellung, Konditorei, Agentur,
Freelancer, Mentor.

Ausgerechnet zwei der drei Testfälle — Blumenladen und Hausmeisterservice —
fallen in die zweite Gruppe. Diese Inhalte entstehen aus den vorhandenen
Erzählungen, den Batch-09-Workflows und eigener Recherche. Sie dürfen nicht
aus einer Nachbarbranche hochgerechnet und dann als belegt behandelt werden.

---

## Umfang und Reihenfolge

Sieben Dateien. Zuerst die drei, für die es bereits Testfälle gibt:

1. **E — Bestellung und Ware** (Blumenladen)
2. **A — Einsatz beim Kunden** (Hausmeister, Elektrobetrieb)
3. **D — Auftrag mit Briefing** (Fotograf)

Die übrigen vier danach. Erst wenn diese drei nachweislich bessere Ausgaben
erzeugen, lohnt sich der Rest.
