"""Frozen grammar, atomic registration and one-execution behavior."""

import asyncio
from dataclasses import FrozenInstanceError, replace

import pytest
from friday_commands import (
    CommandArgument,
    CommandExecution,
    CommandOutcome,
    CommandRegistry,
    CommandRequest,
    CommandSpec,
    ExitData,
    NoData,
    UiEffect,
)


def spec(name: str = "help", aliases: tuple[str, ...] = ()) -> CommandSpec:
    return CommandSpec(name, "Description", "general", "/usage", aliases)


async def noop(request: CommandRequest, execution: CommandExecution) -> CommandOutcome:
    return CommandOutcome(data=NoData())


class DerivedOutcome(CommandOutcome):
    pass


@pytest.mark.asyncio
async def test_canonical_snapshot_and_copy_identity() -> None:
    calls = []

    async def handler(request, execution):
        calls.append((request, execution))
        return CommandOutcome(data=NoData())

    argument = CommandArgument(
        " Topic ", " Topic description ", True, " RAW ", (" A ",)
    )
    raw = CommandSpec(
        "/HELP ",
        " Help description ",
        " general ",
        " /help ",
        ("/H ",),
        (argument,),
        "  detail stays raw  ",
    )
    registry = CommandRegistry()
    registry.register(raw, handler)
    canonical = registry.resolve("H")
    assert canonical is not raw
    assert canonical.name == "help" and canonical.aliases == ("h",)
    assert (canonical.description, canonical.category, canonical.usage) == (
        "Help description",
        "general",
        "/help",
    )
    assert canonical.detail == raw.detail
    assert canonical.arguments == raw.arguments
    assert canonical.arguments[0] is not argument
    assert raw.name == "/HELP " and raw.description == " Help description "
    assert registry.specs() == (canonical,)
    assert registry.specs()[0] is canonical
    assert registry.resolve(" /HELP ") is None
    names, specs = registry.names(), registry.specs()
    registry.register(spec("another"), noop)
    assert names == frozenset({"help", "h"}) and specs == (canonical,)
    assert tuple(s.name for s in registry.specs()) == ("another", "help")
    with pytest.raises(FrozenInstanceError):
        canonical.name = "mutated"
    with pytest.raises(AttributeError):
        names.add("mutated")
    execution = CommandExecution("session")
    await registry.execute_text("/H Topic", execution)
    assert len(calls) == 1
    assert calls[0][0].spec is canonical
    assert calls[0][0].name == "help" and calls[0][0].args == ("Topic",)
    assert calls[0][1] is execution


@pytest.mark.parametrize(
    "candidate",
    [
        spec(""),
        spec("/ "),
        spec("new", ("",)),
        spec("new", (" \t ",)),
        spec(" help "),
        spec("new", (" H ",)),
        spec("new", ("fresh", "/HELP")),
        spec("same", ("/SAME",)),
        spec("new", ("repeat", "/REPEAT ")),
        replace(spec("new"), description=" "),
        replace(spec("new"), category=" "),
        replace(spec("new"), usage=" "),
        replace(spec("new"), arguments=(CommandArgument(" ", "Description"),)),
        replace(spec("new"), arguments=(CommandArgument("name", " "),)),
    ],
)
@pytest.mark.asyncio
async def test_rejected_registration_preserves_all_public_state(
    candidate: CommandSpec,
) -> None:
    registry = CommandRegistry()
    calls = []

    async def original(request, execution):
        calls.append(request.name)
        return CommandOutcome(data=NoData())

    registry.register(spec("help", ("h",)), original)
    names, specs = registry.names(), registry.specs()
    canonical = registry.resolve("help")
    with pytest.raises(ValueError) as exc:
        registry.register(candidate, noop)
    assert type(exc.value) is ValueError
    assert registry.names() == names and registry.specs() == specs
    assert registry.resolve("h") is canonical
    assert registry.resolve("fresh") is None and registry.resolve("new") is None
    await registry.execute_text("/h", CommandExecution())
    assert calls == ["help"]


@pytest.mark.asyncio
async def test_one_pass_normalization_can_retain_a_slash() -> None:
    registry = CommandRegistry()
    calls = []

    async def handler(request, execution):
        calls.append(request)
        return CommandOutcome(data=NoData())

    registry.register(spec(" /HELP "), handler)
    assert registry.names() == frozenset({"/help"})
    assert registry.resolve(" /HELP ").name == "/help"
    assert registry.resolve("/help") is None
    await registry.execute_text("///HELP Topic", CommandExecution())
    assert calls[0].name == calls[0].spec.name == "/help"


@pytest.mark.asyncio
async def test_nonempty_slash_alias_does_not_make_bare_slash_executable() -> None:
    registry = CommandRegistry()
    registry.register(spec("help", (" / ",)), noop)
    assert registry.names() == frozenset({"help", "/"})
    assert registry.resolve(" / ").name == "help"
    bare = await registry.execute_text("/", CommandExecution())
    assert bare.outcome.error.code == "unknown_command"
    assert bare.outcome.error.command_name == ""
    assert (
        type((await registry.execute_text("///", CommandExecution())).outcome.data)
        is NoData
    )


