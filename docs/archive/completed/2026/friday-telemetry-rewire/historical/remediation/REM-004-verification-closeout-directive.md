# Approved REM-004: resolve the remaining TELEM-01 verification gates

Status: Approved construction directive, 2026-10-05.
Approved by: repository maintainer Chuck Russell.
Approval evidence: "I approve both REM-004 and WVR-002."
WVR-002 separately approved in that same explicit response.
A06 and WVR-003 explicitly approved 2026-10-06: "I approve A06 and WVR-003".
[A06](REM-004-A06-command-registry-compatibility.md) supersedes only the
all133-fixed/zero-live lint condition below: fix132 and retain the exact one
CommandRegistry UP046 under [WVR-003](../validation/WVR-003-command-registry-variance.md).
All other scope, tests, typing, guard, listeners, archive pins and gates remain required.
Preparation authorized: maintainer's 2026-10-05 "proceed" following the recommendation
to prepare this exact directive and obtain independent review.
Initiative: friday-telemetry-rewire. Work unit: TELEM-01 / REM-004, approved CD-001 A05.
Preparation HEAD: 686a5bd17d84fea3ec3a3d329df2d39c70d10c03.
Branch: feature/friday-telemetry-rewire. Current aggregate outcome: CHANGES_REQUESTED.

## Authority and finding map

Explicit maintainer direction, repository engineering/security policy and accepted
contracts precede this directive. The existing authority-manifest.yaml, build and
tactical plans, CD-001 A01–A04 and verification-profile remain controlling.
REM-003:19–23 explicitly left these components outside its implementation authority.
This proposal maps VAL-005-F01 exactly once into R4-01 through R4-06 below; those
components do not create six independently waived copies of the finding.

Preparation and proposal reviews are historical. The maintainer explicitly approved
this exact directive and WVR-002 on 2026-10-05. CD-001 A05, the verification
profile and controlling manifest record that approval. Freeze amended authority
and obtain fresh readiness before implementation. WVR-002 covers only the exact
326 historical diagnostics; all live lint, typing, security and complete-suite
gates remain mandatory. No broader exception or initiative acceptance is granted.

Use a separate remediator for the entire work unit: it includes security, public
type boundaries and a repeated aggregate failure. The controller may prepare and
record evidence but may not substitute self-validation for independent review.
Previous unsuccessful verification attempts have already been returned to the
maintainer; this proposal is the concrete new remediation decision, not another
automatic cycle under REM-003.

## Diagnosis and frozen exact scope

[REM-004-scope.json](REM-004-scope.json) is the exact baseline inventory: 459 root
Ruff diagnostics, 326 in four historical MCP validation probes, 133 in 80 current
files; 16 root failures and 11 fixture errors. It pins file hashes, rules,
locations/messages and all 27 node IDs. Counts derive from immutable VAL-005 raw
root Ruff/root pytest evidence at 4c0afdb; no governed source/test/lock changed
between that revision and the preparation HEAD.

Current diagnostic probes are recorded in
[REM-004-diagnosis.md](REM-004-diagnosis.md). All seven native-tool nodes pass alone
and fail after one agent-registry test; its autouse fixture clears the global
decorator registry without restoring it. Private IPv4/IPv6 literals are accepted
when the guard prevents their DNS lookup; the validator swallows the resolver
exception. The localhost failures are sandbox binding errors. Reader tests infer
missing dependencies from invalid ZIP payloads even when those dependencies are
installed. The PTY acknowledgment timer includes cold imports.

Product/test paths may change only as follows:

1. R4-01: `packages/friday-agent/tests_agent/conftest.py` and
   `packages/friday-runtime/tests_runtime/test_di.py`; fixture isolation and one
   deterministic preservation regression only. No agent/runtime product change.
2. R4-02: `packages/friday-tools/tests_tools/test_filesystem_readers.py`; deterministic
   dependency-unavailable and invalid-archive tests only. No reader source change.
3. R4-03: `packages/friday-tools/src/friday_tools/web/validators.py`,
   `packages/friday-tools/tests_tools/test_web_validators.py`,
   `packages/friday-tools/tests_tools/test_web_reader.py`; literal-IP validation and
   resolver-independent security coverage only.
