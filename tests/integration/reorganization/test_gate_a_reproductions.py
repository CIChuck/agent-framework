"""Synthetic Gate A reproductions for the diagnosed reorganization defects."""

from __future__ import annotations

import asyncio
import sqlite3
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import chromadb
import pytest
import yaml
from chromadb.config import Settings
from friday_chat.adapters import FrameworkMaintenanceAdapter
from friday_chat.app import FridayChatApp, ListInputSource, ListOutputSink
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import FakeTranscriptStore, build_runtime
from friday_memory.maintenance import BackupManager
from friday_memory.maintenance.models import PruneReport, ReorganizationReport


@dataclass
class SyntheticSplitLayout:
    """Disposable representation of the configured Friday Chat store layout."""

    root: Path
    vector_directory: Path
    graph_path: Path
    transcript_path: Path
    transcript_wal_path: Path
    access_buffer_wal_path: Path
    recovery_directory: Path
    log_directory: Path
    collection_index_files: tuple[Path, ...]
    transcript_connection: sqlite3.Connection
    chroma_client: Any


@pytest.fixture
def synthetic_split_layout(tmp_path: Path) -> Iterator[SyntheticSplitLayout]:
    root = tmp_path / "runtime" / ".friday"
    vector_directory = root / "vector"
    export_directory = root / "exports"
    graph_path = root / "graph.json"
    transcript_path = export_directory / "friday_transcripts.sqlite"
    access_buffer_wal_path = root / "access-buffer.wal"
    recovery_directory = tmp_path / "operator" / "recovery"
    log_directory = tmp_path / "operator" / "logs"
    vector_directory.mkdir(parents=True)
    export_directory.mkdir(parents=True)
    recovery_directory.mkdir(parents=True)
    log_directory.mkdir(parents=True)

    graph_path.write_text(
        '{"nodes": {"synthetic-node": {"label": "Synthetic"}}, "edges": []}'
    )
    access_buffer_wal_path.write_text("synthetic-access-buffer-entry\n")

    chroma_client = chromadb.PersistentClient(
        path=str(vector_directory),
        settings=Settings(anonymized_telemetry=False),
    )
    for index, name in enumerate(("synthetic-short-term", "synthetic-long-term")):
        collection = chroma_client.create_collection(name)
        embeddings: list[Sequence[float] | Sequence[int]] = [
            [float(index), 0.25, 0.75]
        ]
        collection.add(
            ids=[f"synthetic-{index}"],
            documents=[f"synthetic document {index}"],
            embeddings=embeddings,
        )
    collection_index_files = tuple(
        path
        for path in vector_directory.rglob("*")
        if path.is_file() and path.name != "chroma.sqlite3"
    )
    if not collection_index_files:
        raise RuntimeError("Synthetic Chroma fixture did not create index state.")

    transcript_connection = sqlite3.connect(transcript_path)
    journal_mode = transcript_connection.execute("PRAGMA journal_mode=WAL").fetchone()
    if journal_mode is None or journal_mode[0].lower() != "wal":
        raise RuntimeError("Synthetic transcript fixture did not enter WAL mode.")
    transcript_connection.execute(
        "CREATE TABLE synthetic_entries (id TEXT PRIMARY KEY, body TEXT NOT NULL)"
    )
    transcript_connection.execute(
        "INSERT INTO synthetic_entries VALUES (?, ?)",
        ("synthetic-turn", "synthetic transcript content"),
    )
    transcript_connection.commit()
    transcript_wal_path = Path(f"{transcript_path}-wal")
    if not transcript_wal_path.is_file():
        raise RuntimeError("Synthetic transcript fixture did not retain WAL state.")

    try:
        yield SyntheticSplitLayout(
            root=root,
            vector_directory=vector_directory,
            graph_path=graph_path,
            transcript_path=transcript_path,
            transcript_wal_path=transcript_wal_path,
            access_buffer_wal_path=access_buffer_wal_path,
            recovery_directory=recovery_directory,
            log_directory=log_directory,
            collection_index_files=collection_index_files,
            transcript_connection=transcript_connection,
            chroma_client=chroma_client,
        )
    finally:
        transcript_connection.close()


def test_example_configuration_resolves_to_a_split_layout() -> None:
    raw = yaml.safe_load(Path("packages/friday-chat/config.example.yaml").read_text())
    vector_directory = Path(raw["memory"]["persist_directory"])
    graph_path = vector_directory.with_name("graph.json")
    transcript_path = (
        Path(raw["transcript"]["export_directory"]) / "friday_transcripts.sqlite"
    )

    assert vector_directory == Path(".friday/vector")
    assert graph_path == Path(".friday/graph.json")
    assert transcript_path == Path(".friday/exports/friday_transcripts.sqlite")
    assert len({vector_directory, graph_path, transcript_path}) == 3


