"""Frozen session compatibility, real delegation and host memory boundaries."""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

import friday_commands.session_views as shared
import pytest
from friday_chat.app import FridayChatApp, ListInputSource, ListOutputSink
from friday_chat.commands import registry as registry_module
from friday_chat.commands import session_views
from friday_chat.commands.contracts import (
    CommandContext,
    CommandMetadata,
    CommandResult,
)
from friday_chat.commands.registry import (
    BASIC_COMMAND_HANDLERS,
    DEFAULT_COMMAND_SPECS,
    CommandRegistry,
    RegistryCommandContext,
    _clear_handler,
    _history_handler,
    build_default_registry,
)
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import FakeMemoryController, build_runtime
from friday_commands import (
    CommandError,
    CommandExecution,
    CommandOutcome,
    CommandRequest,
    ExitData,
    HelpData,
    HistoryData,
    HistoryTurn,
    NoData,
    SessionClearedData,
    UiEffect,
)

FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures_session/session-baseline.json").read_text()
)
UNUSED_METADATA = CommandMetadata("unused", "Unused", "unused", "/unused")


def json_value(value):
    return json.loads(json.dumps(value))


def result_value(result):
    return None if result is None else json_value(asdict(result))


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

    @property
    def runtime(self):
        self.events.append("runtime.read")
        if self.runtime_failure is not None:
            raise self.runtime_failure
        return self._runtime


class Memory:
    def __init__(self, history, events, returned=True, failure=None):
        self.history = history
        self.events = events
        self.returned = returned
        self.failure = failure

    async def clear_session_memory(self):
        self.events.append("memory.clear:history=" + json.dumps(self.history))
        if self.failure is not None:
            raise self.failure
        return self.returned


@pytest.mark.parametrize("row", FIXTURE["cases"], ids=lambda row: row["case"])
@pytest.mark.asyncio
async def test_session_observations_match_frozen_fixture(row):
    """Reproduce every frozen row, including event/exception and pending state."""
    case = row["case"]
    events = []
    actual = {"case": case}
    if case.startswith("history:"):
        history = History(row["turns"], events)
        context = Context(history, events, runtime_failure=AssertionError("runtime"))
        actual.update(turns=row["turns"], args=row["args"])
        try:
            actual["result"] = result_value(
                await _history_handler(context, tuple(row["args"]), UNUSED_METADATA)
            )
        except Exception as error:
            actual["exception"] = {"type": type(error).__name__, "message": str(error)}
        actual.update(events=events, history_after=list(history))
    elif case == "clear:await-order":
        history = History([("hello", "world")], events)
        entered, release = asyncio.Event(), asyncio.Event()

        class BlockingMemory:
            async def clear_session_memory(self):
                events.append("memory.enter")
                entered.set()
                await release.wait()
                events.append("memory.return")
                return False

        context = Context(history, events, SimpleNamespace(memory=BlockingMemory()))
        task = asyncio.create_task(_clear_handler(context, (), UNUSED_METADATA))
        try:
            await asyncio.wait_for(entered.wait(), 2)
            actual["during_await"] = {
                "history": list(history),
                "task_done": task.done(),
                "events": list(events),
            }
            release.set()
            actual["result"] = result_value(await asyncio.wait_for(task, 2))
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
            returned=label != "memory-false",
            failure=failure if label in ("memory-exception", "memory-cancel") else None,
        )
        context = Context(
            history,
            events,
            None if label == "no-runtime" else SimpleNamespace(memory=memory),
            failure if label == "runtime-exception" else None,
        )
        actual["args"] = row["args"]
        try:
            actual["result"] = result_value(
                await _clear_handler(context, tuple(row["args"]), UNUSED_METADATA)
            )
        except BaseException as error:
            actual["exception"] = {
                "type": type(error).__name__,
                "message": str(error),
                "same_object": error is failure,
            }
        actual.update(events=events, history_after=list(history))
    else:
        registry = build_default_registry()
        if case.startswith("renamed:"):
            registry = CommandRegistry()
            handler = _history_handler if case.endswith("history") else _clear_handler
            registry.register(
                "renamed", description="Renamed", category="test", handler=handler
            )
            text = "/renamed extra"
        else:
            text = case.removeprefix("dispatch:")
        context = CommandContext(history=[("hello", "world")])
        handled, result = await registry.execute(text, context)
        actual.update(
            handled=handled, result=result_value(result), history_after=context.history
        )
        if case.startswith("dispatch:"):
            actual["exit_requested"] = context.exit_requested
    assert json_value(actual) == row


