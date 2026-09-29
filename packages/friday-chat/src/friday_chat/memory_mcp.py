"""Owned MCP memory staging and append-only transcript publication coordination."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from dataclasses import replace

from friday_core.mcp import MCPIngestionPolicy, MCPToolCallProvenance
from friday_memory.models.mcp import MCPMemorySnapshot

from friday_chat.runtime import (
    MCPMemoryCapability,
    MCPTranscriptCapability,
    TranscriptStore,
)
from friday_chat.tools.schemas import ToolCallRecord
from friday_chat.turns.models import InteractionTurn


class MCPMemoryPersistenceError(RuntimeError):
    def __init__(self) -> None:
        super().__init__("MCP memory transcript receipt could not be verified.")


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


async def persist_mcp_interaction(
    memory: object,
    transcript: TranscriptStore,
    policy: MCPIngestionPolicy,
    turn: InteractionTurn,
) -> tuple[ToolCallRecord, ...]:
    if not policy.long_term_memory_enabled or not any(
        c.mcp_provenance for c in turn.tool_calls
    ):
        await transcript.record_interaction(turn)
        return turn.tool_calls
    if not isinstance(memory, MCPMemoryCapability) or not isinstance(
        transcript, MCPTranscriptCapability
    ):
        calls = tuple(_skipped(c) for c in turn.tool_calls)
        await transcript.record_interaction(replace(turn, tool_calls=calls))
        return calls
    pending: list[MCPMemorySnapshot] = []
    calls_list: list[ToolCallRecord] = []
    append_started = False
    try:
        for call in turn.tool_calls:
            if call.mcp_provenance is None:
                calls_list.append(call)
                continue
            prepared = await memory.prepare_mcp_memory(call, turn.turn_id, policy)
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
        append_started = True
        receipt = await transcript.record_mcp_interaction(
            replace(turn, tool_calls=calls)
        )
        expected = tuple(
            c.mcp_provenance for c in calls if c.mcp_provenance is not None
        )
        if receipt.entry_id != turn.turn_id or receipt.calls != expected:
            raise MCPMemoryPersistenceError()
        for snapshot in pending:
            with suppress(Exception):
                # A durable ingested receipt stays truthful even if publication
                # fails. It remains pending, rather than deleting the receipt's record.
                await memory.publish_mcp_memory(snapshot)
        return calls
    except (Exception, asyncio.CancelledError):
        if not append_started:
            for snapshot in pending:
                with suppress(Exception):
                    await memory.discard_mcp_memory(snapshot)
        # Once append starts it can have committed despite a later error. Never
        # remove its record without proof; excluded pending storage is fail-closed.
        raise
