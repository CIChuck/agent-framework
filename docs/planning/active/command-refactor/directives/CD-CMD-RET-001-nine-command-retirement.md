# CD-CMD-RET-001 — retire nine Chat slash commands

Date: 2026-11-06
Status: **DRAFT — awaiting exact maintainer approval; no construction authorized**
Initiative: `friday-command-refactor`
Unit: `RET-001` / `CMD-RET-001`
Execution branch: `feature/command-retirement`

## Objective and authority

Remove the nine selected commands directly from current Chat before any retained
handler migration. The supported surface becomes 41 canonical names and the
unchanged three aliases. No retired handler enters the neutral foundation.

Precedence: explicit maintainer instructions, repository engineering/independent
validation/lifecycle policies, [scope decisions S-02/O-01/O-04/O-05](../scope-decisions.md),
[build plan](../build-plan.md), [phase plan](../phase-plan.md), then this directive.
The [foundation implementation](../validation/VAL-CMD-FND-001-report.md) is VERIFIED
at `b4fc199eeef3c63a5cf9a8b960cf61c0116170ad` and subsequently accepted by Chuck
Russell in the [execution log](../execution-log.md). Acceptance covers that unit.

Proposed product/source base: `6f291ca5755a616d9185c86dff104b660a1fba8c`. Before approval, bind this exact directive hash and source commit.
Subsequent approval/status-only commits may precede execution only after a
product/input equality check records the actual starting HEAD. New product
changes or directive changes require reconciliation rather than silent rebasing.

## Decisions included in the requested approval

Approval of this directive must explicitly include the following bounded
sequencing disposition; existing RD-01 approves the foundation alone.

| Decision | Proposed disposition |
| --- | --- |
| RET-GATE-01 | Execute RET-001 immediately after the accepted foundation and before PILOT-001, as proposed in the historical unit map. Permit this deletion-only unit before completion of unrelated retained-family APIs/full P1. This does not close full P0/P1 or authorize a migration. |
| RET-GATE-02 | Retire only the slash-command behavior. Preserve startup priming, runtime configuration, automatic/native/MCP tool selection/execution and retained diagnostics. No new family/service contract is needed because no command is extracted or wired. |
| RET-GATE-03 | Preserve `CommandContext.variables` and the retained `/memory` scoped-variable metric. Preserve shared tool-budget/session/security state. Remove command-only payload injection state and dead helpers only after a repository-wide caller audit proves they have no retained consumer. Do not delete persisted data or migrate stores. |

Every affected retirement requirement below must have evidence before the unit
can be verified. Any unresolved retained-service, security or contract impact
blocks implementation of that part; this draft supplies no waiver.

## Assigned cases and exact behavior

| PAR case | Removed canonical name | Former effect to prohibit through slash dispatch |
| --- | --- | --- |
| PAR-004 | clear-tools | Clearing manual selection |
| PAR-019 | inject-payload | Staging synthetic payloads |
| PAR-020 | inject-tools | Selecting/injecting manual tools |
| PAR-027 | prime | Loading/reading priming through this command |
| PAR-030 | recommend-tools | Querying/ranking tool candidates |
| PAR-034 | run-tool | Tool calls, admission, result sanitation, state/file bookkeeping |
| PAR-039 | set | Scoped-variable writes |
| PAR-046 | tool-budget | Reading/synchronizing tool selection/budget state |
| PAR-049 | vars | Enumerating scoped variables |

Remove each name from default metadata, handler maps, help and supported-name
views. Remove `run-tool` from the admission-name set while preserving every
retained admission member. Inputs for a removed name must take the existing
ordinary unknown-command path, including its exact response, with no notices,
redirects, compatibility handlers, effects, state mutation or service access.
Test ordinary, uppercase, extra-slash and argument-bearing forms according to
the current Chat parser; do not change parsing. The three aliases stay
`quit`/`q` → `exit` and `clearscreen` → `cls`.

Retained metadata must equal the frozen pre-change snapshot minus exactly these
nine records. `/tools` retains category filtering and native/MCP diagnostics.
No completion implementation currently exists in Chat: prove the supported-name
view excludes the nine, audit consumers, and do not invent a frontend completer.

## Allowed paths and boundaries

Product changes are limited to:

- `packages/friday-chat/src/friday_chat/commands/registry.py`: exact registrations,
  mappings, retired handlers and exclusively retired helpers/imports/admission name.
- `packages/friday-chat/src/friday_chat/commands/tools.py`: remove retired handlers
  and exclusively dead helpers/exports; preserve `list_runtime_tools` for `/tools`.
- `packages/friday-chat/src/friday_chat/commands/contracts.py`: remove only proven
  command-only orphan fields; preserve `variables`, security counters and shared
  tool/session fields. An outside consumer blocks the field removal.

