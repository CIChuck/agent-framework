# CD-CMD-PILOT-001 — shared help, exit and clear-screen pilot

Status: **draft; construction approval not granted**. Owner: Chuck Russell.
Prepared 2026-11-07. Unit: PILOT-001; branch: `feature/command-retirement`.
The preparation instruction and later harness/council amendment authorize diagnostic tooling and review only; pilot product construction remains unapproved.

## Authority and required approval

Repository AGENTS, engineering/lifecycle/independent-validation policies and
the board control execution. The approved foundation and accepted retirement
unit remain controlling inputs. This directive implements only the proposed
[pilot contract](../pilot-command-contract.md), hash
`e9cf8af3c0fc5e164de35c27d01e428ac9a912f0f957c21c40648c2334dc86d3`.
Approve that contract first, then this exact directive; an explicit approval
of both together is also sufficient. Record both hashes, approver, date and
instruction in authority/approval records before generating product code.
Explicit contract approval must also disposition the pilot's additive public
API/ownership review; foundation approval alone does not cover this extension.

Execution product baseline is
`7b80ca01489a52608aafb54b626b74fbb36efbe3`. Only planning/approval descendants
with identical product, test, package and lock bytes may precede construction.
Record the actual starting HEAD and verify that equality. Otherwise stop and
refresh this directive before approval; do not silently rebase its evidence.

Frozen inputs (SHA-256):

| Input | Hash |
| --- | --- |
| `shared-command-api.md` | `e5ba883fb246967320243e1dbc9c2a70fcf6189c05540a45961388f2b6466b74` |
| `validation/command-matrix.json` | `87c7880b21bbd7b02f227a7f93373dc3acc67db91e3ced18fd65511c34081f85` |
| `directives/CD-CMD-RET-001-nine-command-retirement.md` | `b760a9a8f8b94e120e5d26914d9bdf45f037a6a3f7f9552cd3d4054d829da9df` |
| `validation/retirement/receipts.json` | `7d0d557f7e4593110b3eb75a6e191dfa3119a8c980947cf4e57360192adab767` |

The 50-name matrix is a historical metadata oracle: compare its seven metadata
fields and nested arguments after removing the exact nine RET-001 names.
Its planning-only columns are not runtime metadata. Current product baseline
contains 41 canonical names/three aliases; it is not the historical 50-name app.

## Objective, paths and non-goals

Implement PC-01–PC-07 without observable Chat behavior changes. Shared behavior
must execute in the maintained Chat application, not only in synthetic tests.

| Allowed product path | Exact change |
| --- | --- |
| `packages/friday-commands/src/friday_commands/pilot.py` (new) | Proposed four-symbol API, three metadata definitions and three injected handlers. |
| `packages/friday-commands/src/friday_commands/__init__.py` | Add four exports; update stale no-built-in-handler module description. |
| `packages/friday-chat/src/friday_chat/commands/pilot.py` (new) | Typed metadata/catalog adapters, shared invocation and Chat outcome/text rendering. No runtime dependency. |
| `packages/friday-chat/src/friday_chat/commands/registry.py` | Replace only three metadata definitions with projections; delegate help/exit wrappers and synchronous help rendering. Retain parser, registration, execute/admission and other handlers unchanged. Move existing rendering helpers to the adapter only if required to avoid import cycles; preserve their behavior. |
| `packages/friday-chat/src/friday_chat/commands/session.py` | Replace `cls_handler` policy body with shared delegation; preserve signature/export. |
| `packages/friday-chat/pyproject.toml` | Required exact-version commands dependency and workspace source only. |
| `uv.lock` | Corresponding Chat dependency/requires-dist edges only. No version refresh. |

Allowed tests: add `packages/friday-commands/tests_commands/test_pilot.py` and
`packages/friday-chat/tests_chat/test_command_pilot.py`; extend existing
`test_command_registry.py`, `test_command_foundations.py`, `test_display.py`,
`test_session_memory_commands.py` and `test_command_production_adapters.py` in
that Chat test tree. No other existing test may change. Existing assertions
remain unless an exact node/assertion disposition demonstrates that an internal
ownership expectation moved while its public behavior remains covered. Do not
delete, xfail, relax or replace assertions just to obtain passing results.
Keep `test_command_retirements.py` and all its negatives unchanged.

