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

## 2026-09-27 — WS-01 Candidate Preparation

- Added strict runtime-facing MCP config models, workspace-scoped path
  validation, and compatibility for unambiguous protocol-local client config;
  no runtime connection or Chat behavior changed. The
  [implementation report](execution/WS-01-implementation-report.md) records
  the exact contract and test evidence.
- Builder checks: 257 core/MCP/runtime tests passed; affected-package Ruff
  passed; Python 3.13 mypy passed on 37 files. The default mypy NumPy-stub
  syntax failure and the unchanged integration board-count failure remain
  documented baseline issues.
- Execution phase advances to `validation`; validation state is `pending`.
  The scoped candidate must be committed and its exact diff pinned before
  fresh independent validation. No WS-02 authority is inferred.

## 2026-09-27 — WS-01 Candidate Freeze And Review Request

- Candidate `de8db57b565968fa02e429e16a481e00c6a92024` is frozen against
  work-unit base `22a5643943da06043515494e23b3dfe549052c55`.
- [VAL-003](validation/VAL-003-request.yaml) pins the candidate, exact diff,
  ten authority hashes, acceptance criteria, checks, exclusions, and baseline
  failures. The request and this checkpoint are planning-only metadata added
  after the candidate; source, tests, and directive remain unchanged.

## 2026-09-27 — Independent VAL-003 Review

- Fresh-context, read-only [VAL-003](validation/VAL-003-report.md) returned
  `CHANGES_REQUESTED` on candidate `de8db57`; all ten authority hashes
  matched. F-001 finds the inherited but mandatory MCP `mode: selected`
  default unmet. F-002 finds no test proving Friday Chat can consume the
  canonical MCP config without another shape.
- Deterministic core/MCP/runtime tests, Ruff, Python 3.13 mypy, board,
  dashboard, documentation, and diff checks passed. The default-target mypy
  NumPy-stub issue and 22-versus-23-task integration assertion remain separate
  baseline failures, not WS-01 regressions.
- Execution phase is `remediation`; validation state is
  `changes_requested`. [REM-002](remediation/REM-002-directive.md) binds
  F-001/F-002. Because F-002 crosses the Friday Chat package boundary, the
  next gate is maintainer authorization of a separate remediator. No product
  code is edited under this planning checkpoint.

## 2026-09-27 — REM-002 Delegation Authorized

- The repository maintainer explicitly replied "authorized go for rem-002"
  to the request for a separate remediator on the bounded F-001/F-002
  [directive](remediation/REM-002-directive.md).
- Authorization is limited to the directive's files and corrective tests.
  Candidate `de8db57` and VAL-003 remain historical evidence. No WS-02,
  Friday Chat source, or other product behavior is approved.
- The next gate is a committed REM-002 candidate for fresh independent delta
  and complete WS-01 aggregate review. The initiative remains `started` and
  the packet remains in `remediation` / `changes_requested` meanwhile.

## 2026-09-27 — REM-002 Stop Condition: Test Ownership

- The separate remediator stopped before any edit or commit. The required
  F-002 test in `friday-runtime/tests_runtime` would import downstream
  `friday_chat.config`; runtime does not declare Chat, while Chat declares
  runtime and imports `friday_runtime.model_library`. This is the directive's
  explicit undeclared-dependency stop condition.
- F-001 and F-002 remain unresolved; candidate `de8db57` and VAL-003 stand.
  Unrelated dirty files and product source/tests were untouched.
- Recommended narrow decision: allow only the F-002 config-compatibility test
  under `packages/friday-chat/tests_chat/`, with no Chat source or turn
  behavior change. The next gate is maintainer approval of that test-only
  scope adjustment before any remediation resumes.

## 2026-09-27 — REM-002 Test-Location Revision Approved

- The maintainer replied "revise" to the explicit request to move only the
  F-002 config-compatibility test into Friday Chat's downstream test package.
- [REM-002](remediation/REM-002-directive.md) now allows exactly
  `packages/friday-chat/tests_chat/test_mcp_config_compatibility.py`, alongside
  the existing F-001 runtime files and narrow execution reports. No Friday
  Chat source or production dependency change is approved.
- The separate remediator may resume both findings. A new candidate requires
  fresh delta and complete WS-01 aggregate review; no verification or WS-02
  authority is inferred from this scope correction.

## 2026-09-27 — REM-002 Candidate And Fresh Validation Gate

- Separate remediator committed `dd6c65bce0035682bbc688953aff8e2011d9d3b7`
  against authorization revision `84c9841`. The three MCP defaults now use
  `selected`, and the authorized downstream Chat test proves config retention
  through the real YAML loader followed by canonical runtime validation.
  Source, test, and example changes remain inside the revised directive.
- The [REM-002 report](execution/REM-002-implementation-report.md) records
  262 core/MCP/runtime tests and 46 Chat config tests passing. The controller
  reconfirmed the combined 308 tests, affected Ruff, Python 3.13 mypy on 38
  files, and both candidate diff whitespace checks. Known default-mypy and
  board-integration baselines remain separately documented.
- VAL-003 is retained historically and superseded for the current candidate's
  decision. Execution phase is `validation`; validation state is `pending`.
  Fresh delta `de8db57..dd6c65b` and full WS-01 aggregate
  `22a5643..dd6c65b` must both pass before work-unit closeout.

## 2026-09-27 — Independent VAL-004 And WS-01 Work-Unit Closeout

- A fresh-context, read-only validator inspected candidate `dd6c65b` against
  both exact diffs and all twelve pinned authority hashes, matching them at
  start and closeout. Delta and complete WS-01 aggregate both returned
  `VERIFIED`, with no findings. [VAL-004](validation/VAL-004-report.md)
  records independent commands, baselines, and residual risks.
- The [WS-01 closeout](execution/WS-01-closeout.md) records the verified
  configuration-only result. Execution phase is `closeout`; validation state
  is `verified`. Reviewed source/tests/directive stayed frozen; subsequent
  additions are closeout evidence and process metadata only.
- The wider initiative remains `started`, not `completed` or `accepted`.
  WS-01 maintainer acceptance and bounded WS-02 approval are separate next
  decisions. Runtime loading/connection and later workstreams remain
  unapproved, and delivery remains local.

## 2026-09-27 — Maintainer Accepted WS-01 Work Unit

- The repository maintainer explicitly said "accept ws-01" after the
  independently verified work-unit closeout. The
  [WS-01 closeout](execution/WS-01-closeout.md) records the accepting
  maintainer, date, candidate, validation, and conversation evidence.
- This acceptance applies only to WS-01. The wider `friday-mcp` initiative
  remains `started`; its packet stays active and delivery stays local.
  No initiative-level acceptance, archive move, or delivery event is implied.
- The next gate is explicit approval of bounded WS-02 runtime lifecycle
  scope. Its directive remains Draft; no WS-02 product code is authorized.

## 2026-09-27 — Maintainer Approved WS-02; Readiness Scope Stop

- The repository maintainer explicitly said "ws-02 approved". This approves
  the existing bounded runtime lifecycle directive, not later workstreams,
  delivery, live-provider effects, or new source files outside that directive.
- Created `feature/friday-mcp-ws02-lifecycle` from accepted WS-01 checkpoint
  `a64e423cffca6162c43b8cfa193792508cf87fd6`. The initiative remains
  `started` and delivery remains local.
- Readiness inspection found that `MCPClientBase.disconnect()` returns
  without cleanup after a failed handshake. An in-process fake-transport
  probe reproduced a still-connected transport, zero disconnect calls, and
  a retained receiver task; the probe then explicitly cleaned up its fake
  resources. No external service or subprocess was used.
- The stdio transport also logs raw command arguments and server stderr.
  The original directive allows manager/adapter changes but not the two
  modules owning these behaviors. Accessing their private state from runtime
  or manager would violate the public package-boundary policy.
- Product code generation stopped before any source or test edit under the
  directive's partial-startup-cleanup stop condition. The
  [readiness checkpoint](execution/WS-02-readiness-checkpoint.md) proposes a
  bounded amendment for `client/base.py` and `client/stdio.py` plus related
  regression tests. The amendment awaits maintainer approval.
- Execution phase is `planning`; validation state is `not_ready` for WS-02.
  Existing WS-00/01 validation and acceptance remain intact. Unrelated dirty
  paths were preserved; no candidate or independent WS-02 verdict exists.

## 2026-09-27 — WS-02 Cleanup Amendment Approved; Implementation Resumed

- After the two-file amendment request and explanation, the maintainer said
  "continue next steps". This approves the proposed narrow cleanup/redaction
  changes in MCP `client/base.py` and `client/stdio.py`, with related tests.
- The directive and tactical plan now explicitly defer registry insertion,
  canonical naming/collisions, final filters, and prompt-visible schema
  sanitization to WS-03. WS-02 preserves a bounded untrusted discovery handoff;
  binding validation still rejects names absent from the real registry.
- Public runtime startup signatures remain unchanged. Local fake servers only;
  no paid/provider/remote effects or delivery operation is authorized.
- Execution phase is `implementation`; validation state is `not_ready` until
  a stable candidate is committed. Fresh-context independent validation is
  required before any WS-02 completion or acceptance proposal.

## 2026-09-27 — WS-02 Lifecycle Candidate Prepared

- Implemented the amended [WS-02 directive](directives/ws-02-runtime-lifecycle-provider-loading.md)
  on `feature/friday-mcp-ws02-lifecycle` against authorization `5c31f7c`.
  The [implementation report](execution/WS-02-implementation-report.md)
  records explicit runtime ownership, bounded startup/discovery, typed safe
  diagnostics, cleanup, and the untrusted WS-03 handoff. No MCP registry entry
  or agent/Chat execution integration is claimed.
- Core/MCP/runtime plus local fake-server integration: **316 passed**;
  existing Chat config compatibility/migration tests: **46 passed**. Affected
  Ruff passed. Python 3.13 mypy passed on 42 files, including the three
  touched MCP source modules whose broad ignores were removed.
