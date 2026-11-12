Navigation copy: source links use repository-relative anchors for documentation validation.
The [exact raw report](report.md.gz) retains reviewer bytes and SHA256
`1f89fd079af6e089bed629c41861674e5587ceb58befef72a57f443bde9804f0`.
Only link notation and this notice differ.

# INGEST C0 foundation — fresh bounded implementation review

**CHANGES_REQUESTED**

Candidate `ecfa38bb71854bb3174ceb9ee82cbb87ef110e69` violates mandatory C0 controls. The supplied 37 selftests pass in normal and optimized modes, and required private static and administrative checks pass. Independent call-phase witnesses nevertheless demonstrate an unguarded standard thread, directory-relative mutations outside the declared policy, an undeclared existence probe, and transport attempts after revocation/expiry changes during reservation. Four numbered findings below require correction. No candidate source was repaired.

## Identity, authority and independence

- Review unit: `INGEST-C0-FOUNDATION`, full review of the bounded CC-01–10 component, not full HR-01–18/pipeline completion.
- Reviewer: separate fresh Codex agent instance `/root/ingest_c0_fresh_validation`, OpenAI GPT-6 family. A more specific runtime model/version was not exposed to this reviewer. No nested delegation.
- Date: 2026-11-11 America/New_York; evidence captured 2026-11-12 UTC.
- Base: `e42082195cd70d4ff384fcf73eac10303144aa07`.
- Exact diff: `e42082195cd70d4ff384fcf73eac10303144aa07..ecfa38bb71854bb3174ceb9ee82cbb87ef110e69`.
- Code source: `f6ef86491a88464bfc07cf2aabeb68d7e596e4de`, tree `272a46f8c331826e1a828129b50180b28046297e`. All 29 selected harness files match their committed Git blobs/SHA256s and the candidate bytes.
- Branch: `feature/cmd-ingest-001`.
- Repository: `/Users/chuckrussell/Dev/gendev/agent-framework`.
- Private reviewer scratch, abbreviated `S` below: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c0-fresh-review-l5jq055c`.
- Exact committed harness export, abbreviated `H`: `S/source/tests/readiness/ingest`.
- Qualified interpreter, abbreviated `P`: `/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13`; SHA256 `e2adf1814122d8b26166917ef7d294d7426963e0f59e28d0d5aef773f67c4bb0`. Observed CPython 3.13.10, Darwin arm64.

Before reading its contents, I verified the self-contained request at `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c0-build-ffm98ttz/review-request.json` against SHA256 `861d1cb5a1d6657fbbdeac155d81f0e6a72f7db36f2dfb60fdc5fa1eb3ee812b`. Its identity snapshot also matched the supplied SHA256 `262cfc453aa34cf17f9ca32140223f0f2ba148cfc4a639bc804e8e0773bfb910`. All 16 authority pins and nine protected business pins matched before review. See `request.json`, `pins.json`, `opening.json`, and `opening-comparison.json` in S.

Read controlling AGENTS/policies, construction directive and approval, execution contract, isolation requirements, effects envelope, readiness plan, C0 scope and tool activation, selected source/tests/README/configuration and changed routing. The approved C0 slice does not waive the higher directive. Full A0–A4 implementation and qualification remain required and open. Existing design-verdict references embedded in controlling documents were not used as implementation evidence; prior review reports/verdicts, memory, builder conversation and builder reasoning were not consulted. Compressed historical receipt payloads were hash-checked for integrity without deriving review conclusions from their claims. Operational tool-launcher/driver text was inspected solely to construct fresh private validation with rewritten paths.

Shared-checkout exception: the live candidate was observed read-only; validation executed against a committed export and fresh fake projects in S. No detached worktree was created because Git/worktree mutation was prohibited. Dirty YAML contents and store/user configuration payloads were not inspected. Hashing declared files and observing declared metadata were the permitted preservation operations.

## Mandatory findings

### 1. C0-F01 — High — `threading.Thread` escapes the active guard

**Requirement:** CC-06 requires armed guard enforcement with real private-root thread negatives; [execution contract](../../../execution-contract.md#L154) requires Python-visible reads/probes to remain inside declared roots. Essential invariants must use explicit enforcement under normal and optimized execution.

**Affected source:** [startup.py](../../../../../../../../../../tests/readiness/ingest/startup.py#L23), especially the ContextVar lookup at line 83 and installation at lines 249–265. Only `_thread.start_new_thread` is replaced. A standard `threading.Thread` can start on the qualified CPython and its new thread sees the default inactive ContextVar. The audit hook returns without enforcing policy when that value is absent.

**Reproduction and proof:** In `independent_probes.py`, with `Guard((owned,), (owned,))` active, launch `threading.Thread(target=...)` whose target writes `outside/thread-effect`. Both `independent-normal.json` and `independent-optimized.json` record a successful launch, no worker errors and `thread_marker_exists: true`. The marker was written outside the nested guard's declared roots, within reviewer-owned fake storage. Direct outside read/stat controls in the same policy correctly raise `Refusal`, proving the intended guard was armed rather than failing at setup/import. Existing [test_protection.py](../../../../../../../../../../tests/readiness/ingest/tests/test_protection.py#L47) tests only `_thread.start_new_thread`, missing the standard thread path.

**Risk:** ordinary Python worker code can lose all read/write/network guard policy without an explicit policy transition. This defeats the claimed C0 controlled-thread refusal and makes the guard unsafe to reuse for later profiles.

**Required mitigation:** refuse all supported unpropagated Python thread creation paths on the qualified interpreter, or explicitly propagate and enforce a non-escalating guard in every supported worker. Reject unsupported thread shapes before launch. Do not rely on replacing one low-level entry point.

**Required regression:** normal and `-O` witnesses through `threading.Thread` and qualified low-level thread APIs, including import-before-guard alias behavior. A rejected worker must leave its outside marker absent; an explicitly supported guarded worker must enforce the same roots and capability limits.

**Documentation/configuration impact:** reconcile README/control-coverage statements with the actual supported thread boundary; no root rules or authority expansion. No production thread or state was targeted.

### 2. C0-F02 — High — `chmod`/`utime` with `dir_fd` mutate an undeclared directory

**Requirement:** CC-06 requires actual private-root write and dir-fd negatives before effect. The execution contract's prevention class and production-isolation rules require controlled Python path violations to be refused before the intercepted effect.

**Affected source:** [startup.py](../../../../../../../../../../tests/readiness/ingest/startup.py#L98). The audit branch checks `dir_fd` only for mkdir/remove/rmdir. For chmod and utime it validates the relative spelling against cwd, while the OS resolves that spelling against the supplied descriptor.

**Reproduction and proof:** Open a descriptor to the fake outside directory before tightening the guard, set cwd to owned, then under `Guard((owned,), (owned,))` execute `os.chmod('sentinel', 0o600, dir_fd=fd)` and `os.utime('sentinel', ns=(1000000000,2000000000), dir_fd=fd)`. Both modes return successfully. The outside target changes from mode `0644` to `0600`, and its mtime becomes exactly `2000000000`. Evidence: `independent-normal.json` and `independent-optimized.json`, rows `dirfd_chmod_outside`, `dirfd_utime_outside`, and `effects_after_guard`. This is an actual call-phase mutation, not a simulated rejection or native/OS residual class. Existing test covers only `os.open(...,dir_fd=...)`.

**Risk:** a process holding a directory descriptor can mutate an undeclared file while the guard validates a different pathname.

**Required mitigation:** reject unsupported directory-relative operations for every controlled mutation API, or resolve/validate the descriptor target and final operation with an explicitly qualified design. Cover chmod/utime and audit the remaining supported dir-fd entry points; do not treat the cwd-based spelling as the OS target.

**Required regression:** normal and optimized tests for each admitted dir-fd mutation shape; verify mode/time/content remain unchanged on rejection and retain clean owned-path positives.

**Documentation/configuration impact:** update control coverage and its regression inventory. Keep the existing policy and private-root boundaries; no production target or restoration is required.

### 3. C0-F03 — Medium — `os.access` bypasses the existence-probe guard

**Requirement:** CC-06 includes read/probe negatives; execution contract section 2.1 explicitly denies Python-visible existence/stat probes outside declared roots and requires explicit guarded entrypoints because audit hooks do not cover every probe. CC-07's fake/profile evidence cannot substitute for that requirement.

**Affected source:** [startup.py](../../../../../../../../../../tests/readiness/ingest/startup.py#L259). Installed wrappers cover stat/lstat/open/readlink, but `os.access` remains an unguarded existence/permission probe.

**Reproduction and proof:** Under the same armed nested policy that rejects direct `os.stat(outside/sentinel)` and an outside payload read, `os.access(outside/sentinel, os.F_OK)` returns true in both modes. See `outside_access_probe` in both independent JSON witnesses. No outside payload was printed or consumed by that probe.

**Risk:** Python code can discover undeclared configuration/credential candidates through a standard existence API, contrary to the C0 read/probe boundary.

**Required mitigation:** instrument or reject `os.access` and inventory the equivalent Python-visible discovery entrypoints supported by C0. Keep ancestor canonicalization metadata narrowly separated from arbitrary outside probes, including directory-relative forms.

**Required regression:** normal/optimized outside-present and outside-absent `os.access` cases must refuse consistently, with declared-root positives and dir-fd negative coverage.

**Documentation/configuration impact:** document the exact supported probe coverage. This does not require an actual SDK import or expanded A1 qualification.

### 4. C0-F04 — Medium — fake transport uses stale revocation/expiry admission after reservation

**Requirement:** CC-08 requires fake window expiry/revocation controls and actual attempted-call witnesses. [Execution contract](../../../execution-contract.md#L322) requires rechecking before each request/effect; section 6 reserves the in-flight exception for work already sent/accepted, not preparation before transport. C0 specifically must prove concurrent stop/expiry and no new request after observation.

**Affected source:** [window.py](../../../../../../../../../../tests/readiness/ingest/window.py#L181). The gate checks stop/time once, then executes counter/reservation callbacks and calls the fake transport at line 212 with no renewed check at the attempted-send boundary.

**Reproduction and proof:** Use a real private C0 ledger for reservation. A deterministic callback first completes `Ledger.reserve`, then advances fake time from 2 to 21 for a window expiring at 20. `send('GET',status_path,{})` still calls the fake with observed time 21 and attempts=1. A second callback completes reservation then publishes private stop.json; the fake is still called with stopped=true and attempts=1. Both modes reproduce. A subsequent call correctly refuses, isolating the gap to the pre-send interval. Evidence: `expiry_during_reservation_before_send`, `expiry_transport_witness`, `stop_observed_in_reservation_before_send`, `stop_transport_witness`, and `subsequent_stopped_call_refuses` in both independent JSON files.

**Risk:** control changes during input preparation/reservation do not prevent the next actual transport attempt. This is a failing C0 fake seam; no HTTP client or real endpoint is implemented or was used.

**Required mitigation:** revalidate revocation and expiry immediately before handing off to transport, after preparation and reservations. Retain conservative charges already reserved and make the actual-send/accepted-in-flight boundary explicit; do not invent universal race-free OS guarantees.

**Required regression:** both modes must reject expiry/stop published during counting/reservation with zero fake calls and zero increment in actual attempts; retain already-valid flow, cumulative charges, and explicitly bounded accepted-in-flight behavior.

**Documentation/configuration impact:** reconcile the documented boundary and proof examples. No real model window, network operation or A3 construction expansion is needed to fix or verify this C0 issue.

## CC-01–10 matrix

The criterion authority is `docs/planning/active/command-refactor/validation/document-ingestion/gate-a/construction/c0/implementation-scope.md`, lines 17–29. Source/test paths below are relative to the repository; receipts are relative to S. PASS applies only to the named bounded component behavior.

| Criterion | Outcome | Current source/test and reproduced evidence |
| --- | --- | --- |
| CC-01 | PASS | Approved construction and private-tool pins match. Exact changed-path list equals the 65 paths in the request; `.gitignore` adds only its comment/spacing and `/.friday_test/`. No production source/root metadata changed in the range. Full opening freeze and closing identity match: `opening-comparison.json`, `closing-comparison.json`, `pins.json`, `tool-closing.json`. Current board remains started with granted bounded authority and pending validation. |
| CC-02 | PASS, bounded startup | `bootstrap.py:38` verifies bounded manifest/blob/hash buffers; `bootstrap.py:133` executes the verified buffers; `run.py:6` pins bootstrap. `tests/test_startup.py:43` through the startup suite exercises approved manifest, dirty/extra/pyc refusal, post-hash swap, armed private site and guarded child positive. `normal.json` and `optimized.json` reproduce all tests, 37/37 each, with isolated/no-site/no-bytecode flags. Public OS input and interpreter hash are independently checked. No actual SDK/backend qualification is claimed. |
| CC-03 | PASS | `config.py:20`, `paths.py:15`, `paths.py:48`, `stages.py:185` implement strict config/path admission and no-effects preflight/new-only init. `tests/test_manifests.py`, `test_paths.py`, `test_cli.py` cover malformed controls, canonical paths, aliases, new-only run conditions and nonempty scratch rejection; the owner check was inspected in source. `normal.json`/`optimized.json`; independent external bootstrap/frozen-copy walkthrough in `manual-commands.json`, preflight/init exit 0, no project output after preflight. |
| CC-04 | PASS for bounded ledger primitives; transport stop gap is CC-08 | `ledger.py:33` through `promote` and `stages.py:19` bind immutable configuration, canonical append records, chain/order/stale tip, exclusive lease, candidate promotion/order and cumulative reservations; `stages.py:48` publishes sticky stop. `tests/test_ledger.py` and `test_cli.py` provide intended refusal/positive witnesses, reproduced both modes. Manual repeated stop exits 0 and run-after-stop exits 2. Full stage choreography and real effect adapters stay open. |
| CC-05 | PASS, private component export | `export.py:19` through `export` uses owned read-only object view and exact Git-object operations; selection is regular committed blobs with SHA1/SHA256 validation. `tests/test_export.py:15` creates an actual fake Git repository, poisons selected dirty/untracked bytes, exports the committed content and checks unchanged private source index plus path/hash refusals. Both selftest receipts reproduce it. Live production Git logical identity is unchanged. The full production source/index collector remains an open A0 obligation. |
| CC-06 | FAIL: C0-F01–F03 | Positive direct read/stat refusal and owned write succeed; existing `test_protection.py` also reproduces metadata change/truncation and socket/low-level thread/dir-fd negatives in both lanes. Independent `independent_probes.py` reaches and disproves standard thread, chmod/utime dir-fd and access-probe controls in both modes. Metadata detection is separate evidence and cannot turn these missing preventive controls into PASS. No OS containment claim is accepted. |
| CC-07 | PASS for environment/site inventory component | `environment.py:11` builds explicit allowlisted child environment with unchanged HOME and private discovery locations; `environment.py:47` classifies fake startup files. `tests/test_environment.py` and guarded child tests strip fake credentials/proxy/Python settings and reject executable/external sites, reproduced in both receipts. No real SDK, uv backend child or installed-site profile is qualified; thread/probe defects are separately mandatory under CC-06. |
| CC-08 | FAIL: C0-F04 | `window.py:31` parses typed fake receipts/loaded identity and `window.py:181` gates routes/model/input/vector/token/request budgets. `tests/test_window.py` reproduces clean fake status/input flow and preexisting invalid state/expiry/stop/budget refusals. Independent callbacks show expiry/revocation during reservation still permit actual fake attempts. Only in-process fake calls were made; counters give no real token/model qualification. |
| CC-09 | PASS, explicitly incomplete | `stages.py:65`, `reports.py:8`, `fixtures.py:20`/`:50`/`:83`; `tests/test_cli.py`, `test_reports.py`, `test_fixtures.py`. Both selftest lanes reproduce real structural PDF/DOCX seeds and archive path/member/duplicate/expanded-byte controls. Independent frozen-copy manual preflight/init succeed; run all/A0–A4 and prepare-model exit 3, report exits 3 with full_readiness=false, stopped run exits 2. These controls supply no upstream, extraction or thirty-format success. |
| CC-10 | Static checks PASS; verification gate NOT SATISFIED | Copied approved Ruff and all 1,177 mypy target files/five pinned wheels match digests. Private config equals root hash `d1e8ff05afbe8f1a06d3ddaa07db520ff0a1378f6fae23baf3ee525b9619e9d7`; no new source suppression or essential Python `assert` was found. `ruff.json`, `format.json`, `mypy.json`, `copied-tool-verification.json` pass. 25 files lint/format/type-check. Fresh review exists but returns CHANGES_REQUESTED; this slice cannot be called independently verified. |

## Reproduced checks and exact command evidence

The exact argv, cwd, exit, stdout and stderr for each selftest/static/admin/manual invocation are retained in the named JSON receipts. The following paths are explicit reviewer-owned substitutions; no supplied output/cache path was reused.

- `P -I -S -B H/run.py selftest --harness-manifest S/harness-manifest.json --harness-manifest-sha256 50e1d67cc01dae457155e11e1b79394975d7b18b89373117932b905b11cbbdeb --scratch S/normal`: exit **0**, 37 tests, PASS. Receipt `normal.json`.
- Same with explicit `-O` and distinct `--scratch S/optimized`: exit **0**, 37 tests, PASS. Receipt `optimized.json`.
- `S/tools/ruff check --no-cache --no-respect-gitignore --config S/tools/pyproject.toml H`: exit **0**. `ruff.json`.
- `S/tools/ruff format --check --no-cache --config S/tools/pyproject.toml H`: exit **0**, 25 files already formatted. `format.json`.
- `P -I -S -B S/private_mypy.py`: exit **0**, no issues in 25 files. The launcher verifies its bootstrap/manifest/public OS read, arms the guard before importing copied mypy, excludes `/usr/local/lib/mypy`, and supplies `--config-file S/tools/pyproject.toml --no-site-packages --explicit-package-bases --cache-dir S/mypy-cache H`. `mypy.json`, `private_mypy.py` and `static-admin-commands.json`. Two absent CPython `Modules/Setup`/`Setup.local` probes are refused and caught by sysconfig; they are logged, not granted extra roots. Root rules remain unchanged.
- `P -I -S -B S/independent_probes.py` and `P -I -S -B -O S/independent_probes.py`: each exit **0** as witness collectors. **This exit is not a passing-control result.** Both JSON witness sets explicitly mark six expected-refusal controls as failed (two mutation operations share finding F02; stop/expiry share F04), while positive/direct-refusal controls pass. Source/setup/import completed successfully.
- `P -I -S -B S/manual_probe.py`: exit **0** for the walkthrough controller; all 14 subprocess exits match the documented expected outcomes. Exact command/config paths and child stdout/stderr are in `manual-commands.json`.
- `P -I -S -B S/close_identity.py`: exit **0**, all opening/closing comparisons equal. `closing.json`, `closing-comparison.json`, `tool-closing.json`.

Repository administrative checks used only the separately permitted existing admin environment, with `GIT_OPTIONAL_LOCKS=0`, `PYTHONDONTWRITEBYTECODE=1` and `UV_CACHE_DIR=S/uv-cache`. They did not run harness/static checks from `.venv`. No mutating `render` command was run.

| Exact command relative to repository cwd | Exit | Evidence |
| --- | --- | --- |
| `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` | 0 | `board.json`: 36 tasks valid |
| `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check` | 0 | `dashboard.json`: dashboard current |
| `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py` | 0 | `docs.json`: 1,082 Markdown files checked |
| `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py` | 0 | `metadata.json`: 18 metadata files valid |
| `git diff --check -- .gitignore docs/planning tests/readiness/ingest` | 0 | `owned-whitespace.json` |
| `git diff --cached --check` | 0 | `staged-whitespace.json` |
| `git diff --check e42082195cd70d4ff384fcf73eac10303144aa07..ecfa38bb71854bb3174ceb9ee82cbb87ef110e69` | 0 | `range-whitespace.json` |

Private tool details: Ruff binary SHA256 `3844f53974c6e6d52dcfccdc02e9b34188c5003f0060ad2f3a96b9d550eea6f5`; mypy target manifest SHA256 `42080c45bc8eba17794de093aecc51815bface423e7d8b7e281392b7b5125dcb`. Copied files exactly match the approved target manifest; all five existing wheel sizes/digests match the approved profile. No download, resolver, install or startup-file processing occurred. Public SystemVersion.plist SHA256 matched `bd61e19dd67dd97ce9a27c79a2148d42cc9685a71c6f17ff27d62b819f39f983` before mypy execution.

## Inspected versus reproduced, integrity and limits

**Reproduced:** current source selftests normal/-O, fresh exact committed export, private lint/format/type-check, listed read-only administrative checks, fresh external CLI/frozen-copy walk, independent in-process guard and transport witnesses, all authority/business pins and opening/closing comparisons.

**Inspected/hash-verified only:** approved construction/profile receipts and operational launcher inputs; twelve compressed evidence-index entries pass both compressed and uncompressed SHA256 checks (`evidence-integrity.json`). That proves retained receipt integrity, not the correctness of their historical conclusions. Builder evidence narratives and historical peer reviews were not used. Recorded baseline debt was not rerun or repaired.

At each identity boundary, `GIT_OPTIONAL_LOCKS=0 git ls-files -s -z` was hashed **before** status. Both boundaries have logical index SHA256 `78fcdae83d0c12165ae731f703edbf6dc25d06a6ffd6aa90917132a5a06c5b3b`, the requested HEAD/branch, identical full porcelain status and an empty stage. All 18,088 declared file hashes, 26 symlink identities and nine declared preserved-state records match the supplied freeze, then match each other at close. `.friday_test` in the actual repository remains absent. Protected YAML hash/metadata records, `.friday-old`, `.friday`, `.venv` and exports records remain identical. Preservation coverage is the request's declared file/metadata scope; no store payload scan or newly invented full-system inventory was performed.

Copied/supplied tool hashes and target manifest contents were checked again at close and remain unchanged. All runnable drivers, outputs, private caches, fake Git repositories, fake controls and deliberately modified outside-shaped targets belong to S. No supplied-scratch output or cache was written. No source/board/Git mutation, application import/provider/model/store operation, actual repository `.friday_test`, cleanup/restoration, or delivery action was performed. Outside-shaped effects in findings F01/F02 were intentional writes only to new reviewer private fixtures, not protected user state.

Historical root Ruff/collection/registry format debt remains failed/unwaived per the request, and protected dirty YAML whitespace remains excluded from repair. Passing scope/admin/range checks does not establish whole-repository green.

Full A0 metadata/source/index collection; actual native/backend/startup profiles; A1 real dependencies/import/CA controls; A2 Docling/RapidOCR/counters, complete 6 PDF/6 DOCX/10 XLSX/8 PPTX oracle matrix, chunk strategies and all limit cases; A3 real model/counter/token/prepared-batch/window qualification; active-time/RSS/disk/process/cache controls for activated adapters; full promotion/preparation choreography; A4 measured readiness; and later product command/store/consumer/migration/guide work all remain open. No skipped or blocked real stage receives qualification credit. The fake transport contains no HTTP client.

**Advisory score: 7.0/10 for this bounded C0 candidate.** Scope discipline, exact-byte loading, clear incomplete-stage behavior and reproducible private checks are sound component evidence. The preventive guard and transport-admission gaps are material mandatory failures, so the score cannot override CHANGES_REQUESTED. Review supplies no maintainer acceptance, new construction scope, automated remediation loop, push/PR/merge/release/deployment authority or broader harness-readiness claim.
