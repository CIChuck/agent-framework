# CD-CMD-MEMQ-001 — shared memory query commands

Status: **approved with the bounded [directive-correction amendment](../approval/memory-queries-directive-correction.md)**; fresh directive-readiness council pending. Owner: Chuck Russell.
Prepared 2026-11-09. Branch: `feature/command-retirement`. Unit: MEMQ-001.
Preparation under the maintainer's “proceed” instructions changes planning and
evidence only. The subsequent approval binds the exact
[contract](../memory-query-command-contract.md) and this directive before product,
test or probe implementation. The maintainer selected MQ-D3 option R and then
“The edited version”, including the record-projection/schema clarification and
completion of its evidence and hash references. His later “lets apply the
corrections and iterate” authorizes only the four findings in
[REM-CMD-MEMQ-DIR-001](../remediation/REM-CMD-MEMQ-DIR-001-readiness.md),
their exact verification and a fresh council. Product D0/D1 waits for that
readiness result; this correction does not start construction.

## Authority and execution base

Apply AGENTS and the engineering, lifecycle and independent-validation policies,
the current board and packet, then MQ-01–MQ-07 in the contract. Record the
maintainer, instruction, date and exact contract/directive/preparation digests in
a subsequent approval. That approval must explicitly cover the closed payload
expansion (MQ-01), the MQ-D1 kind refusal, the MQ-D2 argument rule, the MQ-D3
choice (with any change to the option R defaults) and the MQ-D4 export-assertion
extension. Proposal labels never replace that exact approval.

Baseline: `c5871054266da2340486d2043062c5fb95611c00`.
Only planning/approval descendants with byte-identical packages, tests, scripts,
root AGENTS/README/main/metadata and lock may precede construction. Record the
actual start HEAD and that equality. Unexpected source drift requires a
refreshed approved baseline. The initiative remains started/local; MEMQ
construction is approved only within this directive and the selected option R.

The frozen input table below is normative. The supplemental record-projection
characterization preserves the original 76-case preparation unchanged. Accepted
DIAG, SESSION and pilot
technical inputs, their raw reports/receipts and harnesses remain immutable.
Known root Ruff 534, the sole Chat/CLI `test_display` root collection conflict
(6,929 collected), and existing format debt in `memory.py`, `registry.py`,
`runtime.py` and `adapters.py` are failed/unwaived baseline debt, not passing
gates. The pinned per-file formatting inventory and comparison below classify
that debt without authorizing reformatting untouched code. No new regression
may hide behind it.

