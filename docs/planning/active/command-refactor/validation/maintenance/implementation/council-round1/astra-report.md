# MAINT-001 independent implementation review — round 1

**VERIFIED** — advisory score **9.5/10**. No mandatory implementation findings.

Reviewer: GPT-6 Astra, high reasoning effort, fresh independent context, 2026-11-10. Single reviewer; no nested agents. This is bounded implementation conformance, not human acceptance, UAT completion, delivery authorization, or whole-repository health certification.

## Mandatory findings and mitigation

1. None identified in the bounded candidate. No product remediation requested by this review.

Residual advisory: the safety envelope is complex and validation is limited to macOS arm64 / Python 3.13.10 with deterministic doubles. Keep the requested human UAT gate and existing root debt separate. The score reflects strong independent source, regression, mutation and installed evidence, with a deduction for those platform and operational limits; it does not derive from a controller threshold or earlier scores.

## Identity and authority

Request SHA256 was checked **before reading**: `38e70301b045691b84c2c324ca972ec9db76306b330b6dee68ba3bf5d9bb8d76`.

- Workdir: `/Users/chuckrussell/Dev/gendev/agent-framework`.
- Branch: `feature/command-retirement`.
- Frozen candidate: `b15ee091a1bfae07b61de521d6478b39ca4b48d2`.
- Construction diff: `fcc1ecb1..b15ee091a1bfae07b61de521d6478b39ca4b48d2`, explicit product paths only; retained as `product.diff`.
- Product baseline: `2b0850bfe6cfc6a91d744fa4440a40eaadaf3a60`.
- Artifact/product source: `ae15a5374350807bd909bc823078087a53a47ce4`; runtime source: `6318959eeb4bed55ded0f22d66519645317b97de`.
- Probe SHA256: `d0cb264535eef5b8c13a0af3ff8fcd0a298360eb06bd2e645c38bbe2687772de`.

`request.json` contains the exact frozen authority manifest. AGENTS, engineering/lifecycle/independent-validation policies, validator and council skills, conditional approval, exact activation, specification, directive, ownership/remediation constraints and fixed vectors were used. Activation is authority evidence only. No historical council report bodies or peer implementation reports were read; no builder transcript/private reasoning was supplied. No verdict was inherited. General memory guidance was used only for read-only review procedure.

The explicit shared-checkout read-only exception was used. All generated work is beneath this new private scratch. No repository edit, cleanup, staging, commit, provider call, external contact or personal-store operation was performed. Personal files were hash-read only as requested.

## Criterion matrix

