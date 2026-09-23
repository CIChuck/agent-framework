# REM-003 Backward-Delivery Regression Construction Directive

Status: implemented; independent validation pending

## Authority Required

This is a third remediation cycle. The repository maintainer explicitly
authorized the exception to the independent-validation policy's two-cycle stop
on 2026-09-04. No authority is granted beyond the allowed scope below.

## Source Finding

- `VAL-003-F01`
- [VAL-003 report](../validation/VAL-003-report.md)
- [VAL-003 evidence](../validation/VAL-003-evidence.yaml)

## Objective

Supply the missing negative regression for the already implemented monotonic
delivery-state guard and correct the REM-002 implementation report.

## Allowed Scope

- `tests/integration/test_development_board.py`
- `execution/REM-002-implementation-report.md`
- VAL-003 remediation and revalidation artifacts

No board-script change is authorized or expected.

## Required Test

1. Establish a task with an advanced delivery state such as `merged`.
2. Invoke `set-delivery` with an earlier state such as `pushed`.
3. Assert exit code `1`.
4. Assert the message identifies forbidden backward movement.
5. Reload the board and assert the original delivery state is unchanged.

## Documentation Correction

Replace the unsupported claim that existing backward-delivery tests remained
passing with exact evidence that the negative regression was added and passed.

## Verification

- focused board tests;
- full integration suite;
- focused Ruff and applicable mypy profiles;
- board and documentation validation;
- aggregate diff and protected-scope checks; and
- a new stable candidate and fresh aggregate validator.

## Stop Conditions

Stop if the test reveals a behavior defect, any board-script change becomes
necessary, scope expands, or another validation failure occurs.
