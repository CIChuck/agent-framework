# mypy: ignore-errors
"""
Maintenance Utility Data Models.

Pydantic models for backup manifests, analysis reports, and operation results.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

# =============================================================================
# Enums
# =============================================================================


class IssueSeverity(str, Enum):
    """Severity levels for consistency issues."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class IssueType(str, Enum):
    """Types of consistency issues detected."""

    ORPHANED_EDGE = "orphaned_edge"
    ORPHANED_PROVENANCE = "orphaned_provenance"
    DUPLICATE_ENTITY = "duplicate_entity"
    STALE_ENTITY = "stale_entity"
    STALE_INSIGHT = "stale_insight"
    STALE_EDGE = "stale_edge"
    CROSS_STORE_MISMATCH = "cross_store_mismatch"
    MISSING_INSIGHT = "missing_insight"
    SEMANTIC_DUPLICATE = "semantic_duplicate"


class ClaimType(str, Enum):
    """Types of claims for fact classification."""

    STATISTICAL = "statistical"
    HISTORICAL = "historical"
    SCIENTIFIC = "scientific"
    OPINION = "opinion"
    PREFERENCE = "preference"
    BELIEF = "belief"


class VerificationVerdict(str, Enum):
    """Verdicts from fact verification."""

    VERIFIED = "VERIFIED"
    DISPUTED = "DISPUTED"
    UNVERIFIABLE = "UNVERIFIABLE"
    CONVERSATIONAL = "CONVERSATIONAL"


class LogVerbosity(str, Enum):
    """Verbosity levels for reorganization logging."""

    MINIMAL = "minimal"  # Action summaries only
    NORMAL = "normal"  # Summaries + IDs and brief content previews
    VERBOSE = "verbose"  # Everything including full prompts/responses


class LogFormat(str, Enum):
    """Output formats for reorganization logs."""

    MARKDOWN = "markdown"  # Human-readable .md
    JSON = "json"  # Structured .json for analysis
    CSV = "csv"  # Tabular .csv for spreadsheets


class ActionType(str, Enum):
    """Types of actions that can be logged during reorganization."""

    # Backup actions
    BACKUP_CREATED = "backup_created"

    # Pruning actions
    ENTITY_REMOVED = "entity_removed"
    ENTITY_MERGED = "entity_merged"
    INSIGHT_REMOVED = "insight_removed"
    EDGE_REMOVED = "edge_removed"

    # Fact checking actions
    FACT_CLASSIFIED = "fact_classified"
    FACT_VERIFIED = "fact_verified"
    FACT_METADATA_UPDATED = "fact_metadata_updated"

    # Synthesis actions
    META_INSIGHT_CREATED = "meta_insight_created"
    RELATIONSHIP_INFERRED = "relationship_inferred"
    KNOWLEDGE_GAP_IDENTIFIED = "knowledge_gap_identified"


# =============================================================================
# Configuration Models
# =============================================================================


class PruneConfig(BaseModel):
    """Configuration for pruning operations."""

    stale_threshold_days: int = Field(
        default=90,
        ge=1,
        description="Days without access before entity is considered stale",
    )
    min_hit_count: int = Field(
        default=1,
        ge=0,
        description="Minimum hit count to keep an entity",
    )
    similarity_threshold: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
        description="Cosine similarity threshold for deduplication",
    )


class SynthesisConfig(BaseModel):
    """Configuration for synthesis operations."""

    cluster_min_size: int = Field(
        default=3,
        ge=2,
        description="Minimum insights per topic cluster",
    )
    meta_insight_confidence: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Default confidence for synthesized insights",
    )


class FactCheckConfig(BaseModel):
    """Configuration for fact checking operations."""

    batch_size: int = Field(
        default=50,
        ge=1,
        description="Number of claims to verify per run",
    )
    verification_timeout: int = Field(
        default=30,
        ge=1,
        description="Seconds per claim lookup",
    )


# Default prompts (used if not provided in config)
DEFAULT_CLASSIFICATION_PROMPT = """Analyze this statement and determine if it is FALSIFIABLE.

A falsifiable claim:
- Makes an objective assertion about the real world
- Can be verified or disproven with evidence
- Examples: dates, statistics, scientific facts, historical events

A conversational/subjective claim:
- Expresses opinion, belief, preference, or feeling
- Cannot be objectively proven true or false
- Examples: "X is the best", "I prefer Y", "Chuck thinks Z"

Statement: "{statement}"

Respond with JSON:
{{
    "falsifiable": true or false,
    "reasoning": "brief explanation",
    "claim_type": "statistical|historical|scientific|opinion|preference|belief",
    "suggested_verification": "how to verify if falsifiable, null otherwise"
}}"""  # noqa: E501

