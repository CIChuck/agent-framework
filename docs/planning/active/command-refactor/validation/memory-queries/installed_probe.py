"""Isolated installed MEMQ aggregate proof; Git exports supply oracles only."""

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


async def retained_memq_session_neutral_behavior() -> dict:
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
        "MemoryWarningData",
        "MemoryMetricData",
        "MemorySectionData",
        "MemoryStatisticsData",
        "MemoryRecordData",
        "MemoryRecordsData",
        "MemoryQueryFailedData",
        "MemoryUnavailableData",
        "GraphEntityData",
        "GraphRelationshipData",
        "GraphData",
        "IngestedDocumentData",
        "IngestedDocumentsData",
        "MEMORY_QUERY_SPECS",
        "MemoryQueryPort",
        "build_memory_query_handlers",
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


async def retained_memq_neutral_diagnostics(args) -> dict:
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

        def context_debug_snapshot(self):
            # A deliberately different count proves shared code never re-measures.
            events.append("context_debug")
            return api.ContextData("context", 42)

        def prompt_text(self):
            events.append("prompt")
            return "prompt"

        def export_context(self, data):
            events.append("export_context")
            require(
                data == api.ContextData("context", 42),
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
            ["context_debug", "export_context"],
            api.ContextData("context", 42, "context.txt"),
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
        registry.specs()
        == tuple(sorted(shared.DIAGNOSTIC_SPECS, key=lambda spec: spec.name)),
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

    for snapshot, kind in (
        (None, TypeError),
        ("context", TypeError),
        (api.PromptData("context"), TypeError),
        (type("Child", (api.ContextData,), {})("context", 7), TypeError),
        (api.ContextData("context"), ValueError),
        (api.ContextData("context", 7, "path"), ValueError),
    ):

        class Snapshot(Port):
            def context_debug_snapshot(self, snapshot=snapshot):
                events.append("context_debug")
                return snapshot

        for arguments in (("--debug",), ("--debug", "--file")):
            events.clear()
            error = None
            try:
                await shared.build_diagnostic_handlers(Snapshot())["context"](
                    request("context", arguments), api.CommandExecution()
                )
            except Exception as caught:
                error = caught
            require(
                type(error) is kind and events == ["context_debug"],
                "Invalid context debug snapshot accepted",
            )

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


async def retained_memq_chat_diagnostics(args) -> dict:
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
    for index, flags in enumerate((("--debug",), ("--file", "--debug", "--debug"))):
        for kind in ("grows", "format-raises", "length-raises-after-format"):
            trace, formatted = [], []
            format_failure = RuntimeError("format sentinel")
            length_failure = LookupError("length sentinel")

            class Stateful(str):
                failures = (format_failure, length_failure)

                def __len__(self, kind=kind, trace=trace, formatted=formatted):
                    trace.append("len")
                    if formatted and kind == "length-raises-after-format":
                        raise self.failures[1]
                    require(
                        not (formatted and kind == "format-raises"),
                        "Length measured after a failed format",
                    )
                    return 99 if formatted else 3

                def __format__(self, spec, kind=kind, trace=trace, formatted=formatted):
                    trace.append("format")
                    formatted.append(spec)
                    if kind == "format-raises":
                        raise self.failures[0]
                    return "xyz"

            order = args.report.with_suffix(f".context-order-{index}-{kind}")
            ordered = reg.RegistryCommandContext(
                registry=reg.CommandRegistry(),
                runtime=SimpleNamespace(
                    config=SimpleNamespace(
                        transcript=SimpleNamespace(export_directory=str(order))
                    )
                ),
                last_context=Stateful("abc"),
            )
            error, result = None, None
            try:
                result = await reg.BASIC_COMMAND_HANDLERS["context"](
                    ordered, flags, object()
                )
            except Exception as caught:
                error = caught
            if kind == "grows":
                body = "xyz\n\nDebug:\n- characters: 99"
                if "--file" in flags:
                    target = order / "friday_context.txt"
                    require(
                        target.read_bytes() == body.encode(),
                        "Format-then-length export changed",
                    )
                    body += f"\n\nExported context to {target.resolve()}"
                require(
                    error is None
                    and result == CommandResult(body)
                    and trace == ["len", "format", "len"],
                    "Legacy format-then-length evaluation changed",
                )
                continue
            require(
                error is (format_failure if kind == "format-raises" else length_failure)
                and trace
                == (
                    ["len", "format"]
                    if kind == "format-raises"
                    else ["len", "format", "len"]
                )
                and not order.exists(),
                "Legacy context evaluation failure order changed",
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
        "format_then_length_order": "passed",
        "custom_renamed_context": "passed",
    }


FIXTURE_SHA256 = "3b512406d989e7d114fdcc17ac270eaccb3bcf772dc09a15fd566b10afeb6ea7"
DIAG_PROBE_SHA256 = "c943d7070aeae2624444a165a9c3f77f3317c062e06376b3d0f89e089d70db58"
MEMQ_NAMES = ("memory", "insights", "summaries", "meta", "entities", "list-ingested")


async def retained_memq_session_chat_behavior(args) -> dict:
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
            if count:
                if "args" in row:
                    expected_args = tuple(row["args"])
                elif case.startswith("renamed:"):
                    expected_args = ("extra",)
                else:
                    expected_args = {
                        'dispatch:/history "quoted words"': ('"quoted', 'words"'),
                        "dispatch:/HiStOrY ignored": ("ignored",),
                        "dispatch:/clear ignored": ("ignored",),
                        "dispatch:/ClEaR\tmore": ("more",),
                    }.get(case, ())
                require(
                    calls[-1][1] == expected_args,
                    "Shared session arguments changed: " + case,
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


async def neutral_memory_queries(args) -> dict:
    import friday_commands as api
    import friday_commands.contracts as contracts
    import friday_commands.memory_queries as shared

    fixture = (
        args.source
        / "packages/friday-commands/tests_commands/fixtures/memory-query-metadata.json"
    )
    require(
        digest(fixture)
        == "a2b848e67b1ee033e22d22a5e1c96a672979e674f5b1ec0fd9e82f6f7aee6480",
        "MEMQ neutral fixture drift",
    )
    require(
        json_value({s.name: asdict(s) for s in shared.MEMORY_QUERY_SPECS})
        == json.loads(fixture.read_text()),
        "MEMQ metadata changed",
    )
    require(
        tuple(s.name for s in shared.MEMORY_QUERY_SPECS) == MEMQ_NAMES,
        "MEMQ spec order changed",
    )
    exports = (
        "MemoryWarningData",
        "MemoryMetricData",
        "MemorySectionData",
        "MemoryStatisticsData",
        "MemoryRecordData",
        "MemoryRecordsData",
        "MemoryQueryFailedData",
        "MemoryUnavailableData",
        "GraphEntityData",
        "GraphRelationshipData",
        "GraphData",
        "IngestedDocumentData",
        "IngestedDocumentsData",
        "MEMORY_QUERY_SPECS",
        "MemoryQueryPort",
        "build_memory_query_handlers",
    )
    for name in exports:
        require(
            getattr(api, name)
            is getattr(contracts if name in exports[:13] else shared, name),
            "MEMQ export owner changed: " + name,
        )
    require(api.CommandRegistry().specs() == (), "MEMQ implicitly populated registry")
    values = [
        api.MemoryWarningData("component", "reason"),
        api.MemoryMetricData("key", "available", "0"),
        api.MemorySectionData("section"),
        api.MemoryStatisticsData(),
        api.MemoryRecordData(None, "text", None),
        api.MemoryRecordsData("insight"),
        api.MemoryQueryFailedData("summary"),
        api.MemoryUnavailableData("runtime_missing"),
        api.GraphEntityData("entity", "type", "0"),
        api.GraphRelationshipData("a", "rel", "b", "False"),
        api.GraphData(),
        api.IngestedDocumentData("path", "0", ""),
        api.IngestedDocumentsData(),
    ]
    expected_fields = [
        ("component", "reason"),
        ("key", "state", "value", "reason"),
        ("title", "metrics"),
        ("sections", "warnings"),
        (
            "record_id",
            "text",
            "collection",
            "lifecycle_stage",
            "created_at",
            "confidence",
            "source_count",
            "provenance_source_type",
            "source_memory_ids",
            "provenance_truncated",
            "verification",
        ),
        ("kind", "records", "warnings", "complete"),
        ("kind",),
        ("reason",),
        ("label", "node_type", "hit_count"),
        ("source", "relation", "target", "hit_count"),
        ("entities", "relationships"),
        ("source_path", "chunk_count", "description"),
        ("documents", "warnings"),
    ]
    for value, fields in zip(values, expected_fields, strict=True):
        require(
            tuple(value.__dataclass_fields__) == fields
            and not hasattr(value, "__dict__"),
            "MEMQ model layout changed",
        )
        expect_error(
            AttributeError,
            lambda value=value, field=fields[0]: setattr(value, field, "changed"),
        )
    metric = api.MemoryMetricData("key", "available", "0")
    warning = api.MemoryWarningData("z", "reason")
    events = []

    def sequence():
        events.append("iterated")
        yield metric
        yield metric

    section = api.MemorySectionData("section", sequence())
    require(
        events == ["iterated"] and section.metrics == (metric, metric),
        "MEMQ snapshot lost order/duplicates or iterated twice",
    )
    source = [section]
    stats = api.MemoryStatisticsData(source, [warning, warning])
    source.clear()
    require(
        stats.sections == (section,) and stats.warnings == (warning, warning),
        "MEMQ data retained mutable input",
    )
    record = api.MemoryRecordData(None, "text", None)
    entity = api.GraphEntityData("a", "type", "0")
    relationship = api.GraphRelationshipData("a", "r", "b", "0")
    document = api.IngestedDocumentData("path", "1", "description")
    require(
        len(api.IngestedDocumentsData([document] * 101).documents) == 101,
        "MEMQ document listing acquired cap",
    )

    class Text(str):
        pass

    text = Text("Unicode π")
    require(
        api.MemoryRecordData(None, text, None).text is text,
        "MEMQ accepted string subclass coerced",
    )

    class MetricChild(api.MemoryMetricData):
        pass

    class RecordsChild(api.MemoryRecordsData):
        pass

    invalid = [
        (ValueError, lambda: api.MemoryMetricData("k", "unknown")),
        (ValueError, lambda: api.MemoryMetricData("k", "available")),
        (ValueError, lambda: api.MemoryMetricData("k", "available", "0", "reason")),
        (ValueError, lambda: api.MemoryMetricData("k", "unavailable")),
        (
            ValueError,
            lambda: api.MemoryMetricData("k", "not_configured", "0", "reason"),
        ),
        (TypeError, lambda: api.MemoryMetricData("k", "available", False)),
        (
            TypeError,
            lambda: api.MemorySectionData("s", [MetricChild("k", "available", "1")]),
        ),
        (TypeError, lambda: api.MemoryStatisticsData([object()])),
        (TypeError, lambda: api.MemoryStatisticsData(warnings=[object()])),
        (ValueError, lambda: api.MemoryRecordsData("wrong")),
        (ValueError, lambda: api.MemoryRecordsData("insight", [record] * 101)),
        (ValueError, lambda: api.MemoryRecordsData("meta_insight", [record])),
        (
            ValueError,
            lambda: api.MemoryRecordsData(
                "insight", [api.MemoryRecordData("id", "text", None)]
            ),
        ),
        (TypeError, lambda: api.MemoryRecordsData("insight", complete=1)),
        (
            TypeError,
            lambda: api.MemoryRecordData(None, "text", None, provenance_truncated=0),
        ),
        (
            TypeError,
            lambda: api.MemoryRecordData(None, "text", None, source_memory_ids=[False]),
        ),
        (ValueError, lambda: api.MemoryQueryFailedData("other")),
        (ValueError, lambda: api.MemoryUnavailableData("other")),
        (TypeError, lambda: api.GraphEntityData("a", "type", 0)),
        (TypeError, lambda: api.GraphRelationshipData("a", "r", "b", False)),
        (TypeError, lambda: api.GraphData([object()])),
        (ValueError, lambda: api.GraphData([entity] * 101)),
        (ValueError, lambda: api.GraphData(relationships=[relationship] * 101)),
        (TypeError, lambda: api.IngestedDocumentData("path", 1, "")),
        (TypeError, lambda: api.IngestedDocumentsData([object()])),
        (TypeError, lambda: api.CommandOutcome(metric)),
        (TypeError, lambda: api.CommandOutcome(RecordsChild("insight"))),
    ]
    for kind, action in invalid:
        expect_error(kind, action)
    for missing in ("unavailable", "not_configured"):
        require(
            api.MemoryMetricData("k", missing, reason="reason").value is None,
            "MEMQ missing state changed",
        )
    meta = api.MemoryRecordData("id", "text", "short", source_memory_ids=["a", "a"])
    require(
        api.MemoryRecordsData("meta_insight", [meta]).records == (meta,),
        "MEMQ meta model changed",
    )

    class NoReads:
        def __getattribute__(self, name):
            raise RuntimeError("Unexpected MEMQ construction read: " + name)

    pure = shared.build_memory_query_handlers(NoReads())
    require(
        type(pure) is MappingProxyType
        and tuple(pure) == MEMQ_NAMES
        and pure is not shared.build_memory_query_handlers(NoReads()),
        "MEMQ factory map changed",
    )

    def mutate():
        pure["memory"] = None

    expect_error(TypeError, mutate)
    specs = {s.name: s for s in shared.MEMORY_QUERY_SPECS}

    def request(name, arguments=()):
        return api.CommandRequest(name, arguments, specs[name])

    class Port:
        def __init__(self):
            self.events = []
            self.available = True
            self.failure = None
            self.result = None
            self.gate = None
            self.entered = None

        def memory_available(self):
            self.events.append("available")
            return self.available

        async def query(self, name, *arguments):
            self.events.append((name, arguments))
            if self.entered is not None:
                self.entered.set()
            if self.gate is not None:
                await self.gate.wait()
            if self.failure is not None:
                raise self.failure
            return self.result

        async def memory_statistics(self):
            return await self.query("statistics")

        async def memory_records(self, kind):
            return await self.query("records", kind)

        async def graph_snapshot(self, name, relationships):
            return await self.query("graph", name, relationships)

        async def ingested_documents(self):
            return await self.query("documents")

    results = {
        "memory": stats,
        "insights": api.MemoryRecordsData("insight", [record]),
        "summaries": api.MemoryRecordsData("summary", [record]),
        "meta": api.MemoryRecordsData("meta_insight", [meta]),
        "entities": api.GraphData([entity], [relationship]),
        "list-ingested": api.IngestedDocumentsData([document]),
    }
    calls = {
        "memory": ("statistics", ()),
        "insights": ("records", ("insight",)),
        "summaries": ("records", ("summary",)),
        "meta": ("records", ("meta_insight",)),
        "entities": ("graph", (None, True)),
        "list-ingested": ("documents", ()),
    }

    async def refuse(kind, action, identity=None):
        try:
            await action()
        except kind as error:
            require(
                identity is None or error is identity, "MEMQ failure identity changed"
            )
            return
        raise RuntimeError("Missing MEMQ async refusal: " + kind.__name__)

    pending = 0
    for name in MEMQ_NAMES:
        port = Port()
        port.result = results[name]
        handler = shared.build_memory_query_handlers(port)[name]
        outcome = await handler(request(name), api.CommandExecution())
        require(
            outcome.data is port.result
            and outcome.error is None
            and outcome.ui_effects == ()
            and port.events == ["available", calls[name]],
            "MEMQ single capability/result consumption changed: " + name,
        )
        for bad_request, bad_execution, kind in [
            (object(), object(), TypeError),
            (request(name), object(), TypeError),
            (
                request("summaries" if name != "summaries" else "insights"),
                api.CommandExecution(),
                ValueError,
            ),
        ]:
            port.events.clear()
            await refuse(
                kind,
                lambda handler=handler,
                bad_request=bad_request,
                bad_execution=bad_execution: handler(bad_request, bad_execution),
            )
            require(not port.events, "MEMQ validation read port too early")
        expect_error(TypeError, lambda name=name: request(name, (1,)))
        for arguments in [(), ("ignored",), ("nodes",), ("NODES",)]:
            port.available = False
            port.events.clear()
            outcome = await handler(request(name, arguments), api.CommandExecution())
            require(
                outcome.data == api.MemoryUnavailableData("runtime_missing")
                and port.events == ["available"],
                "MEMQ availability precedence changed",
            )
        port.available = 0
        await refuse(
            TypeError,
            lambda handler=handler, name=name: handler(
                request(name), api.CommandExecution()
            ),
        )
        port.available = True
        port.result = object()
        await refuse(
            TypeError,
            lambda handler=handler, name=name: handler(
                request(name), api.CommandExecution()
            ),
        )
        port.result = results[name]
        for marker in [
            RuntimeError("MEMQ failure"),
            asyncio.CancelledError("MEMQ cancellation"),
        ]:
            port.failure = marker
            port.events.clear()
            await refuse(
                type(marker),
                lambda handler=handler, name=name: handler(
                    request(name), api.CommandExecution()
                ),
                marker,
            )
            require(
                port.events == ["available", calls[name]],
                "MEMQ failure retried or added effects",
            )
        port.failure = None
        port.gate = asyncio.Event()
        port.entered = asyncio.Event()
        port.events.clear()
        task = asyncio.create_task(handler(request(name), api.CommandExecution()))
        try:
            await asyncio.wait_for(port.entered.wait(), 5)
            require(
                not task.done() and port.events == ["available", calls[name]],
                "MEMQ did not await capability once",
            )
            port.gate.set()
            require(
                (await asyncio.wait_for(task, 5)).data is results[name],
                "MEMQ pending result changed",
            )
            pending += 1
        finally:
            if not task.done():
                task.cancel()
            with suppress(asyncio.CancelledError):
                await task
    port = Port()
    handlers = shared.build_memory_query_handlers(port)
    for command, kind in [
        ("insights", "insight"),
        ("summaries", "summary"),
        ("meta", "meta_insight"),
    ]:
        for data in [
            api.MemoryRecordsData("summary" if kind != "summary" else "insight"),
            api.MemoryQueryFailedData("summary" if kind != "summary" else "insight"),
        ]:
            port.result = data
            await refuse(
                ValueError,
                lambda command=command: handlers[command](
                    request(command), api.CommandExecution()
                ),
            )
    for arguments, name, include in [
        (("nodes", "ignored"), None, False),
        (("NODES",), "NODES", True),
        (('"Ada', 'Lovelace"'), '"Ada Lovelace"', True),
    ]:
        port.result = api.GraphData([entity])
        port.events.clear()
        await handlers["entities"](
            request("entities", arguments), api.CommandExecution()
        )
        require(
            port.events == ["available", ("graph", (name, include))],
            "MEMQ graph selection changed",
        )
    port.result = api.GraphData([entity], [relationship])
    await refuse(
        ValueError,
        lambda: handlers["entities"](
            request("entities", ("nodes",)), api.CommandExecution()
        ),
    )
    require(
        all(
            not name.startswith(("friday_chat", "friday_memory", "friday_core"))
            for name in sys.modules
        ),
        "Neutral MEMQ imported host/framework",
    )
    return {
        "models": 13,
        "strict_refusals": len(invalid),
        "exact_exports": 54,
        "factory_map": "fresh immutable lazy",
        "commands": list(MEMQ_NAMES),
        "pending_capabilities": pending,
        "failure_and_cancel_identity": "passed",
        "kind_and_nodes_refusals": "passed",
        "optimized_invariants": sys.flags.optimize,
    }


async def installed_persisted_listing(args) -> dict:
    import builtins

    from friday_chat import adapters
    from friday_chat.adapters import FrameworkEmbeddingService, FrameworkMemoryAdapter
    from friday_chat.commands.contracts import CommandContext
    from friday_chat.commands.registry import build_default_registry
    from friday_chat.config import FridayChatConfig
    from friday_chat.runtime import build_runtime
    from friday_llm import LiteLLMEmbeddingService

    class Embeddings(LiteLLMEmbeddingService):
        def __init__(self):
            pass

        async def embed_query(self, text):
            checksum = sum(text.encode())
            return [float(checksum % 101) / 101, float((checksum * 7) % 103) / 103]

        async def embed_documents(self, texts):
            return [await self.embed_query(text) for text in texts]

    root = args.report.with_suffix(".persisted-memory")
    root.mkdir()
    config = FridayChatConfig.model_validate(
        {
            "llm": {
                "model": "openai/memq-installed-no-provider",
                "api_key": "provider-prohibited",
            },
            "embedding": {
                "model": "openai/memq-installed-local",
                "api_key": "provider-prohibited",
            },
            "memory": {
                "persist_directory": str(root / "vector"),
                "context_window": 4096,
                "output_buffer": 512,
                "priming": {"enabled": True, "previous_sessions": 2},
            },
            "transcript": {"export_directory": str(root / "transcript")},
            "maintenance": {
                "backup_directory": str(root / "recovery"),
                "logging": {"log_directory": str(root / "logs")},
            },
            "lifecycle": {
                "enabled": True,
                "access_buffer": {
                    "enabled": True,
                    "wal_path": str(root / "access-buffer.wal"),
                },
            },
            "tools": {"enabled": False},
        }
    )
    with patch.object(
        adapters,
        "build_framework_embedding_service",
        lambda _config: FrameworkEmbeddingService(service=Embeddings()),
    ):
        runtime = build_runtime(config, fake=False, session_id="memq-installed-real")
    require(
        type(runtime.memory) is FrameworkMemoryAdapter,
        "Installed real adapter not selected",
    )
    for path in runtime.maintenance_layout.all_declared_paths:
        require(
            path.resolve().is_relative_to(args.report.parent.resolve()),
            "Persisted proof escaped private report root",
        )
    memory = runtime.memory
    manager = memory.collection_manager
    registry = build_default_registry()
    context = CommandContext(runtime=runtime)

    async def command(text):
        handled, result = await registry.execute(text, context)
        require(
            handled and result is not None, "Installed persisted command not dispatched"
        )
        return result.output

    single = root / "a.txt"
    multi = root / "z.txt"
    single.write_text("single installed chunk")
    multi.write_text("many words for installed persisted chunks.\n" * 500)
    require(
        "Ingested file:" in await command("/ingest " + str(single) + " base"),
        "Installed single ingest failed",
    )
    require(
        "Ingested file:" in await command("/ingest " + str(multi) + " desc"),
        "Installed multi ingest failed",
    )
    first = await manager.short_term.get_all(
        limit=None, where={"type": "ingested_file"}
    )
    single_count = sum(row["metadata"]["source"] == str(single) for row in first)
    multi_count = sum(row["metadata"]["source"] == str(multi) for row in first)
    require(
        single_count == 1 and multi_count > 1,
        "Installed chunk fixture did not exercise single/multi records",
    )
    require(
        "Ingested file:" in await command("/ingest " + str(multi) + " desc"),
        "Installed re-ingest failed",
    )
    stored = await manager.short_term.get_all(
        limit=None, where={"type": "ingested_file"}
    )
    require(
        sum(row["metadata"]["source"] == str(multi) for row in stored)
        == 2 * multi_count,
        "Installed re-ingest count changed",
    )
    require(await manager.promote_memory(stored[0]["id"]), "Installed promotion failed")
    for description in ["B", "A"]:
        await memory.ingest_document(
            source_path=str(single),
            description=description,
            content="additional installed chunk",
        )
    require(
        await manager.add_to_short_term(
            ["absent description", "empty description"],
            [
                {"type": "ingested_file", "source": str(single)},
                {"type": "ingested_file", "source": str(single), "description": ""},
            ],
            ids=["memq-absent", "memq-empty"],
        ),
        "Installed persisted metadata setup failed",
    )
    before = [
        await store.get_all(limit=None, where={"type": "ingested_file"})
        for store in (manager.short_term, manager.long_term)
    ]
    expected = [
        (str(single), None, 1),
        (str(single), "", 1),
        (str(single), "A", 1),
        (str(single), "B", 1),
        (str(single), "base", 1),
        (str(multi), "desc", 2 * multi_count),
    ]
    original_open, original_stat = builtins.open, os.stat

    def no_source_open(path, *a, **kw):
        require(
            str(path) not in {str(single), str(multi)},
            "Listing opened an ingested source file",
        )
        return original_open(path, *a, **kw)

    def no_source_stat(path, *a, **kw):
        require(
            str(path) not in {str(single), str(multi)},
            "Listing inspected an ingested source path",
        )
        return original_stat(path, *a, **kw)

    async def no_decayed(*a, **kw):
        raise RuntimeError("Listing read decayed collection")

    with (
        patch.object(manager.decayed, "get_all", no_decayed),
        patch.object(builtins, "open", no_source_open),
        patch.object(os, "stat", no_source_stat),
    ):
        data = await memory.query_ingested_documents()
        output = await command("/list-ingested ignored words")
    require(
        [(d.source_path, d.description, d.chunk_count) for d in data.documents]
        == expected
        and data.warnings == (),
        "Installed persisted grouping/count/order changed",
    )
    require(
        output
        == "\n".join(
            ["Ingested documents:"]
            + [
                f"- {source} ({count} chunks): {description or ''}"
                for source, description, count in expected
            ]
        ),
        "Installed persisted rendering ignored typed records",
    )
    after = [
        await store.get_all(limit=None, where={"type": "ingested_file"})
        for store in (manager.short_term, manager.long_term)
    ]
    require(before == after, "Installed listing changed persisted records")
    return {
        "adapter": "FrameworkMemoryAdapter",
        "single_chunks": single_count,
        "multi_chunks": multi_count,
        "reingest_chunks": 2 * multi_count,
        "promotion": True,
        "groups": [{"source": p, "description": d, "count": n} for p, d, n in expected],
        "empty_and_absent_separate": True,
        "no_source_or_decayed_reads": True,
        "read_only_records": True,
        "output": output,
    }


async def chat_memory_queries(args) -> dict:
    import friday_commands as api
    import friday_commands.memory_queries as shared
    from friday_chat.commands import memory_queries as host
    from friday_chat.commands import registry as reg
    from friday_chat.commands.contracts import CommandContext, CommandResult
    from friday_chat.config import FridayChatConfig
    from friday_chat.memory_views import MemoryRecordKind, MemoryRecordQueryResult
    from friday_chat.runtime import FakeMemoryController, build_runtime

    fixture = (
        args.source
        / "packages/friday-chat/tests_chat/fixtures/memory-query-baseline.json"
    )
    require(
        digest(fixture)
        == "0403471ba7bc293320e0dc2d0420c01859ec67b706f35f4cfd631ea9be47a272",
        "Installed MEMQ Chat fixture drift",
    )
    expected = json.loads(fixture.read_text())
    registry = reg.build_default_registry()
    require(
        len(registry.canonical_names()) == 41
        and registry.command_names() - registry.canonical_names()
        == {"q", "quit", "clearscreen"},
        "Installed MEMQ registry surface changed",
    )
    require(
        json_value({name: asdict(registry.commands[name]) for name in MEMQ_NAMES})
        == expected["metadata"],
        "Installed MEMQ metadata/help changed",
    )
    for name in MEMQ_NAMES:
        result = (
            await registry.execute(
                "/help " + name, reg.RegistryCommandContext(registry=registry)
            )
        )[1]
        require(
            result is not None
            and name in result.output
            and registry.commands[name].description in result.output,
            "Installed MEMQ focused help changed",
        )
    config = FridayChatConfig.model_validate(
        {
            "llm": {"model": "fake/memq-installed"},
            "transcript": {
                "export_directory": str(
                    args.report.with_suffix(".memq-fake-transcript")
                )
            },
            "tools": {"enabled": False},
        }
    )
    runtime = build_runtime(config, fake=True, session_id="memq-installed-fake")
    memory = runtime.memory
    require(type(memory) is FakeMemoryController, "Installed fake adapter changed")
    memory.insights = [{"text": "installed insight"}]
    memory.summaries = [{"text": "installed summary"}]
    memory.ingested_documents = [
        {"source_path": "z", "description": None, "chunk_count": 0},
        {"source_path": "a", "description": "fact", "chunk_count": 3},
    ]
    context = reg.RegistryCommandContext(registry=registry, runtime=runtime)
    factory = shared.build_memory_query_handlers
    parser = reg._parse_command_input
    adapter = host.adapt_memory_query_outcome
    factories = []
    calls = []
    parsed = []
    outcomes = []
    consumed = []
    supplied_args = []

    def parse(text):
        value = parser(text)
        parsed.append((text, value))
        return value

    def construct(name, arguments, spec):
        supplied_args.append(arguments)
        return api.CommandRequest(name, arguments, spec)

    def build(port):
        require(port.context is context, "Installed MEMQ factory lost context")
        factories.append(port)
        handlers = factory(port)

        def select(name):
            async def execute(request, execution):
                require(
                    type(request) is api.CommandRequest
                    and type(execution) is api.CommandExecution
                    and request.name == name
                    and request.spec
                    is next(s for s in shared.MEMORY_QUERY_SPECS if s.name == name),
                    "Installed MEMQ invocation identity changed",
                )
                require(
                    supplied_args[-1] is parsed[-1][1][1]
                    and request.args == parsed[-1][1][1],
                    "Installed MEMQ reparsed or changed args before request snapshot",
                )
                calls.append((name, request.args))
                outcome = await handlers[name](request, execution)
                outcomes.append(outcome)
                return outcome

            return execute

        return {name: select(name) for name in handlers}

    def consume(outcome):
        consumed.append(outcome)
        return adapter(outcome)

    outputs = {}
    with (
        patch.object(shared, "build_memory_query_handlers", build),
        patch.object(reg, "_parse_command_input", parse),
        patch.object(host, "CommandRequest", construct),
        patch.object(host, "adapt_memory_query_outcome", consume),
    ):
        for name in MEMQ_NAMES:
            before = len(factories), len(calls), len(parsed), len(consumed)
            handled, result = await registry.execute(
                "/" + name.upper() + ' extra "quoted words"', context
            )
            require(
                handled
                and result is not None
                and (len(factories), len(calls), len(parsed), len(consumed))
                == tuple(v + 1 for v in before),
                "Installed MEMQ not once per canonical dispatch",
            )
            require(
                consumed[-1] is outcomes[-1] and result == adapter(outcomes[-1]),
                "Installed MEMQ ignored real outcome",
            )
            outputs[name] = result.output
    require(
        type(outcomes[0].data) is api.MemoryStatisticsData
        and len(outcomes[0].data.sections) == 8
        and sum(len(s.metrics) for s in outcomes[0].data.sections) == 24,
        "Installed MEMQ statistics projection changed",
    )
    require(
        outputs["insights"] == "Insights:\n- installed insight"
        and outputs["summaries"] == "Summaries:\n- installed summary",
        "Installed MEMQ record rendering changed",
    )
    require(
        outputs["list-ingested"]
        == "Ingested documents:\n- z (0 chunks): \n- a (3 chunks): fact",
        "Installed fake listing order/counts changed",
    )
    injected = {
        "memory": api.MemoryStatisticsData(
            [
                api.MemorySectionData(
                    "Injected", [api.MemoryMetricData("zero", "available", "0")]
                )
            ]
        ),
        "insights": api.MemoryRecordsData(
            "insight", [api.MemoryRecordData(None, "injected insight", None)]
        ),
        "summaries": api.MemoryRecordsData(
            "summary", [api.MemoryRecordData(None, "injected summary", None)]
        ),
        "meta": api.MemoryQueryFailedData("meta_insight"),
        "entities": api.GraphData([api.GraphEntityData("graph fact", "kind", "0")]),
        "list-ingested": api.IngestedDocumentsData(
            [api.IngestedDocumentData("injected-source", "17", "fact")]
        ),
    }
    expected_outputs = {
        "memory": "Memory statistics:\nInjected:\n- zero: 0",
        "insights": "Insights:\n- injected insight",
        "summaries": "Summaries:\n- injected summary",
        "meta": "Unable to query meta insights: store read failed.",
        "entities": "Entities:\n- graph fact (kind), hits=0",
        "list-ingested": "Ingested documents:\n- injected-source (17 chunks): fact",
    }
    injections = []

    def inject(port):
        factories.append(port)
        handlers = factory(port)

        def select(name):
            async def execute(request, execution):
                calls.append((name, request.args))
                await handlers[name](request, execution)
                injections.append(name)
                return api.CommandOutcome(injected[name])

            return execute

        return {name: select(name) for name in handlers}

    with patch.object(shared, "build_memory_query_handlers", inject):
        for name in MEMQ_NAMES:
            result = (await registry.execute("/" + name, context))[1]
            require(
                result == CommandResult(expected_outputs[name]),
                "Installed shared injected outcome ignored: " + name,
            )
    require(
        injections == list(MEMQ_NAMES),
        "Installed injected handlers not called exactly once",
    )
    renamed = []
    custom = []
    with patch.object(shared, "build_memory_query_handlers", inject):
        for name in MEMQ_NAMES:
            alias = reg.CommandRegistry()
            alias.register(
                "renamed-" + name,
                description="renamed",
                category="test",
                handler=reg.BASIC_COMMAND_HANDLERS[name],
            )
            before = len(injections)
            result = (await alias.execute("/renamed-" + name + " literal", context))[1]
            require(
                len(injections) == before + 1
                and injections[-1] == name
                and result == CommandResult(expected_outputs[name]),
                "Installed renamed MEMQ wrapper lost canonical identity",
            )
            renamed.append(name)

            async def own(_context, _args, _metadata):
                return CommandResult("custom MEMQ")

            selected = reg.CommandRegistry()
            selected.register(name, description="Custom", category="test", handler=own)
            before = len(factories)
            result = (await selected.execute("/" + name, context))[1]
            require(
                result == CommandResult("custom MEMQ") and len(factories) == before,
                "Installed custom MEMQ intercepted",
            )
            custom.append(name)
    for name in MEMQ_NAMES:
        for arguments in ["", " nodes ignored"]:
            result = (await registry.execute("/" + name + arguments, CommandContext()))[
                1
            ]
            require(
                result == CommandResult("Memory runtime is not initialized."),
                "Installed MEMQ unavailable precedence changed",
            )

    class Tripwire:
        def __getattribute__(self, name):
            raise RuntimeError("Unexpected installed MEMQ context read: " + name)

    require(
        host.ChatMemoryQueryPort(Tripwire()).context is not None,
        "Installed MEMQ construction read context",
    )
    try:
        await host.invoke_memory_query("insights", (1,), Tripwire())
    except TypeError:
        pass
    else:
        raise RuntimeError("Installed MEMQ accepted non-string arguments")
    for bad in [
        api.CommandOutcome(api.NoData()),
        api.CommandOutcome(
            api.MemoryStatisticsData(), ui_effects=(api.UiEffect.CLEAR_SCREEN,)
        ),
        api.CommandOutcome(error=api.CommandError("failed", "MEMQ")),
    ]:
        expect_error(ValueError, lambda bad=bad: adapter(bad))
    entered = asyncio.Event()
    release = asyncio.Event()
    events = []

    async def delayed(kind):
        events.append(kind)
        entered.set()
        await release.wait()
        return MemoryRecordQueryResult(kind=MemoryRecordKind.INSIGHT, records=())

    with patch.object(memory, "query_memory_records", delayed):
        task = asyncio.create_task(registry.execute("/insights", context))
        try:
            await asyncio.wait_for(entered.wait(), 5)
            require(
                not task.done() and events == [MemoryRecordKind.INSIGHT],
                "Installed Chat MEMQ did not await query once",
            )
            release.set()
            await asyncio.wait_for(task, 5)
        finally:
            if not task.done():
                task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    async def error(_kind):
        raise RuntimeError("sensitive store failure")

    with patch.object(memory, "query_memory_records", error):
        require(
            (await registry.execute("/insights", context))[1]
            == CommandResult("Unable to query insights: store read failed."),
            "Installed Chat MEMQ error conversion changed",
        )
    marker = asyncio.CancelledError("installed MEMQ identity")

    async def cancelled(_kind):
        raise marker

    with patch.object(memory, "query_memory_records", cancelled):
        try:
            await registry.execute("/insights", context)
        except asyncio.CancelledError as caught:
            require(
                caught is marker, "Installed Chat MEMQ cancellation identity changed"
            )
        else:
            raise RuntimeError("Installed Chat MEMQ swallowed cancellation")
    persisted = await installed_persisted_listing(args)
    return {
        "metadata": 6,
        "canonical_delegations": 6,
        "factory_calls": len(factories),
        "handler_calls": len(calls),
        "injected_consumed": list(MEMQ_NAMES),
        "renamed": renamed,
        "custom": custom,
        "availability_precedence": "passed",
        "pending_error_cancel": "passed",
        "pure_adapter_refusals": "passed",
        "canonical_outputs": outputs,
        "persisted_listing": persisted,
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
        "diagnostics-probe",
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
    require(
        digest(args.diagnostics_probe) == DIAG_PROBE_SHA256, "Pinned DIAG helper drift"
    )
    session = accepted_session(args.session_probe)
    bootstrap = load_guard(args.prepared)
    for actual, relative in (
        (Path(__file__), "memory-queries/installed_probe.py"),
        (args.diagnostics_probe, "diagnostics/installed_probe.py"),
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
        "diagnostics_probe_sha256": digest(args.diagnostics_probe),
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
    report["neutral_memory_queries"] = asyncio.run(neutral_memory_queries(args))
    if args.lane == "chat":
        report["artifacts"]["chat"] = artifact_members(
            args, legacy, "friday-chat", "friday_chat"
        )
        __import__("friday_chat")
        origins()
        report["retained_SESSION"] = asyncio.run(
            retained_memq_session_chat_behavior(args)
        )
        report["retained_DIAG"] = asyncio.run(retained_memq_chat_diagnostics(args))
        report["memory_queries"] = asyncio.run(chat_memory_queries(args))
        report["entry_point_help"] = session["entry_help"](args)
        __import__("friday_tools")
        __import__("friday_finance")
    else:
        report["retained_SESSION"] = asyncio.run(
            retained_memq_session_neutral_behavior()
        )
        report["retained_DIAG"] = asyncio.run(retained_memq_neutral_diagnostics(args))
        report["memory_queries"] = report["neutral_memory_queries"]
    report["origins"] = origins()
    report["status"] = "passed"
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Installed MEMQ {args.lane} proof passed; {len(installed)} distributions")


if __name__ == "__main__":
    main()
