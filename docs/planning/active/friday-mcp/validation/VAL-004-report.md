# VAL-004 — Independent MCP-WS-01 Remediation And Aggregate Review

**Verdict:** remediation delta `VERIFIED`; complete WS-01 aggregate
`VERIFIED`; overall WS-01 validation gate `VERIFIED`.

**Reviewer:** Fresh-context Codex validation subagent
`/root/mcp_ws01_val004`, independent of the builder and remediator. Reviewer
reported GPT-6 family; exact deployment version unavailable.

**Date:** 2026-09-27

**Modes:** Read-only delta review followed by complete WS-01 aggregate review.

**Candidate:** `dd6c65bce0035682bbc688953aff8e2011d9d3b7`

**Delta:** `de8db57b565968fa02e429e16a481e00c6a92024..dd6c65bce0035682bbc688953aff8e2011d9d3b7`

**Aggregate:** `22a5643943da06043515494e23b3dfe549052c55..dd6c65bce0035682bbc688953aff8e2011d9d3b7`

**Bounded remediation:** `84c984101046613051824748bf9f6a8f8a068518..dd6c65bce0035682bbc688953aff8e2011d9d3b7`

The reviewer read the complete [VAL-004 request](VAL-004-request.yaml), all
twelve pinned authority documents, historical [VAL-003](VAL-003-report.md)
findings, revised [REM-002](../remediation/REM-002-directive.md), candidate
source/tests/examples, and exact diffs. All twelve SHA-256 values matched
initially and at closeout; REM-002 also matched authorization commit
`84c9841`. The disclosed post-candidate VAL-003 superseded-status note did not
alter its historical verdict or findings.

HEAD stayed at `ff8703c9810c873e32330ff95dcd8671dbd0b73b` throughout review.
Its changes after the candidate were process metadata only. Source, tests,
directive, and governed authority stayed frozen. The reviewer made no edits,
repairs, commits, board mutations, MCP/provider calls, or external effects.
Unrelated dirty paths were unchanged.

## Delta Verdict — VERIFIED

F-001 is resolved. The MCP direct constructor, parser fallback, and runtime
default-source template now use `selected` in
`packages/friday-runtime/src/friday_runtime/config.py`. The default-mode
regressions in `test_mcp_runtime_config.py` cover all three omitted-mode
paths, preserve non-MCP `all` defaults, retain explicit MCP `all`, and reject
invalid mode.

F-002 is resolved. The new
`packages/friday-chat/tests_chat/test_mcp_config_compatibility.py` uses the
real Chat YAML loader and `FridayChatConfig`, verifies unchanged retention
of a canonical MCP stanza, and validates that same stanza through
`MCPToolProviderConfig.from_dict()`. Negative cases retain canonical rejection
of reserved includes and invalid limits. Chat already declares runtime as a
dependency; no reverse dependency was introduced.

The bounded remediation contains only the three permitted source/test files,
the corrected config example, and the implementation report. No Chat source,
dependency, alias, selection, turn behavior, or later-workstream behavior was
added.

## Aggregate Verdict — VERIFIED

All `MCP-01-01` through `MCP-01-07` criteria have candidate evidence:

- Typed provider/client/server models reuse the WS-00 discovery, limits,
  security, and ingestion DTOs; default and round-trip tests pass.
- Stdio server declarations validate enabled/required semantics, commands,
  timeouts, retries, transports, and trust levels, with positive and negative
  tests.
- Reserved `config_file` fails with an actionable WS-09 message in direct and
  YAML parsing. Unknown provider, server, and policy keys fail closed.
- Duplicate canonical IDs, configured caps, include/exclude conflicts, and
  working-directory traversal, absolute-path, and symlink escapes are tested.
- Existing defaults → YAML → permitted environment → explicit override
  precedence is preserved. Protocol-local MCP/SSE APIs remain unchanged,
  with compatibility regression coverage.
- The committed disabled, optional stdio, required-server, exclude-only, and
  rejected-include examples were independently parsed. The downstream Chat
  test supplies the required canonical-config compatibility evidence without
  claiming actual Chat runtime integration.

## Independent Checks

All `uv` commands used `UV_CACHE_DIR=/private/tmp/friday-uv-cache`; tests and
diagnostic imports also used `LITELLM_LOCAL_MODEL_COST_MAP=true`. Exact
required commands are recorded in the request.

- Core/MCP/runtime tests: **262 passed**.
- Required Friday Chat config tests: **46 passed**.
- Affected-package/new-test Ruff: **passed**.
- Python 3.13 mypy for affected packages and new Chat test: **passed**,
  38 files.
- Board validation: **passed**, 23 tasks; dashboard freshness: **passed**;
  documentation lifecycle: **passed**, 324 Markdown files.
- Both delta and aggregate diff whitespace checks: **passed**.
- Additional independent probes passed for strict boolean/numeric fields,
  unknown keys in all four policy sections, ingestion tuple normalization,
  and committed examples.

Default-target package-wide mypy reproduced the baseline NumPy Python 3.12
type-statement syntax failure under the repository's unchanged Python 3.10
target. The prescribed Python 3.13 check passed. The additional board
integration check produced **10 passed, 1 baseline failure**: its unchanged
test expects 22 tasks, while the base board already had 23. Neither baseline
is a candidate regression.

**Findings:** none.

## Residual Risk And Boundary

Runtime MCP enablement still raises the intentional unsupported-loader error
in `friday_runtime.tool_loading`. This verdict verifies configuration
declarations and Chat config compatibility only. Connection/discovery/loading,
registration/filter enforcement, Chat bridging/turn behavior,
execution/persistence redaction, and live interoperability remain later
gates. Workspace containment is checked during construction; later execution
must preserve that boundary.

`VERIFIED` closes the independent validation gate for WS-01 only. It does not
complete or accept the wider initiative, authorize WS-02, or grant merge,
push, release, deployment, or other delivery authority.
