# CD-CMD-RET-001 — retire nine Chat slash commands

Date: 2026-11-06
Status: **DRAFT — awaiting exact maintainer approval; no construction authorized**
Initiative: `friday-command-refactor`
Unit: `RET-001` / `CMD-RET-001`
Execution branch: `feature/command-retirement`

The maintainer approved strengthening this document's drift controls. That
authorizes this planning revision only; the resulting exact directive remains
draft until its construction approval is recorded.

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
| RET-GATE-03 | Apply only the explicit symbol/field disposition below. Preserve `CommandContext.variables`, the `/memory` scoped-variable metric and shared tool-budget/session/security state. Remove the four named command-only fields; a newly found retained consumer stops that removal. Do not delete persisted data or migrate stores. |

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

Retirement changes the default catalog, not the generic registration API. Do not
add a blacklist to parsing/dispatch, change normalization, or prevent an explicitly
constructed custom registry from registering an arbitrary name.

## Exact symbol and state disposition

The source/caller audit for this table uses the proposed product base above.
Recheck it before editing; discovery of another consumer requires reconciliation,
not expansion of this list. Names refer only to the named module/class.

| Location | Remove exactly | Preserve explicitly |
| --- | --- | --- |
| commands/registry.py handlers | `_prime_handler`, `_inject_payload_handler`, `_run_tool_handler`, `_recommend_tools_handler`, `_vars_handler`, `_set_handler` | Every other handler, registry/parser/help implementation and public re-export |
| commands/registry.py helpers | `_parse_tool_parameters`, `_plain_text_parameter_name`, `_missing_required_parameters`, `_sanitize_tool_result`, `_truncate_tool_output` | `_tool_parameter_names` used by retained `/tools`; `_list_runtime_tools` import; `sanitize_payload` used by `/security-test`; all other helpers |
| commands/registry.py catalog | Exactly nine entries in `DEFAULT_COMMAND_SPECS` and `BASIC_COMMAND_HANDLERS`; only `run-tool` in `_SHARED_ADMISSION_COMMANDS` | All 41 remaining metadata records, three aliases and six other admission members |
| commands/tools.py | `find_tool`, `inject_tools_handler`, `clear_tools_handler`, `tool_budget_handler`, `_selection_error_text`, `_format_names`, `_display_text`; corresponding retired exports | Module path and `list_runtime_tools`, its existing behavior and public export |
| CommandContext in commands/contracts.py | `injected_payload`, `tool_results`, `tool_lifecycle_records`, `tool_ingestions` | Every other field, default and property, including `variables`, `last_tool_budget_snapshot`, `security_stats`, history/session/runtime/progress and exit state |

The four removed fields have only retired-command production consumers in
registry.py; tests of those retired effects are accounted for below. The
similarly named `tool_results` on transcript, turn, agent and memory models are
different contracts and must remain untouched. `variables` is still read by
commands/memory.py; `last_tool_budget_snapshot` is written by app.py. No other
field cleanup is authorized. Remove only imports/exports made unused by the
listed removals; shared imports and module behavior must be preserved.

## Pinned behavior oracles

Use [command-matrix.json](../validation/command-matrix.json), SHA-256
`87c7880b21bbd7b02f227a7f93373dc3acc67db91e3ced18fd65511c34081f85`,
as the immutable 50-record metadata oracle. Its `commands` array, minus the nine
named records, defines the exact retained set and metadata; count alone is not
acceptance. Canonicalize runtime tuples to JSON arrays before value comparison.
Do not regenerate this oracle from the changed implementation.

Unknown output is exactly `Unknown command: /{parsed_name}. Type /help for available commands.`
and the result is handled, with no exit request or UI effects. For each retired
name `r`, fixtures must independently expect:

| Input | Expected result |
| --- | --- |
| `/r`, `/R` (uppercase), `//r`, `/ /r`, `/r argument`, `/r "a b"` | Ordinary unknown response with parsed name `r`; zero former effects |
| `///r` | Ordinary unknown response with parsed name `/r`, therefore the output contains `//r`; no second normalization |
| ` /r` | Non-command `(False, None)`, preserving the leading-space quirk |

