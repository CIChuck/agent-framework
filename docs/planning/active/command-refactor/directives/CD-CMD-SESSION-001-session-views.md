# CD-CMD-SESSION-001 — shared history and conversation clear

Status: **draft; construction approval not granted**. Owner: Chuck Russell.
Prepared 2026-11-08. Branch: `feature/command-retirement`. Unit: SESSION-001.
The maintainer's “proceed” authorizes contract/directive preparation and guarded
read-only characterization only. It does not approve this construction.

## Authority, exact approval and execution base

Follow AGENTS, engineering/lifecycle/independent-validation policies and the
board, then the exact proposed [session contract](../session-command-contract.md),
SHA-256 `f29ac447d9cc76c1c1bb1dff9d6fc9ef619ca3b5ff43f1833ee5346250a3e003`. Approve that contract first, then this exact directive,
or approve both together. Record approver, date, instruction and both digests
before any product/test edits. Contract approval explicitly dispositions the
two new closed payload variants and the direct non-string-args boundary in
SV-04; it does not extend the accepted pilot's old scope retroactively.

Product/test/metadata/lock baseline: `38a0c58a0b533edc29908992c8c6ee64fa04eb20`.
Only documentation/approval descendants with identical package, test, script,
root metadata and lock bytes may precede construction. Record actual start
HEAD, branch and equality; drift requires a refreshed approved baseline.
The initiative stays started/local; SESSION-001 itself is unapproved.

| Frozen input | SHA-256 |
| --- | --- |
| `shared-command-api.md` | `e5ba883fb246967320243e1dbc9c2a70fcf6189c05540a45961388f2b6466b74` |
| `approval/pilot-acceptance.md` | `7968c499d768bcf632afaebb5d0ec0accf24cdcf385690453f6db05e33f8f618` |
| `pilot-command-contract.md` | `e625123b8222262fb02b32aeadb2cae5c91d18ff573f04763b0af7ea3f22eb8c` |
| `remediation/REM-CMD-PILOT-D2-001-metadata-compatibility.md` | `fb1408a6e833b73981aa79f0fce8a57d18e9d24aa8f4c11838fd734335973964` |
| `approval/pilot-metadata-compatibility.md` | `1f71ed053573682f788915742beccb1fc7de7c53c3fb5d20b0b8325953331cf0` |
| `validation/pilot/baseline.json` | `48c3161cf1a0467c7e95ac11a85de0972d46421b5a9318ee618651f7cc7ad7f1` |
| `validation/pilot/harness/capture.py` | `96f3f53c970fe1051a2b498250cce397ea952101483982103e9419391f4c3c4a` |
| `validation/pilot/harness/bundle.py` | `46cc788e7aea59add8367de6568bae135cfd3689a813af8d530661f3267d327d` |
| `validation/pilot/installed_probe.py` | `8c1233a0a5181566bb188735358141e8718a5aaba205e6c4bfa3a2620a8e43ac` |
| `validation/session/preparation.json` | `afa7acce7d32e4ef79947ac8db5b78593f49d1aa33b91fd028f28bcfb9205221` |

Preserve both original dirty Chat example configurations, with SHA-256
`c2f728c98adc5ca773bfdf3170d846a610f15d77eae9a380e1a815534b93c3e7`
and `11e99116d885a431f085b6bd05b5bd30348eb37654fd4c9350a7cca58c527896`
respectively (`config.example.yaml`, `models-config.example.yaml`). Never stage,
copy into fixtures/artifacts or change them. Set `GIT_OPTIONAL_LOCKS=0` before
Git/subprocess calls. Logical index pins hash exact `git ls-files -s -z` stdout,
not raw `.git/index`. Preserve caches, stores, unrelated work and frozen reports.

## Exact implementation and documentation paths

