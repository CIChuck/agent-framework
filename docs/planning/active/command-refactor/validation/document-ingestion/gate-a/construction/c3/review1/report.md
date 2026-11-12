# INGEST-C3-OFFLINE-SOLVER independent validation

**VERIFIED** — the C3 delta and full bounded retained C0–C3 component aggregate satisfy CS-01–10. No mandatory finding was established. This is current-source implementation validation of an incremental offline component, not full HR/A0–A4 readiness, a 9.5 readiness result, acceptance, advancement, or delivery authorization.

Reviewer: fresh Codex validation subagent `/root/ingest_c3_independent_validation`, GPT-6 family (exact backend build not exposed), 2026-11-12. No nested delegation or memory lookup. Review workdir: `/Users/chuckrussell/Dev/gendev/agent-framework`. All reviewer outputs, source exports, target copies and caches are in this external private directory. No checkout, supplied input, supplied target or supplied cache was written. No repair, cleanup, staging, commit, worktree, network, download, install, actual index resolution, product import, Docling/tokenizer/model/provider call or store effect was performed.

## Frozen identity and authority

- Request was SHA256-verified **before its contents were read**: `e48e102babda06d8e1c374bc1ed9db3db0b230d8631fabd6de0501e0bc3a36c2`. Reviewer copy: `request.json`.
- Candidate: `5c37bf0382699cda2234e73407065f1a6455e2a6`, branch `feature/cmd-ingest-001`, tree `0e7bdf2e495e2712a576cc3f779978421aefdc7b`.
- Delta base: `ba5a41f80d446f9bebb87053fb5b21eb441e6e2c`; exact range is base through candidate. All 45 changed paths match the request. Executable/source behavior changes are confined to `tests/readiness/ingest/manifests.py`, `tests/readiness/ingest/tests/test_manifests.py`, and its README.
- Harness source commit: `75d880e8b2d7ceb855f7497b2639b6d6b8effb98`, source tree `4c97b4caf623c11f87f0b3b4e3047c160528a998`. The 29 current candidate blobs, modes and SHA256s exactly equal its approved selection manifest: `688c258e9772403fde49bd646dc43f52613dc820ff4e70602ef2b02c0491c80e`. Both reviewer exports remain read-only and byte-identical.
- Interpreter: `/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13`, SHA256 `e2adf1814122d8b26166917ef7d294d7426963e0f59e28d0d5aef773f67c4bb0`; bootstrap SHA256 `70e03f2215282e2d4aa6fd0a58161ce0b9858981a114caba49f4826f5833599c`.
- Boundary SHA256: `42ca0ac205b34d102f713db9061892d83488441ddb1032f3cc6da4514ec3a84c`; logical index SHA256, collected before status at both boundaries: `668cb8c7e392cc3ff37d1d5cf56b19505b40c2e08cb63b2c58546c3dadc80b81`.

Read `AGENTS.md`, engineering/lifecycle/independent-validation policies, exact approved directive, execution/effects/isolation contracts, construction approval, C1 continuation, C0/C1/C2 requirements, C3 implementation scope, and the exact private typing/parser/engine profiles and activation receipts. All request pins match at opening and closing. Immutable proposal headings are interpreted with their explicit subsequent exact activation receipts; their old labels do not activate actual stages. The C3 profile approval authorizes this offline engine only. Current status remains `in_review` and actual A0–A4 activation is false; this report makes no repository state transition.

## Execution evidence and reproduction

The C3 source delta was inspected first. An initial current-source startup/manual rehearsal was retained in `formal/commands.json`; it is supplemental and is not the final aggregate basis. The C3 engine selector and independently authored delta probes then completed. The full retained parser, minimal and frozen manual aggregate was subsequently rerun in `aggregate/`.

