"""Die fachlichen Regeln stehen im Prompt, den die Anwendung wirklich lädt.

Kein Modellaufruf. Diese Tests halten fest, was inhaltlich zugesagt ist —
nicht wie es formuliert ist. Sie laden die Prompts über dieselbe Funktion wie
der Produktionspfad: Wird eine Datei umbenannt oder ein Aufruf umgehängt,
werden sie rot statt still zu einem anderen Text zu greifen.

Der Anlass: Ein sehr kleiner Automationsfall bekam fünf Lösungsfamilien,
drei erzwungene Beispielansichten und einen Hebel, der genau die morgendliche
Handarbeit vorschlug, die die Lösung gerade abschafft. Nichts davon war ein
Fehler im Code — alles stand so im Prompt.
"""

from __future__ import annotations

import re

import pytest

from app.openai_service import _prompt

def _fliesstext(name: str) -> str:
    """Der Prompt als eine Zeile.

    Eine Regel steht im Prompt umbrochen. Ein Test, der am Umbruch
    haengt, wird rot, sobald jemand einen Absatz neu formatiert -- und
    sagt dann etwas ueber Zeilenlaengen statt ueber die Zusage.
    """

    ohne_zitatzeichen = re.sub(r"^\s*>\s?", "", _prompt(name), flags=re.M)
    return " ".join(ohne_zitatzeichen.split())


DIAGNOSE = "diagnose"
AUSWAHL = "zielarchitektur"
ANSICHTEN = "ergebnis_teil2a"
REST = "ergebnis_teil2b"


# --- Die kleinste Lösung, die den Engpass löst ----------------------------


def test_the_selection_asks_for_the_smallest_sufficient_set() -> None:
    """Die Auswahlregel steht da, und sie steht als Frage."""

    fliess = _fliesstext(AUSWAHL)

    assert "kleinste Menge" in fliess
    assert "Löst die verbleibende Gesamtlösung ohne diese Familie" in fliess
    assert "Bleibt eine dafür notwendige Station ungelöst" in fliess


def test_a_mention_is_not_a_recommendation() -> None:
    """Dass jemand E-Mails erwähnt, begründet keine Marketingautomation."""

    prompt = _prompt(AUSWAHL)

    assert "Eine Erwähnung ist keine Empfehlung" in prompt
    assert "nicht automatisieren will" in prompt


def test_the_selection_forces_no_minimum() -> None:
    """Null Familien sind eine richtige Antwort.

    Eine Untergrenze im Prompt macht jede Grenze im Schema wirkungslos: Das
    Modell füllt dann auf, und der Server lässt es durch, weil nichts
    verletzt ist.
    """

    prompt = _prompt(AUSWAHL)

    assert "Es gibt keine Mindestzahl" in prompt
    assert "drei bis neun" not in prompt
    assert "drei bis fünf Kurznamen" not in prompt


# --- Ansichten nur, wenn ein Mensch etwas ansehen muss --------------------


def test_views_are_only_created_when_someone_must_look(  ) -> None:
    """Null Ansichten sind gültig, wenn die Lösung im Hintergrund läuft."""

    prompt = _prompt(ANSICHTEN)

    assert "null Ansichten die richtige Antwort" in prompt
    assert "Was müsste der Mensch künftig tatsächlich sehen?" in prompt


def test_no_screen_is_drawn_for_a_system_that_stays() -> None:
    """Bleibt der Kalender, wird er nicht als neue Anwendung nachgebaut."""

    prompt = _prompt(ANSICHTEN)

    assert "Baue keine Oberfläche für ein System, das bleibt" in prompt
    assert "keine erfundene Anwendung" in prompt


# --- Hebel, die nicht die Handarbeit verstärken ---------------------------


def test_a_lever_may_not_reinforce_the_manual_work_being_removed() -> None:
    """**Der Widerspruch, der im Live-Lauf sichtbar wurde.**

    Eine Automation empfehlen und daneben eine tägliche Kontrollrunde von
    Hand hebt die eigene Empfehlung auf.
    """

    prompt = _prompt(REST)

    assert "darf nicht die Handarbeit verstärken" in prompt
    assert "manuelle Prüfliste" in prompt


def test_no_lever_is_a_valid_answer() -> None:
    """Kein Hebel ist besser als ein erfundener."""

    prompt = _prompt(REST)

    assert "gern **keiner**" in prompt


# --- Jedes Feld hat genau eine Aufgabe ------------------------------------


