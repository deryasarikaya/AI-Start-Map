# AI Start Map V2

AI Start Map hilft Solo-Selbstständigen und kleinen Betrieben, aus einem unübersichtlichen Arbeitsalltag einen klaren ersten Schritt abzuleiten. Die Anwendung erkennt einen konkreten Prozess, fragt nur nach entscheidungsrelevanten Lücken und zeigt:

```text
eigentliches Problem
→ dein bester KI-Hebel
→ zukünftiger Ablauf
→ konkrete Ergebnisvorschau
→ deine Prüfung
→ einfachster Umsetzungsweg
```

AI Start Map diagnostiziert und unterstützt Entscheidungen. Die Anwendung führt keine Unternehmensprozesse autonom aus und trifft keine automatischen Preis-, Vertrags-, Zahlungs- oder Freigabeentscheidungen.

## Nutzerreise

```text
Erzählung per Sprache oder Text
→ einen erkannten Ablauf auswählen
→ kurze Ist-Zusammenfassung bestätigen oder korrigieren
→ null bis wenige relevante Rückfragen
→ sichtbare Verarbeitung
→ klares Sofortergebnis
→ optional Startplan, Details, PDF und Kontakt
```

Die Oberfläche ist mobile-first. Browser-Spracherkennung wird genutzt, wenn sie verfügbar ist; das Transkript bleibt editierbar und Texteingabe funktioniert immer. Prozessdarstellungen sind kurze vertikale HTML-/CSS-Listen, damit Labels auf kleinen Bildschirmen und im Druck lesbar bleiben.

Das Ergebnis beschreibt KI konkret über Eingabe, KI-Aufgabe, Ergebnis und menschliche Kontrolle. Ist zunächst Ordnung oder Standardisierung nötig, wird KI nicht erzwungen: Die App nennt dann ehrlich die Voraussetzung, ab der KI sinnvoll unterstützen kann.

Fünf reproduzierbare Mentor-Demofälle für Hausmeisterservice, Fotograf, Blumenladen, Coach und einen Nicht-KI-Fall stehen mit wörtlichen Eingaben und geprüften Ergebnissen in [`docs/MENTOR_DEMO_2026-08-07.md`](docs/MENTOR_DEMO_2026-08-07.md).

## Technologie

- FastAPI und Jinja2
- HTML, CSS und JavaScript
- PostgreSQL, SQLAlchemy und Alembic
- OpenAI Structured Outputs
- drei getrennte FAISS-Indizes mit sicherem deterministischem Fallback für das kleine Solution-Wissen
- pytest

## Voraussetzungen

- Python
- PostgreSQL
- lokale `.env` mit `DATABASE_URL`, `TEST_DATABASE_URL`, `OPENAI_API_KEY` und `OPENAI_MODEL`

Die erwarteten Variablen stehen in `.env.example`. `SESSION_SIGNING_KEY` kann für über Neustarts stabile signierte Sitzungscookies gesetzt werden. `.env` wird nicht versioniert.

## Installation und Start

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Danach läuft die Anwendung unter `http://127.0.0.1:8000`.

Die vorhandenen produktiven Indizes müssen für den normalen Start nicht neu gebaut werden. Falls sich der freigegebene Korpus später technisch ändert, schreiben die vorhandenen Build-Prozesse zunächst getrennte Testindizes; Vergleich und Promotion bleiben eigene bewusste Schritte.

## Wissen und Agent

- Diagnoseindex: 634 freigegebene Chunks aus dem bisherigen, jetzt unter `knowledge/archive/` liegenden Korpus. Der produktive Index wurde bei der Umordnung nicht neu gebaut.
- Agent-Pattern-Index: 205 optionale Patterns; direkt geladene Fragevorlagen und 27 geprüfte Batch-09-Inference-Patterns liegen getrennt unter `knowledge/runtime/patterns/`. Inference-Patterns bleiben immer unbestätigte Hypothesen.
- Strukturierter Recommendation-Katalog: `knowledge/runtime/recommendation_catalog.json` mit zwölf Problemfamilien, zehn Solution Patterns und einer validierten Zuordnungsmatrix. Zehn Batch-09-Output-Strukturen werden deterministisch geladen.
- Solution-Wissen: 28 kontrollierte Runtime-Workflows; 27 positive Workflows liegen im getrennten `solution_workflow_index`, der dokumentarische SP-04-Ausschluss nicht. Bei fehlendem Index greift eine direkte deterministische Auswahl desselben Solution Patterns.
- Evaluationen: 91 Legacy-Fälle plus 30 getrennte Batch-09-Fälle unter `knowledge/evaluation/`, die niemals indexiert werden. Alle Labels bleiben bis zur fachlichen Bestätigung Vorschläge und keine Ground Truth.
- Agentenaktionen: `ASK`, `CLARIFY`, `RETRIEVE`, `ANALYZE`, `STOP`.
- Werkzeuge: `extract_process_state`, `search_diagnostic_knowledge`, `evaluate_readiness_and_next_action`.

