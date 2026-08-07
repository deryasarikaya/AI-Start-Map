# Tasks – Solution-Pattern-Recommendation

**Status:** Implemented, integrated, tested, documented and published
**Datum:** 2026-08-07
**Umsetzungsstatus:** Produktvertrag v3, Katalog, Loader, Retrieval, Agent-Pattern-Aufruf, Gate-Kaskade, A0 und fallbezogenes Ranking zulässiger Kandidaten sind integriert. Ergebnisseite und Druckbericht sind überarbeitet und mit echten Browser-/PDF-Renders geprüft. Nicht alle erneuten Live-Modellläufe wurden wegen API-Timeouts erfolgreich abgeschlossen.

| Bereich | Aufgabe | Status | Nachweis / Abhängigkeit |
|---|---|---|---|
| Fachlicher Review | Zwölf Problemfamilien und ihre Abgrenzungen fachlich freigeben. | Done | Fachgrundlage und Auftrag 2026-08-06 |
| Fachlicher Review | Zehn Solution Patterns, Voraussetzungen und Ausschlüsse fachlich freigeben. | Done | Fachgrundlage und Acceptance Criteria |
| Fachlicher Review | Vertrag für Wochentest und Anzahl der Opportunities erneut entscheiden. | Done | DEC-016 |
| Schema | Bestehende Pydantic-Schemas und JSONB-Verträge gegen die Spec prüfen. | Done | Keine Migration; JSONB-View vorgesehen |
| Schema | Minimalen typisierten Solution-Pattern-Vertrag entwerfen und freigeben. | Done | `app/recommendation_service.py` |
| Strukturierte Katalogdateien | Speicherformat und Pfad für den nicht-indexierten Katalog festlegen. | Done | `knowledge/runtime/recommendation_catalog.json` |
| Strukturierte Katalogdateien | Zehn freigegebene Patterns vollständig und validierbar erfassen. | Done | 12/10/Matrix-Validierung und Tests |
| Deterministische Gates | Vorgangsanker-, Kanal-, Reife-, Risiko-, Regelstabilitäts- und Freigabegates spezifizieren. | Done | `DecisionGates` |
| Deterministische Gates | Applicability, Exclusion und Tie-Breaking implementieren und testen. | Done | Selector-Unit-Tests und Laufzeitintegration vor dem finalen Modellaufruf |
| Retrieval-Vertrag | Diagnose-RAG-Ausgabe für Problem- und Bedingungsevidenz abgrenzen. | Done | Nutzerfakt-/Evidenztrennung und Retrievaltests |
| Retrieval-Vertrag | Konkurrenz defensiver Chunktypen und fehlenden `automation_pattern`-Gegencheck beheben. | Done | Vier reservierte Analyse-Typen |
| Recommendation-Auswahl | Problemfamilien und anwendbare Patterns in den Laufzeitpfad integrieren. | Done | `routes.py` → `recommendation_service.py` |
| Recommendation-Auswahl | Ranking gegen den aktuellen Prompt-/Python-Vertrag abgleichen. | Done | Selector entscheidet; Prompt formuliert den validierten Output |
| Output-Anpassung | Nutzerhandlung, KI-Aufgabe, sichtbares Ergebnis und Human Check verbindlich abbilden. | Done | Pydantic-Vertrag, Sprach- und Längentests |
| Output-Anpassung | Voraussetzungen und variable Opportunity-Anzahl umsetzen. | Done | Kein neuer Wochentest; 1–3 persistierte Zeilen |
| Evaluationen | Hausmeisterfall mit SP-03 auf Rang 1 unter bestätigten Bedingungen prüfen. | Done | Katalog- und Experience-Test |
| Evaluationen | Schuhmacherfall gegen Objekt-ID-/Orts-Gate prüfen. | Done | Objekt-/Orts- und Herausgabeprüfung |
| Evaluationen | Blumenladen gegen Bestellkarten- und Kapazitätsgrenze prüfen. | Done | Bestellkarte, offene Angaben, keine Autoannahme |
| Evaluationen | Massagesalon gegen Kapazitäts- und Freigabe-Gate prüfen. | Done | Keine automatische Zusage |
| Dokumentation | Projektstand, Architektur, Entscheidungen, Issues, Changelog, Roadmap und INDEX nach Implementierung aktualisieren. | Done | Documentation-Update-Skill |
| Code Review | Produktionsdiff auf Scope, Sicherheitsgrenzen, Knowledge-Trennung und unnötige Abstraktion prüfen. | Done | Abschlussdiff, `git diff --check` und Secret-/Artefaktprüfung bestanden |
| Release | Relevante Tests, Migrationen falls beschlossen, App-Start und Deployment-Artefakte verifizieren. | Done | Keine Migration; `107 passed`, HTTP 200, Commit `4ed51ab` gepusht |
| RAG-Zuverlässigkeit | Nach Promptbereinigung leere Chunks ohne Zuordnungsverschiebung überspringen. | Done | Isolierter Regressionstest bestanden |
| RAG-Zuverlässigkeit | Vor jedem Index-Promote getrennte vollständige Diagnose-/Agenten-Backups erzeugen. | Done | Zwei Promotes, zwei validierbare Backups und validierbare Produktion getestet |
| RAG-Zuverlässigkeit | FAISS-Indizes pro Prozess und Verzeichnis mit mtime-Invalidierung cachen. | Done | Wiederverwendung, Reload nach Dateiänderung und Fehlerpfad für fehlende Dateien getestet |
| Batch 09 | Output-Strukturen, Inference Patterns, Workflows und Evaluationen nach Datenrolle trennen. | Done | Pydantic-Loader, reproduzierbare Promotion und 30 ausgeschlossene Evaluationen |
| Batch 09 | Solution-Workflow-Index getrennt bauen und direkten Fallback erhalten. | Done | 27 positive Chunks, SP-04/Evaluationen ausgeschlossen, Index validiert |
| Gate-Kaskade | GATE-01 bis GATE-06 mit `pass`/`fail`/`unknown`, Begründung, Zielgruppenfit und A0 umsetzen. | Done | `test_gate_cascade.py`, 149 Tests |
| Gate-Kaskade | Legacy 91 und Batch 09 getrennt messen und Labelstatus bewahren. | Done | `scripts/evaluate.py`, keine gemittelte Kennzahl |
| Output v3 | Rollen, offene Angaben, kleinste Version, Nicht-Automationen und A0–A2 strukturiert speichern. | Done | Pydantic-/Persistenz-/Contract-Tests |
| Output v3 | OUT-Felder, Human Review, Kataloggrenzen und Vorschaukennzeichnung deterministisch anwenden. | Done | `test_output_contract_v3.py` |
| Filter | Nutzer-, Beispiel- und Zukunftsbegriffe erlauben; erfundene Ist-Fakten feldbezogen neutralisieren. | Done | DEC-023, Grounding-Regression |
| Legacy | Vorhandene Altanalysen prüfen, Shim-Platzhalter loggen und unsichtbar halten. | Done | DEC-024, lokale DB-Prüfung und View-Test |
| Modell | Finalprompt auf 15 Regeln kürzen, `medium`, zwei Versuche und Zeitbudget live prüfen. | Done | DEC-025, 60,141 s, ein Versuch |
| Ergebnisansicht | Sieben Klartextblöcke, offenen gekürzten Ist-Ablauf, kompakte Typografie, Zukunftsschritte und Vorher-/Nachher-Veranschaulichung umsetzen. | Done | Layout-/Sprachregressionen und echte Prüfung bei 1440 und 390 Pixeln |
| Druckbericht | V3-Inhalt auf genau zwei A4-Seiten begrenzen, Vorschau kennzeichnen und sichtbare Link-URLs unterdrücken. | Done | Report-Regression und visueller Zwei-Seiten-Hausmeister-Render |
| Kundenpayload | Verbotene technische Begriffe und unbelegte Nutzenbehauptungen protokollieren; betroffenes Feld einmal neu erzeugen und danach auslassen. | Done | Kundenpayload-, HTML- und Berichtstests |
| Veranschaulichung | Eingangsnachricht, daraus abgeleiteten Eintrag und konkrete Rückfrage fallbezogen erzeugen; Katalogwerte nur als protokollierten Notfall verwenden. | Done | Exklusivitäts-, Zahlenkonsistenz- und Branchenfremdheitstests |
| Musterauswahl | Statische Listenreihenfolge durch Structured-Output-Ranking ausschließlich zulässiger Kandidaten ersetzen und Obhut-Gegenstände eng abgrenzen. | Done | Vier neue Auswahl-Regressionsfälle |
| Fehlerverhalten | Stichwort-Fallback aus dem Produktivpfad entfernen und Klassifikations-, Ranking- sowie kritische Ausgabefehler sichtbar machen. | Done | Routen- und Service-Regressionen |
| Qualitäts-Liveläufe | Neue Modellpfade mit Hausmeister, Fotograf, Coach und langem Blumenladenfall prüfen; verbleibende Timeout-/Rate-Limit-Lücken offen dokumentieren. | In Progress | Browser- und PDF-Prüfung bestanden; Blumen-Demofall und A0-Endanalyse nicht erneut erfolgreich abgeschlossen |
| Live-Funde | A0-Override, PF-02-Abgrenzung, direkte Kundensprache, vollständige Zukunftssätze und kundensichere Katalogtitel absichern. | Done | Contract-, Gate-, Klassifikations- und View-Regressionen plus wiederholte Live-Fälle |
| Solution-Retrieval | Varianten-Ranking gegen deterministische Auswahl an den vier KI-Mentor-Fällen messen. | Done | Je Pattern 3 zulässig/2 geliefert; identische Workflowmenge, kein belegter Mehrwert |

## Statuswerte

- `Not Started`
- `In Progress`
- `Blocked`
- `Done`