Allowed documentation: both package READMEs; the root README and AGENTS package
description sentences only (neutral package now has opt-in pilot handlers);
this initiative's current status/approval/execution/PAR evidence and a new
`validation/pilot/` evidence directory; board/dashboard current gate. Preserve
frozen source inventories, receipts, requests and independent reports. Do not
rewrite earlier reviews, directive bytes or the approved foundation API.

Do not change neutral `contracts.py`/`registry.py`, Chat contracts or `app.py`,
other 38 handlers/metadata, generic CLI source/tests, root metadata/cohort or
artifact scripts, configuration/templates, runtime/store/provider ownership,
terminal implementations, TUI or other family contracts. No shell parsing,
command consolidation, capability framework, handler retries, default-populated
neutral registry or retired-name blacklist. New scope requires an amendment.

## Required implementation sequence

1. Verify authority, board, branch, frozen inputs and all unrelated dirty hashes.
   Before source edits, run baseline checks and capture the exact metadata,
   general/focused help strings, result fields, parser/alias outcomes and
   lifecycle events used below. Store the capture program, hash, argv and raw
   output in `validation/pilot/`. The capture must use baseline Git source;
   expected output cannot be regenerated from the new shared implementation.
2. Inventory every existing test function/assertion in allowed test files and
   every source definition in changed files. Record exact permitted ownership
   edits; compare retained definitions by AST. Module import changes alone must
   not become permission to rewrite retained functions or format entire files.
3. Add the shared API and standalone tests. Keep the old foundation API intact.
   Use existing closed data variants; validate essential shape invariants with
   explicit exceptions. All shared imports remain standard-library/own-package.
4. Add the Chat adapters, project only the three owned definitions and replace
   wrappers. Invoke one shared handler per dispatch from already parsed args.
   Help's synchronous public entry point must share selection with the async
   handler. Do not retain an alternate legacy help-selection engine.
5. Add the required Chat dependency and workspace source, then regenerate the
   lock. First try `uv lock --offline`; public Python registry access solely for
   `uv lock`/missing locked artifacts is permitted if cache resolution requires
   it. Record the actual service/command. No live model/tool/provider calls.
   Prove only the declared lock edges changed and all resolved versions stayed.
6. Run after checks, compare frozen baseline strings/metadata/assertions/source
   and perform clean Git-export artifact/installed proofs. Update documentation
   and PAR rows with exact bounded evidence; no broad P0/P1 closure.
7. Commit a stable candidate locally and freeze a review request with directive,
   contract/authority hashes, baseline/candidate/diff, criteria, commands,
   limitations and protected-file manifest. Obtain a fresh-context read-only
   independent validation under repository policy. Reviewer receives no builder
   private reasoning and makes no repairs. A changed candidate needs fresh review.
   Stop after VERIFIED for maintainer acceptance; no publication is authorized.

## Required acceptance cases

Each criterion requires concrete test nodes and receipts. Equal output alone
does not prove extraction: use spy handlers/catalog ports and typed-outcome
checks to establish which shared code ran and how often.

