# Legacy Policy Debt Backlog

## Purpose

This document tracks known legacy violations against the canonical repository policy in [repository-engineering-policy.md](/Users/chuckrussell/Dev/gendev/agent-framework/docs/policies/repository-engineering-policy.md).

It exists to:

- prevent new policy debt from being introduced casually
- make existing debt explicit rather than implicit
- prioritize cleanup by package risk and architectural impact
- separate governed legacy debt from acceptable policy-compliant code

This is a seeded backlog, not yet a full repository audit.

## Current Status

This backlog is based on categories and concrete violations already uncovered during:

- repo-wide and scoped `mypy` passes
- Phase 4 implementation work
- follow-on policy and typing review

It is currently:

- partially inventoried
- strongest on non-integration typing debt
- incomplete for `tests/integration`
- incomplete for semantic-drift categories that require architecture review rather than tool output alone

## Prioritization Rules

### Package Priority

Repair order should generally follow this package priority:

1. `friday-runtime`
2. `friday-agent`
3. `friday-core`
4. `friday-memory`
5. `friday-cli`
6. `friday-tools`
7. remaining packages

### Violation Priority

Repair order should generally follow this violation priority:

1. essential runtime invariants enforced weakly
2. source-level blanket mypy suppressions
3. unstable cross-package contracts
4. repeated casts indicating abstraction drift
5. untyped or weakly typed public APIs
6. test-only typing debt

## Categories

## C1. Source-Level Blanket Typing Suppression

Definition:

- source files under `packages/*/src` using `# mypy: ignore-errors` or equivalent broad suppression

Why it matters:

- hides real regressions
- prevents meaningful static analysis
- allows architectural drift to accumulate silently

Current known baseline from this session:

- approximately `241` source files carry `# mypy: ignore-errors`

Priority:

- `P0` for core runtime and boundary packages
- `P1` for active source packages
- `P2` for older legacy source modules

## C2. Test-Local Mypy Relaxations

Definition:

- package test files using local mypy directives that relax strictness for pytest ergonomics

Why it matters:

- lower risk than source suppression
- still useful to track so test debt does not silently become permanent

Current known baseline from this session:

- approximately `130` test files carry local mypy relaxations

Priority:

- `P2`

## C3. Weak Runtime Invariant Enforcement

Definition:

- code relying on `assert` where explicit exceptions or validation should enforce lifecycle or configuration invariants

Why it matters:

- runtime guarantees become weaker than intended
- invariants are less explicit at boundary failures
- design intent gets encoded as type-narrowing rather than stable runtime contract

Priority:

- `P0`

## C4. Repeated Cast-Based Boundary Narrowing

Definition:

- repeated `cast(...)` usage where protocol or interface design should carry the contract instead

Why it matters:

- often signals abstraction drift
- repeated local narrowing increases maintenance cost
- can hide mismatches between concrete implementations and declared interfaces

Priority:

- `P1`

## C5. Weak Cross-Package Data Contracts

Definition:

- unstructured or weakly typed data crossing package boundaries
- especially `dict[str, Any]` used as long-lived contract surfaces

Why it matters:

- allows semantic drift without obvious failures
- weakens both static typing and runtime validation

Priority:

- `P1`

## C6. Cross-Package Internal Reach-Through

Definition:

- packages depending on implementation details from other packages instead of stable interfaces or public modules

Why it matters:

- makes refactors unsafe
- increases hidden coupling
- turns local changes into cross-package break risks

Priority:

- `P1`

## C7. Legacy Test Debt Blocking Meaningful Typing

Definition:

- test suites whose annotation debt or dynamic fixtures dominate mypy signal

Why it matters:

- encourages pressure to weaken repo-wide typing instead of fixing source boundaries first

Priority:

- `P2`

## Seeded Backlog

