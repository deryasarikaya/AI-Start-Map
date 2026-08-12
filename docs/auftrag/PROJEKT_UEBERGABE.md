# AI Start Map — Projektübergabe

Lies das hier zuerst, bevor du irgendetwas änderst.

---

## 1. Was das Projekt ist

**AI Start Map** ist ein Diagnosewerkzeug für kleine Betriebe. Ein Betrieb
erzählt in eigenen Worten, wie sein Arbeitsalltag abläuft — gesprochen oder
geschrieben. Am Ende bekommt er eine Auswertung: das ist dein Engpass, das ist
der eine sinnvolle erste KI-Schritt, so würde es danach laufen, so sieht das
Ergebnis aus, das prüfst du weiterhin selbst.

Es ist Deryas Masterschool-Abschlussprojekt und gleichzeitig der Prototyp für
ihre spätere Beratungstätigkeit.

**Zielgruppe:** Betriebe mit 1 bis 10 Personen, die **schon digital arbeiten**,
aber nichts automatisiert haben. Ihre Informationen liegen verstreut über
WhatsApp, Instagram, E-Mail, Fotos, Sprachnachrichten, Kalender und Tabellen.
Blumenladen, Hausmeisterservice, Fotograf, Coach, kleine Werkstatt.

**Nicht die Zielgruppe:** Betriebe ohne jede Digitalisierung. Das war eine
frühere Annahme und ist widerlegt.

### Das Grundprinzip — daran hängt alles

1. **Bei dem anfangen, was der Betrieb schon hat.** Keine neue App, kein neues
   System, nichts Neues lernen.
2. **Fehlende Voraussetzungen ehrlich benennen**, statt sie stillschweigend
   vorauszusetzen.
3. **Wenn KI hier noch nicht hilft, das sagen.** Das ist eine gültige und gute
   Antwort, keine Niederlage.

Beispiel für Punkt 2 und 3: Eine Floristin nimmt Bestellungen auch telefonisch
an und schreibt dabei nichts oder nur auf einen Zettel. Falsche Antwort wäre
„die KI sammelt alle deine Bestellungen ein" — ein Telefongespräch, das nirgends
festgehalten wurde, kann sich keine KI später holen. Richtige Antwort: „Für
Anrufe brauchst du zuerst eine feste kleine Gewohnheit: nach dem Gespräch drei
Sätze in denselben Eingang. Danach funktioniert der Rest."

Dasselbe beim Fotografen, dessen Dateiversionen keine erkennbaren Namen haben,
oder beim Hausmeister, bei dem nicht erkennbar ist, zu welchem Auftrag ein Bon
gehört. **Die fehlende Voraussetzung liegt fast immer darin, dass etwas gar
nicht erst festgehalten wird — nicht in fehlender Technik.**

### Der Qualitätsmaßstab

Der Betrieb liest die Auswertung und denkt nach 30 bis 60 Sekunden:

> „Ah, jetzt verstehe ich genau, was das für mich machen würde."

Nicht: „Was ist eine Vorgangsakte?" — nicht: „Was heißt Felder extrahieren?"

Der Kunde weiß nicht, wie man eine gute Frage an eine KI stellt. Er kennt weder
die Begriffe noch weiß er, wonach er suchen soll. Er kann nur sein Chaos
erzählen. Das Werkzeug formuliert die Frage für ihn und liefert die Antwort,
die er bekommen hätte, wenn er gewusst hätte, wie man fragt.

---

## 2. Stack und Betrieb

- Python, FastAPI, Jinja2-Templates, PostgreSQL, SQLAlchemy 2.x, Alembic
- Pydantic v2 für alle Modelle
- OpenAI mit Structured Outputs (`chat.completions.parse`)
- FAISS für Retrieval (`IndexFlatIP` + `normalize_L2`)
- pytest, aktuell 214 Tests grün

**Branch:** `feature/gate-cascade-quality`
**Letzter Commit:** `a811726 Fix pattern selection and make results concrete`

Tests laufen mit `python -m pytest -q` (`pytest.ini` setzt `pythonpath = .`).

---

## 3. Wo was steht

### `app/` — die Anwendung

