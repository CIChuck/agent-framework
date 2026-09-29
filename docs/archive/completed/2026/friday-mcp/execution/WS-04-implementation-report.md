# MCP WS-04 Implementation Report

Date: 2026-09-28
Status: Implementation candidate; fresh independent VAL-010 and acceptance pending
Branch: `feature/friday-mcp-ws04-chat-budget`
Work-unit base: `acd1fd1e736a38134fac40d7fdb35cd1f32cf683`
Approval/start authority commit: `ac4530ac8063f299776c807cfa22140e3cff184a`
Authority: [approved WS-04 directive](../directives/ws-04-friday-chat-context-budget.md)
Maintainer evidence: "proceed - lets build it" after reviewing the eight features

This is builder evidence. The controller will pin the stable candidate and
complete work-unit aggregate for a new fresh-context read-only validator.
The wider initiative remains started/granted/normal/local. Accepted WS-00
through WS-03 and their frozen reports remain intact. Implementation does not
record independent verification, maintainer acceptance or delivery authority.

## Exact Implementation Manifest

Seven source paths:

- `packages/friday-chat/src/friday_chat/config.py`
- `packages/friday-chat/src/friday_chat/tools/selection.py`
- `packages/friday-chat/src/friday_chat/tools/mcp.py` (new)
- `packages/friday-chat/src/friday_chat/turns/processor.py`
- `packages/friday-chat/src/friday_chat/commands/tools.py`
- `packages/friday-chat/src/friday_chat/runtime.py`
- `packages/friday-chat/src/friday_chat/app.py`

Three test paths:

- `packages/friday-chat/tests_chat/test_mcp_config_compatibility.py`
- `packages/friday-chat/tests_chat/test_mcp_turn_budget.py` (new)
- `packages/friday-chat/tests_chat/test_mcp_chat_bridge.py` (new)

Plus this report: exactly eleven implementation paths. Readiness, approval,
builder-evidence archive, request, independent evidence and process/controller
files are separate scope. No dependency, example configuration, accepted
framework/native registry/transport, transcript, ingestion or telemetry edits.

## Configuration And Public Ownership

Chat retains the canonical `tools.providers.mcp` object and validates it with
the existing `MCPToolProviderConfig.from_dict`, including when disabled.
Invalid previously retained MCP input now fails during Chat config parsing.
The root validation error excludes input values, and provider config is omitted
from `ToolsConfig` repr. There is no parallel public provider/server model.

Two optional Chat selection keys are added under the existing `tools.context`:
`max_mcp_tools` is a nonnegative integer subset cap, and `required_tools` is a
unique list of registered native/canonical MCP tool names. Booleans, negative
counts, non-list required sets, empty names and duplicate names fail parsing.
Existing tool settings and canonical provider limits retain their authority.
WS-08 must document these keys and the earlier invalid-config failure point.

Real Chat assembly constructs `MCPChatRegistry` only when Chat tools and MCP
are enabled. It owns the accepted public `RuntimeMCPProvider` and
`DefaultToolRegistry`, seeds native proxies for collision preflight, and
publishes through public provider methods. Native calls continue through the
original Chat adapter. MCP calls use the public registry callable, preserving
the exact original server/name/arguments from WS-03. Chat reads the typed
read-only sidecar and copied public registry definitions, not manager internals.

The app starts discovery before input/commands and stops through its retained
owner on EOF, startup failure and cancellation, then runs its existing shutdown
coordinator even if MCP stop raises. Direct turn processing starts the same
owner idempotently. Incomplete cleanup leaves that owner reachable for public
retry; it is not replaced. Accepted production transport budgets are unchanged.
Fake runtime construction never connects configured external peers; local tests
explicitly install the bridge alongside fake model/memory/native services.

## Selection, Schema Validation And Budget

