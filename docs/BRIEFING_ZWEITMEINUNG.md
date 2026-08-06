# AI Start Map – Briefing für eine Zweitmeinung

**Status:** Historical Snapshot – vor Integration des semantischen Klassifikators erstellt. Für den aktuellen Implementierungs- und Teststand gilt `docs/PROJECT_STATE.md`; dieses Briefing bleibt als zeitgebundener Review-Kontext erhalten.

*Zum Kopieren in einen neuen Chat. Der Text ist so geschrieben, dass er ohne
weiteren Kontext verständlich ist.*

---

Ich heiße Daria. Ich schließe gerade ein Masterschool-Programm ab, und das hier
ist mein Abschlussprojekt. Gleichzeitig ist es der Prototyp für das, was ich
langfristig beruflich machen möchte: kleinen Betrieben KI-Lösungen anbieten.
Ich lerne das meiste davon gerade erst, während ich es baue.

Ich möchte von dir eine ehrliche Einschätzung, keine Bestätigung. Wenn mein
Ansatz an einer Stelle nicht trägt, sag es mir deutlich.

## Was ich erreichen will

Meine Zielgruppe sind Handwerker, Blumenläden, Massagesalons, Fahrradwerkstätten,
Hausmeisterservices — Solo-Selbstständige und sehr kleine Betriebe. Diese Leute
hören überall „KI, KI, KI" und denken sich: Kann mir das helfen? Sie haben keine
IT-Abteilung, oft kein System außer Handy, WhatsApp, vielleicht Excel, und sie
wissen nicht, wo sie anfangen sollen. Viele sind eher überfordert als skeptisch.

Meine Idee: So jemand kommt auf meine Website, erzählt frei — am liebsten
gesprochen — wie sein Alltag wirklich abläuft. Am Ende bekommt er eine konkrete,
verständliche Empfehlung: das ist dein eigentliches Problem, das ist der eine
sinnvolle erste Schritt mit KI, so würde der Ablauf danach aussehen, so sieht
das Ergebnis aus, das prüfst du selbst.

Langfristig will ich genau diese Lösungen dann für ihn bauen. Das Werkzeug ist
also Diagnose und Einstieg in eine Zusammenarbeit, kein fertiges Produkt, das
er allein benutzt.

## Was mich von bestehenden Anbietern unterscheiden soll

Es gibt Anbieter, die drei feste Lösungen haben — Telefonassistent, Termin
buchen, Rechnung abschließen — und jeden Kunden in eine davon pressen. Zwei
Beispiele, warum mich das stört:

**Schuhmacher.** Er sagt: „Ich finde die Schuhe im Regal nicht wieder." Die
Empfehlung dort lautet sinngemäß: „Wir richten es so ein, dass der Kunde eine
Nachricht bekommt, wenn der Schuh fertig ist." Das klingt gut, geht aber nicht.
Es gibt kein System im Regal. Niemand weiß, welcher Schuh zu welchem Auftrag
gehört. Die Empfehlung setzt eine Grundlage voraus, die es nicht gibt. Richtig
wäre: „Du brauchst zuerst eine eindeutige Kennzeichnung am Schuh und einen
festen Ablageort. Danach ist die Benachrichtigung einfach."

**Hausmeister.** Er sagt: „Ich fahre zum Kunden, der will noch dies und das,
ich kaufe Material ein, ich habe Rechnungen überall, mal ein Zettel, mal was auf
dem Handy." Was ich hier möchte: „Du hast doch schon ein Handy und WhatsApp.
Schick nach dem Einsatz einfach wie bisher deine Sprachnachricht, ein Foto und
den Bon. Daraus entsteht automatisch eine fertige Einsatznotiz mit Zeit,
Material und Tätigkeit, die du nur noch prüfst und freigibst." Keine neue App,
nichts Neues lernen.

Das Prinzip dahinter: bei dem anfangen, was der Betrieb **schon hat**. Fehlende
Voraussetzungen ehrlich benennen, statt sie stillschweigend vorauszusetzen. Und
wenn KI an dieser Stelle noch gar nicht hilft, das auch sagen.

## Wo ich technisch stehe

Ich habe eine funktionierende Webanwendung gebaut: Python, FastAPI, PostgreSQL,
OpenAI mit Structured Outputs, zwei FAISS-Indizes für Retrieval, 107 Tests
laufen grün.

