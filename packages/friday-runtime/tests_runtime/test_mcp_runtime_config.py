"""WS-01 canonical MCP configuration tests; no server is started here."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from friday_core.mcp import MCPClientLimits, MCPClientSecurityPolicy
from friday_mcp.config import MCPConfig, MCPServerConfig, TransportType
from friday_runtime.config import (
    MCPRuntimeClientConfig,
    MCPToolProviderConfig,
    RuntimeConfig,
    ToolProviderConfig,
    ToolsConfig,
)


def _provider(
    config: dict[str, object] | None = None, **other: object
) -> MCPToolProviderConfig:
    return MCPToolProviderConfig.from_dict({"config": config or {}, **other})


def test_default_and_disabled_provider_are_safe_and_typed() -> None:
    provider = _provider(enabled=False)
    assert provider.config.servers == ()
    assert provider.config.limits == MCPClientLimits()
    assert provider.config.security == MCPClientSecurityPolicy()
    assert provider.config.security.integrated_transport == "stdio_only"
    assert provider.config.security.store_argument_hashes is False
    assert provider.config.ingestion.long_term_memory_enabled is False


def test_direct_mcp_constructor_defaults_to_selected() -> None:
    assert MCPToolProviderConfig().mode == "selected"
    assert ToolProviderConfig().mode == "all"


def test_omitted_mcp_mode_parses_as_selected() -> None:
    assert MCPToolProviderConfig.from_dict({}).mode == "selected"
    assert ToolProviderConfig.from_dict({}).mode == "all"


def test_runtime_source_default_selects_mcp_only(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    providers = RuntimeConfig.from_sources(
        env={},
        overrides={
            "install_root": str(tmp_path),
            "runtime_data_root": str(tmp_path / "data"),
            "workspace_root": str(workspace),
        },
    ).tools.providers
    assert providers.mcp.mode == "selected"
    assert providers.builtin.mode == "all"
    assert providers.friday_tools.mode == "all"


def test_explicit_all_mcp_mode_remains_valid(tmp_path: Path) -> None:
    assert MCPToolProviderConfig(mode="all").mode == "all"
    assert MCPToolProviderConfig.from_dict({"mode": "all"}).mode == "all"
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    runtime = RuntimeConfig.from_sources(
        env={},
        overrides={
            "install_root": str(tmp_path),
            "runtime_data_root": str(tmp_path / "data"),
            "workspace_root": str(workspace),
            "tools_config": {"providers": {"mcp": {"mode": "all"}}},
        },
    )
    assert runtime.tools.providers.mcp.mode == "all"


def test_invalid_mcp_mode_still_fails() -> None:
    with pytest.raises(ValueError, match="mode must be 'all' or 'selected'"):
        MCPToolProviderConfig.from_dict({"mode": "automatic"})


def test_valid_stdio_optional_and_required_servers_round_trip(tmp_path: Path) -> None:
    config = {
        "auto_connect": False,
        "tool_name_prefix": "federated_",
        "discovery": {"refresh_mode": "startup_only"},
        "limits": {"max_servers": 2},
        "security": {"allowed_workspace_ids": ["project"]},
        "ingestion": {"long_term_memory_enabled": False},
        "servers": [
            {"name": "optional", "command": "npx", "cwd": "tools"},
            {
                "name": "required",
                "required": True,
                "command": "python",
                "args": ["-m", "server"],
            },
        ],
    }
    provider = _provider(
        config, enabled=True, mode="selected", include_tools=["federated_optional_read"]
    )
    assert provider.enabled
    assert provider.config.auto_connect is False
    assert [server.required for server in provider.config.servers] == [False, True]
    assert provider.config.security.allowed_workspace_ids == ("project",)
    assert provider.include_tools == ("federated_optional_read",)
    assert "npx" not in repr(provider.config.servers[0])
    assert "tools" not in repr(provider.config.servers[0])
    assert (
        MCPRuntimeClientConfig.model_validate(provider.config.model_dump())
        == provider.config
    )
    provider.config.validate_workspace(str(tmp_path))


def test_legacy_protocol_local_mcp_config_is_not_mutated() -> None:
    # Existing direct-use SSE APIs remain independent of runtime stdio policy.
    legacy = MCPConfig(
        servers=[
            MCPServerConfig(
                name="remote",
                transport=TransportType.SSE,
                url="https://example.test/sse",
            )
        ]
    )
    assert legacy.servers[0].transport == TransportType.SSE
    assert MCPRuntimeClientConfig.model_fields["servers"].annotation is not None
    with pytest.raises(ValueError, match="transport"):
        MCPToolProviderConfig.from_dict({"config": legacy})
    local = MCPConfig(servers=[MCPServerConfig(name="local", command="python")])
    normalized = MCPToolProviderConfig.from_dict({"config": local})
    assert normalized.config.servers[0].name == "local"
    assert (
        MCPToolProviderConfig.from_dict({"config": {"server": None}}).config.servers
        == ()
    )
    with pytest.raises(ValueError, match="server exposure"):
        MCPToolProviderConfig.from_dict({"config": {"server": {"mode": "agent"}}})


@pytest.mark.parametrize(
    "payload,match",
    [
        ({"config_file": "mcp.yaml"}, "MCP-WS-09"),
        ({"config": {"config_file": "mcp.yaml"}}, "MCP-WS-09"),
        ({"future": True}, "Unknown keys"),
        ({"config": {"future": True}}, "<unknown>"),
        (
            {"config": {"servers": [{"name": "one", "command": "npx", "future": 1}]}},
            "<unknown>",
        ),
    ],
)
def test_future_fields_fail_closed(payload: dict[str, object], match: str) -> None:
    with pytest.raises(ValueError, match=match):
        MCPToolProviderConfig.from_dict(payload)


@pytest.mark.parametrize(
    "server,match",
    [
        (
            {"name": "one", "transport": "sse", "url": "https://example.test"},
            "transport",
        ),
        ({"name": "one"}, "command"),
        ({"name": "one", "enabled": False, "required": True}, "required"),
        ({"name": "one", "command": "npx", "timeout_seconds": 0}, "timeout_seconds"),
        (
            {"name": "one", "command": "npx", "tool_timeout_seconds": 0},
            "tool_timeout_seconds",
        ),
        ({"name": "one", "command": "npx", "retry_attempts": -1}, "retry_attempts"),
        ({"name": "one", "command": "npx", "trust_level": "remote"}, "trust_level"),
        ({"name": "one", "command": "npx", "cwd": "../outside"}, "cwd"),
    ],
)
def test_invalid_server_settings_fail(server: dict[str, object], match: str) -> None:
    with pytest.raises(ValueError, match=match):
        _provider({"servers": [server]})


def test_disabled_server_needs_no_command() -> None:
    provider = _provider({"servers": [{"name": "later", "enabled": False}]})
    assert provider.config.servers[0].command is None


@pytest.mark.parametrize(
    "servers",
    [
        [{"name": "one", "command": "npx"}, {"name": "one", "command": "python"}],
        [
            {"name": "file-system", "command": "npx"},
            {"name": "file_system", "command": "python"},
        ],
    ],
)
def test_duplicate_canonical_server_names_fail(
    servers: list[dict[str, object]],
) -> None:
    with pytest.raises(ValueError, match="duplicate canonical"):
        _provider({"servers": servers})


def test_limits_and_filters_fail_closed() -> None:
    with pytest.raises(ValueError, match="max_servers"):
        _provider(
            {
                "limits": {"max_servers": 1},
                "servers": [
                    {"name": "one", "command": "npx"},
                    {"name": "two", "command": "python"},
                ],
            }
        )
    with pytest.raises(ValueError, match="max_servers"):
        _provider({"limits": {"max_servers": 0}})
    with pytest.raises(ValueError, match="overlap"):
        _provider(include_tools=["mcp_one_read"], exclude_tools=["mcp_one_read"])
    with pytest.raises(ValueError, match="canonical"):
        _provider(include_tools=["bad-name"])
    with pytest.raises(ValueError, match="canonical"):
        _provider(include_tools=[""])


def test_security_rejects_unsafe_override() -> None:
    with pytest.raises(ValueError, match="argument hashes"):
        _provider({"security": {"store_argument_hashes": True}})
    with pytest.raises(ValueError, match="integrated_transport"):
        _provider({"security": {"integrated_transport": "sse"}})


def test_cwd_must_remain_inside_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    inside = workspace / "tools"
    inside.mkdir()
    provider = _provider(
        {"servers": [{"name": "one", "command": "npx", "cwd": str(inside)}]}
    )
    provider.config.validate_workspace(str(workspace))
    outside = _provider(
        {"servers": [{"name": "one", "command": "npx", "cwd": str(tmp_path)}]}
    )
    with pytest.raises(ValueError, match="workspace_root"):
        outside.config.validate_workspace(str(workspace))
    link = workspace / "escape"
    link.symlink_to(tmp_path, target_is_directory=True)
    symlink = _provider(
        {"servers": [{"name": "one", "command": "npx", "cwd": "escape"}]}
    )
    with pytest.raises(ValueError, match="workspace_root"):
        symlink.config.validate_workspace(str(workspace))
    with pytest.raises(ValueError, match="workspace_root"):
        RuntimeConfig(
            install_root=str(tmp_path),
            runtime_data_root=str(tmp_path / "data"),
            workspace_root=str(workspace),
            tools_config=ToolsConfig.from_dict(
                {
                    "providers": {
                        "mcp": {
                            "config": {
                                "servers": [
                                    {
                                        "name": "one",
                                        "command": "npx",
                                        "cwd": str(tmp_path),
                                    }
                                ]
                            },
                        }
                    }
                }
            ),
        )


def test_validation_errors_never_echo_environment_secret() -> None:
    secret = "never-print-this-token"
    with pytest.raises(ValueError, match="command") as failure:
        _provider({"servers": [{"name": "one", "env": {"API_KEY": secret}}]})
    assert secret not in str(failure.value)


def test_runtime_yaml_canonical_parse_and_config_file_rejection(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config_path = tmp_path / "runtime.yaml"
    mcp_data: dict[str, object] = {
        "enabled": True,
        "mode": "selected",
        "include_tools": ["mcp_fs_read"],
        "config": {
            "auto_connect": False,
            "servers": [
                {"name": "fs", "command": "npx", "cwd": "tools"},
            ],
        },
    }
    data = {
        "runtime_paths": {
            "install_root": str(tmp_path),
            "runtime_data_root": str(tmp_path / "data"),
            "workspace_root": str(workspace),
        },
        "tools": {"providers": {"mcp": mcp_data}},
    }
    config_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    runtime = RuntimeConfig.from_sources(yaml_path=config_path, env={})
    assert isinstance(runtime.tools.providers.mcp.config, MCPRuntimeClientConfig)
    assert runtime.tools.providers.mcp.config.servers[0].name == "fs"
    mcp_data["config_file"] = "external.yaml"
    config_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ValueError, match="MCP-WS-09"):
        RuntimeConfig.from_sources(yaml_path=config_path, env={})


def test_non_mcp_provider_behavior_is_unchanged() -> None:
    tools = ToolsConfig.from_dict(
        {"providers": {"builtin": {"enabled": True, "mode": "all"}}}
    )
    assert tools.providers.builtin.enabled
    assert not tools.providers.mcp.enabled


def remote_server(**changes):
    return {
        "name": "remote",
        "transport": "streamable_http",
        "protocol_version": "2026-07-28",
        "trust_level": "remote",
        "url": "https://example.com/mcp",
        **changes,
    }


def remote_stanza(servers, **changes):
    return {
        "enabled": True,
        "mode": "all",
        "config": {
            "security": {
                "integrated_transport": "stdio_and_streamable_http",
                "trust_posture": "explicit_remote",
            },
            "servers": servers,
            **changes,
        },
    }


@pytest.mark.parametrize(
    "change",
    [
        {"protocol_version": None},
        {"protocol_version": "auto"},
        {"trust_level": "local"},
        {"command": "SENTINEL_COMMAND"},
        {"args": []},
        {"env": {}},
        {"cwd": None},
        {"protocol_profile": "modern"},
        {"headers": {}},
        {"cookies": {}},
        {"proxy": None},
        {"verify_tls": False},
        {"allow_fixture_http": True},
        {"ca_file": None},
        {"retry_attempts": 1},
        {"retry_attempts": False},
        {"timeout_seconds": True},
        {"tool_timeout_seconds": 0},
        {"enabled": "yes"},
        {"required": True, "enabled": False},
        {"url": "http://example.com/mcp"},
        {"url": "https://user:SENTINEL_TOKEN@example.com/mcp"},
        {"url": "https://example.com/mcp?SENTINEL_QUERY"},
        {"url": "https://example.com/mcp#SENTINEL_FRAGMENT"},
        {"url": "https://127.0.0.1/mcp"},
        {"url": "https://example.com:8443/mcp"},
        {"url": "https://[::ffff:127.0.0.1]/mcp"},
        {"url": "https://example.com/雪"},
        {"auth": "inline"},
        {"credential_env": "SENTINEL_TOKEN"},
        {"auth": "bearer_env"},
        {"auth": "bearer_env", "credential_env": "${SENTINEL_TOKEN}"},
        {"network": {"allowed_addresses": ["127.0.0.1/32"]}},
        {"network": {"allowed_addresses": ["*.example.com"]}},
        {"network": {"allowed_addresses": ["127.0.0.1", "127.0.0.1"]}},
        {"network": {"allowed_addresses": ["::ffff:127.0.0.1"]}},
        {"network": {"allowed_ports": [True]}},
        {"network": {"allowed_ports": []}},
        {"network": {"allowed_ports": [443, 443]}},
        {"network": {"allowed_ports": [65536]}},
    ],
)
@pytest.mark.parametrize("disabled", [False, True])
def test_http_union_rejects_bad_shapes_including_disabled_before_effects(
    change, disabled
):
    entry = (
        remote_server(enabled=not disabled, **change)
        if "enabled" not in change
        else remote_server(**change)
    )
    with pytest.raises(ValueError) as failure:
        MCPToolProviderConfig.from_dict(remote_stanza([entry]))
    current = failure.value
    while current is not None:
        assert "SENTINEL" not in str(current)
        current = current.__cause__ or current.__context__


def test_remote_opt_in_and_local_union_defaults():
    with pytest.raises(ValueError, match="explicit remote"):
        _provider({"servers": [remote_server()]})
    off = _provider({"servers": [remote_server(enabled=False)]})
    assert off.config.security.trust_posture == "local_stdio_only"
    for profile in ("legacy", "modern", "auto"):
        local = _provider(
            {
                "servers": [
                    {"name": "local", "command": "fake", "protocol_profile": profile}
                ]
            }
        )
        assert local.config.servers[0].protocol_profile == profile
    assert (
        _provider({"servers": [{"name": "local", "command": "fake"}]})
        .config.servers[0]
        .protocol_profile
        == "legacy"
    )