Substitute every actual retired name; do not literally test only `r`. Seed
nonempty variables, tool/session/security state and verify snapshots unchanged.
Use fail-on-access spies to establish zero runtime/tool/priming/admission access,
zero writes and zero callbacks. Test unknown dispatch both without a runtime and
with those spies; a happy-path output assertion alone is insufficient.

## Allowed paths and boundaries

Product changes are limited to:

- `packages/friday-chat/src/friday_chat/commands/registry.py`: only the exact
  symbol/catalog/import changes in the disposition table.
- `packages/friday-chat/src/friday_chat/commands/tools.py`: only the table's exact
  removals and directly unused imports; preserve the retained inventory function.
- `packages/friday-chat/src/friday_chat/commands/contracts.py`: only the four
  named CommandContext fields. A retained consumer blocks removal.

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

Before source edits, record an assertion-disposition ledger in new
`validation/retirement/` evidence: original node/function, parameter cases,
assertion source/hash, disposition, replacement node/API and expected evidence.
Every rewritten or removed assertion must be covered. The following fixed map
controls its classification; unlisted retained assertions/parameter cases must
stay logically unchanged. Formatting with identical test ASTs is permitted.

| Existing file / node group | Required treatment |
| --- | --- |
| test_tool_commands.py: `test_run_tool_supports_json_and_plain_text_parameters`, `test_run_tool_validation_errors_are_user_facing`, `test_tool_sanitization_updates_security_stats`, `test_tool_result_truncation_lifecycle_and_ingestion_tracking`, `test_inject_clear_and_tool_budget_commands`, `test_recommend_tools_returns_scored_results` | Retire assertions of these removed slash behaviors and replace their command reachability with nine-name negative coverage. Preserve every existing ToolLoop, heartbeat, circuit-breaker and pruning test in the same file. Do not reproduce the deleted manual-execution sanitizer/bookkeeping in a new helper. |
| test_security_speech.py: `test_injected_payload_is_single_use` | Replace the retired payload/manual-run scenario with unknown/no-effect checks. Preserve all other sanitizer, security counters/config rollback, speech and cancellation assertions. |
| test_session_memory_commands.py: `test_vars_and_set_commands`, `test_basic_memory_diagnostic_commands_with_fake_runtime` | Replace set/vars/prime command expectations with negatives. Preserve every retained diagnostic assertion; seed `context.variables` directly for retained `/memory` metric coverage and preserve runtime priming observations. |
| test_tool_selection_budget.py: `test_manual_mode_persists_exact_set_until_clear_restores_automatic`, `test_tool_budget_reports_no_turn_manual_selected_and_executed_states`, `test_clear_uses_prior_automatic_estimate_and_keeps_last_manual_turn`, `test_clear_without_prior_automatic_turn_reports_honest_pre_turn_state`, `test_disabled_and_empty_registries_offer_zero_schemas`, `test_command_display_sanitizes_and_bounds_untrusted_tool_metadata` | Retire deleted-command presentation assertions. Exercise existing public selection APIs (`inject_manual`, `clear_manual`, selection snapshots) for the retained atomicity/order/budget/model-byte guarantees; preserve unsafe-metadata rendering checks on retained `/tools` wherever applicable. No replacement tool-budget renderer or selection implementation. |
| test_mcp_turn_budget.py: `test_retrieval_receives_exact_budget_before_model`; test_command_production_adapters.py: `test_tool_budget_reports_schemas_selected_for_real_turn` | Replace only calls/assertions on the removed budget handler with existing runtime/turn snapshot evidence; preserve exact model schema bytes, retrieval allocation, accounting and production-adapter guarantees. |
| test_mcp_chat_bridge.py: `test_real_stdio_chat_turn_routes_exact_name_and_stops`; test_command_disposable_uat.py: `test_real_app_cli_pty_command_uat_is_contained_and_provider_free` | Remove retired slash steps, replace with negatives as appropriate, and retain actual model/tool execution, MCP routing, containment, exit/clear/transcript and cleanup evidence through current public seams. |
| test_command_registry.py: `test_remediated_command_help_documents_final_runtime_contracts`; test_command_foundations.py: `test_affected_handlers_are_owned_by_their_category_modules` | Remove only nine-name metadata/ownership expectations; retain every other record/assertion. Add exact 41/3, alias and help checks. |
| test_display.py: `test_generic_output_sink_preserves_literal_help_arguments` | Replace its synthetic `/run-tool` text with retained-command text; preserve literal-output equality assertions. |
| compat/test_command_surface_parity.py and parity_overrides.yaml | Preserve the historical fixture; record precisely the nine deliberate exclusions and assert full exact supported-set equality, including newer retained commands. |

