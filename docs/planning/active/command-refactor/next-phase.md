# Command refactor — next-phase checkpoint

Date: 2026-11-06
Branch: `feature/command-retirement`
Status: Foundation checkpoint merged; retirement directive ready for approval
Execution phase: planning
Validation state: not_ready (RET-001); merged checkpoint independently VERIFIED

This is the main next-step document. The [board](../../board.yaml) owns initiative
state and the [packet index](README.md) maps supporting material. The overall
command refactor remains started. Its completed checkpoint is merged; the next
unit and its administrative branch preparation are local.

## Completed checkpoint

[PR #13](https://github.com/CIChuck/agent-framework/pull/13) merged into master at
`6f291ca5755a616d9185c86dff104b660a1fba8c`. The old `feature/command-refactor` branch was deleted locally and
remotely after merge/tree/ancestry confirmation. The new branch starts at that
merge. Two unrelated working Chat example configurations remain byte-identical,
uncommitted and excluded from the PR.

The [fresh independent aggregate report](validation/checkpoint/verified-report.md)
VERIFIED candidate `51334a5b3f92ca7922976f1c0f3aa15443ae61e6`, with 3,116 tests
and current package/default-install/archive proof. Only evidence/status closeout
followed before publication. [Delivery receipt](validation/checkpoint/delivery.json)
records exact base/head/merge and remote gates: clean mergeability, no configured
checks, protection, rulesets, requested reviews or unresolved threads. Missing CI
is not described as a passing CI run. Existing root Ruff/pytest/format and
optional-cohort cache limitations remain in the report.

The foundation was accepted separately. Its no-default-handler neutral package,
required-finance metadata and legacy CLI launcher retirement are delivered.
Current Chat still has 50 canonical commands and three aliases. No command has
been retired or migrated, and no TUI source was added.

## Next steps, in order

1. **Approve [CD-CMD-RET-001](directives/CD-CMD-RET-001-nine-command-retirement.md).**
   It removes the nine selected slash commands directly from Chat before the
   pilot. Approval includes RET-GATE-01–03: bounded retirement ordering/P1
   disposition, preserved runtime behavior and orphan-state/metric treatment.
2. **Implement and validate RET-001 after exact approval.** Capture before/after
   evidence, remove registrations/help/exclusively dead command code, and update
   affected tests/guides. Prove 41 canonical names/three aliases and ordinary
   unknown responses with no former effects. Preserve retained behavior,
   startup priming, configuration, budgets/native/MCP execution and diagnostics.
   Freeze the candidate, obtain fresh independent review and present acceptance.
3. **Prepare PILOT-001.** Define catalog/host routing/rendering/exit/clear seams,
   then approve its own directive before moving help/exit/cls and aliases.
4. **Migrate retained families and integrate.** Close affected P0/P1 contracts,
   use bounded directives, then cumulative installed/cross-family proof and
   aggregate review before full command-refactor acceptance and TUI resumption.

## Exact next approval

- Source base: `6f291ca5755a616d9185c86dff104b660a1fba8c` (merged master).
- Directive SHA-256: `a8646a4bbd2c0275bca74d5430a9169b053f45490c34621aa144f224b0f79e28`.
- Foundation API SHA-256 remains
  `e5ba883fb246967320243e1dbc9c2a70fcf6189c05540a45961388f2b6466b74`.

Only branch/source identity changed in the draft; its retirement scope and
verification requirements are unchanged. This administrative handoff introduces
no product/test/dependency/lock change and grants no construction approval.
Record actual administrative descendants and source equality before any future
unit starts. Historical approvals/reports/requests retain their exact candidate
provenance; current working references are updated in board/authority/index.
The prior checkpoint publication authority is consumed for PR #13; new retirement
publication and exact implementation authority are not inferred.
