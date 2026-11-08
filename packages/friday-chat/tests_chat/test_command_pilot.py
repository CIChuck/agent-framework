"""Shared pilot delegation, frozen Chat compatibility and host ownership."""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict
from pathlib import Path

import friday_commands.pilot as shared
import pytest
from friday_chat.app import FridayChatApp, ListInputSource, ListOutputSink
from friday_chat.commands import pilot
from friday_chat.commands import registry as registry_module
from friday_chat.commands.contracts import (
    CommandArgument,
    CommandContext,
    CommandMetadata,
    CommandResult,
    CommandUiEffect,
)
from friday_chat.commands.registry import (
    DEFAULT_COMMAND_SPECS,
    CommandRegistry,
    RegistryCommandContext,
    _exit_handler,
    _help_handler,
    build_default_registry,
)
from friday_chat.commands.session import cls_handler
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import build_runtime
from friday_commands import (
    CommandError,
    CommandExecution,
    CommandOutcome,
    CommandRequest,
    ExitData,
    HelpData,
    NoData,
    UiEffect,
)
from friday_commands import CommandRegistry as SharedRegistry

ORACLE = json.loads(
    (
        Path(__file__).resolve().parents[3]
        / "docs/planning/active/command-refactor/validation/pilot/baseline.json"
    ).read_text()
)["observations"]
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


def spy_factory(monkeypatch):
    """Wrap the real shared factory and async handlers, rather than fake output."""
    original = shared.build_pilot_handlers
    factories, invocations, outcomes = [], [], []

    def factory(catalog):
        factories.append(catalog)
        handlers = original(catalog)

        def wrap(name):
            async def handler(request, execution):
                invocations.append((name, request, execution))
                result = await handlers[name](request, execution)
                outcomes.append(result)
                return result

            return handler

        return {name: wrap(name) for name in handlers}

    monkeypatch.setattr(shared, "build_pilot_handlers", factory)
    return factories, invocations, outcomes


def test_all_metadata_matches_independent_frozen_oracle():
    registry = build_default_registry()
    actual = json.loads(
        json.dumps({k: asdict(v) for k, v in registry.commands.items()})
    )
    assert actual == ORACLE["metadata"]
    assert len(registry.canonical_names()) == 41
    assert registry.command_names() - registry.canonical_names() == {
        "q",
        "quit",
        "clearscreen",
    }
    assert len(DEFAULT_COMMAND_SPECS) == 39
    assert DEFAULT_COMMAND_SPECS[1].name == "cls"
    assert all(type(row) is CommandMetadata for row in registry.commands.values())


@pytest.mark.parametrize("row", ORACLE["help"], ids=lambda row: repr(row["focus"]))
def test_every_frozen_help_string(row):
    assert build_default_registry().render_help(row["focus"]) == row["output"]


@pytest.mark.parametrize("row", ORACLE["dispatch"], ids=lambda row: row["input"])
async def test_every_frozen_parser_and_dispatch_result(row):
    registry = build_default_registry()
    context = RegistryCommandContext(registry=registry)
    handled, result = await registry.execute(row["input"], context)
    assert {
        "input": row["input"],
        "handled": handled,
        "output": None if result is None else result.output,
        "result_handled": None if result is None else result.handled,
        "exit": None if result is None else result.exit_requested,
        "effects": []
        if result is None
        else [effect.value for effect in result.ui_effects],
        "context_exit": context.exit_requested,
    } == row


@pytest.mark.parametrize(
    ("text", "name", "args"),
    [
        ('//HeLp "q more" ignored', "help", ('"q', 'more"', "ignored")),
        ("/help\t/q", "help", ("/q",)),
        ("/ /HELP q", "help", ("q",)),
        ("/exit extra", "exit", ("extra",)),
        ("/quit extra", "exit", ("extra",)),
        ("/q extra", "exit", ("extra",)),
        ("/cls extra", "cls", ("extra",)),
        ("/clearscreen extra", "cls", ("extra",)),
    ],
)
async def test_dispatch_parses_once_and_awaits_one_canonical_shared_handler(
    monkeypatch, text, name, args
):
    factories, calls, outcomes = spy_factory(monkeypatch)
    registry = build_default_registry()
    context = RegistryCommandContext(registry=registry)
    original = registry_module._parse_command_input
    parses = []

    def parse(value):
        parses.append(value)
        return original(value)

    def redispatch(*_args, **_kwargs):
        pytest.fail("Chat must not redispatch through the neutral registry")

    monkeypatch.setattr(registry_module, "_parse_command_input", parse)
    monkeypatch.setattr(SharedRegistry, "execute_text", redispatch)
    handled, result = await registry.execute(text, context)
    assert parses == [text]
    assert len(factories) == len(calls) == len(outcomes) == 1
    called_name, request, execution = calls[0]
    assert called_name == name
    assert type(request) is CommandRequest
    assert request.name == name and request.args == args
    assert request.spec is next(
        spec for spec in shared.PILOT_SPECS if spec.name == name
    )
    assert type(execution) is CommandExecution and execution.session_id is None
    assert handled is True and result == pilot.adapt_outcome(outcomes[0])
    assert context.exit_requested is (name == "exit")


