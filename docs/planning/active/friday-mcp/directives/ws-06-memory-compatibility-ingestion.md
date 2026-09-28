# Construction Directive: MCP-WS-06 Memory Compatibility And Optional MCP Ingestion

Status: Draft construction directive
Date: 2026-07-24
Tactical plan: [Friday Framework MCP Tactical Implementation Plan](../tactical-plan.md)
Workstream: `MCP-WS-06`

## AI Builder Role

You are the implementation agent for MCP compatibility with Friday memory. Your job is to make memory retrieval budget-aware and provenance-aware while keeping long-term MCP output ingestion disabled by default.

## Source Authority And Precedence

1. [Repository engineering policy](../../../../reference/policies/repository-engineering-policy.md)
2. [Friday Framework MCP tactical implementation plan](../tactical-plan.md)
3. [Friday Framework MCP enhancements build plan](../build-plan.md)
4. Completed `MCP-WS-04` and `MCP-WS-05`
5. Current Friday memory, Friday Chat memory adapter, and transcript source

## Implementation Objective

Integrate MCP provenance into Friday memory behavior so MCP-derived content can be safely excluded, labeled, optionally ingested, sanitized, quarantined, and retrieved under explicit budget control.

## Allowed Scope

You may edit:

- `packages/friday-memory/src/friday_memory/`
- `packages/friday-memory/tests_memory/`
- `packages/friday-chat/src/friday_chat/turns/processor.py`
- `packages/friday-chat/src/friday_chat/memory/`
- `packages/friday-chat/tests_chat/`
- `packages/friday-transcript/src/friday_transcript/models/transcript.py` only for linking transcript IDs to memory provenance
- `packages/friday-core/src/friday_core/` only for shared provenance contracts

Do not edit runtime lifecycle, MCP discovery, registry behavior, or telemetry event emission unless a narrow type import is required.

## Explicit Non-Goals

- Do not enable MCP long-term memory ingestion by default.
- Do not ingest MCP resources or prompts.
- Do not implement automatic revocation when an external MCP source changes.
- Do not implement live MCP refresh.
- Do not expose raw untrusted MCP output in memory.
- Do not add a memory UI.
- Do not add external MCP config includes.

## Required Workstreams

### `MCP-06-01`: Memory-Facing MCP Provenance Fields

Add memory-facing provenance for:

- `source_type=mcp_tool`;
- MCP server name;
- canonical Friday tool name;
- original MCP tool name;
- MCP call ID;
- transcript entry ID;
- memory record ID;
- trust level;
- ingestion policy;
- sanitization status;
- truncation status;
- freshness assumptions;
- revocation assumptions.

### `MCP-06-02`: Keep Ingestion Disabled By Default

The default behavior is transcript recording only, not long-term memory storage. Tests must prove MCP tool output does not enter long-term memory unless explicitly configured.

### `MCP-06-03`: Per-Server And Per-Tool Allowlists

If ingestion is enabled, support per-server and per-tool allowlists. Do not allow broad ingestion without explicit policy.

### `MCP-06-04`: Sanitization And Quarantine

Apply memory-specific sanitization before storage. Unsafe or untrusted MCP output must either be rejected or routed through quarantine policy.

Do not store raw unsanitized output in normal long-term memory.

### `MCP-06-05`: Freshness And Revocation Assumptions

Record assumptions that MCP-derived memory may be stale and that automatic revocation is not implemented in this phase.

### `MCP-06-06`: Retrieval Budget Inputs

Ensure retrieval budget calculation accounts for selected tool schema tokens and reserved result tokens from `MCP-WS-04`.

Do not re-derive unrelated budget behavior differently in memory. The turn processor remains the owner of per-turn allocation; memory should receive and respect the computed token limit.

### `MCP-06-07`: Query-Time Provenance Labels

Retrieved MCP-derived memories must be distinguishable from conversation, file, transcript, and native tool memories. Add labels or metadata that allow later filtering and display.

## Migration And Removal Instructions

Preserve existing memory records and retrieval behavior. Additive provenance fields must remain compatible with older records that do not have MCP metadata.

If a storage schema migration is required, make it explicit, reversible where practical, and test old-record compatibility.

## Security And Governance Requirements

- Treat MCP output as untrusted.
- Long-term ingestion must be opt-in.
- Apply sanitization before storage.
- Preserve provenance on every ingested MCP record.
- Do not store raw arguments or raw unsafe outputs by default.
- Do not leak secrets through memory metadata.
- Use explicit exceptions for required provenance invariants.
- Do not add broad mypy suppressions.

## Testing Requirements

Add tests for:

- MCP ingestion disabled by default;
- transcript-only MCP output flow;
- explicit ingestion enabled;
- per-server allowlist;
- per-tool allowlist;
- rejected unallowlisted tool output;
- provenance labels;
- sanitization before storage;
- quarantine or rejection of unsafe output;
- oversized output handling;
- missing provenance rejection;
- stale-source metadata;
- retrieval of MCP-derived memory with labels;
- compatibility with older non-MCP memory records;
- memory retrieval respecting token limit from Friday Chat.

Negative tests are mandatory for untrusted outputs, oversized outputs, disabled ingestion, missing provenance, and unallowlisted tools.

## Verification Commands

Run:

```bash
uv run pytest packages/friday-memory/tests_memory
uv run pytest packages/friday-chat/tests_chat
uv run pytest packages/friday-transcript/tests
uv run ruff check packages/friday-memory packages/friday-chat packages/friday-transcript packages/friday-core
uv run mypy packages/friday-memory packages/friday-chat packages/friday-transcript packages/friday-core
```

If memory integration crosses package boundaries, also run:

```bash
uv run pytest tests/integration
```

## CLI, API, And UAT Requirements

CLI:

- No new CLI command is required.
- Existing Friday Chat behavior must remain compatible when MCP ingestion is disabled.

API:

- Memory APIs must preserve and return MCP provenance metadata when records are ingested.
- Retrieval APIs must allow MCP-derived records to be identified by source labels.

UAT:

- Execute an MCP tool and verify transcript contains the call but long-term memory does not by default.
- Enable MCP ingestion for a specific server/tool and verify the record is stored with provenance.
- Retrieve memory and verify MCP-derived source labels.
- Attempt ingestion of untrusted unsafe output and verify quarantine or rejection.

## Documentation Close-Out

Record user-facing memory behavior for `MCP-WS-08`:

- transcript records are allowed by default;
- long-term memory ingestion is disabled by default;
- ingestion requires explicit allowlists;
- MCP-derived memory carries source and trust labels.

Do not write the final user guide unless this phase is being combined with `MCP-WS-08`.

## Reporting Requirements

Report:

- files changed;
- default ingestion behavior;
- allowlist behavior;
- provenance fields stored;
- sanitization and quarantine behavior;
- retrieval label behavior;
- migration compatibility notes;
- verification commands and results;
- skipped checks;
- follow-up required for telemetry and docs.

## Stop Conditions

Stop if:

- prior Friday Chat budget and provenance phases are incomplete;
- MCP ingestion would be enabled by default;
- memory storage cannot preserve provenance;
- unsafe output would have to be stored unsanitized;
- schema migration would break old memory records without compatibility handling;
- implementation requires MCP resources, prompts, live refresh, external config includes, or telemetry service changes.
