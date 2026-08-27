"""Der Ergebnisvertrag der neuen Ergebnisseite.

Das Modell liefert Daten, die Vorlage liefert Layout. Deshalb steht hier kein
HTML, kein Klassenname und keine Farbe — nur Felder mit Text, Listen und
Auswahlwerten aus festen Listen.

Die Feldnamen sind bewusst deutsch: Sie sind Daten, in die das Modell
deutschen Text schreibt, keine Bezeichner. Die Klassennamen sind englisch
wie im übrigen Code; in Klammern steht jeweils der Abschnitt der
Ergebnisseite, den das Feld füllt.

Vier Regeln werden hier scharf durchgesetzt:

1. Jedes Zitat unter `verstanden.belege` kommt wörtlich in der Erzählung des
   Kunden vor. Dafür braucht die Prüfung den Erzähltext — er wird als
   Validierungskontext übergeben. Ein Zitat, das nicht wörtlich vorkommt, wird
   **einzeln aussortiert**; es reißt nicht mehr das ganze Ergebnis mit. Was
   danach zu tun ist, entscheidet der Aufrufer, nicht der Vertrag.
2. `aufgabenteilung.grenzen` steht nur, wenn der Kunde selbst etwas
   ausgeschlossen hat.
3. `wert.faellt_weg` und `wert.zeit_fuer` enthalten keine Zahl und keine
   Zeitangabe.
4. Die bestehenden Prüfungen gegen interne Verweise und Fachsprache gelten
   über `StrictResultModel` unverändert weiter.
"""

from __future__ import annotations

import contextvars
import logging
import re
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from typing import Annotated, Any, Literal

from pydantic import Field, ValidationInfo, model_validator

from app.schemas import NonEmptyText, StrictResultModel

logger = logging.getLogger(__name__)

# Die Ansichtstypen aus ANSICHTSBIBLIOTHEK.md. Das Modell wählt aus dieser
# Liste; für jeden Typ gibt es ein Jinja-Makro.
VIEW_TYPES = (
    "uebersicht",
    "vorgangsakte",
    "eingangspruefung",
    "nachrichtenverlauf",
    "kundenakte",
    "terminuebersicht",
    "aussenansicht",
    "dokumentenablage",
)
ViewType = Literal[
    "uebersicht",
    "vorgangsakte",
    "eingangspruefung",
    "nachrichtenverlauf",
    "kundenakte",
    "terminuebersicht",
    "aussenansicht",
    "dokumentenablage",
]

# Die Ebenen des Ablaufdiagramms. Mehr Arten gibt es nicht, damit die Vorlage
# jede Ebene sicher rendern kann.
FlowLevel = Literal["eingang", "schluessel", "verzweigung", "nebenast", "ausgang"]

# Statusfarbe in den Ansichten. Das Modell wählt den Status, nie die Farbe.
StatusColour = Literal["rot", "gelb", "gruen", "grau"]

# Wann ein Modul drankommt. Jeder Betrieb bekommt das vollständige Zielbild;
# was sich unterscheidet, ist die Reihenfolge.
Stage = Literal["jetzt", "danach", "spaeter"]

# Zahlen, Prozentzeichen und Zeitangaben. Damit fällt „spart drei Stunden“
# durch, während „Zeit für die Arbeit am Kunden“ stehen bleibt.
NUMBER_PATTERN = re.compile(r"\d|%|\bProzent\b", re.IGNORECASE)
TIME_UNIT_PATTERN = re.compile(
    r"\b("
    r"Sekunden?|Minuten?|Stunden?|Tage?n?|Wochen?|Monate?n?|Jahre?n?|"
    r"täglich|wöchentlich|monatlich|jährlich|stündlich"
    r")\b",
    re.IGNORECASE,
)


# Die Einheiten, in denen jemand seinen Aufwand nennt. Als Wortstamm, damit
# „Minute" und „Minuten" derselbe Fall sind.
ANGABE_STAEMME = (
    "sekund",
    "minut",
    "stund",
    "tag",
    "woch",
    "monat",
    "jahr",
    "prozent",
)

#: Eine Zahl mit ihrer Einheit, so wie ein Mensch sie schreibt.
ANGABE_PATTERN = re.compile(
    r"(\d[\d.,]*)\s*(" + "|".join(ANGABE_STAEMME) + r")\w*",
    re.IGNORECASE,
)


def _angabe_steht_in_der_erzaehlung(text: str, erzaehlung: str) -> bool:
    """Prüft, ob jede Angabe im Text aus der Erzählung stammt.

    Dieselbe Strenge wie bei einem Zitat: Zahl **und** Einheit müssen
    beieinander in seinen eigenen Worten vorkommen. „70 Minuten" besteht,
    wenn er „ungefähr 70 Minuten" gesagt hat. Eine Zahl, die er nie genannt
    hat, besteht nicht — auch dann nicht, wenn sie plausibel klingt.

    Eine Zeitangabe ohne Zahl („spart Stunden", „täglich weniger Aufwand")
    besteht nie: Sie behauptet einen Aufwand, ohne einen zu benennen.
    """

    gefunden = ANGABE_PATTERN.findall(text)
    if not gefunden:
        return False

    klein = erzaehlung.casefold()
    for zahl, stamm in gefunden:
        stamm = stamm.casefold()
        if not any(
            stamm in klein[treffer.end() : treffer.end() + 24]
            for treffer in re.finditer(re.escape(zahl), klein)
        ):
            return False

    # Was neben den geprüften Angaben noch übrig ist, muss ebenfalls ihm
    # gehören. Eine weitere Zahl ohne Einheit ist immer ungedeckt; ein
    # blosses „pro Woche" ist es nicht, wenn er selbst von einer Woche
    # gesprochen hat.
    rest = ANGABE_PATTERN.sub(" ", text)
    if NUMBER_PATTERN.search(rest):
        return False
    return all(
        einheit.casefold()[:4] in klein for einheit in TIME_UNIT_PATTERN.findall(rest)
    )


