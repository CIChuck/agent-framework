# Friday MCP Ordered Task Queue

Status: REM-004 committed; fresh VAL-007 independent review pending dispatch
Updated: 2026-09-28
Initiative: `friday-mcp`
Branch: `feature/friday-mcp-ws02-lifecycle`
Planning checkpoint before this update: `5200819b79ec10dee541800505994ab3fcf140ee`
Current frozen product candidate: `a257f041d1d68f8aea2f5b9773df1b88acd82379`

The [development board](../../board.yaml) remains the canonical initiative
registry. This queue makes the existing [tactical sequence](tactical-plan.md)
and current [REM-004 directive](remediation/REM-004-directive.md) actionable;
it does not approve later workstreams, create new board states, or change
construction scope. Execute one gate at a time and update queue evidence at
each handoff. An approved future step is not a claim that it has started.

## Current Checkpoint

- WS-00 contracts/defaults and WS-01 strict configuration: independently
  verified and explicitly accepted.
- WS-02 runtime lifecycle: implemented but not accepted. Historical VAL-006
  verified REM-003's delta but requested aggregate changes for a production
  stdio shutdown hang. That report is superseded for current-candidate decisions,
  with its full verdict/findings retained. Current overall result is pending.
- REM-004: explicitly approved by the maintainer on 2026-09-28, including a
  separate remediator. The subsequent "proceed" execution attempt
  hit `agent thread limit reached` for both new dispatch and prior-remediator
  resumption. Existing `/root/mcp_ws01_val004` confirmed availability and has
  been reassigned/dispatched as the separate remediator; it was not a WS-02
  builder/remediator and will not validate its new work. Correction, required
  checks and exact six-path commit are complete at `a257f04`; fresh-validator
  capacity remains unresolved. [VAL-007](validation/VAL-007-request.yaml) pins
  the candidate, authority manifest, full scope and all required checks.
- WS-03 through WS-08: draft, not approved for implementation. WS-09: deferred
  optional scope. Initiative remains `started`; delivery remains `local`.

## Immediate Queue

| Order / ID | Next task | Readiness | Exit gate / evidence |
| --- | --- | --- | --- |
| 1 / MCP-NEXT-01 | Dispatch a separate REM-004 remediator to fix paused-output/forced-kill teardown entirely within the approved transport boundary. | Complete: reassigned separate remediator executed the approved scope. | No MCP base/manager/runtime product changes or private boundary reach-through; exact six-path correction committed. |
| 2 / MCP-NEXT-02 | Add direct/public-kernel noisy-peer regressions, retained-owner and cancellation coverage; run required checks and commit evidence. | Complete: frozen candidate `a257f04`, [implementation report](execution/REM-004-implementation-report.md). | 39 focused, 333 aggregate, 32 loading and 46 Chat tests pass; integration 44 pass plus declared board-count baseline; Ruff and prescribed typing pass. No independent verdict inferred. |
| 3 / MCP-NEXT-03 | Freeze the new candidate and request fresh read-only VAL-007 delta plus complete WS-02 aggregate review. | Current: candidate frozen, historical status note retained and pinned request prepared; fresh dispatch pending capacity. | Independent production retry/cleanup probes, every criterion, baseline separation and one overall review outcome; existing contexts cannot be relabeled fresh. |
| 4 / MCP-NEXT-04 | Record WS-02 closeout and request explicit maintainer acceptance. | Only after task 3 returns overall VERIFIED. | Independent report and work-unit closeout recorded; maintainer acceptance recorded separately. If this second WS-02 remediation cycle fails, stop and return unresolved findings to the maintainer rather than auto-remediate again. |
| 5 / MCP-NEXT-05 | Reconcile the draft WS-03 directive with the accepted WS-02 handoff and current registry/contracts, then request bounded WS-03 approval. | Waits for WS-02 acceptance. Planning/readiness only until approval. | Exact files, immutable untrusted discovery handoff consumption, typed metadata, naming/filter/security rules, tests and stop conditions reconciled; maintainer explicitly approves WS-03 before code generation. |

Tasks 1–2 are complete as implementation/check/commit steps, not validation or acceptance.
The controller may not self-repair or
relabel that agent or another existing reviewer as fresh validation. If new
validator creation still fails after candidate freeze, stop at task 3 and
resume review in a session with fresh-agent capacity; do not waive the gate.
No new remediation scope approval is needed. Task 3 has a frozen request but
no reviewer verdict; task 4 and later gates remain unstarted. Fresh dispatch
must be attempted and recorded separately; passing implementation checks
cannot waive that gate.

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
