"""
Tests for ChromaVectorStore adapter.

Tests cover:
- Adding and querying documents
- Metadata filtering
- Document deletion
- Similarity scoring
- Where-clause normalization for ChromaDB compatibility

Note: Tests use mock EmbeddingModel protocol from conftest fixtures.
"""

import uuid

import pytest

from friday_memory import ChromaVectorStore


class TestNormalizeWhere:
    """Tests for ChromaVectorStore._normalize_where static method."""

    def test_none_passthrough(self):
        """Test that None is passed through."""
        assert ChromaVectorStore._normalize_where(None) is None

    def test_empty_dict_passthrough(self):
        """Test that empty dict is passed through."""
        assert ChromaVectorStore._normalize_where({}) == {}

    def test_single_key_passthrough(self):
        """Test that single-key where is passed through."""
        where = {"type": "insight"}
        result = ChromaVectorStore._normalize_where(where)
        assert result == {"type": "insight"}

    def test_compound_wrapped_in_and(self):
        """Test that multi-key where is wrapped in $and."""
        where = {"type": "insight", "created_at": {"$gte": "2026-01-01"}}
        result = ChromaVectorStore._normalize_where(where)
        assert "$and" in result
        assert len(result["$and"]) == 2
        assert {"type": "insight"} in result["$and"]
        assert {"created_at": {"$gte": "2026-01-01"}} in result["$and"]

    def test_existing_logical_operator_passthrough(self):
        """Test that where already using $and/$or is passed through."""
        where = {"$and": [{"type": "insight"}, {"stage": "short_term"}]}
        result = ChromaVectorStore._normalize_where(where)
        assert result is where  # Same object, no transformation

    def test_three_keys_wrapped(self):
        """Test that three top-level keys are wrapped correctly."""
        where = {"type": "insight", "stage": "short_term", "author": "system"}
        result = ChromaVectorStore._normalize_where(where)
        assert "$and" in result
        assert len(result["$and"]) == 3


class TestChromaVectorStore:
    """Tests for ChromaVectorStore."""

    @pytest.mark.asyncio
    async def test_add_documents(self, vector_store: ChromaVectorStore):
        """Test adding documents to the store."""
        result = await vector_store.add_documents(
            texts=["Hello world", "Goodbye world"],
            metadatas=[{"source": "test1"}, {"source": "test2"}],
            ids=["doc_1", "doc_2"],
        )

        assert result is True
        count = await vector_store.count()
        assert count == 2

    @pytest.mark.asyncio
    async def test_add_empty_documents(self, vector_store: ChromaVectorStore):
        """Test adding empty document list."""
        result = await vector_store.add_documents(
            texts=[],
            metadatas=[],
            ids=[],
        )

        assert result is True
        count = await vector_store.count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_query_documents(self, vector_store: ChromaVectorStore):
        """Test querying documents."""
        # Add documents
        await vector_store.add_documents(
            texts=["Python programming", "Java development", "Machine learning"],
            metadatas=[
                {"topic": "programming"},
                {"topic": "programming"},
                {"topic": "ai"},
            ],
            ids=["doc_1", "doc_2", "doc_3"],
        )

        # Query
        results = await vector_store.query("programming", n_results=2)

        assert len(results) <= 2
        assert all("id" in r for r in results)
        assert all("text" in r for r in results)
        assert all("similarity" in r for r in results)

    @pytest.mark.asyncio
    async def test_query_with_metadata_filter(self, vector_store: ChromaVectorStore):
        """Test querying with metadata filter."""
        await vector_store.add_documents(
            texts=["Python code", "Java code", "Python tutorial"],
            metadatas=[
                {"language": "python"},
                {"language": "java"},
                {"language": "python"},
            ],
            ids=["doc_1", "doc_2", "doc_3"],
        )

        # Query with filter
        results = await vector_store.query(
            "code",
            n_results=10,
            where={"language": "python"},
        )

        # Should only return python documents
        for result in results:
            assert result["metadata"]["language"] == "python"

    @pytest.mark.asyncio
    async def test_delete_by_ids(self, vector_store: ChromaVectorStore):
        """Test deleting documents by ID."""
        await vector_store.add_documents(
            texts=["Doc 1", "Doc 2", "Doc 3"],
            metadatas=[{"type": "doc"}, {"type": "doc"}, {"type": "doc"}],
            ids=["doc_1", "doc_2", "doc_3"],
        )

        # Delete some
        result = await vector_store.delete(["doc_1", "doc_2"])
        assert result is True

        count = await vector_store.count()
        assert count == 1

    @pytest.mark.asyncio
    async def test_delete_empty_list(self, vector_store: ChromaVectorStore):
        """Test deleting with empty list."""
        result = await vector_store.delete([])
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_where(self, vector_store: ChromaVectorStore):
        """Test deleting documents by metadata filter."""
        await vector_store.add_documents(
            texts=["Old doc 1", "Old doc 2", "New doc"],
            metadatas=[
                {"status": "archived"},
                {"status": "archived"},
                {"status": "active"},
            ],
            ids=["doc_1", "doc_2", "doc_3"],
        )

        # Delete archived documents
        deleted_count = await vector_store.delete_where({"status": "archived"})
        assert deleted_count == 2

        count = await vector_store.count()
        assert count == 1

    @pytest.mark.asyncio
    async def test_get_by_id(self, vector_store: ChromaVectorStore):
        """Test getting a document by ID."""
        await vector_store.add_documents(
            texts=["Test document"],
            metadatas=[{"key": "value"}],
            ids=["doc_1"],
        )

        doc = await vector_store.get_by_id("doc_1")

        assert doc is not None
        assert doc["id"] == "doc_1"
        assert doc["text"] == "Test document"
        assert doc["metadata"]["key"] == "value"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, vector_store: ChromaVectorStore):
        """Test getting non-existent document."""
        doc = await vector_store.get_by_id("nonexistent")
        assert doc is None

    @pytest.mark.asyncio
    async def test_similarity_scores(self, vector_store: ChromaVectorStore):
        """Test that similarity scores are returned."""
        await vector_store.add_documents(
            texts=["Document about cats", "Document about dogs"],
            metadatas=[{"topic": "cats"}, {"topic": "dogs"}],
            ids=["doc_1", "doc_2"],
        )

        results = await vector_store.query("cats", n_results=2)

        for result in results:
            # Similarity should be between 0 and 1 (converted from distance)
            assert "similarity" in result
            assert "distance" in result

    @pytest.mark.asyncio
    async def test_unique_collection_names(self, mock_embedding_model):
        """Test that different collection names are isolated."""
        store1 = ChromaVectorStore(
            collection_name=f"collection_{uuid.uuid4().hex[:8]}",
            embedding_function=mock_embedding_model,
        )
        store2 = ChromaVectorStore(
            collection_name=f"collection_{uuid.uuid4().hex[:8]}",
            embedding_function=mock_embedding_model,
        )

        await store1.add_documents(
            texts=["Store 1 doc"],
            metadatas=[{"source": "store1"}],
            ids=["doc_1"],
        )

        # Store 2 should be empty
        count = await store2.count()
        assert count == 0
