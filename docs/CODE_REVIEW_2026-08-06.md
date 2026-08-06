# Projektanalyse AI Start Map V2 — 2026-08-06

**Status:** Historical Review Snapshot – beschreibt den Stand vor Katalog-v2-, Evaluation- und LLM-Klassifikator-Commits. Es ist keine aktuelle Source of Truth; der verifizierte Stand steht in `docs/PROJECT_STATE.md` und `docs/ARCHITECTURE.md`.

Externe Durchsicht des gesamten Repos. Ziel: warum kommt das gewünschte
Ergebnis nicht heraus, was ist gut, was ist zu kompliziert, was ist unnötig.

---

## 1. Was wirklich gut ist

- **Produktidee und Zielbild sind scharf.** README und PROJECT_STATE beschreiben
  ein klares, verkaufbares Ergebnis: ein Hebel, ein Ablauf, eine Vorschau, eine
  menschliche Prüfung. Die meisten Projekte dieser Art haben das nicht.
- **Die Trennung „Nutzerfakt vs. RAG-Evidenz vs. Ableitung" ist konzeptionell
  richtig** und in `generate_final_analysis()` (A/B/C/D-Payload) sauber umgesetzt.
- **Der strukturierte Katalog** (`recommendation_catalog.json`, 12 PF × 10 SP +
  Matrix) ist das stärkste Asset im Projekt. Fachlich durchdacht, validiert,
  versionierbar. Den behalten.
- **Handwerk stimmt**: Typisierung, Pydantic-Validierung, Alembic, strukturierte
  Logs, Timeouts, Session-Locks, kein Mermaid im Print. Das ist überdurchschnittlich.
- **Ehrliche Doku.** `KNOWN_ISSUES.md` benennt Probleme, statt sie zu verstecken.

---

## 2. Kernbefund: warum das Wunschresultat nicht rauskommt

Die Qualität der Empfehlung wird **nicht** vom LLM und **nicht** vom Katalog
entschieden, sondern von **ca. 40 hartkodierten deutschen Teilstrings** in
`app/recommendation_service.py`.

```python
rules = (
    ("PF-08", ("sprachnachricht", "bon", "einsatz", "rechnung")),
    ("PF-05", ("schuh", "gegenstand", "regal", "ablageort")),
    ...
)
matches = [...][:3] or ["PF-01"]
```

Konsequenzen:

1. **Alles, was nicht wortwörtlich passt, fällt auf `PF-01` zurück.** Ein echter
   Nutzer, der von „Angebote schreiben", „Nachfassen", „Reklamation" oder
   „Wareneingang" erzählt, trifft keine einzige Regel. Er bekommt PF-01 → immer
   dieselbe Lösungsfamilie. Das ist exakt das Symptom „bekomme mein Wunschresultat
   nicht raus".
2. **Reihenfolgeabhängige Kollisionen.** `"rechnung"` steht in PF-08 *und* PF-09;
   PF-08 gewinnt allein, weil es oben steht. `"einsatz"` matcht auch in
   „Einsatzplanung" (eigentlich PF-06). `"termin"` setzt gleichzeitig PF-06 und
   `error_impact="high"` — mit Folgewirkung auf die Approval-Grenzen.
3. **Die Gates sind derselbe Mechanismus.** `infer_decision_gates()` leitet sechs
   Entscheidungsdimensionen aus Wortmarkern wie `"pflichtfeld"`, `"nur papier"`,
   `"lose zettel"` ab. Kein Mensch redet so. In der Praxis landet fast alles auf
   `"medium"` → die Gates diskriminieren nichts.
4. **Danach ist es zu spät.** `select_recommendation()` gibt `primary` deterministisch
   vor, und der finale Prompt zwingt das Modell: *„Erzeuge genau eine dominante
   Hauptlösung aus der deterministischen Vorauswahl."* Das LLM darf einen falschen
   Vorschlag also nur noch schön formulieren, nicht korrigieren.

