# Anweisung: Endanalyse ersetzen

**Ein Problem. Keine anderen Änderungen.**

Die Musterauswahl funktioniert seit heute (Blumenladen wählt SP-01). Der
Interview- und Bestätigungsteil funktioniert — der erkannte Ist-Ablauf ist
inhaltlich gut. Kaputt ist **nur der Schritt danach**: die Erzeugung des
Kundentexts.

Heute wird der Text in einzelne Felder gefüllt (`short_reason`, `promise`,
`future_process`, `sample_output` mit festen Feldnamen) und danach durch Filter
geschickt. Ergebnis: abstrakte Sätze, Fachwörter, Widersprüche, und im
Beispielblock steht ein Datum im Feld „Wer kümmert sich".

Ersetze diesen einen Schritt.

---

## Was geändert wird

**`app/schemas.py`** — `FinalAnalysisResult` bekommt eine neue Struktur für den
Kundenteil. Die internen Felder (gewähltes Muster, Gates, Ist-Ablauf) bleiben
unverändert.

Neue Kundenfelder:

```
engpass                     Text, 2-3 Sätze
vorschlag_titel             Text, eine Zeile
vorschlag_erklaerung        Text, 2-3 Sätze
das_nimmt_die_ki_ab         Liste, 5-8 Einträge
beispiel_nachricht          Text, 2-4 Sätze
beispiel_kanal              Text, z.B. "WhatsApp"
beispiel_daraus_wird        Liste von {label, wert}
beispiel_das_fehlt          Liste, 1-3 Einträge
beispiel_rueckfrage         Text, ein Satz
dein_tag_danach             Text, 3-6 Sätze
das_bleibt_bei_dir          Text, 1-2 Sätze
erster_schritt              Text, ein Absatz
spaeter_moeglich            Liste, max 3
was_zuerst_fehlt            Liste, 0-3 (leer wenn nichts fehlt)
```

**`app/openai_service.py`** — `generate_final_analysis()` bekommt einen neuen
Systemprompt. Der vollständige Wortlaut steht in
`docs/prompts/endanalyse_system.md` (Datei neu anlegen, Inhalt siehe unten).

**`app/routes.py`** — die Payload-Erzeugung für die Ergebnisseite gibt die
neuen Felder direkt weiter. Die feste Ausgabestruktur aus
`output_structures.jsonl` wird für den Beispielblock **nicht mehr** verwendet.
`_customer_sample_output()` entfällt.

**`app/templates/results.html` und `report.html`** — rendern die neuen Felder.

---

## Der neue Systemprompt

Lege ihn als `docs/prompts/endanalyse_system.md` ab und lade ihn von dort.

Inhalt: Verwende die Datei, die Derya dir gibt
(`EXPERIMENT_FREIER_PROMPT.md`, Teil A zwischen `=== PROMPT ANFANG ===` und
`=== PROMPT ENDE ===`), mit drei Anpassungen:

1. Der Abschnitt „Meine zehn Lösungsmuster" wird nicht mehr vollständig
   mitgegeben. Stattdessen nur das **bereits ausgewählte** Muster mit seinen
   Feldern aus `recommendation_catalog.json`: `customer_title`, `user_action`,
   `ai_task`, `visible_output`, `human_check`, `smallest_entry`, `later_stage`,
   `counterexample`. Die Auswahl ist zu diesem Zeitpunkt schon getroffen.

2. Ergänze vor „Wie du schreibst" diesen Abschnitt:

```
## Woran du den Fall entlanggehst — das sieht niemand

Dies ist ein stummes Denkraster. Es wird NIEMALS ausgegeben, nie zitiert, nie
als Frage gestellt. Es hilft dir nur, die Stelle zu finden.

Geh die Erzählung entlang und prüfe:
Kommt etwas rein?
Muss daraus etwas gemacht werden?
Fehlt dabei regelmäßig etwas?
Muss jemand entscheiden?
Muss es irgendwo eingetragen werden?
Muss später jemand erinnert werden?

Wo mehrfach "ja" steht, liegt der Engpass.

## Drei Arten von Lösung

Unterscheide sichtbar:
- Was die KI übernimmt (etwas Unstrukturiertes verstehen: Sprache, freie
  Nachricht, Foto)
- Was normale Software macht (Nummer vergeben, Status setzen, rechnen,
  erinnern) — dafür braucht es keine KI
- Was der Betrieb zuerst selbst ordnen muss

Wenn der dritte Punkt der wichtigste ist, sag das deutlich und empfiehl
zunächst keine KI.
```

3. Am Ende, statt „welches Muster hast du gewählt": Die Ausgabe erfolgt als
   JSON nach dem Schema oben. Kein Fließtext mit Überschriften.

---

## Was NICHT geändert wird

