# VAL-009 independent review

## Decision

| Review mode | Outcome | Basis |
| --- | --- | --- |
| `delta` | **VERIFIED** | All six approved REM-005 criteria satisfied; both public collision variants independently reproduced with distinct, retained, bounded source records. Exact eight-path correction boundary confirmed. |
| `work_unit_aggregate` | **VERIFIED** | All ten WS-03 criteria satisfied on the complete original work-unit aggregate, including accepted WS-00/01/02 and REM-003/004 interactions. |

**Overall outcome: VERIFIED.**

Findings: none. No candidate defect, unmet authorized criterion, missing required check or frozen-input drift was confirmed. Required failing commands remain failures; independently established predecessor failures are separated below and are neither repaired nor waived. This decision is verification of the frozen candidate, not maintainer acceptance, approval of later workstreams, a complete feature-branch pre-merge review or delivery authority.

## Identity, independence and scope

- Review date: `2026-09-28`. Available reviewer model identity: Codex, based on GPT-6. The exact deployed model name/build/version is not exposed to this reviewer session and is unavailable.
- Reviewer: newly dispatched `/root/mcp_ws03_val009`, fresh context, no further delegation. Formal work began only after controller GO on stable dispatch HEAD. No parent, builder or remediator sessions/private reasoning were read. Candidate and historical reports were read as repository inputs; their conclusions and archived executions were not adopted as independent passing evidence.
- Workspace: `/Users/chuckrussell/Dev/gendev/agent-framework`; branch `feature/friday-mcp-ws03-registry`; stable dispatch/closeout HEAD `9d6df3408279eb58347b1d7be26543d292ce6576`.
- Candidate/authority revision: `d395acdba9e233cb226f54e6258575f480157cf1`; previous candidate `397caa9898612cd989f6404951b3e1f5005dfac2`.
- Request: `docs/planning/active/friday-mcp/validation/VAL-009-request.yaml`, frozen commit `34a457a540ca5e092c332431c824a537dcf7a8b0`, SHA256 `15d4ca5ebbacd828b3b918ca2e6b409e42cd2862042a09062dce07ff23b6e715`.
- WS-03 base `2c0d6bd1fe481fff9bb180f9e6dfb4a9a2131641`, approval `b54069654bb3e21a6265fbabcd23f6991e286ab0`; accepted predecessor `a257f041d1d68f8aea2f5b9773df1b88acd82379`.
- REM-005 authorization/bounded base `215e54de71eda08067d22695d0062f7bed35e9d0`.
- All 22 pinned authority documents, the entire request and both frozen implementation reports were read completely. Complete requested diff contents were inspected, including authority/controller changes and lossless historical evidence; all compressed historical logs were decoded/read, and all 33 historical artifact byte-length/hash pairs matched their manifest. Those artifacts were not executed as this review's probes.
- Read-only governed workspace: no source, test, configuration, report, authority or process edits; no staging, commits, fixes, branch cleanup, external messages, credentials, live MCP/model/provider/network calls or delivery. All new evidence, probe fixtures, logs and reports were written under `/private/tmp/val009-20260928`.

Three complete exact diff artifacts are preserved:

| Mode | Exact range | Changed paths | Artifact |
| --- | --- | ---: | --- |
| Full delta | `397caa9898612cd989f6404951b3e1f5005dfac2..d395acdba9e233cb226f54e6258575f480157cf1` | 50 | [delta_diff_range.diff](VAL-009-evidence.tar.gz#delta_diff_range.diff) |
| Bounded correction | `215e54de71eda08067d22695d0062f7bed35e9d0..d395acdba9e233cb226f54e6258575f480157cf1` | 8 | [bounded_remediation_diff_range.diff](VAL-009-evidence.tar.gz#bounded_remediation_diff_range.diff) |
| Original work-unit aggregate | `2c0d6bd1fe481fff9bb180f9e6dfb4a9a2131641..d395acdba9e233cb226f54e6258575f480157cf1` | 62 | [aggregate_diff_range.diff](VAL-009-evidence.tar.gz#aggregate_diff_range.diff) |

The bounded correction is exactly the approved two runtime source files, two runtime test files, integration registry test, fake-peer fixture and two implementation reports. It contains 853 insertions/12 deletions. The full delta also contains approved REM-005/controller relocation and immutable VAL-008 evidence archival. The original aggregate contains the seven approved product source paths, eight changed test/fixture paths and the implementation reports, plus authority/controller artifacts. Original WS-03 implementation before REM-005 changed 16 paths within its 17-path allowlist; the approved lifecycle test path was unchanged. No native registry implementation, dependencies, configuration defaults, protocol normalizer, base/manager/stdio transport, security module or later-slice product paths changed. Candidate-to-dispatch-HEAD differences are only seven controller request/status/index/queue/log/board documents, independently inspected; they do not alter frozen product/report/authority inputs.

## REM-005 criterion evidence

Source anchors below refer to the frozen candidate. Probe names identify the executable independent harness and full evidence table below; required checks identify the numbered exact-command table.

| Criterion | Independent assessment and evidence | Result |
| --- | --- | --- |
| REM-005-AC-01 | Frozen `MCPOriginalNameSummary`, `MCPCollisionSource`, `MCPNameCollision` and additive optional `MCPRegistrationDecision.collision` at `mcp_registration.py:97–195`; whole-handoff bound/JSON/normalization admission precedes source construction, preflight at line 456 precedes sanitation/filtering/insertion. `real_collision_matrix` independently used actual public `RuntimeKernel` and stdio peers for same-peer `Read.File`/`Read-File`; records preserve the safe canonical ID, both configured MCP identities and distinct summaries/fingerprints after public failed-start cleanup. `real_cross_peer` independently reproduced `peer_one`/`Read.File` versus `peer`/`one.Read-File` ambiguity with both safe server IDs. Checks 1–2 pass. | PASS |
| REM-005-AC-02 | `prepare_registration` checks native names before any registry insertion and emits native-first/MCP-second typed records without introspecting native internals. Public stdio `real_collision_matrix` includes MCP/native both default-selected and excluded-category cases; native descriptor has `provider='native'`, null server/summary; MCP descriptor has `provider='mcp'`, safe `peer` and summary. All existing native registry objects remain identical by `is`, no MCP tool/sidecar is published, public kernel/provider are inspectable after cleanup. | PASS |
| REM-005-AC-03 | Provider lifetime contract at `mcp_loading.py:86`, failed-preflight capture at line 156, new-attempt reset at line 326, stop at line 561. Optional/default zero selection, explicit selected and both name/category exclusion collisions all remain fatal. `real_collision_matrix` retains the same decision tuple across successful public cleanup and repeated stop. `diagnostic_attempt_reset` verifies obstructed prior-owner cleanup retains history, a new discovery attempt replaces it and a no-op start preserves it. `optional_failure_attempt_reset` verifies the new optional failure clears current collision history while previously obtained immutable snapshots remain valid. | PASS |
| REM-005-AC-04 | Field validators bound safe server ID/canonical ID to 64; length string is decimal through 9999 then `9999+`; shape masks only first 24 characters to `[a0_.?-]`; fingerprint is 12 lowercase hex digits of SHA256 over the complete admitted original UTF-8 with `surrogatepass` for escaped lone surrogates. `pure_filters_diagnostics`, `real_unusual_names`, `same_shape_fingerprint` cover large, control/zero-width, entity-encoded and escaped-surrogate originals. Same-first-24/length originals differ by full-original fingerprint. Nested records reject mutation; diagnostic repr stays below 1000 bytes in probe pairs and contains no catalog sentinel/raw original. Static public errors and captured DEBUG logs contain no raw original/catalog/schema/stdout/stderr/argument/environment/exception sentinel. Noncolliding surrogate-bearing original is rejected by export admission. | PASS |
| REM-005-AC-05 | Old three/four positional `MCPRegistrationDecision` constructors remain valid with `collision=None`; binding reasons/codes unchanged. Collision descriptors do not invent two rejected decisions/counters: public same-peer failure reports discovered 2, selected/registered/filtered 0, rejected 1; native collision reports discovered 1/rejected 1. `real_late_counts` verifies discovered/selected/registered/rejected/filtered `4/1/1/2/1` for mixed WS-02/late WS-03 rejection. Full routing, final-export costs, sidecar, transaction, retained owner, cancellation/noisy settlement probes pass. Checks 1, 2, 4, 6, 9 and governance checks pass; predecessor baseline separation is documented below. | PASS |
| REM-005-AC-06 | Exact bounded eight-path set equals request allowlist; approval directive hash equals authorized-commit blob and candidate/working content. No mandatory protocol/config/dependency/private native-registry change. New diagnostics are typed/frozen; no new broad typing ignore. Both reports accurately describe bounds, additive constructors/serialization implications, retention/reset semantics, counters, non-goals and unchanged baseline debt. All 17 checks ran, including core-inclusive failures without filtering/waiver; exact Ruff and meaningful 45-file typing pass. | PASS |

## WS-03 aggregate criterion evidence

| Criterion | Independent assessment and evidence | Result |
| --- | --- | --- |
| MCP-03-AC-01 | Existing core normalizer remains authoritative and unchanged: accepted safe prefix/server/original normalization, lowercase canonical naming and 64-character maximum apply at preflight; empty/oversized/canonical-overflow originals are rejected. `real_routing_cost_sidecar` registers two real stdio peers with the same original `Read.File` under different canonical IDs; calling actual native-registry callable wrappers routes to the correct peer, exact original `Read.File`, and identical nested argument dictionary. Each peer sees one discovery call; no-op start and public restart preserve correct behavior. Legacy adapter naming remains compatible. Checks 1–2 include accepted core normalization contracts. | PASS |
| MCP-03-AC-02 | Complete prepared-catalog collision preflight is before filters and before insertion, so zero/default selection and excluded entries cannot hide MCP/MCP or MCP/native conflicts. Same-peer, cross-peer and native public variants independently pass. Static errors, immutable typed both-source evidence, native identity preservation and retained public diagnostics are detailed above. Successful first contenders are not inserted when a later collision aborts. | PASS |
| MCP-03-AC-03 | `core.mcp.py` additive metadata cost/state/count fields and frozen read-only index; provider `tool_metadata` returns an immutable mapping and `MCPToolMetadata` snapshots. Sidecar exact canonical key set matches owned registered MCP entries, excludes native entries and preserves configured server, original routing name, trust, transport, discovery/filter/sanitization state and complete byte cost. `real_routing_cost_sidecar` checks mapping assignment refusal and every metadata cost against registry plain/OpenAI exports; `pure_cost_mutation` checks input/adapter snapshot isolation. `real_late_counts` proves mixed pre/post-admission counts without double counting. Existing metadata constructors retain defaults and original-name repr suppression. Trusted registry exports remain mutable under the approved boundary. Checks 1–2 pass. | PASS |
| MCP-03-AC-04 | `_selected` at `mcp_registration.py:440` implements all/selected, category/name inclusion union and exclusion precedence. All-mode category restrictions, explicit name overrides, selected category opt-in, default-selected zero, name exclusion and category exclusion independently tested with spoofed peer category/tag input; admitted exports remain category/tag `mcp`. `real_caps_strict_includes` proves explicit missing/excluded includes fatal even with optional peers. Preflight collision ordering is unaffected by those filters. Checks 1–2 pass. | PASS |
| MCP-03-AC-05 | WS-02 discovery limits remain unchanged upstream; WS-03 applies final total/per-peer count and full export/aggregate byte-equivalent token caps deterministically without repeated list/backfill. `exported_definition_size` at line 243 charges maximum compact JSON bytes of complete plain and OpenAI exports including canonical name, description, parameters, category/tags and nesting. Pure fixture raw definition 124 bytes versus final export 195 bytes: a cap that fits raw+1 but not export admits nothing; aggregate budget equal to two final exports minus one admits only first. Public actual registry exports agree with sidecar costs. Upstream cap of two plus exclusion of first admits only second, never backfills third; one list call. Checks 1–2 pass. | PASS |
| MCP-03-AC-06 | Complete raw definition bound, JSON finiteness/shape, conservative supported inline schema keyword validation, annotation-only sanitation and unsafe semantic-text rejection at registration lines 251–439. Traversal is bounded to depth 32 and 4096 visited nodes, including object keys. Exact safe scalar/numeric/object/array/boolean/combinator constraints preserve semantics; unsupported/external/local refs are rejected rather than resolved. Eight encoded/control/zero-width/comment/role-delimiter attack forms tested in annotations (redaction) and property/default/enum semantics (rejection); 24 malformed/unsupported cases fail closed. Deep 34-level, 4100-node and attack after 500 valid properties fail, so early content truncation does not bypass validation. Original bounds, input/adapter repr safety and mutation isolation tested. Schema keyword/depth/node limits are deliberate compatibility limits, not universal semantic support or proof of all prompt-injection prevention. Checks 1–2 pass. | PASS |
| MCP-03-AC-07 | Adapter supplies the complete `ToolDefinition` runtime protocol (`name`, description, schema, category/tags, callable execution and plain/OpenAI exports), with frozen validated JSON snapshots and defensive returned containers. `pure_cost_mutation` runtime-checks protocol and legacy constructor `old_Legacy.Name`; existing adapter API tests pass. Public `RuntimeKernel` uses actual `DefaultToolRegistry`, actual registry callable and local stdio `MCPClient` routing, rather than direct adapter-only invocation. Native registry tests pass. Native suite's two unchanged invalid-ZIP fixture failures are independently reproduced and separated below. | PASS |
| MCP-03-AC-08 | `di.py:123` registers MCP tools/metadata after native registry construction and before agent bindings; `kernel.py:112` applies bindings after successful publication; safe optional `MCPBindingContext` reaches tool loading. `real_binding_publication` witnesses owned registry/sidecar available when real binding builder runs, then a genuinely missing native profile fails with its prior native error and public cleanup removes MCP tools. Core/native/disabled/empty/autoconnect-off and safe known-MCP missing reasons covered by complete affected tests, old binding-context probe and source review; Chat compatibility 46 tests pass. Native missing names retain prior behavior; no new mandatory context parameter. | PASS |
| MCP-03-AC-09 | Transaction ownership uses only public registry methods, records insert-then-raise/cancel before unwind, removes only identical owned objects, preserves native identities and retains public registry/metadata ownership when rollback refuses. Five independent actual-registry fault modes cover before insert, after insert, cancellation, unregister refusal and changed final export; public stop retries recover. Sidecar/model-visible entries are unpublished before disconnect wait/failure/cancel. Retained-provider and public-kernel failure/retry probes prove the same provider/manager owner stays reachable, successful peers drain, obstruction prevents owner replacement, removing obstruction permits public stop/restart. Real noisy stdio optional and required discovery failures settle with ignored SIGTERM and >1 MiB stderr/unterminated stdout at ~5.02 seconds; successful noisy registered peer cancellation propagates and subsequent public stop completes. Actual process exit, both pipe EOFs and no new unfinished tasks are asserted before defensive teardown. REM-003 cancellation and REM-004 noisy shutdown tests are included in all 459 affected passes; production cleanup budgets unchanged. | PASS |
| MCP-03-AC-10 | Complete allowed product/test/report scope and all controller authority changes reviewed. No dependencies, defaults, external effects, broad ignore or unauthorized later-slice implementation. Ruff passes; affected runtime/MCP plus integration 45-file Python 3.13 check passes. Unfiltered core-inclusive typing baseline is independently reproduced with a fresh full-core cache; default mypy explicitly prevents further project checking. Both implementation reports and approved authority hashes stable. Documentation describes public diagnostic lifecycle, conservative sanitizer/byte costs, additive DTOs/serialization and remaining gates accurately. Board/render/lifecycle checks pass. | PASS |

## Public collision reproduction and privacy bounds

After actual public failed `RuntimeKernel.start()` cleanup, `kernel.mcp_provider.registration_decisions` retains the typed last collision. Same-peer canonical name `mcp_peer_read_file` has first MCP server `peer`, length `9`, shape `aaaa.aaaa`, fingerprint `965778ac841a`; second MCP server `peer`, length `9`, shape `aaaa-aaaa`, fingerprint `ae6cb96ad30d`. The configured server is safe; neither record stores `Read.File` or `Read-File`. Native collision has the same canonical name, first native/null/null, second MCP/`peer`/the first summary. All native registry objects remain exact original objects; no wrapper or sidecar entry survives abort. Calling public stop again preserves that tuple. These are the independent reproductions of both F-001 variants, not readings of the candidate test assertions.

Cross-peer ambiguity (`peer_one` + `Read.File`, `peer` + `one.Read-File`) retains different configured safe server IDs. The summaries are deliberately lossy and bounded. 20,000-character punctuation originals, entity/control forms and escaped lone-surrogate names cannot create unbounded/unsafe diagnostic text. Two originals sharing the first 24 masked characters and `9999+` length still have distinct hashes of the complete originals; the hash is a 48-bit diagnostic discriminator, not collision-proof provenance or a secrecy guarantee. Escaped surrogate summarization permits reporting a collision before later export admission; the noncolliding surrogate case is rejected. No raw original-name field or peer-content/exception/output/argument/environment sentinel appears in diagnostic repr/static errors/captured DEBUG logs in the probes; raw tested originals `Read.File`, `Read-File` and `&#83;` are absent from captured DEBUG logs. Accepted canonical IDs and configured IDs remain intentionally visible and can contain normalized portions of originals.

The snapshot's retention is last-attempt history: successful/failed stop does not erase it, and cleanup obstruction prevents discovery reset. A real new discovery attempt clears it after prior-owner settlement and workspace validation, including new optional discovery failure. A no-op start does not erase it. This precisely matches the documented contract; callers retaining an old frozen tuple keep a valid immutable snapshot.

## Independent adversarial harness and settlement

Executable fixtures: [probes.py](VAL-009-evidence.tar.gz#probes.py), [peer.py](VAL-009-evidence.tar.gz#peer.py), [supplement.py](VAL-009-evidence.tar.gz#supplement.py). Both harness commands completed exit 0 on their first executed candidate run. They use local catalog/registry/client doubles for bounded fault injection and an independently written line-oriented local stdio fake peer for public routing/collision/noisy lifecycle checks. Public runtime construction stubs only unrelated model/memory/storage/telemetry factories; actual kernel/provider/manager/client/stdio transport/native registry remain on the tested path. No production budgets are patched.

Every synthetic resource is handled in explicit `finally`: fixture-owned tasks cancel/join, cleanup controls release, public owner stop retries, and the defensive fixture fallback kills, incrementally drains both pipes and reaps every recorded synthetic process. Public success assertions run before defensive fallback and require public ownership/registry state, process exit/pipe EOF, closed stdin and no new unfinished asyncio task. A 13-second watchdog provides slack around the unchanged 11-second transport cleanup budget; emergency pipe drain/reap and canceled-task joins are individually bounded. The optional/required noisy cases and registered cancel/retry cases passed their public assertions without needing an otherwise-hidden saved client reference to make cleanup succeed.

The supplement deliberately injects a scratch `AssertionError` after starting a noisy registered real peer. The outer witness then confirms process reap, both pipe EOFs and no pending tasks after the fixture `finally`. This expected-control probe validates defensive harness settlement even when assertions fail; it is expressly not counted as public cleanup success. The supplemental error log lines are fixed `MCP disconnect failed`, with no injected exception sentinel. No accidental harness failure or cleanup leak occurred.

`all-probe-results.json` is the complete combined result manifest (26 groups), reconstructed from the two complete PASS logs. The small helper `probe-results.json` is replaced when `supplement.py` imports the main helper and records supplemental groups; it is not the complete-run manifest and no evidence is lost because both execution logs and combined manifest are preserved.


## Required commands, exact exits and results


All 17 request commands were independently run in the governed workspace. Recorded command strings below are exact; process-level `UV_OFFLINE=true` and `PYTHONDONTWRITEBYTECODE=1` were also supplied. Required local LiteLLM cost-map and UV-cache prefixes were retained. No error filtering, import-silent substitute or remote call was used. Wall seconds are subprocess elapsed times; pytest times are its own reported times. Twelve commands exited 0; five failed as explicitly recorded. Complete logs and structured records are preserved in [required-checks.json](VAL-009-evidence.tar.gz#required-checks.json).


| # | Exact command | Exit | Wall seconds | Result | Full log |
| --- | --- | ---: | ---: | --- | --- |
| 1 | `LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run pytest packages/friday-core/tests_core/test_mcp_contracts.py packages/friday-mcp/tests_mcp/client/test_adapter.py packages/friday-runtime/tests_runtime/test_mcp_registration.py packages/friday-agent/tests_agent/test_registry.py tests/integration/test_mcp_registry.py -q` | 0 | 8.077 | 173 passed in 5.82s. | [check-01.log](VAL-009-evidence.tar.gz#check-01.log) |
| 2 | `LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime packages/friday-agent/tests_agent/test_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/test_mcp_registry.py -q` | 0 | 54.288 | 459 passed in 52.22s; complete affected WS-00/01/02/03 and REM-003/004 regression targets. | [check-02.log](VAL-009-evidence.tar.gz#check-02.log) |
| 3 | `LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run pytest packages/friday-tools/tests_tools -q` | 1 | 12.735 | 233 passed, 2 failed, 1 warning in 11.82s. Same invalid-ZIP DOCX/XLSX fixtures as predecessor; baseline B1. | [check-03.log](VAL-009-evidence.tar.gz#check-03.log) |
| 4 | `LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run pytest packages/friday-chat/tests_chat/test_mcp_config_compatibility.py packages/friday-chat/tests_chat/compat/test_config_compatibility.py packages/friday-chat/tests_chat/test_llm_config_migration.py -q` | 0 | 2.199 | 46 passed in 1.39s. | [check-04.log](VAL-009-evidence.tar.gz#check-04.log) |
| 5 | `LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run pytest tests/integration -q --tb=short` | 1 | 50.964 | 69 passed, 1 failed in 50.02s. Board-count assertion expects 22, canonical output 23; baseline B2. | [check-05.log](VAL-009-evidence.tar.gz#check-05.log) |
| 6 | `UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run ruff check packages/friday-core/src/friday_core/mcp.py packages/friday-core/tests_core/test_mcp_contracts.py packages/friday-mcp packages/friday-runtime tests/integration/test_mcp_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py` | 0 | 0.040 | All checks passed. | [check-06.log](VAL-009-evidence.tar.gz#check-06.log) |
| 7 | `UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run mypy packages/friday-core packages/friday-runtime packages/friday-mcp` | 2 | 0.309 | Installed NumPy __init__.pyi:737 syntax unsupported under default Python 3.10 target; 1 error prevents further project checking. Baseline B3. | [check-07.log](VAL-009-evidence.tar.gz#check-07.log) |
| 8 | `UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run mypy --python-version 3.13 packages/friday-core/src/friday_core/mcp.py` | 1 | 0.216 | Exactly four untouched profiles.py no-any-return errors at 77/82/110/115; checked 1 root source file. Baseline B5. | [check-08.log](VAL-009-evidence.tar.gz#check-08.log) |
| 9 | `UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run mypy --python-version 3.13 packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py` | 0 | 0.931 | Success: no issues found in 45 source files. | [check-09.log](VAL-009-evidence.tar.gz#check-09.log) |
| 10 | `UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run mypy --python-version 3.13 packages/friday-core/src/friday_core/mcp.py packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py` | 1 | 0.792 | Exactly same four profiles.py errors; checked 46 root source files. Baselines B4/B5 and supplemental fresh-core run. | [check-10.log](VAL-009-evidence.tar.gz#check-10.log) |
| 11 | `UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run python scripts/friday-dev-board.py validate` | 0 | 0.075 | Development board validation passed: 23 tasks. | [check-11.log](VAL-009-evidence.tar.gz#check-11.log) |
| 12 | `UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run python scripts/friday-dev-board.py render --check` | 0 | 0.077 | Planning dashboard is current. | [check-12.log](VAL-009-evidence.tar.gz#check-12.log) |
| 13 | `UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run python scripts/check-documentation-lifecycle.py` | 0 | 0.215 | Documentation lifecycle validation passed: 342 Markdown files. | [check-13.log](VAL-009-evidence.tar.gz#check-13.log) |
| 14 | `git diff --check 2c0d6bd1fe481fff9bb180f9e6dfb4a9a2131641..d395acdba9e233cb226f54e6258575f480157cf1` | 0 | 0.013 | Clean original aggregate whitespace diff. | [check-14.log](VAL-009-evidence.tar.gz#check-14.log) |
| 15 | `git diff --exit-code d395acdba9e233cb226f54e6258575f480157cf1 -- packages tests pyproject.toml uv.lock` | 0 | 0.009 | Working packages/tests/configuration equal frozen candidate; no diff. | [check-15.log](VAL-009-evidence.tar.gz#check-15.log) |
| 16 | `git diff --check 215e54de71eda08067d22695d0062f7bed35e9d0..d395acdba9e233cb226f54e6258575f480157cf1` | 0 | 0.009 | Clean bounded remediation whitespace diff. | [check-16.log](VAL-009-evidence.tar.gz#check-16.log) |
| 17 | `git diff --exit-code d395acdba9e233cb226f54e6258575f480157cf1 -- docs/planning/active/friday-mcp/execution/REM-005-implementation-report.md docs/planning/active/friday-mcp/execution/WS-03-implementation-report.md` | 0 | 0.008 | Both working implementation reports equal frozen candidate; no diff. | [check-17.log](VAL-009-evidence.tar.gz#check-17.log) |



## Independently established predecessor baselines


Accepted predecessor `a257f041d1d68f8aea2f5b9773df1b88acd82379` was extracted read-only with `git archive a257f041d1d68f8aea2f5b9773df1b88acd82379 packages tests scripts docs pyproject.toml uv.lock AGENTS.md` into `/private/tmp/val009-20260928/predecessor`; no branch/worktree change. Runs use the existing `.venv/bin/python` at its original path (not its resolved interpreter symlink), same installed dependencies, local cost map, requested UV cache, offline flag and bytecode-disabled flag. For the two pytest runs only, `PYTHONPATH` is the exact sorted archived source path list below so editable imports load predecessor packages; warning source paths confirm archived imports. Mypy runs use the standard import environment with neither an added `PYTHONPATH` nor `MYPYPATH`, and explicit fresh scratch caches. This avoids a baseline changed by an artificial type-discovery environment. [baseline-results.json](VAL-009-evidence.tar.gz#baseline-results.json) records exact argv, cwd, test import paths, exits, times and logs.


Exact baseline process environment additions: `LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache UV_OFFLINE=true PYTHONDONTWRITEBYTECODE=1`. Cwd for every B command: `/private/tmp/val009-20260928/predecessor`. B1/B2 additionally use:


```text
PYTHONPATH=/private/tmp/val009-20260928/predecessor/packages/friday-agent/src:/private/tmp/val009-20260928/predecessor/packages/friday-chat/src:/private/tmp/val009-20260928/predecessor/packages/friday-cli/src:/private/tmp/val009-20260928/predecessor/packages/friday-core/src:/private/tmp/val009-20260928/predecessor/packages/friday-finance/src:/private/tmp/val009-20260928/predecessor/packages/friday-llm/src:/private/tmp/val009-20260928/predecessor/packages/friday-mcp/src:/private/tmp/val009-20260928/predecessor/packages/friday-memory/src:/private/tmp/val009-20260928/predecessor/packages/friday-moltbook/src:/private/tmp/val009-20260928/predecessor/packages/friday-optimization/src:/private/tmp/val009-20260928/predecessor/packages/friday-runtime/src:/private/tmp/val009-20260928/predecessor/packages/friday-sandbox/src:/private/tmp/val009-20260928/predecessor/packages/friday-speech/src:/private/tmp/val009-20260928/predecessor/packages/friday-telemetry/src:/private/tmp/val009-20260928/predecessor/packages/friday-tools/src:/private/tmp/val009-20260928/predecessor/packages/friday-transcript/src
```


| Baseline | Exact argv rendered as command | Exit | Wall seconds | Result | Full log |
| --- | --- | ---: | ---: | --- | --- |
| B1 | `/Users/chuckrussell/Dev/gendev/agent-framework/.venv/bin/python -m pytest packages/friday-tools/tests_tools -q` | 1 | 13.194 | 233 passed, 2 failed, 1 warning in 12.27s; exactly TestDocxReader::test_docx_reader_missing_dependency and TestXlsxReader::test_xlsx_reader_missing_dependency. Same assertions at test_filesystem_readers.py:286/306: “Failed to read DOCX: File is not a zip file” / “Failed to read Excel file: File is not a zip file”. | [baseline-1.log](VAL-009-evidence.tar.gz#baseline-1.log) |
| B2 | `/Users/chuckrussell/Dev/gendev/agent-framework/.venv/bin/python -m pytest tests/integration/test_development_board.py -q --tb=short` | 1 | 2.060 | 10 passed, 1 failed in 1.77s; same test_development_board.py:75 expects “22 tasks” and receives successful canonical “23 tasks”. | [baseline-2.log](VAL-009-evidence.tar.gz#baseline-2.log) |
| B3 | `/Users/chuckrussell/Dev/gendev/agent-framework/.venv/bin/python -m mypy packages/friday-core packages/friday-runtime packages/friday-mcp --cache-dir /private/tmp/val009-20260928/baseline-mypy-default` | 2 | 0.660 | Same NumPy __init__.pyi:737 Type statement only supported in Python 3.12+ syntax error under default target; further checking prevented. | [baseline-3.log](VAL-009-evidence.tar.gz#baseline-3.log) |
| B4 | `/Users/chuckrussell/Dev/gendev/agent-framework/.venv/bin/python -m mypy --python-version 3.13 packages/friday-core --cache-dir /private/tmp/val009-20260928/baseline-mypy-py313` | 1 | 2.619 | Same four no-any-return errors at profiles.py:77/82 (VectorStoreAdapter), 110/115 (GraphStoreAdapter); checked 32 source files. | [baseline-4.log](VAL-009-evidence.tar.gz#baseline-4.log) |
| B5 | `/Users/chuckrussell/Dev/gendev/agent-framework/.venv/bin/python -m mypy --python-version 3.13 packages/friday-core/src/friday_core/mcp.py --cache-dir /private/tmp/val009-20260928/baseline-mypy-py313` | 1 | 0.149 | Same four profiles.py errors with exact core MCP root; checked 1 root source file. | [baseline-5.log](VAL-009-evidence.tar.gz#baseline-5.log) |



Baseline classifications are established by these new predecessor runs, not by builder/remediator or historical reviewer reports. An additional exact diff verifies native tool source/tests, profiles.py, the board test, pyproject.toml and uv.lock are unchanged from accepted predecessor. Current fresh-cache full-core typing returns the same four errors; no new touched-source error is observed. The default-target typing command supplies no project type assurance because dependency syntax prevents checking. The passing 45-file run and source/annotation review supply narrower meaningful type evidence. Full required commands still fail with their exact original codes.


## Supplemental command evidence


| Check | Exact command | Exit | Result | Evidence |
| --- | --- | ---: | --- | --- |
| delta-whitespace | `git diff --check 397caa9898612cd989f6404951b3e1f5005dfac2..d395acdba9e233cb226f54e6258575f480157cf1` | 0 | Full delta whitespace clean. | [delta-whitespace.log](VAL-009-evidence.tar.gz#delta-whitespace.log) |
| unchanged-baseline-inputs | `git diff --exit-code a257f041d1d68f8aea2f5b9773df1b88acd82379..d395acdba9e233cb226f54e6258575f480157cf1 -- packages/friday-tools packages/friday-core/src/friday_core/profiles.py tests/integration/test_development_board.py pyproject.toml uv.lock` | 0 | No changes in declared baseline source/configuration inputs. | [unchanged-baseline-inputs.log](VAL-009-evidence.tar.gz#unchanged-baseline-inputs.log) |
| candidate-core-fresh | `LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache UV_OFFLINE=true uv run mypy --python-version 3.13 packages/friday-core --cache-dir /private/tmp/val009-20260928/candidate-core-fresh` | 1 | Same four profiles.py errors; checked 32 files; fresh cache, standard unfiltered import environment. | [candidate-core-fresh.log](VAL-009-evidence.tar.gz#candidate-core-fresh.log) |
| independent-probes | `LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache UV_OFFLINE=true PYTHONDONTWRITEBYTECODE=1 uv run python /private/tmp/val009-20260928/probes.py > /private/tmp/val009-20260928/probes.log 2>&1` | 0 | 21 independent groups PASS. | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| supplemental-probes | `LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache UV_OFFLINE=true PYTHONDONTWRITEBYTECODE=1 uv run python /private/tmp/val009-20260928/supplement.py > /private/tmp/val009-20260928/supplement.log 2>&1` | 0 | 5 supplemental groups PASS, including deliberate assertion-failure defensive settlement. | [supplement.log](VAL-009-evidence.tar.gz#supplement.log) |
| closeout-freeze | `PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/val009-20260928/freeze.py` | 0 | All start/closeout inputs identical; all pinned hash checks and candidate product/report comparisons pass. | [closeout.json](VAL-009-evidence.tar.gz#closeout.json) |



## All independent probe groups


Every group below completed PASS with no unexpected harness exception. Full logs preserve observations; [all-probe-results.json](VAL-009-evidence.tar.gz#all-probe-results.json) preserves nested descriptors, counts and other structured evidence. The two main commands and their exit codes are above.


| # | Executable group | Result | Recorded independent evidence | Log |
| --- | --- | --- | --- | --- |
| 1 | `pure_schema` | PASS | `{"safe_semantics":true,"annotations":8,"unsupported_and_malformed":24,"depth_nodes_late":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 2 | `pure_filters_diagnostics` | PASS | `{"filter_cases":6,"unusual_collision_pairs":5,"surrogate_rejected_without_collision":true,"immutable_summaries":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 3 | `pure_cost_mutation` | PASS | `{"raw_bytes":124,"final_bytes":195,"full_export_and_aggregate_caps":true,"input_adapter_snapshots":true,"legacy":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 4 | `transaction_before` | PASS | `{"native_identity":true,"public_cleanup":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 5 | `transaction_after` | PASS | `{"native_identity":true,"public_cleanup":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 6 | `transaction_cancel` | PASS | `{"native_identity":true,"public_cleanup":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 7 | `transaction_refuse` | PASS | `{"native_identity":true,"public_cleanup":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 8 | `transaction_export` | PASS | `{"native_identity":true,"public_cleanup":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 9 | `diagnostic_attempt_reset` | PASS | `{"obstruction_preserves":true,"new_attempt_clears":true,"no_op_retains":true,"old_snapshot_immutable":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 10 | `retained_provider_recovery` | PASS | `{"successful_peer_drained":true,"registry_removed_first":true,"owner_retained":true,"public_retry_recovers":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 11 | `real_collision_matrix` | PASS | `{"cases":6,"peer_native_distinct":true,"retained_after_cleanup":true,"exact_native_identity":true,"descriptors":"All six exact nested public descriptors in all-probe-results.json; both F-001 variants described above."}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 12 | `real_cross_peer` | PASS | `{"safe_ids":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 13 | `real_unusual_names` | PASS | `{"cases":3,"bound_and_fingerprints":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 14 | `real_routing_cost_sidecar` | PASS | `{"peers":2,"exact_original_and_arguments":true,"discovery_calls":1,"restart":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 15 | `real_binding_publication` | PASS | `{"witnessed_before_failure":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 16 | `real_late_counts` | PASS | `{"counters":[4,1,1,2,1]}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 17 | `real_caps_strict_includes` | PASS | `{"upstream_no_backfill":true,"includes_fatal":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 18 | `real_noisy_optional` | PASS | `{"seconds":5.024,"public_cleanup":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 19 | `real_noisy_required` | PASS | `{"seconds":5.027,"public_cleanup":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 20 | `real_registered_cancel_retry` | PASS | `{"unpublished_before_wait":true,"public_owner_retained":true,"public_cleanup":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 21 | `privacy_and_settlement` | PASS | `{"debug_sentinels_absent":true,"all_synthetic_tasks_and_processes_settled":true}` | [probes.log](VAL-009-evidence.tar.gz#probes.log) |
| 22 | `same_shape_fingerprint` | PASS | `{"complete_original_hashed":true,"frozen_nested_record":true}` | [supplement.log](VAL-009-evidence.tar.gz#supplement.log) |
| 23 | `optional_failure_attempt_reset` | PASS | `{"old_collision_cleared":true,"snapshot_retained":true}` | [supplement.log](VAL-009-evidence.tar.gz#supplement.log) |
| 24 | `public_kernel_startup_owner_retry` | PASS | `{"identity_retained":true,"successful_peer_drained":true,"public_recovery":true}` | [supplement.log](VAL-009-evidence.tar.gz#supplement.log) |
| 25 | `canceled_retry_owner` | PASS | `{"cancellation_propagated":true,"retained_public_owner":true,"public_stop_recovers":true}` | [supplement.log](VAL-009-evidence.tar.gz#supplement.log) |
| 26 | `assertion_failure_defensive_settlement` | PASS | `{"deliberately_injected_assertion":true,"reaped_and_drained":true,"tasks_settled":true,"not_public_cleanup_evidence":true}` | [supplement.log](VAL-009-evidence.tar.gz#supplement.log) |



## Frozen-input start/closeout evidence


Formal start: `2026-09-28T16:05:09.417470+00:00`. Final snapshot: `2026-09-28T16:30:36.977822+00:00`. Both snapshots independently hash all 22 authorities and both implementation reports against the request and candidate blobs, all 968 tracked packages/tests/pyproject/uv.lock files, and all files under the five unrelated path manifests (60 existing files; deleted family-tree remains absent). [start.json](VAL-009-evidence.tar.gz#start.json) and [closeout.json](VAL-009-evidence.tar.gz#closeout.json) preserve every path/hash and exact porcelain. [freeze.py](VAL-009-evidence.tar.gz#freeze.py) is the executable closeout snapshot implementation.


| Freeze item | Start | Closeout | Result |
| --- | --- | --- | --- |
| head | `9d6df3408279eb58347b1d7be26543d292ce6576` | `9d6df3408279eb58347b1d7be26543d292ce6576` | Identical |
| branch | `feature/friday-mcp-ws03-registry` | `feature/friday-mcp-ws03-registry` | Identical |
| candidate | `d395acdba9e233cb226f54e6258575f480157cf1` | `d395acdba9e233cb226f54e6258575f480157cf1` | Identical |
| request_sha256 | `15d4ca5ebbacd828b3b918ca2e6b409e42cd2862042a09062dce07ff23b6e715` | `15d4ca5ebbacd828b3b918ca2e6b409e42cd2862042a09062dce07ff23b6e715` | Identical |
| Request frozen commit blob | `34a457a540ca5e092c332431c824a537dcf7a8b0` | Same SHA256 as working request | MATCH |
| Pinned authority/report manifest | 24 exact expected/working/candidate matches | Same 24 exact matches | MATCH |
| Product source/tests/configuration | 968 tracked file hashes | Same paths and hashes; candidate diff exit 0 | IDENTICAL |
| Both implementation reports | Frozen expected hashes | Same hashes; candidate diff exit 0 | IDENTICAL |
| Unrelated paths | Five path manifests, 60 existing file hashes and preserved deletion | Same paths/hashes/deletion | IDENTICAL |
| Git status | Five unrelated dirty entries only | Exact same porcelain | IDENTICAL |



All 22 authority rows below were read completely; their SHA256 values match the request, candidate committed content, working content at formal start and working content at closeout. The two report rows also match all four sources. Original 20 authorities also match previous candidate contents; approved WS-03 and REM-005 directive blobs match their authorization commits.


| Input | SHA256 | Start/candidate/closeout vs request |
| --- | --- | --- |
| `AGENTS.md` | `7fad2b4063a0dc4201d26e353138da6165060077cc88e097dad2ac57551d987f` | MATCH / MATCH / MATCH |
| `docs/reference/policies/repository-engineering-policy.md` | `17b830b8990f74d1b0a25a46fc2cf2f62249f4e0d668f45b96cfe03a6cc76aff` | MATCH / MATCH / MATCH |
| `docs/reference/policies/development-task-lifecycle.md` | `d23f306ab33908f255109152c6c8686423725655184637fe2309e84d8491dc1c` | MATCH / MATCH / MATCH |
| `docs/reference/policies/independent-validation-policy.md` | `4d951418e0f0c96a4c87d4b8a07cb4025dd94738da50893d19a6d2b7a7f82f4a` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/build-plan.md` | `17b341bf51bd21b00ed88f6b0e413baad0b09b865cb9223a9a96d4887a9b6f00` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/tactical-plan.md` | `ead395b4949c01bdae6dfc6fb01d8b7af3ee6071902af45ec077c913f6dcd6ba` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/directives/ws-03-tool-naming-metadata-registry.md` | `c723e899d0916012dc324836f8c2882d5c2362a40825cec377e19182f1749efd` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/directives/ws-00-contract-policy-foundation.md` | `ec482e46364c9f4edcd7e76f2e4156d2f8af1710cc1811bf3390d6a5a0f99fac` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/directives/ws-01-configuration-model-validation.md` | `96ed70391066ac4402542f1f4056f4d38ac9e08be787dbd6daa2f8a41c4cb319` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/directives/ws-02-runtime-lifecycle-provider-loading.md` | `a432dc3c17e7cff9e767ed9dc78f6a1f65ea0d51dead3fc7e5421ef04327f55d` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/remediation/REM-003-directive.md` | `b04504638f1bded4af42c481ba35a89f02217a25fc392fae33b16ca51a57b680` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/remediation/REM-004-directive.md` | `1079756e6f6738c1dd4fb61126d2a1b3159c3ca48ef092470b47f22a09fec37b` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/execution/WS-00-closeout.md` | `434c24937dd4eff77d37ab6ec5c031127723fc54c83ee9446c3b088d848da486` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/execution/WS-01-closeout.md` | `8e10fcf509102c1faadcc2e56ce06fe6f9333aaa9d164ad82494e960cbfef32b` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/execution/WS-02-closeout.md` | `df241a9ad65e09f47df8c1aa33437e720994b811cd98d25a559b1c9626fbf5d3` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/validation/VAL-002-report.md` | `cfceee2537adb53d5e12fa517f12cc6549691811bd63709e5902edcdedfe2566` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/validation/VAL-004-report.md` | `d680911d220b0181fa32fca8260e0ce87f24a322d5dc64794951a85809ed2e0f` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/validation/VAL-007-report.md` | `649c70566c59109c413e55922b7150dbee7b0acb3c131f30b78ca726060561b6` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/rebaseline-2026-09-27.md` | `ccc6f1ca9feab180474e85b30e4c5b9319c32fbd56131f341907a452388f461a` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/execution/WS-03-readiness-checkpoint.md` | `2224bd224d7b004e9e43ebfa1c1eaa00c906f40fa8e35d5865236d44d720b521` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/remediation/REM-005-directive.md` | `5bff5b4b043d504384219d85af958bfffc4da584e057d910d35da3cb0a4c3ecb` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/validation/VAL-008-report.md` | `1bf0b019e0ba69f75eb638e1aa68f89a3d90088e2471dea11ce7ee76c1b46d0c` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/execution/REM-005-implementation-report.md` | `df3207f11d0beab740599346ffa9b9a9ec76eb1b9aca6861093956014cafebd1` | MATCH / MATCH / MATCH |
| `docs/planning/active/friday-mcp/execution/WS-03-implementation-report.md` | `836cbe11243da78ba34f739f808b97ee52dda264b3448c51d3763caae1d31965` | MATCH / MATCH / MATCH |



Unrelated preservation manifest:

```text
 M .DS_Store
 D family-tree.md
?? docker-bench-security/
?? packages/friday-chat/config.example.yaml.pre-typed-llm-20260828.bak
?? packages/friday-sandbox/docker/Dockerfile.audit
```


`family-tree.md` remains deleted exactly as found; `.DS_Store` modification and all three untracked path roots remain byte-for-byte unchanged. No broad stage or cleanup occurred. [diff-and-integrity.json](VAL-009-evidence.tar.gz#diff-and-integrity.json) records complete diff path sets, diff hashes, authorization hash equality, original-authority equality and all 33 immutable historical evidence hash results.


## Documentation/configuration and remaining gates

The public diagnostic record is an additive optional field: ordinary old three/four argument decision constructors and existing codes/binding reasons remain compatible. Consumers that reject additional serialized dataclass/DTO fields need to accommodate optional `collision` and the additive cost/count fields. The nested diagnostic is frozen and bounded; it does not replace exact routing provenance. Sidecar/original metadata is a trusted in-process capability with repr protections. Native registry exports remain mutable by trusted callers as explicitly approved; a later prompt consumer must copy/reverify as its separate contract requires.

No application configuration/default, dependency, mandatory MCP protocol field, transport cleanup budget or native registry API changed. The conservative supported schema subset can reject unusual otherwise-valid JSON Schema forms; current directive and reports disclose that boundary. Sanitization addresses tool definitions and known patterns; it does not claim universal injection prevention or tool-output safety. Existing default/core typing, board assertion and DOCX/XLSX test debt remains open and unchanged; no repair or waiver is included.

Residual gates remain: controller archival/closeout and explicit maintainer WS-03 acceptance; later WS-04 and subsequent slices require their own approval; complete feature-branch pre-merge review remains separate. Live MCP/provider/network/model UAT, output/prompt/transcript/Chat/memory/telemetry integration and delivery were not performed or authorized by this request. Any changed candidate, pinned authority, request or implementation report requires fresh review. Accepted WS-00/01/02 authority and acceptance remain intact.


## Evidence delivery


Repository artifact links identify original members of the controller archive `VAL-009-evidence.tar.gz`. Restoring the archive’s sibling layout exposes the exact named artifacts. This navigation adjustment makes no claim of independent verification of controller packaging.


Complete report: `/private/tmp/val009-20260928/report.md`. Machine-readable evidence/artifact SHA256 manifest: `/private/tmp/val009-20260928/evidence.json`. Exact command/result manifests, all logs, executable probes/fake peer, complete diffs and start/closeout snapshots are retained beside this report. No repository write is needed to consume this review. The controller may archive these bytes without changing the reviewed implementation inputs.