# Wörter, mit denen jemand etwas ausschließt. Ohne eines davon in der
# Erzählung darf keine selbst genannte Grenze behauptet werden.
EXCLUSION_PATTERN = re.compile(
    r"\b("
    r"nicht|nichts|kein|keine|keinen|keinem|keiner|keines|niemals|nie|"
    r"ungern|weigere|verzichte|tabu|ausgeschlossen|auf keinen Fall"
    r")\b",
    re.IGNORECASE,
)

NARRATIVE_CONTEXT_KEY = "erzaehlung"

#: Die Erzählung des Kunden für die Dauer eines Modellaufrufs.
#:
#: Die OpenAI-Schnittstelle baut das Ergebnismodell selbst und reicht dabei
#: keinen Validierungskontext durch. Ohne diese Variable könnte die
#: Zitatprüfung beim Erzeugen nicht greifen — genau dort, wo sie gebraucht
#: wird. `model_validate(..., context=...)` funktioniert weiterhin und hat
#: Vorrang.
_narrative: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "result_narrative",
    default=None,
)


# Was die Zitatprüfung aussortiert hat. Der Aufrufer muss es erfahren, um
# gezielt nachfragen zu können — und Pydantic baut das Modell selbst, kann
# also nichts zurückgeben. Deshalb hier, neben der Erzählung.
_aussortierte_zitate: contextvars.ContextVar[list[str] | None] = contextvars.ContextVar(
    "result_rejected_quotes",
    default=None,
)


#: Die Modulnamen, auf die sich Aufruf 3 und 4 berufen dürfen — samt der
#: gewählten Familien. Wie `_narrative` eine Kontextvariable, weil die
#: OpenAI-Schnittstelle das Modell selbst baut und keinen
#: Validierungskontext durchreicht.
_freigegebene_module: contextvars.ContextVar[tuple[str, ...] | None] = (
    contextvars.ContextVar("freigegebene_module", default=None)
)
_gewaehlte_familien: contextvars.ContextVar[tuple[str, ...] | None] = (
    contextvars.ContextVar("gewaehlte_familien", default=None)
)


def _vergleichbarer_name(text: str) -> str:
    """Zwei Modulnamen vergleichbar machen, ohne sie zu verändern."""

    return " ".join(str(text).split()).casefold()


@contextmanager
def freigegebene_module(
    namen: Sequence[str], familien: Sequence[str] = ()
) -> Iterator[None]:
    """Stellt für die Dauer eines Aufrufs, worauf er sich berufen darf.

    Ohne diesen Rahmen prüft nichts: Aufruf 3 und 4 dürfen keine Ansicht,
    kein System, keine Ebene und keinen Schritt erfinden, der zu keinem
    freigegebenen Modul gehört.
    """

    marke = _freigegebene_module.set(tuple(namen))
    marke_familien = _gewaehlte_familien.set(tuple(familien))
    try:
        yield
    finally:
        _freigegebene_module.reset(marke)
        _gewaehlte_familien.reset(marke_familien)


def _eindeutiges_modul(bezug: str, erlaubt: Sequence[str]) -> str | None:
    """Findet das gemeinte Modul — auch wenn der Name gekürzt wurde.

    Heisst ein Modul „Morgenliste mit Verantwortlichkeiten" und die Ansicht
    beruft sich auf „Morgenliste", dann meint sie dieses Modul. Ein exakter
    Zeichenvergleich würde das zurückweisen und den ganzen Lauf mitreissen —
    an einer Schreibweise, nicht an einer erfundenen Funktion.

    Geprüft wird trotzdem Herkunft, nicht Ähnlichkeit: Der Bezug muss in
    genau **einem** freigegebenen Namen enthalten sein oder ihn enthalten.
    Passt keiner, ist es ein fremdes Modul. Passen mehrere, ist unklar
    welches gemeint war — und Unklarheit gilt hier als Fehler.
    """

    gesucht = _vergleichbarer_name(bezug)
    # Der Regelfall: die Nummer aus `MODULE_DIESER_LOESUNG`.
    if gesucht.isdigit():
        stelle = int(gesucht)
        return erlaubt[stelle - 1] if 1 <= stelle <= len(erlaubt) else None
    for name in erlaubt:
        if _vergleichbarer_name(name) == gesucht:
            return name
    kandidaten = [
        name
        for name in erlaubt
        if gesucht and (
            gesucht in _vergleichbarer_name(name)
            or _vergleichbarer_name(name) in gesucht
        )
    ]
    if len(kandidaten) == 1:
        logger.info(
            "result.module_ref_shortened bezug=%r modul=%r", bezug, kandidaten[0]
        )
        return kandidaten[0]
    return None


def _pruefe_modulbezug(bezuege: Sequence[str], wofuer: str) -> list[str]:
    """Jeder Bezug muss auf ein freigegebenes Modul zeigen.

    Kein Textverständnis, nur Herkunft: Der Bezug muss eines der bereits
    geprüften Module eindeutig bezeichnen. Ist kein Rahmen gesetzt — etwa
    beim Lesen eines gespeicherten Ergebnisses —, wird nicht geprüft.
    """

    erlaubt = _freigegebene_module.get()
    if erlaubt is None:
        return list(bezuege)
    getroffen: list[str] = []
    fremd: list[str] = []
    for bezug in bezuege:
        treffer = _eindeutiges_modul(bezug, erlaubt)
        if treffer is None:
            fremd.append(bezug)
        elif treffer not in getroffen:
            getroffen.append(treffer)
    if fremd:
        raise ValueError(
            f"{wofuer} beruft sich auf {fremd}. Das ist kein Modul dieser "
            f"Lösung. Erlaubt sind: {list(erlaubt)}."
        )
    if not getroffen:
        raise ValueError(
            f"{wofuer} nennt kein Modul. Jede Ansicht, jedes System, jede "
            "Ebene und jeder Schritt gehört zu einem der Module."
        )
    return getroffen


#: Was nach einer erfundenen Zahl aussieht. SF-25 beschreibt eine Lösung,
#: die Beträge später **berechnet** — sie stehen nicht im Ergebnis.
GELDBETRAG = re.compile(
    r"(?:€|\bEUR\b|\bEuro\b)\s*-?\d|\d[\d.,]*\s*(?:€|\bEUR\b|\bEuro\b)",
    re.IGNORECASE,
)


