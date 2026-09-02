# Pre-Results UI Foundation

## Zweck und Geltungsbereich

Diese Foundation verbindet die öffentliche Strecke von der Landingpage über
die Betriebsbeschreibung, die beiden Analysezustände und die
Verständnisbestätigung. Sie verändert weder den Analysevertrag noch den
Vier-Aufruf-Flow, das RAG, den Lösungskatalog oder die Ergebnisdaten.

Die sichtbare Results V1 übernimmt diese semantischen Tokens und
Interaktionsmuster. Damit bleibt der Wechsel von der Analyse in die
Auswertung ein Wechsel innerhalb desselben Produkts, nicht in eine zweite
visuelle Sprache. Die Results-spezifischen Komponenten liegen getrennt in
`app/templates/results_v1.html`, `app/templates/results_experiences.html`,
`app/static/results-v1.css` und `app/static/results-v1.js`.

Der Page Background ist dabei eine globale Produktkonstante. Seine Komposition
ist nicht neu angenähert, sondern aus dem sichtbaren Kopf der aktuellen
Results-Seite übernommen: der Weiß-zu-Creme-Verlauf, der zweite Teal-Radiallayer
und der langsam wandernde Teal-Schein. Landingpage, Betriebsbeschreibung,
Processing, Verständnisbestätigung und Results verwenden dieselbe zentrale
Backdrop-Schicht aus `app/templates/_page_background.html` und
`app/static/styles.css`.

## Produktversprechen entlang der Strecke

Die Strecke erzählt durchgängig denselben Dreiklang:

1. Der Betrieb beschreibt einen echten Ablauf in eigenen Worten.
2. AI Start Map bestätigt zuerst Engpass und Ist-Ablauf.
3. Danach entsteht eine begründete Auswertung mit sinnvollem Startpunkt und
   einem möglichen künftigen Ablauf.

Die Landingpage verkauft deshalb keine allgemeine Liste von KI-Ideen. Sie
zeigt den erwartbaren Entscheidungsvorteil. Die Interviewseite verlangt keine
Vorbereitung oder Lösungssprache. Die Verstandenseite bleibt eine
Diagnosebestätigung und spielt noch keine Ergebnisdarstellung vor.

Der Landing-Hero benennt diesen Nutzen verbindlich als Frage: „Finden Sie
heraus, wo KI Ihnen wirklich Arbeit abnehmen kann.“ Er erklärt anschließend
Aufwand, sinnvolle KI- und Automatisierungsverbesserungen, einen möglichen
Beginn und die künftig besser zusammenspielenden Abläufe.

## Semantische Design-Tokens

Die Tokens stehen zentral in `app/static/styles.css` unter `:root`.

| Token | Zweck |
|---|---|
| `--page-bg`, `--page-bg-gradient` | Grundfarbe und beide Results-Gradient-Layer |
| `--page-bg-position`, `--page-bg-size`, `--page-bg-repeat` | verbindliche Layer-Geometrie |
| `--page-bg-height`, `--page-bg-glow` | Höhe und bewegter Results-Schein |
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
- zeigt Engpass, sinnvollen Start und möglichen künftigen Ablauf als kompakten
  Ergebnisvorgeschmack;
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
- erklärt knapp, dass Engpass, möglicher künftiger Ablauf und sinnvoller erster
  Schritt zusammengeführt werden.

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

Results V1 übernimmt `--page-bg`, die Surface-, Text-, Border-, Radius-,
Shadow-, Width-, Spacing- und Motion-Tokens direkt. Für normale Inhalte,
wichtige Zielbildflächen und Handlungen verwendet sie die vorhandenen Karten-
und Buttonmuster, ergänzt aber keine zweite lokale Palette.

Results V1 bindet außerdem `_page_background.html` ein. Die Backdrop-Schicht
beginnt unter der jeweiligen oberen Produktleiste; Seiteninhalt und Karten
liegen transparent darüber. Eigene `body`-, Full-height-Wrapper- oder
Hero-Hintergründe dürfen diese Grundkomposition nicht zurücksetzen. Damit
bleiben Grundfarbe, Verlauf, Intensität und Bewegung beim Seitenwechsel
konstant.

Results V1 übernimmt weder parallel gepflegte lokale Farbwerte noch einen
zweiten Satz Radien und Schatten unter `.ergebnis`. Die fachliche
Informationsarchitektur wird ausschließlich aus `ResultDTO` projiziert:
Engpass, Start, Anker, Operating Center, Capabilities, Evidence, Human
Boundaries, Future und die konkrete Lösungsvorschau aus `ansichten`. Die
sichtbare Betriebslandkarte ist dabei die feste
vierstufige Strecke **Heute → Was verbindet → Neuer Arbeitsstand → Später
möglich**. Sie zeigt nur bereits im DTO entschiedene Inhalte und trifft im
Renderer keine neue fachliche Entscheidung. Experience-Inhalte und Why-not
bleiben Vertragsdaten; die Experience-Inhalte werden nach dem Alltagsflow als
eigene, kontrollierte Lösungsvorschau mit einer Haupt- und höchstens zwei
ergänzenden Ansichten gezeigt.

## Status

Die Pre-Results Foundation ist auf `feature/pre-results-ui-foundation`
implementiert und getestet. Die saubere Results-V1-Webprojektion ist auf
`feature/results-v1-clean-sheet` implementiert und wird dort separat geprüft.
Beide Branches werden nicht automatisch in `feature/final-stabilization`
zusammengeführt.
