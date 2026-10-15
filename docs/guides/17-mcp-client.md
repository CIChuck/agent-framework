---
title: MCP client setup and operation
description: Configure dated local/HTTPS tools clients, admission, results, refresh and lifecycle without implicit optional roles.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: guide
---

# MCP client setup and operation

This guide covers the integrated MCP **client** in the Friday runtime and
Friday Chat. It connects to local stdio and explicitly admitted HTTPS Streamable
HTTP servers, discovers their tools at
startup, and registers only tools admitted by Friday's filters and limits.
MCP is off by default. The owned local server example below needs no network or credentials.

## Install and choose a profile

Install `friday-framework-mcp==0.1.0a3` for programmatic use, or use the aligned
Chat/Runtime environment that owns the integration. Python 3.13.4+ is required.
The official MCP SDK is a development interoperability counterpart; Friday owns
the production protocol implementation. Modern examples here select the dated
2026-07-28 tools profile explicitly. See [the migration matrix](19-mcp-migration.md)
for legacy/default and 2025 HTTP behavior.

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
      include_tools: [mcp_demo_echo]
      config:
        servers:
          - name: demo
            transport: stdio
            command: python
            protocol_profile: modern
            args: [-u, mcp_echo_server.py]
            cwd: .
            required: false
            retry_attempts: 0
```

Save the complete stdio server from [the server guide](18-mcp-server.md#register-an-async-tool-and-serve-stdio)
as `mcp_echo_server.py` in your workspace and launch Chat from that directory.
`python` must resolve to the environment containing Friday MCP; use an absolute
interpreter path when launch environments differ. Replace command/args only
with your own trusted local server. Run
Friday Chat with `friday-chat --config /path/to/config.yaml --runtime real` and
the model/embedding configuration required by that application. The server's
discovered `echo` tool is named `mcp_demo_echo`: Friday normalizes the server
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
pins `include_tools: [mcp_demo_echo]`: that is a separate **required tool**
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
            protocol_profile: modern
            args: [-u, mcp_echo_server.py]
            cwd: .
            required: false
            retry_attempts: 0
```

With this category-based example, a failed optional peer leaves other
providers available; when it connects, **all** valid discovered MCP tools
may be registered, so use it only when that broader admission is intended.
A required server cannot also be disabled. Integrated discovery happens at
startup/reconnect; use public stop/start to rediscover a changed catalog.
Programmatic manual refresh is described below. No Chat MCP health command is added.

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
      include_tools: [mcp_demo_echo]
      config:
        servers:
          - name: demo
            command: python
            protocol_profile: modern
            args: [-u, mcp_echo_server.py]
            env:
              EXAMPLE_API_KEY: ${EXAMPLE_API_KEY}
```

For a headless RuntimeConfig caller, provide the server `env` mapping from
your application's secret source. Local stdio defaults to legacy 2024 behavior;
`protocol_profile: modern` selects 2026-07-28, while `auto` uses bounded read-only
discovery/fallback. Programmatic `friday-mcp` transport/server APIs are separate and
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


## Explicit HTTPS Streamable HTTP peers

Use the same inline config.yaml location for headless Runtime and real Friday Chat.
Every HTTP peer requires an explicit dated version and per-peer remote admission;
enabled HTTP also requires the matching global security pair. Example:

```yaml
tools:
  providers:
    mcp:
      enabled: true
      mode: all
      config:
        security:
          integrated_transport: stdio_and_streamable_http
          trust_posture: explicit_remote
        servers:
          - name: remote_tools
            transport: streamable_http
            protocol_version: '2026-07-28'
            trust_level: remote
            url: https://mcp.example.com/mcp
            auth: bearer_env
            credential_env: FRIDAY_REMOTE_MCP_TOKEN
            network:
              allowed_addresses: []
              allowed_ports: [443]
            timeout_seconds: 30
            tool_timeout_seconds: 30
            retry_attempts: 0
