"""Antworten und Vorlagen.

Die Jinja2-Konfiguration, die Weiterleitung und die Fehlerseite. Unverändert
aus `routes.py` hierher verschoben.
"""

from __future__ import annotations

import os
from functools import lru_cache
import re
from pathlib import Path
from urllib.parse import quote

from fastapi import Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.schemas import customer_plain_text

templates = Jinja2Templates(directory=Path(__file__).resolve().parents[1] / "templates")
templates.env.filters["customer_text"] = customer_plain_text

GESPRAECHS_BETREFF = 'AI Start Map – Gespräch zu meiner Auswertung'
GESPRAECHS_TEXT = (
    'Guten Tag,\n'
    '\n'
    'ich habe meine Auswertung gesehen und möchte über die Umsetzung\n'
    'sprechen.\n'
    '\n'
    'Mein Betrieb:\n'
    'Womit ich anfangen möchte:\n'
    'So bin ich erreichbar:\n'
    '\n'
    'Freundliche Grüße\n'
)


def gespraechs_adresse() -> str:
    """Der Knopf „Genau so möchte ich arbeiten" als fertige mailto-Adresse.

    Betreff und ein vorgeschriebener Text hängen mit dran: Wer auf den
    Knopf drückt, hat gerade seine eigene Auswertung gelesen und soll
    nicht vor einem leeren Fenster sitzen.

    Die Empfängeradresse steht in der Umgebungsvariable
    `KONTAKT_ADRESSE` und **nicht** im Code — eine erfundene Adresse
    würde die Anfragen ins Leere schicken. Fehlt sie, öffnet sich das
    Mailprogramm trotzdem, nur mit leerem Empfängerfeld.
    """

    empfaenger = os.getenv('KONTAKT_ADRESSE', '').strip()
    return (
        f'mailto:{quote(empfaenger, safe="@")}'
        f'?subject={quote(GESPRAECHS_BETREFF)}'
        f'&body={quote(GESPRAECHS_TEXT)}'
    )


templates.env.globals['gespraechs_adresse'] = gespraechs_adresse

#: Wo die ausgelieferten Dateien liegen. Einmal berechnet, nicht je Aufruf.
STATISCHER_ORDNER = Path(__file__).resolve().parents[1] / "static"


@lru_cache(maxsize=64)
def _stand_der_datei(name: str) -> str:
    """Der Änderungszeitpunkt einer statischen Datei als kurze Kennung."""

    datei = STATISCHER_ORDNER / name.lstrip("/")
    try:
        return f"{int(datei.stat().st_mtime):x}"
    except OSError:
        # Fehlt die Datei, hängt eben nichts dran. Ein fehlender
        # Zwischenspeicher-Schlüssel ist kein Grund, die Seite nicht
        # auszuliefern.
        return ""


def mit_stand(pfad: str) -> str:
    """Hängt an eine statische Adresse den Änderungszeitpunkt der Datei.

    **Warum es das gibt.** Der Browser hält `styles.css` fest, bis er einen
    Grund zum Nachladen hat. Während der Arbeit heisst das: Die Datei auf
    der Platte ist neu, die Seite zeigt die alte — und man sucht den Fehler
    im CSS, das man gerade richtig geschrieben hat. Nach einer
    Veröffentlichung wäre es schlimmer: Die Änderung ist drauf und kommt bei
    niemandem an.

    Ändert sich die Datei, ändert sich die Adresse. Ändert sie sich nicht,
    behält der Browser seine Kopie — das ist richtig und schnell.
    """

    stand = _stand_der_datei(pfad)
    return f"/static{pfad}?v={stand}" if stand else f"/static{pfad}"


templates.env.globals["statisch"] = mit_stand


