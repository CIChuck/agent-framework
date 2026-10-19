# Product Requirements Document: Friday TUI

**Status:** Active; TUI-N01S and TUI-N01A independently VERIFIED. N01A is
closed under a maintainer-approved Linux-smoke deferral for that unit only.
TUI-CI01's latest authorized Ubuntu run passed focused tests, unchanged
`friday-cli` tests and installed-wheel checks, but failed one Runtime and five
Chat tests. Its full Linux verification gate remains open. Product/test
remediation requires a separately approved directive under the CI01 stop
condition.

**Lifecycle:** Started; board priority 14; current authority `granted` for
TUI-CI01 only

**Branch:** `feature/friday-tui`

execution_phase: planning; validation_state: changes_requested (TUI-CI01 Linux failures; CI02 approval pending)

**Reviewed:** 2026-10-16 against source revision `c3426986` (`0.1.0a4`)

**Parity target:** The maintained `friday-chat` application

**Package boundary:** `friday-tui` must be independently installable and must
not depend on or import `friday-chat`, `friday-cli` or their CLI code.

**Current design notice:** The [accepted decisions](decisions.md) and
[independent replacement plan](replacement-plan.md) are the current planning
path. The older [build plan](build-plan.md),
[integration contract](integration-contract.md),
[tactical plan](tactical-plan.md),
[test/UAT unit map](test-and-uat-plan.md) and
[CD-TUI-001](directives/CD-TUI-001-shared-presentation-contracts.md)
are withdrawn historical proposals, not construction instructions.

**Compatibility requirement:** Preserve the current feature set and behavior of
the `friday-cli` package and the existing `friday-chat` application.

**Evolution requirement:** Support additional `/` commands and richer command
capabilities over time without changing existing CLI behavior.

**Accepted UX configuration design:** Extend the existing CLI presentation file
with an optional versioned `tui` namespace, preserving current root fields,
defaults and CLI behavior. UX settings remain separate from runtime policy.

**Runtime/configuration requirement:** CLI and TUI are UX layers over Friday's
existing runtime infrastructure. The same runtime configuration files, schemas,
precedence and storage/service interpretation must work in both environments.

**Confirmed product choices:** Initial macOS/Linux support; a multiline editor
with an explicit submit shortcut; quit at a safe stopping point, completing
non-interruptible work and cleanup before exit (Q-01 through Q-03).

**Documentation requirement:** Completion includes a dedicated, user-facing
[TUI guide and configuration updates](user-guide-requirements.md), checked
against the installed candidate and user UAT.

Current planning artifacts:

- [Independent integration, construction and test/UAT plan](replacement-plan.md)
- [Architecture boundary and remaining technical work](architecture-reset.md)
- [Command/alias/usage coverage matrix](command-matrix.md)
- [Per-command neutral-capability and first-extraction map](neutral-capability-map.md)
- [TUI-N00 source and integration review](n00-integration-review.md)
- [Approved TUI-N01S session-identity directive](directives/CD-TUI-N01S-session-identity.md)
- [Independent TUI-N01S validation report](validation/VAL-N01S-session-identity.md)
- [Reviewed UI-neutral runtime configuration loader contract](neutral-config-loader-contract.md)
- [TUI-N01A before-code configuration characterization](validation/N01A-before-code-characterization.md)
- [Approved TUI-N01A neutral-loader construction directive](directives/CD-TUI-N01A-neutral-config-loader.md)
- [TUI-N01A local construction checks](validation/N01A-local-checks.md)
- [Independent TUI-N01A blocked validation report](validation/VAL-N01A-neutral-config-loader.md)
- [Independent TUI-N01A closeout review under Linux deferral](validation/VAL-N01A-waiver-closeout.md)
- [Approved Linux GitHub Actions verification directive](directives/CD-TUI-CI01-linux-actions.md)
- [TUI-CI01 local workflow checks](validation/TUI-CI01-local-checks.md)
- [TUI-CI01 first-candidate independent preflight findings](validation/VAL-TUI-CI01-preflight-7d97aacd.md)
- [First Ubuntu Actions run and failure diagnosis](validation/TUI-CI01-ubuntu-run-39172562601.md)
- [Second-candidate independent preflight finding](validation/VAL-TUI-CI01-preflight-3086f7d7.md)
- [Third-candidate independent preflight](validation/VAL-TUI-CI01-preflight-7a41004a.md)
- [Second Ubuntu Actions run and Runtime failures](validation/TUI-CI01-ubuntu-run-39173445329.md)
- [Finance-candidate independent preflight finding](validation/VAL-TUI-CI01-preflight-89a875ac.md)
- [Finance-rerun packet independent preflight](validation/VAL-TUI-CI01-preflight-505c4c1d.md)
- [Third Ubuntu Actions run and Runtime failures](validation/TUI-CI01-ubuntu-run-39174159031.md)
- [Moltbook-candidate independent preflight findings](validation/VAL-TUI-CI01-preflight-49acc931.md)
- [Fourth Ubuntu Actions run and complete failure evidence](validation/TUI-CI01-ubuntu-run-39175010441.md)
- [TUI-CI01 independent post-run review](validation/VAL-TUI-CI01-final-a7519db2.md)
- [Proposed CI02 Linux regression remediation directive](directives/CD-TUI-CI02-linux-regression-remediation.md)
- [CI02 before-code Linux failure diagnosis](validation/TUI-CI02-before-code-diagnosis.md)
- [Draft UI-neutral event and lifecycle contract](neutral-event-lifecycle-contract.md)
- [Draft startup bootstrap contract and test matrix](startup-bootstrap-contract.md)
- [Accepted CLI presentation-file extension and TUI UX options](ux-configuration.md)
- [Accepted product decisions](decisions.md)
- [TUI user guide and configuration documentation requirements](user-guide-requirements.md)
- [Screen layout and interaction proposal](screen-layout.md)
- [Optional reasoning display requirement](reasoning-display-requirement.md)
- [Agentic tool-activity requirement](tool-activity-requirement.md)
- [Planning authority](authority.json) and [source baseline](source-baseline.json)
- [Execution log](execution-log.md)

## 1. Product goal

Provide an installable, keyboard-accessible Textual terminal application that
supports every current Friday Chat command and workflow inside the TUI. Users
must be able to enter the same commands, arguments and aliases, see their
results, and continue the same session without opening a separate CLI.

The TUI must also support ongoing growth of its slash-command interface: new
commands, command groups, subcommands and additional capabilities. Here,
"command-line capability" means application commands entered with `/` in the
TUI. Launcher options and optional `!` shell execution are separate compatibility
surfaces, not the definition of this evolution goal.

Parity covers command behavior, state changes, progress, errors and shutdown.
Presentation may use panes, tables and Markdown, but must preserve the meaning
of the underlying operation. Optional services must report the same actual
availability as Chat; displaying a command does not make its backend available.

The first release requires complete parity with the agreed current application
baseline. An initial shell or a subset of commands is an implementation
milestone, not a completed TUI.

The current command inventory is the initial compatibility baseline, not a
permanent limit. Preserving existing CLI behavior and extending the TUI's command
surface are simultaneous requirements.

### 1.1. Mandatory CLI preservation requirement

The TUI is an additive frontend. Designing or implementing it must not change
the current feature set or behavior of
[`packages/friday-cli`](../../../../packages/friday-cli/README.md)
(`friday-framework-cli`, import `friday_cli`). The current `friday-chat`
application remains the command-parity target and must also continue operating
as it does now.

This requirement applies to both direct package edits and indirect effects of
shared-code changes, dependency changes, imports or process-wide configuration:

- Keep the existing `friday-cli` implementation outside the TUI refactoring
  scope. Do not move, replace or rewrite its components to accommodate Textual.
