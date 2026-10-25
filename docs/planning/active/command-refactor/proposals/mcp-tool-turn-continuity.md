# Proposal — MCP tool continuity across Friday Chat turns

**Status:** maintainer policy decisions recorded on 2026-10-25; engineering
contract and construction directive still pending. No product-code authority.

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

- A short follow-up within a pending task grounded in the user's request should
  retain access to the relevant, **currently registered** tool, subject to the
  same per-turn count, schema, memory, and result-reservation limits.
- Tool availability must not imply a tool call or substitute for the user's
  decision to perform an external action. An ambiguous `yes` without a clear
  pending action must not trigger a write.
- The pending-task reminder expires at the first of: task completion,
  cancellation, a different task, session end, five subsequent user turns, or
  30 minutes. Expiry removes only the reminder. The registered catalog remains
  available for selection from a later explicit request; a bare `yes` after
  expiry requires clarification.
- Give a pending tool priority over unrelated optional tools. If it still
  cannot be offered because of registration, server availability or a budget
  limit, Friday may continue the conversation but must clearly state that the
  action cannot proceed and why. It must not silently substitute another
  action tool.
- Keep large server catalogs registered and discoverable without pinning every
  schema into every model request. The existing `required_tools` setting can
  pin selected names but is not a practical server-wide continuity policy.

## Maintainer decisions

The maintainer accepted each of these policies in the conversation on
2026-10-25. They settle intended behavior, not the implementation mechanism or
the separate schema-registration gap.

| Topic | Decision |
| --- | --- |
| Continuity source | Carry a specific pending task grounded in the user's request, with a small set of relevant tools from the actual registered catalog. A prior assistant statement or broad prior tool list alone does not establish the task. |
| Lifetime | Clear the reminder on completion, cancellation, task change or session end, and no later than five subsequent user turns or 30 minutes, whichever comes first. Clearing does not unregister a tool. |
| Budget and availability | Prioritize the pending tool over unrelated optional tools while preserving all limits. If it still cannot be offered, continue conversation with a clear reason the action cannot proceed; do not silently substitute another action tool. |
| User control | Apply continuity only in automatic mode. `required_tools` retain priority; manual mode offers its manual set plus configured required tools and does not add pending tools. |
| Catalog change | Keep a pending tool only while it still matches the same server, tool identity and validated schema in the current catalog. Otherwise discard that binding and re-evaluate the action; do not map a similar name automatically. |
| First implementation | Limit the first fix to Friday Chat automatic selection. Define continuity state without UI-specific data, but defer package relocation and TUI integration to their own architecture work. |

## Design direction and remaining engineering questions

Introduce a small, session-scoped continuity signal for a *specific* pending
tool-assisted task. Derive it from the prior user request and an actually
registered candidate/tool, not from unverified server text or a broad copy of
the prior model prompt. Carry tool identifiers and bounded intent metadata,
not tool arguments, credentials, raw descriptions, or schemas. Rank the latest
request together with that signal in automatic mode. Preserve required tools,
the memory floor and all other policy checks before any schema is offered.
Revalidate the binding against the current catalog; manual mode ignores it.
The first unit belongs in Friday Chat's automatic selection path and should
expose a UI-neutral state contract for later review.

For larger catalogs, evaluate a compact capability index or explicit tool
lookup as a later complement. That directory would identify candidates before
their full schemas are offered. It does not replace the immediate need to
handle a short continuation of an already established action.

Before a construction directive, specify how Friday records an explicit
pending task from user intent without treating assistant prose or untrusted MCP
content as authority. Define the task-change detector and the exact turn/time
expiry bookkeeping. Choose a safe schema identity/fingerprint for catalog
revalidation and an observable, non-sensitive unavailability reason. Show how
the pending candidate wins over optional tools while required/manual policy,
memory floors and other budget limits remain unchanged. These are design and
test details under the decisions above, not reopened policy choices.

## Required proof for a later implementation

- Deterministic multi-turn tests: a pending tool survives a short
  confirmation, has priority over unrelated optional tools, and is not
  executed merely because it is available. An unrelated request, completion,
  cancellation, session end, five-turn limit and 30-minute limit each clear
  the reminder. A later explicit request can reselect a still-registered tool;
  a bare ambiguous confirmation after expiry cannot trigger an action.
- Separate tests for registration loss, server unavailability, same-name but
  changed-schema catalog refresh, manual/required modes, count/schema/memory
  floors, and a clear action-unavailable result when the pending tool cannot
  fit. Confirm manual mode never adds a pending tool or displaces a required
  tool, and no similar-name tool silently replaces a changed binding.
- An integration fixture with multiple MCP and native tools, showing exact
  registered, selected, rejected, and executed names on both turns. No live
  email is needed for this proof.
- Preserve current MCP trust, output, authorization and write-action
  confirmation behavior; compare native-tool selection before and after.

The pending Zapier write executor also needs the independent schema
compatibility work. Do not claim the two-turn workflow is fixed until both
registration and per-turn selection are verified together.
