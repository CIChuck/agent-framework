# MCP-WS-07 Implementation Report

Date: 2026-09-29
Status: Stable builder candidate; fresh independent review pending
Branch: `feature/friday-mcp-ws07-telemetry`
Work-unit base: `c05882e45d78dc83ad48ee17b156aa9efff6fff0`
Candidate: `2e36613eae6060a99c1255cce04fcb7a27bc7374`
Authority: [approved WS-07 directive](../directives/ws-07-telemetry-diagnostics-health.md)
Scope/freeze: [16-path product and unrelated fingerprint manifest](WS-07-product-manifest.json)

The approved first pass adds typed, allowlisted MCP events and an inspectable
operational snapshot. Runtime emits connection, list-tools, registration,
tool-call and disconnect outcomes through its existing lifecycle owner. Chat
adds final checked-output, per-turn budget and optional ingestion decisions.
The maintainer approved deferring a new Chat health command; no command,
configuration, dependency metadata, telemetry endpoint, memory store or
transcript schema was changed. This builder report is not an independent
VERIFIED result or maintainer acceptance.

## Boundaries and behavior

- Telemetry's immutable `MCPEvent` has closed event/reason literals,
  nonnegative capped counts and only scalar exported attributes. Server and
  canonical tool identifiers become stable 16-hex opaque references before
  either Debug or OTel receives an event. No caller-supplied dictionary,
  schema, description, exception, argument, output, env/header, command,
  cwd or memory text is exported. Invalid payloads and recorder failures
  fail closed without changing MCP behavior.
- `RuntimeMCPProvider` consumes its existing typed discovery, lifecycle,
  diagnostics and registration decisions. Its public
  `operational_diagnostics` snapshot includes retained collision contenders,
  configured optional/required failure outcomes, actual registered/capped
  counts, budget skips, truncation and ingestion outcome counts. Skip events
  are aggregated by server/reason, bounded to one event per category even for
  oversized catalogs. A failed/rolled-back registration never emits a
  successful registration. Failed cleanup never emits a false successful
  disconnect for a still-connected server.
- The accepted validated `MCPToolWrapper` has an optional metadata-only
  observer. Legacy/unvalidated wrappers reject observation; the MCP package
  gains no Telemetry dependency. Runtime attaches the observer only to
  admitted wrappers. Headless and Chat paths emit start/finish/failure around
  the single existing RPC; observer failure cannot alter its result.
- Chat's public bridge accepts an optional injected telemetry interface and
  exposes its provider as before. A checked call emits its final categorical
  outcome after output policy, distinguishing RPC success from truncation,
  sanitizer block or failed result. The turn processor emits MCP budget
  rejections from the accepted selection snapshot without selecting again.
  Optional memory observation occurs after durable receipt verification and
  publication attempts: disabled/skipped, pending and published outcomes
  remain distinct. A false/throwing publication does not become a published
  event or change receipt/retry behavior.
- Existing telemetry opt-in and default-disabled direct MCP semantic
  ingestion remain unchanged. The first pass exposes Python diagnostics and
  injectable events; it does not wire a new user command or telemetry backend.

## Builder validation

| Check | Result |
| --- | --- |
| Final focused changed-boundary set: Telemetry event, Runtime loading/registration, MCP adapter/execution, Chat bridge/security/budget/memory | **294 passed** |
| Telemetry package | **56 passed**, exit 0; an existing OTel background exporter reported a post-test closed-stream error after pytest completed |
| Runtime package | **194 passed** |
| MCP package | **65 passed** |
| Chat package | **620 passed, 5 skipped, 1 failed, 3 errors**; PTY timing and three localhost bind permissions match the independently recorded pre-WS-07 baseline in [VAL-015](../validation/VAL-015-report.md). This command is nonzero, not waived or claimed passing. |
| Top-level integration | **79 passed, 1 failed**; the board test still asserts 22 tasks while the validated board has 23. This command is nonzero. |
| Four MCP-specific integration modules | **56 passed** with local peers, real Chroma/SQLite and transcript paths |
| Ruff on all four touched packages | Pass |
| Affected nine source files, mypy Python 3.13 with silent unrelated imports | Pass |
| Offline lock consistency, `uv lock --check --offline` | Pass; 208 packages resolved from the existing lock |
| Board validate/next/show, dashboard render check, documentation lifecycle/links, diff/whitespace | Pass; 23 board tasks and 366 Markdown files |
| Exact product manifest, historical validation bytes and five unrelated fingerprints | Pass; exactly 16 approved product/test paths, zero scope error |
| Offline wheels and isolated public imports | All 16 framework wheels build; four touched packages import from freshly extracted wheels in a Python `-I` process with existing declared external distribution files, and a typed MCP event is emitted without editable source or `PYTHONPATH` |

An initial `uv build --no-build-isolation --offline` attempt for the four
touched packages exited nonzero because the active environment lacks
`hatchling`. The declared normal isolated backend, `uv build --wheel
--offline`, then built all 16 packages successfully from the current source.
This is not a clean resolver installation: the prior clean offline resolver
gap for uncached `litellm==1.100.1` remains. No network, provider, paid
endpoint, credential or external side effect was used.

## Task and handoff evidence

| Tactical task | Builder evidence |
| --- | --- |
| `MCP-07-01` | Ordered lifecycle/list-tools/skip/register/call/disconnect tests; headless and Chat public paths; failure/rollback/cancellation classifications. |
| `MCP-07-02` | Closed payload model; Debug/OTel input, peer env/schema/argument/output/exception and Chat real-peer sentinel negatives. |
| `MCP-07-03` | Public diagnostic snapshot reuses accepted states and both collision contenders; cap, optional/required failure, budget, truncation and ingestion tests. |
| `MCP-07-04/05` | Explicitly approved first-pass deferral; no command paths modified. |
| `MCP-07-06` | Immutable typed event and operational diagnostic models, no log-string parsing. |

The [product manifest](WS-07-product-manifest.json) records each changed file's
SHA256, the accepted base, five unchanged unrelated fingerprints and unchanged
historical validation paths. Only the 16 directive-listed product/test files
changed in the candidate. The unchanged unrelated paths are modified
`.DS_Store`, deleted `family-tree.md`, `docker-bench-security/`, the Chat
config backup and the Sandbox audit Dockerfile. Review should compare
`c05882e..2e36613` as the full WS-07 aggregate, run its own checks and
return exactly `VERIFIED`, `CHANGES_REQUESTED` or `BLOCKED` with a complete
reproducible report. WS-08, maintainer acceptance and delivery remain separate.
