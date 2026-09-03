# REM-001 Independent Validation Remediation Directive

Status: authorized bounded documentation remediation

## Authority

- `validation/VAL-001-report.md`
- `validation/VAL-001-evidence.yaml`
- `docs/reference/policies/independent-validation-policy.md`
- Maintainer authorization limiting this amendment to documentation and process
  updates

## Objective

Resolve `VAL-001-B01` and `VAL-001-F02` without changing source, tests,
automation, guides, runtime behavior, package metadata, or unrelated files.

## Finding VAL-001-B01

Required changes:

1. Assign stable `AC-01` through `AC-13` identifiers to the existing build-plan
   acceptance criteria without changing their meaning.
2. Assign stable `TP-01` through `TP-15` identifiers to the existing tactical
   tasks without changing their order or meaning.
3. Create a new validation request that explicitly enumerates those IDs and
   pins the new candidate revision and affected hashes.

Acceptance:

- every declared ID resolves exactly once in its controlling plan;
- every request ID maps to one controlling-plan requirement; and
- no ID is invented by the validator.

## Finding VAL-001-F02

Required changes:

1. Remove the superfluous blank line at EOF in
   `docs/dev-skills/independent-code-validator.md`.
2. Require the next aggregate `git diff --check` to exit `0` with no output.

## Non-Goals

- Do not change the substance of the accepted policy decisions.
- Do not alter board automation, schema, tests, package source, guides,
  configuration, entrypoints, workspace metadata, or runtime behavior.
- Do not address repository-wide Ruff baseline debt.
- Do not broaden remediation beyond the two named findings.

## Verification

- validate ID uniqueness and request-to-plan mapping;
- run board validation and documentation lifecycle validation;
- run the full integration suite;
- run aggregate `git diff --check`;
- confirm the amendment changes no protected path; and
- freeze a new candidate before dispatching a fresh-context aggregate validator.
