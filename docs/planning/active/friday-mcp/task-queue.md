# Friday MCP Ordered Task Queue

Status: WS-02 accepted; VAL-008 changes requested; bounded REM-005 approved for separate remediation
Updated: 2026-09-28
Initiative: `friday-mcp`
Branch: `feature/friday-mcp-ws03-registry`
WS-03 frozen work-unit base: `2c0d6bd1fe481fff9bb180f9e6dfb4a9a2131641`
WS-03 preparation base: `56251144345888f721c9fc9235ad8a54bbbb23db`
Current frozen WS-03 product candidate: `397caa9898612cd989f6404951b3e1f5005dfac2`

The [development board](../../board.yaml) remains the canonical initiative
registry. This queue makes the existing [tactical sequence](tactical-plan.md)
and current [approved REM-005](remediation/REM-005-directive.md) actionable;
it does not approve later workstreams, create new board states, or change
construction scope. Execute one gate at a time and update queue evidence at
each handoff. An approved future step is not a claim that it has started.

## Current Checkpoint

- WS-00 contracts/defaults, WS-01 strict configuration and WS-02 runtime
  lifecycle: independently verified and explicitly accepted.
- WS-02: the maintainer explicitly said "WS-02 accepted" on 2026-09-28.
  [Closeout](execution/WS-02-closeout.md) records that decision for candidate
  `a257f04`. Historical VAL-006
  verified REM-003's delta but requested aggregate changes for a production
  stdio shutdown hang. That report is superseded for current-candidate decisions,
  with its full verdict/findings retained. Fresh [VAL-007](validation/VAL-007-report.md)
  verifies both remediation delta and complete current WS-02 aggregate with no
  findings. Acceptance is for this work unit only, not the wider initiative.
- REM-004: explicitly approved by the maintainer on 2026-09-28, including a
  separate remediator. The subsequent "proceed" execution attempt
  hit `agent thread limit reached` for both new dispatch and prior-remediator
  resumption. Existing `/root/mcp_ws01_val004` confirmed availability and has
  been reassigned/dispatched as the separate remediator; it was not a WS-02
  builder/remediator and will not validate its new work. Correction, required
  checks and exact six-path commit are complete at `a257f04`; fresh-validator
  creation succeeded after remediation completion. [VAL-007](validation/VAL-007-request.yaml) pins
  the candidate, authority manifest, full scope and all required checks.
- WS-03: explicitly approved on 2026-09-28 with "ws-03 approved"; task 6 is
  in progress on the named branch. WS-04 through WS-08: draft, not approved for
  implementation. WS-09: deferred
  optional scope. Initiative remains `started`; delivery remains `local`.
- WS-03 readiness reconciliation is complete in the
  [checkpoint](execution/WS-03-readiness-checkpoint.md) and
  [revised bounded draft](directives/ws-03-tool-naming-metadata-registry.md).
  Explicit approval is recorded; bounded candidate `397caa9` is committed.
  Fresh independent [VAL-008](validation/VAL-008-report.md) now returns
  `CHANGES_REQUESTED` for the sole medium F-001 collision diagnostic finding.

Current task 6 checkpoint: builder implementation/check/commit complete at
`397caa9`, sixteen approved implementation paths. [Report](execution/WS-03-implementation-report.md)
and pinned [VAL-008 request](validation/VAL-008-request.yaml) are recorded.
The earlier fresh-agent capacity stop is resolved. New conversation
`/root/val_008_independent_review`, `fork_turns: none`, completed the read-only
review with all fifteen required commands, all ten criteria, independently
reproduced predecessor baselines and sixteen independent passing probe groups.
The failing public collision-source requirement is retained as F-001; passing
collision prevention/cleanup is not diagnostic conformance. The complete
report is archived byte-for-byte with [evidence](validation/VAL-008-evidence.yaml).

