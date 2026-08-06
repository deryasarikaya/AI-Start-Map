# Zukunftsfeature: klickbarer Ergebnisprototyp

**Status:** Idee festgehalten, nicht geplant, nicht umgesetzt
**Erfasst:** 2026-08-06
**Voraussetzung:** Klassifikation und Ausgabestrukturen müssen stehen (siehe Abschnitt 7)

---

## 1. Die Idee in einem Satz

Am Ende der Diagnose sieht der Betrieb nicht nur eine Beschreibung seiner
künftigen Lösung, sondern ein **klickbares Miniaturbeispiel davon** — gefüllt
mit seinen eigenen Angaben, in seiner eigenen Sprache.

## 2. Was der Kunde erlebt

Ein Hausmeisterbetrieb hat fünf Minuten lang erzählt, wie sein Alltag abläuft.
Er bekommt sein Ergebnis, und darin ist kein Textblock, sondern eine Seite, auf
der er etwas tun kann:

Er sieht eine Einsatznotiz. Oben steht „Einsatz Müller, Lindenstraße 4". Darin
Tätigkeit, Zeit, Material, zwei Fotos, ein Bon. Ein Feld ist gelb markiert:
*„Der Kunde wollte spontan noch die Tür nachstellen — abrechnen?"* Darunter zwei
Knöpfe: **Freigeben** und **Korrigieren**.

Er klickt auf Korrigieren, ändert die Arbeitszeit von 2,5 auf 3 Stunden, klickt
auf Freigeben. Die Notiz wechselt auf „freigegeben", und darunter erscheint der
nächste Schritt: ein Rechnungsentwurf, der aus der freigegebenen Notiz entsteht.

Vielleicht sind es zwei oder drei solche Einsätze, die er durchklicken kann.
Mehr nicht. Nach dreißig Sekunden weiß er, was gemeint ist.

Bei einem Coach wäre dasselbe eine Anfragekarte mit Antwortentwurf. Bei einem
Blumenladen eine Bestellübersicht aus drei Kanälen. Gleiche Mechanik, anderes
Dokument.

## 3. Warum das wirkt

**Es ersetzt Vorstellungsvermögen durch Anschauung.** Deine Zielgruppe hat keine
Erfahrung mit KI-Projekten. „Strukturierte Einsatzdokumentation" ist für sie ein
leerer Begriff. Ein Dokument mit seinem Kundennamen darin ist es nicht.

**Es macht die menschliche Kontrolle erfahrbar.** Der Freigabeknopf ist keine
Zusicherung im Text, sondern eine Handlung. Er merkt körperlich, dass nichts
ohne ihn passiert. Das ist der stärkste Vertrauensbeweis, den das Produkt
liefern kann — und genau der Punkt, an dem sich AI Start Map von Anbietern
unterscheidet, die Autonomie versprechen.

**Es kostet ihn nichts.** Kein Konto, keine Anmeldung, keine Daten, keine
Entscheidung. Er klickt und geht wieder, wenn er will.

**Es ist der ehrlichste denkbare Verkauf.** Er sieht vor dem ersten Euro genau
das, was er bekommen würde.

## 4. Was es ausdrücklich nicht ist

Die Abgrenzung ist der wichtigste Teil dieses Dokuments, weil die naheliegende
Fehlinterpretation viel teurer wäre.

**Es ist kein Agent, der live Software baut.** Keine Codegenerierung zur
Laufzeit, keine erzeugten Integrationen, kein „die KI stellt dir dein System
hin". Drei Gründe:

1. **Authentifizierung.** Jeder echte Anschluss — sein WhatsApp, sein Postfach,
   seine Buchhaltung — braucht eine Anmeldung bei einem Drittdienst. Das mitten
   in einer anonymen Diagnose zu verlangen, funktioniert weder rechtlich noch
   praktisch. Ohne Impressum und Datenschutzerklärung ist es ohnehin
   ausgeschlossen.
2. **Unvorhersehbarkeit.** Live erzeugter Code kann brechen. Ein hakendes Demo
   ist schlimmer als gar keines, besonders bei einer Zielgruppe, die schon
   einmal enttäuscht wurde. Das gesamte Produktversprechen beruht darauf, dass
   nichts behauptet wird, was nicht trägt.
