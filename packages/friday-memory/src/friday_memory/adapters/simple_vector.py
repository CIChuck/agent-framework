"""
In-memory vector store for ephemeral and testing scenarios.
Implements VectorStoreAdapter with numpy-based cosine similarity search.

Ref: Phase 1 - Scalable Adapters Build Plan
"""

import asyncio
import uuid
from typing import Any, Protocol

import numpy as np

from friday_core.interfaces.memory import VectorStoreAdapter


class EmbeddingFunction(Protocol):
    """Protocol for embedding functions compatible with SimpleVectorStore."""

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple documents."""
        ...

    async def embed_query(self, text: str) -> list[float]:
        """Embed a single query."""
        ...


class VectorDocument:
    """Internal document representation for in-memory storage."""

    __slots__ = ("id", "text", "embedding", "metadata")

    def __init__(
        self,
        id: str,
        text: str,
        embedding: np.ndarray,
        metadata: dict[str, Any],
    ):
        self.id = id
        self.text = text
        self.embedding = embedding
        self.metadata = metadata


class SimpleVectorStore(VectorStoreAdapter):
    """
    In-memory vector store using numpy for similarity search.

    Features:
    - Cosine similarity search
    - Metadata filtering
    - Thread-safe with asyncio.Lock
    - No persistence (ephemeral by design)

    Use Cases:
    - Unit testing without ChromaDB
    - Ephemeral agent sessions
    - Resource-constrained deployments
    - Rapid prototyping

    Example:
        from friday_llm import LiteLLMEmbeddingService

        embeddings = LiteLLMEmbeddingService(model_name="text-embedding-3-small")
        store = SimpleVectorStore(embedding_function=embeddings)
        await store.add_documents(["Hello world"], [{"type": "greeting"}], ["doc1"])
        results = await store.query("Hi there")
    """

    def __init__(
        self,
        embedding_function: EmbeddingFunction,
    ) -> None:
        """
        Initialize in-memory vector store.

        Args:
            embedding_function: Model for generating embeddings (must implement
                embed_documents and embed_query methods)
        """
        self._embedding_function = embedding_function
        self._documents: dict[str, VectorDocument] = {}
        self._lock = asyncio.Lock()

    async def add_documents(
        self,
        texts: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str],
    ) -> bool:
        """
        Embeds and stores documents.

        Thread-safe: Uses lock for write operations.

        Args:
            texts: List of text chunks to embed and store
            metadatas: List of metadata dicts (should include provenance)
            ids: List of unique document IDs

        Returns:
            True if successful
        """
        if not texts:
            return True

        # Generate embeddings outside lock (can be slow/async)
        embeddings = await self._embedding_function.embed_documents(texts)

        # Store documents under lock
        async with self._lock:
            for text, embedding, metadata, doc_id in zip(
                texts, embeddings, metadatas, ids
            ):
                self._documents[doc_id] = VectorDocument(
                    id=doc_id,
                    text=text,
                    embedding=np.array(embedding, dtype=np.float32),
                    metadata=metadata,
                )

        return True

    async def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: dict[str, Any] | None = None,
        rerank: bool = False,
        hybrid: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Performs semantic retrieval on stored documents.

        Args:
            query_text: The search query
            n_results: Maximum results to return
            where: Optional metadata filter (e.g., {'source_type': 'document'})
            rerank: Ignored (no reranking in simple store)
            hybrid: Ignored (no hybrid search in simple store)

        Returns:
            List of result dicts containing text, metadata, and similarity scores
        """
        if not self._documents:
            return []

        # Generate query embedding
        query_embedding = await self._embedding_function.embed_query(query_text)
        query_vec = np.array(query_embedding, dtype=np.float32)

        # Calculate similarities (snapshot under lock)
        async with self._lock:
            candidates = list(self._documents.values())

        results = []
        for doc in candidates:
            # Apply metadata filter
            if where and not self._matches_filter(doc.metadata, where):
                continue

            # Cosine similarity
            similarity = self._cosine_similarity(query_vec, doc.embedding)

            results.append({
                "id": doc.id,
                "text": doc.text,
                "metadata": doc.metadata,
                "similarity": float(similarity),
                "distance": float(1 - similarity),
            })

        # Sort by similarity (descending) and limit
        results.sort(key=lambda r: r["similarity"], reverse=True)
        return results[:n_results]

    async def delete(self, ids: list[str]) -> bool:
        """
        Removes documents by ID.

        Thread-safe: Uses lock for write operations.

        Args:
            ids: List of document IDs to delete

        Returns:
            True if successful
        """
        if not ids:
            return True

        async with self._lock:
            for doc_id in ids:
                self._documents.pop(doc_id, None)

        return True

    async def delete_where(self, where: dict[str, Any]) -> int:
        """
        Removes documents matching a metadata filter.

        Thread-safe: Uses lock for write operations.

        Args:
            where: Metadata filter (e.g., {'source_type': 'document'})

        Returns:
            Number of documents deleted
        """
        async with self._lock:
            to_delete = [
                doc_id
                for doc_id, doc in self._documents.items()
                if self._matches_filter(doc.metadata, where)
            ]
            for doc_id in to_delete:
                del self._documents[doc_id]
            return len(to_delete)

    # --- Utility Methods (matching ChromaVectorStore API) ---

    async def count(self) -> int:
        """Get the number of documents in the store."""
        return len(self._documents)

    async def get_by_id(self, doc_id: str) -> dict[str, Any] | None:
        """Get a document by ID."""
        doc = self._documents.get(doc_id)
        if not doc:
            return None
        return {
            "id": doc.id,
            "text": doc.text,
            "metadata": doc.metadata,
        }

    async def get_all(
        self, limit: int = 100, where: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Get all documents from the store.

        Args:
            limit: Maximum number of documents to return
            where: Optional metadata filter dict

        Returns:
            List of documents with id, text, and metadata
        """
        async with self._lock:
            documents = []
            for doc in self._documents.values():
                if where and not self._matches_filter(doc.metadata, where):
                    continue
                documents.append({
                    "id": doc.id,
                    "text": doc.text,
                    "metadata": doc.metadata,
                })
                if len(documents) >= limit:
                    break
            return documents

    async def clear(self) -> int:
        """
        Clear all documents from the store.

        Returns:
            Number of documents deleted
        """
        async with self._lock:
            count = len(self._documents)
            self._documents.clear()
            return count

    async def update_metadata(
        self,
        doc_id: str,
        metadata_updates: dict[str, Any],
    ) -> bool:
        """
        Update metadata for an existing document.

        Args:
            doc_id: ID of the document to update
            metadata_updates: Dict of metadata fields to update

        Returns:
            True if successful, False if document not found
        """
        async with self._lock:
            doc = self._documents.get(doc_id)
            if not doc:
                return False
            doc.metadata.update(metadata_updates)
            return True

    async def increment_hit_count(self, doc_id: str) -> int:
        """
        Increment the hit_count for a document.

        Args:
            doc_id: ID of the document

        Returns:
            New hit_count value, or -1 if document not found
        """
        import datetime

        async with self._lock:
            doc = self._documents.get(doc_id)
            if not doc:
                return -1
            new_count = doc.metadata.get("hit_count", 0) + 1
            doc.metadata["hit_count"] = new_count
            doc.metadata["last_accessed_at"] = datetime.datetime.now().isoformat()
            return new_count

    async def get_sample(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get a sample of documents from the store."""
        return await self.get_all(limit=limit)

    # --- Private Helper Methods ---

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def _matches_filter(
        self,
        metadata: dict[str, Any],
        where: dict[str, Any],
    ) -> bool:
        """
        Check if metadata matches filter conditions.

        Supports:
        - Simple equality: {"key": "value"}
        - ChromaDB-style operators: {"key": {"$eq": "value"}, "num": {"$gt": 5}}

        Returns:
            True if metadata matches all filter conditions
        """
        for key, value in where.items():
            if key not in metadata:
                return False

            # Handle operator syntax
            if isinstance(value, dict):
                metadata_val = metadata[key]
                for op, op_val in value.items():
                    if op == "$eq" and metadata_val != op_val:
                        return False
                    elif op == "$ne" and metadata_val == op_val:
                        return False
                    elif op == "$gt" and not (metadata_val > op_val):
                        return False
                    elif op == "$gte" and not (metadata_val >= op_val):
                        return False
                    elif op == "$lt" and not (metadata_val < op_val):
                        return False
                    elif op == "$lte" and not (metadata_val <= op_val):
                        return False
                    elif op == "$in" and metadata_val not in op_val:
                        return False
                    elif op == "$nin" and metadata_val in op_val:
                        return False
            else:
                # Simple equality
                if metadata[key] != value:
                    return False

        return True
