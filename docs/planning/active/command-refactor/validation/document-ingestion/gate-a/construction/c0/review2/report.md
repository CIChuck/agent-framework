Navigation copy: links point to repository files or durable compressed evidence.
The [exact raw reviewer report](report.md.gz) retains SHA256
`619d0d9b44c67e25a6eb53db2aa2abbc11d56574505946b3daca645bba211208`.
Only link notation and this notice differ.

# INGEST-C0-FOUNDATION fresh corrected-candidate implementation review

**VERIFIED — bounded C0 only.** C0-F01–04 are closed on the changed candidate, and all current CC-01–10 obligations pass. No mandatory finding remains. The full higher directive, HR requirements and A0–A4 construction/qualification remain open; no acceptance, effect activation, push, merge or other delivery authority follows.

Reviewer: separate fresh read-only Codex agent `/root/ingest_c0_corrected_fresh_validation`. Model identification: **GPT-6-based Codex as identified by session developer instructions; exact model/version unavailable in this agent context**. Review date: **2026-11-11 America/New_York**, runtime integrity observation **2026-11-12T04:51:58.683744+00:00** UTC. Exact provider model/version was not exposed and is not guessed. This reviewer did not build or remediate the candidate, delegate work, search memory/history, or consult prior report bodies or prior scores as correctness evidence. The numbered finding requirements and original probe source were the only prior C0 review material used for remediation trace. Historical labels embedded in current routing documents supply no correctness evidence.

## Frozen inputs and read-only integrity

