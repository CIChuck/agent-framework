# Build Plan: Friday Framework MCP Enhancements

**Status:** Draft, remediated after initial architecture review
**Target:** MCP client capability across Friday runtime, tools, memory, and app
layers
**Objective:** Add configurable MCP client support to the Friday framework while
preserving existing tool-calling, memory, context-management, security,
telemetry, and runtime-boundary contracts.

The [2026-09-27 current-code rebaseline](rebaseline-2026-09-27.md) is the
current status assessment. It credits the existing standalone package and
separates its tested primitives from the unimplemented cross-package feature.

---

## 1. Conversation Snapshot

This plan captures the initial MCP enhancement brainstorming session and is
intended to evolve over time.

Current decisions:

- MCP client capability should integrate with the existing Friday tool-provider
  architecture.
- MCP must be compatible with:
  - `friday-memory`
  - tool-calling context management
  - `friday-tools`
  - runtime tool registration
  - Friday Chat V2 normal turn processing
- Canonical MCP configuration should live inline in the existing `config.yaml`
  architecture under `tools.providers.mcp`.
- A separate MCP YAML may be added later as an optional include, but it should
  normalize into the same typed `MCPConfig` model and must not become a second
  configuration authority.
- MCP client support in the first implementation pass is tools-only. MCP
  resources, MCP prompts, resource subscriptions, and Friday-as-MCP-server
  exposure changes are explicitly out of scope unless this plan is amended.
- First-pass MCP server failures are optional by default. Use `required: true`
  only for servers or tools that must fail runtime startup when unavailable.
- First-pass include/exclude filters match canonical prefixed MCP tool names.
  Original MCP tool-name filtering is deferred unless a separate explicit config
  field is added.
- First-pass MCP tool discovery is startup-time only. Runtime refresh/reload
  behavior is deferred until a later phase unless explicitly pulled forward.

Recommended canonical config shape:

```yaml
tools:
  providers:
    mcp:
      enabled: true
      mode: selected
      include_tools: []
      exclude_tools: []
      include_categories: []
      exclude_categories: []
      config:
        auto_connect: true
        tool_name_prefix: mcp_
        discovery:
          refresh_mode: startup_only
        limits:
          max_servers: 8
          max_tools_per_server: 25
          max_total_tools: 50
          max_schema_tokens: 4000
          max_schema_bytes_per_tool: 8192
          max_result_bytes: 65536
        security:
          default_trust_level: local
          redact_env: true
          redact_headers: true
          redact_arguments: true
          require_explicit_stdio_commands: true
          allowed_workspace_roots: []
        ingestion:
          long_term_memory_enabled: false
        servers:
          - name: filesystem
            enabled: true
            required: false
            transport: stdio
            command: npx
            args:
              - -y
              - "@modelcontextprotocol/server-filesystem"
              - /path/to/workspace
            env: {}
            cwd: /path/to/workspace
            timeout_seconds: 30
            tool_timeout_seconds: 60
            retry_attempts: 3
            trust_level: local
```

The numeric limits above are provisional planning defaults. Phase 0 must verify
or adjust them against at least one small-context model profile and one
large-context model profile before implementation treats them as stable defaults.

Optional future include shape:

```yaml
tools:
  providers:
    mcp:
      enabled: true
      config_file: ./mcp.servers.yaml
```

`config_file` is not part of the first implementation unless Phase 5 is
explicitly pulled forward. Until it is implemented, the runtime config parser
must reject `tools.providers.mcp.config_file` rather than silently ignoring it.
If `config_file` is later added, inline and external configuration must still
normalize into one `MCPConfig` instance before runtime construction.

Config values that may contain secrets, including `env`, `headers`, command
arguments, URLs, and tool-call arguments, must be treated as runtime-only input.
Diagnostics may report key names and redacted summaries, but not raw values.

## 2. Existing Repository Baseline

The repository already contains a `friday-mcp` package with:

- MCP config models for stdio and SSE server connections.
- `MCPClientManager` for multiple client connections.
- Stdio and SSE client implementations.
- `MCPToolAdapter` and `MCPToolWrapper` that adapt MCP tools to Friday's
  `ToolDefinition` protocol.
- MCP server-side capabilities for exposing Friday agents or tools.

The runtime layer already has typed tool-provider config:

- `ToolsConfig`
- `ToolProvidersConfig`
- `MCPToolProviderConfig`

The current runtime integration gap is narrow but important:

- `friday_runtime.tool_loading.register_runtime_tools()` is synchronous.
- Runtime DI boot is async, but tool registry construction still calls the
  synchronous helper.
- `friday_runtime.tool_loading` currently raises a `ToolProviderLoadError` when
  `tools.providers.mcp.enabled` is true.
- Existing provider filtering silently ignores missing `include_tools` entries.
  MCP must not preserve that behavior for required server/tool configuration.
