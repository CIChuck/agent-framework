"""WS-00 contract, default, and fail-closed policy tests."""

from __future__ import annotations

from types import MappingProxyType

import pytest
from friday_core.mcp import (
    MCPClientLimits,
    MCPClientSecurityPolicy,
    MCPDiscoveryPolicy,
    MCPDiscoveryState,
    MCPIngestionPolicy,
    MCPProviderDiagnostics,
    MCPServerRuntimePolicy,
    MCPToolCallProvenance,
    MCPToolMetadata,
    build_mcp_metadata_index,
    normalize_mcp_tool_name,
    normalize_mcp_tool_names,
)
from pydantic import BaseModel, ValidationError


def _metadata() -> MCPToolMetadata:
    return MCPToolMetadata(
        canonical_name="mcp_filesystem_read_file",
        server_name="filesystem",
        original_name="read_file",
        transport="stdio",
        trust_level="local",
    )


def test_limits_have_bounded_defaults_for_small_and_large_profiles() -> None:
    limits = MCPClientLimits()
    assert limits.max_servers == 8
    assert limits.max_tools_per_server == 25
    assert limits.max_total_tools == 50
    assert limits.max_schema_bytes_per_tool == 8192
    assert limits.max_schema_tokens == 4000
    assert limits.max_result_bytes == 65536
    assert limits.connection_timeout_seconds == 30
    assert limits.tool_timeout_seconds == 60
    assert limits.max_parallel_server_connects == 4
    assert limits.max_parallel_tool_calls == 4
    for context_window in (50_000, 250_000, 1_000_000):
        usable_input = context_window - 2500
        protected = (
            limits.max_schema_tokens
            + limits.reserved_tool_result_tokens
            + limits.min_memory_retrieval_tokens
        )
        assert protected < usable_input
    assert MCPClientLimits.model_validate(limits.model_dump()) == limits


