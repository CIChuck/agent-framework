---
title: Package, API and terminology reference
description: Verified distribution/import mapping, native tool source inventory, public APIs and glossary.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: reference
---

# Package, API and terminology reference

This reference is a navigation layer over current package metadata and source.
Configuration is owned by [the configuration guide](10-configuration.md), CLI
syntax by [the CLI reference](09-cli-reference.md), and dated MCP behavior by
[the migration matrix](19-mcp-migration.md). Keeping one owner per subject
avoids divergent “complete configuration” copies.

## Package map

All 16 workspace packages below declare version 0.1.0a3 and Python>=3.13.4.
The root `friday-framework` distribution is metadata-only: it aggregates a core
cohort and optional integrations, but exposes no `friday_framework` module.
Install only the components/extras your application needs.

| Directory | Distribution | Import |
| --- | --- | --- |
| [friday-agent](../../packages/friday-agent/README.md) | `friday-framework-agent` | `friday_agent` |
| [friday-chat](../../packages/friday-chat/README.md) | `friday-chat` | `friday_chat` |
| [friday-cli](../../packages/friday-cli/README.md) | `friday-framework-cli` | `friday_cli` |
| [friday-core](../../packages/friday-core/README.md) | `friday-framework-core` | `friday_core` |
| [friday-finance](../../packages/friday-finance/README.md) | `friday-framework-finance` | `friday_finance` |
| [friday-llm](../../packages/friday-llm/README.md) | `friday-framework-llm` | `friday_llm` |
| [friday-mcp](../../packages/friday-mcp/README.md) | `friday-framework-mcp` | `friday_mcp` |
| [friday-memory](../../packages/friday-memory/README.md) | `friday-framework-memory` | `friday_memory` |
| [friday-moltbook](../../packages/friday-moltbook/README.md) | `friday-framework-moltbook` | `friday_moltbook` |
| [friday-optimization](../../packages/friday-optimization/README.md) | `friday-framework-optimization` | `friday_opt` |
| [friday-runtime](../../packages/friday-runtime/README.md) | `friday-framework-runtime` | `friday_runtime` |
| [friday-sandbox](../../packages/friday-sandbox/README.md) | `friday-framework-sandbox` | `friday_sandbox` |
| [friday-speech](../../packages/friday-speech/README.md) | `friday-framework-speech` | `friday_speech` |
| [friday-telemetry](../../packages/friday-telemetry/README.md) | `friday-framework-telemetry` | `friday_telemetry` |
| [friday-tools](../../packages/friday-tools/README.md) | `friday-framework-tools` | `friday_tools` |
| [friday-transcript](../../packages/friday-transcript/README.md) | `friday-framework-transcript` | `friday_transcript` |


## Public API entry points

