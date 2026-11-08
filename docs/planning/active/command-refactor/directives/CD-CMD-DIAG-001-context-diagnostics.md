# CD-CMD-DIAG-001 — shared context diagnostics

Status: **proposed; construction approval not granted**. Owner: Chuck Russell.
Prepared 2026-11-08. Branch: `feature/command-retirement`. Unit: DIAG-001.
Preparation under “proceed” changes planning/evidence only. Approval of the
exact [contract](../diagnostics-command-contract.md), then this directive (or
both together), is required before product/test/probe implementation.

## Authority and execution base

Apply AGENTS and engineering/lifecycle/independent-validation policies, current
board and packet, then DG-01–DG-06 in the contract. Record maintainer, instruction,
date and exact contract/directive/preparation digests in a subsequent approval.
That approval must explicitly cover the closed payload expansion, the two
declared-type decisions and the narrow pre-existing export assertion update.
Preserved proposal labels do not replace a subsequent exact approval.

Baseline: `9dbcec54773f10274eea058e5d59edb0ce53b6cc`.
Only planning/approval descendants with byte-identical packages, tests, scripts,
root AGENTS/README/main/metadata and lock may precede construction. Record actual
start HEAD and equality. Unexpected source drift requires a refreshed approved
baseline. Initiative remains started/local; DIAG is not approved yet.

The frozen input table below is normative. Accepted SESSION/pilot technical
inputs, their raw reports/receipts and harnesses remain immutable. Known root
Ruff 534, sole Chat/CLI `test_display` root collection conflict (6668 collected)
and legacy registry formatting are failed/unwaived baseline debt, not waived
prerequisites or passing gates. No new regression may hide behind them.

| Input relative to packet | SHA-256 |
| --- | --- |
| `diagnostics-command-contract.md` | `14dd68f6cc2c5dfbba7f31c19305eeeec68a00598b3b1a1740806832b621be62` |
| `validation/diagnostics/preparation.json` | `1f8ee9c7e882d0d0e857deb8489b0eeb309e0d1fa5c21ccbf40223e0886a2c55` |
| `approval/session-acceptance.md` | `86d2642ac4aa8aeaee73fc727539ef5bb9fe87946aedca085f9db07e50a87a1c` |
| `approval/session-views.md` | `ebe203d07e4143fa81221ab76fb04db4e3e2d82e981a633df263ba0174d61ab4` |
| `session-command-contract.md` | `f29ac447d9cc76c1c1bb1dff9d6fc9ef619ca3b5ff43f1833ee5346250a3e003` |
| `directives/CD-CMD-SESSION-001-session-views.md` | `1fd4b3cf0a2de5ad180e9c3c3d06e7bb5d239bb3516ccca60fb7376041a96b46` |
| `approval/council-roster.md` | `80c8e25ed071503313e9b3c97d93d2fb3712d29de6822e22b539d7b3a3fa8e02` |
| `shared-command-api.md` | `e5ba883fb246967320243e1dbc9c2a70fcf6189c05540a45961388f2b6466b74` |
| `pilot-command-contract.md` | `e625123b8222262fb02b32aeadb2cae5c91d18ff573f04763b0af7ea3f22eb8c` |
| `remediation/REM-CMD-PILOT-D2-001-metadata-compatibility.md` | `fb1408a6e833b73981aa79f0fce8a57d18e9d24aa8f4c11838fd734335973964` |
| `approval/pilot-metadata-compatibility.md` | `1f71ed053573682f788915742beccb1fc7de7c53c3fb5d20b0b8325953331cf0` |
| `validation/session/preparation.json` | `afa7acce7d32e4ef79947ac8db5b78593f49d1aa33b91fd028f28bcfb9205221` |
| `validation/session/implementation/d3/evidence.json` | `e101833651784025c22f805a682a2f96beffce05c646eb2d52bab7c806ee8244` |
| `validation/session/installed_probe.py` | `059c1e4e392de1e00853e4acaadfe97f7a1eefe3f4d1de412ebf4970f07f15cd` |
| `validation/pilot/installed_probe.py` | `8c1233a0a5181566bb188735358141e8718a5aaba205e6c4bfa3a2620a8e43ac` |
| `validation/pilot/harness/prepare.py` | `788f6f8fbc7c4c6f1b53458632c16ecc09153c8d8604cb7ecb776dc8b3075f2e` |
| `validation/pilot/harness/bundle.py` | `46cc788e7aea59add8367de6568bae135cfd3689a813af8d530661f3267d327d` |
| `validation/pilot/baseline.json` | `48c3161cf1a0467c7e95ac11a85de0972d46421b5a9318ee618651f7cc7ad7f1` |

