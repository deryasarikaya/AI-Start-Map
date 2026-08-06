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

## Technologie

- FastAPI und Jinja2
- HTML, CSS und JavaScript
- PostgreSQL, SQLAlchemy und Alembic
- OpenAI Structured Outputs
- zwei getrennte FAISS-Indizes
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
- Agent-Pattern-Index: 205 optionale Patterns; die direkt geladene Fragevorlage liegt unter `knowledge/runtime/patterns/`, weitere bisherige Quellen unter `knowledge/archive/`.
- Strukturierter Recommendation-Katalog: `knowledge/runtime/recommendation_catalog.json` mit zwölf Problemfamilien, zehn Solution Patterns und einer validierten Zuordnungsmatrix ohne zusätzlichen Vektorindex.
- Evaluationen: 91 getrennte Fälle unter `knowledge/evaluation/`, die niemals indexiert werden. Vorbelegte erwartete Labels bleiben bis zur fachlichen Bestätigung ausdrücklich Vorschläge und keine Ground Truth.
- Agentenaktionen: `ASK`, `CLARIFY`, `RETRIEVE`, `ANALYZE`, `STOP`.
- Werkzeuge: `extract_process_state`, `search_diagnostic_knowledge`, `evaluate_readiness_and_next_action`.

Der Agent-Pattern-Index unterstützt im Interviewpfad die Auswahl relevanter Frage- und Guardrail-Muster. Die Solution-Auswahl erfolgt deterministisch aus Problemfamilien, sechs getrennten Gates und dem strukturierten Katalog. Echtes OpenAI Function Calling ist noch nicht integriert.

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

Die kundenverständliche Druckansicht nutzt zwei Seiten für Hauptlösung und Umsetzung. Eine dritte Seite erscheint nur bei fachlich vorhandenen weiteren Möglichkeiten. Sie wird über den Browser-Druckdialog (`window.print()`) als PDF gespeichert. Interne IDs, Prompts, Modellnamen, Logs, Scores und fremde Unternehmensdaten werden nicht ausgegeben. Der Kontakt zu Derya erfolgt über einen Mailto-Link; die gespeicherte PDF muss anschließend selbst angehängt werden.

## Projektdokumentation

Das verbindliche Register der Projekt-, Architektur-, Flow- und Feature-Dokumentation steht in [`docs/INDEX.md`](docs/INDEX.md). Dort sind Status, Source of Truth, letzte Prüfung und verwandte beziehungsweise ersetzte Dokumente ausgewiesen. Geplant, beschlossen, implementiert, integriert und getestet werden getrennt dokumentiert.

## Tests

```powershell
pytest -q
```

OpenAI- und Embedding-Aufrufe werden in automatisierten Tests gemockt. PostgreSQL-spezifische Prüfungen verwenden die in `TEST_DATABASE_URL` konfigurierte Testdatenbank.
