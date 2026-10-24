# Friday slash-command refactor — feature intent and design rationale

**Status:** Canonical feature-intent and design-rationale document, begun
2026-10-19. Its established direction and maintainer clarifications guide this
branch; sections labeled as candidates or proposals are not accepted contracts.
It does not authorize product-code work. The [scope decision register](scope-decisions.md)
reconciles current retirement decisions and open choices with the
[scored inventory](command-inventory.md). The [command matrix](command-matrix.md)
remains the 50-command before-change baseline. Accepted TUI decision D-123
(`01cbaa0b:docs/planning/active/friday-tui/decisions.md`) is historical
context for the shared-owner requirement.

**Initiative handoff, 2026-10-24:** The
[shared Friday command refactor](README.md)
is now a separate active project with its own
[build plan](build-plan.md) and
[regression strategy](test-strategy.md).
This intent document and the TUI matrix remain linked canonical inputs. The
separate project owns Chat extraction and cross-client regression; Friday TUI owns its
later adapter and parity/UAT work. The separate `friday-framework-cli` package's
direct-consumer role is an open technical-contract decision, while its existing
behavior remains protected.

This note and the [command matrix](command-matrix.md) are companion planning
artifacts: the matrix identifies each current parity case, while this note
records the migration direction and candidate pruning ideas that could change
those cases. Reconcile them together when a command decision is accepted.
The [command inventory and scoring sheet](command-inventory.md) puts every
current command and architecture opportunity in one place for the maintainer's
value score and migration decision. Its recommendations do not change the
accepted baseline.
Its [consolidation recommendations](command-inventory.md#consolidation-recommendations)
are a separate scored section near the top of that sheet.
The [source-backed pruning review](command-pruning-review.md) preserves an
earlier seven-command recommendation. The maintainer has instead selected six
specific retirements for the shared command refactor; the current 50-command
as-built baseline remains in force until scope and construction are reconciled.

## Why we are considering this work

Friday TUI needs the maintained Friday Chat `/` commands to behave the same way
in both frontends without copying their implementations. The TUI must be an
independently installable package that does not import or depend on
`friday-chat` or `friday-cli`. Commands should also be able to grow over time:
one change to a maintained command should reach both clients, while TUI-only
commands can remain separate.

The maintained conversational slash commands currently live primarily in
[`friday_chat.commands.registry`](../../../../packages/friday-chat/src/friday_chat/commands/registry.py)
and neighboring `friday_chat.commands` modules. The similarly named
[`friday_cli.commands`](../../../../packages/friday-cli/src/friday_cli/commands.py)
is a generic registry for the separate `friday-framework-cli` package; it is
not the maintained Friday Chat slash-command implementation. The package
called `friday-cli` must retain its current feature set and behavior. In this
note, **Chat command refactor** means work on the Friday Chat `/` surface and
its supporting command code, not a rewrite of `friday-cli`.

The [shared-command architecture](shared-command-architecture.md) proposes a
UI-neutral command owner below Friday Chat and Friday TUI. The proposed
`friday-framework-commands` package name, API, and migration units are not
yet accepted technical contracts. Reusing Friday's runtime and services is
essential; importing Friday Chat handlers into the TUI, wrapping the Chat
application, or maintaining parallel TUI handlers would violate the agreed
boundary.

The command boundary has two parts. The shared owner resolves invocation
(name/alias, parameters, defaults, validation) and performs execution through
Friday's services, returning the same semantic outcome and effect intents for
equivalent state. Each frontend renders that outcome in its own interface.
The CLI's existing output text remains a compatibility obligation for retained
commands, but the TUI must not have to parse CLI-formatted text to obtain
structured command data. The proposed contract and separate parity checks are
described in the [architecture note](shared-command-architecture.md#invocation-execution-and-presentation-boundary).

The longer-lived purpose is to let the Friday harness evolve. Domain packages
and Runtime should own new capabilities and expose coherent public operations;
the shared command layer should expose selected capabilities to both clients
without reproducing domain logic. Neither frontend should need changes when
an existing service improves behind its stable contract. See the
[framework evolution rule](shared-command-architecture.md#framework-evolution-rule)
for the dependency and extension criteria.

## Direction established in conversation

1. Treat the Chat command architecture as a separate board initiative, then
   connect the TUI to its accepted shared command owner as a later TUI phase.
   This reduces the risk of discovering Chat compatibility failures while
   simultaneously building TUI interactions.
2. Capture existing Chat command behavior before changing it. A refactor must
   preserve the behavior of every **retained** command: names and aliases,
   syntax, defaults, validation, result meaning, errors, session and runtime
   effects, and file/tool effects. Presentation may differ by frontend where a
   typed result explicitly requests a UI effect.
3. Use substantial Friday Chat regression coverage, plus the separate
   `friday-cli` regression baseline, installed-package checks, and independent
   validation before treating the shared engine as ready for TUI use. TUI
   parity then compares both frontends on equivalent disposable fixtures and
   includes terminal UAT.
4. Retire the six selected slash commands as an explicit scope unit in
   the shared command refactor. This intentional change needs its own
   compatibility checks and must not be treated as a behavior-preserving
   extraction or an unnoticed test failure. Old-name behavior still needs a
   decision.

This fourth point qualifies the earlier blanket preservation language in
D-123 (`01cbaa0b:docs/planning/active/friday-tui/decisions.md`), the TUI PRD draft
(`../friday-tui/prd/README.md`), the TUI vision draft
(`../friday-tui/vision/README.md`), the TUI phase plan
(`01cbaa0b:docs/planning/active/friday-tui/planning/phase-build-plan.md`), and the
[50-command matrix](command-matrix.md). Those documents still describe all 50
currently maintained commands and unchanged Chat behavior. The selected
six-command retirement is a product-scope decision for the shared refactor;
the as-built parity baseline is not silently rewritten. Before construction,
reconcile the decision record,
release scope, matrix/acceptance cases, phase gates, help, user guides, and
tests before claiming full command parity against a reduced set. Preserve
interactive `/replay` and startup replay unless their separately accepted
requirements are explicitly reopened.

## Source-backed pruning candidates, not decisions

The following is an initial value review of current handlers, not evidence of
user adoption or a final removal recommendation. Usage telemetry and external
consumer impact have not been established.

| Commands | Current implementation observed | Possible disposition to evaluate |
| --- | --- | --- |
| `/set`, `/vars` | Store and list variables on Chat command context. The source search found no operational consumer beyond listing and a memory metric. | Retire together if no supported workflow relies on them, or define a real purpose before migrating them. |
| `/prime` | Reports the configured priming `enabled` and `previous_sessions` values; it does not itself load primed context, despite its current description. | Fold the status into `/memory` or correct and retain the command. |
| `/speech-test` | Makes one speech-adapter call for either `once` or `loop`; `loop` is not a continuous loop. | Move validation to a diagnostic/test surface, or retain with accurate semantics. |
| `/security-test`, `/inject-payload` | Exercise fixed sanitizer samples and stage synthetic content for the next manual `/run-tool` result, respectively. | Consider removing from the normal user command set or placing behind an explicit diagnostics surface. Review the tool-testing workflow first. |
| `/recommend-tools` | Ranks registered tools by query-word substring matches against metadata and labels any match `high` confidence. | Retire, consolidate with `/tools`, or redesign if users need recommendation quality. |
| `/debug-budget` | Reports configured `context_window` and `output_buffer`, not an assembled request budget. | Consider consolidation into diagnostics or a more accurate label; do not remove without assessing its troubleshooting value. |

The observations above come from the Chat
[`registry.py` handlers](../../../../packages/friday-chat/src/friday_chat/commands/registry.py)
and [`memory.py` metric](../../../../packages/friday-chat/src/friday_chat/commands/memory.py).
The current [CLI reference](../../../guides/09-cli-reference.md) also documents
these commands, so an accepted removal would have user-facing documentation
and compatibility consequences. `/clear` and `/cls` have distinct effects and
should not be treated as duplicate names. Core runtime, session, tool,
maintenance, and workflow commands have not been assessed for pruning merely
because they are complex or infrequently visible.

## Proposed work order and evidence gates

1. **Characterize the baseline.** Inventory the live Chat registry and
   aliases, identify handler/service dependencies, and capture positive,
   negative, unavailable-service, state, and side-effect behavior by command
   family. Use the current matrix as the starting inventory; do not infer
   parity from names or help text alone.
2. **Set the supported command surface.** Decide each candidate's fate:
   retain, consolidate, move to diagnostics, deprecate, or retire. Record
   affected users, replacement path, compatibility period if any, and expected
   behavior for an old command name. Update the accepted parity baseline only
   after these product decisions are made. Where practical, prune before
   extracting handlers so low-value code is not migrated needlessly.
3. **Refactor Friday Chat in bounded command families.** Define typed neutral
   context, capability, result, and UI-effect contracts; move one command
   implementation at a time to the shared owner; keep Chat's existing
   executable and presentation. Remove each old active handler after Chat
   delegates to the shared one, so two implementations do not persist.
4. **Prove Chat compatibility.** For retained commands, compare before/after
   parsing, aliases, help, outputs and meaning, errors, session/runtime state,
   and file/tool effects. For intentionally changed commands, test the
   approved replacement or retired-name behavior and confirm help/docs match.
   Run focused and broader Chat regressions, protected `friday-cli` checks,
   package installation/import checks, and independent review. Do not count
   expected pruning changes as regressions, or use them to excuse unrelated
   changes.
5. **Integrate Friday TUI.** Depend on the shared owner, not a CLI package.
   Test matching maintained-command effects through both installed clients,
   TUI-specific rendering and navigation, command discovery/completion,
   extension isolation, and macOS/Linux terminal UAT at the applicable gates.

This ordering is a planning proposal, not a construction directive. The
[separate initiative](README.md) owns
the refactor sequence, and the historical TUI phase build plan
(`01cbaa0b:docs/planning/active/friday-tui/planning/phase-build-plan.md`)
owns only TUI integration. The board, approved
construction directives, and independent-validation policy govern any later
code work.

## First proposed design and migration slice

The current-source check on 2026-10-22 still finds 50 canonical Chat commands
and three aliases (`/quit`, `/q`, `/clearscreen`). The focused registry,
foundation and command-surface parity tests pass (22 tests). This is a useful
baseline for planning, not installed parity or approval to edit source.

The first contract review should settle the neutral package owner and a narrow
invocation/result API before moving handlers. Today
`friday_chat.commands.registry.CommandRegistry` owns normalization, alias
resolution, dispatch and help; `CommandContext` carries concrete Chat runtime
and session types, while `RegistryCommandContext` adds Chat's maintenance gate
and reorganization coordinator. `/help` reaches back to the active registry,
and `FridayChatApp` consumes output, exit intent and display effects. Moving
that code wholesale would carry Chat-owned types into the shared package.

**Proposed first construction unit, after contract and directive approval:**
move command metadata, name/alias resolution, argument tokenization, generated
help and the `/help`, `/exit` and `/cls` semantics into the neutral owner.
Keep Chat's established help text, exit handling and screen-clear result through
its existing application boundary. The remaining Chat handlers may be bound
temporarily by Chat while their command families are migrated; they must not
be exposed to the TUI as shared implementations or copied into TUI handlers.
The neutral owner must not import `friday_chat`, `friday_cli`, Textual, Rich or
Chat's private runtime/session types. A typed context/capability boundary must
be reviewed before any handler needing Chat state moves across it.

The first unit's comparison should cover the exact 50/3 registry inventory;
all command and alias help, normalization and unknown-command text; focused
help; `/exit`, `/quit` and `/q` exit intent; `/cls` and `/clearscreen` clear
intent and no replacement output; unchanged Chat rendering; unchanged
`friday-cli` tests; and isolated installed package imports and entry points.
Check that the neutral package installs without either frontend and that the
TUI dependency closure still excludes both CLI packages. Run independent
read-only review on a frozen candidate. Later units migrate service-owning
families one at a time with disposable effect comparisons, then connect TUI
to the same implementations.

The six selected command retirements belong in the shared command
refactor, but require a reconciled baseline, old-name behavior, acceptance
checks and a bounded construction directive before any source change. TUI
development is deferred until the command refactor is completed, tested and
accepted; a command construction unit needs its own reconciled board/packet
state and exact maintainer-approved directive.

## Maintainer clarifications, 2026-10-22

- Migrate `/security`, `/security-config`, `/security-test`, `/workflow` and
  `/speech-test` with their current behavior. The security and
  workflow capability reviews belong in the
  [command follow-up backlog](../../backlog/friday-tui-command-followups/README.md).
- Retain `/tools` as a read-only list of loaded, valid tools. Its presentation
  improvement is backlog work. Five other tool slash commands and
  `/inject-payload` are marked for retirement within the shared command
  refactor.
- Retain `/migrate` in the first TUI version. Any later retirement is separate
  backlog work.
- Preserve current behavior during the command refactor. Confirmation for
  `/clear` and `/reset`, ingested-source validation, diagnostic presentation,
  file-to-context attachment and other enhancements are separate follow-ups.
- Add transcript-session restoration through `/sessions` to the backlog. The
  accepted first-release matrix still covers listing, inspection and export
  without an active session switch.
- Put scored consolidation proposals C-01 through C-06 in the backlog. Keep
  current command names, aliases and syntax during the refactor.
- Disregard the inventory comment about transcript model identification for
  this scope; it is not a command-refactor requirement or backlog item.

## Open decisions

- For each removal, should an old name return a migration message for a period
  or immediately become unknown? What release boundary communicates it?
- Is `friday-framework-commands` the right owner/package, and what typed
  context and UI-effect API should its first bounded migration use?
- Which currently documented Chat behaviors are compatibility commitments
  versus existing defects to correct through a later explicit decision?
  `/prime` remains unsettled; `/speech-test loop` migrates with its current
  behavior in this refactor.
