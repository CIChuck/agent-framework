"""WS-00 contract, default, and fail-closed policy tests."""

from __future__ import annotations

from datetime import datetime, timezone
from types import MappingProxyType

import pytest
from friday_core.mcp import (
    MCPClientLimits,
    MCPClientSecurityPolicy,
    MCPDiscoveryPolicy,
    MCPDiscoveryState,
    MCPIngestionPolicy,
    MCPProviderDiagnostics,
    MCPServerDiscoveryState,
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


def test_registration_metadata_is_additive_content_minimal_and_repr_safe() -> None:
    old = _metadata().model_dump(exclude={"schema_byte_size", "discovery_state"})
    restored = MCPToolMetadata.model_validate(old)
    assert restored.schema_byte_size is None
    assert restored.discovery_state == "not_checked"
    populated = restored.model_copy(
        update={
            "schema_byte_size": 240,
            "schema_token_estimate": 240,
            "discovery_state": "discovered",
        }
    )
    assert MCPToolMetadata.model_validate_json(populated.model_dump_json()) == populated
    assert "original_name=" not in repr(populated)
    assert set(populated.model_dump()) - set(old) == {
        "schema_byte_size",
        "discovery_state",
    }
    with pytest.raises(ValidationError):
        MCPToolMetadata.model_validate({**old, "schema_byte_size": -1})
    assert MCPProviderDiagnostics(
        codes=("missing_include", "registration_failed")
    ).codes == ("missing_include", "registration_failed")


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
    assert policy.trust_posture == "local_stdio_only"
    assert policy.path_scope == "workspace_only"
    assert policy.allowed_workspace_ids == ()
    assert policy.require_explicit_stdio_command
    assert policy.redact_environment
    assert policy.redact_headers
    assert policy.redact_arguments
    assert not policy.store_raw_tool_results
    assert not policy.store_argument_hashes
    assert policy.model_dump()["store_argument_hashes"] is False
    scoped = MCPClientSecurityPolicy(allowed_workspace_ids=("project-1",))
    assert (
        MCPClientSecurityPolicy.model_validate_json(scoped.model_dump_json()) == scoped
    )


@pytest.mark.parametrize(
    "unsafe_policy",
    [
        {"integrated_transport": "sse"},
        {"trust_posture": "remote"},
        {"path_scope": "unrestricted"},
        {"allowed_workspace_ids": ("/private/workspace",)},
        {"allowed_workspace_ids": ("x" * 65,)},
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
    ingestion = MCPIngestionPolicy()
    assert not ingestion.long_term_memory_enabled
    assert ingestion.require_sanitized_content
    assert ingestion.opted_in_servers == ()
    assert ingestion.opted_in_tools == ()
    assert MCPDiscoveryPolicy().refresh_mode == "startup_only"
    assert MCPServerRuntimePolicy().transport == "stdio"
    assert not MCPServerRuntimePolicy().required
    with pytest.raises(ValidationError):
        MCPIngestionPolicy(require_sanitized_content=False)
    with pytest.raises(ValidationError):
        MCPIngestionPolicy(long_term_memory_enabled=True)
    with pytest.raises(ValidationError):
        MCPIngestionPolicy(opted_in_servers=("server/secret",))
    with pytest.raises(ValidationError):
        MCPIngestionPolicy(opted_in_tools=("read.file",))
    assert MCPIngestionPolicy(
        long_term_memory_enabled=True, opted_in_tools=("mcp_server_read",)
    ).model_dump()["opted_in_tools"] == ("mcp_server_read",)
    server_opt_in = MCPIngestionPolicy(
        long_term_memory_enabled=True, opted_in_servers=("filesystem",)
    )
    assert (
        MCPIngestionPolicy.model_validate_json(server_opt_in.model_dump_json())
        == server_opt_in
    )
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
        MCPServerDiscoveryState(server_id="filesystem"),
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
    with pytest.raises(ValueError, match="collision") as collision:
        normalize_mcp_tool_names(
            [("file-system", "read.file"), ("file_system", "read_file")]
        )
    message = str(collision.value)
    assert "mcp_file_system_read_file" in message
    assert "first=(len=11,shape=aaaa-aaaaaa" in message
    assert "second=(len=11,shape=aaaa_aaaaaa" in message
    assert "shape=aaaa.aaaa" in message
    assert "shape=aaaa_aaaa" in message
    assert "file-system" not in message
    assert "read.file" not in message
    with pytest.raises(ValueError, match="collision") as long_collision:
        normalize_mcp_tool_names(
            [("file-system", "read"), ("file" + "-" * 10_000 + "system", "read")]
        )
    assert "len=9999+" in str(long_collision.value)
    assert len(str(long_collision.value)) < 250
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
    enriched = MCPToolMetadata.model_validate(
        {
            **item.model_dump(),
            "schema_token_estimate": 42,
            "schema_sanitization_state": "sanitized",
            "filter_state": "excluded",
            "filter_diagnostic_codes": ("filter_excluded",),
        }
    )
    assert MCPToolMetadata.model_validate_json(enriched.model_dump_json()) == enriched
    assert item.schema_token_estimate is None
    assert item.schema_sanitization_state == "not_checked"
    assert item.filter_state == "not_evaluated"
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
    for invalid in (
        {"schema_token_estimate": -1},
        {"schema_sanitization_state": "raw secret"},
        {"filter_state": "unknown"},
        {"filter_diagnostic_codes": ["raw exception text"]},
    ):
        with pytest.raises(ValidationError):
            MCPToolMetadata.model_validate({**item.model_dump(), **invalid})


def test_provenance_and_diagnostics_cannot_carry_raw_payloads() -> None:
    provenance = MCPToolCallProvenance(tool=_metadata(), status="succeeded")
    assert provenance.arguments_redacted
    assert "arguments" not in provenance.model_dump()
    assert "result" not in provenance.model_dump()
    assert "argument_hash" not in provenance.model_dump()
    assert provenance.call_id is None
    assert provenance.transcript_correlation_id is None
    assert provenance.memory_correlation_id is None
    assert provenance.output_sanitization_state == "not_checked"
    assert provenance.ingestion_decision == "disabled"
    correlated = MCPToolCallProvenance(
        tool=_metadata(),
        status="succeeded",
        call_id="call-1",
        output_sanitization_state="sanitized",
        ingestion_decision="ingested",
        memory_ingested=True,
        transcript_correlation_id="turn-1",
        memory_correlation_id="memory-1",
    )
    assert (
        MCPToolCallProvenance.model_validate_json(correlated.model_dump_json())
        == correlated
    )
    with pytest.raises(ValidationError):
        MCPToolCallProvenance.model_validate(
            {"tool": _metadata(), "status": "succeeded", "arguments": {"key": "secret"}}
        )
    with pytest.raises(ValidationError):
        MCPToolCallProvenance(
            tool=_metadata(), status="failed", arguments_redacted=False
        )
    for invalid in (
        {"call_id": "/secret"},
        {"transcript_correlation_id": "x" * 65},
        {"output_sanitization_state": "raw"},
        {"ingestion_decision": "ingested"},
    ):
        with pytest.raises(ValidationError):
            MCPToolCallProvenance.model_validate(
                {"tool": _metadata(), "status": "succeeded", **invalid}
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


def test_discovery_tracks_bounded_per_server_state() -> None:
    server = MCPServerDiscoveryState(
        server_id="filesystem",
        connection_state="connected",
        catalog_version="v1.2",
        cache_timestamp=datetime(2026, 9, 27, tzinfo=timezone.utc),
        rejected_tools=1,
        filtered_tools=2,
        diagnostic_codes=("invalid_schema", "filter_excluded"),
        refresh_eligible=False,
    )
    state = MCPDiscoveryState(
        status="completed",
        connected_servers=1,
        discovered_tools=3,
        selected_tools=1,
        servers=(server,),
    )
    assert MCPDiscoveryState.model_validate_json(state.model_dump_json()) == state
    assert MCPDiscoveryState().servers == ()
    for invalid in (
        {"server_id": "/private/path"},
        {"connection_state": "raw exception"},
        {"catalog_version": "x" * 65},
        {"cache_timestamp": datetime(2026, 9, 27)},
        {"rejected_tools": -1},
        {"diagnostic_codes": ("raw exception",)},
    ):
        with pytest.raises(ValidationError):
            MCPServerDiscoveryState.model_validate({"server_id": "safe", **invalid})
    with pytest.raises(ValidationError):
        MCPDiscoveryState(servers=(server, server))


def test_execution_provenance_optional_sizes_and_fixed_failure_roundtrip() -> None:
    old = MCPToolCallProvenance(tool=_metadata(), status='succeeded')
    assert old.result_size_bytes is None and old.model_result_size_bytes is None
    assert old.failure_code is None
    for status, code, state in [
        ('succeeded', None, 'sanitized'), ('failed', 'tool_error', 'sanitized'),
        ('failed', 'invalid_result', 'sanitized'), ('failed', 'execution_error', 'sanitized'),
        ('failed', 'timeout', 'sanitized'), ('blocked', 'output_rejected', 'rejected'),
    ]:
        facts = MCPToolCallProvenance.model_validate({
            'tool': _metadata(), 'status': status, 'failure_code': code,
            'output_sanitization_state': state, 'result_size_bytes': 42,
            'model_result_size_bytes': 64,
        })
        assert MCPToolCallProvenance.model_validate_json(facts.model_dump_json()) == facts
        assert facts.ingestion_decision == 'disabled' and not facts.memory_ingested


@pytest.mark.parametrize('invalid', [
    {'result_size_bytes': -1}, {'model_result_size_bytes': -1},
    {'result_size_bytes': True}, {'failure_code': 'raw secret exception'},
    {'failure_code': 'tool_error'},
    {'status': 'failed', 'failure_code': 'output_rejected'},
    {'status': 'blocked', 'failure_code': 'output_rejected', 'output_sanitization_state': 'sanitized'},
    {'status': 'blocked', 'failure_code': 'timeout'}, {'arguments_hash': 'hash'},
])
def test_execution_provenance_rejects_bad_sizes_status_codes_and_hashes(invalid) -> None:
    with pytest.raises(ValidationError):
        MCPToolCallProvenance.model_validate({'tool': _metadata(), 'status': 'succeeded', **invalid})


def test_rejected_output_cannot_claim_success_without_failure_code():
    with pytest.raises(ValidationError):
        MCPToolCallProvenance(tool=_metadata(), status="succeeded", output_sanitization_state="rejected")