# Wonach ein Kanalzeichen gesucht wird. Die Reihenfolge entscheidet: Das
# erste passende Wort gewinnt, damit „WhatsApp-Nachricht" nicht als
# allgemeine Nachricht endet.
KANALWOERTER: tuple[tuple[str, str], ...] = (
    ("whatsapp", "i-whatsapp"),
    ("sprachnotiz", "i-sprache"),
    ("sprachnachricht", "i-sprache"),
    ("anrufnotiz", "i-telefon"),
    ("telefon", "i-telefon"),
    ("anruf", "i-telefon"),
    ("rückruf", "i-telefon"),
    ("e-mail", "i-mail"),
    ("email", "i-mail"),
    ("mail", "i-mail"),
    ("postfach", "i-mail"),
    ("formular", "i-formular"),
    ("website", "i-formular"),
    ("webseite", "i-formular"),
    ("online", "i-formular"),
    ("portal", "i-formular"),
    ("foto", "i-foto"),
    ("bild", "i-foto"),
    ("scan", "i-foto"),
    ("aufnahme", "i-foto"),
    ("pdf", "i-dokument"),
    ("dokument", "i-dokument"),
    ("beleg", "i-dokument"),
    ("rechnung", "i-dokument"),
    ("unterlage", "i-dokument"),
    ("anhang", "i-dokument"),
    ("brief", "i-brief"),
    ("post", "i-brief"),
    ("sms", "i-chat"),
    ("chat", "i-chat"),
    ("nachricht", "i-chat"),
    ("anfrage", "i-chat"),
)


def kanalsymbol(text: str) -> str:
    """Das Zeichen zu einem Eingangskanal, oder das allgemeine.

    Gesucht wird im Text des Knotens, so wie das Modell ihn geschrieben hat —
    „E-Mails und Anhänge", „WhatsApp-Gruppe der Monteure", „Scans und Fotos".
    Trifft nichts, bleibt es beim Eingangszeichen; erfunden wird nichts.
    """

    klein = text.casefold()
    for wort, symbol in KANALWOERTER:
        if wort in klein:
            return symbol
    return "i-eingang"


templates.env.filters["kanalsymbol"] = kanalsymbol

# Ausgeschriebene Zahlwörter. „Acht Leute" ist genauso seine Angabe wie
# „450 Einheiten" — nur schreibt er das eine aus und das andere nicht.
# „ein"/„eine" fehlen mit Absicht: Eins ist nie eine interessante Menge, und
# als Artikel stünde es in jedem zweiten Satz („eine Liste", „ein Termin").
ZAHLWOERTER = (
    "zwei",
    "drei",
    "vier",
    "fünf",
    "sechs",
    "sieben",
    "acht",
    "neun",
    "zehn",
    "elf",
    "zwölf",
)

#: Eine Mengenangabe: „450", „~620", „70 oder 80", „250 bis 320",
#: „Sechs bis acht".
_MENGE = r"(?:[~≈]?\s*\d[\d.,]*|" + "|".join(ZAHLWOERTER) + r")"
ZAHL_IM_SATZ = re.compile(
    r"\b(" + _MENGE + r"(?:\s*(?:bis|oder|–|-)\s*" + _MENGE + r")?)"
    r"\s+((?:\w+[-\w]*\s*){1,2})",
    re.IGNORECASE,
)

# Steht eine davon vor der Zahl, ist es ein Zeitpunkt und keine Menge:
# „in zwei Tagen", „seit drei Wochen", „nach zehn Minuten".
ZEITWOERTER = frozenset("in seit vor nach binnen innerhalb ab um".split())


def zahl_im_satz(text: str) -> dict[str, str] | None:
    """Holt die erste Mengenangabe samt Bezeichnung aus einem Satz.

    „…sind da teilweise 70 oder 80 neue E-Mails." wird zu
    `{"zahl": "70 oder 80", "wort": "neue E-Mails"}`. Steht keine Menge
    darin, kommt nichts zurück — dann trägt der Satz keine Zahl, und eine
    zu erfinden wäre genau der Fehler, den diese Seite vermeidet.

    **Nicht jede Zahl ist eine Menge.** „In zwei Minuten draufgucken" ist
    eine Redewendung, „Kurse, die in zwei Tagen stattfinden" ein Zeitpunkt.
    Gross gesetzt behaupteten beide, hier sei etwas gemessen worden.
    Deshalb: was gezählt wird, muss ein Substantiv sein — im Deutschen gross
    geschrieben —, und vor der Zahl darf keine Zeitpräposition stehen.

    Beide Teile stehen wörtlich in dem, was der Kunde gesagt hat; sie werden
    nur getrennt gesetzt, damit die Zahl gross erscheinen kann.
    """

    for treffer in ZAHL_IM_SATZ.finditer(text.strip()):
        davor = text[: treffer.start()].split()
        if davor and davor[-1].strip(",.;:").casefold() in ZEITWOERTER:
            continue

        woerter = treffer.group(2).split()
        while woerter and not woerter[-1].strip(",.;:")[:1].isupper():
            woerter.pop()
        if not woerter:
            continue

        return {
            "zahl": " ".join(treffer.group(1).split()),
            "wort": " ".join(woerter).strip(",.;:"),
        }
    return None