| Allowed path | Bounded change |
| --- | --- |
| `packages/friday-commands/src/friday_commands/contracts.py` | Add SV-01's three dataclasses, expand only the `FoundationData` alias and outcome data-type whitelist by two variants. Retain every prior constructor/invariant verbatim. |
| `packages/friday-commands/src/friday_commands/session_views.py` (new) | Two specs, injected `SessionPort` and immutable handler factory implementing SV-01–03. |
| `packages/friday-commands/src/friday_commands/__init__.py` | Exactly six additive exports and accurate module description; preserve all 18 prior exports. |
| `packages/friday-chat/src/friday_chat/commands/session_views.py` (new) | Typed Chat port, shared metadata projection, `invoke_session` and exact two-shape result renderer from SV-04. |
| `packages/friday-chat/src/friday_chat/commands/registry.py` | Imports, the two delegating wrapper bodies, a metadata projection helper, and only default-spec entries 0/2. Existing handler map, other functions and 37 other tuple entries unchanged. |
| `packages/friday-commands/tests_commands/test_session_views.py` (new) | New models, shared/standalone semantics, port counts/order, failures and validation tests. |
| `packages/friday-chat/tests_chat/test_command_session_views.py` (new) | Frozen comparisons, real delegation, adapter/context and app sequence tests. |
| `packages/friday-chat/tests_chat/fixtures_session/session-baseline.json` (new) | Exact `metadata`/`cases` projection of the frozen baseline; generated fixture bytes/digest specified in preparation evidence. Tests resolve it inside their own package. |
| Both package `README.md` files | Describe shared session behavior, host/domain ownership and preserved `/clear` vs `/cls` distinction. |
| Current initiative status/approval/log/PAR, `validation/session/`, board/dashboard | Baseline/preservation/receipts, future installed probe, frozen review request and controller state only. |

All existing tests, assertions and fixtures remain byte-identical, including
foundation/pilot/retirement tests. Add the new coverage without weakening or
rewriting old tests, adding skips/xfails or fixing old async-marker debt.
Do not modify neutral `registry.py`/`pilot.py`, Chat contracts/app/runtime/adapters/
`commands/session.py`/pilot adapter, other packages, metadata/lock, root AGENTS/
README, cohort/artifact scripts, configuration, terminal or domain services.
No new dependency, generic capability layer, confirmation, service migration,
maintenance lock, progress/retry/rollback, parser change or later family/TUI work.
Do not edit this approved directive/contract, old API, preparation baseline or
accepted pilot harness/probe after approval; a defect needs an explicit amendment.

## Deliverables and incremental acceptance

| Deliverable / gate | Required result before advancing |
| --- | --- |
| D1 / S0–S1 | Reproduce frozen baselines and capture test/source inventory. Implement only shared models/API/handlers plus new neutral tests and package docs. Full Commands/cohort and strict import/optimized checks pass; fresh D1 council reconciled before D2. |
| D2 / S2–S3 | Chat port/projection/wrappers plus new fixture/tests; exact 25 session observations and all 196 pilot observations match. App sequence/failure boundary and shared-outcome ownership pass; fresh D2 council reconciled before D3. |
| D3 / S4–S5 | All owning after-suites, source/assertion preservation, clean Git artifacts/isolated installs and new installed session proof; fresh D3 plus complete bounded SESSION aggregate review, then maintainer acceptance. |

The prior council-after-each-deliverable preference is retained in this proposal.
Freeze the actual requested reviewer membership before dispatch; the pilot's
two-member exception was specifically for its D3 and is not a blanket waiver
for this new unit. Independent reviews are fresh, read-only and own-scratch,
with no builder private reasoning or nested delegation. Use delta plus full
bounded aggregate review after fixes, and escalate after two unsuccessful
remediation cycles. Scores never override mandatory findings or grant acceptance.

Every requirement below owns concrete nodes in the **new** files; missing nodes
or placeholder assertions fail the gate. `N` means neutral new test file, `C`
means Chat new test file. All new async tests use explicit asyncio markers.

