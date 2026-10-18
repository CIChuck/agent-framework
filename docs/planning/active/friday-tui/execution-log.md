# Friday TUI execution log

Status: Active design/planning; product implementation not authorized

execution_phase: planning; validation_state: not_ready

## 2026-10-16 — activation and build planning

Chuck Russell explicitly requested moving Friday TUI from queued to active,
constructing a build plan from the revised README, asking project questions and
opening a dedicated branch. Created `feature/friday-tui` from master `c3426986`,
carrying the existing uncommitted README revisions without discarding them.

Scope is design/planning only. Recorded the maintainer's scoped activation and
agent start with `implementation_authority: design_only`; the new draft plan is
not automatically approved. No product implementation, dependency installation,
commit, push, merge or publication is included.

Preserved requirements: current Friday Chat command parity; unchanged
`friday-cli` implementation/features/behavior; extensible `/` commands; separate
frontend state, adapters and command registration. Current source inventory is
50 canonical commands and three aliases; this count is not an evolution ceiling.

Moved the packet to `docs/planning/active/friday-tui/` and prepared the build
plan, tactical sequence, decision register, authority and source baseline.
Historical classification-ledger and frozen telemetry-evidence paths remain
historical; they are not rewritten during this activation.

The board transition helper grants full implementation authority by default;
its existing validated save/controller was used to preserve the narrower
`design_only` authority supported by the schema, without changing automation.
Priority remains 14. The maintainer-selected TUI planning task does not authorize
implementation of the separately queued Langfuse task returned by `next`.

Read-only source inspection identified mutating display-config activation,
missing operation-wide public stop/quit contracts, text-only status routing and
different startup/interactive replay semantics. They are TUI-00 design items.
Asked about OS support, multiline input and quit during mutations; answers are
recorded in the decision register as they arrive.

## Current stop point

Build plan and tactical sequence are draft. Product choices and the exact
integration contract must be reviewed before a product-code construction
directive is approved. Planning checks are pending; product behavioral tests
have not been run or claimed as passing for this documentation transaction.

## 2026-10-16 — planning transaction verified

Board/schema validation passed for all 34 tasks; generated dashboard is current.
README inventory reconciles to 50 canonical commands and three aliases. Source
hashes and protected CLI/Chat package trees are unchanged. Packet links/status,
JSON, whitespace and exact changed-path scope pass. Other board tasks and all
prior events remain unchanged. The full documentation checker reports only the
six unchanged historical telemetry VAL-001 temporary-checkout links. Results are
retained in `planning-checks.json`; they are planning checks, not a product
implementation or behavioral validation result.

The three product questions remain pending in `decisions.md`. Build and tactical
plans remain draft. Current stop point: review those choices and the build plan,
then approve exact TUI-00 construction scope before any product code generation.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — product decisions confirmed

Chuck Russell explicitly answered:

- Q-01: Support macOS and Linux initially.
- Q-02: Use a multiline editor with an explicit submit shortcut.
- Q-03: Quit at a safe stopping point, finishing any non-interruptible operation
  and cleaning up before exiting.

Recorded these as accepted choices in the decision register and planning
authority; synchronized README, acceptance criteria, build requirements and
tactical sequence. Concrete terminal/shortcut choices and operation-specific
safe stopping contracts remain TUI-00 technical work. Earlier planning-check
records remain unchanged as historical results; this update receives its own
planning check record.

Authority remains design_only. No product code, dependency, CLI behavior or
release change is authorized by these product answers. Current next gate:
finalize the TUI-00 technical integration contract, review the draft build plan
and approve exact construction scope before product code generation.
execution_phase: planning; validation_state: not_ready.

Decision-update checks passed: board/dashboard, changed-document links, source
hashes, JSON, whitespace and changed-path scope. Retained results in
`decision-update-checks.json`; product authority remains design_only.

## 2026-10-16 — concrete technical contract and first directive drafted

The maintainer requested proceeding through the technical integration decisions
and an explanation of the decision process. Prepared integration-contract.md,
T-01 through T-08 rationale, an actual-registry command/argument matrix and draft
CD-TUI-001. Synchronized README, build/tactical plans and the board's next gate.
Technical choices remain proposals; no product authority is granted by drafting.

Source inspection changed the proposed execution model from one UI loop to an
owned backend loop/thread: current async file handlers perform synchronous reads.
The worker keeps that work off the UI loop while preserving handlers and backend
ordering. Runtime construction/use/closure stays on its owning backend loop;
bounded ordered bridges carry input, output and metadata snapshots.

Proposed Quit closes admission, completes admitted work, then wakes the existing
input contract with EOF and waits for shared cleanup. This conservative safe
boundary can wait for a slow invocation; no generic mid-operation cancellation
is invented. The two proposed additive Chat APIs are a pure display-config
reader and immutable categorical shutdown report. CD-TUI-001 limits construction
to five Chat source/new-test paths, leaving CLI implementation, existing tests,
widgets, dependencies, metadata and all other packages outside the unit.

Textual 8.2.8 metadata and a dependency-only overlay resolve were inspected
without installation or workspace changes. The overlay retains the existing
rendering stack and adds Textual plus three transitive packages; it is not a
full workspace solve or UI compatibility proof. Proposed keyboard defaults use
Enter for newline, F2 submit with a focusable Submit fallback, and Ctrl+Q for
safe Quit. Startup replay is an isolated fake-runtime view; interactive replay
and existing CLI behavior stay under their current backend contracts.

The unchanged source baseline passed 241 tests: 155 CLI and 86 selected Chat.
Ruff and focused Mypy passed on app/display. Initial pytest collection collided
on duplicate test_display.py names; importlib collection corrected the harness
without edits or cache deletion. Preserved both logs. Existing editable package
metadata still identifies alpha3 while checkout source is alpha4, so these are
source tests, not a clean installed-release baseline. No environment sync ran.
Neither Textual execution nor Linux/real terminal behavior was tested.

Retained baseline, command metadata and resolution logs under validation/.
Original source-baseline.json, planning-checks.json and decision-update-checks.json
remain historical records. The new technical-contract-checks.json records this
planning transaction. No product implementation, commit, push, PR, merge, release
or publication occurred. Next gate: review the concrete contract/build plan and
approve CD-TUI-001's exact scope before granting product-code authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — continuous testing and UAT added to the build contract

Chuck Russell required testing as construction proceeds, testable phase subunits
and explicit UAT. Added test-and-uat-plan.md and the unit-to-PAR map. The proposed
breakdown has 24 bounded construction units, with behavior/failure/regression
checks and independent candidate review before dependent implementation.

Split draft CD-TUI-001 into 00A pure configuration and 00B shutdown reporting.
Each has its own exact path subset, acceptance cases, commands and frozen review
boundary; 00B uses verified 00A as its recorded base. No widget implementation
starts before both interfaces are verified. Package/dependency checks occur
when the package is first introduced and repeat for the final installed build.

Added AC-13 and FR-10, synchronized requirements/build/tactical/contract documents
and recorded D-05 as a maintainer requirement. The proposed five UAT checkpoints
start at the usable shell and cover 14 scenario groups, including rolling
command-family demonstrations, slow work, Quit, failure visibility, extension,
keyboard/resize and final installed macOS/Linux workflows. Formal user approval
is at the five milestone gates; blocking findings stop affected work when found.

UAT records identify tester, candidate/artifacts, terminal/environment, fixtures,
expected and actual results, defects and explicit checkpoint approval. Required
failed/blocked/unrun UAT cannot pass a gate. Technical VERIFIED and automated
headless/PTY tests do not replace real-user UAT or maintainer acceptance.

All future construction units and UAT scenarios remain not_run; no signoff,
implementation approval, test execution or live integration acceptance is
claimed by this planning amendment. Existing 241-test results remain historical
source-baseline evidence and were not rerun for documentation changes. Prior
planning receipts and baseline logs are retained unchanged. Current authority
remains design_only on feature/friday-tui; no product, dependency, existing test,
commit/push or delivery changes are included. Checks for this amendment are
recorded separately in incremental-testing-checks.json.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — shared runtime configuration boundary confirmed

Chuck Russell clarified that the configuration surface remains compatible
between CLI and TUI, with UI acting as UX over Friday runtime infrastructure.
Recorded fixed requirement D-06 and acceptance AC-14/FR-11. Both frontends use
the same current Chat configuration loader and runtime factory; runtime files
need no translation, duplication, rewriting or frontend-specific override layer.

