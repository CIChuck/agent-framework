# Proposed CD-004: turn, tool, memory and persistence telemetry

Status: proposed, not approved. Prepared 2026-10-07.
Initiative: friday-telemetry-rewire. Work unit: TELEM-04.
Branch: feature/friday-telemetry-rewire.
Preparation base: e6209e3156216afde1655758e280690229f7d3e6.
Aggregate base: 2155a0fc51f5b20dea4e35c6cfc70f1d52002735.

Chuck Russell instructed "lets continue with telem-04" after TELEM-03's VERIFIED
closeout and explanation of the next unit. That authorizes this planning packet;
this exact new construction scope and separate lint disposition require approval.
Planning-only exemption: Chuck Russell,2026-10-07; prepare this directive, contract,
profile, scope manifest, evidence, TELEM-03 acceptance archive and the initiative's
board/dashboard/index/log/closeout metadata. No product behavior changes. Validate
authority hashes, static scope, board, documentation and dirty-work preservation.

## Objective and controlling authority

Link one safe turn identity across existing Friday Chat model/tool/memory/transcript
execution, expose truthful failure/commit outcomes and bounded operational diagnostics,
and preserve accepted LLM/MCP contracts and borrowed provider ownership. Follow
maintainer direction, repository policies, accepted TELEM-01–03 specifications,
build/tactical plans, this directive, the [contract](../telem04-contract.md), and
[verification profile](../verification-profile-TELEM-04.md), in that order.
The [manifest](../authority-manifest-TELEM-04.yaml) pins exact controls and29 product
targets. Approval does not rewrite prior frozen specifications or lint waivers.

## Exact product manifest

| Existing source | Allowed behavior |
| --- | --- |
| packages/friday-telemetry/src/friday_telemetry/__init__.py | Additive typed exports only |
| packages/friday-chat/src/friday_chat/telemetry.py | Validate new event union; owned typed correlation; linked accepted events; safe spans/metrics/snapshots |
| packages/friday-chat/src/friday_chat/turns/processor.py | Turn/operation scopes; selection/reasoning facts; truthful persistence; optional safe TurnResult context |
| packages/friday-chat/src/friday_chat/tools/loop.py | Actual native/MCP dispatch observation; existing selection/failure/provenance control flow |
| packages/friday-chat/src/friday_chat/runtime.py | Optional typed observation assembly and PendingExtractionTurn origin context |
| packages/friday-chat/src/friday_chat/adapters.py | Instrument existing memory ingestion and per-item extraction boundaries; optional observer injection only |
| packages/friday-chat/src/friday_chat/background.py | Explicit safe context handoff and background scope clearing; preserve scheduling/requeue |
| packages/friday-chat/src/friday_chat/app.py | Pass successful origin context to background work; preserve custom/fake turn handler compatibility |
| packages/friday-chat/src/friday_chat/commands/registry.py | Extend existing /debug and /timing with bounded safe local snapshots |

New source: packages/friday-telemetry/src/friday_telemetry/models/execution.py,
packages/friday-telemetry/src/friday_telemetry/helpers/correlation.py, and
packages/friday-chat/src/friday_chat/turns/telemetry.py. These own the closed schema,
typed scope/identity contract and Chat execution observation helpers respectively.

Existing tests, all under packages/friday-chat/tests_chat/: test_telemetry.py,
test_turn_processing.py, test_background_work.py, test_app_lifecycle.py,
test_runtime.py, test_command_foundations.py, test_command_production_adapters.py,
test_mcp_execution_transcript.py and test_mcp_memory.py.

New tests: packages/friday-telemetry/tests_telemetry/test_execution_events.py and
test_correlation.py; packages/friday-chat/tests_chat/test_turn_telemetry.py,
test_tool_telemetry.py, test_memory_telemetry.py and test_telemetry_diagnostics.py.
Documentation: packages/friday-telemetry/README.md and packages/friday-chat/README.md.
Total12 source,15 test and2 documentation targets. Changed paths may be a subset,
never a superset. Existing prospective source typing/lint passes without waiver;
new/changed code must also pass. No unrelated cleanup within these files.

