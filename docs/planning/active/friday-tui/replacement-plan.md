# Friday TUI independent integration and construction plan

**Status:** Active replacement planning contract; N01S and N01A independently
VERIFIED; CI01-CI03 automated Linux gates VERIFIED; N01B-01 pre-push candidate
and exact-source Ubuntu gate independently VERIFIED

**Branch and authority:** `feature/friday-tui`; `granted` for the exact
CD-TUI-N01B-01 subunit only; later product units remain design-only

**Source baseline:** `c34269867be50f71923c93c95a63236a35505812`

This is the current planning path for an independently installable Friday TUI.
The [product requirements](README.md) and [accepted decisions](decisions.md)
control its scope. The [command inventory](command-matrix.md),
[screen proposal](screen-layout.md), [neutral-capability map](neutral-capability-map.md),
[reviewed neutral configuration loader contract](neutral-config-loader-contract.md),
[draft startup bootstrap contract](startup-bootstrap-contract.md),
[reasoning requirement](reasoning-display-requirement.md) and
[Activity requirement](tool-activity-requirement.md) provide supporting detail. The
earlier [build plan](build-plan.md), [integration contract](integration-contract.md),
[tactical plan](tactical-plan.md), [test/UAT plan](test-and-uat-plan.md), and
[CD-TUI-001](directives/CD-TUI-001-shared-presentation-contracts.md) are
withdrawn Chat-dependent history, not construction instructions. The rows
below do not themselves authorize product code, a dependency change, UAT
signoff or publication; N01S had its own now-closed approval.

## 1. Invariants and package direction

- `friday-tui` owns its executable, command handlers/registry, UI, input,
  presentation configuration and lifecycle. Neither its source nor installed
  dependency closure imports or requires `friday-chat` or `friday-cli`.
- Both CLI applications keep their current feature set, defaults, output,
  configuration and operational behavior. TUI work does not refactor
  `packages/friday-cli`. Shared changes require before/after behavioral
  evidence for Chat and `friday-cli`, including installs with and without TUI.
- A capability currently trapped in `friday-chat` may be extracted into a
  UI-neutral Friday service when parity needs it. Chat and TUI call that
  service through their own handlers. Extraction is scoped by command family
  and must not move presentation code or make the neutral package depend on
  either frontend. No wholesale copy of Chat handlers into the TUI is approved.
- The maintained Chat registry is the source behavior inventory, not a runtime
  dependency. The TUI independently registers its commands and derives its
  help, completion and palette from that registry. Every command and alias in
  the [50-command snapshot](command-matrix.md) needs syntax, effect, error,
  state and optional-service parity. A source-registry drift check must fail
  when a new Chat command has no assessed TUI case.
- Use Friday's existing runtime files and service semantics. A TUI-only
  `tui:` namespace in the common `cli-config.yaml` controls view and
  interaction only; it never selects a model, storage path, tool policy or
  runtime mode. Existing CLI readers and behavior remain unchanged.

The source currently places `load_friday_py_config()` and `build_runtime()` in
`friday-chat`, while `friday-runtime` provides a headless kernel but does not
establish all Chat command capabilities. The first technical gate must map
each command family and startup behavior to an existing UI-neutral API or a
bounded extraction. A claim of "same runtime" is not evidence that the
configuration, maintenance and transcript behavior already match.

The [neutral configuration loader contract](neutral-config-loader-contract.md)
and [approved N01A directive](directives/CD-TUI-N01A-neutral-config-loader.md)
bind a shared Chat-compatible file loader and Chat facade. The
[startup bootstrap contract](startup-bootstrap-contract.md) collects D-47
through D-61, a source-backed proposed chooser signature and an explicit
failure-state test matrix. The N01A directive has separate bounded maintainer
approval; chooser construction needs its own later reviewed directive.
The [event and lifecycle contract](neutral-event-lifecycle-contract.md)
records source-backed ownership and failure boundaries for later units;
its exact API, hooks and termination mechanism need their own directives.

## 2. Integration contracts to finish before code authority

### Configuration and startup

