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
