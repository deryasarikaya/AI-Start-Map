# Bewertung und Einbauplan – Research Batches 05–08

**Status:** Historical Integration Plan – teilweise umgesetzt. Katalog v2, Evaluation-Harness und semantische Problemklassifikation sind integriert; die fachliche GATE-01-bis-GATE-06-Kaskade, der A0-Ausgang und die deterministische Autonomieberechnung sind nicht umgesetzt. Batch 08 ist nicht produktiv integriert. Aktueller Stand: `docs/PROJECT_STATE.md`.

Stand: 2026-08-06
Bezug: `docs/CODE_REVIEW_2026-08-06.md`

**Kurzurteil: Ja, das bringt sehr viel — aber nicht als RAG-Wissen.**
Die Batches 05–07 sind exakt die drei Bausteine, die im Code-Review als fehlend
identifiziert wurden. Sie gehören in den **deterministischen Entscheidungspfad**,
nicht in den Vektorindex.

---

## 1. Der wichtigste Befund: unabhängige Bestätigung deines Katalogs

Batch 06 enthält dieselben zehn Solution Patterns `SP-01` bis `SP-10` wie dein
bestehender `recommendation_catalog.json` — mit fast identischen Namen. Das ist
eine unabhängige fachliche Validierung deines stärksten Assets.

Die PF→SP-Zuordnungen wurden verglichen:

| SP | Abweichung |
|---|---|
| SP-02, SP-03, SP-05, SP-06, SP-08, SP-09, SP-10 | **identisch** |
| SP-01 | neu **ohne** PF-11, PF-12 |
| SP-04 | neu **ohne** PF-04 |
| SP-07 | neu **ohne** PF-04 |

Alle vier Abweichungen sind **Verengungen** — die neue Recherche entfernt zu
breite Zuordnungen. Genau das braucht ein Empfehlungssystem, das aktuell zu
generisch antwortet. Die Verengungen übernehmen.

---

## 2. Was jeder Batch löst

### Batch 05 – GenAI Capabilities + 6 Gates → **löst den Kernbefund des Reviews**

Die sechs neuen Gates sind **semantische Fragen mit Pass/Fail-Verzweigung**, kein
Wortmarker-Scoring:

```
GATE-01 Aufgabenfit   → Fail: keine KI empfehlen, Prozess/Regel/Standardsoftware
GATE-02 Vorgangsanker → Fail: zuerst minimalen Anker schaffen
GATE-03 Zieloutput    → Fail: zuerst Zielschema definieren
GATE-04 Prüfbarkeit   → Fail: kein operativer Einsatz
GATE-05 Fehlerfolgen  → setzt Freigabestufe
GATE-06 Daten/Rechte  → Fail: Einführung stoppen
```

Drei Dinge, die das besser macht als deine aktuellen sechs Gates:

1. **Es ist eine Kaskade, kein Score-Bündel.** Deine aktuellen Gates sind sechs
   unabhängige `low/medium/high`-Werte, die fast alle auf `"medium"` landen und
   nichts diskriminieren. Diese hier haben eine definierte Fail-Aktion pro Gate.
2. **GATE-01 „Aufgabenfit" existiert bei dir gar nicht.** Dein System empfiehlt
   *immer* ein Solution Pattern. Es kann nie sagen „das ist keine KI-Aufgabe,
   du brauchst eine Regel". Abschnitt 5 der Forschungsgrundlage liefert dafür
   die vollständige Gegenliste (ID-Vergabe, Preisberechnung, Statuswechsel,
   Fälligkeiten, Zugriffsrechte, physischer Lagerort → alles nicht GenAI).
3. **Sie sind LLM-beantwortbar.** „Besteht die Reibung wesentlich aus Verstehen,
   Extrahieren, Klassifizieren …?" ist eine Frage, die ein Modell aus einer
   Erzählung zuverlässig beantwortet — und `str.__contains__` niemals.

