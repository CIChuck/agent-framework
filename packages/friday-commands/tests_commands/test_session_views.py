"""SESSION-001's model, call-boundary, ordering and standalone obligations."""

from __future__ import annotations

import asyncio
import contextlib
import os
import subprocess
import sys
from dataclasses import FrozenInstanceError, asdict, fields
from pathlib import Path
from textwrap import dedent
from types import MappingProxyType

import friday_commands as api
import pytest
from friday_commands import (
    SESSION_SPECS,
    CommandError,
    CommandExecution,
    CommandOutcome,
    CommandRegistry,
    CommandRequest,
    CommandSpec,
    ExitData,
    HelpData,
    HistoryData,
    HistoryTurn,
    NoData,
    SessionClearedData,
    UiEffect,
    build_session_handlers,
)

PACKAGE_SRC = Path(__file__).resolve().parents[1] / "src"
BY_NAME = {spec.name: spec for spec in SESSION_SPECS}
Z = HistoryTurn("z user", "z reply")
A = HistoryTurn("a user", "a reply")


def request(name: str) -> CommandRequest:
    return CommandRequest(name, ("ignored", '"quoted', 'words"'), BY_NAME[name])


class Port:
    def __init__(self, turns=(Z, A, A)):
        self.turns = turns
        self.events = []

    def history_snapshot(self):
        self.events.append("snapshot")
        return self.turns

    def clear_history(self):
        self.events.append("history.clear")
        self.turns = ()

    async def clear_session_memory(self):
        self.events.append("memory.clear")


class NoReads:
    def __getattribute__(self, name):
        raise AssertionError("Unexpected port/object access: " + name)


class TurnSubclass(HistoryTurn):
    pass


class HistorySubclass(HistoryData):
    pass


class ClearedSubclass(SessionClearedData):
    pass


class RequestSubclass(CommandRequest):
    pass


class ExecutionSubclass(CommandExecution):
    pass


@pytest.mark.parametrize(
    "factory",
    [
        lambda: HistoryTurn(1, "reply"),
        lambda: HistoryTurn("user", None),
        lambda: HistoryTurn(b"user", "reply"),
        lambda: HistoryData(None),
        lambda: HistoryData(1),
        lambda: HistoryData("turn"),
        lambda: HistoryData(b"turn"),
        lambda: HistoryData(bytearray(b"turn")),
        lambda: HistoryData({"turn": Z}),
        lambda: HistoryData(("not a turn",)),
        lambda: HistoryData((NoData(),)),
        lambda: HistoryData((TurnSubclass("u", "a"),)),
        lambda: SessionClearedData(1),
        lambda: SessionClearedData(unexpected=True),
        lambda: CommandOutcome(data=Z),
        lambda: CommandOutcome(data=HistorySubclass(())),
        lambda: CommandOutcome(data=ClearedSubclass()),
    ],
)
def test_models_snapshot_and_reject_invalid_values(factory) -> None:
    with pytest.raises(TypeError) as error:
        factory()
    assert type(error.value) is TypeError


def test_model_snapshot_is_once_only_frozen_and_keeps_strings() -> None:
    class Once:
        calls = 0

        def __iter__(self):
            self.calls += 1
            if self.calls != 1:
                raise AssertionError("Iterable read twice")
            return iter((Z, A, A))

    class String(str):
        def __str__(self):
            raise AssertionError("A model converted an accepted string subclass")

    value = String("user")
    turn = HistoryTurn(value, "reply")
    assert turn.user_message is value
    once = Once()
    assert HistoryData(once).turns == (Z, A, A)
    assert once.calls == 1
    original = [Z, A]
    snapshot = HistoryData(original)
    original.append(Z)
    assert snapshot.turns == (Z, A)
    assert tuple(field.name for field in fields(HistoryTurn)) == (
        "user_message",
        "assistant_message",
    )
    assert tuple(field.name for field in fields(HistoryData)) == ("turns",)
    assert fields(SessionClearedData) == ()
    for model, attribute, replacement in (
        (turn, "user_message", "changed"),
        (snapshot, "turns", ()),
    ):
        with pytest.raises(FrozenInstanceError):
            setattr(model, attribute, replacement)
        assert not hasattr(model, "__dict__")
    marker = SessionClearedData()
    assert not hasattr(marker, "__dict__")
    with pytest.raises((AttributeError, TypeError)):
        marker.extra = True