| ID | Required proof |
| --- | --- |
| PILOT-01 | Exact three shared specs and immutable handler-map keys; no implicit registration; all prior foundation tests still pass. Standalone neutral registry executes each pilot/alias without Chat, CLI, runtime, Rich, providers or stores. |
| PILOT-02 | General help returns a canonically sorted snapshot and calls only `specs` once; focused help calls only exact-key lookup, resolves aliases and preserves canonical focus. Unknown error has the normalized name and no effect. No-arg, empty, whitespace-only and extra-arg cases obey PC-01. Catalog failure and cancellation propagate once. Wrong canonical request names raise before any catalog read. |
| PILOT-03 | Exact 41/3 metadata projection and all baseline general/focused help strings, including every canonical command, all three aliases, all nine removed names and a new unknown. Preserve category/name ordering, details, argument/default/choices text and blank lines. Empty/multiple-category custom catalogs also match. |
| PILOT-04 | Text fixtures include ordinary text, leading-space noncommands, `/`, `/ HELP`, `//HELP`, `///HELP`, `/ /HELP`, mixed case, tabs/newlines, `/help q`, `/help /q`, `/help //q`, `/help exit ignored`, and quote tokens. Preserve current whitespace splitting and one normalization; do not adopt CLI shell parsing. Compare exact handled/output/exit/effects against baseline. |
| PILOT-05 | Custom empty registry; explicit custom help/exit/cls and retired-name handlers; context registry different from dispatch registry; plain context default-help fallback; direct `render_help(None)`, `render_help('')`, `render_help(' ')`; registered empty alias and slash-retaining names. Delegating wrappers also work when explicitly registered under another name, as before. |
| PILOT-06 | PC-04 permissive argument cases (numeric default, truthy/falsy required, tuple/list/string/mapping choices), invalid choice member, and an unrelated malformed metadata entry during focused/unknown help. No new registration rejection, eager projection or silent repair. Typed outcome adapter rejects every unrecognized data/error/effect combination explicitly. |
| PILOT-07 | Exit and both aliases ignore extra args, shared invocation/await occurs once, exact Goodbye/result/context flag. App output precedes command exit and cleanup occurs once with the same exit reason. Shared exit/clear succeed with tripwire catalog/context/runtime/session objects and perform no I/O. |
| PILOT-08 | `cls`/`clearscreen` ignore extra args, one shared effect maps to one Chat effect and one display call, no replacement text or history clearing. Missing display/failing display messages exactly match baseline. Preserve effect-before-output ordering and existing PTY production-display proof. No app source change. |
| PILOT-09 | Other 38 handler bodies, registration/dispatch/parser/admission APIs, all nine retirement negatives and generic CLI suites unchanged. Existing test/assertion disposition is complete, with no weakened behavior checks. |
| PILOT-10 | Required dependency in source, lock, wheel and sdist; clean standalone neutral install and default installed Chat closure outside checkout; installed/Git/wheel/sdist source equality, exact 41/3 and aliases/help/exit/clear behavior. Default imports/help include finance success and no legacy `friday` executable. No diagnostic extras substituted for default proof. |

Required test ownership (all paths relative to their package test tree):

| ID | Test files that must cover the criterion |
| --- | --- |
| PILOT-01 | Commands `test_pilot.py`, `test_import_boundary.py`; retain the entire existing Commands suite. |
| PILOT-02 | Commands `test_pilot.py`, including invalid focus/request/execution types before catalog access. |
| PILOT-03 | Chat `test_command_pilot.py`, `test_command_registry.py`, unchanged `test_command_retirements.py`. |
| PILOT-04 | Chat `test_command_pilot.py`, `test_command_registry.py`. |
| PILOT-05 | Chat `test_command_pilot.py`, including legacy falsy focuses `False`, `0`, `[]`. |
| PILOT-06 | Chat `test_command_pilot.py`. |
| PILOT-07 | Chat `test_command_pilot.py`, `test_session_memory_commands.py`, `test_command_production_adapters.py`; unchanged `test_app_lifecycle.py` nodes `test_session_initializes_lazily_on_first_chat_turn`, `test_app_help_output_includes_usage_and_argument_descriptions`, `test_command_only_session_does_not_initialize_chat_defaults`, `test_async_clients_close_after_background_and_llm_maintenance`. |
| PILOT-08 | Chat `test_command_pilot.py`, `test_display.py` (including PTY), and `test_command_production_adapters.py::test_clear_aliases_request_display_effect_without_false_output`. |
| PILOT-09 | All three full suites; unchanged retirement negatives; Chat `test_command_foundations.py`; source/assertion disposition. |
| PILOT-10 | Commands `test_pilot.py` standalone cases plus a recorded `validation/pilot/installed_probe.py` for both installed environments, metadata/closure/origin/source proofs and invocation spies. |

## Reproducible check environment