| Input relative to packet | SHA-256 |
| --- | --- |
| `memory-query-command-contract.md` | `b02ba788038618a82bf285565943b1169ae9ae6cddfe40b7681839b70d3d87e2` |
| `validation/memory-queries/record-projection-characterization.json` | `a191df967b3f84d0c3f91723e41cd45680ed84685a9f4bebf7f4f7724893009d` |
| `validation/memory-queries/preparation.json` | `e6d203a0f87c92ddd7f3e1038a53c18b59cb01cdb56e89b9a3e84c086e78b593` |
| `remediation/REM-CMD-MEMQ-DIR-001-readiness.md` | `eeaeba9e12b291d50a19e60869d66f4c10d7ea2d7dc37efb973f66df48559540` |
| `validation/memory-queries/format_debt.py` | `3ad2f9cce5439e6e29463d7e32caf11ad5750b5567a01e04315e47e735a53751` |
| `validation/memory-queries/format-baseline.json` | `7475cd9172dd566a2a4af71776eecd66f9275b239a969b1e6dc1ca2ea7ec7ad2` |
| `validation/memory-queries/verify_directive_corrections.py` | `7bd5cf6524e982093c007f0d48a4b0f76ed55370aeb9556cca57cc0d5c6a6bb9` |
| `approval/diagnostics-acceptance.md` | `1a3eecabf3b96bc456f1595933f5f2a8cba13810bb51bdb3ba6803d25e22b5ca` |
| `approval/diagnostics.md` | `8aeb991d742a38d717c49d488b34d6a5800b57fbec97b3d4a461e2027caa1cb2` |
| `approval/diagnostics-context-evaluation.md` | `6a752d7977afb5e07c5212c8b361aba63b0c680f87a738a0a9fcd8bd01ce18de` |
| `diagnostics-command-contract.md` | `14dd68f6cc2c5dfbba7f31c19305eeeec68a00598b3b1a1740806832b621be62` |
| `directives/CD-CMD-DIAG-001-context-diagnostics.md` | `1a9a506020b8d5faa0b864c053b1085e8f8c15c8feab8a4c0f59d4293677ee47` |
| `remediation/REM-CMD-DIAG-D3-001-context-evaluation-order.md` | `3078bb19195044212a115cb3f3f169d030af2b282154d4d336856b37c41fa865` |
| `validation/diagnostics/preparation.json` | `1f8ee9c7e882d0d0e857deb8489b0eeb309e0d1fa5c21ccbf40223e0886a2c55` |
| `validation/diagnostics/installed_probe.py` | `c943d7070aeae2624444a165a9c3f77f3317c062e06376b3d0f89e089d70db58` |
| `validation/diagnostics/implementation/d3/evidence.json` | `17023f2ff51ecbea68a07e7fa97f447f7b987feccfe17b1ae31947abc2a16564` |
| `validation/diagnostics/implementation/d3/correction-evidence.json` | `641d9b0d2d9cb94e409908bd94dc818718a666da2c466d4bab5ed79c0aac8db9` |
| `approval/session-acceptance.md` | `86d2642ac4aa8aeaee73fc727539ef5bb9fe87946aedca085f9db07e50a87a1c` |
| `validation/session/preparation.json` | `afa7acce7d32e4ef79947ac8db5b78593f49d1aa33b91fd028f28bcfb9205221` |
| `validation/session/installed_probe.py` | `059c1e4e392de1e00853e4acaadfe97f7a1eefe3f4d1de412ebf4970f07f15cd` |
| `approval/council-roster.md` | `80c8e25ed071503313e9b3c97d93d2fb3712d29de6822e22b539d7b3a3fa8e02` |
| `shared-command-api.md` | `e5ba883fb246967320243e1dbc9c2a70fcf6189c05540a45961388f2b6466b74` |
| `scope-decisions.md` | `6760092e9d7b4f38a0e96d8109fde0e95cd8c3db0aeaf05c927801243dccb749` |
| `command-inventory.md` | `a671de2837683cab999dcc4ad8d03f1fe0d2158ba5bcbf2de38dc9fdd5b9a8da` |
| `../../backlog/friday-tui-command-followups/README.md` | `b8021069f2752074ac7fb6a25d9d41055749b161d7cd18b0c49f14eded35daa8` |
| `validation/pilot/installed_probe.py` | `8c1233a0a5181566bb188735358141e8718a5aaba205e6c4bfa3a2620a8e43ac` |
| `validation/pilot/harness/prepare.py` | `788f6f8fbc7c4c6f1b53458632c16ecc09153c8d8604cb7ecb776dc8b3075f2e` |
| `validation/pilot/harness/bundle.py` | `46cc788e7aea59add8367de6568bae135cfd3689a813af8d530661f3267d327d` |
| `validation/pilot/baseline.json` | `48c3161cf1a0467c7e95ac11a85de0972d46421b5a9318ee618651f7cc7ad7f1` |

Preserve both dirty Chat examples unstaged with SHA-256:
`config.example.yaml`: `c2f728c98adc5ca773bfdf3170d846a610f15d77eae9a380e1a815534b93c3e7`;
`models-config.example.yaml`: `11e99116d885a431f085b6bd05b5bd30348eb37654fd4c9350a7cca58c527896`.
Do not clean caches, `.friday`, exports, stores or unrelated work. Preserve the
existing ignored `exports/` files byte/mode/time-identical.

## Exact implementation allowlist and limits

Paths are relative to repository root; no other product path may change.

| Path | Permitted change |
| --- | --- |
| `packages/friday-commands/src/friday_commands/contracts.py` | `MemoryRecordKindName` plus thirteen MQ-01 models and exactly six new union/whitelist alternatives; retain all earlier definitions/invariants. |
| `packages/friday-commands/src/friday_commands/__init__.py` | Sixteen additive exports/imports; preserve previous 38 in order/binding. |
| `packages/friday-commands/src/friday_commands/memory_queries.py` (new) | Specs, protocol and factory only. |
| `packages/friday-commands/tests_commands/test_memory_queries.py` (new) | MQ-01, MQ-02, MQ-D1, MQ-D2 neutral/standalone tests. |
| `packages/friday-commands/tests_commands/fixtures/memory-query-metadata.json` (new) | Exact preparation metadata fixture. |
| `packages/friday-commands/tests_commands/test_session_views.py` | Append only the sixteen MQ-01 names to the literal list in `test_session_specs_and_factory_are_immutable`. |
| `packages/friday-commands/tests_commands/test_diagnostics.py` | In `test_diagnostic_specs_exports_and_factory` only: insert one local `import friday_commands.memory_queries as memory_queries_module`; append sixteen names to the API literal; append thirteen MQ-01 models to the existing `contracts` owner tuple; append one final three-name `memory_queries_module` row after `shared`; change `38` to `54`. Exact names/order follow MQ-D4; every other AST statement remains unchanged. |
| `packages/friday-chat/src/friday_chat/commands/memory_queries.py` (new) | Narrow typed Chat port, metadata helper, projections, pure renderers, exact outcome adapter and once-only invocation. |
| `packages/friday-chat/src/friday_chat/commands/memory.py` | Four compatibility wrapper bodies; private formatting/query helpers may move to the new module. Public `preview_text`, `record_value` and `__all__` unchanged. |
| `packages/friday-chat/src/friday_chat/commands/registry.py` | `_entities_handler` and `_list_ingested_handler` wrapper bodies, imports, metadata helper and only tuple entries 3, 9, 10, 11, 12, 16; an import made unused may be removed. All other AST/order/handler-map definitions unchanged. |
| `packages/friday-chat/tests_chat/test_command_memory_queries.py` (new) | MQ-03–MQ-07 compatibility, dispatch, failure, synthetic app tests; option R repair tests. |
| `packages/friday-chat/tests_chat/fixtures/memory-query-baseline.json` (new) | Exact preparation metadata/cases fixture. |
| Both package `README.md` files | Describe memory queries, shared/host ownership, read-only effects, explicit type boundaries and the MQ-D3 outcome. |
| **Option R only:** `packages/friday-chat/src/friday_chat/memory_views.py` | Add `IngestedDocumentView` and `IngestedDocumentQueryResult` and their `__all__` entries only. |
| **Option R only:** `packages/friday-chat/src/friday_chat/runtime.py` | Add `query_ingested_documents` to the `MemoryController` protocol and `FakeMemoryController` only. |
| **Option R only:** `packages/friday-chat/src/friday_chat/adapters.py` | Add `FrameworkMemoryAdapter.query_ingested_documents` and one private projection helper only, using the existing public `collection_manager.short_term/long_term.get_all`. |
| Current packet, board/dashboard, log/authority, `validation/memory-queries/`, PAR evidence | Bounded status, preservation, review, receipts and a new D3 installed probe only. |

