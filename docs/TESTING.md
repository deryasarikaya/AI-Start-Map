# Tests und Evaluation

## Die wichtigste Regel

```bash
pytest -q
```

**Läuft vollständig offline.** Kein Test macht einen echten OpenAI-Aufruf —
weder für ein Modell noch für eine Einbettung. Geprüft wird das nicht durch
Zusehen, sondern so:

```bash
OPENAI_API_KEY=ungueltig OPENAI_BASE_URL=http://127.0.0.1:9/v1 pytest -q
```

Ein unerreichbarer Endpunkt. Wenn die Suite grün bleibt, hat niemand gerufen.

Ein API-Schlüssel wird zum Testen nicht gebraucht. Eine PostgreSQL-Datenbank
schon — die Integrationstests fahren echte Routen gegen eine echte Datenbank.

---

## Wie das Offline-Bleiben erzwungen wird

In `tests/conftest.py` steht eine `autouse`-Vorrichtung, die für **jeden** Test
gilt:

| ersetzt | durch |
|---|---|
| `generate_diagnosis` | eine Diagnose aus einer Vorlage, mit Zitaten aus der jeweiligen Erzählung |
| `generate_target_architecture` | eine Auswahl, gebaut **aus dem echten Katalog** |
| `generate_result_part_two` | ein gültiger unterer Teil |
| `retrieve_solution_context` | ein leeres Ergebnis — sonst würde jeder Lauf einbetten |

Zwei Feinheiten, die dahinterstecken:

**Die Zitate werden aus der übergebenen Erzählung geschnitten**, nicht fest
eingetippt. Der Vertrag prüft sie wörtlich gegen genau diese Erzählung — eine
feste Attrappe würde die Prüfung aushebeln, die geprüft werden soll.

**Die Katalogauswahl der Attrappe kommt aus dem echten Katalog.** Ändert sich
die Freigabeliste, ändert sich die Attrappe mit. Eine fest eingetippte Kennung
würde irgendwann eine Familie behaupten, die es nicht mehr gibt.

---

## Was die Tests prüfen

| Bereich | Datei | worum es geht |
|---|---|---|
| **Der Vertrag** | `test_result_contract.py` | Zitate wörtlich, keine erfundenen Zahlen, keine Fachsprache, Grenzen nur selbstgesagt |
| **Die Entscheidung** | `test_decision_signals.py` | Signalspeicher, Belegkennungen, eine Entscheidung je kritischem Signal, übergangene Signale werden sichtbar |
| **Das Geländer** | `test_solution_catalog.py` | erfundene Kennungen, Module ohne Baustein, kein Katalogtreffer, vorhandene Software, zu viele Familien |
| **Die Hydration** | `test_solution_hydration.py` | dass die gewählten Familien wirklich geladen werden — und die ungewählten nicht |
| **Kleine Lösungen** | `test_small_and_no_tech_results.py` | ein Modul, keine Ansicht, kein System, keine neue Technik |
| **Die Teilung** | `test_second_call_split.py` | beide Hälften laufen, keine halben Ergebnisse |
| **Zuverlässigkeit** | `test_result_reliability.py` | Wiederholung nach schlechtem Zitat, Denkstufen, Zeitbudget |
| **Der Ablauf** | `test_analysis_flow.py`, `test_understanding_step.py` | Routen, Zwischenstand, höchstens zwei Runden |
| **Die Seiten** | `test_example_page.py`, `test_report_page.py`, `test_ux_journey.py` | Ergebnisseite, PDF, Rückfallebene |
| **Das Wissen** | `test_knowledge_hook.py`, `test_batch10_validator.py` | Abrufweg, Wissensprüfung, Zirkelschluss |
| **Die Messwerkzeuge** | `test_gold_lauf.py`, `test_zehn_laeufe.py` | dass die Messskripte messen, was sie behaupten |

Die Entscheidungsgruppe prüft eine Trennung, die leicht verwischt: Was in
sich nicht stimmt — eine erfundene Belegkennung, ein Einstieg auf einer
Familie, aus der nichts gebaut wird — **scheitert**. Was nur fehlt, wird
**sichtbar**, statt den Lauf mitzunehmen. Kein Test dort verlangt eine
bestimmte Lösungsfamilie; ein Test, der „Signal X also Familie Y“ prüfte,
wäre selbst die starre Zuordnung, gegen die der Katalogweg gebaut ist.

Die letzte Gruppe ist besonders: Sie prüft **Werkzeuge**, die im Kundenablauf
nie laufen. Ein Messskript, dessen Schalter nicht schalten, misst zweimal
dasselbe und sagt es nicht — deshalb hat es einen Trockenlauf.

---

## Evaluation — kostet Geld, läuft nur von Hand

Diese Skripte machen **echte** Modellaufrufe. Kein Test startet sie; sie laufen
nur, wenn jemand sie aufruft.

