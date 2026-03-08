# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
from pathlib import Path
from unittest.mock import MagicMock

from friday_core.profiles import MemoryProfile
from friday_runtime.config import LLMServiceConfig, RuntimeConfig
from friday_runtime.di import DIContainer


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
    assert di.embeddings.api_key == "reasoning-key"


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
