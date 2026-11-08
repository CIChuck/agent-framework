# REM-CMD-DIAG-D1-001 — named test coverage and public binding identities

Cycle: 1. Reviewed base: `bc553cb097d3f62586b0d1808100bc186a5a67c9`.
Authority: existing [exact DIAG approval](../approval/diagnostics.md), DG-01–06,
DG-T01–07 and the repository independent-validation policy. This is bounded
mechanical completion of already-required tests in the approved allowlist;
no new construction approval or product behavior decision is needed.

The [round-one council](../validation/diagnostics/implementation/d1/council-round1.json)
reconciles to CHANGES_REQUESTED despite two VERIFIED reports. No reviewer found
a runtime defect. Current source models/API/handlers and frozen approvals remain
unchanged. D2 cannot start until a corrected D1 council is reconciled.

## VAL-D1-001 — complete each named test row

Only `packages/friday-commands/tests_commands/test_diagnostics.py` may change
outside current DIAG documentation/evidence/status. Fold the existing sibling
cases into parametrized tests with the exact seven DG-T01–07 node names, or
make those nodes directly exercise their full rows. Preserve the existing
positive/negative assertions; do not replace them with a coverage document.

DG-T01 must carry model validation order/types/values, closed union and old
alternatives, exact nested types, immutable once-only snapshots, recorded and
preview invariants. DG-T04 must carry count-before-export, invalid port results
and unchanged export/text failure/cancellation behavior. DG-T05 retains exact
snapshot/purity assertions and their failure propagation. DG-T06 must carry
exact-bool availability, pending/awaited behavior, invalid/mismatched results and
unchanged failures/cancellation. The other rows retain all mandatory assertions.

Record a DG-T→exact node/parameter-family map in current correction evidence.
Run only the seven named nodes in an unchanged private control and against
four private source mutants: preview cap 10→11, permissive nested DiagnosticField
members, missing exact-bool availability check and missing query-match check.
Every mutant must have a named test-call assertion witness; standard pytest
raises-check assertion failures count, setup/import/collection failures do not.
Verify canonical module origins/hashes before, at session finish and afterward.

## VAL-D1-002 — all 38 public bindings

In DG-T02 retain the independent literal ordered 38-name API assertion and add
identity checks for every export against its declared owning module: contracts,
registry, pilot, session_views or diagnostics. Do not limit the check to the
fourteen additions or derive expected bindings from the public API itself.

Privately append a same-name subclass rebinding of public `CommandRegistry` in
`__init__.py`. The corrected named node must fail by a test-call identity
assertion; the unmodified control must pass. Preserve all runtime bytes.

## Bounded advisories and verification

- A-1: run offline lock verification against a clean committed corrected
  candidate export, rather than the before-source export. Change no lock or
  dependency metadata.
- A-2: within the standalone test, explicitly verify the intended canonical
  package source origins in normal/`-O`/`-OO` execution, before and after use.

Use fresh external scratch/prepared runner and private caches. Preserve the
original D1 evidence, raw receipts, source captures and all three round-one
reports. New correction evidence records exact test before/after hashes, node
coverage, assertion preservation, positive and negative receipts and limits.

Rerun full Commands/cohort, the seven-node selection, focused Ruff/format, source
mypy, candidate offline lock, metadata, board/dashboard/docs, whitespace and
preservation audits. Record actual collected counts. Original tests outside
this new DIAG file, including the exact SESSION literal append, remain unchanged.
Do not modify models/handlers/exports, Chat, dependencies, configuration, frozen
contract/directive/preparation, accepted units or either dirty example file.

Freeze a stable new candidate and obtain fresh Sol/Astra/Claude delta then full
bounded D1 aggregate reviews. Prior verdicts are historical for changed test
bytes. Reconcile every mandatory finding before D2; escalate after two
unsuccessful cycles. No automatic DIAG acceptance or external delivery follows.
