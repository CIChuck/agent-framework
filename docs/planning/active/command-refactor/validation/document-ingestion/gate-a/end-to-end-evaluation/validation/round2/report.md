# Corrected isolated end-to-end ingestion review

**VERIFIED** — E2E-IV-001 is closed; all mandatory EE-01–EE-08 criteria pass for the explicit reporting-only profile. No mandatory findings remain.

Candidate `1f5f86dcd8315eaf9a7508c44c65b4637766c323`; correction base `cae6aa4c183f013c19d10af4358dcf93fd189367`; original actual live source `c97777366671006f56866aa92898aaffcec524d6`. Reviewer: /root/ingest_e2e_corrected_independent_validation (fresh Codex validator; exact model identifier not exposed). Date: 2026-11-12T22:57:49.989238+00:00. Fresh read-only delta-first then full bounded aggregate review. No nested agents.

The source request SHA256 was verified before reading it: `89c31e373f8b6c203f184569e39b6bc13b79a30813d5d970d6a901300256c6d0`. The24 input pins and frozen manifest `04f9c1975fa22eae3fddb9cc3af0961a682f285f106d897697cc855ffe02bde1` matched at both boundaries. AGENTS.md, engineering/lifecycle/independent-validation policies, the harness directive, scope amendment, criteria and EE-REM-001 governed this review. Exact input hashes are in request.json.

## Delta first

The correction compares nonempty consistent lowercase64-character conversion-runner digests from the exact hash-validated corpus buffer with physical, singly-linked behavior.py. Missing, malformed, conflicting, changed or aliased source/binding refuses before report PASS. It retains own-runner, command-completeness and artifact-hash controls. A later admitted-attempt pointer does not invalidate the unchanged source digest.

I reproduced30 independent canonical CLI cases across normal and optimized Python: valid and advanced-pointer fixtures pass; missing/malformed/conflicting binding, missing/changed/symlink/hardlink/parent-symlink behavior source, aliased corpus, changed e2e source, failed result, changed HTTP artifact and missing evidence all refuse without PASS. The full79-case suites add the committed malformed/alias/failure coverage. The corrected canonical runner also refuses copied authentic old-code receipts in both modes (`Report runner changed`, exit1). Synthetic fixtures receive no conversion/inference/storage execution credit.

Independent AST comparison found exactly20 unchanged definitions, changed report(), added report_conversion_source(), and no removed definitions. Top-level nondefinitions and behavior.py bytes match c977. The original c977 archive/source/receipts/stores remain original historical evidence.

## Full bounded matrix

| Criterion | Result and evidence | Advisory score |
| --- | --- | --- |
| EE-01 | PASS — test-only correction; committed source/package origins and all preserved identities match. Selected three-file diff; static-integrity.json; opening.json; closing-summary.json. 149 Friday wheel payload files equal commit 96f752d6, candidate and supplied installed files. | 9.4/10 |
| EE-02 | PASS — historical five genuine conversions cover native/scanned PDF, DOCX, XLSX and PPTX; corrupt PDF and missing-formula-cache XLSX remain excluded. Default512 and DOCX128 content oracles bind to immutable conversion attempts. conversion-oracle-attribution.json; original attempt/result/document receipts; historical-attribution.json. Reproduced token counts on persisted copies: maximum510 at512 and84 at128. No fresh Docling replay. | 9.2/10 |
| EE-03 | PASS — inspected original Friday-LLM broker and task-preparation path; recomputed all18 POST input hashes from stored document/query text; all36 surrounding observations retain exact model/context/fingerprint. e2e.py embed() source; original HTTP receipts; historical-attribution.json; 149 committed/installed wheel-member comparisons. No live request reproduced. | 9.1/10 |
| EE-04 | PASS — unchanged runtime validates model/count/order/finite/nonzero768 dimensions and reserves budgets before zero-retry transport. Fresh malformed-response and exhausted-budget controls refuse; all162 persisted document vectors independently checked. independent-response-budget.json; independent_controls.py; reopen-normal.json; reopen-optimized.json; original request sequence4..57 and 172 vectors/41556 local tokens. | 9.2/10 |
| EE-05 | PASS — shared public Memory adapter retains81 rows per mode in fresh per-mode historical stores; exact content hash, source, chunk, budget, protected metadata and absent description all reproduced from copied stores. Refused cases absent. reopen-normal.json; reopen-optimized.json; original corpus/stored receipts; historical-attribution.json. Original physical18 store files still byte-equal archive. | 9.3/10 |
| EE-06 | PASS — inspected original query embedding attribution; independently reopened both physical store copies in separate normal/-O processes with networking denied and embedding callbacks that raise. All10 retrieval ID lists match. independent_reopen.py; reopen-normal.json; reopen-optimized.json and guard receipts. Queries reuse source text; semantic retrieval quality remains unqualified. | 9.3/10 |
| EE-07 | PASS — E2E-IV-001 CLOSED. Fresh canonical CLI positives and source/binding/alias/failure/artifact negatives succeed in both modes. Historical e2e receipts refuse the corrected runner as expected. All pins/archives/per-run bindings and frozen boundaries agree. independent-cli.json; old-receipts-normal.stderr; old-receipts-optimized.stderr; static-integrity.json; closing-summary.json. Home-cache metadata/mkdir attempts prevented; Python-visible guard is not an OS sandbox. | 9.1/10 |
| EE-08 | PASS — fresh79-case bootstrap suites pass normal/-O; Ruff check and format pass29 files. Inspected successful private mypy receipt has29/29 source-byte equality and exact root config. Manual commands, setup limitations and actual versions remain accurately attributed. Fresh administration passes. normal.stdout/stderr; optimized.stdout/stderr; ruff.stdout; format.stdout; typing-source-equality.json; admin-*.stdout; command-ledger.json. Typing was inspected, not rerun. | 9.2/10 |