DEFAULT_RESEARCH_PROMPT = """You are a fact-checking researcher. Your task is to gather evidence about the following claim.

CLAIM: {claim}

Instructions:
1. Consider what authoritative sources would verify or refute this claim
2. Think about the context and domain of the claim
3. Evaluate the claim's specificity and verifiability
4. Provide evidence summary and confidence assessment

Respond with JSON:
{{
    "evidence_found": true or false,
    "evidence_summary": "Summary of evidence for/against the claim",
    "sources": ["source1", "source2"],
    "supports_claim": true or false or null (if inconclusive),
    "confidence": 0.0-1.0,
    "notes": "Any caveats or context"
}}"""  # noqa: E501

DEFAULT_JUDGE_PROMPT = """You are an impartial judge evaluating a fact-checking case. Review the evidence and render a verdict.

ORIGINAL CLAIM: {claim}

RESEARCHER'S EVIDENCE:
{evidence}

Instructions:
1. Evaluate the quality and relevance of the evidence
2. Consider if the evidence definitively supports or refutes the claim
3. Account for any ambiguity or context-dependence
4. Render a fair verdict

Respond with JSON:
{{
    "verdict": "VERIFIED" or "DISPUTED" or "UNVERIFIABLE",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed explanation of your decision",
    "correction": "If DISPUTED, provide the correct information. Otherwise null."
}}"""  # noqa: E501

DEFAULT_META_INSIGHT_PROMPT = """Analyze the following collection of insights and generate a higher-order meta-insight that captures a cross-cutting theme or pattern.

INSIGHTS:
{insights}

RELATED ENTITIES:
{entities}

Generate a meta-insight that:
1. Identifies a pattern that spans multiple insights
2. Provides a meaningful observation not explicitly stated in any single insight
3. Could be useful for future context retrieval

Respond with JSON:
{{
    "meta_insight": "The synthesized observation (1-2 sentences)",
    "reasoning": "Brief explanation of why this pattern is significant",
    "confidence": 0.0-1.0,
    "source_insight_indices": [list of indices of insights that support this]
}}"""  # noqa: E501

DEFAULT_KNOWLEDGE_GAP_PROMPT = """Analyze the following entities and their relationships to identify knowledge gaps.

ENTITIES:
{entities}

RELATIONSHIPS:
{relationships}

EXISTING INSIGHTS:
{insights}

Identify gaps where:
1. An entity has very few relationships (isolated)
2. A topic is mentioned but lacks detailed insights
3. Questions seem to have been asked but not answered

Respond with JSON:
{{
    "gaps": [
        {{
            "description": "What knowledge is missing",
            "related_entities": ["entity1", "entity2"],
            "evidence": "Why this is considered a gap",
            "priority": "low|medium|high"
        }}
    ]
}}"""  # noqa: E501

DEFAULT_RELATIONSHIP_INFERENCE_PROMPT = """Based on the following graph structure, infer potential new relationships.

EXISTING ENTITIES:
{entities}

EXISTING RELATIONSHIPS:
{relationships}

Infer new relationships where:
1. If A→B and B→C exist, consider if A→C makes sense
2. Similar entities might have similar relationships
3. Common patterns in the domain

Only suggest high-confidence inferences.

Respond with JSON:
{{
    "inferred_relationships": [
        {{
            "source": "entity_id",
            "relation": "RELATIONSHIP_TYPE",
            "target": "entity_id",
            "reasoning": "Why this relationship likely exists",
            "confidence": 0.0-1.0
        }}
    ]
}}"""  # noqa: E501