That is fifteen package paths under option P and eighteen under option R. Every
other existing source/test/fixture keeps its bytes. Do not add skips/xfails or
change old test bodies, parameters, decorators or assertions beyond the two
named MQ-D4 extensions.

No metadata/dependency/lock/config change. No `friday-memory`, `friday-runtime`,
`friday-cli` or other framework package change. No change to `/ingest`, its
chunk metadata, storage, protection or promotion; no `/reset`, maintenance,
reorganization, synthesis, telemetry, transcript writing or turn-processing
change. No new parser, dependency, service locator, `Any`, casts, suppressions,
retry, rollback, progress/confirmation, pagination, consolidation (C-01),
source validation (CMD-F05), renaming or TUI work. If an approved change cannot
be made within these paths, stop for a bounded decision.

## Deliverables and review gates

| Deliverable | Required result before advancement |
| --- | --- |
| D1 / D0–D1 | D0 baselines, inventories and guard controls; approved neutral models/API/specs/handlers, exact fixture and tests. Full Commands/cohort passes, including both MQ-D4 extended assertions. Fresh D1 council reconciled before D2. |
| D2 / D2–D3 | Typed Chat port/wrappers/projection/rendering, exact fixture, once-only ownership, source observations, synthetic app tests and the approved MQ-D3 option. Fresh D2 council reconciled before D3. |
| D3 / D4–D5 | Full owning regressions/preservation, candidate builds and isolated installed proof; fresh D3 plus complete bounded MEMQ aggregate review, then human acceptance. |

Use only **GPT-6.1 Sol/high, GPT-6 Astra/high and Claude Opus 5.5/high**, per the
[roster](../approval/council-roster.md). Every review has fresh context, a
read-only frozen candidate, private external caches/output, no builder
reasoning and no nested delegation. Measure the logical index before status
using exact `git ls-files -s -z` stdout, with `GIT_OPTIONAL_LOCKS=0` inherited by
every Git child. Verify request, authority, source/deliverable/protected/dirty
pins and identity at start and end. A cache write to supplied evidence
invalidates that review. A seat whose session built or remediated the reviewed
work must be a fresh context.

Reconcile all mandatory findings rather than majority-voting or using scores as
approval. A changed candidate gets a fresh delta plus bounded aggregate review.
Escalate after two unsuccessful remediation cycles under policy. No acceptance,
next family or delivery follows from VERIFIED automatically.

## Required test nodes and evidence

Missing nodes or partial assertions fail their gate. Equivalent parametrization
is allowed without replacing these node names. Async tests have explicit
`@pytest.mark.asyncio`; no skips/xfails. Use event-controlled bounded awaits with
cleanup, never timing sleeps. Product invariants use exceptions, not asserts.

