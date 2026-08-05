# Roadmap

**Last Updated:** 2026-08-06

Diese Roadmap enthält geplante Arbeit. Fachlich analysiert oder entschieden ist nicht gleich implementiert, integriert oder getestet. Eine Produktänderung gilt erst nach Verifikation und Dokumentation in `docs/CHANGELOG.md` als umgesetzt.

## Now

### Fachliche Arbeit

- Die vorhandene Fachgrundlage mit zwölf Problemfamilien und zehn Solution Patterns prüfen und formal freigeben; die Analyse ist erstellt, die Freigabe noch zu bestätigen.
- Abgrenzungen, Reifegrad-/Gate-Modell und Hausmeister-, Schuhmacher- sowie Massagesalon-Analyse im Fachreview bestätigen.
- Den entschiedenen variablen Outputvertrag ohne Wochentest gegen Referenzfälle abnehmen.
- Die Leitregel operationalisieren: **„So wenig Ordnung wie zwingend nötig, so früh konkrete KI-Unterstützung wie realistisch möglich, Automatisierung erst nach bestätigten Daten und klaren Freigaben.“**

### Technische Arbeit

- Recommendation-Feature-Spec technisch prüfen: bestehende Schemas, Persistenz, Laufzeitpunkte und Testpunkte verifizieren.
- Minimalen Vertrag für den strukturierten Solution-Katalog und die getrennten Gates spezifizieren.
- Reproduzierbare Evaluationseingaben und erwartete Kriterien für Hausmeister, Schuhmacher und Massagesalon festlegen.
- Den freigegebenen Katalog, die Gates und die Recommendation-Auswahl implementieren und integrieren.
- Datenschutz-, Betriebs- und Deployment-Konfiguration vor einem öffentlichen Produktivbetrieb abschließend prüfen.
- Bereitstellung der ignorierten produktiven FAISS-Artefakte für frischen Checkout beziehungsweise Deployment verifizieren.

### Produktarbeit

- Aktuelle Ergebnis- und PDF-Ausgaben anhand realer Beispiele auf Länge, Verständlichkeit und konkrete Handlungsfähigkeit prüfen.
- Product-Output-Vertrag gegen die neue Fachgrundlage reviewen, ohne den aktuellen Flow stillschweigend zu verändern.

## Next

### Fachliche Arbeit

- Solution Patterns mit Eignung, Voraussetzungen, Ausschlüssen, Reife, Risiko und menschlicher Kontrolle final freigeben.
- Ranking- und Tie-Breaking-Regeln für mehrere passende Patterns bestätigen.

### Technische Arbeit

- Fachlich freigegebenen strukturierten Solution-Katalog implementieren; zunächst ohne neuen FAISS-Solution-Index.
- Deterministische Applicability- und Exclusion-Gates implementieren.
- Recommendation-Auswahl auf Problemfamilie, Ursache, Reife und Freigabe ausrichten.
- Gezielte Tests für Hausmeister, Schuhmacher und Massagesalon ergänzen beziehungsweise schärfen.
- Agent-Pattern-Retrieval separat kontrolliert evaluieren und gegen deterministische Guardrails absichern.
- Observability für Retrieval-Auswahl, Agentenaktion, Promptphase, Validierung und Ergebnisqualität entwerfen.

### Produktarbeit

- Kundensprache kürzen und technische Begriffe reduzieren.
- Ergebnisansicht stärker priorisieren und vertiefende Inhalte konsequent einklappen.
- Druckansicht auf weniger Text und stabilere Seitennutzung optimieren.

## Later

### Fachliche Arbeit

- Solution-Pattern-Abdeckung schrittweise um weitere bestätigte Problemfamilien erweitern.
- Reifegrad- und Auswahlregeln anhand echter AI-Start-Map-Interviews kalibrieren.

### Technische Arbeit

- Echtes LLM-Function-Calling für klar typisierte interne Agentenwerkzeuge einführen.
- Einen dynamischen Interview-Agenten aufbauen, weiterhin begrenzt durch deterministische Budgets und Sicherheitsregeln.
- End-to-End-Observability und Tracing implementieren.
- Agent-Pattern-Retrieval nur bei nachgewiesenem Qualitätsgewinn dauerhaft aktivieren.
- Einen Solution-Index nur bei nachgewiesenem Bedarf und nach separater Entscheidung prüfen.

### Produktarbeit

- Interviewtiefe und Ergebnisdarstellung anhand realer Nutzung weiter kalibrieren.
- Mobile und Print-Darstellung auf den festgelegten Zielbrowsern vollständig abnehmen.

## Not planned yet

### Fachliche Arbeit

- Kein breiter, ungeprüfter Katalog beliebiger KI-Ideen.
- Keine Ausweitung über die Diagnose eines konkreten Geschäftsprozesses hinaus.

### Technische Arbeit

- Keine autonome Ausführung realer Unternehmensprozesse.
- Keine automatischen Preis-, Vertrags-, Zahlungs-, Qualitäts- oder Freigabeentscheidungen.
- Keine neuen Datenbanktabellen oder Felder ohne bestätigten aktuellen Produktbedarf.
- Keine zusätzliche Framework- oder schwere PDF-Infrastruktur ohne neue Entscheidung.

### Produktarbeit

- Keine Zusage bestimmter Drittanbieterintegrationen oder APIs ohne Verifikation und Freigabe.
- Kein automatisches Anhängen oder Versenden des PDF-Berichts; Kontakt bleibt derzeit ein `mailto:`-Link.