class PromptsConfig(BaseModel):
    """Configuration for LLM prompts used in maintenance operations."""

    classification: str = Field(
        default=DEFAULT_CLASSIFICATION_PROMPT,
        description="Prompt for classifying facts as falsifiable vs conversational",
    )
    research: str = Field(
        default=DEFAULT_RESEARCH_PROMPT,
        description="Prompt for researching claims to gather evidence",
    )
    judge: str = Field(
        default=DEFAULT_JUDGE_PROMPT,
        description="Prompt for judging claims based on evidence",
    )
    meta_insight: str = Field(
        default=DEFAULT_META_INSIGHT_PROMPT,
        description="Prompt for generating meta-insights from topic clusters",
    )
    knowledge_gap: str = Field(
        default=DEFAULT_KNOWLEDGE_GAP_PROMPT,
        description="Prompt for identifying knowledge gaps",
    )
    relationship_inference: str = Field(
        default=DEFAULT_RELATIONSHIP_INFERENCE_PROMPT,
        description="Prompt for inferring new relationships",
    )


class LogConfig(BaseModel):
    """Configuration for reorganization logging."""

    enabled: bool = Field(
        default=True,
        description="Whether logging is enabled",
    )
    log_directory: str = Field(
        default="./reorganization_logs",
        description="Directory for log files (relative to memory_dir or absolute)",
    )
    verbosity: LogVerbosity = Field(
        default=LogVerbosity.NORMAL,
        description="How much detail to include in logs",
    )
    format: LogFormat = Field(
        default=LogFormat.MARKDOWN,
        description="Output format for log files",
    )


class EmbeddingConfig(BaseModel):
    """Configuration for embedding model used in maintenance operations.

    The embedding model is used when storing synthesized memories (meta-insights)
    in the vector store. It should match the embedding model used to create the
    original vector store collection to avoid dimension mismatches.
    """

    model: str = Field(
        default="openai/nomic-embed-text-v1.5",
        description="Embedding model name (LiteLLM format, e.g., 'openai/model-name')",
    )
    api_base: str | None = Field(
        default=None,
        description="API base URL (e.g., 'http://localhost:1234/v1' for LM Studio)",
    )
    api_key: str | None = Field(
        default=None,
        description="API key (use any non-empty string for local models)",
    )
    timeout_seconds: float = Field(
        default=60.0,
        ge=1.0,
        description="Timeout in seconds for embedding requests",
    )


class AccessBufferConfig(BaseModel):
    """Configuration for the access buffer (lazy access tracking)."""

    max_buffer_size: int = Field(
        default=1000,
        ge=1,
        description="Maximum number of access events to buffer before flushing",
    )
    max_buffer_age_seconds: int = Field(
        default=300,  # 5 minutes
        ge=1,
        description="Maximum age of buffer before time-based flush",
    )
    wal_enabled: bool = Field(
        default=False,
        description="Enable write-ahead log for crash recovery",
    )
    wal_path: str | None = Field(
        default=None,
        description="Path for WAL file (relative to memory_dir or absolute)",
    )


class LifecycleDecayConfig(BaseModel):
    """
    Configuration for memory lifecycle decay.

    This is a simplified version for YAML config; the full DecayConfig
    with validation is in the lifecycle module.
    """

    enabled: bool = Field(
        default=True,
        description="Enable decay calculations",
    )
    decay_rate: float = Field(
        default=0.01,
        ge=0.001,
        le=0.5,
        description="Lambda for exponential decay. At 0.01: 24h->79%, 72h->49%",
    )
    access_boost: float = Field(
        default=0.2,
        ge=0.0,
        le=0.5,
        description="Score boost on each access",
    )
    promotion_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum score for SHORT_TERM -> LONG_TERM promotion",
    )
    decay_threshold: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Score below which memory becomes DECAYED",
    )
    short_term_min_age_hours: int = Field(
        default=24,
        ge=1,
        description="Minimum hours in SHORT_TERM before promotion eligibility",
    )
    decay_check_interval_hours: int = Field(
        default=24,
        ge=1,
        description="How often to run decay calculations",
    )
    decayed_retention_days: int = Field(
        default=30,
        ge=1,
        description="Days to retain DECAYED memories before deletion",
    )
    # Promotion weights
    promotion_weight_age: float = Field(default=0.2, ge=0.0, le=1.0)
    promotion_weight_access: float = Field(default=0.4, ge=0.0, le=1.0)
    promotion_weight_confidence: float = Field(default=0.2, ge=0.0, le=1.0)
    promotion_weight_connection: float = Field(default=0.2, ge=0.0, le=1.0)