| Executed lane | Current result | Exact commands/output |
| --- | --- | --- |
| C3 engine selector, normal and `-O` | Exit 0 each; 7 positive + 24 actual-call refusal cases per mode | `engine-delta.json` |
| Independent solver probes, normal and `-O` | Exit 0 each; 27 checks per mode: 6 positive and 21 refusal/control witnesses | `delta-commands.json`, `independent_solver.py` |
| Retained parser selector, normal and `-O` | Exit 0 each; 6 positive + 39 actual-call refusal cases per mode | `aggregate-commands.json` |
| Retained minimal tests, normal and `-O` | Exit 0 each; 57 tests per mode, zero failures/errors/skips | `aggregate/commands.json`, first command in each mode |
| Frozen manual control flow, both modes | All 20 manual command exits match their required results | `aggregate/commands.json` |
| Root-rule Ruff check / format check | Exit 0 / 0; all checks pass; 25 files already formatted; no cache | `static-commands.json` |
| Private mypy, selected 25 sources | Inner and outer exit 0; no issues in 25 files | `formal/mypy.json`, `static-commands.json` |
| Separate read-only administration | All seven exits 0 | `admin-commands.json` |

The frozen manual flow in **each** mode is preflight 0, init 0, prepare-fixtures 0, repeat preparation 2, run-all blocked 3, incomplete report 3, prepare-model blocked 3, stop 0, stopped preparation 2, and report after stop 3. Preflight leaves its private project empty. Each publication contains exactly 30 read-only inputs with matching sizes/hashes and oracle digest. Both modes publish the same fixture manifest hash. Reports state that prepared-input receipts are ledger witnesses, not current-byte/converter proof, and never claim full readiness. The real checkout `.friday_test` remains absent.

Private workers use exactly `-I -S -B`, plus `-O` for optimized runs. Verified harness buffers execute through the committed loader. Optional imports occur under a read-only guard with no allowed filesystem write root, and declared private targets only. Actual loaded packaging/resolvelib origins are recorded, checked within the copied targets, and inventories rechecked before leaving the guard. Independent attempted filesystem-write and socket-creation canaries reach and prove the intended refusal paths. No import/setup/collection failure is counted as a semantic rejection.

The independent probes assert a real newest-version rejection and compatible older selection; impossible closure; canonical names; base and late extras; an active finite cycle; inactive platform markers; reversed-order choice stability and repeated output; caller-mutation snapshot isolation; Python/platform/yanked/byte exclusions; malformed metadata refusal even on excluded candidates; unknown extras; round, time, candidate, graph-edge and selected-byte boundaries; backward/nonfinite clock handling; caller stop with exactly nine callbacks and no retry; and the 1 MiB snapshot limit. Every successful solver and nested C2 plan has all actual artifact/license/installed/execution qualification flags false; actual index resolution is false.

Read-only copies match **1,177 typing files, 23 packaging files and 15 resolvelib files** at both boundaries, with no symlinks. Raw copied METADATA/license files independently confirm the pinned package versions, supported Python versions, resolvelib ISC license and absence of unconditional runtime dependencies or startup hooks. See `raw-tool-metadata.json`. The already approved extracted tool targets were reused; no original wheel was transferred or executed anew.

The mypy launcher was inspected before use, copied into reviewer scratch and bound to reviewer source/manifest/target/config/cache paths. Its PEP561 search path contains only the private packaging and resolvelib targets. Root rules were copied unchanged; no source/library/root configuration edits or suppression were introduced. Mypy logs two denied harmless stdlib-discovery probes for `bin/Modules/Setup` and `Setup.local`; the guard denies those probes, and mypy completes successfully. These are neither semantic-negative credit nor authorization for those reads.

Administration is the explicitly authorized separate maintenance lane using `uv run --offline --frozen --no-sync --no-python-downloads --no-env-file python -B ...`, with `PYTHONDONTWRITEBYTECODE=1`, `GIT_OPTIONAL_LOCKS=0`, and reviewer UV/XDG/TMP locations. Board validation passes 36 tasks, render `--check` confirms the dashboard, documentation validation checks 1,103 Markdown files, and metadata validation checks 18 pyprojects. Owned-worktree, cached and exact-range `git diff --check` pass. Only this maintenance lane may use the repository maintenance interpreter; harness/runtime/static checks never use working `.venv`. Whole-repo legacy debt and unrelated dirty-YAML whitespace remain failed/unwaived as declared in the request; no whole-repo green claim is made or broad product suite run.