Preserve both dirty Chat examples unstaged with SHA-256:
`config.example.yaml`: `c2f728c98adc5ca773bfdf3170d846a610f15d77eae9a380e1a815534b93c3e7`;
`models-config.example.yaml`: `11e99116d885a431f085b6bd05b5bd30348eb37654fd4c9350a7cca58c527896`.
Do not clean caches, .friday, exports, stores or unrelated work.

## Exact implementation allowlist and limits

Paths below are relative to repository root; no other product path may change.

| Path | Permitted change |
| --- | --- |
| `packages/friday-commands/src/friday_commands/contracts.py` | Eleven DG-01 models plus exactly seven new union/whitelist alternatives; retain all earlier definitions/invariants. |
| `packages/friday-commands/src/friday_commands/__init__.py` | Fourteen additive exports/imports; preserve previous 24 in order/binding. |
| `packages/friday-commands/src/friday_commands/diagnostics.py` (new) | Specs, protocol and factory only. |
| `packages/friday-commands/tests_commands/test_diagnostics.py` (new) | DG-01–05 neutral/standalone tests. |
| `packages/friday-commands/tests_commands/fixtures/diagnostics-metadata.json` (new) | Exact preparation metadata fixture. |
| `packages/friday-commands/tests_commands/test_session_views.py` | Append only fourteen DG-01 names to the existing literal list in `test_session_specs_and_factory_are_immutable`; no other AST change. |
| `packages/friday-chat/src/friday_chat/commands/diagnostics.py` (new) | Narrow typed Chat port, metadata helper, pure renderers, exact outcome adapter and once-only invocation; move three registry helper bodies unchanged. |
| `packages/friday-chat/src/friday_chat/commands/registry.py` | Six compatibility wrapper bodies, new imports/metadata helper and only tuple entries 4,5,6,7,8,15; move `_build_context_text`, `_build_prompt_text`, `_write_export_file` definitions out. All other AST/order/handler-map definitions unchanged. |
| `packages/friday-chat/tests_chat/test_command_diagnostics.py` (new) | DG-03–06 compatibility, dispatch, failure, export, synthetic app tests. |
| `packages/friday-chat/tests_chat/fixtures/diagnostics-baseline.json` (new) | Exact preparation metadata/cases fixture. |
| Both package `README.md` files | Describe diagnostics, shared/host ownership, file effects and explicit type boundaries. |
| Current packet, board/dashboard, log/authority, `validation/diagnostics/`, PAR evidence | Bounded status, preservation, review, receipts and new D3 installed probe only. |

This is twelve package paths, including two READMEs and the narrowly amended
old SESSION test. Every other existing source/test/fixture retains bytes.
Do not add skips/xfails or change old test bodies, parameters, decorators or
assertions. Preserve original counts with a separately identified exact export
assertion expansion; it is an approved schema evolution, never a subset test.

No metadata/dependency/lock/config change. No other package, neutral registry/
pilot/session implementation, Chat contracts/app/runtime/telemetry/turn
processing, generic CLI, accepted adapters/probes, existing domain service,
admission policy, public helper owner or transcript export behavior change.
No new parser, dependency, service locator, `Any`, casts, suppressions, retry,
rollback, progress/confirmation, policy/sanitization redesign or later family/TUI.
Helpers with the same names in `turns/processor.py` are unrelated and stay intact.

## Deliverables and review gates

| Deliverable | Required result before advancement |
| --- | --- |
| D1 / D0–D1 | D0 baselines, inventories and guard controls; approved neutral models/API/specs/handlers, exact fixture and tests. Full Commands/cohort passes including the expanded old literal assertion. Fresh D1 council reconciled before D2. |
| D2 / D2–D3 | Typed Chat port/wrappers/rendering/file effects, exact fixture, once-only ownership, source observations and synthetic app tests. Fresh D2 council reconciled before D3. |
| D3 / D4–D5 | Full owning regressions/preservation and current candidate builds/isolated installed proof; fresh D3 plus complete bounded DIAG aggregate review, then human acceptance. |

