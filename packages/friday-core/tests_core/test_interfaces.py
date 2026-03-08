# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""
Tests for storage adapter protocols and context engineering interface.

Tests cover:
- Protocol definitions are abstract
- Required method signatures
- Interface documentation

Ref: Batch 1 Specification, Section 1
"""

from abc import ABC

import pytest
from friday_core import (
    ContextEngineeringInterface,
    EpisodicStoreAdapter,
    GraphStoreAdapter,
    VectorStoreAdapter,
)


class TestEpisodicStoreAdapter:
    """Tests for EpisodicStoreAdapter protocol."""

    def test_is_abstract(self):
        """Test that EpisodicStoreAdapter is abstract."""
        assert issubclass(EpisodicStoreAdapter, ABC)

    def test_cannot_instantiate(self):
        """Test that EpisodicStoreAdapter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            EpisodicStoreAdapter()

    def test_defines_add_turn(self):
        """Test that add_turn method is defined."""
        assert hasattr(EpisodicStoreAdapter, "add_turn")

    def test_defines_get_turns(self):
        """Test that get_turns method is defined."""
        assert hasattr(EpisodicStoreAdapter, "get_turns")

    def test_defines_get_unconsolidated_turns(self):
        """Test that get_unconsolidated_turns method is defined."""
        assert hasattr(EpisodicStoreAdapter, "get_unconsolidated_turns")

    def test_defines_mark_consolidated(self):
        """Test that mark_consolidated method is defined."""
        assert hasattr(EpisodicStoreAdapter, "mark_consolidated")

    def test_defines_rewind_history(self):
        """Test that rewind_history method is defined."""
        assert hasattr(EpisodicStoreAdapter, "rewind_history")

    def test_concrete_implementation(self):
        """Test that a concrete implementation can be created."""

        class ConcreteEpisodicStore(EpisodicStoreAdapter):
            async def add_turn(self, session_id, turn):
                return True

            async def get_turns(self, session_id, limit=10, offset=0):
                return []

            async def get_unconsolidated_turns(self, session_id):
                return []

            async def mark_consolidated(self, turn_ids):
                return True

            async def mark_compacted(self, turn_ids):
                return True

            async def rewind_history(self, session_id, target_turn_id):
                return True

        store = ConcreteEpisodicStore()
        assert isinstance(store, EpisodicStoreAdapter)


class TestVectorStoreAdapter:
    """Tests for VectorStoreAdapter protocol."""

    def test_is_abstract(self):
        """Test that VectorStoreAdapter is abstract."""
        assert issubclass(VectorStoreAdapter, ABC)

    def test_cannot_instantiate(self):
        """Test that VectorStoreAdapter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            VectorStoreAdapter()

    def test_defines_add_documents(self):
        """Test that add_documents method is defined."""
        assert hasattr(VectorStoreAdapter, "add_documents")

    def test_defines_query(self):
        """Test that query method is defined."""
        assert hasattr(VectorStoreAdapter, "query")

    def test_defines_delete(self):
        """Test that delete method is defined."""
        assert hasattr(VectorStoreAdapter, "delete")

    def test_defines_delete_where(self):
        """Test that delete_where method is defined."""
        assert hasattr(VectorStoreAdapter, "delete_where")

    def test_concrete_implementation(self):
        """Test that a concrete implementation can be created."""

        class ConcreteVectorStore(VectorStoreAdapter):
            async def add_documents(self, texts, metadatas, ids):
                return True

            async def query(
                self, query_text, n_results=5, where=None, rerank=False, hybrid=False
            ):
                return []

            async def delete(self, ids):
                return True

            async def delete_where(self, where):
                return 0

        store = ConcreteVectorStore()
        assert isinstance(store, VectorStoreAdapter)


class TestGraphStoreAdapter:
    """Tests for GraphStoreAdapter protocol."""

    def test_is_abstract(self):
        """Test that GraphStoreAdapter is abstract."""
        assert issubclass(GraphStoreAdapter, ABC)

    def test_cannot_instantiate(self):
        """Test that GraphStoreAdapter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            GraphStoreAdapter()

    # CRUD Operations
    def test_defines_add_node(self):
        """Test that add_node method is defined."""
        assert hasattr(GraphStoreAdapter, "add_node")

    def test_defines_add_edge(self):
        """Test that add_edge method is defined."""
        assert hasattr(GraphStoreAdapter, "add_edge")

    def test_defines_remove_node(self):
        """Test that remove_node method is defined."""
        assert hasattr(GraphStoreAdapter, "remove_node")

    # Traversal Operations
    def test_defines_get_neighbors(self):
        """Test that get_neighbors method is defined."""
        assert hasattr(GraphStoreAdapter, "get_neighbors")

    def test_defines_find_path(self):
        """Test that find_path method is defined."""
        assert hasattr(GraphStoreAdapter, "find_path")

    # Maintenance Operations
    def test_defines_merge_nodes(self):
        """Test that merge_nodes method is defined."""
        assert hasattr(GraphStoreAdapter, "merge_nodes")

    def test_defines_fuzzy_search(self):
        """Test that fuzzy_search method is defined."""
        assert hasattr(GraphStoreAdapter, "fuzzy_search")

    def test_defines_rank_nodes(self):
        """Test that rank_nodes method is defined."""
        assert hasattr(GraphStoreAdapter, "rank_nodes")

    def test_concrete_implementation(self):
        """Test that a concrete implementation can be created."""

        class ConcreteGraphStore(GraphStoreAdapter):
            async def add_node(self, node):
                return True

            async def add_edge(self, edge):
                return True

            async def remove_node(self, node_id):
                return True

            async def get_neighbors(self, node_id, depth=1):
                return []

            async def find_path(self, start_id, end_id, max_depth=5):
                return []

            async def merge_nodes(self, primary_id, secondary_id):
                return True

            async def fuzzy_search(self, query, threshold=0.8):
                return []

            async def rank_nodes(self, algorithm="pagerank"):
                return []

        store = ConcreteGraphStore()
        assert isinstance(store, GraphStoreAdapter)


