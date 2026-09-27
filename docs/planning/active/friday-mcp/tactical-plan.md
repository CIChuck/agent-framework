# Friday Framework MCP Tactical Implementation Plan

Status: WS-00 approved 2026-09-27; later workstreams draft

Date: 2026-07-24  
Source build plan: [friday-framework-mcp-enhancements.md](build-plan.md)

## Source Authority And Precedence

1. [Repository engineering policy](../../../reference/policies/repository-engineering-policy.md) is the code-quality and governance authority for implementation.
2. [Friday Framework MCP enhancements build plan](build-plan.md) is the feature and architectural authority for this work.
3. [Tactical implementation planner skill](../../../dev-skills/tactical-implementation-planner.md) is the planning-format authority for this document.
4. Current package source is the implementation-reality authority when older documentation conflicts with code.

`docs/methodology/constitution/gendev.md` was referenced by the planner skill but is not present in this checkout. If that file is restored later, this plan should be reviewed against it before implementation starts.

## Implementation Objective

Introduce MCP client capability into the Friday Framework through the existing runtime, tool, memory, and Friday Chat architecture without creating a second configuration authority. The implementation must support configurable MCP tool discovery, runtime registration, per-turn tool budget management, provenance-aware tool execution, optional memory ingestion, telemetry, diagnostics, and end-user documentation.

The first implementation pass is tools-only. MCP resources, prompts, subscriptions, server exposure, automatic discovery refresh, and external MCP config includes are deferred unless explicitly activated by later phases.

## Assumptions

- Canonical MCP configuration lives under `tools.providers.mcp` in the current config architecture.
- `config_file` support is deferred and must be rejected with a clear validation error until the optional external include phase.
- MCP server failures are optional by default; `required: true` converts connection or discovery failure into startup failure.
- MCP discovery runs at startup only in the first pass.
- MCP include and exclude filters match canonical prefixed Friday tool names in the first pass.
- Default long-term memory ingestion for MCP outputs is disabled.
- Tool schemas, tool descriptions, tool arguments, tool results, telemetry, diagnostics, and memory payloads are treated as untrusted until sanitized or redacted.
- Implementation should remove `# mypy: ignore-errors` from touched MCP source files when practical and must not add new broad suppressions under `packages/*/src`.

## Non-Goals

- Do not implement MCP resource or prompt ingestion in the first pass.
- Do not implement automatic live MCP server refresh in the first pass.
- Do not expose Friday as an MCP server as part of this client enhancement.
- Do not create a separate MCP-only config authority.
- Do not persist raw MCP tool outputs to long-term memory by default.
- Do not perform broad package refactors unrelated to the MCP contracts and integration path.
- Do not clean or delete generated state such as `.friday/`, Chroma databases, transcripts, caches, or local config.

## Global Stop Conditions

- Stop if the chosen shared contract ownership would create circular imports or force implementation through incidental private details.
- Stop if MCP provider loading cannot be made compatible with the runtime async lifecycle without changing public runtime startup semantics.
- Stop if budget enforcement cannot reserve a minimum memory context floor for Friday Chat turns.
- Stop if security requirements would require passing complete unredacted config, secrets, or local state paths into an MCP server.
- Stop if a requested implementation step conflicts with repository policy.

## Workstream Dependency Map

1. `MCP-WS-00` establishes contracts, defaults, and unresolved policy decisions.
2. `MCP-WS-01` implements strict configuration parsing and validation.
3. `MCP-WS-02` implements runtime lifecycle and provider loading.
4. `MCP-WS-03` implements tool naming, metadata, filtering, and registry integration.
5. `MCP-WS-04` integrates Friday Chat tool selection and context budget management.
6. `MCP-WS-05` implements execution provenance, transcript metadata, and result handling.
7. `MCP-WS-06` integrates optional memory ingestion and memory retrieval budgeting.
8. `MCP-WS-07` adds telemetry, diagnostics, and operational health surfaces.
9. `MCP-WS-08` completes documentation and guide updates.
10. `MCP-WS-09` is the deferred optional external MCP config include phase.

## MCP-WS-00: Contract And Policy Foundation

### Purpose

