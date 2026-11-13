# INGEST — planning baseline and implementation branch

2026-11-13. **Sequence approved by Chuck: “yes proceed”.**
The [Git authorization](../../../../approval/ingest-git-handoff-20261113.json)
permits the checkpoint, push, baseline PR, merge when checks permit and new coding
branch. Execution results are recorded separately from this plan. Document
approval is recorded in the
[approval record](../../../../approval/ingest-construction-documents-20261113.json).

## Current baseline

The inspected local branch is `feature/cmd-ingest-001`, at `d12f9c6c` before
this documentation amendment. Live remote refs were checked: `master` is
`c36e7ee5`, and the remote planning branch is `3f0490cb`. The local planning
branch is 100 commits ahead of that remote branch. No PR for this branch was
found in the connected repository search. These are inspection-time facts;
refresh before publishing.

Compared with `origin/master`, the committed branch contains 1,604 planning and
evidence files, 35 isolated readiness-harness files under `tests/readiness/ingest/`
and `.gitignore`. No Friday package source, package metadata, product test or
shared lock changes are in that diff. This is a planning **and readiness-test**
baseline, so its PR must not be described as documentation only. The readiness
work has already happened; merging it does not install or activate ingestion.

The two dirty Chat example YAML files and `.friday-old/` are unrelated local
state. Keep them unstaged and untouched. Do not copy them into the coding worktree.

## Approved sequence

1. Commit only the current planning approval/validation amendment and its exact
   approval receipt on `feature/cmd-ingest-001`. Complete the presented-commit
   binding without changing the approved content. Run the planning checks.
2. Under the recorded Git authorization, push this branch and open a baseline PR
   to `master`. State that the analysis, design, directives and impact v0.8 are
   maintainer-approved, with a three-model council after every implementation
   slice. Preserve the actual historical review outcomes and baseline debt.
3. Merge the reviewed baseline before coding. Prefer a regular merge to retain
   the commit IDs cited throughout the evidence. If squash is selected, first
   agree how the original evidence commits will remain reachable. The explicit “yes proceed” approves this merge step; a PR or passing check
   alone would not grant that authority.
4. Create `feature/cmd-ingest-implementation` from the merged `master`, ideally
   in a separate clean worktree. Record that branch/base on the board and in the
   phase binding; retain the old checkout and its local state. Bind the actual
   private test roots and protected original paths before any implementation or
   install. This is a Git/operational binding, not a new request to approve the
   unchanged design.
5. Build I1, commit a stable candidate and run its council. Repeat for I2, then
   I3 with the aggregate council. Each gate has at most three passes. Human UAT
   and the later implementation PR remain separate steps.

This gives a clear pre-implementation checkpoint and a separate implementation
diff. Abandoning an unmerged coding branch leaves the approved baseline intact;
if implementation is later merged, revert its merge or PR as appropriate.
Branch isolation does not replace disposable stores or the execution profile.

## Proposed baseline PR text

**Title:** Record approved ingestion design and isolated readiness baseline

The `/ingest` document remediation is ready for implementation planning to close.
This PR records Chuck's approval of the analysis, design, construction directives
and package-impact assessment v0.8, together with the completed isolated readiness
harness/evidence. It defines Sol, Astra and Opus councils after I1, I2 and I3,
with at most three passes per gate; I3 also reviews the full aggregate.

No ingestion product implementation, package dependency/lock change or production
deployment is included. Product coding will start on a separate branch from the
merged baseline. Planning board, documentation lifecycle, package metadata,
binding/link/whitespace and preserved-state checks are the validation for this
approval amendment; the recorded historical Docling tests are not rerun here.

## Execution boundary

The document approval and subsequent Git confirmation are separate recorded
decisions. Proceed through the authorized handoff without re-requesting them.
Record actual commits, PR, merge and new branch before implementation; stop on
failed checks, unexpected remote changes or an approval requirement that cannot
be satisfied within this authorization. Product delivery and production effects
remain outside this baseline PR.
