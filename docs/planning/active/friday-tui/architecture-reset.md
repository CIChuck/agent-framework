# Friday TUI architecture reset

**Status:** Accepted product boundaries; N01S/N01A verified; CI01-CI03
automated Linux gates verified; N01B-01 corrected pre-push candidate verified

**Branch:** `feature/friday-tui`; initiative authority `granted`, with N01B-01
the only approved product subunit and no active product-code generation

This record incorporates Chuck Russell's answers after the documentation review.
It controls where the earlier packet proposes a direct dependency on
`friday-chat` or `friday-cli`. The previous integration contract and
CD-TUI-001 are withdrawn as construction proposals. They remain historical
evidence of what was reviewed, not an implementation path.

## Accepted product contract

- `friday-tui` is independently installable. Its source, package metadata and
  dependency closure must not import or require `friday_chat`, `friday_cli`,
  `friday-chat` or `friday-framework-cli`. It uses Friday's UI-neutral runtime
  packages and owns its presentation, command registration and resource
  lifecycle. `friday-chat` is a behavior reference, not a TUI backend.
- The current `friday-chat` slash commands, aliases, argument meanings, effects,
  errors and service limits define initial parity. Equivalent behavior and
  state are required; TUI layout and wording may differ. Parity remains an
  ongoing requirement when Chat commands change. TUI-only commands may be added
  without changing CLI defaults.
- The first release shows the current transcript session and retains
  `/sessions` and `/transcript` for listing, inspection and export. It adds
  no transcript-session switching control; `/switch [agent]` changes the
  active agent.
- When idle, `/exit`, `/quit` and `/q` follow the TUI's normal slash-command
  path with the current command semantics. A submit attempt while busy is
  rejected and retains the editor text, including these commands. Ctrl+Q and
  the Quit action request graceful exit during active work; accepted work
  reaches a safe stopping point and cleanup completes before the terminal is
  released. A separately warned and confirmed emergency Force quit may exit
  stalled work without complete cleanup; it is never a successful normal Quit.
- The same runtime configuration files and presentation file work in both
  frontends. TUI loading must be independent of CLI code. With no `--config`,
  show a chooser for an existing runtime configuration file. The accepted
  optional, versioned `tui:` namespace remains in the existing presentation
  file; existing CLI fields and behavior stay unchanged. D-48 fixes the
  chooser's initial search to the launch working directory with browsing
  elsewhere. D-49 requires likely Chat runtime YAML, including custom names,
  while excluding recognized model-library/display YAML. Under D-50, invalid
  chooser selections leave the chooser open with a diagnostic and Retry,
  Browse and Quit actions. Under D-51, an invalid explicit `--config` file
  reports an error and exits nonzero without opening the chooser or starting
  the runtime. D-52 keeps the chooser open with Browse and Quit when the
  launch-folder list is empty. D-53 cleans up partial real-start resources
  after a chooser selection, then returns to the chooser with the error,
  Retry, Browse and Quit when cleanup succeeds. D-56 reports both startup
  and cleanup failures and exits nonzero with best-effort terminal restoration
  rather than retrying in an uncertain process.
  D-54 cleans up partial real-start resources after an explicit `--config`
  selection, reports the error and exits nonzero without opening the chooser;
  cleanup failure must also be reported.
  D-55 uses shallow, read-only top-level YAML inspection to recognize likely
  runtime files with custom names while excluding model-library/presentation
  files; unrecognized files remain available through Browse. D-57 keeps
  incomplete but recognizable runtime files in the list until selection and
  validation. D-58 lets Browse accept folder navigation and typed/pasted
  absolute, relative and `~` paths to existing files, including outside the
  launch folder; relative entries resolve from the folder Browse displays.
  Missing or invalid choices use D-50 recovery. Exact key signatures, parser
  ownership and schema bounds still require a technical contract.
  D-59 adds a visible keyboard-focusable Refresh action to rescan the captured
  launch folder's candidates on demand. The chooser does not watch the folder;
  an empty list offers Refresh, Browse and Quit, and Refresh starts no services.
  D-60 also lists direct-child `.yaml`/`.yml` links to readable regular
  runtime files, including outside-folder targets. Broken, cyclic, unreadable,
  directory-target and unrelated links are skipped by automatic discovery;
  Browse can still select them and show D-50 errors. No directory recursion is
  implied.
  D-61 keeps Chat's `FRIDAY_CHAT_RUNTIME` mode override out of TUI mode
  selection. Configured TUI startup still defaults to real, while its own
  explicit `--runtime fake` selects fake; runtime YAML environment lookup is
  unaffected.
  D-62 keeps a successful startup replay result visible in a read-only TUI
  screen until Quit. Replay still precedes configured startup and does not
  admit interactive prompts or commands. D-63 limits the first-release view
  to replay file and processed-turn count. D-64 keeps a failed startup replay
  in a read-only file/error view until Quit and then exits nonzero; the chooser
  and interactive session do not open. D-65 excludes in-process Retry and
  requires correction and relaunch. Neutral cleanup details still need a
  separate technical contract.
