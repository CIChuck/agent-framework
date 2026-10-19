# Friday TUI neutral-capability map

**Status:** Source-backed planning inventory; proposed seams require review and
separate construction directives. **Authority:** `design_only`.

**Baseline:** `c34269867be50f71923c93c95a63236a35505812`. The
[command matrix](command-matrix.md) supplies exact names, aliases and usage;
this document maps effects and service ownership. It does not assert that the
TUI exists or that the proposed neutral APIs already provide parity.

## Boundary found in the current source

`friday_chat.commands.registry.build_default_registry()` registers 50 slash
commands, but its `CommandContext`, handlers, runtime bundle and several
effect services live in `friday-chat`. In particular,
`friday_chat.config.load_friday_py_config()` now delegates the established YAML
shape, diagnostics, interpolation and model-library binding to the verified
`friday_runtime.application_config` neutral loader;
`friday_chat.runtime.build_runtime()` assembles Chat's fake or real services.
`friday_runtime.kernel.RuntimeKernel` is headless, but its `RuntimeConfig` and
assembly path are distinct and do not currently demonstrate the same Chat
file, tool, maintenance, transcript or command behavior. Substituting the
kernel alone is therefore not a parity contract. Chat's presentation loader
in `friday_chat.display` imports `friday_cli`, so the TUI must read its own
`tui:` settings from the common file without importing that loader.

The proposed neutral service home is `friday-runtime` where it can depend on
existing framework packages without depending on `friday-chat` or
`friday-cli`. Keep Chat command parsing, formatting, registry, terminal
display and `FridaySession` in Chat; the TUI owns corresponding handlers,
registry, view state and results. Move only reusable typed effects and
contracts after a focused comparison proves them. Public names and ownership
below are proposals, not approved API signatures.

| Seam | Current source of behavior | Proposed neutral contract and evidence |
| --- | --- | --- |
| S: session/turn state | `friday_chat.session`; `app.py` and `turns/processor.py` | Shared invocation identity and typed turn-state snapshots; independent frontend session/history views. Start with identity only. Compare identity propagation and unchanged Chat startup. |
| C: configuration/assembly | `friday_chat.config`, `runtime.py`, `adapters.py`; existing `friday_runtime.config` and `model_library.py` | Separate a [shared Chat-compatible loader and facade](neutral-config-loader-contract.md) from later neutral service assembly. Preserve established YAML, environment, captured working directory, model/service/storage choices, diagnostics, fake/real behavior and close ownership; do not silently translate into `RuntimeConfig`. |
| D: diagnostics/memory | `friday_chat.memory_views`, `commands/memory.py` and Chat runtime memory adapter over `friday-memory` | Typed diagnostic/record queries and session/turn metrics, retaining unavailable versus zero and bounded results. TUI formats its own display. |
| M: maintenance | `commands/registry.py`, `reorganization/`, `background.py`, `adapters.py` over `friday-memory`/`friday-transcript` | Typed admission, dry-run/execute, progress, recovery and reset effects, with the same persistence layout and safe shutdown boundaries. Split by operation; reorganization is not a small extraction. |
| F: file/replay | `commands/files.py`, `replay.py`; configured `friday_tools.filesystem.smart_read.SmartFileReadTool` | Typed file read/ingest and replay operations with the same path, line-limit, CSV, reset and delay semantics; TUI controls presentation. The first-release sidebar file browser is new TUI presentation work. Deliberate selection immediately initiates attachment for the next eligible model turn through a new neutral contract, not an existing Chat command effect (D-77). |
| T: tools/security | `tools/`, `security.py` and tool handlers; underlying `friday-tools`/MCP packages | Typed registry, selection/budget, manual invocation and sanitizer results. Preserve current manual-call output, tool policy and exact executed arguments; event admission is a separate contract. |
| P: speech/orchestration/workflow | `speech.py`, Chat runtime orchestrator and `FrameworkWorkflowAdapter` | Typed optional-service operations and state. Verify actual fake/real availability before promising a richer backend. |
| X: transcripts/exports | `transcripts.py`, transcript handlers and `FrameworkTranscriptAdapter` over `friday-transcript` | Typed queries, session identity, export file effects/limits and errors. TUI need not reuse CLI prose; exported contents and persistence semantics must match. Verified N01B-01 moved only the three read-only query views and their protocol. Independently verified N01B-02 moved the four persisted read methods into a neutral adapter while Chat delegates. N01B-03 moved only pure export content serialization into Runtime. [N01B-04](validation/VAL-N01B-04-postrun-27c84ad9.md) moved only root creation and safe-path resolution; all four units are independently VERIFIED locally and on exact-source Ubuntu. Chat retains transcript writes and command policy. Its public export-root helper also serves `/context --file` and `/prompt --file`. [N01B-05](validation/VAL-N01B-05-postrun-3d5695d8.md) moved only current-session and prompt-log single-file write effects while preserving Chat path hooks and result identity; its local and exact-source Ubuntu gates are independently VERIFIED. [N01B-06](validation/VAL-N01B-06-postrun-3413c25f.md) moved all-session directory and two-file write effects into Runtime while preserving Chat's path hooks, output and result identity; its local and exact-source Ubuntu gates are independently VERIFIED. TUI UAT remains open. |