Die neun Capabilities `GAI-01` bis `GAI-09` geben zusätzlich pro Fähigkeit
`required_process_foundation`, `human_review`, `failure_modes` und
`autonomy_ceiling`. Das füllt `required_prerequisites` und `human_check` mit
belegten statt generierten Inhalten.

### Batch 06 – validierte Solution Patterns → **füllt die leeren Ausgabefelder**

Neue Felder pro SP, die dein Runtime-Katalog nicht hat:

| Neues Feld | Füllt im Output |
|---|---|
| `genai_capabilities` | Verbindung SP → GAI, begründet `ai_task` |
| `deterministic_components` | was **nicht** die KI macht — heute komplett unsichtbar |
| `human_decisions` | `human_check`, `human_approval_boundaries` |
| `counterexample` | Ausschlussgrund im Selector, statt erfundener Begründung |
| `pilot` (scope/output/no_action) | `implementation_path` — endlich konkret statt Floskel |
| `metrics` | Erfolgskriterium, das dem Kunden fehlt |
| `stop_conditions` | `error_boundaries` — heute vom Modell frei erfunden |
| `autonomy_level` | siehe unten |

### Batch 07 – Failure Patterns → **ersetzt die Regex-Zensur**

Zwölf `FAIL-01` bis `FAIL-12` mit `trigger`, `harm`, `detection`, `guardrail`
und `blocks_autonomy`. Das ist die prinzipielle Version dessen, was du heute mit
`SPECULATIVE_PROCESS_TERMS` und `CUSTOMER_LANGUAGE_REPLACEMENTS` per Wortliste
erzwingst. Insbesondere:

- `FAIL-07 RAG-Wissen wird zum Nutzerfakt` — genau dein A/B/C-Trennungsproblem,
  jetzt als benannter, testbarer Guardrail.