Shared fixture/metadata helpers may be adjusted solely to use retained names or
the same public API needed by these rows. Any additional test-logic change must
be listed with its original assertion and justified under an existing row before
editing; an unmapped behavior change stops for directive reconciliation. Never
xfail, skip, delete or soften retained checks to obtain green results. Counts may
change, but every retired and replacement assertion must be accounted for.

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
   two documented test constants. The control plugin must not alter working
   examples or test assertions; authorized test edits follow the fixed map above.
   Do not run the old control script that overwrites historical receipts.
5. All package checks use `uv run --offline --frozen --no-sync
   --no-python-downloads --with-editable packages/friday-commands …`.
   Install the network audit guard before application imports; disable bytecode,
   pytest/Ruff caches and place mypy cache in scratch. Run focused Ruff/format,
   mypy on changed source (report existing errors separately), root Ruff/root
   pytest, package metadata, offline lock consistency, board/docs and whitespace.
   Only the precisely documented root collection/lint and older-format failures
   in the merged checkpoint may be classified as baseline, after source/input
   equivalence. TUI links were repaired: documentation lifecycle must pass.
   A new link, lint, format or collection failure is a regression, not baseline.
   No dependency download/sync allowed.
6. Build Chat wheel/sdist offline from a clean archive of the frozen candidate
   Git tree, with output in scratch. Never build from this mixed working tree:
   its two uncommitted examples must not enter artifacts. Inspect metadata; install
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

Tests/probes may use temporary files and fake/disposable runtime fixtures only.
Disposable loopback-only HTTP/stdio test fixtures are permitted, must be owned by
the test, and must be shut down on success/failure/cancellation. No external
application destinations, registry downloads, real providers/tool services,
credentials, user stores, audio, pre-existing local services or live external
servers. The guard must be installed before imports and inherited by test child
processes. A fixture-containment failure stops testing; do not disable the guard.
No whole-platform, full P1 or aggregate feature acceptance is claimed.

## Reproducible verification recipe

Run from the repository root, first with `RET_PHASE=before` against unchanged
product bytes, then with `RET_PHASE=after` against the committed implementation
candidate. Use a different fresh scratch directory for each phase. Do not run
these instructions during directive-only preparation. Record every actual argv,
exit, source identity and output; do not infer a full suite pass from a subset.

The reviewed harness is embedded as data in
[verified-evidence.json](../validation/checkpoint/verified-evidence.json).
Extract only the three named files after checking their embedded text hashes;
never execute arbitrary members of that evidence bundle. This pins the actual
guard, sanitized subprocess runner and committed-example control instead of
asking the builder to invent an equivalent harness.

