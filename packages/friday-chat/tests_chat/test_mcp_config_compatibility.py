"""Config-only MCP compatibility; no Chat runtime or tool selection is exercised."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from friday_chat.config import FridayChatConfig, load_friday_py_config
from friday_runtime.config import MCPRuntimeClientConfig, MCPToolProviderConfig


def test_chat_retains_canonical_mcp_stanza_for_runtime_validation(
    tmp_path: Path,
) -> None:
    stanza = {
        "enabled": True,
        "mode": "selected",
        "include_tools": ["mcp_filesystem_read_file"],
        "exclude_tools": ["mcp_filesystem_delete_file"],
        "config": {
            "auto_connect": False,
            "tool_name_prefix": "mcp_",
            "discovery": {"refresh_mode": "startup_only"},
            "limits": {"max_servers": 1},
            "security": {"allowed_workspace_ids": ["project"]},
            "ingestion": {"long_term_memory_enabled": False},
            "servers": [
                {
                    "name": "filesystem",
                    "enabled": True,
                    "required": False,
                    "transport": "stdio",
                    "command": "python",
                    "args": ["-m", "example_server"],
                    "env": {},
                    "cwd": "tools",
                    "timeout_seconds": 30,
                    "tool_timeout_seconds": 60,
                    "retry_attempts": 3,
                    "trust_level": "local",
                }
            ],
        },
    }
    config_path = tmp_path / "chat.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "llm": {"model": "openai/test-chat-model"},
                "tools": {"providers": {"mcp": stanza}},
            }
        ),
        encoding="utf-8",
    )
    chat = load_friday_py_config(config_path, env={})
    retained = chat.tools.model_dump()["providers"]["mcp"]

    assert isinstance(chat, FridayChatConfig)
    assert retained == stanza
    provider = MCPToolProviderConfig.from_dict(retained)
    assert provider == MCPToolProviderConfig.from_dict(stanza)
    assert isinstance(provider.config, MCPRuntimeClientConfig)
    assert provider.mode == "selected"
    assert provider.include_tools == ("mcp_filesystem_read_file",)
    assert provider.config.servers[0].name == "filesystem"
    assert provider.config.auto_connect is False


@pytest.mark.parametrize(
    "stanza,match",
    [
        ({"enabled": False, "config_file": "mcp.yaml"}, "MCP-WS-09"),
        ({"enabled": False, "config": {"limits": {"max_servers": 0}}}, "max_servers"),
    ],
)
def test_chat_retention_does_not_bypass_canonical_mcp_validation(
    stanza: dict[str, object], match: str
) -> None:
    with pytest.raises(ValueError, match=match):
        FridayChatConfig.model_validate({"tools": {"providers": {"mcp": stanza}}})


@pytest.mark.parametrize("version", ["2026-07-28", "2025-11-25"])
def test_both_real_yaml_loaders_preserve_http_reference(tmp_path, version):
    from friday_runtime.config import RuntimeConfig

    class Environment(dict):
        def __getitem__(self, key):
            pytest.fail(
                "Credential must remain an unresolved reference during YAML load"
            )

        def get(self, key, default=None):
            pytest.fail(
                "Credential must remain an unresolved reference during YAML load"
            )

    stanza = {
        "enabled": True,
        "mode": "all",
        "config": {
            "security": {
                "integrated_transport": "stdio_and_streamable_http",
                "trust_posture": "explicit_remote",
            },
            "servers": [
                {
                    "name": "remote",
                    "transport": "streamable_http",
                    "protocol_version": version,
                    "trust_level": "remote",
                    "url": "https://example.com/mcp",
                    "auth": "bearer_env",
                    "credential_env": "SYNTHETIC_REMOTE_REFERENCE",
                }
            ],
        },
    }
    data = {
        "llm": {"model": "openai/test-chat-model"},
        "tools": {"providers": {"mcp": stanza}},
        "runtime_paths": {
            "install_root": str(tmp_path),
            "runtime_data_root": str(tmp_path / "data"),
            "workspace_root": str(tmp_path / "workspace"),
        },
    }
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(data))
    chat = load_friday_py_config(path, env=Environment())
    (tmp_path / "workspace").mkdir()
    runtime = RuntimeConfig.from_sources(yaml_path=path, env={})
    assert chat.tools.mcp_provider == runtime.tools.providers.mcp
    assert (
        chat.tools.mcp_provider.config.servers[0].credential_env
        == "SYNTHETIC_REMOTE_REFERENCE"
    )
    assert "SYNTHETIC_REMOTE_REFERENCE" in str(
        chat.tools.mcp_provider.config.model_dump()
    )
    assert "credential_env=" not in repr(chat.tools.mcp_provider.config.servers[0])


@pytest.mark.parametrize(
    "reference",
    [
        "${SENTINEL_REFERENCE}",
        "${SENTINEL_REFERENCE:-fallback}",
        "Bearer SENTINEL_INLINE",
        "",
        None,
    ],
)
def test_chat_rejects_credential_interpolation_before_environment_access(
    tmp_path, reference
):
    class Environment(dict):
        def __getitem__(self, key):
            pytest.fail("Invalid reference was interpolated")

        def get(self, key, default=None):
            pytest.fail("Invalid reference was interpolated")

    path = tmp_path / "bad.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "tools": {
                    "providers": {
                        "mcp": {
                            "config": {
                                "servers": [
                                    {
                                        "name": "remote",
                                        "transport": "streamable_http",
                                        "credential_env": reference,
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        )
    )
    with pytest.raises(ValueError) as failure:
        load_friday_py_config(path, env=Environment())
    assert failure.value.__cause__ is None and failure.value.__context__ is None
    assert "SENTINEL" not in str(failure.value)


@pytest.mark.parametrize(
    "change",
    [
        {"command": "${SENTINEL_COMMAND}"},
        {"headers": {"Authorization": "${SENTINEL_TOKEN}"}},
        {"auth": "${SENTINEL_AUTH}"},
        {"url": "https://${SENTINEL_HOST}/mcp"},
        {"protocol_version": "${SENTINEL_VERSION}"},
        {"SENTINEL_UNKNOWN": "${SENTINEL_TOKEN}"},
    ],
)
def test_chat_validates_remote_shape_before_any_interpolation(tmp_path, change):
    class Environment(dict):
        def __contains__(self, key):
            pytest.fail("Invalid MCP config reached environment interpolation")

        def __getitem__(self, key):
            pytest.fail("Invalid MCP config read environment")

    entry = {
        "name": "remote",
        "transport": "streamable_http",
        "protocol_version": "2026-07-28",
        "trust_level": "remote",
        "url": "https://example.com/mcp",
        **change,
    }
    path = tmp_path / "invalid.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "tools": {
                    "providers": {
                        "mcp": {
                            "enabled": False,
                            "config": {
                                "security": {
                                    "integrated_transport": "stdio_and_streamable_http",
                                    "trust_posture": "explicit_remote",
                                },
                                "servers": [entry],
                            },
                        }
                    }
                }
            }
        )
    )
    with pytest.raises(ValueError) as failure:
        load_friday_py_config(path, env=Environment())
    assert "SENTINEL" not in str(failure.value)
    assert failure.value.__cause__ is failure.value.__context__ is None


def test_chat_keeps_remote_fields_literal_and_does_not_expand_disabled_url(tmp_path):
    class Environment(dict):
        def __contains__(self, key):
            pytest.fail("Remote URL must not consult environment")

        def __getitem__(self, key):
            pytest.fail("Remote URL must not consult environment")

    url = "https://example.com/${SYNTHETIC_REFERENCE}"
    entry = {
        "name": "remote",
        "transport": "streamable_http",
        "protocol_version": "2026-07-28",
        "trust_level": "remote",
        "url": url,
        "enabled": False,
    }
    path = tmp_path / "disabled.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "llm": {"model": "openai/test-chat-model"},
                "tools": {"providers": {"mcp": {"config": {"servers": [entry]}}}},
            }
        )
    )
    chat = load_friday_py_config(path, env=Environment())
    assert chat.tools.mcp_provider.config.servers[0].url == url