class TestContextEngineeringInterface:
    """Tests for ContextEngineeringInterface protocol."""

    def test_is_abstract(self):
        """Test that ContextEngineeringInterface is abstract."""
        assert issubclass(ContextEngineeringInterface, ABC)

    def test_cannot_instantiate(self):
        """Test that ContextEngineeringInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ContextEngineeringInterface()

    # Session Management
    def test_defines_initialize_session(self):
        """Test that initialize_session method is defined."""
        assert hasattr(ContextEngineeringInterface, "initialize_session")

    def test_defines_restore_checkpoint(self):
        """Test that restore_checkpoint method is defined."""
        assert hasattr(ContextEngineeringInterface, "restore_checkpoint")

    # Ingestion Cycle
    def test_defines_extract_context(self):
        """Test that extract_context method is defined."""
        assert hasattr(ContextEngineeringInterface, "extract_context")

    # Maintenance Cycle
    def test_defines_consolidate_memory(self):
        """Test that consolidate_memory method is defined."""
        assert hasattr(ContextEngineeringInterface, "consolidate_memory")

    # Retrieval Cycle
    def test_defines_assemble_context(self):
        """Test that assemble_context method is defined."""
        assert hasattr(ContextEngineeringInterface, "assemble_context")

    # Formatting Cycle
    def test_defines_format_prompt(self):
        """Test that format_prompt method is defined."""
        assert hasattr(ContextEngineeringInterface, "format_prompt")

    def test_concrete_implementation(self):
        """Test that a concrete implementation can be created."""

        class ConcreteContextEngine(ContextEngineeringInterface):
            async def initialize_session(self, session_id, user_id):
                return {"session_id": session_id, "user_id": user_id}

            async def restore_checkpoint(self, session_id, turn_id):
                return {"session_id": session_id}

            async def extract_context(self, interaction_turn, async_execution=True):
                pass

            async def consolidate_memory(self, session_id):
                return {"session_id": session_id}

            async def assemble_context(self, query, state, budget_limit):
                return {"query": query}

            async def format_prompt(self, system_prompt, payload):
                return [{"role": "system", "content": system_prompt}]

        engine = ConcreteContextEngine()
        assert isinstance(engine, ContextEngineeringInterface)


class TestInterfaceImports:
    """Tests for interface exports from friday_core package."""

    def test_episodic_adapter_importable(self):
        """Test EpisodicStoreAdapter can be imported from friday_core."""
        from friday_core import EpisodicStoreAdapter

        assert EpisodicStoreAdapter is not None

    def test_vector_adapter_importable(self):
        """Test VectorStoreAdapter can be imported from friday_core."""
        from friday_core import VectorStoreAdapter

        assert VectorStoreAdapter is not None

    def test_graph_adapter_importable(self):
        """Test GraphStoreAdapter can be imported from friday_core."""
        from friday_core import GraphStoreAdapter

        assert GraphStoreAdapter is not None

    def test_context_interface_importable(self):
        """Test ContextEngineeringInterface can be imported from friday_core."""
        from friday_core import ContextEngineeringInterface

        assert ContextEngineeringInterface is not None