Use only **GPT-6.1 Sol/high, GPT-6 Astra/high and Claude Opus 5.5/high**, per the
[roster](../approval/council-roster.md). The earlier two-member PILOT exception
and Gemini unavailability are historical, not this unit's roster. Every review
has fresh context, read-only frozen candidate, private external caches/output,
no builder reasoning, no nested delegation. Explicit shared-checkout exception
may be recorded when necessary; otherwise isolation is preferred. Measure logical
index before status using exact `git ls-files -s -z` stdout and
`GIT_OPTIONAL_LOCKS=0` inherited by every Git child. Verify request, authority,
source/deliverable/protected/dirty pins and identity at start/end. A cache write
to supplied evidence invalidates that review; fix procedures and reissue fresh.

Reconcile all mandatory findings rather than majority-voting or using scores
as approval. A changed candidate gets a fresh delta plus bounded aggregate
review. Escalate after two unsuccessful remediation cycles under policy.
No acceptance, next-family or delivery follows from VERIFIED automatically.

## Required test nodes and evidence

Missing nodes or partial assertions fail their gate. Equivalent parametrization
is allowed without replacing these node names. Async tests must have explicit
`@pytest.mark.asyncio`; no skips/xfails. Use event-controlled bounded awaits with
cleanup, never timing sleeps. Product invariants use exceptions, not assertions.

| ID / node in new neutral test | Mandatory assertions |
| --- | --- |
| DG-T01 `test_diagnostic_models_and_closed_union` | Every field in declaration order, bool-vs-int, optional/negative/invalid values, reasons, exact nested/payload types and subclasses, once-only immutable snapshots, empty/ordered/duplicate values, preview limit, recorded invariants; all old alternatives/invariants retained. |
| DG-T02 `test_diagnostic_specs_exports_and_factory` | Exact ordered literal 38-name API, no duplicates/extra/missing/reordered old or new exports; all bindings, six specs/seven metadata fields/arguments equal package fixture; fresh immutable six-key maps, zero construction reads, empty registry, structural protocol. |
| DG-T03 `test_diagnostic_invocation_validation_order` | All six: exact request then execution before field reads; wrong canonical names before port; execution/spec unused; direct non-string args fail at request construction, strings/subclasses accepted. |
| DG-T04 `test_context_prompt_flags_and_export_order` | One selected text call; exact anywhere/repeated/case/unknown flags; len before export; exact unexported typed data identity/content; matching export method once; returned path; file failure/invalid port return, no other reads/effects, same exception/cancellation. |
| DG-T05 `test_diagnostic_snapshots_once` | Debug/budget/timing call only the matching port once; exact result refusal, typed success/empty recorded data, no rendering/formatting/other capabilities; snapshot data retained in outcome. |
| DG-T06 `test_retrieval_precedence_and_await` | Runtime-before-empty-args, exact bool, no await on unavailable/usage; original args joined, exactly one await; query match; pending state, invalid return, exception/cancellation identity, no retry/other effects. |
| DG-T07 `test_diagnostics_standalone` | Explicit neutral registry dispatch all six, aliases remain generic opt-in, normal/`-O`/`-OO`, valid and invalid boundaries active, stdlib/own-package-only loaded closure. Preload pinned guard explicitly if `-I` ignores PYTHONPATH. |

| ID / node in new Chat test | Mandatory assertions |
| --- | --- |
| DG-T08 `test_diagnostic_metadata_and_frozen_cases` | Exact package fixture identity, 41/3 registry and six metadata records; all 72 source rows under DG-03 decisions, all unchanged pilot/SESSION observations; package-local fixture lookup, no active-doc path at collection/execution. |
| DG-T09 `test_diagnostic_once_only_delegation` | All six one parse/factory/await, fixed spec identity and original parsed args supplied to request; direct wrapper no parse; port construction no context reads; supplied differing context registry, renamed wrappers and custom handlers authoritative. Inject distinct valid typed outcomes for all six and assert Chat consumes them, with no legacy recomputation. |
| DG-T10 `test_diagnostic_projection_order_and_failures` | Trace cached/fallback reads and one-time custom formatting; debug/telemetry/last-turn and counter order, mixed-key failures, empty branches lazy; budget zero/negative/truthy dynamic values; timing .3f/non-numeric errors; exact exceptions and no eager unrelated reads. All four approved cache refusals and falsy fallback. |
| DG-T11 `test_diagnostic_exports_fixed_bytes_and_failures` | Actual scratch directory creation, context debug body before write, prompt body, fixed names/path/footer/no extra newline, repeated overwrite; configured/default root in private cwd, ignored filename args, mkdir/write failure/cancellation identity, no success/rollback on failure, one export request and no export on absent flag. |
| DG-T12 `test_diagnostic_retrieval_projection_and_await` | Runtime/usage precedence and repeated reads, exactly one public await, pending/cancel/failure behavior; dict/list/subclasses vs ignored containers, count before details/previews, sorted keys, total count but first ten previews, limit160/Unicode/control whitespace and ellipsis; no query reinterpretation or unrelated stores. |
| DG-T13 `test_diagnostic_adapter_refusals_and_purity` | Exactly seven allowed data/no-error/no-effect shapes; all other types/subclasses/errors/effects rejected; pure rendering, no second service/file call, exact result defaults. |
| DG-T14 `test_diagnostic_real_app_sequence` | Real synthetic app: conversational turn, all six diagnostics, both scratch file exports, `/history`, `/clear`, `/cls`, `/q`; output/effect/lifecycle and cleanup order, distinct cleared history vs display; no network/providers/real stores. |

