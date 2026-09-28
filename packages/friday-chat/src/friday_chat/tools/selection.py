"""Runtime-owned tool selection and schema-budget contracts."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from decimal import ROUND_FLOOR, Decimal, InvalidOperation
from enum import Enum
from typing import Any, Protocol

from friday_core.mcp import MCPToolMetadata
from friday_runtime.mcp_registration import sanitize_definition

from friday_chat.config import FridayChatConfig
from friday_chat.tools.schemas import ToolDefinition

_DEFAULT_CONTEXT_WINDOW = 8192
_DEFAULT_OUTPUT_BUFFER = 1024
_DEFAULT_MAX_BUDGET_RATIO = Decimal("0.25")


class ToolSelectionMode(str, Enum):
    """Authoritative mode used to choose tool schemas for a turn."""

    AUTOMATIC = "automatic"
    MANUAL = "manual"
    DISABLED = "disabled"


class ToolRejectionReason(str, Enum):
    """Categorical reason a requested or candidate tool was not selected."""

    UNKNOWN_TOOL = "unknown_tool"
    COUNT_LIMIT = "count_limit"
    TOKEN_LIMIT = "token_limit"
    TOOLS_DISABLED = "tools_disabled"
    MCP_COUNT_LIMIT = "mcp_count_limit"
    MEMORY_FLOOR = "memory_floor"
    MISSING_METADATA = "missing_metadata"
    UNSAFE_SCHEMA = "unsafe_schema"
    SCHEMA_LIMIT = "schema_limit"
    NOT_REGISTERED = "not_registered"
    NOT_RELEVANT = "not_relevant"
    NOT_REQUESTED = "not_requested"


@dataclass(frozen=True)
class ToolSelectionRejection:
    """One tool omitted from a selection with its stable reason."""

    name: str
    reason: ToolRejectionReason


@dataclass(frozen=True)
class ToolBudgetSnapshot:
    """Immutable evidence for the schemas selected for one model turn."""

    mode: ToolSelectionMode
    registered_names: tuple[str, ...]
    manual_names: tuple[str, ...]
    selected_names: tuple[str, ...]
    selected_categories: tuple[str, ...]
    rejections: tuple[ToolSelectionRejection, ...]
    schema_tokens: int
    maximum_schema_tokens: int
    max_tools: int
    max_budget_ratio: float
    available_context_tokens: int
    utilization_pct: float
    schema_bytes: bytes = field(repr=False)
    reserved_result_tokens: int = 0
    minimum_memory_tokens: int = 0
    memory_tokens_before_selection: int = 0
    memory_tokens_after_selection: int = 0
    selected_mcp_count: int = 0


@dataclass(frozen=True)
class ToolSelection:
    """Selected definitions and their immutable budget evidence."""

    definitions: tuple[ToolDefinition, ...]
    budget: ToolBudgetSnapshot


class ToolSelectionError(ValueError):
    """Raised when a manual selection cannot be accepted atomically."""

    def __init__(
        self,
        reason: ToolRejectionReason,
        names: Sequence[str],
        message: str,
    ) -> None:
        super().__init__(message)
        self.reason = reason
        self.names = tuple(names)


class SchemaTokenEstimator(Protocol):
    """Replaceable estimator boundary over the exact serialized model schema."""

    def estimate(self, schema_bytes: bytes) -> int: ...


@dataclass(frozen=True)
class UTF8SchemaTokenEstimator:
    """Compatible native estimate; not a claim of tokenizer parity."""

    def estimate(self, schema_bytes: bytes) -> int:
        return (len(schema_bytes) + 3) // 4 if schema_bytes else 0


@dataclass(frozen=True)
class ToolBudgetCalculator:
    """Canonical schema serialization, estimation, and configured limits."""

    max_tools: int
    max_budget_ratio: Decimal
    context_window: int
    output_buffer: int
    estimator: SchemaTokenEstimator = field(default_factory=UTF8SchemaTokenEstimator)
    mcp_metadata: Mapping[str, MCPToolMetadata] = field(
        default_factory=dict, repr=False
    )

    @classmethod
    def from_config(
        cls,
        config: FridayChatConfig,
        *,
        registered_count: int,
        mcp_metadata: Mapping[str, MCPToolMetadata] | None = None,
        estimator: SchemaTokenEstimator | None = None,
    ) -> ToolBudgetCalculator:
        """Build one calculator from the four authoritative config values."""
        context = config.tools.context
        return cls(
            max_tools=_configured_nonnegative_int(
                context.get("max_tools"),
                default=registered_count,
            ),
            max_budget_ratio=_configured_ratio(context.get("max_budget_ratio")),
            context_window=_configured_positive_int(
                config.memory.context_window,
                default=_DEFAULT_CONTEXT_WINDOW,
            ),
            output_buffer=_configured_nonnegative_int(
                config.memory.output_buffer,
                default=_DEFAULT_OUTPUT_BUFFER,
            ),
            mcp_metadata=mcp_metadata or {},
            estimator=estimator or UTF8SchemaTokenEstimator(),
        )

    @property
    def available_context_tokens(self) -> int:
        """Return the input context remaining after the output reservation."""
        return max(0, self.context_window - self.output_buffer)

    @property
    def maximum_schema_tokens(self) -> int:
        """Return the exact configured schema-token ceiling."""
        value = Decimal(self.available_context_tokens) * self.max_budget_ratio
        return int(value.to_integral_value(rounding=ROUND_FLOOR))

    def schema_bytes(self, tools: Sequence[ToolDefinition]) -> bytes:
        """Serialize exactly the model-bound schemas in canonical JSON form."""
        if not tools:
            return b""
        schemas = [_model_schema(tool) for tool in tools]
        return json.dumps(
            schemas,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

    def estimate_schema_tokens(self, tools: Sequence[ToolDefinition]) -> int:
        """Estimate tokens solely from the canonical model schema bytes."""
        schema_bytes = self.schema_bytes(tools)
        if not schema_bytes:
            return 0
        estimate = self.estimator.estimate(schema_bytes)
        if isinstance(estimate, bool) or not isinstance(estimate, int) or estimate < 0:
            raise ValueError("Schema estimator must return a nonnegative integer")
        mcp_tools = [tool for tool in tools if tool.name in self.mcp_metadata]
        if not mcp_tools:
            return estimate
        native = [tool for tool in tools if tool.name not in self.mcp_metadata]
        native_estimate = self.estimator.estimate(self.schema_bytes(native))
        if (
            isinstance(native_estimate, bool)
            or not isinstance(native_estimate, int)
            or native_estimate < 0
        ):
            raise ValueError("Schema estimator must return a nonnegative integer")
        # Retain WS-03's conservative complete-export costs; never divide them
        # by four or confuse registry costs with approximate native estimates.
        mcp_cost = sum(
            max(
                self.mcp_metadata[tool.name].schema_token_estimate or 0,
                len(
                    json.dumps(
                        _model_schema(tool), ensure_ascii=False, separators=(",", ":")
                    ).encode("utf-8")
                ),
            )
            for tool in mcp_tools
        )
        return max(estimate, native_estimate + mcp_cost + 2)

    def fits(self, tools: Sequence[ToolDefinition]) -> bool:
        """Return whether definitions satisfy both configured hard limits."""
        return (
            len(tools) <= self.max_tools
            and self.estimate_schema_tokens(tools) <= self.maximum_schema_tokens
        )


class ToolSelectionState:
    """Single mutable runtime authority for manual and per-turn tool selection."""

    def __init__(
        self,
        config: FridayChatConfig,
        tools: Sequence[ToolDefinition],
        *,
        mcp_metadata: Mapping[str, MCPToolMetadata] | None = None,
        estimator: SchemaTokenEstimator | None = None,
    ) -> None:
        self._config = config
        self._mcp_metadata = dict(mcp_metadata or {})
        self._estimator = estimator or UTF8SchemaTokenEstimator()
        self._tools = _validated_registered_tools(tools)
        self._manual_names: tuple[str, ...] | None = None
        self._last_turn_snapshot: ToolBudgetSnapshot | None = None
        self._last_automatic_snapshot: ToolBudgetSnapshot | None = None
        self._last_executed_names: tuple[str, ...] = ()

    @property
    def mode(self) -> ToolSelectionMode:
        """Return the current authoritative selection mode."""
        if not self._config.tools.enabled:
            return ToolSelectionMode.DISABLED
        if self._manual_names is not None:
            return ToolSelectionMode.MANUAL
        return ToolSelectionMode.AUTOMATIC

    @property
    def registered_tools(self) -> tuple[ToolDefinition, ...]:
        """Return definitions in stable registry order."""
        return self._tools

    @property
    def registered_names(self) -> tuple[str, ...]:
        """Return registered tool names in stable registry order."""
        return tuple(tool.name for tool in self._tools)

    @property
    def manual_names(self) -> tuple[str, ...]:
        """Return the accepted manual set, or an empty tuple outside manual mode."""
        return self._manual_names or ()

    @property
    def last_turn_snapshot(self) -> ToolBudgetSnapshot | None:
        """Return immutable evidence from the most recent completed turn."""
        return self._last_turn_snapshot

    @property
    def last_automatic_snapshot(self) -> ToolBudgetSnapshot | None:
        """Return evidence from the most recent completed automatic turn."""
        return self._last_automatic_snapshot

    @property
    def last_executed_names(self) -> tuple[str, ...]:
        """Return unique tool names executed by the most recent completed turn."""
        return self._last_executed_names

    @property
    def calculator(self) -> ToolBudgetCalculator:
        """Return the canonical calculator for the current registry."""
        return ToolBudgetCalculator.from_config(
            self._config,
            registered_count=len(self._tools),
            mcp_metadata=self._mcp_metadata if self._mcp_enabled else {},
            estimator=self._estimator,
        )

    def synchronize_registered_tools(
        self,
        tools: Sequence[ToolDefinition],
        *,
        mcp_metadata: Mapping[str, MCPToolMetadata] | None = None,
    ) -> None:
        """Synchronize an explicitly replaced runtime registry before selection."""
        definitions = _validated_registered_tools(tools)
        if mcp_metadata is not None:
            self._mcp_metadata = dict(mcp_metadata)
        if definitions == self._tools:
            return
        new_names = {tool.name for tool in definitions}
        if self._manual_names is not None and any(
            name not in new_names for name in self._manual_names
        ):
            raise ToolSelectionError(
                ToolRejectionReason.UNKNOWN_TOOL,
                self._manual_names,
                "The runtime registry changed while a manual tool set was active.",
            )
        self._tools = definitions

    def inject_manual(self, names: Sequence[str]) -> ToolBudgetSnapshot:
        """Validate an exact manual set, then switch modes in one mutation."""
        if not self._config.tools.enabled:
            raise ToolSelectionError(
                ToolRejectionReason.TOOLS_DISABLED,
                (),
                "Tool selection is disabled by configuration.",
            )
        requested_names = _unique_names(names)
        if self._mcp_enabled or self._config.tools.context.get("required_tools"):
            selection = self._select_policy("", requested_names)
            self._manual_names = requested_names
            return self._snapshot(
                ToolSelectionMode.MANUAL,
                selection.definitions,
                rejections=selection.budget.rejections,
            )
        selected = self._validated_manual_tools(requested_names)
        self._manual_names = requested_names
        return self._snapshot(
            ToolSelectionMode.MANUAL,
            selected,
            rejections=(),
        )

    def _validated_manual_tools(
        self,
        requested_names: tuple[str, ...],
    ) -> tuple[ToolDefinition, ...]:
        if not self._config.tools.enabled:
            raise ToolSelectionError(
                ToolRejectionReason.TOOLS_DISABLED,
                requested_names,
                "Tool selection is disabled by configuration.",
            )

        tools_by_name = {tool.name: tool for tool in self._tools}
        unknown = tuple(name for name in requested_names if name not in tools_by_name)
        if unknown:
            raise ToolSelectionError(
                ToolRejectionReason.UNKNOWN_TOOL,
                unknown,
                "Unknown tool names: " + ", ".join(unknown),
            )

        calculator = self.calculator
        if len(requested_names) > calculator.max_tools:
            raise ToolSelectionError(
                ToolRejectionReason.COUNT_LIMIT,
                requested_names,
                (
                    f"Manual selection has {len(requested_names)} tools; "
                    f"the configured maximum is {calculator.max_tools}."
                ),
            )

        selected = tuple(tools_by_name[name] for name in requested_names)
        estimated_tokens = calculator.estimate_schema_tokens(selected)
        if estimated_tokens > calculator.maximum_schema_tokens:
            raise ToolSelectionError(
                ToolRejectionReason.TOKEN_LIMIT,
                requested_names,
                (
                    f"Manual schemas require {estimated_tokens} tokens; "
                    f"the configured maximum is {calculator.maximum_schema_tokens}."
                ),
            )

        return selected

    def clear_manual(self) -> bool:
        """Clear manual mode and return whether a manual set was active."""
        was_manual = self._manual_names is not None
        self._manual_names = None
        return was_manual

    def manual_preview(self) -> ToolBudgetSnapshot | None:
        """Return current manual budget evidence without recording a turn."""
        if self._manual_names is None or not self._config.tools.enabled:
            return None
        if self._mcp_enabled or self._config.tools.context.get("required_tools"):
            return self._select_policy("", self._manual_names).budget
        selected = self._validated_manual_tools(self._manual_names)
        return self._snapshot(ToolSelectionMode.MANUAL, selected, rejections=())

    def select_for_turn(self, user_message: str) -> ToolSelection:
        """Select and budget the exact schemas to bind to one model turn."""
        if not self._config.tools.enabled:
            return ToolSelection(
                definitions=(),
                budget=self._snapshot(
                    ToolSelectionMode.DISABLED,
                    (),
                    rejections=tuple(
                        ToolSelectionRejection(
                            tool.name,
                            ToolRejectionReason.TOOLS_DISABLED,
                        )
                        for tool in self._tools
                    ),
                ),
            )

        if self._mcp_enabled or self._config.tools.context.get("required_tools"):
            return self._select_policy(user_message, self._manual_names)

        if self._manual_names is not None:
            selected = self._validated_manual_tools(self._manual_names)
            return ToolSelection(
                definitions=selected,
                budget=self._snapshot(
                    ToolSelectionMode.MANUAL,
                    selected,
                    rejections=(),
                ),
            )

        selected, rejections = self._select_automatic(user_message)
        return ToolSelection(
            definitions=selected,
            budget=self._snapshot(
                ToolSelectionMode.AUTOMATIC,
                selected,
                rejections=rejections,
            ),
        )

    def record_completed_turn(
        self,
        snapshot: ToolBudgetSnapshot,
        executed_names: Sequence[str],
    ) -> None:
        """Retain completed-turn selection and execution state for commands."""
        self._last_turn_snapshot = snapshot
        if snapshot.mode is ToolSelectionMode.AUTOMATIC:
            self._last_automatic_snapshot = snapshot
        self._last_executed_names = _unique_names(executed_names)

    def _select_automatic(
        self,
        user_message: str,
    ) -> tuple[tuple[ToolDefinition, ...], tuple[ToolSelectionRejection, ...]]:
        if not self._tools:
            return (), ()

        threshold = _configured_float(
            self._config.tools.context.get("recommendation_threshold"),
            default=0.5,
        )
        scored = [
            (score, index, tool)
            for index, tool in enumerate(self._tools)
            if (score := tool_relevance_score(user_message, tool)) >= threshold
        ]
        if scored:
            scored.sort(key=lambda item: (-item[0], item[1]))
            candidates = tuple(tool for _score, _index, tool in scored)
        else:
            candidates = self._tools

        calculator = self.calculator
        selected: list[ToolDefinition] = []
        rejections: list[ToolSelectionRejection] = []
        for tool in candidates:
            if len(selected) >= calculator.max_tools:
                rejections.append(
                    ToolSelectionRejection(
                        tool.name,
                        ToolRejectionReason.COUNT_LIMIT,
                    )
                )
                continue
            candidate_selection = (*selected, tool)
            if (
                calculator.estimate_schema_tokens(candidate_selection)
                > calculator.maximum_schema_tokens
            ):
                rejections.append(
                    ToolSelectionRejection(
                        tool.name,
                        ToolRejectionReason.TOKEN_LIMIT,
                    )
                )
                continue
            selected.append(tool)
        return tuple(selected), tuple(rejections)

    def _snapshot(
        self,
        mode: ToolSelectionMode,
        selected: Sequence[ToolDefinition],
        *,
        rejections: tuple[ToolSelectionRejection, ...],
    ) -> ToolBudgetSnapshot:
        definitions = tuple(selected)
        calculator = self.calculator
        schema_tokens = calculator.estimate_schema_tokens(definitions)
        maximum = self.maximum_schema_tokens
        reservation = self.configured_result_reservation if definitions else 0
        before = max(0, calculator.available_context_tokens - self._system_tokens)
        after = max(0, before - schema_tokens - reservation)
        utilization_pct = (schema_tokens / maximum) * 100 if maximum else 0.0
        return ToolBudgetSnapshot(
            mode=mode,
            registered_names=tuple(
                tool.name
                if tool.category != "mcp"
                or re.fullmatch(r"[a-z][a-z0-9_]{0,63}", tool.name)
                else "mcp_invalid_tool"
                for tool in self._tools
            ),
            manual_names=self.manual_names,
            selected_names=tuple(tool.name for tool in definitions),
            selected_categories=tuple(tool.category for tool in definitions),
            rejections=rejections,
            schema_tokens=schema_tokens,
            maximum_schema_tokens=maximum,
            max_tools=calculator.max_tools,
            max_budget_ratio=float(calculator.max_budget_ratio),
            available_context_tokens=calculator.available_context_tokens,
            utilization_pct=utilization_pct,
            schema_bytes=calculator.schema_bytes(definitions),
            reserved_result_tokens=reservation,
            minimum_memory_tokens=self.minimum_memory_tokens,
            memory_tokens_before_selection=before,
            memory_tokens_after_selection=after,
            selected_mcp_count=sum(
                tool.name in self._mcp_metadata for tool in definitions
            ),
        )

    @property
    def _mcp_enabled(self) -> bool:
        return self._config.tools.enabled and self._config.tools.mcp_provider.enabled

    @property
    def _system_tokens(self) -> int:
        return max(1, len(self._config.chat.system_prompt) // 4)

    @property
    def configured_result_reservation(self) -> int:
        return (
            self._config.tools.mcp_provider.config.limits.reserved_tool_result_tokens
            if self._mcp_enabled
            else 0
        )

    @property
    def minimum_memory_tokens(self) -> int:
        return (
            self._config.tools.mcp_provider.config.limits.min_memory_retrieval_tokens
            if self._mcp_enabled
            else 0
        )

    @property
    def maximum_schema_tokens(self) -> int:
        ceiling = self.calculator.maximum_schema_tokens
        if self._mcp_enabled:
            ceiling = min(
                ceiling, self._config.tools.mcp_provider.config.limits.max_schema_tokens
            )
        return ceiling

    def _checked_mcp(self, tool: ToolDefinition) -> ToolDefinition:
        metadata = self._mcp_metadata.get(tool.name)
        if metadata is None:
            raise ToolSelectionError(
                ToolRejectionReason.MISSING_METADATA,
                (),
                "MCP tool metadata is missing.",
            )
        if (
            metadata.canonical_name != tool.name
            or metadata.discovery_state != "discovered"
            or metadata.filter_state != "included"
            or metadata.schema_sanitization_state not in {"unchanged", "sanitized"}
            or metadata.schema_token_estimate is None
            or metadata.schema_byte_size is None
        ):
            raise ToolSelectionError(
                ToolRejectionReason.NOT_REGISTERED,
                (),
                "MCP tool metadata is not eligible.",
            )
        limits = self._config.tools.mcp_provider.config.limits
        try:
            clean, state = sanitize_definition(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.input_schema,
                },
                limits.max_schema_bytes_per_tool,
            )
            parameters = clean.parameters()
            model_bytes = len(
                json.dumps(
                    _model_schema(tool),
                    ensure_ascii=False,
                    separators=(",", ":"),
                    allow_nan=False,
                ).encode("utf-8")
            )
        except (ValueError, TypeError, OverflowError, RecursionError):
            raise ToolSelectionError(
                ToolRejectionReason.UNSAFE_SCHEMA, (), "MCP schema verification failed."
            ) from None
        if state != "unchanged" or tool.category != "mcp":
            raise ToolSelectionError(
                ToolRejectionReason.UNSAFE_SCHEMA, (), "MCP schema verification failed."
            )
        if (
            model_bytes > limits.max_schema_bytes_per_tool
            or model_bytes > metadata.schema_byte_size
        ):
            raise ToolSelectionError(
                ToolRejectionReason.SCHEMA_LIMIT,
                (),
                "MCP schema exceeds its verified export bound.",
            )
        return ToolDefinition(tool.name, clean.description, parameters, tool.category)

    def _policy_reason(
        self, tools: Sequence[ToolDefinition]
    ) -> ToolRejectionReason | None:
        calculator = self.calculator
        if len(tools) > calculator.max_tools:
            return ToolRejectionReason.COUNT_LIMIT
        maximum_mcp = self._config.tools.context.get("max_mcp_tools")
        if (
            maximum_mcp is not None
            and sum(t.name in self._mcp_metadata for t in tools) > maximum_mcp
        ):
            return ToolRejectionReason.MCP_COUNT_LIMIT
        cost = calculator.estimate_schema_tokens(tools)
        if cost > self.maximum_schema_tokens:
            return ToolRejectionReason.TOKEN_LIMIT
        memory = (
            calculator.available_context_tokens
            - self._system_tokens
            - cost
            - (self.configured_result_reservation if tools else 0)
        )
        if memory < self.minimum_memory_tokens:
            return ToolRejectionReason.MEMORY_FLOOR
        return None

    def _select_policy(
        self, user_message: str, manual: tuple[str, ...] | None
    ) -> ToolSelection:
        required = _unique_names(
            (*self._config.tools.context.get("required_tools", ()), *(manual or ()))
        )
        by_name = {tool.name: tool for tool in self._tools}
        if any(name not in by_name for name in required):
            raise ToolSelectionError(
                ToolRejectionReason.UNKNOWN_TOOL,
                (),
                "Required selected tool is unavailable.",
            )
        base_reason = self._policy_reason(())
        if base_reason is not None:
            raise ToolSelectionError(
                base_reason,
                (),
                "Context budget cannot preserve the memory retrieval floor.",
            )
        checked: dict[str, ToolDefinition] = {}
        rejected: list[ToolSelectionRejection] = []
        for tool in self._tools:
            if tool.category == "mcp" or tool.name in self._mcp_metadata:
                try:
                    if not self._mcp_enabled:
                        raise ToolSelectionError(
                            ToolRejectionReason.TOOLS_DISABLED,
                            (),
                            "MCP selection is disabled.",
                        )
                    checked[tool.name] = self._checked_mcp(tool)
                except ToolSelectionError as exc:
                    if tool.name in required:
                        raise ToolSelectionError(
                            exc.reason,
                            (),
                            "Required MCP tool failed schema/metadata verification.",
                        ) from None
                    # Peer-controlled malformed names never enter diagnostic text.
                    safe = (
                        tool.name
                        if re.fullmatch(r"[a-z][a-z0-9_]{0,63}", tool.name)
                        else "mcp_invalid_tool"
                    )
                    rejected.append(ToolSelectionRejection(safe, exc.reason))
            else:
                checked[tool.name] = tool
        selected = [checked[name] for name in required]
        reason = self._policy_reason(selected)
        if reason is not None:
            raise ToolSelectionError(
                reason,
                (),
                "Required selected tools cannot fit the configured turn budget.",
            )
        mode = (
            ToolSelectionMode.MANUAL
            if manual is not None
            else ToolSelectionMode.AUTOMATIC
        )
        if manual is None:
            threshold = _configured_float(
                self._config.tools.context.get("recommendation_threshold"), default=0.5
            )
            scored = [
                (tool_relevance_score(user_message, t), i, t)
                for i, t in enumerate(checked.values())
                if t.name not in required
            ]
            relevant = [row for row in scored if row[0] >= threshold]
            candidates = (
                sorted(relevant, key=lambda row: (-row[0], row[1]))
                if relevant
                else scored
            )
            if relevant:
                rejected.extend(
                    ToolSelectionRejection(t.name, ToolRejectionReason.NOT_RELEVANT)
                    for score, _index, t in scored
                    if score < threshold
                )
            # Native optional candidates win memory-floor ties over MCP candidates.
            # Other limits retain existing relevance order.
            for _score, _index, tool in candidates:
                reason = self._policy_reason((*selected, tool))
                if (
                    reason is ToolRejectionReason.MEMORY_FLOOR
                    and tool.name not in self._mcp_metadata
                ):
                    optional_mcp = [
                        t
                        for t in selected
                        if t.name in self._mcp_metadata and t.name not in required
                    ]
                    tentative = list(selected)
                    removed: list[ToolDefinition] = []
                    for old in reversed(optional_mcp):
                        tentative.remove(old)
                        removed.append(old)
                        if self._policy_reason((*tentative, tool)) is None:
                            selected = tentative
                            rejected.extend(
                                ToolSelectionRejection(
                                    t.name, ToolRejectionReason.MEMORY_FLOOR
                                )
                                for t in removed
                            )
                            reason = None
                            break
                if reason is None:
                    selected.append(tool)
                else:
                    rejected.append(ToolSelectionRejection(tool.name, reason))
        else:
            rejected.extend(
                ToolSelectionRejection(t.name, ToolRejectionReason.NOT_REQUESTED)
                for t in checked.values()
                if t.name not in required
            )
        return ToolSelection(
            tuple(selected), self._snapshot(mode, selected, rejections=tuple(rejected))
        )


def canonical_tool_schema_bytes(tools: Sequence[ToolDefinition]) -> bytes:
    """Return canonical model-schema bytes for deterministic identity checks."""
    calculator = ToolBudgetCalculator(
        max_tools=len(tools),
        max_budget_ratio=Decimal("1"),
        context_window=1,
        output_buffer=0,
    )
    return calculator.schema_bytes(tools)


def tool_relevance_score(user_message: str, tool: ToolDefinition) -> float:
    """Return deterministic relevance of one tool for a user message."""
    query_tokens = _scoring_tokens(user_message)
    if not query_tokens:
        return 0.0

    name_tokens = _scoring_tokens(tool.name)
    description_tokens = _scoring_tokens(tool.description)
    schema_tokens = _scoring_tokens(json.dumps(tool.input_schema, sort_keys=True))
    category_tokens = _scoring_tokens(tool.category)

    score = 0.0
    if query_tokens & name_tokens:
        score += 0.4
    score += min(len(query_tokens & description_tokens) * 0.15, 0.3)
    score += min(len(query_tokens & schema_tokens) * 0.05, 0.15)
    if query_tokens & category_tokens:
        score += 0.1
    if _matches_temporal_tool(user_message, tool):
        score += 0.6
    if _matches_file_read_tool(user_message, tool):
        score += 0.6
    if _matches_file_write_tool(user_message, tool):
        score += 0.6
    if _is_file_read_query(user_message) and _is_file_write_tool(tool):
        score -= 0.5
    if _is_file_write_query(user_message) and _is_file_read_tool(tool):
        score -= 0.5
    return min(score, 1.0)


def _model_schema(tool: ToolDefinition) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.input_schema,
        },
    }


def _unique_names(names: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(names))


def _validated_registered_tools(
    tools: Sequence[ToolDefinition],
) -> tuple[ToolDefinition, ...]:
    definitions = tuple(tools)
    names = tuple(tool.name for tool in definitions)
    if len(set(names)) != len(names):
        raise ValueError("Tool registry contains duplicate names.")
    return definitions


def _configured_positive_int(value: object, *, default: int) -> int:
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    return default


def _configured_nonnegative_int(value: object, *, default: int) -> int:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return default


def _configured_float(value: object, *, default: float) -> float:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return default


def _configured_ratio(value: object) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return _DEFAULT_MAX_BUDGET_RATIO
    try:
        ratio = Decimal(str(value))
    except InvalidOperation:
        return _DEFAULT_MAX_BUDGET_RATIO
    if not ratio.is_finite() or ratio < 0 or ratio > 1:
        return _DEFAULT_MAX_BUDGET_RATIO
    return ratio


def _matches_temporal_tool(user_message: str, tool: ToolDefinition) -> bool:
    tool_tokens = _normalized_tokens(
        f"{tool.name} {tool.description} {json.dumps(tool.input_schema, sort_keys=True)}"
    )
    if not ({"date", "time", "datetime", "current"} & tool_tokens):
        return False
    query_tokens = _normalized_tokens(user_message)
    return bool({"date", "time", "day", "today", "now", "timezone"} & query_tokens)


def _matches_file_read_tool(user_message: str, tool: ToolDefinition) -> bool:
    return _is_file_read_query(user_message) and _is_file_read_tool(tool)


def _matches_file_write_tool(user_message: str, tool: ToolDefinition) -> bool:
    return _is_file_write_query(user_message) and _is_file_write_tool(tool)


def _is_file_read_query(user_message: str) -> bool:
    query_tokens = _normalized_tokens(user_message)
    read_intents = {
        "read",
        "review",
        "evaluate",
        "inspect",
        "analyze",
        "analyse",
        "summarize",
        "summarise",
        "show",
        "open",
        "load",
    }
    file_markers = {
        "file",
        "path",
        "config",
        "yaml",
        "yml",
        "json",
        "toml",
        "md",
        "py",
        "txt",
    }
    return bool(query_tokens & read_intents) and (
        bool(query_tokens & file_markers) or "/" in user_message or "\\" in user_message
    )


def _is_file_write_query(user_message: str) -> bool:
    query_tokens = _normalized_tokens(user_message)
    write_intents = {
        "write",
        "create",
        "save",
        "edit",
        "modify",
        "update",
        "append",
        "overwrite",
        "delete",
        "remove",
    }
    file_markers = {
        "file",
        "path",
        "config",
        "yaml",
        "yml",
        "json",
        "toml",
        "md",
        "py",
        "txt",
    }
    return bool(query_tokens & write_intents) and (
        bool(query_tokens & file_markers) or "/" in user_message or "\\" in user_message
    )


def _is_file_read_tool(tool: ToolDefinition) -> bool:
    tool_tokens = _normalized_tokens(
        f"{tool.name} {tool.description} {json.dumps(tool.input_schema, sort_keys=True)}"
    )
    return "path" in tool_tokens and (
        "read" in tool_tokens or "summarize" in tool_tokens or "process" in tool_tokens
    )


def _is_file_write_tool(tool: ToolDefinition) -> bool:
    tool_tokens = _normalized_tokens(
        f"{tool.name} {tool.description} {json.dumps(tool.input_schema, sort_keys=True)}"
    )
    return "path" in tool_tokens and (
        "write" in tool_tokens or "append" in tool_tokens or "overwrite" in tool_tokens
    )


def _normalized_tokens(value: str) -> set[str]:
    return {
        _normalize_token(token) for token in re.findall(r"[a-z0-9]+", value.lower())
    }


def _scoring_tokens(value: str) -> set[str]:
    ignored = {
        "a",
        "an",
        "and",
        "api",
        "current",
        "dev",
        "for",
        "get",
        "the",
        "to",
        "using",
        "with",
    }
    return {token for token in _normalized_tokens(value) if token not in ignored}


def _normalize_token(token: str) -> str:
    if len(token) > 3 and token.endswith("ies"):
        return f"{token[:-3]}y"
    if len(token) > 3 and token.endswith("s"):
        return token[:-1]
    return token


__all__ = [
    "ToolBudgetCalculator",
    "ToolBudgetSnapshot",
    "ToolRejectionReason",
    "ToolSelection",
    "ToolSelectionError",
    "ToolSelectionMode",
    "ToolSelectionRejection",
    "ToolSelectionState",
    "canonical_tool_schema_bytes",
    "tool_relevance_score",
]