| Datei | Zeilen | Was drin ist |
|---|---|---|
| `routes.py` | 2796 | **Alle HTTP-Routen — und viel zu viel mehr.** Datenbankzugriffe, Ablauflogik, Kundentext-Aufbereitung. Siehe Abschnitt 6. |
| `openai_service.py` | 966 | Alle OpenAI-Aufrufe, Prompts, Structured Outputs, Timeouts, Grounding-Prüfungen |
| `rag_service.py` | 872 | FAISS-Indizes, Embeddings, Retrieval |
| `agent_service.py` | 777 | Agentenentscheidung: ASK, CLARIFY, RETRIEVE, ANALYZE, STOP — heute regelbasiert, nicht modellbasiert |
| `schemas.py` | 768 | Pydantic-Modelle, u.a. `FinalAnalysisResult` |
| `recommendation_service.py` | 669 | Katalog laden und validieren, Gate-Kaskade, Musterauswahl (`select_recommendation`) |
| `solution_knowledge.py` | 392 | Batch-09-Workflows und Output-Strukturen laden |
| `llm_classification.py` | 298 | Problemfamilien-Klassifikation per LLM |
| `models.py` | 155 | SQLAlchemy-Tabellen |
| `questions.py` | 114 | Fragenlogik |
| `main.py` | 41 | App-Einstieg |

### `app/templates/` — die Strecke in Reihenfolge

```
landing.html          Startseite
interview_start.html  "Erzähl mir, wie es bei dir läuft" (Text oder Sprache)
interview_saved.html  Zwischenseite
process_options.html  erkannte Abläufe zur Auswahl
process_confirm.html  "So habe ich deinen Ablauf verstanden" — bestätigen
process_details.html  Details
follow_ups.html       Rückfragen (0 bis 3)
processing.html       Warteseite während der Analyse
results.html          die Auswertung
report.html           Druckansicht / PDF
```

### `knowledge/` — das Fachwissen

```
runtime/                          wird vom Produkt direkt geladen
  recommendation_catalog.json     12 Problemfamilien PF-01..12,
                                  10 Solution Patterns SP-01..10,
                                  Zuordnungsmatrix, 9 GenAI-Fähigkeiten,
                                  6 Gates, 12 Fehlermuster, Autonomiestufen A0-A5
  output_structures.jsonl         10 Ergebnisstrukturen mit Beispielwerten
  solution_knowledge/
    solution_workflows.jsonl      28 Workflows, mit business_type
  patterns/
    next_question_patterns.jsonl  40 Fragevorlagen
    inference_patterns.jsonl      27 Hypothesenmuster

candidates/                       geprüft, aber noch keine Runtime-Quelle
evaluation/                       Testfälle — NIEMALS indexieren
archive/                          alte Recherchebatches 02-08
```

### `docs/`

Wichtig zum Einlesen:
- `PROJECT_STATE.md` — aktueller Implementierungsstand
- `DECISIONS.md` — getroffene Architekturentscheidungen
- `KNOWN_ISSUES.md` — bekannte Probleme
- `ARCHITECTURE.md` — Aufbau
- `CHANGELOG.md` — was wann geändert wurde

Historisch, nicht mehr aktuell: `BRIEFING_ZWEITMEINUNG.md`,
`CODE_REVIEW_2026-08-06.md`, `RESEARCH_BATCHES_05_08_INTEGRATION.md`.

### `scripts/`

- `evaluate.py` — Messschleife über die Evaluationsfälle
- `build_index.py` — FAISS-Indizes bauen
- `merge_catalog_v2.py`, `promote_batch09_runtime.py` — einmalige Datenaufbereitung

---

## 4. Der fachliche Ablauf

```
Erzählung (Text oder Sprache)
  → Prozesse erkennen, Nutzer wählt einen
  → Ist-Ablauf zusammenfassen, Nutzer bestätigt
  → 0 bis 3 Rückfragen
  → Problemfamilien klassifizieren (LLM)
  → Gate-Kaskade auswerten
  → Kandidaten filtern und ausschließen
  → Rangfolge unter zulässigen Kandidaten (LLM)
  → Endanalyse: Kundentext erzeugen
  → Ergebnisseite + PDF
```

**Grundregel für die Aufgabenteilung:** Sicherheitsentscheidungen bleiben in
Python — Gates, Ausschlüsse, Autonomiedeckel, Freigabegrenzen. Das Modell
entscheidet fachliche Reihenfolge und formuliert. Es hebt nie einen Ausschluss
auf.