For reproduction, create a new external owned scratch directory, copy `request.json`, `audit.py`, `prepare.py`, `checks.py`, and `independent_solver.py` there, independently verify the supplied request/pins/inputs again, then run the pinned interpreter with `-I -S -B` on `audit.py opening`, `prepare.py`, and `formal_reruns.py`. The last operation prepares the initial exact source export and supplemental manual rehearsal. Run the explicit engine worker as captured in `engine-delta.json`, then `checks.py delta`, `checks.py aggregate`, `checks.py static`, `checks.py admin`, and `audit.py terminal`. `prepare.py` copies the inspected launchers/tools into that new scratch and rebinds the export to the exact source manifest. Do not replay already occupied generated-output roots. Every executed validation argv, cwd, exit, stdout and stderr is retained in the named JSON records; the scripts retain their explicit environments and timeout settings. Missing or changed frozen inputs require stopping, never downloading replacements.

## Full CS-01–10 matrix

Source paths below are repository-relative; receipt paths are relative to this report.

| Criterion | Outcome | Requirement/source and current evidence |
| --- | --- | --- |
| CS-01 | PASS | Exact approved scope/profile/source pins; only the three permitted source/README paths alter harness behavior. `manifests.py:155`, `:396`; request pins, `preparation.json`, `opening-checks.json`, `terminal-checks.json`. Protected C0–C2 bytes remain unchanged. |
| CS-02 | PASS | Strict schema/count/full marker fields/tag spelling before optional imports; bounded immutable JSON snapshot. `manifests.py:99`, `:155`, `:396`; new minimal test `test_manifests.py:37` and independent outer-shape/snapshot/bounded-JSON calls. |
| CS-03 | PASS | Real resolvelib provider/reporter and newest-first ordering; older compatible result requires at least one actual rejected candidate; impossible closure refuses. `manifests.py:396`; engine 7/24 and independent backtracking/impossible witnesses. |
| CS-04 | PASS | Canonical names, complete selected closure, base/extra union and late expansion, explicit markers, finite cycles and unknown reference/extra refusal. `manifests.py:207`, `:218`, `:238`, `:315`, `:396`; current parser 6/39, engine 7/24 and independent combined late-extra/marker/cycle test. |
| CS-05 | PASS | Entire wheel declaration is validated before exclusion; known Python/platform/yanked/oversize exclusions are reported; no malformed fallback. Deterministic sort and chosen C2 closure check. `manifests.py:238`, `:396`; independent exclusion, malformed excluded metadata, order and snapshot assertions. |
| CS-06 | PASS | 512 candidates, 8,192 declared edges, at most 500 rounds/300 seconds, existing per-requirement/selected-byte limits, repeated caller/time checkpoints, no retry. `manifests.py:155`, `:207`, `:315`, `:396`; actual-call boundary probes, exact stop callback count, and retained cumulative ledger tests. |
| CS-07 | PASS | Lazy private library use; no fetch/build/install channel; all qualification flags withheld. `manifests.py:396`, `startup.py:37`, `:86`; read-only guarded workers, actual origins, opening/closing 23/15 inventories, write/socket canaries, raw metadata inspection. |
| CS-08 | PASS | All previous 56 method bodies preserved byte-for-byte; current 57 minimal tests, parser 6/39 and engine 7/24 execute both modes. `preparation.json`, selector command logs and `aggregate/commands.json`. Rejection evidence is call-phase assertions/explicit exceptions. |
| CS-09 | PASS | Root-rule Ruff/no-cache format and mypy pass the exact 25-source selection using declared PEP561 dependencies; no new ignores or upstream/root edits. All seven bounded admin/whitespace commands pass. `static-commands.json`, `formal/mypy.json`, `admin-commands.json`, terminal private inventory. |
| CS-10 | PASS | Stable candidate; C3 source/delta assessment then complete retained bounded aggregate; independent scripts and exact receipts; preservation at both boundaries; explicit operational exceptions and future limits below. No acceptance, advancement, full9.5 or delivery claim. |

## Full bounded retained C0–C2 aggregate

All outcomes apply to the retained incremental component obligations, not to deferred higher-directive HR rows or real stage effects. Each row is supported by current source inspection and normal/optimized execution, not a prior component verdict.

