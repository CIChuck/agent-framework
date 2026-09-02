# mypy: ignore-errors
"""
Memory Extractor (The Harvester).
Analyzes conversation turns to extract new entities and facts for the Graph.

Ref: Batch 2a Specification, Section 3
Updated: Batch 3 - Now uses injected LLMClient protocol
Updated: Phase 3 - Added edge embedding support for graph path scoring

Strategies:
1. Named Entity Extraction (NER): "User mentioned 'Project Alpha'."
2. Task State Extraction: "User completed task 'Fix Bug'."
3. Sentiment/Preference Extraction: "User expressed frustration with Python."
"""

import asyncio
import json
import logging
import time
import uuid
from typing import TYPE_CHECKING, Any

from friday_core import TelemetryInterface

from friday_memory.context.extraction_filter import (
    ExtractionFilter,
    configure_rejection_logging,
)
from friday_memory.context.ontology import OntologyConfig
from friday_memory.controller import MemoryController
from friday_memory.json_response import (
    json_parse_warning_detail,
    json_response_text,
    parse_json_object_from_text,
    strip_llm_reasoning,
)
from friday_memory.llm_completion import (
    MemoryLLMClient,
    complete_memory_request,
)
from friday_memory.models import (
    GraphEdge,
    GraphNode,
    InteractionTurn,
    ProvenanceMetadata,
)

if TYPE_CHECKING:
    from friday_core.interfaces import EmbeddingModel


logger = logging.getLogger(__name__)


class ExtractionCommitCompletedUnderCancellation(asyncio.CancelledError):
    """Signal that the current extraction committed before cancellation won."""


# Default extraction prompt template (used if none provided in config)
# Storage strategy:
# - entities, relationships → Graph Store (structured, Hebbian learning via hit_count)
# - insights → Vector Store (rich semantic content for similarity search)
DEFAULT_EXTRACTION_PROMPT = """Analyze the conversation turn below to extract a knowledge graph and semantic memories.

Turn ID: {turn_id}
Timestamp: {timestamp}

Conversation Context:
- Speaker A (Human): {user_name}
- Speaker B (AI): {assistant_name}

TEXT TO ANALYZE:
{user_name}: {user_message}
{assistant_name}: {assistant_response}

{ontology_constraints}

INSTRUCTIONS:

1. **Entity Extraction (Nodes)**
   - Extract ONLY concrete, named entities: specific people, organizations, technologies, locations, products, or documents.
   - Do NOT extract abstract concepts, feelings, time references, adjectives, or generic terms.
   - Do NOT extract "{user_name}" or "{assistant_name}" unless they are referred to by a proper name in the conversation.
   - Each entity must have a `type` from the ALLOWED TYPES listed above.
   - **Canonicalization**: Create an `id` in snake_case (e.g., "Python 3.1" → "python_3").
   - **Resolution**: Resolve pronouns (he, she, it) to the specific noun if clear from context.
   - **Be selective**: Only extract entities that carry meaningful, reusable knowledge. Skip throwaway mentions.

2. **Relationship Extraction (Edges)**
   - Extract directional relationships: SOURCE → RELATION → TARGET.
   - The `relation` field MUST be one of the ALLOWED RELATIONS listed above. Do not invent new relation types.
   - Source and target must reference entity `id` values from your entity list.
   - Prefer the most specific applicable relation (e.g., AUTHORED over RELATES_TO).
   - Do NOT create relationships for trivial or obvious connections.

3. **Insight Extraction (Structured Facts)**
   - Extract 1-3 rich, contextual observations worth remembering long-term.
   - **text**: A complete 1-2 sentence observation. Write as if explaining to someone with no prior context.
   - **topic**: One of "preference", "biographical", "technical", or "constraint".
   - **entities**: Entity names mentioned in this insight.
   - **confidence**: 0.0-1.0 based on how explicitly the information was stated.
   - **sentiment**: "positive", "negative", or "neutral".
   - Do NOT extract trivial observations. Each insight should be independently useful for future recall.

4. **Turn Summary**
   - Write a 2-4 sentence paragraph summarizing the conversation turn.
   - Include who was talking, the main topic, and any decisions or conclusions.

JSON OUTPUT FORMAT:

Respond ONLY with valid JSON:

{{
    "entities": [
        {{"id": "entity_id", "label": "Display Name", "type": "ALLOWED_TYPE", "properties": {{}}}}
    ],
    "relationships": [
        {{"source_id": "actor_id", "relation": "ALLOWED_RELATION", "target_id": "recipient_id"}}
    ],
    "insights": [
        {{
            "text": "Rich, contextual sentence worth remembering.",
            "topic": "preference|biographical|technical|constraint",
            "entities": ["entity1"],
            "confidence": 0.9,
            "sentiment": "positive|negative|neutral"
        }}
    ],
    "summary": "A 2-4 sentence summary of this conversation turn."
}}

If nothing meaningful is found, return empty arrays and empty string for summary. Quality over quantity — fewer accurate extractions are better than many noisy ones.
"""  # noqa: E501