4. R4-04: `packages/friday-chat/tests_chat/test_reorganization_terminal.py`; child
   readiness/parent trigger handshake and bounded test cleanup only. No production
   application change or acknowledgment deadline increase.
5. R4-05: no fixture/product changes; exactly the 11 synthetic localhost nodes in
   REM-004-scope.json may bind `127.0.0.1` with OS-assigned ephemeral ports under the
   execution profile below. Their complete containing suites must also run.
6. R4-06: exactly the 80 keys in `live_lint_files` in REM-004-scope.json, and only the
   identified diagnostic sites plus necessary imports/annotations/line wrapping,
   and the three exact typing sites in R4-06b below.
   These overlap some paths above; the union is the allowed manifest. Allowed rules:
   UP017(71), UP041(19), UP040(12), UP043(7), UP046(6), UP047(4), UP035(1), I001(2),
   E501(11). No other opportunistic refactoring. Focused public typing regressions
   may additionally be added to these existing files:
   `packages/friday-core/tests_core/test_interfaces.py`,
   `packages/friday-cli/tests_cli/test_cancellation.py`,
   `packages/friday-memory/tests_memory/test_llm_completion.py`, and
   `packages/friday-chat/tests_chat/test_llm_adapter_migration.py`.

If one of the named existing regression files is absent, stop and revise that
path before construction rather than silently creating a differently named file.
No files in docs/archive, previous review artifacts, dependency manifests/lock,
scaffolds, Dockerfiles, local config or original runtime state may change.

Planning closeout paths are the active telemetry packet's new REM-004 documents,
execution report/log, CD-001/A05, verification profile, current authority manifest,
index, fresh request/review/evidence files, and telemetry-only board/dashboard
changes. Preserve unrelated dirty edits through a hashed manifest and selective
staging. Older controlling amendments and review outcomes remain historical.

## Required fixes and acceptance criteria

**R4-01 — Registry fixture isolation.** Snapshot the pre-test decorator registry,
clear it for each agent test, and restore the snapshot in a finally block after
the test. Restoration includes original names and their declaration metadata;
test-created registrations must not leak. Avoid source imports/reloads, new global
production state, or cached catalog changes. Preserve runtime dependency-binding,
native/provider category filtering, async MCP registration, retry ownership and
stop/cleanup assertions. Require both all seven exact runtime nodes alone and the
same nodes after the full agent package in one pytest process; all must pass.
Record the ordered regression failing with the old clear-only fixture and passing
with restoration; it is the cross-package isolation regression. Do not weaken
the missing-tool assertions.

**R4-02 — Optional reader tests.** Use scoped import monkeypatching to force the
specific `docx` or `openpyxl` import to raise ImportError even when installed.
Assert failure, actionable dependency error and exact `missing_dependency`
metadata. Restore imports automatically; do not unload or mutate shared installed
packages. Separately verify invalid ZIP/container errors with installed optional
dependencies and valid synthetic document/spreadsheet reads. No network, installs,
dependency change or catch-all "any failure is acceptable" assertion.

**R4-03 — Literal-IP SSRF protection.** Parse literal hosts with ipaddress before
DNS. Apply the existing private/loopback/link-local/reserved/multicast policy to
IPv4 and bracketed IPv6 literals without resolver access. Preserve explicit
allow_private_ips=True and scheme/blocked-host behavior. Domain validation must
still reject any private answer, including mixed public/private IPv4/IPv6 results;
tests must stub resolver answers. Preserve the existing DNS-failure policy for
domain names; changing it, DNS pinning/rebinding, redirects, noncanonical numeric
hosts and broader Web redesign require separate authority. Test private IPv4,
link-local, IPv6 unique/link-local/multicast, public literals, overrides, mixed
resolver answers and Web reader rejection before transport. For literal tests,
patch getaddrinfo to raise if called; no real DNS or outbound transport. Retain
the existing guard and verify the pre-change regression fails. Remove no existing
security assertions or suppressions; introduce no new suppressions.

