"""Aus welchem Stand ist ein Ergebnis entstanden?

**Wozu.** Ein Auswertungsergebnis ist nur so viel wert wie die Antwort auf
die Frage, woraus es entstanden ist. Code, Prompts, Vertrag, Katalog und
Index aendern sich unabhaengig voneinander; laeuft dann noch ein Prozess
mit einem aelteren Stand, ist keine Messung mehr zuordenbar.

Dieses Skript liest nur. Es aendert nichts und ruft kein Modell auf.

    python scripts/laufstempel.py            # lesbar
    python scripts/laufstempel.py --json     # zum Mitspeichern

Die Ausgabe gehoert neben jede Messung. Zwei Messungen mit verschiedenen
Stempeln sind nicht vergleichbar - auch dann nicht, wenn beide gruen sind.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WURZEL))


def _hash(pfad: Path) -> str:
    """Kurzer Inhaltsabdruck einer Datei."""

    return hashlib.sha256(pfad.read_bytes()).hexdigest()[:12]


def _git(*argumente: str) -> str:
    ergebnis = subprocess.run(
        ["git", *argumente], capture_output=True, text=True, cwd=WURZEL
    )
    return ergebnis.stdout.strip()


def stempel() -> dict[str, object]:
    """Alles, was ein Ergebnis erklaert - als eine Struktur."""

    from dotenv import load_dotenv

    load_dotenv(WURZEL / ".env")

    from app import solution_catalog

    prompts = {
        pfad.name: _hash(pfad)
        for pfad in sorted((WURZEL / "app/prompts").glob("*.md"))
    }

    index_datei = WURZEL / "data/solution_architecture_index/manifest.json"
    index: dict[str, object] = {}
    if index_datei.is_file():
        roh = json.loads(index_datei.read_text(encoding="utf-8"))
        index = {
            "chunks": roh.get("chunk_count"),
            "einbettungsmodell": roh.get("embedding_model"),
            "korpus_hash": str(roh.get("corpus_hash", ""))[:12],
            "evaluationen_ausgeschlossen": roh.get("excluded_evaluations"),
        }

    # **Der schmutzige Arbeitsbaum ist das wichtigste Feld.** Ist er nicht
    # sauber, gehoert das Ergebnis zu keinem Commit - und die Messung ist
    # nicht wiederholbar, egal wie gut die Zahlen aussehen.
    offen = _git("status", "--porcelain")

    return {
        "code": {
            "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
            "commit": _git("rev-parse", "HEAD")[:12],
            "sauber": not offen,
            "offene_dateien": [z[3:] for z in offen.splitlines()] if offen else [],
        },
        "prompts": prompts,
        "vertrag": {
            "result_schema": _hash(WURZEL / "app/result_schema.py"),
        },
        "katalog": {
            "freigabe": _hash(WURZEL / "knowledge/catalog/FREIGABE.json"),
            "familien": len(solution_catalog.katalog()),
        },
        "index": index,
        "modell": {
            "sprachmodell": os.getenv("OPENAI_MODEL"),
            "einbettungsmodell": os.getenv("OPENAI_EMBEDDING_MODEL"),
        },
    }


def _zeige(daten: dict[str, object], tiefe: int = 0) -> None:
    for name, wert in daten.items():
        if isinstance(wert, dict):
            print("  " * tiefe + f"{name}:")
            _zeige(wert, tiefe + 1)
        else:
            print("  " * tiefe + f"{name}: {wert}")


def main() -> int:
    daten = stempel()
    if "--json" in sys.argv:
        print(json.dumps(daten, ensure_ascii=False, indent=1))
    else:
        _zeige(daten)
        if not daten["code"]["sauber"]:  # type: ignore[index]
            print("\nACHTUNG: Der Arbeitsbaum ist nicht sauber.")
            print("Eine Messung aus diesem Stand gehoert zu keinem Commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