| Skript | was es tut | Kosten |
|---|---|---|
| `scripts/gold_lauf.py` | fährt die synthetischen Evaluationsfälle durch die Anwendung und vergleicht mit hinterlegten Erwartungen | 4 Aufrufe je Fall, mit Belegwiederholung 5 |
| `scripts/zehn_laeufe.py` | derselbe Fall zehnmal, für Zuverlässigkeit und Zeiten | 2 je Lauf |
| `scripts/pruefe_batch10.py` | prüft die Wissensdateien | **kostenlos**, liest nur |

Jedes dieser Skripte sagt im Kopf seiner Datei, was ein Durchgang kostet.
`gold_lauf.py` zählt seine Aufrufe mit — Wiederholungen eingeschlossen — und
hält vor einem Fall an, wenn ein gesetztes Budget nicht mehr reicht:

```bash
python scripts/gold_lauf.py --hoechstens 30
```

**Der Lauf wartet, bis wirklich gerechnet wurde.** Seit die Analyse im
Celery-Worker steckt, kommt `POST /analyze` sofort mit `state: processing`
zurück. Ein Runner, der danach weitermacht, fragt ein Ergebnis ab, das noch
niemand geschrieben hat — und schreibt dessen Abwesenheit als Messwert fort.
Deshalb schaltet `gold_lauf.py` Celery in den Sofortmodus: dieselbe Aufgabe,
derselbe Analyseweg, ein Prozess weniger. Nur so zählen Aufrufe und Laufzeit
überhaupt mit, denn beide sind in einem fremden Prozess unsichtbar.

Mit `--worker` läuft es über einen echten Worker und fragt den Stand ab wie
der Warteschirm. Das prüft den Weg, nicht die Kosten.

Neben jeder Messung liegt ein **Laufstempel** (`laufstempel.json`) mit Commit,
Prompt-, Vertrags-, Katalog- und Indexstand. Zwei Messungen mit
verschiedenen Stempeln sind nicht vergleichbar — auch dann nicht, wenn beide
grün sind:

```bash
python scripts/laufstempel.py
```

Das ist kein Luxus: In einem Lauf wurden 30 statt der geplanten 22 Aufrufe
verbraucht, weil jeder gescheiterte Aufruf einmal wiederholt wird und niemand
mitzählte.

---

## Die Evaluationsfälle

`knowledge/evaluation/gold/` enthält 13 **synthetische** Fälle. Sie sind
erfunden — keine echten Kundendaten. Je Fall: eine Erzählung und die
hinterlegte Erwartung.

Gemessen wird unter anderem:

| Kennzahl | Frage |
|---|---|
| Fehlstart-Quote | Steht als **erster Schritt** etwas, das dort nicht stehen darf? |
| Größentreffer | Passt die Zahl der Module zum Betrieb? |
| Startpunkt | Fängt die Lösung dort an, wo dieser Betrieb heute steht? |
| Belehrungsquote | Kommt ein Thema vor, zu dem der Betrieb nicht gefragt hat? |
| Abschreibquote | Wurde Wortlaut aus dem Abrufwissen übernommen? |
| Durchkommensquote | Wie viele Läufe liefern überhaupt ein Ergebnis? |

---

## Wie geprüft wird, dass nichts erfunden wird

Drei Sorten Test greifen ineinander:

**Der Vertrag** weist eine Antwort ab, die eine Kennung nennt, die es
nicht gibt — oder ein Modul, dessen Bausteine nicht zu seinen Familien
gehören. `test_solution_catalog.py` fährt genau diese Fälle.

**Der Pfad** prüft, dass die Prüfung auch stattfindet.
`test_solution_hydration.py` sieht nach, ob nach der Auswahl wirklich
geladen wird und ob die späteren Aufrufe nur das Gewählte sehen. Eine
Funktion, die es gibt und die niemand ruft, ist kein Geländer.

**Die Grösse** prüft, dass das Schema nichts erzwingt.
`test_small_and_no_tech_results.py` fährt den kleinen Fall: ein Modul,
keine Ansicht, kein neues System — und den Fall, in dem gar keine neue
Technik nötig ist.

## Offene Punkte, offen benannt

- **Die Durchkommensquote liegt nicht bei 100 %.** In der letzten Messung kamen
  8 von 11 Fällen durch; die Ausfälle waren Zeitabläufe beim vierten Aufruf.
  **Diese Zahl ist nicht mehr belastbar:** Der Runner wartete damals nicht
  auf den Worker. Sie wird mit dem reparierten Lauf neu erhoben.
  Die Ursache ist nicht bewiesen.
- **Die Größentreffer lagen bei 88 %** — das System liefert eher zu viele
  Module als zu wenige.
- **Eine Übernahme aus dem Abrufwissen wurde gemessen**, einmal in elf Fällen.