Define the shared typed contracts and final defaults needed before touching runtime loading, Friday Chat turns, transcript recording, or memory ingestion. The [current-code rebaseline](rebaseline-2026-09-27.md) credits the existing standalone package and limits this workstream to contract/default changes.

### Implementation Tasks

- `MCP-00-01`: Choose package ownership for shared MCP DTOs. Candidate owners are `friday-core` for cross-package protocols and DTOs, or `friday-mcp` for MCP-specific models with exported stable interfaces.
- `MCP-00-02`: Define `MCPClientLimits`, `MCPClientSecurityPolicy`, `MCPIngestionPolicy`, `MCPDiscoveryPolicy`, `MCPServerRuntimePolicy`, `MCPToolMetadata`, `MCPToolCallProvenance`, `MCPDiscoveryState`, and `MCPProviderDiagnostics`.
- `MCP-00-03`: Decide the tool metadata representation: extend the existing tool protocol, add a registry sidecar, or expose metadata through a wrapper protocol.
- `MCP-00-04`: Set first-pass default limits for server count, tools per server, total tools, schema bytes per tool, aggregate schema token budget, result bytes, connection timeout, tool timeout, and minimum memory retrieval floor.
- `MCP-00-05`: Define deterministic tool-name normalization and collision behavior for `mcp_<server_name>_<tool_name>`.
- `MCP-00-06`: Define argument redaction and hashing policy, including whether hashes are salted and where salt configuration lives.
- `MCP-00-07`: Define first-pass SSE trust posture and whether SSE is disabled, allowed with explicit trust configuration, or allowed with stricter defaults.
- `MCP-00-08`: Record a policy cleanup checklist for touched files that currently use `# mypy: ignore-errors`.

### Affected Areas

- `packages/friday-core/src/friday_core/interfaces/`
- `packages/friday-core/src/friday_core/`
- `packages/friday-mcp/src/friday_mcp/`
- Focused tests in `packages/friday-core/tests_core/` and
  `packages/friday-mcp/tests_mcp/`.
- Runtime, Friday Chat, memory, and transcript are **later consumers**, not
  WS-00 edit targets.

### Required Tests

- Unit tests for DTO validation, defaults, serialization, redaction flags, and name normalization.
- Negative tests for invalid names, duplicate normalized names, invalid limits, unknown enum values, and unsafe defaults.
- Focused mypy checks for the package owning the contracts and any package importing them.

### Acceptance Criteria

- Shared contracts are importable without circular dependencies.
- Defaults are explicit and documented in tests.
- Tool metadata representation is chosen before runtime registration work begins.
- Budget defaults include a minimum memory retrieval floor.
- Security policy defaults do not allow unredacted secrets or raw outputs into telemetry, diagnostics, transcript exports, or memory.

### Dependencies

None.

### Non-Goals

- Do not implement runtime loading in this workstream.
- Do not implement Friday Chat turn behavior in this workstream.

## MCP-WS-01: Configuration Model And Validation

### Purpose

Make the canonical `tools.providers.mcp` config shape strict, typed, and compatible with current runtime configuration.

### Implementation Tasks

- `MCP-01-01`: Extend MCP config models with `enabled`, `mode`, `include_tools`, `exclude_tools`, `config.auto_connect`, `tool_name_prefix`, `discovery`, `limits`, `security`, `ingestion`, and `servers`.
- `MCP-01-02`: Extend server config with `required`, `transport`, `command`, `args`, `env`, `cwd`, `timeout_seconds`, `tool_timeout_seconds`, `retry_attempts`, and `trust_level`.
- `MCP-01-03`: Reject `config_file` with a clear validation error until `MCP-WS-09`.
- `MCP-01-04`: Reject unknown MCP provider keys instead of silently ignoring them.
- `MCP-01-05`: Validate duplicate server names, disabled servers, invalid transports, missing stdio commands, unsafe cwd values, invalid timeout values, invalid limits, and invalid include/exclude combinations.
- `MCP-01-06`: Define config precedence for runtime config, explicit construction overrides, permitted environment overrides, and Friday Chat aliases after canonical normalization.
- `MCP-01-07`: Add config examples for disabled MCP, one stdio server, optional server failure, required server failure, strict include filters, and rejected `config_file`.

### Affected Areas