**Das ist die Stelle, an der du dich verrannt hast.** Die Angst vor LLM-Halluzination
hat dazu geführt, dass die schwierigste semantische Aufgabe im ganzen System —
„welches Problem hat dieser Betrieb wirklich?" — an `str.__contains__` delegiert
wurde. Das ist die einzige Aufgabe, die ein LLM zuverlässig besser kann als Regeln.

**Verschärfend:** in `_parse_structured_output()` steht für gpt-5
`reasoning_effort: "minimal"` und für die finale Analyse `maximum_attempts = 1`.
Die anspruchsvollste Denkaufgabe des Systems bekommt also das kleinste Denkbudget
und keinen zweiten Versuch.

---

## 3. Weitere Stellen, an denen du dich verrannt hast

### 3.1 Regex-Zensur statt besserer Eingabe

`openai_service.py` enthält drei Schichten nachträglicher Textpolizei:

- `CUSTOMER_LANGUAGE_REPLACEMENTS` mit Einträgen wie `"übergabevermerkgabel"`,
  `"formulardoppie"`, `"handschriftenkapazität"` — das sind einmalige
  Modellausrutscher, die zu **permanenten globalen Regexen** befördert wurden.
- `SPECULATIVE_PROCESS_TERMS` / `SOLUTION_ONLY_UNCERTAINTY_TERMS` löschen ganze
  Ist-Schritte aus dem Ergebnis und rechnen die Index-Zuordnung neu — oder werfen
  die komplette Analyse weg (`raise AIServiceError`). Ein Nutzer, der selbst „Foto"
  sagt, kommt durch; ein anderer verliert den halben Ablauf.
- `schemas.py` hat neun weitere Regex-Muster (`SUMMARY_META_PATTERN`,
  `AS_IS_META_PATTERN`, `DISTANT_CUSTOMER_LANGUAGE_PATTERN` …).

Jeder Fehlfall hat ein neues Muster erzeugt. Das skaliert nicht und macht das
Verhalten unvorhersehbar. Wenn ein Modell wiederholt Fachjargon ausgibt, ist der
Prompt oder das Modell falsch, nicht der Output-Filter.

### 3.2 Der Mega-Prompt

Der System-Prompt in `generate_final_analysis()` enthält ~50 einzelne Vorschriften
in einem Block, inklusive Detailregeln zu Wortzahlen, Fotos, physischen Gegenständen
und medizinisch-rechtlichen Grenzen. Ab dieser Länge gewichtet kein Modell alle
Regeln gleich; die Regeln in der Mitte verpuffen. Und: **Formvorschriften, die im
Schema stehen (max_length, min_length, Anzahl), gehören nicht zusätzlich in den
Prompt.** Doppelte Durchsetzung kostet nur Aufmerksamkeit.

### 3.3 Der „Agent", der keiner ist

`agent_service.py` definiert `ProcessState` mit ~25 Feldern — sieht nach einem
reichen Zustandsmodell aus. Tatsächlich:

```python
if role_text:
    state.actors.append(role_fact)
    state.channels.append(role_fact.model_copy())
    state.tools.append(role_fact.model_copy())
    state.available_data.append(role_fact.model_copy())
```

Eine einzige Antwort wird viermal in vier verschiedene Felder kopiert. `actors`,
`channels`, `tools` und `available_data` enthalten immer denselben Text. Der
Zustand ist eine Fassade: die Struktur suggeriert Information, die nicht da ist.
`_digital_maturity()` ist wieder Wortmarker-Matching. `contradictions` entstehen,
sobald jemand „aber" schreibt.

Du dokumentierst das selbst korrekt unter TECH-002 — der Punkt ist, dass die
750 Zeilen Agent-Infrastruktur derzeit **negativen Wert** haben: sie erzeugen
Wartungslast und liefern dem finalen Prompt Pseudo-Fakten.

### 3.4 Der Legacy-Shim in `schemas.py`

