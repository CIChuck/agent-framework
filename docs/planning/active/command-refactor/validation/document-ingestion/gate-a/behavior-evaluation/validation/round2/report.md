# Independent corrected Docling behavior review

**VERIFIED** — BE-REV-001 remediation delta, followed by the complete bounded BE-01 through BE-12 aggregate. No unresolved mandatory finding and no additional numbered finding.

Reviewer: fresh independent subagent `/root/docling_corrected_independent_validation`, GPT-6 family (precise model build not exposed), 2026-11-12. No delegation, memory, builder conversation/private reasoning or aggregate peer verdicts were used. The formal BE-REV-001 finding-only input was read. Historical reviewer reports, raw authority.json and execution-log were hash-only inputs. Shared-checkout read-only exception was explicit; every generated file, cache, copied dependency and process output belongs to this new external scratch.

## Frozen identity and authority

- Candidate `96f752d64ead1c98bd900891aaa94edfe4ebe5d3`, branch `feature/cmd-ingest-001`.
- Source candidate `1ebc16905300ba6d946383c05cdf686ac8ff7d36`; harness tree `7cc9e7f91abd7b59057c0fcb4e1a158517b7feb1`, all31 regular files' Git blob IDs and SHA256s verified.
- Delta base `4fd5f8252cd5d89924e0e01527dadca3ea1ee3b3`; aggregate base `11e8fccc23981b5449a51f2ef3f7d3ea565a062c`.
- Request SHA256 `dc9cc8a7d1efb224349c1257ff139f2731bd32c5216ca6ee268276e4fba47be7` was checked before reading. All19 request pins match.
- Corrected runner SHA256 `d27a7974fc9ede16038a9798623093df475f370d15cf1fa4b0e92f77d1fed21a`.
- Read AGENTS, all three repository policies, original CD-CMD-INGEST-GATE-A-001 interpreted with the pinned focus amendment/authorization, criteria.md, BE-REM-001, current README, full corrected behavior source/tests and applicable source diffs. No whole Gate-A or product authority was inferred.
- Aggregate scope is37 paths:33 planning/evidence paths and4 test-harness paths. No package/product, dependency/lock or root configuration change. The original57 minimal tests are unchanged; the stages change only adds behavior-test selection.

Opening and closing calculated the logical `git ls-files -s -z` SHA256 **before status**, with `GIT_OPTIONAL_LOCKS=0` and fsmonitor disabled. Both give `711e1297bfbdfdfd7eb1ad0db6f12b2265b0e4a0e8c425b2e4e496051638c598`. HEAD, branch and exact dirty status agree. All18,638 tracked file hashes,26 symlinks and8 protected metadata records match. Both dirty YAMLs, .venv, stores and exports remain unchanged. A full separate snapshot of74,733 supplied-runtime entries and24,485 supplied-controller entries also matches hashes, links, modes, inode/link counts and relevant metadata at close. See opening.json, closing.json and supplied-closing.json.

## Remediation delta: BE-REV-001 closed

Source inspection: `behavior.py` now invalidates eligibility before setup/launch (`begin_attempt`, around lines684-725), binds current input/oracle/settings/runner identity, and requires the latest matching immutable completion. `supervise` records the immutable supervised flag before Popen and publishes a successful terminal receipt only after the child ends. `admitted_document` (around lines1081-1135) requires that receipt for supervised attempts. `summarize` rechecks the attempt bound to saved chunk evidence. Empty admitted sources fail before supplemental payload construction. The direct entrypoint begins its own new attempt.

Fresh independent semantic reproduction in **both normal and -O**, using actual candidate code and own copies:

| Control | Observed evidence |
| --- | --- |
| Genuine current PDF conversion and chunks | Direct PDF conversion0; initial chunks0/report0. No fabricated successful result. |
| Genuine success → actual candidate-supervisor1-second timeout | Supervisor124; child SIGTERM(-15); earlier result bytes remained present but old attempt was ineligible. This is attempt invalidation proof, not a native reader refusal. |
| Stale report | report1; old chunk evidence refused. |
| Valid sibling with stale document | sibling retained; chunk command0 contains only current sibling; stale source explicitly skipped. |
| Only stale document | chunks1; actual_document_sources/results empty; failure occurs before generic supplemental sources; report1. |
| Fresh retry | Genuine direct conversion0, new attempt ID; chunks0/report0 restore admission. |
| Never-started child | Candidate supervisor executes prelaunch revocation, controlled Popen FileNotFoundError; old admission refuses; sibling remains valid. |
| Parent dies after actual worker success, before terminal receipt | Actual candidate supervisor parent deliberately exits17 at receipt publication after genuine worker success. Immutable attempt remains supervised; missing receipt refuses. |
| Immutable supervision identity | Changing only the attempt's supervision bit cannot relabel that successful worker as direct; semantic admission refuses. |
| Abnormal parent receipts | -15/time_limit,0/time_limit and17/no-reason all refuse; no setup-failure credit. |
| Actual input/settings/runner changes | Each independently refuses via semantic assertion; restoring bytes restores the positive, sibling controls remain eligible. |
| Final genuine direct success | New direct completion and current chunks/report all0. |

`delta.py`, delta-proof-normal/optimized.json, delta-ledger-normal/optimized.json and their logs contain exact argv, identities and assertions. The builder's remediation proof was not used to substitute for this execution. No code in the shared tree was edited for controls.

## Complete bounded criteria matrix

| ID | Outcome | Evidence and attribution |
| --- | --- | --- |
| BE-01 | PASS | Source/diff inspection; exact opening/closing tracked/symlink/protected comparisons; own physical copies only. |
| BE-02 | PASS | **Inspected** successful standard uv compile and wheel-only --require-hashes private sync receipts, lock/package/assets evidence. First historical invalid --no-build compile attempt remains a setup failure; later standard compile succeeds. **Fresh** private probes/import origins confirm Docling2.150.0, RapidOCR3.10.0, Certifi2026.10.23 and Certifi floor. No installation/network repeated. |
| BE-03 | PASS, bounded | **Fresh** -I -S -B runtime, -O second lane, owned target/assets/config/caches; six isolation controls pass in each mode. Python-visible connection, outside read/write refused; own writes permitted. Native libraries are not OS contained. |
| BE-04 | PASS | **Fresh** full37-case configured evaluate in each mode:30 genuine format fixtures plus7 controls.27 actual Docling calls,10 early structural/size/format refusals,0 setup errors. Six native empty/error outcomes are distinguished from supported meaningful documents. |
| BE-05 | PASS | **Inspected** raw30-document outcomes/default chunk limitations retained: PDF first-page furniture omission, hidden-row/column leaks and formula-cache acceptance; isolated scanned heading absent from default chunker. **Fresh** configured OCR/order/table/hidden/notes controls and original oracles. No alternate reader supplies text; Office audit returns structural facts only. |
| BE-06 | PASS | **Fresh** public Docling body/furniture serializer, isolated-heading setting and unambiguous notes preserve required source markers. PPTX comments stay excluded. Unsafe spreadsheet cases refuse before native conversion; visible admitted source text remains. |
| BE-07 | PASS, bounded | **Fresh**324/324 per mode (21 admitted docs+6 payloads ×3 strategies ×4 limits64/128/512/1024). No-override512 separately passes81/81 per mode. Independent direct-tokenizers recount checks all2,017 saved chunks per mode, actual prepared prefix and specials, with0 discrepancies/overflows. Prefix alone counts6 including2 specials. Server agreement/vector quality remain unqualified. Recursive/fixed remain test prototypes. |
| BE-08 | PASS | **Fresh** genuine interruption/receipt/currentness proof above; refused/empty/error/stale docs absent. Original marker, exclusion and ordered-source oracles pass independently. Recount confirms prepared limits; recursive/fixed exactly reconstruct public Docling serialized source. |
| BE-09 | PASS, bounded | **Fresh**39 supervised matrix commands per mode, all expected0/no limit reason. Normal183.34s cumulative, longest32.82s, peak sampled RSS1,998,274,560 bytes; optimized189.16s, longest33.67s, peak2,005,712,896 bytes. Each run about1.63GB logical bytes. Actual timeout controls terminate only owned groups and keep logs. Historical setup/assets caps inspected. Sampling is not OS containment. |
| BE-10 | PASS | **Fresh**68 minimal cases normal/-O (57 retained+8 original behavior+3 lifecycle regressions), both0. Fresh private Ruff/format both0 on27 Python files using exact root config. **Inspected/hash-bound** parser6/39, engine7/24 per mode and private mypy27-source exit0; current source equality verified. No working-.venv runtime/static use. |
| BE-11 | PASS | **Fresh** evaluate/chunks/report CLI, no-override default, meaningful distinct conversion/admission/setup phases, stale/empty/report errors and retry. Exact argv/exits/logs retained. Zero embedding/service/store calls. |
| BE-12 | PASS, bounded | All request/source/archive pins verified;8,148 member bytes/sizes verified (67,376,725 raw bytes), current corrected-normal/optimized builder receipts inspected separately from fresh results. This report supplies independent proof attribution and closing integrity. Full-framework/installed profiles, model window, embeddings/storage, human acceptance and delivery remain open. |

