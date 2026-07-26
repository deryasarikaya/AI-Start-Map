from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIRECTORY))

from app.rag_service import (  # noqa: E402
    AGENT_TEST_INDEX_DIRECTORY,
    DIAGNOSTIC_TEST_INDEX_DIRECTORY,
    audit_duplicates,
    build_vector_index,
    load_agent_pattern_chunks,
    load_diagnostic_chunks,
    promote_test_indexes,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target",
        choices=("test", "promote"),
        default="test",
        help="Testindizes bauen oder bereits validierte Testindizes übernehmen.",
    )
    arguments = parser.parse_args()
    if arguments.target == "promote":
        promote_test_indexes()
        print("Validierte Testindizes wurden übernommen; der alte Index ist gesichert.")
        return
    diagnostic_chunks = load_diagnostic_chunks()
    agent_chunks = load_agent_pattern_chunks()
    for label, chunks in (("Diagnose", diagnostic_chunks), ("Agent", agent_chunks)):
        report = audit_duplicates(chunks)
        if report.duplicate_ids:
            raise RuntimeError(f"{label}-Korpus enthält doppelte IDs.")
        print(
            f"{label}: {len(chunks)} Datensätze, "
            f"{len(report.exact_content_duplicates)} exakte und "
            f"{len(report.near_duplicates)} mögliche Near-Duplicates."
        )
    build_vector_index(
        force=True,
        index_kind="diagnostic",
        output_directory=DIAGNOSTIC_TEST_INDEX_DIRECTORY,
    )
    build_vector_index(
        force=True,
        index_kind="agent",
        output_directory=AGENT_TEST_INDEX_DIRECTORY,
    )
    print("Separate Testindizes wurden erstellt; der Produktionsindex blieb unverändert.")


if __name__ == "__main__":
    main()
