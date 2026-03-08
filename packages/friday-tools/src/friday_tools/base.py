# mypy: ignore-errors
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from friday_core.interfaces import ToolDefinition
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ToolResult(BaseModel):
    """
    Standardized return object for all Friday Tools.

    Attributes:
        content: The human-readable string representation (for LLM context).
        data: The raw structured data (for Memory/Code analysis).
        metadata: Additional context (e.g., execution time, source IDs).
        error: Optional error message if execution failed.
    """

    content: str
    data: Any | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None

    def __str__(self) -> str:
        """String representation prioritizes content or error."""
        if self.error:
            return f"Error: {self.error}"
        return self.content


class FridayTool(ToolDefinition, ABC):
    """
    Abstract base class for Friday Tools with automatic Pydantic Schema generation.

    Subclasses must:
    1. Define `name` and `description`.
    2. Define `Input` (a Pydantic BaseModel) as a class attribute.
    3. Implement `run(self, args: Input) -> ToolResult`.

    Optional:
    - Define `category` (default: "uncategorized")
    - Define `tags` (default: [])
    """

    name: str
    description: str
    category: str = "uncategorized"
    tags: list[str] = []
    Input: type[BaseModel]

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """Generate JSON Schema from the Input Pydantic model."""
        return self.Input.model_json_schema()

    def to_schema(self, format: str = "plain") -> dict[str, Any]:
        """
        Convert tool to JSON schema format.

        Args:
            format: "plain" (default) or "openai".
        """
        base_schema = {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema,
            "category": self.category,
            "tags": self.tags,
        }

        if format == "openai":
            return {
                "type": "function",
                "function": {
                    "name": self.name,
                    "description": self.description,
                    "parameters": self.parameters_schema,
                },
                "category": self.category,
                "tags": self.tags,
            }
        return base_schema

    async def execute(self, **kwargs: Any) -> str:
        """Execute the tool. This is the entry point for Agents.

        Handles validation (kwargs -> Input model), execution
        (calling ``run()``), and serialization (ToolResult -> str).

        Includes a recovery path for ``{"raw": ...}`` arguments
        produced when the LLM service layer fails to parse tool
        call JSON (e.g. truncated output from models with
        content-length limits).  Also logs diagnostic details on
        validation or execution failure.

        Args:
            **kwargs: Raw keyword arguments from the LLM tool call.

        Returns:
            String content for the LLM — either the ToolResult
            content or a descriptive error message.
        """
        # Defense-in-depth: if the LLM service couldn't parse
        # the tool arguments and wrapped them as {"raw": ...},
        # try to extract the actual fields from the raw string.
        if "raw" in kwargs and len(kwargs) == 1:
            recovered = self._recover_raw_args(kwargs["raw"])
            if recovered is not None:
                kwargs = recovered

        try:
            validated_args = self.Input(**kwargs)
        except Exception as e:
            arg_summary = {
                k: (
                    f"<{type(v).__name__}, len={len(v)}>"
                    if isinstance(v, str) and len(v) > 200
                    else v
                )
                for k, v in kwargs.items()
            }
            logger.error(
                "Tool '%s' input validation failed: %s | args=%s",
                self.name,
                e,
                arg_summary,
            )
            return f"Error executing tool '{self.name}': {e}"

        try:
            result = await self.run(validated_args)
            return str(result)
        except Exception as e:
            logger.error(
                "Tool '%s' execution failed: %s",
                self.name,
                e,
                exc_info=True,
            )
            return f"Error executing tool '{self.name}': {e}"

    @staticmethod
    def _recover_raw_args(
        raw: str,
    ) -> dict[str, Any] | None:
        """Attempt to parse a raw JSON string into tool arguments.

        When the LLM service layer fails to parse tool call
        arguments (e.g. due to unescaped characters or
        truncation), it wraps them as ``{"raw": "<json>"}``.
        This method makes a last-ditch attempt to extract the
        actual argument fields.

        Args:
            raw: The raw JSON string from ``kwargs["raw"]``.

        Returns:
            Parsed dict if successful, ``None`` otherwise.
        """
        import json

        if not isinstance(raw, str):
            return None

        # Try direct parse first
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                logger.info(
                    "Recovered tool args from raw JSON (len=%d)",
                    len(raw),
                )
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass

        # Try closing truncated JSON
        if raw.lstrip().startswith("{"):
            # Close any open string + braces
            attempt = raw.rstrip()
            # Check if we're inside an unclosed string
            in_str = False
            for ch in attempt:
                if ch == "\\":
                    continue
                if ch == '"':
                    in_str = not in_str
            if in_str:
                attempt += '"'
            # Count unclosed braces
            depth = attempt.count("{") - attempt.count("}")
            if depth > 0:
                attempt += "}" * depth
            try:
                parsed = json.loads(attempt)
                if isinstance(parsed, dict):
                    logger.info(
                        "Recovered tool args from truncated JSON (len=%d)",
                        len(raw),
                    )
                    return parsed
            except (json.JSONDecodeError, TypeError):
                pass

        return None

    @abstractmethod
    async def run(self, args: BaseModel) -> ToolResult:
        """
        Implementation logic for the tool.

        Args:
            args: The validated Input model.

        Returns:
            A ToolResult object containing structured data.
        """
        pass
