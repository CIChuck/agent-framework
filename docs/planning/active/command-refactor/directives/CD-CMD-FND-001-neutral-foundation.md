# CD-CMD-FND-001 — neutral command foundation

Date: 2026-11-04
Revision: 2026-11-05 — bounded council findings SOL3-ARCH-001–003
Status: DRAFT — not approved; product implementation not authorized
Initiative: `friday-command-refactor`
Work unit: `CMD-FND-001`; proposed P2 foundation slice, not P2 completion
Branch: `feature/command-refactor`
Baseline inspected: `25d2dcb6`; exact execution base must be frozen at approval

## Role, authority and entry conditions

Builder implements only the approved foundation API. Follow repository
`AGENTS.md`, engineering/independent-validation policies, the board,
[scope decisions](../scope-decisions.md), [phase plan](../phase-plan.md) and
[API draft](../shared-command-api.md). This directive remains a draft until
maintainer approval and the exact API revision/base are recorded. Independent
architecture review and applicable P0/P1 gates must be satisfied or explicitly
amended by the maintainer; the scope decisions alone do not waive those gates.

Before construction, record the full execution-base SHA, authority file digests,
accepted API-01–API-06 criteria and review disposition in the unit report. Run
board validate/next/show and confirm started/granted/current branch. Unresolved
family behavior and installed baseline gaps cannot be silently waived; the
maintainer must explicitly confirm this foundation-only unit's readiness.

## Objective and non-goals

Create a separately installable, standard-library-only neutral foundation with
typed metadata/requests/outcomes and a registry supporting injected handlers.
Implement exactly the foundation types/signatures in the approved API revision.

Do not add production default handlers, wire Chat/TUI, move any handler, remove
any of the nine names yet, alter generic CLI, fix the missing generic CLI entry
point, change example configs, add provider/domain transports, alter persistence
or admission gates, implement family capabilities, or expose a new executable.
No push, PR, merge, release or deployment is authorized by this directive.

## Exact allowed paths

New package metadata:

- `packages/friday-commands/pyproject.toml`
- `packages/friday-commands/README.md`
- `uv.lock` — only workspace resolution for the new local package; no unrelated upgrades

New source:

- `packages/friday-commands/src/friday_commands/__init__.py`
- `packages/friday-commands/src/friday_commands/py.typed`
- `packages/friday-commands/src/friday_commands/contracts.py`
- `packages/friday-commands/src/friday_commands/registry.py`

New tests:

- `packages/friday-commands/tests_commands/test_contracts.py`
- `packages/friday-commands/tests_commands/test_registry.py`
- `packages/friday-commands/tests_commands/test_import_boundary.py`

Unit receipts only:

- `docs/planning/active/command-refactor/validation/CMD-FND-001-report.md`

No root metadata edit is expected: the workspace already includes `packages/*`.
If root metadata, existing package files or any additional path is required,
stop and request a bounded amendment. Do not stage the unrelated backlog/config
edits. Board/controller state transitions and independent-review reports are
controller/reviewer responsibilities, not builder-owned acceptance.

## Workstreams and acceptance

1. **FND-01 packaging / API-01:** distribution `friday-framework-commands`, import
   `friday_commands`, version 0.1.0a4, Python >=3.13.4. Match existing Hatchling
   packaging convention, ship `py.typed`, no runtime dependencies or scripts.
   Exports must match the approved API draft; no hidden frontend imports.
2. **FND-02 contracts / API-04:** frozen typed metadata, request/execution,
   closed `FoundationData` union, error/UI-effect/outcome/dispatch models. Enforce
   every row of the API runtime-validation table with exact TypeError/ValueError
   boundaries; no trusted-only constructor bypass; no source-level mypy blanket
   suppression, `Any`, casts hiding an interface defect, or untyped payload escape.
3. **FND-03 registry / API-02–API-03:** normalized canonical/alias maps, immutable
   snapshots, rebuilt canonical stored specs, one-pass normalization, explicit
   blank-alias rejection, deterministic ordering and atomic registration failures.
   Current Chat whitespace grammar, unknown and noncommand semantics are fixed.
   No generic enforcement of metadata choices/required args or shell tokenization.
4. **FND-04 execution / API-05–API-06:** await one injected async handler once;
   propagate unexpected exceptions and cancellation. No I/O, host state mutation,
   UI application, retries, built-in/default handler set or automatic discovery.

## Meaningful tests

- Metadata rejection: blank normalized canonical name/alias, blank trimmed
  description/category/usage, blank argument name/description,
  canonical collision, alias collision and same-call duplicate alias. Compare
  full registry state before/after each failure to prove no partial registration.
  Mixed-case/slashed/padded inputs must yield canonical keys from names() and
  matching rebuilt spec values through resolve()/specs()/request, while leaving
  caller input unchanged. Test
  normalization collisions and the non-idempotent normalization-order examples.
