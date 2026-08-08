"""Typed graph/vector mutation boundary for coordinated Friday maintenance.

This module intentionally has no Friday Chat or Friday Transcript dependency.
Callers supply an explicit :class:`MemoryMaintenanceLayout`, obtain a read-only
plan, and apply only typed commands derived from that plan.  The participant
never guesses a persistence root and never accepts a transcript path.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import struct
from collections.abc import Iterable, Sequence
from enum import Enum
from typing import Protocol, runtime_checkable

import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from chromadb.errors import ChromaError
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    TypeAdapter,
    model_validator,
)

from friday_memory.adapters.graph import ElementXGraphStore
from friday_memory.maintenance.recovery_models import (
    CHROMA_REBUILD_MAXIMUM_FLOAT32_ULP_DRIFT,
    MemoryMaintenanceLayout,
)
from friday_memory.models.graph import MemoryStage


class StrictMutationModel(BaseModel):
    """Reject unknown fields at the public maintenance boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class MemoryMutationStep(str, Enum):
    """Closed graph/vector operations supported by the participant."""

    ANALYZE = "analyze"
    REEMBED = "reembed"
    DEDUPE = "dedupe"
    PRUNE = "prune"
    SYNTHESIZE = "synthesize"
    VERIFY = "verify"


class MemoryMutationErrorCode(str, Enum):
    """Stable content-safe failure categories."""

    INVALID_COMMAND = "invalid_command"
    STORE_UNAVAILABLE = "store_unavailable"
    STORE_INTEGRITY_FAILED = "store_integrity_failed"
    APPLY_FAILED = "apply_failed"
    POSTCONDITION_FAILED = "postcondition_failed"


class MemoryMutationError(StrictMutationModel):
    """Content-safe participant failure detail."""

    code: MemoryMutationErrorCode
    message: str
    store: str | None = None


class VectorMemoryReference(StrictMutationModel):
    """Stable reference to one record in one explicit Chroma collection."""

    collection: str
    memory_id: str


class VectorMemoryRecord(VectorMemoryReference):
    """Typed provider input retained in-process and never written to logs."""

    document: str | None = None
    metadata: dict[str, JsonValue] | None = None


_MAX_SOURCE_PROVENANCE_CHARS = 32_000


def _canonical_source_memories(source_memory_ids: tuple[str, ...]) -> str:
    """Encode bounded Chroma-scalar-safe synthesis lineage deterministically."""
    return json.dumps(
        source_memory_ids,
        ensure_ascii=True,
        separators=(",", ":"),
    )


class DuplicateMemoryGroup(StrictMutationModel):
    """One exact-content duplicate group with a deterministic survivor."""

    survivor: VectorMemoryReference
    duplicates: tuple[VectorMemoryReference, ...]


class GraphEdgeReference(StrictMutationModel):
    """Stable reference to a graph edge requiring maintenance."""

    source_id: str
    target_id: str
    relation: str


class VectorCollectionDimension(StrictMutationModel):
    """Observed public embedding dimension for one configured collection."""

    collection: str
    dimension: int = Field(gt=0, le=8192)


class MemoryMutationPlan(StrictMutationModel):
    """Read-only, typed plan for one operation.

    ``provider_records`` may contain memory content and is only for the
    explicitly injected maintenance-provider adapter.  User-facing reporting
    must use the nullable counts and references instead.
    """

    plan_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    step: MemoryMutationStep
    scanned_count: int | None = Field(default=None, ge=0)
    candidate_count: int | None = Field(default=None, ge=0)
    vector_collection_count: int = Field(default=0, ge=0)
    vector_collection_dimensions: tuple[VectorCollectionDimension, ...] = ()
    graph_node_count: int | None = Field(default=None, ge=0)
    graph_edge_count: int | None = Field(default=None, ge=0)
    duplicate_groups: tuple[DuplicateMemoryGroup, ...] = ()
    vector_targets: tuple[VectorMemoryReference, ...] = ()
    graph_node_targets: tuple[str, ...] = ()
    graph_edge_targets: tuple[GraphEdgeReference, ...] = ()
    provider_records: tuple[VectorMemoryRecord, ...] = ()
    target_records: tuple[VectorMemoryRecord, ...] = ()
    all_vector_references: tuple[VectorMemoryReference, ...] = ()
    maximum_output_count: int | None = Field(default=None, ge=0, le=128)
    warnings: tuple[str, ...] = ()
    errors: tuple[MemoryMutationError, ...] = ()


class MemoryMetadataUpdate(VectorMemoryReference):
    """Complete metadata replacement for one vector record."""

    metadata: dict[str, str | int | float | bool]