def _pruefe_keine_geldbetraege(werte: Any, wofuer: str) -> None:
    """Bei gewählter SF-25: keine erfundenen Beträge im Kundentext.

    Die Familie darf beschrieben werden — dass sie Deckungsbeitrag und
    Liquidität aus strukturierten Daten ermittelt, ist ihre Aussage. Was
    sie nicht darf: eine Zahl nennen, die niemand gerechnet hat.
    """

    if "SF-25" not in (_gewaehlte_familien.get() or ()):
        return
    for text in _plain_texts(werte):
        if GELDBETRAG.search(text):
            raise ValueError(
                f"{wofuer} nennt einen Geldbetrag: {text!r}. Die Lösung "
                "rechnet solche Werte später aus den Daten des Betriebs — "
                "hier darf keine Zahl stehen, die niemand gerechnet hat."
            )


@contextmanager
def narrative(erzaehlung: str) -> Iterator[None]:
    """Stellt die Erzählung für die Dauer eines Modellaufrufs bereit.

    Legt zugleich die Liste an, in der die Zitatprüfung vermerkt, was sie
    aussortiert hat. Sie beginnt bei jedem Aufruf leer.
    """

    marke = _narrative.set(erzaehlung)
    zettel = _aussortierte_zitate.set([])
    try:
        yield
    finally:
        _narrative.reset(marke)
        _aussortierte_zitate.reset(zettel)


def rejected_quotes() -> list[str]:
    """Die Zitate, die in diesem Aufruf nicht wörtlich vorkamen.

    Nur innerhalb von `narrative()` gefüllt. Ausserhalb ist die Liste leer —
    dann hat auch keine Prüfung stattgefunden.
    """

    vermerkt = _aussortierte_zitate.get()
    return list(vermerkt or [])


def _current_narrative(info: ValidationInfo) -> str | None:
    """Die Erzählung aus dem Validierungskontext oder aus der Kontextvariablen."""

    kontext = info.context or {}
    aus_kontext = kontext.get(NARRATIVE_CONTEXT_KEY)
    if aus_kontext is not None:
        return str(aus_kontext)
    laufend = _narrative.get()
    return None if laufend is None else str(laufend)


def _plain_texts(value: Any) -> list[str]:
    """Sammelt alle Zeichenketten aus einer verschachtelten Struktur."""

    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _plain_texts(item)]
    if isinstance(value, (list, tuple)):
        return [text for item in value for text in _plain_texts(item)]
    return []


def normalize_for_quote_match(value: str) -> str:
    """Macht zwei Texte vergleichbar, ohne die Wörter zu verändern.

    Das Modell gibt Zitate manchmal mit anderen Anführungszeichen oder mit
    zusammengefassten Leerzeichen zurück. Das ist kein Umformulieren und soll
    die Prüfung nicht auslösen. Alles andere — ein geändertes Wort, eine
    andere Beugung — fällt weiterhin durch.
    """

    ersetzungen = {
        "„": '"', "“": '"', "”": '"', "«": '"', "»": '"',
        "‘": "'", "’": "'",
        # Alles, was wie ein Bindestrich aussieht, wird einer. Das Modell
        # schreibt "E‑Mail" mit geschütztem Bindestrich, die Erzählung mit
        # einem gewöhnlichen — gleiche Wörter, anderes Zeichen.
        "–": "-", "—": "-", "‐": "-", "‑": "-", "−": "-",
        # Und alles, was wie ein Leerzeichen aussieht, wird eins.
        " ": " ", " ": " ", " ": " ", " ": " ",
    }
    for alt, neu in ersetzungen.items():
        value = value.replace(alt, neu)
    gefasst = " ".join(value.split()).casefold()
    # Umschliessende Anführungszeichen gehören zum Zitieren, nicht zum Zitat.
    # Das Modell setzt sie gern dazu; in der Erzählung stehen sie nicht. In
    # zehn gemessenen Läufen sind daran zwei von acht Belegen gescheitert,
    # ohne dass ein Wort anders war.
    return gefasst.strip("\"'").strip()


class Evidence(StrictResultModel):
    """Ein wörtliches Zitat aus der Erzählung mit seiner Bedeutung (`belege`)."""

    zitat: NonEmptyText
    bedeutung: NonEmptyText


class Summary(StrictResultModel):
    """Die Kurzfassung ganz oben auf der Seite (`kurzfassung`)."""

    engpass_satz: NonEmptyText
    loesungsname: NonEmptyText
    relevante_module: Annotated[list[NonEmptyText], Field(max_length=5)]


# Zwei Belege sind die Untergrenze, unter der der Abschnitt nicht mehr trägt:
# Ein einzelnes Zitat wirkt wie ein Zufallsfund, nicht wie Zuhören.
MINIMUM_EVIDENCE = 2


class Understanding(StrictResultModel):
    """Was aus der Erzählung verstanden wurde (`verstanden`).

    Der Abschnitt wirkt nicht durch die Diagnose, sondern dadurch, dass der
    Kunde seine eigenen Sätze wiedererkennt. Deshalb die harte Zitatprüfung.
    """

    engpass_absatz: NonEmptyText
    # Keine Untergrenze auf dem Feld: Die Prüfung unten sortiert aus, und was
    # danach zu wenig ist, entscheidet der Aufrufer. Eine Untergrenze hier
    # würde das Aussortieren wieder in ein Scheitern verwandeln.
    belege: Annotated[list[Evidence], Field(max_length=3)]
    eckdaten: Annotated[list[NonEmptyText], Field(min_length=3, max_length=5)]

    @model_validator(mode="after")
    def quotes_are_checked_one_by_one(self, info: ValidationInfo) -> Understanding:
        """Sortiert jedes Zitat aus, das nicht wörtlich in der Erzählung steht.

        Früher riss ein einziges ungenaues Zitat das ganze Ergebnis mit —
        fünfzig Sekunden Arbeit für ein Wort. Geprüft wird weiterhin genauso
        scharf, aber Zitat für Zitat: Das schlechte fällt, die guten bleiben.

        Ohne Erzähltext lässt sich gar nichts prüfen. Dann schlägt die
        Validierung weiterhin fehl, statt die Prüfung stillschweigend zu
        überspringen — ein ungeprüftes Zitat ist genau der Fall, den diese
        Regel verhindern soll.
        """

        erzaehlung = _current_narrative(info)
        if erzaehlung is None:
            raise ValueError(
                "Zitate lassen sich ohne den Erzähltext nicht prüfen. Übergib "
                f"ihn als Kontext unter '{NARRATIVE_CONTEXT_KEY}' oder über "
                "narrative()."
            )
        haystack = normalize_for_quote_match(erzaehlung)
        behalten: list[Evidence] = []
        for beleg in self.belege:
            if normalize_for_quote_match(beleg.zitat) in haystack:
                behalten.append(beleg)
                continue
            logger.warning(
                "result.quote_rejected zitat=%r grund=nicht_woertlich", beleg.zitat
            )
            vermerkt = _aussortierte_zitate.get()
            if vermerkt is not None:
                vermerkt.append(beleg.zitat)
        self.belege = behalten
        return self


