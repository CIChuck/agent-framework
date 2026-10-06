# TELEM-01 verification profile — CD-001 amendments A01, A03, A04 and A05

Status: Approved verification authority, 2026-10-05.
Maintainer evidence: "approved, proceed" following the independent CD-001 review
findings CDR-001 and CDR-002. This profile changes verification and reporting,
not telemetry behavior. A04 explicitly changes package minimum versions and
metadata/setup scope under [REM-003](remediation/REM-003-python-minimum-directive.md),
approved by the maintainer's "Make it happen." on 2026-10-05.

## Required scope and commands

Every command in [CD-001](directives/CD-001-local-telemetry-assembly.md) is
mandatory. Run against a stable, isolated tracked checkout; do not lint or test
the unrelated untracked security tree, dirty config, or original runtime state.
Root Ruff uses `uv run ruff check .` with the repository's configured exclusions
only. Root pytest uses root `testpaths` (all package test trees and experiment
test trees), with exactly these additional safety exclusions:

- `packages/friday-chat/tests_chat/test_live_lmstudio.py`: explicitly live model
  service tests, gated by `FRIDAY_CHAT_LIVE`.
- `packages/friday-llm/tests_llm/test_live_lmstudio.py`: explicitly live model
  service tests, gated by `FRIDAY_LLM_LIVE`.

A03, approved by the maintainer on 2026-10-05 through REM-002, changes the
root invocation to `uv run pytest --import-mode=importlib` plus the same two
`--ignore` arguments above. Prepend the external network guard, the isolated
package source directories, `<isolated-checkout>/packages/friday-chat/tests_chat`
and the isolated checkout root to PYTHONPATH, in that order. The helper entry
resolves existing bare sibling test imports without changing test bodies. Run
the same invocation with `--collect-only` on preparation base and candidate
before full execution. Preserve the original A01 failed default invocation.

These exclusions enforce the already approved no-live-services boundary. They
are not a deterministic-failure waiver. Do not exclude terminal timing tests,
loopback fixtures, other packages, experiments, or failing tests by implication.
Keep the full two-package command too, with live activation flags absent so its
existing live tests skip; record skip counts and reasons.

Expand the changed-file placeholders from the exact preparation-base/candidate
diff. The existing TELEM-01 changed-source list is:

```text
packages/friday-chat/src/friday_chat/telemetry.py
packages/friday-chat/src/friday_chat/config.py
packages/friday-chat/src/friday_chat/runtime.py
packages/friday-chat/src/friday_chat/cli.py
packages/friday-chat/src/friday_chat/app.py
packages/friday-telemetry/src/friday_telemetry/providers/composite.py
```

Changed-file Ruff additionally includes changed Python tests from the same diff.
New candidate changes must remain within approved directives and must regenerate
the frozen exact lists, rather than silently retaining an obsolete list.

## Broad-test safety preflight

Before pytest collection (which executes imports), inspect the frozen discovery
configuration, test modules, conftests, imported helpers, and subprocess launch
paths for credential loading, real data, unmocked service access, and writes.
Record the reviewed revision and paths in a preflight artifact. Execute only
with synthetic providers, temporary filesystem state, and deterministic
loopback fixtures. Use an environment allowlist without provider credentials,
live activation flags, telemetry/exporter activation, or inherited endpoint
configuration; do not print or persist discarded environment values.

The isolated checkout must contain no copied `.env`, `.friday`, transcript or
Chroma state. Ensure imports resolve its package sources, not editable sources
in the original dirty checkout. Use offline/no-sync execution where needed:
`UV_CACHE_DIR=/private/tmp/friday-uv-cache`, `UV_NO_SYNC=true`, `UV_OFFLINE=true`,
and `LITELLM_LOCAL_MODEL_COST_MAP=true`. Record interpreter/tool versions and
source-resolution setup. Do not install or download missing tools implicitly. A03's completed Python 3.10 provisioning remains historical evidence.
A04/REM-003 replaces the supported minimum with Python 3.13.4. Tests use the
already-installed Python 3.13.10 environment without synchronization. Only
REM-003 permits bounded lock regeneration, cache/offline first with optional
credential-free public PyPI reads; surviving dependency pins must not change.
No interpreter download, source build or shared environment mutation is allowed.