- Friday Chat already estimates tool schema tokens and subtracts them from the
  memory retrieval budget, but MCP needs discovery-time caps before large tool
  catalogs can reach turn processing.
- Existing Friday Chat token estimation is approximate. MCP budget tests should
  assert monotonic budget behavior and configured cap enforcement, not exact
  tokenizer parity unless a concrete tokenizer is introduced.
- Several existing `friday-mcp` and `friday-memory` model files have legacy
  `# mypy: ignore-errors` suppressions. New MCP boundary work must not expand
  that debt; any touched files should either be remediated or explicitly tracked
  as legacy policy debt.
- The current shared `ToolDefinition` protocol does not expose arbitrary
  provider metadata. MCP provenance therefore needs either a typed protocol
  extension, a registry metadata sidecar, or a wrapper-specific metadata access
  path before tool metadata can reliably flow across package boundaries.
- Friday Chat has a separate app configuration model from the headless runtime
  configuration. The plan must define how MCP runtime provider settings are
  surfaced when `friday-chat` is run directly.
- Current Friday Chat tool-call records are intentionally small and do not carry
  provider provenance, security metadata, or truncation state. Transcript and
  memory provenance work must extend that record path rather than assuming the
  current shape can preserve MCP metadata.

## 3. Desired Architecture

Keep package responsibilities explicit:

| Package | Responsibility |
| --- | --- |
| `friday-mcp` | MCP transports, client manager, protocol adapters, server-status models, MCP tool wrappers |
| `friday-runtime` | Lifecycle, typed config loading, async MCP connection startup/shutdown, registry assembly, provider diagnostics |
| `friday-tools` | Native Friday tool library and common tool contracts |
| `friday-memory` | Memory retrieval budgets, provenance-aware storage, optional MCP output ingestion, memory-specific sanitization/quarantine |
| `friday-agent` | Agent profiles, required tool validation, workflows, orchestration |
| `friday-chat` | App-layer turn selection, tool schema budget application, tool loop, user-facing command integration |
| `friday-core` | Shared protocols, typed cross-package contracts, security wrappers, provenance DTOs where broadly shared |

MCP tools should enter the system through the same runtime registry path as
builtin and `friday-tools` tools. Friday Chat and agents must not need a
special MCP execution path for normal tool calls.

Budget ownership should be split intentionally:

- `friday-runtime` owns provider discovery limits and registry-time caps.
- `friday-chat` owns per-turn tool selection and tool schema budget application.
- `friday-memory` owns memory retrieval budget compliance and optional persisted
  memory ingestion.
- A shared typed contract should describe tool schema cost, provenance, and
  prompt-visible safety state so packages do not exchange incidental dicts.

Required shared contracts:

- `MCPClientLimits`: provider/server/tool count caps, schema size caps, result
  size caps, and reserved result-token policy.
- `MCPClientSecurityPolicy`: trust level, redaction policy, stdio command
  handling, path/workspace scoping, and remote transport posture.
- `MCPIngestionPolicy`: disabled-by-default long-term ingestion plus future
  per-server/per-tool opt-in settings.
- `MCPToolMetadata`: provider, server, original name, prefixed name, transport,
  trust level, schema token estimate, schema sanitization status, and filtering
  diagnostics.
- `MCPToolCallProvenance`: call id, tool metadata, arguments visibility policy,
  result truncation state, output sanitization metadata, ingestion decision, and
  transcript/memory correlation identifiers.
- `MCPDiscoveryState`: server connection state, listed tool catalog version,
  cache timestamp, rejected/filtered tool diagnostics, and refresh eligibility.

Phase 0 should decide whether those contracts live in `friday-core`,
`friday-mcp`, or `friday-runtime`. Cross-package consumers must not pass raw
metadata dictionaries when a typed contract is practical.

## 4. Design Considerations

### 4.1 Configuration

MCP should be configured under:

```yaml
tools:
  providers:
    mcp:
      enabled: true
      mode: selected
      config:
        servers: []
```

Reasons:

- MCP tools are tool providers, not a separate app subsystem.
- Runtime startup already owns tool-provider assembly.
- Agent and workflow tool binding validation must see MCP tools during runtime
  construction.
- Tool context budgeting should treat MCP tools like other tools once MCP tools
  pass provider-level caps.
- One config file is easier to validate, test, and reproduce.

Required config model additions:

- Provider-level limits:
  - `max_servers`
  - `max_tools_per_server`
  - `max_total_tools`
  - `max_schema_tokens`
  - `max_schema_bytes_per_tool`
  - `max_result_bytes`
- Server-level lifecycle controls:
  - `required`
  - `timeout_seconds`
  - `tool_timeout_seconds`
  - `retry_attempts`
- Security controls:
  - `trust_level`
  - env/header redaction flags
  - argument redaction and hashing policy
  - explicit stdio command requirements
  - optional workspace/path allowlists for stdio servers that touch files
