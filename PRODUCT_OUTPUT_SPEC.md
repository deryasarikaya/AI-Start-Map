# AI Start Map – Product Output Spec

_Stand: 26.07.2026_

## Verbindlicher Kernoutput

Jede neue Analyse erzeugt mit `FinalAnalysisResult` zuerst folgende Kundenausgabe:

| Feld | Sichtbare Bedeutung | Grenze |
|---|---|---|
| `core_problem` | Dein eigentliches Problem | ein verständlicher Satz |
| `first_change` | Das solltest du zuerst ändern | eine konkrete priorisierte Maßnahme |
| `ai_support` | konkrete Einordnung der KI-Hilfe | keine generische Optimierungsfloskel |
| `ai_input` | Eingabe des Menschen | nur vorhandene oder realistisch erfassbare Angaben |
| `ai_task` | Aufgabe der KI | erkennen, ordnen, extrahieren oder formulieren |
| `ai_output` | konkretes Ergebnis | prüfbarer Entwurf oder strukturierte Ausgabe |
| `human_check` | menschliche Kontrolle | Freigabe und Entscheidung sichtbar |
| `weekly_test` | Test für diese Woche | ein bis drei sichtbare Schritte |
| `weekly_test_success` | Erfolgskriterium | beobachtbar, ohne erfundene Zahl |
| `later_automation` | späterer Ausbau | genau ein realistischer nächster Schritt |

Ergänzend werden `why_this_first`, `required_prerequisites`, `human_decisions`, `uncertainties`, `current_process_summary` und `optional_details` strukturiert erzeugt. Die tieferen drei `opportunities` und der bestehende Blueprint bleiben für Rückwärtskompatibilität und optionale Vertiefung erhalten, bestimmen aber nicht mehr die primäre sichtbare Hierarchie.

## Ehrlichkeit und Grounding

- Fehlende Angaben bleiben Unsicherheiten.
- RAG-Inhalte sind Vergleichswissen und niemals Nutzerfakten.
- Bestätigte Nutzerfakten werden nicht durch Retrieval oder Modellannahmen überschrieben.
- Gibt es noch keine sinnvolle KI-Grundlage, beginnt `ai_support` sinngemäß mit „KI ist heute noch nicht der erste Schritt“ und nennt die notwendige Voraussetzung.
- Preise, Verträge, Zahlungen, Qualität, Ausnahmen und unklare Zuordnungen bleiben menschliche Entscheidungen.
- Erfundene Tools, APIs, Geräte, Datenquellen, Einsparungszahlen und fremde Fallinformationen sind unzulässig.

## Speicherung und Kompatibilität

Der neue Kernoutput wird ohne Migration im vorhandenen JSONB-Feld `analyses.uncertainties` unter `core_output` gespeichert. Bestehende Analysen ohne diesen Block werden über `_result_view` auf lesbare Fallbacks abgebildet. Neue Structured Outputs verlangen die neuen Felder im JSON-Schema.

## Kundendarstellung

Der erste Ergebnisbereich zeigt ausschließlich die fünf Kernpunkte. Startplan und Diagnosekontext sind standardmäßig geschlossen. Interne IDs, Wissensreferenzen, Prompts, Modellnamen, Logs und Scores durchlaufen vor der Ausgabe weiterhin die vorhandenen Sicherheitsprüfungen.
