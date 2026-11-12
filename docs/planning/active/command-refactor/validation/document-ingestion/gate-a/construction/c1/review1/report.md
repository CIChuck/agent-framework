# INGEST-C1-INPUTS independent implementation validation

**VERIFIED** — C1 synthetic fixture/input-preparation delta, followed by the full bounded retained offline-controls/input-preparation aggregate. **No mandatory findings. Advisory score: 9.2/10 for this bounded implementation only.** This is not A0–A4 readiness, product readiness, human acceptance, delivery authorization, or a 9.5 advancement.

## Identity and authority

- Reviewer: fresh native validator `/root/ingest_c1_independent_validation`, GPT-6 agent; exact serving model identifier is not exposed. Date: 2026-11-12 UTC.
- Repository: `/Users/chuckrussell/Dev/gendev/agent-framework`.
- Base: `2920d0dd295e9ecb1b35acc1d646cba18149c60d`.
- Frozen candidate: `48bc7c973a8de00ec79117ece4792455e7164ccd`.
- Candidate root tree: `d5494d2f45a1f252ba30a29073ed78d71b294abf`.
- Source candidate: `e07892f0f3ca3291d91dd7686dd77d8f05425417`. All 29 selected harness files are byte-identical between this source commit and the frozen candidate.
- Branch at both boundaries: `feature/cmd-ingest-001`.
- Request SHA256 verified **before reading**: `8bc06f8b0bd755ae2394102330f645daf132ed9fc42759d0823634814cbc3b56`.
- Supplied boundary SHA256: `fb9235fbb44448808f590d6a531fa88e573fecc0d6391507d7eb0e590e6e0713`.
- Private scratch: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c1-validator-P2CzAi`.
- Final reviewer-created exact candidate manifest SHA256: `1fa29eeb336b637c590adb105582e19aea67c07e516c8db7c49a3d1846da6e1d` (`candidate-manifest.json`). Files were exported with read-only Git operations, each candidate blob ID and SHA256 independently matched to the pinned selection, and all selected file bytes were checked again at close. The private export is read-only.
- Interpreter SHA256: `e2adf1814122d8b26166917ef7d294d7426963e0f59e28d0d5aef773f67c4bb0`; bootstrap SHA256: `70e03f2215282e2d4aa6fd0a58161ce0b9858981a114caba49f4826f5833599c`.

Read authorities: AGENTS.md, engineering/lifecycle/independent-validation policies, Friday development-board skill, pinned directive, C1 continuation and implementation criteria, execution contract, isolation requirements, readiness plan, effects envelope, exact construction approval and static-tool approval/profile. All 17 request authority pins matched both current bytes and candidate blobs. The separately referenced construction approval matched SHA256 `dc3b4a1d20054256310cc0b6464d18c782b04326fe315b09ea5f96911e66845f`. The approval and C1 continuation supply the operative construction authorization despite retained draft-era labels in the directive. The current C1 routing agrees with this component review and keeps full qualification open.

The permitted shared-checkout exception was used for read-only identity, Git blobs, authority and administration. No worktree, staging, commit, repair, cleanup, board mutation, network request, dependency installation, application import, actual resolver/converter/tokenizer/OCR/model/store/provider call, delegation, or council iteration occurred. No memory or peer/historical validation report was used. Builder conclusions were not correctness evidence. Operational launcher sources were inspected before adaptation; retained evidence was audited by hashes rather than accepted as a verdict.

The controller clarified the separate required administration lane during the review: existing documented `uv run` repository scripts may use the existing working interpreter, without sync/install, under offline/frozen/no-sync/no-download/no-env-file settings and reviewer-owned UV/XDG/cache/temp paths. This does not permit working `.venv` use in the harness, static checks, or upstream profiles. No candidate or authority bytes changed. The newly communicated resolver-tool approval was held outside this frozen review: the pinned candidate's proposal remains unactivated and no resolver execution was performed.

## CI-01–CI-10 matrix

| Criterion | Outcome | Fresh evidence and source assessment |
| --- | --- | --- |
| CI-01 Authority and preservation | PASS | Exact request/boundary/interpreter pins; all 17 authority pins match candidate and current bytes. Exact diff has 38 declared paths and no extras. Only the five named implementation/README files, literal expectations, and four test modules change executable behavior. The other 19 harness paths are byte-identical to base. Opening and closing preserve all 18,229 tracked-file hashes, 26 symlink targets, all 9 protected metadata records, HEAD, branch, logical index and status. `opening-summary.json`, `closing-summary.json`, `administration-audit.json`, `final-audit.json`. |
| CI-02 Complete deterministic inputs | PASS | Exact 6 PDF / 6 DOCX / 10 XLSX / 8 PPTX, deterministic repeat bytes and 30 unique SHA256 values. Independent assertions inspect all PDF xref offsets/object counts/stream lengths/page counts, raster dimensions and pixels, and independently derive the PDF Standard Security key and decrypt the password fixture. Office part content/order and literal markers were independently checked. Normal and optimized manual publications yield the same manifest hash `e59b85645888ab1277043e21574fcecd2d537cf007447448109310de64ac45c0`. `fixtures.py:488,621`; independent cases 01–03; manual receipts. |
| CI-03 Independent oracles | PASS | Literal 30-case JSON contains expected markers, exclusions, counts and extract/refuse/characterize dispositions; there are six refusal dispositions. Generation does not consume converter output. Independent assertions compare the literal case names and source markers against actual generated containers; excluded Office markers remain present in source inputs to challenge later selection policy. `fixtures/expectations.json`; `fixtures.py:621,1083`; independent case 01. Scanned-image text is a literal future OCR expectation, not inferred extracted text. |
| CI-04 Structural facts and bounds | PASS | Independent positives cover ordered Word body/table content; workbook ordering and hidden sheet/row/column distinctions; slide/shape hiding; notes versus comments; included formula missing/error caches; excluded hidden formula suppression; external-relationship no-fetch code; facts with `text_extracted:false`. Explicit call-phase refusals cover archive escape, XML DTD/entity declarations, cell-coordinate overflow and merged expansion. Candidate cases also execute duplicate/expanded/member bounds, UTF-16 declaration, wrong format/content type and invalid boolean checks in both modes. `fixtures.py:43,793,821,839`; independent cases 03–04; committed fixture tests. |
| CI-05 Publication integrity | PASS | A new physical absent destination and complete 30-case oracle are required before publication. Exclusive creation and mode 0444 observed for all published artifacts. Fresh verification accepts the complete set and refuses same-length wrong bytes, extra files and a symlink alias; incomplete oracle leaves destination absent. A stop callback during publication leaves exactly three partial inputs and no ready manifest. Repeated manual preparation refuses, preserving the finished inventory. `fixtures.py:1083,1160`; independent cases 05–06; manual prepare/repeat/stop receipts. |
| CI-06 Writer ownership | PASS | The command holds its ledger lease over fixture publication and appends with the held token. Fresh assertions exercise live same-instance positive append; foreign instance, unrelated/released token, mismatched PID and stale tip refusals; a competing normal writer fails while the lease is held. Required exceptions run under `-O`. `ledger.py:26,96,103`; `stages.py:263`; independent case 06 and appended committed ledger test. |
| CI-07 Manual command and reports | PASS | Both normal and optimized frozen CLI flows run: preflight/init/prepare-fixtures/report/all and each A0–A4 selector/prepare-model/stop/rejected stopped prepare/report after stop. Preflight creates no unit-project state; all 30 lengths, hashes and read-only modes match published inventory. Ledger events remain only init and preparation finish; no promotion occurs. Reports exit 3 with INCOMPLETE, `ledger_witness_only`, `current_bytes_revalidated:false`, `converter_qualified:false`, and `full_readiness:false`. A0–A4/all/model preparation remain blocked exit 3; duplicate/stopped effects refuse exit 2. `manual-summary.json`, `optimized-manual-summary.json`, command appendix; `stages.py:62`, `reports.py:9`. |
| CI-08 Retained controls | PASS | Independently compared exact original test-function source bodies against base: all 43 remain unchanged. Final exact-manifest loader executes 54 selected tests without skips in normal mode and 54 under `-O`, both exit 0. Full bounded C0 source was inspected, including startup/path/probe/dir_fd/thread/process/network guards, private environment, strict JSON, export, metadata detection, ledger/promotion/budgets and fake model window. Eight additional reviewer-owned test cases pass in each mode with 28 explicit refusal witnesses per mode and no application modules imported. `administration-audit.json`, selftest receipts, `independent-final.py` and final stdout/stderr. |
| CI-09 Static and administration | PASS | Hash-verified private copies of Ruff/config and all 1,177 mypy-target files; no downloads. Focused root-rule Ruff and format pass for explicit 25 Python sources. Adapted launcher arms the committed Guard before mypy imports and uses only private target/config/cache/temp; 25-source mypy passes. Board validates 36 tasks; dashboard --check is current; documentation lifecycle checks 1,090 Markdown files; metadata validates 18 pyprojects; owned/cached/base-to-candidate whitespace checks all exit 0. All 12 raw/gzip digest pairs match. `static-selection.json`, `ruff-check.json`, `ruff-format.json`, `mypy.json`, `admin-commands.json`, `administration-audit.json`. |
| CI-10 Independent review and limits | PASS | Fresh native validator, no inherited implementation discussion or private reasoning, no memory/peer/historical report reliance, no nested agent. C1 delta inspected first, then the full bounded retained aggregate; no previous verdict carried forward. Own candidate Git-blob export, exact manifest, normal/optimized tests, manual flows, independent assertions, static and administration receipts are retained. Closing shared integrity is exactly equal to opening. Distinctions and exclusions below remain explicit. |

## Commands and exits

The complete literal argv, cwd and expected/observed exit for every final test/manual/static/admin command is retained in **`command-appendix.md`**, with raw stdout/stderr in the named JSON receipts. Reviewer driver source is retained, so the frozen controls and private paths are concrete and reproducible.

| Executed check | Exit / observed result |
| --- | --- |
| Initial `shasum -a 256` request; boundary/interpreter | 0; all expected digests match |
| Initial `GIT_OPTIONAL_LOCKS=0 git ls-files -s -z` piped to SHA256, before status | 0; `dc6c227a62e57367a9e3f4c7eb24941e77a6f1556f95da5155bd05fde8230645` |
| Opening audit / Git-blob export / private-tool copy | 0; no boundary or pin mismatch |
| Final committed-loader selftests, normal and optimized | 0 / 0; 54 / 54 pass |
| Reviewer independent assertions, normal and optimized | 0 / 0; 8 / 8 pass, 28 / 28 refusal witnesses |
| Normal and optimized manual preflight/init/preparation | 0 each; both publish 30 exact inputs |
| Normal and optimized duplicate preparation | 2 each; explicit existing-destination refusal |
| Normal and optimized report before/after stop | 3 each; INCOMPLETE |
| Normal and optimized all, A0, A1, A2, A3, A4 and prepare-model | 3 each; BLOCKED_NOT_ACTIVATED, effects false |
| Normal and optimized stop / stopped preparation | 0 / 2 each |
| Ruff check / format check / guarded mypy | 0 / 0 / 0; 25 sources |
| Board validate / dashboard render --check / docs / metadata | 0 / 0 / 0 / 0 |
| Owned / cached / base-to-candidate diff --check | 0 / 0 / 0 |
| AST test retention / evidence-pair / diff-scope audit | 0; 43 bodies, 12 pairs, 38 exact paths |
| Closing audit / final tool/export audit | 0 / 0; shared boundary identical and supplied/private tool files unchanged |

The mypy guard explicitly refused two undeclared sysconfig probes for `bin/Modules/Setup` and `Setup.local`; mypy completed with zero issues. These are refusals before probes, not reads or a setup failure. No production/cache write is excused.

Reviewer setup corrections are retained and are not candidate failures: an initial independent assertion expected seven rather than six refusal dispositions, used a case-sensitive alias-message expectation and a different budget-message phrase; corrected assertions pass in fresh output roots. An early reviewer-generated manifest preserved the source commit's root-tree metadata while naming the final candidate; the final exact manifest corrects its tree to the candidate tree, and the decisive selftest/manual/static/independent lanes all use that final manifest. No failed setup or collection earned negative-test credit, and no candidate repair occurred.

## Mandatory findings

None. No unmet CI-01–CI-10 requirement or high-severity candidate finding was established in the bounded review.

## Fresh execution versus inspection and unrun scope

Freshly executed: boundary and authority hash checks, independent Git-blob export, exact test-body comparison, committed normal/optimized selftests, normal/optimized frozen manual flows, normal/optimized independent assertions, private Ruff/format/mypy, required administrative selectors, owned/cached/range whitespace checks, gzip/raw audit and closing integrity.

Inspected: pinned authority/current routing, complete bounded harness source and C1 source delta, literal oracles, appended tests, operational tool launchers. Retained builder evidence was hash-audited; it does not replace current execution or prove correctness. Repository administrative validators inspect repository documents as inputs, but historical verdicts were not used as decision evidence.

Unrun and unqualified: actual A0 resolver/download/install profiles, A1 dependency import behavior, A2 real reader/OCR/schema interoperability/extraction/chunking/provenance, tokenizer/model behavior, A3 model/status/network calls or service windows, A4 full-readiness aggregation, application/Memory/Chroma/graph/WAL/provider behavior, whole-repository product tests and broad root lint/type gates. No supplied real document was selected. Whole-worktree whitespace was not rerun because it would inspect the explicitly excluded preserved dirty YAML; only required owned/cached/range checks were run. The two user YAML files were hashed without displaying their content; `.friday*` received only the specified metadata observations, apart from Git's required status inventory of names.

Python-visible preventive controls are not an OS sandbox. Native tools/extensions retain separately classified detective/residual limits. This review exercises controlled protocols and synthetic containers; it does not qualify arbitrary adversarial native code, malicious local-owner rewrites, real Office/PDF readers, OCR output quality or production integration. The score reflects the bounded implementation's deterministic, explicit and reproduced controls, with these limits intact. It authorizes no acceptance, merge, push, deployment, activation or remediation loop.

## Closing integrity

`opening.json` equals `closing.json` exactly: same HEAD and branch, logical index `dc6c227a62e57367a9e3f4c7eb24941e77a6f1556f95da5155bd05fde8230645`, full status, 18,229 tracked hashes, 26 symlink targets and all 9 protected records (including absent repository `.friday_test`). The dirty YAML hashes and metadata are unchanged. `.friday`, `.friday-old`, `.venv`, exports and their specified records are unchanged. Supplied request/boundary and all supplied/private static-tool file hashes remain unchanged. No shared or supplied cleanup was performed; all reviewer artifacts remain in the private scratch.
