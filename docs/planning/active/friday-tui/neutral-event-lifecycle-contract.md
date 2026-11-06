# Friday TUI event and lifecycle integration contract

**Status:** Source-backed design proposal; exact API and implementation owner
require separate directives. No product-code authority.

**Branch/source:** `feature/friday-tui` /
`c34269867be50f71923c93c95a63236a35505812`

The independent TUI needs execution facts and safe cleanup from UI-neutral
Friday services. It cannot import Chat's turn processor, tool loop, application
or terminal display. This document narrows the future TUI-N01B/N01C,
TUI-N02A/N02B and TUI-N06 contracts without adding those features to the
[first identity directive](directives/CD-TUI-N01S-session-identity.md).

## Source boundaries

| Existing source | What it proves | What it does not prove |
| --- | --- | --- |
| [`LiteLLMService.chat_completion_events()`](../../../../packages/friday-llm/src/friday_llm/service.py) and [typed stream events](../../../../packages/friday-llm/src/friday_llm/streaming.py) | Provider text, reasoning, tool, usage and finish events have typed representations. | A configured TUI operation receives them, or every provider supplies reasoning text. |
| [`FrameworkChatModel.stream_complete()`](../../../../packages/friday-chat/src/friday_chat/adapters.py) | Chat's text streaming path forwards text and discards reasoning, usage and finish events. | TUI reasoning visibility or a neutral per-step stream. |
| [Chat tool loop](../../../../packages/friday-chat/src/friday_chat/tools/loop.py) and [manual tool handler](../../../../packages/friday-chat/src/friday_chat/commands/registry.py) | Requests, admission and actual native/MCP invocation have different boundaries. | A model tool request means execution started; the Chat loop can be imported by TUI. |
| [MCP invocation](../../../../packages/friday-chat/src/friday_chat/tools/mcp.py) and [retained output policy](../../../../packages/friday-chat/src/friday_chat/tools/output.py) | Arguments are available before the call; retained MCP records intentionally replace them with `{}`. | A post-call record can supply the executed-argument Activity view. |
| [Chat application shutdown](../../../../packages/friday-chat/src/friday_chat/app.py), [maintenance coordinator](../../../../packages/friday-chat/src/friday_chat/reorganization/coordinator.py) and [headless DI shutdown](../../../../packages/friday-runtime/src/friday_runtime/di.py) | Chat drains/finalizes more resources than DI shutdown currently handles. | `DIContainer.shutdown()` alone provides TUI safe Quit or partial-start cleanup. |

## Event contract to bind in TUI-N02 directives

One neutral operation owns an ordered event stream and one terminal outcome.
Every event carries an operation ID and monotonic sequence number; model-step
and tool-invocation events additionally carry distinct step/invocation IDs and
actor identity. The frontend may transform these facts into bounded Activity,
but it must not parse CLI text or infer execution from a tool-call request.

| Stage | Required event facts | Source rule |
| --- | --- | --- |
| Provider step | Start/terminal state and step ID for each internal model call. | Emit around actual model invocation, including follow-up after a tool. |
| Reasoning text | Provider-supplied text, ordered within that step. | Capture before a text-only adapter drops it. A token count alone supplies no text. |
| Tool requested but not run | Tool identity and rejection reason after an actual model/user request fails admission. | Pre-request selection exclusions produce no tool Activity entry. |
| Tool execution started | Stable invocation ID; native/MCP identity; actor; bounded snapshot of the arguments after validation/normalization and immediately before the callable receives them. | Do not reconstruct arguments from retained MCP records or render an unbounded value. The callable still receives its full validated input. |
| Tool execution terminal | Same invocation ID; completed, failed, timed-out or cancelled status and elapsed time if known. | Failure after invocation starts is an executed-call failure, not `Not run`; no automatic tool-result payload is added to Activity. |
| Answer | Ordered final-answer chunks or final text separate from reasoning and tool Activity. | Keep the existing transcript/persistence policy; TUI Activity is in-process view state. |

The sink must preserve order within an operation and distinguish repeated tool
names and delegated actors. Its queue must have a finite bound and explicit
overflow/failure state; a UI subscriber failure must not silently change an
already admitted provider/tool effect. The event directive must fix the public
types, owning package, delivery/overflow policy and exact native/MCP/manual
hook points, then test fake, real-adapter and failure paths. Reasoning defaults
hidden in TUI; the visible option applies forward only and never invents
reasoning where a provider supplied none. No extra TUI masking of arguments is
required by the current product decision.

## Lifecycle contract to bind in TUI-N01B/N01C and TUI-N06

The TUI owns terminal and presentation teardown. A neutral runtime session
owns acquired model clients, MCP providers, maintenance/compaction tasks,
transcript stores and other services. The startup API must either return a
fully usable owner or retain a reachable partial owner for cleanup; a failure
must never drop the only reference to an acquired resource.

Normal Quit first stops new TUI admission, then waits for the accepted
non-interruptible operation to reach its owner-defined safe stopping point.
After that, stop tool admission/providers, drain/finalize configured maintenance
and transcripts, close owned async clients and restore the terminal. The
neutral close operation must be safe to call after partial startup and must
report which stages succeeded or failed. The TUI preserves the original
startup/operation error alongside cleanup errors and offers chooser Retry only
when cleanup succeeded, per the [startup contract](startup-bootstrap-contract.md).
Completed tool and memory effects are not rolled back by a later failure.

Force quit is a distinct, warned and confirmed emergency path available while
normal Quit waits. It may leave work or persistence incomplete and must report
that uncertainty. An in-process task or thread cancellation alone does not
prove a non-interruptible mutation stopped. The TUI-N06 directive must bind
an actual termination boundary, best-effort terminal restoration, exit status
and recovery instructions before implementation. No mechanism is approved by
this document merely because it appears viable in a fake test.

## Small-unit evidence gates

1. TUI-N01B: disposable partial-start and cleanup-failure fixtures establish
   ownership, close idempotence, retained primary error and typed status;
   existing Chat/`friday-cli` results remain unchanged.
2. TUI-N01C: identical runtime files, environment and captured launch cwd
   produce equivalent real/fake model, tool, memory, transcript, maintenance
   and path behavior from Chat and a neutral caller; compare shutdown effects
   and failed-start cleanup on disposable stores.
3. TUI-N02A: fake and adapter tests cover multi-step text/reasoning order,
   hidden/show-forward behavior, missing reasoning, final-answer separation,
   no new persistence and source event closure.
4. TUI-N02B: exercise accepted, rejected, timed-out and failed native/MCP
   requests, delegated and manual tool calls, repeated names, argument
   normalization, bounded display snapshots and no automatic result payload.
   Prove the executed callable receives the full argument value while the
   view uses its bounded snapshot.
5. TUI-N06: exercise real terminal/PTY restoration and slow or stalled work;
   use user macOS UAT and final installed Linux UAT in addition to automated
   tests. Do not call an automated pass user acceptance.

The first proposed TUI-N01S identity extraction has none of these event or
resource effects. Each later directive must resolve its exact public types,
hook points, bounds and failure behavior before product code is authorized.
