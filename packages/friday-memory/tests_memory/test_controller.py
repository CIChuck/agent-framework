# mypy: ignore-errors
# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
# mypy: disallow-untyped-defs=False
"""
Tests for MemoryController.

Tests cover:
- Provenance enforcement (required for store operations)
- Consolidation bridge (fetch/mark unconsolidated events)
- Unified recall from multiple stores
- Identity merging

Note: Tests use mock EmbeddingModel protocol from conftest fixtures.
"""

import uuid
from datetime import datetime

import pytest
from friday_memory import (
    GraphEdge,
    GraphNode,
    InteractionTurn,
    MemoryController,
    ProvenanceMetadata,
)


def create_turn(
    user_msg: str = "Hello", session_id: str = "test_session"
) -> InteractionTurn:
    """Helper to create test turns."""
    return InteractionTurn(
        id=str(uuid.uuid4()),
        session_id=session_id,
        timestamp=datetime.now(),
        user_message=user_msg,
        assistant_message="Response",
        consolidated=False,
    )


class TestProvenanceEnforcement:
    """Tests for provenance validation on store operations."""

    @pytest.mark.asyncio
    async def test_store_fact_requires_provenance(
        self, memory_controller: MemoryController
    ) -> None:
        """Test that GraphNode requires provenance at creation time."""
        # Provenance is required by Pydantic model - cannot create node without it
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            GraphNode(
                id="node_1",
                type="test",
                label="Test Node",
                # provenance is missing - Pydantic will reject this
            )

    @pytest.mark.asyncio
    async def test_store_fact_with_provenance_succeeds(
        self, memory_controller: MemoryController, sample_provenance: ProvenanceMetadata
    ) -> None:
        """Test that store_fact succeeds with provenance."""
        node = GraphNode(
            id="node_1",
            type="test",
            label="Test Node",
            provenance=sample_provenance,
        )

        result = await memory_controller.store_fact(node)
        assert result is True

    @pytest.mark.asyncio
    async def test_store_fact_with_edge_requires_provenance(
        self, memory_controller: MemoryController, sample_provenance: ProvenanceMetadata
    ) -> None:
        """Test that GraphEdge requires provenance at creation time."""
        from pydantic import ValidationError

        # Edge provenance is required by Pydantic model
        with pytest.raises(ValidationError):
            GraphEdge(
                source_id="node_1",
                target_id="node_2",
                relation="related",
                # provenance is missing - Pydantic will reject this
            )

    @pytest.mark.asyncio
    async def test_store_insight_requires_metadata(
        self, memory_controller: MemoryController
    ) -> None:
        """Test that store_insight raises ValueError without provenance."""
        with pytest.raises(ValueError, match="Provenance metadata is required"):
            await memory_controller.store_insight("Test insight", provenance=None)

    @pytest.mark.asyncio
    async def test_store_insight_with_metadata_succeeds(
        self, memory_controller: MemoryController, sample_provenance: ProvenanceMetadata
    ) -> None:
        """Test that store_insight succeeds with provenance."""
        result = await memory_controller.store_insight(
            "Test insight about Python",
            provenance=sample_provenance,
        )
        assert result is True


class TestConsolidationBridge:
    """Tests for consolidation proxy methods."""

    @pytest.mark.asyncio
    async def test_fetch_unconsolidated_events(
        self, memory_controller: MemoryController
    ) -> None:
        """Test fetching unconsolidated turns."""
        # Add some turns
        session_id = "test_session"
        for i in range(5):
            turn = create_turn(f"Message {i}")
            await memory_controller.add_turn(session_id, turn)

        # Fetch unconsolidated
        turns = await memory_controller.fetch_unconsolidated_events(session_id)
        assert len(turns) == 5

    @pytest.mark.asyncio
    async def test_mark_events_consolidated(self, memory_controller: MemoryController) -> None:
        """Test marking turns as consolidated."""
        session_id = "test_session"
        turn_ids = []
        for i in range(5):
            turn = create_turn(f"Message {i}")
            await memory_controller.add_turn(session_id, turn)
            turn_ids.append(turn.id)

        # Mark first 3 as consolidated
        result = await memory_controller.mark_events_consolidated(turn_ids[:3])
        assert result is True

        # Should only have 2 unconsolidated
        unconsolidated = await memory_controller.fetch_unconsolidated_events(session_id)
        assert len(unconsolidated) == 2

    @pytest.mark.asyncio
    async def test_consolidation_round_trip(self, memory_controller: MemoryController) -> None:
        """Test full consolidation workflow."""
        session_id = "consolidation_test"

        # Add turns
        turn_ids = []
        for i in range(5):
            turn = create_turn(f"Message {i}")
            await memory_controller.add_turn(session_id, turn)
            turn_ids.append(turn.id)

        # Initial: all unconsolidated
        unconsolidated = await memory_controller.fetch_unconsolidated_events(session_id)
        assert len(unconsolidated) == 5

        # Mark all as consolidated
        await memory_controller.mark_events_consolidated(turn_ids)

        # Final: none unconsolidated
        unconsolidated = await memory_controller.fetch_unconsolidated_events(session_id)
        assert len(unconsolidated) == 0


