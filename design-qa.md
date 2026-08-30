# Results V1 — Design QA

## Vergleichsgrundlage

- Source visual truth: `C:\Users\Derus\.codex\visualizations\2026\08\28\01a047b2-0bbd-7e11-8481-2f08c6cd2887\results-audit-new\06-desktop-map.png`
- Weitere verbindliche Source-Ansichten: `03-desktop-future-flow.png` und
  `04-desktop-mockups-a.png` im selben Verzeichnis.
- Implementierung: `http://127.0.0.1:8019/beispiel/hausverwaltung`
- Desktop-Map-Capture: `C:\Users\Derus\.codex\visualizations\2026\08\30\results-v1-sollbild-qa\02-ai-start-map-desktop.png`
- Mobile-Map-Capture: `C:\Users\Derus\.codex\visualizations\2026\08\30\results-v1-sollbild-qa\07-ai-start-map-mobile-390.png`

Der Source-Map-Ausschnitt misst 1425 × 990 px. Der aktuelle Desktop-Capture
misst 1265 × 712 px bei einem 1280 × 720 CSS-Viewport. Beide zeigen denselben
Hausverwaltungs-Zustand, aber nicht denselben Scroll-Crop; verglichen wurden
deshalb die Kartenfläche und der Detailbereich, nicht Browser-Chrome oder
der obere Seitenabstand. Der Mobile-Capture misst 375 × 812 px bei einem
390 × 844 CSS-Viewport. Es wurde keine künstliche Pixel-Normalisierung
vorgenommen, da die Prüfung auf Informationshierarchie und Layoutstruktur
zielt, nicht auf eine 1:1-Rasterkopie.

## Vergleichsverlauf

1. **Erster Vergleich — blocked.** Die erste Landschaft hatte lange
   Modulnamen an allen 14 Punkten; dadurch überlappten Beschriftungen im
   Wissensgebiet. Auf Mobile entstanden nach dem Startfilter leere Karten,
   weil die ruhigen Labels visuell ausgeblendet waren.
2. **Korrektur.** Die Kartenpunkte verwenden feste, kurze
   Präsentationslabels für die vorhandenen Operating-Module; stille Punkte
   bleiben als Orientierungspunkte, ohne die Karte zu überladen. Der
   Operating Center wird mehrzeilig lesbar gesetzt. Der initiale State-Filter
   wird nur bei einem echten Mobile-Erstaufruf angewendet; ohne JavaScript
   bleibt die vollständige Liste lesbar.
3. **Nachvergleich — passed.** Desktop zeigt wieder sechs Flächen,
   verbindende Wege, Operating Center, Start-/Ziel-/Später-Zustände und ein
   evidenzgebundenes Detailpanel. Mobile zeigt zunächst nur die zwei
   Startmodule und keine leeren Karten; der Zielbildfilter und der
   Modulklick wurden funktional geprüft.

## Fidelity-Prüfung

- **Typografie:** Display-Schrift, Gewicht, ruhige Sans-UI-Texte und die
  reduzierte Map-Überschrift folgen der gemeinsamen Foundation. Dynamische
  Beschriftungen bleiben innerhalb der Module; keine Trunkierung beobachtet.
- **Spacing und Layout:** Karte und Detail teilen sich den Desktop in einen
  klaren 2/3–1/3-Arbeitsbereich. Der Flow ist kompakt als durchgehende
  Sequenz gesetzt. Auf 390 px wird die Karte bewusst zur gefilterten Liste;
  kein horizontaler Überlauf.
- **Farben und Tokens:** Ausschließlich bestehende Cream-, Teal-, Sand- und
  Surface-Tokens; Start, Zielbild, Zukunft und menschliche Entscheidung sind
  semantisch unterscheidbar, ohne eine zweite Results-Palette.
- **Bild-/Asset-Fidelity:** Die Map verwendet die vorhandene feste
  Sechs-Gebiete-Geometrie aus dem Produkt statt einer neuen Illustration.
  Experience-Previews verwenden ausschließlich die vorhandene, DTO-gebundene
  Experience-Bibliothek. Es wurden keine neuen Bild- oder Icon-Assets
  erzeugt.
- **Copy und Inhalt:** Start, Evidenz, Module, Experience, Grenzen, Future
  und Why-not stammen aus dem ResultDTO. Die ergänzenden Überschriften
  beschreiben nur die feste Darstellungsstruktur.
- **Interaktion und Accessibility:** Map-Nodes sind echte Buttons mit
  `aria-pressed`; die Filter aktualisieren sichtbare States und das
  Detailpanel. Mobile-Zielbildfilter und Node-Auswahl wurden geprüft.
  Native Fokusstile und `prefers-reduced-motion` bleiben aus der Foundation
  aktiv. Der Kerninhalt ist ohne JavaScript weiterhin im HTML vorhanden.

## Restgrenzen

- Der gespeicherte Beispielrun enthält keinen `why_not`-Eintrag. Deshalb
  erscheint dort korrekt kein Why-not-Panel; die Vorlage rendert es nur bei
  vorhandenem DTO-Inhalt.
- PDF/Web verwenden weiter dasselbe DTO. Die visuelle PDF-Paginierung ist
  nicht gegen einen neuen Referenz-PDF-Entwurf pixelverglichen, weil für diese
  Korrektur kein separater PDF-Visual-Target vorliegt.

## Final result

passed