@pytest.mark.parametrize(
    "field,value",
    [
        ("max_servers", 0),
        ("max_tools_per_server", -1),
        ("max_schema_bytes_per_tool", 0),
        ("reserved_tool_result_tokens", 0),
        ("min_memory_retrieval_tokens", -1),
        ("connection_timeout_seconds", 0),
        ("max_total_tools", True),
    ],
)
def test_limits_reject_invalid_values(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        MCPClientLimits.model_validate({field: value})


def test_contracts_are_strict_and_immutable() -> None:
    with pytest.raises(ValidationError):
        MCPClientLimits.model_validate({"unknown_limit": 1})
    with pytest.raises(ValidationError):
        MCPClientLimits.model_validate({"max_servers": "8"})
    with pytest.raises(ValidationError):
        MCPClientLimits().max_servers = 99


def test_security_defaults_are_stdio_only_and_content_safe() -> None:
    policy = MCPClientSecurityPolicy()
    assert policy.integrated_transport == "stdio_only"
    assert policy.require_explicit_stdio_command
    assert policy.redact_environment
    assert policy.redact_headers
    assert policy.redact_arguments
    assert not policy.store_raw_tool_results
    assert not policy.store_argument_hashes
    assert policy.model_dump()["store_argument_hashes"] is False


@pytest.mark.parametrize(
    "unsafe_policy",
    [
        {"integrated_transport": "sse"},
        {"require_explicit_stdio_command": False},
        {"redact_environment": False},
        {"redact_headers": False},
        {"redact_arguments": False},
        {"store_raw_tool_results": True},
        {"store_argument_hashes": True},
    ],
)
def test_security_policy_rejects_unsafe_first_pass(
    unsafe_policy: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        MCPClientSecurityPolicy.model_validate(unsafe_policy)


def test_ingestion_discovery_and_server_policy_defaults() -> None:
    assert not MCPIngestionPolicy().long_term_memory_enabled
    assert MCPIngestionPolicy().require_sanitized_content
    assert MCPDiscoveryPolicy().refresh_mode == "startup_only"
    assert MCPServerRuntimePolicy().transport == "stdio"
    assert not MCPServerRuntimePolicy().required
    with pytest.raises(ValidationError):
        MCPIngestionPolicy(require_sanitized_content=False)
    with pytest.raises(ValidationError):
        MCPDiscoveryPolicy.model_validate({"refresh_mode": "live"})
    with pytest.raises(ValidationError):
        MCPServerRuntimePolicy.model_validate({"transport": "sse"})


@pytest.mark.parametrize(
    "contract",
    [
        MCPClientLimits(),
        MCPClientSecurityPolicy(),
        MCPIngestionPolicy(),
        MCPDiscoveryPolicy(),
        MCPServerRuntimePolicy(),
        MCPDiscoveryState(),
        MCPProviderDiagnostics(),
        _metadata(),
        MCPToolCallProvenance(tool=_metadata(), status="succeeded"),
    ],
)
def test_contracts_round_trip_through_json(contract: BaseModel) -> None:
    model_type = type(contract)
    assert model_type.model_validate_json(contract.model_dump_json()) == contract


def test_normalization_is_deterministic_and_uses_safe_ascii() -> None:
    assert (
        normalize_mcp_tool_name("My Server", "Read.File") == "mcp_my_server_read_file"
    )
    assert normalize_mcp_tool_name("file-system", "READ__FILE") == (
        "mcp_file_system_read_file"
    )
    assert (
        normalize_mcp_tool_name(
            "filesystem", "read_file", tool_name_prefix="federated_"
        )
        == "federated_filesystem_read_file"
    )


@pytest.mark.parametrize(
    "server,tool",
    [
        ("!!!", "read"),
        ("server", "øø"),
        ("s" * 60, "read"),
        ("server", 12),
    ],
)
def test_normalization_rejects_unusable_or_oversize_names(
    server: object, tool: object
) -> None:
    with pytest.raises((TypeError, ValueError)):
        normalize_mcp_tool_name(server, tool)  # type: ignore[arg-type]


def test_normalization_rejects_unusable_prefix() -> None:
    with pytest.raises(ValueError):
        normalize_mcp_tool_name("server", "read", tool_name_prefix="!!!")
    with pytest.raises(ValueError):
        normalize_mcp_tool_name("server", "read", tool_name_prefix="123")


def test_normalization_rejects_collisions_and_returns_read_only_index() -> None:
    with pytest.raises(ValueError, match="collision"):
        normalize_mcp_tool_names(
            [("file-system", "read.file"), ("file_system", "read_file")]
        )
    names = normalize_mcp_tool_names([("filesystem", "read_file")])
    assert isinstance(names, MappingProxyType)
    assert names["mcp_filesystem_read_file"] == ("filesystem", "read_file")


def test_metadata_sidecar_is_typed_and_collision_safe() -> None:
    item = _metadata()
    index = build_mcp_metadata_index([item])
    assert isinstance(index, MappingProxyType)
    assert index[item.canonical_name] == item
    assert item.model_dump()["provider"] == "mcp"
    custom = MCPToolMetadata(
        canonical_name="federated_filesystem_read_file",
        server_name="filesystem",
        original_name="read_file",
        tool_name_prefix="federated_",
        transport="stdio",
        trust_level="local",
    )
    assert custom.canonical_name == "federated_filesystem_read_file"
    with pytest.raises(ValueError, match="duplicate"):
        build_mcp_metadata_index([item, item])
    with pytest.raises(ValidationError):
        MCPToolMetadata.model_validate(
            {**item.model_dump(), "canonical_name": "not valid!"}
        )
    with pytest.raises(ValidationError):
        MCPToolMetadata.model_validate(
            {**item.model_dump(), "canonical_name": "mcp_other_read_file"}
        )


def test_provenance_and_diagnostics_cannot_carry_raw_payloads() -> None:
    provenance = MCPToolCallProvenance(tool=_metadata(), status="succeeded")
    assert provenance.arguments_redacted
    assert "arguments" not in provenance.model_dump()
    assert "result" not in provenance.model_dump()
    assert "argument_hash" not in provenance.model_dump()
    with pytest.raises(ValidationError):
        MCPToolCallProvenance.model_validate(
            {"tool": _metadata(), "status": "succeeded", "arguments": {"key": "secret"}}
        )
    with pytest.raises(ValidationError):
        MCPToolCallProvenance(
            tool=_metadata(), status="failed", arguments_redacted=False
        )
    diagnostics = MCPProviderDiagnostics(codes=("connection_failed",))
    assert diagnostics.model_dump()["codes"] == ("connection_failed",)
    with pytest.raises(ValidationError):
        MCPProviderDiagnostics.model_validate({"codes": ["raw exception text"]})


def test_discovery_counts_are_consistent() -> None:
    state = MCPDiscoveryState(
        status="completed", connected_servers=1, discovered_tools=2, selected_tools=1
    )
    assert state.model_dump()["selected_tools"] == 1
    with pytest.raises(ValidationError):
        MCPDiscoveryState(discovered_tools=1, selected_tools=2)