class FlowNode(StrictResultModel):
    """Ein Kasten im Ablaufdiagramm."""

    text: NonEmptyText
    kategorie: NonEmptyText


class FlowStage(StrictResultModel):
    """Eine Ebene des Ablaufdiagramms (`zielbild.ablauf`)."""

    art: FlowLevel
    label: NonEmptyText
    knoten: Annotated[list[FlowNode], Field(min_length=1, max_length=6)]


class TargetPicture(StrictResultModel):
    """Die empfohlene Ziel-Lösung und ihr Ablauf (`zielbild`)."""

    name: NonEmptyText
    beschreibung: NonEmptyText
    # Keine Untergrenze: Ein Betrieb, dessen Arbeit in einer Ebene
    # zusammenläuft, bekommt eine Ebene. Zwei zu verlangen erzwingt eine
    # Verzweigung, die es nicht gibt.
    ablauf: Annotated[list[FlowStage], Field(max_length=6)]


class Comparison(StrictResultModel):
    """Derselbe Vorgang heute und künftig (`vergleich`)."""

    # Fünf Zeilen waren eine Zahl aus dem Entwurf. Ein einfacher Ablauf hat
    # drei Schritte, und drei erfundene dazu wären keine Beschreibung mehr.
    heute: Annotated[list[NonEmptyText], Field(max_length=7)]
    kuenftig: Annotated[list[NonEmptyText], Field(max_length=7)]


class Module(StrictResultModel):
    """Ein Baustein der Ziel-Lösung (`module`).

    Die Module stehen gleichrangig nebeneinander. `gruppe` zeigt den
    Zusammenhang, `stufe` sagt, wann der Baustein drankommt.
    """

    gruppe: NonEmptyText
    name: NonEmptyText
    beschreibung: NonEmptyText
    #: **Was der Betrieb davon hat**, in wenigen Wörtern.
    #:
    #: Die Beschreibung sagt, was der Baustein tut. Das hier sagt,
    #: warum ihn das interessieren sollte — zwei verschiedene Fragen,
    #: und die zweite ist die, die verkauft.
    #:
    #: Leer mit Vorgabe, damit ältere gespeicherte Ergebnisse lesbar
    #: bleiben. Eine Zeit- oder Geldersparnis steht hier nicht: Die
    #: alte Regel gegen erfundene Zahlen gilt für den ganzen
    #: Kundentext und damit auch für dieses Feld.
    nutzen: str = ""
    #: Wann dieser Baustein drankommt. Am Modul selbst und nicht in einer
    #: Liste daneben: So kann er weder vergessen noch zweimal eingeordnet
    #: werden — das Schema erzwingt die Zuordnung, statt sie zu prüfen.
    #:
    #: Nullbar mit Vorgabe, damit ein gespeichertes Ergebnis von vor dem
    #: 19.08. lesbar bleibt. Bei neuen Läufen verlangt das strenge Schema
    #: einen der drei Werte.
    stufe: Stage | None = None
    #: **Woher dieses Modul kommt.** Intern, der Kunde sieht es nie.
    #:
    #: Leer mit Vorgabe, damit älter gespeicherte Ergebnisse lesbar bleiben
    #: — der hinterlegte Beispiellauf kennt diese Felder nicht. Bei der
    #: Erzeugung verlangt `SelectedModule` beide, und der Katalog prüft sie.
    solution_family_ids: list[str] = []
    baustein_refs: list[str] = []

    @model_validator(mode="after")
    def the_benefit_promises_no_saving(
        self, info: ValidationInfo | None = None
    ) -> Module:
        """Ein Nutzen mit einer Zahl fällt weg — ausser sie gehört ihm.

        „Spart drei Stunden pro Woche" ist keine Zusage, die jemand
        halten kann: Niemand hat den Betrieb des Kunden gemessen, und
        ein Sprachmodell erfindet eine überzeugend aussehende Ersparnis,
        wenn man es lässt.

        **Seine eigene Angabe ist etwas anderes.** Sagt er „ungefähr 70
        Minuten in einer normalen Woche", dann ist „70 Minuten pro Woche"
        kein Versprechen von uns, sondern sein Satz — und er überzeugt
        mehr als eine fremde Zahl, weil er mit sich selbst nicht streiten
        kann. Deshalb keine Lockerung, sondern eine Ausnahme mit
        Beweispflicht: Zahl und Einheit müssen wörtlich in der Erzählung
        stehen, genau wie bei einem Zitat.

        Ohne Erzählung im Kontext bleibt es beim Wegwerfen. Was sich
        nicht prüfen lässt, wird nicht geglaubt.

        Weggeworfen wird die Zeile, nicht das Ergebnis: Der Baustein
        bleibt mit Name und Beschreibung stehen, nur ohne die
        Behauptung. Genauso wie im Wertabschnitt und bei den
        Zitaten — eine schlechte Zeile kostet nicht den ganzen Lauf.
        """

        if not self.nutzen:
            return self
        if not (
            NUMBER_PATTERN.search(self.nutzen)
            or TIME_UNIT_PATTERN.search(self.nutzen)
        ):
            return self

        erzaehlung = _current_narrative(info) if info is not None else None
        if erzaehlung is None:
            erzaehlung = _narrative.get()
        if erzaehlung and _angabe_steht_in_der_erzaehlung(
            self.nutzen, str(erzaehlung)
        ):
            logger.info(
                "result.benefit_kept_own_figure modul=%r nutzen=%r",
                self.name,
                self.nutzen,
            )
            return self

        logger.warning(
            "result.benefit_dropped modul=%r nutzen=%r",
            self.name,
            self.nutzen,
        )
        self.nutzen = ""
        return self


