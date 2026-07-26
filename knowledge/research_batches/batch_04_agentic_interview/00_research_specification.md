# Research-Spezifikation – Batch 04 Agentic Interview

Stand: 22. Juli 2026

## 1. Ziel

Batch 04 liefert evidenzbasiertes Entscheidungswissen für einen begrenzten Diagnostic Interview Agent der AI Start Map. Der Agent diagnostiziert einen ausgewählten betrieblichen Prozess, fragt gezielt nach, klärt relevante Widersprüche, ruft bei Bedarf kuratiertes Wissen ab und beendet das Interview rechtzeitig. Er führt keine betrieblichen Aktionen aus.

Die möglichen nächsten Aktionen sind ausschließlich `ASK`, `CLARIFY`, `RETRIEVE`, `ANALYZE` und `STOP`.

## 2. Abgrenzung

- keine Agentenimplementierung
- keine Änderung an Code, Prompts, Datenbank oder Retrieval
- kein Merge mit den 111 bestehenden Chunks, Batch 02, Batch 03 oder FAISS
- keine realen Fallinformationen als Fakten über den aktuellen Nutzer
- keine produktive Indexierung der Evaluationsfälle
- keine universellen starren Fragen oder unbelegten Grenzwerte

## 3. Zielgruppe

Solo-Selbstständige, Kleinstunternehmen und kleine Betriebe mit ungefähr 1–20 Mitarbeitenden in Deutschland. Die Interviewlogik muss auch analoge, papierbasierte, smartphone-only und physische Prozesse verarbeiten.

## 4. Forschungsfragen

1. Welche Prozessinformationen sind für eine belastbare Diagnose entscheidungsrelevant?
2. Wie wird die nächste Frage nach erwartetem diagnostischem Nutzen ausgewählt?
3. Wann ist eine Aussage widersprüchlich, ergänzend, zeitabhängig oder nur unklar?
4. Wann wird RAG benötigt, und wann genügt der vorhandene Nutzerzustand?
5. Wann reichen Informationen für Analyse oder Stop trotz verbleibender Unsicherheit?
6. Wie werden Tool-Schleifen, Wiederholungen, Erfindungen und unnötige Belastung verhindert?
7. Wie werden State-Konsistenz und Gesprächsqualität evaluiert?

## 5. Quellenstrategie

Priorität haben peer-reviewte Primärarbeiten, wissenschaftliche Surveys, offizielle Standards, staatliche Prozess- und UX-Leitfäden, offizielle Risiko-/Datenschutzdokumente und offizielle technische Dokumentation. Marketingmaterial ohne Methodik ist ausgeschlossen. Neuere Preprints werden höchstens mittel gewichtet.

## 6. Qualitätskriterien

- jede Regel besitzt Quellen-IDs, Quellenstärke und `content_origin`
- `direct_evidence`: eng an eine Quelle gebundene Aussage
- `multi_source_inference`: transparente Übertragung mehrerer Quellen auf AI Start Map
- `project_heuristic`: produktbezogene, später zu validierende Regel
- unbekannte Angaben bleiben unbekannt
- bestätigte Nutzerfakten werden nicht still überschrieben
- Frageauswahl muss einen möglichen Einfluss auf Diagnose, Priorisierung, Sicherheit oder Umsetzbarkeit benennen
- Stop-Regeln berücksichtigen Informationsnutzen und Nutzerbelastung

## 7. Geplante Chunk-Typen

- `agent_decision_pattern`
- `next_question_pattern`
- `contradiction_pattern`
- `agent_stop_rule`
- `tool_selection_pattern`
- `agent_guardrail`

## 8. Ausschlusskriterien

Ausgeschlossen werden reine Plausibilitätsregeln ohne Kennzeichnung, autonome Unternehmensaktionen, medizinische/rechtliche Beratung, sensible Fragen ohne diagnostische Notwendigkeit, Fallübernahmen aus fremden Unternehmen, unbegrenzte Tool- oder Frageschleifen und starre universelle Fragezahlen.

## 9. Bezug zu Batch 02 und 03

Batch 02/03 liefern Fall-, Prozess-, Reifegrad-, Voraussetzung- und Guardrailwissen. Batch 04 darf diese Inhalte später abrufen, enthält aber selbst keine neuen Unternehmensfälle. Retrieval-Evidenz bleibt von Nutzerfakten getrennt.

## 10. Research versus Produktheuristik

Forschung stützt Prinzipien wie expliziten Dialogue State, erwarteten Informationswert, fokussierte Fragen, Akzeptanz von „weiß ich nicht“, adaptive Belastungssteuerung und Iterationsgrenzen. Konkrete Schwellenwerte, Gewichtungen und maximale Follow-up-Zahlen sind produktspezifisch und müssen anhand echter AI-Start-Map-Sessions kalibriert werden.
