# API Endpoints

## MVP Kern (Woche 2-4)
- `GET /` → Landingpage
- `GET /start` → Interview starten
- `POST /sessions` → Session anlegen
- `GET /sessions/<id>` → Session laden
- `POST /sessions/<id>/answers` → Antwort speichern
- `POST /sessions/<id>/analyze` → KI-Auswertung starten
- `GET /sessions/<id>/result` → Ergebnis anzeigen
- `DELETE /sessions/<id>` → Session löschen

## Phase 2 (Woche 5-7)
- `POST /sessions/<id>/transcribe` → Voice-Input
