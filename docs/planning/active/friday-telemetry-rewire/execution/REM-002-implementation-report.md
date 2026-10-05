# REM-002 verification execution report

Status: executed under approved A03; mandatory aggregate gates remain failed.
This is builder evidence, not implementation VERIFIED or maintainer acceptance.
Authority candidate: `362b66c720ad3681e556aef8fa1a4a069deb8a1f` after fresh
CDR-005 READY. Reviewed product remains `3a69050`; preparation base `2155a0f`.
No product source/test body/deadline/config, package metadata or lock changed.

## Matched retrospective results

| Required check | Candidate | Preparation baseline |
| --- | --- | --- |
| A03 root collect, importlib + isolated Chat helper entry | 2727 collected, exit0 | 2679 collected, exit0 |
| A03 complete root pytest, exact two live exclusions | 2699 passed,16 failed,11 errors,1 skipped; exit1 | 2651 passed, same16 failed/11 errors/1 skipped; exit1 |
| Root Ruff | 337 diagnostics, exit1 | Identical337 diagnostics, exit1 |
| Changed Python Ruff | 10 files, pass | 9 existing files, pass |
| Source mypy3.10 and3.13 | Both6 files, pass | Both5 existing files, pass |
| 3.10 syntax and unchanged API review | Pass; genuine package import failure retained separately | Pass for5 existing files |
| Focused pytest | 135 passed, exit0 | 87 passed, exit0; observer source/tests absent |
| Complete Chat + telemetry pytest | 724 passed,1 failed,3 errors,5 skipped; exit1 | 676 passed, same failure/errors/skips; exit1 |
| Approved privileged localhost rerun, exactly three nodes | 3 passed, exit0 | 3 passed, exit0 |
| Actual installed3.10 package smoke | Exit1: locked LiteLLM imports unavailable typing.NotRequired; lifecycle not reached | Identical import failure; lifecycle not reached |
| Board/docs checks | Pass:24 tracked tasks/403 Markdown files | Existing absent active-lane failure; exit1 |
| Whitespace/state/authority/preservation | Pass; unchanged tracked review files/12 pins/64 preserved entries | Frozen tracked baseline unchanged |

Root failure/error identifiers and normalized lint diagnostic tuples match exactly,
not merely counts. Root collection now exposes baseline defects/environment
limits that could not run under A01's default duplicate-module import failure.
The original A01 failure remains in VAL-002, not erased or turned into PASS.
Root failures: one unchanged0.8s PTY acknowledgement, seven runtime/native-tool
registration tests, two optional DOCX/XLSX dependency expectation tests, six Web
validation tests under the non-loopback guard. Eleven listener setup errors are
three Chat and eight LLM wire-capture nodes. Only the three approved Chat nodes
were rerun with privilege; broad nonzero suites remain failed. No extra live
exclusion, test change, guard weakening or broad privilege was introduced.

## Python3.10 provisioning and stop condition

Created a separate environment using existing CPython3.10.19. Frozen uv export
preserved lock hash `53efa78379fb81d3089aea9f64e73b0355eb6b292b61ca2bf902cd28babf9272`.
Offline cache-first installation found missing packages; the sandbox blocked
public DNS, then already-approved bounded network permission fetched locked
public PyPI artifacts. No interpreter download, re-resolution, source build or
unlocked build dependency was used. The locked PyPika0.48.9 has no public wheel:
reused its existing pure-Python cached wheel after comparing all16 package files
byte-for-byte with the exact hash-checked locked source archive and verifying
its name/version/no-dependencies metadata. Recorded derived wheel SHA-256 and
installed it offline with --require-hashes. Installed127 locked distributions;
all public artifact URLs/hashes, chosen versions, scripts and failed attempts
are retained. Original PyPika cache files remained unchanged.

Both real package smoke imports then fail at locked LiteLLM1.100.1
`llms/anthropic/experimental_pass_through/context_management/editors/compact.py:17`:
`from typing import ... NotRequired ...` is unavailable on Python3.10. No stub,
monkeypatch, dependency replacement, constraint edit or minimum-version raise
was attempted. This reaches REM-002's incompatibility stop condition. Python3.10
observer/composite lifecycle PASS is not claimed. The remaining permitted checks
are independent evidence and do not substitute for this missing runtime gate.
The existing3.13 test environment uses approved no-sync execution; its versions
are separate from the newly provisioned frozen3.10 dependency set. Its195
installed version/RECORD hashes and pyvenv config remain unchanged.

## Evidence and unresolved disposition

Raw commands, expanded lists, revisions, environment allowlists, exits, logs,
artifact provenance and before/after hashes are losslessly archived in
`validation/REM-002-builder/builder-check-artifacts.tar.gz` with sha256.json.
Temporary test state, caches, database trees and package binaries are excluded.
Safety preflight rechecked621 candidate/619 baseline raw inventory modules;
all are unchanged from the reviewed product. Synthetic tests use isolated
sources, temporary state and the unchanged network guard; no real .friday,
transcript/Chroma data, provider credentials, vendor calls or runtime exporters.
The required historical console OTel fixture's shutdown output exception is
retained; it is not a remote exporter/runtime success claim.

REM-002 setup/reruns are performed, but AC-06 is unresolved. Existing337 lint
diagnostics, root baseline failures, listener permission limits, timing and the
newly exposed frozen dependency incompatibility remain unwaived. Work remains
started, local, validation pending for fresh delta/aggregate independent review.
No source VERIFIED, completion, acceptance, delivery or exception is inferred.