| ID / node in new neutral test | Mandatory assertions |
| --- | --- |
| MQ-T01 `test_memory_query_models_and_closed_union` | Every field in declaration order; metric state/value/reason invariants; exact completion bool; required meta id/collection versus absent plain-record metadata; literals; optional/str-subclass/Unicode values; exact nested/payload types and subclasses; once-only immutable snapshots; ≤100 limits; empty/ordered/duplicate values; bool-vs-str; all old alternatives/invariants retained. |
| MQ-T02 `test_memory_query_specs_exports_and_factory` | Exact ordered 54-name API, no duplicates/extra/missing/reordered names; all bindings; six specs with all metadata/detail/argument fields equal to the package fixture; fresh immutable six-key maps; zero construction reads; empty registry; structural protocol. |
| MQ-T03 `test_memory_query_invocation_validation_order` | All six: exact request, then execution, then name before any port access; execution/spec unused; direct non-string args fail at request construction (MQ-D2); string subclasses accepted. |
| MQ-T04 `test_memory_query_availability_and_single_await` | One exact-bool availability call first; False returns unavailable data with no other call for every args shape; exactly one awaited capability per command; pending state; invalid result types; exception/cancellation identity; no retry/other effects. |
| MQ-T05 `test_record_kind_and_graph_selection` | Fixed kinds; MQ-D1 refusal for mismatched records/failure kinds; entities exact first-argument `nodes`, `NODES`/other names, one-space join without quote processing, `include_relationships`, nodes-only refusal when relationships are returned. |
| MQ-T06 `test_memory_queries_standalone` | Explicit neutral registry dispatch of all six under normal/`-O`/`-OO`; valid and invalid boundaries active; stdlib/own-package-only loaded closure. Preload the pinned guard explicitly if `-I` ignores PYTHONPATH. |

| ID / node in new Chat test | Mandatory assertions |
| --- | --- |
| MQ-T07 `test_memory_query_metadata_and_frozen_cases` | Exact package fixture identity, 41/3 registry and six metadata records; all 76 rows under the approved decisions (74 exact + 2 MQ-D1 refusals, or 68 + 2 + 6 superseded under option R); unchanged pilot/SESSION/DIAG observations; package-local fixture lookup only. |
| MQ-T08 `test_memory_query_once_only_delegation` | All six: one parse/factory/await, fixed spec identity, original parsed args; direct wrappers do not parse; port construction does no context reads; differing context registry, renamed wrappers and custom handlers authoritative. Inject distinct valid typed outcomes for all six and assert Chat consumes them with no legacy recomputation. |
| MQ-T09 `test_memory_statistics_projection_order_and_failures` | Exact read/await order; store and transcript `Exception` conversion with warnings; cancellation identity; budget/session absence; zero vs unavailable vs not configured; bool/float/str formatting once; utilization suffix; 256 preview; unique sorted warnings. |
| MQ-T10 `test_memory_record_projection_and_rendering` | All three kinds: empty complete/incomplete (both meta messages, including incomplete with no warning members), populated, 100-record cap, preview 160/80 exactly once, no unused plain-record metadata reads/formatting, full and sparse meta fields, traced verification-before-text-before-ISO-before-confidence order with repeated accesses, stateful/raising float/datetime/string values, None versus present-empty facts, original concatenation behavior, decayed-policy line, query failure message and cancellation identity. Renderers do not preview/format original objects again. |
| MQ-T11 `test_entities_projection_and_rendering` | Read order, nodes-only skip, projection only after both awaits, `record_value` fallbacks, `0`/`False` shown and None omitted, 100 caps, blank separator, `No entities found.`, failure/cancellation identity, non-mapping `AttributeError` after both reads. |
| MQ-T12 `test_memory_query_adapter_refusals_and_purity` | Exactly six allowed data/no-error/no-effect shapes; all other types/subclasses/errors/effects rejected; pure renderers; no second service call; exact result defaults; no trailing newline. |
| MQ-T13 `test_memory_query_real_app_sequence` | Real synthetic app: a conversational turn, all six commands, `/ingest` then `/list-ingested`, `/history`, `/clear`, `/cls`, `/q`; output, lifecycle and cleanup order; no network/providers/real user stores. |
| MQ-T14 (option R) `test_ingested_listing_reads_persisted_metadata` | Real `FrameworkMemoryAdapter` over a fresh `tmp_path` store: `/ingest` single- and multi-chunk files, re-ingest, promotion to long-term, then `/list-ingested` lists persisted sources with grouping/count/order per the approved defaults; malformed records and per-collection failures warn; cancellation propagates; the decayed collection and source files are not read; fake listing unchanged. |
| MQ-T14 (option P) `test_list_ingested_preserves_getattr_listing` | Exact current getattr fallback, falsy/tuple/missing-key behavior and the documented production limitation; no new protocol method. |

In private source copies, prove the new tests reject these changes with named
**test-call assertion failures**, not import/setup errors:
- extra, dropped, reordered or duplicate exports;
- an eager-reading factory;
- usage or kind selection before the runtime check;
- double or unawaited queries;
- a missing MQ-D1 refusal;
- case-insensitive `nodes`;
- relationships queried for nodes-only;
- projection before the second graph await;
- warning dedupe/sort drift;
- `0` shown as unavailable;
- a missing utilization `%`;
- record or entity cap drift;
- double formatting;
- an ignored injected result;
- legacy engine substitution;
- under option R, reading the decayed collection, wrong grouping/order and swallowed cancellation.