`fill_legacy_core_output()` (~110 Zeilen, `model_validator(mode="before")`) mappt
ein altes Ausgabeschema auf das neue und **füllt fehlende Felder mit erfundenem
Text**:

```python
while len(future_steps) < 3:
    future_steps.append("Du prüfst das Ergebnis." ...)
payload.setdefault("ai_task", "Die KI erkennt und ordnet die relevanten Angaben.")
```

Zwei Probleme: (a) generische Platzhalter landen im Kundenergebnis, ohne dass
irgendwo Alarm ausgelöst wird; (b) **die Tests laufen durch diesen Shim.** 89 Tests,
davon ~94 `monkeypatch`-Aufrufe mit festen Fake-Antworten. Grün bedeutet hier
„die Verrohrung passt", nicht „die Empfehlung ist richtig". Genau deshalb kann
`107 passed` stehen, während das Produkt das Wunschresultat verfehlt.

### 3.5 Es gibt keine Messschleife

79 Evaluationsfälle liegen in `knowledge/evaluation/` und in Batch 04 — und werden
bewusst nie indexiert. Sie werden aber auch **nie gemessen**. Es gibt kein Skript,
das den echten Pipeline-Lauf über die Fälle schickt und zählt, wie oft die richtige
Problemfamilie und das richtige Solution Pattern gewählt werden. Ohne diese Zahl
ist jede Verbesserung Bauchgefühl — und genau das erklärt das Gefühl, seit Wochen
nicht näher ans Ziel zu kommen.

### 3.6 Doku als Ersatz für Validierung

8 Top-Level-Dokumente + `specs/` + `flows/` + `AGENTS.md` + `knowledge/README.md`,
alle am selben Tag aktualisiert, teils mit überlappendem Inhalt (`ARCHITECTURE`,
`PROJECT_STATE`, `DECISIONS`, `INDEX`, `DOCUMENTATION_GUIDE` — letzteres ist Doku
über Doku). Das ist mehr Prozess, als ein Ein-Personen-Projekt trägt, und es
ersetzt keine einzige Messung.

---

## 4. Unnötig — kann weg

| Was | Wo | Warum |
|---|---|---|
| `_massage_demo_fallback_result()` | `routes.py` 1442–1537 | ~95 Zeilen hartkodiertes Fake-Ergebnis für *einen* Demo-Slug. Wenn die Demo nur mit Fallback funktioniert, ist es keine Demo. |
| Alle `*_public`-Route-Wrapper | `routes.py` 2099–2217 | ~120 Zeilen reine Duplikation. Mit einer Session-Dependency und einem Router-Prefix ist das eine Zeile pro Route. |
| `data/vector_index_test`, `agent_pattern_index_test`, `vector_index_backup_pre_batch04` | `data/` | 7,3 MB tote Artefakte; Backup gehört nicht ins Arbeitsverzeichnis. |
| `.postgres-data/` im Projektordner | Repo-Root | Datenbank-Cluster im Quellordner. Gehört nach außerhalb. |
| `docs/DOCUMENTATION_GUIDE.md` | `docs/` | Doku über Doku bei einem Solo-Projekt. |
| `CUSTOMER_LANGUAGE_REPLACEMENTS` Einzelfall-Einträge | `openai_service.py` | Nach Prompt-Fix überflüssig. |
| `fill_legacy_core_output()` | `schemas.py` | Sobald die Tests echte Payloads verwenden. |

---

## 5. Zu kompliziert — vereinfachen

- **Zwei FAISS-Indizes für 634 + 205 Chunks.** Das ist winzig. Ein einziger Index
  mit `chunk_type`-Filter reicht; der Agent-Pattern-Index könnte ganz entfallen,
  da die Python-Guardrails ohnehin maßgeblich sind.
- **`routes.py` mit 2381 Zeilen.** Enthält Session-Handling, Journey-Steuerung,
  Analyse-Orchestrierung, View-Mapping, Demo-Setup und Fallbacks. Mindestens
  aufteilen in `routes/journey.py`, `routes/analysis.py`, `services/analysis_pipeline.py`,
  `views/result_view.py`.
