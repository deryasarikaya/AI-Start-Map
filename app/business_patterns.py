"""Betriebsartenwissen laden und je Aufruf zuschneiden.

Die Dateien unter ``knowledge/business_patterns/`` sagen dem Modell, worauf es
bei einer Betriebsart achten kann — nie, welche Lösung der Betrieb braucht.

Welches Feld an welchen Aufruf geht, steht in den beiden Feldlisten unten.
Nicht jede Betriebsart-Datei geht vollständig in jeden Aufruf: Sie sind
umfangreich, und das Zeitbudget der Endanalyse ist knapp.
"""

from __future__ import annotations

import logging
import re
from functools import lru_cache
from pathlib import Path

import yaml


logger = logging.getLogger(__name__)

PATTERN_DIRECTORY = (
    Path(__file__).resolve().parents[1] / "knowledge" / "business_patterns"
)

#: Felder für den Interviewpfad - worauf sich Rückfragen stützen dürfen.
INTERVIEW_FIELDS: tuple[str, ...] = (
    "diagnostic_focus",
    "typical_workflows",
    "channels",
    "diagnostic_signals",
    "do_not_assume",
    "diagnostically_relevant_questions",
    "typical_exceptions",
    "required_information",
)

#: Felder für die Endanalyse - Wortschatz und typische Engpässe.
FINAL_ANALYSIS_FIELDS: tuple[str, ...] = (
    "diagnostic_focus",
    "typical_workflows",
    "channels",
    "diagnostic_signals",
    "do_not_assume",
    "domain_vocabulary",
    "important_entities",
    "typical_statuses",
    "typical_handoffs",
    "typical_bottlenecks",
    "realistic_customer_language",
    "realistic_worker_language",
)


#: Vorauswahl über den Betriebstyp. Nur A, D und E haben derzeit eine
#: Wissensdatei; die übrigen Buchstaben laden bewusst nichts, bis die
#: Dateien geschrieben sind.
BUSINESS_TYPE_TO_PATTERN: dict[str, str] = {
    typ: buchstabe
    for buchstabe, typen in {
        "A": (
            "hausmeisterservice", "elektriker", "maler", "sanitaer", "dachdecker",
            "reinigungsservice", "mobiler_reparaturdienst", "gartenpflege",
            "physischer_servicebetrieb", "mobiler_servicebetrieb",
        ),
        "B": ("kfz_werkstatt", "fahrradwerkstatt", "schuhmacher", "schneiderei"),
        "C": (
            "friseur", "kosmetik", "massage", "fitnessstudio", "fahrschule",
            "physiotherapie",
        ),
        "D": (
            "fotograf", "architekturbuero", "kreativagentur", "kleine_agentur",
            "freelancer", "b2b_agentur", "designer",
        ),
        "E": (
            "blumenladen", "konditorei", "einzelhandel", "onlinehandel",
            "kleine_manufaktur", "catering", "veranstaltungsdienstleister",
        ),
        "F": (
            "coach", "mentor", "berater", "beratungsteam", "b2b_dienstleister",
            "virtuelle_assistenz",
        ),
        "G": ("hausverwaltung", "immobilienmakler", "kfz_gutachter", "ferienwohnung"),
    }.items()
    for typ in typen
}

#: Woran ein gewählter Prozess eine andere Betriebsart verrät. Derselbe
#: Fotograf fällt beim Kundenprojekt unter D und beim Beratungsgespräch
#: unter F - die Betriebsart hängt am Prozess, nicht am Unternehmen.
PROCESS_SIGNALS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("D", ("briefing", "freigabe", "fassung", "korrekturschleife", "entwurf",
           "gestaltung", "abnahme")),
    ("F", ("beratung", "gespräch", "gespraech", "sitzung", "coaching",
           "erstgespräch", "erstgespraech")),
    ("C", ("terminanfrage", "terminvergabe", "buchung", "behandlung")),
    ("E", ("bestellung", "lieferung", "ware", "sortiment")),
    ("A", ("einsatz", "vor ort", "baustelle", "montage", "wartung")),
)


