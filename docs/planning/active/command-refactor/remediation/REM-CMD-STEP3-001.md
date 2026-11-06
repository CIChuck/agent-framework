# REM-CMD-STEP3-001 — bounded readiness correction

Date: 2026-11-06
Status: authorized for planning/evidence correction; product construction excluded
Maintainer: Chuck Russell
Authorization: “i Accept your recommendation. Proceed.”
Base: `e0eb3e9c718539b014174721c5d5086e5c94c393`

The maintainer accepted the controller's recommendation to correct five
readiness findings, freeze the revised packet and obtain fresh independent
validation before Step 4. This records the documentation/evidence exemption:
only planning contracts, process records and an isolated diagnostic capture
script/output change; runtime behavior and product package bytes cannot change.
API-01–API-06 approval remains pinned to
`e5ba883fb246967320243e1dbc9c2a70fcf6189c05540a45961388f2b6466b74`.
This approval does not approve CD-CMD-FND-001, RD-01/RD-02 or product code.

## Exact corrections and acceptance

1. **CMD-RDY-001:** amend draft CD-CMD-FND-001 to join the existing lock-step
   cohort as its eighteenth project. Permit only the necessary root metadata,
   cohort-test, artifact-inventory and package-list changes during later
   construction. Require cohort/metadata/artifact and import checks. No root
   metadata, product test or package is changed in this remediation. Acceptance:
   draft scope covers every required integration edit and the commands install
   the package before root tests.
2. **CMD-RDY-002:** correct default-install attribution and sandbox claims in
   the readiness summary, unit map, receipt and draft RD-02; append an execution
   log correction. Preserve original raw logs, augmented script/output and all
   round-one council records. Add a pinned default-profile probe that captures
   imports separately from help/entry-point loading and runtime exclusions,
   blocks network, and rerun in a fresh disposable default wheel environment.
   Acceptance: default Chat/CLI imports/help and tools/finance failure are
   represented separately with exact commands, versions, hashes and per-run
   network counts. No runtime health or minimum-extras claim.
3. **CMD-RDY-003:** place FILE-001 after MAINT-001, require MAINT-001 admission
   capability and explicitly preserve ingest admission. Update summary/scenario
   references. Acceptance: acyclic order; all 50 cases, nine retirements and
   three aliases remain assigned once; no new admission implementation unit.
4. **CMD-RDY-004:** choose a single future lock-generation procedure: explicitly
   permitted Python package-registry metadata/artifact access for resolution
   and verification, no application-provider/tool calls and no unrelated
   upgrades. Require semantic lock-diff inspection and frozen checks afterward.
   Acceptance: new local member/root references are the only expected semantic
   lock changes; otherwise stop for disposition. Registry access is described
   in the draft for Step 4 and is not needed by current offline evidence work.
5. **CMD-RDY-005:** split SC-08's foundation source-level CLI regression from
   later installed-client entry-point acceptance. Acceptance: the latter stays
   explicit, required before affected delivery, and is not assigned to FND-001.

## Allowed paths and work split

- `directives/CD-CMD-FND-001-neutral-foundation.md`: a separate remediator
  handles its package-boundary and verification changes under repository policy.
- `readiness-review.md`, `validation/step3/unit-map.json`,
  `validation/step3/receipt.json`: controller applies bounded corrections.
- New `validation/step3/default-profile/` diagnostic script, install/probe logs,
  installed version list and pinned receipt; disposable environments outside
  the checkout only.
- This remediation record and `validation/step3/correction-*` review handoff/
  evidence/results; `README.md`, `next-phase.md`, `tactical-plan.md`, `authority.json`,
  `execution-log.md`, board task/event and generated dashboard for process
  reconciliation only. Partial-stage shared board/dashboard changes.

Non-goals: product source/tests/metadata/lock changes, API redesign, new command
handlers, client fixes, runtime/store construction, live providers/tools,
retirement implementation, PR/push/merge/release or unrelated dirty edits.
The original council request, reports and collection receipt stay immutable.

## Verification and handoff

Use fresh disposable offline Chat/CLI installation from the saved, hash-checked
wheels. Run the new pinned probe outside the checkout with isolated Python;
check dependency consistency, expected observed outcomes and module origins.
Run Ruff lint/format on the new script, map/dependency/source-hash checks,
board validation, documentation lifecycle and Git whitespace checks. Preserve
the exact four unrelated TUI broken-link baseline and all protected file hashes.
Full owning suites are not required to rerun for planning-only corrections;
their stored counts remain historical. Do not claim foundation implementation
verification because no foundation package exists.

Commit a stable correction candidate and dispatch a fresh read-only validator
with no builder transcript. Review the five corrections and all R-01–R-08
readiness criteria against the complete selected Step 3 packet, not just this
delta. This is limited readiness validation, not aggregate feature-branch
implementation/merge validation; that later gate remains open. One new
validation pass is authorized here; do not launch an automatic remediation or
council loop. Stop for unresolved findings or Step 4's exact directive/base,
RD-01/RD-02 and architecture-readiness decision.
