# AI Start Map V2 – sichtbare Nutzerreise

_Stand: 2026-07-22_

## Bestehender Ausgangspunkt

Das Repository enthält einen funktionierenden FastAPI-/Jinja2-Fluss mit PostgreSQL-Persistenz, fünf Tabellen, strukturierten OpenAI-Ausgaben, FAISS-RAG, drei Demo-Routen und automatisierten Tests. Der bisher sichtbare Ablauf besteht aus Landingpage, zwei Einstiegsfragen, Prozessvorschlägen, sieben Pflichtfragen, bis zu drei gleichzeitig sichtbaren Rückfragen, Analyse-Ladeansicht und Ergebnis mit drei Chancen sowie Blueprint.

Weiterverwendet werden die bestehenden Routenfamilien für Start, Interview, Prozessoptionen, Prozessdetails, Rückfragen, Analyse-Status, Analyse und Ergebnis sowie `/demo/{demo_slug}`. Die sichtbaren Seiten und einzelne Handler werden innerhalb dieser Architektur neu zugeschnitten.

## Zielreise

```text
Landingpage
→ freie Beschreibung per Sprache oder Text
→ erkannte Prozessoptionen
→ Auswahl eines Ablaufs
→ strukturierte Zusammenfassung und kontrolliertes Ist-Diagramm
→ Bestätigung oder Korrektur
→ höchstens vier dynamische Rückfragen, einzeln angezeigt
→ sichtbarer Analyse- und Fehlerzustand
→ priorisiertes Ergebnis mit Ist- und nächstem Soll-Ablauf
→ erster Schritt / Druck-PDF / weiterer Ablauf / Kontakt
```

Die interne numerische Session-ID wird nie als Seiteninhalt gezeigt. Bestehende Angaben bleiben bei Analysefehlern erhalten. Mehrfaches Absenden wird in Oberfläche und Backend begrenzt.

## Minimal-Change-Plan

1. Vorhandene FastAPI-Routen und Tabellen weiterverwenden; keine Migration und keine neue Produktionsabhängigkeit.
2. Bestehende Interview-Datensätze für freie Beschreibung, strukturierte Prozessdaten, Korrekturen und dynamische Rückfragen verwenden.
3. Strukturierte Schemas nur um die für Darstellung und Priorisierung nötigen Felder erweitern; Fakten, Ableitungen, Unsicherheiten und Empfehlungen getrennt halten.
4. Templates und das zentrale Stylesheet mobile-first neu gestalten; gemeinsame kleine JavaScript-Helfer für Sprache, Diagramme und Submit-Schutz ergänzen.
5. Ergebnisse in den vorhandenen JSONB-Feldern speichern und für Webansicht sowie Druckansicht normalisieren.
6. Bestehende Demo- und Analyse-Endpunkte erhalten; die sichtbare Reise ohne feste Sieben-Fragen-Seite führen.
7. Erst nach bestandenen Tests und Startprüfung die öffentliche README auf den tatsächlich funktionierenden Stand bringen.

## Seiten und Verhalten

### Landingpage

Lange, klar gegliederte Startseite mit dem freigegebenen Hero, Chaos-zu-Klarheit-Visual, vier Alltagssituationen, psychologischer Entlastung, drei Funktionsschritten, Chatbot-Abgrenzung, vier möglichen Branchenbeispielen, Vertrauensaussagen und zwei Start-CTAs.

### Freie Beschreibung

Ein großes editierbares Textfeld ist die Datenquelle. Browser-Spracherkennung (`SpeechRecognition` oder `webkitSpeechRecognition`) ergänzt es mit Deutsch als Standardsprache. Sichtbare Zustände: `idle`, `recording`, `processing`, `done`, `error`. Wenn die API fehlt oder eine Berechtigung scheitert, bleibt die Texteingabe vollständig bedienbar. Vor der Eingabe steht der Hinweis, keine vollständigen Namen oder vertraulichen Kundendaten zu nennen.

### Prozesswahl und Verständnis