- Ingestion controls:
  - long-term memory ingestion disabled by default
  - per-server or per-tool opt-in if automatic ingestion is later allowed
- Discovery controls:
  - `refresh_mode: startup_only` for the first implementation pass
  - no background or automatic rediscovery in the first pass
  - future reload support must re-run all validation and binding checks

Recommended DTO names:

- `MCPClientLimits`
- `MCPClientSecurityPolicy`
- `MCPIngestionPolicy`
- `MCPDiscoveryPolicy`
- `MCPDiscoveryState`
- `MCPServerRuntimePolicy`
- `MCPProviderDiagnostics`

Unknown keys under `tools.providers.mcp` should fail validation. This avoids a
dangerous state where users believe a `config_file`, limit, or security setting
is active when it was ignored by the parser.

Friday Chat configuration bridge:

- Direct Friday Chat runs must be able to consume the effective MCP provider
  config, either by delegating to `RuntimeConfig` loading or by normalizing
  Friday Chat config into the same typed runtime provider model.
- The MCP config authority remains `tools.providers.mcp`; Friday Chat must not
  introduce a second MCP-specific config shape.
- Any app-local convenience settings must be documented as aliases that normalize
  into the canonical runtime MCP model.

Configuration precedence:

1. Canonical runtime config file values.
2. Explicit runtime construction overrides used by tests.
3. Environment-variable overrides only where the existing runtime config policy
   permits them.
4. Friday Chat aliases only after they normalize into the canonical runtime MCP
   model.

Secrets must continue to come from environment variables or local runtime-only
configuration, not from committed example config files.

### 4.2 Runtime Lifecycle

MCP client setup is async. Runtime integration should happen inside runtime
startup, not inside a synchronous helper that cannot connect or list tools.

Required lifecycle behavior:

- Split or replace synchronous tool loading with an async provider loading step.
- Connect enabled MCP servers during runtime boot when `auto_connect` is true.
- Store `MCPClientManager` or an equivalent lifecycle owner on the runtime DI
  container.
- Make MCP startup ordering explicit: configure services, connect/list MCP
  servers, register accepted tools, then validate agent/workflow tool bindings.
- Register discovered MCP tools into the runtime tool registry only after
  applying provider limits, filters, sanitization, and collision checks.
- Preserve per-server connection status and diagnostics.
- Disconnect all MCP clients during runtime shutdown.
- Make shutdown idempotent.
- Surface connection failures without silently dropping configured required
  tools.
- Preserve the existing runtime startup invariant that partial initialization is
  either explicit and diagnosed or fails deterministically.

Failure behavior:

- Required server connection failure should fail runtime startup.
- Optional server connection failure should allow startup but emit structured
  diagnostics and exclude that server's tools.
- Required tool missing after filtering, discovery, or server failure should fail
  startup before agent profile validation completes.
- Non-required MCP failures must not be indistinguishable from "provider
  disabled"; diagnostics must retain skipped/failed server state for user-facing
  troubleshooting.

### 4.3 Tool Registration And Naming

MCP tool names need stable, collision-resistant names.

Default naming:

```text
mcp_<server_name>_<tool_name>
```

Required behavior:

- Normalize server names and tool names to valid Friday/OpenAI function names.
- Detect collisions with builtin, `friday-tools`, and other MCP tools.
- Preserve the original MCP server/tool name in tool metadata for provenance and
  debugging.
- Apply include/exclude filters to prefixed names by default.
- Optionally support original-name filters later, but only if the config field
  makes that explicit.
- Report filtered, unavailable, and over-budget tools in diagnostics.
- Use a deterministic normalization algorithm for server and tool names. The
  original server/tool name must remain available in metadata even when the
  registered name is normalized.
- Fail on normalized-name collisions rather than adding disambiguating suffixes
  silently.

Required metadata on each registered MCP tool:

- `provider: mcp`
- `server_name`
- `original_tool_name`
- `prefixed_tool_name`
- `transport`
- `trust_level`
- `schema_token_estimate`
- `schema_sanitization_status`

The implementation must define how this metadata is represented. Current
`ToolDefinition` does not include a metadata property, so the plan requires one
of:

- a backward-compatible protocol extension such as `ToolDefinitionMetadata`;
- a registry sidecar keyed by registered tool name; or
- an MCP wrapper API that runtime/chat/transcript adapters can query without
  importing implementation internals.

### 4.4 Context Budgeting

MCP servers can expose many tools with large schemas. MCP must use the existing
tool context and budgeting system, but discovery-time controls must prevent
unbounded catalogs from reaching per-turn prompt assembly.

Required behavior:

- Enforce provider/server discovery caps before registry insertion.
- Enforce per-tool schema byte caps before registry insertion.
- Enforce aggregate MCP schema-token and tool-count caps before registry
  insertion unless a later phase explicitly supports lazy per-turn registration.