- `packages/friday-mcp/src/friday_mcp/config.py`
- `packages/friday-runtime/src/friday_runtime/config.py`
- `packages/friday-runtime/tests_runtime/`
- `packages/friday-mcp/tests_mcp/`
- Example config templates used by Friday Chat desktop installation.

### Required Tests

- Runtime config parsing tests for the canonical MCP shape.
- Negative tests for unknown provider keys and rejected `config_file`.
- Negative tests for required stdio fields, invalid paths, duplicate names, invalid limit values, and invalid trust levels.
- Round-trip tests for config DTOs.

### Acceptance Criteria

- `RuntimeConfig` can parse canonical MCP config into typed models.
- Unsupported future config is rejected with actionable messages.
- Existing non-MCP tool provider config continues to behave as before.
- Tests prove Friday Chat can normalize or consume the same canonical MCP config model.

### Dependencies

- Depends on `MCP-WS-00`.

### Non-Goals

- Do not connect to MCP servers in this workstream.
- Do not implement external include loading in this workstream.

## MCP-WS-02: Runtime Lifecycle And MCP Provider Loading

### Purpose

Integrate MCP client discovery into runtime startup and shutdown while preserving existing runtime composition semantics.

### Implementation Tasks

- `MCP-02-01`: Replace or augment synchronous `register_runtime_tools` behavior so MCP providers can be loaded through the async runtime boot lifecycle.
- `MCP-02-02`: Add an MCP provider loader that creates and owns an `MCPClientManager` for the runtime lifetime.
- `MCP-02-03`: Implement startup order: configure services, connect enabled MCP servers, list tools, apply discovery caps, register accepted tools, validate agent tool bindings.
- `MCP-02-04`: Implement shutdown order that disconnects MCP clients even when startup partially fails.
- `MCP-02-05`: Implement optional versus required server behavior.
- `MCP-02-06`: Add connection and discovery timeout handling.
- `MCP-02-07`: Add bounded discovery concurrency.
- `MCP-02-08`: Preserve diagnostics for failed optional servers without registering their tools.

### Affected Areas

- `packages/friday-runtime/src/friday_runtime/di.py`
- `packages/friday-runtime/src/friday_runtime/kernel.py`
- `packages/friday-runtime/src/friday_runtime/tool_loading.py`
- `packages/friday-runtime/src/friday_runtime/tools.py`
- `packages/friday-mcp/src/friday_mcp/client/manager.py`
- `packages/friday-mcp/src/friday_mcp/client/adapter.py`

### Required Tests

- Runtime boot tests for MCP disabled, MCP enabled with no servers, optional server failure, required server failure, partial success, discovery timeout, and shutdown cleanup.
- Integration tests with a fake stdio MCP server.
- Negative tests proving tools are not registered for failed servers.
- Mypy and ruff on touched runtime and MCP modules.

### Acceptance Criteria

- MCP enabled no longer raises an intentional unsupported error.
- Optional server failures do not block runtime startup.
- Required server failures fail startup with clear diagnostics.
- Runtime shutdown disconnects MCP clients.
- Existing native tool registration behavior remains compatible.

### Dependencies

- Depends on `MCP-WS-00` and `MCP-WS-01`.

### Non-Goals

- Do not add live refresh or reload behavior.
- Do not add MCP resources or prompts.

## MCP-WS-03: Tool Naming, Metadata, Filtering, And Registry Integration

### Purpose

Convert discovered MCP tools into Friday tool registry entries with deterministic names, metadata, budget visibility, and strict filtering.

### Implementation Tasks

- `MCP-03-01`: Implement deterministic canonical tool names using `tool_name_prefix`, server name, and original tool name.
- `MCP-03-02`: Fail discovery or registration on normalized name collisions with server and tool details in diagnostics.
- `MCP-03-03`: Attach metadata that records provider type, server name, original tool name, transport, trust level, schema size, and discovery state.
- `MCP-03-04`: Apply `include_tools` and `exclude_tools` against canonical prefixed names.
- `MCP-03-05`: Change filtering behavior so missing requested include tools are diagnosable and can fail when policy requires.
- `MCP-03-06`: Enforce `max_tools_per_server`, `max_total_tools`, `max_schema_bytes_per_tool`, and aggregate schema budget before registry registration.
- `MCP-03-07`: Sanitize tool names, descriptions, and schemas at registration time.
- `MCP-03-08`: Verify that registered MCP tools satisfy the current Friday tool protocol, including `category`, `tags`, `execute`, and `to_schema`.

