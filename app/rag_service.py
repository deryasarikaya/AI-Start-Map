"""Sucht passende Textstellen im aufbereiteten Wissensbestand.

Zu einer Frage werden ähnliche Abschnitte aus dem eigenen Wissen gesucht und
dem Prompt beigelegt. Die Suche läuft über einen FAISS-Index, der vorab aus den
Dateien unter `knowledge/` gebaut wird.

Benutzt wird das an drei Stellen: bei den Ablaufvorschlägen, bei den Rückfragen
und bei der Endanalyse.

Achtung, hier liegen zwei verschiedene Dinge nebeneinander: das **Bauen** des
Index (gehört eigentlich in ein Werkzeug, nicht in den laufenden Betrieb) und
das **Suchen** darin. Die Trennung steht im Backlog.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from shutil import copy2
from threading import Lock
from typing import Any, Iterable, Literal, Sequence

import faiss
import numpy as np

from app.openai_service import embed_texts, get_embedding_model


logger = logging.getLogger(__name__)

ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
# Der Diagnosekorpus liegt bis zum Umbau auf Batch 09 im Archiv.
CURATED_DIRECTORY = ROOT_DIRECTORY / "knowledge" / "archive" / "curated"
INDEX_DIRECTORY = ROOT_DIRECTORY / "data" / "vector_index"
INDEX_FILE = INDEX_DIRECTORY / "knowledge.faiss"
METADATA_FILE = INDEX_DIRECTORY / "chunks.json"
MANIFEST_FILE = INDEX_DIRECTORY / "manifest.json"
DIAGNOSTIC_TEST_INDEX_DIRECTORY = ROOT_DIRECTORY / "data" / "vector_index_test"
AGENT_INDEX_DIRECTORY = ROOT_DIRECTORY / "data" / "agent_pattern_index"
AGENT_TEST_INDEX_DIRECTORY = ROOT_DIRECTORY / "data" / "agent_pattern_index_test"
SOLUTION_INDEX_DIRECTORY = ROOT_DIRECTORY / "data" / "solution_workflow_index"
SOLUTION_TEST_INDEX_DIRECTORY = ROOT_DIRECTORY / "data" / "solution_workflow_index_test"
SOLUTION_WORKFLOW_FILE = (
    ROOT_DIRECTORY
    / "knowledge"
    / "runtime"
    / "solution_knowledge"
    / "solution_workflows.jsonl"
)
# Batch 10: Lösungsfamilien, Zielbilder, Diagnosemuster. Ein eigener Index,
# damit die Lösungsfamilien nicht von den älteren Diagnosekorpora verdrängt
# werden — die sind zahlreicher und würden jede Suche dominieren.
SOLUTION_ARCHITECTURE_DIRECTORY = (
    ROOT_DIRECTORY / "knowledge" / "candidates" / "batch_10"
)
SOLUTION_ARCHITECTURE_INDEX_DIRECTORY = (
    ROOT_DIRECTORY / "data" / "solution_architecture_index"
)
SOLUTION_ARCHITECTURE_TEST_INDEX_DIRECTORY = (
    ROOT_DIRECTORY / "data" / "solution_architecture_index_test"
)
#: Wie viele Abschnitte je **gesuchtem** Typ genommen werden. Nur diese zwei
#: werden semantisch gesucht; alles Weitere hängt an Kennungen und wird
#: nachgeschlagen. Als Konstante, damit sich die Mischung messbar ändern
#: lässt — und damit sichtbar ist, dass hier eine Entscheidung getroffen
#: wurde und keine Zufallszahl steht.
CHUNKS_PER_SEARCHED_TYPE = {
    "business_pattern": 1,
    "diagnostic_pattern": 3,
}
#: Obergrenzen für das Nachgeschlagene. Drei Diagnosemuster können auf viele
#: Familien zeigen; ohne Deckel wächst der Prompt unbemerkt, und Prompt-Länge
#: ist bei 43 Prozent Zeitabläufen keine Nebensache.
#:
#: Sechs, nicht vier. Vier war eine Zahl ohne Begründung, und sie hat den
#: ganzen Aufbau zunichte gemacht: DP-06 nennt fünf Familien, also war die
#: Auswahl nach dem **ersten** Muster voll. Gemessen am 21.08. bekam jede
#: Erzählung exakt die ersten vier Familien ihres erstplatzierten Musters —
#: Malerbetrieb und 450-Einheiten-Verwaltung dieselben. Sechs ist das, was
#: ein Ergebnis mit sechs bis neun Modulen tragen kann.
MAXIMUM_SOLUTION_FAMILIES = 6
MAXIMUM_CAPABILITIES = 6

#: Wie kurz ein Absatz sein darf, bevor er mit dem nächsten zusammengelegt
#: wird. Ein Fragment von fünf Wörtern trägt keine eigene Suche.
MINDESTLAENGE_ABSATZ = 160
#: Und wie lang er werden darf, bevor er an Satzgrenzen weiter zerfällt.
#:
#: Nicht jede Erzählung hat Leerzeilen: Die des Malerbetriebs ist ein Block
#: von 857 Zeichen. Ohne diese zweite Teilung würde die absatzweise Suche
#: genau die Fälle nicht erreichen, die kurz und am Stück erzählt sind —
#: und das sind die kleinen Betriebe.
HOECHSTLAENGE_ABSATZ = 600
#: Höchstens so viele Absätze werden einzeln eingebettet. Sie gehen in
#: **einem** Aufruf zusammen an die Einbettung; die Grenze deckelt trotzdem,
#: was eine sehr lange Erzählung kostet.
HOECHSTENS_ABSAETZE = 25
#: Wie viele Plätze je Absatz und Wissenstyp Punkte bekommen. Ein Muster,
#: das in mehreren Absätzen weit oben steht, soll eines schlagen, das in
#: einem Absatz knapp führt.
PUNKTE_JE_PLATZ = (3, 2, 1)

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
    / "archive"
    / "research_batches"
    / "batch_02_analog_reality"
    / "02_rag_corpus.jsonl",
    ROOT_DIRECTORY
    / "knowledge"
    / "archive"
    / "research_batches"
    / "batch_03_diagnostic_depth"
    / "02_rag_corpus.jsonl",
)
AGENT_PATTERN_DIRECTORY = (
    ROOT_DIRECTORY
    / "knowledge"
    / "archive"
    / "research_batches"
    / "batch_04_agentic_interview"
)
# Die direkt geladenen Fragemuster liegen unter knowledge/runtime/;
# die übrigen Agentenmuster bleiben bis zu einem späteren Umbau im Archiv.
AGENT_PATTERN_FILES = (
    AGENT_PATTERN_DIRECTORY / "02_agent_decision_patterns.jsonl",
    ROOT_DIRECTORY
    / "knowledge"
    / "runtime"
    / "patterns"
    / "next_question_patterns.jsonl",
    AGENT_PATTERN_DIRECTORY / "04_clarification_and_contradiction_patterns.jsonl",
    AGENT_PATTERN_DIRECTORY / "05_stop_rules.jsonl",
    AGENT_PATTERN_DIRECTORY / "06_tool_selection_patterns.jsonl",
    AGENT_PATTERN_DIRECTORY / "08_agent_guardrails.jsonl",
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


IndexKind = Literal["diagnostic", "agent", "solution", "architecture"]
IndexCacheSignature = tuple[int, int]
IndexCacheEntry = tuple[IndexCacheSignature, Any, list[KnowledgeChunk]]

_INDEX_CACHE: dict[Path, IndexCacheEntry] = {}
_INDEX_CACHE_LOCK = Lock()


def _metadata_value(raw_value: str) -> Any:
    """Wandelt einen Metadatenwert aus dem Text in den passenden Typ."""

    value = raw_value.strip()
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value.strip('"')


def _parse_metadata(metadata_text: str) -> dict[str, Any]:
    """Liest den Metadatenblock eines Abschnitts."""

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
    """Bringt Metadaten verschiedener Herkunft auf eine gemeinsame Form."""

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
    """Stellt sicher, dass aus dieser Datei indiziert werden darf.

    Evaluationsdaten dürfen nie in den Index - sonst prüft die
    Anwendung sich an ihren eigenen Testfällen.
    """

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


#: Welche Felder je Wissenstyp in den Suchtext gehören.
#:
#: Ohne diese Listen landet jedes Feld im Einbettungstext — auch
#: `is_primary_evidence: false` und Querverweislisten wie
#: `passende_loesungsfamilien: ["SF-02", "SF-03"]`. Das ist Rauschen: Danach
#: sucht niemand, und es verwässert die Ähnlichkeit.
#:
#: Die Querverweise bleiben im Datensatz. Sie werden zum **Nachschlagen**
#: gebraucht, nicht zum Finden — siehe `retrieve_solution_context`.
#:
#: Für einen Typ ohne Eintrag bleibt es beim bisherigen Verhalten. Die
#: vorhandenen Bestände dürfen sich nicht verändern.
SEARCHABLE_FIELDS_BY_CHUNK_TYPE: dict[str, tuple[str, ...]] = {
    "business_pattern": (
        "title",
        "worum_es_geht",
        "typische_betriebe",
        "was_durch_den_betrieb_laeuft",
        "typische_kanaele",
        "wichtige_gegenstaende",
        "notwendige_angaben",
        "typische_uebergaben",
        "typische_zustaende",
        "typische_ausnahmen",
        "engpasssignale",
        "fachbegriffe",
        "nicht_annehmen",
    ),
    "diagnostic_pattern": (
        "title",
        "muster_name",
        "worum_es_geht",
        # Das wichtigste Feld dieser Datei: wie Menschen es tatsächlich sagen.
        "signale_in_der_erzaehlung",
        "moegliche_ursachen",
        "was_es_kostet",
        "was_es_nicht_ist",
        "klaerende_fragen",
    ),
    "solution_family": (
        "title",
        "familie_name",
        "worum_es_geht",
        "geeignet_wenn",
        "nicht_geeignet_wenn",
        "bausteine",
        "bleibt_beim_menschen",
        "setzt_voraus",
        "reihenfolge_hinweis",
        "kundennaher_name",
    ),
    "automation_capability": (
        "title",
        "faehigkeit_name",
        "worum_es_geht",
        "braucht_als_eingabe",
        "liefert",
        "zuverlaessigkeit",
        "typische_fehler",
        "menschliche_pruefung",
    ),
    "target_architecture": (
        "title",
        "ausgangslage",
        # `ebenen` trägt die Beschreibung der Schichten. In den Objekten darin
        # stehen auch SF-Kennungen; sie herauszuschneiden würde das Feld
        # zerlegen, und die paar Kennungen wiegen den Beschreibungstext nicht
        # auf. Die einzige Stelle, an der noch Kennungen im Suchtext stehen.
        "ebenen",
        "kleinste_fassung",
        "groesste_fassung",
        "passt_nicht_wenn",
    ),
}

#: Was ohne hinterlegte Feldliste aus dem Suchtext fällt. Der bisherige Stand.
ADMINISTRATIVE_FIELDS = frozenset(
    {
        "chunk_id",
        "chunk_type",
        "batch_id",
        "source_ids",
        "source_strength",
        "content_origin",
    }
)


def _jsonl_content(record: dict[str, Any]) -> str:
    """Baut den durchsuchbaren Text eines Datensatzes.

    Steht ein `content`-Feld drin, gilt das. Sonst werden die Felder
    aneinandergereiht — welche, sagt `SEARCHABLE_FIELDS_BY_CHUNK_TYPE`.
    """

    direct = record.get("content") or record.get("text")
    if direct:
        return str(direct).strip()
    erlaubt = SEARCHABLE_FIELDS_BY_CHUNK_TYPE.get(str(record.get("chunk_type") or ""))
    # Die Feldliste greift nur, wenn der Datensatz auch so aussieht. Ein
    # älterer Bestand kann denselben Typnamen tragen und ganz andere Felder
    # haben — dann würde die Liste alles wegfiltern und der Suchtext wäre
    # leer. Für ihn bleibt es beim bisherigen Verhalten.
    if erlaubt is not None and not any(feld in record for feld in erlaubt):
        erlaubt = None
    lines: list[str] = []
    for key, value in record.items():
        if erlaubt is not None:
            if key not in erlaubt:
                continue
        elif key in ADMINISTRATIVE_FIELDS:
            continue
        if value in (None, "", [], {}):
            continue
        rendered = value if isinstance(value, str) else json.dumps(
            value, ensure_ascii=False
        )
        lines.append(f"{key}: {rendered}")
    return "\n".join(lines)


def _source_label(path: Path) -> str:
    """Woher ein Abschnitt kommt, als Pfad relativ zum Projekt.

    Liegt die Datei ausserhalb des Projektordners, steht dort nur ihr Name.
    Vorher brach das mit einer ValueError ab, die nichts erklärte.
    """

    try:
        return str(path.relative_to(ROOT_DIRECTORY)).replace("\\", "/")
    except ValueError:
        return path.name


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
                source_file=_source_label(path),
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
    """Prüft, dass jeder Abschnitt Kennung, Typ und Inhalt hat."""

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
    for path in AGENT_PATTERN_FILES:
        if not path.is_file():
            raise RagConfigurationError(f"Agenten-Pattern-Datei fehlt: {path}")
        chunks.extend(_parse_jsonl_file(path))
    _validate_chunks(chunks)
    return chunks


def load_solution_workflow_chunks() -> list[KnowledgeChunk]:
    if not SOLUTION_WORKFLOW_FILE.is_file():
        raise RagConfigurationError(
            f"Solution-Workflow-Datei fehlt: {SOLUTION_WORKFLOW_FILE}"
        )
    chunks = [
        chunk
        for chunk in _parse_jsonl_file(SOLUTION_WORKFLOW_FILE)
        if chunk.metadata.get("batch_scope") == "in_scope"
    ]
    if len(chunks) != 27:
        raise RagConfigurationError(
            "Der Solution-Korpus muss 27 positive Workflows enthalten; "
            "der dokumentarische SP-04-Ausschluss darf nicht indexiert werden."
        )
    if any(
        chunk.metadata.get("quality_status") != "runtime_approved"
        for chunk in chunks
    ):
        raise RagConfigurationError(
            "Nur runtime-freigegebene Solution Workflows dürfen indexiert werden."
        )
    _validate_chunks(chunks)
    return chunks



def load_solution_architecture_chunks() -> list[KnowledgeChunk]:
    """Alle Datensätze aus Batch 10 — Lösungsarchitektur-Wissen.

    Ein noch nicht geschriebener Batch ist kein Fehler: Solange der Ordner
    leer ist, kommt eine leere Liste zurück. Der Indexaufbau sagt das dann und
    baut nichts, statt mit einem Fehler abzubrechen.
    """

    if not SOLUTION_ARCHITECTURE_DIRECTORY.is_dir():
        return []
    chunks: list[KnowledgeChunk] = []
    for path in sorted(SOLUTION_ARCHITECTURE_DIRECTORY.glob("*.jsonl")):
        chunks.extend(_parse_jsonl_file(path))
    if chunks:
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
    """Findet gleiche und fast gleiche Abschnitte.

    Doppelte Abschnitte verzerren die Suche: Derselbe Inhalt belegt
    zwei der sechs Plätze.
    """

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
    """Fingerabdruck über Inhalte und Einbettungsmodell.

    Damit erkennt der Bau, ob sich seit dem letzten Mal etwas geändert
    hat.
    """

    digest = hashlib.sha256(embedding_model.encode("utf-8"))
    for chunk in chunks:
        digest.update(chunk.source_file.encode("utf-8"))
        digest.update(chunk.content.encode("utf-8"))
    return digest.hexdigest()


def _index_paths(directory: Path) -> tuple[Path, Path, Path]:
    """Die drei Dateien eines Index: Vektoren, Abschnitte, Manifest."""

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
    """Baut einen FAISS-Index aus den Wissensabschnitten.

    Werkzeug, kein Laufzeitcode - gerufen wird das aus
    `scripts/build_index.py`.
    """

    if index_kind == "diagnostic":
        chunks = load_diagnostic_chunks()
    elif index_kind == "agent":
        chunks = load_agent_pattern_chunks()
    elif index_kind == "architecture":
        chunks = load_solution_architecture_chunks()
        if not chunks:
            raise RagConfigurationError(
                "Batch 10 ist noch leer. Erst schreiben, dann indexieren — "
                "siehe scripts/pruefe_batch10.py."
            )
    else:
        chunks = load_solution_workflow_chunks()
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
    """Prüft einen gebauten Index gegen sein Manifest."""

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
    """Uebernimmt die geprüften Testindizes als produktive."""

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
    """Kennzeichen, an dem ein zwischengespeicherter Index hängt."""

    return (index_file.stat().st_mtime_ns, metadata_file.stat().st_mtime_ns)


def _invalidate_index_cache(directory: Path | None = None) -> None:
    with _INDEX_CACHE_LOCK:
        if directory is None:
            _INDEX_CACHE.clear()
            return
        _INDEX_CACHE.pop(directory.resolve(), None)


def _load_index_from(directory: Path) -> tuple[Any, list[KnowledgeChunk]]:
    """Lädt einen Index von der Platte, mit Zwischenspeicher.

    Der Index wird beim ersten Zugriff geladen und dann behalten - er
    ändert sich zur Laufzeit nicht.
    """

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
    """Wie viele Abschnitte je Suche zurückkommen (RAG_TOP_K, Standard 6)."""

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
    """Wählt die Abschnitte aus, die zurückgehen.

    Nicht rein nach Ähnlichkeit: Bestimmte Abschnittstypen müssen
    vertreten sein, und zum selben Muster kommen höchstens zwei Belege
    durch.
    """

    selected: list[KnowledgeChunk] = []
    selected_ids: set[str] = set()
    evidence_by_pattern: dict[str, int] = {}

    def add(chunk: KnowledgeChunk) -> bool:
        """Nimmt einen Abschnitt in die Auswahl auf, wenn noch Platz ist."""

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
    # Source strength bleibt als Transparenzmetadatum erhalten. Der frühere
    # pauschale Abzug von 0,15 beziehungsweise 0,08 war nicht gegen die
    # Retrieval-Evaluation kalibriert und wird deshalb neutralisiert.
    """Sortiert die Suchtreffer nach Ähnlichkeit."""

    ranked = sorted(
        (
            (
                float(score),
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
    """Sucht Vergleichswissen im Diagnoseindex."""

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
    """Sucht Muster für die Gesprächsführung."""

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
    """Bereitet Abschnitte für den Prompt auf.

    Jeder Abschnitt wird ausdrücklich als Vergleichswissen
    gekennzeichnet, damit das Modell ihn nicht für einen Nutzerfakt
    hält.
    """

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
@dataclass(frozen=True)
class RetrievedKnowledge:
    """Was zu einer Erzählung an Lösungswissen zusammenkam.

    In der Reihenfolge, in der es entstanden ist: gesucht wird oben,
    nachgeschlagen wird unten.
    """

    betriebsarten: tuple[KnowledgeChunk, ...] = ()
    diagnosemuster: tuple[KnowledgeChunk, ...] = ()
    loesungsfamilien: tuple[KnowledgeChunk, ...] = ()
    faehigkeiten: tuple[KnowledgeChunk, ...] = ()
    zielbild: KnowledgeChunk | None = None

    def all_chunks(self) -> list[KnowledgeChunk]:
        """Alles zusammen, in der Reihenfolge des Wegs."""

        zusammen = [
            *self.betriebsarten,
            *self.diagnosemuster,
            *self.loesungsfamilien,
            *self.faehigkeiten,
        ]
        if self.zielbild is not None:
            zusammen.append(self.zielbild)
        return zusammen


def _ids(chunk: KnowledgeChunk, feld: str) -> list[str]:
    """Die Kennungen aus einem Querverweisfeld eines Datensatzes."""

    return [str(eintrag).strip() for eintrag in _as_string_list(chunk.metadata.get(feld))]


def _betriebsart_buchstaben(chunks: Sequence[KnowledgeChunk]) -> set[str]:
    """Die Buchstaben der erkannten Betriebsarten, etwa {"A", "G"}."""

    buchstaben: set[str] = set()
    for chunk in chunks:
        buchstabe = str(chunk.metadata.get("betriebsart_buchstabe") or "").strip()
        if buchstabe:
            buchstaben.add(buchstabe.upper())
        buchstaben.update(
            eintrag.strip().upper()
            for eintrag in _as_string_list(chunk.metadata.get("process_type"))
            if eintrag.strip()
        )
    return buchstaben


def _passt_zur_betriebsart(chunk: KnowledgeChunk, buchstaben: set[str]) -> bool:
    """Ob eine Lösungsfamilie für die erkannte Betriebsart überhaupt gilt.

    Ohne erkannte Betriebsart wird nicht gefiltert — dann wüsste man nichts,
    wonach man filtert. Ein Datensatz ohne Angabe gilt für alle.
    """

    if not buchstaben:
        return True
    gilt_fuer = {
        eintrag.strip().upper()
        for eintrag in _as_string_list(chunk.metadata.get("gilt_fuer_betriebsarten"))
        if eintrag.strip()
    }
    return not gilt_fuer or bool(gilt_fuer & buchstaben)


def _in_saetzen(block: str) -> list[str]:
    """Zerlegt einen zu langen Block an Satzenden in tragfähige Stücke.

    Gesammelt wird bis `MINDESTLAENGE_ABSATZ`; erst dann beginnt ein neues
    Stück. So entstehen keine Einzelsätze, die für sich nichts sagen.
    """

    stuecke: list[str] = []
    laufend = ""
    for satz in re.split(r"(?<=[.!?]) +", block):
        laufend = f"{laufend} {satz}".strip()
        if len(laufend) >= MINDESTLAENGE_ABSATZ:
            stuecke.append(laufend)
            laufend = ""
    if laufend:
        if stuecke:
            stuecke[-1] = f"{stuecke[-1]} {laufend}"
        else:
            stuecke.append(laufend)
    return stuecke


def _absaetze(query: str) -> list[str]:
    """Teilt die Erzählung an Leerzeilen in Absätze.

    Sehr kurze Absätze wandern zum folgenden, damit keine Fragmente
    entstehen; ist der letzte zu kurz, wandert er zum vorigen. Gibt es
    keine Leerzeilen, bleibt der Text ein Stück — dann ist die Suche
    dieselbe wie vorher.
    """

    roh: list[str] = []
    for block in re.split(r"\n\s*\n", query):
        block = block.strip()
        if not block:
            continue
        roh.extend(_in_saetzen(block) if len(block) > HOECHSTLAENGE_ABSATZ else [block])
    if not roh:
        return []
    zusammengelegt: list[str] = []
    for absatz in roh:
        if zusammengelegt and len(zusammengelegt[-1]) < MINDESTLAENGE_ABSATZ:
            zusammengelegt[-1] = f"{zusammengelegt[-1]} {absatz}"
            continue
        zusammengelegt.append(absatz)
    if len(zusammengelegt) > 1 and len(zusammengelegt[-1]) < MINDESTLAENGE_ABSATZ:
        zusammengelegt[-2] = f"{zusammengelegt[-2]} {zusammengelegt.pop()}"
    # Zu viele Absätze werden paarweise zusammengelegt, bis die Grenze hält.
    while len(zusammengelegt) > HOECHSTENS_ABSAETZE:
        zusammengelegt = [
            " ".join(zusammengelegt[stelle : stelle + 2])
            for stelle in range(0, len(zusammengelegt), 2)
        ]
    return zusammengelegt


def _zusammengefuehrt(
    werte, plaetze, chunks: list[KnowledgeChunk]
) -> list[KnowledgeChunk]:
    """Führt die Trefferlisten aller Absätze zu einer Rangfolge zusammen.

    Je Absatz und Wissenstyp bekommen die ersten drei Plätze Punkte. Ein
    Muster, das in drei Absätzen zweiter wird, schlägt damit eines, das in
    einem Absatz knapp führt — genau das unterscheidet die absatzweise
    Suche von der über den ganzen Text.

    Bei Punktgleichheit entscheidet die beste einzelne Ähnlichkeit; damit
    bleibt auch alles geordnet, was gar keine Punkte bekommen hat.
    """

    punkte: dict[int, int] = {}
    bester: dict[int, float] = {}
    for zeile_werte, zeile_plaetze in zip(werte, plaetze, strict=True):
        nach_typ: dict[str, list[tuple[float, int]]] = {}
        for wert, platz in zip(zeile_werte, zeile_plaetze, strict=True):
            if platz < 0:
                continue
            bester[platz] = max(bester.get(platz, -1.0), float(wert))
            nach_typ.setdefault(chunks[platz].chunk_type, []).append(
                (float(wert), platz)
            )
        for treffer in nach_typ.values():
            treffer.sort(key=lambda paar: paar[0], reverse=True)
            for rang, (_wert, platz) in enumerate(treffer[: len(PUNKTE_JE_PLATZ)]):
                punkte[platz] = punkte.get(platz, 0) + PUNKTE_JE_PLATZ[rang]
    rangfolge = sorted(
        bester,
        key=lambda platz: (punkte.get(platz, 0), bester[platz]),
        reverse=True,
    )
    return [chunks[platz] for platz in rangfolge]


def _rank_solution_architecture(query: str) -> list[KnowledgeChunk]:
    """Alle Abschnitte aus Batch 10, nach Ähnlichkeit zur Erzählung sortiert.

    **Gesucht wird absatzweise, nicht am Stück.** Dreitausend Wörter als ein
    Vektor sind ein Mittelwert über Personal, Kanäle, Software, Fristen und
    Rechnungen — und ein Mittelwert liegt ungefähr gleich weit von allem
    entfernt. Gemessen am 21.08.: 0,8 Prozent zwischen der ersten und der
    zweiten Betriebsart. Ein einzelner Absatz beschreibt dagegen eine Sache
    und trifft sie scharf.

    Alle Absätze gehen in **einem** Einbettungsaufruf hinaus; die Kosten
    hängen an den Zeichen, nicht an der Anzahl der Aufrufe.

    Eigene Funktion, damit ein Test sie ersetzen kann, ohne einzubetten —
    Einbetten kostet Geld.
    """

    index, chunks = _load_index_from(SOLUTION_ARCHITECTURE_INDEX_DIRECTORY)
    absaetze = _absaetze(query)
    if not absaetze:
        return []
    vektoren = np.asarray(embed_texts(absaetze), dtype="float32")
    if vektoren.ndim != 2 or vektoren.shape[0] != len(absaetze):
        raise RagConfigurationError(
            "Die Suche im Lösungswissen konnte nicht vorbereitet werden."
        )
    faiss.normalize_L2(vektoren)
    werte, plaetze = index.search(vektoren, len(chunks))
    logger.info(
        "solution_architecture.absaetze anzahl=%d zeichen=%d",
        len(absaetze),
        sum(len(absatz) for absatz in absaetze),
    )
    return _zusammengefuehrt(werte, plaetze, chunks)


def retrieve_solution_context(query: str) -> RetrievedKnowledge:
    """Sammelt Lösungswissen zu einer Erzählung — suchend und nachschlagend.

    Gesucht wird nur dort, wo es unscharf ist: welche Betriebsart, welche
    Engpassmuster. Alles darunter hängt an Kanten, die im Bestand schon
    stehen, und wird über Kennungen **nachgeschlagen**:

        Erzählung → Betriebsart, Diagnosemuster        (gesucht)
                  → dp.passende_loesungsfamilien       (nachgeschlagen)
                  → sf.braucht_capabilities            (nachgeschlagen)
                  → das TA mit der grössten Überdeckung (zugeordnet)

    Das verhindert Empfehlungen ohne diagnostischen Weg: Wer viele E-Mails
    hat, bekäme sonst irgendwann Marketing-Automation vorgeschlagen, weil das
    semantisch in die Nähe rückt — obwohl kein Diagnosemuster dorthin führt.

    Ohne gebauten Index kommt ein leeres Ergebnis zurück. Das ist der Zustand,
    solange kein Batch indexiert ist; der Prompt muss auch dann vollständig
    funktionieren.
    """

    if not (SOLUTION_ARCHITECTURE_INDEX_DIRECTORY / INDEX_FILE_NAME).is_file():
        return RetrievedKnowledge()
    # Die Uhr läuft über den ganzen Abruf, die Einbettung eingeschlossen — sie
    # ist der teure Teil. Der Messplan fragt, ob der Abruf die
    # Zeitablaufquote verschlechtert; ohne diese Zahl liesse sich das nur
    # raten.
    begonnen = perf_counter()
    try:
        sortiert = _rank_solution_architecture(query)
    except RagConfigurationError:
        logger.warning(
            "solution_architecture.unavailable seconds=%.2f",
            perf_counter() - begonnen,
        )
        return RetrievedKnowledge()

    nach_kennung = {chunk.chunk_id: chunk for chunk in sortiert}

    # Eine einzige Rangfolge trägt beide Suchen — der Index ist derselbe.
    betriebsarten = tuple(
        chunk for chunk in sortiert if chunk.chunk_type == "business_pattern"
    )[: CHUNKS_PER_SEARCHED_TYPE["business_pattern"]]
    diagnosemuster = tuple(
        chunk for chunk in sortiert if chunk.chunk_type == "diagnostic_pattern"
    )[: CHUNKS_PER_SEARCHED_TYPE["diagnostic_pattern"]]

    buchstaben = _betriebsart_buchstaben(betriebsarten)

    # **Reihum, nicht der Reihe nach.**
    #
    # Vorher lief die Schleife Muster für Muster durch und nahm alles, was
    # das erste nannte. Da DP-06 fünf Familien führt und die Grenze bei vier
    # lag, kam das zweite Muster nie zum Zug — es wurde gesucht, gerankt,
    # protokolliert und trug nichts bei. Jetzt liefert jedes Muster erst
    # seine erste Familie, dann seine zweite, und so weiter.
    familien: list[KnowledgeChunk] = []
    listen = [list(_ids(muster, "passende_loesungsfamilien")) for muster in diagnosemuster]
    for runde in range(max((len(liste) for liste in listen), default=0)):
        for liste in listen:
            if len(familien) >= MAXIMUM_SOLUTION_FAMILIES:
                break
            if runde >= len(liste):
                continue
            kennung = liste[runde]
            kandidat = nach_kennung.get(kennung)
            if kandidat is None or kandidat in familien:
                continue
            if kandidat.chunk_type != "solution_family":
                continue
            if not _passt_zur_betriebsart(kandidat, buchstaben):
                logger.info(
                    "solution_architecture.family_filtered id=%s betriebsarten=%s",
                    kennung,
                    sorted(buchstaben),
                )
                continue
            familien.append(kandidat)
        if len(familien) >= MAXIMUM_SOLUTION_FAMILIES:
            break

    faehigkeiten: list[KnowledgeChunk] = []
    for familie in familien:
        for kennung in _ids(familie, "braucht_capabilities"):
            kandidat = nach_kennung.get(kennung)
            if (
                kandidat is None
                or kandidat in faehigkeiten
                or kandidat.chunk_type != "automation_capability"
            ):
                continue
            faehigkeiten.append(kandidat)
            if len(faehigkeiten) >= MAXIMUM_CAPABILITIES:
                break
        if len(faehigkeiten) >= MAXIMUM_CAPABILITIES:
            break

    # Das Zielbild, dessen enthaltene Familien am meisten überdecken. Bei
    # Gleichstand gewinnt das ähnlichere — `sortiert` ist danach geordnet.
    familien_kennungen = {familie.chunk_id for familie in familien}
    zielbild = None
    beste_ueberdeckung = 0
    for chunk in sortiert:
        if chunk.chunk_type != "target_architecture":
            continue
        ueberdeckung = len(
            familien_kennungen & set(_ids(chunk, "enthaltene_familien"))
        )
        if ueberdeckung > beste_ueberdeckung:
            zielbild, beste_ueberdeckung = chunk, ueberdeckung

    ergebnis = RetrievedKnowledge(
        betriebsarten=betriebsarten,
        diagnosemuster=diagnosemuster,
        loesungsfamilien=tuple(familien),
        faehigkeiten=tuple(faehigkeiten),
        zielbild=zielbild,
    )
    logger.info(
        "solution_architecture.retrieved seconds=%.2f betriebsart=%s "
        "business_pattern=%d diagnostic_pattern=%d solution_family=%d "
        "automation_capability=%d target_architecture=%d gesamt=%d",
        perf_counter() - begonnen,
        sorted(buchstaben) or "unbekannt",
        len(betriebsarten),
        len(diagnosemuster),
        len(familien),
        len(faehigkeiten),
        1 if zielbild is not None else 0,
        len(ergebnis.all_chunks()),
    )
    return ergebnis