Define a UI-neutral owner for the existing Chat runtime YAML parsing,
model-library resolution, environment interpolation and diagnostics. The
[loader proposal](neutral-config-loader-contract.md) separates that work from
storage path interpretation, service assembly and fake/real selection. The
TUI must accept the same files without translation and must not import the
Chat loader. Compare both frontends under the same files, environment and
captured working directory.
Preserve the existing version → startup replay → configured-startup precedence
where a TUI launcher exposes those options; interactive `/replay` remains a
separate command. A successful startup `--replay FILE` keeps a read-only file
and processed-count result screen open until Quit, without a first-release
turn-by-turn record; it does not admit prompts or enter the configured
interactive session (D-62, D-63). A failed startup replay keeps a read-only
file/error screen until Quit, then exits nonzero; it offers no in-process
Retry or transition to the chooser or interactive session (D-64, D-65).
After correction, the user relaunches. Without `--config`, show
a chooser for an existing runtime file. Its initial list comes from the
captured process launch working directory, with a Browse action for another
path (D-48); do not
automatically scan a user configuration directory or recurse. Explicit
`--config` bypasses the list. The initial list uses shallow, read-only
top-level YAML content inspection rather than filename stems (D-55). It
includes likely Chat runtime YAML with custom names and excludes recognized
model-library and CLI presentation YAML (D-49), without credential resolution,
service-reference loading, full runtime validation or startup. Bind the exact
key signature and filesystem error behavior in the bootstrap directive;
unrecognized files remain selectable through Browse. Recognizable but
incomplete runtime files remain listed and validate only on selection (D-57).
Browse allows folder navigation and typed or pasted absolute, relative and
`~` home paths to an existing file, including outside the launch folder.
Relative entry resolves from the currently displayed Browse folder, initially
the captured launch working directory; a missing or invalid selection follows
the chooser error and retry path (D-58). Browse never creates a file.
The visible keyboard-focusable Refresh action rescans only the launch folder's
candidate list on demand. Added, removed and newly recognizable files update
the list; a watcher does not update it automatically. Refresh does not fully
validate a configuration or start services. An empty list retains Refresh,
Browse and Quit (D-59).
Direct-child `.yaml`/`.yml` symbolic links that resolve to readable regular
runtime files count as candidates, including outside-folder targets. Broken,
cyclic, unreadable, directory-target or unrelated links stay off the automatic
list but remain reachable through Browse and D-50 error recovery (D-60).
A chooser-selected invalid runtime file keeps the chooser open with an
actionable error, Retry of the selected path after an external correction,
Browse to another file and Quit (D-50). It cannot start the runtime. No startup
file creation or preference rewrite is implied. An invalid explicit `--config`
file reports an error and exits nonzero without opening the chooser or starting
the runtime (D-51). When the launch-folder list is empty, the chooser stays
open, says no configurations were found there, and offers Refresh, Browse and
Quit (D-52, D-59). Refresh does not search elsewhere or start the runtime.
For interactive TUI startup after an explicit or chosen config, omitted
`--runtime` means `real`; `--runtime fake` explicitly selects deterministic
services. If real startup fails after a chooser selection, close partially
started services, show the error and return to the chooser with Retry of the
selected file, Browse and Quit when cleanup succeeds (D-53). If cleanup also
fails, report both failures, restore the terminal as far as possible and exit
nonzero without in-process retry (D-56). A failed real startup never silently
becomes fake.
With an explicit `--config` path, failed real startup closes partial services,
reports the error and exits nonzero without opening the chooser (D-54); any
cleanup failure is also reported.
This TUI default does not change Chat's current fake default or `friday-cli`.
Version and startup replay keep their own precedence and behavior.
`FRIDAY_CHAT_RUNTIME` remains a Chat-only launcher setting: it cannot change
the TUI's real default or explicit `--runtime` choice (D-61). Runtime YAML
environment interpolation and credential lookup remain compatible.

Read the common presentation file independently or through a neutral typed
reader. Keep explicit-file → sibling-file → defaults selection and leave root
CLI fields intact. Validate only the TUI namespace for TUI startup; existing
CLI applications continue to ignore valid-YAML TUI-only fields. The exact
schema bounds, keyboard collisions and visible setting effects belong in
scoped UI units, with `tui.output.reasoning_visibility` defaulting to `hidden`.

### Commands, state and lifecycle

For every command family, record the Chat handler's observable contract, the
neutral service owner, any extraction required, the TUI handler, and tests on
equivalent disposable fixtures. Cover `@agent`, disabled-by-default `!`,
startup options and optional-service failures separately from slash commands.
Do not substitute a registered name or copied output string for effect parity.
Typed outcomes carry progress, errors, state changes and UI effects; the TUI
does not parse formatted CLI text for status.

The TUI owns every runtime, client, worker and terminal resource it creates.
Normal Quit closes admission, allows accepted non-interruptible work to reach
the owner's safe stopping point, performs ordered cleanup and restores the
terminal. A busy submission, including `/q`, is rejected with its draft
retained; Ctrl+Q or the Quit action requests normal graceful Quit. An explicit
emergency **Force quit** action is separately available while Quit is
pending. It requires a clear warning and deliberate confirmation that work,
persistence and cleanup may be incomplete. It is never reported as successful
graceful cleanup. Define the process/worker termination mechanism, best-effort
terminal restoration and recovery instructions in the lifecycle directive;
do not treat thread cancellation as proof a mutation stopped.

### Provider and tool events

Define a typed, UI-neutral, per-operation event stream rather than enabling
telemetry or scraping CLI output. Its semantic event set must cover:

| Event | Required facts |
| --- | --- |
| Provider step | Operation/exchange ID, step ID, actor/agent, sequence and start/end state. |
| Provider reasoning | Text actually supplied for that step, in order; never synthesize text from a token count. The TUI discards text received while visibility is hidden. |
| Tool request rejected | Only after a model or user requested the tool: identity and runtime reason, labeled `Not run`; no execution status or executed-call count. |
| Tool execution started | Stable invocation ID, actor/workflow, step/order, native or MCP identity and a bounded view snapshot of the structured argument values actually delivered to the tool after runtime validation/normalization; mark any field truncated for size. |
| Tool execution terminal | Same invocation ID, completed/failed/timed-out/cancelled state, ordering and elapsed time if known; no result payload in Activity. |
| Final response | Ordered answer chunks or final text, separate from reasoning and tool Activity. |

Capture execution arguments at the invocation boundary. Model tool-call deltas
prove a request, not execution; retained MCP records can omit argument values,
and current agent telemetry truncates them. A failed preflight after an actual
tool request belongs in `Not run`. Selection or budget exclusions before a
request do not create Activity entries. Failure after execution begins belongs
in an executed-call failure state. Correlation must handle repeated names,
delegated agents/workflows and manual `/run-tool` calls without conflation.
Current agent execution is serial;
tests may inject completion reordering to validate the event contract, but
parallel execution is not introduced merely to satisfy a UI test.

