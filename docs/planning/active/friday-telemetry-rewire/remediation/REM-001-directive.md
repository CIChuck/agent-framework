# REM-001: preserve composite identity across provider replacement

Status: Proposed for maintainer approval; no remediation code is authorized yet.
Date: 2026-10-05. Initiative: `friday-telemetry-rewire`; work unit: `TELEM-01`.
Finding: `VAL-001-F01` from the fresh-context candidate review.
Candidate to remediate: `0c7b6d4c416402443d140a5ee09abed70be34c69`.
Branch: `feature/friday-telemetry-rewire`.

## Problem and authority amendment to approve

Two conforming providers can issue the same provider-local span ID. If the first
provider is replaced while its span is open, `CompositeProvider.start_span`
currently overwrites ownership under that ID. Ending the ID closes the new
provider's span and strands the removed provider's old span. This violates
CD-001 AC-05 and the approved contract's pinned span ownership requirement.

The current contract's unconditional reuse of the first child's ID cannot
represent both spans in this case. Approve this bounded identity amendment:
retain that ID when it can safely identify one composite span; otherwise issue
an opaque composite-owned ID and retain the complete per-child mapping. A stale
end must never close a different, later span. Keep normal first-child-ID
compatibility and treat child IDs as opaque; do not require provider-generated
UUIDs or rename child spans. This amendment is proposed, not silently applied
to the frozen authority.

## Exact remediation scope

Product changes are limited to:

- `packages/friday-telemetry/src/friday_telemetry/providers/composite.py`
- `packages/friday-telemetry/tests_telemetry/test_providers.py`
- `packages/friday-telemetry/README.md`

On explicit approval, reconcile the identity paragraph in this initiative's
`telemetry-contract.md` and CD-001 and record the amendment in this directive and
execution log before code generation. Other Chat/telemetry contracts and
product files remain frozen. Preserve unrelated local state and the dirty
example YAML. No OTel, Langfuse, exporters, later telemetry units, test timing
changes, dependencies, external services, or storage changes are authorized.

## Required mitigation and regressions

1. Prevent public-ID aliasing from overwriting an existing child ownership tuple.
   Pin each span's original children independently of later membership changes.
2. Reproduce the finding with two distinct providers whose local ID generators
   both begin at `span-0`. Start an old span, remove that provider, install the
   new one, and start another. Both public spans must remain independently
   addressable; ending either closes only its recorded child exactly once.
3. Cover reused IDs after a prior span has ended, repeated/stale ends, nested
   parent mapping across replacement, removed-provider cleanup, empty
   composites, partial-start rollback, and failing-child fan-out. No test may
   rely on UUID collision probability to establish identity correctness.
4. Preserve ordinary first-child-ID behavior and existing two-recorder parent,
   end, mutation, and best-effort failure behavior. Document collision behavior.

Run the complete CD-001 required checks, all fresh review probes, focused new
collision regressions, and the full Chat + telemetry suite. Preserve evidence
of baseline timing failures separately. Record exact paths, authority amendment,
commands, criteria coverage, and residual risks in an implementation report.
Commit a new stable candidate; preserve VAL-001 as superseded for decision
purposes. Freeze a new authority manifest and request. A fresh read-only validator
must perform the finding delta review and aggregate TELEM-01 review.

Stop at new scope, architectural conflict, failed requirements, or the committed
candidate and report. No self-verification, automatic acceptance, merge, push,
release, or unapproved further remediation. Baseline waiver WVR-001, if approved,
is a separate AC-06 decision; it cannot waive this ownership defect.