| ID | Package / Scope | Category | Priority | Current State | Recommended Action |
|---|---|---|---|---|---|
| LPD-001 | `packages/friday-runtime/src` | C3, C4 | P0 | recent runtime work uses narrowing patterns that should be reviewed under the new policy | replace essential `assert`-only invariants with explicit exceptions where appropriate; reduce repeated cast patterns by improving interfaces |
| LPD-002 | `packages/friday-agent/src` | C4, C6 | P0 | agent/runtime boundaries still rely on interface narrowing in key paths | review protocol coverage for agent runtime interfaces and remove repeated casts where interface changes are cleaner |
| LPD-003 | `packages/friday-core/src` | C5, C6 | P0 | core interfaces define the boundary contracts but still contain weak areas | tighten interface surfaces and ensure core contracts are the stable import point across packages |
| LPD-004 | `packages/friday-memory/src` | C1, C5 | P1 | large legacy source area currently under broad source suppression | remove blanket source suppression incrementally, starting with controller, context, lifecycle, and maintenance boundaries |
| LPD-005 | `packages/friday-cli/src` | C1, C5 | P1 | CLI compatibility and session/config surfaces still depend on legacy source suppression | recover typed boundary behavior for session, configuration, and compatibility adapters |
| LPD-006 | `packages/friday-tools/src` | C1, C6 | P1 | broad source suppression and dynamic tool contracts | recover typed tool base contracts, especially override correctness and boundary adapters |
| LPD-007 | `packages/friday-memory/tests_memory` | C2, C7 | P2 | local mypy relaxations used to stop pytest annotation debt from dominating signal | keep local relaxations for now; revisit only after source debt is reduced |
| LPD-008 | package test trees outside integration | C2, C7 | P2 | similar local relaxations used to preserve source-level progress | maintain as controlled debt, not a reason to weaken source typing |
| LPD-009 | non-integration source files with `# mypy: ignore-errors` | C1 | P0/P1 depending on package | explicit policy debt introduced to restore signal quickly | inventory by package and remove in package-priority order |
| LPD-010 | cross-package structured data using loose dictionaries | C5 | P1 | known pattern across memory, tools, CLI, and transcript flows | identify durable data contracts and replace with Pydantic models or typed dataclasses |
| LPD-011 | repeated protocol casts at runtime composition boundaries | C4 | P1 | known in runtime/agent/CLI composition paths | decide where casts are justified and where interface definitions must be widened or corrected |
| LPD-012 | `tests/integration` | audit gap | P1 | not included in current remediation pass by explicit instruction | perform separate policy audit later; do not let this area drive immediate source-policy weakening |

## Known Quantitative Baseline

These numbers are from the current session and should be treated as initial baseline data, not a permanent metric source:

- repo-wide `mypy` backlog originally measured at `2738` errors in `233` files
- approximately `86%` of that backlog was test-side
- highest debt concentration was in:
  - `friday-memory`
  - `tests/integration`
  - `friday-tools`
  - `friday-agent`
  - `friday-cli`

This backlog document is meant to govern cleanup, not to preserve those exact counts indefinitely.

## Immediate Remediation Strategy

### Phase A

1. Stop introducing new source suppressions.
2. Treat all current source suppressions as governed legacy debt.
3. Apply the policy strictly to new and materially changed source files.

### Phase B

1. Remove source suppressions from `friday-runtime`, `friday-agent`, and `friday-core`.
2. Review essential runtime invariants and replace weak `assert` patterns with explicit exceptions where required.
3. Identify repeated cast hotspots and convert them into interface improvements.

### Phase C

1. Remove source suppressions from `friday-memory`, `friday-cli`, and `friday-tools`.
2. Tighten cross-package data models.
3. Address test typing debt only after source typing is meaningfully restored.

## Audit Gaps

The following still need dedicated review passes:

1. `tests/integration`
2. semantic-drift risk not visible from static typing alone
3. cross-package internal import reach-through across the whole repo
4. persisted format and schema versioning gaps
5. explicit waiver records for currently tolerated violations

## Usage Rules

This backlog should be updated when:

1. a legacy violation is discovered
2. a violation is removed
3. a waiver is granted
4. a package priority changes

A backlog item is not considered resolved until the underlying policy violation is actually removed or formally waived.