class LabelValue(StrictResultModel):
    """Ein beschriftetes Feld in einer Ansicht."""

    label: NonEmptyText
    wert: NonEmptyText


class StatusLine(StrictResultModel):
    """Eine Zeile mit Statusfarbe in der Übersicht."""

    text: NonEmptyText
    status: StatusColour


class Badge(StrictResultModel):
    """Ein Statusabzeichen an einer Akte."""

    text: NonEmptyText
    status: StatusColour


class HistoryEntry(StrictResultModel):
    """Ein Eintrag im Verlauf einer Vorgangsakte."""

    zeit: NonEmptyText
    text: NonEmptyText


class InboxMessage(StrictResultModel):
    """Eine eingegangene Nachricht mit ihrer erkannten Einordnung."""

    absender: NonEmptyText
    zeit: NonEmptyText
    text: NonEmptyText
    marken: Annotated[list[NonEmptyText], Field(min_length=1, max_length=4)]


class ChatBubble(StrictResultModel):
    """Eine Sprechblase im Nachrichtenverlauf."""

    seite: Literal["kunde", "betrieb"]
    text: NonEmptyText
    zeit: NonEmptyText


class Appointment(StrictResultModel):
    """Ein Eintrag in der Terminübersicht."""

    zeit: NonEmptyText
    person: NonEmptyText
    leistung: NonEmptyText
    status: StatusColour


class OutsideStep(StrictResultModel):
    """Ein Schritt in der Außenansicht, erreicht oder noch offen."""

    text: NonEmptyText
    erreicht: bool


class DocumentEntry(StrictResultModel):
    """Ein Eintrag in der Dokumentenablage."""

    typ: NonEmptyText
    name: NonEmptyText
    datum: NonEmptyText
    zuordnung: NonEmptyText


class ViewData(StrictResultModel):
    """Die Werte einer Beispielansicht.

    Jedes Feld gehört zu einem oder mehreren Ansichtstypen; das Makro liest
    nur die, die es kennt. Alle Felder sind wahlfrei, weil jede Ansicht nur
    einen Teil davon braucht. Ein freies Objekt wäre einfacher gewesen — die
    Structured-Outputs-Schnittstelle lässt das aber nicht zu, und feste Felder
    machen zugleich unmöglich, dass Layout aus dem Modell kommt.
    """

    # Übersicht
    kennzahlen: list[LabelValue] | None = None
    zeilen: list[StatusLine] | None = None
    haupttext: str | None = None
    untertext: str | None = None
    hinweis: str | None = None
    # Vorgangs- und Kundenakte
    name: str | None = None
    abzeichen: Badge | None = None
    felder: list[LabelValue] | None = None
    verlauf: list[HistoryEntry] | None = None
    dateien: list[NonEmptyText] | None = None
    notiz: str | None = None
    vorgaenge: list[NonEmptyText] | None = None
    # Eingangsprüfung und Nachrichtenverlauf
    nachrichten: list[InboxMessage] | None = None
    blasen: list[ChatBubble] | None = None
    # Terminübersicht
    tag: str | None = None
    eintraege_termine: list[Appointment] | None = None
    # Außenansicht
    schritte: list[OutsideStep] | None = None
    statussatz: str | None = None
    # Dokumentenablage
    eintraege_dokumente: list[DocumentEntry] | None = None


#: Welches Feld eine Ansicht mindestens braucht, damit ihr Makro etwas zu
#: zeigen hat. Fehlt es, ist die Ansicht leer und wird zurückgewiesen.
REQUIRED_VIEW_FIELDS: dict[str, tuple[str, ...]] = {
    "uebersicht": ("zeilen",),
    "vorgangsakte": ("felder",),
    "eingangspruefung": ("nachrichten",),
    "nachrichtenverlauf": ("blasen",),
    "kundenakte": ("felder",),
    "terminuebersicht": ("eintraege_termine",),
    "aussenansicht": ("schritte",),
    "dokumentenablage": ("eintraege_dokumente",),
}


class View(StrictResultModel):
    """Eine Beispielansicht aus der Ansichtsbibliothek (`ansichten`).

    Das Modell wählt einen Typ aus der festen Liste und füllt Beschriftungen
    und Werte. Es schreibt kein Layout — für jeden Typ gibt es ein
    Jinja-Makro, und ein unbekannter Typ kommt hier gar nicht erst durch.
    """

    typ: ViewType
    titel: NonEmptyText
    beschreibung: NonEmptyText
    daten: ViewData
    #: Welches Modul diese Ansicht zeigt. Intern, nie auf der Seite.
    module_refs: list[str] = []

    @model_validator(mode="after")
    def data_must_fit_the_type(self) -> View:
        """Weist eine Ansicht zurück, deren Makro nichts anzuzeigen hätte."""

        for feld in REQUIRED_VIEW_FIELDS[self.typ]:
            if not getattr(self.daten, feld, None):
                raise ValueError(
                    f"Die Ansicht „{self.typ}“ braucht Werte in „{feld}“."
                )
        self.module_refs = _pruefe_modulbezug(
            self.module_refs, f"Die Ansicht „{self.titel}“"
        )
        _pruefe_keine_geldbetraege(
            self.daten.model_dump(), f"Die Ansicht „{self.titel}“"
        )
        return self


class Boundary(StrictResultModel):
    """Eine Grenze, die der Kunde selbst gezogen hat (`grenzen`)."""

    titel: NonEmptyText
    erlaeuterung: NonEmptyText


