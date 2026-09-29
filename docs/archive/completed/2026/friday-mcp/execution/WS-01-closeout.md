# MCP-WS-01 Work-Unit Closeout

**Date:** 2026-09-27

**Work unit:** canonical runtime MCP configuration and validation only.

**Candidate:** `dd6c65bce0035682bbc688953aff8e2011d9d3b7`

**Validation:** independent delta and complete WS-01 aggregate `VERIFIED`
in [VAL-004](../validation/VAL-004-report.md).

**Accepted by:** repository maintainer

**Accepted at:** 2026-09-27

**Acceptance evidence:** explicit maintainer message "accept ws-01" in the
active conversation after review of this verified closeout.

WS-01 provides strict runtime-facing MCP client/server configuration under
`tools.providers.mcp`, reusing the WS-00 policy DTOs. It validates stdio-only
server declarations, safe defaults and filters, unknown/future fields,
limits, canonical server IDs, and workspace-confined working directories.
The existing protocol-local MCP/SSE APIs are preserved. MCP mode defaults to
`selected`; deliberate `mode: all` remains valid.

Initial candidate `de8db57` received two VAL-003 findings. REM-002 corrected
the default and added downstream Chat config-consumption evidence. Its first
attempt stopped without edits at a reverse test-dependency boundary; the
maintainer approved moving only that test into Friday Chat's package.
The resulting candidate does not change Chat source or dependencies. Fresh
independent review verified both the correction and complete WS-01 work unit.

Evidence: **262 core/MCP/runtime tests plus 46 Chat config tests passed**;
Ruff, Python 3.13 mypy on 38 files, board/dashboard, documentation lifecycle,
and candidate diff checks passed. Default-target mypy and the board-count
integration assertion retain documented pre-existing failures, distinguished
from regressions in VAL-004. No live MCP server or provider was contacted.

The maintainer accepted this WS-01 work unit only, not the wider initiative.
The wider `friday-mcp` task remains `started` and local. MCP runtime loading
still deliberately rejects enablement. WS-02 and later workstreams remain
draft; the next gate is explicit maintainer approval of bounded WS-02
lifecycle scope. This acceptance does not authorize connection, tool
registration, merge, push, release, deployment, or other delivery actions.
