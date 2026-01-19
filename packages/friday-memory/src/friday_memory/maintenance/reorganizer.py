"""
Memory Reorganizer Orchestrator.

Main entry point for coordinating all maintenance operations:
- Backup
- Analyze
- Prune
- Synthesize
- Verify
- Lifecycle (promotion/decay)
- Optimization (access buffer flush, retrieval factor recompute, edge embedding)
- Full reorganization
"""

import logging
import time
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

from friday_memory.maintenance.analyzer import ConsistencyAnalyzer
from friday_memory.maintenance.backup import BackupManager
from friday_memory.maintenance.fact_checker import FactChecker
from friday_memory.maintenance.logger import ReorganizationLogger
from friday_memory.maintenance.models import (
    CleanupReport,
    ConsistencyReport,
    DeduplicationReport,
    InsightCluster,
    LifecycleReport,
    MaintenanceConfig,
    OptimizationReport,
    PruneReport,
    ReorganizationReport,
    SynthesisReport,
    VerificationReport,
)
from friday_memory.maintenance.pruner import RedundancyPruner
from friday_memory.maintenance.synthesizer import MemorySynthesizer

if TYPE_CHECKING:
    from friday_llm import LiteLLMService

    from friday_memory.retrieval import (
        AccessBuffer,
        CollectionManager,
        RetrievalFactorComputer,
    )
    from friday_memory.lifecycle import DecayCalculator, PromotionScorer

logger = logging.getLogger(__name__)