Run an unchanged control through the same harness. Record canonical module
roots and hashes before pytest, at session finish and afterwards; resolve macOS
`/var` aliases on both sides. Never mutate supplied source or environment.

## D0 — reproducible guarded preparation

Only after approval, reproduce current behavior and inventory before any source
edits. Use Python 3.13.10 and the existing uv-managed frozen environment; no
sync/upgrade or downloaded Python. From repository root in zsh:

```sh
export GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1
MEMQ_PYTHON="$PWD/.venv/bin/python"
MEMQ_HARNESS="$PWD/docs/planning/active/command-refactor/validation/pilot/harness"
MEMQ_SCRATCH="$(mktemp -d /tmp/friday-memq-build.XXXXXX)"
export MEMQ_PYTHON MEMQ_HARNESS MEMQ_SCRATCH
# MEMQ_WHEELHOUSE is the supplied eight-wheel directory, verified by prepare.py.
"$MEMQ_PYTHON" -B "$MEMQ_HARNESS/prepare.py" "$MEMQ_SCRATCH/prepared" --wheelhouse "$MEMQ_WHEELHOUSE"
MEMQ_RUNNER="$MEMQ_SCRATCH/prepared/pilot_run.py"
export MEMQ_RUNNER
"$MEMQ_PYTHON" -B "$MEMQ_RUNNER" guard python -B "$MEMQ_HARNESS/guard_selftest.py"
```

Materialize the preparation's exact programs and baseline into scratch, after
verifying the preparation digest. Refuse overwrite and verify every text hash:

```sh
"$MEMQ_PYTHON" -B - <<'PY'
import hashlib, json, os
from pathlib import Path
p=Path('docs/planning/active/command-refactor/validation/memory-queries/preparation.json')
if hashlib.sha256(p.read_bytes()).hexdigest() != 'e6d203a0f87c92ddd7f3e1038a53c18b59cb01cdb56e89b9a3e84c086e78b593':
    raise RuntimeError('Preparation changed')
d=json.loads(p.read_text()); out=Path(os.environ['MEMQ_SCRATCH'])
for name, entry in [('capture_memq.py',d['programs']['capture']),
                    ('compare_memq.py',d['programs']['comparison']),
                    ('frozen-memq.json',d['baseline'])]:
    raw=entry['text'].encode(); target=out/name
    if hashlib.sha256(raw).hexdigest()!=entry['sha256'] or target.exists():
        raise RuntimeError('Invalid identity or overwrite: '+name)
    target.write_bytes(raw)
PY
"$MEMQ_PYTHON" -B "$MEMQ_RUNNER" comparator python -B "$MEMQ_SCRATCH/compare_memq.py" --selftest
```

Export committed clean inputs and run the source capture. Receipt labels and
output filenames must differ. At D0:

```sh
MEMQ_REVISION=c5871054266da2340486d2043062c5fb95611c00
MEMQ_PHASE=before
MEMQ_SOURCE="$MEMQ_SCRATCH/$MEMQ_PHASE-source"
export MEMQ_REVISION MEMQ_PHASE MEMQ_SOURCE
mkdir "$MEMQ_SOURCE"
git archive --format=tar --output "$MEMQ_SCRATCH/$MEMQ_PHASE.tar" "$MEMQ_REVISION"
tar -xf "$MEMQ_SCRATCH/$MEMQ_PHASE.tar" -C "$MEMQ_SOURCE"
"$MEMQ_PYTHON" -B "$MEMQ_RUNNER" "$MEMQ_PHASE-memq-capture" python -B "$MEMQ_SCRATCH/capture_memq.py" "$MEMQ_SOURCE" "$MEMQ_SCRATCH/$MEMQ_PHASE-observations.json" "$MEMQ_REVISION"
"$MEMQ_PYTHON" -B "$MEMQ_RUNNER" "$MEMQ_PHASE-memq-compare" python -B "$MEMQ_SCRATCH/compare_memq.py" "$MEMQ_SCRATCH/frozen-memq.json" "$MEMQ_SCRATCH/$MEMQ_PHASE-observations.json" ce5da59c62ce761354b2977fcb0c3f5816a858c7e22d4873ae60e4d2613db6b9 eafcfcbc45e04a11cd04bfc8203d7e4e953f1cc7a5be85b9ca9b2e1d113f0f8a
```

At D2/D4 use an actual committed candidate revision and fresh output paths,
adding `--allow-declared-kind-refusal`, and `--allow-approved-ingested-repair`
only when option R is approved. Report **74 exact + 2 declared refusals** (P) or
**68 exact + 2 declared refusals + 6 repair-superseded rows** (R), never 76
unchanged rows. The comparer forbids any other event/type/value drift. Repeat
the capture and comparison. Capture validates every package `src` file against
Git before imports, plus file/path origins against the export roots. Reproduce
its extra-source and changed-byte refusals before imports; failed setup earns
no credit.