### Affected Areas

- `packages/friday-core/src/friday_core/interfaces/tools.py`
- `packages/friday-runtime/src/friday_runtime/tool_loading.py`
- `packages/friday-runtime/src/friday_runtime/tools.py`
- `packages/friday-mcp/src/friday_mcp/client/adapter.py`
- `packages/friday-mcp/src/friday_mcp/client/manager.py`
- `packages/friday-tools/src/friday_tools/`

### Required Tests

- Unit tests for canonical naming, collision detection, filter matching, missing include diagnostics, metadata attachment, schema sanitization, and cap enforcement.
- Integration tests proving native and MCP tools can coexist in one registry.
- Negative tests for oversized schemas, duplicate names, unsafe schema descriptions, and missing protocol properties.

### Acceptance Criteria

- Registered MCP tools have deterministic stable names.
- Every registered MCP tool carries inspectable provenance metadata.
- Provider filters are predictable and diagnosable.
- Oversized or unsafe tools are skipped or rejected according to policy before they reach turn context.

### Dependencies

- Depends on `MCP-WS-00`, `MCP-WS-01`, and `MCP-WS-02`.

### Non-Goals

- Do not implement per-turn ranking in this workstream.
- Do not implement transcript or memory persistence in this workstream.

## MCP-WS-04: Friday Chat Tool Context And Budget Management

### Purpose

Make Friday Chat MCP-aware so tool schemas, memory retrieval, output reservation, and per-turn context assembly share one explicit budget.

### Implementation Tasks

- `MCP-04-01`: Bridge Friday Chat config to the canonical runtime MCP provider config without introducing a second MCP shape.
- `MCP-04-02`: Include MCP tools in Friday Chat tool selection through the existing registry abstraction.
- `MCP-04-03`: Enforce per-turn selected tool count and aggregate schema token budget.
- `MCP-04-04`: Implement the budget formula: context window minus output buffer, system prompt tokens, selected tool schema tokens, reserved tool result tokens, and minimum memory retrieval floor.
- `MCP-04-05`: Reduce selected MCP tools before reducing memory below the configured floor.
- `MCP-04-06`: Fail a turn with a clear diagnostic when selected required tools cannot fit within budget.
- `MCP-04-07`: Improve schema-token estimation or isolate it behind a replacement-ready estimator interface.
- `MCP-04-08`: Add user-visible diagnostics for skipped MCP tools caused by budget, security, or discovery state.

### Affected Areas

- `packages/friday-chat/src/friday_chat/config.py`
- `packages/friday-chat/src/friday_chat/turns/processor.py`
- `packages/friday-chat/src/friday_chat/tools/`
- `packages/friday-chat/tests_chat/`
- `packages/friday-runtime/src/friday_runtime/config.py`

### Required Tests

- Unit tests for budget calculation with no tools, native tools only, MCP tools only, mixed tools, oversized schemas, and reserved result tokens.
- Negative tests for memory floor exhaustion and required tool over-budget behavior.
- Friday Chat turn tests proving memory retrieval receives the reduced token limit.
- Regression tests proving existing non-MCP chat turns are unchanged.

### Acceptance Criteria

- Friday Chat does not blindly include all discovered MCP tools in the turn prompt.
- Tool schema budget is subtracted before memory retrieval.
- Memory retrieval never drops below the configured floor unless the turn fails intentionally.
- Budget decisions are explainable through diagnostics.

### Dependencies

- Depends on `MCP-WS-00` through `MCP-WS-03`.

### Non-Goals

- Do not implement long-term memory ingestion here.
- Do not add a web UI for MCP configuration here.

## MCP-WS-05: Tool Execution Security, Provenance, And Transcript Recording

### Purpose

Ensure MCP tool execution outputs are bounded, sanitized, traceable, and stored with enough provenance for debugging and later memory policy decisions.

### Implementation Tasks