- Final broad integration recheck: **38 passed, 1 known baseline failure**
  for the unchanged 22-versus-23-task board assertion. Default-target mypy
  still stops on installed NumPy's Python 3.12+ type-statement syntax; the
  repository targets 3.10. Neither unrelated issue was modified or hidden.
- Board validation passed with 23 tasks, dashboard check passed,
  documentation lifecycle passed with 328 Markdown files, and diff whitespace
  passed. All scoped source/tests will be committed as a stable candidate;
  unrelated worktree paths remain excluded from staging.
- Execution phase is `validation`; validation state is `pending` until a
  fresh-context read-only validator reviews the frozen candidate and exact
  authority. Initiative remains `started`; delivery remains local.

## 2026-09-27 — WS-02 Candidate Frozen And Independent Review Requested

- Stable candidate `5a2856dea0f57208906fbd6eae5419d716bbf55a` is frozen
  against authorization `5c31f7c19f93d8b461dd90936e459ba9e28a4a5d` and
  accepted predecessor `a64e423cffca6162c43b8cfa193792508cf87fd6`.
- [VAL-005](validation/VAL-005-request.yaml) pins thirteen authority hashes,
  both exact diffs, acceptance criteria, checks, exclusions, and known
  baselines. The fresh-context validator operates read-only against that
  candidate. Request/process metadata do not change reviewed source/tests or
  controlling authority; no completion or acceptance is implied.

## 2026-09-27 — Fresh VAL-005 Dispatched

- Dispatched `/root/mcp_ws02_val005` with `fork_turns: none` under the
  repository's mandatory independent-review rule. It receives only the
  pinned request and repository authority, not builder session reasoning.
- Execution phase remains `validation`; validation state is `in_review`.
  Source/tests and thirteen pinned authority documents remain frozen at the
  candidate. Only process metadata changes after freeze.

## 2026-09-27 — Independent VAL-005 Changes Requested; REM-003 Gate

- Fresh-context read-only [VAL-005](validation/VAL-005-report.md) returned
  `CHANGES_REQUESTED` against candidate `5a2856d` and both exact diffs. All
  thirteen authority hashes matched at start and closeout; governed source,
  tests, configuration, and authority remained frozen.
- The reviewer independently confirmed 316 affected package/local-stdio tests,
  46 Chat config tests, Ruff, Python 3.13 mypy on 42 files, board/dashboard/docs,
  and diff checks. Broad integration was 38 passed with the one declared board
  baseline failure; default mypy reproduced the declared NumPy syntax baseline.
- High F-001 reproduces discarded ownership after a failed cleanup followed
  by startup retry, at both provider-manager and DI-provider layers. Once cleanup
  was allowed, public kernel shutdown reached only the replacement owner, not
  the first retained client. The reviewer explicitly cleaned every probe
  resource. This is a candidate defect, separate from the two baseline issues.
- [REM-003](remediation/REM-003-directive.md) bounds the single finding, allowed
  runtime files, regression/acceptance criteria, checks, and stop conditions.
  It remains Draft. A separate remediator is required for lifecycle ownership
  and resource integrity; the next gate is explicit maintainer authorization.
- Execution phase is `remediation`; validation state is `changes_requested`.
  No corrective product edits or new delegation occurred. Initiative remains
  `started`, not completed/accepted; WS-03 and delivery remain separate gates.

## 2026-09-27 — Separate REM-003 Remediator Authorized

- The maintainer replied "proceed" to the explicit request to authorize the
  separate [REM-003 pass](remediation/REM-003-directive.md). This approves
  only F-001's retained-owner correction, the directive's allowed files and
  tests, and separate remediation followed by fresh independent validation.
- The remediator may commit a stable scoped correction on
  `feature/friday-mcp-ws02-lifecycle`. Failed candidate `5a2856d` and
  VAL-005 remain historical evidence; no passing verdict is inferred.
- Execution phase remains `remediation`; validation state remains
  `changes_requested`. Next gate is a committed candidate for fresh delta and
  complete WS-02 aggregate review. Initiative remains `started` and local;
  no WS-03, external-service, or delivery authority is granted.

## 2026-09-27 — REM-003 Candidate Frozen; Fresh VAL-006 Requested

- Separate remediator `/root/mcp_ws02_rem003` committed
  `26f4d7d4bfd0514b6eb76bed71cb4797da91a067` against authorization
  `0ab969275561b1c239d54c786074fdc8e900766c`, changing only the three
  allowed runtime source/test files and two implementation reports.
- Provider retry completes cleanup before replacing its manager; DI retains
  its provider. Failed/cancelled shutdown clears the handoff while retaining
  ownership. The [REM-003 report](execution/REM-003-implementation-report.md)
  records five new regression cases, 32 focused tests, 321 affected package/
  local-stdio tests, 46 Chat configuration tests, Ruff, Python 3.13 mypy,
  board/dashboard/docs, and whitespace checks. Declared NumPy typing and
  board-count integration baselines remain separate and unchanged.
- Controller confirmed the exact five-path bounded diff, governed working
  files match the commit, and unrelated dirty paths remain excluded.
  VAL-005 is retained with only a superseded decision-status note.
- [VAL-006](validation/VAL-006-request.yaml) freezes REM-003 delta and complete
  WS-02 aggregate review against the accepted WS-01 checkpoint. Candidate
  source, tests, configuration, and authority cannot change during review.
  Only disclosed controller process metadata may follow candidate freeze.
- Execution phase is `validation`; validation state is `pending` until fresh
  reviewer dispatch. Initiative remains `started` and local. No successful
  independent verdict, acceptance, WS-03 authority, or delivery is inferred.

## 2026-09-27 — Fresh VAL-006 Dispatched

- Dispatched `/root/mcp_ws02_val006` with `fork_turns: none` under the
  repository's mandatory fresh independent-review rule. Request revision is
  `c137e7b9a6b97c3383ea52c1b5991ec25fbf1c13`; it supplies the fifteen pinned
  authority hashes, exact candidate/diffs, criteria, checks, baselines, and
  exclusions without builder or remediator session reasoning.
- Execution phase remains `validation`; validation state is `in_review`.
  Candidate `26f4d7d` source/tests/config and all pinned authority remain
  frozen; this dispatch changes only the index and append-only execution log.

## 2026-09-27 — VAL-006 Delta Verified; Aggregate Cleanup Changes Requested

- Fresh-context read-only [VAL-006](validation/VAL-006-report.md) verifies
  REM-003's bounded delta at `26f4d7d`: original provider/manager ownership
  remains reachable across failed startup/cleanup retry, successful peers
  drain, public cleanup/recovery succeeds, and diagnostics remain redacted.
  All fifteen authority hashes and governed candidate files matched at start
  and closeout; controller dispatch metadata was the only later difference.
- The complete WS-02 aggregate and overall gate are `CHANGES_REQUESTED`.
  High VAL-006 F-001 uses the real stdio transport and a local synthetic peer
  to reproduce shutdown hanging after forced kill when unread oversized stdout
  prevents pipe closure. The transport's post-kill wait has no bound. Public
  kernel ownership is retained, but shutdown cannot complete without caller
  pipe intervention. Reviewer explicitly cleaned every probe resource.
- The deliberately perpetual synthetic kernel retry-cleanup pause was not
  counted as a separate finding; production direct/public-kernel evidence
  independently establishes F-001. Do not introduce a two-second shutdown SLA
  from that diagnostic observation.
- Independent checks: 32 focused tests, 321 affected package/local-stdio tests,
  46 Chat config tests, Ruff, Python 3.13 mypy on 42 files, board/dashboard/docs,
  and all three exact diff checks passed. Broad integration reproduced 38
  passes and one unchanged board-count baseline; default mypy reproduced the
  unchanged NumPy syntax baseline. Neither baseline is the cleanup finding.
- [Draft REM-004](remediation/REM-004-directive.md) covers F-001 exactly once,
  proposing only stdio source, three existing local test/fixture files, and
  two implementation reports. Separate remediator authorization is required;
  REM-003 explicitly excludes MCP source. No product fix or new remediation
  dispatch occurred. If the proposed second WS-02 correction cycle fails,
  return unresolved findings to the maintainer rather than automatically loop.
- Execution phase is `remediation`; validation state is `changes_requested`.
  Next gate is explicit maintainer authorization of REM-004 and its separate
  remediator. Initiative remains `started`, delivery local; no WS-02 acceptance,
  WS-03 authority, live effect, or delivery operation is implied.

## 2026-09-28 — REM-004 Approved; Ordered Task Queue Recorded

- The maintainer replied "aproved... make a list of next steps in our task
  queue" to the REM-004 authorization request. This explicitly approves the
  bounded [REM-004 directive](remediation/REM-004-directive.md) and separate
  remediator, including its exact files, regressions, checks, and fresh review.
  It does not accept WS-02 or approve WS-03/later workstreams or delivery.
- Added the [ordered task queue](task-queue.md): separate REM-004 dispatch;
  fix/regressions/checks and stable candidate; fresh VAL-007 delta plus full
  WS-02 aggregate; verified closeout and explicit WS-02 acceptance; then draft
  WS-03 readiness/approval and the existing later workstream sequence.
- The queue distinguishes approved, dependency-gated, unapproved, and deferred
  steps. Runtime skills remains in its separate backlog; existing board
  initiative priorities and count are unchanged. If the second WS-02 correction
  cycle fails, return unresolved findings to the maintainer under policy.
- This turn is planning/approval recording only: no REM-004 remediator was
  dispatched, no product source or tests changed, and no fresh candidate or
  verdict was claimed. Unrelated dirty work remains preserved.
- Execution phase remains `remediation`; validation state remains
  `changes_requested`. Next gate is dispatch of the authorized separate
  remediator and a committed scoped candidate. Initiative remains `started`
  and local; prior candidate `26f4d7d` and VAL-006 remain historical evidence.

