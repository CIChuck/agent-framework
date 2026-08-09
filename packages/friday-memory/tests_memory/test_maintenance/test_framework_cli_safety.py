"""Fail-closed coverage for the standalone Friday Memory maintenance CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from friday_memory.maintenance import __main__ as maintenance_cli


def _parse(*args: str) -> argparse.Namespace:
    return maintenance_cli.create_parser().parse_args(args)


def test_standalone_command_inventory_is_explicit() -> None:
    parser = maintenance_cli.create_parser()

    for command in (
        "backup",
        "restore",
        "list",
        "analyze",
        "prune",
        "synthesize",
        "classify",
        "verify",
        "reorganize",
    ):
        parsed = parser.parse_args([command, "--dir", "/synthetic/memory"])
        assert parsed.command == command


@pytest.mark.parametrize(
    "command",
    ("prune", "synthesize", "verify", "reorganize"),
)
def test_mutating_option_help_advertises_fail_closed_status(
    command: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exit_info:
        maintenance_cli.create_parser().parse_args([command, "--help"])

    output = capsys.readouterr().out
    normalized_output = " ".join(output.split())
    assert exit_info.value.code == 0
    assert "--no-dry-run" in output
    assert "currently rejected; use Friday Chat" in normalized_output
    if command == "reorganize":
        assert "Legacy backup bypass" in normalized_output
        assert "recovery bundles are mandatory" in normalized_output
        assert "dangerous" not in output


@pytest.mark.parametrize(
    ("arguments", "expected_path"),
    (
        (("restore", "--dir", "/synthetic/memory"), "restore command"),
        (
            ("prune", "--dir", "/synthetic/memory", "--no-dry-run"),
            "prune mutation path",
        ),
        (
            ("synthesize", "--dir", "/synthetic/memory", "--no-dry-run"),
            "synthesize mutation path",
        ),
        (
            ("verify", "--dir", "/synthetic/memory", "--no-dry-run"),
            "verify mutation path",
        ),
        (
            ("reorganize", "--dir", "/synthetic/memory", "--no-dry-run"),
            "reorganize mutation path",
        ),
    ),
)
async def test_standalone_mutation_and_restore_paths_fail_closed(
    arguments: tuple[str, ...],
    expected_path: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "argv", ["friday-memory-maintenance", *arguments])

    result = await maintenance_cli.main()

    output = capsys.readouterr().out
    assert result == 2
    assert "FAIL-CLOSED:" in output
    assert expected_path in output
    assert "Friday Chat" in output


async def test_standalone_reorganize_rejects_backup_bypass(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "friday-memory-maintenance",
            "reorganize",
            "--dir",
            "/synthetic/memory",
            "--no-backup",
        ],
    )

    result = await maintenance_cli.main()

    output = capsys.readouterr().out
    assert result == 2
    assert "--no-backup is rejected" in output
    assert "verified recovery bundle" in output


async def test_memory_only_backup_is_labeled_incomplete_for_chat_recovery(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    memory_directory = tmp_path / "synthetic-memory"
    memory_directory.mkdir()
    (memory_directory / "graph.json").write_text('{"nodes": {}, "edges": []}')
    output_directory = tmp_path / "external-recovery" / "memory-only"

    result = await maintenance_cli.cmd_backup(
        _parse(
            "backup",
            "--dir",
            str(memory_directory),
            "--output",
            str(output_directory),
        )
    )

    output = capsys.readouterr().out
    assert result == 0
    assert "memory-only file backup" in output
    assert "not a complete Friday Chat recovery bundle" in output
    assert (output_directory / "manifest.json").is_file()


async def test_list_remains_read_only(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    memory_directory = tmp_path / "synthetic-memory"
    memory_directory.mkdir()

    result = await maintenance_cli.cmd_list(
        _parse("list", "--dir", str(memory_directory))
    )

    assert result == 0
    assert "No backups found" in capsys.readouterr().out
    assert list(memory_directory.iterdir()) == []


async def test_analyze_and_all_dry_run_paths_remain_available(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, bool]] = []

    class Analyzer:
        def __init__(self, _directory: str, _config: object) -> None:
            pass

        async def analyze(self) -> object:
            calls.append(("analyze", True))
            return object()

        def generate_report_summary(self, _report: object) -> str:
            return "synthetic analysis"

    class Pruner:
        def __init__(self, _directory: str, _config: object) -> None:
            pass

        async def prune(self, *, dry_run: bool) -> object:
            calls.append(("prune", dry_run))
            return object()

        def generate_report_summary(self, _report: object) -> str:
            return "synthetic prune"

    class Synthesizer:
        def __init__(self, _directory: str, *, llm_service: object) -> None:
            pass

        async def synthesize(self, *, dry_run: bool) -> object:
            calls.append(("synthesize", dry_run))
            return object()

        def generate_report_summary(self, _report: object) -> str:
            return "synthetic synthesis"

    class FactChecker:
        def __init__(self, _directory: str, **_kwargs: Any) -> None:
            pass

        async def classify_facts(
            self,
            *,
            limit: int,
            dry_run: bool,
        ) -> list[object]:
            assert limit == 7
            calls.append(("classify", dry_run))
            return []

        async def run_full_check(self, *, dry_run: bool) -> object:
            calls.append(("verify", dry_run))
            return object()

        def generate_report_summary(self, _report: object) -> str:
            return "synthetic verification"

    class Reorganizer:
        def __init__(self, _directory: str, *, llm_service: object) -> None:
            pass

        async def reorganize(self, **kwargs: Any) -> object:
            calls.append(("reorganize", bool(kwargs["dry_run"])))
            assert kwargs["backup_first"] is True
            return SimpleNamespace(success=True)

        def generate_report_summary(self, _report: object) -> str:
            return "synthetic reorganization"

    import friday_memory.maintenance.analyzer as analyzer_module
    import friday_memory.maintenance.fact_checker as fact_checker_module
    import friday_memory.maintenance.pruner as pruner_module
    import friday_memory.maintenance.reorganizer as reorganizer_module
    import friday_memory.maintenance.synthesizer as synthesizer_module

    monkeypatch.setattr(analyzer_module, "ConsistencyAnalyzer", Analyzer)
    monkeypatch.setattr(pruner_module, "RedundancyPruner", Pruner)
    monkeypatch.setattr(synthesizer_module, "MemorySynthesizer", Synthesizer)
    monkeypatch.setattr(fact_checker_module, "FactChecker", FactChecker)
    monkeypatch.setattr(reorganizer_module, "MemoryReorganizer", Reorganizer)
    monkeypatch.setattr(maintenance_cli, "get_llm_service", lambda _args: object())

    directory = str(tmp_path / "synthetic-memory")
    assert await maintenance_cli.cmd_analyze(_parse("analyze", "--dir", directory)) == 0
    assert (
        await maintenance_cli.cmd_prune(
            _parse("prune", "--dir", directory, "--backup-first")
        )
        == 0
    )
    assert (
        await maintenance_cli.cmd_synthesize(
            _parse("synthesize", "--dir", directory, "--backup-first")
        )
        == 0
    )
    assert (
        await maintenance_cli.cmd_classify(
            _parse("classify", "--dir", directory, "--limit", "7")
        )
        == 0
    )
    assert await maintenance_cli.cmd_verify(_parse("verify", "--dir", directory)) == 0
    assert (
        await maintenance_cli.cmd_reorganize(_parse("reorganize", "--dir", directory))
        == 0
    )

    assert calls == [
        ("analyze", True),
        ("prune", True),
        ("synthesize", True),
        ("classify", True),
        ("verify", True),
        ("reorganize", True),
    ]
