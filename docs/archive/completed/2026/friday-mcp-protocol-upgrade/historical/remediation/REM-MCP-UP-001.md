# REM-MCP-UP-001 — bounded correction of CD-MCP-UP-001

Prepared 2026-10-12. Authorization: existing maintainer-approved CD-MCP-UP-001
and A01, particularly CD-AC-02/03/04/05 and the tactical independent-candidate
gate that requires bounded remediation within existing authority. This record
adds no scope, dependency exception, waiver, optional capability or delivery
authority. It is a controller breakdown of two unsatisfied approved requirements.

Predecessor candidate: 4f3574c8d3fe6cca25d9835eda811ebda262429c.
Predecessor verdict: CHANGES_REQUESTED. Immutable original independent report:
validation/VAL-UP02A-01/report.md, SHA256
1fb7603c3abbcd394a32fafd75a6bb83808920ea047d305f383cd853a91f05a6.
The original candidate/report remain historical evidence and cannot support a
corrected-candidate verdict. Use a separate remediator for protocol data integrity.

## Exact corrections

| Finding | Fix, regression evidence and completion criterion |
| --- | --- |
| VAL-UP02A-001 | Recognize all three defined modern reserved wire error codes (-32020/-32021/-32022). Modern errors never issue initialize/initialized or negotiate legacy; preserve varied non-modern error and timeout fallback, exact legacy version, late IDs and fixed safe failures. Keep Friday local error identifiers separate from wire codes. Update package wording if needed. |
| VAL-UP02A-002 | Bounded context-aware validation of named modern protocol metadata/results/notifications, discovery capabilities/identity, Tool optional fields and supported TextContent metadata/annotations against the frozen schema. Validate metadata key grammar and declared typed fields; preserve unknown extension JSON as bounded, untrusted data. Reject malformed later pages without a partial catalog. Test positive valid shapes, every original counterexample, safe logs/reprs, and arbitrary application JSON named _meta inside arguments, structuredContent and inputSchema annotation/default/examples. No recursive interpretation of application data, fetching, or new handler. Update docs to state exact parsing boundary. |

Allowed edits are confined to existing approved product paths:
packages/friday-mcp/src/friday_mcp/client/base.py,
packages/friday-mcp/src/friday_mcp/client/protocol.py,
packages/friday-mcp/tests_mcp/client/test_modern_protocol.py,
packages/friday-mcp/tests_mcp/client/test_execution.py (only if required for
legacy compatibility), and packages/friday-mcp/README.md. No dependency/lock,
transport/config/Runtime/Chat/Core/Telemetry/server or unrelated source changes.
Controller-only evidence/report/hash/packet/board records remain process paths.

## Checks, non-goals and stops

Read the complete original approved directive/contract, A01 and immutable report.
Apply all original bounds, fixed failures/privacy, legacy compatibility and
effects constraints. Run every tactical verification command against the final
candidate in the private guarded environment; full regression fixture-only
loopback is authorized. Independently retained baseline and raw debt may be
compared without mutating baseline. Retain complete commands/raw outputs,
adversarial reproducer outcomes, exact changed-file hashes and dependency hashes.
No source ignore/cast, checker weakening, new skips, live credentials/providers,
user state, endpoint fetches, model/root exposure, HTTP/YAML implementation,
opportunistic refactoring, acceptance, push/merge/release or schema feature expansion.
Stop and report any required fix outside these paths or controlling requirements.

Remediator commits a stable corrected candidate and builder report, without
self-VERIFIED. Controller refreshes frozen review inputs and uses a new
fresh-context read-only reviewer for finding delta and full original work-unit
regressions/conformance. Two failed remediation cycles return unresolved findings
to the maintainer. Whole MCP initiative remains started/local throughout.
