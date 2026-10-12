# Friday MCP protocol and remote transport upgrade

---
title: Friday MCP protocol and remote transport upgrade
initiative: friday-mcp-protocol-upgrade
document_type: initiative-index
status: approved
work_state: started
condition: normal
created: 2026-10-11
updated: 2026-10-12
next_gate: approve bounded CD-MCP-UP-001 A01 IDNA dependency exception before construction
implementation_authority: granted for CD-MCP-UP-001 only
execution_phase: planning
validation_state: blocked
---

## Current checkpoint

Chuck Russell approved the MCP-UP-01 contract and exact CD-MCP-UP-001 slice
on 2026-10-12. The board keeps this at priority **4**.
[Approval evidence](approval.json) preserves the original proposal hashes and
explicit statement. Product files remain unchanged during execution preparation;
code generation requires the named MCP branch and a recorded started transition.

Core telemetry TELEM-01 through04 is accepted and closed. The proposed MCP
baseline is `46005353046553477417a730f05ff21ead64a00d`, containing accepted
TELEM-04 product `5c3a0e6dc8ba995bad9e7dfb8c574f5dfd335bc8` and VAL-010 VERIFIED.
[Accepted telemetry evidence](../../../archive/completed/2026/friday-telemetry-rewire-telem-04/README.md)
supersedes the original queue note's pending REM-005 status. The
[baseline receipt](baseline.json) verifies fifteen product hashes and forty-six
accepted controlling hashes. Telemetry waivers have expired; they do not transfer.
[Langfuse remains queued after this upgrade's acceptance](../../queued/friday-langfuse-integration/README.md).

## Review packet

- [Build plan and initiative acceptance criteria](build-plan.md)
- [Protocol/transport contract and compatibility matrix](protocol-contract.md)
- [Tactical order, exact checks and fixture effects](tactical-plan.md)
- [CD-MCP-UP-001: exact first twelve-path construction scope](directives/CD-MCP-UP-001-client-core.md)
- [Normative conformance target and research-to-test mapping](conformance-matrix.md)
- [Official-specification and SDK decision record](research.md)
- [Exact approval evidence](approval.json)
- [Frozen normative source bytes and immutable schema pin](research-sources/manifest.json)
- [Current source/accepted baseline receipt](baseline.json)
- [Hashed proposal authority manifest](authority-manifest.json)
- [Execution log and stop point](execution-log.md)

## Objective and decisions

Upgrade Friday from fixed `2024-11-05` behavior to released
[`2026-07-28`](https://modelcontextprotocol.io/specification/2026-07-28), rechecked
against the official latest specification on 2026-10-12. Deliver modern stdio
and Streamable HTTP client tools through the existing
`tools.providers.mcp.config.servers` YAML integration, then a modern tools-only
Friday server. Preserve accepted tool safety, provenance, budgets and
provider-neutral TelemetryInterface injection.

[Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)
uses POST requests with JSON or request-scoped SSE responses. Friday's existing
GET stream/separate POST endpoint is legacy HTTP+SSE. Adding a transport name or
changing the version constant alone cannot deliver modern support.

Retain Friday's current protocol core; use official Python SDK **2.3.0**, pinned
as a development interoperability counterpart. This preserves accepted ownership/
safety boundaries and avoids adopting SDK automatic retry/caching/input and
tracing defaults unchanged. The research records the tradeoff and tagged source.
Friday stays Python >=3.13.4.

Support explicit modern/auto stdio plus retained `2024-11-05` compatibility;
add modern HTTP and explicit `2025-11-25` HTTP compatibility next. Retain existing
programmatic legacy SSE with no automatic transport fallback or integrated-runtime
SSE expansion. The first remote auth profile is unauthenticated HTTPS or an
origin-scoped supplied bearer token; OAuth login is deferred.

## Fresh source gaps

| Surface | Verified current behavior | Planned correction |
| --- | --- | --- |
| Client/server core | Hardcoded 2024-11-05, initialize/initialized | Revision-aware metadata/discovery/results and honest capabilities |
| Client remote transport | GET stream discovers separate POST endpoint | Distinct Streamable HTTP JSON/SSE implementation |
| Runtime config/loading | Strict local stdio command and trust contracts | Explicit reviewed remote policy and transport-specific YAML assembly |
| Catalog/tool results | One page; legacy text extraction | Bounded full pagination and typed text/structured/interim disposition |
| Chat tools | Shared runtime MCP registration/selection | Preserve registry/filter/budget/safety flow with real remote-path evidence |
| Server remote binding | /sse and /message sessions | Separately bounded modern tools-only server, origin/auth/lifecycle proof |

Exact source paths and hashes are in the baseline/research records. Accepted
[earlier MCP work](../../../archive/completed/2026/friday-mcp/README.md) remains
the safety baseline; its acceptance does not claim this new protocol profile.

## Construction order and next gate

First approved unit **CD-MCP-UP-001 / UP-02A** adds modern client discovery,
metadata, bounded catalog/results and explicit modern/auto stdio modes while
keeping current callers on the legacy default. Independent official SDK stdio
wire tests and lifecycle/privacy regressions are required.

Then deliver HTTP client (UP-02B), remote YAML/Runtime/Chat (UP-03), selected result/
refresh hardening (UP-04), modern tools server (UP-05), and aggregate docs/verification
(UP-06). Each later product slice needs its own exact directive. Optional extensions,
Langfuse, config includes, adaptive tool continuity and live deployment are separate.

Next: commit the approved controls and frozen normative source pins, create
`feature/friday-mcp-protocol-upgrade`, and record the start. Fresh independent
product validation follows a committed implementation candidate. Planning checks
are not product VERIFIED, completion, acceptance or delivery authority.


## Dependency preparation stop — 2026-10-12

SDK resolution requires IDNA >=3.18, versus the existing workspace 3.11 pin.
The isolated no-churn resolver proves this conflict. The [A01 amendment](directives/CD-MCP-UP-001-A01-sdk-dependency.md)
proposes only IDNA 3.11 to3.20 and preserves all other existing versions.
Original eight criteria and twelve product paths remain controlling. Private
product metadata/lock have been restored; no client source edits or SDK installation
have occurred. Reviewable original diagnostics and full proposed lock are retained.
