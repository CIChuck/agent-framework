# Friday TUI technical integration contract

**Status:** Withdrawn technical proposal; retained as historical design evidence

**Branch:** `feature/friday-tui`

**Baseline:** `c34269867be50f71923c93c95a63236a35505812`, Friday `0.1.0a4`

The maintainer now requires an independently installable `friday-tui` with no
imports or dependencies on CLI code or packages. The Chat-app, Chat registry,
Chat display-reader and Chat shutdown-report proposals below violate that
boundary and must not be implemented. See the controlling
[architecture reset](architecture-reset.md) and [decisions](decisions.md).

This contract records technical choices under the accepted product requirements
in [decisions.md](decisions.md). The UX configuration design in T-02 is accepted;
other technical proposals and product construction remain subject to review.
Proposed interfaces below do not exist merely because this document names them.

## 1. Invariants

1. Existing `friday-cli` implementation, features, public contracts and behavior
   remain unchanged. Existing Chat CLI invocations retain their behavior.
2. The existing Chat command registry/handlers, runtime, session identity,
   maintenance coordinator and cleanup own backend behavior. TUI widgets do not
   implement a second command engine or call private application methods.
3. Current command/argument/alias coverage is the initial baseline. TUI-owned
   extensions can grow `/` capabilities without changing existing CLI defaults.
4. Initial targets are macOS and Linux; input is a multiline editor with an
   explicit submit shortcut. Quit waits for an owner-defined safe stopping point,
   finishes non-interruptible work and completes cleanup before exit.
5. CLI and TUI are UX layers over the same Friday runtime infrastructure.
   Runtime configuration files, schemas, interpretation, precedence, model
   routing, credential references, service opt-ins and storage resolution remain
   compatible. Frontend presentation settings cannot override runtime behavior.

The [command matrix](command-matrix.md) records current syntax and required
parity evidence. [Technical evidence](validation/technical-evidence.json) records
the source/metadata checks and limited current-code baseline test profile.

## 2. T-01: Textual and dependency policy

