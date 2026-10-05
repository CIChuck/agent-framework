# REM-001 implementation and builder verification report

Date: 2026-10-05. Branch: `feature/friday-telemetry-rewire`.
Authority preparation commit: `98cc9e74cf40320af08533f4915e394eecf39537`.
Original preparation base: `2155a0fc51f5b20dea4e35c6cfc70f1d52002735`.
Product before remediation: `0c7b6d4c416402443d140a5ee09abed70be34c69`.
Final candidate and delta/aggregate diff are pinned in the next independent
validation request. Independent result pending; no completion or acceptance.

## Behavior and exact changes

REM-001 changes only composite.py, test_providers.py, and the telemetry README.
A never-published first child ID retains normal compatibility. A reused ID gets
an opaque composite ID allocated using an instance namespace and monotonic
counter, with explicit collision checks against every previously published ID.
Each public ID still maps to its own original child/provider tuple. Ends remove
active ownership before fan-out, so repeated or stale ends cannot close a later
span. Published-ID strings remain reserved for instance lifetime; completed
provider and payload references are released. This entails cumulative string
retention proportional to the number of published spans, as the README states.
No dependency, timing-test, Chat source, OTel, exporter, state or configuration
change occurred.

## Verification matrix

| Check | Preparation base / before REM-001 | Remediated builder result |
| --- | --- | --- |
| Six new deterministic collision regressions | 6 failed against clean pre-remediation source | All six pass within focused suite |
| Focused CD-001 suites | 129 passed before remediation | 135 passed |
| Earlier independent synthetic probes, rerun by builder | Historical evidence preserved, not self-issued validation | 14 passed, including original replacement collision probe |
| Full Chat/telemetry suites | Preparation base: 676 passed, 5 skipped, 1 timing failure, 3 localhost setup errors; pre-remediation: 718 passed with same identifiers | 724 passed, 5 skipped, same 1 failure and 3 errors |
| Changed-file Ruff | Earlier gate passed | All ten changed Python files pass |
| Root Ruff | 337 failures | 337 failures; exact normalized diagnostic tuples equal, no introduced or removed diagnostics |
| Root pytest with exactly two approved live-module exclusions | 2649 collected, collection halted by duplicate test_display module | 2697 collected, same collection error; no full root execution pass claimed |
| Root importlib diagnostic, additional to required gate | Revealed two sibling test_mcp_execution_security import errors | Not a substitute for the required failing root gate; no metadata or tests altered |
| Affected source mypy, Python 3.10 / 3.13 | Both pass for existing five source files; new observer absent at preparation base | Both pass for all six source files |
| Frozen-source Python 3.10 syntax parse | Five files pass | Six files pass |
| Minimum-version API review | Package minimum and dependency metadata unchanged | Introduced APIs reviewed against actual installed Python 3.10 stdlib and official Python 3.10/Pydantic 2.0 documentation; detailed symbols/import lines and hashes retained |
| Real Python 3.10 import/lifecycle smoke | Fails before test body: installed interpreter lacks pydantic | Stdlib probe stage passes; full observer/package smoke fails on same missing dependency. No dependency install/download or full 3.10 runtime pass claimed |
| Warm isolated PTY timing rerun, performed sequentially | Existing 0.8-second criterion fails | Same unchanged criterion fails |

Raw commands, cwd, revisions, environment allowlist, source hashes, nonzero
statuses, full logs, syntax/smoke scripts, API evidence, and preflight module
hashes are in `validation/REM-001-builder/builder-check-artifacts.tar.gz`, with
checksums in `sha256.json`. Provisional builder checks use an isolated checkout
of the authority commit plus exactly the three approved product-file overlays;
no provisional checkout is presented as a formal frozen candidate. Newly added
A01 preparation-base checks are retrospective evidence, not pre-build runs.

## Safety, scope, and remaining gates

Before collection, all root test/helper Python files were parsed and screened
with conftests, fixture storage and provider/subprocess launch paths. Tests use
synthetic/temporary data. The external sitecustomize audit guard blocks public
DNS and non-loopback connect/sendto in imports and inherited test subprocesses;
mocked Web HTTP tests otherwise attempt public DNS in validators.py. Identical
allowlist and guard apply to baseline/candidate. No additional test exclusion,
privileged test execution, real data, provider credentials, exporter activation,
vendor traffic, or test result suppression occurred.

Root collection and 337 lint failures are unresolved repository baseline gates,
not waivers. Three localhost fixtures cannot bind under the sandbox. The timing
failure persists, but WVR-001 remains unapproved and its all-other-gates-pass
condition is not satisfied. A Python 3.10 interpreter is installed, but its
runtime dependencies are absent; this smoke limitation remains explicit. The
builder cannot grant VERIFIED or broaden REM-001 to these out-of-scope files.

Fresh A02 directive readiness review CDR-003 returned READY at `98cc9e7`, with
all eleven authority hashes unchanged. This is distinct from product review.
The next fresh validator must assess REM-001 delta and aggregate TELEM-01,
independently reproduce required evidence and report unresolved AC-06 gates.
All 64 unrelated preservation entries remain unchanged; original dirty YAML,
board/tool-continuity edits, deletion, security tree and backups remain excluded.