| ID | Required test nodes and evidence |
| --- | --- |
| SESSION-01 | N:`test_models_snapshot_and_reject_invalid_values`, `test_outcome_union_addition_preserves_old_invariants`, `test_session_specs_and_factory_are_immutable`. Exact metadata/order, six exports only, empty registry, zero port reads at factory construction; scalar/mapping/subclass, frozen-state and `-O`/`-OO` validation controls. |
| SESSION-02 | N:`test_history_snapshot_once_preserves_order`, `test_history_ignores_unrelated_fields`. Feed out-of-order duplicate turns; one snapshot, no sorting/filtering or clear/memory/context reads, exact empty/nonempty typed data, ignored args/spec/execution, snapshot immutability and invalid-port refusal. |
| SESSION-03 | N:`test_clear_orders_history_before_memory_await`, `test_clear_failure_and_cancellation_boundaries`. Exact once-only calls, task pending with history already empty, no premature success; clear failure prevents memory, memory failure/cancel leaves history cleared, same exception identity and no retry/rollback. Bound waits and clean up all test tasks. |
| SESSION-04 | N:`test_invocation_validation_precedes_port_access`, `test_standalone_session_dispatch`. Exact request then execution checks before fields/name, all wrong-name pairings and tripwire args/spec/session fields. Explicit standalone registry executes both in normal/optimized modes under stdlib-only import guard; no auto-registration. |
| SESSION-05 | C:`test_session_observations_match_frozen_fixture`, `test_metadata_and_help_are_unchanged`. Exact 25 captured rows (including exception messages/events), two metadata records/all fields; 41/3 metadata and all 196 pilot observations remain exact. Original registry/retirement tests pass. |
| SESSION-06 | C:`test_session_delegates_once_and_consumes_shared_outcome`, `test_custom_and_renamed_session_handlers`. One parse, canonical request/spec identity, original args, one factory/await; distinct injected HistoryData changes output. Explicit custom history/clear/retired handlers bypass shared factory; renamed wrappers and differing context registry use supplied context. No text reparse or shadow legacy body. |
| SESSION-07 | C:`test_history_projection_preserves_legacy_formatting`, `test_session_outcome_adapter_refuses_other_shapes`. Preserve Unicode/newlines/empty/duplicate/ordered turns, f-string numeric/None/list members, custom string-subclass formatting exactly once, malformed pairs and formatting exceptions without unrelated runtime reads. Invalid/new/old payload, error and effect combinations refuse explicitly. |
| SESSION-08 | C:`test_clear_uses_public_current_session_memory_after_history`, `test_app_history_clear_history_sequence`. Runtime absent/present, bool return true/false ignored, in-place list/alias identity, runtime/history/memory failures/cancellation and pending await state. Direct wrappers ignore metadata; no display or extra store calls. Real synthetic FridayChatApp sequence shows cleared memory and history; existing exit/help/clear-screen behavior, cleanup and PTY tests still pass. |
| SESSION-09 | All original test/fixture/source hash inventories, retained-definition AST equality and full owning suites. No assertion deletion/weakening, lost collection, new skip or changed dependency/profile version. Preserve other 39 command paths (including pilot) and all nine retirement negatives. |
| SESSION-10 | New `validation/session/installed_probe.py` runs actual isolated installed normal/optimized lanes; proves exact current source/data/file/directory/sdist inventories, both origins, model/port semantics and real Chat shared delegation. Full S5 requirements below; no source-path injection can satisfy installed proof. |

## S0 — reproducible baseline and guard

Preparation evidence contains exact source/comparison programs and raw receipts.
Current planning preparation reproduced 25 cases, 434 related Chat tests and
217 Commands/cohort tests; **no new SESSION APIs/tests or installed SESSION proof
exist yet**. Historical full pilot/build receipts are inspected context only.
S0 must pass again under the approved construction start before any source edits.

Use the existing workspace Python **3.13.10** test environment with locked dev
dependencies; eight pinned wheels bootstrap build tools, not the full test env.
Build/resolve/install target remains macOS/arm64/3.13.10. Stop if unavailable;
do not use bare `--python-version 3.13`. Materialize the unchanged accepted
pilot preparer/guard using a new empty external scratch directory:

```sh
export GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1
SESSION_PYTHON="$PWD/.venv/bin/python"
SESSION_HARNESS="$PWD/docs/planning/active/command-refactor/validation/pilot/harness"
SESSION_PREPARATION="$PWD/docs/planning/active/command-refactor/validation/session/preparation.json"
SESSION_SCRATCH=$(mktemp -d -t friday-session-check)
export SESSION_PYTHON SESSION_HARNESS SESSION_PREPARATION SESSION_SCRATCH
"$SESSION_PYTHON" -B "$SESSION_HARNESS/prepare.py" "$SESSION_SCRATCH" --fetch-build-tools
"$SESSION_PYTHON" -B "$SESSION_SCRATCH/pilot_run.py" guard python -B "$SESSION_HARNESS/guard_selftest.py"
```