- `MCP-05-01`: Extend or replace Friday Chat `ToolCallRecord` to include provider provenance, server name, original tool name, canonical tool name, transport, call ID, trust level, sanitization status, truncation status, and result size.
- `MCP-05-02`: Redact or hash arguments before diagnostics, transcript persistence, telemetry, or memory ingestion.
- `MCP-05-03`: Enforce `max_result_bytes` before tool results are passed back to the model.
- `MCP-05-04`: Sanitize MCP tool outputs before model re-entry.
- `MCP-05-05`: Add per-call metadata distinct from turn-level metadata.
- `MCP-05-06`: Persist MCP provenance in transcript entries and preserve it in JSONL export.
- `MCP-05-07`: Decide whether Markdown and CSV transcript exporters include summarized MCP provenance by default.
- `MCP-05-08`: Ensure failed MCP calls record failure provenance without leaking secrets or raw unsafe output.

### Affected Areas

- `packages/friday-chat/src/friday_chat/tools/schemas.py`
- `packages/friday-chat/src/friday_chat/turns/processor.py`
- `packages/friday-chat/src/friday_chat/tools/`
- `packages/friday-transcript/src/friday_transcript/models/transcript.py`
- `packages/friday-transcript/src/friday_transcript/export/`
- `packages/friday-agent/src/friday_agent/security/output_processor.py`

### Required Tests

- Unit tests for provenance construction, argument redaction, argument hashing, result truncation, output sanitization, and failed-call records.
- Transcript serialization tests for MCP provenance.
- Exporter tests for JSONL and any chosen Markdown or CSV provenance representation.
- Negative tests for secret-like argument values, oversized outputs, unsafe output content, and tool failure paths.

### Acceptance Criteria

- MCP tool results cannot exceed configured size limits before model re-entry.
- Unsafe output is sanitized before prompt assembly.
- Transcript records distinguish native tools from MCP tools.
- Argument and output handling does not leak secrets into telemetry, diagnostics, or exports.

### Dependencies

- Depends on `MCP-WS-00`, `MCP-WS-03`, and `MCP-WS-04`.

### Non-Goals

- Do not enable long-term memory ingestion by default.
- Do not preserve unsanitized raw outputs outside an explicit quarantine policy.

## MCP-WS-06: Memory Compatibility And Optional MCP Ingestion

### Purpose

Make MCP compatible with Friday memory retrieval and optional long-term memory ingestion while preserving context budgets and provenance.

### Implementation Tasks

- `MCP-06-01`: Add memory-facing MCP provenance fields for `source_type=mcp_tool`, server name, tool name, call ID, transcript entry ID, memory record ID, trust level, ingestion policy, and truncation status.
- `MCP-06-02`: Keep long-term MCP output ingestion disabled by default.
- `MCP-06-03`: Implement per-server and per-tool ingestion allowlists if ingestion is enabled.
- `MCP-06-04`: Apply memory sanitization and quarantine policy before storing MCP outputs.
- `MCP-06-05`: Record freshness and revocation assumptions for ingested MCP outputs.
- `MCP-06-06`: Ensure retrieval budget calculation accounts for selected tool schema tokens and reserved result tokens.
- `MCP-06-07`: Add query-time provenance labels so MCP-derived memories can be distinguished from conversation, file, and native tool memory.

### Affected Areas

- `packages/friday-memory/src/friday_memory/`
- `packages/friday-chat/src/friday_chat/turns/processor.py`
- `packages/friday-chat/src/friday_chat/memory/`
- `packages/friday-transcript/src/friday_transcript/models/transcript.py`
- `packages/friday-core/src/friday_core/`

### Required Tests

- Unit tests for ingestion disabled by default, ingestion allowlists, provenance labels, sanitization, quarantine, and retrieval budget inputs.
- Integration tests for an MCP tool output flowing into transcript but not memory by default.
- Integration tests for explicit ingestion into memory with provenance and retrieval labels.
- Negative tests for untrusted outputs, oversized outputs, missing provenance, disabled ingestion, and revoked or stale-source metadata.

### Acceptance Criteria

- MCP tool outputs are not stored in long-term memory unless explicitly enabled.
- Memory records created from MCP outputs carry enough provenance to audit source and trust.
- Friday Chat memory retrieval receives a budget reduced by tool-schema and result reservations.
- MCP-derived memories can be excluded, filtered, or identified later.

### Dependencies

