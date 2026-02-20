"""
Redundancy Pruner for Friday Memory.

Handles pruning of redundant and stale memories:
- Semantic deduplication using stored embeddings (zero API calls)
- Entity consolidation via merge
- Stale memory removal
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

import chromadb

from friday_memory.maintenance.models import (
    DuplicateGroup,
    PruneConfig,
    PrunedItem,
    PruneReport,
)

if TYPE_CHECKING:
    from friday_memory.maintenance.logger import ReorganizationLogger

logger = logging.getLogger(__name__)


class RedundancyPruner:
    """
    Prunes redundant and stale memories from the stores.

    Uses efficient algorithms that leverage stored data:
    - ChromaDB's stored embeddings for semantic dedup (zero API calls)
    - Graph merge_nodes for entity consolidation
    - Configurable staleness thresholds

    Example:
        pruner = RedundancyPruner(memory_dir="./memory")

        # Dry run first
        report = await pruner.prune(dry_run=True)
        print(f"Would remove {report.insights_removed} insights")

        # Actually prune
        report = await pruner.prune(dry_run=False)
    """

    def __init__(
        self,
        memory_dir: str | Path,
        config: PruneConfig | None = None,
        reorg_logger: ReorganizationLogger | None = None,
    ) -> None:
        """
        Initialize the pruner.

        Args:
            memory_dir: Directory containing memory stores
            config: Configuration for pruning thresholds
            reorg_logger: Optional logger for recording destructive actions
        """
        self._memory_dir = Path(memory_dir)
        self._config = config or PruneConfig()
        self._reorg_logger = reorg_logger
        self._graph_data: dict[str, Any] | None = None
        self._graph_modified = False

    def _load_graph(self) -> dict[str, Any]:
        """Load graph data."""
        if self._graph_data is not None:
            return self._graph_data

        graph_path = self._memory_dir / "graph.json"
        if not graph_path.exists():
            self._graph_data = {"nodes": {}, "edges": []}
            return self._graph_data

        with open(graph_path) as f:
            self._graph_data = json.load(f)

        return self._graph_data

    def _save_graph(self) -> None:
        """Save modified graph data."""
        if not self._graph_modified or self._graph_data is None:
            return

        graph_path = self._memory_dir / "graph.json"

        # Atomic write
        temp_path = graph_path.with_suffix(".tmp")
        with open(temp_path, "w") as f:
            json.dump(self._graph_data, f, indent=2, default=str)
        temp_path.replace(graph_path)

        logger.info("Graph saved")
        self._graph_modified = False

    def _get_chroma_client(self) -> chromadb.ClientAPI | None:
        """Get ChromaDB client if vector store exists."""
        # Try both possible locations for ChromaDB:
        # 1. Directly in memory_dir (when memory_dir IS the vector dir)
        # 2. In memory_dir/vector subdirectory
        for vector_dir in [self._memory_dir, self._memory_dir / "vector"]:
            chroma_db = vector_dir / "chroma.sqlite3"
            if chroma_db.exists():
                try:
                    return chromadb.PersistentClient(path=str(vector_dir))
                except Exception as e:
                    logger.warning(f"Failed to open ChromaDB at {vector_dir}: {e}")
                    continue

        logger.warning(
            f"ChromaDB not found in {self._memory_dir} or {self._memory_dir / 'vector'}"
        )
        return None

    async def identify_redundant_insights(self) -> list[DuplicateGroup]:
        """
        Find semantically redundant insights using stored embeddings.

        Uses ChromaDB's stored embeddings for efficient similarity search
        without any embedding API calls.

        Returns:
            List of duplicate groups
        """
        duplicates: list[DuplicateGroup] = []

        client = self._get_chroma_client()
        if not client:
            return duplicates

        try:
            # Get collection
            collections = client.list_collections()
            if not collections:
                return duplicates

            collection = collections[0]  # Assume single collection

            # Get all documents with their embeddings
            # This is efficient - no API calls, just reads from disk
            all_data = collection.get(include=["embeddings", "metadatas", "documents"])

            ids = all_data["ids"]
            embeddings = all_data["embeddings"]

            # Check for empty results (embeddings may be numpy array)
            if not ids or embeddings is None or len(embeddings) == 0:
                return duplicates
            all_data["metadatas"] or [{}] * len(ids)

            logger.info(f"Checking {len(ids)} documents for semantic duplicates")

            # Track which IDs have been marked as duplicates
            marked_duplicates: set[str] = set()

            # For each document, find similar ones using stored embedding
            for i, doc_id in enumerate(ids):
                if doc_id in marked_duplicates:
                    continue

                # Query using the stored embedding
                similar = collection.query(
                    query_embeddings=[embeddings[i]],
                    n_results=min(10, len(ids)),
                    include=["distances"],
                )

                if not similar["ids"] or not similar["ids"][0]:
                    continue

                # Find duplicates (distance < threshold)
                # ChromaDB returns cosine distance, so lower = more similar
                # For cosine similarity > 0.95, distance < 0.05
                distance_threshold = 1 - self._config.similarity_threshold
                dup_ids: list[str] = []
                dup_scores: dict[str, float] = {}

                for _j, (sim_id, distance) in enumerate(
                    zip(similar["ids"][0], similar["distances"][0], strict=False)
                ):
                    if sim_id == doc_id:
                        continue
                    if sim_id in marked_duplicates:
                        continue
                    if distance <= distance_threshold:
                        dup_ids.append(sim_id)
                        dup_scores[sim_id] = 1 - distance  # Convert to similarity

                if dup_ids:
                    duplicates.append(
                        DuplicateGroup(
                            primary_id=doc_id,
                            duplicate_ids=dup_ids,
                            similarity_scores=dup_scores,
                            match_type="semantic",
                        )
                    )
                    marked_duplicates.update(dup_ids)

            logger.info(f"Found {len(duplicates)} redundant insight groups")

        except Exception as e:
            logger.error(f"Error finding redundant insights: {e}")

        return duplicates

    async def identify_stale_entities(self) -> list[PrunedItem]:
        """
        Find entities that are stale based on hit_count and age.

        Returns:
            List of items that would be pruned
        """
        stale_items: list[PrunedItem] = []
        graph_data = self._load_graph()

        threshold_date = datetime.now() - timedelta(
            days=self._config.stale_threshold_days
        )

        for node_id, node_data in graph_data.get("nodes", {}).items():
            hit_count = node_data.get("hit_count", 0)

            if hit_count >= self._config.min_hit_count:
                continue

            # Check last_accessed
            last_accessed_str = node_data.get("last_accessed")
            if not last_accessed_str:
                continue

            try:
                if "T" in last_accessed_str:
                    last_accessed = datetime.fromisoformat(
                        last_accessed_str.replace("Z", "+00:00")
                    )
                else:
                    last_accessed = datetime.strptime(
                        last_accessed_str, "%Y-%m-%d %H:%M:%S"
                    )

                if last_accessed < threshold_date:
                    label = node_data.get("label", node_id)
                    stale_items.append(
                        PrunedItem(
                            item_id=node_id,
                            item_type="entity",
                            store="graph",
                            reason=(
                                f"Stale: hit_count={hit_count}, "
                                f"last_accessed={last_accessed.date()}"
                            ),
                            content_preview=f"{label} ({node_data.get('type', 'unknown')})",  # noqa: E501
                        )
                    )
            except (ValueError, TypeError):
                pass

        return stale_items

    async def identify_stale_edges(self) -> list[PrunedItem]:
        """
        Find edges that are stale based on hit_count and age.

        Similar to identify_stale_entities() but for graph edges.
        Edges without last_accessed (pre-migration) are skipped.

        Returns:
            List of items that would be pruned
        """
        stale_items: list[PrunedItem] = []
        graph_data = self._load_graph()

        threshold_date = datetime.now() - timedelta(
            days=self._config.stale_threshold_days
        )

        for _i, edge in enumerate(graph_data.get("edges", [])):
            hit_count = edge.get("hit_count", 0)

            if hit_count >= self._config.min_hit_count:
                continue

            # Check last_accessed - skip edges without it (pre-migration)
            last_accessed_str = edge.get("last_accessed")
            if not last_accessed_str:
                continue

            try:
                if "T" in last_accessed_str:
                    last_accessed = datetime.fromisoformat(
                        last_accessed_str.replace("Z", "+00:00")
                    )
                else:
                    last_accessed = datetime.strptime(
                        last_accessed_str, "%Y-%m-%d %H:%M:%S"
                    )

                if last_accessed < threshold_date:
                    source_id = edge.get("source", "?")
                    target_id = edge.get("target", "?")
                    relation = edge.get("relation", "unknown")
                    edge_id = f"{source_id}->{target_id}"

                    stale_items.append(
                        PrunedItem(
                            item_id=edge_id,
                            item_type="edge",
                            store="graph",
                            reason=(
                                f"Stale edge: hit_count={hit_count}, "
                                f"last_accessed={last_accessed.date()}"
                            ),
                            content_preview=f"{source_id} --[{relation}]--> {target_id}",  # noqa: E501
                        )
                    )
            except (ValueError, TypeError):
                pass

        return stale_items

    def _merge_entities(
        self,
        primary_id: str,
        duplicate_ids: list[str],
        dry_run: bool,
    ) -> int:
        """
        Merge duplicate entities into the primary.

        Args:
            primary_id: ID of the entity to keep
            duplicate_ids: IDs of duplicates to merge
            dry_run: If True, don't actually modify

        Returns:
            Number of entities merged
        """
        graph_data = self._load_graph()
        nodes = graph_data.get("nodes", {})
        edges = graph_data.get("edges", [])

        if primary_id not in nodes:
            return 0

        merged_count = 0
        primary_node = nodes[primary_id]
        primary_label = primary_node.get("label", primary_id)

        for dup_id in duplicate_ids:
            if dup_id not in nodes:
                continue

            dup_node = nodes[dup_id]
            dup_label = dup_node.get("label", dup_id)

            if not dry_run:
                # Merge properties (keep higher hit_count)
                primary_node["hit_count"] = max(
                    primary_node.get("hit_count", 0),
                    dup_node.get("hit_count", 0),
                )

                # Merge properties dict
                for key, value in dup_node.get("properties", {}).items():
                    if key not in primary_node.get("properties", {}):
                        if "properties" not in primary_node:
                            primary_node["properties"] = {}
                        primary_node["properties"][key] = value

                # Redirect edges
                for edge in edges:
                    if edge.get("source") == dup_id:
                        edge["source"] = primary_id
                    if edge.get("target") == dup_id:
                        edge["target"] = primary_id

                # Remove duplicate node
                del nodes[dup_id]

                self._graph_modified = True

            # Log the merge action
            if self._reorg_logger:
                self._reorg_logger.log_entity_merged(
                    primary_id=primary_id,
                    merged_ids=[dup_id],
                    reason=f"Duplicate entity '{dup_label}' merged into '{primary_label}'",  # noqa: E501
                    content_preview=f"{dup_label} -> {primary_label}",
                    metadata={
                        "dup_hit_count": dup_node.get("hit_count", 0),
                        "primary_hit_count": primary_node.get("hit_count", 0),
                        "dup_type": dup_node.get("type", "unknown"),
                    },
                )

            merged_count += 1

        # Remove duplicate edges after redirecting
        if not dry_run and merged_count > 0:
            seen_edges: set[tuple] = set()
            unique_edges = []
            for edge in edges:
                key = (edge.get("source"), edge.get("target"), edge.get("relation"))
                if key not in seen_edges:
                    seen_edges.add(key)
                    unique_edges.append(edge)
            graph_data["edges"] = unique_edges

        return merged_count

    def _remove_entity(
        self,
        node_id: str,
        dry_run: bool,
        reason: str = "Stale entity removed",
    ) -> bool:
        """
        Remove an entity and its edges.

        Args:
            node_id: ID of the entity to remove
            dry_run: If True, don't actually modify
            reason: Reason for removal (for logging)

        Returns:
            True if removed
        """
        graph_data = self._load_graph()
        nodes = graph_data.get("nodes", {})

        if node_id not in nodes:
            return False

        node = nodes[node_id]
        label = node.get("label", node_id)

        # Log the removal action
        if self._reorg_logger:
            self._reorg_logger.log_entity_removed(
                entity_id=node_id,
                reason=reason,
                content_preview=f"{label} ({node.get('type', 'unknown')})",
                content_full=str(node)
                if self._reorg_logger.verbosity.value == "verbose"
                else None,
                metadata={
                    "hit_count": node.get("hit_count", 0),
                    "type": node.get("type", "unknown"),
                    "last_accessed": node.get("last_accessed"),
                },
            )

        if not dry_run:
            # Remove node
            del nodes[node_id]

            # Remove associated edges
            edges = graph_data.get("edges", [])
            graph_data["edges"] = [
                e
                for e in edges
                if e.get("source") != node_id and e.get("target") != node_id
            ]

            self._graph_modified = True

        return True

    def _remove_stale_edges(
        self,
        stale_edges: list[PrunedItem],
        dry_run: bool,
    ) -> int:
        """
        Remove stale edges from the graph.

        Args:
            stale_edges: List of stale edge items from identify_stale_edges()
            dry_run: If True, don't actually modify

        Returns:
            Number of edges removed
        """
        if not stale_edges:
            return 0

        graph_data = self._load_graph()
        edges = graph_data.get("edges", [])

        # Build a set of edge keys to remove
        # Edge IDs are in format "source_id->target_id"
        edges_to_remove: set[tuple[str, str]] = set()
        for item in stale_edges:
            if "->" in item.item_id:
                source_id, target_id = item.item_id.split("->", 1)
                edges_to_remove.add((source_id, target_id))

        if not edges_to_remove:
            return 0

        removed_count = 0

        # Log removals
        if self._reorg_logger:
            for item in stale_edges:
                self._reorg_logger.log_edge_removed(
                    edge_id=item.item_id,
                    reason=item.reason,
                    content_preview=item.content_preview,
                )

        if not dry_run:
            # Filter out stale edges
            new_edges = []
            for edge in edges:
                source_id = edge.get("source", "")
                target_id = edge.get("target", "")
                if (source_id, target_id) not in edges_to_remove:
                    new_edges.append(edge)
                else:
                    removed_count += 1

            graph_data["edges"] = new_edges
            self._graph_modified = True

            logger.info(f"Removed {removed_count} stale edges from graph")
        else:
            removed_count = len(stale_edges)

        return removed_count

    def _remove_insights(
        self,
        insight_ids: list[str],
        dry_run: bool,
        reasons: dict[str, str] | None = None,
    ) -> int:
        """
        Remove insights from vector store.

        Args:
            insight_ids: IDs of insights to remove
            dry_run: If True, don't actually remove
            reasons: Optional mapping of insight_id -> reason for removal

        Returns:
            Number of insights removed
        """
        if not insight_ids:
            return 0

        reasons = reasons or {}

        # Log each insight removal
        if self._reorg_logger:
            for insight_id in insight_ids:
                self._reorg_logger.log_insight_removed(
                    insight_id=insight_id,
                    reason=reasons.get(insight_id, "Semantic duplicate"),
                )

        if dry_run:
            return len(insight_ids)

        client = self._get_chroma_client()
        if not client:
            return 0

        try:
            collections = client.list_collections()
            if not collections:
                return 0

            collection = collections[0]
            collection.delete(ids=insight_ids)

            logger.info(f"Removed {len(insight_ids)} insights from vector store")
            return len(insight_ids)

        except Exception as e:
            logger.error(f"Error removing insights: {e}")
            return 0

    async def prune_redundancies(self, dry_run: bool = True) -> PruneReport:
        """
        Prune redundant data from all stores.

        This is an alias for prune() to match the plan interface.
        """
        return await self.prune(dry_run=dry_run)

    async def merge_duplicate_entities(
        self,
        groups: list[DuplicateGroup] | None = None,
        dry_run: bool = True,
    ) -> PruneReport:
        """
        Merge duplicate entity groups.

        Args:
            groups: Optional list of duplicate groups. If None, finds them.
            dry_run: If True, don't actually merge

        Returns:
            PruneReport with results
        """
        report = PruneReport(dry_run=dry_run)

        # Find duplicates if not provided
        if groups is None:
            from friday_memory.maintenance.analyzer import ConsistencyAnalyzer

            analyzer = ConsistencyAnalyzer(self._memory_dir, self._config)
            graph_data = self._load_graph()
            groups = analyzer._find_duplicate_entities(graph_data)

        for group in groups:
            merged = self._merge_entities(
                group.primary_id,
                group.duplicate_ids,
                dry_run,
            )
            report.entities_merged += merged
            report.merged_groups.append(group)

        if not dry_run and self._graph_modified:
            self._save_graph()

        return report

    async def prune(self, dry_run: bool = True) -> PruneReport:
        """
        Perform full pruning operation.

        Args:
            dry_run: If True, report what would be pruned without modifying

        Returns:
            PruneReport with results
        """
        logger.info(f"Starting pruning (dry_run={dry_run}) of {self._memory_dir}")

        report = PruneReport(dry_run=dry_run)

        try:
            # 1. Find and handle redundant insights
            logger.debug("Identifying redundant insights...")
            redundant_insights = await self.identify_redundant_insights()

            # Build reasons mapping for logging
            insight_reasons: dict[str, str] = {}
            for group in redundant_insights:
                # Collect duplicate IDs for removal
                for dup_id in group.duplicate_ids:
                    reason = f"Semantic duplicate of {group.primary_id}"
                    insight_reasons[dup_id] = reason
                    report.items.append(
                        PrunedItem(
                            item_id=dup_id,
                            item_type="insight",
                            store="vector",
                            reason=reason,
                            content_preview=None,
                        )
                    )

            # Remove redundant insights
            all_dup_insight_ids = [
                dup_id for group in redundant_insights for dup_id in group.duplicate_ids
            ]
            report.insights_removed = self._remove_insights(
                all_dup_insight_ids, dry_run, reasons=insight_reasons
            )

            # 2. Find and merge duplicate entities
            logger.debug("Identifying duplicate entities...")
            from friday_memory.maintenance.analyzer import ConsistencyAnalyzer

            analyzer = ConsistencyAnalyzer(self._memory_dir, self._config)
            graph_data = self._load_graph()
            duplicate_groups = analyzer._find_duplicate_entities(graph_data)

            for group in duplicate_groups:
                merged = self._merge_entities(
                    group.primary_id,
                    group.duplicate_ids,
                    dry_run,
                )
                report.entities_merged += merged
                report.merged_groups.append(group)

            # 3. Find and remove stale entities
            logger.debug("Identifying stale entities...")
            stale_entities = await self.identify_stale_entities()

            entity_edges_removed = 0
            for item in stale_entities:
                report.items.append(item)
                if self._remove_entity(item.item_id, dry_run, reason=item.reason):
                    report.entities_removed += 1
                    # Count edges removed with entity (approximate)
                    entity_edges_removed += 2  # Average estimate

            # 4. Find and remove stale edges
            logger.debug("Identifying stale edges...")
            stale_edges = await self.identify_stale_edges()

            for item in stale_edges:
                report.items.append(item)

            stale_edges_removed = self._remove_stale_edges(stale_edges, dry_run)

            # Total edges removed = from entity removal + direct stale edge removal
            report.edges_removed = entity_edges_removed + stale_edges_removed

            # Save graph if modified
            if not dry_run and self._graph_modified:
                self._save_graph()

            logger.info(
                f"Pruning complete: "
                f"insights_removed={report.insights_removed}, "
                f"entities_merged={report.entities_merged}, "
                f"entities_removed={report.entities_removed}, "
                f"edges_removed={report.edges_removed}"
            )

        except Exception as e:
            logger.error(f"Error during pruning: {e}")
            report.errors.append(str(e))
            # Save graph even on error to preserve any changes made before failure
            if not dry_run and self._graph_modified:
                logger.info("Saving graph after error to preserve changes")
                self._save_graph()

        return report

    def generate_report_summary(self, report: PruneReport) -> str:
        """
        Generate a human-readable summary of the prune report.

        Args:
            report: The prune report

        Returns:
            Formatted summary string
        """
        status = "DRY RUN" if report.dry_run else "EXECUTED"

        lines = [
            "=" * 60,
            f"PRUNE REPORT ({status})",
            "=" * 60,
            f"Time: {report.pruned_at.isoformat()}",
            "",
            "RESULTS:",
            f"  Insights removed: {report.insights_removed}",
            f"  Entities merged: {report.entities_merged}",
            f"  Entities removed: {report.entities_removed}",
            f"  Edges removed: {report.edges_removed}",
            "",
        ]

        if report.merged_groups:
            lines.append(f"MERGE GROUPS: {len(report.merged_groups)}")
            for group in report.merged_groups[:5]:
                lines.append(
                    f"  - {group.primary_id} <- "
                    f"{', '.join(group.duplicate_ids[:3])}"
                    f"{'...' if len(group.duplicate_ids) > 3 else ''}"
                )
            if len(report.merged_groups) > 5:
                lines.append(f"  ... and {len(report.merged_groups) - 5} more")
            lines.append("")

        if report.items:
            lines.append(f"PRUNED ITEMS: {len(report.items)}")
            for item in report.items[:10]:
                lines.append(f"  [{item.store}] {item.item_id}: {item.reason}")
            if len(report.items) > 10:
                lines.append(f"  ... and {len(report.items) - 10} more")

        if report.errors:
            lines.append("")
            lines.append("ERRORS:")
            for error in report.errors:
                lines.append(f"  - {error}")

        lines.append("=" * 60)

        return "\n".join(lines)
