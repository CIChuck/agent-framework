# Repository Engineering Policy

## Purpose

This policy defines how the Friday Agent Framework evolves without semantic drift.
It exists to preserve:

- stable package boundaries
- explicit runtime invariants
- meaningful static typing
- compatibility across dependent packages
- safe use of AI-assisted code generation

This document is the canonical repository engineering policy for the codebase.

Known legacy violations and phased remediation are tracked in [legacy-policy-debt.md](/Users/chuckrussell/Dev/gendev/agent-framework/docs/policies/legacy-policy-debt.md).

## Scope

This policy applies to:

- all source code under `packages/*/src`
- repository entrypoints such as `main.py`
- package test trees under `packages/*/tests_*`
- top-level tests under `tests/`
- architecture and design documents when they define implementation contracts

## Policy Order

When rules conflict, apply them in this order:

1. explicit developer and maintainer instructions in the active task
2. this repository engineering policy
3. `AGENTS.md`
4. local package conventions

## Design Principles

The repository follows these principles:

1. Cross-package behavior must be governed by explicit contracts, not incidental implementation details.
2. Runtime safety must not depend on static typing alone.
3. Static typing must remain meaningful; suppressions must not become the default solution.
4. Boundary APIs must be narrower and more stable than implementation internals.
5. AI agents must obey the same engineering rules as human contributors.

## Package Boundary Rules

### Public Surfaces

Cross-package usage should go through stable public modules, interfaces, or documented package APIs.

Avoid:

- importing another package's internal implementation files when a stable API exists
- passing unstructured data across package boundaries when a typed model should exist
- coupling package behavior to undocumented side effects

Prefer:

- `Protocol` or interface-based dependencies
- Pydantic models or typed dataclasses for exchanged data
- explicit factory, registry, and adapter interfaces

### Boundary Changes

Any change that alters a package contract should include:

1. a summary of the contract change
2. the affected upstream or downstream packages
3. validation evidence
4. migration notes if behavior changed

## Typing Policy

### Source Code

Source files under `packages/*/src` and repository entrypoints must preserve meaningful type checking.

Required:

1. Public and semi-public functions must have explicit return annotations.
2. Cross-package boundary functions and constructors must use explicit typed contracts.
3. New code must not introduce `Any` unless it is justified at a dynamic boundary.
4. Repeated casts across a boundary should trigger interface review.

Forbidden in source by default:

1. `# mypy: ignore-errors`
2. broad file-level or package-level suppression used as a substitute for actual fixes
3. new global weakening of mypy settings to bypass package debt

Allowed in source only with an approved waiver:

1. local suppression with owner, reason, issue reference, and cleanup plan
2. temporary compatibility shims that are explicitly documented

### Test Code

Test code may use lighter typing standards than source code, but only intentionally.

Allowed in tests:

1. local mypy relaxation where pytest fixture ergonomics make strict signatures low value
2. narrow suppressions around dynamic test doubles and mocks

Not allowed in tests:

1. broad repository-wide weakening of typing rules because of test debt
2. using test debt to justify source suppressions

## Runtime Invariant Policy

Essential runtime invariants must be enforced explicitly.

Preferred:

```python
if controller is None:
    raise RuntimeError("Memory controller not initialized")
```

Avoid using `assert` as the sole enforcement mechanism for essential runtime guarantees.

`assert` is acceptable only when all are true:

1. the condition is an internal invariant, not an external input contract
2. failure represents a programmer error
3. the code would remain semantically correct if assertions were disabled

Use explicit exceptions instead of `assert` for:

1. lifecycle requirements
2. configuration validity
3. external or user-controlled inputs
4. persistence and workflow invariants

## Cast Policy

`cast(...)` is allowed only as a last-mile narrowing tool.

A cast is acceptable when all are true:

1. the runtime invariant already exists
2. mypy cannot prove the invariant from local context
3. the cast narrows to the actual contract expected at the boundary

Before adding a cast, prefer:

1. explicit validation
2. explicit exceptions
3. stronger interface definitions
4. more precise field or attribute types

If the same cast pattern appears repeatedly, that is a design issue and should be replaced by an interface or API improvement.

## Data Contract Policy

Structured data that crosses package boundaries should use typed models.

Prefer:

1. Pydantic models for validated external and persisted data
2. typed dataclasses for simple internal structured values
3. narrow typed dictionaries only when models are not appropriate

Avoid:

1. unstructured `dict[str, Any]` as a long-lived contract
2. implicit schema evolution without versioning or migration notes

## Semantic Drift Prevention

Static typing is necessary but not sufficient.

The repository must also use:

1. contract tests for boundary behavior
2. regression tests for existing semantics
3. explicit versioning or migration notes for important persisted or external formats
4. design-document updates when architectural contracts change

Code that still type-checks but changes a documented package contract without updating tests or docs is a policy violation.

## CI and Validation Expectations

At minimum, changes should preserve the relevant validation gates:

1. `uv run ruff check .`
2. `uv run pytest`
3. `uv run mypy ...` for the affected scope

When changing package boundaries, contributors should also run the narrowest meaningful validation for the impacted packages.

Repository-wide mypy remains a desired gate, but legacy debt must be handled through explicit cleanup work, not hidden by blanket source suppressions.

## AI Agent Compliance

AI coding agents working in this repository must:

1. treat this document as binding repository policy
2. prefer real fixes over suppressions
3. stop and report when a requested change conflicts with policy
4. identify any waiver-like behavior explicitly in the final summary
5. avoid hiding source typing failures with blanket ignores

AI agents must not assume that passing CI alone is sufficient if the change violates an explicit policy rule.

## Waiver Process

Any exception to this policy must be explicit.

A waiver must include:

1. scope
2. reason
3. owner
4. issue or follow-up reference
5. intended cleanup point

Absent an explicit waiver, the default policy applies.

## Review Checklist

Before merging a change, reviewers should ask:

1. Did this change alter a package contract?
2. Was the contract expressed through typed interfaces or models?
3. Were runtime invariants enforced explicitly?
4. Were casts justified by real invariants?
5. Did the change add any source suppressions?
6. Was there any semantic drift not covered by tests or docs?

If the answer to any of those questions is unclear, the change is not ready.