Also materialize the unchanged DIAG, SESSION and pilot capture/comparers from
their pinned preparations into private outputs with distinct labels:
- **DIAG:** reproduce 68 exact rows plus 4 approved cache refusals, using `--allow-declared-cache-refusal`.
- **SESSION:** reproduce all 25 rows.
- **Pilot:** reproduce all 196 observations, using `--baseline-sha256 48c3161cf1a0467c7e95ac11a85de0972d46421b5a9318ee618651f7cc7ad7f1`.

Use no provider, store or network credentials and no real user data.

## D1–D4 — tests, static checks and preservation

Materialize both new package fixtures from preparation `fixtures.*.text` at their
exact target paths, checking the embedded digests. No new test reads this active
planning packet. Record the original file/test/assertion inventory before edits.
- **AST audits:**
  - The two old tests must equal the baseline with only their exact MQ-D4 extensions removed. For the diagnostic test, remove the one local `memory_queries_module` import, sixteen appended API names, thirteen appended `contracts` owner names, final three-name owner row and the 38-to-54 count change. For the SESSION test, remove only the sixteen API names. Require exact ordered 54 bindings before reversal, and reject any other statement or assertion change.
  - The contracts AST differs only by the MQ-01 alias, models and six union/whitelist members.
  - Registry parser/register/dispatch/admission/handler-map and the other 33 tuple entries stay AST-identical.
- **Option R:** the `memory_views`, `runtime` and `adapters` changes are only the named additions; every other definition is unchanged.
- **Old tests:** retain all old test definitions and assertion counts.

Fast gate commands, with runner-owned basetemps/caches:

```sh
"$MEMQ_PYTHON" -B "$MEMQ_RUNNER" d1 python -B -m pytest -p no:cacheprovider -q packages/friday-commands/tests_commands tests/integration/test_package_cohort_metadata.py
"$MEMQ_PYTHON" -B "$MEMQ_RUNNER" d2 python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-chat/tests_chat/test_command_memory_queries.py packages/friday-chat/tests_chat/test_memory_diagnostics_commands.py packages/friday-chat/tests_chat/test_session_memory_commands.py packages/friday-chat/tests_chat/test_files_replay_shell.py packages/friday-chat/tests_chat/test_command_registry.py packages/friday-chat/tests_chat/test_command_foundations.py packages/friday-chat/tests_chat/test_command_retirements.py packages/friday-chat/tests_chat/test_command_pilot.py packages/friday-chat/tests_chat/test_command_session_views.py packages/friday-chat/tests_chat/test_command_diagnostics.py
"$MEMQ_PYTHON" -B "$MEMQ_RUNNER" d3 python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-chat/tests_chat/test_command_memory_queries.py packages/friday-chat/tests_chat/test_command_production_adapters.py packages/friday-chat/tests_chat/test_background_work.py packages/friday-chat/tests_chat/test_command_disposable_uat.py packages/friday-chat/tests_chat/test_app_lifecycle.py packages/friday-chat/tests_chat/test_display.py
```

At D4 run the entire owning suites separately, not root discovery as their proxy:

```sh
"$MEMQ_PYTHON" -B "$MEMQ_RUNNER" full-chat python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-chat/tests_chat --ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py
"$MEMQ_PYTHON" -B "$MEMQ_RUNNER" full-commands python -B -m pytest -p no:cacheprovider -q packages/friday-commands/tests_commands tests/integration/test_package_cohort_metadata.py
"$MEMQ_PYTHON" -B "$MEMQ_RUNNER" full-cli python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-cli/tests_cli
"$MEMQ_PYTHON" -B "$MEMQ_RUNNER" lint ruff check --no-cache packages/friday-commands/src packages/friday-commands/tests_commands packages/friday-chat/src/friday_chat/commands/memory.py packages/friday-chat/src/friday_chat/commands/memory_queries.py packages/friday-chat/src/friday_chat/commands/registry.py packages/friday-chat/tests_chat/test_command_memory_queries.py docs/planning/active/command-refactor/validation/memory-queries/installed_probe.py
"$MEMQ_PYTHON" -B "$MEMQ_RUNNER" types mypy --cache-dir "$MEMQ_SCRATCH/mypy" packages/friday-commands/src packages/friday-chat/src/friday_chat/commands/memory.py packages/friday-chat/src/friday_chat/commands/memory_queries.py packages/friday-chat/src/friday_chat/commands/registry.py packages/friday-chat/src/friday_chat/commands/diagnostics.py packages/friday-chat/src/friday_chat/commands/session_views.py
```