| Criterion | Outcome | Source and independent evidence |
|---|---|---|
| MI-01 | PASS | All 14 authority, 14 deliverable, 72 product and 461 external pins match. `scope-audit.json` finds no unexpected changed path, configuration/lock/Commands modification, added suppression, skip or xfail. Exact conditional activation binds the reviewed directive. |
| MI-02 | PASS | Memory `mutation.py`: strict frozen count/selection contracts, normalized command/plan binding, instance-local begin/end receipts, exact returned synthesis-result identity, consumed batches and persisted judge readback. Selection tests and fresh broad-scope rejection; installed normal and -O proofs. |
| MI-03 | PASS | Memory `pipeline.py` owns planned stages, skips, provider assessments, command construction, lifecycle and postconditions. Chat coordinator removes local order/skip loop and invokes `execute_pipeline` once. Full owning suites, named order cases and installed one-call Chat proof pass. |
| MI-04 | PASS | Pending selector preserved; fresh synthesis follows pending verdict writes; created verification obtains exact operation receipt, including empty/migration-only batches. Three-role strict coverage/decoder retained in shared provider contracts. Fresh scope controls and real-store installed flows pass. |
| MI-05 | PASS | `_inspect_preflight` distinguishes execute from preview, uses configuration-only checks for verification roles, readiness for selected synthesis/embedding; direct execute rechecks current stores. Preview and missing-capability tripwires, named cases and installed direct/headless proof pass. |
| MI-06 | PASS | `ShieldedMemoryMaintenanceBoundary.run_atomic` drains repeated cancellation and gives worker failure priority. Execute checks callback once/actual object identity and closes operation in finally. Chat uses existing transaction rollback and atomic boundary. Four fresh unsafe-boundary call-phase assertion witnesses; installed cancellation/outer restore and rollback flows pass. |
| MI-07 | PASS | Shared receipt digest binds actual effective references; coordinator correlates started/planned/terminal facts and stores immutable sidecars through existing durability writer. New-stage faults, sidecar failures, substituted/omitted scope, foreign receipts and unknown recovery versions covered by named/owning suites and inspected mutation witnesses. Fixed-vector bytes unchanged. |
| MI-08 | PASS | Mutation readback counts final persisted judge statuses; successful count totals strict, failure/deferred/skipped unavailable. Registry labels rolled-back/uncertain-retention counts as attempted. Explicit --full scoped parser/help covered; approved exact-cell retained comparison passed. |
| MI-09 | PASS | 46 named cases pass. Real graph/Chroma headless helper uses explicit runtime checks (also under -O), verifies no Chat imports and complete chain. Fresh clean/source mutants have canonical private origins and identical start/finish/end hashes. No existing test removed; assertion deltas mapped below. |
| MI-10 | PASS | Own clean closed build: 13 workspace builds, 125 locked inputs, 154 actual artifact hashes equal both supplied trials. Profiles match both trials and accepted normalized 138-package map; neutral closure 1. Four actual installed probes pass. Fresh copied member/origin/order/scope/count refusals plus restored clean control. Raw v1 fixture provenance and materialization verified; installed public-reader completed history and actual interrupted recovery pass distinctly. |
| MI-11 | PASS within approved exception | Commands/cohort 621, Memory 802 plus one existing skip, CLI 155. Chat 1413 pass / 15 failures retained. Exact separate retained comparison passes. Fourteen immutable help/metadata rejections reflect only approved reorganize cells; dirty default failure isolated by fresh committed-default success. Root debt remains unwaived. |
| MI-12 | PASS | Board validates 36 tasks, dashboard current, documentation lifecycle 970 files. Current MAINT state is implementation validation/in_review, with UAT and acceptance due. Histories distinguished from final artifact proof. Final protected/personal/metadata/index/status audit unchanged. |

## Fresh execution

- Offline preparation from supplied eight-wheel wheelhouse; no fetching. Guard selftest passed 18 refusal controls.
- Commands/cohort: **621 passed**.
- Memory: **802 passed, 1 pre-existing skip**.
- Chat: **1413 passed, 15 failed**. Failures were not deselected or monkeypatched. Live LM Studio exclusion is the directive's offline exclusion.
- CLI: **155 passed**.
- Named pipeline/selection/Chat/headless/recovery: **46 passed**.
- Exact retained comparison: **1 passed** (covers the bounded retained families, not only one behavior).
- Clean committed-default check: **1 passed**, using this reviewer's source export.
- Changed Python lint, seven new-file format checks, ten-source mypy, 18 package metadata checks, board/dashboard/docs: all exit 0. Explicit mypy `--cache-dir` is private; the runner also sets `MYPY_CACHE_DIR` to its own private `prepared/mypy-cache`.
- Offline lock check on both artifact source and exact frozen candidate export: exit 0, 214 packages.
- Unit and staged whitespace: exit 0.
- Own closed bundle: exit 0. All 154 actual artifact hashes match the supplied final build and independent replay, not just their manifests. Raw default-profile bytes differ from the accepted profile's formatting/comments; normalized name/version maps are exactly equal. Both supplied-trial profiles match own build byte-for-byte.
- Actual installed neutral and Chat, each normal `-I -B` and optimized `-I -B -O`: all exit 0. Chat probes exercise real disposable stores, no-Chat headless execution, fixed vectors, scoped counts, migration-only synthesis, cancellation/outer restore, one-call Chat, rollback, v1 recovery, retained repair and entry-child origins.

### Fresh rejection controls

`source-controls-r2/ledger.json` records exact argv, exits and witnesses. Unchanged control exit 0; old-order exit 1 with 10 assertion witnesses; broad-generated exit 1 at `test_generated_scope_is_exact`; unsafe-default-boundary exit 1 with four `test_default_and_injected_cancellation_boundaries` assertion witnesses. All failures credited here are call-phase, not setup/import/collection. Start/session-finish/end module hashes are equal, with canonical private source origins.

