# VAL-008 — Independent MCP-WS-03 Work-Unit Aggregate Review

Overall outcome: **CHANGES_REQUESTED**

One medium mandatory conformance finding remains: public runtime collision diagnostics omit the required source identities and provider labels. Collision prevention, registry ownership, admission, routing, sanitation and local lifecycle checks otherwise have supporting evidence. The declared compatibility/type-check failures reproduced on unchanged predecessor inputs and are separated below; they are not the reason for this outcome.

## Reviewer and independence

Reviewer: fresh-context Codex validation agent `/root/val_008_independent_review`, GPT-6 family; exact deployment version unavailable. Date: 2026-09-28. Review mode: `work_unit_aggregate`, read-only.

This agent received the committed request and explicit read-only task in a fresh context. It did not inherit or inspect parent/controller/builder/remediator sessions or private reasoning. No further agents were spawned. The implementation report was inspected as candidate documentation, and its claims were assessed against source and independently executed checks; its conclusions were not adopted as evidence.

No governed source, tests, reports, authority, process metadata or board files were edited, staged or committed. No branch cleanup, credential inspection, live endpoint, model/provider call, network request, delivery action or external effect occurred. Additional files and predecessor extracts were written only under `/private/tmp`. All synthetic tasks and subprocesses were settled in `finally`, including failing scratch assertions. Production cleanup budgets were unchanged.

## Frozen inputs and complete scope

| Input | Revision or value |
| --- | --- |
| Request/mapping revision and initial/final HEAD | `b8e1f041695b94303517617362f590ef3272e0cc` |
| Request path | `docs/planning/blocked/friday-mcp/validation/VAL-008-request.yaml` |
| Request SHA-256, start and closeout | `43fb708815e569dbe3d8b0a443ec28bf782e5b5ff2db75fb0be5d4dd2d139cfc` |
| Original request-addition revision | `1070cc2` |
| Candidate and authority revision | `397caa9898612cd989f6404951b3e1f5005dfac2` |
| Work-unit base | `2c0d6bd1fe481fff9bb180f9e6dfb4a9a2131641` |
| Approval/start revision | `b54069654bb3e21a6265fbabcd23f6991e286ab0` |
| Accepted WS-02 product predecessor | `a257f041d1d68f8aea2f5b9773df1b88acd82379` |
| Aggregate diff | `2c0d6bd1fe481fff9bb180f9e6dfb4a9a2131641..397caa9898612cd989f6404951b3e1f5005dfac2` |
| Implementation diff | `b54069654bb3e21a6265fbabcd23f6991e286ab0..397caa9898612cd989f6404951b3e1f5005dfac2` |
| Branch, unchanged | `feature/friday-mcp-ws03-registry` |

AGENTS.md and all twenty authority documents were read completely from the pinned candidate revision. Both complete requested diffs were inspected, including every source/test/fixture/report addition and approval/process change. The original active packet paths were used for `git show`; only working-file hash checks used the request's active-to-blocked relocation mapping.

The implementation diff contains exactly seven approved source paths, eight of the nine allowed test/fixture paths, and one report: sixteen paths within the seventeen-path allowlist. `test_mcp_runtime_lifecycle.py` is unchanged. The aggregate adds eight approval/process paths; the approval diff changes status/start evidence rather than reconciled behavioral requirements. WS-03 directive content at approval/start revision hashes to the same pinned SHA-256.

The seven source paths are core `mcp.py`, MCP `client/adapter.py`, and runtime `mcp_registration.py`, `mcp_loading.py`, `di.py`, `tool_loading.py`, and `kernel.py`. The eight changed tests/fixtures are core `test_mcp_contracts.py`, MCP `client/test_adapter.py`, runtime `test_di.py`, `test_kernel.py`, `test_mcp_loading.py`, `test_mcp_registration.py`, and integration `mcp_fake_server.py`, `test_mcp_registry.py`. The report is `execution/WS-03-implementation-report.md`.

Candidate-to-HEAD changes are controller request/status/backlink/board/dashboard metadata plus the disclosed mechanical packet relocation. Rename-aware inspection shows unchanged authority/report content. Current board condition remains the historical fresh-agent capacity block; this fresh review encountered no capacity or infrastructure blocker. The reviewer did not change that process state.

