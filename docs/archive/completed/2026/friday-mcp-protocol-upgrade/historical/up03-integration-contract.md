# UP-03 Runtime, YAML and Chat integration contract

Status: **Proposed; construction approval pending.** Prepared 2026-10-12.
Bound only by separate CD-MCP-UP-003 and its exact proposal manifest. No source
changes are authorized by this planning document. The accepted HTTP unit and
all earlier controls remain immutable evidence of their reviewed candidates.

## Configuration surface

Retain `tools.providers.mcp.config.servers`; use the canonical Runtime parser in
both headless Runtime and `load_friday_py_config`. Provider enable/mode/include/
exclude, discovery, limits, security and ingestion keep their existing locations.
Absent transport remains stdio. Normalize the discriminator before validating a
strict, frozen union of existing `MCPRuntimeServerConfig` (stdio) and new
`MCPRuntimeHTTPServerConfig`. Every supplied field is validated even for a disabled
entry. Do not retain unknown keys or accept bools as integers.

| Entry / field | Exact proposed semantics |
| --- | --- |
| Shared `name`, `enabled`, `required` | Existing bounded identifier, booleans, unique canonical server IDs; required+disabled invalid |
| Shared `timeout_seconds`, `tool_timeout_seconds` | Existing positive strict integer defaults 30 and 60; operative modern/HTTP budgets are lower-only and never exceed protocol 30 seconds |
| Stdio `transport` | `stdio`, default when omitted |
| Stdio `protocol_profile` | `legacy` default (2024-11-05), explicit `modern` (2026-07-28) or `auto` (accepted bounded read-only stdio discovery/fallback) |
| Stdio local fields | Existing command/args/env/workspace cwd and retry defaults/validation preserved; HTTP-only fields forbidden even when empty/null |
| HTTP `transport` | Exactly `streamable_http`; no `http`, `sse`, or HTTP-to-SSE fallback |
| HTTP `protocol_version` | Required explicit `2026-07-28` or `2025-11-25`; no auto/default/negotiated fallback |
| HTTP `trust_level` | Required explicit `remote`; it acknowledges configured peer admission and does not make results trusted |
| HTTP `url` | Required ASCII endpoint, 1..4096 characters, HTTPS only, validated by accepted HTTPEndpoint.parse before I/O; no userinfo/query/fragment/backslash/zone ID |
| HTTP `auth` | `none` default or `bearer_env`; unknown values invalid |
| HTTP `credential_env` | Required only for bearer_env, forbidden for none; literal POSIX environment identifier `[A-Za-z_][A-Za-z0-9_]{0,127}`; never `${...}`/fallback/interpolation/inline token |
| HTTP `network.allowed_addresses` | Default empty tuple; at most 16 unique canonical literal IP addresses, each an exact per-peer opt-in; no hostname, CIDR, wildcard or IPv4-mapped IPv6 |
| HTTP `network.allowed_ports` | Default `[443]`; 1..16 unique strict integer ports 1..65535; endpoint port must be present; no implicit permission for non-443 ports |
| HTTP `retry_attempts` | Default and only value 0; neither startup nor a call retries HTTP operations automatically |
| HTTP forbidden fields | command, args, env, cwd, protocol_profile, inline token, arbitrary headers, cookies, proxies, redirects, TLS verification disable/CA config, fixture HTTP flag and config includes |

Unknown/inappropriate transport fields are rejected by the union before any
factory, environment reference lookup, subprocess or network operation. Public
legacy protocol-local MCPConfig/MCPServerConfig and SSEMCPClient remain unchanged;
remote YAML is not normalized into a fake stdio command or permissive legacy SSE
config. MCPServerRuntimePolicy retains its accepted local-only semantics; the new
strict HTTP Runtime model owns the explicitly different remote connection shape.

## Explicit Core policy amendment

This proposal authorizes only the following additive changes to the accepted
local-only Core policy, subject to approval of the exact directive:

- `integrated_transport`: retain default `stdio_only`; add `stdio_and_streamable_http`.
- `trust_posture`: retain default `local_stdio_only`; add `explicit_remote`.
- Permit only the two matching pairs. Enabled HTTP entries require the second
  pair as well as their own explicit `trust_level: remote`. Disabled HTTP entries
  are still shape-validated but do not require the provider's remote-enable pair.
- Preserve workspace scope, explicit stdio commands, redaction=true and raw
  result/argument-hash storage=false invariants. SSE admission stays prohibited.
- Add `streamable_http` to MCPToolMetadata transport without changing existing
  stdio/SSE values or provenance/storage fields. Populate actual transport and
  trust from validated configured server policy; never hard-code remote as stdio.

Old YAML and public default DTOs continue describing stdio-only/local-only use.
Provider/entry disable and `auto_connect: false` suppress factory invocation and
credential lookup. A disabled required entry remains invalid.

## Credential and network boundary

Resolve only the named reference when an enabled bearer HTTP connection is
assembled, through a typed injectable resolver. The production resolver reads
that single name with `os.environ.get`; it does not enumerate environment, read
.env/keychain/stores, or mutate environment. Missing/empty/invalid token is a fixed
safe connection failure. Keep the resolved token only in the live non-repr client,
never in config models/dumps, diagnostics, logs, exception chains, reports,
transcript, memory or telemetry. Explicit reconnect may resolve the current
reference again; there is no automatic credential refresh or call replay.

The Chat loader must reject interpolated credential_env syntax before its generic
environment interpolation can resolve it. Runtime/Chat config error formatting
must omit invalid values, untrusted keys and exception context. Tests inspect
repr, str, causes/contexts, model_dump, captured logs/events and stored call facts
using synthetic token/URL/argument/result/header/peer-error sentinels. Values of
valid environment references stay unresolved through load, validate and dump.

Map network policy to the accepted HTTPEndpointPolicy with
`allow_fixture_http=False` unconditionally in production assembly. No configurable
TLS relaxation. Public destinations are allowed only after remote opt-in and
all actual DNS candidates satisfy the accepted address policy; non-public literal
addresses need exact per-peer allowlisting. Reject forbidden special classes and
mapped addresses as the accepted policy does, including mixed DNS answers.
Every new connection must use the policy backend's validated numeric address,
retain the original hostname for TLS/SNI, and recheck DNS/address/port. URL-only or
startup-only checks are insufficient. No redirects, ambient proxies, cookies,
OAuth discovery/login/refresh, arbitrary auth/header overrides or forwarding.

## Typed assembly and lifetime ownership

Add a public frozen `MCPManagedServer` record in friday_mcp.client.manager, with
name, enabled and a non-repr zero-argument typed client factory. Add optional
keyword-only `managed_servers` to MCPClientManager. With it absent, all existing
MCPConfig-based manager APIs retain their behavior. With it present, it is the
complete ordered connection-entry list; require legacy config.servers to be empty
in that mode, and reject mixed configuration instead of silently merging or
ignoring entries. Reject duplicate names/invalid entries before invocation.
Export the record through friday_mcp.client. The factory returns MCPClientBase,
never an arbitrary untyped adapter. Manager remains the single client/adapter
owner; runtime does not write manager._clients/_adapters or duplicate routing.

Add friday_runtime.mcp_clients as the typed construction seam. It creates stdio
clients using accepted public profile/limits constructors and HTTP clients using
exact protocol_version, endpoint policy, limits and resolved optional bearer.
The manager adopts each constructed client before await connect; partial startup
is inspectable/retryable until disconnect succeeds. Preserve primary failures
and cancellation while reporting retained cleanup ownership separately. No new
owner replaces an incompletely cleaned manager/client/registry. Public Runtime
and Chat start/stop retry paths must settle owned clients, pools, streams, tasks,
child processes and registered MCP tools; borrowed network providers remain open.