During this authorized harness preparation, run only startup, guard, comparison, baseline capture, unchanged baseline suites and the unchanged baseline artifact controls and bundle trial below. New pilot tests and after-change checks wait for construction approval. Use a fresh
scratch directory per before/after lane. Extract only `run.py`, `controls.py`
and `sitecustomize.py` from the pinned retirement receipt's `files` object,
checking their text hashes before writing/executing them:

| Helper | SHA-256 |
| --- | --- |
| `run.py` | `409769f1c17a63fcbd7ea2bd3d079af315dcc9afabca8bd35602033c198124af` |
| `controls.py` | `d62238fd3fac3188f9464604cf091ed2eeb4d9ad76ef21f1f796b3b7af0ba20d` |
| `sitecustomize.py` | `8365940b2d00a21061c00f671304b29f4c4ba1e9b344a1f4c38c5365de41631f` |

Materialize both example files from baseline Git into scratch for the controls
plugin. Never copy the dirty working examples into tests or artifacts. The
runner supplies offline/frozen/no-sync commands with the editable neutral
package, a sanitized environment, xterm, scratch caches and guard injection.
Verify the guard blocks external DNS/connect/send/connect_ex and Python open/
SQLite access to known user/repository `.friday` stores before application
imports, including subprocesses. The historical helper hashes below are input
pins; `prepare.py` appends the pilot guard extension and records its hash and
the combined guard hash in `bootstrap.json`. SQLite file URIs and Darwin case variants are covered. A SQLite authorizer also denies protected or unresolved ATTACH/VACUUM INTO destinations; do not override it in fixtures to force a pass.
Real SQLite refusal probes use a synthetic repo in scratch, never a real user
database. This is Python audit containment, not an OS sandbox for arbitrary
native I/O; every fixture must use scratch explicitly. Only locally bound
disposable loopback servers are allowed. Failed controls stop testing.

The materialized [preparer](../validation/pilot/harness/prepare.py) extracts these
helpers, verifies eight public build wheels against
[build-tools.json](../validation/pilot/harness/build-tools.json) and supplies
`pilot_run.py`, a wrapper around the unchanged historical runner. The wrapper
sets `UV_FIND_LINKS` to the closed wheelhouse, `UV_NO_INDEX=1` and the local
LiteLLM cost-map option. It also checks positional and equals-joined arguments against all existing top-level scratch JSON/log files and
suffixes repeated run labels to preserve earlier receipts and gives each pytest run a unique scratch `--basetemp`. This removes the fresh-cache startup defect without
changing production metadata or relying on a prior global build cache.
[build-requirements.txt](../validation/pilot/harness/build-requirements.txt)
records all eight exact versions and allowed distribution hashes. Registry access
for `--fetch-build-tools` is limited to the eight pinned HTTPS wheel URLs at
`files.pythonhosted.org`; no credentials or application services are needed.

```sh
PILOT_PHASE=before               # after for committed implementation
PILOT_SCRATCH=$(mktemp -d -t friday-pilot-check)
PILOT_HARNESS="$PWD/docs/planning/active/command-refactor/validation/pilot/harness"
export PILOT_PHASE PILOT_SCRATCH PILOT_HARNESS
python3 -B "$PILOT_HARNESS/prepare.py" "$PILOT_SCRATCH" --fetch-build-tools
# For fully offline bootstrap instead, use an existing verified wheelhouse:
# python3 -B "$PILOT_HARNESS/prepare.py" "$PILOT_SCRATCH" --wheelhouse /absolute/path/to/wheelhouse
python3 -B "$PILOT_SCRATCH/pilot_run.py" guard-selftest python -B "$PILOT_HARNESS/guard_selftest.py"
python3 -B "$PILOT_HARNESS/compare.py" --selftest
```

The repository test `.venv` and its existing locked development dependencies
are prerequisites; the eight wheels bootstrap build tooling only. Record the
interpreter, uv version and installed distribution inventory. Do not claim this
workspace test environment is the later isolated default-install proof.

With `PILOT_SCRATCH` naming that directory and `PILOT_PHASE` equal to `before`
or `after`, execute these commands from the repository root. The runner records
each argv, exit, elapsed time and raw log; supply the current source identity too.

