# REM-002 Delivery-State Preservation Construction Directive

Status: implemented; independent validation pending

## Authority Required

The repository maintainer explicitly approved this directive and its bounded
source/test scope on 2026-09-03. No authority is granted beyond the allowed
scope, verification, and closeout artifacts below.

## Source Finding

- `VAL-002-F01`
- [VAL-002 report](../validation/VAL-002-report.md)
- [VAL-002 evidence](../validation/VAL-002-evidence.yaml)

## Objective

Make work-state reopening preserve independent delivery facts. A
`completed -> started` transition must not downgrade `delivery_state` from
`pushed`, `merged`, `released`, `local`, or `unknown` to `local`.

## Allowed Scope

- `scripts/friday-dev-board.py`
- `tests/integration/test_development_board.py`
- This initiative's execution, validation, remediation, and closeout artifacts

## Required Implementation

1. When starting work for the first time, promote `delivery_state: not_started`
   to `local`.
2. When reopening completed work, preserve the existing delivery state.
3. Preserve the dedicated delivery command's rejection of backward movement.
4. Preserve maintainer-only approval and acceptance gates.
5. Do not change work-state, condition, packet-placement, or delivery-state
   enumerations.

## Required Tests

- Initial `approved -> started` promotes `not_started` to `local`.
- Reopened `completed -> started` preserves `local`.
- Reopened `completed -> started` preserves `pushed`.
- Reopened `completed -> started` preserves `merged`.
- Reopened `completed -> started` preserves `released`.
- Reopened `completed -> started` preserves `unknown`.
- Existing backward-delivery rejection remains effective.

## Verification

- focused tests for `test_development_board.py`;
- full `tests/integration` suite;
- focused Ruff and mypy for the board script and test;
- board and documentation lifecycle validation;
- aggregate `git diff --check`; and
- a new frozen candidate, request, and fresh aggregate review.

## Non-Goals

- Do not change the independent-validation policy or its accepted decisions.
- Do not implement machine board fields for execution or validation state.
- Do not refactor unrelated board commands or schemas.
- Do not touch package source, guides, runtime configuration, provider state, or
  unrelated worktree files.

## Stop Conditions

Stop and return to the maintainer if the fix requires schema changes, changes a
documented state meaning, expands beyond the two allowed files, weakens an
authorization gate, or reveals another delivery-history inconsistency.
