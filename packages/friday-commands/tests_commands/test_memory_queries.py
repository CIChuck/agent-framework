"""MEMQ D1: exact neutral values, invocation boundaries and opt-in dispatch."""

from __future__ import annotations

import asyncio
import contextlib
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import FrozenInstanceError, asdict, fields, replace
from pathlib import Path
from textwrap import dedent
from types import MappingProxyType
from typing import get_args

import friday_commands as api
import friday_commands.contracts as c
import friday_commands.memory_queries as shared
import pytest

NAMES = ("memory", "insights", "summaries", "meta", "entities", "list-ingested")
KINDS = {"insights": "insight", "summaries": "summary", "meta": "meta_insight"}
BY_NAME = {s.name: s for s in shared.MEMORY_QUERY_SPECS}
ADDITIONS = (
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
ORIGINAL_API = (
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
)
W = c.MemoryWarningData("z", "reason")
M = c.MemoryMetricData("count", "available", "0")
S = c.MemorySectionData("Section", (M,))
PLAIN = c.MemoryRecordData(None, "Å\n\x00text", None)
META = c.MemoryRecordData(
    "id",
    "text",
    "long-term",
    "active",
    "now",
    "0.5",
    "2",
    "source",
    ("z", "a", "a"),
    True,
    "verified",
)
E = c.GraphEntityData("Ada", "person", "0")
REL = c.GraphRelationshipData("Ada", "knows", "Bob", "False")
D = c.IngestedDocumentData("source", "2", "description")
MODELS = [
    (c.MemoryWarningData, ("component", "reason"), ("z", "reason")),
    (
        c.MemoryMetricData,
        ("key", "state", "value", "reason"),
        ("count", "available", "0", None),
    ),
    (c.MemorySectionData, ("title", "metrics"), ("Section", (M, M))),
    (c.MemoryStatisticsData, ("sections", "warnings"), ((S, S), (W, W))),
    (
        c.MemoryRecordData,
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
        (
            "id",
            "text",
            "long-term",
            "active",
            "now",
            "0.5",
            "2",
            "source",
            ("z", "a", "a"),
            True,
            "verified",
        ),
    ),
    (
        c.MemoryRecordsData,
        ("kind", "records", "warnings", "complete"),
        ("meta_insight", (META, META), (W, W), False),
    ),
    (c.MemoryQueryFailedData, ("kind",), ("insight",)),
    (c.MemoryUnavailableData, ("reason",), ("runtime_missing",)),
    (c.GraphEntityData, ("label", "node_type", "hit_count"), ("Ada", "person", "0")),
    (
        c.GraphRelationshipData,
        ("source", "relation", "target", "hit_count"),
        ("Ada", "knows", "Bob", "False"),
    ),
    (c.GraphData, ("entities", "relationships"), ((E, E), (REL, REL))),
    (
        c.IngestedDocumentData,
        ("source_path", "chunk_count", "description"),
        ("source", "2", "description"),
    ),
    (c.IngestedDocumentsData, ("documents", "warnings"), ((D, D), (W, W))),
]
COLLECTIONS = [
    (lambda x: c.MemorySectionData("s", x), "metrics", (M, M)),
    (lambda x: c.MemoryStatisticsData(x), "sections", (S, S)),
    (lambda x: c.MemoryStatisticsData(warnings=x), "warnings", (W, W)),
    (
        lambda x: c.MemoryRecordData(None, "t", None, source_memory_ids=x),
        "source_memory_ids",
        ("z", "a", "a"),
    ),
    (lambda x: c.MemoryRecordsData("insight", x), "records", (PLAIN, PLAIN)),
    (lambda x: c.MemoryRecordsData("summary", warnings=x), "warnings", (W, W)),
    (lambda x: c.GraphData(x), "entities", (E, E)),
    (lambda x: c.GraphData(relationships=x), "relationships", (REL, REL)),
    (lambda x: c.IngestedDocumentsData(x), "documents", (D, D)),
    (lambda x: c.IngestedDocumentsData(warnings=x), "warnings", (W, W)),
]


class Text(str):
    def __str__(self):
        raise AssertionError("String must not be converted")


class NoReads:
    def __getattribute__(self, name):
        raise AssertionError("Unexpected read: " + name)


def request(name, args=()):
    return c.CommandRequest(name, args, BY_NAME[name])


def result_for(name):
    if name == "memory":
        return c.MemoryStatisticsData((S,), (W,))
    if name in KINDS:
        return c.MemoryRecordsData(KINDS[name], (META if name == "meta" else PLAIN,))
    if name == "entities":
        return c.GraphData((E,))
    return c.IngestedDocumentsData((D,), (W,))


class Port:
    """Record method access separately from call/await; forbid surplus reads."""

    METHODS = {
        "memory_available",
        "memory_statistics",
        "memory_records",
        "graph_snapshot",
        "ingested_documents",
    }

    def __init__(self, name):
        self.events = []
        self.available = True
        self.result = result_for(name)
        self.failure = None
        self.availability_failure = None
        self.entered = None
        self.release = None

    def __getattribute__(self, name):
        if name in Port.METHODS:
            object.__getattribute__(self, "events").append(("read", name))
        return object.__getattribute__(self, name)

    def memory_available(self):
        self.events.append(("available",))
        if self.availability_failure is not None:
            raise self.availability_failure
        return self.available

    async def _query(self, method, *args):
        self.events.append(("await", method, *args))
        if self.entered is not None:
            self.entered.set()
            await self.release.wait()
        if self.failure is not None:
            raise self.failure
        return self.result

    async def memory_statistics(self):
        return await self._query("memory_statistics")

    async def memory_records(self, kind):
        return await self._query("memory_records", kind)

    async def graph_snapshot(self, name, include_relationships):
        return await self._query("graph_snapshot", name, include_relationships)

    async def ingested_documents(self):
        return await self._query("ingested_documents")


def expected_events(name, args=()):
    if name in KINDS:
        method, selected = "memory_records", (KINDS[name],)
    elif name == "entities":
        nodes = bool(args) and args[0] == "nodes"
        method = "graph_snapshot"
        selected = (" ".join(args) if args and not nodes else None, not nodes)
    else:
        method = "memory_statistics" if name == "memory" else "ingested_documents"
        selected = ()
    return [
        ("read", "memory_available"),
        ("available",),
        ("read", method),
        ("await", method, *selected),
    ]


def check_model(model, names, args):
    value = model(*args)
    assert tuple(f.name for f in fields(model)) == names
    assert value.__slots__ == names
    assert not hasattr(value, "__dict__")
    assert model.__dataclass_params__.frozen
    with pytest.raises(FrozenInstanceError):
        setattr(value, names[0], None)
    for i, item in enumerate(args):
        invalid = list(args)
        invalid[i] = object()
        with pytest.raises(TypeError):
            model(*invalid)
        if isinstance(item, str):
            changed = list(args)
            changed[i] = Text(item)
            assert getattr(model(*changed), names[i]) is changed[i]
            seen = []

            class Invalid:
                def __init__(self, position):
                    self.position = position

                @property
                def __class__(self, seen=seen):
                    seen.append(self.position)
                    return object

            invalid = list(args)
            for position in range(i, len(args)):
                invalid[position] = Invalid(position)
            with pytest.raises(TypeError):
                model(*invalid)
            assert seen == [i]
    # Explicit keyword construction also pins all declaration positions.
    assert model(**dict(zip(names, args, strict=True))) == value


def check_collection(factory, attribute, values):
    class Once:
        count = 0

        def __iter__(self):
            self.count += 1
            assert self.count == 1
            yield from values

    once = Once()
    assert getattr(factory(once), attribute) == values
    assert once.count == 1
    mutable = list(values)
    snapshot = factory(mutable)
    mutable.clear()
    assert getattr(snapshot, attribute) == values
    assert type(getattr(snapshot, attribute)) is tuple
    assert getattr(factory(iter(())), attribute) == ()
    for bad in (
        None,
        7,
        True,
        "x",
        b"x",
        bytearray(b"x"),
        {},
        MappingProxyType({}),
        (object(),),
        (False,),
    ):
        with pytest.raises(TypeError):
            factory(bad)
    item = values[0]
    if isinstance(item, str):
        text = Text("Å\n\x00")
        assert getattr(factory((text,)), attribute)[0] is text
    else:
        child = type("Child", (type(item),), {})(
            **{f.name: getattr(item, f.name) for f in fields(item)}
        )
        with pytest.raises(TypeError):
            factory((child,))


def check_semantics():
    assert c.MemorySectionData("").metrics == ()
    assert c.MemoryStatisticsData() == c.MemoryStatisticsData((), ())
    assert c.MemoryRecordData(None, "", None) == c.MemoryRecordData(
        None, "", None, None, None, None, None, None, (), False, None
    )
    assert c.MemoryRecordsData("insight").complete is True
    assert c.MemoryRecordsData("meta_insight", complete=False).warnings == ()
    assert c.GraphData() == c.GraphData((), ())
    assert c.IngestedDocumentsData() == c.IngestedDocumentsData((), ())
    for state in ("available", "unavailable", "not_configured"):
        for value in (None, "", "0"):
            for reason in (None, "", "why"):
                valid = (
                    (value is not None and reason is None)
                    if state == "available"
                    else (value is None and reason is not None)
                )
                if valid:
                    metric = c.MemoryMetricData("", state, value, reason)
                    assert (metric.value, metric.reason) == (value, reason)
                else:
                    with pytest.raises(ValueError):
                        c.MemoryMetricData("", state, value, reason)
    for factory in (
        lambda x: c.MemoryMetricData("k", x, "0"),
        c.MemoryQueryFailedData,
        c.MemoryRecordsData,
        c.MemoryUnavailableData,
    ):
        for bad in (None, True, 7, object()):
            with pytest.raises(TypeError):
                factory(bad)
        with pytest.raises(ValueError):
            factory("unknown")
    for bad in (0, 1, None, "False"):
        with pytest.raises(TypeError):
            c.MemoryRecordsData("insight", complete=bad)
        with pytest.raises(TypeError):
            replace(PLAIN, provenance_truncated=bad)
    for kind in ("insight", "summary"):
        assert c.MemoryRecordsData(kind, (PLAIN, PLAIN)).records == (PLAIN, PLAIN)
        for field in fields(PLAIN):
            if field.name == "text":
                continue
            bad = (
                ("id",)
                if field.name == "source_memory_ids"
                else True
                if field.name == "provenance_truncated"
                else ""
            )
            with pytest.raises(ValueError):
                c.MemoryRecordsData(kind, (replace(PLAIN, **{field.name: bad}),))
    for record in (replace(META, record_id=None), replace(META, collection=None)):
        with pytest.raises(ValueError):
            c.MemoryRecordsData("meta_insight", (record,))
    assert c.MemoryRecordsData(
        "meta_insight", (replace(META, record_id="", collection=""),)
    ).records
    for factory, member, attr in (
        (lambda x: c.MemoryRecordsData("insight", x), PLAIN, "records"),
        (lambda x: c.GraphData(x), E, "entities"),
        (lambda x: c.GraphData(relationships=x), REL, "relationships"),
    ):
        assert len(getattr(factory([member] * 100), attr)) == 100
        with pytest.raises(ValueError):
            factory([member] * 101)
    assert len(c.IngestedDocumentsData([D] * 101).documents) == 101

    # Declaration-order failures must not touch a later iterable/string value.
    class Unread:
        def __iter__(self):
            raise AssertionError("Later field consumed")

    with pytest.raises(TypeError):
        c.MemorySectionData(False, Unread())
    with pytest.raises(ValueError):
        c.MemoryRecordsData("bad", Unread(), Unread(), 1)
    with pytest.raises(TypeError):
        c.MemoryRecordData(False, False, False, source_memory_ids=Unread())
    sentinel = RuntimeError("iterator identity")

    def failing():
        yield W
        raise sentinel

    with pytest.raises(RuntimeError) as caught:
        c.MemoryStatisticsData(warnings=failing())
    assert caught.value is sentinel
    old = (
        c.NoData(),
        c.HelpData(()),
        c.ExitData(),
        c.HistoryData(()),
        c.SessionClearedData(),
        c.ContextData(""),
        c.PromptData(""),
        c.DebugData(False),
        c.BudgetData(None, None),
        c.TimingData(False),
        c.RetrievalData("", 0),
        c.RetrievalUnavailableData("query_missing"),
    )
    new = (
        c.MemoryUnavailableData("runtime_missing"),
        c.MemoryStatisticsData(),
        c.MemoryRecordsData("insight"),
        c.MemoryQueryFailedData("summary"),
        c.GraphData(),
        c.IngestedDocumentsData(),
    )
    assert set(get_args(c.FoundationData.__value__)) == {type(v) for v in old + new}
    assert len(get_args(c.FoundationData.__value__)) == 18
    for value in old + new:
        assert c.CommandOutcome(data=value).data is value
        child = type("Child", (type(value),), {})(**asdict(value))
        with pytest.raises(TypeError):
            c.CommandOutcome(data=child)
        with pytest.raises(ValueError):
            c.CommandOutcome(data=value, error=c.CommandError("failed", "memory"))
    for nested in (W, M, S, PLAIN, E, REL, D, {}, "", object()):
        with pytest.raises(TypeError):
            c.CommandOutcome(data=nested)
    with pytest.raises(ValueError):
        c.CommandOutcome(
            error=c.CommandError("failed", "memory"),
            ui_effects=(c.UiEffect.CLEAR_SCREEN,),
        )


MODEL_CASES = [(check_model, (model, names, args)) for model, names, args in MODELS]
MODEL_CASES += [(check_collection, args) for args in COLLECTIONS]
MODEL_CASES += [(check_semantics, ())]


@pytest.mark.parametrize("check,arguments", MODEL_CASES)
def test_memory_query_models_and_closed_union(check, arguments):
    check(*arguments)


def test_memory_query_specs_exports_and_factory():
    assert api.__all__ == list(ORIGINAL_API + ADDITIONS)
    assert len(api.__all__) == len(set(api.__all__)) == 54
    for name in ADDITIONS[:13]:
        assert getattr(api, name) is getattr(c, name)
    for name in ADDITIONS[13:]:
        assert getattr(api, name) is getattr(shared, name)
    assert not hasattr(api, "MemoryRecordKindName")
    assert get_args(c.MemoryRecordKindName) == ("insight", "summary", "meta_insight")
    fixture = Path(__file__).parent / "fixtures/memory-query-metadata.json"
    assert (
        hashlib.sha256(fixture.read_bytes()).hexdigest()
        == "a2b848e67b1ee033e22d22a5e1c96a672979e674f5b1ec0fd9e82f6f7aee6480"
    )
    assert tuple(s.name for s in shared.MEMORY_QUERY_SPECS) == NAMES
    assert type(shared.MEMORY_QUERY_SPECS) is tuple
    assert json.dumps(
        {s.name: asdict(s) for s in shared.MEMORY_QUERY_SPECS}, sort_keys=True
    ) == json.dumps(json.loads(fixture.read_text()), sort_keys=True)
    with pytest.raises(FrozenInstanceError):
        shared.MEMORY_QUERY_SPECS[0].name = "changed"
    first = shared.build_memory_query_handlers(NoReads())
    second = shared.build_memory_query_handlers(NoReads())
    assert type(first) is MappingProxyType
    assert first is not second
    assert tuple(first) == tuple(second) == NAMES
    for name in NAMES:
        assert first[name] is not second[name]
    with pytest.raises(TypeError):
        first["other"] = first["memory"]
    assert api.CommandRegistry().names() == frozenset()
    with pytest.raises(TypeError):
        isinstance(NoReads(), shared.MemoryQueryPort)
    assert set(shared.MemoryQueryPort.__protocol_attrs__) == Port.METHODS


@pytest.mark.asyncio
@pytest.mark.parametrize("name", NAMES)
async def test_memory_query_invocation_validation_order(name, monkeypatch):
    handler = shared.build_memory_query_handlers(NoReads())[name]
    with pytest.raises(TypeError, match="CommandRequest"):
        await handler(NoReads(), NoReads())
    child = type("Child", (c.CommandRequest,), {})(name, (), BY_NAME[name])
    with pytest.raises(TypeError, match="CommandRequest"):
        await handler(child, NoReads())
    req = request(name)
    with pytest.raises(TypeError, match="CommandExecution"):
        await handler(req, type("Child", (c.CommandExecution,), {})())
    with monkeypatch.context() as scoped:

        def forbidden(self, field):
            raise AssertionError("Request read before execution validation")

        scoped.setattr(c.CommandRequest, "__getattribute__", forbidden)
        with pytest.raises(TypeError, match="CommandExecution"):
            await handler(req, NoReads())
    for other in NAMES:
        if other != name:
            with pytest.raises(ValueError):
                await handler(request(other), c.CommandExecution())
    for bad in (None, 1, False, object()):
        with pytest.raises(TypeError):
            request(name, (bad,))
    custom = c.CommandRequest(
        name, (Text("ignored"),), c.CommandSpec(name, "Other", "test", "/other")
    )
    execution = c.CommandExecution("session")
    reads = []
    original = c.CommandRequest.__getattribute__

    def read(self, field):
        reads.append(field)
        if field not in ("name", "args"):
            raise AssertionError("Unused request field " + field)
        return original(self, field)

    def execution_read(self, field):
        raise AssertionError("Execution read " + field)

    monkeypatch.setattr(c.CommandRequest, "__getattribute__", read)
    monkeypatch.setattr(c.CommandExecution, "__getattribute__", execution_read)
    p = Port(name)
    result = await shared.build_memory_query_handlers(p)[name](custom, execution)
    assert reads[0] == "name"
    assert result.data is p.result
    if name != "entities":
        assert reads == ["name"]
    assert p.events == expected_events(name, ("ignored",))


@pytest.mark.asyncio
@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize(
    "mode",
    (
        "success",
        "unavailable",
        "invalid_bool",
        "invalid_result",
        "subclass_result",
        "pending",
        "task_cancel",
        "error",
        "cancel",
        "availability_error",
        "availability_cancel",
    ),
)
async def test_memory_query_availability_and_single_await(name, mode, monkeypatch):
    p = Port(name)
    handler = shared.build_memory_query_handlers(p)[name]
    if mode == "unavailable":
        p.available = False
        for args in (
            (),
            ("nodes",),
            ("NODES",),
            ("x", "y"),
            ("",),
            (Text("nodes"), "extra"),
        ):
            p.events.clear()
            req = request(name, args)
            original = c.CommandRequest.__getattribute__

            def read(self, field, original=original):
                if field == "args":
                    raise AssertionError("Arguments inspected before availability")
                return original(self, field)

            with monkeypatch.context() as scoped:
                scoped.setattr(c.CommandRequest, "__getattribute__", read)
                result = await handler(req, c.CommandExecution())
            assert result == c.CommandOutcome(
                data=c.MemoryUnavailableData("runtime_missing")
            )
            assert p.events == [("read", "memory_available"), ("available",)]
        return
    if mode == "invalid_bool":
        for bad in (None, 0, 1, "yes", [], object()):
            p.events.clear()
            p.available = bad
            error = None
            try:
                await handler(request(name), c.CommandExecution())
            except Exception as caught:
                error = caught
            assert type(error) is TypeError
            assert p.events == [("read", "memory_available"), ("available",)]
        return
    if mode in ("error", "cancel", "availability_error", "availability_cancel"):
        failure = (
            asyncio.CancelledError("sentinel")
            if "cancel" in mode
            else RuntimeError("sentinel")
        )
        if mode.startswith("availability"):
            p.availability_failure = failure
        else:
            p.failure = failure
        caught = None
        try:
            await handler(request(name), c.CommandExecution())
        except BaseException as error:
            caught = error
        assert caught is failure
        assert p.events == (
            expected_events(name)[:2]
            if mode.startswith("availability")
            else expected_events(name)
        )
        return
    if mode in ("invalid_result", "subclass_result"):
        values = [
            None,
            c.NoData(),
            {},
            object(),
            c.MemoryUnavailableData("runtime_missing"),
        ]
        if mode == "subclass_result":
            values = [
                type("Child", (type(p.result),), {})(
                    **{f.name: getattr(p.result, f.name) for f in fields(p.result)}
                )
            ]
        for bad in values:
            p.result = bad
            p.events.clear()
            caught = None
            try:
                await handler(request(name), c.CommandExecution())
            except Exception as error:
                caught = error
            assert type(caught) is TypeError
            assert p.events == expected_events(name)
        return
    if mode in ("pending", "task_cancel"):
        p.entered, p.release = asyncio.Event(), asyncio.Event()
        task = asyncio.create_task(handler(request(name), c.CommandExecution()))
        try:
            await asyncio.wait_for(p.entered.wait(), 2)
            assert not task.done()
            assert p.events == expected_events(name)
            if mode == "task_cancel":
                marker = object()
                task.cancel(marker)
                with pytest.raises(asyncio.CancelledError) as caught:
                    await task
                assert caught.value.args == (marker,)
                assert p.events == expected_events(name)
                return
            p.release.set()
            result = await asyncio.wait_for(task, 2)
        finally:
            p.release.set()
            if not task.done():
                task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
    else:
        caught = None
        result = None
        try:
            result = await handler(
                request(name, ("ignored",) if name != "entities" else ()),
                c.CommandExecution(),
            )
        except Exception as error:
            caught = error
        assert caught is None
    assert result == c.CommandOutcome(data=p.result)
    assert result.data is p.result
    assert result.error is None and result.ui_effects == ()
    assert p.events == expected_events(name)


@pytest.mark.asyncio
async def test_record_kind_and_graph_selection():
    for name, kind in KINDS.items():
        for args in ((), ("nodes",), ("summary", "ignored")):
            for value in (c.MemoryRecordsData(kind), c.MemoryQueryFailedData(kind)):
                p = Port(name)
                p.result = value
                result = await shared.build_memory_query_handlers(p)[name](
                    request(name, args), c.CommandExecution()
                )
                assert result.data is value
                assert p.events == expected_events(name)
        for wrong in set(KINDS.values()) - {kind}:
            for value in (c.MemoryRecordsData(wrong), c.MemoryQueryFailedData(wrong)):
                p = Port(name)
                p.result = value
                caught = None
                try:
                    await shared.build_memory_query_handlers(p)[name](
                        request(name), c.CommandExecution()
                    )
                except Exception as error:
                    caught = error
                assert type(caught) is ValueError
                assert p.events == expected_events(name)
    for args, selection in (
        ((), (None, True)),
        (("nodes",), (None, False)),
        (("nodes", "ignored"), (None, False)),
        ((Text("nodes"),), (None, False)),
        (("NODES",), ("NODES", True)),
        (("Ada", "Lovelace"), ("Ada Lovelace", True)),
        (('"Ada', 'Lovelace"'), ("Ada Lovelace", True)),
        (("",), ("", True)),
        (("", "a", ""), (" a ", True)),
    ):
        p = Port("entities")
        if selection[1]:
            p.result = c.GraphData((E,), (REL,))
        caught = None
        value = None
        try:
            value = await shared.build_memory_query_handlers(p)["entities"](
                request("entities", args), c.CommandExecution()
            )
        except Exception as error:
            caught = error
        assert caught is None
        assert value.data is p.result
        assert p.events == [
            ("read", "memory_available"),
            ("available",),
            ("read", "graph_snapshot"),
            ("await", "graph_snapshot", *selection),
        ]
    p = Port("entities")
    p.result = c.GraphData(relationships=(REL,))
    caught = None
    try:
        await shared.build_memory_query_handlers(p)["entities"](
            request("entities", ("nodes",)), c.CommandExecution()
        )
    except Exception as error:
        caught = error
    assert type(caught) is ValueError
    assert p.events == expected_events("entities", ("nodes",))


@pytest.mark.parametrize("optimization", [(), ("-O",), ("-OO",)])
def test_memory_queries_standalone(optimization):
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
    assert prepared is not None, "Use the pinned guarded runner"
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
        before=set(sys.modules)
        class OnlyStdlib:
            def find_spec(self,fullname,path=None,target=None):
                if fullname.split('.')[0] not in sys.stdlib_module_names and fullname.split('.')[0]!='friday_commands':
                    raise ModuleNotFoundError(fullname)
        sys.meta_path.insert(0,OnlyStdlib())
        import friday_commands as a
        def require(ok):
            if not ok: raise RuntimeError('Standalone boundary failed')
        def refused(factory,kind):
            try: factory()
            except kind: return
            raise RuntimeError('Invariant disabled')
        class P:
            def memory_available(self): return True
            async def memory_statistics(self): return a.MemoryStatisticsData()
            async def memory_records(self,kind): return a.MemoryRecordsData(kind)
            async def graph_snapshot(self,name,include_relationships): return a.GraphData()
            async def ingested_documents(self): return a.IngestedDocumentsData()
        async def main():
            registry=a.CommandRegistry(); require(not registry.names())
            handlers=a.build_memory_query_handlers(P())
            for spec in a.MEMORY_QUERY_SPECS: registry.register(spec,handlers[spec.name])
            expected=(a.MemoryStatisticsData,a.MemoryRecordsData,a.MemoryRecordsData,a.MemoryRecordsData,a.GraphData,a.IngestedDocumentsData)
            for spec,kind in zip(a.MEMORY_QUERY_SPECS,expected,strict=True):
                result=await registry.execute_text('/'+spec.name.upper(),a.CommandExecution())
                require(result.handled and type(result.outcome.data) is kind)
                require(result.outcome.error is None and result.outcome.ui_effects==())
                try: await handlers[spec.name](object(),object())
                except TypeError: pass
                else: raise RuntimeError('Request guard disabled')
                try: await handlers[spec.name](a.CommandRequest(spec.name,(),spec),object())
                except TypeError: pass
                else: raise RuntimeError('Execution guard disabled')
            refused(lambda:a.MemoryMetricData('k','available'),ValueError)
            refused(lambda:a.MemoryRecordsData('bad'),ValueError)
            refused(lambda:a.MemoryRecordsData('meta_insight',(a.MemoryRecordData(None,'t',None),)),ValueError)
            refused(lambda:a.MemoryRecordsData('insight',complete=1),TypeError)
            refused(lambda:a.CommandOutcome(data=a.GraphEntityData('','','')),TypeError)
            refused(lambda:a.GraphData((a.GraphEntityData('','',''),)*101),ValueError)
            class Wrong(P):
                async def memory_records(self,kind): return a.MemoryQueryFailedData('summary')
            try: await a.build_memory_query_handlers(Wrong())['insights'](a.CommandRequest('insights',(),a.MEMORY_QUERY_SPECS[1]),a.CommandExecution())
            except ValueError: pass
            else: raise RuntimeError('Kind guard disabled')
            class Unavailable(P):
                def memory_available(self): return False
            handlers=a.build_memory_query_handlers(Unavailable())
            for spec in a.MEMORY_QUERY_SPECS:
                result=await handlers[spec.name](a.CommandRequest(spec.name,('nodes',),spec),a.CommandExecution())
                require(result.data==a.MemoryUnavailableData('runtime_missing'))
        asyncio.run(main())
        intended=Path({str(source)!r}).resolve()/'friday_commands'
        for name,module in tuple(sys.modules.items()):
            if name=='friday_commands' or name.startswith('friday_commands.'):
                file=getattr(module,'__file__',None)
                require(file and Path(file).resolve().is_relative_to(intended))
            elif name not in before:
                require(name.split('.')[0] in sys.stdlib_module_names)
        print('Standalone memory queries passed')
    """)
    result = subprocess.run(
        [sys.executable, "-I", "-B", *optimization, "-c", script],
        capture_output=True,
        text=True,
        check=False,
        timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "Standalone memory queries passed"
