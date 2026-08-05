# AI Start Map – Product Output Spec

**Status:** Needs Review
**Letzte Prüfung:** 2026-08-05
**Grund:** Der bisher verpflichtende Wochentest, genau drei Opportunities und einzelne Output-Verträge werden durch die neue Fachgrundlage fachlich überprüft. Die Prüfung ändert die aktuelle Laufzeit noch nicht.
**Verwandt mit:** `docs/product/AI_Start_Map_Fachgrundlage_Painpoints_Solutions_2026-08-05.md`, `docs/specs/solution-pattern-recommendation/`

_Stand: 26.07.2026_

## Statusabgrenzung

### Aktuell implementiert

- `FinalAnalysisResult` verlangt den unten beschriebenen Kernoutput einschließlich mindestens eines `weekly_test`-Schritts.
- Die Laufzeit speichert und rendert genau drei gerankte Opportunities.
- `required_prerequisites` verlangt mindestens einen Eintrag.
- Ergebnisansicht und Bericht zeigen den Wochentest im aktuellen Code.

### Fachlich bestätigt, aber noch nicht implementiert

- Kanaleignung, Prozess-/Datenreife und Automationsreife sollen getrennt bewertet werden.
- Ein strukturierter Solution-Katalog und deterministische Applicability-/Exclusion-Gates sollen die Lösungsauswahl steuern.
- Diagnose-RAG und Solution-Katalog sollen getrennte Rollen haben.

### Offene Punkte

- Bleibt der Wochentest für jeden Fall verpflichtend oder wird er situationsabhängig?
- Bleiben genau drei Opportunities Teil des Vertrags?
- Wie werden leichte Voraussetzungen dargestellt, ohne `required_prerequisites` künstlich aufzublähen?
- Welche Felder des neuen Solution-Patterns werden Teil der sichtbaren Kundenausgabe?

Die folgenden Abschnitte erhalten den vollständigen bisherigen Vertrag. „Verbindlich“ beschreibt bis zu einer beschlossenen und implementierten Änderung den aktuellen Codevertrag, nicht automatisch die künftige fachliche Zielentscheidung.

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
