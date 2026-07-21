# Build Plan: Friday Framework MCP Enhancements

**Status:** Draft
**Target:** MCP client capability across Friday runtime, tools, memory, and app
layers
**Objective:** Add configurable MCP client support to the Friday framework while
preserving existing tool-calling, memory, context-management, security, and
runtime-boundary contracts.

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
        servers:
          - name: filesystem
            enabled: true
            transport: stdio
            command: npx
            args:
              - -y
              - "@modelcontextprotocol/server-filesystem"
              - /path/to/workspace
            env: {}
            timeout_seconds: 30
            retry_attempts: 3
```

Optional future include shape:

```yaml
tools:
  providers:
    mcp:
      enabled: true
      config_file: ./mcp.servers.yaml
```

If `config_file` is later added, inline and external configuration must still
normalize into one `MCPConfig` instance before runtime construction.

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

The current gap is runtime integration. `friday_runtime.tool_loading` currently
raises a `ToolProviderLoadError` when `tools.providers.mcp.enabled` is true.

## 3. Desired Architecture

Keep package responsibilities explicit:

| Package | Responsibility |
| --- | --- |
| `friday-mcp` | MCP transports, client manager, server manager, protocol adapters |
| `friday-runtime` | Lifecycle, typed config loading, MCP connection startup/shutdown, tool registration |
| `friday-tools` | Native Friday tool library and common tool contracts |
| `friday-memory` | Tool-context budgeting, provenance-aware storage, optional MCP output ingestion |
| `friday-agent` | Agent profiles, tool binding validation, workflows, orchestration |
| `friday-chat` | App-layer tool loop and user-facing command integration |
| `friday-core` | Shared protocols and boundary contracts |

MCP tools should enter the system through the same runtime registry path as
builtin and `friday-tools` tools. Friday Chat and agents should not need a
special MCP execution path for normal tool calls.

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
- Tool context budgeting should treat MCP tools like other tools.
- One config file is easier to validate, test, and reproduce.

### 4.2 Runtime Lifecycle

MCP client setup is async. Runtime integration should happen inside runtime
startup, not inside a synchronous helper that cannot connect or list tools.

Required lifecycle behavior:

- Connect enabled MCP servers during runtime boot when `auto_connect` is true.
- Register discovered MCP tools into the runtime tool registry.
- Preserve per-server connection status and diagnostics.
- Disconnect all MCP clients during runtime shutdown.
- Surface connection failures without silently dropping configured required
  tools.

### 4.3 Tool Registration And Naming

MCP tool names need stable, collision-resistant names.

Default naming:

```text
mcp_<server_name>_<tool_name>
```

Required behavior:

- Detect collisions with builtin, `friday-tools`, and other MCP tools.
- Apply include/exclude filters after prefixing, or clearly document whether
  filters match original names, prefixed names, or both.
- Preserve the original MCP server/tool name in tool metadata for provenance and
  debugging.

### 4.4 Context Budgeting

MCP servers can expose many tools with large schemas. MCP must use the existing
tool context and budgeting system.

Required behavior:

- Respect max-tool and schema-token budgets.
- Support provider-level include/exclude filters.
- Avoid injecting every MCP tool into every turn by default.
- Keep `/tools`, `/inject-tools`, `/recommend-tools`, and `/tool-budget`
  behavior coherent with MCP tools.

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

Initial default:

- MCP tool outputs may be fed back into the model after sanitization.
- Long-term ingestion of MCP outputs should be opt-in until provenance,
  refresh, and retention semantics are explicit.

### 4.6 Security

Treat MCP tool schemas, descriptions, resources, prompts, and outputs as
untrusted external content.

Security requirements:

- Sanitize tool descriptions before prompt/context inclusion where applicable.
- Sanitize tool outputs before LLM feedback.
- Sanitize or quarantine stored memory content.
- Preserve existing prompt-injection wrapping for tool results.
- Enforce timeouts on connection and tool execution.
- Avoid passing secrets from Friday config into model-visible context.
- Treat stdio server command, args, env, and cwd as sensitive runtime
  configuration.

### 4.7 MCP Resources And Prompts

MCP supports more than tools. For the first implementation pass, this plan
should be tools-only unless explicitly expanded.

Deferred areas:

- MCP resources as memory-ingestion sources.
- MCP prompts as reusable Friday prompt fragments.
- MCP resource subscriptions or refresh policies.

Those capabilities require separate provenance, freshness, retention, and
security decisions.

### 4.8 Telemetry And Diagnostics

MCP integration should emit structured diagnostics.

Useful events:

- server connection attempted
- server connection succeeded or failed
- tools listed
- tool registered
- tool call started
- tool call succeeded, failed, or timed out
- server disconnected

Telemetry should include server name, transport, tool name, duration,
success/failure status, and sanitized error classification.

### 4.9 Agent And Workflow Compatibility

Agent profile and workflow validation must account for MCP tools.

Required behavior:

- MCP tools are loaded before validating agent tool bindings.
- Profiles may reference prefixed MCP tool names.
- Missing required MCP tools fail clearly when their server is disabled,
  unavailable, or filtered out.
- Workflow execution can use MCP tools through the same registry path as other
  tools.

## 5. Candidate Implementation Phases

### Phase 1: Runtime MCP Tool Provider

Goal:

- Make `tools.providers.mcp.enabled=true` register MCP tools instead of raising
  "not implemented."

Work:

- Move MCP tool loading into an async runtime boot step.
- Store `MCPClientManager` on the runtime DI container.
- Register MCP tool wrappers into the runtime tool registry.
- Disconnect clients during shutdown.
- Add fake MCP client coverage so tests do not require external servers.

Acceptance:

- MCP provider can be enabled in runtime config.
- Fake MCP tools appear in the runtime registry.
- Runtime shutdown disconnects MCP clients.
- Connection failures are visible in diagnostics.

### Phase 2: Tool Context And Friday Chat Compatibility

Goal:

- Ensure MCP tools flow through Friday Chat and tool-context behavior like
  native tools.

Work:

- Verify MCP schemas participate in tool budget calculations.
- Verify `/tools`, `/inject-tools`, `/recommend-tools`, and `/tool-budget`
  include MCP tools correctly.
- Verify a normal Friday Chat turn can execute an MCP tool call.
- Preserve tool-call provenance in raw prompt/response and transcript records.

Acceptance:

- MCP tool calls execute through the normal tool loop.
- Tool schemas do not exceed configured context budgets.
- MCP tools can be selected and filtered through existing command surfaces.

### Phase 3: Memory Provenance And Optional Ingestion

Goal:

- Make MCP tool-output storage safe and traceable.

Work:

- Add MCP provenance metadata for tool results.
- Decide and implement opt-in ingestion controls.
- Ensure sanitized output and memory-storage output remain distinct.
- Add tests for provenance, sanitization, and disabled ingestion defaults.

Acceptance:

- MCP tool results stored in transcript and/or memory have clear provenance.
- Long-term memory ingestion is disabled by default or explicitly configured.
- Sanitization stats and provenance are preserved.

### Phase 4: Optional External MCP Config Include

Goal:

- Support operationally convenient MCP config files without creating a second
  configuration authority.

Work:

- Add optional `tools.providers.mcp.config_file`.
- Merge or override external config into the same typed `MCPConfig`.
- Define precedence between inline `config` and `config_file`.
- Add validation for missing files, invalid YAML, and conflicting server names.

Acceptance:

- Inline MCP config remains canonical.
- External config is normalized into the same runtime model.
- Precedence and diagnostics are documented and tested.

### Phase 5: Update User And Developer Guides

Goal:

- Document MCP client configuration and runtime behavior before the MCP
  enhancement work is considered complete.

Work:

- Update `docs/guides/05-tools.md` with MCP tools as a runtime tool provider,
  naming/prefix behavior, tool filtering, and normal tool-loop execution.
- Update `docs/guides/10-configuration.md` with the canonical inline
  `tools.providers.mcp` YAML shape and any optional external include behavior if
  implemented.
- Update `docs/guides/11-advanced-topics.md` with MCP lifecycle, stdio/SSE
  transport considerations, security boundaries, and memory/provenance behavior.
- Update `docs/guides/13-troubleshooting.md` with MCP connection, tool
  discovery, tool binding, timeout, filtering, and shutdown diagnostics.

Acceptance:

- The guides explain that inline `tools.providers.mcp` config is canonical.
- The guides show at least one stdio MCP server example.
- The guides explain how MCP tools interact with tool context budgeting and
  Friday memory provenance.
- The guides document common failure modes and remediation steps.
- MCP implementation is not considered complete until these guide updates are
  done.

## 6. Open Questions

- Should MCP server failures be fatal by default when `enabled=true`, or should
  each server have a `required` flag?
- Should include/exclude filters match original MCP tool names, prefixed names,
  or both?
- Should MCP tool descriptions be sanitized at registration time, prompt
  assembly time, or both?
- Should MCP resources be modeled as memory ingestion sources in a later plan?
- Should remote SSE MCP servers require a stricter trust profile than local
  stdio servers?
- Should MCP tool calls be eligible for automatic long-term memory ingestion, or
  only explicit ingestion?

## 7. Initial Validation Targets

```bash
uv run pytest packages/friday-mcp/tests_mcp
uv run pytest packages/friday-runtime/tests_runtime
uv run pytest packages/friday-chat/tests_chat
uv run mypy packages/friday-mcp packages/friday-runtime packages/friday-chat
uv run ruff check packages/friday-mcp packages/friday-runtime packages/friday-chat
git diff --check -- docs/guides
git diff --check
```

Repo-wide validation should be run after the framework validation gate
restoration work is complete:

```bash
uv run pytest
uv run mypy packages tests main.py
uv run ruff check .
```

## 8. Completion Criteria

- MCP client tools can be configured through inline `tools.providers.mcp`.
- MCP tools register through the runtime tool provider path and execute through
  normal Friday tool-calling flows.
- MCP tool schemas participate in context budgeting and filtering.
- MCP tool outputs have explicit sanitization and provenance behavior.
- Runtime shutdown disconnects MCP clients.
- `docs/guides/05-tools.md`, `docs/guides/10-configuration.md`,
  `docs/guides/11-advanced-topics.md`, and
  `docs/guides/13-troubleshooting.md` are updated before closeout.
