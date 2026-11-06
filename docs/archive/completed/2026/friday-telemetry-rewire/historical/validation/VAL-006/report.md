# REM-004 final delta and aggregate independent review

**VERIFIED**

Reviewer: fresh independent agent `/root/rem004_final_delta_aggregate_validator`, GPT-6-based Codex; exact model build is unavailable. Date: 2026-10-06. Review mode: read-only REM-004 delta plus complete aggregate TELEM-01 AC-01–AC-06. No builder private reasoning or implementation conclusions were supplied or used. The controller's operational harness and raw receipts were inspected as infrastructure/evidence; all current mandatory gates supporting this result were independently replayed below.

Candidate: `8aedd87c8def5a6c514bdfea7505205e8db78bb6`. Delta base: `1b28d373bb613e754947e4b13c7f7280314c560e`. Aggregate base: `2155a0fc51f5b20dea4e35c6cfc70f1d52002735`. Exact request: `../product-validation-request.json`. Authority revisions/hashes, manifest, expanded lists, diffs, command arguments, environments, exits and log hashes are recorded in `evidence.json`, `snapshot.json` and the adjacent per-command receipts.

The 19 authority pins and controlling manifest match the committed candidate. The review read AGENTS, engineering/lifecycle/independent-validation policies, accepted MCP WS-07 contract, build/telemetry/tactical plans, CD-001/profile, REM-001–004, approved A06, WVR-002 and WVR-003, their exact inventories, and the source/tests/documentation/configuration aggregate. The final delta contains 88 Python paths, all within the approved 91-path REM-004 scope; it changes no other product paths. The aggregate expands to 98 Python files, 63 source targets and 13 owning package test trees. `delta.diff`, `aggregate.diff` and their path inventories preserve the examined ranges.

## Independent isolation and safety

The candidate was materialized in `candidate/` using a shared no-checkout clone and sparse omission set before checkout. All 267 protected tracked runtime artifacts were omitted, with no Python/config intersection. No `.env`, original `.friday`, Chroma, transcripts, credentials or dirty example YAML was used. A separate identically sparse `baseline/` at the delta base supported old/current regression comparisons. Neither snapshot has overlays.

`preflight.json` freezes the independent AST/import/effect scan of 641 retained Python files, test/conftest/helper source hashes, exact 11 listener node IDs, discovery settings and subprocess review before collection. Real children are synthetic experiment runners, MCP fake-server peers, sandbox synthetic code and the readiness-gated PTY child; inherited guard and allowlist were preserved. Only the two reviewed fixtures bind `127.0.0.1:0`, with synthetic responses and explicit server/thread cleanup. The approved normal-user sandbox escape was used for complete suites containing those exact 11 nodes. No sudo, live model/exporter activation, remote transport, installs, synchronization, downloads, builds, push or merge occurred.

The unchanged guard SHA-256 is `6f61ea4ca34c7abef9e0c709eb1e1feb0f3cf7733cbc59bc465d6b01182e9e81`. `review.py` constructs a minimal environment with offline/no-sync/no-download, temporary caches/state, no HOME override or inherited credentials/live flags, and guard first in PYTHONPATH. `origins.log` verifies all 16 public workspace package origins resolve inside this candidate. Installed Python is **3.13.10**, Ruff **0.14.10**, mypy **1.19.1**, Pydantic **2.12.5**. No exact 3.13.4 runtime execution is claimed.

## Commands and results

All pytest invocations used report-only `-rA` and private cache paths. The expanded command arguments and environments are in each named `.json`; their `.log` files retain complete raw output.

| Check / receipt stem | Raw result |
| --- | --- |
| `collect` — unchanged root importlib profile, exactly two live-module ignores | exit 0, 2,805 collected |
| `root` — same complete root profile | exit 0, 2,804 passed, 1 optional SciPy skip, 15 warnings |
| `chat` — complete Chat + telemetry, no live flags | exit 0, 741 passed, 5 gated live skips, 1 warning |
| `owners` — all 13 expanded owning trees, same two live exclusions | exit 0, 2,786 passed, 1 SciPy skip, 15 warnings |
| `focused` — original six prescribed modules | exit 0, 135 passed |
| `native-alone` / `native-after-agent` | exit 0, seven exact runtime nodes; exit 0, full agent + same seven nodes, 216 passed |
| `registry-finally` | exit 0, two actual-fixture generator restoration cases |
| `tools-contracts` | exit 0, 107 reader/Web contract tests |
| `pty-alone` / `pty-module` | exit 0, 1 / 2 passed; also passed in complete suites |
| `changed-ruff` | exit 0, no findings across exact 98 Python targets |
| `root-ruff` | **exit 1, exactly 327 findings**, disposition below |
| `mypy` | exit 0, exact aggregate 63 source files under Python 3.13 |
| `consumer-explicit-sources` | expected exit 1, exactly 12 prohibited variance assignments + 2 invalid BaseModel bounds; no positive inference errors |
| `baseline-consumer` | expected exit 1, same 14 consumer errors + the exact 3 prior response-source typing errors |
| `smoke` | exit 0, genuine Chat observer + two Composite debug providers, nested spans and actual fake application lifecycle; generic specialization/validation and old/current Pydantic schema equality |
| `lock` | exit 0, offline lock check, no download/build |
| `board` / `docs` / `metadata` | exit 0, 24 tasks / 426 Markdown files / 17 package metadata files |
| `lint-syntax-metadata.json` / `lock-metadata-whitespace.json` | 98 py313 AST parses, all 18 project floors, unchanged surviving dependency version/source tuples, selected and aggregate whitespace exits 0 |

