# Forschungsbericht – Batch 04 Agentic Interview

## Executive Summary

Die Forschung stützt einen begrenzten, state-basierten Interview Agent. Der Agent sollte nicht versuchen, „alles“ zu erfragen. Er sollte nach jedem Turn prüfen, welche noch offene Information die Diagnose, Empfehlungsrangfolge, Umsetzbarkeit oder Sicherheit tatsächlich verändern kann. Die Entscheidung zum Fragen ist als erwarteter Nutzen minus Kommunikationskosten zu behandeln. Das ist die zentrale, robuste Mehrquellen-Ableitung aus Clarification Research, Dialogue State Tracking, Prozessaufnahme und Survey-UX.

## 1. Informationsvollständigkeit

Standards und Prozessleitfäden konvergieren auf einen Kern aus Auslöser/Start, Ergebnis/Ende, Schrittfolge, Inputs/Outputs beziehungsweise Informationsobjekten, Beteiligten, Übergaben, Entscheidungen, Status, Ausnahmen und Kontrollen [S01–S04]. Für AI Start Map kommen diagnostische Felder wie Häufigkeit, Warte-/Suchaufwand, Fehler, Nacharbeit, digitale Grundlage, Daten, Umgebung und menschliche Freigaben hinzu; dies ist eine projektbezogene Synthese aus Prozessanalyse und Risikoleitplanken [S03, S04, S27–S30].

**Ableitung für AI Start Map:** Vollständigkeit ist entscheidungsbezogen. Start, Ende, Hauptschritte und Hauptproblem sind grundsätzlich Kernfelder; weitere Felder werden nur dann blockierend, wenn sie Engpass, Rangfolge, Risiko oder Machbarkeit verändern.

## 2. Nächste wertvollste Frage

Rao und Daumé modellieren gute Klärungsfragen über den erwarteten Wert ihrer Antwort [S09]. Neuere Human-Agent-Arbeiten verbinden Mehrdeutigkeit, Aufgabenrisiko und kognitive Kosten [S14, S15]. Active-Learning-Forschung liefert eine hilfreiche Analogie, darf aber nicht direkt als Interviewgesetz übertragen werden [S16, S17].

**Ableitung für AI Start Map:** Eine Kandidatenfrage wird anhand von fünf Kriterien bewertet: offene State-Lücke, möglicher Diagnoseeffekt, möglicher Rangfolgeneffekt, Risiko-/Freigabeeffekt und Nutzerbelastung. Fragen ohne klaren Effekt werden verworfen. Pro Turn wird ein primäres Thema gefragt.

## 3. Klärung und Widersprüche

Requirements Elicitation zeigt, dass Mehrdeutigkeit, unterschiedliche Perspektiven, Änderungen und unvollständige Kommunikation normale Ursachen inkonsistenter Beschreibungen sind [S05]. Dialogue State Tracking verlangt Updates über den Gesprächsverlauf [S06–S08]. Nicht jede Abweichung ist ein Widerspruch: Zeitstände, Varianten, Ausnahmefälle, Bandbreiten oder verschiedene Rollen können Aussagen kompatibel machen; diese Differenzierung ist eine AI-Start-Map-Ableitung aus den genannten Quellen.

**Ableitung für AI Start Map:** Vor `CLARIFY` werden Zeit, Prozessvariante, Geltungsbereich und Schätzcharakter geprüft. Klärungsfragen beschreiben neutral die zwei Aussagen und bitten um die gültige Regel. Bestätigte Korrekturen werden versioniert.

## 4. Stop-Regeln und Nutzerbelastung

Survey- und UX-Forschung zeigt, dass Schwierigkeit, Länge, Position und wahrgenommene Belastung Antwortqualität und Abbruch beeinflussen können; Effekte und Schwellen sind kontextabhängig [S22–S26]. GOV.UK verlangt einen klaren Verwendungszweck für jede Frage, relevante Verzweigung und die Möglichkeit „Ich weiß es nicht“ zu antworten [S19–S21]. In den geprüften Quellen wurde keine belastbare universelle Maximalzahl speziell für diesen KMU-Agenten gefunden.

**Ableitung für AI Start Map:** Stop, wenn die Analyse stabil ist, der Nutzer beendet/überspringt, eine Information unbekannt bleibt und nicht blockiert, kein relevanter Informationsgewinn verbleibt oder eine Loop-/Budgetgrenze erreicht ist. Die konkrete Budgetzahl ist Projektheuristik und muss mit realen Sessions kalibriert werden.

## 5. ASK, CLARIFY, RETRIEVE, ANALYZE, STOP

- `ASK`: fehlender Nutzerfakt mit mittlerem/hohem diagnostischem Effekt.
- `CLARIFY`: relevante Mehrdeutigkeit oder Inkonsistenz, die State oder Ergebnis verändert.
- `RETRIEVE`: externes Diagnose-, Reifegrad-, Voraussetzung- oder Guardrailwissen wird benötigt.
- `ANALYZE`: Mindest-State reicht; offene Unsicherheiten sind sichtbar und nicht blockierend.
- `STOP`: keine weitere sinnvolle Frage, Nutzerwunsch, Grenze/Loop oder dauerhaft unzureichender Kern-State.

