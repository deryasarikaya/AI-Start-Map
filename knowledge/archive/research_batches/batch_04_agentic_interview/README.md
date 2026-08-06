# Batch 04 – Agentic Interview

## Ziel

Evidenzbasierte Research- und Evaluationsgrundlage für den begrenzten Diagnostic Interview Agent der AI Start Map. Kein autonomer Unternehmensagent.

## Inhalt

- 40 Quellen (25 primär, 15 sekundär)
- 60 Decision-Patterns
- 40 Next-Question-Patterns
- 25 Contradiction-/Clarification-Patterns
- 25 Stop-Regeln
- 25 Tool-Selection-Patterns
- 30 Guardrails
- 40 nicht indexierbare Evaluationsfälle

## Dateien

`00` Spezifikation, `01` Forschungsbericht, `02–06` Entscheidungs-/Frage-/Klärungs-/Stop-/Toolmuster, `07` State-Modell, `08` Guardrails, `09` Evaluation, `10` Quellen, `11` Coverage, `12` Quality Gate.

## Qualitätsaussagen

- Nutzerfakten, Agentenableitungen und Retrieval-Evidenz sind getrennt.
- Keine feste maximale Fragenzahl wird als universelle Evidenz behauptet.
- Projektheuristiken sind explizit markiert.
- Unknown, Skip, Korrektur und Unsicherheit bleiben erhalten.
- Evaluation bleibt strikt außerhalb des produktiven RAG.

## Abgrenzung

Batch 02/03 enthalten Unternehmensfälle und Prozessdiagnostik. Batch 04 enthält Interview-Entscheidungswissen. Es wurde nichts mit den 111 Chunks, Batch 02, Batch 03 oder FAISS zusammengeführt oder produktiv indexiert.

## Gate

**READY WITH CONDITIONS** – geeignet für den nächsten Schritt der implementierungsnahen Agent-Spezifikation, nicht für ungeprüften Merge.