@pytest.mark.parametrize(
    "data",
    [NoData(), HelpData(()), ExitData(), HistoryData((Z,)), SessionClearedData()],
)
def test_outcome_union_addition_preserves_old_invariants(data) -> None:
    assert CommandOutcome(data=data).data is data
    with pytest.raises(ValueError):
        CommandOutcome(data=data, error=CommandError("failed", "history"))
    with pytest.raises(ValueError):
        CommandOutcome(
            error=CommandError("failed", "history"), ui_effects=(UiEffect.CLEAR_SCREEN,)
        )
    with pytest.raises(ValueError):
        CommandOutcome()
    for unknown in ({}, "text", True, object()):
        with pytest.raises(TypeError):
            CommandOutcome(data=unknown)


def test_session_specs_and_factory_are_immutable() -> None:
    assert tuple(asdict(spec) for spec in SESSION_SPECS) == (
        dict(
            name="clear",
            description="Clear conversation history.",
            category="session",
            usage="/clear",
            aliases=(),
            arguments=(),
            detail=None,
        ),
        dict(
            name="history",
            description="Show conversation history.",
            category="session",
            usage="/history",
            aliases=(),
            arguments=(),
            detail=None,
        ),
    )
    # Future approved API expansions must explicitly revise this unit's surface.
    assert api.__all__ == [
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
    assert CommandRegistry().names() == frozenset()
    first = build_session_handlers(NoReads())
    second = build_session_handlers(NoReads())
    assert isinstance(first, MappingProxyType)
    assert first is not second
    assert set(first) == {"clear", "history"}
    with pytest.raises(TypeError):
        first["other"] = first["clear"]
    with pytest.raises(FrozenInstanceError):
        SESSION_SPECS[0].name = "changed"
    assert CommandRegistry().names() == frozenset()


@pytest.mark.asyncio
@pytest.mark.parametrize("turns", [(), (Z, A, A), [Z, A, A]])
async def test_history_snapshot_once_preserves_order(turns) -> None:
    port = Port(turns)
    outcome = await build_session_handlers(port)["history"](
        request("history"), CommandExecution()
    )
    assert type(outcome) is CommandOutcome
    assert type(outcome.data) is HistoryData
    assert outcome.data.turns == tuple(turns)
    assert outcome.ui_effects == () and outcome.error is None
    assert port.events == ["snapshot"]
    if isinstance(turns, list):
        turns.append(HistoryTurn("later", "later"))
        assert outcome.data.turns == (Z, A, A)


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["history", "clear"])
async def test_history_ignores_unrelated_fields(name, monkeypatch) -> None:
    current_request = request(name)
    current_execution = CommandExecution("unused")
    original = CommandRequest.__getattribute__
    reads = []

    def request_read(self, key):
        if key == "__class__":
            return original(self, key)
        reads.append(key)
        if key != "name":
            raise AssertionError("Ignored request field was read: " + key)
        return original(self, key)

    def execution_read(self, key):
        raise AssertionError("Execution field was read: " + key)

    monkeypatch.setattr(CommandRequest, "__getattribute__", request_read)
    monkeypatch.setattr(CommandExecution, "__getattribute__", execution_read)
    port = Port()
    outcome = await build_session_handlers(port)[name](
        current_request, current_execution
    )
    assert reads == ["name"]
    assert type(outcome.data) is (
        HistoryData if name == "history" else SessionClearedData
    )
    assert port.events == (
        ["snapshot"] if name == "history" else ["history.clear", "memory.clear"]
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value",
    [None, 1, "turn", b"turn", {"turn": Z}, ("bad",), (TurnSubclass("u", "a"),)],
)
async def test_invalid_snapshot_is_not_repaired(value) -> None:
    port = Port(value)
    with pytest.raises(TypeError):
        await build_session_handlers(port)["history"](
            request("history"), CommandExecution()
        )
    assert port.events == ["snapshot"]


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel", [False, True])
async def test_clear_orders_history_before_memory_await(cancel) -> None:
    entered = asyncio.Event()
    release = asyncio.Event()

    class BlockingPort(Port):
        async def clear_session_memory(self):
            assert self.turns == ()
            self.events.append("memory.enter")
            entered.set()
            await release.wait()
            self.events.append("memory.return")

    port = BlockingPort()
    task = asyncio.create_task(
        build_session_handlers(port)["clear"](request("clear"), CommandExecution())
    )
    try:
        await asyncio.wait_for(entered.wait(), timeout=3)
        assert port.turns == ()
        assert not task.done()
        assert port.events == ["history.clear", "memory.enter"]
        if cancel:
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            assert port.events == ["history.clear", "memory.enter"]
            assert port.turns == ()
        else:
            release.set()
            outcome = await asyncio.wait_for(task, timeout=3)
            assert type(outcome.data) is SessionClearedData
            assert outcome.error is None and outcome.ui_effects == ()
            assert port.events == ["history.clear", "memory.enter", "memory.return"]
    finally:
        release.set()
        if not task.done():
            task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


