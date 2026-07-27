# AI Start Map V2 – sichtbare Nutzerreise

_Stand: 26.07.2026_

## Zielreise

```text
Landingpage
→ freie Erzählung per Sprache oder Text
→ automatische Prozesserkennung
→ einen von höchstens drei Abläufen auswählen
→ kurze Zusammenfassung bestätigen oder korrigieren
→ nur entscheidungsrelevante Rückfrage(n)
→ sichtbare Verarbeitung
→ Kernoutput
→ optional Startplan, Details, PDF, weiterer Ablauf oder Kontakt
```

Die Fortschrittsanzeige hat überall drei Zustände: `Erzählen → Verstehen → Ergebnis`. Rückfragen gehören zu „Verstehen“. Die interne numerische Session-ID erscheint weder in URLs der öffentlichen Reise noch im Seiteninhalt.

## Minimal-Change-Plan

Die vorhandenen FastAPI-Routen, fünf PostgreSQL-Tabellen, JSONB-Ergebnisfelder, Structured Outputs, RAG-Services und signierten Sitzungscookies bleiben erhalten. Es ist keine Migration erforderlich. Die sichtbaren Templates, zentrale Styles, Analysefelder und Agentenheuristiken wurden innerhalb dieser Architektur angepasst.

## Landingpage

Die Seite besteht aus fünf scanbaren Bereichen: Hero, Wiedererkennung, drei Schritte, Abgrenzung zu allgemeiner KI und Schluss-CTA. Der Hero ist die stärkste visuelle Ebene; der folgende Abschnitt wird bereits am unteren Viewportrand angedeutet. Das Versprechen lautet: Alltag erzählen, eigentliches Problem verstehen, ersten Schritt erkennen und konkrete KI-Unterstützung sehen.

## Erzählen und Processing

Browser-Spracherkennung (`SpeechRecognition`/`webkitSpeechRecognition`) nutzt Deutsch als Standardsprache. Das Transkript bleibt editierbar und ein großes Textfeld funktioniert immer als Fallback. Beim Absenden werden Schaltflächen sofort deaktiviert und der gemeinsame Processing-Layer angezeigt.

Nach der Erzählung lädt eine automatische Verarbeitungsansicht die Prozesserkennung ohne weitere Schaltfläche. Bei der finalen Analyse fragt die Seite den echten Serverstatus ab und leitet nach Abschluss automatisch zum Ergebnis weiter. Es gibt keine künstlichen Prozentangaben. Fehler erhalten die Eingaben und bieten Retry beziehungsweise Rückkehr zur Korrektur.

Ein späterer `MediaRecorder`- und Transkriptionsweg ist nicht umgesetzt und bleibt eine mögliche Erweiterung.

## Prozesswahl und Bestätigung

Die App zeigt höchstens drei Prozesse und markiert die wahrscheinlich relevanteste Option. Jede Karte enthält standardmäßig nur Name, kurzen Problemsatz und die Hauptaktion. Start und Ende sind unter „Details anzeigen“ eingeklappt.

Die Bestätigung zeigt höchstens fünf kurze Ist-Schritte als responsive vertikale HTML-/CSS-Prozessleiste. Der Nutzer wählt „Ja, passt“ oder öffnet „Etwas stimmt nicht“. Erst dann erscheinen Sprach-/Textkorrektur und einzelne editierbare Schritte. Mermaid wird in der sichtbaren Nutzerreise und im Bericht nicht mehr verwendet; Lesbarkeit und sichere Zeilenumbrüche haben Vorrang.

## Rückfragen und Agent

Der Agent darf `ASK`, `CLARIFY`, `RETRIEVE`, `ANALYZE` oder `STOP` wählen. Eine Frage ist nur zulässig, wenn sie Kernproblem, ersten Schritt, konkrete KI-Hilfe, Wochen-Test, spätere Automatisierung, eine zwingende Freigabe, eine kritische Voraussetzung oder die Entscheidung über den aktuellen KI-Einsatz ändern kann.

- Null Rückfragen sind ausdrücklich möglich.
- Normal sind null bis zwei Fragen.
- Drei Fragen sind komplexen Fällen vorbehalten.
- Vier bleiben die technische sichtbare Obergrenze.
- Beantwortete, bestätigte, korrigierte, aus der Erzählung bekannte und bewusst übersprungene Informationen werden nicht erneut gefragt.
- „Das habe ich doch schon gesagt“ führt zur erneuten State-Prüfung, nicht zur Rechtfertigung oder Wiederholung.
- „Weiß ich nicht“ bleibt als Unsicherheit erhalten.

Die zentralen, später zu kalibrierenden Heuristiken liegen ausschließlich in `app/agent_config.py`. Agenten- und Tool-Runden bleiben begrenzt. Nutzerfakten, Extraktionen, Ableitungen, RAG-Evidenz, Widersprüche und Unsicherheiten bleiben technisch getrennt.

## Kernoutput

Der erste Ergebnisbildschirm folgt verbindlich dieser Reihenfolge:

1. Dein eigentliches Problem.
2. Das solltest du zuerst ändern.
3. So kann KI dir konkret helfen: Eingabe, KI-Aufgabe, Ergebnis und menschliche Kontrolle.
4. Das kannst du diese Woche testen: höchstens drei Schritte und ein beobachtbares Erfolgskriterium.
5. Später kannst du automatisieren: genau ein realistischer Ausbau nach erfüllter Voraussetzung.

Ist KI heute noch nicht sinnvoll, sagt das Ergebnis ausdrücklich, dass KI noch nicht der erste Schritt ist, und nennt die Voraussetzung für eine spätere konkrete Unterstützung. Tieferer Diagnosekontext, heutiger Ablauf, Unsicherheiten und spätere Möglichkeiten sind standardmäßig geschlossen.

## Startplan, PDF und Kontakt

„Zeig mir, wie ich anfangen kann“ öffnet drei bis fünf Schritte, notwendige Dinge, Erfolgskriterium und menschliche Entscheidungen. Preise, Verträge, Zahlungen, Qualität, Ausnahmen und unklare Zuordnungen bleiben beim Menschen.

Die Druckansicht besteht im Normalfall aus genau drei A4-Seiten:

1. Kernproblem, erster Schritt, konkrete KI-Hilfe und Wochen-Test.
2. Heutiger Ablauf, schwierige Stellen und kurze Begründung.
3. Startplan, Voraussetzungen, menschliche Entscheidungen, Erfolgskriterium, spätere Automatisierung und Kontakt.

Die PDF wird über `window.print()` gespeichert. Der Mailto-Link behauptet nicht, die PDF automatisch anzuhängen.

## Daten- und Wissensgrenzen

Der Diagnoseindex mit 634 Chunks und der Agent-Pattern-Index mit 205 Patterns bleiben getrennt. Alle 79 Evaluationen bleiben außerhalb jedes Indexes. RAG-Evidenz ist nur Vergleichswissen und wird niemals als Nutzerfakt gespeichert oder sichtbar ausgegeben. In dieser Überarbeitung wurden weder Research-Batches noch Indizes neu gebaut.

## Abnahme

Automatisiert geprüft werden Kernoutput, Agentenlimits, Null-Rückfragen, No-Repeat, Schuhmacher, Massagesalon, Betrieb ohne digitale Grundlage, menschliche Preis-/Terminfreigabe, Processing-Verträge, responsive CSS-Grundregeln, drei Berichtseiten und das Fehlen interner IDs. Eine echte Gerätefreigabe bleibt erst nach visueller Prüfung in Chrome, Android und iPhone/Safari vollständig.