---

## 5. Was funktioniert — nicht anfassen

- **Interview und Prozesserkennung.** Der erkannte Ist-Ablauf ist inhaltlich
  präzise und stammt nachweislich aus der Erzählung. Das ist die beste Stelle
  im ganzen Produkt.
- **Musterauswahl.** Seit Commit `a811726` gibt es eine echte fallbezogene
  Rangfolge statt `allowed[0]`. Der Blumenladen bekommt jetzt SP-01, der
  Hausmeister SP-03, der Fotograf SP-02, und Belegfälle nicht mehr SP-04.

**Hinweis zu SP-04 (Gegenstand und Ablageort):** Dieses Muster stammt aus einer
früheren, verworfenen Zielgruppe — Betriebe, die physische Kundengegenstände
lagern und nicht digital arbeiten. Es bleibt im Katalog, ist aber **kein
Demofall und kein Testanker mehr**. Der Gegenstands-Gate muss weiterhin
verhindern, dass Belege, Bons oder Notizen fälschlich als Kundengegenstand
gelten — das war die Ursache eines echten Fehlers.
- **Fehlerverhalten.** Bei API-Ausfall kommt eine sichtbare Fehlerseite statt
  eines stillen Rückfalls auf die alte Stichwortlogik.
- **Rückfragen.** Die Substring-Heuristiken sind entfernt. Der
  Blumenladen-Fall erzeugt null Rückfragen.

---

## 6. Was kaputt ist

### Das aktuelle Hauptproblem: die Kundentext-Erzeugung

Die Empfehlung ist inzwischen richtig — der Text darüber ist es nicht. Beispiel
aus einem echten Lauf (Fotograf):

```
Wer kümmert sich    12.09.2026
Bis wann            12.09.2026
Das fehlt noch      Wer kümmert sich (Verantwortliche Person fehlt)
```

Ein Datum im Feld für eine Person. Derselbe Wert zweimal. Dasselbe Feld
gleichzeitig ausgefüllt und als fehlend markiert.

**Ursache** — nachgeprüft in `app/openai_service.py` ab Zeile 598:

```python
value = existing.get(label.casefold(), "")
if not value and field_index < len(result.sample_output.fields):
    value = result.sample_output.fields[field_index].value
```

Das Modell schreibt eigene Felder mit eigenen Beschriftungen. Danach werden sie
in die Beschriftungen aus `output_structures.jsonl` umgeschrieben: zuerst über
den Namen, und **wenn der nicht passt, über die Position**. So landete
„12.09.2026" unter „Wer kümmert sich" — es war zufällig das vierte Feld. Es ist
also keine Pflichtfeld-Erzwingung, sondern eine positionsbasierte Zuordnung.
`Wer kümmert sich` ist in SP-02 sogar `required: false`.

Direkt danach der zweite Fehler: Bleibt ein Feld leer, wird es aus
`approved_examples` gefüllt — den Beispielwerten des Katalogs. Genau so kamen
die Schuhe (`OUT-SP-04-BASE`) in einen Hausmeisterfall und der Fotograf
(`OUT-SP-02-BASE`) in den Blumenladen.

**Folge für den Auftrag:** Dieser gesamte Umschreibe-Block entfällt ersatzlos.
Die Felder, die das Modell schreibt, werden direkt verwendet.

Weitere Symptome aus demselben Lauf:
- „**Der Fotograf** verliert Zeit beim Zusammentragen" — dritte Person statt
  Anrede
- „eine einfache Vorgangsübersicht **schafft Klarheit**" — unbelegte
  Nutzenbehauptung
- „Vorgangsübersicht", „Projektakte" — interne Fachwörter beim Kunden
- „Eingehende Nachrichten werden einer vorgeschlagenen Vorgangsübersicht
  zugeordnet" — Behördenpassiv statt Alltagssprache

### Weitere bekannte Punkte

- **Zwei von fünf Demofällen** schließen die Endanalyse nicht ab.
- **Keine gültige Messung.** Die Zahlen aus `scripts/evaluate.py` stammen aus
  dem Keyword-Klassifikator, der nicht mehr im Produktivpfad läuft. Eine
  LLM-Evaluation ist an Rate-Limits gescheitert.
