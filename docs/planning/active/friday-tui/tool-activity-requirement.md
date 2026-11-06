# Friday TUI agentic tool-activity requirement

**Status:** Accepted first-release product requirement; implementation not authorized

The TUI must show a live, chronological **Activity** view for submitted work
that invokes tools. It covers the active agent's successive model steps,
delegated agents, workflows and a user-entered `/run-tool`. Label the
responsible agent, workflow or manual command. Keep entries inspectable after
the final answer while retained in the running TUI view; `/cls` and
`/clearscreen` explicitly clear that view.

## What the user sees

Activity appears within the conversation exchange or tool-command entry,
before the final Friday response or command result. It grows as events
arrive across multiple internal model turns; no persistent side pane is
required. The inline section is internally scrollable and collapsible so
the final answer and narrow-terminal conversation remain usable. It opens
automatically with its first entry. The user can collapse and reopen it;
later entries continue to accumulate while collapsed without
forcing it open again. A visible collapsed control remains available. The
collapsed header shows the number of entries added since collapse. Count an
appended entry once, not a later status update to that same entry; reset the
count on reopen or `/cls` or `/clearscreen`. If bounded retention evicts any
counted entry while collapsed, show an eviction indicator in the header and
the detailed notice on reopen, making clear that it is no longer inspectable.
Auto-open does not steal editor focus or move the conversation viewport away
from older history being read. The user can scroll or expand a long call
without losing the final answer. Step labels group provider invocations;
actor labels distinguish delegated work.

Expanded Activity follows new entries only while its own viewport is at the
bottom. Scrolling upward pauses that following. A visible, clickable and
keyboard-focusable `Jump to latest Activity` control appears while away from
the Activity bottom; activating it or scrolling to the bottom resumes
following. It does not move the conversation viewport or latest-prompt pin,
and the conversation's separate `Jump to latest` does not move Activity.

Accepting a new conversational prompt does not change the expanded or
collapsed state of older exchanges' Activity sections. The new exchange's
Activity opens on its own first entry. Older sections remain available while
retained under the bounded view and can still be cleared or evicted under
the existing rules.

| Entry | First-release behavior |
| --- | --- |
| Executed tool | Show stable identity, actor, provider step/order, invocation ID when available, structured argument values actually passed to the tool without TUI masking, subject to a documented display-size limit, and running/completed/failed/timed-out/cancelled status. Show elapsed time when available. |
| Rejected request | After a model or user actually requests a tool, show `Not run`, the requested tool and the runtime's reason if execution is rejected before invocation. Never count or style it as an executed call. |
| Provider reasoning | When the separate visibility option is shown and the provider supplies text, label it as Friday reasoning at its actual model step, including steps after tools. A token count is not reasoning text. |
| Final response | Keep the final answer separate from Activity and provider reasoning. |

A tool omitted by pre-request selection or budget policy was never requested;
it does not create a `Not run` Activity entry. A model-emitted tool request
is not proof that a tool executed. An
execution-start entry must come from the runtime invocation boundary after
admission and validation. Snapshot parameters after runtime normalization,
immediately before delivery to the tool. Do not show streaming fragments as
executed parameters. Keep repeated calls distinct and correlate each terminal
status with its start. If future neutral execution paths run tools in
parallel, preserve their actual start and completion order; this requirement
does not itself introduce parallel execution.

Automatic agentic tool-result payloads go back to Friday for the next model
step but do not appear in Activity or the scrolling conversation. A
user-entered `/run-tool` retains its current inline command result for
command parity and also gets an Activity entry. Showing Activity cannot run
a tool again, alter its arguments, change runtime approval/security policy
or change existing Chat/`friday-cli` behavior.