- Depends on `MCP-WS-04` and `MCP-WS-05`.

### Non-Goals

- Do not ingest MCP resources or prompts.
- Do not implement automatic revocation from remote MCP source changes.

## MCP-WS-07: Telemetry, Diagnostics, And Health Surfaces

### Purpose

Expose enough operational visibility to debug MCP startup, discovery, registration, execution, budget trimming, and ingestion decisions without leaking secrets or unsafe content.

### Implementation Tasks

- `MCP-07-01`: Add telemetry events for server connection, list-tools, skipped tool, registered tool, tool call start, tool call finish, tool call failure, ingestion decision, and disconnect.
- `MCP-07-02`: Ensure telemetry excludes secrets, raw arguments, raw outputs, unredacted environment variables, headers, and unsanitized schemas.
- `MCP-07-03`: Add runtime diagnostics for optional server failures, required server failures, discovery caps, schema caps, budget skips, and registration collisions.
- `MCP-07-04`: Decide whether a Friday Chat health command is needed in the first implementation pass.
- `MCP-07-05`: If a health command is approved, expose server state, registered tool count, skipped tool count, and failure summaries.
- `MCP-07-06`: Add structured diagnostic models suitable for CLI display and tests.

### Affected Areas

- `packages/friday-telemetry/src/friday_telemetry/`
- `packages/friday-runtime/src/friday_runtime/`
- `packages/friday-chat/src/friday_chat/`
- `packages/friday-mcp/src/friday_mcp/client/`

### Required Tests

- Telemetry unit tests for event shape and redaction.
- Diagnostics tests for partial failure, collision, cap skip, and budget skip cases.
- If implemented, Friday Chat command tests for MCP health output.
- Negative tests proving secrets, headers, raw env values, and raw unsafe outputs are not emitted.

### Acceptance Criteria

- Operators can determine which MCP servers connected and which tools were registered or skipped.
- Budget and security skips are explainable.
- Telemetry and diagnostics are redacted by default.
- Health surfaces do not require direct access to private MCP client internals.

### Dependencies

- Depends on `MCP-WS-02` through `MCP-WS-06`.

### Non-Goals

- Do not add telemetry endpoints or backend services.
- Do not expose raw tool schemas or outputs in health output.

## MCP-WS-08: Documentation And Guide Close-Out

### Purpose

Update user-facing and contributor-facing documentation so MCP configuration, operation, security, and memory behavior are understandable.

### Implementation Tasks

- `MCP-08-01`: Update `docs/guides/` with MCP setup examples for stdio servers, disabled MCP, optional servers, required servers, include/exclude filters, and security defaults.
- `MCP-08-02`: Document canonical config location under `tools.providers.mcp`.
- `MCP-08-03`: Document that `config_file` is reserved and rejected until the optional include phase.
- `MCP-08-04`: Document tool budget behavior and the interaction between MCP schemas, Friday Chat context, and memory retrieval.
- `MCP-08-05`: Document default memory behavior: transcript records are allowed, long-term memory ingestion is disabled unless configured.
- `MCP-08-06`: Document secret handling through environment variables and redacted diagnostics.
- `MCP-08-07`: Add troubleshooting guidance for missing tools, server startup failure, required server failure, name collisions, schema budget skips, and oversized results.
- `MCP-08-08`: Update package README files where MCP behavior changes public usage.

### Affected Areas

- `docs/guides/`
- `docs/planning/build-plan.md`
- `packages/friday-mcp/README.md`
- `packages/friday-runtime/README.md`
- `packages/friday-chat/README.md`
- Config templates distributed with Friday Chat.

### Required Tests

- Documentation link checks if available.
- Config snippets copied into tests or validated through config parsing tests.
- Manual review that docs distinguish package-installed templates, editable user config, and runtime state paths.

### Acceptance Criteria

- A user can configure an MCP stdio server from the guide without reading source code.
- Documentation clearly explains budget impact and memory ingestion defaults.
- Config examples match tested config models.
- Guides do not imply external MCP config include support before `MCP-WS-09`.

### Dependencies

- Depends on implementation behavior from `MCP-WS-01` through `MCP-WS-07`.

### Non-Goals

- Do not document unreleased resource, prompt, live refresh, or server-exposure features as available.

