# AI Start Map – UI Redesign Notes

**Status:** Archived
**Historischer Zweck:** Dokumentation des UI-Redesigns vom 26.07.2026.
**Aktuelle Source of Truth:** keine.
**Abgedeckt durch:** `docs/flows/UX_FLOW.md`, `docs/ARCHITECTURE.md`, `docs/CHANGELOG.md` sowie den aktuellen Code in `app/templates/` und `app/static/`. Relevante Design-Tokens, Responsive-Regeln, HTML/CSS-Prozessdarstellung und Print-Grenzen wurden im aktiven UX-Flow festgehalten.

_Stand: 26.07.2026_

## Designrichtung

Das UI bleibt warm und menschlich, nutzt aber mehr Kontrast und visuelle Orientierung. Die zentralen Tokens liegen in `app/static/styles.css`:

- Ink `#183B32`
- Green `#2F6B57`
- Green Soft `#DCEBE4`
- Cream `#FFF9F1`
- Sun `#F3C75F`
- Coral `#E98B6D`
- Sky `#DDECF2`

Die Primäraktion ist dunkelgrün beziehungsweise im Hero grün. Gelb markiert Orientierung und Priorität, Coral das Kernproblem, Sky die konkrete KI-Unterstützung. Akzentfarben werden gezielt eingesetzt.

## Geänderte Seiten

- Landingpage: fünf Abschnitte, neuer Hero, Scan-Zeilen, drei Schritte, KI-Abgrenzung, Schluss-CTA.
- Erzählen: große Mikrofonaktion, editierbares Transkript, klarer Text-Fallback.
- Prozesswahl: höchstens drei knappe Karten, erste Empfehlung markiert, Grenzen eingeklappt.
- Bestätigung: höchstens fünf vertikale Schritte; Korrektur erst nach ausdrücklicher Auswahl.
- Rückfrage: eine Frage, eine Eingabe, „Weiß ich nicht“ und eine dominante Übernahmeaktion.
- Processing: gemeinsame Overlay-Komponente und echte Analyse-Statusseite.
- Ergebnis: fünf Kernpunkte zuerst, Startplan und Details geschlossen.
- Bericht: drei feste, lesbare Seiten ohne Mermaid.

## Responsive Regeln

- Mobile startet einspaltig.
- Touch-Ziele sind mindestens ungefähr 48–56 Pixel hoch.
- `overflow-x: hidden` verhindert horizontalen Seitenlauf; Text in Prozessschritten darf umbrechen.
- Prozessdarstellungen verlaufen vertikal und enthalten höchstens fünf Hauptschritte.
- Ergebnis- und KI-Karten wechseln erst auf breiteren Viewports in mehrere Spalten.
- Der Hero ist die stärkste Überschrift; seine Höhe lässt den Beginn des nächsten Abschnitts sichtbar werden.

## Diagrammentscheidung

Mermaid wurde aus Bestätigung, Ergebnis und PDF entfernt. Die sichtbare Darstellung ist eine kontrollierte HTML-/CSS-Prozessleiste aus validierten `as_is_steps`. Dadurch bleiben lange deutsche Labels auf Mobile und im Druck vollständig lesbar. Die vorhandene Mermaid-Hilfsdatei wird nicht mehr von diesen Seiten geladen und kann für ältere interne Nutzung bestehen bleiben.

## Druck

Die normale Druckansicht besteht aus drei `.report-page`-Abschnitten. Print-CSS setzt jeden Abschnitt auf eine A4-Seite, verhindert eine zusätzliche leere Abschlussseite und blendet Navigation sowie Druckleiste aus. Eine endgültige Freigabe des Browser-Druckdialogs auf allen Zielsystemen bleibt Teil der manuellen Abnahme.