## Construction and acceptance

| Criterion | Required result |
| --- | --- |
| AC04-01 | Strict safe events/references/counts/floats/enums/scalar cap; malformed/forged/content-sentinel negatives; accepted LLM/MCP/interface unchanged |
| AC04-02 | Completion/streaming start/terminal exactly once, including selection/circuit block, timeout, exhausted retry, callback failure and cancellation; stable child lineage, independent concurrent/nested sessions and restored context |
| AC04-03 | Actual native/MCP dispatch counts/outcomes and rejections; accepted provenance/sanitization/ID repair unchanged; no MCP failed return counted successful |
| AC04-04 | Retrieval/store/document-ingestion and per-item extraction observations; origin retention across background retry/preemption/shutdown; mixed-turn batches/no-extractor/empty cases; committed-under-cancellation truth |
| AC04-05 | Individual memory/transcript/context/interaction persistence stages; intermediate partial facts on subsequent failure; no premature turn success or invented atomic rollback; MCP receipt and publication remain distinct |
| AC04-06 | Multi-iteration reasoning-preservation booleans derived from actual outgoing history; accepted MCP redaction and request/results unchanged; links join accepted model requests and safe MCP observations |
| AC04-07 | Bounded exporter-off/failed diagnostics, failed-turn /debug+/timing inspection, fixed counter/histogram ownership, no duplicate/dynamic labels; safe actual SDK/Composite context and cleanup |
| AC04-08 | Scope/API/privacy/typing/lint/tests/lock/docs/accepted-authority/preservation gates, stable product commit and fresh-context independent full unit plus aggregate VERIFIED |

Before source edits, freeze actual scope/API inventory and run fake baseline probes
for normal/failed/cancelled turns, native/MCP tool returns, staged persistence,
reasoning follow-ups, and mixed background extraction. Patch transport/real stores
before calls. Proposal static inspection is not executed behavioral evidence.
Implement schema/scopes first, then turn/tool/persistence boundaries, adapter/background
handoff, diagnostics and docs. Keep each accepted public boundary under consumer
regression tests. Do not edit tests outside the exact manifest to accommodate drift.

## Non-goals and effects

No edits to friday-llm source/events/prices/usage accounting, accepted MCP models,
MCP provider/output-policy/memory_mcp coordination, memory/transcript storage APIs,
database schemas, authorization/tool-governance policy, session persistence IDs,
selection/retry/history algorithms, config/templates, dependencies/lock or lint
configuration. Framework headless adoption, optional Langfuse, OTel Meter wiring,
remote activation and persisted/raw diagnostics require separate scope decisions.

New tests use only fakes and memory; no listener/database/provider/SDK worker effects
from fixtures. A separately executed actual installed SDK probe may use an owned
in-memory exporter, Debug and two-child Composite with explicit cleanup and no
network/global registration. Approval covers the13 unchanged existing loopback
nodes in the [effect inventory](../execution/TELEM-04-planning/listener-scope.json),
normal-user localhost execution after final fixture/import/helper preflight. It
does not inherit prior unit effects. No credentials, real .friday/Chroma/transcript
data, TLS/remote service, paid call, install/sync/download, push/merge or publication.

Root Ruff remains raw exit1 for exactly327 historical findings. Separately proposed
[WVR-006](../validation/WVR-006-telem04-lint-disposition.md) is the only requested
exception; CD-004 approval alone grants none. Its fresh independent reconciliation
must precede construction. All other gates require normal passes.

Stop for changed authority/accepted inputs, extra product paths/effects, new lint
identities/suppressions/skips, public behavior drift, absent required evidence,
non-hermetic transport/state activation or unresolved policy conflicts. Do not
auto-remediate beyond this exact scope. Report raw failures and reruns separately,
freeze candidate/evidence and dispatch a fresh-context read-only product validator
as required by AGENTS.md. VERIFIED permits completion proposal; maintainer acceptance
and delivery remain separate decisions.
