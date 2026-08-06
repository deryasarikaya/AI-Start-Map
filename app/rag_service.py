from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from shutil import copy2
from threading import Lock
from typing import Any, Iterable, Literal

import faiss
import numpy as np

from app.openai_service import embed_texts, get_embedding_model


ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
CURATED_DIRECTORY = ROOT_DIRECTORY / "knowledge" / "curated"
INDEX_DIRECTORY = ROOT_DIRECTORY / "data" / "vector_index"
INDEX_FILE = INDEX_DIRECTORY / "knowledge.faiss"
METADATA_FILE = INDEX_DIRECTORY / "chunks.json"
MANIFEST_FILE = INDEX_DIRECTORY / "manifest.json"
DIAGNOSTIC_TEST_INDEX_DIRECTORY = ROOT_DIRECTORY / "data" / "vector_index_test"
AGENT_INDEX_DIRECTORY = ROOT_DIRECTORY / "data" / "agent_pattern_index"
AGENT_TEST_INDEX_DIRECTORY = ROOT_DIRECTORY / "data" / "agent_pattern_index_test"
INDEX_BACKUP_DIRECTORY = ROOT_DIRECTORY / "data" / "index_backups"
INDEX_FILE_NAME = "knowledge.faiss"
METADATA_FILE_NAME = "chunks.json"
MANIFEST_FILE_NAME = "manifest.json"
CHUNK_HEADING = re.compile(r"^## Chunk:\s*(.+)$", re.MULTILINE)
YAML_BLOCK = re.compile(r"```yaml\s*\n(.*?)```", re.DOTALL)
TOKEN_PATTERN = re.compile(r"[\wäöüß]+", re.IGNORECASE)

DIAGNOSTIC_JSONL_FILES = (
    ROOT_DIRECTORY
    / "knowledge"
    / "research_batches"
    / "batch_02_analog_reality"
    / "02_rag_corpus.jsonl",
    ROOT_DIRECTORY
    / "knowledge"
    / "research_batches"
    / "batch_03_diagnostic_depth"
    / "02_rag_corpus.jsonl",
)
AGENT_PATTERN_FILES = (
    "02_agent_decision_patterns.jsonl",
    "03_next_question_patterns.jsonl",
    "04_clarification_and_contradiction_patterns.jsonl",
    "05_stop_rules.jsonl",
    "06_tool_selection_patterns.jsonl",
    "08_agent_guardrails.jsonl",
)
AGENT_PATTERN_DIRECTORY = (
    ROOT_DIRECTORY
    / "knowledge"
    / "research_batches"
    / "batch_04_agentic_interview"
)
FORBIDDEN_INDEX_MARKERS = ("evaluation", "evaluation_cases", "never_index")


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


@dataclass(frozen=True)
class DuplicateReport:
    duplicate_ids: tuple[tuple[str, str], ...]
    exact_content_duplicates: tuple[tuple[str, str], ...]
    near_duplicates: tuple[tuple[str, str, float], ...]


IndexKind = Literal["diagnostic", "agent"]
IndexCacheSignature = tuple[int, int]
IndexCacheEntry = tuple[IndexCacheSignature, Any, list[KnowledgeChunk]]

_INDEX_CACHE: dict[Path, IndexCacheEntry] = {}
_INDEX_CACHE_LOCK = Lock()


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


