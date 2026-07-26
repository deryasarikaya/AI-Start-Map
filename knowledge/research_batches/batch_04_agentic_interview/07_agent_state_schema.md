# Fachliches Agent-State-Modell

Noch kein Datenbankmodell. Dieses Schema beschreibt die fachliche Trennung von Nutzerfakten, Ableitungen und Unsicherheit.

## Grundprinzip

Jeder gespeicherte Wert benötigt mindestens `value`, `status`, `origin`, `turn_id` und optional `confidence_note`. Zulässige Statuswerte: `candidate`, `confirmed`, `corrected`, `unknown`, `skipped`, `superseded`. `origin` ist `user_statement`, `user_confirmation`, `agent_inference` oder `retrieved_evidence`.

## Felder

| Feld | Typ | Pflicht | Herkunft | Erlaubte Updates |
|---|---|---:|---|---|
| session_context | object | ja | System + Nutzer | ergänzen; keine Prozessfakten hineinmischen |
| selected_process | string/object | ja vor Interview | Nutzerwahl | Wechsel nur nach Bestätigung |
| confirmed_process_title | string | ja vor Analyse | Nutzerbestätigung | versioniert korrigieren |
| process_start | fact | ja vor Analyse | Nutzer | candidate → confirmed/corrected/unknown |
| process_end | fact | ja vor Analyse | Nutzer | wie process_start |
| as_is_steps | ordered fact[] | ja vor Analyse | Nutzer + bestätigte Extraktion | Schritte ergänzen, ordnen, versionieren |
| actors | fact[] | bedingt | Nutzer | Rollen statt unnötiger Klarnamen bevorzugen |
| channels | fact[] | bedingt | Nutzer | Varianten/Zeitstände getrennt halten |
| tools | fact[] | optional | Nutzer | nichts aus Fremdfällen ergänzen |
| information_objects | fact[] | bedingt | Nutzer | physisch/digital kennzeichnen |
| status_transitions | fact[] | bedingt | Nutzer | nur beobachtbare Zustände speichern |
| exceptions | fact[] | optional, wichtig bei hoher Quote | Nutzer | Normalfall und Ausnahme trennen |
| frequency | estimate/unknown | optional | Nutzer | Einheit und Zeitraum bewahren |
| volume | estimate/unknown | optional | Nutzer | Bandbreite zulassen |
| pain_points | fact[] | ja | Nutzer | konkrete Auswirkung ergänzen |
| bottleneck_candidates | inference[] | ja vor Analyse | Agentenableitung | nie als Nutzerfakt markieren |
| digital_maturity | inference + evidence | ja vor Empfehlung | gemischt | aus belegten Fakten ableiten; Unsicherheit erhalten |
| available_data | fact[] | bedingt | Nutzer | Zugriff und Qualität getrennt erfassen |
| human_approvals | fact[] | ja bei kritischen Entscheidungen | Nutzer + Guardrail | niemals durch RAG-Fall ersetzen |
| constraints | fact[] | optional | Nutzer | Akzeptanz/Umgebung/Technik trennen |
| contradictions | object[] | ja als Sammlung | Agentkandidat | erst nach Klärung schließen |
| uncertainties | object[] | ja als Sammlung | Nutzer/Agent/ASR/Tool | blocking und nonblocking markieren |
| answered_questions | question_record[] | ja | System | semantisches Zielfeld speichern |
| skipped_questions | question_record[] | ja | Nutzer/System | nur kritisch begründet erneut anbieten |
| follow_up_count | integer | ja | System | monoton je Prozess; Resume fortsetzen |
| retrieved_evidence | evidence_ref[] | optional | RAG | nie in Nutzerfakten kopieren |
| readiness_status | enum | ja | Agentenableitung | `insufficient`, `clarify`, `retrieve`, `ready`, `blocked` |
| next_action | enum | ja | Policy | ASK/CLARIFY/RETRIEVE/ANALYZE/STOP |
| stop_reason | enum/string | bei STOP | Policy | explizit und prüfbar |
| tool_call_history | object[] | ja | System | Call-Signatur, Ergebnis, Fehler, Fortschritt |
| confirmation_status | enum | ja | Nutzer/System | draft/partially_confirmed/confirmed/corrected |
| resume_status | enum | ja | System | active/paused/resumed/completed |

## Überschreiben bestätigter Fakten

Bestätigte Fakten werden nie gelöscht. Eine klare Nutzerkorrektur erzeugt eine neue Version; die alte wird `superseded`. Bei unklarer Abweichung bleiben beide Aussagen Kandidaten und die nächste Aktion ist nur dann `CLARIFY`, wenn die Abweichung diagnostisch relevant ist.

## Unknown und Skip

`unknown` ist eine gültige Antwort mit Herkunft. `skipped` ist eine bewusste Nichtantwort. Beide verhindern Wiederholungen. Ein erneutes Angebot ist nur zulässig, wenn eine sicherheitskritische oder analyseblockierende Information betroffen ist; der Grund muss nutzerverständlich genannt werden.

## Session-Wiederaufnahme

Bei Resume wird der letzte valide State geladen. Zeitabhängige Angaben wie Tools, Zuständigkeiten und Ablaufvarianten werden nicht ungeprüft als aktuell angenommen. Ein neuer Prozess erhält einen eigenen Process-State; nur ausdrücklich gemeinsame Session-Kontexte werden referenziert.

## Trennung der Wissensarten

- Nutzerfakt: nur explizite Aussage oder bestätigte Extraktion.
- Ableitung: Engpass, Reifegrad, Readiness und nächste Aktion.
- Retrieval-Evidenz: externes Vergleichs- oder Guardrailwissen.
- Unsicherheit: fehlend, mehrdeutig, widersprüchlich, geschätzt, ASR-unsicher oder Tool-fehlerbedingt.
