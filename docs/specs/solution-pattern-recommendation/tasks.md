# Tasks – Solution-Pattern-Recommendation

**Status:** In Progress
**Datum:** 2026-08-06
**Umsetzungsstatus:** Produktvertrag, Katalog, Loader und deterministische Vorauswahl sind umgesetzt und unit-getestet; Laufzeitintegration folgt getrennt.

| Bereich | Aufgabe | Status | Nachweis / Abhängigkeit |
|---|---|---|---|
| Fachlicher Review | Zwölf Problemfamilien und ihre Abgrenzungen fachlich freigeben. | Done | Fachgrundlage und Auftrag 2026-08-06 |
| Fachlicher Review | Zehn Solution Patterns, Voraussetzungen und Ausschlüsse fachlich freigeben. | Done | Fachgrundlage und Acceptance Criteria |
| Fachlicher Review | Vertrag für Wochentest und Anzahl der Opportunities erneut entscheiden. | Done | DEC-016 |
| Schema | Bestehende Pydantic-Schemas und JSONB-Verträge gegen die Spec prüfen. | Done | Keine Migration; JSONB-View vorgesehen |
| Schema | Minimalen typisierten Solution-Pattern-Vertrag entwerfen und freigeben. | Done | `app/recommendation_service.py` |
| Strukturierte Katalogdateien | Speicherformat und Pfad für den nicht-indexierten Katalog festlegen. | Done | `knowledge/structured/recommendation_catalog.json` |
| Strukturierte Katalogdateien | Zehn freigegebene Patterns vollständig und validierbar erfassen. | Done | 12/10/Matrix-Validierung und Tests |
| Deterministische Gates | Vorgangsanker-, Kanal-, Reife-, Risiko-, Regelstabilitäts- und Freigabegates spezifizieren. | Done | `DecisionGates` |
| Deterministische Gates | Applicability, Exclusion und Tie-Breaking implementieren und testen. | Done | Selector-Unit-Tests; Laufzeitintegration separat offen |
| Retrieval-Vertrag | Diagnose-RAG-Ausgabe für Problem- und Bedingungsevidenz abgrenzen. | Not Started | Nutzerfakt-/Evidenztrennung beibehalten |
| Retrieval-Vertrag | Konkurrenz defensiver Chunktypen und fehlenden `automation_pattern`-Gegencheck beheben. | Not Started | Reproduzierbare Retrieval-Tests |
| Recommendation-Auswahl | Problemfamilien und anwendbare Patterns in den Laufzeitpfad integrieren. | Not Started | Gates und Katalog vorhanden |
| Recommendation-Auswahl | Ranking gegen den aktuellen Prompt-/Python-Vertrag abgleichen. | Not Started | Keine doppelte widersprüchliche Entscheidungshoheit |
| Output-Anpassung | Nutzerhandlung, KI-Aufgabe, sichtbares Ergebnis und Human Check verbindlich abbilden. | Not Started | Kundensprach- und Schema-Review |
| Output-Anpassung | Voraussetzungen, Wochentest und Opportunity-Anzahl nach Entscheidung anpassen. | Not Started | Separate Outputentscheidung erforderlich |
| Evaluationen | Hausmeisterfall mit SP-03 auf Rang 1 unter bestätigten Bedingungen prüfen. | Not Started | Evaluation bleibt außerhalb Produktwissen |
| Evaluationen | Schuhmacherfall gegen Objekt-ID-/Orts-Gate prüfen. | Not Started | Negative und positive Fälle |
| Evaluationen | Massagesalon gegen Kapazitäts- und Freigabe-Gate prüfen. | Not Started | Keine automatische Zusage |
| Dokumentation | Projektstand, Architektur, Entscheidungen, Issues, Changelog, Roadmap und INDEX nach Implementierung aktualisieren. | Not Started | Documentation-Update-Skill |
| Code Review | Produktionsdiff auf Scope, Sicherheitsgrenzen, Knowledge-Trennung und unnötige Abstraktion prüfen. | Not Started | Vollständiger Review |
| Release | Relevante Tests, Migrationen falls beschlossen, App-Start und Deployment-Artefakte verifizieren. | Not Started | Kein Release ohne Review und Freigabe |

## Statuswerte

- `Not Started`
- `In Progress`
- `Blocked`
- `Done`