```sh
python3 -B "$PILOT_SCRATCH/pilot_run.py" "$PILOT_PHASE-chat" python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-chat/tests_chat --ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py
python3 -B "$PILOT_SCRATCH/pilot_run.py" "$PILOT_PHASE-foundation" python -B -m pytest -p no:cacheprovider -q packages/friday-commands/tests_commands tests/integration/test_package_cohort_metadata.py
python3 -B "$PILOT_SCRATCH/pilot_run.py" "$PILOT_PHASE-cli" python -B -m pytest -p no:cacheprovider -q packages/friday-cli/tests_cli
python3 -B "$PILOT_SCRATCH/pilot_run.py" "$PILOT_PHASE-lint" ruff check --no-cache packages/friday-commands/src packages/friday-commands/tests_commands packages/friday-chat/src/friday_chat/commands/registry.py packages/friday-chat/src/friday_chat/commands/session.py
python3 -B "$PILOT_SCRATCH/pilot_run.py" "$PILOT_PHASE-types" mypy packages/friday-commands/src packages/friday-chat/src/friday_chat/commands/registry.py packages/friday-chat/src/friday_chat/commands/session.py
python3 -B "$PILOT_SCRATCH/pilot_run.py" "$PILOT_PHASE-root-lint" ruff check --no-cache .
python3 -B "$PILOT_SCRATCH/pilot_run.py" "$PILOT_PHASE-root-tests" python -B -m pytest -p controls -p no:cacheprovider -q
python3 -B "$PILOT_SCRATCH/pilot_run.py" "$PILOT_PHASE-metadata" python -B scripts/check-package-metadata.py
python3 -B "$PILOT_SCRATCH/pilot_run.py" "$PILOT_PHASE-board" python -B scripts/friday-dev-board.py validate
python3 -B "$PILOT_SCRATCH/pilot_run.py" "$PILOT_PHASE-docs" python -B scripts/check-documentation-lifecycle.py
uv lock --check --offline
git diff --check
```

After creation, also run focused Ruff on the new Chat adapter and every changed
test file, mypy on the new adapter, and `ruff format --check --no-cache` on all changed Python
files in both lanes where present. Report existing formatting failures separately;
new files must pass. No blanket formatting cleanup or waiver is included.
Before reference counts are Chat 1,038, foundation/cohort 145, CLI 155; capture
actual current counts. New tests increase counts; totals alone prove nothing.
Root Ruff/pytest and older formatting were failing at RET-001. Reproduce and
enumerate current failures; report them as failed gates, never blanket success.
A new failure or broader collection loss is a regression and stops completion.

## Incremental gates and baseline comparison

The frozen baseline is [baseline.json](../validation/pilot/baseline.json), SHA-256
`48c3161cf1a0467c7e95ac11a85de0972d46421b5a9318ee618651f7cc7ad7f1`.
Its capture program is `harness/capture.py`, SHA-256
`96f3f53c970fe1051a2b498250cce397ea952101483982103e9419391f4c3c4a`.
Do not edit either after construction approval. If a harness defect is found,
stop for an explicit amendment and regenerate/review the baseline from the
unchanged before revision, never the new implementation.

| Gate | Required result before advancing |
| --- | --- |
| G0 — harness | Offline startup from fresh scratch, guard and comparator controls, clean-Git baseline reproduction, and cold-cache unchanged Commands artifact build/install control below. Current preparation supplies this evidence; no new APIs are claimed implemented. |
| G1 — neutral | Add and pass `tests_commands/test_pilot.py`: shared specs/handlers, typed outcomes, catalog calls, standalone consumer and error/cancellation cases (PILOT-01/02). |
| G2 — Chat | Add and pass `tests_chat/test_command_pilot.py`; rerun registry/foundation/retirement tests. Prove real delegation plus metadata, custom registries, projection, parser and exact baseline comparison (PILOT-03–06 and the Chat subset of PILOT-09; full PILOT-09 closes at G4). |
| G3 — lifecycle | Pass exit/clear app tests, ordering, once-only cleanup and PTY/display checks (PILOT-07/08). |
| G4 — regression | All three full suites, unchanged assertion/source proof and focused lint/types; enumerate broader baseline failures rather than declaring them green. |
| G5 — installed | Clean Git artifacts/default closure, PILOT-10 installed subset, then frozen candidate and independent review. |