# Expected outcomes are frozen from the approved independent Chat table.
@pytest.mark.parametrize(
    ("text", "name", "args", "handled", "unknown"),
    [
        ("hello", None, (), False, False),
        (" /HELP topic", None, (), False, False),
        ("/", "", (), True, True),
        ("/HELP topic", "help", ("topic",), True, False),
        ("//HELP topic", "help", ("topic",), True, False),
        ("///HELP topic", "/help", ("topic",), True, True),
        ("/ /HELP topic", "help", ("topic",), True, False),
        ("/   HELP  A B", "help", ("A", "B"), True, False),
        ("/H topic", "help", ("topic",), True, False),
        ('/read "a b.txt"', "read", ('"a', 'b.txt"'), True, False),
    ],
)
@pytest.mark.asyncio
async def test_frozen_text_fixtures(text, name, args, handled, unknown) -> None:
    registry = CommandRegistry()
    calls = []

    async def handler(request, execution):
        calls.append(request)
        return CommandOutcome(data=NoData())

    registry.register(spec("help", ("h",)), handler)
    registry.register(spec("read"), handler)
    result = await registry.execute_text(text, CommandExecution())
    assert result.handled is handled
    if not handled:
        assert result.outcome is None and calls == []
    elif unknown:
        assert result.outcome.error.code == "unknown_command"
        assert result.outcome.error.command_name == name
        assert result.outcome.ui_effects == () and calls == []
    else:
        assert len(calls) == 1
        assert calls[0].name == calls[0].spec.name == name
        assert calls[0].args == args
        assert calls[0].spec is registry.resolve(name)


@pytest.mark.asyncio
async def test_empty_registry_and_bad_public_input_boundaries() -> None:
    registry = CommandRegistry()
    assert registry.names() == frozenset() and registry.specs() == ()
    assert registry.resolve("anything") is None
    assert (
        await registry.execute_text("/help", CommandExecution())
    ).outcome.error.code == "unknown_command"
    for invalid in (None, 1, object(), {}):
        with pytest.raises(TypeError):
            registry.resolve(invalid)
        with pytest.raises(TypeError):
            await registry.execute_text(invalid, CommandExecution())
        with pytest.raises(TypeError):
            await registry.execute_text("plain", invalid)
    with pytest.raises(TypeError):
        registry.register(object(), noop)
    with pytest.raises(TypeError):
        registry.register(spec(), None)

    class DerivedSpec(CommandSpec):
        pass

    class DerivedExecution(CommandExecution):
        pass

    with pytest.raises(TypeError):
        registry.register(DerivedSpec("a", "A", "test", "/a"), noop)
    with pytest.raises(TypeError):
        await registry.execute_text("plain", DerivedExecution())
    assert registry.names() == frozenset()


@pytest.mark.parametrize(
    "invalid_result", [None, "rendered text", object(), DerivedOutcome(data=NoData())]
)
@pytest.mark.asyncio
async def test_handler_result_boundaries_invoke_once(invalid_result: object) -> None:
    registry = CommandRegistry()
    calls = []

    async def handler(request, execution):
        calls.append(request)
        return invalid_result

    registry.register(spec(), handler)
    assert calls == []
    with pytest.raises(TypeError):
        await registry.execute_text("/help", CommandExecution())
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_sync_handler_is_not_called_during_registration_or_retried() -> None:
    registry = CommandRegistry()
    calls = []

    def handler(request, execution):
        calls.append(request)
        return CommandOutcome(data=NoData())

    registry.register(spec(), handler)
    assert calls == []
    with pytest.raises(TypeError):
        await registry.execute_text("/help", CommandExecution())
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_callable_awaitable_handler_runs_and_awaits_once() -> None:
    registry = CommandRegistry()
    calls = []
    awaits = []
    outcome = CommandOutcome(data=ExitData(), ui_effects=(UiEffect.CLEAR_SCREEN,))

    class AwaitableResult:
        def __await__(self):
            awaits.append(1)

            async def finish():
                return outcome

            return finish().__await__()

    def handler(request, execution):
        calls.append(request)
        return AwaitableResult()

    registry.register(spec(), handler)
    assert calls == [] and awaits == []
    result = await registry.execute_text(
        "/help Unchecked Extra Tokens", CommandExecution()
    )
    assert len(calls) == len(awaits) == 1
    assert calls[0].args == ("Unchecked", "Extra", "Tokens")
    assert result.outcome is outcome


@pytest.mark.asyncio
async def test_required_choices_and_defaults_remain_handler_policy() -> None:
    registry = CommandRegistry()
    calls = []

    async def handler(request, execution):
        calls.append(request.args)
        return CommandOutcome(data=NoData())

    metadata = replace(
        spec("accept"),
        arguments=(CommandArgument("mode", "Mode", True, "default", ("only-choice",)),),
    )
    registry.register(metadata, handler)
    await registry.execute_text("/accept", CommandExecution())
    await registry.execute_text("/accept different Extra", CommandExecution())
    assert calls == [(), ("different", "Extra")]


@pytest.mark.asyncio
async def test_unexpected_exception_and_external_cancellation_propagate_once() -> None:
    registry = CommandRegistry()
    calls = []
    failure = RuntimeError("synthetic handler failure")

    async def raises(request, execution):
        calls.append("failure")
        raise failure

    registry.register(spec("fail"), raises)
    with pytest.raises(RuntimeError) as exc:
        await registry.execute_text("/fail", CommandExecution())
    assert exc.value is failure and calls == ["failure"]

    started = asyncio.Event()
    release = asyncio.Event()

    async def waits(request, execution):
        calls.append("cancel")
        started.set()
        await release.wait()
        return CommandOutcome(data=NoData())

    registry.register(spec("cancel"), waits)
    task = asyncio.create_task(registry.execute_text("/cancel", CommandExecution()))
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert calls == ["failure", "cancel"]
    assert registry.names() == frozenset({"fail", "cancel"})
