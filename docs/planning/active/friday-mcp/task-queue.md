# Friday MCP Ordered Task Queue

Status: Active execution queue; REM-004 approved, dispatch pending
Updated: 2026-09-28
Initiative: `friday-mcp`
Branch: `feature/friday-mcp-ws02-lifecycle`
Planning checkpoint before this update: `5200819b79ec10dee541800505994ab3fcf140ee`
Current product candidate: `26f4d7d4bfd0514b6eb76bed71cb4797da91a067`

The [development board](../../board.yaml) remains the canonical initiative
registry. This queue makes the existing [tactical sequence](tactical-plan.md)
and current [REM-004 directive](remediation/REM-004-directive.md) actionable;
it does not approve later workstreams, create new board states, or change
construction scope. Execute one gate at a time and update queue evidence at
each handoff. An approved future step is not a claim that it has started.

## Current Checkpoint

- WS-00 contracts/defaults and WS-01 strict configuration: independently
  verified and explicitly accepted.
- WS-02 runtime lifecycle: implemented but not accepted. VAL-006 verifies the
  REM-003 ownership correction; its full WS-02 aggregate is
  `CHANGES_REQUESTED` for one production stdio shutdown hang.
- REM-004: explicitly approved by the maintainer on 2026-09-28, including a
  separate remediator. No remediator has been dispatched and no REM-004
  product changes have been made at this planning checkpoint.
- WS-03 through WS-08: draft, not approved for implementation. WS-09: deferred
  optional scope. Initiative remains `started`; delivery remains `local`.

## Immediate Queue

| Order / ID | Next task | Readiness | Exit gate / evidence |
| --- | --- | --- | --- |
| 1 / MCP-NEXT-01 | Dispatch a separate REM-004 remediator to fix paused-output/forced-kill teardown entirely within the approved transport boundary. | Ready: maintainer approved; dispatch pending. | Exact six-path directive obeyed; no MCP base/manager or runtime source edits, no private boundary reach-through. Stop and request direction if scope is insufficient. |
| 2 / MCP-NEXT-02 | Add direct-transport and public-kernel noisy-peer regressions, including successful discovery, partial startup, cancellation, stdout/stderr redaction, released resources, and retained ownership on genuinely incomplete cleanup. Run required checks and commit a stable candidate with implementation evidence. | Waits for task 1. | Reproduce F-001 before correction, demonstrate bounded real teardown afterward, rerun all directive checks, preserve existing REM-003 behavior, and record full candidate hash and exact path manifest. |
| 3 / MCP-NEXT-03 | Controller freezes the new candidate, retains historical review evidence with a superseded decision-status note, and requests fresh read-only VAL-007 delta plus complete WS-02 aggregate review. | Waits for committed candidate from task 2. | Pinned authority/revisions/hashes, exact correction and aggregate diffs, every criterion, independent production retry/cleanup probes, baseline separation, and one overall review outcome. |
| 4 / MCP-NEXT-04 | Record WS-02 closeout and request explicit maintainer acceptance. | Only after task 3 returns overall VERIFIED. | Independent report and work-unit closeout recorded; maintainer acceptance recorded separately. If this second WS-02 remediation cycle fails, stop and return unresolved findings to the maintainer rather than auto-remediate again. |
| 5 / MCP-NEXT-05 | Reconcile the draft WS-03 directive with the accepted WS-02 handoff and current registry/contracts, then request bounded WS-03 approval. | Waits for WS-02 acceptance. Planning/readiness only until approval. | Exact files, immutable untrusted discovery handoff consumption, typed metadata, naming/filter/security rules, tests and stop conditions reconciled; maintainer explicitly approves WS-03 before code generation. |

Task 1 is the next executable action. Tasks 2–4 are downstream gates for the
approved REM-004/WS-02 correction, not completed work. VAL-007 is the next
planned review identifier; no request, dispatch, or verdict exists yet.

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