## F-001 — Medium: Collision diagnostics do not identify the colliding sources

**Affected source:** `packages/friday-runtime/src/friday_runtime/mcp_registration.py:95-102`, `:375-406`; public propagation at `packages/friday-runtime/src/friday_runtime/mcp_loading.py:144-152`.

**Authority:** approved WS-03 directive, MCP-03-02, lines 123-128: preflight peer/native collisions before filters or insertion, with diagnostics using canonical names, configured safe server IDs, **provider labels, counts and bounded shape/fingerprints for untrusted original names**. MCP-03-AC-02, lines 286-287, requires safe source diagnostics. Accepted core naming behavior at `friday_core/mcp.py:291-325` already demonstrates bounded both-source diagnostics without printing original names.

**Observed behavior:** runtime preflight stores only a set of canonical names. On collision it appends one decision for the second contender and raises a static error. `MCPRegistrationDecision` has only canonical name, server ID, reason and code; it cannot carry both source descriptors or distinguish a native registry contender from another MCP contender. Cleanup then clears the prepared handoff, so the public diagnostic cannot recover the missing first-source identity after failure.

Independent real public `RuntimeKernel.start()` reproductions used:

1. Optional peer `peer`, selected mode, two eligible originals `Read.File` and `Read-File`, both normalizing to `mcp_peer_read_file`.
2. Optional peer `peer`, selected mode, original `Read.File`, with a native registry entry already named `mcp_peer_read_file`.

Both returned exactly:

```text
MCP registration failed (name_collision); inspect mcp_provider.registration_decisions
(MCPRegistrationDecision(canonical_name='mcp_peer_read_file', server_id='peer', reason='rejected', code='name_collision'),)
```

The two public decision tuples are identical. Neither contains first/second identity, MCP/native provider labels, or bounded original-name shape/fingerprint. The MCP/MCP case reports discovered=2, rejected=1; the MCP/native case reports discovered=1, rejected=1. These aggregate counts do not supply the missing collision-source information. This finding concerns the expressly required diagnostic contract; the probes confirmed startup abort, no MCP insertion, native preservation and client/process cleanup.

**Reproduction command:**

```text
LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run python /private/tmp/val008-collision-repro.py > /private/tmp/val008-checks/collision-repro.log 2>&1
```

Exit 1 at the requirement assertion that peer/peer and peer/native source decisions differ. Both subprocesses were already reaped, both pipes reached EOF, and no synthetic task remained before that assertion. The log prints `all_synthetic_tasks_and_processes_settled=True`. The failure is a candidate conformance reproduction, separate from the intentionally corrected harness issues described below.

**Risk:** callers can identify the canonical conflict but cannot determine the actual colliding source pair or provider kind from the approved public diagnostic. Different lossy original names on the same server remain indistinguishable, frustrating diagnosis without raw catalog recovery. This loses a previously approved safe diagnostic capability.

**Required mitigation:** preserve typed bounded descriptors for both contenders during preflight. Identify MCP/native provider kind and safe configured server IDs; identify untrusted original names using bounded shape/length/name fingerprints, without echoing raw names or peer errors. Publish that collision evidence through a documented public typed diagnostic surface and retain it after failure cleanup. Keep pre-filter failure, no overwrite, native preservation, static errors and existing ownership behavior. Do not reach into native registry private fields or expand core/native mandatory protocols. Reconcile diagnostic counter semantics for fatal preflight in the report without inventing an additional counter requirement.

**Required verification:** unit and real public-runtime cases for distinct lossy originals on one peer, cross-peer canonical ambiguity, MCP/native collisions, exclusions/zero selected mode, bounded oversized originals, and sentinel-free errors/repr/logs. Assert both source descriptors remain publicly inspectable after cleanup, as well as native preservation and complete synthetic cleanup. Obtain a newly frozen candidate and fresh independent review under bounded remediation authority.

**Documentation/config impact:** document the additive typed collision diagnostic and its retention/counter semantics in the implementation report, update criterion evidence, and preserve the external-content/privacy limits. No config schema, defaults, dependency, live-provider or later-slice change is needed.

No other numbered candidate finding was established.

## Evidence for all ten mandatory criteria

