# PAR source coverage ledger

Date: 2026-11-04
Source HEAD: `fc028f3bf128a610aae7d95b59afb4b601bec0eb`

Status: P0 source map with 2026-11-06 proposed unit assignments; behavioral case-level signoff remains open.

The [Step 3 readiness review](../readiness-review.md) and
[unit/scenario/environment map](step3/unit-map.json) assign all 50 cases and three
aliases. These are proposed owners, not approved migration directives. FND-001
migrates no case; its foundation-only prerequisite amendment needs Step 4 approval.

Authority: [resolved decisions](../scope-decisions.md) and [next-phase checkpoint](../next-phase.md).

The 50-name snapshot is unchanged. Target: 41 retained names, nine removals,
three retained aliases. **Extract** means move semantics to the shared owner
while preserving Chat behavior; **remove** means no legacy shim or former effect.

Reproduce the source map with:

```sh
uv run python docs/planning/active/command-refactor/validation/p0/capture_inventory.py
```

[Machine-readable inventory](p0/inventory.json) includes complete live metadata,
direct context accesses/assignments, calls, candidate test nodes and fixture
parameter names, metadata drift and source/test SHA-256 hashes. AST matches
are navigation aids: a command literal in a test is not proof that a behavior
was exercised. Direct accesses omit transitive helper effects.

[Baseline receipt](p0-baseline.md) records actual suite and probe results.

