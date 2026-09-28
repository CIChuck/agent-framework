"""Framework-facing MCP contracts for later runtime integration.

These models describe policy and provenance; this module does not connect to
servers, register tools, execute calls, or persist content. ``friday-mcp`` owns
the protocol transport and client implementations. Consumers should import
these contracts from this public module instead of reaching into that package.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from datetime import datetime
from hashlib import sha256
from types import MappingProxyType
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

MAX_MCP_TOOL_NAME_LENGTH = 64
_CANONICAL_TOOL_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
_NON_ASCII_IDENTIFIER = re.compile(r"[^a-z0-9]+")
MCPSafeIdentifier = Annotated[
    str, StringConstraints(strict=True, min_length=1, max_length=64, pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
]

MCPDiagnosticCode = Literal[
    "connection_failed",
    "required_server_unavailable",
    "invalid_schema",
    "tool_limit",
    "schema_limit",
    "name_collision",
    "filter_excluded",
    "missing_include",
    "registration_failed",
]


class _MCPContract(BaseModel):
    """Strict, immutable base for values crossing Friday package boundaries."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class MCPClientLimits(_MCPContract):
    """Conservative first-pass caps; enforcement belongs to later workstreams."""

    max_servers: int = Field(default=8, gt=0)
    max_tools_per_server: int = Field(default=25, gt=0)
    max_total_tools: int = Field(default=50, gt=0)
    max_schema_bytes_per_tool: int = Field(default=8192, gt=0)
    max_schema_tokens: int = Field(default=4000, gt=0)
    max_result_bytes: int = Field(default=65536, gt=0)
    reserved_tool_result_tokens: int = Field(default=2048, gt=0)
    min_memory_retrieval_tokens: int = Field(default=4096, ge=0)
    max_parallel_server_connects: int = Field(default=4, gt=0)
    max_parallel_tool_calls: int = Field(default=4, gt=0)
    connection_timeout_seconds: int = Field(default=30, gt=0)
    tool_timeout_seconds: int = Field(default=60, gt=0)


class MCPClientSecurityPolicy(_MCPContract):
    """The approved safe posture for the first integrated client pass.

    Existing programmatic SSE clients are unaffected. A later workstream must
    obtain separate authority before exposing SSE or argument hashes through
    the integrated runtime configuration. ``allowed_workspace_ids`` holds
    bounded logical identifiers, never filesystem paths; an empty tuple means
    the current workspace scope without additional named selections. WS-01/02
    own configuration and enforcement.
    """

    integrated_transport: Literal["stdio_only"] = "stdio_only"
    trust_posture: Literal["local_stdio_only"] = "local_stdio_only"
    path_scope: Literal["workspace_only"] = "workspace_only"
    allowed_workspace_ids: tuple[MCPSafeIdentifier, ...] = ()
    require_explicit_stdio_command: bool = True
    redact_environment: bool = True
    redact_headers: bool = True
    redact_arguments: bool = True
    store_raw_tool_results: bool = False
    store_argument_hashes: bool = False

    @model_validator(mode="after")
    def _reject_unsafe_policy(self) -> MCPClientSecurityPolicy:
        if not self.require_explicit_stdio_command:
            raise ValueError("MCP stdio commands must be explicit")
        if not (
            self.redact_environment and self.redact_headers and self.redact_arguments
        ):
            raise ValueError("MCP environment, headers, and arguments must be redacted")
        if self.store_raw_tool_results or self.store_argument_hashes:
            raise ValueError("raw MCP results and argument hashes cannot be stored")
        return self


class MCPIngestionPolicy(_MCPContract):
    """Long-term ingestion needs explicit safe server/tool IDs and sanitation.

    Tool IDs are canonical Friday tool names. Selection is only a policy shape;
    WS-06 owns matching, ingestion, and persistence.
    """

    long_term_memory_enabled: bool = False
    require_sanitized_content: bool = True
    max_ingested_bytes: int = Field(default=65536, gt=0)
    opted_in_servers: tuple[MCPSafeIdentifier, ...] = ()
    opted_in_tools: tuple[MCPSafeIdentifier, ...] = ()

    @model_validator(mode="after")
    def _require_sanitization(self) -> MCPIngestionPolicy:
        if not self.require_sanitized_content:
            raise ValueError("MCP ingestion requires sanitized content")
        if any(not _CANONICAL_TOOL_NAME.fullmatch(name) for name in self.opted_in_tools):
            raise ValueError("MCP tool opt-ins require canonical tool names")
        if self.long_term_memory_enabled and not (
            self.opted_in_servers or self.opted_in_tools
        ):
            raise ValueError("MCP ingestion requires a server or tool opt-in")
        return self


class MCPDiscoveryPolicy(_MCPContract):
    """Discovery is startup-only in the first integrated client pass."""

    refresh_mode: Literal["startup_only"] = "startup_only"
    cache_tool_list: bool = True


