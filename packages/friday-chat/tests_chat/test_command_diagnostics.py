"""Frozen diagnostics compatibility, shared ownership and host-effect boundaries.

Synthetic capture helpers below retain the frozen pre-migration scenarios. They
exercise real handlers; provenance and Git-export machinery stay in external
validation, and expected observations live with the tests.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from contextlib import suppress
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch

import friday_commands.diagnostics as shared
import pytest
from friday_chat.app import FridayChatApp, ListInputSource, ListOutputSink
from friday_chat.commands import diagnostics as host
from friday_chat.commands import registry as reg
from friday_chat.commands.contracts import (
    CommandContext,
    CommandMetadata,
    CommandResult,
)
from friday_chat.commands.registry import (
    CommandRegistry,
    RegistryCommandContext,
    build_default_registry,
)
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import FakeMemoryController, build_runtime
from friday_commands import (
    BudgetData,
    CommandError,
    CommandExecution,
    CommandOutcome,
    CommandRequest,
    ContextData,
    DebugData,
    DebugTurnData,
    DiagnosticField,
    ExitData,
    HelpData,
    HistoryData,
    NoData,
    PromptData,
    RetrievalData,
    RetrievalUnavailableData,
    SessionClearedData,
    TimingCounter,
    TimingData,
    TimingTurnData,
    UiEffect,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures/diagnostics-baseline.json"
FIXTURE = json.loads(FIXTURE_PATH.read_text())
SESSION_FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures_session/session-baseline.json").read_text()
)
MARKER = CommandMetadata("unused", "Unused", "unused", "/unused")
NAMES = ("context", "prompt", "debug", "debug-budget", "timing", "debug-retrieval")


def _json(value):
    # The frozen capture used macOS /var while resolve() emitted /private/var.
    # Canonicalize that root alias only; file contents and relative paths stay exact.
    return json.loads(json.dumps(value).replace("/private$EXPORT", "$EXPORT"))


def _handler(name):
    return reg.BASIC_COMMAND_HANDLERS[name]


RETIRED = (
    "clear-tools",
    "inject-tools",
    "recommend-tools",
    "run-tool",
    "tool-budget",
    "inject-payload",
    "prime",
    "set",
    "vars",
)

# Frozen canonical observation digests keep all 196 comparisons package-local.
PILOT_EXPECTED = {
    "custom": (61, "8e9ecb696c7b770dd0ea9d83405694d1409f90b65de2e2e2ae9bf8aa826cf8a6"),
    "dispatch": (
        29,
        "fc28fc94960a93e821455904a13403685b9b9f032ad068fa149413ad33ba2594",
    ),
    "help": (62, "6ef53fe41b6e9af4af5a1a563b0f8e195d27eab1223907fa8f57e705d2949df5"),
    "lifecycle": (
        3,
        "4c03d20417b5e2878a0df8743db3a397e0fada135d220dca52ae3d93687f54b7",
    ),
    "metadata": (
        41,
        "2ed6f11c0a54ddb17a10475cbb415bc50bc21fd24b00dba6f1a16c81fdabe56f",
    ),
}


async def _capture_diagnostics(destination):
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


async def _capture_session():
    from friday_chat.commands.contracts import CommandContext, CommandMetadata
    from friday_chat.commands.registry import (
        CommandRegistry,
        _clear_handler,
        _history_handler,
        build_default_registry,
    )

    rows = []
    marker = CommandMetadata("unused", "Unused", "unused", "/unused")

    class History(list):
        def __init__(self, values, events, failure=None):
            super().__init__(values)
            self.events = events
            self.failure = failure

        def clear(self):
            self.events.append("history.clear")
            if self.failure is not None:
                raise self.failure
            super().clear()

    class Context:
        def __init__(self, history, events, runtime=None, runtime_failure=None):
            self.history = history
            self.events = events
            self._runtime = runtime
            self.runtime_failure = runtime_failure
            self.exit_requested = False

        @property
        def runtime(self):
            self.events.append("runtime.read")
            if self.runtime_failure is not None:
                raise self.runtime_failure
            return self._runtime

    class Memory:
        def __init__(self, history, events, returned=True, failure=None):
            self.history, self.events, self.returned, self.failure = (
                history,
                events,
                returned,
                failure,
            )

        async def clear_session_memory(self):
            self.events.append("memory.clear:history=" + json.dumps(self.history))
            if self.failure is not None:
                raise self.failure
            return self.returned

    class Runtime:
        def __init__(self, memory):
            self.memory = memory

    def result(value):
        data = asdict(value)
        data["ui_effects"] = [effect.value for effect in value.ui_effects]
        return data

    for label, turns in [
        ("empty", []),
        ("one", [("hello", "world")]),
        ("ordered", [("second", "B"), ("first", "A")]),
        ("unicode-newlines", [("Å\nuser", "答\nreply")]),
        ("formatted-values", [(False, None), (7, ["x"])]),
        ("malformed-short", [("only-one",)]),
        ("malformed-long", [("a", "b", "c")]),
    ]:
        events = []
        history = History(turns, events)
        context = Context(
            history, events, runtime_failure=RuntimeError("history touched runtime")
        )
        row = {
            "case": "history:" + label,
            "turns": turns,
            "args": ["ignored", '"quoted"'],
        }
        try:
            row["result"] = result(
                await _history_handler(context, tuple(row["args"]), marker)
            )
        except Exception as error:
            row["exception"] = {"type": type(error).__name__, "message": str(error)}
        row["events"], row["history_after"] = events, list(history)
        rows.append(row)

    for label in [
        "no-runtime",
        "memory-true",
        "memory-false",
        "memory-exception",
        "memory-cancel",
        "history-exception",
        "runtime-exception",
    ]:
        events = []
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
            returned=label != "memory-false",
            failure=failure if label in ("memory-exception", "memory-cancel") else None,
        )
        context = Context(
            history,
            events,
            None if label == "no-runtime" else Runtime(memory),
            failure if label == "runtime-exception" else None,
        )
        row = {"case": "clear:" + label, "args": ["ignored"]}
        try:
            row["result"] = result(await _clear_handler(context, ("ignored",), marker))
        except BaseException as error:
            row["exception"] = {
                "type": type(error).__name__,
                "message": str(error),
                "same_object": error is failure,
            }
        row["events"], row["history_after"] = events, list(history)
        rows.append(row)

    events = []
    history = History([("hello", "world")], events)
    entered, release = asyncio.Event(), asyncio.Event()

    class BlockingMemory:
        async def clear_session_memory(self):
            events.append("memory.enter")
            entered.set()
            await release.wait()
            events.append("memory.return")
            return False

    task = asyncio.create_task(
        _clear_handler(Context(history, events, Runtime(BlockingMemory())), (), marker)
    )
    await asyncio.wait_for(entered.wait(), 2)
    during = {
        "history": list(history),
        "task_done": task.done(),
        "events": list(events),
    }
    release.set()
    completed = await asyncio.wait_for(task, 2)
    rows.append(
        {
            "case": "clear:await-order",
            "during_await": during,
            "result": result(completed),
            "events": events,
        }
    )

    registry = build_default_registry()
    for text in [
        "/history",
        "/HiStOrY ignored",
        '/history "quoted words"',
        "/clear ignored",
        "/ClEaR\tmore",
        "//history",
        "/ history",
        " /clear",
    ]:
        context = CommandContext(history=[("hello", "world")])
        handled, response = await registry.execute(text, context)
        rows.append(
            {
                "case": "dispatch:" + text,
                "handled": handled,
                "result": None if response is None else result(response),
                "history_after": context.history,
                "exit_requested": context.exit_requested,
            }
        )

    for name, handler in [("history", _history_handler), ("clear", _clear_handler)]:
        custom = CommandRegistry()
        custom.register(
            "renamed", description="Renamed", category="test", handler=handler
        )
        context = CommandContext(history=[("hello", "world")])
        handled, response = await custom.execute("/renamed extra", context)
        rows.append(
            {
                "case": "renamed:" + name,
                "handled": handled,
                "result": result(response),
                "history_after": context.history,
            }
        )

    return {
        "metadata": {
            name: asdict(registry.commands[name]) for name in ("clear", "history")
        },
        "cases": rows,
    }


async def _capture_pilot():
    from friday_chat.app import FridayChatApp, ListInputSource, ListOutputSink
    from friday_chat.commands.registry import (
        CommandArgument,
        CommandContext,
        CommandRegistry,
        CommandResult,
        RegistryCommandContext,
        _exit_handler,
        _help_handler,
        build_default_registry,
    )
    from friday_chat.commands.session import cls_handler
    from friday_chat.config import FridayChatConfig
    from friday_chat.runtime import build_runtime

    registry = build_default_registry()
    if len(registry.canonical_names()) != 41 or len(registry.command_names()) != 44:
        raise RuntimeError("Expected the accepted 41-name, three-alias surface")
    names = sorted(registry.command_names())
    focuses = [
        None,
        "",
        " ",
        False,
        0,
        [],
        *names,
        *RETIRED,
        "unknown-pilot-name",
        "/q",
        "//q",
    ]
    help_rows = [
        {"focus": focus, "output": registry.render_help(focus)} for focus in focuses
    ]
    inputs = [
        "ordinary text",
        " /help",
        "/",
        "/ HELP",
        "//HELP",
        "///HELP",
        "/ /HELP",
        "/HeLp",
        "/help\tq",
        "/help\nq",
        "/help q",
        "/help /q",
        "/help //q",
        "/help exit ignored",
        '/help "exit ignored"',
        "/exit",
        "/quit extra",
        "/q",
        "/cls extra",
        "/clearscreen",
        *("/" + name for name in RETIRED),
    ]
    dispatch = []
    for text in inputs:
        context = RegistryCommandContext(registry=registry)
        handled, result = await registry.execute(text, context)
        dispatch.append(
            {
                "input": text,
                "handled": handled,
                "output": None if result is None else result.output,
                "result_handled": None if result is None else result.handled,
                "exit": None if result is None else result.exit_requested,
                "effects": []
                if result is None
                else [effect.value for effect in result.ui_effects],
                "context_exit": context.exit_requested,
            }
        )

    custom = []

    def custom_help(label: str, argument: CommandArgument) -> None:
        selected = CommandRegistry()
        selected.register(
            "inspect",
            description="Inspect item.",
            category="utility",
            arguments=(argument,),
            aliases=("show",),
        )
        for focus in (None, "inspect", "show", "absent"):
            try:
                value = {"output": selected.render_help(focus)}
            except (TypeError, ValueError) as error:
                value = {"exception": type(error).__name__}
            custom.append({"case": label, "focus": focus, **value})

    for label, kwargs in (
        ("numeric-default", {"default": 7}),
        ("truthy-required", {"required": "yes"}),
        ("falsy-required", {"required": 0}),
        ("list-choices", {"choices": ["text", "json"]}),
        ("string-choices", {"choices": "ab"}),
        ("mapping-choices", {"choices": {"text": 1, "json": 2}}),
        ("invalid-choice", {"choices": ("text", 7)}),
    ):
        # Intentionally invalid static types characterize the permissive legacy API.
        custom_help(label, CommandArgument("format", "Output format.", **kwargs))
    selected = CommandRegistry()
    selected.register("safe", description="Safe.", category="utility")
    selected.register(
        "bad",
        description="Bad.",
        category="utility",
        arguments=(CommandArgument("arg", "Argument.", choices=(7,)),),
    )
    for focus in ("safe", "unknown"):
        custom.append(
            {
                "case": "unrelated-bad-entry",
                "focus": focus,
                "output": selected.render_help(focus),
            }
        )
    for name, aliases in ((" /odd ", ("",)), ("plain", (" /ALIAS ",))):
        selected = CommandRegistry()
        selected.register(name, description="Odd.", category="utility", aliases=aliases)
        for focus in (None, "", " ", " /odd ", "/alias", " //ALIAS "):
            custom.append(
                {
                    "case": "normalization",
                    "name": name,
                    "focus": focus,
                    "output": selected.render_help(focus),
                }
            )
    empty = CommandRegistry()
    custom.append({"case": "empty-catalog", "output": empty.render_help()})

    async def sentinel(_context, args, metadata):
        return CommandResult(output=f"custom:{metadata.name}:{args!r}")

    for name in ("help", "exit", "cls", *RETIRED):
        selected = CommandRegistry()
        selected.register(
            name, description="Custom.", category="custom", handler=sentinel
        )
        _, result = await selected.execute("/" + name + " extra")
        custom.append({"case": "custom-handler", "name": name, "output": result.output})
    for name, handler in (
        ("renamed-help", _help_handler),
        ("renamed-exit", _exit_handler),
        ("renamed-cls", cls_handler),
    ):
        selected = CommandRegistry()
        selected.register(
            name, description="Wrapper.", category="custom", handler=handler
        )
        for context in (CommandContext(), RegistryCommandContext(registry=empty)):
            _, result = await selected.execute("/" + name, context)
            custom.append(
                {
                    "case": "wrapper-context",
                    "name": name,
                    "registry_context": isinstance(context, RegistryCommandContext),
                    "output": result.output,
                    "exit": result.exit_requested,
                    "effects": [effect.value for effect in result.ui_effects],
                }
            )

    async def capture_lifecycle(display_kind):
        events = []
        config = FridayChatConfig.model_validate({"llm": {"model": "fake/pilot-probe"}})
        runtime = build_runtime(config, fake=True, session_id="pilot-frozen-probe")
        original_close = runtime.async_clients.close

        async def close():
            events.append("close_clients")
            await original_close()

        runtime.async_clients.close = close

        class Output(ListOutputSink):
            async def write(self, text):
                events.append("output:" + text)
                await super().write(text)

        class Display:
            def render_banner(self, **_kwargs):
                pass

            def prompt_text(self, **_kwargs):
                return "User: "

            def create_heartbeat(self, _kind):
                return self

            def start(self):
                pass

            def stop(self):
                pass

            def clear_screen(self):
                events.append("clear")
                if display_kind == "failed":
                    raise RuntimeError("private display detail")

        output = Output()
        app = FridayChatApp(
            runtime=runtime,
            input_source=ListInputSource(["/cls", "/clearscreen", "/q"]),
            output_sink=output,
            display=None if display_kind == "missing" else Display(),
        )
        result = await app.run()
        return {
            "display": display_kind,
            "events": events,
            "output": output.values,
            "result": asdict(result),
            "context_exit": app.command_context.exit_requested,
            "started": app.started,
            "background_closed": app.background.closed,
            "client_close_count": runtime.async_clients.close_calls,
            "transcript_finalized": runtime.transcript.finalized,
        }

    lifecycle = [
        await capture_lifecycle(kind) for kind in ("available", "missing", "failed")
    ]
    return {
        "metadata": {
            name: asdict(value) for name, value in sorted(registry.commands.items())
        },
        "help": help_rows,
        "dispatch": dispatch,
        "custom": custom,
        "lifecycle": lifecycle,
    }


@pytest.mark.asyncio
async def test_diagnostic_metadata_and_frozen_cases(tmp_path, monkeypatch):
    # Fallback file paths remain private even if a mutant bypasses the patched writer.
    monkeypatch.chdir(tmp_path)
    assert (
        hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest()
        == "7f379e1060e79db61e37e7959efea89d6aa1ea198e4badfce8b26aa4964bf455"
    )
    registry = build_default_registry()
    assert len(registry.canonical_names()) == 41
    assert registry.command_names() - registry.canonical_names() == {
        "q",
        "quit",
        "clearscreen",
    }
    assert len(reg.DEFAULT_COMMAND_SPECS) == 39
    for name in NAMES:
        assert _json(asdict(registry.commands[name])) == FIXTURE["metadata"][name]
        assert (
            _json(asdict(host.diagnostic_metadata(name))) == FIXTURE["metadata"][name]
        )
    actual = _json(await _capture_diagnostics(tmp_path / "exports"))
    assert actual["metadata"] == FIXTURE["metadata"]
    assert len(actual["cases"]) == len(FIXTURE["cases"]) == 72
    refusals = 0
    for row, expected in zip(actual["cases"], _json(FIXTURE["cases"]), strict=True):
        if ":undeclared-cache:truthy-" in expected["case"]:
            assert row["exception"]["type"] == "TypeError"
            assert "result" not in row
            expected = {
                key: value for key, value in expected.items() if key != "result"
            }
            row = {key: value for key, value in row.items() if key != "exception"}
            refusals += 1
        assert row == expected, row["case"]
    assert refusals == 4
    assert _json(await _capture_session()) == SESSION_FIXTURE
    pilot = _json(await _capture_pilot())
    assert set(pilot) == set(PILOT_EXPECTED)
    for group, (count, digest) in PILOT_EXPECTED.items():
        assert len(pilot[group]) == count
        assert (
            hashlib.sha256(
                json.dumps(pilot[group], sort_keys=True).encode()
            ).hexdigest()
            == digest
        ), group


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.asyncio
async def test_diagnostic_once_only_delegation(monkeypatch, name):
    parser, factory = reg._parse_command_input, shared.build_diagnostic_handlers
    parses, parsed_args, supplied_args, ports, calls, actual_outcomes = (
        [],
        [],
        [],
        [],
        [],
        [],
    )
    payloads = {
        "context": ContextData("injected context", 17, "injected-context"),
        "prompt": PromptData("injected prompt", "injected-prompt"),
        "debug": DebugData(True, (DiagnosticField("injected", "debug"),)),
        "debug-budget": BudgetData("injected-window", "injected-buffer"),
        "timing": TimingData(True, (DiagnosticField("injected", "9.876"),)),
        "debug-retrieval": RetrievalData(
            "injected-query", 97, (), ("injected-preview",)
        ),
    }
    injected = CommandOutcome(payloads[name])

    def parse(text):
        parses.append(text)
        parsed = parser(text)
        parsed_args.append(parsed[1])
        return parsed

    def request(command_name, args, spec):
        supplied_args.append(args)
        return CommandRequest(command_name, args, spec)

    def build(port):
        ports.append(port)
        handlers = factory(port)

        async def selected(request, execution):
            calls.append((request, execution))
            actual_outcomes.append(await handlers[name](request, execution))
            return injected

        return {name: selected}

    monkeypatch.setattr(reg, "_parse_command_input", parse)
    monkeypatch.setattr(host, "CommandRequest", request)
    monkeypatch.setattr(shared, "build_diagnostic_handlers", build)
    context = RegistryCommandContext(registry=CommandRegistry())
    text = "/" + name.upper() + ' "quoted words" //q'
    handled, result = await build_default_registry().execute(text, context)
    assert handled and result == host.adapt_diagnostic_outcome(injected)
    assert parses == [text]
    assert len(calls) == len(ports) == len(actual_outcomes) == 1
    assert supplied_args[0] is parsed_args[0]
    request_value, execution = calls[0]
    assert type(request_value) is CommandRequest and type(execution) is CommandExecution
    assert request_value.name == name and request_value.args == (
        '"quoted',
        'words"',
        "//q",
    )
    assert request_value.spec is next(
        spec for spec in shared.DIAGNOSTIC_SPECS if spec.name == name
    )
    assert ports[0].context is context
    # A renamed wrapper retains its fixed command and uses the supplied context.
    renamed = CommandRegistry()
    renamed.register(
        "renamed", description="Renamed", category="test", handler=_handler(name)
    )
    assert (await renamed.execute("/renamed extra", context))[1] == result
    assert len(calls) == len(ports) == 2 and calls[-1][0].name == name
    parses.clear()
    assert await _handler(name)(context, (), object()) == result
    assert parses == [] and len(calls) == len(ports) == 3

    class Tripwire:
        def __getattribute__(self, attr):
            pytest.fail("Unexpected context read: " + attr)

    tripwire = Tripwire()
    assert host.ChatDiagnosticsPort(tripwire).context is tripwire
    before = len(ports)
    with pytest.raises(TypeError):
        await _handler(name)(tripwire, (1,), object())
    assert len(ports) == before

    async def own(context, args, metadata):
        return CommandResult("custom:" + metadata.name)

    monkeypatch.setattr(
        shared,
        "build_diagnostic_handlers",
        lambda port: pytest.fail("custom delegated"),
    )
    custom = CommandRegistry()
    custom.register(name, description="Own", category="test", handler=own)
    assert (await custom.execute("/" + name, CommandContext()))[1] == CommandResult(
        "custom:" + name
    )


class _Trace:
    def __init__(self, events, label, **values):
        object.__setattr__(self, "_events", events)
        object.__setattr__(self, "_label", label)
        self.__dict__.update(values)

    def __getattribute__(self, name):
        if not name.startswith("_"):
            object.__getattribute__(self, "_events").append(
                object.__getattribute__(self, "_label") + "." + name
            )
        return object.__getattribute__(self, name)


class _Formatted:
    def __init__(self, events, label, text="formatted", failure=None):
        self.events, self.label, self.text, self.failure = events, label, text, failure

    def __bool__(self):
        self.events.append(self.label + ".bool")
        return True

    def __format__(self, spec):
        self.events.append(self.label + ".format:" + spec)
        if self.failure is not None:
            raise self.failure

        class String(str):
            def __str__(self):
                raise AssertionError("Formatted string converted twice")

            def __format__(self, spec):
                raise AssertionError("Formatted string formatted twice")

        return String(self.text)


async def _check_cached_context_formatting(directory):
    """Accepted, stateful string formatting must match legacy in each flag path."""
    for index, flags in enumerate(
        (
            (),
            ("--debug",),
            ("--file",),
            ("--debug", "--file"),
            ("--file", "--debug"),
            ("--debug", "--file", "--debug", "--file"),
        )
    ):
        calls = []

        class Cached(str):
            def __format__(self, spec, calls=calls):
                calls.append(spec)
                if len(calls) > 1:
                    raise RuntimeError("cached text formatted twice")
                return "formatted text"

        target_root = directory / str(index)
        context = CommandContext(
            last_context=Cached("cached text"),
            runtime=NS(config=NS(transcript=NS(export_directory=str(target_root)))),
        )
        error, result = None, None
        try:
            result = await _handler("context")(context, flags, MARKER)
        except BaseException as caught:
            error = caught
        assert error is None, f"Accepted cached text must format once: {error!r}"
        assert calls == ([""] if "--debug" in flags or "--file" in flags else [])
        body = (
            "formatted text\n\nDebug:\n- characters: 11"
            if "--debug" in flags
            else "cached text"
        )
        if "--file" in flags:
            target = (target_root / "friday_context.txt").resolve()
            assert target.read_bytes() == body.encode("utf-8")
            displayed = body if "--debug" in flags else "formatted text"
            assert result == CommandResult(
                displayed + f"\n\nExported context to {target}"
            )
        else:
            assert result == CommandResult(body)
            assert not target_root.exists()
    # A first formatting failure keeps identity and precedes any debug export.
    failure = RuntimeError("first format failure")

    class Broken(str):
        def __format__(self, spec):
            raise failure

    target_root = directory / "format-failure"
    context = CommandContext(
        last_context=Broken("cached"),
        runtime=NS(config=NS(transcript=NS(export_directory=str(target_root)))),
    )
    with pytest.raises(RuntimeError) as caught:
        await _handler("context")(context, ("--debug", "--file"), MARKER)
    assert caught.value is failure
    assert not target_root.exists()


@pytest.mark.parametrize(
    "case",
    [
        "format",
        "debug-turn",
        "timing-turn",
        "lazy",
        "mixed",
        "invalid-timing",
        "failures",
        "cache",
        "fallback",
        "budget",
        "read-failures",
    ],
)
@pytest.mark.asyncio
async def test_diagnostic_projection_order_and_failures(case, tmp_path):
    events = []
    if case == "format":
        await _check_cached_context_formatting(tmp_path / "context-format")
        key = _Formatted(events, "key", "a")
        value = _Formatted(events, "value", "text")
        for name, field in [("debug", "last_debug"), ("timing", "last_timing")]:
            events.clear()
            context = CommandContext(**{field: {key: value}})
            data = getattr(host.ChatDiagnosticsPort(context), name + "_snapshot")()
            assert events == [
                "key.format:",
                "value.format:" + (".3f" if name == "timing" else ""),
            ]
            assert type(data.fields[0].key) is type(data.fields[0].value) is str
            assert host.adapt_diagnostic_outcome(CommandOutcome(data)).output.endswith(
                "- a: text" + ("s" if name == "timing" else "")
            )
            assert len(events) == 2
            getattr(context, field).clear()
            assert data.fields == (DiagnosticField("a", "text"),)
    elif case in ("debug-turn", "timing-turn"):
        name = "debug" if case == "debug-turn" else "timing"
        turn = _Trace(
            events,
            "turn",
            turn_ref="last",
            outcome="ok",
            persistence="saved",
            completed_tools=2,
            failed_tools=1,
            duration_ms=1234.5,
        )
        execution = _Trace(
            events,
            "execution",
            turns=(object(), turn),
            counters=(("z", "ok", 2), ("a", "failed", 1)),
        )
        telemetry = _Trace(
            events,
            "telemetry",
            execution_snapshot=lambda: events.append("snapshot") or execution,
        )
        runtime = _Trace(events, "runtime", telemetry=telemetry)
        context = _Trace(
            events,
            "context",
            runtime=runtime,
            **{"last_" + name: {"z": 2.0, "a": 0.12555}},
        )
        data = getattr(host.ChatDiagnosticsPort(context), name + "_snapshot")()
        assert events[:6] == [
            "context.runtime",
            "context.runtime",
            "runtime.telemetry",
            "context.runtime",
            "runtime.telemetry",
            "telemetry.execution_snapshot",
        ]
        assert events.count("snapshot") == 1
        assert [field.key for field in data.fields] == ["a", "z"]
        if name == "debug":
            assert data.turn == DebugTurnData("last", "ok", "saved", "2", "1")
            assert [value for value in events if value.startswith("turn.")] == [
                "turn.turn_ref",
                "turn.outcome",
                "turn.persistence",
                "turn.completed_tools",
                "turn.failed_tools",
            ]
            assert "execution.counters" not in events
        else:
            assert data.fields[0].value == "0.126"
            assert data.turn == TimingTurnData(
                "1.234",
                "ok",
                "saved",
                (TimingCounter("z", "ok", "2"), TimingCounter("a", "failed", "1")),
            )
            assert [value for value in events if value.startswith("turn.")] == [
                "turn.duration_ms",
                "turn.outcome",
                "turn.persistence",
            ]
            assert events[-1] == "execution.counters"
    elif case == "lazy":

        class Falsy:
            def __bool__(self):
                return False

            def items(self):
                pytest.fail("Empty branch projected eagerly")

        for name in ("debug", "timing"):
            data = getattr(
                host.ChatDiagnosticsPort(CommandContext(**{"last_" + name: Falsy()})),
                name + "_snapshot",
            )()
            assert data.recorded is False
    elif case == "mixed":
        for name in ("debug", "timing"):
            with pytest.raises(TypeError):
                await _handler(name)(
                    CommandContext(**{"last_" + name: {"a": 1, 2: 2}}), (), MARKER
                )
    elif case == "invalid-timing":
        with pytest.raises(ValueError):
            await _handler("timing")(
                CommandContext(last_timing={"bad": "not numeric"}), (), MARKER
            )
    elif case == "failures":
        for failure in (RuntimeError("format"), asyncio.CancelledError("format")):
            for name in ("debug", "timing"):
                context = CommandContext(
                    **{
                        "last_" + name: {
                            "x": _Formatted(events, "value", failure=failure)
                        }
                    }
                )
                with pytest.raises(type(failure)) as caught:
                    await _handler(name)(context, (), MARKER)
                assert caught.value is failure
    elif case == "cache":
        for name in ("context", "prompt"):
            for value in (7, ["x"]):
                context = CommandContext(**{"last_" + name: value})
                with pytest.raises(TypeError):
                    await _handler(name)(context, (), MARKER)
            for value in (0, [], None, ""):
                context = CommandContext(**{"last_" + name: value})
                assert (await _handler(name)(context, (), MARKER)).output.startswith(
                    "Context payload:" if name == "context" else "System:"
                )
    elif case == "fallback":
        for name in ("context", "prompt"):
            context = _Trace(events, "context", **{"last_" + name: "cached"})
            assert (await _handler(name)(context, (), MARKER)).output == "cached"
            assert events == ["context.last_" + name]
            events.clear()
        rt = _Trace(events, "runtime", tool_context="tools")
        context = _Trace(
            events, "context", runtime=rt, last_context=None, history=[("u", "a")]
        )
        assert (
            await _handler("context")(context, (), MARKER)
        ).output == "Context payload:\ntools\nHistory turns: 1"
        assert events == [
            "context.last_context",
            "context.runtime",
            "context.runtime",
            "runtime.tool_context",
            "context.runtime",
            "runtime.tool_context",
            "context.history",
        ]
    elif case == "read-failures":
        for failure in (RuntimeError("host read"), asyncio.CancelledError("host read")):

            class BrokenRuntime:
                @property
                def telemetry(self, failure=failure):
                    events.append("telemetry")
                    raise failure

            for name in ("debug", "timing"):
                events.clear()
                context = _Trace(events, "context", runtime=BrokenRuntime())
                with pytest.raises(type(failure)) as caught:
                    await _handler(name)(context, (), MARKER)
                assert caught.value is failure
                assert events == ["context.runtime", "context.runtime", "telemetry"]

            class BrokenHistory:
                def __bool__(self):
                    return True

                def __getitem__(self, index, failure=failure):
                    raise failure

            with pytest.raises(type(failure)) as caught:
                await _handler("prompt")(
                    CommandContext(history=BrokenHistory()), (), MARKER
                )
            assert caught.value is failure
        for history in (("one",), ("a", "b", "c")):
            with pytest.raises(ValueError):
                await _handler("prompt")(CommandContext(history=[history]), (), MARKER)
    else:
        for window, buffer, expected in [
            (0, False, BudgetData(None, None)),
            (-1, -2, BudgetData("-1", "-2")),
            ("many", "few", BudgetData("many", "few")),
        ]:
            context = CommandContext(
                runtime=NS(
                    config=NS(memory=NS(context_window=window, output_buffer=buffer))
                )
            )
            assert host.ChatDiagnosticsPort(context).budget_snapshot() == expected
        events.clear()
        memory = _Trace(
            events,
            "budget",
            context_window=_Formatted(events, "window", ""),
            output_buffer=_Formatted(events, "buffer", "7"),
        )
        data = host.ChatDiagnosticsPort(
            CommandContext(runtime=NS(config=NS(memory=memory)))
        ).budget_snapshot()
        assert events == [
            "budget.context_window",
            "budget.output_buffer",
            "window.bool",
            "window.format:",
            "buffer.bool",
            "buffer.format:",
        ]
        assert data == BudgetData("", "7")
        assert (
            host.adapt_diagnostic_outcome(CommandOutcome(data)).output
            == "Token budget:\n- context_window: \n- output_buffer: 7"
        )


@pytest.mark.parametrize("name", ["context", "prompt"])
@pytest.mark.parametrize(
    "mode",
    [
        "configured",
        "default",
        "no-flag",
        "mkdir-failure",
        "write-failure",
        "write-cancel",
    ],
)
@pytest.mark.asyncio
async def test_diagnostic_exports_fixed_bytes_and_failures(
    tmp_path, monkeypatch, name, mode
):
    monkeypatch.chdir(tmp_path)
    destination = (
        tmp_path / ("exports" if mode == "default" else "nested/exports")
    ).resolve()
    context = CommandContext(
        runtime=None
        if mode == "default"
        else NS(config=NS(transcript=NS(export_directory=str(destination)))),
        **{"last_" + name: "Å\ntext"},
    )
    events = []

    class Text(str):
        def __bool__(self):
            return True

        def __len__(self):
            events.append("text.len")
            return super().__len__()

    setattr(context, "last_" + name, Text("Å\ntext"))
    original_write, original_mkdir, original_export = (
        Path.write_text,
        Path.mkdir,
        host._write_export_file,
    )
    failure = (
        asyncio.CancelledError("write cancelled")
        if mode == "write-cancel"
        else OSError("synthetic file failure")
    )

    def mkdir(path, *args, **kwargs):
        events.append("mkdir")
        if mode == "mkdir-failure":
            raise failure
        return original_mkdir(path, *args, **kwargs)

    def write(path, text, *args, **kwargs):
        events.append(("write", path, text, kwargs))
        if mode in ("write-failure", "write-cancel"):
            original_write(path, "partial", encoding="utf-8")
            raise failure
        return original_write(path, text, *args, **kwargs)

    def export(ctx, kind, text):
        events.append(("request", ctx, kind, text))
        return original_export(ctx, kind, text)

    monkeypatch.setattr(Path, "mkdir", mkdir)
    monkeypatch.setattr(Path, "write_text", write)
    monkeypatch.setattr(host, "_write_export_file", export)
    args = (
        ("--debug",)
        if mode == "no-flag"
        else ("--file", "--file", "../ignored", "--debug")
    )
    body = "Å\ntext" + ("\n\nDebug:\n- characters: 6" if name == "context" else "")
    target = destination / ("friday_" + name + ".txt")
    if mode.endswith("failure") or mode.endswith("cancel"):
        with pytest.raises(type(failure)) as caught:
            await _handler(name)(context, args, MARKER)
        assert caught.value is failure
        assert (
            sum(isinstance(event, tuple) and event[0] == "request" for event in events)
            == 1
        )
        if mode != "mkdir-failure":
            assert target.read_text() == "partial"  # no rollback
        assert not (tmp_path / "ignored").exists()
        return
    result = await _handler(name)(context, args, MARKER)
    if mode == "no-flag":
        assert result == CommandResult(body)
        assert events == (["text.len"] if name == "context" else [])
        assert not destination.exists()
        return
    assert result == CommandResult(body + f"\n\nExported {name} to {target}")
    if name == "context":
        assert events.count("text.len") == 1
        assert events.index("text.len") < next(
            index
            for index, event in enumerate(events)
            if isinstance(event, tuple) and event[0] == "request"
        )
    assert target.read_bytes() == body.encode("utf-8")
    assert (
        sum(isinstance(event, tuple) and event[0] == "request" for event in events) == 1
    )
    assert (
        sum(isinstance(event, tuple) and event[0] == "write" for event in events) == 1
    )
    assert events.count("mkdir") >= 2
    assert [
        event for event in events if isinstance(event, tuple) and event[0] == "write"
    ][0][3] == {"encoding": "utf-8"}
    assert not (tmp_path / "ignored").exists()
    setattr(context, "last_" + name, "replacement")
    events.clear()
    result = await _handler(name)(context, ("--file",), MARKER)
    assert result.output == "replacement" + f"\n\nExported {name} to {target}"
    assert target.read_bytes() == b"replacement"
    assert (
        sum(isinstance(event, tuple) and event[0] == "request" for event in events) == 1
    )
    if name == "context" and mode == "configured":
        await _check_cached_context_formatting(tmp_path / "export-format")
        # A rendered export must not mask a distinct injected shared outcome.
        factory = shared.build_diagnostic_handlers
        for changed_field in ("text", "count", "path"):

            def build(port, changed_field=changed_field):
                handlers = factory(port)

                async def context_handler(request, execution):
                    outcome = await handlers["context"](request, execution)
                    data = outcome.data
                    return CommandOutcome(
                        ContextData(
                            "injected" if changed_field == "text" else data.text,
                            999 if changed_field == "count" else data.character_count,
                            "injected-path"
                            if changed_field == "path"
                            else data.export_path,
                        )
                    )

                return {**handlers, "context": context_handler}

            with monkeypatch.context() as local:
                local.setattr(shared, "build_diagnostic_handlers", build)
                context.last_context = "source"
                result = await _handler("context")(
                    context, ("--debug", "--file"), MARKER
                )
            text = "injected" if changed_field == "text" else "source"
            count = 999 if changed_field == "count" else 6
            path = "injected-path" if changed_field == "path" else str(target)
            assert result == CommandResult(
                f"{text}\n\nDebug:\n- characters: {count}\n\nExported context to {path}"
            )
            assert target.read_text() == "source\n\nDebug:\n- characters: 6"


@pytest.mark.parametrize(
    "case",
    [
        "precedence",
        "projection",
        "containers",
        "subclasses",
        "pending",
        "cancel",
        "failure",
        "runtime-second",
        "response-failure",
    ],
)
@pytest.mark.asyncio
async def test_diagnostic_retrieval_projection_and_await(case):
    events = []
    if case == "precedence":
        context = _Trace(events, "context", runtime=None)
        assert (
            await _handler("debug-retrieval")(context, (), MARKER)
        ).output == "Memory runtime is not initialized."
        assert events == ["context.runtime"]
        events.clear()
        context = _Trace(events, "context", runtime=object())
        assert (
            await _handler("debug-retrieval")(context, (), MARKER)
        ).output == "Usage: /debug-retrieval <query>"
        assert events == ["context.runtime"]
        return
    if case == "runtime-second":

        class Context:
            @property
            def runtime(self):
                events.append("runtime")
                return object() if len(events) == 1 else None

        with pytest.raises(
            AttributeError, match="'NoneType' object has no attribute 'memory'"
        ):
            await _handler("debug-retrieval")(Context(), ("q",), MARKER)
        assert events == ["runtime", "runtime"]
        return
    entered, release = asyncio.Event(), asyncio.Event()
    failure = (
        asyncio.CancelledError("cancelled")
        if case == "cancel"
        else RuntimeError("retrieval failed")
    )

    class Snippets(list):
        def __len__(self):
            events.append("snippets.len")
            return super().__len__()

        def __getitem__(self, key):
            events.append(("snippets.slice", key))
            return super().__getitem__(key)

    class Snippet:
        def __init__(self, index):
            self.index = index

        def __str__(self):
            events.append(("snippet.str", self.index))
            return "Å\n\t  x\x00" + str(self.index) + "z" * 170

    class Response(dict):
        def get(self, key, default):
            events.append("response.get:" + key)
            if case == "response-failure":
                raise failure
            return super().get(key, default)

    snippets = Snippets(Snippet(i) for i in range(12))
    response = Response(
        snippets=snippets,
        debug_info={
            "z": _Formatted(events, "z", "last"),
            "a": _Formatted(events, "a", "first"),
        },
    )
    if case == "containers":
        response = Response(snippets=("ignored",), debug_info=["ignored"])
    if case == "subclasses":

        class Details(dict):
            pass

        response = Response(
            snippets=Snippets(["one\n二", False, None]),
            debug_info=Details({"b": 2, "a": 1}),
        )

    class Memory:
        async def debug_retrieval(self, query):
            events.append(("memory.enter", query))
            entered.set()
            if case in ("pending", "cancel"):
                await release.wait()
            if case == "failure":
                raise failure
            events.append("memory.return")
            return response

    context = _Trace(
        events, "context", runtime=_Trace(events, "runtime", memory=Memory())
    )
    args = ('"hello', 'world"', "//q", "  raw  ")
    query = '"hello world" //q   raw  '
    task = asyncio.create_task(_handler("debug-retrieval")(context, args, MARKER))
    try:
        await asyncio.wait_for(entered.wait(), 2)
        if case in ("pending", "cancel"):
            assert not task.done() and "memory.return" not in events
            if case == "cancel":
                task.cancel("stop")
                with pytest.raises(asyncio.CancelledError, match="stop"):
                    await asyncio.wait_for(task, 2)
                assert events.count(("memory.enter", query)) == 1
                assert "memory.return" not in events
                return
            release.set()
        if case in ("failure", "response-failure"):
            with pytest.raises(type(failure)) as caught:
                await asyncio.wait_for(task, 2)
            assert caught.value is failure
            assert events.count(("memory.enter", query)) == 1
            return
        result = await asyncio.wait_for(task, 2)
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    assert events[:4] == [
        "context.runtime",
        "context.runtime",
        "runtime.memory",
        ("memory.enter", query),
    ]
    assert events.count(("memory.enter", query)) == 1
    assert (
        result.handled is True and not result.exit_requested and not result.ui_effects
    )
    lines = result.output.splitlines()
    assert lines[:2] == ["Retrieval diagnostics:", "- query: " + query]
    if case == "containers":
        assert lines[2:] == ["- result_count: 0"]
    elif case == "subclasses":
        assert lines[2:] == [
            "- result_count: 3",
            "- a: 1",
            "- b: 2",
            "Results:",
            "- one 二",
            "- False",
            "- None",
        ]
    else:
        assert lines[2:6] == [
            "- result_count: 12",
            "- a: first",
            "- z: last",
            "Results:",
        ]
        assert len(lines[6:]) == 10
        assert all(
            len(line[2:]) == 160 and line.endswith("...") and line.startswith("- Å x")
            for line in lines[6:]
        )
        assert [
            event
            for event in events
            if isinstance(event, tuple) and event[0] == "snippet.str"
        ] == [("snippet.str", i) for i in range(10)]
        assert (
            events.index("snippets.len")
            < events.index("a.format:")
            < events.index("z.format:")
            < events.index(("snippets.slice", slice(None, 10)))
        )
        assert events.count("a.format:") == events.count("z.format:") == 1


def test_diagnostic_adapter_refusals_and_purity(monkeypatch):
    def fail(*args, **kwargs):
        pytest.fail("Pure presentation called a host/shared effect")

    monkeypatch.setattr(host, "_write_export_file", fail)
    monkeypatch.setattr(shared, "build_diagnostic_handlers", fail)
    data_rows = [
        (
            ContextData("body", 4, ""),
            "body\n\nDebug:\n- characters: 4\n\nExported context to ",
        ),
        (PromptData("prompt", "p"), "prompt\n\nExported prompt to p"),
        (DebugData(False), "No debug information recorded."),
        (
            DebugData(
                True,
                (DiagnosticField("key", "value"),),
                DebugTurnData("t", "o", "p", "2", "1"),
            ),
            "Debug information:\n- key: value\n- turn: t\n- outcome: o\n- persistence: p\n- completed_tools: 2\n- failed_tools: 1",
        ),
        (
            BudgetData(None, "0"),
            "Token budget:\n- context_window: unknown\n- output_buffer: 0",
        ),
        (TimingData(False), "No timing data recorded."),
        (
            TimingData(
                True,
                (DiagnosticField("work", "0.000"),),
                TimingTurnData(
                    "1.234", "ok", "saved", (TimingCounter("tool", "ok", "2"),)
                ),
            ),
            "Timing:\n- work: 0.000s\n- observed_turn: 1.234s (ok, persistence=saved)\n- tool/ok: 2",
        ),
        (
            RetrievalData("q", 2, (DiagnosticField("key", "value"),), ("one", "two")),
            "Retrieval diagnostics:\n- query: q\n- result_count: 2\n- key: value\nResults:\n- one\n- two",
        ),
        (
            RetrievalUnavailableData("runtime_missing"),
            "Memory runtime is not initialized.",
        ),
        (RetrievalUnavailableData("query_missing"), "Usage: /debug-retrieval <query>"),
    ]
    assert len({type(data) for data, _ in data_rows}) == 7
    for data, text in data_rows:
        assert host.adapt_diagnostic_outcome(CommandOutcome(data)) == CommandResult(
            text
        )

        class Subclass(type(data)):
            pass

        child = object.__new__(Subclass)
        invalid = object.__new__(CommandOutcome)
        object.__setattr__(invalid, "data", child)
        object.__setattr__(invalid, "error", None)
        object.__setattr__(invalid, "ui_effects", ())
        with pytest.raises(ValueError):
            host.adapt_diagnostic_outcome(invalid)
    for data in (
        NoData(),
        ExitData(True),
        HelpData(()),
        HistoryData(()),
        SessionClearedData(),
    ):
        with pytest.raises(ValueError):
            host.adapt_diagnostic_outcome(CommandOutcome(data))
    for data in (None, object(), "raw"):
        invalid = object.__new__(CommandOutcome)
        object.__setattr__(invalid, "data", data)
        object.__setattr__(invalid, "error", None)
        object.__setattr__(invalid, "ui_effects", ())
        with pytest.raises(ValueError):
            host.adapt_diagnostic_outcome(invalid)
    for outcome in (
        None,
        object(),
        CommandOutcome(error=CommandError("unknown_command", "context")),
        CommandOutcome(ContextData("x"), ui_effects=(UiEffect.CLEAR_SCREEN,)),
    ):
        with pytest.raises(ValueError):
            host.adapt_diagnostic_outcome(outcome)

    class OutcomeSubclass(CommandOutcome):
        pass

    with pytest.raises(ValueError):
        host.adapt_diagnostic_outcome(OutcomeSubclass(ContextData("x")))


@pytest.mark.asyncio
async def test_diagnostic_real_app_sequence(tmp_path, monkeypatch):
    config = FridayChatConfig.model_validate(
        {
            "llm": {"model": "fake/diagnostic-uat"},
            "transcript": {"export_directory": str(tmp_path)},
        }
    )
    runtime = build_runtime(config, fake=True)
    assert isinstance(runtime.memory, FakeMemoryController)
    events, invocations = [], []
    factory, close = shared.build_diagnostic_handlers, runtime.async_clients.close

    def build(port):
        handlers = factory(port)

        async def invoke(request, execution):
            invocations.append(request.name)
            return await handlers[request.name](request, execution)

        return {name: invoke for name in handlers}

    monkeypatch.setattr(shared, "build_diagnostic_handlers", build)

    class Output(ListOutputSink):
        async def write(self, text):
            events.append(("output", text))
            await super().write(text)

    class Display:
        def render_banner(self, **kwargs):
            pass

        def prompt_text(self, **kwargs):
            return "User: "

        def create_heartbeat(self, kind):
            return self

        def start(self):
            pass

        def stop(self):
            pass

        def clear_screen(self):
            events.append("display.clear")

    async def close_clients():
        events.append("close")
        await close()

    monkeypatch.setattr(runtime.async_clients, "close", close_clients)
    output = Output()
    app = FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource(
            [
                "hello",
                "/context",
                "/prompt",
                "/debug",
                "/debug-budget",
                "/timing",
                "/debug-retrieval hello",
                "/context --debug --file",
                "/prompt --file",
                "/history",
                "/clear",
                "/history",
                "/cls",
                "/q",
            ]
        ),
        output_sink=output,
        display=Display(),
    )
    history = app.command_context.history
    clear = runtime.memory.clear_session_memory

    async def clear_memory():
        assert history == []
        events.append("memory.clear")
        return await clear()

    monkeypatch.setattr(runtime.memory, "clear_session_memory", clear_memory)
    result = await app.run()
    assert result.exit_reason == "command_exit" and result.turns_processed == 1
    assert invocations == [*NAMES, "context", "prompt"]
    assert output.values[1].startswith("Context payload:")
    assert output.values[2].startswith("System:")
    assert output.values[3].startswith("Debug information:")
    assert output.values[4].startswith("Token budget:")
    assert output.values[5].startswith("Timing:")
    assert output.values[6].startswith("Retrieval diagnostics:")
    for index, name in ((7, "context"), (8, "prompt")):
        body, footer = output.values[index].rsplit("\n\nExported " + name + " to ", 1)
        target = (tmp_path / ("friday_" + name + ".txt")).resolve()
        assert footer == str(target) and target.read_bytes() == body.encode("utf-8")
    assert "\n\nDebug:\n- characters: " in output.values[7]
    assert output.values[9].startswith(
        "Conversation history:\n1. User: hello\n   Friday:"
    )
    assert output.values[-3:] == [
        "Conversation history cleared.",
        "No conversation history.",
        "Goodbye.",
    ]
    assert app.command_context.history is history and history == []
    assert runtime.memory.stored_turns == []
    assert (
        events.index("memory.clear")
        < events.index("display.clear")
        < events.index(("output", "Goodbye."))
        < events.index("close")
    )
    assert events.count("display.clear") == events.count("close") == 1
    assert not app.started and app.background.closed
    assert runtime.async_clients.close_calls == 1 and runtime.transcript.finalized
