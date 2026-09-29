# Friday MCP Ordered Task Queue

Status: WS-04 accepted; WS-05 explicitly approved, implementation started
Updated: 2026-09-28
Initiative: `friday-mcp`
Branch: `feature/friday-mcp-ws05-execution`
WS-03 frozen work-unit base: `2c0d6bd1fe481fff9bb180f9e6dfb4a9a2131641`
WS-03 preparation base: `56251144345888f721c9fc9235ad8a54bbbb23db`
Current frozen WS-03 product candidate: `d395acdba9e233cb226f54e6258575f480157cf1`
Historical VAL-008 candidate: `397caa9898612cd989f6404951b3e1f5005dfac2`

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
- WS-03: independently verified and explicitly accepted on 2026-09-28 with
  "accepted - Summarize WS-03."; task 6 is complete on the named branch.
  [Closeout](execution/WS-03-closeout.md) records acceptance of frozen `d395acd`
  and complete fresh VAL-009. WS-04: independently verified by fresh VAL-010,
  and explicitly accepted on 2026-09-28 with "accepted"; WS-05 through WS-08: draft, not approved for
  implementation. WS-09: deferred
  optional scope. Initiative remains `started`; delivery remains `local`.
- WS-03 readiness reconciliation is complete in the
  [checkpoint](execution/WS-03-readiness-checkpoint.md) and
  [revised bounded draft](directives/ws-03-tool-naming-metadata-registry.md).
  Explicit approval is recorded; bounded candidate `397caa9` is committed.
  Historical fresh independent [VAL-008](validation/VAL-008-report.md) returned
  `CHANGES_REQUESTED` for the sole medium F-001 collision diagnostic finding.

Historical task 6 builder checkpoint: implementation/check/commit complete at
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
with "That's approved. Proceed." Separate remediation is complete at `d395acd`.
Fresh [VAL-009](validation/VAL-009-report.md) returned delta, full WS-03 aggregate
and overall `VERIFIED`, no findings. All seventeen independent commands ran;
predecessor baselines were reproduced and twenty-six independent groups passed.
The complete byte-exact report and [evidence](validation/VAL-009-evidence.yaml)
are archived. Six REM-005 and ten WS-03 criteria passed. Frozen candidate,
request, twenty-two authorities and both implementation reports remained stable;
unrelated local work remained unchanged.

The maintainer explicitly accepted the verified WS-03 work unit with
"accepted - Summarize WS-03." on 2026-09-28; [closeout](execution/WS-03-closeout.md)
records candidate, review and decision. Tasks 6a–6e are complete. WS-04 is now approved after directive/readiness reconciliation. Current phase
`implementation`, validation state `not_ready` describe this work unit;
accepted WS-03's VERIFIED result remains unchanged. Condition normal; wider
initiative remains started/granted/local. Historical VAL-008 is unchanged and
superseded only for decisions on the corrected candidate. WS-05 and later implementation
and delivery retain separate approval gates.

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
| 6c / MCP-NEXT-06C | Dispatch separate remediator; correct only F-001, add regressions, run checks and freeze a new candidate. | Complete: separate remediator committed exact eight-path candidate `d395acd`. | 173 focused / 459 aggregate / 46 Chat pass; baseline failures retained, source/report/authority/preservation checks complete; no independent verdict inferred. |
| 6d / MCP-NEXT-06D | Obtain new fresh-context VAL-009 delta then complete WS-03 aggregate review. | Complete: new `/root/mcp_ws03_val009`, `fork_turns: none`, returned delta, aggregate and overall VERIFIED, no findings. | All seventeen checks executed, independent baselines reproduced, twenty-six groups passed and all six REM-005/ten WS-03 criteria satisfied. Complete byte-exact report/evidence archived; historical VAL-008 unchanged. |
| 6e / MCP-NEXT-06E | Record verified WS-03 closeout and request explicit work-unit acceptance. | Complete: maintainer explicitly accepted verified WS-03 on 2026-09-28; [closeout](execution/WS-03-closeout.md) records the decision. | Work-unit acceptance only; next is WS-04 directive/readiness reconciliation and separate approval. |

Tasks 1–4 are complete, with fresh independent verification and a subsequent
explicit maintainer acceptance decision. Task 5's planning/readiness work is
complete and its explicit approval gate is satisfied. Task 6a records the
completed VAL-008 review and bounded correction. Tasks 6b–6e are complete;
WS-03 and WS-04 are independently verified and explicitly accepted;
subsequent workstreams remain unstarted.
Accepted work-unit verification and acceptance are unchanged. Do not reuse the remediator as its
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
| 6 / [WS-03](directives/ws-03-tool-naming-metadata-registry.md) | Executable MCP registry integration: canonical names, collision rejection, typed metadata, include/exclude filters, schema/cap enforcement, sanitization, and mixed native/MCP compatibility. | Complete: verified and explicitly accepted in WS-03 closeout; frozen candidate `d395acd`. |
| 7 / [WS-04](directives/ws-04-friday-chat-context-budget.md) | Friday Chat tool selection and context budgeting: select rather than blindly inject tools, account for schema/result costs before memory retrieval, preserve the memory floor, and expose safe budget decisions. | Complete: fresh complete VAL-010 aggregate VERIFIED and explicit maintainer acceptance recorded in WS-04 closeout. |
| 8 / [WS-05](directives/ws-05-execution-provenance-transcript.md) | Secure execution/result handling and transcript provenance: bounded sanitized outputs, redacted arguments, typed provenance, and the accepted no-stored-argument-hash default. | Approved with "ws-05 is approved. proceed"; implementation started from `a609f94`, stable candidate and fresh VAL-011 required. |
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

