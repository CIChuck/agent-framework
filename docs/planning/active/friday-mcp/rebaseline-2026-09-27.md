# Friday MCP Rebaseline — 2026-09-27

**State:** Read-only implementation audit and proposed scope correction; no
implementation approval or completion claim.

## What Already Exists

The standalone `friday-mcp` package is real, substantial prior work. It has
stdio and SSE client transports, `MCPClientManager`, MCP-to-Friday tool
adapters, configuration models, and server-side agent/tool exposure code. The
core package implementation predates this enhancement plan: Git history adds
`client/manager.py` in `55f0c29` on 2026-01-05. Preserve these public APIs;
the enhancement must integrate and harden them, not recreate the package.

The headless runtime has a partial typed MCP provider configuration surface,
but `register_runtime_tools()` deliberately raises `ToolProviderLoadError`
when `tools.providers.mcp.enabled` is true. Friday Chat has no MCP client
integration in its current source. The planned MCP policy/provenance DTOs are
absent from package source. The existing `MCPConfig` also accepts an unknown
key without error, so it is not the proposed strict canonical config model.

This is the distinction between **package present** and **integrated feature
complete**. The current board item is the latter. Existing server-side code
is a separate baseline, not evidence that the client-enhancement acceptance
criteria were met.

## Workstream Reconciliation

| Workstream | Existing baseline | Remaining outcome / status |
| --- | --- | --- |
| WS-00 contracts and policy | Protocol-local config, tool wrapper, and core tool protocol exist. | Planned shared DTOs, conservative defaults, metadata strategy, naming/collision rule, SSE posture, and argument-redaction/hash policy are not established; **not started under this packet**. |
| WS-01 strict configuration | Runtime parses an MCP provider stanza and `friday-mcp` has config models. | Strict canonical keys, required-server behavior, reserved `config_file` rejection, and app normalization remain; **partial baseline only**. |
| WS-02 runtime lifecycle | `MCPClientManager` and transports can be used programmatically. | Runtime ownership, connection/discovery lifecycle, optional/required failures, and bounded startup remain; runtime currently rejects enablement. |
| WS-03 registry integration | `MCPToolAdapter` wraps discovered tools and prefixes names. | Deterministic normalization/collision checks, metadata, filters, caps, and registry registration remain. |
| WS-04 Friday Chat context | Generic Chat tool selection and schema budgeting exist. | MCP source/configuration, selection, continuation, and budget integration are not present. |
| WS-05 execution provenance | MCP tool wrapper can call a server tool. | Security policy enforcement, typed call provenance, redacted transcript handoff, and result handling remain. |
| WS-06 memory | Generic memory context machinery exists. | MCP-specific retrieval-floor enforcement and opt-in, sanitized ingestion remain. |
| WS-07 operations | General telemetry/diagnostic infrastructure exists. | MCP-scoped health, sanitized diagnostics, and telemetry remain. |
| WS-08 documentation | Package README describes direct use. | Canonical runtime/Chat setup, security, limits, and failure guides remain. |
| WS-09 external include | None claimed. | Optional and deferred; reject `config_file` until separately approved. |

The labels above are source-based status, not an independent validation
verdict. Do not mark a workstream complete merely because adjacent primitives
exist.

## Focused Evidence And Limits

- At audit start, branch `feature/friday-chat-client-lifecycle` was at
  `1e579cc` with unrelated dirty paths. No MCP package source or tests were
  locally modified; the planning edits from this rebaseline are separate.
- `uv run pytest packages/friday-mcp/tests_mcp -q`: **31 passed**. These tests
  cover config, protocols, and adapters; they do not establish live client,
  manager, transport, server-mode, or cross-package integration quality.
- Focused runtime config and DI tests: **2 passed**, including the test that
  expects MCP provider loading to be rejected.
- Source search found no planned WS-00 DTO names in `packages/`, and no MCP
  client references in Friday Chat, memory, or transcript source. This is a
  current-checkout observation, not a claim about external branches/releases.
- `MCPConfig.model_validate({"unexpected": 1})` currently succeeds while
  dropping the key. WS-01 must close this silent-configuration gap.

No live MCP server interoperability, remote transport, server exposure,
package-wide type check, end-to-end Chat call, or independent acceptance test
was performed for this rebaseline.

## Corrected First Slice And Ownership

`MCP-WS-00` remains a **contracts/defaults-only** candidate in `friday-core`
and `friday-mcp`, with tests in those packages. It may define cross-package
DTOs, metadata strategy, conservative limits, deterministic naming, and
security policy. It must not connect servers, load runtime providers, register
tools, alter Friday Chat/memory/transcript/telemetry, or change CLI behavior.
The existing manager, transports, adapters, and server code are inputs to
compatibility analysis, not code to rewrite in WS-00.

The broader build plan's old Phase 0 mixed decisions with later behavior.
Reassign its pieces explicitly:

- WS-00: contract ownership and shapes; policy defaults; naming and collision
  contract; schema/result limit values; minimum memory-floor value; argument
  redaction/hash and SSE trust decisions; touched-file typing debt.
- WS-01: strict `tools.providers.mcp` parsing, required-server fields,
  `config_file` rejection, unknown keys, and direct-run Chat config mapping.
- WS-02/03: enforce connection, discovery, concurrency, tool count, schema,
  naming, filtering, and registry contracts.
- WS-04/06: enforce token-budget ordering and memory floor in real turns;
  audit Chat command surfaces before promising behavior.
- WS-05/07: enforce redaction and provenance at execution, persistence,
  telemetry, and diagnostics boundaries.
- WS-08: publish behavior actually demonstrated by preceding workstreams.

## Decisions Required Before Code Generation

The maintainer must explicitly approve a bounded WS-00 directive after this
rebaseline and record `approved` then `started` on a dedicated branch per
repository policy. The following are recommendations for that approval, not
decisions silently made by this audit:

1. **First integrated transport posture:** stdio-only by default; existing
   programmatic SSE APIs remain untouched. If SSE is wanted in the integrated
   first pass, define explicit remote trust and secret-handling conditions.
2. **Argument hashes:** no raw argument persistence and no unsalted hash. If
   correlation hashes are required, use a keyed digest with an explicit
   runtime secret and fail closed when unavailable; otherwise omit hashes.
3. **Limit values:** confirm numeric defaults against at least a small and a
   large configured context profile, including a concrete minimum retrieval
   floor. The build plan's numbers are still provisional.
4. **Delivery baseline:** choose the new MCP feature branch and base commit.
   The current branch contains accepted but local-only work and is 19 commits
   ahead of local `master`; delivery/merge is a separate maintainer decision.

Until those choices and the board transition are recorded, `friday-mcp`
remains queued with implementation authority not granted. Rebaselining does
not itself authorize WS-00 code or retroactively validate the standalone
package.