class MCPServerRuntimePolicy(_MCPContract):
    """Per-server runtime defaults independent of protocol-local connection config."""

    enabled: bool = True
    required: bool = False
    transport: Literal["stdio"] = "stdio"
    trust_level: Literal["local"] = "local"
    connection_timeout_seconds: int = Field(default=30, gt=0)
    tool_timeout_seconds: int = Field(default=60, gt=0)
    retry_attempts: int = Field(default=3, ge=0)


class MCPToolMetadata(_MCPContract):
    """Content-minimal metadata for a registry sidecar keyed by tool name.

    A missing token estimate means unmeasured, and ``not_checked`` means no
    sanitizer/filter decision has been recorded. Reason codes never contain
    descriptions, schemas, or raw exception text. WS-03/04 own population.
    """

    canonical_name: str
    server_name: str = Field(min_length=1, max_length=256)
    original_name: str = Field(min_length=1, max_length=256, repr=False)
    tool_name_prefix: str = "mcp_"
    transport: Literal["stdio", "sse"]
    trust_level: Literal["local", "remote"]
    provider: Literal["mcp"] = "mcp"
    schema_token_estimate: int | None = Field(default=None, ge=0)
    schema_byte_size: int | None = Field(default=None, ge=0)
    discovery_state: Literal["not_checked", "discovered"] = "not_checked"
    schema_sanitization_state: Literal[
        "not_checked", "unchanged", "sanitized", "rejected"
    ] = "not_checked"
    filter_state: Literal["not_evaluated", "included", "excluded"] = "not_evaluated"
    filter_diagnostic_codes: tuple[MCPDiagnosticCode, ...] = ()

    @model_validator(mode="after")
    def _validate_canonical_name(self) -> MCPToolMetadata:
        expected = normalize_mcp_tool_name(
            self.server_name,
            self.original_name,
            tool_name_prefix=self.tool_name_prefix,
        )
        if self.canonical_name != expected:
            raise ValueError("MCP canonical tool name does not match source names")
        return self


class MCPToolCallProvenance(_MCPContract):
    """A call record that cannot carry raw arguments, results, or hashes.

    Optional IDs are absent until assigned by WS-05/06. ``not_checked`` is not
    a claim of safe output; downstream consumers must sanitize before re-entry
    or persistence. The ingestion decision and boolean must agree.
    """

    tool: MCPToolMetadata
    call_id: MCPSafeIdentifier | None = None
    status: Literal["succeeded", "failed", "blocked"]
    arguments_redacted: bool = True
    result_truncated: bool = False
    memory_ingested: bool = False
    output_sanitization_state: Literal[
        "not_checked", "unchanged", "sanitized", "rejected"
    ] = "not_checked"
    ingestion_decision: Literal["disabled", "skipped", "ingested"] = "disabled"
    transcript_correlation_id: MCPSafeIdentifier | None = None
    memory_correlation_id: MCPSafeIdentifier | None = None
    result_size_bytes: int | None = Field(default=None, ge=0)
    model_result_size_bytes: int | None = Field(default=None, ge=0)
    failure_code: (
        Literal[
            "tool_error",
            "invalid_result",
            "execution_error",
            "timeout",
            "output_rejected",
        ]
        | None
    ) = None

    @model_validator(mode="after")
    def _require_redacted_arguments(self) -> MCPToolCallProvenance:
        if not self.arguments_redacted:
            raise ValueError("MCP call provenance requires redacted arguments")
        if self.memory_ingested != (self.ingestion_decision == "ingested"):
            raise ValueError("MCP ingestion decision must match ingestion state")
        if self.status == "succeeded" and self.failure_code is not None:
            raise ValueError("Successful MCP calls cannot have a failure code")
        if self.output_sanitization_state == "rejected" and self.status != "blocked":
            raise ValueError("Rejected MCP output requires blocked provenance")
        if self.failure_code == "output_rejected" and (
            self.status != "blocked" or self.output_sanitization_state != "rejected"
        ):
            raise ValueError("Rejected MCP output must have blocked provenance")
        if (
            self.failure_code not in {None, "output_rejected"}
            and self.status != "failed"
        ):
            raise ValueError("MCP execution failure codes require failed provenance")
        return self


class MCPServerDiscoveryState(_MCPContract):
    """Safe per-server discovery facts; identifiers are not raw server content.

    Catalog versions are bounded labels, timestamps are timezone-aware, and
    refresh eligibility is descriptive; WS-02/03 own discovery and WS-00's
    startup-only policy does not schedule refreshes.
    """

    server_id: MCPSafeIdentifier
    connection_state: Literal[
        "not_started", "connecting", "connected", "failed", "disconnected"
    ] = "not_started"
    catalog_version: MCPSafeIdentifier | None = None
    cache_timestamp: datetime | None = None
    rejected_tools: int = Field(default=0, ge=0)
    filtered_tools: int = Field(default=0, ge=0)
    diagnostic_codes: tuple[MCPDiagnosticCode, ...] = ()
    refresh_eligible: bool = False

    @model_validator(mode="after")
    def _require_aware_cache_timestamp(self) -> MCPServerDiscoveryState:
        if self.cache_timestamp is not None and self.cache_timestamp.utcoffset() is None:
            raise ValueError("MCP cache timestamp must include a timezone")
        return self