@pytest.mark.asyncio
@pytest.mark.parametrize("phase", ["snapshot", "history.clear", "memory.clear"])
@pytest.mark.parametrize("kind", [RuntimeError, asyncio.CancelledError])
async def test_clear_failure_and_cancellation_boundaries(phase, kind) -> None:
    failure = kind("sentinel")

    class FailingPort(Port):
        def history_snapshot(self):
            self.events.append("snapshot")
            raise failure

        def clear_history(self):
            self.events.append("history.clear")
            if phase == "history.clear":
                raise failure
            self.turns = ()

        async def clear_session_memory(self):
            self.events.append("memory.clear")
            raise failure

    port = FailingPort()
    name = "history" if phase == "snapshot" else "clear"
    with pytest.raises(kind) as error:
        await build_session_handlers(port)[name](request(name), CommandExecution())
    assert error.value is failure
    assert port.events == (
        ["snapshot"]
        if phase == "snapshot"
        else ["history.clear"]
        if phase == "history.clear"
        else ["history.clear", "memory.clear"]
    )
    assert port.turns == (() if phase == "memory.clear" else (Z, A, A))


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["clear", "history"])
@pytest.mark.parametrize(
    "case",
    [
        "both-invalid",
        "request-subclass",
        "execution-invalid",
        "execution-subclass",
        "wrong-name-invalid-execution",
        "wrong-name",
        "other-name",
    ],
)
async def test_invocation_validation_precedes_port_access(
    name, case, monkeypatch
) -> None:
    handlers = build_session_handlers(NoReads())
    req = request(name)
    execution = CommandExecution()
    expected = TypeError
    match = (
        "CommandRequest"
        if case in ("both-invalid", "request-subclass")
        else "CommandExecution"
    )
    if case == "both-invalid":
        req, execution = NoReads(), NoReads()
    elif case == "request-subclass":
        req = RequestSubclass(name, (), BY_NAME[name])
    elif case == "execution-invalid":
        execution = NoReads()
    elif case == "execution-subclass":
        execution = ExecutionSubclass()
    else:
        other = (
            "other"
            if case == "other-name"
            else "history"
            if name == "clear"
            else "clear"
        )
        req = CommandRequest(other, (), CommandSpec(other, "Other", "test", "/other"))
        if case == "wrong-name-invalid-execution":
            execution = NoReads()
        else:
            expected, match = ValueError, "session handler"
    original = CommandRequest.__getattribute__

    def fields(self, key):
        if key == "__class__":
            return original(self, key)
        if key != "name" or case in (
            "request-subclass",
            "execution-invalid",
            "execution-subclass",
            "wrong-name-invalid-execution",
        ):
            raise AssertionError("Field read before invocation checks: " + key)
        return original(self, key)

    monkeypatch.setattr(CommandRequest, "__getattribute__", fields)
    with pytest.raises(expected, match=match):
        await handlers[name](req, execution)


