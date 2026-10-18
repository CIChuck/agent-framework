# Friday TUI build plan

**Status:** Superseded draft; must be redesigned for the independent TUI package

**Initiative:** `friday-tui`

**Branch:** `feature/friday-tui`

**Source baseline:** `c34269867be50f71923c93c95a63236a35505812`, Friday `0.1.0a4`

execution_phase: planning; validation_state: not_ready

The [architecture reset](architecture-reset.md) and [accepted decisions](decisions.md)
control. This plan's direct reuse of `friday-chat` application code, registries,
handlers and loader is withdrawn. Its phases, gates and exact first directive
are reference material until a replacement plan is reviewed. No product scope
is approved from this document.

## 1. Authority and intended outcome

Chuck Russell requested activation of this unit of work, a dedicated branch and
a build plan. [Planning authority](authority.json) permits packet construction
and board reconciliation. The follow-up request to proceed and explain the
decision process includes drafting the technical contract and first directive.
This plan proposes future implementation; it is not an approved construction
directive or publication authorization.

The [product requirements](README.md) control the scope. Six requirements are
fixed by the maintainer:

1. Replicate every current `friday-chat` `/` command, alias and workflow within
   the TUI, preserving its arguments, results, state changes and service limits.
2. Preserve the existing `friday-cli` package's feature set, public contracts and
   behavior. The maintained Chat CLI must also continue working as it does now.
3. Design an extensible slash-command interface that can gain commands,
   subcommands and richer capabilities through modular registration.
4. Keep this work isolated on its own branch. Product implementation begins only
   after the plan and a bounded work-unit directive are approved.
5. Use the same Friday runtime/configuration infrastructure in both frontends.
   Runtime files, schemas, precedence and service/storage interpretation remain
   compatible; TUI-specific settings are limited to presentation.
6. Extend the existing CLI presentation file using the accepted optional
   versioned `tui` namespace and UX option families. Preserve current root
   fields/defaults and CLI behavior; keep runtime settings in runtime files.

The maintainer also requires testing throughout construction and explicit UAT.
The [incremental test and UAT plan](test-and-uat-plan.md) divides these phases
into 24 independently testable units, with regression/independent-review gates
and real-user checkpoints from the first usable shell onward. These are required
parts of the proposed build, not tests deferred until the feature is finished.

Here, command-line capability means `/` commands within the TUI. The initial
50 canonical commands and three aliases are a minimum compatibility baseline,
not a command-count ceiling. [Source baseline](source-baseline.json) records
where that inventory came from. The [command matrix](command-matrix.md) adds
current argument metadata. A limited current-code baseline passed 241 existing
tests; full CLI/TUI behavioral parity remains future work.

## 2. Scope, boundaries and deliverables

### Intended implementation surfaces

| Surface | Planned responsibility and boundary |
| --- | --- |
| `packages/friday-tui/` | New installable `friday-tui` / `friday_tui` presentation package, Textual app, input queue, adapters, widgets, styles, command extensions and tests. |
| `packages/friday-chat/` | Reuse the application, registry, runtime, identity and maintenance contracts. Only exact, additive public-interface extensions may be proposed; existing CLI callers/defaults must remain unchanged. |
| `packages/friday-cli/` | Protected existing implementation. No TUI-driven source refactor, component move, monkey patch or replacement. Run its unchanged regression coverage. |
| Workspace/package metadata | Minimal registration, supported Python/Textual constraints, exact internal pins and package resources. Enumerate actual paths in the packaging directive. |
| Release-cohort helpers/tests | Assess package-inventory assumptions when adding the new distribution. Any necessary bounded change requires its own explicit scope; no automatic cohort-wide release bump. |
| Planning and user documentation | Record contracts, decisions, evidence, clone/installed startup, commands and extension authoring. |

No runtime or package files are authorized for editing in the current planning
phase. Future directives must list exact files and acceptance tests rather than
using this table as a blanket allowlist.