Under option R, add `memory_views.py`, `runtime.py` and `adapters.py` to the
lint and type gates, recording any pre-existing findings in those whole files
separately from new ones. At earlier gates omit only not-yet-created paths,
recording that bounded scope; never count missing files as passes. Run changed-
Python `ruff format --check --no-cache`. New Python files must pass completely.
For the five existing files in the pinned `format-baseline.json`, preserve the
raw failed/unwaived format result and additionally require the pinned
`format_debt.py check` gate below: no new owner-bound formatting fragments,
including multiplicity, beyond the baseline inventory. Removing baseline debt
is not required and never authorizes edits outside the path/definition allowlist.
Existing baseline fragments may remain only at their original lexical owner;
line-number shifts alone do not create new debt. Do not reformat untouched code
or treat the comparison pass as a whole-file formatting pass. Formatter version
and configuration must match. Other changed existing Python files have no
format-debt allowance and must pass completely. Before counts are Chat 1,338, Commands/cohort 498 and
CLI 155; reconcile actual new cases, collection, skips and exits. Reproduce and
record root Ruff and root pytest through the guarded runner (`-p controls
-p no:cacheprovider`), plus root `--collect-only` at D4. Run metadata,
`uv lock --check --offline` in the clean export, board validate/render
`--check`, documentation lifecycle and `git diff --check` over the worktree and
complete unit range. Tests and static controls run on actual current source with
canonical origins, not stale exports.

### Exact baseline-format comparison

At D0, reproduce the pinned inventory from the unchanged baseline in fresh
scratch. Compare its JSON bytes with the pinned file (same Ruff version/config,
source hashes, owner-bound fragments and full diagnostic diffs). A mismatch
stops for reconciliation, not a larger debt allowance. `record` refuses overwrite.
For current candidates run `check`; it reads source and writes no product files:

```sh
MEMQ_FORMAT="$PWD/docs/planning/active/command-refactor/validation/memory-queries/format_debt.py"
MEMQ_FORMAT_BASE="$PWD/docs/planning/active/command-refactor/validation/memory-queries/format-baseline.json"
"$MEMQ_PYTHON" -B "$MEMQ_RUNNER" format-baseline python -B "$MEMQ_FORMAT" record "$MEMQ_SOURCE" "$MEMQ_SCRATCH/format-baseline.json"
"$MEMQ_PYTHON" -I -B - "$MEMQ_FORMAT_BASE" "$MEMQ_SCRATCH/format-baseline.json" <<'PYFMT'
import sys
from pathlib import Path
if Path(sys.argv[1]).read_bytes() != Path(sys.argv[2]).read_bytes():
    raise SystemExit('Baseline format inventory changed')
PYFMT
"$MEMQ_PYTHON" -B "$MEMQ_RUNNER" format-current python -B "$MEMQ_FORMAT" check "$PWD" "$MEMQ_FORMAT_BASE"
```

Use the D0 baseline `MEMQ_SOURCE` for recording, before changing it to a candidate.
The comparison uses exact deleted/inserted text and lexical owners, without line
numbers/context; it counts duplicate fragments and rejects new ones. New code
must be formatted even if an old identical fragment exists elsewhere. Preserve
untouched definitions/bytes in the independent AST/allowlist audit. Correction
controls cover unchanged debt, shifted line numbers, an injected new defect and
a behavior-changing AST edit; they do not replace future implementation tests.

## D5 — clean artifacts and actual installed behavior

Use the pinned `bundle.py`, exact 3.13.10 interpreter, eight pinned build tools
and 125 lock-verified artifacts. At D0 perform one baseline closed trial; at D5
build and replay a committed candidate in separate empty directories:

```sh
"$MEMQ_PYTHON" -B "$MEMQ_HARNESS/bundle.py" "$MEMQ_SOURCE" "$MEMQ_SCRATCH/baseline-bundle" "$MEMQ_SCRATCH/prepared" --revision "$MEMQ_REVISION" --artifacts "$MEMQ_LOCKED_ARTIFACTS" --require-pilot-edge
# Set MEMQ_SOURCE and MEMQ_REVISION to an actual committed candidate for D5:
"$MEMQ_PYTHON" -B "$MEMQ_HARNESS/bundle.py" "$MEMQ_SOURCE" "$MEMQ_SCRATCH/candidate-bundle" "$MEMQ_SCRATCH/prepared" --revision "$MEMQ_REVISION" --artifacts "$MEMQ_LOCKED_ARTIFACTS" --require-pilot-edge
"$MEMQ_PYTHON" -B "$MEMQ_HARNESS/bundle.py" "$MEMQ_SOURCE" "$MEMQ_SCRATCH/candidate-replay" "$MEMQ_SCRATCH/prepared" --revision "$MEMQ_REVISION" --artifacts "$MEMQ_LOCKED_ARTIFACTS" --require-pilot-edge
```

