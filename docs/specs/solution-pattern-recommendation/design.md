# Design – Solution-Pattern-Recommendation

**Status:** Active – implemented, integrated and tested
**Datum:** 2026-08-06 (Revision: Katalog v2 und LLM-Klassifikation mit deterministischem Fallback)
**Geltung:** Verbindliches Design; Implementierungs-, Integrations- und Teststatus werden getrennt geführt.

## Verbindlicher Zielpfad

```text
bestätigte Nutzerfakten
→ LLM-Klassifikation von Problemfamilien und Gates (Structured Output,
  Katalogdefinitionen als Kontext, deterministischer Keyword-Fallback
  nur bei API-Fehlern)
→ sechs getrennte Gates
→ validierter Solution-Katalog
→ primäre Empfehlung plus 0–2 sekundäre Kandidaten
→ kompakter Structured Output
→ Pydantic-, Grounding- und Sprachvalidierung
→ JSONB-Persistenz und kurze HTML-/Druckdarstellung
```

## Katalog v2 und Research-Grundlage

Katalogversion `2026-08-06-v2` ergänzt die bestehenden zwölf Problemfamilien,
zehn Solution Patterns und die Matrix um neun GenAI-Capabilities `GAI-01` bis
`GAI-09`, sechs fachliche Gates `GATE-01` bis `GATE-06`, zwölf Failure Patterns
`FAIL-01` bis `FAIL-12`, die Autonomiestufen `A0` bis `A5` und zehn
Nicht-GenAI-Mechanismen. Problemfamilien und Solution Patterns tragen die
zugehörigen Research-Felder aus Batch 05 bis 07.

Diese Felder werden geladen und auf IDs, Referenzen und Autonomiegrenzen
validiert. Der bestehende Selector nutzt sie noch nicht fachlich; seine Logik
bleibt in diesem Datenpaket unverändert. Batch 08 wird unverändert als
zeitkritische Tool- und Architektur-Researchgrundlage versioniert, ist aber
weder in den Laufzeitkatalog noch in einen produktiven Index integriert.

## Klassifikation: LLM mit deterministischem Fallback

Die frühere deterministische Stichwort-Klassifikation ist als primärer Pfad
abgelöst. Gemessene Ursachen (Baseline 2026-08-06, 91 Evaluationsfälle):
48 % Default-Fallback auf `PF-01`, PF Top-1 28 %, SP Top-1 30 %, `PF-03` und
`PF-11` ohne Regel technisch unerreichbar, Gates zu 82–99 % auf demselben Wert.

Neuer verbindlicher Pfad (`app/llm_classification.py`):

- Ein Structured-Output-Aufruf erhält die bestätigte Erzählung sowie die zwölf
  Problemfamilien-Definitionen (`definition`, `typical_statements`, `symptoms`,
  `common_causes`) und die sechs Gate-Definitionen aus Katalog v2 als Kontext.
- Das Modell liefert ein bis drei Problemfamilien-IDs als Enum (keine
  erfundenen IDs möglich), je Familie ein wörtliches Belegzitat aus der
  Erzählung, sechs Gate-Werte mit `unknown` als ausdrücklich erlaubtem Wert
  sowie `physical_object` und `real_location_known`.
- Die Stichwort-Funktionen `classify_problem_families()` und
  `infer_decision_gates()` bleiben unverändert erhalten und dienen
  ausschließlich als Fallback bei API-Fehlern (`AIServiceError`). Der genutzte
  Pfad wird geloggt.
- Selector, Matrix, Ausschlussregeln, UI, Bericht, Regex-Filter, Agent-Layer
  und Indizes bleiben unverändert. Der Agent-Layer nutzt weiterhin die
  deterministische Gate-Heuristik; seine Umstellung ist eine getrennte
  Entscheidung.

Problemfamilien und Patterns liegen als versionierte JSON-Dateien außerhalb aller Evaluationspfade. Der Loader validiert Anzahl, IDs, Referenzen und Kernfelder. Der Selector liefert Auswahl, Ausschlussgründe, Voraussetzungen, Fehlergrenzen und Freigabegrenzen. Der neue Kernoutput liegt in bestehendem JSONB; die View-Schicht liest neue und alte Analysen. Neue Seiten zeigen keinen Wochentest.

Das Analyse-Retrieval balanciert Diagnose, konkretes `automation_pattern`, Voraussetzung und Guardrail. Agentenpatterns unterstützen nur die Wahl einer entscheidungsrelevanten Lücke oder Aktion. Budgets, No-Repeat, Schleifenstopp, Faktenintegrität, Stop-Wunsch und Sicherheitsgrenzen bleiben deterministisch in Python.

