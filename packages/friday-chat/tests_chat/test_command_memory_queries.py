"""MEMQ Chat compatibility, exact projection ownership and persisted listing."""

from __future__ import annotations

import asyncio
import builtins
import hashlib
import json
import os
from contextlib import suppress
from dataclasses import FrozenInstanceError, asdict, fields
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace as NS

import friday_commands as api
import friday_commands.memory_queries as shared
import pytest
from friday_chat import memory_views as mv
from friday_chat.adapters import FrameworkMemoryAdapter
from friday_chat.app import FridayChatApp, ListInputSource, ListOutputSink
from friday_chat.commands import memory as mem
from friday_chat.commands import memory_queries as host
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

NAMES = ("memory", "insights", "summaries", "meta", "entities", "list-ingested")
FIXTURE_PATH = Path(__file__).parent / "fixtures/memory-query-baseline.json"
FIXTURE = json.loads(FIXTURE_PATH.read_text())
MARKER = CommandMetadata("unused", "Unused", "unused", "/unused")


def _handler(name):
    return (
        getattr(mem, name + "_handler")
        if name in ("memory", "insights", "summaries", "meta")
        else getattr(reg, "_" + name.replace("-", "_") + "_handler")
    )


async def _capture_memory_queries():
    from types import SimpleNamespace as NS

    from friday_chat import memory_views as mv
    from friday_chat.commands import memory as mem
    from friday_chat.commands import registry as reg
    from friday_chat.commands.contracts import (
        CommandContext,
        CommandMetadata,
        CommandResult,
    )
    from friday_chat.commands.registry import CommandRegistry, build_default_registry

    M, R, W, C = (
        mv.MemoryMetric,
        mv.MemoryDiagnosticReason,
        mv.MemoryDiagnosticWarning,
        mv.MemoryStoreComponent,
    )
    rows = []
    marker = CommandMetadata("unused", "Unused", "unused", "/unused")
    events = []

    class Trace:
        def __init__(self, label, **values):
            object.__setattr__(self, "_label", label)
            self.__dict__.update(values)

        def __getattribute__(self, name):
            if not name.startswith("_"):
                events.append(object.__getattribute__(self, "_label") + "." + name)
            return object.__getattribute__(self, name)

    def store(**overrides):
        values = dict(
            episodic_turns=M.available(3),
            vector_short_term=M.available(0),
            vector_long_term=M.available(12),
            vector_decayed=M.not_configured(),
            vector_active_total=M.available(12),
            vector_total=M.unavailable(R.STORE_READ_FAILED),
            graph_nodes=M.available(5),
            graph_relationships=M.available(4),
            lifecycle_enabled=M.available(False),
            access_buffer_entries=M.available(2),
            access_buffer_accesses=M.available(9),
            priming_enabled=M.available(True),
            priming_previous_sessions=M.not_configured(),
            warnings=(
                W(C.VECTOR_LONG_TERM),
                W(C.GRAPH, R.COMPONENT_INITIALIZATION_FAILED),
                W(C.VECTOR_LONG_TERM),
            ),
        )
        values.update(overrides)
        return mv.MemoryStoreStatistics(**values)

    def at(label):
        return datetime(2026, 11, 9, 1, 2, 3, tzinfo=UTC) if label else None

    def record(
        kind,
        index=0,
        *,
        full=False,
        text=None,
        collection=mv.MemoryCollection.SHORT_TERM,
    ):
        base = dict(
            record_id=f"rec-{index:03d}",
            kind=kind,
            text=text if text is not None else f"record {index}\ttext\n",
            collection=collection,
        )
        if full:
            base.update(
                lifecycle_stage="active",
                created_at=at(True),
                confidence=0.12345,
                source_count=0,
                provenance_source_type="synthesis",
                source_memory_ids=("a", "b"),
                provenance_truncated=True,
                verification_status="verified",
                verification_confidence=0.9,
            )
        return mv.MemoryRecordView(**base)

    class Memory:
        def __init__(
            self,
            label="memory",
            *,
            statistics=None,
            stats_failure=None,
            records=None,
            records_failure=None,
            entities=(),
            relationships=(),
            entity_failure=None,
            relationship_failure=None,
            documents=None,
            entered=None,
            release=None,
        ):
            self.label, self.statistics, self.stats_failure = (
                label,
                statistics,
                stats_failure,
            )
            self.records, self.records_failure = records or {}, records_failure
            self.entities, self.relationships = list(entities), list(relationships)
            self.entity_failure, self.relationship_failure = (
                entity_failure,
                relationship_failure,
            )
            self.entered, self.release = entered, release
            if documents is not None:
                self.ingested_documents = documents

        async def _pause(self):
            if self.entered is not None:
                self.entered.set()
                await self.release.wait()

        async def query_memory_statistics(self):
            events.append("memory.query_memory_statistics")
            await self._pause()
            if self.stats_failure is not None:
                raise self.stats_failure
            return self.statistics

        async def query_memory_records(self, kind):
            events.append("memory.query_memory_records:" + kind.value)
            await self._pause()
            if self.records_failure is not None:
                raise self.records_failure
            return (
                self.records[kind]
                if kind in self.records
                else mv.MemoryRecordQueryResult(kind, ())
            )

        async def list_entities(self, name=None):
            events.append("memory.list_entities:" + repr(name))
            await self._pause()
            if self.entity_failure is not None:
                raise self.entity_failure
            return self.entities

        async def list_relationships(self, name=None):
            events.append("memory.list_relationships:" + repr(name))
            if self.relationship_failure is not None:
                raise self.relationship_failure
            return self.relationships

        def __getattribute__(self, name):
            if name == "ingested_documents":
                events.append("memory.ingested_documents")
            return object.__getattribute__(self, name)

    class Transcript:
        def __init__(self, entries=(), failure=None):
            self.entries, self.failure = list(entries), failure

        async def query_entries(self, session_id):
            events.append("transcript.query_entries:" + session_id)
            if self.failure is not None:
                raise self.failure
            return self.entries

    def runtime(memory=None, transcript=None, session_id="session-1"):
        return Trace(
            "runtime",
            memory=memory if memory is not None else Memory(),
            transcript=transcript
            if transcript is not None
            else Transcript(("e1", "e2")),
            session_identity=Trace("identity", value=session_id),
        )

    budget = NS(
        total_tokens=900,
        message_tokens=700,
        tool_tokens=0,
        available_budget=100,
        utilization_pct=87.25,
        severity=NS(value="warning"),
    )

    def context(**values):
        defaults = dict(
            runtime=None,
            history=[("u", "a")],
            variables={"x": "1"},
            last_budget_status=None,
            session=None,
        )
        defaults.update(values)
        return Trace("context", **defaults)

    def normalize(value):
        if isinstance(value, dict):
            return {k: normalize(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [normalize(v) for v in value]
        return value

    def handler(name):
        return (
            getattr(mem, name + "_handler")
            if name in ("memory", "insights", "summaries", "meta")
            else getattr(reg, "_" + name.replace("-", "_") + "_handler")
        )

    async def run(label, name, ctx, args=(), failure=None):
        events.clear()
        row = {"case": label, "command": name, "args": list(args)}
        try:
            result = await handler(name)(ctx, args, marker)
            row["result"] = asdict(result)
        except BaseException as error:
            row["exception"] = {"type": type(error).__name__, "message": str(error)}
            if failure is not None:
                row["exception"]["same_object"] = error is failure
        row["events"] = list(events)
        rows.append(normalize(row))

    # /memory
    await run("memory:runtime-missing", "memory", context(), ("ignored",))
    await run(
        "memory:full",
        "memory",
        context(
            runtime=runtime(memory=Memory(statistics=store())),
            last_budget_status=budget,
            session=Trace("session", turn_ids=["t1", "t2", "t3"]),
        ),
        ("ignored",),
    )
    await run(
        "memory:no-turn-no-session",
        "memory",
        context(runtime=runtime(memory=Memory(statistics=store(warnings=())))),
    )
    await run(
        "memory:store-failure",
        "memory",
        context(
            runtime=runtime(
                memory=Memory(stats_failure=RuntimeError("secret store detail"))
            )
        ),
    )
    await run(
        "memory:transcript-failure",
        "memory",
        context(
            runtime=runtime(
                memory=Memory(statistics=store()),
                transcript=Transcript(failure=OSError("secret transcript")),
            )
        ),
    )
    await run(
        "memory:both-failures",
        "memory",
        context(
            runtime=runtime(
                memory=Memory(stats_failure=ValueError("x")),
                transcript=Transcript(failure=KeyError("y")),
            )
        ),
    )
    cancel = asyncio.CancelledError("stats cancelled")
    await run(
        "memory:store-cancel",
        "memory",
        context(runtime=runtime(memory=Memory(stats_failure=cancel))),
        (),
        cancel,
    )
    cancel = asyncio.CancelledError("transcript cancelled")
    await run(
        "memory:transcript-cancel",
        "memory",
        context(
            runtime=runtime(
                memory=Memory(statistics=store()), transcript=Transcript(failure=cancel)
            )
        ),
        (),
        cancel,
    )
    zero_budget = NS(
        total_tokens=0,
        message_tokens=0,
        tool_tokens=0,
        available_budget=-5,
        utilization_pct=0.04,
        severity=NS(value=""),
    )
    await run(
        "memory:zero-budget-empty-session",
        "memory",
        context(
            runtime=runtime(
                memory=Memory(statistics=store(warnings=())), transcript=Transcript(())
            ),
            history=[],
            variables={},
            last_budget_status=zero_budget,
            session=Trace("session", turn_ids=[]),
        ),
    )
    await run(
        "memory:session-id-control-text",
        "memory",
        context(
            runtime=runtime(
                memory=Memory(statistics=store(warnings=())),
                session_id="id\twith\x00control " + "x" * 300,
            )
        ),
    )
    await run(
        "memory:all-not-configured",
        "memory",
        context(
            runtime=runtime(
                memory=Memory(
                    statistics=mv.MemoryStoreStatistics(*([M.not_configured()] * 13))
                )
            ),
            last_budget_status=budget,
        ),
    )

    # /insights, /summaries, /meta
    kinds = {
        "insights": mv.MemoryRecordKind.INSIGHT,
        "summaries": mv.MemoryRecordKind.SUMMARY,
        "meta": mv.MemoryRecordKind.META_INSIGHT,
    }
    for name, kind in kinds.items():
        await run(name + ":runtime-missing", name, context(), ("ignored",))
        await run(
            name + ":empty-complete", name, context(runtime=runtime()), ("ignored",)
        )
        incomplete = mv.MemoryRecordQueryResult(
            kind, (), (W(C.MEMORY_RECORD), W(C.VECTOR_SHORT_TERM), W(C.MEMORY_RECORD))
        )
        await run(
            name + ":empty-incomplete",
            name,
            context(runtime=runtime(memory=Memory(records={kind: incomplete}))),
        )
        populated = mv.MemoryRecordQueryResult(
            kind,
            (
                record(kind, 1),
                record(kind, 2, full=True, collection=mv.MemoryCollection.LONG_TERM),
            ),
            (W(C.VECTOR_DECAYED),),
        )
        await run(
            name + ":populated",
            name,
            context(runtime=runtime(memory=Memory(records={kind: populated}))),
        )
        many = mv.MemoryRecordQueryResult(
            kind,
            tuple(
                record(kind, i, text="x" * 170 if i == 0 else None) for i in range(103)
            ),
        )
        await run(
            name + ":over-limit",
            name,
            context(runtime=runtime(memory=Memory(records={kind: many}))),
        )
        failure = RuntimeError("secret query detail")
        await run(
            name + ":query-failure",
            name,
            context(runtime=runtime(memory=Memory(records_failure=failure))),
        )
        cancel = asyncio.CancelledError("query cancelled")
        await run(
            name + ":query-cancel",
            name,
            context(runtime=runtime(memory=Memory(records_failure=cancel))),
            (),
            cancel,
        )
    other = mv.MemoryRecordQueryResult(
        mv.MemoryRecordKind.META_INSIGHT, (record(mv.MemoryRecordKind.META_INSIGHT, 7),)
    )
    await run(
        "insights:service-returns-meta-kind",
        "insights",
        context(
            runtime=runtime(memory=Memory(records={mv.MemoryRecordKind.INSIGHT: other}))
        ),
    )
    other = mv.MemoryRecordQueryResult(mv.MemoryRecordKind.INSIGHT, ())
    await run(
        "meta:service-returns-insight-kind-empty",
        "meta",
        context(
            runtime=runtime(
                memory=Memory(records={mv.MemoryRecordKind.META_INSIGHT: other})
            )
        ),
    )
    sparse = mv.MemoryRecordQueryResult(
        mv.MemoryRecordKind.META_INSIGHT,
        (
            mv.MemoryRecordView(
                "m" * 100,
                mv.MemoryRecordKind.META_INSIGHT,
                "",
                mv.MemoryCollection.SHORT_TERM,
                verification_confidence=0.5,
            ),
        ),
    )
    await run(
        "meta:sparse-record",
        "meta",
        context(
            runtime=runtime(
                memory=Memory(records={mv.MemoryRecordKind.META_INSIGHT: sparse})
            )
        ),
    )

    # /entities
    ents = [
        {"label": "Alice", "type": "person", "hit_count": 3},
        {"id": "n2", "type": None, "hit_count": 0},
        {"label": None, "id": "n3"},
        {},
    ]
    rels = [
        {
            "source_label": "Alice",
            "relation": "knows",
            "target_label": "Bob",
            "hit_count": 2,
        },
        {"source_id": "s", "type": "linked", "target_id": "t", "hit_count": None},
        {},
    ]
    for label, args in [
        ("all", ()),
        ("nodes", ("nodes",)),
        ("nodes-extra", ("nodes", "x")),
        ("name", ("Alice", "Smith")),
        ("upper-nodes", ("NODES",)),
        ("quoted", ('"a', 'b"')),
    ]:
        await run(
            "entities:" + label,
            "entities",
            context(runtime=runtime(memory=Memory(entities=ents, relationships=rels))),
            args,
        )
    await run("entities:runtime-missing", "entities", context(), ("nodes",))
    await run("entities:empty", "entities", context(runtime=runtime()))
    await run(
        "entities:nodes-empty",
        "entities",
        context(runtime=runtime(memory=Memory(relationships=rels))),
        ("nodes",),
    )
    await run(
        "entities:relationships-only",
        "entities",
        context(runtime=runtime(memory=Memory(relationships=rels))),
    )
    await run(
        "entities:entities-only",
        "entities",
        context(runtime=runtime(memory=Memory(entities=ents))),
    )
    await run(
        "entities:over-limit",
        "entities",
        context(
            runtime=runtime(
                memory=Memory(
                    entities=[{"label": f"e{i}"} for i in range(103)],
                    relationships=[{"relation": f"r{i}"} for i in range(101)],
                )
            )
        ),
    )
    failure = RuntimeError("entity failure")
    await run(
        "entities:entity-failure",
        "entities",
        context(
            runtime=runtime(memory=Memory(entity_failure=failure, relationships=rels))
        ),
        (),
        failure,
    )
    failure = RuntimeError("relationship failure")
    await run(
        "entities:relationship-failure",
        "entities",
        context(
            runtime=runtime(memory=Memory(entities=ents, relationship_failure=failure))
        ),
        (),
        failure,
    )
    cancel = asyncio.CancelledError("entity cancelled")
    await run(
        "entities:entity-cancel",
        "entities",
        context(runtime=runtime(memory=Memory(entity_failure=cancel))),
        (),
        cancel,
    )
    await run(
        "entities:bad-record",
        "entities",
        context(runtime=runtime(memory=Memory(entities=["not-a-mapping"]))),
    )
    await run(
        "entities:unicode-values",
        "entities",
        context(
            runtime=runtime(
                memory=Memory(
                    entities=[{"label": "Å\nname", "type": 1.5, "hit_count": False}]
                )
            )
        ),
    )

    # /list-ingested
    await run("list-ingested:runtime-missing", "list-ingested", context(), ("ignored",))
    await run(
        "list-ingested:attribute-missing", "list-ingested", context(runtime=runtime())
    )
    await run(
        "list-ingested:empty",
        "list-ingested",
        context(runtime=runtime(memory=Memory(documents=[]))),
    )
    docs = [
        {"source_path": "/a/b.md", "chunk_count": 2, "description": "Doc"},
        {"source_path": "c.txt", "chunk_count": 0, "description": None},
        {"source_path": "Å\nd", "chunk_count": "3", "description": ""},
        {"source_path": 7, "chunk_count": 1.5, "description": 0},
    ]
    await run(
        "list-ingested:documents",
        "list-ingested",
        context(runtime=runtime(memory=Memory(documents=docs))),
        ("ignored",),
    )
    await run(
        "list-ingested:missing-key",
        "list-ingested",
        context(runtime=runtime(memory=Memory(documents=[{"source_path": "x"}]))),
    )
    await run(
        "list-ingested:falsy-non-list",
        "list-ingested",
        context(runtime=runtime(memory=Memory(documents=None))),
    )
    await run(
        "list-ingested:tuple",
        "list-ingested",
        context(
            runtime=runtime(
                memory=Memory(
                    documents=(
                        {"source_path": "t", "chunk_count": 1, "description": "d"},
                    )
                )
            )
        ),
    )

    # Awaited-service observation while pending
    entered, release = asyncio.Event(), asyncio.Event()
    memory = Memory(statistics=store(warnings=()), entered=entered, release=release)
    events.clear()
    task = asyncio.create_task(
        mem.memory_handler(context(runtime=runtime(memory=memory)), (), marker)
    )
    try:
        await asyncio.wait_for(entered.wait(), 5)
        during = {"task_done": task.done(), "events": list(events)}
        release.set()
        result = await asyncio.wait_for(task, 5)
        rows.append(
            {
                "case": "memory:await",
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
        "/MEMORY extra",
        "/insights a b",
        "/summaries",
        "/meta --full",
        "/entities nodes",
        '/entities "a b" c',
        "/list-ingested x",
        " /memory",
        "//memory",
        "/ entities",
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
    for name in NAMES:
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


@pytest.mark.asyncio
async def test_memory_query_metadata_and_frozen_cases(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert (
        hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest()
        == "0403471ba7bc293320e0dc2d0420c01859ec67b706f35f4cfd631ea9be47a272"
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
        assert (
            json.loads(json.dumps(asdict(host.memory_query_metadata(name))))
            == FIXTURE["metadata"][name]
        )
        assert (
            json.loads(json.dumps(asdict(registry.commands[name])))
            == FIXTURE["metadata"][name]
        )
    actual = json.loads(json.dumps(await _capture_memory_queries()))
    assert json.loads(json.dumps(actual["metadata"])) == FIXTURE["metadata"]
    assert len(actual["cases"]) == len(FIXTURE["cases"]) == 76
    kind_refusals = {
        "insights:service-returns-meta-kind",
        "meta:service-returns-insight-kind-empty",
    }
    repaired = {
        "list-ingested:" + label
        for label in (
            "attribute-missing",
            "empty",
            "documents",
            "missing-key",
            "falsy-non-list",
            "tuple",
        )
    }
    counts = [0, 0, 0]
    for row, expected in zip(actual["cases"], FIXTURE["cases"], strict=True):
        assert row["case"] == expected["case"]
        if row["case"] in kind_refusals:
            assert "exception" in row and "result" not in row
            assert row["exception"]["type"] == "ValueError"
            assert {k: v for k, v in row.items() if k != "exception"} == {
                k: v for k, v in expected.items() if k != "result"
            }
            counts[1] += 1
        elif row["case"] in repaired:
            # These six synthetic attribute-fallback rows are superseded by
            # the real and fake typed listing tests, never claimed unchanged.
            counts[2] += 1
        else:
            assert row == expected, row["case"]
            counts[0] += 1
    assert counts == [68, 2, 6]
    # Reuse the accepted package-local controls for all retained families.
    from test_command_diagnostics import test_diagnostic_metadata_and_frozen_cases

    await test_diagnostic_metadata_and_frozen_cases(tmp_path, monkeypatch)


@pytest.mark.asyncio
@pytest.mark.parametrize("name", NAMES)
async def test_memory_query_once_only_delegation(name, monkeypatch):
    injected = api.CommandOutcome(
        {
            "memory": api.MemoryStatisticsData((api.MemorySectionData("injected"),)),
            "insights": api.MemoryRecordsData(
                "insight", (api.MemoryRecordData(None, "insight fact", None),)
            ),
            "summaries": api.MemoryRecordsData(
                "summary", (api.MemoryRecordData(None, "summary fact", None),)
            ),
            "meta": api.MemoryQueryFailedData("meta_insight"),
            "entities": api.GraphData(
                (api.GraphEntityData("graph fact", "kind", "0"),)
            ),
            "list-ingested": api.IngestedDocumentsData(
                (api.IngestedDocumentData("injected-source", "17", "fact"),)
            ),
        }[name]
    )
    calls, ports, parses, parsed_args, supplied_args, actual_outcomes = (
        [],
        [],
        [],
        [],
        [],
        [],
    )
    original_parse, factory = (
        reg._parse_command_input,
        shared.build_memory_query_handlers,
    )

    def parse(text):
        parses.append(text)
        value = original_parse(text)
        parsed_args.append(value[1])
        return value

    def request(command_name, args, spec):
        supplied_args.append(args)
        return api.CommandRequest(command_name, args, spec)

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
    monkeypatch.setattr(shared, "build_memory_query_handlers", build)
    context = RegistryCommandContext(registry=CommandRegistry())
    text = "/" + name.upper() + ' "quoted words" //q'
    handled, result = await build_default_registry().execute(text, context)
    assert handled and result == host.adapt_memory_query_outcome(injected)
    assert parses == [text]
    assert len(calls) == len(ports) == len(actual_outcomes) == 1
    assert supplied_args[0] is parsed_args[0]
    value, execution = calls[0]
    assert type(value) is api.CommandRequest and type(execution) is api.CommandExecution
    assert value.name == name and value.args == ('"quoted', 'words"', "//q")
    assert value.spec is next(s for s in shared.MEMORY_QUERY_SPECS if s.name == name)
    assert ports[0].context is context
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
            raise AssertionError("Unexpected context read: " + attr)

    tripwire = Tripwire()
    assert host.ChatMemoryQueryPort(tripwire).context is tripwire
    before = len(ports)
    with pytest.raises(TypeError):
        await _handler(name)(tripwire, (1,), object())
    assert len(ports) == before

    async def own(context, args, metadata):
        return CommandResult("custom:" + metadata.name)

    monkeypatch.setattr(
        shared,
        "build_memory_query_handlers",
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


def _store(**changes):
    values = {
        f.name: mv.MemoryMetric.available(0)
        for f in fields(mv.MemoryStoreStatistics)
        if f.name != "warnings"
    }
    values.update(
        lifecycle_enabled=mv.MemoryMetric.available(False),
        priming_enabled=mv.MemoryMetric.available(True),
        vector_decayed=mv.MemoryMetric.not_configured(),
        warnings=(),
    )
    values.update(changes)
    return mv.MemoryStoreStatistics(**values)


def _context(memory, events=None, *, transcript=None, budget=None):
    events = [] if events is None else events

    class Transcript:
        async def query_entries(self, session_id):
            events.append("transcript.query")
            return []

    runtime = _Trace(
        events,
        "runtime",
        memory=memory,
        transcript=Transcript() if transcript is None else transcript,
        session_identity=NS(value="session"),
    )
    return _Trace(
        events,
        "context",
        runtime=runtime,
        last_budget_status=budget,
        session=None,
        history=[],
        variables={},
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mode",
    [
        "normal",
        "failures",
        "store-cancel",
        "transcript-cancel",
        "pending",
        "format-once",
    ],
)
async def test_memory_statistics_projection_order_and_failures(mode, monkeypatch):
    events = []
    entered, release = asyncio.Event(), asyncio.Event()
    failure = asyncio.CancelledError("identity")

    class Float(float):
        def __format__(self, spec):
            events.append("format:" + spec)
            return float.__format__(self, spec)

    class Text(str):
        def __str__(self):
            raise AssertionError("raw string coerced")

    warnings = (
        mv.MemoryDiagnosticWarning(mv.MemoryStoreComponent.GRAPH),
        mv.MemoryDiagnosticWarning(mv.MemoryStoreComponent.EPISODIC),
        mv.MemoryDiagnosticWarning(mv.MemoryStoreComponent.GRAPH),
    )
    store = _store(
        warnings=warnings, graph_nodes=mv.MemoryMetric.available(Float(2.25))
    )

    class Memory:
        async def query_memory_statistics(self):
            events.append("statistics.query")
            if mode == "pending":
                entered.set()
                await release.wait()
            if mode == "failures":
                raise RuntimeError("secret")
            if mode == "store-cancel":
                raise failure
            return store

    class Transcript:
        async def query_entries(self, session_id):
            events.append("transcript.query")
            if mode == "failures":
                raise OSError("secret")
            if mode == "transcript-cancel":
                raise failure
            return []

    budget = NS(
        total_tokens=0,
        message_tokens=0,
        tool_tokens=0,
        available_budget=-1,
        utilization_pct=Float(0.04),
        severity=NS(value=Text("warning")),
    )
    context = _context(Memory(), events, transcript=Transcript(), budget=budget)
    previews = []
    original = host.preview_text

    def preview(value, *, limit=160):
        previews.append((value, limit))
        return original(value, limit=limit)

    monkeypatch.setattr(host, "preview_text", preview)
    if mode.endswith("cancel"):
        caught = None
        try:
            await mem.memory_handler(context, (), MARKER)
        except BaseException as error:
            caught = error
        assert caught is failure
        assert events.count("statistics.query") == 1
        assert events.count("transcript.query") == int(mode == "transcript-cancel")
        return
    if mode == "pending":
        task = asyncio.create_task(mem.memory_handler(context, (), MARKER))
        try:
            await asyncio.wait_for(entered.wait(), 2)
            assert not task.done() and "transcript.query" not in events
            release.set()
            result = await asyncio.wait_for(task, 2)
        finally:
            release.set()
            if not task.done():
                task.cancel()
            with suppress(asyncio.CancelledError):
                await task
    else:
        result = await mem.memory_handler(context, (), MARKER)
    assert events.count("context.runtime") == 5
    assert events.count("statistics.query") == events.count("transcript.query") == 1
    assert (
        events.index("statistics.query")
        < events.index("transcript.query")
        < events.index("context.last_budget_status")
        < events.index("context.session")
    )
    assert result.handled and not result.exit_requested and result.ui_effects == ()
    assert not result.output.endswith("\n")
    assert "- utilization: 0.0%" in result.output
    if mode == "failures":
        assert "episodic: store read failed" in result.output
        assert (
            "transcript: store read failed" in result.output
            and "secret" not in result.output
        )
    else:
        assert "- short_term: 0" in result.output
        assert "- decayed: not configured" in result.output
        assert "- nodes: 2.2" in result.output
        assert "- enabled: false" in result.output
        assert result.output.endswith(
            "Warnings:\n- episodic: store read failed\n- graph: store read failed"
        )
        assert events.count("format:.1f") == 2
        assert previews == [("session", 256), ("warning", 256)]


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", list(mv.MemoryRecordKind))
@pytest.mark.parametrize("mode", ["empty", "records", "cap", "error", "cancel"])
async def test_memory_record_projection_and_rendering(kind, mode, monkeypatch):
    events = []
    failure = asyncio.CancelledError("record identity")
    previews = []
    original = host.preview_text

    def preview(value, *, limit=160):
        previews.append(limit)
        return original(value, limit=limit)

    monkeypatch.setattr(host, "preview_text", preview)

    class Once:
        calls = 0

        def __iter__(self):
            self.calls += 1
            assert self.calls == 1
            events.append("ids.iter")
            yield "a"
            yield "a"

    class Float(float):
        def __format__(self, spec):
            events.append("float:" + spec)
            return float.__format__(self, spec)

    class Empty:
        def __format__(self, spec):
            events.append("empty.format")
            return ""

    class Date:
        def isoformat(self):
            events.append("date.iso")
            return ""

    class Joined(str):
        def __format__(self, spec):
            events.append("verification.format")
            return str.__format__(self, spec)

    class Status(str):
        def __add__(self, other):
            events.append("verification.concat")
            return Joined(str.__add__(self, other))

    ids = Once()
    if kind is mv.MemoryRecordKind.META_INSIGHT:
        raw = _Trace(
            events,
            "record",
            record_id="i" * 90,
            text="Å\n" + "x" * 180,
            collection=mv.MemoryCollection.SHORT_TERM,
            lifecycle_stage="",
            created_at=Date(),
            confidence=Float(0.25),
            source_count=Empty(),
            provenance_source_type="",
            source_memory_ids=ids,
            provenance_truncated=True,
            verification_status=Status("verified"),
            verification_confidence=Float(0.9),
        )
    else:

        class Plain:
            def __getattribute__(self, name):
                assert name == "text", "unused plain field: " + name
                events.append("plain.text")
                return "Å\n" + "x" * 180

        raw = Plain()
    records = () if mode == "empty" else (raw,)
    if mode == "cap":
        records = tuple(
            mv.MemoryRecordView(
                str(i), kind, "record-" + str(i), mv.MemoryCollection.SHORT_TERM
            )
            for i in range(103)
        )

    class Memory:
        async def query_memory_records(self, selected):
            events.append("query:" + selected.value)
            assert selected is kind
            if mode == "error":
                raise RuntimeError("secret")
            if mode == "cancel":
                raise failure
            return NS(kind=kind, records=records, warnings=(), complete=False)

    name = {
        mv.MemoryRecordKind.INSIGHT: "insights",
        mv.MemoryRecordKind.SUMMARY: "summaries",
        mv.MemoryRecordKind.META_INSIGHT: "meta",
    }[kind]
    context = _context(Memory(), events)
    if mode == "cancel":
        caught = None
        try:
            await _handler(name)(context, (), MARKER)
        except BaseException as error:
            caught = error
        assert caught is failure
        return
    result = await _handler(name)(context, ("ignored",), MARKER)
    assert events.count("query:" + kind.value) == 1
    assert not result.output.endswith("\n")
    if mode == "error":
        title = {
            "insights": "insights",
            "summaries": "summaries",
            "meta": "meta insights",
        }[name]
        assert result == CommandResult(f"Unable to query {title}: store read failed.")
    elif mode == "empty":
        if name == "meta":
            assert result.output.startswith("Meta insight query incomplete;")
            assert (
                "Warnings:" not in result.output and "Decayed records:" in result.output
            )
        else:
            assert result == CommandResult(f"No {name} found.")
    elif mode == "cap":
        assert (
            sum(line.startswith("- record-") for line in result.output.splitlines())
            == 100
        )
        assert "record-100" not in result.output
    elif name == "meta":
        assert ids.calls == 1 and previews == [160, 80]
        assert (
            events.index("ids.iter")
            < events.index("verification.concat")
            < events.index("record.text")
            < events.index("date.iso")
            < events.index("record.confidence")
            < events.index("verification.format")
        )
        assert events.count("record.verification_confidence") == 2
        assert (
            events.count("record.created_at")
            == events.count("record.source_count")
            == 2
        )
        assert (
            events.count("float:.3f") == 2 and events.count("verification.concat") == 1
        )
        assert "; created=\n" in result.output
        assert "; source_count=;" in result.output
        assert "source_ids=a, a, ..." in result.output
        # Prepared fields never inspect/preview/format the original objects again.
        data = api.MemoryRecordsData(
            "meta_insight",
            (
                api.MemoryRecordData(
                    "id",
                    "text",
                    "short_term",
                    created_at="",
                    confidence="",
                    verification="fact",
                ),
            ),
        )
        before = list(events)
        host.adapt_memory_query_outcome(api.CommandOutcome(data))
        assert events == before
        # Failures in raw formatting occur outside the service-read conversion.
        # Keep their identity and the original lazy failure point.
        original_record = mv.MemoryRecordView(
            "id",
            kind,
            "text",
            mv.MemoryCollection.SHORT_TERM,
            verification_status="verified",
            verification_confidence=0.5,
        )
        sentinel = RuntimeError("formatter identity")

        class RaisingFloat(float):
            def __format__(self, spec):
                raise sentinel

        class RaisingDate:
            def isoformat(self):
                raise sentinel

        class RaisingStatus(str):
            def __add__(self, other):
                raise sentinel

        class RaisingText(str):
            def __format__(self, spec):
                raise sentinel

        for field, bad_value, before_text in (
            ("verification_confidence", RaisingFloat(0.9), True),
            ("verification_status", RaisingStatus("verified"), True),
            ("created_at", RaisingDate(), False),
            ("confidence", RaisingFloat(0.2), False),
            ("lifecycle_stage", RaisingText("active"), False),
        ):
            values = {
                f.name: getattr(original_record, f.name)
                for f in fields(original_record)
            }
            values[field] = bad_value
            events.clear()
            records = (_Trace(events, "record", **values),)
            caught = None
            try:
                await _handler(name)(context, (), MARKER)
            except BaseException as error:
                caught = error
            assert caught is sentinel
            if before_text:
                assert "record.text" not in events
        values = {
            f.name: getattr(original_record, f.name) for f in fields(original_record)
        }
        values["source_memory_ids"] = (object(),)
        events.clear()
        records = (_Trace(events, "record", **values),)
        caught = None
        try:
            await _handler(name)(context, (), MARKER)
        except BaseException as error:
            caught = error
        assert type(caught) is TypeError and "record.text" not in events
    else:
        assert events.count("plain.text") == 1 and previews == [160]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mode",
    [
        "all",
        "nodes",
        "upper",
        "bad-record",
        "pending",
        "entity-error",
        "relationship-error",
        "cancel",
        "cap",
    ],
)
async def test_entities_projection_and_rendering(mode):
    events = []
    entered, release = asyncio.Event(), asyncio.Event()
    failure = (
        asyncio.CancelledError("graph identity")
        if mode == "cancel"
        else RuntimeError("graph identity")
    )

    class Record(dict):
        def get(self, key, *args):
            events.append("get:" + key)
            return super().get(key, *args)

    entities = [Record(label="A", type=0, hit_count=False)]
    relationships = [Record(source_id="s", type="r", target_id="t", hit_count=0)]
    if mode == "bad-record":
        entities = ["not a mapping"]
    if mode == "cap":
        entities = [{"label": "e" + str(i)} for i in range(103)]
        relationships = [{"relation": "r" + str(i)} for i in range(103)]

    class Memory:
        async def list_entities(self, name):
            events.append(("entities", name))
            if mode == "entity-error":
                raise failure
            return entities

        async def list_relationships(self, name):
            events.append(("relationships", name))
            if mode == "pending":
                entered.set()
                await release.wait()
            if mode in ("relationship-error", "cancel"):
                raise failure
            return relationships

    args = (
        ("nodes", "ignored")
        if mode == "nodes"
        else ("NODES",)
        if mode == "upper"
        else ()
    )
    context = _context(Memory(), events)
    if mode in ("entity-error", "relationship-error", "cancel", "bad-record"):
        caught = None
        try:
            await _handler("entities")(context, args, MARKER)
        except BaseException as error:
            caught = error
        if mode == "bad-record":
            assert type(caught) is AttributeError
            assert ("relationships", None) in events
        else:
            assert caught is failure
        return
    if mode == "pending":
        task = asyncio.create_task(_handler("entities")(context, args, MARKER))
        try:
            await asyncio.wait_for(entered.wait(), 2)
            assert not task.done() and not any(
                isinstance(e, str) and e.startswith("get:") for e in events
            )
            release.set()
            result = await asyncio.wait_for(task, 2)
        finally:
            release.set()
            if not task.done():
                task.cancel()
            with suppress(asyncio.CancelledError):
                await task
    else:
        result = await _handler("entities")(context, args, MARKER)
    if mode == "cap":
        assert sum(x.startswith("- e") for x in result.output.splitlines()) == 100
        assert sum(x.startswith("-  -[r") for x in result.output.splitlines()) == 100
        assert "e100" not in result.output and "r100" not in result.output
    else:
        assert result.output.startswith("Entities:\n- A (0), hits=False")
        if mode == "nodes":
            assert not any(
                isinstance(e, tuple) and e[0] == "relationships" for e in events
            )
        else:
            assert "\n\nRelationships:\n- s -[r]-> t, hits=0" in result.output
            assert events.index(
                ("relationships", "NODES" if mode == "upper" else None)
            ) < events.index("get:label")
    assert not result.output.endswith("\n")


@pytest.mark.parametrize(
    "value",
    [
        api.MemoryUnavailableData("runtime_missing"),
        api.MemoryStatisticsData(),
        api.MemoryRecordsData("insight"),
        api.MemoryRecordsData("summary"),
        api.MemoryRecordsData("meta_insight", complete=False),
        api.MemoryQueryFailedData("meta_insight"),
        api.GraphData(),
        api.IngestedDocumentsData(),
    ],
)
def test_memory_query_adapter_refusals_and_purity(value, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("renderer recomputed host facts")

    monkeypatch.setattr(host, "preview_text", forbidden)
    monkeypatch.setattr(host, "_runtime", forbidden)
    result = host.adapt_memory_query_outcome(api.CommandOutcome(value))
    assert (
        type(result) is CommandResult
        and result.handled
        and not result.exit_requested
        and result.ui_effects == ()
    )
    assert not result.output.endswith("\n")
    for outcome in (
        None,
        object(),
        api.CommandOutcome(error=api.CommandError("failed", "memory")),
        api.CommandOutcome(value, ui_effects=(api.UiEffect.CLEAR_SCREEN,)),
        type("Child", (api.CommandOutcome,), {})(value),
    ):
        caught = None
        try:
            host.adapt_memory_query_outcome(outcome)
        except Exception as error:
            caught = error
        assert type(caught) is ValueError
    bad_data = [
        api.NoData(),
        api.HelpData(()),
        api.ExitData(),
        api.HistoryData(()),
        api.SessionClearedData(),
        api.ContextData(""),
        api.PromptData(""),
        api.DebugData(False),
        api.BudgetData(None, None),
        api.TimingData(False),
        api.RetrievalData("", 0),
        api.RetrievalUnavailableData("query_missing"),
        {},
        object(),
    ]
    child = type("Child", (type(value),), {})(
        **{f.name: getattr(value, f.name) for f in fields(value)}
    )
    for bad in [*bad_data, child]:
        forged = object.__new__(api.CommandOutcome)
        for key, datum in {"data": bad, "error": None, "ui_effects": ()}.items():
            object.__setattr__(forged, key, datum)
        caught = None
        try:
            host.adapt_memory_query_outcome(forged)
        except Exception as error:
            caught = error
        assert type(caught) is ValueError


@pytest.mark.asyncio
async def test_memory_query_real_app_sequence(tmp_path, monkeypatch):
    config = FridayChatConfig.model_validate(
        {
            "llm": {"model": "fake/memq-uat"},
            "transcript": {"export_directory": str(tmp_path / "exports")},
        }
    )
    runtime = build_runtime(config, fake=True)
    assert isinstance(runtime.memory, FakeMemoryController)
    source = tmp_path / "document.txt"
    source.write_text("test document")
    events, invocations = [], []
    factory, close = shared.build_memory_query_handlers, runtime.async_clients.close

    def build(port):
        handlers = factory(port)

        async def invoke(request, execution):
            invocations.append(request.name)
            return await handlers[request.name](request, execution)

        return {name: invoke for name in handlers}

    monkeypatch.setattr(shared, "build_memory_query_handlers", build)

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
                *("/" + name for name in NAMES),
                "/ingest " + str(source) + " description",
                "/list-ingested",
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
    assert invocations == [*NAMES, "list-ingested"]
    assert output.values[1].startswith("Memory statistics:")
    assert output.values[6] == "No ingested documents."
    assert "- " + str(source) + " (1 chunks): description" in output.values[8]
    assert output.values[-3:] == [
        "Conversation history cleared.",
        "No conversation history.",
        "Goodbye.",
    ]
    assert (
        app.command_context.history is history
        and history == []
        and runtime.memory.stored_turns == []
    )
    assert (
        events.index("memory.clear")
        < events.index("display.clear")
        < events.index(("output", "Goodbye."))
        < events.index("close")
    )
    assert events.count("display.clear") == events.count("close") == 1
    assert not app.started and app.background.closed
    assert runtime.async_clients.close_calls == 1 and runtime.transcript.finalized


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mode",
    ["persisted", "malformed", "short-failure", "long-failure", "cancel", "fake"],
)
async def test_ingested_listing_reads_persisted_metadata(tmp_path, monkeypatch, mode):
    if mode == "fake":
        memory = FakeMemoryController()
        memory.ingested_documents = [
            {"source_path": "z", "chunk_count": 0, "description": None},
            {"source_path": "a", "chunk_count": 3, "description": "desc"},
        ]
        result = await memory.query_ingested_documents()
        assert result == mv.IngestedDocumentQueryResult(
            (
                mv.IngestedDocumentView("z", None, 0),
                mv.IngestedDocumentView("a", "desc", 3),
            )
        )
        assert (
            await _handler("list-ingested")(_context(memory), (), MARKER)
        ).output == "Ingested documents:\n- z (0 chunks): \n- a (3 chunks): desc"
        with pytest.raises(FrozenInstanceError):
            result.documents = ()
        return
    # Reuse the accepted disposable real-adapter fixture, including its
    # deterministic local embedding backend, without any active planning input.
    from test_memory_diagnostics_commands import production_runtime

    runtime = production_runtime.__wrapped__(tmp_path, monkeypatch)
    memory = runtime.memory
    assert isinstance(memory, FrameworkMemoryAdapter)
    manager = memory.collection_manager
    calls = []

    async def decayed(*args, **kwargs):
        raise AssertionError("decayed collection read")

    monkeypatch.setattr(manager.decayed, "get_all", decayed)
    registry = build_default_registry()
    context = CommandContext(runtime=runtime)

    async def command(text):
        handled, result = await registry.execute(text, context)
        assert handled and result is not None
        return result.output

    single = tmp_path / "a.txt"
    multi = tmp_path / "z.txt"
    single.write_text("single chunk content")
    multi.write_text("many words for persisted chunks.\n" * 500)
    if mode == "persisted":
        assert "Ingested file:" in await command("/ingest " + str(single) + " base")
        assert "Ingested file:" in await command("/ingest " + str(multi) + " desc")
        first = await manager.short_term.get_all(
            limit=None, where={"type": "ingested_file"}
        )
        expected_single = sum(r["metadata"]["source"] == str(single) for r in first)
        expected_multi = sum(r["metadata"]["source"] == str(multi) for r in first)
        assert expected_single == 1 and expected_multi > 1
        assert "Ingested file:" in await command("/ingest " + str(multi) + " desc")
        stored = await manager.short_term.get_all(
            limit=None, where={"type": "ingested_file"}
        )
        multi_count = sum(r["metadata"]["source"] == str(multi) for r in stored)
        assert multi_count == expected_multi * 2
        assert await manager.promote_memory(stored[0]["id"])
        # Same source but a distinct description is a separate group, None first.
        await memory.ingest_document(
            source_path=str(single), description="B", content="another chunk"
        )
        await memory.ingest_document(
            source_path=str(single), description="A", content="another chunk"
        )
        # Chroma rejects the legacy ingest path's explicit None description.
        # A valid persisted record may instead omit that optional metadata key.
        # Ingest itself is frozen; listing must handle the stored absent field.
        assert await manager.add_to_short_term(
            ["description absent"],
            [{"type": "ingested_file", "source": str(single)}],
            ids=["description-absent"],
        )
        original_open, original_stat = builtins.open, os.stat
        forbidden = {str(single), str(multi)}

        def guarded_open(path, *args, **kwargs):
            if str(path) in forbidden:
                raise AssertionError("source file opened by listing")
            return original_open(path, *args, **kwargs)

        def guarded_stat(path, *args, **kwargs):
            if str(path) in forbidden:
                raise AssertionError("source file validated by listing")
            return original_stat(path, *args, **kwargs)

        with monkeypatch.context() as scoped:
            scoped.setattr(builtins, "open", guarded_open)
            scoped.setattr(os, "stat", guarded_stat)
            output = await command("/list-ingested ignored")
        assert output == "\n".join(
            [
                "Ingested documents:",
                f"- {single} (1 chunks): ",
                f"- {single} (1 chunks): A",
                f"- {single} (1 chunks): B",
                f"- {single} (1 chunks): base",
                f"- {multi} ({multi_count} chunks): desc",
            ]
        )
        assert (await memory.query_ingested_documents()).warnings == ()
        return
    failure = (
        asyncio.CancelledError("listing identity")
        if mode == "cancel"
        else RuntimeError("secret")
    )

    async def short(*, limit, where):
        calls.append(("short", limit, where))
        if mode in ("short-failure", "cancel"):
            raise failure
        if mode == "malformed":
            return [
                object(),
                {"metadata": {}},
                {"metadata": {"source": ""}},
                {"metadata": {"source": 7}},
                {"metadata": {"source": "b", "description": None}},
                {"metadata": {"source": "b", "description": ""}},
            ]
        return [{"metadata": {"source": "b", "description": None}}]

    async def long(*, limit, where):
        calls.append(("long", limit, where))
        if mode == "long-failure":
            raise failure
        return [
            {"metadata": {"source": "a", "description": "x"}},
            {"metadata": {"source": "b", "description": None}},
        ]

    monkeypatch.setattr(manager.short_term, "get_all", short)
    monkeypatch.setattr(manager.long_term, "get_all", long)
    if mode == "cancel":
        caught = None
        try:
            await memory.query_ingested_documents()
        except BaseException as error:
            caught = error
        # gather(return_exceptions=True) reconstructs a child CancelledError.
        assert type(caught) is asyncio.CancelledError

        # A cancellation raised by the public capability itself propagates
        # through the port, neutral handler and wrapper by identity.
        class CancelMemory:
            async def query_ingested_documents(self):
                raise failure

        caught = None
        try:
            await _handler("list-ingested")(_context(CancelMemory()), (), MARKER)
        except BaseException as error:
            caught = error
        assert caught is failure
    else:
        result = await memory.query_ingested_documents()
        assert [x.source_path for x in result.documents] == sorted(
            x.source_path for x in result.documents
        )
        expected = (
            mv.MemoryStoreComponent.MEMORY_RECORD
            if mode == "malformed"
            else mv.MemoryStoreComponent.VECTOR_SHORT_TERM
            if mode == "short-failure"
            else mv.MemoryStoreComponent.VECTOR_LONG_TERM
        )
        assert result.warnings == (mv.MemoryDiagnosticWarning(expected),)
        output = await command("/list-ingested")
        assert "Warnings:" in output and "secret" not in output
        calls = calls[:2]
    assert calls == [
        ("short", None, {"type": "ingested_file"}),
        ("long", None, {"type": "ingested_file"}),
    ]