- Preserve its public APIs, command handling, input/key behavior, rendering,
  configuration/defaults, progress, session and cancellation behavior, and
  existing entry-point behavior. Existing limitations are part of the baseline;
  TUI work is not permission to fix or redefine them.
- Give the TUI its own presentation adapters, widgets and executable. Existing
  CLI paths must work without installing the TUI and continue working when it
  is installed alongside them. They must not import Textual or TUI modules.
- Do not monkey-patch CLI functions, replace shared console globals or mutate
  CLI configuration/defaults as the mechanism for connecting the TUI. Use
  UI-neutral service contracts from the independently installed TUI package.
- A needed neutral-service extraction must be additive, explicitly scoped
  and behavior-preserving for existing Chat and `friday-cli` callers. Keep CLI
  adapters/defaults intact. If no neutral contract can meet a requirement,
  record the design gap rather than relaxing this preservation requirement.

CLI preservation is a release acceptance requirement, not an optional
improvement or a check deferred until after TUI delivery. Establish the current
behavior before implementation and require no new regressions against it.

New TUI commands may add capabilities while existing CLI invocations retain
their current meaning and effects. TUI-specific additions must not be installed
into the existing CLI's default command set implicitly. Reusing an extension in
another frontend is an explicit, separately scoped integration decision.

## 2. Compatibility baseline

The maintained [`friday-chat` application](../../../../packages/friday-chat/README.md)
is the behavior reference. The source-derived
[command matrix](command-matrix.md) records 50 canonical slash commands and
three aliases at the reviewed `c3426986` revision. That count is a snapshot,
not a ceiling or a parity test. `friday-chat` is not a backend or dependency
for `friday-tui`. The historical `tests/integration/memory/friday.py`
application is reference material, not command authority.

The compatibility surface includes command names, aliases, arguments,
subcommands, preconditions, state and file effects, progress, errors,
optional-service availability, and shutdown. It also includes
`@agent_name <message>` routing and the disabled-by-default `!<command>`
shell request path. Existing `friday-cli` and Chat operation must remain
unchanged. The first release requires every command in the matrix, including
high-impact maintenance, reset, export and workflow paths; an initial shell
or subset is only a construction milestone.

## 3. Command parity and growth

The TUI independently owns its command registry, handlers and UI effects.
Its registry drives dispatch, `/help`, completion and any palette. Typing a
leading `/` automatically shows matching command-name and alias suggestions
from that active registry without changing the draft or executing a command
(D-66). Registered subcommands are suggested after a recognized command name,
using the same fill-only selection controls; free-form argument values are not
suggested (D-69). A new command should be added as a module with metadata,
typed handler, tests and user documentation, without a central widget switch
or a change to existing
CLI defaults. Reject duplicate canonical names or aliases. TUI-only commands
may grow over time; changes to the Chat registry require a parity-drift
assessment and corresponding TUI cases.

