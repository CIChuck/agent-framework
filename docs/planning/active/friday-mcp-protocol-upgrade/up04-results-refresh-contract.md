# UP-04 result fidelity and explicit catalog refresh contract

Status: Proposed; exact maintainer approval required before product construction.
Unit: MCP-UP-04. Target: frozen MCP2026-07-28 client tools, explicit2025-11-25
HTTP compatibility and preserved2024-11-05 defaults. Accepted baseline:
`3fd5437088c5ddf5d68be3a2a097770c294cba6b`; UP-03 acceptance is recorded separately.
[Construction directive](directives/CD-MCP-UP-004-results-manual-refresh.md),
[verification profile](verification-profile-UP-04.json) and
[proposal manifest](proposals/UP-04-authority-manifest.json) bind this contract.

## Current product and evidence boundary

Accepted UP-02A/02B already provide full bounded pagination, immutable output
schemas, text/structured string adaptation, unsupported-input/content dispositions
and no replay. UP-03 wires the dated clients into real Runtime/Chat without
changing the tool safety or storage authority. UP-04 hardens existing programmatic
manual refresh and result classification; it does not redo their implementation.

[Planning evidence](execution/up04-planning/report.md) includes a no-network,
in-memory peer using the actual modern base request/receive loop. It observes:

- A declared integer output schema rejects a string before refresh.
- Failed `MCPToolAdapter.get_tools(refresh=True)` leaves prior wrappers cached.
- A later wrapper call accepts that string when the client catalog was invalidated.
- A malformed modern result with `isError: true` and non-list `content` is classified
  as `tool_error` before mandatory content validation.

These are reproduced programmatic refresh/result gaps for this next slice,
not live-peer evidence or a replacement verdict on the accepted UP-03 integration.
HTTP catalog/header generation races are source-inspected construction risks;
required adversarial tests must establish their corrected wire behavior. The
accepted 2025 schema retains `execution.taskSupport`; the separately captured
[dated Tasks source](research-sources/up04/manifest.json) controls exclusion of
required-task tools. No Tasks implementation is proposed.

## Typed catalog generation and manual refresh

Keep `list_tools() -> list[dict[str, Any]]`, `call_tool(name, arguments) -> str`,
legacy constructors and `MCPToolAdapter.get_tools(refresh=False)` compatible.
The new optional refresh-aware seam belongs to the public MCP client package,
not Core/Runtime/Chat configuration or incidental private attribute inspection.
Define and export a declared runtime-checkable `MCPRefreshClient` protocol and
immutable, non-repr `MCPCatalogSnapshot` from `client/catalog.py`:

- `async refresh_tool_catalog() -> MCPCatalogSnapshot` returns the exact complete
  generation produced by that operation, not whichever snapshot became current
  by the time another task inspects a property.
- `current_catalog_snapshot: MCPCatalogSnapshot | None` returns only a complete,
  currently usable immutable snapshot; failed/in-progress refresh exposes none.
- `async call_tool_at_generation(name, arguments, generation) -> str` rejects an
  invalid/retired generation before issuing a mutating request.
- A snapshot has an owner-local positive generation, immutable tool definitions
  with independently decoded exports, and bounded integer rejection counts.
  Generations cannot be reused after disconnect/reconnect; snapshots contain no
  credentials, URLs, peer instructions, live handles or ambient telemetry state.

Generation alone never authorizes a tool. The wrapper retains exact routing,
validated definition and existing admission/observation metadata. Discovery-created
and `from_validated` wrappers bind a generation through the declared optional seam.
Custom clients implementing only the existing MCPClient protocol remain compatible;
no `getattr`, broad cast or source suppression substitutes for this typed contract.

An explicit refresh invalidates new generation-bound admissions until complete
bounded discovery succeeds. Serialize overlapping refreshes under their original
operation deadlines; an older operation cannot publish over a newer operation or
clear a newer successful catalog. A failed/cancelled/limited/partial refresh cannot
leave stale adapter definitions available through subsequent cache reads. Reset
rejection counts and definitions atomically with the resulting catalog. Never
partially publish pages, schemas or HTTP bindings. Reuse16-page/1MiB/256-entry,
32-depth/four-request/default30s caps and accepted lower Runtime budgets.

Every admitted call captures its output schema and, for modern HTTP, argument
header bindings from the same immutable generation before request issuance.
Refresh may not alter that call's validation or headers. A call already issued
settles once against its captured generation; newly attempted stale wrappers fail
with fixed local `catalog_unavailable`, without implicit discovery, call replay,
wire cancellation of unrelated requests or automatic replacement of registries.
Direct legacy/no-catalog calls keep the existing compatibility behavior. Once a
modern/2025 client has established or attempted an explicit catalog refresh, a
failed/invalid generation cannot turn output validation into a schema-free call.
Calls to removed/excluded tools fail before I/O; a successful later explicit
refresh allows newly created wrappers. Reconnect invalidates old wrappers even if
names and schemas happen to match. Concurrency limits and cleanup ownership apply
to waits/refresh tasks as well as issued requests; disconnect must settle owned
operations or retain an observable retryable owner.