Der Agent-Pattern-Index unterstützt im Interviewpfad die Auswahl relevanter Frage- und Guardrail-Muster. Die Solution-Auswahl erfolgt deterministisch aus Problemfamilien, einer begründeten GATE-01…06-Kaskade und dem strukturierten Katalog. Sie kann A0 („keine KI nötig“) oder eine auf A1/A2 begrenzte Unterstützung wählen; SP-04 setzt einen echten physischen Gegenstand voraus. Echtes OpenAI Function Calling ist noch nicht integriert.

Der Kundenvertrag `recommendation-v3` trennt intern Nutzerhandlung, KI-Aufgabe, normale Software-/Regelaufgabe und menschliche Prüfung. Output-Struktur, offene Angaben, kleinste nutzbare Version, Nicht-Automationen und Autonomiestufe werden strukturiert gespeichert; Altanalysen bleiben ohne erfundene v3-Felder lesbar. Kundenseitig erscheinen daraus genau sechs Klartextblöcke: Engpass, Empfehlung, künftiger Ablauf, gekennzeichnete Beispielausgabe, menschliche Kontrolle und kleinster Einstieg. Interne PF-/SP-/OUT-IDs und Rohfelder werden auch bei älteren Ausgaben nicht angezeigt; ein ausdrücklicher Fall „vorhandene Funktion reicht, keine KI nötig“ bleibt deterministisch A0.

Sicherheitsregeln, Budgets, No-Repeat und Schleifenabbruch hängen nicht von semantischem Retrieval ab. RAG-Evidenz bleibt getrennt von Nutzerfakten.

Die zentralen Demoheuristiken bevorzugen null bis zwei sichtbare Rückfragen, erlauben drei nur in komplexen Fällen und begrenzen die sichtbare Zahl technisch auf vier. Agenten- und Werkzeugrunden sind ebenfalls begrenzt. Diese Werte müssen anhand echter Interviews kalibriert werden.

## Demo-Routen

```text
http://127.0.0.1:8000/demo/massage-salon
http://127.0.0.1:8000/demo/etsy-3d-print
http://127.0.0.1:8000/demo/carpet-cleaning
```

Die Demos nutzen dieselbe Analyse- und Ergebnispipeline wie die normale Reise. Fehlende Angaben bleiben Unsicherheiten.

## PDF und Kontakt

Die kundenverständliche Druckansicht nutzt genau zwei A4-Seiten: zuerst Engpass, Empfehlung, Zukunftsablauf und gekennzeichnete Vorschau, danach menschliche Kontrolle, Voraussetzungen, höchstens drei wichtige offene Fragen, kleinsten Einstieg, späteren Ausbau und Kontakt. Passt Inhalt nicht, wird er begrenzt statt auf eine dritte Seite umgebrochen. Gespeichert wird über den Browser-Druckdialog (`window.print()`). Interne IDs, Prompts, Modellnamen, Logs, Scores, Druck-URLs und fremde Unternehmensdaten werden nicht ausgegeben. Der Kontakt zu Derya erfolgt über einen Mailto-Link; die gespeicherte PDF muss anschließend selbst angehängt werden.

## Projektdokumentation

Das verbindliche Register der Projekt-, Architektur-, Flow- und Feature-Dokumentation steht in [`docs/INDEX.md`](docs/INDEX.md). Dort sind Status, Source of Truth, letzte Prüfung und verwandte beziehungsweise ersetzte Dokumente ausgewiesen. Geplant, beschlossen, implementiert, integriert und getestet werden getrennt dokumentiert.

## Tests

```powershell
pytest -q
```

OpenAI- und Embedding-Aufrufe werden in automatisierten Tests gemockt. PostgreSQL-spezifische Prüfungen verwenden die in `TEST_DATABASE_URL` konfigurierte Testdatenbank.
