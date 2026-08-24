"""Der Ergebnisvertrag der neuen Ergebnisseite.

Das Modell liefert Daten, die Vorlage liefert Layout. Deshalb steht hier kein
HTML, kein Klassenname und keine Farbe — nur Felder mit Text, Listen und
Auswahlwerten aus festen Listen.

Die Feldnamen sind deutsch. Das ist die in `AGENTS.md` festgehaltene Ausnahme:
Sie sind Daten, in die das Modell deutschen Text schreibt, keine Bezeichner.
Die Klassennamen sind englisch, wie die Sprachregelung es verlangt; in
Klammern steht jeweils der Abschnitt aus `AUFTRAG_ZIELBILD_V4.md`, Punkt 4b.

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
from collections.abc import Iterator
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
    #: Leer mit Vorgabe, damit gespeicherte Ergebnisse von vor dem 24.08.
    #: lesbar bleiben — der Beispiellauf vom 18.08. kennt diese Felder
    #: nicht. Bei der Erzeugung verlangt `SelectedModule` beide, und der
    #: Katalog prüft sie.
    solution_family_ids: list[str] = []
    baustein_refs: list[str] = []


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

    @model_validator(mode="after")
    def data_must_fit_the_type(self) -> View:
        """Weist eine Ansicht zurück, deren Makro nichts anzuzeigen hätte."""

        for feld in REQUIRED_VIEW_FIELDS[self.typ]:
            if not getattr(self.daten, feld, None):
                raise ValueError(
                    f"Die Ansicht „{self.typ}“ braucht Werte in „{feld}“."
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
        """Weist Zahlen, Prozentangaben und Zeitangaben zurück."""

        for zeile in [*self.faellt_weg, *self.zeit_fuer]:
            if NUMBER_PATTERN.search(zeile) is not None:
                raise ValueError(
                    f"Keine Zahlen im Abschnitt „Wert“: {zeile!r}"
                )
            if TIME_UNIT_PATTERN.search(zeile) is not None:
                raise ValueError(
                    f"Keine Zeitangaben im Abschnitt „Wert“: {zeile!r}"
                )
        return self


class ConnectedSystem(StrictResultModel):
    """Ein System, das verbunden würde (`systeme`)."""

    name: NonEmptyText
    umgang: NonEmptyText


class ArchitectureLayer(StrictResultModel):
    """Eine Schicht der empfohlenen Umsetzungsarchitektur (`architektur`)."""

    ebene: NonEmptyText
    beschreibung: NonEmptyText


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

    **Ohne einen einzigen Lösungsbegriff.** Bis zum 24.08. schrieb dieser
    Aufruf Lösungsname, Zielbild und Module gleich mit — also stand die
    Lösung fest, bevor irgendein Katalog gefragt war. Wer die Lösung
    kennt, diagnostiziert auf sie hin.
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
    eigene Felder, Schachtelungstiefe acht. Bis zum 21.08. standen sie im
    selben Schema wie alles Übrige; dieser Aufruf war doppelt so groß wie
    Aufruf 1 und starb in fast der Hälfte der Läufe.
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
    umsetzung: Annotated[list[NonEmptyText], Field(max_length=9)]
    # Keine Untergrenze, obwohl der Prompt zwei bis vier verlangt: Die
    # Prüfung unten sortiert aus, und eine leere Liste ist ein gültiges
    # Ergebnis. Ein erfundener Ratschlag ist schlimmer als kein Abschnitt.
    # Der Vorgabewert hält ältere gespeicherte Ergebnisse lesbar — der
    # Beispiellauf vom 18.08. kennt dieses Feld nicht, und ihm Hebel
    # anzudichten hiesse, einen geprüften Durchlauf zu fälschen.
    hebel: Annotated[list[Lever], Field(max_length=4)] = []

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

    Die Seite, das PDF und der Beispiellauf vom 18.08. sehen unverändert
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