@pytest.mark.parametrize(
    ("name", "handler"),
    [("help", _help_handler), ("exit", _exit_handler), ("cls", cls_handler)],
)
async def test_renamed_compatibility_wrappers_use_shared_spec(
    monkeypatch, name, handler
):
    _, calls, _ = spy_factory(monkeypatch)
    registry = CommandRegistry()
    registry.register(
        "renamed", description="Unrelated.", category="other", handler=handler
    )
    context = RegistryCommandContext(registry=CommandRegistry())
    handled, result = await registry.execute("/renamed extra", context)
    assert handled and result is not None
    assert len(calls) == 1
    assert calls[0][1].spec.name == name
    assert calls[0][1].spec.description != "Unrelated."
    assert calls[0][1].args == ("extra",)


async def test_help_uses_context_catalog_or_fresh_default_for_plain_context(
    monkeypatch,
):
    registry = build_default_registry()
    other = CommandRegistry()
    other.register("only-here", description="Context entry.", category="custom")
    _, selected = await registry.execute(
        "/help", RegistryCommandContext(registry=other)
    )
    assert selected.output == other.render_help()
    created = []
    original = registry_module.build_default_registry

    def build():
        result = original()
        created.append(result)
        return result

    monkeypatch.setattr(registry_module, "build_default_registry", build)
    for _ in range(2):
        _, result = await registry.execute("/help", CommandContext())
        assert result.output == registry.render_help()
    assert len(created) == 2 and created[0] is not created[1]


@pytest.mark.parametrize("focus", [None, "", False, 0, [], "q", "//q", " "])
def test_synchronous_help_calls_shared_selector_once_without_an_event_loop(
    monkeypatch, focus
):
    calls = []
    original = shared.describe_help

    def describe(catalog, value):
        calls.append(value)
        return original(catalog, value)

    def forbidden(*_args, **_kwargs):
        pytest.fail("Synchronous help must not run a coroutine")

    monkeypatch.setattr(shared, "describe_help", describe)
    monkeypatch.setattr(asyncio, "run", forbidden)
    registry = build_default_registry()
    result = registry.render_help(focus)
    assert isinstance(result, str)
    assert calls == [focus or None]


@pytest.mark.parametrize("name", ["help", "exit", "cls", *RETIRED])
async def test_custom_handlers_remain_authoritative(monkeypatch, name):
    def forbidden(*_args):
        pytest.fail("A custom handler must not enter the shared pilot")

    monkeypatch.setattr(shared, "build_pilot_handlers", forbidden)
    calls = []

    async def sentinel(context, args, metadata):
        calls.append((context, args, metadata))
        return CommandResult("custom result")

    registry = CommandRegistry()
    assert registry.command_names() == set()
    registry.register(name, description="Custom.", category="custom", handler=sentinel)
    context = CommandContext()
    _, result = await registry.execute(f"/{name} extra", context)
    assert result == CommandResult("custom result")
    assert len(calls) == 1 and calls[0][1] == ("extra",)
    assert calls[0][0] is context and calls[0][2].name == name
    assert context.exit_requested is False


def test_catalog_exact_keys_and_snapshot_do_not_revalidate_legacy_names():
    registry = CommandRegistry()
    registry.register(" /odd ", description="Odd.", category="utility", aliases=("",))
    registry.register(
        "plain", description="Plain.", category="utility", aliases=(" /ALIAS ",)
    )
    catalog = pilot.RegistryCatalog(registry._commands, registry._aliases)
    assert catalog.lookup_key("").name == "/odd"
    assert catalog.lookup_key("/alias").name == "plain"
    assert catalog.lookup_key(" /ALIAS ") is None
    assert catalog.lookup_key("alias") is None
    snapshot = catalog.specs()
    registry.register("later", description="Later.", category="utility")
    assert [spec.name for spec in snapshot] == ["/odd", "plain"]
    assert len(catalog.specs()) == 3
    assert registry.render_help(" ").startswith("//odd\n")
    assert registry.render_help(" /ALIAS ").startswith("/plain\n")
    assert registry.render_help(" //ALIAS ") == (
        "Unknown command: ///alias. Type /help for available commands."
    )
    assert (
        CommandRegistry().render_help()
        == "Available commands:\nUse /help <command> for focused details."
    )