class MCPDiscoveryState(_MCPContract):
    """Aggregate startup discovery state without raw server payloads."""

    status: Literal["not_started", "completed", "partial", "failed"] = "not_started"
    connected_servers: int = Field(default=0, ge=0)
    failed_servers: int = Field(default=0, ge=0)
    discovered_tools: int = Field(default=0, ge=0)
    selected_tools: int = Field(default=0, ge=0)
    servers: tuple[MCPServerDiscoveryState, ...] = ()

    @model_validator(mode="after")
    def _validate_counts(self) -> MCPDiscoveryState:
        if self.selected_tools > self.discovered_tools:
            raise ValueError("selected MCP tool count cannot exceed discovered count")
        server_ids = [server.server_id for server in self.servers]
        if len(server_ids) != len(set(server_ids)):
            raise ValueError("duplicate MCP discovery server identifier")
        return self


class MCPProviderDiagnostics(_MCPContract):
    """Safe counters and typed reason codes, never raw exception messages."""

    connected_servers: int = Field(default=0, ge=0)
    failed_servers: int = Field(default=0, ge=0)
    registered_tools: int = Field(default=0, ge=0)
    filtered_tools: int = Field(default=0, ge=0)
    rejected_tools: int = Field(default=0, ge=0)
    codes: tuple[MCPDiagnosticCode, ...] = ()


def _identifier_part(value: str, *, label: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"MCP {label} must be a string")
    normalized = _NON_ASCII_IDENTIFIER.sub("_", value.lower()).strip("_")
    if not normalized:
        raise ValueError(f"MCP {label} has no usable ASCII identifier characters")
    return normalized


def normalize_mcp_tool_name(
    server_name: str, tool_name: str, *, tool_name_prefix: str = "mcp_"
) -> str:
    """Produce a bounded Friday tool name from untrusted MCP identifiers."""

    prefix = _identifier_part(tool_name_prefix, label="tool prefix")
    server = _identifier_part(server_name, label="server name")
    tool = _identifier_part(tool_name, label="tool name")
    canonical = f"{prefix}_{server}_{tool}"
    if len(canonical) > MAX_MCP_TOOL_NAME_LENGTH:
        raise ValueError("normalized MCP tool name exceeds Friday's 64-character cap")
    if not _CANONICAL_TOOL_NAME.fullmatch(canonical):
        raise ValueError("normalized MCP tool name must start with an ASCII letter")
    return canonical


def normalize_mcp_tool_names(
    names: Iterable[tuple[str, str]], *, tool_name_prefix: str = "mcp_"
) -> Mapping[str, tuple[str, str]]:
    """Normalize a discovered set and reject lossy-name collisions."""

    normalized: dict[str, tuple[str, str]] = {}
    for server_name, tool_name in names:
        canonical = normalize_mcp_tool_name(
            server_name, tool_name, tool_name_prefix=tool_name_prefix
        )
        if canonical in normalized:
            previous_server, previous_tool = normalized[canonical]
            raise ValueError(
                "normalized MCP tool name collision: "
                f"{canonical}; first=({_safe_source_label(previous_server)}, "
                f"{_safe_source_label(previous_tool)}); "
                f"second=({_safe_source_label(server_name)}, "
                f"{_safe_source_label(tool_name)})"
            )
        normalized[canonical] = (server_name, tool_name)
    return MappingProxyType(normalized)


def _safe_source_label(value: str) -> str:
    """Identify an untrusted name by bounded shape/fingerprint, without echoing it."""

    shape = "".join(
        "a" if char.isascii() and char.isalpha() else
        "0" if char.isascii() and char.isdigit() else
        char if char in "-_." else "?"
        for char in value[:24]
    )
    fingerprint = sha256(value.encode("utf-8")).hexdigest()[:12]
    length_label = str(len(value)) if len(value) <= 9999 else "9999+"
    return f"len={length_label},shape={shape},id={fingerprint}"


def build_mcp_metadata_index(
    metadata: Iterable[MCPToolMetadata],
) -> Mapping[str, MCPToolMetadata]:
    """Create a read-only metadata sidecar without changing ToolDefinition."""

    index: dict[str, MCPToolMetadata] = {}
    for item in metadata:
        if item.canonical_name in index:
            raise ValueError(f"duplicate MCP metadata name: {item.canonical_name}")
        index[item.canonical_name] = item
    return MappingProxyType(index)


__all__ = [
    "MAX_MCP_TOOL_NAME_LENGTH",
    "MCPClientLimits",
    "MCPClientSecurityPolicy",
    "MCPIngestionPolicy",
    "MCPDiscoveryPolicy",
    "MCPServerRuntimePolicy",
    "MCPToolMetadata",
    "MCPToolCallProvenance",
    "MCPDiscoveryState",
    "MCPServerDiscoveryState",
    "MCPProviderDiagnostics",
    "MCPDiagnosticCode",
    "MCPSafeIdentifier",
    "normalize_mcp_tool_name",
    "normalize_mcp_tool_names",
    "build_mcp_metadata_index",
]