| Criterion | Independent assessment and evidence |
| --- | --- |
| MCP-03-AC-01 | Supported. `mcp_registration.py:388-390` reuses the accepted normalizer; core normalizer source is unchanged. `adapter.py:77-102`, `:143-148` uses canonical metadata and exact original execution name. Core/adapter/focused suites pass. Independent real registry callables routed `Read.File` on peers `one` and `two` to the correct peer with exact nested arguments and one tools/list each. Existing tests cover custom prefix, length, unusable names and legacy concatenation. |
| MCP-03-AC-02 | **Not fully satisfied: F-001.** Pre-filter collision prevention, no overwrite and cleanup are supported by pure and real peer/native/selected-mode probes and candidate tests. Mandatory both-source/provider diagnostic evidence is missing. |
| MCP-03-AC-03 | Supported for published entries and ordinary admission. Core `mcp.py:143-176` provides additive optional byte-size/discovery defaults and original-name repr protection; `build_mcp_metadata_index` returns a read-only mapping. Provider `mcp_loading.py:95-129`, `:193-207`, `:209-264` publishes exact registered metadata and separate counters. Independent sidecar assignment failed, native lookup was absent, full export bytes matched metadata, and a four-entry real catalog yielded discovered=4, selected=1, registered=1, rejected=2 (one discovery, one registration), filtered=1 with consistent server counts. Failed rollback retained exact metadata/owned names and count. Collision-specific missing source evidence is F-001, not an invented immutability requirement. |
| MCP-03-AC-04 | Supported. `_selected`, `mcp_registration.py:349-362`, implements selected/category/include union, all-mode category restriction, exact-name matching and exclusions. `:474-482` rejects unsatisfied explicit includes. Independent pure matrices verified default zero, category selection/restriction and explicit union; real optional excluded include failed with `missing_include`; excluded and upstream-capped entries stayed absent. Required-server semantics remain connection/discovery semantics. |
| MCP-03-AC-05 | Supported. Unchanged early admission at `mcp_loading.py:451-552` supplies only prepared entries; registration `:365-483` has no discovery RPC. Full-export size at `mcp_registration.py:152-157`, `:456-472` includes both formats and category/tags; actual registry exports are rechecked at `mcp_loading.py:167-190`. Independent cost probe measured raw=173 bytes versus complete maximum export=244, rejected a cap that fit raw input but not export, and admitted one tool at sum-of-final-costs minus one. Export-altering registry caused rollback. Real max-tools-per-server=2 plus exclusion of first admitted only second, did not backfill third, and callable returned list_calls=1. |
| MCP-03-AC-06 | Supported within the declared conservative subset and pattern limits. `mcp_registration.py:36-80`, `:160-346` completely validates/traverses within depth32/node4096/byte limits, redacts annotations and rejects unsafe semantics/unsupported keys. Independent probes verified nine encoded/control/comment/role attacks, twelve unsupported keyword variants, eight malformed/finite/shape variants, depth overflow, >4096 nodes, attack in the late property after 500 safe properties, exact safe semantics, repr safety and independent adapter schemas/tags. A real peer with 400 safe properties then unsafe late default was rejected; its separate malicious annotation tool was redacted with no sentinel in exports/metadata/decisions/logs. No universal injection guarantee is inferred. |
| MCP-03-AC-07 | Supported. Adapter implements category/tags, parameters, execute and both schemas, removes its broad ignore and provides the public validated construction path. All legacy adapter/native registry tests pass. Independent runtime-checked ToolDefinition and public `DefaultToolRegistry.get_callable` stdio dispatch prove exact routing/arguments, rather than only mock registration or protocol conformance. |
| MCP-03-AC-08 | Supported. `di.py:123-130` publishes before `kernel.py:112-113` builds profile bindings; `tool_loading.py:147-172` supplies optional known MCP reasons. An independent witness at actual binding construction observed `mcp_peer_read_file` already in sidecar and registry; a subsequent native-missing binding error cleared registrations/clients. Candidate real profile filtered/success tests and native/disabled/empty coverage pass. Native unknown-tool error text remains compatible. |
| MCP-03-AC-09 | Supported. `mcp_loading.py:131-207`, `:266-304`, `:554-574` owns insertion/rollback/stop. Five independent transaction controls passed: failure before insert, insert then raise, insert then cancellation, refused rollback with retained public owner and retry, and modified post-registry export. Native identity survived all. Independent provider and public kernel failed-client cleanup removed tools first, drained successful peers, retained manager/provider identity, recovered via public stop/restart, and did not rediscover during registration. Production noisy optional/required failure and canceled registered shutdown completed public cleanup in roughly 5.02-5.04s; processes/pipes/tasks were settled before defensive cleanup. Required 430-case aggregate includes all REM-003/004 regressions. |
| MCP-03-AC-10 | Bounded source/test/config/typing requirements supported; diagnostic documentation/evidence must be reconciled for F-001. Exactly sixteen implementation paths within allowlist; no native/security/manager/transport/config/dependency edit. Adapter broad ignore removed, none added; current required typing has no touched-file errors, with baseline failures retained explicitly. Candidate report correctly states mutable trusted native exports, one-byte-per-token estimate, stricter MCP-only includes, additive DTO migration and deferred app/output work. It cannot supply missing runtime collision-source conformance. |