@pytest.mark.parametrize(
    ("kwargs", "fragment"),
    [
        ({"default": 7}, "[optional] (default=7)"),
        ({"required": "yes"}, "[required]"),
        ({"required": 0}, "[optional]"),
        ({"choices": ("text", "json")}, "choices=text, json"),
        ({"choices": ["text", "json"]}, "choices=text, json"),
        ({"choices": "ab"}, "choices=a, b"),
        ({"choices": {"text": 1, "json": 2}}, "choices=text, json"),
    ],
)
def test_permissive_legacy_arguments_project_displayed_meaning(kwargs, fragment):
    registry = CommandRegistry()
    argument = CommandArgument("format", "Output format.", **kwargs)
    registry.register(
        "inspect", description="Inspect.", category="utility", arguments=(argument,)
    )
    assert registry.commands["inspect"].arguments[0] is argument
    assert fragment in registry.render_help("inspect")
    assert fragment in registry.render_help()


def test_bad_choice_still_raises_but_is_not_projected_for_other_focus():
    registry = CommandRegistry()
    registry.register("safe", description="Safe.", category="utility")
    registry.register(
        "bad",
        description="Bad.",
        category="utility",
        arguments=(CommandArgument("arg", "Argument.", choices=("text", 7)),),
    )
    assert registry.render_help("safe").startswith("/safe\n")
    assert (
        registry.render_help("unknown")
        == "Unknown command: /unknown. Type /help for available commands."
    )
    for focus in (None, "bad"):
        with pytest.raises(TypeError):
            registry.render_help(focus)


@pytest.mark.parametrize(
    "outcome",
    [
        None,
        CommandOutcome(data=NoData()),
        CommandOutcome(data=NoData(), ui_effects=(UiEffect.CLEAR_SCREEN,) * 2),
        CommandOutcome(data=ExitData(False)),
        CommandOutcome(data=ExitData(), ui_effects=(UiEffect.CLEAR_SCREEN,)),
        CommandOutcome(data=HelpData(()), ui_effects=(UiEffect.CLEAR_SCREEN,)),
        CommandOutcome(data=HelpData((), focused_name="help")),
        CommandOutcome(data=HelpData(shared.PILOT_SPECS, focused_name="help")),
        CommandOutcome(data=HelpData((shared.PILOT_SPECS[0],), focused_name="exit")),
        *[
            CommandOutcome(error=CommandError(code, "help"))
            for code in (
                "invalid_arguments",
                "unavailable",
                "failed",
            )
        ],
        CommandOutcome(error=CommandError("unknown_command", "help", usage="/help")),
    ],
)
def test_adapter_explicitly_rejects_unsupported_foundation_shapes(outcome):
    with pytest.raises(ValueError):
        pilot.adapt_outcome(outcome)


def test_adapter_accepts_only_the_five_documented_shapes():
    help_spec = shared.PILOT_SPECS[0]
    registry = build_default_registry()
    assert pilot.adapt_outcome(CommandOutcome(data=HelpData(()))) == CommandResult(
        "Available commands:\nUse /help <command> for focused details."
    )
    assert pilot.adapt_outcome(
        CommandOutcome(data=HelpData((help_spec,), "help"))
    ) == CommandResult(registry.render_help("help"))
    assert pilot.adapt_outcome(
        CommandOutcome(error=CommandError("unknown_command", "/q"))
    ) == CommandResult("Unknown command: //q. Type /help for available commands.")
    assert pilot.adapt_outcome(CommandOutcome(data=ExitData())) == CommandResult(
        "Goodbye.", exit_requested=True
    )
    assert pilot.adapt_outcome(
        CommandOutcome(data=NoData(), ui_effects=(UiEffect.CLEAR_SCREEN,))
    ) == CommandResult("", ui_effects=(CommandUiEffect.CLEAR_SCREEN,))


@pytest.mark.parametrize("handler", [_exit_handler, cls_handler])
async def test_exit_and_clear_never_read_context_or_legacy_metadata(
    monkeypatch, handler
):
    factories, calls, _ = spy_factory(monkeypatch)

    class Tripwire:
        def __getattribute__(self, name):
            raise AssertionError(f"Unexpected host read: {name}")

    result = await handler(Tripwire(), ("extra",), Tripwire())
    assert len(factories) == len(calls) == 1
    assert factories[0].specs() == () and factories[0].lookup_key("anything") is None
    assert calls[0][2] == CommandExecution()
    assert result.output == ("Goodbye." if handler is _exit_handler else "")


