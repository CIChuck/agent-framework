# VAL-004 independent REM-003 delta and aggregate review

CHANGES_REQUESTED

Candidate `285254b4ebcafa612393baceb38a8a62ffed2960`; delta base `09fe69090f33ae9c047e2e101fe87727d52f9734`; aggregate base `2155a0fc51f5b20dea4e35c6cfc70f1d52002735`. Fresh read-only reviewer `/root/python313_validator`, 2026-10-05. All pinned authority and guard hashes match. Builder implementation reports, prior validator conclusions and private reasoning were not read. Controller supplied a potential marker-selection concern during review; it was independently reproduced.

1. **VAL-004-F01 (high): grpcio selection drift exceeds migration scope.** `uv.lock:417`, `1613`, and `2652` remove the reachable Python3.13 grpcio1.67.1 branch and make1.76.0 unconditional. Baseline lock lines561-562,1879-1888 and3532-3533 select1.67.1 for3.13 and1.76.0 for3.14+. Marker checks at3.13.4 and3.13.10 on Windows/macOS/Linux reproduce that upgrade. REM-003 forbids dependency upgrades and permits removal only of unreachable alternatives. Preserve the original per-environment selection, sources and artifacts, reconcile the board/evidence pin-preservation claim, commit a new candidate and request fresh review. Required regression: selected graph comparison across those environments, offline lock check and fresh aggregate review. See [lock-selection-comparison.json](raw/lock-selection-comparison.json.gz) and [baseline.lock](raw/baseline.lock.gz).
2. **VAL-004-F02 (high): aggregate AC-06 remains nonpassing without a waiver.** Root Ruff fails with459 diagnostics, versus337 baseline:122 additional under the new targets,0 removed (UP017: 71, UP047: 4, UP046: 6, UP040: 12, UP041: 19, UP043: 7, UP035: 1, I001: 2). Complete Chat+telemetry fails with1 failed,724 passed,5 skipped,3 errors. Root importlib pytest fails with16 failed,2699 passed,1 skipped,11 errors. Exact package/root failure IDs match baseline: PTY acknowledgment, native-tool registration, optional DOCX/XLSX readers, guarded-Web DNS and listener permissions. Baselines do not waive gates. Obtain separately bounded maintainer dispositions; no cleanup/suppression/deadline/exclusion expansion is authorized here. Preserve failed AC-06 and started work state. See [ruff-comparison.json](raw/ruff-comparison.json.gz), [pytest-comparison.json](raw/pytest-comparison.json.gz), [packages.log](raw/packages.log.gz) and [root.log](raw/root.log.gz).

| Candidate gate | Result |
| --- | --- |
|18 workspace/lab requirements; SpecifierSet rejects3.10/3.11/3.12 and3.13.0-3.13.3, accepts3.13.4/3.13.10 | PASS |
|Manifest dependency/group/source constraints unchanged; LiteLLM1.100.1 retained | PASS |
|Ruff py313/mypy3.13, `.python-version`, scaffold, Docker FROM and current setup/migration docs | PASS |
|REM-003 no source/test edits; aggregate source/test manifest | PASS |
|Surviving lock identities/sources/sdist/wheel artifact subset | PASS as subset only; selection FAIL in F01 |
|`uv lock --offline --check --no-python-downloads --no-build` | PASS |
|Changed-file Ruff; six-source mypy3.13; ast Python3.13 syntax | PASS |
|Focused six-module suite | PASS:135 tests |
|Genuine public Chat observer/Composite synthetic lifecycle on3.13.10 | PASS |
|Root collection, exactly two approved live module exclusions | PASS:2727 collected |
|Root Ruff; complete package/root suites | FAIL, F02 |
|Board/docs validation; delta and aggregate `git diff --check` | PASS |
|Complete candidate tracked before/after hashes | PASS:identical |

The support floor itself is correctly migrated. The complete REM-003 delta cannot be verified because lock-selection preservation fails; aggregate TELEM-01 cannot be verified because AC-06 is unwaived. Runtime evidence is actual3.13.10, never an exact3.13.4 run. Smoke uses genuine isolated public sources, two synthetic providers, nested/replaced span ownership, exactly-once end, privacy and caller-owned lifecycle; no stubbed dependencies. Supported3.13.4 is established by metadata tests only.

Every executed command, environment allowlist, cwd, revision, exit status and log hash is in [evidence.json](raw/evidence.json.gz). Baseline raw artifacts were independently inspected and compared under the same no-sync/offline/guard/importlib settings; they are reused retrospective evidence, not new reviewer runs. The guard hash and604 unchanged source/test files were checked before collection, with all ten conftests, risky subprocess/fixture helpers, temporary storage and synthetic ignored audit writes inspected. Candidate had no `.env`, `.friday` or Chroma state before execution. No services, credentials, sync, downloads, installs, image effects or original application state were used by this reviewer. The three approved privileged Chat loopback nodes were not rerun; listener errors remain explicit failures. No repetitive broad reruns occurred.

Residual limits: shared installed dependency versions/RECORD hashes and pyvenv.cfg match the recorded REM-002 inventory (195 normalized distributions), but this is not a full installed-file integrity audit. Current no-sync runtime uses grpcio1.67.1, so it supplies no candidate1.76.0 install/runtime evidence. Original checkout `uv.lock` changed concurrently; reviewed isolated candidate tracked hashes did not change. Controller confirmed this was its authorized mechanical F01 remediation; the new lock is outside this frozen review and needs a fresh candidate/review. Future-Python, exact-floor interpreter and Docker execution are not claimed. No maintainer acceptance, completion or delivery is inferred.

Raw artifacts are gzip-compressed byte-for-byte copies. Original names and content hashes remain in the evidence record; decompress a linked artifact to inspect it.
