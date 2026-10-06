from typing import assert_type
from collections.abc import Coroutine
from typing import Any
from pydantic import BaseModel
from friday_chat.memory_views import MemoryMetric
from friday_cli.commands import CommandRegistry
from friday_cli.session import SessionContext, SessionManager
from friday_cli.cancellation import run_cancellable
from friday_core.interfaces.tools import ToolAdapter
from friday_moltbook.responses import MoltbookResponse
from friday_sandbox.serialization import validate_return_type
from friday_memory.llm_completion import complete_structured_memory_request, MemoryLLMClient

class Parent: pass
class Child(Parent): pass
class Item(BaseModel):
    value: int

def directions(a: MemoryMetric[Parent], b: MemoryMetric[Child], c: CommandRegistry[Parent], d: CommandRegistry[Child], e: SessionContext[Parent], f: SessionContext[Child], g: SessionManager[Parent], h: SessionManager[Child], i: ToolAdapter[Parent], j: ToolAdapter[Child], k: MoltbookResponse[Parent], l: MoltbookResponse[Child]) -> None:
    a = b
    b = a
    c = d
    d = c
    e = f
    f = e
    g = h
    h = g
    i = j
    j = i
    k = l
    l = k

async def generic_consumers(operation: Coroutine[Any, Any, str], client: MemoryLLMClient) -> None:
    assert_type(await run_cancellable(operation, show_hint=False), str | None)
    assert_type(validate_return_type({'value': 1}, Item), Item)
    assert_type(await complete_structured_memory_request(client, messages=[{'role':'user','content':'synthetic'}], response_model=Item), Item | None)
    validate_return_type({}, int)
    await complete_structured_memory_request(client, messages=[], response_model=int)
