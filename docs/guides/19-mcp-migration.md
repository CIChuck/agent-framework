---
title: MCP upgrade and migration
description: Dated transport/role matrix, explicit configuration, admission and rollback for the bounded tools profile.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: guide
---

# MCP upgrade and migration

Friday targets the dated [MCP 2026-07-28 specification](https://modelcontextprotocol.io/specification/2026-07-28/),
with explicit [2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/)
HTTP client compatibility. Friday implements a bounded tools profile.
The dated specification, captured schema and role-specific requirements in the
[upgrade contract](../planning/active/friday-mcp-protocol-upgrade/protocol-contract.md)
control this upgrade. This is not a moving “latest” version selector or a claim
that every optional MCP role is implemented.

| Friday role | Transport | Revision / selection | Lifecycle |
|---|---|---|---|
| Integrated Runtime / real Chat client | Local stdio | Default `legacy`: 2024-11-05 | initialize; owned subprocess |
| Integrated Runtime / real Chat client | Local stdio | Explicit `modern`: 2026-07-28 | discovery; no initialize |
| Integrated Runtime / real Chat client | Local stdio | Explicit `auto` | bounded read-only modern probe; legacy fallback under the same deadline |
| Integrated Runtime / real Chat client | HTTPS Streamable HTTP | Explicit 2026-07-28 | single POST; JSON or request-scoped SSE; no session |
| Integrated Runtime / real Chat client | HTTPS Streamable HTTP | Explicit 2025-11-25 | initialize; optional origin-scoped session; no failed-call replay |
| Programmatic modern Friday server | stdio / Streamable HTTP | 2026-07-28 only | explicitly registered async tools |
| Retained programmatic legacy APIs | stdio / HTTP+SSE | 2024-11-05 | original API semantics |

SSE is a response encoding in modern Streamable HTTP. The legacy split HTTP+SSE
transport is a separate programmatic API and is not an integrated YAML transport.
A new modern server is constructed through the APIs in [the server guide](18-mcp-server.md).
Existing server configuration enums (`stdio`, `sse`) do not construct those modern
APIs automatically. Explicit 2025 support belongs to the client; the modern
Friday server does not advertise it.

## Choose a client configuration

Edit your application `config.yaml` under `tools.providers.mcp.config.servers`.
No MCP connection configuration command is added. These are complete MCP stanzas;
keep the application's ordinary model, embedding and storage configuration alongside
them. Real Friday Chat requires `friday-chat --config /path/to/config.yaml --runtime real`.
Its fake runtime does not connect to peers. The headless application loads
`RuntimeConfig.from_sources(yaml_path=..., env=...)` and starts its RuntimeKernel.

MCP remains disabled by default:

```yaml
tools:
  providers:
    mcp:
      enabled: false
      mode: selected
      config:
        servers: []
```

Keep a trusted local server on the legacy default while upgrading other peers:

```yaml
tools:
  providers:
    mcp:
      enabled: true
      mode: selected
      include_categories: [mcp]
      config:
        servers:
          - name: owned
            transport: stdio
            command: /absolute/path/to/trusted-server
            required: false
            retry_attempts: 0
```

Select a known modern stdio peer explicitly:

```yaml
tools:
  providers:
    mcp:
      enabled: true
      mode: selected
      include_tools: [mcp_owned_echo]
      config:
        servers:
          - name: owned
            transport: stdio
            command: /absolute/path/to/trusted-server
            protocol_profile: modern
            required: true
            retry_attempts: 0
```

Use `auto` only when read-only probe/fallback is appropriate for your local peer:

```yaml
tools:
  providers:
    mcp:
      enabled: true
      mode: selected
      include_tools: [mcp_owned_echo]
      config:
        servers:
          - name: owned
            transport: stdio
            command: /absolute/path/to/trusted-server
            protocol_profile: auto
            required: true
            retry_attempts: 0
```

HTTPS requires both the global security pair and an explicit remote peer. This
public hostname is an inert configuration placeholder; it is not a service Friday
provides or a deployment tested by this upgrade:

```yaml
tools:
  providers:
    mcp:
      enabled: true
      mode: selected
      include_categories: [mcp]
      config:
        security:
          integrated_transport: stdio_and_streamable_http
          trust_posture: explicit_remote
        servers:
          - name: owned
            transport: streamable_http
            protocol_version: '2026-07-28'
            trust_level: remote
            url: https://mcp.example.com/mcp
            auth: bearer_env
            credential_env: FRIDAY_REMOTE_MCP_TOKEN
            network:
              allowed_addresses: []
              allowed_ports: [443]
            required: true
            retry_attempts: 0
```

Use this explicit compatibility entry when the remote peer implements 2025:

```yaml
tools:
  providers:
    mcp:
      enabled: true
      mode: selected
      include_categories: [mcp]
      config:
        security:
          integrated_transport: stdio_and_streamable_http
          trust_posture: explicit_remote
        servers:
          - name: owned
            transport: streamable_http
            protocol_version: '2025-11-25'
            trust_level: remote
            url: https://mcp.example.com/mcp
            auth: bearer_env
            credential_env: FRIDAY_REMOTE_MCP_TOKEN
            network:
              allowed_addresses: []
              allowed_ports: [443]
            required: true
            retry_attempts: 0
```

`credential_env` is a literal environment-variable **reference**. It remains
unresolved during loading/model export; an enabled connection looks it up. Never
put a token, `${...}` interpolation, userinfo or query token there. `auth: none`
omits the reference. The stdio `env` mapping has its separate Chat interpolation
behavior described in [client setup](17-mcp-client.md). HTTP rejects process fields;
stdio rejects HTTP fields. Unknown or mixed fields fail even in disabled entries.
Required+disabled is invalid. Disabled providers/peers and `auto_connect: false`
perform no client-factory invocation or credential lookup.

TLS verification has no YAML disable flag. Endpoints must be ASCII HTTPS without
userinfo/query/fragment. Every DNS answer is checked before a numeric connection;
private addresses/non 443 ports require exact per-peer address and port grants.
No proxies, redirects, ambient cookies or wildcard/CIDR grants are enabled. Tests
substitute only private literal loopback, ephemeral port and a verifying synthetic
CA; that testing seam does not change production TLS policy.

## Admission, results and ownership

Canonical tool names use the default `mcp_` prefix and normalized server/tool names.
`include_tools` requires each named tool; a missing include fails startup even for
an optional peer. `include_categories: [mcp]` admits available valid MCP tools
without requiring one named tool. Excludes always remove candidates. Required
peers fail startup on connection/discovery failure; optional failures record safe
diagnostics. Keep catalogs and selection narrow.

Provider limits bound catalogs, schemas, requests and results. Chat also applies
per-turn schema/count/result budgets and preserves its minimum memory retrieval
floor. Ordinary input/output validation, sanitization, provenance, quarantine and
transcript correlation continue. Long-term MCP ingestion stays off unless the
application explicitly enables it and opts in named servers/tools. Structured
Unicode results survive the protocol boundary; valid unsupported media yields a
fixed unsupported-content result with no resource/URL retrieval. Unknown peer
instructions, annotations and capability claims never authorize access.

Programmatic clients support explicit catalog refresh with immutable generations.
Runtime/Chat use public stop/start for rediscovery; there is no live-refresh YAML
switch or subscription. An issued call retains its captured schema/header mapping.
Never replay an uncertain mutating call. HTTP 2025 recovery initializes a fresh
session but requires an explicit subsequent call; modern HTTP has no session or
automatic fallback. Stop is idempotent after success; failed cleanup retains owners
for another stop and blocks unsafe replacement. Async server handlers must cooperate
with cancellation. Server bind/Host/Origin/bearer/TLS policy is a separate application
responsibility and is not granted by client network admission.

Telemetry uses injected, provider-neutral `TelemetryInterface` observers. Borrowed
observers remain open. No MCP trace/baggage propagation, raw arguments/results,
credentials, schema or endpoint labels are added. The telemetry rewire and optional Langfuse backend have separate scope;
Langfuse remains queued on the [development board](../planning/README.md).

## Upgrade and rollback

Provision the reviewed dependency environment separately: Python **>=3.13.4**,
`jsonschema==4.25.1`, `referencing==0.37.0` and accepted IDNA **3.20**. The pinned
`mcp==2.3.0` / `mcp-types==2.3.0` packages are development interoperability
counterparts, not Friday's production transport or telemetry implementation.
This upgrade adds no installer/sync or environment mutation step to startup.

Back up your own configuration through your normal process. Introduce explicit
profile changes peer by peer, check safe operational diagnostics and canonical
names, and exercise the intended tools in your controlled application. To roll
back, stop owned MCP work and restore the prior explicit configuration/profile
with its reviewed compatible application version. Keep legacy stdio peers on their
legacy default or disable MCP. Do not switch an HTTP endpoint to legacy SSE by
inference, automatically retry a failed tool call, clean/migrate memory stores or
replace user configuration files as part of rollback.

The test suite uses synthetic Friday and independent pinned official SDK peers,
verified private TLS, loader/admission/budget/provenance regressions and explicit
cleanup counters. It does not establish public deployment, live credentials or
provider operation. Resources/prompts, agent mode, Tasks, interactive continuation,
OAuth discovery/login/refresh and subscription roles remain outside this profile.
Whole-initiative independent validation, maintainer acceptance and publication are
separate gates; unit acceptance or a successful SDK exchange is not full conformance.

## Alpha3 application checks

Install the aligned 0.1.0a3 application/package cohort rather than manually
substituting protocol dependencies. Before migrating a real peer, exercise the
[owned local round trip](17-mcp-client.md#offline-programmatic-round-trip), load
your intended MCP stanza without connecting, and inspect canonical selection.
Then test the actual peer in your controlled environment with explicit network,
credential and mutation policy. No public peer, collector or live provider was
needed for the local example.

Current optional-role exclusions include MRTR: valid modern input-required
requests return `input_required_unsupported` without callbacks, continuation or
opaque-state forwarding. Do not route that failure into an automatic tool-call
retry. Adding MRTR requires a separate interaction, state and security design.

## Implementation references

- [Pinned protocol contract](../planning/active/friday-mcp-protocol-upgrade/protocol-contract.md)
- [Package metadata](../../packages/friday-mcp/pyproject.toml)
- [Client transports](../../packages/friday-mcp/src/friday_mcp/client)
- [Server profile](../../packages/friday-mcp/src/friday_mcp/server)

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)
