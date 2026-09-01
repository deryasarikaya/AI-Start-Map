"""Die Auswertung als PDF — ein Dokument, kein Ausdruck.

**Warum nicht der Druckdialog des Browsers.**

Bisher führte der Knopf „Vollständige Auswertung als PDF" auf eine Seite,
die von selbst `window.print()` aufrief. Was dabei herauskam, hing davon
ab, was im Dialog des Kunden eingestellt war: Kopf- und Fusszeilen mit
Datum und `localhost`-Adresse, ein Skalierungsfaktor, abgeschaltete
Hintergrundfarben. Drei Kunden bekamen drei verschiedene Dokumente, und
keines davon sah aus wie etwas, das man weiterleitet.

Hier entsteht das PDF stattdessen auf dem Server: **eine** Seitengrösse,
**ein** Rand, keine Browserzeilen, Hintergrundfarben immer an. Die
Seitenaufteilung steht in `results-pdf.css` unter `@page` — nicht in den
Einstellungen eines fremden Rechners.

**Das Blatt ist geschlossen.** Gerendert wird eine Zeichenkette, kein
Netzaufruf: Die Stilvorlagen werden vorher hineingeschrieben. Damit
braucht die Erzeugung keinen laufenden Webserver, sie kann sich nicht
selbst aufrufen, und im Test kommt zweimal dasselbe Dokument heraus.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

#: Rand und Format stehen in der Vorlage unter `@page`. Chromium
#: übernimmt sie nur mit dieser Zusage — ohne sie gewönne das Format von
#: hier und die Vorlage hätte keine Kontrolle mehr über ihre eigenen
#: Seiten.
SEITE = {
    "print_background": True,
    "prefer_css_page_size": True,
    "display_header_footer": False,
}


class PdfNichtVerfuegbar(RuntimeError):
    """Der Browser für die Erzeugung fehlt.

    Kein Grund, die Auswertung selbst scheitern zu lassen: Die Seite steht
    auch ohne PDF. Der Aufrufer entscheidet, was er dem Kunden zeigt.
    """


async def aus_html(html: str) -> bytes:
    """Fertiges HTML zu einem A4-Dokument.

    Erwartet ein Dokument, das sich selbst genügt — die Stilvorlagen also
    schon enthält. `set_content` lädt nichts nach, was relativ verlinkt
    ist; ein `<link href="/styles.css">` bliebe stumm und der Bericht käme
    unformatiert heraus.
    """

    try:
        from playwright.async_api import async_playwright
    except ImportError as fehler:  # pragma: no cover - Umgebungsfrage
        raise PdfNichtVerfuegbar("playwright ist nicht installiert") from fehler

    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            try:
                seite = await browser.new_page()
                await seite.set_content(html, wait_until="load")
                # Webfonts sind sonst noch nicht da, wenn gedruckt wird —
                # und dann bricht der Text an anderen Stellen um als am
                # Bildschirm.
                await seite.evaluate("() => document.fonts.ready")
                return await seite.pdf(**SEITE)
            finally:
                await browser.close()
    except PdfNichtVerfuegbar:
        raise
    except Exception as fehler:  # pragma: no cover - Umgebungsfrage
        raise PdfNichtVerfuegbar(str(fehler)) from fehler


def aus_html_synchron(html: str) -> bytes:
    """Dasselbe ausserhalb einer laufenden Schleife — für Tests und Skripte."""

    return asyncio.run(aus_html(html))


def dateiname(datum: str) -> str:
    """Wie die Datei beim Kunden im Ordner heisst.

    Sie landet in einem Download-Ordner neben hundert anderen und wird
    später an eine Mail gehängt. `report.pdf` wäre dort nicht wiederzu-
    finden — der Name muss allein sagen, was das ist.
    """

    sauber = "".join(z for z in datum if z.isalnum() or z in "-.").strip(".")
    return f"AI-Start-Map-Auswertung-{sauber}.pdf" if sauber else "AI-Start-Map-Auswertung.pdf"


def stilvorlage(name: str) -> str:
    """Eine Stilvorlage als Text, zum Hineinschreiben ins Dokument."""

    pfad = Path(__file__).resolve().parent / "static" / name.lstrip("/")
    return pfad.read_text(encoding="utf-8")