Die vertikale HTML-/CSS-Prozesslinie bleibt verbindlich. Mermaid wird wegen unzuverlässiger Umbrüche langer deutscher Labels, Print- und Sicherheitsaufwand nicht wieder eingeführt.

## Implementierter Ist-Zustand

Die Laufzeit nutzt aktives Diagnose-RAG, deterministische Python-Guardrails, kontrolliertes Agent-Pattern-Retrieval, den direkt geladenen Katalog, LLM-Klassifikation von Problemfamilien und Gates mit deterministischem Fallback, den deterministischen Selector und einen finalen Structured-Output-Prompt. Der Selector-Kontext bleibt technisch von Nutzerfakten, Ableitungen und RAG-Evidenz getrennt.

## Behobene strukturelle Ursachen der defensiven Empfehlungen

- Kanaleignung und Prozess-/Datenreife wurden vermischt.
- `automation_pattern` war im Analyse-Retrieval erlaubt, aber nicht verpflichtend.
- Defensive Chunktypen konkurrierten im selben Top-k mit konkreteren Mustern.
- Der finale Prompt verlangte keinen systematischen Vorgangsanker-/Kanal-Gegencheck.
- Genau drei Opportunities konnten schwächere Empfehlungen erzwingen.
- `required_prerequisites` konnte Voraussetzungen künstlich aufblähen.
- Ein normalisierter Solution-Katalog fehlte.

Diese Ursachen waren fachlich und technisch belegt. Katalog, Gates, reservierte Retrieval-Typen, variabler Outputvertrag und Selector beheben sie strukturell; reale Kalibrierung bleibt erforderlich.

## Zwölf Problemfamilien

1. `PF-01` – Vorgangsbezogene Informationen sind über mehrere Kanäle verteilt.
2. `PF-02` – Eingehende Anfragen werden nicht zuverlässig erfasst und qualifiziert.
3. `PF-03` – Daten werden mehrfach übertragen oder abgeschrieben.
4. `PF-04` – Aufträge, Übergaben und offene Schritte haben keinen verlässlichen Status.
5. `PF-05` – Physischer Gegenstand, Auftrag und Ablageort sind nicht stabil verbunden.
6. `PF-06` – Termine und Kapazitäten werden ohne reale Constraints koordiniert.
7. `PF-07` – Änderungen, Zusatzarbeit und Freigaben blockieren oder entkoppeln den Prozess.
8. `PF-08` – Außendienstnachweise erreichen Rechnung und Büro nicht vollständig.
9. `PF-09` – Zahlung, Beleg und offener Vorgang werden nicht zuverlässig abgeglichen.
10. `PF-10` – Material, Bestand, Charge oder Produktionsfortschritt sind nicht rückverfolgbar.
11. `PF-11` – Inhaber oder Einzelperson ist der einzige Wissens- und Koordinationspunkt.
12. `PF-12` – Eingehende Dokumente und freie Texte werden nicht zu prüfbaren Datensätzen.

## Zehn Solution Patterns

1. `SP-01` – Gemeinsamer Anfrageeingang mit Missing-Info-Prüfung.
2. `SP-02` – Einfache Vorgangsakte mit Status und nächstem Schritt.
3. `SP-03` – Mobile Einsatzdokumentation aus Sprache, Fotos und Bon.
4. `SP-04` – Objekt-ID und echter Ablageort.
5. `SP-05` – Termin-Anfrage mit Kapazitätsprüfung statt blinder Sofortbuchung.
6. `SP-06` – Dokument-zu-Datensatz mit Unsicherheitsprüfung.
7. `SP-07` – Zusatzarbeit und Änderung mit dokumentierter Freigabe.
8. `SP-08` – Einfaches Material- und Produktionsboard.
9. `SP-09` – Geprüfte Rechnungsgrundlage und Zahlungsnachverfolgung.
10. `SP-10` – Übergabe- und Wissensnotiz im Vorgang.

## Getrennte Gates

