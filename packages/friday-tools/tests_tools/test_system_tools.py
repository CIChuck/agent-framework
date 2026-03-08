# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
from unittest.mock import MagicMock, patch

import pytest

from friday_tools.system.health import SystemHealthTool


@pytest.fixture
def mock_psutil():
    with patch("friday_tools.system.health.psutil") as m:
        # Mock CPU
        m.cpu_percent.return_value = 15.5

        # Mock Memory
        mem_mock = MagicMock()
        mem_mock.total = 16 * (1024**3)
        mem_mock.available = 8 * (1024**3)
        mem_mock.percent = 50.0
        m.virtual_memory.return_value = mem_mock

        # Mock Disk
        disk_mock = MagicMock()
        disk_mock.total = 100 * (1024**3)
        disk_mock.free = 40 * (1024**3)
        disk_mock.percent = 60.0
        m.disk_usage.return_value = disk_mock

        yield m


@pytest.mark.asyncio
async def test_system_health_tool(mock_psutil):
    tool = SystemHealthTool()

    # Run without disk
    result = await tool.run(SystemHealthTool.Input(check_disk=False))

    assert "CPU Usage: 15.5%" in result.content
    assert result.data["memory"]["percent"] == 50.0
    assert result.data["disk"] == {}

    mock_psutil.disk_usage.assert_not_called()


@pytest.mark.asyncio
async def test_system_health_tool_with_disk(mock_psutil):
    tool = SystemHealthTool()

    # Run with disk
    result = await tool.run(SystemHealthTool.Input(check_disk=True))

    assert "Disk: 60.0%" in result.content
    assert result.data["disk"]["percent"] == 60.0
    mock_psutil.disk_usage.assert_called_once()


# --- Transcript Tool Tests ---


from friday_transcript import SQLiteTranscriptStore  # noqa: E402

from friday_tools.system.transcript import TranscriptTool  # noqa: E402


@pytest.fixture
def mock_transcript_store():
    return MagicMock(spec=SQLiteTranscriptStore)


@pytest.mark.asyncio
async def test_transcript_tool(mock_transcript_store, tmp_path):
    tool = TranscriptTool(mock_transcript_store)

    # Test export session (mocking the exporter would be better, but we trust the tool logic just calls it)  # noqa: E501
    # Since we can't easily mock the Exporter classes initialized INSIDE the run method without patching,  # noqa: E501
    # we will just test validation logic here.

    # Missing session_id
    res = await tool.run(TranscriptTool.Input(action="export_session", format="jsonl"))
    assert res.error == "Missing session_id"

    # Invalid format
    res2 = await tool.run(
        TranscriptTool.Input(action="export_session", session_id="123", format="xml")
    )
    assert res2.error == "Invalid format"