class MaintenanceConfig(BaseModel):
    """Full configuration for maintenance operations."""

    pruning: PruneConfig = Field(default_factory=PruneConfig)
    synthesis: SynthesisConfig = Field(default_factory=SynthesisConfig)
    fact_checking: FactCheckConfig = Field(default_factory=FactCheckConfig)
    prompts: PromptsConfig = Field(default_factory=PromptsConfig)
    logging: LogConfig = Field(default_factory=LogConfig)
    embedding: EmbeddingConfig | None = Field(
        default=None,
        description="Embedding model config for storing synthesized memories. "
        "If None, falls back to the main embedding config or ChromaDB default.",
    )
    collection_name: str | None = Field(
        default=None,
        description="ChromaDB collection name for storing synthesized memories. "
        "Should match the collection used by the main application. "
        "If None, falls back to main memory config or first available collection.",
    )
    backup_directory: str | None = Field(
        default=None,
        description="Directory for storing backups. If None, uses memory_dir/backups",
    )
    # Lifecycle management
    decay: LifecycleDecayConfig = Field(
        default_factory=LifecycleDecayConfig,
        description="Memory lifecycle decay configuration",
    )
    access_buffer: AccessBufferConfig = Field(
        default_factory=AccessBufferConfig,
        description="Access buffer configuration for lazy access tracking",
    )


# =============================================================================
# Context Assembly Configuration
# =============================================================================


class ContextAssemblyConfig(BaseModel):
    """Configuration for context assembly optimization features."""

    # Entity display
    entity_format: str = Field(
        default="natural",
        description="Entity format: 'natural' (with relationships), 'table' (legacy), 'none'",  # noqa: E501
    )

    # Summaries
    summaries_mode: str = Field(
        default="conditional",
        description="Summaries mode: 'always', 'conditional' (skip when history complete), 'never'",  # noqa: E501
    )
    history_threshold_for_summaries: int = Field(
        default=10,
        description="Minimum history turns before considering summaries redundant",
    )

    # Insight deduplication
    dedupe_insights: bool = Field(
        default=True,
        description="Enable topic-based insight deduplication at retrieval",
    )

    # Query relevance filtering
    filter_by_relevance: bool = Field(
        default=True,
        description="Filter insights by query keyword relevance",
    )
    min_relevance_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum relevance score for insights (0 = any overlap)",
    )

    # Format options
    numbered_lists: bool = Field(
        default=False,
        description="Use numbered lists instead of bullets for insights/summaries",
    )


# =============================================================================
# Backup Models
# =============================================================================


class BackupManifest(BaseModel):
    """Manifest describing a backup of memory stores."""

    backup_id: str = Field(..., description="Unique backup identifier (UUID)")
    created_at: datetime = Field(default_factory=datetime.now)
    source_dir: str = Field(..., description="Original memory directory path")
    backup_dir: str = Field(..., description="Backup directory path")
    files: dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of original path to backup path",
    )
    checksums: dict[str, str] = Field(
        default_factory=dict,
        description="SHA256 checksums for each file",
    )
    store_stats: dict[str, Any] = Field(
        default_factory=dict,
        description="Statistics about each store at backup time",
    )

    def get_backup_path(self) -> Path:
        """Get the backup directory as a Path."""
        return Path(self.backup_dir)


# =============================================================================
# Consistency Analysis Models
# =============================================================================


class ConsistencyIssue(BaseModel):
    """A single consistency issue detected during analysis."""

    issue_type: IssueType = Field(..., description="Type of issue")
    severity: IssueSeverity = Field(..., description="Issue severity")
    description: str = Field(..., description="Human-readable description")
    affected_ids: list[str] = Field(
        default_factory=list,
        description="IDs of affected entities/documents",
    )
    store: str = Field(
        ..., description="Which store is affected: graph, vector, episodic"
    )
    suggested_action: str | None = Field(
        default=None,
        description="Suggested remediation action",
    )


class DuplicateGroup(BaseModel):
    """A group of duplicate or near-duplicate items."""

    primary_id: str = Field(..., description="ID of the canonical/primary item")
    duplicate_ids: list[str] = Field(..., description="IDs of duplicates")
    similarity_scores: dict[str, float] = Field(
        default_factory=dict,
        description="Similarity score for each duplicate",
    )
    match_type: str = Field(..., description="exact, fuzzy, or semantic")