class Division(StrictResultModel):
    """Was das System übernimmt und was beim Menschen bleibt."""

    system: Annotated[list[NonEmptyText], Field(max_length=8)]
    mensch: Annotated[list[NonEmptyText], Field(max_length=6)]
    grenzen: Annotated[list[Boundary], Field(max_length=3)] = []

    @model_validator(mode="after")
    def boundaries_need_a_self_statement(self, info: ValidationInfo) -> Division:
        """Lässt Grenzen nur zu, wenn der Kunde selbst etwas ausgeschlossen hat.

        Geprüft wird, ob die Erzählung überhaupt eine Ausschlussformulierung
        enthält. Das ist bewusst grob: Es fängt den Fall, dass allgemeine
        Hinweise als selbst genannte Grenze ausgegeben werden, und lässt
        ansonsten durch. Ob die Grenze inhaltlich zur Aussage passt, kann eine
        Regel nicht entscheiden.
        """

        if not self.grenzen:
            return self
        erzaehlung = _current_narrative(info)
        if erzaehlung is None:
            raise ValueError(
                "Selbst genannte Grenzen lassen sich ohne den Erzähltext nicht "
                f"prüfen. Übergib ihn als Kontext unter '{NARRATIVE_CONTEXT_KEY}' "
                "oder über narrative()."
            )
        if EXCLUSION_PATTERN.search(erzaehlung) is None:
            raise ValueError(
                "Der Kunde hat nichts ausgeschlossen. Dann bleibt die Liste der "
                "Grenzen leer, statt allgemeine Hinweise zu erfinden."
            )
        return self


class Value(StrictResultModel):
    """Was wegfällt und wofür Zeit entsteht (`wert`).

    Ohne Zahlen: Eine Zeit- oder Geldersparnis über den Betrieb des Kunden
    lässt sich aus einem Gespräch nicht belegen.
    """

    faellt_weg: Annotated[list[NonEmptyText], Field(max_length=8)]
    zeit_fuer: Annotated[list[NonEmptyText], Field(max_length=5)]

    @model_validator(mode="after")
    def no_numbers_or_durations(self) -> Value:
        """Sortiert jede Zeile mit Zahl, Prozent- oder Zeitangabe aus.

        **Zeile für Zeile, nicht der ganze Abschnitt.** Genau wie bei den
        Zitaten: Eine Zeile, die eine Ersparnis behauptet, fällt — die
        übrigen bleiben. Vorher riss eine einzige solche Zeile drei Minuten
        Arbeit mit, obwohl alles andere in Ordnung war.

        Die Zusage ändert sich dadurch nicht, sie wird härter: Eine Zahl
        über den Betrieb des Kunden kommt hier **nie** heraus, auch nicht
        über einen zweiten Versuch, in dem sie zufällig durchrutscht.
        """

        def sauber(zeilen: list[str]) -> list[str]:
            behalten: list[str] = []
            for zeile in zeilen:
                if NUMBER_PATTERN.search(zeile) is not None:
                    logger.warning(
                        "result.value_line_dropped grund=zahl zeile=%r", zeile
                    )
                    continue
                if TIME_UNIT_PATTERN.search(zeile) is not None:
                    logger.warning(
                        "result.value_line_dropped grund=zeitangabe zeile=%r", zeile
                    )
                    continue
                behalten.append(zeile)
            return behalten

        self.faellt_weg = sauber(list(self.faellt_weg))
        self.zeit_fuer = sauber(list(self.zeit_fuer))
        return self


class ImplementationStep(StrictResultModel):
    """Ein Schritt der Umsetzung (`umsetzung`).

    Kein blosser Text, sondern ein Objekt mit Herkunft: Weil die späteren
    Aufrufe nichts hinzufügen dürfen, trägt jeder Schritt das Modul, aus
    dem er folgt.
    """

    text: NonEmptyText
    module_refs: list[str] = []

    @model_validator(mode="before")
    @classmethod
    def a_plain_sentence_is_a_step(cls, wert: object) -> object:
        """Ein älter gespeichertes Ergebnis führt hier blossen Text.

        Der hinterlegte Beispiellauf ist so abgelegt. Ihm nachträglich eine
        Herkunft anzudichten hiesse, einen geprüften Durchlauf zu fälschen —
        also bleibt er lesbar, mit leerer Herkunft.
        """

        return {"text": wert} if isinstance(wert, str) else wert

    @model_validator(mode="after")
    def the_step_belongs_to_a_module(self) -> ImplementationStep:
        """Kein Schritt ohne Modul."""

        self.module_refs = _pruefe_modulbezug(
            self.module_refs, f"Der Umsetzungsschritt „{self.text[:40]}“"
        )
        return self


class ConnectedSystem(StrictResultModel):
    """Ein System, das verbunden würde (`systeme`)."""

    name: NonEmptyText
    umgang: NonEmptyText
    #: Zu welchem Modul dieses System gehört. Intern.
    module_refs: list[str] = []

    @model_validator(mode="after")
    def the_system_belongs_to_a_module(self) -> ConnectedSystem:
        """Kein System ohne Modul, das es anfasst."""

        self.module_refs = _pruefe_modulbezug(
            self.module_refs, f"Das System „{self.name}“"
        )
        return self


class ArchitectureLayer(StrictResultModel):
    """Eine Schicht der empfohlenen Umsetzungsarchitektur (`architektur`)."""

    ebene: NonEmptyText
    beschreibung: NonEmptyText
    #: Aus welchem Modul diese Ebene folgt. Intern, der Kunde sieht es nie.
    module_refs: list[str] = []

    @model_validator(mode="after")
    def the_layer_belongs_to_a_module(self) -> ArchitectureLayer:
        """Keine Ebene ohne Modul."""

        self.module_refs = _pruefe_modulbezug(
            self.module_refs, f"Die Architekturebene „{self.ebene}“"
        )
        return self


class FollowUp(StrictResultModel):
    """Die eine Rückfrage, wenn eine Antwort das Ergebnis verändern würde."""

    frage: NonEmptyText
    warum: NonEmptyText


