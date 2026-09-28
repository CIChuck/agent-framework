# Friday MCP Client Enhancement

---
title: Friday MCP Client Enhancement
initiative: friday-mcp
document_type: initiative-index
status: active
updated: 2026-09-27
next_gate: fresh independent WS-02 candidate validation
implementation_authority: granted for MCP-WS-00 through MCP-WS-02 with bounded cleanup amendment
execution_phase: validation
validation_state: pending
---

The repository contains substantial standalone MCP client and server code.
Runtime-owned stdio startup/discovery/shutdown is implemented in a WS-02
candidate awaiting independent validation. WS-00 contracts and WS-01 strict
configuration are implemented and independently verified. WS-02 and its
bounded startup-cleanup/stdio-redaction amendment are approved;
WS-03 and later remain Draft. The
[2026-09-27 rebaseline](rebaseline-2026-09-27.md) distinguishes the existing
package from this integration initiative and narrows the first slice.

Controlling packet:

- [Build plan](build-plan.md) — proposed feature and architecture authority.
- [Tactical plan](tactical-plan.md) — proposed workstream ordering.
- [Current-code rebaseline](rebaseline-2026-09-27.md) — baseline evidence,
  workstream status, and outstanding decisions.
- [Design notes](design-notes.md) — historical input, not controlling authority.
- [Construction directives](directives/) — approved WS-00/01/02 and draft later slices.
- [Execution log](execution-log.md) — approval, baseline, and work-unit progress.

The maintainer approved the rebaselined `MCP-WS-00` contracts/defaults-only
scope, stdio-only first-pass runtime posture, and no stored argument hashes by
default on 2026-09-27. Execution started on
`feature/friday-mcp-ws00-contracts` from baseline `20c70dd`. Local
implementation and focused checks are recorded in the
[WS-00 report](execution/WS-00-implementation-report.md). Independent
[VAL-001](validation/VAL-001-report.md) returned `CHANGES_REQUESTED` for two
contract findings. [REM-001](remediation/REM-001-directive.md) bounds the
required corrections. The maintainer authorized a separate remediator for the
cross-package architecture finding on 2026-09-27. REM-001 produced candidate
`b79754f`; [the report](execution/REM-001-implementation-report.md) records
its checks. Fresh independent [VAL-002](validation/VAL-002-report.md) verified
both the remediation delta and complete WS-00 candidate. The
[WS-00 work-unit closeout](execution/WS-00-closeout.md) records the result and
remaining boundaries. The wider `friday-mcp` initiative remains `started`.
At that closeout, WS-02 through WS-08 were draft, and runtime loading was not
authorized by that work-unit verdict. The maintainer accepted the WS-00 work-unit result and
approved the bounded [WS-01 directive](directives/ws-01-configuration-model-validation.md)
on 2026-09-27. WS-01 was implemented on
`feature/friday-mcp-ws01-config`.
The [WS-01 implementation report](execution/WS-01-implementation-report.md)
records the typed configuration model, tests, and known baseline failures.
Independent [VAL-003](validation/VAL-003-report.md) returned
`CHANGES_REQUESTED` for the MCP default mode and missing Friday Chat
config-consumption evidence. [REM-002](remediation/REM-002-directive.md)
bounds the fixes. A separate remediator and fresh delta plus aggregate
review were required for the corrected WS-01 verdict. The maintainer authorized the
separate REM-002 remediator on 2026-09-27. The remediator encountered the
directive's F-002 dependency stop condition before editing: a runtime-package test
cannot import downstream Friday Chat without an undeclared reverse
dependency. The maintainer approved moving only the F-002 compatibility test
to Friday Chat's test package. Revised REM-002 resumed within that scope;
candidate `dd6c65b` passed fresh delta and complete WS-01 aggregate review in
[VAL-004](validation/VAL-004-report.md). The
[REM-002 report](execution/REM-002-implementation-report.md) and
[WS-01 work-unit closeout](execution/WS-01-closeout.md) record the bounded
fixes, checks, and remaining gates. The maintainer explicitly accepted WS-01
on 2026-09-27. This is work-unit acceptance only; the wider initiative remains
`started` and delivery remains local.

The maintainer explicitly approved bounded WS-02 on 2026-09-27 with
"ws-02 approved". Execution preparation is on
`feature/friday-mcp-ws02-lifecycle` from accepted WS-01 checkpoint `a64e423`.
The [readiness checkpoint](execution/WS-02-readiness-checkpoint.md) reproduces
failed-handshake cleanup loss and identifies raw stdio logging below the
directive's allowed files. That inspection changed no source or tests. The
maintainer subsequently authorized the narrow amendment for MCP
`client/base.py` and `client/stdio.py` with "continue next steps", after the
scope request and defect explanation. The
[WS-02 implementation report](execution/WS-02-implementation-report.md)
records the lifecycle candidate and bounded verification. The next gate is
fresh independent candidate validation. Current
process fields describe WS-02, not a change to the independently verified and
accepted WS-00/01 results.
