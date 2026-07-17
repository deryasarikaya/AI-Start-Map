from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app.openai_service import embed_texts, get_embedding_model


ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
CURATED_DIRECTORY = ROOT_DIRECTORY / "knowledge" / "curated"
INDEX_DIRECTORY = ROOT_DIRECTORY / "data" / "vector_index"
INDEX_FILE = INDEX_DIRECTORY / "knowledge.faiss"
METADATA_FILE = INDEX_DIRECTORY / "chunks.json"
MANIFEST_FILE = INDEX_DIRECTORY / "manifest.json"
CHUNK_HEADING = re.compile(r"^## Chunk:\s*(.+)$", re.MULTILINE)
YAML_BLOCK = re.compile(r"```yaml\s*\n(.*?)```", re.DOTALL)


class RagConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True)
class KnowledgeChunk:
    chunk_id: str
    chunk_type: str
    title: str
    content: str
    source_file: str
    metadata: dict[str, Any]


def _metadata_value(raw_value: str) -> Any:
    value = raw_value.strip()
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value.strip('"')


def _parse_metadata(metadata_text: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for line in metadata_text.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        metadata[key.strip()] = _metadata_value(raw_value)
    return metadata


def _parse_file(path: Path) -> list[KnowledgeChunk]:
    text = path.read_text(encoding="utf-8")
    matches = list(CHUNK_HEADING.finditer(text))
    chunks: list[KnowledgeChunk] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        chunk_text = text[match.start():end].strip()
        yaml_match = YAML_BLOCK.search(chunk_text)
        if yaml_match is None:
            raise RagConfigurationError(
                f"Im Wissens-Chunk in {path.name} fehlen die Metadaten."
            )
        metadata = _parse_metadata(yaml_match.group(1))
        chunk_id = str(metadata.get("chunk_id", "")).strip()
        chunk_type = str(metadata.get("chunk_type", "")).strip()
        if not chunk_id or not chunk_type:
            raise RagConfigurationError(
                f"Ein Wissens-Chunk in {path.name} hat keine ID oder keinen Typ."
            )
        chunks.append(
            KnowledgeChunk(
                chunk_id=chunk_id,
                chunk_type=chunk_type,
                title=match.group(1).strip(),
                content=chunk_text,
                source_file=path.name,
                metadata=metadata,
            )
        )
    return chunks


def load_curated_chunks(
    curated_directory: Path = CURATED_DIRECTORY,
) -> list[KnowledgeChunk]:
    if not curated_directory.is_dir():
        raise RagConfigurationError(
            "Die kuratierte Wissensbasis wurde nicht gefunden."
        )
    files = sorted(curated_directory.glob("*.md"))
    if not files:
        raise RagConfigurationError(
            "In der kuratierten Wissensbasis wurden keine Dateien gefunden."
        )
    chunks = [chunk for path in files for chunk in _parse_file(path)]
    if not chunks:
        raise RagConfigurationError("Die kuratierte Wissensbasis enthält keine Chunks.")
    return chunks


def _corpus_hash(chunks: list[KnowledgeChunk], embedding_model: str) -> str:
    digest = hashlib.sha256(embedding_model.encode("utf-8"))
    for chunk in chunks:
        digest.update(chunk.source_file.encode("utf-8"))
        digest.update(chunk.content.encode("utf-8"))
    return digest.hexdigest()


def build_vector_index(*, force: bool = False) -> bool:
    chunks = load_curated_chunks()
    embedding_model = get_embedding_model()
    corpus_hash = _corpus_hash(chunks, embedding_model)
    index_is_current = (
        MANIFEST_FILE.is_file()
        and INDEX_FILE.is_file()
        and METADATA_FILE.is_file()
    )
    if not force and index_is_current:
        manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
        if manifest.get("corpus_hash") == corpus_hash:
            return False

    embeddings = np.asarray(
        embed_texts([chunk.content for chunk in chunks]),
        dtype="float32",
    )
    if embeddings.ndim != 2 or embeddings.shape[0] != len(chunks):
        raise RagConfigurationError("Die erzeugten Wissensvektoren sind unvollständig.")
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    INDEX_DIRECTORY.mkdir(parents=True, exist_ok=True)
    temporary_index = INDEX_DIRECTORY / "knowledge.faiss.tmp"
    faiss.write_index(index, str(temporary_index))
    temporary_index.replace(INDEX_FILE)
    METADATA_FILE.write_text(
        json.dumps([asdict(chunk) for chunk in chunks], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    MANIFEST_FILE.write_text(
        json.dumps(
            {
                "corpus_hash": corpus_hash,
                "embedding_model": embedding_model,
                "chunk_count": len(chunks),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return True


def _load_index() -> tuple[Any, list[KnowledgeChunk]]:
    if not INDEX_FILE.is_file() or not METADATA_FILE.is_file():
        raise RagConfigurationError(
            "Der Wissensindex fehlt. Führe zuerst python scripts/build_index.py aus."
        )
    raw_chunks = json.loads(METADATA_FILE.read_text(encoding="utf-8"))
    chunks = [KnowledgeChunk(**raw_chunk) for raw_chunk in raw_chunks]
    index = faiss.read_index(str(INDEX_FILE))
    if index.ntotal != len(chunks):
        raise RagConfigurationError("Wissensindex und Metadaten passen nicht zusammen.")
    return index, chunks


PHASE_TYPES = {
    "suggestion": {
        "allowed": {"case_evidence", "diagnostic_pattern", "automation_guardrail"},
        "required": ("diagnostic_pattern", "automation_guardrail"),
    },
    "follow_up": {
        "allowed": {
            "interview_question_set",
            "diagnostic_pattern",
            "automation_guardrail",
        },
        "required": (
            "interview_question_set",
            "diagnostic_pattern",
            "automation_guardrail",
        ),
    },
    "analysis": {
        "allowed": {
            "case_evidence",
            "diagnostic_pattern",
            "automation_pattern",
            "automation_guardrail",
        },
        "required": ("diagnostic_pattern", "automation_guardrail"),
    },
}


def _top_k() -> int:
    try:
        top_k = int(os.getenv("RAG_TOP_K", "6"))
    except ValueError as error:
        raise RagConfigurationError("RAG_TOP_K muss eine positive Zahl sein.") from error
    if top_k < 1:
        raise RagConfigurationError("RAG_TOP_K muss eine positive Zahl sein.")
    return top_k


def _diverse_selection(
    ranked_chunks: list[KnowledgeChunk],
    *,
    required_types: tuple[str, ...],
    top_k: int,
) -> list[KnowledgeChunk]:
    selected: list[KnowledgeChunk] = []
    selected_ids: set[str] = set()
    evidence_by_pattern: dict[str, int] = {}

    def add(chunk: KnowledgeChunk) -> bool:
        if chunk.chunk_id in selected_ids or len(selected) >= top_k:
            return False
        if chunk.chunk_type == "case_evidence":
            pattern = str(
                chunk.metadata.get("pattern_id")
                or chunk.metadata.get("case_id")
                or chunk.chunk_id
            )
            if evidence_by_pattern.get(pattern, 0) >= 2:
                return False
            evidence_by_pattern[pattern] = evidence_by_pattern.get(pattern, 0) + 1
        selected.append(chunk)
        selected_ids.add(chunk.chunk_id)
        return True

    for required_type in required_types:
        matching = next(
            (chunk for chunk in ranked_chunks if chunk.chunk_type == required_type),
            None,
        )
        if matching is not None:
            add(matching)
    for chunk in ranked_chunks:
        add(chunk)
        if len(selected) == top_k:
            break
    return selected


def retrieve_chunks(
    query: str,
    *,
    phase: str,
    top_k: int | None = None,
) -> list[KnowledgeChunk]:
    phase_configuration = PHASE_TYPES.get(phase)
    if phase_configuration is None:
        raise ValueError(f"Unbekannte Analysephase: {phase}")
    index, chunks = _load_index()
    query_vector = np.asarray(embed_texts([query]), dtype="float32")
    if query_vector.ndim != 2 or query_vector.shape[0] != 1:
        raise RagConfigurationError("Die Suchanfrage konnte nicht vorbereitet werden.")
    faiss.normalize_L2(query_vector)
    requested_count = top_k or _top_k()
    result_count = len(chunks)
    _scores, positions = index.search(query_vector, result_count)
    ranked = [
        chunks[position]
        for position in positions[0]
        if position >= 0
        and chunks[position].chunk_type in phase_configuration["allowed"]
    ]
    return _diverse_selection(
        ranked,
        required_types=phase_configuration["required"],
        top_k=requested_count,
    )


def format_chunks_for_prompt(chunks: list[KnowledgeChunk]) -> list[str]:
    return [
        json.dumps(
            {
                "chunk_id": chunk.chunk_id,
                "chunk_type": chunk.chunk_type,
                "metadata": chunk.metadata,
                "content": chunk.content,
            },
            ensure_ascii=False,
        )
        for chunk in chunks
    ]
