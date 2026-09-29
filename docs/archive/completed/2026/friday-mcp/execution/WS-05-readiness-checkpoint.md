# MCP-WS-05 Readiness Checkpoint

Date: 2026-09-28
Preparation HEAD: `1e845001f6b6c48e7cc255ac76460a058f026f70`
Branch: `feature/friday-mcp-ws04-chat-budget`
Status: Planning reconciliation complete; WS-05 implementation approval pending
Phase/state: `planning` / `not_ready`

## Accepted Handoff And Current Authority

WS-00 through WS-04 are explicitly accepted. WS-04's frozen product candidate
`53d76d45cedea16122436e53b178de074c5bc322` and complete fresh
[VAL-010](../validation/VAL-010-report.md) remain intact. The maintainer's
"proceed" follows the recorded next gate to reconcile WS-05/readiness before
separate approval. This checkpoint changes planning artifacts only; it grants
no WS-05 product authority, creates no new branch, and dispatches no validator.

The [reconciled directive](../directives/ws-05-execution-provenance-transcript.md)
is complete and reviewable: exact 23-path manifest, eight tactical tasks, ten
acceptance criteria, migration/export decisions, required tests/checks and stops.
After explicit approval, pin this planning checkpoint as work-unit base, create
`feature/friday-mcp-ws05-execution`, record approval/start, then implement.

## Live Read-Only Findings

| Public boundary | Verified gap | Bounded proposed remedy |
| --- | --- | --- |
| MCP Chat bridge / ToolLoop | Exact original Read.File routing works; configured 64-byte cap returned 119 UTF-8 bytes. | Reuse routing/ownership; bound the complete safe result including sanitizer wrapping and notices. |
| ToolCallRecord / production SQLite adapter / JSONL | Synthetic argument sentinel survives record and JSONL; no typed per-call MCP provenance. | Redact all MCP arguments and retain atomic typed provenance before return/model capture or persistence. |
| Shared public sanitizer defaults | Warn action retains detected injection content; wrapping expands output. | Explicit block/drop consumer policy, full retained-prefix scanning, final byte cap and safe untrusted envelope. Shared source stays read-only. |
| MCPClientBase.call_tool | isError true returns error text as ordinary success. | Narrow static protocol-failure interpretation; successful string API retained. |

The executable local stdio/SQLite/JSONL/request-double probe and all original
attempt logs are preserved in [readiness evidence](WS-05-readiness-evidence.yaml).
Final command exited 0. Two earlier scratch-harness failures are disclosed:
incomplete abstract request double/nonexistent close, then a reused scratch
SQLite entry ID. They are not product findings; existing state was preserved,
and the final probe used a unique database. The bridge stops in `finally`.
All inputs were synthetic; no live/paid provider, credentials or external service.
This is controller readiness evidence, not independent WS-05 validation.

Source inspection also identifies original assistant request arguments in
continuation/raw prompt/response capture, possible exhausted-loop responses,
and pending transcript context logs. A pure sanitizer helper test cannot prove
these boundaries: the directive requires real TurnProcessor, fake and production
adapters, both tool-turn modes, all exporters and direct public bridge coverage.

## Resolved Architecture And Product Choices

- Accepted public Core provenance is the one cross-package contract. Add only
  optional nonnegative original/final UTF-8 sizes and fixed safe failure codes.
- Fully redact argument objects to `{}`; do not implement hashes. This follows
  accepted WS-00 rather than old generic hash proposals.
- Keep original arguments transiently for exact execution. Only checked bounded
  output and safe typed records cross model/return/diagnostic/capture boundaries.
- Reuse public Core sanitizer with explicit block/drop settings and no raw
  quarantine/detection logging; cover the entire retained prefix and wrapper
  expansion. Reject impossible tiny caps before RPC with a fixed safe error.
- Recognize protocol isError and malformed call results in the existing client;
  keep discovery, transport, lifecycle and timeout contracts unchanged.
- Use the real transcript adapter and additive optional typed call/result fields.
  Declare Core in Transcript metadata and only its workspace lock edge. Existing
  SQLite JSON serialization/loading needs no schema migration/store edit.
- JSONL keeps full provenance when metadata is enabled. Markdown keeps tool-call
  display opt-in; CSV keeps existing columns. Human exports show bounded safe
  summaries; old/native payload shape and export controls remain compatible.
- Correlate distinct calls with safe unique IDs and actual persisted entry IDs.
  Preserve native IDs; no invented memory/correlation records.

No long-term MCP ingestion, telemetry, command, selection/budget/config change,
shared Agent/security refactor, live refresh or later-slice work is included.
Ordinary conversation-memory behavior remains unchanged. The policy bounds
outbound text and known injection handling, not inbound wire allocations,
universal secret detection or exact multi-call token consumption.

## Validation, Preservation And Exit Gate

The directive requires focused/package/Core/MCP/Runtime/Memory/Agent/integration
regressions, Ruff, broad and unfiltered meaningful Python-3.13 typing, dependency
lock/distribution checks, documentation/board checks, public local-peer UAT and
fresh read-only complete-aggregate VAL-011 after a stable candidate. Historical
VAL-010/009 baseline failures are references, not waivers or fresh WS-05 results;
they must be independently reproduced and separated from regressions.

Readiness closeout checks passed before the local planning commit:
`friday-dev-board.py validate` (23 tasks), `next`/`show` (matching approval gate),
`render --check`, `check-documentation-lifecycle.py` (349 Markdown files),
`git diff --check`, directive/checkpoint relative links, and all seven exact
readiness archive member hashes/sizes. The controller freeze check confirms all
29 pinned VAL-010 authority/report inputs, its request/report/evidence, 971
tracked product files and five unrelated paths unchanged. Its predecessor
check also confirms 24 pinned VAL-009 inputs and 961 files outside WS-04 scope.
Unrelated paths: `.DS_Store`, deleted `family-tree.md`, `docker-bench-security/`,
Chat `config.example.yaml.pre-typed-llm-20260828.bak`, and sandbox
`docker/Dockerfile.audit`. No broad staging or runtime-state cleanup is authorized.

Next gate: **explicit approval of the reconciled WS-05 construction directive**.
AGENTS.md requires an "approved construction directive" before product edits;
this planning result supplies the complete bounded proposal for that decision.
WS-04 remains accepted and the wider initiative remains started/local.
