# TUI planning working-home reconciliation

**Historical transfer record:** This describes the earlier move into the TUI
folder. It was superseded by the maintainer's later 2026-11-05 direction to
copy planning back to Agent Framework. Current planning authority is recorded
in the packet index and the new transfer record. The original snapshots and
previous observations below are retained without repeating their evaluation.

Date: 2026-11-05
Maintainer: Chuck Russell
Current home: `agent-framework-friday-tui`, branch `feature/friday-tui`
Status: Documentation consolidated; local design/evidence confirmation pending

## Authority and scope

The maintainer clarified that this checkout warehouses the entire TUI evolution
and that command refactoring is its first stop, then instructed “proceed” with
document-only reconciliation. This supersedes prior separate-checkout directions
for current work. Logical command acceptance still precedes TUI construction.
This records a documentation-only exemption: no runtime behavior can change,
and no product source, tests, package metadata or lockfile is modified.
No design approval, source verification, P0/P1 closure or implementation grant
is inferred. Current destination AGENTS/policies/board govern future work.

## Imported material and overlaps

The complete committed command packet is copied from the exact source commit
in [the manifest](import-manifest.json). The original package is preserved in
[source-command-packet.tar.gz](source-command-packet.tar.gz); source authority
is retained separately in [source-authority.json](source-authority.json).
Only the old destination handoff README overlapped. Current working-location
metadata and the local navigation index are reconciled; source review/evidence
files, historical receipts and raw baseline/scoring data remain intact.
All relative document dependencies were already present locally. The relevant
backlog link/count guidance was reconciled. The pre-existing CMD-F11 tool-trace
working draft was also carried into the local backlog, explicitly labeled as
source-checkout observations with no implementation authority, and preserved
verbatim as source-backlog-working-draft.md.txt. Source config edits were not imported. The sibling checkout remains untouched as preserved provenance,
not a second active planning home.

## Preserved work and evidence limits

All pre-existing TUI dirty files, including vision/PRD drafts, are protected by
before/after hashes. They are not included in the reconciliation commit. The
three pre-existing dirty source files remain unchanged in their source checkout.
A local external backup and full import hashes are recorded in the manifest.
No branch history is rewritten and no blanket branch merge is performed.

The command source branch contains earlier MCP source changes that are not
imported. Destination product code has its own baseline, including TUI evolution.
The manifest classifies each of 84 source/test evidence hashes as matching,
different or absent here. Imported 826/155 suite counts and review verdicts are
historical source-checkout evidence only. Do not overwrite historical snapshots
by running their capture scripts locally. New local baseline evidence must be
written separately and reviewed before a construction directive is approved.

## Validation and next step

Validate the local board/dashboard, documentation lifecycle, relative links,
import/source archive hashes, protected dirty files and unchanged product bytes.
Scope and stage only the explicit reconciliation paths. No broad runtime suite
rerun establishes historical source parity for a documentation import.

Use the [local design request](../approval/foundation-design.md) as the entry
point for further planning. First confirm this location/authority reconciliation
and its evidence limitations; prior reviews do not verify the changed authority.
Finish remaining local P0/P1 and obtain the required design/directive decisions
before product construction. Source directories and unrelated dirty changes
require separately scoped work; they are not silently folded into planning.