- Copy/freeze invariants: caller collection changes cannot change registered
  metadata; returned names/spec snapshots cannot mutate the registry.
- Parsing: ordinary text, leading space before slash, bare slash, uppercase name,
  extra whitespace, aliases, quoted fragments, //HELP, ///HELP and slash/space
  normalization order. Use the independent API fixture table exactly, including
  zero handler calls for the unresolved /help key from ///HELP. Expected sequences
  come from P0 observations, not a call to the implementation under test.
- Dispatch: unknown name calls no handler; alias delivers canonical request;
  exact argument spelling/order; one awaited call; synthetic handler exception
  and cancellation are propagated, not wrapped or retried. Non-callable handlers,
  nonawaitable returns, invalid outcome types and invalid execute input/context
  types raise TypeError at the specified boundary without retry.
- Constructor negatives cover every row of the runtime-validation table: wrong
  scalar/container/member types (including bool-vs-int), opaque/subclass payloads,
  invalid error codes, raw-string UI effects, mismatched request/spec names, both/
  neither data/error and invalid handled/outcome/effect combinations. Assert the
  exact built-in exception class. Test copied finite iterables and immutability;
  metadata blank-value semantics remain registration checks, not argument policy.
  Exit/clear data are returned, not applied. NoData remains typed semantic data.
- Boundary: importing foundation with frontend modules blocked succeeds; static
  imports and built wheel contain no frontend/domain dependency. Synthetic
  handlers only; no live provider or tool execution and no persisted stores.

Freeze the expected token/result fixtures in tests independently of the new
implementation. There are no command-family parity claims from synthetic cases.
The existing 50-name baseline remains unchanged in Chat throughout this unit.

## Verification commands and expected results

From repository root:

```sh
uv run pytest -q packages/friday-commands/tests_commands
uv run ruff check packages/friday-commands
uv run ruff format --check packages/friday-commands
uv run mypy packages/friday-commands/src
uv run pytest -q packages/friday-chat/tests_chat/test_command_registry.py packages/friday-chat/tests_chat/test_command_foundations.py
uv run pytest -q packages/friday-cli/tests_cli
uv run python scripts/friday-dev-board.py validate
uv run python scripts/check-documentation-lifecycle.py
git diff --check
```

All new-package checks and the registry/foundation Chat suites must pass; generic
CLI must retain its 155-pass baseline unless a reproducible unrelated difference
is recorded and dispositioned before completion. Do not run both whole client
suites in one pytest process; their test module names collide in current config.
Verify baseline 50/3 Chat metadata remains unchanged using the P0 capture method,
but do not overwrite historical receipts; direct new outputs into the unit report.
Full owning-suite proof, if required by review, must preserve committed-example/
xterm controls and disclose pre-existing dirty inputs as in the baseline receipt.

Packaging proof (use a disposable directory from `mktemp -d`):

```sh
CMD_FND_ARTIFACTS=$(mktemp -d)
uv build --package friday-framework-commands --out-dir "$CMD_FND_ARTIFACTS/dist"
uv venv "$CMD_FND_ARTIFACTS/venv"
uv pip install --python "$CMD_FND_ARTIFACTS/venv/bin/python" --no-deps "$CMD_FND_ARTIFACTS"/dist/*.whl
```

From a working directory outside the repository, clear inherited PYTHONPATH and
run the disposable interpreter in isolated mode (`-I`). Import the public API,
register a synthetic handler and execute canonical/alias/unknown/plain-text
cases. Assert the module loads from that venv, the distribution has no runtime
requirements, `py.typed` is present and frontend imports remain blocked. This
is foundation installation proof; it does not repair or prove installed Chat/
generic CLI entry points or complete their later packaging gates. Record exact
commands/results, wheel hash, environment, counts and skips in the report.

## Handoff and stop conditions

Stop before editing if approval/API/base pins are absent or branch/board disagree.
Stop for scope expansion, unresolved contract ambiguity, dependency cycles, required
frontend imports, unrelated lock changes or a need to modify existing source/tests.
Do not implement deferred features, invent new defaults or weaken security behavior.
Report failures/skips and partially completed work honestly; do not self-approve.

After required checks, commit only allowed paths and provide the candidate full
SHA/diff, authority digests, test/install receipts and limitations. Stop for a fresh
read-only independent validator reviewing API-01–API-06 and the exact directive.
A changed candidate requires fresh validation. No automatic remediation loop,
phase closure, maintainer acceptance or external delivery follows from this unit.