@pytest.mark.parametrize("name", [AUSWAHL, REST])
def test_each_field_has_one_job(name: str) -> None:
    """Sonst liest der Kunde dieselbe Empfehlung sieben Mal."""

    prompt = _prompt(name)

    assert "Jeder Abschnitt hat genau eine Aufgabe" in prompt
    assert "kurze vollständige Sätze" in prompt


def test_the_two_explaining_fields_are_kept_apart() -> None:
    """„Warum diese Lösung" und das Zielbild beantworten verschiedene Fragen."""

    prompt = _prompt(AUSWAHL)

    assert "Warum löst genau diese Zusammenstellung den diagnostizierten" in prompt
    assert "Was passiert künftig als zusammenhängendes System?" in prompt


# --- Ein vorhandenes System, das passt, bleibt das System -----------------


def test_an_existing_system_is_used_before_a_second_one_is_built() -> None:
    """**Die zweite Gegenfrage.**

    Ein Betrieb mit passender Fachsoftware, die uneinheitlich genutzt wird,
    braucht keinen gemeinsamen Eingang davor — das waere ein zweites System
    unter anderem Namen.
    """

    fliess = _fliesstext(AUSWAHL)

    assert "Gibt es in der Erzählung ein System, das diese Aufgabe schon" in fliess
    assert "Ist die Antwort ja, dann ist die Lösung, es zu benutzen" in fliess
    assert "ist ein zweites System, auch wenn er anders heißt" in fliess


def test_modules_describe_the_existing_system_not_a_new_place() -> None:
    """Auch mit gewaehlten Familien bleibt das vorhandene System der Ort."""

    fliess = _fliesstext(AUSWAHL)

    assert "eingerichtet, vereinheitlicht oder angebunden" in fliess
    assert "nicht, wie ein neuer zentraler Ort entsteht" in fliess


# --- Vollstaendigkeit vor Minimalitaet ------------------------------------


def test_completeness_comes_before_minimality() -> None:
    """**Der Salami-Effekt.**

    Fuer sich allein wirkt fast jede Familie verzichtbar. Fuenf solche
    Entscheidungen spaeter fehlt mitten im Ablauf eine Station. Deshalb
    erst vollstaendig waehlen, dann kuerzen -- in dieser Reihenfolge.
    """

    fliess = _fliesstext(AUSWAHL)

    assert "Vollständigkeit kommt vor Minimalität" in fliess
    assert "Ende zu Ende" in fliess
    assert "Erst danach reduzierst du diese Menge" in fliess


def test_the_cut_is_checked_against_the_rest_not_the_single_family() -> None:
    """Geprueft wird die verbleibende Gesamtloesung, nicht die Familie."""

    fliess = _fliesstext(AUSWAHL)

    assert (
        "Löst die verbleibende Gesamtlösung ohne diese Familie weiterhin den "
        "vollständigen Kernengpass"
    ) in fliess
    assert "Bleibt eine dafür notwendige Station ungelöst, bleibt die Familie" in fliess


def test_small_stays_possible_and_large_stays_possible() -> None:
    """Minimal heisst nicht klein, sondern nicht mehr als noetig."""

    fliess = _fliesstext(AUSWAHL)

    assert "So klein wie möglich, aber so vollständig wie nötig" in fliess


def test_a_mention_is_not_a_station() -> None:
    """Eine erwaehnte Taetigkeit ist keine Station des Kernengpasses."""

    fliess = _fliesstext(AUSWAHL)

    assert "Nicht** jede Tätigkeit, die der Betrieb erwähnt, ist eine Station" in fliess
    assert "blosse Erwähnungen sind keine" in fliess


# --- Der Prompt behauptet nichts, was der Aufruf nicht mitschickt ---------


def test_the_selection_prompt_promises_only_what_the_call_delivers() -> None:
    """**Ein Prompt, der einen Abschnitt nennt, den es nicht gibt, luegt.**

    Das Zielbildmuster entsteht erst nach der Auswahl -- der Server sucht es
    zu den geprueften Familien. Der Auswahlaufruf bekommt keines. Stand es
    trotzdem im Prompt, suchte das Modell nach einem leeren Abschnitt.
    """

    import inspect

    from app import openai_service

    quelle = inspect.getsource(openai_service.generate_target_architecture)
    abschnitte = re.findall(r'"([A-Z][A-Z_]+)":', quelle)

    assert "ZIELBILDMUSTER" not in abschnitte
    assert "ZIELBILDMUSTER" not in _prompt(AUSWAHL)

    # Und umgekehrt: Was der Aufruf mitschickt, steht auch im Prompt.
    for name in abschnitte:
        assert name in _prompt(AUSWAHL), name