class ConsistencyReport(BaseModel):
    """Full report from consistency analysis."""

    analyzed_at: datetime = Field(default_factory=datetime.now)
    memory_dir: str = Field(..., description="Directory that was analyzed")

    # Store statistics
    graph_stats: dict[str, int] = Field(
        default_factory=dict,
        description="node_count, edge_count, orphan_count",
    )
    vector_stats: dict[str, int] = Field(
        default_factory=dict,
        description="insight_count, summary_count, duplicate_count",
    )
    episodic_stats: dict[str, int] = Field(
        default_factory=dict,
        description="turn_count, consolidated_count, session_count",
    )

    # Issues found
    issues: list[ConsistencyIssue] = Field(default_factory=list)
    duplicate_groups: list[DuplicateGroup] = Field(default_factory=list)

    # Summary counts
    severity_counts: dict[str, int] = Field(
        default_factory=lambda: {"critical": 0, "warning": 0, "info": 0},
    )

    def add_issue(self, issue: ConsistencyIssue) -> None:
        """Add an issue and update severity counts."""
        self.issues.append(issue)
        self.severity_counts[issue.severity.value] += 1


# =============================================================================
# Pruning Models
# =============================================================================


class PrunedItem(BaseModel):
    """Details of an item that was or would be pruned."""

    item_id: str = Field(..., description="ID of the item")
    item_type: str = Field(..., description="Type: entity, insight, edge")
    store: str = Field(..., description="Source store: graph, vector")
    reason: str = Field(..., description="Why this item was pruned")
    content_preview: str | None = Field(
        default=None,
        description="Preview of content for review",
    )


class PruneReport(BaseModel):
    """Report from pruning operations."""

    pruned_at: datetime = Field(default_factory=datetime.now)
    dry_run: bool = Field(..., description="Whether this was a dry run")

    # Counts
    insights_removed: int = Field(default=0)
    entities_merged: int = Field(default=0)
    entities_removed: int = Field(default=0)
    edges_removed: int = Field(default=0)
    bytes_freed: int = Field(default=0)

    # Details
    items: list[PrunedItem] = Field(default_factory=list)
    merged_groups: list[DuplicateGroup] = Field(default_factory=list)

    # Errors
    errors: list[str] = Field(default_factory=list)


# =============================================================================
# Synthesis Models
# =============================================================================


class TopicCluster(BaseModel):
    """A cluster of related insights."""

    cluster_id: str = Field(..., description="Unique cluster identifier")
    theme: str = Field(..., description="Dominant theme/topic")
    insight_ids: list[str] = Field(..., description="IDs of insights in cluster")
    entity_ids: list[str] = Field(
        default_factory=list,
        description="Related entity IDs",
    )
    coherence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="How coherent/related the cluster members are",
    )


class KnowledgeGap(BaseModel):
    """An identified gap in knowledge."""

    gap_id: str = Field(..., description="Unique gap identifier")
    description: str = Field(..., description="What knowledge is missing")
    related_entities: list[str] = Field(default_factory=list)
    evidence: str = Field(..., description="Why this is considered a gap")
    priority: str = Field(default="medium", description="low, medium, high")


class SynthesizedMemory(BaseModel):
    """A memory generated through synthesis."""

    id: str = Field(..., description="Unique identifier")
    type: str = Field(
        ...,
        description="meta_insight, inferred_relationship, topic_summary",
    )
    content: str = Field(..., description="The synthesized content")
    source_memories: list[str] = Field(
        ...,
        description="IDs of source insights/entities",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in the synthesis",
    )
    reasoning: str = Field(..., description="Explanation of the synthesis")


class SynthesisReport(BaseModel):
    """Report from synthesis operations."""

    synthesized_at: datetime = Field(default_factory=datetime.now)
    dry_run: bool = Field(..., description="Whether this was a dry run")

    # Results
    clusters_found: int = Field(default=0)
    meta_insights_created: int = Field(default=0)
    relationships_inferred: int = Field(default=0)
    gaps_identified: int = Field(default=0)

    # Details
    clusters: list[TopicCluster] = Field(default_factory=list)
    synthesized_memories: list[SynthesizedMemory] = Field(default_factory=list)
    knowledge_gaps: list[KnowledgeGap] = Field(default_factory=list)

    # Errors
    errors: list[str] = Field(default_factory=list)


# =============================================================================
# Fact Checking Models
# =============================================================================


