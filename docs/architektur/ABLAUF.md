# Was passiert, wenn jemand AI Start Map benutzt

Geschrieben für jemanden, der keine Anwendung gebaut hat. Wo ein Fachwort nötig
ist, steht die Erklärung dabei.

---

## Die Geschichte einer Kundin

Stell dir eine Hausverwalterin vor, die auf die Seite kommt.

### 1. Sie klickt auf „Meinen Ablauf beschreiben"

Das Programm legt für sie einen **Vorgang** an — eine Zeile in der Datenbank,
an der ab jetzt alles hängt, was sie sagt. Diese Zeile bekommt eine Nummer.

Damit die Nummer nicht in der Adresszeile steht, wird sie in einem **Cookie**
gespeichert: ein kleiner Vermerk, den ihr Browser sich merkt und bei jedem
Klick mitschickt. Sie sieht `/interview`, das Programm weiß trotzdem, dass sie
Vorgang 17 ist.

*Im Code: `begin_journey` in `app/routes.py`*

### 2. Sie erzählt

Ein großes Textfeld. Sie kann tippen oder sprechen — der Browser schreibt das
Gesprochene mit.

Was sie schreibt, wird gespeichert. Sonst passiert noch nichts.

*Im Code: `save_interview`*

### 3. Sie sieht „Ich prüfe deine Beschreibung"

Ein Warteschirm mit drei Punkten. Dahinter passiert der **erste Modellaufruf**:
Das Programm schickt ihre Erzählung an OpenAI mit der Frage „welche Abläufe
erkennst du hier?" und bekommt bis zu drei zurück.

Vorher schaut es noch im eigenen Wissen nach — dazu unten mehr.

*Im Code: `create_process_options`*

### 4. Sie wählt einen Ablauf

Drei Karten: „Bearbeitung eingehender Schadensmeldungen", „Rechnungs- und
Angebotsabgleich", „Antworten auf Eigentümeranfragen". Sie klickt einen an.

Jetzt der **zweite Modellaufruf**: Das Programm lässt sich beschreiben, wie
dieser Ablauf bei ihr heute tatsächlich läuft — Anfang, Ende, die Schritte
dazwischen.

*Im Code: `select_process`*

### 5. Vielleicht kommt eine Rückfrage

Hier entscheidet das Programm: Weiß ich genug, oder muss ich noch etwas
fragen?

Wenn es genug weiß, geht es direkt weiter. Wenn nicht, kommen bis zu vier
Fragen — immer nur eine auf einmal. „Weiß ich gerade nicht" ist eine gültige
Antwort.

Für diese Entscheidung braucht es je nach Fall zwei weitere Modellaufrufe.

*Im Code: `continue_after_process_answers` in `app/services/process_service.py`*

### 6. Sie sieht „Ich prüfe, welcher KI-Schritt zu deinem Ablauf passt"

Der zweite Warteschirm. Diesmal fragt die Seite alle paar Sekunden beim Server
nach, ob es fertig ist.

Dahinter läuft die eigentliche Analyse — **drei weitere Modellaufrufe**:

1. Um welche Art von Problem geht es?
2. Welches der hinterlegten Lösungsmuster passt am besten?
3. Und schließlich: der ganze Ergebnistext.

*Im Code: `run_analysis` in `app/services/analysis_service.py`*

### 7. Sie sieht ihr Ergebnis

Bevor die Seite angezeigt wird, prüft das Programm dreimal: Ist überhaupt ein
Ergebnis da? Ist es vollständig? Enthält es Fachsprache oder interne
Kennungen, die niemand außerhalb verstehen soll?

Fällt eine Prüfung durch, sieht sie lieber eine Fehlermeldung als ein halbes
Ergebnis.

*Im Code: `show_results`*

---

## Das Wichtigste in einem Satz

**Ein Durchlauf fragt das Sprachmodell bis zu sieben Mal.** Deshalb dauert er
so lange. Jeder einzelne Aufruf braucht zwischen zehn und über hundert
Sekunden.

---

## Was ist „RAG"?

