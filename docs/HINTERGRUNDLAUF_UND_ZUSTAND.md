# Hintergrundlauf und Journey-State

Wie AI Start Map lange Modellaufrufe aus dem HTTP-Request herauslöst, und
woher das System weiß, an welcher Stelle ein Nutzer gerade steht.

---

## 1 · Der Hauptflow

Der Weg vom Klick bis zum gespeicherten Ergebnis, in der Reihenfolge, in der
ein Request ihn durchläuft:

```
Browser
  │  POST /interview          Beschreibung wird gespeichert
  ▼
/processing                   Warteschirm, startet die Analyse
  │  POST /analyze
  ▼
routes.analyze_session        stellt den Auftrag ein und antwortet sofort
  │  auswertung_erzeugen.delay(session_id)
  ▼
─ ─ ─ ─ Prozessgrenze ─ ─ ─ ─
  ▼
Celery-Worker
  │  app/hintergrund.py
  ▼
analysis_service.run_generation
  ├─ run_first_call            generate_diagnosis            ~18 s
  ├─ (Verstandenseite)
  └─ run_second_call
       ├─ generate_target_architecture                       ~32 s
       ├─ generate_result_part_two (Ansichten)               ~9 s
       └─ generate_result_part_two (Rest)                    ~17 s
  ▼
PostgreSQL: partial_results, results
  ▲
  │  GET /analysis-status      der Warteschirm fragt nach
Browser
```

Jeder Modellaufruf geht durch `openai_service.parse_structured_output` und
wird gegen den Ergebnisvertrag geprüft, bevor er gespeichert wird.

---

## 2 · Der gewählte langsame Aufruf

**`generate_target_architecture`, rund 32 Sekunden** — der längste
Einzelaufruf. Der ganze Durchlauf braucht etwa 78 Sekunden, gemessen an
einem echten Fall.

Herausgelöst wurde deshalb nicht dieser eine Aufruf, sondern die Funktion,
die ihn enthält: `run_generation`. Sie ist die Einheit, die der Warteschirm
anstößt, und eine halbe Analyse im Request wäre dasselbe Problem in klein.

**Was sich nicht geändert hat:** Katalog, Abruf, Prompts, Prüfungen,
Datenbankschema der Ergebnisse. Nur *wo und wann* gerechnet wird.

---

## 3 · Der Hintergrundlauf

```
kurzer Request:  Browser → Server → „Auftrag liegt an" → sofort zurück
lange Arbeit:                     → Worker → Modell → Ergebnis ablegen
```

**Warum.** Ein Sprachmodell hat keine zugesagte Laufzeit — Sekunden,
Minuten oder ein Fehler. Zwischen Browser und Anwendung sitzen im Betrieb
Reverse Proxies mit Zeitgrenzen, die deutlich unter 78 Sekunden liegen.
Der Request stirbt dann mitten in der Arbeit, und niemand weiß, wie weit
sie kam.

Der Unterschied, auf den es ankommt: **Eine lange Analyse ist aus
Kundensicht in Ordnung. Ein minutenlang offener HTTP-Request ist es
nicht.**

### Der Broker ist eine Konfigurationszeile

```python
broker_url = "filesystem://"      # heute — kein Dienst nötig
broker_url = "redis://localhost"  # im Betrieb, über CELERY_BROKER_URL
```

Der Dateisystem-Broker macht die Vorführung zu zwei Befehlen statt einer
Installation. Am Muster ändert er nichts: eigener Prozess, echte
Warteschlange, echtes `delay()`.

### Kein Ergebnis-Backend

Celery braucht keins. Der Zustand liegt bereits in PostgreSQL; ein zweiter
Speicher für dieselbe Information wäre eine zweite Wahrheit. Der Worker
schreibt dorthin, wo die Seite ohnehin liest.

### Starten

```
Terminal 1:  uvicorn app.main:app --port 8000
Terminal 2:  celery -A app.hintergrund worker --loglevel=info --pool=solo
```

Der `--pool=solo` gilt nur für Windows; unter Linux entfällt er.

---

## 4 · Journey-State: Woher das System weiß, wo jemand steht

Es gibt **keine** eigene Zustandsspalte und keine Sitzungsvariable. Der
Stand ergibt sich aus dem, was tatsächlich in der Datenbank liegt — und
kann deshalb nicht mit der Wirklichkeit auseinanderlaufen.

| Frage | Woran man es sieht |
|---|---|
| Sitzung existiert? | Zeile in `sessions` |
| Beschreibung erhalten? | `interview_questions.answer_text` gefüllt |
| Diagnose fertig? | `partial_results.payload` ist nicht leer |
| Welche Runde? | `partial_results.rounds` (Obergrenze 2) |
| Rückfrage erledigt? | `partial_results.moving_on` |
| Ergebnis fertig? | Zeile in `results` |
| Lauf gescheitert? | `sessions.lauf_fehler` |
| Läuft gerade schon einer? | `repository.acquire_session_write_lock` |

**Der Türsteher** ist `process_service.next_valid_path`. Er liest genau
diese Felder und gibt zurück, wo der Nutzer wirklich steht:

```
results vorhanden                      → /results
Beschreibung fehlt                     → /interview
payload da und moving_on falsch        → /verstanden
sonst                                  → /processing
```

Jede Seite fragt ihn beim Aufruf. Wer eine Adresse aufruft, für die er noch
nicht so weit ist, landet an der Stelle, an der er tatsächlich steht.

### Was bei einem Abbruch passiert

Bricht der Browser oder die Internetverbindung weg, geht **nichts**
verloren:

- Was fertig ist, steht in der Datenbank und wird nicht neu berechnet.
- Der Worker läuft unabhängig vom Browser weiter.
- Beim nächsten Aufruf führt `next_valid_path` an dieselbe Stelle zurück.
- Die Schreibsperre verhindert, dass ein zweiter Lauf derselben Sitzung
  parallel startet.
- Ein gescheiterter Lauf hinterlässt seinen Grund in `sessions.lauf_fehler`,
  und die Statusabfrage meldet `failed` statt endlos `pending`.

### Warum der Zustand nicht doppelt geführt wird

Eine Spalte `journey_state = "diagnose_fertig"` wäre lesbarer — und die
zweite Stelle, an der derselbe Sachverhalt steht. Sie kann veralten, wenn
ein Lauf abbricht, bevor sie geschrieben wird. Die Felder oben können das
nicht: Sie *sind* das Ergebnis, nicht seine Beschreibung.

---

## 5 · Was bewusst nicht gemacht wurde

- Nicht alle Modellaufrufe migriert — ein echter langsamer Schritt reicht
  als Muster.
- RAG, FAISS, Embeddings und der Katalog unverändert.
- Keine Microservices, keine neue Agentenarchitektur.
- Keine erfundenen Phasen in der Statusabfrage: Belegbar sind zwei — vor
  und nach dem ersten Modellaufruf. Der Warteschirm markiert deshalb auch
  nur diese beiden und lässt die übrigen Stationen sichtbar warten.
