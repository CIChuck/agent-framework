"""DIAG-001's neutral model, orchestration and isolated execution obligations."""

from __future__ import annotations

import asyncio
import contextlib
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import FrozenInstanceError, asdict, fields
from inspect import signature
from itertools import product
from pathlib import Path
from textwrap import dedent
from types import MappingProxyType
from typing import get_args

import friday_commands as api
import friday_commands.contracts as contracts
import friday_commands.diagnostics as shared
import friday_commands.pilot as pilot_module
import friday_commands.registry as registry_module
import friday_commands.session_views as session_module
import pytest
from friday_commands import (
    DIAGNOSTIC_SPECS,
    BudgetData,
    CommandError,
    CommandExecution,
    CommandOutcome,
    CommandRegistry,
    CommandRequest,
    CommandSpec,
    ContextData,
    DebugData,
    DebugTurnData,
    DiagnosticField,
    DiagnosticsPort,
    ExitData,
    FoundationData,
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
    build_diagnostic_handlers,
)

BY_NAME = {spec.name: spec for spec in DIAGNOSTIC_SPECS}
NAMES = ("context", "prompt", "debug", "debug-budget", "timing", "debug-retrieval")
Z = DiagnosticField("z", "last")
A = DiagnosticField("a", "first")
COUNTER = TimingCounter("tool", "ok", "2")
DEBUG_TURN = DebugTurnData("turn", "ok", "stored", "2", "0")
TIMING_TURN = TimingTurnData("1.235", "ok", "stored", (COUNTER,))
MODELS = [
    (DiagnosticField, ("key", "value")),
    (ContextData, ("text", 4, "path")),
    (PromptData, ("text", "path")),
    (DebugTurnData, ("turn", "ok", "stored", "2", "0")),
    (DebugData, (True, (Z, A, A), DEBUG_TURN)),
    (BudgetData, ("1000", "100")),
    (TimingCounter, ("tool", "ok", "2")),
    (TimingTurnData, ("1.235", "ok", "stored", (COUNTER,))),
    (TimingData, (True, (Z, A, A), TIMING_TURN)),
    (RetrievalData, ("query", 3, (Z, A, A), ("z", "a", "a"))),
    (RetrievalUnavailableData, ("runtime_missing",)),
]
PAYLOADS = [
    ContextData("text"),
    PromptData("text"),
    DebugData(False),
    BudgetData(None, None),
    TimingData(False),
    RetrievalData("query", 0),
    RetrievalUnavailableData("query_missing"),
]
COLLECTIONS = [
    (lambda value: DebugData(True, value), "fields", (Z, A, A)),
    (lambda value: TimingData(True, value), "fields", (Z, A, A)),
    (
        lambda value: TimingTurnData("0", "ok", "stored", value),
        "counters",
        (COUNTER,) * 2,
    ),
    (lambda value: RetrievalData("q", 0, value), "fields", (Z, A, A)),
    (lambda value: RetrievalData("q", 0, previews=value), "previews", ("z", "a", "a")),
]


class Text(str):
    pass


class NoReads:
    def __getattribute__(self, name):
        raise AssertionError("Unexpected read: " + name)


class Port:
    def __init__(self):
        self.events = []
        self.text = "Å\ntext"
        self.path = "scratch/export.txt"
        self.snapshot = None
        self.available = True
        self.debug = DebugData(True, (Z, A, A), DEBUG_TURN)
        self.budget = BudgetData("1000", "100")
        self.timing = TimingData(True, (Z, A, A), TIMING_TURN)

    def context_text(self):
        self.events.append("context_text")
        return self.text

    def context_debug_snapshot(self):
        self.events.append("context_debug_snapshot")
        if self.snapshot is not None:
            return self.snapshot
        return ContextData(self.text, len(self.text))

    def prompt_text(self):
        self.events.append("prompt_text")
        return self.text

    def export_context(self, data):
        self.events.append(("export_context", data))
        return self.path

    def export_prompt(self, data):
        self.events.append(("export_prompt", data))
        return self.path

    def debug_snapshot(self):
        self.events.append("debug_snapshot")
        return self.debug

    def budget_snapshot(self):
        self.events.append("budget_snapshot")
        return self.budget

    def timing_snapshot(self):
        self.events.append("timing_snapshot")
        return self.timing

    def retrieval_available(self):
        self.events.append("available")
        return self.available

    async def retrieve(self, query):
        self.events.append(("retrieve", query))
        return RetrievalData(query, 12, (Z, A, A), ("preview",))


def request(name, args=()):
    return CommandRequest(name, args, BY_NAME[name])


