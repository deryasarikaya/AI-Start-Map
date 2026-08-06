# Tasks – Solution-Pattern-Recommendation

**Status:** Implemented, integrated, tested, documented and published
**Datum:** 2026-08-06
**Umsetzungsstatus:** Produktvertrag, Katalog, Loader, Retrieval, Agent-Pattern-Aufruf, Gate-Kaskade, A0 und deterministische Auswahl sind integriert; Kundenausgabe und Bericht werden im aktiven Qualitätslauf weiter konkretisiert. 149 Tests sind bestanden.

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

## Statuswerte

- `Not Started`
- `In Progress`
- `Blocked`
- `Done`