class ClassifiedFact(BaseModel):
    """A fact that has been classified for falsifiability."""

    fact_id: str = Field(..., description="ID in the vector store")
    original_text: str = Field(..., description="The fact text")
    falsifiable: bool = Field(..., description="Whether the claim is falsifiable")
    claim_type: ClaimType = Field(..., description="Type of claim")
    reasoning: str = Field(..., description="Why this classification")
    suggested_verification: str | None = Field(
        default=None,
        description="How to verify if falsifiable",
    )


class VerifiedClaim(BaseModel):
    """A claim that has been through verification."""

    claim_id: str = Field(..., description="ID of the claim")
    original_text: str = Field(..., description="The claim text")
    falsifiable: bool = Field(..., description="Whether falsifiable")
    verdict: VerificationVerdict = Field(..., description="Verification result")
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in the verdict",
    )
    evidence_summary: str = Field(default="", description="Summary of evidence")
    sources: list[str] = Field(default_factory=list, description="Source URLs")
    correction: str | None = Field(
        default=None,
        description="Correct information if disputed",
    )
    judge_reasoning: str = Field(default="", description="Judge's reasoning")


class VerificationReport(BaseModel):
    """Report from fact verification operations."""

    verified_at: datetime = Field(default_factory=datetime.now)
    dry_run: bool = Field(default=True)

    # Counts
    total_claims: int = Field(default=0)
    verified_true: int = Field(default=0)
    verified_false: int = Field(default=0)
    unverifiable: int = Field(default=0)
    skipped_conversational: int = Field(default=0)

    # Details
    classified_facts: list[ClassifiedFact] = Field(default_factory=list)
    verified_claims: list[VerifiedClaim] = Field(default_factory=list)

    # Errors
    errors: list[str] = Field(default_factory=list)


# =============================================================================
# Lifecycle Report Models
# =============================================================================


class LifecycleReport(BaseModel):
    """Report from lifecycle maintenance operations."""

    processed_at: datetime = Field(default_factory=datetime.now)
    dry_run: bool = Field(default=True)

    # Promotion stats
    promotions_checked: int = Field(default=0)
    promotions_executed: int = Field(default=0)
    promotion_failures: int = Field(default=0)

    # Decay stats
    decays_checked: int = Field(default=0)
    decays_executed: int = Field(default=0)
    decay_failures: int = Field(default=0)

    # Reactivation stats
    reactivations_checked: int = Field(default=0)
    reactivations_executed: int = Field(default=0)

    # Graph decay linkage
    graph_nodes_decayed: int = Field(default=0)

    # Details
    promoted_memory_ids: list[str] = Field(default_factory=list)
    decayed_memory_ids: list[str] = Field(default_factory=list)
    reactivated_memory_ids: list[str] = Field(default_factory=list)

    # Errors
    errors: list[str] = Field(default_factory=list)


class OptimizationReport(BaseModel):
    """Report from latency optimization operations."""

    processed_at: datetime = Field(default_factory=datetime.now)
    dry_run: bool = Field(default=True)

    # Access buffer flush stats
    access_buffer_flushed: bool = Field(default=False)
    short_term_accesses_flushed: int = Field(default=0)
    long_term_accesses_flushed: int = Field(default=0)

    # Retrieval factor stats
    retrieval_factors_computed: bool = Field(default=False)
    short_term_factors_updated: int = Field(default=0)
    long_term_factors_updated: int = Field(default=0)

    # Edge embedding stats
    edge_embeddings_backfilled: bool = Field(default=False)
    edges_embedded: int = Field(default=0)
    edges_skipped: int = Field(default=0)

    # Timestamp backfill stats (created_at_ts for date-range filtering)
    timestamp_backfill_done: bool = Field(default=False)
    timestamps_backfilled: int = Field(default=0)
    timestamps_skipped: int = Field(default=0)

    # Timing
    access_flush_duration_ms: float = Field(default=0.0)
    factor_compute_duration_ms: float = Field(default=0.0)
    edge_embed_duration_ms: float = Field(default=0.0)
    timestamp_backfill_duration_ms: float = Field(default=0.0)

    # Errors
    errors: list[str] = Field(default_factory=list)