# --- Der Bestand zaehlt zur Vollstaendigkeit ------------------------------


def test_an_existing_system_counts_towards_completeness() -> None:
    """**Der Konflikt zwischen Vollstaendigkeit und Bestand.**

    Die Vollstaendigkeitsregel verlangte fuer jede Station eine Familie. Ein
    Betrieb mit passender Fachsoftware bekam deshalb die ganze Kette noch
    einmal daneben gebaut.
    """

    fliess = _fliesstext(AUSWAHL)

    assert "auch dann abgedeckt, wenn ein vorhandenes System sie schon" in fliess
    assert "Bestand und gewählte Familien zusammen" in fliess
    assert "ein System, von dem nur der Name fällt, kann nichts" in fliess


def test_an_existing_function_is_not_built_a_second_time() -> None:
    """Eine Familie schliesst Luecken, sie verdoppelt nichts."""

    fliess = _fliesstext(AUSWAHL)

    assert "erst nötig, wo danach eine echte funktionale Lücke bleibt" in fliess
    assert "daneben ein zweites Mal zu bauen" in fliess
    assert "Gelöst wird `DIAGNOSE.engpass`" in fliess


def test_no_new_technology_binds_the_modules_too() -> None:
    """`recommend_new_technology=false` ist keine Verzierung.

    Ein `false` neben Modulen, die eine zweite Systembasis entwerfen, ist ein
    Widerspruch -- und der Kunde merkt ihn.
    """

    fliess = _fliesstext(AUSWAHL)

    assert "Dieses Feld bindet auch die Module" in fliess
    assert "kein Modul eine neue Systembasis neben der vorhandenen" in fliess


# --- Die Umsetzung ist unsere Arbeit -------------------------------------


def test_the_rollout_steps_are_our_work_not_the_customers() -> None:
    """**Wer baut, ist nicht der Betrieb.**

    Aus dem Live-Lauf: „Sammeln Sie eine Beispielmenge eingehender E-Mails
    und Fälle zum Test." Das macht aus einem Angebot eine Hausaufgabe — und
    aus einem Kunden jemanden, der absagt.
    """

    fliess = _fliesstext(REST)

    assert "Das machen wir, nicht der Betrieb" in fliess
    assert "schreib sie in der Wir-Form" in fliess
    assert "macht aus einem Angebot eine Hausaufgabe" in fliess


def test_what_the_customer_must_contribute_is_named() -> None:
    """Wo er wirklich etwas beisteuern muss, steht es ausdrücklich dabei.

    Sonst wäre die Wir-Form eine Verschleierung statt einer Zusage.
    """

    fliess = _fliesstext(REST)

    assert "dazu brauchen wir von Ihnen einmal" in fliess


# --- Was der Betrieb davon hat -------------------------------------------


def test_every_module_says_what_the_business_gets_out_of_it() -> None:
    """**Was von seinem Tisch verschwindet**, nicht was der Baustein kann.

    Die Zusage war einmal „warum ihn das interessiert" und wurde damit
    von Eigenschaften erfüllt: „Weniger Nachfragen", „Zentrale Ablage".
    Das beschreibt den Baustein und entlastet niemanden. Der Kunde soll
    den Satz vervollständigen können: Danach muss ich nicht mehr …
    """

    fliess = _fliesstext(AUSWAHL)

    assert "was er künftig nicht mehr selbst machen muss" in fliess
    assert "das ist eine Beschreibung und keine Entlastung" in fliess


def test_the_benefit_may_not_become_an_invented_saving() -> None:
    """**Keine ausgedachte Ersparnis — und auch keine ausgerechnete.**

    Der Nutzen ist die Stelle, an der eine erfundene Zahl am leichtesten
    hineinrutscht: Sie sieht genauso überzeugend aus wie eine gemessene.
    Das Rechnen steht ausdrücklich mit dabei, weil aus „80 Mails am Tag"
    sonst eine Stundenzahl wird, die niemand genannt hat.
    """

    fliess = _fliesstext(AUSWAHL)

    assert "Keine ausgedachte Ersparnis" in fliess
    assert "Rechne auch nichts aus" in fliess
    assert "eine leere Zeile ist besser als eine Floskel" in fliess