class MemoryReorganizer:
    """
    Orchestrates all memory maintenance operations.

    Provides a unified interface for:
    - Creating backups before destructive operations
    - Analyzing consistency
    - Pruning redundancies
    - Synthesizing new memories
    - Verifying facts
    - Full reorganization pipeline

    Example:
        from friday_llm import LiteLLMService

        llm = LiteLLMService(model_name="gpt-4")
        reorganizer = MemoryReorganizer(
            memory_dir="./memory",
            llm_service=llm,
        )

        # Full reorganization with backup
        report = await reorganizer.reorganize(backup_first=True, dry_run=False)
    """

    def __init__(
        self,
        memory_dir: str | Path,
        config: MaintenanceConfig | None = None,
        llm_service: "LiteLLMService | None" = None,
        classifier_llm: "LiteLLMService | None" = None,
        researcher_llm: "LiteLLMService | None" = None,
        judge_llm: "LiteLLMService | None" = None,
        embedding_function: Any = None,
        collection_name: str | None = None,
        # Lifecycle components (Phase 8)
        collection_manager: "CollectionManager | None" = None,
        access_buffer: "AccessBuffer | None" = None,
        factor_computer: "RetrievalFactorComputer | None" = None,
        promotion_scorer: "PromotionScorer | None" = None,
        decay_calculator: "DecayCalculator | None" = None,
        graph_store: Any = None,
    ) -> None:
        """
        Initialize the reorganizer.

        Args:
            memory_dir: Directory containing memory stores
            config: Configuration for all maintenance operations
            llm_service: Default LLM for all operations (synthesis, classification)
            classifier_llm: Optional separate LLM for fact classification
            researcher_llm: Optional separate LLM for fact research
            judge_llm: Optional separate LLM for fact judgment
            embedding_function: Optional embedding function for synthesized memories.
                               Should match the embedding model used to create the
                               vector store. If not provided, ChromaDB's default
                               embedding will be used (may cause dimension mismatch).
            collection_name: ChromaDB collection name for storing synthesized memories.
                            Should match the collection used by the main application.
            collection_manager: CollectionManager for lifecycle-aware retrieval.
            access_buffer: AccessBuffer for lazy access tracking.
            factor_computer: RetrievalFactorComputer for pre-computing retrieval factors.
            promotion_scorer: PromotionScorer for evaluating promotion eligibility.
            decay_calculator: DecayCalculator for calculating decay scores.
            graph_store: GraphStoreAdapter for graph-vector decay linkage.
        """
        self._memory_dir = Path(memory_dir)
        self._config = config or MaintenanceConfig()

        # Use provided LLMs or fall back to default
        self._llm = llm_service
        self._classifier_llm = classifier_llm or llm_service
        self._researcher_llm = researcher_llm or llm_service
        self._judge_llm = judge_llm or llm_service

        # Lifecycle components
        self._collection_manager = collection_manager
        self._access_buffer = access_buffer
        self._factor_computer = factor_computer
        self._promotion_scorer = promotion_scorer
        self._decay_calculator = decay_calculator
        self._graph_store = graph_store
        self._embedding_function = embedding_function

        # Initialize logger
        self._reorg_logger = ReorganizationLogger(
            config=self._config.logging,
            memory_dir=self._memory_dir,
        )

        # Initialize components
        self._backup_manager = BackupManager(
            memory_dir,
            backup_root=self._config.backup_directory,
        )
        self._analyzer = ConsistencyAnalyzer(memory_dir, self._config.pruning)
        self._pruner = RedundancyPruner(
            memory_dir,
            self._config.pruning,
            reorg_logger=self._reorg_logger,
        )
        self._synthesizer = MemorySynthesizer(
            memory_dir,
            llm_service=self._llm,
            config=self._config.synthesis,
            prompts=self._config.prompts,
            reorg_logger=self._reorg_logger,
            embedding_function=embedding_function,
            collection_name=collection_name,
        )
        self._fact_checker = FactChecker(
            memory_dir,
            classifier_llm=self._classifier_llm,
            researcher_llm=self._researcher_llm,
            judge_llm=self._judge_llm,
            config=self._config.fact_checking,
            prompts=self._config.prompts,
            reorg_logger=self._reorg_logger,
        )

    @property
    def backup_manager(self) -> BackupManager:
        """Get the backup manager."""
        return self._backup_manager

    @property
    def analyzer(self) -> ConsistencyAnalyzer:
        """Get the consistency analyzer."""
        return self._analyzer

    @property
    def pruner(self) -> RedundancyPruner:
        """Get the redundancy pruner."""
        return self._pruner

    @property
    def synthesizer(self) -> MemorySynthesizer:
        """Get the memory synthesizer."""
        return self._synthesizer

    @property
    def fact_checker(self) -> FactChecker:
        """Get the fact checker."""
        return self._fact_checker

    @property
    def reorg_logger(self) -> ReorganizationLogger:
        """Get the reorganization logger."""
        return self._reorg_logger

    @property
    def has_lifecycle_support(self) -> bool:
        """Check if lifecycle components are configured."""
        return self._collection_manager is not None

    @property
    def collection_manager(self) -> "CollectionManager | None":
        """Get the collection manager."""
        return self._collection_manager

    @property
    def access_buffer(self) -> "AccessBuffer | None":
        """Get the access buffer."""
        return self._access_buffer

    @property
    def factor_computer(self) -> "RetrievalFactorComputer | None":
        """Get the factor computer."""
        return self._factor_computer

    async def backup(self, backup_dir: str | Path | None = None):
        """
        Create a backup of all memory stores.

        Args:
            backup_dir: Optional specific backup directory

        Returns:
            BackupManifest
        """
        logger.info("Creating backup...")
        return self._backup_manager.create_backup(backup_dir)

    async def analyze(self) -> ConsistencyReport:
        """
        Analyze memory stores for consistency issues.

        Returns:
            ConsistencyReport
        """
        logger.info("Analyzing consistency...")
        return await self._analyzer.analyze()

    async def prune(
        self,
        dry_run: bool = True,
        backup_first: bool = False,
    ) -> PruneReport:
        """
        Prune redundant and stale memories.

        Args:
            dry_run: If True, report what would be pruned without modifying
            backup_first: If True, create backup before pruning

        Returns:
            PruneReport
        """
        if backup_first and not dry_run:
            logger.info("Creating backup before pruning...")
            self._backup_manager.create_backup()

        logger.info(f"Pruning redundancies (dry_run={dry_run})...")
        return await self._pruner.prune(dry_run=dry_run)

    async def synthesize(
        self,
        dry_run: bool = True,
        backup_first: bool = False,
    ) -> SynthesisReport:
        """
        Synthesize new memories from existing knowledge.

        Args:
            dry_run: If True, report what would be synthesized without storing
            backup_first: If True, create backup before synthesis

        Returns:
            SynthesisReport
        """
        if backup_first and not dry_run:
            logger.info("Creating backup before synthesis...")
            self._backup_manager.create_backup()

        logger.info(f"Synthesizing memories (dry_run={dry_run})...")
        return await self._synthesizer.synthesize(dry_run=dry_run)

    async def classify(
        self,
        limit: int = 100,
        dry_run: bool = True,
    ) -> list:
        """
        Classify facts as falsifiable or conversational.

        Args:
            limit: Maximum number of facts to classify
            dry_run: If True, don't update metadata

        Returns:
            List of ClassifiedFact
        """
        logger.info(f"Classifying up to {limit} facts (dry_run={dry_run})...")
        return await self._fact_checker.classify_facts(limit=limit, dry_run=dry_run)

    async def verify(
        self,
        dry_run: bool = True,
        backup_first: bool = False,
    ) -> VerificationReport:
        """
        Verify falsifiable claims.

        Args:
            dry_run: If True, report what would be verified without updating
            backup_first: If True, create backup before verification

        Returns:
            VerificationReport
        """
        if backup_first and not dry_run:
            logger.info("Creating backup before verification...")
            self._backup_manager.create_backup()

        logger.info(f"Verifying claims (dry_run={dry_run})...")
        return await self._fact_checker.run_full_check(dry_run=dry_run)

    async def lifecycle(
        self,
        dry_run: bool = True,
        backup_first: bool = False,
    ) -> LifecycleReport:
        """
        Run lifecycle maintenance: promotions, decays, and reactivations.

        This step:
        1. Evaluates short-term memories for promotion to long-term
        2. Calculates decay scores for long-term memories
        3. Marks highly-decayed memories as DECAYED
        4. Propagates decay to linked graph nodes

        Args:
            dry_run: If True, report what would change without modifying
            backup_first: If True, create backup before modifications

        Returns:
            LifecycleReport with promotion/decay statistics
        """
        if backup_first and not dry_run:
            logger.info("Creating backup before lifecycle maintenance...")
            self._backup_manager.create_backup()

        report = LifecycleReport(dry_run=dry_run)

        if not self.has_lifecycle_support:
            logger.warning("Lifecycle support not configured, skipping")
            report.errors.append("Lifecycle components not configured")
            return report

        logger.info(f"Running lifecycle maintenance (dry_run={dry_run})...")

        try:
            # Get short-term memories for promotion evaluation
            short_term_results = await self._collection_manager.short_term.get_all(
                limit=1000,
            )

            report.promotions_checked = len(short_term_results)

            # Evaluate each for promotion
            if self._promotion_scorer:
                for memory in short_term_results:
                    memory_id = memory.get("id", "")
                    metadata = memory.get("metadata", {})

                    # Check promotion eligibility
                    score = self._promotion_scorer.score(metadata)
                    if score >= self._config.decay.promotion_threshold:
                        if not dry_run:
                            try:
                                await self._collection_manager.promote_memory(
                                    memory_id=memory_id
                                )
                                report.promotions_executed += 1
                                report.promoted_memory_ids.append(memory_id)
                            except Exception as e:
                                report.promotion_failures += 1
                                report.errors.append(f"Promotion failed for {memory_id}: {e}")
                        else:
                            report.promotions_executed += 1
                            report.promoted_memory_ids.append(memory_id)

            # Get long-term memories for decay evaluation
            long_term_results = await self._collection_manager.long_term.get_all(
                limit=5000,
            )

            report.decays_checked = len(long_term_results)

            # Evaluate each for decay
            if self._decay_calculator:
                decayed_ids = set()
                for memory in long_term_results:
                    memory_id = memory.get("id", "")
                    metadata = memory.get("metadata", {})

                    decay_score = self._decay_calculator.calculate(metadata)
                    if decay_score < self._config.decay.decay_threshold:
                        if not dry_run:
                            try:
                                await self._collection_manager.demote_to_decayed(
                                    memory_id=memory_id
                                )
                                report.decays_executed += 1
                                report.decayed_memory_ids.append(memory_id)
                                decayed_ids.add(memory_id)
                            except Exception as e:
                                report.decay_failures += 1
                                report.errors.append(f"Decay failed for {memory_id}: {e}")
                        else:
                            report.decays_executed += 1
                            report.decayed_memory_ids.append(memory_id)
                            decayed_ids.add(memory_id)

                # Propagate decay to graph nodes
                if self._graph_store and decayed_ids:
                    nodes_decayed = await self._propagate_decay_to_graph(
                        decayed_ids, dry_run
                    )
                    report.graph_nodes_decayed = nodes_decayed

            logger.info(
                f"Lifecycle complete: {report.promotions_executed} promoted, "
                f"{report.decays_executed} decayed, "
                f"{report.graph_nodes_decayed} graph nodes decayed"
            )

        except Exception as e:
            logger.error(f"Lifecycle maintenance failed: {e}")
            report.errors.append(str(e))

        return report

    async def _propagate_decay_to_graph(
        self, decayed_memory_ids: set[str], dry_run: bool
    ) -> int:
        """
        Mark graph nodes as decayed if all their source memories have decayed.

        Args:
            decayed_memory_ids: Set of memory IDs that have decayed
            dry_run: If True, don't actually modify nodes

        Returns:
            Number of nodes marked as decayed
        """
        if not self._graph_store:
            return 0

        nodes_decayed = 0
        try:
            all_nodes = self._graph_store.get_all_nodes()
            for node in all_nodes:
                source_ids = getattr(node, "source_memory_ids", [])
                if not source_ids:
                    continue  # No linkage, skip

                # Check if ALL source memories have decayed
                if all(mid in decayed_memory_ids for mid in source_ids):
                    if not dry_run:
                        node.mark_decayed()
                        # Update in store
                        self._graph_store.remove_node(node.id)
                        self._graph_store.add_node(node)
                    nodes_decayed += 1

        except Exception as e:
            logger.warning(f"Error propagating decay to graph: {e}")

        return nodes_decayed

    async def optimize(
        self,
        dry_run: bool = True,
    ) -> OptimizationReport:
        """
        Run latency optimization: flush access buffer, recompute retrieval factors.

        This step:
        1. Flushes AccessBuffer to batch-update hit_count/decay_score
        2. Recomputes retrieval_factor for all memories
        3. Backfills missing edge embeddings (if embedding function available)

        Args:
            dry_run: If True, report what would change without modifying

        Returns:
            OptimizationReport with optimization statistics
        """
        report = OptimizationReport(dry_run=dry_run)

        if not self.has_lifecycle_support:
            logger.warning("Lifecycle support not configured, skipping optimization")
            report.errors.append("Lifecycle components not configured")
            return report

        logger.info(f"Running latency optimization (dry_run={dry_run})...")

        try:
            # 1. Flush access buffer
            if self._access_buffer:
                start = time.time()
                if not dry_run:
                    flush_result = await self._access_buffer.flush_all(
                        short_term_collection=self._collection_manager.short_term,
                        long_term_collection=self._collection_manager.long_term,
                    )
                    report.short_term_accesses_flushed = flush_result.short_term_updated
                    report.long_term_accesses_flushed = flush_result.long_term_updated
                else:
                    # Report what would be flushed
                    stats = self._access_buffer.get_stats()
                    report.short_term_accesses_flushed = stats.get("short_term_memories", 0)
                    report.long_term_accesses_flushed = stats.get("long_term_memories", 0)

                report.access_buffer_flushed = True
                report.access_flush_duration_ms = (time.time() - start) * 1000
                logger.info(
                    f"Access buffer flushed: {report.short_term_accesses_flushed} short-term, "
                    f"{report.long_term_accesses_flushed} long-term"
                )

            # 2. Recompute retrieval factors
            if self._factor_computer:
                start = time.time()
                if not dry_run:
                    # Compute for short-term
                    st_result = await self._factor_computer.compute_factors(
                        collection=self._collection_manager.short_term,
                    )
                    report.short_term_factors_updated = st_result.memories_updated

                    # Compute for long-term
                    lt_result = await self._factor_computer.compute_factors(
                        collection=self._collection_manager.long_term,
                    )
                    report.long_term_factors_updated = lt_result.memories_updated
                else:
                    # Report what would be updated (all memories)
                    st_results = await self._collection_manager.short_term.get_all(
                        limit=1000
                    )
                    lt_results = await self._collection_manager.long_term.get_all(
                        limit=5000
                    )
                    report.short_term_factors_updated = len(st_results)
                    report.long_term_factors_updated = len(lt_results)

                report.retrieval_factors_computed = True
                report.factor_compute_duration_ms = (time.time() - start) * 1000
                logger.info(
                    f"Retrieval factors computed: {report.short_term_factors_updated} short-term, "
                    f"{report.long_term_factors_updated} long-term"
                )

            # 3. Backfill missing edge embeddings
            logger.info(
                f"Edge embedding check: graph_store={self._graph_store is not None}, "
                f"embedding_function={self._embedding_function is not None}"
            )
            if self._graph_store and self._embedding_function:
                start = time.time()
                edges_embedded, edges_skipped = await self._backfill_edge_embeddings(
                    dry_run
                )
                report.edges_embedded = edges_embedded
                report.edges_skipped = edges_skipped
                report.edge_embeddings_backfilled = True
                report.edge_embed_duration_ms = (time.time() - start) * 1000
                logger.info(
                    f"Edge embeddings backfilled: {edges_embedded} embedded, "
                    f"{edges_skipped} skipped"
                )
            else:
                logger.warning(
                    f"Skipping edge embedding backfill: "
                    f"graph_store={self._graph_store is not None}, "
                    f"embedding_function={self._embedding_function is not None}"
                )

            logger.info("Optimization complete")

        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            report.errors.append(str(e))

        return report

    async def _backfill_edge_embeddings(self, dry_run: bool) -> tuple[int, int]:
        """
        Backfill missing edge embeddings.

        Args:
            dry_run: If True, don't actually modify edges

        Returns:
            Tuple of (edges_embedded, edges_skipped)
        """
        if not self._graph_store or not self._embedding_function:
            return 0, 0

        edges_embedded = 0
        edges_skipped = 0

        try:
            # Get all edges directly
            all_edges = await self._graph_store.get_all_edges()
            logger.info(f"Edge backfill: found {len(all_edges)} total edges")

            # Collect edges that need embeddings
            edges_needing_embeddings: list[tuple[str, str, str]] = []  # (source, target, relation_text)

            for edge in all_edges:
                if edge.embedding is not None:
                    edges_skipped += 1
                    continue

                relation_text = edge.get_relation_text()
                edges_needing_embeddings.append((edge.source_id, edge.target_id, relation_text))

            logger.info(
                f"Edge backfill: {len(edges_needing_embeddings)} need embeddings, "
                f"{edges_skipped} already have embeddings"
            )

            if not edges_needing_embeddings:
                return 0, edges_skipped

            edges_embedded = len(edges_needing_embeddings)

            if not dry_run:
                # Batch compute embeddings for efficiency
                relation_texts = [e[2] for e in edges_needing_embeddings]

                # Process in batches to avoid overwhelming the embedding API
                batch_size = 100
                edges_with_embeddings: list[tuple[str, str, list[float]]] = []

                for i in range(0, len(relation_texts), batch_size):
                    batch_texts = relation_texts[i : i + batch_size]
                    batch_edges = edges_needing_embeddings[i : i + batch_size]

                    embeddings = await self._embedding_function.embed_documents(batch_texts)

                    if embeddings:
                        for (source_id, target_id, _), embedding in zip(batch_edges, embeddings):
                            edges_with_embeddings.append((source_id, target_id, embedding))

                # Batch update all edges
                if edges_with_embeddings:
                    updated = await self._graph_store.update_edges_embeddings(edges_with_embeddings)
                    logger.info(f"Updated {updated} edge embeddings")

        except Exception as e:
            logger.warning(f"Error backfilling edge embeddings: {e}")

        return edges_embedded, edges_skipped

    async def cleanup(
        self,
        dry_run: bool = True,
        backup_first: bool = False,
    ) -> CleanupReport:
        """
        Hard delete expired decayed memories and cleanup orphaned graph nodes.

        This step:
        1. Permanently removes memories that have been in DECAYED state beyond
           decayed_retention_days (default 30 days)
        2. Removes graph nodes whose ALL source memories have been deleted

        Args:
            dry_run: If True, report what would be deleted without modifying
            backup_first: If True, create backup before modifications

        Returns:
            CleanupReport with deletion statistics
        """
        if backup_first and not dry_run:
            logger.info("Creating backup before cleanup...")
            self._backup_manager.create_backup()

        report = CleanupReport(
            dry_run=dry_run,
            retention_days=self._config.decay.decayed_retention_days,
        )

        if not self.has_lifecycle_support:
            logger.warning("Lifecycle support not configured, skipping cleanup")
            report.errors.append("Lifecycle components not configured")
            return report

        logger.info(
            f"Running cleanup (dry_run={dry_run}, "
            f"retention_days={self._config.decay.decayed_retention_days})..."
        )

        try:
            # 1. Hard delete expired memories
            delete_result = await self._collection_manager.hard_delete_expired(
                retention_days=self._config.decay.decayed_retention_days,
                dry_run=dry_run,
            )

            report.memories_deleted = delete_result.get("deleted_count", 0)
            report.deleted_memory_ids = delete_result.get("deleted_ids", [])

            if delete_result.get("error"):
                report.errors.append(delete_result["error"])

            # 2. Cleanup orphaned graph nodes
            if (
                report.deleted_memory_ids
                and self._graph_store
                and not delete_result.get("error")
            ):
                cleanup_result = await self._collection_manager.cleanup_orphaned_graph_nodes(
                    deleted_memory_ids=set(report.deleted_memory_ids),
                    graph_store=self._graph_store,
                    dry_run=dry_run,
                )

                report.graph_nodes_deleted = cleanup_result.get("deleted_count", 0)
                report.deleted_node_ids = cleanup_result.get("deleted_node_ids", [])

                if cleanup_result.get("error"):
                    report.errors.append(cleanup_result["error"])

            logger.info(
                f"Cleanup complete: {report.memories_deleted} memories deleted, "
                f"{report.graph_nodes_deleted} graph nodes cleaned up"
            )

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            report.errors.append(str(e))

        return report

    async def dedupe_insights(
        self,
        dry_run: bool = True,
    ) -> DeduplicationReport:
        """
        Deduplicate insights by clustering similar ones.

        For each cluster of similar insights, keeps the most recent one
        and marks others with `superseded_by` metadata.

        This is a batch operation intended to be run during reorganization
        to reduce redundancy in the insight store.

        Args:
            dry_run: If True, only report what would be done without modifying

        Returns:
            DeduplicationReport with statistics and cluster details
        """
        report = DeduplicationReport(dry_run=dry_run)
        logger.info(f"Running insight deduplication (dry_run={dry_run})...")

        try:
            # Get all insights from vector store
            if not self._synthesizer:
                report.errors.append("Synthesizer not configured")
                return report

            vector_store = self._synthesizer._vector_store
            if not vector_store:
                report.errors.append("Vector store not available")
                return report

            # Fetch all insights
            all_insights = await vector_store.get_all(
                limit=10000,
                where={"type": "insight"},
            )

            report.insights_scanned = len(all_insights)

            if len(all_insights) < 2:
                logger.info("Not enough insights to deduplicate")
                return report

            # Build clusters by entity signature
            clusters: dict[frozenset[str], list[dict[str, Any]]] = {}

            for insight in all_insights:
                entities = self._extract_insight_entities(insight)
                if not entities:
                    continue  # Can't cluster without entity signature

                entity_key = frozenset(entities)
                if entity_key not in clusters:
                    clusters[entity_key] = []
                clusters[entity_key].append(insight)

            # Process each cluster
            for entity_key, insights in clusters.items():
                if len(insights) < 2:
                    continue  # No duplicates

                # Sort by recency (most recent first)
                insights.sort(
                    key=lambda x: x.get("metadata", {}).get("created_at", ""),
                    reverse=True,
                )

                # Keep the first (most recent), mark others as superseded
                primary = insights[0]
                primary_id = primary.get("id", "")
                superseded_ids = []

                for secondary in insights[1:]:
                    secondary_id = secondary.get("id", "")
                    if not secondary_id:
                        continue

                    superseded_ids.append(secondary_id)

                    if not dry_run:
                        # Update metadata to mark as superseded
                        try:
                            metadata = secondary.get("metadata", {})
                            metadata["superseded_by"] = primary_id
                            await vector_store.update(
                                secondary_id, metadata=metadata
                            )
                        except Exception as e:
                            report.errors.append(
                                f"Failed to mark {secondary_id} as superseded: {e}"
                            )

                # Record cluster
                cluster = InsightCluster(
                    cluster_id=str(uuid.uuid4())[:8],
                    primary_insight_id=primary_id,
                    superseded_ids=superseded_ids,
                    entity_key=";".join(sorted(entity_key)),
                )
                report.clusters.append(cluster)
                report.insights_superseded += len(superseded_ids)

            report.clusters_found = len(report.clusters)

            logger.info(
                f"Deduplication complete: {report.clusters_found} clusters found, "
                f"{report.insights_superseded} insights superseded"
            )

        except Exception as e:
            logger.error(f"Insight deduplication failed: {e}")
            report.errors.append(str(e))

        return report

    def _extract_insight_entities(self, insight: dict[str, Any]) -> set[str]:
        """
        Extract entity mentions from an insight for clustering.

        Args:
            insight: Insight dict with text and metadata

        Returns:
            Set of normalized entity names
        """
        entities: set[str] = set()
        metadata = insight.get("metadata", {})

        # Primary: use entities_mentioned if available (semicolon-separated)
        entities_mentioned = metadata.get("entities_mentioned", "")
        if entities_mentioned:
            for entity in entities_mentioned.split(";"):
                entity = entity.strip().lower()
                if entity:
                    entities.add(entity)

        # Secondary: extract proper nouns from text
        if not entities:
            text = insight.get("text", "") or insight.get("document", "")
            words = text.split()
            for word in words:
                clean_word = word.strip(".,!?\"'()[]")
                if (
                    clean_word
                    and clean_word[0].isupper()
                    and len(clean_word) > 2
                    and clean_word.lower()
                    not in {"the", "this", "that", "they", "their"}
                ):
                    entities.add(clean_word.lower())

        return entities

    async def reorganize(
        self,
        backup_first: bool = True,
        dry_run: bool = True,
        skip_synthesis: bool = False,
        skip_verify: bool = False,
        skip_lifecycle: bool = False,
    ) -> ReorganizationReport:
        """
        Run full reorganization pipeline.

        Pipeline:
        1. Backup (if requested)
        2. Analyze consistency
        3. Prune redundancies
        4. Synthesize new memories (if not skipped)
        5. Classify and verify facts (if not skipped)
        6. Lifecycle maintenance: promotions/decays (if not skipped)
        7. Latency optimization: flush buffers, recompute factors (if not skipped)
        8. Cleanup: hard delete expired decayed memories (if not skipped)

        Args:
            backup_first: Create backup before any modifications
            dry_run: If True, don't actually modify anything
            skip_synthesis: Skip the synthesis step
            skip_verify: Skip the verification step
            skip_lifecycle: Skip the lifecycle, optimization, and cleanup steps

        Returns:
            ReorganizationReport with all sub-reports
        """
        total_steps = 8
        logger.info(
            f"Starting full reorganization "
            f"(backup_first={backup_first}, dry_run={dry_run})"
        )

        # Set dry_run state on logger for all subsequent entries
        self._reorg_logger.set_dry_run(dry_run)

        report = ReorganizationReport(memory_dir=str(self._memory_dir))
        log_path = None

        try:
            # 1. Backup
            if backup_first and not dry_run:
                logger.info(f"Step 1/{total_steps}: Creating backup...")
                report.backup_manifest = self._backup_manager.create_backup()
                # Log the backup action
                self._reorg_logger.log_backup_created(
                    backup_id=report.backup_manifest.backup_id,
                    backup_dir=report.backup_manifest.backup_dir,
                    file_count=len(report.backup_manifest.files),
                    metadata={"store_stats": report.backup_manifest.store_stats},
                )
            else:
                logger.info(f"Step 1/{total_steps}: Skipping backup (dry_run or not requested)")

            # 2. Analyze
            logger.info(f"Step 2/{total_steps}: Analyzing consistency...")
            report.consistency_report = await self._analyzer.analyze()

            # 3. Prune
            logger.info(f"Step 3/{total_steps}: Pruning redundancies...")
            report.prune_report = await self._pruner.prune(dry_run=dry_run)

            # 4. Synthesize
            if not skip_synthesis:
                logger.info(f"Step 4/{total_steps}: Synthesizing memories...")
                report.synthesis_report = await self._synthesizer.synthesize(
                    dry_run=dry_run
                )
            else:
                logger.info(f"Step 4/{total_steps}: Skipping synthesis")

            # 5. Verify
            if not skip_verify:
                logger.info(f"Step 5/{total_steps}: Verifying facts...")
                report.verification_report = await self._fact_checker.run_full_check(
                    dry_run=dry_run
                )
            else:
                logger.info(f"Step 5/{total_steps}: Skipping verification")

            # 6. Lifecycle maintenance (Phase 8)
            if not skip_lifecycle and self.has_lifecycle_support:
                logger.info(f"Step 6/{total_steps}: Running lifecycle maintenance...")
                report.lifecycle_report = await self.lifecycle(dry_run=dry_run)
            else:
                if skip_lifecycle:
                    logger.info(f"Step 6/{total_steps}: Skipping lifecycle (--skip-lifecycle)")
                else:
                    logger.info(f"Step 6/{total_steps}: Skipping lifecycle (not configured)")

            # 7. Latency optimization (Phase 8)
            if not skip_lifecycle and self.has_lifecycle_support:
                logger.info(f"Step 7/{total_steps}: Running latency optimization...")
                report.optimization_report = await self.optimize(dry_run=dry_run)
            else:
                if skip_lifecycle:
                    logger.info(f"Step 7/{total_steps}: Skipping optimization (--skip-lifecycle)")
                else:
                    logger.info(f"Step 7/{total_steps}: Skipping optimization (not configured)")

            # 8. Cleanup: hard delete expired decayed memories
            if not skip_lifecycle and self.has_lifecycle_support:
                logger.info(f"Step 8/{total_steps}: Running cleanup (hard delete expired)...")
                report.cleanup_report = await self.cleanup(dry_run=dry_run)
            else:
                if skip_lifecycle:
                    logger.info(f"Step 8/{total_steps}: Skipping cleanup (--skip-lifecycle)")
                else:
                    logger.info(f"Step 8/{total_steps}: Skipping cleanup (not configured)")

            report.complete(success=True)
            logger.info("Reorganization complete!")

        except Exception as e:
            logger.error(f"Reorganization failed: {e}")
            report.errors.append(str(e))
            report.complete(success=False)

        finally:
            # Write the reorganization log
            log_path = self._reorg_logger.write_log()
            if log_path:
                logger.info(f"Reorganization log written to: {log_path}")

        return report

    def generate_report_summary(self, report: ReorganizationReport) -> str:
        """
        Generate a comprehensive summary of the reorganization.

        Args:
            report: The reorganization report

        Returns:
            Formatted summary string
        """
        lines = [
            "=" * 70,
            "MEMORY REORGANIZATION REPORT",
            "=" * 70,
            f"Memory Directory: {report.memory_dir}",
            f"Started: {report.started_at.isoformat()}",
            f"Completed: {report.completed_at.isoformat() if report.completed_at else 'N/A'}",
            f"Success: {report.success}",
            "",
        ]

        # Backup info
        if report.backup_manifest:
            lines.extend([
                "BACKUP:",
                f"  ID: {report.backup_manifest.backup_id[:8]}...",
                f"  Location: {report.backup_manifest.backup_dir}",
                f"  Files: {len(report.backup_manifest.files)}",
                "",
            ])

        # Consistency summary
        if report.consistency_report:
            cr = report.consistency_report
            lines.extend([
                "CONSISTENCY ANALYSIS:",
                f"  Graph: {cr.graph_stats.get('node_count', 0)} nodes, "
                f"{cr.graph_stats.get('edge_count', 0)} edges",
                f"  Issues: {len(cr.issues)} "
                f"(critical={cr.severity_counts['critical']}, "
                f"warning={cr.severity_counts['warning']})",
                "",
            ])

        # Prune summary
        if report.prune_report:
            pr = report.prune_report
            status = "DRY RUN" if pr.dry_run else "EXECUTED"
            lines.extend([
                f"PRUNING ({status}):",
                f"  Insights removed: {pr.insights_removed}",
                f"  Entities merged: {pr.entities_merged}",
                f"  Entities removed: {pr.entities_removed}",
                "",
            ])

        # Synthesis summary
        if report.synthesis_report:
            sr = report.synthesis_report
            status = "DRY RUN" if sr.dry_run else "EXECUTED"
            lines.extend([
                f"SYNTHESIS ({status}):",
                f"  Clusters found: {sr.clusters_found}",
                f"  Meta-insights: {sr.meta_insights_created}",
                f"  Relationships inferred: {sr.relationships_inferred}",
                f"  Knowledge gaps: {sr.gaps_identified}",
                "",
            ])

        # Verification summary
        if report.verification_report:
            vr = report.verification_report
            status = "DRY RUN" if vr.dry_run else "EXECUTED"
            lines.extend([
                f"FACT VERIFICATION ({status}):",
                f"  Total claims: {vr.total_claims}",
                f"  Verified true: {vr.verified_true}",
                f"  Disputed: {vr.verified_false}",
                f"  Unverifiable: {vr.unverifiable}",
                f"  Conversational (skipped): {vr.skipped_conversational}",
                "",
            ])

        # Lifecycle summary
        if report.lifecycle_report:
            lr = report.lifecycle_report
            status = "DRY RUN" if lr.dry_run else "EXECUTED"
            lines.extend([
                f"LIFECYCLE MAINTENANCE ({status}):",
                f"  Promotions: {lr.promotions_executed}/{lr.promotions_checked} checked",
                f"  Decays: {lr.decays_executed}/{lr.decays_checked} checked",
                f"  Graph nodes decayed: {lr.graph_nodes_decayed}",
                "",
            ])

        # Optimization summary
        if report.optimization_report:
            opr = report.optimization_report
            status = "DRY RUN" if opr.dry_run else "EXECUTED"
            lines.extend([
                f"LATENCY OPTIMIZATION ({status}):",
                f"  Access buffer: {opr.short_term_accesses_flushed} ST, "
                f"{opr.long_term_accesses_flushed} LT flushed",
                f"  Retrieval factors: {opr.short_term_factors_updated} ST, "
                f"{opr.long_term_factors_updated} LT updated",
                f"  Edge embeddings: {opr.edges_embedded} embedded, "
                f"{opr.edges_skipped} skipped",
                "",
            ])

        # Cleanup summary
        if report.cleanup_report:
            cr = report.cleanup_report
            status = "DRY RUN" if cr.dry_run else "EXECUTED"
            lines.extend([
                f"CLEANUP ({status}):",
                f"  Retention days: {cr.retention_days}",
                f"  Memories hard deleted: {cr.memories_deleted}",
                f"  Graph nodes cleaned up: {cr.graph_nodes_deleted}",
                "",
            ])

        # Errors
        if report.errors:
            lines.extend([
                "ERRORS:",
                *[f"  - {error}" for error in report.errors],
                "",
            ])

        lines.append("=" * 70)

        return "\n".join(lines)
