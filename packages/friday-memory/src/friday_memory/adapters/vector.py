"""
ChromaDB Vector Store Implementation.
Implements VectorStoreAdapter with LiteLLM embeddings.

Ref: Batch 1 Specification, Section 3.1
"""

from typing import Any

import chromadb
import litellm

from friday_core import TelemetryInterface, VectorStoreAdapter


class ChromaVectorStore(VectorStoreAdapter):
    """
    ChromaDB-based implementation of VectorStoreAdapter.

    Uses LiteLLM for embeddings, providing model-agnostic embedding support.
    Supports both persistent and ephemeral (in-memory) storage.

    Features:
    - Semantic search with metadata filtering
    - LiteLLM-powered embeddings (OpenAI, Cohere, etc.)
    - Telemetry integration for observability
    """

    def __init__(
        self,
        collection_name: str,
        persist_directory: str | None = None,
        embedding_model: str = "text-embedding-3-small",
        telemetry: TelemetryInterface | None = None,
    ) -> None:
        """
        Initialize the ChromaDB vector store.

        Args:
            collection_name: Namespace for this memory (e.g., 'friday_long_term')
            persist_directory: Local path for persistence. If None, uses ephemeral client.
            embedding_model: LiteLLM embedding model name (default: text-embedding-3-small)
            telemetry: Optional telemetry recorder for white-box testing
        """
        self._collection_name = collection_name
        self._embedding_model = embedding_model
        self._telemetry = telemetry

        # Initialize ChromaDB client
        if persist_directory:
            self._client = chromadb.PersistentClient(path=persist_directory)
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
        Generate embeddings using LiteLLM.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        response = await litellm.aembedding(
            model=self._embedding_model,
            input=texts,
        )
        return [item["embedding"] for item in response.data]

    async def add_documents(
        self,
        texts: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str],
    ) -> bool:
        """
        Embeds and stores documents.

        Args:
            texts: List of text chunks to embed and store
            metadatas: List of metadata dicts (should include provenance)
            ids: List of unique document IDs

        Returns:
            True if successful
        """
        if not texts:
            return True

        # Generate embeddings via LiteLLM
        span_id = None
        if self._telemetry:
            span_id = self._telemetry.start_span("vector_embed")

        try:
            embeddings = await self._get_embeddings(texts)
        finally:
            if span_id:
                self._telemetry.end_span(span_id)

        # Add to ChromaDB
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
    ) -> list[dict[str, Any]]:
        """
        Performs semantic retrieval.

        Args:
            query_text: The search query
            n_results: Maximum results to return
            where: Optional metadata filter
            rerank: If True, apply reranking (not yet implemented)
            hybrid: If True, combine semantic and keyword search (not yet implemented)

        Returns:
            List of result dicts with text, metadata, and similarity
        """
        span_id = None
        if self._telemetry:
            span_id = self._telemetry.start_span("vector_query")

        try:
            # Get query embedding
            query_embedding = (await self._get_embeddings([query_text]))[0]

            # Query ChromaDB
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
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
                        "text": results["documents"][0][i] if results["documents"] else "",
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
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

        Args:
            ids: List of document IDs to delete

        Returns:
            True if successful
        """
        if not ids:
            return True

        self._collection.delete(ids=ids)

        self._emit_event(
            "vector_documents_deleted",
            {"count": len(ids), "collection": self._collection_name},
        )
        return True

    async def delete_where(self, where: dict[str, Any]) -> int:
        """
        Removes documents matching a metadata filter.

        Args:
            where: Metadata filter (e.g., {'source_type': 'document'})

        Returns:
            Number of documents deleted
        """
        # Get matching IDs first
        results = self._collection.get(
            where=where,
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