## 6. Tool-Auswahl

Tool- und Agent-Benchmarks zeigen, dass einzelne korrekte Calls nicht genügen: relevant sind Auswahl, Abstention, Reihenfolge, State-Konsistenz, Policy-Einhaltung, Fehlerbehandlung und Endzustand [S31–S34]. Offizielle technische Dokumentation stützt explizite Schemas, Tool-Ergebnisse, Bestätigung bei realen Auswirkungen und Iterationsgrenzen [S35–S37].

**Ableitung für AI Start Map:** Nach einer neuen Nutzerantwort wird zuerst der State aktualisiert. Danach wird Readiness/Next Action bewertet. Retrieval folgt nur einem expliziten Wissensbedarf und darf Nutzerlücken nie mit Fremdfällen füllen. Identische Tool-Calls ohne Zustandsfortschritt werden gestoppt.

## 7. Agent State

Dialogue State Tracking stützt einen expliziten, fortgeschriebenen Zustand [S06, S07]. Ein starres Slot-System ist für offene KMU-Prozesse jedoch zu eng; unbekannte Werte und dynamische Varianten müssen zulässig bleiben [S08].

**Ableitung für AI Start Map:** State-Felder sind schema-geführt, aber offen für Listen und Unsicherheiten. Jeder Wert trägt Herkunft und Status. Nutzerfakt, Agentenableitung und Retrieval-Evidenz bleiben getrennt.

## 8. Vertrauen, Unsicherheit und Human Oversight

NIST, DSK und EU-Leitplanken unterstützen dokumentierte Risiken, Datenminimierung, Provenienz, menschliche Aufsicht und das Vermeiden von Übervertrauen [S27–S30, S38]. Die rechtliche Einordnung der AI Start Map ist nicht Bestandteil dieses Batchs.

**Ableitung für AI Start Map:** Preis-, Vertrags-, Zahlungs-, Freigabe- und andere wirkungsvolle Entscheidungen bleiben menschlich. Der Interview Agent führt überhaupt keine externen Unternehmensaktionen aus. Unsicherheiten erscheinen im Analyse-Handoff.

## 9. Evaluation

AgentBench, tau-bench, ToolTalk und BFCL stützen szenario-, trajectory- und endzustandsbasierte Evaluation [S31–S34]. Für AI Start Map reicht Textqualität allein nicht; dies ist die direkte Evaluationsableitung für das Projekt.

**Ableitung für AI Start Map:** Zu messen sind richtige Aktion, relevante/nicht wiederholte/nicht suggestive Frage, korrekte Tool-Auswahl oder Abstention, State-Patch, Widerspruchsbehandlung, Stop-Zeitpunkt, Unsicherheitserhalt, Guardrail-Einhaltung und Analysebereitschaft. Evaluationsfälle bleiben außerhalb des RAG-Index.

## 10. Widersprüchliche oder begrenzte Evidenz

- Einzelne Fragen reduzieren kognitive Komplexität, können aber Gesamtdauer erhöhen.
- Frageposition kann Ermüdung oder Lerneffekte zeigen; Befunde sind gemischt.
- „Weiß ich nicht“ kann echte Wissensgrenze, Schwierigkeit oder Satisficing bedeuten; der Agent darf es nicht pauschal als schlechte Antwort behandeln.
- Active Learning ist nur eine Analogie zur Interviewfrageauswahl.
- Neuere 2026-Arbeiten zu Value of Information und Uncertainty-Aware Clarification sind vielversprechend, aber noch nicht breit repliziert.

## 11. Offene Forschungslücken

1. Keine Feldstudie bestimmt die optimale Rückfragetiefe speziell für deutsche Kleinstbetriebe.
2. Keine publizierte Ontologie definiert universelle Mindestfelder für alle operativen KMU-Prozesse.
3. Gewichtung von Informationsgewinn, Nutzerbelastung und Risiko muss mit echten AI-Start-Map-Sessions kalibriert werden.
4. Sprachinput benötigt eigene Tests für ASR-Unsicherheit, Unterbrechungen und Selbstkorrekturen.
5. LLM-basierte User-Simulation darf reale Nutzerstudien nicht ersetzen.

## 12. Wichtigste belastbare Aussagen

1. Expliziter, fortgeschriebener Dialogue State ist zentral.
2. Gute nächste Fragen müssen downstream nützlich sein.
3. Nicht jede Abweichung ist ein Widerspruch.
4. „Unknown“ und „Skip“ sind legitime Zustände.
5. RAG-Evidenz ist kein Nutzerfakt.
6. Tool-Loops brauchen harte Grenzen und Fortschrittsprüfung.
7. Analysebereitschaft ist wichtiger als maximale Datensammlung.
8. Evaluation muss ganze Gesprächstrajektorien und State-Updates prüfen.
