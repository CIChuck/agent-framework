# Independent bounded large-document corpus validation

**CHANGES_REQUESTED** — one medium mandatory finding, LD-CORPUS-001. The corpus is deterministic and natively readable, but it does not yet provide the required meaningful cross-section retrieval control. Passing engineering checks do not waive that missing requirement.

Reviewer: fresh independent isolated validator, GPT-6 family (exact deployment identifier unavailable),2026-11-12. Read-only full bounded LD-01–08 review. Base `641ad015a30ea0db1ef3d4a8c5ba6263c86cf7a3`; frozen candidate `b341a3c9f6c326b8f891b058fec642dd31d5efc4`; branch `feature/cmd-ingest-001`. Actual generation source `3bf25f4ebac0497f43862783c0652312cebd998c`. Request SHA256 `f05007d337d2dc0794beaf9433b47b30c8c2f83af8f5ea8814ec9e7ad8a7cf12` verified before reading it. No memory/history/peer-review/private-reasoning inputs or delegation used.

## Mandatory finding

**LD-CORPUS-001 — medium — declared cross-section query is tail-only.**

Affected: `tests/readiness/ingest/large_documents.py:108` and `:145`–`:147`, `tests/readiness/ingest/tests/test_large_documents.py:47`–`:50`, generated oracles/documents and their README/results description.

Authority: `large-documents-scope.md:15`–`:17` requires independent start/middle/tail facts and “cross-section retrieval queries”; LD-03 explicitly requires cross-section queries. LD-08 requires accurate closeout evidence.

The authorization query asks for `COMPASS-N` and `RELEASE-(N+17)`, listing evidence sections `[N/2,N]`. The tail itself says both exact answers together. Fresh direct reference-text witnesses show the single sufficient section is16,64,128,256 or384 respectively. For384, section384 alone states: `Authorization requires COMPASS-384 and RELEASE-401.` No middle retrieval is necessary. The three remaining queries each require only one section. The existing test checks the metadata array `[size//2,size]`; it does not test answer separation.

Risk: a future retriever can return only the tail and satisfy the purported cross-section oracle. That would overstate coverage of combining facts from separate document regions. No present model-readiness credit is involved.

Required mitigation: provide at least one question per length whose answer requires facts split across the declared evidence sections, with no individual section sufficient. For example, avoid repeating the middle-only key in the tail, or combine a unique opening fact with a unique tail fact. Add a regression proving the declared sections jointly supply every required answer while each single section is insufficient. Regenerate both frozen corpora, native receipts and hash/archive/facts documentation from a new stable candidate and obtain fresh bounded review. Keep the model/production boundary. Do not silently repair the current candidate.

Witness: `LD03-cross-section-tail-only-witness.json` (all5 profiles, exact question/answers/section identities/tail suffixes). This is a semantic corpus defect; native reader success and metadata labels do not rebut it.

## Full criterion matrix

| Criterion | Outcome | Evidence and limits |
| --- | --- | --- |
| LD-01 | PASS | Filename-only complete base/candidate inventory is limited to named test source/selector/README and planning/evidence. No production source/config/lock change. Full opening/closing protected boundary and all supplied trees match. |
| LD-02 | PASS | Fresh20 genuine native documents +5 references at five lengths per mode; native counts and all bounded size/unit limits match. Source documents1,361,146 bytes. |
| LD-03 | FAIL | Start/middle/tail anchors, complete bodies/IDs and supersession are reproduced. The sole declared cross-section query is answerable from its tail alone in all5 profiles: LD-CORPUS-001. |
| LD-04 | PASS | Explicit word/character counts;25 per-document token fields null and model-serving/chunking/inference flags false. Procedural synthetic limits accurately disclosed; no model credit. |
| LD-05 | PASS | 87 offline cases per mode plus22 independent corpus controls per mode: fresh-only publish, injected partial publication no manifest, aliases/source/tamper/model-claim refusals and native body/ID/fact/unit failures. Existing native report refused without overwrite. Normal/-O all27 corpus members match originals exactly. |
| LD-06 | PASS | Fresh physical external runs, copied frozen source, empty required output/config/cache/tmp at entry; declared native target readonly. Fresh network/child/write/rename audit probes refuse per mode. All supplied tree bytes/metadata unchanged. Python/native containment limits retained. |
| LD-07 | PASS | Fresh87-case bootstrap selftests per mode; Ruff/check and format31 files; pinned typing receipt exact31 current source + config; actual native25 assets/4,240 bodies per mode;3 retained PNGs inspected; board/dashboard/docs/package metadata/scoped whitespace/preservation pass. |
| LD-08 | FAIL (linked) | Commands, source attribution,191-member archive, paths, unqualified Qwen prerequisites and current started/local/in_review lifecycle agree. README/results describe cross-section questions as provided, but that specific claim is unsupported until LD-CORPUS-001 is fixed. No state advancement. |

