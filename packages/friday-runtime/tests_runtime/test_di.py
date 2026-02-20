from pathlib import Path
from unittest.mock import MagicMock

from friday_core.profiles import MemoryProfile
from friday_runtime.config import RuntimeConfig
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