## MCP-WS-09: Optional External MCP Config Include

### Purpose

Optionally support an external MCP config include while preserving the canonical runtime config model as the single authority.

### Implementation Tasks

- `MCP-09-01`: Define include semantics for `tools.providers.mcp.config_file`.
- `MCP-09-02`: Define relative path resolution, allowed roots, missing-file behavior, and conflict resolution with inline config.
- `MCP-09-03`: Parse the external file into the same typed MCP provider model used by inline config.
- `MCP-09-04`: Preserve redaction, diagnostics, validation, and config precedence behavior.
- `MCP-09-05`: Add examples for user-specific external MCP config files.

### Affected Areas

- `packages/friday-runtime/src/friday_runtime/config.py`
- `packages/friday-mcp/src/friday_mcp/config.py`
- `docs/guides/`
- Config templates.

### Required Tests

- Unit tests for include loading, relative paths, absolute paths, missing files, invalid files, unknown keys, duplicate servers, and inline conflict behavior.
- Negative tests for path traversal and disallowed roots.

### Acceptance Criteria

- External config includes normalize into the same canonical typed config model.
- Inline config remains the authoritative shape.
- Unsafe include paths fail closed.

### Dependencies

- Depends on `MCP-WS-01`.
- Should not start until the tools-only inline config implementation is stable.

### Non-Goals

- Do not allow external config to bypass validation.
- Do not support multiple competing config authorities.

## File And Module Ownership

- `friday-core`: shared protocols and DTOs only when multiple packages need the same contract.
- `friday-mcp`: MCP protocol clients, transport adapters, client manager, server config models, and MCP-specific wrappers.
- `friday-runtime`: lifecycle ownership, provider loading, config normalization, registry assembly, startup and shutdown diagnostics.
- `friday-tools`: native tool contracts and compatibility points only; do not make native tools depend on MCP internals.
- `friday-chat`: per-turn tool selection, context budget enforcement, tool loop integration, user-visible command or diagnostic surfaces.
- `friday-memory`: retrieval budgets, provenance-aware storage, optional ingestion, sanitization and quarantine policy for memory records.
- `friday-transcript`: durable transcript model and export behavior for tool-call provenance.
- `friday-telemetry`: redacted event contracts and emitters.

## Data, Schema, And Contract Changes

- Add typed MCP config objects for provider, server, limits, discovery, security, and ingestion policies.
- Add typed discovery diagnostics for connected servers, failed servers, skipped tools, registered tools, and cap decisions.
- Add tool metadata for provider type, server name, original name, canonical name, transport, trust level, schema status, and discovery state.
- Add tool-call provenance for call ID, provider metadata, argument redaction/hash status, result truncation status, sanitization status, transcript ID, and optional memory record ID.
- Add memory provenance fields for MCP-derived records.
- Keep raw arguments and raw outputs out of default telemetry, diagnostics, and long-term memory.

## API, CLI, And Config Impact

- Config impact is first-class: `tools.providers.mcp` becomes the canonical public config surface.
- CLI impact should be minimal at first. A health command is optional and should be decided in `MCP-WS-07`.
- Friday Chat should consume the canonical runtime MCP provider config directly or through a compatibility normalization layer.
- Public Python APIs should expose typed diagnostics rather than requiring callers to inspect private client manager state.

## Migration Order

1. Land contracts and default policy tests.
2. Land strict config parsing and validation with MCP still functionally disabled if needed.
3. Land runtime lifecycle support and fake-server discovery.
4. Land registry integration, naming, metadata, and filter behavior.
5. Land Friday Chat budget and tool-selection integration.
6. Land execution provenance, transcript recording, and output security.
7. Land optional memory ingestion behavior.
8. Land telemetry, diagnostics, and optional health surface.
9. Land guide and README updates tied to tested examples.
10. Revisit optional external config include after inline behavior is stable.

## Security And Governance Requirements

- Never pass full Friday config to an MCP server.
- Never emit raw secrets, env values, headers, arguments, or raw outputs in diagnostics or telemetry.
- Treat MCP schema descriptions and tool outputs as untrusted external content.
- Sanitize schemas at registration time and verify sanitized schemas before prompt assembly.
- Sanitize tool results before they are passed back to the model.
- Enforce path scoping for `cwd` and any later external config includes.
- Bound connection, discovery, and execution timeouts.
- Bound discovery and execution concurrency.
- Remove broad mypy ignores from touched files where practical; do not add new broad suppressions without an explicit waiver.