- Klassifikation, Gates, Rangfolge, Musterauswahl — läuft
- Interview, Prozessauswahl, Bestätigung, Ist-Ablauf — läuft
- Fehlerverhalten bei API-Ausfall — bleibt wie heute
- Der Wortfilter bleibt, aber **nur als Prüfung**: bei einem Treffer wird
  einmal neu erzeugt, nicht ersetzt und nicht gelöscht

---

## Abnahmebedingung

Fertig ist es, wenn **alle drei** Fälle vollständig durchlaufen und die Ausgabe
diese Prüfung besteht:

**Blumenladen** (Originaltext aus `knowledge/evaluation/`)
- Muster SP-01
- „Das nimmt dir die KI ab" nennt Bestellangaben, die eine Floristin kennt
  (Farben, Anlass, Lieferadresse, Kartentext o.ä.)
- Die Beispielnachricht klingt wie eine echte Kundennachricht über WhatsApp,
  Instagram oder Mail
- Kein Fotoshooting, keine Schuhe, kein Regal

**Hausmeister** „Auftrag erfassen nach Einsatz vor Ort"
- Muster SP-03
- Sprache, Fotos und Bon kommen vor
- Kein Regal, kein Ablageort

**Fotograf**
- Muster SP-02
- Briefing, Änderungswünsche, Freigabe kommen vor
- Keine Blumen, keine Einsatznotiz

**Für alle drei:**
- Anrede durchgehend „du", nie „der Fotograf" oder „die Inhaberin"
- Keines dieser Wörter kommt vor: Vorgangsakte, Vorgangsübersicht,
  Vorgangsentwurf, Datensatz, Zieloutput, Zielschema, Felder extrahieren,
  Pflichtfelder, Anker, Autonomiestufe, Pilot, Rollout, strukturiert,
  deterministisch