## 2026-09-28 — REM-004 Execution Requested; Agent Dispatch Capacity Stop

- The maintainer said "proceed" after the read-only readiness audit, instructing
  execution of the already-approved REM-004 pass, not WS-03 or later work.
- Verified branch `feature/friday-mcp-ws02-lifecycle`, HEAD
  `cdd808ed653f2f5fe4ccc4a695782d97c39c2ce8`, board validation with 23 tasks,
  current task `started` with granted authority, approved REM-004, queue, and
  unchanged unrelated dirty manifest before attempting dispatch.
- `collaboration.spawn_agent` for fresh `/root/mcp_ws02_rem004`, with
  `fork_turns: none` and the exact six-path directive, returned
  `agent thread limit reached`. No agent was created. The live registry lists
  root plus completed WS-01/WS-02 validator contexts only; a readiness-only
  `followup_task` to prior `/root/mcp_ws02_rem003` returned the same capacity
  error. No prior remediator resumed and no product edit was delegated.
- Inspected available operations: no supported thread close/reset operation
  is exposed. Interrupt does not remove an agent thread. An existing reviewer
  context cannot be relabeled as the mandated fresh validator; no self-repair
  or freshness waiver was inferred. Separately checking whether an existing
  agent can be reassigned to remediation without validating its own candidate.
- `git diff --exit-code cdd808e -- packages tests pyproject.toml uv.lock`
  passed. No source/test/config/dependency changes, subprocess probe, candidate,
  fresh review, acceptance, or delivery operation occurred. All unrelated
  dirty paths remain preserved and excluded from staging.
- REM-004 remains approved. Execution phase remains `remediation`; validation
  state remains `changes_requested` for the existing WS-02 defect. The process
  stopped at dispatch, before implementation. Next gate is an execution
  session with available capacity for the separate remediator and fresh
  validator; resume from the approved directive/queue without new scope
  approval. Initiative remains `started` and local; later gates are unchanged.

## 2026-09-28 — Existing Separate Remediator Available; Bounded Recovery

- A readiness-only followup to existing `/root/mcp_ws01_val004` succeeded.
  That agent independently reread the approved REM-004 and role policy,
  confirmed branch/board/authority alignment and 23-task board validation,
  and reported no source edits, staging, commits, spawning, or implementation.
- It previously reviewed accepted WS-01; it was not the WS-02 builder, REM-003
  remediator, or VAL-006 reviewer. Repository policy permits reassignment to
  separate remediation, but it must not validate its resulting candidate.
  This is not a fresh reviewer context and no such claim will be made.
- Prepare that existing thread for the approved REM-004 execution instruction.
  This avoids a new remediator thread; fresh VAL-007 creation must still be
  attempted after a stable candidate. If thread capacity remains unavailable,
  stop at independent-review dispatch and hand off the exact frozen candidate,
  manifest, and checks to a session with fresh-agent capacity.
- Execution phase remains `remediation`; validation state remains
  `changes_requested`. Next gate is the approved scoped correction and stable
  candidate. No scope, review-freshness, acceptance, or delivery waiver is given.

## 2026-09-28 — Reassigned Separate REM-004 Remediator Dispatched

- Following readiness confirmation, sent `/root/mcp_ws01_val004` the bounded
  REM-004 execution instruction against approved revision `cdd808e` and
  execution baseline `bd10656fed43083ff1d81ef2232205b50f58ac99`.
  The agent is reassigned to remediation only; its historical WS-01 review
  remains historical and it must not review its new code. No claim of fresh
  remediator context is made or required; fresh independent VAL-007 is required.
- Instruction binds the exact six allowed files, all six criteria, checks,
  local-only fake peers, explicit fixture cleanup, typing/redaction/ownership
  constraints, scoped local commit, and scope stop conditions. Controller
  owns these process metadata; source and approved authority are untouched.
- Queue tasks 1–2 are in progress. Execution phase remains `remediation`;
  validation state remains `changes_requested` until candidate freeze and a
  fresh review request. Later workstreams, acceptance, and delivery are gated.

## 2026-09-28 — REM-004 Frozen Candidate And VAL-007 Request

- Separate remediator `/root/mcp_ws01_val004` delivered final frozen candidate
  `a257f041d1d68f8aea2f5b9773df1b88acd82379` against correction base
  `097bbd9eced5e5ba2ffcc97fbe60273285bf605e`. Its provisional local commit
  `eb960785` was amended before freeze to strengthen assertion-failure fixture
  cleanup. It will not independently review its own remediation.
- Exactly six authorized source/test/report paths changed. Source correction
  is confined to MCP stdio transport: owned shielded cleanup, single-reader
  handoff, 4096-byte stdout/stderr discard, bounded graceful/forced process
  waits and task settlement, static incomplete-cleanup error and retryable
  retained ownership. Public signatures, configuration, runtime/DI/provider
  source and accepted predecessor contracts are unchanged.
- The [REM-004 report](execution/REM-004-implementation-report.md) records
  before-fix direct reproduction, real direct/public-kernel noisy-peer cleanup,
  required/optional partial-start variants, finite 11-second asynchronous
  attempt budget, cancellation/retry limits and explicit synthetic teardown.
- Final remediator checks: 39 focused lifecycle, 333 Core/MCP/runtime aggregate,
  32 loading and 46 Chat tests passed. Broad integration: 44 passed and only
  the declared board-count baseline failed. Ruff and prescribed Python 3.13
  mypy passed (42 files); default mypy reproduced only installed NumPy syntax
  baseline. Board validate (23)/render, docs (335) and diff checks passed.
- Controller checked exact bounded path manifest, product worktree/candidate
  match, no runtime/core/Chat/dependency correction, authority hashes and
  unchanged unrelated dirty manifest. Implementation checks are not a formal
  independent verdict. Controller reran the focused direct/public-kernel suite:
  39 passed in 40.98s. Board validate/render and docs lifecycle also passed
  after request/process metadata preparation.
- Historical VAL-006 retains its complete verdict/findings, with only a
  superseded decision-status note added. [VAL-007](validation/VAL-007-request.yaml)
  pins eighteen authority documents, the exact candidate/delta/correction/full
  WS-02 aggregate ranges, every criterion and required command, baseline and
  local-only validation boundaries. Full branch/merge review remains later.
- Queue tasks 1–2 are complete as implementation steps. Execution phase is
  `validation`; validation state is `pending`. Next gate is fresh read-only
  VAL-007 dispatch and complete review. New-agent capacity must be checked;
  no current context may be relabeled fresh. No WS-02 acceptance, later-slice
  implementation, push, merge, release or external effect is authorized here.

## 2026-09-28 — Fresh VAL-007 Successfully Dispatched

- Following the final remediator completion, fresh agent creation succeeded:
  `/root/mcp_ws02_val007`, `fork_turns: none`. The earlier thread-capacity stop
  is historical and has not been waived by reusing a reviewer context.
- The reviewer received only the repository-visible pinned request, exact
  candidate/ranges/authority requirements, read-only/local-only constraints,
  explicit probe cleanup and reporting contract; no builder private reasoning
  or conclusions. It may not remediate or accept its candidate.
- The request-adding commit is `201f4d1`; full revision must be resolved by the
  reviewer. Candidate remains `a257f041d1d68f8aea2f5b9773df1b88acd82379`.
  This dispatch update affects only board/dashboard/index/queue/log metadata,
  not request, authority hashes, product source/tests/config or findings.
- Execution phase `validation`, validation state `in_review`; board next gate
  is receipt of delta and complete WS-02 aggregate verdict. No outcome,
  acceptance, later-workstream approval or delivery is inferred.

## 2026-09-28 — VAL-007 Verified; WS-02 Closeout Awaiting Acceptance

- Fresh read-only `/root/mcp_ws02_val007` returned REM-004 delta `VERIFIED`,
  complete WS-02 aggregate `VERIFIED`, and overall `VERIFIED`, with no findings.
  Its full [report](validation/VAL-007-report.md) is preserved without substantive
  changes; only trailing Markdown whitespace was normalized.
- Reviewed candidate `a257f041d1d68f8aea2f5b9773df1b88acd82379`, request
  `201f4d19de5ce2d007a5f6a33ef750db6c2a0376`, and disclosed dispatch metadata
  `a4b71d09be731a919b13350c2148b4d2af2b7b56`. All eighteen pinned authority
  documents and full candidate product bytes matched at start/closeout.
- Independent checks reproduced 39 focused, 32 loading, 333 aggregate and
  46 Chat passes; broad integration 44 passes plus only declared board-count
  baseline. Ruff, prescribed Python 3.13 typing (42 files), board/dashboard,
  docs (335), exact diff checks and product stability passed. Default typing
  reproduced only installed NumPy baseline. No required check was skipped.
- Independently constructed production peers verified direct and public kernel
  noisy-child teardown, canceled stop/public retry, and optional/required
  noisy handshake/list failures, typically around five seconds with existing
  graceful policy. Assertions confirmed reaped children, pipe EOF, closed stdin,
  no owned tasks, empty public manager/handoff and redaction before defensive
  cleanup. Independent retained-owner/retry doubles and all eight provider/
  kernel ownership variants passed. Deliberate scratch assertion failure proved
  fixture cleanup; this is not a product regression.
- Controller reviewed completeness against all six REM-004 criteria, eight
  WS-02 criteria, amendment/REM-003 regression controls and required checks.
  No unresolved mandatory finding remains. [WS-02 closeout](execution/WS-02-closeout.md)
  records the verified candidate, capability/non-goal boundaries and residual
  cooperative-budget/process-tree/cwd/live-interoperability limits.
- This closeout adds evidence/process metadata only. No candidate product,
  configuration or authority was changed after review; unrelated dirty work
  remains preserved. Queue tasks 1–3 are complete; task 4 awaits explicit
  maintainer WS-02 acceptance. Execution phase `closeout`, validation state
  `verified`; board next gate is that acceptance. Wider initiative remains
  `started` and local. WS-03 and later require separate approvals; no delivery
  or external-effect authority follows from validation.