def test_metadata_and_help_are_unchanged():
    registry = build_default_registry()
    assert len(registry.canonical_names()) == 41
    assert registry.command_names() - registry.canonical_names() == {
        "q",
        "quit",
        "clearscreen",
    }
    assert len(DEFAULT_COMMAND_SPECS) == 39
    assert [DEFAULT_COMMAND_SPECS[i].name for i in (0, 1, 2)] == [
        "clear",
        "cls",
        "history",
    ]
    assert BASIC_COMMAND_HANDLERS["clear"] is _clear_handler
    assert BASIC_COMMAND_HANDLERS["history"] is _history_handler
    for name, expected in FIXTURE["metadata"].items():
        assert json_value(asdict(registry.commands[name])) == expected
        assert json_value(asdict(session_views.session_metadata(name))) == expected
        assert registry.render_help(name) == (
            f"/{name}\nCategory: session\nUsage: /{name}\n"
            f"Description: {expected['description']}\nArguments: none"
        )


@pytest.mark.parametrize(
    ("text", "name", "args"),
    [
        ("/history", "history", ()),
        ('/HiStOrY "quoted words" //q', "history", ('"quoted', 'words"', "//q")),
        ("//history extra", "history", ("extra",)),
        ("/ history", "history", ()),
        ("/clear", "clear", ()),
        ("/ClEaR\textra", "clear", ("extra",)),
    ],
)
@pytest.mark.asyncio
async def test_session_delegates_once_and_consumes_shared_outcome(
    monkeypatch, text, name, args
):
    parser = registry_module._parse_command_input
    factory = shared.build_session_handlers
    parses, parsed_args, request_args, ports, calls, outcomes = [], [], [], [], [], []
    injected = CommandOutcome(data=HistoryData((HistoryTurn("injected", "shared"),)))

    def parse(text):
        parses.append(text)
        parsed = parser(text)
        parsed_args.append(parsed[1])
        return parsed

    def build(port):
        ports.append(port)
        handlers = factory(port)

        async def handler(request, execution):
            calls.append((request, execution))
            outcomes.append(await handlers[name](request, execution))
            return injected

        return {name: handler}

    def request(command_name, arguments, spec):
        request_args.append(arguments)
        return CommandRequest(command_name, arguments, spec)

    monkeypatch.setattr(registry_module, "_parse_command_input", parse)
    monkeypatch.setattr(shared, "build_session_handlers", build)
    monkeypatch.setattr(session_views, "CommandRequest", request)
    context = RegistryCommandContext(
        registry=CommandRegistry(), history=[("source", "original")]
    )
    history_alias = context.history
    handled, result = await build_default_registry().execute(text, context)
    assert handled and result is not None
    assert result == CommandResult(
        output="Conversation history:\n1. User: injected\n   Friday: shared"
    )
    assert parses == [text]
    assert len(ports) == len(calls) == len(outcomes) == 1
    assert ports[0].context is context
    request, execution = calls[0]
    assert type(request) is CommandRequest and type(execution) is CommandExecution
    assert request.name == name and request.args == args
    assert len(request_args) == 1 and request_args[0] is parsed_args[0]
    assert request.spec is next(s for s in shared.SESSION_SPECS if s.name == name)
    assert context.history is history_alias
    if name == "clear":
        assert context.history == []
        assert outcomes[0] == CommandOutcome(data=SessionClearedData())
    else:
        assert outcomes[0] == CommandOutcome(
            data=HistoryData((HistoryTurn("source", "original"),))
        )


@pytest.mark.parametrize("name", ["history", "clear", "vars"])
@pytest.mark.asyncio
async def test_custom_and_renamed_session_handlers(monkeypatch, name):
    def forbidden(_port):
        pytest.fail("Custom handlers must not enter shared session code")

    calls = []

    async def custom(context, args, metadata):
        calls.append((context, args, metadata))
        return CommandResult("custom")

    monkeypatch.setattr(shared, "build_session_handlers", forbidden)
    registry = CommandRegistry()
    registry.register(name, description="custom", category="test", handler=custom)
    context = CommandContext(history=[("keep", "me")])
    handled, result = await registry.execute(f"/{name} extra", context)
    assert handled and result == CommandResult("custom")
    assert calls == [(context, ("extra",), registry.commands[name])]
    assert context.history == [("keep", "me")]


