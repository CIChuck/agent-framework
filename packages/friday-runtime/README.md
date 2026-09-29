# Friday Framework Runtime

Headless runtime assembly package for the Friday Framework.

This package provides the runtime kernel and dependency-injection surface used
to compose memory, LLM, telemetry, transcript, agent, and tool services.

## Install

```bash
pip install friday-framework-runtime
```

## Import Package

```python
import friday_runtime
```

## MCP client provider

`RuntimeConfig.tools.providers.mcp` is the canonical headless MCP client
configuration. It is disabled by default. Enabling it connects to explicit
local stdio servers at startup and registers only tools admitted by the
provider's selected-mode filters, schema checks and caps. An optional server
connection failure remains in typed diagnostics, but a pinned missing
`include_tools` name still fails registration with `missing_include`; a
required server failure stops startup.
The external `config_file` key is reserved and rejected.

`RuntimeKernel.mcp_provider` retains the runtime owner, including after a
failed start. Its public `operational_diagnostics` snapshot covers discovery,
server lifecycle, registration/collision decisions, budget skips, truncation
and ingestion outcomes. Optional telemetry exports only closed redacted MCP
events. The [MCP client guide](../../docs/guides/17-mcp-client.md) contains a
parser-checked stdio example, the Friday Chat compatibility shape, security
defaults and troubleshooting steps.

## License

MIT