```

Provide the token through the named process environment variable. credential_env
is a literal reference, never `${...}` or an inline value. It remains unresolved
through loading/model_dump; only an enabled connection looks it up. `auth: none`
omits credential_env. Explicit compatibility uses protocol_version:'2025-11-25'.
No default/auto HTTP version, legacy SSE fallback, OAuth discovery/login/refresh,
GET subscriptions, resources/prompts or server exposure is configured here.
The target is the pinned MCP 2026-07-28 tools/transport specification plus the
explicit 2025-11-25 compatibility profile, not every optional MCP feature.

Endpoints are ASCII HTTPS without userinfo, query, fragment or escaped host.
TLS verifies the original hostname; no YAML flag changes trust or verification.
Default port 443 and public addresses apply. Private destinations/non 443 ports
need exact per-peer allowed_addresses/allowed_ports; hostnames/CIDR/wildcards and
mapped IPv6 opt-ins are rejected. All DNS candidates are checked for each new
connection before a validated numeric address is passed to the connector; mixed
allowed/forbidden answers fail closed. No proxies, redirects or ambient cookies.

The strict union rejects process fields on HTTP, remote fields on stdio and
unknown fields even for disabled entries. Required+disabled is invalid. Provider
or peer disable and auto_connect:false perform no factory invocation or credential
lookup. Missing/invalid tokens and peer failures have fixed safe diagnostics.
HTTP startup retries must be zero; no failed/ambiguous tools/call is replayed.
2025 session recovery only initializes a fresh session; a subsequent call requires
an explicit new invocation. Modern HTTP cancellation closes the owned request
stream; modern stdio/2025 use their dated accepted cancellation behavior.

For modern/auto stdio and HTTP, handshake plus full discovery share
min(server timeout, global connection timeout, 30 seconds). Calls use
min(server tool timeout, global tool timeout, 30 seconds), at most four concurrent
requests and at most 64 KiB protocol results. Legacy stdio retains its existing
budgets/retries. Runtime admission and Chat per-turn count/schema/result budgets
still apply. Remote metadata accurately reports streamable_http/remote; peer
instructions and annotations never grant policy or enter prompts automatically.

The model-facing inline schema admits the canonical root 2020-12 declaration and
validated modern HTTP x-mcp-header annotations, then removes those protocol fields.
The client retains its original catalog/wire bindings, including exact Unicode
Base64 header encoding. Unsupported references/dialects/keywords remain rejected.
Checked results use the same sanitation, quarantine, transcript correlation and
explicit memory opt-in as stdio. Borrowed telemetry stays open; no trace/baggage
or credential/application content is forwarded as telemetry. Public stop is
idempotent, with failed cleanup owners retained for retry before replacement.


### Explicit manual catalog refresh

The client package exposes the optional typed `MCPRefreshClient` contract and
immutable `MCPCatalogSnapshot`. `refresh_tool_catalog()` returns the exact complete
generation produced by that operation; `current_catalog_snapshot` is `None`
while refresh is in progress or after failure. Exported tool dictionaries are
independent copies. A generation identifies wire definitions, output schemas
and HTTP argument-header bindings; it does not grant tool admission.

This **API fragment** receives an adapter over an already connected,
explicitly configured client. Calling it performs discovery/refresh; it is not
an independent connection example:

```python
from friday_mcp.client import MCPToolAdapter

async def refresh_tools(adapter: MCPToolAdapter) -> None:
    tools = await adapter.get_tools()
    fresh_tools = await adapter.get_tools(refresh=True)
    print(len(tools), len(fresh_tools))
