# Independent Validation Policy

## Purpose

This policy defines the independent validation gate between implementation and
maintainer acceptance for Friday engineering work. It prevents an implementation
agent from approving its own work and makes conformance, remediation, and
acceptance evidence durable and reproducible.

This policy supplements the
[repository engineering policy](repository-engineering-policy.md) and the
[development task lifecycle policy](development-task-lifecycle.md). It cannot
waive either policy.

## Scope

The policy applies to generated or human-written product code, tests, package
metadata, runtime configuration, migrations, and other changes whose failure
could alter behavior. Documentation-only, spelling-only, generated-file, and
dependency-lock work may use the lightweight-change exemption described below.

Independent validation is required before qualifying applicable work as
`completed`. A validation result is not maintainer acceptance and does not grant
merge, push, release, deployment, credential, or external-system authority.

### Adoption Boundary

The construction-directive gate applies prospectively to code generation that
starts after this policy is adopted. Work generated before adoption does not
require a retroactive directive when the packet records its controlling build
and tactical plans, implementation history, and maintainer-approved adoption
exception. Such work must still receive an aggregate independent review before
acceptance if it remains on an unaccepted feature branch.

## Roles And Separation

The workflow separates five responsibilities:

1. The maintainer approves scope and retains final acceptance authority.
2. The controller or supervising agent freezes authority, dispatches work,
   verifies review completeness, and records repository-visible state.
3. The builder implements one bounded construction directive.
4. The independent validator reviews a frozen candidate without modifying it.
5. The remediator resolves only numbered findings under a bounded remediation
   directive.

One agent may perform controller and builder duties only when the resulting
candidate is reviewed by a fresh validator. The validator must not approve its
own implementation or remediation and must not silently repair the candidate it
is reviewing.

## Authority Chain

Use the following precedence when the artifacts exist:

1. explicit maintainer direction for the active task;
2. repository engineering and security policies;
3. accepted product, architecture, and governance specifications;
4. the approved phase or feature build plan;
5. the approved tactical implementation plan;
6. the work-unit construction directive; and
7. recorded amendments or waivers within their stated scope.

Lower-level artifacts must not silently override higher-level authority. If the
artifacts conflict, implementation and validation stop until the conflict is
reconciled by the appropriate authority.

## Construction Directive Gate

Every code-generating work unit must have an approved construction directive
before product code is generated or modified. The directive must identify:

- controlling authority and precedence;
- objective and acceptance criteria;
- allowed files, packages, and boundaries;
- explicit non-goals and deferred behavior;
- required implementation and migration behavior;
- security and configuration constraints;
- required positive, negative, regression, and integration tests;
- verification commands and permitted external services;
- documentation and configuration closeout;
- reporting requirements; and
- stop conditions.

A broad build plan is not a substitute for a work-unit directive. A directive
may cover one bounded phase or work stream, but it must be narrow enough to
detect scope drift.

### Lightweight-Change Exemption

Documentation-only, spelling-only, generated-file, or dependency-lock changes
may proceed without a construction directive when the packet records:

- the maintainer who authorized or accepted the exemption;
- the date, reason, and exact scope;
- why runtime behavior cannot change; and
- the validation appropriate to the change.

If implementation reveals source, test, runtime, package-contract, or behavioral
work, the exemption ends. Stop and obtain a construction directive before
continuing.

## Candidate Freeze

Formal validation begins only after the builder creates a stable candidate
commit. The controller prepares a validation request containing:

- board initiative and work-unit IDs;
- base and candidate commit hashes;
- the exact diff range;
- authority-document paths, revisions, and content hashes;
- tactical task and acceptance-criterion IDs;
- required validation commands;
- explicit exclusions and known baseline failures;
- permitted credentials, live-provider tests, costs, and external effects; and
- the required review mode.

The validation request may embed the authority manifest or reference a separate
`authority-manifest.yaml`; either form must pin the same revisions and hashes.

Uncommitted work may receive advisory feedback but cannot receive a formal
`VERIFIED` result.

The initiative remains `started` while implementation, validation, or
remediation is underway. It becomes `completed` only after independent
validation is `VERIFIED` and the required evidence is recorded.

## Execution And Validation Tracking

Until automated board support is separately approved and implemented, every
active packet records these process fields in its index and execution log:

- `execution_phase`: `planning`, `implementation`, `validation`, `remediation`,
  or `closeout`; and
- `validation_state`: `not_ready`, `pending`, `in_review`, `changes_requested`,
  `blocked`, or `verified`.

The canonical board `next_gate` must agree with these packet fields. The board's
existing `validation` collection records completed evidence. Packet metadata is
process evidence; it does not create a new work state or grant authority.

## Independent Validator Requirements

A formal validator must:

