# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
from pathlib import Path
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from friday_core.profiles import MemoryProfile
from friday_runtime.config import (
    EmbeddingServiceConfig,
    LLMServiceConfig,
    MCPToolProviderConfig,
    RuntimeConfig,
    ToolProviderConfig,
    ToolProvidersConfig,
    ToolsConfig,
)
from friday_runtime.di import DIContainer
from friday_runtime.tool_loading import ToolProviderLoadError
from friday_transcript import SQLiteTranscriptStore


def _config(tmp_path: Path, memory_mode: str) -> RuntimeConfig:
    install_root = tmp_path / "install"
    runtime_data_root = tmp_path / "runtime-data" / "friday"
    workspace_root = tmp_path / "workspace"
    install_root.mkdir(parents=True)
    runtime_data_root.parent.mkdir(parents=True)
    workspace_root.mkdir(parents=True)
    return RuntimeConfig(
        memory_mode=memory_mode,
        install_root=str(install_root),
        runtime_data_root=str(runtime_data_root),
        workspace_root=str(workspace_root),
    )


def test_di_single_agent_mode_keeps_multi_agent_stack_disabled(tmp_path: Path):
    di = DIContainer(_config(tmp_path, "single_agent"), MemoryProfile.FULL)
    di.memory = MagicMock()
    di._create_multi_agent_stack()
    assert di.multi_agent_memory is None
    assert di.multi_agent_journal is None
    assert di.multi_agent_coordinator is None


def test_di_multi_agent_mode_builds_multi_agent_stack(tmp_path: Path):
    di = DIContainer(_config(tmp_path, "multi_agent"), MemoryProfile.FULL)
    di.memory = MagicMock()
    di._create_multi_agent_stack()
    assert di.multi_agent_memory is not None
    assert di.multi_agent_journal is not None
    assert di.multi_agent_coordinator is not None


def test_di_creates_named_llm_pool_and_selects_default_service(tmp_path: Path):
    config = _config(tmp_path, "single_agent")
    config.llm_pool_default_service = "reasoning"
    config.llm_pool_services = {
        "default": LLMServiceConfig(
            provider="openai",
            model="gpt-4o-mini",
            api_key="default-key",
        ),
        "reasoning": LLMServiceConfig(
            provider="openai",
            model="o3",
            api_key="reasoning-key",
        ),
    }

    di = DIContainer(config, MemoryProfile.FULL)
    di._create_llm_services()

    assert set(di.llm_pool) == {"default", "reasoning"}
    assert di.llm is di.llm_pool["reasoning"]
    assert di.llm_pool["default"].model == "gpt-4o-mini"
    assert di.llm_pool["reasoning"].model == "o3"
    assert di.embeddings is not None


def test_di_maps_runtime_resilience_to_service_clients(tmp_path: Path):
    config = _config(tmp_path, "single_agent")
    config.llm_pool_services = {
        "default": LLMServiceConfig.from_dict(
            {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "api_key": "default-key",
                "resilience": {
                    "timeout_seconds": 45,
                    "max_retries": 4,
                },
            }
        )
    }

    di = DIContainer(config, MemoryProfile.FULL)
    di._create_llm_services()

    assert di.llm is not None
    assert di.llm.resilience.timeout_seconds == 45
    assert di.llm.resilience.max_retries == 4


def test_di_creates_named_embedding_pool_and_selects_default_service(tmp_path: Path):
    config = _config(tmp_path, "single_agent")
    config.embedding_pool_default_service = "graph"
    config.embedding_pool_services = {
        "default": EmbeddingServiceConfig(
            provider="openai",
            model="text-embedding-3-small",
            api_key="default-embed-key",
        ),
        "graph": EmbeddingServiceConfig(
            provider="openai",
            model="text-embedding-3-large",
            api_key="graph-embed-key",
        ),
    }

    di = DIContainer(config, MemoryProfile.FULL)
    di._create_llm_services()

    assert set(di.embedding_pool) == {"default", "graph"}
    assert di.embeddings is di.embedding_pool["graph"]
    assert di.embeddings.api_key == "graph-embed-key"


def test_di_skips_archive_extractor_when_disabled(tmp_path: Path):
    config = _config(tmp_path, "single_agent")
    config.memory_extraction_enabled = False

    di = DIContainer(config, MemoryProfile.FULL)
    di.memory = MagicMock()
    di._create_context_engine()

    assert di.context_engine is not None
    assert di.context_engine._extractor is None


