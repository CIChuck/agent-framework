# VAL-CMD-MCP-002 — 2025 Draft-07 runtime registration review

**Verdict:** VERIFIED

**Date:** 2026-10-25

**Reviewer:** Codex fresh-context, read-only validation subagent

**Board initiative:** `friday-command-refactor` (still `started`)

**Work unit:** approved [Draft-07 registration remediation](../remediation/REM-CMD-MCP-002-2025-draft7-registration.md)

**Base:** `c7c29b9c04e8aeadd69ffc7067cfe48bec3ae4db`

**Candidate:** `ddd73e0ac3e0e446113a25b68643f9a71afad2c3`

**Diff range:** `c7c29b9c04e8aeadd69ffc7067cfe48bec3ae4db..ddd73e0ac3e0e446113a25b68643f9a71afad2c3`

## Scope and authority

The reviewer checked the nine supplied SHA256 values against `AGENTS.md`,
repository engineering, task lifecycle and independent validation policies,
the board, authority record, build plan, tactical plan and approved directive;
all matched. The seven-file candidate diff stays within the directive's
allowed source, test, guide and packet paths. The user's modified Friday Chat
YAML and models config were excluded and left untouched.

The runtime sanitizer now admits and strips the exact Draft-07 root URI only
for HTTP peers configured with `2025-11-25`. Its bounded inline subset,
semantic checks and rejection of nested declarations, other dialects and
unsupported keywords remain. The 2026 and legacy stdio paths retain Draft-07
rejection. The change does not alter budgets, authentication, networking or
remote tool-call behavior.

## Reproduced checks

| Check | Result |
| --- | --- |
| `uv run pytest -q packages/friday-mcp/tests_mcp/client packages/friday-runtime/tests_runtime/test_mcp_registration.py packages/friday-runtime/tests_runtime/test_mcp_runtime_config.py packages/friday-runtime/tests_runtime/test_mcp_http_integration.py packages/friday-runtime/tests_runtime/test_mcp_loading.py packages/friday-chat/tests_chat/test_mcp_chat_bridge.py packages/friday-chat/tests_chat/test_mcp_http_integration.py packages/friday-chat/tests_chat/test_mcp_turn_budget.py packages/friday-chat/tests_chat/test_mcp_execution_security.py packages/friday-chat/tests_chat/test_mcp_execution_transcript.py packages/friday-chat/tests_chat/test_mcp_config_compatibility.py packages/friday-chat/tests_chat/test_mcp_memory.py` | 2,003 passed |
| Focused Ruff on the four changed Python files | Passed |
| `uv run mypy packages/friday-runtime/src/friday_runtime/mcp_registration.py` | Passed |
| `uv run python scripts/friday-dev-board.py validate` | Passed; 36 tasks |
| `uv run python scripts/check-documentation-lifecycle.py` | Passed; 661 Markdown files |
| `git diff --check` on the candidate | Passed |

The independent no-auth, discovery-only OpenAI Docs probe connected, found
five tools, prepared five and registered five `mcp_openaidocs_*` tools, with
five `registered` decisions and no remote tool calls. The deterministic Chat
integration confirms that all five appear in `/tools mcp`.

## Limits and status

The live probe verifies the endpoint's current availability; deterministic
tests carry the regression gate. The user's working YAML changed from the
40,000 schema budget recorded at candidate freeze to 50,000 during validation.
This file remains outside the candidate and did not affect the five-tool Docs
registration result. A separate builder discovery-only probe with both
servers registered 19 tools, leaving the three previously identified Zapier
schema rejections; the independent reviewer did not repeat that authenticated
probe. An optional Ruff format check still finds only pre-existing formatting
in `test_mcp_registration.py`; the required Ruff lint check passed.

`VERIFIED` closes this bounded work-unit review. It is not aggregate command
refactor validation, maintainer acceptance, push, merge or TUI handoff.
