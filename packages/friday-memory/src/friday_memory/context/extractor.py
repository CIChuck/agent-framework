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


# Extraction prompt template
EXTRACTION_PROMPT = """Analyze the following conversation turn and extract structured information.

Turn ID: {turn_id}
Timestamp: {timestamp}

User Message:
{user_message}

Assistant Response:
{assistant_response}

Extract the following (if present):

1. **Named Entities**: People, organizations, projects, technologies, files, or other specific nouns.
2. **Facts**: Explicit statements of truth (e.g., "The API key is XYZ", "The deadline is Friday").
3. **Preferences**: User preferences or opinions (e.g., "I prefer Python", "I hate red").
4. **Tasks**: Mentioned tasks or goals (e.g., "Need to fix the login bug").
5. **Relationships**: Connections between entities (e.g., "Alice works on Project X").

Respond in JSON format:
{{
    "entities": [
        {{"label": "entity name", "type": "person|project|technology|file|organization|concept", "properties": {{}}}},
    ],
    "facts": [
        {{"subject": "entity", "predicate": "relation", "object": "value"}},
    ],
    "preferences": [
        {{"topic": "what", "sentiment": "positive|negative|neutral", "detail": "specifics"}},
    ],
    "tasks": [
        {{"description": "task description", "status": "pending|completed|blocked"}},
    ],
    "relationships": [
        {{"source": "entity1", "relation": "relation_type", "target": "entity2"}},
    ]
}}

If nothing relevant is found, return empty arrays. Be conservative - only extract clear, explicit information.
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
    ) -> None:
        """
        Initialize the Memory Extractor.

        Args:
            memory_controller: The memory controller for storing extracted data
            llm: LLMClient for extraction (injected dependency)
            telemetry: Optional telemetry recorder
        """
        self._memory = memory_controller
        self._llm = llm
        self._telemetry = telemetry

    def _emit_event(self, event_name: str, data: dict[str, Any]) -> None:
        """Emit telemetry event if recorder is configured."""
        if self._telemetry:
            self._telemetry.capture_event(event_name, data)

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
            # Build extraction prompt
            prompt = EXTRACTION_PROMPT.format(
                turn_id=turn.id,
                timestamp=turn.timestamp.isoformat() if turn.timestamp else "unknown",
                user_message=turn.user_message or "",
                assistant_response=turn.assistant_response or "",
            )

            # Call LLM for extraction using injected client
            response = await self._llm.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a precise information extraction system. Always respond with valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,  # Deterministic extraction
            )

            # Parse response
            content = response.content or "{}"
            extracted = json.loads(content)

            # Store extracted data
            stats = await self._store_extractions(turn, extracted)

            self._emit_event(
                "extraction_completed",
                {
                    "turn_id": turn.id,
                    "entities": len(extracted.get("entities", [])),
                    "facts": len(extracted.get("facts", [])),
                    "preferences": len(extracted.get("preferences", [])),
                    "tasks": len(extracted.get("tasks", [])),
                    "relationships": len(extracted.get("relationships", [])),
                },
            )

            return {
                "extracted": extracted,
                "stats": stats,
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse extraction response: {e}")
            return {"error": str(e), "extracted": {}, "stats": {}}
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
            "edges_created": 0,
            "insights_stored": 0,
        }

        # Create provenance for all extracted data
        provenance = ProvenanceMetadata(
            source_id=turn.id,
            source_type="extraction",
            confidence=0.8,  # LLM extraction confidence
            author_id="memory_extractor",
        )

        # Store entities as graph nodes
        for entity in extracted.get("entities", []):
            try:
                node = GraphNode(
                    id=str(uuid.uuid4()),
                    type=entity.get("type", "entity"),
                    label=entity.get("label", "unknown"),
                    properties=entity.get("properties", {}),
                    provenance=provenance,
                )
                await self._memory.store_fact(node)
                stats["nodes_created"] += 1
            except Exception as e:
                logger.warning(f"Failed to store entity: {e}")

        # Store relationships as graph edges
        for rel in extracted.get("relationships", []):
            try:
                # First ensure both nodes exist
                source_node = GraphNode(
                    id=str(uuid.uuid4()),
                    type="entity",
                    label=rel.get("source", "unknown"),
                    provenance=provenance,
                )
                target_node = GraphNode(
                    id=str(uuid.uuid4()),
                    type="entity",
                    label=rel.get("target", "unknown"),
                    provenance=provenance,
                )

                edge = GraphEdge(
                    source_id=source_node.id,
                    target_id=target_node.id,
                    relation=rel.get("relation", "related_to"),
                    provenance=provenance,
                )

                await self._memory.store_fact(source_node)
                await self._memory.store_fact(target_node, edge)
                stats["nodes_created"] += 2
                stats["edges_created"] += 1
            except Exception as e:
                logger.warning(f"Failed to store relationship: {e}")

        # Store facts as vector insights
        for fact in extracted.get("facts", []):
            try:
                fact_text = f"{fact.get('subject', '')} {fact.get('predicate', '')} {fact.get('object', '')}"
                await self._memory.store_insight(fact_text.strip(), provenance)
                stats["insights_stored"] += 1
            except Exception as e:
                logger.warning(f"Failed to store fact: {e}")

        # Store preferences as vector insights
        for pref in extracted.get("preferences", []):
            try:
                pref_text = f"User {pref.get('sentiment', 'has opinion on')} {pref.get('topic', 'something')}: {pref.get('detail', '')}"
                await self._memory.store_insight(pref_text.strip(), provenance)
                stats["insights_stored"] += 1
            except Exception as e:
                logger.warning(f"Failed to store preference: {e}")

        # Store tasks as graph nodes
        for task in extracted.get("tasks", []):
            try:
                node = GraphNode(
                    id=str(uuid.uuid4()),
                    type="task",
                    label=task.get("description", "unknown task"),
                    properties={"status": task.get("status", "pending")},
                    provenance=provenance,
                )
                await self._memory.store_fact(node)
                stats["nodes_created"] += 1
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
