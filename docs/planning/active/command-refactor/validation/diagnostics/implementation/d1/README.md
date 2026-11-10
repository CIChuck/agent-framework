# DIAG-001 D1 — independently VERIFIED

Execution phase: closeout. Validation state: verified (bounded D1 only).
[Council reconciliation](verified-report.md) records all three round2 members
VERIFIED9.7 at `409926b6`, independently closing both findings.
[Raw round2 reports](council-round2.json), [correction evidence](test-coverage-fix-evidence.json)
and earlier checkpoints remain preserved. Approved D2 proceeds after controller
reconciliation; DIAG acceptance and delivery are not granted.

## Historical D1 correction and review checkpoints

# DIAG-001 D1 — corrected test coverage, cycle1/round2

Execution phase: validation. Validation state: in_review (fresh round2).
The [bounded remediation](../../../../remediation/REM-CMD-DIAG-D1-001-test-coverage.md)
is implemented pending fresh independent closure. Test source: `e2f514a66407bf5da9868e586ca6cdf30bdadefb`;
runtime/models/exports remain equal to `7cab1f0f`. Only the new DIAG test changes
outside documentation against the reviewed round-one candidate.

[Current correction evidence](test-coverage-fix-evidence.json) and
[exact node/family coverage map](test-coverage-map.json) supplement the preserved
original evidence and [round-one reports](council-round1.json).

| Gate | Exact node | Cases |
| --- | --- | --- |
| DG-T01 | `test_diagnostic_models_and_closed_union` | 109 |
| DG-T02 | `test_diagnostic_specs_exports_and_factory` | 1 |
| DG-T03 | `test_diagnostic_invocation_validation_order` | 6 |
| DG-T04 | `test_context_prompt_flags_and_export_order` | 51 |
| DG-T05 | `test_diagnostic_snapshots_once` | 9 |
| DG-T06 | `test_retrieval_precedence_and_await` | 21 |
| DG-T07 | `test_diagnostics_standalone` | 3 |

All200 cases now run under the seven exact gate names. Twenty-four original
helper bodies preserve their assertion AST. DG-T02 retains the exact ordered
API38 list and checks every binding against its owning module. Standalone normal,
-O and -OO now check intended source origins explicitly before and after use.

Full Commands/cohort478 and named200 pass. Each of the five named mutations
passed the pre-fix45 selection; corrected named200 rejects preview cap11,
permissive nested fields, non-bool availability, query mismatch and old-registry
rebinding through test-call assertions. All14 original full-suite mutants are
refused again; unchanged private full control478 passes. Start/session-finish/
end canonical module roots and hashes match; no setup failure supplies credit.
Candidate-export offline lock passes, addressing A-1. A-2 origin checks pass.

Runtime, other tests, existing SESSION literal append, Chat/dependencies/lock,
frozen authority and dirty examples are unchanged. Current root collection6868
still has only the known test_display conflict; root Ruff534 and registry-format
debt remain failed/unwaived. D2/D3/UAT/acceptance are deliberately pending.

Next gate: fresh Sol/Astra/Claude delta then full bounded D1 round2, followed by
controller reconciliation before D2. The following earlier checkpoints retain
historical labels and do not represent a current independent verdict.

## Historical round-one remediation checkpoint

# DIAG-001 D1 — council remediation checkpoint

Execution phase: remediation. Validation state: changes_requested (cycle1).
[Round-one reconciliation](council-round1.json) records Sol/Astra VERIFIED9.7 and
Claude CHANGES_REQUESTED8.4. Two mandatory test-evidence gaps require
[test-only correction](../../../../remediation/REM-CMD-DIAG-D1-001-test-coverage.md)
and fresh round2 before D2. Product code is unchanged; original evidence below
is historical for the reviewed test bytes and remains preserved.

## Historical original D1 builder checkpoint

# DIAG-001 D1 — neutral diagnostics implementation

Execution phase: validation. Validation state: in_review (D1 council round 1).
This is builder evidence, not an independent verdict or maintainer acceptance.

The [exact approval](../../../../approval/diagnostics.md) governs the frozen
[contract](../../../../diagnostics-command-contract.md) and
[directive](../../../../directives/CD-CMD-DIAG-001-context-diagnostics.md),
despite their preserved preapproval labels. Construction base: `b2f5b8f01f6b177c0a9519ff000036599417ad6e`;
product source: `7cab1f0f90a868a34de3faa4f763ce3b31352f8b`. Subsequent candidate changes are evidence/status only.

D1 adds eleven immutable models, seven closed data alternatives, fourteen appended
exports and six opt-in handlers. Factory construction makes no port reads;
handlers enforce request/execution/name order, exact flags, count-before-export,
strict typed snapshots and runtime-before-usage with one awaited retrieval.
No Chat DIAG implementation or dependency/lock change is part of this deliverable.

[Evidence](evidence.json), [preservation](preservation.json),
[before inventory](before-inventory.json) and [source observations](observations.json)
record exact raw receipts and hashes:

- D0: 1297 Chat / 278 Commands-cohort / 155 CLI passes; six DIAG metadata records,
  72 DIAG / 25 SESSION / 196 pilot observations; guard18/comparator10 refusals,
  extra/changed-source refusals and precise prebuild extra-data refusal.
- D0 closed baseline bundle: 13 workspace builds, 125 lock-verified raw inputs,
  154 artifact hashes, isolated neutral/default-Chat installs. Baseline machinery
  only; candidate installed-DIAG proof is D3.
- Current D1: **478 Commands/cohort passes**, including **200 new DIAG cases**.
  Current Chat1297 / CLI155 regressions also pass. Scoped Ruff, five-file format,
  ten-source-file mypy, metadata and offline lock checks pass.
- All 14 final private mutants have named test-call assertion witnesses with
  stable canonical module roots/hashes before, at session finish and afterward.
  Unchanged private control passes 478; no setup/import failure earns credit.
- Source captures at the actual product commit match all 72/25/196 observations.
  DIAG Chat handlers remain legacy until D2, so all 72 match without activating
  the approved four-cache-refusal comparison option.
- 1245 protected original non-documentation files match; 279 old test files
  retain 3028 test-prefixed definitions and 9190 assertions. The sole old-test
  exception is the exact fourteen-name export-list append; all remaining AST is
  identical. Earlier package/test/metadata ownership remains preserved.

Known root Ruff534, sole Chat/CLI test_display root collection error and legacy
registry-format failure remain failed and unwaived. Collection is 6868 = 6668+200.
Historical fixture-order/style attempts and intermediate passes are labeled;
only the final receipts support current gates.

Next: fresh read-only Sol/Astra/Claude council and controller reconciliation
before D2. D2 host projections/export effects and D3 candidate artifacts/installed
DIAG proof remain intentionally pending; DG-T08–14 are not D1 completion claims.
The manual UAT roadmap remains NOT RUN. No acceptance, later-family/TUI or
external delivery authority follows this evidence.
