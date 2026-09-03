# FridayV2 Turn Integration Remediation Plan

This plan fixes functional FridayV2 parity failures discovered during manual CLI
testing: tool calls are not executing during normal conversation turns,
background memory work is not producing summaries, and current-session context is
not reliably reaching the model.

## Problem

FridayV2 currently has several low-level components that pass isolated tests, but
the normal interactive turn path does not wire those components together like the
reference CLI at `tests/integration/memory/friday.py`.

Observed symptoms:

- Asking for the current date can return nothing or no useful answer.
- Tool calls requested by the model are not executed as part of the conversation
  turn.
- Transcript persistence appears to work, but prior turns are not reliably used
  in later model prompts.
- After several turns, asking for a summary can produce an answer that claims the
  conversation has just started.
- Background extraction/summarization does not appear to run as real memory work.
- On CLI exit, configured reorganization cleanup does not appear to run with the
  real `friday.py` cleanup behavior.

Likely implementation causes in the current FridayV2 package:

- The FridayV2 chat model protocol returns only `str`, so structured provider
  fields such as `tool_calls`, usage, and reasoning content are lost.
- The framework chat adapter converts tool-call-only responses into text instead
  of returning executable tool calls.
- `TurnProcessor` builds `prompt_text`, but the LLM call receives only the raw
  user message plus optional tool context, so system prompt, assembled context,
  and current-session history may not reach the model.
- The standalone `ToolLoop` is not integrated into the normal conversation turn
  path.
- Real-runtime construction still uses fake maintenance services, so extraction,
  summarization, lifecycle, and compaction behavior are not equivalent to
  `friday.py`.
- Exit maintenance currently proves only a fake action record. It does not prove
  the reference `MemoryReorganizer` cleanup path, maintenance LLM role selection,
  fast/full mode behavior, user-facing progress messages, or error handling.
- Background extraction scheduling does not buffer every completed turn before
  interval checks, which can lose turns when extraction interval is greater than
  one.

## Decisions

- Treat this as a release-blocking Friday compatibility remediation.
- Add tests before implementation so the current failures become reproducible.
- Keep changes inside `packages/friday-chat`, its tests, launcher/config
  examples, and FridayV2 planning docs.
- Do not modify frozen framework packages. Missing framework capabilities must be
  logged in the framework upgrade log and adapted at the FridayV2 boundary.
- End-to-end behavior matters more than low-level component existence. A tool
  loop that passes unit tests but is not invoked by chat turns does not satisfy
  compatibility.

## Reference Behavior

The reference `friday.py` turn path:

- Assembles context before every turn.
- Formats the prompt with system prompt, supporting context, history, tools, user
  query, and turn count.
- Uses streaming LLM calls when no tools are active.
- Uses a non-streaming tool loop when tools are active.
- Executes returned tool calls, appends tool results to the model message list,
  and repeats until the model returns final content or max iterations is reached.
- Persists the interaction, stores raw prompt/response context logs when
  configured, buffers the turn for extraction, and schedules extraction at the
  configured interval.
- Flushes pending extraction before compaction and on exit when configured.
- On exit, checks `session.flush_on_exit`, `session.lifecycle_on_exit`, and
  `session.reorganize_on_exit`; when any are enabled, displays exit maintenance
  progress and runs cleanup before transcript finalization.
- If `session.reorganize_on_exit` is enabled and a persistence directory exists,
  constructs `MemoryReorganizer` with maintenance config, maintenance LLM roles,
  embedding function, collection manager, access buffer, lifecycle components,
  and graph store where available.
- Runs reorganization with `dry_run=False`, `backup_first=True`,
  `skip_lifecycle=True`, and fast-mode synthesis/verification skips.

## Implementation Steps

1. Add failing compatibility tests.

   Add integration-style fake tests under `packages/friday-chat/tests_chat/compat`
   that exercise the real `FridayChatApp` plus `TurnProcessor`, not only isolated
   helper classes.

2. Introduce a structured chat response model.

   Replace the `str`-only internal LLM contract with a FridayV2-owned response
   type that can carry final content, tool calls, usage, reasoning content, and
   raw provider metadata. Keep fake and framework adapters behind that boundary.

3. Fix prompt/message assembly.

   Ensure the LLM receives the effective system prompt, assembled supporting
   context, current-session history, prior-session history where available,
   active tool schemas/context, the current query, and the current turn count.
   The stored raw prompt must match what was actually sent to the model.

4. Integrate tool loop into normal turn processing.

   When active tools are present, route conversation turns through the tool loop.
   Execute provider-returned tool calls using the configured tool registry,
   sanitize tool outputs for model context and memory storage, append tool
   results to working messages, and continue until final content or max
   iterations.

5. Add current-date/date-tool acceptance coverage.

   Add a deterministic fake LLM/tool test where the model requests the configured
   date/time tool and the final assistant response includes the tool result. This
   guards the user-facing failure where asking for the date returns nothing.

6. Repair current-session context flow.

   Make current-session history a first-class input to prompt assembly. After
   multiple turns, a summary request must receive earlier user and assistant
   turns in the prompt/context passed to the model.

7. Repair background extraction buffering.

   Buffer every successfully persisted turn. For interval `N`, extract the full
   buffered batch on turns `N`, `2N`, and so on. For interval `0`, extract every
   turn. For interval `-1`, defer extraction until exit flush.

