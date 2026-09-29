# MCP WS-05 Implementation Report

Date: 2026-09-28
Status: Stable implementation candidate; fresh independent VAL-011 and maintainer acceptance pending
Branch: `feature/friday-mcp-ws05-execution`
Work-unit base: `a609f948fe2d869ac29d0cce29d22d9334cd7d08`
Approval/start commit: `5e86df832a311a62509fb0838f6c45b6ecd6fdfa`
Accepted predecessor product: `53d76d45cedea16122436e53b178de074c5bc322`
Authority: [approved WS-05 directive](../directives/ws-05-execution-provenance-transcript.md)
Candidate: the immutable commit containing this report, pinned in `validation/VAL-011-request.yaml`; no self-referential hash is inserted into this frozen report.

The approved Chat consumer boundary now returns checked, escaped, bounded MCP
text with atomic typed per-call facts and empty captured arguments. Protocol
errors cannot masquerade as successful tool results. Streaming and ordinary
turns send the same safe request/result copies to model continuation and transcript
capture. This builder report does not supply independent verification or acceptance.

## Exact Deliverables

Exactly 23 approved implementation paths changed; no other product or test path
was authorized. Approval/start/controller artifacts are separate process records.

- `packages/friday-core/src/friday_core/mcp.py`
- `packages/friday-mcp/src/friday_mcp/client/base.py`
- `packages/friday-chat/src/friday_chat/tools/schemas.py`
- `packages/friday-chat/src/friday_chat/tools/loop.py`
- `packages/friday-chat/src/friday_chat/tools/mcp.py`
- `packages/friday-chat/src/friday_chat/tools/output.py`
- `packages/friday-chat/src/friday_chat/turns/processor.py`
- `packages/friday-chat/src/friday_chat/adapters.py`
- `packages/friday-transcript/src/friday_transcript/models/transcript.py`
- `packages/friday-transcript/src/friday_transcript/exporters/jsonl.py`
- `packages/friday-transcript/src/friday_transcript/exporters/markdown.py`
- `packages/friday-transcript/src/friday_transcript/exporters/csv.py`
- `packages/friday-transcript/pyproject.toml`
- `uv.lock`
- `packages/friday-core/tests_core/test_mcp_contracts.py`
- `packages/friday-mcp/tests_mcp/client/test_execution.py`
- `packages/friday-chat/tests_chat/test_mcp_execution_security.py`
- `packages/friday-chat/tests_chat/test_mcp_execution_transcript.py`
- `packages/friday-chat/tests_chat/test_mcp_chat_bridge.py`
- `packages/friday-transcript/tests/test_mcp_provenance.py`
- `tests/integration/test_mcp_execution_provenance.py`
- `packages/friday-chat/tests_chat/fixtures/mcp_execution_peer.py`
- `docs/planning/active/friday-mcp/execution/WS-05-implementation-report.md`

## Public Contracts And Execution Behavior

Core's existing `MCPToolCallProvenance` gains optional nonnegative original decoded
text and final model-facing UTF-8 byte sizes, and five fixed failure codes.
Contradictory success/rejection/failure states are explicitly rejected. Unknown
original sizes remain absent. Existing payloads still validate. Chat's immutable
four-field `ToolCallRecord` gains a final optional typed provenance field; native
and fake registries retain the original `call_tool -> str` boundary.

The optional public recording protocol returns an atomic record. The public MCP
Chat bridge's ordinary `call_tool` uses exactly that checked path. Each invocation
snapshots accepted public metadata before awaiting execution, routes the original
name and argument object to the existing manager, and records provider/server,
original/canonical names, transport, schema/trust facts and call ID without a
parallel metadata authority or private manager lookup. Direct and concurrent
calls do not share mutable raw result caches.

MCP call IDs preserve valid unique safe identifiers and replace invalid, missing
or reused IDs with opaque UUID-based identifiers. Native IDs are reserved before
MCP allocation in mixed responses and remain unchanged. A shared per-turn set
retains uniqueness across loop iterations; paired transcript calls/results must
have equal facts and exactly one coherent ID association. Actual transcript entry
IDs are assigned by the production adapter and validated on persisted loads.

MCP argument values and keys are passed unchanged to execution, then replaced
with `{}` in returned records, continuation assistant requests, pending/fallback
responses, raw/context capture and persistence. MCP request prose/reasoning and
extra serialized fields are dropped. User messages and native-only records remain
compatible. Accepted MCP names are snapshotted before memory retrieval so a
concurrent public shutdown cannot remove capture policy. Known literal, JSON
escaped and normalized argument echoes in retained result text are removed,
including partial long echoed arguments at the initial byte cut. These transient
removal tokens and argument normalizer results are never persisted or cached.
This is not semantic classification of arbitrary secrets or transformed echoes.

