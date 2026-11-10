"""Entity-name syntax belongs to the shared command handler."""

import asyncio

import pytest
from friday_commands import CommandExecution, CommandRequest, GraphData
from friday_commands.memory_queries import (
    MEMORY_QUERY_SPECS,
    build_memory_query_handlers,
)


class GraphPort:
    def __init__(self, failure=None):
        self.calls = []
        self.failure = failure

    def memory_available(self):
        return True

    async def graph_snapshot(self, name, include_relationships):
        self.calls.append((name, include_relationships))
        if self.failure is not None:
            raise self.failure
        return GraphData()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("args", "selection"),
    [
        ((), (None, True)),
        (("nodes",), (None, False)),
        (("nodes", "ignored"), (None, False)),
        (("NODES",), ("NODES", True)),
        (('"nodes"',), ("nodes", True)),
        (("'nodes'",), ("nodes", True)),
        (("Chuck",), ("Chuck", True)),
        (('"Chuck"',), ("Chuck", True)),
        (("'Chuck'",), ("Chuck", True)),
        (('"Peano', "Arithmetic", '(PA)"'), ("Peano Arithmetic (PA)", True)),
        (("'Peano", "Arithmetic", "(PA)'"), ("Peano Arithmetic (PA)", True)),
        (('"O\'Brien"',), ("O'Brien", True)),
        (('"Kurt', 'Gödel"'), ("Kurt Gödel", True)),
        (('"C:\\notes"',), ("C:\\notes", True)),
        (('""Chuck""',), ('"Chuck"', True)),
        (('"Chuck',), ('"Chuck', True)),
        (("\"Chuck'",), ("\"Chuck'", True)),
        (('""',), ('""', True)),
        (("''",), ("''", True)),
        (('"', '"'), ('" "', True)),
    ],
)
async def test_shared_entity_selection_preserves_mode_and_normalizes_one_pair(
    args, selection
):
    port = GraphPort()
    spec = next(spec for spec in MEMORY_QUERY_SPECS if spec.name == "entities")
    request = CommandRequest("entities", args, spec)
    outcome = await build_memory_query_handlers(port)["entities"](
        request, CommandExecution()
    )
    assert outcome.data == GraphData()
    assert port.calls == [selection]
    assert request.args == args


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", [RuntimeError("fixture"), asyncio.CancelledError()])
async def test_quoted_selection_preserves_failure_identity(failure):
    port = GraphPort(failure)
    spec = next(spec for spec in MEMORY_QUERY_SPECS if spec.name == "entities")
    with pytest.raises(type(failure)) as caught:
        await build_memory_query_handlers(port)["entities"](
            CommandRequest("entities", ('"Chuck"',), spec), CommandExecution()
        )
    assert caught.value is failure
    assert port.calls == [("Chuck", True)]
