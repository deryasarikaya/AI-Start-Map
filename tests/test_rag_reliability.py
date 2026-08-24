from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

import faiss
import numpy as np
import pytest

import app.agent_service as agent_service
import app.rag_service as rag_service


def _chunk(chunk_id: str, content: str) -> rag_service.KnowledgeChunk:
    return rag_service.KnowledgeChunk(
        chunk_id=chunk_id,
        chunk_type="diagnostic_pattern",
        title=chunk_id,
        content=content,
        source_file="knowledge/test.jsonl",
        metadata={
            "batch_id": "test",
            "source_ids": ["test"],
            "source_strength": "high",
            "content_origin": "test",
            "is_primary_evidence": False,
            "industry": [],
            "process_type": [],
            "digital_maturity_level": "unknown",
            "pattern_ids": [],
            "guardrail_ids": [],
        },
    )


def _write_index(
    directory: Path, *, kind: rag_service.IndexKind, marker: str
) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    index = faiss.IndexFlatIP(2)
    index.add(np.asarray([[1.0, 0.0]], dtype="float32"))
    faiss.write_index(index, str(directory / rag_service.INDEX_FILE_NAME))
    chunk = _chunk(f"{kind}-{marker}", marker)
    (directory / rag_service.METADATA_FILE_NAME).write_text(
        json.dumps([asdict(chunk)], ensure_ascii=False),
        encoding="utf-8",
    )
    (directory / rag_service.MANIFEST_FILE_NAME).write_text(
        json.dumps(
            {
                "index_kind": kind,
                "chunk_count": 1,
                "embedding_model": "test",
                "corpus_hash": marker,
                "excluded_evaluations": True,
            }
        ),
        encoding="utf-8",
    )


def test_search_skips_empty_cleaned_chunks_and_keeps_valid_chunks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    empty = _chunk("empty", "```yaml\nchunk_id: empty\n```")
    valid = _chunk("valid", "Inhalt bleibt erhalten.")
    monkeypatch.setattr(
        agent_service,
        "retrieve_chunks",
        lambda query, *, phase: [empty, valid],
    )

    evidence = agent_service.search_diagnostic_knowledge("Test")

    assert [item.chunk_id for item in evidence] == ["valid"]
    assert [item.content for item in evidence] == ["Inhalt bleibt erhalten."]


def test_two_promotes_create_complete_separate_backups(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    production_diagnostic = tmp_path / "production-diagnostic"
    production_agent = tmp_path / "production-agent"
    test_diagnostic = tmp_path / "test-diagnostic"
    test_agent = tmp_path / "test-agent"
    backups = tmp_path / "backups"
    _write_index(production_diagnostic, kind="diagnostic", marker="production-1")
    _write_index(production_agent, kind="agent", marker="production-1")
    _write_index(test_diagnostic, kind="diagnostic", marker="test-1")
    _write_index(test_agent, kind="agent", marker="test-1")
    monkeypatch.setattr(rag_service, "INDEX_DIRECTORY", production_diagnostic)
    monkeypatch.setattr(rag_service, "AGENT_INDEX_DIRECTORY", production_agent)
    monkeypatch.setattr(
        rag_service, "DIAGNOSTIC_TEST_INDEX_DIRECTORY", test_diagnostic
    )
    monkeypatch.setattr(rag_service, "AGENT_TEST_INDEX_DIRECTORY", test_agent)
    monkeypatch.setattr(rag_service, "INDEX_BACKUP_DIRECTORY", backups)
    rag_service._invalidate_index_cache()

    rag_service.promote_test_indexes()
    _write_index(test_diagnostic, kind="diagnostic", marker="test-2")
    _write_index(test_agent, kind="agent", marker="test-2")
    rag_service.promote_test_indexes()

    backup_directories = sorted(path for path in backups.iterdir() if path.is_dir())
    assert len(backup_directories) == 2
    for backup_directory in backup_directories:
        assert rag_service.validate_index(
            backup_directory / "diagnostic", expected_kind="diagnostic"
        )["chunk_count"] == 1
        assert rag_service.validate_index(
            backup_directory / "agent", expected_kind="agent"
        )["chunk_count"] == 1
    assert rag_service.validate_index(
        production_diagnostic, expected_kind="diagnostic"
    )["corpus_hash"] == "test-2"
    assert rag_service.validate_index(
        production_agent, expected_kind="agent"
    )["corpus_hash"] == "test-2"


def test_index_cache_reuses_load_and_invalidates_on_mtime_change(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    directory = tmp_path / "index"
    _write_index(directory, kind="diagnostic", marker="first")
    rag_service._invalidate_index_cache()
    real_read_index = rag_service.faiss.read_index
    read_count = 0

    def counted_read_index(path: str) -> Any:
        nonlocal read_count
        read_count += 1
        return real_read_index(path)

    monkeypatch.setattr(rag_service.faiss, "read_index", counted_read_index)

    first_index, first_chunks = rag_service._load_index_from(directory)
    second_index, second_chunks = rag_service._load_index_from(directory)

    assert read_count == 1
    assert second_index is first_index
    assert second_chunks is first_chunks

    metadata_file = directory / rag_service.METADATA_FILE_NAME
    raw_chunks = json.loads(metadata_file.read_text(encoding="utf-8"))
    raw_chunks[0]["content"] = "changed"
    metadata_file.write_text(json.dumps(raw_chunks), encoding="utf-8")
    changed_mtime = metadata_file.stat().st_mtime_ns + 1_000_000_000
    os.utime(metadata_file, ns=(changed_mtime, changed_mtime))

    _third_index, third_chunks = rag_service._load_index_from(directory)

    assert read_count == 2
    assert third_chunks[0].content == "changed"


def test_missing_index_files_still_raise_configuration_error(tmp_path: Path) -> None:
    rag_service._invalidate_index_cache()

    with pytest.raises(rag_service.RagConfigurationError, match="Wissensindex fehlt"):
        rag_service._load_index_from(tmp_path / "missing")