@pytest.mark.parametrize("name", ["clear", "history"])
@pytest.mark.asyncio
async def test_renamed_wrapper_uses_supplied_context_and_fixed_spec(monkeypatch, name):
    original = shared.build_session_handlers
    calls = []

    def factory(port):
        handlers = original(port)

        async def invoke(request, execution):
            calls.append((port.context, request))
            return await handlers[name](request, execution)

        return {name: invoke}

    monkeypatch.setattr(shared, "build_session_handlers", factory)
    registry = CommandRegistry()
    registry.register(
        "renamed",
        description="Renamed",
        category="test",
        handler=BASIC_COMMAND_HANDLERS[name],
    )
    context = RegistryCommandContext(registry=CommandRegistry(), history=[("u", "a")])
    handled, result = await registry.execute("/renamed /q extra", context)
    assert handled and result is not None
    assert len(calls) == 1 and calls[0][0] is context
    assert calls[0][1].spec is next(s for s in shared.SESSION_SPECS if s.name == name)
    assert calls[0][1].args == ("/q", "extra")
    assert result.output == (
        "Conversation history cleared."
        if name == "clear"
        else "Conversation history:\n1. User: u\n   Friday: a"
    )


@pytest.mark.parametrize(
    "turns",
    [
        [],
        [("", "")],
        [("z", "B"), ("a", "A"), ("z", "B")],
        [("Å\nu", "答\na")],
        [(False, None), (7, ["x"])],
    ],
)
def test_history_projection_preserves_legacy_formatting(turns):
    events = []
    context = Context(turns, events, runtime_failure=AssertionError("runtime"))
    snapshot = session_views.ChatSessionPort(context).history_snapshot()
    assert snapshot == tuple(HistoryTurn(f"{u}", f"{a}") for u, a in turns)
    assert all(
        type(v) is str for t in snapshot for v in (t.user_message, t.assistant_message)
    )
    expected = "No conversation history."
    if turns:
        lines = ["Conversation history:"]
        for index, (u, a) in enumerate(turns, 1):
            lines.extend((f"{index}. User: {u}", f"   Friday: {a}"))
        expected = "\n".join(lines)
    assert session_views.adapt_session_outcome(
        CommandOutcome(data=HistoryData(snapshot))
    ) == CommandResult(expected)
    assert events == []


def test_projection_formats_each_member_once_and_preserves_access_order():
    events = []

    class Formatted(str):
        def __format__(self, spec):
            pytest.fail("A formatted str subclass must become a plain str")

    class Value:
        def __format__(self, spec):
            assert spec == ""
            events.append("format")
            return Formatted("rendered")

    turns = [(Value(), Value())]

    class HistoryContext:
        @property
        def history(self):
            events.append("history.read")
            return turns

        def __getattr__(self, name):
            pytest.fail("Unrelated context read: " + name)

    port = session_views.ChatSessionPort(HistoryContext())
    assert events == []
    snapshot = port.history_snapshot()
    assert events == ["history.read", "history.read", "format", "format"]
    assert snapshot == (HistoryTurn("rendered", "rendered"),)
    assert type(snapshot[0].user_message) is str
    assert (
        session_views.adapt_session_outcome(
            CommandOutcome(data=HistoryData(snapshot))
        ).output
        == "Conversation history:\n1. User: rendered\n   Friday: rendered"
    )
    assert events == ["history.read", "history.read", "format", "format"]
    turns.clear()
    assert len(snapshot) == 1


@pytest.mark.parametrize("phase", ["truth", "iteration", "format"])
def test_history_projection_propagates_failures_without_runtime_reads(phase):
    failure = RuntimeError(phase)

    class Values:
        def __bool__(self):
            if phase == "truth":
                raise failure
            return True

        def __iter__(self):
            if phase == "iteration":
                raise failure
            return iter([(self, "reply")])

        def __format__(self, spec):
            raise failure

    context = Context(Values(), [], runtime_failure=AssertionError("runtime"))
    with pytest.raises(RuntimeError) as caught:
        session_views.ChatSessionPort(context).history_snapshot()
    assert caught.value is failure
    assert context.events == []