- Controller post-report/closeout checks passed: board validation (23), rendered
  dashboard, documentation lifecycle (337 Markdown files), diff whitespace and
  frozen product/configuration comparison. Request and all three independent
  scratch-probe hashes match the returned report.

## 2026-09-28 — Maintainer Explicitly Accepted WS-02

- The maintainer said "WS-02 accepted" in the active conversation after the
  verified closeout and next-gate review. Record that deliberate decision,
  rather than inferring acceptance from VAL-007's verdict.
- Acceptance applies only to MCP-WS-02 candidate
  `a257f041d1d68f8aea2f5b9773df1b88acd82379`, independently verified by
  fresh VAL-007 delta and complete WS-02 aggregate review. The
  [WS-02 closeout](execution/WS-02-closeout.md) records accepting maintainer,
  date and exact conversation evidence. Historical reviewer evidence and
  candidate source/tests/configuration are unchanged.
- Queue tasks 1–4 are complete. Next gate is reconciliation of the draft
  WS-03 directive against the accepted discovery handoff, current contracts
  and registry, then an explicit bounded maintainer approval request. This
  acceptance-recording turn performs no WS-03 reconciliation or product work.
- Index fields now describe next-slice preparation: execution phase `planning`,
  validation state `not_ready`. Accepted WS-00/01/02 results remain intact;
  the current fields do not downgrade them or grant new implementation scope.
- Wider initiative remains `started`, condition `normal`, delivery `local`,
  on `feature/friday-mcp-ws02-lifecycle`. No entire-packet acceptance/archive,
  branch change, push, merge, release, live/provider use or external effect is
  authorized or performed. Preserve the unrelated manifest: modified
  `.DS_Store`; deleted `family-tree.md`; untracked `docker-bench-security/`,
  `packages/friday-chat/config.example.yaml.pre-typed-llm-20260828.bak` and
  `packages/friday-sandbox/docker/Dockerfile.audit`. Stage only scoped
  acceptance/process metadata.
- Acceptance metadata checks passed: board validation (23 tasks), rendered
  dashboard, documentation lifecycle (337 Markdown files), diff whitespace and
  full frozen product/configuration comparison. No product checks were rerun
  because this turn changes only acceptance/process records, not behavior.

## 2026-09-28 — WS-03 Directive Reconciled; Approval Requested

- Maintainer said "continue" after WS-02 acceptance. Current board next gate
  is WS-03 directive/readiness preparation, not code generation. Verified
  branch `feature/friday-mcp-ws02-lifecycle`, base
  `56251144345888f721c9fc9235ad8a54bbbb23db`, started/granted predecessor
  authority, local delivery and unchanged unrelated dirty manifest.
- Read policies, build/tactical authority, accepted predecessor evidence and
  actual contract/config/provider/adapter/native registry implementation.
  [WS-03 readiness checkpoint](execution/WS-03-readiness-checkpoint.md) records
  concrete probes, scope discrepancies, commands/results and residual limits.
- Reconciled only the draft [WS-03 directive](directives/ws-03-tool-naming-metadata-registry.md),
  not approved predecessor authority. Proposed scope is seven source paths,
  nine exact test/fixture paths and one implementation report. Missing runtime
  tools.py and broad native source/protocol edits are removed. No manager,
  transport, dependency/config schema or native registry source edits proposed.
- Decisions for approval: reuse immutable untrusted discovery handoff without
  rediscovery/backfill; accepted canonical normalizer and typed sidecar; additive
  metadata completeness; category mcp and exact filters; fatal explicit missing
  includes; collision preflight and owned rollback; bounded inline-schema
  sanitation and final exported-definition byte/cost checks; guarded publication
  before binding validation and public shutdown/retry ownership. Preserve
  existing trusted-caller mutable native schema semantics, documenting their
  boundary rather than promising whole-registry immutability.
- Read-only baseline: 88 compatibility tests passed, Ruff passed, existing
  runtime/MCP Python 3.13 typing passed on 42 files. Unfiltered core checks
  reproduce exactly four historical profiles.py errors; default mypy reproduces
  NumPy syntax baseline. Supplemental import-silent core check is advisory only.
  First test command referenced a nonexistent legacy target and ran no tests;
  corrected actual targets passed. No future/new WS-03 test or broad integration
  completion is inferred from preparation. Full details remain in checkpoint.
- No product source/test/config changes, implementation branch, subagent,
  candidate, review request/verdict, credentials/live calls or delivery action.
  Accepted candidate comparison passed. Preserved unrelated five-path manifest
  is unchanged; only seven explicit planning files will be staged.
- Queue task 5 reconciliation is complete, awaiting explicit approval of the
  full revised directive. Board/index next gate is that approval. Execution
  phase `planning`, validation state `not_ready`; wider initiative remains
  `started`, normal and local. Future fresh VAL-008 is reserved only, not
  dispatched or verified. No approval or later-slice scope is inferred.
- Planning closeout checks passed: board validation (23 tasks), generated
  dashboard freshness, documentation lifecycle (338 Markdown files), diff
  whitespace and frozen source/test/config comparison to accepted WS-02.
  No accepted authority, historical validation or closeout changed.

## 2026-09-28 — WS-03 Explicitly Approved And Started

- Maintainer evidence: "ws-03 approved" in the active conversation. This grants
  the full reconciled WS-03 directive, not later workstreams or delivery.
- Created local branch `feature/friday-mcp-ws03-registry` from frozen work-unit
  base `2c0d6bd1fe481fff9bb180f9e6dfb4a9a2131641`. That checkpoint stacks on
  accepted WS-02 product candidate `a257f041d1d68f8aea2f5b9773df1b88acd82379`.
  Approval/start records precede product edits; board branch and packet agree.
- Queue task 5 is complete, task 6 implementation is in progress. Initiative
  remains started/granted/normal/local, current phase implementation and
  validation not_ready. Stable candidate and fresh read-only VAL-008 are next;
  no review request, dispatch, verdict, or WS-03 acceptance exists yet.
- Exact approved boundary is seven source paths, nine tests/fixtures and one
  implementation report. Main controller builds; mandatory fresh validator
  will not receive builder private reasoning. No native registry, transport,
  manager, security package, dependency or config schema changes authorized.
- Preserve unrelated modified `.DS_Store`, deleted `family-tree.md`, untracked
  `docker-bench-security/`, Friday Chat config backup and sandbox Dockerfile
  audit. Explicit scoped staging only; no cleanup or external actions.

## 2026-09-28 — WS-03 Stable Candidate And Fresh Review Request

- Main builder committed `397caa9898612cd989f6404951b3e1f5005dfac2` on
  `feature/friday-mcp-ws03-registry`: exactly sixteen approved implementation
  paths, within the seventeen-path allowlist. Seven source paths, eight test/
  fixture paths and [implementation report](execution/WS-03-implementation-report.md).
  WS-02 lifecycle integration tests remain unchanged; no transport/manager,
  native registry/config/security/dependency source edits.
- Approved work-unit base `2c0d6bd1fe481fff9bb180f9e6dfb4a9a2131641`,
  approval/start commit `b54069654bb3e21a6265fbabcd23f6991e286ab0`.
  Implemented canonical naming, full typed adapter, bounded schema sanitation,
  exact filters/strict includes/final export costs, transactional registry
  ownership/metadata/counters, pre-binding publication and owned public cleanup.
- Builder evidence: 146 focused, 430 affected aggregate, 46 Chat compatibility
  pass; full integration 57 pass plus declared board-count baseline. Native
  tools 233 pass / two invalid-zip dependency-only fixture failures, both
  independently reproduced by main on the exact unchanged predecessor archive;
  not repaired or waived. Ruff and meaningful runtime/MCP/integration Python
  3.13 typing pass. Default mypy NumPy syntax and four core profiles.py errors
  are retained as declared baselines, with exact output in the report.
- Board (23 tasks), dashboard, documentation (339 Markdown files), whitespace,
  stable candidate range and frozen source/tests/config comparison pass.
  Unrelated five-path manifest is unchanged; stage only named metadata files.
- [VAL-008 request](validation/VAL-008-request.yaml) pins candidate/base/ranges,
  twenty authority SHA256 hashes, all criteria/required commands, baseline
  reproduction obligations and independent adversarial public-interface probes.
  Request preparation is not reviewer dispatch or verdict. Current phase
  validation/state pending; task 6 remains in progress. Fresh reviewer creation
  is mandatory; no existing context will be relabeled fresh if capacity fails.
- Wider initiative remains started/normal/local; predecessor acceptance intact.
  No WS-03 closeout/acceptance, WS-04 code, full-initiative completion or delivery
  operation is inferred. Frozen product and controlling authority will remain
  unchanged while review proceeds.

## 2026-09-28 — VAL-008 Fresh Dispatch Capacity Stop

- Committed request checkpoint `1070cc2` pins stable candidate
  `397caa9898612cd989f6404951b3e1f5005dfac2` and the complete authority/check
  manifest. Requested `/root/mcp_ws03_val008` with `fork_turns: none`, read-only
  role and the committed request, without builder private conclusions.
- Spawn returned exactly `agent thread limit reached`. No reviewer was created,
  no dispatch occurred and no independent verdict/report exists. Live-agent
  inventory shows completed historical contexts; no supported close/reset
  operation is available. Existing contexts cannot satisfy fresh independence
  and are not reassigned as validators. No repeated futile spawn/reset attempt.
- Stop at the required validation gate. Board condition blocked, initiative
  still started/granted/local; execution phase validation, validation state
  blocked. This workflow blocker is NOT an independent BLOCKED verdict and
  does not downgrade accepted WS-00/01/02 or revoke approved WS-03 scope.
- Resume pinned VAL-008 in a fresh session with agent capacity. No product
  regeneration or redundant implementation approval is needed. Do not proceed
  to closeout/acceptance/WS-04 or delivery without the missing verdict/gates.