class TestUnifiedRecall:
    """Tests for recall() orchestration."""

    @pytest.mark.asyncio
    async def test_recall_returns_context_payload(
        self, memory_controller: MemoryController
    ) -> None:
        """Test that recall returns a ContextPayload."""
        payload = await memory_controller.recall(
            query="test query",
            session_id="test_session",
            include_history=False,
        )

        assert payload is not None
        assert hasattr(payload, "history")
        assert hasattr(payload, "passages")
        assert hasattr(payload, "entities")
        assert hasattr(payload, "facts")
        assert hasattr(payload, "debug_info")

    @pytest.mark.asyncio
    async def test_recall_includes_history(self, memory_controller: MemoryController) -> None:
        """Test that recall includes episodic history."""
        session_id = "history_test"

        # Add turns
        for i in range(3):
            await memory_controller.add_turn(session_id, create_turn(f"Msg {i}"))

        # Recall with history
        payload = await memory_controller.recall(
            query="test",
            session_id=session_id,
            include_history=True,
            history_limit=10,
        )

        assert len(payload.history) == 3

    @pytest.mark.asyncio
    async def test_recall_without_history(self, memory_controller: MemoryController) -> None:
        """Test recall without history."""
        session_id = "no_history_test"

        # Add turns
        for i in range(3):
            await memory_controller.add_turn(session_id, create_turn(f"Msg {i}"))

        # Recall without history
        payload = await memory_controller.recall(
            query="test",
            session_id=session_id,
            include_history=False,
        )

        assert len(payload.history) == 0

    @pytest.mark.asyncio
    async def test_recall_debug_info(self, memory_controller: MemoryController) -> None:
        """Test that recall populates debug info."""
        payload = await memory_controller.recall(
            query="test query for debugging",
            session_id="debug_test",
            include_history=False,
        )

        assert "query_length" in payload.debug_info
        assert "total_latency" in payload.debug_info

    @pytest.mark.asyncio
    async def test_recall_minimal_mode_skips_query_embedding(
        self, memory_controller: MemoryController
    ) -> None:
        """Minimal recall should not require semantic embedding."""
        embedding_model = memory_controller._collection_manager._embedding_function

        payload = await memory_controller.recall(
            query="minimal query",
            session_id="minimal_test",
            include_history=False,
            semantic_retrieval=False,
        )

        embedding_model.embed_query.assert_not_called()
        assert payload.passages == []
        assert payload.entities == []
        assert payload.facts == []
        assert payload.debug_info["semantic_retrieval"] is False


class TestIdentityMerging:
    """Tests for merge_identities."""

    @pytest.mark.asyncio
    async def test_merge_identities(
        self, memory_controller: MemoryController, sample_provenance: ProvenanceMetadata
    ) -> None:
        """Test merging two nodes."""
        # Create two nodes
        bob = GraphNode(
            id="bob_id",
            type="person",
            label="Bob",
            provenance=sample_provenance,
        )
        robert = GraphNode(
            id="robert_id",
            type="person",
            label="Robert",
            provenance=sample_provenance,
        )

        await memory_controller.store_fact(bob)
        await memory_controller.store_fact(robert)

        # Merge
        result = await memory_controller.merge_identities("bob_id", "robert_id")
        assert result is True

        # Robert should be gone
        robert_node = await memory_controller.graph.get_node("robert_id")
        assert robert_node is None

        # Bob should still exist
        bob_node = await memory_controller.graph.get_node("bob_id")
        assert bob_node is not None


class TestSessionManagement:
    """Tests for session-related operations."""

    @pytest.mark.asyncio
    async def test_add_turn(self, memory_controller: MemoryController) -> None:
        """Test adding a turn via controller."""
        turn = create_turn("Hello from controller")
        result = await memory_controller.add_turn("session_1", turn)

        assert result is True

    @pytest.mark.asyncio
    async def test_rewind_session(self, memory_controller: MemoryController) -> None:
        """Test rewinding session history."""
        session_id = "rewind_test"
        turn_ids = []

        # Add turns
        for i in range(5):
            turn = create_turn(f"Message {i}")
            await memory_controller.add_turn(session_id, turn)
            turn_ids.append(turn.id)

        # Rewind to turn 2
        result = await memory_controller.rewind_session(session_id, turn_ids[2])
        assert result is True


class TestTelemetryIntegration:
    """Tests for telemetry event emission."""

    @pytest.mark.asyncio
    async def test_store_fact_emits_event(
        self, memory_controller: MemoryController, sample_provenance: ProvenanceMetadata
    ) -> None:
        """Test that store_fact emits telemetry."""
        node = GraphNode(
            id="telemetry_test",
            type="test",
            label="Test",
            provenance=sample_provenance,
        )

        await memory_controller.store_fact(node)

        # Check telemetry was captured
        telemetry = memory_controller._telemetry
        event = telemetry.get_event("fact_stored")
        assert event is not None
        assert event["node_id"] == "telemetry_test"

    @pytest.mark.asyncio
    async def test_recall_emits_event(self, memory_controller: MemoryController) -> None:
        """Test that recall emits telemetry."""
        await memory_controller.recall(
            query="telemetry test",
            include_history=False,
        )

        telemetry = memory_controller._telemetry
        event = telemetry.get_event("memory_recall_completed")
        assert event is not None
