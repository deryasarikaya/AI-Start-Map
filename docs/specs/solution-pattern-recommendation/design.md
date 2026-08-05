# Design – Solution-Pattern-Recommendation

**Status:** Active – decided
**Datum:** 2026-08-06
**Geltung:** Verbindliches Design; Implementierungs-, Integrations- und Teststatus werden getrennt geführt.

## Verbindlicher Zielpfad

```text
bestätigte Nutzerfakten
→ deterministische Problemfamilienklassifikation
→ sechs getrennte Gates
→ validierter Solution-Katalog
→ primäre Empfehlung plus 0–2 sekundäre Kandidaten
→ kompakter Structured Output
→ Pydantic-, Grounding- und Sprachvalidierung
→ JSONB-Persistenz und kurze HTML-/Druckdarstellung
```

Problemfamilien und Patterns liegen als versionierte JSON-Dateien außerhalb aller Evaluationspfade. Der Loader validiert Anzahl, IDs, Referenzen und Kernfelder. Der Selector liefert Auswahl, Ausschlussgründe, Voraussetzungen und Freigabegrenzen. Der neue Kernoutput liegt in bestehendem JSONB; die View-Schicht liest neue und alte Analysen. Neue Seiten zeigen keinen Wochentest.

Das Analyse-Retrieval balanciert Diagnose, konkretes `automation_pattern`, Voraussetzung und Guardrail. Agentenpatterns unterstützen nur die Wahl einer entscheidungsrelevanten Lücke oder Aktion. Budgets, No-Repeat, Schleifenstopp, Faktenintegrität, Stop-Wunsch und Sicherheitsgrenzen bleiben deterministisch in Python.

Die vertikale HTML-/CSS-Prozesslinie bleibt verbindlich. Mermaid wird wegen unzuverlässiger Umbrüche langer deutscher Labels, Print- und Sicherheitsaufwand nicht wieder eingeführt.

## Aktueller Ist-Zustand

Die Laufzeit nutzt ein aktives Diagnose-RAG, überwiegend deterministische Python-Agentenregeln und einen finalen Structured-Output-Prompt. Der Agent-Pattern-Index ist gebaut, aber nicht eingebunden. Ein normalisierter Solution-Katalog und explizite Solution-Gates existieren im produktiven Laufzeitpfad noch nicht. Der Recommendation Layer bleibt technisch unverändert.

## Belegte Ursachen der defensiven Empfehlungen

- Kanaleignung und Prozess-/Datenreife werden vermischt.
- `automation_pattern` ist im Analyse-Retrieval erlaubt, aber nicht verpflichtend.
- Defensive Chunktypen konkurrieren im selben Top-k mit konkreteren Mustern.
- Der finale Prompt verlangt keinen systematischen Vorgangsanker-/Kanal-Gegencheck.
- Genau drei Opportunities können schwächere Empfehlungen erzwingen.
- `required_prerequisites` kann Voraussetzungen künstlich aufblähen.
- Ein normalisierter Solution-Katalog fehlt.

Diese Ursachen sind fachlich und anhand des vorhandenen Retrieval-/Output-Vertrags belegt. Sie gelten nicht als behoben.

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

Der Katalog hält für jedes Pattern stabile ID, passende Problemfamilien, erforderliche Signale, Voraussetzungen, Ausschlüsse, Risiken, Reifeanforderungen, Nutzerhandlung, KI-Aufgabe, sichtbares Ergebnis und Human Check. Die Auswahl prüft Katalogeinträge gegen den bestätigten State und die Gates. Das konkrete Schema und der Speicherpfad werden erst im technischen Review festgelegt.

## Warum zunächst kein neuer FAISS-Solution-Index empfohlen wird

Der Katalog umfasst zunächst nur zehn strukturierte Patterns. Deterministische Filterung und Ranking über explizite Felder sind dafür nachvollziehbarer und leichter zu testen als ein weiterer semantischer Top-k. Ein zusätzlicher Index würde die belegte Konkurrenz unspezifischer Treffer nicht automatisch lösen und erhöht Build-, Deployment- und Evaluationsaufwand. Eine spätere semantische Erweiterung bleibt möglich, benötigt aber einen nachgewiesenen Qualitätsgewinn und eine eigene Entscheidung.

## Mögliche Integrationspunkte

Die Fachgrundlage nennt `app/rag_service.py`, `app/openai_service.py`, `app/schemas.py`, `app/agent_service.py` und die Qualitäts-/Produktfinalisierungstests als mögliche Prüfstellen. Exakte Aufrufkette, Schemaänderungen und Dateipfade sind noch zu verifizieren; diese Spec beschließt keine Codeänderung.

## Risiken

- Zu grobe Gates können geeignete KI-Unterstützung weiterhin verdrängen.
- Zu lockere Gates können ungesicherte Automatisierungs- oder Auffindbarkeitsbehauptungen erzeugen.
- Ein zu großer Pflichtkatalog kann Kundenausgaben und Voraussetzungen wieder aufblähen.
- Doppelte Entscheidungshoheit in Python, Retrieval und Prompt kann widersprüchliche Rankings erzeugen.
- Änderungen am Opportunity-Vertrag können Persistenz, Templates und bestehende Tests berühren.

## Noch zu verifizierende technische Details

- Bestehende Felder und Validatoren in `app/schemas.py`, die den Katalogvertrag tragen können.
- Exakter Zeitpunkt und Besitzer der Problemfamilienklassifikation.
- Persistenzbedarf; nach heutigem Stand ist keine neue Tabelle beschlossen.
- Deterministisches Ranking und Tie-Breaking zwischen mehreren anwendbaren Patterns.
- Rückwärtskompatible Abbildung alter Drei-Opportunity- und Wochentest-Daten.
- Test-Fixtures, Mocking und erwartete Laufzeitpfade für die drei Referenzfälle.
- Ob spätere Agent-Pattern-Retrieval-Aktivierung die Solution-Auswahl überhaupt beeinflussen soll.
