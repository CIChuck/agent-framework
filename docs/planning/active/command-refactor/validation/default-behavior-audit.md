# Default-invocation behavior audit

Date: 2026-11-04

Fixture: fresh in-memory `RegistryCommandContext(runtime=None)` per case.
No provider, external tool or persistent store is configured. This captures
the actual default/no-runtime branch of all 50 commands; it does not prove
successful initialized-runtime behavior or classify every failure branch.

Reproduce with `uv run python docs/planning/active/command-refactor/validation/p0/probe_no_runtime.py`.

[Full before/after state and outputs](p0/no-runtime.json). All retained and
retired names still exist in this baseline; retirement is a future change.

| Case | Invocation | Observed first line | State change |
| --- | --- | --- | --- |
| PAR-001 | `/agent` | Orchestrator is not enabled. | none in captured fields |
| PAR-002 | `/agents` | Orchestrator is not enabled. | none in captured fields |
| PAR-003 | `/clear` | Conversation history cleared. | none in captured fields |
| PAR-004 | `/clear-tools` | Error: Tool registry not initialized. | none in captured fields |
| PAR-005 | `/cls` | (no text) | clear_screen |
| PAR-006 | `/compact` | Compaction service is not configured. | none in captured fields |
| PAR-007 | `/context` | Context payload: | none in captured fields |
| PAR-008 | `/debug` | No debug information recorded. | none in captured fields |
| PAR-009 | `/debug-budget` | Token budget: | none in captured fields |
| PAR-010 | `/debug-retrieval` | Memory runtime is not initialized. | none in captured fields |
| PAR-011 | `/delegate` | Orchestrator is not enabled. | none in captured fields |
| PAR-012 | `/entities` | Memory runtime is not initialized. | none in captured fields |
| PAR-013 | `/exit` | Goodbye. | exit_requested |
| PAR-014 | `/export` | Transcript storage is unavailable. | none in captured fields |
| PAR-015 | `/export-prompts` | Transcript storage is unavailable. | none in captured fields |
| PAR-016 | `/help` | Available commands: | none in captured fields |
| PAR-017 | `/history` | No conversation history. | none in captured fields |
| PAR-018 | `/ingest` | Memory runtime is not initialized. | none in captured fields |
| PAR-019 | `/inject-payload` | Usage: /inject-payload <payload> | none in captured fields |
| PAR-020 | `/inject-tools` | Usage: /inject-tools <names> | none in captured fields |
| PAR-021 | `/insights` | Memory runtime is not initialized. | none in captured fields |
| PAR-022 | `/lifecycle` | Lifecycle service is not configured. | none in captured fields |
| PAR-023 | `/list-ingested` | Memory runtime is not initialized. | none in captured fields |
| PAR-024 | `/memory` | Memory runtime is not initialized. | none in captured fields |
| PAR-025 | `/meta` | Memory runtime is not initialized. | none in captured fields |
| PAR-026 | `/migrate` | Cannot migrate: memory.persist_directory is required. | none in captured fields |
| PAR-027 | `/prime` | Primed context: | none in captured fields |
| PAR-028 | `/prompt` | System: You are Friday. | none in captured fields |
| PAR-029 | `/read` | Usage: /read <path> [--lines=N] | none in captured fields |
| PAR-030 | `/recommend-tools` | Usage: /recommend-tools <query> | none in captured fields |
| PAR-031 | `/reorganize` | Cannot reorganize: memory.persist_directory is required. | none in captured fields |
| PAR-032 | `/replay` | Runtime is not initialized. | none in captured fields |
| PAR-033 | `/reset` | Memory runtime is not initialized. | none in captured fields |
| PAR-034 | `/run-tool` | Error: Tool registry not initialized. | none in captured fields |
| PAR-035 | `/security` | Security status: | none in captured fields |
| PAR-036 | `/security-config` | Security runtime is not initialized. | none in captured fields |
| PAR-037 | `/security-test` | Security test results: | security_stats |
| PAR-038 | `/sessions` | Transcript storage is unavailable. | none in captured fields |
| PAR-039 | `/set` | Usage: /set <key> <value> | none in captured fields |
| PAR-040 | `/speech` | Speech runtime is not initialized. | none in captured fields |
| PAR-041 | `/speech-test` | Speech test requires speech to be enabled. | none in captured fields |
| PAR-042 | `/status` | Orchestrator is not enabled. | none in captured fields |
| PAR-043 | `/summaries` | Memory runtime is not initialized. | none in captured fields |
| PAR-044 | `/switch` | Orchestrator is not enabled. | none in captured fields |
| PAR-045 | `/timing` | No timing data recorded. | none in captured fields |
| PAR-046 | `/tool-budget` | Tool budget unavailable: runtime not initialized. | none in captured fields |
| PAR-047 | `/tools` | No tools are available. | none in captured fields |
| PAR-048 | `/transcript` | Transcript storage is unavailable. | none in captured fields |
| PAR-049 | `/vars` | No scoped variables. | none in captured fields |
| PAR-050 | `/workflow` | Workflow engine is not enabled. | none in captured fields |

## Coverage limits

Positive service/state effects, invalid grammar, cancellation, partial failure
ordering and frontend rendering remain separate obligations. No-runtime
branches that ignore extra arguments must not be silently tightened during
extraction. For `/cls`, dispatch requests a UI effect; this does not invoke
a terminal. For `/exit`, the result/context flag changes; no process exits.

Compare against the [source ledger](par-coverage-ledger.md) and
[baseline failure controls](p0-failure-disposition.md) before defining directives.
