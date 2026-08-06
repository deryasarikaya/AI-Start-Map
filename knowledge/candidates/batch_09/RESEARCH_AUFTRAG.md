# Rechercheauftrag Batch 09 — Ableitungsmuster für digital arbeitende Kleinbetriebe

*Diesen Text vollständig in die Recherche geben. Er ist ohne weiteren Kontext
verständlich.*

---

## Auftrag

Erstelle eine maschinenlesbare Wissensbasis mit zwei Dateien für ein
Diagnosewerkzeug, das kleinen Unternehmen einen ersten sinnvollen KI-Schritt
empfiehlt.

Das Werkzeug hat bereits einen Katalog aus zwölf Problemfamilien und zehn
Lösungsmustern. Was fehlt, ist die Brücke dazwischen: **Ableitungsmuster**, mit
denen aus dem, was ein Unternehmer erzählt, geschlossen werden kann, was er
*nicht* gesagt hat, aber mit hoher Wahrscheinlichkeit ebenfalls zutrifft.

## Zielgruppe — bitte streng einhalten

Kleine Unternehmen und Solo-Selbstständige, die **bereits digital arbeiten**,
deren Informationen aber über mehrere Kanäle verteilt, unstrukturiert oder
manuell nachzubearbeiten sind.

Es gibt bei ihnen bereits digitale Spuren: WhatsApp-Nachrichten, E-Mails, PDFs,
Fotos, Sprachnachrichten, Kalendereinträge, Online-Anfragen, Excel-Listen,
digitale Rechnungen.

Beispielbranchen: Blumenladen mit Bestellungen über WhatsApp, Instagram und
E-Mail. Coach oder Berater mit Anfragen, Notizen und Terminvorbereitung.
Fotograf mit Kundenbriefings, Dateien und Freigaben. Agentur oder Freelancer mit
Anfragen, Angeboten und Übergaben. Kleiner Onlinehändler mit Kundenmails,
Reklamationen und Produktdaten. Physiotherapie- oder Arztpraxis mit
Terminanfragen und Dokumentation. Fahrschule. Reinigungsfirma mit
wiederkehrenden Kunden. Restaurant oder Catering mit Bestellungen und
Reservierungen. Handwerksbetrieb, der bereits Smartphone, WhatsApp und digitale
Rechnungen nutzt. Mobiler Dienstleister mit Fotos, Sprache und digitalen Belegen.

**Ausdrücklich nicht gesucht:** rein analoge Betriebe ohne digitalen Kanal,
Betriebe, deren Kernproblem die physische Kennzeichnung oder Lagerung von
Gegenständen ist, sowie Fälle, in denen zuerst eine grundlegende
Prozessorganisation nötig wäre. Dieser Bereich ist bereits abgedeckt.

## Datei 1 — `01_inference_patterns.jsonl`

20 bis 25 Ableitungsmuster. Ein JSON-Objekt pro Zeile, exakt diese Felder:

```json
{
  "pattern_id": "IP-01",
  "name": "kurzer_technischer_name_in_snake_case",
  "wenn_er_sagt": [
    "drei bis fünf Alltagsformulierungen, wie Betroffene es wirklich sagen",
    "keine Fachsprache, keine Prozessbegriffe",
    "so, wie es in einem Gespräch fallen würde"
  ],
  "dann_typisch": "Ein Satz: die Folge, die daraus fast immer entsteht, die der Erzählende aber selbst nicht benannt hat.",
  "warum": "Ein Satz: der Mechanismus dahinter.",
  "prueffrage": "Eine einzige Frage nach konkretem Verhalten, nicht nach Bewertung.",
  "warum_diese_frage": "Ein Satz: was jede der beiden möglichen Antworten verrät.",
  "kleinster_schritt": "Was der Betrieb ab morgen selbst tun kann, ohne Software, ohne Kosten.",
  "gilt_bei": {
    "vorgangstyp": "information",
    "reifegrad_min": 2,
    "kanaele": ["whatsapp", "email", "telefon", "formular", "instagram", "kalender", "pdf", "foto", "sprache", "tabelle"]
  },
  "problem_family_ids": ["PF-02"],
  "solution_pattern_ids": ["SP-01"],
  "source_url": "https://…",
  "source_strength": "high",
  "content_origin": "source_reported"
}
```

### Regeln für die Felder

**`wenn_er_sagt`** ist der wichtigste Teil. Es sind die tatsächlichen
Formulierungen, mit denen Menschen ihr Problem beschreiben — gefunden in Foren,
Erfahrungsberichten, Branchendiskussionen. Nicht: „fehlende
Vorgangsverknüpfung". Sondern: „Ich such dann immer, wo die Anfrage nochmal
war." Bitte wörtlich oder eng am Original.

**`dann_typisch`** ist die Kernleistung dieser Recherche. Es beschreibt die
Folge, die der Erzählende selbst nicht ausspricht. Beispiel: Wenn jemand sagt,
Anfragen kommen über drei Kanäle, dann ist die typische Folge nicht „Unordnung",
sondern etwas Konkretes wie „Anfragen, die abends kommen, werden am ehesten
vergessen, weil sie nicht in derselben Liste landen wie die vom Tag."

**`prueffrage`** fragt nach Verhalten, nicht nach Meinung. Nicht „Geht dabei
etwas verloren?", sondern „Wenn abends um acht eine Anfrage reinkommt — wo
landet die?" Beide möglichen Antworten müssen für die Diagnose brauchbar sein.

**`kleinster_schritt`** muss ohne Software, ohne Anschaffung und ohne
Umgewöhnung machbar sein und dem Betrieb auch dann nützen, wenn er nie etwas
weiteres unternimmt.