- Initial targets are macOS and Linux. Use automated Linux checks during
  construction. Conduct real-user macOS UAT at the relevant milestones and
  hands-on Linux terminal UAT on the final candidate before first-release
  acceptance. Automation does not replace Linux UAT. Final acceptance also
  requires a controlled real-provider/tool run; select the provider before
  final UAT rather than assuming one is available now.
- A dedicated, user-facing TUI guide and updated configuration guidance are
  required for completion. Validate their instructions against the final
  installed candidate and user UAT. See
  [user-guide-requirements.md](user-guide-requirements.md).
- Present prompts, Friday responses and command results in one scrollable
  timeline. Use distinct color cues for the user and Friday, with labels and
  other visible distinctions so the roles remain clear without color. See the
  [screen layout](screen-layout.md).
- Pin the latest accepted conversational prompt above its scrolling response.
  This is a view of the same history entry, not a duplicate model input or
  transcript record. Pause automatic following when away from the bottom;
  hide the pin when browsing older exchanges while retaining it when reading
  its own response. A visible clickable and keyboard-focusable `Jump to
  latest` control returns to the bottom, restores the pin when one exists and
  resumes following; scrolling back to the bottom does likewise. `/cls` and
  `/clearscreen` clear the displayed conversation, pinned prompt and Activity
  without changing session history, memory or persisted transcripts. The pin
  stays empty until the next accepted conversational prompt.
- Preserve a UI-neutral path for provider-exposed reasoning events or text so a
  first-release TUI option can show them separately from final answers. The default
  view remains final-answer-only. Availability depends on what the provider
  returns; reasoning-token counts are not reasoning text. This TUI view option
  must not change runtime generation settings or existing CLI behavior. The
  in-app toggle applies to subsequent events without rewriting config or
  retaining earlier hidden text.
- Provide a [rolling tool-activity view](tool-activity-requirement.md) for each
  submitted operation. Show automatic, manual `/run-tool` and delegated/workflow
  tools that actually begin execution, their actors, parameter values as
  passed to the tool without TUI masking, and execution status across multiple
  internal steps. An actual model or user request rejected before invocation
  gets a distinct `Not run` reason, not an executed-call status. Pre-request
  selection or budget exclusions create no Activity entry. Do not render
  automatic tool-result payloads in scrolling chat or Activity; `/run-tool`
  keeps its inline command result.
  Activity is bounded in-process view state, not persisted or exported.
  Oversized parameter values show an explicit truncated preview with no
  retained full copy in the TUI; the tool receives its complete argument.
  Selected visible Activity and shown provider reasoning can be copied; a
  truncated parameter copies only its preview and notice, and reasoning
  received while hidden is unavailable to copy.
  Place provider-exposed reasoning from later model steps in
  sequence when its separate display option is enabled; keep the final answer
  distinct. This view is required in the first TUI release. TUI-specific
  filtering is separate later scope; existing runtime tool policy is unchanged.

## Package boundary

```text
friday-tui  --->  UI-neutral Friday runtime and service packages
friday-chat --->  its existing dependencies
friday-cli  --->  its existing dependencies

No dependency or import from friday-tui to either CLI package.
No dependency or import from either CLI package to friday-tui.
```

