"""
Post-processing validation gate for memory extraction.

Filters extracted entities and relationships against the configured ontology
before they are stored in the knowledge graph. Purely programmatic — no LLM
calls, zero additional latency.

All rejected items are logged to a dedicated rejection logger for offline
analysis and ontology tuning. The rejection logger operates independently
of the global log level so that rejections are always captured when a log
file is configured via ``configure_rejection_logging()``.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from friday_memory.context.ontology import OntologyConfig

logger = logging.getLogger(__name__)
rejection_logger = logging.getLogger("friday_memory.extraction.rejections")

# Prevent rejection logs from bubbling up to the root logger when no
# file handler is configured (avoids duplicate console output).
rejection_logger.propagate = False


def configure_rejection_logging(log_path: str | Path) -> None:
    """Attach a file handler to the rejection logger.

    This ensures extraction rejections are always written to disk regardless
    of the global log level.  Safe to call multiple times — duplicate
    handlers are avoided by checking existing handler paths.

    Args:
        log_path: File path for the rejection log.  Parent directories are
                  created automatically if they don't exist.
    """
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Guard against duplicate handlers if called more than once
    resolved = str(log_path.resolve())
    for handler in rejection_logger.handlers:
        if (
            isinstance(handler, logging.FileHandler)
            and handler.baseFilename == resolved
        ):
            return  # Already configured

    file_handler = logging.FileHandler(str(log_path), encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    # Force the logger to process all messages irrespective of the
    # global root level.
    rejection_logger.setLevel(logging.DEBUG)
    rejection_logger.addHandler(file_handler)

    logger.info("Rejection log configured: %s", log_path)

# Pattern matching timestamps like "1:30 PM", "14:00", "2024-01-15"
TIMESTAMP_PATTERN = re.compile(
    r"^\d{1,2}:\d{2}(\s*(AM|PM|am|pm))?$"  # time patterns
    r"|^\d{4}-\d{2}-\d{2}"  # ISO date patterns
    r"|^\d{1,2}/\d{1,2}/\d{2,4}$"  # date patterns MM/DD/YYYY
)

# Pattern matching purely numeric strings
NUMERIC_PATTERN = re.compile(r"^\d+(\.\d+)?$")


class ExtractionFilter:
    """Validates extracted entities and relationships against the ontology.

    Applies programmatic filtering rules to remove noisy extractions before
    they reach the graph store. Logs all rejections to a dedicated logger
    for later analysis and ontology tuning.

    Args:
        ontology: The ontology configuration defining allowed types and relations.
    """

    def __init__(self, ontology: OntologyConfig) -> None:
        self._ontology = ontology
        # Pre-compute uppercase canonical relations for fast lookup
        self._canonical_upper: dict[str, str] = {}
        for relation in ontology.all_edge_relations:
            self._canonical_upper[relation.upper()] = relation

    def filter_entities(
        self,
        entities: list[dict[str, Any]],
        turn_id: str = "",
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Filter entities against the ontology.

        Args:
            entities: List of entity dicts from LLM extraction.
            turn_id: Source turn ID for rejection logging.

        Returns:
            Tuple of (accepted, rejected) entity lists.
        """
        accepted: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []

        for entity in entities:
            label = entity.get("label", "")
            node_type = entity.get("type", "")
            reason = self._check_entity(label, node_type)

            if reason is None:
                accepted.append(entity)
            else:
                rejected.append(entity)
                rejection_logger.info(
                    "Rejected node: type=%r label=%r reason=%r turn_id=%r",
                    node_type,
                    label,
                    reason,
                    turn_id,
                )

        if rejected:
            logger.debug(
                "Filtered %d/%d entities (turn=%s)",
                len(rejected),
                len(entities),
                turn_id,
            )

        return accepted, rejected

    def filter_relationships(
        self,
        relationships: list[dict[str, Any]],
        turn_id: str = "",
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Filter relationships against the ontology and normalize relation names.

        Accepted relationships have their `relation` field normalized to the
        canonical form (uppercase).

        Args:
            relationships: List of relationship dicts from LLM extraction.
            turn_id: Source turn ID for rejection logging.

        Returns:
            Tuple of (accepted, rejected) relationship lists.
        """
        accepted: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []

        for rel in relationships:
            relation = rel.get("relation", "")
            normalized = self._normalize_relation(relation)

            if normalized is not None:
                # Update the relation to canonical form
                rel_copy = dict(rel)
                rel_copy["relation"] = normalized
                accepted.append(rel_copy)
            else:
                rejected.append(rel)
                source = rel.get("source") or rel.get("source_id", "?")
                target = rel.get("target") or rel.get("target_id", "?")
                rejection_logger.info(
                    "Rejected edge: relation=%r source=%r target=%r "
                    "reason='relation not in ontology' turn_id=%r",
                    relation,
                    source,
                    target,
                    turn_id,
                )

        if rejected:
            logger.debug(
                "Filtered %d/%d relationships (turn=%s)",
                len(rejected),
                len(relationships),
                turn_id,
            )

        return accepted, rejected

    def _check_entity(self, label: str, node_type: str) -> str | None:
        """Check if an entity passes all validation rules.

        Args:
            label: The entity label.
            node_type: The entity type.

        Returns:
            None if valid, or a rejection reason string.
        """
        # Check type is allowed
        if node_type.lower() not in self._ontology.allowed_node_types:
            return f"type not allowed: {node_type}"

        # Check label length
        if len(label) < self._ontology.min_label_length:
            return f"label too short: {len(label)} < {self._ontology.min_label_length}"

        if len(label) > self._ontology.max_label_length:
            return f"label too long: {len(label)} > {self._ontology.max_label_length}"

        # Check blocklist (case-insensitive exact match)
        label_lower = label.lower().strip()
        for blocked in self._ontology.label_blocklist:
            if label_lower == blocked.lower():
                return f"label in blocklist: {blocked}"

        # Check purely numeric
        if NUMERIC_PATTERN.match(label):
            return "label is purely numeric"

        # Check timestamp pattern
        if TIMESTAMP_PATTERN.match(label):
            return "label matches timestamp pattern"

        return None

    def _normalize_relation(self, relation: str) -> str | None:
        """Normalize a relation name to the nearest canonical form.

        Tries in order:
        1. Exact match (case-insensitive)
        2. Underscore/space normalization then case-insensitive match

        Args:
            relation: The relation string from LLM extraction.

        Returns:
            The canonical relation name, or None if no match found.
        """
        if not relation:
            return None

        # Normalize: strip, uppercase, replace spaces with underscores
        normalized = relation.strip().upper().replace(" ", "_")

        # Direct lookup
        if normalized in self._canonical_upper:
            return self._canonical_upper[normalized]

        # Try without underscores (e.g., "WORKSAT" → "WORKS_AT")
        no_underscore = normalized.replace("_", "")
        for canonical_upper, canonical in self._canonical_upper.items():
            if canonical_upper.replace("_", "") == no_underscore:
                return canonical

        return None