def _check_diagnostic_models_and_closed_union(model, args):
    value = model(*args)
    assert not hasattr(value, "__dict__")
    assert tuple(value.__slots__) == tuple(f.name for f in fields(model))
    with pytest.raises(FrozenInstanceError):
        setattr(value, fields(model)[0].name, "changed")
    for index in range(len(args)):
        invalid = list(args)
        invalid[index] = object()
        with pytest.raises(TypeError):
            model(*invalid)
    # Neutral constructors retain string subclass identity, without conversion.
    for index, item in enumerate(args):
        if isinstance(item, str):
            changed = list(args)
            changed[index] = Text(item)
            assert getattr(model(*changed), fields(model)[index].name) is changed[index]


def _check_outcome_accepts_exact_diagnostic_variants(value):
    assert CommandOutcome(data=value).data is value
    subclass = type("Subclass", (type(value),), {})
    child = subclass(**{f.name: getattr(value, f.name) for f in fields(value)})
    with pytest.raises(TypeError):
        CommandOutcome(data=child)
    with pytest.raises(ValueError):
        CommandOutcome(data=value, error=CommandError("failed", "context"))


def _check_closed_union_retains_old_variants_and_refuses_nested_values():
    expected = {type(x) for x in PAYLOADS} | {
        NoData,
        HelpData,
        ExitData,
        HistoryData,
        SessionClearedData,
    }
    assert set(get_args(FoundationData.__value__)) == expected
    for value in (
        NoData(),
        HelpData(()),
        ExitData(),
        HistoryData(()),
        SessionClearedData(),
    ):
        assert CommandOutcome(data=value).data is value
    for value in (Z, DEBUG_TURN, COUNTER, TIMING_TURN, object(), "text", {}):
        with pytest.raises(TypeError):
            CommandOutcome(data=value)


def _check_model_type_refusals(factory):
    with pytest.raises(TypeError):
        factory()


def _check_model_value_refusals(factory):
    with pytest.raises(ValueError):
        factory()


def _check_model_optional_and_empty_edges():
    assert ContextData("", 0, "").export_path == ""
    assert ContextData("", None, None).character_count is None
    assert PromptData("", None).export_path is None
    assert BudgetData(None, "").context_window is None
    assert DebugData(True).recorded is True
    assert TimingData(True).recorded is True
    assert len(RetrievalData("", 0, previews=("x",) * 10).previews) == 10
    assert TimingTurnData("NaN", "", "").seconds == "NaN"
    text = Text("preview")
    assert RetrievalData("q", 0, previews=(text,)).previews[0] is text
    with pytest.raises(ValueError):
        CommandOutcome(
            error=CommandError("failed", "context"), ui_effects=(UiEffect.CLEAR_SCREEN,)
        )


def _check_model_snapshots_once_order_and_duplicates(factory, attribute, values):
    class Once:
        def __init__(self):
            self.reads = 0

        def __iter__(self):
            self.reads += 1
            assert self.reads == 1
            yield from values

    source = Once()
    result = factory(source)
    assert source.reads == 1
    assert getattr(result, attribute) == values
    mutable = list(values)
    result = factory(mutable)
    mutable.clear()
    assert getattr(result, attribute) == values
    assert getattr(factory(()), attribute) == ()


def _check_model_collection_refusals(factory, attribute, values, invalid):
    with pytest.raises(TypeError):
        factory(invalid)


def _check_exact_collection_members(factory):
    child = type("Child", (DiagnosticField,), {})("k", "v")
    with pytest.raises(TypeError):
        factory(child)
    with pytest.raises(TypeError):
        TimingTurnData(
            "0", "o", "p", (type("Child", (TimingCounter,), {})("k", "o", "1"),)
        )


def _check_model_validation_order_and_iterator_failure():
    failure = RuntimeError("iterator sentinel")

    class Broken:
        def __iter__(self):
            raise failure

    for action in (
        lambda: DebugData(1, Broken(), object()),
        lambda: TimingData(1, Broken(), object()),
        lambda: TimingTurnData(1, "ok", "p", Broken()),
        lambda: RetrievalData(1, 0, Broken(), Broken()),
        lambda: RetrievalData("q", True, Broken(), Broken()),
    ):
        with pytest.raises(TypeError):
            action()
    for action in (
        lambda: DebugData(True, Broken(), object()),
        lambda: TimingData(True, Broken(), object()),
        lambda: TimingTurnData("0", "ok", "p", Broken()),
        lambda: RetrievalData("q", 0, Broken(), Broken()),
        lambda: RetrievalData("q", 0, previews=Broken()),
    ):
        with pytest.raises(RuntimeError) as error:
            action()
        assert error.value is failure


