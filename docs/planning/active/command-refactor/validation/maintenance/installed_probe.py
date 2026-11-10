"""MAINT installed-artifact proof; export supplies data/program oracles only."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib
import importlib.metadata as metadata
import json
import os
import runpy
import stat
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path


def require(value: object, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(
    source: Path, package: str, distribution: str, prefix: Path
) -> dict[str, object]:
    root = Path(metadata.distribution(distribution).locate_file(package)).resolve()
    require(
        root.is_relative_to(prefix), "package root escaped installed prefix: " + package
    )
    expected_root = source / "packages" / distribution / "src" / package
    expected = {
        str(p.relative_to(expected_root)): sha(p)
        for p in expected_root.rglob("*")
        if p.is_file()
    }
    expected_dirs = {
        str(p.relative_to(expected_root))
        for p in expected_root.rglob("*")
        if p.is_dir()
    }
    actual = {}
    actual_dirs = set()
    for path in root.rglob("*"):
        info = path.lstat()
        relative = str(path.relative_to(root))
        require(
            not stat.S_ISLNK(info.st_mode),
            "package contains symlink: " + package + "/" + relative,
        )
        if stat.S_ISDIR(info.st_mode):
            actual_dirs.add(relative)
        else:
            require(
                stat.S_ISREG(info.st_mode),
                "package contains non-file: " + package + "/" + relative,
            )
            require(
                not info.st_mode & 0o111,
                "package contains executable data: " + package + "/" + relative,
            )
            actual[relative] = sha(path)
    require(
        actual_dirs == expected_dirs,
        "installed directory inventory changed: " + package,
    )
    require(
        set(actual) == set(expected), "installed member inventory changed: " + package
    )
    require(actual == expected, "installed member bytes changed: " + package)
    return {
        "root": str(root),
        "members": len(actual),
        "sha256": hashlib.sha256(
            json.dumps(actual, sort_keys=True).encode()
        ).hexdigest(),
    }


def origins(inventories: dict[str, dict[str, object]]) -> int:
    count = 0
    for name, module in tuple(sys.modules.items()):
        package = name.partition(".")[0]
        if package not in inventories or module is None:
            continue
        root = Path(str(inventories[package]["root"]))
        file = getattr(module, "__file__", None)
        spec = getattr(module, "__spec__", None)
        require(
            isinstance(file, str) and Path(file).resolve().is_relative_to(root),
            "module origin escaped inventoried root: " + name,
        )
        origin = getattr(spec, "origin", None)
        require(
            isinstance(origin, str) and Path(origin).resolve() == Path(file).resolve(),
            "module spec origin mismatch: " + name,
        )
        locations = getattr(spec, "submodule_search_locations", None)
        if locations is not None:
            require(
                len(locations) == 1
                and all(Path(x).resolve().is_relative_to(root) for x in locations),
                "module search path escaped inventoried root: " + name,
            )
        count += 1
    return count


def normalize_approved_help(value: object) -> object:
    old_flags = [
        "--backup",
        "--dedupe",
        "--analyze",
        "--prune",
        "--synthesize",
        "--verify",
    ]
    if isinstance(value, dict):
        return {k: normalize_approved_help(v) for k, v in value.items()}
    if isinstance(value, list):
        return (
            ["--full", *old_flags]
            if value == old_flags
            else [normalize_approved_help(v) for v in value]
        )
    if isinstance(value, str):
        return (
            value.replace(
                "[" + "|".join(old_flags) + "]", "[--full|" + "|".join(old_flags) + "]"
            )
            .replace(
                "Run one reorganization step instead of the full operation.",
                "Choose explicit full mode or one reorganization step.",
            )
            .replace(", ".join(old_flags), ", ".join(["--full", *old_flags]))
        )
    return value


async def chat_flow(helper: dict, root: Path, *, fail: bool) -> dict[str, object]:
    import chromadb
    from friday_chat.commands.registry import (
        _format_reorganization_result,
        _parse_reorganize_invocation,
    )
    from friday_chat.reorganization.contracts import (
        MaintenanceRunEvidence,
        MutationStep,
        OperationTrigger,
        ReorganizationMode,
        ReorganizationRequest,
        ResultStatus,
    )
    from friday_chat.reorganization.coordinator import (
        CoordinatorFaultPoint,
        ManualMaintenanceDrainResult,
        ManualMaintenanceResumeResult,
        ReorganizationCoordinator,
    )
    from friday_chat.reorganization.gate import MaintenanceAdmissionGate
    from friday_chat.reorganization.layout import FridayChatMaintenanceLayout
    from friday_chat.reorganization.lease import DarwinLayoutLeaseRegistry
    from friday_chat.reorganization.mutation import FrameworkMaintenanceMutationAdapter
    from friday_memory.maintenance.recovery import MemoryMaintenanceParticipant
    from friday_transcript import (
        SQLiteTranscriptStore,
        TranscriptEntry,
        TranscriptSession,
    )

    (
        pipeline,
        providers,
        embedding,
        lifecycle,
        collection,
        graph,
        memory_layout,
    ) = await helper["setup"](root)
    transcript = SQLiteTranscriptStore(root / "transcript.sqlite")
    require(
        await transcript.create_session(
            TranscriptSession(session_id="installed", model_name="synthetic")
        ),
        "transcript setup failed",
    )
    require(
        await transcript.append_entry(
            TranscriptEntry(
                id="entry",
                session_id="installed",
                turn_number=1,
                user_message="synthetic",
                assistant_message="synthetic",
            )
        ),
        "transcript entry setup failed",
    )
    layout = FridayChatMaintenanceLayout.resolve_once(
        captured_process_cwd=root,
        vector_directory=memory_layout.vector_directory,
        graph_path=memory_layout.graph_path,
        access_buffer_wal_path=None,
        transcript_database_path=root / "transcript.sqlite",
        recovery_root=memory_layout.recovery_directory,
        log_root=memory_layout.log_directory,
    )

    class Hooks:
        async def prepare_for_manual_maintenance(self):
            pass

        async def drain_for_manual_maintenance(self):
            return ManualMaintenanceDrainResult()

        def resume_after_manual_maintenance(self):
            return ManualMaintenanceResumeResult()

        async def close_for_shutdown(self, *, snapshot_requested):
            pass

        async def finalize_transcript(self):
            pass

    adapter = FrameworkMaintenanceMutationAdapter(
        pipeline.memory, pipeline.providers, lifecycle
    )
    original = adapter.execute_pipeline
    calls = []

    async def execute(request, *, run_id, observer, boundary):
        calls.append((request, run_id))
        return await original(
            request, run_id=run_id, observer=observer, boundary=boundary
        )

    adapter.execute_pipeline = execute

    async def fault(point, stage):
        if (
            fail
            and point is CoordinatorFaultPoint.AFTER_MUTATION_STEP
            and stage is MutationStep.VERIFY_GENERATED
        ):
            raise RuntimeError("synthetic installed fault after generated verification")

    coordinator = ReorganizationCoordinator(
        layout=layout,
        gate=MaintenanceAdmissionGate(),
        memory_participant=MemoryMaintenanceParticipant(
            memory_layout, graph_store=graph
        ),
        transcript_participant=transcript,
        runtime_hooks=Hooks(),
        mutation_adapter=adapter,
        lease_registry=DarwinLayoutLeaseRegistry(
            namespace_root=root / "leases",
            platform_name="Darwin",
            host_id="installed-maint",
        ),
        application_version="installed-proof",
        fault_injector=fault,
    )
    before = collection.get(include=["documents", "metadatas"])
    result = await coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL, mode=ReorganizationMode.FULL, execute=True
        )
    )
    require(
        len(calls) == 1 and calls[0][1] == result.run_id,
        "Chat did not delegate exactly once with run identity",
    )
    require(
        _parse_reorganize_invocation(("--execute",))
        == _parse_reorganize_invocation(("--full", "--execute")),
        "explicit full changed admission",
    )
    text = _format_reorganization_result(result, dry_run=False)
    if fail:
        require(
            result.status is ResultStatus.FAILED_ROLLED_BACK,
            "installed failure did not roll back",
        )
        fresh = (
            chromadb.PersistentClient(path=str(layout.vector_directory))
            .get_collection("headless")
            .get(include=["documents", "metadatas"])
        )

        def rows(value):
            return {
                i: (d, m)
                for i, d, m in zip(
                    value["ids"], value["documents"], value["metadatas"], strict=True
                )
            }

        require(
            rows(fresh) == rows(before),
            "Chat rollback retained verdict changes or generated records",
        )
        require(
            "attempted; rolled back" in text,
            "rolled-back verdicts presented as retained",
        )
    else:
        require(
            result.status
            in {ResultStatus.COMPLETED, ResultStatus.COMPLETED_WITH_WARNINGS},
            "installed Chat flow failed",
        )
        require(
            [r.step.value for r in result.mutation_steps]
            == [
                "dedupe",
                "prune",
                "verify_pending",
                "synthesize",
                "verify_generated",
                "lifecycle",
            ],
            "Chat stage order changed",
        )
        require(
            result.mutation_steps[2].verification_counts.selected == 5
            and result.mutation_steps[4].verification_counts.selected == 1,
            "Chat did not consume shared verdict facts",
        )
        require(
            "selected=5; verified=4; rejected=0; uncertain=1" in text
            and "selected=1; verified=1; rejected=0; uncertain=0" in text,
            "visible stage verdicts changed",
        )
    evidence = [
        MaintenanceRunEvidence.model_validate_json(p.read_bytes())
        for p in sorted(
            (layout.recovery_root / result.run_id / "evidence").glob("*.json")
        )
    ]
    for stage in result.mutation_steps:
        if stage.step not in {
            MutationStep.VERIFY_PENDING,
            MutationStep.VERIFY_GENERATED,
        }:
            continue
        planned = [
            e
            for e in evidence
            if e.state == "planned" and e.receipt.stage.value == stage.step.value
        ]
        terminal = [
            e
            for e in evidence
            if e.state == "completed" and e.receipt.stage.value == stage.step.value
        ]
        require(
            len(planned) == len(terminal) == 1
            and planned[0].receipt == terminal[0].receipt == stage.receipt,
            "durable scope evidence differs from shared result",
        )
    require(
        await transcript.count_entries("installed") == 1, "Chat flow changed transcript"
    )
    return {
        "status": result.status.value,
        "calls": len(calls),
        "evidence_events": len(evidence),
        "stages": [r.step.value for r in result.mutation_steps],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["source", "prepared", "profile", "report"]:
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--lane", choices=["neutral", "chat"], required=True)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    prepared = args.prepared.resolve()
    report = args.report.resolve()
    prefix = Path(sys.prefix).resolve()
    require(not report.exists(), "probe refuses to overwrite report")
    require(
        not prefix.is_relative_to(source), "installed prefix cannot be source export"
    )
    # Isolated interpreters ignore PYTHONPATH; explicitly install the pinned audit guard.
    sys.path.insert(0, str(prepared))
    runpy.run_path(str(prepared / "sitecustomize.py"), run_name="maint_guard")
    require("pilot_guard" in sys.modules, "audit guard was not installed")
    profile = {}
    for line in args.profile.read_text().splitlines():
        if "==" not in line or line[:1].isspace():
            continue
        name, _, version = line.partition("==")
        profile[name.lower().replace("_", "-")] = version.rstrip(" \\")
    actual = {
        d.metadata["Name"].lower().replace("_", "-"): d.version
        for d in metadata.distributions()
    }
    require(
        actual == profile,
        "installed distribution closure differs from recorded profile",
    )
    bundle = json.loads((args.profile.parent / "bundle-report.json").read_text())
    require(
        bundle["revision"] == args.revision, "probe revision is not artifact source"
    )
    inventories = {
        "friday_commands": inventory(
            source, "friday_commands", "friday-commands", prefix
        )
    }
    import friday_commands

    require(len(friday_commands.__all__) == 54, "retained Commands API changed")
    details = {
        "lane": args.lane,
        "revision": args.revision,
        "prefix": str(prefix),
        "optimized": sys.flags.optimize,
        "closure": len(actual),
    }
    if args.lane == "neutral":
        require(set(actual) == {"friday-commands"}, "neutral closure expanded")
        require(
            importlib.util.find_spec("friday_memory") is None,
            "neutral closure gained Memory",
        )
        require(
            importlib.util.find_spec("friday_chat") is None,
            "neutral closure gained Chat",
        )
    else:
        for package, distribution in [
            ("friday_memory", "friday-memory"),
            ("friday_chat", "friday-chat"),
        ]:
            inventories[package] = inventory(source, package, distribution, prefix)
        helper_path = (
            source / "tests/integration/reorganization/test_maintenance_headless.py"
        )
        helper_copy = report.parent / "headless-proof-program.py"
        if helper_copy.exists():
            require(
                sha(helper_copy) == sha(helper_path), "copied proof program drifted"
            )
        else:
            helper_copy.write_bytes(helper_path.read_bytes())
        helper = runpy.run_path(str(helper_copy), run_name="maint_headless_proof")
        vectors = (
            source
            / "packages/friday-memory/tests_memory/test_maintenance/fixtures/selection-digest-vectors.json"
        )
        work = report.parent / (report.stem + "-stores")
        work.mkdir()
        details["headless"] = asyncio.run(
            helper["run_flow"](work / "headless", vectors)
        )
        details["force_reembed"] = asyncio.run(
            helper["run_flow"](work / "reembed", vectors, force_reembed=True)
        )
        details["migration_only"] = asyncio.run(
            helper["migration_only_flow"](work / "migration")
        )
        details["cancellation"] = [
            asyncio.run(
                helper["cancellation_restore_flow"](
                    work / ("cancel-" + str(injected)), injected=injected
                )
            )
            for injected in [False, True]
        ]
        require(
            not any(
                n == "friday_chat" or n.startswith("friday_chat.") for n in sys.modules
            ),
            "Chat imported in headless installed proof",
        )
        details["chat"] = asyncio.run(chat_flow(helper, work / "chat", fail=False))
        details["rollback"] = asyncio.run(
            chat_flow(helper, work / "rollback", fail=True)
        )
        fixtures = source / "packages/friday-chat/tests_chat/fixtures/maintenance-v1"
        details["v1"] = [
            asyncio.run(
                helper["recover_v1_fixture"](fixtures, work / ("v1-" + kind), kind)
            )
            for kind in ["completed", "interrupted"]
        ]
        from friday_chat.commands.registry import build_default_registry

        oracle = json.loads(
            (
                source
                / "docs/planning/active/command-refactor/validation/pilot/baseline.json"
            ).read_text()
        )["observations"]
        registry = build_default_registry()
        current = json.loads(
            json.dumps(
                {name: asdict(value) for name, value in registry.commands.items()}
            )
        )
        require(
            current == normalize_approved_help(oracle["metadata"]),
            "metadata changed outside approved reorganize cells",
        )
        for row in oracle["help"]:
            require(
                registry.render_help(row["focus"])
                == normalize_approved_help(row["output"]),
                "help changed outside approved reorganize cells",
            )
        launcher = prefix / "bin/friday-chat"
        child = subprocess.run(
            [str(launcher), "--help"],
            capture_output=True,
            text=True,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
        )
        require(
            child.returncode == 0 and "Usage" in child.stdout,
            "installed entry-point child failed",
        )
        details["entrypoint_help"] = True
    details["module_origins"] = origins(inventories)
    for package in inventories:
        distribution = package.replace("_", "-")
        require(
            inventory(source, package, distribution, prefix) == inventories[package],
            "installed package drifted during probe",
        )
    details.update(
        status="passed", inventories=inventories, probe_sha256=sha(Path(__file__))
    )
    report.write_text(json.dumps(details, indent=2) + "\n")
    print(
        json.dumps(
            {
                "status": "passed",
                "lane": args.lane,
                "optimized": sys.flags.optimize,
                "report": str(report),
            }
        )
    )


if __name__ == "__main__":
    main()