## Exact required checks and results

All commands below ran independently in the governed checkout. `T` means the exact prefix `LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache`; `U` means `UV_CACHE_DIR=/private/tmp/friday-uv-cache`. These environment variables are nonsecret and explicitly authorized. No command was skipped. Logs are `/private/tmp/val008-checks/01.log` through `15.log`; exact commands/exits/times are also in `results.json`.

| # | Exact command after the stated prefix | Exit and result |
| --- | --- | --- |
| 1 | T `uv run pytest packages/friday-core/tests_core/test_mcp_contracts.py packages/friday-mcp/tests_mcp/client/test_adapter.py packages/friday-runtime/tests_runtime/test_mcp_registration.py packages/friday-agent/tests_agent/test_registry.py tests/integration/test_mcp_registry.py -q` | 0; 146 passed, 5.45s pytest / 7.91s wall. |
| 2 | T `uv run pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime packages/friday-agent/tests_agent/test_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/test_mcp_registry.py -q` | 0; 430 passed, 51.55s pytest / 54.12s wall. |
| 3 | T `uv run pytest packages/friday-tools/tests_tools -q` | 1; 233 passed, 2 declared compatibility failures, 1 unrelated deprecation warning; 11.92s pytest / 12.87s wall. |
| 4 | T `uv run pytest packages/friday-chat/tests_chat/test_mcp_config_compatibility.py packages/friday-chat/tests_chat/compat/test_config_compatibility.py packages/friday-chat/tests_chat/test_llm_config_migration.py -q` | 0; 46 passed, 1.51s pytest / 2.36s wall. |
| 5 | T `uv run pytest tests/integration -q --tb=short` | 1; 57 passed, 1 declared board-count baseline failure, 49.88s pytest / 51.51s wall. |
| 6 | U `uv run ruff check packages/friday-core/src/friday_core/mcp.py packages/friday-core/tests_core/test_mcp_contracts.py packages/friday-mcp packages/friday-runtime tests/integration/test_mcp_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py` | 0; all checks passed. |
| 7 | U `uv run mypy packages/friday-core packages/friday-runtime packages/friday-mcp` | 2; installed NumPy syntax baseline, stops before project checking. |
| 8 | U `uv run mypy --python-version 3.13 packages/friday-core/src/friday_core/mcp.py` | 1; four declared unchanged profiles.py no-any-return errors, 1 root file. |
| 9 | U `uv run mypy --python-version 3.13 packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py` | 0; 45 files, no issues. |
| 10 | U `uv run mypy --python-version 3.13 packages/friday-core/src/friday_core/mcp.py packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py` | 1; only the same four profiles.py errors, 46 root files. |
| 11 | U `uv run python scripts/friday-dev-board.py validate` | 0; 23 tasks. |
| 12 | U `uv run python scripts/friday-dev-board.py render --check` | 0; dashboard current. |
| 13 | U `uv run python scripts/check-documentation-lifecycle.py` | 0; 339 Markdown files. |
| 14 | `git diff --check 2c0d6bd1fe481fff9bb180f9e6dfb4a9a2131641..397caa9898612cd989f6404951b3e1f5005dfac2` | 0. |
| 15 | `git diff --exit-code 397caa9898612cd989f6404951b3e1f5005dfac2 -- packages tests pyproject.toml uv.lock` | 0, start and closeout. |