Activity is bounded in-process view state, inspectable after the final answer
while retained in the running TUI view; it is not added to session storage,
transcripts or exports.
The TUI adds no credential/sensitive-value masking to argument values.
Retained entries can wrap, scroll or collapse. Values within the per-entry
limit remain complete on expansion; an oversized value gets a bounded preview
and explicit truncation notice, and the TUI discards its overflow. This does
not change the complete argument delivered to the tool. An overall rendered
cap shows when old entries are evicted. Automatic agentic tool-result payloads
stay out of Activity and the scrolling conversation. A user-entered
`/run-tool` keeps its existing inline command result and also adds an Activity
entry. Delegated calls show their
actor; rejected requests show `Not run` with a reason. Existing runtime tool
security, sanitization and approval policy is unchanged.

Selected visible Activity and shown provider reasoning can be copied. Copy
uses only selected rendered text: an oversized argument contributes its
bounded preview and truncation notice, never discarded overflow; reasoning
received while hidden is unavailable. Copy does not add these views to
session storage, transcripts or exports.

When bounded rendering evicts older conversation messages, show a clear
notice. Direct the user to `/transcript` for saved older messages when that
store is available; otherwise say no saved transcript is available. Do not
add a first-release `Load older` control or suggest that `/transcript` can
restore transient Activity or reasoning. UI eviction does not delete any
persisted transcript or memory record.

`/cls` and `/clearscreen` clear the displayed conversation, pinned prompt and
Activity view without replacement text. The pin stays empty until the next
accepted conversational prompt. Session history, memory and persisted
transcripts are unaffected; later work may add new Activity entries. D-105
keeps a recoverable failed first prompt and its editor-adjacent Restore action
after this display clear, while the error notice disappears with the view.
D-106 keeps that recovery while a different conversational turn runs and
clears it only on successful
completion, leaving any retained error text non-actionable. D-107 presents
multiple current-run recoveries through one editor-adjacent newest-first
chooser, with no transcript entry for a failed attempt. D-108 keeps a
confirmed restored prompt in that pending set until conversational success or
explicit confirmed Dismiss (D-109); editing the editor copy does not change the
recoverable original. Dismiss removes one snapshot without changing that editor
copy or sending a request. The directive binds finite recovery-state limits
and deterministic overflow behavior as construction details.

Reasoning is hidden by default. An in-app toggle can change visibility for
subsequent events without rewriting the config file; earlier hidden text is
not held for retroactive reveal. Shown text is labeled, collapsible and
separate from the final answer. No TUI-added raw-reasoning persistence, export,
memory, telemetry or log path is approved. Bind the accepted `/cls` and
selected-visible-text copy behavior, then specify exact copy controls and
rendered-cap behavior for these transient views in the UI directive. No
transcript-session switching control is in the first
release; `/switch [agent]` retains its active-agent meaning.

## 3. Testable construction sequence

Each unit needs a separate exact-path directive, expected behavior and
negative cases, a frozen candidate, focused tests and fresh independent
review before dependent implementation. The IDs below are planning units.
N01S and N01A are independently verified, and the CI01-CI03 infrastructure
work has a green [Ubuntu run](validation/TUI-CI03-ubuntu-run-39183895627.md)
and [final independent review](validation/VAL-TUI-CI03-final-676700f5.md).
N01B is the next product unit. Its first read-only query-contract
subunit is bounded by [CD-TUI-N01B-01](directives/CD-TUI-N01B-01-neutral-transcript-query-contracts.md)
and the [before-code baseline](validation/N01B-01-before-code-characterization.md),
and its exact directive is approved for bounded construction.
Installed TUI terminal UAT on macOS and Linux remains a release gate.