class MemoryExtractor:
    """
    The Harvester - extracts memories from conversation turns.

    Parses live conversation stream to identify candidates for memory
    before they are forgotten. Uses LLM-based extraction for semantic
    understanding.

    Supports multiple extraction strategies:
    - Named Entity Recognition (NER)
    - Task State Extraction
    - Sentiment/Preference Extraction

    Example:
        from friday_llm import LiteLLMService

        llm = LiteLLMService(model_name="gpt-4-turbo")
        extractor = MemoryExtractor(
            memory_controller=memory,
            llm=llm,
        )
    """

    def __init__(
        self,
        memory_controller: MemoryController,
        llm: MemoryLLMClient,
        telemetry: TelemetryInterface | None = None,
        prompt_template: str | None = None,
        user_name: str = "User",
        assistant_name: str = "Assistant",
        embedding_model: "EmbeddingModel | None" = None,
        temperature: float | None = 0.0,
        max_tokens: int | None = None,
        ontology_config: OntologyConfig | None = None,
        rejection_log_path: str | None = None,
    ) -> None:
        """
        Initialize the Memory Extractor.

        Args:
            memory_controller: The memory controller for storing extracted data
            llm: LLMClient for extraction (injected dependency)
            telemetry: Optional telemetry recorder
            prompt_template: Custom extraction prompt template (uses default if None).
                             Must contain placeholders: {turn_id}, {timestamp},
                             {user_name}, {assistant_name}, {user_message},
                             {assistant_response}, {ontology_constraints}
            user_name: Name of the human user (for entity extraction)
            assistant_name: Name of the AI assistant (for entity extraction)
            embedding_model: Optional EmbeddingModel for pre-computing edge embeddings.
                            If provided, edge embeddings are computed during extraction
                            for fast graph path scoring at retrieval time.
            temperature: Optional request override; None uses service defaults.
            max_tokens: Optional maximum tokens for extraction response (limits output length)
            ontology_config: Ontology defining allowed node types and edge relations.
                            If None, uses OntologyConfig.default().
            rejection_log_path: File path for the extraction rejection log.
                               If provided, all rejected entities and relationships
                               are written to this file regardless of the global log
                               level.  Useful for offline ontology tuning.
        """  # noqa: E501
        self._memory = memory_controller
        self._llm = llm
        self._telemetry = telemetry
        self._prompt_template = prompt_template or DEFAULT_EXTRACTION_PROMPT
        self._user_name = user_name
        self._assistant_name = assistant_name
        self._embedding_model = embedding_model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._ontology = ontology_config or OntologyConfig.default()
        self._filter = ExtractionFilter(self._ontology)

        # Configure rejection file logging if a path was provided
        if rejection_log_path:
            configure_rejection_logging(rejection_log_path)

    def _emit_event(self, event_name: str, data: dict[str, Any]) -> None:
        """Emit telemetry event if recorder is configured."""
        if self._telemetry:
            self._telemetry.capture_event(event_name, data)

    def _parse_json_response(
        self,
        content: str,
        *,
        reasoning_content: str | None = None,
    ) -> dict[str, Any]:
        """
        Parse JSON from LLM response, handling various formats.

        Local LLMs often wrap JSON in markdown code blocks or add extra text.
        This method tries multiple strategies to extract valid JSON.
        """
        parse_content = content
        parsed = parse_json_object_from_text(parse_content)
        if parsed is not None:
            return parsed

        # Strategy 4: Try to repair truncated JSON
        # If JSON was cut off mid-way (token limit), try to salvage what we can
        repaired = self._repair_truncated_json(strip_llm_reasoning(parse_content))
        if repaired:
            return repaired

        # Strategy 5: Return empty extraction structure
        logger.warning(
            json_parse_warning_detail(
                "memory extraction",
                content,
                reasoning_content=reasoning_content,
            )
        )
        return {
            "entities": [],
            "facts": [],
            "preferences": [],
            "tasks": [],
            "relationships": [],
        }

    def _repair_truncated_json(self, content: str) -> dict[str, Any] | None:
        """
        Attempt to repair truncated JSON by closing unclosed brackets.

        When LLM response is cut off due to token limits, the JSON is often
        truncated mid-structure. This tries to salvage complete top-level arrays.
        """
        import re

        # Extract JSON portion (strip markdown)
        json_text = content
        code_block_match = re.search(r"```(?:json)?\s*([\s\S]*)", content)
        if code_block_match:
            json_text = code_block_match.group(1).rstrip("`").strip()

        # Find the opening brace
        brace_start = json_text.find("{")
        if brace_start == -1:
            return None

        json_text = json_text[brace_start:]

        # Try progressively truncating at array boundaries
        # Look for complete array entries we can salvage
        result: dict[str, Any] = {
            "entities": [],
            "relationships": [],
            "insights": [],
        }

        # Extract each top-level array that might be complete
        for key in ["entities", "relationships", "insights"]:
            pattern = rf'"{key}"\s*:\s*\[([\s\S]*?)(?:\]|\Z)'
            match = re.search(pattern, json_text)
            if match:
                array_content = match.group(1).strip()
                if array_content:
                    # Try to parse complete items from the array
                    items = self._extract_complete_items(array_content, key)
                    if items:
                        result[key] = items
                        logger.debug(f"Salvaged {len(items)} {key} from truncated JSON")

        # Only return if we salvaged something
        if any(result.values()):
            logger.info(
                f"Repaired truncated JSON: salvaged {sum(len(v) for v in result.values())} items"  # noqa: E501
            )
            return result

        return None

    def _extract_complete_items(self, array_content: str, key: str) -> list:
        """Extract complete JSON objects/strings from a potentially truncated array."""
        import re

        items = []

        if key == "insights":
            # Insights are strings, extract complete quoted strings
            string_pattern = r'"([^"\\]*(?:\\.[^"\\]*)*)"'
            for match in re.finditer(string_pattern, array_content):
                items.append(match.group(1))
        else:
            # Other fields are objects, extract complete {...} blocks
            depth = 0
            start = None
            for i, char in enumerate(array_content):
                if char == "{":
                    if depth == 0:
                        start = i
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0 and start is not None:
                        obj_str = array_content[start : i + 1]
                        try:  # noqa: SIM105
                            items.append(json.loads(obj_str))
                        except json.JSONDecodeError:
                            pass  # Skip malformed objects
                        start = None

        return items

    async def extract(self, turn: InteractionTurn) -> dict[str, Any]:
        """
        Extract memories from an interaction turn.

        Uses LLM to analyze the conversation and extract:
        - Named entities (filtered by ontology)
        - Relationships (constrained to canonical types)
        - Insights (rich contextual observations)

        Args:
            turn: The interaction turn to analyze

        Returns:
            Dict with extraction results and statistics
        """
        span_id = None
        if self._telemetry:
            span_id = self._telemetry.start_span("memory_extraction")

        try:
            # Build extraction prompt from template with ontology constraints
            prompt = self._prompt_template.format(
                turn_id=turn.id,
                timestamp=turn.timestamp.isoformat() if turn.timestamp else "unknown",
                user_name=self._user_name,
                assistant_name=self._assistant_name,
                user_message=turn.user_message or "",
                assistant_response=turn.assistant_message or "",
                ontology_constraints=self._ontology.format_for_prompt(),
            )

            # Log what we're extracting (for debugging latency)
            user_len = len(turn.user_message or "")
            asst_len = len(turn.assistant_message or "")
            prompt_len = len(prompt)
            logger.info(
                f"Extraction input: user={user_len} chars, assistant={asst_len} chars, "
                f"total prompt={prompt_len} chars"
            )

            # Call LLM for extraction using injected client
            start_time = time.time()
            logger.debug("Calling LLM for extraction...")
            response = await complete_memory_request(
                self._llm,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise information extraction system. Always respond with valid JSON.",  # noqa: E501
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
            elapsed = time.time() - start_time
            logger.info(f"Extraction LLM call took {elapsed:.2f}s")
            logger.debug(
                "Extraction response received (content_chars=%d)",
                len(response.content or ""),
            )
            reasoning_content = getattr(response, "reasoning_content", None)
            if reasoning_content:
                logger.debug(
                    "Extraction response.reasoning_content chars: %d",
                    len(reasoning_content),
                )

            # Parse response - handle various LLM output formats
            content = response.content or ""
            if content:
                logger.debug(f"Extraction LLM response: {content[:500]}")
            elif reasoning_content:
                logger.debug("Extraction LLM response: content empty; reasoning present")
            else:
                logger.debug("Extraction LLM response: (empty)")
            extracted = self._parse_json_response(
                content,
                reasoning_content=reasoning_content,
            )

            # Once writes begin, keep this shared writer alive until the current
            # turn reaches a safe commit boundary.  The caller can observe the
            # retained cancellation request and stop before the next turn.
            commit_task = asyncio.create_task(self._store_extractions(turn, extracted))
            cancellation_pending = False
            while True:
                try:
                    stats = await asyncio.shield(commit_task)
                    break
                except asyncio.CancelledError:
                    if commit_task.cancelled():
                        raise
                    cancellation_pending = True
                    continue

            self._emit_event(
                "extraction_completed",
                {
                    "turn_id": turn.id,
                    "entities": len(extracted.get("entities", [])),
                    "relationships": len(extracted.get("relationships", [])),
                    "insights": len(extracted.get("insights", [])),
                    "tasks": len(extracted.get("tasks", [])),
                },
            )

            if cancellation_pending:
                raise ExtractionCommitCompletedUnderCancellation

            return {
                "extracted": extracted,
                "stats": stats,
            }

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return {"error": str(e), "extracted": {}, "stats": {}}
        finally:
            if span_id:
                self._telemetry.end_span(span_id)

    async def _store_extractions(
        self, turn: InteractionTurn, extracted: dict[str, Any]
    ) -> dict[str, int]:
        """
        Store extracted information in the memory system.

        Args:
            turn: Source interaction turn
            extracted: Extracted data from LLM

        Returns:
            Statistics about stored items
        """
        stats = {
            "nodes_created": 0,
            "nodes_skipped": 0,
            "nodes_rejected": 0,
            "edges_created": 0,
            "edges_skipped": 0,
            "edges_rejected": 0,
            "insights_stored": 0,
            "summaries_stored": 0,
        }

        # Create provenance for all extracted data
        provenance = ProvenanceMetadata(
            source_id=turn.id,
            source_type="extraction",
            confidence=0.8,  # LLM extraction confidence
            author_id="memory_extractor",
        )

        # Helper to find or create a node by label
        async def find_or_create_node(
            label: str,
            node_type: str = "entity",
            properties: dict | None = None,
        ) -> tuple[GraphNode, bool]:
            """Find existing node or create new one. Returns (node, was_created)."""
            existing = await self._memory.graph.find_by_label(label, node_type)
            if existing:
                last_turn = existing.properties.get("last_extraction_turn_id")
                same_origin = existing.provenance.source_id == turn.id
                if not same_origin and last_turn != turn.id:
                    existing.touch()
                    existing.properties["last_extraction_turn_id"] = turn.id
                    await self._memory.graph.update_node(existing)
                return existing, False

            # Create new node
            node = GraphNode(
                id=str(uuid.uuid4()),
                type=node_type,
                label=label,
                properties=properties or {},
                provenance=provenance,
            )
            await self._memory.store_fact(node)
            return node, True

        # Filter entities through ontology validation gate
        raw_entities = extracted.get("entities", [])
        entities, rejected_entities = self._filter.filter_entities(
            raw_entities, turn_id=turn.id
        )
        stats["nodes_rejected"] = len(rejected_entities)

        # Store entities as graph nodes (with deduplication)
        for entity in entities:
            try:
                label = entity.get("label", "unknown")
                node_type = entity.get("type", "entity")
                properties = entity.get("properties", {})

                _, was_created = await find_or_create_node(label, node_type, properties)
                if was_created:
                    stats["nodes_created"] += 1
                else:
                    stats["nodes_skipped"] += 1
                    logger.debug(f"Entity '{label}' already exists, touched hit_count")
            except Exception as e:
                logger.warning(f"Failed to store entity: {e}")

        # Filter relationships through ontology validation gate
        raw_relationships = extracted.get("relationships", [])
        relationships, rejected_rels = self._filter.filter_relationships(
            raw_relationships, turn_id=turn.id
        )
        stats["edges_rejected"] = len(rejected_rels)

        # Store relationships as graph edges (with node and edge deduplication)
        for rel in relationships:
            try:
                # Support both "source"/"target" and "source_id"/"target_id" formats
                source_label = rel.get("source") or rel.get("source_id", "unknown")
                target_label = rel.get("target") or rel.get("target_id", "unknown")

                # Find or create both nodes
                source_node, source_created = await find_or_create_node(source_label)
                target_node, target_created = await find_or_create_node(target_label)

                if source_created:
                    stats["nodes_created"] += 1
                if target_created:
                    stats["nodes_created"] += 1

                # Compute edge embedding if embedding model is available
                # This enables fast graph path scoring at retrieval time
                relation = rel.get("relation", "related_to")
                edge_embedding: list[float] | None = None
                if self._embedding_model is not None:
                    try:
                        # Create natural language representation of the edge
                        edge_text = f"{source_node.label} {relation.replace('_', ' ')} {target_node.label}"  # noqa: E501
                        embeddings = await self._embedding_model.embed_documents(
                            [edge_text]
                        )
                        edge_embedding = embeddings[0] if embeddings else None
                        logger.debug(f"Computed embedding for edge: {edge_text}")
                    except Exception as e:
                        logger.warning(f"Failed to compute edge embedding: {e}")

                # Create the edge (add_edge now has built-in deduplication)
                edge = GraphEdge(
                    source_id=source_node.id,
                    target_id=target_node.id,
                    relation=relation,
                    provenance=provenance,
                    embedding=edge_embedding,  # Pre-computed for fast path scoring
                )
                edge_added = await self._memory.graph.add_edge(edge)
                if edge_added:
                    stats["edges_created"] += 1
                else:
                    stats["edges_skipped"] += 1
                    logger.debug(
                        f"Skipped duplicate edge: {source_label} --[{relation}]--> {target_label}"  # noqa: E501
                    )
            except Exception as e:
                logger.warning(f"Failed to store relationship: {e}")

        # Store rich insights in vector store (for semantic search)
        # These should be full, contextual sentences - NOT micro-facts
        # Now supports structured insights with metadata (topic, sentiment, entities, confidence)  # noqa: E501
        insight_items: list[tuple[str, dict[str, Any]]] = []  # (text, metadata) pairs

        # Collect insights (supports both string and dict formats)
        for insight in extracted.get("insights", []):
            if isinstance(insight, str) and insight.strip():
                # Simple string format: "insight text" (legacy)
                insight_items.append((insight.strip(), {"type": "insight"}))
            elif isinstance(insight, dict) and insight.get("text"):
                # Structured format: {"text": "...", "topic": "...", "confidence": 0.95, ...}  # noqa: E501
                text = insight["text"].strip()
                metadata: dict[str, Any] = {"type": "insight"}
                if insight.get("topic"):
                    metadata["topic"] = insight["topic"]
                if insight.get("sentiment"):
                    metadata["sentiment"] = insight["sentiment"]
                if insight.get("confidence") is not None:
                    metadata["confidence"] = float(insight["confidence"])
                if insight.get("entities"):
                    # Store entities as semicolon-separated string for ChromaDB compatibility  # noqa: E501
                    metadata["entities_mentioned"] = ";".join(insight["entities"])
                insight_items.append((text, metadata))

        # Legacy support: convert old-style facts/preferences if present
        # (for backwards compatibility with existing prompts)
        for fact in extracted.get("facts", []):
            if isinstance(fact, dict):
                fact_text = f"{fact.get('subject', '')} {fact.get('predicate', '')} {fact.get('object', '')}"  # noqa: E501
                text = fact_text.strip()
                if text and len(text) > 10:  # Skip very short facts
                    insight_items.append(
                        (text, {"type": "insight", "topic": "technical"})
                    )

        for pref in extracted.get("preferences", []):
            if isinstance(pref, dict):
                pref_text = f"{self._user_name} {pref.get('sentiment', 'feels')} about {pref.get('topic', 'something')}: {pref.get('detail', '')}"  # noqa: E501
                text = pref_text.strip()
                if text:
                    insight_items.append(
                        (text, {"type": "insight", "topic": "preference"})
                    )

        # Store insights with metadata
        if insight_items:
            try:
                record_ids = [
                    self._extraction_record_id(turn.id, "insight", index)
                    for index in range(len(insight_items))
                ]
                stored = await self._memory.store_insights_batch_with_metadata(
                    insight_items,
                    provenance,
                    record_ids=record_ids,
                    upsert=True,
                )
                stats["insights_stored"] = stored
                logger.info(f"Batch stored {stored} insights in vector store")
            except Exception as e:
                logger.warning(f"Failed to batch store insights: {e}")
                # Retain the same stable identities if the batch path fails.
                for index, (text, metadata) in enumerate(insight_items):
                    try:
                        await self._memory.store_insight(
                            text,
                            provenance,
                            metadata,
                            record_id=record_ids[index],
                            upsert=True,
                        )
                        stats["insights_stored"] += 1
                    except Exception as e2:
                        logger.warning(f"Failed to store insight: {e2}")

        # Store turn summary in vector store (with type="summary")
        summary = extracted.get("summary", "")
        if summary and isinstance(summary, str) and summary.strip():
            try:
                summary_metadata = {
                    "type": "summary",
                    "turn_id": turn.id,
                }
                await self._memory.store_insight(
                    summary.strip(),
                    provenance,
                    summary_metadata,
                    record_id=self._extraction_record_id(turn.id, "summary", 0),
                    upsert=True,
                )
                stats["summaries_stored"] = 1
                logger.info("Stored turn summary in vector store")
            except Exception as e:
                logger.warning(f"Failed to store summary: {e}")

        # Task storage removed — tasks created too much graph noise
        # (0% engagement rate on task nodes). Tasks are better tracked
        # outside the knowledge graph.

        return stats

    @staticmethod
    def _extraction_record_id(turn_id: str, kind: str, index: int) -> str:
        """Return the stable vector identity for one extraction output slot."""
        return str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                f"friday:extraction:v1:{turn_id}:{kind}:{index}",
            )
        )

    async def extract_entities_only(self, text: str) -> list[str]:
        """
        Quick entity extraction from text without full analysis.

        Useful for query enhancement in the recall loop.

        Args:
            text: Text to extract entities from

        Returns:
            List of entity names
        """
        try:
            response = await complete_memory_request(
                self._llm,
                messages=[
                    {
                        "role": "system",
                        "content": "Extract named entities from the text. Return a JSON object with an 'entities' key containing an array of strings.",  # noqa: E501
                    },
                    {"role": "user", "content": text},
                ],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
            result = parse_json_object_from_text(json_response_text(response)) or {}
            return result.get("entities", [])
        except Exception as e:
            logger.warning(f"Quick entity extraction failed: {e}")
            return []