class SelectedModule(Module):
    """Ein Modul, das auf den Katalog zurückgeführt ist — Aufruf 2.

    Der Unterschied zu `Module`: Hier sind Herkunftsfelder Pflicht. Ein
    Modul ohne gültige Familie und ohne zulässigen Baustein ist eine
    Erfindung, und Erfindungen sind genau das, was dieser Weg verhindert.
    """

    solution_family_ids: Annotated[list[str], Field(min_length=1, max_length=3)]
    baustein_refs: Annotated[list[str], Field(min_length=1, max_length=4)]


class Diagnose(StrictResultModel):
    """Was der Betrieb erzählt hat und woran es liegt — Aufruf 1.

    **Ohne einen einzigen Lösungsbegriff.** Stünden Lösungsname, Zielbild
    und Module schon hier, wäre die Lösung fest, bevor irgendein Katalog
    gefragt ist. Wer die Lösung kennt, diagnostiziert auf sie hin.
    """

    engpass_satz: NonEmptyText
    verstanden: Understanding
    #: Der Vorgang, wie er heute läuft. Das sind Kundenfakten und gehören
    #: deshalb hierher, nicht zur Lösung.
    vergleich_heute: Annotated[list[NonEmptyText], Field(max_length=7)]
    rueckfrage: FollowUp | None = None


class Zielarchitektur(StrictResultModel):
    """Die ausgewählte Lösung und ihre Formulierung — Aufruf 2.

    Das Modell wählt **Kennungen** aus dem freigegebenen Katalog und setzt
    daraus eine Lösung für diesen Betrieb zusammen. Frei ist die Sprache:
    Name, Beschreibung, Reihenfolge, Zielbild. Nicht frei ist, **was**
    angeboten wird.

    Die Prüfung unten ist serverseitig und hart. Sie lässt kein Modul
    durch, das sich nicht auf eine ausgewählte Familie und einen ihrer
    Bausteine zurückführen lässt.
    """

    #: Passt überhaupt etwas aus dem Katalog? `False` ist eine gültige
    #: Antwort und besser als eine erfundene Lösung.
    catalog_fit: bool
    #: Braucht dieser Betrieb überhaupt neue Technik? Wer ein geeignetes
    #: System hat und es nur nicht konsequent nutzt, braucht keins.
    recommend_new_technology: bool
    begruendung: NonEmptyText
    selected_solution_family_ids: Annotated[list[str], Field(max_length=8)]
    loesungsname: NonEmptyText
    relevante_module: Annotated[list[NonEmptyText], Field(max_length=5)]
    warum_diese_loesung: NonEmptyText
    zielbild: TargetPicture
    vergleich_kuenftig: Annotated[list[NonEmptyText], Field(max_length=7)]
    module: Annotated[list[SelectedModule], Field(max_length=9)]

    @model_validator(mode="after")
    def every_module_comes_from_the_catalogue(self) -> Zielarchitektur:
        """Das Geländer. Jede Kennung und jeder Baustein wird geprüft.

        Verstösse sind Fehler, keine Warnungen: Ein Ergebnis mit einem
        erfundenen Modul darf nicht entstehen. Der Aufruf wird danach
        einmal wiederholt — das ist der eingebaute zweite Versuch.

        Ohne Katalogtreffer (`catalog_fit` ist falsch) bleibt die Liste
        leer. Auch das ist ein gültiges Ergebnis.
        """

        from app import solution_catalog

        gueltig, ungueltig = solution_catalog.pruefe_auswahl(
            self.selected_solution_family_ids
        )
        if ungueltig:
            raise ValueError(
                "Diese Lösungsfamilien gibt es im freigegebenen Katalog "
                f"nicht: {ungueltig}. Wähle nur Kennungen aus der Liste."
            )
        if not self.catalog_fit:
            if self.module or gueltig:
                raise ValueError(
                    "catalog_fit ist falsch, aber es stehen Familien oder "
                    "Module im Ergebnis. Beides zusammen geht nicht."
                )
            return self
        if not gueltig:
            raise ValueError(
                "Keine gültige Lösungsfamilie ausgewählt. Wenn nichts "
                "passt, setze catalog_fit auf false."
            )
        if not self.module:
            raise ValueError(
                "Es wurden Familien gewählt, aber kein Modul daraus gebaut. "
                "Wenn nichts passt, setze catalog_fit auf false."
            )
        self.selected_solution_family_ids = gueltig
        for modul in self.module:
            eigene, fremde = solution_catalog.pruefe_auswahl(
                modul.solution_family_ids
            )
            if fremde:
                raise ValueError(
                    f"Das Modul „{modul.name}“ nennt eine Familie, die es "
                    f"nicht gibt: {fremde}."
                )
            ausserhalb = [k for k in eigene if k not in gueltig]
            if ausserhalb:
                raise ValueError(
                    f"Das Modul „{modul.name}“ nennt {ausserhalb}, aber "
                    "diese Familie wurde nicht ausgewählt."
                )
            modul.solution_family_ids = eigene
            getroffen = [
                baustein
                for baustein in modul.baustein_refs
                if solution_catalog.pruefe_baustein(baustein, eigene)
            ]
            if not getroffen:
                erlaubt = solution_catalog.bausteine_von(eigene)
                raise ValueError(
                    f"Das Modul „{modul.name}“ nennt keinen Baustein seiner "
                    f"Familien. Erlaubt sind: {erlaubt}."
                )
            modul.baustein_refs = getroffen
        return self


class ResultPartOne(StrictResultModel):
    """Der obere Teil der Ergebnisseite — der erste Modellaufruf.

    Dieser Teil wird sofort gerendert, während der zweite noch entsteht.
    """

    kurzfassung: Summary
    verstanden: Understanding
    warum_diese_loesung: NonEmptyText
    zielbild: TargetPicture
    vergleich: Comparison
    # **Die Diagnose bestimmt die Größe, nicht das Schema.**
    #
    # Erst waren es sechs Module Mindestmenge, dann drei. Beide Zahlen
    # standen ohne Begründung da, und beide erzwangen bei kleinen Betrieben
    # eine Lösung, die größer war als ihr Problem. Ein Fall, dem ein Modul
    # hilft, bekommt ein Modul; ein Fall ohne Katalogtreffer bekommt keins.
    # Die Obergrenze bleibt — sie schützt vor einer Aufzählung statt einer
    # Lösung.
    module: Annotated[list[Module], Field(max_length=9)]
    # `None` ist der Normalfall und kein Mangel: Ein Agent, der nur fragt,
    # wenn er etwas braucht, wirkt klüger als einer, der immer fragt. Der
    # Vorgabewert steht hier, damit ein älteres gespeichertes Ergebnis ohne
    # dieses Feld weiterhin lesbar bleibt — etwa der hinterlegte Beispiellauf.
    rueckfrage: FollowUp | None = None


