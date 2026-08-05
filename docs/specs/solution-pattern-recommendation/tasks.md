# Tasks – Solution-Pattern-Recommendation

**Status:** Draft
**Datum:** 2026-08-05
**Umsetzungsstatus:** In diesem Dokumentationsauftrag wurde keine Implementierungsaufgabe begonnen.

| Bereich | Aufgabe | Status | Nachweis / Abhängigkeit |
|---|---|---|---|
| Fachlicher Review | Zwölf Problemfamilien und ihre Abgrenzungen fachlich freigeben. | Not Started | Fachgrundlage, Reviewprotokoll |
| Fachlicher Review | Zehn Solution Patterns, Voraussetzungen und Ausschlüsse fachlich freigeben. | Not Started | Fachgrundlage, Acceptance Criteria |
| Fachlicher Review | Vertrag für Wochentest und Anzahl der Opportunities erneut entscheiden. | Not Started | Product-Output-Spec, `docs/DECISIONS.md` |
| Schema | Bestehende Pydantic-Schemas und JSONB-Verträge gegen die Spec prüfen. | Not Started | Technischer Review von `app/schemas.py` und Persistenz |
| Schema | Minimalen typisierten Solution-Pattern-Vertrag entwerfen und freigeben. | Not Started | Keine unnötigen Felder oder neue Tabellen |
| Strukturierte Katalogdateien | Speicherformat und Pfad für den nicht-indexierten Katalog festlegen. | Not Started | Entscheidung und Allow-List-Prüfung |
| Strukturierte Katalogdateien | Zehn freigegebene Patterns vollständig und validierbar erfassen. | Not Started | Schema- und Fachreview |
| Deterministische Gates | Vorgangsanker-, Kanal-, Reife-, Risiko-, Regelstabilitäts- und Freigabegates spezifizieren. | Not Started | Design und fachliche Freigabe |
| Deterministische Gates | Applicability, Exclusion und Tie-Breaking implementieren und testen. | Not Started | Freigegebene Spezifikation |
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