| Need | Entry points | Detailed guide |
| --- | --- | --- |
| Core contracts | `LLMClient`, `EmbeddingModel`, memory adapters, `ToolDefinition`, `ToolRegistry`, `MemoryProfile` | [Architecture](03-core-concepts.md) |
| Model requests | `LiteLLMService`, `ChatCompletionRequest`, `GenerationConfig`, `GenerationOverrides`, typed events | [Advanced integration](11-advanced-topics.md) |
| Model profiles | `ModelLibrary`, service bindings, profile resolution and service specs | [Configuration](10-configuration.md) |
| Memory | `MemoryController`, `ContextAssembler`, `PromptArchitect`, concrete adapters, extraction/maintenance contracts | [Memory](04-adaptive-memory.md) |
| Transcripts | `TranscriptSession`, `TranscriptEntry`, SQLite/JSONL stores and exporters | [Durable transcripts](04-adaptive-memory.md#durable-transcripts) |
| Agents | `AgentProfile`, `AgentLoader`, `AgentRegistry`, `InteractiveAgent`, `AgentOrchestrator` | [Agents](06-agents.md) and [orchestration](07-multi-agent.md) |
| Workflows | `WorkflowLoader`, `WorkflowEngine`, flat/canonical models and dispatch contracts | [Workflows](08-workflows.md) |
| Tools | `FunctionTool`, `FridayTool`, `ToolResult`, `DefaultToolRegistry` | [Tools](05-tools.md) |
| Composition | `RuntimeConfig`, `RuntimeKernel` | [Runtime ownership](03-core-concepts.md#runtime-composition-and-ownership) |
| Telemetry | `TelemetryInterface`, `create_telemetry`, `ManagedTelemetry`, provider/event models | [Telemetry](11-advanced-topics.md#telemetry-ownership-and-exporters) |
| MCP | Dated clients, adapters, modern tools-server APIs | [Client](17-mcp-client.md) / [server](18-mcp-server.md) |
| Speech | `SpeechConfig`, `SpeechService`, `SpeechHarness`, `AdapterRegistry` | [Speech](speech.md) |

An export is not a promise of complete functionality. `AutonomousAgent` raises
`NotImplementedError`, Optimization remains a skeleton, and some integration
tools below are stubs. Inspect [capability status](FRIDAY-FEATURES.md) before
planning an application around a declared name.

## Native tool source catalog

This inventory covers statically named tool classes found in the Tools source
at the reviewed release. It includes alternative classes with the same name;
choose one intentionally rather than registering colliding implementations.
Input fields are names from declared Pydantic models, not a claim that every
field is required. Follow each source link for defaults, validators, inherited
fields and return/error behavior.

“Implementation present” means code is present, **not** that credentials,
dependencies, runtime registration, live operation or safe isolation were
validated. A “stub” raises or returns an explicit unimplemented outcome. Runtime
membership is shown by `/tools`; MCP tools are dynamically discovered and
are not part of this static table.

| Group | Tool name | Class / input fields | Implementation |
| --- | --- | --- | --- |
| archive | `archive_create` | [ArchiveCreateTool](../../packages/friday-tools/src/friday_tools/archive/archive.py); see schema/source | implementation present |
| archive | `archive_extract` | [ArchiveExtractTool](../../packages/friday-tools/src/friday_tools/archive/archive.py); see schema/source | implementation present |
| archive | `archive_list` | [ArchiveListTool](../../packages/friday-tools/src/friday_tools/archive/archive.py); see schema/source | implementation present |
| code | `code_parse_ast` | [CodeParseAstTool](../../packages/friday-tools/src/friday_tools/code/analyze.py); see schema/source | implementation present |
| code | `code_extract_symbols` | [CodeExtractSymbolsTool](../../packages/friday-tools/src/friday_tools/code/analyze.py); see schema/source | implementation present |
| code | `code_format` | [CodeFormatTool](../../packages/friday-tools/src/friday_tools/code/format.py); see schema/source | implementation present |
| code | `code_lint` | [CodeLintTool](../../packages/friday-tools/src/friday_tools/code/format.py); see schema/source | implementation present |
| codegen | `code_generate` | [CodeGenerationTool](../../packages/friday-tools/src/friday_tools/codegen/tool.py); see schema/source | implementation present |
| data | `csv_read` | [CsvReadTool](../../packages/friday-tools/src/friday_tools/data/csv_tools.py); see schema/source | implementation present |
| data | `csv_write` | [CsvWriteTool](../../packages/friday-tools/src/friday_tools/data/csv_tools.py); see schema/source | implementation present |
| data | `json_read` | [JsonReadTool](../../packages/friday-tools/src/friday_tools/data/json_tools.py); see schema/source | implementation present |
| data | `json_write` | [JsonWriteTool](../../packages/friday-tools/src/friday_tools/data/json_tools.py); see schema/source | implementation present |
| data | `json_query` | [JsonQueryTool](../../packages/friday-tools/src/friday_tools/data/json_tools.py); see schema/source | implementation present |
| data | `toml_read` | [TomlReadTool](../../packages/friday-tools/src/friday_tools/data/toml_tools.py); see schema/source | implementation present |
| data | `toml_write` | [TomlWriteTool](../../packages/friday-tools/src/friday_tools/data/toml_tools.py); see schema/source | implementation present |
| data | `xml_read` | [XmlReadTool](../../packages/friday-tools/src/friday_tools/data/xml_tools.py); see schema/source | implementation present |
| data | `xml_query` | [XmlQueryTool](../../packages/friday-tools/src/friday_tools/data/xml_tools.py); see schema/source | implementation present |
| data | `yaml_read` | [YamlReadTool](../../packages/friday-tools/src/friday_tools/data/yaml_tools.py); see schema/source | implementation present |
| data | `yaml_write` | [YamlWriteTool](../../packages/friday-tools/src/friday_tools/data/yaml_tools.py); see schema/source | implementation present |
| encoding | `base64_encode` | [Base64EncodeTool](../../packages/friday-tools/src/friday_tools/encoding/encoding.py); see schema/source | implementation present |
| encoding | `base64_decode` | [Base64DecodeTool](../../packages/friday-tools/src/friday_tools/encoding/encoding.py); see schema/source | implementation present |
| encoding | `hash_compute` | [HashComputeTool](../../packages/friday-tools/src/friday_tools/encoding/encoding.py); see schema/source | implementation present |
| encoding | `uuid_generate` | [UuidGenerateTool](../../packages/friday-tools/src/friday_tools/encoding/encoding.py); see schema/source | implementation present |
| encoding | `url_encode` | [UrlEncodeTool](../../packages/friday-tools/src/friday_tools/encoding/encoding.py); see schema/source | implementation present |
| encoding | `url_decode` | [UrlDecodeTool](../../packages/friday-tools/src/friday_tools/encoding/encoding.py); see schema/source | implementation present |
| execution | `python_execute` | [PythonExecuteTool](../../packages/friday-tools/src/friday_tools/execution/python.py); see schema/source | implementation present |
| execution | `python_execute_unsandboxed` | [UnsandboxedPythonExecuteTool](../../packages/friday-tools/src/friday_tools/execution/unsandboxed_python.py); see schema/source | implementation present |
| filesystem | `directory_list` | [DirectoryListTool](../../packages/friday-tools/src/friday_tools/filesystem/directory.py); path, pattern, show_hidden, sort_by | implementation present |
| filesystem | `directory_list` | [DirectoryListToolLegacy](../../packages/friday-tools/src/friday_tools/filesystem/directory.py); see schema/source | implementation present |
| filesystem | `directory_tree` | [DirectoryTreeTool](../../packages/friday-tools/src/friday_tools/filesystem/directory.py); see schema/source | implementation present |
| filesystem | `directory_create` | [DirectoryCreateTool](../../packages/friday-tools/src/friday_tools/filesystem/directory.py); see schema/source | implementation present |
| filesystem | `file_search` | [FileSearchTool](../../packages/friday-tools/src/friday_tools/filesystem/directory.py); see schema/source | implementation present |
| filesystem | `file_copy` | [FileCopyTool](../../packages/friday-tools/src/friday_tools/filesystem/operations.py); see schema/source | implementation present |
| filesystem | `file_move` | [FileMoveTool](../../packages/friday-tools/src/friday_tools/filesystem/operations.py); see schema/source | implementation present |
| filesystem | `file_delete` | [FileDeleteTool](../../packages/friday-tools/src/friday_tools/filesystem/operations.py); see schema/source | implementation present |
| filesystem | `file_chmod` | [FileChmodTool](../../packages/friday-tools/src/friday_tools/filesystem/operations.py); see schema/source | implementation present |
| filesystem | `file_read` | [FileReadTool](../../packages/friday-tools/src/friday_tools/filesystem/read.py); path, encoding, start_line, max_lines | implementation present |
| filesystem | `file_read_lines` | [FileReadLinesTool](../../packages/friday-tools/src/friday_tools/filesystem/read.py); see schema/source | implementation present |
| filesystem | `file_info` | [FileInfoTool](../../packages/friday-tools/src/friday_tools/filesystem/read.py); see schema/source | implementation present |
| filesystem | `file_grep` | [FileGrepTool](../../packages/friday-tools/src/friday_tools/filesystem/read.py); see schema/source | implementation present |
| filesystem | `smart_read` | [SmartFileReadTool](../../packages/friday-tools/src/friday_tools/filesystem/smart_read.py); path, add_to_context, store_to_memory, description, force_chunked, force_reprocess | implementation present |
| filesystem | `file_write` | [FileWriteTool](../../packages/friday-tools/src/friday_tools/filesystem/write.py); path, content, mode, overwrite, encoding, create_dirs | implementation present |
| filesystem | `file_append` | [FileAppendTool](../../packages/friday-tools/src/friday_tools/filesystem/write.py); see schema/source | implementation present |
| filesystem | `file_insert` | [FileInsertTool](../../packages/friday-tools/src/friday_tools/filesystem/write.py); see schema/source | implementation present |
| filesystem | `file_replace` | [FileReplaceTool](../../packages/friday-tools/src/friday_tools/filesystem/write.py); see schema/source | implementation present |
| filesystem | `file_patch` | [FilePatchTool](../../packages/friday-tools/src/friday_tools/filesystem/write.py); see schema/source | implementation present |
| finance | `get_market_data` | [GetMarketDataTool](../../packages/friday-tools/src/friday_tools/finance/massive.py); see schema/source | implementation present |
| finance | `get_crypto_data` | [GetCryptoDataTool](../../packages/friday-tools/src/friday_tools/finance/massive.py); see schema/source | implementation present |
| finance | `get_technical_analysis` | [GetTechnicalAnalysisTool](../../packages/friday-tools/src/friday_tools/finance/massive.py); see schema/source | implementation present |
| git | `git_branch_list` | [GitBranchListTool](../../packages/friday-tools/src/friday_tools/git/branches.py); see schema/source | implementation present |
| git | `git_branch_create` | [GitBranchCreateTool](../../packages/friday-tools/src/friday_tools/git/branches.py); see schema/source | implementation present |
| git | `git_checkout` | [GitCheckoutTool](../../packages/friday-tools/src/friday_tools/git/branches.py); see schema/source | implementation present |
| git | `git_add` | [GitAddTool](../../packages/friday-tools/src/friday_tools/git/staging.py); see schema/source | implementation present |
| git | `git_commit` | [GitCommitTool](../../packages/friday-tools/src/friday_tools/git/staging.py); see schema/source | implementation present |
| git | `git_stash` | [GitStashTool](../../packages/friday-tools/src/friday_tools/git/staging.py); see schema/source | implementation present |
| git | `git_status` | [GitStatusTool](../../packages/friday-tools/src/friday_tools/git/status.py); see schema/source | implementation present |
| git | `git_diff` | [GitDiffTool](../../packages/friday-tools/src/friday_tools/git/status.py); see schema/source | implementation present |
| git | `git_log` | [GitLogTool](../../packages/friday-tools/src/friday_tools/git/status.py); see schema/source | implementation present |
| git | `git_show` | [GitShowTool](../../packages/friday-tools/src/friday_tools/git/status.py); see schema/source | implementation present |
| integrations | `calendar_create_event` | [CalendarCreateEventTool](../../packages/friday-tools/src/friday_tools/integrations/calendar.py); see schema/source | stub |
| integrations | `calendar_list_events` | [CalendarListEventsTool](../../packages/friday-tools/src/friday_tools/integrations/calendar.py); see schema/source | stub |
| integrations | `database_query` | [DatabaseQueryTool](../../packages/friday-tools/src/friday_tools/integrations/database.py); see schema/source | stub |
| integrations | `email_send` | [EmailSendTool](../../packages/friday-tools/src/friday_tools/integrations/email.py); see schema/source | stub |
| integrations | `moltbook_register_agent` | [MoltbookRegisterAgentTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_get_my_profile` | [MoltbookGetMyProfileTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_get_claim_status` | [MoltbookGetClaimStatusTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_update_profile` | [MoltbookUpdateProfileTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_upload_avatar` | [MoltbookUploadAvatarTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_delete_avatar` | [MoltbookDeleteAvatarTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_get_agent_profile` | [MoltbookGetAgentProfileTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_create_post` | [MoltbookCreatePostTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_create_link_post` | [MoltbookCreateLinkPostTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_get_feed` | [MoltbookGetFeedTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_get_submolt_posts` | [MoltbookGetSubmoltPostsTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_get_submolt_feed` | [MoltbookGetSubmoltFeedTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_get_post` | [MoltbookGetPostTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_delete_post` | [MoltbookDeletePostTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_add_comment` | [MoltbookAddCommentTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_reply_to_comment` | [MoltbookReplyToCommentTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_get_comments` | [MoltbookGetCommentsTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_upvote_post` | [MoltbookUpvotePostTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_downvote_post` | [MoltbookDownvotePostTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_upvote_comment` | [MoltbookUpvoteCommentTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_create_submolt` | [MoltbookCreateSubmoltTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_list_submolts` | [MoltbookListSubmoltsTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_get_submolt` | [MoltbookGetSubmoltTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_subscribe_submolt` | [MoltbookSubscribeSubmoltTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_unsubscribe_submolt` | [MoltbookUnsubscribeSubmoltTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_follow_agent` | [MoltbookFollowAgentTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_unfollow_agent` | [MoltbookUnfollowAgentTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_get_personal_feed` | [MoltbookGetPersonalFeedTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_search` | [MoltbookSearchTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_pin_post` | [MoltbookPinPostTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_unpin_post` | [MoltbookUnpinPostTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_update_submolt_settings` | [MoltbookUpdateSubmoltSettingsTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_upload_submolt_avatar` | [MoltbookUploadSubmoltAvatarTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_upload_submolt_banner` | [MoltbookUploadSubmoltBannerTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_add_moderator` | [MoltbookAddModeratorTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_remove_moderator` | [MoltbookRemoveModeratorTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `moltbook_list_moderators` | [MoltbookListModeratorsTool](../../packages/friday-tools/src/friday_tools/integrations/moltbook.py); see schema/source | implementation present |
| integrations | `slack_send` | [SlackSendTool](../../packages/friday-tools/src/friday_tools/integrations/slack.py); see schema/source | stub |
| integrations | `webhook_call` | [WebhookCallTool](../../packages/friday-tools/src/friday_tools/integrations/webhook.py); see schema/source | stub |
| math | `calculator` | [CalculatorTool](../../packages/friday-tools/src/friday_tools/math/math.py); see schema/source | implementation present |
| math | `unit_convert` | [UnitConvertTool](../../packages/friday-tools/src/friday_tools/math/math.py); see schema/source | implementation present |
| math | `date_parse` | [DateParseTool](../../packages/friday-tools/src/friday_tools/math/math.py); see schema/source | implementation present |
| math | `date_format` | [DateFormatTool](../../packages/friday-tools/src/friday_tools/math/math.py); see schema/source | implementation present |
| math | `date_calculate` | [DateCalculateTool](../../packages/friday-tools/src/friday_tools/math/math.py); see schema/source | implementation present |
| memory | `memory_stats` | [MemoryStatsTool](../../packages/friday-tools/src/friday_tools/memory/inspection.py); session_id | implementation present |
| memory | `graph_inspect` | [GraphInspectionTool](../../packages/friday-tools/src/friday_tools/memory/inspection.py); limit, node_type | implementation present |
| memory | `vector_inspect` | [VectorInspectionTool](../../packages/friday-tools/src/friday_tools/memory/inspection.py); limit, doc_type, query | implementation present |
| memory | `memory_lifecycle` | [LifecycleTool](../../packages/friday-tools/src/friday_tools/memory/lifecycle.py); action, dry_run | implementation present |
| memory | `memory_maintain` | [MemoryMaintenanceTool](../../packages/friday-tools/src/friday_tools/memory/maintenance.py); operation, dry_run, backup_first | implementation present |
| memory | `memory_reset` | [MemoryResetTool](../../packages/friday-tools/src/friday_tools/memory/maintenance.py); confirm, session_id | implementation present |
| shell | `command_execute` | [CommandExecuteTool](../../packages/friday-tools/src/friday_tools/shell/command.py); command, cwd, timeout, env | implementation present |
| shell | `shell_execute` | [ShellExecuteTool](../../packages/friday-tools/src/friday_tools/shell/execute.py); see schema/source | implementation present |
| shell | `shell_script` | [ShellScriptTool](../../packages/friday-tools/src/friday_tools/shell/execute.py); see schema/source | implementation present |
| shell | `process_list` | [ProcessListTool](../../packages/friday-tools/src/friday_tools/shell/system.py); see schema/source | implementation present |
| shell | `process_kill` | [ProcessKillTool](../../packages/friday-tools/src/friday_tools/shell/system.py); see schema/source | implementation present |
| shell | `environment_get` | [EnvironmentGetTool](../../packages/friday-tools/src/friday_tools/shell/system.py); see schema/source | implementation present |
| shell | `system_info` | [SystemInfoTool](../../packages/friday-tools/src/friday_tools/shell/system.py); see schema/source | implementation present |
| system | `system_health` | [SystemHealthTool](../../packages/friday-tools/src/friday_tools/system/health.py); check_disk | implementation present |
| system | `transcript_tool` | [TranscriptTool](../../packages/friday-tools/src/friday_tools/system/transcript.py); action, format, session_id, output_dir | implementation present |
| text | `markdown_to_text` | [MarkdownToTextTool](../../packages/friday-tools/src/friday_tools/text/convert.py); see schema/source | implementation present |
| text | `html_to_markdown` | [HtmlToMarkdownTool](../../packages/friday-tools/src/friday_tools/text/convert.py); see schema/source | implementation present |
| text | `text_search` | [TextSearchTool](../../packages/friday-tools/src/friday_tools/text/search.py); see schema/source | implementation present |
| text | `text_extract` | [TextExtractTool](../../packages/friday-tools/src/friday_tools/text/search.py); see schema/source | implementation present |
| text | `text_replace` | [TextReplaceTool](../../packages/friday-tools/src/friday_tools/text/transform.py); see schema/source | implementation present |
| text | `text_split` | [TextSplitTool](../../packages/friday-tools/src/friday_tools/text/transform.py); see schema/source | implementation present |
| text | `text_join` | [TextJoinTool](../../packages/friday-tools/src/friday_tools/text/transform.py); see schema/source | implementation present |
| text | `text_template` | [TextTemplateTool](../../packages/friday-tools/src/friday_tools/text/transform.py); see schema/source | implementation present |
| utility | `get_current_datetime` | [GetCurrentDateTimeTool](../../packages/friday-tools/src/friday_tools/utility/datetime.py); timezone_name, format | implementation present |
| utility | `echo` | [EchoTool](../../packages/friday-tools/src/friday_tools/utility/echo.py); message | implementation present |
| web | `web_fetch` | [WebFetchTool](../../packages/friday-tools/src/friday_tools/web/fetch.py); see schema/source | implementation present |
| web | `web_screenshot` | [WebScreenshotTool](../../packages/friday-tools/src/friday_tools/web/fetch.py); see schema/source | stub |
| web | `web_extract_links` | [WebExtractLinksTool](../../packages/friday-tools/src/friday_tools/web/fetch.py); see schema/source | implementation present |
| web | `web_extract_text` | [WebExtractTextTool](../../packages/friday-tools/src/friday_tools/web/fetch.py); see schema/source | implementation present |
| web | `http_get` | [HttpGetTool](../../packages/friday-tools/src/friday_tools/web/http.py); see schema/source | implementation present |
| web | `http_post` | [HttpPostTool](../../packages/friday-tools/src/friday_tools/web/http.py); see schema/source | implementation present |
| web | `http_put` | [HttpPutTool](../../packages/friday-tools/src/friday_tools/web/http.py); see schema/source | implementation present |
| web | `http_delete` | [HttpDeleteTool](../../packages/friday-tools/src/friday_tools/web/http.py); see schema/source | implementation present |
| web | `http_download` | [HttpDownloadTool](../../packages/friday-tools/src/friday_tools/web/http.py); see schema/source | implementation present |
| web | `http_upload` | [HttpUploadTool](../../packages/friday-tools/src/friday_tools/web/http.py); see schema/source | implementation present |
| web | `web_reader` | [WebReaderTool](../../packages/friday-tools/src/friday_tools/web/reader.py); see schema/source | implementation present |
| web | `web_search` | [WebSearchTool](../../packages/friday-tools/src/friday_tools/web/search.py); see schema/source | implementation present |
| web | `serper_search` | [SerperSearchTool](../../packages/friday-tools/src/friday_tools/web/serper.py); see schema/source | implementation present |


## Configuration and example conventions

Guides label complete offline Python examples, complete configuration files,
schema fragments and live examples. A fragment belongs at the stated location;
it is not an independent application configuration. External endpoints/model
identifiers are operator-selected examples unless explicitly verified otherwise.

All guide metadata records the framework release and actual review date.
`status: current` describes the guide's implementation basis; it does not
assert production certification, lifecycle acceptance or a new release.
Source and accepted specifications control when prose disagrees.

## Migration reference

| Old assumption | Current action |
| --- | --- |
| Run the retired memory integration script | Use `friday-chat` with explicit configuration |
| Import directory/distribution names directly | Use the package map above |
| Configure all providers through one flat LLM block | Prefer canonical model-library profiles and role bindings |
| Treat local chat as all-local processing | Review extraction, embeddings, tools, speech and exporters separately |
| Treat HTTP+SSE as the newest MCP transport | Select dated stdio or Streamable HTTP profiles explicitly |
| Enable Langfuse through new local telemetry | New provider-neutral Langfuse remains queued; legacy callbacks differ |
| Use Optimization's knapsack/DSPy helpers | No implemented optimization API is shipped |
| Delete database locks to repair recall | Inspect owners, quiesce and use supported recovery |

For MCP wire/profile transitions, use [the dedicated migration guide](19-mcp-migration.md).
For old/new generation controls, use [the model-library contract](../reference/llm/model-library-technical-spec.md).
No universal all-store migration script or future release-date promise is
provided by this guide.

## Glossary

| Term | Meaning in Friday |
| --- | --- |
| Application | The host that owns configuration, authorization, lifecycle and paths |
| Profile | Agent identity/selection configuration, or a model-library model definition; context distinguishes them |
| Service role | An application name bound to a chat/embedding profile |
| Episodic memory | Conversation-turn history |
| Semantic memory | Text/metadata retrieved through embeddings |
| Associative memory | Entity/relationship graph |
| Priming | Initial context retrieval, optionally including earlier-session turns |
| Context payload | Retrieved/filtered/pruned material before final model message formatting |
| Compaction | Summarization/deduplication/promotion work intended to reduce future context load |
| Lifecycle decay | Stage/retention scoring based on configured access/age rules |
| Inclusion score | Retrieval priority combining similarity, age and usage; not factual confidence |
| Provenance | Source/author/time/trust metadata attached to a record or operation |
| Namespace | An application-defined visibility partition, not authentication by itself |
| Handoff | Explicit result/artifact/context passed between tasks or agents |
| Canonical workflow | Workflow/pipeline/task hierarchy with explicit contracts |
| Quiescence | A coordinated state in which relevant owners cannot mutate the snapshot/restore participants |
| Borrowed provider | A dependency whose lifecycle remains owned by the caller |
| Closed telemetry event | A validated categorical schema with bounded allowed fields |
| MCP profile | Friday's explicitly bounded dated protocol/transport/role support |
| MRTR | Multi-round tool request continuation; not implemented in Friday's current MCP profile |

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)