def test_his_own_figure_is_allowed_with_proof() -> None:
    """Seine eigene Angabe darf zurückkommen — mit Beweispflicht.

    Der Unterschied zur erfundenen Zahl ist die Herkunft, nicht die Form.
    Deshalb muss im Prompt beides stehen: dass er sie nennen darf, und
    dass Zahl und Einheit wörtlich bei ihm vorkommen müssen.
    """

    fliess = _fliesstext(AUSWAHL)

    assert "Seine eigene Angabe darfst du nennen" in fliess
    assert "Zahl **und** Einheit müssen wörtlich bei ihm vorkommen" in fliess
    assert "Im Zweifel ohne Zahl" in fliess
def test_the_meaning_is_a_headline_not_a_comment() -> None:
    """**Ein Hauptsatz, keine Einleitung.**

    Auf der Ergebnisseite steht die Bedeutung gross über dem Zitat und trägt
    die Karte. Ein Kommentar über den Beleg, mit dem Verb am Satzende, liest
    sich gross gesetzt wieder wie ein Bericht — und die Seite soll eine
    Geschichte erzählen, die man versteht, ohne viel zu lesen.
    """

    fliess = _fliesstext(DIAGNOSE)

    assert 'eine Schlagzeile, kein Kommentar' in fliess
    assert 'höchstens acht Wörter' in fliess
    assert 'Keine Einleitung wie' in fliess


def test_a_quotation_is_short_enough_to_read() -> None:
    """Ein Beleg trifft den Punkt, statt den Absatz mitzubringen.

    Wörtlich heisst nicht vollständig: Anfang und Ende dürfen an Satzgrenzen
    liegen, verändert werden darf innerhalb nichts. Ohne diese Erlaubnis
    nimmt das Modell lieber zu viel als zu wenig — eine Karte trug sechs
    Zeilen Zitat.
    """

    fliess = _fliesstext(DIAGNOSE)

    assert 'Wähl einen kurzen Satz' in fliess
    assert 'Wörtlich heisst nicht vollständig' in fliess
def test_a_comparison_line_fits_on_a_card() -> None:
    """Acht Wörter, sonst ist es kein Vergleich mehr, sondern ein Absatz.

    Die Zeilen stehen paarweise auf einer Karte, vier davon nebeneinander.
    Wer dort einen Nebensatz liest, hat den Vergleich schon verloren — und
    das „statt …" ist ohnehin überflüssig, weil das Heute direkt daneben
    steht.
    """

    assert 'Höchstens acht Wörter je Zeile' in _fliesstext(DIAGNOSE)
    assert 'Höchstens acht Wörter je Zeile' in _fliesstext(AUSWAHL)
    assert 'den Vergleich zieht der Leser selbst' in _fliesstext(AUSWAHL)
def test_a_comparison_line_names_friction() -> None:
    """Eine Heute-Zeile muss wehtun, sonst ist der Vergleich keiner.

    Beim Schulungszentrum begann die Reihe mit „Teilnehmer melden sich über
    die Website" — wahr, und kein Problem. Daneben stand dann eine
    Verbesserung ohne Ursache, und der Kunde las vier Beobachtungen statt
    einer Kette.
    """

    heute = _fliesstext(DIAGNOSE)
    kuenftig = _fliesstext(AUSWAHL)

    assert 'Jede Zeile muss Reibung benennen' in heute
    assert 'eine Kette, keine Sammlung' in heute
    assert 'nimmt genau die Reibung weg, die gegenüber steht' in kuenftig
def test_the_first_view_shows_the_biggest_promise() -> None:
    """Die grosse Ansicht ist die, bei der er denkt: genau das fehlt mir.

    Auf der Seite steht die erste Ansicht über die volle Breite und die
    beiden anderen kleiner darunter. Ohne Regel liefert das Modell sie in
    beliebiger Reihenfolge — und dann bekam ein Handwerker, dessen Problem
    das Zusammensuchen eines Auftrags ist, oben eine Tagesübersicht.
    """

    fliess = _fliesstext(ANSICHTEN)

    assert 'Die erste Ansicht ist die wichtigste' in fliess
    assert 'nicht den ersten Schritt im Ablauf' in fliess
    assert 'wie dieses Ergebnis zustande kommt' in fliess
    assert 'dürfen nicht dieselben drei Typen bekommen' in fliess
