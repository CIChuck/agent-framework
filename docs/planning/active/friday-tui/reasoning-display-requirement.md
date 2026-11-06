# Friday TUI reasoning display requirement

**Status:** Required in the first TUI release, confirmed by the maintainer.
No product implementation is authorized by this record.

**User intent:** Let a person choose whether the TUI shows thinking information
that a model provider actually supplies. Keep the familiar final-answer-only
view as the default. This is a TUI presentation choice; it does not ask the
model to generate reasoning, change its reasoning effort or change the existing
CLI.

## Required first-release behavior

1. Add a documented TUI-only setting,
   `tui.output.reasoning_visibility: hidden | shown`, to the existing
   presentation file. Default to `hidden`. Show the active choice in a
   discoverable TUI control or help view. Provide an in-app toggle that
   changes the view for subsequent reasoning events, including later steps
   of an in-flight response. It does not rewrite the configuration file.
   Earlier text received while hidden is not retained for later reveal.
   Exact key/menu placement belongs in the implementation contract.
2. With `hidden`, show Friday's final answer and normal status/tool activity;
   do not render raw reasoning text. With `shown`, render only reasoning text
   actually returned by the provider, in a clearly labeled, separate,
   collapsible area associated with the response or provider invocation.
   Distinguish that area from Friday's final answer, command results and
   progress. Place it in the chronological Activity view with separate
   reasoning labels, including model steps after tool execution. Do not show
   tool-result payloads there. Preserve event order when streaming and do not
   duplicate text.
3. A provider may expose reasoning text, a reasoning-token count, both or
   neither. A count is usage data, not viewable reasoning text. When `shown`
   is selected but no text is supplied, state that no reasoning text was
   provided; do not synthesize an explanation or imply that the model did not
   reason. The final answer remains available in every case.
4. Keep reasoning display transient and bounded. Discard hidden reasoning
   at the TUI view boundary rather than storing it for a later toggle. Do not
   add raw reasoning to
   normal transcripts, exports, memory, telemetry or logs by default. Define
   explicit limits and the behavior of the view setting, `/cls` and application
   exit before construction. The first release has no transcript-session
   switching control. Any later retention/export feature requires its own
   policy and acceptance decision.
   Shown reasoning may be selected and copied as visible text. Text received
   while hidden is not retained and cannot be copied; copying does not add
   reasoning to normal transcripts or exports.
5. Use UI-neutral Friday LLM/runtime events and responses. The TUI must not
   import `friday-chat` or `friday-cli`, depend on their text-only adapter or
   alter their current output. Keep the generation setting in runtime config
   separate from this view setting in presentation config.

## Current source boundary

The premise that all reasoning is discarded in `friday-llm` is too broad.
`friday-llm` defines `ReasoningDeltaEvent` and optional reasoning-token usage,
emits reasoning deltas when the provider supplies them, and retains
`reasoning_content` in typed non-streaming responses. The current
`friday-chat` text-stream adapter ignores reasoning and usage events, so they
are absent from the user-visible text stream. Its normal response serializer
also omits reasoning text. The independent TUI needs its own UI-neutral event
path rather than reusing that display adapter.

Source anchors: [`friday_llm/streaming.py`](../../../../packages/friday-llm/src/friday_llm/streaming.py),
[`friday_llm/service.py`](../../../../packages/friday-llm/src/friday_llm/service.py),
[`friday_chat/adapters.py`](../../../../packages/friday-chat/src/friday_chat/adapters.py),
[`friday_chat/turns/processor.py`](../../../../packages/friday-chat/src/friday_chat/turns/processor.py).

## Test and documentation contract

Test hidden/default and shown settings and a forward-only in-app toggle
with a provider stub that emits text
deltas, reasoning deltas and usage, plus cases with counts only
and no reasoning data. Cover toggling during an in-flight response without
retroactive reveal or config-file writes, streaming, tool follow-up invocations, ordering
relative to actual tool execution, and the absence of tool-result payloads,
collapse/scroll behavior, copying only selected shown text and never hidden
reasoning, bounds, lack of transcript/export/log persistence,
and unchanged CLI output both with and without the TUI installed. Test the
setting through the installed application on macOS and Linux; include it in
first-release user UAT. Explain the control and provider-availability caveat in the
[TUI guide requirement](user-guide-requirements.md), with detailed setting
values/defaults in `docs/guides/10-configuration.md` before release acceptance.
