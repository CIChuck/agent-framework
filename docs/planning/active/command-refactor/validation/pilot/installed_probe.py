"""Guarded isolated-wheel proof for the neutral and default Chat pilot lanes."""

from __future__ import annotations

import argparse
import asyncio
import email
import hashlib
import importlib
import importlib.metadata as metadata
import json
import re
import runpy
import subprocess
import sys
import tarfile
import zipfile
from dataclasses import asdict
from pathlib import Path
from types import MappingProxyType


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def origins() -> dict[str, list[str]]:
    result = {}
    for name, module in tuple(sys.modules.items()):
        if not name.startswith("friday") or module is None:
            continue
        file = getattr(module, "__file__", None)
        paths = [file] if file else list(getattr(module, "__path__", ()))
        require(bool(paths), "Missing installed module origin: " + name)
        require(
            all(
                Path(path).resolve().is_relative_to(Path(sys.prefix).resolve())
                for path in paths
            ),
            "Module escaped installed environment: " + name,
        )
        result[name] = [str(Path(path).resolve()) for path in paths]
    return result


def artifact_members(args: argparse.Namespace, distribution: str, package: str) -> dict:
    slug = distribution.replace("-", "_")
    project = (
        args.source
        / "packages"
        / ("friday-commands" if package == "friday_commands" else "friday-chat")
    )
    source_root = project / "src"
    expected = {
        str(path.relative_to(source_root)): path.read_bytes()
        for path in (source_root / package).rglob("*")
        if path.is_file()
    }
    wheel = args.dist / f"{slug}-0.1.0a4-py3-none-any.whl"
    sdist = args.dist / f"{slug}-0.1.0a4.tar.gz"
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "Duplicate wheel members")
        source_names = {
            name
            for name in names
            if name.startswith(package + "/") and not name.endswith("/")
        }
        require(
            source_names == set(expected),
            "Wheel source/data inventory differs from Git",
        )
        dist_info = f"{slug}-0.1.0a4.dist-info/"
        generated = {dist_info + name for name in ("METADATA", "WHEEL", "RECORD")}
        if package == "friday_chat":
            generated |= {
                dist_info + "entry_points.txt",
                dist_info + "licenses/LICENSE",
            }
        require(
            set(names) == source_names | generated,
            "Unrecognized generated wheel member",
        )
        installed = metadata.distribution(distribution)
        for name, content in expected.items():
            require(archive.read(name) == content, "Wheel/Git byte mismatch: " + name)
            require(
                Path(installed.locate_file(name)).read_bytes() == content,
                "Installed/Git byte mismatch: " + name,
            )
        wheel_metadata = email.message_from_bytes(archive.read(dist_info + "METADATA"))
    with tarfile.open(sdist) as archive:
        files = [member for member in archive.getmembers() if member.isfile()]
        prefix = f"{slug}-0.1.0a4/"
        require(
            all(member.name.startswith(prefix) for member in files),
            "Unexpected sdist root",
        )
        contents = {}
        for member in files:
            require(member.name not in contents, "Duplicate sdist member")
            handle = archive.extractfile(member)
            require(handle is not None, "Unreadable sdist file")
            contents[member.name.removeprefix(prefix)] = handle.read()
        project_files = {
            str(path.relative_to(project)): path.read_bytes()
            for path in project.rglob("*")
            if path.is_file()
        }
        require(
            set(contents) == set(project_files) | {".gitignore", "PKG-INFO"},
            "Sdist inventory differs from Git project",
        )
        for name, content in project_files.items():
            require(contents[name] == content, "Sdist/Git mismatch: " + name)
        require(
            contents[".gitignore"] == (args.source / ".gitignore").read_bytes(),
            "Generated sdist gitignore differs from Git root",
        )
        info = email.message_from_bytes(contents["PKG-INFO"])
        for field in ("Name", "Version", "Requires-Python"):
            require(
                info[field] == wheel_metadata[field],
                "Wheel/sdist metadata mismatch: " + field,
            )
        require(
            info.get_all("Requires-Dist", [])
            == wheel_metadata.get_all("Requires-Dist", []),
            "Wheel/sdist dependency mismatch",
        )
    requirements = wheel_metadata.get_all("Requires-Dist", [])
    if package == "friday_commands":
        require(not requirements, "Neutral package acquired dependencies")
        require(not installed.entry_points, "Neutral package acquired entry points")
    else:
        require(
            "friday-framework-commands==0.1.0a4" in requirements,
            "Required unconditional Commands edge absent",
        )
    return {
        "wheel_sha256": digest(wheel),
        "sdist_sha256": digest(sdist),
        "source_members": len(expected),
        "sdist_files": len(files),
        "requires_dist": requirements,
    }


