# AI Start Map – Processing Flow

**Status:** Active
**Letzte Prüfung:** 2026-08-07
**Source of Truth:** Aktuell implementiertes Processing-, Fehler- und Retry-Verhalten

_Stand: 26.07.2026_

## Gemeinsames Verhalten

Alle Formulare mit merklicher Modell-, RAG- oder Agentenarbeit tragen `data-disable-on-submit`. `app/static/app.js` deaktiviert beim Absenden sofort alle Submit-Schaltflächen und zeigt den gemeinsamen Processing-Layer aus `base.html`. Titel und Klartext werden pro Formular gesetzt; Prozentwerte werden nicht simuliert.

## Phasen

| Übergang | Sichtbarer Zustand | Serververhalten | Abschluss |
|---|---|---|---|
| Erzählung → Prozesse | „Ich prüfe deine Beschreibung.“ | Eingaben speichern; automatische Processing-Ansicht startet Prozesserkennung | Weiterleitung zur Prozesswahl |
| Prozesswahl → Agent | „Ich prüfe deine Angaben.“ | Structured Output rekonstruiert höchstens fünf Ist-Schritte und schreibt daraus alle sieben Prozessantworten; anschließend State-Extraktion, deterministische Agentenentscheidung, gegebenenfalls Diagnose- und kontrolliertes Agent-Pattern-Retrieval | Rückfrage oder Analyse |
| Rückfrage → nächste Aktion | gleiche Processing-Komponente | Antwort speichern, State erneut prüfen, verbleibende Fragen gegebenenfalls verwerfen | nächste Frage oder Analyse |
| Analyse → Ergebnis | „Ich prüfe, welcher KI-Schritt zu deinem Ablauf passt.“ mit vier Klartextstatuspunkten | Statusabfrage an `/analysis-status`, Problemfamilien/Gates, Diagnose-Retrieval, Solution-Selector und finale Structured-Output-Analyse über `/analyze` | automatische Weiterleitung zur einen priorisierten Hauptlösung |

Die Analyse-Processing-Seite arbeitet mit echtem Serverstatus (`pending`, `processing`, `complete`, `error`). Parallel laufende Analyseversuche werden durch den bestehenden Sitzungs-Schreibschutz begrenzt.

## Fehler und Retry

- Eingaben bleiben in der Datenbank erhalten.
- Die Analysefehleransicht zeigt keinen Stacktrace.
- Retry startet nur die fehlgeschlagene Analyse erneut.
- „Angaben bearbeiten“ führt zur Prozesswahl zurück. Eine eigene Bestätigungs- und Korrekturseite gibt es seit der Entfernung des Bestätigungsschritts nicht mehr.
- Eine erneute Erzählung ist nicht erforderlich.

## Technische Grenze

Prozesserkennung und Zusammenfassung laufen weiterhin in synchronen FastAPI-Requests; der sofortige Browser-Layer macht die tatsächliche Wartezeit sichtbar. Die finale Analyse besitzt zusätzlich die echte Statusabfrage. Eine Queue oder neue Infrastruktur wurde bewusst nicht eingeführt.