Runtime/Chat keep startup/reconnect discovery and their existing transactional
registration. UP-04 adds no integrated in-place refresh API, no YAML knob, no
registry replacement, no per-turn schema pinning and no automatic peer instructions.
Use the existing public stop/start workflow for integrated rediscovery. Existing
native/MCP collisions, filters,25/50 counts,8192-byte schemas and token budgets
remain controlling and are exercised by the full integration regressions.

## Result validation and adaptation

Validate bounded JSON/envelope/tag/metadata/content shape before classifying
`isError`. A well-formed ordinary tool failure stays `tool_error` and need not
provide successful structured output or satisfy its success output schema. A
malformed error envelope/content stays a fixed protocol/result failure; it cannot
be excused by an error flag. Validate mandatory fields of each declared content
variant before choosing the supported/unsupported disposition. Accepted legacy
text compatibility remains explicit, rather than inferred from a2025 HTTP profile.

Modern complete results retain every supported text block in order, deterministic
JSON for structured-only results (including null/scalar/array), and the existing
bounded combined envelope for mixed text plus structured data. Preserve the
difference between omitted `structuredContent` and explicit null. Explicit2025
structured output stays object-only with its dated metadata grammar; modern rules
must not be applied to2024 or2025 merely because a shared boolean is false.

Success output schemas remain the accepted bounded acyclic/regex-free JSON Schema
2020-12 subset with an empty external reference registry. Reject unsupported
schemas before publication; no remote `$ref` resolution, new keyword/dialect,
regex evaluation or dependency. Enforce wire/result/depth/node/evaluation/adapted
output limits before retention, expensive validation and downstream sanitation.
Schema-validation exceptions and all peer payloads remain absent from exception
strings, chained traceback context, logs and telemetry.

Well-formed unsupported image/audio/resource-link/embedded content yields a fixed
`unsupported_content` failure for the selected modern/2025 profile. Do not silently
lose one block in mixed results, fetch content URIs, decode media, render arbitrary
HTML or promote peer annotations to trusted facts. Well-formed modern
`input_required` stays `input_required_unsupported`; malformed/unknown result tags
stay fixed invalid-result failures. Never fabricate input responses, forward opaque
state, perform callback requests, continue a tool call or cache tool results.

## Optional interaction boundary

The2025 Tools/Tasks negotiation can require task augmentation. Friday advertises
no Tasks support and sends no task-augmented requests. Exclude a2025 tool declaring
`execution.taskSupport: required` from ordinary callable publication, including an
inconsistent declaration without a matching server capability. Record only a
bounded count, and reject an explicit attempt to call an observed excluded name
before I/O with fixed `unsupported_task`. Missing/forbidden/optional taskSupport
remain normal-call candidates, subject to all other existing admission rules;
server Tasks capability alone never activates Tasks. Do not interpret this dated
field as a2026 extension. An unsolicited CreateTaskResult is not a tool success;
no task polling, cancellation, persistence or immediate-response promotion follows.

No subscriptions/listen, GET notification streams, cross-call result caching,
progress tokens, sampling, roots, elicitation, resource subscriptions or extension
capabilities are added. Unsolicited list-changed/progress/logging messages must
remain bounded and cannot trigger a refresh, model-context mutation, task or
telemetry-payload exposure. Modern HTTP still closes the request stream for
cancellation;2025 and stdio retain their accepted dated behavior.

## Safety, evidence and acceptance

All results retain the existing sanitization, untrusted provenance, quarantine,
atomic transcript pairing and explicit memory opt-in. Existing TelemetryInterface
injection owns one logical call observation; catalog helpers may not add a second
observer, exporter, outgoing trace/baggage or global state. Native tools and borrowed
clients/providers remain owned by their current layer.

Every applicable requirement of the 19 complete pinned sources and selected dated
schemas requires a preconstruction requirement-to-criterion/test plan and a final
source/positive/negative/command ledger. Original ledgers/control bytes remain
immutable. Correct raw 349 mandatory-keyword accounting in the new mapping; preserve
the earlier 347 terminology-only discrepancy as history. Map conditional Tasks
requirements honestly to non-task exclusion evidence or the unsupported-role
boundary, rather than claiming Tasks conformance. Fresh independent full-unit
VERIFIED precedes any completion proposal; maintainer acceptance and later UP-05/
UP-06/whole-initiative conformance/publication remain separate.
