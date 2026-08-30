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
ViewType = Literal[
    "uebersicht",
    "vorgangsakte",
    "eingangspruefung",
    "nachrichtenverlauf",
    "kundenakte",
    "terminuebersicht",
    "aussenansicht",
    "dokumentenablage",
    "telefonassistent",
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


#: Die Signale aus Aufruf 1, damit Aufruf 2 dagegen geprüft werden kann.
#: Der Planner nennt in seiner Abdeckung Signalkennungen; ob es die gibt und
#: welche davon kritisch sind, steht in der Diagnose — einem Objekt, das der
#: Zielarchitektur-Vertrag nicht sieht. Wie bei `_narrative`: Die
#: OpenAI-Schnittstelle baut das Modell selbst und reicht keinen
#: Validierungskontext durch.
_signalregister: contextvars.ContextVar[dict[str, bool] | None] = (
    contextvars.ContextVar("entscheidungssignale", default=None)
)

#: Die Belegkennungen aus Aufruf 1. Dieselbe Begründung: Aufruf 2 beruft
#: sich beim Why-not auf Belege, und ob es die gibt, steht in der Diagnose.
_belegregister: contextvars.ContextVar[frozenset[str] | None] = (
    contextvars.ContextVar("belegstellen", default=None)
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


@contextmanager
def signalregister(
    signale: Sequence[DecisionSignal],
    belege: Sequence[EvidenceItem] = (),
) -> Iterator[None]:
    """Stellt Signale und Belege aus Aufruf 1 für die Prüfung von Aufruf 2 bereit.

    Ohne diesen Rahmen kann der Vertrag nicht feststellen, ob der Planner
    ein Signal übergangen hat — und genau dafür ist diese Prüfung da.

    Die Belege stehen daneben, weil das Why-not sich auf sie beruft: Eine
    bewusste Nicht-Empfehlung ist glaubwürdiger, wenn sie auf einen Satz
    des Betriebs zeigt — und ein Verweis auf einen Beleg, den es nicht
    gibt, ist dieselbe Erfindung wie ein erfundenes Zitat.
    """

    marke = _signalregister.set({s.id: s.critical for s in signale})
    marke_belege = _belegregister.set(frozenset(b.id for b in belege))
    try:
        yield
    finally:
        _signalregister.reset(marke)
        _belegregister.reset(marke_belege)


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
    # Der Telefonassistent braucht kein eigenes Feld: Der Mitschnitt
    # steckt in denselben Sprechblasen wie ein Chatverlauf, das Erkannte
    # in denselben Feldern wie eine Akte.
    "telefonassistent": ("blasen",),
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


#: Was ein Signal ist. Nicht jeder Satz der Erzählung wird eines — nur
#: das, was eine Empfehlung, eine Grenze, eine Phase oder eine
#: Nicht-Empfehlung verändern kann.
SignalArt = Literal[
    "primary_pain",
    "explicit_goal",
    "start_preference",
    "human_boundary",
    "safety_boundary",
    "existing_system",
    "prerequisite",
    "uncertainty",
]

#: Wie sicher das Signal ist. `confirmed` steht auf einem wörtlichen Beleg,
#: `inferred` folgt aus der Erzählung, ohne dass er es so gesagt hat,
#: `open` ist erkannt und aus dem Vorliegenden nicht entscheidbar.
SignalStand = Literal["confirmed", "inferred", "open"]

#: Kennungen sind kurz und maschinenlesbar. Der Kunde sieht sie nie; sie
#: verbinden Beleg, Signal und Entscheidung über drei Modellaufrufe hinweg.
KENNUNG = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,15}$")


class EvidenceItem(StrictResultModel):
    """Ein wörtliches Zitat mit einer Kennung, auf die sich etwas berufen kann.

    **Der Unterschied zu `Evidence`.** `Evidence` steht auf der Seite und
    wird gelesen. Ein `EvidenceItem` wird *referenziert*: Ein Signal sagt
    „das steht hier", und diese Kennung ist die Adresse dafür.

    Dieselbe Prüfung wie überall: Das Zitat kommt wörtlich in der
    Erzählung vor, sonst fliegt es raus. Das ist keine neue Regel, nur
    dieselbe an einer zweiten Stelle.
    """

    id: NonEmptyText
    zitat: NonEmptyText
    bedeutung: NonEmptyText


class DecisionSignal(StrictResultModel):
    """Ein Punkt, der eine Entscheidung verändern kann — Aufruf 1.

    **Warum es das gibt.** Seit der Breitensuche wurde die Morgenübersicht
    in drei von drei Läufen gefunden und dem Planner angeboten — und in
    drei von drei Läufen fallengelassen, ohne dass irgendwo stand, dass
    sie fallengelassen wurde. Ein Bedarf, den niemand aufgeschrieben hat, kann
    auch niemand bewusst ablehnen. Er verschwindet einfach.

    Ein Signal ist die Aufschreibung. Was daraus wird, entscheidet Aufruf 2
    — aber er muss es entscheiden, und die Entscheidung ist nachlesbar.

    **Kein Betriebsmodell.** Das hier zerlegt nicht die Erzählung. Wer
    jeden Absatz zu einem Signal macht, hat eine zweite Erzählung und
    keine Entscheidungsgrundlage.
    """

    id: NonEmptyText
    kind: SignalArt
    #: Der Punkt in einem Satz, in der Sprache des Betriebs. Intern.
    statement: NonEmptyText
    status: SignalStand
    #: **Muss dieser Punkt bewusst entschieden werden?** `True` heisst:
    #: Aufruf 2 kommt an ihm nicht vorbei. Nicht jedes Signal ist das —
    #: aber was der Betrieb selbst als grösste Last, als Wunsch oder als
    #: Grenze benannt hat, ist es.
    critical: bool
    #: Die Kennungen der Belege, auf denen das Signal steht. Leer ist
    #: erlaubt: Ein abgeleitetes Signal hat keinen wörtlichen Beleg.
    evidence_refs: Annotated[list[NonEmptyText], Field(max_length=4)] = []


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
    #: **Die Belegstellen des Ledgers.** Getrennt von `verstanden.belege`:
    #: Die stehen auf der Seite und sind auf drei begrenzt, weil dort drei
    #: Karten hängen. Hier stehen die Stellen, auf die sich Signale berufen
    #: — das sind mehr, und der Kunde sieht sie nie.
    #: Leer mit Vorgabe, damit ältere gespeicherte Diagnosen lesbar bleiben.
    evidence_items: Annotated[list[EvidenceItem], Field(max_length=12)] = []
    #: **Was bewusst entschieden werden muss.** Leer mit Vorgabe, aus
    #: demselben Grund.
    decision_signals: Annotated[list[DecisionSignal], Field(max_length=12)] = []

    @model_validator(mode="after")
    def the_ledger_holds_together(self, info: ValidationInfo) -> Diagnose:
        """Belege sind wörtlich, Kennungen eindeutig, Verweise gehen ins Leere nicht.

        **Drei verschiedene Fälle, drei verschiedene Antworten.**

        Ein Zitat, das nicht wörtlich dasteht, fliegt raus — dieselbe
        Regel wie bei `verstanden.belege`, und aus demselben Grund einzeln
        statt als Scheitern des ganzen Laufs.

        Ein Verweis auf einen *so aussortierten* Beleg wird stillschweigend
        gelöst: Das Signal bleibt, es steht nur nicht mehr auf diesem
        Zitat. Den Fehler hat die Zitatprüfung bereits vermerkt; ihn ein
        zweites Mal zum Scheitern zu bringen, kostet einen Modellaufruf und
        bringt nichts.

        Ein Verweis auf eine Kennung, die es **nie gab**, ist etwas
        anderes: Da hat sich das Modell eine Adresse ausgedacht. Das ist
        ein Fehler und löst den eingebauten zweiten Versuch aus. Sonst
        stünde am Ende ein Signal, das behauptet, belegt zu sein, und der
        Beleg existiert nicht.
        """

        erzaehlung = _current_narrative(info)
        if erzaehlung is None:
            raise ValueError(
                "Belegstellen lassen sich ohne den Erzähltext nicht prüfen. "
                f"Übergib ihn als Kontext unter '{NARRATIVE_CONTEXT_KEY}' "
                "oder über narrative()."
            )

        gesehen: set[str] = set()
        for beleg in self.evidence_items:
            if KENNUNG.match(beleg.id) is None:
                raise ValueError(
                    f"Die Belegkennung „{beleg.id}“ ist keine Kennung. "
                    "Erlaubt sind Buchstaben, Ziffern, Strich und "
                    "Unterstrich, höchstens sechzehn Zeichen."
                )
            if beleg.id in gesehen:
                raise ValueError(
                    f"Die Belegkennung „{beleg.id}“ steht zweimal. Jede "
                    "Kennung gehört genau einem Beleg."
                )
            gesehen.add(beleg.id)

        haystack = normalize_for_quote_match(erzaehlung)
        behalten: list[EvidenceItem] = []
        verworfen: set[str] = set()
        for beleg in self.evidence_items:
            if normalize_for_quote_match(beleg.zitat) in haystack:
                behalten.append(beleg)
                continue
            verworfen.add(beleg.id)
            logger.warning(
                "ledger.quote_rejected id=%s zitat=%r grund=nicht_woertlich",
                beleg.id,
                beleg.zitat,
            )
            vermerkt = _aussortierte_zitate.get()
            if vermerkt is not None:
                vermerkt.append(beleg.zitat)
        self.evidence_items = behalten
        vorhanden = {beleg.id for beleg in behalten}

        signalkennungen: set[str] = set()
        for signal in self.decision_signals:
            if KENNUNG.match(signal.id) is None:
                raise ValueError(
                    f"Die Signalkennung „{signal.id}“ ist keine Kennung. "
                    "Erlaubt sind Buchstaben, Ziffern, Strich und "
                    "Unterstrich, höchstens sechzehn Zeichen."
                )
            if signal.id in signalkennungen:
                raise ValueError(
                    f"Die Signalkennung „{signal.id}“ steht zweimal. Jede "
                    "Kennung gehört genau einem Signal."
                )
            signalkennungen.add(signal.id)
            erfunden = [
                bezug
                for bezug in signal.evidence_refs
                if bezug not in vorhanden and bezug not in verworfen
            ]
            if erfunden:
                raise ValueError(
                    f"Das Signal „{signal.id}“ beruft sich auf Belege, die "
                    f"es nicht gibt: {erfunden}. Ein Verweis zeigt auf eine "
                    "Kennung aus evidence_items."
                )
            signal.evidence_refs = [
                bezug for bezug in signal.evidence_refs if bezug in vorhanden
            ]
        return self


#: Die vier Stellen, an denen ein Ablauf hängen bleiben kann.
Stelle = Literal["eingang", "zusammenlauf", "sichtbarkeit", "ergebnis"]


class Abdeckung(StrictResultModel):
    """Eine der vier Stellen des Ablaufs — und was sie abdeckt.

    **Warum das ein Feld ist und keine Prompt-Regel.**

    Die Regel stand schon da: „Geh den ganzen Weg ab und prüfe jede Stelle
    einzeln." Drei Läufe auf demselben Fall wählten daraufhin eine, drei
    und wieder eine Familie. Eine Prüfung, die niemand aufschreiben muss,
    wird abgehakt — sie kostet nichts, sie hinterlässt nichts, und ihr
    Ergebnis kann niemand nachlesen.

    Aufgeschrieben kostet sie etwas: Wer „eingang: nicht abgedeckt"
    hinschreiben muss, sieht, dass der Anruf weiterhin ungefiltert
    ankommt. Das ist der ganze Zweck.

    Der Kunde sieht davon nichts. Es steht im Protokoll und im Vertrag.
    """

    stelle: Stelle
    #: Welche gewählten Familien diese Stelle abdecken. Leer ist erlaubt —
    #: aber dann muss `begruendung` sagen, warum das in Ordnung ist.
    abgedeckt_durch: Annotated[list[str], Field(max_length=4)] = []
    #: Bei Abdeckung: was dort geschieht. Ohne Abdeckung: warum diese
    #: Stelle für diesen Betrieb keine ist.
    begruendung: NonEmptyText


class Ausbaustufe(StrictResultModel):
    """Ein Schritt auf dem Weg vom ersten Engpass zum verbundenen Betrieb.

    **Der Unterschied zu einem Modul.** Ein Modul ist ein Teil der Lösung,
    die jetzt gebaut wird. Eine Ausbaustufe ist ein *Bereich des Betriebs*,
    der danach dazukommen kann — die Kundenkommunikation, die Selbst-
    auskunft, die Kundenhistorie, das Nachfassen.

    Solange der Ausblick ein Modul war, blieb er auf derselben Schiene:
    Auf einen gemeinsamen Fahrzeugstand folgte „Statusfragen automatisch
    beantworten" — dieselbe Sache, ein Feature weiter. Ein Betrieb, der so
    etwas liest, sieht eine Funktion. Er soll sehen, wie weit das gehen
    kann.
    """

    #: Wann dieser Bereich an die Reihe kommt. Die erste Stufe ist immer
    #: `jetzt` — das ist die Grundlage, die gerade empfohlen wurde.
    stufe: Stage
    #: Der Bereich, um den es geht. „Kundenkommunikation anbinden",
    #: „Kunden selbst Auskunft ermöglichen" — keine Produktnamen.
    name: NonEmptyText
    #: **Was der Betrieb dann nicht mehr selbst macht**, in einem Satz.
    #: Wie bei `Module.nutzen`: Die Beschreibung sagt, was entsteht; das
    #: hier sagt, warum es ihn angeht.
    nutzen: NonEmptyText
    #: Zwei bis fünf greifbare Teile dieses Bereichs, in seiner Sprache.
    #: Der Kunde soll sehen, woraus so ein Schritt besteht, ohne dass
    #: daraus schon ein Angebot wird.
    bausteine: Annotated[list[NonEmptyText], Field(max_length=6)] = []
    #: **Woher dieser Bereich kommt.** Intern, der Kunde sieht es nie.
    #: Ohne Katalogbindung wäre der Ausbaupfad genau das, was dieser ganze
    #: Weg verhindert: eine überzeugend klingende Erfindung.
    solution_family_ids: Annotated[list[str], Field(min_length=1, max_length=3)]


#: Was mit einem Signal geschieht. Sechs Antworten, und **jede davon ist
#: eine**. Auch „derzeit nicht empfohlen" und „nicht entscheidbar" sind
#: Entscheidungen — das stille Weglassen ist keine.
Disposition = Literal[
    "start",
    "target",
    "future",
    "supporting",
    "not_recommended",
    "open",
]

#: Was `not_recommended` an Begründung mindestens braucht. Ein Wort ist
#: keine, und „passt nicht" ist auch keine.
BEGRUENDUNG_MINDESTWOERTER = 5

#: Der Wortlaut, mit dem der Server eine übergangene Entscheidung
#: nachträgt. Als Konstante, weil die Messung ihn wiedererkennen muss:
#: Ein nachgetragenes `open` ist keine Entscheidung des Planners, und wo
#: dieser Unterschied verschwindet, misst sich die Prüfung selbst schön.
NACHGETRAGEN = (
    "Vom Server nachgetragen: Der Planner hat zu diesem Punkt nichts "
    "entschieden."
)


class CoverageItem(StrictResultModel):
    """Was mit einem Signal geschieht — und warum.

    **Abdeckung heisst nicht Umsetzung.** Ein Signal ist behandelt, wenn
    jemand entschieden hat, was damit passiert. Dass daraus eine
    Lösungsfamilie wird, ist einer von sechs möglichen Ausgängen und nicht
    das Ziel. Ein Vertrag, der für jedes Signal eine Familie verlangt,
    erzwingt Empfehlungen — und Empfehlungen, die aus einem Zwang
    entstehen, sind das, wogegen dieser ganze Weg gebaut ist.
    """

    signal_id: NonEmptyText
    disposition: Disposition
    #: Die Familien, die dahinterstehen. Bei `start` und `target` Pflicht:
    #: Wer sagt „das ist Teil der Lösung", muss sagen, welcher Teil. Bei
    #: `supporting`, `not_recommended` und `open` darf die Liste leer sein.
    family_refs: Annotated[list[str], Field(max_length=3)] = []
    #: Ein Satz: warum diese Entscheidung. Intern, der Kunde sieht ihn nie.
    explanation: NonEmptyText


class Coverage(StrictResultModel):
    """Die Entscheidungen zu allen Signalen — Aufruf 2.

    **Die Stelle, an der Übergehen auffällt.** Vorher konnte ein wichtiger
    Bedarf gefunden, dem Planner angeboten und lautlos übergangen werden;
    im Ergebnis war davon nichts zu sehen, weil es keine Stelle gab, an
    der etwas zu sehen gewesen wäre. Hier ist diese Stelle.
    """

    items: Annotated[list[CoverageItem], Field(max_length=16)] = []
    #: **Welche kritischen Signale der Planner nicht entschieden hat.**
    #: Serverseitig gerechnet, nicht übernommen: Eine Selbstauskunft über
    #: die eigenen Lücken ist keine Messung. Was das Modell hier hinschreibt,
    #: wird überschrieben.
    uncovered_critical_signal_ids: Annotated[list[str], Field(max_length=12)] = []


#: Warum etwas Naheliegendes **jetzt** nicht empfohlen wird. Sechs
#: Gründe, und keiner davon ist „passt nicht". Ein Why-not ohne
#: tragenden Grund ist stilles Weglassen mit einer Überschrift davor.
WhyNotGrund = Literal[
    "missing_prerequisite",
    "safety_boundary",
    "human_boundary",
    "existing_solution_is_enough",
    "too_early_for_start",
    "not_useful_now",
]


class WhyNot(StrictResultModel):
    """Eine Möglichkeit, die bewusst nicht empfohlen wird — Aufruf 2.

    **Warum das ein eigenes Feld ist und nicht nur eine Disposition.**

    `coverage` beantwortet, was mit einem *Signal* geschieht. Das Why-not
    beantwortet etwas anderes: Was hätte hier nahegelegen, und warum tun
    wir es nicht? Das muss kein Signal gewesen sein — die automatische
    Terminbuchung bei einem Betrieb, der über Termine klagt, drängt sich
    auf, ohne dass er sie je verlangt hat.

    In drei gemessenen Läufen des Heizungsfalls entstand über die
    Disposition kein einziges `not_recommended`. Ein Abschnitt, der nur
    zufällig entsteht, ist kein Abschnitt.

    **Nie auffüllen.** Null ist die richtige Antwort, wenn nichts
    Naheliegendes ausgeschlossen wurde. Zwei sind die Obergrenze: Eine
    Liste von Absagen liest sich als Verteidigung, nicht als Beratung.
    """

    #: Was nicht empfohlen wird, in der Sprache des Betriebs. Kein
    #: Familienname, kein Produkt: „Termine automatisch vergeben".
    titel: NonEmptyText
    #: Woraus es käme. Mindestens eine Familie aus dem Katalog — sonst
    #: wäre die Absage so erfunden wie die Empfehlung es wäre.
    family_refs: Annotated[list[str], Field(min_length=1, max_length=2)]
    grund: WhyNotGrund
    #: Der Grund in einem Satz, für diesen Betrieb. Intern.
    erlaeuterung: NonEmptyText
    #: Die Belegkennungen, falls der Betrieb selbst etwas dazu gesagt hat.
    evidence_refs: Annotated[list[NonEmptyText], Field(max_length=3)] = []
    #: Was fehlt, damit es später doch ginge. Nur bei
    #: `missing_prerequisite` und `too_early_for_start` sinnvoll.
    fehlende_voraussetzung: str | None = None


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
    #: **Wie die Lösung mit dem Betrieb wachsen kann.** Drei bis sechs
    #: Stufen, jede ein eigener Bereich. Leer mit Vorgabe, damit ältere
    #: gespeicherte Ergebnisse lesbar bleiben.
    ausbaupfad: Annotated[list[Ausbaustufe], Field(max_length=6)] = []
    #: **Der ausgeschriebene Weg.** Vier Einträge, einer je Stelle. Leer
    #: mit Vorgabe, damit ältere gespeicherte Ergebnisse lesbar bleiben.
    abdeckung: Annotated[list[Abdeckung], Field(max_length=4)] = []
    #: **Was aus den Signalen geworden ist.** Leer mit Vorgabe, damit
    #: bestehende Tests und Läufe ohne Ledger weiterlaufen.
    coverage: Coverage | None = None
    #: **Was bewusst nicht empfohlen wird.** Null bis zwei. Leer ist die
    #: richtige Antwort, wenn nichts Naheliegendes ausgeschlossen wurde.
    why_not: Annotated[list[WhyNot], Field(max_length=2)] = []

    @model_validator(mode="after")
    def the_whole_way_is_written_down(self) -> Zielarchitektur:
        """Vier Stellen, jede genau einmal, jede mit einem Satz.

        Ohne Katalogtreffer entfällt die Prüfung: Wo nichts empfohlen
        wird, gibt es auch nichts abzudecken.

        Eine Stelle ohne Abdeckung ist erlaubt — nicht jeder Betrieb hat
        an jeder Stelle ein Problem. Sie muss nur benannt sein. Genau
        darin liegt der Nutzen: Wer hinschreiben muss, dass der Eingang
        offen bleibt, sieht es auch.
        """

        if not self.catalog_fit or not self.abdeckung:
            return self
        from app import solution_catalog

        gesehen: list[str] = []
        for eintrag in self.abdeckung:
            if eintrag.stelle in gesehen:
                raise ValueError(
                    f"Die Stelle „{eintrag.stelle}“ steht zweimal in der "
                    "Abdeckung. Jede Stelle genau einmal."
                )
            gesehen.append(eintrag.stelle)
            eigene, fremde = solution_catalog.pruefe_auswahl(
                eintrag.abgedeckt_durch
            )
            if fremde:
                raise ValueError(
                    f"Die Stelle „{eintrag.stelle}“ nennt eine Familie, die "
                    f"es nicht gibt: {fremde}."
                )
            ausserhalb = [
                kennung
                for kennung in eigene
                if kennung not in self.selected_solution_family_ids
            ]
            if ausserhalb:
                raise ValueError(
                    f"Die Stelle „{eintrag.stelle}“ nennt {ausserhalb}, aber "
                    "diese Familie wurde nicht ausgewählt."
                )
            eintrag.abgedeckt_durch = eigene
        fehlend = [
            stelle
            for stelle in ("eingang", "zusammenlauf", "sichtbarkeit", "ergebnis")
            if stelle not in gesehen
        ]
        if fehlend:
            raise ValueError(
                f"In der Abdeckung fehlen diese Stellen: {fehlend}. Der Weg "
                "wird ganz abgegangen oder gar nicht."
            )
        return self

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

    @model_validator(mode="after")
    def every_critical_signal_gets_a_decision(self) -> Zielarchitektur:
        """Kein kritisches Signal verlässt diesen Aufruf ohne Entscheidung.

        **Was ein Fehler ist und was nur eine Lücke.**

        Eine erfundene Signalkennung, eine Familie ausserhalb des Katalogs,
        ein `start`, der auf etwas zeigt, das gar nicht gebaut wird, zwei
        Entscheidungen zu demselben Signal, ein `not_recommended` ohne
        Grund: Das sind Fehler. Sie lösen den eingebauten zweiten Versuch
        aus, weil die Antwort in sich nicht stimmt.

        Ein kritisches Signal, das der Planner **übergangen** hat, ist
        etwas anderes. Daran ist die Antwort nicht falsch, sondern
        unvollständig — und den ganzen Lauf daran scheitern zu lassen,
        setzt einen Kunden wegen einer fehlenden internen Zeile vor eine
        Fehlermeldung. Stattdessen trägt der Server die Lücke als `open`
        nach und schreibt die Kennung in `uncovered_critical_signal_ids`.

        **Das ist keine Kosmetik, sondern die Messung.** Der nachgetragene
        Eintrag sorgt dafür, dass nichts still verschwindet; die Liste
        daneben sagt, wie oft der Planner es selbst nicht geschafft hat.
        Ohne sie wäre „jedes Signal hat eine Entscheidung" eine Zahl, die
        der Server sich selbst schenkt.
        """

        register = _signalregister.get()
        if register is None:
            if self.coverage is not None:
                raise ValueError(
                    "Die Abdeckung lässt sich ohne die Signale aus Aufruf 1 "
                    "nicht prüfen. Übergib sie über signalregister()."
                )
            return self
        if not self.catalog_fit and self.coverage is None:
            # Ohne Katalogtreffer gibt es keine Auswahl, an der etwas
            # hängen könnte. Ein leerer Ledger ist dann kein Versäumnis.
            return self

        from app import solution_catalog

        if self.coverage is None:
            self.coverage = Coverage()

        # Welche Familien tatsächlich gebaut werden. `start` darf nur auf
        # diese zeigen: Eine Familie, aus der kein Modul entsteht, ist
        # kein Einstieg, sondern eine Absichtserklärung.
        gebaut = {
            kennung
            for modul in self.module
            for kennung in modul.solution_family_ids
        }
        gewaehlt = set(self.selected_solution_family_ids)

        entschieden: list[str] = []
        for eintrag in self.coverage.items:
            if eintrag.signal_id not in register:
                raise ValueError(
                    f"Die Abdeckung nennt das Signal „{eintrag.signal_id}“, "
                    "das es in der Diagnose nicht gibt."
                )
            if eintrag.signal_id in entschieden:
                raise ValueError(
                    f"Das Signal „{eintrag.signal_id}“ bekommt zwei "
                    "Entscheidungen. Genau eine je Signal."
                )
            entschieden.append(eintrag.signal_id)

            eigene, fremde = solution_catalog.pruefe_auswahl(eintrag.family_refs)
            if fremde:
                raise ValueError(
                    f"Die Entscheidung zu „{eintrag.signal_id}“ nennt eine "
                    f"Familie, die es nicht gibt: {fremde}."
                )
            eintrag.family_refs = eigene

            if eintrag.disposition in ("start", "target"):
                if not eigene:
                    raise ValueError(
                        f"Die Entscheidung „{eintrag.disposition}“ zu "
                        f"„{eintrag.signal_id}“ nennt keine Familie. Was zur "
                        "Lösung gehört, gehört zu einer gewählten Familie."
                    )
                ausserhalb = [k for k in eigene if k not in gewaehlt]
                if ausserhalb:
                    raise ValueError(
                        f"Die Entscheidung „{eintrag.disposition}“ zu "
                        f"„{eintrag.signal_id}“ nennt {ausserhalb}, aber "
                        "diese Familie wurde nicht ausgewählt."
                    )
            if eintrag.disposition == "start":
                ohne_modul = [k for k in eigene if k not in gebaut]
                if ohne_modul:
                    raise ValueError(
                        f"Der Einstieg zu „{eintrag.signal_id}“ nennt "
                        f"{ohne_modul}, aber daraus entsteht kein Modul. Ein "
                        "Einstieg ist etwas, das gebaut wird."
                    )
            if eintrag.disposition == "not_recommended":
                if len(eintrag.explanation.split()) < BEGRUENDUNG_MINDESTWOERTER:
                    raise ValueError(
                        f"Die Nicht-Empfehlung zu „{eintrag.signal_id}“ hat "
                        "keine nachvollziehbare Begründung. Sag, was fehlt, "
                        "welche Grenze dagegen spricht oder was schon reicht."
                    )

        # **Jedes Signal, nicht nur die kritischen.** Der erste Entwurf
        # verlangte eine Entscheidung nur bei `critical`. Gemessen am
        # Heizungsfall hat das Modell daraufhin genau die Themen, um die
        # es geht — Morgenübersicht, Kapazitätsgrenze, Wissen in Köpfen —
        # als nicht kritisch eingestuft, und sie fielen wieder lautlos
        # heraus. „Nicht kritisch" war damit der neue stille Papierkorb.
        #
        # Ein Signal entsteht ohnehin nur dort, wo eine Antwort eine
        # Empfehlung verändern könnte. Wer es aufschreibt, entscheidet es.
        # `critical` sagt danach nur noch, wie schwer eine Lücke wiegt.
        offen = [
            kennung for kennung in register if kennung not in entschieden
        ]
        for kennung in offen:
            self.coverage.items.append(
                CoverageItem(
                    signal_id=kennung,
                    disposition="open",
                    family_refs=[],
                    explanation=NACHGETRAGEN,
                )
            )
        self.coverage.uncovered_critical_signal_ids = [
            kennung for kennung in offen if register[kennung]
        ]
        if offen:
            logger.warning(
                "solution.coverage_gap uebergangen=%s davon_kritisch=%s "
                "von_signalen=%d",
                offen,
                self.coverage.uncovered_critical_signal_ids or "keine",
                len(register),
            )
        return self

    @model_validator(mode="after")
    def a_refusal_names_something_real(self) -> Zielarchitektur:
        """Jede Absage zeigt auf eine echte Familie und einen echten Beleg.

        **Und nie auf etwas, das gleichzeitig empfohlen wird.** „Wir
        empfehlen den Kundenzugang und empfehlen ihn nicht" ist keine
        Abwägung, sondern ein Widerspruch — und der Leser glaubt danach
        keiner der beiden Aussagen.
        """

        if not self.why_not:
            return self
        from app import solution_catalog

        belege = _belegregister.get()
        gewaehlt = set(self.selected_solution_family_ids)
        gesehen: list[str] = []
        for absage in self.why_not:
            eigene, fremde = solution_catalog.pruefe_auswahl(absage.family_refs)
            if fremde:
                raise ValueError(
                    f"Die Nicht-Empfehlung „{absage.titel}“ nennt eine "
                    f"Familie, die es nicht gibt: {fremde}."
                )
            if not eigene:
                raise ValueError(
                    f"Die Nicht-Empfehlung „{absage.titel}“ nennt keine "
                    "Familie aus dem Katalog."
                )
            widerspruch = [k for k in eigene if k in gewaehlt]
            if widerspruch:
                raise ValueError(
                    f"Die Nicht-Empfehlung „{absage.titel}“ nennt "
                    f"{widerspruch}, aber diese Familie wurde empfohlen. "
                    "Beides zusammen geht nicht."
                )
            doppelt = [k for k in eigene if k in gesehen]
            if doppelt:
                raise ValueError(
                    f"Die Nicht-Empfehlung „{absage.titel}“ sagt {doppelt} "
                    "ein zweites Mal ab."
                )
            gesehen.extend(eigene)
            absage.family_refs = eigene
            if len(absage.erlaeuterung.split()) < BEGRUENDUNG_MINDESTWOERTER:
                raise ValueError(
                    f"Die Nicht-Empfehlung „{absage.titel}“ hat keine "
                    "nachvollziehbare Begründung."
                )
            if belege is None:
                continue
            erfunden = [b for b in absage.evidence_refs if b not in belege]
            if erfunden:
                raise ValueError(
                    f"Die Nicht-Empfehlung „{absage.titel}“ beruft sich auf "
                    f"Belege, die es nicht gibt: {erfunden}."
                )
        return self

    @model_validator(mode="after")
    def the_path_opens_a_new_area_each_step(self) -> Zielarchitektur:
        """Jede Stufe eine Familie, und keine Familie zweimal.

        Die Kennungen müssen im freigegebenen Katalog stehen — sonst wäre
        der Ausbaupfad genau das, wogegen dieser ganze Weg gebaut ist.

        **Und keine Stufe wiederholt die Familie einer früheren.** Daran
        wäre der alte Ausblick gescheitert: „Gemeinsamer Fahrzeugstand"
        und danach „Statusauskunft zum Fahrzeugstand" sind zwei Kacheln
        und ein Thema. Ein Weg, der zweimal dieselbe Tür öffnet, führt
        nirgendwohin — und der Betrieb, der ihn liest, sieht eine
        Funktion statt einer Richtung.
        """

        from app import solution_catalog

        schon_offen: list[str] = []
        for schritt in self.ausbaupfad:
            eigene, fremde = solution_catalog.pruefe_auswahl(
                schritt.solution_family_ids
            )
            if fremde:
                raise ValueError(
                    f"Die Ausbaustufe „{schritt.name}“ nennt eine Familie, "
                    f"die es nicht gibt: {fremde}."
                )
            if not eigene:
                raise ValueError(
                    f"Die Ausbaustufe „{schritt.name}“ nennt keine Familie "
                    "aus dem Katalog."
                )
            wiederholt = [kennung for kennung in eigene if kennung in schon_offen]
            if wiederholt:
                raise ValueError(
                    f"Die Ausbaustufe „{schritt.name}“ öffnet mit "
                    f"{wiederholt} denselben Bereich noch einmal. Jede Stufe "
                    "erschliesst einen Bereich, den die vorigen nicht haben."
                )
            schritt.solution_family_ids = eigene
            schon_offen.extend(eigene)
        return self


#: Die vier Zustände, in denen die Ergebnisseite einen Bereich zeigt.
#: `today` ist kein Familienzustand — er beschreibt, was heute läuft, und
#: steht deshalb nicht in diesem Vertrag, sondern im Vergleich.
Phase = Literal["today", "start", "target", "future"]


class DecisionState(StrictResultModel):
    """Die fachliche Entscheidung eines Laufs — festgehalten, nicht abgeleitet.

    **Warum es das gibt.** Die Ergebnisseite muss wissen, was zum
    Einstieg gehört, was zum Zielbild und was bewusst später kommt. Bisher
    liess sich das nur erraten: aus Modulstufen, aus dem Ausbaupfad, aus
    der Reihenfolge der Familien. Jede Vorlage, die das selbst
    zusammenreimt, trifft dabei eine fachliche Entscheidung — und zwei
    Vorlagen reimen es verschieden zusammen. Web und PDF zeigten dann
    verschiedene Empfehlungen aus demselben Lauf.

    Hier steht sie einmal, geprüft, und beide lesen dieselbe.

    **Serverseitig abgeleitet, ohne weiteren Modellaufruf.** Alles hier
    steht bereits in Aufruf 1 und 2. Was fehlte, war die Stelle, an der
    es zusammenkommt und geprüft wird.
    """

    contract_version: Literal["results-v1"] = "results-v1"
    #: Die Belegstellen mit ihren Kennungen — die Adressen, auf die sich
    #: alles Weitere beruft.
    evidence: Annotated[list[EvidenceItem], Field(max_length=12)] = []
    signals: Annotated[list[DecisionSignal], Field(max_length=12)] = []
    coverage: Coverage | None = None
    why_not: Annotated[list[WhyNot], Field(max_length=2)] = []
    #: **Das vollständige Zielbild.** Alle empfohlenen Familien.
    target_family_ids: Annotated[list[str], Field(max_length=8)] = []
    #: **Der Einstieg.** Eine echte Teilmenge des Zielbilds — was zuerst
    #: gebaut wird.
    start_family_ids: Annotated[list[str], Field(max_length=8)] = []
    #: **Was bewusst später kommt.** Ausserhalb des Zielbilds; sonst wäre
    #: es kein Später, sondern ein Teil davon.
    future_family_ids: Annotated[list[str], Field(max_length=8)] = []
    #: Signale, die erkannt und nicht entschieden werden konnten. Sie
    #: bleiben als offene Frage sichtbar.
    open_signal_ids: Annotated[list[str], Field(max_length=12)] = []

    @model_validator(mode="after")
    def the_start_lies_inside_the_target(self) -> DecisionState:
        """Start liegt im Zielbild, Später liegt draussen, alles im Katalog.

        Die drei Listen sind serverseitig gerechnet — trotzdem werden sie
        geprüft. Ein gespeichertes Ergebnis wird beim Lesen erneut durch
        diesen Vertrag geschickt, und was dabei nicht mehr stimmt, soll
        auffallen und nicht auf die Seite.
        """

        from app import solution_catalog

        for feld in ("target_family_ids", "start_family_ids", "future_family_ids"):
            eigene, fremde = solution_catalog.pruefe_auswahl(getattr(self, feld))
            if fremde:
                raise ValueError(
                    f"„{feld}“ nennt eine Familie, die es im freigegebenen "
                    f"Katalog nicht gibt: {fremde}."
                )
            setattr(self, feld, eigene)

        ausserhalb = [
            k for k in self.start_family_ids if k not in self.target_family_ids
        ]
        if ausserhalb:
            raise ValueError(
                f"Der Einstieg nennt {ausserhalb}, aber diese Familie gehört "
                "nicht zum Zielbild. Womit man anfängt, ist ein Teil dessen, "
                "wohin man will."
            )
        drin = [k for k in self.future_family_ids if k in self.target_family_ids]
        if drin:
            raise ValueError(
                f"„später“ nennt {drin}, aber diese Familie steht schon im "
                "Zielbild. Dann ist sie kein Später."
            )
        if self.target_family_ids and not self.start_family_ids:
            raise ValueError(
                "Es gibt ein Zielbild, aber keinen Einstieg. Eine Empfehlung "
                "ohne ersten Schritt ist keine."
            )

        kennungen = {signal.id for signal in self.signals}
        erfunden = [k for k in self.open_signal_ids if k not in kennungen]
        if erfunden:
            raise ValueError(
                f"Offen gemeldet sind Signale, die es nicht gibt: {erfunden}."
            )
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
    #: **Die festgehaltene Entscheidung dieses Laufs.** Leer mit Vorgabe:
    #: Ergebnisse von vor diesem Vertrag haben sie nicht, und ihnen eine
    #: anzudichten hiesse, einen geprüften Durchlauf zu fälschen. Was mit
    #: solchen Läufen geschieht, entscheidet der Aufrufer.
    entscheidung: DecisionState | None = None
    # **Der Ausbaupfad, nicht ein weiteres Modul.**
    #
    # Er steht neben den Modulen und nicht zwischen ihnen: Die Module
    # sind die Lösung, die gebaut wird; der Pfad ist das, was danach
    # möglich wird. Solange beides dieselbe Liste war, las sich der
    # Ausblick wie ein viertes Modul — und das Modell schrieb ihn auch
    # so.
    #
    # Leer mit Vorgabe, damit gespeicherte Ergebnisse von vorher lesbar
    # bleiben; die Vorlage lässt den Abschnitt dann weg.
    ausbaupfad: Annotated[list[Ausbaustufe], Field(max_length=6)] = []
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