The existing `friday-framework-runtime` package currently has no Chat/CLI
dependency in its declared package metadata. Its headless kernel is a starting
point, but it does not by itself prove that every Chat command is available
through UI-neutral contracts. The revised plan must map each command's needed
capabilities to public runtime/services and identify any missing neutral API.
It must not copy a Chat implementation into the TUI by importing it indirectly.
The maintainer permits bounded extraction of reusable non-UI operations from
Chat into a neutral Friday service used by both frontends. That extraction
requires unchanged Chat and `friday-cli` behavior evidence. The exact owner
and per-command scope remain technical design work.

## Work required before a construction directive

1. Replace the Chat-app/registry/handler reuse architecture with an independent
   TUI command and session design over UI-neutral Friday services. Keep the
   source command matrix as a behavior inventory and compare effects through
   disposable fixtures, including ongoing parity drift checks.
2. Define an independent runtime and presentation-file loader with the same
   effective configuration, path and service interpretation. Test the chooser,
   explicit paths, invalid files and CLI compatibility without TUI imports of
   CLI code. Preserve the existing CLI package behavior and installed operation.
3. Make the TUI responsible for resources it creates, including failures after
   partial startup. Specify public neutral resource-close boundaries, ordered
   teardown, failure reporting and terminal restoration. No Chat-specific
   shutdown-report or display-reader API is approved.
4. Define typed TUI outcomes for command errors, progress and lifecycle without
   parsing human-readable output. Bound on-screen output by message count and
   byte/character budget, with visible truncation and no loss of persisted data.
   An older-message eviction notice points to `/transcript` only when saved
   entries exist; otherwise it reports that no saved transcript is available.
   No first-release `Load older` control or recovery claim for transient
   Activity/reasoning is part of this design.
   Specify how optional provider reasoning can cross the UI-neutral boundary
   for the first-release display option without routing through the text-only Chat
   adapter or automatically persisting raw reasoning.
   Define separate UI-neutral tool-execution events; LLM tool-call deltas alone
   do not establish that a call ran. Correlate request, admitted execution and
   completion status across internal iterations without importing Chat's tool
   loop or surfacing tool-result payloads.
5. Use the [replacement plan](replacement-plan.md) to refine construction
   units and tests around the independent package.
   Put pure config/schema checks in bootstrap, widget effects in the owning UI
   units, and command families in independently testable increments. Provide a
   committed or reproducible offline test guard instead of relying on the
   ignored `build/alpha4-work/guard/sitecustomize.py` file.
6. Reconcile macOS milestone UAT, automated Linux coverage during construction,
   final-candidate hands-on Linux UAT and real-provider/tool UAT before release
   acceptance. The old 24-unit/5-checkpoint map is withdrawn history.
7. Assign the [TUI guide and configuration updates](user-guide-requirements.md)
   to construction increments and final-candidate UAT; keep command/configuration
   examples aligned with implemented behavior.
8. Review the [screen layout and interaction proposal](screen-layout.md) and
   bind its accepted zones, scrolling, editor, response and resize behavior in
   the replacement technical contract and user UAT.

This planning record itself grants no product-code, dependency, release or UAT
authority. The board remains `started`. N01A was separately approved and its
frozen candidate has a historical [BLOCKED independent review](validation/VAL-N01A-neutral-config-loader.md),
then a maintainer Linux-smoke deferral and a fresh
[VERIFIED closeout review](validation/VAL-N01A-waiver-closeout.md). The later
[CI03 exact-source Ubuntu run](validation/TUI-CI03-ubuntu-run-39183895627.md)
and [final independent review](validation/VAL-TUI-CI03-final-676700f5.md)
reconciled the CI01/CI02 automated Linux gates. Hands-on Linux terminal UAT
remains a release gate. The approved
[N01B-01 directive](directives/CD-TUI-N01B-01-neutral-transcript-query-contracts.md)
was [independently VERIFIED for pre-push readiness](validation/VAL-N01B-01-prepush-edbcee92.md)
on its named source/test paths; exact-source Ubuntu execution is pending a
separately authorized branch push. Later units still need exact
technical ownership and separate maintainer approval before product code
generation.
