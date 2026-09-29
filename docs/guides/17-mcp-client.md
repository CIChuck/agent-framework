# MCP client setup and operation

This guide covers the integrated MCP **client** in the Friday runtime and
Friday Chat. It connects to local stdio servers, discovers their tools at
startup, and registers only tools admitted by Friday's filters and limits.
MCP is off by default. For a repository-checkout test, the local peer below
needs no network or credentials.

## Configure a local server

Put the stanza under `tools.providers.mcp` in the runtime or Friday Chat YAML.
Friday Chat's editable runtime config can be copied from its packaged
`config.example.yaml`; the installed template is a starting point, not the
runtime state directory. In Friday Chat, use `--runtime real` to start the real
tool provider; the CLI's default fake runtime does not connect to MCP peers.

```yaml
tools:
  providers:
    mcp:
      enabled: true
      mode: selected
      include_tools: [mcp_demo_probe]
      config:
        servers:
          - name: demo
            transport: stdio
            command: python
            args: [-u, tests/integration/mcp_fake_server.py, good]
            cwd: .
            required: false
            retry_attempts: 0
```

This example runs from the repository root with the local test peer included
in the checkout. `python` must be on `PATH`; for an installed Friday, replace
the `command`/`args` with your own installed, trusted local MCP server. Run
Friday Chat with `friday-chat --config /path/to/config.yaml --runtime real` and
the model/embedding configuration required by that application. The server's
discovered `probe` tool is named `mcp_demo_probe`: Friday normalizes the server
and original tool names with the default `mcp_` prefix. The default provider
mode is `selected`, so a newly discovered tool is not registered until its
canonical name appears in `include_tools` (or another explicit selection rule
admits it). `exclude_tools` always removes listed canonical names. Filters
must use these Friday names, not raw peer names. If a selected include is
missing, startup reports `missing_include` rather than silently continuing.

To leave MCP off, omit the stanza or use this safe template value:

```yaml
tools:
  providers:
    mcp:
      enabled: false
      mode: selected
      config:
        servers: []
```

Set `required: true` on an enabled server only when Friday must fail startup
if that server cannot connect or list tools. The default `required: false`
records a diagnostic when an optional server fails. The first example also
pins `include_tools: [mcp_demo_probe]`: that is a separate **required tool**
selection. If the optional peer is down, registration fails with
`missing_include` and startup stops despite `required: false`.

If startup must continue when this peer is absent, do not pin one of its tool
names. For a trusted, small MCP catalog, category selection admits available
MCP tools without requiring any one name:

```yaml
tools:
  providers:
    mcp:
      enabled: true
      mode: selected
      include_categories: [mcp]
      config:
        servers:
          - name: demo
            command: python
            args: [-u, tests/integration/mcp_fake_server.py, good]
            cwd: .
            required: false
            retry_attempts: 0
```

With this category-based example, a failed optional peer leaves other
providers available; when it connects, **all** valid discovered MCP tools
may be registered, so use it only when that broader admission is intended.
A required server cannot also be disabled. Discovery is
startup-only; changing a peer's catalog requires a new runtime start. There
is no live refresh or Chat MCP health command in this pass.

### Secrets and paths

Use an explicit local command, keep `cwd` inside the configured workspace,
and grant the peer only the environment values it needs. Friday Chat expands
`${EXAMPLE_API_KEY}` from the process environment before validation; export it
outside the YAML and do not commit real values:

```yaml
tools:
  providers:
    mcp:
      enabled: true
      mode: selected
      include_tools: [mcp_demo_probe]
      config:
        servers:
          - name: demo
            command: python
            args: [-u, tests/integration/mcp_fake_server.py, good]
            env:
              EXAMPLE_API_KEY: ${EXAMPLE_API_KEY}
```

For a headless RuntimeConfig caller, provide the server `env` mapping from
your application's secret source. The integrated configuration accepts local
stdio only. Programmatic `friday-mcp` transport/server APIs are separate and
do not make remote SSE an integrated runtime option. The reserved
`tools.providers.mcp.config_file` key is **rejected**; external includes belong
to deferred WS-09. MCP resources, prompts and server exposure are not part of
this integrated client.

## Discovery, turn budgets and results

`tools.providers.mcp.config.limits` bounds server count, per-server and total
tool count, schema size, concurrent work and result size. Cap and schema
failures can skip a discovered tool before registration. Friday Chat then
selects a smaller set per model turn. Its `tools.context.max_tools`, optional
`max_mcp_tools`, `max_budget_ratio` and required tool list govern that second
selection. Selected schema tokens and a reserved MCP result budget reduce the
context available for memory retrieval. The configured minimum memory
retrieval floor is preserved; an over-budget optional tool may be skipped and
a required/manual selection may fail with a categorical reason. Broad peer
catalogs add prompt overhead, so select only the tools needed for a task.

MCP calls use the ordinary tool loop. Friday checks and bounds peer results
before they reach Chat/transcript paths; oversized text may be truncated or
blocked. Raw tool arguments, raw results, environment values, peer exception
text and argument hashes are not exported as MCP telemetry or retained in MCP
provenance. Checked transcript metadata may record an MCP call. Direct
long-term MCP memory ingestion is **disabled by default**. Opt-in requires
`config.ingestion.long_term_memory_enabled: true`, at least one
`opted_in_servers` or canonical `opted_in_tools` entry, and sanitized content.
Captured memories carry source, trust, freshness and truncation labels; an
accepted transcript receipt can exist while a memory publication remains
pending. A failed/uncertain publication is not a claim of available memory.

## Inspect and troubleshoot

The public local `RuntimeKernel.mcp_provider` (or Friday Chat's
`MCPChatRegistry.provider`) exposes `operational_diagnostics` when enabled.
It contains typed discovery, optional/required server lifecycle, registration
and collision decisions, budget skip counts, truncation counts and ingestion
outcome counts. Optional telemetry emits closed categorical events with opaque
server/tool references; it does not expose peer schemas, descriptions,
arguments, results or exception strings. Do not copy raw peer output or local
config secrets into a support report.

If no MCP tool appears, check `enabled`, the stdio command and workspace `cwd`,
then the local diagnostics. Confirm the peer lists a tool at startup, its
canonical name matches `include_tools`, it is absent from `exclude_tools`,
and no name collision or discovery/schema cap rejected it. For Chat-only
absence, inspect the per-turn selection reason and schema/memory budget. For
truncated output, review `max_result_bytes` and the peer's output size. If
memory is missing, first check the default-disabled ingestion policy, then
the explicit opt-ins and pending/published diagnostic outcome. See
[Troubleshooting](13-troubleshooting.md) for the failure table.