- Apply Friday Chat relevance selection and final per-turn schema-token budget
  after registry insertion.
- Preserve Friday Chat's existing dynamic context behavior where tool schema
  tokens reduce the memory retrieval budget.
- Avoid injecting every MCP tool into every turn by default.
- Default MCP provider mode must remain `selected`.
- Keep `/tools`, `/inject-tools`, `/recommend-tools`, and `/tool-budget`
  behavior coherent with MCP tools.
- Add diagnostics when tools are excluded because of provider filters, budget
  caps, schema size, sanitization failure, or server failure.

Recommended budget contract:

```text
available_prompt_budget =
  model_context_window
  - output_buffer
  - system_prompt_tokens
  - selected_tool_schema_tokens
  - reserved_tool_result_tokens
```

Memory retrieval should receive only the remaining context budget. MCP tool
results should also have a maximum model-visible size and a separate persisted
storage size policy.

Enforcement order:

1. Config validation rejects unsupported keys and invalid server definitions.
2. Runtime discovery connects enabled servers and lists tools.
3. Runtime registration applies server count, per-server tool count, schema byte,
   aggregate schema-token, collision, sanitization, and include/exclude checks.
4. Friday Chat per-turn selection chooses relevant registered tools within the
   app-level `max_tools` and schema-token budget.
5. Memory retrieval receives the remaining prompt budget after selected tool
   schemas and reserved output buffers are accounted for.
6. Tool execution applies execution timeout, result-size cap, sanitization,
   prompt-injection wrapping, and provenance capture before model feedback.

When MCP schemas force the remaining memory retrieval budget below the configured
minimum retrieval floor, Friday Chat must reduce selected tools or fail the
turn with an explicit budget diagnostic rather than silently starving memory
context.

### 4.5 Memory And Provenance

MCP tool outputs are external content. If stored or ingested, they need explicit
provenance.

Recommended provenance fields:

- `source_type: mcp_tool`
- `server_name`
- `tool_name`
- `prefixed_tool_name`
- `call_id`
- `transport`
- `sanitization_status`
- `trust_level`
- `result_truncated`
- `result_size_bytes`
- `schema_sanitization_status`
- `ingestion_policy`
- `arguments_redaction_status`
- `arguments_stored`
- `arguments_hash`
- `tool_result_id`
- `transcript_entry_id`
- `memory_record_id`

Tool call and transcript record requirements:

- Extend Friday Chat tool-call records or introduce a framework-level
  `ToolCallRecord` that can carry provider provenance, security metadata,
  truncation state, and ingestion decisions.
- Preserve MCP provenance through transcript entries and transcript exporters.
- Keep tool-call metadata distinct from turn-level metadata so multiple MCP
  calls in one turn remain individually attributable.
- Store tool-call arguments according to argument redaction policy. When
  arguments are not stored, preserve a stable hash or redacted summary for
  correlation.
- Store raw output only according to the configured security and quarantine
  policy; never assume transcript storage is safe for unsanitized MCP output.

Initial default:

- MCP tool outputs may be fed back into the model after sanitization and
  prompt-injection wrapping.
- Transcript storage should record MCP tool-call provenance when transcripts are
  enabled.
- Long-term ingestion of MCP outputs must be disabled by default until
  provenance, refresh, retention, and deletion semantics are explicit.
- Automatic ingestion, if later enabled, should be opt-in by server or tool and
  should store sanitized content separately from the raw model-visible result.
- Memory retrieval must not treat MCP output as ordinary user-authored fact
  without source labeling.
- Memory ingestion must record freshness and revocation assumptions. MCP-derived
  facts can become stale when the backing server data changes.

### 4.6 Security

Treat MCP tool schemas, descriptions, resources, prompts, and outputs as
untrusted external content.

Security requirements:

- Sanitize tool descriptions before prompt/context inclusion.
- Sanitize schemas and descriptions without losing the original schema's
  provenance and diagnostics.
- Treat schema/description sanitization as a registration-time requirement, then
  verify at prompt assembly that only sanitized schema text is model-visible.
- Sanitize tool outputs before LLM feedback.
- Sanitize or quarantine stored memory content.
- Preserve existing prompt-injection wrapping for tool results.
- Enforce separate timeouts for connection, tool listing, and tool execution.
- Bound concurrent MCP server startup and concurrent MCP tool execution.
- Enforce result byte/token caps before model feedback.
- Avoid passing secrets from Friday config into model-visible context.
- Redact env values, headers, tokens, and credentials from telemetry,
  diagnostics, transcripts, and memory.
- Redact or hash tool-call arguments by default when arguments may contain local
  paths, user data, tokens, or request payloads.
- Treat stdio server command, args, env, and cwd as sensitive runtime
  configuration.
- Consider local stdio MCP servers and remote SSE MCP servers as different trust
  profiles.