Test changes are limited to these files under `packages/friday-chat/tests_chat/`:
`test_command_registry.py`, `test_command_foundations.py`,
`test_session_memory_commands.py`, `test_tool_commands.py`,
`test_tool_selection_budget.py`, `test_mcp_turn_budget.py`,
`test_mcp_chat_bridge.py`, `test_command_production_adapters.py`,
`test_command_disposable_uat.py`, `test_security_speech.py`,
`test_display.py`, `test_memory_diagnostics_commands.py`,
`compat/test_command_surface_parity.py`, `compat/fixtures/parity_overrides.yaml`,
and a new `test_command_retirements.py`.

Preserve `compat/fixtures/legacy_command_names.yaml` as the historical reference;
encode the nine intentional exceptions separately and assert exact surface
equality, including retained names absent from that older fixture. Preserve
underlying automatic tool-selection, budget, native/MCP/security and runtime
tests by exercising their actual APIs with disposable fixtures instead of
retired slash handlers. Do not remove security coverage merely because the
command-local injection helper is removed. Synthetic display fixtures may use
retained commands without weakening display assertions.

Update current guides only where they advertise the retired surface:
`docs/guides/05-tools.md`, `06-agents.md`, `09-cli-reference.md`,
`11-advanced-topics.md`, `13-troubleshooting.md`,
`memory-management-guidelines.md`, `security-configuration-guidelines.md`.
Do not invent replacement diagnostics or replacement commands.

Process/evidence updates: this packet's index/checkpoint, execution log, PAR
ledger and new `validation/retirement/` receipts; command-only board/dashboard
updates. Preserve existing frozen matrices, inventories, review inputs and
receipts as historical evidence; record new hashes/results separately.

No neutral foundation edits, new package/root dependencies, lock/metadata edits,
runtime/app/tool-selection/MCP/security/priming/config implementation changes,
TUI changes, retained-handler migration, external delivery or unrelated cleanup.
If another source/test/guide path is necessary, amend the exact directive first.

## Required verification and acceptance criteria

1. Record board/branch, approval, source/API/directive identity, actual installed
   package/tool versions and protected dirty hashes. Capture current 50-name/
   three-alias metadata and applicable before-change test results before editing.
2. Add table-driven negatives for all nine names and variants with seeded state
   and fail-on-access spies for tools, selection/budgets, priming, variable access,
   admission and writes. Assert exact unknown output, no UI/exit intent and no
   former effects. Require 41 retained canonical names and exactly three aliases.
3. Compare every retained metadata record with the frozen JSON baseline and test
   aliases, help/detail, ordinary parser quirks and `/tools` categories/MCP data.
   Preserve `/memory` variable/priming metrics and shared configuration semantics.
4. Run focused affected tests, foundation/cohort, framework CLI and the full
   provider-free Chat suite before/after. Use the current committed examples and
   `TERM=xterm-256color` control in a temporary plugin, as described in
   [baseline controls](../validation/p0-failure-disposition.md). Redirect only the
   two documented test constants. Do not alter working examples or assertions.
   Do not run the old control script that overwrites historical receipts.
5. All package checks use `uv run --offline --frozen --no-sync
   --no-python-downloads --with-editable packages/friday-commands …`.
   Install the network audit guard before application imports; disable bytecode,
   pytest/Ruff caches and place mypy cache in scratch. Run focused Ruff/format,
   mypy on changed source (report existing errors separately), root Ruff/root
   pytest, package metadata, offline lock consistency, board/docs and whitespace.
   Existing root collection/lint/TUI-link failures remain separate unsuccessful
   broad gates, never a new implicit waiver. No dependency download/sync allowed.
6. Build Chat wheel/sdist offline into scratch. Inspect artifact metadata; install
   the wheel with declared dependencies from the frozen cached profile into a
   new disposable environment. If offline resolution is unavailable, stop and
   report it rather than claim installed proof. Outside the checkout with `-I`,
   guarded imports must prove 41/3, help/alias/unknown/negative-effect behavior,
   Chat `--help`, tools/finance import and absence of the retired framework launcher.
7. Preserve all unrelated dirty files and unchanged package/client boundaries.
   Record actual counts, before/after behavior, artifact/version hashes, exact
   argv/exits and skips in durable new receipts. Do not equate fewer tests with
   preserved coverage; account for each changed legacy assertion.
8. Commit a stable candidate and obtain fresh-context read-only independent
   validation against this approved directive, nine assigned PAR cases and
   retained regressions. Stop at the result for controller/maintainer handoff.

Tests/probes may use temporary files and fake/disposable runtime fixtures only;
no real providers, tool services, credentials, user stores, audio or live servers.
No whole-platform, full P1 or aggregate feature acceptance is claimed.

## Stop conditions and next gate

Stop for missing exact approval, baseline drift, unresolved affected contract,
retained behavior/security regression, required outside-path change, unavailable
installed proof or independent findings. No automatic council/remediation loop.
Next after VERIFIED is maintainer acceptance of RET-001. PILOT-001 still needs
catalog/host routing/rendering contracts and its own reviewed approved directive.
