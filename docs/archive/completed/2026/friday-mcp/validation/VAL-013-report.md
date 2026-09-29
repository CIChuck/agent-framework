# VAL-013 independent validation report

Overall outcome: **VERIFIED**.
Delta outcome: **VERIFIED** (`446e3a6f4e445a456dcbe6ef25058e60af54fe53..cca86b51105666d12c2e7ed571f8f9a05d2085f9`).
Complete REM006 remediation delta: **VERIFIED** (`dd6a337eb2928ab4050ea70fb41dc77072210e34..cca86b51105666d12c2e7ed571f8f9a05d2085f9`).
Work-unit aggregate outcome: **VERIFIED** (`a609f948fe2d869ac29d0cce29d22d9334cd7d08..cca86b51105666d12c2e7ed571f8f9a05d2085f9`).

All ten WS05, six REM006 and four REM007 criteria and all eight original tasks pass the approved scope. VAL-012-F-001 closes; VAL-011-F-001/F002 closure is independently reconfirmed. No new finding or unresolved mandatory product violation was established. The nonzero broad commands below are independently reproduced, unchanged baseline/environment failures, not clean passes. This result is independent verification, **not maintainer acceptance or delivery authorization**.

Reviewer: Codex `/root/mcp_ws05_val013`, newly spawned fresh context without inherited parent/builder/remediator context; GPT-6 family, exact deployment ID unavailable. Date: 2026-09-28 America/New_York. This review remained READ-ONLY: no governed source/test/report/process edit, staging, commit, board mutation, fix, migration or delivery. Scratch scripts/logs only under `/private/tmp/VAL-013-independent-20260928`. No parent/builder/remediator sessions or private reasoning were read. Published VAL012 probe source informed reproductions; all cited commands/probes were executed independently and missing malformed-name negatives newly authored. No earlier verdict was adopted.

## Frozen authority and reviewed scope

Branch `feature/friday-mcp-ws05-execution`; frozen product/report candidate `cca86b51105666d12c2e7ed571f8f9a05d2085f9`. Request/evidence preparation `f5510ed599cae1342f33ce8bc0ca977c2c1b0c06`; observed start/closeout HEAD `ee8aa0367c92a1dfb79ea89737dfb8eb6311509e` adds controller dispatch metadata only. Accepted predecessor `53d76d45cedea16122436e53b178de074c5bc322`; original WS05 authority `5e86df832a311a62509fb0838f6c45b6ecd6fdfa`; REM006 approval `5145f0638fe644c97dc74e0dcf8f7657f8fbcd12`; REM007 start `69831774fcd3ebdbd62a2f09b207ecafe1e6bb58`, dispatch `5ff0831a9d9ef57b1630ef0f6330d5b60bf2d6d5`. REM007 preserves native compatibility within the existing explicitly approved REM006 eight paths and narrows the repair to three paths; it does not create new feature/path authority.

