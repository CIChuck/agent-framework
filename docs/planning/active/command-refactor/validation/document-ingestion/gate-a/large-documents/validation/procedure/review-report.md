# INGEST-LARGE-DOCUMENT-CORPUS independent validation

**BLOCKED — review-procedure isolation.** All observed bounded corpus/code criteria pass; there is no mandatory candidate defect. The request's excluded-history condition was not fully met because one lifecycle-field search exposed unrelated historical review fields. This report therefore does not close the independent gate. No replacement reviewer was launched.

## Frozen identity and authority

- Reviewer: `/root/large_document_corpus_independent_validation`, fresh agent instance, read-only, no delegation. Codex; exact runtime model identifier was not exposed.
- Date: 2026-11-12 (UTC observation 23:45:23). Review mode: full bounded source/artifact review for corpus preparation, not whole ingestion or model evaluation.
- Repository: `/Users/chuckrussell/Dev/gendev/agent-framework`; branch `feature/cmd-ingest-001`.
- Base: `641ad015a30ea0db1ef3d4a8c5ba6263c86cf7a3`; candidate/HEAD: `b341a3c9f6c326b8f891b058fec642dd31d5efc4`.
- Actual supplied generation source: `3bf25f4ebac0497f43862783c0652312cebd998c`. The only later harness diff is the unit alias-test destination; generator, fixture writers and produced corpus bytes are unchanged.
- Request externally SHA256-verified before reading: `a72403cbf5238536409f0ab3d0790d841c7e26eaf9f4cbf001bc94019eab496b`. All request-pinned file hashes match at both boundaries.
- Frozen harness manifest: `2496a5e2be8035fa814a6153e33ba75bcb54c775f621ad64e3f59d9f3ce3d0a5`. All 35 selected frozen files equal current candidate Git bytes. All 70 archived generation-source files equal the actual generation commit.
- Governing inputs read: AGENTS.md; repository engineering, lifecycle and independent-validation policies; pinned historical harness directive within the corpus-only amendment; scope amendment, criteria, facts/results, evidence index/archive, frozen manifest/request/boundary, and complete new generator/tests plus affected selector/README and writer/environment dependencies. Existing authority/navigation changes outside this bounded deliverable were handled by name-only diff and read-only administration, except the disclosed lifecycle-search deviation below.
- Initiative remains `started`, delivery `local`; next gate is fresh independent corpus review. The scope amendment and explicit current request bound the historical draft directive; no broader construction or effect permission was inferred from that draft.

## Mandatory findings and review-procedure deviation

**LD-PROC-001 — BLOCKER, reviewer procedure; no candidate source defect.**

Requirement/source: request exclusions `Memory/history/peer reviews, raw full authority/navigation history` and parent dispatch `Do not read previous reviews or raw score history`.

Observed: after the substantive fresh bootstrap, native, corpus and control checks, this overbroad read-only lifecycle query returned historical unrelated MAINT/MEMQ `next_gate`, `validation_state` and similar fields, including prior review verdicts/scores:

```text
rg -n 'large-document|execution_phase|validation_state|next_gate|work_state|delivery_state' docs/planning/active/command-refactor/README.md docs/planning/active/command-refactor/authority.json docs/planning/active/command-refactor/next-phase.md docs/planning/active/command-refactor/tactical-plan.md docs/planning/board.yaml
```

The exposed authority locations included historical `authority.json` next-gate fields around lines 1617, 1679, 1862 and 1877. No historical review report, corpus peer verdict, builder private reasoning or memory file was opened. The unrelated values were not used to evaluate LD-01–08 or set advisory scores. The exposure was promptly disclosed to the controller, who instructed that its exact scope be retained and further raw-authority/history searches stop. No such further search occurred. The controller did not waive the request exclusion.

Risk: this instance cannot truthfully certify that all excluded historical inputs remained unobserved. Fresh reproduced corpus checks still have attributable technical value, but do not cure the procedure deviation.

Required mitigation/exit gate: obtain a new fresh-context read-only verdict using the same frozen candidate and pins, a preselected current-state authority projection and explicit bounded source/artifact paths. Do not pass this report, verdict, scores or the excluded raw lifecycle output to that reviewer as input. No product/source fix is requested. Keep work `started/local` until the independent gate is validly closed. Regression/verification: the fresh request must constrain lifecycle reads to exact current fields and retain the required LD-01–08/source/integrity checks. Documentation impact: retain this report as a procedure-blocked attempt, not candidate-failure or accepted completion evidence.

Mandatory candidate findings: **none observed**. No code remediation is authorized by this report.

## LD-01–08 observed matrix

The following PASS results describe reproduced or inspected corpus evidence. They do not override LD-PROC-001 or grant formal VERIFIED status.

