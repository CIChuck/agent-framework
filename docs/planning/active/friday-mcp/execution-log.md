# Friday MCP WS-00 Execution Log

## 2026-09-27 — Approval And Start

- Maintainer explicitly approved the [rebaselined](rebaseline-2026-09-27.md)
  WS-00 contracts/defaults-only scope and directed continuation.
- Security decisions: first integrated runtime pass is stdio-only; existing
  programmatic SSE remains untouched. Raw arguments and argument hashes are
  not stored by default. Optional keyed hashing requires a later explicit
  policy and implementation decision.
- Baseline commit: `20c70dd` (`Rebaseline Friday MCP integration plan`).
- Dedicated branch: `feature/friday-mcp-ws00-contracts`.
- Board transitions: `queued -> approved` by repository maintainer, then
  `approved -> started` by Codex after branch creation.
- Execution phase: `implementation`; validation state: `not_ready`.
- Authorized source and test packages: `friday-core` and `friday-mcp` only.
  No runtime, Friday Chat, memory, transcript, telemetry, registry, or CLI
  behavior change is authorized in this work unit.
- Baseline checks: MCP package tests 31 passed; two focused runtime tests
  passed, including the deliberate unimplemented-provider rejection.
- Unrelated dirty paths present at start and excluded from staging:
  `.DS_Store`, deleted `family-tree.md`, `docker-bench-security/`,
  `packages/friday-chat/config.example.yaml.pre-typed-llm-20260828.bak`, and
  `packages/friday-sandbox/docker/Dockerfile.audit`.

## 2026-09-27 — Contract Design Decisions

- `friday_core.mcp` owns strict, frozen, typed framework-facing DTOs. The
  existing `friday_mcp.config` models remain protocol-local and unchanged;
  `friday-mcp` depends on core, not the reverse. No import cycle is introduced.
- Provider metadata uses a separate read-only index keyed by canonical tool
  name. `ToolDefinition` and the native tool registry are unchanged in WS-00;
  WS-03 must attach and enforce this sidecar at registration, including
  collisions with native tool names.
- Names normalize to lowercase ASCII with underscores, defaulting to
  `mcp_<server>_<tool>` and accepting a normalized configured prefix. Invalid,
  over-64-character, and colliding canonical names fail explicitly; names are
  never silently truncated.
- Initial limits: 8 servers; 25 tools/server; 50 total tools; 8192 schema
  bytes/tool; 4000 aggregate selected schema tokens; 65536 result bytes;
  2048 reserved tool-result tokens; 4096 minimum memory-retrieval tokens;
  4 parallel server connects and 4 parallel tool calls; 30-second connection
  and 60-second tool timeouts. These are contract defaults, not yet enforced.
  They leave input capacity under the configured 50k, 250k, and 1m budget
  scenarios after the example 2500-token output reserve; later WS-04/06 must
  enforce actual provider/model limits and memory-floor fallback.
- First-pass security contracts reject integrated SSE, implicit stdio commands,
  unredacted environment/headers/arguments, raw-result storage, and stored
  argument hashes. Long-term memory ingestion is disabled by default and
  always requires sanitized content if later enabled. No execution, storage,
  or telemetry behavior changes in WS-00.
- New source has no broad mypy suppression. Legacy suppressions in untouched
  `friday-mcp` files remain historical debt for later slices that touch them.

## 2026-09-27 — Implementation And Local Validation

- Added `friday_core.mcp` typed policy, metadata, provenance, state, diagnostic,
  and naming contracts; added focused core and MCP import/compatibility tests.
- Existing `friday_mcp` client/server implementation, runtime loader, Friday
  Chat, memory, transcript, telemetry, and CLI source remain unchanged.
- Core, MCP, and runtime package tests: **226 passed**. Focused Ruff for core
  and MCP: **passed**. New MCP contract module mypy: **passed**. Runtime/agent
  import smoke: **passed** (LiteLLM used its local cost-map backup because
  network access was unavailable).
- The directive's package-wide mypy command fails before checking project
  code because the environment's NumPy stub uses Python 3.12 syntax while
  root mypy config targets Python 3.10. Rerunning with `--python-version 3.13`
  reaches four existing `no-any-return` errors in untouched
  `friday_core.profiles.py`. The new module passes its focused type check.
- Broader integration suite: **23 passed, 1 failed**. The failure is
  `test_repository_development_board_is_valid_and_rendered`, whose fixed
  assertion expects `22 tasks`; the board already contained 23 tasks at
  baseline `20c70dd`. The test file is unchanged in this work unit. It is
  out of WS-00's approved file scope and remains a separately reported
  baseline failure, not silently repaired here.