def _normalize(value: str) -> str:
    """Macht einen Text vergleichbar: klein, ohne Satzzeichen, ohne Umlautform."""

    return " ".join(re.findall(r"[a-z0-9äöüß]+", value.casefold().replace("_", " ")))


@lru_cache(maxsize=1)
def _patterns_by_letter() -> dict[str, dict[str, object]]:
    patterns: dict[str, dict[str, object]] = {}
    if not PATTERN_DIRECTORY.is_dir():
        return patterns
    for path in sorted(PATTERN_DIRECTORY.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            logger.warning("business_pattern.unreadable file=%s", path.name)
            continue
        if not isinstance(data, dict):
            continue
        name = str(data.get("business_pattern") or "")
        buchstabe = name.split("_", 1)[0].upper()
        if buchstabe:
            patterns[buchstabe] = data
    return patterns


def _letter_from_process(selected_process: str) -> tuple[str | None, bool]:
    """Was der gewählte Prozess über die Betriebsart verrät.

    Rückgabe: (Buchstabe oder None, mehrdeutig). Die beiden Fälle sind
    verschieden — kein Signal heißt Rückfall auf die Vorauswahl,
    mehrdeutig heißt gar nichts laden.
    """

    text = _normalize(selected_process)
    if not text:
        return None, False
    matches = {
        buchstabe
        for buchstabe, signale in PROCESS_SIGNALS
        if any(signal in text for signal in signale)
    }
    if len(matches) == 1:
        return matches.pop(), False
    return None, bool(matches)


def load_business_pattern(
    business_type: str | None,
    selected_process: str = "",
) -> dict[str, object] | None:
    """Die Wissensdatei zur Betriebsart des gewählten Prozesses, oder keine.

    Der Betriebstyp aus der Klassifikation ist ein Hinweis, keine Festlegung.
    Verrät der gewählte Prozess erkennbar eine andere Betriebsart, gilt die
    des Prozesses: derselbe Fotograf fällt beim Kundenprojekt unter D und beim
    Beratungsgespräch unter F.

    Ist die Zuordnung nicht eindeutig, wird nichts geladen.
    """

    aus_typ = BUSINESS_TYPE_TO_PATTERN.get(
        _normalize(business_type or "").replace(" ", "_")
    )
    aus_prozess, mehrdeutig = _letter_from_process(selected_process)
    if mehrdeutig:
        logger.info(
            "business_pattern.ambiguous_process process=%s", selected_process[:60]
        )
        return None
    buchstabe = aus_prozess or aus_typ
    if buchstabe is None:
        logger.info(
            "business_pattern.no_match business_type=%s process=%s",
            business_type,
            selected_process[:60],
        )
        return None
    matches = _patterns_by_letter().get(buchstabe)
    if matches is None:
        logger.info(
            "business_pattern.no_file letter=%s business_type=%s",
            buchstabe,
            business_type,
        )
        return None
    logger.info(
        "business_pattern.matched letter=%s source=%s business_type=%s pattern=%s",
        buchstabe,
        "prozess" if aus_prozess else "betriebstyp",
        business_type,
        matches.get("business_pattern"),
    )
    return matches


def pattern_context(
    business_type: str | None,
    *,
    fields: tuple[str, ...],
    selected_process: str = "",
) -> dict[str, object]:
    """Die Musterdatei auf die Felder eines Aufrufs zugeschnitten."""

    pattern = load_business_pattern(business_type, selected_process)
    if pattern is None:
        return {}
    zugeschnitten = {
        name: pattern[name]
        for name in fields
        if pattern.get(name) not in (None, "", [], {})
    }
    if zugeschnitten:
        zugeschnitten["business_pattern"] = pattern.get("business_pattern", "")
    return zugeschnitten
