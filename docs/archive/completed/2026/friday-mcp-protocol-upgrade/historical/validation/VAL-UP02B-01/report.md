# CHANGES_REQUESTED — CD-MCP-UP-002 / MCP-UP-02B

Controller navigation cover for the fresh read-only full review by
`/root/mcp_up02b_validator`. The [complete original reviewer report](artifacts/report.md.gz)
and [original artifact hashes](stored-manifest.json) are retained unchanged.

Reviewed candidate: `2a3cec520f20442515d3d9a5a1a33eb500bd8846`.
Original independent report SHA256: `e97e199a556be162ff99a46d6d3ec6db75de3ef61cff5985447b47fbd73487c3`.

The HTTP unit is **not VERIFIED**. Four independent defects require bounded fixes:

1. `x-mcp-header` nested inside `contentSchema` bypasses validation/exclusion.
2. A delayed concurrent 2025 session-404 can mark a successfully recovered session
   disconnected, preventing the next explicit call.
3. Unsupported declared 2025 input-schema dialects are published instead of
   receiving a graceful unsupported-schema failure.
4. Malformed 2025 metadata keys are accepted on Tool, Result and TextContent.

Required candidate gates pass: 198 HTTP, 228 original client, 462 MCP package,
1,211 Runtime/Chat/Telemetry and 3,529 workspace tests. Independent accepted-product
baseline: 3,331 passes. Exact skip groups/warnings and 327 root Ruff findings are
baseline-identical; scoped lint and types pass. Passing existing tests does not
resolve the reproduced conformance/lifecycle failures.

The [bounded remediation directive](../../remediation/REM-MCP-UP-002-streamable-http.md)
is a proposal requiring maintainer authorization. The initiative remains started/
local; no unit completion, acceptance or publication is recorded.