- Add workspace/path scoping for stdio servers that can read or write files.
- Never pass the full Friday config object to MCP servers. Provide only the
  explicit env/headers/args configured for that server.
- Do not expose Friday memory, prompts, or resources through MCP server defaults
  as part of this client-tools implementation.

Schema and description sanitization is separate from output sanitization.
Schemas and descriptions enter model-visible context before any tool call is
executed, so they need their own sanitizer, diagnostics, and tests.

### 4.7 MCP Resources And Prompts

MCP supports more than tools. For the first implementation pass, this plan is
tools-only.

Deferred areas:

- MCP resources as memory-ingestion sources.
- MCP prompts as reusable Friday prompt fragments.
- MCP resource subscriptions or refresh policies.
- Changes to Friday-as-MCP-server prompt/resource exposure defaults.

Those capabilities require separate provenance, freshness, retention, security,
and user-consent decisions.

### 4.8 Telemetry And Diagnostics

MCP integration should emit structured diagnostics.

Useful events:

- server connection attempted
- server connection succeeded or failed
- server skipped because disabled
- server skipped because over provider limit
- tools listed
- tool skipped because filtered
- tool skipped because over budget
- tool skipped because schema sanitization failed
- tool registered
- tool call started
- tool call succeeded, failed, timed out, or was truncated
- memory ingestion skipped, accepted, or quarantined
- server disconnected

Telemetry should include server name, transport, tool name, duration,
success/failure status, sanitized error classification, and budget impact.
Telemetry must not include raw env values, headers, API keys, full tool outputs,
or unsanitized schemas.

### 4.9 Tool Discovery Cache And Refresh

MCP servers may change their tool catalogs while Friday is running. The first
implementation uses startup-time discovery only. Refresh/reload behavior is
deferred until a later phase unless explicitly pulled forward.

Required behavior:

- Cache discovered tools per server with diagnostics that identify when the cache
  was populated.
- Do not automatically refresh or reload MCP tool catalogs during the first
  implementation pass.
- User-facing reload commands are deferred until the framework can reapply all
  registration, filter, budget, collision, sanitization, and agent-binding checks.
- Future refresh work must prevent refresh from silently invalidating active agent
  required-tool bindings.
- Future refresh work must report tools added, removed, changed, filtered, or
  rejected during refresh.
- Future refresh work must avoid leaking old tool wrappers or stale MCP client
  references.

### 4.10 Agent And Workflow Compatibility

Agent profile and workflow validation must account for MCP tools.

Required behavior:

- MCP tools are loaded before validating agent tool bindings.
- Profiles may reference prefixed MCP tool names.
- Missing required MCP tools fail clearly when their server is disabled,
  unavailable, over-budget, or filtered out.
- Workflow execution can use MCP tools through the same registry path as other
  tools.
- Validation errors should distinguish unknown tool names from disabled,
  filtered, unavailable, and over-budget MCP tools.

## 5. Candidate Implementation Phases

These are coarse feature phases, not one-to-one workstream identifiers. The
[tactical plan](tactical-plan.md) supplies the narrower WS-00 through WS-09
order: WS-01 strict configuration precedes WS-02 runtime loading and WS-03
registry integration, even though all contribute to the coarse Phase 1 below.
The tactical construction directive controls the allowed files for each slice.

### Phase 0: Contracts, Defaults, And Policy Cleanup

Goal:

- Make the MCP implementation contract precise before changing runtime
  behavior. This phase is bounded to `MCP-WS-00` in `friday-core` and
  `friday-mcp`; later workstreams own config parsing and consumer behavior.

Work:

- Define typed *contracts and defaults*, without wiring them into runtime or
  Friday Chat config. The named DTO candidates are:
  - `MCPClientLimits`
  - `MCPClientSecurityPolicy`
  - `MCPIngestionPolicy`
  - `MCPServerRuntimePolicy`
  - `MCPProviderDiagnostics`
  - `MCPToolMetadata`
  - `MCPToolCallProvenance`
  - `MCPDiscoveryPolicy`
  - `MCPDiscoveryState`
- Choose package ownership in `friday-core` or `friday-mcp` without creating a
  dependency cycle. Choose a typed tool-metadata representation; do not change
  registry or consumer behavior in this phase.
- Set first-pass default limits for server/tool counts, schema and result size,
  timeouts, and a minimum memory retrieval floor. Enforcement belongs to later
  workstreams.
- Define deterministic name normalization and collision behavior.
- Define startup-only discovery and concurrency *policy defaults*; implementation
  and enforcement belong to WS-02/03.
- Decide tool-call argument redaction and hash policy, and first-pass SSE trust
  posture, before code generation.
- Identify touched `# mypy: ignore-errors` files and either remediate them or
  record explicit legacy-policy debt before expanding their public surface.
- Document selected-mode and no-long-term-ingestion defaults.

