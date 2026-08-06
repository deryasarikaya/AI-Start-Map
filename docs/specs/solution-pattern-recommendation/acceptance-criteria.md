# Acceptance Criteria – Solution-Pattern-Recommendation

**Status:** Active – acceptance criteria passed in automated suite; limited Chrome visual check completed
**Datum:** 2026-08-06
**Fachlicher Status:** Verbindlich entschieden; technische Nachweise werden getrennt dokumentiert.

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

### Blumenladen

- Eine freie Bestellung führt primär zur strukturierten Bestellaufnahme.
- Die Vorschau ist eine Bestellkarte; tatsächlich fehlende Angaben bleiben sichtbar.
- Ein Antwortentwurf ist zulässig; bei ungeklärter Kapazität gibt es keine automatische verbindliche Annahme.

## Struktur jeder Recommendation

Jede sichtbare Empfehlung enthält:

1. Nutzerhandlung,
2. KI-Aufgabe,
3. normale Software- oder Regelaufgabe,
4. sichtbares Ergebnis,
5. Human Check,
6. offene Angaben,
7. kleinste nutzbare Version,
8. Nicht-Automationen und Autonomiestufe.

Zusätzlich enthält sie eine Ergebnisvorschau, ein bis drei Nutzenpunkte, null bis drei Voraussetzungen, zwei bis vier Umsetzungsschritte und optional null bis zwei nachrangige Möglichkeiten. Wochentest und genau drei Opportunities sind nicht Bestandteil der Abnahme.

## Sprache, Länge und Darstellung

- Sichtbare Texte verwenden direkte Du-Ansprache; distanzierte Ersatzrollen sind unzulässig, wenn der Kunde gemeint ist.
- Primärtitel bleibt ungefähr innerhalb 12–14 Wörtern; Begründung maximal zwei kurze Sätze.
- Vorher umfasst maximal drei, der neue Ablauf drei bis sechs Schritte; Nutzen maximal drei, Voraussetzungen maximal drei, sekundäre Möglichkeiten maximal zwei.
- Genau eine Hauptlösung dominiert; die Vorschau ist zentral; weitere Möglichkeiten bleiben eingeklappt.
- Der Druckbericht umfasst zwei Seiten plus eine optionale dritte Seite.
- Die vertikale HTML-/CSS-Prozesslinie wird verwendet; Mermaid bleibt ausgeschlossen.

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
- Output-Strukturen werden deterministisch nach Solution Pattern gewählt; Beispielwerte werden nie zu Kundenwerten.
- Inference Patterns bleiben unbestätigte Hypothesen. Solution-Retrieval darf nur innerhalb des bereits gewählten Patterns Varianten ranken.

## Technischer Nachweis vor Abnahme

- Für jedes Kriterium existiert ein passender automatisierter oder fachlich reproduzierbarer Test.
- Die vier Referenzfälle prüfen positive Auswahl und relevante Freigabe- beziehungsweise Ausschlussgrenzen.
- Externe OpenAI- und Embedding-Aufrufe sind in automatisierten Tests gemockt.
- Die Änderung ist in `docs/CHANGELOG.md`, `docs/PROJECT_STATE.md`, `docs/KNOWN_ISSUES.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/ROADMAP.md` und `docs/INDEX.md` ihrem tatsächlichen Status entsprechend dokumentiert.
