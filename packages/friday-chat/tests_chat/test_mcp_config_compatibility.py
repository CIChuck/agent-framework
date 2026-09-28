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
