# P0 reviewed behavior assertions

Date: 2026-11-04
Status: Selected assertion audit; not all-class PAR signoff

This supplements the [source ledger](par-coverage-ledger.md) with assertions
actually inspected, rather than treating command-string matches as coverage.
The owning Chat suite receipts cover execution; the rows below describe what
selected assertions establish. They do not establish all branches of a command.

| Command cases | Exact test reference under `packages/friday-chat/tests_chat/` | Inspected behavior / fixture | Remaining limits |
| --- | --- | --- | --- |
| help / aliases | `test_command_registry.py::test_help_includes_every_registered_command_and_alias` | Registry context; asserts generated descriptions, usages, argument descriptions and every registered name/alias appear. | Does not prove dispatch/effect semantics of every command. |
| history, clear | `test_session_memory_commands.py::test_history_and_clear_commands_use_session_state` | In-memory history; checks history text, clear response and empty history. | Durable-memory clear error ordering requires separate evidence. |
| exit alias | `test_session_memory_commands.py::test_exit_alias_requests_app_shutdown` | List input/output app; verifies exit result/shutdown route. | Cleanup/provider failures remain separate app lifecycle obligations. |
| set, vars (remove) | `test_session_memory_commands.py::test_vars_and_set_commands` | In-memory variable assignment/listing. | Former behavior evidence only. Replace supported-name expectations in retirement unit; do not migrate these handlers. |
| agent, agents, status, switch | `test_orchestration_workflow.py::test_switch_agents_agent_and_status_commands` | Fake orchestrator; verifies current name, switch response, active marker, detail and status. | Each invalid/disabled case still needs exact mapping. |
| delegate | `test_orchestration_workflow.py::test_delegate_restores_prior_active_agent_on_success_and_failure` | Fake orchestrator; both successful and missing-agent dispatch restore prior `coder`. | Cancellation/exception ordering beyond these paths remains open. |
| workflow | `test_orchestration_workflow.py::test_workflow_list_run_status_approve_and_skip`, `test_workflow_disabled_and_usage_messages` | Fake workflow; list/run/pending approval/approve/skip, no pending approval, disabled, usage and unknown workflow. | External workflow execution and real approval authority are not proved. |
| tools | `test_tool_commands.py::test_tools_command_lists_and_filters_by_category` | Fake registered tools; verifies utility/memory grouping, utility filter excludes memory tool and missing category lists available categories. | MCP rejection/export diagnostics need their own mapped cases. |
| run-tool (remove) | `test_tool_commands.py::test_run_tool_supports_json_and_plain_text_parameters` | Fake tools; JSON echo and plain-text remember results. | Former behavior only; tool runtime itself remains available independently of retired slash names. |
| security-config | `test_security_speech.py::test_security_config_update_success_and_rollback` | Fake config; successful sensitivity update persists, invalid update reports unchanged and preserves the prior high value. | Full security scanning and other effect paths are separate obligations. |
| read | `test_files_replay_shell.py::test_read_dispatches_supported_extensions`, `test_read_errors_and_malformed_line_limit` | `tmp_path`; reader selection, missing file, directory, unsupported extension and malformed line-limit truncation. | Quoted/space-containing paths and real document readers require separate proof. |
| ingest, list-ingested | `test_files_replay_shell.py::test_ingest_records_source_metadata_and_list_ingested` | Fake memory and temporary Markdown; verifies one chunk, resolved source path, description and listing. | Real persistence, partial ingestion and cancellation remain separate. |
| sessions, transcript | `test_transcript_export_commands.py::test_sessions_and_transcript_commands_use_fake_transcript` | Temporary export dir and fake transcript; one processed turn appears in session count and transcript text. | Store failure and production-query paths are separate tests. |
| transcript export | `test_transcript_export_commands.py::test_transcript_export_writes_database_csv` | `tmp_path`; exactly one export directory, sessions/entries CSV existence and header, output destination. | Collision/partial writes and production store paths need separate mapping. |
| export | `test_transcript_export_commands.py::test_current_session_export_formats` | `tmp_path`; CSV, JSONL, Markdown and training exports create their expected files. | File contents/error ordering need additional exact assertion mapping. |
| lifecycle | `test_maintenance_commands.py::test_lifecycle_precedence_and_missing_access_buffer`, `test_lifecycle_default_is_dry_run` | Fake services; stats precedence, missing buffer response, optimize mode, default cycle/dry run. | Real WAL/store operations and partial failure remain separate. |
| compact | `test_maintenance_commands.py::test_compact_flushes_pending_extraction_before_run`, `test_compact_flush_failure_preserves_pending_turns_and_skips_compactor` | Fake extraction/compaction; ordering and flush failure preserve queued turns and skip compaction. | Provider-backed compaction is not proved. |

## Additional default-branch observations

The [50-case default audit](default-behavior-audit.md) executes every command on
fresh `runtime=None` state and records full outputs and before/after fields.
Notably `/security-test` changes in-memory counters even without a runtime;
`/cls` emits a UI-effect intent and `/exit` changes the exit flag. Preserve these
retained-command observations until a separately approved change says otherwise.

## Work still required

Map exact nodes and assertions for every remaining positive/invalid/unavailable/
cancellation/error obligation and transitive effects. Mark inapplicability only
with a command-specific reason. Review production-adapter tests separately from
fake-runtime tests. These selected rows and default probes do not close P0.
