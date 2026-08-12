from __future__ import annotations

import logging
import re
from collections.abc import Mapping, Sequence
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


logger = logging.getLogger(__name__)


def _final_analysis_json_schema(schema: dict[str, Any]) -> None:
    """Structured Outputs verlangt jede Eigenschaft in required."""

    properties = schema.get("properties", {})
    required = schema.setdefault("required", [])
    if isinstance(properties, dict) and isinstance(required, list):
        for field_name in properties:
            if field_name not in required:
                required.append(field_name)


NonEmptyText = Annotated[str, Field(min_length=1)]

DIRECT_CUSTOMER_LANGUAGE_PATTERN = re.compile(
    r"\b(?:du|dein|deine|dir)\b",
    re.IGNORECASE,
)


def _ensure_direct_customer_language(
    value: Any,
    *,
    prefix: str,
    max_length: int,
) -> Any:
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text or DIRECT_CUSTOMER_LANGUAGE_PATTERN.search(text) is not None:
        return text
    repaired = f"{prefix}{text[: max_length - len(prefix)].rstrip()}"
    logger.warning("final_analysis.direct_customer_language_repaired")
    return repaired

INTERNAL_REFERENCE_PATTERN = re.compile(
    r"\b(?:bekannter\s+testfall|testfall|rag[-\s]?fall|referenzfall|"
    r"evaluationsfall|chunk(?:-id)?|content_origin|pattern_ids?|case_id|"
    r"document_id|source_url|is_primary_evidence)\b",
    re.IGNORECASE,
)
INTERNAL_IDENTIFIER_PATTERN = re.compile(
    r"\b(?:(?:PF|SP|OUT)-\d{2}|(?:EVAL-)?[MCKP]-\d{2}(?:[_-][A-Z0-9_]+)*|"
    r"RB(?:02|03|04)-[A-Z0-9]+(?:-[A-Z0-9]+)*)\b",
    re.IGNORECASE,
)
INTERNAL_FILE_PATTERN = re.compile(
    r"(?:knowledge[/\\](?:runtime|candidates|evaluation|archive|curated|raw|patterns)|"
    r"(?:original_[\w-]+|[\w-]+_rag_corpus|evaluation_cases)"
    r"\.(?:md|pdf|json))",
    re.IGNORECASE,
)
PROHIBITED_CUSTOMER_LANGUAGE_PATTERN = re.compile(
    r"\b(?:formulardoppie|nachschlageort|übergabevermerkgabel|"
    r"handschriftenkapazität)\b",
    re.IGNORECASE,
)
FORBIDDEN_CUSTOMER_TERM_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b\w*anker\w*\b", re.IGNORECASE),
    re.compile(r"\b\w*datens(?:atz|\u00e4tze)\w*\b|\bZielschema\w*\b|\bMetadaten\w*\b", re.IGNORECASE),
    re.compile(r"\b\w*pflichtfeld\w*\b|\bFeldvalidierung\w*\b|\bFormate?\b", re.IGNORECASE),
    re.compile(r"\bUpload\w*\b|\bmobiler Eingang\b|\bErfassungskanal\w*\b", re.IGNORECASE),
    re.compile(r"\b(?:Einsatz|Auftrags|Objekt)-ID\w*\b|\bID-Vergabe\w*\b", re.IGNORECASE),
    re.compile(r"\bSoftwareregeln?\b|\bRegelwerk\w*\b|\bdeterministisch\w*\b", re.IGNORECASE),
    re.compile(r"\bAutonomiestufe\w*\b|\bA[0-5]\b", re.IGNORECASE),
    re.compile(
        r"\bSolution\s+Pattern\w*\b|\bProblemfamilie\w*\b|\bPattern\w*\b|"
        r"\bMuster(?:abgleich)?\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bHuman\s+Check\b|\bFreigabe-Gate\w*\b|\bGate\w*\b|\bGuardrail\w*\b", re.IGNORECASE),
    re.compile(r"\bRAG\b|\bRetrieval\w*\b|\bKlassifikation\w*\b|\bInd(?:ex|izes?)\w*\b", re.IGNORECASE),
    re.compile(r"\b(?:PF|SP|OUT|GAI|FAIL|GATE)-[A-Z0-9_-]+\b", re.IGNORECASE),
    re.compile(r"\bKonfigurier\w*\b|\bAktivier\w*\b|\bImplementierung\w*\b|\bPilot\w*\b|\bRollout\w*\b", re.IGNORECASE),
    re.compile(r"\bstrukturiertes Erfassen\b|\binformelle Notizpraxis\b|\bProzessreife\w*\b", re.IGNORECASE),
    re.compile(
        r"\bVorgangsakte\w*\b|\bVorgangsentwurf\w*\b|\bZieloutput\w*\b|"
        r"\bMedien\b|\bDatenobjekt\w*\b|\bEntwurfsstatus\w*\b|"
        r"\bKonsolidierung\w*\b|\bkonsolidier\w*\b|\(\s*nicht verbindlich\s*\)",
        re.IGNORECASE,
    ),
    # Aus den Live-Laeufen Blumenladen, Fotograf und Handwerk. Geprueft wird der
    # Wortstamm, nicht das exakte Wort: "Pflichtfeld" war verboten,
    # "Pflichtfragen" und "Pflichtangaben" rutschten durch.
    re.compile(
        r"\bPflicht(?:feld|frage|angabe|eingabe)\w*\b|"
        r"\bMinimalformular\w*\b|\bEinstiegsformular\w*\b|\bWebformular\w*\b|"
        r"\bInbox\w*\b|\bPosteingang\w*\b|\bWebhook\w*\b|\bWeb-?Eingang\w*\b|"
        r"\bExtraktion\w*\b|\bextrahier\w*\b|"
        r"\bProzessregel\w*\b|\bBelegerkennung\w*\b|\bSpracherkennung\w*\b|"
        r"\bbrowser-?basiert\w*\b|\bVersionierung\w*\b|\bversionier\w*\b|"
        r"\bTranskription\w*\b|\btranskribier\w*\b",
        re.IGNORECASE,
    ),
    # Schreibungsabhaengig: als deutsches Substantiv gross geschrieben.
    # Kleingeschrieben steckt es in CSS-Klassennamen wie "result-layout",
    # die beim Pruefen des gerenderten HTML sonst falsch anschlagen.
    re.compile(r"\bLayout\w*\b"),
)

