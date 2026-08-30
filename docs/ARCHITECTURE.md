# Architektur

## Der Grundgedanke

Das System trennt zwei Dinge, die ein Sprachmodell von sich aus vermischt:

**Diagnose** — was ist bei diesem Betrieb los, woran liegt es, was ist Ursache
und was Symptom. Hier darf das Modell frei arbeiten, aber ausschließlich aus
dem, was der Betrieb selbst erzählt hat.

**Lösung** — was wird empfohlen. Hier darf das Modell nichts erfinden. Es wählt
aus einem freigegebenen Katalog, und der Server prüft die Auswahl.

Diese Trennung ist der Grund für den mehrstufigen Aufbau.

---

## Vier Modellaufrufe

| # | Aufruf | Prompt | Schema | was entsteht |
|---|---|---|---|---|
| 1 | Diagnose | `diagnose.md` | `Diagnose` | Engpass, Belege, Eckdaten, heutiger Ablauf, Rückfrage, Entscheidungsspeicher |

**Aufruf 1 sieht kein Lösungswissen.** Er bekommt die Erzählung, dazu
Betriebsarten und Diagnosemuster als Vergleichsmaterial — keine
Lösungsfamilien, keine Fähigkeiten, kein Zielbild. Wer die Lösung kennt,
diagnostiziert auf sie hin.

**Aufruf 2 sieht die Erzählung wieder.** Er bekam lange nur die Diagnose,
und der Prompt nannte sie „die einzigen Fakten über diesen Betrieb“.
Gemessen am Heizungsfall erreichten ihn damit 115 von 2.064 Wörtern — und
weil die späteren Aufrufe nur ausformulieren dürfen, was hier gewählt
wurde, kam nichts davon zurück. Der ausdrücklich genannte Hauptschmerz
überlebte in einem von drei Läufen.

Seit dem Informationsvertrag bekommt er:

| | |
|---|---|
| `SO_ERZAEHLT_ES_DER_BETRIEB` | die Erzählung im Wortlaut — die Quelle |
| `DIAGNOSE` | die fachliche Deutung — Priorisierungshilfe, nicht Ersatz |
| `LOESUNGSKATALOG` | alle freigegebenen Familien, je mit `braucht_capabilities`, `setzt_voraus`, `bleibt_beim_menschen` |
| `ABRUF_AUS_ERZAEHLUNG` | die breite Abrufsicht |
| `ABRUF_AUS_DIAGNOSE` | die enge Abrufsicht |
| `ENTSCHEIDUNGSSIGNALE` | die Punkte, an denen er nicht vorbeikommt |
| `BELEGSTELLEN` | die wörtlichen Zitate, auf denen sie stehen |

**Zwei Abrufsichten, weil eine nicht reicht.** Über drei Läufe desselben
Textes fand der Abruf auf der Erzählung dreimal dieselben sechs Familien,
der auf der Diagnose dreimal andere. Zwei davon — Portal und Kapazität —
wurden jedes Mal gefunden und kein einziges Mal gewählt.

Danach gemessen: dieselbe Auswahl in allen drei Läufen, Telefon von einem
auf drei Treffer, Portal von null auf drei.

**Und der Entscheidungsspeicher, weil Finden nicht Entscheiden ist.** Nach
der Breitensuche wurde die Morgenübersicht in drei von drei Läufen
gefunden und dem Planner angeboten. Gewählt wurde sie in null von drei —
und nirgends stand, dass sie nicht gewählt wurde. Ein Bedarf, den niemand
aufgeschrieben hat, kann auch niemand bewusst ablehnen; er verschwindet.

Deshalb schreibt Aufruf 1 zusätzlich auf, **was entschieden werden muss**,
und Aufruf 2 schreibt auf, **was er damit gemacht hat**:

```
wichtige Aussage  →  Beleg  →  Signal  →  Entscheidung
```

Ein Signal ist kein Betriebsmodell. Es entsteht nur, wo eine Antwort eine
Empfehlung, eine Grenze, eine Phase oder eine Nicht-Empfehlung verändern
würde — vier bis zehn Stück, davon zwei bis fünf kritisch. Die Erzählung
bleibt vollständig daneben stehen; der Speicher ersetzt sie nicht.

