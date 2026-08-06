# Qualitätsprüfung und Merge-Gate – Research-Batch 02

## Validierter Lieferumfang

- 35 eindeutige Fall-IDs (`RB02-C01` bis `RB02-C35`)
- 35 Quellenregister-Einträge
- 162 valide JSONL-Chunks ohne doppelte `chunk_id`
- alle Pflichtmetadaten in jedem Chunk vorhanden
- 35 `case_evidence`-Chunks mit Quellen-URL
- 38 `interview_question_pattern`, 35 `minimal_viable_improvement` und 38 `automation_guardrail`
- alle zwölf vorgesehenen Chunk-Typen sind vertreten

## Quellenprofil

| Quellenstärke | Anzahl |
|---|---:|
| hoch | 16 |
| mittel | 15 |
| niedrig | 4 |

32 Fälle beruhen auf als primär eingeordneten öffentlichen Selbstauskünften. Drei Fälle sind als Zweitbericht (`is_primary_evidence=false`) markiert. „Primär“ bedeutet hier Selbstauskunft des Betriebs/der beteiligten Person, nicht unabhängige Prüfung.

## Bekannte Grenzen

1. Viele Fälle haben nur eine öffentlich zugängliche betriebsbezogene Quelle. Das Vertrauensniveau ist deshalb transparent abgestuft.
2. Reddit-Nutzernamen, Firmennamen und personenbezogene Angaben wurden nicht in den Korpus übernommen.
3. Einige Quellen enthalten Toolwünsche oder spätere Lösungen. Diese wurden nicht als Beweis des aktuellen Ist-Prozesses behandelt.
4. Digitale Reifegrade, Verbesserungstreppen, Diagnosefragen und Guardrails sind `expert_derived`.
5. Zeit- und Mengenangaben wurden nur übernommen, wenn sie im Quellenbericht standen; sie dürfen nicht auf andere Betriebe übertragen werden.
6. Branchen mit weiterhin dünner Evidenz: Schuhmacher, Textilreinigung, Uhren-/Schmuckreparatur, Instrumentenreparatur, Floristik und kleine Reiseanbieter.

## Merge-Gate vor Aufnahme in den Hauptkorpus

Ein Chunk darf erst in einen gemeinsamen Index, wenn:

- `batch_id=RB02` erhalten bleibt;
- `content_origin`, `is_primary_evidence` und `source_strength` nicht entfernt werden;
- Dubletten und nahe Fallähnlichkeiten gegen bestehende `pattern_ids` geprüft wurden;
- niedrige Quellenstärke beim Ranking abgewertet oder als Hypothesenquelle behandelt wird;
- Fallbelege, Fragen, minimale Verbesserungen und Guardrails getrennte Chunks bleiben;
- Quellenfälle in System-/Analyseprompts ausdrücklich als Vergleichsmuster, nicht als Nutzerfakten bezeichnet werden;
- Evaluationserwartungen in einer separaten Datei entstehen und nicht aus denselben Chunks als vermeintlicher Testdatensatz recycelt werden.

## Empfohlene Retrieval-Policy

1. Kandidaten zunächst semantisch nach Prozess und Geschäftsobjekt suchen.
2. Maximal zwei `case_evidence` je `pattern_id` zulassen.
3. Mindestens einen `diagnostic_pattern` oder `interview_question_pattern` ergänzen.
4. Mindestens einen `automation_guardrail` ergänzen.
5. `source_strength=low` nie als alleinige Evidenz einer Empfehlung verwenden.
6. Bei `digital_maturity_level` 0–1 zuerst `analog_workaround`, `implementation_prerequisite` und `minimal_viable_improvement` bevorzugen.
7. Entscheidungen über Preis, Termin, Zahlung, Bestellung, Qualität, Vertrag oder rechtlich relevante Dokumente nur mit menschlichem Freigabegate ausgeben.

## Prompt-Guardrail für AI Start Map

> Die gefundenen Quellenfälle dienen ausschließlich als Vergleichsmuster. Übernimm keine Mengen, Tools, Abläufe, Risiken oder Geschäftsdaten daraus als Fakten über das aktuell analysierte Unternehmen. Trenne belegte Nutzeraussagen, offene Fragen, fachliche Ableitungen und mögliche Zielabläufe. Wenn Objekt-ID, Pflichtfelder, Status, verantwortliche Person, Datenquelle oder Gerätekontext fehlen, frage zuerst nach oder empfehle eine minimale Ordnungsmaßnahme statt einer Automatisierung.