UNSUBSTANTIATED_BENEFIT_PATTERN = re.compile(
    r"\b(?:reduziert|spart|verkürzt|erhöht|verbessert|steigert)\w*\b"
    r"[^.!?]*(?:Aufwand|Zeit|Suchzeit|Nacharbeit|Fehler|Fehlern|Kosten)\w*",
    re.IGNORECASE,
)


def contains_forbidden_customer_term(value: Any) -> bool:
    """Return whether a rendered customer value still contains internal language."""

    if isinstance(value, str):
        return any(pattern.search(value) is not None for pattern in FORBIDDEN_CUSTOMER_TERM_PATTERNS)
    if isinstance(value, BaseModel):
        return contains_forbidden_customer_term(value.model_dump())
    if isinstance(value, Mapping):
        return any(contains_forbidden_customer_term(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(contains_forbidden_customer_term(item) for item in value)
    return False


def customer_plain_text(value: Any, field_path: str = "customer_output") -> str:
    """Omit unsafe customer text; finished prose is never repaired word by word."""

    text = str(value or "").strip()
    if not text:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    safe_sentences = [
        sentence
        for sentence in sentences
        if UNSUBSTANTIATED_BENEFIT_PATTERN.search(sentence) is None
    ]
    if len(safe_sentences) != len(sentences):
        logger.warning("customer_output.unsupported_benefit_omitted field=%s", field_path)
    text = " ".join(safe_sentences).strip()
    if contains_forbidden_customer_term(text):
        logger.warning("customer_output.field_omitted field=%s", field_path)
        return ""
    return text


def sanitize_customer_payload(value: Any, field_path: str = "customer_output") -> Any:
    """Return the finished customer payload with unsafe fields omitted."""

    if isinstance(value, str):
        return customer_plain_text(value, field_path)
    if isinstance(value, BaseModel):
        return sanitize_customer_payload(value.model_dump(), field_path)
    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            clean = sanitize_customer_payload(item, f"{field_path}.{key}")
            if clean in ("", None, [], {}):
                continue
            sanitized[str(key)] = clean
        return sanitized
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        sanitized_items = [
            sanitize_customer_payload(item, f"{field_path}[{index}]")
            for index, item in enumerate(value)
        ]
        return [item for item in sanitized_items if item not in ("", None, [], {})]
    return value


DISTANT_CUSTOMER_LANGUAGE_PATTERN = re.compile(
    r"\b(?:der Nutzer|die Nutzerin|der Unternehmer|der Mitarbeiter|"
    r"die Person|man sollte)\b",
    re.IGNORECASE,
)
FOLLOW_UP_SOLUTION_PATTERN = re.compile(
    r"\b(?:sollte|sollten|könnte|könnten|würde|würden|empfehlen|"
    r"automatisier\w*|software|app|schnittstelle|api|zum beispiel|"
    r"verbindliche regel|nach \w+ tagen)\b",
    re.IGNORECASE,
)
CURRENT_PROCESS_PATTERN = re.compile(
    r"\b(?:heute|aktuell|derzeit|momentan|bisher|tatsächlich)\b",
    re.IGNORECASE,
)
SUMMARY_META_PATTERN = re.compile(
    r"^(?:prozessname:|ausgewählter prozess:|der prozess heißt|"
    r"aus den vorliegenden angaben|auf grundlage der daten|quelle:|"
    r"die rekonstruktion bleibt unsicher)",
    re.IGNORECASE,
)
AS_IS_META_PATTERN = re.compile(
    r"\b(?:unbekannt|nicht beschrieben|detaillierte schritte fehlen|"
    r"laut prozessname|bekannte einschränkung)\b",
    re.IGNORECASE,
)


def contains_internal_reference(value: Any) -> bool:
    if isinstance(value, str):
        return any(
            pattern.search(value) is not None
            for pattern in (
                INTERNAL_REFERENCE_PATTERN,
                INTERNAL_IDENTIFIER_PATTERN,
                INTERNAL_FILE_PATTERN,
            )
        )
    if isinstance(value, BaseModel):
        return contains_internal_reference(value.model_dump())
    if isinstance(value, Mapping):
        return any(contains_internal_reference(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(contains_internal_reference(item) for item in value)
    return False


def contains_prohibited_customer_language(value: Any) -> bool:
    if isinstance(value, str):
        return PROHIBITED_CUSTOMER_LANGUAGE_PATTERN.search(value) is not None
    if isinstance(value, BaseModel):
        return contains_prohibited_customer_language(value.model_dump())
    if isinstance(value, Mapping):
        return any(
            contains_prohibited_customer_language(item) for item in value.values()
        )
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(contains_prohibited_customer_language(item) for item in value)
    return False


def _neutralize_internal_reference_fields(value: Any) -> tuple[Any, bool]:
    if isinstance(value, str):
        if contains_internal_reference(value):
            return "noch offen", True
        return value, False
    if isinstance(value, Mapping):
        changed = False
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            normalized_item, item_changed = _neutralize_internal_reference_fields(item)
            normalized[str(key)] = normalized_item
            changed = changed or item_changed
        return normalized, changed
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        changed = False
        normalized_items: list[Any] = []
        for item in value:
            normalized_item, item_changed = _neutralize_internal_reference_fields(item)
            normalized_items.append(normalized_item)
            changed = changed or item_changed
        return normalized_items, changed
    return value, False


class StrictResultModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @model_validator(mode="after")
    def reject_internal_references(self) -> StrictResultModel:
        if contains_internal_reference(self.model_dump()):
            raise ValueError(
                "Interne Wissensreferenzen dürfen nicht ausgegeben werden."
            )
        if contains_prohibited_customer_language(self.model_dump()):
            raise ValueError("Die Ausgabe enthält unverständliche Fachbegriffe.")
        return self


class ProcessBoundaryResult(StrictResultModel):
    process_name: NonEmptyText
    start_event: NonEmptyText
    end_event: NonEmptyText

    @model_validator(mode="after")
    def reject_general_category(self) -> ProcessBoundaryResult:
        if self.process_name.casefold() in {
            "marketing",
            "organisation",
            "kundenkommunikation",
        }:
            raise ValueError("Die Beschreibung muss ein konkreter Ablauf sein.")
        return self


class ProcessSuggestion(StrictResultModel):
    process_name: NonEmptyText
    start_event: NonEmptyText
    end_event: NonEmptyText
    reason: NonEmptyText

    @model_validator(mode="after")
    def reject_general_category(self) -> ProcessSuggestion:
        if self.process_name.casefold() in {
            "marketing",
            "organisation",
            "kundenkommunikation",
        }:
            raise ValueError("Der Vorschlag muss ein konkreter Prozess sein.")
        return self


class ProcessSuggestionResult(StrictResultModel):
    suggestions: list[ProcessSuggestion] = Field(min_length=1, max_length=3)


class ProcessUnderstandingResult(StrictResultModel):
    process_name: NonEmptyText
    start_event: NonEmptyText
    end_event: NonEmptyText
    as_is_steps: list[NonEmptyText] = Field(min_length=2, max_length=5)
    confirmed_facts: list[NonEmptyText] = Field(max_length=6)
    difficult_points: list[NonEmptyText] = Field(max_length=4)
    problem_step_indexes: list[int] = Field(default_factory=list, max_length=4)
    open_points: list[NonEmptyText] = Field(max_length=4)

    @model_validator(mode="after")
    def validate_problem_step_indexes(self) -> ProcessUnderstandingResult:
        if len(set(self.problem_step_indexes)) != len(self.problem_step_indexes):
            raise ValueError("Problemstellen dürfen nicht doppelt markiert werden.")
        if any(index < 0 or index >= len(self.as_is_steps) for index in self.problem_step_indexes):
            raise ValueError("Eine markierte Problemstelle liegt außerhalb des Ablaufs.")
        return self


class FollowUpQuestion(StrictResultModel):
    question: NonEmptyText
    issue_type: Literal[
        "missing",
        "ambiguous",
        "approximate",
        "self_correction",
        "contradiction",
        "critical_unknown",
    ]

    @model_validator(mode="after")
    def validate_current_process_question(self) -> FollowUpQuestion:
        if not self.question.endswith("?"):
            raise ValueError("Eine Rückfrage muss als einzelne Frage formuliert sein.")
        if CURRENT_PROCESS_PATTERN.search(self.question) is None:
            raise ValueError("Eine Rückfrage muss nach dem heutigen Ablauf fragen.")
        if FOLLOW_UP_SOLUTION_PATTERN.search(self.question) is not None:
            raise ValueError("Eine Rückfrage darf keine Lösung oder Regel vorschlagen.")
        return self


class FollowUpResult(StrictResultModel):
    questions: list[FollowUpQuestion] = Field(max_length=4)

    @model_validator(mode="after")
    def validate_unique_questions(self) -> FollowUpResult:
        normalized = {question.question.casefold().rstrip(" ?!.") for question in self.questions}
        if len(normalized) != len(self.questions):
            raise ValueError("Rückfragen dürfen nicht doppelt vorkommen.")
        return self


class AutomationOpportunityResult(StrictResultModel):
    rank: int = Field(ge=1, le=3)
    title: NonEmptyText
    problem: NonEmptyText
    recommendation: NonEmptyText
    benefit: NonEmptyText
    human_approval: NonEmptyText
    first_step: NonEmptyText
    category: Literal[
        "Ordnung und Standardisierung",
        "einfache Digitalisierung",
        "regelbasierte Automatisierung",
        "KI-Unterstützung",
    ] = "einfache Digitalisierung"
    prerequisite: str = ""
    mini_test: list[NonEmptyText] = Field(default_factory=list, max_length=5)
    effort: Literal["niedrig", "mittel", "hoch"] = "mittel"
    acceptance_risk: str = ""


class AutomationBlueprint(StrictResultModel):
    objective: NonEmptyText
    trigger: NonEmptyText
    required_inputs: list[NonEmptyText]
    workflow_steps: list[NonEmptyText] = Field(min_length=3, max_length=5)
    human_review_point: NonEmptyText
    output: NonEmptyText
    exceptions: list[NonEmptyText]


class OptionalAnalysisDetails(StrictResultModel):
    current_difficulties: list[NonEmptyText] = Field(default_factory=list, max_length=4)
    additional_prerequisites: list[NonEmptyText] = Field(
        default_factory=list, max_length=4
    )
    later_possibilities: list[NonEmptyText] = Field(default_factory=list, max_length=3)


class SampleOutputField(StrictResultModel):
    label: Annotated[str, Field(min_length=1, max_length=45)]
    value: Annotated[str, Field(min_length=1, max_length=140)]


class SampleOutput(StrictResultModel):
    title: Annotated[str, Field(min_length=1, max_length=80)]
    input_context: Annotated[str, Field(max_length=100)] = ""
    incoming_message: Annotated[str, Field(max_length=520)] = ""
    incoming_note: Annotated[str, Field(max_length=100)] = ""
    fields: list[SampleOutputField] = Field(min_length=1, max_length=7)
    missing_details: list[
        Annotated[str, Field(min_length=1, max_length=90)]
    ] = Field(default_factory=list, max_length=2)
    clarification_question: Annotated[str, Field(max_length=240)] = ""
    open_items: list[Annotated[str, Field(min_length=1, max_length=120)]] = Field(
        default_factory=list, max_length=4
    )
    attachments: list[Annotated[str, Field(min_length=1, max_length=80)]] = Field(
        default_factory=list, max_length=3
    )
    preview_notice: Annotated[str, Field(min_length=1, max_length=100)] = (
        "Vorschau – die endgültigen Angaben prüfst du selbst."
    )
    used_catalog_fallback: bool = False


class SecondaryOpportunity(StrictResultModel):
    title: Annotated[str, Field(min_length=1, max_length=90)]
    description: Annotated[str, Field(min_length=1, max_length=220)]


GENERATED_HEADING_MAX_WORDS = 8

CUSTOMER_AS_IMPLEMENTER_PATTERN = re.compile(
    r"\b(?:probier\w*|teste?\s+(?:es\s+)?ab\s+morgen|fang\s+\w*\s*(?:n[äa]chste|kommende)"
    r"\w*\s+Woche\s+an|leg\s+(?:einfach\s+)?los|mach\s+(?:einfach\s+)?selbst)\b",
    re.IGNORECASE,
)


def _validate_generated_heading(value: str, field_name: str) -> str:
    """Ueberschriften tragen Inhalt: kurz, ohne Doppelpunkt und Fragezeichen."""

    text = value.strip()
    # Zusammengesetzte Woerter mit Bindestrich zaehlen als eines:
    # "Shop-Bestellung" ist ein Wort, nicht zwei.
    words = re.findall(r"[\wÄÖÜäöüß]+(?:-[\wÄÖÜäöüß]*)*", text)
    if len(words) > GENERATED_HEADING_MAX_WORDS:
        raise ValueError(
            f"{field_name} darf höchstens {GENERATED_HEADING_MAX_WORDS} Wörter haben."
        )
    if ":" in text or "?" in text:
        raise ValueError(f"{field_name} enthält keinen Doppelpunkt und kein Fragezeichen.")
    return text


class Moeglichkeit(StrictResultModel):
    """Eine erkannte Stelle, an der Arbeit rausgenommen werden kann."""

    rang: Literal["groesster_hebel", "danach", "spaeter"]
    titel: Annotated[str, Field(min_length=1, max_length=120)]
    begruendung: Annotated[str, Field(min_length=1, max_length=300)]


#: Woerter, die in "das fehlt noch" nichts ueber den Inhalt aussagen und
#: deshalb beim Abgleich mit der Nachricht nicht mitzaehlen.
_FEHLT_FUELLWOERTER = frozenset({
    "genaue", "genauer", "genaues", "exakte", "exakter", "exaktes",
    "konkrete", "konkreter", "konkretes", "vereinbarte", "vereinbartes",
    "gewuenschte", "gewünschte", "welche", "welcher", "welches", "oder",
    "sowie", "beziehungsweise",
})


class BeispielFeld(StrictResultModel):
    """Beschriftung und Wert stammen beide aus derselben erfundenen Nachricht."""

    label: Annotated[str, Field(min_length=1, max_length=45)]
    wert: Annotated[str, Field(min_length=1, max_length=140)]


class Beispiel(StrictResultModel):
    """Eine Instanz von loesung.ergebnis_art, keine feste Kartenform."""

    titel: Annotated[str, Field(min_length=1, max_length=120)]
    kanal: Annotated[str, Field(min_length=1, max_length=40)]
    nachricht: Annotated[str, Field(min_length=1, max_length=600)]
    daraus_wird: list[BeispielFeld] = Field(default_factory=list, max_length=8)
    fehlt: list[
        Annotated[str, Field(min_length=1, max_length=140)]
    ] = Field(default_factory=list, max_length=3)
    rueckfrage: Annotated[str, Field(max_length=240)] = ""

    @field_validator("titel")
    @classmethod
    def check_titel(cls, value: str) -> str:
        return _validate_generated_heading(value, "beispiel.titel")

    @model_validator(mode="after")
    def check_beispiel(self) -> Beispiel:
        labels = [item.label.casefold().strip() for item in self.daraus_wird]
        if len(set(labels)) != len(labels):
            raise ValueError("Im Beispiel darf keine Beschriftung doppelt vorkommen.")
        gefuellt = set(labels)
        for eintrag in self.fehlt:
            if eintrag.casefold().strip() in gefuellt:
                raise ValueError(
                    "Ein Feld darf nicht gleichzeitig ausgefüllt und als fehlend "
                    "markiert sein."
                )
        # Was fehlt, darf in der Nachricht nicht vorkommen. Im Handwerksfall
        # fragte die Rueckfrage nach dem Bonfoto, obwohl "Foto angehaengt" in
        # der Nachricht stand. Geprueft werden die Inhaltswoerter des Eintrags.
        nachricht = self.nachricht.casefold()
        for eintrag in self.fehlt:
            woerter = [
                wort
                for wort in re.findall(r"[a-zäöüß]{4,}", eintrag.casefold())
                if wort not in _FEHLT_FUELLWOERTER
            ]
            if woerter and all(wort in nachricht for wort in woerter):
                raise ValueError(
                    f"Als fehlend markiert, steht aber in der Nachricht: {eintrag!r}"
                )
        return self


class Loesung(StrictResultModel):
    titel: Annotated[str, Field(min_length=1, max_length=120)]
    ablauf_heute: list[
        Annotated[str, Field(min_length=1, max_length=180)]
    ] = Field(min_length=3, max_length=6)
    ablauf_kuenftig: list[
        Annotated[str, Field(min_length=1, max_length=180)]
    ] = Field(min_length=3, max_length=6)
    was_reinkommt: Annotated[str, Field(min_length=1, max_length=400)]
    was_die_ki_macht: Annotated[str, Field(min_length=1, max_length=700)]
    was_du_machst: Annotated[str, Field(min_length=1, max_length=400)]
    was_dabei_rauskommt: Annotated[str, Field(min_length=1, max_length=400)]
    ergebnis_art: Annotated[str, Field(min_length=1, max_length=60)]

    @field_validator("titel")
    @classmethod
    def check_titel(cls, value: str) -> str:
        return _validate_generated_heading(value, "loesung.titel")

    @model_validator(mode="after")
    def check_ablauf(self) -> Loesung:
        normalize = lambda items: [
            re.sub(r"[^a-z0-9äöüß]+", " ", item.casefold()).strip() for item in items
        ]
        if normalize(self.ablauf_heute) == normalize(self.ablauf_kuenftig):
            raise ValueError(
                "Heutiger und künftiger Ablauf müssen sich erkennbar unterscheiden."
            )
        return self


class Voraussetzungen(StrictResultModel):
    vorhandene_werkzeuge: list[
        Annotated[str, Field(min_length=1, max_length=140)]
    ] = Field(min_length=1, max_length=8)
    neu_hinzukommend: list[
        Annotated[str, Field(min_length=1, max_length=180)]
    ] = Field(default_factory=list, max_length=5)
    geraete_und_zugang: Annotated[str, Field(min_length=1, max_length=500)]
    musst_du_besorgen: list[
        Annotated[str, Field(min_length=1, max_length=220)]
    ] = Field(default_factory=list, max_length=3)

    @model_validator(mode="after")
    def check_kein_ueberschneiden(self) -> Voraussetzungen:
        """Was bleibt und was dazukommt, darf nicht dieselbe Sache sein."""

        normalize = lambda value: re.sub(r"[^a-z0-9äöüß]+", "", value.casefold())
        bleibt = {normalize(item) for item in self.vorhandene_werkzeuge}
        neu = {normalize(item) for item in self.neu_hinzukommend}
        if bleibt & neu:
            raise ValueError(
                "Ein Werkzeug steht gleichzeitig unter vorhandene_werkzeuge und "
                "neu_hinzukommend."
            )
        return self


class Umsetzung(StrictResultModel):
    hinweis: Annotated[str, Field(min_length=1, max_length=400)]
    einrichtungsschritte: list[
        Annotated[str, Field(min_length=1, max_length=220)]
    ] = Field(min_length=3, max_length=5)
    erster_schritt: Annotated[str, Field(min_length=1, max_length=700)]

    @model_validator(mode="after")
    def check_umsetzung(self) -> Umsetzung:
        if CUSTOMER_AS_IMPLEMENTER_PATTERN.search(self.erster_schritt) is not None:
            raise ValueError(
                "Der erste Umsetzungsschritt macht den Kunden zum Umsetzer."
            )
        return self


#: Die Felder, die das Modell als Kundentext schreibt. Nur diese unterliegen
#: dem Wortfilter. Ist-Ablauf, Diagnose und die aus dem Katalog gefuellten
#: Sicherheitsfelder (not_automated, error_boundaries) sind bewusst
#: ausgenommen: dort steht internes Vokabular, das nie beim Kunden landet.
CUSTOMER_TEXT_FIELDS = frozenset({
    "engpass_titel",
    "engpass_text",
    "moeglichkeiten",
    "loesung",
    "beispiel",
    "voraussetzungen",
    "umsetzung",
    "bleibt_bei_dir",
    "grenzen",
    "spaeter",
})


class FinalAnalysisResult(StrictResultModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra=_final_analysis_json_schema,
    )

    # --- Kundentext nach ERGEBNIS_SPEC.md ------------------------------------
    engpass_titel: Annotated[str, Field(min_length=1, max_length=120)]
    engpass_text: Annotated[str, Field(min_length=1, max_length=600)]
    moeglichkeiten: list[Moeglichkeit] = Field(min_length=1, max_length=3)
    loesung: Loesung
    beispiel: Beispiel | None = None
    voraussetzungen: Voraussetzungen
    umsetzung: Umsetzung
    bleibt_bei_dir: Annotated[str, Field(min_length=1, max_length=400)]
    grenzen: Annotated[str, Field(max_length=400)] = ""
    #: Wird nicht als eigener Block gezeigt - steckt in moeglichkeiten mit Rang
    #: "spaeter". Doppelt zeigen ist laut Spec ein Fehler.
    spaeter: list[
        Annotated[str, Field(min_length=1, max_length=220)]
    ] = Field(default_factory=list, max_length=3)

    # --- Ist-Ablauf und Diagnose: unveraendert --------------------------------
    process_summary: NonEmptyText
    as_is_steps: list[NonEmptyText]
    as_is_problem_step_indexes: list[int] = Field(default_factory=list, max_length=4)
    to_be_steps: list[NonEmptyText] = Field(default_factory=list, max_length=6)
    core_bottleneck: NonEmptyText
    bottleneck_symptom: str = ""
    bottleneck_cause: str = ""
    bottleneck_effect: str = ""
    uncertainties: list[NonEmptyText] = Field(max_length=4)

    # --- Sicherheitsfelder: setzt Python nach dem Modellaufruf ----------------
    autonomy_level: Literal["A0", "A1", "A2", "A3", "A4", "A5"] | None = None
    not_automated: list[
        Annotated[str, Field(min_length=1, max_length=160)]
    ] = Field(default_factory=list, max_length=5)
    error_boundaries: list[
        Annotated[str, Field(min_length=1, max_length=160)]
    ] = Field(default_factory=list, max_length=3)

    @field_validator("engpass_titel")
    @classmethod
    def check_engpass_titel(cls, value: str) -> str:
        return _validate_generated_heading(value, "engpass_titel")

    @field_validator("bleibt_bei_dir", mode="before")
    @classmethod
    def repair_direct_bleibt_bei_dir(cls, value: Any) -> Any:
        return _ensure_direct_customer_language(
            value,
            prefix="Du prüfst: ",
            max_length=400,
        )

    @model_validator(mode="after")
    def validate_customer_output(self) -> FinalAnalysisResult:
        raenge = [item.rang for item in self.moeglichkeiten]
        if len(set(raenge)) != len(raenge):
            raise ValueError("Jeder Rang darf in moeglichkeiten nur einmal vorkommen.")

        if SUMMARY_META_PATTERN.search(self.process_summary) is not None:
            self.process_summary = (
                " ".join(self.as_is_steps)
                or "Der heutige Ablauf bleibt an dieser Stelle noch offen."
            )
        if any(AS_IS_META_PATTERN.search(step) is not None for step in self.as_is_steps):
            original_steps = list(self.as_is_steps)
            kept_indexes = [
                index
                for index, step in enumerate(original_steps)
                if AS_IS_META_PATTERN.search(step) is None
            ]
            index_map = {
                old_index: new_index
                for new_index, old_index in enumerate(kept_indexes)
            }
            self.as_is_steps = [original_steps[index] for index in kept_indexes]
            self.as_is_problem_step_indexes = [
                index_map[index]
                for index in self.as_is_problem_step_indexes
                if index in index_map
            ]
        normalized_uncertainties = {
            uncertainty.casefold().rstrip(".?!") for uncertainty in self.uncertainties
        }
        if len(normalized_uncertainties) != len(self.uncertainties):
            raise ValueError("Unsicherheiten dürfen nicht doppelt vorkommen.")
        if any(
            index < 0 or index >= len(self.as_is_steps)
            for index in self.as_is_problem_step_indexes
        ):
            raise ValueError("Eine markierte Problemstelle liegt außerhalb des Ist-Ablaufs.")

        customer_output = self.model_dump(
            exclude={
                "process_summary",
                "as_is_steps",
                "core_bottleneck",
                "bottleneck_symptom",
                "bottleneck_cause",
                "bottleneck_effect",
                "as_is_problem_step_indexes",
                "to_be_steps",
                "uncertainties",
            }
        )
        distant_matches = {
            match.group(0).casefold()
            for match in DISTANT_CUSTOMER_LANGUAGE_PATTERN.finditer(str(customer_output))
        }
        grounded_role_text = " ".join(
            [self.process_summary, *self.as_is_steps]
        ).casefold()
        ungrounded_matches = distant_matches - {"der mitarbeiter"}
        if "der mitarbeiter" in distant_matches and "mitarbeiter" not in grounded_role_text:
            ungrounded_matches.add("der mitarbeiter")
        if ungrounded_matches:
            raise ValueError("Die Kundenausgabe enthält distanzierte Ansprache.")
        return self