- Frozen source/tests/configuration/authority and unrelated five-path manifest
  are preserved. Controller records only capacity/status metadata; candidate
  implementation report and pinned request remain byte-identical.

### Policy-required blocked packet relocation

- Board validation correctly rejected condition blocked with an active packet.
  Relocated exactly the fifty-file MCP packet mechanically to
  `docs/planning/blocked/friday-mcp/` under lifecycle policy and repaired board
  evidence/backlinks. Source/tests/config and twenty authority contents remain
  byte-identical. Historical reports are not substantively amended.
- VAL-008 request gains a controller-only original-pinned to current-working
  prefix mapping. At pinned Git revisions use original active paths; for current
  working-file hashes use blocked paths. This supersedes the preceding request
  byte-identity sentence solely for that disclosed mapping; review scope,
  candidate/base/authority hashes and criteria remain unchanged. No reviewer
  existed or issued a verdict before this relocation.
- Run fresh VAL-008 from the current blocked request, resolving its latest
  request/mapping commit. Do not change product code or declare verification.

## 2026-09-28 — Fresh VAL-008 Completed; Bounded REM-005 Prepared

- Maintainer explicitly requested a new-conversation, fresh-context read-only
  subagent for the frozen blocked VAL-008 request. Created
  `/root/val_008_independent_review` with `fork_turns: none`, no inherited parent
  context or builder conclusions. It read all twenty pinned authorities and
  complete requested diffs, independently executed all fifteen required checks
  and adversarial local probes, and returned overall `CHANGES_REQUESTED`.
- Frozen candidate/authority `397caa9898612cd989f6404951b3e1f5005dfac2`,
  work-unit base `2c0d6bd1fe481fff9bb180f9e6dfb4a9a2131641`, approval/start
  `b54069654bb3e21a6265fbabcd23f6991e286ab0`, request/mapping/working HEAD
  `b8e1f041695b94303517617362f590ef3272e0cc`. Request SHA256 remained
  `43fb708815e569dbe3d8b0a443ec28bf782e5b5ff2db75fb0be5d4dd2d139cfc`.
  All twenty authority hashes and frozen source/tests/config matched at review
  start and closeout. Capacity block is historical; this reviewer encountered
  no independence or infrastructure blocker.
- Sole medium F-001: public runtime collisions omit first-contender identity,
  provider kinds and bounded original-name summaries. Real public kernel
  MCP/MCP and MCP/native probes returned identical one-entry decisions; abort,
  no overwrite, native preservation and cleanup passed. The missing required
  diagnostic contract, not declared baseline debt, drives the result.
- Complete [report](validation/VAL-008-report.md) archived byte-for-byte from
  the independent reviewer, SHA256
  `1bf0b019e0ba69f75eb638e1aa68f89a3d90088e2471dea11ce7ee76c1b46d0c`.
  [Evidence manifest](validation/VAL-008-evidence.yaml) records hashes and
  paths for all required command logs, predecessor logs, independent harness/
  peer, collision reproduction and freeze snapshots. The thirty-three scratch
  evidence artifacts are copied unchanged; the report's original paths remain
  historical and the manifest documents restoration for reproduction.
- Independent evidence: 146 focused, 430 affected aggregate and 46 Chat tests
  passed; Ruff and runtime/MCP/integration Python 3.13 typing passed. Full
  integration 57 passed plus unchanged board-count assertion. Native tools
  233 passed plus two invalid-zip fixture assertions; exact accepted predecessor
  reproduces these and the board mismatch. Default NumPy syntax and four core
  profiles.py errors also reproduce. Failures remain failures, not reviewer
  waivers. Sixteen probe groups passed; F-001's explicit source-diagnostic
  assertion separately failed. Synthetic resources settled in finally with
  successful public cleanup distinguished from defensive fixture cleanup.
- Maintainer subsequently said "Proceed to the next step." Controller records
  the complete result and prepares [REM-005](remediation/REM-005-directive.md)
  for the single finding. Exact proposed scope: two runtime source paths, three
  test paths, one bounded fake fixture, two reports; six acceptance criteria,
  complete required checks and fresh delta/aggregate review. No product fix,
  remediator dispatch, changed candidate or new authority approval is inferred
  from this draft-preparation step. Separate remediator is required for the
  public typed diagnostic/untrusted-content boundary; reviewer will not repair
  or validate its own correction.
- Current execution phase `remediation`, validation state `changes_requested`.
  Initiative remains started/granted/local on the same branch; condition blocked
  now names pending explicit REM-005/separate-remediator approval, not capacity.
  Queue 6a complete, 6b current, 6c–6e unstarted. WS-00/01/02 acceptance intact;
  no WS-03 verification/acceptance, WS-04 approval or delivery is inferred.
- Preserve modified `.DS_Store`, deleted `family-tree.md`, untracked
  `docker-bench-security/`, Friday Chat config backup and sandbox Dockerfile
  audit. Controller start/closeout byte fingerprints independently confirmed
  preservation during review. Only explicit report/evidence/directive/process
  paths are eligible for staging; no broad-stage or cleanup operation.
- Controller closeout checks passed: board validation (23 tasks), dashboard
  freshness, documentation lifecycle (341 Markdown files), whitespace and full
  frozen product/config comparison. All twenty original authority hashes and
  unchanged request match again; all thirty-four archived report/evidence hashes
  match the independent originals. Unrelated five-path byte fingerprints match
  the pre-dispatch controller snapshot. Product tests were not rerun because
  this handoff changes only review evidence, draft planning and process metadata.
- Full staged whitespace checking initially detected generated trailing spaces
  in the native pytest failure log and its predecessor reproduction. Preserve
  those exact original bytes in deterministic lossless `.log.gz` envelopes;
  the evidence manifest records original/decompressed and compressed hashes.
  No reviewer output or finding was edited, normalized or dropped. No source
  or policy waiver is introduced by this evidence packaging.

## 2026-09-28 — REM-005 Explicitly Approved; Separate Execution Authorized

- Maintainer explicitly said "That's approved. Proceed." after the concrete
  complete REM-005 directive and separate-remediator approval request. Record
  this as approval of the single F-001 correction, exact eight paths, six
  criteria, required checks and fresh delta plus full WS-03 aggregate review.
  It does not approve later workstreams or delivery.
- Restore condition normal and the packet to `docs/planning/active/friday-mcp/`
  under lifecycle policy. Repair board/controller evidence paths; preserve
  all historical independent report/request/executable/log/snapshot bytes.
  Historical VAL-008's blocked mapping remains pinned to its reviewed request
  revision. REM-005's approved two report targets map to active without source/
  test scope expansion; new VAL-009 will pin current active authority paths.
- Separate remediator dispatch follows the stable controller approval commit.
  Original builder and VAL-008 reviewer do not implement this correction.
  Remediator owns only the approved product/test/report paths and must not
  validate its own work. Current phase remediation/state changes_requested;
  queue 6b complete, 6c authorized, new candidate/review not yet produced.
- Initiative remains started/granted/local on
  `feature/friday-mcp-ws03-registry`. Preserve the existing five unrelated dirty
  paths and their contents; no cleanup, broad staging, live service, credential,
  provider, push, merge, release or other external effect.
- Approval/relocation checks passed: board (23 tasks), rendered dashboard,
  documentation lifecycle (341 Markdown files), full frozen product/config
  comparison, all twenty original authority hashes and byte-exact historical
  request/report/executable/snapshot evidence, including lossless log hashes.
  Record approval/relocation in a scoped local commit before product edits.

## 2026-09-28 — Separate REM-005 Candidate Frozen; Fresh VAL-009 Requested

- Approval/start checkpoint `215e54de71eda08067d22695d0062f7bed35e9d0`
  recorded explicit maintainer approval and policy-required active relocation.
  Dispatched new separate `/root/mcp_ws03_rem005` with `fork_turns: none`,
  exact approved directive and no inherited builder/reviewer context. It did
  not modify controller/authority paths, inspect sessions or delegate further.
- Separate remediator committed stable candidate
  `d395acdba9e233cb226f54e6258575f480157cf1`: exactly two source, three test,
  one fixture and two report paths, all eight authorized targets. Typed frozen
  both-source diagnostic records distinguish MCP/MCP and MCP/native; static
  errors, ordinary constructors/defaults, counters and existing behavior remain.
  Public collision history survives cleanup and is replaced at a new discovery
  attempt after prior-owner cleanup. Bounded length/shape/fingerprints handle
  long/control/encoded/escaped-surrogate originals without raw peer exposure.
- [REM-005 report](execution/REM-005-implementation-report.md) documents public
  contract/compatibility/lifetime/counters, before/after evidence, all six
  criteria, final fourteen exact commands/exits/times, baseline reproductions,
  initial harness/setup corrections and explicit synthetic-resource settlement.
  Final 173 focused, 459 affected aggregate and 46 Chat tests pass; integration
  69 plus known board failure; native 233 plus known two invalid-zip failures.
  Required Ruff and affected 45-file typing pass; default NumPy and four core
  profiles.py errors remain unchanged. No repair or waiver of baseline debt.
- Controller checks exact eight-path committed delta, all twenty-two authority
  hashes against candidate/working/approved inputs, frozen source/tests/config,
  both implementation report hashes, unchanged historical VAL-008 and preserved
  unrelated work. Candidate report hashes:
  REM-005 `df3207f11d0beab740599346ffa9b9a9ec76eb1b9aca6861093956014cafebd1`;
  WS-03 `836cbe11243da78ba34f739f808b97ee52dda264b3448c51d3763caae1d31965`.
- Historical VAL-008 is superseded only for decisions on the changed candidate
  in [separate status](validation/VAL-008-status.yaml); its original report,
  findings and evidence remain byte-exact. [VAL-009 request](validation/VAL-009-request.yaml)
  pins previous/full delta, bounded correction and original work-unit aggregate,
  approved authority hashes, report hashes, six remediation/ten WS-03 criteria,
  seventeen commands and independent public/probe/baseline obligations.