- `FAIL-11 KI für eine deterministische Aufgabe` — die Gegenprobe zu GATE-01.
- `FAIL-12 Automation vor Prozessbasis` — die saubere Fassung von KI-003
  („Ordnung vor Automatisierung"), ohne die Übertreibung.

### Batch 07 Evaluationsfälle → **der Eval-Harness, den du brauchst**

Zwölf Fälle im Format:

```json
{"id":"RB07-E01","input":"…","expected":"STOP_OR_CLARIFY",
 "must_include":["Vorgangsanker","Bestätigung"],
 "must_not_include":["automatische Zuordnung"]}
```

`must_include` / `must_not_include` sind **maschinell prüfbar**. Das ist Schritt 2
des Code-Reviews, fertig spezifiziert. Zusammen mit den vorhandenen 79 Fällen
hast du 91 Fälle für eine echte Messschleife.

### Batch 08 – Tools und Referenzarchitekturen → **jetzt noch nicht einbauen**

Sechs Tool-Optionen (OpenAI API, n8n, Textract, Azure DocInt, Postgres, FAISS)
und fünf Referenzarchitekturen `ARCH-01` bis `ARCH-05`. Der Batch ist selbst als
„zeitkritisch/versioniert" markiert und hat ein `as_of`-Feld.

- **Nicht** in Katalog oder Index aufnehmen. Tool-Namen veralten und würden im
  Kundenergebnis zu ungedeckten Behauptungen führen.
- Die **Referenzarchitekturen** sind für dich als Entwickler relevant: `ARCH-01
  A2 Structured Draft` ist die Architektur, die AI Start Map als Produkt selbst
  empfiehlt. Ablage unter `docs/`, nicht unter `knowledge/`.

---

## 3. Die neue Dimension: Autonomiestufen A0–A5

Bisher völlig abwesend im Code. Die Forschungsgrundlage setzt **A2 (eingebetteter
Entwurf, Mensch bestätigt jeden Output) als Regelfall** für Kleinunternehmen und
**A0 (keine KI, Regel oder Standardsoftware reicht) als ausdrücklich empfehlbares
Ergebnis**.

Das löst KI-003 sauber: Die Antwort auf „empfiehlt zu viel Ordnung" ist nicht
„weniger Ordnung", sondern **eine explizite Autonomiestufe pro Empfehlung**.
Jedes SP trägt in Batch 06 bereits sein `autonomy_level`; jeder Failure Pattern
trägt `blocks_autonomy`. Damit ist die Stufe berechenbar:

```
zulässige Stufe = min(SP.autonomy_level,
                      min(GAI.autonomy_ceiling für alle genutzten Capabilities),
                      Deckel aus GATE-05 Fehlerfolgen,
                      Deckel aus allen zutreffenden FAIL-Patterns)
```

Das ist eine deterministische Berechnung auf gepflegten Daten — dieselbe
Sicherheitsgarantie, die du heute mit Wortmarkern anstrebst, nur belastbar.

---

## 4. Die Falle, in die du hier nicht wieder laufen darfst

Der Reflex wäre: alles nach `knowledge/`, neuen FAISS-Index bauen, weitere Gates,
weitere Doku. Das wäre eine Wiederholung genau des Fehlers aus dem Code-Review.

**Regel: Batch 05, 06 und 07 sind Entscheidungsdaten, kein Retrieval-Korpus.**

| Inhalt | Wohin | Warum |
|---|---|---|
| GAI-01…09, SP-01…10 (neue Felder), FAIL-01…12, GATE-01…06 | `knowledge/runtime/recommendation_catalog.json` v2 | wird deterministisch geladen und validiert, nicht gesucht |
| Batch-07-Evaluationsfälle | `knowledge/evaluation/` | niemals indexieren, nur messen |
| Batch 08 | `docs/reference/` | Entwicklerwissen, kein Produktwissen |
| Fließtext der Forschungsgrundlage | `knowledge/archive/raw/` | Beleg, nicht Laufzeit |

Es entsteht **kein neuer Vektorindex**. Die Gesamtmenge ist ~37 Datensätze —
die passen vollständig in einen Prompt.

**Zweite Falle:** Die neuen sechs Gates sind nicht dieselben wie deine alten.
Nur `Vorgangsanker` und `Fehlerfolgen` decken sich. Nicht beide Sätze parallel
führen — das wäre zwölf Gates, die sich widersprechen. Die neuen ersetzen die
alten; `channel_suitability` bleibt als einziger Zusatz erhalten (er entscheidet
bei SP-03 real mit).

---

## 5. Einbauplan in Reihenfolge

### Schritt 1 — Katalog v2 (rein additiv, keine Codeänderung nötig)

`recommendation_catalog.json` auf Version 2 heben:

- Neuen Block `genai_capabilities` mit GAI-01…09.
- Neuen Block `failure_patterns` mit FAIL-01…12.
- Neuen Block `decision_gates` mit GATE-01…06 (Frage, Pass, Fail).
- Je SP die acht neuen Felder aus Batch 06 ergänzen.
- Die vier verengten PF→SP-Zuordnungen übernehmen (SP-01 ohne PF-11/PF-12,
  SP-04 und SP-07 ohne PF-04).
- Je PF die Spalten aus Abschnitt 6 der Forschungsgrundlage ergänzen:
  `genai_role`, `non_genai_requirement`, `human_boundary`.

`recommendation_service.py` bekommt die entsprechenden Pydantic-Modelle. Die
bestehende Validierung (12 PF, 10 SP, Matrix vollständig) bleibt und wird um
Referenzprüfungen SP→GAI und FAIL→autonomy erweitert.

### Schritt 2 — Eval-Harness zuerst, nicht zuletzt

`scripts/evaluate.py` gegen die zwölf RB07-Fälle bauen. Sie sind maschinell
prüfbar, also läuft die Messung sofort. Baseline mit dem **heutigen** Keyword-
Klassifikator aufnehmen. Die Zahl wird schlecht sein — das ist der Punkt.

### Schritt 3 — Gate-Kaskade statt Wortmarker

`classify_problem_families()` und `infer_decision_gates()` durch **einen**
Structured-Output-Call ersetzen:

```python
class Diagnosis(BaseModel):
    problem_family_ids: list[PFEnum]        # max 3
    evidence_per_family: list[str]          # Beleg aus Nutzerangaben
    gate_01_task_fit: GateResult            # pass/fail + Begründung
    gate_02_transaction_anchor: GateResult
    gate_03_target_output: GateResult
    gate_04_verifiability: GateResult
    gate_05_error_impact: ErrorImpact
    gate_06_data_permission: GateResult
    channel_suitability: Level
    confidence: Literal["low","medium","high"]
```

Als Prompt-Kontext bekommt das Modell die PF-Definitionen und die
Gate-Formulierungen aus dem Katalog — nicht den Fließtext der Recherche.

Bei `gate_01 = fail` → **A0-Pfad**: keine KI-Empfehlung, sondern der passende
Mechanismus aus der Gegenliste in Abschnitt 5. Das ist ein neuer, ehrlicher
Ausgang, den das Produkt heute nicht hat.

Bei `confidence = low` → gezielte Rückfrage. Damit ist der Follow-up-Schritt
zum ersten Mal fachlich begründet statt heuristisch budgetiert.

### Schritt 4 — Autonomiestufe berechnen und anzeigen

`select_recommendation()` gibt zusätzlich `autonomy_level` und die begrenzenden
`FAIL`-IDs zurück. Im Kundenergebnis wird daraus ein Satz in Alltagssprache
(„Die KI erstellt den Entwurf, du bestätigst jedes Ergebnis"), keine A2-Nummer.

### Schritt 5 — Regex-Zensur zurückbauen

`stop_conditions` und `guardrail` aus Katalog v2 ersetzen `SPECULATIVE_PROCESS_TERMS`
und `SOLUTION_ONLY_UNCERTAINTY_TERMS`. Filter einzeln deaktivieren, nach jedem
Schritt Eval laufen lassen. Was die Eval nicht verschlechtert, kommt weg.

### Schritt 6 — Prompt entlasten

`pilot`, `deterministic_components`, `stop_conditions`, `metrics` und
`human_decisions` kommen jetzt aus dem Katalog. Die entsprechenden Vorschriften
im Mega-Prompt können ersatzlos entfallen — das Modell formuliert nur noch, es
erfindet nicht mehr.

---

## 6. Erwartete Wirkung auf die offenen Punkte

| Offener Punkt | Wird gelöst durch |
|---|---|
| KI-001 Kalibrierung fehlt | Eval-Harness (Schritt 2) + LLM-Klassifikation (Schritt 3) |
| KI-003 Ordnung wird überbetont | Autonomiestufen A0–A5 + FAIL-12 (Schritt 4) |
| KI-005 Sprache zu technisch | `customer_language` + `pilot` aus Katalog statt Modellerfindung |
| KI-007 Workflow nicht optimal | Verengte PF→SP-Matrix + Gate-Kaskade |
| TECH-002 kein Function Calling | teilweise entschärft: die Entscheidung wird strukturiert, ohne Tool-Loop |

Nicht gelöst: Observability (TECH-003), Index-Deployment (TECH-004),
Gerätematrix (UX-001), `routes.py`-Größe. Die bleiben unabhängig davon offen.

---

## 7. Fazit in drei Sätzen

Die Recherche bestätigt deinen Katalog unabhängig und liefert genau die drei
Teile, die im Code fehlen: eine semantische Gate-Kaskade statt Wortmarker, die
konkreten Umsetzungsfelder pro Solution Pattern, und maschinell prüfbare
Evaluationsfälle. Der Wert liegt vollständig im deterministischen
Entscheidungspfad — kein neuer Index, kein neues Retrieval, kein neues Framework.
Wenn du nur eine Sache daraus einbaust, dann GATE-01 Aufgabenfit mit dem
A0-Ausgang: die Fähigkeit, ehrlich „hier hilft dir keine KI" zu sagen, ist der
größte Glaubwürdigkeitsgewinn, den das Produkt haben kann.
