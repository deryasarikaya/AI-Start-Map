# Der Lösungskatalog — serverseitiges Grounding

## Warum

Ein Sprachmodell, das nach einer Erzählung eine Lösung vorschlägt, erfindet
Module. Sie klingen plausibel, sind manchmal sogar klug — und es gibt sie
nicht. Für ein Beratungsprodukt ist das der teuerste Fehler: Was empfohlen
wurde, muss geliefert werden.

**Abruf allein löst das nicht.** Wissen in den Prompt zu legen ist eine
Anregung, keine Grenze. Das Modell darf es lesen und schreibt trotzdem, was es
will. Die Grenze entsteht erst dadurch, dass das Modell **Kennungen** wählt und
der Server sie prüft.

---

## Die drei Ebenen

| | Datei | was es ist |
|---|---|---|
| **SF** Solution Family | `03_solution_families.jsonl` | was wir dem Betrieb bauen — 25 Familien |
| **CAP** Capability | `04_automation_capabilities.jsonl` | welche technische Fähigkeit es dafür braucht — 12 |
| **TA** Target Architecture | `05_target_architectures.jsonl` | wie mehrere Familien zu einem Ganzen werden — 9 |

Eine Capability ersetzt keine Familie und erzeugt keine. Ein Zielbild darf nur
Familien enthalten, die es gibt.

Jede Familie führt ihre **Bausteine** — die einzelnen Funktionen, aus denen sie
besteht:

```json
{
  "chunk_id": "SF-01",
  "familie_name": "Nachrichten- und Anfrageeingang",
  "worum_es_geht": "Eingehende Nachrichten werden gelesen und zugeordnet …",
  "geeignet_wenn": ["…"],
  "nicht_geeignet_wenn": ["…"],
  "bausteine": [
    "gemeinsamer Eingang",
    "Erkennung von Anliegen und Grunddaten",
    "Anhang- und Fotozuordnung",
    "Zuständigkeitsvorschlag",
    "Übergabe an Vorgang oder Fachsystem"
  ],
  "braucht_capabilities": ["CAP-01", "CAP-02", "…"]
}
```

---

## Die Freigabeliste

`knowledge/catalog/FREIGABE.json` entscheidet, was empfohlen werden darf:

```json
{
  "erlaubt": ["SF-01", "SF-02", "…", "SF-25"]
}
```

**Bestand und Erlaubnis sind zwei Dinge.** Eine Familie kann in der JSONL-Datei
liegen, im FAISS-Index auftauchen, vom Abruf gefunden werden — und trotzdem
nicht empfehlbar sein, weil sie hier fehlt. Eine Familie abschalten ist eine
Zeile, kein Codeeingriff.

Fehlt die Datei, ist **nichts** erlaubt, nicht alles: `KatalogFehlt` bricht ab,
statt still durchzuwinken.

---

## Der Katalog ist kuratiert, nicht gesammelt

Die Liste entsteht nicht dadurch, dass jemand Dateien in einen Ordner legt.
Jede Familie ist eine Entscheidung darüber, was AI Start Map umsetzen oder
integrieren kann — das schließt ein: ein vorhandenes System konfigurieren,
Systeme verbinden, eine digitale Aussenschicht bauen, Abläufe automatisieren
oder eine eigene Komponente entwickeln.

Zwei Beispiele, wie kuratiert wird:

- **SF-25 Wirtschaftlichkeits- und Liquiditätsvorschau** wurde aufgenommen,
  weil keine der übrigen Familien beantwortet, ob ein Zeitraum trägt. Sie
  zeigt Zahlen aus vorhandenen Daten — Preise, Löhne und Zahlungen
  entscheidet ein Mensch, und die Rechnungen kommen aus strukturierten
  Daten statt aus einer Schätzung des Modells.
- **Personalgewinnung und Rückmeldungsauswertung** wurden **nicht** eigene
  Familien. Sie sind Bausteine geworden: Recruiting in SF-21, das Auswerten
  von Rückmeldungen in SF-13. Wo etwas fachlich zu einer bestehenden Familie
  gehört, wächst diese Familie, statt dass der Katalog länger wird.

## Der Ablauf

### 1 · Das Modell sieht den ganzen erlaubten Katalog

```python
solution_catalog.zur_auswahl(vorgeschlagen)
```

Alle 25 Familien mit `id`, `name`, `worum_es_geht`, `geeignet_wenn`,
`nicht_geeignet_wenn` und ihren Bausteinen — dazu die Markierung, welche der
Abruf für passend hält.

**Der Abruf beschneidet die Auswahl nicht.** Ein schlechter Treffer soll nicht
verhindern, dass die richtige Familie überhaupt wählbar ist. Er rankt, er
entscheidet nicht.

### 2 · Structured Output

```json
{
  "catalog_fit": true,
  "recommend_new_technology": true,
  "begruendung": "…",
  "selected_solution_family_ids": ["SF-01", "SF-02", "SF-09"],
  "loesungsname": "Zentrale Vorgangsstelle",
  "module": [
    {
      "name": "Ihr Eingang für Telefon und WhatsApp",
      "beschreibung": "…",
      "gruppe": "Eingang",
      "stufe": "jetzt",
      "solution_family_ids": ["SF-01"],
      "baustein_refs": ["gemeinsamer Eingang"]
    }
  ]
}
```

