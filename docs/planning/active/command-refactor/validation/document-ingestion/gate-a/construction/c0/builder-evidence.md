Historical initial-source receipt for f6ef8649. For the changed source use
[correction cycle1 evidence](correction-evidence.md). The initial candidate was
CHANGES_REQUESTED; these old passes do not verify current code or close findings.

# C0 foundation — builder evidence, independent validation pending

This receipt applies only to [CC-01–10](implementation-scope.md). It does not
claim full HR-01–18 completion, Docling readiness or product INGEST implementation.
Source commit: `f6ef86491a88464bfc07cf2aabeb68d7e596e4de` (29 selected files).
[Committed selection manifest](harness-manifest.json), SHA256
`50e1d67cc01dae457155e11e1b79394975d7b18b89373117932b905b11cbbdeb`.
Bootstrap SHA256 `70e03f2215282e2d4aa6fd0a58161ce0b9858981a114caba49f4826f5833599c`.

## Reproduced builder checks

| Check | Result and evidence |
| --- | --- |
| Committed export selftest | 37 passed normal and 37 with `-O`; exact Git blobs, no working-tree fallback. |
| Frozen post-init run.py selftest | Same 37 passed normal and 37 with `-O`; 148 executions of37 distinct cases in total. |
| Manual control CLI | Preflight leaves fake project empty; init creates only its owned fake run; all/prepare-model exit3, report INCOMPLETE exit3, stop exit0, stopped effects refuse exit2, report remains available. |
| Private Ruff / format | Both exit0;25 Python files formatted, root rules unchanged. |
| Approved private mypy1.19.1 | Exit0, no issues in25 files; `-I -S -B`, hash-bound buffers, no-site-packages, private stubs/config/source/cache and Python-visible guard before tool import. |
| Administrative checks | Board36, dashboard, docs1082, metadata18 and owned/staged whitespace exit0. |
| Production preservation | All18023 protected tracked-file hashes,26 symlink targets and9 local metadata records match. Actual repository `.friday_test/` is absent. |

Commands, expected/actual exits, full unittest output, hashes and raw receipt paths
are in [the evidence index](evidence-index.json). Files are gzip archives of their
named raw text; hashes cover both compressed and uncompressed bytes. Supplied
scratch/tool caches are evidence inputs, never reviewer output destinations.

## Requirement trace

| ID | Source / intended call-phase witnesses |
| --- | --- |
| CC-01 | Exact approval and scope, protected-baseline/preservation receipts, selected manifest; no package/lock changes. |
| CC-02 | bootstrap.py/run.py; test_startup positive, dirty/extra/pyc, exact-buffer swap, armed private canary and guarded child controls. |
| CC-03 | config.py/paths.py; test_manifests, test_paths and test_cli preflight/new-only init. |
| CC-04 | ledger.py; promotion candidate/actor/tip, cumulative reserve, partial/tamper/concurrent/order/sticky-stop tests. |
| CC-05 | export.py; actual private Git fixture, committed export versus dirty/untracked data and operation/path/hash refusals. |
| CC-06 | startup.py/protection.py; armed discovery assertion, read/stat/write/dir_fd/thread/socket controls, distinct change detection and truncated-snapshot tests. |
| CC-07 | environment.py; inherited-secret/proxy stripping and guarded-data versus executable-site inventory. |
| CC-08 | window.py; in-process fake loaded-state/window/expiry/revocation/route/model/vector/token/attempt budgets. No HTTP client or model-token claim. |
| CC-09 | stages.py/reports.py/fixtures.py; manual receipts, incomplete/unactivated nonzero results, deterministic structural PDF/DOCX/ZIP controls. Only2 seeds. |
| CC-10 | Static receipts and private tool receipts; fresh independent review remains pending. |

## Tool qualification and exclusions

Chuck [approved the exact five-wheel profile](private-typecheck-approval.json).
[Execution receipt](private-typecheck-execution.json) records five requests,
2609181 payload bytes, wheel hashes/RECORD/licenses/startup inspection and private
extraction. The frozen proposed profile's NOT ACTIVATED label is historical,
superseded by that later approval/receipt; no proposed bytes were rewritten.
Mypy's stock `/usr/local/lib/mypy` fallback is filtered out in the operational
launcher to prevent ambient global stubs; root rules are unchanged. One exact
public OS-version file is a hashed interpreter input. Two absent CPython build
metadata probes are refused by the guard and handled by sysconfig; typing still
finishes successfully. No unknown filesystem read or network fallback is enabled.

Development fixture attempts and initial private-tool setup refusals are not formal
candidate proof. Formal receipts use the real committed source above. The failed
unscoped whitespace check reports pre-existing trailing whitespace in the protected
dirty models YAML; it is unwaived and untouched. The scoped/staged checks pass.
Historical root Ruff/collection/format debt was not rerun for this test-only slice;
there is no whole-repository-green claim. No product suites, installs or services
were exercised.

The full A0–A4 adapters, actual upstream imports/native child qualification,
30-format oracles, real counters/model window, comprehensive runtime resource
control and final readiness report remain required future work. No actual store,
provider/model request, LM Studio operation, production test directory, push or
acceptance occurred. C0 is a component foundation, not the full pipeline.