[N01B-07](validation/VAL-N01B-07-postrun-4fc8309d.md) subsequently moved
only pure MCP provenance preflight and tool-call/result record preparation
into Runtime; Chat still owns transcript append, optional context-log write,
session/turn state and receipt checks. The [approved N01B-08
directive](directives/CD-TUI-N01B-08-neutral-transcript-write-effects.md)
would move only append/context-log effects after the [before-code failure
characterization](validation/N01B-08-before-code-transcript-write-characterization.md).
Its four local source/test paths are approved; independent review remains
open.

Source check for selected-file context: Chat's `/read` formats file content as
command output; `/ingest` writes content to vector memory. `/context` shows or
exports an assembled context, and `/run-tool file_read` runs a configured tool
and returns its result as command output. The configured smart-file tool's
`add_to_context` parameter controls whether its content appears in that tool
result, which the model can see during a model-driven tool loop. It does not
register a selected file for later prompts. Chat's normal turn preparation
accepts a user message and retrieved memories, with no selected-file input.
The Chat `/read` helper lists PDF, DOCX and XLSX extensions but returns a
placeholder string for their contents; the configured smart-file tool skips
binary extensions. Neither is evidence of actual PDF/Office text extraction
for a TUI attachment. D-82 requires real first-release extraction for these
three formats alongside readable text/code/data. `friday-tools` already has
`ReaderFactory`, `PdfReader`, `DocxReader` and `XlsxReader`, with optional
`documents` and `spreadsheets` dependencies. The PDF reader extracts embedded
text via pypdf; DOCX reads paragraphs and tables; XLSX reads the active sheet
by default with openpyxl and accepts explicit sheet name/index selection.
D-89 requires TUI attachment to enumerate and combine every worksheet,
including hidden sheets, in workbook order with sheet-name labels; the
existing default call alone would silently omit non-active sheets. D-90
requires atomic workbook attachment: a failed worksheet read names the sheet,
rejects the whole new workbook and leaves a prior complete snapshot intact
on failed refresh. The reader opens XLSX with `data_only=True`, so formula
expressions are absent from its current output; D-91 requires the TUI-neutral
path to provide both formulas and workbook-saved results when present, with
no invented calculation or Chat/CLI behavior change. Seven focused existing
reader tests pass, but the PDF test uses a malformed file and does not prove
positive PDF extraction or TUI attachment. N01E must prove actual content with
genuine fixtures and package
the dependencies for the installed TUI without changing Chat `/read`.
Therefore immediate attachment on deliberate sidebar file selection needs a
new UI-neutral file/context contract and tests; it must not import Chat/CLI
handlers or quietly substitute memory ingestion. Under D-78, the attachment
continues into later accepted turns until explicit removal; removal changes
only future turns. Under D-79, attachment state is discarded on exit and a
fresh launch starts empty regardless of transcript availability. Additional-file
selection accumulates distinct attachments under D-80; each can be removed
independently. D-81 freezes each file's content at selection, with deliberate
same-file reselection refreshing the existing attachment in place; failed
refresh retains the last good snapshot. D-83 adds Tesseract OCR for scanned
PDFs through a separate rendering/OCR step; the existing pypdf reader cannot
provide that text. A cross-platform PDF page renderer and Tesseract invocation
need a neutral, independently testable contract and install checks. The local
Mac has a Tesseract executable, but that does not establish installed macOS
or Linux support; no PDF renderer or OCR attachment path is present in this
repository. D-84 routes mixed PDFs page by page: embedded text when usable,
Tesseract only when absent, with original page order and no duplicated page
text. D-85 requires the user to install Tesseract separately on macOS/Linux;
the TUI must discover it when OCR is needed and report an actionable
missing-tool failure without blocking text-only reading. D-86 rejects the
whole PDF attachment when any required OCR page fails, with a page-specific
error and no partial model input; failed refresh retains the last complete
snapshot. D-87 selects English by default or one or more installed Tesseract
language packs through a TUI-only setting in the shared presentation file;
missing requested packs fail the OCR attachment without fallback. The
PDF page renderer is an installed `friday-tui` dependency under D-88, so
users install Tesseract and language packs separately but not a renderer.
The exact renderer, its license/platform/native dependency behavior and
installed-package closure require proof. The usable-text criterion,
language-code validation bounds, exact estimator and numeric per-file and
aggregate thresholds, raw-file/processing safeguards and runtime context
headroom remain open. D-92 rejects an over-limit whole-file attachment
rather than supplying a partial excerpt. Existing readers can report
`truncated`, and the XLSX
reader defaults to 1,000 data rows; N01E must reject incomplete output or
obtain complete content within the bound, with no Chat/CLI behavior change.
D-93 rejects a proposed attachment or refresh when the combined active file
snapshots would exceed their budget, retaining existing snapshots and allowing
manual removal/retry; the exact estimator and runtime context reservation
are still contract work. D-94 places optional typed per-file
and combined limit settings with defaults under the shared presentation
file's `tui.attachments` namespace; a neutral TUI reader must validate them
without changing the CLI loader or Friday runtime configuration. D-95
expresses both bounds in estimated tokens of the complete formatted text
supplied to the model, including labels and OCR/formula content. D-96 keeps
omitted limit defaults fixed across models and providers, regardless of known
or unknown context-window metadata. D-97 fixes them at 4,000 estimated tokens
per file and 8,000 combined; a passed attachment still may not fit a later
model turn, especially with an 8,192-token context window. D-98/D-99 require
a UI-neutral check of every fully assembled conversational provider request
after normal Friday context selection. An overage may recover through one
eligible older-turn compaction attempt; otherwise the blocked request must
not be sent. An initial failure retains the draft and attachments without a
new turn; a later failure leaves the current turn incomplete with recorded
tool activity and effects intact. Current `PromptArchitect` stores a budget
status and warns on overage but does not itself reject the request; N01G must
bind an enforceable admission seam without changing Chat/CLI.
`friday-memory` has `InSessionCompactor`, which summarizes eligible older
persisted turns and may call a configured model and update durable memory.
The current Chat `/compact` handler provides frontend orchestration, not an
importable TUI contract. N01H must expose a UI-neutral request with typed
eligibility, status and effect reporting that honors runtime configuration;
the TUI must reassemble and re-estimate the pending conversational request
afterward. Existing compaction cannot shrink current-loop tool output or
active attachment snapshots. Manual `/compact` command parity remains a
separate TUI command slice.
`friday-memory` has a UI-neutral approximate token estimator and an optional
tiktoken-based estimator; the exact estimator, safety margin and context
reservation remain to be bound, without a Chat/CLI import.
After a passing estimate, the provider can still reject a request for context
length. D-100 requires a distinct post-send error outcome: the TUI reports it
and leaves correction/retry to the user while preserving the submitted initial
draft and attachments or marking a later turn incomplete with prior tool work
intact. N01I needs a UI-neutral classification and recovery contract. Current
`friday-llm` telemetry classifies `litellm.BadRequestError` broadly as
`invalid_request`; that category alone does not prove context-length rejection.
Do not infer that the provider was never called or change the LLM transport's
existing retry policy or either CLI frontend's behavior.
D-101 places the initial failed prompt back in an empty editor or exposes a
TUI-owned Restore action when a newer draft exists. That draft-state decision
does not belong in the neutral provider service; it consumes N01I's failed
request identity and preserved submitted text without importing Chat/CLI UI.
D-104 keeps that TUI-owned action beside the editor if the bounded conversation
evicts the error notice; this placement and focus behavior need no additional
neutral runtime service or persistent transcript record.
D-105 applies the same TUI-owned recovery after `/cls` or `/clearscreen` clears
the view. Display clearing does not ask the neutral service to resubmit the
failed request or persist the failed attempt.
D-106 clears the old TUI-owned recovery only when a different conversational
turn reaches its successful completion outcome. Admission, partial output,
commands and failed outcomes do not clear it. Remove Restore controls from
the editor and any retained error notice; a retained notice becomes
non-actionable current-run display. This uses the UI's completed-turn outcome,
not a new Chat/CLI dependency or a change to neutral transcript persistence.
D-107 lets the TUI keep distinct failed-request identities and preserved text
in its current-run recovery state, presenting one editor-adjacent control and
a newest-first chooser when more than one is pending. Opening or browsing the
chooser is UI-only; retained notices have no separate Restore controls in this
state. Selection uses D-41/D-101 editor protection and makes no
new provider request. No pending failed prompt becomes a transcript record.
D-108 keeps the chosen failed-request snapshot in TUI-owned pending recovery
after Confirm fills the editor; the editor copy may change without mutating
that snapshot or creating a duplicate pending entry. A later successful
conversational completion clears all earlier pending recoveries through the
same UI-owned outcome handling as D-106. Restore and repeated Restore make no
neutral provider or transcript call.
D-109 adds confirmed per-prompt Dismiss within that TUI-owned recovery state.
It removes only the selected pending snapshot and updates the visible count;
the editor copy, attachments and neutral Friday state remain unchanged. Cancel
does not remove it. No new neutral provider, persistence or Chat/CLI contract
is needed for this UI action. The construction directive must bind a finite
count/size limit and deterministic overflow behavior for recovery snapshots.
D-102 excludes a failed initial request from persisted transcripts while
retaining in-process recovery. N01J must prove the neutral transcript write
occurs only for a completed corrected turn; a provider call or telemetry record
must not be mistaken for a saved conversation turn. Existing Chat turn
persistence is on its successful processor path; its behavior is a comparison
baseline, not a TUI dependency. D-103 governs later post-tool failure
persistence: N01K leaves the transcript unchanged on either a local
overage after eligible compaction or a provider context-length rejection.
The already executed tool effect remains real, while its TUI Activity is
bounded, in-process display state under D-23. Neither a provider call nor a
compaction memory write is an incomplete-turn transcript record.

