# CD-CMD-PILOT-001 — shared help, exit and clear-screen pilot

Status: **draft; construction approval not granted**. Owner: Chuck Russell.
Prepared 2026-11-07. Unit: PILOT-001; branch: `feature/command-retirement`.
The instruction “proceed” authorizes preparing this packet, not implementing it.

## Authority and required approval

Repository AGENTS, engineering/lifecycle/independent-validation policies and
the board control execution. The approved foundation and accepted retirement
unit remain controlling inputs. This directive implements only the proposed
[pilot contract](../pilot-command-contract.md), hash
`ef0af6e9c5300906594191ee18ea2b195ef4ae525fcd6898a644bdcc961c958d`.
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

Implement PC-01–PC-06 without observable Chat behavior changes. Shared behavior
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
| PILOT-02 | General help snapshots canonical specs, sorts once and calls only `specs`; focused help calls only exact-key lookup, resolves aliases and preserves canonical focus. Unknown error has the normalized name and no effect. No-arg, empty, whitespace-only and extra-arg cases obey PC-01. Catalog failure and cancellation propagate once. Wrong canonical request names raise before any catalog read. |
| PILOT-03 | Exact 41/3 metadata projection and all baseline general/focused help strings, including every canonical command, all three aliases, all nine removed names and a new unknown. Preserve category/name ordering, details, argument/default/choices text and blank lines. Empty/multiple-category custom catalogs also match. |
| PILOT-04 | Text fixtures include ordinary text, leading-space noncommands, `/`, `/ HELP`, `//HELP`, `///HELP`, `/ /HELP`, mixed case, tabs/newlines, `/help q`, `/help /q`, `/help //q`, `/help exit ignored`, and quote tokens. Preserve current whitespace splitting and one normalization; do not adopt CLI shell parsing. Compare exact handled/output/exit/effects against baseline. |
| PILOT-05 | Custom empty registry; explicit custom help/exit/cls and retired-name handlers; context registry different from dispatch registry; plain context default-help fallback; direct `render_help(None)`, `render_help('')`, `render_help(' ')`; registered empty alias and slash-retaining names. Delegating wrappers also work when explicitly registered under another name, as before. |
| PILOT-06 | PC-04 permissive argument cases (numeric default, truthy/falsy required, tuple/list/string/mapping choices), invalid choice member, and an unrelated malformed metadata entry during focused/unknown help. No new registration rejection, eager projection or silent repair. Typed outcome adapter rejects every unrecognized data/error/effect combination explicitly. |
| PILOT-07 | Exit and both aliases ignore extra args, shared invocation/await occurs once, exact Goodbye/result/context flag. App output precedes command exit and cleanup occurs once with the same exit reason. Shared exit/clear succeed with tripwire catalog/context/runtime/session objects and perform no I/O. |
| PILOT-08 | `cls`/`clearscreen` ignore extra args, one shared effect maps to one Chat effect and one display call, no replacement text or history clearing. Missing display/failing display messages exactly match baseline. Preserve effect-before-output ordering and existing PTY production-display proof. No app source change. |
| PILOT-09 | Other 38 handler bodies, registration/dispatch/parser/admission APIs, all nine retirement negatives and generic CLI suites unchanged. Existing test/assertion disposition is complete, with no weakened behavior checks. |
| PILOT-10 | Required dependency in source, lock, wheel and sdist; clean standalone neutral install and default installed Chat closure outside checkout; installed/Git/wheel/sdist source equality, exact 41/3 and aliases/help/exit/clear behavior. Default imports/help include finance success and no legacy `friday` executable. No diagnostic extras substituted for default proof. |

## Reproducible check environment

Do not run these implementation checks during document preparation. Use a fresh
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
Verify the guard blocks external DNS/connect/send/connect_ex and real user
stores before imports, including subprocesses; only locally bound disposable
loopback test servers are allowed. A failed guard self-test stops testing.

The extraction/preflight recipe is:

```sh
PILOT_PHASE=before               # after for committed implementation
PILOT_SCRATCH=$(mktemp -d -t friday-pilot-check)
export PILOT_PHASE PILOT_SCRATCH
python3 -B - <<'PY'
import hashlib, json, os, pathlib, subprocess
scratch = pathlib.Path(os.environ['PILOT_SCRATCH'])
bundle = pathlib.Path('docs/planning/active/command-refactor/validation/retirement/receipts.json')
if hashlib.sha256(bundle.read_bytes()).hexdigest() != '7d0d557f7e4593110b3eb75a6e191dfa3119a8c980947cf4e57360192adab767':
    raise SystemExit('Frozen retirement receipt changed')
files = json.loads(bundle.read_text())['files']
pins = {
    'run.py': '409769f1c17a63fcbd7ea2bd3d079af315dcc9afabca8bd35602033c198124af',
    'controls.py': 'd62238fd3fac3188f9464604cf091ed2eeb4d9ad76ef21f1f796b3b7af0ba20d',
    'sitecustomize.py': '8365940b2d00a21061c00f671304b29f4c4ba1e9b344a1f4c38c5365de41631f',
}
for name, expected in pins.items():
    text = files[name]['text']
    if hashlib.sha256(text.encode()).hexdigest() != expected:
        raise SystemExit(f'Harness hash mismatch: {name}')
    (scratch / name).write_text(text)
for name in ('config.example.yaml', 'models-config.example.yaml'):
    content = subprocess.check_output([
        'git', 'show', '7b80ca01489a52608aafb54b626b74fbb36efbe3:packages/friday-chat/' + name
    ])
    (scratch / name).write_bytes(content)
PY
```

With `PILOT_SCRATCH` naming that directory and `PILOT_PHASE` equal to `before`
or `after`, execute these commands from the repository root. The runner records
each argv, exit, elapsed time and raw log; supply the current source identity too.

```sh
python3 -B "$PILOT_SCRATCH/run.py" "$PILOT_PHASE-chat" python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-chat/tests_chat --ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py
python3 -B "$PILOT_SCRATCH/run.py" "$PILOT_PHASE-foundation" python -B -m pytest -p no:cacheprovider -q packages/friday-commands/tests_commands tests/integration/test_package_cohort_metadata.py
python3 -B "$PILOT_SCRATCH/run.py" "$PILOT_PHASE-cli" python -B -m pytest -p no:cacheprovider -q packages/friday-cli/tests_cli
python3 -B "$PILOT_SCRATCH/run.py" "$PILOT_PHASE-lint" ruff check --no-cache packages/friday-commands/src packages/friday-commands/tests_commands packages/friday-chat/src/friday_chat/commands/registry.py packages/friday-chat/src/friday_chat/commands/session.py
python3 -B "$PILOT_SCRATCH/run.py" "$PILOT_PHASE-types" mypy packages/friday-commands/src packages/friday-chat/src/friday_chat/commands/registry.py packages/friday-chat/src/friday_chat/commands/session.py
python3 -B "$PILOT_SCRATCH/run.py" "$PILOT_PHASE-root-lint" ruff check --no-cache .
python3 -B "$PILOT_SCRATCH/run.py" "$PILOT_PHASE-root-tests" python -B -m pytest -p controls -p no:cacheprovider -q
python3 -B "$PILOT_SCRATCH/run.py" "$PILOT_PHASE-metadata" python -B scripts/check-package-metadata.py
python3 -B "$PILOT_SCRATCH/run.py" "$PILOT_PHASE-board" python -B scripts/friday-dev-board.py validate
python3 -B "$PILOT_SCRATCH/run.py" "$PILOT_PHASE-docs" python -B scripts/check-documentation-lifecycle.py
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

## Artifact proof and handoff

Export the committed candidate using `git archive`, never the dirty checkout.
Build fresh wheel and sdist for both changed distributions with
`uv build --offline --no-python-downloads --package friday-framework-commands`
and the equivalent `--package friday-chat`, supplying a scratch `--out-dir`.
Validate each pair using `scripts/check-package-artifacts.py` with package
selectors `friday_framework_commands` and `friday_chat` and the scratch artifact directory.
Supply all required workspace dependency wheels from clean Git sources with
hash/source lineage; no public same-version workspace replacement or stale
editable installation may satisfy the proof.

Use separate disposable environments for (a) commands wheel alone, proving no
dependencies/host imports and standalone pilot execution; and (b) default Chat
plus its declared dependency closure, without optional speech/sandbox/moltbook
extras. Pin every distribution/version to the baseline locked profile plus the
new required commands distribution. The prior default profile had 129 members;
derive and verify the new closure rather than choosing extras to reach a count.
Install cached third-party artifacts offline; record any permitted registry
fetch of missing locked artifacts separately, then repeat installation offline.
Require `uv pip check --offline`, compare installed metadata with declared closure
and prove commands is a required Chat edge. `--no-deps` installation alone is
insufficient without these closure/dependency checks.

Run probes outside the checkout using the installed interpreter with `-I` and
explicitly load the pinned guard before imports (`-I` ignores PYTHONPATH).
Check every changed installed source member against both Git and built wheel,
and sdist contents against clean Git, including unchanged config templates.
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