class MemoryVectorAddition(VectorMemoryReference):
    """One provider-produced synthesized vector record."""

    document: str = Field(min_length=1, max_length=32_000)
    embedding: tuple[float, ...] = Field(min_length=1, max_length=8192)
    source_memory_ids: tuple[str, ...] = Field(min_length=2, max_length=256)

    @model_validator(mode="after")
    def validate_embedding(self) -> MemoryVectorAddition:
        if not self.embedding or not all(
            math.isfinite(value) for value in self.embedding
        ):
            raise ValueError("embedding must contain only finite values")
        if len(self.source_memory_ids) != len(set(self.source_memory_ids)):
            raise ValueError("source memory identifiers must be unique")
        if (
            len(_canonical_source_memories(self.source_memory_ids))
            > _MAX_SOURCE_PROVENANCE_CHARS
        ):
            raise ValueError("source memory provenance exceeds its bounded limit")
        return self


class MemoryVerificationStatus(str, Enum):
    """Provider verdicts that may be persisted by verification."""

    VERIFIED = "verified"
    REJECTED = "rejected"
    UNCERTAIN = "uncertain"


class MemoryVerificationUpdate(VectorMemoryReference):
    """Bounded provider verdict for one planned memory record."""

    status: MemoryVerificationStatus
    confidence: float = Field(ge=0.0, le=1.0)


class MemoryEmbeddingUpdate(VectorMemoryReference):
    """One explicit replacement vector embedding."""

    embedding: tuple[float, ...] = Field(min_length=1, max_length=8192)

    @model_validator(mode="after")
    def validate_embedding(self) -> MemoryEmbeddingUpdate:
        if not self.embedding or not all(
            math.isfinite(value) for value in self.embedding
        ):
            raise ValueError("embedding must contain only finite values")
        return self


class GraphEmbeddingUpdate(GraphEdgeReference):
    """One explicit replacement graph-edge embedding."""

    embedding: tuple[float, ...] = Field(min_length=1, max_length=8192)

    @model_validator(mode="after")
    def validate_embedding(self) -> GraphEmbeddingUpdate:
        if not self.embedding or not all(
            math.isfinite(value) for value in self.embedding
        ):
            raise ValueError("embedding must contain only finite values")
        return self


class MemoryMutationCommand(StrictMutationModel):
    """Typed, step-specific mutation payload."""

    plan_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    step: MemoryMutationStep
    vector_additions: tuple[MemoryVectorAddition, ...] = ()
    verification_updates: tuple[MemoryVerificationUpdate, ...] = ()
    embedding_updates: tuple[MemoryEmbeddingUpdate, ...] = ()
    graph_embedding_updates: tuple[GraphEmbeddingUpdate, ...] = ()

    @model_validator(mode="after")
    def validate_step_payload(self) -> MemoryMutationCommand:
        fields_for_step = {
            MemoryMutationStep.SYNTHESIZE: self.vector_additions,
            MemoryMutationStep.VERIFY: self.verification_updates,
            MemoryMutationStep.REEMBED: (
                *self.embedding_updates,
                *self.graph_embedding_updates,
            ),
        }
        unexpected = any(
            value
            for selected_step, value in fields_for_step.items()
            if selected_step is not self.step
        )
        if self.step is MemoryMutationStep.ANALYZE or unexpected:
            raise ValueError("mutation command does not match its selected step")
        # Empty commands are valid typed no-change outcomes. Apply-time binding
        # rejects them when the fresh plan actually contains candidates.
        return self


class MemoryMutationResult(StrictMutationModel):
    """Honest result for one participant operation."""

    plan_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    step: MemoryMutationStep
    succeeded: bool
    scanned_count: int | None = Field(default=None, ge=0)
    changed_count: int | None = Field(default=None, ge=0)
    warnings: tuple[str, ...] = ()
    errors: tuple[MemoryMutationError, ...] = ()

    @model_validator(mode="after")
    def validate_outcome(self) -> MemoryMutationResult:
        if self.succeeded and self.errors:
            raise ValueError("successful mutation result cannot contain errors")
        if not self.succeeded and not self.errors:
            raise ValueError("failed mutation result requires typed errors")
        return self