`installed/ledger.json` records exact isolated interpreter argv and exits. Copied installation identity was checked before mutation, its launcher rewritten to the copied prefix, and its mutations restored after each semantic run:

| Control | Exit | Intended terminal reason |
|---|---:|---|
| Extra Memory member | 1 | installed member inventory changed: friday_memory |
| Commands spec-origin substitution | 1 | module spec origin mismatch: friday_commands |
| Coherent old ordering in source and installed package | 1 | shared preview order changed |
| Coherent broad generated selection | 1 | generated scope/counts changed |
| Coherent same-total counterfeit counts | 1 | pending scope/counts changed |
| Restored Chat installation | 0 | complete installed proof passes |

Fresh copied controls exercised Chat/normal mode; its restored clean control passes. Both lanes/modes were additionally exercised clean in the own build. Full 96 supplied member/origin controls and six semantic mode cases were inspected as allowed, not represented as fresh reproduction.

## Inspected evidence, not fresh runs

`inspected-evidence-audit.json`, `receipt-inspection.json`, and `bridge-check.json` record the checks. All 221 implementation and 32 D0 embedded raw records match their recorded SHA256 and external file bytes. All 64 external-inventory entries match. All 18 source mutant receipts have stable canonical source hashes; the callback mutant requires the separate callback AssertionError supplement, whose unchanged control and call-phase witness were inspected. The original callback result alone receives no assertion credit. Both original and historical failed setup/refusal-matcher attempts remain visible and receive no credit.

The second closed replay was hash-checked rather than rebuilt. Full copied-control matrix, prebuild refusal, extra installed dependency/finance imports, baseline root Ruff/collection/format receipts and final package-byte bridge were inspected. The bridge independently compares actual Commands/Memory/Chat source members with the earlier control source: all equal. Later fixture/test packaging changes do not supply runtime mutation credit.

Synthetic v1 fixture raw bytes all match the baseline provenance after applying only the storage-filename materialization map. Generator/source-test provenance binds the old coordinator test at baseline `2b0850b...`; private fixture replay reconstructs permissions and records path/fingerprint/checksum relocation audits. Completed historical state was read through `MaintenanceArtifactStore.read_journal`; this review does **not** claim successful completed-run coordinator recovery. Interrupted v1 state underwent actual installed recovery and returned completed_with_warnings. The own installed reports include the two relocation audits (22 and 30 path changes respectively).

## Original assertions and baseline classification

AST comparison found no removed existing test function. Coordinator assertions 146→146 unchanged; mutation assertions 58→59; diagnostics 51→52; recovery 38→38. Changed assertions correspond to configuration-only verification preflight, operation cleanup, shared stage names and real rollback evidence. Fake adapters are explicitly test-only; their fabricated counts were not used as real-store proof. No new source/type suppression, skip or xfail was added.

Root Ruff **534 errors**, root pytest **test_display import-name collection conflict** (7196 collected), and seven legacy whole-file format failures remain **failed/unwaived**, supported by inspected current/baseline receipts. They do not imply this candidate introduced those failures. Original installed pilot/MEMQ oracles remain failed where they reject the approved help delta or predate accepted quote repair; separate bounded compatibility evidence does not relabel them passing. No whole-repository-green claim.

## Harness history and limits

The initial source-control harness attempt failed before tests because `/var` versus `/private/var` canonical paths disagreed and REVIEW_REPO was absent. Its local-model-map fetch attempt was blocked by the DNS guard; no external request succeeded. It earns no rejection credit. After correcting only reviewer harness environment/canonical paths, the unchanged control and all three representative mutants ran successfully as tests.

A receipt's clean-default inline command contained an indirect `/tmp/current-maint-build.txt` lookup. The driver was stopped before reaching it; that receipt was not executed. A reviewer-owned helper ran the exact test in own export instead. The interrupted driver had started the named suite; its completed duplicate receipt is retained, not counted as additional coverage. No supplied cache or output path was written.

