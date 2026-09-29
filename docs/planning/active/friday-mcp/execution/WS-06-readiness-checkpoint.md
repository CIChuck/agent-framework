# MCP-WS-06 Readiness Checkpoint

Date: 2026-09-29
Preparation HEAD: `6890771127e405f3299ed783296174366c67f995`
Branch: `feature/friday-mcp-ws05-execution`
Status: Planning reconciliation complete; bounded implementation approval pending
Phase/state: `planning` / `not_ready`

## Accepted Handoff And Authority

WS-00 through WS-05 are explicitly accepted. Frozen WS-05
`cca86b51105666d12c2e7ed571f8f9a05d2085f9` and complete fresh
[VAL-013](../validation/VAL-013-report.md) remain intact. The maintainer's
"proceed" follows the recorded planning/readiness gate. No product edit, new
execution branch or reviewer dispatch occurred in this preparation.

The [reconciled directive](../directives/ws-06-memory-compatibility-ingestion.md)
binds 18 paths, seven tactical tasks, ten criteria, safety/failure/compatibility
choices, required commands and independent review. It remains unapproved.
After approval, pin this planning commit as the WS-06 base, create
`feature/friday-mcp-ws06-memory`, record approval/start and implement the manifest.

## Current Source Findings

| Boundary and inspected source | Readiness finding and bounded resolution |
| --- | --- |
| Core `mcp.py:98-124` | The accepted policy already has disabled default, required sanitation, byte cap and exact safe server/canonical-tool lists. Reuse it; define union-of-explicit-grants matching without new settings. |
| Chat `adapters.py:251-291,573` | Actual memory integration is FrameworkMemoryAdapter over MemoryController, not a Chat memory directory. Use optional typed adapter capabilities and public storage interfaces. |
| Chat `turns/processor.py:300-325` | WS-04 already computes schema/result-reduced budget and supplies token_limit before retrieval. Preserve it once; account for new labels within residual estimated budget. |
| Chat `adapters.py:2333-2375` | Payload flattening currently returns passage/insight text without MCP source labels. Add validated labeled/excludable MCP formatting; preserve ordinary snippets. |
| Memory `ingestion/tool_ingester.py` | Generic native ingester is default-enabled and lacks typed MCP grants/provenance. Keep it unchanged; create a separate disabled-by-default MCP snapshot path. |
| Chat `turns/processor.py:571-623`, `adapters.py:1107-1208` | Persistence currently stores conversation, builds a fresh turn ID inline and appends paired facts; no durable memory receipt. Allocate once, stage safe pending records, verify paired transcript readback and then publish. |
| Transcript `stores/protocol.py:93-108`, `stores/sqlite.py:956-1024` | Entries are append-only; append returns bool and get_entry is public. Preserve stores/models/exporters; optional Chat receipt verifies the real append without rewriting entries. |
| Memory `retrieval/collection_manager.py:262-270,434`, `models/vector_metadata.py` | Retrieval eligibility only quarantines maintenance synthesis; promotion copies existing metadata. Add MCP pending/malformed gates, prevent pending promotion and prove typed metadata survives committed stage movement. |
| Memory `maintenance/mutation.py:433-468,537-751` | Typed maintenance eligibility can otherwise treat stored text as ordinary duplicate/synthesis input. Add only an MCP exclusion guard; keep native plan behavior. Generic synthesis filters type=insight; snapshots use their own type. |

This is controller source-based readiness, not a WS-06 implementation or
independent validation verdict. [Readiness evidence](WS-06-readiness-evidence.yaml)
pins inspected source bytes, original draft, accepted candidate and preservation.
No live provider, external MCP service, real credentials or runtime databases
were used; no product behavior tests are claimed for this planning-only change.

## Resolved Proposal

- Direct MCP semantic ingestion stays off by default. Ordinary assistant/user
  conversation storage is unaffected; there is no global taint-tracking promise.
- Enabled plus exact server OR canonical-tool grant authorizes one sanitized
  snapshot per eligible completed call. Both lists are a union; no wildcards.
- Store typed bounded provenance with actual call/entry/memory IDs. Use a distinct
  record kind and explicit reject policy for unsafe/oversized content; no raw quarantine.
- Stage non-retrievable records, verify durable storage, append truthful paired
  transcript facts, read back the actual entry and only then publish. Crash/cleanup
  failures can leave excluded pending records; no automatic recovery is added.
  Publication failure after an immutable stored receipt must preserve that record.
- Add source/trust/freshness labels and query exclusion. Count wrapper/label cost
  before including new MCP snippets; reuse the exact supplied WS-04 budget.
- Capture-time snapshot/no-revocation assumptions remain honest through reload and
  stage movement. Maintenance cannot transform snapshots into ordinary facts.
- Additive metadata and optional public capabilities preserve old/custom/native
  consumers. No Core contract, transcript store/schema, dependency or config changes.

The draft's broad shared-Core/transcript/model scopes are unnecessary. The new
manifest confines product work to Memory and Chat plus regression tests. Touched
CollectionManager's existing file-wide typing suppression must be removed with
local typed repairs; any required outside-file fix returns to scope reconciliation.

## Checks, Preservation And Exit Gate

Board validate passed (23 tasks); next/show agree with the planning-only gate.
Ordinary `uv run` attempted to rebuild Transcript and could not resolve hatchling
because PyPI DNS/network was unavailable. The same board operations passed with
`uv run --no-sync` in the installed environment. This does not establish clean
installation; the directive retains separate built-distribution proof.
Final board/dashboard checks pass; documentation lifecycle and links pass for
358 Markdown files after UV_NO_SYNC=true also disabled the nested board-command
sync. The failed nested rebuild attempt is retained. Manifest/task/criterion,
16 source-hash, whitespace and accepted-input preservation checks also pass.
Exact results are recorded in readiness evidence.

The freeze checker verifies unchanged VAL-013 request, 34 authority inputs,
five reports, 19 historical artifacts and 978 tracked product files. Five unrelated
paths retain their byte fingerprints: `.DS_Store`, absent `family-tree.md`,
`docker-bench-security/`, Chat's pre-typed-LLM config backup and sandbox
`docker/Dockerfile.audit`. No cache/runtime-state cleanup or broad staging.

Next: explicit bounded approval of the reconciled WS-06 directive.
[AGENTS.md](../../../../../AGENTS.md) requires an "approved construction directive"
before product edits. This checkpoint supplies that concrete decision, not approval.
After implementation, fresh read-only complete-aggregate VAL-014 and separate
maintainer acceptance remain required. WS-07/08 and delivery stay separate gates.
