# AI Start Map – Research-Erweiterung Batch 05 bis 08

Stand: 2026-08-06

Diese Erweiterung übersetzt die Forschungsgrundlage „Wie GenAI Kleinunternehmen konkret unterstützen kann“ in maschinenlesbare Wissensschichten.

## Schichten

| Batch | Inhalt | Stabilität | Für produktives Retrieval? |
|---|---|---|---|
| 05 | GenAI-Fähigkeiten und Entscheidungs-Gates | relativ stabil | ja, nach Merge-Gate |
| 06 | validierte Solution Patterns | relativ stabil | ja, nach Merge-Gate |
| 07 | Fehlanwendungen und Überautomatisierung | relativ stabil | Failure Patterns ja; Evaluationen nein |
| 08 | aktuelle Tools und Referenzarchitekturen | zeitkritisch/versioniert | nur separater Tool-Layer |

## Verbindliche Trennung

- `capability_pattern`: Was GenAI grundsätzlich leisten kann.
- `solution_pattern`: Wie eine vollständige betriebliche Lösung aussieht.
- `failure_pattern`: Woran eine Empfehlung oder Umsetzung scheitern kann.
- `tool_option`: Welche aktuelle Technik eine Teilfunktion abdecken kann.
- `evaluation_case`: Testdaten; niemals in den produktiven Index aufnehmen.

## Übergreifende Produktregel

GenAI erzeugt einen prüfbaren Entwurf. Deterministische Logik schützt Prozesswahrheit und Aktionen. Ein Mensch bestätigt folgenreiche Ergebnisse.

## Status

Die Dateien sind eine kuratierte, implementation-ready Forschungsgrundlage. Sie ändern noch keinen produktiven Index. Vor der Aufnahme müssen Schema-Kompatibilität, Retrieval-Gewichtung, Duplikate und Tests im echten Repository geprüft werden.