Scores are advisory component assessments of this bounded slice. There is no whole-Gate-A or overall9.5 claim.

## Reproduced checks and exact commands

command-ledger.json records exact argv and exit status for every runnable validation lane, including expected refusal exits. All executions use the recorded CPython3.13.10 base with -I -S -B and -O in optimized lanes. The canonical report commands execute the copied corrected e2e.py directly. independent_controls.py, independent_reopen.py, historical_check.py, static_integrity.py and closing_integrity.py are retained for reproduction.

- Bootstrap selftest via externally pinned frozen bootstrap/manifest with distinct reviewer scratch: normal0, optimized0;79 cases each.
- Private Ruff check0 and format --check0 over29 harness Python files, private cache paths.
- Independent response/budget controls:10 explicit refusals plus positive768-vector and last-permitted reservation; refused budget file remains unchanged.
- All367 original and411 correction archive members are regular, unique, safe relative members with complete index and matching size/SHA256. All149 Friday wheel payload members match committed96f752d6, current candidate and supplied installed source.
- Both physical disposable store copies reopen with denied networking, failing embedding callbacks, exact source/content/provenance/metadata and retrieval IDs;81 rows and5 queries each. Vectors are finite, nonzero and768-dimensional. Prepared document maxima are510 tokens at512 and84 at128, including prefix and special tokens.
- Board validate0 (36 tasks), dashboard render --check0, tracked documentation lifecycle0 (1116 Markdown files), package metadata0 (18 pyprojects), correction-range/staged/owned whitespace0. Supplied builder render receipt was inspected only; no render mutation was replayed.

Private mypy is **inspected**, not freshly executed: its pinned exit0 receipt reports29 files, and all29 source files plus root rule config equal the current candidate exactly (typing-source-equality.json). This is the explicit permitted source-equality profile.

## Historical actual execution attribution

The actual c977 archive independently binds normal b30fc98907624550ae98706e847de03d and optimized287706eaf2ab44469dccc2eb2961a511. Each has five genuine successful converted document bindings,41 default512 rows plus40 DOCX128 rows,4 document broker calls,5 query calls,9 embedding POSTs and18 model-state GETs. Recomputed prepared input SHA256 lists match every saved POST. All before/after observations show selected Nomic/context2048 and the same loaded-instance fingerprint. Totals remain57/64 reserved requests,172/256 vectors and41556/131072 local prepared tokens. All10 expected source query ranks are1.

Each corpus attempt matches its immutable attempt/result/document bytes and original input hash. Literal source oracles pass across each default/override corpus. Corrupt PDF is an actual Docling failure with empty content; missing-formula-cache XLSX is a structural admission refusal before Docling. Both are absent from corpus and storage. Package source and original e2e.py/behavior.py match their recorded committed origins. This is inspected historical execution plus independently reproduced copy reopening, never a new corrected-code inference experiment.

## Preservation and limits

Opening and closing matched: 18665 tracked-file hashes,26 symlinks,8 preserved records,24 pins, HEAD/branch/status and logical index `aa9ece30961e4648b0ab7bff84f811e510fa5ccb9228e56d65b58f4ecaa56e26`. git ls-files -s -z was captured before status at both boundaries. Two dirty YAML files remain dirty and unchanged; .friday-old, personal stores and working environment remain preserved. All18 supplied physical disposable-store files still equal the immutable original archive.

All reviewer outputs/caches/copies are under this fresh external scratch. All output, scratch, caches, copied stores, tokenizer copy and artifacts under this new external scratch; no candidate, supplied artifact/runtime/store, dirty YAML or Git mutation.

- Original real experiment remains attributed to c977; corrected synthetic reports confer only report-control credit.
- No raw server-token equivalence: saved upstream usage is zero; local tokenizer counts are independently reproduced.
- Retrieval uses known source text and proves consistency rather than semantic quality.
- Python audit guards and targeted home-cache metadata wrappers prevented recorded probes/mkdir attempts; no home-cache payload open or write was permitted. Native extension code is not OS-contained.
- Native copied-store reopens used the supplied read-only private package target; only reviewer-owned extracted store copies were opened.
- Documentation checker used reviewer PATH wrappers: uv child invocations forced offline/frozen/no-sync/no-python-downloads and python -B; git document inventory used cached paths only to avoid .friday-old enumeration. Frozen status showed no untracked documentation.
- Original failed setup/version-lookup attempts are retained/documented as setup evidence and receive no negative-test credit. Reviewer-only order/glob inspection mistakes are recorded separately in the command ledger.
- No prior full peer review or private reasoning was read; EE-REM-001 alone supplied the approved finding. Controller results/status were treated as claims, never inherited verdicts. Memory and history were not used.
- Whole-repository baseline debt remains unwaived and was not rerun.

VERIFIED is bounded independent conformance only; no whole Gate-A9.5, product construction, maintainer acceptance, push/merge/release/deployment or delivery authority.
