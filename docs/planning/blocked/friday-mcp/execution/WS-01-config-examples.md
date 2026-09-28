# MCP-WS-01 Configuration Examples

These are parsing examples for the canonical runtime YAML location
`tools.providers.mcp`. WS-01 does **not** connect servers or register tools.
Until WS-02 is implemented and verified, a runtime with `enabled: true` still
rejects MCP provider loading. `RuntimeConfig.from_sources()` uses the existing
defaults → YAML → permitted environment overrides → explicit construction
overrides precedence; WS-01 adds no MCP-specific environment variable or
Friday Chat alias.

Disabled MCP (safe default, with omitted `mode` defaulting to `selected`):

```yaml
tools:
  providers:
    mcp:
      enabled: false
      config:
        servers: []
```

One local stdio server with optional failure semantics:

```yaml
tools:
  providers:
    mcp:
      enabled: true
      mode: selected
      include_tools: [mcp_filesystem_read_file]
      config:
        auto_connect: true
        servers:
          - name: filesystem
            enabled: true
            required: false
            transport: stdio
            command: npx
            args: [-y, "@modelcontextprotocol/server-filesystem"]
            cwd: tools
            trust_level: local
```

`cwd` is resolved under `runtime_paths.workspace_root`; absolute paths must
also remain under that root, and traversal or symlink escapes are rejected.
Setting `required: true` on the enabled server chooses required-server
semantics for WS-02; connection-failure handling is not implemented in WS-01.
`include_tools` and `exclude_tools` contain canonical Friday tool names;
overlap fails validation. For an exclude-only selection, set `mode: all` and
`exclude_tools: [mcp_filesystem_delete_file]`.

External config includes remain invalid, including when MCP is disabled:

```yaml
tools:
  providers:
    mcp:
      enabled: false
      config_file: ./mcp.yaml  # rejected; reserved for MCP-WS-09
```

The existing `friday_mcp.config.MCPConfig` remains a separate protocol-local
API. Programmatic SSE use is unchanged, but the integrated runtime config
accepts stdio only. Safe values from an `MCPConfig` object can normalize into
the runtime model; server-exposure settings and SSE do not normalize.
