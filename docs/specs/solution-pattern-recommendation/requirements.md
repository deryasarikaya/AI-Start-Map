# Requirements – Solution-Pattern-Recommendation

**Status:** Draft
**Datum:** 2026-08-05
**Fachlicher Status:** Aus der aktiven Fachgrundlage abgeleitet; noch nicht technisch implementiert oder integriert.
**Source of Truth:** Diese Datei für den geplanten Feature-Scope; fachliche Begriffe und Kataloginhalte stammen aus `docs/product/AI_Start_Map_Fachgrundlage_Painpoints_Solutions_2026-08-05.md`.

## Ziel

Der Recommendation Layer soll aus bestätigtem Prozessproblem, Ursache, Problemfamilie, Reife und notwendigen Freigaben den kleinsten realistischen KI-unterstützten nächsten Workflow auswählen. Defensive Guardrails sollen ungeeignete Automatisierung begrenzen, passende KI-Unterstützung aber nicht unbegründet durch manuelle Ablage ersetzen.

## Problem

Der aktuelle Laufzeitpfad erkennt Engpässe häufig plausibel, wählt aber nicht zuverlässig den besten konkreten Workflow. Diagnose-Retrieval und finale Modellauswahl vermischen heute teilweise Kanaleignung, Prozess-/Datenreife und Automationsreife. Es fehlt ein normalisierter, technisch integrierter Solution-Katalog.

## Nutzerfälle

- Ein Hausmeisterservice erhält eine mobile Einsatzdokumentation als ersten Vorschlag, wenn ein leichter Einsatzanker vorhanden ist oder im selben Einstieg geschaffen werden kann.
- Ein Schuhmacher erhält keine KI-Aussage zur Auffindbarkeit, solange Objekt-ID und realer Ablageort fehlen.
- Ein Massagesalon erhält bei unsicherer Personalverfügbarkeit keine automatische Terminbestätigung, sondern einen prüfbaren Vorschlag mit menschlicher Freigabe.
- Ein Betrieb mit ausreichender digitaler Reife erhält früh konkrete KI-Unterstützung, ohne pauschal auf eine vorgelagerte Ordnungsphase zurückgesetzt zu werden.

## Scope

- Zuordnung bestätigter Symptome und Ursachen zu zwölf Problemfamilien.
- Auswahl aus zehn fachlich definierten Solution Patterns.
- Getrennte Prüfung von Vorgangsanker, Kanaleignung, Prozess-/Datenreife, Risiko, Regelstabilität und menschlicher Freigabe.
- Strukturierter Applicability- und Exclusion-Vertrag für jedes Solution Pattern.
- Klare Trennung von Diagnose-RAG-Evidenz, Nutzerfakten und Solution-Auswahl.
- Recommendation-Ausgabe mit Nutzerhandlung, KI-Aufgabe, sichtbarem Ergebnis und Human Check.
- Gezielte Evaluation der drei bestätigten Referenzfälle.

## Nicht-Ziele

- Keine autonome Ausführung betrieblicher Prozesse.
- Keine automatischen Preis-, Vertrags-, Zahlungs-, Qualitäts- oder Freigabeentscheidungen.
- Kein neuer FAISS-Solution-Index im ersten Umsetzungsschritt.
- Keine Aufnahme von Evaluationen in Produktwissen.
- Kein ungeprüfter breiter Katalog beliebiger KI-Ideen.
- Kein echtes LLM-Function-Calling innerhalb dieses Features, sofern es nicht getrennt beschlossen wird.

## Fachliche Anforderungen

1. Symptom, Ursache und Problemfamilie müssen getrennt repräsentiert und bewertet werden.
2. Nicht jeder Betrieb beginnt bei Ordnung; notwendige Mindestordnung darf geeignete KI-Unterstützung nicht ersetzen.
3. Die Leitregel lautet: „So wenig Ordnung wie zwingend nötig, so früh konkrete KI-Unterstützung wie realistisch möglich, Automatisierung erst nach bestätigten Daten und klaren Freigaben.“
4. Solution-Auswahl muss über einen strukturierten Katalog und nachvollziehbare Gates erfolgen, nicht allein über ein zufälliges semantisches Top-k.
5. Diagnose-RAG liefert Problem- und Bedingungsevidenz, entscheidet aber nicht allein über die Lösung.
6. Voraussetzungen dürfen nur aufgenommen werden, wenn sie für Eignung, Sicherheit oder Prüfung erforderlich sind.
7. Rückfragen sind nur zulässig, wenn ihre Antwort Problemfamilie, Reifegrad, Lösung oder Freigabe verändert.
8. Die bisherige Vorgabe genau dreier Opportunities bleibt bis zum fachlichen Review bestehen und wird nicht durch diese Spec aufgehoben.

## Sicherheitsanforderungen

- RAG-Evidenz darf nie als Nutzerfakt ausgegeben werden.
- Interne IDs, Metadaten, Quellenmarker, Prompts und Modellnamen bleiben unsichtbar.
- Unsicherheit und Widersprüche bleiben technisch getrennt und sichtbar ehrlich.
- Ausschluss- und Freigabegates werden deterministisch durchgesetzt; semantisches Retrieval ist keine alleinige Sicherheitskontrolle.
- Empfehlungen mit relevanten Risiken enthalten eine explizite menschliche Prüfung.
- Evaluationen bleiben außerhalb aller produktiven Knowledge-Allow-Lists.

## Kundensprache

- Deutsch, kurz, konkret und ohne unnötige Fachbegriffe.
- Der erste Schritt muss als reale Nutzerhandlung verständlich sein.
- KI wird über Aufgabe und sichtbares Ergebnis beschrieben, nicht über Modell- oder Systembegriffe.
- Voraussetzungen werden nur genannt, wenn sie zwingend sind, und nicht zu einer langen defensiven Vorliste aufgebläht.

## Offene Fragen

- Bleibt genau drei Opportunities der verbindliche Outputvertrag oder wird eine kleinere variable Anzahl zugelassen?
- Bleibt ein Wochentest in jedem Fall verpflichtend oder wird er abhängig vom Solution Pattern?
- In welchem bestehenden strukturierten Dateiformat wird der Solution-Katalog gespeichert?
- Welche bestehenden Pydantic-Felder können wiederverwendet werden, ohne den aktuellen Outputvertrag stillschweigend zu verändern?
- An welchem Laufzeitpunkt werden Problemfamilie und Gates technisch berechnet?
- Welche Messgrößen entscheiden über die fachliche Freigabe nach den drei Referenzfällen?