Die sechs möglichen Entscheidungen sind `start`, `target`, `future`,
`supporting`, `not_recommended` und `open`. **Fünf davon kosten keine
einzige zusätzliche Lösungsfamilie.** Das ist Absicht: Verlangt wird eine
Entscheidung, keine Empfehlung. Ein Vertrag, der für jedes Signal eine
Familie fordert, würde Empfehlungen erzwingen — genau das, wogegen der
Katalogweg gebaut ist.
| 2 | Zielarchitektur | `zielarchitektur.md` | `Zielarchitektur` | Katalogauswahl, Module, Name, Zielbild, künftiger Ablauf |
| 3 | Ansichten | `ergebnis_teil2a.md` | `ResultPartTwoViews` | Beispieloberflächen |
| 4 | Rest | `ergebnis_teil2b.md` | `ResultPartTwoRest` | Aufgabenteilung, Wert, Systeme, Umsetzung, Hebel |

Aufruf 3 und 4 waren einmal einer. Er hatte 65 Felder bei Schachtelungstiefe
acht und starb in fast der Hälfte der Läufe, während Aufruf 1 zehn von zehn
schaffte. Nach der Teilung kamen drei zuvor gescheiterte Fälle durch.

Zwischen Aufruf 1 und 2 liegt die Verstandenseite: Der Kunde sieht die
Diagnose, bevor die Lösung entsteht, und kann etwas ergänzen. Dann läuft
Aufruf 1 ein zweites Mal — höchstens einmal.

**Aufruf 1 hat eine Belegwiederholung.** Die Zitatprüfung im Vertrag sortiert
jedes Zitat einzeln aus, das nicht wörtlich in der Erzählung steht. Bleiben
danach weniger als zwei übrig, fragt der Server genau einmal nach — mit den
abgelehnten Zitaten im Prompt, damit das Modell weiß, woran es lag. Hilft auch
das nicht, entfällt der Belegabschnitt und die Seite entsteht trotzdem. Einen
dritten Aufruf gibt es nie.

---

## Wissen ist nicht gleich Wissen

Zwei Sorten, die nie vermischt werden:

| | was | wer sieht es |
|---|---|---|
| **Diagnosewissen** | Betriebsarten, Engpassmuster | Aufruf 1 |
| **Lösungswissen** | Familien, Fähigkeiten, Zielbilder | erst Aufruf 2, und danach nur das Gewählte |

Ein abgerufener Abschnitt ist **nie** ein Beleg über den Kunden. Was über
ihn gesagt wird, steht in seiner Erzählung; die Zitatprüfung erzwingt das.

```
Kundenfakt / bestätigter Ablauf   →  Diagnose      ✓
abgerufener Abschnitt             →  Kundenfakt    ✗
```

Und die Rollenverteilung im Lösungsteil:

```
Abruf    = Rangfolge
Katalog  = erlaubte Menge
Modell   = Auswahl und Formulierung
Server   = Prüfung
```

## Der Weg durch den Code

```
POST /interview   interview_service     Erzählung ablegen
POST /analyze     analysis_service      run_first_call
                    → openai_service    generate_diagnosis            Aufruf 1
                    → repository        Zwischenstand speichern
GET  /verstanden  routes                Diagnose zeigen
POST /verstanden  process_service       weiter oder ergänzen
POST /analyze     analysis_service      run_second_call
                    → rag_service       vorgeschlagene_familien       (Einbettung)
                    → openai_service    generate_target_architecture  Aufruf 2
                    → result_schema     Kennungen und Bausteine prüfen
                    → solution_catalog  vollstaendig() · faehigkeiten_zu()
                                        zielbild_zu()   ← erst jetzt
                    → openai_service    generate_result_part_two      Aufruf 3+4
                    → repository        Ergebnis speichern
GET  /results     routes                Ergebnisseite
GET  /report      routes                Druckansicht fürs PDF
```

`/beispiel/hausverwaltung` zeigt einen gespeicherten Lauf ohne jeden
Modellaufruf — die Rückfallebene für eine Vorführung.

Die Nutzerstrecke vor der Ergebnisdarstellung teilt sich eine semantische
visuelle Foundation, ohne in diesen Datenfluss einzugreifen. Tokens,
Komponentenmuster, Zuständigkeiten und die Übergabe an eine spätere Results V1
stehen in [`PRE_RESULTS_UI_FOUNDATION.md`](PRE_RESULTS_UI_FOUNDATION.md).

---

## Der Vertrag

`app/result_schema.py` beschreibt jede Modellantwort als Pydantic-Modell. Das
ist mehr als eine Typprüfung: In den Validatoren steckt, was der Kunde nie zu
sehen bekommen darf.

