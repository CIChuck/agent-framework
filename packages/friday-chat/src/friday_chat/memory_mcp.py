"""Owned MCP memory staging and append-only transcript publication coordination."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from contextlib import suppress
from dataclasses import replace
from typing import Literal, Protocol, runtime_checkable

from friday_core.mcp import MCPIngestionPolicy, MCPToolCallProvenance
from friday_memory.models.mcp import MCPMemoryPreparation, MCPMemorySnapshot

from friday_chat.runtime import (
    MCPMemoryCapability,
    MCPTranscriptCapability,
    MCPTranscriptReceipt,
    TranscriptStore,
)
from friday_chat.tools.schemas import ToolCallRecord
from friday_chat.turns.models import InteractionTurn


class MCPMemoryPersistenceError(RuntimeError):
    def __init__(self) -> None:
        super().__init__("MCP memory transcript receipt could not be verified.")


MCPIngestionOutcome = Literal[
    "ingestion_disabled", "skipped", "pending", "published"
]
MCPIngestionObserver = Callable[[str, MCPIngestionOutcome], None]


def _observe(
    observer: MCPIngestionObserver | None,
    call: ToolCallRecord,
    outcome: MCPIngestionOutcome,
) -> None:
    if observer is not None:
        # Optional observation cannot change receipt or publication truth.
        with suppress(Exception):
            observer(call.name, outcome)


@runtime_checkable
class _ReadableMCPTranscript(MCPTranscriptCapability, Protocol):
    async def read_mcp_interaction(
        self, turn: InteractionTurn
    ) -> MCPTranscriptReceipt | None: ...


@runtime_checkable
class _VerifiableMCPMemory(MCPMemoryCapability, Protocol):
    async def verify_mcp_memory(
        self, call: ToolCallRecord, entry_id: str, policy: MCPIngestionPolicy,
        record_id: str,
    ) -> MCPMemoryPreparation: ...


def _skipped(call: ToolCallRecord) -> ToolCallRecord:
    if call.mcp_provenance is None:
        return call
    facts = MCPToolCallProvenance.model_validate(
        {
            **call.mcp_provenance.model_dump(),
            "memory_ingested": False,
            "ingestion_decision": "skipped",
            "memory_correlation_id": None,
        }
    )
    return replace(call, mcp_provenance=facts)


async def _read_receipt(
    transcript: MCPTranscriptCapability, turn: InteractionTurn
) -> MCPTranscriptReceipt | None:
    if not isinstance(transcript, _ReadableMCPTranscript):
        return None
    try:
        return await transcript.read_mcp_interaction(turn)
    except Exception:
        raise MCPMemoryPersistenceError() from None


async def _reuse_receipt(
    memory: MCPMemoryCapability,
    policy: MCPIngestionPolicy,
    turn: InteractionTurn,
    receipt: MCPTranscriptReceipt,
    observe: MCPIngestionObserver | None = None,
) -> tuple[ToolCallRecord, ...]:
    if receipt.entry_id != turn.turn_id:
        raise MCPMemoryPersistenceError()
    result: list[ToolCallRecord] = []
    facts_iter = iter(receipt.calls)
    for call in turn.tool_calls:
        if call.mcp_provenance is None:
            result.append(call)
            continue
        facts = next(facts_iter, None)
        if facts is None or facts.call_id != call.call_id:
            raise MCPMemoryPersistenceError()
        if facts.memory_ingested:
            if not isinstance(memory, _VerifiableMCPMemory) or facts.memory_correlation_id is None:
                raise MCPMemoryPersistenceError()
            prepared = await memory.verify_mcp_memory(
                call, turn.turn_id, policy, facts.memory_correlation_id
            )
            if prepared.snapshot is None or prepared.snapshot.call != facts:
                raise MCPMemoryPersistenceError()
            published = False
            with suppress(Exception):
                published = bool(await memory.publish_mcp_memory(prepared.snapshot))
            _observe(observe, call, "published" if published else "pending")
        elif facts.memory_correlation_id is not None:
            raise MCPMemoryPersistenceError()
        else:
            _observe(observe, call, "skipped")
        result.append(replace(call, mcp_provenance=facts))
    if next(facts_iter, None) is not None:
        raise MCPMemoryPersistenceError()
    return tuple(result)


async def persist_mcp_interaction(
    memory: object,
    transcript: TranscriptStore,
    policy: MCPIngestionPolicy,
    turn: InteractionTurn,
    *,
    observe: MCPIngestionObserver | None = None,
) -> tuple[ToolCallRecord, ...]:
    if not policy.long_term_memory_enabled or not any(
        c.mcp_provenance for c in turn.tool_calls
    ):
        await transcript.record_interaction(turn)
        for call in turn.tool_calls:
            if call.mcp_provenance is not None:
                _observe(observe, call, "ingestion_disabled")
        return turn.tool_calls
    if not isinstance(memory, MCPMemoryCapability) or not isinstance(
        transcript, MCPTranscriptCapability
    ):
        calls = tuple(_skipped(c) for c in turn.tool_calls)
        await transcript.record_interaction(replace(turn, tool_calls=calls))
        for call in calls:
            if call.mcp_provenance is not None:
                _observe(observe, call, "skipped")
        return calls
    existing = await _read_receipt(transcript, turn)
    if existing is not None:
        return await _reuse_receipt(memory, policy, turn, existing, observe)
    pending: list[MCPMemorySnapshot] = []
    calls_list: list[ToolCallRecord] = []
    try:
        for call in turn.tool_calls:
            if call.mcp_provenance is None:
                calls_list.append(call)
                continue
            try:
                prepared = await memory.prepare_mcp_memory(
                    call, turn.turn_id, policy
                )
            except Exception:
                raise MCPMemoryPersistenceError() from None
            if prepared.snapshot is None:
                calls_list.append(_skipped(call))
            else:
                snapshot = prepared.snapshot
                if (
                    snapshot.transcript_entry_id != turn.turn_id
                    or snapshot.call.call_id != call.call_id
                    or snapshot.call.tool != call.mcp_provenance.tool
                ):
                    raise MCPMemoryPersistenceError()
                pending.append(snapshot)
                calls_list.append(replace(call, mcp_provenance=snapshot.call))
        # Even skipped facts acquire their real correlation at the verified append.
        calls = tuple(
            replace(
                c,
                mcp_provenance=MCPToolCallProvenance.model_validate(
                    {
                        **c.mcp_provenance.model_dump(),
                        "transcript_correlation_id": turn.turn_id,
                    }
                ),
            )
            if c.mcp_provenance is not None
            else c
            for c in calls_list
        )
        recorded_turn = replace(turn, tool_calls=calls)
        try:
            receipt: MCPTranscriptReceipt | None = await transcript.record_mcp_interaction(
                recorded_turn
            )
        except asyncio.CancelledError:
            raise
        except Exception:
            # An append can commit before its caller observes a failure.
            # Only complete immutable public readback can settle ambiguity.
            receipt = await _read_receipt(transcript, turn)
            if receipt is None:
                raise MCPMemoryPersistenceError() from None
        expected = tuple(
            c.mcp_provenance for c in calls if c.mcp_provenance is not None
        )
        if receipt is None or receipt.entry_id != turn.turn_id or receipt.calls != expected:
            raise MCPMemoryPersistenceError()
        published_ids: set[str] = set()
        for snapshot in pending:
            with suppress(Exception):
                # A durable ingested receipt stays truthful even if publication
                # fails. It remains pending, rather than deleting the receipt's record.
                if await memory.publish_mcp_memory(snapshot):
                    published_ids.add(snapshot.call.call_id or "")
        for call in calls:
            facts = call.mcp_provenance
            if facts is None:
                continue
            if facts.memory_ingested:
                _observe(
                    observe, call,
                    "published" if facts.call_id in published_ids else "pending"
                )
            else:
                _observe(observe, call, "skipped")
        return calls
    except asyncio.CancelledError:
        raise
