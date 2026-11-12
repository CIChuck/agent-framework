"""Offline controls/input preparation. Actual upstream adapters remain unqualified."""

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
import unittest
from pathlib import Path

from ingest.config import Config
from ingest.ledger import ZERO, Ledger
from ingest.manifests import canonical, decode, digest, object_value, read, require
from ingest.paths import physical
from ingest.reports import report


def _bound(config: Config) -> Ledger:
    path = config.layout.destination("config/control.json")
    require(
        path.is_file() and read(path) == config.record(),
        "Immutable run configuration changed",
    )
    ledger = Ledger(config.layout.destination("state"))
    records = ledger.records()
    require(bool(records), "Missing run ledger")
    require(
        records[0]["payload"]
        == {
            "run_id": config.layout.run_id,
            "config_sha256": digest(canonical(config.record())),
            "harness_sha256": config.harness_sha256,
        },
        "Run identity mismatch",
    )
    return ledger


def _stop(ledger: Ledger) -> None:
    destination = ledger.state / "stop.json"
    if destination.exists():
        read(destination)
        return
    temporary = ledger.state / ("stop-" + str(os.getpid()) + ".tmp")
    with temporary.open("xb") as target:
        target.write(
            canonical(
                {
                    "schema": 1,
                    "reason": "operator_stop",
                    "effect_resume": "new_run_required",
                }
            )
        )
        target.flush()
        os.fsync(target.fileno())
    temporary.replace(destination)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=[
            "preflight",
            "init",
            "selftest",
            "run",
            "promote",
            "prepare-model",
            "prepare-fixtures",
            "stop",
            "report",
        ],
    )
    parser.add_argument("--harness-manifest", required=True, type=Path)
    parser.add_argument("--harness-manifest-sha256", required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--config-sha256")
    parser.add_argument("--scratch", type=Path)
    parser.add_argument("--profile", choices=["minimal"], default="minimal")
    parser.add_argument(
        "--stage", choices=["all", "A0", "A1", "A2", "A3", "A4"], default="all"
    )
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--window-receipt", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--sha256")
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--model-profile", type=Path)
    parser.add_argument("--reason", choices=["operator_stop"], default="operator_stop")
    args = parser.parse_args(argv)
    require(
        digest(args.harness_manifest.read_bytes()) == args.harness_manifest_sha256,
        "Harness manifest changed after bootstrap",
    )
    if args.command == "selftest":
        require(
            args.scratch is not None and args.scratch.is_dir(),
            "Explicit existing private C0 scratch required",
        )
        from ingest.startup import Guard, guarded, harness_state

        ROOT, BUFFERS = harness_state()
        scratch = physical(args.scratch)
        require(
            scratch == args.scratch and not any(scratch.iterdir()),
            "C0 scratch must be canonical, owned and empty",
        )
        require(
            not (
                {".git", ".venv", ".friday", ".friday-old", "exports"}
                & set(scratch.parts)
            ),
            "Protected scratch destination refused",
        )
        require(
            scratch != ROOT
            and scratch not in ROOT.parents
            and ROOT not in scratch.parents,
            "Scratch/harness overlap refused",
        )
        from ingest import tests as test_package

        test_package.__dict__.update(SCRATCH=args.scratch.resolve(), SOURCE=ROOT)
        stdlib = Path(sys.base_prefix).resolve() / "lib"
        policy = Guard(
            (ROOT, stdlib, Path(sys.executable).resolve(), Path("/usr/bin/git")),
            (args.scratch.resolve(),),
            python=sys.executable,
            native_git="/usr/bin/git",
            native_fixture_writes=True,
            python_scripts=tuple(
                (str(ROOT / name), digest(BUFFERS[name]))
                for name in ("bootstrap.py", "run.py")
            ),
        )
        expected_tests = {
            "test_startup.py",
            "test_paths.py",
            "test_environment.py",
            "test_manifests.py",
            "test_ledger.py",
            "test_export.py",
            "test_protection.py",
            "test_window.py",
            "test_fixtures.py",
            "test_cli.py",
            "test_reports.py",
            "test_behavior.py",
            "test_e2e.py",
            "test_large_documents.py",
        }
        require(
            {
                Path(name).name
                for name in BUFFERS
                if name.startswith("tests/") and name.endswith(".py")
            }
            == expected_tests,
            "C0 test selection is incomplete/unknown",
        )
        with guarded(policy):
            suite = unittest.TestSuite()
            for name in sorted(BUFFERS):
                if name.startswith("tests/test_") and name.endswith(".py"):
                    module = importlib.import_module(
                        "ingest." + name[:-3].replace("/", ".")
                    )
                    suite.addTests(
                        unittest.defaultTestLoader.loadTestsFromModule(module)
                    )
            result = unittest.TextTestRunner(verbosity=2).run(suite)
        print(
            json.dumps(
                {
                    "status": "PASS" if result.wasSuccessful() else "FAIL",
                    "scope": "offline controls and synthetic input preparation only",
                    "cases": result.testsRun,
                    "optimized": bool(sys.flags.optimize),
                    "upstream_qualified": False,
                }
            )
        )
        return 0 if result.wasSuccessful() else 1
    require(
        args.config is not None and args.config_sha256 is not None,
        "Exact approved config path/digest required",
    )
    config = Config.parse(read(args.config, args.config_sha256))
    require(
        config.harness_sha256 == args.harness_manifest_sha256,
        "Config/manifest binding mismatch",
    )
    require(
        digest(Path(sys.executable).read_bytes()) == config.interpreter_sha256,
        "Interpreter identity mismatch",
    )
    if args.command == "preflight":
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "scope": "declarations only; no file/Git/network/store effects",
                    "run_root": str(config.layout.run),
                    "deferred": [
                        "source object availability",
                        "A0-A4 activation",
                        "private tool qualification",
                        "model window",
                    ],
                }
            )
        )
        return 0
    if args.command == "init":
        from ingest.startup import harness_state

        _, BUFFERS = harness_state()
        config.layout.create()
        for name, raw in BUFFERS.items():
            target = config.layout.destination("harness/" + name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            target.chmod(0o444)
        control = canonical(config.record())
        config.layout.destination("config/control.json").write_bytes(control)
        config.layout.destination("config/harness-manifest.json").write_bytes(
            args.harness_manifest.read_bytes()
        )
        ledger = Ledger(config.layout.destination("state"))
        ledger.append(
            "init",
            {
                "run_id": config.layout.run_id,
                "config_sha256": digest(control),
                "harness_sha256": config.harness_sha256,
            },
            ZERO,
        )
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "scope": "C0 control-run initialized; application source/upstream qualification deferred",
                    "config": str(config.layout.destination("config/control.json")),
                    "config_sha256": digest(control),
                    "harness_manifest": str(
                        config.layout.destination("config/harness-manifest.json")
                    ),
                    "ledger_tip": ledger.tip(),
                }
            )
        )
        return 0
    ledger = _bound(config)
    if args.command == "stop":
        _stop(ledger)
        output: dict[str, object] = {
            "status": "STOPPED",
            "effect_resume": "new_run_required",
            "report_available": True,
        }
    elif args.command == "prepare-fixtures":
        from ingest.fixtures import publish_matrix
        from ingest.startup import harness_state

        require(not ledger.stopped(), "Run stopped; effects require new run")
        _, buffers = harness_state()
        oracle = object_value(
            object_value(decode(buffers["fixtures/expectations.json"])["A2"])[
                "fixture_oracles"
            ]
        )
        destination = config.layout.destination("fixtures/generated")
        with ledger.lease() as token:
            require(not ledger.stopped(), "Run stopped; effects require new run")
            tip = ledger.tip()
            published = publish_matrix(
                destination,
                oracle,
                lambda: require(
                    not ledger.stopped(), "Run stopped during fixture preparation"
                ),
            )
            manifest_sha = digest(canonical(published))
            ledger.append_held(
                "finish",
                {
                    "operation": "prepare_fixtures",
                    "manifest_sha256": manifest_sha,
                    "fixture_count": 30,
                    "converter_qualified": False,
                },
                tip,
                token,
            )
        output = {
            "status": "PREPARED_INPUTS",
            "scope": "generated synthetic inputs only",
            "fixture_count": 30,
            "manifest": str(destination / "manifest.json"),
            "manifest_sha256": manifest_sha,
            "converter_qualified": False,
            "full_readiness": False,
        }
    elif args.command == "report":
        output = report(ledger)
    elif args.command == "promote":
        require(
            args.manifest is not None
            and args.sha256 is not None
            and args.approval is not None,
            "Explicit promotion manifest/digest/approval required",
        )
        read(args.manifest, args.sha256)
        ledger.promote(args.sha256, read(args.approval))
        output = {"status": "PASS", "ledger_tip": ledger.tip()}
    else:
        require(not ledger.stopped(), "Run stopped; effects require new run")
        output = {
            "status": "BLOCKED_NOT_ACTIVATED",
            "scope": "offline construction only",
            "requested_stage": args.stage if args.command == "run" else "prepare-model",
            "reason": "Actual A0-A4 adapters/profiles remain unimplemented or unqualified in this offline component; no stage activation is inferred",
            "ledger_tip": ledger.tip(),
            "full_readiness": False,
            "effects_performed": False,
        }
    print(json.dumps(output))
    return 3 if output["status"] in {"BLOCKED_NOT_ACTIVATED", "INCOMPLETE"} else 0
