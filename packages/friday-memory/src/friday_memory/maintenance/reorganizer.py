"""
Memory Reorganizer Orchestrator.

Main entry point for coordinating all maintenance operations:
- Backup
- Analyze
- Prune
- Synthesize
- Verify
- Full reorganization
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from friday_memory.maintenance.analyzer import ConsistencyAnalyzer
from friday_memory.maintenance.backup import BackupManager
from friday_memory.maintenance.fact_checker import FactChecker
from friday_memory.maintenance.logger import ReorganizationLogger
from friday_memory.maintenance.models import (
    ConsistencyReport,
    MaintenanceConfig,
    PruneReport,
    ReorganizationReport,
    SynthesisReport,
    VerificationReport,
)
from friday_memory.maintenance.pruner import RedundancyPruner
from friday_memory.maintenance.synthesizer import MemorySynthesizer

if TYPE_CHECKING:
    from friday_llm import LiteLLMService

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
        embedding_function: any = None,
        collection_name: str | None = None,
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
        """
        self._memory_dir = Path(memory_dir)
        self._config = config or MaintenanceConfig()

        # Use provided LLMs or fall back to default
        self._llm = llm_service
        self._classifier_llm = classifier_llm or llm_service
        self._researcher_llm = researcher_llm or llm_service
        self._judge_llm = judge_llm or llm_service

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

    async def reorganize(
        self,
        backup_first: bool = True,
        dry_run: bool = True,
        skip_synthesis: bool = False,
        skip_verify: bool = False,
    ) -> ReorganizationReport:
        """
        Run full reorganization pipeline.

        Pipeline:
        1. Backup (if requested)
        2. Analyze consistency
        3. Prune redundancies
        4. Synthesize new memories (if not skipped)
        5. Classify and verify facts (if not skipped)

        Args:
            backup_first: Create backup before any modifications
            dry_run: If True, don't actually modify anything
            skip_synthesis: Skip the synthesis step
            skip_verify: Skip the verification step

        Returns:
            ReorganizationReport with all sub-reports
        """
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
                logger.info("Step 1/5: Creating backup...")
                report.backup_manifest = self._backup_manager.create_backup()
                # Log the backup action
                self._reorg_logger.log_backup_created(
                    backup_id=report.backup_manifest.backup_id,
                    backup_dir=report.backup_manifest.backup_dir,
                    file_count=len(report.backup_manifest.files),
                    metadata={"store_stats": report.backup_manifest.store_stats},
                )
            else:
                logger.info("Step 1/5: Skipping backup (dry_run or not requested)")

            # 2. Analyze
            logger.info("Step 2/5: Analyzing consistency...")
            report.consistency_report = await self._analyzer.analyze()

            # 3. Prune
            logger.info("Step 3/5: Pruning redundancies...")
            report.prune_report = await self._pruner.prune(dry_run=dry_run)

            # 4. Synthesize
            if not skip_synthesis:
                logger.info("Step 4/5: Synthesizing memories...")
                report.synthesis_report = await self._synthesizer.synthesize(
                    dry_run=dry_run
                )
            else:
                logger.info("Step 4/5: Skipping synthesis")

            # 5. Verify
            if not skip_verify:
                logger.info("Step 5/5: Verifying facts...")
                report.verification_report = await self._fact_checker.run_full_check(
                    dry_run=dry_run
                )
            else:
                logger.info("Step 5/5: Skipping verification")

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

        # Errors
        if report.errors:
            lines.extend([
                "ERRORS:",
                *[f"  - {error}" for error in report.errors],
                "",
            ])

        lines.append("=" * 70)

        return "\n".join(lines)