The consumer explicitly enables public Core normalization and high-sensitivity
injection detection with capacities above the retained prefix, uses block/drop,
disables detection logging/raw quarantine, and owns a complete escaped
`untrusted_content` envelope. All retained decoded text is normalized/scanned
before model entry. The argument-token-only normalizer disables detection solely
for transient removal tokens; it never supplies model output or a safety verdict.
Final UTF-8 limits include complete wrapper, escaping, truncation notice and
static failure text. Truncation preserves complete Unicode characters and HTML
entities. Original decoded text byte counts exclude JSON/JSON-RPC escaping.
A cap too small for a complete safe result raises a static safe exception before
RPC; TurnProcessor exposes a safe TurnProcessingError and invents no attempted
call record. Byte limits bound returned text, not peer/wire allocation or exact
token budgets.

Base MCP client interprets `isError=True` and invalid flag/content structures with
safe fixed typed errors. Chat converts tool/protocol/transport/timeout failures
into bounded failed records, and unsafe output into blocked records. No raw
exception, peer content, arguments, env/header values or sanitizer detection
sample/repr is copied into those records or logs. Cancellation propagates through
the existing owner; public cleanup and later restart remain available. The
existing lower-level Runtime/native registry APIs are outside this Chat policy.

## Transcript, Exports, Dependencies And Migration

Both real and fake transcript adapters receive safe records. The production
adapter validates bound/checked/correlated facts before storage and assigns the
actual entry ID. Transcript call/result fields use the one public Core DTO with
safe validation errors, including JSON list-to-tuple round-trips under the shared
strict contract. Entry validation rejects unpaired, duplicate or contradictory
MCP correlations. Existing SQLite JSON storage requires no schema migration.
Optional MCP fields are omitted when absent, preserving old/native serialization.
Four touched Transcript model/exporter files lose broad mypy ignores and now pass
meaningful typing without a blanket suppression.

JSONL with metadata enabled preserves full structured provenance; the existing
metadata-disabled privacy flag still omits tool metadata. Markdown still defaults
`include_tool_calls=False`; opt-in MCP cells use bounded escaped safe summaries.
CSV retains columns/default tool cells, using bounded JSON summaries and checked
text for MCP cells. Human summaries include safe server/canonical name, call ID,
status, sanitization/truncation and sizes, escape markup/control characters and
omit original raw peer names. Full original names remain in typed JSONL. Legacy
native export cells remain compatible. WS-08 should document this decision.

Transcript declares `friday-framework-core==0.1.0a2`. Its lockfile changes are
exactly the two Core dependency-edge entries; no third-party upgrade, root metadata
change, reverse dependency, storage migration or new config/command occurs.
Cached offline build tools produced Telemetry/Core/Transcript wheels, checked
actual Transcript Requires-Dist metadata, and tested public imports/typed JSON
round-trips with `python -S` and extracted wheels without editable .pth hooks.
Third-party dependencies came from the existing environment. This is a declared
package/import check, not a new clean-environment network installation.

## Tactical Task And Criterion Evidence

| Task | Implemented behavior and verification |
| --- | --- |
| MCP-05-01 | Additive public Core DTO and atomic Chat record; contract and bridge tests. |
| MCP-05-02 | Full argument redaction with no hashes; direct/loop/real turn/fake/SQLite/raw capture/export sentinel tests. |
| MCP-05-03 | Final UTF-8 cap includes all envelope overhead; exact/large/multibyte/tiny cap tests. |
| MCP-05-04 | Explicit normalize/detect/block/drop; high-offset attacks, envelope escape and no raw retention tests. |
| MCP-05-05 | Distinct per-call metadata and opaque IDs; mixed/repeated/multiple/concurrent and across-iteration tests. |
| MCP-05-06 | Safe production persistence and actual entry correlation; typed JSONL/SQLite round-trip and old/native tests. |
| MCP-05-07 | Existing JSONL metadata flag, Markdown opt-in and CSV columns; bounded escaped summaries tested. |
| MCP-05-08 | Fixed error/invalid/timeout/blocked facts, cancellation/restart and no peer exception retention tests. |

