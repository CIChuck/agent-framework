---
title: Board validation and GitHub delivery reconciliation
initiative: friday-board-delivery-reconciliation
document_type: initiative-index
status: draft
work_state: queued
condition: normal
created: 2026-10-15
updated: 2026-10-15
implementation_authority: not_granted
next_gate: Review and approve the delivery-evidence contract, migration and bounded construction directive
---

# Board validation and GitHub delivery reconciliation

The maintainer requested that this remediation be queued on 2026-10-15.
This is a proposed work item; no implementation is authorized. Existing task
priorities and maintainer acceptance boundaries remain unchanged.

## Problem and observed evidence

[PR #9](https://github.com/CIChuck/agent-framework/pull/9) merged into master at
2026-10-15T01:55:15Z as a2dd82be951aaa1bb15dc4cc1f5753f14727f8ad, and its
source branch was deleted. The cleanup task still recorded local delivery and
PR/merge execution as its next gate. Ordinary board validation passed.
The [corrected delivery receipt](../../active/friday-deprecated-credential-cleanup/delivery-evidence.json)
and [execution log](../../active/friday-deprecated-credential-cleanup/execution-log.md)
record the later reconciliation in local commit ed47d651. That manual correction
does not prevent the failure from recurring.

Current source and tests explain the gap:

- [validate_board()](../../../../scripts/friday-dev-board.py) checks fields,
  lifecycle rules, packet placement and event structure, without Git/GitHub
  observation or delivery-event/evidence reconciliation.
- The validate command checks that the rendered dashboard matches board.yaml.
  A dashboard can faithfully render stale delivery information.
- set-delivery requires an evidence string for merged/released states but does
  not verify the evidence contents. The board has no structured task-to-PR map.
- [Existing board tests](../../../../tests/integration/test_development_board.py)
  accept the illustrative string "merge commit abc123" and verify monotonic
  delivery changes; they do not test remote freshness or receipt agreement.
- Read-only in-memory probes on 2026-10-15 returned no validation errors when
  the corrected cleanup task was reverted to local while retaining its merge
  event/receipt, and when its merged state was retained without a delivery event.
  The repository files were not modified by those probes.

The [original governance build plan](../../../archive/completed/2026/development-kanban-governance/build-plan.md)
specified structural validation and guarded mutations, without a live GitHub
reconciliation requirement. This remediation adds that missing capability and
makes the delivery-closeout handoff explicit.

## Proposed scope

1. Define structured delivery references and observations: owning task/work unit,
   repository, PR number, candidate/head revision, target branch, observed merge
   SHA/time, verification time/source and separately observed branch cleanup.
   Resolve how multiple PRs, reopened work and prior delivered revisions coexist
   before implementing the schema. A reused/deleted branch name is insufficient
   as the sole identity.
2. Strengthen offline validation to check evidence/receipt shape, referenced
   artifacts and hashes, delivery-event agreement and required evidence for
   merged/released records. Missing legacy evidence needs explicit migration,
   not invented history or silently assumed verification.
3. Add a read-only delivery audit, with a proposed interface such as
   validate --delivery. Query authoritative GitHub PR metadata for mapped
   deliveries and identify stale recorded states. Ordinary offline validation
   must state that GitHub delivery was not checked. Authentication, rate limits,
   missing mappings and unavailable networking must report verification
   incomplete with a non-success result in strict delivery mode. Verification
   availability remains distinct from the recorded delivery-state enum.
4. Add an explicit reconciliation operation, with a proposed interface such as
   reconcile-delivery --apply. Under authorized local-write scope, update only
   proven delivery observations/state, append a deduplicated event, retain
   evidence and regenerate the dashboard. Surface obsolete next gates and
   reconcile bounded packet closeout metadata. Do not rewrite arbitrary prose
   or infer approval/acceptance from a merge.
5. Integrate the audit/reconciliation into post-merge closeout and the process
   used before claiming the board is current. Record whether a report covers
   structural consistency, saved evidence or current GitHub observations.
6. Plan merge-event and periodic auditing as a subsequent bounded automation
   slice. A periodic audit catches missed events; merge-event handling must
   distinguish closed-and-merged from closed-without-merge. External write
   credentials, workflow permissions and publication behavior require explicit
   approval before implementation/activation.

The command names above are proposals, not existing supported commands.
Local Git may corroborate commit presence. GitHub PR metadata establishes the
PR merge observation. A missing branch alone does not establish a merge, and
squash/rebase delivery must not depend on merge-commit-message heuristics.

## Acceptance criteria and regression coverage

- **AC-01 / PR9 regression:** A mapped GitHub PR is merged while its task remains
  local/pushed. Delivery audit detects the mismatch with exact PR/merge evidence.
  Reconciliation corrects the board, event, receipt and dashboard. Offline
  structural checks alone never claim live delivery freshness.
- **AC-02 / Evidence consistency:** Reject missing, malformed, mismatched or
  tampered delivery receipts and contradictory typed delivery events. Check
  repository, PR, target branch and candidate identity; unrelated PRs cannot
  advance a task. Legacy migration is explicit and auditable.
- **AC-03 / Unmerged cases:** Open PRs, closed-unmerged PRs and deleted source
  branches without a proven merge do not advance delivery to merged.
- **AC-04 / Incomplete verification:** Authentication errors, rate limits,
  unavailable network/API and unmapped deliveries are visible incomplete
  results. Preserve prior observations; do not convert uncertainty into a
  verified merge, a successful delivery check or an automatic delivery downgrade.
- **AC-05 / Revision scope:** Multiple PRs, reused branches, reopened work,
  historical merges/releases and squash/rebase merges follow the approved
  delivery/revision contract. An old merged PR cannot stand in for new work;
  observing a merge cannot downgrade an already released historical delivery.
- **AC-06 / Safe repeatability:** Reconciliation is idempotent for unchanged
  observations, avoids duplicate events, checks for concurrent board/candidate
  changes and preserves unrelated dirty files and tasks. Preview/check mode is
  read-only; apply mode requires explicit authorized scope. All generated views
  remain reproducible and validation passes after the update.
- **AC-07 / Authority:** Delivery updates never approve, accept, reopen or close
  implementation work implicitly. No automatic source push/merge/branch deletion,
  credential action, release or deployment is introduced by this remediation.
- **AC-08 / Lifecycle integration:** Post-merge closeout and board-status reporting
  use the new evidence/freshness distinction. If later automation is approved,
  test missed/duplicate events, periodic recovery, permissions and self-trigger
  avoidance as part of that separate slice.

## Proposed implementation order and validation

First approve the structured contract, legacy migration rules and exact authority.
Then implement schema/model validation, read-only audit and guarded reconciliation
with deterministic mocked GitHub responses. Add PR9 and failure-mode regressions,
CLI help/status wording and policy/operator documentation. Test with private
fixtures and no real credentials; any live read-only GitHub verification must
be explicitly included in the approved validation scope. Run focused board tests,
changed-scope Ruff/Mypy, board/render/documentation checks and full committed-range
whitespace. Freeze the candidate for fresh-context independent review before
proposing completion. Implement event/scheduled automation only under its own
approved directive and external-effect boundaries.

Likely affected implementation paths, after approval:

- scripts/friday-dev-board.py and docs/planning/board.schema.json;
- tests/integration/test_development_board.py;
- docs/reference/policies/development-task-lifecycle.md and related operator guidance;
- bounded migration/evidence records for existing delivery entries;
- later GitHub workflow files only if that automation slice is approved.

## Non-goals and current gate

This queue entry does not modify validators, schema, tests, workflows, existing
task states or GitHub. It does not grant Langfuse or other queued work authority.

Next gate: review and approve the delivery-evidence contract, migration and a
bounded construction directive. Status remains queued; implementation authority
remains not_granted; delivery is not_started and no implementation branch exists.
