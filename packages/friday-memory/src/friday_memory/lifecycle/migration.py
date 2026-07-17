# mypy: ignore-errors
"""
Memory Lifecycle Migration Utilities.

Provides migration from legacy single-collection memories to
lifecycle-aware multi-collection storage.

Ref: docs/archive/build-plans/completed/friday-core-legacy/memory-lifecycle-staging-decay.md, Section "/migrate Command"
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from friday_memory.lifecycle.stages import MemoryStage

if TYPE_CHECKING:
    from friday_memory.retrieval.collection_manager import CollectionManager

logger = logging.getLogger(__name__)


class MigrationReport(BaseModel):
    """Report from lifecycle migration."""

    migrated_at: datetime = Field(default_factory=datetime.now)
    dry_run: bool = Field(default=True)

    # Vector store stats
    vectors_scanned: int = 0
    vectors_migrated: int = 0
    vectors_skipped: int = 0

    # Graph store stats
    nodes_scanned: int = 0
    nodes_migrated: int = 0
    nodes_skipped: int = 0

    # Edge stats
    edges_scanned: int = 0
    edges_migrated: int = 0
    edges_skipped: int = 0

    # Errors
    errors: list[str] = Field(default_factory=list)

    @property
    def total_migrated(self) -> int:
        """Get total items migrated."""
        return self.vectors_migrated + self.nodes_migrated + self.edges_migrated

    @property
    def success(self) -> bool:
        """Check if migration completed without errors."""
        return len(self.errors) == 0

    @property
    def needs_migration(self) -> bool:
        """Check if any items need migration."""
        return (
            self.vectors_migrated > 0
            or self.nodes_migrated > 0
            or self.edges_migrated > 0
        )


class MemoryMigrator:
    """
    Migrates existing memories to include lifecycle metadata.

    This migrator is designed to be:
    1. Non-destructive: Only adds fields, never removes data
    2. Idempotent: Safe to run multiple times
    3. Incremental: Only processes items that need migration

    Migration adds the following metadata to vector documents:
    - stage: MemoryStage.LONG_TERM (existing memories are assumed valuable)
    - hit_count: 0 (or preserve existing)
    - decay_score: 1.0 (fresh start)
    - retrieval_factor: 1.0 (neutral factor)
    - migrated_at: timestamp

    Migration adds the following to graph nodes:
    - stage: MemoryStage.LONG_TERM
    - migrated_at: timestamp

    Example:
        migrator = MemoryMigrator(
            vector_store=vector_store,
            graph_store=graph_store,
            collection_manager=collection_manager,
        )

        # Preview what would be migrated
        report = await migrator.migrate(dry_run=True)
        print(f"Would migrate: {report.total_migrated} items")

        # Actually perform migration
        report = await migrator.migrate(dry_run=False)
    """

    def __init__(
        self,
        vector_store: Any = None,
        graph_store: Any = None,
        collection_manager: CollectionManager | None = None,
    ) -> None:
        """
        Initialize the migrator.

        Args:
            vector_store: VectorStoreAdapter for legacy single-collection access
            graph_store: GraphStoreAdapter for graph node migration
            collection_manager: CollectionManager for multi-collection migration
        """
        self._vector_store = vector_store
        self._graph_store = graph_store
        self._collection_manager = collection_manager

    async def migrate(self, dry_run: bool = True) -> MigrationReport:
        """
        Run the migration process.

        Args:
            dry_run: If True, only report what would be migrated without changes

        Returns:
            MigrationReport with migration statistics
        """
        report = MigrationReport(dry_run=dry_run)

        logger.info(f"Starting migration (dry_run={dry_run})...")

        try:
            # Migrate vector store
            await self._migrate_vectors(report, dry_run)

            # Migrate graph store
            await self._migrate_graph_nodes(report, dry_run)

            # Migrate graph edges (add staleness tracking fields)
            await self._migrate_graph_edges(report, dry_run)

            # Migrate decayed memories (add decayed_at timestamp if missing)
            await self._migrate_decayed_timestamps(report, dry_run)

            logger.info(
                f"Migration complete: {report.total_migrated} items migrated, "
                f"{report.vectors_skipped + report.nodes_skipped + report.edges_skipped} already migrated"  # noqa: E501
            )

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            report.errors.append(str(e))

        return report

    async def _migrate_vectors(self, report: MigrationReport, dry_run: bool) -> None:
        """Migrate vector store documents to include lifecycle metadata."""
        if not self._vector_store:
            logger.info("No vector store provided, skipping vector migration")
            return

        try:
            # Get all documents from vector store
            # Note: This may need pagination for large collections
            all_docs = await self._get_all_vector_documents()
            report.vectors_scanned = len(all_docs)

            for doc in all_docs:
                doc_id = doc.get("id", "")
                metadata = doc.get("metadata", {})

                # Check if already migrated
                if self._has_lifecycle_metadata(metadata):
                    report.vectors_skipped += 1
                    continue

                # Prepare updated metadata
                updated_metadata = self._add_lifecycle_metadata(metadata)

                if not dry_run:
                    try:
                        await self._update_vector_metadata(doc_id, updated_metadata)
                    except Exception as e:
                        report.errors.append(f"Failed to migrate vector {doc_id}: {e}")
                        continue

                report.vectors_migrated += 1

        except Exception as e:
            logger.error(f"Error migrating vectors: {e}")
            report.errors.append(f"Vector migration error: {e}")

    async def _migrate_graph_nodes(
        self, report: MigrationReport, dry_run: bool
    ) -> None:
        """Migrate graph nodes to include lifecycle metadata."""
        if not self._graph_store:
            logger.info("No graph store provided, skipping graph migration")
            return

        try:
            # Get all nodes (async)
            all_nodes = await self._graph_store.get_all_nodes()
            report.nodes_scanned = len(all_nodes)

            for node in all_nodes:
                # Check if already migrated
                if hasattr(node, "stage") and node.stage is not None:
                    report.nodes_skipped += 1
                    continue

                if not dry_run:
                    try:
                        # Add lifecycle metadata to node
                        node.stage = MemoryStage.LONG_TERM
                        if not hasattr(node, "migrated_at") or node.migrated_at is None:
                            node.migrated_at = datetime.now()

                        # Update node in store (async)
                        await self._graph_store.remove_node(node.id)
                        await self._graph_store.add_node(node)
                    except Exception as e:
                        report.errors.append(f"Failed to migrate node {node.id}: {e}")
                        continue

                report.nodes_migrated += 1

        except Exception as e:
            logger.error(f"Error migrating graph nodes: {e}")
            report.errors.append(f"Graph node migration error: {e}")

    async def _migrate_graph_edges(
        self, report: MigrationReport, dry_run: bool
    ) -> None:
        """Migrate graph edges to add staleness tracking fields."""
        if not self._graph_store:
            logger.info("No graph store provided, skipping edge migration")
            return

        # Check if this is a real graph store with internal graph access
        # (required for staleness field migration which needs direct _graph access)
        # We check for _graph being a networkx graph which is specific to ElementXGraphStore  # noqa: E501
        try:
            import networkx as nx

            if not (
                hasattr(self._graph_store, "_graph")
                and isinstance(self._graph_store._graph, nx.Graph)
            ):
                logger.info(
                    "Graph store does not support direct graph access, skipping edge migration"  # noqa: E501
                )
                return
        except ImportError:
            logger.info("NetworkX not available, skipping edge migration")
            return

        try:
            # Get all edges directly
            all_edges = await self._graph_store.get_all_edges()
            report.edges_scanned = len(all_edges)
            now = datetime.now().isoformat()

            # Track edges that need migration
            edges_to_update: list[tuple[str, str]] = []

            for edge in all_edges:
                # Check if edge needs migration (missing staleness fields)
                # We need to check the raw edge data in the graph
                async with self._graph_store._acquire_lock():
                    if not self._graph_store._graph.has_edge(
                        edge.source_id, edge.target_id
                    ):
                        continue

                    edge_data = self._graph_store._graph.edges[
                        edge.source_id, edge.target_id
                    ]

                    needs_migration = (
                        "hit_count" not in edge_data
                        or "last_accessed" not in edge_data
                        or "created_at" not in edge_data
                    )

                    if not needs_migration:
                        report.edges_skipped += 1
                        continue

                    edges_to_update.append((edge.source_id, edge.target_id))

            # Perform updates outside the per-edge lock
            if edges_to_update and not dry_run:
                async with self._graph_store._acquire_lock():
                    for source_id, target_id in edges_to_update:
                        if self._graph_store._graph.has_edge(source_id, target_id):
                            edge_data = self._graph_store._graph.edges[
                                source_id, target_id
                            ]
                            if "hit_count" not in edge_data:
                                edge_data["hit_count"] = 0
                            if "last_accessed" not in edge_data:
                                edge_data["last_accessed"] = now
                            if "created_at" not in edge_data:
                                edge_data["created_at"] = now

                    self._graph_store._save()

            report.edges_migrated = len(edges_to_update)
            logger.info(
                f"Edge migration: {report.edges_migrated} migrated, "
                f"{report.edges_skipped} already have staleness fields"
            )

        except Exception as e:
            logger.error(f"Error migrating graph edges: {e}")
            report.errors.append(f"Graph edge migration error: {e}")

    async def _migrate_decayed_timestamps(
        self, report: MigrationReport, dry_run: bool
    ) -> None:
        """
        Add decayed_at timestamp to DECAYED memories missing it.

        This is required for hard_delete_expired() to work correctly.
        """
        if not self._collection_manager:
            logger.info(
                "No collection manager provided, skipping decayed timestamp migration"
            )
            return

        try:
            # Get all decayed memories
            decayed_store = getattr(self._collection_manager, "_decayed", None)
            if not decayed_store:
                logger.info("No decayed collection found, skipping")
                return

            decayed_docs = await decayed_store.get_all(limit=10000)
            now = datetime.now().isoformat()
            migrated_count = 0

            for doc in decayed_docs:
                metadata = doc.get("metadata", {})

                # Check if decayed_at is missing
                if "decayed_at" in metadata:
                    continue

                if not dry_run:
                    # Add decayed_at timestamp
                    # Use migrated_at or created_at as fallback, otherwise use now
                    decayed_at = (
                        metadata.get("migrated_at") or metadata.get("created_at") or now
                    )
                    await decayed_store.update_metadata(
                        doc["id"], {"decayed_at": decayed_at}
                    )

                migrated_count += 1

            logger.info(
                f"Decayed timestamp migration: {migrated_count} memories updated"
            )
            # Add to report (reusing vectors fields for simplicity)
            report.vectors_scanned += len(decayed_docs)
            report.vectors_migrated += migrated_count

        except Exception as e:
            logger.error(f"Error migrating decayed timestamps: {e}")
            report.errors.append(f"Decayed timestamp migration error: {e}")

    def _has_lifecycle_metadata(self, metadata: dict) -> bool:
        """Check if metadata contains lifecycle fields."""
        # Check for key lifecycle fields
        required_fields = ["stage"]
        return all(field in metadata for field in required_fields)

    def _add_lifecycle_metadata(self, metadata: dict) -> dict:
        """Add lifecycle metadata to existing metadata."""
        updated = dict(metadata)

        # Existing memories go to LONG_TERM (they've proven their value)
        updated["stage"] = MemoryStage.LONG_TERM.value

        # Preserve hit_count if exists, otherwise set to 0
        if "hit_count" not in updated:
            updated["hit_count"] = 0

        # Set decay_score to 1.0 (fresh start)
        if "decay_score" not in updated:
            updated["decay_score"] = 1.0

        # Set retrieval_factor to 1.0 (neutral)
        if "retrieval_factor" not in updated:
            updated["retrieval_factor"] = 1.0

        # Add migration timestamp
        updated["migrated_at"] = datetime.now().isoformat()

        return updated

    async def _get_all_vector_documents(self) -> list[dict]:
        """Get all documents from vector store."""
        if not self._vector_store:
            return []

        try:
            # Use search with empty query to get all documents
            # This is a common pattern but may vary by implementation
            if hasattr(self._vector_store, "get_all"):
                return await self._vector_store.get_all()
            elif hasattr(self._vector_store, "search"):
                # Fallback: search with large limit
                results = await self._vector_store.search(
                    query_embedding=[0.0] * 768,  # Dummy embedding
                    n_results=10000,
                )
                return results
            else:
                logger.warning("Vector store does not support bulk retrieval")
                return []
        except Exception as e:
            logger.error(f"Error getting vector documents: {e}")
            return []

    async def _update_vector_metadata(self, doc_id: str, metadata: dict) -> None:
        """Update metadata for a vector document."""
        if not self._vector_store:
            return

        if hasattr(self._vector_store, "update_metadata"):
            await self._vector_store.update_metadata(doc_id, metadata)
        elif hasattr(self._vector_store, "_collection"):
            # Direct ChromaDB access
            self._vector_store._collection.update(
                ids=[doc_id],
                metadatas=[metadata],
            )
        else:
            raise NotImplementedError("Vector store does not support metadata updates")

    async def check_migration_needed(self) -> bool:
        """
        Check if any memories need migration.

        Checks:
        1. Vector documents for lifecycle metadata (stage field)
        2. Graph nodes for stage field
        3. Graph edges for staleness fields (hit_count, last_accessed, created_at)
        4. Decayed memories for decayed_at timestamp

        Returns:
            True if migration is needed, False otherwise
        """
        # Check vector store
        if self._vector_store:
            try:
                docs = await self._get_all_vector_documents()
                for doc in docs[:10]:  # Sample first 10
                    metadata = doc.get("metadata", {})
                    if not self._has_lifecycle_metadata(metadata):
                        return True
            except Exception as e:
                logger.warning(f"Error checking vector store: {e}")

        # Check graph store nodes
        if self._graph_store:
            try:
                nodes = await self._graph_store.get_all_nodes()
                for node in nodes[:10]:  # Sample first 10
                    if not hasattr(node, "stage") or node.stage is None:
                        return True
            except Exception as e:
                logger.warning(f"Error checking graph store nodes: {e}")

        # Check graph store edges for staleness fields
        if self._graph_store:
            try:
                import networkx as nx

                if hasattr(self._graph_store, "_graph") and isinstance(
                    self._graph_store._graph, nx.Graph
                ):
                    edges = await self._graph_store.get_all_edges()
                    for edge in edges[:10]:  # Sample first 10
                        async with self._graph_store._acquire_lock():
                            if self._graph_store._graph.has_edge(
                                edge.source_id, edge.target_id
                            ):
                                edge_data = self._graph_store._graph.edges[
                                    edge.source_id, edge.target_id
                                ]
                                if (
                                    "hit_count" not in edge_data
                                    or "last_accessed" not in edge_data
                                    or "created_at" not in edge_data
                                ):
                                    return True
            except ImportError:
                pass  # NetworkX not available
            except Exception as e:
                logger.warning(f"Error checking graph store edges: {e}")

        # Check decayed memories for decayed_at timestamp
        if self._collection_manager:
            try:
                decayed_store = getattr(self._collection_manager, "_decayed", None)
                if decayed_store:
                    decayed_docs = await decayed_store.get_all(limit=10)
                    for doc in decayed_docs:
                        metadata = doc.get("metadata", {})
                        if "decayed_at" not in metadata:
                            return True
            except Exception as e:
                logger.warning(f"Error checking decayed memories: {e}")

        return False


async def migrate_to_multi_collection(
    source_collection: Any,
    collection_manager: CollectionManager,
    embedding_function: Any = None,
) -> MigrationReport:
    """
    Migrate from single collection to multi-collection (short-term + long-term).

    This is a more aggressive migration that:
    1. Reads all documents from the source collection
    2. Classifies them based on age/access patterns
    3. Moves them to appropriate lifecycle collections

    Args:
        source_collection: The original single collection
        collection_manager: CollectionManager for lifecycle collections
        embedding_function: Optional embedding function for re-embedding

    Returns:
        MigrationReport with statistics
    """
    report = MigrationReport(dry_run=False)

    try:
        # Get all documents from source
        if hasattr(source_collection, "get"):
            result = source_collection.get(
                include=["metadatas", "documents", "embeddings"]
            )
            ids = result.get("ids", [])
            documents = result.get("documents", [])
            metadatas = result.get("metadatas", [])
            embeddings = result.get("embeddings", [])
        else:
            logger.error("Source collection does not support bulk retrieval")
            report.errors.append("Source collection does not support bulk retrieval")
            return report

        report.vectors_scanned = len(ids)

        # Migrate each document
        for i, doc_id in enumerate(ids):
            metadata = metadatas[i] if i < len(metadatas) else {}
            document = documents[i] if i < len(documents) else ""
            embedding = embeddings[i] if embeddings and i < len(embeddings) else None

            # Check if already has lifecycle metadata
            if "stage" in metadata:
                report.vectors_skipped += 1
                continue

            # Classify based on existing metadata
            # Default to LONG_TERM for existing memories
            stage = MemoryStage.LONG_TERM

            # Add lifecycle metadata
            metadata["stage"] = stage.value
            metadata["hit_count"] = metadata.get("hit_count", 0)
            metadata["decay_score"] = 1.0
            metadata["retrieval_factor"] = 1.0
            metadata["migrated_at"] = datetime.now().isoformat()

            try:
                # Add to appropriate collection
                await collection_manager.add_to_long_term(
                    texts=[document],
                    metadatas=[metadata],
                    ids=[doc_id],
                    embeddings=[embedding] if embedding else None,
                )
                report.vectors_migrated += 1

            except Exception as e:
                report.errors.append(f"Failed to migrate {doc_id}: {e}")

        logger.info(
            f"Multi-collection migration complete: "
            f"{report.vectors_migrated} migrated, {report.vectors_skipped} skipped"
        )

    except Exception as e:
        logger.error(f"Multi-collection migration failed: {e}")
        report.errors.append(str(e))

    return report
