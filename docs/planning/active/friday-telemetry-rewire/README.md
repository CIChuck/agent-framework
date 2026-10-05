# Friday-telemetry-rewire

---
title: Friday-telemetry-rewire
initiative: friday-telemetry-rewire
document_type: initiative-index
status: approved
work_state: started
condition: normal
created: 2026-10-01
updated: 2026-10-05
next_gate: validate Python 3.13.4 support migration and resolve remaining AC-06 baseline gates; no waiver approved
execution_phase: remediation
validation_state: changes_requested
implementation_authority: granted
---

The maintainer approved the telemetry plan and preparation of its first
implementation slice on 2026-10-04 (conversation: "approved"). The dedicated
preparation branch is `feature/friday-telemetry-rewire`, based on
`2155a0fc51f5b20dea4e35c6cfc70f1d52002735`. No construction directive existed
at that approval. The specific [CD-001 directive](directives/CD-001-local-telemetry-assembly.md)
was explicitly approved on 2026-10-05 by the maintainer's "proceed".

The `tests/integration/memory/friday.py` launcher configured a LiteLLM
Langfuse callback and separately supplied an in-memory telemetry recorder to
the memory controller. Friday already has a provider-neutral
`TelemetryInterface` with debug, OpenTelemetry, and composite adapters. The
extracted `friday-chat` CLI does not assemble that interface into an end-to-end
path. The [build plan](build-plan.md) records the historical behavior,
current adapter capabilities and defects, proposed contract, and acceptance
criteria. Langfuse is one optional integration, not the target architecture.

The [first-slice contract](telemetry-contract.md) specifies approved local
configuration, ownership, privacy, and failure behavior. The [tactical plan](tactical-plan.md)
orders subsequent work and maps CD-001 requirements to tests. The
[execution log](execution-log.md) records approval, the baseline, and preserved
local changes. Remote exporters and optional Langfuse compatibility are later
work units. Existing `.friday` data is outside every first-slice operation.

The board records execution as `started` on the named branch under approved
CD-001. Later units require separate construction authority.

Independent [VAL-001](validation/VAL-001/report.md) returned `CHANGES_REQUESTED`
for a provider-replacement span-ID collision. [REM-001](remediation/REM-001-directive.md)
is approved by the maintainer's "i Approve your recommendations. Continue."
The separate [WVR-001 proposal](validation/WVR-001-baseline-pty-timing.md) remains
unapproved: fix the collision and rerun first, then consider a waiver if needed.

The maintainer approved the verification-only A01 amendment after the independent
[directive review](validation/CDR-001/report.md). The approved
[verification profile](verification-profile.md) reconciles repository checks and
advertised Python 3.10 compatibility evidence. Fresh [CDR-002 directive readiness review](validation/CDR-002/report.md)
returned `READY` for frozen authority candidate `6013be5`. Existing implementation validation remains unresolved; changing
controlling authority requires fresh subsequent implementation review.

CD-001 A02 records the approved collision identity amendment. Its fresh readiness
review precedes bounded REM-001 source generation; subsequent independent product
review must assess the delta and aggregate TELEM-01 under all A01 checks.

[CDR-003](validation/CDR-003/report.md) returned `READY` for A02. Approved REM-001
is implemented and builder checks are in the
[remediation report](execution/REM-001-implementation-report.md). Independent [VAL-002](validation/VAL-002/report.md) supports the collision
remediation and AC-01 through AC-05, with 135 focused tests and 10 new probes
passing. Aggregate verdict is `CHANGES_REQUESTED` for VAL-002-F01: identical
baseline lint, collection, timing and listener failures remain unwaived.
Actual Python 3.10 package smoke cannot import missing pydantic. No implementation
VERIFIED or task completion is claimed. The maintainer approved
[REM-002 verification setup](remediation/REM-002-verification-directive.md) on
2026-10-05. Fresh A03 readiness review precedes execution. No lint or timing
waiver is approved; product source/tests remain frozen at `3a69050`.

[CDR-005](validation/CDR-005/report.md) returned READY for corrected A03.
Approved REM-002 setup/reruns are recorded in the
[execution report](execution/REM-002-implementation-report.md). Root collection
is complete, three permitted localhost tests pass, and all broad failures match
baseline. The frozen3.10 dependency set installs but genuine imports fail on
LiteLLM typing.NotRequired, identically at base/candidate. No dependency change,
waiver or runtime3.10 PASS is claimed. Fresh independent [VAL-003](validation/VAL-003/report.md) returned
CHANGES_REQUESTED for sole finding VAL-003-F01. The
[REM-002 execution closeout](execution/REM-002-closeout.md) records completed
actions, standalone Composite3.10 PASS and unresolved aggregate gates.
No task completion, acceptance or waiver is claimed.

The maintainer's "Make it happen." approves [REM-003](remediation/REM-003-python-minimum-directive.md)
and CD-001 A04: require Python >=3.13.4 across the workspace and align tooling,
lockfile and current setup docs. Prior 3.10 evidence remains historical; the
new support policy removes that obligation without waiving other AC-06 failures.
Fresh readiness review precedes implementation, then fresh candidate review.

[CDR-006](validation/CDR-006/report.md) returned READY for A04. The approved
[REM-003 implementation](execution/REM-003-implementation-report.md) now aligns
all18 project minimums and tooling/setup with Python >=3.13.4. Frozen dependency
versions remain unchanged; candidate verification and fresh independent review
are pending. All other aggregate AC-06 failures remain unresolved.

[VAL-004](validation/VAL-004/report.md) requested exact grpcio selection
preservation and retained unwaived aggregate failures. A bounded lock correction
preserves existing supported-runtime selections across24 graph contexts. Fresh
review of the new stable candidate follows; no source/test/authority changes.
