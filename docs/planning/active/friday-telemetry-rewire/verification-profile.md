# TELEM-01 verification profile — CD-001 amendments A01 and A03

Status: Approved verification authority, 2026-10-05.
Maintainer evidence: "approved, proceed" following the independent CD-001 review
findings CDR-001 and CDR-002. This profile changes verification and reporting,
not product behavior, package minimum versions, or allowed product paths.

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
source-resolution setup. Do not install or download missing tools implicitly. A03 explicitly authorizes
a separate temporary Python 3.10 environment using frozen lock versions, hashes
and compatible metadata. Use cached distributions first; public PyPI downloads
are approved only for that environment. Record every artifact URL/hash and
installed version. Do not alter the shared environment, lock or metadata.
No interpreter download or dependency re-resolution is authorized.

If a discovered test cannot satisfy these boundaries, stop before collection or
execution and identify its exact module/node, import/helper path, unsafe effect,
and required bounded authority decision. No further exclusion is approved. A03 permits bounded privileged execution
of exactly the three synthetic localhost nodes named in REM-002, with the
non-loopback network guard and the same isolated credential-free environment.
Other test execution remains unprivileged. Retain broad-suite failures if
listener permissions remain unavailable there; the three-node rerun supplies
additional evidence and does not turn a nonzero broad suite into PASS. An incomplete safety preflight or unavailable runtime
is reported as a missing gate, never a passing root test run. This profile does
not authorize vendor traffic or reading the user's existing application state.

## Advertised Python 3.10 compatibility

Both affected packages continue to advertise Python >=3.10. Required typing is
`uv run mypy --python-version 3.10 <exact changed source files>` using the root
configuration, separately from the retained Python 3.13 command. Do not weaken
typing or raise package minimum metadata to make the checks pass.

Also run this syntax check on the exact changed-source list, saved as a frozen
list argument rather than relying on discovery:

```python
import ast
import sys
from pathlib import Path

for filename in sys.argv[1:]:
    ast.parse(Path(filename).read_text(encoding="utf-8"),
              filename=filename, feature_version=(3, 10))
```

Execute it with `uv run python <external syntax-check script> <exact changed
source files>`; store the script and hashes with validation evidence. Syntax
parsing alone does not establish API or runtime compatibility. Review every
introduced/changed standard-library import and API against Python 3.10
availability, and every changed dependency API against frozen supported metadata.
Record symbols, source lines, availability evidence (installed 3.10 stdlib/stubs
or official versioned documentation), and any compatibility guard.

Use an already available Python 3.10 interpreter for synthetic observer/composite
import and lifecycle smoke checks when available; do not download an interpreter under
this directive. A03 permits locked dependency installation in a separate
temporary environment for the existing installed interpreter. If unavailable, report that limitation and rely only on the
explicit typing, syntax, and API review evidence, without claiming a 3.10
runtime pass. Missing or inconclusive required typing/syntax/API evidence needs
a bounded authority decision or waiver before `VERIFIED`; interpreter absence
does not silently waive those checks. Run the same applicable checks on the
preparation base, omitting the then-absent new telemetry source and recording it.

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
distinguish 3.13 typing from minimum-version evidence, and map results to AC-06.
Pending or nonzero results remain pending or failed; narrower successes do not
replace missing broad gates. Unchanged baseline failures are not implicit waivers.

Changing this authority requires a fresh directive review and fresh subsequent
implementation review. Directive readiness does not verify the existing code,
resolve VAL-001-F01, approve REM-001/WVR-001, or complete the initiative.