| C0 criterion | Outcome | Current source/test/receipt evidence |
| --- | --- | --- |
| CC-01 | PASS | Approved scope and pinned bytes; `opening-checks.json`, `terminal-checks.json`; 18,569 protected files and preserved metadata match. |
| CC-02 | PASS | `bootstrap.py:38`, `:133`, `:164`; `test_startup.py:43` through guarded-child tests: clean positive, dirty/extra/pyc refusal, exact-buffer path swap, armed private site canary; aggregate both modes. |
| CC-03 | PASS | `config.py:25`, `paths.py`, `stages.py:62`; current path/config tests and no-effects preflight/new-only init in aggregate manual receipts. |
| CC-04 | PASS | `ledger.py:34`, `:49`, `:102`, `:140`, `:157`, `stages.py:20`, `:41`; current ledger tamper/truncation/concurrency/promotion/budget/sticky-stop tests and manual stop flow. |
| CC-05 | PASS | `export.py:ObjectView`; `test_export.py:14` creates a real private commit, poisons dirty/untracked content and proves exact blob export and unchanged fixture index. Reviewer committed export independently checks all 29 blobs. |
| CC-06 | PASS | `startup.py:37`, `:86`, `:221`, `:322`, `protection.py`; current protection tests cover real private read/write/probe/dir-fd/descriptor/thread/socket refusals, clean positives, separate metadata detection and truncation. |
| CC-07 | PASS | `environment.py`, `startup.py:86`; current child-environment/site tests and guarded-child positive/refusal. No claim to qualify a future real SDK/backend import. |
| CC-08 | PASS | `window.py:20`, `:157`, `:181`; all current fake-window/loaded-state/prepared-input/stop/expiry/budget/in-flight tests execute. Counters remain fake protocol controls. |
| CC-09 | PASS | `stages.py`, `reports.py:9`, `fixtures.py:43`, `:68`, `:102`; full frozen manual flow, current seed/archive/report tests, intentional exit 3 for unimplemented stages. |
| CC-10 | PASS | Current root-rule private static checks and fresh independent aggregate; command logs and hashes, no working-venv harness execution. |

| C1 criterion | Outcome | Current source/test/receipt evidence |
| --- | --- | --- |
| CI-01 | PASS | Exact directive/continuation and preserved boundary; request pins, opening/closing evidence. |
| CI-02 | PASS | `fixtures.py:488`, `:621`; current full-matrix repeatability/unique-hash/count/PDF xref/image/encryption tests, 6/6/10/8 publication each mode. |
| CI-03 | PASS | Literal `fixtures/expectations.json` and independent structural assertions in `test_fixtures.py`; no converter output was used. |
| CI-04 | PASS | `fixtures.py:793`, `:821`, `:839`; current ordered-unit/visibility/notes/comments/formula/relationship/XML/coordinate/merged-expansion tests. Structural facts explicitly withhold text extraction. |
| CI-05 | PASS | `fixtures.py:1083`, `:1160`; current publication/tamper/incomplete-oracle/partial-stop tests and manual exact input/oracle/mode checks. |
| CI-06 | PASS | `ledger.py:34`, `:102`; `test_ledger.py:84` proves same-instance/process/live-token ownership, stale tip, foreign/released token and competing writer refusal. |
| CI-07 | PASS | Frozen prepare-fixtures/report/stop commands execute with expected exits and false qualification claims in both modes. |
| CI-08 | PASS | Earlier C0 bodies are included within the 56 byte-identical prior bodies; all 57 current tests execute under verified guarded loader normal/-O. |
| CI-09 | PASS | Exact 25-source lint/format/type checks and bounded admin/whitespace receipts all pass. |
| CI-10 | PASS | Exact source/blob selection, independent reviewer-owned scratch and limits, explicit rerun/inspection distinction, closing integrity. |

