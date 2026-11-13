# INGEST isolated end-to-end independent validation

**CHANGES_REQUESTED**

Reviewer: fresh independent validation agent `/root/ingest_e2e_independent_validation`, GPT-6 based Codex (exact backend build not exposed). Date: 2026-11-12T22:31:56.771249+00:00. Mode: full bounded read-only E2E review, including amended scope. No delegation. No memory, prior reviews, peer verdicts or builder private reasoning used. Builder facts/results and actual execution receipts were inspected as pinned evidence, never adopted as the verdict.

Candidate `cae6aa4c183f013c19d10af4358dcf93fd189367`; source candidate `c97777366671006f56866aa92898aaffcec524d6`; base `96f752d64ead1c98bd900891aaa94edfe4ebe5d3`; branch `feature/cmd-ingest-001`. Governing request hash `4748408644b616c28a9f739f96f9ef47567ed84b347fe8b286000e62465e26c4` was checked before reading. All 17 pinned request input hashes matched. Authority is the explicit maintainer request and E2E scope amendment, original directive within that amendment, AGENTS.md and repository policies. Full authority.json and prior-review reports were not displayed or used. Other changed paths were inspected name-only. Source review covers all of e2e.py/test_e2e.py and the complete README/stages.py delta; behavior.py's unchanged identity and relevant reused mechanics were inspected.

## Mandatory finding

### E2E-IV-001 — report accepts changed conversion source

Severity: **Medium**, mandatory integrity/acceptance-criterion violation. Affects `tests/readiness/ingest/e2e.py:872` (report), the source identities carried at lines 410/445, and regression coverage in `tests/readiness/ingest/tests/test_e2e.py:107`.

Requirement: EE-07, `end-to-end-evaluation/criteria.md:17`: source change must refuse reporting. The original directive at line 44 also requires a changed source/config/envelope to invalidate the old run. The amendment retains behavior.py's independently verified bytes.

Observed: `report()` verifies its own e2e.py hash and hashes of the four saved E2E JSON artifacts. It does not compare the current behavior.py bytes against the conversion runner hashes already carried by corpus conversion attempts. A copied source can therefore change without report refusing its old success.

Canonical-origin reproduction: in a new physical reviewer-owned `.friday_test/runs/docling-behavior-e2e-review` layout, exact archived source and actual normal/optimized result receipts first produce CLI exit 0/status PASS. Append `raise RuntimeError("Independent disposable-source tamper")` to only the copied `source/ingest/behavior.py`; the unchanged canonical e2e.py `report --run-root <copy>` still produces exit 0/status PASS, in normal Python and -O. Original behavior SHA256 is `d27a7974fc9ede16038a9798623093df475f370d15cf1fa4b0e92f77d1fed21a`; changed copy SHA256 is `8afbf6497cdfeb1a05f46a75cd87cc89e8d24c4f11dd293214aaf6609e9d1bae`. This is a call-phase false PASS, with successful controls; it is not rejection credit from a setup failure. See `stale_cli.py`, `canonical-stale-source-normal.json`, `canonical-stale-source-optimized.json`, and the CLI stdout/stderr files.

Risk: the reusable report can endorse stale extraction/source evidence after the conversion runner changes, violating the promised run/source binding. This does not show that the recorded original c977 experiment failed; that execution remains attributable to its frozen bytes.

Bounded fix: make reporting verify the current conversion runner against an immutable per-run source binding (including the already recorded behavior runner digest), in addition to e2e.py. Fail explicitly on missing/mismatched binding before PASS. Add clean positive and changed-behavior-source canonical CLI regressions in normal/-O, while retaining failed, missing, modified-artifact and changed-e2e-source controls. Changes can remain in e2e.py, test_e2e.py and necessary README/evidence documentation; behavior.py and production code need no change. Preserve original live evidence/stores as evidence of c977; do not rewrite it or relabel it as execution of corrected code. Fresh offline proof can validate the reporting correction; any later inference needs separate authority and budget.

## Complete EE matrix

