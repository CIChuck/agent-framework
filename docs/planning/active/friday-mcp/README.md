# Friday MCP Client Enhancement

---
title: Friday MCP Client Enhancement
initiative: friday-mcp
document_type: initiative-index
status: active
updated: 2026-09-27
next_gate: revised REM-002 candidate and fresh delta plus aggregate review
implementation_authority: granted for MCP-WS-00 and MCP-WS-01 only
execution_phase: remediation
validation_state: changes_requested
---

The repository contains substantial standalone MCP client and server code.
The cross-package runtime client integration described here has not been
implemented; enabling the runtime MCP provider still raises an explicit error.
Only the `MCP-WS-00` construction directive is approved. All later directives
remain Draft. The
[2026-09-27 rebaseline](rebaseline-2026-09-27.md) distinguishes the existing
package from this integration initiative and narrows the first slice.

Controlling packet:

- [Build plan](build-plan.md) — proposed feature and architecture authority.
- [Tactical plan](tactical-plan.md) — proposed workstream ordering.
- [Current-code rebaseline](rebaseline-2026-09-27.md) — baseline evidence,
  workstream status, and outstanding decisions.
- [Design notes](design-notes.md) — historical input, not controlling authority.
- [Construction directives](directives/) — approved WS-00 and draft later slices.
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
remaining boundaries. The wider `friday-mcp` initiative remains `started`:
WS-02 through WS-08 are draft, and runtime loading is not authorized by this
work-unit verdict. The maintainer accepted the WS-00 work-unit result and
approved the bounded [WS-01 directive](directives/ws-01-configuration-model-validation.md)
on 2026-09-27. WS-01 implementation is now in progress on
`feature/friday-mcp-ws01-config`.
The [WS-01 implementation report](execution/WS-01-implementation-report.md)
records the typed configuration model, tests, and known baseline failures.
Independent [VAL-003](validation/VAL-003-report.md) returned
`CHANGES_REQUESTED` for the MCP default mode and missing Friday Chat
config-consumption evidence. [REM-002](remediation/REM-002-directive.md)
bounds the needed fixes. A separate remediator and fresh delta plus aggregate
review are required before a WS-01 verdict. The maintainer authorized the
separate REM-002 remediator on 2026-09-27. The remediator encountered the
directive's F-002 dependency stop condition before editing: a runtime-package test
cannot import downstream Friday Chat without an undeclared reverse
dependency. The maintainer approved moving only the F-002 compatibility test
to Friday Chat's test package. REM-002 is revised and may resume; the next
gate is a new candidate and fresh delta plus aggregate review. No WS-02
behavior is authorized yet.