def test_synthetic_split_layout_covers_required_store_semantics(
    synthetic_split_layout: SyntheticSplitLayout,
) -> None:
    layout = synthetic_split_layout
    collection_names = {
        collection.name for collection in layout.chroma_client.list_collections()
    }

    assert collection_names == {"synthetic-short-term", "synthetic-long-term"}
    assert len(layout.collection_index_files) >= 2
    assert layout.transcript_wal_path.is_file()
    assert layout.access_buffer_wal_path.is_file()
    assert not layout.recovery_directory.is_relative_to(layout.root)
    assert not layout.log_directory.is_relative_to(layout.root)


def test_vector_root_backup_reproduces_incomplete_split_layout_capture(
    synthetic_split_layout: SyntheticSplitLayout,
) -> None:
    layout = synthetic_split_layout
    manager = BackupManager(
        layout.vector_directory,
        backup_root=layout.recovery_directory,
    )

    manifest = manager.create_backup(layout.recovery_directory / "baseline")

    backed_up_sources = {Path(path).resolve() for path in manifest.files}
    assert manifest.store_stats["vector"]["exists"] is True
    assert manifest.store_stats["graph"]["exists"] is False
    assert manifest.store_stats["episodic"]["exists"] is False
    assert layout.graph_path.resolve() not in backed_up_sources
    assert layout.transcript_path.resolve() not in backed_up_sources
    assert layout.transcript_wal_path.resolve() not in backed_up_sources
    assert layout.access_buffer_wal_path.resolve() not in backed_up_sources
    assert not any(
        path.resolve() in backed_up_sources for path in layout.collection_index_files
    )


async def test_production_adapter_reproduces_full_dispatch_and_fake_only_counts(
    synthetic_split_layout: SyntheticSplitLayout,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    layout = synthetic_split_layout
    calls: list[str] = []
    adapter_vector_directory = layout.root / "adapter-vector"
    adapter_vector_directory.mkdir()

    class RecordingReorganizer:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        async def reorganize(self, **_kwargs: object) -> ReorganizationReport:
            calls.append("full-reorganize")
            return ReorganizationReport(
                memory_dir=str(adapter_vector_directory),
                prune_report=PruneReport(
                    dry_run=True,
                    insights_removed=4,
                    entities_removed=3,
                ),
                success=True,
            )

    monkeypatch.setattr(
        "friday_chat.adapters.MemoryReorganizer",
        RecordingReorganizer,
    )
    runtime = build_runtime(
        FridayChatConfig.model_validate(
            {
                "llm": {"model": "openai/synthetic-chat-model"},
                "embedding": {"model": "openai/synthetic-embedding-model"},
                "memory": {"persist_directory": str(adapter_vector_directory)},
                "transcript": {"export_directory": str(layout.transcript_path.parent)},
                "maintenance": {
                    "backup_directory": str(layout.recovery_directory),
                    "logging": {
                        "enabled": False,
                        "log_directory": str(layout.log_directory),
                    },
                },
                "tools": {"registry": []},
            }
        ),
        fake=False,
        session_id="synthetic-session",
    )
    assert isinstance(runtime.maintenance, FrameworkMaintenanceAdapter)

    result = await runtime.maintenance.reorganize(
        mode="dedupe",
        dry_run=True,
        backup_first=True,
    )

    assert calls == ["full-reorganize"]
    assert result["mode"] == "dedupe"
    assert result["scanned"] == 0
    assert result["changed"] == 0


async def test_shutdown_coordinator_drains_and_finalizes_before_contained_exit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = build_runtime(
        FridayChatConfig.model_validate(
            {
                "llm": {"model": "openai/synthetic-chat-model"},
                "session": {
                    "flush_on_exit": False,
                    "lifecycle_on_exit": False,
                    "reorganize_on_exit": True,
                },
            }
        )
    )
    app = FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource([]),
        output_sink=ListOutputSink(),
    )
    release = asyncio.Event()
    started = asyncio.Event()
    events: list[str] = []

    async def pending_writer() -> None:
        started.set()
        try:
            await release.wait()
        finally:
            events.append("background_drained")

    pending_task = app.background.create_task(pending_writer())
    await started.wait()
    transcript = runtime.transcript
    assert isinstance(transcript, FakeTranscriptStore)
    original_finalize = transcript.finalize

    async def observe_finalize() -> None:
        assert app.background.closed is True
        assert app.background.pending_count == 0
        assert pending_task.done()
        events.append("transcript_finalize")
        await original_finalize()

    async def unexpected_execute(*_args: object, **_kwargs: object) -> None:
        events.append("exit_execute_attempted")
        raise AssertionError("contained exit must not reach snapshot or execution")

    monkeypatch.setattr(transcript, "finalize", observe_finalize)
    monkeypatch.setattr(
        app.reorganization_coordinator,
        "_execute_locked",
        unexpected_execute,
    )

    assert app.reorganization_coordinator.execution_configured is False

    result = await app.run()

    assert events == ["background_drained", "transcript_finalize"]
    assert result.maintenance_actions[-1] == "reorganize_skipped:execute_disabled"
    assert app.background.closed is True
    assert app.background.pending_count == 0
    assert pending_task.cancelled()
    assert transcript.finalized is True