The prior location/profile discussion remains a file-placement recommendation.
Optional TUI settings cover presentation only. Automatic discovery, new startup
precedence or setup generation remains a separate shared-contract proposal.
Current explicit --config selection and existing path/environment rules remain
controlling; portable profiles can use absolute configured data paths.

Reconciled an actual draft inconsistency: the earlier TUI-only rejection of
startup replay combined with config/runtime flags is withdrawn. Preserve the
existing version-then-replay-then-configured-startup precedence, including the
isolated default fake replay runtime and ignored options. Retaining a replay
result view is still a presentation choice. No existing CLI code changes.

Added CFG-01..06 to the startup test plan and shared-file/store-identity checks
to UAT-01 and UAT-05. The 24-unit/five-UAT breakdown remains intact. No future
case, user signoff, runtime test or implementation approval is claimed by this
planning reconciliation. Retained all earlier evidence unchanged; current
checks are recorded in shared-config-checks.json. Branch remains feature/friday-tui
with design_only authority; no product, config, dependency or release changes.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — existing CLI presentation file extension proposed

Chuck Russell asked to consider additional UX settings and specifically extend
the CLI configuration file used by Friday Chat. Recorded D-07 and FR-12/AC-15;
prepared ux-configuration.md with the current section inventory, additive YAML
example, mapping/validation rules, UXCFG-01..08 and UAT coverage.

The proposal keeps current theme/icons/prompt/response/banner/spinner fields and
adds an optional versioned tui namespace in the same --cli-config-selected file.
This supersedes the earlier separate tui-config.yaml suggestion. Proposed
settings cover appearance/accessibility, layout, editor, keybindings, output and
discovery; later notification/persistence/editing behavior needs separate scope.
Runtime configuration remains shared and cannot be overridden from UX settings.

Existing source selects known root sections and ignores additional ones. Three
isolated probes on disposable copies confirmed unchanged legacy framework/Chat
display values and byte-identical rendered assistant output with the proposed
namespace, an invalid TUI-only shape and an unknown TUI-only version (all valid
YAML). The CLI remains tolerant; a future TUI reader will validate its namespace
without imposing new validation on CLI startup. Malformed YAML follows existing
whole-file error rules. No user config or packaged template was modified.

All 47 existing tests in CLI test_cli_config.py and Chat test_display.py passed
using importlib collection, disposable fixtures and the prior offline guard.
Retained the profile/result and log in validation/ux-config-compatibility.json
and validation/ux-config-baseline.log. These are current-loader source checks,
not execution of a TUI schema/setting or real-user UAT.

Synchronized contract, README, build/tactical plans, decisions, authority and
startup/interaction UAT references. CD-TUI-001's exact five paths/two API units
remain unchanged; the later TUI-01A directive must bind the new settings reader.
The 24-unit/five-UAT breakdown remains intact; fields/defaults and all TUI UX
execution/signoff remain proposed/pending. Prior evidence is retained unchanged.
Current amendment checks are in ux-configuration-checks.json. Authority remains
design_only on feature/friday-tui; no product implementation or delivery change.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — UX configuration design accepted and documentation aligned

Chuck Russell agreed with the suggested CLI presentation-file extension and
requested that documentation match. Recorded approval of the existing file,
optional versioned tui namespace, compatibility boundaries and documented UX
option families. The separate TUI-file suggestion remains superseded.

Aligned ux-configuration.md, README, decision register, integration contract,
build/tactical/test plans and authority to distinguish accepted design from
pending construction. Example YAML remains a design reference; exact field
bounds, reader API and implementation paths must be bound in their directives.
Later notifications, persistent preferences/history and preference editing
remain deferred as stated. No new runtime override or CLI behavior change.

The approval is for this design, not the whole build plan or CD-TUI-001 product
scope, and is not implementation/UAT acceptance. Authority remains design_only
on feature/friday-tui. Existing 47-test/three-probe evidence and earlier receipts
remain unchanged; no runtime tests or UAT were rerun for this documentation
update. Current checks are retained in ux-design-approval-checks.json.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — documentation-review decisions and architecture reset

Chuck Russell chose normal slash-command dispatch for idle `/q` and `/quit`,
busy rejection with editor retention, semantic command parity with TUI-specific
presentation, automated Linux checks during construction with hands-on Linux
terminal UAT before first-release acceptance, and ongoing parity as Chat slash
commands evolve. He also chose an existing-file chooser when `--config` is
absent.

The maintainer clarified that `friday-tui` must be independently installable and
must not depend on any CLI code, including `friday-chat` and `friday-cli`. The
previous Chat-app/registry/handler integration architecture and both proposed
Chat APIs in CD-TUI-001 conflict with this boundary. Recorded the controlling
architecture-reset.md, withdrew that integration contract/directive, and marked
the old unit sequence as reference material pending a replacement plan. Existing
source probes and receipts remain historical evidence; they do not establish
TUI implementation or UAT. Authority remains design_only on feature/friday-tui;
no product, dependency, package metadata or release changes.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — TUI user documentation requirement added

Chuck Russell required a new TUI guide that explains actual operation,
interaction, commands and all associated everyday use, with configuration
guidance updated for the TUI. He specified a user persona and plain language.
Recorded D-14, AC-16 and user-guide-requirements.md. The guide will be drafted
alongside implemented behavior and verified against the final installed
macOS/Linux candidate through user UAT before acceptance. The detailed TUI
settings reference may live in 10-configuration.md or the TUI guide; one
location will own it and the other will link. Existing published guides remain
unchanged until there is an executable to document. Authority remains
design_only; no implementation or UAT result is claimed.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — TUI configuration reference placement confirmed

Chuck Russell agreed that docs/guides/10-configuration.md will own the detailed
`tui:` settings reference. The new TUI guide will explain task-focused setup
and link to that reference; the configuration guide will link back to operating
instructions. Recorded D-15 and updated the documentation requirements and
authority. This is a guide-placement decision, not a claim that either guide
already documents an implemented TUI. Product authority remains design_only.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — TUI screen layout proposed

At the maintainer's request, drafted screen-layout.md to make the visible UI
concrete before implementation: a compact header, optional context sidebar,
chronological scrollable conversation and command results, fixed multiline
editor/actions, and a concise status area. The proposal specifies prompt
submission, streaming in place, busy draft retention, independent scrolling,
help/palette overlays, responsive collapse, accessible controls and safe Quit.
It uses only the independent TUI/runtime boundary; no Chat/CLI package code is
an implementation dependency. Inline command results versus a separate result
pane remains a stated design choice for maintainer review. No UI was built,
tested or accepted by this planning draft; authority remains design_only.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — inline timeline and role colors accepted

Chuck Russell selected inline command results in the conversation timeline and
required different colors for user prompts and Friday responses. Updated the
screen proposal, D-16, AC-07, UX configuration tests and user-guide requirement.
Role labels and other visible distinctions accompany color for accessibility;
dark/light/high-contrast and terminal color behavior remain test/UAT work. The
exact accent palette and other layout details remain proposals. No TUI code or
user UAT was performed; authority remains design_only.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — pinned prompt and reasoning display direction recorded

Chuck Russell requested a fixed view of the latest accepted prompt while its
response scrolls below, and a future hide/show option for thinking content.
Recorded D-17/D-18, the pinned view in screen-layout.md and AC-07, and a
separate reasoning-display-requirement.md. Current Friday LLM typed responses
and events can carry provider-exposed reasoning; the Chat text adapter drops
those events from visible streaming. The TUI requirement uses a UI-neutral path,
keeps final-answer-only display as default, and does not change model
generation or CLI behavior. First-release timing for the reasoning option
awaits the maintainer's answer. No TUI code or UAT was performed;
authority remains design_only.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — first-release reasoning visibility confirmed

Chuck Russell answered that the provider-supplied reasoning display option is
required in the first TUI release. Updated D-18, AC-17, the screen,
configuration and user-guide requirements, architecture boundary and authority
record. The first-release default remains final-answer-only. Provider-exposed
reasoning is a distinct, bounded display when enabled; no CLI or runtime
generation behavior changes. The option and UAT are requirements, not completed
implementation or acceptance. Authority remains design_only.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — agentic tool-activity visibility requested

Chuck Russell requested a rolling TUI log of tool calls and their parameters
across multiple internal turns of an agentic loop. Recorded D-19 and
tool-activity-requirement.md, with a proposed in-exchange Activity section
and user-guide coverage. Source inspection distinguished provider-requested
tool-call events from actual execution. Current Friday Agent emits telemetry
but does not expose a complete UI-neutral tool-execution event contract; the
TUI must not import Chat or CLI loops. First-release timing and parameter
disclosure await maintainer answers. No product code or UAT was performed;
authority remains design_only.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — tool activity and later reasoning sequence clarified