The maintainer explicitly approved bounded REM-005 and its separate remediator
with "That's approved. Proceed." Next is the authorized separate remediation.
Current phase `remediation`, validation state `changes_requested`, condition
normal; work remains started/granted/local. Approved execution may now correct
only F-001. Candidate `397caa9`, historical pinned request,
twenty authority contents and unrelated local paths remain unchanged. Task 6
continues through remediation, new freeze, fresh delta/aggregate review,
closeout and explicit acceptance; no WS-04 authority.

## Immediate Queue

| Order / ID | Next task | Readiness | Exit gate / evidence |
| --- | --- | --- | --- |
| 1 / MCP-NEXT-01 | Dispatch a separate REM-004 remediator to fix paused-output/forced-kill teardown entirely within the approved transport boundary. | Complete: reassigned separate remediator executed the approved scope. | No MCP base/manager/runtime product changes or private boundary reach-through; exact six-path correction committed. |
| 2 / MCP-NEXT-02 | Add direct/public-kernel noisy-peer regressions, retained-owner and cancellation coverage; run required checks and commit evidence. | Complete: frozen candidate `a257f04`, [implementation report](execution/REM-004-implementation-report.md). | 39 focused, 333 aggregate, 32 loading and 46 Chat tests pass; integration 44 pass plus declared board-count baseline; Ruff and prescribed typing pass. No independent verdict inferred. |
| 3 / MCP-NEXT-03 | Freeze candidate and obtain fresh read-only VAL-007 delta plus complete WS-02 aggregate review. | Complete: fresh context returned delta, aggregate and overall VERIFIED, no findings. | Full report preserves pinned authority, exact scope, required checks, independent production/resource-integrity probes, baselines and residual risks. |
| 4 / MCP-NEXT-04 | Record WS-02 closeout and explicit maintainer acceptance. | Complete: maintainer said "WS-02 accepted" on 2026-09-28; decision recorded in [closeout](execution/WS-02-closeout.md). | Work-unit acceptance only; no wider initiative completion or later-workstream authority inferred. |
| 5 / MCP-NEXT-05 | Reconcile the WS-03 directive and request bounded approval. | Complete: maintainer explicitly approved the full reconciled directive on 2026-09-28. | Exact paths, handoff/sidecar, strict includes, transactional registry ownership, conservative sanitation/caps, tests and stop conditions approved. |
| 6a / MCP-NEXT-06A | Record full independent VAL-008 and convert F-001 into bounded REM-005. | Complete: unchanged report/evidence archived and directive drafted. | One medium finding appears exactly once; exact eight-path remediation boundary, six criteria, checks and non-goals are reviewable. |
| 6b / MCP-NEXT-06B | Approve REM-005 and its separate remediator. | Complete: maintainer said "That's approved. Proceed." | Complete bounded directive and separate remediation explicitly authorized. |
| 6c / MCP-NEXT-06C | Dispatch separate remediator; correct only F-001, add regressions, run checks and freeze a new candidate. | Authorized; preparation/dispatch next. | Safe typed both-source diagnostics retained after public cleanup, exact scope, native preservation and all required check results. |
| 6d / MCP-NEXT-06D | Obtain new fresh-context VAL-009 delta then complete WS-03 aggregate review. | Reserved only; no request or dispatch yet. | Pin new candidate/approved authority; all six REM-005 and ten WS-03 criteria independently evaluated. Keep VAL-008 unchanged as historical evidence. |
| 6e / MCP-NEXT-06E | Record verified WS-03 closeout and request explicit work-unit acceptance. | Not ready; depends on independent VERIFIED. | Maintainer acceptance is separate from verification; only after acceptance reconcile/request WS-04 approval. |

Tasks 1–4 are complete, with fresh independent verification and a subsequent
explicit maintainer acceptance decision. Task 5's planning/readiness work is
complete and its explicit approval gate is satisfied. Task 6a records the
completed VAL-008 review and draft correction. Task 6b is approved; task 6c is
current, and tasks 6d–6e and later workstreams remain unstarted. Accepted predecessor
verification and acceptance are unchanged. Do not reuse the remediator as its
fresh validator or waive a missing independent-review capacity gate.