| Unit | Demonstrable result | Immediate evidence before next unit |
| --- | --- | --- |
| TUI-N00 | Source command/configuration/service inventory and protected CLI baseline. | All current command/alias/argument routes mapped; neutral API gaps named; unchanged Chat/`friday-cli` tests and installed behavior captured. |
| TUI-N01S | Approved small neutral session-identity extraction with Chat compatibility re-exports under CD-TUI-N01S. | Same generated/injected identity, mismatch exception and transcript propagation through Chat; neutral import closure and unchanged Chat/`friday-cli` comparisons. This unit alone does not supply neutral runtime assembly. |
| TUI-N01A | One neutral Chat-compatible runtime-file schema/loader with a Chat public-API facade; no service assembly. | Frozen legacy/canonical fixtures show identical typed results, diagnostics, model-library binding, path anchors and errors from Chat and the neutral loader; Chat monkeypatch seams and `friday-cli` regressions preserved; installed dependency/import closure checked. |
| TUI-N01B | Neutral session, transcript, command-effect and resource-close primitives needed by the first command families. | Per-capability effect fixtures and protected frontend comparisons; no TUI/CLI imports in neutral packages. Split further by owner if needed. |
| TUI-N01C | Neutral real/fake runtime assembly over the shared config and required primitives, without frontend imports. | Same effective model/service, storage, maintenance, tool, transcript and close behavior from Chat and a neutral caller under identical files, environment and captured cwd; failure injection and CLI regressions. |
| TUI-N01D | UI-neutral selected-file context input for the TUI, separately scoped from Chat file commands and memory ingestion. | Typed file identity/content snapshot and attachment outcome reach accepted model-turn assembly without Chat/CLI imports. Disposable-file tests prove content captured at selection reaches successive accepted turns until explicit removal, then is absent; source edits/deletion do not silently change the snapshot, and removal does not change an already admitted turn. Selecting a second distinct file preserves the first and both reach later turns; removing one leaves the other. Reselecting the same file refreshes in place without duplication; failed refresh reports error and keeps the last good snapshot. Attachment state is in-process only and begins empty on a new TUI run, independent of transcript availability. Missing/read-failed initial files are not reported as attached, and attachment does not call `/ingest` or alter Chat/`friday-cli` behavior. D-92 rejects an over-limit individual file without partial model input and retains the last complete snapshot on failed refresh. D-93 rejects a new attachment that would exceed the combined budget while keeping existing snapshots; an over-budget refresh keeps its prior snapshot. Test two individually valid files whose sum exceeds the budget, unchanged next-turn model input after rejection, manual removal and successful retry, and failed-refresh retention. D-94 makes both bounds optional TUI-only settings in the shared presentation file with defaults; test omitted, valid custom and invalid settings through the neutral presentation reader without changing CLI behavior. D-95 measures the complete formatted attachment text in estimated tokens, including labels and OCR/formula content. D-96/D-97 make omitted defaults fixed at 4,000 per file and 8,000 combined estimated tokens across models rather than context-window-derived; test identical defaults and file-admission outcomes with differing and unknown model metadata, plus explicit override and below/at/above numeric boundaries. Inject a deterministic estimator to test per-file and proposed-combined boundaries, refresh replacement without double-counting, visible estimated-token errors and actual model input. Bind exact field names, estimator/headroom, allowed override ranges, format safeguards and runtime-context interaction in a directive after the remaining product choices. |
| TUI-N01E | Neutral file-content extraction for first-release attachment formats. | Verify the existing `friday-tools` reader factory/format readers through a typed neutral boundary usable by an independently installed TUI. Positive synthetic text/code/CSV/JSON/YAML, real PDF with extractable text, DOCX and XLSX fixtures prove content reaches N01D rather than Chat's placeholders; negative fixtures cover corrupt, unreadable and empty extraction, and missing reader dependencies produce explicit failure. Include required PDF/DOCX/XLSX reader dependencies in the installed TUI; verify no Chat `/read` or `friday-cli` behavior change. Tesseract OCR is a separate TUI-N01F unit. For XLSX, enumerate every worksheet, including hidden and non-active sheets, label each by name in workbook order and pass their combined content through one attachment snapshot. A genuine multi-sheet fixture with a non-first active sheet and distinct hidden-sheet content must prove the actual model input includes each sheet; no silent active-sheet-only success or silent loss from a size bound. Inject a read failure in the middle sheet of a multi-sheet workbook: reject the whole new attachment with the sheet and cause named, send no partial workbook content to the model, and retain the last complete snapshot on failed refresh while other files remain attached. A readable empty sheet is not a read error, but all-empty content is not successful attachment. For formula cells, obtain the original expression as well as any workbook-saved result, label both with sheet/cell identity, and mark an absent saved result unavailable without evaluation or fabricated value. Test formula cells with numeric/text saved results and no saved result, ordinary values, all-sheet ordering and actual model input. The existing `data_only=True` reader yields saved results alone; bind a neutral formula-aware read without changing Chat/CLI behavior. D-92 requires whole-file rejection above the per-file extracted-content bound; test under/over-bound text, PDF, DOCX and multi-sheet XLSX, reader-reported truncation (including the XLSX default row limit), visible error, no partial model input and last-good refresh retention. D-93 also requires aggregate-budget admission to reject a new complete extraction without trimming existing attachments. Use D-95 estimated-token counts of complete formatted content, not raw bytes/characters; test labels and formula/OCR overhead with a deterministic estimator. D-97 fixes omitted per-file and aggregate thresholds at 4,000/8,000 estimated tokens; bind allowed override ranges before this unit's directive. Existing seven reader tests are a baseline, not positive PDF attachment proof. |
| TUI-N01F | UI-neutral scanned-PDF extraction using Tesseract OCR. | Use a defined cross-platform page renderer declared as an installed `friday-tui` dependency to feed Tesseract, then pass recognized text through N01D's snapshot/model-context path. A genuine image-only PDF fixture must produce nonempty text in the model input; a subprocess success or UI label alone is insufficient. Separate page-routing tests and a mixed-page fixture must prove embedded-text pages skip OCR, scanned pages run Tesseract, original page order is preserved, and no duplicate page text enters model context. Inject missing renderer, missing Tesseract/language data, corrupt page, OCR error, empty recognition and timeout. Verify English default, multiple configured installed language codes passed to Tesseract, invalid setting shape, and named missing-pack failure without English fallback. A three-page mixed fixture with a failing scanned middle page must reject the whole new attachment, identify the page/cause, send no partial PDF text to the model, and preserve a prior complete snapshot on failed refresh. Require separately system-installed Tesseract rather than bundling or installing it from the TUI. Verify discovery on `PATH`, actionable missing-tool failure only when OCR is needed, unaffected text/embedded-text attachment, and correction after relaunch on installed macOS/Linux candidates, plus unchanged Chat `/read` and `friday-cli` regressions. Prove fresh wheel/sdist installation on macOS and Linux renders scanned PDF pages without a separate renderer installation, while Tesseract remains system-installed. Apply D-92 to scanned and mixed PDFs: an over-limit extraction rejects the whole new attachment with no partial OCR text and preserves a last-good refresh. Bind the exact renderer, its license/platform/native dependency behavior, usable-text criterion, language-code validation bounds and size/time thresholds before its directive. |
| TUI-N01G | UI-neutral enforceable budget preflight for each conversational model step. | Assemble and estimate the complete pending request after normal Friday context selection, including system instructions, selected history/memory, tool definitions, user draft or current loop content, whole active attachments and configured response reserve. An over-budget result carries estimated total, available budget and overage; no conversational provider request proceeds until it fits. Integrate N01H as the single eligible recovery attempt, then reassemble and re-estimate. If the initial step still fails, TUI retains exact draft/caret and attachment snapshots without a new accepted turn, pin, editor recall or transcript/session turn; no blocked primary request or user-turn tool runs. If a later step fails, report an incomplete turn and retain prior recorded tool activity/effects without further model/tool calls; N01K excludes an incomplete-turn transcript entry. Compaction maintenance calls and memory writes are separate, observable effects. Deterministic below/equal/above and first/later-step tests use separate primary/maintenance provider spies, varied context components, corrected retry, and unchanged Chat/CLI regressions. Bind the neutral enforcement seam and exact estimator/reserve before construction; D-100 handles recognized provider context-length rejection after a passing estimate in N01I. |
| TUI-N01H | Configured older-turn compaction recovery for an over-budget model step, separate from manual `/compact` parity. | Expose a UI-neutral runtime request that honors `memory.compaction.enabled`, service availability, in-flight/cooldown state, protected recent turns and minimum compactable history. At most one eligible attempt is made per over-budget step; it may call a configured maintenance model and persist turn summaries plus configured ancillary memory maintenance. Return typed started/skipped/completed/failed status and effect details for bounded UI feedback. Reassemble the pending request after the attempt and let N01G re-estimate it even when `target_met` is true. Test unavailable/disabled/empty-history and eligibility gates, maintenance model calls and durable memory effects, success that brings the request below or exactly to budget, ineffective/error/timeout outcomes, one-attempt bound, later loop with an already executed tool, no current-loop/tool-output/attachment truncation, no Chat/CLI imports, and unchanged existing frontend behavior. The construction directive must bind exact maintenance coordination and persistence semantics. |
| TUI-N01I | Post-send provider context-length rejection and user-directed recovery. | Through a UI-neutral provider-error outcome, distinguish a recognized context-length rejection from generic invalid requests and other provider failures after a passing N01G estimate. Show the provider error and a correction/retry path without TUI-triggered compaction or resending. Preserve the submitted initial draft/caret for D-101 editor recovery and active attachment snapshots without overwriting a newer unsent draft; for a later loop step, mark the turn incomplete, retain recorded Activity and completed tool effects, issue no further loop step and apply N01K transcript exclusion. Do not claim the provider request was never sent or roll back completed runtime effects. Inject recognized and unrelated errors with a fake provider, prove no TUI-level retry/compaction, test both first and post-tool later steps, preserve Chat/`friday-cli` behavior, and verify installed macOS/Linux recovery. Bind exact classification and provider-detail display in a directive; D-104/D-105 fix Restore placement after eviction and display clear; D-106 clears an older recovery after a different successful conversational turn; D-107 presents multiple recoverable failures in one chooser; D-108 retains a confirmed selected entry until conversational success or D-109 confirmed dismissal; bind finite recovery-state limits and deterministic overflow behavior in the construction directive; N01J owns failed-initial transcript exclusion and existing `friday-llm` transport retry behavior is unchanged. |
| TUI-N01J | UI-neutral transcript persistence boundary for an initial provider context-length rejection. | On a recognized post-send failure before any completed answer, keep D-101 error/prompt recovery in process and write no failed-attempt transcript entry. Use a disposable transcript store to prove unchanged record count/content after failure, one normal successful turn after a corrected user resubmission, no duplicate failed record and no restoration of the failed attempt after relaunch. Distinguish transcript exclusion from provider telemetry and any separately persisted maintenance effects. Test this neutral persistence ordering independently of TUI widgets, then integrate with N01I/N03B; protect Chat/`friday-cli` behavior. N01K separately tests later post-tool failure persistence. |
| TUI-N01K | UI-neutral incomplete-turn transcript boundary after executed tools. | With a fake tool that produces a real disposable effect, drive a later provider step through both D-99 local overage after compaction/recheck and D-100 post-send context-length rejection. Return a typed incomplete-turn outcome, stop additional model/tool steps, retain the in-process Activity and completed effect, and leave the persistent transcript unchanged, including no prompt/status-only partial record or serialized Activity. Test each path against a disposable transcript store with prior completed turns, bounded view clearing/eviction, relaunch without transcript recovery, and unchanged Chat/`friday-cli` behavior. Distinguish transcript exclusion from provider telemetry and configured compaction memory effects; bind failure/persistence ordering in the directive. |
| TUI-N02A | Typed provider-step/reasoning events across successive model invocations. | Hidden/shown, text/count/neither, streaming/non-streaming order, follow-up after tools and no new persistence. |
| TUI-N02B | Typed tool request/admission/execution events for native and MCP tools. | Exact argument snapshot, `Not run` only for rejected actual requests, no entry for pre-request exclusions, start/terminal states, repeated IDs, exceptions/timeouts, delegated actors, manual calls and no result payload; CLI behavior unchanged. |
| TUI-N03A | Installable TUI bootstrap and independent common-file readers. | Help/version without services; chooser shallow-inspects top-level YAML in the launch directory, listing runtime-shaped canonical/legacy files with custom names, including incomplete `llm:` files and valid direct-child linked runtime YAML, including outside-folder targets, while excluding recognized model-library/display and unrelated YAML. Broken, cyclic, unreadable, directory-target and non-runtime links are Browse-only; test these and full validation on selection. Browse supports folder navigation and typed/pasted absolute, relative and `~` home paths to existing files, including outside the launch folder; relative entry resolves from the displayed folder, and missing/invalid choices retain D-50 recovery. Explicit paths bypass the list. Visible keyboard-focusable Refresh rescans the launch-folder candidates only on demand; tests cover added/removed/reclassified files, empty-to-populated and populated-to-empty lists, and no automatic watch. An empty list shows Refresh, Browse and Quit. Listing and Refresh perform no credential resolution, reference load, full validation or runtime start. Invalid chooser selections show a diagnostic and retain Retry of the selected path, Browse and Quit without starting the runtime; invalid explicit `--config` reports an error and exits nonzero without the chooser. Both selection routes default to real; explicit fake and failed-real-without-fallback cases. Set `FRIDAY_CHAT_RUNTIME` to fake, real and invalid values and verify it does not alter TUI mode while Chat retains its existing override. Inject partial real-start failure to verify cleanup, chooser recovery versus explicit-path nonzero exit and no fake fallback. Inject cleanup failure to verify both errors, nonzero exit, no in-process retry and best-effort terminal restoration. Check presentation schema/defaults including `tui.attachments.ocr_languages` and the D-94/D-95 estimated-token per-file/combined limit options: absent fields use fixed 4,000/8,000 estimated-token defaults across models with differing or unknown context metadata, valid custom values change only TUI attachment admission, invalid types/ranges fail before runtime services, and the existing CLI ignores valid YAML TUI fields. Verify package/dependency isolation and Linux automation. |
| TUI-N03B | Owned UI/backend bridge and first usable shell. | Bounded ordered events, `Enter` submits once, `Ctrl+Enter` inserts one newline without submitting where distinct, multiline paste never submits, busy draft retention, focusable Submit and Insert newline actions, failure teardown and terminal restoration. First macOS user UAT records physical key events and fallback behavior. Integrate N01G/N01H so an initial over-budget submission shows bounded compaction progress/result, then either continues after a passing recheck or shows total/available/overage while retaining draft and attachments; a blocked primary request is never sent. Integrate N01I/D-101 so a post-send provider context-length rejection automatically restores the exact submitted prompt/caret when the editor is empty; if a newer unsent draft exists, keep it unchanged and show a Restore action with the error and beside the editor after notice eviction (D-104). Test retained newer draft/caret/focus through eviction and D-105 display clearing, action activation with Confirm/Cancel and no extra request; D-106 keeps prior recovery while a different turn runs, then clears it only on successful completion, with failed outcomes leaving it available; D-107 keeps distinct failed-request identities and exact prompt/caret snapshots for a single newest-first chooser when more than one is pending, without overwriting a newer draft; D-108 keeps an immutable pending snapshot and count after Confirm and allows repeated Restore after editor edits/replacement. A successful conversational completion clears all pending entries, while D-109 confirmed Dismiss removes only the selected entry without changing the editor, attachments, provider or transcript; test Confirm/Cancel and count changes. Bind finite recovery-state limits and deterministic overflow behavior in the directive; recovery stays in-process under D-102. |
| TUI-N04A | Conversation, pinned prompt, inline command results and responsive navigation. | No duplicate prompt/history/export, chunk ordering, scroll/focus/resize, dark/light/contrast role cues and output bounds; N01G/N01H failed initial admission leaves the latest accepted prompt pin and conversation unchanged while a visible compaction/overage message explains recovery; a failed later step is marked incomplete with earlier activity intact; N01I/D-101 show a distinct post-send provider error, restoring the failed prompt into an empty editor or offering a keyboard-focusable Restore action when newer text exists; the action uses D-41 Confirm/Cancel replacement behavior and never submits; under D-104, bounded eviction of the error notice leaves a compact editor-adjacent, pointer- and keyboard-accessible Restore action only while the failed prompt remains recoverable in this run, including on narrow/reshaped terminals without focus theft; test notice eviction, focus traversal, newer-draft preservation and exact prompt/caret restoration with no extra provider call; D-102/D-103 leave failed initial and later incomplete turns out of persisted transcripts; typing a leading `/` shows registry-derived name/alias matches without changing the draft or submitting. After a recognized command and space, declared subcommand matches appear while its token is typed; no free-form value suggestions. A metadata-derived usage hint shows required/optional argument shapes for recognized command/subcommand syntax, updates as syntax changes, and inserts nothing. With suggestions open, `Up`/`Down` highlight and `Tab` completes only the highlighted command, alias or subcommand token while preserving other draft text and focus, without dispatch; a list with no highlighted match cannot insert. With no list open, `Tab` moves focus. `Enter` always submits the editor draft. Editor history includes accepted conversational prompts, `/` commands, `@agent` messages and enabled/admitted `!` commands, recalls them into the editor without dispatch, and excludes disabled/rejected routes, unsent/busy-rejected drafts and outputs; it starts empty on launch and is discarded on exit, independent of persisted transcripts. Browsing preserves an unsent draft and editing position, restores both on leaving without submission, and never mutates stored submitted entries. With suggestions closed, `Up` at the editor's upper boundary and `Down` at its lower boundary while browsing traverse history; interior arrows move the caret, and open suggestions take arrow priority. No F3/F4 history binding. Palette selection of a `/` command fills an empty editor without dispatch. With an unsent draft, Cancel preserves it exactly and Confirm replaces it without submission; later editor Submit dispatches once. Following pauses away from bottom, pin remains while reading its response but hides in older exchanges, a clickable and keyboard-focusable `Jump to latest` or scrolling to bottom restores it when available and resumes following, and `/cls` and alias clear the conversation, pin and Activity without changing session history or transcripts; D-105 keeps a recoverable failed-prompt Restore action beside the editor after both aliases or the bound clear-display shortcut, with no automatic resend. Test cleared view versus retained action and keyboard focus in headless and installed terminal UAT. Under D-106, a different conversational turn keeps old recovery while pending and removes Restore from editor and retained notice only after success; test pending, partial, failed and successful outcomes, non-actionable retained error text, and transcript boundaries. Under D-107, two pending failures show one accurate-count Restore control and a newest-first, keyboard/pointer chooser with no separate notice-bound Restore controls; test both selections, draft/caret/focus on open/cancel, D-41 Confirm/Cancel, narrow layout, view eviction and display clear without extra requests or transcript records. Under D-108, Confirm leaves the selected pending entry and count unchanged, repeated Restore retrieves its exact original after editor edits, and a successful conversational turn clears all older pending controls; test Cancel, failed turns, attachments and no duplicate entries. Under D-109, each pending prompt offers confirmed Dismiss; test single and multiple states, count/order changes, editor-copy preservation, focus and no provider/transcript effect. Eviction notice distinguishes saved `/transcript` access from unavailable transcripts; no `Load older` or transient-view recovery claim. macOS user UAT. |
| TUI-N04B | Activity and reasoning views over the typed event stream. | Activity sits inline with the exchange or tool command that produced it, ahead of its final response/result, with no persistent side pane; nested scrolling/collapse preserves answer visibility at 80x24. Verify multi-step automatic/manual/delegated calls, `Not run`, status, first-entry auto-open without focus theft or pulling the paused conversation viewport, user collapse/reopen, older exchange expansion states preserved across a new prompt while the new section opens independently, later entries retained without forced reopening, collapsed header count for appended entries only with reopen/`/cls` reset, eviction indicator while collapsed and detail on reopen. Expanded Activity follows only at its own bottom; scrolling up pauses, and a clickable keyboard-focusable `Jump to latest Activity` or scrolling back down resumes without moving the conversation. Verify bounded argument previews with visible truncation and unchanged execution values, selected visible text copy with no hidden reasoning or discarded overflow, `/cls` clearing, forward-only reasoning toggle, no persistence/export, overflow and final-answer separation. macOS user UAT. |
| TUI-N04C | First-release read-only Context file browser. | Browse folders and select files without ingesting memory, editing files or changing the transcript session. Test missing/inaccessible paths, keyboard/pointer focus, independent scrolling, collapse, resize and narrow macOS/Linux terminal UAT. Deliberate selection triggers the separate TUI-N04D attachment unit; focus movement or scrolling does not. |
| TUI-N04D | Context sidebar selection and attachment feedback over TUI-N01D. | Pointer click or keyboard activation immediately starts capturing and attaching the selected file for the next eligible model turn; no separate Add action and no automatic prompt submission. Show loading, attached and failed status plus a visible keyboard-focusable Remove action for each attachment. Test focus movement/scrolling without attachment, initial failure recovery, same-file reselect refreshing in place or preserving the last good snapshot on failure, busy editor preservation, two distinct files attached together, individual removal while another remains, continued snapshot context in later accepted turns after source edits/deletion, removal without altering an admitted turn, empty attachments after relaunch even with an earlier transcript, no file/memory mutation, and macOS/Linux terminal UAT. Resolve file-size, format-specific limits and aggregate budget handling before its directive. |
| TUI-N05 | Command-family parity in small independently checked slices. | Every PAR case's syntax, effect, state, failure and availability compared on disposable fixtures, including `/sessions` and `/transcript` inspection/export without changing the active transcript session and `/switch [agent]` changing the active agent; new registered names, aliases and declared subcommands appear in automatic `/` suggestions without separate UI wiring; Help and palette reflect the active registry; ongoing drift check; rolling macOS user UAT. |
| TUI-N06 | Normal safe Quit and explicit emergency Force quit. | Controlled slow/stalled operations, pending status, safe cleanup, confirmed force path, incomplete-work reporting, recovery and terminal behavior; macOS user UAT. |
| TUI-N07 | Installed candidate, user guides and aggregate acceptance. | Wheel/sdist and outside-checkout runs, no CLI regressions with/without TUI, AC-01..34 evidence, final macOS and hands-on Linux UAT, controlled real-provider/tool run and guide-based tasks. |

