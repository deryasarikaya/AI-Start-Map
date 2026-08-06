# Evaluationsbericht Diagnostic Interview Agent

**Status:** Archived
**Hinweis:** Historischer Evaluationsnachweis. Der aktuelle verifizierte Teststand wird in `docs/PROJECT_STATE.md` dokumentiert.

Stand: 26. Juli 2026

## Ergebnis

Die vollständige automatisierte Projektsuite besteht mit 69 von 69 Tests. Die
fokussierte Agenten-/RAG-Suite besteht mit 18 von 18 Tests. Alle 40
Batch-04-Fälle liefern die erwartete nächste Aktion. Keine der insgesamt 79
Evaluationen ist in einem Diagnose- oder Agent-Pattern-Index enthalten.

Die OpenAI- und Embedding-Aufrufe sind in pytest gemockt. Zusätzlich wurden die real
erstellten Indizes strukturell geprüft und mit drei echten Embedding-Abfragen
verglichen. Das ist eine technische Demo-Freigabe, aber noch keine Kalibrierung der
Fragezahl mit realen Nutzern.

Ein anonymer Massage-Demofall wurde zusätzlich über den lokal gestarteten Server mit
der konfigurierten Modell- und Retrieval-Pipeline ausgeführt. Einstieg, Analyse,
Ergebnis und Druckbericht antworteten erfolgreich; der priorisierte Startpunkt und
die Browser-Druckfunktion waren vorhanden.

## Verwendete Evaluationsbestände

| Bestand | Fälle | Automatisierte Nutzung |
|---|---:|---|
| `knowledge/evaluation/evaluation_cases.json` | 25 | Schema, eindeutige IDs, verbotene Empfehlungen, Freigaben, Indexausschluss und bestehende Qualitäts-/Demo-Tests |
| Batch 03 `06_evaluation_cases.json` | 14 | Schema, eindeutige IDs, Diagnose-Gates, verbotene Verhaltensweisen, Indexausschluss und Szenarioabdeckung |
| Batch 04 `09_evaluation_cases.json` | 40 | erwartete nächste Aktion 40/40, State-/Tool-/Stop-Policy und Indexausschluss |

## Geforderte Schwerpunktszenarien

| Szenario | Prüfpfad | Status |
|---|---|---|
| Schuhreparatur mit Papierzetteln und Regalsuche | Batch 03 RB03-E01, Reifegrad 0, realer Retrievalvergleich | bestanden |
| Drittabholung | Batch 03 RB03-E02, menschliche Freigabe/keine autonome Herausgabe | bestanden |
| Massagesalon mit mehreren Kanälen | bestehender Massage-Demofall und Qualitätsfluss | bestanden |
| begrenzte Personalverfügbarkeit | bestehende Evaluation und Diagnose-Retrieval | bestanden |
| Handwerksbetrieb mit Angebot und Aufmaß | bestehender C-01-Fall, Preis- und Bestellfreigabe | bestanden |
| Smartphone-only Betrieb | Batch 03 RB03-E06, Reifegrad 1 | bestanden |
| Betrieb ohne digitale Auftragsdaten | Reifegrad-0-State und Ordnung-vor-Digitalisierung | bestanden |
| widersprüchliche Angaben | `CLARIFY` vor Analyse | bestanden |
| Nutzer sagt `Weiß ich nicht` | Unsicherheit bleibt erhalten, Frage wird nicht wiederholt | bestanden |
| bereits beantwortete Information | beantwortete/übersprungene Informationslücke wird nicht erneut gewählt | bestanden |
| scheinbarer Widerspruch | Batch-04-Aktionsorakel | bestanden |
| fehlender Prozessstart | `ASK` mit Lücke `process_start` | bestanden |
| fehlendes Prozessende | `ASK` mit Lücke `process_end` | bestanden |
| Automatisierung ist noch nicht sinnvoll | Analyse erlaubt Standardisierung/Digitalisierung als ersten Schritt | bestanden |
| Standardisierung muss zuerst erfolgen | Prompt-, Schema- und Qualitätsprüfung | bestanden |
| Preisfreigabe bleibt menschlich | realer Retrievalvergleich und Guardrail-Prüfung | bestanden |

## Bewertete Dimensionen

- nächste Aktion und relevante Informationslücke,
- keine Wiederholung beantworteter oder übersprungener Fragen,
- richtige Toolgrenzen und Abbruch wiederholter Tool-Signaturen,
- Stop bei Nutzerwunsch, Budget oder autonomer Ausführungsanforderung,
- technische Trennung von Fakten, Extraktionen, Ableitungen, RAG und Unsicherheit,
- digitale Reifestufe 0, 1 und 2,
- Erhalt menschlicher Preis-, Qualitäts-, Vertrags- und Zahlungsfreigaben,
- exakt drei priorisierte Startpunkte in der Ergebnis-Pipeline,
- keine internen IDs oder fremden Fallfakten in sichtbaren Ergebnissen.

## Offene Grenzen

Es scheitert aktuell kein automatisierter Fall. Noch nicht empirisch belegt sind die
optimalen Grenzwerte für zwei bis drei normale, vier maximale Rückfragen sowie acht
Agenten- und sechs Werkzeugrunden. Diese zentralen Demoheuristiken müssen anhand
echter AI-Start-Map-Interviews kalibriert werden. Vor öffentlichem Produktivbetrieb
bleiben außerdem manuelle visuelle Abnahmen auf Chrome/Android und Safari/iPhone
sowie wiederholte Live-Modell-Stichproben sinnvoll.