Activity is bounded, in-process TUI state. It is not written to persistent
session storage, transcripts or exports. The TUI does not add credential
detection, redaction or sensitive-value filtering to the displayed
arguments in the first release, and it does not reverse runtime
normalization. Values within the per-entry size limit may wrap, scroll or
collapse and remain complete on expansion. An oversized parameter shows a
bounded preview and an explicit truncation notice; discard its overflow from
TUI memory rather than keeping a hidden full copy. The tool still receives
the complete argument. An overall rendered-history cap needs a visible
eviction notice. `/cls` and `/clearscreen` clear the displayed Activity with
the conversation and pin, without changing session history or persisted
transcripts; later work creates new entries. Users may select and copy visible
Activity text. Copy includes only the selected rendered text; for an oversized
parameter it includes the preview and truncation notice, never the discarded
overflow. The UI directive must set measurable per-entry and total limits and
bind the copy affordance and truncation behavior before construction. The first
release has no transcript-session switch, so it needs no per-session Activity
migration or restoration rule.

After a tool result returns to the model, any later provider-exposed
reasoning belongs to that later provider step. Do not attribute a later
step to one particular tool when several ran. With reasoning hidden, show
tool status and a working/continuing state without raw reasoning text.

## Source and integration boundary

`friday-llm` `ToolCallDeltaEvent` and `ToolCallCompleteEvent` describe
model-requested calls, not execution. `ReasoningDeltaEvent` can carry text
actually supplied by a provider. The current `friday-agent` loop iterates
through model responses and executes tools, but `_emit_event` is
telemetry-only and its argument field is truncated. Some retained MCP call
records omit argument values entirely. The independent TUI therefore needs
a typed UI-neutral seam with provider-step, request-rejection,
execution-start and execution-terminal events, stable correlation,
actor identity and faithful argument snapshots at execution time. It must
not import Chat's tool loop, scrape CLI text or enable telemetry for UI
status. The [replacement plan](replacement-plan.md#provider-and-tool-events)
sets the planning contract.

Source anchors: [`friday_llm/streaming.py`](../../../../packages/friday-llm/src/friday_llm/streaming.py),
[`friday_agent/repl_base.py`](../../../../packages/friday-agent/src/friday_agent/repl_base.py),
[`friday_agent/base.py`](../../../../packages/friday-agent/src/friday_agent/base.py),
[`friday_chat/tools/output.py`](../../../../packages/friday-chat/src/friday_chat/tools/output.py).

## Tests, UAT and user guide

Use deterministic providers and tools for zero, one and multiple model
steps; repeated calls; manual `/run-tool`; delegated/workflow calls;
rejection of an actual request before invocation; pre-request tool-budget
exclusions that produce no `Not run` entry; execution failure/timeout;
long and oversized arguments;
normal and Force quit; late final answers; and synthetic completion
reordering. Assert no request is displayed as executed before admission,
every rejected request has a distinct `Not run` reason, IDs and actors
remain correlated, automatic tool results stay out of Activity/chat, and
`/run-tool` retains its result. Test expansion of ordinary and
credential-shaped argument values, marked truncation without a retained full
copy, unchanged execution arguments, bounded memory, non-persistence/export
and responsive navigation. Test that `/cls` and `/clearscreen` remove old
Activity from the displayed view and later work adds fresh entries without
changing session history. Test that copying selected visible Activity includes
only the bounded preview and notice for an oversized argument, with no hidden
overflow. Verify first-entry auto-open, user collapse and reopen, retained
entries accumulating while collapsed, and no forced reopening on later
entries. Assert the collapsed count increments only for appended entries,
resets on reopen and display clear, and coexists with an eviction indicator
while collapsed and a detailed notice on reopen.
Test Activity following at bottom, pause while reading earlier entries,
return by its own control or scrolling, and independence from conversation
navigation. After a new prompt, verify that older Activity sections retain
their individual expanded/collapsed states and the new section opens
independently.
Hidden/shown reasoning tests include text,
count-only and absent cases.

Perform macOS milestone UAT and final-candidate macOS/Linux installed
terminal UAT. Final acceptance additionally requires a controlled real
provider and executing tool after the provider and permitted effects are
selected. The [TUI guide](user-guide-requirements.md) must explain
Activity labels, parameters, statuses, `Not run`, actor labels, scrolling,
the request/execution distinction, and the `/run-tool` result exception.
