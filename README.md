# AI Start Map

Ein Diagnosewerkzeug für kleine Betriebe. Jemand erzählt in eigenen Worten,
wie sein Arbeitsalltag abläuft — das System versteht den Ablauf, benennt den
Engpass und empfiehlt eine Ziellösung, **die ausschließlich aus einem
freigegebenen Lösungskatalog stammt**.

Zielgruppe sind Betriebe mit einer bis zehn Personen, die bereits digital
arbeiten, aber nichts automatisiert haben: Malerbetrieb, Hausverwaltung,
Kfz-Werkstatt, Fotografin, Salon.

---

## Das Problem, das dieses Projekt löst

Ein Sprachmodell, das nach einer Erzählung eine Lösung vorschlägt, erfindet
gern Software, die es nicht gibt — und die niemand bauen kann. Für ein
Beratungsprodukt ist das unbrauchbar: Was empfohlen wird, muss lieferbar sein.

**AI Start Map trennt deshalb Diagnose und Lösung.**

Das Modell darf frei diagnostizieren und frei formulieren. Es darf **nicht**
frei entscheiden, was angeboten wird. Es wählt Kennungen aus einem Katalog,
und der Server prüft jede einzelne, bevor irgendetwas beim Kunden landet.

---

## Der Datenfluss

```
Erzählung des Betriebs
        │
        ├─ Aufruf 1 · Diagnose            Engpass, wörtliche Belege, heutiger Ablauf
        │                                 keine Lösung, kein Produktname
        │
        ├─ Abruf (RAG)                    FAISS über 70 Wissensabschnitte
        │                                 rankt passende Lösungsfamilien — nur ein Vorschlag
        │
        ├─ Aufruf 2 · Auswahl             Modell sieht ALLE freigegebenen Familien
        │      ↓                          und antwortet mit SF-Kennungen + Bausteinen
        │   SERVERPRÜFUNG                 jede Kennung gegen die Freigabeliste
        │      ↓                          jedes Modul gegen die Bausteine seiner Familie
        │   Katalogdaten laden            volle Datensätze, Capabilities, Zielbildmuster
        │
        ├─ Aufruf 3 · Ansichten           Beispieloberflächen
        ├─ Aufruf 4 · Rest                Aufgabenteilung, Wert, Systeme, Umsetzung
        │
        └─ Ergebnisseite + PDF
```

Die PDF-Auswertung wird serverseitig aus demselben `ResultDTO` wie die
Ergebnisseite erzeugt. Eine eigene A4-Vorlage (`app/templates/results_pdf.html`
mit `app/static/results-pdf.css`) hält die mintfarbene Titelseite,
zusammengehörige Karten und den fortlaufenden Seitenfluss stabil.

Details in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

Die gemeinsame visuelle und inhaltliche Foundation für Landingpage,
Betriebsbeschreibung, Analysezustände und Verständnisbestätigung ist in
[`docs/PRE_RESULTS_UI_FOUNDATION.md`](docs/PRE_RESULTS_UI_FOUNDATION.md)
dokumentiert.

---

## Das Geländer

Jedes Modul, das der Kunde sieht, ist intern auf den Katalog zurückgeführt:

```json
{
  "name": "Ihr Eingang für Telefon und WhatsApp",
  "beschreibung": "Anrufe, Nachrichten und E-Mails landen an einer Stelle …",
  "solution_family_ids": ["SF-01"],
  "baustein_refs": ["gemeinsamer Eingang"]
}
```

Der Kunde sieht nur Name und Beschreibung. Die Kennungen bleiben innen und
machen jede Empfehlung nachvollziehbar.

Ein Modul namens „Autonomer KI-Einkaufsagent" mit `SF-01` danebengesetzt wird
**abgewiesen**, weil kein Baustein von SF-01 das beschreibt. Wie das genau
funktioniert, steht in [`docs/SOLUTION_CATALOG.md`](docs/SOLUTION_CATALOG.md).

---

## Technik

| | |
|---|---|
| Web | FastAPI, Jinja2, serverseitig gerendert, kein Frontend-Framework |
| Datenbank | PostgreSQL, SQLAlchemy 2.x, Alembic |
| Modell | OpenAI Structured Outputs (`chat.completions.parse`), `gpt-5-mini` |
| Vertrag | Pydantic v2 — jede Modellantwort läuft durch prüfende Validatoren |
| Abruf | FAISS, `text-embedding-3-small`, absatzweise Suche |
| Tests | pytest, umfangreiche Offline-Suite ohne einen einzigen echten Modellaufruf |

---

## Lokal starten

```bash
python -m venv .venv
.venv/Scripts/activate          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env            # DATABASE_URL und OPENAI_API_KEY eintragen
alembic upgrade head

python scripts/build_index.py --target architecture   # baut den FAISS-Index
uvicorn app.main:app --reload
```

Der Index liegt unter `data/` und ist **nicht** im Repository — er entsteht aus
den Wissensdateien und kostet ein paar Einbettungen. Ohne Index läuft die
Anwendung trotzdem: Der Abruf liefert dann nichts, und die Auswahl arbeitet
allein auf dem Katalog.

### Tests

```bash
pytest -q
```

Läuft ohne Netz und ohne API-Schlüssel. Was gemockt wird und welche
Evaluationen bewusst Geld kosten, steht in [`docs/TESTING.md`](docs/TESTING.md).

---

## Verzeichnisse

| | |
|---|---|
| `app/` | Anwendung, Vertrag, Prompts, Vorlagen |
| `app/solution_catalog.py` | die Katalogprüfung — das Geländer |
| `app/result_schema.py` | der Datenvertrag samt aller Prüfungen |
| `knowledge/` | Wissensbasis, Katalog, Freigabeliste, Evaluationsfälle |
| `scripts/` | Index bauen, Wissen prüfen, Evaluation fahren |
| `tests/` | die Offline-Testsuite |
| `docs/` | Architektur, Katalog, Abruf, Tests |

---

## Stand

Das Projekt ist in Entwicklung. Was gemessen ist und was nicht, steht offen in
[`docs/TESTING.md`](docs/TESTING.md) — einschließlich der Fehlerquote, die
noch nicht gelöst ist.