The passing suites overlap; their counts are not additive. Required failures are reported as failures, not converted into passing checks or repaired/waived by the reviewer.

## Independently established predecessor baselines

The exact accepted predecessor `a257f041d1d68f8aea2f5b9773df1b88acd82379` was extracted read-only with `git archive` into `/private/tmp/val008-predecessor` (packages, tests, scripts, docs, root pyproject and AGENTS). No Git worktree/branch was created or changed. The current installed venv interpreter was used against archived inputs.

For native tools and board tests, `PYTHONPATH` was the ordered `os.pathsep.join(str(p) for p in sorted(Path('/private/tmp/val008-predecessor').glob('packages/*/src')))` so every predecessor package source took precedence over editable installation. The archived warning/import paths confirmed predecessor source loading. Cwd was `/private/tmp/val008-predecessor`, with authorized T environment.

```text
/Users/chuckrussell/Dev/gendev/agent-framework/.venv/bin/python -m pytest packages/friday-tools/tests_tools -q
```

Exit 1: exactly 233 passed, the same two failures, one deprecation warning; 12.45s. The DOCX invalid ZIP fixture at `test_filesystem_readers.py:286` produced `Failed to read DOCX: File is not a zip file`; XLSX at `:306` produced `Failed to read Excel file: File is not a zip file`. Both tests demand dependency-only error wording for deliberately invalid ZIP data. No candidate edit or dependency change affects them.

```text
/Users/chuckrussell/Dev/gendev/agent-framework/.venv/bin/python -m pytest tests/integration/test_development_board.py::test_repository_development_board_is_valid_and_rendered -q --tb=short
```

Exit 1: unchanged line75 expects `22 tasks`, archived canonical board validation returns `23 tasks`; 0.09s. The command's subprocess output names the archived script/root.

With no added PYTHONPATH/MYPYPATH for the normal typing environment, archived checks were:

```text
/Users/chuckrussell/Dev/gendev/agent-framework/.venv/bin/python -m mypy --python-version 3.13 packages/friday-core --cache-dir /private/tmp/val008-baseline-fullcore-standard
/Users/chuckrussell/Dev/gendev/agent-framework/.venv/bin/python -m mypy --python-version 3.13 packages/friday-core/src/friday_core/mcp.py --cache-dir /private/tmp/val008-baseline-fullcore-standard
```

Both exit 1 with the same four `profiles.py:77/82/110/115` no-any-return errors (32 and 1 root files respectively). A fresh-cache current full-core command also exit1 with those same four errors:

```text
UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run mypy --python-version 3.13 packages/friday-core --cache-dir /private/tmp/val008-candidate-fullcore-fresh
```

The archived default command:

```text
/Users/chuckrussell/Dev/gendev/agent-framework/.venv/bin/python -m mypy packages/friday-core packages/friday-runtime packages/friday-mcp --cache-dir /private/tmp/val008-predecessor-mypy-default
```

Exit2 at unchanged installed `numpy/__init__.pyi:737`: `Type statement is only supported in Python 3.12 and greater`. The repository still targets Python3.10. It prevents project checking and is weak evidence for source correctness.

An initial supplemental archived core check with explicit source-import PYTHONPATH/MYPYPATH returned zero: those paths resolve more concrete imported package types. It is recorded as a changed import environment, not substituted for any required command or used to erase the standard-environment errors. The normal-environment predecessor runs above reproduce the baseline.

This candidate/predecessor comparison independently returned exit0:

```text
git diff --exit-code a257f041d1d68f8aea2f5b9773df1b88acd82379..397caa9898612cd989f6404951b3e1f5005dfac2 -- packages/friday-tools packages/friday-core/src/friday_core/profiles.py tests/integration/test_development_board.py pyproject.toml uv.lock
```

Thus the exact native source/tests, profiles.py, board assertion, typing/dependency configuration and lock are unchanged. Logs `baseline-1.log` through `baseline-8.log` retain the reproduction and supplemental import-environment observations. No baseline fix or waiver was made.

## Independent adversarial probe evidence

The reviewer wrote a separate stdio peer and probe harness, using production manager/client/transport/registry/kernel behavior. Unrelated LLM/storage/telemetry factories were stubbed to prevent external effects. Deterministic client/registry doubles were independently constructed for synthetic ownership/failure cases.