Chuck Russell clarified that a model tool request is not proof of execution
and that the scrolling UI need not show tool-result payloads. Revised D-19,
added D-20, and updated the Activity, reasoning and user-guide requirements:
show actual tool invocations with parameters/status, omit result content, then
show only provider-exposed reasoning from subsequent model steps when the
reasoning view is enabled. The final answer remains separate. This is a
planning clarification, not a claim that every provider supplies reasoning
or that the TUI event seam is implemented. First-release tool-log timing and
parameter disclosure still await answers; authority remains design_only.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — first-release tool activity confirmed

Chuck Russell confirmed that the rolling Activity log belongs in the first
TUI release. Updated D-19, AC-18, the tool-activity requirement, architecture
contract, user-guide requirement and authority record. First-release tests
and macOS/Linux user UAT must cover actual tool invocations, parameters,
status and later provider-exposed reasoning without tool-result payloads.
The parameter-disclosure rule is the one remaining open question. This is a
planning decision; product implementation and UAT remain pending under
design_only authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — first-release parameter display confirmed

Chuck Russell answered that no credential or sensitive-value filtering is
needed for tool parameters at this stage; filtering may be considered later.
Recorded D-21 and updated AC-18, the Activity display, architecture and guide
requirements to show the parameters actually passed to each executed tool
without TUI masking. This does not change runtime tool policy or add parameter
persistence/export. The first-release scope and both open tool-activity choices
are resolved. Product implementation and UAT remain pending under design_only
authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — independent replacement plan and review answers reconciled

Chuck Russell answered the remaining documentation-review questions one at a
time. D-22 through D-30 record neutral extraction with separate Chat/TUI
handlers, in-process-only Activity, a forward-only reasoning toggle, the
manual `/run-tool` result exception, controlled real-provider/tool UAT,
manual and delegated tool Activity, separate emergency Force quit, and
rejected requests labeled `Not run` with their reason. D-20 now states the
automatic-tool-result rule explicitly.

The new [replacement plan](replacement-plan.md) is a draft independent
integration, construction and test/UAT path. It supersedes the withdrawn
Chat-dependent plans and directive as current planning guidance. The PRD,
architecture, screen, Activity, reasoning, UX configuration and user-guide
requirements were aligned to these decisions; the board's next gate points
to the remaining capability map and exact technical contracts.

This is planning work on `feature/friday-tui`. No product code, TUI package,
terminal UAT, real-provider test, publication, construction directive or
maintainer acceptance is claimed. Authority remains `design_only`.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — bounded oversized Activity parameters confirmed

Chuck Russell selected a bounded, explicitly truncated preview when one tool
parameter is too large for TUI Activity. The TUI discards the overflow instead
of retaining a hidden full copy. This does not mask credentials or change the
complete argument received by the tool. Recorded D-31 and aligned the PRD,
replacement plan, Activity requirement, screen, architecture, user-guide
requirements and authority record. Exact per-entry and total limits remain
technical-contract work; no implementation or UAT is claimed.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — rejected request boundary clarified

Chuck Russell chose to show `Not run` only when a model or user actually
requested a tool and execution was rejected before invocation. Tool selection
or budget exclusions before a request produce no `Not run` Activity entry.
Recorded D-32 across the product, architecture, Activity, screen, guide and
replacement-plan requirements, and corrected the active command inventory's
Chat-handler obligations to match independent TUI handlers. No product code,
UAT or construction approval is claimed.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — display clearing confirmed

Chuck Russell chose to make `/cls` and `/clearscreen` clear the displayed
conversation, pinned latest prompt and Activity view, while preserving
session history and saved data. Recorded D-33 and aligned the requirements,
screen layout, independent replacement plan, command matrix, user-guide
requirements and acceptance cases. The display returns no replacement text;
the pin resumes on the next accepted conversational prompt. No product code,
UAT or construction approval is claimed.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — transcript-session switch excluded from first release

Chuck Russell selected the existing-session inspection scope for the first
TUI release: display the current transcript session, retain `/sessions` and
`/transcript` behavior, and do not add a transcript-session switching
control. `/switch [agent]` retains its active-agent meaning. Recorded D-34,
removed the proposed session-switch Activity/UI contract and aligned the
command and guide requirements. Product construction, command parity tests
and UAT remain pending under `design_only` authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — visible Activity and reasoning copy confirmed

Chuck Russell selected copy of selected visible Activity entries and shown
provider reasoning. A truncated parameter contributes only its bounded preview
and notice; the TUI cannot copy overflow it discarded or reasoning received
while hidden. Recorded D-35 and aligned the product, Activity, reasoning,
screen, user-guide and replacement-plan requirements. Copy is user-initiated;
normal transcript/export behavior remains unchanged. No product code, UAT or
construction approval is claimed.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — history browsing and return control confirmed

Chuck Russell selected hiding the latest-prompt pin while browsing older
conversation and requested a clickable return-to-bottom control. Recorded
D-36: a visible, keyboard-focusable `Jump to latest` control returns to the
bottom, restores the pin when one exists and resumes following new output.
Scrolling back to the bottom has the same effect; new output does not move the
view while history is being read. Aligned the screen mockup, product, UX
configuration, user-guide, architecture, build-unit and UAT requirements.
No product code, UAT or construction approval is claimed.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — bounded history eviction behavior confirmed

Chuck Russell selected a visible notice when older conversation messages
leave the bounded on-screen view, with `/transcript` as the route to messages
that were saved. The UI must say when no saved transcript is available. There
is no first-release `Load older` control, and transient Activity or provider
reasoning must not be presented as recoverable transcript content. Recorded
D-37 across the product, layout, UX configuration, guide and replacement-plan
requirements. No product code, UAT or construction approval is claimed.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — editor key preference confirmed

Chuck Russell changed the first-release multiline editor keys to `Enter` for
submission and `Ctrl+Enter` for newline insertion. Recorded D-38, replacing the
withdrawn Enter/F2 proposal in the current product, layout, UX configuration,
user-guide and construction/UAT plan. Multiline paste must not submit, and
visible focusable Submit and Insert newline actions are required. Physical
key delivery on macOS and Linux terminals remains a UAT gate because some
terminals may not distinguish `Ctrl+Enter` from `Enter`; document and exercise
the fallback where necessary. No product code, terminal UAT or construction
approval is claimed.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — newline fallback confirmed

Chuck Russell selected option A for terminals that cannot distinguish
`Ctrl+Enter` from `Enter`. The first-release fallback is the visible,
clickable and keyboard-focusable Insert newline control; no second default
newline shortcut is assigned. Recorded D-39 across the product, layout, UX
configuration, user-guide and UAT planning documents. Physical terminal
behavior and control activation still require macOS and Linux UAT. No product
code or construction approval is claimed.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — slash-command palette selection confirmed

Chuck Russell selected option A: choosing a `/` command in the palette fills
and focuses the prompt editor for review and argument entry. Selection alone
does not run the command; the user submits it separately with `Enter` or the
Submit control. Recorded D-40 in the product, screen, UX configuration,
user-guide and testable construction plan. Existing-draft replacement
behavior remains a separate UI design choice. No product code, UAT or
construction approval is claimed.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — palette replacement of an unsent draft confirmed

Chuck Russell selected option A: when a palette `/` command would replace an
unsent editor draft, ask first. Cancel keeps the draft exactly; Confirm
replaces it and focuses the editor without running the command. An empty
editor fills directly. Recorded D-41 and aligned product, screen, UX
configuration, user-guide and construction/UAT evidence. Product code and
UAT remain pending under `design_only` authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — Activity first-entry visibility confirmed

Chuck Russell selected option A: Activity opens automatically with its first
entry so the agent/tool log is visible. The user can collapse and reopen it;
later entries accumulate while collapsed without forcing it open again.
Recorded D-42 in the product, Activity requirement, screen, UX configuration,
user-guide and construction/UAT plan. Auto-opening must not steal editor focus
or pull a reader away from older conversation. Product code and UAT remain
pending under `design_only` authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — collapsed Activity entry count confirmed