3. **Umfang.** Das wäre ein eigenes Produkt, kein Feature. Es gehört nicht in
   ein Abschlussprojekt und auch nicht in die erste Ausbaustufe danach.

**Es ist auch kein funktionsfähiges Werkzeug.** Der Prototyp verarbeitet keine
echten Daten, speichert nichts, verschickt nichts. Er ist eine Vorschau, und er
sagt das auch: *„Vorschau — die endgültigen Angaben prüfst du selbst."*

## 5. Wie es technisch funktioniert

Der entscheidende Entwurfsgedanke: **Der Prototyp wird deterministisch aus einer
bereits strukturierten Ausgabe gerendert.** Es entsteht kein neuer KI-Schritt.
Deshalb kann er nicht halluzinieren, nicht abstürzen und ist normal testbar.

### Datenfluss

```
Erzählung
   ↓
Klassifikation          → Problemfamilie, Gates
   ↓
Auswahl (Katalog)       → Solution Pattern, z. B. SP-03
   ↓
Ausgabestruktur         → OUT-03 "Einsatznotiz": welche Felder existieren
   ↓
Finale Analyse (LLM)    → füllt die Felder mit SEINEN Angaben
   ↓
Jinja2-Template         → rendert die klickbare Seite
```

Die ersten vier Stufen existieren bereits oder sind eingeplant. Nur die letzte
ist neu.

### Woher die Struktur kommt

`knowledge/active/` liefert je Lösungsmuster die Feldliste. Aus dem
Rechercheauftrag Batch 09, Datei `02_output_structures.jsonl`:

```json
{
  "output_id": "OUT-03",
  "name": "Einsatznotiz",
  "solution_pattern_ids": ["SP-03"],
  "felder": [
    {"label": "Tätigkeit", "beispielwert": "…", "pflicht": true},
    {"label": "Zeit", "beispielwert": "…", "pflicht": true}
  ],
  "typische_offene_punkte": ["Zusatzarbeit bestätigen"],
  "anhaenge": ["Foto", "Bon"],
  "menschliche_pruefung": "Du prüfst Zuordnung, Zeit und Material."
}
```

### Woher die Inhalte kommen

Das Schema in `app/schemas.py` hat das passende Feld bereits:

```python
class SampleOutput(StrictResultModel):
    title: str
    fields: list[SampleOutputField]      # label + value
    open_items: list[str]
    attachments: list[str]
    preview_notice: str
```

Heute erfindet das Modell die Feldnamen frei. Künftig bekommt es die Feldliste
aus `OUT-xx` vorgegeben und füllt nur die Werte — aus den Angaben des Nutzers.
Das ist derselbe Wechsel wie bei der Klassifikation: Struktur deterministisch,
Inhalt vom Modell.

### Was neu gebaut wird

Genau drei Dinge:

1. **`app/templates/prototype.html`** — ein Jinja2-Template, das aus
   `sample_output` eine Karte rendert: Titel, Felder, markierte offene Punkte,
   Anhangsymbole, zwei Knöpfe.
2. **Etwa 40 Zeilen JavaScript** — Zustandswechsel „Entwurf → freigegeben",
   Felder editierbar machen, bei Freigabe die nächste Stufe einblenden. Kein
   Server-Aufruf, kein Speichern, alles im Browser.
3. **Eine Route** `GET /sessions/{id}/prototyp`, die das Template mit der
   gespeicherten Analyse füllt.

Kein neues Modell, keine neue Abhängigkeit, keine Datenbankmigration.

### Grenzen im Code

- Der Prototyp darf ausschließlich Werte anzeigen, die im Nutzertext oder in
  `sample_output` stehen. Keine Beispielwerte aus dem Katalog dürfen als seine
  Daten erscheinen — das wäre `FAIL-07` (RAG-Wissen wird zum Nutzerfakt).
- Fehlende Werte erscheinen als „noch offen", nie erfunden.
- Der Hinweis „Vorschau" bleibt sichtbar und ist nicht wegklickbar.
- Keine Zeit- oder Geldangabe, die nicht aus seiner Erzählung stammt.

## 6. Der zweite Nutzen: dieselben Daten sind das Lastenheft

Wenn er sagt „ja, das will ich", liegt bereits alles vor, was für den echten Bau
gebraucht wird — es muss nur anders gelesen werden:

