"""Resolve one production reorganization layout before adapter construction."""

from __future__ import annotations

from pathlib import Path

from friday_chat.config import FridayChatConfig
from friday_chat.reorganization.contracts import (
    OperationTrigger,
    ReorganizationMode,
    ReorganizationRequest,
)
from friday_chat.reorganization.layout import FridayChatMaintenanceLayout


class ExitReorganizationModeError(ValueError):
    """Raised when legacy exit configuration cannot be mapped safely."""


def resolve_maintenance_layout(
    config: FridayChatConfig,
    *,
    captured_process_cwd: Path,
) -> FridayChatMaintenanceLayout:
    """Resolve every live and external path from one captured process cwd."""
    vector = Path(config.memory.persist_directory or ".friday/vector")
    vector_parent = vector.parent
    graph = vector.with_name("graph.json")
    transcript_export = Path(config.transcript.export_directory or "./exports")
    transcript = transcript_export / "friday_transcripts.sqlite"
    access_wal_value = config.lifecycle.access_buffer.get("wal_path")
    access_wal = (
        Path(access_wal_value)
        if isinstance(access_wal_value, str) and access_wal_value
        else None
    )
    recovery = Path(
        config.maintenance.backup_directory or vector_parent / "recovery"
    )
    configured_log = config.maintenance.logging.get("log_directory")
    logs = (
        Path(configured_log)
        if isinstance(configured_log, str) and configured_log
        else vector_parent / "reorganization_logs"
    )
    return FridayChatMaintenanceLayout.resolve_once(
        captured_process_cwd=captured_process_cwd,
        vector_directory=vector,
        graph_path=graph,
        access_buffer_wal_path=access_wal,
        transcript_database_path=transcript,
        recovery_root=recovery,
        log_root=logs,
    )


def build_exit_reorganization_request(
    config: FridayChatConfig,
) -> ReorganizationRequest | None:
    """Adapt only the two established exit-mode spellings to typed requests."""
    if not config.session.reorganize_on_exit:
        return None
    mode = config.session.reorganize_mode
    if mode == "fast":
        return ReorganizationRequest(
            trigger=OperationTrigger.SHUTDOWN,
            mode=ReorganizationMode.FULL,
            execute=True,
            skip_synthesis=True,
            skip_verify=True,
        )
    if mode in {"full", "deep"}:
        return ReorganizationRequest(
            trigger=OperationTrigger.SHUTDOWN,
            mode=ReorganizationMode.FULL,
            execute=True,
        )
    raise ExitReorganizationModeError(
        "session.reorganize_mode must be exactly 'fast', 'full', or 'deep'"
    )


__all__ = [
    "ExitReorganizationModeError",
    "build_exit_reorganization_request",
    "resolve_maintenance_layout",
]
