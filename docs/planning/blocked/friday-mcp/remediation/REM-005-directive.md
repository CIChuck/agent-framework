# REM-005 — MCP-WS-03 Safe Collision Source Diagnostics

Status: Draft; awaiting explicit maintainer approval before product edits or remediator dispatch
Date: 2026-09-28
Initiative: `friday-mcp`
Work unit: `MCP-WS-03`
Finding: [VAL-008 F-001](../validation/VAL-008-report.md#f-001--medium-collision-diagnostics-do-not-identify-the-colliding-sources)
Reviewed candidate: `397caa9898612cd989f6404951b3e1f5005dfac2`
Work-unit base: `2c0d6bd1fe481fff9bb180f9e6dfb4a9a2131641`
Approval/start revision: `b54069654bb3e21a6265fbabcd23f6991e286ab0`
Accepted predecessor: `a257f041d1d68f8aea2f5b9773df1b88acd82379`
Branch: `feature/friday-mcp-ws03-registry`

## Authority And Role

Repository engineering, development-lifecycle and independent-validation
policies, the approved [WS-03 directive](../directives/ws-03-tool-naming-metadata-registry.md),
its accepted predecessor authority, and the complete
[VAL-008 report](../validation/VAL-008-report.md) control this correction.
The unchanged [request](../validation/VAL-008-request.yaml) pins the twenty
authority hashes at the reviewed candidate. The original active paths remain
the Git paths at that revision; the blocked prefix identifies current working
content only.

VAL-008 is a completed fresh-context, read-only aggregate review with overall
`CHANGES_REQUESTED`, not a capacity block or an acceptance decision. Its sole
finding is the missing safe source information for fatal runtime collisions.
This draft converts that finding into one bounded remediation scope. The
maintainer's "Proceed to the next step" authorizes recording the result and
preparing this directive; it does not approve an as-yet-unreviewed directive
or waive the original review-only no-fixes boundary.

Use a separate remediator under the independent-validation policy because this
correction changes a public typed diagnostic contract at an untrusted-content
boundary. The original builder and VAL-008 reviewer must not silently repair
the candidate. A remediator must not validate its resulting work. No remediator
is dispatched by preparation of this draft.

After approval, record authorization and start, clear the approval condition
and reconcile packet location/backlinks through controller metadata, then
dispatch the separate remediator. Implement only the finding below, commit a
new stable candidate and obtain a new fresh-context read-only delta review
followed by the complete WS-03 work-unit aggregate review. Reserve `VAL-009`
for that review; no request, dispatch or verdict exists yet. The full
feature-branch pre-merge review remains separate. This is the first WS-03
remediation cycle; after two unsuccessful cycles, return unresolved findings
to the maintainer rather than launching an automatic correction loop.

## VAL-008 F-001 — Medium: Retain Both Safe Collision Source Descriptors

The public runtime currently returns the same static error and one second-source
`MCPRegistrationDecision` for peer/peer and MCP/native collisions. A set of
canonical names discards the first contender; no provider label or bounded
original-name shape/fingerprint remains inspectable after cleanup. This
violates approved MCP-03-02 and MCP-03-AC-02 even though abort/no-overwrite and
public cleanup pass. The unchanged report contains exact public-kernel
reproduction, risks, command exits and baseline separation. Archived
[evidence](../validation/VAL-008-evidence.yaml) preserves the executable probes
and logs without altering the reviewer report.

Required correction:

- Keep a typed safe descriptor for the first contender and construct one for
  the second. Publish both in an additive typed collision record attached to
  registration decisions or an equivalent documented public provider surface.
  Preserve existing decision constructors and ordinary binding reasons with
  backward-compatible defaults; do not change mandatory native protocols.
- Each collision record identifies the canonical name, first/second provider
  kind (`mcp` or `native`), and configured safe server IDs for MCP contenders.
  Native entries have an explicit native label and no invented MCP server ID.
  Identify untrusted original MCP names with bounded length/shape/fingerprint
  summaries. Distinct lossy originals on the same peer must be distinguishable.
  Do not retain or echo raw originals in the new public diagnostic, exceptions,
  repr or logs. Define and test the exact bounded summary representation.
- Use only the existing accepted normalizer and public native-registry APIs.
  Do not import private core helpers, inspect native `_tools`, expose arbitrary
  peer dictionaries, add dependencies, or copy source names into free-form
  exception text. Native source identity can use its canonical registry name;
  no introspection of native tool internals is needed.
- Retain the bounded collision evidence through failed-startup cleanup on the
  provider reachable via `RuntimeKernel.mcp_provider`. Document its lifetime
  and what a subsequent attempt replaces. Successful cleanup must not erase
  the evidence needed to diagnose the failed attempt.
- Preserve fatal pre-filter collision checking for optional peers, zero default
  selection, selected mode and exclusions, with no overwrite or MCP insertion.
  Preserve ordinary counters and explain fatal-preflight counts without
  inventing a new rejected-count or both-contenders-count requirement.
- Preserve owned rollback, native identity, public cleanup/retry, successful
  peer draining, registration-before-bindings, no rediscovery/backfill, final
  export caps, sanitation and all REM-003/004 lifecycle behavior. This is a
  diagnostic correction, not an ownership or transport redesign.
- Document the public additive types, compatibility/defaults, privacy bounds,
  retention semantics, counter interpretation, exact before/after evidence,
  command results and remaining gates in the bounded implementation reports.

## Exact Allowed Files After Approval

The remediator's product/test/report edits are limited to these eight paths:

1. `packages/friday-runtime/src/friday_runtime/mcp_registration.py`
2. `packages/friday-runtime/src/friday_runtime/mcp_loading.py`
3. `packages/friday-runtime/tests_runtime/test_mcp_registration.py`
4. `packages/friday-runtime/tests_runtime/test_mcp_loading.py`
5. `tests/integration/test_mcp_registry.py`
6. `tests/integration/mcp_fake_server.py` — bounded collision catalog variants
   only; preserve all existing noisy/lifecycle modes.
7. `docs/planning/blocked/friday-mcp/execution/REM-005-implementation-report.md`
8. `docs/planning/blocked/friday-mcp/execution/WS-03-implementation-report.md`
   — a bounded diagnostic/API and criterion-evidence correction.

If the controller relocates the packet after approval, only the two report
prefixes above map to the new active packet. This does not broaden source/test
scope. The controller owns board/dashboard/index/log/queue, approval records,
review requests, unchanged historical reports and their evidence/status notes.
No core DTO/normalizer/native registry, adapter, DI/kernel/tool-loader, manager,
base/stdio transport, configuration, dependency, broader test or authority
edit is authorized. Stop before expanding these exact eight targets.

## Regression And Acceptance Criteria

- `REM-005-AC-01`: Unit and real public-runtime peer/peer collisions retain
  both bounded source descriptors. `Read.File` and `Read-File` on one server
  are distinguishable; cross-peer normalized ambiguity retains both safe
  configured server identities and original-name summaries.
- `REM-005-AC-02`: MCP/native collisions distinguish the native and MCP
  contenders through the public typed surface. Both peer/peer and MCP/native
  variants abort before insertion, preserve every native object and complete
  public cleanup. Their diagnostics are observably different.
- `REM-005-AC-03`: Optional servers, default-zero and selected modes, and
  exclusions cannot conceal either collision class. Evidence survives cleanup
  on the publicly reachable provider; public repeated stop/start/retry remains
  sound and diagnostic replacement semantics are documented/tested.
- `REM-005-AC-04`: Diagnostic size is bounded for oversized/encoded/control/
  sentinel originals admitted to preflight. Shape/length/fingerprints distinguish
  sources without raw peer names, catalog text, exception details, arguments or
  environment values in public errors, repr, decisions or captured DEBUG logs.
  Preserve the existing handoff/normalization/schema limits; no unbounded scan
  or weaker rejection is introduced.
- `REM-005-AC-05`: Existing decision construction and binding reasons remain
  compatible. Ordinary discovery/filter/selection/registration counters do not
  regress; fatal-preflight interpretation is documented without a new counting
  contract. Final export caps, exact callable routing, sidecar integrity,
  transaction/rollback refusal and all retained-owner/noisy/cancellation
  regressions continue to pass.
- `REM-005-AC-06`: Exact eight-path boundary, meaningful source typing, no broad
  ignores, native protocol/config/dependency changes or private reach-through;
  accurate public contract/migration and criterion/check reports. VAL-008's
  existing baseline failures remain explicit and unchanged.

Use deterministic local doubles and bounded local stdio fake peers only.
Assert successful public cleanup before defensive fixture cleanup; explicitly
settle tasks, kill/drain/reap synthetic processes in `finally`, including failed
assertions. Preserve production cleanup budgets. VAL-008's scratch detector and
resource observations do not define a new shutdown SLA.

## Required Checks And Fresh Review

All uv commands use `UV_CACHE_DIR=/private/tmp/friday-uv-cache`; tests/imports
also use `LITELLM_LOCAL_MODEL_COST_MAP=true`. Required checks are the complete
fourteen implementation checks from the approved WS-03 directive:

```text
uv run pytest packages/friday-core/tests_core/test_mcp_contracts.py packages/friday-mcp/tests_mcp/client/test_adapter.py packages/friday-runtime/tests_runtime/test_mcp_registration.py packages/friday-agent/tests_agent/test_registry.py tests/integration/test_mcp_registry.py -q
uv run pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime packages/friday-agent/tests_agent/test_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/test_mcp_registry.py -q
uv run pytest packages/friday-tools/tests_tools -q
uv run pytest packages/friday-chat/tests_chat/test_mcp_config_compatibility.py packages/friday-chat/tests_chat/compat/test_config_compatibility.py packages/friday-chat/tests_chat/test_llm_config_migration.py -q
uv run pytest tests/integration -q --tb=short
uv run ruff check packages/friday-core/src/friday_core/mcp.py packages/friday-core/tests_core/test_mcp_contracts.py packages/friday-mcp packages/friday-runtime tests/integration/test_mcp_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py
uv run mypy packages/friday-core packages/friday-runtime packages/friday-mcp
uv run mypy --python-version 3.13 packages/friday-core/src/friday_core/mcp.py
uv run mypy --python-version 3.13 packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py
uv run mypy --python-version 3.13 packages/friday-core/src/friday_core/mcp.py packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py
uv run python scripts/friday-dev-board.py validate
uv run python scripts/friday-dev-board.py render --check
uv run python scripts/check-documentation-lifecycle.py
git diff --check
```

After freezing the replacement candidate, the controller additionally requires
whitespace checking on the exact delta and complete WS-03 aggregate ranges,
and `git diff --exit-code <new-candidate> -- packages tests pyproject.toml uv.lock`.
Pin the approved REM-005 revision/hash with the WS-03 authority manifest, exact
delta base/new candidate and original work-unit base. Fresh VAL-009 must
independently review all six remediation criteria, all ten WS-03 criteria,
required checks and interactions with accepted WS-00/01/02. It must independently
reproduce both public collision variants and their safe retained descriptors,
not rely only on candidate tests or builder claims.

VAL-008 independently reproduces unchanged NumPy/default-target syntax,
four `profiles.py` Python 3.13 errors, board count 22 versus 23, and the native
DOCX/XLSX invalid-zip assertions on accepted predecessor inputs. Retain exact
failures and meaningful narrow typing evidence; do not repair/waive them,
change dependencies/import paths to conceal them, or classify a new touched-file
failure as legacy. No favorable result or acceptance is promised by this draft.

## Non-Goals And Stops

No schema dialect/filter/cap/normalizer redesign, whole-registry immutability,
argument-hash storage, Chat turns/budgeting, output/provenance, memory/transcript,
telemetry, CLI, remote transports, live services, credentials, paid calls,
refresh, external includes, opportunistic refactor or workspace cleanup. No
push, merge, release, deployment or other external effect.

Stop before product edits or dispatch until the complete directive and separate
remediator are approved. Stop for candidate/authority drift, loss of accepted
predecessor evidence, additional numbered findings, need for files outside the
allowlist, mandatory protocol/config/signature changes, unsafe raw diagnostics,
private boundary access, broader lifecycle work or missing fresh-review
capacity. Report the exact decision required. Preserve unrelated `.DS_Store`,
deleted `family-tree.md`, `docker-bench-security/`, Friday Chat config backup
and sandbox Dockerfile audit; stage only explicitly named task paths.

Initiative remains `started` and local. VAL-008 remains historical evidence for
its frozen candidate; only after a replacement candidate exists may the
controller mark it superseded for current decisions in a separate status record.
Do not amend the independent report. WS-03 closeout needs independent VERIFIED,
WS-03 acceptance needs an explicit maintainer decision, and later workstreams
retain their separate approval gates.