After construction approval and creation of each named new test file, these are
fast iteration commands. A missing test file is a failed gate, not a reason to
skip tests. Expected failing new tests may guide implementation during a stage;
all must pass before advancing. Do not xfail them or weaken the oracle.

```sh
python3 -B "$PILOT_SCRATCH/pilot_run.py" g1-fast python -B -m pytest -p no:cacheprovider -q packages/friday-commands/tests_commands tests/integration/test_package_cohort_metadata.py
python3 -B "$PILOT_SCRATCH/pilot_run.py" g2-fast python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-chat/tests_chat/test_command_pilot.py packages/friday-chat/tests_chat/test_command_registry.py packages/friday-chat/tests_chat/test_command_foundations.py packages/friday-chat/tests_chat/test_command_retirements.py
python3 -B "$PILOT_SCRATCH/pilot_run.py" g3-fast python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-chat/tests_chat/test_command_pilot.py packages/friday-chat/tests_chat/test_display.py packages/friday-chat/tests_chat/test_session_memory_commands.py packages/friday-chat/tests_chat/test_command_production_adapters.py packages/friday-chat/tests_chat/test_app_lifecycle.py
```

G1 deliberately runs the entire small Commands suite, including new pilot and
import-boundary tests. G3 deliberately runs the entire app-lifecycle and
production-adapter files, not just the EOF-only cleanup node. This covers the
existing `/help`, `/q`, `/cls` and `/clearscreen` application paths before G4.

For baseline reproduction, set `PILOT_REVISION` to the frozen before commit.
For the G2/G5 after comparison, set it to the actual committed candidate.
Intermediate local WIP commits of authorized product/test changes are expressly
allowed for G2 captures; retain `started` state and pending validation, exclude
both dirty example files, and never infer push/acceptance authority. Export
into a new directory per capture. The capture verifies every package `src/`
file (including YAML/data) against that revision before imports, and all loaded
`friday*` file/namespace origins, including the new pilot modules when loaded.
It refuses existing outputs or outputs inside the checkout/export.
Its five groups contain 41 metadata records, 62 help cases, 29 dispatch cases,
61 custom compatibility cases and three fake-app lifecycle traces.

```sh
PILOT_REVISION=7b80ca01489a52608aafb54b626b74fbb36efbe3  # actual candidate for after
export PILOT_REVISION
PILOT_SOURCE="$PILOT_SCRATCH/source-$PILOT_PHASE"
export PILOT_SOURCE
mkdir "$PILOT_SOURCE"
git archive --format=tar --output "$PILOT_SCRATCH/source-$PILOT_PHASE.tar" "$PILOT_REVISION"
python3 -B - <<'PY'
import os, pathlib, tarfile
scratch = pathlib.Path(os.environ['PILOT_SCRATCH'])
with tarfile.open(scratch / ('source-' + os.environ['PILOT_PHASE'] + '.tar')) as archive:
    archive.extractall(os.environ['PILOT_SOURCE'], filter='data')
PY
python3 -B "$PILOT_SCRATCH/pilot_run.py" "$PILOT_PHASE-capture" python -B "$PILOT_HARNESS/capture.py" "$PILOT_SOURCE" "$PILOT_SCRATCH/capture-$PILOT_PHASE.json" --revision "$PILOT_REVISION"
python3 -B "$PILOT_HARNESS/compare.py" docs/planning/active/command-refactor/validation/pilot/baseline.json "$PILOT_SCRATCH/capture-$PILOT_PHASE.json" --baseline-sha256 48c3161cf1a0467c7e95ac11a85de0972d46421b5a9318ee618651f7cc7ad7f1
```

The comparator rejects altered values, list order, missing/extra groups and
boolean/integer substitutions. It also rejects a different capture program;
provenance differences such as source location/revision are expected. The
capture is a compatibility oracle; additional new-API/spy tests are required
because equal text alone cannot prove shared ownership or once-only invocation.