```

A failed refresh clears usable cached definitions. Previously created wrappers
fail with `catalog_unavailable` before issuing a call after failure, removal or
reconnect. An already-issued call settles once against its captured output schema
and HTTP header bindings. Refresh never replays a tool call. An explicit successful
refresh creates new wrappers; code should replace its own programmatic references
after applying its existing admission rules. Custom clients implementing only the
original MCPClient contract remain supported, without generation guarantees.

Runtime and Chat retain startup/reconnect discovery and transactional registration.
They expose no in-place refresh YAML option or automatic list-change subscription.
Use their public stop/start lifecycle for integrated rediscovery. Existing selection,
filters, collision and schema/token budgets, provenance, quarantine, transcripts,
explicit memory opt-in and injected provider-neutral telemetry remain controlling.

### Dated tool results and optional features

Modern MCP 2026-07-28 preserves ordered text and structured JSON values, including
null, scalars and arrays; omitted structured content remains distinct from null.
Mixed text/structured results use the bounded deterministic JSON envelope. Explicit
2025-11-25 HTTP structured content remains object-only. Both dated profiles validate
complete content/tag/metadata shapes before classifying ordinary tool errors. A
well-formed tool error needs no successful structured output; malformed error
content is an invalid result. The output-schema subset remains bounded JSON Schema
2020-12 with no network reference retrieval or regex evaluation.

Valid image/audio/resource-link/embedded content returns `unsupported_content`;
malformed variants are invalid results. No media decoding, URL retrieval or resource
fetch occurs. Valid modern input requests return `input_required_unsupported`,
with no callback, opaque-state forwarding or interactive continuation.

Friday advertises no Tasks capability. In the explicit 2025 profile, tools declaring
`execution.taskSupport: required` are excluded; attempts to call an observed
excluded tool return `unsupported_task` before I/O. Absent, forbidden and optional
task support remain ordinary tool candidates. This dated field does not enable a
modern extension. No Tasks RPC, polling, persistence, subscriptions, automatic
refresh, cross-call result cache or outgoing trace/baggage is added. This tools-client
profile and SDK fixture interoperability do not claim whole MCP conformance.

The accepted 2025 raw `call_tool` API permits a later explicit call after session
recovery, without replaying the failed call. It retains the prior output schema
for that raw call; generation-bound wrappers stay invalid and current catalog
snapshot stays unavailable until explicit rediscovery. Manual refresh failure or
explicit disconnect clears this compatibility data. Runtime/Chat wrappers use
public stop/start rediscovery after recovery.

Custom MCPClientBase subclasses that override raw `list_tools` or `call_tool`
keep their virtual APIs. `supports_catalog_refresh` defaults to false for these
subclasses; they may explicitly opt in when their optional refresh/generation
methods implement this contract. Other custom clients can implement the declared
MCPRefreshClient protocol directly.

For dated transport choices, exact configuration examples and rollback, see
[MCP migration](19-mcp-migration.md). To expose explicitly owned tools through
Friday, use the separate [modern server APIs](18-mcp-server.md).

## Offline programmatic round trip

After saving `mcp_echo_server.py` from the server guide, save this beside it as
`mcp_echo_client.py`. This **offline Python example** owns a local subprocess;
it needs no LLM, network service, credentials or persistent memory:

```python
import asyncio
from pathlib import Path
import sys
from friday_mcp.client.stdio import StdioMCPClient

async def main() -> None:
    async with StdioMCPClient(
        name="demo", command=sys.executable,
        args=["-u", str(Path(__file__).with_name("mcp_echo_server.py"))],
        protocol_profile="modern",
    ) as client:
        await client.list_tools()
        print(await client.call_tool("echo", {"text": "Hello from MCP"}))

asyncio.run(main())
```

Run `python mcp_echo_client.py`; expected output is `Hello from MCP`. Programmatic
calls use the peer's raw name `echo`; integrated registry selection uses
`mcp_demo_echo`. Await client context exit so the owned process is stopped.
This validates a tools-profile exchange, not whole-protocol conformance.

## Implementation references

- [Runtime MCP configuration](../../packages/friday-runtime/src/friday_runtime/config.py)
- [Client package](../../packages/friday-mcp/src/friday_mcp/client)
- [Chat MCP registry](../../packages/friday-chat/src/friday_chat/tools/mcp.py)
- [Checked results](../../packages/friday-chat/src/friday_chat/tools/output.py)
- [Long-term ingestion](../../packages/friday-chat/src/friday_chat/memory_mcp.py)

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)