The first release includes complete command parity, a keyboard-usable interface,
streaming/progress, safe lifecycle integration, discoverability, a demonstrated
command-extension mechanism and an installed executable. Full file management,
new memory/tool engines, external plugin discovery/hot reload and an arbitrary
set of new production commands are separate future scope. Prove extensibility
with a deterministic test extension; do not ship a test-only command by default.

## 3. Proposed architecture

Use Textual's UI loop and a dedicated backend thread/event loop. Construct, run
and close the Chat runtime and its async clients on that backend loop, with one
supervised `FridayChatApp.run()` per session. Existing synchronous file reads
make a same-UI-loop task insufficient for responsive navigation. Bridge the
loops through bounded thread-safe input and ordered output events; all widget
updates stay on the UI thread. The [integration contract](integration-contract.md)
defines ownership, backpressure and admission.

Inject an `InputSource`, a TUI output sink, a display/heartbeat adapter and an
owned command registry. Route submitted text through the existing application
loop rather than independently invoking handlers from widgets.

```text
Prompt / discovery / UI actions                  UI loop
             |
     admission + thread-safe input bridge
             |
      FridayChatApp lifecycle                   Backend loop
       /          |           \
command set   turn processor   maintenance + cleanup
       \          |           /
      output / stream / display adapters
             |
       ordered event bridge
             |
   conversation + results + status views         UI loop
```

The registry composes the inherited command set with approved TUI extensions.
The resulting metadata drives `/help`, completion and discovery. New ordinary
commands need a module, typed handler, metadata, registration, documentation and
tests; they must not require a new switch branch in the core UI dispatcher.
Reject name/alias collisions rather than overriding inherited handlers.

Share backend session identity, command context, runtime services and admission
rules. Keep Textual imports and view state in the TUI package. Extensions use
typed service/UI-effect contracts, not private runtime access. Additional TUI
commands do not alter the existing CLI's default registry implicitly.

### Concrete TUI-00 proposals ready for review

- **Display configuration:** `friday_chat.display.resolve_display_config()` and
  its loader call `set_cli_config()` and `reset_console()`. Calling that resolver
  from the TUI would violate isolation of shared CLI console state. Propose an
  additive pure `read_display_config()` API while preserving the CLI's current
  activation path.
- **Active-operation shutdown:** Chat exposes an async application lifecycle but
  not a complete public stop/cancel API for every operation. Propose a separate
  Quit intent that closes admission, lets admitted work return, then signals EOF
  through the existing input contract. Add a public immutable shutdown report;
  never drive private shutdown methods or cancel a mutation to exit the UI.
- **Output channels:** Generic command/progress output is text; assistant stream
  hooks are separate. Preserve text faithfully initially. Separate status/error
  channels or richer views require explicit typed events, not parsing output text
  to infer application state. The bridge uses TUI-owned immutable events.
- **Replay:** CLI startup replay creates its own default fake runtime and exits;
  interactive `/replay` uses the session runtime and can reset memory. Define the
  TUI startup view separately, preserving interactive replay behavior. The
  contract specifies launcher validation and a retained offline result view.

No gap is permission to change existing CLI semantics. If an additive design
cannot satisfy a requirement, record the conflict before construction.

## 4. Functional requirements and traceability