For offline startup replace `--fetch-build-tools` with
`--wheelhouse /absolute/path/to/a/hash-verified-eight-wheelhouse`; the current
preparation receipt records the actual source path. Verify all guard refusal
and permitted controls before imports. Synthetic stores/fixtures stay in scratch;
do not remove SQLite authorizers or touch user/repository stores. The runner
sets scratch caches, basetemps, clean Git config fixtures, offline/frozen/no-sync,
local LiteLLM cost map and no indexes. Record every actual argv/exit/cwd and safe
required environment, tool/version/helper hashes and failed historical attempts.

Materialize the two diagnostic programs from their frozen embedded bytes:

```sh
"$SESSION_PYTHON" -B - "$SESSION_PREPARATION" "$SESSION_SCRATCH" <<'PY'
import hashlib, json, sys
from pathlib import Path
d = json.loads(Path(sys.argv[1]).read_text())
for key, name in (("capture", "capture_session.py"), ("comparison", "compare_session.py")):
    program = d["programs"][key]
    raw = program["text"].encode()
    if hashlib.sha256(raw).hexdigest() != program["sha256"]:
        raise RuntimeError("Diagnostic program identity drift")
    destination = Path(sys.argv[2]) / name
    if destination.exists():
        raise RuntimeError("Refuse program overwrite")
    destination.write_bytes(raw)
baseline = d["baseline"]
raw = baseline["text"].encode()
if hashlib.sha256(raw).hexdigest() != baseline["sha256"]:
    raise RuntimeError("Frozen baseline identity drift")
destination = Path(sys.argv[2]) / "frozen-session-baseline.json"
if destination.exists():
    raise RuntimeError("Refuse baseline overwrite")
destination.write_bytes(raw)
PY
"$SESSION_PYTHON" -B "$SESSION_SCRATCH/compare_session.py" --selftest
```

Set `SESSION_PHASE=before` and the baseline revision below; at S2 use `after`
and a committed actual product candidate. Local WIP commits for source captures
and clean builds are permitted after approval; they grant no acceptance/push.
Archive only committed bytes, including clean configuration templates:

```sh
SESSION_PHASE=before
SESSION_REVISION=38a0c58a0b533edc29908992c8c6ee64fa04eb20
SESSION_SOURCE="$SESSION_SCRATCH/$SESSION_PHASE-source"
export SESSION_PHASE SESSION_REVISION SESSION_SOURCE
mkdir "$SESSION_SOURCE"
git archive --format=tar --output "$SESSION_SCRATCH/$SESSION_PHASE.tar" "$SESSION_REVISION"
tar -xf "$SESSION_SCRATCH/$SESSION_PHASE.tar" -C "$SESSION_SOURCE"
"$SESSION_PYTHON" -B "$SESSION_SCRATCH/pilot_run.py" "$SESSION_PHASE-session" python -B "$SESSION_SCRATCH/capture_session.py" "$SESSION_SOURCE" "$SESSION_SCRATCH/$SESSION_PHASE-session.json" "$SESSION_REVISION"
```

The capture verifies the complete package **src file** inventory/bytes against
the named Git commit and loaded Friday origins against export source roots.
It is not whole-build provenance; the separate bundle proof covers all build
inputs, types/modes/symlinks/directories. Refuse extra source-file and modified
source controls before imports; never mutate supplied exports for controls.
Compare via the embedded comparator using this frozen baseline/digest/program:

```sh
"$SESSION_PYTHON" -B "$SESSION_SCRATCH/compare_session.py" "$SESSION_SCRATCH/frozen-session-baseline.json" "$SESSION_SCRATCH/$SESSION_PHASE-session.json" 3210852a23743420fdcc61e2c213dedc632431c8d39b831cca36da3e2595ed46 5c72294b80ebf63eb68330b7d74e1bb7090b077ab175eb01069f9f84a3e3bd24
```

The materialization command above supplies `frozen-session-baseline.json` from
the pinned preparation bytes. The comparator checks metadata/cases with exact JSON value types,
order and capture identity, excluding revision/path provenance differences.
Also run the unchanged pilot capture/compare against its pinned baseline using
the same clean export and distinct output/receipt names. The exact helper CLI
is `capture.py SOURCE OUTPUT --revision REVISION`, then `compare.py BASELINE
OUTPUT --baseline-sha256 <pinned pilot baseline hash>`.