In private source copies, prove the new tests reject these changes with named
**test-call assertion failures**, not import/setup errors: extra/dropped/reordered/
duplicate export; shared factory eager-read; double export, debug-count-after-
export, case-insensitive flags, usage-before-runtime, double or unawaited retrieval;
host missing sort, numeric-zero budget, premature stringification of mixed keys,
preview cap/count drift, double formatting, ignored injected result and legacy
engine substitution. Run an unchanged control through the same harness. Record
canonical module roots and hashes before pytest, session finish and afterward;
resolve macOS `/var` aliases on both sides. No mutation to supplied source/env.

## D0 — reproducible guarded preparation

Only after approval, reproduce current before behavior and inventory before
source edits. Use Python 3.13.10 and the existing uv-managed frozen environment;
no sync/upgrade or downloaded Python. Define variables in zsh from repository root:

```sh
export GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1
DIAG_PYTHON="$PWD/.venv/bin/python"
DIAG_HARNESS="$PWD/docs/planning/active/command-refactor/validation/pilot/harness"
DIAG_SCRATCH="$(mktemp -d /tmp/friday-diag-build.XXXXXX)"
export DIAG_PYTHON DIAG_HARNESS DIAG_SCRATCH
# DIAG_WHEELHOUSE is the supplied eight-wheel directory, verified by prepare.py.
"$DIAG_PYTHON" -B "$DIAG_HARNESS/prepare.py" "$DIAG_SCRATCH/prepared" --wheelhouse "$DIAG_WHEELHOUSE"
DIAG_RUNNER="$DIAG_SCRATCH/prepared/pilot_run.py"
export DIAG_RUNNER
"$DIAG_PYTHON" -B "$DIAG_RUNNER" guard python -B "$DIAG_HARNESS/guard_selftest.py"
```

Materialize preparation's exact programs/baseline into scratch, after verifying
preparation's table digest. Refuse overwrite and verify every text hash:

```sh
"$DIAG_PYTHON" -B - <<'PY'
import hashlib, json, os
from pathlib import Path
p=Path('docs/planning/active/command-refactor/validation/diagnostics/preparation.json')
if hashlib.sha256(p.read_bytes()).hexdigest() != '1f8ee9c7e882d0d0e857deb8489b0eeb309e0d1fa5c21ccbf40223e0886a2c55':
    raise RuntimeError('Preparation changed')
d=json.loads(p.read_text()); out=Path(os.environ['DIAG_SCRATCH'])
for name, entry in [('capture_diagnostics.py',d['programs']['capture']),
                    ('compare_diagnostics.py',d['programs']['comparison']),
                    ('frozen-diagnostics.json',d['baseline'])]:
    raw=entry['text'].encode(); target=out/name
    if hashlib.sha256(raw).hexdigest()!=entry['sha256'] or target.exists():
        raise RuntimeError('Invalid identity or overwrite: '+name)
    target.write_bytes(raw)
PY
"$DIAG_PYTHON" -B "$DIAG_RUNNER" comparator python -B "$DIAG_SCRATCH/compare_diagnostics.py" --selftest
```

Export committed clean inputs and run source capture. Receipt labels and output
filenames must differ; do not repeat the historical SESSION collision. At D0:

```sh
DIAG_REVISION=9dbcec54773f10274eea058e5d59edb0ce53b6cc
DIAG_PHASE=before
DIAG_SOURCE="$DIAG_SCRATCH/$DIAG_PHASE-source"
export DIAG_REVISION DIAG_PHASE DIAG_SOURCE
mkdir "$DIAG_SOURCE"
git archive --format=tar --output "$DIAG_SCRATCH/$DIAG_PHASE.tar" "$DIAG_REVISION"
tar -xf "$DIAG_SCRATCH/$DIAG_PHASE.tar" -C "$DIAG_SOURCE"
"$DIAG_PYTHON" -B "$DIAG_RUNNER" "$DIAG_PHASE-diag-capture" python -B "$DIAG_SCRATCH/capture_diagnostics.py" "$DIAG_SOURCE" "$DIAG_SCRATCH/$DIAG_PHASE-observations.json" "$DIAG_REVISION"
"$DIAG_PYTHON" -B "$DIAG_RUNNER" "$DIAG_PHASE-diag-compare" python -B "$DIAG_SCRATCH/compare_diagnostics.py" "$DIAG_SCRATCH/frozen-diagnostics.json" "$DIAG_SCRATCH/$DIAG_PHASE-observations.json" 1dcd83ecd8d2e4e739099eb495e43f98b78439d7bb14e3bebc167ba1b8514e98 8f7a55d5ae773774fa5ef6125215f29ea35b4788af13074451cdd5fc4e2e2464
```

At D2/D4 use an actual committed candidate revision and fresh after paths, adding
`--allow-declared-cache-refusal` only after exact DG-03 approval. Require the four
cache rows to refuse by D2; report **68 exact rows + four approved refusals**, not
72 unchanged rows. The comparer forbids other event/type/value/file drift. Repeat
capture and compare. Capture validates every package src file against Git before
imports, plus both file/path origins against export source roots. Reproduce its
extra-source and changed-byte refusals before imports; no failed setup earns
credit. Whole-build inputs/modes/types are a separate D5 check.

Also materialize the unchanged SESSION capture/comparer from its pinned
preparation, using private outputs/distinct labels: `capture_session.py SOURCE
OUTPUT REVISION`, then `compare_session.py BASELINE OUTPUT BASELINE_SHA
CAPTURE_SHA`. Reproduce all 25 SESSION rows. Run unchanged pilot `capture.py
SOURCE OUTPUT --revision REVISION`, then `compare.py BASELINE OUTPUT
--baseline-sha256 48c3161cf1a0467c7e95ac11a85de0972d46421b5a9318ee618651f7cc7ad7f1`;
all 196 observations must agree. No provider/store/network credentials or real
user data. Synthetic file exports are confined to the private capture directory.

## D1–D4 — tests, static checks and preservation

Materialize both new package fixtures from preparation `fixtures.*.text` at their
exact target paths, checking their embedded digests. No new test reads this
active planning packet. Record original file/test/assertion inventory before
edits; keep every old file except the expressly allowed paths unchanged. AST
audit the one old SESSION test with only its exact fourteen-name list extension
removed; the remainder must equal the baseline. Contracts AST differs only by
the eleven models and seven union/whitelist members. Registry parser/register/
dispatch/admission/handler-map and other 33 tuple entries remain AST-identical.
Moved helper bodies stay equal. Retain all old test definitions/assertion counts.

Use these complete fast gate commands, with runner-owned basetemps/caches:

```sh
"$DIAG_PYTHON" -B "$DIAG_RUNNER" d1 python -B -m pytest -p no:cacheprovider -q packages/friday-commands/tests_commands tests/integration/test_package_cohort_metadata.py
"$DIAG_PYTHON" -B "$DIAG_RUNNER" d2 python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-chat/tests_chat/test_command_diagnostics.py packages/friday-chat/tests_chat/test_command_registry.py packages/friday-chat/tests_chat/test_command_foundations.py packages/friday-chat/tests_chat/test_command_retirements.py packages/friday-chat/tests_chat/test_command_pilot.py packages/friday-chat/tests_chat/test_command_session_views.py
"$DIAG_PYTHON" -B "$DIAG_RUNNER" d3 python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-chat/tests_chat/test_command_diagnostics.py packages/friday-chat/tests_chat/test_session_memory_commands.py packages/friday-chat/tests_chat/test_app_lifecycle.py packages/friday-chat/tests_chat/test_command_production_adapters.py packages/friday-chat/tests_chat/test_display.py packages/friday-chat/tests_chat/test_command_session_views.py
```