**R4-04 — PTY timing measurement.** Use a readiness marker after child imports and
synthetic runtime setup, then a parent-controlled trigger before action begins.
Start the existing 0.8-second acknowledgment budget at that trigger. Keep the
coordinator's one-second work delay, acknowledge before progress completion, and
retain all shutdown/ownership assertions. Readiness has its own finite bootstrap
timeout and diagnostic failure; no unbounded waits. Avoid a marker-only scheme
where action begins before the parent sees readiness. Bound subprocess cleanup
on every failure path and close inherited pipe/PTY descriptors. Run the test alone,
its whole module, and in both complete suites. This tests post-readiness application
acknowledgment and makes no cold-process startup performance claim. WVR-001 is not
used or extended.

**R4-05 — Synthetic listener environment.** Reconfirm all 11 exact nodes use only
temporary synthetic responses, fake clients and localhost ephemeral listeners.
Privileged here means escaping the binding-restricted sandbox with normal user
permissions; never sudo/admin rights. Approved A05 permits the complete root and
Chat+telemetry suite invocations below to execute in that environment solely to
allow those listeners. Freeze a fresh import/helper/subprocess safety preflight,
environment allowlist and source-resolution inventory before either invocation.
Keep non-loopback DNS/connect/sendto prohibition in every Python subprocess; no
credentials, live model flags, real application data or remote exporter activation.
All 11 nodes must pass as part of zero-exit complete suites; node reruns alone do
not convert a failed broad command into PASS. If the complete profile cannot be
approved/executed safely, report the missing gate; no infrastructure waiver is
proposed.

**R4-06 — Current-code lint and historical evidence.** Fix all 133 live findings
within the exact manifest. UTC and TimeoutError replacements must preserve values,
exception matching and cancellation behavior. Generic/alias changes require
manual call-site/runtime review; do not apply blanket unsafe fixes. Preserve
public import names, parameter/return contracts, variance, subscriptability,
Pydantic/schema and structured-memory completion behavior. PEP 695 type statements
create different runtime alias objects; a caller relying on old identity or
introspection is a stop condition requiring an explicit compatibility decision.
Run affected package contract tests and targeted type checks without adding broad
suppression or reducing Ruff rules/targets. If extra regression paths are needed,
freeze an exact amendment first. Keep the four archive files byte-identical.
[WVR-002](../validation/WVR-002-archived-probe-lint.md) covers only their exact
326 existing diagnostics. Root Ruff must still run unchanged and its nonzero raw
exit/count must be reported. Under the explicit WVR-002 approval, an exact match
of those 326 diagnostics and hashes, zero live findings and all other passing
checks satisfies that limited gate. Any other diagnostic remains a failure.

**R4-06b — Exact expanded-scope typing failures.** Independent proposal review
REM004-PR-F01 reproduced three errors over the 58 proposed source targets.
At the frozen baseline, `friday_chat/adapters.py:167` reassigns a legacy-inferred
ChatCompletionResponse variable to TypedChatCompletionResponse, and `:178` then
reports dict usage has no model_dump. `friday_memory/llm_completion.py:85` reuses
a typed-inferred response variable for a legacy ChatCompletionResponse. Both
files already belong to the 80-file lint scope. Scope additionally permits only
response local-variable/annotation separation and necessary public model imports
in FrameworkChatModel.complete and complete_memory_request, plus the bounded
response regressions in the existing two completion-test files named above.
Use separate branch-local response names or an explicit public response union
with correct narrowing; no cast workaround, Any erasure, suppression, changed
LLM interfaces, response coercion, request defaults or deprecation policy.

Preserve and verify both typed and legacy Chat request forwarding, content,
reasoning, model, tool calls, usage projection and raw response identity; preserve
both typed and legacy Memory content/reasoning projection, controls, structured
response-model validation and compatibility warning behavior. Use published
response models and synthetic clients. Cover absent/empty content, omitted typed
usage fields, invalid structured JSON/model data and unchanged exception propagation
in both branches; malformed structured output must not become a valid model.
Existing adequate coverage may be retained;
add only missing response-contract cases. Require zero exit from the exact
aggregate changed-source mypy command and record that the three baseline errors
are resolved without weakening configuration or other checks. A fourth typing
error or additional function/file is a stop condition for a precise amendment.
This typing component belongs to R4-06's acceptance criterion and sole
VAL-005-F01 mapping; no new waiver is proposed.