## Per-command effect map

`UI` means the TUI can own the interaction over its own state; a row naming
another seam also requires that runtime effect. The named Chat handler is a
source reference only. Each proposed seam must have its own typed result,
failure and state tests before a TUI handler claims parity. The unchanged
Chat tests listed below are candidate comparison fixtures, not TUI proof.

| Case | Command | Current effect and proposed dependency |
| --- | --- | --- |
| PAR-001 | `/agent` | Describe an agent through Chat's orchestrator; P. |
| PAR-002 | `/agents` | List agents, active marker and cache state; P. |
| PAR-003 | `/clear` | Clear in-process history **and** runtime session memory; UI + D. Distinct from `/cls`. |
| PAR-004 | `/clear-tools` | Restore automatic tool selection; T. |
| PAR-005 | `/cls` | Clear only the displayed conversation/pin/Activity; UI. `/clearscreen` shares this case. |
| PAR-006 | `/compact` | Flush pending extraction, then compact with guards/results; M. |
| PAR-007 | `/context` | Show last/current context, optional debug/file export; S + C + X/file effect. |
| PAR-008 | `/debug` | Show last-turn debug and execution telemetry; S + D. |
| PAR-009 | `/debug-budget` | Show configured context/output token limits; C. |
| PAR-010 | `/debug-retrieval` | Query retrieval diagnostics; D. |
| PAR-011 | `/delegate` | Route a task to another agent and restore prior active agent; P. |
| PAR-012 | `/entities` | Query graph entities/relationships with display bounds; D. |
| PAR-013 | `/exit` | Request normal shutdown; UI + resource-close/lifecycle contract. `/quit` and `/q` share the case. |
| PAR-014 | `/export` | Export current persisted session in selected format; X. |
| PAR-015 | `/export-prompts` | Export captured raw context logs for a session; X. |
| PAR-016 | `/help` | Render own registry metadata and alias details; UI, with drift check against the Chat inventory. |
| PAR-017 | `/history` | Show current in-process user/answer pairs; UI + S. |
| PAR-018 | `/ingest` | Read a supported file and add chunks to memory; F + D. |
| PAR-019 | `/inject-payload` | Set a one-use payload applied to the next manual tool result; UI + T. |
| PAR-020 | `/inject-tools` | Atomically select an exact manual tool set under schema budget; T. |
| PAR-021 | `/insights` | Query typed active insight records; D. |
| PAR-022 | `/lifecycle` | Stats/flush/optimize/cycle, dry-run default and guards; M. |
| PAR-023 | `/list-ingested` | Show memory ingestion records; D. |
| PAR-024 | `/memory` | Combine memory, transcript and last-turn statistics; D + S + X. |
| PAR-025 | `/meta` | Query typed meta-insight records without synthesis; D. |
| PAR-026 | `/migrate` | Preview/execute storage migration with persistence guard; M. |
| PAR-027 | `/prime` | Show configured priming state; C + D. |
| PAR-028 | `/prompt` | Show last/current assembled prompt, optional file export; S + C + X/file effect. |
| PAR-029 | `/read` | Read a supported file with `--lines` rules; F. |
| PAR-030 | `/recommend-tools` | Rank available tool names/descriptions for a query; T. |
| PAR-031 | `/reorganize` | Preview/execute/recover with durable journal, admission and progress; M. |
| PAR-032 | `/replay` | Parse CSV, reset as specified and process ordered turns; F + S + M. |
| PAR-033 | `/reset` | Reset chosen/all memory stores; full reset also archives transcripts and clears state; M + D + S + X. |
| PAR-034 | `/run-tool` | Validate and invoke a tool, sanitize/truncate the inline result and update lifecycle state; T. Also emit TUI Activity from actual invocation events. |
| PAR-035 | `/security` | Show policy and local scan counters; C + T. |
| PAR-036 | `/security-config` | Validate and change in-process sanitization settings with rollback; T + C. |
| PAR-037 | `/security-test` | Run local sample scans and update counters; T. |
| PAR-038 | `/sessions` | List persisted/current/primed transcript sessions; X + S. No active transcript-session switch. |
| PAR-039 | `/set` | Set a scoped in-process variable; UI + S. |
| PAR-040 | `/speech` | Inspect/change in-process speech settings and system-prompt snippet; P + C. |
| PAR-041 | `/speech-test` | Speak the test phrase when enabled; P. |
| PAR-042 | `/status` | Show orchestrator active agent/cache/message count; P. |
| PAR-043 | `/summaries` | Query typed active summary records; D. |
| PAR-044 | `/switch` | Change or show the active **agent**; P. |
| PAR-045 | `/timing` | Show last-turn timings and execution telemetry; S + D. |
| PAR-046 | `/tool-budget` | Show current selection, estimates, last execution and rejection state; T. |
| PAR-047 | `/tools` | List/filter registered tools and parameter names; T. |
| PAR-048 | `/transcript` | Inspect persisted session or export all non-archived sessions; X. |
| PAR-049 | `/vars` | List scoped in-process variables; UI + S. |
| PAR-050 | `/workflow` | List/run/status/approve/skip through workflow engine; P. |