At D4 run entire owning suites separately, not root discovery as their proxy:

```sh
"$DIAG_PYTHON" -B "$DIAG_RUNNER" full-chat python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-chat/tests_chat --ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py
"$DIAG_PYTHON" -B "$DIAG_RUNNER" full-commands python -B -m pytest -p no:cacheprovider -q packages/friday-commands/tests_commands tests/integration/test_package_cohort_metadata.py
"$DIAG_PYTHON" -B "$DIAG_RUNNER" full-cli python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-cli/tests_cli
"$DIAG_PYTHON" -B "$DIAG_RUNNER" lint ruff check --no-cache packages/friday-commands/src packages/friday-commands/tests_commands packages/friday-chat/src/friday_chat/commands/registry.py packages/friday-chat/src/friday_chat/commands/pilot.py packages/friday-chat/src/friday_chat/commands/session.py packages/friday-chat/src/friday_chat/commands/session_views.py packages/friday-chat/src/friday_chat/commands/diagnostics.py packages/friday-chat/tests_chat/test_command_diagnostics.py docs/planning/active/command-refactor/validation/diagnostics/installed_probe.py
"$DIAG_PYTHON" -B "$DIAG_RUNNER" types mypy --cache-dir "$DIAG_SCRATCH/mypy" packages/friday-commands/src packages/friday-chat/src/friday_chat/commands/registry.py packages/friday-chat/src/friday_chat/commands/pilot.py packages/friday-chat/src/friday_chat/commands/session.py packages/friday-chat/src/friday_chat/commands/session_views.py packages/friday-chat/src/friday_chat/commands/diagnostics.py
```

At earlier gates omit only not-yet-created D2/D3 paths, recording that bounded
scope; never count missing files as passes. Run changed-Python
`ruff format --check --no-cache`, separately recording unchanged registry debt.
Before counts: Chat1297, Commands/cohort278, CLI155; reconcile actual new cases,
collection, skips and exits. Reproduce/disposition root Ruff and root pytest
through the guarded runner (`-p controls -p no:cacheprovider` for pytest), plus
root `--collect-only` at D4. Run metadata, `uv lock --check --offline` in the
clean export, board validate/render --check, documentation lifecycle and
`git diff --check` over worktree and complete unit range. Tests/static controls
must run on actual current source with canonical origins, not stale exports.

## D5 — clean artifacts and actual installed behavior

Use the pinned existing `bundle.py`, exact 3.13.10 interpreter, eight pinned build
tools and 125 lock-verified artifacts. At D0 perform one baseline closed trial;
at D5 build and replay a committed candidate in separate empty directories:

```sh
"$DIAG_PYTHON" -B "$DIAG_HARNESS/bundle.py" "$DIAG_SOURCE" "$DIAG_SCRATCH/baseline-bundle" "$DIAG_SCRATCH/prepared" --revision "$DIAG_REVISION" --artifacts "$DIAG_LOCKED_ARTIFACTS" --require-pilot-edge
# Set DIAG_SOURCE and DIAG_REVISION to an actual committed candidate for D5:
"$DIAG_PYTHON" -B "$DIAG_HARNESS/bundle.py" "$DIAG_SOURCE" "$DIAG_SCRATCH/candidate-bundle" "$DIAG_SCRATCH/prepared" --revision "$DIAG_REVISION" --artifacts "$DIAG_LOCKED_ARTIFACTS" --require-pilot-edge
"$DIAG_PYTHON" -B "$DIAG_HARNESS/bundle.py" "$DIAG_SOURCE" "$DIAG_SCRATCH/candidate-replay" "$DIAG_SCRATCH/prepared" --revision "$DIAG_REVISION" --artifacts "$DIAG_LOCKED_ARTIFACTS" --require-pilot-edge
```

`DIAG_LOCKED_ARTIFACTS` is a supplied closed raw-artifact directory verified by
the helper. No fetch/network permission is added. Missing exact inputs stop the
gate for a bounded maintainer decision. All child builds/resolves/installs remain
offline/no-index/frozen/private-cache, with explicit tool/interpreter identities,
PyPika lineage and no public same-version workspace substitute. Verify complete
Git inventory/directories/types/modes/bytes before build and at end. An injected
extra source/data control must refuse its exact member **before any build or
fetch**. Both actual 154-artifact/profile hash maps must agree. Neutral closure
exactly one dependency-free distribution/no entry point; Chat closure exactly
the accepted SESSION 138-name/version map (from its pinned D3 evidence), no new
extras/executable; both pip checks, finance/tools imports, lock/artifact checks.