class Lever(StrictResultModel):
    """Was der Betrieb ohne Technik ändern könnte (`hebel`).

    Nicht jede Verbesserung muss gebaut werden. Eine andere Regel, ein
    anderer Preis, eine andere Reihenfolge kosten nichts — und wer zuerst
    etwas gibt, das nichts kostet, dem glaubt man den bezahlten Teil eher.
    """

    idee: NonEmptyText
    #: Der Satz aus **seiner** Erzählung, aus dem die Idee folgt. Ohne
    #: dieses Feld erfindet das Modell Ratschläge für einen Betrieb, den es
    #: zehn Minuten kennt. Geprüft wie ein Zitat in `verstanden.belege`.
    woraus: NonEmptyText
    warum: NonEmptyText
    ohne_technik: bool


class ResultPartTwoViews(StrictResultModel):
    """Die Beispielansichten — Aufruf 2a.

    Sie sind der verschachtelte Teil des unteren Bereichs: je Ansichtstyp
    eigene Felder, Schachtelungstiefe acht. In einem Schema mit allem
    Übrigen wird dieser Aufruf doppelt so groß wie Aufruf 1 und läuft in
    fast der Hälfte der Fälle in die Zeitgrenze — deshalb steht er allein.
    """

    # Null bis vier: Eine Ansicht entsteht, wenn sie etwas erklärt. Zwei zu
    # verlangen hiess, für einen einfachen Fall eine zweite zu erfinden.
    ansichten: Annotated[list[View], Field(max_length=4)]


class ResultPartTwoRest(StrictResultModel):
    """Alles Übrige des unteren Teils — Aufruf 2b.

    Flach: sechs Bereiche aus Listen und kurzen Texten. Die Prüfung der
    Hebel sitzt hier, weil die Hebel hier entstehen.
    """

    aufgabenteilung: Division
    wert: Value
    # Systeme kommen aus der Erzählung. Vier zu verlangen hiess, bei einem
    # Betrieb mit Telefon und Zettel zwei zu erfinden.
    systeme: Annotated[list[ConnectedSystem], Field(max_length=7)]
    architektur: Annotated[list[ArchitectureLayer], Field(max_length=5)]
    umsetzung: Annotated[list[ImplementationStep], Field(max_length=9)]
    # Keine Untergrenze, obwohl der Prompt zwei bis vier verlangt: Die
    # Prüfung unten sortiert aus, und eine leere Liste ist ein gültiges
    # Ergebnis. Ein erfundener Ratschlag ist schlimmer als kein Abschnitt.
    # Der Vorgabewert hält ältere gespeicherte Ergebnisse lesbar — der
    # hinterlegte Beispiellauf kennt dieses Feld nicht, und ihm Hebel
    # anzudichten hiesse, einen geprüften Durchlauf zu fälschen.
    hebel: Annotated[list[Lever], Field(max_length=4)] = []

    @model_validator(mode="after")
    def no_invented_money(self) -> ResultPartTwoRest:
        """Bei gewählter SF-25 steht hier keine erfundene Zahl.

        Die Familie sagt zu, Deckungsbeitrag und Liquidität später aus den
        Daten des Betriebs zu **rechnen**. Ein Betrag im Ergebnistext wäre
        keine Rechnung, sondern eine Behauptung.
        """

        _pruefe_keine_geldbetraege(self.model_dump(), "Der untere Teil")
        return self

    @model_validator(mode="after")
    def levers_are_checked_one_by_one(
        self, info: ValidationInfo
    ) -> ResultPartTwoRest:
        """Sortiert jeden Hebel aus, dessen `woraus` nicht wörtlich dasteht.

        Dieselbe Prüfung wie bei den Belegen und dieselbe Behandlung: Der
        einzelne Hebel fällt, das Ergebnis bleibt. Bleibt keiner übrig,
        bleibt die Liste leer und der Abschnitt entfällt auf der Seite.
        """

        if not self.hebel:
            return self
        erzaehlung = _current_narrative(info)
        if erzaehlung is None:
            raise ValueError(
                "Hebel lassen sich ohne den Erzähltext nicht prüfen. Übergib "
                f"ihn als Kontext unter '{NARRATIVE_CONTEXT_KEY}' oder über "
                "narrative()."
            )
        haystack = normalize_for_quote_match(erzaehlung)
        behalten: list[Lever] = []
        for hebel in self.hebel:
            if normalize_for_quote_match(hebel.woraus) in haystack:
                behalten.append(hebel)
                continue
            logger.warning(
                "result.lever_rejected woraus=%r grund=nicht_woertlich",
                hebel.woraus,
            )
        self.hebel = behalten
        return self


class ResultPartTwo(ResultPartTwoViews, ResultPartTwoRest):
    """Beide Hälften zusammen — was gespeichert und angezeigt wird.

    Die Seite, das PDF und der hinterlegte Beispiellauf sehen unverändert
    ein Ergebnis mit allen sieben Bereichen. Dass es aus zwei Aufrufen
    entsteht, ist eine Frage der Erzeugung und keine des Vertrags.
    """


class Result(ResultPartOne, ResultPartTwo):
    """Das vollständige Ergebnis aus beiden Aufrufen.

    Erbt von beiden Teilen, damit es nur eine Stelle gibt, an der ein Feld
    beschrieben ist. Die Reihenfolge auf der Seite bestimmt die Vorlage, nicht
    diese Klasse.
    """

    contract_version: Literal["ergebnis-v6"] = "ergebnis-v6"


def validation_context(erzaehlung: str) -> dict[str, str]:
    """Baut den Kontext, den die Zitat- und Grenzenprüfung braucht."""

    return {NARRATIVE_CONTEXT_KEY: erzaehlung}
