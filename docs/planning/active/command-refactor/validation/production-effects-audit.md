# Production-adapter and effect-order audit

Date: 2026-11-04
Source: `25d2dcb6`; inspected source/test hashes match the initial P0 inventory
Status: Evidence for API design; not aggregate PAR or P0 signoff

## Evidence provenance

The initial [Chat JUnit receipt](p0/chat.xml) contains 54 passing cases across
`test_command_production_adapters.py` (8), `test_transcript_production_commands.py`
(7), `test_memory_diagnostics_commands.py` (12) and `test_maintenance_commands.py`
(27). Their current SHA-256 hashes match [the inventory](p0/inventory.json).
The later controlled full suite passed 826 tests. No repeated suite run was
necessary for this source audit. Production adapters use temporary stores and
deterministic embedding dependencies; selected modules prohibit network/provider
transports. This is real adapter/store evidence, not live model/provider proof.

## Inspected assertions and required preservation

| Evidence under `packages/friday-chat/tests_chat/` | What it establishes | Required shared boundary |
| --- | --- | --- |
| `test_command_production_adapters.py::test_sessions_lists_seeded_persisted_session` and `test_transcript_reads_seeded_current_and_selected_sessions` | Seeded persisted sessions and both user/assistant markers are visible through current and explicitly selected IDs. | Query persisted identity and entries; never substitute only in-process history. |
| `test_command_production_adapters.py::test_memory_reports_seeded_real_episodic_count` | `/memory` observes one stored turn. | Public memory statistics, distinct from cached UI history. |
| `test_command_production_adapters.py::test_clear_aliases_request_display_effect_without_false_output` | `/cls` and `/clearscreen` each clear once and produce no output text. | One clear intent; frontend performs it once. No service reset or fake success text. |
| `test_command_production_adapters.py::test_meta_dispatches_seeded_real_adapter_record` | A seeded synthesis record appears via `/meta`. | Typed active-memory query; do not replace with a placeholder or trigger synthesis. |
| `test_memory_diagnostics_commands.py::test_memory_metric_preserves_zero_unavailable_and_not_configured` | Zero is available data; unavailable/not-configured have no value; invalid available-without-value is rejected. | Preserve discriminated metric state/value invariants. |
| `test_memory_diagnostics_commands.py::test_memory_reports_exact_seeded_public_store_and_context_values` | Vector tiers, graph, access-buffer, priming, session and token budgets have specific values. | Typed per-component data; removing `/prime` does not remove startup priming. The scoped-variable count needs explicit treatment in the retirement directive, not incidental removal. |
| `test_memory_diagnostics_commands.py::test_memory_partial_count_failure_retains_other_real_values` and `test_meta_partial_failure_returns_records_and_sanitized_warning` | Available components/records survive a partial failure; raw database errors/paths are not displayed. | Partial-data outcome with typed sanitized warnings, not zero filling or all-or-nothing failure. |
| `test_memory_diagnostics_commands.py::test_meta_empty_state_is_actionable_and_read_only` | Empty result has guidance and leaves store stats unchanged. | Empty query remains a read; guidance is renderer-owned from semantic status. |
| `test_transcript_production_commands.py::test_query_and_partial_export_failures_are_sanitized` | Query/export errors use bounded messages; failed all-session export leaves no partial export directory. | Query and export errors remain distinct; service owns cleanup and renderer owns safe messages. |
| `test_maintenance_commands.py::test_replay_waits_for_exclusive_maintenance_admission` | Replay waits while another task holds exclusive admission. | Neutral admission capability preserving actual gate ownership, fairness and wait semantics. |
| `test_maintenance_commands.py::test_compact_flushes_pending_extraction_before_run` | Flush completes, pending work clears, then compaction runs with manual-command reason. | One shared sequencing policy: flush before compact. |
| `test_maintenance_commands.py::test_compact_flush_failure_preserves_pending_turns_and_skips_compactor` | Failed flush leaves pending turns intact and compaction is not called. | Do not dequeue first or report compaction success. No automatic retry. |
| `test_maintenance_commands.py::test_lifecycle_default_is_dry_run` and `test_migrate_force_execute_alias_and_no_migration_needed` | Lifecycle defaults to dry-run; migrate force/execute agree; no-needed stats report no changed records. | Preserve argument defaults and aliases, not a new generic safety policy. |

## Source-derived ordering that still needs exact failure probes

- `registry.py::_clear_handler` clears in-process history before awaiting
  `memory.clear_session_memory()`. A later exception does not restore that history.
  Changing this to transactional clear would change retained behavior.
- `registry.py::_reset_handler` attempts graph, vector and episodic resets in that
  order for full reset, collecting per-store errors and continuing. It then clears
  diagnostic fields, conditionally awaits session-memory clear, and on full reset
  clears history/pending extraction before archiving transcripts. Later failures
  can propagate after earlier effects; there is no blanket rollback guarantee.
- `registry.py::_compact_handler` checks unavailable/disabled/running conditions,
  flushes pending extraction, then compacts. Its two caught failures have different
  messages; preserve both stages and their pending-state behavior.
- Registry admission wraps reset, lifecycle, migrate, compact, ingest and replay;
  reorganize/recovery also has its own coordinator/exclusive path. The retired
  run-tool admission case is before-change evidence only. Do not add or remove
  locks during neutralization, or wrap exclusive work in a deadlocking new gate.
- `transcript.py` validates/query-selects identity before exporting; helpers own
  file effects and cleanup. Do not move export execution into a frontend renderer.
- Current Chat `_read_handler` takes `remaining[0]` after whitespace parsing;
  unlike the generic CLI parser, quoted paths are not combined at this boundary.
  This is a compatibility observation; no quote-support enhancement is authorized.

These source observations do not claim fault-injection proof. Exact probe cases
for clear/reset late failures, cancellation and progress-sink failure must be
bound before the corresponding family's construction directive.

## Design disposition

Use narrow session, memory-query, file, transcript/export, tool-inventory,
maintenance/admission, orchestration, replay, security, speech and workflow
capabilities. Domain services own storage/transport and cleanup. Shared handlers
own command sequencing/policy. Frontends own rendering and UI intents.

The [API draft](../shared-command-api.md) applies these findings. Family-specific
port signatures and relocation of services currently owned by Chat still need
review. The [foundation directive](../directives/CD-CMD-FND-001-neutral-foundation.md)
is proposed only; no product implementation is authorized by this audit.
