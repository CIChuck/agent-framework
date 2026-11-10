"""Exact operation-local batches, strict counts and fresh-scope application."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import chromadb
import pytest
from friday_memory.maintenance.mutation import (
    ExplicitMemoryMutationParticipant,
    MemoryMutationCommand,
    MemoryMutationResult,
    MemoryMutationStep,
    MemoryVectorAddition,
    MemoryVerificationCounts,
    MemoryVerificationSelection,
    MemoryVerificationStatus,
    MemoryVerificationUpdate,
    VectorMemoryReference,
)
from pydantic import ValidationError

from .test_mutation_participant import _participant

OP = "1" * 32


async def created_batch(
    participant: ExplicitMemoryMutationParticipant,
) -> MemoryMutationResult:
    plan = await participant.plan(MemoryMutationStep.SYNTHESIZE)
    group = plan.synthesis_groups[0]
    addition = MemoryVectorAddition(
        collection=group.collection,
        memory_id=f"reorg-synth-{group.fingerprint[:20]}",
        document="A distinct higher-order synthetic insight",
        embedding=(0.5, 0.5),
        source_memory_ids=group.source_memory_ids,
        topic=group.topic,
        confidence=0.95,
        reasoning="Supported by independent sources",
        synthesis_fingerprint=group.fingerprint,
        synthesis_version="1",
        created_at=datetime.now(UTC),
    )
    result = await participant.apply(
        plan,
        MemoryMutationCommand(
            plan_id=plan.plan_id,
            step=plan.step,
            vector_additions=(addition,),
            synthesis_metadata_migrations=plan.synthesis_metadata_migrations,
        ),
    )
    assert result.succeeded, result.errors
    return result


@pytest.mark.asyncio
async def test_selection_models_and_operation_receipts(tmp_path: Path) -> None:
    for value in [True, "1", 1.0, -1]:
        with pytest.raises(ValidationError):
            MemoryVerificationCounts(
                selected=value, verified=0, rejected=0, uncertain=0
            )
    with pytest.raises(ValidationError):
        MemoryVerificationCounts(selected=1, verified=0, rejected=0, uncertain=0)
    ref = VectorMemoryReference(collection="primary", memory_id="new-meta")
    for fields in [
        dict(mode="pending", references=(ref,)),
        dict(mode="created"),
        dict(
            mode="created",
            operation_id=OP,
            synthesis_plan_id="a" * 64,
            references=(ref, ref),
        ),
    ]:
        with pytest.raises(ValidationError):
            MemoryVerificationSelection(**fields)
    participant, _ = await _participant(tmp_path)
    participant.begin_operation(OP)
    with pytest.raises(RuntimeError):
        participant.begin_operation(OP)
    result = await created_batch(participant)
    selection = participant.verification_selection_for(result)
    assert len(selection.references) == 1
    ref = selection.references[0]
    assert ref.collection == "primary" and ref.memory_id.startswith("reorg-synth-")
    assert selection.operation_id == OP
    for changed in [
        result.model_copy(),
        result.model_copy(update={"created_references": ()}),
        result.model_copy(update={"step": MemoryMutationStep.VERIFY}),
    ]:
        with pytest.raises(ValueError):
            participant.verification_selection_for(changed)
    with pytest.raises(ValueError):
        await participant.plan(
            MemoryMutationStep.VERIFY,
            verification_selection=selection.model_copy(
                update={"operation_id": "2" * 32}
            ),
        )
    participant.end_operation(OP)
    participant.begin_operation("2" * 32)
    with pytest.raises(ValueError):
        participant.verification_selection_for(result)
    with pytest.raises(ValueError):
        await participant.plan(
            MemoryMutationStep.VERIFY, verification_selection=selection
        )
    participant.end_operation("2" * 32)


@pytest.mark.asyncio
async def test_scoped_apply_and_postconditions(tmp_path: Path) -> None:
    participant, _ = await _participant(tmp_path)
    participant.begin_operation(OP)
    result = await created_batch(participant)
    scope = participant.verification_selection_for(result)
    plan = await participant.plan(
        MemoryMutationStep.VERIFY, verification_selection=scope
    )
    assert [(r.collection, r.memory_id) for r in plan.provider_records] == [
        (r.collection, r.memory_id) for r in scope.references
    ]
    command = MemoryMutationCommand(
        plan_id=plan.plan_id,
        step=plan.step,
        verification_selection=scope,
        verification_updates=(
            MemoryVerificationUpdate(
                collection="primary",
                memory_id=scope.references[0].memory_id,
                status=MemoryVerificationStatus.UNCERTAIN,
                confidence=0.6,
            ),
        ),
    )
    # Missing exact selection must not silently re-plan the broad pending batch.
    wrong = await participant.apply(
        plan,
        command.model_copy(
            update={"verification_selection": MemoryVerificationSelection()}
        ),
    )
    assert not wrong.succeeded and wrong.verification_counts is None
    applied = await participant.apply(plan, command)
    assert applied.succeeded
    assert applied.verification_counts == MemoryVerificationCounts(
        selected=1, verified=0, rejected=0, uncertain=1
    )
    with pytest.raises(ValueError):
        participant.verification_selection_for(result)
    assert not (await participant.apply(plan, command)).succeeded
    participant.end_operation(OP)


@pytest.mark.asyncio
async def test_created_selection_refuses_missing_and_changed_record(
    tmp_path: Path,
) -> None:
    participant, _ = await _participant(tmp_path)
    participant.begin_operation(OP)
    result = await created_batch(participant)
    scope = participant.verification_selection_for(result)
    plan = await participant.plan(
        MemoryMutationStep.VERIFY, verification_selection=scope
    )
    collection = chromadb.PersistentClient(
        path=str(tmp_path / "vector")
    ).get_collection("primary")
    collection.update(
        ids=[scope.references[0].memory_id],
        documents=["changed after planning"],
        embeddings=[[0.5, 0.5]],
    )
    command = MemoryMutationCommand(
        plan_id=plan.plan_id,
        step=plan.step,
        verification_selection=scope,
        verification_updates=(
            MemoryVerificationUpdate(
                collection="primary",
                memory_id=scope.references[0].memory_id,
                status=MemoryVerificationStatus.VERIFIED,
                confidence=0.9,
            ),
        ),
    )
    assert not (await participant.apply(plan, command)).succeeded
    collection.delete(ids=[scope.references[0].memory_id])
    with pytest.raises(ValueError):
        await participant.plan(MemoryMutationStep.VERIFY, verification_selection=scope)
    participant.end_operation(OP)


@pytest.mark.asyncio
@pytest.mark.parametrize("migration", [False, True])
async def test_exact_empty_batch_is_not_pending(
    tmp_path: Path, migration: bool
) -> None:
    participant, _ = await _participant(tmp_path)
    participant.begin_operation(OP)
    if migration:
        collection = chromadb.PersistentClient(
            path=str(tmp_path / "vector")
        ).get_collection("primary")
        collection.add(
            ids=["legacy-meta"],
            documents=["Legacy synthesized memory"],
            metadatas=[
                {
                    "type": "meta_insight",
                    "source_memories": '["insight-a","insight-b"]',
                    "maintenance_generated": True,
                    "verification_status": "verified",
                }
            ],
            embeddings=[[0.75, 0.25]],
        )
    plan = await participant.plan(MemoryMutationStep.SYNTHESIZE)
    result = await participant.apply(
        plan,
        MemoryMutationCommand(
            plan_id=plan.plan_id,
            step=plan.step,
            synthesis_metadata_migrations=plan.synthesis_metadata_migrations,
        ),
    )
    assert result.succeeded and result.created_references == ()
    assert result.changed_count == int(migration)
    scope = participant.verification_selection_for(result)
    plan = await participant.plan(
        MemoryMutationStep.VERIFY, verification_selection=scope
    )
    assert plan.provider_records == () and plan.candidate_count == 0
    result = await participant.apply(
        plan,
        MemoryMutationCommand(
            plan_id=plan.plan_id, step=plan.step, verification_selection=scope
        ),
    )
    assert result.verification_counts == MemoryVerificationCounts(
        selected=0, verified=0, rejected=0, uncertain=0
    )
    participant.end_operation(OP)
