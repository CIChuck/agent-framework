"""
Consistency Analyzer for Friday Memory.

Analyzes cross-store consistency and identifies issues:
- Orphaned graph references
- Duplicate entities
- Stale/obsolete data
- Cross-store inconsistencies
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from friday_memory.maintenance.models import (
    ConsistencyIssue,
    ConsistencyReport,
    DuplicateGroup,
    IssueSeverity,
    IssueType,
    PruneConfig,
)

logger = logging.getLogger(__name__)


class ConsistencyAnalyzer:
    """
    Analyzes memory stores for consistency issues.

    Performs read-only analysis across Graph, Vector, and Episodic stores
    to identify:
    - Orphaned references
    - Duplicate entities
    - Stale data
    - Cross-store inconsistencies

    Example:
        analyzer = ConsistencyAnalyzer(memory_dir="./memory")
        report = await analyzer.analyze()
        print(f"Found {len(report.issues)} issues")
    """

    def __init__(
        self,
        memory_dir: str | Path,
        config: PruneConfig | None = None,
    ) -> None:
        """
        Initialize the analyzer.

        Args:
            memory_dir: Directory containing memory stores
            config: Configuration for staleness thresholds
        """
        self._memory_dir = Path(memory_dir)
        self._config = config or PruneConfig()

        # Cache for loaded data
        self._graph_data: dict[str, Any] | None = None
        self._transcript_turn_ids: set[str] | None = None

    def _load_graph(self) -> dict[str, Any]:
        """Load and cache graph data."""
        if self._graph_data is not None:
            return self._graph_data

        graph_path = self._memory_dir / "graph.json"
        if not graph_path.exists():
            self._graph_data = {"nodes": {}, "edges": []}
            return self._graph_data

        try:
            with open(graph_path) as f:
                self._graph_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load graph: {e}")
            self._graph_data = {"nodes": {}, "edges": []}

        return self._graph_data

    def _load_transcript_turn_ids(self) -> set[str]:
        """Load turn IDs from transcript database."""
        if self._transcript_turn_ids is not None:
            return self._transcript_turn_ids

        self._transcript_turn_ids = set()

        # Check both possible locations
        transcript_paths = [
            self._memory_dir / "vector" / "transcript.db",
            self._memory_dir / "transcript.db",
        ]

        for transcript_path in transcript_paths:
            if transcript_path.exists():
                try:
                    conn = sqlite3.connect(transcript_path)
                    # Try 'entries' table (friday-transcript) first, fall back to 'turns'  # noqa: E501
                    for table_name in ["entries", "turns"]:
                        try:
                            cursor = conn.execute(f"SELECT id FROM {table_name}")
                            self._transcript_turn_ids = {
                                row[0] for row in cursor.fetchall()
                            }
                            break
                        except sqlite3.Error:
                            continue
                    conn.close()
                    if self._transcript_turn_ids:
                        break
                except sqlite3.Error as e:
                    logger.warning(
                        f"Failed to read transcript from {transcript_path}: {e}"
                    )

        return self._transcript_turn_ids

    def _get_vector_collection_data(self) -> tuple[list[dict], dict[str, int]]:
        """
        Get data from ChromaDB vector store.

        Returns:
            Tuple of (documents list, stats dict)
        """
        documents: list[dict] = []
        stats = {"insight_count": 0, "summary_count": 0, "total": 0}

        # Try both possible locations for ChromaDB
        chroma_db = None
        for vector_dir in [self._memory_dir, self._memory_dir / "vector"]:
            candidate = vector_dir / "chroma.sqlite3"
            if candidate.exists():
                chroma_db = candidate
                break

        if not chroma_db:
            return documents, stats

        try:
            conn = sqlite3.connect(chroma_db)

            # Get embeddings_queue or similar table
            # ChromaDB schema varies by version, try common patterns
            try:
                # Try to get documents from embeddings table
                cursor = conn.execute("""
                    SELECT id, document, metadata
                    FROM embeddings
                    WHERE document IS NOT NULL
                """)
                for row in cursor.fetchall():
                    doc_id, text, metadata_str = row
                    metadata = json.loads(metadata_str) if metadata_str else {}
                    documents.append(
                        {
                            "id": doc_id,
                            "text": text,
                            "metadata": metadata,
                        }
                    )
                    doc_type = metadata.get("type", "unknown")
                    if doc_type == "insight":
                        stats["insight_count"] += 1
                    elif doc_type == "summary":
                        stats["summary_count"] += 1
                    stats["total"] += 1
            except sqlite3.Error:
                # Try alternative table structure
                try:
                    cursor = conn.execute("""
                        SELECT embedding_id
                        FROM embedding_metadata
                    """)
                    stats["total"] = len(cursor.fetchall())
                except sqlite3.Error:
                    pass

            conn.close()
        except Exception as e:
            logger.warning(f"Failed to read vector store: {e}")

        return documents, stats

    def _get_episodic_stats(self) -> dict[str, int]:
        """Get statistics from episodic store."""
        stats = {
            "turn_count": 0,
            "consolidated_count": 0,
            "session_count": 0,
        }

        transcript_paths = [
            self._memory_dir / "vector" / "transcript.db",
            self._memory_dir / "transcript.db",
        ]

        for transcript_path in transcript_paths:
            if transcript_path.exists():
                try:
                    conn = sqlite3.connect(transcript_path)

                    # Try 'entries' table (friday-transcript) first, fall back to 'turns'  # noqa: E501
                    table_name = None
                    for tbl in ["entries", "turns"]:
                        try:
                            cursor = conn.execute(f"SELECT COUNT(*) FROM {tbl}")
                            stats["turn_count"] = cursor.fetchone()[0]
                            table_name = tbl
                            break
                        except sqlite3.Error:
                            continue

                    if table_name:
                        # Count consolidated (if column exists)
                        try:
                            cursor = conn.execute(
                                f"SELECT COUNT(*) FROM {table_name} WHERE consolidated = 1"  # noqa: E501
                            )
                            stats["consolidated_count"] = cursor.fetchone()[0]
                        except sqlite3.Error:
                            pass

                        # Count sessions
                        try:
                            cursor = conn.execute(
                                f"SELECT COUNT(DISTINCT session_id) FROM {table_name}"
                            )
                            stats["session_count"] = cursor.fetchone()[0]
                        except sqlite3.Error:
                            pass

                    conn.close()
                    break
                except sqlite3.Error as e:
                    logger.warning(f"Failed to get episodic stats: {e}")

        return stats

    def _find_orphaned_edges(self, graph_data: dict) -> list[ConsistencyIssue]:
        """Find edges that reference non-existent nodes."""
        issues: list[ConsistencyIssue] = []
        node_ids = set(graph_data.get("nodes", {}).keys())

        for edge in graph_data.get("edges", []):
            source = edge.get("source")
            target = edge.get("target")

            orphaned = []
            if source and source not in node_ids:
                orphaned.append(f"source '{source}'")
            if target and target not in node_ids:
                orphaned.append(f"target '{target}'")

            if orphaned:
                issues.append(
                    ConsistencyIssue(
                        issue_type=IssueType.ORPHANED_EDGE,
                        severity=IssueSeverity.CRITICAL,
                        description=f"Edge has orphaned {', '.join(orphaned)}",
                        affected_ids=[source or "", target or ""],
                        store="graph",
                        suggested_action="Delete the orphaned edge",
                    )
                )

        return issues

    def _find_orphaned_provenance(self, graph_data: dict) -> list[ConsistencyIssue]:
        """Find nodes with provenance source_ids that don't exist in transcript."""
        issues: list[ConsistencyIssue] = []
        turn_ids = self._load_transcript_turn_ids()

        # Skip if no transcript data
        if not turn_ids:
            return issues

        for node_id, node_data in graph_data.get("nodes", {}).items():
            provenance = node_data.get("provenance", {})
            source_id = provenance.get("source_id")
            source_type = provenance.get("source_type", "")

            # Only check interaction-based provenance
            if source_type == "interaction" and source_id and source_id not in turn_ids:
                issues.append(
                    ConsistencyIssue(
                        issue_type=IssueType.ORPHANED_PROVENANCE,
                        severity=IssueSeverity.WARNING,
                        description=f"Node '{node_id}' references non-existent turn '{source_id}'",  # noqa: E501
                        affected_ids=[node_id, source_id],
                        store="graph",
                        suggested_action="Update provenance or mark as orphaned",
                    )
                )

        return issues

    def _find_duplicate_entities(self, graph_data: dict) -> list[DuplicateGroup]:
        """Find duplicate entities based on label similarity."""
        duplicates: list[DuplicateGroup] = []
        nodes = graph_data.get("nodes", {})

        # Group by normalized label
        label_groups: dict[str, list[str]] = {}
        for node_id, node_data in nodes.items():
            label = node_data.get("label", "").lower().strip()
            if label:
                if label not in label_groups:
                    label_groups[label] = []
                label_groups[label].append(node_id)

        # Find exact duplicates
        for label, node_ids in label_groups.items():  # noqa: B007
            if len(node_ids) > 1:
                # Determine primary by hit_count
                primary = max(node_ids, key=lambda nid: nodes[nid].get("hit_count", 0))
                duplicates.append(
                    DuplicateGroup(
                        primary_id=primary,
                        duplicate_ids=[nid for nid in node_ids if nid != primary],
                        similarity_scores={
                            nid: 1.0 for nid in node_ids if nid != primary
                        },
                        match_type="exact",
                    )
                )

        # Find fuzzy duplicates (>0.85 similarity)
        checked_pairs: set[tuple[str, str]] = set()
        all_labels = list(label_groups.keys())

        for i, label1 in enumerate(all_labels):
            for label2 in all_labels[i + 1 :]:
                if (label1, label2) in checked_pairs:
                    continue
                checked_pairs.add((label1, label2))

                similarity = SequenceMatcher(None, label1, label2).ratio()
                if similarity >= 0.85 and similarity < 1.0:
                    # Get node IDs for both labels
                    ids1 = label_groups[label1]
                    ids2 = label_groups[label2]

                    # Primary is from first group (arbitrary for fuzzy)
                    primary = ids1[0]
                    dup_ids = ids1[1:] + ids2

                    if dup_ids:
                        duplicates.append(
                            DuplicateGroup(
                                primary_id=primary,
                                duplicate_ids=dup_ids,
                                similarity_scores={nid: similarity for nid in dup_ids},
                                match_type="fuzzy",
                            )
                        )

        return duplicates

    def _find_stale_entities(self, graph_data: dict) -> list[ConsistencyIssue]:
        """Find entities that are stale based on hit_count and last_accessed."""
        issues: list[ConsistencyIssue] = []
        threshold_date = datetime.now() - timedelta(
            days=self._config.stale_threshold_days
        )

        for node_id, node_data in graph_data.get("nodes", {}).items():
            hit_count = node_data.get("hit_count", 0)

            if hit_count >= self._config.min_hit_count:
                continue

            # Check last_accessed
            last_accessed_str = node_data.get("last_accessed")
            if last_accessed_str:
                try:
                    # Handle various datetime formats
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
                        issues.append(
                            ConsistencyIssue(
                                issue_type=IssueType.STALE_ENTITY,
                                severity=IssueSeverity.INFO,
                                description=(
                                    f"Entity '{label}' is stale: "
                                    f"hit_count={hit_count}, "
                                    f"last_accessed={last_accessed.date()}"
                                ),
                                affected_ids=[node_id],
                                store="graph",
                                suggested_action="Consider pruning this entity",
                            )
                        )
                except (ValueError, TypeError):
                    pass

        return issues

    def _find_stale_edges(self, graph_data: dict) -> list[ConsistencyIssue]:
        """Find edges that are stale based on hit_count and last_accessed."""
        issues: list[ConsistencyIssue] = []
        threshold_date = datetime.now() - timedelta(
            days=self._config.stale_threshold_days
        )

        for edge in graph_data.get("edges", []):
            hit_count = edge.get("hit_count", 0)

            if hit_count >= self._config.min_hit_count:
                continue

            # Check last_accessed
            last_accessed_str = edge.get("last_accessed")

            # Skip edges without last_accessed (pre-migration edges)
            # These need migration first, not pruning
            if not last_accessed_str:
                continue

            try:
                # Handle various datetime formats
                if "T" in last_accessed_str:
                    last_accessed = datetime.fromisoformat(
                        last_accessed_str.replace("Z", "+00:00")
                    )
                else:
                    last_accessed = datetime.strptime(
                        last_accessed_str, "%Y-%m-%d %H:%M:%S"
                    )

                if last_accessed < threshold_date:
                    source = edge.get("source", "")
                    target = edge.get("target", "")
                    relation = edge.get("relation", "related_to")
                    issues.append(
                        ConsistencyIssue(
                            issue_type=IssueType.STALE_EDGE,
                            severity=IssueSeverity.INFO,
                            description=(
                                f"Edge '{source}' --[{relation}]--> '{target}' is stale: "  # noqa: E501
                                f"hit_count={hit_count}, "
                                f"last_accessed={last_accessed.date()}"
                            ),
                            affected_ids=[source, target],
                            store="graph",
                            suggested_action="Consider pruning this edge",
                        )
                    )
            except (ValueError, TypeError):
                pass

        return issues

    def _find_cross_store_issues(
        self,
        graph_data: dict,
        vector_docs: list[dict],
    ) -> list[ConsistencyIssue]:
        """Find inconsistencies between stores."""
        issues: list[ConsistencyIssue] = []

        # Get all entity labels from graph
        graph_labels = {
            node_data.get("label", "").lower()
            for node_data in graph_data.get("nodes", {}).values()
        }

        # Check vector documents for entity references
        for doc in vector_docs:
            metadata = doc.get("metadata", {})
            entities = metadata.get("entities", [])

            for entity in entities:
                entity_lower = entity.lower() if isinstance(entity, str) else ""
                if entity_lower and entity_lower not in graph_labels:
                    issues.append(
                        ConsistencyIssue(
                            issue_type=IssueType.CROSS_STORE_MISMATCH,
                            severity=IssueSeverity.WARNING,
                            description=(
                                f"Insight references entity '{entity}' "
                                f"not found in graph"
                            ),
                            affected_ids=[doc.get("id", ""), entity],
                            store="vector",
                            suggested_action="Add entity to graph or update insight",
                        )
                    )

        return issues

    async def analyze(self) -> ConsistencyReport:
        """
        Perform full consistency analysis.

        Returns:
            ConsistencyReport with all findings
        """
        logger.info(f"Starting consistency analysis of {self._memory_dir}")

        report = ConsistencyReport(
            memory_dir=str(self._memory_dir),
        )

        # Load data
        graph_data = self._load_graph()
        vector_docs, vector_stats = self._get_vector_collection_data()
        episodic_stats = self._get_episodic_stats()

        # Populate stats
        report.graph_stats = {
            "node_count": len(graph_data.get("nodes", {})),
            "edge_count": len(graph_data.get("edges", [])),
        }
        report.vector_stats = vector_stats
        report.episodic_stats = episodic_stats

        # Find issues
        logger.debug("Checking for orphaned edges...")
        for issue in self._find_orphaned_edges(graph_data):
            report.add_issue(issue)

        logger.debug("Checking for orphaned provenance...")
        for issue in self._find_orphaned_provenance(graph_data):
            report.add_issue(issue)

        logger.debug("Finding duplicate entities...")
        report.duplicate_groups = self._find_duplicate_entities(graph_data)
        for group in report.duplicate_groups:
            report.add_issue(
                ConsistencyIssue(
                    issue_type=IssueType.DUPLICATE_ENTITY,
                    severity=IssueSeverity.WARNING,
                    description=(
                        f"Duplicate entities found ({group.match_type}): "
                        f"{group.primary_id} and {len(group.duplicate_ids)} others"
                    ),
                    affected_ids=[group.primary_id] + group.duplicate_ids,
                    store="graph",
                    suggested_action="Merge duplicate entities",
                )
            )

        logger.debug("Finding stale entities...")
        for issue in self._find_stale_entities(graph_data):
            report.add_issue(issue)

        logger.debug("Finding stale edges...")
        for issue in self._find_stale_edges(graph_data):
            report.add_issue(issue)

        logger.debug("Checking cross-store consistency...")
        for issue in self._find_cross_store_issues(graph_data, vector_docs):
            report.add_issue(issue)

        # Update orphan count in graph stats
        report.graph_stats["orphan_count"] = sum(
            1
            for issue in report.issues
            if issue.issue_type
            in (IssueType.ORPHANED_EDGE, IssueType.ORPHANED_PROVENANCE)
        )

        logger.info(
            f"Analysis complete: {len(report.issues)} issues found "
            f"(critical={report.severity_counts['critical']}, "
            f"warning={report.severity_counts['warning']}, "
            f"info={report.severity_counts['info']})"
        )

        return report

    def generate_report_summary(self, report: ConsistencyReport) -> str:
        """
        Generate a human-readable summary of the report.

        Args:
            report: The consistency report

        Returns:
            Formatted summary string
        """
        lines = [
            "=" * 60,
            "MEMORY CONSISTENCY REPORT",
            "=" * 60,
            f"Analyzed: {report.memory_dir}",
            f"Time: {report.analyzed_at.isoformat()}",
            "",
            "STORE STATISTICS:",
            f"  Graph: {report.graph_stats.get('node_count', 0)} nodes, "
            f"{report.graph_stats.get('edge_count', 0)} edges",
            f"  Vector: {report.vector_stats.get('total', 0)} documents "
            f"({report.vector_stats.get('insight_count', 0)} insights, "
            f"{report.vector_stats.get('summary_count', 0)} summaries)",
            f"  Episodic: {report.episodic_stats.get('turn_count', 0)} turns "
            f"({report.episodic_stats.get('consolidated_count', 0)} consolidated)",
            "",
            "ISSUES FOUND:",
            f"  Critical: {report.severity_counts['critical']}",
            f"  Warning: {report.severity_counts['warning']}",
            f"  Info: {report.severity_counts['info']}",
            "",
        ]

        if report.duplicate_groups:
            lines.append(f"DUPLICATE GROUPS: {len(report.duplicate_groups)}")
            for group in report.duplicate_groups[:5]:  # Show first 5
                lines.append(
                    f"  - {group.primary_id} ({group.match_type}): "
                    f"{len(group.duplicate_ids)} duplicates"
                )
            if len(report.duplicate_groups) > 5:
                lines.append(f"  ... and {len(report.duplicate_groups) - 5} more")
            lines.append("")

        if report.issues:
            lines.append("SAMPLE ISSUES:")
            for issue in report.issues[:10]:  # Show first 10
                lines.append(f"  [{issue.severity.value.upper()}] {issue.description}")
            if len(report.issues) > 10:
                lines.append(f"  ... and {len(report.issues) - 10} more issues")

        lines.append("=" * 60)

        return "\n".join(lines)
