# AI Start Map V2

AI Start Map unterstützt Solo-Selbstständige und kleine Betriebe dabei, einen konkreten Arbeitsablauf zu verstehen, den größten Engpass zu erkennen und drei realistische nächste Schritte abzuwägen. Die Anwendung diagnostiziert und bereitet Entscheidungen vor; sie führt keine Unternehmensprozesse autonom aus.

## Nutzerreise

```text
Freie Beschreibung per Sprache oder Text
→ konkrete Prozessoption auswählen
→ verstandenen Ist-Ablauf prüfen und korrigieren
→ höchstens vier relevante Rückfragen
→ Engpass und drei priorisierte Startpunkte
→ Umsetzungsplan und druckbarer Kundenbericht
```

Die Oberfläche ist mobile-first aufgebaut. Spracheingabe nutzt die Spracherkennung des Browsers, wenn sie verfügbar ist; das Transkript bleibt editierbar und die Texteingabe funktioniert immer als Fallback. Prozessdiagramme werden aus validierten Schrittdaten erzeugt und besitzen eine sichtbare Listenansicht als Fallback.

Die Ergebnisse unterscheiden den sichtbaren Engpass, seine Ursache und Auswirkung. Der beste Startpunkt kann je nach Reifegrad Ordnung und Standardisierung, einfache Digitalisierung, regelbasierte Automatisierung oder KI-Unterstützung sein. Der Kundenbericht lässt sich über den Browser-Druckdialog als PDF speichern.

## Technologie

- FastAPI und Jinja2
- HTML, CSS und JavaScript
- PostgreSQL, SQLAlchemy und Alembic
- OpenAI Structured Outputs
- FAISS-basiertes RAG
- pytest

## Voraussetzungen

- Python
- PostgreSQL
- eine lokale `.env` mit `DATABASE_URL`, `TEST_DATABASE_URL`, `OPENAI_API_KEY` und `OPENAI_MODEL`

Die erwarteten Variablen stehen in `.env.example`. `SESSION_SIGNING_KEY` ist optional und sorgt dafür, dass signierte Sitzungscookies über App-Neustarts hinweg gültig bleiben. Die lokale `.env` wird nicht versioniert.

## Installation und Start

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
alembic upgrade head
python scripts/build_index.py --target test
python scripts/compare_indexes.py
python scripts/build_index.py --target promote
uvicorn app.main:app --reload
```

Danach ist die Anwendung unter `http://127.0.0.1:8000` erreichbar.

Die Anwendung verwendet zwei getrennte FAISS-Indizes. Der Diagnoseindex enthält 634 freigegebene Chunks aus `knowledge/curated/` sowie den RAG-Korpora von Batch 02 und Batch 03. Der optionale Agent-Pattern-Index enthält 205 Patterns aus Batch 04. Raw-Dateien, Reports, Quellenregister, Coverage-Matrizen und sämtliche 79 Evaluationen werden nicht indexiert.

`scripts/build_index.py` schreibt standardmäßig nur separate Testindizes. Eine Übernahme in die produktiven Verzeichnisse erfolgt erst mit `--target promote`; dabei wird der vorherige Diagnoseindex gesichert.

## Demo-Routen

```text
http://127.0.0.1:8000/demo/massage-salon
http://127.0.0.1:8000/demo/etsy-3d-print
http://127.0.0.1:8000/demo/carpet-cleaning
```

Die Demos nutzen dieselbe Analyse- und Ergebnispipeline wie die normale Reise. Fehlende Angaben bleiben als Unsicherheit sichtbar.

## Tests

```powershell
pytest -q
```

OpenAI- und Embedding-Aufrufe werden in den automatisierten Tests gemockt. PostgreSQL-spezifische Regeln laufen gegen die in `TEST_DATABASE_URL` konfigurierte Testdatenbank.

Die erste Demo nutzt zentral konfigurierte Interviewheuristiken: normalerweise zwei bis drei und maximal vier sichtbare Rückfragen sowie begrenzte Agenten- und Werkzeugrunden. Diese Werte müssen nach echten Interviews kalibriert werden.