- Kein Feld enthält einen Wert, der nicht zu seiner Beschriftung passt
  (heutiger Fehler: Datum im Feld „Wer kümmert sich")
- Keine Zahl, die nicht in der erfundenen Beispielnachricht steht oder aus ihr
  folgt
- Kein Satz behauptet eine Ersparnis oder Verbesserung ohne Grundlage
  („reduziert Suchzeit", „spart Zeit", „erhöht die Effizienz")
- „So klein fängst du an" ist ein vollständiger Satz mit Verb und beschreibt
  etwas, das man morgen früh tun kann

Wenn eine dieser Bedingungen nicht erfüllt ist: melden, nicht als fertig
ausgeben.

---

## Bericht

Vier Punkte, mehr nicht:

1. Geänderte Dateien
2. Der vollständige Kundentext für den Blumenladen
3. Welche Abnahmebedingungen nicht erfüllt sind
4. Testergebnis

---

# Anhang: Neues Katalogfeld `ai_capabilities`

Ergänze in `knowledge/runtime/recommendation_catalog.json` bei jedem Solution
Pattern ein Feld `ai_capabilities` mit den unten stehenden Einträgen.

**Zweck:** Der Abschnitt „Das nimmt dir die KI ab" ist heute vage, weil das
Modell nichts Konkretes zur Hand hat. Diese Liste ist der Wortschatz, aus dem
es schöpft.

**Wichtige Regel, die in den Systemprompt gehört:**

```
Unter "Das nimmt dir die KI ab" wählst du aus den Fähigkeiten des gewählten
Musters die fünf bis acht aus, die auf diesen Betrieb zutreffen.

Du schreibst sie NICHT ab. Du übersetzt sie in die Sprache und die Gegenstände
dieses Betriebs.

Falsch:  "ordnet Fotos der richtigen Anfrage zu"
Richtig: "das Foto vom Strauß, das die Kundin mitschickt, hängt an der
          richtigen Bestellung"

Fähigkeiten, die auf diesen Betrieb nicht zutreffen, lässt du weg. Lieber fünf
zutreffende als acht, von denen drei danebenliegen.
```

---

**SP-01 — Anfragen aus allen Kanälen sammeln**
- nimmt Nachrichten aus WhatsApp, Mail, Instagram, Formular und Shop entgegen
- wandelt eine Sprachnachricht in Text um
- erkennt, worum es dem Kunden überhaupt geht
- liest die wichtigen Angaben heraus: was, wann, wohin, wie viel
- hängt mitgeschickte Fotos und Dateien an die richtige Anfrage
- erkennt, ob die Anfrage zu einem bestehenden Kunden gehört
- führt mehrere Nachrichten zur selben Sache zusammen
- markiert, welche Angaben noch fehlen
- bereitet die passende Rückfrage vor
- erkennt, dass eine Anfrage noch unbeantwortet ist
- sortiert nach Art des Anliegens
- fasst die Anfrage in zwei Zeilen zusammen

**SP-02 — Übersicht mit Status und nächstem Schritt**
- ordnet neue Nachrichten dem laufenden Vorgang zu
- fasst zusammen, was seit dem letzten Mal passiert ist
- erkennt den nächsten offenen Schritt
- markiert, wo etwas gerade hängt
- erkennt, dass etwas liegen geblieben ist
- zeigt, worauf der Kunde noch wartet
- hebt hervor, was sich zuletzt geändert hat
- bereitet eine Zwischenmeldung an den Kunden vor
- stellt die Tagesliste zusammen: heute fällig, unvollständig, neu

**SP-03 — Mobile Einsatzdokumentation**
- wandelt die Sprachnachricht nach dem Einsatz in Text um
- liest den Bon: Lieferant, Datum, Betrag, Positionen
- ordnet Fotos dem richtigen Einsatz zu
- erkennt Tätigkeit, Dauer und verwendetes Material
- erkennt zusätzlich ausgeführte Arbeiten
- erkennt festgestellte, aber nicht erledigte Sachen
- markiert unsichere oder fehlende Angaben
- erstellt die Einsatznotiz als Entwurf
- bereitet eine Rückfrage ans Büro oder an den Kunden vor
- bereitet aus bestätigten Notizen später den Rechnungsentwurf vor

**SP-04 — Gegenstand und Ablageort**
- liest aus der Annahme heraus, was gemacht werden soll
- hält den Zustand bei Annahme mit Fotos fest
- verbindet Auftragsnummer, Kunde und Gegenstand
- zeigt, was zu diesem Gegenstand vereinbart wurde
- erkennt Gegenstände, die ungewöhnlich lange liegen
- bereitet die Fertigmeldung an den Kunden vor

Ausdrücklich NICHT: den Ablageort erraten oder aus Notizen ableiten. Der Ort
wird beim Weglegen erfasst, sonst gar nicht.

**SP-05 — Terminanfragen**
- liest den Terminwunsch aus der Nachricht
- erkennt, welche Leistung gewünscht ist und wie lange sie dauert
- markiert fehlende Angaben
- bereitet Terminvorschläge aus vorhandenen freien Zeiten vor
- bereitet Bestätigung und Erinnerung vor
- nimmt Verschiebung und Absage auf
- erkennt Doppelbelegung

**SP-06 — Angaben aus Dokumenten lesen**
- liest Rechnungen, Bons, Lieferscheine und Formulare
- erkennt Lieferant, Datum, Betrag, Nummer und Positionen
- ordnet das Dokument dem richtigen Auftrag oder Kunden zu
- benennt die Datei und legt sie ab
- markiert unsichere Stellen und Widersprüche
- zeigt die gelesenen Angaben neben dem Original
- erkennt, dass ein Beleg fehlt
- fasst Angaben aus mehreren Unterlagen zusammen

**SP-07 — Änderungen und Zusagen festhalten**
- erkennt, dass sich am Auftrag etwas geändert hat
- hält fest, was zugesagt wurde und von wem
- führt nach, welche Fassung gerade gilt
- markiert offene Freigaben
- bereitet die Rückfrage zur Änderung vor
- bereitet den aktualisierten Auftrag vor

**SP-08 — Material und Arbeitsstand**
- erkennt, welches Material für einen Auftrag gebraucht wird
- erkennt niedrigen Bestand
- stellt die Einkaufsliste zusammen
- ordnet Lieferungen der Bestellung zu
- erkennt fehlende oder verspätete Lieferungen
- hält Verbrauch fest
- markiert Aufträge, die auf Material warten

**SP-09 — Rechnungen und Zahlungen**
- sammelt bestätigte Leistungen zu einem Auftrag
- übernimmt Material und Zeiten aus dem Auftrag
- bereitet den Rechnungsentwurf vor
- ordnet Belege der richtigen Rechnung zu
- erkennt überfällige Rechnungen
- bereitet die Zahlungserinnerung im passenden Ton vor
- erkennt Angebote, auf die niemand geantwortet hat
- sammelt die Unterlagen für die Buchhaltung

**SP-10 — Wissen und Übergaben**
- macht aus einer kurzen Notiz eine Übergabe
- fasst zusammen, was entschieden wurde
- hält fest, was offen ist und wer übernimmt
- findet frühere Absprachen zu diesem Kunden
- beantwortet wiederkehrende Fragen aus vorhandenen Unterlagen

---

**Gemeinsam für alle Muster — das macht normale Software, nicht die KI.**
Ergänze das als eigenes Feld `software_not_ai` einmal im Katalog, nicht pro
Muster:

- eine Auftrags- oder Objektnummer vergeben
- den Status umschalten, wenn etwas passiert ist
- Preise, Mengen und Summen rechnen
- Fälligkeiten und Erinnerungen auslösen
- eine Nachricht in den richtigen Ordner legen
- Zugriffsrechte regeln
- festhalten, wo ein Gegenstand physisch liegt

Wenn der Engpass des Betriebs hier liegt, gehört das ins Ergebnis — mit dem
Hinweis, dass dafür keine KI nötig ist.