```text
LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run python /private/tmp/val008-probes.py > /private/tmp/val008-checks/independent-probes.log 2>&1
```

Exit0. Sixteen named groups passed: admission; filters/cost/collisions; five transaction controls; provider retained failure/cancellation; public kernel retained cleanup; real multi-peer routing; binding after observed publication; late schema attack; cross-stage counts; upstream cap/no-backfill; strict optional excluded include; peer collision prevention; native collision prevention; optional noisy failure; required noisy failure; canceled noisy registered shutdown.

The collision-control passes establish abort/cleanup behavior and record the deficient diagnostic. They do not establish source-diagnostic conformance; the separate F-001 requirement assertion exit1 does that distinction explicitly.

Production public-cleanup observations, before defensive finally cleanup:

| Probe | Observation |
| --- | --- |
| Multi-peer registry routing | 2 peers; exact `Read.File` and nested arguments; one list RPC each; byte cost equals actual native-rewrapped maximum export. |
| Binding failure after publication | Witness saw registry and sidecar published before real binding validation; subsequent failure removed MCP entries and closed peer. |
| Late schema / counts / cap / strict includes | Correct reject/redact/filter/count behavior; no backfill or repeated discovery; strict include aborts optional configuration. |
| Optional noisy failed peer | 5.032s; successful peer remained registered until public stop; both children reaped/pipes EOF. |
| Required noisy failed peer | 5.037s; startup aborted; no registration/client retained after public cleanup. |
| Canceled noisy registered stop | 5.026s total; tools/metadata removed before client wait, cancellation propagated, provider identity remained public, public stop retry completed cleanup. |
| Transaction/refusal/client doubles | Native object identity preserved; failed rollback retained exact public registry/owned-name/metadata state; retry removed it. Client failure drained successful peers; kernel/provider retained owner identity; subsequent public stop/restart recovered. |

Real probes captured DEBUG-level logs without peer sentinels. Every real probe asserted process return code, stdout/stderr EOF and absence of new live tasks before defensive cleanup. Finally blocks retried public cleanup, settled tracked transports/tasks, and killed/drained/reaped any synthetic child if necessary. No saved/private caller reference was required to make asserted public cleanup pass. Resource observations and defensive finally settlement are kept distinct.

The first scratch harness invocation exit1 because its test incorrectly estimated a two-tool budget using a different, longer canonical name, and its first noisy peer exited normally after bounded output so cancellation arrived after completed shutdown. These were probe-construction errors, not candidate defects. The harness was corrected to sum the actual two final exports, and its independent SIGTERM-ignoring peer stays alive after output. The corrected full run and expanded final run exit0. Both first-run failure cases also executed explicit final task/process settlement. Production code/budgets were not changed.

Additional local enum/pattern consistency explorations produced no candidate finding and made no external request. They do not expand the accepted schema dialect or claim universal standards/interoperability coverage.

## Documentation, configuration and package implications

Public metadata adds optional `schema_byte_size` and `discovery_state`; older input payloads/constructors remain accepted, while older strict DTO consumers need migration for new serialized fields. The report documents that distinction. `MCPValidatedDefinition`, validated wrapper construction, read-only sidecar, registration decisions, binding context and explicit registry ownership are additive boundaries. Native mandatory ToolDefinition/protocol/registry behavior and dependencies are unchanged.

MCP explicit includes now fail if unavailable/rejected/capped/excluded even on optional peers, while native missing includes retain existing behavior. Fixed MCP category/tags prevent peer category impersonation. Runtime caps include complete exported plain/OpenAI definitions and use one byte per estimated token, without tokenizer parity. The supported inline keyword list, bounded traversal and unsupported-reference rejection are explicit.

Native registry exports remain mutable to trusted in-process callers by approved scope. This review verifies peer/input/adapter mutation isolation and initial rewrapping checks; it does not demand whole-registry immutability. Later prompt consumers must copy and verify exports. Sanitized schema text remains external content and known-pattern detection is not a universal injection-proof guarantee. F-001 requires a bounded typed diagnostic/report correction; no configuration or later-slice implementation is needed.

## Stability closeout and preserved workspace

