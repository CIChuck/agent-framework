# Construction Directive: MCP-WS-05 Tool Execution Security, Provenance, And Transcript Recording

Status: Draft construction directive  
Date: 2026-07-24  
Tactical plan: [Friday Framework MCP Tactical Implementation Plan](../planning/friday-framework-mcp-tactical-implementation-plan.md)  
Workstream: `MCP-WS-05`

## AI Builder Role

You are the implementation agent for MCP tool execution provenance and transcript safety. Your job is to ensure MCP calls produce bounded, sanitized, redacted, traceable records before tool results re-enter the model or are persisted to transcript storage.

## Source Authority And Precedence

1. [Repository engineering policy](../reference/policies/repository-engineering-policy.md)
2. [Friday Framework MCP tactical implementation plan](../planning/friday-framework-mcp-tactical-implementation-plan.md)
3. [Friday Framework MCP enhancements build plan](../planning/build-plans/friday-framework-mcp-enhancements.md)
4. Completed `MCP-WS-00`, `MCP-WS-03`, and `MCP-WS-04`
5. Current Friday Chat tool loop and transcript source

## Implementation Objective

Extend MCP tool execution handling so every MCP call records provider provenance, redacts or hashes arguments, enforces result byte limits, sanitizes output before model re-entry, and persists transcript metadata without leaking secrets or unsafe raw content.

## Allowed Scope

You may edit:

- `packages/friday-chat/src/friday_chat/tools/schemas.py`
- `packages/friday-chat/src/friday_chat/turns/processor.py`
- `packages/friday-chat/src/friday_chat/tools/`
- `packages/friday-transcript/src/friday_transcript/models/transcript.py`
- `packages/friday-transcript/src/friday_transcript/export/`
- `packages/friday-agent/src/friday_agent/security/output_processor.py` only if the existing sanitizer is the right shared implementation point
- `packages/friday-chat/tests_chat/`
- `packages/friday-transcript/tests/`
- package-local tests for any sanitizer code touched

## Explicit Non-Goals

- Do not enable long-term memory ingestion.
- Do not preserve unsanitized raw outputs outside an explicit quarantine policy.
- Do not add telemetry event emission except where tests need a redacted event payload contract for later phases.
- Do not change runtime discovery or registry behavior.
- Do not change Friday Chat tool selection budgets beyond using existing configured result limits.
- Do not implement resources, prompts, live refresh, server exposure, or external config includes.

## Required Workstreams

### `MCP-05-01`: Extend Tool Call Record

Extend or replace Friday Chat `ToolCallRecord` so MCP calls can record:

- provider type;
- server name;
- original MCP tool name;
- canonical Friday tool name;
- transport;
- call ID;
- trust level;
- sanitization status;
- truncation status;
- result byte size;
- schema status if available;
- transcript entry ID when known;
- optional memory record ID reserved for later phases.

Native tool call records must remain supported.

### `MCP-05-02`: Redact Or Hash Arguments

Before diagnostics, transcript persistence, telemetry, or memory ingestion, redact or hash tool arguments according to `MCP-WS-00` policy.

Do not persist raw secret-like arguments by default.

### `MCP-05-03`: Enforce `max_result_bytes`

Limit MCP tool results before they are passed back to the model. Truncation must be explicit in provenance. The model-facing tool result should indicate truncation without exposing omitted content.

### `MCP-05-04`: Sanitize Tool Outputs Before Model Re-Entry

Apply output sanitization before constructing tool-result messages. Unsafe MCP output must not be injected into the model unchanged.

### `MCP-05-05`: Add Per-Call Metadata

Keep per-call metadata separate from turn-level metadata. A turn with multiple MCP calls must preserve distinct provenance for each call.

### `MCP-05-06`: Persist Transcript Provenance

Persist MCP provenance in transcript entries. JSONL export must preserve the structured provenance.

### `MCP-05-07`: Decide Markdown And CSV Export Behavior

Decide whether Markdown and CSV transcript exporters include summarized MCP provenance by default. If full provenance is too verbose, keep full provenance JSONL-only and add summary fields to Markdown or CSV.

### `MCP-05-08`: Record Failure Provenance

Failed MCP tool calls must produce failure provenance without leaking raw unsafe output, full arguments, env, headers, or server secrets.

## Migration And Removal Instructions

Preserve existing transcript readability and backwards compatibility where practical. If transcript schema changes are breaking, add compatibility handling for older transcript entries.

Do not delete existing native tool-call recording behavior. Extend it so native and MCP records can coexist.

## Security And Governance Requirements

- Raw MCP output is untrusted.
- Sanitize before model re-entry.
- Enforce result byte limits before persistence and model re-entry.
- Redact or hash arguments before diagnostics and transcript storage.
- Do not emit secrets in exception messages.
- Use explicit exceptions for essential invariants.
- Do not add broad mypy suppressions.

## Testing Requirements

Add tests for:

- MCP provenance construction;
- native tool record compatibility;
- argument redaction;
- argument hashing;
- secret-like argument values;
- result truncation;
- truncation status in provenance;
- output sanitization;
- unsafe output content;
- failed MCP call provenance;
- multiple MCP calls in one turn;
- transcript JSONL preservation;
- Markdown and CSV export behavior if changed.

Negative tests are mandatory for secret leakage, oversized outputs, unsafe output content, failed tool execution, and missing provenance.

## Verification Commands

Run:

```bash
uv run pytest packages/friday-chat/tests_chat
uv run pytest packages/friday-transcript/tests
uv run pytest packages/friday-agent/tests_agent
uv run ruff check packages/friday-chat packages/friday-transcript packages/friday-agent
uv run mypy packages/friday-chat packages/friday-transcript packages/friday-agent
```

If cross-package transcript integration is touched, also run:

```bash
uv run pytest tests/integration
```

## CLI, API, And UAT Requirements

CLI:

- Existing Friday Chat command behavior must remain compatible.
- No new command is required.

API:

- Tool call provenance must be accessible as structured data.
- Transcript export APIs must preserve or summarize MCP provenance according to the documented decision.

UAT:

- Execute a fake MCP tool and inspect transcript JSONL provenance.
- Execute a fake MCP tool with a large result and verify truncation.
- Execute a failing fake MCP tool and verify redacted failure provenance.
- Verify native tool transcript records still work.

## Documentation Close-Out

Do not complete user-facing docs in this phase. Record transcript exporter decisions for `MCP-WS-08`.

## Reporting Requirements

Report:

- files changed;
- provenance fields implemented;
- argument redaction or hash behavior;
- result truncation behavior;
- output sanitizer used;
- transcript schema and exporter behavior;
- compatibility notes for old transcript records;
- verification commands and results;
- skipped checks;
- follow-up required for memory ingestion.

## Stop Conditions

Stop if:

- prior workstreams are incomplete;
- argument redaction or hashing policy is unresolved;
- output sanitization cannot occur before model re-entry;
- transcript schema changes would break existing exports without compatibility handling;
- implementation requires enabling long-term memory ingestion, telemetry emission, live refresh, resources, prompts, or external config includes.