class MemoryMutationVerification(StrictMutationModel):
    """Postcondition and live-integrity evidence."""

    verified: bool
    vector_collection_count: int | None = Field(default=None, ge=0)
    vector_record_count: int | None = Field(default=None, ge=0)
    graph_node_count: int | None = Field(default=None, ge=0)
    graph_edge_count: int | None = Field(default=None, ge=0)
    warnings: tuple[str, ...] = ()
    errors: tuple[MemoryMutationError, ...] = ()

    @model_validator(mode="after")
    def validate_outcome(self) -> MemoryMutationVerification:
        if self.verified and self.errors:
            raise ValueError("verified postconditions cannot contain errors")
        if not self.verified and not self.errors:
            raise ValueError("failed postconditions require typed errors")
        return self


@runtime_checkable
class MemoryMutationParticipant(Protocol):
    """Narrow public graph/vector planning and mutation interface."""

    async def plan(self, step: MemoryMutationStep) -> MemoryMutationPlan: ...

    async def apply(
        self,
        plan: MemoryMutationPlan,
        command: MemoryMutationCommand,
    ) -> MemoryMutationResult: ...

    async def verify_postconditions(
        self,
        commands: tuple[MemoryMutationCommand, ...],
    ) -> MemoryMutationVerification: ...


_SPACE_PATTERN = re.compile(r"\s+")
_JSON_MAPPING = TypeAdapter(dict[str, JsonValue])


