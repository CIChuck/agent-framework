# CMD-DESIGN-001 — Sol-only council, round 1

Outcome: CHANGES_REQUESTED — design approval readiness
Reviewed HEAD: fa94f180e95ba75022e81bb269b18543e6360e38
Date: 2026-11-04

Scope: read-only evaluation of the foundation approval artifact and supporting
API/directive, AP-01–AP-06. Three distinct Sol versions at high reasoning effort,
as expressly requested by the maintainer; this is not a three-provider council.

## Results

| Reviewer | Verdict | Advisory score |
| --- | --- | --- |
| GPT-6.1 Sol | VERIFIED | 9/10 |
| GPT-6 Sol | VERIFIED | 9/10 |
| GPT-5.6 Sol | CHANGES_REQUESTED | 7.8/10 |

Scores are advisory. Positive verdicts do not dispose of mandatory findings.
The complete reviewer responses were returned to the parent thread and are
available in their respective delegated review threads.

## Mandatory corrections

1. **SOL3-ARCH-001, medium:** Specify runtime enforcement at the public model
   boundary: payload/error/effect types, permitted error codes, immutable
   collection conversion and member validation, request/spec name coherence,
   and exact exception classes. Bind independent constructor-negative fixtures.
2. **SOL3-ARCH-002, medium:** Specify normalization/storage for a preconstructed
   CommandSpec: canonical metadata reconstruction, trimming, blank-alias and
   argument-field behavior, normalized collision checks and atomicity. Ensure
   names(), resolve(), specs() and dispatched requests share canonical identity.
3. **SOL3-ARCH-003, low:** Correct current six-retirement instructions to nine,
   and label superseded passages while preserving raw scoring history.

Affected documents: shared-command-api.md (runtime model and registration
sections), directives/CD-CMD-FND-001-neutral-foundation.md (negative proof),
test-strategy.md:18, command_refactor.md:42 and command-inventory.md:338.

Controller inspected the actual API text, current Chat registration algorithm
and stale count passages at the unchanged reviewed HEAD. The first two identify
contract precision gaps: the model table primarily states static types, and
canonical stored-spec construction is not fully specified. The stale instructions
are directly reproducible. Corrections fit the existing decided scope.

## Disagreement and advisory feedback

SOL2 treats stale retirement wording as advisory because the dated supersession
notice and scope register control; SOL3 treats the current instruction as a
mandatory inconsistency. It remains recorded for correction rather than waived.
SOL1/SOL2 did not report the constructor/canonicalization gaps.

SOL1 and SOL3 recommend explicit multi-slash and normalization-order fixtures,
including //HELP and ///HELP, with expected tokens derived independently of
the new registry. This can accompany the bounded fixture clarification.

## Evidence and boundaries

All reviewers verified the candidate, 19 manifest entries and four supplied
pins, board validation (36 tasks), documentation lifecycle (682 Markdown files)
and whitespace checks. They preserved the three pre-existing dirty inputs.
Historical 54-case production and 826/155 suite evidence was inspected, not
represented as newly executed code tests.

This consolidated report is review output only. No governed design, source,
test or configuration was changed, no finding was remediated, and no re-review
was dispatched. P0/P1 closure, construction, installed-client/live-provider proof,
maintainer approval, acceptance and delivery remain separately gated.

Next: bounded documentation corrections, then fresh review of the revised
candidate before requesting CMD-DESIGN-001 approval.
