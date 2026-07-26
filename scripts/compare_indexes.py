from __future__ import annotations

from pathlib import Path
import sys

import faiss
import numpy as np


ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIRECTORY))

from app.rag_service import _load_index_from, embed_texts, validate_index  # noqa: E402


LEGACY_BACKUP_DIRECTORY = Path("data/vector_index_backup_pre_batch04")
BASELINE_DIRECTORY = (
    LEGACY_BACKUP_DIRECTORY
    if LEGACY_BACKUP_DIRECTORY.is_dir()
    else Path("data/vector_index")
)
INDEX_DIRECTORIES = (
    BASELINE_DIRECTORY,
    Path("data/vector_index_test"),
    Path("data/agent_pattern_index_test"),
)
QUERIES = (
    "Papierzettel Regalsuche Schuhreparatur Auftrag finden",
    "Termine aus Telefon WhatsApp und Instagram zusammenführen",
    "Preisfreigabe bleibt beim Menschen",
)


def main() -> None:
    loaded = [_load_index_from(directory) for directory in INDEX_DIRECTORIES]
    legacy_index, legacy_chunks = loaded[0]
    legacy_ids = {chunk.chunk_id for chunk in legacy_chunks}
    diagnostic_ids = {chunk.chunk_id for chunk in loaded[1][1]}

    print("legacy_consistent", legacy_index.ntotal, len(legacy_chunks))
    print(
        "test_indexes_valid",
        [
            (str(directory), validate_index(directory))
            for directory in INDEX_DIRECTORIES[1:]
        ],
    )
    print("legacy_ids_preserved", len(legacy_ids), len(legacy_ids - diagnostic_ids))

    for query in QUERIES:
        print("query", query)
        query_vector = np.asarray(embed_texts([query]), dtype="float32")
        faiss.normalize_L2(query_vector)
        for directory, (index, chunks) in zip(INDEX_DIRECTORIES, loaded, strict=True):
            _scores, positions = index.search(query_vector, min(5, len(chunks)))
            results = [
                (chunks[position].chunk_id, chunks[position].chunk_type)
                for position in positions[0]
                if position >= 0
            ]
            print(directory.name, results)


if __name__ == "__main__":
    main()