def _as_string_list(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def _normalize_metadata(
    metadata: dict[str, Any],
    *,
    source_file: str,
    default_batch_id: str,
) -> dict[str, Any]:
    normalized = dict(metadata)
    source_ids = _as_string_list(metadata.get("source_ids"))
    if not source_ids:
        source_ids = _as_string_list(metadata.get("source_id"))
    if not source_ids:
        source_ids = _as_string_list(
            metadata.get("source_url")
            or metadata.get("source_urls")
            or metadata.get("source_file")
        )
    if not source_ids:
        source_ids = [source_file]
    pattern_ids = _as_string_list(metadata.get("pattern_ids"))
    if not pattern_ids:
        pattern_ids = _as_string_list(metadata.get("pattern_id"))
    normalized.update(
        {
            "batch_id": str(metadata.get("batch_id") or default_batch_id),
            "source_ids": source_ids,
            "source_strength": str(
                metadata.get("source_strength") or "not_assessed"
            ),
            "content_origin": str(metadata.get("content_origin") or "not_assessed"),
            "is_primary_evidence": bool(
                metadata.get("is_primary_evidence", False)
            ),
            "industry": _as_string_list(
                metadata.get("industry")
                or metadata.get("sector")
                or metadata.get("business_type")
            ),
            "process_type": _as_string_list(
                metadata.get("process_type")
                or metadata.get("process_tags")
                or metadata.get("categories")
                or metadata.get("related_processes")
            ),
            "digital_maturity_level": metadata.get(
                "digital_maturity_level", "unknown"
            ),
            "pattern_ids": pattern_ids,
            "guardrail_ids": _as_string_list(metadata.get("guardrail_ids")),
        }
    )
    return normalized


def _assert_indexable_path(path: Path) -> None:
    lowered = str(path).casefold()
    if any(marker in lowered for marker in FORBIDDEN_INDEX_MARKERS):
        raise RagConfigurationError(
            f"Evaluations- oder Sperrdatei darf nicht indexiert werden: {path}"
        )


def _parse_file(path: Path) -> list[KnowledgeChunk]:
    _assert_indexable_path(path)
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
        raw_metadata = _parse_metadata(yaml_match.group(1))
        metadata = _normalize_metadata(
            raw_metadata,
            source_file=path.name,
            default_batch_id="legacy_curated",
        )
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


def _jsonl_content(record: dict[str, Any]) -> str:
    direct = record.get("content") or record.get("text")
    if direct:
        return str(direct).strip()
    excluded = {
        "chunk_id",
        "chunk_type",
        "batch_id",
        "source_ids",
        "source_strength",
        "content_origin",
    }
    lines: list[str] = []
    for key, value in record.items():
        if key in excluded or value in (None, "", [], {}):
            continue
        rendered = value if isinstance(value, str) else json.dumps(
            value, ensure_ascii=False
        )
        lines.append(f"{key}: {rendered}")
    return "\n".join(lines)


def _parse_jsonl_file(path: Path) -> list[KnowledgeChunk]:
    _assert_indexable_path(path)
    chunks: list[KnowledgeChunk] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise RagConfigurationError(
                f"Ungültiges JSONL in {path.name}:{line_number}."
            ) from error
        chunk_id = str(record.get("chunk_id") or record.get("id") or "").strip()
        chunk_type = str(
            record.get("chunk_type") or record.get("pattern_type") or ""
        ).strip()
        if not chunk_id or not chunk_type:
            raise RagConfigurationError(
                f"Datensatz in {path.name}:{line_number} hat keine ID oder keinen Typ."
            )
        chunks.append(
            KnowledgeChunk(
                chunk_id=chunk_id,
                chunk_type=chunk_type,
                title=str(record.get("title") or record.get("pattern_name") or chunk_id),
                content=_jsonl_content(record),
                source_file=str(path.relative_to(ROOT_DIRECTORY)).replace("\\", "/"),
                metadata=_normalize_metadata(
                    record,
                    source_file=path.name,
                    default_batch_id=path.parent.name,
                ),
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
    _validate_chunks(chunks)
    return chunks


def _validate_chunks(chunks: list[KnowledgeChunk]) -> None:
    required_metadata = {
        "batch_id",
        "source_ids",
        "source_strength",
        "content_origin",
        "is_primary_evidence",
        "industry",
        "process_type",
        "digital_maturity_level",
        "pattern_ids",
        "guardrail_ids",
    }
    seen: dict[str, str] = {}
    for chunk in chunks:
        if chunk.chunk_id in seen:
            raise RagConfigurationError(
                f"Doppelte Chunk-ID {chunk.chunk_id} in {seen[chunk.chunk_id]} "
                f"und {chunk.source_file}."
            )
        seen[chunk.chunk_id] = chunk.source_file
        missing = required_metadata - chunk.metadata.keys()
        if missing:
            raise RagConfigurationError(
                f"Chunk {chunk.chunk_id} hat unvollständige Metadaten: {sorted(missing)}"
            )
        if any(
            marker in chunk.source_file.casefold()
            for marker in FORBIDDEN_INDEX_MARKERS
        ):
            raise RagConfigurationError("Evaluationen dürfen niemals indexiert werden.")


def load_diagnostic_chunks() -> list[KnowledgeChunk]:
    chunks = load_curated_chunks()
    for path in DIAGNOSTIC_JSONL_FILES:
        if not path.is_file():
            raise RagConfigurationError(f"Diagnose-Korpus fehlt: {path}")
        chunks.extend(_parse_jsonl_file(path))
    _validate_chunks(chunks)
    return chunks


def load_agent_pattern_chunks() -> list[KnowledgeChunk]:
    chunks: list[KnowledgeChunk] = []
    for file_name in AGENT_PATTERN_FILES:
        path = AGENT_PATTERN_DIRECTORY / file_name
        if not path.is_file():
            raise RagConfigurationError(f"Agenten-Pattern-Datei fehlt: {path}")
        chunks.extend(_parse_jsonl_file(path))
    _validate_chunks(chunks)
    return chunks


def _normalized_tokens(content: str) -> set[str]:
    return {
        token.casefold()
        for token in TOKEN_PATTERN.findall(content)
        if len(token) > 2
    }


def audit_duplicates(
    chunks: Iterable[KnowledgeChunk], *, near_duplicate_threshold: float = 0.92
) -> DuplicateReport:
    chunk_list = list(chunks)
    id_owner: dict[str, KnowledgeChunk] = {}
    content_owner: dict[str, KnowledgeChunk] = {}
    duplicate_ids: list[tuple[str, str]] = []
    exact_duplicates: list[tuple[str, str]] = []
    near_duplicates: list[tuple[str, str, float]] = []
    token_sets = [_normalized_tokens(chunk.content) for chunk in chunk_list]
    for chunk, tokens in zip(chunk_list, token_sets, strict=True):
        if chunk.chunk_id in id_owner:
            duplicate_ids.append((id_owner[chunk.chunk_id].chunk_id, chunk.chunk_id))
        id_owner[chunk.chunk_id] = chunk
        content_hash = hashlib.sha256(
            " ".join(sorted(tokens)).encode("utf-8")
        ).hexdigest()
        if content_hash in content_owner:
            exact_duplicates.append((content_owner[content_hash].chunk_id, chunk.chunk_id))
        else:
            content_owner[content_hash] = chunk
    exact_set = set(exact_duplicates)
    for left_index, left in enumerate(chunk_list):
        for right_index in range(left_index + 1, len(chunk_list)):
            right = chunk_list[right_index]
            if left.chunk_type != right.chunk_type:
                continue
            left_tokens = token_sets[left_index]
            right_tokens = token_sets[right_index]
            if not left_tokens or not right_tokens:
                continue
            score = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
            if (
                score >= near_duplicate_threshold
                and (left.chunk_id, right.chunk_id) not in exact_set
            ):
                near_duplicates.append(
                    (left.chunk_id, right.chunk_id, round(score, 3))
                )
    return DuplicateReport(
        duplicate_ids=tuple(duplicate_ids),
        exact_content_duplicates=tuple(exact_duplicates),
        near_duplicates=tuple(near_duplicates),
    )


def _corpus_hash(chunks: list[KnowledgeChunk], embedding_model: str) -> str:
    digest = hashlib.sha256(embedding_model.encode("utf-8"))
    for chunk in chunks:
        digest.update(chunk.source_file.encode("utf-8"))
        digest.update(chunk.content.encode("utf-8"))
    return digest.hexdigest()


def _index_paths(directory: Path) -> tuple[Path, Path, Path]:
    return (
        directory / INDEX_FILE_NAME,
        directory / METADATA_FILE_NAME,
        directory / MANIFEST_FILE_NAME,
    )


def build_vector_index(
    *,
    force: bool = False,
    index_kind: IndexKind = "diagnostic",
    output_directory: Path = INDEX_DIRECTORY,
) -> bool:
    chunks = (
        load_diagnostic_chunks()
        if index_kind == "diagnostic"
        else load_agent_pattern_chunks()
    )
    embedding_model = get_embedding_model()
    corpus_hash = _corpus_hash(chunks, embedding_model)
    index_file, metadata_file, manifest_file = _index_paths(output_directory)
    index_is_current = (
        manifest_file.is_file()
        and index_file.is_file()
        and metadata_file.is_file()
    )
    if not force and index_is_current:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
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

    output_directory.mkdir(parents=True, exist_ok=True)
    temporary_index = output_directory / "knowledge.faiss.tmp"
    faiss.write_index(index, str(temporary_index))
    temporary_index.replace(index_file)
    metadata_file.write_text(
        json.dumps([asdict(chunk) for chunk in chunks], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    manifest_file.write_text(
        json.dumps(
            {
                "index_kind": index_kind,
                "corpus_hash": corpus_hash,
                "embedding_model": embedding_model,
                "chunk_count": len(chunks),
                "excluded_evaluations": True,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    validate_index(output_directory, expected_kind=index_kind)
    return True


def validate_index(
    directory: Path, *, expected_kind: IndexKind | None = None
) -> dict[str, Any]:
    index_file, metadata_file, manifest_file = _index_paths(directory)
    if not all(path.is_file() for path in (index_file, metadata_file, manifest_file)):
        raise RagConfigurationError(f"Index ist unvollständig: {directory}")
    raw_chunks = json.loads(metadata_file.read_text(encoding="utf-8"))
    chunks = [KnowledgeChunk(**raw_chunk) for raw_chunk in raw_chunks]
    _validate_chunks(chunks)
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    index = faiss.read_index(str(index_file))
    if index.ntotal != len(chunks) or manifest.get("chunk_count") != len(chunks):
        raise RagConfigurationError(
            "Wissensindex, Manifest und Metadaten passen nicht zusammen."
        )
    if expected_kind and manifest.get("index_kind") != expected_kind:
        raise RagConfigurationError("Der Index hat den falschen Verwendungszweck.")
    return manifest


def promote_test_indexes() -> None:
    validate_index(DIAGNOSTIC_TEST_INDEX_DIRECTORY, expected_kind="diagnostic")
    validate_index(AGENT_TEST_INDEX_DIRECTORY, expected_kind="agent")
    validate_index(INDEX_DIRECTORY, expected_kind="diagnostic")
    validate_index(AGENT_INDEX_DIRECTORY, expected_kind="agent")

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
    backup_directory = INDEX_BACKUP_DIRECTORY / timestamp
    suffix = 1
    while backup_directory.exists():
        backup_directory = INDEX_BACKUP_DIRECTORY / f"{timestamp}-{suffix:02d}"
        suffix += 1
    for label, source_directory in (
        ("diagnostic", INDEX_DIRECTORY),
        ("agent", AGENT_INDEX_DIRECTORY),
    ):
        target_directory = backup_directory / label
        target_directory.mkdir(parents=True, exist_ok=False)
        for name in (INDEX_FILE_NAME, METADATA_FILE_NAME, MANIFEST_FILE_NAME):
            copy2(source_directory / name, target_directory / name)

    for source_directory, target_directory in (
        (DIAGNOSTIC_TEST_INDEX_DIRECTORY, INDEX_DIRECTORY),
        (AGENT_TEST_INDEX_DIRECTORY, AGENT_INDEX_DIRECTORY),
    ):
        target_directory.mkdir(parents=True, exist_ok=True)
        for name in (INDEX_FILE_NAME, METADATA_FILE_NAME, MANIFEST_FILE_NAME):
            temporary_target = target_directory / f"{name}.tmp"
            copy2(source_directory / name, temporary_target)
            temporary_target.replace(target_directory / name)
        _invalidate_index_cache(target_directory)

    validate_index(INDEX_DIRECTORY, expected_kind="diagnostic")
    validate_index(AGENT_INDEX_DIRECTORY, expected_kind="agent")


def _index_cache_signature(index_file: Path, metadata_file: Path) -> IndexCacheSignature:
    return (index_file.stat().st_mtime_ns, metadata_file.stat().st_mtime_ns)


def _invalidate_index_cache(directory: Path | None = None) -> None:
    with _INDEX_CACHE_LOCK:
        if directory is None:
            _INDEX_CACHE.clear()
            return
        _INDEX_CACHE.pop(directory.resolve(), None)


def _load_index_from(directory: Path) -> tuple[Any, list[KnowledgeChunk]]:
    index_file, metadata_file, _manifest_file = _index_paths(directory)
    if not index_file.is_file() or not metadata_file.is_file():
        raise RagConfigurationError(
            "Der Wissensindex fehlt. Führe zuerst python scripts/build_index.py aus."
        )
    cache_key = directory.resolve()
    signature = _index_cache_signature(index_file, metadata_file)
    with _INDEX_CACHE_LOCK:
        cached = _INDEX_CACHE.get(cache_key)
        if cached is not None and cached[0] == signature:
            return cached[1], cached[2]

        raw_chunks = json.loads(metadata_file.read_text(encoding="utf-8"))
        chunks = [KnowledgeChunk(**raw_chunk) for raw_chunk in raw_chunks]
        index = faiss.read_index(str(index_file))
        if index.ntotal != len(chunks):
            raise RagConfigurationError(
                "Wissensindex und Metadaten passen nicht zusammen."
            )
        _INDEX_CACHE[cache_key] = (signature, index, chunks)
        return index, chunks


def _load_index() -> tuple[Any, list[KnowledgeChunk]]:
    return _load_index_from(INDEX_DIRECTORY)


PHASE_TYPES = {
    "suggestion": {
        "allowed": {
            "case_evidence",
            "diagnostic_pattern",
            "process_pattern",
            "digital_readiness_pattern",
            "automation_guardrail",
            "minimal_viable_improvement",
        },
        "required": ("diagnostic_pattern", "automation_guardrail"),
    },
    "follow_up": {
        "allowed": {
            "interview_question_set",
            "interview_question_pattern",
            "diagnostic_question_set",
            "diagnostic_pattern",
            "process_pattern",
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
            "process_pattern",
            "automation_pattern",
            "automation_guardrail",
            "digital_readiness_pattern",
            "implementation_prerequisite",
            "minimal_viable_improvement",
            "prioritization_pattern",
            "analog_workaround",
            "adoption_risk",
            "information_flow_problem",
            "physical_object_tracking_pattern",
        },
        "required": (
            "diagnostic_pattern",
            "automation_pattern",
            "implementation_prerequisite",
            "automation_guardrail",
        ),
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


def _rank_with_source_strength(
    scores: Iterable[float],
    positions: Iterable[int],
    chunks: list[KnowledgeChunk],
) -> list[KnowledgeChunk]:
    penalties = {"low": 0.15, "derived_from_low": 0.08}
    ranked = sorted(
        (
            (
                float(score)
                - penalties.get(
                    str(chunks[position].metadata.get("source_strength", "")),
                    0.0,
                ),
                position,
            )
            for score, position in zip(scores, positions, strict=True)
            if position >= 0
        ),
        key=lambda item: item[0],
        reverse=True,
    )
    return [chunks[position] for _adjusted_score, position in ranked]


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
    scores, positions = index.search(query_vector, result_count)
    ranked = [
        chunk
        for chunk in _rank_with_source_strength(scores[0], positions[0], chunks)
        if chunk.chunk_type in phase_configuration["allowed"]
    ]
    return _diverse_selection(
        ranked,
        required_types=phase_configuration["required"],
        top_k=requested_count,
    )


def retrieve_agent_patterns(
    query: str,
    *,
    allowed_types: set[str] | None = None,
    top_k: int = 5,
) -> list[KnowledgeChunk]:
    if top_k < 1:
        raise ValueError("top_k muss positiv sein.")
    allowed = allowed_types or {
        "agent_decision_pattern",
        "next_question_pattern",
        "contradiction_pattern",
        "agent_stop_rule",
        "tool_selection_pattern",
        "agent_guardrail",
    }
    index, chunks = _load_index_from(AGENT_INDEX_DIRECTORY)
    query_vector = np.asarray(embed_texts([query]), dtype="float32")
    if query_vector.ndim != 2 or query_vector.shape[0] != 1:
        raise RagConfigurationError("Die Agentensuche konnte nicht vorbereitet werden.")
    faiss.normalize_L2(query_vector)
    scores, positions = index.search(query_vector, len(chunks))
    return [
        chunk
        for chunk in _rank_with_source_strength(scores[0], positions[0], chunks)
        if chunk.chunk_type in allowed
    ][:top_k]


def format_chunks_for_prompt(chunks: list[KnowledgeChunk]) -> list[str]:
    formatted_chunks: list[str] = []
    for chunk in chunks:
        yaml_match = YAML_BLOCK.search(chunk.content)
        content = (
            chunk.content[yaml_match.end():]
            if yaml_match is not None
            else chunk.content
        )
        content = re.sub(r"\[([^\]]+)]\(https?://[^)]+\)", r"\1", content)
        content = re.sub(r"https?://\S+", "", content)
        content = re.sub(
            r"\b(?:(?:EVAL-)?[MCKP]-\d{2}(?:[_-][A-Za-z0-9_]+)*|"
            r"RB(?:02|03|04)-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)\b",
            "",
            content,
            flags=re.IGNORECASE,
        )
        cleaned_content = content.strip()
        if cleaned_content:
            formatted_chunks.append(cleaned_content)
    return formatted_chunks
