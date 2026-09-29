# Friday Framework MCP

`friday-mcp` provides protocol-level MCP clients, transports and server APIs.
Its programmatic clients support stdio and SSE; the integrated Friday runtime
client currently configures **local stdio only**. The runtime owns discovery,
registration, filters, diagnostics and lifecycle. See the
[MCP client guide](../../docs/guides/17-mcp-client.md) for the canonical
`tools.providers.mcp` configuration and Friday Chat use.

## Installation

```bash
pip install friday-framework-mcp
```

The optional `server` extra provides standalone server dependencies. The
`full` extra includes the package's broader protocol integrations; neither
extra enables remote servers in the integrated runtime config.

## Programmatic client

This low-level example uses the repository's local synthetic peer. It runs
from a checkout and does not contact a network:

```python
import asyncio

from friday_mcp import MCPClientManager, MCPConfig, MCPServerConfig

async def main() -> None:
    config = MCPConfig(
        servers=[
            MCPServerConfig(
                name="demo",
                command="python",
                args=["-u", "tests/integration/mcp_fake_server.py", "good"],
            )
        ]
    )

    async with MCPClientManager(config) as manager:
        tools = await manager.get_all_tools()
        print([tool.name for tool in tools])

asyncio.run(main())
```

Run it from the repository root. For an installed application, substitute an
owned local server executable. The integrated
runtime path uses `friday_runtime.config.MCPToolProviderConfig` and imposes
stricter local transport, workspace, filtering, schema and result policies.

The package also exposes programmatic MCP server classes. They are separate
from `tools.providers.mcp`, which configures Friday as a client and does not
expose Friday as a server. Resources, prompts and external config includes
are not implemented by that integrated client.

## License

MIT