| Criterion | Observed result and evidence |
| --- | --- |
| LD-01 | PASS. Exact base→candidate path inventory has only four allowed harness paths (new generator, focused tests, one selector line, README) and bounded planning/evidence records. `fixtures.py`, `behavior.py`, `e2e.py` equal the base. All tracked bytes/symlinks, dirty YAML bytes/metadata, preserved metadata, index/HEAD/branch/status/staging and supplied source/tools/target/corpora remain unchanged across the review. See preparation.json, changed-paths.txt, bounded-source.diff, equivalence.json, opening/closing-boundary.json. |
| LD-02 | PASS. Fresh generation in both modes contains 20 genuine native documents plus five UTF-8 references, with 27 entries including oracle/manifest. Native PDFium/python-docx/openpyxl/python-pptx load them. Independent actual PDF pages, workbook sheets and slides equal every manifest row and stay below 50/32/100. Every asset is below 32 MiB; full retained corpus including oracle/manifest is 1,377,448 bytes, below 16 MiB. See corpus-generate/verify/validate receipts and mode reports/independent-native.json. |
| LD-03 | PASS. All section IDs and all complete unique bodies were independently recovered once and in order: 4,240 bodies over 25 files per mode. Literal opening NORTH QUAY/provisional AMBER, middle COMPASS, tail COBALT/AMBER-revoked/RELEASE facts and their section locations match. Supersession/cross-section oracle evidence is checked against independent literals. Native extraction here is input validation, not Docling qualification. See independent_native.py, per-mode independent-native.json and native-validation.json; generator sections/oracle/native_validate at lines 89/113/468. |
| LD-04 | PASS. Independent reference measurements verify explicit words and characters for every row; all exact Qwen token values are null, qualification/inference flags false. The docs label the procedural templates as controlled completeness/truncation/retrieval controls, not real-corpus semantic-quality or model-capacity evidence. See equivalence.json, independent-native.json, manifest.json, README and pinned results/scope. |
| LD-05 | PASS. Fresh normal/-O generation is byte-identical across all 27 corpus entries, and equals both supplied corpora and both archived copies, including oracles and manifest. 20 independent canonical call-phase controls per mode verify existing-output refusal/no overwrite, tamper/missing/extra/oracle refusal, direct file/folder/source alias checks, source change/missing refusal, false-qualification/token/format refusal, parent-alias refusal, manifest-last order and injected mid-publication failure with no success manifest. See controls.py, controls-normal/optimized.json; generator source_binding/physical_file/publish/verify at lines 71/264/273/335. |
| LD-06 | PASS with declared native limits. All execution outputs/config/cache/temp/copies are under new reviewer scratch. Both run roots were physical, with copied exact frozen source and initially empty inputs/reports/config/cache/tmp. Base CPython uses -I -S -B; -O is separately run. Five guard controls per mode refuse socket creation, child launch, outside read/write and declared-target write before effect. No install/download/model/store/service command was run. All supplied trees are unchanged. Audit interception is not an OS sandbox. See guard_controls.py, per-mode guard-controls.json, command-ledger.json, boundary comparison; guard/main at lines 392/571. |
| LD-07 | PASS technical evidence; formal review blocked by LD-PROC-001. Fresh bootstrap reports exactly 87 tests in each mode, exit 0 with no skips. Fresh Ruff and format cover exactly 31 sources, exit 0. Inspected mypy receipt exit 0 is applicable because all 31 retained typing-source files and exact config bytes equal current candidate/root config; no typing cache was reused or written. Actual native 25-file validation passes per mode. Fresh board/dashboard/docs/metadata/whitespace administration passes. Three hash-verified largest-PDF PNGs (pages 1,24,46) were visually inspected: legible text within margins, no visible glyph clipping or overlap. See receipts, typing-inspection.json, equivalence.json and archive member verification. |
| LD-08 | PASS observed content, formal independent closure pending. Request/current/frozen source identities, actual generation source, README commands/run structure, archive/member hashes and measured tables agree. The 191-member archive is checked for inventory, duplicate/path/type/expanded-size constraints and every size/hash before extraction solely into reviewer scratch. Qwen serving/tokenizer and future context comparison remain pending; no production default, whole Gate-A, acceptance or delivery advancement follows. See preparation.json, archive-source-equality.json, equivalence.json and pinned scope/results. |

## Fresh measurements

| Sections | Canonical words | Canonical characters | PDF pages | XLSX sheets | PPTX slides |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 1,358 | 9,572 | 2 | 1 | 4 |
| 64 | 5,294 | 37,259 | 8 | 1 | 16 |
| 128 | 10,542 | 74,181 | 16 | 2 | 32 |
| 256 | 21,038 | 148,020 | 31 | 4 | 64 |
| 384 | 31,534 | 221,852 | 46 | 6 | 96 |

Native word counts vary for workbook headers and slide titles, as expected; canonical metrics describe the shared reference text. Source bytes for 25 documents/references total 1,361,146. Token counts remain unknown.

## Reproduction and exact exits