Keep old stdio timeout/retry behavior for legacy entries. Modern/auto stdio and
HTTP enforce a single startup deadline across handshake and full discovery,
bounded by min(server timeout, global connection timeout, 30). Calls have
min(server tool timeout, global tool timeout, 30) and min(global call concurrency,
4) for these new profiles; max result bytes min(config limit, 65536). Catalog
protocol caps stay 16 pages /1 MiB /256 entries /depth32 /4096 nodes and can only
be lowered; Runtime admission still applies 25 per server /50 total /8192 complete
schema bytes per tool and existing selected schema token budget. Legacy public
configuration defaults are not rewritten merely to mirror protocol maxima.

HTTP outer startup retries remain zero. Every mutating tools/call is issued at
most once under disconnect/status/header/session/timeout/cancellation failures.
Preserve the independently verified 2025 generation-owned session recovery and
modern request-scoped cancellation by using the accepted client unchanged.
Do not add a runtime retry, auto reconnect loop, GET listener, refresh subscription,
interactive continuation, per-call result cache, or fallback transport.

## Admission, headers and model-facing data

Keep the accepted complete-discovery -> sanitize -> canonicalize/filter/cap ->
transactional registration -> per-turn selection chain. Required-peer failure
blocks startup and rolls back owned publications. Optional failures retain safe
bounded diagnostics and settle their owner. No partial/stale catalog or bindings
are exposed, native tools are preserved, collisions fail closed, and exact
original peer-tool names remain the wire routing identifiers.

Make only two narrow additions to the accepted inline input-schema sanitizer:
allow a root `$schema` equal to canonical JSON Schema 2020-12, and admit valid
`x-mcp-header` schema annotations for modern HTTP after applying the accepted
public `header_bindings` validation. Re-export that pure helper through the client
module for typed Runtime consumption; no new header extractor/parser. Malformed
or unreachable annotations exclude the tool before publication. Strip these
protocol-only declarations from the model schema only after validation; preserve
client-side original schemas/header bindings and JSON application values. Never
mutate the live client's catalog to sanitize model context. Root dialect omission
continues working; unsupported/nested declarations and all other previously
unsupported schema keywords/references remain explicit admission rejections.
Do not add `$ref`/definitions/composition behavior beyond the accepted subset.

Both raw complete definitions and final registry exports retain the existing
byte/token bounds, sanitization, copied/verified model schema and collision
behavior. Peer server instructions/identity/metadata never grant policy or enter
model context automatically. Text/structured/mixed results follow the accepted
string adapter, then existing output sanitizer, MCP provenance, quarantined
transcript and explicit memory opt-in. No resource/image/link fetch or raw-result
persistence. MCP is still subject to accepted per-turn count/token/result budgets;
this unit does not implement queued discovery-aware tool pinning.

## Provider-neutral observations

Use the existing TelemetryInterface/MCPTelemetryHelper injection and accepted
TELEM-01..04 context. One logical Runtime/Chat call produces the existing logical
observation sequence; credential resolution and HTTP internal recovery create no
duplicate successful call. Never install or change global providers, propagate
W3C trace/baggage to peers, or export tokens, URLs, headers, schema/argument/result
content or peer messages. Keep a supplied recorder/provider borrowed at shutdown.
Langfuse remains optional and queued after the whole MCP initiative is accepted.

## Proposed production YAML example

This example becomes supported only after approved construction and independent
verification. It makes no network request during planning.

```yaml
tools:
  providers:
    mcp:
      enabled: true
      mode: all
      config:
        auto_connect: true
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

Unauthenticated uses `auth: none` and omits credential_env. Exact2025 compatibility
changes only protocol_version to '2025-11-25'. Local stdio remains its existing
command stanza; opt into `protocol_profile: modern` or `auto` explicitly. Default
examples remain disabled and contain no credentials/real service addresses.
