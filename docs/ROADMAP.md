# Roadmap

**Last Updated:** 2026-08-05

Diese Roadmap enthält geplante Arbeit. Ein Punkt ist erst umgesetzt, wenn er im Code beziehungsweise Produkt verifiziert und anschließend in `CHANGELOG.md` dokumentiert wurde.

## Now

### Fachliche Arbeit

- Bestehendes Diagnosewissen auswerten und strukturiert inventarisieren.
- Eine Pain-Point-Taxonomie erarbeiten.
- Symptome, Ursachen und Problemfamilien fachlich sauber trennen.
- Ein vierstufiges Reifegradmodell ausarbeiten:
  1. Ordnung
  2. Digitalisierung
  3. KI-Unterstützung
  4. Automatisierung
- Die Leitregel operationalisieren: **„Ordnung vor Automatisierung, aber nicht Ordnung statt KI.“**
- Einen kleinen, hochwertigen Solution-Pattern-Katalog entwerfen.
- Hausmeister, Schuhmacher und Massagesalon gezielt fachlich bewerten.

### Technische Arbeit

- Datenschutz-, Betriebs- und Deployment-Konfiguration vor einem öffentlichen Produktivbetrieb abschließend prüfen.
- Noch keine ungeprüften Solution Patterns in Prompts, RAG oder Laufzeitlogik integrieren.
- Für die drei Zielbeispiele reproduzierbare Evaluationseingaben und erwartete Qualitätskriterien definieren.
- Die Bereitstellung der ignorierten produktiven FAISS-Artefakte für einen frischen Checkout beziehungsweise das Deployment verifizieren.

### Produktarbeit

- Aktuelle Ergebnis- und PDF-Ausgaben anhand realer Beispiele auf Länge, Verständlichkeit und konkrete Handlungsfähigkeit prüfen.
- Die Fehlentscheidungen des Recommendation Layers sammeln und nach Problemfamilie ordnen.

## Next

### Fachliche Arbeit

- Den Solution-Pattern-Katalog fachlich freigeben.
- Pro Solution Pattern Eignung, Voraussetzungen, Ausschlusskriterien, Reifegrad, menschliche Kontrolle und kleinen Test definieren.
- Auswahlregeln entwickeln, die nicht jeden Betrieb automatisch bei „Ordnung“ beginnen lassen.

### Technische Arbeit

- Fachlich freigegebene Solution Patterns strukturiert integrieren.
- Die Recommendation-Auswahl gegen Pain-Point-Taxonomie, Ursache und Reifegrad ausrichten.
- Gezielte Tests für Hausmeister, Schuhmacher und Massagesalon ergänzen beziehungsweise schärfen.
- Agent-Pattern-Retrieval kontrolliert in die Entscheidungslogik einbinden und gegen deterministische Guardrails absichern.
- Observability für Retrieval-Auswahl, Agentenaktion, Promptphase, Validierung und Ergebnisqualität entwerfen.

### Produktarbeit

- Kundensprache kürzen und technische Begriffe reduzieren.
- Ergebnisansicht stärker priorisieren und vertiefende Inhalte konsequent einklappen.
- Druckansicht auf weniger Text und stabilere Seitennutzung optimieren.

## Later

### Fachliche Arbeit

- Solution-Pattern-Abdeckung schrittweise um weitere bestätigte Problemfamilien erweitern.
- Reifegrad- und Auswahlregeln anhand echter AI-Start-Map-Interviews kalibrieren.

### Technische Arbeit

- Echtes LLM-Function-Calling für klar typisierte, interne Agentenwerkzeuge einführen.
- Einen dynamischen Interview-Agenten aufbauen, der weiterhin durch deterministische Budgets und Sicherheitsregeln begrenzt wird.
- End-to-End-Observability und Tracing implementieren.
- Agent-Pattern-Retrieval evaluieren und nur bei nachgewiesenem Qualitätsgewinn dauerhaft aktivieren.

### Produktarbeit

- Interviewtiefe und Ergebnisdarstellung anhand realer Nutzung weiter kalibrieren.
- Mobile und Print-Darstellung auf den festgelegten Zielbrowsern vollständig abnehmen.

## Not planned yet

### Fachliche Arbeit

- Kein breiter, ungeprüfter Katalog beliebiger KI-Ideen.
- Keine Ausweitung über die Diagnose eines konkreten Geschäftsprozesses hinaus.

### Technische Arbeit

- Keine autonome Ausführung realer Unternehmensprozesse.
- Keine automatischen Preis-, Vertrags-, Zahlungs-, Qualitäts- oder Freigabeentscheidungen.
- Keine neuen Datenbanktabellen oder Felder ohne bestätigten aktuellen Produktbedarf.
- Keine Ablösung der vorhandenen Architektur durch zusätzliche Frameworks oder schwere PDF-Infrastruktur ohne neue Entscheidung.

### Produktarbeit

- Keine Zusage bestimmter Drittanbieterintegrationen oder APIs, solange diese nicht verifiziert und freigegeben sind.
- Kein automatisches Anhängen oder Versenden des PDF-Berichts; Kontakt bleibt derzeit ein `mailto:`-Link.