| Criterion | Builder evidence; independent assessment remains pending |
| --- | --- |
| WS05-AC01 | Core contract tests; native positional record; lock check and wheel metadata/isolated import. |
| WS05-AC02 | Real original route/argument capture, echo/error/env/header sentinels, both turn modes and all capture/export paths. |
| WS05-AC03 | Cap matrix 100/128/256/65536/300000, full overhead, UTF-8/exact/empty/tiny cap and public execution tests. |
| WS05-AC04 | Unsafe high-offset normalized attacks, envelope escaping, static blocked output and no logs/quarantine/raw DTO samples. |
| WS05-AC05 | Real local peer error/bad flags/content/RPC/EOF/timeout plus client doubles, cancellation/public stop/restart. |
| WS05-AC06 | Distinct two-peer facts, repeated tool names, unsafe/duplicate/missing IDs, concurrency and loop iteration tests. |
| WS05-AC07 | Production SQLite and fake captures; negative adapter/entry correlation tests and legacy native compatibility. |
| WS05-AC08 | Full typed JSONL/privacy flag, escaped bounded Markdown and CSV/control/markup tests. |
| WS05-AC09 | Existing parity/selection/budget suites and broad Agent/Core/MCP/Runtime/Memory; frozen source outside exact scope. |
| WS05-AC10 | Complete commands below, synthetic real-peer UAT, package checks and 30 input/956 outside-scope/five unrelated fingerprint checks. |

The local stdio peer covers benign text, UTF-8 output larger than the selected
consumer cap, injected output, isError, malformed flags/content, RPC failure,
hang, exit and argument echo. The large fixture remains below the accepted
64-KiB transport line limit; no transport limit change is implied. Public Chat
bridge/ToolLoop/real TurnProcessor, streaming/non-streaming continuation, fallback,
raw capture, production SQLite and exporters are exercised with synthetic data.
Two peer processes and repeated same-name calls verify association. Fixture
finally blocks defensively drain/kill/reap children and settle tasks on failures;
public cleanup state is asserted separately. No live model/service, credential,
paid provider, external telemetry, delivery or dedicated MCP ingestion is used.
Ordinary conversation-memory writes retain existing semantics.

## Complete Verification Commands

All final commands used the existing workspace environment with
`LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache
UV_NO_SYNC=true UV_OFFLINE=true PYTHONDONTWRITEBYTECODE=1`.
`UV_NO_SYNC` avoids an unavailable index build during uv's editable sync; it does
not skip checks. Commands, env, exits and full stdout/stderr are losslessly archived
in [builder evidence](WS-05-builder-evidence.yaml), with reproducible harnesses.

1. `uv run pytest packages/friday-core/tests_core/test_mcp_contracts.py packages/friday-mcp/tests_mcp/client/test_execution.py packages/friday-chat/tests_chat/test_mcp_execution_security.py packages/friday-chat/tests_chat/test_mcp_execution_transcript.py packages/friday-chat/tests_chat/test_mcp_chat_bridge.py packages/friday-transcript/tests/test_mcp_provenance.py tests/integration/test_mcp_execution_provenance.py packages/friday-chat/tests_chat/compat/test_tool_loop_parity.py packages/friday-chat/tests_chat/compat/test_turn_contract_parity.py packages/friday-chat/tests_chat/test_turn_processing.py packages/friday-chat/tests_chat/test_transcript_production_commands.py packages/friday-chat/tests_chat/test_transcript_export_commands.py -q --tb=short` — exit 0. 201 passed.

2. `uv run pytest packages/friday-chat/tests_chat -q --tb=short` — exit 1. 548 passed, 5 skipped; one unchanged PTY failure and three blocked localhost fixture errors.

3. `uv run pytest packages/friday-transcript/tests -q --tb=short` — exit 0. 34 passed.

4. `uv run pytest packages/friday-agent/tests_agent -q --tb=short` — exit 0. 209 passed; 10 existing deprecation warnings.

5. `uv run pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime -q --tb=short` — exit 0. 416 passed.

6. `uv run pytest packages/friday-memory/tests_memory -q --tb=short` — exit 0. 680 passed, 1 skipped; existing warning.

7. `uv run pytest tests/integration -q --tb=short` — exit 1. 73 passed; unchanged board-count assertion fails.

8. `uv run ruff check packages/friday-core packages/friday-mcp packages/friday-chat packages/friday-transcript packages/friday-agent tests/integration/test_mcp_execution_provenance.py` — exit 0. All checks passed.

9. `uv run mypy packages/friday-core packages/friday-mcp packages/friday-chat packages/friday-transcript packages/friday-agent` — exit 2. NumPy __init__.pyi:737 Python-3.10 type-statement syntax stops project checking.