## Routes outside the slash registry

- `@agent_name <message>` routes through the orchestrator (P); unknown agents
  and active-agent state need parity fixtures.
- `!<command>` is disabled by default. Its opt-in execution, timeout,
  subprocess output and working-directory behavior currently live in
  `friday_chat.shell`. A neutral shell service is needed for first-release
  route parity; disabled and enabled states both need tests.
- Startup `--version`, `--replay`/`--replay-delay`, `--config`,
  `--cli-config` and `--runtime` are currently dispatched in
  `friday_chat.cli`. The TUI launcher owns equivalent precedence, errors and
  help independently. The no-`--config` existing-file chooser is a TUI
  addition; its initial list comes from the launch working directory, with
  browsing elsewhere, and an explicit path bypasses the list (D-48). The
  initial list includes likely Chat runtime YAML with custom names but
  excludes recognized model-library/display YAML (D-49); listing alone
  does not resolve credentials or start services. A chooser-selected invalid
  file leaves the chooser open with an actionable error and Retry, Browse and
  Quit (D-50). An invalid explicit `--config` reports the error and exits
  nonzero without a chooser or runtime start (D-51); real-provider startup
  failure is separate. An empty launch-folder list stays in the chooser with
  a clear message, Browse and Quit (D-52). A real startup failure after
  chooser selection cleans up partial services, reports the error and returns
  to the chooser with Retry, Browse and Quit when cleanup succeeds (D-53).
  When cleanup itself fails, report
  both failures, restore the terminal as far as possible and exit nonzero
  without in-process retry (D-56). The same failure after explicit
  `--config` instead cleans up, reports the error and exits nonzero without
  a chooser; cleanup failure is also reported (D-54).
  Initial chooser candidate detection is a shallow, read-only inspection of
  top-level YAML structure, independent of basename, with recognized model
  library/presentation files excluded and unrecognized files still available
  through Browse (D-55). An incomplete but recognizable `llm:` file is listed
  and validated on selection (D-57). Browse supports folder navigation and
  typed/pasted absolute, relative and `~` home paths to existing files; relative
  entry resolves from the displayed folder, and missing/invalid selections
  follow chooser recovery (D-58). A visible keyboard-focusable Refresh action
  rescans launch-folder candidates on demand, including an empty-list recovery;
  there is no automatic file watching or runtime start on Refresh (D-59).
  A direct-child YAML link to a readable regular runtime file is a candidate
  even when its target is outside the launch folder. Broken, cyclic, unreadable,
  directory-target and unrelated links are Browse-only, with D-50 error
  recovery; no directory recursion occurs (D-60).
  Exact keys are a bootstrap-contract detail.
  Unlike Chat's current fake default, the TUI uses `real` for
  configured interactive startup unless `--runtime fake` is explicit (D-47);
  real startup failure never silently changes the mode. Version and startup
  replay precedence are unaffected by this default.
  `friday_chat.display.resolve_display_config()` cannot be imported
  because it uses `friday-cli`; the TUI reads only its own additive namespace
  from the same selected presentation file.
