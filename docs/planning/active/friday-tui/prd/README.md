# Friday TUI product requirements

**Status:** Proposed vision-traceable PRD for maintainer review. The accepted
decision register and existing detailed acceptance cases remain in force until
this reconciliation is accepted. This document grants no construction, delivery,
or release authority.

**Date:** 2026-10-19

**Source authority:** Chuck Russell's TUI requirements and live runtime-control
instruction; [Friday TUI vision](../vision/README.md); [accepted decision
register](../decisions.md); the [current detailed requirements and AC-01–AC-34](../README.md);
[command matrix](../command-handoff.md#command-matrix); [shared command architecture](../command-handoff.md#shared-command-architecture);
[screen proposal](../screen-layout.md);
[presentation configuration](../ux-configuration.md); [Activity](../tool-activity-requirement.md),
[reasoning](../reasoning-display-requirement.md), and [user-guide](../user-guide-requirements.md)
requirements. The [replacement plan](../replacement-plan.md) supplies context but
does not add product scope. Withdrawn plans and historical technical proposals
are not product authority.

## Product objective and users

Deliver an independently installed terminal application in which a person can
start Friday with an existing runtime configuration, converse, use the maintained
`/` command surface, change the active conversational model between turns, add file
context, understand agent/tool activity, recover from errors, and quit safely.
Existing Friday Chat and `friday-cli` behavior must remain intact. The product
serves terminal users and the operators who configure and supervise their
Friday sessions. The initial use case is one person in a local macOS or Linux
terminal; a multi-user service is not assumed.

## Product context and scope rule

The current installed TUI is a no-backend shell. It cannot yet start Friday,
answer a prompt, or run `/` commands. A connected conversation is the next
user-visible milestone; it is not the whole first release. The first release
retains all accepted requirements that trace to the vision, including command
parity, Activity, reasoning visibility, file context, live model
selection, startup replay, documentation, and UAT. Here **first full release**
means the complete accepted baseline; labeled preview alphas may ship tested
subsets under a separate phase plan and cannot claim full-release acceptance.
Older source references to "first release" mean this first full release. Each
baseline requirement below cites at
least one stable [vision outcome](../vision/README.md#desired-outcomes). A source
request without a direct product-outcome link appears in **Out-of-bounds scope
review** rather than being given a token vision citation.

The existing [decision register](../decisions.md) and detailed [AC cases](../README.md#8-acceptance-and-verification)
retain their exact edge conditions where mapped below. This PRD groups them by
user outcome and uses EARS acceptance language. It does not quietly weaken an
accepted behavior. An `open` status means the product intent is in scope but
specified behavior still needs a maintainer decision before architecture or a
construction directive can implement it.

## Requirements table

All rows are first-full-release P0 unless marked otherwise. `FR` denotes a
functional requirement; `NFR` denotes a non-functional or release requirement.
The vision column is an outcome link, not a claim that the feature already
exists. Every row has its statement, EARS acceptance criteria, and testability
notes in the sections that follow.

| ID | Short name | Vision outcome(s) | Phase | Status | Source cases |
| --- | --- | --- | --- | --- | --- |
| FR-01 | Start and choose configuration | [V-01](../vision/README.md#v-01), [V-06](../vision/README.md#v-06) | First release | baseline | D-13, D-47–D-60; AC-06 |
| FR-02 | Runtime configuration continuity | [V-07](../vision/README.md#v-07) | First release | baseline | D-06, D-61; AC-14 |
| FR-03 | Active conversational-model selection | [V-03](../vision/README.md#v-03), [V-06](../vision/README.md#v-06) | First full release | baseline | D-110–D-114, D-121; AC-35 |
| FR-04 | Presentation preferences | [V-01](../vision/README.md#v-01), [V-07](../vision/README.md#v-07) | First release | baseline | D-07, D-15; UXCFG-01–UXCFG-08; AC-15 |
| FR-05 | Conversation and response | [V-01](../vision/README.md#v-01), [V-06](../vision/README.md#v-06) | First release | baseline | D-122; AC-04, AC-36; screen proposal |
| FR-06 | Multiline editor | [V-01](../vision/README.md#v-01), [V-06](../vision/README.md#v-06) | First release | baseline | Q-02, D-38–D-39; AC-07 |
| FR-07 | Conversation navigation | [V-01](../vision/README.md#v-01), [V-06](../vision/README.md#v-06) | First release | baseline | D-16–D-17, D-33, D-36–D-37; AC-03, AC-07 |
| FR-08 | Maintained command parity | [V-02](../vision/README.md#v-02), [V-07](../vision/README.md#v-07) | First release | baseline | D-01, D-09–D-12, D-22, D-25, D-27, D-123; AC-01–AC-03 |
| FR-09 | Command discovery and growth | [V-02](../vision/README.md#v-02), [V-06](../vision/README.md#v-06) | First release | baseline | D-03, D-40–D-41, D-66–D-70, D-123; AC-11–AC-12 |
| FR-10 | Sessions and transcripts | [V-01](../vision/README.md#v-01), [V-02](../vision/README.md#v-02) | First release | baseline | D-33–D-34, D-122; AC-03, AC-36 |
| FR-11 | In-run editor recall | [V-06](../vision/README.md#v-06) | First release | baseline | D-71–D-75; AC-07 |
| FR-12 | Tool and agent Activity | [V-04](../vision/README.md#v-04) | First release | baseline | D-19–D-23, D-25, D-27, D-29–D-32, D-35, D-42–D-46; AC-18 |
| FR-13 | Provider reasoning view | [V-04](../vision/README.md#v-04) | First release | baseline | D-18, D-20, D-24, D-35; AC-17 |
| FR-14 | File selection and lifecycle | [V-05](../vision/README.md#v-05) | First release | baseline | D-76–D-81; AC-19–AC-20 |
| FR-15 | Real file-content extraction | [V-05](../vision/README.md#v-05) | First release | baseline | D-82, D-89–D-91; AC-21 |
| FR-16 | Scanned-PDF OCR | [V-05](../vision/README.md#v-05) | First release | baseline | D-83–D-88; AC-22 |
| FR-17 | Attachment admission limits | [V-05](../vision/README.md#v-05), [V-06](../vision/README.md#v-06) | First release | baseline | D-92–D-97; AC-21–AC-22 |
| FR-18 | Complete-request budget and compaction | [V-05](../vision/README.md#v-05), [V-06](../vision/README.md#v-06) | First release | baseline | D-98–D-99; AC-23–AC-24 |
| FR-19 | Provider context-length failure | [V-06](../vision/README.md#v-06) | First release | baseline | D-100–D-103; AC-25, AC-27–AC-28 |
| FR-20 | Failed-prompt recovery | [V-06](../vision/README.md#v-06) | First release | baseline | D-101–D-102, D-104–D-109, D-122; AC-26, AC-29–AC-34, AC-36 |
| FR-21 | Safe exit and cleanup | [V-06](../vision/README.md#v-06) | First release | baseline | Q-03, D-09, D-28; AC-05 |
| FR-22 | Startup replay | [V-09](../vision/README.md#v-09), [V-06](../vision/README.md#v-06) | First full release | baseline | D-62–D-65, D-116; AC-06, AC-14 |
| FR-23 | General provider/runtime failure recovery | [V-06](../vision/README.md#v-06) | First release | baseline | D-122; AC-36 |
| NFR-01 | Independent package and CLI preservation | [V-07](../vision/README.md#v-07) | First release | baseline | D-02, D-08, D-22, D-123; AC-08–AC-10 |
| NFR-02 | Terminal usability and accessibility | [V-06](../vision/README.md#v-06), [V-08](../vision/README.md#v-08) | First release | baseline | Q-01, D-11, D-16, D-36, D-39, D-119; AC-07 |
| NFR-03 | Security and data boundaries | [V-06](../vision/README.md#v-06), [V-07](../vision/README.md#v-07) | First release | baseline | D-20–D-23, D-31–D-35, D-121–D-122; UXCFG-06 |
| NFR-04 | User guide and configuration reference | [V-08](../vision/README.md#v-08) | First release | baseline | D-14–D-15; AC-16; guide requirements |
| NFR-05 | Incremental verification and UAT | [V-08](../vision/README.md#v-08) | First full release | baseline | D-05, D-11, D-26, D-118–D-120; AC-08, AC-13 |

## Functional requirements

### FR-01 — Start and choose an existing runtime configuration

**Requirement:** The installed TUI shall make existing Friday runtime
configuration selectable without inventing a new runtime file or silently
changing runtime mode. **Priority/phase:** P0, first release. **Status:**
baseline. **Vision:** V-01, V-06.

**Acceptance criteria (EARS):**

- When `--config` is omitted, the TUI shall offer a chooser that lists likely
  runtime YAML files from the captured launch directory and lets the user
  Refresh or Browse to an existing file elsewhere; listing and refresh shall
  not start Friday services.
- When the user provides `--config`, the TUI shall bypass the chooser. When a
  valid configuration is selected, it shall start real Friday unless the user
  explicitly selects fake mode; the Chat-specific `FRIDAY_CHAT_RUNTIME` value
  shall not select the TUI mode.
- If a chooser selection is invalid, then the chooser shall remain available
  with an actionable error, Retry, Browse, and Quit. If an explicit path is
  invalid, then the TUI shall report the error and exit nonzero without a
  chooser. Startup failure shall clean up partial resources and follow the
  distinct chooser/explicit-path outcomes in D-53–D-56.
- When discovering candidates, the TUI shall use shallow, read-only YAML
  inspection to include recognizable custom-named runtime files and readable
  direct-child links while excluding recognized model-library and presentation
  files; Browse shall accept folder navigation and typed paths, including
  absolute, relative, and `~` paths. The empty-list, Refresh, incomplete-file,
  and invalid-link cases remain as specified in D-48–D-60.

**Testability:** Use disposable launch folders and runtime files for valid,
invalid, empty, symlink, custom-name, and partial-start cases; verify installed
chooser interaction, no premature service start, diagnostics, cleanup, and exit
status on macOS/Linux. AC-06 and D-47–D-61 retain the detailed case matrix.

### FR-02 — Preserve runtime configuration meaning

**Requirement:** The TUI shall interpret the existing Friday runtime files,
environment, workspace context, model/service bindings, and persistence paths
compatibly with Friday Chat while using its own frontend. **Priority/phase:**
P0, first release. **Status:** baseline. **Vision:** V-07.

**Acceptance criteria (EARS):**

- When the two frontends start from the same files, environment, launch
  context, and explicit mode, they shall resolve equivalent runtime services,
  model bindings, memory/storage paths, and validation results.
- If a runtime configuration is invalid, then the TUI shall present a
  diagnostic consistent with the same underlying Friday validation rather
  than silently substituting different defaults or a fake runtime.

**Testability:** Compare both frontends under disposable equivalent fixtures;
inspect service/model/path outcomes and failures, not just successful parsing.
Live changes made after startup are covered separately by FR-03.

### FR-03 — Change the active conversational model between turns

**Requirement:** A running TUI shall show and allow an explicit change to the
active conversational model, using loaded Friday chat profiles, without a
relaunch or a change to other service bindings. **Priority/phase:** P0, first
full release. **Status:** baseline. **Vision:** V-03, V-06.

**Acceptance criteria (EARS):**

- While a Friday session is idle, the TUI shall show the effective active
  conversational model and offer a keyboard-accessible chooser of `kind: chat`
  profiles in declaration order from the model-library YAML (normally
  `models.yaml`) referenced by the selected runtime configuration. The chooser shall include eligible chat profiles even if they
  are not currently bound to another service; it shall exclude embedding
  profiles and shall not accept an ad hoc provider or model ID.
- When the user confirms a valid chat-profile choice while idle, the TUI shall
  show it as the active conversational model and apply it only to future turns
  of the active conversation. It shall leave admitted work and other agent,
  extraction, compaction, and embedding bindings unchanged.
- While Friday is performing an operation, the TUI shall keep the current
  model visible, explain that switching is available after the operation
  finishes, and neither queue nor partly apply a requested change.
- If a selected profile fails validation or cannot be activated, then the TUI
  shall explain the selection error and retain the previous active model
  without making a provider request for the rejected choice.
- If a provider request through a newly selected conversational model fails,
  then the TUI shall show the error and restore the previously effective
  conversational model for future turns of the active conversation. It shall
  not automatically resend the failed prompt through either model; FR-20 and
  FR-23 govern its user-directed recovery. Other service bindings, admitted
  work, completed tool effects, and shared configuration shall stay unchanged.
- When the TUI exits, its selected model shall be discarded; a later run shall
  start from the loaded configuration. Selection shall not rewrite runtime
  YAML or TUI presentation settings. Other live runtime-setting controls,
  including active-workspace switching, are not first-full-release scope.

**Testability:** Use a loaded model library with multiple ordered chat profiles,
an unbound chat profile, and an embedding profile. Inspect chooser order and
eligibility, activation validation, future active-conversation provider calls,
other service bindings, busy-time behavior, failed-request fallback for the
next turn without TUI-level resend, and run-end reset. Existing Chat `/set`
changes scoped variables, so parity with it does not satisfy this requirement.

### FR-04 — Configure TUI presentation without changing runtime policy

**Requirement:** The TUI shall read optional, versioned `tui:` settings from
the existing CLI presentation file for appearance, layout, editor, keys,
output, discovery, accessibility, and TUI-only attachment options.
**Priority/phase:** P0, first release. **Status:** baseline. **Vision:** V-01,
V-07.

**Acceptance criteria (EARS):**

- When `tui:` is absent or partial, the TUI shall apply documented defaults,
  and existing Friday Chat and `friday-cli` shall retain their present file
  selection, values, and rendering behavior.
- When supported TUI settings are present, the TUI shall show their documented
  effects without using appearance/layout preferences to change model,
  credentials, storage, tool, or security policy. Explicit FR-03 runtime
  actions remain separate.
- If a TUI schema version, type, value, or keybinding is invalid, then the TUI
  shall show an actionable error before starting runtime services; valid YAML
  with TUI-only fields shall not break the existing CLI readers.

**Testability:** Load unchanged and extended copies of `cli-config.yaml` in
both frontends; compare CLI values/output, TUI defaults and visible settings,
invalid cases, read-only file behavior, and installed use. UXCFG-01–UXCFG-10
retain the detailed setting and attachment-limit cases.

### FR-05 — Conduct and display a Friday conversation

**Requirement:** The TUI shall submit accepted conversational input through
Friday's runtime and show the response, progress, errors, and subsequent turns
in one coherent session. **Priority/phase:** P0, first release. **Status:**
baseline. **Vision:** V-01.

**Acceptance criteria (EARS):**

- When a conversational prompt is accepted, the TUI shall show it once in
  chronological history and display Friday's streamed or final answer in
  order, without duplicate chunks or a duplicate persisted turn.
- While a response or slow command is in progress, the TUI shall keep
  navigation and editing responsive, show an accurate working state, and
  admit or reject additional submissions according to its visible busy rules.
- If a provider or runtime operation fails, then the TUI shall show a
  comprehensible failure state without presenting incomplete output as a
  successful final answer. FR-23 governs recovery and transcript treatment.

**Testability:** Drive deterministic streaming, slow, final-only, and failure
responses through the installed UI; assert ordering, one accepted turn, and
responsive focus/navigation. FR-18–FR-20 cover context-limit failures; FR-23
covers other provider/runtime failures.

### FR-06 — Enter and submit multiline prompts and commands

**Requirement:** One multiline editor shall accept conversational prompts and
`/` commands with explicit, predictable submission and newline actions.
**Priority/phase:** P0, first release. **Status:** baseline. **Vision:** V-01,
V-06.

**Acceptance criteria (EARS):**

- When the user presses `Enter` in the editor, the TUI shall submit the
  complete draft once. When the terminal delivers a distinct `Ctrl+Enter`, it
  shall insert one newline without submitting. Multiline paste shall not
  submit automatically.
- Where a terminal cannot distinguish `Ctrl+Enter` from `Enter`, the TUI shall
  provide a visible, keyboard-focusable Insert newline control and a visible
  Submit control; no undocumented substitute key shall be assumed.
- If submission is rejected because the TUI is busy or the input is invalid,
  then the editor shall retain the draft and caret for correction, without
  creating a new turn.

**Testability:** Combine headless key/paste tests with physical macOS/Linux
terminal observations of delivered keys, focus, pointer controls, multiline
text, and busy rejection. Synthetic events alone do not prove `Ctrl+Enter`.

### FR-07 — Navigate a readable conversation

**Requirement:** The TUI shall distinguish user prompts, Friday responses,
command results, and Activity while allowing the user to inspect retained
history without losing the current exchange. **Priority/phase:** P0, first
release. **Status:** baseline. **Vision:** V-01, V-06.

**Acceptance criteria (EARS):**

- When Friday displays an accepted prompt and response, the TUI shall use
  distinct role color cues plus text labels, show command results inline, and
  pin the latest accepted prompt above its scrolling response as a view of the
  same turn rather than a second model/transcript entry.
- While the conversation viewport is away from the bottom, the TUI shall
  pause automatic following, hide the pin when browsing an older exchange,
  and offer a visible keyboard- and pointer-accessible `Jump to latest`
  control. Returning to the bottom shall resume following and restore the pin
  when a latest prompt exists.
- If display bounds evict older messages, then the TUI shall show an eviction
  notice that points to `/transcript` only when saved entries exist and shall
  not imply that transient Activity or reasoning can be recovered there.

**Testability:** Use long streamed exchanges, older-history scrolling, view
clearing, eviction, no-transcript fixtures, narrow terminals, and role-color
accessibility checks. Verify no duplicate prompt in model input or export.

### FR-08 — Match the maintained `/` command behavior

**Requirement:** The TUI shall offer every maintained Friday Chat `/` command
and alias through the same UI-neutral command implementation used by Chat,
with identical syntax, validation, effects, error meaning, and state changes,
while presenting results in TUI form. **Priority/phase:** P0, first release.
**Status:** baseline. **Vision:** V-02, V-07.

**Acceptance criteria (EARS):**

- When a user submits any command or alias in the [50-command
  baseline](../../../active/command-refactor/command-matrix.md), the TUI shall produce equivalent behavior to
  Friday Chat for valid and invalid arguments, optional-service availability,
  progress, state/file effects, and result meaning. A displayed name alone
  shall not count as parity.
- The maintained command metadata, parser, validation, handlers/policy and
  typed results shall have one UI-neutral owner used by Chat and TUI. Neither
  frontend shall keep a second maintained-command implementation. When that
  command set changes, both frontends shall expose the intended behavior;
  TUI-only additions shall not silently alter Chat or `friday-cli` defaults.
- If a command requests a destructive or unavailable operation, then the TUI
  shall preserve the corresponding intent gate, error, and effect boundaries;
  it shall not turn a display action into an unrequested backend operation.

**Testability:** Run the [command matrix](../command-handoff.md#command-matrix) against equivalent
disposable Chat/TUI fixtures by command family, including aliases and negative
paths. Assert both frontends use the shared command owner and compare effects,
not merely output text. The `@agent` conversational
route is included in routing parity; D-117 defers optional `!` shell execution
from this release.

### FR-09 — Discover, review, and extend `/` commands

**Requirement:** Users shall be able to discover supported commands in place,
complete their names and declared subcommands, review syntax, and explicitly
submit them; the TUI command surface shall support later additions.
**Priority/phase:** P0, first release. **Status:** baseline. **Vision:** V-02,
V-06.

**Acceptance criteria (EARS):**

- When a user types a leading `/` or recognized subcommand prefix, the TUI
  shall show matches and a metadata-derived usage hint without changing the
  draft or dispatching. `Up`/`Down` and `Tab` shall highlight and insert only
  the selected token; `Enter` shall remain Submit.
- When a command is chosen from the palette, the TUI shall fill and focus the
  editor without running it. If a draft already exists, then Cancel shall
  preserve it exactly and Confirm shall replace it without submission.
- When a new TUI-only command is registered, help, completion, and the palette
  shall expose it, name/alias collisions shall be rejected, and existing
  command behavior shall remain unchanged.
- Help, completion, usage hints, and the palette for maintained commands shall
  derive from the shared registry metadata, so a maintained syntax or alias
  change is defined once. TUI-only extensions compose into the TUI's effective
  registry without changing either CLI's default registry.

**Testability:** Exercise typed prefixes, aliases, subcommands, free-form
arguments, palette selection, draft replacement, keyboard focus, duplicate
registration, and one representative added command in a disposable session.

### FR-10 — Preserve session and transcript meaning

**Requirement:** The TUI shall distinguish current display state from Friday
session history, persisted transcripts, memory, and active-agent selection.
**Priority/phase:** P0, first release. **Status:** baseline. **Vision:** V-01,
V-02.

**Acceptance criteria (EARS):**

- When `/cls` or `/clearscreen` is submitted, the TUI shall clear the visible
  conversation, latest-prompt pin, and Activity without deleting session
  history, memory, or persisted transcript entries; `/clear` and `/reset`
  shall retain their distinct Chat-compatible effects.
- When `/sessions` or `/transcript` is submitted, the TUI shall list, inspect,
  or export persisted sessions according to its arguments without changing
  the active transcript session. `/switch [agent]` shall change the active
  agent, not the transcript session.
- If a turn fails under FR-19 or FR-23, then its transcript treatment shall
  follow the failed/incomplete-turn rules rather than recording a successful
  turn or serializing transient Activity/reasoning.

**Testability:** Compare command effects against disposable transcript and
memory stores; verify display clear, export bytes where applicable, active
agent/session distinction, and no failed-turn records.

### FR-11 — Recall current-run editor submissions

**Requirement:** The editor shall offer non-executing recall of accepted
submissions during the current TUI run while protecting an unsent draft.
**Priority/phase:** P0, first release. **Status:** baseline. **Vision:** V-06.

**Acceptance criteria (EARS):**

- When an accepted prompt, `/` command, or `@agent` message is submitted, the
  TUI shall make its text available for current-run editor recall without
  re-executing it; rejected and unsent drafts, results, and Friday responses
  shall not become recall entries. The deferred `!` route does not create
  first-full-release recall entries.
- While a user browses recall, boundary `Up`/`Down` keys shall navigate
  entries only when slash suggestions are closed; editing a recalled copy
  shall not change the stored entry. Leaving recall without submission shall
  restore the exact unsent draft and caret.
- When the TUI exits, it shall discard editor recall state; a new run shall
  not rebuild it from persisted transcripts.

**Testability:** Test caret boundaries, suggestion priority, unsent draft
restoration, route inclusion/exclusion, no execution on recall, and restart.
Distinguish this history from the Chat-compatible `/history` command.

### FR-12 — Show truthful, inspectable Activity

**Requirement:** The TUI shall show a bounded chronological Activity view for
actual tool execution and relevant rejected requests across agentic steps,
delegation, workflows, and manual `/run-tool`. **Priority/phase:** P0, first
release. **Status:** baseline. **Vision:** V-04.

**Acceptance criteria (EARS):**

- When a tool actually begins execution, Activity shall show its actor,
  identity, ordered step, parameters as passed, and running/terminal status.
  When a model or user request is rejected before invocation, Activity shall
  mark it `Not run` with a reason, never as executed. Tool candidates excluded
  before a request shall produce no `Not run` entry.
- When Activity receives its first entry for an exchange, the TUI shall open
  the inline section before the final answer. While the user has collapsed
  it, new entries shall accumulate without reopening it; its header shall
  count new entries and indicate eviction. While its own viewport is above
  the bottom, it shall pause following and offer a separate `Jump to latest
  Activity` control without moving the conversation viewport.
- If a parameter exceeds its view limit, then Activity shall show a marked
  preview and discard the overflow from TUI view state while the tool still
  receives its full argument. The user shall be able to copy only selected
  rendered text. Automatic tool-result payloads shall not appear in Activity
  or chat; user-entered `/run-tool` shall retain its inline command result.

**Testability:** Use a multi-step fake agent with executed, rejected, repeated,
delegated, failed, and timed-out tool calls. Check actual invocation boundaries,
argument fidelity, ordering, copy bounds, collapse/scroll behavior, and
non-persistence. The [Activity requirement](../tool-activity-requirement.md)
remains the detailed behavior source.

### FR-13 — Offer provider-supplied reasoning as a separate view

**Requirement:** A user shall be able to hide or show reasoning text actually
supplied by a provider without changing generation settings or the final
answer. **Priority/phase:** P0, first release. **Status:** baseline.
**Vision:** V-04.

**Acceptance criteria (EARS):**

- When no TUI preference is set, the view shall show the final answer and
  hide raw reasoning. When the user enables the view, it shall show only
  provider-supplied reasoning text in a labeled, separate, collapsible area
  at the correct model step, including steps after tool execution.
- When the in-app visibility toggle changes, it shall affect subsequent
  reasoning events without rewriting configuration or revealing text
  discarded while hidden.
- If a provider supplies only a reasoning-token count or no reasoning text,
  then the TUI shall not synthesize text or confuse usage with a viewable
  thought; the final answer shall remain available.

**Testability:** Stub text, count-only, and absent provider events; test
hidden/shown/default, mid-stream toggle, later model steps, ordering, copy,
view bounds, and absence from normal transcripts, exports, memory, and logs.

### FR-14 — Browse and manage selected-file context

**Requirement:** The Context area shall let a user select, inspect, refresh,
and remove files whose captured content is supplied to later eligible model
turns. **Priority/phase:** P0, first release. **Status:** baseline.
**Vision:** V-05.

**Acceptance criteria (EARS):**

- When a user deliberately activates a readable file by keyboard or pointer,
  the TUI shall begin attaching its content without submitting a prompt or
  requiring a second Add action. Focus movement and list scrolling alone
  shall not attach it. A new distinct file shall join existing attachments.
- While attached, a complete captured snapshot shall be used for later
  eligible turns until Remove. Reselecting the same file shall refresh its
  snapshot; a failed refresh shall leave the previous complete snapshot
  active. Removal shall affect future turns, not an already admitted one.
- When the TUI exits, it shall discard active attachments. Browsing or
  attaching shall not edit files, ingest memory, or switch transcript
  sessions.

**Testability:** Inspect actual model inputs after selection, subsequent
turns, multi-file addition, removal, source-file modification, refresh
success/failure, restart, and an in-flight turn. Exercise sidebar collapse,
keyboard focus, pointer selection, and narrow terminal behavior.

### FR-15 — Extract complete content from supported files

**Requirement:** Attached text/code/data, PDF, DOCX, and XLSX files shall
contribute real, complete extracted content rather than a filename or
placeholder. **Priority/phase:** P0, first release. **Status:** baseline.
**Vision:** V-05.

**Acceptance criteria (EARS):**

- When a supported readable file is selected, the TUI shall supply its
  extracted content, with source labels, to Friday's next eligible model
  input. An XLSX attachment shall include every worksheet, including hidden
  sheets, in workbook order; formula cells shall distinguish expressions
  from saved results and identify absent saved results.
- If extraction yields no usable content, a dependency is unavailable, a
  file is corrupt, a worksheet is unreadable, or a reader truncates output,
  then the TUI shall report the cause and shall not attach a partial new
  snapshot. A failed refresh shall retain the last complete snapshot.

**Testability:** Use positive installed-package fixtures for every format,
multi-sheet and formula cases, plus corrupt, empty, missing-reader, and
truncation fixtures. Assert actual model-bound content, not merely reader
return values or an attachment label.

### FR-16 — Read scanned PDF pages with Tesseract

**Requirement:** The TUI shall obtain usable text from scanned/image-only PDF
pages for selected-file context. **Priority/phase:** P0, first release.
**Status:** baseline. **Vision:** V-05.

**Acceptance criteria (EARS):**

- When a selected PDF page has usable embedded text, the TUI shall use it;
  when a page needs OCR, it shall render that page and use Tesseract with the
  configured installed language packs, preserving page order without duplicate
  text. English shall be the default OCR language.
- If rendering, Tesseract, a requested language pack, or usable text is
  unavailable for a required page, then the TUI shall identify the page and
  cause and reject the entire new PDF attachment. A failed refresh shall
  retain the previous complete snapshot.
- When installed from a wheel or sdist on macOS or Linux, the TUI shall
  include its PDF page-rendering capability; the user shall install Tesseract
  and selected language packs separately as documented.

**Testability:** Run real scanned and mixed-page PDF fixtures through the
installed package; inspect actual model input, page order, language delivery,
missing-prerequisite errors, and complete-rejection behavior.

### FR-17 — Bound whole selected-file attachments

**Requirement:** The TUI shall admit selected-file context only when each
complete formatted attachment and the combined active set fit their TUI
attachment limits. **Priority/phase:** P0, first release. **Status:**
baseline. **Vision:** V-05, V-06.

**Acceptance criteria (EARS):**

- When limits are omitted, the TUI shall use fixed defaults of 4,000
  estimated tokens per file and 8,000 combined, independent of the selected
  model; valid explicit TUI settings shall override the corresponding limit.
  The estimate shall count the complete formatted text sent to Friday,
  including labels, OCR, formulas, and saved-result labels.
- If a new file or proposed combined set exceeds its limit, then the TUI
  shall reject the whole new attachment with estimated usage and limit,
  without trimming, evicting an existing file, or changing model input. An
  over-limit refresh shall keep the last complete snapshot.

**Testability:** Use deterministic boundary fixtures at 3,999/4,000/4,001
and 7,999/8,000/8,001 estimated tokens, multiple models, multi-file totals,
and refresh replacement. Verify invalid settings fail before runtime startup.
These limits do not guarantee that a whole model request fits; FR-18 is
separate.

### FR-18 — Check complete model input and request bounded compaction

**Requirement:** Before each conversational model step, Friday shall check
the complete assembled request against the effective input budget and use
configured older-turn compaction at most once when eligible. **Priority/phase:**
P0, first release. **Status:** baseline. **Vision:** V-05, V-06.

**Acceptance criteria (EARS):**

- When a model step is assembled, the TUI shall evaluate the effective
  budget including instructions, selected history/memory, tools, draft,
  whole active attachments, and output reserve before the primary provider
  call.
- If the step is over budget and runtime older-turn compaction is enabled
  and eligible, then Friday shall attempt it at most once, show progress,
  reassemble and re-estimate, and continue automatically only if the full
  step now fits. It shall not trim current tool output or attachments or
  silently change runtime settings.
- If the step still does not fit, then the TUI shall show estimated total,
  available budget, and overage. For a first step it shall retain the draft,
  caret, and attachment snapshots without admitting a new turn or sending
  the blocked primary request; for a later step it shall stop further model/
  tool work and mark the turn incomplete while preserving completed effects.

**Testability:** Use deterministic request estimates, separate primary and
maintenance provider spies, disabled/ineligible/failed/successful compaction,
first and later steps, and disposable memory/transcript stores. Compaction's
own calls and durable effects must remain visible and must not be described
as a side-effect-free rejection.

### FR-19 — Handle provider context-length rejection after send

**Requirement:** A provider context-length rejection after a locally passing
estimate shall be presented as a post-send failure with user-directed
correction, without a TUI-level automatic retry. **Priority/phase:** P0,
first release. **Status:** baseline. **Vision:** V-06.

**Acceptance criteria (EARS):**

- If the provider rejects a sent request for context length, then the TUI
  shall identify it as a provider response, preserve recoverable user state,
  and not automatically compact, resend, or claim that the provider was
  never called.
- If the first provider step is rejected, then the TUI shall create no
  failed-attempt transcript record and keep the prompt recoverable for this
  run under FR-20. If a later step fails after tools executed, then it shall
  mark the turn incomplete, retain earlier Activity and actual tool effects,
  stop further steps, and write no incomplete-turn transcript entry.

**Testability:** Use a fake provider that distinguishes recognized context
errors from unrelated failures, with provider-call counts, disposable
transcripts, executed-tool effects, and installed error/retry UX.

### FR-20 — Restore or dismiss failed prompts without accidental resubmission

**Requirement:** An initial prompt failed by a provider/runtime error shall remain
recoverable in the current TUI run without overwriting a newer unsent draft
or creating a transcript record for the failed attempt. **Priority/phase:**
P0, first release. **Status:** baseline. **Vision:** V-06.

**Acceptance criteria (EARS):**

- When an initial prompt receives a recognized context-length rejection or
  another provider/runtime failure, the TUI shall restore its exact text/caret
  into an empty editor or offer a
  visible Restore action if newer text is present. Restoring into a nonempty
  editor shall require Confirm/Cancel and shall never submit automatically.
- While a failed prompt remains recoverable, its editor-adjacent action shall
  survive error-notice eviction and `/cls`. With multiple pending failures,
  the TUI shall show an accurate-count, newest-first chooser; restoring one
  shall keep its original snapshot available until a later conversational
  turn succeeds or the user explicitly dismisses it.
- When the user selects Dismiss, the TUI shall require confirmation, remove
  only that snapshot, update the visible count/actions, and leave the editor
  draft, caret, attachments, and provider/transcript state unchanged. A
  successful later conversation shall clear earlier pending recoveries;
  relaunch shall not reconstruct them.

**Testability:** Exercise context-length, network, authentication, timeout and
other runtime failures with empty/occupied editor, multiple pending failures,
newer draft, notice eviction, display clear, repeated Restore, Cancel,
Dismiss, later failure/success, relaunch, focus, and narrow layouts. Assert
no TUI-initiated resend and no failed-attempt transcript entry. AC-26 and
AC-29–AC-34 retain the detailed state cases.

### FR-21 — Quit at a safe stopping point

**Requirement:** Normal Quit shall stop accepting new work, finish admitted
non-interruptible work, clean up owned resources, and restore the terminal;
a separately confirmed Force quit shall warn about incomplete work/cleanup.
**Priority/phase:** P0, first release. **Status:** baseline. **Vision:** V-06.

**Acceptance criteria (EARS):**

- When the user requests normal Quit while work is active, the TUI shall
  show a pending state, wait for a safe stopping point, clean up, and report
  success or failure accurately. Busy `/q` and `/quit` submissions shall
  retain editor text; the separate Quit action may request graceful exit.
- If the operation is stalled and the user deliberately confirms Force quit,
  then the TUI shall warn that work or cleanup may remain incomplete and
  shall not report a successful graceful Quit.

**Testability:** Simulate slow/non-interruptible work, cleanup success/failure,
busy slash submission, and Force quit; verify no lost accepted operation,
resource outcome, process status, and terminal-mode restoration in a PTY and
physical terminal.

### FR-22 — Show startup replay outcomes without entering a session

**Requirement:** The TUI shall preserve the accepted `--replay FILE` startup
route and its separate read-only success/error views. **Priority/phase:** P0,
first full release. **Status:** baseline. **Vision:** V-09, V-06.

**Acceptance criteria (EARS):**

- When `--replay FILE` is supplied, the TUI shall follow the accepted launcher
  precedence and delay behavior in D-62–D-65, without starting an interactive
  configuration chooser or accepting prompts and `/` commands.
- When replay succeeds, the TUI shall show the replay file and processed-turn
  count, without a per-turn list, in a read-only result view until Quit.
- If replay fails, then the TUI shall show the file and actionable error in a
  read-only view until Quit, then exit nonzero. It shall not offer in-process
  Retry; the user corrects the cause and relaunches.

**Testability:** Exercise success, input error, processing error, delay and
option precedence through the installed launcher; verify file/count versus
file/error, no interactive session, Quit, exit code, and no hidden retry.
Interactive `/replay` remains command parity under FR-08.

### FR-23 — Recover from other provider and runtime failures

**Requirement:** Ordinary provider/runtime failures shall leave the user with
truthful turn state and a deliberate recovery path, using the same user-state
protections as provider context-length failures. **Priority/phase:** P0,
first release. **Status:** baseline. **Vision:** V-06.

**Acceptance criteria (EARS):**

- If the initial conversational request fails before any tool runs, then the
  TUI shall show the error, preserve the exact submitted text/caret and active
  attachments under FR-20, protect any newer unsent draft, and create no
  failed-attempt or successful-turn transcript entry. It shall not
  automatically resend the prompt at the TUI level.
- If a later model/runtime step fails after one or more tools execute, then
  the TUI shall mark the turn incomplete, retain its earlier Activity and
  completed tool effects under bounded current-run display rules, stop
  further model/tool steps, and create no incomplete/completed-turn
  transcript entry. A newer unsent editor draft shall remain intact.
- When a provider request using a newly selected conversational model fails,
  FR-03's fallback shall determine the active model for future turns; the
  failed turn shall still follow this requirement without automatic resend.

**Testability:** Use deterministic network/authentication/timeout and runtime
failures before and after a fake executing tool; assert editor/caret and
attachment preservation, Restore behavior, no extra TUI-level provider call,
next-turn model routing, visible incomplete Activity/effects, unchanged
completed transcript entries and no failed/incomplete turn entry. Check
installed macOS/Linux recovery and unchanged Chat/`friday-cli` behavior;
Friday LLM transport retry policy remains separate.

## Non-functional and release requirements

### NFR-01 — Install independently and preserve both CLIs

**Requirement:** `friday-tui` shall install and run independently without a
runtime dependency or import of `friday-chat` or `friday-cli`; its construction
shall preserve both existing applications' behavior. **Priority/phase:** P0,
first release. **Status:** baseline. **Vision:** V-07.

The [shared command architecture](../command-handoff.md#shared-command-architecture)
implements this package boundary by placing maintained command behavior below
both frontends; sharing code does not mean importing or launching a CLI.

**Acceptance criteria (EARS):**

- When the TUI is installed without either CLI package, its declared
  executable and supported functions shall work through Friday's UI-neutral
  runtime/services. When installed alongside the CLIs, neither CLI shall
  import TUI/UI dependencies or change its commands, defaults, rendering,
  configuration, public behavior, or package startup because of the TUI.
- If shared Friday service behavior must change to support a TUI workflow,
  then the change shall have a bounded public contract and before/after
  regression evidence for affected Chat and `friday-cli` behavior.

**Testability:** Build and install wheel/sdist outside the checkout, inspect
dependency/import closure, run both CLIs with and without the TUI, and compare
the pre-implementation behavior baseline and focused regressions. A successful
TUI test alone is insufficient.

### NFR-02 — Work in supported terminals and remain accessible

**Requirement:** Essential TUI workflows shall remain usable from a keyboard
on initial macOS/Linux terminals, with specified pointer controls and readable
status across ordinary and narrow layouts. **Priority/phase:** P0, first
release. **Status:** baseline. **Vision:** V-06, V-08.

**Acceptance criteria (EARS):**

- While the terminal is at or above the documented minimum usable size, the
  TUI shall keep editor, conversation, status, command help, file selection,
  and safe Quit reachable through keyboard focus; it shall adapt rather than
  hide essential controls when the Context area collapses.
- When dark, light, or high-contrast presentation is selected, the TUI shall
  keep user/Friday roles and operation states understandable without color
  alone. Where a specified pointer action exists, keyboard activation shall
  produce the same user effect.
- If a terminal does not deliver a distinct shortcut or is resized below a
  usable layout, then the TUI shall provide the documented focusable fallback
  or an explicit size/interaction message rather than silently losing input.

**Testability:** Combine headless resize/focus tests with physical macOS
Terminal.app on arm64 and Ubuntu 24.04 GNOME Terminal on x86_64. Cover actual
key delivery, paste, mouse actions, color modes, Unicode, and terminal
restoration at 120×30 full layout, 80×24 minimum usable layout, and below
minimum with a resize message and Quit reachable. Record actual OS and
terminal versions.

### NFR-03 — Respect security, data, and observability boundaries

**Requirement:** TUI presentation shall not grant tool authority, alter Friday
runtime policy, or silently persist transient Activity and reasoning. Live
runtime controls shall report their effects and obey existing Friday safety
boundaries. **Priority/phase:** P0, first release. **Status:** baseline.
**Vision:** V-06, V-07.

**Acceptance criteria (EARS):**

- When a command, tool, or model choice is presented, the TUI
  shall use Friday's actual admission/validation outcome; a visible control
  shall not bypass tool policy or make an unavailable capability appear to
  have run.
- While Activity or provider reasoning is shown, it shall be bounded
  in-process view state rather than a new transcript, export, memory, or
  telemetry record by default. Selected visible text may be copied; hidden
  reasoning and discarded oversized arguments shall not be copyable.
- When Activity shows tool parameters, it shall show the values passed up to
  the display bound without TUI-specific credential filtering, as already
  decided; the guide shall explain the exposure in a shared or recorded
  terminal. If a live model selection is rejected or a request through a
  newly selected model fails, then the prior effective conversational model
  shall be shown and usable for future turns under FR-03, without changing
  other service bindings or automatically resending the failed prompt.

**Testability:** Verify policy-denied calls, `Not run` vs execution, no
unrequested tool invocation, bounded view/copy behavior, no transient-data
persistence, and failure atomicity for FR-03 using disposable stores.

### NFR-04 — Publish accurate, task-oriented user documentation

**Requirement:** The first full release shall include a user-oriented TUI guide
and updated configuration reference verified against the installed TUI.
**Priority/phase:** P0, first release. **Status:** baseline. **Vision:** V-08.

**Acceptance criteria (EARS):**

- When the TUI is ready for acceptance, `docs/guides/` shall provide a
  task-focused guide covering install/start, configuration choice, screen
  zones, editing, navigation, every shipped `/` command and alias, live
  conversational-model changes, startup replay, file context,
  Activity/reasoning, recovery, and
  safe Quit. It shall link to the detailed `tui:` setting reference in
  `docs/guides/10-configuration.md`.
- If a documented key, setting, label, command, result, or recovery action
  differs from the installed candidate, then the discrepancy shall be
  corrected before the guide claims release behavior. The guides shall not
  claim TUI availability before the feature is shipped.

**Testability:** Have users follow the guide on installed macOS and Linux
candidates; verify examples, links, setting defaults, labels, errors, and
command effects. The [user-guide requirements](../user-guide-requirements.md)
remain the detailed content checklist, with the deferred `!` route omitted
from first-full-release instructions.

### NFR-05 — Verify each increment and the final installed product

**Requirement:** Construction and acceptance shall use bounded behavioral
checks, independent candidate review, CLI compatibility regression checks,
physical terminal UAT, and a controlled real-provider/tool run.
**Priority/phase:** P0, first release. **Status:** baseline. **Vision:** V-08.

**Acceptance criteria (EARS):**

- When a user-visible increment is built, it shall have positive, negative,
  and regression evidence tied to its requirement IDs before dependent work
  is treated as complete; passing automation shall not substitute for
  hands-on terminal UAT where physical interaction matters.
- When a preview alpha is published, its release notes shall identify the
  tested subset and open requirements; the preview shall not claim
  first-full-release acceptance. A separate phase plan shall map requirements
  and UAT gates to previews before staging is treated as settled.
- Before final installed UAT, the named pre-UAT gate shall bind the exact real
  model provider, executing tool, fixture, expected effect, and authority
  for the controlled run, without placing credentials in the PRD.
- Before first-full-release acceptance, installed macOS and Linux terminal UAT
  shall cover the main workflows, and a controlled installed run shall use
  that bound real provider and executing tool. Required guides and CLI
  preservation checks shall pass; failed or unrun release cases shall remain
  open.

**Testability:** Maintain requirement-to-test evidence, disposable stores,
deterministic fake providers/tools for failure paths, focused and installed
package tests, exact-source automated Linux checks, and separately recorded
physical UAT. The current shell's macOS physical UAT remains open.

## User workflows

| Workflow | User goal and expected outcome | Requirements |
| --- | --- | --- |
| First launch | Install, select an existing runtime YAML, see active mode, configured workspace, and model, submit a prompt, read Friday's answer, and quit safely. | FR-01–FR-07, FR-21, NFR-01–NFR-02 |
| Change the model | While idle, choose a loaded chat profile in file order, confirm it, and see only future turns of this conversation use it. A rejected selection keeps the previous model; a failed provider request through the newly selected model restores the previous model for future turns, shows an error and leaves retry to the user. | FR-03, FR-23, NFR-03 |
| Replay at startup | Launch with `--replay FILE`, inspect a read-only file/count result or file/error result, then Quit without an interactive session. | FR-22, NFR-04 |
| Use a command | Discover a `/` command, inspect usage, edit arguments, submit, inspect result/effects, and continue the same session; use equivalent Chat semantics for invalid input and unavailable services. | FR-08–FR-11, FR-21 |
| Follow agent work | Submit a task that calls tools, inspect real execution parameters/status and optional provider reasoning, read the final answer, browse older Activity, then return to latest. | FR-05, FR-07, FR-12–FR-13, NFR-03 |
| Attach a document | Browse to a file, select it, see extracted content become active for later turns, refresh/remove it, and receive a complete error if extraction/OCR or limits fail. | FR-14–FR-18 |
| Recover from context pressure | Submit an over-budget or provider-rejected prompt, see a truthful error/compaction outcome, restore/edit the prompt without losing newer work, and retry deliberately. | FR-18–FR-20, FR-10 |
| Recover from another runtime failure | If the initial request fails, recover the exact prompt without losing a newer draft or attachments and retry deliberately. If a later step fails after a tool runs, inspect the incomplete turn and completed effects. | FR-20, FR-23, FR-10 |

## Edge cases that must remain visible in test planning

These cases refine the numbered requirements; they are not additional
untraced requirements.

| Case | Required outcome | Requirement / vision |
| --- | --- | --- |
| Invalid explicit config versus invalid chooser selection | Explicit path exits nonzero; chooser selection remains recoverable. Partial startup cleans up and reports failures. | FR-01 / V-01, V-06 |
| Model switch requested during work | No switch or queue is accepted until Friday is idle; current work and other service bindings remain unchanged. | FR-03 / V-03, V-06 |
| Newly selected model fails on a provider request | Show the error and restore the previous model for future turns; do not automatically resend the failed prompt. | FR-03, FR-23 / V-03, V-06 |
| `Ctrl+Enter` indistinguishable from `Enter` | Focusable Insert newline remains available; paste does not submit. | FR-06, NFR-02 / V-06 |
| Requested tool rejected before invocation | Show `Not run` and reason, never executed status or a fabricated result. | FR-12 / V-04 |
| Mixed or unreadable document | Preserve PDF page/XLSX sheet order; reject incomplete new content and keep a previous good snapshot on refresh failure. | FR-14–FR-16 / V-05 |
| Attachment admitted but full request too large | Keep attachment snapshots and draft; apply only eligible bounded older-turn compaction, then recheck whole request. | FR-17–FR-18 / V-05, V-06 |
| Provider rejects after local estimate passes | State that a provider call occurred; no automatic resend; preserve recoverable prompt or incomplete later-turn evidence. | FR-19–FR-20 / V-06 |
| Other provider/runtime failure | Preserve initial prompt/caret/attachments and any newer draft, or mark a post-tool turn incomplete with completed effects visible; no automatic TUI resend or completed-turn transcript entry. | FR-20, FR-23 / V-06 |
| Multiple pending failed prompts | One accurate-count chooser; no accidental provider call or transcript record; Confirm/Cancel and Dismiss protect newer draft. | FR-20 / V-06 |
| Stalled work on exit | Normal Quit waits and reports cleanup; confirmed Force quit warns of unfinished effects. | FR-21 / V-06 |

## Explicit non-goals and deferred items

- The TUI does not replace or change `friday-chat` or `friday-cli`, create a
  second runtime-file dialect, use presentation settings to alter runtime
  policy, or make a displayed tool request count as execution (NFR-01,
  NFR-03; V-07).
- A partial command set or static shell is an implementation milestone, not
  first-release acceptance (FR-05, FR-08; V-01, V-02, V-08).
- Browsing a file does not edit it, ingest it into memory, or switch active
  transcript sessions (FR-14; V-05). The first release has no active
  transcript-session switch, `Load older` control, or recovery of transient
  Activity/reasoning from transcripts (FR-07, FR-10, FR-12–FR-13).
- Persisted editor-recall history, automatic TUI preference-file writes,
  provider-reasoning export, full Activity export, and TUI-specific sensitive-
  value filtering are deferred ideas, not current release requirements. Each
  needs a new vision/requirements decision before implementation.
- The first full release has no active-workspace switch or additional live
  runtime-setting editor beyond conversational-model selection (FR-03; V-03).
  The optional `!<command>` shell route is deferred; this does not change
  Friday Chat or `friday-cli` (D-117; V-02, V-07).

## Out-of-bounds scope review

The following source requests are deferred or are technical/process choices
rather than first-full-release product requirements. Startup replay was
reconciled into V-09/FR-22 and is no longer out of bounds. Their source text
remains visible in the linked documents. Architecture or release planning
must not infer approval to implement deferred items from this table.

| Review ID | Source request | Disposition and reason | Future treatment |
| --- | --- | --- | --- |
| OOB-02 | Optional `!<command>` shell route (command matrix additional route; D-75 recall and guide references). | **Deferred by D-117.** It is not first-full-release TUI input parity or editor recall. The `@agent` route remains in scope; Chat/CLI behavior is unchanged. | Define a later release's safety and UX criteria only if prioritized. |
| OOB-03 | Optional terminal bell/native desktop notifications, extra dashboard panels, persisted drafts/history, active transcript-session switching, reasoning/Activity export, or TUI-specific parameter redaction (UX configuration and focused requirement documents). | **Out of first-release scope or deferred.** These are later possibilities or explicit first-release exclusions; none should be converted to a baseline requirement through incidental mention. | Reframe in a future vision and PRD only if prioritized. |
| OOB-04 | Exact Textual version, thread/loop bridge, package cohort choreography, historical Enter/F2/F3/F4 bindings, and withdrawn Chat-dependent API proposals (T-01, T-03–T-08 and withdrawn plans). | **Out of product PRD scope.** These are implementation or withdrawn proposals; some conflict with accepted independence and editor decisions. | Decide technical design under an authorized construction contract, using current product requirements rather than reviving the old proposal. |
| OOB-05 | Branch activation and board/directive workflow instructions (D-04 and packet authority records). | **Out of product PRD scope.** The repository lifecycle policy governs this process; it does not describe user-visible TUI behavior. | Continue tracking it on the board, not as a product acceptance criterion. |

## Security, governance, and observability notes

NFR-03 is the product security boundary: runtime/tool policy continues to
decide what may execute, and a live model choice must not bypass it.
FR-12/FR-13 are display observability, with truthful execution and provider
availability labels. Their view state is bounded and transient. Persistent
transcripts, configured memory, and provider/operational telemetry retain
their separate existing meanings; a failure or display clear must not be
described as rolling back already completed runtime effects. Showing
unfiltered tool parameters is an accepted first-release choice; the user
guide must explain that visible content can appear in terminal recordings.

## Testability and release evidence

Requirement-level tests should use deterministic fakes to prove event and
failure ordering, disposable real stores to prove side effects, installed
wheel/sdist checks to prove packaging, and physical terminal UAT for keys,
pointer use, resize, readability, and restoration. Full first-release
acceptance additionally needs a controlled real-provider/tool run, a hands-on
Linux terminal run, updated user guides, and unchanged Chat/`friday-cli`
behavior. Automated Linux checks and a `VERIFIED` unit are evidence for their
named gates, not substitutes for product acceptance. The current TUI shell
remains a development milestone with physical macOS UAT open.

## Source disposition and vision trace audit

This audit accounts for the numbered product decisions and current AC rows.
Ranges are inclusive. The requirement table provides the individual vision
links; the out-of-bounds rows deliberately have none. Supporting screen,
Activity, reasoning, UX, command, and guide documents refine the cited IDs.

| Source IDs | PRD destination |
| --- | --- |
| Q-01–Q-03 | NFR-02; FR-06; FR-21 |
| D-01–D-03 | FR-08; NFR-01; FR-09 |
| D-04 | OOB-05, process only |
| D-05–D-08 | NFR-05; FR-02; FR-04; NFR-01 |
| D-09–D-15 | FR-21; FR-08; NFR-05; FR-01; NFR-04 |
| D-16–D-18 | FR-07; FR-13 |
| D-19–D-32 | FR-12; FR-13; NFR-03; NFR-05; FR-21 |
| D-33–D-39 | FR-07; FR-10; FR-11; FR-06 |
| D-40–D-46 | FR-09; FR-12 |
| D-47–D-61 | FR-01; FR-02 |
| D-62–D-65 | FR-22 |
| D-66–D-70 | FR-09 |
| D-71–D-75 | FR-11; `!` portion of D-75 to OOB-02 |
| D-76–D-81 | FR-14 |
| D-82–D-91 | FR-15; FR-16 |
| D-92–D-97 | FR-17 |
| D-98–D-99 | FR-18 |
| D-100–D-109 | FR-19; FR-20 |
| D-110–D-114 | FR-03; NFR-03 |
| D-115 (superseded by D-121) | Historical decision only; D-121 controls current behavior |
| D-116 | FR-22 |
| D-117 | OOB-02; FR-11 exclusion |
| D-118–D-120 | NFR-02; NFR-05; release boundary |
| D-121 | FR-03; FR-23; NFR-03; AC-35 |
| D-122 | FR-05; FR-10; FR-20; FR-23; NFR-03; AC-36 |
| D-123 | FR-08; FR-09; NFR-01 |
| AC-01–AC-03 | FR-07–FR-10; OOB-02 for deferred shell route |
| AC-04–AC-07 | FR-01; FR-05–FR-07; FR-21–FR-22; NFR-02 |
| AC-08–AC-13 | NFR-01; NFR-05; FR-09 |
| AC-14–AC-18 | FR-02; FR-04; FR-12–FR-13; FR-22; NFR-04 |
| AC-19–AC-22 | FR-14–FR-17 |
| AC-23–AC-24 | FR-18 |
| AC-25–AC-28 | FR-10; FR-19–FR-20 |
| AC-29–AC-34 | FR-20 |
| AC-35–AC-36 | FR-03; FR-05; FR-10; FR-20; FR-23; NFR-03 |
| PAR-001–PAR-050 and recorded aliases | FR-08; command matrix is a behavior inventory, not name-only acceptance |
| UXCFG-01–UXCFG-08 | FR-04; NFR-01–NFR-02; NFR-03 |
| UXCFG-09–UXCFG-10 | FR-16–FR-18 |
| User-guide checklist 1–7 | NFR-04; model fallback to FR-03; general failure recovery to FR-23; startup replay to FR-22; deferred `!` portion to OOB-02 |
| Historical T-01–T-08 and withdrawn plans | OOB-04 except accepted T-02 product direction already covered by FR-04 |

## Accuracy pass and decision resolution

| Finding | Consequence / next decision |
| --- | --- |
| [Vision V-03](../vision/README.md#v-03) requires live model choice. Friday Chat `/set` currently changes scoped variables, not the active model. | FR-03 now specifies loaded chat-profile order, idle-only activation, active-conversation future-turn effect, run scope, and fallback after a request through the newly selected model fails. Do not treat `/set` parity as delivery. |
| D-62–D-65 startup replay previously lacked a direct vision outcome; the optional `!` route was ambiguous. | V-09/FR-22 retain startup replay. D-117 explicitly defers `!` from the first full release, including recall and user-guide instructions. |
| The old PRD broadly defers mouse interaction, while D-36/D-44/D-76–D-77 and the screen proposal require specified pointer controls. | Treat named pointer workflows as baseline under FR-07, FR-12, FR-14, and NFR-02; defer only unspecified extra mouse features. |
| Terminal size/platform targets were generic, and the real provider/tool case has not yet been bound. | NFR-02 records the accepted physical UAT matrix. NFR-05 places exact provider/tool/fixture/authority binding at a named pre-UAT gate; final installed UAT cannot claim completion before that gate and run. |
| The accepted first-full-release bundle is large and the current shell has no runtime connection. | Re-plan around the installed startup-to-answer milestone, then live model selection, then bounded command/Activity/file workflows. Preview alphas may ship tested subsets with explicit open scope; the first full release retains the complete baseline. |

The maintainer answered the PRD review cohort and follow-up on 2026-10-19.
These decisions are recorded in D-110–D-122; they settle product intent but do not authorize
construction, delivery, or release.

| Review ID | Decision to settle | Affected scope | Status |
| --- | --- | --- | --- |
| PRD-Q-01 | Which models may be selected? | FR-03 | **Resolved:** `kind: chat` profiles from loaded `models.yaml` in declaration order, including unbound chat profiles; no embeddings or ad hoc IDs (D-111). |
| PRD-Q-02 | Which additional runtime choices change live? | FR-03, V-03 | **Resolved:** None beyond active conversational model; no active-workspace switch (D-110). |
| PRD-Q-03 | When may a change occur and what work does it affect? | FR-03, NFR-03 | **Resolved:** Idle only, no queue; future turns of active conversation only, with other service bindings unchanged (D-112–D-113). |
| PRD-Q-04 | Is model selection saved? | FR-03, FR-02 | **Resolved:** Current run only; no YAML or preference write (D-114). |
| PRD-Q-05 | Does startup replay stay in scope? | FR-22, V-09 | **Resolved:** Yes, first full release (D-116). |
| PRD-Q-06 | Does `!<command>` belong in first-full-release input parity? | OOB-02 | **Resolved:** Defer (D-117). |
| PRD-Q-07 | How will releases be staged? | Release boundary, NFR-05 | **Resolved:** Tested preview alphas, then complete first full release; phase mapping follows in a separate plan (D-118). |
| PRD-Q-08 | Which physical terminals and sizes form UAT? | NFR-02, NFR-05 | **Resolved:** Terminal.app/arm64 and Ubuntu 24.04 GNOME Terminal/x86_64; 120×30, 80×24, and below-minimum resize (D-119). |
| PRD-Q-09 | When is the real provider/tool UAT case chosen? | NFR-05 | **Resolved:** Exact provider and executing tool at the pre-UAT gate, before final installed UAT (D-120). |
| PRD-Q-10 | What happens if a provider request fails through a newly selected model? | FR-03, FR-23 | **Resolved:** D-115 is superseded. Show the error, restore the prior model for future turns and do not automatically resend the failed prompt (D-121). |
| PRD-Q-11 | How do other provider/runtime failures affect a draft, tool effects and transcripts? | FR-20, FR-23 | **Resolved:** Before any tool runs, preserve the exact prompt/caret, attachments and newer draft for deliberate retry, with no failed-attempt transcript entry. After a tool runs, stop further steps, retain completed effects and Activity as an incomplete current-run turn, and write no incomplete-turn transcript entry (D-122). |

No PRD product-choice question remains open from this cohort. The exact real
provider/tool case and preview requirement mapping remain scheduled gate/plan
artifacts, not unmade product-scope decisions. Product review and acceptance of
this proposed PRD remain separate from the recorded decision answers.
