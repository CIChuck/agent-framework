# mypy: ignore-errors
"""
Reorganization Logger.

Provides comprehensive logging for all actions taken during memory reorganization.
Supports multiple output formats (Markdown, JSON, CSV) and verbosity levels.
"""

import csv
import json
import logging
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any

from friday_memory.maintenance.models import (
    ActionLogEntry,
    ActionType,
    LogConfig,
    LogFormat,
    LogVerbosity,
)

logger = logging.getLogger(__name__)


class ReorganizationLogger:
    """
    Logger for reorganization actions.

    Collects ActionLogEntry records during reorganization and writes them
    to log files in the configured format (Markdown, JSON, or CSV).

    Verbosity levels control what details are included:
    - MINIMAL: Action summaries only (counts, high-level outcomes)
    - NORMAL: Summaries + IDs, content previews, and reasons
    - VERBOSE: Everything including full prompts, LLM responses, and config

    Example:
        config = LogConfig(
            enabled=True,
            log_directory="./logs",
            verbosity=LogVerbosity.NORMAL,
            format=LogFormat.MARKDOWN,
        )
        log = ReorganizationLogger(config, memory_dir="./memory")

        # Log actions during operations
        log.log_action(ActionLogEntry(
            action_type=ActionType.ENTITY_REMOVED,
            item_id="entity_123",
            item_type="entity",
            store="graph",
            reason="Stale entity with 0 hit count",
        ))

        # Write log file at end
        log_path = log.write_log()
    """

    def __init__(
        self,
        config: LogConfig | None = None,
        memory_dir: str | Path = ".",
    ) -> None:
        """
        Initialize the logger.

        Args:
            config: Logging configuration (uses defaults if None)
            memory_dir: Base directory for relative log paths
        """
        self._config = config or LogConfig()
        self._memory_dir = Path(memory_dir)
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._entries: list[ActionLogEntry] = []
        self._dry_run = False  # Set by components when in dry-run mode

    @property
    def enabled(self) -> bool:
        """Whether logging is enabled."""
        return self._config.enabled

    @property
    def verbosity(self) -> LogVerbosity:
        """Current verbosity level."""
        return self._config.verbosity

    @property
    def entries(self) -> list[ActionLogEntry]:
        """All logged entries."""
        return self._entries.copy()

    def set_dry_run(self, dry_run: bool) -> None:
        """Set the dry-run flag for subsequent entries."""
        self._dry_run = dry_run

    def log_action(self, entry: ActionLogEntry) -> None:
        """
        Log a single action.

        Args:
            entry: The action log entry to record
        """
        if not self._config.enabled:
            return

        # Set dry_run from logger state if not explicitly set
        if not entry.dry_run:
            entry.dry_run = self._dry_run

        self._entries.append(entry)
        logger.debug(f"Logged action: {entry.action_type.value} on {entry.item_id}")

    def log_entity_removed(
        self,
        entity_id: str,
        reason: str,
        content_preview: str | None = None,
        content_full: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Convenience method for logging entity removal."""
        self.log_action(
            ActionLogEntry(
                action_type=ActionType.ENTITY_REMOVED,
                item_id=entity_id,
                item_type="entity",
                store="graph",
                reason=reason,
                content_preview=content_preview,
                content_full=content_full,
                metadata=metadata or {},
                dry_run=self._dry_run,
            )
        )

    def log_entity_merged(
        self,
        primary_id: str,
        merged_ids: list[str],
        reason: str,
        content_preview: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Convenience method for logging entity merge."""
        self.log_action(
            ActionLogEntry(
                action_type=ActionType.ENTITY_MERGED,
                item_id=primary_id,
                item_type="entity",
                store="graph",
                merged_into_id=primary_id,
                merged_from_ids=merged_ids,
                reason=reason,
                content_preview=content_preview,
                metadata=metadata or {},
                dry_run=self._dry_run,
            )
        )

    def log_insight_removed(
        self,
        insight_id: str,
        reason: str,
        content_preview: str | None = None,
        content_full: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Convenience method for logging insight removal."""
        self.log_action(
            ActionLogEntry(
                action_type=ActionType.INSIGHT_REMOVED,
                item_id=insight_id,
                item_type="insight",
                store="vector",
                reason=reason,
                content_preview=content_preview,
                content_full=content_full,
                metadata=metadata or {},
                dry_run=self._dry_run,
            )
        )

    def log_edge_removed(
        self,
        edge_id: str,
        reason: str,
        content_preview: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Convenience method for logging edge removal."""
        self.log_action(
            ActionLogEntry(
                action_type=ActionType.EDGE_REMOVED,
                item_id=edge_id,
                item_type="edge",
                store="graph",
                reason=reason,
                content_preview=content_preview,
                metadata=metadata or {},
                dry_run=self._dry_run,
            )
        )

    def log_fact_classified(
        self,
        fact_id: str,
        falsifiable: bool,
        claim_type: str,
        reason: str,
        content_preview: str | None = None,
        prompt_sent: str | None = None,
        llm_response_raw: str | None = None,
        llm_response_parsed: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Convenience method for logging fact classification."""
        self.log_action(
            ActionLogEntry(
                action_type=ActionType.FACT_CLASSIFIED,
                item_id=fact_id,
                item_type="fact",
                store="vector",
                reason=reason,
                content_preview=content_preview,
                prompt_sent=prompt_sent,
                llm_response_raw=llm_response_raw,
                llm_response_parsed=llm_response_parsed,
                metadata={
                    "falsifiable": falsifiable,
                    "claim_type": claim_type,
                    **(metadata or {}),
                },
                dry_run=self._dry_run,
            )
        )

    def log_fact_verified(
        self,
        fact_id: str,
        verdict: str,
        confidence: float,
        reason: str,
        content_preview: str | None = None,
        evidence_summary: str | None = None,
        sources: list[str] | None = None,
        correction: str | None = None,
        prompt_sent: str | None = None,
        llm_response_raw: str | None = None,
        llm_response_parsed: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Convenience method for logging fact verification."""
        self.log_action(
            ActionLogEntry(
                action_type=ActionType.FACT_VERIFIED,
                item_id=fact_id,
                item_type="fact",
                store="vector",
                reason=reason,
                confidence=confidence,
                content_preview=content_preview,
                prompt_sent=prompt_sent,
                llm_response_raw=llm_response_raw,
                llm_response_parsed=llm_response_parsed,
                metadata={
                    "verdict": verdict,
                    "evidence_summary": evidence_summary,
                    "sources": sources or [],
                    "correction": correction,
                    **(metadata or {}),
                },
                dry_run=self._dry_run,
            )
        )

    def log_meta_insight_created(
        self,
        insight_id: str,
        content: str,
        source_ids: list[str],
        confidence: float,
        reason: str,
        prompt_sent: str | None = None,
        llm_response_raw: str | None = None,
        llm_response_parsed: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Convenience method for logging meta-insight creation."""
        self.log_action(
            ActionLogEntry(
                action_type=ActionType.META_INSIGHT_CREATED,
                item_id=insight_id,
                item_type="meta_insight",
                store="vector",
                reason=reason,
                confidence=confidence,
                content_preview=content[:200] if content else None,
                content_full=content,
                prompt_sent=prompt_sent,
                llm_response_raw=llm_response_raw,
                llm_response_parsed=llm_response_parsed,
                metadata={
                    "source_ids": source_ids,
                    **(metadata or {}),
                },
                dry_run=self._dry_run,
            )
        )

    def log_relationship_inferred(
        self,
        relationship_id: str,
        source_entity: str,
        relation: str,
        target_entity: str,
        confidence: float,
        reason: str,
        prompt_sent: str | None = None,
        llm_response_raw: str | None = None,
        llm_response_parsed: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Convenience method for logging relationship inference."""
        self.log_action(
            ActionLogEntry(
                action_type=ActionType.RELATIONSHIP_INFERRED,
                item_id=relationship_id,
                item_type="relationship",
                store="graph",
                reason=reason,
                confidence=confidence,
                content_preview=f"{source_entity} --[{relation}]--> {target_entity}",
                prompt_sent=prompt_sent,
                llm_response_raw=llm_response_raw,
                llm_response_parsed=llm_response_parsed,
                metadata={
                    "source_entity": source_entity,
                    "relation": relation,
                    "target_entity": target_entity,
                    **(metadata or {}),
                },
                dry_run=self._dry_run,
            )
        )

    def log_knowledge_gap_identified(
        self,
        gap_id: str,
        description: str,
        related_entities: list[str],
        priority: str,
        reason: str,
        prompt_sent: str | None = None,
        llm_response_raw: str | None = None,
        llm_response_parsed: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Convenience method for logging knowledge gap identification."""
        self.log_action(
            ActionLogEntry(
                action_type=ActionType.KNOWLEDGE_GAP_IDENTIFIED,
                item_id=gap_id,
                item_type="knowledge_gap",
                store="analysis",
                reason=reason,
                content_preview=description[:200] if description else None,
                content_full=description,
                prompt_sent=prompt_sent,
                llm_response_raw=llm_response_raw,
                llm_response_parsed=llm_response_parsed,
                metadata={
                    "related_entities": related_entities,
                    "priority": priority,
                    **(metadata or {}),
                },
                dry_run=self._dry_run,
            )
        )

    def log_backup_created(
        self,
        backup_id: str,
        backup_dir: str,
        file_count: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Convenience method for logging backup creation."""
        self.log_action(
            ActionLogEntry(
                action_type=ActionType.BACKUP_CREATED,
                item_id=backup_id,
                item_type="backup",
                store="all",
                reason="Pre-reorganization backup",
                content_preview=f"Backup to {backup_dir} ({file_count} files)",
                metadata={
                    "backup_dir": backup_dir,
                    "file_count": file_count,
                    **(metadata or {}),
                },
                dry_run=False,  # Backups are always real
            )
        )

    def get_log_directory(self) -> Path:
        """Get the resolved log directory path."""
        log_dir = Path(self._config.log_directory)
        if not log_dir.is_absolute():
            log_dir = self._memory_dir / log_dir
        return log_dir

    def get_log_filename(self) -> str:
        """Generate the log filename based on format."""
        extension = {
            LogFormat.MARKDOWN: "md",
            LogFormat.JSON: "json",
            LogFormat.CSV: "csv",
        }[self._config.format]
        return f"reorganization_{self._session_id}.{extension}"

    def write_log(self) -> Path | None:
        """
        Write the accumulated log entries to a file.

        Returns:
            Path to the written log file, or None if logging disabled/no entries
        """
        if not self._config.enabled or not self._entries:
            return None

        log_dir = self.get_log_directory()
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / self.get_log_filename()

        logger.info(f"Writing {len(self._entries)} log entries to {log_path}")

        if self._config.format == LogFormat.MARKDOWN:
            content = self._format_markdown()
        elif self._config.format == LogFormat.JSON:
            content = self._format_json()
        else:  # CSV
            content = self._format_csv()

        log_path.write_text(content, encoding="utf-8")
        return log_path

    def _format_markdown(self) -> str:
        """Format log entries as Markdown."""
        lines = [
            "# Memory Reorganization Log",
            "",
            f"**Session ID:** {self._session_id}",
            f"**Generated:** {datetime.now().isoformat()}",
            f"**Verbosity:** {self._config.verbosity.value}",
            f"**Total Actions:** {len(self._entries)}",
            "",
        ]

        # Summary section
        lines.extend(self._format_markdown_summary())

        # Detailed entries section
        lines.extend(
            [
                "",
                "---",
                "",
                "## Action Details",
                "",
            ]
        )

        for i, entry in enumerate(self._entries, 1):
            lines.extend(self._format_markdown_entry(i, entry))

        return "\n".join(lines)

    def _format_markdown_summary(self) -> list[str]:
        """Generate summary statistics for Markdown."""
        lines = ["## Summary", ""]

        # Count by action type
        action_counts: dict[str, int] = {}
        dry_run_count = 0
        for entry in self._entries:
            action_counts[entry.action_type.value] = (
                action_counts.get(entry.action_type.value, 0) + 1
            )
            if entry.dry_run:
                dry_run_count += 1

        lines.append("### Actions by Type")
        lines.append("")
        lines.append("| Action Type | Count |")
        lines.append("|-------------|-------|")
        for action_type, count in sorted(action_counts.items()):
            lines.append(f"| {action_type} | {count} |")

        lines.extend(
            [
                "",
                f"**Dry Run Actions:** {dry_run_count}",
                f"**Executed Actions:** {len(self._entries) - dry_run_count}",
            ]
        )

        return lines

    def _format_markdown_entry(self, index: int, entry: ActionLogEntry) -> list[str]:
        """Format a single entry as Markdown."""
        lines = [
            f"### {index}. {entry.action_type.value}",
            "",
            f"- **Time:** {entry.timestamp.isoformat()}",
            f"- **Item ID:** `{entry.item_id}`",
            f"- **Item Type:** {entry.item_type}",
            f"- **Store:** {entry.store}",
            f"- **Dry Run:** {'Yes' if entry.dry_run else 'No'}",
        ]

        if entry.reason:
            lines.append(f"- **Reason:** {entry.reason}")

        if entry.confidence is not None:
            lines.append(f"- **Confidence:** {entry.confidence:.2%}")

        # Normal verbosity: add content preview
        if self._config.verbosity in (LogVerbosity.NORMAL, LogVerbosity.VERBOSE):
            if entry.content_preview:
                lines.extend(
                    [
                        "",
                        "**Content Preview:**",
                        "```",
                        entry.content_preview,
                        "```",
                    ]
                )

            if entry.merged_into_id:
                lines.append(f"- **Merged Into:** `{entry.merged_into_id}`")
            if entry.merged_from_ids:
                merged_ids = ", ".join(f"`{id}`" for id in entry.merged_from_ids)
                lines.append(f"- **Merged From:** {merged_ids}")

            if entry.metadata:
                lines.extend(
                    [
                        "",
                        "**Metadata:**",
                        "```json",
                        json.dumps(entry.metadata, indent=2, default=str),
                        "```",
                    ]
                )

        # Verbose: add full content, prompts, and responses
        if self._config.verbosity == LogVerbosity.VERBOSE:
            if entry.content_full and entry.content_full != entry.content_preview:
                lines.extend(
                    [
                        "",
                        "**Full Content:**",
                        "```",
                        entry.content_full,
                        "```",
                    ]
                )

            if entry.prompt_sent:
                lines.extend(
                    [
                        "",
                        "**Prompt Sent to LLM:**",
                        "```",
                        entry.prompt_sent,
                        "```",
                    ]
                )

            if entry.llm_response_raw:
                lines.extend(
                    [
                        "",
                        "**Raw LLM Response:**",
                        "```",
                        entry.llm_response_raw,
                        "```",
                    ]
                )

            if entry.llm_response_parsed:
                lines.extend(
                    [
                        "",
                        "**Parsed LLM Response:**",
                        "```json",
                        json.dumps(entry.llm_response_parsed, indent=2, default=str),
                        "```",
                    ]
                )

            if entry.config_snapshot:
                lines.extend(
                    [
                        "",
                        "**Config Snapshot:**",
                        "```json",
                        json.dumps(entry.config_snapshot, indent=2, default=str),
                        "```",
                    ]
                )

        lines.append("")
        return lines

    def _format_json(self) -> str:
        """Format log entries as JSON."""
        output = {
            "session_id": self._session_id,
            "generated_at": datetime.now().isoformat(),
            "verbosity": self._config.verbosity.value,
            "total_actions": len(self._entries),
            "summary": self._get_summary_dict(),
            "entries": [],
        }

        for entry in self._entries:
            entry_dict = self._entry_to_dict(entry)
            output["entries"].append(entry_dict)

        return json.dumps(output, indent=2, default=str)

    def _get_summary_dict(self) -> dict[str, Any]:
        """Generate summary statistics as dict."""
        action_counts: dict[str, int] = {}
        dry_run_count = 0
        store_counts: dict[str, int] = {}

        for entry in self._entries:
            action_counts[entry.action_type.value] = (
                action_counts.get(entry.action_type.value, 0) + 1
            )
            store_counts[entry.store] = store_counts.get(entry.store, 0) + 1
            if entry.dry_run:
                dry_run_count += 1

        return {
            "actions_by_type": action_counts,
            "actions_by_store": store_counts,
            "dry_run_count": dry_run_count,
            "executed_count": len(self._entries) - dry_run_count,
        }

    def _entry_to_dict(self, entry: ActionLogEntry) -> dict[str, Any]:
        """Convert an entry to dict, respecting verbosity."""
        result: dict[str, Any] = {
            "timestamp": entry.timestamp.isoformat(),
            "action_type": entry.action_type.value,
            "dry_run": entry.dry_run,
            "item_id": entry.item_id,
            "item_type": entry.item_type,
            "store": entry.store,
            "reason": entry.reason,
        }

        if entry.confidence is not None:
            result["confidence"] = entry.confidence

        # Normal verbosity additions
        if self._config.verbosity in (LogVerbosity.NORMAL, LogVerbosity.VERBOSE):
            if entry.content_preview:
                result["content_preview"] = entry.content_preview
            if entry.merged_into_id:
                result["merged_into_id"] = entry.merged_into_id
            if entry.merged_from_ids:
                result["merged_from_ids"] = entry.merged_from_ids
            if entry.metadata:
                result["metadata"] = entry.metadata

        # Verbose additions
        if self._config.verbosity == LogVerbosity.VERBOSE:
            if entry.content_full:
                result["content_full"] = entry.content_full
            if entry.prompt_sent:
                result["prompt_sent"] = entry.prompt_sent
            if entry.llm_response_raw:
                result["llm_response_raw"] = entry.llm_response_raw
            if entry.llm_response_parsed:
                result["llm_response_parsed"] = entry.llm_response_parsed
            if entry.config_snapshot:
                result["config_snapshot"] = entry.config_snapshot

        return result

    def _format_csv(self) -> str:
        """Format log entries as CSV."""
        output = StringIO()

        # Define columns based on verbosity
        columns = [
            "timestamp",
            "action_type",
            "dry_run",
            "item_id",
            "item_type",
            "store",
            "reason",
            "confidence",
        ]

        if self._config.verbosity in (LogVerbosity.NORMAL, LogVerbosity.VERBOSE):
            columns.extend(
                [
                    "content_preview",
                    "merged_into_id",
                    "merged_from_ids",
                    "metadata",
                ]
            )

        if self._config.verbosity == LogVerbosity.VERBOSE:
            columns.extend(
                [
                    "content_full",
                    "prompt_sent",
                    "llm_response_raw",
                    "llm_response_parsed",
                    "config_snapshot",
                ]
            )

        writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()

        for entry in self._entries:
            row = {
                "timestamp": entry.timestamp.isoformat(),
                "action_type": entry.action_type.value,
                "dry_run": entry.dry_run,
                "item_id": entry.item_id,
                "item_type": entry.item_type,
                "store": entry.store,
                "reason": entry.reason,
                "confidence": entry.confidence if entry.confidence is not None else "",
            }

            if self._config.verbosity in (LogVerbosity.NORMAL, LogVerbosity.VERBOSE):
                row["content_preview"] = entry.content_preview or ""
                row["merged_into_id"] = entry.merged_into_id or ""
                row["merged_from_ids"] = (
                    "|".join(entry.merged_from_ids) if entry.merged_from_ids else ""
                )
                row["metadata"] = (
                    json.dumps(entry.metadata, default=str) if entry.metadata else ""
                )

            if self._config.verbosity == LogVerbosity.VERBOSE:
                row["content_full"] = entry.content_full or ""
                row["prompt_sent"] = entry.prompt_sent or ""
                row["llm_response_raw"] = entry.llm_response_raw or ""
                row["llm_response_parsed"] = (
                    json.dumps(entry.llm_response_parsed, default=str)
                    if entry.llm_response_parsed
                    else ""
                )
                row["config_snapshot"] = (
                    json.dumps(entry.config_snapshot, default=str)
                    if entry.config_snapshot
                    else ""
                )

            writer.writerow(row)

        return output.getvalue()

    def clear(self) -> None:
        """Clear all logged entries (e.g., after writing)."""
        self._entries.clear()
