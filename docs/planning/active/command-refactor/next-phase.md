# Command refactor — next-phase checkpoint

Date: 2026-11-06
Branch: `feature/command-refactor`
Status: Foundation accepted; aggregate checkpoint findings await bounded disposition
Execution phase: validation
Validation state: changes_requested (aggregate checkpoint; RET-001 remains not_ready)

This is the main next-step document. The [packet index](README.md) maps supporting
files; the [board](../../board.yaml) owns initiative state. The whole initiative
remains started/local. No next construction directive has been approved yet.

## Accepted foundation

Chuck Russell accepted CMD-FND-001 by direct instruction:
“approved, proceed what's next steps?” This follows the foundation-only
[VERIFIED report](validation/VAL-CMD-FND-001-report.md) for
`b4fc199eeef3c63a5cf9a8b960cf61c0116170ad`, with no mandatory findings.
All 319 scoped tests, focused static checks, exact lock proof and isolated
artifact checks passed independently. Existing broad Ruff, root pytest collection
and four unrelated TUI-link failures remain documented. Acceptance covers the
foundation unit, not the whole feature branch.

[Builder report](validation/CMD-FND-001-report.md),
[frozen review request](validation/CMD-FND-001-request.json),
[durable receipts](validation/CMD-FND-001-evidence.json) and
[construction approvals](approval/foundation-readiness.md) retain their original
provenance. Old pending/draft labels in frozen documents describe earlier states;
this checkpoint, board and append-only execution log record the later decisions.

## Immediate next decision

Read [CD-CMD-CHK-001](directives/CD-CMD-CHK-001-checkpoint-reconciliation.md),
the single bounded disposition prepared from the
[aggregate CHANGES_REQUESTED report](validation/checkpoint/aggregate-report.md).
Its source base is `dea496075de55060ad477820e04b71c78239cca0` and SHA-256 is
`d0cc21779452767862b52ca025db1fa11417e8481418d119aa8a0a875ef2823d`.

AGG-001 needs an explicit one-time historical construction-authority exception
for the existing two-file archival-board behavior. AGG-002 needs mechanical
formatting of exactly five files with unchanged syntax trees. All 3,116 tests
pass, including full Chat 826; this does not cure missing authority or a failed
required format check. No source correction has begun. After approval, correct
only those findings, obtain fresh independent verification and continue the
already-authorized checkpoint push/PR/merge/new-branch sequence.

## Current checkpoint delivery

Chuck Russell authorized the proposed checkpoint commit/push/PR/merge and
fresh-branch sequence. First obtain aggregate independent verification of the
whole current branch, then publish/merge its checkpoint. See the
[exact scope and exclusions](validation/checkpoint/README.md). Preserve the two
unrelated working Chat example configurations; include authorized planning
transfers. After merge, create `feature/command-retirement` from updated master
and refresh the draft's branch/source identity before its approval. Existing
frozen work-unit reports remain candidate-specific. This supersedes earlier
no-delivery labels for this checkpoint only; no retirement construction follows.

## Next steps, in order

1. **Review and approve [CD-CMD-RET-001](directives/CD-CMD-RET-001-nine-command-retirement.md).**
   It removes the nine previously selected names directly from current Chat,
   before PILOT-001. Its requested approval includes RET-GATE-01–03: the bounded
   retirement-before-full-family-P1 sequence, preserved runtime behavior and
   explicit orphan-state/metric treatment. RD-01 alone does not authorize it.
2. **Implement and validate RET-001 after that approval.** Capture before/after
   evidence; remove registration/help/name exposure and exclusively dead command
   code; update affected tests and guides. Prove 41 canonical names/three aliases,
   ordinary unknown responses and no former effects. Preserve `/tools`, startup
   priming, runtime config, budgets/native/MCP execution and retained diagnostics.
   Freeze the candidate, obtain fresh independent review, then present acceptance.
3. **Prepare and approve PILOT-001.** Define catalog ownership, Chat routing,
   rendering and exit/clear lifecycle seams before moving help/exit/cls and the
   quit/q/clearscreen aliases into the shared implementation.
4. **Proceed through retained families and final integration.** Complete each
   affected P0/P1 contract/evidence gate, then use separate bounded directives in
   dependency order. Cross-family/installed proof, aggregate review and final
   refactor acceptance precede resuming TUI development.

## Single next approval

Read the [retirement directive](directives/CD-CMD-RET-001-nine-command-retirement.md).
Its embedded case/effect table, scope, three prerequisite decisions and verification
plan are the current review material; supporting sources are linked there.

- Proposed product/source base: `08b1900defda3150f30027bec30998360515b72d`.
- Directive SHA-256: `5be2c7af2384a1bc15a3f385dbca16807ec29d504e2c08e184f23cac4d8c1a66`.
- Foundation API SHA-256 remains
  `e5ba883fb246967320243e1dbc9c2a70fcf6189c05540a45961388f2b6466b74`.

This draft is prepared for a decision, not approved by this continuation.
The historical [unit map](validation/step3/unit-map.json) remains proposed and
cannot approve later units. Full family schemas, service ownership, progress/
cancellation and supported-environment/client scenarios remain required before
those affected migrations. This retirement draft requests only its own bounded
sequencing disposition. No product source changed during this preparation.

Legacy CLI launcher retirement and mandatory finance remain separately VERIFIED
at `06285ae4` and `d003c4db`; RD-02 needs no defect waiver. No push, PR, merge,
release, deployment or TUI construction is authorized by retirement planning. The
later explicit checkpoint instruction supplies only the delivery authority above.