| C2 criterion | Outcome | Current source/test/receipt evidence |
| --- | --- | --- |
| CD-01 | PASS | Scope/pins/protected earlier evidence match; changed behavior confined to allowed C3 extension/factorization. |
| CD-02 | PASS | `manifests.py:155`, `:190`; all full explicit environment/tag controls retained; minimal malformed-schema/tag tests prove refusal before optional imports. |
| CD-03 | PASS | `manifests.py:207`, `:218`, `:238`, `:315`; retained parser 6 positive cases per mode cover versions/Python/wheels/extras/markers/cycles/late extras/compressed tags/explicit prerelease. |
| CD-04 | PASS | Retained parser 39 actual-call refusals per mode cover conflicting/missing/unreachable/wrong metadata/platform/Python/extra/host/reference/yanked/byte declarations, including malformed populated tag components. |
| CD-05 | PASS | `manifests.py:155`, `:207`, `:238`, `:315`; graph/requirement/count/byte controls remain; checker never fetches/installs or grants qualification. |
| CD-06 | PASS | Previous C2 bodies remain unchanged within the 56-body preservation comparison; normal/-O minimal and explicit private parser runs pass, inventories/origins match. |
| CD-07 | PASS | Typed private packaging PEP561 dependency only; current 25-source root-rule static passes with no suppression/upstream/root edits. |
| CD-08 | PASS | Stable current candidate; this fresh bounded C0–C3 aggregate, exact source export, private caches, all bounded administrative receipts and closing preservation; actual A0–A4 remains open. |

## Findings, limits and advisory score

Numbered mandatory findings: **none**. No product repair is proposed or performed.

The result is limited to an explicit, complete, bounded offline catalog and the retained offline harness controls/input preparation. It does not qualify actual wheels/licenses, a real target machine/installed profile, real index metadata, Docling/OCR/chunkers/tokenizers, an embedding model or any A0–A4 effect. The selected external worker bounds overall invocation time; in-function time/stop checks are cooperative checkpoints. Python-visible prevention is demonstrated; arbitrary native/OS containment and universal graph correctness are not claimed. Higher HR/full-readiness, maintainer UAT/acceptance, and delivery gates remain open. No future-stage proof was demanded to pass this component.

Procedural exceptions are disclosed rather than concealed: an early overbroad extraction of the current authority JSON displayed historical summary fields and old outcomes/scores; no historical or peer report was opened, and none of those results was used for correctness. A first boundary command used `git status --short --untracked-files=all`, expanding untracked `.friday-old` filenames; no store payload was read. Its status-text comparison failed solely because the frozen boundary uses default collapsed status. The command was corrected to `git status --short`; all protected bytes, symlinks, metadata, pins and inputs matched throughout. The initial setup mismatch is not semantic negative credit. Subsequent authority inspection was narrowed and personal state was not reopened. No builder private reasoning or correctness narrative was used. These exceptions reduce procedural quality; they do not establish a source defect or a protected-state mutation.

Advisory **9.0/10 for this bounded component**, using an explicit non-gating rubric: authority/scope/preservation 1.9/2; solver semantics 2.8/3; bounds/private effects 1.9/2; retained/static/admin verification 1.8/2; evidence/procedural clarity 0.6/1. Deductions reflect finite synthetic coverage and the disclosed procedural exceptions, not missing future-stage evidence. This score is not the requested broader full9.5/HR target, does not override a finding, and conveys no approval.

## Closing integrity and artifact map

`opening-state.json` and `terminal-state.json` independently reproduce the exact frozen HEAD, branch, pre-status logical index, status and empty staged diff. **18,569 protected regular-file hashes, 26 symlink targets and all nine preservation/absence records match** the frozen boundary. Dirty YAMLs are preserved by hash/metadata only, without payload display. `.friday`, `.friday-old`, working `.venv`, exports and absence of real `.friday_test` retain their declared metadata. Every authority pin, supplied input hash and supplied private target inventory matches at closing. Reviewer copied targets and both read-only source exports also remain exact; private ownership/target checks are in `terminal-private-checks.json`.

`preparation.json` records exact changed-path comparison, 56 unchanged prior test bodies/current57, copied-target inventories and the 26 current raw/gzip hash pairs. Gzip pairs were decompressed for hash comparison only; builder result conclusions were not credited. Operational launchers were inspected/adapted before execution. `raw-tool-metadata.json` records current raw metadata/license inspection. `aggregate/summary.json` binds the final 29-file source and complete manual/test run. `evidence-manifest.json` hashes the reproducible report/drivers/receipts; `report.sha256` names this report's final digest. All artifacts are reviewer-owned external evidence and leave candidate/supplied state untouched.