## Verification Commands

Run focused commands as each workstream lands:

```bash
uv run pytest packages/friday-mcp/tests_mcp
uv run pytest packages/friday-runtime/tests_runtime
uv run pytest packages/friday-chat/tests_chat
uv run pytest packages/friday-memory/tests_memory
uv run pytest packages/friday-transcript/tests
uv run pytest tests/integration
uv run ruff check packages/friday-core packages/friday-mcp packages/friday-runtime packages/friday-chat packages/friday-memory packages/friday-transcript packages/friday-telemetry
uv run mypy packages/friday-core packages/friday-mcp packages/friday-runtime packages/friday-chat packages/friday-memory packages/friday-transcript packages/friday-telemetry
```

When repo-wide validation fails because of unrelated legacy debt, record the failure and run the narrowest meaningful validation for touched files.

## UAT Scenarios

- `MCP-UAT-01`: Start Friday Chat with MCP disabled and verify existing chat behavior.
- `MCP-UAT-02`: Start Friday Chat with one local stdio MCP server and verify discovered tools appear with canonical prefixed names.
- `MCP-UAT-03`: Start with one optional failing server and verify chat still starts with diagnostics.
- `MCP-UAT-04`: Start with one required failing server and verify startup fails with a clear error.
- `MCP-UAT-05`: Configure include and exclude filters and verify only expected canonical tool names are registered.
- `MCP-UAT-06`: Configure an oversized schema and verify the tool is skipped or rejected before registration.
- `MCP-UAT-07`: Execute an MCP tool with a large result and verify truncation before model re-entry.
- `MCP-UAT-08`: Verify transcript provenance for an MCP call.
- `MCP-UAT-09`: Verify MCP output is not stored in long-term memory by default.
- `MCP-UAT-10`: Enable explicit MCP memory ingestion and verify provenance labels on retrieval.

## Acceptance Criteria

- MCP can be configured through `tools.providers.mcp` without a second config authority.
- Runtime startup can discover and register MCP tools through async lifecycle ownership.
- Optional and required MCP server failures behave differently and predictably.
- MCP tools are named deterministically and carry inspectable metadata.
- Friday Chat enforces tool-schema and result-token budgets before memory retrieval.
- Memory ingestion is disabled by default and provenance-aware when enabled.
- Telemetry and diagnostics are useful and redacted.
- End-user guides include tested config examples and troubleshooting notes.

## Clarifying Questions For Implementation

These questions do not block creation of this tactical plan, but they should be resolved before the corresponding workstreams start:

1. Should shared MCP DTOs live in `friday-core` as framework contracts, or in `friday-mcp` with stable exported interfaces?
2. Which metadata strategy should be used for tools: protocol extension, registry sidecar, or wrapper accessor?
3. What first-pass values should be used for total tool budget, schema token budget, result byte budget, and minimum memory retrieval floor?
4. Should SSE transports be enabled in the first release, or deferred behind a stricter trust profile?
5. Should Friday Chat expose an MCP health command in the first implementation pass?
6. Should transcript Markdown and CSV exports include summarized MCP provenance by default, or should full provenance remain JSONL-only?
7. Should argument hashes be salted, and if so where should that salt be configured?

## Deferred Items

- MCP resources and prompts.
- Live server refresh and tool registry reload.
- Friday as an MCP server.
- External MCP config include.
- Original-name include and exclude filters.
- UI-based MCP configuration.
- Automatic memory revocation when external MCP source state changes.

## Risks

- MCP schemas can consume enough context to starve memory retrieval unless budgets are enforced before prompt assembly.
- MCP tool descriptions and outputs can become prompt-injection vectors unless sanitized at registration and execution boundaries.
- Adding async provider loading can disturb runtime startup unless lifecycle ownership is explicit.
- Metadata bolted onto tools without a stable contract can create hidden cross-package coupling.
- Optional failed servers can become invisible operational failures unless diagnostics are first-class.
- Enabling memory ingestion too broadly can pollute long-term memory with untrusted or stale tool outputs.