Python audit guards are not an OS sandbox. Tests are local deterministic substitutes, not live provider or human UAT evidence. Cross-platform operation, live provider limits and personal data migrations are outside scope. Inspection of permitted receipts is explicitly weaker than reproducing their entire matrix, and is not presented otherwise.

## Integrity and handoff

Entry and exit logical index SHA256, computed from exact `git ls-files -s -z` stdout **before status**, is `91007eb0d945d316d5aecef6428f4962e84661f2866d65807346ac1ba1676dc5`. All Git processes inherit `GIT_OPTIONAL_LOCKS=0`. HEAD/branch/status/staging unchanged. Both dirty example YAMLs, `.friday-old`, exports and their required metadata remain unchanged. All 17,513 protected files and 91 personal hashes match; symlink directories and gitlink HEAD match. All authority/product/external pins remain unchanged. See `entry.json`, `pins-entry.json`, `exit-integrity.json`.

Return this review to the controller for reconciliation. It grants no acceptance, UAT completion, publication, push, merge, release or delivery authority.

## Exact fresh command receipts

The following commands and exits are the actual private-lane receipts. Companion logs are in `prepared/`; source and installed control argv are additionally retained in their ledgers. Paths are literal and reviewer-owned.

- `bounded-retained-comparison3.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands python -B -m pytest -p controls -p no:cacheprovider -q --tb=short packages/friday-chat/tests_chat/test_maintenance_order.py::test_approved_maintenance_help_delta_preserves_frozen_families --basetemp /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared/pytest-tmp/bounded-retained-comparison3
```

- `bundle.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands python -B /Users/chuckrussell/Dev/gendev/agent-framework/docs/planning/active/command-refactor/validation/pilot/harness/bundle.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/bundle /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared --revision ae15a5374350807bd909bc823078087a53a47ce4 --artifacts /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/session-build-d1-_k6hm5vb/baseline-bundle/locked-artifacts --require-pilot-edge
```

- `candidate-lock.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands uv lock --check --offline --project /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/candidate
```

- `clean-default.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands python -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/clean_default.py
```

- `d0-guard.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands python -B /Users/chuckrussell/Dev/gendev/agent-framework/docs/planning/active/command-refactor/validation/pilot/harness/guard_selftest.py
```

- `final-all-changed-lint.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands ruff check --no-cache docs/planning/active/command-refactor/validation/maintenance/installed_probe.py packages/friday-chat/src/friday_chat/adapters.py packages/friday-chat/src/friday_chat/commands/registry.py packages/friday-chat/src/friday_chat/reorganization/artifacts.py packages/friday-chat/src/friday_chat/reorganization/contracts.py packages/friday-chat/src/friday_chat/reorganization/coordinator.py packages/friday-chat/src/friday_chat/reorganization/mutation.py packages/friday-chat/src/friday_chat/runtime.py packages/friday-chat/tests_chat/test_maintenance_order.py packages/friday-chat/tests_chat/test_reorganization_coordinator.py packages/friday-chat/tests_chat/test_reorganization_mutation.py packages/friday-chat/tests_chat/test_reorganization_response_diagnostics.py packages/friday-memory/src/friday_memory/maintenance/__init__.py packages/friday-memory/src/friday_memory/maintenance/mutation.py packages/friday-memory/src/friday_memory/maintenance/pipeline.py packages/friday-memory/src/friday_memory/maintenance/provider_contracts.py packages/friday-memory/tests_memory/test_maintenance/test_pipeline.py packages/friday-memory/tests_memory/test_maintenance/test_verification_selection.py tests/integration/reorganization/test_maintenance_headless.py tests/integration/reorganization/test_reorganization_recovery.py
```

- `final-metadata.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands python -B scripts/check-package-metadata.py
```

- `final-new-format.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands ruff format --check --no-cache packages/friday-memory/src/friday_memory/maintenance/pipeline.py packages/friday-memory/src/friday_memory/maintenance/provider_contracts.py packages/friday-memory/tests_memory/test_maintenance/test_pipeline.py packages/friday-memory/tests_memory/test_maintenance/test_verification_selection.py packages/friday-chat/tests_chat/test_maintenance_order.py tests/integration/reorganization/test_maintenance_headless.py docs/planning/active/command-refactor/validation/maintenance/installed_probe.py
```