Der Ablauf: freie Erzählung per Text oder Spracheingabe, Auswahl eines erkannten
Prozesses, Bestätigung einer kurzen Ist-Zusammenfassung, null bis maximal drei
Rückfragen, dann das Ergebnis mit Vorher/Nachher, KI-Ablauf, Ergebnisvorschau
und Umsetzungsweg. Ausdruck als PDF möglich.

Fachlich habe ich einen strukturierten Katalog erarbeitet: zwölf Problemfamilien
(zum Beispiel „verteilte Vorgangsinformationen", „fehlende Objekt- und
Ortszuordnung", „Lücke zwischen Außendienst und Rechnung") und zehn
Lösungsmuster (zum Beispiel „mobile Einsatzdokumentation aus Sprache, Fotos und
Bon", „Objekt-ID und echter Ablageort") mit einer Zuordnungsmatrix. Dazu neun
GenAI-Fähigkeiten, sechs Entscheidungs-Gates, zwölf Fehlermuster und
Autonomiestufen A0 bis A5, wobei A0 ausdrücklich bedeutet: hier ist eine Regel
oder normale Software besser als KI.

## Das gemessene Problem

Ich habe gerade zum ersten Mal gemessen, wie gut das System die richtige
Problemfamilie und das richtige Lösungsmuster wählt. 91 Testfälle:

- 48 Prozent aller Fälle fallen auf dieselbe Standard-Problemfamilie zurück
- die richtige Problemfamilie wird in 28 Prozent der Fälle als erste erkannt
- das richtige Lösungsmuster in 30 Prozent
- zwei der zwölf Problemfamilien sind technisch überhaupt nicht erreichbar
- die sechs Entscheidungs-Gates liegen zu 82 bis 99 Prozent auf demselben Wert

Die Ursache ist klar: Die Zuordnung von Erzählung zu Problemfamilie läuft über
etwa 40 hartkodierte deutsche Stichwörter. Wer nicht wörtlich „Sprachnachricht"
oder „Regal" sagt, fällt durch. Das Sprachmodell darf die Vorauswahl danach nur
noch schön formulieren, nicht korrigieren.

Mir ist bewusst, dass ich damit gerade strukturell dasselbe mache wie die
Anbieter, die ich kritisiere: ein festes Menü, nur mit zehn statt drei Einträgen.

Der geplante nächste Schritt ist, diese Zuordnung an das Sprachmodell zu geben —
mit den Katalogdefinitionen als Kontext, während die Sicherheitsregeln,
Budgets und Freigabegrenzen weiter fest in Python bleiben.

## Worüber ich deine Einschätzung möchte

1. **Ist der Ansatz realistisch?** Überschätze ich, was ein Sprachmodell aus
   einer freien, ungeordneten Erzählung eines Handwerkers verlässlich
   herausholen kann?

2. **Trägt die Katalog-Idee?** Sind zwölf Problemfamilien und zehn Lösungsmuster
   eine sinnvolle Struktur, oder ist jeder feste Katalog am Ende dasselbe Menü,
   das ich vermeiden will? Was wäre die Alternative?

3. **Wo endet KI und fängt mein Urteil an?** Welchen Teil der Diagnose kann ein
   Modell zuverlässig übernehmen, und wo brauche ich zwingend einen Menschen?

4. **Was kann ich für einen Kunden wie den Hausmeister realistisch bauen?**
   WhatsApp-Nachricht rein, strukturierte Einsatznotiz raus, ohne dass er eine
   neue App braucht. Mit welcher Technik, mit welchem Aufwand, mit welchen
   rechtlichen und datenschutzrechtlichen Stolpersteinen? Ich habe darin noch
   keine Erfahrung.

5. **Chatbot oder geführter Ablauf?** Am liebsten hätte ich ein freies Gespräch
   statt eines Formulars. Ist das eine gute Idee oder eine Falle, wenn ich am
   Ende ein strukturiertes, verlässliches Ergebnis brauche?

6. **Woran sollte ich Qualität messen?** Trefferquote bei der Zuordnung ist
   messbar, aber vielleicht das falsche Ziel. Mein eigentliches Kriterium ist:
   Der Betrieb liest das Ergebnis und denkt „genau so ist es bei mir" — und
   traut sich den ersten Schritt zu. Wie macht man so etwas messbar?

7. **Was übersehe ich?** Sowohl fachlich als auch geschäftlich.

Bitte antworte konkret und mit Begründung. Wenn du etwas nicht sicher weißt,
sag das, statt zu raten.
