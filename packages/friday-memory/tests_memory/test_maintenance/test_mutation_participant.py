"""Production graph/vector mutation participant tests with synthetic stores."""

import json
from collections.abc import Sequence
from pathlib import Path

import chromadb
import pytest
from friday_memory import (
    ElementXGraphStore,
    ExplicitMemoryMutationParticipant,
    GraphEdge,
    GraphEmbeddingUpdate,
    GraphNode,
    MemoryEmbeddingUpdate,
    MemoryMaintenanceLayout,
    MemoryMutationCommand,
    MemoryMutationStep,
    MemoryVectorAddition,
    MemoryVerificationStatus,
    MemoryVerificationUpdate,
    ProvenanceMetadata,
)
from friday_memory.models.graph import MemoryStage as GraphMemoryStage
from pydantic import ValidationError


async def _participant(
    root: Path,
) -> tuple[ExplicitMemoryMutationParticipant, ElementXGraphStore]:
    vector = root / "vector"
    graph_path = root / "graph.gpickle"
    client = chromadb.PersistentClient(path=str(vector))
    primary = client.create_collection("primary")
    embeddings: list[Sequence[float] | Sequence[int]] = [
        [1.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
        [0.5, 0.5],
    ]
    primary.add(
        ids=["insight-a", "insight-b", "expired", "pending"],
        documents=[
            "Synthetic duplicate insight",
            "  synthetic   duplicate INSIGHT ",
            "Synthetic expired memory",
            "Synthetic pending fact",
        ],
        metadatas=[
            {"type": "insight", "topic": "synthetic"},
            {"type": "insight", "topic": "synthetic"},
            {"type": "insight", "stage": "decayed"},
            {"type": "insight", "topic": "synthetic"},
        ],
        embeddings=embeddings,
    )
    secondary = client.create_collection("secondary")
    secondary_embedding: list[Sequence[float] | Sequence[int]] = [[0.25, 0.75]]
    secondary.add(
        ids=["secondary-a"],
        documents=["Synthetic secondary memory"],
        metadatas=[{"type": "insight"}],
        embeddings=secondary_embedding,
    )
    graph = ElementXGraphStore(str(graph_path))
    await graph.add_node(
        GraphNode(
            id="active-node",
            type="Entity",
            label="Synthetic active node",
            provenance=ProvenanceMetadata(
                source_id="synthetic-source-a",
                source_type="test",
            ),
        )
    )
    await graph.add_edge(
        GraphEdge(
            source_id="active-node",
            target_id="decayed-node",
            relation="synthetic_relation",
            provenance=ProvenanceMetadata(
                source_id="synthetic-edge-source",
                source_type="test",
            ),
        )
    )
    await graph.add_node(
        GraphNode(
            id="decayed-node",
            type="Entity",
            label="Synthetic decayed node",
            stage=GraphMemoryStage.DECAYED,
            provenance=ProvenanceMetadata(
                source_id="synthetic-source-b",
                source_type="test",
            ),
        )
    )
    layout = MemoryMaintenanceLayout(
        vector_directory=vector,
        graph_path=graph_path,
        recovery_directory=root / "recovery",
        log_directory=root / "logs",
    )
    return ExplicitMemoryMutationParticipant(layout, graph_store=graph), graph


@pytest.mark.asyncio
async def test_plans_are_read_only_and_cover_all_configured_collections(
    tmp_path: Path,
) -> None:
    participant, _ = await _participant(tmp_path)
    before = {
        collection.name: collection.count()
        for collection in chromadb.PersistentClient(
            path=str(tmp_path / "vector")
        ).list_collections()
    }

    analysis = await participant.plan(MemoryMutationStep.ANALYZE)
    dedupe = await participant.plan(MemoryMutationStep.DEDUPE)
    prune = await participant.plan(MemoryMutationStep.PRUNE)
    synthesize = await participant.plan(MemoryMutationStep.SYNTHESIZE)
    verify = await participant.plan(MemoryMutationStep.VERIFY)
    reembed = await participant.plan(MemoryMutationStep.REEMBED)

    assert analysis.errors == ()
    assert analysis.vector_collection_count == 2
    assert analysis.scanned_count == 8
    assert dedupe.candidate_count == 1
    assert dedupe.duplicate_groups[0].survivor.memory_id == "insight-a"
    assert dedupe.duplicate_groups[0].duplicates[0].memory_id == "insight-b"
    assert prune.candidate_count == 2
    assert [target.memory_id for target in prune.vector_targets] == ["expired"]
    assert prune.graph_node_targets == ("decayed-node",)
    assert synthesize.candidate_count == 3
    assert verify.candidate_count == 4
    assert reembed.candidate_count == 5
    assert {
        collection.name: collection.count()
        for collection in chromadb.PersistentClient(
            path=str(tmp_path / "vector")
        ).list_collections()
    } == before
    assert not (tmp_path / "recovery").exists()
    assert not (tmp_path / "logs").exists()


@pytest.mark.asyncio
async def test_dedupe_and_prune_apply_actual_counts_and_postconditions(
    tmp_path: Path,
) -> None:
    participant, graph = await _participant(tmp_path)
    dedupe_plan = await participant.plan(MemoryMutationStep.DEDUPE)
    client = chromadb.PersistentClient(path=str(tmp_path / "vector"))
    primary = client.get_collection("primary")
    dedupe_command = MemoryMutationCommand(
        plan_id=dedupe_plan.plan_id,
        step=MemoryMutationStep.DEDUPE,
    )
    dedupe_result = await participant.apply(
        dedupe_plan,
        dedupe_command,
    )

    assert dedupe_result.succeeded
    assert dedupe_result.changed_count == 1
    assert (await participant.verify_postconditions((dedupe_command,))).verified

    prune_plan = await participant.plan(MemoryMutationStep.PRUNE)
    prune_command = MemoryMutationCommand(
        plan_id=prune_plan.plan_id,
        step=MemoryMutationStep.PRUNE,
    )
    prune_result = await participant.apply(
        prune_plan,
        prune_command,
    )

    assert prune_result.succeeded
    assert prune_result.changed_count == 3
    assert primary.get(ids=["insight-b", "expired"])["ids"] == []
    assert await graph.get_node("decayed-node") is None
    verification = await participant.verify_postconditions(
        (dedupe_command, prune_command)
    )
    assert verification.verified
    assert verification.vector_collection_count == 2
    assert verification.vector_record_count == 3
    assert verification.graph_node_count == 1


@pytest.mark.asyncio
async def test_provider_commands_are_confined_to_fresh_plan(tmp_path: Path) -> None:
    participant, _ = await _participant(tmp_path)
    plan = await participant.plan(MemoryMutationStep.VERIFY)
    unplanned = MemoryVerificationUpdate(
        collection="primary",
        memory_id="not-in-plan",
        status=MemoryVerificationStatus.UNCERTAIN,
        confidence=0.5,
    )

    result = await participant.apply(
        plan,
        MemoryMutationCommand(
            plan_id=plan.plan_id,
            step=MemoryMutationStep.VERIFY,
            verification_updates=(unplanned,),
        ),
    )

    assert not result.succeeded
    assert result.changed_count == 0
    assert result.errors[0].code.value == "apply_failed"


def test_synthesis_source_provenance_is_bounded() -> None:
    with pytest.raises(ValidationError, match="provenance exceeds"):
        MemoryVectorAddition(
            collection="primary",
            memory_id="synthetic-meta-insight",
            document="Synthetic provider-produced insight",
            embedding=(0.75, 0.25),
            source_memory_ids=("a" * 16_000, "b" * 16_000),
        )


@pytest.mark.asyncio
async def test_synthesis_verification_and_reembedding_postconditions(
    tmp_path: Path,
) -> None:
    synthesis_participant, _ = await _participant(tmp_path / "synthesis")
    synthesis_plan = await synthesis_participant.plan(MemoryMutationStep.SYNTHESIZE)
    synthesis = MemoryVectorAddition(
        collection="primary",
        memory_id=f"reorg-{synthesis_plan.plan_id[:12]}-synthetic",
        document="Synthetic provider-produced insight",
        embedding=(0.75, 0.25),
        source_memory_ids=("insight-a", "insight-b"),
    )
    synthesis_command = MemoryMutationCommand(
        plan_id=synthesis_plan.plan_id,
        step=MemoryMutationStep.SYNTHESIZE,
        vector_additions=(synthesis,),
    )
    synthesis_result = await synthesis_participant.apply(
        synthesis_plan, synthesis_command
    )
    assert synthesis_result.succeeded
    assert synthesis_result.changed_count == 1
    assert (
        await synthesis_participant.verify_postconditions((synthesis_command,))
    ).verified
    synthesis_collection = chromadb.PersistentClient(
        path=str(tmp_path / "synthesis" / "vector")
    ).get_collection("primary")
    synthesized_record = synthesis_collection.get(
        ids=[synthesis.memory_id],
        include=["metadatas"],
    )
    synthesized_metadatas = synthesized_record.get("metadatas")
    assert synthesized_metadatas is not None
    synthesized_metadata = synthesized_metadatas[0]
    assert synthesized_metadata is not None
    assert synthesized_metadata["type"] == "meta_insight"
    assert synthesized_metadata["source_count"] == 2
    assert json.loads(str(synthesized_metadata["source_memories"])) == [
        "insight-a",
        "insight-b",
    ]
    assert synthesized_metadata["source_memories"] == '["insight-a","insight-b"]'
    assert synthesized_metadata["provenance_source_type"] == "synthesis"
    verification_after_synthesis = await synthesis_participant.plan(
        MemoryMutationStep.VERIFY
    )
    reembedding_after_synthesis = await synthesis_participant.plan(
        MemoryMutationStep.REEMBED
    )
    synthesized_key = (synthesis.collection, synthesis.memory_id)
    assert synthesized_key in {
        (record.collection, record.memory_id)
        for record in verification_after_synthesis.provider_records
    }
    assert synthesized_key in {
        (record.collection, record.memory_id)
        for record in reembedding_after_synthesis.provider_records
    }
    synthesis_collection.update(
        ids=[synthesis.memory_id],
        metadatas=[{**synthesized_metadata, "source_memories": '["wrong"]'}],
    )
    corrupted_provenance = await synthesis_participant.verify_postconditions(
        (synthesis_command,)
    )
    assert not corrupted_provenance.verified
    assert corrupted_provenance.errors[0].code.value == "postcondition_failed"

    verification_participant, _ = await _participant(tmp_path / "verification")
    verification_plan = await verification_participant.plan(MemoryMutationStep.VERIFY)
    verification_updates = tuple(
        MemoryVerificationUpdate(
            collection=record.collection,
            memory_id=record.memory_id,
            status=MemoryVerificationStatus.VERIFIED,
            confidence=0.9,
        )
        for record in verification_plan.provider_records
    )
    verification_command = MemoryMutationCommand(
        plan_id=verification_plan.plan_id,
        step=MemoryMutationStep.VERIFY,
        verification_updates=verification_updates,
    )
    verification_result = await verification_participant.apply(
        verification_plan, verification_command
    )
    assert verification_result.succeeded
    assert verification_result.changed_count == len(verification_updates)
    assert (
        await verification_participant.verify_postconditions((verification_command,))
    ).verified

    reembed_participant, _ = await _participant(tmp_path / "reembed")
    reembed_plan = await reembed_participant.plan(MemoryMutationStep.REEMBED)
    embedding_updates = tuple(
        MemoryEmbeddingUpdate(
            collection=record.collection,
            memory_id=record.memory_id,
            embedding=(0.3, 0.7),
        )
        for record in reembed_plan.provider_records
    )
    graph_embedding_updates = tuple(
        GraphEmbeddingUpdate(
            source_id=edge.source_id,
            target_id=edge.target_id,
            relation=edge.relation,
            embedding=(0.4, 0.6),
        )
        for edge in reembed_plan.graph_edge_targets
    )
    reembed_command = MemoryMutationCommand(
        plan_id=reembed_plan.plan_id,
        step=MemoryMutationStep.REEMBED,
        embedding_updates=embedding_updates,
        graph_embedding_updates=graph_embedding_updates,
    )
    reembed_result = await reembed_participant.apply(reembed_plan, reembed_command)
    assert reembed_result.succeeded
    assert reembed_result.changed_count == 5
    assert (
        await reembed_participant.verify_postconditions((reembed_command,))
    ).verified


def test_empty_no_change_command_is_valid_but_mismatched_payload_is_rejected() -> None:
    command = MemoryMutationCommand(
        plan_id="0" * 64,
        step=MemoryMutationStep.PRUNE,
    )
    assert command.verification_updates == ()
    with pytest.raises(ValueError, match="does not match"):
        MemoryMutationCommand(
            plan_id="0" * 64,
            step=MemoryMutationStep.DEDUPE,
            verification_updates=(
                MemoryVerificationUpdate(
                    collection="primary",
                    memory_id="synthetic-memory",
                    status=MemoryVerificationStatus.UNCERTAIN,
                    confidence=0.5,
                ),
            ),
        )


def test_provider_models_reject_type_coercion() -> None:
    with pytest.raises(ValidationError):
        MemoryVerificationUpdate.model_validate(
            {
                "collection": "primary",
                "memory_id": "synthetic-memory",
                "status": "verified",
                "confidence": "0.5",
            }
        )