Explicit deferrals: WS-01 owns strict `tools.providers.mcp` parsing,
`config_file` rejection, and Friday Chat config mapping. WS-04/06 own budget
enforcement and the memory-floor fallback. WS-04/07 own command-surface audits.
WS-05/07 own redaction enforcement and persistence/telemetry behavior. The
rebaseline records each boundary and prevents a Phase 0 acceptance check from
silently expanding the narrow WS-00 construction directive.

Acceptance:

- Shared contract ownership and imports are stable, typed, and free of circular
  dependencies; old programmatic MCP APIs remain compatible.
- DTO defaults, invalid values, metadata representation, name normalization,
  duplicate-name rejection, and security defaults have focused tests.
- The policy records conservative numeric limits, a minimum memory retrieval
  floor, SSE posture, argument redaction/hash behavior, and deferred enforcement.
- No runtime, Chat, memory, transcript, telemetry, registry, or CLI behavior is
  changed in WS-00. Touched typing debt is remediated or explicitly tracked.

### Phase 1: Runtime MCP Tool Provider

Goal:

- Make `tools.providers.mcp.enabled=true` register MCP tools instead of raising
  "not implemented."

Work:

- Move MCP tool loading into an async runtime boot step.
- Store `MCPClientManager` on the runtime DI container.
- Connect enabled servers according to required/optional failure semantics.
- Bound concurrent server startup according to the configured runtime policy.
- List MCP tools with fake-client coverage so tests do not require external
  servers.
- Sanitize MCP tool descriptions and schemas before registration.
- Apply server limits, tool limits, schema limits, include/exclude filters, and
  collision checks before tools enter the registry.
- Register MCP tool wrappers into the runtime tool registry.
- Preserve provider diagnostics for connected, failed, skipped, filtered, and
  over-budget tools.
- Populate the chosen MCP tool metadata contract or registry sidecar for every
  registered MCP tool.
- Implement startup-time tool cache semantics and diagnostics.
- Disconnect clients during shutdown.

Acceptance:

- MCP provider can be enabled in runtime config.
- Fake MCP tools appear in the runtime registry.
- Runtime shutdown disconnects MCP clients and is safe to call multiple times.
- Required server failures fail startup clearly.
- Optional server failures are visible in diagnostics.
- Over-budget and filtered tools are visible in diagnostics.
- Startup concurrency is bounded and cancellation-safe.
- MCP tool metadata is available to Friday Chat, transcript, and memory paths
  without importing MCP implementation internals.
- Startup-time tool cache state is observable in diagnostics.

### Phase 2: Tool Context And Friday Chat Compatibility

Goal:

- Ensure MCP tools flow through Friday Chat and tool-context behavior like native
  tools without overwhelming prompt budget.

Work:

- Bridge Friday Chat direct-run configuration to canonical runtime MCP provider
  config.
- Verify MCP schemas participate in Friday Chat tool budget calculations.
- Add tests with large fake MCP catalogs and oversized schemas.
- Verify selected MCP schemas reduce memory retrieval budget exactly like native
  tool schemas.
- Verify MCP schema selection does not reduce memory retrieval below the defined
  floor without an explicit fallback or diagnostic.
- Verify `/tools`, `/inject-tools`, `/recommend-tools`, and `/tool-budget`
  include MCP tools correctly.
- Verify a normal Friday Chat turn can execute an MCP tool call.
- Preserve tool-call provenance in raw prompt/response and transcript records.
- Extend or replace Friday Chat `ToolCallRecord` so MCP calls retain provider
  provenance, security metadata, result truncation state, and ingestion decision.
- Add diagnostics for model-visible tool schema token usage and reserved
  tool-result budget.

Acceptance:

- MCP tool calls execute through the normal tool loop.
- Tool schemas do not exceed configured context budgets.
- Large MCP catalogs do not cause all tools to be injected by default.
- MCP tools can be selected and filtered through existing command surfaces.
- Memory retrieval receives the prompt budget remaining after selected MCP tool
  schemas are accounted for.
- Memory retrieval floor behavior is tested for oversized MCP schema selections.
- Tool-call provenance survives from tool execution through transcript capture.

### Phase 3: Memory Provenance And Optional Ingestion

Goal:

- Make MCP tool-output storage safe and traceable.

Work:

- Add MCP provenance metadata for tool results.
- Ensure provenance is recorded per tool call, not only at the turn level.
- Keep transcript provenance distinct from long-term memory ingestion.
- Implement disabled-by-default long-term memory ingestion controls.
- If opt-in ingestion is enabled, support per-server and per-tool controls.
- Ensure sanitized model-visible output and memory-storage output remain
  distinct.
- Add tests for provenance, sanitization, truncation, quarantine, and disabled
  ingestion defaults.
- Ensure memory retrieval displays MCP-derived content with clear source labels.
- Preserve stale/freshness metadata for any MCP-derived memory.
- Add transcript exporter coverage for MCP tool-call metadata in JSONL, Markdown,
  and CSV exports.

