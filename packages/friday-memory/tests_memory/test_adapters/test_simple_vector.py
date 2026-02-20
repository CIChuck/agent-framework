"""
Tests for SimpleVectorStore adapter.

Tests cover:
- Adding and querying documents
- Metadata filtering (simple and operator-based)
- Document deletion
- Similarity scoring
- Utility methods (count, get_by_id, clear, etc.)

Note: Tests use mock EmbeddingModel protocol from conftest fixtures.
"""

import pytest
from friday_memory.adapters.simple_vector import SimpleVectorStore


class TestSimpleVectorStore:
    """Tests for SimpleVectorStore."""

    @pytest.fixture
    def simple_vector_store(self, mock_embedding_model) -> SimpleVectorStore:
        """Create an in-memory SimpleVectorStore with mock embedding model."""
        return SimpleVectorStore(embedding_function=mock_embedding_model)

    @pytest.mark.asyncio
    async def test_add_documents(self, simple_vector_store: SimpleVectorStore):
        """Test adding documents to the store."""
        result = await simple_vector_store.add_documents(
            texts=["Hello world", "Goodbye world"],
            metadatas=[{"source": "test1"}, {"source": "test2"}],
            ids=["doc_1", "doc_2"],
        )

        assert result is True
        count = await simple_vector_store.count()
        assert count == 2

    @pytest.mark.asyncio
    async def test_add_empty_documents(self, simple_vector_store: SimpleVectorStore):
        """Test adding empty document list."""
        result = await simple_vector_store.add_documents(
            texts=[],
            metadatas=[],
            ids=[],
        )

        assert result is True
        count = await simple_vector_store.count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_query_documents(self, simple_vector_store: SimpleVectorStore):
        """Test querying documents."""
        # Add documents
        await simple_vector_store.add_documents(
            texts=["Python programming", "Java development", "Machine learning"],
            metadatas=[
                {"topic": "programming"},
                {"topic": "programming"},
                {"topic": "ai"},
            ],
            ids=["doc_1", "doc_2", "doc_3"],
        )

        # Query
        results = await simple_vector_store.query("programming", n_results=2)

        assert len(results) <= 2
        assert all("id" in r for r in results)
        assert all("text" in r for r in results)
        assert all("similarity" in r for r in results)

    @pytest.mark.asyncio
    async def test_query_empty_store(self, simple_vector_store: SimpleVectorStore):
        """Test querying empty store returns empty list."""
        results = await simple_vector_store.query("anything")
        assert results == []

    @pytest.mark.asyncio
    async def test_query_with_metadata_filter(
        self, simple_vector_store: SimpleVectorStore
    ):
        """Test querying with simple metadata filter."""
        await simple_vector_store.add_documents(
            texts=["Python code", "Java code", "Python tutorial"],
            metadatas=[
                {"language": "python"},
                {"language": "java"},
                {"language": "python"},
            ],
            ids=["doc_1", "doc_2", "doc_3"],
        )

        # Query with filter
        results = await simple_vector_store.query(
            "code",
            n_results=10,
            where={"language": "python"},
        )

        # Should only return python documents
        assert len(results) == 2
        for result in results:
            assert result["metadata"]["language"] == "python"

    @pytest.mark.asyncio
    async def test_query_with_operator_filter(
        self, simple_vector_store: SimpleVectorStore
    ):
        """Test querying with operator-based metadata filter."""
        await simple_vector_store.add_documents(
            texts=["Doc 1", "Doc 2", "Doc 3"],
            metadatas=[
                {"priority": 1},
                {"priority": 5},
                {"priority": 10},
            ],
            ids=["doc_1", "doc_2", "doc_3"],
        )

        # Query with $gt filter
        results = await simple_vector_store.query(
            "doc",
            n_results=10,
            where={"priority": {"$gt": 3}},
        )

        # Should return docs with priority > 3
        assert len(results) == 2
        for result in results:
            assert result["metadata"]["priority"] > 3

    @pytest.mark.asyncio
    async def test_query_with_in_operator(self, simple_vector_store: SimpleVectorStore):
        """Test querying with $in operator."""
        await simple_vector_store.add_documents(
            texts=["Doc A", "Doc B", "Doc C"],
            metadatas=[
                {"status": "active"},
                {"status": "pending"},
                {"status": "archived"},
            ],
            ids=["doc_1", "doc_2", "doc_3"],
        )

        # Query with $in filter
        results = await simple_vector_store.query(
            "doc",
            n_results=10,
            where={"status": {"$in": ["active", "pending"]}},
        )

        assert len(results) == 2
        for result in results:
            assert result["metadata"]["status"] in ["active", "pending"]

    @pytest.mark.asyncio
    async def test_delete_by_ids(self, simple_vector_store: SimpleVectorStore):
        """Test deleting documents by ID."""
        await simple_vector_store.add_documents(
            texts=["Doc 1", "Doc 2", "Doc 3"],
            metadatas=[{"type": "doc"}, {"type": "doc"}, {"type": "doc"}],
            ids=["doc_1", "doc_2", "doc_3"],
        )

        # Delete some
        result = await simple_vector_store.delete(["doc_1", "doc_2"])
        assert result is True

        count = await simple_vector_store.count()
        assert count == 1

    @pytest.mark.asyncio
    async def test_delete_empty_list(self, simple_vector_store: SimpleVectorStore):
        """Test deleting with empty list."""
        result = await simple_vector_store.delete([])
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_where(self, simple_vector_store: SimpleVectorStore):
        """Test deleting documents by metadata filter."""
        await simple_vector_store.add_documents(
            texts=["Old doc 1", "Old doc 2", "New doc"],
            metadatas=[
                {"status": "archived"},
                {"status": "archived"},
                {"status": "active"},
            ],
            ids=["doc_1", "doc_2", "doc_3"],
        )

        # Delete archived documents
        deleted_count = await simple_vector_store.delete_where({"status": "archived"})
        assert deleted_count == 2

        count = await simple_vector_store.count()
        assert count == 1

    @pytest.mark.asyncio
    async def test_get_by_id(self, simple_vector_store: SimpleVectorStore):
        """Test getting a document by ID."""
        await simple_vector_store.add_documents(
            texts=["Test document"],
            metadatas=[{"key": "value"}],
            ids=["doc_1"],
        )

        doc = await simple_vector_store.get_by_id("doc_1")

        assert doc is not None
        assert doc["id"] == "doc_1"
        assert doc["text"] == "Test document"
        assert doc["metadata"]["key"] == "value"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, simple_vector_store: SimpleVectorStore):
        """Test getting non-existent document."""
        doc = await simple_vector_store.get_by_id("nonexistent")
        assert doc is None

    @pytest.mark.asyncio
    async def test_similarity_scores(self, simple_vector_store: SimpleVectorStore):
        """Test that similarity scores are returned."""
        await simple_vector_store.add_documents(
            texts=["Document about cats", "Document about dogs"],
            metadatas=[{"topic": "cats"}, {"topic": "dogs"}],
            ids=["doc_1", "doc_2"],
        )

        results = await simple_vector_store.query("cats", n_results=2)

        for result in results:
            # Similarity should be between 0 and 1
            assert "similarity" in result
            assert "distance" in result
            assert 0 <= result["similarity"] <= 1
            assert 0 <= result["distance"] <= 2  # Distance can be up to 2 for cosine

    @pytest.mark.asyncio
    async def test_clear(self, simple_vector_store: SimpleVectorStore):
        """Test clearing all documents."""
        await simple_vector_store.add_documents(
            texts=["Doc 1", "Doc 2", "Doc 3"],
            metadatas=[{}, {}, {}],
            ids=["doc_1", "doc_2", "doc_3"],
        )

        count_before = await simple_vector_store.count()
        assert count_before == 3

        deleted_count = await simple_vector_store.clear()
        assert deleted_count == 3

        count_after = await simple_vector_store.count()
        assert count_after == 0

    @pytest.mark.asyncio
    async def test_get_all(self, simple_vector_store: SimpleVectorStore):
        """Test getting all documents."""
        await simple_vector_store.add_documents(
            texts=["Doc 1", "Doc 2", "Doc 3"],
            metadatas=[{"type": "a"}, {"type": "b"}, {"type": "a"}],
            ids=["doc_1", "doc_2", "doc_3"],
        )

        # Get all
        docs = await simple_vector_store.get_all()
        assert len(docs) == 3

        # Get with filter
        docs = await simple_vector_store.get_all(where={"type": "a"})
        assert len(docs) == 2

        # Get with limit
        docs = await simple_vector_store.get_all(limit=2)
        assert len(docs) == 2

    @pytest.mark.asyncio
    async def test_update_metadata(self, simple_vector_store: SimpleVectorStore):
        """Test updating document metadata."""
        await simple_vector_store.add_documents(
            texts=["Test document"],
            metadatas=[{"version": 1}],
            ids=["doc_1"],
        )

        # Update metadata
        result = await simple_vector_store.update_metadata(
            "doc_1", {"version": 2, "updated": True}
        )
        assert result is True

        doc = await simple_vector_store.get_by_id("doc_1")
        assert doc["metadata"]["version"] == 2
        assert doc["metadata"]["updated"] is True

    @pytest.mark.asyncio
    async def test_update_metadata_not_found(
        self, simple_vector_store: SimpleVectorStore
    ):
        """Test updating metadata for non-existent document."""
        result = await simple_vector_store.update_metadata(
            "nonexistent", {"key": "value"}
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_increment_hit_count(self, simple_vector_store: SimpleVectorStore):
        """Test incrementing hit count."""
        await simple_vector_store.add_documents(
            texts=["Test document"],
            metadatas=[{}],
            ids=["doc_1"],
        )

        # Increment hit count
        count = await simple_vector_store.increment_hit_count("doc_1")
        assert count == 1

        count = await simple_vector_store.increment_hit_count("doc_1")
        assert count == 2

        # Verify metadata
        doc = await simple_vector_store.get_by_id("doc_1")
        assert doc["metadata"]["hit_count"] == 2
        assert "last_accessed_at" in doc["metadata"]

    @pytest.mark.asyncio
    async def test_increment_hit_count_not_found(
        self, simple_vector_store: SimpleVectorStore
    ):
        """Test incrementing hit count for non-existent document."""
        result = await simple_vector_store.increment_hit_count("nonexistent")
        assert result == -1


class TestSimpleVectorStoreFiltering:
    """Tests for metadata filtering operators."""

    @pytest.fixture
    def simple_vector_store(self, mock_embedding_model) -> SimpleVectorStore:
        """Create an in-memory SimpleVectorStore with mock embedding model."""
        return SimpleVectorStore(embedding_function=mock_embedding_model)

    @pytest.mark.asyncio
    async def test_filter_eq(self, simple_vector_store: SimpleVectorStore):
        """Test $eq operator."""
        await simple_vector_store.add_documents(
            texts=["A", "B"],
            metadatas=[{"val": 1}, {"val": 2}],
            ids=["a", "b"],
        )

        results = await simple_vector_store.query("", where={"val": {"$eq": 1}})
        assert len(results) == 1
        assert results[0]["id"] == "a"

    @pytest.mark.asyncio
    async def test_filter_ne(self, simple_vector_store: SimpleVectorStore):
        """Test $ne operator."""
        await simple_vector_store.add_documents(
            texts=["A", "B"],
            metadatas=[{"val": 1}, {"val": 2}],
            ids=["a", "b"],
        )

        results = await simple_vector_store.query("", where={"val": {"$ne": 1}})
        assert len(results) == 1
        assert results[0]["id"] == "b"

    @pytest.mark.asyncio
    async def test_filter_gte_lte(self, simple_vector_store: SimpleVectorStore):
        """Test $gte and $lte operators."""
        await simple_vector_store.add_documents(
            texts=["A", "B", "C"],
            metadatas=[{"val": 1}, {"val": 5}, {"val": 10}],
            ids=["a", "b", "c"],
        )

        results = await simple_vector_store.query(
            "", where={"val": {"$gte": 5, "$lte": 10}}
        )
        assert len(results) == 2
        ids = {r["id"] for r in results}
        assert ids == {"b", "c"}

    @pytest.mark.asyncio
    async def test_filter_nin(self, simple_vector_store: SimpleVectorStore):
        """Test $nin (not in) operator."""
        await simple_vector_store.add_documents(
            texts=["A", "B", "C"],
            metadatas=[{"status": "a"}, {"status": "b"}, {"status": "c"}],
            ids=["a", "b", "c"],
        )

        results = await simple_vector_store.query(
            "", where={"status": {"$nin": ["a", "b"]}}
        )
        assert len(results) == 1
        assert results[0]["id"] == "c"
