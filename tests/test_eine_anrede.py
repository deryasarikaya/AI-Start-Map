"""Eine Anrede auf der ganzen Strecke.

Der Eingang duzte, die Auswertung siezte, und der Zwischenschirm, der über
allen Seiten liegt, duzte auch dort, wo die Seite darunter schon siezte.
Der Bruch kam für den Kunden nach dem ersten Klick.

Das ist genau die Art Fehler, die ohne Wächter zurückkommt: Jemand
schreibt ein neues Formular, kopiert eine Zeile aus einer alten Vorlage,
und die Mischform ist wieder da — ohne dass ein Test rot wird.

Die Regel gilt für **jede** Vorlage und für das Skript. Kommentare sind
ausgenommen: Sie zitieren, was dort einmal stand, und genau dieses Zitat
macht die Änderung nachvollziehbar.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[1]
VORLAGEN = sorted((WURZEL / "app/templates").glob("*.html"))

#: Wortformen, die auf ein Duzen hindeuten. Als Wortgrenzen, damit
#: „Dokument" oder „Handeuten" nicht mitgezählt werden.
DUZEN = re.compile(
    r"\b(du|dir|dich|dein|deine|deinem|deinen|deiner|deines|euch|euer|eure)\b",
    re.IGNORECASE,
)


def _ohne_kommentare(vorlage: str) -> str:
    """Der sichtbare Text — Jinja-Kommentare fallen weg.

    In den Kommentaren steht bewusst, wie ein Satz **vorher** hiess. Diese
    Zitate sind der Grund, warum die Änderung später noch verständlich
    ist; sie dürfen keinen Test rot machen.
    """

    return re.sub(r"\{#.*?#\}", " ", vorlage, flags=re.DOTALL)


@pytest.mark.parametrize("pfad", VORLAGEN, ids=lambda p: p.name)
def test_no_template_says_du(pfad: Path) -> None:
    """Keine Vorlage duzt.

    Auch nicht in einem Platzhalter, einem Knopftext oder einem
    `data-`-Attribut — der Zwischenschirm hat gezeigt, dass genau dort das
    letzte „du" überlebt.
    """

    sichtbar = _ohne_kommentare(pfad.read_text(encoding="utf-8"))

    treffer = sorted(set(DUZEN.findall(sichtbar)))

    assert not treffer, f"{pfad.name} duzt: {treffer}"


def test_the_script_says_sie_too() -> None:
    """Auch die Meldungen aus dem Skript.

    Die Spracheingabe meldet sich mit eigenen Sätzen — beim Start, beim
    Pausieren, im Fehlerfall. Sie stehen in keiner Vorlage und sind
    deshalb beim ersten Durchgang übersehen worden.
    """

    skript = (WURZEL / "app/static/app.js").read_text(encoding="utf-8")
    # Nur die Zeichenketten prüfen, nicht den Code: `document` enthält kein
    # „du", aber eine Variable könnte es.
    texte = " ".join(re.findall(r'"([^"]{4,})"', skript))

    treffer = sorted(set(DUZEN.findall(texte)))

    assert not treffer, f"app.js duzt: {treffer}"


#: Wendungen, die zur Kürze auffordern. Nicht die blosse Zeichenfolge
#: „kurz": `kurzfassung` ist ein Feldname und `Kurzfassung` ein
#: Abschnittstitel — beide sagen nichts über die Länge einer Erzählung.
KUERZE = (
    "erzähl kurz",
    "erzählen sie kurz",
    "schreib kurz",
    "schreiben sie kurz",
    "beschreib kurz",
    "beschreiben sie kurz",
    "kurz,",
    "in wenigen sätzen",
    "30 sekunden",
    "maximal",
)


def test_no_page_asks_for_brevity() -> None:
    """Und keine Seite bittet um Kürze.

    „Erzähl mir kurz" stand einmal auf der Interview-Seite und dreimal auf
    der Startseite — und wer glaubt, er solle sich kurzfassen, lässt genau
    die Nebensätze weg, aus denen die Diagnose lebt. Die Regel galt lange
    nur dort, wo sie ausgesprochen wurde; deshalb steht sie hier für alle.
    """

    for pfad in VORLAGEN:
        sichtbar = _ohne_kommentare(pfad.read_text(encoding="utf-8")).lower()
        for wendung in KUERZE:
            assert wendung not in sichtbar, f"{pfad.name}: {wendung}"
