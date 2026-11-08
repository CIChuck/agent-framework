"""Isolated installed SESSION proof; source exports are inventory oracles only."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata as metadata
import json
import os
import re
import runpy
import stat
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from types import MappingProxyType, SimpleNamespace

PILOT_PROBE_SHA256 = "8c1233a0a5181566bb188735358141e8718a5aaba205e6c4bfa3a2620a8e43ac"
GUARD_SHA256 = "d96294f94f5378beb38675d0624e6f78c622914cafbaffb4ce486d8310d2eb7e"
EXTENSION_SHA256 = "e04eea8bc9722defe3ea89212385f8befda03e051b9816b305e1b9f73ff94681"
FIXTURE_SHA256 = "3b512406d989e7d114fdcc17ac270eaccb3bcf772dc09a15fd566b10afeb6ea7"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expect_error(kind, action) -> None:
    try:
        action()
    except kind:
        return
    raise RuntimeError("Missing required refusal: " + kind.__name__)


def load_guard(prepared: Path) -> dict:
    bootstrap = json.loads((prepared / "bootstrap.json").read_text())
    require(
        digest(prepared / "sitecustomize.py")
        == bootstrap["combined_guard_sha256"]
        == GUARD_SHA256,
        "Combined guard drift",
    )
    require(
        digest(prepared / "pilot_guard.py")
        == bootstrap["guard_extension_sha256"]
        == EXTENSION_SHA256,
        "Guard extension drift",
    )
    sys.path.insert(0, str(prepared))
    try:
        runpy.run_path(str(prepared / "sitecustomize.py"))
    finally:
        sys.path.pop(0)
    return bootstrap


def origins() -> dict[str, list[str]]:
    """Check file AND search paths; bind changed packages to inventoried roots."""
    roots = {
        package: Path(
            metadata.distribution(distribution).locate_file(package)
        ).resolve()
        for package, distribution in (
            ("friday_commands", "friday-framework-commands"),
            ("friday_chat", "friday-chat"),
        )
        if any(
            name == package or name.startswith(package + ".") for name in sys.modules
        )
    }
    result = {}
    for name, module in tuple(sys.modules.items()):
        if not name.startswith("friday") or module is None:
            continue
        file = getattr(module, "__file__", None)
        paths = ([file] if file else []) + list(getattr(module, "__path__", ()))
        require(bool(paths), "Missing installed module origin: " + name)
        resolved = [Path(path).resolve() for path in paths]
        require(
            all(path.is_relative_to(Path(sys.prefix).resolve()) for path in resolved),
            "Module escaped installed environment: " + name,
        )
        package = name.split(".", 1)[0]
        if package in roots:
            require(
                all(path.is_relative_to(roots[package]) for path in resolved),
                "Module escaped inventoried package root: " + name,
            )
        result[name] = [str(path) for path in resolved]
    return result


def profile_versions(path: Path) -> dict[str, str]:
    return {
        re.sub(r"[-_.]+", "-", name).lower(): version
        for name, version in re.findall(
            r"^([\w.-]+)==([^\s;]+)", path.read_text(), re.MULTILINE
        )
    }


def artifact_members(args, legacy, distribution: str, package: str) -> dict:
    # Reuse the immutable accepted complete wheel/installed/sdist checks.
    result = legacy["artifact_members"](args, distribution, package)
    project = "friday-commands" if package == "friday_commands" else "friday-chat"
    source = args.source / "packages" / project / "src" / package
    installed = Path(metadata.distribution(distribution).locate_file(package))
    for path in source.rglob("*"):
        if path.is_file():
            actual = installed / path.relative_to(source)
            require(
                stat.S_IMODE(actual.stat().st_mode) & 0o111
                == stat.S_IMODE(path.stat().st_mode) & 0o111,
                "Installed/Git executable mode mismatch",
            )
    result["installed_root"] = str(installed.resolve())
    result["complete_file_directory_byte_executable_inventory"] = "passed"
    return result


async def neutral_behavior() -> dict:
    import friday_commands as api
    import friday_commands.session_views as shared

    expected_exports = [
        "PILOT_SPECS",
        "SESSION_SPECS",
        "CommandArgument",
        "CommandError",
        "CommandExecution",
        "CommandHandler",
        "CommandOutcome",
        "CommandRegistry",
        "CommandRequest",
        "CommandSpec",
        "DispatchResult",
        "ExitData",
        "FoundationData",
        "HelpCatalog",
        "HelpData",
        "HistoryData",
        "HistoryTurn",
        "NoData",
        "SessionClearedData",
        "SessionPort",
        "UiEffect",
        "build_pilot_handlers",
        "build_session_handlers",
        "describe_help",
    ]
    require(api.__all__ == expected_exports, "Exact SESSION export surface changed")

    def request(name, args=()):
        spec = next((s for s in shared.SESSION_SPECS if s.name == name), None)
        if spec is None:
            spec = api.CommandSpec(name, "Other", "test", "/" + name)
        return api.CommandRequest(name, args, spec)

    class Text(str):
        pass

    text = Text("unchanged")
    turn = api.HistoryTurn(text, "reply")
    require(turn.user_message is text, "String subclass was coerced")
    expect_error(TypeError, lambda: api.HistoryTurn(1, "reply"))
    expect_error(TypeError, lambda: api.HistoryTurn("user", None))
    values = [api.HistoryTurn("z", "B"), api.HistoryTurn("a", "A"), turn, turn]
    reads = []

    def once():
        for item in values:
            reads.append(item)
            yield item

    snapshot = api.HistoryData(once())
    require(
        snapshot.turns == tuple(values) and reads == values,
        "Snapshot changed order/count",
    )
    values.clear()
    require(len(snapshot.turns) == 4, "Snapshot was not independent")
    expect_error(AttributeError, lambda: setattr(turn, "user_message", "changed"))
    expect_error(AttributeError, lambda: setattr(snapshot, "turns", ()))
    require(not hasattr(turn, "__dict__"), "HistoryTurn is not slotted")
    expect_error(TypeError, lambda: api.SessionClearedData("extra"))

    class ChildTurn(api.HistoryTurn):
        pass

    class ChildData(api.HistoryData):
        pass

    for bad in (None, 1, "", b"", bytearray(), {}, [object()], [ChildTurn("u", "a")]):
        expect_error(TypeError, lambda bad=bad: api.HistoryData(bad))
    expect_error(TypeError, lambda: api.CommandOutcome(data=ChildData(())))
    expect_error(ValueError, api.CommandOutcome)
    expect_error(
        ValueError,
        lambda: api.CommandOutcome(
            data=api.NoData(), error=api.CommandError("failed", "clear")
        ),
    )
    expect_error(
        ValueError,
        lambda: api.CommandOutcome(
            error=api.CommandError("failed", "clear"),
            ui_effects=(api.UiEffect.CLEAR_SCREEN,),
        ),
    )

    class Tripwire:
        def __getattribute__(self, name):
            raise RuntimeError("Unexpected port read: " + name)

    first = shared.build_session_handlers(Tripwire())
    second = shared.build_session_handlers(Tripwire())
    require(
        first is not second and isinstance(first, MappingProxyType),
        "Factory mapping not fresh/immutable",
    )
    require(tuple(first) == ("clear", "history"), "Session handler keys changed")

    def mutate():
        first["clear"] = None

    expect_error(TypeError, mutate)
    for name, handler in first.items():
        for invocation, execution, kind in (
            (object(), object(), TypeError),
            (request(name), object(), TypeError),
            (request("wrong"), api.CommandExecution(), ValueError),
        ):
            try:
                await handler(invocation, execution)
            except kind:
                pass
            else:
                raise RuntimeError("Invocation boundary refusal missing")

    events, turns = [], list(snapshot.turns)
    entered, release = asyncio.Event(), asyncio.Event()

    class Port:
        def history_snapshot(self):
            events.append("snapshot")
            return turns

        def clear_history(self):
            events.append("history.clear")
            turns.clear()

        async def clear_session_memory(self):
            events.append("memory.enter")
            entered.set()
            await release.wait()
            events.append("memory.return")

    handlers = shared.build_session_handlers(Port())
    history = await handlers["history"](
        request("history", ("ignored",)), api.CommandExecution()
    )
    require(
        history == api.CommandOutcome(data=snapshot), "Shared history snapshot changed"
    )
    require(events == ["snapshot"], "History performed other operations")
    events.clear()
    task = asyncio.create_task(
        handlers["clear"](request("clear", ("ignored",)), api.CommandExecution())
    )
    try:
        await asyncio.wait_for(entered.wait(), 2)
        require(not turns and not task.done(), "Clear returned before memory await")
        require(
            events == ["history.clear", "memory.enter"], "Clear order/count changed"
        )
        release.set()
        require(
            await asyncio.wait_for(task, 2)
            == api.CommandOutcome(data=api.SessionClearedData()),
            "Clear result changed",
        )
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    require(history.data.turns == snapshot.turns, "Prior history result mutated")

    for phase in ("snapshot", "history.clear", "memory"):
        for kind in (RuntimeError, asyncio.CancelledError):
            failure = kind(phase)

            class FailingPort:
                def __init__(self, failure, phase):
                    self.failure, self.phase, self.calls = failure, phase, []

                def history_snapshot(self):
                    self.calls.append("snapshot")
                    raise self.failure

                def clear_history(self):
                    self.calls.append("history.clear")
                    if self.phase == "history.clear":
                        raise self.failure

                async def clear_session_memory(self):
                    self.calls.append("memory")
                    raise self.failure

            name = "history" if phase == "snapshot" else "clear"
            port = FailingPort(failure, phase)
            try:
                await shared.build_session_handlers(port)[name](
                    request(name), api.CommandExecution()
                )
            except kind as error:
                require(error is failure, "Port exception identity changed")
            else:
                raise RuntimeError("Port exception swallowed")
            expected = (
                ["snapshot"]
                if name == "history"
                else ["history.clear"] + (["memory"] if phase == "memory" else [])
            )
            require(port.calls == expected, "Failure boundary retried or reordered")

    registry = api.CommandRegistry()
    require(not registry.names(), "Neutral registry populated implicitly")
    release.set()
    for spec in shared.SESSION_SPECS:
        registry.register(spec, handlers[spec.name])
    require(
        (await registry.execute_text("/HISTORY extra", api.CommandExecution())).outcome
        == api.CommandOutcome(data=api.HistoryData(())),
        "Explicit history dispatch failed",
    )
    require(
        (await registry.execute_text("/clear extra", api.CommandExecution())).outcome
        == api.CommandOutcome(data=api.SessionClearedData()),
        "Explicit clear dispatch failed",
    )
    require(
        all(
            name == "friday_commands" or name.startswith("friday_commands.")
            for name in origins()
        ),
        "Neutral lane imported host packages",
    )
    return {
        "models_snapshot_boundaries": "passed",
        "factory_and_dispatch": "passed",
        "pending_await_and_order": "passed",
        "exception_identity_controls": 6,
        "host_imports": "none",
    }


async def chat_behavior(args) -> dict:
    import friday_commands as api
    import friday_commands.session_views as shared
    from friday_chat.commands import registry as registry_module
    from friday_chat.commands import session_views as adapter
    from friday_chat.commands.contracts import (
        CommandContext,
        CommandMetadata,
        CommandResult,
    )
    from friday_chat.commands.registry import (
        CommandRegistry,
        RegistryCommandContext,
        _clear_handler,
        _history_handler,
        build_default_registry,
    )

    fixture = (
        args.source
        / "packages/friday-chat/tests_chat/fixtures_session/session-baseline.json"
    )
    require(digest(fixture) == FIXTURE_SHA256, "Session oracle drift")
    baseline = json.loads(fixture.read_text())
    registry = build_default_registry()
    require(
        json.dumps(
            {name: asdict(registry.commands[name]) for name in ("clear", "history")},
            sort_keys=True,
        )
        == json.dumps(baseline["metadata"], sort_keys=True),
        "Session metadata changed",
    )
    original_factory, original_parse = (
        shared.build_session_handlers,
        registry_module._parse_command_input,
    )
    factories, calls, parses = [], [], []
    expected_context = None

    def parse(text):
        parses.append(text)
        return original_parse(text)

    def factory(port):
        require(port.context is expected_context, "Wrong supplied session context")
        factories.append(port)
        handlers = original_factory(port)

        def wrapped(name):
            async def invoke(request, execution):
                require(
                    type(request) is api.CommandRequest
                    and type(execution) is api.CommandExecution,
                    "Wrong shared invocation types",
                )
                require(
                    request.name == name
                    and request.spec
                    is next(s for s in shared.SESSION_SPECS if s.name == name),
                    "Noncanonical shared session request",
                )
                calls.append((name, request.args))
                return await handlers[name](request, execution)

            return invoke

        return {name: wrapped(name) for name in handlers}

    class History(list):
        def __init__(self, values, events, failure=None):
            super().__init__(values)
            self.events, self.failure = events, failure

        def clear(self):
            self.events.append("history.clear")
            if self.failure is not None:
                raise self.failure
            super().clear()

    class Context:
        def __init__(self, history, events, runtime=None, failure=None):
            self.history, self.events = history, events
            self._runtime, self.failure = runtime, failure

        @property
        def runtime(self):
            self.events.append("runtime.read")
            if self.failure is not None:
                raise self.failure
            return self._runtime

    class Memory:
        def __init__(self, history, events, returned=True, failure=None):
            self.history, self.events = history, events
            self.returned, self.failure = returned, failure

        async def clear_session_memory(self):
            self.events.append("memory.clear:history=" + json.dumps(self.history))
            if self.failure is not None:
                raise self.failure
            return self.returned

    def result(value):
        return None if value is None else asdict(value)

    rows = []
    marker = CommandMetadata("unused", "Unused", "unused", "/unused")
    shared.build_session_handlers, registry_module._parse_command_input = factory, parse
    try:
        for row in baseline["cases"]:
            before, before_parse = len(calls), len(parses)
            case, events = row["case"], []
            actual = {"case": case}
            if case.startswith("history:"):
                history = History(row["turns"], events)
                expected_context = Context(
                    history, events, failure=RuntimeError("History read runtime")
                )
                actual.update(turns=row["turns"], args=row["args"])
                try:
                    actual["result"] = result(
                        await _history_handler(
                            expected_context, tuple(row["args"]), marker
                        )
                    )
                except Exception as error:
                    actual["exception"] = {
                        "type": type(error).__name__,
                        "message": str(error),
                    }
                actual.update(events=events, history_after=list(history))
            elif case == "clear:await-order":
                history = History([("hello", "world")], events)
                entered, release = asyncio.Event(), asyncio.Event()

                class BlockingMemory:
                    def __init__(self, events, entered, release):
                        self.events, self.entered, self.release = (
                            events,
                            entered,
                            release,
                        )

                    async def clear_session_memory(self):
                        self.events.append("memory.enter")
                        self.entered.set()
                        await self.release.wait()
                        self.events.append("memory.return")
                        return False

                expected_context = Context(
                    history,
                    events,
                    SimpleNamespace(memory=BlockingMemory(events, entered, release)),
                )
                task = asyncio.create_task(_clear_handler(expected_context, (), marker))
                try:
                    await asyncio.wait_for(entered.wait(), 2)
                    actual["during_await"] = {
                        "history": list(history),
                        "task_done": task.done(),
                        "events": list(events),
                    }
                    release.set()
                    actual["result"] = result(await asyncio.wait_for(task, 2))
                finally:
                    task.cancel()
                    await asyncio.gather(task, return_exceptions=True)
                actual["events"] = events
            elif case.startswith("clear:"):
                label = case.split(":", 1)[1]
                failure = (
                    asyncio.CancelledError("cancelled")
                    if label == "memory-cancel"
                    else RuntimeError(label)
                )
                history = History(
                    [("hello", "world")],
                    events,
                    failure if label == "history-exception" else None,
                )
                memory = Memory(
                    history,
                    events,
                    label != "memory-false",
                    failure if label in ("memory-exception", "memory-cancel") else None,
                )
                expected_context = Context(
                    history,
                    events,
                    None if label == "no-runtime" else SimpleNamespace(memory=memory),
                    failure if label == "runtime-exception" else None,
                )
                actual["args"] = row["args"]
                alias = history
                try:
                    actual["result"] = result(
                        await _clear_handler(
                            expected_context, tuple(row["args"]), marker
                        )
                    )
                except BaseException as error:
                    actual["exception"] = {
                        "type": type(error).__name__,
                        "message": str(error),
                        "same_object": error is failure,
                    }
                require(expected_context.history is alias, "History list replaced")
                actual.update(events=events, history_after=list(history))
            else:
                selected = registry
                expected_context = CommandContext(history=[("hello", "world")])
                if case.startswith("renamed:"):
                    selected = CommandRegistry()
                    selected.register(
                        "renamed",
                        description="Renamed",
                        category="test",
                        handler=_history_handler
                        if case.endswith("history")
                        else _clear_handler,
                    )
                    text = "/renamed extra"
                else:
                    text = case.removeprefix("dispatch:")
                handled, value = await selected.execute(text, expected_context)
                actual.update(
                    handled=handled,
                    result=result(value),
                    history_after=expected_context.history,
                )
                if case.startswith("dispatch:"):
                    actual["exit_requested"] = expected_context.exit_requested
            require(
                json.dumps(actual, sort_keys=True) == json.dumps(row, sort_keys=True),
                "Installed SESSION fixture changed: " + case,
            )
            count = 0 if case == "dispatch: /clear" else 1
            require(
                len(calls) == before + count and len(factories) == len(calls),
                "Session row did not delegate once: " + case,
            )
            require(
                len(parses)
                == before_parse
                + (1 if case.startswith(("dispatch:", "renamed:")) and count else 0),
                "Session parse count changed: " + case,
            )
            rows.append(actual)
        require(len(calls) == 24, "Frozen SESSION delegation count changed")

        class Formatted(str):
            def __format__(self, spec):
                raise RuntimeError("Formatted message was formatted twice")

        formatted = []

        class Value:
            def __format__(self, spec):
                formatted.append(spec)
                return Formatted("once")

        expected_context = CommandContext(history=[(Value(), Value())])
        rendered = await _history_handler(expected_context, (), marker)
        require(
            rendered.output == "Conversation history:\n1. User: once\n   Friday: once"
            and formatted == ["", ""],
            "Legacy formatting projection changed",
        )
        expected_context = RegistryCommandContext(
            registry=CommandRegistry(), history=[("context", "wins")]
        )
        _, rendered = await registry.execute("/history extra", expected_context)
        require("User: context" in rendered.output, "Supplied context was replaced")

        async def sentinel(_context, _args, _metadata):
            return CommandResult("custom")

        for name in ("history", "clear", "set", "prime"):
            selected = CommandRegistry()
            selected.register(
                name, description="Custom", category="test", handler=sentinel
            )
            before = len(calls)
            _, rendered = await selected.execute("/" + name, CommandContext())
            require(
                rendered == CommandResult("custom") and len(calls) == before,
                "Custom session handler intercepted",
            )

        injected_calls = []

        def injected_factory(port):
            async def invoke(request, execution):
                injected_calls.append(request.name)
                return api.CommandOutcome(
                    data=api.HistoryData((api.HistoryTurn("shared", "sentinel"),))
                )

            return {"history": invoke, "clear": invoke}

        shared.build_session_handlers = injected_factory
        for name in ("history", "clear"):
            context = CommandContext(history=[("original", "untouched")])
            _, rendered = await registry.execute("/" + name, context)
            require(
                rendered
                == CommandResult(
                    "Conversation history:\n1. User: shared\n   Friday: sentinel"
                ),
                "Shared SESSION outcome ignored by Chat",
            )
            require(
                context.history == [("original", "untouched")],
                "Chat retained a shadow session engine",
            )
        require(
            injected_calls == ["history", "clear"],
            "Injected session invocation count changed",
        )
    finally:
        shared.build_session_handlers, registry_module._parse_command_input = (
            original_factory,
            original_parse,
        )
    for outcome in (
        api.CommandOutcome(data=api.NoData()),
        api.CommandOutcome(data=api.ExitData()),
        api.CommandOutcome(error=api.CommandError("failed", "history")),
        api.CommandOutcome(
            data=api.HistoryData(()), ui_effects=(api.UiEffect.CLEAR_SCREEN,)
        ),
    ):
        expect_error(
            ValueError, lambda outcome=outcome: adapter.adapt_session_outcome(outcome)
        )
    return {
        "metadata": 2,
        "frozen_observations": len(rows),
        "frozen_factory_handler_calls": 24,
        "format_once": "passed",
        "custom_context_renamed": "passed",
        "consumed_shared_outcomes": injected_calls,
    }


def entry_help(args) -> dict:
    destination = args.report.with_suffix(".entry-origins.json")
    require(not destination.exists(), "Refuse entry-point report overwrite")
    code = (
        "import sys,runpy,json,importlib.metadata as m\nfrom pathlib import Path\n"
        f"p=runpy.run_path({str(Path(__file__).resolve())!r})\n"
        f"p['load_guard'](Path({str(args.prepared)!r}))\n"
        "sys.argv=['friday-chat','--help']\n"
        "e=[x for x in m.distribution('friday-chat').entry_points if x.name=='friday-chat'][0]\n"
        "try:\n e.load()()\n"
        "except SystemExit as error:\n if error.code not in (None,0): raise\n"
        f"Path({str(destination)!r}).write_text(json.dumps(p['origins']())+'\\n')\n"
    )
    argv = [sys.executable, "-I", "-B", *(["-O"] * sys.flags.optimize), "-c", code]
    result = subprocess.run(
        argv, cwd=args.report.parent, text=True, capture_output=True
    )
    require(
        result.returncode == 0 and "Usage:" in result.stdout,
        "Installed Chat entry-point help failed: " + result.stderr,
    )
    return {
        "command": argv,
        "exit": result.returncode,
        "output": result.stdout,
        "stderr": result.stderr,
        "origins": json.loads(destination.read_text()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=("neutral", "chat"), required=True)
    for name in (
        "prepared",
        "source",
        "dist",
        "profile",
        "accepted-profile",
        "pilot-probe",
        "report",
    ):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    require(
        sys.flags.isolated == 1 and sys.dont_write_bytecode,
        "Use installed interpreter with -I -B",
    )
    require(not args.report.exists(), "Refuse report overwrite")
    require(
        args.report.resolve().is_relative_to(
            Path(os.environ["REVIEW_SCRATCH"]).resolve()
        ),
        "Report must be in private scratch",
    )
    bootstrap = load_guard(args.prepared)
    require(digest(args.pilot_probe) == PILOT_PROBE_SHA256, "Pinned pilot probe drift")
    require(
        Path(__file__).read_bytes()
        == (
            args.source
            / "docs/planning/active/command-refactor/validation/session/installed_probe.py"
        ).read_bytes(),
        "SESSION probe/source drift",
    )
    legacy = runpy.run_path(str(args.pilot_probe))
    installed = {
        re.sub(r"[-_.]+", "-", d.metadata["Name"]).lower(): d.version
        for d in metadata.distributions()
    }
    require(
        installed == profile_versions(args.profile),
        "Installed distribution closure differs from hashed profile",
    )
    if args.lane == "neutral":
        require(
            installed == {"friday-framework-commands": "0.1.0a4"},
            "Neutral closure changed",
        )
    else:
        require(
            installed == profile_versions(args.accepted_profile)
            and len(installed) == 138,
            "Default Chat closure differs from accepted profile",
        )
        require(
            not {
                "friday-framework-speech",
                "friday-framework-sandbox",
                "friday-framework-moltbook",
            }
            & installed.keys(),
            "Diagnostic extras installed",
        )
        require(
            not (Path(sys.prefix) / "bin/friday").exists()
            and not any(
                p.name == "friday"
                for p in metadata.entry_points(group="console_scripts")
            ),
            "Legacy executable installed",
        )
    report = {
        "lane": args.lane,
        "prefix": sys.prefix,
        "interpreter": sys.executable,
        "isolated": True,
        "optimized": sys.flags.optimize,
        "probe_sha256": digest(Path(__file__)),
        "pilot_probe_sha256": digest(args.pilot_probe),
        "guard_sha256": bootstrap["combined_guard_sha256"],
        "bootstrap_sha256": digest(args.prepared / "bootstrap.json"),
        "profile_sha256": digest(args.profile),
        "accepted_profile_sha256": digest(args.accepted_profile),
        "installed_distributions": installed,
        "environment": {
            name: os.environ.get(name)
            for name in (
                "REVIEW_REPO",
                "REVIEW_SCRATCH",
                "LITELLM_LOCAL_MODEL_COST_MAP",
                "PYTHONDONTWRITEBYTECODE",
                "ANONYMIZED_TELEMETRY",
                "FRIDAY_TELEMETRY_ENABLED",
                "GIT_OPTIONAL_LOCKS",
            )
        },
        "artifacts": {},
    }
    report["artifacts"]["commands"] = artifact_members(
        args, legacy, "friday-framework-commands", "friday_commands"
    )
    __import__("friday_commands")
    origins()
    if args.lane == "chat":
        report["artifacts"]["chat"] = artifact_members(
            args, legacy, "friday-chat", "friday_chat"
        )
        __import__("friday_chat")
        origins()
        report["behavior"] = asyncio.run(chat_behavior(args))
        report["entry_point_help"] = entry_help(args)
    else:
        report["behavior"] = asyncio.run(neutral_behavior())
    report["origins"] = origins()
    report["status"] = "passed"
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Installed SESSION {args.lane} proof passed; {len(installed)} distributions")


if __name__ == "__main__":
    main()
