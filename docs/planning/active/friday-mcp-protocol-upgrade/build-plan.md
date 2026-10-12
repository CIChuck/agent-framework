# MCP upgrade build plan

Status: Approved by Chuck Russell on 2026-10-12 for the contract and first
CD-MCP-UP-001 construction slice; later slices retain separate directives.

Upgrade the client and server to the dated MCP `2026-07-28` tools profile,
deliver Streamable HTTP through `tools.providers.mcp.config.servers`, and retain
the accepted local stdio workflow. The [protocol contract](protocol-contract.md)
defines supported combinations and failure behavior. The [tactical plan](tactical-plan.md)
defines delivery order. [CD-MCP-UP-001](directives/CD-MCP-UP-001-client-core.md)
is the first approved construction unit; approval of it does not grant later units.

The required outcome is conformance to the official MCP **2026-07-28**
specification and dated authoritative schema for our declared roles/transports/tools
profile. The [conformance mapping](conformance-matrix.md) binds primary-source
authority, applicable normative requirements and acceptance evidence. Full
initiative conformance requires all declared profiles and independent verification.

## Authority and baseline

Explicit maintainer direction controls over this proposal. Apply [AGENTS.md](../../../../AGENTS.md),
the [engineering policy](../../../reference/policies/repository-engineering-policy.md),
the [task lifecycle](../../../reference/policies/development-task-lifecycle.md), and
the [independent validation policy](../../../reference/policies/independent-validation-policy.md).
Accepted earlier MCP safety contracts remain controlling unless an exact later
directive explicitly changes them. A framework MCP directive is separate from
the FridayV2 parity pass; it supplies no general exception to that pass's freeze.

The inspected baseline is `46005353046553477417a730f05ff21ead64a00d` on
`feature/friday-telemetry-rewire`. TELEM-01 through TELEM-04 are accepted and
closed. TELEM-04 product is `5c3a0e6dc8ba995bad9e7dfb8c574f5dfd335bc8`, with
VAL-010 VERIFIED and acceptance recorded at `4600535`. The
[baseline receipt](baseline.json) pins the source inventory and accepted controls.
Langfuse remains [queued after MCP acceptance](../../queued/friday-langfuse-integration/README.md).
The old telemetry waivers have expired and do not authorize MCP construction.

## Requirements and acceptance

| ID | Required behavior | Owner / first delivery | Acceptance evidence |
| --- | --- | --- | --- |
| UP-AC-01 | Revision-aware metadata, discovery, honest capabilities and safe version errors | MCP client / UP-02A | Official SDK stdio counterpart plus deterministic wire tests; explicit modern and legacy cases |
| UP-AC-02 | POST-based Streamable HTTP, JSON/SSE framing, metadata headers and isolated cancellation | MCP transport / UP-02B | Independently maintained SDK HTTP server, adversarial stream fixtures, concurrent request isolation |
| UP-AC-03 | Strict transport-specific YAML, credential references and remote trust policy | Core/runtime/Chat / UP-03 | Real YAML loader to runtime/Chat registration, selection, call and shutdown; invalid config causes no I/O |
| UP-AC-04 | Complete bounded discovery, result fidelity and explicit interim/unsupported result disposition | MCP / UP-02A and UP-04 | Pagination cycles/caps, structured-only and mixed results, error cases, unsupported input requests, schema/result limits |
| UP-AC-05 | Preserve canonical naming, filters, admission, provenance, sanitization, quarantine and memory opt-in | Runtime/Chat / UP-03 and UP-04 | Accepted MCP security/context/transcript/memory regression suites; exact original peer-tool routing |
| UP-AC-06 | Preserve provider-neutral telemetry and owned lifecycle semantics | MCP/runtime/Chat / every unit | No raw content/credentials or global-provider changes; no duplicate observations, leaked tasks, orphan processes or ambiguous call replay |
| UP-AC-07 | Modern server tools profile with safe HTTP origin/auth/bind rules | MCP server / UP-05 | Official SDK client against Friday server; declared role/version matrix, metadata errors and cancellation |
| UP-AC-08 | Accurate configuration/migration documentation and aggregate verification | MCP/runtime/Chat / UP-06 | Working stdio/HTTP examples, exact pinned counterpart versions, complete required checks and fresh independent VERIFIED before completion proposal |

## Dependency decision

Retain Friday's custom protocol/transport implementation for this upgrade.
Pin the official Python SDK `mcp==2.3.0` as a development interoperability
counterpart, not a runtime dependency. The [research record](research.md)
documents the release, MIT license, transport support and relevant defaults.
This is a maintenance tradeoff: Friday must implement and test the selected
wire profile, instead of delegating conformance to the SDK.

SDK v2 supports the target. Its high-level client also supplies caching, input
round trips and header-mismatch retries; SDK tracing can participate in the
global OpenTelemetry provider. These can be controlled through lower-level
integration, but adopting that integration would change ownership and dependency
boundaries while our current adapters already enforce accepted Friday policies.
Keeping the current core makes the first directive smaller. SDK adoption may be
revisited by a separately scoped decision with privacy/lifecycle evidence.

Friday remains Python `>=3.13.4`. The SDK's lower supported Python floor does
not introduce Python 3.10 compatibility work for Friday. No dependency has been
installed or resolved during this planning step. Before construction, freeze
the exact SDK artifact and transitive lock changes in an isolated environment.
Unrelated package upgrades are outside the approved directive.
Declare `jsonschema==4.25.1` and `referencing==0.37.0` directly in friday-mcp for
output-schema validation and its explicit reference registry; both versions are
already present in the workspace lock. Validation must refuse
remote reference retrieval and enforce schema/result bounds before evaluation.

## Scope limits

HTTP OAuth discovery/interactive login, identity assertion, automatic sampling,
elicitation/roots, Tasks, Apps, Skills, WebSockets, config includes/WS-09,
adaptive tool selection/pinning, model-provider changes and Langfuse are deferred.
The first remote profile supports unauthenticated HTTPS or a maintainer-supplied,
origin-scoped bearer token. This is a bounded authentication profile, not a claim
of complete MCP OAuth support. Server publication and live external-peer calls
are separate effects; fixture interoperability is sufficient for this packet.

## Closeout

Each approved construction unit freezes a committed candidate, exact authority
and diff, required check results and counterpart artifacts. A fresh read-only
validator returns VERIFIED, CHANGES_REQUESTED or BLOCKED. The controller may
propose completion only after required verification; acceptance and delivery
remain maintainer decisions. No planning result is product conformance evidence.