async def neutral_behavior() -> dict:
    import friday_commands as api
    import friday_commands.pilot as shared

    registry = api.CommandRegistry()
    require(not registry.names(), "Neutral registry populated implicitly")

    class Catalog:
        def specs(self) -> tuple:
            return registry.specs()

        def lookup_key(self, key: str) -> object:
            keys = {
                key: spec
                for spec in registry.specs()
                for key in (spec.name, *spec.aliases)
            }
            return keys.get(key)

    catalog = Catalog()
    handlers = shared.build_pilot_handlers(catalog)
    require(isinstance(handlers, MappingProxyType), "Handler map is mutable")
    require(tuple(handlers) == ("help", "exit", "cls"), "Pilot handler keys changed")
    for spec in shared.PILOT_SPECS:
        registry.register(spec, handlers[spec.name])
    for text in ("/exit extra", "/q", "/quit"):
        result = await registry.execute_text(text, api.CommandExecution())
        require(
            result.outcome == api.CommandOutcome(data=api.ExitData(True)),
            "Standalone exit/alias failed",
        )
    for text in ("/cls extra", "/clearscreen"):
        result = await registry.execute_text(text, api.CommandExecution())
        require(
            result.outcome
            == api.CommandOutcome(
                data=api.NoData(), ui_effects=(api.UiEffect.CLEAR_SCREEN,)
            ),
            "Standalone clear failed",
        )
    general = await registry.execute_text("/help", api.CommandExecution())
    require(
        tuple(spec.name for spec in general.outcome.data.commands)
        == ("cls", "exit", "help"),
        "Standalone help sorting failed",
    )
    focused = await registry.execute_text("/help /q", api.CommandExecution())
    require(
        focused.outcome.data.focused_name == "exit", "Standalone focused alias failed"
    )
    unknown = await registry.execute_text("/help //q", api.CommandExecution())
    require(
        unknown.outcome.error == api.CommandError("unknown_command", "/q"),
        "Standalone normalization changed",
    )
    snapshot = catalog.specs()
    registry.register(
        api.CommandSpec("later", "Later.", "custom", "/later"), handlers["exit"]
    )
    require(
        len(snapshot) == 3 and len(catalog.specs()) == 4, "Catalog snapshot changed"
    )
    require(
        all(
            name == "friday_commands" or name.startswith("friday_commands.")
            for name in origins()
        ),
        "Neutral lane loaded a host package",
    )
    return {
        "aliases_and_help": "passed",
        "snapshot": "immutable",
        "host_imports": "none",
    }