class ExplicitMemoryMutationParticipant:
    """Public-API implementation bound to explicit graph/vector stores."""

    def __init__(
        self,
        layout: MemoryMaintenanceLayout,
        *,
        graph_store: ElementXGraphStore | None,
    ) -> None:
        self.layout = layout
        self._graph_store = graph_store

    @staticmethod
    def _with_plan_id(plan: MemoryMutationPlan) -> MemoryMutationPlan:
        payload = plan.model_dump(mode="json", exclude={"plan_id"})
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode()
        return plan.model_copy(update={"plan_id": hashlib.sha256(encoded).hexdigest()})

    @staticmethod
    def _open_client(path: str) -> ClientAPI:
        return chromadb.PersistentClient(path=path)

    def _collections(self) -> tuple[Collection, ...]:
        path = self.layout.vector_directory
        if not path.is_dir():
            raise FileNotFoundError("configured vector store is unavailable")
        client = self._open_client(str(path))
        return tuple(sorted(client.list_collections(), key=lambda item: item.name))

    @staticmethod
    def _records(collection: Collection) -> tuple[VectorMemoryRecord, ...]:
        result = collection.get(include=["documents", "metadatas"])
        ids = result.get("ids") or []
        documents = result.get("documents")
        metadatas = result.get("metadatas")
        records: list[VectorMemoryRecord] = []
        for index, memory_id in enumerate(ids):
            document = documents[index] if documents is not None else None
            metadata = (
                _JSON_MAPPING.validate_python(dict(metadatas[index]))
                if metadatas is not None and metadatas[index] is not None
                else None
            )
            records.append(
                VectorMemoryRecord(
                    collection=collection.name,
                    memory_id=str(memory_id),
                    document=document,
                    metadata=metadata,
                )
            )
        return tuple(sorted(records, key=lambda item: item.memory_id))

    @staticmethod
    def _collection_dimension(
        collection: Collection,
    ) -> VectorCollectionDimension | None:
        result = collection.get(limit=1, include=["embeddings"])
        embeddings = result.get("embeddings")
        if embeddings is None or len(embeddings) == 0:
            return None
        dimension = len(embeddings[0])
        if dimension <= 0:
            raise ValueError("configured collection has an invalid dimension")
        return VectorCollectionDimension(
            collection=collection.name,
            dimension=dimension,
        )

    @staticmethod
    def _is_active(record: VectorMemoryRecord) -> bool:
        metadata = record.metadata or {}
        return not any(
            (
                metadata.get("superseded_by"),
                metadata.get("stage") in {"decayed", "deleted"},
                metadata.get("status") == "deleted",
            )
        )

    @staticmethod
    def _normalized_document(document: str | None) -> str | None:
        if document is None:
            return None
        normalized = _SPACE_PATTERN.sub(" ", document).strip().casefold()
        return normalized or None

    @staticmethod
    def _is_insight(record: VectorMemoryRecord) -> bool:
        metadata = record.metadata or {}
        kind = metadata.get("type", metadata.get("memory_type"))
        return kind in {"insight", "long_term"}

    @classmethod
    def _duplicate_groups(
        cls, records: tuple[VectorMemoryRecord, ...]
    ) -> tuple[DuplicateMemoryGroup, ...]:
        grouped: dict[tuple[str, str], list[VectorMemoryRecord]] = {}
        for record in records:
            normalized = cls._normalized_document(record.document)
            if (
                normalized is None
                or not cls._is_active(record)
                or not cls._is_insight(record)
            ):
                continue
            grouped.setdefault((record.collection, normalized), []).append(record)
        duplicates: list[DuplicateMemoryGroup] = []
        for group in grouped.values():
            ordered = sorted(group, key=lambda item: item.memory_id)
            if len(ordered) < 2:
                continue
            duplicates.append(
                DuplicateMemoryGroup(
                    survivor=VectorMemoryReference(
                        collection=ordered[0].collection,
                        memory_id=ordered[0].memory_id,
                    ),
                    duplicates=tuple(
                        VectorMemoryReference(
                            collection=record.collection,
                            memory_id=record.memory_id,
                        )
                        for record in ordered[1:]
                    ),
                )
            )
        return tuple(
            sorted(
                duplicates,
                key=lambda item: (item.survivor.collection, item.survivor.memory_id),
            )
        )

    @staticmethod
    def _prune_targets(
        records: tuple[VectorMemoryRecord, ...],
    ) -> tuple[VectorMemoryReference, ...]:
        targets = []
        for record in records:
            metadata = record.metadata or {}
            if any(
                (
                    bool(metadata.get("superseded_by")),
                    metadata.get("stage") in {"decayed", "deleted"},
                    metadata.get("status") == "deleted",
                )
            ):
                targets.append(
                    VectorMemoryReference(
                        collection=record.collection,
                        memory_id=record.memory_id,
                    )
                )
        return tuple(targets)

    @staticmethod
    def _provider_candidates(
        step: MemoryMutationStep,
        records: tuple[VectorMemoryRecord, ...],
    ) -> tuple[VectorMemoryRecord, ...]:
        active = tuple(
            record
            for record in records
            if record.document and ExplicitMemoryMutationParticipant._is_active(record)
        )
        if step is MemoryMutationStep.SYNTHESIZE:
            topic_counts: dict[str, int] = {}
            for record in active:
                topic = (record.metadata or {}).get("topic")
                if isinstance(topic, str) and topic.strip():
                    topic_counts[topic.strip().casefold()] = (
                        topic_counts.get(topic.strip().casefold(), 0) + 1
                    )
            return tuple(
                record
                for record in active
                if isinstance((record.metadata or {}).get("topic"), str)
                and topic_counts.get(
                    str((record.metadata or {}).get("topic")).strip().casefold(), 0
                )
                >= 2
            )
        if step is MemoryMutationStep.VERIFY:
            return tuple(
                record
                for record in active
                if (record.metadata or {}).get("verification_status")
                not in {"verified", "rejected"}
            )
        if step is MemoryMutationStep.REEMBED:
            return active
        return ()

    async def plan(self, step: MemoryMutationStep) -> MemoryMutationPlan:
        """Build a side-effect-free plan from explicit graph/vector state."""
        try:
            collections = self._collections()
            records = tuple(
                record
                for collection in collections
                for record in self._records(collection)
            )
            collection_dimensions = tuple(
                dimension
                for collection in collections
                if (dimension := self._collection_dimension(collection)) is not None
            )
            graph_nodes = (
                await self._graph_store.get_all_nodes()
                if self._graph_store is not None
                else []
            )
            graph_edges = (
                await self._graph_store.get_all_edges()
                if self._graph_store is not None
                else []
            )
        except (ChromaError, OSError, RuntimeError, ValueError) as exc:
            return self._with_plan_id(
                MemoryMutationPlan(
                    plan_id="0" * 64,
                    step=step,
                    errors=(
                        MemoryMutationError(
                            code=MemoryMutationErrorCode.STORE_UNAVAILABLE,
                            message=f"memory mutation planning failed ({type(exc).__name__})",
                        ),
                    ),
                )
            )

        duplicate_groups = self._duplicate_groups(records)
        prune_targets = self._prune_targets(records)
        graph_prune_targets = tuple(
            sorted(
                node.id
                for node in graph_nodes
                if node.stage in {MemoryStage.DECAYED, MemoryStage.DELETED}
            )
        )
        edge_targets = tuple(
            GraphEdgeReference(
                source_id=edge.source_id,
                target_id=edge.target_id,
                relation=edge.relation,
            )
            for edge in sorted(
                graph_edges,
                key=lambda item: (item.source_id, item.target_id, item.relation),
            )
            if step is MemoryMutationStep.REEMBED
        )
        provider_records = self._provider_candidates(step, records)
        synthesis_topics = {
            (
                record.collection,
                str((record.metadata or {}).get("topic")).strip().casefold(),
            )
            for record in provider_records
            if step is MemoryMutationStep.SYNTHESIZE
        }
        if step is MemoryMutationStep.DEDUPE:
            candidate_count = sum(len(group.duplicates) for group in duplicate_groups)
        elif step is MemoryMutationStep.PRUNE:
            candidate_count = len(prune_targets) + len(graph_prune_targets)
        elif step in {
            MemoryMutationStep.SYNTHESIZE,
            MemoryMutationStep.VERIFY,
            MemoryMutationStep.REEMBED,
        }:
            candidate_count = len(provider_records) + len(edge_targets)
        else:
            candidate_count = (
                sum(len(group.duplicates) for group in duplicate_groups)
                + len(prune_targets)
                + len(graph_prune_targets)
            )
        target_references = {
            (target.collection, target.memory_id)
            for group in duplicate_groups
            for target in group.duplicates
        }
        if step is MemoryMutationStep.PRUNE:
            target_references = {
                (target.collection, target.memory_id) for target in prune_targets
            }
        target_records = tuple(
            record
            for record in records
            if (record.collection, record.memory_id) in target_references
        )
        return self._with_plan_id(
            MemoryMutationPlan(
                plan_id="0" * 64,
                step=step,
                scanned_count=len(records) + len(graph_nodes) + len(graph_edges),
                candidate_count=candidate_count,
                vector_collection_count=len(collections),
                vector_collection_dimensions=collection_dimensions,
                graph_node_count=len(graph_nodes),
                graph_edge_count=len(graph_edges),
                duplicate_groups=(
                    duplicate_groups
                    if step in {MemoryMutationStep.ANALYZE, MemoryMutationStep.DEDUPE}
                    else ()
                ),
                vector_targets=(
                    prune_targets if step is MemoryMutationStep.PRUNE else ()
                ),
                graph_node_targets=(
                    graph_prune_targets if step is MemoryMutationStep.PRUNE else ()
                ),
                graph_edge_targets=edge_targets,
                provider_records=provider_records,
                target_records=target_records,
                all_vector_references=tuple(
                    VectorMemoryReference(
                        collection=record.collection,
                        memory_id=record.memory_id,
                    )
                    for record in records
                ),
                maximum_output_count=(
                    len(synthesis_topics)
                    if step is MemoryMutationStep.SYNTHESIZE
                    else None
                ),
            )
        )

    def _collection_map(self) -> dict[str, Collection]:
        return {collection.name: collection for collection in self._collections()}

    @staticmethod
    def _write_metadata(
        metadata: dict[str, JsonValue] | None,
    ) -> dict[str, str | int | float | bool]:
        result: dict[str, str | int | float | bool] = {}
        for key, value in (metadata or {}).items():
            if isinstance(value, (str, int, float, bool)):
                result[key] = value
            elif value is not None:
                raise ValueError("vector metadata is not publicly writable")
        return result

    @staticmethod
    def _command_has_payload(command: MemoryMutationCommand) -> bool:
        return bool(
            command.vector_additions
            or command.verification_updates
            or command.embedding_updates
            or command.graph_embedding_updates
        )

    @staticmethod
    def _reference_key(reference: VectorMemoryReference) -> tuple[str, str]:
        return reference.collection, reference.memory_id

    def _validate_bound_command(
        self,
        plan: MemoryMutationPlan,
        command: MemoryMutationCommand,
    ) -> None:
        if (
            plan.step is not command.step
            or plan.plan_id != command.plan_id
            or plan.errors
        ):
            raise ValueError("mutation command is not bound to the supplied plan")
        if plan.candidate_count == 0:
            if self._command_has_payload(command):
                raise ValueError("no-change plan cannot accept mutation payload")
            return
        if command.step in {MemoryMutationStep.DEDUPE, MemoryMutationStep.PRUNE}:
            if self._command_has_payload(command):
                raise ValueError("deterministic step cannot accept caller targets")
            return
        provider_keys = {
            self._reference_key(record) for record in plan.provider_records
        }
        dimensions = {
            item.collection: item.dimension
            for item in plan.vector_collection_dimensions
        }
        if command.step is MemoryMutationStep.SYNTHESIZE:
            allowed_collections = {
                record.collection for record in plan.provider_records
            }
            existing_keys = {
                self._reference_key(reference)
                for reference in plan.all_vector_references
            }
            prefix = f"reorg-{plan.plan_id[:12]}-"
            addition_keys = {
                self._reference_key(addition) for addition in command.vector_additions
            }
            if (
                not command.vector_additions
                or plan.maximum_output_count is None
                or len(command.vector_additions) > plan.maximum_output_count
                or len(addition_keys) != len(command.vector_additions)
            ):
                raise ValueError("synthesis candidates require provider output")
            for addition in command.vector_additions:
                source_keys = {
                    (addition.collection, memory_id)
                    for memory_id in addition.source_memory_ids
                }
                if (
                    addition.collection not in allowed_collections
                    or not addition.memory_id.startswith(prefix)
                    or self._reference_key(addition) in existing_keys
                    or not addition.document.strip()
                    or dimensions.get(addition.collection) != len(addition.embedding)
                    or len(source_keys) < 2
                    or not source_keys.issubset(provider_keys)
                ):
                    raise ValueError("synthesis output exceeds its fresh plan")
            return
        if command.step is MemoryMutationStep.VERIFY:
            update_keys = {
                self._reference_key(update) for update in command.verification_updates
            }
            if update_keys != provider_keys or len(update_keys) != len(
                command.verification_updates
            ):
                raise ValueError("verification output does not cover its fresh plan")
            return
        if command.step is MemoryMutationStep.REEMBED:
            update_keys = {
                self._reference_key(update) for update in command.embedding_updates
            }
            edge_keys = {
                (update.source_id, update.target_id, update.relation)
                for update in command.graph_embedding_updates
            }
            planned_edge_keys = {
                (target.source_id, target.target_id, target.relation)
                for target in plan.graph_edge_targets
            }
            configured_dimensions = set(dimensions.values())
            if (
                update_keys != provider_keys
                or len(update_keys) != len(command.embedding_updates)
                or edge_keys != planned_edge_keys
                or len(edge_keys) != len(command.graph_embedding_updates)
                or any(
                    dimensions.get(update.collection) != len(update.embedding)
                    for update in command.embedding_updates
                )
                or (
                    bool(command.graph_embedding_updates)
                    and (
                        len(configured_dimensions) != 1
                        or any(
                            len(update.embedding) not in configured_dimensions
                            for update in command.graph_embedding_updates
                        )
                    )
                )
            ):
                raise ValueError("embedding output does not cover its fresh plan")
            return
        raise ValueError("unsupported mutation command")

    async def apply(
        self,
        plan: MemoryMutationPlan,
        command: MemoryMutationCommand,
    ) -> MemoryMutationResult:
        """Apply one already-validated command through public store APIs."""
        changed = 0
        try:
            fresh_plan = await self.plan(command.step)
            if fresh_plan.plan_id != plan.plan_id:
                raise ValueError("memory mutation plan is stale")
            self._validate_bound_command(fresh_plan, command)
            if fresh_plan.candidate_count == 0:
                return MemoryMutationResult(
                    plan_id=plan.plan_id,
                    step=command.step,
                    succeeded=True,
                    scanned_count=plan.scanned_count,
                    changed_count=0,
                )
            collections = self._collection_map()
            deterministic_updates: list[MemoryMetadataUpdate] = []
            if command.step is MemoryMutationStep.DEDUPE:
                records = {
                    self._reference_key(record): record
                    for record in fresh_plan.target_records
                }
                for group in fresh_plan.duplicate_groups:
                    for duplicate in group.duplicates:
                        metadata = self._write_metadata(
                            records[self._reference_key(duplicate)].metadata
                        )
                        metadata["superseded_by"] = group.survivor.memory_id
                        deterministic_updates.append(
                            MemoryMetadataUpdate(
                                collection=duplicate.collection,
                                memory_id=duplicate.memory_id,
                                metadata=metadata,
                            )
                        )
            if command.step is MemoryMutationStep.VERIFY:
                records = {
                    self._reference_key(record): record
                    for record in fresh_plan.provider_records
                }
                for verification_update in command.verification_updates:
                    metadata = self._write_metadata(
                        records[self._reference_key(verification_update)].metadata
                    )
                    metadata["verification_status"] = verification_update.status.value
                    metadata["verification_confidence"] = verification_update.confidence
                    deterministic_updates.append(
                        MemoryMetadataUpdate(
                            collection=verification_update.collection,
                            memory_id=verification_update.memory_id,
                            metadata=metadata,
                        )
                    )
            for metadata_update in deterministic_updates:
                collections[metadata_update.collection].update(
                    ids=[metadata_update.memory_id],
                    metadatas=[metadata_update.metadata],
                )
                changed += 1
            grouped_deletions: dict[str, list[str]] = {}
            for target in (
                fresh_plan.vector_targets
                if command.step is MemoryMutationStep.PRUNE
                else ()
            ):
                grouped_deletions.setdefault(target.collection, []).append(
                    target.memory_id
                )
            for collection_name, memory_ids in grouped_deletions.items():
                collections[collection_name].delete(ids=memory_ids)
                changed += len(memory_ids)
            if (
                command.step is MemoryMutationStep.PRUNE
                and fresh_plan.graph_node_targets
            ):
                if self._graph_store is None:
                    raise RuntimeError("configured graph store is unavailable")
                for node_id in fresh_plan.graph_node_targets:
                    if await self._graph_store.remove_node(node_id):
                        changed += 1
            grouped_additions: dict[str, list[MemoryVectorAddition]] = {}
            for addition in command.vector_additions:
                grouped_additions.setdefault(addition.collection, []).append(addition)
            for collection_name, additions in grouped_additions.items():
                addition_embeddings: list[Sequence[float] | Sequence[int]] = [
                    list(addition.embedding) for addition in additions
                ]
                collections[collection_name].add(
                    ids=[addition.memory_id for addition in additions],
                    documents=[addition.document for addition in additions],
                    metadatas=[
                        {
                            "type": "meta_insight",
                            "source_count": len(addition.source_memory_ids),
                            "source_memories": _canonical_source_memories(
                                addition.source_memory_ids
                            ),
                            "provenance_source_type": "synthesis",
                            "maintenance_generated": True,
                            "verification_status": "unverified",
                        }
                        for addition in additions
                    ],
                    embeddings=addition_embeddings,
                )
                changed += len(additions)
            for embedding_update in command.embedding_updates:
                update_embeddings: list[Sequence[float] | Sequence[int]] = [
                    list(embedding_update.embedding)
                ]
                collections[embedding_update.collection].update(
                    ids=[embedding_update.memory_id], embeddings=update_embeddings
                )
                changed += 1
            if command.graph_embedding_updates:
                if self._graph_store is None:
                    raise RuntimeError("configured graph store is unavailable")
                changed += await self._graph_store.update_edges_embeddings(
                    [
                        (
                            update.source_id,
                            update.target_id,
                            list(update.embedding),
                        )
                        for update in command.graph_embedding_updates
                    ]
                )
        except (ChromaError, KeyError, OSError, RuntimeError, ValueError) as exc:
            return MemoryMutationResult(
                plan_id=plan.plan_id,
                step=command.step,
                succeeded=False,
                scanned_count=plan.scanned_count,
                changed_count=changed,
                errors=(
                    MemoryMutationError(
                        code=MemoryMutationErrorCode.APPLY_FAILED,
                        message=f"memory mutation failed ({type(exc).__name__})",
                    ),
                ),
            )
        return MemoryMutationResult(
            plan_id=plan.plan_id,
            step=command.step,
            succeeded=True,
            scanned_count=plan.scanned_count,
            changed_count=changed,
        )

    async def verify_postconditions(
        self,
        commands: tuple[MemoryMutationCommand, ...],
    ) -> MemoryMutationVerification:
        """Verify live stores and selected deterministic postconditions."""
        try:
            collections = self._collections()
            collections_by_name = {
                collection.name: collection for collection in collections
            }
            records = tuple(
                record
                for collection in collections
                for record in self._records(collection)
            )
            nodes = (
                await self._graph_store.get_all_nodes()
                if self._graph_store is not None
                else []
            )
            edges = (
                await self._graph_store.get_all_edges()
                if self._graph_store is not None
                else []
            )
            steps = {command.step for command in commands}
            if MemoryMutationStep.DEDUPE in steps and self._duplicate_groups(records):
                raise ValueError("active exact duplicate insights remain")
            if MemoryMutationStep.PRUNE in steps:
                if self._prune_targets(records):
                    raise ValueError("explicit vector prune targets remain")
                if any(
                    node.stage in {MemoryStage.DECAYED, MemoryStage.DELETED}
                    for node in nodes
                ):
                    raise ValueError("explicit graph prune targets remain")
            graph_edges_by_key = {
                (edge.source_id, edge.target_id, edge.relation): edge for edge in edges
            }
            for command in commands:
                for addition in command.vector_additions:
                    result = collections_by_name[addition.collection].get(
                        ids=[addition.memory_id],
                        include=["documents", "metadatas", "embeddings"],
                    )
                    if result.get("ids") != [addition.memory_id]:
                        raise ValueError("synthesized memory is absent")
                    documents = result.get("documents")
                    metadatas = result.get("metadatas")
                    embeddings = result.get("embeddings")
                    if (
                        documents is None
                        or documents[0] != addition.document
                        or metadatas is None
                        or (metadatas[0] or {}).get("type") != "meta_insight"
                        or (metadatas[0] or {}).get("source_count")
                        != len(addition.source_memory_ids)
                        or (metadatas[0] or {}).get("source_memories")
                        != _canonical_source_memories(addition.source_memory_ids)
                        or (metadatas[0] or {}).get("provenance_source_type")
                        != "synthesis"
                        or (metadatas[0] or {}).get("maintenance_generated") is not True
                        or embeddings is None
                        or not self._embedding_equivalent(
                            embeddings[0], addition.embedding
                        )
                    ):
                        raise ValueError("synthesis postcondition failed")
                for verification_update in command.verification_updates:
                    result = collections_by_name[verification_update.collection].get(
                        ids=[verification_update.memory_id], include=["metadatas"]
                    )
                    metadatas = result.get("metadatas")
                    if metadatas is None or metadatas[0] is None:
                        raise ValueError("verification metadata is absent")
                    metadata = metadatas[0]
                    confidence = metadata.get("verification_confidence")
                    if (
                        metadata.get("verification_status")
                        != verification_update.status.value
                        or not isinstance(confidence, (int, float))
                        or not math.isclose(
                            float(confidence),
                            verification_update.confidence,
                            abs_tol=1e-7,
                        )
                    ):
                        raise ValueError("verification metadata postcondition failed")
                for embedding_update in command.embedding_updates:
                    result = collections_by_name[embedding_update.collection].get(
                        ids=[embedding_update.memory_id], include=["embeddings"]
                    )
                    embeddings = result.get("embeddings")
                    if embeddings is None or not self._embedding_equivalent(
                        embeddings[0], embedding_update.embedding
                    ):
                        raise ValueError("vector embedding postcondition failed")
                for graph_embedding_update in command.graph_embedding_updates:
                    edge = graph_edges_by_key.get(
                        (
                            graph_embedding_update.source_id,
                            graph_embedding_update.target_id,
                            graph_embedding_update.relation,
                        )
                    )
                    if (
                        edge is None
                        or edge.embedding is None
                        or tuple(edge.embedding)
                        != tuple(graph_embedding_update.embedding)
                    ):
                        raise ValueError("graph embedding postcondition failed")
        except (ChromaError, OSError, RuntimeError, TypeError, ValueError) as exc:
            return MemoryMutationVerification(
                verified=False,
                errors=(
                    MemoryMutationError(
                        code=MemoryMutationErrorCode.POSTCONDITION_FAILED,
                        message=f"memory postcondition verification failed ({type(exc).__name__})",
                    ),
                ),
            )
        return MemoryMutationVerification(
            verified=True,
            vector_collection_count=len(collections),
            vector_record_count=len(records),
            graph_node_count=len(nodes),
            graph_edge_count=len(edges),
        )

    @staticmethod
    def _float32_ordered_integer(value: float, *, round_input: bool) -> int:
        if not math.isfinite(value):
            raise ValueError("embedding contains a non-finite value")
        try:
            encoded = struct.pack("!f", value)
        except (OverflowError, struct.error) as exc:
            raise ValueError("embedding is outside the finite float32 range") from exc
        restored = float(struct.unpack("!f", encoded)[0])
        if not round_input and restored != value:
            raise ValueError("stored embedding is not exactly represented as float32")
        bits = int.from_bytes(encoded, byteorder="big")
        if bits & 0x80000000:
            return ~bits & 0xFFFFFFFF
        return bits | 0x80000000

    @classmethod
    def _embedding_equivalent(
        cls,
        actual: Iterable[float | int],
        expected: Iterable[float | int],
    ) -> bool:
        actual_values = tuple(actual)
        expected_values = tuple(expected)
        return len(actual_values) == len(expected_values) and all(
            abs(
                cls._float32_ordered_integer(float(first), round_input=False)
                - cls._float32_ordered_integer(float(second), round_input=True)
            )
            <= CHROMA_REBUILD_MAXIMUM_FLOAT32_ULP_DRIFT
            for first, second in zip(actual_values, expected_values, strict=True)
        )


__all__ = [
    "DuplicateMemoryGroup",
    "ExplicitMemoryMutationParticipant",
    "GraphEdgeReference",
    "GraphEmbeddingUpdate",
    "MemoryEmbeddingUpdate",
    "MemoryMetadataUpdate",
    "MemoryMutationCommand",
    "MemoryMutationError",
    "MemoryMutationErrorCode",
    "MemoryMutationParticipant",
    "MemoryMutationPlan",
    "MemoryMutationResult",
    "MemoryMutationStep",
    "MemoryMutationVerification",
    "MemoryVerificationStatus",
    "MemoryVerificationUpdate",
    "MemoryVectorAddition",
    "VectorMemoryRecord",
    "VectorMemoryReference",
    "VectorCollectionDimension",
]
