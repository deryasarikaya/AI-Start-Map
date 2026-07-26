# Architektur des Diagnostic Interview Agent

## Begrenzter Auftrag

Der Agent diagnostiziert genau einen bestätigten Geschäftsprozess. Er darf fragen,
klären, Wissen suchen, die Analyse freigeben oder stoppen. Er besitzt keine Werkzeuge
zum Versenden, Bestellen, Buchen, Bezahlen, Verändern realer Systeme oder autonomen
Ausführen eines Unternehmensprozesses.

Zulässige Aktionen sind `ASK`, `CLARIFY`, `RETRIEVE`, `ANALYZE` und `STOP`.

## Werkzeuge

`extract_process_state` rekonstruiert aus gespeicherten Nutzerantworten und der
bestätigten Prozesswahl einen validierten State. Es trennt bestätigte Fakten,
unbestätigte Extraktionen, fachliche Ableitungen, Widersprüche und Unsicherheiten.

`search_diagnostic_knowledge` liefert ausschließlich `RagEvidence` mit Chunk-ID,
Typ und internem Text. Das Ergebnis wird nie in Nutzerfakten kopiert.

`evaluate_readiness_and_next_action` wendet zuerst deterministische Schutz- und
Budgetregeln an. Es liefert Aktion, Begründung, Informationslücke, mögliche Frage,
Unsicherheiten, Analysefreigabe und Stop-Grund.

## State-Trennung

Bestätigte Nutzerfakten entstehen nur durch ausdrückliche Aussagen oder bestätigte
Extraktionen. Eine Nutzerkorrektur ersetzt sie nicht still: der bisherige Wert wird
als überholt erhalten. Unbestätigte Extraktionen und fachliche Ableitungen bleiben
eigene Sammlungen. RAG-Evidenz ist ein eigener Typ. `unknown` und `skipped` sind
gültige Zustände und verhindern Wiederholungen.

Der State wird für die Demo aus den vorhandenen fünf Tabellen rekonstruiert:
Prozessgrenzen und Auswahl aus `process_options`, Antworten und Fragehistorie aus
`interview_questions`, Ergebnisdaten aus den bestehenden JSONB-Feldern. Deshalb ist
keine Migration erforderlich. Diese Rekonstruktion ist absichtlich kleiner als ein
späterer vollständig versionierter Persistenz-State.

## Deterministische Regeln

Nicht vom semantischen Retrieval abhängig sind:

- zentrale Agenten-, Tool- und Rückfragebudgets,
- höchstens vier sichtbare Rückfragen,
- keine Wiederholung beantworteter oder übersprungener Ziele,
- Schleifenstopp bei fehlendem Fortschritt,
- kein Überschreiben bestätigter Fakten durch RAG oder Ableitungen,
- `Weiß ich nicht` als gültige nicht blockierende Antwort,
- keine erfundene Unsicherheit oder fremde Fallinformation,
- Evaluationen niemals indexieren,
- keine autonome Prozess-, Preis-, Vertrags-, Zahlungs- oder Versandentscheidung.

## Batch-04-Klassifikation

| Inhalt | Verwendung |
|---|---|
| Entscheidungs-, Frage-, Widerspruchs-, Stop- und Tool-Patterns | optionaler Agent-Pattern-Index und Policy-Tests |
| kritische Agent-Guardrails | deterministischer Code plus Prompt-Guardrail; optional zusätzlich abrufbar |
| State-Schema, Reports, Spezifikation, Coverage und Merge-Gate | Dokumentation, nicht indexieren |
| `09_evaluation_cases.json` | Evaluation, `NEVER_INDEX` |

## Demo-Heuristiken

Die zentrale Konfiguration markiert ausdrücklich: normalerweise zwei bis drei,
maximal vier sichtbare Rückfragen; begrenzte Agenten- und Toolrunden; Analyse trotz
nicht blockierender Unsicherheiten; bei Budgetende Stop oder Analyse ohne erfundene
Ergänzung. Diese Werte sind keine universelle Forschungsaussage und müssen nach
echten Interviews kalibriert werden.

## Ablauf

Nach der Prozessbestätigung wird der State extrahiert und bewertet. Fehlende
blockierende Grenzen führen zu `ASK`, relevante Widersprüche zu `CLARIFY`. Nur wenn
Vergleichswissen die Diagnose oder Reifegradentscheidung ändern kann, folgt
`RETRIEVE`. Sobald Kernablauf und Engpass ausreichend sind oder das Budget erreicht
ist, folgt `ANALYZE` beziehungsweise `STOP`. Offene nicht blockierende Unsicherheiten
bleiben im Ergebnis sichtbar.