- `final-types.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands mypy --cache-dir /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/mypy packages/friday-memory/src/friday_memory/maintenance/mutation.py packages/friday-memory/src/friday_memory/maintenance/pipeline.py packages/friday-memory/src/friday_memory/maintenance/provider_contracts.py packages/friday-chat/src/friday_chat/reorganization/contracts.py packages/friday-chat/src/friday_chat/reorganization/mutation.py packages/friday-chat/src/friday_chat/reorganization/coordinator.py packages/friday-chat/src/friday_chat/reorganization/artifacts.py packages/friday-chat/src/friday_chat/commands/registry.py packages/friday-chat/src/friday_chat/adapters.py packages/friday-chat/src/friday_chat/runtime.py
```

- `freeze-board.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands python -B scripts/friday-dev-board.py validate
```

- `freeze-dashboard-check.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands python -B scripts/friday-dev-board.py render --check
```

- `freeze-docs.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands python -B scripts/check-documentation-lifecycle.py
```

- `lock.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands uv lock --check --offline --project /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source
```

- `offline-startup.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands python -B -c 'import friday_commands; print('"'"'offline editable startup passed'"'"')'
```

- `verified-full-chat.json` — exit 1:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-chat/tests_chat --ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py --basetemp /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared/pytest-tmp/verified-full-chat
```

- `verified-full-cli.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands python -B -m pytest -p no:cacheprovider -q packages/friday-cli/tests_cli --basetemp /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared/pytest-tmp/verified-full-cli
```

- `verified-full-commands.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands python -B -m pytest -p no:cacheprovider -q packages/friday-commands/tests_commands tests/integration/test_package_cohort_metadata.py --basetemp /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared/pytest-tmp/verified-full-commands
```

- `verified-full-memory.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands python -B -m pytest -p no:cacheprovider -q packages/friday-memory/tests_memory --basetemp /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared/pytest-tmp/verified-full-memory
```

- `verified-named-maintenance-2.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-memory/tests_memory/test_maintenance/test_pipeline.py packages/friday-memory/tests_memory/test_maintenance/test_verification_selection.py packages/friday-chat/tests_chat/test_maintenance_order.py tests/integration/reorganization/test_maintenance_headless.py tests/integration/reorganization/test_reorganization_recovery.py --basetemp /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared/pytest-tmp/verified-named-maintenance-2
```

- `verified-named-maintenance.json` — exit 0:

```sh
uv run --offline --frozen --no-sync --no-python-downloads --with-editable packages/friday-commands python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-memory/tests_memory/test_maintenance/test_pipeline.py packages/friday-memory/tests_memory/test_maintenance/test_verification_selection.py packages/friday-chat/tests_chat/test_maintenance_order.py tests/integration/reorganization/test_maintenance_headless.py tests/integration/reorganization/test_reorganization_recovery.py --basetemp /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared/pytest-tmp/verified-named-maintenance
```

### source-controls-r2

- control: exit 0

```sh
/Users/chuckrussell/Dev/gendev/agent-framework/.venv/bin/python -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source-controls-r2/entry.py /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source-controls-r2/control/source /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source-controls-r2/control/result.json /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source-controls-r2/control/basetemp /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared
```

- old-order: exit 1

```sh
/Users/chuckrussell/Dev/gendev/agent-framework/.venv/bin/python -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source-controls-r2/entry.py /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source-controls-r2/old-order/source /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source-controls-r2/old-order/result.json /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source-controls-r2/old-order/basetemp /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared
```

- broad-generated: exit 1

```sh
/Users/chuckrussell/Dev/gendev/agent-framework/.venv/bin/python -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source-controls-r2/entry.py /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source-controls-r2/broad-generated/source /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source-controls-r2/broad-generated/result.json /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source-controls-r2/broad-generated/basetemp /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared
```

- unsafe-default-boundary: exit 1

```sh
/Users/chuckrussell/Dev/gendev/agent-framework/.venv/bin/python -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source-controls-r2/entry.py /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source-controls-r2/unsafe-default-boundary/source /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source-controls-r2/unsafe-default-boundary/result.json /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source-controls-r2/unsafe-default-boundary/basetemp /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared
```

### installed

- neutral-False: exit 0

```sh
/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/bundle/installed-neutral/bin/python -I -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source/docs/planning/active/command-refactor/validation/maintenance/installed_probe.py --source /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source --prepared /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared --profile /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/bundle/neutral-profile.txt --report /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/installed/neutral-False/report.json --lane neutral --revision ae15a5374350807bd909bc823078087a53a47ce4
```

- neutral-True: exit 0

```sh
/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/bundle/installed-neutral/bin/python -I -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source/docs/planning/active/command-refactor/validation/maintenance/installed_probe.py --source /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source --prepared /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared --profile /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/bundle/neutral-profile.txt --report /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/installed/neutral-True/report.json --lane neutral --revision ae15a5374350807bd909bc823078087a53a47ce4
```

- chat-False: exit 0

```sh
/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/bundle/installed-chat/bin/python -I -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source/docs/planning/active/command-refactor/validation/maintenance/installed_probe.py --source /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source --prepared /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared --profile /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/bundle/default-profile.txt --report /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/installed/chat-False/report.json --lane chat --revision ae15a5374350807bd909bc823078087a53a47ce4
```

- chat-True: exit 0

```sh
/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/bundle/installed-chat/bin/python -I -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source/docs/planning/active/command-refactor/validation/maintenance/installed_probe.py --source /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source --prepared /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared --profile /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/bundle/default-profile.txt --report /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/installed/chat-True/report.json --lane chat --revision ae15a5374350807bd909bc823078087a53a47ce4
```

- member-refusal: exit 1

```sh
/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/copied-chat/bin/python -I -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source/docs/planning/active/command-refactor/validation/maintenance/installed_probe.py --source /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source --prepared /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared --profile /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/bundle/default-profile.txt --report /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/installed/member-refusal/report.json --lane chat --revision ae15a5374350807bd909bc823078087a53a47ce4
```

- origin-refusal: exit 1

```sh
/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/copied-chat/bin/python -I -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/installed/origin-hook.py --source /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source --prepared /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared --profile /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/bundle/default-profile.txt --report /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/installed/origin-refusal/report.json --lane chat --revision ae15a5374350807bd909bc823078087a53a47ce4
```

- semantic-old-order: exit 1

```sh
/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/copied-chat/bin/python -I -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source/docs/planning/active/command-refactor/validation/maintenance/installed_probe.py --source /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/semantic-old-order --prepared /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared --profile /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/bundle/default-profile.txt --report /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/installed/semantic-old-order/report.json --lane chat --revision ae15a5374350807bd909bc823078087a53a47ce4
```

- semantic-broad-generated: exit 1

```sh
/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/copied-chat/bin/python -I -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source/docs/planning/active/command-refactor/validation/maintenance/installed_probe.py --source /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/semantic-broad-generated --prepared /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared --profile /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/bundle/default-profile.txt --report /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/installed/semantic-broad-generated/report.json --lane chat --revision ae15a5374350807bd909bc823078087a53a47ce4
```

- semantic-counterfeit-counts: exit 1

```sh
/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/copied-chat/bin/python -I -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source/docs/planning/active/command-refactor/validation/maintenance/installed_probe.py --source /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/semantic-counterfeit-counts --prepared /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared --profile /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/bundle/default-profile.txt --report /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/installed/semantic-counterfeit-counts/report.json --lane chat --revision ae15a5374350807bd909bc823078087a53a47ce4
```

- restored-chat: exit 0

```sh
/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/copied-chat/bin/python -I -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source/docs/planning/active/command-refactor/validation/maintenance/installed_probe.py --source /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/source --prepared /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/prepared --profile /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/bundle/default-profile.txt --report /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-astra-review-nodsxy8l/installed/restored-chat/report.json --lane chat --revision ae15a5374350807bd909bc823078087a53a47ce4
```