Chuck Russell selected option A: the collapsed Activity header shows how many
new entries arrived since collapse. The count increments for a newly appended
entry, not a status update to an existing entry, and resets on reopen or
`/cls`/`/clearscreen`. Bounded eviction remains visible so the count does
not suggest all entries are still inspectable: an indicator appears in the
collapsed header, with detail on reopen. Recorded D-43 across the
product, Activity requirement, screen, UX configuration, guide and test plan.
No product code or UAT is claimed; authority remains `design_only`.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — Activity scroll and return behavior confirmed

Chuck Russell selected option A: scrolling up within expanded Activity pauses
its following of new entries, leaving the earlier step in view. A visible,
clickable and keyboard-focusable `Jump to latest Activity` control, or
scrolling to the Activity bottom, resumes following. This control is separate
from the conversation's `Jump to latest` and must not move the conversation
or latest-prompt pin. Recorded D-44 across product, layout, Activity, UX,
guide and test/UAT planning. No product code or UAT is claimed; authority
remains `design_only`.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — Activity inline placement confirmed

Chuck Russell selected option A: the Activity log belongs inline within
the conversation exchange or user-entered tool-command entry that produced
it, ahead of the final response or command result. Its own scroll and
collapse controls keep a multi-step log inspectable on narrow terminals
without a persistent side pane. Recorded D-45 across the product, screen,
Activity requirement, UX configuration, guide and construction/UAT plan.
No product code or UAT is claimed; authority remains `design_only`.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — older Activity state across prompts confirmed

Chuck Russell selected option A: accepting a new conversational prompt
does not auto-collapse older inline Activity sections. Each retains its
chosen expanded or collapsed state while still in the bounded view, and
the new exchange's Activity opens independently on its first entry.
Recorded D-46 across product, screen, Activity requirement, UX
configuration, guide and construction/UAT plan. No product code or UAT is
claimed; authority remains `design_only`.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — source-backed neutral-capability map drafted

Mapped all 50 Chat slash commands and the additional `@agent`, `!` and
startup routes to proposed UI-neutral service seams. Source inspection
confirmed that Chat's configuration loader, runtime assembly, many typed
views and command effects remain in `friday-chat`; the headless
`RuntimeKernel` alone does not establish command/configuration parity.
Proposed a small first extraction of session identity into `friday-runtime`
with Chat compatibility re-exports and unchanged-frontend regression checks.
The map and first directive require review; no code change, product test,
UAT or construction approval is claimed.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — TUI runtime startup default confirmed

After the current `friday-chat --runtime` flag and fake default were explained,
Chuck Russell selected A: configured interactive `friday-tui` starts the
real provider-backed runtime unless `--runtime fake` is explicit. Recorded
D-47 across the product, replacement plan, capability map, UX configuration,
user-guide requirements and authority record. A failed real startup must not
silently switch modes. This affects only the planned TUI; existing Chat and
`friday-cli` defaults and behavior remain unchanged. No implementation or
UAT is claimed under `design_only` authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — chooser initial search location confirmed

Chuck Russell selected A: without `--config`, the first TUI chooser list
comes from the captured launch working directory, with a Browse action
for an existing runtime file elsewhere. No automatic user-directory or
recursive search is added; an explicit `--config` path bypasses the list.
Recorded D-48 in the product, architecture, replacement plan, capability
map, user-guide requirements and authority record. Candidate classification
and empty/invalid-file recovery remain to be bound. Existing CLI behavior,
product code and UAT are unchanged under `design_only` authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — chooser candidate types confirmed

Chuck Russell selected A after the roles of `config.yaml`, `models.yaml` and
`cli-config.yaml` were explained. The launch-directory list should show
likely Friday Chat runtime configuration YAML, including custom names, but
exclude recognized model-library and presentation YAML. Browsing still
accepts another existing path. Recorded D-49 in the product, architecture,
replacement plan, capability map, guide requirements and authority record.
The exact read-only classifier, empty list and invalid-file recovery remain
bootstrap-contract work. No product code or UAT changed; authority remains
`design_only`.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — invalid chooser selection recovery confirmed

Chuck Russell selected A: if an existing file selected through the interactive
chooser fails runtime-configuration validation, the chooser stays open and
shows an actionable error with Retry, Browse and Quit. Retry rereads the
selected path, allowing an external file correction. No runtime starts from
that invalid file. Recorded D-50 in the product, architecture, replacement
plan, capability map, guide requirements and authority record. Empty-list
behavior, exact candidate classification, explicit `--config` errors and
provider-startup failure UX remain to be bound. Product code, CLI behavior and
UAT are unchanged under `design_only` authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — invalid explicit config handling confirmed

Chuck Russell selected A: when an explicit `--config` file is invalid, the
planned TUI reports the configuration error and exits nonzero. It does not
open the chooser or start the runtime from that file. This matches the
direction of the current Chat explicit-config error path while preserving
the TUI's independent package boundary. Recorded D-51 in the product,
architecture, replacement plan, capability map, guide requirements and
authority record. The empty-list chooser case, exact candidate classifier
and provider-startup failure UX remain open. Product code, CLI behavior and
UAT are unchanged under `design_only` authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — empty initial chooser list confirmed

Chuck Russell selected A: with no likely runtime configuration in the
captured launch folder and no explicit `--config`, the chooser stays open,
says no configurations were found there, and offers Browse to another
existing file and Quit. It does not search elsewhere automatically, create
a file or start the runtime. Recorded D-52 in the product, architecture,
replacement plan, capability map, guide requirements and authority record.
The exact candidate classifier and real-provider startup failure UX remain
open. Product code, CLI behavior and UAT are unchanged under `design_only`
authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — chooser real-runtime startup failure confirmed

Chuck Russell selected A: if a chooser-selected configuration validates but
real-runtime startup fails, close partially started services, show the
startup error and return to the chooser with Retry of the selected file,
Browse and Quit. Do not silently use fake. Failed cleanup must be reported
without claiming that retry is safe; the exact failure-recovery mechanism
belongs in the lifecycle contract. Recorded D-53 across the active plan.
Explicit-path startup failure and exact chooser candidate classification
remain open. Product code, CLI behavior and UAT are unchanged under
`design_only` authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — explicit config real-runtime startup failure confirmed

Chuck Russell selected A: after a valid explicit `--config`, failed real
runtime startup cleans up any partial services, reports the failure and
exits nonzero. It does not open the chooser or silently use fake mode.
Cleanup failure must also be reported. Recorded D-54 across the active
plan. Exact chooser candidate classification and lifecycle cleanup-failure
mechanics remain technical-contract work. Product code, CLI behavior and
UAT are unchanged under `design_only` authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — chooser candidate detection approach confirmed

Chuck Russell selected A: the initial chooser list should use a shallow,
read-only look at YAML top-level structure so runtime files with custom
basenames can appear, while recognized model-library and CLI presentation
files are excluded. Unrecognized files remain accessible through Browse.
This inspection does not resolve credentials or start Friday. Recorded D-55
across the active plan. The exact runtime signature and filesystem edge
rules remain technical-contract work; no product code, CLI behavior or UAT
changed under `design_only` authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — combined startup and cleanup failure confirmed

Chuck Russell selected A: after a chooser-based real startup failure, if
cleanup of partial services also fails, report both failures, restore the
terminal as far as possible and exit nonzero. Do not offer in-process Retry
or Browse while resource state is uncertain. Recorded D-56 across the
active plan, acceptance checks and testable bootstrap unit. The exact
cleanup and terminal-recovery mechanism remains technical-contract work.
Product code, CLI behavior and UAT are unchanged under `design_only`
authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — startup bootstrap contract drafted

Consolidated accepted D-47 through D-56 into a draft
`startup-bootstrap-contract.md` with a proposed read-only chooser signature,
entry/failure outcome table and bounded bootstrap test groups. The proposal
uses the current Chat config shape and packaged runtime/model-library/display
examples as source evidence only; it grants no dependency on Chat code.
Exact parser bounds, neutral loader/resource-close owners and a construction
directive remain open. No product code, CLI behavior, UAT or release state
changed; authority remains `design_only`.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — incomplete runtime-shaped candidates confirmed

Chuck Russell selected A: a YAML file whose top-level structure looks like
Friday runtime configuration remains in the initial chooser list even when
incomplete, such as `llm:` without a required model. Full validation runs
after selection, with the D-50 error and retry path. Recorded D-57 in the
product and bootstrap contract, including its test matrix. Exact signature
and parser boundaries still need technical review. Product code, CLI
behavior and UAT remain unchanged under `design_only` authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — Browse path entry and folder navigation confirmed