- use a fresh agent context that does not inherit the builder's session;
- read `AGENTS.md`, applicable repository policy, the frozen authority manifest,
  the construction directive, and the candidate diff;
- review the current candidate rather than relying on the builder's summary,
  conclusions, private reasoning, or claims of passing tests;
- operate read-only against the candidate;
- avoid commits, pushes, board mutations, releases, deployments, or remediation;
- record reviewer identity, model/version when available, date, review mode,
  inputs, authority revisions, candidate revision, diff range, shared-context
  exceptions, commands, results, and residual risk; and
- support every `PASS` or `VERIFIED` assertion with cited source, requirement,
  or reproducible command evidence.

A different model is optional. A separate agent instance and fresh context are
mandatory. When practical, use a detached or otherwise isolated read-only
worktree at the candidate commit.

The validator may receive authorized environment variables through the test
environment but must never request, print, persist, or include secret values in
review artifacts.

## Review Scope

Use a work-unit review for each construction directive and an aggregate branch
review before merge.

- A **full review** evaluates all applicable authority, the complete selected
  diff, tests, documentation, configuration, and package boundaries.
- A **delta review** evaluates remediation for identified findings and checks
  that the remediation introduced no new drift.
- An **aggregate review** evaluates the complete feature-branch diff and the
  interaction among previously verified work units.

A delta review does not replace the aggregate review.

## Validation Outcomes

The validator must return exactly one outcome.

### VERIFIED

`VERIFIED` is permitted only when:

- every mandatory acceptance criterion has evidence;
- all required deterministic checks pass or an approved waiver covers them;
- no prohibited scope or package-boundary change exists;
- no violated mandatory requirement remains;
- no blocker, critical, or high-severity finding remains;
- baseline failures are separated from regressions;
- documentation and configuration implications are reconciled; and
- residual risk and advisory findings are recorded.

Low-severity advisory improvements may coexist with `VERIFIED` only when they do
not represent a violated requirement. An uncited `PASS` is advisory and cannot
support `VERIFIED`.

### CHANGES_REQUESTED

Use `CHANGES_REQUESTED` when the candidate violates authority or lacks required
evidence. Each finding must contain:

- stable finding ID;
- severity;
- affected files or modules;
- violated authority and exact requirement;
- evidence and observed problem;
- risk;
- required mitigation;
- required regression or verification coverage; and
- documentation or configuration impact.

### BLOCKED

Use `BLOCKED` when a defensible result cannot be reached because authority,
candidate stability, infrastructure, credentials, or acceptance criteria are
unavailable or contradictory. A blocked review is not a code failure. It must
identify the blocking condition, checks already performed, and the exact exit
gate.

## Remediation

The controller converts `CHANGES_REQUESTED` findings into a remediation
directive. Every finding appears exactly once with its required fix, tests,
documentation impact, acceptance criteria, and non-goals.

The original builder may perform bounded mechanical remediation. Use a separate
remediator for security, architecture, data integrity, package boundaries, or a
repeated failure. Remediation must not broaden scope or perform opportunistic
refactoring.

After remediation:

1. commit a new stable candidate;
2. mark the prior report superseded for decision purposes while retaining it as
   historical evidence;
3. start a fresh validator context against the new revision; and
4. perform a delta review followed by the required aggregate review.

After two unsuccessful remediation cycles, stop and return the unresolved
findings to the maintainer. Automated remediation may proceed only for bounded,
non-destructive findings that the maintainer preauthorized.

## Stale Review Rule

A formal review becomes stale when any reviewed code, test, configuration,
authority document, directive, or candidate revision changes after review
begins. Do not salvage or amend the stale conclusion. Stabilize the new
candidate and begin a fresh review.

Review evidence files added after a successful review may be inspected as
closeout metadata, but any change to the governed deliverable or authority
requires a new review.

## Required Artifacts

Applicable initiative packets use this structure as needed:

```text
authority-manifest.yaml
directives/
  CD-<id>-<work-unit>.md
execution/
  implementation-report.md
validation/
  VAL-<id>-request.yaml
  VAL-<id>-report.md
  VAL-<id>-evidence.yaml
remediation/
  REM-<id>-directive.md
closeout.md
```

The request and evidence formats may be machine-readable, but the report and
closeout must remain understandable without special tooling.

## External And Live Validation

Live-provider, paid, destructive, privileged, or externally visible validation
requires explicit authority identifying the permitted service and effects.
Validation authority does not authorize credential disclosure, external
messages, deployment, publication, or release.

Merge readiness, release readiness, and live-provider readiness are separate
profiles. Passing one does not imply the others.

## Acceptance Boundary

`VERIFIED` means the independent validation gate passed. It permits the
controller to propose the initiative as `completed`; it is not `accepted`.

Only the maintainer may accept completed work. Merge, push, release, deployment,
or publication remains separately authorized and tracked even after acceptance.