- **Sechs Gates + Ausschlussgründe + Voraussetzungen + Approval-Grenzen**, alle
  gespeist aus Wortmarkern. Die Struktur ist zehnmal genauer als ihre Eingabe.
- **Synchroner Analyse-Call mit 60 s Timeout im Request.** Funktioniert in der Demo,
  nicht in der Realität — aber erst relevant, wenn die Qualität stimmt.

---

## 6. Was ich konkret ändern würde — in dieser Reihenfolge

### Schritt 1 — Klassifikation ans LLM (der eigentliche Fix)

Ersetze `classify_problem_families()` und `infer_decision_gates()` durch **einen
Structured-Output-Call**, der genau das ausgibt:

```python
class ProblemClassification(BaseModel):
    problem_family_ids: list[str]      # Enum PF-01..PF-12, max 3, sortiert
    reasoning_per_family: list[str]    # je ein Satz Beleg aus den Nutzerangaben
    gates: DecisionGates               # dieselben sechs Gates, aber begründet
    confidence: Literal["low","medium","high"]
```

Wichtig: Dem Modell die **Definitionen aus dem Katalog mitgeben** (`definition`,
`typical_statements`, `symptoms` je Problemfamilie stehen bereits in der JSON).
Das Modell ordnet zu, der Katalog bleibt die Autorität, Python behält alle Gates,
Ausschlüsse und Sicherheitsregeln. Du verlierst **keine** Determinismus-Garantie,
die dir wirklich wichtig ist — nur die falsche Zuordnung.

Bei `confidence: "low"` → gezielte Rückfrage statt Raten. Das ist zugleich die
richtige Rechtfertigung für den Follow-up-Schritt.

### Schritt 2 — Eval-Harness bauen (`scripts/evaluate.py`)

Alle 79 Fälle durch `classify → gates → select_recommendation` schicken und drei
Zahlen ausgeben:

- Problemfamilie Top-1 korrekt (%)
- Solution Pattern Top-1 korrekt (%)
- Anteil Fälle, die auf PF-01-Default fallen

Erst diese Baseline, dann Schritt 1, dann vergleichen. Ohne diese Zahl arbeitest
du weiter blind. Das ist der wichtigste Punkt der ganzen Analyse nach Schritt 1.

### Schritt 3 — Prompt entschlacken

Den finalen Prompt auf ~15 Kernregeln kürzen: alles streichen, was das Schema
bereits erzwingt. `reasoning_effort` für die finale Analyse auf `"medium"`,
`maximum_attempts` auf 2. Dann die Regex-Filter einzeln deaktivieren und prüfen,
welche überhaupt noch anschlagen.

### Schritt 4 — Aufräumen

Legacy-Shim entfernen, Tests auf echte Payloads umstellen, Demo-Fallback löschen,
`*_public`-Duplikate zusammenführen, `routes.py` aufteilen, tote Indizes löschen.

### Schritt 5 — Agent-Layer entscheiden

Entweder echtes Function Calling bauen oder `agent_service.py` auf das reduzieren,
was tatsächlich Wirkung hat (Budgets, No-Repeat, Stop-Regeln, Faktenintegrität).
Der aktuelle Mittelweg kostet 750 Zeilen und liefert kopierte Strings.

---

## 7. Ein-Satz-Zusammenfassung

Fachlich bist du weiter, als der Code zeigt: der Katalog ist stark, das Zielbild
ist klar, das Handwerk ist solide. Was fehlt, ist eine **verlässliche Brücke von
freier Nutzererzählung zur richtigen Problemfamilie** — und die ist derzeit ein
Keyword-Match, dem nachgelagert ein Mega-Prompt und ein Dutzend Regex-Filter die
Fehler austreiben sollen. Klassifikation ans Modell, Katalog als Autorität,
Messschleife auf die 79 Fälle: das sind die drei Änderungen, die das Wunschresultat
freischalten.