## Artifact proof and handoff

Plain offline build commands must not rely on a user's global cache. Every
build/venv/install command below exports its closed wheel source, no-index and
offline settings and a new scratch cache. Before G5, perform this G0 control
against the unchanged baseline export produced above. `PILOT_PYTHON` is the
absolute existing workspace test interpreter; capture it before changing cwd.

```sh
PILOT_PYTHON="$PWD/.venv/bin/python"
export PILOT_PYTHON
(
  cd "$PILOT_SOURCE"
  export UV_FIND_LINKS="$PILOT_SCRATCH/wheelhouse" UV_NO_INDEX=1 UV_OFFLINE=1
  export UV_CACHE_DIR="$PILOT_SCRATCH/g0-build-cache"
  uv build --offline --no-python-downloads --package friday-framework-commands --out-dir "$PILOT_SCRATCH/g0-dist"
  uv venv --offline --no-python-downloads --python "$PILOT_PYTHON" "$PILOT_SCRATCH/g0-venv"
  uv pip install --offline --no-index --python "$PILOT_SCRATCH/g0-venv/bin/python" --find-links "$PILOT_SCRATCH/g0-dist" friday-framework-commands==0.1.0a4
  uv pip check --offline --python "$PILOT_SCRATCH/g0-venv/bin/python"
)
```

The authoritative G5 preparation recipe is the materialized
[bundle.py](../validation/pilot/harness/bundle.py). It requires the exact
macOS/arm64 **Python 3.13.10** interpreter (`>=3.13.4` is the package floor).
Do not pass bare `--python-version 3.13`, which targets an unsupported patch
level. Its resolver command supplies `--python <actual interpreter>` and
`--python-version 3.13.10`; target/native wheel tags come from that interpreter.

Before any build or fetch, the helper resolves the revision to a canonical
commit and requires exact whole-export inventory equality with Git: no extra
files or directories, missing files, changed blobs, file/symlink substitutions,
executable-mode drift, escaping symlinks or special files. It constructs its own
private `git archive`, verifies the same complete inventory and builds only
from that private export. An end check requires that export to remain unchanged.
A negative control must reject an extra package source or data file before any
build/fetch. It then executes these fully recorded operations:

1. `uv export --frozen --offline --no-dev --package friday-chat --no-editable`
   with hashes retained. Preserve conditional versions such as both `grpcio`
   entries; evaluate the selected artifacts for the recorded target.
2. Select compatible third-party wheels from `uv.lock`, fetch only their exact
   `files.pythonhosted.org` URLs and verify both lock and export SHA-256 hashes.
   There is no implicit global cache or unpinned registry resolution.
3. For the sole approved source-only package, `pypika==0.48.9`, verify the locked
   sdist hash and build its wheel offline using pinned `setuptools==75.8.0` and
   `wheel==0.45.1` from the eight-tool closed build bundle. Record input sdist,
   build-tool and output-wheel hashes. A generated wheel is validated by this
   source/build lineage, not by pretending it has a wheel hash in `uv.lock`.
   Any other source-only dependency stops the unit for an amendment.
4. Build every required workspace distribution from the clean Git export with
   `uv --no-config build --offline --no-python-downloads --python <driver interpreter> --package <name>`. Put Chat and
   Commands in `g5-dist` and other selected workspace artifacts in
   `workspace-wheels`; third-party files never supply workspace packages.
5. Compile the default profile with marker-aware lock constraints, exact target
   Python and wheel hashes, using only the three local wheel directories.
   Install separate neutral/default Chat venvs with `--require-hashes --no-deps`,
   then require both `uv pip check` and guarded `-I` imports/origin checks.

Run this trial at G0 against the unchanged baseline export. At G5, repeat with
its actual candidate revision and add `--require-pilot-edge`, which checks the
unconditional required Commands dependency in the built Chat wheel metadata.
Use a new, empty output directory for each run. The helper's driver may fetch
only pinned public artifacts; all build/resolver/install child processes are
sanitized, guarded, offline, no-index and use its fresh local cache. Ambient
`UV_*` and `VIRTUAL_ENV` settings are removed; every uv child uses `--no-config`,
and every build uses the explicit driver interpreter.

