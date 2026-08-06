# AI Start Map – Product Output Spec

**Status:** Active – implemented, integrated and tested
**Letzte Prüfung:** 2026-08-06
**Verwandt mit:** `docs/specs/solution-pattern-recommendation/`

## Ziel

Das Kundenergebnis beantwortet in wenigen Sekunden: bester KI-Hebel, zukünftiger Ablauf, KI-Aufgabe, sichtbares Ergebnis, menschliche Kontrolle, Umsetzungsweg und optional spätere Möglichkeiten. Es ist kein langer Diagnosebericht.

## Verbindliche Produktregeln

- Die Hauptseite zeigt genau eine dominante primäre Empfehlung.
- `weekly_test`, `weekly_test_success` und „Das kannst du diese Woche testen“ gehören nicht zum neuen Vertrag. Der Kunde erhält keine Hausaufgabe.
- Stattdessen zeigt `implementation_path` einen konkreten Umsetzungsweg.
- Sekundäre Möglichkeiten sind optional: null bis maximal zwei, nicht dominant und nie Füllvorschläge.
- Alle sichtbaren Texte sprechen den Kunden mit „du“, „dir“, „dein“ oder „deine“ an. Distanzierte Ersatzrollen sind unzulässig, sofern keine andere reale Rolle gemeint ist.
- Nutzen umfasst ein bis drei Punkte; Voraussetzungen null bis drei; Umsetzung zwei bis vier Schritte.
- Die Vorschau verwendet nur bestätigte Nutzerfakten und neutrale, sichtbar offene Platzhalter.
- Dieselbe Aussage wird nicht in mehreren Karten wiederholt.

## Neuer verbindlicher Kernoutput

| Feld | Bedeutung | Grenze |
|---|---|---|
| `primary_recommendation` | eine klare Hauptlösung | ungefähr 12–14 Wörter |
| `promise` | kurzer Satz mit greifbarem Ergebnis | ein Satz |
| `short_reason` | knappe Begründung | maximal zwei kurze Sätze |
| `before_process` | bestätigter Ist-Ablauf | maximal drei Schritte |
| `future_process` | zukünftiger Ablauf | drei oder vier Schritte |
| `sample_output` | typisierte Vorschau mit Titel, Zeilen, offenen Punkten, optional Anhängen und Vorschauhinweis | nur geerdete Inhalte |
| `user_action` | konkrete Eingabe/Handlung | ein kurzer Du-Satz |
| `ai_task` | Aufgabe der KI | ein kurzer Satz |
| `visible_result` | greifbares Arbeitsergebnis | ein kurzer Satz |
| `human_check` | echte menschliche Prüfung/Entscheidung | ein kurzer Du-Satz |
| `customer_benefits` | konkrete Vorteile | ein bis drei |
| `required_prerequisites` | echte Voraussetzungen | null bis drei |
| `implementation_path` | einfachster Umsetzungsweg | zwei bis vier Schritte |
| `later_stage` | genau ein realistischer Ausbau | optional |
| `secondary_opportunities` | nachrangige Titel plus ein Satz | null bis zwei |
| `error_boundaries` | echte Fehlergrenzen für die ausführliche PDF | null bis drei |

## Hauptseite und Details

Die erste Ebene zeigt primäre Empfehlung, Promise, kurze Begründung, Heute/Mit KI, den Viererschritt „Du gibst ein – KI verarbeitet – Du erhältst – Du prüfst“, die Ergebnisvorschau, höchstens drei Nutzenpunkte, nur vorhandene Voraussetzungen und eine Hauptaktion „So setzt du das um“. Weitere Möglichkeiten stehen eingeklappt.

## Grounding und Sicherheit

- Nur Nutzerangaben und bestätigte Extraktionen sind Fakten über den Betrieb.
- RAG-Evidenz, interne IDs, Quellen, Prompts, Modellnamen und fremde Falldaten bleiben unsichtbar.
- Physische Identität und realer Ort werden nie erraten.
- Preis-, Vertrags-, Zahlungs-, Qualitäts-, Personal-, Sicherheits-, Termin- und Herausgabeentscheidungen bleiben bei einem Menschen, wenn sie extern wirksam oder risikoreich sind.
- Fehlende Angaben bleiben als „noch offen“ sichtbar; es gibt keine erfundenen Tools, Integrationen, Zahlen oder Einsparungen.

## Speicherung und Rückwärtskompatibilität

Der neue Vertrag wird ohne Migration in `analyses.uncertainties.core_output` gespeichert. Die bestehenden fünf Tabellen bleiben erhalten. Neue Analysen dürfen eine bis drei Opportunity-Zeilen persistieren: Rang 1 ist die primäre Lösung, Rang 2–3 sind optionale sekundäre Möglichkeiten. Bestehende Analysen mit altem Kernoutput, Wochentest oder drei Opportunities bleiben über eine rückwärtskompatible View-Abbildung lesbar; alte Felder werden nicht mehr auf neuen Seiten gerendert.

## Druckbericht

Die Browser-Druckansicht verwendet weiter `window.print()`. Seite 1 zeigt beste Lösung, Vorher/Nachher, KI-Ablauf, Vorschau und Human Check. Seite 2 zeigt Umsetzung, Voraussetzungen, offene Punkte, Fehlergrenzen und menschliche Entscheidungen. Eine dritte Seite erscheint nur bei fachlich vorhandenen sekundären Möglichkeiten; ein alleiniger späterer Ausbau bleibt auf Seite 2.