Start and closeout snapshots are `/private/tmp/val008-start.json` and `/private/tmp/val008-closeout.json`. All twenty pinned hashes matched expected and mapped working content at both points. The request hash is unchanged and equals its HEAD blob. Branch and HEAD remained unchanged. The full candidate-to-working product/config diff returned exit0 again at closeout, and the exact unrelated porcelain manifest is unchanged:

```text
 M .DS_Store
 D family-tree.md
?? docker-bench-security/
?? packages/friday-chat/config.example.yaml.pre-typed-llm-20260828.bak
?? packages/friday-sandbox/docker/Dockerfile.audit
```

No source/test/config/authority instability invalidated this review. Reviewer made no preservation-sensitive edits or cleanup. Controller may separately compare its own starting unrelated-file fingerprints.

## Residual limits and remaining gates

F-001 requires a bounded remediation directive, a new stable candidate and fresh independent review. A favorable review would permit proposed WS-03 closeout only; explicit maintainer acceptance remains separate. This report supplies neither acceptance nor implementation/remediation authority.

WS-04 per-turn selection/budget/memory-floor accounting, WS-05 output sanitation/truncation/provenance, later transcript/memory/telemetry/guides, live interoperability and complete app UAT remain unimplemented or separately gated. Full feature-branch aggregate pre-merge review and all delivery actions remain separate gates.

Local synthetic cleanup evidence uses unchanged production budgets and cooperative asynchronous scheduling. It is not a hard real-time SLA, process-tree sandbox, or proof against OS reaping failures, descendants holding pipes, cancellation-resistant I/O, arbitrary executables or universal injection. Genuine incomplete cleanup retains public ownership pending obstruction removal and retry. Declared baseline test/type debt remains visible and unresolved.

## Scratch artifacts

- Complete report: `/private/tmp/val008-report.md`.
- Required exact commands/results/logs: `/private/tmp/val008-checks/results.json`, `01.log` through `15.log`.
- Predecessor logs: `/private/tmp/val008-checks/baseline-1.log` through `baseline-8.log`; archive `/private/tmp/val008-predecessor`.
- Independent harness/peer: `/private/tmp/val008-probes.py`, `/private/tmp/val008-peer.py`; result JSON `/private/tmp/val008-probe-results.json`; final log `/private/tmp/val008-checks/independent-probes.log`.
- Public F-001 reproduction: `/private/tmp/val008-collision-repro.py`, its imported identical harness copy `/private/tmp/val008_probes.py`, and `/private/tmp/val008-checks/collision-repro.log`.
- Freeze evidence: `/private/tmp/val008-start.json`, `/private/tmp/val008-closeout.json`.

All report/evidence artifacts are outside the repository.

A supplemental `pgrep -fl /private/tmp/val008-peer.py` inventory attempt returned exit3 (`sysmond service not found`; process list unavailable). It is not evidence of global process absence and did not block the review: each spawned synthetic Process was independently tracked and had a completed wait, return code and pipe EOF in the probe's public-cleanup assertions/finally settlement. Final governed diff check still returned exit0 after all probes.

## Full authority hash closeout

All documents below are pinned to candidate `397caa9898612cd989f6404951b3e1f5005dfac2`. Each expected SHA-256 equals both pinned blob and relocated working content at start and closeout. The original `docs/planning/active/friday-mcp/` prefix is used here; only working-file comparisons replace it with `docs/planning/blocked/friday-mcp/`.

