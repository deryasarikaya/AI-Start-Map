# Qualitätsprüfung und Merge-Gate – Batch 04

## Validierter Umfang

- 40 recherchierte Quellen
- 60 Agent-Decision-Patterns
- 40 Next-Question-Patterns
- 25 Contradiction-/Clarification-Patterns
- 25 Stop-Regeln
- 25 Tool-Selection-Patterns
- 30 Agent-Guardrails
- 40 separate Evaluationsfälle

## Quellenprofil

- Primärquellen: 25
- Sekundärquellen: 15
- Quellenstärke hoch: 32
- Quellenstärke mittel: 8
- Quellenstärke niedrig: 0

## Herkunft der maschinenlesbaren Regeln

- direct_evidence: 0
- multi_source_inference: 133
- project_heuristic: 72

Viele Datensätze sind bewusst `multi_source_inference`: Forschung liefert Prinzipien, aber nicht fertige AI-Start-Map-Regeln. Konkrete Budget-, Retry-, Ranking- und State-Regeln sind als Projektheuristik markiert.

## Regelprüfung

- Chunk-IDs sind eindeutig.
- Alle Pattern-Datensätze tragen `batch_id`, Quellen-IDs, Quellenstärke und Herkunft.
- Keine Regel übernimmt einen fremden Unternehmensfall als Nutzerfakt.
- Keine universelle maximale Rückfragezahl wird als Forschungsfakt behauptet.
- `unknown`, `skipped`, Schätzung und Korrektur bleiben unterscheidbar.
- ASK/CLARIFY/RETRIEVE/ANALYZE/STOP sind getrennt.
- Tool-Auswahl enthält Loop-Risiko und Fallback.
- Preis, Vertrag, Zahlung und andere reale Wirkungen bleiben menschlich; der Agent besitzt keine Aktionstools.
- Evaluationsdatei ist mit `NEVER_INDEX` markiert.

## Dubletten und Widersprüche

Semantische Nähe ist bei Sicherheitsregeln beabsichtigt, aber Auslöser unterscheiden sich. Potenzielle Spannung zwischen „eine Frage pro Turn“ und Gesprächsdauer ist dokumentiert: fokussierte Fragen verbessern Verständlichkeit, können aber mehr Turns erzeugen. Daher steuert nicht eine feste Turnzahl, sondern erwarteter diagnostischer Nutzen plus konfigurierbares Budget.

## Risiken vor Implementierung

1. LLM-Selbsteinschätzung allein ist keine verlässliche Readiness-Messung.
2. Eine numerische Information-Gain-Schätzung wäre ohne Kalibrierungsdaten Scheingenauigkeit.
3. Semantische Wiederholungserkennung braucht Tests gegen Paraphrasen.
4. State-Patches müssen schema-validiert und versioniert werden.
5. Tool-Loop-Limits und Follow-up-Budgets müssen konfigurierbar sein.
6. Voice-Sessions benötigen ASR-spezifische Unsicherheitsfälle.
7. Reale deutsche KMU-Nutzerstudien fehlen noch.

## Bedingungen für einen späteren Merge

1. Nur Pattern-Dateien 02–08 prüfen; Datei 09 nie indexieren.
2. Agentenwissen in eigenem Retrieval-Bereich halten; nicht mit `case_evidence` vermischen.
3. `content_origin=project_heuristic` niedriger gewichten und separat evaluieren.
4. Quellen-IDs und Provenienz erhalten.
5. Keine Regel direkt als Prompt-Wahrheit übernehmen; zuerst in ausführbare Policy mit Tests übersetzen.
6. Retrieval von Batch 02/03 darf niemals State-Felder mit Nutzerfakten befüllen.
7. Vor Produktion mindestens alle 40 Evaluationen plus paraphrasierte Varianten ausführen.

## Merge-Gate-Entscheidung

**READY WITH CONDITIONS**

Der Batch ist als Research- und Designgrundlage geeignet. Er ist noch nicht bereit für ungeprüfte produktive Indexierung oder direkte Agentenimplementierung. Zuerst müssen konkrete State-Schemas, Policy-Prioritäten, Budgetwerte und Tool-Verträge implementierungsnah spezifiziert und gegen reale Session-Traces kalibriert werden.