```sh
# G0 baseline trial; PILOT_SOURCE/PILOT_REVISION identify the clean before export.
"$PILOT_PYTHON" -B "$PILOT_HARNESS/bundle.py" "$PILOT_SOURCE" "$PILOT_SCRATCH/baseline-bundle" "$PILOT_SCRATCH" --revision "$PILOT_REVISION" --fetch
# G5: new candidate export/revision; reuse verified raw artifacts fully offline.
"$PILOT_PYTHON" -B "$PILOT_HARNESS/bundle.py" "$PILOT_SOURCE" "$PILOT_SCRATCH/candidate-bundle" "$PILOT_SCRATCH" --revision "$PILOT_REVISION" --artifacts "$PILOT_SCRATCH/baseline-bundle/locked-artifacts" --require-pilot-edge
```

`bundle-report.json` records every actual argv/exit, exact target/environment,
the helper hash and uv version, canonical revision, complete source inventory
with types/modes/blob hashes, private archive hash, input build-tool hashes,
fetched artifact hashes, PyPika lineage and output artifact/profile hashes.
The large complete inventory stays in scratch, with its count and digest in
the embedded report so reviewers can reconstruct it from Git. Per-command logs remain alongside it. The
preparation baseline trial proves the artifact machinery, not an implemented
pilot or its future installed behavior. G5 must additionally run the specified
`installed_probe.py`, including pilot handler/delegation and source-member
checks; the helper's basic imports/catalog check does not replace that proof.

Stop if resolution needs a version change or an unapproved extra. All artifact
commands record actual environment, argv, cwd, exit, input/output hashes.
Validate each pair using `scripts/check-package-artifacts.py` with package
selectors `friday_framework_commands` and `friday_chat` and the scratch artifact directory.
Supply all required workspace dependency wheels from clean Git sources with
hash/source lineage; no public same-version workspace replacement or stale
editable installation may satisfy the proof.

Use separate disposable environments for (a) commands wheel alone, proving no
dependencies/host imports and standalone pilot execution; and (b) default Chat
plus its declared dependency closure, without optional speech/sandbox/moltbook
extras. Pin every resolved distribution version to the unchanged `uv.lock`
constraints and include the new required Commands edge. The prior installed
profile's 129-member count is historical evidence, not a new resolver target;
derive and verify the current locked closure rather than adding extras to reach
a count. Record and explain any membership difference from that historical profile.
Use only the explicitly fetched, hash-verified artifact bundle; repeat the
bundle trial offline before candidate handoff. Do not rely on an ambient cache.
Require `uv pip check --offline`, compare installed metadata with declared closure
and prove commands is a required Chat edge. `--no-deps` installation alone is
insufficient without these closure/dependency checks.

Run probes outside the checkout using the installed interpreter with `-I` and
explicitly load the pinned guard before imports (`-I` ignores PYTHONPATH).
Check every changed installed source member against both Git and built wheel.
Compare the complete package source/data member sets and bytes in the Chat and
Commands wheels and sdists against clean Git, including unchanged templates;
reject additional members outside the declared generated metadata. Check all
loaded Friday module file and namespace origins, refusing missing origins.
Probe PILOT-01–10's installed subset, module origins, exact metadata and outputs;
spy on shared calls so a bundled legacy implementation cannot pass by output
coincidence. No terminal/provider/store construction during import/help proof.
Bounded app/display tests use only disposable fixtures as above.

Publish a local builder report, assertion/source disposition, pinned before/
after fixtures, command receipts, artifact/profile hashes and frozen independent
request under `validation/pilot/`. Include limits and every unsuccessful attempt.
Keep the initiative started/local through independent review. Acceptance and
push/PR/merge/release are separate human decisions.

Stop for changed pins/authority, inaccessible baseline fixtures, new scope or
dependency versions, unrepresentable legacy metadata, guard failure, new test/
type/lint/collection failure, source/evidence mismatch or dirty-file mutation.
Do not infer permission to repair unrelated debt, change this approved contract
or start another family/council/remediation round.