Required remediation checks are listed in approved REM-005 and the approved WS-03
directive. Keep unchanged native invalid-zip fixtures, integration board count,
default NumPy syntax and four core profiles.py typing failures separate from
regressions; none is authorized for repair or waived. Meaningful affected-scope
Python 3.13 typing must still pass. Preserve all unrelated paths listed in
VAL-008; never broad-stage the
mixed worktree. Local fake peers only, with explicit fixture/probe cleanup.

## Subsequent MCP Workstream Queue

These are the existing proposed workstreams in tactical order. Each needs its
own reconciled, approved construction directive, implementation checks, stable
candidate, fresh independent review, and explicit work-unit acceptance. None
is authorized by the REM-004 approval.

| Order / work unit | Scope | Entry gate |
| --- | --- | --- |
| 6 / [WS-03](directives/ws-03-tool-naming-metadata-registry.md) | Executable MCP registry integration: canonical names, collision rejection, typed metadata, include/exclude filters, schema/cap enforcement, sanitization, and mixed native/MCP compatibility. | WS-02 accepted and task 5's bounded WS-03 directive approved. |
| 7 / [WS-04](directives/ws-04-friday-chat-context-budget.md) | Friday Chat tool selection and context budgeting: select rather than blindly inject tools, account for schema/result costs before memory retrieval, preserve the memory floor, and expose safe budget decisions. | Predecessor workstreams verified/accepted and WS-04 explicitly approved. |
| 8 / [WS-05](directives/ws-05-execution-provenance-transcript.md) | Secure execution/result handling and transcript provenance: bounded sanitized outputs, redacted arguments, typed provenance, and the accepted no-stored-argument-hash default. | Budget/registry integration ready; WS-05 directive reconciled with accepted policies and explicitly approved. |
| 9 / [WS-06](directives/ws-06-memory-compatibility-ingestion.md) | Memory compatibility and opt-in ingestion: no long-term MCP storage by default, policy allowlists/sanitization/quarantine, provenance and retrieval-budget compatibility. | Prior contracts/execution/budget behavior ready and WS-06 explicitly approved. |
| 10 / [WS-07](directives/ws-07-telemetry-diagnostics-health.md) | Redacted telemetry, runtime diagnostics, and operational health; make any new Chat health command a separate explicit scope decision. | Relevant lifecycle/registry/execution/budget signals ready and WS-07 explicitly approved. |
| 11 / [WS-08](directives/ws-08-documentation-guide-closeout.md) | Tested guide/config examples, package/developer docs, accurate capabilities/limits, and documentation/UAT closeout for implemented behavior. | WS-01 through WS-07 ready and WS-08 explicitly approved. Live/paid/provider UAT requires its own external-effects authority. |
| 12 / Initiative closeout | Complete feature-branch aggregate review, evidence reconciliation, and explicit maintainer initiative acceptance. | Required workstreams verified and accepted, no unresolved mandatory finding; delivery operations remain a separate approval. |
| Deferred / [WS-09](directives/ws-09-optional-external-config-include.md) | Optional external MCP config includes parsed into the canonical typed runtime model, with path confinement and precedence. | Tools-only inline integration stable and a separate maintainer decision to activate the phase. Not required automatically by this queue. |

## Separate Backlog And Delivery Gates

- [Friday runtime skills](../../backlog/friday-runtime-skills/README.md) remains
  a separate backlog initiative. Its next gate is definition review and
  promotion of a bounded first phase, not implementation under MCP approval.
  Reconcile system-prompt placement and shared tool/memory/skills budget
  accounting when that initiative is promoted; do not schedule it here by
  inference.
- Other initiative priorities on the development board are unchanged; this
  work-unit queue does not create additional board initiatives or reorder them.
- Push, merge, release, deployment, credentials, paid/provider calls and other
  externally visible actions require separate authority. Acceptance and local
  deterministic evidence do not grant those permissions.
