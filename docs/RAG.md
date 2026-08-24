# Abruf (RAG)

## Was der Abruf hier ist — und was nicht

Er **rankt**, er **begrenzt nicht**. Welche Lösungen empfohlen werden dürfen,
entscheidet die Freigabeliste (siehe [`SOLUTION_CATALOG.md`](SOLUTION_CATALOG.md)).
Der Abruf sagt nur, welche davon zur Diagnose am ehesten passen.

Das war nicht immer so. In einer früheren Fassung bestimmte der Abruf die
wählbare Menge — und ein schlechter Treffer machte die richtige Familie
unerreichbar. Gemessen: Ein Zweipersonen-Malerbetrieb und eine Verwaltung mit
450 Einheiten bekamen **dieselben vier Familien**, weil beide über dasselbe
generische Diagnosemuster einstiegen.

---

## Der Wissensgraph

Gesucht wird nur oben; alles darunter hängt an Kanten, die im Bestand stehen:

```
Diagnose
   │  semantische Suche
   ├──→ Betriebsart      BP-A … BP-G
   └──→ Diagnosemuster   DP-01 … DP-18
              │  nachgeschlagen über Kennungen
              └──→ passende_loesungsfamilien → SF-*
                          └──→ braucht_capabilities → CAP-*
                                      └──→ Zielbild mit grösster Überdeckung → TA-*
```

Nur zwei Typen werden gesucht. Alles andere wird **nachgeschlagen**. Das
verhindert Empfehlungen ohne diagnostischen Weg: Wer viele E-Mails hat, bekäme
sonst irgendwann Marketing-Automation vorgeschlagen, weil das semantisch in die
Nähe rückt — obwohl kein Diagnosemuster dorthin führt.

Familien werden **reihum** eingesammelt, nicht der Reihe nach: erst die erste
Familie jedes Musters, dann die zweite. Vorher füllte das erstplatzierte Muster
alle Plätze allein, und die anderen beiden trugen nichts bei.

---

## Absatzweise Suche

Eine Erzählung von dreitausend Wörtern als **ein** Vektor ist ein Mittelwert
über Personal, Kanäle, Software, Fristen und Rechnungen — und ein Mittelwert
liegt ungefähr gleich weit von allem entfernt. Gemessen: 0,8 Prozent Abstand
zwischen der ersten und der zweiten Betriebsart.

Deshalb wird die Erzählung an Leerzeilen geteilt, zu lange Blöcke zusätzlich an
Satzgrenzen. Jeder Absatz wird einzeln eingebettet — alle in **einem**
API-Aufruf — und die Trefferlisten werden zusammengeführt: Je Absatz und
Wissenstyp bekommen die ersten drei Plätze Punkte. Ein Muster, das in drei
Absätzen zweiter wird, schlägt eines, das in einem Absatz knapp führt.

Gesucht wird mit dem **Engpass-Satz aus Aufruf 1**, nicht mit der rohen
Erzählung. Der Satz ist eine Diagnose und trifft damit die Sprache, in der die
Muster geschrieben sind. Gemessen spreizt er die Trefferliste mehr als doppelt
so weit.

---

## Der Index

```bash
python scripts/build_index.py --target architecture
```

Baut `data/solution_architecture_index/` aus `knowledge/candidates/batch_10/`.
Modell: `text-embedding-3-small` — dasselbe wie beim Suchen, sonst passen die
Vektoren nicht zusammen.

**Der Index liegt nicht im Repository.** Er ist ein Artefakt, reproduzierbar
aus den Wissensdateien, und kostet ein paar Einbettungen. Fehlt er, liefert der
Abruf leere Listen und die Anwendung läuft weiter — die Auswahl arbeitet dann
allein auf dem Katalog.

Vor dem Bauen lohnt sich:

```bash
python scripts/pruefe_batch10.py
```

Das prüft Pflichtfelder, doppelte Kennungen, Verweise ins Leere — und ob ein
Wissensabschnitt aus einem Evaluationsfall abgeschrieben wurde. Fünf gleiche
Wörter hintereinander sind ein Fehler: Wissen, das aus einem Messfall stammt,
findet genau diesen Fall wieder und macht jede spätere Messung wertlos.

---

## Grenzen, offen benannt

- **Die Betriebsart trennt schwach.** Zwischen Platz eins und zwei liegen
  teilweise 0,8 Prozent. Genommen wird genau eine.
- **Generische Diagnosemuster gewinnen.** DP-06 („Rückfrageschleifen") stand
  bei sehr verschiedenen Betrieben auf Platz eins.
- **Ein abgerufener Abschnitt ist nie ein Beleg über den Kunden.** Aussagen
  über den Betrieb stammen ausschließlich aus seiner Erzählung; der Prompt sagt
  das, und die Zitatprüfung erzwingt es.
- **Übernahmen kommen vor.** In einer Messung hat das Modell einen Satz aus
  einem abgerufenen Abschnitt wörtlich in den Kundentext übernommen. Deshalb
  prüft `scripts/messlauf.py` genau darauf.