- Provider reasoning and tool lifecycle events currently pass through Chat's
  turn processor, tool loop and adapters. A neutral typed stream must be
  mapped to the actual model request and native/MCP invocation boundaries;
  Chat telemetry or formatted output cannot substitute for it.

The event seam has three concrete source constraints. In
`friday_chat.adapters.FrameworkChatModel.complete()`, a non-stream response
contains `reasoning_content`, but its `stream_complete()` discards
`ReasoningDeltaEvent` while yielding only text. In
`friday_chat.tools.loop.ToolLoop.run()`, an unknown or unselected requested
tool can be rejected before invocation, while a permitted call goes through
`call_tool_record()` or `call_tool()`. For MCP calls,
`friday_chat.tools.output.MCPOutputPolicy` returns retained
`ToolCallRecord` objects with empty `arguments` even though the callable
received the original arguments. A user-entered `/run-tool` invokes the
registry through its own handler and bypasses `ToolLoop`. Thus reasoning
must be captured before the text-only streaming adapter drops it; a
`Not run` event belongs at the actual rejected-request boundary; and
executed argument snapshots plus start/terminal events belong at the
native/MCP invocation boundary shared with manual calls, before retained
MCP records omit arguments. The exact hook and normalization point still
need an event directive and tests. Neither this map nor current telemetry
proves the required typed event stream exists.