```sh
RET_PHASE=before                 # use after for the committed after-change lane
RET_SCRATCH=$(mktemp -d -t friday-ret-check)
export RET_SCRATCH RET_PHASE
python3 -B - <<'PY'
import hashlib, json, os, pathlib, subprocess
root = pathlib.Path.cwd()
scratch = pathlib.Path(os.environ['RET_SCRATCH'])
bundle = root / 'docs/planning/active/command-refactor/validation/checkpoint/verified-evidence.json'
if hashlib.sha256(bundle.read_bytes()).hexdigest() != '9da84625482273524bd9fd74867251a147d6d5b271d6ea1a52bc9a5411af513e':
    raise SystemExit('Reviewed evidence bundle changed')
evidence = json.loads(bundle.read_text())['files']
pins = {
    'run.py': '409769f1c17a63fcbd7ea2bd3d079af315dcc9afabca8bd35602033c198124af',
    'controls.py': 'd62238fd3fac3188f9464604cf091ed2eeb4d9ad76ef21f1f796b3b7af0ba20d',
    'sitecustomize.py': 'dab06413128cd2b2e2cad75470dd1a9ed0341216d1fcac6c2de7c42e10f911bf',
}
for name, expected in pins.items():
    text = evidence[name]['text']
    if hashlib.sha256(text.encode()).hexdigest() != expected:
        raise SystemExit(f'Harness hash mismatch: {name}')
    (scratch / name).write_text(text)
# The reviewed guard blocks connects/sends; add explicit DNS/bind containment.
# Record the combined helper hashes and negative self-tests in this unit's receipt.
with (scratch / 'sitecustomize.py').open('a') as guard:
    guard.write('''
def _ret_extra_audit(event, args):
    if event in ('socket.getaddrinfo', 'socket.gethostbyname', 'socket.gethostbyaddr'):
        if args[0] not in ('localhost', '127.0.0.1', '::1'):
            raise RuntimeError('Retirement DNS guard blocked destination')
    if event == 'socket.bind':
        address = args[1]
        if not isinstance(address, tuple) or address[0] not in ('localhost', '127.0.0.1', '::1'):
            raise RuntimeError('Retirement bind guard blocked destination')
sys.addaudithook(_ret_extra_audit)
''')
for name in ('config.example.yaml', 'models-config.example.yaml'):
    data = subprocess.check_output(['git', 'show',
        f'6f291ca5755a616d9185c86dff104b660a1fba8c:packages/friday-chat/{name}'])
    (scratch / name).write_bytes(data)
PY
# macOS/APFS cache clone: no root environment sync and no downloads.
# If cloning is unavailable, use an ordinary copy to a new scratch cache;
# never empty or alter the existing cache to make a check pass.
cp -cR "$(uv cache dir)" "$RET_SCRATCH/uv-cache"
ret_check() { python3 -B "$RET_SCRATCH/run.py" "$RET_PHASE-$1" "${@:2}"; }
ret_check origin python -B -c 'from pathlib import Path; import friday_commands; assert Path("packages/friday-commands/src").resolve() in Path(friday_commands.__file__).resolve().parents'
ret_check chat python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-chat/tests_chat --ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py
ret_check foundation python -B -m pytest -p no:cacheprovider -q packages/friday-commands/tests_commands tests/integration/test_package_cohort_metadata.py
ret_check cli python -B -m pytest -p no:cacheprovider -q packages/friday-cli/tests_cli
ret_check lint ruff check --no-cache packages/friday-chat/src/friday_chat/commands/registry.py packages/friday-chat/src/friday_chat/commands/tools.py packages/friday-chat/src/friday_chat/commands/contracts.py packages/friday-chat/tests_chat
ret_check format ruff format --check --no-cache packages/friday-chat/src/friday_chat/commands/registry.py packages/friday-chat/src/friday_chat/commands/tools.py packages/friday-chat/src/friday_chat/commands/contracts.py packages/friday-chat/tests_chat
ret_check types mypy packages/friday-chat/src/friday_chat/commands/registry.py packages/friday-chat/src/friday_chat/commands/tools.py packages/friday-chat/src/friday_chat/commands/contracts.py
ret_check root-lint ruff check --no-cache .
ret_check root-tests python -B -m pytest -p no:cacheprovider -q
ret_check metadata python -B scripts/check-package-metadata.py
ret_check board python -B scripts/friday-dev-board.py validate
ret_check docs python -B scripts/check-documentation-lifecycle.py
uv lock --check --offline --no-python-downloads
git diff --check
```