- **`routes.py` ist ein Monolith.** 2796 Zeilen mit Routing, Datenbankzugriff,
  Ablauflogik und Textaufbereitung durcheinander. Deryas Mentor hat das
  ausdrücklich angemerkt: Routen sollen dünn sein — Request rein, Funktion
  aufrufen, Antwort raus. Datenbanklogik gehört in ein eigenes Modul,
  Ablauflogik in Services. Eine Route ruft nie eine andere Route auf (kommt
  aktuell vor). Das ist eine eigene, spätere Aufgabe — **nicht Teil des
  aktuellen Auftrags.**
- **PDF-Kopfzeilen.** `127.0.0.1:8000/report` steht im gedruckten PDF. Das sind
  Browser-Kopf- und Fußzeilen und über `@media print` **nicht** abschaltbar.
  Nicht erneut versuchen, es als gelöst zu melden.

---

## 7. Arbeitsregeln

- **Kein Push nach `main`, kein Merge nach `main`.** Nur auf
  `feature/gate-cascade-quality`.
- Keine Git-Historie verändern, keine bestehenden Änderungen verwerfen oder
  stashen.
- Nicht committen: `.env`, Datenbanken, produktive FAISS-Dateien, temporäre
  Evaluationsartefakte.
- Evaluationsdaten bleiben aus allen Indizes ausgeschlossen.
- Autor und Committer: **Derya** — mit y in der Mitte, nicht mit i. Die
  falsche Schreibweise ist in einem früheren Durchgang mehrfach vorgekommen;
  ein Test prüft das inzwischen repositoryweit.
- Vor größeren Änderungen einen Rückweg-Tag setzen und pushen.

### Zwei Regeln aus schmerzhafter Erfahrung

**Keine fallbezogene Hartkodierung.** Es gab einmal einen Block
`if solution_id == "SP-03":` mit vierzig Zeilen fest verdrahtetem Kundentext in
`routes.py`. Ergebnis: genau ein Fall sah gut aus, alle anderen schlecht. Der
Block ist entfernt. Es darf kein neuer entstehen — für kein Muster, in keiner
Datei.

**Keine ungeprüften Erfolgsmeldungen.** Ein früherer Bericht meldete „Localhost
verschwunden", obwohl die Zeile nachweislich noch im PDF stand. Wenn eine
Bedingung nicht erfüllt ist, melde das. Ein offener Punkt ist harmlos, eine
falsche Erfolgsmeldung kostet einen ganzen Durchgang.

---

## 8. Was du zuerst lesen solltest

In dieser Reihenfolge:

1. `docs/PROJECT_STATE.md` — wo das Projekt steht
2. `knowledge/runtime/recommendation_catalog.json` — die zehn Solution
   Patterns, besonders die Felder `customer_title`, `user_action`, `ai_task`,
   `visible_output`, `human_check`, `counterexample`
3. `app/recommendation_service.py`, Funktion `select_recommendation` — wie ein
   Muster gewählt wird
4. `app/openai_service.py`, Funktion `generate_final_analysis` — **hier liegt
   die aktuelle Aufgabe**
5. `app/schemas.py`, Klasse `FinalAnalysisResult` — das Ausgabeschema
6. `app/routes.py` — die Payload-Erzeugung für die Ergebnisseite
7. `app/templates/results.html` und `report.html`

---

## 9. Der aktuelle Auftrag

Steht in einer eigenen Datei: **`ANWEISUNG_ENDANALYSE.md`**. Dazu gehört
**`EXPERIMENT_FREIER_PROMPT.md`** mit dem Prompt-Wortlaut.

Kurz: Die Endanalyse wird ersetzt. Statt feste Felder zu befüllen, schreibt das
Modell den Kundentext — mit dem gewählten Muster und den Regeln als Briefing.
Alles davor bleibt unverändert.

Der Beleg, dass das trägt: Derselbe Katalog und dieselben Regeln, als freier
Prompt in ein Chatfenster gegeben, haben für den Blumenladen eine Auswertung
erzeugt, die genau den Qualitätsmaßstab trifft. Die Maschinerie dazwischen
nimmt weg statt beizutragen.