TUI-N03A also tests the D-62/D-63 startup replay path: version precedence,
isolated fake execution without config/chooser, compatible delay, a read-only
file/count result view that stays until Quit without a per-turn list, and no
prompt or command admission. D-64 adds missing/invalid CSV, invalid delay and
processing-failure cases: read-only file/error view until Quit, nonzero exit,
and no Retry or configured startup. Verify Quit and relaunch after correction.
Exact error categories and resource-close behavior remain directive work.

TUI-N01B, TUI-N01C and TUI-N05 must be subdivided into bounded directives after
review of the [capability map](neutral-capability-map.md). TUI-N01B-01 moves
only the three frozen transcript query views and their asynchronous query
protocol into a neutral module, with Chat compatibility re-exports.
`TranscriptExportResult`, query/store implementation, command effects,
session state and resource close remain outside that subunit. Subsequent N01B
subunits require their own source review and exact directives; N01B-01 alone
does not make transcript commands available in an independent TUI.
TUI-N01A is bounded by the
[reviewed loader contract](neutral-config-loader-contract.md) and
[approved exact directive](directives/CD-TUI-N01A-neutral-config-loader.md),
which authorizes only this bounded unit.
N02 events must be demonstrated against the
real neutral execution path, not just a synthetic UI feed. A usable shell is a
milestone, not first-release command parity.