class CleanupReport(BaseModel):
    """Report from hard delete and cleanup operations."""

    processed_at: datetime = Field(default_factory=datetime.now)
    dry_run: bool = Field(default=True)

    # Hard delete stats
    memories_deleted: int = Field(default=0)
    deleted_memory_ids: list[str] = Field(default_factory=list)

    # Graph cleanup stats
    graph_nodes_deleted: int = Field(default=0)
    deleted_node_ids: list[str] = Field(default_factory=list)

    # Configuration
    retention_days: int = Field(default=30)

    # Errors
    errors: list[str] = Field(default_factory=list)


class InsightCluster(BaseModel):
    """A cluster of similar/duplicate insights for deduplication."""

    cluster_id: str = Field(..., description="Unique cluster identifier")
    primary_insight_id: str = Field(
        ..., description="ID of the insight kept (most recent + highest confidence)"
    )
    superseded_ids: list[str] = Field(
        default_factory=list, description="IDs of insights marked as superseded"
    )
    entity_key: str = Field(
        default="", description="Entity signature used for clustering"
    )
    similarity_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Similarity score within cluster",
    )


class DeduplicationReport(BaseModel):
    """Report from insight deduplication operations."""

    processed_at: datetime = Field(default_factory=datetime.now)
    dry_run: bool = Field(default=True, description="Whether this was a dry run")

    # Counts
    insights_scanned: int = Field(default=0)
    clusters_found: int = Field(default=0)
    insights_superseded: int = Field(default=0)

    # Details
    clusters: list[InsightCluster] = Field(
        default_factory=list, description="List of insight clusters found"
    )

    # Errors
    errors: list[str] = Field(default_factory=list)


# =============================================================================
# Full Reorganization Report
# =============================================================================


class ReorganizationReport(BaseModel):
    """Complete report from a full reorganization run."""

    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = Field(default=None)
    memory_dir: str = Field(..., description="Directory that was reorganized")

    # Sub-reports
    backup_manifest: BackupManifest | None = Field(default=None)
    consistency_report: ConsistencyReport | None = Field(default=None)
    prune_report: PruneReport | None = Field(default=None)
    synthesis_report: SynthesisReport | None = Field(default=None)
    verification_report: VerificationReport | None = Field(default=None)
    lifecycle_report: LifecycleReport | None = Field(default=None)
    optimization_report: OptimizationReport | None = Field(default=None)
    cleanup_report: CleanupReport | None = Field(default=None)
    deduplication_report: DeduplicationReport | None = Field(default=None)

    # Overall status
    success: bool = Field(default=False)
    errors: list[str] = Field(default_factory=list)

    def complete(self, success: bool = True) -> None:
        """Mark the reorganization as complete."""
        self.completed_at = datetime.now()
        self.success = success


# =============================================================================
# Logging Models
# =============================================================================


class ActionLogEntry(BaseModel):
    """A single logged action during reorganization."""

    timestamp: datetime = Field(default_factory=datetime.now)
    action_type: ActionType = Field(..., description="Type of action performed")
    dry_run: bool = Field(default=False, description="Whether this was a dry run")

    # What was affected
    item_id: str = Field(..., description="ID of the affected item")
    item_type: str = Field(
        default="", description="Type of item (entity, insight, edge, etc.)"
    )
    store: str = Field(default="", description="Which store (graph, vector, episodic)")

    # Content details (verbosity: normal+)
    content_preview: str | None = Field(
        default=None,
        description="Brief preview of content (for normal verbosity)",
    )
    content_full: str | None = Field(
        default=None,
        description="Full content snapshot (for verbose)",
    )

    # For merge operations
    merged_into_id: str | None = Field(
        default=None,
        description="ID of item this was merged into",
    )
    merged_from_ids: list[str] = Field(
        default_factory=list,
        description="IDs of items merged into this one",
    )

    # Decision context
    reason: str = Field(default="", description="Why this action was taken")
    confidence: float | None = Field(
        default=None,
        description="Confidence score if applicable",
    )

    # LLM interaction details (verbosity: verbose)
    prompt_sent: str | None = Field(
        default=None,
        description="Full prompt sent to LLM (verbose only)",
    )
    llm_response_raw: str | None = Field(
        default=None,
        description="Raw LLM response (verbose only)",
    )
    llm_response_parsed: dict[str, Any] | None = Field(
        default=None,
        description="Parsed LLM response (verbose only)",
    )

    # Configuration context (verbosity: verbose)
    config_snapshot: dict[str, Any] | None = Field(
        default=None,
        description="Relevant config values (verbose only)",
    )

    # Additional metadata
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Any additional context",
    )
