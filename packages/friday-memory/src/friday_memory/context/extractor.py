"""
Memory Extractor (The Harvester).
Analyzes conversation turns to extract new entities and facts for the Graph.

Ref: Batch 2a Specification, Section 3
Updated: Batch 3 - Now uses injected LLMClient protocol

Strategies:
1. Named Entity Extraction (NER): "User mentioned 'Project Alpha'."
2. Task State Extraction: "User completed task 'Fix Bug'."
3. Sentiment/Preference Extraction: "User expressed frustration with Python."
"""

import json
import logging
import time
import uuid
from typing import TYPE_CHECKING, Any

from friday_core import TelemetryInterface

from friday_memory.controller import MemoryController
from friday_memory.models import (
    GraphEdge,
    GraphNode,
    InteractionTurn,
    ProvenanceMetadata,
)

if TYPE_CHECKING:
    from friday_core.interfaces import LLMClient


logger = logging.getLogger(__name__)


# Default extraction prompt template (used if none provided in config)
# Storage strategy:
# - entities, relationships → Graph Store (structured, Hebbian learning via hit_count)
# - insights → Vector Store (rich semantic content for similarity search)
# - tasks → Graph Store (as task nodes)
DEFAULT_EXTRACTION_PROMPT = """Analyze the following conversation turn and extract structured information.

Turn ID: {turn_id}
Timestamp: {timestamp}

Conversation participants:
- Human user: {user_name}
- AI assistant: {assistant_name}

{user_name} said:
{user_message}

{assistant_name} replied:
{assistant_response}

Extract the following:

1. **Entities**: Named people, organizations, projects, technologies, or concepts mentioned.
   - Use "{user_name}" for the human, "{assistant_name}" for the AI
   - Include type: person, project, technology, organization, concept

2. **Relationships**: Directional connections between entities.
   - SOURCE performs action on TARGET (active voice)
   - Example: source="{user_name}", relation="creates", target="{assistant_name}"
   - Do NOT create reverse/duplicate relationships

3. **Insights**: Rich, contextual observations worth remembering (1-2 sentences each).
   - Write as complete, meaningful sentences
   - Include context that would be useful for future semantic search
   - Examples:
     - "{user_name} is building an AI assistant named {assistant_name} with persistent memory capabilities."
     - "{assistant_name} expressed enthusiasm about helping with coding tasks."
   - NOT micro-facts like "Chuck creates Friday" (those go in relationships)

4. **Tasks**: Mentioned tasks or goals with their status.

Respond ONLY with valid JSON:
{{
    "entities": [
        {{"label": "name", "type": "person|project|technology|organization|concept", "properties": {{}}}}
    ],
    "relationships": [
        {{"source": "actor", "relation": "verb", "target": "recipient"}}
    ],
    "insights": [
        "Rich, contextual sentence worth remembering for future reference."
    ],
    "tasks": [
        {{"description": "task description", "status": "pending|completed|blocked"}}
    ]
}}

If nothing relevant is found, return empty arrays. Be selective - only extract meaningful information.
"""


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
        llm: "LLMClient",
        telemetry: TelemetryInterface | None = None,
        prompt_template: str | None = None,
        user_name: str = "User",
        assistant_name: str = "Assistant",
    ) -> None:
        """
        Initialize the Memory Extractor.

        Args:
            memory_controller: The memory controller for storing extracted data
            llm: LLMClient for extraction (injected dependency)
            telemetry: Optional telemetry recorder
            prompt_template: Custom extraction prompt template (uses default if None).
                             Must contain placeholders: {turn_id}, {timestamp},
                             {user_name}, {assistant_name}, {user_message}, {assistant_response}
            user_name: Name of the human user (for entity extraction)
            assistant_name: Name of the AI assistant (for entity extraction)
        """
        self._memory = memory_controller
        self._llm = llm
        self._telemetry = telemetry
        self._prompt_template = prompt_template or DEFAULT_EXTRACTION_PROMPT
        self._user_name = user_name
        self._assistant_name = assistant_name

    def _emit_event(self, event_name: str, data: dict[str, Any]) -> None:
        """Emit telemetry event if recorder is configured."""
        if self._telemetry:
            self._telemetry.capture_event(event_name, data)

    def _parse_json_response(self, content: str) -> dict[str, Any]:
        """
        Parse JSON from LLM response, handling various formats.

        Local LLMs often wrap JSON in markdown code blocks or add extra text.
        This method tries multiple strategies to extract valid JSON.
        """
        import re

        # Strategy 1: Try direct parse
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Strategy 2: Extract from markdown code block
        # Match ```json ... ``` or ``` ... ```
        code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if code_block_match:
            try:
                return json.loads(code_block_match.group(1))
            except json.JSONDecodeError:
                pass

        # Strategy 3: Find JSON object in text (first { to last })
        brace_match = re.search(r'\{[\s\S]*\}', content)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass

        # Strategy 4: Return empty extraction structure
        logger.warning(f"Could not parse JSON from response: {content[:200]}...")
        return {
            "entities": [],
            "facts": [],
            "preferences": [],
            "tasks": [],
            "relationships": [],
        }

    async def extract(self, turn: InteractionTurn) -> dict[str, Any]:
        """
        Extract memories from an interaction turn.

        Uses LLM to analyze the conversation and extract:
        - Named entities
        - Facts
        - Preferences
        - Tasks
        - Relationships

        Args:
            turn: The interaction turn to analyze

        Returns:
            Dict with extraction results and statistics
        """
        span_id = None
        if self._telemetry:
            span_id = self._telemetry.start_span("memory_extraction")

        try:
            # Build extraction prompt from template
            prompt = self._prompt_template.format(
                turn_id=turn.id,
                timestamp=turn.timestamp.isoformat() if turn.timestamp else "unknown",
                user_name=self._user_name,
                assistant_name=self._assistant_name,
                user_message=turn.user_message or "",
                assistant_response=turn.assistant_message or "",
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
            response = await self._llm.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a precise information extraction system. Always respond with valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,  # Deterministic extraction
            )
            elapsed = time.time() - start_time
            logger.info(f"Extraction LLM call took {elapsed:.2f}s")
            logger.debug(f"Extraction response object: {response}")
            logger.debug(f"Extraction response type: {type(response)}")
            logger.debug(f"Extraction response.content: {response.content!r}")

            # Parse response - handle various LLM output formats
            content = response.content or ""
            logger.debug(f"Extraction LLM response: {content[:500] if content else '(empty)'}")
            extracted = self._parse_json_response(content)

            # Store extracted data
            stats = await self._store_extractions(turn, extracted)

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
            "edges_created": 0,
            "edges_skipped": 0,
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
                # Touch the node to update hit_count (Hebbian learning)
                existing.touch()
                # Persist the updated hit_count back to the graph store
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

        # Store entities as graph nodes (with deduplication)
        for entity in extracted.get("entities", []):
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

        # Store relationships as graph edges (with node and edge deduplication)
        for rel in extracted.get("relationships", []):
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

                # Create the edge (add_edge now has built-in deduplication)
                edge = GraphEdge(
                    source_id=source_node.id,
                    target_id=target_node.id,
                    relation=rel.get("relation", "related_to"),
                    provenance=provenance,
                )
                edge_added = await self._memory.graph.add_edge(edge)
                if edge_added:
                    stats["edges_created"] += 1
                else:
                    stats["edges_skipped"] += 1
                    logger.debug(
                        f"Skipped duplicate edge: {source_label} --[{rel.get('relation')}]--> {target_label}"
                    )
            except Exception as e:
                logger.warning(f"Failed to store relationship: {e}")

        # Store rich insights in vector store (for semantic search)
        # These should be full, contextual sentences - NOT micro-facts
        # Now supports structured insights with metadata (topic, sentiment, entities, confidence)
        insight_items: list[tuple[str, dict[str, Any]]] = []  # (text, metadata) pairs

        # Collect insights (supports both string and dict formats)
        for insight in extracted.get("insights", []):
            if isinstance(insight, str) and insight.strip():
                # Simple string format: "insight text" (legacy)
                insight_items.append((insight.strip(), {"type": "insight"}))
            elif isinstance(insight, dict) and insight.get("text"):
                # Structured format: {"text": "...", "topic": "...", "confidence": 0.95, ...}
                text = insight["text"].strip()
                metadata: dict[str, Any] = {"type": "insight"}
                if insight.get("topic"):
                    metadata["topic"] = insight["topic"]
                if insight.get("sentiment"):
                    metadata["sentiment"] = insight["sentiment"]
                if insight.get("confidence") is not None:
                    metadata["confidence"] = float(insight["confidence"])
                if insight.get("entities"):
                    # Store entities as semicolon-separated string for ChromaDB compatibility
                    metadata["entities_mentioned"] = ";".join(insight["entities"])
                insight_items.append((text, metadata))

        # Legacy support: convert old-style facts/preferences if present
        # (for backwards compatibility with existing prompts)
        for fact in extracted.get("facts", []):
            if isinstance(fact, dict):
                fact_text = f"{fact.get('subject', '')} {fact.get('predicate', '')} {fact.get('object', '')}"
                text = fact_text.strip()
                if text and len(text) > 10:  # Skip very short facts
                    insight_items.append((text, {"type": "insight", "topic": "technical"}))

        for pref in extracted.get("preferences", []):
            if isinstance(pref, dict):
                pref_text = f"{self._user_name} {pref.get('sentiment', 'feels')} about {pref.get('topic', 'something')}: {pref.get('detail', '')}"
                text = pref_text.strip()
                if text:
                    insight_items.append((text, {"type": "insight", "topic": "preference"}))

        # Store insights with metadata
        if insight_items:
            try:
                stored = await self._memory.store_insights_batch_with_metadata(
                    insight_items, provenance
                )
                stats["insights_stored"] = stored
                logger.info(f"Batch stored {stored} insights in vector store")
            except AttributeError:
                # Fall back to simple batch storage if new method not available
                texts = [text for text, _ in insight_items]
                stored = await self._memory.store_insights_batch(texts, provenance)
                stats["insights_stored"] = stored
                logger.info(f"Batch stored {stored} insights (without metadata)")
            except Exception as e:
                logger.warning(f"Failed to batch store insights: {e}")
                # Fall back to individual storage
                for text, metadata in insight_items:
                    try:
                        await self._memory.store_insight(text, provenance, metadata)
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
                await self._memory.store_insight(summary.strip(), provenance, summary_metadata)
                stats["summaries_stored"] = 1
                logger.info(f"Stored turn summary in vector store")
            except Exception as e:
                logger.warning(f"Failed to store summary: {e}")

        # Store tasks as graph nodes (with deduplication)
        for task in extracted.get("tasks", []):
            try:
                label = task.get("description", "unknown task")
                properties = {"status": task.get("status", "pending")}

                _, was_created = await find_or_create_node(label, "task", properties)
                if was_created:
                    stats["nodes_created"] += 1
                else:
                    stats["nodes_skipped"] += 1
                    logger.debug(f"Task '{label}' already exists, touched hit_count")
            except Exception as e:
                logger.warning(f"Failed to store task: {e}")

        return stats

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
            response = await self._llm.chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "Extract named entities from the text. Return a JSON object with an 'entities' key containing an array of strings.",
                    },
                    {"role": "user", "content": text},
                ],
                temperature=0.0,
            )
            content = response.content or "{}"
            result = json.loads(content)
            return result.get("entities", [])
        except Exception as e:
            logger.warning(f"Quick entity extraction failed: {e}")
            return []