Chuck Russell selected A: the chooser's Browse action supports both folder
navigation and typed or pasted paths to an existing runtime file. Absolute,
relative and `~` home paths are covered; relative entry resolves from the
folder shown in Browse, initially the captured launch directory. Missing or
invalid selections remain in the chooser with D-50 recovery. Recorded D-58 in
the startup contract, build unit, acceptance checks and future user-guide
requirements. Product code, CLI behavior and UAT remain unchanged under
`design_only` authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — on-demand chooser Refresh confirmed

Chuck Russell accepted the recommended visible Refresh action for the
no-`--config` chooser. Recorded D-59: Refresh rescans the captured launch
folder's runtime candidates on demand, allowing newly added, removed or
newly recognizable files to update the list, including empty-list recovery.
The chooser does not watch the folder or silently update the list. Refresh
does not validate a selected config or start services; D-50 Retry still rereads
the selected path independently. Updated the startup test matrix and future
user-guide requirements. Product code and UAT remain unchanged under
`design_only` authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-16 — linked runtime candidates confirmed

Chuck Russell accepted the recommendation to include a `.yaml`/`.yml`
symbolic link directly in the launch folder when it resolves to a readable
regular runtime-shaped file, even if the target is elsewhere. Recorded D-60;
broken, cyclic, unreadable, directory-target and unrelated links stay out of
automatic discovery but remain reachable through Browse and D-50 error
recovery. This adds no directory scan, full validation or runtime startup
during listing. Updated the bootstrap test matrix and user-guide requirements.
Product code, CLI behavior and UAT remain unchanged under `design_only`
authority.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — shared configuration loader proposal drafted

Inspected the current Chat application-config loader, distinct headless
`RuntimeConfig` parser, model-library path resolution, presentation-file
selection and Chat assembly path anchors. Drafted
`neutral-config-loader-contract.md` for one neutral Chat-compatible loader
under `friday-runtime` with a Chat public-API facade. Separated loader work
(TUI-N01A) from neutral effects/resource primitives (TUI-N01B), runtime
assembly (TUI-N01C) and launcher/chooser behavior (TUI-N03A). This is a
source-backed proposal, not a maintainer-approved API or directive.

Before any code change, 103 focused Chat/runtime configuration and CLI tests
and 155 `friday-cli` tests passed. These are characterization baselines, not
after-code regression evidence, installed-package verification or UAT. The
headless parser cannot be substituted for Chat runtime YAML as-is. Exact
facade/error behavior, neutral assembly and close ownership, shallow chooser
bounds and TUI runtime-mode environment handling remain open. Product code,
dependency metadata and existing CLI behavior were not changed;
`design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — Chat-only runtime-mode environment confirmed

Chuck Russell agreed that `FRIDAY_CHAT_RUNTIME` remains specific to the
existing `friday-chat` launcher. Recorded D-61: TUI configured interactive
startup ignores that variable for mode selection, defaults to real when its
own `--runtime` is omitted, and uses fake only when requested through its own
`--runtime fake`. The first-release TUI has no runtime-mode environment
override. This does not change runtime YAML environment interpolation,
credential lookup or Chat's current override. Added mode-isolation checks to
the bootstrap and acceptance plans. No product code or UAT changed;
`design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — startup replay result retention confirmed

Chuck Russell selected option A for startup replay: after a successful
`friday-tui --replay FILE`, keep a read-only result screen visible until the
user chooses Quit. Recorded D-62 and updated the startup contract, build
sequence, command-route inventory, acceptance criteria and future user-guide
requirements. The view shows at least the input file and processed-turn
count; it admits no prompts or `/` commands and does not enter a configured
interactive session. Version/replay/configuration precedence and isolated
fake replay behavior remain the Chat compatibility baseline. Exact per-turn
content and failure-view behavior still need a separate decision/contract.
No product code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — startup replay summary content confirmed

Chuck Russell selected option A for the completed startup replay screen:
show the input file and processed-turn count, without a browsable turn-by-turn
record in the first TUI release. Recorded D-63 across the startup contract,
build plan, acceptance criteria and future user guide. This limits the
result view only; replay execution, delay, D-62 read-only retention until
Quit and interactive `/replay` remain as specified. Failure presentation
is still open. No product code or UAT changed; `design_only` authority
remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — startup replay failure view confirmed

Chuck Russell selected option A for a failed startup replay: show the file
and actionable error in a read-only TUI screen until Quit, then exit nonzero.
Recorded D-64 across the startup contract, build plan, acceptance criteria
and user-guide requirements. The chooser and configured interactive session
do not open; the TUI does not silently retry or claim success. An explicit
Retry action and exact error/cleanup categories remain technical-contract
work. Existing Chat behavior is unchanged. No product code or UAT changed;
`design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — startup replay Retry excluded

Chuck Russell selected option A for no in-process Retry on a failed startup
replay and accepted the recommended remaining replay direction. Recorded D-65:
the read-only file/error screen offers Quit, then exits nonzero; after
correcting the cause, the user relaunches. This does not affect chooser Retry
or interactive `/replay`. The neutral service error mapping, partial-resource
cleanup and associated tests remain technical directive work; no additional
startup replay product-choice round is needed. No product code or UAT changed;
`design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — automatic slash-command suggestions confirmed

Chuck Russell selected option A for automatic command suggestions while
typing a leading `/`. Recorded D-66 across the screen layout, command plan,
acceptance criteria and user-guide requirements. Matches come from the TUI's
active command registry, including aliases; showing them has no editor or
command side effect and does not change accepted `Enter` submission behavior.
Suggestion-selection controls remain a separate interaction decision. No
product code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — inline slash-suggestion selection confirmed

Chuck Russell selected option A for choosing an inline suggestion to complete
the command token in the current editor draft, with a separate Submit step.
Recorded D-67 across the screen layout, build plan, acceptance criteria and
future guide requirements. Following argument text and editor focus stay in
place; selection has no command side effect. Exact keyboard and pointer
selection controls remain open. No product code or UAT changed;
`design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — inline suggestion keys confirmed

Chuck Russell selected option A for `Up`/`Down` highlighting and `Tab`
insertion while inline slash suggestions are open. Recorded D-68 across the
screen, build and guide plans. `Enter` always submits the editor draft;
without an open list, `Tab` moves focus. A list with no highlighted match
cannot insert. Terminal key behavior and focus need macOS/Linux UAT; pointer
and dismissal details remain technical UI work. No product code or UAT changed;
`design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — slash-subcommand suggestions confirmed

Chuck Russell selected option A for registered subcommand suggestions after a
recognized `/` command name. Recorded D-69 across command discovery, screen,
build, acceptance and future guide requirements. `/workflow r` can suggest
`run` from active TUI metadata; the existing highlight/Tab fill-only flow
applies to that token, while `Enter` remains Submit. Free-form argument values
are not suggested. No product code or UAT changed; `design_only` authority
remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — contextual slash usage hints confirmed

Chuck Russell selected option A for short usage hints once a `/` command or
subcommand is recognized. Recorded D-70 across command discovery, screen,
build, acceptance and future guide requirements. Hints derive from active TUI
metadata and show required/optional argument shapes, such as
`/workflow run` → `<name> [key=value ...]`; they do not fill values or run
commands. No product code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — editor-history content confirmed

Chuck Russell selected option A for editor history to include accepted
conversational prompts and submitted `/` commands. Recorded D-71 across the
screen, build, acceptance and future guide requirements. Recall fills the
editor for review and does not run an entry; unsent and busy-rejected drafts
and output are not submitted entries. This is separate from `/history` and
persisted transcripts. Restart persistence, other input routes, keys and
unsent-draft restoration remain open. No product code or UAT changed;
`design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — editor-history restart scope confirmed

Chuck Russell selected option A for editor recall history to last only while
the TUI is running. Recorded D-72 across the screen, build, acceptance and
future guide requirements. A new launch starts with an empty recall list even
when transcripts exist; no new history file or runtime-memory write is added.
Existing `/history`, transcript, Chat and `friday-cli` behavior is unchanged.
Other input routes, navigation keys and unsent-draft restoration remain open.
No product code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — editor-history draft restoration confirmed

Chuck Russell selected option A for preserving an unsent draft while browsing
editor recall history. Recorded D-73 across the screen, build, acceptance and
future guide requirements. Leaving history without submitting a recalled
entry restores the original draft and editing position exactly. Browsed
entries are editable copies and do not rewrite submitted history. Navigation
keys and additional input routes remain open. No product code or UAT changed;
`design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — editor-history boundary keys confirmed

