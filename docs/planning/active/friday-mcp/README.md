# Friday MCP Client Enhancement

---
title: Friday MCP Client Enhancement
initiative: friday-mcp
document_type: initiative-index
status: active
updated: 2026-09-27
next_gate: independent validation of frozen MCP-WS-00 candidate
implementation_authority: granted for MCP-WS-00 only
execution_phase: validation
validation_state: pending
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
[WS-00 report](execution/WS-00-implementation-report.md). The next gate is
independent validation of the frozen WS-00 candidate. Runtime loading is a
later dependent workstream and is not authorized here.