async def chat_behavior(args: argparse.Namespace) -> dict:
    import friday_commands as api
    import friday_commands.pilot as shared
    from friday_chat.commands.contracts import CommandContext, CommandResult
    from friday_chat.commands.registry import (
        CommandRegistry,
        RegistryCommandContext,
        _exit_handler,
        _help_handler,
        build_default_registry,
    )
    from friday_chat.commands.session import cls_handler

    importlib.import_module("friday_finance")
    importlib.import_module("friday_tools")
    baseline = json.loads(args.baseline.read_text())["observations"]
    registry = build_default_registry()
    require(
        len(registry.canonical_names()) == 41 and len(registry.command_names()) == 44,
        "Installed surface changed",
    )
    actual = {key: asdict(value) for key, value in registry.commands.items()}
    require(
        json.dumps(actual, sort_keys=True)
        == json.dumps(baseline["metadata"], sort_keys=True),
        "Installed metadata differs from oracle",
    )
    original_factory, original_select = (
        shared.build_pilot_handlers,
        shared.describe_help,
    )
    calls, factories, selections = [], [], []

    def factory(catalog) -> object:
        factories.append(catalog)
        handlers = original_factory(catalog)

        def wrap(name):
            async def invoke(request, execution):
                require(
                    request.spec
                    is next(spec for spec in shared.PILOT_SPECS if spec.name == name),
                    "Shared request spec is not canonical",
                )
                require(
                    type(request) is api.CommandRequest
                    and type(execution) is api.CommandExecution,
                    "Shared request/execution type changed",
                )
                calls.append((name, request.args))
                return await handlers[name](request, execution)

            return invoke

        return MappingProxyType({name: wrap(name) for name in handlers})

    def select(catalog, focus=None) -> object:
        selections.append(focus)
        return original_select(catalog, focus)

    shared.build_pilot_handlers, shared.describe_help = factory, select
    try:
        for row in baseline["help"]:
            before = len(selections)
            require(
                registry.render_help(row["focus"]) == row["output"],
                "Installed help output changed",
            )
            require(
                len(selections) == before + 1, "Synchronous help did not select once"
            )
        for row in baseline["dispatch"]:
            before = len(calls)
            context = RegistryCommandContext(registry=registry)
            handled, result = await registry.execute(row["input"], context)
            actual_row = {
                "input": row["input"],
                "handled": handled,
                "output": None if result is None else result.output,
                "result_handled": None if result is None else result.handled,
                "exit": None if result is None else result.exit_requested,
                "effects": []
                if result is None
                else [effect.value for effect in result.ui_effects],
                "context_exit": context.exit_requested,
            }
            require(actual_row == row, "Installed parser/dispatch fixture changed")
            if len(calls) > before:
                require(
                    len(calls) == before + 1 and len(factories) == len(calls),
                    "Handler invoked more than once",
                )

        class Tripwire:
            def __getattribute__(self, name):
                raise RuntimeError("Host attribute read: " + name)

        for handler in (_exit_handler, cls_handler):
            before = len(calls)
            await handler(Tripwire(), ("ignored",), Tripwire())
            require(len(calls) == before + 1, "Direct wrapper did not delegate once")
        custom = CommandRegistry()
        custom.register(
            "only-here", description="Custom.", category="custom", detail=False
        )
        result = await _help_handler(
            RegistryCommandContext(registry=custom), (), registry.commands["help"]
        )
        require(
            result.output == custom.render_help(),
            "Context-specific/falsy-detail help changed",
        )

        async def sentinel(_context, _args, _metadata):
            return CommandResult("custom authoritative")

        for name in ("help", "exit", "cls", "vars"):
            selected = CommandRegistry()
            selected.register(
                name, description="Custom.", category="custom", handler=sentinel
            )
            before = len(calls)
            _, result = await selected.execute("/" + name)
            require(
                result.output == "custom authoritative" and len(calls) == before,
                "Custom handler intercepted",
            )

        def injected_factory(_catalog) -> object:
            async def injected(_request, _execution):
                return api.CommandOutcome(
                    error=api.CommandError("unknown_command", "shared-outcome-sentinel")
                )

            return {name: injected for name in ("help", "exit", "cls")}

        shared.build_pilot_handlers = injected_factory
        for text in ("/help", "/exit", "/cls"):
            context = CommandContext()
            _, result = await registry.execute(text, context)
            require(
                result
                == CommandResult(
                    "Unknown command: /shared-outcome-sentinel. Type /help for available commands."
                ),
                "Shared outcome ignored by Chat",
            )
            require(not context.exit_requested, "Chat duplicated exit policy")
    finally:
        shared.build_pilot_handlers, shared.describe_help = (
            original_factory,
            original_select,
        )
    return {
        "metadata": 41,
        "help": 62,
        "dispatch": 29,
        "factory_calls": len(factories),
        "handler_calls": len(calls),
        "shared_outcome_injection": "passed",
        "default_finance_tools_imports": "passed",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=("neutral", "chat"), required=True)
    for name in ("prepared", "source", "dist", "profile", "baseline", "report"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    require(sys.flags.isolated == 1, "Use installed interpreter with -I")
    require(not args.report.exists(), "Refuse report overwrite")
    bootstrap = json.loads((args.prepared / "bootstrap.json").read_text())
    require(
        digest(args.prepared / "sitecustomize.py")
        == bootstrap["combined_guard_sha256"],
        "Combined guard drift",
    )
    require(
        digest(args.prepared / "pilot_guard.py") == bootstrap["guard_extension_sha256"],
        "Guard extension drift",
    )
    sys.path.insert(0, str(args.prepared))
    try:
        runpy.run_path(str(args.prepared / "sitecustomize.py"))
    finally:
        sys.path.pop(0)
    require(
        digest(args.baseline)
        == "48c3161cf1a0467c7e95ac11a85de0972d46421b5a9318ee618651f7cc7ad7f1",
        "Baseline drift",
    )
    expected = {
        normalized(name): version
        for name, version in re.findall(
            r"^([\w.-]+)==([^\s;]+)", args.profile.read_text(), flags=re.MULTILINE
        )
    }
    installed = {
        normalized(dist.metadata["Name"]): dist.version
        for dist in metadata.distributions()
    }
    require(
        installed == expected,
        "Installed distribution closure differs from hashed profile",
    )
    if args.lane == "neutral":
        require(
            installed == {"friday-framework-commands": "0.1.0a4"},
            "Neutral closure includes other packages",
        )
    else:
        require(
            not {
                "friday-framework-speech",
                "friday-framework-sandbox",
                "friday-framework-moltbook",
            }
            & installed.keys(),
            "Diagnostic optional extras installed",
        )
        require(
            not any(
                point.name == "friday"
                for point in metadata.entry_points(group="console_scripts")
            ),
            "Legacy executable declared",
        )
        require(
            not (Path(sys.prefix) / "bin/friday").exists(),
            "Legacy executable installed",
        )
    report = {
        "lane": args.lane,
        "interpreter": sys.executable,
        "prefix": sys.prefix,
        "isolated": True,
        "guard_sha256": bootstrap["combined_guard_sha256"],
        "probe_sha256": digest(Path(__file__)),
        "installed_distributions": installed,
        "artifacts": {},
    }
    report["artifacts"]["commands"] = artifact_members(
        args, "friday-framework-commands", "friday_commands"
    )
    if args.lane == "chat":
        report["artifacts"]["chat"] = artifact_members(
            args, "friday-chat", "friday_chat"
        )
        report["behavior"] = asyncio.run(chat_behavior(args))
        code = (
            "import sys,runpy,importlib.metadata as m;sys.path.insert(0,"
            + repr(str(args.prepared))
            + ");runpy.run_path("
            + repr(str(args.prepared / "sitecustomize.py"))
            + ");sys.path.pop(0);sys.argv=['friday-chat','--help'];[p for p in m.distribution('friday-chat').entry_points if p.name=='friday-chat'][0].load()()"
        )
        help_run = subprocess.run(
            [sys.executable, "-I", "-B", "-c", code],
            text=True,
            capture_output=True,
            cwd=args.report.parent,
        )
        require(
            help_run.returncode == 0 and "Usage:" in help_run.stdout,
            "Installed Chat entry-point help failed",
        )
        report["entry_point_help"] = {
            "exit": help_run.returncode,
            "output": help_run.stdout,
            "stderr": help_run.stderr,
        }
    else:
        report["behavior"] = asyncio.run(neutral_behavior())
    report["origins"] = origins()
    report["status"] = "passed"
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"Installed {args.lane} proof passed: {len(installed)} distributions; artifact members/origins/behavior verified"
    )


if __name__ == "__main__":
    main()
