# MCP-WS-00 Work-Unit Closeout

**Date:** 2026-09-27

**Work unit:** contracts and policy foundation only

**Candidate:** `b79754f23aeee69ea3618b711c78f2c3e51edb71`

**Validation:** independent delta and aggregate `VERIFIED` in
[VAL-002](../validation/VAL-002-report.md)

WS-00 delivered typed, importable framework-facing MCP contracts and
conservative policy defaults in `friday_core.mcp`, with focused tests. The
metadata-sidecar and naming contracts prepare later integration without
changing the existing `friday-mcp` protocol client, runtime provider loader,
tool registry, Friday Chat, memory, transcript, telemetry, or CLI behavior.
The first integrated runtime pass is planned as stdio-only, and stored
argument hashes remain off by default; neither decision is runtime-enforced
by this work unit.

The initial candidate received two findings in
[VAL-001](../validation/VAL-001-report.md). A separately authorized remediator
addressed them in `b79754f`, and fresh independent review verified both the
remediation delta and complete WS-00 aggregate. The focused test suite passed
232 tests, alongside Ruff, targeted mypy, and board/documentation checks.
Package-wide mypy and one board-count integration assertion retain documented
pre-existing failures; see VAL-002 for the exact distinction. No live MCP
server or external service was exercised.

**Boundary:** This is work-unit closeout, not initiative completion or
maintainer acceptance. The `friday-mcp` board task remains `started` and local.
WS-01 through WS-08 remain draft; the next gate is maintainer review and
explicit approval of a bounded WS-01 directive before new product code.