## Fresh execution and inspected evidence

Fresh base interpreter: `/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13` with `-I -S -B`; optimized mode additionally `-O`. Both `bootstrap.py selftest` commands used the pinned final harness manifest `2496a5e2be8035fa814a6153e33ba75bcb54c775f621ad64e3f59d9f3ce3d0a5` and distinct empty reviewer scratch. Both exited0 with87 tests and `upstream_qualified:false`.

Fresh physical runs: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/large-isolated-validator-l2egp241/.friday_test/runs/large-documents-review-normal` and `...-optimized`. Source was copied from the current frozen harness; inputs/reports/config/cache/tmp began empty. Canonical `large_documents.py generate`, `verify`, and `validate --target /Users/chuckrussell/Dev/gendev/agent-framework/.friday_test/runs/docling-behavior-e2e-20261112/target` each exited0 in both modes. No validation ran against supplied original corpora. Every25-file native validation recovered4,240 complete section bodies, all unique section IDs and anchors/facts. Private readers: PDFium5.15.2, python-docx1.2.0, openpyxl3.1.5, python-pptx1.0.2. Docling conversion false; inference requests0.

| Sections | Words | Characters | PDF pages | XLSX sheets | PPTX slides |
| ---: | ---: | ---: | ---: | ---: | ---: |
|16 |1,358 |9,572 |2 |1 |4 |
|64 |5,294 |37,259 |8 |1 |16 |
|128 |10,542 |74,181 |16 |2 |32 |
|256 |21,038 |148,020 |31 |4 |64 |
|384 |31,534 |221,852 |46 |6 |96 |

Fresh27-member corpus inventories in both modes exactly equal the originals, including assets/oracles/manifest. Documents total1,361,146 bytes; retained corpus including JSON totals1,377,448 bytes, below16MiB. Every document is below32MiB, with maxima46 pages/6 sheets/96 slides. Normal and optimized source bindings match actual generator/fixture source3bf25f4e; only later test alias target differs in the final harness. Archive normal source35 files match the actual-generation commit bytes.

Fresh independent corpus controls:22 per mode, including existing-output hash preservation; missing/changed/extra/oracle tampering; physical file and source symlink/hardlink refusal; missing/changed source; false serving/inference/token claims; removed format; injected second-asset write fault leaving no manifest; native body/ID/fact tampering with updated correct hashes so integrity verification passes before native failure; native count mismatch; exclusive native report refusal. Expected native negative commands exit1 at the named content/count/report invariant, not import/setup. Guard probes separately pass4 per mode: socket, child launch, outside-run write and rename refuse before effect. See authoritative `independent-controls-normal.json`, `independent-controls-optimized-explicit.json`, and `independent-guard-and-facts.json`.

Fresh private Ruff0.14.9 `check --no-cache` exits0; `format --check --no-cache` exits0 for31 sources, using the exact retained/root configuration. Typing is **inspected**, not rerun: pinned `mypy-last.json` exit0 says31 sources; all31 archived typing-source byte hashes and config exactly match current frozen sources and private/root config. No supplied typing cache was used or modified.

Fresh safe archive inspection:191 unique bounded regular members, no aliases/escape paths, all sizes and SHA256 match `evidence-index.json`; archive SHA256 `04be83aa8f5295f97cfce44f452db2c7e0daa2c889a0fdaf6126e96b868d8417`. Retained PNGs for largest PDF pages1/24/46 were copied to reviewer scratch and visually inspected: readable text and margins, no clipping/overlap observed. This is inspected retained rendering, not a fresh render or exhaustive Office layout review. Reproduced PDF bytes are exact originals.

Administration freshly exits0: board validate36 tasks; dashboard `render --check`; board next; package metadata18 projects; canonical documentation lifecycle1,121 Markdown files; selected-source/new-doc whitespace. Own bounded links additionally pass7 links. Global board `next` selects the separate unapproved Langfuse initiative; the explicitly selected command-refactor record remains started/normal/granted/local on the pinned branch, with the corpus-specific next gate. No task selection or state mutation occurred.

Exact validation command argv, cwd, exit, stdout/stderr and timings are retained in `command-ledger.json` and individual receipts. Every administrative Git call had `GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1`. Admin used offline/frozen/no-sync/no-download uv and reviewer-owned UV cache; nested docs uv inherited corresponding environment flags. No installs/downloads/network/model/store/service effects occurred.

## Integrity and procedure

Logical index `git ls-files -s -z` was hashed **before status** at both boundaries. Opening and closing candidate/branch/logical index/status/staging match the supplied boundary and one another:18,681 tracked hashes,26 symlink targets,8 protected/preserved metadata entries. Index digest `7bc62c6f093ce32fcf892a33e16e0348514ff646ef5debca1440ee56fceb42db`; staging empty. Both dirty YAML files remain byte/metadata identical and their payloads were not inspected. `.friday-old` payloads were not read. All request pins match at close. Raw authority was hash-only and matches pinned safe controls.

Supplied read-only tree hashes/metadata unchanged: harness38 entries, tools23,206, native target45,607, normal91, optimized88. The reviewer wrote only new external scratch. No repository changes, Git mutations, repairs, commits, further agents or reviews were made. Full before/after snapshots remain at `opening-boundary.json`, `closing-boundary.json`, `opening-input-trees.json`, `closing-input-trees.json`; compact evidence includes their hashes plus the integrity summary.

**Disclosed read-bound exception:** an inspection displayed README lines1–115 rather than stopping at the top large-corpus section. Adjacent prior evaluation contracts/manual instructions were exposed. This was disclosed promptly. The controller inspected the exact exposure and determined it contained no peer verdicts/scores, review contents or private reasoning, allowing continued independent substantive review without changing candidate/pins/authority. I concur the exposure does not explain or undermine the fresh cross-section finding, but it violates the narrower read boundary and prevents a claim of perfect procedure compliance. No further expansion followed. Canonical docs checker internal historical parsing was then explicitly clarified as permitted administration; only its summary was used.

Reviewer tooling setup errors and the superseded initial optimized assertion-based driver are disclosed in the ledger. The authoritative optimized independent control rerun uses explicit exceptions, so `-O` cannot strip its checks. None of those reviewer tooling issues is attributed to the candidate.

## Advisory component scores and limits

| Component | Score /10 | Rationale |
| --- | ---: | --- |
| Genuine format generation and deterministic measurement |9.0 | Full native positives and exact dual-mode reproduction; representative layout only. |
| Provenance, preservation and repeatability |9.0 | Exact pins/archive/source/input boundaries and fresh command evidence; typing receipt inspected. |
| Retrieval oracle design |6.5 | Mandatory cross-section control absent despite metadata; synthetic repeated procedures are correctly disclosed. |
| Isolation controls |8.0 | Fresh refusal witnesses and unchanged input trees; Python audit guard cannot establish OS/native containment. |
| Documentation and closeout accuracy |8.0 | Commands and lifecycle accurate; cross-section success description needs correction. |
| Review procedure |8.0 | Evidence strong, with explicit README read-bound deviation and corrected own-driver setup issues. |

These scores are advisory components, with no whole Gate-A or9.5 implication. The mandatory LD-CORPUS-001 remains regardless of scores. This review grants no acceptance, delivery, whole Gate-A, production construction, model/default selection, tokenizer qualification, Qwen serving or inference authority. The later exact-tokenizer/embedding-serving prerequisite remains pending. No model communication or real-world semantic-quality benchmark was performed.

Exit gate: bounded authorized remediation of LD-CORPUS-001, stable new candidate and regenerated attributable evidence, then fresh independent full LD-01–08 review. Source/state remain frozen.
