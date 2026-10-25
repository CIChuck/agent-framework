# Proposal — MCP tool continuity across Friday Chat turns

**Status:** planning and diagnosis only; no construction directive or product-code authority.

**Branch/relationship:** `feature/command-refactor`. This is a separate MCP
follow-up, not a P0–P5 slash-command migration or a change to the 50-command
baseline. Read with the [schema compatibility proposal](mcp-schema-compatibility.md):
both affect Zapier workflows, but they fail at different boundaries.

## Problem and evidence

The maintainer reported that Friday recognized Zapier Gmail capability in one
conversation turn, then lacked the appropriate MCP tool after the short
follow-up asking it to send the email. A registered tool is not necessarily
offered to the model on every turn. `/tools mcp` lists registered tools; the
turn's `selected_tool_names` and `/tool-budget` describe the smaller offered
set. A tool absent from `/tools mcp` is a registration problem, not this
selection problem.

The current path is:

1. `TurnProcessor._prepare_turn()` synchronizes the registered catalog and
   calls `ToolSelectionState.select_for_turn(user_message)` using only the
   latest user message (`packages/friday-chat/src/friday_chat/turns/processor.py`).
2. Automatic selection scores that message against registered names,
   descriptions, categories and input schemas. When any scores meet the
   threshold, lower-scoring tools are excluded as `not_relevant`
   (`packages/friday-chat/src/friday_chat/tools/selection.py`).
3. A completed-turn selection snapshot is saved for command diagnostics, but
   is not an input to the next turn's ranking. The selected definitions remain
   fixed across model/tool calls *within* the prepared turn.

A read-only, offline selection probe on 2026-10-25 used two synthetic registered
MCP tools and the existing policy. `Use the Gmail write action` selected the
write-action tool. On `Yes, send it`, selection excluded that tool as
`not_relevant` and selected a send-feedback tool. This demonstrates the
mechanism; it is not an authenticated Zapier end-to-end reproduction. The
three Zapier tools currently rejected at registration include its write-action
executor, so continuity alone cannot make that executor callable. See the
[registration finding](../validation/FIND-CMD-MCP-002-registration-gap.md).

## Intended behavior

- A short follow-up within an established task should retain access to the
  relevant, **currently registered** tool, subject to the same per-turn count,
  schema, memory, and result-reservation limits.
- Tool availability must not imply a tool call or substitute for the user's
  decision to perform an external action. An ambiguous `yes` without a clear
  pending action must not trigger a write.
- A new task, expired intent, disconnected server, removed tool, or changed
  catalog must not carry a stale tool into a later turn.
- If the needed tool cannot be offered, Friday should expose a specific
  availability/budget outcome instead of claiming the action is ready.
- Keep large server catalogs registered and discoverable without pinning every
  schema into every model request. The existing `required_tools` setting can
  pin selected names but is not a practical server-wide continuity policy.

## Recommended design to evaluate

Introduce a small, session-scoped continuity signal for a *specific* pending
tool-assisted task. Derive it from the prior user request and an actually
registered candidate/tool, not from unverified server text or a broad copy of
the prior model prompt. Carry tool identifiers and bounded intent metadata,
not tool arguments, credentials, raw descriptions, or schemas. Rank the latest
request together with that signal; preserve current policy checks before any
schema is offered. Clear or revalidate it on task change, completion,
expiration, manual-mode changes, catalog refresh, or server loss.

For larger catalogs, evaluate a compact capability index or explicit tool
lookup as a later complement. That directory would identify candidates before
their full schemas are offered. It does not replace the immediate need to
handle a short continuation of an already established action.

## Decisions needed before a construction directive

| Decision | Review question |
| --- | --- |
| Continuity source | What observable state establishes a pending tool-assisted task: selected candidates, an explicit assistant action proposal, a tool call, or a combination? |
| Lifetime | When does the signal expire, and what counts as a task switch or completion? |
| Budget conflict | Should an unavailable/budgeted-out pending tool fail the turn clearly or permit an explicit alternative? |
| User control | How do manual selection and `required_tools` interact with continuity without silently changing their current meaning? |
| Catalog change | Which catalog identity/generation must be checked before carrying an MCP tool into the next turn? |
| Scope | Is the first unit limited to Friday Chat automatic selection, with any shared selector API reviewed separately for TUI reuse? |

## Required proof for a later implementation

- Deterministic two-turn tests: relevant tool survives a short confirmation;
  an unrelated follow-up does not retain it; a bare ambiguous confirmation
  cannot execute an action on its own.
- Separate tests for registration loss, catalog change, manual/required modes,
  count/schema/memory floors, and a budget failure with an observable reason.
- An integration fixture with multiple MCP and native tools, showing exact
  registered, selected, rejected, and executed names on both turns. No live
  email is needed for this proof.
- Preserve current MCP trust, output, authorization and write-action
  confirmation behavior; compare native-tool selection before and after.

The pending Zapier write executor also needs the independent schema
compatibility work. Do not claim the two-turn workflow is fixed until both
registration and per-turn selection are verified together.
