# AI Start Map V2 — Umsetzungsstand

_Stand: 26.07.2026_

## Aktuell umgesetzt

- Freie Erzählung per Browser-Spracheingabe oder editierbarem Text.
- Automatische Verarbeitung nach dem Absenden, ohne zweite Trigger-Schaltfläche.
- Bis zu drei erkannte Prozessoptionen; die wahrscheinlich relevanteste steht zuerst.
- Kurze Bestätigung des heutigen Ablaufs mit höchstens fünf vertikalen Schritten.
- Korrektur erst nach „Etwas stimmt nicht“, per Sprache, Text oder einzelnen Schritten.
- Diagnostic Interview Agent mit `ASK`, `CLARIFY`, `RETRIEVE`, `ANALYZE` und `STOP`.
- Null Rückfragen sind möglich; üblich sind null bis zwei, komplex höchstens drei, technisch maximal vier.
- Deterministischer Schutz gegen Wiederholungen, Schleifen, erfundene Fakten und autonome Prozessausführung.
- Ergebnis in der Reihenfolge Problem → erster Schritt → konkrete KI-Hilfe → Wochen-Test → spätere Automatisierung.
- Konkrete KI-Darstellung mit Eingabe, KI-Aufgabe, Ergebnis und menschlicher Kontrolle.
- Aufklappbarer Startplan, optionale Details, Druck-/PDF-Bericht und freigegebener Mailto-Kontakt.
- Konsistenter Processing-Layer bei merklicher Modell-, RAG- und Agentenarbeit; echte Analyse-Statusabfrage vor dem Ergebnis.
- Signierte HttpOnly-Sitzungscookies und keine sichtbaren numerischen Session-IDs.
- Fünf bestehende Datenbanktabellen; keine neue Migration für diese Überarbeitung.

## Wissensstand

- Produktiver Diagnoseindex: 634 Chunks aus kuratiertem Bestand, Batch 02 und Batch 03.
- Separater Agent-Pattern-Index: 205 Batch-04-Patterns.
- 79 Evaluationen sind getrennt und nicht indexierbar.
- Research-Batches und produktive Indizes wurden in dieser Überarbeitung nicht verändert oder neu gebaut.

## Noch offen

- Frage-, Agenten- und Tool-Runden anhand echter AI-Start-Map-Interviews kalibrieren.
- Visuelle Abnahme in echtem Chrome sowie auf Android und iPhone/Safari abschließen.
- Browser-Druckdialog auf den vorgesehenen Zielsystemen prüfen; die normale Druckstruktur ist auf drei Seiten begrenzt.
- Vor einem öffentlichen Produktivbetrieb Datenschutz-, Betriebs- und Deployment-Konfiguration final abnehmen.

## Bewusste Nicht-Ziele

- Keine autonome Ausführung von Unternehmensprozessen.
- Keine automatischen Preis-, Vertrags-, Zahlungs-, Qualitäts- oder Freigabeentscheidungen.
- Kein CRM, Kontaktformular, Newsletter, Tracking, WhatsApp- oder Calendly-Anschluss.
- Keine React-/Next.js-Migration und keine neue kostenpflichtige API.
- Kein automatischer E-Mail-Anhang; die gespeicherte PDF wird vom Nutzer selbst angehängt.