def test_diagnostic_specs_exports_and_factory():
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
    owners = (
        (
            contracts,
            (
                "CommandArgument",
                "CommandError",
                "CommandExecution",
                "CommandOutcome",
                "CommandRequest",
                "CommandSpec",
                "DispatchResult",
                "ExitData",
                "FoundationData",
                "HelpData",
                "HistoryData",
                "HistoryTurn",
                "NoData",
                "SessionClearedData",
                "UiEffect",
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
            ),
        ),
        (registry_module, ("CommandHandler", "CommandRegistry")),
        (
            pilot_module,
            ("PILOT_SPECS", "HelpCatalog", "build_pilot_handlers", "describe_help"),
        ),
        (session_module, ("SESSION_SPECS", "SessionPort", "build_session_handlers")),
        (shared, ("DIAGNOSTIC_SPECS", "DiagnosticsPort", "build_diagnostic_handlers")),
    )
    expected_bindings = {
        name: getattr(module, name) for module, names in owners for name in names
    }
    assert len(expected_bindings) == 38
    assert set(expected_bindings) == set(api.__all__)
    for name, expected in expected_bindings.items():
        assert getattr(api, name) is expected, name
    frozen = json.loads(
        (Path(__file__).parent / "fixtures/diagnostics-metadata.json").read_text()
    )
    metadata = {s.name: asdict(s) for s in DIAGNOSTIC_SPECS}
    assert tuple(metadata) == NAMES
    assert json.dumps(metadata, sort_keys=True) == json.dumps(frozen, sort_keys=True)
    assert type(DIAGNOSTIC_SPECS) is tuple
    with pytest.raises(FrozenInstanceError):
        DIAGNOSTIC_SPECS[0].name = "changed"
    assert CommandRegistry().names() == frozenset()
    first = build_diagnostic_handlers(NoReads())
    second = build_diagnostic_handlers(NoReads())
    assert type(first) is MappingProxyType
    assert first is not second
    assert tuple(first) == NAMES
    with pytest.raises(TypeError):
        first["other"] = first["context"]
    with pytest.raises(TypeError):
        isinstance(NoReads(), DiagnosticsPort)
    assert CommandRegistry().names() == frozenset()


@pytest.mark.asyncio
@pytest.mark.parametrize("name", NAMES)
async def test_diagnostic_invocation_validation_order(name, monkeypatch):
    handler = build_diagnostic_handlers(NoReads())[name]
    with pytest.raises(TypeError, match="CommandRequest"):
        await handler(NoReads(), NoReads())
    with pytest.raises(TypeError, match="CommandRequest"):
        await handler(
            type("RequestChild", (CommandRequest,), {})(name, (), BY_NAME[name]),
            NoReads(),
        )
    with pytest.raises(TypeError, match="CommandExecution"):
        await handler(request(name), NoReads())
    with pytest.raises(TypeError, match="CommandExecution"):
        await handler(request(name), type("ExecutionChild", (CommandExecution,), {})())
    for wrong in NAMES:
        if wrong != name:
            with pytest.raises(ValueError):
                await handler(request(wrong), CommandExecution())
    with pytest.raises(TypeError):
        request(name, (1,))
    guarded_request = request(name)

    def forbidden_read(self, field):
        raise AssertionError("Request field read before execution validation: " + field)

    with monkeypatch.context() as scoped:
        scoped.setattr(CommandRequest, "__getattribute__", forbidden_read)
        with pytest.raises(TypeError, match="CommandExecution"):
            await handler(guarded_request, NoReads())
    reads = []
    original = CommandRequest.__getattribute__

    def read(self, field):
        reads.append(field)
        if field not in ("name", "args"):
            raise AssertionError("Unused request field: " + field)
        return original(self, field)

    def execution_read(self, field):
        raise AssertionError("Execution field read: " + field)

    custom = CommandRequest(
        name, (Text("ignored"),), CommandSpec(name, "Other", "test", "/other")
    )
    execution = CommandExecution()
    monkeypatch.setattr(CommandRequest, "__getattribute__", read)
    monkeypatch.setattr(CommandExecution, "__getattribute__", execution_read)
    port = Port()
    outcome = await build_diagnostic_handlers(port)[name](custom, execution)
    assert reads[0] == "name"
    assert set(reads) <= {"name", "args"}
    assert outcome.error is None and outcome.ui_effects == ()
    if name in ("debug", "debug-budget", "timing"):
        assert reads == ["name"]


async def _check_context_prompt_flags_and_export_order(name, args):
    port = Port()
    outcome = await build_diagnostic_handlers(port)[name](
        request(name, args), CommandExecution()
    )
    count = len(port.text) if name == "context" and "--debug" in args else None
    expected = (
        ContextData(port.text, count) if name == "context" else PromptData(port.text)
    )
    selected = "context_debug_snapshot" if count is not None else name + "_text"
    if "--file" in args:
        assert port.events == [selected, ("export_" + name, expected)]
        assert port.events[1][1].export_path is None
        expected = (
            ContextData(port.text, count, port.path)
            if name == "context"
            else PromptData(port.text, port.path)
        )
    else:
        assert port.events == [selected]
    assert outcome == CommandOutcome(data=expected)


