# VAL-CMD-MCP-003 — server-neutral schema interim review

**Verdict:** CHANGES_REQUESTED

**Date:** 2026-10-25

**Reviewer:** Codex fresh-context, read-only validation subagent

**Board initiative:** `friday-command-refactor` (still `started`)

**Work unit:** approved [CD-CMD-MCP-003](../directives/CD-CMD-MCP-003-server-neutral-schema.md)

**Base:** `936fb835ad0685c59ea93d8979f63a0618a99982`

**Reviewed candidate:** `c0d5518aa132b5e416d9806e65132476f34840ea`

The reviewer matched the directive and engineering-matrix hashes, checked the
full candidate diff against the approved package boundaries, and left the two
pre-existing dirty Friday Chat example configs untouched. Targeted offline
tests passed **214**; focused Ruff lint and mypy passed; board validation
passed **36 tasks**, documentation lifecycle passed **666 Markdown files**,
and `git diff --check` passed. The builder's broader MCP client, runtime and
Chat selection passed **2,037 tests**; the reviewer did not rerun that full
selection.

## Findings

| ID | Severity | Evidence | Required remediation |
| --- | --- | --- | --- |
| F-CMD-MCP-003-03 | High | `MCPClientBase.call_tool_at_generation` checks the generation before scheduling the request exchange. A local fake invalidated the catalog after that check and before simulated dispatch; one stale RPC was still recorded. | Add a generation guard at the stdio and HTTP dispatch seams, with deterministic refresh-between-check-and-dispatch tests asserting zero calls. The additional client-source boundary requires the [proposed amendment](../directives/AMEND-CMD-MCP-003-001-send-boundary.md). |
| F-CMD-MCP-003-04 | Low | `ruff format --check` found one new formatting difference in `friday_chat/tools/mcp.py:194`; two other changed files already failed formatting at the base commit. | Format the changed Chat line and rerun focused format validation. |

The review confirmed that the earlier argument-preflight and
discovery-to-registration generation findings were addressed in this
candidate. The current verdict remains **CHANGES_REQUESTED**. The first two
unsuccessful remediation cycles and this additional finding require a
maintainer decision on the proposed amendment before further client-source
work. Neither this review nor earlier reviews establish work-unit validation,
maintainer acceptance, or command-refactor completion.
