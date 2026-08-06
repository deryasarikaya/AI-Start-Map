# Roadmap

**Last Updated:** 2026-08-07

Diese Roadmap enthält nur verbleibende geplante Arbeit. Der implementierte Recommendation-Vertrag, Katalog, Selector, Agent-Pattern-Aufruf, neue Ergebnisoberfläche und variable Druckansicht stehen im Changelog und nicht mehr als Planung hier.

## Now

### Fachliche Arbeit

- Problemfamilienklassifikation, Gates, Fragezahl und sichtbare Ergebnisse anhand echter AI-Start-Map-Interviews kalibrieren.
- Neue reale Fehlfälle sauber in Diagnosefehler, Auswahlfehler und Formulierungsfehler trennen.
- Ranking- und Tie-Breaking-Regeln nur dann erweitern, wenn reale Fälle mit mehreren gleich geeigneten Patterns dies belegen.

### Technische Arbeit

- Bereitstellung der gitignorierten produktiven Diagnose- und Agent-Pattern-Indizes für frischen Checkout beziehungsweise Deployment verifizieren.
- Datenschutz-, Betriebs- und Deployment-Konfiguration vor einem öffentlichen Produktivbetrieb abschließend prüfen.
- Die vorhandenen strukturierten Logs im Betrieb auf Nutzbarkeit und Datenminimierung prüfen.
- Latenz, Validierungsfehler und tatsächliche Retry-Quote des v3-Finaloutputs über mehrere reale, datensparsam protokollierte Läufe messen; die Einzelmessung von 60,141 Sekunden ist keine belastbare Statistik.

### Produktarbeit

- Die kompakte Hauptseite und den variablen Bericht mit echten anonymisierten Kundenergebnissen prüfen.
- Die vollständige Zielmatrix auf physischem Android/iPhone, Safari und unterschiedlichen Druckdialogen abnehmen.

## Next

### Fachliche Arbeit

- Kataloginhalte nur aus bestätigter Fachgrundlage versioniert fortschreiben.
- Zusätzliche Problemfamilien oder Solution Patterns erst bei nachgewiesener fachlicher Lücke entscheiden.

### Technische Arbeit

- Den in den Mentor-Fällen nicht belegten Mehrwert des kleinen Solution-Workflow-Indexes nur noch an echten anonymisierten Fällen prüfen; bis dahin bleibt die deterministische Auswahl der gleichwertige Fallback.
- Datenschutzarmes Korrelations- und Aufbewahrungskonzept für persistentes Tracing entscheiden, bevor eine neue Observability-Komponente entsteht.
- Robustheit von Agent-Pattern-Treffern gegen reale Interviewformulierungen evaluieren; deterministische Guardrails unverändert beibehalten.
- Rückwärtskompatible View-Abbildung mit älteren produktiven Analysen beobachten und bei belegten Altformaten ergänzen.

### Produktarbeit

- Kundensprache und Vorschaukarten anhand realer Verständlichkeit weiter kürzen, ohne bestätigte Fakten zu verlieren.
- Optionale sekundäre Möglichkeiten nur bei nachgewiesenem Kundennutzen weiter ausgestalten.

## Later

### Technische Arbeit

- Echtes LLM-Function-Calling für klar typisierte interne Werkzeuge als getrennten, begrenzten Tool-Loop evaluieren.
- Vor einer Integration maximale Runden, maximale Toolaufrufe, Signaturwiederholung, Fallback und Offline-Evaluation spezifizieren.
- Den bestehenden kleinen Solution-Workflow-Index entfernen oder vereinfachen, falls auch Realfälle keinen Auswahlvorteil gegenüber der deterministischen Variantenwahl zeigen. Die Mentor-Stichprobe lieferte dieselben zwei Workflows und belegt keinen Vorteil.

### Produktarbeit

- Interviewtiefe, Patternabdeckung und Ergebnisdarstellung anhand wachsender realer Nutzung kalibrieren.

## Backlog-Ideen (nicht geplant)

- [Klickbarer Ergebnisprototyp](future-features/clickable-result-prototype.md) nach stabiler Klassifikation, eingebauten Output-Strukturen und fachlich geprüften Ergebnissen.

## Not planned

- Keine autonome Ausführung realer Unternehmensprozesse.
- Keine automatischen Preis-, Vertrags-, Zahlungs-, Qualitäts-, Personal-, Sicherheits-, Herausgabe- oder Freigabeentscheidungen.
- Kein breiter ungeprüfter Katalog beliebiger KI-Ideen.
- Keine Evaluation als Produktwissen.
- Keine neuen Datenbanktabellen, Frameworks, schweren PDF-Abhängigkeiten oder kostenpflichtigen APIs ohne bestätigten Bedarf und eigene Entscheidung.
- Kein automatisches Anhängen oder Versenden des PDF-Berichts; Kontakt bleibt ein `mailto:`-Link.