| Exact pinned authority path | SHA-256 |
| --- | --- |
| `AGENTS.md` | `7fad2b4063a0dc4201d26e353138da6165060077cc88e097dad2ac57551d987f` |
| `docs/reference/policies/repository-engineering-policy.md` | `17b830b8990f74d1b0a25a46fc2cf2f62249f4e0d668f45b96cfe03a6cc76aff` |
| `docs/reference/policies/development-task-lifecycle.md` | `d23f306ab33908f255109152c6c8686423725655184637fe2309e84d8491dc1c` |
| `docs/reference/policies/independent-validation-policy.md` | `4d951418e0f0c96a4c87d4b8a07cb4025dd94738da50893d19a6d2b7a7f82f4a` |
| `docs/planning/active/friday-mcp/build-plan.md` | `17b341bf51bd21b00ed88f6b0e413baad0b09b865cb9223a9a96d4887a9b6f00` |
| `docs/planning/active/friday-mcp/tactical-plan.md` | `ead395b4949c01bdae6dfc6fb01d8b7af3ee6071902af45ec077c913f6dcd6ba` |
| `docs/planning/active/friday-mcp/directives/ws-03-tool-naming-metadata-registry.md` | `c723e899d0916012dc324836f8c2882d5c2362a40825cec377e19182f1749efd` |
| `docs/planning/active/friday-mcp/directives/ws-00-contract-policy-foundation.md` | `ec482e46364c9f4edcd7e76f2e4156d2f8af1710cc1811bf3390d6a5a0f99fac` |
| `docs/planning/active/friday-mcp/directives/ws-01-configuration-model-validation.md` | `96ed70391066ac4402542f1f4056f4d38ac9e08be787dbd6daa2f8a41c4cb319` |
| `docs/planning/active/friday-mcp/directives/ws-02-runtime-lifecycle-provider-loading.md` | `a432dc3c17e7cff9e767ed9dc78f6a1f65ea0d51dead3fc7e5421ef04327f55d` |
| `docs/planning/active/friday-mcp/remediation/REM-003-directive.md` | `b04504638f1bded4af42c481ba35a89f02217a25fc392fae33b16ca51a57b680` |
| `docs/planning/active/friday-mcp/remediation/REM-004-directive.md` | `1079756e6f6738c1dd4fb61126d2a1b3159c3ca48ef092470b47f22a09fec37b` |
| `docs/planning/active/friday-mcp/execution/WS-00-closeout.md` | `434c24937dd4eff77d37ab6ec5c031127723fc54c83ee9446c3b088d848da486` |
| `docs/planning/active/friday-mcp/execution/WS-01-closeout.md` | `8e10fcf509102c1faadcc2e56ce06fe6f9333aaa9d164ad82494e960cbfef32b` |
| `docs/planning/active/friday-mcp/execution/WS-02-closeout.md` | `df241a9ad65e09f47df8c1aa33437e720994b811cd98d25a559b1c9626fbf5d3` |
| `docs/planning/active/friday-mcp/validation/VAL-002-report.md` | `cfceee2537adb53d5e12fa517f12cc6549691811bd63709e5902edcdedfe2566` |
| `docs/planning/active/friday-mcp/validation/VAL-004-report.md` | `d680911d220b0181fa32fca8260e0ce87f24a322d5dc64794951a85809ed2e0f` |
| `docs/planning/active/friday-mcp/validation/VAL-007-report.md` | `649c70566c59109c413e55922b7150dbee7b0acb3c131f30b78ca726060561b6` |
| `docs/planning/active/friday-mcp/rebaseline-2026-09-27.md` | `ccc6f1ca9feab180474e85b30e4c5b9319c32fbd56131f341907a452388f461a` |
| `docs/planning/active/friday-mcp/execution/WS-03-readiness-checkpoint.md` | `2224bd224d7b004e9e43ebfa1c1eaa00c906f40fa8e35d5865236d44d720b521` |

## Scratch executable evidence hashes

| File | SHA-256 |
| --- | --- |
| `/private/tmp/val008-probes.py` | `5076019241e4d7a2752f8700becdb97242037e66b3cb433cc8fd39854ae3e532` |
| `/private/tmp/val008-peer.py` | `000d4af3b9c7fb10ccde682a8a51b2f2a1b216a86c072cc11855a9a35e644ecd` |
| `/private/tmp/val008-collision-repro.py` | `3de929c600812be00b1f0df552ab04b121d6bdd7d38556950b8e234aa6d6538e` |
| `/private/tmp/val008_probes.py` | `5076019241e4d7a2752f8700becdb97242037e66b3cb433cc8fd39854ae3e532` |
| `/private/tmp/val008-checks/results.json` | `82303a6fe445268f262de602d8d33b838689c2c5d5f482bc451e61d146142120` |
| `/private/tmp/val008-checks/independent-probes.log` | `004467a2222477289b0df0188a0fca622a986d788a962a5433f955e441d83490` |
| `/private/tmp/val008-checks/collision-repro.log` | `fc31967686fce3af09bfa3ffb71d56c96e4e024ca051574ac6d530df5462038f` |