| Prüfung | was sie verhindert |
|---|---|
| Zitate wörtlich | `verstanden.belege` müssen Zeichen für Zeichen in der Erzählung stehen. Wer umformuliert, fliegt raus — einzeln, nicht als ganze Antwort |
| Hebel belegt | `hebel[].woraus` muss ebenfalls wörtlich dastehen |
| Katalogtreue | jedes Modul auf eine freigegebene Familie **und** einen ihrer Bausteine zurückführbar |
| keine Fachsprache | eine Wortliste, die im Kundentext nicht vorkommen darf |
| keine internen Kennungen | Fall-, Muster-, Datei- oder Chunk-Namen |
| keine Zeit- oder Geldersparnis | weder in Zahlen noch in Worten — sie wären erfunden |
| Grenzen nur selbstgesagt | eine Einschränkung darf nur stehen, wenn der Betrieb sie genannt hat |
| Belegkennungen echt | ein Signal darf sich nur auf eine Belegstelle berufen, die es gibt |
| eine Entscheidung je Signal | jedes Signal genau einmal in der Abdeckung, nicht nur die kritischen |
| Einstieg wird gebaut | `start` nur auf Familien, aus denen auch ein Modul entsteht |
| Nicht-Empfehlung begründet | `not_recommended` braucht einen tragenden Grund, nicht „passt nicht“ |

**Warum jedes Signal und nicht nur die kritischen.** Der erste Entwurf
verlangte eine Entscheidung nur bei `critical`. Gemessen am Heizungsfall
stufte das Modell daraufhin genau die Themen, um die es geht —
Morgenübersicht, Kapazitätsgrenze, Wissen in Köpfen — als nicht kritisch
ein, und sie fielen wieder lautlos heraus. „Nicht kritisch“ war der neue
stille Papierkorb. Ein Signal entsteht ohnehin nur dort, wo eine Antwort
die Empfehlung verändern könnte; wer es aufschreibt, entscheidet es.
`critical` sagt seither nur noch, wie schwer eine Lücke wiegt.

**Eine Ausnahme, und sie ist bewusst.** Ein Signal, das der Planner
übergangen hat, lässt den Lauf **nicht** scheitern. Daran ist die
Antwort nicht falsch, sondern unvollständig — und ein Kunde soll wegen
einer fehlenden internen Zeile keine Fehlermeldung sehen. Der Server trägt
die Lücke als `open` nach und schreibt die Kennung in
`coverage.uncovered_critical_signal_ids`.

Diese Liste ist die eigentliche Messung: Der nachgetragene Eintrag sorgt
dafür, dass nichts still verschwindet, die Liste daneben sagt, wie oft der
Planner es selbst nicht geschafft hat. Ohne sie wäre „jedes Signal hat
eine Entscheidung“ eine Zahl, die der Server sich selbst schenkt.

Ein Verstoß führt zu einem zweiten Versuch mit Hinweis. Kommt auch der nicht
sauber zurück, entsteht **kein** Ergebnis — es gibt keinen Rückfall auf
Beispieldaten.

---

## Datenmodell

| Tabelle | Inhalt |
|---|---|
| `analysis_sessions` | eine Sitzung, ihre Erzählung, ihr Zustand |
| `interview_questions` | gestellte Rückfragen und Antworten |
| `partial_results` | die Diagnose zwischen Aufruf 1 und 2 |
| `results` | das fertige Ergebnis als JSON |

Der Zwischenstand ist eine eigene Tabelle, weil der Kunde die Verstandenseite
neu laden können muss, ohne dass ein Modellaufruf erneut Geld kostet.

---

## Wissensschichten

```
knowledge/
├── catalog/FREIGABE.json          welche Lösungsfamilien empfohlen werden dürfen
├── candidates/batch_10/           Betriebsarten · Diagnosemuster · Familien ·
│                                  Fähigkeiten · Zielbilder
├── business_patterns/             Betriebsarten für das Interview
├── runtime/                       Rückfragemuster, Lösungsabläufe
├── examples/                      ein gespeicherter Lauf ohne Modellaufruf
└── evaluation/gold/               synthetische Fälle für die Regression
```

Der Unterschied zwischen `candidates/batch_10/` und `catalog/FREIGABE.json` ist
wichtig: Die erste Datei ist der **Bestand**, die zweite die **Erlaubnis**. Eine
Familie kann im Bestand liegen und trotzdem nicht empfohlen werden.

Mehr dazu in [`SOLUTION_CATALOG.md`](SOLUTION_CATALOG.md) und [`RAG.md`](RAG.md).

---

## Was bewusst nicht drin ist

- **Kein Frontend-Framework.** Serverseitig gerendertes HTML, eine CSS-Datei.
  Das Produkt ist eine Seite, die jemand einmal liest.
- **Kein Rückfall auf Beispieldaten.** Scheitert ein Aufruf, zeigt die Seite
  einen sichtbaren Hinweis. Ein halbes Ergebnis wäre schlimmer als keins.
- **Keine Agentenschleife.** Feste Reihenfolge, gedeckelte Wiederholungen. Was
  wie viel kostet, ist vorher bekannt.