| ID | Implementation requirement | Product acceptance |
| --- | --- | --- |
| FR-01 | Preserve all inherited commands, aliases, argument families, state effects, errors and unavailable-service responses; retain `@agent` and disabled-by-default `!` request handling. | AC-01, AC-02 |
| FR-02 | Registry-derived help/completion/discovery; command entry remains available for every command and subcommand. | AC-01, AC-11 |
| FR-03 | Separate visible clear (`/cls`, `/clearscreen`) from history/session clear and store reset; preserve export, execution and maintenance flags. | AC-03 |
| FR-04 | Preserve ordered streaming/final output, progress and responsive navigation without duplicate completion text or duplicate accepted submissions. | AC-04 |
| FR-05 | Serialize backend work under existing admission rules; implement safe-point quit, finish non-interruptible operations and complete shared cleanup before exit (Q-03). | AC-05 |
| FR-06 | Installable executable, packaged UI resources, shared Chat configuration and service opt-ins, isolated TUI presentation settings. | AC-06 |
| FR-07 | Initial macOS/Linux support (Q-01), a multiline editor with an explicit submit shortcut (Q-02), editable history, safe paste, focus/navigation, readable output, resize and terminal restoration. | AC-07 |
| FR-08 | Preserve source and behavior of existing `friday-cli`; preserve Chat CLI defaults/callers; verify CLI use with and without TUI installed. | AC-08, AC-09, AC-10 |
| FR-09 | Add commands through typed modular registration; reject collisions and isolate frontend command sets. | AC-11, AC-12 |
| FR-10 | Test bounded units during construction and run real-user UAT at the five milestone gates; retain candidate-specific evidence and defect/signoff records. | AC-13 |
| FR-11 | Reuse the shared runtime loader/factory and configuration interpretation without TUI-specific runtime overrides, path rebasing or startup precedence. | AC-14 |
| FR-12 | Extend the existing CLI presentation file through an optional typed TUI namespace while preserving legacy fields/defaults and all CLI behavior. | AC-15 |