| Case | Name / target | Handler | Direct state/service access (abridged) | Candidate test nodes | Proposed unit | Behavioral signoff |
| --- | --- | --- | --- | ---: | --- | --- |
| PAR-001 | `/agent` — extract | `friday_chat.commands.registry._agent_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:1103) | context.runtime, context.runtime.orchestrator, context.runtime.orchestrator.active_agent, context.runtime.orchestrator.describe_agent | 1 | ORCH-001 | Open before owning unit |
| PAR-002 | `/agents` — extract | `friday_chat.commands.registry._agents_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:1085) | context.runtime, context.runtime.orchestrator | 1 | ORCH-001 | Open before owning unit |
| PAR-003 | `/clear` — extract | `friday_chat.commands.registry._clear_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:260) | context.history, context.history.clear, context.runtime, context.runtime.memory | 1 | SESSION-001 | Open before owning unit |
| PAR-004 | `/clear-tools` — remove | `friday_chat.commands.tools.clear_tools_handler` (packages/friday-chat/src/friday_chat/commands/tools.py:77) | context.runtime, context.runtime.tool_selection, context.runtime.tool_selection.clear_manual | 3 | RET-001 | Open before owning unit |
| PAR-005 | `/cls` — extract | `friday_chat.commands.session.cls_handler` (packages/friday-chat/src/friday_chat/commands/session.py:13) | See helper calls in inventory | 5 | PILOT-001 | Open before owning unit |
| PAR-006 | `/compact` — extract | `friday_chat.commands.registry._compact_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:755) | context.runtime, context.runtime.config, context.runtime.config.memory, context.runtime.config.memory.compaction | 3 | MAINT-001 | Open before owning unit |
| PAR-007 | `/context` — extract | `friday_chat.commands.registry._context_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:285) | context.last_context | 4 | DIAG-001 | Open before owning unit |
| PAR-008 | `/debug` — extract | `friday_chat.commands.registry._debug_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:311) | context.last_debug, context.last_debug.items, context.runtime, context.runtime.telemetry | 3 | DIAG-001 | Open before owning unit |
| PAR-009 | `/debug-budget` — extract | `friday_chat.commands.registry._debug_budget_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:329) | context.runtime, context.runtime.config, context.runtime.config.memory | 1 | DIAG-001 | Open before owning unit |
| PAR-010 | `/debug-retrieval` — extract | `friday_chat.commands.registry._debug_retrieval_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:382) | context.runtime, context.runtime.memory, context.runtime.memory.debug_retrieval | 1 | DIAG-001 | Open before owning unit |
| PAR-011 | `/delegate` — extract | `friday_chat.commands.registry._delegate_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:1117) | context.runtime, context.runtime.orchestrator | 1 | ORCH-001 | Open before owning unit |
| PAR-012 | `/entities` — extract | `friday_chat.commands.registry._entities_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:409) | context.runtime, context.runtime.memory, context.runtime.memory.list_entities, context.runtime.memory.list_relationships | 3 | MEMQ-001 | Open before owning unit |
| PAR-013 | `/exit` — extract | `friday_chat.commands.registry._exit_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:252) | See helper calls in inventory | 4 | PILOT-001 | Open before owning unit |
| PAR-014 | `/export` — extract | `friday_chat.commands.transcript.export_handler` (packages/friday-chat/src/friday_chat/commands/transcript.py:107) | context.runtime, context.runtime.transcript, context.runtime.transcript.query_entries, context.runtime.transcript.query_session | 7 | TRANSCRIPT-001 | Open before owning unit |
| PAR-015 | `/export-prompts` — extract | `friday_chat.commands.transcript.export_prompts_handler` (packages/friday-chat/src/friday_chat/commands/transcript.py:145) | context.runtime, context.runtime.transcript, context.runtime.transcript.query_context_logs, context.runtime.transcript.query_session | 6 | TRANSCRIPT-001 | Open before owning unit |
| PAR-016 | `/help` — extract | `friday_chat.commands.registry._help_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:1346) | context.registry | 20 | PILOT-001 | Open before owning unit |
| PAR-017 | `/history` — extract | `friday_chat.commands.registry._history_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:271) | context.history | 3 | SESSION-001 | Open before owning unit |
| PAR-018 | `/ingest` — extract | `friday_chat.commands.registry._ingest_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:812) | context.runtime, context.runtime.memory, context.runtime.memory.ingest_document | 1 | FILE-001 | Open before owning unit |
| PAR-019 | `/inject-payload` — remove | `friday_chat.commands.registry._inject_payload_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:992) | context.injected_payload | 1 | RET-001 | Open before owning unit |
| PAR-020 | `/inject-tools` — remove | `friday_chat.commands.tools.inject_tools_handler` (packages/friday-chat/src/friday_chat/commands/tools.py:32) | context.runtime, context.runtime.tool_selection, context.runtime.tools, context.runtime.tools.list_tools | 4 | RET-001 | Open before owning unit |
| PAR-021 | `/insights` — extract | `friday_chat.commands.memory.insights_handler` (packages/friday-chat/src/friday_chat/commands/memory.py:110) | See helper calls in inventory | 2 | MEMQ-001 | Open before owning unit |
| PAR-022 | `/lifecycle` — extract | `friday_chat.commands.registry._lifecycle_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:682) | context.runtime, context.runtime.config, context.runtime.config.lifecycle, context.runtime.config.lifecycle.access_buffer | 2 | MAINT-001 | Open before owning unit |
| PAR-023 | `/list-ingested` — extract | `friday_chat.commands.registry._list_ingested_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:844) | context.runtime, context.runtime.memory | 1 | MEMQ-001 | Open before owning unit |
| PAR-024 | `/memory` — extract | `friday_chat.commands.memory.memory_handler` (packages/friday-chat/src/friday_chat/commands/memory.py:31) | context.history, context.last_budget_status, context.runtime, context.runtime.memory | 7 | MEMQ-001 | Open before owning unit |
| PAR-025 | `/meta` — extract | `friday_chat.commands.memory.meta_handler` (packages/friday-chat/src/friday_chat/commands/memory.py:136) | See helper calls in inventory | 8 | MEMQ-001 | Open before owning unit |
| PAR-026 | `/migrate` — extract | `friday_chat.commands.registry._migrate_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:722) | context.runtime, context.runtime.config, context.runtime.config.memory, context.runtime.config.memory.persist_directory | 2 | MAINT-001 | Open before owning unit |
| PAR-027 | `/prime` — remove | `friday_chat.commands.registry._prime_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:365) | context.runtime, context.runtime.config, context.runtime.config.memory, context.runtime.config.memory.priming | 1 | RET-001 | Open before owning unit |
| PAR-028 | `/prompt` — extract | `friday_chat.commands.registry._prompt_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:299) | context.last_prompt | 2 | DIAG-001 | Open before owning unit |
| PAR-029 | `/read` — extract | `friday_chat.commands.registry._read_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:797) | See helper calls in inventory | 3 | FILE-001 | Open before owning unit |
| PAR-030 | `/recommend-tools` — remove | `friday_chat.commands.registry._recommend_tools_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:1293) | See helper calls in inventory | 2 | RET-001 | Open before owning unit |
| PAR-031 | `/reorganize` — extract | `friday_chat.commands.registry._reorganize_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:496) | context.runtime, context.runtime.config, context.runtime.config.memory, context.runtime.config.memory.persist_directory | 18 | MAINT-001 | Open before owning unit |
| PAR-032 | `/replay` — extract | `friday_chat.commands.registry._replay_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:863) | context.runtime | 3 | REPLAY-001 | Open before owning unit |
| PAR-033 | `/reset` — extract | `friday_chat.commands.registry._reset_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:451) | context.history, context.history.clear, context.last_budget_status, context.last_context | 4 | MAINT-001 | Open before owning unit |
| PAR-034 | `/run-tool` — remove | `friday_chat.commands.registry._run_tool_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:1247) | context.injected_payload, context.runtime, context.runtime.tools, context.runtime.tools.call_tool | 6 | RET-001 | Open before owning unit |
| PAR-035 | `/security` — extract | `friday_chat.commands.registry._security_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:893) | context.runtime, context.runtime.config, context.runtime.config.security, context.runtime.config.security.sanitization | 1 | SEC-001 | Open before owning unit |
| PAR-036 | `/security-config` — extract | `friday_chat.commands.registry._security_config_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:953) | context.runtime, context.runtime.config, context.runtime.config.security, context.runtime.config.security.sanitization | 2 | SEC-001 | Open before owning unit |
| PAR-037 | `/security-test` — extract | `friday_chat.commands.registry._security_test_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:922) | context.security_stats | 1 | SEC-001 | Open before owning unit |
| PAR-038 | `/sessions` — extract | `friday_chat.commands.transcript.sessions_handler` (packages/friday-chat/src/friday_chat/commands/transcript.py:32) | context.runtime, context.runtime.transcript, context.runtime.transcript.query_session, context.runtime.transcript.query_sessions | 7 | TRANSCRIPT-001 | Open before owning unit |
| PAR-039 | `/set` — remove | `friday_chat.commands.registry._set_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:1333) | context.variables | 3 | RET-001 | Open before owning unit |
| PAR-040 | `/speech` — extract | `friday_chat.commands.registry._speech_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:1003) | context.runtime, context.runtime.config, context.runtime.config.chat, context.runtime.config.chat.system_prompt | 3 | SPEECH-001 | Open before owning unit |
| PAR-041 | `/speech-test` — extract | `friday_chat.commands.registry._speech_test_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:1054) | context.runtime, context.runtime.config, context.runtime.config.speech, context.runtime.config.speech.enabled | 1 | SPEECH-001 | Open before owning unit |
| PAR-042 | `/status` — extract | `friday_chat.commands.registry._status_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:1140) | context.runtime, context.runtime.orchestrator | 1 | ORCH-001 | Open before owning unit |
| PAR-043 | `/summaries` — extract | `friday_chat.commands.memory.summaries_handler` (packages/friday-chat/src/friday_chat/commands/memory.py:123) | See helper calls in inventory | 2 | MEMQ-001 | Open before owning unit |
| PAR-044 | `/switch` — extract | `friday_chat.commands.registry._switch_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:1068) | context.runtime, context.runtime.orchestrator | 1 | ORCH-001 | Open before owning unit |
| PAR-045 | `/timing` — extract | `friday_chat.commands.registry._timing_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:346) | context.last_timing, context.last_timing.items, context.runtime, context.runtime.telemetry | 1 | DIAG-001 | Open before owning unit |
| PAR-046 | `/tool-budget` — remove | `friday_chat.commands.tools.tool_budget_handler` (packages/friday-chat/src/friday_chat/commands/tools.py:89) | context.runtime, context.runtime.tool_selection, context.runtime.tools, context.runtime.tools.list_tools | 5 | RET-001 | Open before owning unit |
| PAR-047 | `/tools` — extract | `friday_chat.commands.registry._tools_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:1197) | context.runtime, context.runtime.mcp_tools, context.runtime.mcp_tools.rejection_lines, context.runtime.mcp_tools.status_lines | 4 | TOOLS-001 | Open before owning unit |
| PAR-048 | `/transcript` — extract | `friday_chat.commands.transcript.transcript_handler` (packages/friday-chat/src/friday_chat/commands/transcript.py:78) | context.runtime, context.runtime.transcript, context.runtime.transcript.query_entries, context.runtime.transcript.query_session | 11 | TRANSCRIPT-001 | Open before owning unit |
| PAR-049 | `/vars` — remove | `friday_chat.commands.registry._vars_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:1321) | context.variables, context.variables.items | 1 | RET-001 | Open before owning unit |
| PAR-050 | `/workflow` — extract | `friday_chat.commands.registry._workflow_handler` (packages/friday-chat/src/friday_chat/commands/registry.py:1158) | context.runtime, context.runtime.workflow | 2 | WORKFLOW-001 | Open before owning unit |

## Alias obligations

- `/clearscreen` → `/cls` (PAR-005): retain dispatch, help and effect equivalence; see baseline probe.
- `/quit` → `/exit` (PAR-013): retain dispatch, help and effect equivalence; see baseline probe.
- `/q` → `/exit` (PAR-013): retain dispatch, help and effect equivalence; see baseline probe.

## Open evidence obligations

Each of the 50 rows remains **case-level review pending**: inspect the candidate
test assertions, assign exact positive/invalid/unavailable/cancellation/error
nodes or document why a class is inapplicable, and link actual receipts.
Use existing tmp_path/fake-runtime fixtures where applicable; effectful probes
must use disposable stores. Do not infer coverage from suite totals or literals.

The nine removal rows retain before-change behavior evidence only; after-change
unknown-name, no-effect and discovery-removal checks belong to an approved
retirement directive. No handler migration or retirement occurred in P0.

Before construction: finish the transitive service/effect and failure-order map,
freeze exact fixture/result expectations, assign migration families and cross-family
scenarios, and obtain contract/directive approval. No P0/P1 completion claimed.

The [50-case default behavior audit](default-behavior-audit.md) adds observed
outputs/state, and the [selected assertion audit](behavior-assertion-audit.md)
records inspected test semantics. The [failure controls](p0-failure-disposition.md)
isolate the initial red baseline without modifying product source or tests.