The [request](VAL-013-evidence.tar.gz#input/VAL-013-request.yaml) and [current freeze](VAL-013-evidence.tar.gz#input/VAL-013-frozen-inputs.json) were read first, then AGENTS/policies, all pinned contracts/directives/history, candidate claims, and the full approved aggregate plus both remediation ranges. Request SHA256 `d61fae8ab6095d9871cad19229146f999f815ad0ef5686b786fc76c49cbb5b90`; freeze SHA256 `d8349753c1a1678a595507bc10bfe7de92154d6d0c1e3741ee8d86e1446ddc40`. All pinned input bytes are retained at their original paths below `input/`; the current freeze lists their individual hashes.

Start and closeout independently match request1, authorities34, candidate reports5, historical evidence19, builder evidence5, tracked product/config/test bytes978, and preserved unrelated fingerprints5: **2064 comparisons each, zero mismatch**. The product/authority/report checks include exact candidate Git blobs; post-candidate controller evidence uses pinned filesystem checksums without claiming membership in that candidate tree. `.DS_Store`, absent `family-tree.md`,57-file `docker-bench-security/`, Chat config backup and Sandbox audit Dockerfile retain their recorded states/fingerprints.

Full aggregate has exactly24 allowed implementation paths:12 sources,2 dependency paths,8 tests/fixture paths and2 approved reports. Complete REM006 has exactly8; followup has exactly3 (`loop.py`, existing security test, existing REM006 report). Controller paths are separately enumerated; no unallowed implementation path exists. Full diffs: [aggregate](VAL-013-evidence.tar.gz#input/aggregate.diff), [REM006](VAL-013-evidence.tar.gz#input/remediation.diff), [followup](VAL-013-evidence.tar.gz#input/followup.diff). E7/E8 retain exact scopes and freeze results.

Historical manifests govern their original candidates, never the current product. Independent member hash/size verification: VAL011181/182 members, VAL012327/328, REM006205/206, REM007184/185; all declared members match, no error. The one additional member in each is its manifest. Archived original REM006 report SHA256 `99d856c508203693782386109fd8841b20a0cfaa266197299fa5a476dd3e6950` matches `f24ed20f82eac0cbce17e4b86615497cc9993921`; current report retains that byte-exact prefix and appends the authorized followup. Current report SHA256 `30c0b2ab647c5337626e725d77681dae438969a962da70d240f265062fe88c51` is governed by the current freeze.

## Source and independently executed evidence index

Line references below describe the frozen candidate, with complete source bytes retained. The complete test assertion/decorator index is [candidate test review](VAL-013-evidence.tar.gz#probes/candidate-test-review.txt); all eight test/fixture paths and aggregate test diff are archived. Requirement IDs below refer to the pinned request/directives, not inferred features.

| Source | Frozen member | Reviewed contract |
|---|---|---|
| S1 | [packages/friday-core/src/friday_core/mcp.py](VAL-013-evidence.tar.gz#sources/packages/friday-core/src/friday_core/mcp.py) | 179-231: immutable shared DTO, optional byte sizes, fixed status/code rules |
| S2 | [packages/friday-mcp/src/friday_mcp/client/base.py](VAL-013-evidence.tar.gz#sources/packages/friday-mcp/src/friday_mcp/client/base.py) | 33-41,255-293: safe tools/call errors; exact original routing |
| S3 | [packages/friday-chat/src/friday_chat/tools/schemas.py](VAL-013-evidence.tar.gz#sources/packages/friday-chat/src/friday_chat/tools/schemas.py) | ToolCallRecord: optional shared provenance follows original four positional fields |
| S4 | [packages/friday-chat/src/friday_chat/tools/output.py](VAL-013-evidence.tar.gz#sources/packages/friday-chat/src/friday_chat/tools/output.py) | 37-105: ID allocation/reconciliation;108-296: complete checked envelope;299-358: copied request redaction |
| S5 | [packages/friday-chat/src/friday_chat/tools/loop.py](VAL-013-evidence.tar.gz#sources/packages/friday-chat/src/friday_chat/tools/loop.py) | 24-38,65-196: recording protocol, guarded reservation, legacy filtering and thresholds |
| S6 | [packages/friday-chat/src/friday_chat/tools/mcp.py](VAL-013-evidence.tar.gz#sources/packages/friday-chat/src/friday_chat/tools/mcp.py) | 93-150: direct public checked record boundary and fixed error classification |
| S7 | [packages/friday-chat/src/friday_chat/turns/processor.py](VAL-013-evidence.tar.gz#sources/packages/friday-chat/src/friday_chat/turns/processor.py) | 369-407,451-569: both turn modes, retained history, pending capture and coherent IDs |
| S8 | [packages/friday-chat/src/friday_chat/adapters.py](VAL-013-evidence.tar.gz#sources/packages/friday-chat/src/friday_chat/adapters.py) | 1108-1205: safe actual-entry persistence;1313-1333: new-session MCP stanza exclusion |
| S9 | [packages/friday-transcript/src/friday_transcript/models/transcript.py](VAL-013-evidence.tar.gz#sources/packages/friday-transcript/src/friday_transcript/models/transcript.py) | 32-137,263-300: bounded summaries, optional typed facts and strict paired actual correlations |
| S10 | [packages/friday-transcript/src/friday_transcript/exporters/jsonl.py](VAL-013-evidence.tar.gz#sources/packages/friday-transcript/src/friday_transcript/exporters/jsonl.py) | full structured serialization and existing metadata flag |
| S11 | [packages/friday-transcript/src/friday_transcript/exporters/markdown.py](VAL-013-evidence.tar.gz#sources/packages/friday-transcript/src/friday_transcript/exporters/markdown.py) | opt-in MCP provenance and bounded escaped human previews |
| S12 | [packages/friday-transcript/src/friday_transcript/exporters/csv.py](VAL-013-evidence.tar.gz#sources/packages/friday-transcript/src/friday_transcript/exporters/csv.py) | unchanged entry columns; bounded MCP summaries and all-session snapshot export |
| S13 | [packages/friday-transcript/pyproject.toml](VAL-013-evidence.tar.gz#sources/packages/friday-transcript/pyproject.toml) | declared Core dependency; uv.lock adds only two matching Core edges |

| Evidence | Executed result/log | Retained reproduction |
|---|---|---|
| E1 | [E1](VAL-013-evidence.tar.gz#logs/independent-probes-final.log) | 35 independently executed public cases; scripts/test_independent.py and probe_common.py; probe-results.json |
| E2 | [E2](VAL-013-evidence.tar.gz#logs/extra-supplement.log) | 10 independently executed ownership/capture/storage negatives; scripts/test_supplement.py; supplement-results.json |
| E3 | [E3](VAL-013-evidence.tar.gz#logs/added-corrected.log) | 24 newly authored malformed-name and unchanged failure-threshold cases; scripts/test_val013_added.py; probes/added-matrix.json |
| E4 | [E4](VAL-013-evidence.tar.gz#finding-facts-candidate.json) | standalone exact privacy and later-native collision reproduction; original/remediation/followup comparison files and logs retained |
| E5 | [E5](VAL-013-evidence.tar.gz#native-controls-candidate.json) | 16 native malformed-name controls per revision; all four revision results retained |
| E6 | [E6](VAL-013-evidence.tar.gz#probes/required-commands.json) | 19 exact required commands, exits and elapsed times; logs/command-01.log through command-19.log include full output/env/cwd |
| E7 | [E7](VAL-013-evidence.tar.gz#probes/integrity.json) | all delta scopes, historical archive/member hashes, original REM006 report and unchanged failure-source proof |
| E8 | [E8](VAL-013-evidence.tar.gz#probes/freeze-closeout.json) | 2064 current byte/fingerprint comparisons; freeze-start.json independently checked same set |
| E9 | [E9](VAL-013-evidence.tar.gz#package-commands.json) | offline builds and isolated imports; wheel-metadata.json, declared-dependencies.json and full package logs |
| E10 | [E10](VAL-013-evidence.tar.gz#logs/baseline-corrected-integration.log) | corrected complete original-source integration; original Chat/default typing/import and initial harness logs retained |

## Numbered historical finding closure

| Finding | Severity and controlling requirement | Independent reproduction and final evidence | Status/risk boundary |
|---|---|---|---|
| VAL-012-F-001 | Medium; REM007-AC01 and REM006-AC03 native compatibility | Original and reviewed WS05 source:16 native controls each,zero exception. Pre-followup REM006 source:8 present-ID dict/list exceptions. Current source:16 controls,zero exception, exact valid-following legacy IDs. Newly authored16 native/mixed matrix cases plus8 unchanged threshold cases pass; S5 string guard precedes set membership. E3/E5 and four revision import/fact files. | CLOSED. Invalid calls still contribute to the established failure threshold; they never execute. |
| VAL-011-F-001 | High; WS05-AC02 and REM006-AC01 | Original and remediation-base source retain env/header/launch in new session,JSONL on/off and all-session sessions.csv. Candidate omits MCP stanza; original native snapshot and actual runtime config remain intact. Production both modes/fallback and all7 exporters are sentinel-free; session/entry CSV files checked separately. S8:1327,E1/E4. | CLOSED for new snapshots. Previously stored snapshots remain unchanged and can still export their original sensitive config; no migration/rewrite authority. |
| VAL-011-F-002 | High; WS05-AC06/07 and REM006-AC02 | Reviewed WS05 source: later native shared ID gives TurnPersistenceError and zero new entry. Candidate: native ID unchanged, prior MCP request/result/record/facts move coherently, one durable entry. Repeated replacement reclaims, pending native and duplicate pending MCP fallback IDs, repeated names/two peers/concurrent8 calls, fake/SQLite × stream/nonstream × normal/fallback pass. S4/S5/S7/S9,E1/E4. | CLOSED. Tools are not rerun and records are not dropped. Earlier wire requests were paired when submitted; reconciliation changes retained history/future invocations, not already submitted wire bytes. |

No new numbered finding remains. The current three-path repair resolves the native malformed-name regression while retaining the two original repairs. Baseline failures and residual boundaries below are explicit evidence limits, not new remediation proposals.

## Criterion and original task mapping

| Criterion | Result | Source | Independent evidence | Assessment |
|---|---|---|---|---|
| WS05-AC01 | PASS | S1,S3,S9,S13 | E1,E2,E6,E9 | Shared DTO and optional sizes/codes; old/native four-field and absent-provenance shapes; all 12 sources type-check; built dependency/import roundtrip. |
| WS05-AC02 | PASS | S4-S8 | E1-E4 | Exact original peer names/arguments execute. MCP record, request/history, prose/reasoning, pending/raw capture, logs/repr, new session and exports exclude synthetic keys/values/launch material; actual config unchanged. |
| WS05-AC03 | PASS | S4,S6-S8 | E1,E6 | Complete UTF-8 envelope caps: exact110, oversize, Unicode/entity/normalization growth, empty and tiny cap1 before RPC; direct/loop plus both actual turn modes; no false execution record. |
| WS05-AC04 | PASS | S4,S6 | E1,E6 | Explicit high-risk block/drop/log-off, full retained-prefix normalization/scan; offset210000 attack under cap300000 blocked; marker escape, partial/encoded echoes; static sanitizer rejection without raw samples/quarantine. |
| WS05-AC05 | PASS | S1,S2,S4,S6 | E1,E2 | isError=true, malformed flag/content, RPC/transport/timeout and sanitizer rejection produce safe accurate typed codes; cancellation propagates; same public cleanup owner retries/restarts. |
| WS05-AC06 | PASS | S4-S7,S9 | E1-E5 | Two peers/repeated names, concurrent8 atomic calls, missing/invalid/duplicate IDs, later native claims including replacement reuse and pending fallback; native IDs unchanged and coherent distinct MCP IDs without rerun. |
| WS05-AC07 | PASS | S8,S9 | E1,E2,E9 | Fake/production SQLite safe records, typed call/result roundtrip and actual entry IDs; six adapter and five strict-pair negatives reject before entry write; native/context-log shapes remain compatible. |
| WS05-AC08 | PASS | S9-S12 | E1,E4,E6 | JSONL full provenance and metadata on/off; Markdown default-off/opt-in; CSV existing columns and bounded200 summaries; controls/markup escaped; all-session entry/session files checked separately. |
| WS05-AC09 | PASS | S5-S8 and unchanged accepted runtime/selection sources | E1,E2,E6,E7 | Native/no-MCP both modes, exact WS04 retrieval6432 with floor50/reserve40 and accepted selection tests; real public WS02/03 owner/registry cleanup; no dedicated long-term ingestion, telemetry or later-phase source addition. |
| WS05-AC10 | PASS | complete aggregate and S13 | E1-E10 | Exact allowed 24 implementation paths; all19 commands independently run with explicit reproduced baselines; real local stdio, full source/test/dependency review, historical integrity and start/closeout freeze. |
| REM006-AC01 | PASS | S8,S10,S12 | E1,E4 | Original/remediation-base snapshot+JSONL(on/off)+all-session CSV leaks reproduced; new candidate snapshots/all7 export forms safe, env/header/launch execution audited exact and config unchanged. |
| REM006-AC02 | PASS | S4,S5,S7-S9 | E1,E4 | Reviewed product later-native reuse fails persistence; candidate adds durable entry, reconciles request/result/record/facts and preserves native IDs. Eight mode/adapter/fallback combinations independently pass. |
| REM006-AC03 | PASS | S1-S12 | E1,E2,E6 | Strict pairing/correlations preserved, native/old shapes, both modes/pending captures, caps/security/failures/cancellation and accepted WS04 selection/budget reconfirmed. |
| REM006-AC04 | PASS | complete remediation diff | E7,E8 | Exactly eight implementation paths; no dependency/config/shared-source drift in remediation, broad suppression, historical DB edit, argument hash or real secret copy. |
| REM006-AC05 | PASS | request and all review ranges | E1-E10 | Complete commands/reproductions/public cleanup/freeze/preservation are reproducible and fully archived; original failures retained distinctly. |
| REM006-AC06 | PASS | fresh VAL013 current request replaces historical VAL012 label | E1-E10 | Fresh read-only exact delta plus complete WS05 aggregate closes both High findings; no newly violated requirement established. |
| REM007-AC01 | PASS | S5:94-110,128-134 | E3,E5 | dict/list × flat/function × present/missing ID × native-only/mixed; skip invalid calls, execute valid following native/MCP, preserve native IDs. Eight failure-threshold controls remain exact. |
| REM007-AC02 | PASS | S4-S12 | E1,E2,E4,E6 | Both original findings remain closed; ID reservation/reconciliation/pairing/storage/privacy/caps/security/failure/cancellation and WS04 controls reconfirmed. |
| REM007-AC03 | PASS | complete followup diff | E7,E8 | Exactly loop.py, existing security test and existing REM006 report change; original authorities/review archives, all978 current product bytes and five unrelated fingerprints match freeze. |
| REM007-AC04 | PASS | all three complete ranges and frozen request | E1-E10 | All mandatory commands and public/package reproductions complete; fresh stable-candidate read-only delta then complete original aggregate assessment leaves no mandatory violation. |

| Original task | Result | Source | Criterion/evidence | Implemented behavior |
|---|---|---|---|---|
| MCP-05-01 | PASS | S1,S3 | WS05-AC01,06;E1/E2/E6 | Shared public immutable provenance after four legacy fields; sizes/status/truncation/trust/source/IDs validated. |
| MCP-05-02 | PASS | S4,S7,S8 | WS05-AC02;REM006-AC01;E1/E2/E6 | Directive narrows tactical redact-or-hash to empty arguments, no hashes. New snapshots omit MCP stanza, runtime config/dispatch preserved. |
| MCP-05-03 | PASS | S4,S6-S8 | WS05-AC03;E1/E2/E6 | Bound complete final UTF-8 model/persisted envelope before return; impossible tiny cap fails before execution. |
| MCP-05-04 | PASS | S4,S6 | WS05-AC04;E1/E2/E6 | Normalize/check whole retained prefix, explicit block/drop/log-off, escape wrappers and redact transient echoes. |
| MCP-05-05 | PASS | S4-S7 | WS05-AC05,06;E1/E2/E6 | Atomic per-call facts, coherent safe unique IDs and preserved exact source metadata across async/concurrent/mixed iterations. |
| MCP-05-06 | PASS | S8-S10 | WS05-AC07,08;E1/E2/E6 | Actual entry correlated paired DTOs persist in existing SQLite schema and full JSONL roundtrip. |
| MCP-05-07 | PASS | S9,S11,S12 | WS05-AC08;E1/E2/E6 | Markdown provenance default-off/opt-in; CSV provenance in existing bounded JSON columns; safe controls/markup. |
| MCP-05-08 | PASS | S1,S2,S4,S6 | WS05-AC05;E1/E2/E6 | Fixed safe failure/blocked codes, redacted records/logs/repr, propagated cancellation and public retry ownership. |

Public probes use real synthetic local stdio RPC with accepted public provider/bridge/ToolLoop/TurnProcessor and fake model/memory or production SQLite. Peer audits confirm exact original names and supported arguments/env/header-like launch material without copying real secrets. The accepted strict stdio config has no HTTP-header field; no HTTP/SSE config authority is added. Both actual turn modes/fallback and raw capture were exercised. DTO/adapter rejection tests enforce empty MCP arguments, checked bounded output, correct ID/name/size, equal paired facts and actual entry correlations. Native IDs/arguments/output remain exact.

E1 records `snapshot_and_exports_safe:false` for fake-adapter cases as the original script's `bool(production)` applicability marker; fake adapters have no stored sessions/export API. This is not a failed privacy assertion. All production cases assert snapshot and export absence and record true. Fake records and raw capture are checked independently.

Every peer-owning reproduction settles/cancels/joins tasks and drains/kills/reaps children in guaranteed pytest fixture teardown or `finally`, including initial failed assertions. Public cleanup is asserted separately before defensive teardown: empty published metadata/owned names/connections, reaped children and EOF pipes. Obstructed public cleanup leaves the same provider/manager reachable, and retry/restart succeeds (E2); defensive cleanup is not credited as a public pass. No live provider, real credential, network/paid service or external effect was used.

## Required commands and baseline distinction

All19 request commands ran independently. E6 and each complete log retain exact command/env/cwd/exit/output; no errors were filtered and no ignore or broad typing suppression was added. Common request environment: `LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache UV_NO_SYNC=true UV_OFFLINE=true PYTHONDONTWRITEBYTECODE=1`. Additional cache controls `PYTEST_ADDOPTS=-p no:cacheprovider`, scratch `MYPY_CACHE_DIR` and `RUFF_CACHE_DIR` prevent workspace cache writes. Required source typing is unfiltered Python3.13 over all12 source paths.

| # | Executed required command scope | Exit | Full result | Complete log |
|---|---|---|---|---|
| 01 | Focused12 targets | 0 | 248 passed | [log](VAL-013-evidence.tar.gz#logs/command-01.log) |
| 02 | Full Chat | 1 | 591 passed,5 skipped,1 warning;1 PTY failure+3 localhost setup errors (baseline) | [log](VAL-013-evidence.tar.gz#logs/command-02.log) |
| 03 | Transcript | 0 | 34 passed | [log](VAL-013-evidence.tar.gz#logs/command-03.log) |
| 04 | Agent | 0 | 209 passed,10 warnings | [log](VAL-013-evidence.tar.gz#logs/command-04.log) |
| 05 | Core+MCP+Runtime | 0 | 416 passed | [log](VAL-013-evidence.tar.gz#logs/command-05.log) |
| 06 | Memory | 0 | 680 passed,1 skipped,1 warning | [log](VAL-013-evidence.tar.gz#logs/command-06.log) |
| 07 | Integration | 1 | 77 passed; board22/23 expectation failure (baseline) | [log](VAL-013-evidence.tar.gz#logs/command-07.log) |
| 08 | Required Ruff scope | 0 | All checks passed | [log](VAL-013-evidence.tar.gz#logs/command-08.log) |
| 09 | Default five-package mypy | 2 | Installed NumPy __init__.pyi:737 type-statement syntax under Python3.10 target (baseline) | [log](VAL-013-evidence.tar.gz#logs/command-09.log) |
| 10 | Unfiltered Python3.13 all12 changed SOURCE files | 0 | Success: no issues found in12 source files | [log](VAL-013-evidence.tar.gz#logs/command-10.log) |
| 11 | uv lock --check --offline | 0 | 208 packages resolved; lock current | [log](VAL-013-evidence.tar.gz#logs/command-11.log) |
| 12 | Board validate | 0 | 23 tasks valid | [log](VAL-013-evidence.tar.gz#logs/command-12.log) |
| 13 | Board render --check | 0 | Current | [log](VAL-013-evidence.tar.gz#logs/command-13.log) |
| 14 | Documentation lifecycle | 0 | 356 Markdown files checked | [log](VAL-013-evidence.tar.gz#logs/command-14.log) |
| 15 | Full aggregate git diff --check | 0 | No whitespace errors | [log](VAL-013-evidence.tar.gz#logs/command-15.log) |
| 16 | Working product/config/tests vs frozen candidate | 0 | No differences | [log](VAL-013-evidence.tar.gz#logs/command-16.log) |
| 17 | All five working reports vs frozen candidate | 0 | No differences | [log](VAL-013-evidence.tar.gz#logs/command-17.log) |
| 18 | Complete REM006 git diff --check | 0 | No whitespace errors | [log](VAL-013-evidence.tar.gz#logs/command-18.log) |
| 19 | Followup git diff --check | 0 | No whitespace errors | [log](VAL-013-evidence.tar.gz#logs/command-19.log) |

Original-source baseline reproduction uses an exact `git archive` of `a609f948fe2d869ac29d0cce29d22d9334cd7d08`, original `packages/*/src` PYTHONPATH and the existing environment without sync. [import proof](VAL-013-evidence.tar.gz#logs/baseline-imports.log) identifies archived Chat/Core/Transcript imports. A read-only original tracked-file catalogue answers only the documentation checker's exact `git ls-files --cached --others --exclude-standard` query; other Git calls delegate unchanged. Exact commands/environment/exits are in the per-baseline JSON records and scripts.

| Nonzero required gate | Independently reproduced original-source result | Attribution and remaining limit |
|---|---|---|
| Full Chat PTY |479 passed,5 skipped, same reorganization early-acknowledgement assertion at test_reorganization_terminal.py:113; exit1 |Unchanged test bytes and behavior. Existing terminal acknowledgement failure remains, not attributed to WS05. |
| Three Chat localhost fixtures |Same `PermissionError` at test_llm_adapter_migration.py:341 during127.0.0.1 bind before adapter behavior; included in original Chat exit1 |Environment restriction. These three HTTP wire tests are not verified by this restricted run; stdio UAT passes separately. |
| Integration board count |Corrected whole original integration:69 passed,1 failed, exit1. Same test_development_board.py:75 expects22 while board validates23. |Unchanged expectation source; board validate/render themselves pass. No board/test fix authorized or applied. |
| Default five-package mypy |Exit2, same installed NumPy __init__.pyi:737 Python3.10-target type-statement syntax |Default broad typing stops before useful project coverage. Mandatory Python3.13 all12 changed source typing passes. Historical four profiles.py errors are not asserted present or used as a waiver. |

Baseline full logs: [Chat](VAL-013-evidence.tar.gz#logs/baseline-chat.log), [default typing](VAL-013-evidence.tar.gz#logs/baseline-mypy.log), E10 corrected whole integration. E7 proves the failing PTY/HTTP/board/docs test source hashes equal original/candidate. No candidate failure was excused by a scratch error: initial archive baseline missed AGENTS.md, causing one scratch-only documentation-link failure; exact original AGENTS bytes restored in scratch and whole integration rerun to69 passed/only board failure. The initial log remains archived. Newly authored matrix first incorrectly expected ToolLoop to append tool-result messages (TurnProcessor owns that step):8 failed/16 passed; assertions corrected to ToolLoop's request/record contract and all24 rerun pass. Original script/log retained. No product fix or assertion suppression occurred. An optional host `ps` inventory attempted during packaging was sandbox-denied; it is not claimed or needed for the separately asserted owned-child returncode/EOF and fixture task settlement evidence.

## Mandatory offline package boundary check

Cached tools built Telemetry,Core,Transcript wheels independently from exact candidate archive, all exit0. Tools:Python3.13.10,uv0.11.3 (Homebrew2026-04-01 aarch64-apple-darwin) in `package-tools.log`, built WHEEL Generator hatchling1.32.4; pytest9.0.2,mypy1.19.1,ruff0.14.10. Complete exact commands/flags are E9; [environment and wheel tool versions](VAL-013-evidence.tar.gz#probes/environment.json) records versions. Transcript built Requires-Dist includes `friday-framework-core==0.1.0a2`; Core requires Telemetry==0.1.0a2, Telemetry has no reverse framework edge. Transcript pyproject/lock change is only the Core edge (two lock entries); no cycle or undeclared repository dependency.

Clean `uv pip install --offline` into a new venv returned1 because pydantic-settings was unavailable in that cache. This is explicitly **not** a successful clean offline resolver/install claim. Required isolated import was completed successfully: new venv Python `-I`, three extracted built wheels plus only recursively declared/marker-selected/version-validated third-party distributions copied into a fresh directory, no editable `.pth` hooks or repo paths. Imported Core/Telemetry/Transcript `__file__` paths are all under extracted wheels. Public SQLite and all exporters import and a typed paired TranscriptEntry JSON roundtrip passes, exit0 ([complete isolated import](VAL-013-evidence.tar.gz#logs/package-isolated-import.log)).

Declared closure: pydantic-settings2.15.0,pydantic2.12.5,structlog25.5.0,aiosqlite0.22.1,python-dotenv1.2.1,typing-inspection0.4.2,annotated-types0.7.0,pydantic-core2.41.5,typing-extensions4.15.0. Metadata requirements/markers/versions and every copied third-party file hash are retained in [dependency proof](VAL-013-evidence.tar.gz#declared-dependencies.json); built framework wheel hashes and raw metadata are [wheel proof](VAL-013-evidence.tar.gz#wheel-metadata.json). This proves the mandatory built-wheel imports/roundtrip without editable support while retaining the separate cache limitation.

## Impact, residual boundaries and handoff

Public DTOs gain optional additive execution sizes/codes and optional transcript provenance; old/native constructor/input/serialization shapes tested unchanged. Older strict consumers reading newly enriched MCP JSON may require a reader update; no SQLite schema or stored-database migration is included. JSONL's existing metadata flag semantics remain, including session snapshot export when entry metadata is disabled. Prevention removes the entire MCP stanza only from **new** session snapshots; historical snapshots and their exports remain unchanged. Any historical cleanup requires separate authority.

No runtime config/default/example, native mandatory protocol, selection implementation, shared sanitizer, standalone transport policy, dedicated MCP long-term memory ingestion, telemetry emission, HTTP/SSE/resources/prompts/live refresh or later work-unit feature changed. Ordinary conversation memory remains on its existing path. Complete UTF-8 result bounds do not claim total input allocation/token budgeting; known-pattern sanitation and transient argument-echo redaction do not claim universal secret/injection detection.

Residual gates are explicit maintainer WS05 acceptance; WS06/07/08, full initiative pre-merge aggregate, live UAT and push/merge/release/delivery retain separate authority. Existing PTY acknowledgement/board expectation/default broad typing failures remain explicit; three localhost tests need an environment permitting bind; clean offline installation needs cached declared packages. None is silently fixed or promoted to a pass. No second-remediation-cycle unresolved product finding was found.

The evidence archive retains complete original/adapted/new scripts, full logs/exit/environment records, pinned inputs/history, complete diffs/source/test bytes, synthetic peer audits and built wheels. Runtime DBs/cache/venvs/state and real secrets are excluded. Artifact manifest records every archive member SHA256/size; delivery and archive verification record report/manifest/archive/delivery hashes and bytes outside the archive to avoid self-referential hashes. All portable evidence locators, member hashes/sizes, Markdown table structure, trailing whitespace and exactly one report EOF newline are verified before handoff. The controller may archive this report byte-for-byte; this validator changed no governed artifact.