| Criterion | Outcome | Evidence and coverage | Advisory component score |
| --- | --- | --- | --- |
| EE-01 | PASS | Full selected source diff is test-only plus planning artifacts. Opening/closing boundary pins, 18,654 tracked hashes, 26 symlinks, 8 preserved records; index/status/HEAD/staging preserved. All 149 wheel payload members match committed baseline source; no package source change in range. `origins.json`. | 9.0/10 |
| EE-02 | PASS | Saved genuine Docling conversions cover native/scanned PDF (OCR), DOCX, XLSX and PPTX. Corpus/chunk/oracle identities checked. 41 document/512 rows and 40 long-DOCX/128 rows per mode. Corrupt PDF conversion failure and missing-formula-cache structural refusal are absent from corpus, wire input attribution and stores. `attribution.json`, archive attempts/documents/chunks. Full 30-document standalone matrix was not rerun or newly claimed. | 8.8/10 |
| EE-03 | PASS | Inspected pinned LiteLLMEmbeddingService construction and transport hooks; no direct embedding HTTP path. Recorded 4 document batches and 5 query broker calls per mode match wire hashes and task prefixes. Native status observations surround every request and preserve selected model/context/digest. Wheel origins match baseline. Local tokenizer usage is explicit; server token-equivalence remains unqualified. | 8.7/10 |
| EE-04 | PASS | Inspected count/model/index/dimension/finite/nonzero validation and retry=0, reservation before transport. 29 independent controls include malformed response cases, request/vector/token exhaustion, invalid reservations, and contention. Saved 18 POSTs, 172 vectors (162 document +10 query), expected 768 dimensions; shared budget57/64 requests and41556/131072 prepared tokens. Raw response bodies were not retained, so raw-response replay is not claimed. | 8.5/10 |
| EE-05 | PASS | Fresh independent reopen of both copied physical stores checked all162 rows against corpus: exact text, recomputed content hash, source, chunk index, budget, protected flag and absent description. Persisted vectors are finite/nonzero/768-dimensional. Two fresh collections per mode; refused sources absent. `fresh-reopen.json`. | 9.0/10 |
| EE-06 | PASS | Saved real query vectors cover four formats plus override; fresh separate-process reopen used public precomputed-query-vector seam and an embedding object that always refuses. All10 retrieval ID lists identical, expected source rank1, no embedding or network call. This establishes persistence/retrieval consistency; known-source query text is not a semantic-quality evaluation. | 8.8/10 |
| EE-07 | FAIL | Run IDs and saved corpus/HTTP/store/reopen artifact hashes are attributable; changed/missing HTTP and failed/stale result controls refuse. Canonical CLI nevertheless accepts changed behavior.py source in both modes: E2E-IV-001. Python-visible guards prevented ambient Chroma cache opens; native limits remain. | 6.0/10 |
| EE-08 | PASS | Fresh 74-case normal and optimized stdlib selftests, Ruff check/format (29 files) and administration pass. Private mypy exit0/29 files receipt inspected, with byte equality confirmed for every checked Python file; mypy was not rerun. Manual scope/version/setup-attempt/remaining integration limits match evidence. Test coverage gap is captured under EE-07. | 8.8/10 |

Overall bounded component score: **8.4/10**. This is advisory and does not override E2E-IV-001. No whole Gate-A, production /ingest, 9.5-readiness, acceptance or delivery conclusion is supplied.

## Fresh versus inspected evidence

Freshly reproduced: opening/closing pins; safe archive/member hash verification; all149 payload members of four wheels versus Git baseline; static typing receipt source equality; normal/-O74-case stdlib selftests; focused Ruff/format;29 additional offline controls; corpus-to-chunk-to-wire-to-store attribution; copied-store reopen and10 identical retrieval lists with no embedding/network; prevented network canary; canonical normal/-O stale-behavior witnesses; board/dashboard/docs/metadata and whitespace administration.

Inspected rather than rerun: actual Docling conversion/OCR and its source/oracle/admission attempts, live Friday-LLM/Nomic requests, server status/settings/operator-window evidence, original store creation, builder separate-process reopen receipts, package build/install/setup commands, private mypy receipt. No live endpoint/provider/model call, download, install, product suite, full Gate-A or 30-document standalone matrix was executed by this reviewer. Docling2.150.0, Core2.106.0, RapidOCR3.10.0, LiteLLM1.100.1, Chroma1.4.0, Certifi2026.10.23 and Friday packages0.1.0a4 are supported by saved metadata/receipts; reopened private versions independently confirm Chroma, Memory and Certifi. The original dateutil resolver conflict and mistaken distribution lookup are documented setup failures and earn no refusal/conformance credit.

Original evidence archive SHA256 `64034d38f01f1dc2791da765f0a39f02b58df0bce40af3fcc3ba8a7d652a452c` matches all367 indexed regular members,41,960,997 expanded bytes, no duplicate/traversal/symlink members. It was extracted only into reviewer scratch. Only extracted store copies were reopened; native Chroma can mutate those reviewer-owned copies. Supplied stores/targets/tools and archive remained read-only.

Transport accounting:27 recorded HTTP requests/mode =9 GET/POST/GET groups. Across modes:54 HTTP requests,18 embedding POSTs,36 status GETs,172 vectors and41556 local prepared tokens. Including3 prior reserved status requests:57/64 cumulative requests. Response usage is zero, so server/local count agreement and model-context-ceiling overflow behavior are unqualified.