async def _check_context_length_precedes_export():
    events = []

    class Counted(str):
        def __len__(self):
            events.append("len")
            return super().__len__()

    port = Port()
    port.events = events
    port.text = Counted("abc")
    port.snapshot = ContextData(port.text, 7)
    result = await build_diagnostic_handlers(port)["context"](
        request("context", ("--debug", "--file")), CommandExecution()
    )
    assert events == [
        "context_debug_snapshot",
        ("export_context", port.snapshot),
    ]
    assert events[1][1] is port.snapshot
    assert result.data == ContextData(port.text, 7, port.path)
    assert result.data.text is port.text


async def _check_invalid_selected_text_fails_before_export(name, value):
    port = Port()
    port.text = value
    with pytest.raises(TypeError):
        await build_diagnostic_handlers(port)[name](
            request(name, ("--file",)), CommandExecution()
        )
    assert port.events == [name + "_text"]


async def _check_invalid_export_path_fails_without_repair(name, value):
    port = Port()
    port.path = value
    with pytest.raises(TypeError):
        await build_diagnostic_handlers(port)[name](
            request(name, ("--file",)), CommandExecution()
        )
    assert len(port.events) == 2
    assert port.events[0] == name + "_text"
    assert port.events[1][0] == "export_" + name


async def _check_diagnostic_snapshots_once(name, method, attribute):
    port = Port()
    expected = getattr(port, attribute)
    outcome = await build_diagnostic_handlers(port)[name](
        request(name, ("ignored",)), CommandExecution()
    )
    assert outcome.data is expected
    assert outcome.error is None and outcome.ui_effects == ()
    assert port.events == [method]
    empty = {
        "debug": DebugData(False),
        "debug-budget": BudgetData(None, None),
        "timing": TimingData(False),
    }[name]
    setattr(port, attribute, empty)
    port.events.clear()
    assert (
        await build_diagnostic_handlers(port)[name](request(name), CommandExecution())
    ).data is empty
    assert port.events == [method]
    for invalid in (
        None,
        NoData(),
        type("Child", (type(expected),), {})(
            **{f.name: getattr(expected, f.name) for f in fields(expected)}
        ),
    ):
        setattr(port, attribute, invalid)
        port.events.clear()
        with pytest.raises(TypeError):
            await build_diagnostic_handlers(port)[name](
                request(name), CommandExecution()
            )
        assert port.events == [method]


async def _check_retrieval_precedence_and_await(available, args, reason):
    port = Port()
    port.available = available
    outcome = await build_diagnostic_handlers(port)["debug-retrieval"](
        request("debug-retrieval", args), CommandExecution()
    )
    if reason:
        assert outcome == CommandOutcome(data=RetrievalUnavailableData(reason))
        assert port.events == ["available"]
    else:
        query = " ".join(args)
        assert outcome == CommandOutcome(
            data=RetrievalData(query, 12, (Z, A, A), ("preview",))
        )
        assert port.events == ["available", ("retrieve", query)]


async def _check_retrieval_availability_requires_exact_bool(value):
    port = Port()
    port.available = value
    with pytest.raises(TypeError):
        await build_diagnostic_handlers(port)["debug-retrieval"](
            request("debug-retrieval"), CommandExecution()
        )
    assert port.events == ["available"]


async def _check_invalid_retrieval_result(value, kind):
    class Invalid(Port):
        async def retrieve(self, query):
            self.events.append(("retrieve", query))
            return value

    port = Invalid()
    with pytest.raises(kind):
        await build_diagnostic_handlers(port)["debug-retrieval"](
            request("debug-retrieval", ("q",)), CommandExecution()
        )
    assert port.events == ["available", ("retrieve", "q")]


async def _check_retrieval_pending_and_cancellation(cancel):
    entered, release = asyncio.Event(), asyncio.Event()

    class Blocking(Port):
        async def retrieve(self, query):
            self.events.append(("retrieve", query))
            entered.set()
            await release.wait()
            return RetrievalData(query, 0)

    port = Blocking()
    task = asyncio.create_task(
        build_diagnostic_handlers(port)["debug-retrieval"](
            request("debug-retrieval", ("q",)), CommandExecution()
        )
    )
    try:
        await asyncio.wait_for(entered.wait(), 3)
        assert not task.done()
        assert port.events == ["available", ("retrieve", "q")]
        if cancel:
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        else:
            release.set()
            assert (await asyncio.wait_for(task, 3)).data == RetrievalData("q", 0)
        assert port.events == ["available", ("retrieve", "q")]
    finally:
        release.set()
        if not task.done():
            task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