For each [PAR case](command-matrix.md), compare the TUI and current Chat
command against equivalent disposable fixtures: accepted inputs, aliases,
invalid inputs, output meaning, stored state, errors and optional-service
limits. Compare effects as well as displayed wording. Do not use Chat source
as a TUI runtime import. If the needed operation lives only in Chat, a
bounded extraction into a UI-neutral Friday service is allowed; Chat and
TUI keep their own command handlers, and before/after CLI regressions must
prove unchanged behavior. The
[replacement plan](replacement-plan.md#1-invariants-and-package-direction)
defines this boundary.

Command input remains available for every operation even if a menu or
button is added. Preserve these distinctions:

- `/cls` and `/clearscreen` clear the displayed conversation, pinned latest
  prompt and Activity view without changing session history, memory or
  persisted transcripts. They emit no replacement result. The pin stays empty
  until the next accepted conversational prompt. `/clear` changes
  conversation/session history; `/reset` retains its selected-store or
  full-store effect.
- `/exit`, `/quit` and `/q` use the normal idle slash-command shutdown path.
  Busy submissions retain the editor draft; the Quit action requests graceful
  exit separately.
- The first release shows the current transcript session. `/sessions` lists
  persisted sessions and `/transcript` inspects a current or selected
  transcript or exports sessions as its existing arguments allow. There is no
  control for changing the active transcript session; `/switch [agent]`
  changes the active agent.
- Export, ingest, replay, tool and maintenance commands retain their
  existing validation, paths, execution-intent flags and failure semantics.
  A TUI control must not silently add or remove an effect.

## 4. Startup and configuration

Provide an installed `friday-tui` executable. Existing Chat runtime YAML and
model-library files must work without translation or rewriting, with the
same effective model/service bindings, storage paths, environment and
startup precedence under the same launch context. The TUI reads them
through UI-neutral contracts, never a Chat/CLI import. With no `--config`,
offer a chooser for an existing runtime file. Its initial list uses the
captured launch working directory, without automatic home-directory or
recursive search; users can browse to another path (D-48). An explicit
`--config` path bypasses the list. Show likely Friday Chat runtime YAML files,
including custom names, while excluding recognized model-library and CLI
presentation files (D-49). Use a shallow, read-only top-level YAML content
check to find runtime-shaped files regardless of basename (D-55). The exact
key signature belongs in the bootstrap contract; unrecognized files remain
reachable through Browse. Show recognizable but incomplete runtime files and
validate them only when selected (D-57). If no candidates appear in the launch
folder, keep the chooser open with a clear empty-list message, Refresh, Browse
and Quit (D-52, D-59). Browse supports folder navigation and typed or pasted
absolute, relative and `~` home paths to existing files, including outside the launch
folder; relative entry starts from the folder Browse displays (D-58).
Direct-child `.yaml`/`.yml` links to readable runtime files can also appear,
including when the target is elsewhere. Broken or non-runtime links are left
out of the automatic list but can be tried through Browse (D-60).
The chooser has a visible Refresh action to rescan the launch-folder candidate
list after files are added, removed or edited. It does not watch for changes
automatically; Refresh does not validate a selected file or start the runtime
(D-59).
If a chooser-selected file fails runtime-configuration validation, keep the
chooser open with an actionable error and Retry, Browse and Quit actions (D-50).
Retry rereads the selected path after an external correction. Explicit
`--config` files that fail validation instead report the error and exit
nonzero, without opening the chooser or starting the runtime (D-51).
If real runtime startup fails after a chooser selection, clean up partially
started services, show the error and return to that chooser with Retry,
Browse and Quit when cleanup succeeds (D-53). If cleanup also fails, report
both failures, restore the terminal as far as possible and exit nonzero;
do not offer in-process retry (D-56). With an explicit `--config` path, a
failed real startup cleans up partial services, reports the error and exits nonzero
without opening the chooser; cleanup failure is also reported (D-54).
For interactive startup with an explicit or chosen config, use the real
provider-backed runtime by default when `--runtime` is omitted (D-47).
`--runtime fake` remains an explicit deterministic test mode; a failed real
startup never silently falls back to fake. This is a TUI-only startup default:
the existing `friday-chat` fake default and `friday-cli` behavior are unchanged.
`FRIDAY_CHAT_RUNTIME` controls only the existing Chat launcher and is ignored
for TUI mode selection (D-61); it does not change the TUI's real default or
an explicit TUI `--runtime` choice. Runtime YAML environment interpolation and
credential lookup still work normally.
Real mode must use configured services and cannot be inferred from a fake pass.

Keep the existing `cli-config.yaml` as the common presentation file,
including a custom `--cli-config` target. Its current root fields and
CLI meanings remain intact; the optional versioned `tui:` namespace controls
appearance, layout, editor, keys, output, discovery, accessibility and
TUI-selected-file OCR languages (D-87) and configurable per-file/combined
attachment limits with defaults (D-94), measured in estimated tokens of
complete model-input attachment text (D-95). Omitted attachment-limit
settings use fixed defaults across models (D-96): 4,000 estimated tokens
per file and 8,000 combined when omitted (D-97).
The TUI reads that file independently or through a neutral typed reader,
without activating CLI globals. `tui.output.reasoning_visibility` defaults
to `hidden`. An in-app toggle changes subsequent reasoning display without
rewriting the file or retaining earlier hidden text. The
[UX configuration design](ux-configuration.md) and
[replacement plan](replacement-plan.md#configuration-and-startup) specify
the current direction; field bounds and parsing tests belong to a scoped
directive.

The launcher design must assess `--help`, `--version`, `--runtime fake|real`,
`--replay` and `--replay-delay` in addition to `--config` and
`--cli-config`. Startup replay is distinct from interactive `/replay`.
Version inspection and replay precedence must match the maintained Chat
behavior where equivalent launcher options are exposed. After a successful
startup replay, keep a read-only result view showing only the replay file and
processed-turn count until the user chooses Quit (D-62, D-63). Do not add a
turn-by-turn record, admit prompts or commands, or enter a configured
interactive session. If startup replay fails, show the file and actionable
error in a read-only screen until Quit, then exit nonzero without entering
the chooser or interactive session. There is no in-process Retry; the user
corrects the cause and relaunches (D-64, D-65). Shell completion is
separate from in-TUI slash-command completion.

## 5. Independent architecture

`friday-tui` uses UI-neutral Friday runtime and service packages. A reusable
operation may be extracted from Chat into a neutral owner only when a
command-family contract and parity tests justify it. Neither frontend
imports the other's code. The TUI owns its presentation, command registration,
session/worker bridge, resources and terminal restoration. Its UI remains
responsive while accepted backend work proceeds. It uses typed progress,
error and lifecycle outcomes, not text scraped from Chat output or telemetry
enabled for display.

Normal Quit reaches an owner-defined safe stopping point, finishes admitted
non-interruptible work and performs cleanup. A separately confirmed emergency
Force quit is available if work stalls, with an explicit warning that an
operation and cleanup may be incomplete. A force path is never reported as
successful graceful Quit. The exact worker/process mechanism, failure report
and recovery instructions require the lifecycle directive.

The first release also has a typed UI-neutral event path for each provider
step, provider-exposed reasoning, rejected tool request, actual tool execution
and final answer. An executed call shows the tool, actor, order, status and
argument values passed to it without TUI masking. An oversized value gets a
bounded preview and visible truncation notice; the tool's input is unchanged.
Only actual model or user tool requests rejected before invocation show
`Not run` with a reason; pre-request selection or budget exclusions do not
create Activity entries. Activity includes automatic, manual `/run-tool`,
delegated-agent and workflow calls tied to the operation. Automatic tool
result payloads remain out of Activity and scrolling chat; `/run-tool`
retains its inline command result. Activity is bounded, in-process view
state and is not persisted or exported. Reasoning is hidden by default;
a forward-only in-app toggle shows subsequent provider-supplied text
separately from the final answer. See the
[replacement plan](replacement-plan.md#provider-and-tool-events),
[Activity requirement](tool-activity-requirement.md) and
[reasoning requirement](reasoning-display-requirement.md).

Activity appears inline within the conversation exchange or user-entered
tool-command entry that produced it, before that entry's final response or
command result. Its collapsible, internally scrollable section keeps
multi-step work inspectable without a persistent side pane (D-45).
The Activity view opens automatically when its first entry arrives. Users can
collapse and reopen it; later entries accumulate without overriding a manual
collapse. A new prompt leaves older exchanges' expanded/collapsed Activity
states as the user left them, while the new exchange's Activity opens
independently on its first entry (D-46). Opening it does not steal editor
focus or pull a user away from older conversation they are reading
(D-36/D-42).
While collapsed, its header shows how many entries arrived since collapse;
reopening or clearing Activity resets that count. If bounded retention discards
entries while collapsed, the header also indicates that loss (D-43).
When expanded, Activity follows new entries only while its own view is at the
bottom. Scrolling up pauses that following; a separate, clickable and
keyboard-focusable `Jump to latest Activity` control or scrolling back down
resumes it without moving the conversation (D-44).

## 6. TUI interaction and rendering

Keep the proposed layout, with a collapsible Context sidebar, main scrollable
conversation/command output, prompt editor and status area. In the first
release, the sidebar shows directory context and lets users browse folders
and select files (D-76). File editing and other management can follow later.
Deliberate file selection immediately attaches content for the next eligible
model turn without a separate Add action (D-77). Moving focus or scrolling the
list does not select or attach. Attachment does not submit a prompt, and its
status or failure is visible. Once attached, the file remains in the active
context across later turns until the user chooses its visible Remove action
(D-78). Removal affects future turns without deleting the file or changing a
turn already admitted. Attachments are discarded on exit, so every launch
starts with none, even when an earlier transcript is available (D-79).
Selecting another distinct file adds it alongside the existing attachments;
each has its own Remove action (D-80). Friday uses a snapshot captured at
selection time for later turns. Selecting the same file again refreshes that
snapshot in place; changes to the source file do not appear automatically,
and a failed refresh leaves the last good snapshot attached with an error
(D-81). First-release attachment accepts readable text, code and text-based
data files plus actual extracted PDF, DOCX and XLSX content (D-82), including
Tesseract OCR text from scanned PDFs (D-83). In mixed PDFs, use embedded
text where usable and OCR only the pages that lack it, keeping page order and
avoiding duplicate page text (D-84). Users install Tesseract separately;
missing Tesseract fails OCR attachment with a setup hint while ordinary text
and embedded-text attachments remain usable (D-85). If one page that requires
OCR fails, reject the entire new PDF attachment with a page-specific error;
a failed refresh retains the previous complete snapshot (D-86). OCR
defaults to English and can use installed language packs selected in the
TUI-only presentation setting (D-87). The TUI package supplies its PDF page
renderer as a dependency; users do not separately install a renderer (D-88).
Excel `.xlsx` attachment includes every worksheet, labeled by sheet name
in workbook order, including hidden sheets (D-89). If one worksheet
cannot be read, the whole new workbook attachment fails with that sheet
named; a failed refresh retains the last complete snapshot (D-90). For
formula cells, include both the formula and any saved workbook result with
clear labels; if no saved result exists, say so without calculating one
(D-91). A file whose extracted content exceeds the per-file limit fails
as a whole with a clear size message; no partial excerpt is attached, and a
failed refresh keeps the last complete snapshot (D-92). If adding a file
would exceed the combined attachment budget, it fails without changing
existing attachments; users can remove files and retry. An over-budget refresh
also keeps the last complete snapshot (D-93). Both limits have TUI-only
settings with defaults in the shared presentation file (D-94). Both count
estimated tokens of the formatted content Friday would add to model input,
including labels and OCR/formula text (D-95). Omitted limits use the same
fixed defaults across models, without context-window scaling (D-96):
4,000 estimated tokens per file and 8,000 combined (D-97). The combined
default can nearly fill an 8,192-token model window. D-98/D-99 check every
assembled conversational model request before it is sent. When a request is
over budget, the TUI attempts configured, eligible older-turn compaction once,
reassembles and rechecks the request, then continues if it fits or stops that
model step safely. An initial failed submission retains the draft and attached
snapshots; a later failed step leaves the turn incomplete with earlier tool
activity and effects intact. Compaction itself can call a separate model service
and change stored memory. If a provider instead rejects a request that passed
Friday's estimate for context length, the TUI shows the provider error and
leaves correction and retry to the user (D-100). It restores the failed prompt
automatically into an empty editor or offers a Restore action if a newer draft
is present (D-101). If its error notice leaves the bounded conversation, the
Restore action remains beside the editor during this run (D-104). That failed
prompt also remains recoverable after `/cls` clears the view (D-105). The failed
attempt stays recoverable only during the current TUI run and does not create
a transcript entry (D-102). A later incomplete turn after tools remains
visible in this run but likewise creates no transcript entry (D-103). A
different conversational turn that completes successfully clears the earlier
failed-prompt recovery action (D-106). If multiple failed prompts remain
recoverable, one editor-adjacent control opens a newest-first chooser (D-107).
Confirming Restore keeps that original recoverable until a conversational turn
completes successfully (D-108), unless the user explicitly confirms `Dismiss`
for that prompt (D-109). Dismiss removes only its in-process recovery entry;
the editor draft and attachments stay intact.
No file attachment may use a placeholder or report empty extraction as success.
A UI-neutral runtime contract is needed:
Chat `/read` displays content and `/ingest` stores vector memory; neither is
a selected-file attachment for the next prompt.

Required behavior:

- All commands, arguments and results are usable through the TUI prompt.
  Support editable history, command discovery and paste without accidental
  partial submission. Use a multiline editor (accepted Q-02): `Enter` submits
  the complete draft, and `Ctrl+Enter` inserts a newline without submitting
  (D-38). Keep visible, keyboard-focusable Submit and Insert newline controls
  as accessible fallbacks. Verify that real macOS and Linux terminals deliver
  distinguishable keys before advertising `Ctrl+Enter` for each terminal;
  document the Insert newline control where they do not. No second default
  newline shortcut is planned for the first release (D-39).
- Choosing a `/` command from the command palette puts its command text in
  the editor and focuses it for review or argument entry. Selection does not
  execute the command; normal `Enter` or Submit is required (D-40). If an
  unsent draft is already present, ask before replacing it. Cancel preserves
  the draft exactly; confirm replaces it without submitting (D-41).
- As a user types a leading `/` command name, show matching names and aliases
  automatically from the active TUI registry. Merely displaying suggestions
  leaves the draft and `Enter` submission behavior unchanged (D-66). Selecting
  one completes the chosen name or alias token in the current draft, preserves
  any following arguments and focuses the editor; it never executes the
  command. `Up`/`Down` highlight matches and `Tab` inserts the highlighted
  one while the list is open; otherwise `Tab` moves focus. `Enter` or Submit
  runs the editor draft separately (D-67, D-68). After a recognized command
  followed by a space, suggest declared subcommands as their token is typed,
  using the same controls without suggesting free-form values (D-69). Once a
  command or subcommand is recognized, show its expected argument shape as a
  short usage hint without inserting values or running anything (D-70).
- Editor history includes accepted conversational prompts and submitted `/`
  commands, plus accepted `@agent` messages and enabled, admitted `!`
  commands in the running TUI. Recalling any fills the editor without
  executing; `Enter` or Submit remains necessary. This is separate from the
  `/history` command and does not change runtime/session history (D-71, D-75).
  The recall list is discarded when the TUI exits and starts empty on the
  next launch; it is not saved as a separate history file (D-72). Browsing
  saves any unsent draft and editing position, then restores them exactly if
  the user leaves history without submitting a recalled entry (D-73). With no
  slash suggestion list open, `Up` at the editor's upper caret boundary
  browses older entries; `Down` at its lower boundary moves newer while
  browsing, eventually restoring the draft. Otherwise these keys move the
  caret; suggestion navigation takes priority when its list is open (D-74).
- Distinguish user messages, assistant responses, command output and errors.
  Preserve Markdown/code readability and selectable output. Users can copy
  selected visible Activity and shown reasoning; a truncated tool parameter
  copies only its preview and notice, never discarded overflow. Hidden
  reasoning is unavailable to copy. Treat literal tool output, filenames and
  diagnostic text as data rather than executable markup.
- Update a streamed response in place, preserving chunk order and final content;
  do not render every chunk as a separate completed message or duplicate it at
  completion. Retain the backend's streaming/final-output behavior when tools or
  providers do not support the same streaming path.
- Show command progress and busy/maintenance state while keeping navigation
  responsive. Preserve serialized input processing and existing maintenance
  admission; one accepted submission must enqueue at most one operation.
- Pause automatic scrolling when the user reads earlier output and provide a
  visible, clickable and keyboard-focusable `Jump to latest` control when away
  from the bottom. Hide the latest-prompt pin while browsing older exchanges.
  Clicking or activating the control scrolls to the bottom, restores the pin
  when one exists and resumes following new output. Scrolling back to the
  bottom has the same effect. Bound rendered history/log buffers. If older
  conversation messages leave the on-screen buffer, show a notice and point
  to `/transcript` when saved messages are available; say when they are not.
  Do not add `Load older` in the first release or imply that transient
  Activity or reasoning can be recovered from transcripts. Rendering limits
  must not delete persisted transcripts.
- Support keyboard focus navigation across prompt, output, workspace and status.
  Specify history keys, scroll keys, clear-view and quit bindings, including
  collisions with Textual defaults. Do not communicate status by color alone.
- Support macOS and Linux initially (accepted Q-01). Define the actual terminal
  matrix and test minimum size, resizing, narrow-layout fallback, Unicode and
  configured user/assistant names. A fixed diagram is not a resize or
  accessibility specification.

Mouse interaction, richer workspace management and additional dashboard panels
may follow later. Essential command parity must be available by keyboard.

## 7. Long operations, interruption and shutdown

Define an operation-by-operation policy for input admission, cancellation and
quit during generation, tools, replay, ingest and memory maintenance. Editing
the next prompt is separate from executing it concurrently.

Accepted Q-03 requires quitting at a safe stopping point, finishing any
non-interruptible operation and completing cleanup before exit. On an active
operation, show that quit is pending while the owner reaches that point; do not
force-cancel a persistent mutation. Idle quit still follows normal cleanup.

`Ctrl+C`, the TUI's Quit binding and slash-command exit need documented idle
and busy behavior. Route normal graceful exit through the TUI-owned neutral
runtime lifecycle before releasing the terminal. Preserve extraction
drain/cancellation rules, configured exit maintenance, transcript finalization
and closure of asynchronous clients and MCP connections where applicable.

Operation completion is the initial normal safe boundary. Do not call private
methods, cancel a worker blindly, or promise rollback merely because Quit was
pressed. Show pending, completed or failed cleanup and preserve recovery
information. A separately confirmed emergency Force quit is available when
normal Quit is pending and work stalls. It must warn that an operation,
persistence or cleanup can remain incomplete, and never report this path as
successful graceful shutdown. The exact mechanism and terminal recovery
belong in the lifecycle directive. Ctrl+Q is the proposed normal Quit key;
Ctrl+C retains editor/output copy behavior without changing CLI keys.

## 8. Acceptance and verification

| ID | Required evidence |
| --- | --- |
| AC-01 | A registry-derived inventory covers every current command, alias, argument family and additional input route. Every parity case has expected output/state/effects and a TUI interaction test; name-only registration checks are insufficient. |
| AC-02 | Equivalent disposable fixtures produce matching Chat/TUI command outcomes for session, memory, transcript/export, tools, security, speech, agent and workflow commands, including unavailable integrations and invalid input, without a TUI dependency on Chat code. |
| AC-03 | Tests distinguish `/cls` and `/clearscreen` from `/clear` and `/reset`: the display-clearing aliases remove the current conversation, pin and Activity view without a replacement result or changes to session history, memory and persisted transcripts; the pin resumes on the next accepted conversational prompt. AC-30 separately keeps failed-prompt editor recovery through that display clear. Verify `/sessions` and `/transcript` list, inspect and export without switching the active transcript session, while `/switch [agent]` changes the active agent. Typing a leading `/` shows matching registered names and aliases as the command name changes, without altering the draft, dispatching or changing `Enter` submission. After a recognized command and space, registered subcommand matches appear as their token is typed, including `/workflow r` → `run`; commands without declared subcommands do not offer invented matches or free-form value suggestions. Once a command/subcommand is recognized, a metadata-derived usage hint shows required/optional argument shapes, updates with the syntax and disappears when no registered syntax applies; it does not fill values or dispatch. With suggestions open, `Up`/`Down` highlight and `Tab` completes only the highlighted name, alias or subcommand token, preserving other draft text and editor focus without execution; with no highlighted match, `Tab` does not insert. With the list closed, `Tab` moves focus; `Enter` always submits the editor draft. A `/` command chosen from the palette fills and focuses an empty editor without dispatch; with an unsent draft, canceling replacement preserves it exactly, while confirming replaces it without submission. Verify other aliases, help/discovery, workflow approvals, export contents and maintenance dry-run/execute behavior without duplicate side effects. |
| AC-04 | Streaming, slow commands and progress remain visible while the UI accepts navigation/editing. Tests verify output ordering, completion, exceptions and admission of additional submissions. |
| AC-05 | Normal Quit reaches an owner-defined safe stopping point, finishes non-interruptible work and completes cleanup before exit (Q-03), or reports explicit failure. A separate confirmed Force quit warns that work/cleanup may remain incomplete and never claims graceful success; its termination and terminal recovery paths are tested. |
| AC-06 | Installed `friday-tui` help/version/startup, configuration diagnostics and fake/real selection behave as specified. Without `--config`, the chooser starts with likely Friday Chat runtime configs, including custom names, incomplete but recognizable files, and valid direct-child YAML links to readable runtime files, in the captured launch directory; shallow top-level YAML inspection excludes recognized model-library/display YAML. Broken, cyclic, unreadable, directory-target and non-runtime links stay off the automatic list but remain Browse-selectable. Browse supports folder navigation and typed/pasted absolute, relative and `~` paths to existing files, including other folders and unrecognized files; relative paths resolve from the displayed Browse folder. Explicit paths bypass the list. An empty initial list keeps the chooser open with a clear message, Refresh, Browse and Quit. Visible keyboard-focusable Refresh rescans only the launch folder on demand: added, removed and changed files update the candidates, but no watcher updates them automatically; listing and refreshing do not start the runtime or resolve credentials. If a chooser-selected file is invalid or missing, the chooser remains open with an actionable error, Retry of the selected path, Browse and Quit; no runtime starts from that file. An invalid explicit `--config` file instead reports the error and exits nonzero without opening the chooser or starting the runtime. Omitted `--runtime` starts real with either selection route; explicit fake remains available, and a failed real startup never silently falls back. If real startup fails after chooser selection and cleanup succeeds, the chooser returns with the error, Retry, Browse and Quit. If startup and cleanup both fail, report both failures, restore the terminal as far as possible and exit nonzero without in-process retry. With explicit `--config`, failed real startup cleans up, reports the error and exits nonzero without a chooser; cleanup failure is also reported. Version/startup-replay precedence is unaffected. Wheel/sdist include required UI resources, and installation works outside the source checkout. |
| AC-07 | On the initial macOS/Linux terminal matrix (Q-01), verify that `Enter` submits once and `Ctrl+Enter` inserts one newline without submitting when the terminal distinguishes them (D-38). Check the actual key events and the visible keyboard-focusable Submit and Insert newline controls; document and exercise the fallback where `Ctrl+Enter` is indistinguishable. Pasting multiline text never submits it; busy rejection retains the full draft. Editor history recalls accepted prompts, `/` commands, `@agent` messages and enabled/admitted `!` commands into the editor without running them; disabled/rejected routes, unsent/busy-rejected drafts, command results and assistant responses are not submitted entries. The recall list starts empty on a fresh launch and is not rebuilt from transcripts or a new persistent history file. Browsing with an unsent draft preserves its text and editing position; leaving without submitting a recalled entry restores both exactly. Browsed entries are editable copies and do not mutate stored submissions. With no suggestions open, `Up` at the editor's upper caret boundary browses older entries and `Down` at the lower boundary browses newer only while already browsing; interior arrows move the caret. Open slash suggestions consume `Up`/`Down` for match highlighting. No first-release F3/F4 history binding; test wrapped multiline input and physical terminal focus. Verify keyboard/focus, inline command results, distinct prompt/response role colors plus labels, a pinned latest accepted prompt over its scrolling response without duplicate history/model input/export, dark/light/high-contrast readability, scrolling, literal output, resizing, narrow terminals and terminal restoration. Away from the bottom, new output does not pull the view; the pin remains while reading its own response but hides when browsing earlier exchanges. A visible clickable and keyboard-focusable `Jump to latest` control returns to the bottom, restores the pin when available and resumes following. Scrolling to the bottom has the same restoration; after `/cls` the pin stays empty until a new conversational prompt. When bounded rendering evicts older conversation messages, verify a notice, `/transcript` access to saved entries when available, honest unavailable behavior and no `Load older` control or false Activity/reasoning recovery claim. |
| AC-08 | Maintained Chat command/lifecycle regressions still pass; focused TUI pytest, Ruff, Mypy, package metadata, board/dashboard and changed-document links pass. Report unrelated repository debt separately. |
| AC-09 | Establish a pre-implementation `friday-cli` and Chat CLI behavior baseline. Existing tests remain intact; before/after comparisons cover public APIs, commands, input, rendering, configuration/defaults, progress, session/cancellation and entry points. No new regression or TUI-driven edit to the existing `friday-cli` implementation is accepted. Record pre-existing failures separately rather than weakening expectations. |
| AC-10 | Verify existing CLI use both without TUI installed and with it installed alongside. TUI installation/import/startup must not introduce a Textual dependency into CLI paths, replace their entry points, or mutate their shared console/configuration state. Dependency-resolution changes must not alter existing CLI behavior. |
| AC-11 | Demonstrate a representative additional `/` command through a new typed command module and registration, without changes to existing CLI implementation, baseline handlers or generic UI dispatch/layout. Verify execution, help, discovery/completion, errors and relevant runtime effects through the TUI. |
| AC-12 | Extension tests reject canonical-name/alias collisions, preserve existing-command behavior, and verify command-set isolation between the TUI and existing CLI. The coverage inventory tracks baseline and added commands without treating the initial command count as a ceiling. |
| AC-13 | Each bounded construction unit includes immediate positive/negative/regression checks and independent candidate review before dependent work. macOS user UAT begins with the first shell; Linux automation runs during construction; hands-on Linux terminal UAT occurs on the final installed candidate. Record actual user results, defects and approval. Automation is not UAT signoff. |
| AC-14 | With the same explicit runtime mode, identical runtime configuration files, environment and launch/workspace context resolve equivalent model/service bindings, memory/storage paths and validation results in Chat and TUI. Startup option precedence stays compatible where equivalent options are exposed; D-47 intentionally sets a different TUI default mode. D-61 keeps `FRIDAY_CHAT_RUNTIME` specific to Chat: TUI mode stays real by default or follows its own explicit `--runtime` even when that variable is set to `real`, `fake` or invalid; Chat retains its existing override. D-62 and D-63 keep a successful startup replay's read-only file/count result visible until Quit without a per-turn list, config startup or command admission. D-64 and D-65 keep a failed startup replay's read-only file/error view until Quit, then exit nonzero without Retry, chooser or interactive session; correction requires relaunch. Runtime files need no translation or rewriting; optional TUI presentation settings cannot override runtime configuration. |
| AC-15 | Existing CLI presentation files work unchanged; adding a supported `tui` namespace preserves CLI values/rendering, selection precedence and defaults without CLI source edits. TUI-only settings, including selected-file OCR languages and estimated-token per-file/combined attachment limits, have typed defaults/validation and tested effects; omitted attachment limits stay fixed at 4,000 per file and 8,000 combined estimated tokens across differing model context metadata (D-96/D-97). No runtime overrides, implicit file writes or separate preference source is introduced. |
| AC-16 | A dedicated TUI user guide and updated configuration guidance explain installed startup, file choice, screens, keyboard use, every shipped command/alias, common tasks, settings, accessibility and recovery in plain language. Index/navigation links work; examples and keys match the final installed macOS/Linux candidate; user UAT follows the guide and defects are corrected before release acceptance. |
| AC-17 | The installed TUI defaults to final-answer-only display and accepts a TUI-only hidden/shown reasoning setting plus an in-app toggle. The toggle affects subsequent events without rewriting config or retaining earlier hidden text. Shown provider-exposed text is separately labeled/collapsible and selectable for copying; hidden reasoning cannot be copied. Test streaming and tool follow-ups, text/count/neither cases, bounds, no TUI-added raw-reasoning persistence/export, unchanged CLI output and macOS/Linux user UAT. |
| AC-18 | The installed TUI has a live, bounded, in-process Activity view inline within the conversation exchange or user-entered tool-command entry that produced it, before the final answer or command result. Its collapsible, internally scrollable section remains usable on narrow terminals without a persistent side pane. Its first entry opens the view automatically without stealing editor focus or overriding paused conversation following; users can collapse and reopen it, and later entries accumulate without overriding a manual collapse. Accepting a new prompt preserves each older exchange's chosen expanded/collapsed Activity state while the new exchange's Activity opens independently. The collapsed header counts newly appended entries once, not status updates; reopening or `/cls` resets the count, and eviction while collapsed is indicated in the header with detail on reopen. Expanded Activity follows only while its own viewport is at the bottom; scrolling up pauses following, and a clickable keyboard-focusable `Jump to latest Activity` control or scrolling to its bottom resumes it without moving the conversation viewport. Executed calls show actor, identity, actual parameter values without TUI masking and status; oversized values get a bounded preview and explicit truncation notice, with overflow discarded from TUI memory and the tool's input unchanged. Selected visible Activity text can be copied; a truncated value copies only the preview and notice. Actual tool requests rejected before invocation show a distinct `Not run` reason, never an executed call; pre-request selection or budget exclusions create no Activity entry. Automatic tool-result payloads stay out of Activity/chat; `/run-tool` retains its inline result. `/cls` clears visible Activity while later operations can add new entries. Provider reasoning appears in sequence only when enabled. Deterministic and real-provider/tool tests plus installed macOS/Linux UAT verify correlation, ordering, argument fidelity, truncation, copy, non-persistence/export, scrolling and unchanged CLI behavior. |
| AC-19 | The first-release Context sidebar supports keyboard and pointer folder navigation and file selection, remains collapsible and usable on narrow macOS/Linux terminals, and preserves conversation/editor state while browsing. Browsing does not ingest memory, edit files or change the active transcript session. Test inaccessible/missing folders and files, focus and scroll behavior, and installed-terminal UAT. AC-20 covers the selected-file context effect. |
| AC-20 | In the installed TUI, deliberately selecting a readable file by pointer or keyboard activation immediately initiates attachment for the next eligible model turn, without a separate Add action or automatic prompt submission. Merely moving focus or scrolling never attaches. A visible status distinguishes attached, loading and failed files; a failed initial read is not reported as attached. With disposable files and a fake provider, verify the next and later accepted conversational turns receive the selected snapshot through a UI-neutral contract until the user activates a visible keyboard-focusable Remove action. Selecting a second distinct file keeps the first attached and adds the second; both reach later accepted turns. Editing or deleting a source after selection does not change its attached snapshot; reselecting the same file refreshes in place without a duplicate, while a failed refresh preserves the last good snapshot and reports the error. Removing one file omits only that file from future turns, while an already admitted turn is unchanged. A new TUI run starts with no attachments, including when an earlier transcript is available; no attachment list or content is persisted merely for restoration. Attachment and removal do not edit the file, write `/ingest` memory or depend on `friday-chat` or `friday-cli`. Check installed macOS/Linux terminal behavior and unchanged Chat/CLI regressions. D-92 rejects over-limit individual files. D-93 rejects a new file or refresh that would exceed the combined attachment budget without evicting current files; test manual removal and retry plus unchanged model input after rejection. D-94 adds optional TUI-only settings with defaults for both limits; test omitted/default, valid custom and invalid values without changing CLI behavior. D-95 measures the complete formatted attachment text in estimated tokens, including labels, OCR and formula content. Deterministic estimator tests cover per-file and proposed-combined boundaries, refresh replacement and visible estimated-token errors. D-96/D-97 set fixed omitted defaults at 4,000 per file and 8,000 combined estimated tokens; test below/at/above each boundary, the same defaults and admission outcomes with different and unknown model context metadata, plus explicit override. An attachment that passes these limits can still exceed a model turn's remaining context, including an 8,192-token model; D-98/D-99 check the first conversational request, attempt eligible older-turn compaction once, and reject it if a fresh full estimate remains over budget while retaining the draft and attachments. Exact field names, estimator/headroom, override validation ranges and format safeguards remain open. |
| AC-21 | On a fresh installed TUI, first-release file attachment extracts actual content from supported text/code/text-data files and representative PDF, DOCX and XLSX fixtures. The model-turn input contains the extracted content, not a file label, placeholder or empty success. Verify genuine positive fixtures for each format, corrupted/unreadable files, missing reader dependencies, empty extraction and explicit user-visible failure; do not count a malformed-file test as proof of positive extraction. Package the required readers with the installed TUI and preserve Chat `/read` placeholders and existing CLI behavior. Scanned-PDF OCR has separate AC-22 evidence. XLSX attachment includes every worksheet, including hidden sheets, labeled by sheet name in workbook order. A multi-sheet fixture with a non-first active sheet and distinct content on a hidden sheet must prove all sheets reach the actual model input through one attachment, with no silent active-sheet-only result. A multi-sheet failure fixture with readable sheets on either side of an unreadable sheet must produce a sheet-specific error, no partial new model input and a retained last complete snapshot after failed refresh; other attachments remain active. A readable empty sheet is not a failure, but an entirely empty workbook cannot attach successfully. Formula cells must carry both the expression and the workbook-saved result when present, with sheet/cell identity and distinct labels; an absent saved result is identified as unavailable, never fabricated or freshly calculated. Prove numeric/text saved results and missing saved results in actual model input while ordinary cell values remain intact. An individual file over the TUI attachment limit must fail visibly as a whole, with no excerpt or partial new model input; failed refresh keeps the last complete snapshot and other attachments remain active. Test near-bound text, PDF, DOCX and multi-sheet XLSX content, plus reader-reported truncation (including the current XLSX default row limit), so an incomplete read is never marked attached. D-93 also rejects a proposed combined attachment set above its budget while retaining existing complete snapshots. D-95/D-97 set estimated-token measurement and omitted limits at 4,000 per file and 8,000 combined; the exact estimator, override ranges and processing safeguards require further decisions. |
| AC-22 | On a fresh installed TUI with its documented OCR prerequisites, selecting a genuine scanned/image-only PDF runs page rendering and Tesseract OCR and attaches usable recognized text to the next and later eligible model turns through the same snapshot path. Verify the actual model input, not just a successful OCR subprocess or filename. A mixed-page fixture must keep original page order, include embedded text and OCR text from their respective pages, and show no duplicate OCR for text pages. For an image-only PDF, a render failure, missing Tesseract or language data, OCR failure, or no usable recognized text produces a visible failure rather than an attached placeholder; a failed refresh retains the last good snapshot. For a mixed PDF whose required OCR page fails between readable pages, reject the entire new attachment with a page-specific error, pass no partial PDF text to the model, and keep an existing complete snapshot on failed refresh. Test the neutral OCR unit independently, then its selected-file integration and installed macOS/Linux terminal workflow. Require separately system-installed Tesseract, default to English OCR, and accept one or more installed language packs through `tui.attachments.ocr_languages`. Verify configured pack names reach Tesseract, missing requested packs fail the OCR attachment by name without silent fallback, and existing CLI configuration handling remains unchanged. Document macOS/Linux installation, language-pack checks and relaunch recovery in the TUI guide, and verify ordinary attachment without Tesseract; preserve Chat `/read` and `friday-cli` behavior. A fresh TUI installed from a wheel or sdist on macOS/Linux must include its PDF-rendering dependency and process scanned PDFs without separate renderer installation; Tesseract remains the system prerequisite. D-92 also rejects scanned PDFs that exceed the per-file extracted-content limit without attaching a partial OCR result. The usable-text criterion, OCR-language validation bounds, exact renderer selection and size/time thresholds need further decisions. |
| AC-23 | In the installed TUI, a fully assembled first conversational model request is checked against the selected model's effective input budget after normal Friday context selection. Use an enforceable UI-neutral estimate of complete outgoing input, including system instructions, selected history/memory, tool definitions, the user draft and whole active attachments, with the configured output reserve. If over budget, apply AC-24's eligible older-turn compaction and fresh recheck before deciding whether to send the primary request. If it still does not fit, show estimated total, available budget and overage; preserve the exact draft/caret and attachment snapshots. No accepted prompt, pin update, editor-recall/new transcript or session turn, blocked primary provider request, user-turn tool execution, file truncation or runtime-config change occurs. Compaction's separate model calls and persistent memory effects must remain observable and must not be mislabeled as a side-effect-free rejection. Test below/equal/above budget with deterministic counts, varied context components, separate primary and maintenance provider spies, state/effect checks and correction followed by successful resubmission. Verify installed macOS/Linux recovery and unchanged Chat/CLI behavior. Exact estimator/reserve remains open; AC-25 covers post-send provider context-length rejection. |
| AC-24 | In the installed TUI, an initial or later agent-loop conversational model step that exceeds budget triggers at most one eligible request to Friday's UI-neutral older-turn compaction service when runtime `memory.compaction.enabled` is true. Preserve configured service, in-flight/cooldown, recency and minimum-history eligibility; report progress and result/failure. Reassemble and re-estimate the whole pending request after compaction, independently of `target_met`; if it fits, continue that step automatically. If disabled, unavailable, ineligible, failed or still over budget, do not send the blocked conversational request or invoke further tools. A failed initial step retains draft/caret/attachments without accepting a turn; a failed later step leaves the turn incomplete while retaining recorded activity and prior tool effects, with transcript treatment under AC-28. Do not trim current tool output or attachments, fabricate an active-loop summary, import Chat/CLI handlers, roll back completed compaction effects, or silently alter runtime settings. Test each gate and failure, one-attempt bound, durable maintenance effects, reassembly below/at/above budget, a tool-executed later step, visible status, installed macOS/Linux behavior and unchanged Chat/`friday-cli` regressions. Bind the neutral service/effect contract before construction. |
| AC-25 | In the installed TUI, a request that passed the local budget estimate but receives a recognized provider context-length rejection displays that provider error with user-directed correction and retry. The TUI does not automatically compact or resend after this post-send error. For an initial request, the submitted draft and active attachment snapshots remain available for editing/resubmission under AC-26 without overwriting newer unsent editor text; AC-27 excludes a failed-attempt transcript entry. For a later request, the current turn is incomplete, earlier Activity and tool effects remain, and no further loop step runs; AC-28 excludes an incomplete-turn transcript entry. The UI distinguishes this from a local preflight rejection and does not claim the provider was never called or that completed runtime effects were reversed. Deterministic fake-provider cases cover recognized and unrelated errors, no TUI-level compaction/resend, preserved user state and tool effects, and Chat/`friday-cli` regressions; installed macOS/Linux terminal UAT covers the recovery message. Bind context-length classification and provider detail before construction; preserve Friday LLM transport retry policy. |
| AC-26 | After an initial post-send provider context-length rejection, an empty editor receives the exact failed submitted prompt text and caret position automatically, without resubmission, compaction or attachment change. If a newer unsent draft occupies the editor, keep its text/caret/focus unchanged and show a visible clickable and keyboard-focusable `Restore failed prompt` action with the provider-error notice. Activating Restore with a nonempty editor uses the existing confirm/cancel replacement behavior: Cancel keeps the newer draft exactly; Confirm places the failed submitted prompt in the editor for editing without sending it. Test both editor states, multiline prompts, caret/focus, Confirm/Cancel, attachment snapshots, no extra provider request, headless UI and installed macOS/Linux terminal UAT. AC-29 governs action placement after view eviction; AC-27 governs failed-attempt transcript exclusion. Keep Chat/`friday-cli` behavior unchanged. |
| AC-27 | After a recognized post-send provider context-length rejection on the first conversational request, the failed attempt creates no persisted transcript record. The error and submitted prompt stay recoverable in process under AC-26 during the current TUI run; relaunch does not reconstruct them from a transcript, and attachments remain run-scoped. In a disposable transcript store, verify unchanged record count and existing entries after failure, one normal record after a successful corrected resubmission, no duplicate failed record, and no failed-attempt recovery after relaunch. Do not mislabel provider telemetry or any configured compaction memory effects as transcript records or imply they were rolled back. Test the neutral persistence ordering separately from the TUI editor and installed macOS/Linux UAT; preserve Chat/`friday-cli` behavior. AC-28 covers a later post-tool failure. |
| AC-28 | After one or more tools execute, a later conversational model step that fails for context length leaves the turn incomplete in the current TUI view, with its earlier Activity and tool effects visible while retained under the existing bounded-view rules. This applies both to a local overage after D-99's eligible compaction/recheck and to a provider rejection after a passing estimate under D-100. No incomplete-turn transcript record is written, including a prompt/status-only entry or serialized Activity. With a fake executing tool and disposable transcript store, verify no further model/tool call, unchanged prior transcript records after each failure path, visible incomplete state and Activity until clearing/eviction or exit, retained actual tool effect, and no reconstruction from `/transcript` after relaunch. Check installed macOS/Linux terminal behavior and unchanged Chat/`friday-cli` regressions; provider telemetry and configured compaction effects remain separate. |
| AC-29 | When a failed initial provider context-length error notice is evicted from the bounded conversation, a compact `Restore failed prompt` action remains visible beside the editor while that prompt is recoverable in this TUI run, independently of the Context sidebar. The action is pointer- and keyboard-accessible, appears without stealing focus, and is absent when no failed prompt is recoverable. With a newer unsent draft, Cancel preserves its text/caret/focus; Confirm restores the exact failed prompt/caret for editing without submitting, changing attachments or making another provider call. Verify notice eviction, narrow/reshaped terminal layouts, focus traversal, Confirm/Cancel, current-run teardown, headless interaction and installed macOS/Linux UAT. AC-30 covers explicit display clearing. |
| AC-30 | After a failed first provider context-length attempt leaves a recoverable prompt and a Restore action, invoking `/cls`, `/clearscreen` or the bound clear-display shortcut removes the conversation error notice, latest prompt pin and Activity as in AC-03, but retains the in-process failed prompt and an editor-adjacent `Restore failed prompt` action. The action remains visible and keyboard/pointer-accessible without stealing focus; its Confirm/Cancel path protects any newer draft and does not submit or call the provider. Verify both slash aliases and the shortcut against a disposable transcript store, including cleared view state, unchanged prior transcripts, no failed-attempt record, no extra provider request, recovery during this run and no recovery after relaunch. Include headless tests and installed macOS/Linux terminal UAT. |
| AC-31 | If an older failed initial provider-context prompt is still recoverable when the user submits a different conversational prompt, keep its Restore action and payload while the new turn is pending, including after admission or partial output. Once that different turn completes successfully, discard the old recovery payload and remove Restore from beside the editor and any retained error notice. The old error text may remain as bounded, non-actionable current-run display, but the failed attempt is never added to the transcript; the successful turn is recorded normally once. A newer failed turn or slash command does not by itself clear the older recovery. With a fake provider and disposable transcript store, test pending, partial, failed and successful outcomes, both action placements, no extra provider call or automatic retry, unchanged attachment snapshots and successful-turn result, and installed macOS/Linux UAT. AC-32 governs presentation of multiple pending recoveries. |
| AC-32 | If two or more failed initial provider-context prompts are recoverable while the editor contains a newer draft, show one compact `Restore failed prompts (N)` control beside the editor, with the accurate pending count. Activating it opens a keyboard- and pointer-accessible chooser with distinct entries newest first; retained error notices have no separate Restore controls in this multiple-prompt state. One pending prompt uses the singular Restore control, and zero pending prompts shows none. Opening, browsing and canceling the chooser preserve the newer draft text/caret and do not submit or call the provider; focus moves to the chooser intentionally and returns predictably on close. Selecting either failed prompt follows the existing Confirm/Cancel protection before replacing a nonempty editor, with exact text/caret restoration only on Confirm. Verify count/order, both choices, notice eviction, `/cls`, narrow/reshaped layouts, focus, no failed-attempt transcript record, current-run teardown, headless interaction and installed macOS/Linux UAT. AC-33 governs selected-entry retention, AC-34 governs explicit dismissal, and the finite recovery-state bound belongs in the construction directive. |
| AC-33 | Confirming Restore of one pending failed prompt places its exact text/caret in the editor for editing but keeps its original recovery snapshot in the chooser or singular Restore control, with the same pending count and no duplicate entry. Editing, clearing or replacing the editor copy does not mutate that snapshot; the user can select it again and restore the exact original, subject to D-41 Confirm/Cancel if the editor is occupied. Cancel leaves all pending entries and the current draft unchanged. A later successful conversational turn clears all earlier pending failed-prompt recovery entries and controls; admission, partial output, failure, slash commands and `/cls` do not. AC-34 also permits explicit confirmed removal of one recovery entry. With two failed prompts and a newer draft, test repeated Restore and edit/overwrite, stable count/order and other entry, exact caret, no automatic provider request or failed-attempt transcript record, attachment preservation, successful-versus-failed later turns, and installed macOS/Linux UAT. |
| AC-34 | Each recoverable failed prompt offers `Dismiss`: alongside singular Restore at its current placement when one is pending, or on that prompt in the multi-prompt chooser. Confirm/Cancel protects removal of the selected in-process snapshot. Cancel keeps it; Confirm removes only that entry, updates the count and chooser order, switches to singular Restore when one remains, and removes Restore when none remain. An existing editor draft and caret, including a restored copy, and active attachments remain unchanged. A retained error notice may stay visible as non-actionable current-run history. Dismiss sends no provider request and writes no failed-attempt transcript. Verify zero/one/two-entry states, keyboard/pointer access, focus return, Confirm/Cancel, accurate controls, headless UI and installed macOS/Linux UAT. Bind a finite count/size limit and deterministic overflow behavior in the construction directive. |

Use Textual's [headless `run_test()` and `Pilot` APIs](https://textual.textualize.io/guide/testing/)
for automated input, output and resize tests. Add terminal/PTY smoke coverage for
behavior headless tests cannot establish, especially terminal restoration and
key handling. A launcher under `tests/integration/` is not acceptance evidence
or a substitute for the installed executable.

The [replacement plan](replacement-plan.md#3-testable-construction-sequence)
defines testable units and the current macOS/Linux UAT schedule. Write behavior
and failure cases before or alongside each increment; passing checks and
required user approvals gate dependent work. Failed, blocked or unrun required
cases prevent the relevant gate from passing. Completion requires AC-01 through
AC-34, including the
[user documentation requirement](user-guide-requirements.md) and the
[reasoning display requirement](reasoning-display-requirement.md) and
[tool-activity requirement](tool-activity-requirement.md).

Run deterministic fake-runtime tests first, then neutral-service integration
tests with disposable real stores and fake provider transports. Final installed
UAT additionally requires a controlled real provider and executing tool; select
the provider and obtain any needed service/cost/state authority before that run.
UI tests must not read or mutate a developer's existing Friday state.

## 9. Construction sequence and remaining decisions

The [replacement plan](replacement-plan.md) is the current draft for an
independent package, neutral service extraction, typed execution events,
testable units and macOS/Linux UAT. The prior [build plan](build-plan.md),
[integration contract](integration-contract.md),
[tactical plan](tactical-plan.md),
[test/UAT unit map](test-and-uat-plan.md) and
[CD-TUI-001](directives/CD-TUI-001-shared-presentation-contracts.md)
are withdrawn historical proposals. Their 24 units, five checkpoints and
Chat API changes cannot be used as construction gates.

The first neutral session-identity unit is verified. The approved neutral
configuration-loader unit is frozen at candidate `4a5311f2`. Its first
independent review was [BLOCKED](validation/VAL-N01A-neutral-config-loader.md)
only because the automated Linux smoke could not run. The maintainer
[deferred that check for N01A closeout](directives/CD-TUI-N01A-neutral-config-loader.md),
and a fresh independent reviewer returned
[VERIFIED](validation/VAL-N01A-waiver-closeout.md). Linux testing remains a
later TUI cross-platform/release gate. Dependent construction needs its own
approved directive.
Later product units need their own bounded directives and authority. At each
increment, test behavior and regressions before dependent work. macOS user
UAT begins at the first usable shell; automated Linux checks are active under
TUI-CI01, and hands-on Linux terminal UAT remains mandatory on the final
installed candidate. A controlled
real-provider/tool run is also required for first-release acceptance; select
its provider before final UAT. Build the user guide and configuration reference
alongside the features they describe and verify them against that candidate.

The [board](../../board.yaml) records `started` on `feature/friday-tui` with
implementation authority `granted` for TUI-CI01's Linux Actions workflow
only. N01A is closed under its unit-specific Linux deferral. No TUI
executable, UAT result, publication or acceptance of the full initiative is
claimed by this packet.

## 10. Planning review record

Chuck Russell requested review and revision of this README on 2026-10-16 and
selected the current `friday-chat` application as the command-parity target.
He additionally required that TUI design and implementation preserve the
current `friday-cli` feature set and behavior. Section 1.1 and AC-09/AC-10 make
that an explicit architecture boundary and acceptance requirement.
He clarified that the TUI must evolve by adding and enriching `/` commands.
Section 3 and AC-11/AC-12 require extensible registration, discovery,
compatibility and frontend isolation; the initial inventory is not a ceiling.
The earlier documentation review was scoped to this README and changed no
product code, tests, package metadata or runtime behavior. Its validation covered
source-based inventory reconciliation, links, whitespace and board/dashboard
agreement.

The review replaced the obsolete legacy-session extraction plan, made command
and startup coverage explicit, separated display effects from memory mutations,
identified the remaining typed lifecycle/output contracts, and replaced a manual
launcher-only check with measurable parity and terminal acceptance criteria.
Chuck Russell subsequently requested activation, a dedicated branch and a build
plan. The packet remains active for design/planning under [bounded
authority](authority.json). Q-01 through Q-03 and the later decisions in the
[decision register](decisions.md) are accepted. His independent-package
clarification withdrew the Chat-dependent integration contract and first
construction directive. The [replacement plan](replacement-plan.md) now
records the accepted follow-up decisions and remaining technical design.
An exact directive still requires review before product implementation.