- Current phase validation/state pending; queue 6c complete, 6d current.
  Request preparation is not dispatch, independent verification or acceptance.
  Only a new fresh context may perform VAL-009. Wider initiative remains
  started/normal/local, accepted predecessors intact; no WS-04/delivery authority.

## 2026-09-28 — Fresh VAL-009 Successfully Dispatched

- Committed request checkpoint `34a457a540ca5e092c332431c824a537dcf7a8b0`,
  request SHA256
  `15d4ca5ebbacd828b3b918ca2e6b409e42cd2862042a09062dce07ff23b6e715`.
  Newly spawned `/root/mcp_ws03_val009` uses `fork_turns: none`, no inherited
  controller/builder/remediator context, and the exact read-only request.
- Reviewer reads request/authority while controller records this actual
  dispatch; formal start snapshot/checks wait for controller GO after the
  stable dispatch checkpoint. No candidate, request, twenty-two authorities,
  implementation reports or source/tests/configuration will change during
  formal review. No builder/remediator conclusions are supplied as evidence.
- Phase validation/state in_review, queue 6d in progress. No verdict exists
  yet. Fresh delta and entire WS-03 aggregate review are both mandatory;
  no acceptance, later-slice authority or delivery inferred. Original five
  unrelated dirty-path fingerprints still match the controller start snapshot.

## 2026-09-28 — Fresh VAL-009 Verified; WS-03 Closeout Prepared

- New read-only `/root/mcp_ws03_val009`, `fork_turns: none`, reviewed frozen
  `d395acdba9e233cb226f54e6258575f480157cf1` after stable dispatch `9d6df34`.
  Delta, complete original WS-03 aggregate and overall outcome are `VERIFIED`,
  with no findings. Six REM-005 and ten WS-03 criteria all passed; both public
  F-001 variants retain distinct safe source diagnostics after cleanup.
- All seventeen required commands ran independently. 173 focused/459 affected
  aggregate/46 Chat passes; native 233 plus two unchanged invalid-ZIP failures;
  integration 69 plus unchanged board-count failure. Ruff and meaningful
  affected 45-file typing pass. Required default/core-inclusive typing failures
  remain explicit; five fresh accepted-predecessor reproductions establish the
  unchanged NumPy/profile/native/board baseline classifications without waiver.
- Twenty-six independent probe groups passed: actual public routing/registration,
  collision privacy/history/reset, schema/filter/export costs, transactions,
  binding order, retained public owners/cancellation and noisy process/pipe/task
  settlement. Public cleanup assertions precede defensive fixture cleanup;
  deliberately injected scratch assertion separately proves fixture settlement.
- Archive the complete [report](validation/VAL-009-report.md) byte-for-byte,
  SHA256 `69fc9a1355e1de082396fc5259064f9c88976d25f57dd518126bac414dece05a`.
  [Evidence](validation/VAL-009-evidence.yaml) packages all 73 original reviewer
  artifacts losslessly in deterministic gzip/tar, including the original report,
  manifests, exact logs/diffs, executable probes and snapshots. All member
  lengths/hashes are checked against originals; predecessor extraction/caches
  are reproducible scratch inputs, not omitted review evidence. Restore sibling
  layout to inspect the exact artifacts named in the report links. This packaging retains
  generated-log whitespace without changing reviewer evidence or waiving policy.
- Reviewer finalized output-only identity/date/model availability, Markdown
  tables and archive-member navigation before archival; no finding/evidence/candidate input changed.
  Final freeze matches request, 22 authorities, both reports, 968 tracked product
  files and five unrelated dirty paths/60 existing files/preserved deletion.
  Historical VAL-008 remains unchanged; separate status marks its single F-001
  closed only for current-candidate decisions using fresh VAL-009.
- [WS-03 closeout](execution/WS-03-closeout.md) is prepared. Phase closeout/state
  verified, queue 6d complete and 6e awaiting explicit maintainer WS-03 acceptance.
  Wider initiative remains started/granted/normal/local, accepted predecessors
  intact. This records no acceptance, WS-04 scope or delivery authority.
- Controller closeout checks passed: board validation (23 tasks), dashboard
  freshness, documentation lifecycle (344 Markdown files), scoped whitespace,
  complete frozen product/config and both report comparisons. All 24 pinned
  authority/report hashes, unchanged request, 968 product-file hashes and all
  73 archived member lengths/hashes match; five unrelated path fingerprints
  match the original controller snapshot, including the preserved deletion.
  Initial scratch-relative report links failed archival lifecycle checking;
  the independent reviewer supplied archive-member navigation in its final
  output, then the controller regenerated and checked the lossless archive.
  No frozen review input or policy was altered. Product tests were not repeated
  for this evidence/process-only handoff after independent checks completed.

## 2026-09-28 — WS-03 Explicitly Accepted

- Maintainer said "accepted - Summarize WS-03." after review of the independently
  verified closeout and explicit WS-03 acceptance gate. Record acceptance by
  repository maintainer on 2026-09-28 for frozen product candidate
  `d395acdba9e233cb226f54e6258575f480157cf1` and fresh VAL-009's verified delta,
  complete WS-03 aggregate and overall gate, with no findings.
- [WS-03 closeout](execution/WS-03-closeout.md) now records that decision.
  Queue 6e and all WS-03 tasks are complete. WS-00 through WS-03 are accepted
  work units; wider initiative remains started/granted/normal/local with its
  active packet in place. No initiative archive/acceptance or delivery transition.
- Next gate is WS-04 directive/readiness reconciliation before requesting bounded
  approval. Current phase planning/state not_ready describe next-slice preparation,
  not reversal of accepted WS-03 verification. This turn records acceptance and
  summarizes WS-03; it does not perform WS-04 reconciliation or authorize code.
- Frozen source/tests/config, all 22 authority documents, both implementation
  reports, independent request/report/evidence and historical VAL-008 remain
  unchanged. Preserve all five unrelated local paths and their contents;
  stage only the six acceptance/controller files. No product tests repeated
  for this process-only record; board/dashboard/docs/whitespace and freeze/
  preservation checks cover the changed scope.
- Acceptance-record checks passed: board 23 tasks, dashboard current, docs
  lifecycle 344 Markdown files, whitespace clean, exact frozen product/report
  comparison, all 24 pinned input hashes and all 73 archived evidence hashes.
  All 968 tracked product-file hashes and five unrelated path fingerprints
  match the prior controller snapshot, including preserved deletion.

## 2026-09-28 — WS-04 Explicitly Approved And Started

- Maintainer said "proceed - lets build it" after the eight-feature WS-04 scope,
  compatibility/non-goals and approval boundary were presented. This explicitly
  authorizes that work; no redundant approval is requested for necessary narrow
  Chat config/registry/turn/budget wiring.
- Reconciled exact [directive](directives/ws-04-friday-chat-context-budget.md)
  and [readiness](execution/WS-04-readiness-checkpoint.md) before product edits.
  Chat already has selection/schema subtraction and exact retrieval limits;
  add MCP metadata, result reservation, floor/required tools and public provider
  wiring without changing accepted runtime/transport contracts or budgets.
- Base `acd1fd1e736a38134fac40d7fdb35cd1f32cf683`; dedicated branch
  `feature/friday-mcp-ws04-chat-budget`. Wider initiative started/granted/normal/
  local. Phase implementation/state not_ready; new fresh VAL-010 required.
- Original five dirty-path fingerprints match. No cleanup/broad staging, live
  MCP/network/model/provider/credentials or delivery. Baseline commands run in
  scratch and remain separate from implementation verification. WS-05+ unapproved.

## 2026-09-28 — WS-04 Implementation Frozen; Fresh VAL-010 Pending

- Stable candidate `53d76d45cedea16122436e53b178de074c5bc322` from accepted base `acd1fd1e736a38134fac40d7fdb35cd1f32cf683` and approval/start
  `ac4530a`, exactly seven source/three test/one report paths plus two controller
  builder-evidence artifacts. No accepted framework/transport/native source,
  dependency/config example, transcript/ingestion/telemetry or later-slice edits.
- Public Chat provider/registry owner and exact callable routing; canonical
  config, metadata/schema copy checks, count/cost/reservation/floor policy,
  optional MCP reduction, required/manual failure and safe budget diagnostics.
- Independent verdict remains pending. Builder evidence records 84 focused,
  190 Runtime, 680 Memory/1 skip and 440 accepted MCP passes. Full Chat: 479
  passes/5 skips plus unchanged PTY failure and three blocked localhost fixture
  errors independently baselined before edits; integration 69 passes/unchanged
  board-count failure, reproduced from extracted accepted predecessor. Default
  NumPy typing fails unchanged; all seven changed sources pass meaningful
  Python 3.13 typing. Ruff, board/dashboard and docs/whitespace checks pass.
- Complete [report](execution/WS-04-implementation-report.md) and lossless
  [builder evidence](execution/WS-04-builder-evidence.yaml) retain commands,
  failures/development iterations and exact preservation hashes. Twenty-four
  prior pinned inputs, 961 prior product files outside scope, and all five
  unrelated roots remain unchanged; only named paths staged.
- [VAL-010 request](validation/VAL-010-request.yaml) freezes exact complete
  work-unit diff, 26 authority/three report hashes and all eight criteria.
  Fresh context/read-only required; do not pass private builder reasoning or
  rely on builder conclusions. Phase validation/state pending; not dispatched,
  verified, accepted or delivered. No product/report/authority edits during review.

## 2026-09-28 — Fresh VAL-010 Dispatched

New `/root/mcp_ws04_val010`, `fork_turns: none`, received the frozen request
after local request commit `62a5c50`. It independently reviews complete WS-04
aggregate, all eight criteria and required commands/probes, read-only. No
parent/private builder reasoning is supplied. Phase validation/state in_review;
no verdict/acceptance or later-slice/delivery authority. Candidate source/tests/
config, 26 authorities and three implementation reports remain frozen; all
unrelated work is preserved. Task 7 independent review is in progress.