Run all commands and retain nonzero outcomes; do not hide later checks behind an
early shell exit. Successful before/after Chat lanes must run the complete
provider-free suite without new skips/xfails or collection errors. The prior
826 count is a reference, not the required after-change count. Legacy formatting,
lint and typing debt must be reproduced on the pinned base with identical tools;
require changed-code checks to introduce no new finding. Known root pytest
collision is not permission for any second collection error. Docs must exit zero.
The new retirement test file, included by full Chat discovery, must implement
every pinned input/negative-effect and exact-metadata oracle above.

For packaging, commit the exact candidate before export. Output-in-scratch alone
is insufficient: export inputs from Git, not from the working examples.

```sh
RET_CANDIDATE=$(git rev-parse HEAD)
RET_BUILD=$(mktemp -d -t friday-ret-build)
git archive "$RET_CANDIDATE" | tar -xf - -C "$RET_BUILD"
(cd "$RET_BUILD" && uv build --offline --no-python-downloads --package friday-chat --out-dir "$RET_SCRATCH/dist")
ret_check artifacts python -B scripts/check-package-artifacts.py --package friday_chat "$RET_SCRATCH/dist"
uv venv --no-python-downloads --python .venv/bin/python "$RET_SCRATCH/installed"
python3 -B - <<'PY'
import hashlib, json, os, pathlib
profile = pathlib.Path('docs/planning/active/command-refactor/validation/required-finance/installed.json')
if hashlib.sha256(profile.read_bytes()).hexdigest() != 'd28035601c666363e90f90fa33a818a43fe4f3d1607f0b8afa0bcd0510c7bbb1':
    raise SystemExit('Frozen dependency profile changed')
rows = json.loads(profile.read_text())
if len(rows) != 129:
    raise SystemExit('Unexpected frozen default profile')
(pathlib.Path(os.environ['RET_SCRATCH']) / 'locked-profile.txt').write_text(
    ''.join(f"{row['name']}=={row['version']}\n" for row in rows))
PY
uv pip install --offline --no-deps --python "$RET_SCRATCH/installed/bin/python" -r "$RET_SCRATCH/locked-profile.txt"
uv pip install --offline --no-deps --python "$RET_SCRATCH/installed/bin/python" "$RET_SCRATCH/dist/friday_chat-0.1.0a4-py3-none-any.whl"
uv pip check --offline --python "$RET_SCRATCH/installed/bin/python"
```

That requirements file comes from the exact 129-distribution
[default profile](../validation/required-finance/installed.json), not the root
development environment. Pin its hash before use, as with the other inputs.
Resolve only those exact cached versions, then override Chat with
the freshly built wheel. Verify all reused Friday wheel sources/metadata equal
candidate Git bytes; build matching wheels offline if needed, or stop. Do not
accept a cached same-version wheel merely because its name matches. Use the
recorded profile as installation evidence, not as an unchanged 50-name oracle.

Run installed probes outside the checkout with isolated Python `-I -B`; install
the guard explicitly before imports because `-I` ignores PYTHONPATH. Reuse the
new retirement test oracles, not a copied pre-retirement probe asserting 50/3.
Verify package origins, dependency metadata, all installed source/config bytes
against the candidate/wheel, 41/3/catalog/aliases/help/unknown/no-effects, finance
and SDK imports, Chat entry-point help and absence of a `friday` console script.
Record both protected working-example hashes before/after export/build/install.
No working-copy config, credential, `.env` or `.friday` data may enter artifacts.

Before validator handoff, require a complete base-to-candidate path audit: only
the three allowed product files, enumerated tests/guides and process records may
differ. Verify the exact nine-name subtraction, all retained metadata, every
assertion disposition and all protected hashes. A scope violation stops the unit
even when tests pass. Freeze this directive and all authority/oracle hashes in
the independent request; do not let the builder silently revise acceptance.

## Stop conditions and next gate

Stop for missing exact approval, baseline drift, unresolved affected contract,
retained behavior/security regression, required outside-path change, unavailable
installed proof or independent findings. No automatic council/remediation loop.
Next after VERIFIED is maintainer acceptance of RET-001. PILOT-001 still needs
catalog/host routing/rendering contracts and its own reviewed approved directive.