If a discovered test cannot satisfy these boundaries, stop before collection or
execution and identify its exact module/node, import/helper path, unsafe effect,
and required bounded authority decision. No further test exclusion is approved. A05/REM-004, approved by
"I approve both REM-004 and WVR-002.", supersedes A03's three-node privilege
restriction: exactly the11 synthetic listener nodes in REM-004-scope.json may
bind localhost ephemeral ports during the complete root and Chat+telemetry
commands. Normal-user sandbox escape only; no sudo/admin or real service access.
Fresh complete import/helper/subprocess preflight, allowlist, isolated sources and
unchanged inherited guard remain required. Full commands must exit zero; separate
node reruns do not replace their gates. Missing safe execution is a missing gate.
This profile authorizes no vendor traffic or original application data access.

## Supported Python 3.13.4 minimum

All workspace projects and the lab project require Python >=3.13.4 under A04.
Run `uv run mypy --python-version 3.13 <exact changed source files>` with root
configuration; do not weaken typing. Python 3.10 checks are historical and are
no longer current acceptance gates. This is an explicit support-contract change,
not a waiver or a claim that the old Python 3.10 runtime passed.

Parse the exact changed-source list with `ast.parse(..., feature_version=(3, 13))`.
Syntax alone does not establish API/runtime compatibility. Review changed
stdlib/dependency APIs against Python 3.13 and the frozen dependency pins.
Independently smoke-test the real public Chat observer and Composite lifecycle
on installed Python 3.13.10, using synthetic providers, temporary state, the
same guard and no credentials. Record the actual interpreter patch version;
do not claim an exact 3.13.4 runtime run when only 3.13.10 is installed.
Package SpecifierSet checks establish that 3.13.3 is rejected and 3.13.4 accepted.
No exact-floor interpreter download is authorized; do not silently waive a
missing required runtime check. Repeat applicable supported-runtime checks on
preparation base/candidate, omitting then-absent new observer source explicitly.

## Baselines, frozen requests, and implementation reporting

Run the same broad/typing profile against the preparation base and candidate.
For checks added after implementation, label both as retrospective runs, not as
pre-build evidence. Record command, cwd, revision, environment variable names
and approved nonsecret values, file lists, exclusions, exit status, totals,
failure/skip identifiers, logs, and whether evidence is baseline or candidate.
Use identical approved isolation and tool settings for the comparison.

The next validation request must pin this profile, all authority hashes, exact
expanded commands/lists, both revisions and diff, preflight evidence, exclusions,
known failures, and any separately approved waiver. Preserve old requests and
reports as historical frozen evidence; do not edit their recorded outcomes.
The next implementation/remediation report must include a row for each command,
distinguish 3.13 typing, the metadata patch floor, and actual runtime evidence, and map results to AC-06.
Pending or nonzero results remain pending or failed; narrower successes do not
replace missing broad gates. Unchanged baseline failures are not implicit waivers.

Changing this authority requires a fresh directive review and fresh subsequent
implementation review. Directive readiness does not verify the existing code,
resolve VAL-001-F01, approve REM-001/WVR-001, or complete the initiative.

## A05 exact archival lint disposition and expanded source checks

The approved [REM-004](remediation/REM-004-verification-closeout-directive.md)
adds only its exact file/site scope, regression and positive/negative contracts.
Regenerate changed-source, Python-test and owning-package lists from the aggregate
preparation-base/candidate diff. Require changed-source3.13 mypy, syntax, changed-
file Ruff, all owning packages and original telemetry checks; no obsolete six-
source substitution. The three exact existing response-branch typing errors must
be fixed under R4-06b, never waived.

Approved [WVR-002](validation/WVR-002-archived-probe-lint.md) covers only the exact
326 archived findings and four content hashes in REM-004-scope.json. Run unchanged
root Ruff, retain its nonzero raw result and independently verify exact diagnostic
multiset/hash/tool/config matches, zero live/other findings and all other gates
passing. The report names the approved exception rather than claiming raw lint
passed. No pytest, typing, security, listener or future-phase exception exists.
WVR-001 remains unapproved. All WVR-002 expiry conditions apply.