@pytest.mark.parametrize(
    "outcome",
    [
        object(),
        CommandOutcome(data=NoData()),
        CommandOutcome(data=ExitData()),
        CommandOutcome(data=HelpData(())),
        CommandOutcome(error=CommandError("unknown_command", "history")),
        CommandOutcome(data=HistoryData(()), ui_effects=(UiEffect.CLEAR_SCREEN,)),
        CommandOutcome(data=SessionClearedData(), ui_effects=(UiEffect.CLEAR_SCREEN,)),
        CommandOutcome(data=NoData(), ui_effects=(UiEffect.CLEAR_SCREEN,)),
    ],
)
def test_session_outcome_adapter_refuses_other_shapes(outcome):
    with pytest.raises(ValueError):
        session_views.adapt_session_outcome(outcome)


def test_session_outcome_adapter_requires_exact_models():
    class ChildOutcome(CommandOutcome):
        pass

    class ChildHistory(HistoryData):
        pass

    class ChildMarker(SessionClearedData):
        pass

    for outcome in (
        ChildOutcome(data=HistoryData(())),
        SimpleNamespace(data=HistoryData(()), error=None, ui_effects=()),
    ):
        with pytest.raises(ValueError):
            session_views.adapt_session_outcome(outcome)
    for data in (ChildHistory(()), ChildMarker(), object()):
        # Exercise the adapter defensively without weakening shared constructors.
        outcome = object.__new__(CommandOutcome)
        object.__setattr__(outcome, "data", data)
        object.__setattr__(outcome, "error", None)
        object.__setattr__(outcome, "ui_effects", ())
        with pytest.raises(ValueError):
            session_views.adapt_session_outcome(outcome)


@pytest.mark.parametrize("returned", [True, False])
@pytest.mark.asyncio
async def test_clear_uses_public_current_session_memory_after_history(returned):
    events = []
    history = History([("u", "a")], events)
    alias = history
    entered, release = asyncio.Event(), asyncio.Event()
    session_id = object()

    class CurrentMemory:
        async def clear_session_memory(self):
            assert history is alias and history == []
            events.append("memory.enter")
            entered.set()
            await release.wait()
            events.append("memory.return")
            return returned

    runtime = SimpleNamespace(memory=CurrentMemory(), session_id=session_id)
    context = Context(history, events, runtime)
    task = asyncio.create_task(_clear_handler(context, ("ignored",), object()))
    try:
        await asyncio.wait_for(entered.wait(), 2)
        assert not task.done()
        assert events == [
            "history.clear",
            "runtime.read",
            "runtime.read",
            "memory.enter",
        ]
        release.set()
        assert await asyncio.wait_for(task, 2) == CommandResult(
            "Conversation history cleared."
        )
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    assert context.history is alias and alias == []
    assert runtime.session_id is session_id
    assert events == [
        "history.clear",
        "runtime.read",
        "runtime.read",
        "memory.enter",
        "memory.return",
    ]


@pytest.mark.asyncio
async def test_clear_ignores_memory_return_truthiness_and_has_no_eager_reads():
    class Untestable:
        def __bool__(self):
            pytest.fail("Memory result must be discarded")

    events = []
    history = History([("u", "a")], events)
    memory = Memory(history, events, returned=Untestable())
    context = Context(history, events, SimpleNamespace(memory=memory))
    port = session_views.ChatSessionPort(context)
    assert events == []
    operation = port.clear_session_memory()
    assert events == []
    operation.close()
    assert await _clear_handler(context, (), object()) == CommandResult(
        "Conversation history cleared."
    )
    assert events == [
        "history.clear",
        "runtime.read",
        "runtime.read",
        "memory.clear:history=[]",
    ]


def test_port_construction_does_not_read_context():
    class Tripwire:
        def __getattribute__(self, name):
            pytest.fail("Context read during construction: " + name)

    context = Tripwire()
    port = session_views.ChatSessionPort(context)
    assert port.context is context


def test_falsy_history_is_not_iterated():
    class Falsy:
        def __bool__(self):
            return False

        def __iter__(self):
            pytest.fail("Falsy history must not be iterated")

    events = []
    context = Context(Falsy(), events, runtime_failure=AssertionError("runtime"))
    assert session_views.ChatSessionPort(context).history_snapshot() == ()
    assert events == []


