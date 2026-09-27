# Friday MCP Client Enhancement

---
title: Friday MCP Client Enhancement
initiative: friday-mcp
document_type: initiative-index
status: draft
updated: 2026-09-27
next_gate: approve rebaselined MCP-WS-00 and security defaults
implementation_authority: not granted
---

The repository contains substantial standalone MCP client and server code.
The cross-package runtime client integration described here has not been
implemented; enabling the runtime MCP provider still raises an explicit error.
Every construction directive remains Draft. The
[2026-09-27 rebaseline](rebaseline-2026-09-27.md) distinguishes the existing
package from this integration initiative and narrows the first slice.

Controlling packet:

- [Build plan](build-plan.md) — proposed feature and architecture authority.
- [Tactical plan](tactical-plan.md) — proposed workstream ordering.
- [Current-code rebaseline](rebaseline-2026-09-27.md) — baseline evidence,
  workstream status, and outstanding decisions.
- [Design notes](design-notes.md) — historical input, not controlling authority.
- [Construction directives](directives/) — draft execution instructions.

The next action is explicit maintainer approval of the rebaselined `MCP-WS-00`
scope and security defaults. A dedicated branch, baseline, and `started`
transition are required before code generation. Runtime loading is a later
dependent workstream.