The original native/manual/disabled path remains active when MCP is disabled
and no new required set is configured. With MCP enabled, selection checks total
count, optional MCP subset count, existing schema-ratio ceiling and canonical
aggregate/per-tool caps. It requires eligible measured WS-03 metadata and
revalidates each current MCP schema through accepted public sanitation.
Missing/ineligible sidecars, changed unsafe annotations and exports exceeding
the current or recorded byte bound are omitted with static typed reasons;
required versions fail. It does not silently resanitize changed annotations.
The selected MCP model schemas are independent copies of the mutable registry.

`SchemaTokenEstimator` isolates the replaceable native estimate. Its default
is the existing ceil(UTF-8 bytes / 4) approximation. Invalid estimator return
values fail explicitly. MCP cost never falls below the accepted complete-export
metadata estimate or complete current OpenAI export bytes; combined cost also
retains the full model serialization estimate and native contribution. This
conservative estimate is not tokenizer parity. No broad type suppression is added.

Before memory retrieval, the processor computes:

```text
context_window - output_buffer - system_prompt_estimate
  - selected_schema_estimate - reserved_tool_result_tokens
```

Canonical MCP limits provide the memory floor and result reservation only when
Chat tools and MCP are enabled. Any selected tool set reserves the configured
result tokens; empty selection reserves zero. These defaults remain 4096/2048
in accepted runtime config. No tool result is falsely recorded as observed
usage. Streaming and non-streaming both pass the exact remaining `token_limit`
to the existing memory controller. No memory source edit is necessary.

Explicit required tools are selected first. A manual set is required in full
and unions with the configured required list. Unavailable, invalid or count/
schema/floor-exceeding required selections raise a safe `TurnBudgetError`
before retrieval/model calls, and failed manual injection does not mutate the
saved manual set. Provider include filters and required servers do not imply
per-turn required tools.

Optional selection retains deterministic relevance and registry order. When
memory would fall below the floor, optional MCP tools are reduced before losing
optional native candidates. An impossible base budget fails even with no tools.
Count/schema limits retain deterministic ranked admission. Typed frozen evidence
records selected/skipped names, reasons, schema cost, reservation, floor,
before/after memory and MCP count. Known malformed MCP names become a fixed
placeholder; raw schema bytes are excluded from repr. `/tool-budget` adds these
values, retains bounded display/rejection output and safely reports invalid
manual previews. Eligible omissions also identify relevance/manual intent.

## Criterion Evidence Map

| Criterion | Implementation and candidate evidence |
| --- | --- |
| MCP-04-AC-01 | Canonical config/property validator, invalid-config compatibility tests, fake/real factory and unchanged native tests. |
| MCP-04-AC-02 | Public Chat bridge and lifecycle wiring; real stdio exact routing, repeat-start, commands, collision/native preservation, required/optional failure, EOF/cancellation and retained-stop/restart tests. |
| MCP-04-AC-03 | Sidecar eligibility, per-tool/current-export copy validation, count/subset/aggregate caps; mutable-schema, malformed-name, missing/unmeasured metadata and attack tests. |
| MCP-04-AC-04 | Shared preparation subtracts reservation before retrieval; four tool mixes plus exact streaming/non-streaming retrieval tests. |
| MCP-04-AC-05 | Empty/base floor check and optional MCP reduction; mixed native/MCP floor and pre-retrieval exhaustion tests. |
| MCP-04-AC-06 | Required/manual union and atomic saved-set behavior; unavailable/count/subset/schema/floor negative tests. |
| MCP-04-AC-07 | Injectable protocol, native compatibility and conservative MCP tests; seven-source-file meaningful typing and scoped Ruff pass. |
| MCP-04-AC-08 | Frozen budget/static error reasons, bounded command diagnostics, local secret-sentinel/owner/task/process checks, configuration migration and exact check/baseline record below. |

Tests assert public process termination and both pipe EOFs before defensive
fixture cleanup. Fixtures still kill/drain/reap synthetic children and settle
tasks on assertion failure. Real factory UAT constructs actual framework
adapters with temporary storage and inert model identifiers without calling
a live model. UAT is deterministic local evidence, not live-provider approval.

## Exact Verification Record