## 2026-09-28 — WS-04 Approved Execution Checkpoint

Maintainer said "proceed - lets build it" after the eight-feature scope review.
Reconciled directive and readiness checkpoint are complete within that scope.
Task 7 is current: implement exact Chat paths, add local regressions/UAT, run
required checks, freeze a candidate, obtain fresh read-only VAL-010, then propose
closeout for explicit acceptance. WS-05 and later implementation remains draft.
Current phase implementation/state not_ready; accepted WS-00 through WS-03
remain intact. Later execution/delivery retains separate approval gates.

## 2026-09-28 — WS-04 Candidate And VAL-010 Request

Task 7 implementation/check/commit complete at `53d76d45cedea16122436e53b178de074c5bc322`.
Next is new fresh-context read-only VAL-010, complete WS-04 aggregate from
`acd1fd1e736a38134fac40d7fdb35cd1f32cf683`, all eight criteria and independent required checks/probes.
Request pins 26 authorities and three reports. Current phase validation/state
pending; no verdict, acceptance, WS-05 authority or delivery is inferred.
All five unrelated path fingerprints and predecessor contracts remain unchanged.

## 2026-09-28 — Fresh VAL-010 Dispatched

New `/root/mcp_ws04_val010`, `fork_turns: none`, received the frozen request
after local request commit `62a5c50`. It independently reviews complete WS-04
aggregate, all eight criteria and required commands/probes, read-only. No
parent/private builder reasoning is supplied. Phase validation/state in_review;
no verdict/acceptance or later-slice/delivery authority. Candidate source/tests/
config, 26 authorities and three implementation reports remain frozen; all
unrelated work is preserved. Task 7 independent review is in progress.

## 2026-09-28 — WS-04 Verified Closeout And Acceptance Gate

Task 7 implementation/check/commit and fresh VAL-010 aggregate review are
complete at frozen `53d76d4`, VERIFIED with no findings. Complete report and
lossless evidence are archived. [Closeout](execution/WS-04-closeout.md) records
all eight criteria, independent checks/probes, baseline debt and frozen inputs.
Current phase closeout/state verified; next is explicit maintainer WS-04
acceptance. Task 7 acceptance is pending. WS-05 remains draft/unstarted; no
later-slice implementation or delivery authority is supplied by verification.

## 2026-09-28 — WS-04 Accepted; Next Preparation Gate

Task 7 is complete: the maintainer explicitly said "accepted" after the
VERIFIED WS-04 result, complete fresh VAL-010 and explicit acceptance gate.
[Closeout](execution/WS-04-closeout.md) records the decision for frozen
`53d76d4`. WS-00 through WS-04 are accepted work units. Wider initiative
remains started/granted/normal/local; no initiative archive or delivery.

Next is WS-05 directive/readiness reconciliation before requesting bounded
approval. This turn records acceptance without performing reconciliation or
authorizing WS-05 code. Phase planning/state not_ready describes that next gate;
accepted work-unit verification remains unchanged.

## 2026-09-28 — WS-05 Ready For Bounded Approval

Task 8 planning/readiness is complete: exact 23-path [directive](directives/ws-05-execution-provenance-transcript.md),
eight tasks/ten criteria, local evidence and export/dependency/redaction decisions
are recorded in the [checkpoint](execution/WS-05-readiness-checkpoint.md).
Next is explicit maintainer approval, then recorded start/base/branch, implementation,
stable candidate, fresh read-only complete-aggregate VAL-011 and explicit acceptance.
Current phase planning/state not_ready; no product/branch/reviewer action or
later-slice/delivery authority is inferred from the planning "proceed".

## 2026-09-28 — WS-05 Approved Execution

Explicit maintainer approval: "ws-05 is approved. proceed". Task 8 is current:
implement the exact approved 23 paths, perform required checks/UAT, freeze a
candidate, obtain new fresh read-only complete-aggregate VAL-011, then propose
closeout for explicit acceptance. Work-unit base `a609f94`; branch
`feature/friday-mcp-ws05-execution`; phase implementation/state not_ready.
Accepted WS-00 through WS-04 remain intact. Later slices and delivery remain gated.

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
