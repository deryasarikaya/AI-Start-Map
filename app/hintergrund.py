"""Die lange Analyse läuft im Worker, nicht im Browser-Request.

**Warum es diese Datei gibt.**

Der Warteschirm rief `POST /analyze` auf, und darin lief die vollständige
Analyse: drei Modellaufrufe, zusammen rund achtzig Sekunden, während der
HTTP-Request offen blieb. Für den Kunden ist langes Warten in Ordnung —
er bekommt etwas Aufwändiges. Für die Technik ist es das nicht: Ein
Sprachmodell hat keine zugesagte Laufzeit, und zwischen Browser und
Anwendung sitzen im Betrieb Reverse Proxies mit Zeitgrenzen, die deutlich
unter achtzig Sekunden liegen. Der Request stirbt dann mitten in der
Arbeit, und niemand weiß, wie weit sie gekommen war.

Deshalb dieselbe Trennung, die jede Anwendung mit langen Aufgaben macht:

    kurzer Request:  Browser → Server → „Auftrag liegt an" → sofort zurück
    lange Arbeit:                     → Worker → Modell → Ergebnis ablegen

**Was Celery hier ändert — und was nicht.** Der Katalog, der Abruf, die
Prompts und die Prüfungen bleiben unberührt. Es ändert sich nur, *wo und
wann* gerechnet wird. `run_generation` ist dieselbe Funktion wie vorher;
sie läuft jetzt nur in einem anderen Prozess.

**Der Broker ist eine Konfigurationszeile.** Hier steht ein Dateisystem-
Broker, weil er ohne Server auskommt und die Vorführung damit aus zwei
Befehlen besteht statt aus einer Installation. Für den Betrieb steht in
`CELERY_BROKER_URL` stattdessen `redis://…` — mehr ist an dieser Stelle
nicht zu tun.

**Kein Ergebnis-Backend.** Celery braucht keins: Der Zustand liegt schon
in PostgreSQL, in `partial_results` und `results`. Ein zweiter Speicher
für dieselbe Information wäre eine zweite Wahrheit.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from celery import Celery

logger = logging.getLogger(__name__)

#: Wo der Dateisystem-Broker seine Aufträge ablegt. Nur ein Umschlagplatz
#: für Nachrichten — die Daten selbst stehen in der Datenbank.
WARTESCHLANGE = Path(__file__).resolve().parents[1] / "data" / "warteschlange"


def _broker_einstellungen() -> tuple[str, dict[str, object]]:
    """Woher die Aufträge kommen.

    Steht `CELERY_BROKER_URL` in der Umgebung, gilt sie — im Betrieb wäre
    das `redis://…`. Ohne sie fällt es auf den Dateisystem-Broker zurück,
    der keinen laufenden Dienst braucht.
    """

    gesetzt = os.getenv("CELERY_BROKER_URL", "").strip()
    if gesetzt:
        return gesetzt, {}

    for ordner in ("ein", "verarbeitet", "steuerung"):
        (WARTESCHLANGE / ordner).mkdir(parents=True, exist_ok=True)
    # `control_folder` ausdrücklich setzen: Ohne ihn legt Celery seine
    # Steuerdateien im aktuellen Arbeitsverzeichnis ab — also mitten im
    # Projektstamm, wo sie in `git status` auftauchen.
    return "filesystem://", {
        "broker_transport_options": {
            "data_folder_in": str(WARTESCHLANGE / "ein"),
            "data_folder_out": str(WARTESCHLANGE / "ein"),
            "processed_folder": str(WARTESCHLANGE / "verarbeitet"),
            "control_folder": str(WARTESCHLANGE / "steuerung"),
            "store_processed": False,
        }
    }


_adresse, _optionen = _broker_einstellungen()

celery_app = Celery("ai_start_map", broker=_adresse)
celery_app.conf.update(
    **_optionen,
    # Kein Ergebnis-Backend: Der Zustand steht in PostgreSQL.
    result_backend=None,
    task_serializer="json",
    accept_content=["json"],
    timezone="Europe/Berlin",
    enable_utc=True,
    # Ein Auftrag je Worker auf einmal. Die Analyse ist rechen- und
    # wartelastig, nicht parallelisierbar, und zwei gleichzeitige Läufe
    # derselben Sitzung verhindert ohnehin die Schreibsperre.
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)


@celery_app.task(name="ai_start_map.auswertung")
def auswertung_erzeugen(session_id: int) -> str:
    """Führt die Analyse einer Sitzung aus — im Worker, nicht im Request.

    Gibt nur zurück, wie es ausgegangen ist. **Wohin das Ergebnis gehört,
    weiß die Funktion selbst:** Sie schreibt es in dieselben Tabellen wie
    vorher, und der Warteschirm liest den Stand über `/analysis-status`.
    Ein Rückgabewert, den jemand abholen müsste, wäre eine zweite Wahrheit
    neben der Datenbank.
    """

    # Erst hier importiert: Der Worker soll die Anwendung laden, wenn er
    # arbeitet — nicht schon beim Einlesen dieses Moduls, das auch der
    # Webprozess importiert.
    from app.database import SessionFactory
    from app.services import analysis_service

    with SessionFactory() as datenbank:
        nutzlast, _ = analysis_service.run_generation(session_id, datenbank)
    zustand = str(nutzlast.get("state", "unbekannt"))
    logger.info("worker.finished session=%s state=%s", session_id, zustand)
    return zustand