## 2026-09-28 — Fresh VAL-010 Verified; WS-04 Closeout Prepared

- New read-only `/root/mcp_ws04_val010`, `fork_turns: none`, reviewed candidate
  `53d76d45cedea16122436e53b178de074c5bc322`, complete work-unit aggregate from `acd1fd1`. All eight criteria
  pass; aggregate and overall VERIFIED with no findings. No inherited private
  context or governed writes. Fifteen independent required commands executed.
- 84 focused, 190 Runtime, 680 Memory/one skip and 440 accepted MCP passes;
  Ruff/seven-source typing/board/dashboard/docs/freeze checks pass. Full Chat
  479 passes/five skips plus identical predecessor PTY/socket-fixture failures;
  integration 69 passes/unchanged board-count failure; default NumPy typing
  failure independently reproduced. No failed check relabeled passing or waived.
- Complete report SHA256 `21064837f338f0334cfab89cc6a3b9ac03c65ec9bbdbe438b22a7b682739f5f9` archived byte-exact;
  all 56 original reviewer artifacts losslessly preserved and each member
  length/hash checked. 16 independent probe groups recorded with exact
  reproduction logs and public cleanup separated from defensive settlement.
- Frozen request, 26 authorities, three reports and all 971 product/config files
  remain unchanged. Five unrelated local roots preserved, including deletion.
  Controller changes only evidence/closeout/board/dashboard/index/queue/log.
- Phase closeout/state verified; [closeout](execution/WS-04-closeout.md) prepared.
  Next gate explicit maintainer WS-04 acceptance. Wider initiative remains
  started/granted/normal/local; accepted WS-00–03 intact. No acceptance, WS-05+
  product implementation, initiative archive or delivery is inferred.
- Controller closeout checks pass: board 23 tasks, dashboard current,
  documentation lifecycle 348 Markdown files, scoped/aggregate whitespace,
  exact candidate product/report comparison, unchanged request and all 29
  pinned input/971 product hashes. All 56 archived member lengths/hashes match
  original independent artifacts; report remains byte-exact at SHA256
  `21064837f338f0334cfab89cc6a3b9ac03c65ec9bbdbe438b22a7b682739f5f9`.
  Original five unrelated path fingerprints remain unchanged. Only nine
  evidence/closeout/controller paths staged; no product tests repeated for
  this evidence/process-only handoff after independent checks completed.

## 2026-09-28 — WS-04 Explicitly Accepted

- Maintainer explicitly said "accepted" after the independently VERIFIED
  WS-04 result, full review/closeout links and explicit acceptance gate.
  Record acceptance by repository maintainer on 2026-09-28 for frozen candidate
  `53d76d45cedea16122436e53b178de074c5bc322` and complete fresh VAL-010,
  all eight criteria passing with no findings.
- [Closeout](execution/WS-04-closeout.md) records that decision. Queue task 7
  complete; WS-00 through WS-04 accepted. Wider initiative stays started/
  granted/normal/local with active packet intact. No initiative acceptance,
  archive, later-slice implementation or delivery transition.
- Next gate WS-05 directive/readiness reconciliation before bounded approval.
  Current phase planning/state not_ready describes next-slice preparation;
  accepted WS-04's independently VERIFIED result is unchanged. This turn records
  acceptance only and does not perform WS-05 reconciliation.
- Stage only six acceptance/controller paths. Frozen source/tests/config, all
  29 authority/report inputs, request, complete independent report and 56-artifact
  evidence archive remain unchanged. Preserve all five unrelated path roots
  and their contents, including the existing deletion. No product tests repeat
  for this process-only record; board/dashboard/docs/whitespace and frozen-input/
  evidence/preservation checks verify the changed scope.
- Acceptance-record checks pass: board 23 tasks, dashboard current, documentation
  lifecycle 348 Markdown files and scoped whitespace clean. Exact candidate
  product/report comparison, request hash, all 29 pinned input/971 product hashes,
  all 56 evidence member lengths/hashes and five unrelated path fingerprints
  match the verified closeout, including the preserved deletion.

## 2026-09-28 — WS-05 Directive And Readiness Reconciliation

Maintainer said "proceed" after explicit WS-04 acceptance and the stated WS-05
planning gate. From `1e845001f6b6c48e7cc255ac76460a058f026f70` on the WS-04 branch,
the controller performed read-only product inspection/local synthetic stdio,
SQLite/JSONL and protocol request-double probes. The final probe exited 0 and
confirms missing final byte enforcement, raw argument capture, missing per-call
provenance, sanitizer warning retention/wrapper growth and dropped isError status.
Two disclosed scratch-harness errors preceded the successful unique-database run;
all original scripts/logs/facts are archived, with no runtime databases committed.

The [reconciled draft](directives/ws-05-execution-provenance-transcript.md) and
[readiness checkpoint](execution/WS-05-readiness-checkpoint.md) bind 23 exact
implementation paths, eight tactical tasks and ten criteria. Decisions: full
argument redaction/no hashes; explicit checked bounded untrusted output; static
protocol failure handling; one typed Core DTO; declared Transcript dependency;
compatible per-call persistence and JSONL/full versus human-summary exports.
Shared security/Agent/Runtime/Memory source and all accepted authorities stay frozen.

Execution phase `planning`, validation state `not_ready`; next gate explicit
approval of reconciled WS-05 construction directive. This is planning only,
not WS-05 implementation/validation/acceptance. No feature branch, product edits
or subagent dispatch. Board remains started/granted/normal/local with authority
through WS-04 only. No later-slice, delivery or external-effect authority.

## 2026-09-28 — WS-05 Explicit Approval And Start

Maintainer explicitly said "ws-05 is approved. proceed" after complete bounded
directive/readiness review. Approved scope: exactly 23 implementation paths,
eight tactical tasks and ten criteria at `a609f948fe2d869ac29d0cce29d22d9334cd7d08`.
Dedicated branch created: `feature/friday-mcp-ws05-execution`. Board names that
branch and implementation gate before code generation. Phase implementation,
validation state not_ready. Stable candidate, full required checks and fresh
read-only complete-aggregate VAL-011 precede proposed work-unit acceptance.
No later-slice, push/merge/release or live-provider authority. Five unrelated
path fingerprints are retained from the accepted predecessor audit.

## 2026-09-28 — WS-05 Candidate Frozen For VAL-011

Approved task 8 implementation and builder checks are complete at `2388e747ba1bf8157881230ad36ae3ef3272b807`
from full work-unit base `a609f948fe2d869ac29d0cce29d22d9334cd7d08`. Exactly 23 deliverables plus two builder-evidence
artifacts are committed. Full logs, unchanged baseline reproduction, offline
wheel/import proof and preservation are recorded. Phase validation/state pending;
next gate fresh read-only complete-aggregate [VAL-011](validation/VAL-011-request.yaml).
Request preparation is not dispatch, verification or acceptance. Accepted WS-00
through WS-04 and five unrelated dirty paths remain intact. No later phase or delivery.

## 2026-09-28 — Fresh VAL-011 Dispatched

New `/root/mcp_ws05_val011` was created with `fork_turns: none` after request
commit `d9d8685`. It received only the pinned request, frozen candidate/base,
read-only restrictions and required complete independent report/evidence. No
parent/private reasoning or inherited builder context was supplied. Phase
validation/state in_review; no verdict or acceptance exists yet. Candidate
source/tests/config, 30 authority documents and four reports remain frozen,
with 978 tracked product-file hashes and five unrelated fingerprints checked.

## 2026-09-28 — WS-05 VAL-011 Changes Requested; REM-006 Approval Gate

Fresh read-only `/root/mcp_ws05_val011` completed full original WS-05 aggregate
at frozen `2388e747ba1bf8157881230ad36ae3ef3272b807`, **CHANGES_REQUESTED**,
with two High findings: F-001 unsafe MCP session snapshot/JSONL/all-session CSV
env capture; F-002 across-iteration native ID collision with new production
persistence failure. Complete report and all 182 original evidence members are
archived byte-for-byte; 149 report links and every artifact hash verify. All 17
required checks ran; independent matrix 22 passed/five failed. Baselines, package
resolver limit/successful isolated wheel imports and resource/freeze evidence
remain explicit. Candidate, 30 authorities/four reports/978 product files and
five unrelated fingerprints remain unchanged.

Task 8 cannot close or advance to acceptance. The concrete eight-path
[REM-006 draft](remediation/REM-006-directive.md) converts both findings exactly
once, with six criteria, regressions, separate-remediator requirement and new
fresh delta plus complete-aggregate VAL-012. Next gate explicit maintainer approval
of that draft and separate remediator. Phase remediation/state changes_requested
is a proposed correction gate, not authority to execute. No fixes or remediator
dispatch occurred. Accepted predecessors, later-phase and delivery boundaries hold.

## 2026-09-28 — REM-006 Approved And Started

Maintainer explicitly said "fix them - proceed" after the complete eight-path
REM-006 proposal and separate-remediator request. Both High VAL-011 findings,
regressions/report/checks and new fresh read-only delta plus original WS-05
aggregate VAL-012 are authorized. Remediation base `dd6a337eb2928ab4050ea70fb41dc77072210e34`;
branch `feature/friday-mcp-ws05-execution`; phase remediation/state changes_requested.
Next dispatch the separate remediator, execute only the approved manifest and
freeze a corrected candidate. Historical reports/evidence and accepted predecessors
remain byte-exact; five unrelated dirty fingerprints are preserved. No acceptance,
later-phase, delivery or historical database cleanup authority is inferred.

## 2026-09-28 — Separate REM-006 Remediator Dispatched