Chuck Russell selected option B: `Up`/`Down` at the multiline editor's caret
boundaries traverse older/newer recall entries, instead of F3/F4. Recorded
D-74 across the screen, build, acceptance and future guide requirements.
Inside the editor, arrows move the caret; an open slash-suggestion list takes
priority under D-68. Moving newer past the last recalled entry restores the
unsent draft under D-73. Physical key/focus and wrapped-line behavior require
terminal UAT. No product code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — additional editor-history routes confirmed

Chuck Russell selected option A for accepted `@agent` messages and enabled,
admitted `!` commands to join current-run editor recall history. Recorded
D-75 across the screen, build, acceptance and future guide requirements.
Recalling either fills the editor without routing or executing it; disabled
or rejected routes are not submitted entries. The existing `!` enablement
policy and CLI behavior remain unchanged. No product code or UAT changed;
`design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — Context file browsing confirmed and file-context path checked

Chuck Russell selected option B: include folder browsing and file selection
in the first-release Context sidebar. Recorded D-76 and a separate testable
TUI-N04C unit with AC-19 and future user-guide coverage. Read-only source
inspection found that Chat `/read` displays file content, `/ingest` writes
vector memory, and configured `file_read`/smart-read tools can return file
content within a tool turn. None is a selected-file attachment carried into
the next prompt. Five focused existing file-command/tool tests passed. Adding
selected content to a TUI model turn requires an explicit product interaction
decision and UI-neutral runtime contract, without TUI imports from Chat or
`friday-cli`. No product code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — immediate attachment on file selection confirmed

Chuck Russell selected option B: deliberate file selection in the first-release
Context browser immediately initiates attachment to Friday's next eligible
model turn; there is no separate Add to context control. Recorded D-77,
AC-20, and distinct neutral-contract and UI test units TUI-N01D/TUI-N04D.
Keyboard focus movement and list scrolling are navigation, while click or
keyboard activation selects. Selection does not submit a prompt; attached or
failed status must be visible. The attachment lifetime beyond the next
accepted conversational turn, supported file types and size/budget policy
remain to be decided. No product code or UAT changed; `design_only` authority
remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — attached file retained across turns until removal

Chuck Russell selected option B: an attached file remains active in Friday's
TUI model context across later accepted conversational turns until the user
explicitly removes it. Recorded D-78 and updated the Context screen, neutral
contract unit, UI unit, AC-20 and future user-guide requirements. A visible,
keyboard-focusable Remove action affects future turns only; it does not edit
the source file, write memory or alter an already admitted turn. Behavior
across exit/relaunch and additional selected files remains open. No product
code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — attached files discarded on TUI exit

Chuck Russell selected option A: every new TUI run starts with no active
file attachments, even if an earlier transcript or runtime session is
available. Recorded D-79 across the Context screen, neutral build unit,
UI unit, AC-20 and future user-guide requirements. Attachments remain active
across turns during a run under D-78, but are not restored from configuration,
memory, transcripts or a new attachment-history file. Additional-file behavior
remains open. No product code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — multiple distinct file attachments confirmed

Chuck Russell selected option A: selecting another distinct file adds it
alongside the current attachment rather than replacing it. Recorded D-80,
individual Remove controls and two-file cases in the neutral/UI build units,
AC-20, screen and future guide requirements. A later accepted turn must
receive both until one is removed; removing one leaves the other active.
Duplicate selection of the same file and aggregate context-budget behavior
remain open. No product code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — selection-time file snapshot confirmed

Chuck Russell selected option A: Friday keeps the file content captured when
the user deliberately selects it, rather than rereading before every later
prompt. Recorded D-81 across the neutral/UI build units, AC-20, screen and
future guide requirements. Selecting the same file again refreshes that
attachment in place without duplication; a failed refresh shows an error
and leaves the last successful snapshot available. Tests must cover source
edits/deletion after selection and successive turns. Format, size and
aggregate context-budget choices remain open. No product code or UAT changed;
`design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — first-release file-content formats confirmed

Chuck Russell selected option B: the first TUI release attaches real content
from readable text/code/text-data files and from PDF, DOCX and XLSX files.
Recorded D-82 and added the neutral extraction unit TUI-N01E and AC-21.
The source inventory found `friday-tools` reader candidates for the three
document formats, while Chat `/read` still returns placeholders for them.
Seven focused existing reader tests passed, but the PDF test does not prove
positive text extraction; the future construction unit needs genuine positive
fixtures and installed-dependency checks. Scanned-PDF OCR, spreadsheet scope,
file size and aggregate context budget remain open. Chat/`friday-cli` behavior
must stay unchanged. No product code or UAT changed; `design_only` authority
remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — Tesseract OCR for scanned PDFs confirmed

Chuck Russell selected option B and specified Tesseract. Recorded D-83:
first-release selected-file attachment must obtain actual recognized text
from scanned/image-only PDFs and carry it through the same snapshot/model
context path as other attachments. Added separate neutral OCR unit TUI-N01F
and AC-22, with positive image-only PDF/model-input evidence, negative
renderer/OCR/language/empty/timeout cases, installed macOS/Linux checks and
Chat/`friday-cli` regression protection. The existing Friday PDF reader uses
pypdf embedded-text extraction only; no OCR or PDF page-rendering attachment
path was found. Tesseract is installed on this Mac, but that does not verify
the future installed TUI or Linux environment. Mixed-page policy, OCR
languages, dependency distribution and size/time limits remain open. No
product code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — mixed-PDF page routing confirmed

Chuck Russell selected option A for a PDF with selectable-text and scanned
pages. Recorded D-84: use usable embedded text on a page, run Tesseract only
for pages lacking it, and combine page content in original order without
duplicate OCR text. Expanded TUI-N01F and AC-22 with separate page-routing
checks and a genuine mixed-PDF fixture that verifies actual model input.
The exact usable-text criterion and partial-page failure handling remain to
be bound; this answer does not choose whole-file failure or partial success
when one page cannot be read. No product code or UAT changed; `design_only`
authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — system-installed Tesseract confirmed

Chuck Russell selected option A: first-release macOS/Linux users install the
Tesseract executable separately; the TUI package does not bundle, fetch or
auto-install it. Recorded D-85 across OCR acceptance, the neutral OCR unit,
screen behavior and future user-guide requirements. A missing executable
must produce an actionable error only when OCR is needed; text and
embedded-text attachment remain usable. Installed-package tests must cover
both missing and present Tesseract, plus correction and relaunch. Distribution
of the PDF page renderer, OCR languages and mixed-page failure policy remain
open. No product code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — required OCR-page failure rejects PDF attachment