## Containment observation and limits

The independent reopen audit recorded **two prevented open attempts** at `/Users/chuckrussell/.cache/chroma/telemetry_user_id`, despite Chroma anonymized telemetry being false. The guard raised PermissionError before file payload access or mutation; no cache contents were read. Chroma1.4.0's ProductTelemetryClient hardcodes that path under Path.home(), and catches file-access errors. This is attempted/prevented access, not an actual successful read, a detected completed change, or proof that environment variables alone neutralize Chroma. HOME was not reassigned. The successful result retains the attempts explicitly; earlier reviewer reopen trials intentionally exited1 because their overly strict accounting treated any denied attempt as failure. After identifying the permitted prevention outcome, the final trial exits0, with zero network attempts, zero embedding calls and zero successful outside effects. The post-run socket canary was refused before connecting. See `fresh-reopen.json`, `network-denial-canary.json`, `reopen.stderr` and `reopen-diagnostic.stderr`.

Python audit controls are not an OS sandbox and do not prove prevention of all native-library I/O. The existing stated native residual limit remains. Request provenance relies on inspected exact hook code and saved request/response-hash receipts; original raw response bodies cannot be replayed. No current LM Studio setting or operator window is asserted from old evidence, and no user stores/settings or dirty YAML content was opened by this reviewer. Protected YAML was hashed only for preservation. Repository administration scanners operated as read-only checks and emitted no peer-review or authority-history text.

## Commands and exits

Exact argv/cwd/exits and stdout/stderr paths are retained in `command-ledger.json`; all external commands carried GIT_OPTIONAL_LOCKS=0 and PYTHONDONTWRITEBYTECODE=1. Test commands used qualified base CPython3.13.10 `-I -S -B`; optimized lanes also used `-O`. All output/cache/temp paths were rewritten to reviewer-owned scratch; supplied receipt argv was not replayed with supplied caches.

| Check | Exit/outcome |
| --- | --- |
| Frozen run.py selftest + pinned manifest + own normal scratch | 0;74/74 |
| Same with -O + distinct own scratch | 0;74/74 |
| Private Ruff check --no-cache --config own exact root rules | 0 |
| Private Ruff format --check --no-cache,29 files | 0 |
| controls.py | 0;29 checks; synthetic vectors earn no live credit |
| attribution.py corrected | 0; full source/corpus/chunk/wire/run accounting |
| reopen.py final | 0;162 rows,10 retrieval ID lists;2 prevented cache opens |
| stale_cli.py, normal and-O | Harness exit0; both clean CLI and changed-behavior CLI return0/PASS, demonstrating E2E-IV-001 |
| uv run --offline --frozen --no-sync --no-python-downloads python -B board validate | 0;36 tasks |
| Same administrative flags, board render --check | 0 |
| Same flags, documentation lifecycle via own wrapper | 0;1114 Markdown files; wrapper only rewrites nested board UV invocation to same safe flags |
| Same flags, check-package-metadata.py | 0;18 projects |
| git diff --check base..candidate, staged and owned worktree paths | 0 each |
| closing-integrity.py | 0; all tracked, authority, preserved metadata, symlink, index, HEAD/branch and status pins match |

Reviewer helper failures are retained and are not product failures or rejection evidence: the first wheel helper parsed the filename with the wrong separator (KeyError, exit1), then corrected and verified all149 members; the first attribution helper assumed attempt directories instead of named files (AssertionError, exit1), then corrected and passed; two initial optional reopen trials exited1 on deliberately overstrict denied-open accounting, then final correctly classified prevented attempts and passed. No candidate repairs were made.

## Integrity and handoff boundary

Opening index was collected before status; logical SHA256 `92e8bb95a32757d97fd237d39e6dfb7dc5178f0b904c49586a819024831b252b`. Opening boundary matched18,654 tracked file hashes,26 symlinks,8 retained metadata records, HEAD/branch and status. Expected dirty state remains exactly the two specified example YAML edits and `.friday-old/`; no staging change. Closing repeated logical index before status and all pins, including all17 authority/input hashes, with no mismatches. `opening-integrity.json` and `closing-integrity.json` carry exact results.

All reviewer writes are confined to `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-e2e-independent-3e_a67gm` (new external private scratch, canonical path, reviewer UID). No Git mutation, source repair, commit, council, production construction, acceptance or delivery was performed or authorized. The next step is bounded reporting-source binding remediation and a new frozen independent review; existing actual experiment evidence remains historical evidence of its original pinned source.