@pytest.mark.parametrize("optimize", [[], ["-O"], ["-OO"]])
def test_standalone_session_dispatch(optimize) -> None:
    guards = [
        str(Path(item).resolve())
        for item in os.environ.get("PYTHONPATH", "").split(os.pathsep)
        if item
        and (Path(item) / "sitecustomize.py").is_file()
        and (Path(item) / "pilot_guard.py").is_file()
    ]
    script = dedent(
        f"""
        import asyncio, hashlib, json, runpy, sys
        from pathlib import Path
        guards = {guards!r}
        if guards:
            prepared = Path(guards[0])
            bootstrap = json.loads((prepared/'bootstrap.json').read_text())
            for name, key in [('sitecustomize.py','combined_guard_sha256'), ('pilot_guard.py','guard_extension_sha256')]:
                if hashlib.sha256((prepared/name).read_bytes()).hexdigest() != bootstrap[key]:
                    raise RuntimeError('Standalone guard drift')
            sys.path.insert(0,str(prepared))
            runpy.run_path(str(prepared/'sitecustomize.py'))
            sys.path.pop(0)
        source = Path({str(PACKAGE_SRC)!r}).resolve()
        sys.path.insert(0,str(source))
        class StdlibOnly:
            def find_spec(self, fullname, path=None, target=None):
                if fullname.split('.')[0] != 'friday_commands' and fullname.split('.')[0] not in sys.stdlib_module_names:
                    raise ModuleNotFoundError(fullname)
        sys.meta_path.insert(0,StdlibOnly())
        from friday_commands import SESSION_SPECS, CommandExecution, CommandOutcome, CommandRegistry, CommandRequest, HistoryData, HistoryTurn, SessionClearedData, build_session_handlers
        class TurnSubclass(HistoryTurn): pass
        class HistorySubclass(HistoryData): pass
        class ClearedSubclass(SessionClearedData): pass
        class Port:
            def __init__(self):
                self.turns = (HistoryTurn('z','Z'),HistoryTurn('a','A'))
                self.events = []
            def history_snapshot(self):
                self.events.append('snapshot'); return self.turns
            def clear_history(self):
                self.events.append('clear'); self.turns=()
            async def clear_session_memory(self):
                self.events.append('memory')
        async def main():
            port=Port(); handlers=build_session_handlers(port); registry=CommandRegistry()
            if registry.names() or port.events: raise RuntimeError('Unexpected implicit state')
            for spec in SESSION_SPECS: registry.register(spec,handlers[spec.name])
            for invalid in [lambda:HistoryTurn(1,'a'),lambda:HistoryTurn('u',None),lambda:HistoryData(['bad']),lambda:HistoryData([TurnSubclass('u','a')]),lambda:SessionClearedData(1),lambda:CommandOutcome(data=HistorySubclass(())),lambda:CommandOutcome(data=ClearedSubclass())]:
                try: invalid()
                except TypeError: pass
                else: raise RuntimeError('Runtime model checks bypassed')
            for name in ['clear','history']:
                req=CommandRequest(name,(),next(spec for spec in SESSION_SPECS if spec.name==name))
                for bad_req,bad_exec in [(object(),CommandExecution()),(req,object())]:
                    try: await handlers[name](bad_req,bad_exec)
                    except TypeError: pass
                    else: raise RuntimeError('Runtime invocation type checks bypassed')
                other=next(spec for spec in SESSION_SPECS if spec.name!=name)
                try: await handlers[name](CommandRequest(other.name,(),other),CommandExecution())
                except ValueError: pass
                else: raise RuntimeError('Canonical invocation check bypassed')
            if port.events: raise RuntimeError('Invalid invocation reached port')
            history=await registry.execute_text('/HiStOrY ignored',CommandExecution('unused'))
            if type(history.outcome.data) is not HistoryData or history.outcome.data.turns != port.turns:
                raise RuntimeError('Standalone history changed')
            cleared=await registry.execute_text('/clear extra',CommandExecution())
            if type(cleared.outcome.data) is not SessionClearedData or cleared.outcome.ui_effects or port.turns:
                raise RuntimeError('Standalone clear changed')
            if port.events != ['snapshot','clear','memory']: raise RuntimeError('Wrong standalone calls')
            if CommandRegistry().names(): raise RuntimeError('Global registry populated')
        asyncio.run(main())
        for name,module in tuple(sys.modules.items()):
            if name.startswith('friday'):
                if not name.startswith('friday_commands'): raise RuntimeError('Host module imported')
                file=getattr(module,'__file__',None)
                paths=([file] if file else [])+list(getattr(module,'__path__',()))
                if not paths or not all(Path(path).resolve().is_relative_to(source) for path in paths):
                    raise RuntimeError('Standalone module escaped source')
        print('Standalone SESSION passed')
        """
    )
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-S", *optimize, "-c", script],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "Standalone SESSION passed"