Chuck Russell selected option A: if an otherwise readable PDF contains a
page that needs OCR and that page cannot yield usable text, the entire new
PDF attachment fails. Recorded D-86. The TUI must identify the failed page
and cause without sending partial PDF content to a later model turn.
A failed refresh keeps the last complete snapshot and error status; other
attachments remain active. Expanded TUI-N01F and AC-22 with a mixed PDF
fixture whose middle scanned page fails, plus model-input and refresh
checks. OCR language, renderer distribution, usable-text criterion and
size/time budgets remain open. No product code or UAT changed;
`design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — configurable installed OCR languages confirmed

Chuck Russell selected option B: PDF OCR defaults to English and lets TUI
users select one or more installed Tesseract language packs through the
common presentation file. Recorded D-87 and proposed
`tui.attachments.ocr_languages: [eng]` in the additive configuration design.
The TUI validates setting shape; a missing requested pack is named when OCR
is needed, with no silent English fallback or partial PDF attachment. Added
configuration and installed-OCR checks to TUI-N01F/N03A, AC-15/AC-22 and the
user-guide requirements. This Mac currently lists `eng`, `osd` and `snum`;
non-English installed-pack UAT requires a prepared environment. Renderer
distribution, text-usability criteria, language-code bounds and size/time
budgets remain open. No product code or UAT changed; `design_only` authority
remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — PDF page renderer included with TUI package

Chuck Russell selected option A: the independently installed `friday-tui`
must supply the cross-platform PDF page renderer needed before Tesseract OCR
through a declared package dependency. Recorded D-88. Fresh wheel/sdist
installation checks on macOS and Linux must prove scanned-PDF rendering
without a separate renderer installation. Tesseract and its selected language
packs remain system-installed. The exact rendering library, licensing and
platform/native dependency behavior require a bounded construction decision.
No package dependencies, product code or UAT changed; `design_only` authority
remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — all XLSX worksheets in TUI attachment confirmed

Chuck Russell selected option A: a selected `.xlsx` workbook contributes
content from every worksheet, labeled by sheet name, in workbook order. D-89
makes that one attachment snapshot and includes non-active and hidden sheets.
The current `friday-tools` reader defaults to the active sheet, though it
accepts explicit sheet selection; the TUI's neutral extraction path must
enumerate sheets without importing or changing Chat/CLI handlers. N01E and
AC-21 now require a genuine multi-sheet fixture, non-first active sheet,
distinct hidden-sheet content and proof in actual model input. Formula
representation, sheet-read failure semantics and size/context limits remain
open. No product code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-17 — unreadable XLSX sheet rejects workbook attachment

Chuck Russell selected option A: if any sheet cannot be read, reject the whole
new workbook attachment with the worksheet and cause named. Recorded D-90.
No partial workbook text enters a model turn; a failed refresh keeps the last
complete snapshot and other attached files remain active. A readable blank
sheet is not itself a read failure, while an all-empty workbook cannot count
as attached content. Expanded N01E and AC-21 with a failing middle-sheet
fixture, actual model-input absence and failed-refresh checks. Formula
representation and size/context limits remain open. No product code or UAT
changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — XLSX formula and saved-result content confirmed

Chuck Russell selected option A: attached workbook formula cells supply both
the original expression and any result saved in the workbook, distinctly
labeled with the sheet and cell. Recorded D-91. If no saved result exists, the
formula remains visible and the missing saved result is explicit; the TUI does
not calculate or fabricate a result. The current reader's `data_only=True`
path yields saved results alone. N01E and AC-21 now require a neutral
formula-aware extraction path and fixtures with numeric/text saved values and
an absent saved value, checked in actual model input. Chat/CLI behavior stays
unchanged. Size/context limits remain open. No product code or UAT changed;
`design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — oversized file attachment rejection confirmed

Chuck Russell selected option A: a selected file whose extracted content
exceeds the TUI's per-file attachment bound is rejected as a whole with a
visible size-limit message. Recorded D-92. No partial excerpt becomes an
attachment or model input; a failed refresh preserves the last complete
snapshot and other files remain attached. N01D/N01E/N01F and AC-20/21/22
now require under/over-bound and reader-truncation checks, including the
existing XLSX reader's default 1,000-data-row cap. Exact measurement and
threshold, raw-file/processing safeguards and aggregate context budget need
later contract decisions. No product code or UAT changed; `design_only`
authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — combined attachment budget rejection confirmed

Chuck Russell selected option A: if a new file would exceed the combined
active-attachment budget, reject that file and retain all existing attached
snapshots. Recorded D-93. The user can remove a file and retry; no automatic
eviction, replacement or partial inclusion occurs. A refresh that would exceed
the total keeps its previous complete snapshot with a visible limit error.
N01D/N01E and AC-20/21 now require tests with individually valid files that
exceed the budget together, unchanged model input after rejection, manual
removal and retry, and failed-refresh retention. Exact aggregate measure,
threshold and runtime context reservation remain contract work. No product
code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — configurable attachment limits confirmed

Chuck Russell selected option A: the first-release per-file and combined
attachment bounds are optional, typed TUI-only settings under `tui.attachments`
in the existing shared presentation file, with safe defaults. Recorded D-94.
The existing CLI values, parser behavior and Friday runtime configuration stay
unchanged, and the TUI reader does not import Chat/CLI loaders or rewrite the
file. Updated the UX configuration design, N01D/N03A, AC-15/20 and the user
configuration-guide requirements for omitted/default, valid custom and invalid
setting tests. Exact setting names, measurement units and numeric bounds need
later construction decisions. No product code or UAT changed; `design_only`
authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — estimated-token attachment limits confirmed

Chuck Russell selected option A: express both first-release attachment limits
in estimated tokens. Recorded D-95. Count the complete formatted attachment
text that reaches model input, including file/sheet labels, OCR and formula
content; count a proposed refresh as a replacement, not a second copy. Token
estimates may differ from provider counts and do not replace runtime context
budgeting. Updated the configuration design, neutral admission/extraction
units, AC-15/20 and user-guide requirements with deterministic estimator
boundary tests and estimated-token error wording. The exact estimator,
headroom, field names and numeric defaults/thresholds remain contract work.
No product code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — fixed attachment-limit defaults confirmed

Chuck Russell selected option A: omitted per-file and combined attachment
limits use fixed conservative estimated-token defaults across models and
providers. Recorded D-96. Known or unknown model context metadata and model
switches do not recalculate these TUI admission defaults; explicit valid
settings still override them. Friday runtime context budgeting remains
separate, and the defaults do not guarantee every turn fits. Updated the
configuration design, neutral-capability map, build units, acceptance and
user-guide requirements to test identical defaults/admission outcomes with
different or unknown model metadata. Exact numeric values, estimator, override
ranges and headroom remain contract work. No product code or UAT changed;
`design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — attachment-limit default values confirmed

Chuck Russell selected option B: set omitted TUI attachment limits to 4,000
estimated tokens per file and 8,000 estimated tokens combined. Recorded D-97.
Exactly-at-limit content is admitted; above-limit content is rejected whole
under D-92/D-93. The defaults remain fixed across models under D-96, while
valid explicit settings override each limit independently. These values can
consume nearly an 8,192-token model window before other context, so selected
attachments do not guarantee that a later turn fits. Updated configuration,
capability, build-plan, acceptance and user-guide requirements with numerical
boundary tests. Exact field names, estimator, allowed override ranges and
turn-level context behavior remain open. No product code or UAT changed;
`design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — initial turn over-budget rejection confirmed