The one optional root/owner skip is `packages/friday-memory/tests_memory/test_adapters/test_graph.py::TestElementXGraphStore::test_rank_nodes_pagerank`, because installed SciPy is absent. The five Chat skips are `test_live_primary_complete_accepts_supported_controls[disabled]`, `[enabled]`, `test_live_primary_stream_exposes_visible_text_only`, `test_live_primary_automatic_tool_selection`, and `test_live_bounded_turn_processor_flow` in `test_live_lmstudio.py`, because FRIDAY_CHAT_LIVE is absent. They are existing explicit test policy, not new reviewer exclusions. All 11 inventoried synthetic listener nodes have individual PASSED records in `root.log`; the three Chat listener nodes also pass in `chat.log`.

## Exact lint disposition

**Root Ruff nonzero; exact 326 archival findings covered by approved WVR-002, plus the exact one live CommandRegistry UP046 covered by approved WVR-003.** No raw lint pass is claimed. `lint-syntax-metadata.json` independently compares the complete sorted path/code/location/end_location/message multiset against frozen scope entries, verifies all four archive hashes, byte-identical commands.py SHA-256 `15992e7f38fe874f0104a164180679c7e76d7e09413d68152ef5cc77c0f99308`, all 17 lint configuration hashes, current tool version and py313 target. No additional diagnostic exists. Commands.py is unchanged and absent from the changed 98-file targets, so changed-file Ruff has a genuine raw zero exit.

A06 explicitly reconciles WVR-002's former zero-live condition. Both exceptions remain limited to TELEM-01 and expire at its acceptance decision or earlier source/identity/tool/config drift. Their separate historical-archive and generic-policy follow-ups remain maintainer decisions. WVR-001 is unapproved and was not used.

## Requirement and regression assessment

AC-01/02: strict default-disabled debug config rejects unknown fields/providers/malformed types; fake and stubbed-real assembly retain the observer before services, inject caller providers despite disabled YAML, and CLI reports safe state. AC-03/04: immutable bounded records retain cumulative counts; startup/application/cleanup/cancellation outcomes are truthful; sentinel privacy, validated MCP meaning, invalid-event rejection and borrowed-provider ownership are covered in `test_telemetry.py`, CLI/runtime/lifecycle suites and genuine smoke. No raw LLM/memory hooks were connected.

AC-05: per-child IDs/parents and start-time membership are retained, payload dictionaries isolated, unknown/duplicate ends ignored, partial starts rolled back, failures fan out with content-free aggregate errors. Deterministic replacement/reuse/native-generated-ID collision regressions preserve stale-end safety and completed references are released except intentional lifetime ID reservations. Full provider suites and genuine nested-span smoke pass.

R4-01: own old sparse snapshot reproduces seven passes alone and **seven failures after the full 209-test agent suite** (`baseline-native-ordered`, raw exit 1). Same ordering passes on current candidate; actual fixture preserves declaration object identity and excludes test registrations through finally on normal/early close. No production reload/catalog workaround exists.

R4-02/03/04: optional dependency imports are scoped monkeypatches, malformed/valid synthetic containers are distinguished, literals are classified before DNS and domains preserve private-answer and resolver-failure policy. PTY readiness/trigger starts the retained 0.8-second budget after imports, retains one-second work delay and bounded progress/shutdown/descriptor cleanup. Exact prechange Web/fixture raw evidence was audited against frozen old source hashes: 19 failures/1 pass before fixes, retained as retrospective rather than a reviewer-run claim (`retrospective-baselines.json`).

R4-06/06b: UTC and TimeoutError substitutions preserve Python 3.13 identities/exception matching; typing defaults, suppressions, dependency constraints and runtime policies are not weakened. The same six public generic classes remain invariant in both directions, public names/subscriptability and BaseModel bounds remain usable, and actual generic Pydantic schema/validation matches baseline. Runtime alias shape changes to TypeAliasType are explicitly observed; repository consumers use annotations, with no old identity/introspection reliance found. Published typed/legacy response forwarding, content/reasoning/tools/model/usage/raw identity, warnings, structured validation and exception identity retain their contracts. Exact three old source errors disappear in current aggregate mypy. New response regressions pass in complete owning/root suites.

The first private consumer-only invocation imported packages as Any under the existing missing-import policy and produced three assert-type errors. It is preserved in `consumer.log` and supplies no product conclusion; the corrected explicit-source probe yields precisely the same 14 intended negative diagnostics on old and new sources, with all positive assert_type checks clean (`consumer-disposition.json`).

## Preservation and residual risk

`preservation-final.json` confirms the original HEAD is still the frozen candidate, all authority pins remain exact, original dirty-path status is unchanged, and candidate/baseline governed file hashes are unchanged. Omitted protected paths remain absent. Reviewer writes are confined to private validation artifacts and snapshot infrastructure; no original product/authority/index/runtime writes were performed. Original application data was not re-read to hash it. Validation authorizes no repository mutation.

Chat/focused raw output contains an existing ConsoleSpanExporter shutdown `ValueError: I/O operation on closed file.` after pytest's successful summary. The traceback is byte-equivalent to immutable REM-003/VAL-005 baseline output; the OTel provider source is unchanged (`retrospective-baselines.json`). This diagnostic is retained, not suppressed or counted as a raw command failure. Console SDK teardown/exporter lifecycle is deferred by the first-slice contract; no remote exporter was used. It is an existing residual issue for separately governed telemetry work.

No blocking/high-severity finding or mandatory requirement violation remains. Optional SciPy coverage, exact patch-floor execution, live providers, remote exporters, complete end-to-end turn tracing, and TELEM-02–05 remain outside this result. Composite lifetime ID reservation has the documented cumulative memory cost. **VERIFIED** covers this frozen delta and aggregate TELEM-01 only; it is not maintainer acceptance, whole-initiative completion, push/merge/release or live-provider approval.
