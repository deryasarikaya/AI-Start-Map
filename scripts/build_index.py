from __future__ import annotations

import sys
from pathlib import Path


ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIRECTORY))

from app.rag_service import build_vector_index, load_curated_chunks  # noqa: E402


def main() -> None:
    chunk_count = len(load_curated_chunks())
    created = build_vector_index()
    if created:
        print(f"Wissensindex mit {chunk_count} kuratierten Chunks erstellt.")
    else:
        print(f"Wissensindex ist aktuell ({chunk_count} kuratierte Chunks).")


if __name__ == "__main__":
    main()