Implement `validation/diagnostics/installed_probe.py` only at D3. Define and
record its exact CLI in evidence before running both actual installed Python
interpreters with `-I -B` and `-I -B -O`. No repository/PYTHONPATH source injection.
Load/hash the pinned guard explicitly, record safe REVIEW_REPO/REVIEW_SCRATCH,
local LiteLLM cost map, disabled bytecode/telemetry and optional Git locks; never
record secrets. Fresh report paths, exact source/probe/artifact revisions, child
commands/exits and both parent and entry-point-child origins are mandatory.
Require final probe/product bytes equal the artifact-source commit; later
commits may change evidence/status only.

Reuse the accepted SESSION complete member/type/directory/byte/executable and
origin check functions via hash-verified read-only helpers. Validate actual
disk inventories against Git, wheel and sdists, including no extra source/data,
empty directories, pyc, symlinks, FIFO, changed/missing bytes or executable drift.
Check both `__file__` and every `__path__`, refuse missing origins and escaped
prefix paths. Bind every Commands/Chat module to its inventoried distribution
root, including the guarded entry-point child; an in-prefix shadow must refuse.

Run unchanged pilot installed proof on candidate artifacts. The old SESSION
neutral probe's 24-name assertion is intentionally obsolete for an approved
38-name expansion: preserve its original file and do not claim it passed.
In the new aggregate probe, copy `neutral_behavior` as a named retained SESSION
check, changing only function name and the fourteen appended expected-export
names (AST-audit the remaining body against the pinned function). Reuse the
unchanged SESSION Chat behavior check and helpers with hash-checked inputs.
Run retained SESSION semantics in both lanes/modes alongside new DIAG proof.
Never temporarily spoof `api.__all__`, monkeypatch an old gate to pass or weaken
exactness. The source old test's analogous explicit extension is separately
required at D1. These are the entire approved evolving-surface exceptions.

New installed DIAG proof requires model/factory/strict/optimized neutral checks,
all six actual canonical delegations, exact metadata/help/args and real outcome
consumption. Inject distinct typed results for all six to reject a shadow engine
that calls shared code then discards it. Verify per-dispatch factory/handler
counts unconditionally for these six, not just when a spy happens to fire.
Exercise custom and renamed wrappers, current context, fallback and recorded
snapshots, runtime/usage precedence, pending/error/cancel propagation, fixed
scratch export bytes/footer/order and no unrequested effects. A source-only
capture is not installed execution proof. Guarded entry-point `--help` must pass.

For each private copied installation first prove copied sys.prefix, executable
and canonical Commands/Chat roots; mutate only that copy, require exact refusal
reason and re-run restored clean probes. Normal and optimized controls cover:
extra source/data/directory/pyc/symlink/FIFO, changed/missing bytes/executable,
file-only/namespace/missing/mixed paths, valid file plus escaped path, and
in-prefix shadow modules. Add archive extra/duplicate/byte drift and sdist
extra/directory controls. Setup/import/report-collision failures get no credit.

## Freeze, reporting and stop

Each D1/D2/D3 candidate is committed locally and frozen before its council.
Report authority/path/pin/branch/base/range, exact checks, actual exits/counts,
preservation/AST evidence, test coverage, origin checks, environment and all
raw receipts. Keep embedded text/hash and raw-file hashes equal. Label earlier
failed attempts and inspected historical evidence separately; do not overwrite
accepted reports or transcribe their scores as correctness evidence.

Keep current packet/index/tactical/next-phase/log/authority/board/dashboard in
agreement at every gate (`execution_phase`, `validation_state`, next action,
review roster, acceptance pending). Execution log is append-only. Only six DIAG
PAR rows gain bounded evidence; no generic P0/P1 closure. At final VERIFIED
prepare a concrete bounded acceptance handoff and stop for the maintainer.

Stop for missing exact approval/input/guard, drift in protected/frozen/source
pins or dirty bytes, unexpected path/dependency/type-policy change, new failing
check/collection loss, a tighter legacy boundary beyond the explicit decisions,
lost await/format/export/lifecycle behavior, a duplicate engine, mismatched
artifacts/probe source, or incomplete council. No push, PR, merge, release,
next family or TUI follows automatically.
