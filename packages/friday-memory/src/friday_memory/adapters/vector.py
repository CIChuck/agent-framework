"""
ChromaDB Vector Store Implementation.
Implements VectorStoreAdapter with injected EmbeddingModel.

Ref: Batch 1 Specification, Section 3.1
Updated: Batch 3 - Now uses injected EmbeddingModel protocol
"""

import asyncio
from typing import TYPE_CHECKING, Any, Protocol

import chromadb
from friday_core import TelemetryInterface, VectorStoreAdapter

if TYPE_CHECKING:
    from friday_core.interfaces import EmbeddingModel


class EmbeddingFunction(Protocol):
    """Protocol for embedding functions compatible with ChromaVectorStore."""

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple documents."""
        ...

    async def embed_query(self, text: str) -> list[float]:
        """Embed a single query."""
        ...


class ChromaVectorStore(VectorStoreAdapter):
    """
    ChromaDB-based implementation of VectorStoreAdapter.

    Uses an injected EmbeddingModel for embeddings, providing model-agnostic
    embedding support. Supports both persistent and ephemeral (in-memory) storage.

    Features:
    - Semantic search with metadata filtering
    - Injected EmbeddingModel for flexibility (LiteLLM, OpenAI, etc.)
    - Telemetry integration for observability

    Example:
        from friday_llm import LiteLLMEmbeddingService

        embeddings = LiteLLMEmbeddingService(model_name="text-embedding-3-small")
        store = ChromaVectorStore(
            collection_name="my_collection",
            embedding_function=embeddings,
        )
    """

    def __init__(
        self,
        collection_name: str,
        embedding_function: "EmbeddingFunction | EmbeddingModel",
        path: str | None = None,
        persist_directory: str | None = None,
        telemetry: TelemetryInterface | None = None,
    ) -> None:
        """
        Initialize the ChromaDB vector store.

        Args:
            collection_name: Namespace for this memory (e.g., 'friday_long_term')
            embedding_function: EmbeddingModel for generating embeddings
            path: Local path for persistence (alias for persist_directory)
            persist_directory: Local path for persistence. If None, uses ephemeral client.
            telemetry: Optional telemetry recorder for white-box testing
        """  # noqa: E501
        self._collection_name = collection_name
        self._embedding_function = embedding_function
        self._telemetry = telemetry

        # Thread safety: asyncio lock for write operations
        self._lock = asyncio.Lock()

        # Support both 'path' and 'persist_directory' for convenience
        storage_path = path or persist_directory

        # Initialize ChromaDB client
        if storage_path:
            self._client = chromadb.PersistentClient(path=storage_path)
        else:
            self._client = chromadb.EphemeralClient()

        # Get or create collection (without embedding function - we handle embeddings)
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def _emit_event(self, event_name: str, data: dict) -> None:
        """Emit telemetry event if recorder is configured."""
        if self._telemetry:
            self._telemetry.capture_event(event_name, data)

    async def _get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings using the injected embedding function.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        return await self._embedding_function.embed_documents(texts)

    async def add_documents(
        self,
        texts: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str],
    ) -> bool:
        """
        Embeds and stores documents.

        Thread-safe: Uses lock for ChromaDB write operations.

        Args:
            texts: List of text chunks to embed and store
            metadatas: List of metadata dicts (should include provenance)
            ids: List of unique document IDs

        Returns:
            True if successful
        """
        if not texts:
            return True

        # Generate embeddings via LiteLLM (outside lock - can be slow)
        span_id = None
        if self._telemetry:
            span_id = self._telemetry.start_span("vector_embed")

        try:
            embeddings = await self._get_embeddings(texts)
        finally:
            if span_id:
                self._telemetry.end_span(span_id)

        # Add to ChromaDB (under lock)
        async with self._lock:
            self._collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids,
            )

        self._emit_event(
            "vector_documents_added",
            {"count": len(texts), "collection": self._collection_name},
        )
        return True

    async def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: dict[str, Any] | None = None,
        rerank: bool = False,
        hybrid: bool = False,
        query_embedding: list[float] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Performs semantic retrieval.

        Args:
            query_text: The search query
            n_results: Maximum results to return
            where: Optional metadata filter
            rerank: If True, apply reranking (not yet implemented)
            hybrid: If True, combine semantic and keyword search (not yet implemented)
            query_embedding: Optional pre-computed query embedding. When provided,
                skips the internal embedding computation to avoid redundant API calls.

        Returns:
            List of result dicts with text, metadata, and similarity
        """
        span_id = None
        if self._telemetry:
            span_id = self._telemetry.start_span("vector_query")

        try:
            # Use pre-computed embedding if provided, otherwise compute it
            if query_embedding is None:
                query_embedding = (await self._get_embeddings([query_text]))[0]

            # Query ChromaDB
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=self._normalize_where(where),
                include=["documents", "metadatas", "distances"],
            )
        finally:
            if span_id:
                self._telemetry.end_span(span_id)

        # Format results
        formatted = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                # ChromaDB returns distances (lower = more similar for cosine)
                # Convert to similarity score
                distance = results["distances"][0][i] if results["distances"] else 0
                similarity = 1 - distance  # For cosine distance

                formatted.append(
                    {
                        "id": doc_id,
                        "text": results["documents"][0][i]
                        if results["documents"]
                        else "",
                        "metadata": results["metadatas"][0][i]
                        if results["metadatas"]
                        else {},
                        "similarity": similarity,
                        "distance": distance,
                    }
                )

        self._emit_event(
            "vector_query_completed",
            {
                "query_length": len(query_text),
                "results_count": len(formatted),
                "collection": self._collection_name,
            },
        )
        return formatted

    async def delete(self, ids: list[str]) -> bool:
        """
        Removes documents by ID.

        Thread-safe: Uses lock for ChromaDB write operations.

        Args:
            ids: List of document IDs to delete

        Returns:
            True if successful
        """
        if not ids:
            return True

        async with self._lock:
            self._collection.delete(ids=ids)

        self._emit_event(
            "vector_documents_deleted",
            {"count": len(ids), "collection": self._collection_name},
        )
        return True

    async def delete_where(self, where: dict[str, Any]) -> int:
        """
        Removes documents matching a metadata filter.

        Thread-safe: Uses lock for ChromaDB write operations.

        Args:
            where: Metadata filter (e.g., {'source_type': 'document'})

        Returns:
            Number of documents deleted
        """
        async with self._lock:
            # Get matching IDs first
            results = self._collection.get(
                where=self._normalize_where(where),
                include=[],
            )

            if not results["ids"]:
                return 0

            count = len(results["ids"])
            self._collection.delete(ids=results["ids"])

        self._emit_event(
            "vector_documents_deleted_where",
            {"count": count, "filter": where, "collection": self._collection_name},
        )
        return count

    # --- Utility Methods ---

    async def count(self) -> int:
        """Get the number of documents in the collection."""
        return self._collection.count()

    async def get_by_id(self, doc_id: str) -> dict[str, Any] | None:
        """Get a document by ID."""
        results = self._collection.get(
            ids=[doc_id],
            include=["documents", "metadatas"],
        )
        if not results["ids"]:
            return None

        return {
            "id": results["ids"][0],
            "text": results["documents"][0] if results["documents"] else "",
            "metadata": results["metadatas"][0] if results["metadatas"] else {},
        }

    @staticmethod
    def _normalize_where(where: dict[str, Any] | None) -> dict[str, Any] | None:
        """Normalize a where filter for ChromaDB compatibility.

        ChromaDB requires compound filters (multiple keys) to be wrapped
        in a ``$and`` operator. This method detects multi-key where dicts
        and rewrites them automatically.

        Args:
            where: Raw where-clause dict, possibly with multiple top-level keys.

        Returns:
            A ChromaDB-compatible where dict, or None if input is None/empty.
        """
        if not where:
            return where

        # Already uses a logical operator — pass through
        if any(k.startswith("$") for k in where):
            return where

        # Single key — ChromaDB handles this natively
        if len(where) <= 1:
            return where

        # Multiple keys — wrap in $and
        return {"$and": [{k: v} for k, v in where.items()]}

    async def get_all(
        self, limit: int | None = 100, where: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Get all documents from the collection.

        Args:
            limit: Maximum number of documents to return. Pass ``None`` to
                   fetch all matching documents (ChromaDB default behavior).
                   **Important:** ChromaDB's ``.get()`` returns documents in
                   arbitrary insertion order, so callers that need
                   recency-ordered results should fetch all and sort
                   externally.
            where: Optional metadata filter dict (e.g., {"type": "insight"}).
                   Compound filters with multiple keys are automatically
                   wrapped in ``$and`` for ChromaDB compatibility.

        Returns:
            List of documents with id, text, and metadata
        """
        get_kwargs: dict[str, Any] = {
            "where": self._normalize_where(where),
            "include": ["documents", "metadatas"],
        }
        if limit is not None:
            get_kwargs["limit"] = limit
        results = self._collection.get(**get_kwargs)

        documents = []
        for i, doc_id in enumerate(results["ids"]):
            documents.append(
                {
                    "id": doc_id,
                    "text": results["documents"][i] if results["documents"] else "",
                    "metadata": results["metadatas"][i] if results["metadatas"] else {},
                }
            )

        return documents

    async def clear(self) -> int:
        """
        Clear all documents from the collection.

        Thread-safe: Uses lock for ChromaDB write operations.

        Returns:
            Number of documents deleted
        """
        async with self._lock:
            # Get count before clearing
            count = self._collection.count()

            if count > 0:
                # Get all document IDs and delete them
                results = self._collection.get(limit=count)
                if results["ids"]:
                    self._collection.delete(ids=results["ids"])

        self._emit_event("vector_store_cleared", {"documents_deleted": count})
        return count

    async def update_metadata(
        self,
        doc_id: str,
        metadata_updates: dict[str, Any],
    ) -> bool:
        """
        Update metadata for an existing document.

        Used for lifecycle management (updating hit_count, decay_score, etc.)
        without re-embedding the document.

        Thread-safe: Uses lock for ChromaDB write operations.

        Args:
            doc_id: ID of the document to update
            metadata_updates: Dict of metadata fields to update

        Returns:
            True if successful, False if document not found
        """
        async with self._lock:
            # Get current document (under lock to ensure atomicity)
            results = self._collection.get(
                ids=[doc_id],
                include=["documents", "metadatas"],
            )
            if not results["ids"]:
                return False

            existing_metadata = results["metadatas"][0] if results["metadatas"] else {}

            # Merge updates with existing metadata
            updated_metadata = {**existing_metadata, **metadata_updates}

            # ChromaDB update
            self._collection.update(
                ids=[doc_id],
                metadatas=[updated_metadata],
            )

        self._emit_event(
            "vector_metadata_updated",
            {
                "doc_id": doc_id,
                "updated_fields": list(metadata_updates.keys()),
                "collection": self._collection_name,
            },
        )
        return True

    async def increment_hit_count(self, doc_id: str) -> int:
        """
        Increment the hit_count for a document.

        Convenience method for tracking access frequency in long-term memories.
        Thread-safe: Uses lock for atomic read-modify-write operation.

        Args:
            doc_id: ID of the document

        Returns:
            New hit_count value, or -1 if document not found
        """
        import datetime

        async with self._lock:
            # Get current document
            results = self._collection.get(
                ids=[doc_id],
                include=["documents", "metadatas"],
            )
            if not results["ids"]:
                return -1

            # Increment hit count atomically
            metadata = results["metadatas"][0] if results["metadatas"] else {}
            new_count = metadata.get("hit_count", 0) + 1
            metadata["hit_count"] = new_count
            metadata["last_accessed_at"] = datetime.datetime.now().isoformat()

            # Update document
            self._collection.update(
                ids=[doc_id],
                metadatas=[metadata],
            )

        return new_count

    async def get_sample(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get a sample of documents from the collection.

        Useful for computing statistics without loading all documents.

        Args:
            limit: Maximum number of documents to return

        Returns:
            List of documents with id, text, and metadata
        """
        return await self.get_all(limit=limit)