## S1–S4 — fast checks and preservation

After each named new file exists, run these gate commands; missing files fail,
never become skipped checks. S1 covers SESSION-01–04, S2 covers05–07 and S3 covers08.

```sh
"$SESSION_PYTHON" -B "$SESSION_SCRATCH/pilot_run.py" s1 python -B -m pytest -p no:cacheprovider -q packages/friday-commands/tests_commands tests/integration/test_package_cohort_metadata.py
"$SESSION_PYTHON" -B "$SESSION_SCRATCH/pilot_run.py" s2 python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-chat/tests_chat/test_command_session_views.py packages/friday-chat/tests_chat/test_command_registry.py packages/friday-chat/tests_chat/test_command_foundations.py packages/friday-chat/tests_chat/test_command_retirements.py packages/friday-chat/tests_chat/test_command_pilot.py
"$SESSION_PYTHON" -B "$SESSION_SCRATCH/pilot_run.py" s3 python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-chat/tests_chat/test_command_session_views.py packages/friday-chat/tests_chat/test_session_memory_commands.py packages/friday-chat/tests_chat/test_app_lifecycle.py packages/friday-chat/tests_chat/test_command_production_adapters.py packages/friday-chat/tests_chat/test_display.py packages/friday-chat/tests_chat/test_command_pilot.py
```

Before edits record all package/test/script/root metadata hashes, existing test
function/assertion inventories and ASTs for retained definitions. At S4 prove
every original test/fixture and all source outside the exact allowlist retain
bytes. In the registry only wrappers and helper/tuple/import edits above may
differ; all parser/dispatch/admission/other-handler ASTs stay equal. In contracts
all original models remain identical except the expressly expanded union and
outcome whitelist; original outcomes/invariants retain test coverage. Only
PAR-003/017 gain current case evidence, not broader P0/P1 closure.

At D2, materialize the one new package fixture from preparation `fixture.text`;
check its exact SHA-256
`3b512406d989e7d114fdcc17ac270eaccb3bcf772dc09a15fd566b10afeb6ea7`.
It contains only frozen `metadata`/`cases`, not export provenance. No tests
may open the active planning packet at collection or execution time.

Run the entire Chat suite excluding `test_live_lmstudio.py`, entire Commands/
cohort suite and entire CLI suite with the runner (Chat uses `-p controls`, all
use `-p no:cacheprovider`). Run focused `ruff check --no-cache` on all Commands
source/tests, Chat registry/pilot/session/new session_views adapters, the new
Chat test and new installed probe; changed-Python `ruff format --check --no-cache`;
mypy on **all** Commands source plus Chat registry, pilot, session and new
session_views adapters explicitly. New/changed compliant files must pass;
legacy registry formatting remains separately failed, unwaived baseline debt.
Before counts are Chat 1,228 / Commands-cohort 217 / CLI 155; record actual collection,
new cases, skips and exits rather than relying on totals alone.

Also run root `ruff check --no-cache .` and root pytest with `-p controls` and
`-p no:cacheprovider`; metadata, offline lock, board, dashboard `render --check`,
documentation lifecycle and diff whitespace checks. Reproduce/disposition root
Ruff 534, sole root `test_display` import-file mismatch and registry-format
baseline failures separately from regressions. No blanket passing-repo claim
or waiver is authorized; a new failure/collection loss stops the unit.

## S5 — clean artifacts, actual installed execution and review

Use the pinned accepted `bundle.py` as the authoritative closed build recipe.
At S0 execute one unchanged baseline trial; at S5 build a committed actual
candidate and replay offline into a different empty directory. Full Git input
inventory/mode/type/byte equality and a private archive are mandatory before
build/fetch and at end; an extra source/data control must fail first. Never
hand-edit an export to repair a build or use public same-version workspace
packages. The helper already records/sanitizes uv state, explicit interpreter,
eight pinned tools, marker-aware locked hashes and PyPika sdist-to-wheel lineage.

