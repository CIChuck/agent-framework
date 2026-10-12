# MCP upgrade execution log

## 2026-10-12 — MCP-UP-01 preparation

Maintainer direction: "lets move onto the mcp upgrade" following the proposed
MCP-UP-01 preparation gate. Prepared current baseline, primary-source revision
check, protocol/compatibility contract, SDK/dependency decision, build/tactical
plans and exact twelve-path CD-MCP-UP-001 proposal. No product construction or
implementation approval is inferred from this progression request.

Baseline `46005353046553477417a730f05ff21ead64a00d` includes accepted core
TELEM-01 through04. Checked fifteen accepted telemetry product hashes and the
forty-six acceptance-control hashes. Preserve TelemetryInterface and queue
Langfuse after MCP acceptance. Existing source core remains 2024-11-05; new
revision/profile decisions are proposed, not implemented.

Planning validation: board/dashboard consistency, documentation lifecycle,
proposal control/source hash checks and diff whitespace checks. Existing
client/base.py and client/stdio.py Ruff and Mypy checks pass. SDK/network
interop, dependency resolution, product tests and independent product validation
have not been executed. No source, tests, package metadata, lock or user config
was edited; unrelated dirty/deleted/queued assets were preserved.

Next gate: maintainer review of the build/protocol/tactical contract and
CD-MCP-UP-001; then frozen approval/branch/start preparation and only the first
approved construction slice. HTTP, remote YAML, server and Langfuse work retain
their separately bounded scopes. Proposal remains queued/not_granted.

## 2026-10-12 — approval and normative-source clarification

Chuck Russell explicitly approved the contract and CD-MCP-UP-001, and asked
whether the packet specifically matches the new MCP specification and is pegged
to the appropriate research. Recorded the exact statement and original seventeen
proposal-control hashes/twelve-path product scope in [approval.json](approval.json).
Made official dated specification/schema conformance explicit and added
[research-to-acceptance mapping](conformance-matrix.md). No product-scope or optional-feature expansion.

Official latest still selects 2026-07-28. The TypeScript schema linked by that
specification is normative; SDK 2.3.0 is counterpart evidence and Anthropic
connector documentation is context. Complete normative-byte and SDK artifact
hashes remain required before product edits. Board approval authorizes execution
preparation and only CD-MCP-UP-001; later construction directives remain separate.

Captured complete public normative bytes for nine dated documents and the
TypeScript schema, archived losslessly with URL/size/content/artifact hashes.
Schema upstream commit `271ecc9accafdd9b83a3c869fa67c22953b2af80` was fetched
separately and its full bytes match SHA-256
`742750af0bb8c716e7030c4977c992b55d1adc4407e9e66997db5846baedc2cd`.
These inputs are research authority, not executed product-conformance evidence.


## 2026-10-12 — approved first construction slice started

MCP dedicated branch now derives from telemetry merge1302b5f and approved planning
checkpoint `a3c0cbdc867ca3535f611c2461ff080a991de86c`. Original approved product hashes remain unchanged.
Move packet to active, repair scheduling links, preserve original approval bytes
and original queued-control hashes at that checkpoint, and hash active controls.
Started/granted on feature/friday-mcp-protocol-upgrade for CD-MCP-UP-001 only.
Construct and validate in an isolated sparse snapshot excluding protected state
before checkout. No later-unit or delivery authority is added.


## 2026-10-12 — SDK dependency conflict; A01 prepared for approval

Two isolated sparse checkouts exclude267 protected paths before checkout; both
use committed started/granted authority8f80463 without a dirty-work overlay.
PyPI confirms SDK2.3.0 and exact artifact hashes. Default and minimum-httpx2
resolutions require an existing IDNA update. Original no-churn resolver exits1:
SDK2.3.0 -> httpx2>=2.10.0 -> idna>=3.18 conflicts with idna3.11.
Prepared exact A01 proposal and full lock/metadata/registry/command receipts.
Only IDNA changes among existing version sets; twelve new SDK transitive packages
are individually inventoried. All other contexts still require formal preservation
checks before execution. Restore isolated pyproject/lock to original bytes; no
client/test edits, dependency install, SDK execution or product checks are claimed.
Started/local; execution_phase planning; validation_state blocked. Approval of
this bounded exception and renewed frozen controls is the next gate.