### 3 · Die Prüfung

In `Zielarchitektur.every_module_comes_from_the_catalogue`, also im Vertrag —
**bevor** irgendetwas gespeichert oder gezeigt wird:

| Prüfung | Fehlerfall |
|---|---|
| Kennung existiert und ist freigegeben | „SF-99" oder eine gesperrte Familie |
| Modul nennt nur ausgewählte Familien | Modul zeigt auf SF-24, gewählt war SF-01 |
| Modul nennt einen Baustein **seiner** Familien | „Autonomer KI-Einkaufsagent" mit `SF-01` daneben |
| `catalog_fit: false` heißt leer | kein Katalogtreffer und trotzdem Module |
| `catalog_fit: true` heißt gewählt | Treffer behauptet, nichts ausgewählt |
| gewählte Familien heißt gebaute Module | Auswahl ohne ein einziges Modul |

**Keine Mindestmenge an Modulen.** Ein Fall, dem ein Modul hilft, bekommt
eines. Die Diagnose bestimmt die Größe der Lösung, nicht das Schema.

Ein Verstoß löst den zweiten Versuch aus. Danach entsteht kein Ergebnis.

### 4 · Erst dann die vollen Daten — im echten Pfad

```python
# app/services/analysis_service.py — geprueftes_loesungswissen()
solution_catalog.vollstaendig(kennungen)      # ganze Datensätze
solution_catalog.faehigkeiten_zu(kennungen)   # die gebrauchten CAPs
solution_catalog.zielbild_zu(kennungen)       # passendes TA-Muster
```

Diese drei laufen **nach** der Prüfung und **vor** der Formulierung. Das
Ergebnis geht als Kontext in Aufruf 3 und 4 — und enthält nur, was
gewählt wurde. Familien, die nicht gewählt wurden, sehen die späteren
Aufrufe nicht mehr; sie können also auch nicht mehr auftauchen.

**Das Zielbildmuster wird hier bestimmt, nicht vorher.** Käme es aus dem
Vorschlag des Abrufs, hinge es an einer Auswahl, die noch niemand
getroffen hat. Passt keines, bleibt es leer; erzwungen wird keines.

---

## Die Sprache bleibt frei

Gebunden ist die **Funktion**, nicht das Wort. Aus dem Baustein „gemeinsamer
Eingang" darf werden:

> **Ihr Eingang für Telefon und WhatsApp**
> Anrufe, Nachrichten und E-Mails landen künftig an einer Stelle, mit Name,
> Adresse und Anliegen daneben.

Der Kunde sieht nie eine Kennung. Sie steht im gespeicherten Ergebnis und macht
jede Empfehlung nachvollziehbar.

---

## Das Geländer endet nicht bei den Modulen

Auch Ansichten, Systeme, Architekturebenen und Umsetzungsschritte tragen
intern `module_refs` — den Namen des Moduls, aus dem sie folgen. Der Server
prüft, dass jeder Bezug zu einem bereits geprüften Modul gehört; was sich auf
nichts beruft, kommt nicht durch.

Damit kann keine Funktion nachträglich entstehen: Ohne diese Prüfung könnte
eine Ansicht etwas zeigen, das in keinem Modul steht — und der Kunde würde
glauben, es gäbe die Sache dahinter.

**Bei SF-25 kommt eine Zahlensperre dazu.** Die Familie sagt zu,
Deckungsbeitrag und Liquidität später aus den Daten des Betriebs zu rechnen.
Solange das nicht geschehen ist, darf im Ergebnis kein Eurobetrag stehen —
beschrieben werden darf die Rechnung, behauptet werden darf das Ergebnis
nicht.

## Wenn nichts passt

Das Modell wird nicht gezwungen, etwas zu wählen:

```json
{ "catalog_fit": false, "selected_solution_family_ids": [], "begruendung": "…" }
```

Und der Fall, der in der Praxis am häufigsten übersehen wird:

```json
{ "recommend_new_technology": false }
```

Wer bereits ein geeignetes Fachsystem hat und es nur unvollständig nutzt,
braucht kein zweites System. Dann heißt die Empfehlung „das Vorhandene
konsequent nutzen" — auch das ist eine Lösung aus dem Katalog.

---

## Was gemessen wird

Aus dieser Architektur folgt die zentrale Kennzahl:

**Anteil der ausgegebenen Module mit gültiger Katalogzuordnung — Sollwert
100 %.** Sie ist durch den Vertrag erzwungen, nicht durch Hoffnung: Ein Modul
ohne Zuordnung kann gar nicht entstehen.

Daneben: wie oft `catalog_fit` verneint wird, wie oft `recommend_new_technology`
verneint wird, und wie viele Familien je Fall gewählt werden — zu viele wären
eine Aufzählung statt einer Lösung.