@pytest.mark.parametrize("phase", ["history.read", "runtime.second", "memory.read"])
@pytest.mark.asyncio
async def test_clear_attribute_failures_preserve_identity_and_cleared_state(phase):
    events = []
    failure = RuntimeError(phase)
    history = History([("u", "a")], events)

    class Runtime:
        @property
        def memory(self):
            events.append("memory.read")
            raise failure

    class AccessContext:
        @property
        def history(self):
            if phase == "history.read":
                events.append("history.read")
                raise failure
            return history

        @property
        def runtime(self):
            events.append("runtime.read")
            if phase == "runtime.second" and events.count("runtime.read") == 2:
                raise failure
            return Runtime()

    with pytest.raises(RuntimeError) as caught:
        await _clear_handler(AccessContext(), (), object())
    assert caught.value is failure
    expected = {
        "history.read": ["history.read"],
        "runtime.second": ["history.clear", "runtime.read", "runtime.read"],
        "memory.read": ["history.clear", "runtime.read", "runtime.read", "memory.read"],
    }
    assert events == expected[phase]
    assert history == ([("u", "a")] if phase == "history.read" else [])


@pytest.mark.asyncio
async def test_cancellation_during_memory_await_leaves_history_cleared():
    events = []
    history = History([("u", "a")], events)
    entered = asyncio.Event()

    class PendingMemory:
        async def clear_session_memory(self):
            events.append("memory.enter")
            entered.set()
            await asyncio.Event().wait()

    context = Context(history, events, SimpleNamespace(memory=PendingMemory()))
    task = asyncio.create_task(_clear_handler(context, (), object()))
    try:
        await asyncio.wait_for(entered.wait(), 2)
        assert history == [] and not task.done()
        task.cancel("stop")
        with pytest.raises(asyncio.CancelledError, match="stop"):
            await asyncio.wait_for(task, 2)
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    assert history == []
    assert events == ["history.clear", "runtime.read", "runtime.read", "memory.enter"]


@pytest.mark.parametrize("name", ["clear", "history"])
@pytest.mark.parametrize("failure_type", [RuntimeError, asyncio.CancelledError])
@pytest.mark.asyncio
async def test_shared_failure_propagates_once_before_adaptation(
    monkeypatch, name, failure_type
):
    failure = failure_type("shared")
    calls = []

    def factory(port):
        calls.append("factory")

        async def handler(request, execution):
            calls.append("handler")
            raise failure

        return {name: handler}

    def adapt(outcome):
        pytest.fail("A failed shared invocation must not reach presentation")

    monkeypatch.setattr(shared, "build_session_handlers", factory)
    monkeypatch.setattr(session_views, "adapt_session_outcome", adapt)
    with pytest.raises(failure_type) as caught:
        await BASIC_COMMAND_HANDLERS[name](CommandContext(), (), object())
    assert caught.value is failure
    assert calls == ["factory", "handler"]


@pytest.mark.asyncio
async def test_app_history_clear_history_sequence(tmp_path, monkeypatch):
    config = FridayChatConfig.model_validate(
        {
            "llm": {"model": "openai/test-chat-model"},
            "transcript": {"export_directory": str(tmp_path)},
        }
    )
    runtime = build_runtime(config)
    assert isinstance(runtime.memory, FakeMemoryController)
    output = ListOutputSink()
    app = FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource(["hello", "/history", "/clear", "/history", "/q"]),
        output_sink=output,
    )
    identity = runtime.session_identity
    history = app.command_context.history
    original_clear = runtime.memory.clear_session_memory
    cleared = []

    async def clear():
        assert history == []
        assert runtime.memory.stored_turns
        cleared.append(runtime.session_identity)
        return await original_clear()

    monkeypatch.setattr(runtime.memory, "clear_session_memory", clear)
    result = await app.run()
    assert result.exit_reason == "command_exit" and result.turns_processed == 1
    assert (
        output.values[1]
        == f"Conversation history:\n1. User: hello\n   Friday: {output.values[0]}"
    )
    assert output.values[2:] == [
        "Conversation history cleared.",
        "No conversation history.",
        "Goodbye.",
    ]
    assert app.command_context.history is history and history == []
    assert runtime.memory.stored_turns == []
    assert cleared == [identity] and runtime.session_identity is identity