async def _check_port_failures_propagate_once(method, name, args, kind):
    port = Port()
    failure = kind("sentinel")

    def fail(*values):
        port.events.append("failure:" + method)
        raise failure

    async def fail_async(*values):
        return fail(*values)

    setattr(port, method, fail_async if method == "retrieve" else fail)
    with pytest.raises(kind) as error:
        await build_diagnostic_handlers(port)[name](
            request(name, args), CommandExecution()
        )
    assert error.value is failure
    prefix = (
        ["context_debug_snapshot" if "--debug" in args else name + "_text"]
        if method.startswith("export_")
        else ["available"]
        if method == "retrieve"
        else []
    )
    assert port.events == prefix + ["failure:" + method]


@pytest.mark.parametrize("optimization", [(), ("-O",), ("-OO",)])
def test_diagnostics_standalone(optimization):
    source = Path(__file__).resolve().parents[1] / "src"
    prepared = next(
        (
            Path(p)
            for p in os.environ.get("PYTHONPATH", "").split(os.pathsep)
            if p
            and (Path(p) / "bootstrap.json").is_file()
            and (Path(p) / "pilot_guard.py").is_file()
        ),
        None,
    )
    assert prepared is not None, "Run through the pinned DIAG runner"
    bootstrap = json.loads((prepared / "bootstrap.json").read_text())
    assert (
        hashlib.sha256((prepared / "sitecustomize.py").read_bytes()).hexdigest()
        == bootstrap["combined_guard_sha256"]
    )
    script = dedent(f"""
        import asyncio, hashlib, json, runpy, sys
        from pathlib import Path
        prepared=Path({str(prepared)!r})
        bootstrap=json.loads((prepared/'bootstrap.json').read_text())
        if hashlib.sha256((prepared/'sitecustomize.py').read_bytes()).hexdigest()!=bootstrap['combined_guard_sha256']:
            raise RuntimeError('Guard drift')
        sys.path.insert(0,str(prepared))
        runpy.run_path(str(prepared/'sitecustomize.py'))
        sys.path.insert(0,{str(source)!r})
        class OnlyStdlib:
            def find_spec(self, fullname, path=None, target=None):
                if fullname.split('.')[0] not in sys.stdlib_module_names and fullname.split('.')[0]!='friday_commands':
                    raise ModuleNotFoundError(fullname)
        sys.meta_path.insert(0,OnlyStdlib())
        import friday_commands as api
        intended_root=Path({str(source)!r}).resolve()/'friday_commands'
        def check_source_origins():
            for name,module in tuple(sys.modules.items()):
                if name=='friday_commands' or name.startswith('friday_commands.'):
                    file=getattr(module,'__file__',None)
                    paths=([file] if file else [])+list(getattr(module,'__path__',()))
                    if not file or not all(Path(path).resolve().is_relative_to(intended_root) for path in paths):
                        raise RuntimeError('Standalone module escaped intended source: '+name)
        check_source_origins()
        class Port:
            def context_text(self): return 'abc'
            def context_debug_snapshot(self): return api.ContextData('abc',3)
            def prompt_text(self): return 'prompt'
            def export_context(self,data): return 'context.txt'
            def export_prompt(self,data): return 'prompt.txt'
            def debug_snapshot(self): return api.DebugData(False)
            def budget_snapshot(self): return api.BudgetData(None,None)
            def timing_snapshot(self): return api.TimingData(False)
            def retrieval_available(self): return True
            async def retrieve(self,query): return api.RetrievalData(query,0)
        async def main():
            registry=api.CommandRegistry()
            handlers=api.build_diagnostic_handlers(Port())
            for spec in api.DIAGNOSTIC_SPECS: registry.register(spec,handlers[spec.name])
            for name, expected in [('context',api.ContextData),('prompt',api.PromptData),('debug',api.DebugData),('debug-budget',api.BudgetData),('timing',api.TimingData),('debug-retrieval',api.RetrievalData)]:
                result=await registry.execute_text('/'+name.upper()+' q',api.CommandExecution())
                if not result.handled or type(result.outcome.data) is not expected:
                    raise RuntimeError('Standalone dispatch failed')
            custom=api.CommandSpec('renamed','Renamed','test','/renamed',aliases=('alias',))
            registry.register(custom,lambda req,exe: handlers['context'](api.CommandRequest('context',req.args,api.DIAGNOSTIC_SPECS[0]),exe))
            result=await registry.execute_text('/ALIAS --debug --file',api.CommandExecution())
            if result.outcome.data!=api.ContextData('abc',3,'context.txt'):
                raise RuntimeError('Opt-in alias failed')
            for factory in [lambda:api.ContextData('x',True),lambda:api.RetrievalData('q',-1),lambda:api.RetrievalUnavailableData('bad'),lambda:api.DebugData(False,(api.DiagnosticField('x','y'),))]:
                try: factory()
                except (TypeError,ValueError): pass
                else: raise RuntimeError('Validation disabled')
            try: await handlers['context'](object(),object())
            except TypeError: pass
            else: raise RuntimeError('Invocation validation disabled')
            if api.CommandRegistry().names(): raise RuntimeError('Default registry populated')
        asyncio.run(main())
        check_source_origins()
        if any(n.startswith(('friday_chat','friday_cli','friday_runtime')) for n in sys.modules):
            raise RuntimeError('Host imported')
        print('Standalone diagnostics passed')
    """)
    result = subprocess.run(
        [sys.executable, "-I", "-B", *optimization, "-c", script],
        capture_output=True,
        text=True,
        check=False,
        timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "Standalone diagnostics passed"


async def _check_retrieval_is_awaited_exactly_once():
    awaited = []

    class Result:
        def __await__(self):
            awaited.append("q")
            yield from ()
            return RetrievalData("q", 0)

    class AwaitedPort(Port):
        def retrieve(self, query):
            assert query == "q"
            return Result()

    failure = None
    result = None
    try:
        result = await build_diagnostic_handlers(AwaitedPort())["debug-retrieval"](
            request("debug-retrieval", ("q",)), CommandExecution()
        )
    except Exception as error:
        failure = error
    assert awaited == ["q"]
    assert failure is None
    assert result == CommandOutcome(data=RetrievalData("q", 0))


async def _check_export_path_strings_are_preserved(name, path):
    port = Port()
    port.path = path
    result = await build_diagnostic_handlers(port)[name](
        request(name, ("--file",)), CommandExecution()
    )
    assert result.data.export_path is path


async def _check_character_count_failure_prevents_export(kind):
    failure = kind("length sentinel")

    class BadLength(str):
        def __len__(self):
            raise failure

    class Measuring(Port):
        def context_debug_snapshot(self):
            self.events.append("context_debug_snapshot")
            return ContextData(self.text, len(self.text))

    port = Measuring()
    port.text = BadLength("text")
    with pytest.raises(kind) as error:
        await build_diagnostic_handlers(port)["context"](
            request("context", ("--debug", "--file")), CommandExecution()
        )
    assert error.value is failure
    assert port.events == ["context_debug_snapshot"]


async def _check_context_debug_snapshot_refusals(snapshot, kind, args):
    class Returning(Port):
        def context_debug_snapshot(self):
            self.events.append("context_debug_snapshot")
            return snapshot

    port = Returning()
    error = None
    try:
        await build_diagnostic_handlers(port)["context"](
            request("context", args), CommandExecution()
        )
    except Exception as caught:
        error = caught
    assert type(error) is kind, f"Expected exact {kind.__name__}: {error!r}"
    assert port.events == ["context_debug_snapshot"]


def _check_string_field_validation_order(model, args, index):
    seen = []

    class Invalid:
        def __init__(self, position):
            self.position = position

        @property
        def __class__(self):
            seen.append(self.position)
            return object

    values = list(args)
    for position in range(index, len(values)):
        values[position] = Invalid(position)
    with pytest.raises(TypeError):
        model(*values)
    assert seen == [index]


def _coverage_cases(check, label, specifications):
    """Carry each row's existing assertion families under its exact gate node."""
    for index, chosen in enumerate(product(*(rows for _, rows in specifications))):
        arguments = {}
        for (names, _), row in zip(specifications, chosen, strict=True):
            names = tuple(name.strip() for name in names.split(","))
            values = (row,) if len(names) == 1 else row
            arguments.update(zip(names, values, strict=True))
        yield pytest.param(
            check,
            tuple(arguments[name] for name in signature(check).parameters),
            id=f"{label}-{index}",
        )


DG_T01_CASES = [
    *_coverage_cases(
        _check_diagnostic_models_and_closed_union,
        "diagnostic_models_and_closed_union",
        [("model,args", MODELS)],
    ),
    *_coverage_cases(
        _check_outcome_accepts_exact_diagnostic_variants,
        "outcome_accepts_exact_diagnostic_variants",
        [("value", PAYLOADS)],
    ),
    *_coverage_cases(
        _check_closed_union_retains_old_variants_and_refuses_nested_values,
        "closed_union_retains_old_variants_and_refuses_nested_values",
        [],
    ),
    *_coverage_cases(
        _check_model_type_refusals,
        "model_type_refusals",
        [
            (
                "factory",
                [
                    lambda: ContextData("x", True),
                    lambda: RetrievalData("q", False),
                    lambda: DebugData(1),
                    lambda: TimingData(0),
                    lambda: DebugData(True, turn=TimingData(False)),
                    lambda: TimingData(True, turn=DEBUG_TURN),
                    lambda: DebugData(
                        True,
                        turn=type("Child", (DebugTurnData,), {})(
                            "t", "o", "p", "1", "0"
                        ),
                    ),
                    lambda: TimingData(
                        True, turn=type("Child", (TimingTurnData,), {})("0", "o", "p")
                    ),
                    lambda: RetrievalUnavailableData(None),
                    lambda: BudgetData(False, None),
                    lambda: PromptData("x", 1),
                ],
            )
        ],
    ),
    *_coverage_cases(
        _check_model_value_refusals,
        "model_value_refusals",
        [
            (
                "factory",
                [
                    lambda: ContextData("x", -1),
                    lambda: RetrievalData("q", -1),
                    lambda: DebugData(False, (Z,)),
                    lambda: DebugData(False, turn=DEBUG_TURN),
                    lambda: TimingData(False, (Z,)),
                    lambda: TimingData(False, turn=TIMING_TURN),
                    lambda: RetrievalData("q", 0, previews=("x",) * 11),
                    lambda: RetrievalUnavailableData("unknown"),
                ],
            )
        ],
    ),
    *_coverage_cases(
        _check_model_optional_and_empty_edges, "model_optional_and_empty_edges", []
    ),
    *_coverage_cases(
        _check_model_snapshots_once_order_and_duplicates,
        "model_snapshots_once_order_and_duplicates",
        [("factory,attribute,values", COLLECTIONS)],
    ),
    *_coverage_cases(
        _check_model_collection_refusals,
        "model_collection_refusals",
        [
            ("factory,attribute,values", COLLECTIONS),
            (
                "invalid",
                [
                    None,
                    7,
                    "x",
                    b"x",
                    bytearray(b"x"),
                    {},
                    MappingProxyType({}),
                    (object(),),
                ],
            ),
        ],
    ),
    *_coverage_cases(
        _check_exact_collection_members,
        "exact_collection_members",
        [
            (
                "factory",
                [
                    lambda v: DebugData(True, (v,)),
                    lambda v: TimingData(True, (v,)),
                    lambda v: RetrievalData("q", 0, (v,)),
                ],
            )
        ],
    ),
    *_coverage_cases(
        _check_model_validation_order_and_iterator_failure,
        "model_validation_order_and_iterator_failure",
        [],
    ),
    *_coverage_cases(
        _check_string_field_validation_order,
        "string_field_validation_order",
        [
            (
                "model,args,index",
                [
                    (model, args, index)
                    for model, args in MODELS
                    for index, item in enumerate(args)
                    if isinstance(item, str)
                ],
            )
        ],
    ),
]


@pytest.mark.parametrize("check,arguments", DG_T01_CASES)
def test_diagnostic_models_and_closed_union(check, arguments):
    check(*arguments)


DG_T04_CASES = [
    *_coverage_cases(
        _check_context_prompt_flags_and_export_order,
        "context_prompt_flags_and_export_order",
        [
            ("name", ["context", "prompt"]),
            (
                "args",
                [
                    (),
                    ("ignored",),
                    ("--debug",),
                    ("--file",),
                    ("--file", "--debug"),
                    ("--debug", "--file", "--debug", "--file"),
                    ("--DEBUG", "--FILE"),
                    ("ignored", "--file", "../ignored"),
                ],
            ),
        ],
    ),
    *_coverage_cases(
        _check_context_length_precedes_export, "context_length_precedes_export", []
    ),
    *_coverage_cases(
        _check_invalid_selected_text_fails_before_export,
        "invalid_selected_text_fails_before_export",
        [("name", ["context", "prompt"]), ("value", [None, False, 7, [], b"x"])],
    ),
    *_coverage_cases(
        _check_invalid_export_path_fails_without_repair,
        "invalid_export_path_fails_without_repair",
        [("name", ["context", "prompt"]), ("value", [None, False, 7, [], b"x"])],
    ),
    *_coverage_cases(
        _check_export_path_strings_are_preserved,
        "export_path_strings_are_preserved",
        [("name", ["context", "prompt"]), ("path", ["", Text("export.txt")])],
    ),
    *_coverage_cases(
        _check_character_count_failure_prevents_export,
        "character_count_failure_prevents_export",
        [("kind", [RuntimeError, asyncio.CancelledError])],
    ),
    *_coverage_cases(
        _check_context_debug_snapshot_refusals,
        "context_debug_snapshot_refusals",
        [
            (
                "snapshot,kind",
                [
                    (None, TypeError),
                    ("abc", TypeError),
                    (NoData(), TypeError),
                    (PromptData("abc"), TypeError),
                    (type("Child", (ContextData,), {})("abc", 3), TypeError),
                    (ContextData("abc"), ValueError),
                    (ContextData("abc", 3, "path"), ValueError),
                    (ContextData("abc", None, ""), ValueError),
                ],
            ),
            ("args", [("--debug",), ("--debug", "--file")]),
        ],
    ),
    *_coverage_cases(
        _check_port_failures_propagate_once,
        "port_failures_propagate_once",
        [
            (
                "method,name,args",
                [
                    row
                    for row in [
                        ("context_text", "context", ()),
                        ("context_debug_snapshot", "context", ("--debug",)),
                        ("prompt_text", "prompt", ()),
                        ("export_context", "context", ("--file",)),
                        ("export_context", "context", ("--debug", "--file")),
                        ("export_prompt", "prompt", ("--file",)),
                        ("debug_snapshot", "debug", ()),
                        ("budget_snapshot", "debug-budget", ()),
                        ("timing_snapshot", "timing", ()),
                        ("retrieval_available", "debug-retrieval", ()),
                        ("retrieve", "debug-retrieval", ("q",)),
                    ]
                    if row[1] in ("context", "prompt")
                ],
            ),
            ("kind", [RuntimeError, asyncio.CancelledError]),
        ],
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("check,arguments", DG_T04_CASES)
async def test_context_prompt_flags_and_export_order(check, arguments):
    await check(*arguments)


DG_T05_CASES = [
    *_coverage_cases(
        _check_diagnostic_snapshots_once,
        "diagnostic_snapshots_once",
        [
            (
                "name,method,attribute",
                [
                    ("debug", "debug_snapshot", "debug"),
                    ("debug-budget", "budget_snapshot", "budget"),
                    ("timing", "timing_snapshot", "timing"),
                ],
            )
        ],
    ),
    *_coverage_cases(
        _check_port_failures_propagate_once,
        "port_failures_propagate_once",
        [
            (
                "method,name,args",
                [
                    row
                    for row in [
                        ("context_text", "context", ()),
                        ("context_debug_snapshot", "context", ("--debug",)),
                        ("prompt_text", "prompt", ()),
                        ("export_context", "context", ("--file",)),
                        ("export_context", "context", ("--debug", "--file")),
                        ("export_prompt", "prompt", ("--file",)),
                        ("debug_snapshot", "debug", ()),
                        ("budget_snapshot", "debug-budget", ()),
                        ("timing_snapshot", "timing", ()),
                        ("retrieval_available", "debug-retrieval", ()),
                        ("retrieve", "debug-retrieval", ("q",)),
                    ]
                    if row[1] in ("debug", "debug-budget", "timing")
                ],
            ),
            ("kind", [RuntimeError, asyncio.CancelledError]),
        ],
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("check,arguments", DG_T05_CASES)
async def test_diagnostic_snapshots_once(check, arguments):
    await check(*arguments)


DG_T06_CASES = [
    *_coverage_cases(
        _check_retrieval_precedence_and_await,
        "retrieval_precedence_and_await",
        [
            (
                "available,args,reason",
                [
                    (False, (), "runtime_missing"),
                    (False, ("q",), "runtime_missing"),
                    (True, (), "query_missing"),
                    (True, ("hello", '"two', 'words"'), None),
                    (True, ("",), None),
                ],
            )
        ],
    ),
    *_coverage_cases(
        _check_retrieval_availability_requires_exact_bool,
        "retrieval_availability_requires_exact_bool",
        [("value", [None, 0, 1, "yes", []])],
    ),
    *_coverage_cases(
        _check_invalid_retrieval_result,
        "invalid_retrieval_result",
        [
            (
                "value,kind",
                [
                    (None, TypeError),
                    (NoData(), TypeError),
                    (type("Child", (RetrievalData,), {})("q", 0), TypeError),
                    (RetrievalData("other", 0), ValueError),
                ],
            )
        ],
    ),
    *_coverage_cases(
        _check_retrieval_pending_and_cancellation,
        "retrieval_pending_and_cancellation",
        [("cancel", [False, True])],
    ),
    *_coverage_cases(
        _check_retrieval_is_awaited_exactly_once,
        "retrieval_is_awaited_exactly_once",
        [],
    ),
    *_coverage_cases(
        _check_port_failures_propagate_once,
        "port_failures_propagate_once",
        [
            (
                "method,name,args",
                [
                    row
                    for row in [
                        ("context_text", "context", ()),
                        ("context_debug_snapshot", "context", ("--debug",)),
                        ("prompt_text", "prompt", ()),
                        ("export_context", "context", ("--file",)),
                        ("export_context", "context", ("--debug", "--file")),
                        ("export_prompt", "prompt", ("--file",)),
                        ("debug_snapshot", "debug", ()),
                        ("budget_snapshot", "debug-budget", ()),
                        ("timing_snapshot", "timing", ()),
                        ("retrieval_available", "debug-retrieval", ()),
                        ("retrieve", "debug-retrieval", ("q",)),
                    ]
                    if row[1] in ("debug-retrieval",)
                ],
            ),
            ("kind", [RuntimeError, asyncio.CancelledError]),
        ],
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("check,arguments", DG_T06_CASES)
async def test_retrieval_precedence_and_await(check, arguments):
    await check(*arguments)