An drei Stellen schaut das Programm vor einem Modellaufruf im **eigenen Wissen**
nach: bei den Ablaufvorschlägen, bei den Rückfragen und bei der Endanalyse.

Unter `knowledge/` liegen aufbereitete Texte — Forschung über kleine Betriebe,
typische Abläufe, was bei Automatisierung schiefgeht. Aus diesen Texten wurde
ein **Suchindex** gebaut: eine Datei, in der man schnell die Abschnitte findet,
die inhaltlich zu einer Frage passen.

Die gefundenen Abschnitte werden der Frage ans Modell beigelegt. Die Idee: Das
Modell soll nicht aus dem Bauch antworten, sondern auf geprüftem Material
aufsetzen.

*Im Code: `app/rag_service.py`*

**Ehrlich dazu:** Ob es die Antworten wirklich besser macht, ist noch nicht
belegt. Beim Versuch, es zu messen, kam ohne die Suchtreffer gar keine Antwort
zustande — es gab also nichts zu vergleichen.

---

## Wo was gespeichert wird

Fünf Tabellen, alle in `app/models.py`:

| Tabelle | Was drinsteht |
|---|---|
| `AnalysisSession` | ein Besuch. Alles andere hängt daran. |
| `InterviewQuestion` | jede Frage mit ihrer Antwort |
| `ProcessOption` | die erkannten Abläufe |
| `Analysis` | das fertige Ergebnis |
| `AutomationOpportunity` | die einzelnen Möglichkeiten darin |

---

## Welche Datei wofür da ist

| Datei | Wofür |
|---|---|
| `app/routes.py` | die Adressen. Nimmt Klicks entgegen, gibt Seiten zurück. Rechnet nichts. |
| `app/services/` | die Ablauflogik. Hier wird entschieden und gerechnet. |
| `app/repository.py` | alle Datenbankzugriffe. Nirgends sonst wird gespeichert oder gelesen. |
| `app/web/` | Cookie, Weiterleitungen, Vorlagen. |
| `app/prompts/` | die Texte, mit denen das Modell gefragt wird — als eigene Dateien. |
| `app/openai_service.py` | jeder Aufruf des Modells geht hier durch. |
| `app/rag_service.py` | die Suche im eigenen Wissen. |
| `app/recommendation_service.py` | wählt aus dem Katalog das passende Lösungsmuster. |
| `app/schemas.py` | prüft, was das Modell zurückgibt — und was nach außen darf. |
| `app/templates/` | die Seiten, die der Kunde sieht. |

---

## „Ich will X ändern" — wo?

| Ich will … | Datei |
|---|---|
| den Text auf der Startseite ändern | `app/templates/landing.html` |
| die Einstiegsfrage anders stellen | `app/questions.py` |
| ändern, wie das Modell nach Abläufen sucht | `app/prompts/prozessvorschlaege.md` |
| ändern, wie das Ergebnis formuliert wird | `app/prompts/ergebnis_teil1.md` und `ergebnis_teil2.md` |
| das Aussehen der Ergebnisseite ändern | `app/templates/ergebnis.html` und `app/static/styles.css` |
| ein neues Wort verbieten, das nie beim Kunden landen darf | `app/schemas.py` |
| eine neue Seite hinzufügen | `app/routes.py`, plus eine Datei in `app/templates/` |

---

## Was du wissen solltest, wenn du das erklärst

**Die neue Ergebnisseite ist gebaut, aber noch nicht angeschlossen.** Sie liegt
unter `/vorschau/ergebnis`. Der normale Ablauf endet weiterhin auf der alten
Seite. Die Umstellung ist ein eigener Schritt und steht aus.

**Die Sitzungsnummer im Pfad ist nicht geschützt.** `/sessions/1/results` ist
für jeden erreichbar, der die Zahl errät. Das Cookie verhindert nur, dass die
Nummer in der Adresszeile auftaucht — es schützt die Daten nicht.

**Manche Funktionsnamen in älteren Dokumenten stimmen nicht mehr.** Beim
Aufräumen wurden sie umbenannt und verschoben; `_next_valid_path` heißt jetzt
`next_valid_path` und liegt in `app/services/process_service.py`.
