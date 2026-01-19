"""
Multi-Collection Manager for Staged Memory Retrieval.

Manages three separate ChromaDB collections for different memory stages:
- short_term: Recent consolidated insights (lower similarity threshold)
- long_term: Proven, frequently-accessed memories (higher threshold + inclusion scoring)
- decayed: Low-value memories pending cleanup (not queried by default)

Ref: docs/build-plan/memory-lifecycle-staging-decay.md, Section "Storage Architecture Decision"
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from friday_memory.adapters.vector import ChromaVectorStore
from friday_memory.lifecycle.stages import MemoryStage, PromotionState
from friday_memory.models.vector_metadata import create_longterm_metadata

if TYPE_CHECKING:
    from friday_core import TelemetryInterface
    from friday_core.interfaces import EmbeddingModel

    from friday_memory.adapters.graph import GraphStoreAdapter

logger = logging.getLogger(__name__)


class CollectionConfig(BaseModel):
    """Configuration for multi-collection memory architecture."""

    # Collection names
    short_term_collection: str = Field(
        default="memories_short_term",
        description="Collection name for short-term memories",
    )
    long_term_collection: str = Field(
        default="memories_long_term",
        description="Collection name for long-term memories",
    )
    decayed_collection: str = Field(
        default="memories_decayed",
        description="Collection name for decayed memories",
    )

    # Similarity thresholds
    short_term_min_similarity: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum similarity for short-term retrieval",
    )
    long_term_min_similarity: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum similarity for long-term retrieval",
    )

    # Default results per collection
    default_n_results: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Default number of results per collection",
    )


class CollectionManager:
    """
    Manages multiple ChromaDB collections for staged memory retrieval.

    Provides:
    - Parallel queries to short-term and long-term collections
    - Atomic promotion with crash recovery support
    - Demotion to decayed collection
    - Recovery for incomplete promotions

    Example:
        config = CollectionConfig()
        manager = CollectionManager(
            embedding_function=embeddings,
            config=config,
            path="/data/memories",
        )

        # Query all active collections
        results = await manager.query("How do I configure logging?")

        # Promote a memory
        await manager.promote_memory(memory_id)
    """

    def __init__(
        self,
        embedding_function: "EmbeddingModel",
        config: CollectionConfig | None = None,
        path: str | None = None,
        telemetry: "TelemetryInterface | None" = None,
    ) -> None:
        """
        Initialize the collection manager.

        Args:
            embedding_function: EmbeddingModel for generating embeddings
            config: Collection configuration (uses defaults if None)
            path: Persistence path for ChromaDB
            telemetry: Optional telemetry interface
        """
        self._config = config or CollectionConfig()
        self._telemetry = telemetry
        self._embedding_function = embedding_function

        # Initialize the three collections
        self._short_term = ChromaVectorStore(
            collection_name=self._config.short_term_collection,
            embedding_function=embedding_function,
            path=path,
            telemetry=telemetry,
        )
        self._long_term = ChromaVectorStore(
            collection_name=self._config.long_term_collection,
            embedding_function=embedding_function,
            path=path,
            telemetry=telemetry,
        )
        self._decayed = ChromaVectorStore(
            collection_name=self._config.decayed_collection,
            embedding_function=embedding_function,
            path=path,
            telemetry=telemetry,
        )

    @property
    def short_term(self) -> ChromaVectorStore:
        """Access to short-term collection."""
        return self._short_term

    @property
    def long_term(self) -> ChromaVectorStore:
        """Access to long-term collection."""
        return self._long_term

    @property
    def decayed(self) -> ChromaVectorStore:
        """Access to decayed collection."""
        return self._decayed

    def _emit_event(self, event_name: str, data: dict) -> None:
        """Emit telemetry event if recorder is configured."""
        if self._telemetry:
            self._telemetry.capture_event(event_name, data)

    async def query(
        self,
        query_text: str,
        n_results: int | None = None,
        include_decayed: bool = False,
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Query short-term and long-term collections in parallel.

        Args:
            query_text: The search query
            n_results: Max results per collection (uses config default if None)
            include_decayed: If True, also query decayed collection

        Returns:
            Dict with keys 'short_term', 'long_term', and optionally 'decayed',
            each containing list of results with similarity filtering applied.
        """
        n = n_results or self._config.default_n_results

        # Build query tasks
        tasks = [
            self._query_with_threshold(
                self._short_term,
                query_text,
                n,
                self._config.short_term_min_similarity,
            ),
            self._query_with_threshold(
                self._long_term,
                query_text,
                n,
                self._config.long_term_min_similarity,
            ),
        ]

        if include_decayed:
            tasks.append(
                self._query_with_threshold(
                    self._decayed,
                    query_text,
                    n,
                    0.0,  # No threshold for decayed
                )
            )

        # Execute in parallel
        results = await asyncio.gather(*tasks)

        output = {
            "short_term": results[0],
            "long_term": results[1],
        }

        if include_decayed:
            output["decayed"] = results[2]

        self._emit_event(
            "collection_manager_query",
            {
                "query_length": len(query_text),
                "short_term_results": len(results[0]),
                "long_term_results": len(results[1]),
                "include_decayed": include_decayed,
            },
        )

        return output

    async def _query_with_threshold(
        self,
        collection: ChromaVectorStore,
        query_text: str,
        n_results: int,
        min_similarity: float,
    ) -> list[dict[str, Any]]:
        """Query a collection and filter by minimum similarity threshold."""
        results = await collection.query(query_text, n_results=n_results)

        # Filter by similarity threshold
        return [r for r in results if r.get("similarity", 0) >= min_similarity]

    async def add_to_short_term(
        self,
        texts: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str],
    ) -> bool:
        """
        Add new memories to short-term collection.

        This is the entry point for newly consolidated memories.
        """
        # Ensure stage is set correctly
        for metadata in metadatas:
            metadata["stage"] = MemoryStage.SHORT_TERM.value
            metadata["promotion_state"] = PromotionState.NONE.value

        return await self._short_term.add_documents(texts, metadatas, ids)

    async def promote_memory(self, memory_id: str) -> bool:
        """
        Promote memory from short-term to long-term with crash recovery support.

        Uses PromotionState tracking to ensure promotion can be recovered
        if the process crashes mid-operation.

        Args:
            memory_id: ID of memory to promote

        Returns:
            True if promotion successful, False if memory not found
        """
        # Read from short-term
        memory = await self._short_term.get_by_id(memory_id)
        if not memory:
            return False

        text = memory.get("text", "")
        existing_metadata = memory.get("metadata", {})

        # Mark promotion as pending (for crash recovery)
        # Update metadata for long-term
        longterm_metadata = create_longterm_metadata(existing_metadata)
        longterm_metadata["promotion_state"] = PromotionState.PENDING.value

        # Get embedding by re-embedding the text (we don't have access to original)
        # This ensures consistency with the embedding function
        embeddings = await self._embedding_function.embed_documents([text])

        # Insert into long-term
        self._long_term._collection.add(
            ids=[memory_id],
            embeddings=embeddings,
            documents=[text],
            metadatas=[longterm_metadata],
        )

        # Delete from short-term
        await self._short_term.delete([memory_id])

        # Mark promotion complete
        await self._long_term.update_metadata(
            memory_id,
            {"promotion_state": PromotionState.COMPLETE.value},
        )

        self._emit_event(
            "memory_promoted",
            {"memory_id": memory_id, "from": "short_term", "to": "long_term"},
        )

        return True

    async def demote_to_decayed(self, memory_id: str) -> bool:
        """
        Demote a long-term memory to decayed collection.

        Args:
            memory_id: ID of memory to demote

        Returns:
            True if demotion successful, False if memory not found
        """
        # Try long-term first
        memory = await self._long_term.get_by_id(memory_id)
        source_collection = self._long_term

        if not memory:
            # Also check short-term (edge case)
            memory = await self._short_term.get_by_id(memory_id)
            source_collection = self._short_term

        if not memory:
            return False

        text = memory.get("text", "")
        metadata = memory.get("metadata", {})

        # Update metadata for decayed state
        metadata["stage"] = MemoryStage.DECAYED.value
        metadata["decayed_at"] = datetime.now().isoformat()

        # Get embedding
        embeddings = await self._embedding_function.embed_documents([text])

        # Add to decayed collection
        self._decayed._collection.add(
            ids=[memory_id],
            embeddings=embeddings,
            documents=[text],
            metadatas=[metadata],
        )

        # Delete from source
        await source_collection.delete([memory_id])

        self._emit_event(
            "memory_demoted",
            {"memory_id": memory_id, "to": "decayed"},
        )

        return True

    async def reactivate_from_decayed(self, memory_id: str) -> bool:
        """
        Reactivate a decayed memory back to long-term.

        Called when a decayed memory is accessed, indicating it's still valuable.

        Args:
            memory_id: ID of memory to reactivate

        Returns:
            True if reactivation successful, False if memory not found
        """
        memory = await self._decayed.get_by_id(memory_id)
        if not memory:
            return False

        text = memory.get("text", "")
        metadata = memory.get("metadata", {})

        # Update metadata for reactivation
        metadata["stage"] = MemoryStage.LONG_TERM.value
        metadata["decay_score"] = 0.5  # Reset to neutral
        # Remove decayed_at (ChromaDB doesn't support None values)
        metadata.pop("decayed_at", None)
        metadata["last_accessed_at"] = datetime.now().isoformat()
        metadata["access_count"] = metadata.get("access_count", 0) + 1

        # Get embedding
        embeddings = await self._embedding_function.embed_documents([text])

        # Add to long-term
        self._long_term._collection.add(
            ids=[memory_id],
            embeddings=embeddings,
            documents=[text],
            metadatas=[metadata],
        )

        # Delete from decayed
        await self._decayed.delete([memory_id])

        self._emit_event(
            "memory_reactivated",
            {"memory_id": memory_id, "from": "decayed", "to": "long_term"},
        )

        return True

    async def recover_incomplete_promotions(self) -> int:
        """
        Complete any promotions that were interrupted by crash.

        Scans long-term collection for memories with PENDING promotion state
        and completes the promotion by deleting from short-term.

        Returns:
            Number of recovered promotions
        """
        # Find memories with pending promotion state in long-term
        pending_results = await self._long_term.get_all(
            limit=1000,
            where={"promotion_state": PromotionState.PENDING.value},
        )

        recovered = 0
        for memory in pending_results:
            memory_id = memory.get("id")
            if not memory_id:
                continue

            # Delete from short-term (completing the promotion)
            await self._short_term.delete([memory_id])

            # Mark promotion complete
            await self._long_term.update_metadata(
                memory_id,
                {"promotion_state": PromotionState.COMPLETE.value},
            )
            recovered += 1

        if recovered > 0:
            self._emit_event(
                "promotions_recovered",
                {"count": recovered},
            )

        return recovered

    async def get_stats(self) -> dict[str, int]:
        """
        Get document counts across all collections.

        Returns:
            Dict with counts for each collection
        """
        short_term_count, long_term_count, decayed_count = await asyncio.gather(
            self._short_term.count(),
            self._long_term.count(),
            self._decayed.count(),
        )

        return {
            "short_term": short_term_count,
            "long_term": long_term_count,
            "decayed": decayed_count,
            "total_active": short_term_count + long_term_count,
            "total": short_term_count + long_term_count + decayed_count,
        }

    async def clear_all(self) -> dict[str, int]:
        """
        Clear all documents from all collections.

        Returns:
            Dict with counts of deleted documents per collection
        """
        short_deleted, long_deleted, decayed_deleted = await asyncio.gather(
            self._short_term.clear(),
            self._long_term.clear(),
            self._decayed.clear(),
        )

        return {
            "short_term_deleted": short_deleted,
            "long_term_deleted": long_deleted,
            "decayed_deleted": decayed_deleted,
        }

    async def hard_delete_expired(
        self,
        retention_days: int = 30,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        """
        Permanently delete memories decayed beyond retention period.

        Scans decayed collection for memories where:
            decayed_at + retention_days < now

        This enforces the decayed_retention_days config that was previously
        not enforced, allowing DECAYED memories to be permanently removed.

        Args:
            retention_days: Days to retain decayed memories (default 30)
            dry_run: If True, report what would be deleted without modifying

        Returns:
            Dict with deleted_count and deleted_ids
        """
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        # Get all decayed memories
        try:
            decayed_docs = await self._decayed.get_all(limit=10000)
        except Exception as e:
            logger.error(f"Error getting decayed memories: {e}")
            return {"deleted_count": 0, "deleted_ids": [], "error": str(e)}

        expired_ids: list[str] = []

        for doc in decayed_docs:
            memory_id = doc.get("id")
            if not memory_id:
                continue

            metadata = doc.get("metadata", {})
            decayed_at_str = metadata.get("decayed_at")

            if not decayed_at_str:
                # Skip memories without decayed_at (need migration first)
                continue

            try:
                # Parse decayed_at timestamp
                if "T" in decayed_at_str:
                    decayed_at = datetime.fromisoformat(
                        decayed_at_str.replace("Z", "+00:00")
                    )
                else:
                    decayed_at = datetime.strptime(
                        decayed_at_str, "%Y-%m-%d %H:%M:%S"
                    )

                # Check if memory has expired
                # Note: comparing naive datetimes for simplicity
                decayed_at_naive = (
                    decayed_at.replace(tzinfo=None)
                    if decayed_at.tzinfo
                    else decayed_at
                )
                if decayed_at_naive < cutoff_date:
                    expired_ids.append(memory_id)

            except (ValueError, TypeError) as e:
                logger.warning(
                    f"Could not parse decayed_at for memory {memory_id}: {e}"
                )
                continue

        # Actually delete if not dry run
        if not dry_run and expired_ids:
            try:
                await self._decayed.delete(expired_ids)
                logger.info(f"Hard deleted {len(expired_ids)} expired decayed memories")
            except Exception as e:
                logger.error(f"Error deleting expired memories: {e}")
                return {
                    "deleted_count": 0,
                    "deleted_ids": [],
                    "error": str(e),
                    "would_delete": expired_ids,
                }

        self._emit_event(
            "hard_delete_expired",
            {
                "retention_days": retention_days,
                "dry_run": dry_run,
                "deleted_count": len(expired_ids),
            },
        )

        return {
            "deleted_count": len(expired_ids),
            "deleted_ids": expired_ids,
            "dry_run": dry_run,
        }

    async def cleanup_orphaned_graph_nodes(
        self,
        deleted_memory_ids: set[str],
        graph_store: "GraphStoreAdapter",
        dry_run: bool = True,
    ) -> dict[str, Any]:
        """
        Remove graph nodes whose ALL source memories were hard deleted.

        When memories are hard deleted, graph nodes that were derived from
        those memories become orphaned. This method identifies and removes
        nodes where all source_memory_ids have been deleted.

        Args:
            deleted_memory_ids: Set of memory IDs that were hard deleted
            graph_store: GraphStoreAdapter to remove orphaned nodes from
            dry_run: If True, report what would be deleted without modifying

        Returns:
            Dict with deleted_count and deleted_node_ids
        """
        if not deleted_memory_ids:
            return {"deleted_count": 0, "deleted_node_ids": [], "dry_run": dry_run}

        orphaned_node_ids: list[str] = []

        try:
            all_nodes = await graph_store.get_all_nodes()

            for node in all_nodes:
                source_memory_ids = getattr(node, "source_memory_ids", [])

                # Skip nodes without source memory links
                if not source_memory_ids:
                    continue

                # Check if ALL source memories have been deleted
                if all(mid in deleted_memory_ids for mid in source_memory_ids):
                    orphaned_node_ids.append(node.id)

            # Actually delete if not dry run
            if not dry_run and orphaned_node_ids:
                for node_id in orphaned_node_ids:
                    await graph_store.remove_node(node_id)
                logger.info(
                    f"Removed {len(orphaned_node_ids)} orphaned graph nodes"
                )

        except Exception as e:
            logger.error(f"Error cleaning up orphaned graph nodes: {e}")
            return {
                "deleted_count": 0,
                "deleted_node_ids": [],
                "error": str(e),
                "dry_run": dry_run,
            }

        self._emit_event(
            "cleanup_orphaned_graph_nodes",
            {
                "dry_run": dry_run,
                "deleted_count": len(orphaned_node_ids),
            },
        )

        return {
            "deleted_count": len(orphaned_node_ids),
            "deleted_node_ids": orphaned_node_ids,
            "dry_run": dry_run,
        }