def test_di_uses_configured_archive_extraction_services(tmp_path: Path):
    config = _config(tmp_path, "single_agent")
    config.llm_pool_services = {
        "default": LLMServiceConfig(
            provider="openai",
            model="gpt-4o-mini",
            api_key="default-key",
        ),
        "extractor": LLMServiceConfig(
            provider="openai",
            model="gpt-4.1-mini",
            api_key="extractor-key",
        ),
    }
    config.embedding_pool_services = {
        "default": EmbeddingServiceConfig(
            provider="openai",
            model="text-embedding-3-small",
            api_key="embed-key",
        ),
        "archive": EmbeddingServiceConfig(
            provider="openai",
            model="text-embedding-3-large",
            api_key="archive-key",
        ),
    }
    config.memory_extraction_enabled = True
    config.memory_extraction_llm_service = "extractor"
    config.memory_extraction_embedding_service = "archive"
    config.memory_extraction_max_tokens = 2048
    config.memory_extraction_user_name = "Chuck"
    config.memory_extraction_assistant_name = "Friday"
    config.memory_extraction_ontology = {
        "node_types": {"person": {"description": "human"}},
        "edge_relations": {"association": ["KNOWS"]},
    }

    di = DIContainer(config, MemoryProfile.FULL)
    di._create_llm_services()
    di.memory = MagicMock()
    di._create_context_engine()

    assert di.context_engine is not None
    extractor = di.context_engine._extractor
    assert extractor is not None
    assert extractor._llm is di.llm_pool["extractor"]
    assert extractor._embedding_model is di.embedding_pool["archive"]
    assert extractor._max_tokens == 2048
    assert extractor._user_name == "Chuck"
    assert extractor._assistant_name == "Friday"


@pytest.mark.asyncio
async def test_di_uses_transcript_backed_episodic_store_when_enabled(tmp_path: Path):
    config = _config(tmp_path, "single_agent")
    config.transcript_enabled = True
    config.transcript_path = "transcripts/runtime.db"
    config.transcript_capture_context_log = False

    di = DIContainer(config, MemoryProfile.FULL)
    di._create_llm_services()
    await di._create_storage_adapters()

    assert isinstance(di.transcript_store, SQLiteTranscriptStore)
    assert di.episodic_store is not None
    assert di.episodic_store.__class__.__name__ == "TranscriptBackedEpisodicStore"
    assert cast(Any, di.transcript_store)._db_path == config.resolve_transcript_path(
        config.transcript_path
    )
    assert cast(Any, di.episodic_store)._capture_context_log is False


def test_di_loads_builtin_tools_by_default(tmp_path: Path):
    config = _config(tmp_path, "single_agent")

    di = DIContainer(config, MemoryProfile.FULL)
    di.memory = MagicMock()
    di._create_tool_registry()

    assert di.tool_registry is not None
    names = set(di.tool_registry.list_names())
    assert "recall_memory" in names
    assert "store_fact" in names
    assert "web_search" not in names


def test_di_loads_friday_tools_provider_with_category_filter(tmp_path: Path):
    config = _config(tmp_path, "single_agent")
    config.tools_config = ToolsConfig(
        providers=ToolProvidersConfig(
            builtin=ToolProviderConfig(enabled=True),
            friday_tools=ToolProviderConfig(
                enabled=True,
                mode="selected",
                include_categories=("web",),
                include_tools=("file_write",),
            ),
        )
    )

    di = DIContainer(config, MemoryProfile.FULL)
    di.memory = MagicMock()
    di._create_tool_registry()

    assert di.tool_registry is not None
    names = set(di.tool_registry.list_names())
    assert "recall_memory" in names
    assert "web_search" in names
    assert "web_reader" in names
    assert "file_write" in names


def test_di_native_registration_defers_mcp_to_async_boot(tmp_path: Path):
    config = _config(tmp_path, "single_agent")
    config.tools_config = ToolsConfig(
        providers=ToolProvidersConfig(
            builtin=ToolProviderConfig(enabled=True),
            mcp=MCPToolProviderConfig.from_dict(
                {
                    "enabled": True,
                    "mode": "selected",
                    "include_tools": ["mcp_filesystem_read_file"],
                    "config": {
                        "auto_connect": False,
                        "servers": [],
                    },
                }
            ),
        )
    )

    di = DIContainer(config, MemoryProfile.FULL)
    di.memory = MagicMock()

    di._create_tool_registry()
    assert di.tool_registry is not None
    assert "recall_memory" in di.tool_registry.list_names()
    assert di.mcp_provider is None


@pytest.mark.asyncio
async def test_direct_di_missing_include_failure_uses_public_provider_cleanup(
    tmp_path, monkeypatch
):
    config = _config(tmp_path, "single_agent")
    config.tools_config = ToolsConfig.from_dict(
        {
            "providers": {
                "mcp": {
                    "enabled": True,
                    "include_tools": ["mcp_peer_missing"],
                    "config": {"auto_connect": False},
                }
            }
        }
    )
    di = DIContainer(config, MemoryProfile.TESTING)
    for method in (
        "_create_telemetry",
        "_create_llm_services",
        "_create_memory_controller",
        "_create_multi_agent_stack",
        "_create_context_engine",
    ):
        monkeypatch.setattr(di, method, lambda: None)
    monkeypatch.setattr(di, "_create_storage_adapters", AsyncMock())
    try:
        with pytest.raises(ToolProviderLoadError, match="missing_include"):
            await di.boot()
        assert di.mcp_provider is not None
        assert not di.mcp_provider.tool_metadata
        assert not di.mcp_provider.owned_tool_names
        assert di.mcp_provider.registration_registry is None
        assert "missing_include" in di.mcp_provider.diagnostics.codes
        assert not di._booted
    finally:
        await di.shutdown()