The exact acceptance wording remains in [README section 8](README.md#8-acceptance-and-verification).
The [decision register](decisions.md) records accepted Q-01 through Q-03:
initial macOS/Linux support, a multiline editor with an explicit submit shortcut,
and quit at a safe stopping point with non-interruptible work and cleanup
completed before exit. It separately tracks proposed technical details.

## 5. Work packages and gates

### TUI-00 — integration contract and compatibility baseline

**Entry:** Planning is active; product implementation is not yet authorized.

Deliver an exact command/argument/alias coverage matrix, current CLI behavior
baseline, supported terminal matrix, dependency baseline and typed adapter/control
contract. Resolve display-config isolation, replay mapping, lifecycle requests,
extension ownership and technical details under the accepted product choices.
The [draft contract](integration-contract.md), [decision rationale](decisions.md),
[command matrix](command-matrix.md) and
[baseline evidence](validation/technical-evidence.json) now supply these design
artifacts. Remaining runtime/UI/terminal checks are explicitly unexecuted.
Record existing failures without rewriting tests or declaring them fixed.
Build the pure display reader as TUI-00A, verify its candidate, then build the
shutdown report as TUI-00B. Their separate scopes and check commands are bound in
CD-TUI-001; do not implement both before checking the first.

**Gate G0:** Maintainer reviews this plan, the contract and
[CD-TUI-001](directives/CD-TUI-001-shared-presentation-contracts.md). That draft
binds exactly five Chat source/new-test paths to the pure display reader and
shutdown report, with positive/negative tests and stop conditions. Record
product-code authority only when explicitly granted for that unit. Implement
and independently validate those shared interfaces before a separate directive
authorizes the TUI package/widgets. No dependency installation is part of CD-TUI-001.

### TUI-01 — package, shell and adapters

**Dependencies:** G0, a `VERIFIED` CD-TUI-001 candidate and a separate approved
TUI shell directive.

Build the presentation package, resource loading, installed help/version,
configuration diagnostics, layout and typed input/output/display adapters. Run a
supervised fake session on its owned backend loop with inherited `/help`,
`/history`, clear-view and exit through the Chat lifecycle. Test bounded ordered
bridges, busy submission rejection with draft retention, EOF Quit and thread
ownership. Do not nest an event loop inside an already running loop or activate
the shared console. Preserve a usable diagnostic view on startup failure.
TUI-01A must prove shared runtime configuration parity (CFG-01..06) before the
UI depends on startup behavior; file selection does not introduce another
runtime configuration parser or override layer.
The [accepted UX configuration design](ux-configuration.md) adds UXCFG-01..08 for the
optional `tui` namespace in the same CLI presentation file. The startup directive
must bind initial fields/defaults and parser scope; later widget units verify
actual preference effects as they are built. Existing CLI source remains protected.

**Gate G1:** Fake-session UI tests, resource/entry-point checks and CLI isolation
checks pass, plus user-approved UAT-01 on both target terminals. Build/check
bootstrap, worker bridges and usable shell as 01A, 01B and 01C. Independently
validate each stable candidate before dependent work. This shell milestone is
not complete command parity.

### TUI-02 — complete inherited slash-command parity

**Dependencies:** G1; a bounded parity directive and frozen coverage matrix.

Exercise every canonical command, alias, relevant option/subcommand family and
additional route through the TUI prompt using shared handlers. Compare backend
effects against the maintained CLI on equivalent fresh fixtures. Cover session,
memory/diagnostics, transcripts/export/replay, maintenance, tools/security,
speech, agents/workflows and files. Validate disabled/unavailable services as
their actual current behavior, not as successes.

**Gate G2:** Every matrix row is tested or carries an explicit unresolved gap;
no unapproved omission qualifies as parity. Verify clear/reset distinctions,
workflow control, contained exports, maintenance dry-run/execute/recovery rules
and no duplicate operations. Build command groups as 02A..J, with maintenance
split into F1..F3, under exact per-unit directives and tests. Demonstrate
and record family UAT as each becomes usable; combined approval of all UAT-02
scenarios is required for G2. Independent review covers each unit and their
combined parity. Blocking UAT findings stop affected dependent work.

### TUI-03 — responsive operations and lifecycle

**Dependencies:** G2; approved active-operation policy and control contracts.

Integrate ordered assistant streaming, command progress and busy/error state;
maintain responsive navigation/editing while backend execution remains serialized
on the worker. Implement Q-03 for generation, tools, replay, ingest and
maintenance: finish the admitted operation, reach the next input boundary, then
clean up and quit. Earlier cooperative stop points require a later explicit
owner contract. Preserve extraction drain, transcript finalization,
configured exit maintenance and client/MCP closure. Show pending or failed cleanup
without implying that cancellation rolled back persistent work.

**Gate G3:** Controlled slow/failing-operation tests prove ordering, responsiveness,
admission and cleanup. Add real terminal checks where headless execution cannot
prove key handling or terminal restoration. Independent review includes lifecycle
failure paths and unchanged CLI behavior. Test 03A streaming, 03B active Quit and
03C failure/cleanup separately; user-approved UAT-03 is required for G3.

### TUI-04 — command evolution and interaction polish

**Dependencies:** G3; approved extension and keyboard contracts.

Prove a new command can be added by a test module/registration without modifying
baseline handlers or core UI dispatch/layout. Verify help/completion, aliases,
typed effects, capability failures and collision rejection. Preserve independent
CLI command sets. Complete the multiline editor with Enter for newline, F2 for
submission and a focusable Submit fallback, plus focus, resize, scroll and
readability behavior across the proposed macOS/Linux terminal matrix.

**Gate G4:** AC-07, AC-11 and AC-12 pass alongside inherited command coverage.
No test extension is accidentally shipped in the normal command set. Test 04A
extension/discovery before 04B terminal polish; UAT-04 approval is required.

### TUI-05 — packaging, aggregate validation and handoff

**Dependencies:** G4; exact packaging/documentation directive.

Validate workspace registration and release-cohort assumptions, exact internal
pins, documentation URL, Textual dependency compatibility, wheel/sdist contents,
installed startup outside the checkout and preservation of existing entry points.
Use a disposable installed environment; include the full intended supported
terminal/dependency matrix. Prepare clone/PyPI usage and command-extension docs.

**Gate G5:** All AC-01 through AC-15 have evidence, required checks pass and a fresh
read-only aggregate validator returns `VERIFIED`. Test clean installed artifacts
in 05A and reconcile the final candidate in 05B. Required earlier UAT and final
UAT-05 must be user-approved for the actual candidate on both targets, with no
unresolved blocking defect. The controller may then propose completion for
maintainer acceptance. Push, merge, release and PyPI publication are separate
authorized delivery steps, not inferred from this plan.

## 6. Verification strategy

Each of the [24 construction units](test-and-uat-plan.md#2-testable-construction-units)
has an immediate behavior test boundary. Tests and failure cases accompany its
implementation; dependent work waits for passing checks and independent review.
Each scheduled UAT checkpoint additionally requires explicit approval by Chuck
Russell or a user he designates. Automated tests and `VERIFIED` are not UAT
signoff. Required UAT cannot be silently carried to the end or marked passed
because a target machine is unavailable.

- **Baseline versus regression:** Capture source/interface/dependency baselines
  before any runtime changes. Run unchanged CLI tests and selected installed
  probes before and after each shared-interface or dependency change.
- **Deterministic parity:** Use isolated fake runtimes and provider transports;
  compare outputs, return values, persisted state and UI effects on independent
  fixtures. A shared handler or registered name alone is not behavioral evidence.
- **Real-store integration:** Use disposable transcript/memory stores for export,
  reset, maintenance and shutdown evidence. Never use existing developer state.
- **UI:** Use Textual headless interaction tests for command submission, focus,
  discovery, streaming, progress, resize and failure visibility. Use PTY/manual
  terminal evidence for the selected real terminal matrix.
- **Package:** Run focused pytest, Ruff and Mypy; metadata/internal-pin checks;
  wheel/sdist/resource checks and clean installed-entry-point smoke checks.
  Retain existing CLI behavior in environments both with and without TUI present.
- **Independent validation:** Freeze each code candidate and controlling authority
  for a fresh read-only validator. Review shared-interface work before dependent
  TUI work, and perform an aggregate review of the final branch.
- **UAT:** Use the real-terminal scenarios, candidate/fixture records and defect
  rules in [the UAT plan](test-and-uat-plan.md#3-uat-checkpoints-and-executable-user-scenarios).
  Begin at G1, repeat for command families and lifecycle/interaction milestones,
  and approve final installed end-to-end workflows before proposing completion.

No live-provider, paid or remote-MCP validation is included in current planning
authority. Any such profile needs explicit effects/service authority. Fake UI
checks, real-store checks and live-service acceptance remain distinct evidence.

## 7. Risks and stop conditions

| Risk | Required response |
| --- | --- |
| Existing CLI rendering/configuration changes indirectly | Reject the regression; preserve its baseline and isolate TUI adapters/configuration. |
| UI/event-loop cancellation bypasses an in-progress mutation | Stop the affected slice; require an owner-defined safe boundary and failure/recovery test. |
| New command overrides an inherited name or leaks to the CLI | Reject registration and demonstrate per-frontend isolation. |
| Shared public API cannot express required behavior | Record a bounded additive contract gap; no private-method or global-state workaround. |
| Fixed package inventory or dependency changes break existing installs | Reconcile the packaging directive and dependency matrix before merging. |
| Tests only prove command registration or fake runtime success | Require state/effect/UI evidence and the intended integration profile. |
| Construction advances without unit evidence or real-user feedback | Block dependent work at its test/UAT gate; retain failed/blocked/not-run results and remedy the bounded defect. |
| A product decision remains unanswered | Keep the affected design explicitly pending; continue independent planning rather than assuming approval. |

## 8. Completion criteria for this planning request

The packet is active on its named branch with `design_only` authority; the revised
README is preserved; this build plan, tactical plan, decisions, authority,
source-baseline record, concrete contract, first directive, command matrix and
execution log exist; the board/dashboard agree; moved links and document
structure pass; and no product package, runtime config, test or dependency file
changes. The limited 241-test source baseline and metadata-only dependency
resolution are recorded separately from future TUI verification. The
implementation plan remains draft until approved.
The incremental test/UAT plan must be linked from controlling documents, split
the first directive into independently checked units and leave every future
execution/signoff explicitly unclaimed.
