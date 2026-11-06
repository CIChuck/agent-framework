# Friday TUI draft phase build plan

**Status:** Draft for a joint maintainer review of the vision, PRD, and this
plan. Phase boundaries and preview labels are proposals, not accepted release
commitments. This document does not approve construction, UAT signoff, a push,
or publication.

**Date:** 2026-10-19

**Initiative and branch:** `friday-tui` on `feature/friday-tui`

**Phase objective:** Reach the complete first full release through installed,
user-visible increments, each with a bounded failure case, compatibility
evidence, and an explicit exit gate.

## Source authority and planning position

The proposed vision draft (`../vision/README.md`) defines outcomes V-01–V-09. The
proposed PRD draft (`../prd/README.md`) defines FR-01–FR-23 and NFR-01–NFR-05. Both
await the requested joint review. The [accepted decisions](../decisions.md),
[detailed AC-01–AC-36 cases](../README.md#8-acceptance-and-verification),
[50-command matrix](../command-handoff.md#command-matrix), and accepted product boundaries in
the [architecture reset](../architecture-reset.md) constrain this draft. The
[replacement plan](../replacement-plan.md) and
[neutral-capability map](../neutral-capability-map.md) supply source-backed
unit ideas and historical evidence; their old ordering is not a new release
commitment. The [board](../../../board.yaml) controls current work state and
implementation authority. Repository engineering, task-lifecycle, and
independent-validation policies apply to later code units.

The [shared command refactor](../command-handoff.md#command-initiative)
is a separate queued initiative. Its accepted result is a dependency for P5
command integration; this TUI plan does not authorize extraction of Chat
command handlers or changes to the separate `friday-framework-cli` package.

The planner skill names `docs/methodology/constitution/gendev.md` as a
governing standard when available; that file is absent in this checkout. No
accepted TUI G3 architecture specification was found. This draft mirrors the
accepted architecture-reset boundaries and flags the missing formal
architecture acceptance below. It must not turn a proposed neutral API into
an approved implementation contract.

The current installed `friday-tui` is a no-backend shell. N03A-01 has an
implemented candidate, but its [first independent review](../validation/VAL-N03A-01-first-f921eb4c.md)
requested packet reconciliation and physical macOS terminal UAT. The
[board next gate](../../../board.yaml) calls for a fresh read-only review of
the corrected candidate; the physical UAT remains open. Earlier neutral
config, identity, transcript, and Linux CI subunits have their own recorded
evidence, but none establishes a working TUI conversation.

## Coverage contract and release rule

- **Included:** The first full release covers every PRD baseline requirement
  FR-01–FR-23 and NFR-01–NFR-05, all applicable accepted AC cases, every
  maintained command/alias in PAR-001–PAR-050 as reconciled with the accepted
  separate command refactor, and `@agent_name` routing. The 50 rows remain the
  before-change baseline; retained-command parity and approved retired-name
  behavior close different cases.
  The exact effects and error paths matter; a visible command name or a green
  headless test alone is not completion.
- **Included:** Preview alphas may expose tested subsets. Each preview must
  state its supported workflows, incomplete PRD coverage, known limits, and
  actual UAT evidence. A preview is an installed artifact, not a claim of
  first-full-release acceptance. The proposed alpha count and distribution
  remain review choices.
- **Included across every phase:** `friday-tui` is independently installable
  and uses UI-neutral Friday runtime/services with the same runtime files,
  service interpretation, and storage paths as Friday Chat. It never imports
  or depends on `friday-chat` or `friday-cli`. Existing Chat and `friday-cli`
  behavior and installation must remain unchanged, including after shared
  service extraction. Maintained `/` commands ultimately use one shared,
  UI-neutral definition and execution path; no phase may add a duplicate TUI
  handler for an exposed maintained command. Runtime tool/security policy
  remains authoritative.
- **Deferred:** Optional `!<command>` input, active-workspace switching,
  additional live runtime-setting editors, persisted editor recall,
  transcript-session switching, `Load older`, reasoning/Activity export, and
  TUI-specific tool-parameter filtering. These require separate future scope
  decisions; none is a hidden phase deliverable.
- **Out of scope:** Replacing either CLI, creating a second runtime YAML
  dialect or preference file, silently rewriting shared configuration,
  inventing provider reasoning, treating a requested tool as executed, or
  changing Friday LLM transport retry policy.
- **Blocked for approval, not for drafting:** Vision/PRD acceptance, a formal
  architecture mirror decision, and phase-specific technical contracts must
  be reconciled before this plan can authorize a tactical plan. No future
  phase gains code authority merely by appearing here.

## Proposed sequence and requirement ownership

"Primary completion" names the phase that must close the listed PRD criteria.
Earlier phases may exercise a smaller slice; later phases must rerun affected
integration and regression cases. All phase exits remain provisional until
the three-document review accepts their boundaries.

| Phase | User-visible outcome and proposed gate | Primary completion | Vision |
| --- | --- | --- | --- |
| P0 — Shell baseline | Reconcile the existing installed shell candidate and complete its required review and macOS terminal observation. No preview claim. | Existing N03A-01 only; no full PRD row closed by a no-backend shell. | V-08 |
| P1 — Connected Friday | **Preview alpha 1:** choose an existing configuration, start real Friday, submit and answer successive prompts, recover from an initial failure, and quit without losing accepted work. | FR-01, FR-02, FR-05, FR-06; first-turn slices of FR-18, FR-20, FR-21, FR-23. | V-01, V-06, V-07, V-08 |
| P2 — Live model and request control | **Preview alpha 2:** change the active conversational model while idle; use it for future turns, restore the previous model after a failed request, and exercise budget/failure contracts. | FR-03; core slices of FR-18, FR-19, FR-20 and FR-23, completed with later UI and file integration. | V-03, V-05, V-06 |
| P3 — Inspectable session | **Preview alpha 3:** navigate the accepted screen, inspect actual Activity and optional provider reasoning, recover after post-tool failures, recall editor submissions, and exit safely during long or stalled work. | FR-07, FR-11, FR-12, FR-13, FR-19, FR-20, FR-21, FR-23; presentation slice of FR-04. | V-01, V-04, V-06 |
| P4 — Selected-file context | **Preview alpha 4:** browse, attach, refresh and remove complete file content, including PDF/DOCX/XLSX and scanned PDFs, with visible admission limits. | FR-04, FR-14, FR-15, FR-16, FR-17, FR-18. | V-05, V-06, V-07 |
| P5 — Complete commands and replay | **Preview alpha 5:** discover and use the maintained `/` command set with equivalent effects; inspect startup replay separately from interactive `/replay`. | FR-08, FR-09, FR-10, FR-22; `@agent_name` route. | V-02, V-07, V-09 |
| P6 — Full-release candidate | Installed product, guides, physical macOS/Linux UAT and controlled real-provider/tool evidence meet the entire baseline. Publication is a separate decision. | NFR-01, NFR-02, NFR-03, NFR-04, NFR-05 and aggregate recheck of FR-01–FR-23. | V-01–V-09 |

No P0–P6 phase is deferred in this proposed first-full-release path. Preview
publication at any intermediate gate is optional and separately authorized;
the full-release coverage contract is not optional. If a phase cannot close
its exit test, retain it as open or split it into smaller subphases instead of
moving its requirement silently into a later preview.

## Assumptions and dependencies

The initial product serves one person in a local macOS or Linux terminal.
No calendar release date, external preview distribution, provider credential,
or broader platform support is assumed. The first connected-conversation
preview can use a controlled configuration with no executing tools and
older-turn compaction disabled while the Activity and full budget recovery
paths are still being built, but its notes must disclose those limits. The
TUI must not silently disable a service in a user's loaded configuration;
the gate fixture is deliberately chosen. The full release cannot use that
limitation. The common runtime YAML, referenced `models.yaml`, and optional
shared presentation file remain the configuration sources; a TUI run does
not rewrite them.

The near-term dependency is a reviewed N03A-01 shell and its required physical
UAT. P1 then depends on a Chat-compatible UI-neutral runtime assembly and
owned close contract. P2 requires an effective-model switch and full-request
budget/failure outcomes. P3 requires events that prove actual tool admission
and execution rather than inferring them from model text. P4 requires a
complete selected-file snapshot path into model input plus a verified PDF
renderer and system Tesseract for OCR UAT. P5 requires the separately reviewed
and accepted [shared command refactor](../command-handoff.md#command-initiative),
including typed neutral context/effect seams for each retained command family;
P5 connects and proves the TUI adapter. P6 requires the accepted
pre-UAT provider/tool binding and physical Linux terminal access. Each
technical contract must be reviewed before its owning directive; this draft
does not specify package APIs by implication.

## Phase workstreams, dependencies, and exit tests

### P0 — Reconcile the existing shell

**Included work:** Close the corrected N03A-01 packet review and observe the
installed shell in macOS Terminal.app: actual `Enter`/`Ctrl+Enter` delivery,
Insert newline fallback, paste, pointer actions, resize at 120×30 and 80×24,
focus, Quit, and terminal restoration. Record defects and any bounded
remediation under the existing directive/validation process.

**Exit test:** An independently reviewed frozen shell candidate and recorded
physical observations show that its stated controls work. The shell still
reports runtime connection as pending. This is evidence toward NFR-01/NFR-02
and V-08, not a substitute for FR-05 or V-01.

### P1 — Connect the Friday runtime and first conversation

**Workstreams:** (1) common-file chooser/explicit-path startup and neutral
real/fake service assembly, including ownership and cleanup; (2) a typed,
ordered prompt/answer bridge and the same active session for the next turn;
(3) initial request admission, transcript outcome and failure recovery; (4)
installed packaging and a task-focused preview guide. Reuse existing neutral
primitives only where their public contracts and behavior are verified.
Extract another Chat operation only when this integration proves the missing
UI-neutral capability, with before/after Chat and `friday-cli` comparisons.

**Testable subunits:** configuration selection and startup errors; neutral
service assembly/teardown; one submitted prompt and a second turn; first-step
budget-safe rejection or provider/runtime failure with preserved editor state;
graceful Quit during an admitted operation. Each subunit has an injected
failure, disposable state, installed-wheel check and its own review gate.

**Exit test:** From a freshly installed TUI outside the checkout, a person
selects an existing valid real runtime YAML in that controlled preview
configuration, submits a short prompt, sees a
real Friday answer, submits a follow-up in the same session, and exits after
cleanup. Invalid chooser and explicit paths take their distinct routes; an
initial failed request preserves the prompt and does not appear as a
successful transcript turn. A fake-only answer or no-backend screen fails
this gate (FR-01, FR-02, FR-05, FR-06; V-01, V-07). Initial budget and
failure handling is demonstrable. P2 builds all-step budget and recovery
contracts; P3 closes post-tool UI behavior and P4 closes attachment input.
Preview notes state that command parity, Activity, file context, and
live model control are still open.

### P2 — Control the model and whole-request budget

**Workstreams:** (1) an idle-only, run-scoped chooser of eligible `kind: chat`
profiles from loaded `models.yaml` in file order; (2) a UI-neutral effective
model switch for future turns only; (3) full-request estimate and one eligible
older-turn compaction attempt for each model step, followed by reassembly and
recheck; (4) post-send context error and ordinary provider/runtime failure
recovery with transcript and completed-effect boundaries.

**Testable subunits:** chooser eligibility and rejected selection; two-model
future-turn routing and unchanged other services; failed newly selected model
restoring the prior model without a TUI resend; below/at/above budget before
the first and a later post-tool step; disabled, ineligible, failed and
successful compaction; empty versus newer editor draft, Restore/Dismiss,
and failed/incomplete transcript exclusion. Use a fake executing tool and
separate conversational versus maintenance provider spies.

**Exit test:** In one installed session with a controlled no-tool
configuration, switch from model A to eligible model B while idle,
demonstrate the next turn uses B, then inject a B request failure. The TUI
reports it, makes A effective for the next deliberate turn, keeps the failed
prompt recoverable and makes no TUI-level resend. Deterministic service
tests prove that an over-budget request triggers at most one configured
eligible older-turn compaction attempt and proceeds only after a passing
full recheck; otherwise the first draft remains editable. Post-tool UI
evidence remains for P3 and attachment-input coverage for P4, so this phase
does not claim complete FR-18–FR-20 or FR-23 (FR-03; slices of FR-18–FR-20,
FR-23; V-03, V-05, V-06). The 4,000/8,000 attachment-admission defaults
remain fixed across models; P4 proves actual selected-file enforcement.
Physical macOS UAT checks the chooser and recovery controls.

### P3 — Make ongoing work inspectable and controllable

**Workstreams:** (1) accepted conversation zones, role cues, pinned latest
prompt, independent scrolling, jump controls and display clear; (2) truthful
typed Activity from actual tool admission/execution, including ordered steps,
arguments, `Not run`, and bounded in-process view state; (3) provider-supplied
reasoning hidden by default, with a forward-only in-app toggle; (4) editor
recall, theme/layout preferences, and normal/Force quit lifecycle.

**Testable subunits:** conversation scroll/focus at wide, minimum and
below-minimum sizes; a multi-step agent with executed and rejected tool
requests; collapse/count/eviction/copy limits; reasoning text versus
count-only versus absent; later post-tool failure with retained effects;
normal Quit during slow work and a separately confirmed Force quit during
stalled work. Use deterministic headless/PTY tests and physical macOS
terminal observation. Keep automatic tool-result payloads out of chat.

**Exit test:** A representative agentic turn yields an ordered inline
Activity log with actual parameters/status and a final answer. The user can
pause/resume independent scrolling, read the pinned prompt, inspect or hide
reasoning when supplied, recall a submitted draft without executing it, and
Quit through the appropriate safe path. A later post-tool provider/runtime
failure stops the loop, leaves completed effects and Activity visible, and
writes no incomplete-turn transcript entry. No transient Activity/reasoning
is silently persisted (FR-07, FR-11–FR-13, FR-19–FR-21, FR-23; V-01,
V-04, V-06). P3 does not claim all slash commands are present.

### P4 — Add deliberate file context

**Workstreams:** (1) read-only sidebar browsing and in-run attachment
snapshots supplied to later model input through a neutral contract; (2)
complete text/code/data, PDF, DOCX and all-sheet XLSX extraction; (3)
mixed-page PDF rendering and separately installed Tesseract OCR; (4)
per-file and combined estimated-token admission through optional `tui:`
settings, linked to P2's whole-request budget check.

**Testable subunits:** deliberate selection versus focus/scroll; successive
turns, second file, removal, same-file refresh and failed-refresh retention;
positive format fixtures in actual model input; every XLSX sheet and formula
representation; scanned and mixed PDF pages, missing Tesseract/language pack
and failed middle page; 3,999/4,000/4,001 and 7,999/8,000/8,001 estimated
token boundaries with fixed defaults across models. Reject partial or empty
new content. Tests use disposable files and installed wheel/sdist on macOS
and automated Ubuntu, with physical macOS file-selection UAT.

**Exit test:** Select a real document and see its complete extracted content
in Friday's next model input, then refresh or remove it and see the expected
future-turn change. A scanned PDF reaches the same path through Tesseract;
an unreadable page or over-limit attachment fails visibly without partial
model input or loss of an earlier good snapshot. Full-request admission is
rechecked with active attachment snapshots and the selected model before a
conversational provider call (FR-04, FR-14–FR-18; V-05, V-06, V-07).
The TUI guide describes the installed OCR prerequisite and
limits; it does not claim a filename alone is context.

### P5 — Finish `/` parity and startup replay

**Workstreams:** (1) consume the separately accepted shared command owner;
(2) connect TUI input and result/UI-effect presentation to that owner,
deriving suggestions, palette and usage hints from its metadata; (3) prove
retained command families over verified neutral context and effects through
disposable-fixture subphases; (4)
active session/transcript versus display-state rules; (5) startup read-only
replay success/error routes separate from interactive `/replay`.

The [command matrix](../command-handoff.md#command-matrix) remains the 50-case before-change
inventory. Reconcile retained and retired rows with the accepted command
refactor before assigning TUI integration subphases; selected retirements must
have their approved old-name behavior tested rather than being counted as
missing TUI parity. The optional `!` route remains deferred.

**Testable subunits:** for each retained command family, compare positive
syntax, aliases, invalid arguments, unavailable service, observable state/file
effects, progress and cancellation against equivalent Chat/TUI disposable fixtures.
No name-only registration check closes a case. High-impact reset,
maintenance, tool and security cases use explicit disposable fixtures and
retain their intent gates. Discovery tests add one TUI-only test command
without modifying either CLI. Reconcile the command matrix with the accepted
shared registry and both frontend adapters at every subphase boundary. Rerun
affected Chat and `friday-framework-cli` regression and installed-package
checks when integrating the TUI adapter. Physical macOS UAT follows
representative families.

**Exit test:** Every PAR-001–PAR-050 row has a recorded retained or retired
disposition. Retained rows have outcome/effect parity evidence, retired names
have approved response evidence, and every retained alias follows its command.
`/sessions` and `/transcript` do not switch
the active transcript session, `/switch` changes the agent, and `/cls`
clears only the view. Startup `--replay FILE` shows its read-only file/count
or file/error outcome until Quit, while interactive `/replay` remains a
slash command (FR-08–FR-10, FR-22; V-02, V-07, V-09).

### P6 — Prove the complete installed product

**Included work:** Build and install final wheel/sdist outside the checkout;
close every FR/NFR and AC trace with positive, negative, regression and
installed evidence; run both existing CLIs with and without the TUI; perform
physical macOS and Ubuntu 24.04 GNOME Terminal UAT at 120×30, 80×24 and a
below-minimum resize; complete the controlled real-provider/executing-tool
run. Bind its exact provider, tool, fixture, expected effect and authority at
the named pre-UAT gate. Record actual OS/terminal versions and key delivery.
Automated Ubuntu checks support, but do not replace, hands-on Linux UAT.

**Exit test:** A person follows the published-candidate TUI guide to
configure, converse, switch models, browse/attach files, use representative
`/` commands, inspect tool work/reasoning, recover from failures and Quit on
both target terminals. All reconciled command cases and required negative paths
remain green; Friday Chat and `friday-cli` behave as before; the real
provider/tool run shows truthful Activity and completed effects. Guide and
configuration reference instructions match the installed candidate
(NFR-01–NFR-05; V-01–V-09). Maintainer acceptance and any release or
publication are subsequent, separately recorded decisions.

## Integration criteria between phases

| Boundary | Required integration evidence before dependent construction |
| --- | --- |
| P0 → P1 | Independently reviewed shell with physical macOS observations, package/import closure, and a stable owned app lifecycle; unresolved shell findings stay explicit. |
| P1 → P2 | Neutral runtime assembly provides typed config, effective model, session identity, prompt/answer stream, failure and close outcomes; installed real conversation and unchanged CLI behavior are demonstrated. |
| P2 → P3 | A typed provider/tool/lifecycle event path can distinguish a tool request from actual execution and preserve failed-turn identity; model and budget outcomes remain UI-neutral, while Restore/editor state stays TUI-owned. |
| P3 → P4 | Conversation and Activity can show attachment progress/errors without treating selection as a model turn; P2's budget contract includes complete attachment snapshots, which P4 must integrate through a neutral model-input seam. |
| P4 → P5 | The separate shared-command initiative is accepted with a reviewed UI-neutral owner, complete retained-command and intentional-retirement evidence, protected CLI regressions and installed package checks. Command effects consume neutral services without importing CLI handlers into TUI; attachment state, transcripts, active agent and display state remain distinct. Both frontends use the same maintained-command metadata and execution, while TUI-only extensions remain isolated. |
| P5 → P6 | All PRD rows and PAR cases have candidate evidence; remaining work is integrated defect correction, guide reconciliation and final installed/UAT gates, not silent feature deferral. |

## Migration, security, governance, and architecture mirror

Shared-service extraction remains a migration task wherever Chat currently
owns a needed effect. The separate
[command refactor](../command-handoff.md#command-build-plan) owns
maintained-command extraction and Chat delegation. This TUI phase consumes
its accepted public contract and records frontend parity, dependency closure
and rollback/remediation evidence. No user runtime-file migration is planned: the
same YAML and presentation file remain usable, and TUI-only settings do not
change CLI interpretation. After the joint review, reconcile the older
replacement plan and packet links to the accepted phase map; do not erase
historical directives or validation evidence.

The architecture mirror currently passes only at the **product-boundary**
level: independent `friday-tui`; UI-neutral Friday services and a shared
maintained-command owner; common runtime files; TUI-owned presentation,
editor, extension composition and view state; unchanged CLI behavior. It does
**not** establish accepted technical interfaces for the command package/API,
runtime assembly, live model changes, request-budget enforcement, older-turn
compaction, provider failure classification, tool execution events, selected
file snapshots, OCR, or resource close. Those gaps require a reviewed
architecture/contract binding before their owning phase's tactical plan and
directive. If a proposed interface violates the accepted boundary, treat it
as an architecture regression for review rather than silently changing the
phase plan. The old `G3` label in a withdrawn build plan referred to a UAT
gate; it is not evidence of an accepted G3 architecture specification.

Security and governance remain cross-cutting. A visible tool request is not
execution authority; runtime policy decides admission. Activity shows
actual parameters without TUI-specific credential filtering as accepted,
but bounds display and copy; reasoning/Activity remain transient by default.
Model fallback and error recovery must not automatically resend a failed
turn or roll back completed tool effects. Every code unit needs its own
approved scope, frozen candidate, independent review, required automated
Linux check and appropriate terminal UAT. A `VERIFIED` report is evidence
for its named candidate, not maintainer acceptance or delivery.

## Test and CLI/API/UAT strategy

Each tactical subunit should bind one observable behavior, one negative or
recovery path, and affected Chat/`friday-cli` regressions before code. Use
deterministic provider/tool/event doubles for ordering and boundary cases;
disposable real stores for transcript, memory, export and file effects;
installed wheel/sdist tests for launcher, dependencies and resource files;
headless Textual and PTY checks for focus, sizing, key behavior and terminal
restoration. Compare shared command outcomes and UI-neutral API effects against
Chat behavior before and after extraction, then exercise that same
implementation through the TUI. A passing test for a handler name or fake screen does
not prove an installed user workflow.

Run automated Ubuntu checks throughout construction. Record physical macOS
UAT at shell, connected conversation, model chooser, Activity/reasoning,
file-context and command/lifecycle milestones. At the full-release gate,
run hands-on Ubuntu GNOME Terminal UAT in addition to macOS, including the
guide tasks and real-provider/tool case. Record candidate SHA, package,
config/fixture, terminal, user actions, observed outcome, defects and
acceptance for each UAT session. Testing and UAT are planned during each
phase; they are not postponed to P6.

## Documentation close-out and plan acceptance

Grow a dedicated user-oriented `docs/guides/20-tui.md` alongside shipped
behavior. Put detailed optional `tui:` setting reference in
`docs/guides/10-configuration.md`, with links in both directions. Preview
guides must label incomplete commands and features; the final guide covers
screen zones, editor, navigation, model chooser, all `/` commands and
aliases, file context/OCR, Activity/reasoning, recovery and safe Quit in
task language. Check every example, key, setting, label and recovery step
against the installed candidate and guide-based user UAT before P6 exit.

This **draft plan** is ready for joint review only when every FR/NFR has a
primary completion phase, every phase has a user-visible exit test traced to
the vision and PRD, deferred scope is explicit, architecture gaps are named,
and the P0 current-state gate is accurate. Review the vision, PRD and plan
together; record any changed product choice in the decision register first,
then update all three documents and the replacement-plan/board pointers as
appropriate. Only after maintainer acceptance of the planning baseline
should the next active phase receive a just-in-time tactical plan, specific
construction directives, test/UAT plan, review and as-built evidence.

## Risks and open decisions for the joint review

| Item | Risk or decision | Proposed disposition |
| --- | --- | --- |
| R-01 | A large first-full-release scope could pull work back into invisible service extraction. | Require a running, installed workflow at each phase exit; extract only a demonstrated missing neutral primitive. |
| R-02 | Migration to a shared engine can regress Chat behavior or leave a frontend with stale metadata/effect handling. | Keep the source-derived matrix, prove Chat before/after behavior for each migrated family, test both installed frontends on equivalent fixtures, and reconcile their effective registries at each P5 subphase and P6. |
| R-03 | Terminals differ in key, pointer, color, resize and restoration behavior. | Keep visible fallback controls and physical milestone UAT; final Linux UAT remains mandatory. |
| R-04 | OCR renderer/native dependencies and Tesseract languages may differ across platforms. | Bind renderer/license and processing limits before P4 directive; prove installed macOS/Linux fixtures. |
| R-05 | Model/context estimates and provider outcomes may disagree. | Bind estimator, response reserve, override ranges and failure classification before P2/P4 directives; test post-send failure separately from preflight. |
| R-06 | Event gaps can make Activity infer execution from a request. | Bind typed admission/execution/terminal event provenance before P3; use actual tool spies. |
| Q-01 | Should alpha 1 stop at connected conversation and alpha 2 add live model switching, or combine them? | Propose separate alphas to reach the first real user journey sooner; confirm at joint review. |
| Q-02 | What accepted architecture artifact will serve as the G3 mirror for tactical phase approval? | Review the architecture-reset boundary and produce/accept a technical architecture binding without treating proposed APIs as approved. |
| Q-03 | Which exact provider and executing tool form final installed UAT? | Bind at the already accepted pre-UAT gate; do not put credentials in this plan. |
| Q-04 | Which preview alphas, if any, will be distributed externally? | Decide per preview after its evidence gate; alpha numbering here is proposed and grants no publication authority. |

Before accepting this plan, repeat the skill's accuracy pass: confirm scope
labels, no deferred feature disguised as included, no requirement without an
exit criterion, complete FR/NFR/V traces, architecture mirror disposition,
migration and security work, test/UAT coverage, and technical decisions
required before the next tactical plan.