Die KI erzeugt bis zu drei konkrete Optionen mit Start, Ende und Begründung. Nach Auswahl zeigt die App einen aus strukturierten Daten gebildeten Ist-Ablauf mit fünf bis sieben Hauptschritten, bestätigten Fakten, schwierigen Stellen und offenen Punkten. Nutzer können Titel und Schritte bearbeiten, Schritte ergänzen und eine freie Korrektur sprechen oder schreiben. Empfehlungen erscheinen hier noch nicht.

### Diagramme

Das Backend liefert ausschließlich validierte strukturierte Prozessdaten. JavaScript kürzt und bereinigt Labels und erzeugt daraus kontrolliert `flowchart TD`; Modell-Ausgaben werden nie als Mermaid-Quelltext übernommen. Mermaid läuft im strikten Sicherheitsmodus. Eine vollständige vertikale Listenansicht ist bereits im HTML vorhanden und bleibt bei Lade- oder Renderfehlern sichtbar.

### Rückfragen

Die KI erzeugt meist zwei bis drei, höchstens vier konkrete Fragen. Die Oberfläche zeigt nur die erste noch unbeantwortete Frage. Nach jeder Antwort folgt ein kurzer Verarbeitungszustand; danach erscheint die nächste Frage oder direkt die Analyse. Sprache und Text sind möglich, ebenso „Weiß ich gerade nicht“. Fehlende Angaben bleiben als Unsicherheit erhalten.

Die nächste Aktion wird durch einen begrenzten Diagnostic Interview Agent als `ASK`, `CLARIFY`, `RETRIEVE`, `ANALYZE` oder `STOP` bestimmt. Harte Grenzen, No-Repeat, Schutz bestätigter Fakten und Schleifenabbruch sind deterministisch. RAG-Evidenz bleibt vom Nutzer-State getrennt. Die Demoheuristiken stehen zentral in `app/agent_config.py` und müssen anhand echter Interviews kalibriert werden.

### Ergebnis und erster Schritt

Die Reihenfolge ist: kurze Einordnung, größter Engpass mit Symptom/Ursache/Auswirkung, priorisierter Startpunkt, Mini-Test, bestätigter Ist-Ablauf, nächster realistischer Soll-Ablauf, zwei kleinere Alternativen, Voraussetzungen und echte offene Punkte. Der Blueprint für Rang 1 wird als kompakter Umsetzungsplan auf derselben Seite aufklappbar dargestellt.

### Druck/PDF und Kontakt

Eine eigene druckoptimierte Kundenansicht enthält Branding, Datum, Derya Sarikaya, `deryaxsarikaya@gmail.com`, alle freigegebenen Analysebereiche und robuste Diagramm-Fallbacks. Der Nutzer öffnet mit `window.print()` den Browser-Druckdialog und speichert die Ansicht dort als PDF. Interne IDs, Wissensquellen, Prompts, Modellnamen, Logs und Scores werden nicht ausgegeben. Kontakt erfolgt ausschließlich über den freigegebenen `mailto:`-Link; die Seite weist korrekt darauf hin, die gespeicherte PDF anschließend selbst anzuhängen.

## Mobile und Browsergrenzen

Die Layouts starten einspaltig, Buttons sind mindestens 48 Pixel hoch, Diagramme verlaufen vertikal und Tabellen werden nicht verwendet. Desktop-Erweiterungen setzen erst ab größeren Viewports ein. CSS wird bei schmalen Viewports und die HTML-Struktur mit automatisierten Tests geprüft.

Browser-Spracherkennung ist keine einheitlich unterstützte Webplattform-Funktion. Chromium-basierte Browser bieten sie häufig an; Firefox und manche Safari-/iOS-Versionen können sie nicht oder nur eingeschränkt bereitstellen. Die App erkennt das zur Laufzeit und zeigt dann die Texteingabe ohne Fehler. Ein späterer `MediaRecorder`-Upload mit serverseitiger Transkription kann an dieselbe UI-Zustandslogik angeschlossen werden; Upload-Endpunkt, Dateigrenzen, Einwilligung, Löschkonzept und Transkriptionsanbieter sind bewusst noch offen.

## Datenbankentscheidung

