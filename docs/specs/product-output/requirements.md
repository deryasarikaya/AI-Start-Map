# AI Start Map – Product Output Spec

**Status:** Active – implemented, integrated and tested
**Letzte Prüfung:** 2026-08-07
**Verwandt mit:** `docs/specs/solution-pattern-recommendation/`

## Ziel

Das Kundenergebnis beantwortet in unter zwei Minuten: was heute schiefläuft, was der Kunde künftig tut, was die KI tut, welches konkrete Ergebnis entsteht, was der Kunde prüft und womit er klein beginnt. A0 kann ausdrücklich bedeuten, dass keine KI nötig ist. Es ist kein langer Diagnosebericht.

## Verbindliche Produktregeln

- Die Hauptseite zeigt genau eine dominante primäre Empfehlung.
- `weekly_test`, `weekly_test_success` und „Das kannst du diese Woche testen“ gehören nicht zum neuen Vertrag. Der Kunde erhält keine Hausaufgabe.
- Stattdessen zeigt `implementation_path` einen konkreten Umsetzungsweg.
- Sekundäre Möglichkeiten sind optional: null bis maximal zwei, nicht dominant und nie Füllvorschläge.
- Alle sichtbaren Texte sprechen den Kunden mit „du“, „dir“, „dein“ oder „deine“ an. Distanzierte Ersatzrollen sind unzulässig, sofern keine andere reale Rolle gemeint ist.
- Nutzen umfasst ein bis drei Punkte; Voraussetzungen null bis drei; Umsetzung zwei bis vier Schritte.
- Die Vorschau verwendet echte belegte Nutzerangaben mit Vorrang. Fehlende Werte erhalten realistische deutsche Beispielwerte ausschließlich im klar gekennzeichneten Vorschaublock; diese Werte sind keine Nutzerfakten.
- Der fertige Kundenpayload wird gegen die verbindliche Liste interner und technischer Begriffe geprüft. Ein betroffenes Feld erhält vorhandenen Klartext oder entfällt.
- Offene Angaben werden semantisch entdoppelt, auf drei echte Fragen begrenzt und ausschließlich im Bericht gezeigt.
- Dieselbe Aussage wird nicht in mehreren Karten wiederholt.

## Neuer verbindlicher Kernoutput

| Feld | Bedeutung | Grenze |
|---|---|---|
| `primary_recommendation` | eine klare Hauptlösung | ungefähr 12–14 Wörter |
| `promise` | kurzer Satz mit greifbarem Ergebnis | ein Satz |
| `short_reason` | knappe Begründung | maximal zwei kurze Sätze |
| `before_process` | bestätigter Ist-Ablauf | maximal drei Schritte |
| `future_process` | ausdrücklich zukünftiger Ablauf | drei bis sechs Schritte |
| `sample_output` | typisierte, klar gekennzeichnete Vorschau mit deutschen Labels, realistischen Beispielwerten und optional echten Nutzerwerten | nur im Vorschaublock sichtbar |
| `user_action` | konkrete Eingabe/Handlung | ein kurzer Du-Satz |
| `ai_task` | Aufgabe der KI | ein kurzer Satz |
| `software_rule` | Aufgabe normaler Software oder fester Regeln | ein kurzer Satz |
| `visible_result` | greifbares Arbeitsergebnis | ein kurzer Satz |
| `human_check` | echte menschliche Prüfung/Entscheidung | ein kurzer Du-Satz |
| `customer_benefits` | konkrete Vorteile | ein bis drei |
| `required_prerequisites` | echte Voraussetzungen | null bis drei |
| `implementation_path` | einfachster Umsetzungsweg | zwei bis vier Schritte |
| `later_stage` | genau ein realistischer Ausbau | optional |
| `open_details` | nicht bestätigte Angaben | intern null bis sechs; kundenseitig höchstens drei echte Fragen nur im Bericht |
| `smallest_usable_version` | kleinster fachlich nutzbarer Einstieg | ein kurzer Abschnitt |
| `not_automated` | ausdrücklich menschlich bleibende Entscheidungen | null bis fünf |
| `autonomy_level` | deterministisch vorausgewählte Stufe | A0 bis A2 im aktuellen Selector |
| `secondary_opportunities` | nachrangige Titel plus ein Satz | null bis zwei |
| `error_boundaries` | echte Fehlergrenzen für die ausführliche PDF | null bis drei |

## Hauptseite und Details

Die Hauptseite verwendet verbindlich genau sechs sichtbare Blöcke: Engpass, empfohlene Lösung, zukünftiger Ablauf, Beispielausgabe, menschliche Kontrolle und kleinster Einstieg. Nutzer-, KI- und Menschenhandlung stehen als normale Sätze im Zielablauf; die rohe Rollentabelle entfällt. Voraussetzungen, offene Fragen und Ausbau stehen nur im Bericht. Weitere Möglichkeiten und der bereits bestätigte Ist-Ablauf bleiben geschlossen. Desktop-H1 liegt bei höchstens 42 Pixeln, Mobile-H1 bei höchstens 34 Pixeln; Fließtext bleibt auf ungefähr 60–75 Zeichen begrenzt.

## Grounding und Sicherheit

- Nur Nutzerangaben und bestätigte Extraktionen sind Fakten über den Betrieb.
- RAG-Evidenz, interne IDs, Quellen, Prompts, Modellnamen und fremde Falldaten bleiben unsichtbar.
- Physische Identität und realer Ort werden nie erraten.
- Preis-, Vertrags-, Zahlungs-, Qualitäts-, Personal-, Sicherheits-, Termin- und Herausgabeentscheidungen bleiben bei einem Menschen, wenn sie extern wirksam oder risikoreich sind.
- Es gibt keine erfundenen Tools, Integrationen, Betriebsfakten, Zahlen oder Einsparungen. Die einzige Ausnahme sind anschauliche Werte im eindeutig gekennzeichneten Beispielblock.
- Feldnamen, Human Review und Nicht-Automationen werden deterministisch aus der freigegebenen Output-Struktur und dem Katalog nachgeführt. Der Beispielblock trägt genau einen gemeinsamen Veranschaulichungshinweis statt wiederholter Präfixe.

## Speicherung und Rückwärtskompatibilität

Der Vertrag `recommendation-v3` wird ohne Migration in `analyses.uncertainties.core_output` gespeichert. Die bestehenden fünf Tabellen bleiben erhalten. Neue Analysen dürfen eine bis drei Opportunity-Zeilen persistieren: Rang 1 ist die primäre Lösung, Rang 2–3 sind optionale sekundäre Möglichkeiten. Bestehende Analysen mit altem Kernoutput bleiben über eine rückwärtskompatible View-Abbildung lesbar. Vom Shim erzeugte Platzhalter werden protokolliert und in der Kundensicht unterdrückt; die neuen v3-Felder werden für Legacy-Daten nicht erfunden.

## Druckbericht

Die Browser-Druckansicht verwendet weiter `window.print()` und umfasst genau zwei physische Seiten. Seite 1 zeigt Diagnosehinweis, Engpass, Empfehlung, zukünftigen Ablauf und eindeutig gekennzeichnete Beispielausgabe. Seite 2 zeigt menschliche Kontrolle, menschlich bleibende Entscheidungen, höchstens drei Klartextvoraussetzungen, höchstens drei wichtige offene Fragen, kleinsten Einstieg, einen späteren Ausbau und Kontakt. Inhalt wird begrenzt statt auf eine dritte Seite umgebrochen; sichtbare Link-URLs, leere Seiten, abgeschnittene Inhalte und übergroße Karten sind unzulässig.
