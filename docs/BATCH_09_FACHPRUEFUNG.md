# Fachprüfung Batch 09

**Status:** Review abgeschlossen; ausgewählte Inhalte für eine kontrollierte Runtime-Übernahme geeignet, noch nicht integriert

**Prüfdatum:** 2026-08-06

**Lieferung:** `knowledge/candidates/batch_09/`

**Herkunftsstatus:** `research_proposed`

## Prüfumfang und Annahmen

Die unveränderte Kandidatenlieferung bleibt die Herkunftsquelle. Korrekturen und Runtime-spezifische Verschärfungen werden nicht still in das Research-Original geschrieben, sondern später als nachvollziehbare Runtime-Kopie umgesetzt.

Automatisiert geprüft wurden alle Dateien auf JSONL-/CSV-Lesbarkeit, eindeutige IDs, gültige `PF-01` bis `PF-12`- und `SP-01` bis `SP-10`-Referenzen, Quellenreferenzen und erwartete Mengen. Das Ergebnis entspricht der Lieferung:

- 27 Inference Patterns,
- 28 Solution Workflows,
- 10 Output-Strukturen,
- 30 Evaluationen,
- 20 Quellen,
- Evaluationsverteilung 10 `ambiguous`, 10 `clear`, 5 `multiple`, 5 `no_ai`.

Alle verwendeten `source_refs` sind im Quellenregister vorhanden. Neun der zwanzig registrierten Quellen werden nur in der begleitenden Herleitung und nicht direkt in den vier JSONL-Dateien referenziert; das ist kein formaler Fehler, begrenzt aber die Rückverfolgbarkeit einzelner Datensätze auf elf direkt verknüpfte Quellen.

## Geprüfte Stichprobe

### Inference Patterns

Fachlich näher geprüft wurden neun Patterns über alle im Batch vertretenen Problemfamilien: `IP-01`, `IP-04`, `IP-07`, `IP-10`, `IP-13`, `IP-16`, `IP-19`, `IP-22` und `IP-25`.

### Solution Workflows

Fachlich näher geprüft wurden zehn Workflows, je einer pro Solution Pattern: `SW-SP01-02`, `SW-SP02-01`, `SW-SP03-01`, `SW-SP04-01`, `SW-SP05-02`, `SW-SP06-02`, `SW-SP07-01`, `SW-SP08-01`, `SW-SP09-01` und `SW-SP10-01`.

### Output-Strukturen

Alle zehn Strukturen `OUT-SP-01-BASE` bis `OUT-SP-10-BASE` wurden vollständig auf Feld-IDs, Pflichtfelder, Quellenarten, Beispielwerte, Human Review und Nicht-Automationen geprüft.

### Evaluationen

Alle 30 Fälle wurden automatisiert auf Struktur, Labelstatus, Indexausschluss und Verteilung geprüft. Zwölf Fälle wurden zusätzlich fachlich näher gelesen: `B09-EVAL-001`, `003`, `004`, `005`, `006`, `008`, `009`, `012`, `018`, `020`, `022` und `029`.

## Stärken

- Hypothesen sind konsequent als `must_be_confirmed` gekennzeichnet und nicht als Tatsachen über einen Betrieb formuliert.
- Verifikationsfragen fragen überwiegend nach beobachtbarem Verhalten oder vorhandenen Daten statt nach Selbsteinschätzungen.
- Die kleinsten KI-Schritte erzeugen prüfbare Entwürfe und markieren Lücken; sie behaupten keine autonome End-to-End-Ausführung.
- Die Workflows beginnen mit konkreten digitalen Quellen, trennen KI, deterministische Regeln und menschliche Prüfung und enden in einem sichtbaren Arbeitsergebnis.
- Preis-, Vertrags-, Zahlungs-, Personal-, Qualitäts-, Herausgabe- und verbindliche Freigabeentscheidungen bleiben ausdrücklich beim Menschen.
- Jede Output-Struktur besitzt stabile Feld-IDs und kennzeichnet Beispielwerte unmissverständlich als Nicht-Kundenfakten.
- Alle Evaluationen tragen `label_status: research_proposed` und `index_policy: exclude_from_all_rag_indexes`.

## Schwächen und verbleibende Unsicherheiten

1. Die zwei `answer_branches` der Inference Patterns sind meist abstrakte Spiegelbilder „Grundlage vorhanden/nicht vorhanden“. Sie helfen bei der Frageauswahl, reichen aber ohne Auswertung einer konkreten Nutzerantwort nicht für einen automatischen Pattern-Statuswechsel.
2. Die Workflows verwenden neben `user`, `ai`, `software_rule` und `human` den Akteur `system`. Inhaltlich ist der letzte Schritt eine deterministische Speicher-/Freigaberegel und soll in der Runtime als `software_rule` normalisiert werden.
3. `SW-SP04-01` ist kein KI-Workflow, sondern bewusst ein dokumentarischer Ausschluss. Er darf weder semantisch als positive Empfehlung noch als Batch-09-KI-Lösung verwendet werden.
4. In `OUT-SP-04-BASE` sind Objekt-ID, physischer Ablageort und prüfende Person manuelle beziehungsweise bestehende Angaben, aber noch nicht konsistent als zwingend menschlich zu bestätigen markiert. Eine Runtime-Kopie muss diese Grenze verschärfen.
5. Human Checks, Mindestvoraussetzungen und Fehlerfälle der Workflows sind weitgehend generisch. Sie sind ein sicherer Basisschutz, aber kein Beleg für branchenspezifische Vollständigkeit.
6. `B09-EVAL-020` ordnet einen bereits vollständigen digitalen Einsatzbericht weiterhin `PF-08` zu, obwohl laut Text nur die menschliche Preisentscheidung fehlt. Das Label bleibt deshalb ausdrücklich unbestätigt und darf nicht als Ground Truth optimiert werden.
7. Öffentliche Quellen stützen die allgemeine Richtung. Die konkreten Branchenworkflows bleiben `source_synthesized` und müssen mit realen Betrieben kalibriert werden.

## Vorgenommene Korrekturen

Am Research-Original wurden keine stillen inhaltlichen Änderungen vorgenommen. Das bewahrt Herkunft und Vergleichbarkeit. Für die kontrollierten Runtime-Kopien sind folgende reproduzierbare Korrekturen vorgesehen:

- Workflow-Akteur `system` wird zu `software_rule` normalisiert.
- `SW-SP04-01` bleibt nur dokumentarisch und wird aus positivem Lösungswissen ausgeschlossen.
- Die drei Pflichtfelder von `OUT-SP-04-BASE` verlangen menschliche Bestätigung.
- Beispielwerte werden vom Loader nie in Kundendaten übernommen.

## Qualitätsstatus

| Bereich | research_proposed | reviewed | runtime_approved |
|---|---:|---:|---:|
| 27 Inference Patterns | ja | Stichprobe 9/27 | nein; nur nach typisierter Hypothesenlogik |
| 28 Solution Workflows | ja | Stichprobe 10/28 | nein; erst nach Rollen-Normalisierung und Ausschluss SP-04 |
| 10 Output-Strukturen | ja | 10/10 | bedingt; nach Pydantic-Validierung und SP-04-Verschärfung |
| 30 Evaluationen | ja | 30 strukturell, 12 fachlich | nein; Evaluation bleibt niemals Runtime-Wissen |

`reviewed` bedeutet hier eine nachvollziehbare Fach- und Strukturprüfung, nicht bestätigte Wahrheit. `runtime_approved` wird erst gesetzt, wenn die kontrollierte Kopie geladen, getestet und im tatsächlichen Laufzeitpfad verwendet wird.