## Verification commands and execution profile

Use installed Python 3.13.10; retain >=3.13.4 metadata, all frozen dependency pins
and root py313 rules. No exact-floor interpreter download. Tests run from a new
tracked isolated candidate checkout under /private/tmp/telem-01/REM-004; do not
copy .env, .friday, transcript/Chroma databases or unrelated untracked files.
Before collection, audit changed tests and their imported helpers/subprocesses.
Use the same guard pinned in REM-004-diagnosis.md, never relax it for DNS tests.
Use the credential-free allowlist, UV_NO_SYNC=true, UV_OFFLINE=true,
UV_PYTHON_DOWNLOADS=never, UV_CACHE_DIR=/private/tmp/friday-uv-cache,
LITELLM_LOCAL_MODEL_COST_MAP=true, ANONYMIZED_TELEMETRY=False,
TERM=xterm-256color, temporary cache/state paths and PYTHONDONTWRITEBYTECODE=1.
Prepend guard, isolated */src paths, isolated Chat test helpers and checkout root
to PYTHONPATH. All nested uv/subprocess invocations inherit no-sync/offline/guard.

Run these exact broad commands after safety preflight, retaining both live-module
exclusions and no others; live flags remain absent in the full package command:

```text
uv run --no-sync pytest packages/friday-chat/tests_chat packages/friday-telemetry/tests_telemetry
uv run --no-sync pytest --import-mode=importlib --ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py --ignore=packages/friday-llm/tests_llm/test_live_lmstudio.py --collect-only
uv run --no-sync pytest --import-mode=importlib --ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py --ignore=packages/friday-llm/tests_llm/test_live_lmstudio.py
uv run --no-sync ruff check . --output-format json
uv lock --offline --check --no-python-downloads --no-build
uv run --no-sync python scripts/friday-dev-board.py validate
uv run --no-sync python scripts/check-documentation-lifecycle.py
git diff --check 686a5bd17d84fea3ec3a3d329df2d39c70d10c03 HEAD
git diff --check 2155a0fc51f5b20dea4e35c6cfc70f1d52002735 HEAD
```

Also run the unchanged six-module telemetry suite in CD-001, genuine synthetic
Chat observer/Composite lifecycle smoke, all package tests owning changed source,
the R4-01 order regression, and focused R4-02/03/04 checks. Expand changed-file
Ruff and `mypy --python-version 3.13` lists from the exact aggregate Git diff,
recording source/test lists before dispatch; syntax-check all changed Python
files with ast.parse(feature_version=(3,13)). Do not type-check an obsolete
six-file list after expanding product scope. Separate pre-existing typing debt
from new issues; any nonzero required changed-source check stops closure rather
than silently waiving it. Check aliases/generics with affected-package tests
and any needed explicit targeted consumer typing probes.

Reuse immutable preparation/base logs only as clearly labeled retrospective
baseline evidence. New diagnostic probes and candidate runs require commands,
revision, environment nonsecret values, guard/source hashes, exit status, totals,
failure/skip IDs and log hashes. Freeze exact expanded commands, source lists,
preflight, approved exception and authority hashes in the independent request.

## Closeout, review and stops

Commit a stable product candidate and dispatch a fresh-context read-only delta
plus aggregate review against the complete feature branch. Readiness is not
VERIFIED; VERIFIED is not maintainer acceptance. Preserve original and isolated
tracked files/runtime state via before/after manifests. Resolve VAL-005-F01 only
when all R4 criteria and aggregate AC-01 through AC-06 pass, including the exact
approved exact archival disposition. Keep work started until then.

Stop on additional files/diagnostics, new baseline failures, generic API drift,
dependency changes, failed mandatory checks, unsafe imports/subprocesses,
unavailable listener authority, guard mismatch, unauthorized effects, or conflict
with accepted contracts. Do not repair a newly discovered defect opportunistically.
After two unsuccessful new remediation cycles, return unresolved findings to the
maintainer. No push, merge, acceptance, live provider, exporter, image, deployment
or publication authority is supplied. TELEM-02 through TELEM-05 remain deferred.