**`gilt_bei.reifegrad_min`** verwendet: 0 = nur Papier, 1 = einzelne digitale
Werkzeuge ohne Verbindung, 2 = mehrere digitale Kanäle, manuell verbunden,
3 = teilweise strukturierte Systeme, 4 = integriert, 5 = durchgängig automatisiert.
Der Schwerpunkt dieser Recherche liegt bei 2 und 3.

**Belege.** Jedes Muster braucht mindestens eine überprüfbare Quelle. Wenn ein
Muster fachlich abgeleitet und nicht direkt belegt ist, setze
`"content_origin": "expert_derived"` und `"source_strength": "low"` — das ist
zulässig, muss aber sichtbar sein.

### Problemfamilien zur Zuordnung

```
PF-01  Verteilte Vorgangsinformationen
PF-02  Unzuverlässige Anfrageerfassung
PF-03  Mehrfachübertragung derselben Daten
PF-04  Unsichtbarer Status und offene Schritte
PF-05  Fehlende Objekt- und Ortszuordnung
PF-06  Termin- und Kapazitätskonflikte
PF-07  Ungeklärte Änderungen und Freigaben
PF-08  Lücke zwischen Außendienst und Rechnung
PF-09  Unklarer Zahlungs- und Belegstatus
PF-10  Fehlende Material- und Produktionssicht
PF-11  Abhängigkeit von einer Person
PF-12  Unstrukturierte Dokumente und freie Texte
```

### Lösungsmuster zur Zuordnung

```
SP-01  Gemeinsamer Anfrageeingang mit Missing-Info-Prüfung
SP-02  Einfache Vorgangsakte mit Status und nächstem Schritt
SP-03  Mobile Einsatzdokumentation aus Sprache, Fotos und Bon
SP-04  Objekt-ID und echter Ablageort
SP-05  Termin-Anfrage mit Kapazitätsprüfung
SP-06  Dokument-zu-Datensatz mit Unsicherheitsprüfung
SP-07  Zusatzarbeit mit dokumentierter Freigabe
SP-08  Einfaches Material- und Produktionsboard
SP-09  Geprüfte Rechnungsgrundlage und Zahlungsnachverfolgung
SP-10  Übergabe- und Wissensnotiz im Vorgang
```

Bitte eine ausgewogene Verteilung. Die Schwerpunkte dieser Recherche liegen bei
`PF-02`, `PF-03`, `PF-04`, `PF-09`, `PF-11` und `PF-12`, weil dort die
bestehende Wissensbasis am dünnsten ist. `PF-05` bitte gar nicht bearbeiten.

## Datei 2 — `02_output_structures.jsonl`

Zehn Ergebnisstrukturen, eine je Lösungsmuster. Sie beschreiben, wie das
konkrete Arbeitsergebnis aussieht, das der Betrieb am Ende in der Hand hält.

```json
{
  "output_id": "OUT-03",
  "name": "Einsatznotiz",
  "solution_pattern_ids": ["SP-03"],
  "beschreibung": "Ein Satz, was das Dokument ist.",
  "felder": [
    {"label": "Tätigkeit", "beispielwert": "Dichtung Waschbecken getauscht", "pflicht": true},
    {"label": "Zeit", "beispielwert": "2,5 Std", "pflicht": true},
    {"label": "Material", "beispielwert": "Dichtungssatz 12,40 €", "pflicht": false}
  ],
  "typische_offene_punkte": [
    "Zusatzarbeit bestätigen",
    "Arbeitszeit fehlt noch"
  ],
  "anhaenge": ["Foto", "Bon"],
  "menschliche_pruefung": "Du prüfst Zuordnung, Zeit und Material und gibst frei.",
  "source_url": "https://…",
  "content_origin": "expert_derived"
}
```

Die `beispielwert`-Angaben sind Platzhalter, die zeigen, welche Art von Inhalt
in das Feld gehört. Sie werden im Betrieb durch echte Angaben ersetzt und
dürfen nie als Tatsache über einen konkreten Betrieb erscheinen.

Orientiere dich für die Feldlisten an dem, was in der jeweiligen Branche
tatsächlich für Angebot, Auftrag, Termin, Rechnung oder Übergabe gebraucht wird.
Belege, wo möglich, mit Quellen zu üblichen Formularen und Pflichtangaben.

## Verbindliche Ausschlüsse

- Keine erfundenen Zeit- oder Geldersparnisse. Keine Prozentangaben zu
  Effizienzgewinnen. Keine Anbieterversprechen.
- Keine konkreten Produkt- oder Toolnamen in den Mustern. Die Muster müssen
  gültig bleiben, wenn sich der Markt ändert.
- Keine Empfehlung, die eine Voraussetzung stillschweigend annimmt. Wenn ein
  Muster eine Grundlage braucht, gehört sie in `kleinster_schritt`.
- Keine personenbezogenen Daten aus Quellen. Fälle anonymisiert wiedergeben.
- Keine Aussage, die eine autonome Entscheidung über Preis, Vertrag, Zahlung,
  Qualität, Personal oder Herausgabe durch KI nahelegt.

## Lieferformat

Zwei JSONL-Dateien wie oben beschrieben, dazu:

- `03_source_register.csv` mit Spalten `source_id, url, typ, abgerufen_am, verwendet_in`
- `README.md` mit Umfang, Methodik, Einschränkungen und offenen Lücken

Deutsch. Ein JSON-Objekt pro Zeile, kein umschließendes Array, keine Kommentare.