Per mode the37 outcomes are26 expected passes,1 characterization and10 admission refusals. Of27 native calls, six are expected empty/error outcomes (`corrupt.pdf`, `over-pages.pdf`, blank-image/encrypted PDF, empty DOCX/PPTX);21 meaningful documents enter chunks. Expected-negative passes never imply those inputs are supported conversions.

## Commands, exits and retained debt

The exact machine-readable command/semantic ledger is **ledger.json**. Its matrix child receipts record the expanded39 argv per mode, including actual supervised attempt IDs. The controlling interpreter is `/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13` (SHA256 `e2adf1814122d8b26166917ef7d294d7426963e0f59e28d0d5aef773f67c4bb0`). All runtime/selftest entries use `-I -S -B`, optimized entries add `-O`.

- Frozen run.py selftest with pinned manifest and separate private scratch:0/0,68/68 cases.
- Own copied behavior.py evaluate --chunk-tokens64 128 512 1024:0/0; report324:0/0; chunks with no override:0/0; report default512:0/0.
- Independent reviewer-recount-v2.py:0/0;324 cases and2,017 chunks each,0 mismatches.
- Copied pinned Ruff check --no-cache and format --check --no-cache with copied exact root config:0/0.
- `uv run --offline --frozen --no-sync --no-python-downloads python -B` board validate, board render --check, documentation lifecycle and package metadata:all0; **administrative-only maintenance-.venv exception**, own UV cache.
- Owned, aggregate-range and cached whitespace:all0. Full dirty-worktree whitespace remains **2** for the preexisting models-config.example.yaml lines130/142. Root-product lint/collection/registry-format debt remains unwaived; no broad product suite or live endpoint was run.
- Expected remediation exits1/17/124 are described above; they are intentional semantic control witnesses, not ignored unexpected failures.

Reviewer-only scratch corrections are disclosed in ledger.json. An early inspector assumed an absent historical field, and one display treated an integer count as a collection. The first recount helper, outside the owned run, was correctly refused when Torch traceback machinery tried to read that helper; it was moved inside the owned run. A subsequent supplemental reconstruction check initially compared raw row strings with Docling Markdown; the corrected reviewer expectation uses the public Docling serialization being chunked. Tokens/original markers already matched. All prior recount logs are retained. These errors earn no product rejection or passing credit; no shared input was written.

## Mandatory findings, scores and limits

- **BE-REV-001: CLOSED** by fresh delta proof and complete bounded aggregate.
- **Additional mandatory findings: NONE.**
- Advisory evidence-coverage score: **9.3/10**. Advisory overall bounded-slice score: **9.2/10**. These reflect strong direct execution and independent semantic/token checks, with setup/raw/profile/mypy proof intentionally inspected and native containment remaining bounded. No earlier numeric score or verdict is inherited.

No arbitrary malicious local-owner tamper resistance, OS sandbox, all-document compatibility or production readiness is claimed. Oracles cover distinctive content/order/exclusions in genuine synthetic documents, not all semantics of every real-world file. This result applies only to the frozen test-only standalone Docling behavior slice. It grants no whole Gate-A/product, acceptance, push/merge/deployment/release or delivery authority.