Propose `textual>=8.2.8,<8.3`, initially locked to `8.2.8`, without the optional
syntax extra. Official [PyPI metadata](https://pypi.org/project/textual/8.2.8/)
declares Python `>=3.9,<4` and Rich `>=14.2.0`; Friday requires Python `>=3.13.4`.
The existing lock already has Rich `14.2.0`, Markdown-it `4.0.0`, Pygments
`2.19.2` and typing-extensions `4.15.0`.

A metadata-only overlay resolution preserves those versions and resolves nine
packages, including Textual and three new transitive packages. It installs nothing and
does not prove full-workspace or installed UI compatibility. Keep the existing
lock records fixed during the eventual full workspace resolution; disclose and
review any additional change. Textual upgrades require rerunning the CLI and UI
compatibility profiles rather than floating to an untested minor release.

The primary terminal targets are macOS Terminal.app on arm64 and Ubuntu 24.04
GNOME Terminal on x86_64. Record actual OS/terminal versions with execution
evidence. The present host is macOS `27.0.1`/arm64 with Python `3.13.10`; Linux
and real Textual UI behavior have not been tested in this planning slice.
Release acceptance requires both OS targets, plus headless minimum-size tests.

## 3. Execution ownership and responsiveness

Use two owned loops: Textual's main/UI loop and one backend loop on a dedicated
worker thread. Construct, run and close the Chat runtime and all its async
clients on the backend loop. Never move an existing live runtime between loops.

This refines the earlier same-loop proposal: existing `/read` and `/ingest`
handlers call synchronous file readers. A UI-thread async task would still block
rendering during those reads. Isolating the whole backend preserves those
handlers and its existing execution/maintenance ordering.

The TUI owns a supervisor and bounded thread-safe input/output bridges. All
Textual/widget updates occur on the UI thread through supported messages or
`call_from_thread`. The [Textual worker guide](https://textual.textualize.io/guide/workers/)
documents thread/UI boundaries. A cancelled worker flag is not proof the backend
thread or a write stopped. Do not use exclusive worker replacement to abort Chat.

| Owner | Responsibilities |
| --- | --- |
| UI loop | Editor, views, focus, discovery snapshot, input admission and presentation of received events. |
| Backend loop/thread | Chat config/runtime construction, registry and context, one `FridayChatApp.run()`, handlers, maintenance and client closure. |
| Bridge/supervisor | Thread-safe submit/quit requests, ordered events, backpressure and worker completion; no backend state mutation from UI callbacks. |

Only one submitted backend operation is active. While busy, users can edit and
navigate; a submit attempt returns `busy` and retains the editor text. Clear the
editor only after an accepted submission. Do not queue speculative commands or
deduplicate separate deliberate invocations by their text.

## 4. T-02: pure display configuration

Add this public Chat API in `friday_chat.display`:

```text
read_display_config(*, config_path: Path | None,
                    cli_config_path: Path | None = None) -> DisplayConfigResult
```

It returns fresh configuration values with the existing precedence: explicit
file, sibling `cli-config.yaml`, then defaults. Preserve existing validation,
error classes/messages and response/banner value parsing. It must not call
`set_cli_config`, `reset_console`, `get_console`, or a global configuration getter.

Keep `resolve_display_config` as the existing CLI activation API. It may compose
the pure reader with its existing activation, but successful activation order,
error behavior, rendering and CLI globals must remain unchanged for its callers.
No `friday-cli` file changes are needed.

The TUI maps theme colors and configured user/assistant names to its own styles.
It renders a compact header, rather than terminal banner art. An explicit file
with inapplicable banner/spinner settings gets one nonfatal startup diagnostic;
default values do not generate repeated warnings. No config file is rewritten.
The exact field mapping must be tested when the TUI adapters are constructed.

### Extend the existing CLI presentation file

[The accepted UX configuration design](ux-configuration.md) extends the same
`cli-config.yaml`/`--cli-config` file with an optional, versioned `tui:` namespace.
Keep existing root theme/icons/prompt/response/banner/spinner sections, defaults
and CLI interpretation unchanged. Existing CLI loaders already ignore additional
root keys. TUI-owned typed settings cover layout, editor, keybindings, output,
discovery, accessibility and TUI chrome; applicable shared styles/messages retain
their current meaning. Old files work without a `tui` section.

This replaces the earlier separate `tui-config.yaml` suggestion. Bind the new
namespace reader and exact fields/tests in the later TUI-01A directive;
CD-TUI-001 remains limited to its two shared APIs and five product/test paths.
The presentation-file design and UX option families are accepted. Exact fields,
bounds, reader APIs and product paths must be bound in construction directives;
no new setting/widget behavior has been implemented or user-tested.

## 5. T-03: replay and startup

Normal startup uses the existing Chat config/model-library parser and fake/real
factory selection, including `FRIDAY_CHAT_RUNTIME` precedence. Installed help
and version inspection start no runtime services. TUI display loading uses the
pure API above; it does not call the activating CLI resolver.

### Shared runtime configuration surface

Use the current `load_friday_py_config()` and `build_runtime()` path used by
Chat. One existing main YAML and its referenced model catalog must work in
either frontend without translation, duplication or rewriting. Memory and other
service settings retain their current schema. Do not introduce a TUI-specific
runtime YAML, loader, runtime defaults or model/memory override layer.

For the same files, environment, runtime selection and captured launch/workspace
context, both frontends must resolve equivalent runtime settings, service
bindings, storage paths and configuration errors. Preserve model-library paths
relative to the main YAML and existing data-path resolution against captured
process cwd. Do not silently rebase data paths or change process cwd for the TUI.
Portable installed configurations should use explicit absolute data paths.

User-owned directories such as `~/.config/friday/` and
`~/.local/share/friday/` are placement conventions, not new lookup rules. Named
profile directories can group existing files for either frontend; they do not
create a second configuration format. TUI browsing/selection may supply an
explicit `--config` path to the shared loader. Automatic profile discovery,
new precedence or configuration-generation behavior remains a separate shared
startup-contract proposal; none is approved or implemented by this clarification.

The optional future `tui:` namespace in the existing CLI presentation file is
limited to UX settings. It cannot contain or override models, credentials, memory
paths, maintenance, tools, MCP, security policy or runtime-mode selection. Runtime
files remain usable without TUI-specific preferences. Existing CLI configuration
and behavior remain unchanged; TUI-only schema errors do not add validation to
existing CLI startup. Malformed YAML retains current whole-file error behavior.

Two replay paths remain distinct:

- Interactive `/replay <csv_path> [delay_seconds]` uses the active session and
  existing handler, including its current reset/state behavior. Display the actual
  result; do not add/remove execution flags or change the parser.
- `friday-tui --replay <csv_path> [--replay-delay <seconds>]` opens a dedicated
  offline replay view using an isolated default fake runtime, as the current CLI
  startup path does. Display reset/result text and retain the view until Quit;
  do not open a real chat session afterward automatically.

Preserve the current CLI launch precedence: version inspection first, then
startup replay, then configured interactive startup. Startup replay therefore
uses its existing isolated fake runtime even when configuration/display/runtime
options are supplied; do not add TUI-only conflicting-mode rejection or load an
otherwise ignored configuration. Retaining the replay result view is a UX
choice. Invalid paths/delays produce visible errors through the existing rules.

## 6. T-04: safe Quit and shutdown outcome

The TUI input adapter implements the existing `InputSource.read() -> str` async
boundary. Quit uses a separate idempotent intent flag/wakeup, not a slash command
placed behind other input and not `Task.cancel()` on the backend task.

At the next input-admission boundary it raises `EOFError`, allowing Chat's normal
`finally` cleanup to run. If Quit races with a submission, close admission first:
input not yet handed to Chat is rejected and retained visibly; input already
handed to Chat completes its owner-defined operation before the EOF boundary.
The UI remains mounted and drains output during this process.

For this first contract, the safe stopping point of an existing submitted
operation is its return to the app's input boundary. Existing handlers and turns
do not expose a general cooperative interruption contract. Do not invent one.
The tradeoff is that Quit can wait for a slow operation or its configured timeout.
Future earlier stopping points require explicit owner-provided hooks and tests.

| Active operation | Initial Quit rule |
| --- | --- |
| Idle input wait | Wake with EOF and begin shared cleanup. |
| Generation/turn, tool or agent/workflow request | Finish the admitted invocation, including its persistence, then EOF/cleanup. No blind cancellation. |
| File read/ingest, replay, reset or other mutation | Finish the admitted command. Replay's whole invocation is the boundary until its owner exposes a finer safe hook. |
| Exclusive maintenance/recovery | Let the coordinator finish or report failure; preserve recovery artifacts and existing admission. |
| Cleanup already running | Repeated Quit is idempotent; keep showing progress, not a second cleanup attempt. |

Retain the existing MCP-stop, maintenance/extraction drain, transcript finalization
and async-client closure sequence. The TUI must wait for backend completion before
destroying views or releasing the terminal. It must not force-kill a pending
write to satisfy a UI timeout.

Add an immutable public `AppShutdownReport` in `friday_chat.lifecycle`, exposed
through a read-only `FridayChatApp.shutdown_report` property:

```text
cleanup_outcome: "not_attempted" | "succeeded" | "failed"
stop_reason: "command_exit" | "eof" | "keyboard_interrupt" |
             "startup_failed" | "application_failed" | "cancelled" |
             "shutdown_failed"
```

Before a run and while running, the property is `None`. After a run returns or
raises, it reports cleanup truth for that run only. Startup failure before
lifecycle entry means `not_attempted`; cleanup failures caught by existing hooks
mean `failed`. A run failure with successful cleanup remains an application
failure, with cleanup reported separately. Use categorical data only.

This is an additive observation API. Preserve `AppRunResult`, exception propagation,
existing telemetry events and all cleanup behavior. Do not perform new cleanup
merely to populate the report. On a failed run/cleanup, show failure and retain
the view for acknowledgement after the worker has terminated; never label it
successful. Do not inspect private telemetry flags from TUI code.

## 7. T-05: output and status bridge

Keep the current text/stream/display protocols as the backend boundary. TUI-owned
immutable bridge events carry: command/progress text, assistant begin/chunk/end,
clear-view, heartbeat changes, session state and the final run/shutdown outcome.
They are presentation messages, not a second telemetry or persistence system.

Assign ordered sequence numbers in one backend publisher; preserve every text
character and stream order. Bound the transport queue and apply backpressure.
Split large text into ordered transport pieces rather than silently truncating
the command result. Heartbeat/status snapshots may be coalesced; command and
assistant content may not be dropped. Retain visible truncation markers when
limiting the rendered view; never delete persisted transcripts through that cap.

Generic command output stays command output: the current `write(str)` hook has
no severity or table schema. Do not scrape text to infer success, mutation state
or structured diagnostics. Status comes from the host's input/run state,
heartbeat hooks and the public shutdown report. Typed richer events can be a
later additive contract. No stdout capture, console replacement or telemetry
enablement is required to drive UI state.

## 8. T-06: slash-command growth

Build a fresh default Chat registry on the backend, register explicitly selected
TUI-owned modules through its existing public `register()` API, and inject that
registry/context into `FridayChatApp`. CLI registry construction remains unchanged.
Duplicate canonical names or aliases fail startup before normal input.

Send an immutable metadata snapshot to the UI for help/completion/palette use;
do not share the mutable registry object across threads. Palette actions submit
the same text/operation through normal admission. Shared handlers remain free
of Textual imports and use typed context/capability contracts.

Prove extension with a test-only command registered by a fixture. It must become
visible and execute without changing inherited handlers or generic UI dispatch.
Do not ship that fixture in the default production command set. Automatic
filesystem plugin discovery and hot reload are outside the initial contract.

## 9. T-07: initial keyboard and layout proposal

Use Textual [`TextArea`](https://textual.textualize.io/widgets/text_area/) in
plain-text multiline mode. The proposed bindings are:

| Input | Effect |
| --- | --- |
| Enter | Insert newline; pasting never submits partial lines. |
| F2 | Submit the entire editor once; a focusable Submit button provides a keyboard fallback via Tab/Enter. |
| F3 / F4 | Previous/next submitted prompt; preserve the unsent draft when browsing history. |
| F1 | Open slash-command help/discovery from the metadata snapshot. |
| Ctrl+P | Registry-backed command palette. |
| Tab / Shift+Tab | Move focus between accessible controls; command completion is chosen through discovery, not by stealing all focus navigation. |
| Ctrl+L | Clear the visible result/conversation area; same display-only effect as `/cls`. |
| Ctrl+Q, palette Quit, `/q` or `/quit` | Request the same graceful Quit path. Override Textual's direct-exit action; no shortcut may bypass it. |
| Ctrl+C | Copy selected text in the editor/output; it is not the TUI's Quit shortcut. Existing CLI Ctrl+C behavior is unchanged. |
| Escape | Dismiss a popup/return focus; does not cancel backend work. |

This avoids assuming modified Enter keys have portable terminal encoding. Record
actual key delivery on both target terminals, including Mac function-key settings.
If F2 is intercepted by the desktop, the focusable Submit button remains usable
without mouse interaction. Do not introduce an untested alternative silently.

Minimum usable size is 80x24. Collapse the workspace below 100 columns; provide
the full split layout at 120x30 or larger. Below minimum size show a resize hint
and keep Quit reachable. Preserve scroll position while reading older output,
provide jump-to-latest and avoid color-only status indicators.

## 10. T-08: package and release integration

Create a separate `friday-tui` distribution/import `friday_tui` and `friday-tui`
entry point in a later package directive. Base dependencies are Chat and Textual;
optional Chat integrations remain opt-in. Existing CLI entry points and package
dependencies must not acquire a reverse dependency on Textual/TUI.

The future package directive must explicitly enumerate root workspace/all-extra
registration, `scripts/check-package-metadata.py`, artifact-helper assumptions,
and `tests/integration/test_package_cohort_metadata.py` inventory/internal-name
patterns. Existing patterns recognize Chat/framework names and fixed cohort
members, so adding a directory alone is insufficient.

Use workspace source while developing. A published TUI that needs the new Chat
APIs must depend on a newly published Chat version containing them. It cannot
claim compatibility with immutable published Chat `0.1.0a4` merely because an
editable checkout has those APIs. Select the next coordinated version separately
at release preparation; no bump or PyPI upload occurs under this contract draft.

## 11. Construction and evidence order

The first directive is
[CD-TUI-001](directives/CD-TUI-001-shared-presentation-contracts.md), with two
separately built and independently validated units: TUI-00A pure display reader,
then TUI-00B shutdown observation API. Neither includes `friday-cli`, TUI widget,
dependency or package-metadata changes. Do not implement the second unit before
checking the first or start widgets before the shared contracts are verified.

The maintainer requires testing throughout construction and explicit UAT.
[The incremental test and UAT plan](test-and-uat-plan.md) defines 24 bounded
units, immediate positive/negative/regression checks and independent candidate
review, plus five real-user checkpoints with 14 scenario groups beginning with the first usable shell.
Required UAT gates need explicit user approval on both target terminals; they
cannot be satisfied by headless tests or deferred wholesale to closeout.

The current baseline profile passed 241 existing tests, including all six CLI
test modules and selected Chat command/config/display/lifecycle/identity/input
tests. This is limited current-code evidence, not full command parity or a
working TUI. No Textual package was installed; neither Linux UI compatibility
nor a full workspace dependency solve has been demonstrated.

Maintainer review must approve this contract and the exact first directive
before product authority is granted. The branch remains `design_only` meanwhile.