Chuck Russell selected option A: after normal Friday context assembly, reject
a first provider request that exceeds the selected model's effective input
budget before calling the provider. Recorded D-98. The TUI shows estimated
total, available budget and overage while preserving the exact editor draft
and attachments for correction; the rejected attempt creates no accepted
turn, transcript/editor-history entry, prompt pin, provider call or tool
effect. This is a UI-neutral admission boundary for the TUI, not a change to
Chat/CLI behavior or runtime configuration. Added a separate N01G testable
unit and AC-23 with deterministic boundary, side-effect and installed-UAT
checks. Exact estimator/reserve, provider rejection after a passing estimate
and later agent-loop overage remain open. No product code or UAT changed;
`design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — older-turn compaction recovery confirmed

Chuck Russell accepted the recommended first-release recovery: when an initial
or later agent-loop conversational model request is over budget, use one
eligible attempt through Friday's configured older-turn compaction service,
then reassemble and recheck that request. Recorded D-99 and refined D-98,
N01G and AC-23 so their no-provider/no-side-effect wording applies to the
blocked conversational request, not to maintenance. A compaction run can use a
separate model and persist memory changes. Added N01H and AC-24 for disabled,
unavailable, ineligible, successful and ineffective paths, including a later
step after a tool has run. No new active-loop compaction is in first release.
No product code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — post-estimate provider context rejection confirmed

Chuck Russell selected option A: if Friday's estimate passed but a provider
reports a recognizable context-length rejection, show the provider error and
leave correction and retry to the user. Recorded D-100, AC-25 and a separate
N01I testable unit. An initial submitted draft and attachments remain available
for correction without overwriting a newer unsent draft; a later failure after
tools marks the turn incomplete and retains their Activity and effects. No
TUI-triggered compaction or resend follows this post-send error. Friday's
existing LLM transport retry policy and Chat/`friday-cli` behavior remain
unchanged. Current `friday-llm` telemetry only groups bad requests under a
broad `invalid_request` category; exact context-length classification,
provider-detail display, transcript treatment and draft-recovery placement
need a construction contract. No product code or UAT changed; `design_only`
authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — failed prompt editor recovery confirmed

Chuck Russell selected option A for a first request rejected by the provider
for context length after a passing Friday estimate. Recorded D-101 and AC-26:
restore the exact submitted prompt and caret automatically if the editor is
empty; if the user typed a newer draft during the request, leave it untouched
and show a visible Restore action. The action uses D-41's Confirm/Cancel
replacement pattern and never submits. Updated N01I/N03B/N04A tests for empty
and occupied editors, attachment preservation and terminal UAT. Action
lifetime under view eviction and transcript treatment remain construction
contract work. No product code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — failed initial request transcript exclusion confirmed

Chuck Russell selected option A: a first conversational request rejected by
the provider for context length after a passing estimate leaves no persisted
failed-attempt transcript entry. Recorded D-102 and AC-27, with separate N01J
neutral persistence tests. D-101's error and failed prompt remain recoverable
in-process during the current TUI run; relaunch does not recover them from a
transcript. A corrected successful user submission is a distinct turn recorded
once. This does not erase provider telemetry or completed compaction effects.
Later agent-loop failure after tools remains a separate persistence decision.
No product code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — later incomplete-turn transcript exclusion confirmed

Chuck Russell selected option A for a later agent-loop context failure after
one or more tools have executed. Recorded D-103 and AC-28 with a separate N01K
neutral persistence test unit. Both local overage after D-99 compaction/recheck
and post-send provider rejection under D-100 stop further loop work, show an
incomplete turn and retain prior Activity only in the bounded current TUI run.
No incomplete-turn transcript entry is written, including a prompt/status-only
record or serialized Activity. Existing completed transcripts stay intact;
already executed tool effects, provider telemetry and compaction memory effects
are not rolled back. No product code or UAT changed; `design_only` authority
remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — failed-prompt Restore location after notice eviction confirmed

Chuck Russell selected option A: if a failed initial provider-context error
notice leaves the bounded conversation, keep `Restore failed prompt` beside the
editor while that prompt remains recoverable in the current TUI run. Recorded
D-104 and AC-29. The action is pointer- and keyboard-accessible, does not steal
editor focus, and appears only for a recoverable failed prompt. D-41/D-101
Confirm/Cancel still protects a newer draft; restoring never submits or calls
the provider. Updated the screen layout, user-guide requirements, neutral
capability map and N03B/N04A UI tests for eviction and narrow layouts.
Explicit `/cls` treatment of editor recovery remains a separate decision.
No product code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — failed-prompt recovery after display clear confirmed

Chuck Russell selected option A: `/cls` clears the displayed conversation,
pin and Activity but keeps a still-recoverable failed initial prompt and its
`Restore failed prompt` action beside the editor during the current TUI run.
The `/clearscreen` alias and bound display-clear shortcut have the same rule.
Recorded D-105 and AC-30; updated the existing D-33/D-104 boundaries, screen
layout, user-guide requirements, neutral map and N03B/N04A UI tests. The
cleared error notice does not become a transcript record, and Restore still
uses D-41/D-101 Confirm/Cancel without resubmitting. Behavior after a separate
successful prompt or explicit dismissal remains a later decision. No product
code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — successful newer turn clears older failed-prompt recovery

Chuck Russell selected option A: when a different conversational turn completes
successfully, clear the older failed initial prompt's in-process recovery and
remove `Restore failed prompt` from the editor and any retained error notice.
Recorded D-106 and AC-31. Admission and partial output do not clear recovery;
a newer failed turn or slash command alone does not clear it. A retained old
error remains non-actionable bounded display, with no failed-attempt transcript
record. Updated the screen layout, guide requirements, neutral map and
N03B/N04A test units for pending, failed and successful outcomes. Multiple
simultaneous recoverable failures and explicit dismissal remain separate
decisions. No product code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — multiple failed-prompt Restore chooser confirmed

Chuck Russell selected option A for multiple pending failed initial
provider-context prompts. Recorded D-107 and AC-32: one compact
`Restore failed prompts (N)` control beside the editor opens a chooser of
distinct recoverable prompts, newest first. One pending prompt uses the singular
control; none shows no control. Opening, browsing or canceling the chooser
leaves a newer editor draft unchanged; selecting a prompt still uses D-41/D-101
Confirm/Cancel without submission. Updated screen layout, guide requirements,
neutral capability map and N03B/N04A UI tests for two failures, focus,
view clearing and narrow terminals. Disposition after confirmed restoration
and a pending-count cap remain separate decisions. No product code or UAT
changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — confirmed Restore retains pending original until success

Chuck Russell selected option A: confirming Restore copies a failed prompt into
the editor but keeps its exact original pending in the current-run recovery
set. Recorded D-108 and AC-33. The chooser count and order do not change or
duplicate; later editor edits or replacement cannot mutate the recoverable
snapshot, and the user can restore it again. Only a successful conversational
turn clears all earlier pending recoveries, whether that turn uses the restored
prompt or another prompt. Cancel, partial output, failed turns, slash commands
and display clearing do not. Updated screen layout, guide requirements,
neutral capability map and N03B/N04A tests for repeated Restore, count and
transcript boundaries. Explicit dismissal and a pending cap remain separate
decisions. No product code or UAT changed; `design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — explicit failed-prompt Dismiss confirmed

Chuck Russell selected option A and asked to stop spending time on failed-prompt
options. Recorded D-109 and AC-34: each recoverable failed prompt offers a
confirmed Dismiss action, removing only the selected current-run snapshot while
leaving the editor draft/caret, including a restored copy, and attachments
unchanged. The pending count and Restore controls update immediately; no
provider request or failed-attempt transcript write occurs. Updated screen,
guide, neutral-capability and N03B/N04A test requirements. A finite count/size
bound and deterministic overflow behavior belong in the construction
directive as implementation details, not another maintainer product question.
Planning checks only; no product code or UAT changed. `design_only` authority
remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — TUI-N00 source review and first directive drafted

After the maintainer said to proceed to core integration work, rechecked
`feature/friday-tui`, source revision `c3426986`, the board's `design_only`
authority and the 50-command matrix. The saved command names, three aliases,
usage and argument metadata match the live Chat registry; all 50 PAR cases
remain in the neutral-capability map. Read-only baseline checks passed: 108
focused Chat/Runtime tests and 155 `friday-cli` tests. The installed workspace
`friday-chat` launcher reports `0.1.0a4` and help; the existing `friday`
console entry exits with an `app` import error from `friday_cli.main`. These
outcomes are a before-code baseline, not TUI or outside-checkout wheel proof.

Recorded source-backed configuration, event and cleanup gaps in
`n00-integration-review.md`; refined the neutral loader proposal with a
diagnostic-rules parameter to preserve Chat's monkeypatch seam. Added a
separate neutral event/lifecycle proposal with source boundaries and test
gates for later units. Drafted
`CD-TUI-N01S-session-identity.md` with exact paths, behavior, tests and stop
conditions for the first independent neutral extraction. The directive is
proposed, not approved; no product code, dependency, CLI behavior or UAT
changed. Later loader, assembly, event and lifecycle units remain separately
scoped. TUI packet links and board validation pass. The repository-wide
documentation lifecycle checker remains failed on six pre-existing absolute
links in the separate Friday telemetry review packet; that file is unchanged.
`design_only` authority remains.
execution_phase: planning; validation_state: not_ready.

## 2026-10-18 — CD-TUI-N01S approved for identity-only implementation

Chuck Russell answered "approved, proceed" to the explicit question approving
CD-TUI-N01S and granting implementation authority for that session-identity
slice only. Recorded the bounded grant in the directive, `authority.json` and
board. The permitted product paths are the new Runtime identity module, the
Chat session re-export module, and the new Runtime identity tests. All other
TUI units remain design-only; no TUI release or UAT is implied. The next gate
is local implementation, regression checks and fresh-context independent
validation of a frozen candidate.
execution_phase: implementation; validation_state: not_ready.

## 2026-10-18 — TUI-N01S identity candidate implemented and locally checked

Moved the immutable identity type, mismatch exception and resolver without
behavior changes to `friday_runtime.session_identity`; `friday_chat.session`
re-exports the same objects and retains `FridaySession`. Added focused Runtime
tests for generation, validation, injection, mismatch, old Chat import/pickle
class lookup and the neutral import boundary. No `friday-cli`, Chat command,
package metadata, dependency or TUI implementation file changed.

Local checks: 117 focused Chat/Runtime tests and 155 `friday-cli` tests passed.
With local loopback enabled, all 324 Runtime tests passed and all 828 Chat
tests passed (five skipped). Focused Ruff and Mypy on the three allowed files
pass. Both affected wheels built, and importing them from a temporary install
outside the checkout preserved the neutral import closure and Chat class
identity; dependencies for that smoke were supplied by the existing workspace
environment. `friday-chat --version` still reports `0.1.0a4`, its help exits
zero, and `friday --help` retains its pre-existing `friday_cli.main.app` import
failure. Repository-wide Ruff still reports 534 existing errors outside the
three changed files; focused changed-file lint passes. No user UAT applies to
this identity-only slice. Freeze a candidate commit and seek fresh-context
independent validation before claiming verification or completion.
execution_phase: validation; validation_state: pending.