## 4. Verification and UAT gates

- During every code unit, run its focused positive/negative/regression tests
  and affected Chat/`friday-cli` baselines. Neutral extraction also needs
  before/after outcome comparisons and package dependency-closure checks.
  Automate Linux checks throughout construction; include real terminal/PTY
  checks where headless tests cannot establish key delivery or restoration.
  In particular, simulate `Enter` and `Ctrl+Enter` separately in UI tests,
  then inspect actual delivered events and submission behavior in each target
  terminal. If the terminal aliases `Ctrl+Enter` to `Enter`, document and
  exercise the focusable Insert newline fallback rather than claiming the
  shortcut works there. Do not assign a second default newline shortcut;
  verify that mouse and keyboard activation of the visible control both
  insert exactly one newline without submitting.
- Perform hands-on macOS UAT at the first shell, Activity/reasoning,
  command-family and lifecycle milestones. Record actual user actions, fixture,
  candidate, observed result, defect and approval. An automated pass is not UAT.
- Perform hands-on Linux terminal UAT on the **final installed candidate**
  before first-release acceptance. Repeat common-file configuration, keys,
  Activity, reasoning, commands, Quit, resizing and guide instructions there.
- Final UAT includes a controlled real provider and executing tool, in
  addition to deterministic fake-provider coverage. The provider/model,
  environment, tool and permitted effects must be selected and recorded
  **before** final UAT. If that provider does not expose reasoning text,
  record that limitation; deterministic provider tests still prove shown-text
  behavior. No credential values belong in planning evidence.