| Gate | Prüffrage | Wirkung |
|---|---|---|
| Vorgangsanker | Kann der konkrete Vorgang eindeutig erkannt oder mit minimalem Aufwand verankert werden? | Bestimmt, ob Informationen verlässlich zusammengeführt werden können. |
| Kanaleignung | Ist die Erfassung im realen Arbeitsumfeld nutzbar, etwa mobil, offline oder direkt am Objekt? | Verhindert ungeeignete Bedien- und Erfassungswege. |
| Prozess-/Datenreife | Sind Quelle, Zielfelder, Statusereignisse und erforderliche Daten ausreichend klar? | Begrenzt KI-Aufgaben auf prüfbare Eingaben und Ergebnisse. |
| Risiko | Welche Fehler hätten relevante finanzielle, rechtliche, qualitative oder betriebliche Folgen? | Erzwingt Ausschlüsse, Unsicherheitsmarkierung oder strengere Prüfung. |
| Regelstabilität | Sind die Entscheidungskriterien wiederholbar oder stark fallabhängig? | Trennt Vorschlag/Assistenz von belastbarer regelbasierter Automatisierung. |
| Menschliche Freigabe | Wer muss Ergebnis, Zusage, Änderung oder Folgeaktion bestätigen? | Verhindert autonome kritische Entscheidungen. |

Kanaleignung, Prozess-/Datenreife und Automationsreife werden getrennt bewertet. Ein ungeeigneter Kanal darf nicht pauschal als unreifer Gesamtprozess interpretiert werden.

## Rolle des Diagnose-RAG

Das Diagnose-RAG liefert Vergleichswissen zu Symptomen, Ursachen, Bedingungen, Risiken und möglichen Diagnosefragen. Es darf keine Nutzerfakten erfinden und entscheidet nicht allein über das Solution Pattern. Retrieval-Ergebnisse bleiben Evidenz, die gegen bestätigte Nutzerangaben und deterministische Gates geprüft wird.

## Rolle des strukturierten Solution-Katalogs

Der Katalog hält für jedes Pattern stabile ID, passende Problemfamilien, Signale, Voraussetzungen, Ausschlüsse, Risiken, Nutzerhandlung, KI-Aufgabe, sichtbares Ergebnis und Human Check. `app/recommendation_service.py` prüft die Einträge gegen Gates und Matrix. Der Speicherpfad ist `knowledge/structured/recommendation_catalog.json`.

## Warum zunächst kein neuer FAISS-Solution-Index empfohlen wird

Der Katalog umfasst zunächst nur zehn strukturierte Patterns. Deterministische Filterung und Ranking über explizite Felder sind dafür nachvollziehbarer und leichter zu testen als ein weiterer semantischer Top-k. Ein zusätzlicher Index würde die belegte Konkurrenz unspezifischer Treffer nicht automatisch lösen und erhöht Build-, Deployment- und Evaluationsaufwand. Eine spätere semantische Erweiterung bleibt möglich, benötigt aber einen nachgewiesenen Qualitätsgewinn und eine eigene Entscheidung.

## Integrationspunkte

- `app/llm_classification.py`: LLM-Klassifikator für Problemfamilien und Gates mit Keyword-Fallback.
- `app/routes.py`: Orchestrierung von Klassifikation, Gates, Retrieval, Selector, Agent-Patterns, Logging und Persistenz.
- `app/rag_service.py`: reservierte Analyse-Chunktypen und separater Agent-Pattern-Abruf.
- `app/openai_service.py`: getrennte Recommendation-Payload und kompakter Outputprompt.
- `app/schemas.py`: neuer Kundenvertrag und Legacy-Abbildung.
- `app/templates/` und `app/static/styles.css`: Hauptseite und variabler Druckbericht.

## Risiken

- Zu grobe Gates können geeignete KI-Unterstützung weiterhin verdrängen.
- Zu lockere Gates können ungesicherte Automatisierungs- oder Auffindbarkeitsbehauptungen erzeugen.
- Ein zu großer Pflichtkatalog kann Kundenausgaben und Voraussetzungen wieder aufblähen.
- Doppelte Entscheidungshoheit in Python, Retrieval und Prompt kann widersprüchliche Rankings erzeugen.
- Änderungen am Opportunity-Vertrag können Persistenz, Templates und bestehende Tests berühren.

## Verifizierte technische Entscheidungen

- Keine neue Tabelle oder Migration; neuer Output liegt im vorhandenen JSONB.
- Klassifikation und Gates laufen vor `select_recommendation()` in der finalen Analyseorchestrierung; primär per LLM, bei API-Fehlern deterministisch.
- Alte Kernoutputs werden nur beim Lesen beziehungsweise bei Legacy-Fixtures auf den neuen Vertrag abgebildet.
- Agent-Patterns unterstützen den Rückfragekontext und beeinflussen die Solution-Auswahl nicht.
- Echtes Function Calling ist nicht integriert und bleibt ein getrennter nächster Schritt.
