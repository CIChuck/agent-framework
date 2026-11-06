# MCP upgrade tactical plan

Status: Approved by Chuck Russell on 2026-10-12 for preparation and CD-MCP-UP-001.

## Ordered slices

| Slice | Deliverable | Construction authority |
| --- | --- | --- |
| UP-01 | Current baseline, compatibility/SDK decision, contract, first directive and check profile | Planning only, prepared 2026-10-12 |
| UP-02A | Modern client core, bounded catalog/results and explicit modern/auto stdio modes | Approved [CD-MCP-UP-001](directives/CD-MCP-UP-001-client-core.md) |
| UP-02B | Streamable HTTP client and explicit 2025-11-25 compatibility | Later exact directive; no source authority yet |
| UP-03 | Remote policy/contracts and config.yaml to headless runtime/real Chat | Later exact directive; preserve accepted security and registry decisions |
| UP-04 | Result/refresh hardening and selected optional interactions | Later exact directive; no implicit subscription or interactive capability |
| UP-05 | Modern tools-only server stdio/HTTP interoperability | Later exact directive; no live server publication |
| UP-06 | Migration docs and full initiative aggregate verification/acceptance proposal | Later bounded closeout |

Moving pagination and basic structured-result disposition into UP-02A ensures
the first modern tool call cannot silently drop results or expose half a catalog.
HTTP follows immediately after the core is independently verified; remote YAML
admission follows the transport's protocol proof and exact remote safety policy.

## Execution preparation after approval

Commit approved controls and board state, recording the exact maintainer
decision. Create `feature/friday-mcp-protocol-upgrade` from the inspected accepted
baseline plus planning/approval commits. Use an isolated worktree/snapshot;
retain the original mixed checkout and its uncommitted files. Move the packet to
active, repair relative links, record `started/granted` and the named branch,
render/validate/show the board, and hash the active controls again. Do not build
on an uncommitted or mismatched controlling packet.

A documentation-only snapshot preceding source work may contain the approved
MCP/Langfuse queue additions; it must not fold unrelated continuity planning,
local state, user config edits or audit assets into this initiative. Do not
stash/reset/clean to solve checkout preparation. Isolated validation snapshots
omit tracked credential/runtime-state files before checkout; retain a manifest
of omitted path names, without reading their contents.

Resolve/install the exact dev counterpart and declared validation dependency in
private caches/virtualenvs. Registry access, if needed after directive approval,
is limited to PyPI/files.pythonhosted.org artifact resolution/download; retain
hashes and an exact lock delta. Stop on unrelated existing-version churn or
incompatible Python/dependency constraints. Do not sync all extras or install
anything in the user's shared environment during preparation.

## Verification profile for UP-02A

Commands run from the isolated candidate with Python >=3.13.4, locked dependencies,
private cache/temp directories and telemetry/exporters disabled. Use `uv run
--offline --no-sync` after dependencies are frozen. No source suppression or
global lint/type setting weakening is authorized.

1. `python scripts/friday-dev-board.py validate`, `next`, and `show friday-mcp-protocol-upgrade`.
2. `pytest packages/friday-mcp/tests_mcp/client/test_modern_protocol.py packages/friday-mcp/tests_mcp/client/test_stdio_interop.py packages/friday-mcp/tests_mcp/client/test_execution.py packages/friday-mcp/tests_mcp/client/test_lifecycle.py`.
3. `pytest packages/friday-mcp/tests_mcp`.
4. `pytest packages/friday-runtime/tests_runtime packages/friday-chat/tests_chat packages/friday-telemetry/tests_telemetry`.
5. `ruff check packages/friday-mcp/src/friday_mcp/client/base.py packages/friday-mcp/src/friday_mcp/client/stdio.py packages/friday-mcp/src/friday_mcp/client/protocol.py packages/friday-mcp/tests_mcp/client/test_modern_protocol.py packages/friday-mcp/tests_mcp/client/test_stdio_interop.py packages/friday-mcp/tests_mcp/client/test_execution.py packages/friday-mcp/tests_mcp/client/test_lifecycle.py packages/friday-mcp/tests_mcp/fixtures/modern_sdk_server.py packages/friday-mcp/tests_mcp/fixtures/legacy_protocol_server.py`.
6. `mypy packages/friday-mcp/src/friday_mcp/client/base.py packages/friday-mcp/src/friday_mcp/client/stdio.py packages/friday-mcp/src/friday_mcp/client/protocol.py` and `mypy packages/friday-mcp/src/friday_mcp`.
7. `ruff check . --output-format=json` and `pytest` for the full workspace aggregate, including accepted MCP and telemetry regressions.
8. `python scripts/check-documentation-lifecycle.py`, `git diff --check` and exact manifest/authority preservation checks.

Commands 2-6 must pass, including focused test/fixture lint. Raw root Ruff is
reported even if inherited debt remains; reproduce the baseline in a sibling
snapshot using the same checker/version and compare exact path/code/location
identities. Any new finding blocks completion. Existing suppression-bearing
modules outside the directive remain baseline debt, not newly approved practice.
Root pytest must pass with only independently reproduced existing skips.
Infrastructure failure or a new aggregate failure is not an acceptable skip.

These future commands are requirements, not results from this preparation.
Only current planning checks and the two existing source-file lint/type baselines
are reported in [baseline.json](baseline.json).

## Permitted fixture effects under the approved first directive

Use synthetic catalogs/results and local asyncio fake transports. Real stdio
interop spawns only the isolated Python interpreter with the two named fixture
scripts: modern official SDK server and deterministic legacy JSON-RPC peer.
No npx/npm downloads, shell commands, user tools, model providers, paid services,
DNS/TCP or external MCP endpoints. Children inherit an allowlisted test environment,
private cwd/temp/cache, no credentials, and no live telemetry. Assert process
exit/task cleanup on success, partial start, timeout, cancellation and EOF.

Existing broad regression fixtures may use fixture-only 127.0.0.1 ephemeral
HTTP listeners and isolated local filesystem stores. Inventory these effects
before executing broad checks; block all non-loopback network connections and
provider/exporter activations. The frozen review request lists exact fixture
entry points and guard hashes. Unexpected effects stop execution; this profile
does not authorize a real Friday service, user workspace writes or credential reads.

## Independent candidate gate

Builder commits a stable exact-scope candidate and implementation report. Controller
freezes authority hashes, base/candidate commits, every acceptance criterion,
check commands, counterpart lock/artifact hashes and permitted effects. Dispatch
the policy-required fresh-context read-only validator; include full original
unit scope and regressions, not only the last changed lines. Changed product or
controls invalidate the verdict. Any remediation must be bounded by findings
and existing authority; request new scope only when the repair exceeds it.