The [builder evidence manifest](WS-04-builder-evidence.yaml) and lossless archive
preserve scripts, exact commands, logs, results and preservation hashes.
Tests used `LITELLM_LOCAL_MODEL_COST_MAP=true`,
`UV_CACHE_DIR=/private/tmp/friday-uv-cache`, `UV_OFFLINE=true` and
`PYTHONDONTWRITEBYTECODE=1`; tooling used the same cache. All commands below ran
at the candidate source state. No required check was skipped or repaired outside scope.

| Command (prefix `uv run`) | Exit | Result |
| --- | --- | --- |
| `pytest packages/friday-chat/tests_chat -q --tb=short` | 1 | 479 passed, 5 skipped, 1 unchanged PTY failure, 3 sandbox socket-bind fixture errors. |
| `pytest packages/friday-runtime/tests_runtime -q` | 0 | 190 passed. |
| `pytest packages/friday-memory/tests_memory -q` | 0 | 680 passed, 1 skipped. |
| `pytest tests/integration -q --tb=short` | 1 | 69 passed; unchanged board-count assertion expects 22 instead of canonical 23. |
| `pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime tests/integration/test_mcp_registry.py tests/integration/test_mcp_runtime_lifecycle.py -q` | 0 | 440 passed. |
| `ruff check packages/friday-chat packages/friday-runtime packages/friday-memory` | 0 | All checks passed. |
| `mypy packages/friday-chat packages/friday-runtime packages/friday-memory` | 2 | Unchanged installed NumPy stub syntax at line 737 under default Python 3.10 target; project checking stops. |
| `mypy --python-version 3.13` with the exact seven source paths above | 0 | Success: no issues in 7 source files. |
| `python scripts/friday-dev-board.py validate` | 0 | 23 tasks valid. |
| `python scripts/friday-dev-board.py render --check` | 0 | Dashboard current. |
| `python scripts/check-documentation-lifecycle.py` | 0 | Documentation lifecycle passed before adding this report; repeat at freeze. |

Focused command with the three WS-04 tests plus existing
`test_tool_selection_budget.py` and `test_turn_processing.py`: 84 passed.
Before edits, the full Chat suite produced 436 passes/5 skips and the identical
PTY failure/three `PermissionError` localhost fixture errors. Memory baseline
was 680 passes/1 skip, Ruff passed, the same default NumPy typing error occurred,
and focused six-existing-source typing passed. The board-count failure was
separately reproduced from an extracted accepted `acd1fd1` predecessor.
These are explicit unchanged baseline/environment failures, not passed checks
or waivers. The fresh validator must establish its own baseline evidence.

Development iterations caught one new-source typing return annotation issue,
corrected before final checks. New test harnesses were corrected for missing
command metadata and accepted retained-disconnected-manager semantics. An
unsupported assumption that every HTML tag is an accepted attack pattern was
replaced by a known accepted role-delimiter case; no sanitizer expansion is
claimed or implemented. Existing invalid-MCP tests now assert the approved
earlier safe config-validation point. Final results supersede development runs
without deleting their logs or classifying new defects as baseline debt.

Preservation check confirms all 24 previously pinned authority/report hashes,
961 prior tracked product files outside the exact changed scope, and all five
unrelated path fingerprints unchanged, including the existing deletion.
Only named paths will be staged. No cache/user state cleanup is performed.

## Residual Gates

Fresh complete WS-04 aggregate review, durable independent evidence and explicit
maintainer acceptance remain required. The controller will pin the report and
authority hashes, verify frozen source and preserve unrelated work throughout
review. Changing the candidate requires a new independent review.

Approximate native/system estimation is not exact model tokenization. The
approved formula does not promise accounting for every future user/history/
tool-result token. Result reservation does not bound or sanitize actual results.
Known schema sanitation is not universal prompt-injection prevention. Output
handling/provenance, long-term ingestion/quarantine, telemetry/health, final
user documentation and any live UAT remain WS-05/06/07/08 gates. No new command,
resource/prompt support, live refresh, external config include or delivery.
