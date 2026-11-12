**CHANGES_REQUESTED**

Independent bounded implementation review, INGEST-DOCLING-BEHAVIOR, BE-01 through BE-12. One mandatory medium-severity finding remains: a timed-out conversion rerun can leave its previous successful output eligible for admitted chunking. The current successful measured document results remain useful evidence; they do not prove the stale-attempt exclusion claim.

Reviewer: Codex independent subagent `/root/docling_behavior_independent_validation`. Exact model/version is not separately exposed. Date: 2026-11-12T20:33:06.557218+00:00. Mode: fresh-context, read-only implementation and retained-control interaction review, without delegation or council. Memory, builder conversation/private reasoning and prior review verdicts were not consulted. No earlier verdict or score is carried forward.

**Identity and controlling authority**

Repository: `/Users/chuckrussell/Dev/gendev/agent-framework`; branch: `feature/cmd-ingest-001`. Frozen candidate: `4fd5f8252cd5d89924e0e01527dadca3ea1ee3b3`. Diff base: `11e8fccc23981b5449a51f2ef3f7d3ea565a062c`. Test-source bytes match source candidate `24d15ab5a82c662bcbf3a49d0603184d5fba748b`, with no source diff between that commit and the current candidate.

The first operation was SHA256 verification of the supplied review request: `39ccb8bcbf7da0ca3034d4056dc6196676060fdcecdc3f8a411193408d918c83`. It matched before the request was read. All request input pins matched at opening and closing. `review-request.json` in this scratch retains the exact current authority inputs and their hashes.

Read AGENTS.md, repository engineering policy, development task lifecycle policy, independent validation policy, CD-CMD-INGEST-GATE-A-001, the pinned focus amendment and exact focus authorization, BE criteria, behavior results, test README, all changed source/tests, source diff, and relevant retained-control entrypoints. The explicit focus amendment controls the ordinary private package/document evaluation scope; the old draft directive's historical metadata and micro-activation procedures are not reinstated. Raw authority.json, execution log and old review reports were not exposed; tracked-byte checking hashes them without reading their content into this review.

The non-documentation candidate diff consists only of `tests/readiness/ingest/README.md`, `behavior.py`, `stages.py` and `tests/test_behavior.py`. No product integration, full-Friday installed-profile qualification, provider/LM Studio operation, embedding request, Chroma effect, delivery or acceptance is within this review.

**Mandatory finding BE-REV-001 — stale successful output survives a failed latest attempt**

Severity: **medium**. Affected source: `tests/readiness/ingest/behavior.py:886-895` (`document_ready`), `:973-986` (admitted source selection), `:1239-1248` (conversion supervision followed by chunking), and result publication at the end of `convert_case`. Regression coverage: `tests/readiness/ingest/tests/test_behavior.py:test_refused_partial_or_stale_documents_never_reach_chunking` checks serialized JSON mismatch and status fields, but does not exercise a failed rerun retaining a prior successful result.

Violated authority: **BE-08**, “Refused, empty, partial, failed or stale output excluded from admitted chunks.” The README and behavior-results.md claim that stale outputs cannot enter the admitted matrix; that corresponding BE-11 error/reporting claim is too strong.

`document_ready` checks the old result's success flags and its JSON hash. It has no binding to the latest attempt. A conversion killed by the supervisor before result publication leaves the old successful result and JSON intact. `chunk_cases` still treats them as current. `evaluate` continues to chunks after a failed conversion; its final overall exit does record the failed command, so this finding does **not** claim that a complete evaluate invocation silently returns success after the timeout. The narrower violation is that its admitted chunk evidence can include the failed latest attempt's predecessor, and the separate chunks/report commands can succeed on that stale evidence.

Fresh reproduction used only this reviewer's disposable run and exact candidate code. The definitive reproducer first performs a genuine successful Docling PDF conversion in the same private run and Python mode; its seed result is never fabricated. The candidate's own supervisor launched the actual convert CLI with a deliberately shortened one-second ceiling, returned124, and retained the old result bytes. That short timeout is a controlled attempt-invalidation test; it earns no native document-refusal or extraction correctness credit. In **both normal and -O** modes:

- fresh conversion supervisor exit:124; old successful result bytes unchanged;
- `document_ready(old_record, old_json)` returned true;
- subsequent admitted chunks command exited0, included `pdf-native.pdf.json`, skipped nothing and reported84/84 passing cases (one stale document plus six synthetic payload sources, three strategies, four budgets).

Exact reproducible commands (the helper expands and records all candidate child argv, and uses explicit exceptions under -O):

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/docling-independent-review-pznws3a2/reproduce_stale.py
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/docling-independent-review-pznws3a2/reproduce_stale.py
```

Evidence: `stale-reproduction-normal.json`, `stale-reproduction-optimized.json`, `command-logs/stale-reproduction-final-*.stdout`, and the reproduction run's `reports/commands`, logs, old admitted result and serialized document. The exact helper is retained as `reproduce_stale.py`.

Risk: interrupted or timed-out evaluations can mix old extraction with current measurements, falsely crediting chunkability/currentness for a case whose latest attempt failed. This is evidence/data-integrity risk in the test component; no production or store effect was observed.

Bounded required fix: make admission eligibility depend on the latest immutable conversion/evaluation attempt for that case. Invalidate eligibility before launching a new attempt, retain historical outputs separately, and publish eligibility only after successful completion with matching input, effective conversion settings/profile, runner and output identities. A failed/killed attempt must remain excluded even when old success files are present. A small local attempt/result mechanism is sufficient; this does not require more package resolver/metadata machinery or product changes.

Required regression: genuine prior success -> new owned timeout/termination before result publication -> old source absent from admitted chunk sources, with an explicit skip/failure reason; successful current siblings remain eligible. Prove the matching fresh positive and current-input/profile binding, in normal and -O. Retain the failed-attempt logs and update the two stale-exclusion claims/evidence to the verified behavior. No production configuration change is required.

**Criterion matrix**

| Criterion | Outcome | Evidence and practical limit |
| --- | --- | --- |
| BE-01 | PASS | Only the four allowed test/README files change outside docs. Opening/closing tracked-byte, symlink, dirty YAML, lock and protected metadata checks match; no shared writes. |
| BE-02 | PASS | Inspected standard uv compile/sync wheel-only, hash-locked private setup receipts,106 distributions,18 assets. Fresh private imports confirm Docling2.150.0, RapidOCR3.10.0 and Certifi2026.10.23, above2026.10.19, from reviewer target. No network/install replay. |
| BE-03 | PASS, bounded | All actual workers use qualified base Python -I -S -B, with -O for second lane, private target/assets/caches and candidate offline guard. Six isolation canaries pass per mode. Python-visible prevention is demonstrated; no native/OS sandbox claim. |
| BE-04 | PASS, mixed proof | Hash-bound qualified normal and optimized receipts each contain37 records:30 genuine fixtures plus7 controls. Fresh12-case representative lanes execute in both modes, including native PDF, scanned OCR, Word table/order, valid formula and unsafe XLSX, notes/comments, native corrupt PDF and Office admission refusal. |
| BE-05 | PASS | Raw defaults/failures and independent fixture oracles are retained in verified archive. Furniture, OCR heading omission, hidden/formula behavior, notes/comments, empty/encrypted and corrupt results remain distinct. No alternate reader supplies document text; historical setup failures earn no correctness credit. |
| BE-06 | PASS | Fresh body/furniture export restores page markers; configured isolated OCR heading reaches document chunks; unambiguous PPTX notes retained and comments excluded. Unsafe formula cache/hidden row refuse before native conversion. Public Docling APIs supply configured serialization. |
| BE-07 | PASS, scoped | Fresh168 cases per mode,14 sources (8 real documents plus6 generated payloads), all3 strategies and64/128/512/1024. Default no-override invocation passes42 cases at512. Independent recount checks1,394 chunks per mode, including prefix/specials; all actual limits hold. Recursive/fixed are test prototypes; endpoint counter agreement remains unqualified. |
| BE-08 | FAIL | Ordinary refusal/empty/partial/status/hash controls and content checks work, but BE-REV-001 proves stale successful output survives a failed latest attempt and enters admitted chunks in both modes. |
| BE-09 | PASS, observed bounds | Candidate supervision bounds owned groups, logs time/reason/RSS and sampled disk; inspected setup took136.57s. Fresh representative supervised active time168.18s; maximum sampled RSS2006794240B; logical run disk1628563946B. Deliberate one-second timeout targets only reviewer-owned children. Sampling/native limitations remain disclosed. |
| BE-10 | PASS, mixed proof | Fresh65 minimal cases normal/-O; Ruff check and27-file format pass. Hash-bound parser6 positive/39 refusal and engine7 positive/24 refusal per mode, plus private mypy27 sources, inspected against matching source hashes. No product tooling borrowed for actual/static lanes. |
| BE-11 | PARTIAL / BE-REV-001 | Manual convert/chunks/report and error phases reproduced; no model/store effects. Timeout command is recorded, but the admitted-source report's stale exclusion claim is unsatisfied. |
| BE-12 | PASS | Exact current frozen source and all5,247 archive members verified; this independent review separates executed from inspected evidence and preserves explicit full-framework/model/storage/acceptance limits. Its finding prevents qualification of this changed implementation. |

**Freshly executed checks**

The complete exact argv, cwd, exits, elapsed times and output hashes are in `command-ledger.jsonl`; `command-ledger.md` is its readable rendering. Every runtime/source/static/cache/log/output path targets this scratch. No receipt argv was replayed with supplied controller output/cache paths.

- Frozen minimal selftests:65 cases normal and65 optimized, exit0 each, using the31-file frozen manifest (`49cd2cdedcf2c2999505d623f0e92010cc6b7edc9997ad39c0bfd67ebac7ccfc`).
- Fresh configured real cases per mode: `pdf-native.pdf`, `pdf-pages.pdf`, `pdf-scanned.pdf`, `docx-body.docx`, `docx-merged.docx`, `xlsx-formula-valid.xlsx`, `xlsx-formula-missing.xlsx`, `xlsx-hidden-row.xlsx`, `pptx-notes.pptx`, `pptx-comments.pptx`, `corrupt.pdf`, `corrupt.docx`. All expected command exits0. The last is structural admission with native_docling_called=false; corrupt PDF reaches native conversion and reports failure/meaningful=false as the expected native refusal. They do not count as supported extracted documents.
- Eight meaningful real documents reach the fresh chunk matrix in each mode. Each168-case content oracle report passes168/168. Empty corrupt PDF JSON is skipped; Office admission refusal has no native extraction credit. Configured source order, table markers, furniture, OCR and notes/comment oracles pass.
- Independent origin/token check: corrected helper exit0. All1,394 chunks per mode were retokenized from actual prepared text; stored counters agree and none exceed their limit. Default512 CLI invocation passes42/42.
- Isolation and package probe: normal/-O exit0. Actual module paths are in `reviewer-independent-tokens.json`.
- Focused Ruff check and format: exit0;27 files formatted. Approved copied Ruff SHA256 `3844f53974c6e6d52dcfccdc02e9b34188c5003f0060ad2f3a96b9d550eea6f5`, copied config SHA256 `d1e8ff05afbe8f1a06d3ddaa07db520ff0a1378f6fae23baf3ee525b9619e9d7`.
- Board validate, dashboard render --check, documentation lifecycle, package metadata: exit0 each, using the expressly permitted maintenance .venv administrative lane through `uv run --offline --frozen --no-sync --no-python-downloads python -B`, with reviewer-owned UV cache. This confers no runtime/installed-profile qualification.
- Owned-path, base..candidate range and cached whitespace: exit0, with GIT_OPTIONAL_LOCKS=0 and fsmonitor disabled on every Git invocation.
- BE-REV-001 explicit-exception normal/-O reproductions: exit0 means the defect was reproduced; candidate child timeout124 followed by chunks0 in each. These are not passing conformance checks.
- Closing integrity check: exit0.

One reviewer-helper setup attempt failed (exit1): its source file was outside the allowed run, and Torch traceback source inspection was correctly denied by the candidate read guard. The helper was copied into this reviewer's run/source and rerun successfully. This earns no product correctness/refusal credit and did not stop meaningful review. The ledger retains both outputs. Initial stale reproduction was additionally rerun with explicit reviewer exceptions so the proof checks remain active under -O; the definitive proof logs are named `stale-reproduction-final-*` and each first repeats the genuine successful conversion in the same reproduction run and mode.

**Inspected evidence, not replayed**

The supplied compressed archive SHA256 is `44bcbadc510c7c7a9dc80ab28db51f4c7c377ad0693c7a2f227f58bb4af6a297`; its compressed index SHA256 is `081260cf048ef1ad8a77d8313d462f07436ff58e1787c8ecda81dcc35f7b32d1`. Verified exact member set, no duplicate names/aliases, every member length and SHA256,5247 regular members and57,745,989 bytes. The decompressed index digest also matches the evidence index. This validates evidence identity, not an inherited verdict.

The source-matching receipts are under `run/history/qualified-normal` and `run/history/qualified-optimized` in the archive: each37 records,26 pass (including native empty/error refusals),1 characterized,10 admission refusals;27 native Docling calls,21 meaningful admitted documents and324/324 chunk/content cases. All37 source records per mode pin runner SHA256 `32a1f3ee4e030a176a642573bf334425a1e93f79fe1c2a8be3d0117da0d47a60`. Earlier `final-normal`/other attempts use different runner hashes and include failures; they are retained history and were not credited as the final result. The full37/324 runs were not repeated by this reviewer.

Standard private resolution/install, original30 raw defaults,18 asset receipts, parser/engine selectors and mypy27 were inspected, not executed. The ordinary selected package profile was copied physically with APFS cp -cR after alias/hardlink-source rejection; no hardlinks or symlink targets were used. Current selected assets and all indexed input fixtures were hash-checked in both reviewer copy and supplied read-only run at closing. `inspected-summary.json` records exact receipt references. The existing setup source hash differs from the final behavior runner because setup preceded final implementation; that is historical setup proof only, not final runtime correctness proof.

**Preservation, limits and score**

Shared-checkout read-only exception: no isolated Git checkout was created; stable Git blobs supplied all31 frozen source files and their Git object/SHA256 identities were checked against the frozen manifest. Review state/caches/copies/logs are physically under `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/docling-independent-review-pznws3a2`. Runtime copies use the required nine private subdirectories below `.friday_test/runs/docling-behavior-review-20261112` and a separate reviewer-only stale reproduction run. Qualified base CPython3.13.10 binary SHA256 recorded live: `e2adf1814122d8b26166917ef7d294d7426963e0f59e28d0d5aef773f67c4bb0`.

Opening and closing logical index-before-status SHA256: `e60bb3c4876dfe1ca5fa634957ea5288271b3e8a17e5d90ece7ebab2b7f2235c`. Candidate/branch, all18,624 tracked byte pins,26 symlinks, all request input pins and eight protected payload/metadata entries match at both boundaries. Existing dirty `packages/friday-chat/config.example.yaml`, `models-config.example.yaml` and untracked `.friday-old/` remain exactly as supplied. Production source/configuration, workspace lock, .venv/stores/exports and model services were not changed. No supplied source/input/cache/output path was a write destination. Detailed exact metadata evidence is in `opening-integrity.json` and `closing-integrity.json`.

No network, installs, extra model service, LM Studio request, embedding request or Chroma write was performed. Python interception is not an OS sandbox; native libraries and sampled RSS/disk limits do not prove complete native containment. Full-Friday installed-profile compatibility, user documents, model-window/counter agreement, embedding/vector quality, storage and production /ingest remain open. Known root product lint/collection/registry-format and dirty-YAML whitespace debt remain failed/unwaived; no broad product suite was run or green claim made.

Evidence coverage score: **9.0/10** for this bounded slice (fresh representative behavior plus verified complete raw receipts; no full execution replay or native sandbox proof). Overall implementation conformance score: **8.5/10**, advisory only. The reproducible mandatory BE-08 violation controls the outcome regardless of numerical score. No optional advisory is raised beyond the explicitly retained limits. A new stable candidate and fresh bounded remediation-delta plus aggregate BE review are needed; this review grants no acceptance, whole Gate-A, product, delivery or effect authority.