- Board validation and documentation lifecycle checks pass. No live MCP
  server, paid provider, remote SSE endpoint, or external side effect was used.

## 2026-09-27 — Candidate Freeze Preparation

- Execution phase advanced to `validation`; validation state is `pending`.
- The [WS-00 implementation report](execution/WS-00-implementation-report.md)
  records files, decisions, checks, and known baseline failures. The candidate
  commit and exact diff will be pinned in the validation request after the
  scoped source and planning changes are committed.

## 2026-09-27 — Independent VAL-001 Review

- Candidate `e3ae808` was frozen and reviewed against base `20c70dd` by a
  fresh-context, read-only validation subagent. The request was committed as
  `b80770b` without changing reviewed source or tests.
- Verdict: `CHANGES_REQUESTED`, recorded in
  [VAL-001](validation/VAL-001-report.md). F-001 finds incomplete typed
  cross-package metadata/provenance/discovery shapes; F-002 finds insufficient
  collision diagnostic detail. Neither finding authorizes later runtime or
  Friday Chat work.
- Baseline mypy and board-integration failures were distinguished from this
  candidate's changes. No candidate completion or maintainer acceptance is
  claimed.
- Execution phase is `remediation`; validation state is `changes_requested`.
  [REM-001](remediation/REM-001-directive.md) binds F-001 and F-002. A separate
  remediator is required for the architecture finding before a new candidate
  and fresh review.

## 2026-09-27 — REM-001 Delegation Authorized

- The repository maintainer replied "continue" to the explicit request to
  delegate [REM-001](remediation/REM-001-directive.md) to a separate remediator.
- Authorization is limited to F-001/F-002 and the directive's allowed files.
  No runtime integration or later MCP workstream was approved.
- The existing candidate and VAL-001 verdict remain historical. The remediator
  must commit a new candidate for fresh independent review.

## 2026-09-27 — REM-001 Candidate And Fresh Review Gate

- Separate remediator committed candidate
  `b79754f23aeee69ea3618b711c78f2c3e51edb71` from authorization baseline
  `3ad7454954b7a415a99a914ba0197a3a7d88be23`. Only the bounded contract
  module, focused tests, and [REM-001 implementation report](execution/REM-001-implementation-report.md)
  changed.
- Controller reconfirmed 232 core/MCP/runtime tests, Ruff, targeted mypy,
  board validation, and delta diff check. The previously recorded package-wide
  mypy and board-integration baseline failures remain separate.
- Execution phase returns to `validation`; validation state is `pending`.
  VAL-001 is superseded for decision purposes but retained as historical
  evidence. The next independent review must inspect both the REM-001 delta
  and the full WS-00 aggregate candidate before any completion proposal.

## 2026-09-27 — Independent VAL-002 And WS-00 Work-Unit Closeout

- A fresh-context, read-only validator reviewed the pinned REM-001 delta and
  full WS-00 aggregate at candidate `b79754f`; all ten authority hashes
  matched. Both reviews returned `VERIFIED` with no numbered findings. The
  [VAL-002 report](validation/VAL-002-report.md) records exact ranges,
  evidence, baseline failures, and residual risks.
- The [WS-00 closeout](execution/WS-00-closeout.md) records work-unit delivery
  and boundaries. Execution phase is `closeout`; validation state is
  `verified`. No reviewed code, tests, configuration, or authority changed
  after candidate freeze.
- The board initiative remains `started`, not `completed` or `accepted`.
  WS-01 through WS-08 are draft; new product code requires a separately
  approved bounded directive. The next gate is maintainer review and
  explicit approval of WS-01 scope.

## 2026-09-27 — WS-01 Approval And Start

- The maintainer replied "accepted" to the explicit next-gate request for a
  bounded WS-01 strict-configuration directive, after reviewing the WS-00
  independent-verification closeout. This records WS-00 work-unit acceptance
  and WS-01 approval, not completion or acceptance of the wider initiative.
- The approved [WS-01 directive](directives/ws-01-configuration-model-validation.md)
  reconciles the older draft against the current code and WS-00 decisions:
  runtime-facing canonical parsing is separate from protocol-local
  `MCPConfig`; integrated transport is stdio-only; `cwd` is workspace-scoped;
  no connection, registration, Chat turn/alias behavior, or external includes.
- Dedicated branch: `feature/friday-mcp-ws01-config`, based on WS-00 closeout
  commit `ab49ba5`. Execution phase is `implementation`; validation state is
  `not_ready`. Existing unrelated dirty paths remain excluded from staging.
