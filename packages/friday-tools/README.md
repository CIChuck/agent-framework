# Friday Tools

Tool definitions, registries, schema adapters, and a catalog of native and integration tools. Use it to expose typed Python functions to agents or to select built-in tools for your application.

**Distribution:** [friday-framework-tools](https://pypi.org/project/friday-framework-tools/) · **Import:** `friday_tools`
**Python:** 3.13.4+ · **Status:** alpha · **License:** MIT

## Installation

```bash
python -m pip install "friday-framework-tools==0.1.0a4"
```

Friday distributions use the same release version; keep internal Friday dependencies aligned.

## Quick start: define and invoke a tool

```python
import asyncio

from friday_tools import DefaultToolRegistry, FunctionTool

def greet(name: str) -> str:
    """Return a greeting."""
    return f"Hello, {name}!"

async def main() -> None:
    tool = FunctionTool(greet)
    registry = DefaultToolRegistry()
    registry.register(tool)
    print(registry.list_names())
    print(await tool.execute(name="Friday"))

asyncio.run(main())
```

Expected output includes `greet` and `Hello, Friday!`. This invokes a local function directly; it does not call a model or register every built-in tool.

## Catalog and integrations

Native categories include filesystem, shell, web, git, text, data, code and memory. `get_default_registry()` supplies the shared default registry; use a new `DefaultToolRegistry` when your application needs its own membership.

| Extra | Purpose |
| --- | --- |
| `sandbox` | Sandbox-backed execution integration |
| `finance`, `moltbook` | Corresponding provider integrations |
| `documents`, `spreadsheets`, `all-formats` | Optional file-format dependencies |
| `llm`, `langchain`, `anthropic`, `openai`, `all-adapters` | Schema/provider adapter dependencies |

For example: `python -m pip install "friday-framework-tools[documents]==0.1.0a4"`. Extras install dependencies; applications still configure and admit tools explicitly. `FunctionTool` and the typed `FridayTool`/`ToolResult` surface have different result contracts; choose the one your caller expects.

## Execution boundary

A registry and a generated JSON schema do not grant safe execution. Configure filesystem roots, shell restrictions, sandbox choice, tool selection and result sanitization in the owning application. External tools may access networks, incur charges, or mutate files. Read-only tools are the appropriate starting point for a new integration.

## Development

Work from the monorepo root after the [shared contributor setup](https://github.com/CIChuck/agent-framework/blob/master/README.md#development).
Run the focused suite:

```bash
uv run --no-sync pytest packages/friday-tools/tests_tools -q
```

## Documentation and support

[Tools guide](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/05-tools.md) · [Security configuration](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/security-configuration-guidelines.md) · [Sandbox backends](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-sandbox/README.md) · [Source](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-tools/src/friday_tools) · [Issues](https://github.com/CIChuck/agent-framework/issues) · [Contributing](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/15-contributing.md)

## License

[MIT](https://github.com/CIChuck/agent-framework/blob/master/LICENSE).
