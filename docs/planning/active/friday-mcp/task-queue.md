# Friday MCP Ordered Task Queue

Status: WS-02 accepted; WS-03 directive reconciled and awaiting explicit approval
Updated: 2026-09-28
Initiative: `friday-mcp`
Branch: `feature/friday-mcp-ws02-lifecycle`
WS-03 preparation base: `56251144345888f721c9fc9235ad8a54bbbb23db`
Current frozen product candidate: `a257f041d1d68f8aea2f5b9773df1b88acd82379`

The [development board](../../board.yaml) remains the canonical initiative
registry. This queue makes the existing [tactical sequence](tactical-plan.md)
and current [REM-004 directive](remediation/REM-004-directive.md) actionable;
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
- WS-03 through WS-08: draft, not approved for implementation. WS-09: deferred
  optional scope. Initiative remains `started`; delivery remains `local`.
- WS-03 readiness reconciliation is complete in the
  [checkpoint](execution/WS-03-readiness-checkpoint.md) and
  [revised bounded draft](directives/ws-03-tool-naming-metadata-registry.md).
  Explicit maintainer approval is the current gate; no implementation started.

## Immediate Queue

| Order / ID | Next task | Readiness | Exit gate / evidence |
| --- | --- | --- | --- |
| 1 / MCP-NEXT-01 | Dispatch a separate REM-004 remediator to fix paused-output/forced-kill teardown entirely within the approved transport boundary. | Complete: reassigned separate remediator executed the approved scope. | No MCP base/manager/runtime product changes or private boundary reach-through; exact six-path correction committed. |
| 2 / MCP-NEXT-02 | Add direct/public-kernel noisy-peer regressions, retained-owner and cancellation coverage; run required checks and commit evidence. | Complete: frozen candidate `a257f04`, [implementation report](execution/REM-004-implementation-report.md). | 39 focused, 333 aggregate, 32 loading and 46 Chat tests pass; integration 44 pass plus declared board-count baseline; Ruff and prescribed typing pass. No independent verdict inferred. |
| 3 / MCP-NEXT-03 | Freeze candidate and obtain fresh read-only VAL-007 delta plus complete WS-02 aggregate review. | Complete: fresh context returned delta, aggregate and overall VERIFIED, no findings. | Full report preserves pinned authority, exact scope, required checks, independent production/resource-integrity probes, baselines and residual risks. |
| 4 / MCP-NEXT-04 | Record WS-02 closeout and explicit maintainer acceptance. | Complete: maintainer said "WS-02 accepted" on 2026-09-28; decision recorded in [closeout](execution/WS-02-closeout.md). | Work-unit acceptance only; no wider initiative completion or later-workstream authority inferred. |
| 5 / MCP-NEXT-05 | Reconcile the WS-03 directive and request bounded approval. | Ready for approval: [checkpoint](execution/WS-03-readiness-checkpoint.md) and complete revised draft recorded; no code. | Explicit approval covers exact paths, handoff/sidecar, strict includes, transactional registry ownership, conservative schema sanitation/caps, tests and stop conditions. |

Tasks 1–2 are complete as implementation/check/commit steps, not validation or acceptance.
The controller may not self-repair or
relabel that agent or another existing reviewer as fresh validation. If new
validator creation still fails after candidate freeze, stop at task 3 and
resume review in a session with fresh-agent capacity; do not waive the gate.
No new remediation scope approval is needed. Fresh VAL-007 creation succeeded
after the remediator completed; the earlier capacity stop is historical.
Tasks 1–4 are complete, with fresh independent verification and a subsequent
explicit maintainer acceptance decision. Task 5's planning/readiness work is
complete and its explicit approval gate is pending. Task 6/WS-03 implementation
and later tasks remain unstarted. Current process fields describe WS-03
preparation: execution phase `planning`, validation state `not_ready`.
They do not invalidate the accepted WS-02 verification or authorize WS-03 code.

Required implementation checks are listed in REM-004. Keep the unchanged
integration test expecting 22 rather than 23 board tasks and the default-target
NumPy mypy syntax failure separate from regressions; neither is authorized for
repair here. Meaningful affected-scope Python 3.13 typing must still pass.
Preserve all unrelated dirty paths listed in VAL-006; never broad-stage the
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