- The dedicated user [TUI guide](user-guide-requirements.md) and the
  `docs/guides/10-configuration.md` TUI reference grow alongside visible
  units. Users follow their first-launch, file-choice, command, Activity and
  Quit instructions on the final installed candidate. Guide defects block
  acceptance just like UI defects.
- Final technical validation, actual user UAT, maintainer acceptance and
  external delivery are separate gates. No old 24-unit or five-checkpoint
  receipt proves this replacement plan was executed.

## 5. Current construction gate and remaining design work

The [TUI-N00 source review](n00-integration-review.md) reconciles all 50
command cases and records the original Chat/`friday-cli` baseline. TUI-N01S
was independently [VERIFIED](validation/VAL-N01S-session-identity.md) for its
identity-only candidate. N01A's neutral configuration loader was separately
[VERIFIED under the maintainer's unit-specific Linux-smoke deferral](validation/VAL-N01A-waiver-closeout.md).
The subsequent [CI03 exact-source Ubuntu run](validation/TUI-CI03-ubuntu-run-39183895627.md)
and [independent review](validation/VAL-TUI-CI03-final-676700f5.md) reconciled
the CI01/CI02 automated Linux gates. They preceded N01B-01 and are not its
exact-source Linux result or TUI terminal UAT.

1. The first [N01B-01 review](validation/VAL-N01B-01-preflight-7e5241c8.md)
   requested two documentation/evidence corrections under the bounded
   [remediation directive](remediation/REM-TUI-N01B-01-01.md). A fresh
   [independent review VERIFIED the corrected pre-push candidate](validation/VAL-N01B-01-final-closeout-35e297e8.md)
   against the [approved exact directive](directives/CD-TUI-N01B-01-neutral-transcript-query-contracts.md).
   Chuck Russell authorized the branch push; the [exact-source Ubuntu
   run](validation/N01B-01-ubuntu-run-39190668231.md) succeeded and was
   [independently reconciled](validation/VAL-N01B-01-postrun-4febb6f6.md).
   The next product unit needs a separate exact directive and maintainer
   approval. Installed macOS/Linux terminal UAT remains a release gate.
2. Choose owners for command/event seams. Review the
   [event/lifecycle proposal](neutral-event-lifecycle-contract.md) and bind
   event admission, argument snapshot and resource-close boundaries against
   actual native/MCP/provider paths in their later directives.
3. Bind the exact read-only chooser key signature and remaining startup replay
   error/cleanup behavior, the accepted
   `Enter`/`Ctrl+Enter` editor actions and terminal fallback, remaining key
   defaults, Activity per-entry/total limits, accepted `/cls` and selected-text
   copy behavior, overflow behavior and Force quit's confirmed emergency
   mechanism to testable UI contracts.
4. Prepare separate exact directives for later bounded units; recheck board,
   branch, source and authority before each product-code unit.

The board remains `started` with `granted` authority only for the exact
N01B-01 subunit. Its first candidate `7e5241c8` received
`CHANGES_REQUESTED` for packet documentation and command evidence; corrected
candidate `35e297e8` is independently `VERIFIED` for pre-push readiness.
Product source is frozen. The pushed source `62d3ae3b` passed the Ubuntu
workflow and post-run independent reconciliation. N01A is closed,
while later N01B effects and all subsequent product units remain design-only.
No TUI, terminal UAT or real-provider test has run.
