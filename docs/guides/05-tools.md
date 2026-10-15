---
title: Tools and execution
description: Create, register, select and operate tools with explicit execution and safety boundaries.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: guide
---

# Tools and execution

Tools expose operations to an agent or Chat loop through names, descriptions,
schemas and callables. Registration, selection, permission and execution are
separate decisions. A tool description or model request cannot grant authority
to access a file, run a shell command or mutate an external service.

## Two implementation surfaces

| Surface | Input/return contract | Best fit |
| --- | --- | --- |
| `BaseTool` / Core `ToolDefinition` | `parameters_schema`; async `execute(**kwargs) -> str` | Direct protocol implementations and adapters |
| `FunctionTool` | Wraps a sync/async function; generates a basic schema; returns text | Small, explicitly registered operations |
| `FridayTool` | Pydantic `Input`, async `run(args) -> ToolResult`; `execute` validates/serializes | Rich validated native tools |

`ToolResult` carries content plus optional structured data, metadata and error.
That object is the `FridayTool.run()` result; callers of `execute()` receive a
string. Not every tool returns a `ToolResult` object to the agent.

## Register an isolated function tool

This **offline Python example** uses a new registry and synthetic inputs:

```python
import asyncio
from friday_tools import DefaultToolRegistry, FunctionTool

def greet(name: str) -> str:
    """Return a greeting for the supplied name."""
    return f"Hello, {name}"

async def main() -> None:
    registry = DefaultToolRegistry()
    registry.register(FunctionTool(greet, category="utility"))
    print(registry.list_names())
    result = await registry.get_callable("greet")(name="Ada")
    print(result)

asyncio.run(main())
```

Expected output includes `['greet']` and `Hello, Ada`. A new registry starts
empty. `get_default_registry()` returns the shared registry; it is not a promise
that every installed tool has been imported and registered.

`FunctionTool` derives a limited schema from simple Python annotations. It does
not provide a universal runtime type-validation layer for arbitrary Python
functions or complex generic annotations. Validate important invariants in your
callable, or use an explicit Pydantic input model through `FridayTool`.

## A typed tool

This **offline Python example** uses the richer native contract:

```python
import asyncio
from pydantic import BaseModel, Field
from friday_tools import FridayTool, ToolResult

class DoubleTool(FridayTool):
    name = "double_number"
    description = "Double a bounded nonnegative integer."
    category = "utility"
    tags = ["demo"]

    class Input(BaseModel):
        number: int = Field(ge=0, le=100)

    async def run(self, args: Input) -> ToolResult:
        value = args.number * 2
        return ToolResult(content=str(value), data={"value": value})

async def main() -> None:
    tool = DoubleTool()
    result = await tool.run(tool.Input(number=4))
    print(result.data["value"])
    print(await tool.execute(number=4))

asyncio.run(main())
```

Expected output includes `8`. `execute()` can serialize validation/execution
failures as error text. Callers must inspect the relevant error contract rather
than assuming every returned string is success. Native diagnostic logging can
include argument values and exception text; it is not covered by the closed
MCP/LLM telemetry event guarantees.

## Discovery and schema inspection

`DefaultToolRegistry` supports `register`, `unregister`, `get`, `list_tools`,
`list_names`, `get_callable`, `get_schema`, `get_schemas`, category and tag lookup.
Duplicate names raise an error. Explicitly construct a registry for tests or
applications that must avoid shared import-time membership.

The [source catalog](14-appendices.md#native-tool-source-catalog) lists tool
definitions and marks obvious stubs. It is a source inventory, not the set
registered in your running Chat session. `/tools` shows runtime membership;
`/tool-budget` explains the selected schema set.

Common implementation groups include filesystem, shell, web, Git, data, text,
encoding, archive, math, execution, finance, memory and integrations. Dependency
extras may be required. Database, email, calendar and other declared integration
tools include placeholders; inspect the specific implementation before use.

## Configure Chat tool admission

This **Chat configuration fragment** explicitly selects a harmless utility tool:

```yaml
tools:
  enabled: true
  registry:
    - name: echo
      module: friday_tools.utility
      class: EchoTool
  context:
    max_tools: 5
    max_budget_ratio: 0.20
    include_in_context: true
```

Keep the ordinary model/embedding configuration alongside it. A registry entry
names importable application code; only admit trusted modules/classes. Tool
constructors can have side effects. Installation and registration do not imply
the model can always see or execute a tool.

Agent profiles have separate `tools`, `tool_autonomy`, `injected_tools`,
`available_tools` and `required_tools` fields. These configure selection modes,
not a general filesystem/network authorization system. See [agents](06-agents.md).

## Selection and context budgets

Chat selects a model-facing schema set each turn. `tools.context.max_tools` and
`max_budget_ratio` bound the set; optional `max_mcp_tools` bounds the MCP share.
Required names must resolve and fit policy. MCP has additional discovery/result
limits and a minimum memory retrieval floor.

`/inject-tools name ...` sets the exact manual schema set for later turns;
`/clear-tools` restores automatic selection. Unknown names or over-budget
required/manual choices can fail selection. `/recommend-tools <query>` gives
recommendations, not a permission grant. `/run-tool` directly executes an
admitted tool and can mutate state.

The loop also has iteration/failure/result limits. Treat reaching a limit as a
partial operation; increasing it does not repair a failing integration. Never
replay a mutating operation merely because the assistant failed to describe it.

## Filesystem and shell policy

`FilesystemSandbox` validates paths and supports explicit allowed/blocked paths
and patterns. Its convenience defaults can include home and temporary paths;
use `allow_home=False` and `allow_temp=False` when constructing a narrowly
scoped application policy. Path checks are not an OS sandbox or a guarantee
against every filesystem race.

`ShellSandbox` and `CommandExecuteTool` are different policies. The latter uses
command blocklists and permits richer shell expressions. Neither is a complete
containment boundary for arbitrary code. Subprocess execution runs with host
privileges; Docker is a separate backend needing daemon/image/network/mount
configuration. The mock backend executes nothing.

For untrusted code, design and verify the deployment boundary explicitly;
avoid granting a shell tool solely to work around a missing typed operation.
See [security](security-configuration-guidelines.md) and [advanced deployment](11-advanced-topics.md#execution-backends).

## External tools and outputs

MCP client tools are configured under `tools.providers.mcp`, disabled by default.
They support local stdio and explicitly admitted HTTPS Streamable HTTP peers.
Canonical names such as `mcp_demo_echo` differ from raw peer names. Explicit
filters, transport trust, version, auth, schemas, budgets and ownership all apply.
The [MCP client guide](17-mcp-client.md) is the complete configuration reference.

Treat outputs as untrusted data before model use or persistence. The integrated
MCP path has checked bounded results/provenance and explicit long-term-memory
opt-in. Generic native tools and manual commands have different handling; a
security YAML section alone does not prove all output paths are sanitized.

## Implementation references

- [Core tool contracts](../../packages/friday-core/src/friday_core/interfaces/tools.py)
- [Function tools](../../packages/friday-tools/src/friday_tools/definition.py), [typed tools](../../packages/friday-tools/src/friday_tools/base.py) and [registry](../../packages/friday-tools/src/friday_tools/registry.py)
- [Chat registry](../../packages/friday-chat/src/friday_chat/tools/registry.py), [selection](../../packages/friday-chat/src/friday_chat/tools/selection.py) and [loop](../../packages/friday-chat/src/friday_chat/tools/loop.py)
- [Sandbox package](../../packages/friday-sandbox/README.md)

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)