| Feld aus der Diagnose | Bedeutung für den Bau |
|---|---|
| `OUT-xx.felder` | Datenmodell der Zielstruktur |
| `SP.input_channels` | welcher Kanal angebunden wird |
| `SP.deterministic_components` | was in Code gehört, nicht ins Modell |
| `SP.human_decisions` | wo ein Freigabeschritt eingebaut wird |
| `SP.stop_conditions` | Abbruchbedingungen im Betrieb |
| `SP.pilot` | Umfang des ersten Testlaufs |
| `autonomy_level_max` | wie weit automatisiert werden darf |
| `required_prerequisites` | was der Betrieb vorher herstellen muss |

Ein Datensatz, zwei Zwecke: Vorschau für ihn, Spezifikation für dich. Der Bau
selbst passiert danach mit deinen Werkzeugen — nicht in der Diagnose-App.

## 7. Voraussetzungen

Vorher muss stehen, sonst zeigt der Prototyp nur eine falsche Empfehlung
schöner:

1. Die Problemfamilienklassifikation liefert belastbare Ergebnisse. Solange die
   Trefferquote bei 28 Prozent liegt, ist jede Vorschau Zufall.
2. Batch 09 ist eingebaut, insbesondere `02_output_structures.jsonl` mit den
   Feldlisten je Lösungsmuster.
3. Das finale Modell erhält die Feldliste als Vorgabe statt sie zu erfinden.
4. Mindestens fünf reale Ergebnisse wurden fachlich geprüft.

## 8. Aufwand und Reihenfolge

| Schritt | Aufwand | Abhängigkeit |
|---|---|---|
| Feldlisten je Lösungsmuster verfügbar | Teil von Batch 09 | Recherche |
| `sample_output` an `OUT-xx` binden | ein halber Tag | Batch 09 eingebaut |
| Template und Route | ein Tag | vorheriger Schritt |
| Interaktion und Zustandswechsel | ein halber Tag | Template |
| Zweite Stufe (Rechnungsentwurf aus Freigabe) | ein halber Tag | optional |

Realistisch also zwei bis drei Tage, **nachdem** die Grundlagen stehen. Der
Prototyp ist dann fast ein Abfallprodukt der Ausgabestrukturen — nicht ein
eigenes Projekt.

## 9. Risiken

**Zu viel Funktion.** Die Versuchung, den Prototyp „richtig" zu machen, ist
groß. Zwei Knöpfe und ein Zustandswechsel reichen. Alles darüber hinaus erzeugt
die Erwartung eines fertigen Produkts, das nicht existiert.

**Falsche Erwartung beim Kunden.** Er könnte glauben, das sei bereits sein
System. Der Hinweis „Vorschau" muss sichtbar bleiben, und der nächste Schritt
muss ehrlich benannt werden.

**Datenschutz bei echten Inhalten.** Wenn Nutzer echte Kundennamen erzählen,
stehen die im Prototyp. Solange nichts gespeichert wird und die Sitzung endet,
ist das vertretbar — aber es muss geprüft werden, bevor der Prototyp in einen
Bericht oder eine E-Mail wandert.

**Ablenkung vom Kernproblem.** Dieses Feature ist attraktiv und macht Spaß. Es
darf nicht vor der Klassifikation gebaut werden. Ein schön dargestellter
falscher Vorschlag ist schlechter als ein schlicht dargestellter richtiger.

## 10. Offene Entscheidungen

- Ein Beispiel oder zwei bis drei zum Durchklicken?
- Erscheint der Prototyp auf der Ergebnisseite oder hinter einem eigenen Knopf?
- Wird er Teil des Druckberichts, oder bleibt er nur im Browser?
- Soll die zweite Stufe (Rechnungsentwurf aus freigegebener Notiz) sichtbar
  sein, oder überfrachtet das den Moment?

## 11. Für die Abschlusspräsentation

Das ist ein starker Schluss — aber nur in der richtigen Formulierung. Nicht:
„Meine App baut KI-Lösungen." Sondern: **„Meine App zeigt einem Betrieb sein
eigenes künftiges Arbeitsergebnis, bevor er einen Cent ausgibt — und lässt ihn
den Freigabeknopf selbst drücken."**