Es ist keine Migration erforderlich. Die fünf vorhandenen Tabellen decken Sitzung, Fragen/Antworten, Prozessoptionen und Ergebnis ab. Variable, nicht separat verwaltete Darstellungsdaten werden in den vorhandenen JSONB-Ergebnisfeldern gespeichert. Es werden keine Zukunftsfelder oder Account-Funktionen ergänzt.

## Wissens- und Agentenfluss

Der Diagnoseindex enthält 634 Chunks aus dem kuratierten Bestand sowie Batch 02 und Batch 03. Batch 04 wird getrennt verwendet: sicherheitskritische Regeln liegen in Code und Prompt, 205 optionale Patterns liegen in einem separaten Index, das State-Schema und die Forschungsdokumente bleiben Dokumentation und 40 Evaluationen bleiben außerhalb jedes Indexes. Die Analyse erhält nur bestätigte Nutzerfakten, getrennte fachliche Ableitungen und offene Unsicherheiten; Retrieval-Inhalte werden niemals als Nutzerfakten gespeichert.

## Geänderte Dateien

### Anwendung

- `app/routes.py`: öffentliche cookie-basierte Reise ohne fortlaufende Session-ID in der URL, strukturierte Zusammenfassung, einzelne Rückfragen, Ergebnisnormalisierung, Druckansicht und weiterer Ablauf.
- `app/schemas.py`: validierte Prozesszusammenfassung, maximal vier eindeutige Rückfragen und zusätzliche getrennte Ergebnisfelder.
- `app/openai_service.py`: strukturierte Rekonstruktion vor den Rückfragen sowie Diagnose- und Reifegradregeln für die drei Startpunkte.
- `app/static/app.js`: Submit-Schutz, Spracheingabezustände und Schrittbearbeitung.
- `app/static/diagrams.js`: kontrollierte vertikale Mermaid-Erzeugung aus strukturierten Daten mit striktem Sicherheitsmodus.
- `app/static/styles.css`: freigegebenes Designsystem, mobile-first Layout, große Touch-Flächen und Druckregeln.
- `app/templates/*.html`: vollständige sichtbare Reise; neu ist `report.html`.
- `.env.example`: optionaler `SESSION_SIGNING_KEY` für über Neustarts stabile signierte Sitzungscookies.

### Tests und Dokumentation

- `tests/test_interview_flow.py`, `tests/test_analysis_flow.py`, `tests/test_quality_pass.py`: bestehende Prüfungen auf die neue sichtbare Reise abgestimmt.
- `tests/test_ux_journey.py`: vollständiger öffentlicher Ablauf, Spracheingabe-Fallback, sichere Diagramme, Ergebnis, Bericht, Session-Schutz und responsive Grundregeln.
- `AGENTS.md`, `TODO.md`, `UX_FLOW.md`, `README.md`: Produktregeln, Umsetzungsstand, technische Entscheidungen und öffentliche Projektübersicht.

## Ausgeführte Prüfungen

- `pytest -q`: 69 Tests bestanden.
- 40 von 40 Batch-04-Aktionsorakeln bestanden; alle 79 Evaluationen wurden als nicht indexierbar verifiziert.
- Diagnoseindex: 634 Chunks; Agent-Pattern-Index: 205 Patterns; alter 111er-Index gesichert.
- `alembic upgrade head`: erfolgreich; keine neue Migration und keine Schemaänderung.
- Python-Kompilierung der geänderten Module: erfolgreich.
- Lokaler Uvicorn-Start und HTTP-Aufruf der Landingpage: Status 200, neuer Hero vorhanden.
- Mobile Regeln automatisiert geprüft: Breakpoint, fehlender horizontaler Seitenlauf, vertikale Karten/Diagramme, große Buttons und keine Tabellen.

Eine echte visuelle Browserprüfung auf emulierten Android-/iPhone-Viewports konnte in dieser Arbeitsumgebung nicht ausgeführt werden, weil die bereitgestellte Browser-Steuerung keine lokale Node-Laufzeit starten konnte. Das ist keine behauptete Gerätefreigabe; vor Produktivfreigabe bleibt eine manuelle Prüfung in Chrome/Android und Safari/iPhone sinnvoll.