`command-ledger.json` retains the exact leaf argv, cwd, own-cache paths, exits and stdout/stderr for required commands. The reviewer scripts are included with the evidence so that their exact mutations and control assertions are inspectable. Define:

```text
P=/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13
S=/private/tmp/large-document-independent-review-HLnkri
T=/tmp/large-document-independent-review-HLnkri
```

The following commands were executed freshly, each exit **0**:

```text
P -I -S -B T/prepare.py
P -I -S -B T/checks.py normal
P -I -S -B T/checks.py optimized
P -I -S -B T/checks.py static
P -I -S -B T/checks.py admin
P -I -S -B T/independent_native.py normal
P -I -S -B -O T/independent_native.py optimized
P -I -S -B T/controls.py normal
P -I -S -B -O T/controls.py optimized
P -I -S -B T/guard_controls.py normal
P -I -S -B -O T/guard_controls.py optimized
P -I -S -B T/equivalence.py
P -I -S -B T/archive_source.py
P -I -S -B T/boundary.py opening
P -I -S -B T/boundary.py closing
```

These lines abbreviate the declared absolute prefixes (T is the shell launch alias of the physical S scratch) for readability; the JSON ledger has expanded argv. `checks.py optimized` explicitly launches its children with -O. Each mode's leaf commands are the exact copied frozen `bootstrap.py selftest --harness-manifest ... --harness-manifest-sha256 2496... --scratch <own empty scratch>` followed by canonical `large_documents.py generate`, `verify` and `validate --target <declared private target>`, all with -I -S -B and the appropriate optimization flag. Normal and optimized native validations each exit 0 with 25 documents and zero inference requests.

Fresh static commands use the declared existing private Ruff executable and private config/source copies: `ruff check` and `ruff format --check`, each with own `--cache-dir`, all 31 explicit source paths and exit 0. Typing is **inspected, not rerun**: archived receipt reports `Success: no issues found in 31 source files`, exit 0; exact all-source/config equality is independently recorded. Prior builder native/test/admin receipts are integrity-checked, not substituted for the fresh checks. No supplied receipt command with supplied writable paths was replayed.

Fresh administration uses `GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1`, reviewer `UV_CACHE_DIR`, and `uv run --offline --frozen --no-sync --no-python-downloads python -B`: board validate (36 tasks), render --check, documentation lifecycle (1,121 Markdown files), metadata (18 pyproject files). All exit 0. Fresh owned/cached/candidate `git diff --check` commands also exit 0. No render mutation was run.

## Artifacts

Formal report: review-report.md; exact command ledger: command-ledger.json; compact fresh evidence: reviewer-evidence.tar.gz; member hashes: reviewer-evidence-members.json; delivery hashes: delivery-manifest.json. All are under the physical S scratch. The compact archive includes this report, commands, fresh source/corpora, native/control results, boundary snapshots, and only the inspected typing receipt/proof from supplied evidence.

## Integrity and limitations

Both opening and closing snapshots execute `git ls-files -s -z` before status and bind logical index SHA256 `7bc62c6f093ce32fcf892a33e16e0348514ff646ef5debca1440ee56fceb42db`. Both verify candidate/base/generation pins, branch, HEAD, complete status/staging, 18,708 tracked-path bytes/metadata and symlink targets, preserved metadata, all pinned inputs, and complete supplied frozen/tools/native-target/corpus file metadata/hashes. `closing-summary.json` reports `unchanged: true`, no differing sections. Opening also exactly matches the supplied tracked hashes/symlinks/preserved metadata and default status. No Git mutation, repairs, installs, commits, source edits, production tests or external services occurred.

The supplied archive SHA256 is `04be83aa8f5295f97cfce44f452db2c7e0daa2c889a0fdaf6126e96b868d8417`; all 191 indexed members match. Fresh corpus manifest SHA256 is `72a67b0e36e46626676e9e0016eb571ca01c8614012ee198f7ffd1b660a569ce` and oracle SHA256 is `01a7244cecf4f0c84a7f128dbce981427982d6e68f0987286699994df7471c47`. Every normal/optimized fresh/source/supplied comparison is recorded.

Audit guards prevent exercised Python-visible attempts; they do not contain native-library I/O at OS level. Boundary hashes detect persistent changes in enumerated trees and protected metadata; they cannot prove absence of every transient native effect or unenumerated external read. Only representative PDF layout was inspected, not exhaustive Office rendering. These controlled repetitive procedural templates do not establish real-world semantic quality, exact Qwen token capacity or retrieval accuracy. No new Docling conversion, OCR, chunking, embedding, inference, store or loaded-model qualification was performed. Existing baseline product debt remains unwaived.

Advisory bounded scores, independent of any excluded historical values: observed candidate quality **9.0/10**, corpus reproducibility/evidence **9.2/10**, review-protocol compliance **8.0/10** due LD-PROC-001. Scores do not override the formal **BLOCKED** outcome. No acceptance, product construction, whole Gate-A qualification, push/merge/release/deployment or model-default authority is granted.