templates.env.filters["zahl_im_satz"] = zahl_im_satz

# Woran man eine Veränderung erkennt, bevor man sie liest. Wie bei den
# Kanälen: ein geteilter Wortschatz kleiner Betriebe, keine Vorlage für
# eine bestimmte Branche. Die Reihenfolge entscheidet — das erste passende
# Wort gewinnt.
WANDELWOERTER: tuple[tuple[str, str], ...] = (
    ("erinner", "i-glocke"),
    ("frist", "i-glocke"),
    ("fällig", "i-glocke"),
    ("benachrichtig", "i-glocke"),
    ("akte", "i-akte"),
    ("vorgang", "i-akte"),
    ("ablage", "i-akte"),
    ("dokument", "i-akte"),
    ("beleg", "i-akte"),
    ("zuordn", "i-verbindung"),
    ("verknüpf", "i-verbindung"),
    ("verbind", "i-verbindung"),
    ("übernomm", "i-verbindung"),
    ("abgleich", "i-verbindung"),
    ("synchron", "i-verbindung"),
    ("eingang", "i-eingang"),
    ("postfach", "i-mail"),
    ("e-mail", "i-mail"),
    ("nachricht", "i-chat"),
    ("zuständig", "i-person"),
    ("person", "i-person"),
    ("team", "i-person"),
    ("übersicht", "i-schluessel"),
    ("status", "i-schluessel"),
    ("priorit", "i-schluessel"),
    ("automatisch", "i-schluessel"),
)


def wandelsymbol(text: str) -> str:
    """Das Zeichen zu einer Veränderung, oder das allgemeine Häkchen.

    Gesucht wird in dem Satz, den das Modell geschrieben hat. Trifft nichts,
    bleibt es beim Haken — erfunden wird kein Sinn, der nicht dasteht.
    """

    klein = text.casefold()
    for wort, symbol in WANDELWOERTER:
        if wort in klein:
            return symbol
    return "i-haken"


templates.env.filters["wandelsymbol"] = wandelsymbol

# Was eine Lösung dieser Art dem Betrieb abnimmt. Der Hinweis an der
# Hauptansicht sagt genau das und nichts darüber hinaus — ein Satz für alle
# Typen behauptete für den Telefonassistenten dasselbe wie für die
# Dokumentenablage.
AUTOMATISIERT: dict[str, str] = {
    "uebersicht": "Automatisch zusammengeführt",
    "vorgangsakte": "Automatisch zusammengetragen",
    "eingangspruefung": "Automatisch erkannt und eingeordnet",
    "nachrichtenverlauf": "Standardanfragen automatisch beantwortet",
    "kundenakte": "Verlauf automatisch mitgeführt",
    "terminuebersicht": "Automatisch geplant und erinnert",
    "aussenansicht": "Stand automatisch aktuell",
    "dokumentenablage": "Automatisch erkannt und zugeordnet",
    "telefonassistent": "Der Assistent nimmt den Anruf auf",
}


def automatisiert(typ: str) -> str:
    """Der Hinweis zu einem Ansichtstyp.

    Unbekannter Typ — etwa weil ein neuer dazugekommen ist und hier vergessen
    wurde — bekommt den allgemeinen Satz. Lieber unspezifisch als falsch.
    """

    return AUTOMATISIERT.get(typ, "Automatisch vorbereitet")


templates.env.filters["automatisiert"] = automatisiert





PREVIEW_NOTICE = (
    "Beispielangaben zur Veranschaulichung \u2013 hier stehen sp\u00e4ter deine "
    "tats\u00e4chlichen Angaben."
)


def redirect_response(path: str) -> RedirectResponse:
    """Eine Weiterleitung mit Statuscode 303.

    303 und nicht 302, damit der Browser nach einem Formular einen GET
    schickt und ein Neuladen nichts doppelt abschickt.
    """

    return RedirectResponse(path, status_code=status.HTTP_303_SEE_OTHER)


def render_error(
    request: Request,
    message: str,
    *,
    status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
    retry_path: str | None = None,
) -> HTMLResponse:
    """Die Fehlerseite mit einer Meldung und optional einem Weg zurück."""

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "error_title": "Die Analyse konnte nicht fortgesetzt werden.",
            "error_message": message,
            "retry_path": retry_path,
            "error_code": status_code,
        },
        status_code=status_code,
    )
