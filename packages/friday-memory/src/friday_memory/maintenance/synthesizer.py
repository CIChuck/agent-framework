# mypy: ignore-errors
"""
Memory Synthesizer for Friday Memory.

Generates higher-order memories through analysis and LLM-based synthesis:
- Topic clustering
- Meta-insight generation
- Knowledge gap detection
- Relationship inference
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import chromadb
import numpy as np

from friday_memory.json_response import (
    json_parse_warning_detail,
    parse_json_object_from_text,
)
from friday_memory.llm_completion import MemoryLLMClient, complete_memory_request
from friday_memory.maintenance.models import (
    KnowledgeGap,
    PromptsConfig,
    SynthesisConfig,
    SynthesisReport,
    SynthesizedMemory,
    TopicCluster,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from friday_memory.maintenance.logger import ReorganizationLogger

    # Type for embedding functions (sync or async that returns list of floats)
    EmbeddingFunction = Callable[[str], list[float]]

logger = logging.getLogger(__name__)


_SYNTHESIS_SYSTEM_PROMPT = (
    "You are a structured analysis engine. You MUST respond with ONLY "
    "valid JSON — no markdown, no explanatory text, no preamble. "
    "If the input data is insufficient, return the JSON schema with "
    "empty or default values rather than refusing."
)


class MemorySynthesizer:
    """
    Synthesizes new memories from existing knowledge.

    Uses clustering and LLM analysis to:
    - Identify topic clusters
    - Generate meta-insights
    - Find knowledge gaps
    - Infer relationships

    Example:
        from friday_llm import LiteLLMService

        llm = LiteLLMService(model_name="gpt-4")
        synthesizer = MemorySynthesizer(
            memory_dir="./memory",
            llm_service=llm,
        )

        report = await synthesizer.synthesize(dry_run=True)
    """

    def __init__(
        self,
        memory_dir: str | Path,
        llm_service: MemoryLLMClient | None = None,
        config: SynthesisConfig | None = None,
        prompts: PromptsConfig | None = None,
        reorg_logger: ReorganizationLogger | None = None,
        embedding_function: Any | None = None,
        collection_name: str | None = None,
    ) -> None:
        """
        Initialize the synthesizer.

        Args:
            memory_dir: Directory containing memory stores
            llm_service: LiteLLMService for synthesis operations
            config: Configuration for synthesis
            prompts: Prompts configuration (defaults used if not provided)
            reorg_logger: Optional logger for recording actions
            embedding_function: Optional embedding function to use when storing
                               synthesized memories. Should have an embed() method
                               or be callable. If not provided, ChromaDB's default
                               embedding will be used (may cause dimension mismatch).
            collection_name: ChromaDB collection name to use. If not provided,
                            uses the first available collection (may be wrong).
        """
        self._memory_dir = Path(memory_dir)
        self._llm = llm_service
        self._config = config or SynthesisConfig()
        self._prompts = prompts or PromptsConfig()
        self._reorg_logger = reorg_logger
        self._embedding_function = embedding_function
        self._collection_name = collection_name
        self._graph_data: dict[str, Any] | None = None
        self._graph_modified: bool = False

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
        """Save graph data."""
        if self._graph_data is None:
            return

        graph_path = self._memory_dir / "graph.json"
        temp_path = graph_path.with_suffix(".tmp")

        with open(temp_path, "w") as f:
            json.dump(self._graph_data, f, indent=2, default=str)
        temp_path.replace(graph_path)

    def _parse_json_response(
        self,
        content: str,
        *,
        reasoning_content: str | None = None,
    ) -> dict[str, Any]:
        """
        Parse JSON from LLM response, handling various formats.

        LLMs often wrap JSON in markdown code blocks or add extra text.
        This method tries multiple strategies to extract valid JSON.

        Args:
            content: Raw LLM response content

        Returns:
            Parsed JSON as dict, or empty dict if parsing fails
        """
        parsed = parse_json_object_from_text(content)
        if parsed is not None:
            return parsed

        # Strategy 5: Return empty structure
        logger.warning(
            json_parse_warning_detail(
                "memory synthesis",
                content,
                reasoning_content=reasoning_content,
            )
        )
        return {}

    def _get_chroma_client(self) -> chromadb.ClientAPI | None:
        """Get ChromaDB client."""
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

    def _get_collection(self, client: chromadb.ClientAPI) -> chromadb.Collection | None:
        """
        Get the ChromaDB collection.

        Uses configured collection_name if provided, otherwise falls back to
        the first available collection.

        Args:
            client: ChromaDB client

        Returns:
            Collection or None if not found
        """
        try:
            if self._collection_name:
                # Use the specified collection name
                return client.get_collection(name=self._collection_name)
            else:
                # Fall back to first collection (may be wrong!)
                collections = client.list_collections()
                if collections:
                    logger.warning(
                        f"No collection_name specified, using first collection: {collections[0].name}. "  # noqa: E501
                        "This may not be the intended collection."
                    )
                    return collections[0]
                return None
        except Exception as e:
            logger.error(f"Error getting collection: {e}")
            return None

    def _get_insights_with_embeddings(
        self,
    ) -> tuple[list[dict], list[list[float]] | None]:
        """
        Get all insights with their embeddings.

        Returns:
            Tuple of (insights list, embeddings list or None)
        """
        client = self._get_chroma_client()
        if not client:
            return [], None

        try:
            collection = self._get_collection(client)
            if not collection:
                return [], None

            data = collection.get(
                include=["embeddings", "metadatas", "documents"],
                where={"type": "insight"} if collection.count() > 0 else None,
            )

            insights = []
            for i, doc_id in enumerate(data["ids"]):
                insights.append(
                    {
                        "id": doc_id,
                        "text": data["documents"][i] if data["documents"] else "",
                        "metadata": data["metadatas"][i] if data["metadatas"] else {},
                    }
                )

            # Handle embeddings (may be numpy array, can't use truthiness check)
            raw_embeddings = data["embeddings"]
            if raw_embeddings is None or (
                hasattr(raw_embeddings, "__len__") and len(raw_embeddings) == 0
            ):
                embeddings = None
            else:
                embeddings = raw_embeddings

            return insights, embeddings

        except Exception as e:
            logger.error(f"Error getting insights: {e}")
            return [], None

    async def analyze_topic_clusters(self) -> list[TopicCluster]:
        """
        Cluster insights by topic using embeddings.

        Uses simple k-means-like clustering on stored embeddings.

        Returns:
            List of topic clusters
        """
        insights, embeddings = self._get_insights_with_embeddings()

        if not insights or embeddings is None or len(insights) < 3:
            logger.info("Not enough insights for clustering")
            return []

        logger.info(f"Clustering {len(insights)} insights")

        # Simple clustering using cosine similarity
        clusters: list[TopicCluster] = []

        try:
            # Convert to numpy for efficient computation
            emb_array = np.array(embeddings)

            # Normalize for cosine similarity
            norms = np.linalg.norm(emb_array, axis=1, keepdims=True)
            norms[norms == 0] = 1  # Avoid division by zero
            normalized = emb_array / norms

            # Simple greedy clustering
            assigned = set()
            cluster_id = 0

            for i in range(len(insights)):
                if i in assigned:
                    continue

                # Start new cluster with this insight
                cluster_members = [i]
                assigned.add(i)

                # Find similar insights
                similarities = normalized @ normalized[i]

                for j in range(len(insights)):
                    if j in assigned:
                        continue
                    if similarities[j] > 0.7:  # Similarity threshold
                        cluster_members.append(j)
                        assigned.add(j)

                # Only keep clusters meeting minimum size
                if len(cluster_members) >= self._config.cluster_min_size:
                    # Get entity references from cluster members
                    entity_ids = set()
                    for idx in cluster_members:
                        entities = insights[idx].get("metadata", {}).get("entities", [])
                        entity_ids.update(entities)

                    # Determine theme from most common entities/topics
                    topics = []
                    for idx in cluster_members:
                        topic = insights[idx].get("metadata", {}).get("topic", "")
                        if topic:
                            topics.append(topic)

                    theme = max(set(topics), key=topics.count) if topics else "general"

                    # Calculate coherence (average pairwise similarity)
                    if len(cluster_members) > 1:
                        pairwise_sims = []
                        for a in range(len(cluster_members)):
                            for b in range(a + 1, len(cluster_members)):
                                sim = similarities[cluster_members[b]]
                                pairwise_sims.append(sim)
                        coherence = float(np.mean(pairwise_sims))
                    else:
                        coherence = 1.0

                    clusters.append(
                        TopicCluster(
                            cluster_id=f"cluster_{cluster_id}",
                            theme=theme,
                            insight_ids=[
                                insights[idx]["id"] for idx in cluster_members
                            ],
                            entity_ids=list(entity_ids),
                            coherence_score=coherence,
                        )
                    )
                    cluster_id += 1

        except Exception as e:
            logger.error(f"Error during clustering: {e}")

        logger.info(f"Found {len(clusters)} topic clusters")
        return clusters

    async def generate_meta_insights(
        self,
        clusters: list[TopicCluster] | None = None,
    ) -> list[SynthesizedMemory]:
        """
        Generate meta-insights from topic clusters using LLM.

        Args:
            clusters: Optional pre-computed clusters. If None, computes them.

        Returns:
            List of synthesized memories
        """
        if self._llm is None:
            logger.warning(
                "No LLM service configured, skipping meta-insight generation"
            )
            return []

        if clusters is None:
            clusters = await self.analyze_topic_clusters()

        if not clusters:
            return []

        insights, _ = self._get_insights_with_embeddings()
        insight_map = {ins["id"]: ins for ins in insights}

        graph_data = self._load_graph()
        nodes = graph_data.get("nodes", {})

        meta_insights: list[SynthesizedMemory] = []

        for cluster in clusters:
            # Gather cluster insights
            cluster_insights = []
            for ins_id in cluster.insight_ids[:10]:  # Limit for prompt size
                if ins_id in insight_map:
                    cluster_insights.append(insight_map[ins_id]["text"])

            # Gather related entities
            cluster_entities = []
            for ent_id in cluster.entity_ids[:10]:
                if ent_id in nodes:
                    cluster_entities.append(
                        f"- {nodes[ent_id].get('label', ent_id)} "
                        f"({nodes[ent_id].get('type', 'unknown')})"
                    )

            # Generate meta-insight via LLM
            prompt = self._prompts.meta_insight.format(
                insights="\n".join(f"- {ins}" for ins in cluster_insights),
                entities="\n".join(cluster_entities) or "No specific entities",
            )

            try:
                response = await complete_memory_request(
                    self._llm,
                    messages=[
                        {"role": "system", "content": _SYNTHESIS_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                )

                # Parse response with robust JSON handling
                raw_content = response.content or ""
                result = self._parse_json_response(
                    raw_content,
                    reasoning_content=getattr(response, "reasoning_content", None),
                )

                insight_id = f"meta_{uuid.uuid4().hex[:8]}"
                insight_content = result.get("meta_insight", "")
                confidence = result.get(
                    "confidence", self._config.meta_insight_confidence
                )

                meta_insights.append(
                    SynthesizedMemory(
                        id=insight_id,
                        type="meta_insight",
                        content=insight_content,
                        source_memories=cluster.insight_ids,
                        confidence=confidence,
                        reasoning=result.get("reasoning", ""),
                    )
                )

                # Log the meta-insight creation
                if self._reorg_logger:
                    self._reorg_logger.log_meta_insight_created(
                        insight_id=insight_id,
                        content=insight_content,
                        source_ids=cluster.insight_ids,
                        confidence=confidence,
                        reason=f"Synthesized from {len(cluster.insight_ids)} insights in cluster {cluster.cluster_id}",  # noqa: E501
                        prompt_sent=prompt,
                        llm_response_raw=raw_content,
                        llm_response_parsed=result,
                        metadata={
                            "cluster_id": cluster.cluster_id,
                            "cluster_theme": cluster.theme,
                        },
                    )

            except Exception as e:
                logger.error(
                    f"Error generating meta-insight for {cluster.cluster_id}: {e}"
                )

        logger.info(f"Generated {len(meta_insights)} meta-insights")
        return meta_insights

    async def identify_knowledge_gaps(self) -> list[KnowledgeGap]:
        """
        Identify gaps in the knowledge graph.

        Returns:
            List of identified knowledge gaps
        """
        graph_data = self._load_graph()
        nodes = graph_data.get("nodes", {})
        edges = graph_data.get("edges", [])

        gaps: list[KnowledgeGap] = []

        # Find isolated entities (few relationships)
        edge_counts: dict[str, int] = {}
        for edge in edges:
            source = edge.get("source", "")
            target = edge.get("target", "")
            edge_counts[source] = edge_counts.get(source, 0) + 1
            edge_counts[target] = edge_counts.get(target, 0) + 1

        for node_id, node_data in nodes.items():
            count = edge_counts.get(node_id, 0)
            if count <= 1 and node_data.get("hit_count", 0) > 0:
                # Entity has been accessed but has few relationships
                gaps.append(
                    KnowledgeGap(
                        gap_id=f"gap_{uuid.uuid4().hex[:8]}",
                        description=f"Entity '{node_data.get('label', node_id)}' "
                        f"has only {count} relationships despite being accessed "
                        f"{node_data.get('hit_count', 0)} times",
                        related_entities=[node_id],
                        evidence="High access count with low relationship count suggests "  # noqa: E501
                        "incomplete knowledge capture",
                        priority="medium" if count == 0 else "low",
                    )
                )

        # Use LLM for deeper analysis if available
        if self._llm and nodes:
            try:
                # Prepare data for LLM
                entity_summaries = []
                for node_id, node_data in list(nodes.items())[:20]:
                    entity_summaries.append(
                        f"- {node_data.get('label', node_id)} "
                        f"({node_data.get('type', 'unknown')}): "
                        f"hit_count={node_data.get('hit_count', 0)}"
                    )

                relationship_summaries = []
                for edge in edges[:30]:
                    relationship_summaries.append(
                        f"- {edge.get('source')} --[{edge.get('relation')}]--> "
                        f"{edge.get('target')}"
                    )

                insights, _ = self._get_insights_with_embeddings()
                insight_texts = [ins["text"] for ins in insights[:20]]

                prompt = self._prompts.knowledge_gap.format(
                    entities="\n".join(entity_summaries),
                    relationships="\n".join(relationship_summaries)
                    or "No relationships",
                    insights="\n".join(f"- {ins}" for ins in insight_texts)
                    or "No insights",
                )

                response = await complete_memory_request(
                    self._llm,
                    messages=[
                        {"role": "system", "content": _SYNTHESIS_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                )

                result = self._parse_json_response(
                    response.content or "",
                    reasoning_content=getattr(response, "reasoning_content", None),
                )

                for gap_data in result.get("gaps", []):
                    gap_id = f"gap_{uuid.uuid4().hex[:8]}"
                    description = gap_data.get("description", "")
                    related_entities = gap_data.get("related_entities", [])
                    priority = gap_data.get("priority", "medium")

                    gaps.append(
                        KnowledgeGap(
                            gap_id=gap_id,
                            description=description,
                            related_entities=related_entities,
                            evidence=gap_data.get("evidence", ""),
                            priority=priority,
                        )
                    )

                    # Log the knowledge gap
                    if self._reorg_logger:
                        self._reorg_logger.log_knowledge_gap_identified(
                            gap_id=gap_id,
                            description=description,
                            related_entities=related_entities,
                            priority=priority,
                            reason="LLM analysis identified missing knowledge",
                            prompt_sent=prompt,
                            llm_response_raw=response.content,
                            llm_response_parsed=result,
                        )

            except Exception as e:
                logger.error(f"Error in LLM gap analysis: {e}")

        logger.info(f"Identified {len(gaps)} knowledge gaps")
        return gaps

    async def infer_relationships(self) -> list[SynthesizedMemory]:
        """
        Infer new relationships using LLM analysis.

        Returns:
            List of inferred relationships as synthesized memories
        """
        if self._llm is None:
            logger.warning("No LLM service configured, skipping relationship inference")
            return []

        graph_data = self._load_graph()
        nodes = graph_data.get("nodes", {})
        edges = graph_data.get("edges", [])

        if not nodes or not edges:
            return []

        inferred: list[SynthesizedMemory] = []

        try:
            # Prepare data for LLM
            entity_summaries = []
            for node_id, node_data in list(nodes.items())[:30]:
                entity_summaries.append(
                    f"- {node_id}: {node_data.get('label', '')} "
                    f"({node_data.get('type', 'unknown')})"
                )

            relationship_summaries = []
            for edge in edges[:50]:
                relationship_summaries.append(
                    f"- {edge.get('source')} --[{edge.get('relation')}]--> "
                    f"{edge.get('target')}"
                )

            prompt = self._prompts.relationship_inference.format(
                entities="\n".join(entity_summaries),
                relationships="\n".join(relationship_summaries),
            )

            response = await complete_memory_request(
                self._llm,
                messages=[
                    {"role": "system", "content": _SYNTHESIS_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )

            result = self._parse_json_response(
                response.content or "",
                reasoning_content=getattr(response, "reasoning_content", None),
            )

            for rel in result.get("inferred_relationships", []):
                # Only include high-confidence inferences
                confidence = rel.get("confidence", 0)
                if confidence >= 0.7:
                    rel_id = f"rel_{uuid.uuid4().hex[:8]}"
                    source_entity = rel.get("source", "")
                    relation = rel.get("relation", "")
                    target_entity = rel.get("target", "")
                    reasoning = rel.get("reasoning", "")

                    inferred.append(
                        SynthesizedMemory(
                            id=rel_id,
                            type="inferred_relationship",
                            content=f"{source_entity} --[{relation}]--> {target_entity}",  # noqa: E501
                            source_memories=[],  # Inferred from graph structure
                            confidence=confidence,
                            reasoning=reasoning,
                        )
                    )

                    # Log the relationship inference
                    if self._reorg_logger:
                        self._reorg_logger.log_relationship_inferred(
                            relationship_id=rel_id,
                            source_entity=source_entity,
                            relation=relation,
                            target_entity=target_entity,
                            confidence=confidence,
                            reason=reasoning,
                            prompt_sent=prompt,
                            llm_response_raw=response.content,
                            llm_response_parsed=result,
                        )

        except Exception as e:
            logger.error(f"Error inferring relationships: {e}")

        logger.info(f"Inferred {len(inferred)} relationships")
        return inferred

    async def _get_embedding(self, text: str) -> list[float] | None:
        """
        Get embedding for text using the configured embedding function.

        Args:
            text: Text to embed

        Returns:
            Embedding vector or None if no embedding function configured
        """
        if self._embedding_function is None:
            return None

        try:
            # Support different embedding function interfaces
            if hasattr(self._embedding_function, "embed_query"):
                # LiteLLMEmbeddingService style (has embed_query for single text)
                result = self._embedding_function.embed_query(text)
                # Handle async if needed
                if hasattr(result, "__await__"):
                    result = await result
                return result
            elif hasattr(self._embedding_function, "embed"):
                # Alternative interface with embed() method
                result = self._embedding_function.embed(text)
                if hasattr(result, "__await__"):
                    result = await result
                return result
            elif callable(self._embedding_function):
                # Direct callable
                result = self._embedding_function(text)
                if hasattr(result, "__await__"):
                    result = await result
                return result
            else:
                logger.warning(
                    f"Embedding function doesn't have expected interface. "
                    f"Type: {type(self._embedding_function).__name__}, "
                    f"Has embed_query: {hasattr(self._embedding_function, 'embed_query')}, "  # noqa: E501
                    f"Has embed: {hasattr(self._embedding_function, 'embed')}, "
                    f"Callable: {callable(self._embedding_function)}"
                )
                return None
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    async def _store_synthesized_memory(
        self,
        memory: SynthesizedMemory,
    ) -> bool:
        """
        Store a synthesized memory in the appropriate store.

        Args:
            memory: The memory to store

        Returns:
            True if stored successfully
        """
        client = self._get_chroma_client()
        if not client:
            return False

        try:
            collection = self._get_collection(client)
            if not collection:
                return False

            # Generate embedding using configured function if available
            embedding = await self._get_embedding(memory.content)

            # Store as document with metadata
            add_kwargs: dict[str, Any] = {
                "ids": [memory.id],
                "documents": [memory.content],
                "metadatas": [
                    {
                        "type": memory.type,
                        "confidence": memory.confidence,
                        "source_memories": json.dumps(memory.source_memories),
                        "reasoning": memory.reasoning,
                        "created_at": datetime.now().isoformat(),
                        "provenance_source_type": "synthesis",
                    }
                ],
            }

            # Include embedding if we generated one
            if embedding is not None:
                add_kwargs["embeddings"] = [embedding]
            else:
                logger.warning(
                    "No embedding function configured - using ChromaDB default. "
                    "This may cause dimension mismatch if collection was created "
                    "with a different embedding model."
                )

            collection.add(**add_kwargs)

            return True

        except Exception as e:
            logger.error(f"Error storing synthesized memory: {e}")
            return False

    async def _store_inferred_relationship(
        self,
        memory: SynthesizedMemory,
    ) -> bool:
        """
        Store an inferred relationship in the graph.

        Args:
            memory: The inferred relationship

        Returns:
            True if stored successfully
        """
        # Parse relationship from content
        if "--[" not in memory.content or "]--> " not in memory.content:
            return False

        try:
            parts = memory.content.split("--[")
            source = parts[0].strip()
            rest = parts[1].split("]-->")
            relation = rest[0].strip()
            target = rest[1].strip()

            graph_data = self._load_graph()

            # Only add if both nodes exist
            if source not in graph_data.get("nodes", {}):
                return False
            if target not in graph_data.get("nodes", {}):
                return False

            # Add edge
            graph_data["edges"].append(
                {
                    "source": source,
                    "target": target,
                    "relation": relation,
                    "provenance": {
                        "source_id": memory.id,
                        "source_type": "inference",
                        "confidence": memory.confidence,
                        "created_at": datetime.now().isoformat(),
                    },
                    "weight": memory.confidence,
                }
            )

            self._graph_modified = True
            self._save_graph()
            return True

        except Exception as e:
            logger.error(f"Error storing inferred relationship: {e}")
            return False

    async def synthesize_memories(self, dry_run: bool = True) -> SynthesisReport:
        """
        Alias for synthesize() to match plan interface.
        """
        return await self.synthesize(dry_run=dry_run)

    async def synthesize(self, dry_run: bool = True) -> SynthesisReport:
        """
        Perform full synthesis operation.

        Args:
            dry_run: If True, report what would be synthesized without storing

        Returns:
            SynthesisReport with results
        """
        logger.info(f"Starting synthesis (dry_run={dry_run}) of {self._memory_dir}")

        report = SynthesisReport(dry_run=dry_run)

        try:
            # 1. Analyze topic clusters
            logger.debug("Analyzing topic clusters...")
            clusters = await self.analyze_topic_clusters()
            report.clusters = clusters
            report.clusters_found = len(clusters)

            # 2. Generate meta-insights
            logger.debug("Generating meta-insights...")
            meta_insights = await self.generate_meta_insights(clusters)

            for mi in meta_insights:
                report.synthesized_memories.append(mi)
                if not dry_run:
                    await self._store_synthesized_memory(mi)

            report.meta_insights_created = len(meta_insights)

            # 3. Identify knowledge gaps
            logger.debug("Identifying knowledge gaps...")
            gaps = await self.identify_knowledge_gaps()
            report.knowledge_gaps = gaps
            report.gaps_identified = len(gaps)

            # 4. Infer relationships
            logger.debug("Inferring relationships...")
            inferred = await self.infer_relationships()

            for rel in inferred:
                report.synthesized_memories.append(rel)
                if not dry_run:
                    await self._store_inferred_relationship(rel)

            report.relationships_inferred = len(inferred)

            logger.info(
                f"Synthesis complete: "
                f"clusters={report.clusters_found}, "
                f"meta_insights={report.meta_insights_created}, "
                f"relationships={report.relationships_inferred}, "
                f"gaps={report.gaps_identified}"
            )

        except Exception as e:
            logger.error(f"Error during synthesis: {e}")
            report.errors.append(str(e))
            # Save graph even on error to preserve any changes made before failure
            if not dry_run and self._graph_modified:
                logger.info("Saving graph after error to preserve changes")
                self._save_graph()

        return report

    def generate_report_summary(self, report: SynthesisReport) -> str:
        """
        Generate a human-readable summary of the synthesis report.

        Args:
            report: The synthesis report

        Returns:
            Formatted summary string
        """
        status = "DRY RUN" if report.dry_run else "EXECUTED"

        lines = [
            "=" * 60,
            f"SYNTHESIS REPORT ({status})",
            "=" * 60,
            f"Time: {report.synthesized_at.isoformat()}",
            "",
            "RESULTS:",
            f"  Topic clusters found: {report.clusters_found}",
            f"  Meta-insights created: {report.meta_insights_created}",
            f"  Relationships inferred: {report.relationships_inferred}",
            f"  Knowledge gaps identified: {report.gaps_identified}",
            "",
        ]

        if report.clusters:
            lines.append("TOPIC CLUSTERS:")
            for cluster in report.clusters[:5]:
                lines.append(
                    f"  - {cluster.theme}: {len(cluster.insight_ids)} insights "
                    f"(coherence={cluster.coherence_score:.2f})"
                )
            if len(report.clusters) > 5:
                lines.append(f"  ... and {len(report.clusters) - 5} more")
            lines.append("")

        if report.synthesized_memories:
            lines.append("SYNTHESIZED MEMORIES:")
            for mem in report.synthesized_memories[:5]:
                preview = (
                    mem.content[:60] + "..." if len(mem.content) > 60 else mem.content
                )
                lines.append(f"  [{mem.type}] {preview}")
            if len(report.synthesized_memories) > 5:
                lines.append(f"  ... and {len(report.synthesized_memories) - 5} more")
            lines.append("")

        if report.knowledge_gaps:
            lines.append("KNOWLEDGE GAPS:")
            for gap in report.knowledge_gaps[:5]:
                lines.append(f"  [{gap.priority}] {gap.description}")
            if len(report.knowledge_gaps) > 5:
                lines.append(f"  ... and {len(report.knowledge_gaps) - 5} more")

        if report.errors:
            lines.append("")
            lines.append("ERRORS:")
            for error in report.errors:
                lines.append(f"  - {error}")

        lines.append("=" * 60)

        return "\n".join(lines)