Acceptance:

- MCP tool results stored in transcript and/or memory have clear provenance.
- Long-term memory ingestion is disabled by default unless explicitly configured.
- Sanitization stats and provenance are preserved.
- MCP-originated memory cannot be confused with user-authored or first-party
  Friday-generated facts.
- MCP-originated memory carries freshness or revocation assumptions.
- Transcript exports preserve MCP provenance without exposing unsanitized secrets
  or raw quarantined output.

### Phase 4: Security, Telemetry, And Diagnostics Hardening

Goal:

- Make MCP operation observable and safe enough for local desktop use and future
  hosted use.

Work:

- Add redacted diagnostics for stdio command, env, cwd, SSE URL, and headers.
- Add timeout and truncation coverage for connection, list-tools, execution, and
  result feedback.
- Add concurrency and cancellation coverage for startup and tool execution.
- Add telemetry events for MCP lifecycle, registration, execution, budget, and
  memory-ingestion decisions.
- Add security tests for prompt-injection-like tool descriptions and outputs.
- Add separate tests for schema/description sanitization and output sanitization.
- Add failure-mode tests for invalid config, missing commands, missing URLs,
  duplicate server names, duplicate tool names, and collisions with native tools.

Acceptance:

- No secrets appear in telemetry, diagnostics, prompt context, transcript records,
  or memory metadata.
- Prompt-visible MCP content is wrapped or sanitized as untrusted external
  content.
- Schema/description sanitization preserves original-source provenance and
  sanitized-context diagnostics.
- Timeout, truncation, and connection failures produce actionable diagnostics.
- Concurrency limits and cancellation paths do not leak clients, subprocesses, or
  stale registry entries.

### Phase 5: Optional External MCP Config Include

Goal:

- Support operationally convenient MCP config files without creating a second
  configuration authority.

Work:

- Add optional `tools.providers.mcp.config_file`.
- Merge or override external config into the same typed `MCPConfig`.
- Define precedence between inline `config` and `config_file`.
- Add validation for missing files, invalid YAML, unsupported keys, and
  conflicting server names.
- Ensure diagnostics report external config path issues without exposing secrets.

Acceptance:

- Inline MCP config remains canonical.
- External config is normalized into the same runtime model.
- Precedence and diagnostics are documented and tested.
- `config_file` no longer has any silent-ignore path.

### Phase 6: Update User And Developer Guides

Goal:

- Document MCP client configuration and runtime behavior before the MCP
  enhancement work is considered complete.

Work:

- Update `docs/guides/05-tools.md` with MCP tools as a runtime tool provider,
  naming/prefix behavior, tool filtering, selected-mode defaults, and normal
  tool-loop execution.
- Update `docs/guides/10-configuration.md` with the canonical inline
  `tools.providers.mcp` YAML shape, required/optional server behavior, budget
  settings, security settings, ingestion settings, and any optional external
  include behavior if implemented.
- Update `docs/guides/11-advanced-topics.md` with MCP lifecycle, stdio/SSE
  transport considerations, security boundaries, prompt-injection handling,
  telemetry, and memory/provenance behavior.
- Update `docs/guides/13-troubleshooting.md` with MCP connection, tool
  discovery, tool binding, timeout, filtering, budget, truncation, startup, and
  shutdown diagnostics.
- Add a short warning in user-facing guides that MCP can add meaningful prompt
  overhead and that broad tool catalogs should be filtered.
- Document that MCP tool discovery is startup-only in the first implementation
  pass and that refresh/reload commands are deferred.
- Document how Friday Chat direct runs consume canonical MCP configuration.
- Document argument redaction behavior and the difference between redacted
  diagnostics, transcript metadata, and memory-ingested content.

Acceptance:

- The guides explain that inline `tools.providers.mcp` config is canonical.
- The guides show at least one stdio MCP server example.
- The guides explain how MCP tools interact with tool context budgeting and
  Friday memory provenance.
- The guides distinguish runtime provider discovery limits from per-turn Friday
  Chat tool selection limits.
- The guides document common failure modes and remediation steps.
- MCP implementation is not considered complete until these guide updates are
  done.

## 6. Open Questions

- Should the default provider budget be conservative enough for desktop users
  without model-specific tuning, or should defaults vary by configured model
  context window?
- Should original MCP tool-name filters be added as a separate config field?
- Should remote SSE MCP servers require a stricter default trust profile than
  local stdio servers?
- Should automatic long-term memory ingestion ever be supported for MCP tool
  calls, or should MCP output ingestion require an explicit user action?
- Should MCP resources be modeled as memory ingestion sources in a later plan?
- Should Friday expose a user command to show MCP server health separately from
  `/tools`?
- Should MCP tool metadata extend the shared `ToolDefinition` protocol, live in a
  registry sidecar, or remain MCP-wrapper specific with a public accessor?