8. Replace fake maintenance in real runtime where framework support exists.

   Wire real extraction, summarization, lifecycle, and compaction services from
   existing framework packages into real runtime mode. If a required framework
   capability cannot be used without editing frozen packages, log it in the
   framework upgrade log and implement the narrowest FridayV2 adapter fallback.

9. Restore budget-aware in-session compaction.

   Match `friday.py` background compaction behavior: initialize
   `ContextBudgetMonitor` and `InSessionCompactor` from `memory.compaction`;
   after each successful persisted turn, record the actual prompt budget status
   and schedule background compaction when the monitor threshold is crossed.
   Compaction must flush pending extraction first, pass time-budget and token
   budget context into the compactor, mark completion on success or failure, and
   gate the next chat prompt until any in-flight compaction task completes.

10. Restore real exit reorganization cleanup.

   Ensure FridayV2 exit maintenance matches `friday.py`: configured exit
   maintenance emits progress, flushes pending extraction first, runs access
   buffer flush, runs lifecycle, then runs real reorganization when
   `session.reorganize_on_exit` is true. Fast mode must skip synthesis and
   verification LLM work; full/deep mode must wire configured maintenance LLMs
   where available. Errors should be reported as warnings without preventing
   transcript finalization.

11. Preserve transcript behavior.

   Keep transcript persistence working, but verify transcript data also feeds
   current-session and prior-session context according to the configured memory
   settings.

12. Run validation and manual UAT.

    Run automated tests, then perform a CLI UAT script that covers date/tool use,
    multi-turn summary, `/context`, `/prompt`, `/summaries`, and exit maintenance
    with reorganization enabled.

## Test Matrix

| Area | Required proof |
| --- | --- |
| Tool-call response preservation | Framework and fake LLM adapters preserve structured tool calls instead of reducing them to text |
| End-to-end tool execution | A normal conversation turn executes a returned tool call and feeds the tool result into the final model answer |
| Date/time UAT | Asking for the date/time executes the configured date/time tool and produces a non-empty answer with the tool result |
| Empty tool-call response | A tool-call-only model response never becomes an empty assistant response |
| Prompt delivery | Actual LLM messages contain effective system prompt, supporting context, current query, and active tools |
| Current-session history | After several turns, a later summary request receives previous turns in model context |
| Turn count | Prompt assembly receives the correct current turn count rather than resetting every turn |
| Raw prompt capture | Stored raw prompt/context log matches the message payload sent to the LLM |
| Background buffering | Extraction interval `N` extracts all buffered turns, not just the trigger turn |
| Exit extraction | Interval `-1` buffers turns and flushes them on exit when configured |
| Budget monitor initialization | `memory.compaction.enabled` creates the real budget monitor and compactor when framework dependencies are available |
| Budget compaction trigger | After a persisted turn, prompt budget status is recorded and threshold breach schedules background compaction |
| Budget compaction ordering | Pending extraction flushes before compaction; the next chat prompt awaits in-flight compaction before processing |
| Budget compaction payload | Compactor receives session id, trigger reason, time budget, current tokens, available budget, and target utilization |
| Summaries | Background or manual compaction/summarization produces summary records visible through `/summaries` |
| Transcript-to-context | Persisted transcript turns can be recalled into context according to config |
| Exit reorganization config | `session.reorganize_on_exit` and `session.reorganize_mode` control real exit cleanup |
| Exit reorganization order | Pending extraction, access flush, lifecycle, and reorganization run in reference order before transcript finalization |
| Exit reorganization mode | Fast mode skips synthesis/verification; full/deep mode wires configured maintenance LLM roles |
| Exit reorganization errors | Reorganization failures are warning-level exit-maintenance errors and do not prevent transcript finalization |

## Manual UAT Script

Run against a real or local-model config with tools enabled:

```text
What is today's date?
Remember that my FridayV2 smoke-test project is testing turn context.
What project am I testing?
Give me a summary of our conversation so far.
/context
/prompt
/summaries
/q
```

Expected result:

- The date question produces a real answer using the date/time tool.
- The memory/context question sees earlier turns.
- The summary does not claim this is the first turn.
- `/context` and `/prompt` show prior turns or assembled supporting context.
- `/summaries` shows generated summaries after extraction/compaction has run, or
  the test explicitly explains why the configured interval has not produced one.
- With `session.reorganize_on_exit: true`, exiting displays/runs configured exit
  maintenance and invokes real reorganization before transcript finalization.

## Acceptance Commands

```bash
uv run pytest packages/friday-chat/tests_chat/compat
uv run pytest packages/friday-chat/tests_chat
uv run ruff check packages/friday-chat
uv run mypy packages/friday-chat
git diff --check
printf '/q\n' | scripts/run-friday-chat-example.sh
```

## Completion Criteria

- Normal conversation turns can execute tool calls end to end.
- Current-date/date-tool UAT passes with a configured tool.
- Multi-turn summary UAT proves current-session context reaches the model.
- Background extraction buffering follows the configured interval semantics.
- Real runtime no longer silently substitutes fake maintenance for required
  extraction/summarization behavior without a logged framework-upgrade item.
- Exit maintenance in real runtime runs configured reorganization cleanup with
  reference ordering, mode semantics, and transcript-finalization safety.
- The relevant parity matrix rows move from `deferred` to `tested`.
- No frozen framework package source or tests were changed.