New `/root/mcp_ws05_rem006`, `fork_turns: none`, received the complete approved
eight-path directive, both independently reported findings, exact bases and
local-only constraints after authorization commit `5145f06`. It may implement,
test/report and commit only the approved paths; no validator role or acceptance.
Controller freezes 41 authority/report/evidence inputs, 971 product paths outside
the seven allowed existing product/test files, and five unrelated fingerprints.
Phase remediation/state changes_requested; candidate and fresh VAL-012 remain
pending. Historical VAL-011 report/request/evidence and accepted predecessors
remain byte-exact. Controller work is process metadata only.

## 2026-09-28 — REM-006 Candidate Frozen; VAL-012 Prepared

Separate approved remediator committed corrected candidate `f24ed20f82eac0cbce17e4b86615497cc9993921`
from remediation base `dd6a337eb2928ab4050ea70fb41dc77072210e34`. Original WS-05
aggregate base remains `a609f948fe2d869ac29d0cce29d22d9334cd7d08`. Historical VAL-011
report/evidence stays byte-exact, superseded only for changed-candidate decisions.
Pinned VAL-012 requires new fresh read-only remediation delta plus full original
aggregate, six remediation and ten original criteria, all required checks and
independent public/privacy/correlation/package/cleanup probes. Phase validation/
state pending; preparation supplies no verdict or acceptance. Unrelated dirty
work and frozen authorities/reports are preserved. Next dispatch fresh validator.

## 2026-09-28 — Fresh Read-Only VAL-012 Dispatched

New `/root/mcp_ws05_val012`, `fork_turns: none`, received the frozen request
after process/evidence commit `e0b3395`. It independently reviews REM-006 delta
then complete original WS-05 aggregate at `f24ed20f82eac0cbce17e4b86615497cc9993921`,
all six remediation/ten original criteria and eighteen commands plus own public
probes/package/baseline checks. No parent/builder/remediator context or private
reasoning was supplied. Phase validation/state in_review; no verdict/acceptance.
Product/config/test bytes, 32 authorities/five reports and all hash-pinned
historical/builder evidence remain frozen; five unrelated paths preserved.

## 2026-09-28 — VAL-012 Complete; Bounded REM-007 Continuation Started

Fresh read-only `/root/mcp_ws05_val012` at `f24ed20f82eac0cbce17e4b86615497cc9993921`
returned CHANGES_REQUESTED in delta and work-unit aggregate. Both original High
VAL-011 findings close. Single Medium VAL-012-F-001 requires restoring malformed
native-call skip behavior before native ID reservation; final independent matrix
31 passed/four failures for that single finding. Complete report/archive/manifests
are preserved byte-exact. All 18 mandatory commands, baseline comparisons,
local-peer UAT/cleanup and pinned preservation are recorded in the review.

The existing explicit "fix them - proceed" REM-006 approval already requires
native compatibility and allows these same paths. REM-007 records a bounded
three-path continuation under REM006-AC03/WS05-AC09, not new scope or inferred
approval. Follow-up base `446e3a6f4e445a456dcbe6ef25058e60af54fe53`; reviewed source remains f24ed20. Only loop.py,
existing execution security tests and existing REM-006 report may change. Dispatch
the same separate remediator after this recorded started/granted/current-branch
gate. This is cycle two: freeze new candidate, retain historical VAL-012 bytes,
then new fresh read-only VAL-013 delta and complete original aggregate. If it is
unsuccessful, return unresolved findings. Phase remediation/changes_requested;
no acceptance/later phases/delivery. Five unrelated fingerprints remain preserved.

## 2026-09-28 — Separate REM-007 Remediator Dispatched

Controller dispatched the same separate `/root/mcp_ws05_rem006` after approval/
start commit `69831774fcd3ebdbd62a2f09b207ecafe1e6bb58`. REM-007 is a bounded
continuation of the existing explicit REM-006 approval: exactly loop.py, existing
execution-security tests and existing REM-006 report. New freeze pins 56 inputs,
976 outside-scope product files and five unrelated fingerprints. Original
VAL-012 report/archive retained byte-exact. Correct only VAL-012-F-001 and required
regressions, preserve original High-finding corrections. All 18 mandatory checks,
new stable candidate and fresh VAL-013 delta/full aggregate required. Root is
controller; reviewer performs no fixes. Phase remediation/changes_requested;
no new scope, acceptance or delivery. Second unsuccessful cycle would return
unresolved findings to maintainer.

## 2026-09-28 — REM-007 Candidate Frozen; Fresh VAL-013 Prepared

Separate remediator froze `cca86b51105666d12c2e7ed571f8f9a05d2085f9` within the exact three already-approved
paths, from follow-up base `446e3a6f4e445a456dcbe6ef25058e60af54fe53`. Original REM-006 base `dd6a337eb2928ab4050ea70fb41dc77072210e34` and
WS-05 aggregate base `a609f948fe2d869ac29d0cce29d22d9334cd7d08` remain explicit. Original VAL-012 report/archive
and earlier evidence remain byte-exact, superseded for changed candidate only.
Fresh VAL-013 must close VAL-012-F-001 and reconfirm both original High findings,
with delta/full aggregate, all required commands and independent public/storage/
privacy/compatibility/package/cleanup/freeze evidence. Phase validation/pending;
not dispatched/verified/accepted by preparation. Second remediation cycle; if
unsuccessful return remaining findings. Accepted predecessors, unrelated paths,
later phase and delivery boundaries remain intact.

## 2026-09-28 — Fresh VAL-013 Dispatched

New `/root/mcp_ws05_val013`, `fork_turns: none`, receives only pinned public
request/authority/candidate/evidence, not builder/controller conversation or
private reasoning. Candidate `cca86b51105666d12c2e7ed571f8f9a05d2085f9`, request
commit `f5510ed599cae1342f33ce8bc0ca977c2c1b0c06`, 34 authorities/five reports,
19 required commands and current freeze govern. Review follow-up delta, complete
remediation delta and full original WS-05 aggregate; all original/remediation/
follow-up criteria and independent public/storage/privacy/compatibility/package/
cleanup/preservation evidence. Governed workspace read-only; scratch only.
Phase validation/in_review; no verdict, acceptance, later scope or delivery.
Second remediation cycle; any unsuccessful result returns remaining findings.

## 2026-09-28 — VAL-013 VERIFIED; WS-05 Acceptance Gate

Fresh-context read-only `/root/mcp_ws05_val013` returned delta, complete original
work-unit aggregate and overall VERIFIED for `cca86b51105666d12c2e7ed571f8f9a05d2085f9`. Both original High
findings and Medium VAL-012-F-001 close; all ten WS05/six REM006/four REM007 criteria
and 19 required commands have complete independent evidence. Full original report,
archive, manifest, verification and delivery are archived byte-exact; member hashes
and report links verify. Frozen source/authority/reports/historical evidence and
five unrelated fingerprints remain intact. Controller closeout metadata introduces
no product or authority change. Phase closeout/verified; next explicit maintainer
WS-05 acceptance. Wider initiative remains started/granted/normal/local, accepted
predecessors intact, no later phase/delivery or historical storage cleanup.

## 2026-09-28 — WS-05 Explicitly Accepted

The repository maintainer said "accepted" after the verified WS-05 closeout,
complete fresh VAL-013 review and acceptance gate were presented. Acceptance
applies to frozen `cca86b51105666d12c2e7ed571f8f9a05d2085f9`, delta and complete
original aggregate VERIFIED, all three numbered findings closed, complete
report/evidence archived byte-exact. The closeout records accepting maintainer,
date and explicit decision. WS-00 through WS-05 are accepted work units.

Only controller acceptance/index/queue/log/board/dashboard metadata changes;
source/tests/config, controlling authorities and independent report/archive
bytes remain unchanged. Five unrelated dirty fingerprints are preserved.
Current phase closeout/state verified; next gate reconcile the draft WS-06
directive/readiness and obtain separate bounded scope approval. No WS-06
implementation begins here. Wider initiative stays started/granted/normal/local;
its active packet remains until full initiative acceptance. No delivery,
historical storage cleanup or later-phase authority is inferred.

## 2026-09-29 — WS-06 Planning Reconciled; Bounded Approval Pending

Maintainer said "proceed" at the recorded WS-06 planning/readiness gate after
explicit WS-05 acceptance. Controller performed focused read-only source/authority
inspection and rewrote only the unapproved WS-06 draft plus planning metadata.
Preparation HEAD `6890771127e405f3299ed783296174366c67f995`; branch remains
`feature/friday-mcp-ws05-execution`. No product changes, new branch, agent dispatch
or implementation approval. Accepted `cca86b5`, VAL-013 and predecessors intact.

The draft now binds 18 paths, seven tasks and ten criteria. Existing Core policy
remains authoritative; server OR canonical-tool grants are exact explicit union.
Default direct ingestion is off, ordinary conversation memory preserved. Add typed
sanitary bounded snapshots with stage/verify/append-readback/publish sequencing;
immutable transcript receipts remain truthful even if publication fails. Pending
records cannot enter retrieval/promotion; labels/filtering respect WS-04's supplied
budget once. Snapshot/no-revocation assumptions and narrow maintenance eligibility
guard prevent provenance loss. No schema/config/dependency/Core/store edits.

Readiness source hashes, original draft, preservation and environment limits are
recorded in execution/WS-06-readiness-evidence.yaml. Ordinary uv run tried a
Transcript rebuild and failed resolving hatchling through unavailable PyPI DNS;
installed-environment --no-sync board validate/next/show passed (23 tasks). Final
metadata/document/freeze checks are recorded separately in readiness evidence.
All 978 product bytes, 34 authority inputs, five reports, 19 historical artifacts
and five unrelated fingerprints remain unchanged. No runtime-state cleanup.

Current phase planning/state not_ready for WS-06; WS-05 remains accepted/VERIFIED.
Next explicit bounded directive approval. After approval, pin planning checkpoint,
create feature/friday-mcp-ws06-memory and record started execution before code.
Fresh read-only aggregate VAL-014 and later maintainer acceptance remain required.
The wider initiative remains started/granted/normal/local; no WS-07/08 or delivery.