```sh
"$SESSION_PYTHON" -B "$SESSION_HARNESS/bundle.py" "$SESSION_SOURCE" "$SESSION_SCRATCH/baseline-bundle" "$SESSION_SCRATCH" --revision "$SESSION_REVISION" --fetch --require-pilot-edge
# At S5 set SESSION_SOURCE/REVISION to the committed candidate and use new dirs:
"$SESSION_PYTHON" -B "$SESSION_HARNESS/bundle.py" "$SESSION_SOURCE" "$SESSION_SCRATCH/candidate-bundle" "$SESSION_SCRATCH" --revision "$SESSION_REVISION" --artifacts "$SESSION_SCRATCH/baseline-bundle/locked-artifacts" --require-pilot-edge
"$SESSION_PYTHON" -B "$SESSION_HARNESS/bundle.py" "$SESSION_SOURCE" "$SESSION_SCRATCH/candidate-replay" "$SESSION_SCRATCH" --revision "$SESSION_REVISION" --artifacts "$SESSION_SCRATCH/baseline-bundle/locked-artifacts" --require-pilot-edge
```

Offline alternatives may supply the exact raw locked-artifact directory from
preparation evidence instead of `--fetch`. Permitted network is only the exact
hash-pinned public HTTPS artifact URLs at `files.pythonhosted.org` used by the
preparer/bundle fetch; all build/resolve/install children remain offline,
no-index and scratch-cache. No credentials/live providers/application network.
No new source-only exception beyond pinned PyPika, dependency upgrade or new
resolver target. Both trials' actual artifact/profile hashes must agree.

Neutral closure stays exactly one dependency-free Commands distribution;
default Chat stays the locked 138 distributions with the existing required
Commands edge, successful pip checks/finance/tools imports, no diagnostic
extras or legacy executable. Prove the full name/version map equals the current
accepted pilot profile; a count alone is insufficient. No lock edit is allowed.

First run the pinned existing pilot installed probe against candidate artifacts
to retain its proof; its CLI arguments are `--lane neutral|chat --prepared DIR
--source EXPORT --dist BUNDLE/g5-dist --profile BUNDLE/neutral-profile.txt|default-profile.txt
--baseline PILOT_BASELINE --report FRESH_OUTPUT`. Then add/run the new SESSION
installed probe for SESSION-01–10's applicable subset. Use actual venv Python
`-I -B` and `-I -B -O` outside checkout in both lanes. Explicitly load/verify
the pinned guard before application imports: `-I` ignores PYTHONPATH. Record
safe required environment (REVIEW_REPO, own REVIEW_SCRATCH, local LiteLLM cost
map, disabled bytecode/telemetry), helper/bootstrap and script hashes.

The new probe must import installed packages without prepending source paths.
The source export is only an inventory oracle. Compare complete Commands/Chat
installed file **and directory** sets and bytes with Git/wheels, all sdist
project members and generated metadata allowlists. Reject extra source/data/
empty directories/bytecode/symlink/special members; no generated package-tree
exemptions under disabled bytecode. Check file origin **and every package search
path** for all Friday modules, including entry-point child. For changed Chat/
Commands modules additionally bind origins to their inventoried distribution
package roots, preventing a different in-prefix shadow from satisfying the proof.
Each private copied-installation control must first prove its interpreter and
package roots; match the exact refusal reason in normal/optimized modes.

Reuse accepted origin/member checks without modifying the frozen old probe;
new session proof requires immutable models, once-only port calls/await order,
exceptions/cancellation, standalone host isolation, actual Chat canonical
delegation and distinct injected HistoryData consumption, metadata/help/args,
custom/context/renamed behavior and guarded entry help. Do not call the
source-injecting characterization tool an installed execution test. Require
artifact checker on both selected wheels/sdists and prove final probe/source
bytes equal the artifact-source commit, subsequent commits status/evidence only.

Commit a stable candidate, freeze contract/directive/input/product/protected
pins and logical index/status, then obtain fresh read-only D3 plus complete
bounded SESSION aggregate review. Preserve actual receipts, historical failures
and separate reproduced from inspected evidence. Stop after VERIFIED for bounded
maintainer acceptance; no next-family or delivery work follows automatically.

Stop for changed pins/authority/dirty hashes, missing fixture/guard/tool, failed
new check, stricter legacy behavior outside the approved boundary, unsupported
history projection, broadened memory clearing, dependency/version changes,
non-identical retained code/tests, unapproved path or source/probe/build drift.
