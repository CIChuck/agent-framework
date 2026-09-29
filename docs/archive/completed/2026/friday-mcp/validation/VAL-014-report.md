# VAL-014 Independent Full WS-06 Aggregate Review

CHANGES_REQUESTED

Reviewer: `/root/mcp_ws06_val014`, separate fresh validator context. Model: Codex/GPT-6 family as supplied by the runtime; exact serving build is unavailable. Date: 2026-09-29. Review mode: `work_unit_full_aggregate`. Public request, frozen authorities, candidate source/diff, and public repository evidence were the task inputs. No builder/controller conversation, private reasoning or conclusions were inherited. Builder reports and artifacts were fingerprinted rather than adopted as behavioral evidence. No source, test, authority, board, candidate Git index or runtime-state edits were made.

Candidate: `910508cd40c49c30ddfbd6a779aec5fda3ac2a67`. Approved base: `99bde5148ee21f47d4734d2a026fb198a3d19cbd`. Aggregate diff: `99bde5148ee21f47d4734d2a026fb198a3d19cbd..910508cd40c49c30ddfbd6a779aec5fda3ac2a67`. Authorization commit: `4d049880650c62267670b3690928120ac391649b`. Accepted predecessor: `cca86b51105666d12c2e7ed571f8f9a05d2085f9`. Request preparation: `548da4ef9269a0b4ec9b02ae37a3dfdaf5ac9228`. Review checkout HEAD was controller-only dispatch `1c5cb22d9bb39a88582f13e5642ad3b9b79ba776`; all governed candidate bytes match the pinned revision. Mutable controller phase metadata is excluded by the request.

## Decision and prioritized finding

One violated mandatory retry requirement prevents verification. The remaining required evidence was completed. This review does not authorize remediation, completion, acceptance or delivery.

### 1. VAL014-F01 — Medium — Public persistence retries allocate another record and cannot reuse the immutable receipt

Affected sources: `packages/friday-chat/src/friday_chat/adapters.py:292`, `packages/friday-chat/src/friday_chat/memory_mcp.py:65`, and `packages/friday-memory/src/friday_memory/ingestion/mcp.py:89`.

Authority: the approved WS-06 directive's MCP-06-04 requires “Reuse owned IDs on retries” and one bounded record per eligible completed call; WS06-AC05 explicitly requires truthful retry behavior. The lower-level ingester accepts an explicit owned `record_id`, but the production Chat adapter always omits it. The coordinator stages another snapshot before attempting another append for the same owned entry. SQLite correctly rejects the duplicate entry ID, while the coordinator keeps the newly staged record pending after append begins.

Reproduction uses production `FrameworkMemoryAdapter`, `CollectionManager`/Chroma, `FrameworkTranscriptAdapter` and SQLite with deterministic embeddings. Persist the same `InteractionTurn(turn_id="owned-entry")` and checked completed call twice. The first operation creates a committed record and an immutable paired receipt. The second allocates a different pending UUID, then raises `RuntimeError: Failed to append transcript entry.` The original committed record and single transcript entry remain unchanged, but two semantic records now exist for that one completed call. Public retries cannot reuse either the original record or receipt. The same result occurs in fresh installed/extracted declared distributions.

Exact commands (both exit **1**):

```sh
uv run --no-sync python /private/tmp/val014-independent/reproduce_retry.py /private/tmp/val014-independent/retry-current
/private/tmp/val014-independent/isolated/bin/python -I /private/tmp/val014-independent/reproduce_retry.py /private/tmp/val014-independent/retry-installed
```