- Repository `/Users/chuckrussell/Dev/gendev/agent-framework`; branch `feature/cmd-ingest-001`; candidate **`fbe8201dc7829c5e6464f57566875660a3ea0c99`**.
- Corrected source **`f90367e6c296b99799ff3e752fcc9d8a26c3aa6d`**. Its harness source is byte-identical at the candidate; [source-to-candidate-paths.json](evidence/source-to-candidate-paths.json.gz) records the name-only comparison.
- Delta FIRST: **`ecfa38bb71854bb3174ceb9ee82cbb87ef110e69..fbe8201dc7829c5e6464f57566875660a3ea0c99`**. Aggregate: **`e42082195cd70d4ff384fcf73eac10303144aa07..fbe8201dc7829c5e6464f57566875660a3ea0c99`**. Actual changed-path lists exactly match the request: **70 delta / 118 aggregate**. Source changes in the correction remain in startup/window, their two test files and README; the complete construction stays under the approved test-only selection, sole root ignore entry and named planning/evidence paths. Historical archived reports were inspected by name/hash only, not by report-body diff.
- Request SHA256 **`1e56c6c5e2a2d6bf57c4c11f90e0c67cd42abea6ad50538c1ad19010ccdd0a9d`** was checked before reading it. Supplied freeze SHA256 **`699b50b43a938ac35a0ac06197769b88dccfe84b1ab55336fb59b72a8277798e`** and numbered excerpt **`222a437fad76616de5891a1b68535dc0c8e0d0e63533418e975bfbe53e57040c`** also match.
- All **17 authority pins** and **9 protected business pins** match ([pins.json](evidence/pins.json.gz)). Governing authority is the approved directive/contract plus exact C0 obligation selection and correction directive: [AGENTS.md:1](../../../../../../../../../../AGENTS.md#L1), [docs/reference/policies/independent-validation-policy.md:1](../../../../../../../../../reference/policies/independent-validation-policy.md#L1), [docs/planning/active/command-refactor/validation/document-ingestion/gate-a/construction/c0/implementation-scope.md:16](../implementation-scope.md#L16), [docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-C0-001-controls.md:1](../../../../../../remediation/REM-CMD-INGEST-C0-001-controls.md#L1). Frozen historical draft/pending headers are superseded for C0 construction only by the pinned exact construction approval, not silently rewritten.
- Opening and closing snapshots compute **logical index before status** using `GIT_OPTIONAL_LOCKS=0 git ls-files -s -z`. Both logical digests are **`93ee508a52854af2380aa42b0a470d9aa894c6d1cab6086418354326279f7ae3`**. HEAD, branch, full porcelain status, empty staging, all **18,232 captured tracked/untracked file hashes**, 26 symlink targets, and the nine declared protected metadata/hash records are unchanged. The supplied freeze's **18,141** file hashes are an equal subset; this reviewer additionally captured **91** existing untracked files. The opening comparison's `files:false` means this extra coverage, not drift. A final repeated closing check also matches all opening fields (`final-closing.json`, `final-preservation.json`). See [opening.json](evidence/opening.json.gz), [closing.json](evidence/closing.json.gz), [preservation.json](evidence/preservation.json.gz).
- Shared-checkout exception: the checkout was read-only; the exact committed harness was exported to `/private/tmp/ingest-c0-review2-fresh-xIyGX4/candidate/tests/readiness/ingest` (29 selected files). The source-manifest SHA256 is `4ad7ec7abd36a4698360abeae558cbcc46a03c6f1375b4483fb11cf2dc21549c`. [candidate-source-manifest.json](evidence/candidate-source-manifest.json.gz) binds it. No dirty YAML or store/user payload was opened for content. Only the explicitly permitted dirty-file/protected-file hashes and metadata were collected. The actual repository `.friday_test` stayed absent. Protected generated-directory evidence is the declared freeze metadata boundary, not a claim to hash arbitrary ignored store payloads or the entire filesystem.
- All effect/output/cache paths are in the canonical reviewer-owned directory **`/private/tmp/ingest-c0-review2-fresh-xIyGX4`**. Ownership audit covers the retained entries with no nonowned path or symlink escape ([output-ownership-audit.json](evidence/output-ownership-audit.json.gz)). Supplied scratch/tool inputs were read-only. Their closing hashes still match, including all 1,177 mypy-target files ([post-tool-input-audit.json](evidence/post-tool-input-audit.json.gz)). No cleanup, restoration, source/authority edit, production Git mutation, application import/test, dependency installation, network, SDK/provider/model/store call or real A0–A4 effect occurred.

## Correction matrix — independently evaluated before aggregate

The independent delta probe was authored and run before consulting the allowed original probe source. It executes explicit call assertions and records setup/runtime errors separately. Both **normal and -O: 62 PASS, 0 assertion failures, 0 errors** ([delta-normal/result.json](evidence/delta-normal/result.json.gz), [delta-optimized/result.json](evidence/delta-optimized/result.json.gz)). Direct focused probes import only the committed private C0 export; they do not substitute for bootstrap qualification, which is separately reproduced through the committed entrypoint suite.

| Finding | Exact requirement and result | Current source / regression | Reproduced evidence |
| --- | --- | --- | --- |
| **C0-F01, high — CLOSED** | Standard and qualified low-level unpropagated threads refuse before launch, including aliases saved before guard installation. No supported worker gains inactive policy. | [tests/readiness/ingest/startup.py:86](../../../../../../../../../../tests/readiness/ingest/startup.py#L86) audits both CPython launch events, [tests/readiness/ingest/startup.py:311](../../../../../../../../../../tests/readiness/ingest/startup.py#L311) refuses the installed low-level path; [tests/readiness/ingest/tests/test_protection.py:69](../../../../../../../../../../tests/readiness/ingest/tests/test_protection.py#L69); [tests/readiness/ingest/README.md:99](../../../../../../../../../../tests/readiness/ingest/README.md#L99) states the supported boundary. | Five launches per lane: saved `threading.Thread`, saved `start_new_thread`, saved `start_new`, saved `start_joinable_thread`, installed `start_new_thread`. Each raises Refusal, no worker runs and no outside marker exists; owned positive still succeeds. |
| **C0-F02, high — CLOSED** | Every admitted directory-relative mutation shape refuses before effect; mode/time/content/entries stay unchanged; ordinary owned operations remain usable. | [tests/readiness/ingest/startup.py:105](../../../../../../../../../../tests/readiness/ingest/startup.py#L105) checks actual audit descriptor positions; installed `open`/`mkfifo`/`mknod` wrappers cover missing/incomplete events; [tests/readiness/ingest/tests/test_protection.py:117](../../../../../../../../../../tests/readiness/ingest/tests/test_protection.py#L117) and [tests/readiness/ingest/tests/test_protection.py:191](../../../../../../../../../../tests/readiness/ingest/tests/test_protection.py#L191); [tests/readiness/ingest/README.md:123](../../../../../../../../../../tests/readiness/ingest/README.md#L123). | Own probes invoke 16 directory-relative API/forms with cwd set to owned and the descriptor pointing outside, plus fd mutation/discovery forms. Actual `chmod`/`utime` target mode, atime, mtime, size/content and directory entries are unchanged. Committed regressions also reject absolute-path/nondefault-dir_fd calls. Owned chmod/utime/chown and FIFO/node positives pass. |
| **C0-F03, medium — CLOSED** | Outside-present/absent access/probes refuse consistently; owned positives work; dir_fd/fd forms refuse and ancestor canonicalization grants metadata only. | [tests/readiness/ingest/startup.py:219](../../../../../../../../../../tests/readiness/ingest/startup.py#L219) through access/open/readlink wrappers; [tests/readiness/ingest/startup.py:239](../../../../../../../../../../tests/readiness/ingest/startup.py#L239), [tests/readiness/ingest/startup.py:246](../../../../../../../../../../tests/readiness/ingest/startup.py#L246); audited listing/chdir at line 137; [tests/readiness/ingest/tests/test_protection.py:230](../../../../../../../../../../tests/readiness/ingest/tests/test_protection.py#L230); [tests/readiness/ingest/README.md:107](../../../../../../../../../../tests/readiness/ingest/README.md#L107). | `access` F_OK/R_OK outside-present/absent, outside stat/lstat/readlink/listdir/scandir and six directory-relative probe forms refuse. Owned access-present true/access-absent false, listing/read/write positives pass. fstat/stat(fd), listing(fd), fchdir and mutation(fd) refuse. Ancestor stat remains admitted, access/listing refuse; convenience exists functions return false after intercepted refusal. |
| **C0-F04, medium — CLOSED** | Stop/expiry during counting or reservation is rechecked at final fake handoff: zero sends/actual attempts, conservative reserved charges retained; already accepted work is bounded. | [tests/readiness/ingest/window.py:181](../../../../../../../../../../tests/readiness/ingest/window.py#L181), final check at line 212; [tests/readiness/ingest/tests/test_window.py:178](../../../../../../../../../../tests/readiness/ingest/tests/test_window.py#L178), [tests/readiness/ingest/tests/test_window.py:249](../../../../../../../../../../tests/readiness/ingest/tests/test_window.py#L249); [tests/readiness/ingest/README.md:152](../../../../../../../../../../tests/readiness/ingest/README.md#L152). | Own deterministic changes at counter, vectors, tokens and request-reservation callbacks, each stop/expiry, produce zero fake sends and attempts; reopened totals retain requests=2, vectors=1, tokens=4 including one prior request. Next refused call adds no charge. Change inside accepted callback permits exactly one attempt/charge, then next call refuses. |

The runtime `os.supports_dir_fd` inventory matches the documented qualified mutation/probe set (aliases remove/replace are covered too). Regular/directory descriptor forms in `supports_fd` are checked; `pathconf`/`statvfs` profiles are explicitly unqualified, not silently claimed guarded. Standard-thread saved aliases are covered by audited events, unlike saved raw preinstall nonaudit file/probe builtins. Current C0 source uses the installed supported boundary and no real dependency profile is activated. These exclusions do not waive any exercised C0 obligation or authorize a later profile to use an unqualified channel. See discovery inventory in both delta JSON files and [tests/readiness/ingest/README.md:107](../../../../../../../../../../tests/readiness/ingest/README.md#L107).

## Unfixed-source regression witness

I inspected the permitted original probe code and the committed unfixed command witness, then independently replayed the original probes on corrected bytes and a **private mixed negative fixture**: current 43-case test selection with only `startup.py`/`window.py` substituted from `ecfa38bb71854bb3174ceb9ee82cbb87ef110e69`. Origins and hashes are explicit in [replay-unfixed/derived-fixture-origins.json](evidence/replay-unfixed/derived-fixture-origins.json.gz). Its generated manifest is fixture control data; its commit/tree fields are selection context, never a claim that mixed bytes are an approved committed deliverable. No checkout byte was changed.

- Corrected original probes: both lanes exit **0**, all ten expected-control/positive rows meet their expectation. Transport witness rows show zero sends/attempts.
- Unfixed original probes: both lanes exit **0** because the original probe is a recording program, **not** a pass/fail runner. Six intended controls record actual wrong success: access, chmod, utime, standard-thread launch, reservation expiry and reservation stop. The actual outside mode becomes **0600**, mtime becomes **2,000,000,000 ns**, thread marker exists, expiry fake sees **now=21** with **attempts=1**, and stop fake sees **stopped=true** with **attempts=1**. Direct outside read/stat still refuse, establishing an armed nested policy, and the subsequent stopped call refuses. This is positive regression sensitivity, not setup failure credit.
- Unfixed current suite: normal and -O each exit **1**, run **43 tests**, and report **19 assertion failures plus one error**. The `mknod` FileExistsError follows a successful unsafe `mkfifo` creating the same fixture target; it earns **zero rejection credit**. Regex-mismatch and duplicate/subtest failures are not counted as independent vulnerabilities. The actual mutation replay supplies F02 effect proof, and the remaining call-phase assertions independently witness the missing controls.

Exact invocation receipts: [replay-commands.json](evidence/replay-commands.json.gz); raw lane outputs and original result JSON are retained under `replay-corrected/` and `replay-unfixed/`. Supplied receipts were inspected as trace only; the observations above are independently reproduced.

## Full current bounded C0 matrix

| Criterion | Outcome | Current source / required proof | Current reproduced evidence |
| --- | --- | --- | --- |
| **CC-01** | **PASS** | Approved test-only selection, sole anchored ignore, parent pins and preservation: [docs/planning/active/command-refactor/validation/document-ingestion/gate-a/construction/c0/implementation-scope.md:20](../implementation-scope.md#L20), [docs/planning/active/command-refactor/validation/document-ingestion/gate-a/construction-approval.json:1](../../../construction-approval.json#L1). | All authority/business pins; exact 118/70 path sets; source-to-candidate code equality; `.gitignore` adds only comment/blank lines and `/.friday_test/`; full opening/closing preservation equality. |
| **CC-02** | **PASS** | [tests/readiness/ingest/bootstrap.py:38](../../../../../../../../../../tests/readiness/ingest/bootstrap.py#L38) verifies bounded bytes/blob/mode/selection then exact buffers; [tests/readiness/ingest/bootstrap.py:164](../../../../../../../../../../tests/readiness/ingest/bootstrap.py#L164) enforces qualified startup; [tests/readiness/ingest/run.py:1](../../../../../../../../../../tests/readiness/ingest/run.py#L1); [tests/readiness/ingest/tests/test_startup.py:43](../../../../../../../../../../tests/readiness/ingest/tests/test_startup.py#L43). | CPython **3.13.10 / Darwin arm64**, pinned binary, -I/-S/-B, normal/-O 43-case suites; dirty/extra/pyc/path-swap and armed .pth controls. Own **valid timestamp-and-size matching malicious pyc** refuses before execution in both lanes; intentionally unsafe private loader executes it, proving canary armed. Frozen run.py preflight/report work in both modes. |
| **CC-03** | **PASS** | [tests/readiness/ingest/manifests.py:84](../../../../../../../../../../tests/readiness/ingest/manifests.py#L84), [tests/readiness/ingest/config.py:22](../../../../../../../../../../tests/readiness/ingest/config.py#L22), [tests/readiness/ingest/paths.py:27](../../../../../../../../../../tests/readiness/ingest/paths.py#L27), [tests/readiness/ingest/stages.py:99](../../../../../../../../../../tests/readiness/ingest/stages.py#L99); manifest/path/CLI tests. | Strict duplicate/nonfinite/oversize/schema/hash/path/no-symlink/empty-scratch tests; independent manual preflight has unchanged unit-project file listing; new init copies all 29 exact approved files; second init refuses. |
| **CC-04** | **PASS** | [tests/readiness/ingest/ledger.py:42](../../../../../../../../../../tests/readiness/ingest/ledger.py#L42), [tests/readiness/ingest/ledger.py:84](../../../../../../../../../../tests/readiness/ingest/ledger.py#L84), [tests/readiness/ingest/ledger.py:122](../../../../../../../../../../tests/readiness/ingest/ledger.py#L122), [tests/readiness/ingest/ledger.py:139](../../../../../../../../../../tests/readiness/ingest/ledger.py#L139) and [tests/readiness/ingest/stages.py:20](../../../../../../../../../../tests/readiness/ingest/stages.py#L20); ledger/CLI tests. | Canonical timestamped hash chain, tamper/truncate/stale/concurrent-writer/stage-order tests; budget reopen tests; own explicit valid promotion and stale repeat; stop succeeds while writer lease held, is idempotent and sticky, run refuses while report remains available. Changed config digest refuses. Chain/actor strings are consistency records, not malicious-owner authentication. |
| **CC-05** | **PASS** | [tests/readiness/ingest/export.py:20](../../../../../../../../../../tests/readiness/ingest/export.py#L20), [tests/readiness/ingest/export.py:55](../../../../../../../../../../tests/readiness/ingest/export.py#L55), [tests/readiness/ingest/export.py:119](../../../../../../../../../../tests/readiness/ingest/export.py#L119); [tests/readiness/ingest/tests/test_export.py:14](../../../../../../../../../../tests/readiness/ingest/tests/test_export.py#L14). | Actual fake Git commit/blob export with exact hashes and read-only file mode; independently added dirty/untracked/**ignored** traps and invalid poisoned source config. Export still produces committed selected bytes only; source index/config hashes unchanged; symlink, escape, wrong hash, missing/ignored/untracked/excluded source, unapproved operation/options and undeclared alternates refuse. No harness write to production Git. |
| **CC-06** | **PASS** | [tests/readiness/ingest/stages.py:161](../../../../../../../../../../tests/readiness/ingest/stages.py#L161) arms guard before verified discovery; [tests/readiness/ingest/startup.py:45](../../../../../../../../../../tests/readiness/ingest/startup.py#L45), [tests/readiness/ingest/startup.py:86](../../../../../../../../../../tests/readiness/ingest/startup.py#L86), [tests/readiness/ingest/protection.py:29](../../../../../../../../../../tests/readiness/ingest/protection.py#L29), [tests/readiness/ingest/protection.py:66](../../../../../../../../../../tests/readiness/ingest/protection.py#L66). | Normal/-O armed-discovery/guarded-child tests plus all correction probes, actual socket/read/probe/write/thread/dir_fd negatives and owned positives. Independent fake-cache mutation changes snapshot and `unchanged` raises isolation failure; finite/empty/truncated/absent metadata controls. Detection is explicitly separate from prevention; no native/OS containment claim. |
| **CC-07** | **PASS** | [tests/readiness/ingest/environment.py:11](../../../../../../../../../../tests/readiness/ingest/environment.py#L11), [tests/readiness/ingest/environment.py:45](../../../../../../../../../../tests/readiness/ingest/environment.py#L45), [tests/readiness/ingest/startup.py:183](../../../../../../../../../../tests/readiness/ingest/startup.py#L183); environment/startup tests. | Fake credential/proxy/Python/UV inheritance stripped; private child env and unexpected credential rejection; executable .pth and external-path blocks; guarded data classification retained. Own sitecustomize inventory treats bytes as nonexecuted data for guarded profile and blocks site-enabled profile. No actual SDK/backend import or system-setting qualification claimed. |
| **CC-08** | **PASS** | [tests/readiness/ingest/window.py:30](../../../../../../../../../../tests/readiness/ingest/window.py#L30), [tests/readiness/ingest/window.py:121](../../../../../../../../../../tests/readiness/ingest/window.py#L121), [tests/readiness/ingest/window.py:181](../../../../../../../../../../tests/readiness/ingest/window.py#L181); full window tests and F04. | Actual fake attempted-send counts, shared cumulative request/vector/token ledger, strict routes/loaded model/expiry/attestation/prefix/bindings/prepared-input/vector limits; independent eight pretransport stop/expiry cases and two accepted-boundary cases per lane. Character count remains a unit fake, not a qualified model counter. No HTTP client/network request. |
| **CC-09** | **PASS** | [tests/readiness/ingest/stages.py:62](../../../../../../../../../../tests/readiness/ingest/stages.py#L62), [tests/readiness/ingest/reports.py:8](../../../../../../../../../../tests/readiness/ingest/reports.py#L8), [tests/readiness/ingest/fixtures.py:25](../../../../../../../../../../tests/readiness/ingest/fixtures.py#L25), [tests/readiness/ingest/fixtures.py:95](../../../../../../../../../../tests/readiness/ingest/fixtures.py#L95), [tests/readiness/ingest/fixtures/expectations.json:1](../../../../../../../../../../tests/readiness/ingest/fixtures/expectations.json#L1); CLI/report/fixture tests. | Independent manual normal/-O frozen entrypoints, exact control hashes, blocked all/A2-offline/prepare-model exit3 with zero effects; report INCOMPLETE exit3 and five unqualified stages. Actual deterministic PDF xref and DOCX XML structural seeds, archive escape/count/duplicate/expansion controls and independent archive symlink negatives. Two seeds earn no 30-document/converter/A2 credit. |
| **CC-10** | **PASS** | [pyproject.toml:116](../../../../../../../../../../pyproject.toml#L116), [docs/planning/active/command-refactor/validation/document-ingestion/gate-a/construction/c0/private-typecheck-approval.json:1](../private-typecheck-approval.json#L1), [tests/readiness/ingest/README.md:161](../../../../../../../../../../tests/readiness/ingest/README.md#L161). | Copied and pre/post hash-verified approved Ruff, 1,177-file mypy target and exact root config; no resolution/install/startup-hook processing. Private cache/temp/namespaces/typeshed and guarded mypy import; /usr/local/lib/mypy fallback excluded. Ruff/format/mypy exit0, 25 files each where applicable; no source suppression or assert-based essential enforcement found. Current independent delta-first and full bounded review completed. |

## Reproduced command outcomes

The core suite ran through the exact committed bootstrap and approved correction manifest **`3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9`**. Both **43/43** suites passed with no skip/error. Private Ruff: **all checks passed**. Format: **25 files already formatted**. Mypy: **no issues in 25 source files**. Mypy's guard emits caught refusals for unapproved CPython setup/locale probes; they do not disable the guard or read those files, and are retained in stderr. Its explicitly permitted public SystemVersion.plist hash is `bd61e19dd67dd97ce9a27c79a2148d42cc9685a71c6f17ff27d62b819f39f983`.

Administrative commands use the existing environment **only for read-only repository administration**, via `uv run --offline --frozen --no-sync --no-python-downloads python -B`, private UV cache/temp and `GIT_OPTIONAL_LOCKS=0`. The documentation checker internally invokes uv with weaker default argv; an exact-argv reviewer-owned uv wrapper rewrites that one nested board-validate invocation to the same offline/frozen/no-sync/no-download/-B form and rejects any unexpected invocation. Repository script bytes are unchanged. Board validate (36 tasks), dashboard `render --check`, documentation (1,085 Markdown files), metadata (18 pyprojects), combined-range, delta-range and staged whitespace checks all exit **0**.

Exact argv, cwd, exits and per-command stdout/stderr paths are recorded in [commands.json](evidence/commands.json.gz), [admin-commands.json](evidence/admin-commands.json.gz), [aggregate-commands.json](evidence/aggregate-commands.json.gz), [replay-commands.json](evidence/replay-commands.json.gz). The normal and optimized independent delta invocations were:

```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/delta_probes.py /private/tmp/ingest-c0-review2-fresh-xIyGX4/candidate/tests/readiness/ingest /private/tmp/ingest-c0-review2-fresh-xIyGX4/delta-normal
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c0-review2-fresh-xIyGX4/delta_probes.py /private/tmp/ingest-c0-review2-fresh-xIyGX4/candidate/tests/readiness/ingest /private/tmp/ingest-c0-review2-fresh-xIyGX4/delta-optimized
```

Both exited **0**. `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate_probes.py` with `-I -S -B` exited **0**, four compound aggregate groups pass without assertion/setup errors. Individual exact invocation records follow. Effectful fixture/native operations below target reviewer-owned fake projects only.

### commands.json

- `selftest-normal`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/candidate/tests/readiness/ingest/bootstrap.py selftest --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --scratch /private/tmp/ingest-c0-review2-fresh-xIyGX4/selftest-normal
  ```

- `selftest-optimized`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c0-review2-fresh-xIyGX4/candidate/tests/readiness/ingest/bootstrap.py selftest --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --scratch /private/tmp/ingest-c0-review2-fresh-xIyGX4/selftest-optimized
  ```

- `ruff`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4`.

  ```sh
  /private/tmp/ingest-c0-review2-fresh-xIyGX4/validation-tools/ruff check --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/pyproject.toml --no-cache /private/tmp/ingest-c0-review2-fresh-xIyGX4/candidate/tests/readiness/ingest
  ```

- `format`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4`.

  ```sh
  /private/tmp/ingest-c0-review2-fresh-xIyGX4/validation-tools/ruff format --check --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/pyproject.toml --no-cache /private/tmp/ingest-c0-review2-fresh-xIyGX4/candidate/tests/readiness/ingest
  ```

- `mypy`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/private_mypy.py /private/tmp/ingest-c0-review2-fresh-xIyGX4/validation-tools/mypy-target /private/tmp/ingest-c0-review2-fresh-xIyGX4/candidate/tests/readiness/ingest /private/tmp/ingest-c0-review2-fresh-xIyGX4/harness-manifest.json 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 70e03f2215282e2d4aa6fd0a58161ce0b9858981a114caba49f4826f5833599c --config-file /private/tmp/ingest-c0-review2-fresh-xIyGX4/pyproject.toml --no-site-packages --explicit-package-bases --namespace-packages --custom-typeshed-dir /private/tmp/ingest-c0-review2-fresh-xIyGX4/validation-tools/mypy-target/mypy/typeshed --cache-dir /private/tmp/ingest-c0-review2-fresh-xIyGX4/validation-tools/mypy-cache /private/tmp/ingest-c0-review2-fresh-xIyGX4/candidate/tests/readiness/ingest
  ```

### admin-commands.json

- `board-validate`: exit **0**; cwd `/Users/chuckrussell/Dev/gendev/agent-framework`.

  ```sh
  /opt/homebrew/bin/uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate
  ```

- `board-render-check`: exit **0**; cwd `/Users/chuckrussell/Dev/gendev/agent-framework`.

  ```sh
  /opt/homebrew/bin/uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check
  ```

- `documentation`: exit **0**; cwd `/Users/chuckrussell/Dev/gendev/agent-framework`.

  ```sh
  /opt/homebrew/bin/uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py
  ```

- `metadata`: exit **0**; cwd `/Users/chuckrussell/Dev/gendev/agent-framework`.

  ```sh
  /opt/homebrew/bin/uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py
  ```

- `aggregate-whitespace`: exit **0**; cwd `/Users/chuckrussell/Dev/gendev/agent-framework`.

  ```sh
  git diff --check e42082195cd70d4ff384fcf73eac10303144aa07 fbe8201dc7829c5e6464f57566875660a3ea0c99
  ```

- `delta-whitespace`: exit **0**; cwd `/Users/chuckrussell/Dev/gendev/agent-framework`.

  ```sh
  git diff --check ecfa38bb71854bb3174ceb9ee82cbb87ef110e69 fbe8201dc7829c5e6464f57566875660a3ea0c99
  ```

- `staged-whitespace`: exit **0**; cwd `/Users/chuckrussell/Dev/gendev/agent-framework`.

  ```sh
  git diff --cached --check
  ```

### aggregate-commands.json

- `preflight-normal`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/candidate/tests/readiness/ingest/bootstrap.py preflight --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70
  ```

- `preflight-optimized`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c0-review2-fresh-xIyGX4/candidate/tests/readiness/ingest/bootstrap.py preflight --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70
  ```

- `init`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/candidate/tests/readiness/ingest/bootstrap.py init --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70
  ```

- `repeat-init-refuses`: exit **2**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/candidate/tests/readiness/ingest/bootstrap.py init --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70
  ```

- `frozen-normal-preflight`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/harness/run.py preflight --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70
  ```

- `frozen-normal-run`: exit **3**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/harness/run.py run --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70 --stage all
  ```

- `frozen-normal-run-offline`: exit **3**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/harness/run.py run --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70 --stage A2 --offline
  ```

- `frozen-normal-prepare-model`: exit **3**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/harness/run.py prepare-model --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70
  ```

- `frozen-normal-report`: exit **3**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/harness/run.py report --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70
  ```

- `frozen-optimized-preflight`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/harness/run.py preflight --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70
  ```

- `frozen-optimized-run`: exit **3**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/harness/run.py run --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70 --stage all
  ```

- `frozen-optimized-run-offline`: exit **3**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/harness/run.py run --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70 --stage A2 --offline
  ```

- `frozen-optimized-prepare-model`: exit **3**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/harness/run.py prepare-model --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70
  ```

- `frozen-optimized-report`: exit **3**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/harness/run.py report --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70
  ```

- `manual-promote`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/harness/run.py promote --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70 --manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/candidate-record.json --sha256 0937687c244e5ac0059ab520ea07ef56ccf89f261bd5f5a3b3cc509379f0bc27 --approval /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/promotion.json
  ```

- `stale-promotion-refuses`: exit **2**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/harness/run.py promote --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70 --manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/candidate-record.json --sha256 0937687c244e5ac0059ab520ea07ef56ccf89f261bd5f5a3b3cc509379f0bc27 --approval /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/promotion.json
  ```

- `lease-free-stop`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/harness/run.py stop --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70
  ```

- `sticky-stop-repeat`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/harness/run.py stop --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70
  ```

- `stopped-run-refuses`: exit **2**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/harness/run.py run --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70
  ```

- `stopped-report`: exit **3**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/harness/run.py report --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70
  ```

- `config-digest-refuses`: exit **2**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/harness/run.py report --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9 --config /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/manual-project/.friday_test/runs/review/config/control.json --config-sha256 7fd73b40232b43ee041a56bc6202f3de5700a43d5c0068d3fc58214637d99e70
  ```

- `matching-pyc-refuses-normal`: exit **2**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/pyc-normal/bootstrap.py preflight --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9
  ```

- `pyc-armed-private-control-normal`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -c 'import importlib.util; s=importlib.util.spec_from_file_location("private_paths",'"'"'/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/pyc-normal/paths.py'"'"'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)'
  ```

- `matching-pyc-refuses-optimized`: exit **2**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/pyc-optimized/bootstrap.py preflight --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/harness-manifest.json --harness-manifest-sha256 3040aaf82e769c73e817126dc4e181f700fabb2dfff4114171db81f2d86404a9
  ```

- `pyc-armed-private-control-optimized`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O -c 'import importlib.util; s=importlib.util.spec_from_file_location("private_paths",'"'"'/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/pyc-optimized/paths.py'"'"'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)'
  ```

- `fixture-git-init`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/git-fixture/source`.

  ```sh
  /usr/bin/git init --template=/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/git-fixture/template
  ```

- `fixture-git-add`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/git-fixture/source`.

  ```sh
  /usr/bin/git add -- selected.txt .gitignore symlink
  ```

- `fixture-git-commit`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/git-fixture/source`.

  ```sh
  /usr/bin/git -c core.hooksPath=/dev/null commit -m 'private fixture'
  ```

- `fixture-git-head`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4/aggregate/git-fixture/source`.

  ```sh
  /usr/bin/git rev-parse HEAD
  ```

### replay-commands.json

- `replay-corrected-normal`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/replay-corrected/replay.py
  ```

- `replay-corrected-optimized`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c0-review2-fresh-xIyGX4/replay-corrected/replay.py
  ```

- `replay-unfixed-normal`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/replay-unfixed/replay.py
  ```

- `replay-unfixed-optimized`: exit **0**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c0-review2-fresh-xIyGX4/replay-unfixed/replay.py
  ```

- `unfixed-suite-normal`: exit **1**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c0-review2-fresh-xIyGX4/replay-unfixed/source/tests/readiness/ingest/bootstrap.py selftest --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/replay-unfixed/harness-manifest.json --harness-manifest-sha256 393bb2618e82ae7eef32f69c1f326f6668be1f264e4afdcc02f7ffc15bb2a4ad --scratch /private/tmp/ingest-c0-review2-fresh-xIyGX4/replay-unfixed/suite-normal
  ```

- `unfixed-suite-optimized`: exit **1**; cwd `/private/tmp/ingest-c0-review2-fresh-xIyGX4`.

  ```sh
  /Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c0-review2-fresh-xIyGX4/replay-unfixed/source/tests/readiness/ingest/bootstrap.py selftest --harness-manifest /private/tmp/ingest-c0-review2-fresh-xIyGX4/replay-unfixed/harness-manifest.json --harness-manifest-sha256 393bb2618e82ae7eef32f69c1f326f6668be1f264e4afdcc02f7ffc15bb2a4ad --scratch /private/tmp/ingest-c0-review2-fresh-xIyGX4/replay-unfixed/suite-optimized
  ```

## Findings, evidence classes and limits

**Mandatory findings: none.** Each numbered correction above has its severity, violated requirement, source, actual reproduction, mitigation/regression and documentation impact traced. No proposed source repair or authority expansion is required from this review.

Independently reproduced: exact committed normal/-O suites, 62 own delta checks per lane, original corrected/unfixed call probes, unfixed regression-suite assertion witnesses, private static checks, read-only administration, manual/frozen entrypoints, valid armed pyc control, poisoned Git object export, metadata isolation failure, archive/startup negatives and closing identity/tool audits. Inspected only: supplied request/freeze/authority pins, permitted finding excerpt, original probe source, existing operational mypy launcher and unfixed command witness. Existing builder receipt conclusions, prior reports and previous scores do not establish any PASS here.

The unit qualifies installed, declared Python entrypoints on the pinned CPython/Darwin profile. Raw preinstall nonaudit file aliases, preacquired directory entries, arbitrary native calls and pathconf/statvfs-dependent profiles receive no qualification; an actual later profile needing them must be qualified or blocked under the unchanged higher contract. This is not a waiver of reads/probes/writes in the current supported C0 boundary. Audit events specifically close saved-thread-alias launches. Fake synchronous callback entry is the accepted-in-flight boundary, not an atomic service/OS guarantee. Metadata equality covers the named bounded roots/records and cannot establish universal absence of native effects. Trusted interpreter/stdlib and operator/local-owner assumptions remain explicit.

The higher obligations remain open: actual A0 source/index adapter and resolution; real A1 dependencies/import/CA/tool-child profiles; qualified A2 Docling/RapidOCR/counters and 6 PDF/6 DOCX/10 XLSX/8 PPTX fixture matrix; A3 real loaded deployment/model/window, counter, batching and state checks; cumulative actual time/RSS/disk/native-cache limits; A4 measured readiness and later product/consumer/store/test-migration/guide work. No upstream profile is called qualified, and no service was contacted or managed.

Historical whole-repository Ruff/collection/registry-format debt and protected dirty-YAML whitespace are supplied baseline failures, remain failed/unwaived, and were not rerun or repaired here. Scope static/admin/range checks passed. No whole-repository-green, product correctness, full-pipeline readiness or human acceptance claim is made.

**Honest advisory score: 9.2/10 for the bounded C0 candidate.** All mandatory scoped evidence is current and substantive; implementation remains a deliberately small, platform-qualified component foundation with documented unsupported channels and no real upstream-profile proof. The score is advisory, supplies no acceptance gate, and does not change the verdict's strict C0 boundary.

Evidence index: [evidence-manifest.json](evidence/evidence-manifest.json.gz), SHA256 **`24c784275277e54c946ac7ab57e95401753a2063ca7a2b597c1298a5f2b3a6ff`**. It hashes 3706 retained regular evidence/tool/fixture files and lists fixture symlink targets; report and index are separately hashed to avoid recursion.
