# Anweisung an Claude Code

Lies diese Datei zuerst. Sie sagt dir, was zu tun ist und in welcher
Reihenfolge.

---

## 1. Deine Unterlagen

Alle im Ordner `docs/auftrag/`:

| Datei | Wofür |
|---|---|
| `PROJEKT_UEBERGABE.md` | Was das Projekt ist, wo was liegt, was funktioniert, was kaputt ist. **Zuerst lesen.** |
| `ANWEISUNG_ENDANALYSE.md` | Die konkrete Aufgabe. Enthält im Anhang das neue Katalogfeld `ai_capabilities`. |
| `EXPERIMENT_FREIER_PROMPT.md` | Der Wortlaut des neuen Systemprompts, Teil A zwischen den Markierungen. |
| `TESTFAELLE_ZIELGRUPPE.md` | Sieben Betriebe aus der Zielgruppe mit erwartetem Ergebnis. Damit prüfst du. |

Reihenfolge: Übergabe → Anweisung → Prompt-Wortlaut → Testfälle.

---

## 2. Git — verbindlich

### Schritt A: `main` aufholen

`main` steht auf dem Stand vom 17. Juli, `feature/gate-cascade-quality` ist 35
Commits weiter. Geprüft: `main` ist direkter Vorfahre, der Merge ist ein reines
Vorspulen ohne Konfliktmöglichkeit.

Führ das als Erstes aus:

```
git status                                    # muss sauber sein
git checkout feature/gate-cascade-quality
.venv/Scripts/python.exe -m pytest -q         # muss grün sein
git checkout main
git merge feature/gate-cascade-quality
git push origin main
```

Wenn `git status` nicht sauber ist oder Tests fehlschlagen: **stoppen und
melden**, nicht mergen.

Die Branches `agent/complete-diagnostic-architecture` und
`feature/recommendation-experience` enthalten nichts, was nicht schon in
`feature/gate-cascade-quality` steckt. Sie werden nicht gemergt. Löschen ist
optional und nicht Teil dieses Auftrags.

### Schritt B: neuer Arbeitsbranch

Nachdem `main` aktuell ist, zweigt die neue Arbeit **von `main`** ab:

```
git checkout main
git checkout -b feature/customer-output
git push -u origin feature/customer-output
```

Ab hier läuft die gesamte Arbeit dieses Auftrags auf
`feature/customer-output`.

### Schritt C: committen während der Arbeit

**Du darfst committen und pushen.** Vor jedem Commit prüfen:

```
git branch --show-current
```

Erwartet: `feature/customer-output`

Wenn dort etwas anderes steht: **nicht committen**, sondern melden.

**Autor und Committer sind immer Derya.** Niemals Claude, niemals
Co-Authored-By, niemals ein Hinweis auf ein KI-Werkzeug in der
Commit-Nachricht. Die vorhandene Identität im Repo ist:

```
Derya <deryaxsarikaya@gmail.com>
```

Prüf vor dem ersten Commit mit `git config user.name` und
`git config user.email`, dass genau das gesetzt ist. Wenn nicht, setz es lokal
für dieses Repository.

### Schritt D: Abschluss eines Branches

Ein Arbeitsbranch wird nach `main` gemergt, **wenn drei Bedingungen erfüllt
sind**:

1. Alle Tests grün
2. Alle Abnahmebedingungen des Auftrags erfüllt
3. **Derya hat das Ergebnis gesehen und ausdrücklich freigegeben**

Punkt 3 ist keine Formalie. Merge nie von dir aus nach `main`, nur weil die
Tests grün sind. Melde stattdessen: „fertig aus meiner Sicht, Abnahme steht
aus."

Nach der Freigabe:

```
git checkout main
git merge feature/customer-output
git push origin main
git branch -d feature/customer-output
git push origin --delete feature/customer-output
```

Wenn die Arbeit auf einem Branch verworfen wird, wird er **nicht** gemergt,
sondern gelöscht. `main` bleibt sauber.

### Niemals