Evidence: [reproducer](VAL-014-evidence.tar.gz#reproduce_retry.py), [checkout log](VAL-014-evidence.tar.gz#retry-current.log), [checkout observation](VAL-014-evidence.tar.gz#retry-current/observation.json), [distribution log](VAL-014-evidence.tar.gz#retry-installed.log), [distribution observation](VAL-014-evidence.tar.gz#retry-installed/observation.json). Both observations show two distinct record IDs, one committed/one pending, one entry and one retrievable result. No detached tasks remain.

Risk: each retry performs another embedding/write and leaves another indefinitely excluded pending record, while an otherwise valid completed interaction reports persistence failure. This is a bounded data-integrity/idempotency gap; it does not expose the pending record through recall or falsify the original receipt.

Required mitigation: make the production public preparation/persistence boundary preserve and reuse the owned record identity for each entry/call, and verify/reuse an already matching immutable transcript receipt. Preserve provenance ownership, reject conflicting retries without overwrite, and retain existing pending/cancellation rules. A helper-only explicit `record_id` test is insufficient.

Required regression coverage: retry the public coordinator with real Chroma/SQLite after success, false append, ambiguous post-append failure and publication failure; assert stable IDs, no extra embeddings/records, unchanged append-only entry, truthful returned facts, retrying mixed/repeated-name calls, and rejection of conflicting same-entry/call payloads. Cover both checkout and built distributions. Documentation impact: reconcile the implementation report's retry claim with the implemented public behavior; no new configuration/dependency/schema is required by this finding.

## Seven tactical tasks

| Task | Assessment | Independent evidence |
| --- | --- | --- |
| MCP-06-01 typed provenance | PASS | Strict frozen snapshot/receipt contracts reuse Core; actual call/entry/record IDs survive real Chroma/SQLite readback, promotion, decay and reload in checkout and installed probes. |
| MCP-06-02 disabled default | PASS | Public streaming/non-streaming turns make zero semantic writes/embedding calls and allocate no MCP IDs; conversation, native mixed calls and legacy capability consumers remain compatible. |
| MCP-06-03 exact grants | PASS | Server, canonical-tool and union positives; case, prefix, original-name, unlisted, failed, unsafe and tiny-cap negatives exercised with real peers. Wildcards/invalid canonical grants fail the accepted Core contract. |
| MCP-06-04 sanitation/publication | CHANGES_REQUESTED | Separate complete storage sanitation, byte overhead, pending/readback/publication and partial/cancellation probes pass; public owned retry violates F01. |
| MCP-06-05 freshness/maintenance | PASS | Snapshot/no-revocation assumptions retained; stale/unknown labels preserved; pending/malformed records excluded; promotion/reload and all five maintenance plans retain eligibility boundaries. |
| MCP-06-06 supplied budget | PASS | Recall receives exact supplied values once including zero; intact snapshot fits at 68 estimated tokens and is omitted at 67; native/reservation predecessor tests pass. |
| MCP-06-07 labels/old records | PASS | Production Chat retains safe source/trust/freshness and untrusted envelopes; `include_mcp=False` excludes snapshots; ordinary file/native records query normally, malformed metadata fails closed. |

## Ten acceptance criteria

| Criterion | Assessment and evidence |
| --- | --- |
| WS06-AC01 | PASS. Public typed DTOs and Core contracts, complete bounded JSON/scalar provenance, actual correlated paired IDs; checkout/installed server/tool/union probes and reloads. |
| WS06-AC02 | PASS. Both default modes produce no semantic record/embedding or memory ID; actual transcript and ordinary conversation remain; native echo and legacy optional-capability tests pass. |
| WS06-AC03 | PASS. Exact server OR canonical-tool union, no implicit grant; negative public peer cases and unchecked/correlation/model-size facts, malformed wildcard/case contracts. |
| WS06-AC04 | PASS within accepted sanitizer semantics. Independent injection, zero-width normalization, multibyte, escaped-overhead and tiny-cap probes reject; stored text and metadata/log/results/exports contain no argument, protocol/env/header, unsafe-output or exception sentinels. No raw/quarantine storage is added. |
| WS06-AC05 | FAIL: F01. Durable writes and actual append/readback precede publication in normal paths. False/partial write, failed cleanup, false append, bad receipt, cancellation during stage/after append/publication, crash pending, mixed/repeated names and concurrency remain honest and excluded; owned public retry is not implemented correctly. |
| WS06-AC06 | PASS. Pending survives restart excluded, cannot promote; committed provenance survives promote/decay/reload. Stale/unknown state stays honest. Changed allowlist denies future write without falsely revoking earlier snapshots. Five maintenance plans omit snapshots from mutable/provider candidates. |
| WS06-AC07 | PASS. Public helpers and production Chat preserve full labels/wrappers, filters and malformed exclusion. Old file/native/conversation data remains compatible; native/private exporter behavior remains. |
| WS06-AC08 | PASS. Exact once budget spy, zero exclusion and public 68/67 exact-boundary retrieval; complete byte/4 estimate includes all wrappers/labels; unchanged WS-04 schema/result reservation/floor/selection suite passes. Native snippets are counted before newly added MCP snippets; no exact legacy-tokenizer claim is made. |
| WS06-AC09 | PASS. Temporary production Chroma/SQLite actual correlations and existing JSONL/Markdown/CSV verified in checkout and fresh declared distributions. Metadata-disabled JSONL has neither MCP provenance nor memory IDs; native exports retain existing shape. No schema/config/dependency/lock change. |
| WS06-AC10 | PASS for review evidence completion and scope/typing. Exact authorized 18 implementation paths plus eight allowed controller paths; all 16 commands, base comparisons, isolated distribution proof, process/task cleanup and frozen-byte audits completed. Product verification is still denied by AC05/F01. |

Task/criterion evidence: [complete final public probe ledger](VAL-014-evidence.tar.gz#public-final/probes.json), [installed ledger](VAL-014-evidence.tar.gz#public-installed/probes.json), [additional exact-budget/crash/partial/policy ledger](VAL-014-evidence.tar.gz#extra-public/probes.json), [original probe source](VAL-014-evidence.tar.gz#public_probes.py), [additional source](VAL-014-evidence.tar.gz#extra_probes.py). Required focused tests corroborate these independent probes; they are not treated as the verdict.

## All required commands, outputs and exits

Commands ran from the governed repository with `UV_CACHE_DIR=/private/tmp/friday-uv-cache`, `UV_NO_SYNC=true`, `LITELLM_LOCAL_MODEL_COST_MAP=true` and `PYTHONDONTWRITEBYTECODE=1`. `PYTEST_ADDOPTS=-p no:cacheprovider` and a scratch `MYPY_CACHE_DIR` prevent reviewer-owned cache writes in the repository. Full unfiltered stdout/stderr and exact exits are retained; no timeout occurred.

**C01 — exit 0 — 161 passed in 2.63s.** [original evidence](VAL-014-evidence.tar.gz#check-01.log)

```sh
uv run --no-sync pytest packages/friday-memory/tests_memory/test_mcp_memory.py packages/friday-memory/tests_memory/test_retrieval/test_collection_manager.py packages/friday-memory/tests_memory/test_maintenance/test_mutation_participant.py packages/friday-chat/tests_chat/test_mcp_memory.py packages/friday-chat/tests_chat/test_mcp_execution_transcript.py packages/friday-chat/tests_chat/test_mcp_turn_budget.py packages/friday-transcript/tests/test_mcp_provenance.py tests/integration/test_mcp_memory_ingestion.py
```

**C02 — exit 0 — 97 passed in 3.59s.** [original evidence](VAL-014-evidence.tar.gz#check-02.log)

```sh
uv run --no-sync pytest packages/friday-chat/tests_chat/test_mcp_execution_security.py packages/friday-chat/tests_chat/test_mcp_chat_bridge.py tests/integration/test_mcp_execution_provenance.py packages/friday-chat/tests_chat/compat/test_tool_loop_parity.py packages/friday-chat/tests_chat/compat/test_turn_contract_parity.py
```

**C03 — exit 0 — 715 passed, 1 skipped, 1 warning in 9.64s.** [original evidence](VAL-014-evidence.tar.gz#check-03.log)

```sh
uv run --no-sync pytest packages/friday-memory/tests_memory
```

**C04 — exit 1 — 1 failed, 609 passed, 5 skipped, 1 warning, 3 errors in 14.05s.** [original evidence](VAL-014-evidence.tar.gz#check-04.log)

```sh
uv run --no-sync pytest packages/friday-chat/tests_chat
```

**C05 — exit 0 — 35 passed in 0.22s.** [original evidence](VAL-014-evidence.tar.gz#check-05.log)

```sh
uv run --no-sync pytest packages/friday-transcript/tests
```

**C06 — exit 0 — 209 passed, 10 warnings in 0.15s.** [original evidence](VAL-014-evidence.tar.gz#check-06.log)

```sh
uv run --no-sync pytest packages/friday-agent/tests_agent
```

**C07 — exit 0 — 416 passed in 7.81s.** [original evidence](VAL-014-evidence.tar.gz#check-07.log)

```sh
uv run --no-sync pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime
```

**C08 — exit 1 — 1 failed, 79 passed in 50.73s.** [original evidence](VAL-014-evidence.tar.gz#check-08.log)

```sh
uv run --no-sync pytest tests/integration
```

**C09 — exit 0 — All checks passed!.** [original evidence](VAL-014-evidence.tar.gz#check-09.log)

```sh
uv run --no-sync ruff check packages/friday-memory packages/friday-chat packages/friday-transcript tests/integration/test_mcp_memory_ingestion.py
```

**C10 — exit 2 — Found 1 error in 1 file (errors prevented further checking).** [original evidence](VAL-014-evidence.tar.gz#check-10.log)

```sh
uv run --no-sync mypy packages/friday-memory packages/friday-chat packages/friday-transcript
```

**C11 — exit 0 — Success: no issues found in 9 source files.** [original evidence](VAL-014-evidence.tar.gz#check-11.log)

```sh
uv run --no-sync mypy --python-version 3.13 packages/friday-memory/src/friday_memory/models/mcp.py packages/friday-memory/src/friday_memory/ingestion/mcp.py packages/friday-memory/src/friday_memory/retrieval/mcp.py packages/friday-memory/src/friday_memory/retrieval/collection_manager.py packages/friday-memory/src/friday_memory/maintenance/mutation.py packages/friday-chat/src/friday_chat/memory_mcp.py packages/friday-chat/src/friday_chat/runtime.py packages/friday-chat/src/friday_chat/adapters.py packages/friday-chat/src/friday_chat/turns/processor.py
```

**C12 — exit 0 — Resolved 208 packages in 3ms.** [original evidence](VAL-014-evidence.tar.gz#check-12.log)

```sh
uv lock --check --offline
```

**C13 — exit 0 — Development board validation passed: 23 tasks.** [original evidence](VAL-014-evidence.tar.gz#check-13.log)

```sh
uv run --no-sync python scripts/friday-dev-board.py validate
```

**C14 — exit 0 — Planning dashboard is current.** [original evidence](VAL-014-evidence.tar.gz#check-14.log)

```sh
uv run --no-sync python scripts/friday-dev-board.py render --check
```

**C15 — exit 0 — Documentation lifecycle validation passed: 359 Markdown files checked.** [original evidence](VAL-014-evidence.tar.gz#check-15.log)

```sh
uv run --no-sync python scripts/check-documentation-lifecycle.py
```

**C16 — exit 0 — Whitespace check clean.** [original evidence](VAL-014-evidence.tar.gz#check-16.log)

```sh
git diff --check 99bde5148ee21f47d4734d2a026fb198a3d19cbd..910508cd40c49c30ddfbd6a779aec5fda3ac2a67
```

## Immutable-base comparisons and environment distinctions

Base was independently extracted with `git archive 99bde5148ee21f47d4734d2a026fb198a3d19cbd`, and every archived file was compared against that Git revision. A scratch Git index was added only to permit the documentation checker to enumerate the immutable archive. No baseline product files changed. Exact unchanged required commands ran with `UV_PROJECT_ENVIRONMENT` selecting the existing interpreter and `PYTHONPATH` selecting only approved-base framework source directories. The installed environment was used as the tool/dependency environment, not as candidate source. Relevant tracebacks locate base source in the archive.

| Base check | Exit | Independent comparison |
| --- | --- | --- |
| B03-exact | 0 | `uv run --no-sync pytest packages/friday-memory/tests_memory`; [original evidence](VAL-014-evidence.tar.gz#B03-exact.log) |
| B04-exact | 1 | `uv run --no-sync pytest packages/friday-chat/tests_chat`; [original evidence](VAL-014-evidence.tar.gz#B04-exact.log) |
| B08-exact | 1 | `uv run --no-sync pytest tests/integration`; [original evidence](VAL-014-evidence.tar.gz#B08-exact.log) |
| B09-exact | 1 | `uv run --no-sync ruff check packages/friday-memory packages/friday-chat packages/friday-transcript tests/integration/test_mcp_memory_ingestion.py`; [original evidence](VAL-014-evidence.tar.gz#B09-exact.log) |
| B10-exact | 2 | `uv run --no-sync mypy packages/friday-memory packages/friday-chat packages/friday-transcript`; [original evidence](VAL-014-evidence.tar.gz#B10-exact.log) |
| B09-common | 0 | `uv run --no-sync ruff check packages/friday-memory packages/friday-chat packages/friday-transcript`; [original evidence](VAL-014-evidence.tar.gz#B09-common.log) |

Base Chat reports the same PTY assertion and the same three denied localhost-bind fixture errors as the candidate (591 versus 609 passing tests). Base integration reports the same board assertion expecting `22 tasks` when the valid board has 23 (77 versus 79 passing tests). Base and candidate default mypy both stop at installed NumPy `__init__.pyi:737`, where configured Python 3.10 cannot parse Python 3.12 syntax. Candidate meaningful Python-3.13 typing passes all nine affected source files with no error filtering. Both common affected-package Ruff scopes pass; exact base C09 additionally reports only the newly added integration filename absent from the base. Base Memory passes 680 tests; candidate passes 715.

The first archive-only baseline attempt lacked a scratch Git index, so the documentation lifecycle test also failed on `git ls-files` exit 128; this was an archive harness limitation, not a candidate regression or accepted base debt. The complete exact rerun resolves that artifact and leaves only the named board-count failure. Both original and final attempts are retained in `baselines.json`, `base-check-*.log`, `baselines-exact.json` and `B*-exact.log`.

An exploratory probe initially assumed Unicode compatibility/fullwidth normalization that the accepted Core sanitizer does not implement. That assumption is not a new WS-06 requirement: Core's public configuration implements zero-width/entity/comment/whitespace normalization. The original failing exploratory probe/script/log are retained, then the complete bounded normalization probe used the supported zero-width contract and passed. F01 persisted in every independent retry run. Pattern-based sanitation and an untrusted boundary do not claim universal detection of all possible semantic instructions.

## Offline built-distribution proof

All 16 current framework wheels were independently rebuilt from scratch copies with exact `uv build --wheel --offline --out-dir ... PACKAGE` commands, all exit 0. Initial `--no-build-isolation` attempts failed, exit 2 for each package, because hatchling was absent from the selected build interpreter. The successful retry used the existing cached declared isolated build backend; no dependency or environment was installed into the governed repository. Both attempt logs and command ledgers remain intact.

A fresh venv with no system site-packages received the rebuilt framework wheels by extraction and only declared external distributions from installed noneditable distribution files. Recursive requirement expansion checked active environment/extra markers and every declared version: 135 distributions, 259 edges. `.pth`/editable links were excluded; paths outside site-packages were rejected. Fresh Python `-I`, with no source `PYTHONPATH`, independently imported the public snapshot, storage/preparation DTOs and Chat receipt boundaries, then ran the full production peer/Chroma/SQLite/export/failure/cancel/reload/maintenance/budget probes. Recorded origins for all four changed framework distributions are under the fresh isolated site-packages. F01 is independently reproduced there.

The separate clean offline resolver install exits 1 because `litellm==1.100.1` is absent from the resolver cache. This is disclosed as an environment cache gap, distinct from the independently established declared-distribution/extraction proof. No claim of a successful clean resolver installation is made.

Evidence: [build command ledger](VAL-014-evidence.tar.gz#builds.json), [initial failures](VAL-014-evidence.tar.gz#builds-initial.json), [recursive dependency proof](VAL-014-evidence.tar.gz#declared-dependencies.json), [import origins](VAL-014-evidence.tar.gz#public-installed/import-origins.json), [clean install log](VAL-014-evidence.tar.gz#clean-install.log), [package proof source](VAL-014-evidence.tar.gz#package_proof.py). Rebuilt wheels are original archive members under `wheels/` and carry external byte hashes.

## Scope, policy, preservation and cleanup

The complete 26-path aggregate contains exactly nine authorized sources, eight tests, the implementation report and eight allowed controller artifacts. There are no dependency, lock, configuration, transcript-store/schema/exporter or other out-of-scope product changes. CollectionManager's file-wide typing suppression is removed; no new broad ignores, blanket casts or essential assert-only invariants were introduced. New dynamic decoding remains confined to the existing Chat legacy payload boundary; typed Memory and Core public contracts govern the new crossing.

Initial and closeout checks independently match all 40 authority inputs, six candidate reports, two builder artifacts, 19 historical evidence inputs and 985 product files, plus all five unrelated fingerprints: modified `.DS_Store`, absent `family-tree.md`, 57-file `docker-bench-security/`, Chat backup and sandbox audit Dockerfile. Request hash is `916706797bb1d7c07138c98abe4c537d58cd58e9174e583d49ab0581b63860ad`. Candidate-revision blob checks additionally verify all request authorities/reports/builder artifacts and all product hashes against the pinned commit, not only the working directory. No mismatch exists. The initial hash audit occurred after the first focused command results; candidate-revision comparison and identical final bytes establish that no reviewed input drift occurred. Mutable controller dispatch metadata changed only as disclosed above.

All peer processes were owned, awaited, killed if necessary, drained and reaped in `finally`. Each complete public run records 12 reaped peer processes, no registry connections/metadata, and no pending asyncio tasks; dedicated retry reproducers likewise record no pending tasks. Systemwide `ps` inventory was denied by the sandbox; ownership-based cleanup is independently recorded and does not infer the absence of unrelated user processes. Reviewer scratch DBs/venvs/caches remain under `/private/tmp`; no user runtime, cache, `.friday`, Chroma/transcript state or unrelated work was cleaned.

Evidence: [initial preservation](VAL-014-evidence.tar.gz#freeze-initial.json), [closeout preservation](VAL-014-evidence.tar.gz#freeze-final.json), [scope/revision/base byte audit](VAL-014-evidence.tar.gz#scope-and-revision-audit.json), [checkout cleanup](VAL-014-evidence.tar.gz#public-final/cleanup.json), [distribution cleanup](VAL-014-evidence.tar.gz#public-installed/cleanup.json), [original command/source preservation](VAL-014-evidence.tar.gz#supplementary-commands.json).

## Evidence accounting and remaining gate

All 16 required commands completed. Eleven independent baseline command attempts include the initial five and final exact six. Thirty-two framework build attempts comprise 16 initial backend failures and 16 successful offline builds. The initial exploratory public run contains 25 probes/263 assertions; corrected checkout run 25/291; fresh installed run 25/295; supplemental run 29/302 (it repeats the 25 before four additions because importing the original standalone module executes its entry point). Thus 104 complete public probe executions, 1,151 assertions, plus two dedicated retry reproducers were recorded; exploratory failures and repeated executions are not omitted or misrepresented as unique passing cases. Test commands may exit 0 while the probe ledger records a candidate failure because the harness completes all cases. The dedicated F01 reproducers deliberately exit 1.

The external artifact manifest lists every selected member's relative name, byte count and SHA256. The archive verification compares every archived original member byte-for-byte against scratch; the artifact-selection JSON identifies the report member, review mode, outcome, finding, check/probe counts and explicitly excluded regenerable scratch. Original logs, sources, wheel files, exports, temporary test DB/vector evidence and both failed/successful attempts are retained losslessly. The report is archived unchanged, using evidence archive-relative links.

Exit gate: bounded remediation of VAL014-F01, a new stable candidate, and a fresh complete independent review. WS-06 remains started; no maintainer acceptance, future workstream or delivery authority follows from this review.
