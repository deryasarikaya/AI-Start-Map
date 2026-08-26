"""Der Ergebnisvertrag der neuen Ergebnisseite.

Für jede der vier harten Regeln steht hier ein Test, der greift, und einer,
der durchlässt. Die Bausteine unten sind gültige Mindestwerte; jeder Test
verändert genau das Feld, um das es ihm geht.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.result_schema import (
    MINIMUM_EVIDENCE,
    Division,
    Result,
    ResultPartOne,
    ResultPartTwo,
    Understanding,
    Value,
    narrative,
    rejected_quotes,
    validation_context,
)

ERZAEHLUNG = (
    "Ich habe eine kleine Hausverwaltung mit drei Leuten. Mieter melden Schäden "
    "per Telefon, per Mail und manchmal über WhatsApp. Wenn der Mieter nach zwei "
    "Wochen nachfragt, muss ich erst suchen, wo die Meldung liegt. "
    "Eine Buchhaltungssoftware will ich nicht ersetzen."
)
ERZAEHLUNG_OHNE_AUSSCHLUSS = (
    "Mieter melden Schäden per Telefon und per Mail. Ich schreibe das auf einen "
    "Zettel und rufe dann einen Handwerker an."
)


def _understanding(**overrides: object) -> dict[str, object]:
    """Ein gültiger `verstanden`-Block, dessen Zitate in der Erzählung stehen."""

    data: dict[str, object] = {
        "engpass_absatz": "Meldungen werden nicht einheitlich festgehalten.",
        "belege": [
            {
                "zitat": "per Telefon, per Mail und manchmal über WhatsApp",
                "bedeutung": "Die Meldungen kommen über drei getrennte Wege.",
            },
            {
                "zitat": "muss ich erst suchen, wo die Meldung liegt",
                "bedeutung": "Der aktuelle Stand ist nicht abrufbar.",
            },
        ],
        "eckdaten": ["Drei Personen", "Drei Eingangswege", "Kein gemeinsamer Ort"],
    }
    data.update(overrides)
    return data


def _value(**overrides: object) -> dict[str, object]:
    """Ein gültiger `wert`-Block ohne Zahlen und ohne Zeitangaben."""

    data: dict[str, object] = {
        "faellt_weg": [
            "Das Suchen nach der letzten Meldung",
            "Das Nachfragen beim Handwerker",
            "Das doppelte Erfassen derselben Angabe",
            "Das Zusammensuchen des Bearbeitungsstands",
            "Die Rückfrage, wer gerade zuständig ist",
        ],
        "zeit_fuer": [
            "Gespräche mit Mietern",
            "Die Abstimmung mit Eigentümern",
            "Die Vorbereitung der Abrechnung",
        ],
    }
    data.update(overrides)
    return data


def _division(**overrides: object) -> dict[str, object]:
    """Ein gültiger `aufgabenteilung`-Block ohne selbst genannte Grenzen."""

    data: dict[str, object] = {
        "system": [
            "Meldungen aus allen Wegen an einer Stelle sammeln",
            "Zu jeder Meldung eine Karte anlegen",
            "Den Bearbeitungsstand sichtbar halten",
            "An offene Vorgänge erinnern",
            "Den Verlauf je Vorgang festhalten",
        ],
        "mensch": [
            "Die Dringlichkeit einschätzen",
            "Den Handwerker beauftragen",
            "Den Abschluss freigeben",
            "Mit dem Eigentümer sprechen",
        ],
        "grenzen": [],
    }
    data.update(overrides)
    return data


def _part_one(**overrides: object) -> dict[str, object]:
    """Ein gültiger oberer Teil der Ergebnisseite."""

    data: dict[str, object] = {
        "kurzfassung": {
            "engpass_satz": "Meldungen werden nicht einheitlich festgehalten.",
            "loesungsname": "Digitaler Verwaltungs- und Service-Hub",
            "relevante_module": ["Eingang", "Vorgangsakte", "Statusübersicht"],
        },
        "verstanden": _understanding(),
        "warum_diese_loesung": (
            "Der Engpass liegt an der Erfassung, nicht an der Bearbeitung."
        ),
        "zielbild": {
            "name": "Digitaler Verwaltungs- und Service-Hub",
            "beschreibung": "Alle Meldungen laufen an einer Stelle zusammen.",
            "ablauf": [
                {
                    "art": "eingang",
                    "label": "Eingang",
                    "knoten": [{"text": "Telefon", "kategorie": "Kanal"}],
                },
                {
                    "art": "schluessel",
                    "label": "Vorgang",
                    "knoten": [{"text": "Karte je Meldung", "kategorie": "Ablage"}],
                },
            ],
        },
        "vergleich": {
            "heute": [
                "Meldung kommt über drei Wege",
                "Notiz auf Zettel oder in Outlook",
                "Handwerker wird angerufen",
                "Bei Nachfrage wird gesucht",
                "Abschluss wird selten festgehalten",
            ],
            "kuenftig": [
                "Meldung landet an einer Stelle",
                "Karte entsteht automatisch",
                "Zuständigkeit steht fest",
                "Der Stand ist abrufbar",
                "Der Abschluss wird vermerkt",
            ],
        },
        "module": [
            {"gruppe": g, "name": n, "beschreibung": b, "stufe": s}
            for g, n, b, s in (
                ("Eingang", "Sammelstelle", "Nimmt Meldungen aus allen Wegen an.", "jetzt"),
                ("Eingang", "Einordnung", "Erkennt, worum es geht.", "danach"),
                ("Arbeit", "Vorgangsakte", "Hält alles zu einer Meldung zusammen.", "danach"),
                ("Arbeit", "Zuständigkeit", "Zeigt, wer gerade dran ist.", "danach"),
                ("Übersicht", "Statusliste", "Zeigt den Stand aller Vorgänge.", "spaeter"),
                ("Übersicht", "Erinnerung", "Meldet überfällige Vorgänge.", "spaeter"),
            )
        ],
    }
    data.update(overrides)
    return data


def _part_two(**overrides: object) -> dict[str, object]:
    """Ein gültiger unterer Teil der Ergebnisseite."""

    data: dict[str, object] = {
        "ansichten": [
            {
                "typ": "uebersicht",
                "titel": "Was heute Aufmerksamkeit braucht",
                "beschreibung": "Die offenen Vorgänge auf einen Blick.",
                "module_refs": ["Sammelstelle"],
                "daten": {
                    "zeilen": [
                        {"text": "Wasserschaden Haus 12", "status": "rot"},
                        {"text": "Heizung Haus 4", "status": "gelb"},
                    ]
                },
            },
            {
                "typ": "vorgangsakte",
                "titel": "Eine Meldung von innen",
                "beschreibung": "Alles, was zu einem Schaden gehört.",
                "module_refs": ["Vorgangsakte"],
                "daten": {"felder": [{"label": "Objekt", "wert": "Haus 12"}]},
            },
        ],
        "aufgabenteilung": _division(),
        "wert": _value(),
        "systeme": [
            {"name": "Outlook", "umgang": "Meldungen werden übernommen.", "module_refs": ["Sammelstelle"]},
            {"name": "Telefon", "umgang": "Notizen werden erfasst.", "module_refs": ["Sammelstelle"]},
            {"name": "WhatsApp", "umgang": "Nachrichten laufen mit ein.", "module_refs": ["Sammelstelle"]},
            {"name": "Buchhaltung", "umgang": "Bleibt unverändert bestehen.", "module_refs": ["Sammelstelle"]},
        ],
        "architektur": [
            {"ebene": "Eingang", "beschreibung": "Nimmt Meldungen entgegen.", "module_refs": ["Sammelstelle"]},
            {"ebene": "Verstehen", "beschreibung": "Ordnet die Meldung ein.", "module_refs": ["Sammelstelle"]},
            {"ebene": "Arbeit", "beschreibung": "Führt den Vorgang.", "module_refs": ["Sammelstelle"]},
            {"ebene": "Übersicht", "beschreibung": "Zeigt den Stand.", "module_refs": ["Sammelstelle"]},
        ],
        "umsetzung": [
            {"text": "Sammelstelle einrichten", "module_refs": ["Sammelstelle"]},
            {"text": "Eingangswege umleiten", "module_refs": ["Sammelstelle"]},
            {"text": "Vorgangskarte anlegen", "module_refs": ["Sammelstelle"]},
        ],
    }
    data.update(overrides)
    return data


def _diagnose(**overrides: object) -> dict[str, object]:
    """Eine gültige Diagnose — Aufruf 1, ohne jede Lösung."""

    daten: dict[str, object] = {
        "engpass_satz": "Meldungen werden nicht einheitlich festgehalten.",
        "verstanden": _understanding(),
        "vergleich_heute": [
            "Die Meldung kommt per Telefon",
            "Jemand schreibt sie auf einen Zettel",
            "Der Zettel liegt auf dem Schreibtisch",
            "Beim Nachfragen wird gesucht",
            "Der Stand steht in keinem System",
        ],
        "rueckfrage": None,
    }
    daten.update(overrides)
    return daten


def _zielarchitektur(**overrides: object) -> dict[str, object]:
    """Eine gültige Auswahl — mit echten Kennungen und echten Bausteinen.

    Gebaut **aus dem Katalog**, nicht daneben: Wenn sich die Freigabeliste
    ändert, ändert sich diese Vorlage mit. Eine fest eingetippte Kennung
    würde sonst irgendwann eine Familie behaupten, die es nicht mehr gibt.
    """

    from app import solution_catalog

    familien = list(solution_catalog.katalog().values())[:3]
    daten: dict[str, object] = {
        "catalog_fit": True,
        "recommend_new_technology": True,
        "begruendung": "Gemockte Begründung für die Auswahl.",
        "selected_solution_family_ids": [f.kennung for f in familien],
        "loesungsname": "Zentrale Vorgangsstelle",
        "relevante_module": ["Eingang", "Vorgangsakte", "Übersicht"],
        "warum_diese_loesung": (
            "Der Engpass liegt an der Erfassung, nicht an der Bearbeitung."
        ),
        "zielbild": {
            "name": "Zentrale Vorgangsstelle",
            "beschreibung": "Alle Meldungen laufen an einer Stelle zusammen.",
            "ablauf": [
                {
                    "art": "eingang",
                    "label": "Was hereinkommt",
                    "knoten": [{"text": "Telefon", "kategorie": "Kanal"}],
                },
                {
                    "art": "schluessel",
                    "label": "Wo alles zusammenläuft",
                    "knoten": [{"text": "Vorgang", "kategorie": "Ort"}],
                },
            ],
        },
        "vergleich_kuenftig": [
            "Die Meldung landet an einer Stelle",
            "Sie wird dem Objekt zugeordnet",
            "Der Stand ist sichtbar",
            "Nachfragen beantwortet die Übersicht",
            "Der Abschluss wird vermerkt",
        ],
        "module": [
            {
                "gruppe": "Eingang",
                "name": f"Baustein aus {familie.name}",
                "beschreibung": "Tut für diesen Betrieb, was nötig ist.",
                "stufe": ["jetzt", "danach", "spaeter"][platz],
                "solution_family_ids": [familie.kennung],
                "baustein_refs": [familie.bausteine[0]],
            }
            for platz, familie in enumerate(familien)
        ],
    }
    daten.update(overrides)
    return daten


def _kontext(erzaehlung: str = ERZAEHLUNG) -> dict[str, str]:
    return validation_context(erzaehlung)


# --- Regel 1: Zitate kommen wörtlich vor -----------------------------------


def test_verbatim_quote_is_accepted() -> None:
    """Ein Zitat, das wörtlich in der Erzählung steht, geht durch."""

    verstanden = Understanding.model_validate(_understanding(), context=_kontext())
    assert len(verstanden.belege) == 2


def test_reworded_quote_never_reaches_the_customer() -> None:
    """Ein umformuliertes Zitat kommt nicht durch, auch wenn es dasselbe meint.

    Die Behauptung ist dieselbe wie vorher; nur die Wirkung hat sich geändert.
    Früher riss das Zitat das ganze Ergebnis mit, heute fällt nur es selbst.
    """

    umformuliert = _understanding(
        belege=[
            {
                "zitat": "Meldungen kommen über Telefon, Mail und WhatsApp",
                "bedeutung": "Die Meldungen kommen über drei getrennte Wege.",
            },
            {
                "zitat": "muss ich erst suchen, wo die Meldung liegt",
                "bedeutung": "Der aktuelle Stand ist nicht abrufbar.",
            },
        ]
    )

    geprueft = Understanding.model_validate(umformuliert, context=_kontext())

    uebrig = [beleg.zitat for beleg in geprueft.belege]
    assert "Meldungen kommen über Telefon, Mail und WhatsApp" not in uebrig
    assert uebrig == ["muss ich erst suchen, wo die Meldung liegt"]


def test_a_rejected_quote_is_reported_to_the_caller() -> None:
    """Der Aufrufer erfährt den Wortlaut, um gezielt nachfragen zu können."""

    umformuliert = _understanding(
        belege=[
            {
                "zitat": "Meldungen kommen über Telefon, Mail und WhatsApp",
                "bedeutung": "Die Meldungen kommen über drei getrennte Wege.",
            },
            {
                "zitat": "muss ich erst suchen, wo die Meldung liegt",
                "bedeutung": "Der aktuelle Stand ist nicht abrufbar.",
            },
        ]
    )

    with narrative(ERZAEHLUNG):
        Understanding.model_validate(umformuliert)
        gemeldet = rejected_quotes()

    assert gemeldet == ["Meldungen kommen über Telefon, Mail und WhatsApp"]
    # Ausserhalb des Aufrufs steht die Liste wieder leer.
    assert rejected_quotes() == []


def test_good_quotes_survive_a_bad_neighbour() -> None:
    """Zwei gute Zitate tragen den Abschnitt, auch wenn das dritte fällt."""

    gemischt = _understanding(
        belege=[
            {
                "zitat": "per Telefon, per Mail und manchmal über WhatsApp",
                "bedeutung": "Die Meldungen kommen über drei getrennte Wege.",
            },
            {
                "zitat": "Das hat der Kunde so nie gesagt",
                "bedeutung": "Frei erfunden.",
            },
            {
                "zitat": "muss ich erst suchen, wo die Meldung liegt",
                "bedeutung": "Der aktuelle Stand ist nicht abrufbar.",
            },
        ]
    )

    geprueft = Understanding.model_validate(gemischt, context=_kontext())

    assert len(geprueft.belege) == MINIMUM_EVIDENCE


def test_quote_check_needs_the_narrative() -> None:
    """Ohne Erzähltext wird nicht stillschweigend durchgelassen."""

    with pytest.raises(ValidationError, match="Erzähltext"):
        Understanding.model_validate(_understanding())


def test_quote_match_ignores_quotation_marks_and_spacing() -> None:
    """Andere Anführungszeichen und Leerzeichen sind kein Umformulieren."""

    gleicher_text = _understanding(
        belege=[
            {
                "zitat": "per Telefon,  per Mail und manchmal über WhatsApp",
                "bedeutung": "Die Meldungen kommen über drei getrennte Wege.",
            },
            {
                "zitat": "muss ich erst suchen, wo die Meldung liegt",
                "bedeutung": "Der aktuelle Stand ist nicht abrufbar.",
            },
        ]
    )
    assert Understanding.model_validate(gleicher_text, context=_kontext())



def test_quote_match_ignores_a_different_hyphen() -> None:
    """Ein geschützter Bindestrich ist kein anderes Wort.

    Das Modell hat im Abnahmelauf „E‑Mail“ geliefert, die Erzählung schreibt
    „E-Mail“. Ohne diese Regel scheitert ein Lauf an einem Zeichen, das kein
    Mensch unterscheidet.
    """

    mit_erzaehlung = (
        "Mieter schreiben uns E-Mails und rufen an. Ich suche dann lange."
    )
    verstanden = _understanding(
        belege=[
            {
                "zitat": "Mieter schreiben uns E‑Mails und rufen an",
                "bedeutung": "Die Meldungen kommen über zwei Wege.",
            },
            {
                "zitat": "Ich suche dann lange",
                "bedeutung": "Der Stand ist nicht abrufbar.",
            },
        ]
    )

    assert Understanding.model_validate(
        verstanden, context=validation_context(mit_erzaehlung)
    )



def test_quote_match_ignores_wrapping_quotation_marks() -> None:
    """Anführungszeichen um das Zitat sind kein anderer Wortlaut.

    Im Zehnerlauf hat das Modell zwei Belege in typografische
    Anführungszeichen gesetzt. In der Erzählung stehen die nicht — beide
    Belege fielen durch, obwohl kein Wort anders war.
    """

    verstanden = _understanding(
        belege=[
            {
                "zitat": "„per Telefon, per Mail und manchmal über WhatsApp“",
                "bedeutung": "Die Meldungen kommen über drei getrennte Wege.",
            },
            {
                "zitat": "muss ich erst suchen, wo die Meldung liegt",
                "bedeutung": "Der aktuelle Stand ist nicht abrufbar.",
            },
        ]
    )

    geprueft = Understanding.model_validate(verstanden, context=_kontext())

    assert len(geprueft.belege) == 2


# --- Regel 2: Grenzen nur aus Selbstaussagen -------------------------------


def test_boundary_is_accepted_when_the_customer_excluded_something() -> None:
    """Hat der Kunde etwas ausgeschlossen, darf die Grenze stehen."""

    mit_grenze = _division(
        grenzen=[
            {
                "titel": "Buchhaltung bleibt",
                "erlaeuterung": "Die vorhandene Software wird nicht ersetzt.",
            }
        ]
    )
    geprueft = Division.model_validate(mit_grenze, context=_kontext())
    assert len(geprueft.grenzen) == 1


def test_boundary_is_rejected_without_a_self_statement() -> None:
    """Ohne Ausschluss in der Erzählung bleibt die Liste leer."""

    mit_grenze = _division(
        grenzen=[
            {
                "titel": "Nichts ohne Freigabe",
                "erlaeuterung": "Ein allgemeiner Hinweis, den niemand gesagt hat.",
            }
        ]
    )
    with pytest.raises(ValidationError, match="ausgeschlossen"):
        Division.model_validate(
            mit_grenze, context=_kontext(ERZAEHLUNG_OHNE_AUSSCHLUSS)
        )


def test_empty_boundaries_need_no_narrative() -> None:
    """Ohne Grenzen gibt es nichts zu prüfen."""

    assert Division.model_validate(_division()).grenzen == []


# --- Regel 3: keine Zahlen im Abschnitt „Wert“ -----------------------------


def test_value_without_numbers_is_accepted() -> None:
    """Aussagen ohne Zahl und ohne Zeitangabe gehen durch."""

    assert len(Value.model_validate(_value()).faellt_weg) == 5


@pytest.mark.parametrize(
    "zeile",
    [
        "Spart 3 Stunden pro Woche",
        "Bis zu 40 % weniger Rückfragen",
        "Spart mehrere Stunden",
        "Weniger Aufwand pro Tag",
    ],
)
def test_value_with_a_number_or_duration_is_dropped(zeile: str) -> None:
    """Zahlen, Prozentangaben und Zeitangaben fallen aus dem Abschnitt.

    Zeile für Zeile, wie bei den Zitaten: Die behauptende Zeile fällt, die
    übrigen bleiben. Der Kunde sieht die Behauptung nie — und ein einziger
    schlechter Satz kostet nicht das ganze Ergebnis.
    """

    uebrige = _value()["faellt_weg"][1:]
    geprueft = Value.model_validate(_value(faellt_weg=[zeile, *uebrige]))

    assert zeile not in geprueft.faellt_weg
    assert geprueft.faellt_weg == uebrige


def test_a_value_section_may_end_up_empty() -> None:
    """Behauptet jede Zeile etwas, bleibt nichts übrig — und das ist gültig.

    Ein leerer Abschnitt ist ehrlicher als eine erfundene Ersparnis.
    """

    geprueft = Value.model_validate(
        _value(faellt_weg=["Spart 3 Stunden pro Woche", "Bis zu 40 % weniger"])
    )

    assert geprueft.faellt_weg == []


def test_value_keeps_the_word_time_itself() -> None:
    """„Zeit für“ ist der Zweck des Feldes und keine Zeitangabe."""

    erlaubt = _value(zeit_fuer=["Zeit für Gespräche mit Mietern"] + [
        "Die Abstimmung mit Eigentümern",
        "Die Vorbereitung der Abrechnung",
    ])
    assert Value.model_validate(erlaubt)


# --- Regel 4: die bestehenden Prüfungen gelten weiter -----------------------


def test_internal_reference_is_still_rejected() -> None:
    """Eine Musterkennung darf auch im neuen Vertrag nicht nach außen."""

    with pytest.raises(ValidationError):
        Value.model_validate(
            _value(zeit_fuer=[
                "Siehe Testfall EVAL-C-02",
                "Die Abstimmung mit Eigentümern",
                "Die Vorbereitung der Abrechnung",
            ])
        )


def test_jargon_is_still_rejected() -> None:
    """Unverständliche Wortschöpfungen bleiben aus dem Kundentext heraus.

    Das Schema prüft die Wortschöpfungen aus
    `PROHIBITED_CUSTOMER_LANGUAGE_PATTERN`. Die längere Liste
    `FORBIDDEN_CUSTOMER_TERMS` wird nicht hier geprüft, sondern beim Erzeugen
    in `openai_service`, wo ein Treffer eine Neuerzeugung auslöst statt die
    Antwort zu verwerfen.
    """

    with pytest.raises(ValidationError):
        Value.model_validate(
            _value(zeit_fuer=[
                "Weniger Formulardoppie am Nachschlageort",
                "Die Abstimmung mit Eigentümern",
                "Die Vorbereitung der Abrechnung",
            ])
        )


# --- Der ganze Vertrag ------------------------------------------------------


def test_both_parts_validate_together() -> None:
    """Beide Aufrufe ergeben zusammen ein gültiges Ergebnis."""

    teil_eins = ResultPartOne.model_validate(_part_one(), context=_kontext())
    teil_zwei = ResultPartTwo.model_validate(_part_two(), context=_kontext())
    ganz = Result.model_validate(
        {**_part_one(), **_part_two()}, context=_kontext()
    )
    assert teil_eins.kurzfassung.loesungsname == ganz.kurzfassung.loesungsname
    assert len(teil_zwei.ansichten) == len(ganz.ansichten)
    assert ganz.contract_version == "ergebnis-v6"


def test_unknown_view_type_is_rejected() -> None:
    """Das Modell wählt aus der festen Liste, es erfindet keinen Typ."""

    with pytest.raises(ValidationError):
        ResultPartTwo.model_validate(
            _part_two(ansichten=[
                {
                    "typ": "zeitstrahl",
                    "titel": "Erfundene Ansicht",
                    "beschreibung": "Diesen Typ gibt es nicht.",
                    "daten": {},
                },
                _part_two()["ansichten"][1],
            ]),
            context=_kontext(),
        )


def test_extra_fields_are_rejected() -> None:
    """Kein zusätzliches Feld aus dem Modell, insbesondere kein Markup."""

    with pytest.raises(ValidationError):
        ResultPartOne.model_validate(
            _part_one(html="<div class='card'>…</div>"), context=_kontext()
        )


def test_view_without_matching_data_is_rejected() -> None:
    """Eine Ansicht, deren Makro nichts anzuzeigen hätte, fällt durch."""

    leer = _part_two()
    leer["ansichten"] = [
        {
            "typ": "terminuebersicht",
            "titel": "Der Freitag",
            "beschreibung": "Die Termine des Tages.",
            "daten": {"tag": "Freitag"},
        },
        _part_two()["ansichten"][1],
    ]
    with pytest.raises(ValidationError, match="braucht Werte"):
        ResultPartTwo.model_validate(leer, context=_kontext())

# --- Regel 7: Hebel folgen aus einem Satz des Betriebs ---------------------


def _hebel(**overrides: object) -> dict[str, object]:
    """Ein Hebel, dessen `woraus` wörtlich in ERZAEHLUNG steht."""

    daten: dict[str, object] = {
        "idee": "Nehmen Sie Meldungen künftig an einer Stelle an.",
        "woraus": "muss ich erst suchen, wo die Meldung liegt",
        "warum": "Wer an einer Stelle nachsieht, sucht nicht an dreien.",
        "ohne_technik": True,
    }
    daten.update(overrides)
    return daten


def test_a_lever_quoting_the_narrative_is_kept() -> None:
    """Der Regelfall: Der Satz steht wörtlich da, der Hebel bleibt."""

    teil = ResultPartTwo.model_validate(
        _part_two(hebel=[_hebel()]), context=_kontext()
    )

    assert len(teil.hebel) == 1
    assert teil.hebel[0].ohne_technik is True


def test_an_invented_lever_never_reaches_the_customer() -> None:
    """Ohne Satz aus SEINER Erzählung ist es ein Ratschlag für irgendwen.

    Genau das soll `woraus` verhindern: „Erhöhen Sie Ihre Preise" für einen
    Betrieb, den das Modell zehn Minuten kennt.
    """

    teil = ResultPartTwo.model_validate(
        _part_two(
            hebel=[
                _hebel(
                    idee="Erhöhen Sie Ihre Preise.",
                    woraus="Die Preise sind seit Jahren gleich.",
                )
            ]
        ),
        context=_kontext(),
    )

    assert teil.hebel == []


def test_a_good_lever_survives_a_bad_neighbour() -> None:
    """Verworfen wird der einzelne Hebel, nicht das ganze Ergebnis.

    Dieselbe Behandlung wie bei den Belegen: Ein schlechter Vorschlag darf
    keine fünfzig Sekunden Arbeit mitreissen.
    """

    teil = ResultPartTwo.model_validate(
        _part_two(
            hebel=[
                _hebel(woraus="Das hat der Betrieb nie gesagt."),
                _hebel(),
            ]
        ),
        context=_kontext(),
    )

    assert len(teil.hebel) == 1
    assert teil.hebel[0].idee == "Nehmen Sie Meldungen künftig an einer Stelle an."


def test_no_lever_is_a_valid_result() -> None:
    """Eine leere Liste ist kein Mangel — der Abschnitt entfällt dann."""

    teil = ResultPartTwo.model_validate(_part_two(hebel=[]), context=_kontext())

    assert teil.hebel == []


def test_an_older_result_without_levers_stays_readable() -> None:
    """Der hinterlegte Beispiellauf kennt das Feld nicht.

    Ihm Hebel anzudichten hiesse, einen geprüften Durchlauf zu fälschen.
    """

    ohne_feld = _part_two()
    assert "hebel" not in ohne_feld

    teil = ResultPartTwo.model_validate(ohne_feld, context=_kontext())

    assert teil.hebel == []


def test_more_than_four_levers_are_rejected() -> None:
    """Zwei bis vier. Eine Liste von zehn wäre eine Aufzählung, kein Rat."""

    with pytest.raises(ValidationError):
        ResultPartTwo.model_validate(
            _part_two(hebel=[_hebel() for _ in range(5)]), context=_kontext()
        )


def test_levers_need_the_narrative() -> None:
    """Ohne Erzähltext lässt sich nichts prüfen — dann scheitert es laut."""

    with pytest.raises(ValidationError):
        ResultPartTwo.model_validate(_part_two(hebel=[_hebel()]))

# --- Regel 8: Die Modulzahl folgt dem Betrieb ------------------------------


def _module(anzahl: int) -> list[dict[str, str]]:
    """So viele Module, wie verlangt — das erste auf `jetzt`."""

    return [
        {
            "gruppe": "Eingang",
            "name": f"Baustein {nummer}",
            "beschreibung": "Hält fest, was hereinkommt.",
            "stufe": "jetzt" if nummer == 1 else "danach",
        }
        for nummer in range(1, anzahl + 1)
    ]


def test_three_modules_are_enough_for_a_small_business() -> None:
    """Ein Dreipersonenbetrieb bekommt ein kleineres Zielbild als 450 Einheiten.

    Eine Untergrenze von sechs hiesse, dass der kleinste Betrieb gar nicht
    weniger bekommen kann als der grösste. Gemessen lagen vier von neun
    Fällen über ihrer angemessenen Modulzahl — alle vier zu hoch.
    """

    teil = ResultPartOne.model_validate(
        _part_one(module=_module(3)), context=_kontext()
    )

    assert len(teil.module) == 3


def test_one_module_is_enough_when_that_is_the_answer() -> None:
    """Die Diagnose bestimmt die Größe, nicht das Schema.

    Erst waren sechs Module Pflicht, dann drei. Beide Zahlen standen ohne
    Begründung da und erzwangen bei kleinen Betrieben eine Lösung, die
    größer war als ihr Problem.
    """

    teil = ResultPartOne.model_validate(
        _part_one(module=_module(1)), context=_kontext()
    )

    assert len(teil.module) == 1


def test_ten_modules_are_still_too_many() -> None:
    """Die Obergrenze bleibt bei neun — sie war nie das Problem."""

    with pytest.raises(ValidationError):
        ResultPartOne.model_validate(_part_one(module=_module(10)), context=_kontext())


# --- Der Nutzen eines Moduls ---------------------------------------------


def test_a_module_may_carry_a_benefit() -> None:
    """Zwei bis fuenf Woerter, was der Betrieb davon hat."""

    daten = _part_one()
    daten["module"][0]["nutzen"] = "Weniger Nachfragen"

    with narrative(ERZAEHLUNG):
        teil = ResultPartOne.model_validate(daten)

    assert teil.module[0].nutzen == "Weniger Nachfragen"


def test_a_module_without_a_benefit_still_passes() -> None:
    """Faellt nichts Konkretes ein, bleibt die Zeile leer.

    Eine Floskel waere schlechter als nichts — und aeltere gespeicherte
    Ergebnisse kennen das Feld gar nicht.
    """

    daten = _part_one()
    for modul in daten["module"]:
        modul.pop("nutzen", None)

    with narrative(ERZAEHLUNG):
        teil = ResultPartOne.model_validate(daten)

    assert teil.module[0].nutzen == ""


def test_a_benefit_that_promises_hours_or_euros_is_dropped() -> None:
    """**Die verlockendste Stelle fuer eine erfundene Ersparnis.**

    Niemand hat den Betrieb des Kunden gemessen, also kann niemand
    drei Stunden versprechen. Die Zeile faellt — der Baustein bleibt
    mit Name und Beschreibung stehen, so wie eine schlechte Zeile im
    Wertabschnitt auch nicht den ganzen Lauf kostet.
    """

    daten = _part_one()
    daten["module"][0]["nutzen"] = "Spart 3 Stunden pro Woche"
    daten["module"][1]["nutzen"] = "Weniger Nachfragen"

    with narrative(ERZAEHLUNG):
        teil = ResultPartOne.model_validate(daten)

    assert teil.module[0].nutzen == ""
    assert teil.module[0].name
    assert teil.module[1].nutzen == "Weniger Nachfragen"