- Git-Historie verändern, rebasen, Commits umschreiben
- bestehende Änderungen verwerfen oder stashen
- committen: `.env`, Datenbanken, produktive FAISS-Dateien unter `data/`,
  Evaluationsartefakte wie `eval_llm_batch09.json`
- nach `main` mergen ohne Freigabe (siehe Schritt D)

---

## 3. Umgebung

Tests laufen nur über das venv:

```
.venv/Scripts/python.exe -m pytest -q
```

Das blanke `python` hat kein pytest. Aktuell: 214 Tests grün.

---

## 4. Die Aufgabe in einem Absatz

Die Musterauswahl funktioniert seit `a811726` — der Blumenladen bekommt SP-01,
der Hausmeister SP-03. Kaputt ist nur der Schritt danach: die Erzeugung des
Kundentexts. Er entsteht heute, indem das Modell Felder befüllt, die danach in
eine feste Struktur umgeschrieben werden. Dabei landen Werte unter falschen
Beschriftungen und fehlende Felder werden aus Katalogbeispielen gefüllt — so
kam ein Fotografen-Beispiel in eine Blumenladen-Auswertung.

Der Umschreibe-Block in `app/openai_service.py` ab Zeile 598 **entfällt
ersatzlos**. Nicht verbessern, nicht die Positionszuordnung reparieren. Die
Felder, die das Modell schreibt, gehen direkt durch.

Details in `ANWEISUNG_ENDANALYSE.md`.

---

## 5. Was du nicht anfasst

- Klassifikation, Gates, Rangfolge, Musterauswahl — funktioniert
- Interview, Prozessauswahl, Bestätigung, Ist-Ablauf — funktioniert
- Der Umbau von `routes.py` in Services und Repository. Das ist eine bekannte,
  eigene Aufgabe für später. **Nicht jetzt anfangen.**
- Die PDF-Kopfzeilen mit `127.0.0.1`. Das sind Browser-Kopfzeilen, per
  `@media print` nicht abschaltbar. Nicht erneut versuchen.

---

## 6. Zwei Regeln aus schmerzhafter Erfahrung

**Keine fallbezogene Hartkodierung.** Es gab einen Block
`if solution_id == "SP-03":` mit vierzig Zeilen fest verdrahtetem Kundentext.
Ergebnis: ein Fall sah gut aus, alle anderen schlecht. Er ist entfernt. Es darf
kein neuer entstehen — für kein Muster, in keiner Datei.

**Keine ungeprüften Erfolgsmeldungen.** Ein früherer Bericht meldete
„Localhost-URL verschwunden", obwohl sie nachweislich noch im PDF stand. Wenn
eine Abnahmebedingung nicht erfüllt ist, schreib das hin. Ein offener Punkt ist
harmlos, eine falsche Erfolgsmeldung kostet einen ganzen Durchgang.

---

## 7. Ablauf

1. Die vier Unterlagen lesen
2. `main` aufholen (Schritt A)
3. Branch `feature/customer-output` anlegen und pushen (Schritt B)
4. Umsetzen nach `ANWEISUNG_ENDANALYSE.md`
5. Tests laufen lassen
6. Die Abnahmebedingungen prüfen — mit den Fällen aus
   `TESTFAELLE_ZIELGRUPPE.md`, mindestens Blumenladen, Fotograf und
   Handwerksbetrieb
7. Branch prüfen, committen, pushen
8. Bericht — und auf Deryas Abnahme warten. **Nicht selbst nach `main`
   mergen.**

**Commit-Nachricht:**

```
Generate customer text from briefing instead of fixed fields
```

---

## 8. Bericht — fünf Punkte, mehr nicht

1. Geänderte Dateien
2. Der vollständige Kundentext für den Blumenladen
3. Welche Abnahmebedingungen **nicht** erfüllt sind
4. Testergebnis und Commit-Hash
5. Bestätigung: `main` wurde aufgeholt und steht jetzt auf welchem Commit;
   Arbeitsbranch war `feature/customer-output`; Autor war Derya; der
   Abschluss-Merge nach `main` steht noch aus und wartet auf Freigabe

Wenn du an einer Stelle nicht weiterkommst: melden und stoppen. Nicht raten,
nicht ersatzweise etwas anderes bauen.
