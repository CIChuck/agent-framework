"""
Agent-level output processing for sanitization.

Bridges friday-core security utilities with friday-agent execution flow.
"""

from __future__ import annotations

from typing import Any

from friday_core.security import (
    QuarantineStore,
    SanitizationConfig,
    SanitizationResult,
    ToolOutputSanitizer,
)


class AgentOutputProcessor:
    """
    Processes tool outputs before they reach the LLM.

    Used by AgentBase._execute_tool_call() to sanitize results.
    """

    def __init__(
        self,
        config: SanitizationConfig | None = None,
        telemetry: Any = None,  # TelemetryInterface
    ) -> None:
        """
        Initialize the output processor.

        Args:
            config: Optional sanitization configuration.
            telemetry: Optional telemetry interface.
        """
        self.sanitizer = ToolOutputSanitizer(config)
        self.telemetry = telemetry
        self._quarantine_store: QuarantineStore | None = None

        if (
            self.sanitizer.config.storage_policy.store_raw_on_detection
            and self.sanitizer.config.storage_policy.raw_store_mode == "quarantine"
            and self.sanitizer.config.storage_policy.quarantine_path
        ):
            self._quarantine_store = QuarantineStore(
                self.sanitizer.config.storage_policy.quarantine_path
            )

    def process(
        self,
        content: str,
        tool_name: str,
        tool_category: str,
    ) -> tuple[str, dict[str, Any]]:
        """
        Process tool output for safe LLM consumption.

        Args:
            content: Raw tool output.
            tool_name: Source tool name.
            tool_category: Source tool category.

        Returns:
            Tuple of (sanitized_content, security_metadata).

        Raises:
            ValueError: If tool_category is missing or uncategorized.
        """
        if not tool_category or tool_category == "uncategorized":
            raise ValueError(
                f"Tool '{tool_name}' must declare a non-default category."
            )

        result: SanitizationResult = self.sanitizer.sanitize(
            content, tool_name, tool_category
        )

        # Emit telemetry for detections
        if self.telemetry and result.detections:
            self.telemetry.capture_event(
                "security_injection_detected",
                {
                    "tool_name": tool_name,
                    "tool_category": tool_category,
                    "detection_count": len(result.detections),
                    "patterns": [d["pattern_name"] for d in result.detections],
                    "action": self.sanitizer.config.quarantine.action,
                },
            )

        metadata = {
            "source_tool": tool_name,
            "tool_category": tool_category,
            "risk_level": result.risk_level.value,
            "was_sanitized": result.was_modified,
            "injection_detected": len(result.detections) > 0,
        }

        if result.detections:
            metadata["detection_patterns"] = [
                d["pattern_name"] for d in result.detections
            ]

            if self._quarantine_store:
                self._quarantine_store.append(
                    content=result.original_content,
                    tool_name=tool_name,
                    tool_category=tool_category,
                    risk_level=result.risk_level.value,
                    detected_patterns=[d["pattern_name"] for d in result.detections],
                    metadata=metadata,
                )

        return result.sanitized_content, metadata
