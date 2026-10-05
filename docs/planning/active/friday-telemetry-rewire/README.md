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
next_gate: fresh A02 directive review; implement approved REM-001 and rerun all required checks before considering WVR-001
execution_phase: validation
validation_state: pending
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
