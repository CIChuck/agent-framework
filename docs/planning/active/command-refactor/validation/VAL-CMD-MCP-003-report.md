# VAL-CMD-MCP-003 — server-neutral MCP schema work-unit review

**Verdict:** VERIFIED

**Date:** 2026-10-25

**Reviewer:** Codex fresh-context, read-only validation subagent

**Board initiative:** `friday-command-refactor` (still `started`)

**Work unit:** [CD-CMD-MCP-003](../directives/CD-CMD-MCP-003-server-neutral-schema.md)
and its approved [send-boundary amendment](../directives/AMEND-CMD-MCP-003-001-send-boundary.md)

**Base:** `936fb835ad0685c59ea93d8979f63a0618a99982`

**Candidate:** `e898e211d2c666aef3190682cd8cfb4556e3c934`

**Diff range:** `936fb835ad0685c59ea93d8979f63a0618a99982..e898e211d2c666aef3190682cd8cfb4556e3c934`

## Authority and scope

The reviewer matched the frozen directive SHA256
`267dfac31ce6830559d8ab1b09e2351e697077efae1c097c7c1b895c19847694`,
approved amendment SHA256
`b94dd24545974bf0bce2efa17e1181d590ce2de6de92aa05c38e5d1d3c46e073`,
and engineering-matrix SHA256
`ce933848078603a4e9e14a27bf82e7d0fe2e6c1ba6d162d2af8dbd7408904f24`.
The base-to-candidate diff stays within those approved boundaries. The user's
pre-existing edits to the two Friday Chat example config files remain outside
the candidate and were untouched.

The earlier [interim review](VAL-CMD-MCP-003-interim-review.md) returned
`CHANGES_REQUESTED`. This candidate addresses its send-boundary finding with
generation guards at stdio transport send and HTTP pool dispatch, plus
deterministic zero-RPC tests. The new Chat formatting difference was corrected.
The two earlier candidate findings—argument serialization before preflight and
binding a discovered schema to a later catalog generation—also remain covered
by the full candidate's tests and implementation.

## Independently reproduced checks

| Check | Result |
| --- | --- |
| Selected MCP client, runtime and Chat pytest command in the [execution log](../execution-log.md) | 2,040 passed |
| Focused Ruff lint and format on amended client files, refresh test and corrected Chat line | Passed |
| Focused mypy on `friday_mcp.client.base` and `friday_mcp.client.http` | Passed |
| `uv run python scripts/friday-dev-board.py validate` | Passed; 36 tasks |
| `uv run python scripts/check-documentation-lifecycle.py` | Passed; 668 Markdown files |
| `git diff --check` | Passed |

The reviewer confirmed deterministic coverage for bounded schema admission,
canonical argument validation before RPC, provider-export fail-safe withholding,
safe status reporting, stale-generation rejection at registration and dispatch,
generation-free raw calls, and settlement of calls already dispatched. The
independent review used local tests only; it made no live MCP or paid model
call. Provider compatibility for offering the newly admitted recursive tools
to a model remains unproven, so those tools stay withheld with the safe
`provider_export` reason until a separate authorized model-path proof.

`VERIFIED` closes this bounded work-unit review. It does not grant maintainer
acceptance, finish P0–P5 shared-command construction, push or merge the branch,
or start the separate MCP tool-turn-continuity implementation.