- Should transcript exporters include full MCP provenance by default, or only
  when metadata export is explicitly enabled?
- What minimum memory retrieval floor should Friday preserve when MCP tool
  schemas consume most of the prompt budget?
- Should MCP argument hashes use a framework-local salt to avoid cross-system
  correlation?

## 7. Initial Validation Targets

Focused package validation:

```bash
uv run pytest packages/friday-mcp/tests_mcp
uv run pytest packages/friday-runtime/tests_runtime
uv run pytest packages/friday-chat/tests_chat
uv run pytest packages/friday-memory/tests_memory
uv run pytest packages/friday-tools/tests_tools
uv run pytest tests/integration
```

Focused static and formatting checks:

```bash
uv run mypy packages/friday-mcp packages/friday-runtime packages/friday-chat packages/friday-memory packages/friday-tools packages/friday-core
uv run ruff check packages/friday-mcp packages/friday-runtime packages/friday-chat packages/friday-memory packages/friday-tools packages/friday-core
git diff --check -- docs/guides docs/planning/queued/friday-mcp/build-plan.md
git diff --check
```

Required behavioral tests:

- MCP provider disabled keeps existing runtime behavior.
- MCP provider enabled with no servers starts cleanly.
- Optional MCP server failure starts with diagnostics.
- Required MCP server failure fails startup.
- Missing required MCP tool fails startup.
- `config_file` fails validation until Phase 5 implements it.
- Unknown MCP provider config keys fail validation.
- Duplicate server names fail validation.
- Tool-name collisions fail validation.
- Name normalization is deterministic and normalized-name collisions fail
  clearly.
- Large fake MCP catalogs are capped.
- Oversized schemas are rejected or excluded with diagnostics.
- Provider registration caps run before registry insertion.
- Friday Chat per-turn selection runs after runtime provider caps.
- Selected MCP schema tokens reduce memory retrieval budget.
- MCP schema selection preserves the minimum memory retrieval floor or fails with
  a clear budget diagnostic.
- MCP tool results are truncated before model feedback when over result budget.
- MCP tool-call arguments are redacted or hashed according to policy in
  diagnostics, transcripts, and memory paths.
- MCP output is not ingested into long-term memory by default.
- MCP transcript/memory records preserve provenance and sanitization metadata.
- MCP tool-call provenance is preserved per call when multiple MCP tools execute
  in one turn.
- Transcript JSONL, Markdown, and CSV exporters preserve MCP provenance according
  to metadata export settings.
- MCP schema/description sanitization is tested separately from output
  sanitization.
- MCP tool discovery is startup-only in the first implementation pass, and
  refresh/reload behavior is explicitly deferred.
- MCP startup and execution concurrency limits are tested.
- Cancellation during MCP startup and shutdown does not leak clients or registry
  state.
- Friday Chat direct-run config normalizes into canonical runtime MCP config.
- Telemetry and diagnostics redact env/header/API-key values.

Repo-wide validation should be run after the framework validation gate
restoration work is complete:

```bash
uv run pytest
uv run mypy packages tests main.py
uv run ruff check .
```

## 8. Completion Criteria

- MCP client tools can be configured through inline `tools.providers.mcp`.
- Unsupported MCP config keys fail validation.
- MCP tools register through the runtime tool provider path and execute through
  normal Friday tool-calling flows.
- MCP provider discovery is async, lifecycle-owned, and shut down cleanly.
- Required and optional server failure semantics are implemented and tested.
- MCP tool schemas participate in context budgeting and filtering.
- Runtime provider caps run before registry insertion; Friday Chat per-turn
  selection runs after registration.
- Large MCP catalogs and oversized schemas cannot exceed configured prompt
  budgets.
- MCP schema selection preserves the defined memory retrieval floor or produces a
  clear diagnostic.
- Memory retrieval receives budget remaining after selected tool schemas and
  reserved output buffers are accounted for.
- MCP tool outputs have explicit sanitization, truncation, provenance, and
  storage behavior.
- MCP tool metadata and tool-call provenance have typed cross-package contracts.
- MCP transcript exporters preserve provenance according to documented metadata
  export settings.
- MCP discovery is startup-only for the first implementation pass; refresh/reload
  behavior is explicitly deferred.
- MCP startup and execution concurrency are bounded and cancellation-safe.
- MCP tool-call arguments are redacted, hashed, or stored according to documented
  policy.
- Long-term memory ingestion for MCP output is disabled by default.
- Runtime diagnostics and telemetry redact secrets.
- Existing typing-policy debt touched by MCP work is remediated or explicitly
  tracked.
- `docs/guides/05-tools.md`, `docs/guides/10-configuration.md`,
  `docs/guides/11-advanced-topics.md`, and
  `docs/guides/13-troubleshooting.md` are updated before closeout.