@pytest.mark.parametrize("handler", [_help_handler, _exit_handler, cls_handler])
@pytest.mark.parametrize(
    "error", [RuntimeError("pilot failure"), asyncio.CancelledError()]
)
async def test_handler_failure_and_cancellation_propagate_once(
    monkeypatch, handler, error
):
    calls = []

    def factory(_catalog):
        async def fail(request, _execution):
            calls.append(request.name)
            raise error

        return {name: fail for name in ("help", "exit", "cls")}

    monkeypatch.setattr(shared, "build_pilot_handlers", factory)
    context = RegistryCommandContext(registry=CommandRegistry())
    with pytest.raises(type(error)) as caught:
        await handler(
            context, (), CommandMetadata("ignored", "Ignored.", "other", "/ignored")
        )
    assert caught.value is error and len(calls) == 1
    assert context.exit_requested is False


@pytest.mark.parametrize("clear_name", ["cls", "clearscreen"])
@pytest.mark.parametrize("display_kind", ["ok", "missing", "failed"])
async def test_real_app_shared_help_clear_exit_keep_order_and_once_only_cleanup(
    monkeypatch, clear_name, display_kind
):
    factories, calls, outcomes = spy_factory(monkeypatch)
    events = []
    runtime = build_runtime(
        FridayChatConfig.model_validate({"llm": {"model": "fake/pilot-test"}}),
        fake=True,
    )
    original_close = runtime.async_clients.close

    async def close():
        events.append("close")
        await original_close()

    monkeypatch.setattr(runtime.async_clients, "close", close)

    class Output(ListOutputSink):
        async def write(self, text):
            events.append("output:" + text)
            await super().write(text)

    class Display:
        def render_banner(self, **_kwargs):
            pass

        def clear_screen(self):
            events.append("clear")
            if display_kind == "failed":
                raise RuntimeError("private terminal detail")

    output = Output()
    app = FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource(
            ["/help exit", f"/{clear_name} extra", "/q extra", "not reached"]
        ),
        output_sink=output,
        display=None if display_kind == "missing" else Display(),
    )
    result = await app.run()
    assert [call[0] for call in calls] == ["help", "cls", "exit"]
    assert len(factories) == len(outcomes) == 3
    assert result.exit_reason == "command_exit" and result.turns_processed == 0
    assert app.command_context.exit_requested is True
    assert app.session.initialized is False and app.session.turn_ids == []
    assert runtime.async_clients.close_calls == 1
    assert events.count("clear") == (0 if display_kind == "missing" else 1)
    assert events[0].startswith("output:/exit\n")
    assert events[-2:] == ["output:Goodbye.", "close"]
    assert output.values[-1] == "Goodbye."
    if display_kind == "ok":
        assert len(output.values) == 2
        assert events[1] == "clear"
    else:
        expected = (
            "Unable to clear the terminal: display is unavailable."
            if display_kind == "missing"
            else "Unable to clear the terminal."
        )
        assert output.values[1] == expected
    assert all("private terminal detail" not in value for value in output.values)


async def test_app_applies_shared_clear_effect_before_command_output(monkeypatch):
    original_factory = shared.build_pilot_handlers
    events = []

    def factory(catalog):
        handlers = dict(original_factory(catalog))
        original = handlers["cls"]

        async def clear(request, execution):
            events.append("shared")
            return await original(request, execution)

        handlers["cls"] = clear
        return handlers

    monkeypatch.setattr(shared, "build_pilot_handlers", factory)
    original_adapter = pilot.adapt_outcome

    def with_output(outcome):
        result = original_adapter(outcome)
        return CommandResult("after clear", ui_effects=result.ui_effects)

    monkeypatch.setattr(pilot, "adapt_outcome", with_output)

    class Output(ListOutputSink):
        async def write(self, text):
            events.append(text)

    class Display:
        def render_banner(self, **_kwargs):
            pass

        def clear_screen(self):
            events.append("display")

    runtime = build_runtime(
        FridayChatConfig.model_validate({"llm": {"model": "fake/pilot-test"}}),
        fake=True,
    )
    await FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource(["/cls"]),
        output_sink=Output(),
        display=Display(),
    ).run()
    assert events == ["shared", "display", "after clear"]
