# Pre-Results UI Foundation

## Zweck und Geltungsbereich

Diese Foundation verbindet die öffentliche Strecke von der Landingpage über
die Betriebsbeschreibung, die beiden Analysezustände und die
Verständnisbestätigung. Sie verändert weder den Analysevertrag noch den
Vier-Aufruf-Flow, das RAG, den Lösungskatalog oder die Ergebnisdaten.

Die Ergebnisdarstellung ist in diesem Stand bewusst nicht neu gebaut. Eine
spätere Results V1 soll dieselben semantischen Tokens und Interaktionsmuster
verwenden, damit vor und nach der Analyse kein visueller Produktwechsel
entsteht.

## Produktversprechen entlang der Strecke

Die Strecke erzählt durchgängig denselben Dreiklang:

1. Der Betrieb beschreibt einen echten Ablauf in eigenen Worten.
2. AI Start Map bestätigt zuerst Engpass und Ist-Ablauf.
3. Danach entsteht eine begründete Auswertung mit sinnvollem Startpunkt und
   größerem Zielbild.

Die Landingpage verkauft deshalb keine allgemeine Liste von KI-Ideen. Sie
zeigt den erwartbaren Entscheidungsvorteil. Die Interviewseite verlangt keine
Vorbereitung oder Lösungssprache. Die Verstandenseite bleibt eine
Diagnosebestätigung und spielt noch keine Ergebnisdarstellung vor.

## Semantische Design-Tokens

Die Tokens stehen zentral in `app/static/styles.css` unter `:root`.

| Token | Zweck |
|---|---|
| `--page-bg`, `--page-bg-gradient` | gemeinsamer Seitenhintergrund |
| `--surface-elevated` | neutrale Kartenfläche |
| `--surface-accent` | zurückhaltende Akzentfläche |
| `--text-muted`, `--text-accent` | sekundärer Text und Hervorhebungen |
| `--border-subtle` | ruhige Trennlinien und Kartenränder |
| `--radius-card` | Radius für größere Flächen |
| `--radius-control` | Radius für Eingaben und Buttons |
| `--radius-pill` | Chips und kompakte Metadaten |
| `--shadow-card`, `--shadow-elevated` | normale und hervorgehobene Tiefe |
| `--content-width`, `--content-width-narrow` | breite und fokussierte Lesespalte |
| `--space-section`, `--space-card` | vertikaler Rhythmus und Karteninnenraum |
| `--motion-fast`, `--motion-standard`, `--motion-ease` | konsistente Übergänge |

Die semantischen Tokens verweisen auf die bestehende warme Creme-/Teal-Palette.
Sie ersetzen die Herkunftstokens nicht, sondern schaffen eine stabile
Komponentenschnittstelle für weitere Seiten.

## Gemeinsame Muster

### Karten

- `.card`: gemeinsame Fläche, Rand und Radius
- `.card--normal`: ruhige Standardtiefe
- `.card--elevated`: primäre Inhalts- oder Entscheidungsfläche
- `.card--accent`: Akzentfläche für eine Entscheidung oder Erklärung
- `.card--interactive`: nur für tatsächlich interaktive Karten

### Controls

- `.primary-button`: genau eine primäre Handlung pro Entscheidungskontext
- `.secondary-button`: Alternative ohne Konkurrenz zum Hauptweg
- Textlink bzw. `<summary>`: seltene oder korrigierende Nebenhandlung

Alle Controls behalten sichtbare Fokuszustände. Bewegungen werden über
`prefers-reduced-motion` abgeschaltet.

### Journey-Kontext

`.journey-context` zeigt die drei verständlichen Zustände ohne Prozentwerte
oder erfundene Zeitangaben:

`Betrieb beschreiben → Verständnis bestätigen → Auswertung erhalten`

Auf der Processing-Seite darf nur die bereits technisch belegte Phase als
aktiv markiert werden. Die aktive Phase erhält zusätzlich
`aria-current="step"`.

## Seitenspezifische Verantwortung

### Landingpage

- benennt Zielgruppe und Nutzen vor dem ersten CTA;
- zeigt Engpass, Startpunkt und Zielbild als kompakten Ergebnisvorgeschmack;
- erklärt, dass Aussagen begründet und menschliche Entscheidungen sichtbar
  bleiben;
- zeigt typische Alltagssituationen statt Branchen- oder Toollisten;
- sagt korrekt, dass das Ergebnis zuerst kommt und ein Gespräch optional ist.

### Betriebsbeschreibung

- eine echte Alltagserzählung reicht;
- Sprache und Text bleiben gleichwertig;
- der Leitfaden ist Orientierung, keine Pflicht-Checkliste;
- nach dem Absenden wird zuerst das Systemverständnis gezeigt.

### Processing

- zeigt echte, vom Status-Endpunkt gelieferte Phasen;
- enthält keine Prozentzahl, künstliche Dauer oder Fake-Fortschrittsanimation;
- erklärt knapp, dass Engpass, Startpunkt und Zielbild zusammengeführt werden.

### Verständnisbestätigung

- zeigt Engpass, Eckdaten, einen Originalbeleg und den heutigen Ablauf;
- sagt ausdrücklich, dass noch keine Empfehlung angezeigt wird;
- stellt nur eine entscheidungsrelevante Rückfrage und erklärt deren Grund;
- macht Zustimmung zum Hauptweg und Korrektur zur erreichbaren Ausnahme;
- bleibt mit nativen HTML-Elementen auch ohne JavaScript bedienbar.

## Mobile und Barrierefreiheit

- Einspaltige Darstellung unterhalb der definierten Breakpoints.
- Primäre Aktionen werden auf kleinen Viewports vollbreit.
- Die Ergebnisvorschau bleibt sichtbar und wird nicht als „Desktop-Deko“
  entfernt.
- Fokuszustände, semantische Überschriften, beschriftete Navigationen,
  `aria-live`-Status und `aria-current` bleiben erhalten.
- Animationen sind dekorativ und werden bei reduzierter Bewegung deaktiviert.

## Offene Trust-/Privacy-Frage

Die UI behauptet bewusst nicht, wie lange Eingaben gespeichert werden, wer sie
einsehen kann oder ob sie für Modelltraining verwendet werden. Diese Aussagen
müssen vor einer Veröffentlichung fachlich und rechtlich entschieden und dann
mit der realen Datenverarbeitung abgeglichen werden. Bis dahin darf keine
unbelegte Datenschutz-Zusage in Landingpage oder Interview ergänzt werden.

## Übergabe an Results V1

Results V1 sollte `--page-bg`, die Surface-, Text-, Border-, Radius-, Shadow-,
Width-, Spacing- und Motion-Tokens direkt übernehmen. Für normale Inhalte,
wichtige Zielbildflächen und Handlungen stehen die Karten- und Buttonmuster
bereits bereit.

Nicht übernehmen sollte Results V1 parallel gepflegte lokale Farbwerte oder
einen zweiten Satz Radien und Schatten unter `.ergebnis`. Die fachliche
Informationsarchitektur der Results bleibt eine eigene Aufgabe; diese
Foundation legt nur die visuelle und interaktive Sprache fest.

## Status

Implementiert und offline getestet auf `feature/pre-results-ui-foundation`.
Der Branch bleibt getrennt von `feature/final-stabilization` und wird dort
nicht automatisch zusammengeführt.
