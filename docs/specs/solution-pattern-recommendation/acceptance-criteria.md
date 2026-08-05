# Acceptance Criteria – Solution-Pattern-Recommendation

**Status:** Draft
**Datum:** 2026-08-05
**Fachlicher Status:** Die folgenden Kriterien sind fachlich bestätigt. Sie sind noch nicht als technisch implementiert, integriert oder getestet anzusehen, sofern kein späterer Nachweis dies ausdrücklich dokumentiert.

## Referenzfälle

### Hausmeister

- Mobile Einsatzdokumentation ist Rang 1, sofern ein leichter Einsatzanker vorhanden ist oder Teil desselben Einstiegs ist.
- Album oder Umschlag ist nicht die Kernlösung.
- Die Recommendation verbindet Einsatz, Sprache/Fotos/Bon und prüfbare Rechnungsgrundlage, ohne unnötige manuelle Vorablage zu erzwingen.

### Schuhmacher

- Ohne Objekt-ID und realen Ort gibt es keine KI-Behauptung zur Auffindbarkeit.
- KI darf Sonderwünsche oder Klärfälle erst auf Basis einer überprüfbaren Objekt-/Ortszuordnung unterstützen.

### Massagesalon

- Bei unsicherer Personalverfügbarkeit erfolgt keine automatische Terminbestätigung.
- Das System darf fehlende Angaben prüfen und Alternativen vorschlagen; die verbindliche Zusage bleibt bei der verantwortlichen Person.

## Struktur jeder Recommendation

Jede sichtbare Empfehlung enthält:

1. Nutzerhandlung,
2. KI-Aufgabe,
3. sichtbares Ergebnis,
4. Human Check.

## Grounding und Knowledge-Sicherheit

- RAG-Evidenz wird nie als Nutzerfakt ausgegeben.
- Evaluationen bleiben außerhalb des Produktwissens und aller produktiven Indizes.
- Interne IDs, Metadaten, Quellenmarker, Prompts und Modellnamen bleiben unsichtbar.
- Fehlende Angaben, Unsicherheit und Widersprüche werden nicht erfunden oder verdeckt.

## Auswahl- und Guardrail-Verhalten

- Defensive Guardrails dürfen geeignete KI-Unterstützung begrenzen, aber nicht unbegründet verdrängen.
- Kanaleignung, Prozess-/Datenreife und Automationsreife werden getrennt geprüft.
- Eine Voraussetzung wird nur verlangt, wenn sie die Eignung, Sicherheit oder menschliche Prüfung tatsächlich verändert.
- Rückfragen werden nur gestellt, wenn ihre Antwort Problemfamilie, Reifegrad, Lösung oder Freigabe verändert.
- Kein semantischer Retrievaltreffer kann allein ein Sicherheits- oder Freigabegate aufheben.

## Technischer Nachweis vor Abnahme

- Für jedes Kriterium existiert ein passender automatisierter oder fachlich reproduzierbarer Test.
- Die drei Referenzfälle prüfen sowohl positive Auswahl als auch relevante Ausschlüsse.
- Externe OpenAI- und Embedding-Aufrufe sind in automatisierten Tests gemockt.
- Die Änderung ist in `docs/CHANGELOG.md`, `docs/PROJECT_STATE.md`, `docs/KNOWN_ISSUES.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/ROADMAP.md` und `docs/INDEX.md` ihrem tatsächlichen Status entsprechend dokumentiert.
