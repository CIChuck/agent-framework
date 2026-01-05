# friday-mcp

MCP (Model Context Protocol) integration for the Friday Framework.

## Features

- **MCP Client**: Connect to external MCP servers and consume their tools
- **MCP Server**: Expose Friday capabilities (agent or tools) via MCP
- **Transport Support**: Both stdio (subprocess) and SSE (HTTP streaming)
- **Tool Adaptation**: Seamlessly adapt MCP tools to Friday's ToolDefinition protocol

## Installation

```bash
# Core package
pip install friday-mcp

# With SSE server support
pip install friday-mcp[server]

# Full integration with Friday
pip install friday-mcp[full]
```

## Quick Start

### Connecting to MCP Servers (Client)

```python
from friday_mcp import MCPClientManager, MCPConfig, MCPServerConfig

config = MCPConfig(
    servers=[
        MCPServerConfig(
            name="filesystem",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
        )
    ]
)

async with MCPClientManager(config) as manager:
    tools = await manager.get_all_tools()
    # Use tools with Friday's agent
```

### Exposing Friday as MCP Server

```python
from friday_mcp import StdioMCPServer, MCPServerSettings
from friday_mcp.server.agent_mode import configure_agent_mode

server = StdioMCPServer()
configure_agent_mode(server, agent, profile, MCPServerSettings())
await server.start()
```

## License

MIT