## Smallest proposed first extraction and test gate

Start with **TUI-N01S: neutral session identity** before the larger config
and assembly units. Move only `SessionIdentity`,
`SessionIdentityMismatchError` and `resolve_session_identity()` from
`packages/friday-chat/src/friday_chat/session.py` into a new public
`packages/friday-runtime/src/friday_runtime/session_identity.py`. Re-export
those same objects from `friday_chat.session` so existing Chat imports retain
identity and exceptions. Leave `FridaySession` and all Chat command/UI code in
Chat. No `friday-cli` file changes. This proposal is narrow because the
primitive has no provider, storage, terminal or configuration dependency and
its identity is already used by Chat runtime, app, replay and transcript
adapters. It does **not** by itself make Chat runtime assembly neutral.

An exact directive should limit edits to those two source modules and a new
`packages/friday-runtime/tests_runtime/test_session_identity.py`. The public
neutral import path is the module named above; no package-root export is
required for this slice. Use
`packages/friday-chat/tests_chat/test_session_identity.py` and
`test_transcript_production_commands.py` as unchanged comparison tests;
also run Chat startup/command tests and the established `friday-cli` baseline.
Prove generated/injected identities, mismatches, import identity, transcript
propagation, and package import closure. Record the baseline before code and
reject changed CLI behavior or a new runtime-to-Chat/CLI dependency. The
directive and code authority were approved for TUI-N01S on 2026-10-18. Later
units remain design-only.

After that, use the [draft loader contract](neutral-config-loader-contract.md)
to bound TUI-N01A typed file loading/model binding, keep resource/effect
primitives in TUI-N01B and assembly in TUI-N01C, then split D/M/F/T/P/X by
effects actually needed. Exact future
source/test allowlists and typed API signatures require review against each
family's existing fixtures. At each slice, run focused neutral tests plus
unchanged Chat and `friday-cli` comparisons; only then add independent TUI
handlers and interaction/UAT evidence. Current candidates include
`tests_chat/compat/test_config_compatibility.py`, `test_runtime.py`,
`test_memory_diagnostics_commands.py`, `test_maintenance_commands.py`,
`test_files_replay_shell.py`, `test_tool_commands.py`,
`test_security_speech.py`, `test_orchestration_workflow.py` and
`test_transcript_production_commands.py`. No test in that list verifies a
future TUI until the TUI executes its own handler against equivalent fixtures.
