# Requirements – Solution-Pattern-Recommendation

**Status:** Active – implemented, integrated and tested
**Datum:** 2026-08-06
**Source of Truth:** Diese Feature-Spec; Kataloginhalte stammen ausschließlich aus der Fachgrundlage vom 2026-08-05.

## Ziel

Der Recommendation Layer wählt aus bestätigtem Prozessproblem, Problemfamilie und getrennten Gates genau einen besten realistischen KI-unterstützten Einstieg. Leitregel: **So wenig Ordnung wie zwingend nötig, so früh konkrete KI-Unterstützung wie realistisch möglich, und Automatisierung erst nach bestätigten Daten und klaren Freigaben.**

## Scope

- exakt zwölf Problemfamilien `PF-01` bis `PF-12` und zehn Solution Patterns `SP-01` bis `SP-10` als versionierte, validierte Dateien,
- deterministische Klassifikation und Vorauswahl über Vorgangsanker, Kanaleignung, Prozess-/Datenreife, Fehlerauswirkung, Regelstabilität und Human Approval,
- primäre Empfehlung, null bis zwei sekundäre Kandidaten, Ausschlussgründe, Voraussetzungen und Freigabegrenzen,
- Diagnose-RAG für Fälle, Ursachen, Fragen, Risiken, Voraussetzungen und Guardrails; konkrete Auswahl primär aus Katalog und Gates,
- kontrollierte Agent-Pattern-Nutzung für nächste Frage/Aktion bei unveränderten Python-Guardrails,
- kompakter neuer Kundenausgabevertrag und rückwärtskompatible Darstellung alter Analysen,
- Falltests für Hausmeister, Schuhmacher, Blumenladen und Massagesalon.
- technische Trennung von direkt geladenem Katalog und Fragepatterns, noch nicht integrierten Fachkandidaten, niemals indexierbaren Evaluationen und archivierten Herkunftsartefakten.
- deterministische Batch-09-Output-Strukturen, unbestätigte Inference Patterns und getrenntes Solution-Workflow-Wissen mit sicherem direktem Fallback.

## Verbindliche Regeln

1. Niedrige Prozessreife bedeutet nicht automatisch ungeeignete digitale Kanäle.
2. Ein geeigneter digitaler Eingang kann frühe KI-Unterstützung ermöglichen.
3. Ein leichter fehlender Vorgangsanker darf Teil derselben Einstiegslösung sein.
4. Physische Objektidentität und realer Ablageort werden nie durch KI erraten.
5. Hochriskante oder extern wirksame Entscheidungen benötigen menschliche Freigabe.
6. Guardrails begrenzen passende Patterns nachvollziehbar, verdrängen sie aber nicht pauschal.
7. Jede Empfehlung besitzt konkrete Nutzerhandlung, KI-Aufgabe, normale Software-/Regelaufgabe, sichtbares Ergebnis, Human Check und Nicht-Automationen; A0 benennt ausdrücklich, dass keine KI nötig ist.
8. Keine Empfehlung wird allein aus einem semantischen Top-k gewählt.
9. Rückfragen sind nur zulässig, wenn die Antwort Problemfamilie, Ursache, Gate, Risiko, Human Check, zulässiges Pattern oder primäre Empfehlung verändert.
10. Normal sind null bis zwei Rückfragen, drei nur in komplexen Fällen, vier technische Obergrenze.
11. Wochentest und Pflicht zu genau drei Opportunities sind aufgehoben.

## Kundenausgabe

Der Outputvertrag entspricht `docs/specs/product-output/requirements.md`: eine primäre Empfehlung, konkrete Ergebnisvorschau, direkte Du-Ansprache, drei bis sechs Zukunftsschritte, getrennte Rollen, offene Angaben, kleinste nutzbare Version, Autonomiestufe, Grenzen und null bis zwei sekundäre Möglichkeiten.

## Nicht-Ziele

- keine autonome Prozessausführung oder kritische Entscheidung,
- kein Solution-Index mit eigener Entscheidungshoheit und keine Evaluation als Produktwissen,
- keine neue Datenbanktabelle oder Migration ohne zwingenden Bedarf,
- keine erfundenen Anbieter, APIs, Tools oder Einsparungszahlen,
- kein Function Calling, wenn der bestehende sichere Controller nicht sauber erweitert werden kann.

## Abnahme

Abnahme erfordert Katalogvalidierung, deterministische Auswahltests, Retrieval- und Agent-Pattern-Nachweis, neue Output-/Sprach-/Längentests, vollständige relevante Regression, App-Start sowie dokumentierte visuelle Prüfung. Unit-Tests allein gelten nicht als visuelle Browserfreigabe.