10. `uv run mypy --python-version 3.13 packages/friday-core/src/friday_core/mcp.py packages/friday-mcp/src/friday_mcp/client/base.py packages/friday-chat/src/friday_chat/tools/schemas.py packages/friday-chat/src/friday_chat/tools/loop.py packages/friday-chat/src/friday_chat/tools/mcp.py packages/friday-chat/src/friday_chat/tools/output.py packages/friday-chat/src/friday_chat/turns/processor.py packages/friday-chat/src/friday_chat/adapters.py packages/friday-transcript/src/friday_transcript/models/transcript.py packages/friday-transcript/src/friday_transcript/exporters/jsonl.py packages/friday-transcript/src/friday_transcript/exporters/markdown.py packages/friday-transcript/src/friday_transcript/exporters/csv.py` — exit 0. Success: no issues in all 12 changed source files, unfiltered.

11. `uv lock --check --offline` — exit 0. 208 packages resolve; lock current.

12. `uv run python scripts/friday-dev-board.py validate` — exit 0. 23 tasks valid.

13. `uv run python scripts/friday-dev-board.py render --check` — exit 0. Dashboard current.

14. `uv run python scripts/check-documentation-lifecycle.py` — exit 0. 349 Markdown files checked before adding this report/request.

15. `git diff --check (working implementation); frozen aggregate command recorded separately after candidate commit` — exit 0. No whitespace errors.

## Independently Reproduced Builder Baselines And Setup Gaps

Builder baseline reproduction uses a Git archive of approved base `a609f94` in
scratch, the existing environment's Python, and PYTHONPATH containing only that
archive's package source directories, with local cost-map and bytecode-off flags.
The exact harness/commands/env and complete outputs are in archive `baseline/`.
This is builder baseline evidence; the fresh validator must reproduce it itself.

- Full predecessor Chat: exit 1, 479 passed, 5 skipped, the same PTY assertion
  failure and the same three localhost bind PermissionError fixture errors.
- Full predecessor integration: exit 1, 68 passed, same 22-versus-23 board assertion,
  plus an archive-only missing-Git-catalog documentation harness failure.
  Supplying a read-only Git catalog and existing UV environment/cache fixed the
  targeted predecessor documentation test: exit 0, one passed. An intermediate
  retry lacked UV_CACHE_DIR and failed cache permissions; this is also preserved
  as harness evidence, not a product failure or approved waiver.
- Default predecessor five-package mypy: exit 2, same NumPy syntax error.
  Predecessor Python-3.13 typing on the eleven pre-existing changed source paths:
  exit 0. The historical four Core profiles errors were not reproduced here and
  are not claimed as present or used to excuse changed-source errors.

The failed PTY/HTTP/board tests and root Python typing configuration are unchanged
against the base. New focused tests, all affected-source typing and package/import
checks pass. Broad nonzero gates remain explicitly reported; no baseline test or
out-of-scope source was repaired or error output filtered.

Initial offline full lock resolution failed because cached litellm metadata was
unavailable; only the approved two-edge lock update was made, then lock --check
passed. Initial frozen uv execution attempted editable Transcript synchronization
and failed uncached hatchling/network access; later no-sync offline runs and
cached no-isolation wheel builds succeeded. Earlier focused runs caught fixture
setup/oversized-wire/expected-escaping mistakes and JSON strict tuple loading;
all original logs remain archived and the final 201-case run follows the fixes.
No unresolved changed-source/type/test failure is concealed by those early runs.

## Preservation, Freeze And Remaining Gates

Before freeze, all 30 pinned accepted authority/report plus approved directive
hashes match; 956 tracked product/config files outside the approved manifest match
the approved base. Only 22 product/test/metadata paths plus this report comprise
the 23 deliverables. The exact five unrelated path fingerprints remain unchanged:
`.DS_Store`, deleted `family-tree.md`, `docker-bench-security/`, the Chat config
backup and sandbox `Dockerfile.audit`. No broad staging, cleanup, user database,
secret or cache state enters the candidate.

The controller pins the full candidate, complete approved-base aggregate diff,
authority/report hashes and tracked product bytes in VAL-011. Frozen aggregate
whitespace and start/closeout preservation checks supplement the commands above.
Fresh read-only independent complete aggregate review is required before proposing
closeout. A changed candidate or authority requires a new review. No automatic
security/package remediation is preauthorized. Maintainer WS-05 acceptance is
still required after VERIFIED. WS-06 memory compatibility/ingestion, WS-07
telemetry/diagnostics/health and WS-08 documentation/initiative aggregate closeout
remain separately scoped and approved gates. Push/merge/release/live UAT and
optional later capabilities are not authorized by this work unit.
