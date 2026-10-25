# VAL-CMD-MCP-001 — MCP compatibility work-unit review

**Verdict:** VERIFIED

**Date:** 2026-10-25

**Reviewer:** Codex independent subagent (GPT-6; exact version unavailable)

**Review mode:** fresh-context, read-only work-unit review

**Board initiative:** `friday-command-refactor` (still `started`)

**Work unit:** MCP client compatibility exception, CD-CMD-MCP-001 with
AMEND-CMD-MCP-001-001

**Base:** `c5683fd28a40bf92cf32ae9b790897a9a34ce5f4`

**Candidate:** `28c1741ef66f000f68ccb286ac99f8165828dded`

**Diff range:** `c5683fd28a40bf92cf32ae9b790897a9a34ce5f4..28c1741ef66f000f68ccb286ac99f8165828dded`

## Frozen authority and scope

The reviewer read `AGENTS.md`, the repository engineering, development task
lifecycle and independent validation policies, the board task, the
[authority record](../authority.json), [build plan](../build-plan.md),
[tactical plan](../tactical-plan.md), the
[approved directive](../directives/CD-CMD-MCP-001-compatibility-exception.md)
and [approved amendment](../directives/AMEND-CMD-MCP-001-001-2025-dialect-isolation.md).
The reviewer checked all nine authority SHA256 values supplied in the review
request against the frozen files and reported that they matched.

The candidate adds the exact Draft-07 input-schema URI and matching validator
for the MCP 2025 path, carries the selected version through catalog parsing so
the 2024 and 2026 paths stay protected, and preserves endpoint query strings
on HTTP requests. The reviewer found no prohibited scope change. The MCP guide
documents header-based bearer credentials and the non-secret query rule.

## Reproduced checks

| Check | Result |
| --- | --- |
| `uv run pytest -q packages/friday-mcp/tests_mcp/client packages/friday-runtime/tests_runtime/test_mcp_runtime_config.py packages/friday-chat/tests_chat/test_mcp_http_integration.py` | 1,640 passed |
| Focused Ruff on changed source and tests | Passed |
| Focused mypy on changed MCP source and runtime config | Passed |
| `uv run python scripts/friday-dev-board.py validate` | Passed; 36 tasks |
| `uv run python scripts/check-documentation-lifecycle.py` | Passed; 658 Markdown files |
| `git diff --check` on the candidate | Passed |

The builder separately ran a read-only live discovery after the amendment:
`https://developers.openai.com/mcp` and its `?xyz` variant each returned five
tools. The reviewer did not repeat this optional live check. No credentials or
remote tool calls were used in that check.

The two pre-existing dirty files, `packages/friday-chat/config.example.yaml`
and `packages/friday-chat/models-config.example.yaml`, were excluded from the
candidate and left untouched.

## Residual risk and status boundary

The optional live endpoint observation can change independently of the
deterministic regression gate. This verdict applies only to the frozen MCP
work-unit candidate. The command-refactor packet's `planning`/`not_ready`
fields and board next gate still describe the larger command initiative. This
receipt does not mark that initiative completed or accepted.
