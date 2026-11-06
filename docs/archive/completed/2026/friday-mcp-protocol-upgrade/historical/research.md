# MCP-UP-01 research and source-gap record

Checked 2026-10-12. Primary sources only. This records document/source inspection;
it does not assert executed interoperability or dependency installation.
Complete normative source bytes and the immutable schema-commit verification are
now archived in [the frozen source manifest](research-sources/manifest.json).

## Official specification

[Latest](https://modelcontextprotocol.io/specification/latest) resolves to
[`2026-07-28`](https://modelcontextprotocol.io/specification/2026-07-28).
[Versioning](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning)
distinguishes per-request modern metadata from legacy initialization. A recognized
modern error is different from the transport-specific legacy fallback signal.
[Discovery](https://modelcontextprotocol.io/specification/2026-07-28/server/discover)
defines supportedVersions, capabilities and optional self-reported serverInfo.
The [base protocol](https://modelcontextprotocol.io/specification/2026-07-28/basic/index)
requires resultType and reserves error codes that overlap Friday's existing
local-only safe exceptions; the upgrade must keep wire and local errors distinct.

[Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)
replaced HTTP+SSE in 2025-03-26. In this revision it uses one POST endpoint with
JSON or request-scoped SSE responses, no GET notification endpoint or protocol
sessions, and required metadata/method/name headers. Header annotations and safe
encoding need explicit implementation. Closing a response stream cancels that
request; resumption is absent. [Stdio](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio)
has its own discovery/fallback and cancellation mechanics.

[Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) and
the [dated schema](https://modelcontextprotocol.io/specification/2026-07-28/schema)
define pagination, structuredContent (any JSON value), outputSchema, typed
content and complete/input-required results. The
[MRTR contract](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/mrtr)
does not require a client to satisfy unsupported input requests or retry; Friday
will report an explicit unsupported-input outcome without a continuation.
The [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
is release context, not authority to enable every optional extension.

Anthropic's [connector documentation](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector)
describes Claude's connector. Friday's profile is bound to the protocol documents
and tested roles; connector compatibility alone is not Friday conformance evidence.

## Python SDK evaluation

The official [latest release](https://github.com/modelcontextprotocol/python-sdk/releases/tag/v2.3.0)
is **2.3.0**, released October 2. Use this exact tag for the independent counterpart,
not main/latest at execution. Its [tagged metadata](https://github.com/modelcontextprotocol/python-sdk/blob/v2.3.0/pyproject.toml)
declares MIT, Python >=3.10, Pydantic, AnyIO, httpx2>=2.10.0, mcp-types tied to
the SDK version, server/authorization dependencies and opentelemetry-api.
The current prose [SDK landing page](https://py.sdk.modelcontextprotocol.io/)
states Python 3.11+; use tagged package metadata for dependency resolution.
Neither statement lowers Friday's >=3.13.4 requirement.

[Protocol modes](https://py.sdk.modelcontextprotocol.io/protocol-versions/)
support modern and legacy eras. The
[tagged high-level client](https://github.com/modelcontextprotocol/python-sdk/blob/v2.3.0/src/mcp/client/client.py)
defaults to auto negotiation and in-memory caching, automatically drives input
round trips, and retries after a HeaderMismatch rejection. That rejection is
not an ambiguous transport failure; this is not a claim that the SDK blindly
replays disconnected mutations. Friday's approved profile chooses explicit
disposition and no automatic tool-call replay.

The [tagged dispatcher](https://github.com/modelcontextprotocol/python-sdk/blob/v2.3.0/src/mcp/shared/jsonrpc_dispatcher.py)
creates client spans, injects wire trace context and uses peer error messages in
span status descriptions. [SDK OpenTelemetry documentation](https://py.sdk.modelcontextprotocol.io/run/opentelemetry/)
also describes default tracing and propagation. These behaviors conflict with
Friday's chosen content-safe, injected-provider telemetry profile if adopted
unchanged. The source places the client tracing seam inside the dispatcher;
server middleware removal alone does not solve client behavior.

Decision: retain the existing core/transport ownership, pin SDK 2.3.0 for
development interoperability, and avoid a new production SDK dependency. This
is a bounded implementation choice, not a judgment that SDK integration is
impossible. A future adapter could isolate these defaults with a separate
privacy/lifecycle/dependency review. The cost of the current choice is explicit
Friday conformance maintenance, covered by adversarial wire and independent SDK
counterpart tests. SDK fixtures use synthetic values and disabled exporters.

For output validation, declare the already workspace-locked jsonschema 4.25.1
directly. Its [reference documentation](https://python-jsonschema.readthedocs.io/en/v4.25.1/referencing/)
supports an explicit registry/retrieval policy. Friday must refuse remote schema
retrieval; ordinary JSON Schema validation is not authorization to fetch a URL.

## Fresh local source gaps

| Inspected path | Gap / accepted behavior to preserve |
| --- | --- |
| `client/base.py` | Fixed 2024-11-05; unsupported roots/sampling claims; no version validation; one-page catalog; text-only extraction; safe tool-error identifiers and partial-connect cleanup already exist |
| `client/stdio.py` | Accepted child spawn/drain/reap ownership and retryable cleanup; no modern profile selection |
| `client/sse.py` | Legacy endpoint-discovery GET+POST transport, not modern HTTP |
| `client/manager.py` | stdio/SSE factory; retained partial client ownership and explicit raising startup API |
| `config.py`, `protocols.py` | stdio/SSE only and legacy handshake documentation; existing source-wide type suppressions are inherited debt |
| `server/base.py`, `server/sse.py` | Legacy revision and /sse + /message server exposure; modern discovery/binding absent |
| `friday_runtime/config.py` | Strict local stdio configuration, no URL/remote trust fields |
| `friday_runtime/mcp_loading.py` | Builds command-based package config and owns safety/discovery/cleanup/admission |
| `friday_core/mcp.py` | Accepted integrated_transport=stdio_only and local_stdio_only trust; exact later amendment needed before remote runtime exposure |
| `friday_chat/tools/mcp.py` | Uses shared runtime provider and owns Chat registry bridge; retain canonical naming/budget/filter behavior |

Paths are pinned under [baseline.json](baseline.json). The two first-unit existing
source files pass current Ruff and Mypy; this planning check is not a product
test result. The accepted telemetry product's fifteen hashes and forty-six
controlling acceptance hashes were checked before preparing this proposal.