`MEMQ_LOCKED_ARTIFACTS` is a supplied closed raw-artifact directory verified by
the helper. No fetch/network permission is added; missing exact inputs stop the
gate for a bounded maintainer decision. All child builds, resolves and installs
stay offline/no-index/frozen/private-cache. An injected extra source/data file
must be refused **before any build or fetch**. Both actual artifact/profile hash
maps must agree. Neutral closure is exactly one dependency-free distribution
with no entry point; the Chat closure is exactly the accepted 138-name/version
map (from pinned DIAG D3 evidence), with no new extras or executable. Both pip
checks, the finance/tools imports and the lock/artifact checks pass.

Implement `validation/memory-queries/installed_probe.py` only at D3. Define and
record its exact CLI before running both installed interpreters with `-I -B` and
`-I -B -O`, with no repository/PYTHONPATH source injection. Load and hash the
pinned guard explicitly; record report paths, exact source/probe/artifact
revisions, child commands/exits and parent and entry-point-child origins. Final
probe/product bytes must equal the artifact-source commit; later commits may
change evidence/status only. Reuse the accepted complete member/type/directory/
byte/executable and origin check helpers through hash-verified read-only copies;
bind every Commands/Chat module to its inventoried distribution root; an
in-prefix shadow must be refused.

Run unchanged pilot installed proof on candidate artifacts. The DIAG and SESSION
probes' exact 38/24-name assertions are intentionally obsolete for the approved
54-name expansion: preserve their files and do not claim they passed. In the new
probe, copy exactly these pinned function bodies as named retained checks:

| Behavior | Frozen source function | Only permitted body/identity transform |
| --- | --- | --- |
| SESSION neutral | `validation/diagnostics/installed_probe.py::retained_session_neutral_behavior` | Rename to `retained_memq_session_neutral_behavior`; append the sixteen MQ-01 names to its existing ordered **38-name** `expected_exports` list, yielding the exact API54. |
| SESSION Chat | `validation/session/installed_probe.py::chat_behavior` | Rename to `retained_memq_session_chat_behavior`; no body changes. |
| DIAG neutral | `validation/diagnostics/installed_probe.py::neutral_diagnostics` | Rename to `retained_memq_neutral_diagnostics`; no body changes. |
| DIAG Chat | `validation/diagnostics/installed_probe.py::chat_diagnostics` | Rename to `retained_memq_chat_diagnostics`; no body changes. |

The original SESSION `neutral_behavior` (24 names) is **not** the copy source.
Retain required helpers/imports/fixture globals as separately inventoried glue,
without modifying copied behavioral statements. AST-audit each named function
against its exact pinned source after reversing only the tabled rename and,
for the SESSION neutral function only, the sixteen appended names. Dry-check
the exact ordered 54 names and reject any additional behavioral AST edit.
Run all four retained behavior checks in normal and optimized installed modes.
Never spoof `api.__all__`, monkeypatch an old gate or weaken exactness.

New installed MEMQ proof requires:
- model/factory/strict/optimized neutral checks;
- all six actual canonical delegations, with exact metadata, help and args, and real outcome consumption;
- distinct injected typed results for all six, to reject a shadow engine;
- per-dispatch factory/handler counts;
- custom and renamed wrappers;
- availability precedence, the MQ-D1 refusal and nodes-only selection;
- pending/error/cancel propagation, and no unrequested effects.

Under option R, also run `/ingest` then `/list-ingested` on the installed app
against a fresh scratch store. A source-only capture is not installed execution
proof. The guarded entry-point `--help` must pass. For each private copied
installation, prove copied roots, mutate only that copy, require the exact
refusal reason for the accepted control families, and re-run restored clean
probes. Setup/import/report-collision failures earn no credit.

## Freeze, reporting and stop

Each D1/D2/D3 candidate is committed locally and frozen before its council.
Report authority/path/pin/branch/base/range, exact checks, actual exits/counts,
preservation/AST evidence, test coverage, origin checks, environment and all raw
receipts. Keep embedded text/hash and raw-file hashes equal. Label earlier failed
attempts and inspected historical evidence separately; never overwrite accepted
reports or transcribe their scores as correctness evidence.

Keep the current packet/index/tactical/next-phase/log/authority/board/dashboard
in agreement at every gate (`execution_phase`, `validation_state`, next action,
review roster, acceptance pending). The execution log is append-only. Only the
six MEMQ PAR rows gain bounded evidence; CMD-F05 is updated only to record the
MQ-D3 outcome; no generic P0/P1 closure. At final VERIFIED prepare a concrete
bounded acceptance handoff with UAT steps and stop for the maintainer.

Stop for:
- a missing exact approval, input or guard;
- drift in protected, frozen or source pins, or in the dirty bytes;
- an unexpected path, dependency or type-policy change;
- a new failing check or lost collection;
- a legacy boundary tighter than MQ-D1/MQ-D2;
- lost await, read-order or failure-conversion behavior;
- a duplicate engine;
- a need for framework-package or `/ingest` changes;
- mismatched artifacts or probe source;
- an incomplete council.

No push, PR, merge, release, next family or TUI follows automatically.
