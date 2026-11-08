"""Isolated installed DIAG aggregate proof; Git exports supply oracles only."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata as metadata
import json
import os
import re
import runpy
import sys
from contextlib import suppress
from dataclasses import asdict
from pathlib import Path
from types import MappingProxyType, SimpleNamespace
from unittest.mock import patch

SESSION_PROBE_SHA256 = (
    "059c1e4e392de1e00853e4acaadfe97f7a1eefe3f4d1de412ebf4970f07f15cd"
)
PILOT_PROBE_SHA256 = "8c1233a0a5181566bb188735358141e8718a5aaba205e6c4bfa3a2620a8e43ac"
DIAG_FIXTURE_SHA256 = "7f379e1060e79db61e37e7959efea89d6aa1ea198e4badfce8b26aa4964bf455"
NAMES = ("context", "prompt", "debug", "debug-budget", "timing", "debug-retrieval")
_SESSION = {}


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


def accepted_session(path: Path | None = None) -> dict:
    if not _SESSION:
        selected = (
            path or Path(__file__).resolve().parents[1] / "session/installed_probe.py"
        )
        require(digest(selected) == SESSION_PROBE_SHA256, "Pinned SESSION helper drift")
        _SESSION.update(runpy.run_path(str(selected)))
    return _SESSION


def load_guard(prepared: Path) -> dict:
    return accepted_session()["load_guard"](prepared)


def origins() -> dict:
    return accepted_session()["origins"]()


def artifact_members(args, legacy, distribution: str, package: str) -> dict:
    return accepted_session()["artifact_members"](args, legacy, distribution, package)


def json_value(value):
    # Normalize only the frozen capture's macOS root alias.
    return json.loads(json.dumps(value).replace("/private$EXPORT", "$EXPORT"))


async def retained_session_neutral_behavior() -> dict:
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
        "DiagnosticField",
        "ContextData",
        "PromptData",
        "DebugTurnData",
        "DebugData",
        "BudgetData",
        "TimingCounter",
        "TimingTurnData",
        "TimingData",
        "RetrievalData",
        "RetrievalUnavailableData",
        "DIAGNOSTIC_SPECS",
        "DiagnosticsPort",
        "build_diagnostic_handlers",
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


async def installed_diagnostic_observations(destination):
    import importlib.util
    from dataclasses import asdict
    from types import SimpleNamespace as NS

    from friday_chat.commands import registry as reg
    from friday_chat.commands.contracts import (
        CommandContext,
        CommandMetadata,
        CommandResult,
    )
    from friday_chat.commands.registry import CommandRegistry, build_default_registry

    rows = []
    marker = CommandMetadata("unused", "Unused", "unused", "/unused")
    export_owner = (
        importlib.import_module("friday_chat.commands.diagnostics")
        if importlib.util.find_spec("friday_chat.commands.diagnostics")
        else reg
    )
    # The caller supplies a fresh private pytest destination.
    if destination.exists():
        raise RuntimeError("Use a fresh export destination")
    destination.mkdir()
    events = []

    class Trace:
        def __init__(self, label, **values):
            object.__setattr__(self, "_label", label)
            self.__dict__.update(values)

        def __getattribute__(self, name):
            if not name.startswith("_"):
                events.append(object.__getattribute__(self, "_label") + "." + name)
            return object.__getattribute__(self, name)

    class Memory:
        def __init__(self, diagnostics=None, failure=None, entered=None, release=None):
            self.diagnostics, self.failure, self.entered, self.release = (
                diagnostics,
                failure,
                entered,
                release,
            )

        async def debug_retrieval(self, query):
            events.append("memory.debug_retrieval:" + query)
            if self.entered is not None:
                self.entered.set()
                await self.release.wait()
            if self.failure is not None:
                raise self.failure
            return self.diagnostics

    turn = NS(
        turn_ref="turn-2",
        outcome="ok",
        persistence="stored",
        completed_tools=2,
        failed_tools=0,
        duration_ms=1234.5,
    )
    execution = NS(
        turns=(NS(turn_ref="ignored"), turn),
        counters=(("z", "ok", 3), ("a", "failed", 1)),
    )

    def runtime(*, memory=None, telemetry=False, window=1000, buffer=100):
        return Trace(
            "runtime",
            tool_context="Tools: echo",
            memory=memory,
            telemetry=Trace(
                "telemetry",
                execution_snapshot=lambda: (
                    events.append("execution_snapshot") or execution
                ),
            )
            if telemetry
            else None,
            config=Trace(
                "config",
                memory=Trace("budget", context_window=window, output_buffer=buffer),
                chat=Trace("chat", system_prompt="Friday system"),
                transcript=NS(export_directory=str(destination)),
            ),
        )

    def context(**values):
        defaults = dict(
            runtime=None,
            history=[("user\n二", "answer")],
            last_context=None,
            last_prompt=None,
            last_debug={},
            last_timing={},
            exit_requested=False,
        )
        defaults.update(values)
        return Trace("context", **defaults)

    def normalize(value):
        if isinstance(value, str):
            return value.replace(str(destination), "$EXPORT")
        if isinstance(value, dict):
            return {k: normalize(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [normalize(v) for v in value]
        return value

    async def run(label, name, ctx, args=(), failure=None):
        events.clear()
        row = {"case": label, "command": name, "args": list(args)}
        before = {p.name: p.read_text() for p in destination.iterdir()}
        try:
            result = await getattr(reg, "_" + name.replace("-", "_") + "_handler")(
                ctx, args, marker
            )
            row["result"] = asdict(result)
        except BaseException as error:
            row["exception"] = {"type": type(error).__name__, "message": str(error)}
            if failure is not None:
                row["exception"]["same_object"] = error is failure
        row["events"] = list(events)
        row["files_before"] = before
        row["files_after"] = {p.name: p.read_text() for p in destination.iterdir()}
        rows.append(normalize(row))

    for name in ("context", "prompt"):
        for label, value in [
            ("none", None),
            ("empty", ""),
            ("cached", "stored\nÅ text"),
        ]:
            await run(
                name + ":" + label,
                name,
                context(**{"last_" + name: value}),
                ("ignored",),
            )
        await run(name + ":fallback-runtime", name, context(runtime=runtime()), ())
    for name in ("context", "prompt"):
        for label, value in [
            ("falsy-int", 0),
            ("falsy-list", []),
            ("truthy-int", 7),
            ("truthy-list", ["x"]),
        ]:
            await run(
                name + ":undeclared-cache:" + label,
                name,
                context(**{"last_" + name: value}),
            )
    for args in [
        ("--debug",),
        ("--debug", "--debug", "ignored"),
        ("--DEBUG",),
        ("--file", "--debug"),
        ("--file",),
    ]:
        await run(
            "context:flags:" + ",".join(args),
            "context",
            context(runtime=runtime(), last_context="Å\ntext"),
            args,
        )
    await run(
        "prompt:export",
        "prompt",
        context(runtime=runtime(), last_prompt="exact prompt\n"),
        ("--file", "--file", "../ignored"),
    )
    await run(
        "prompt:overwrite",
        "prompt",
        context(runtime=runtime(), last_prompt="replacement"),
        ("--file",),
    )
    for name in ("context", "prompt"):
        failure = OSError("synthetic export failure")

        def fail(*args, failure=failure):
            events.append("write_export")
            raise failure

        with patch.object(export_owner, "_write_export_file", fail):
            await run(
                name + ":export-failure",
                name,
                context(**{"last_" + name: "cached"}),
                ("--file",),
                failure,
            )
    for name, field, values in [
        ("debug", "last_debug", {"z": "last", "a": "first"}),
        ("timing", "last_timing", {"z": 0.0, "a": 0.12555}),
    ]:
        await run(name + ":empty", name, context(), ("ignored",))
        await run(name + ":fields", name, context(**{field: values}), ("ignored",))
        await run(
            name + ":telemetry",
            name,
            context(runtime=runtime(telemetry=True), **{field: values}),
        )
        await run(
            name + ":telemetry-only", name, context(runtime=runtime(telemetry=True))
        )
        await run(
            name + ":no-telemetry", name, context(runtime=runtime(), **{field: values})
        )
        await run(name + ":mixed-keys", name, context(**{field: {"a": 1, 2: 2}}))
    await run(
        "timing:invalid-value", "timing", context(last_timing={"bad": "not-a-number"})
    )
    await run(
        "debug:formatted-values",
        "debug",
        context(last_debug={"none": None, "flag": False, "items": ["x"]}),
    )
    for label, rt in [
        ("none", None),
        ("configured", runtime()),
        ("zero", runtime(window=0, buffer=0)),
        ("truthy-text", runtime(window="many", buffer="few")),
        ("negative", runtime(window=-1, buffer=-2)),
    ]:
        await run("budget:" + label, "debug-budget", context(runtime=rt), ("ignored",))
    rt = runtime()
    rt.config.memory = None
    await run("budget:memory-none", "debug-budget", context(runtime=rt))
    await run("retrieval:runtime-before-usage", "debug-retrieval", context())
    await run("retrieval:usage", "debug-retrieval", context(runtime=runtime()))
    for label, diagnostics in [
        ("empty", {}),
        (
            "details",
            {
                "snippets": ["one\n two", {"x": 1}, "x" * 170] * 4,
                "debug_info": {"z": None, "a": False},
            },
        ),
        ("wrong-containers", {"snippets": ("ignored",), "debug_info": ["ignored"]}),
        (
            "dict-subclass",
            type("D", (dict,), {})({"snippets": [], "debug_info": {"b": 2, "a": 1}}),
        ),
        ("mixed-keys", {"debug_info": {"a": 1, 2: 2}}),
        ("none", None),
    ]:
        await run(
            "retrieval:" + label,
            "debug-retrieval",
            context(runtime=runtime(memory=Memory(diagnostics))),
            ("hello", '"quoted', 'world"'),
        )
    for label, failure in [
        ("exception", RuntimeError("retrieval failed")),
        ("cancel", asyncio.CancelledError("cancelled")),
    ]:
        await run(
            "retrieval:" + label,
            "debug-retrieval",
            context(runtime=runtime(memory=Memory(failure=failure))),
            ("q",),
            failure,
        )
    entered, release = asyncio.Event(), asyncio.Event()
    memory = Memory({}, entered=entered, release=release)
    events.clear()
    task = asyncio.create_task(
        reg._debug_retrieval_handler(
            context(runtime=runtime(memory=memory)), ("wait",), marker
        )
    )
    try:
        await asyncio.wait_for(entered.wait(), 5)
        during = {"task_done": task.done(), "events": list(events)}
        release.set()
        result = await asyncio.wait_for(task, 5)
        rows.append(
            {
                "case": "retrieval:await",
                "during": during,
                "result": asdict(result),
                "events": list(events),
            }
        )
    finally:
        if not task.done():
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
    registry = build_default_registry()
    for text in [
        "/CONTEXT --debug extra",
        "/prompt extra",
        "/debug ignored",
        "/debug-budget extra",
        "/timing extra",
        "/debug-retrieval",
        '/debug-retrieval "a b" c',
        " /debug",
        "//context",
        "/ context",
    ]:
        ctx = CommandContext()
        handled, result = await registry.execute(text, ctx)
        rows.append(
            {
                "case": "dispatch:" + text,
                "handled": handled,
                "result": None if result is None else asdict(result),
            }
        )
    for name in (
        "context",
        "prompt",
        "debug",
        "debug-budget",
        "timing",
        "debug-retrieval",
    ):
        custom = CommandRegistry()

        async def own(*args):
            return CommandResult(output="custom")

        custom.register(name, description="Custom", category="custom", handler=own)
        handled, result = await custom.execute("/" + name, CommandContext())
        rows.append(
            {"case": "custom:" + name, "handled": handled, "result": asdict(result)}
        )
    return {
        "metadata": {name: asdict(registry.commands[name]) for name in NAMES},
        "cases": rows,
    }


async def neutral_diagnostics(args) -> dict:
    import friday_commands as api
    import friday_commands.diagnostics as shared

    fixture = (
        args.source
        / "packages/friday-commands/tests_commands/fixtures/diagnostics-metadata.json"
    )
    require(
        digest(fixture)
        == "71d61907f68708184ba9173b80ba1d07158a8814f24b1fd834166483ae86d765",
        "Neutral diagnostic fixture drift",
    )
    expected = json.loads(fixture.read_text())
    require(
        json_value({spec.name: asdict(spec) for spec in shared.DIAGNOSTIC_SPECS})
        == expected,
        "Installed diagnostic specs changed",
    )
    require(
        tuple(spec.name for spec in shared.DIAGNOSTIC_SPECS) == NAMES,
        "Diagnostic spec order changed",
    )
    require(api.CommandRegistry().specs() == (), "Registry implicitly populated")

    class NoReads:
        def __getattribute__(self, name):
            raise RuntimeError("Unexpected construction read: " + name)

    pure = shared.build_diagnostic_handlers(NoReads())
    require(
        type(pure) is MappingProxyType and tuple(pure) == NAMES,
        "Diagnostic handler map changed",
    )
    require(
        pure is not shared.build_diagnostic_handlers(NoReads()),
        "Factory reused a mutable/global map",
    )

    def mutate():
        pure["context"] = None

    expect_error(TypeError, mutate)

    values = (
        api.DiagnosticField("k", "v"),
        api.ContextData("context"),
        api.PromptData("prompt"),
        api.DebugTurnData("t", "ok", "stored", "2", "0"),
        api.DebugData(False),
        api.BudgetData(None, None),
        api.TimingCounter("tool", "ok", "2"),
        api.TimingTurnData("1.234", "ok", "stored"),
        api.TimingData(False),
        api.RetrievalData("q", 0),
        api.RetrievalUnavailableData("runtime_missing"),
    )
    for value in values:
        require(not hasattr(value, "__dict__"), "Diagnostic model lost slots")
        field = next(iter(value.__dataclass_fields__))
        expect_error(
            AttributeError,
            lambda value=value, field=field: setattr(value, field, "changed"),
        )
    for invalid in (True, -1):
        expect_error(
            TypeError if invalid is True else ValueError,
            lambda invalid=invalid: api.RetrievalData("q", invalid),
        )
        expect_error(
            TypeError if invalid is True else ValueError,
            lambda invalid=invalid: api.ContextData("x", invalid),
        )
    expect_error(
        ValueError, lambda: api.DebugData(False, (api.DiagnosticField("x", "y"),))
    )
    expect_error(
        ValueError,
        lambda: api.TimingData(False, (), api.TimingTurnData("0", "ok", "p")),
    )
    expect_error(ValueError, lambda: api.RetrievalData("q", 11, (), ("x",) * 11))
    expect_error(ValueError, lambda: api.RetrievalUnavailableData("other"))
    expect_error(TypeError, lambda: api.RetrievalData("q", 1, (object(),)))

    class FieldSubclass(api.DiagnosticField):
        pass

    expect_error(TypeError, lambda: api.DebugData(True, (FieldSubclass("k", "v"),)))
    nested = api.DebugTurnData("t", "ok", "p", "1", "0")
    expect_error(TypeError, lambda: api.CommandOutcome(nested))
    fields = [api.DiagnosticField("z", "last"), api.DiagnosticField("a", "first")]
    reads = []

    def snapshot():
        reads.append("iterated")
        yield from fields

    detached = api.DebugData(True, snapshot())
    fields.clear()
    require(
        reads == ["iterated"] and [f.key for f in detached.fields] == ["z", "a"],
        "Diagnostic snapshot changed",
    )

    class Text(str):
        pass

    text = Text("cached")
    require(api.ContextData(text).text is text, "Accepted string subclass coerced")

    def request(name, args=()):
        return api.CommandRequest(
            name, args, next(s for s in shared.DIAGNOSTIC_SPECS if s.name == name)
        )

    events = []

    class Port:
        def context_text(self):
            events.append("context")
            return "context"

        def prompt_text(self):
            events.append("prompt")
            return "prompt"

        def export_context(self, data):
            events.append("export_context")
            require(
                data == api.ContextData("context", 7),
                "Export lost count-before-write data",
            )
            return "context.txt"

        def export_prompt(self, data):
            events.append("export_prompt")
            require(data == api.PromptData("prompt"), "Prompt export data changed")
            return "prompt.txt"

        def debug_snapshot(self):
            events.append("debug")
            return detached

        def budget_snapshot(self):
            events.append("budget")
            return api.BudgetData(None, "-2")

        def timing_snapshot(self):
            events.append("timing")
            return api.TimingData(False)

        def retrieval_available(self):
            events.append("available")
            return True

        async def retrieve(self, query):
            events.append(("retrieve", query))
            return api.RetrievalData(query, 2, (), ("one", "two"))

    handlers = shared.build_diagnostic_handlers(Port())
    cases = {
        "context": (
            ("--file", "--debug", "--file"),
            ["context", "export_context"],
            api.ContextData("context", 7, "context.txt"),
        ),
        "prompt": (
            ("--debug", "--file"),
            ["prompt", "export_prompt"],
            api.PromptData("prompt", "prompt.txt"),
        ),
        "debug": (("ignored",), ["debug"], detached),
        "debug-budget": ((), ["budget"], api.BudgetData(None, "-2")),
        "timing": ((), ["timing"], api.TimingData(False)),
        "debug-retrieval": (
            ("quoted", "  spaces", "//q"),
            ["available", ("retrieve", "quoted   spaces //q")],
            api.RetrievalData("quoted   spaces //q", 2, (), ("one", "two")),
        ),
    }
    for name, (arguments, expected_calls, data) in cases.items():
        events.clear()
        result = await handlers[name](request(name, arguments), api.CommandExecution())
        require(
            result == api.CommandOutcome(data) and events == expected_calls,
            "Neutral diagnostic orchestration changed: " + name,
        )
    registry = api.CommandRegistry()
    for spec in shared.DIAGNOSTIC_SPECS:
        registry.register(spec, handlers[spec.name])
    require(
        registry.specs() == shared.DIAGNOSTIC_SPECS,
        "Explicit diagnostic registration changed",
    )
    for name in NAMES:
        events.clear()
        result = await registry.execute_text(
            "/" + name.upper() + " query", api.CommandExecution()
        )
        require(
            result.handled
            and result.outcome is not None
            and result.outcome.error is None
            and not result.outcome.ui_effects,
            "Installed neutral registry dispatch failed: " + name,
        )
    events.clear()
    events.clear()
    require(
        (
            await handlers["context"](
                request("context", ("--DEBUG", "--FILE")), api.CommandExecution()
            )
        ).data
        == api.ContextData("context"),
        "Flags became case insensitive",
    )
    require(events == ["context"], "Unrequested export happened")

    class InvocationSubclass(api.CommandExecution):
        pass

    for name in NAMES:
        for wrong_request, wrong_execution, kind in (
            (object(), object(), TypeError),
            (request(name), InvocationSubclass(), TypeError),
            (
                api.CommandRequest(
                    "other", (), api.CommandSpec("other", "Other", "test", "/other")
                ),
                api.CommandExecution(),
                ValueError,
            ),
        ):
            events.clear()
            try:
                await handlers[name](wrong_request, wrong_execution)
            except kind:
                pass
            else:
                raise RuntimeError("Missing exact invocation refusal: " + name)
            require(events == [], "Invalid request read a port")
    expect_error(TypeError, lambda: request("context", (1,)))

    class Invalid(Port):
        def debug_snapshot(self):
            return object()

        def budget_snapshot(self):
            return object()

        def timing_snapshot(self):
            return object()

        def retrieval_available(self):
            return 1

    for name in ("debug", "debug-budget", "timing", "debug-retrieval"):
        try:
            await shared.build_diagnostic_handlers(Invalid())[name](
                request(name), api.CommandExecution()
            )
        except TypeError:
            pass
        else:
            raise RuntimeError("Invalid port result accepted: " + name)
    failure = RuntimeError("unchanged retrieval failure")

    class Failed(Port):
        async def retrieve(self, query):
            raise failure

    try:
        await shared.build_diagnostic_handlers(Failed())["debug-retrieval"](
            request("debug-retrieval", ("q",)), api.CommandExecution()
        )
    except RuntimeError as error:
        require(error is failure, "Neutral failure identity changed")
    else:
        raise RuntimeError("Neutral retrieval failure swallowed")

    class Unavailable(NoReads):
        def __getattribute__(self, name):
            if name == "retrieval_available":
                return lambda: False
            return super().__getattribute__(name)

    result = await shared.build_diagnostic_handlers(Unavailable())["debug-retrieval"](
        request("debug-retrieval"), api.CommandExecution()
    )
    require(
        result.data == api.RetrievalUnavailableData("runtime_missing"),
        "Runtime-before-usage changed",
    )
    entered, release = asyncio.Event(), asyncio.Event()

    class Pending(Port):
        async def retrieve(self, query):
            events.append("memory.enter")
            entered.set()
            await release.wait()
            return api.RetrievalData(query, 0)

    task = asyncio.create_task(
        shared.build_diagnostic_handlers(Pending())["debug-retrieval"](
            request("debug-retrieval", ("wait",)), api.CommandExecution()
        )
    )
    try:
        await asyncio.wait_for(entered.wait(), 2)
        require(not task.done(), "Retrieval was not awaited")
        task.cancel("installed cancellation")
        try:
            await task
        except asyncio.CancelledError as error:
            require(str(error) == "installed cancellation", "Cancellation changed")
        else:
            raise RuntimeError("Retrieval cancellation swallowed")
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    require(
        not any(
            n.startswith("friday") and not n.startswith("friday_commands")
            for n in sys.modules
        ),
        "Neutral diagnostics imported host",
    )
    return {
        "models": 11,
        "specs": 6,
        "factory": "fresh immutable/no reads",
        "strict_order_export_await_cancel": "passed",
    }


async def chat_diagnostics(args) -> dict:
    import friday_commands as api
    import friday_commands.diagnostics as shared
    from friday_chat.commands import diagnostics as host
    from friday_chat.commands import registry as reg
    from friday_chat.commands.contracts import CommandResult

    fixture = (
        args.source
        / "packages/friday-chat/tests_chat/fixtures/diagnostics-baseline.json"
    )
    require(digest(fixture) == DIAG_FIXTURE_SHA256, "Diagnostic fixture drift")
    expected = json_value(json.loads(fixture.read_text()))
    actual = json_value(
        await installed_diagnostic_observations(
            args.report.with_suffix(".diagnostic-exports")
        )
    )
    require(
        actual["metadata"] == expected["metadata"],
        "Installed diagnostic metadata changed",
    )
    require(
        len(actual["cases"]) == len(expected["cases"]) == 72,
        "Diagnostic observation count changed",
    )
    refusals = 0
    for row, oracle in zip(actual["cases"], expected["cases"], strict=True):
        if ":undeclared-cache:truthy-" in oracle["case"]:
            require(
                row.get("exception", {}).get("type") == "TypeError"
                and "result" not in row,
                "Missing approved cache refusal",
            )
            row = {k: v for k, v in row.items() if k != "exception"}
            oracle = {k: v for k, v in oracle.items() if k != "result"}
            refusals += 1
        require(
            row == oracle, "Installed diagnostic observation changed: " + row["case"]
        )
    require(refusals == 4, "Approved refusal count changed")

    class Memory:
        async def debug_retrieval(self, query):
            return {"snippets": [query], "debug_info": {"z": 2, "a": 1}}

    destination = args.report.with_suffix(".shared-exports")
    runtime = SimpleNamespace(
        memory=Memory(),
        telemetry=None,
        tool_context="tools",
        config=SimpleNamespace(
            memory=SimpleNamespace(context_window=0, output_buffer=-2),
            chat=SimpleNamespace(system_prompt="System"),
            transcript=SimpleNamespace(export_directory=str(destination)),
        ),
    )
    context = reg.RegistryCommandContext(
        registry=reg.CommandRegistry(),
        runtime=runtime,
        history=[("u", "a")],
        last_context="current context",
        last_prompt="current prompt",
        last_debug={"z": "last", "a": "first"},
        last_timing={"z": 0.0, "a": 0.12555},
    )
    registry = reg.build_default_registry()
    original_factory, original_parse, original_request = (
        shared.build_diagnostic_handlers,
        reg._parse_command_input,
        host.CommandRequest,
    )
    factories, calls, parses, parsed, supplied = [], [], [], [], []

    def parse(text):
        parses.append(text)
        result = original_parse(text)
        parsed.append(result[1])
        return result

    def request(name, arguments, spec):
        supplied.append(arguments)
        return original_request(name, arguments, spec)

    def factory(port):
        require(port.context is context, "Wrong diagnostic context")
        factories.append(port)
        handlers = original_factory(port)

        def wrap(name):
            async def invoke(request, execution):
                require(
                    type(request) is api.CommandRequest
                    and type(execution) is api.CommandExecution,
                    "Wrong diagnostic request types",
                )
                require(
                    request.name == name
                    and request.spec
                    is next(s for s in shared.DIAGNOSTIC_SPECS if s.name == name),
                    "Noncanonical diagnostic request",
                )
                calls.append((name, request.args))
                return await handlers[name](request, execution)

            return invoke

        return {name: wrap(name) for name in handlers}

    injected = {
        "context": api.ContextData("shared context", 99, "shared-context"),
        "prompt": api.PromptData("shared prompt", "shared-prompt"),
        "debug": api.DebugData(True, (api.DiagnosticField("shared", "debug"),)),
        "debug-budget": api.BudgetData("shared-window", "shared-buffer"),
        "timing": api.TimingData(True, (api.DiagnosticField("shared", "9.876"),)),
        "debug-retrieval": api.RetrievalData(
            "shared-query", 97, (), ("shared-preview",)
        ),
    }
    expected_outputs = {
        "context": "shared context\n\nDebug:\n- characters: 99\n\nExported context to shared-context",
        "prompt": "shared prompt\n\nExported prompt to shared-prompt",
        "debug": "Debug information:\n- shared: debug",
        "debug-budget": "Token budget:\n- context_window: shared-window\n- output_buffer: shared-buffer",
        "timing": "Timing:\n- shared: 9.876s",
        "debug-retrieval": "Retrieval diagnostics:\n- query: shared-query\n- result_count: 97\nResults:\n- shared-preview",
    }
    with (
        patch.object(shared, "build_diagnostic_handlers", factory),
        patch.object(reg, "_parse_command_input", parse),
        patch.object(host, "CommandRequest", request),
    ):
        for name in NAMES:
            before = len(factories), len(calls), len(parses)
            text = "/" + name.upper() + ' "quoted words" //q'
            handled, result = await registry.execute(text, context)
            require(
                handled and result is not None, "Installed diagnostic dispatch failed"
            )
            require(
                (len(factories), len(calls), len(parses))
                == tuple(n + 1 for n in before),
                "Diagnostic did not delegate once: " + name,
            )
            require(
                supplied[-1] is parsed[-1]
                and calls[-1][1] == ('"quoted', 'words"', "//q"),
                "Original parsed arguments changed",
            )
            before = len(factories), len(calls), len(parses)
            await reg.BASIC_COMMAND_HANDLERS[name](context, (), object())
            require(
                (len(factories), len(calls), len(parses))
                == (before[0] + 1, before[1] + 1, before[2]),
                "Direct diagnostic wrapper reparsed or lost delegation",
            )
            renamed = reg.CommandRegistry()
            renamed.register(
                "renamed",
                description="Renamed",
                category="test",
                handler=reg.BASIC_COMMAND_HANDLERS[name],
            )
            before = len(factories), len(calls)
            await renamed.execute("/renamed extra", context)
            require(
                (len(factories), len(calls)) == (before[0] + 1, before[1] + 1)
                and calls[-1][0] == name,
                "Renamed diagnostic wrapper changed",
            )
        for name in NAMES:

            async def own(_context, _args, _metadata):
                return CommandResult("custom")

            custom = reg.CommandRegistry()
            custom.register(name, description="Custom", category="test", handler=own)
            before = len(factories), len(calls)
            require(
                (await custom.execute("/" + name, context))[1]
                == CommandResult("custom")
                and (len(factories), len(calls)) == before,
                "Custom diagnostic intercepted",
            )
        injected_calls = []

        def inject(port):
            def selected(name):
                async def invoke(request, execution):
                    injected_calls.append(name)
                    return api.CommandOutcome(injected[name])

                return invoke

            return {name: selected(name) for name in NAMES}

        with patch.object(shared, "build_diagnostic_handlers", inject):
            for name in NAMES:
                before = len(injected_calls)
                result = (await registry.execute("/" + name, context))[1]
                require(
                    result == CommandResult(expected_outputs[name])
                    and len(injected_calls) == before + 1,
                    "Shared diagnostic outcome ignored: " + name,
                )
        require(injected_calls == list(NAMES), "Injected invocation count changed")

    formats = []

    class Cached(str):
        def __format__(self, spec):
            formats.append(spec)
            require(len(formats) == 1, "Cached context formatted twice")
            return "formatted context"

    context.last_context = Cached("raw context")
    result = await reg.BASIC_COMMAND_HANDLERS["context"](
        context, ("--debug", "--file"), object()
    )
    body = "formatted context\n\nDebug:\n- characters: 11"
    require(
        formats == [""]
        and (destination / "friday_context.txt").read_bytes() == body.encode()
        and result.output
        == body
        + f"\n\nExported context to {(destination / 'friday_context.txt').resolve()}",
        "Context rendered body reuse changed",
    )
    for bad in (
        api.CommandOutcome(api.NoData()),
        api.CommandOutcome(
            api.ContextData("x"), ui_effects=(api.UiEffect.CLEAR_SCREEN,)
        ),
        api.CommandOutcome(error=api.CommandError("failed", "context")),
    ):
        expect_error(ValueError, lambda bad=bad: host.adapt_diagnostic_outcome(bad))

    class Tripwire:
        def __getattribute__(self, name):
            raise RuntimeError("Unexpected diagnostic context read: " + name)

    require(
        host.ChatDiagnosticsPort(Tripwire()).context is not None,
        "Port construction failed",
    )
    try:
        await reg.BASIC_COMMAND_HANDLERS["context"](Tripwire(), (1,), object())
    except TypeError:
        pass
    else:
        raise RuntimeError("Invalid direct args were accepted")
    return {
        "metadata": 6,
        "frozen_observations": 72,
        "exact": 68,
        "approved_refusals": refusals,
        "canonical_delegations": len(calls),
        "factory_calls": len(factories),
        "injected_consumed": injected_calls,
        "once_formatted_export": "passed",
        "custom_renamed_context": "passed",
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
        "session-probe",
        "report",
    ):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--revision", required=True)
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
    require(args.report.parent.is_dir(), "Report parent must exist")
    require(
        digest(args.session_probe) == SESSION_PROBE_SHA256,
        "Pinned SESSION helper drift",
    )
    require(digest(args.pilot_probe) == PILOT_PROBE_SHA256, "Pinned pilot helper drift")
    session = accepted_session(args.session_probe)
    bootstrap = load_guard(args.prepared)
    for actual, relative in (
        (Path(__file__), "diagnostics/installed_probe.py"),
        (args.session_probe, "session/installed_probe.py"),
        (args.pilot_probe, "pilot/installed_probe.py"),
    ):
        require(
            actual.read_bytes()
            == (
                args.source
                / "docs/planning/active/command-refactor/validation"
                / relative
            ).read_bytes(),
            "Probe/helper source drift: " + relative,
        )
    # Fallback exports remain private even if a command regresses around a patch.
    os.chdir(args.report.parent)
    legacy = runpy.run_path(str(args.pilot_probe))
    installed = {
        re.sub(r"[-_.]+", "-", d.metadata["Name"]).lower(): d.version
        for d in metadata.distributions()
    }
    require(
        installed == session["profile_versions"](args.profile),
        "Installed distribution closure differs from hashed profile",
    )
    if args.lane == "neutral":
        require(
            installed == {"friday-framework-commands": "0.1.0a4"},
            "Neutral closure changed",
        )
    else:
        require(
            installed == session["profile_versions"](args.accepted_profile)
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
        "revision": args.revision,
        "probe_sha256": digest(Path(__file__)),
        "pilot_probe_sha256": digest(args.pilot_probe),
        "session_probe_sha256": digest(args.session_probe),
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
        report["retained_SESSION"] = asyncio.run(session["chat_behavior"](args))
        report["diagnostics"] = asyncio.run(chat_diagnostics(args))
        report["entry_point_help"] = session["entry_help"](args)
        __import__("friday_tools")
        __import__("friday_finance")
    else:
        report["retained_SESSION"] = asyncio.run(retained_session_neutral_behavior())
        report["diagnostics"] = asyncio.run(neutral_diagnostics(args))
    report["origins"] = origins()
    report["status"] = "passed"
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Installed DIAG {args.lane} proof passed; {len(installed)} distributions")


if __name__ == "__main__":
    main()