def test_evidence_binds_the_problem_not_the_solution() -> None:
    """**Beleg für das Problem, Freiheit für die Lösung.**

    Zwei Regeln zusammen — „die kleinste Menge" und „nur was der Betrieb
    genannt hat" — ergaben E-Mail sortieren, Kalender abgleichen, Aufgaben
    anzeigen. Der Kunde kann keinen Telefonassistenten verlangen, wenn er
    nicht weiss, dass es ihn gibt; wer nur vorschlägt, was er selbst
    benennen konnte, schlägt nie etwas Neues vor.

    Der Engpass bleibt an seine Worte gebunden. Das ist die Zusage, die
    diese Lockerung überhaupt vertretbar macht.
    """

    fliess = _fliesstext(AUSWAHL)

    assert 'Beleg für das Problem, Freiheit für die Lösung' in fliess
    assert 'er kann es also auch nicht verlangen' in fliess
    assert 'Eine Lösung ohne Problem bleibt eine Erfindung' in fliess


def test_the_third_stage_may_name_what_he_does_not_know() -> None:
    """`spaeter` ist die Ambitionsebene, nicht der dritte Bauabschnitt.

    Ohne sie endet jede Auswertung bei dem, was der Betrieb ohnehin schon
    ahnt. Mit ihr sagt die Seite: hier ist der einfache Einstieg — und hier
    ist, was darüber hinaus möglich wäre.

    Die Fessel bleibt: Gibt der freigegebene Katalog nichts her, das auf
    einen belegten Engpass zeigt, bleibt die Stufe leer.
    """

    fliess = _fliesstext(AUSWAHL)

    assert 'Das ist die Ambitionsebene, kein Bauplan' in fliess
    assert 'was er noch nicht kennt' in fliess
    assert 'Zu jeder Lösung gehört ein Modul auf `spaeter`' in fliess
    assert 'bleibt die Stufe leer — erfunden wird nichts' in fliess
def test_the_bottleneck_may_lie_outside_the_business() -> None:
    """Nicht jeder Engpass ist ein Ablageproblem.

    Alle drei Beispiele für den Engpasssatz waren Innensicht — Information
    am falschen Ort, Stand in Köpfen, Unterlagen zu spät. Das Modell lernt
    die Form aus den Beispielen, und drei gleichförmige Beispiele ergeben
    eine gleichförmige Diagnose: Wer jeden Fall als Ablageproblem fasst,
    findet auch nur Lösungen für Ablageprobleme.
    """

    fliess = _fliesstext(DIAGNOSE)

    assert 'Der Engpass muss nicht im Inneren liegen' in fliess
    assert 'Jede Terminfrage unterbricht eine laufende Behandlung' in fliess


def test_what_the_business_calls_its_biggest_burden_counts() -> None:
    """Das Thema darf nicht gewechselt werden.

    Eine Werkstatt sagte wörtlich, die Telefonate seien der grösste
    Zeitfresser. Die Diagnose machte daraus, der Stand stecke in Zurufen und
    Zetteln — wahr, und eine Antwort auf eine Frage, die niemand gestellt
    hat. Die Ursache benennen ist erlaubt; das Thema wechseln nicht.
    """

    fliess = _fliesstext(DIAGNOSE)

    assert 'Was der Betrieb selbst als grösste Last benennt' in fliess
    assert 'du darfst das Thema nicht wechseln' in fliess
def test_one_module_is_the_exception() -> None:
    """Wer eine Stunde erzählt hat, bekommt keinen einzelnen Baustein.

    Der Prompt segnete eine Ein-Modul-Antwort ausdrücklich ab. Für einen
    Betrieb, der über Statusanrufe, Zettel, Freigaben in Nachrichten und
    Teilebestellungen erzählt, ist das kein Zielbild, sondern ein
    Bruchstück — und es liest sich nicht als Sorgfalt, sondern als
    Desinteresse.
    """

    fliess = _fliesstext(AUSWAHL)

    assert 'Ein einzelnes Modul ist die Ausnahme' in fliess
    assert 'Ende zu Ende heisst: der ganze Weg' in fliess


def test_the_outlook_does_not_depend_on_how_many_modules() -> None:
    """Gerade die kleine Lösung braucht den Ausblick.

    Die Regel hing an der Modulzahl — bei vier oder mehr. Bei einer
    minimalen Lösung griff sie nie, und ausgerechnet dort fehlt der
    Ausblick am meisten.
    """

    fliess = _fliesstext(AUSWAHL)

    assert 'unabhängig davon, wie viele es insgesamt sind' in fliess
    assert 'bleibt die Stufe leer — erfunden wird nichts' in fliess
