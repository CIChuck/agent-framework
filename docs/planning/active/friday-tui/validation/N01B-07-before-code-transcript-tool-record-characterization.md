# TUI-N01B-07 before-code transcript tool-record characterization

**Status:** Read-only planning evidence on 2026-10-19. N01B-07 has no
product-code authority. N01B-06 product source is frozen at `e16aede6`;
its one authorized push reached `aa8ae784`, and [Ubuntu run
39284711876](https://github.com/CIChuck/agent-framework/actions/runs/39284711876)
was [independently VERIFIED](VAL-N01B-06-postrun-3413c25f.md). Local
post-push commits change only planning/status/evidence files; no product,
test, workflow or dependency file changed after the pushed source.

## Existing behavior and extraction boundary

`FrameworkTranscriptAdapter.record_interaction` in
`packages/friday-chat/src/friday_chat/adapters.py` owns several distinct
steps. It first validates each MCP tool call's safe provenance **before**
creating a session or writing an entry. It rejects nonempty MCP arguments,
identity mismatches, unchecked output, a result-byte-size mismatch or limit
overage, and unrelated transcript correlation. Valid MCP provenance is copied
with the turn ID as its transcript correlation; native calls retain their
ordinary argument values. A rejected preflight leaves the store untouched.

Only after that preflight does Chat ensure the session, choose the next
turn number and construct `friday_transcript.ToolCall` and `ToolResult`
records. Caller-supplied call IDs are retained; missing IDs use
`turn_id:index:name`. Each result keeps its text and uses the correlated
provenance failure code as its error when present. Chat then constructs the
entry with user/assistant messages, model/temperature, timestamp, latency,
raw-prompt flag and memory-snippet metadata; appends it; optionally stores
a pending raw context log; and advances its cached turn number. Separate
`record_mcp_interaction` and readback methods enforce receipt consistency
for memory ingestion. `record_turn` remains a compatibility no-op.

The proposed next unit extracts only the two pure tool-record stages into
UI-neutral Runtime: preflight validation/correlation before any Chat store
effect, then tool-call/result construction after Chat has ensured the
session and chosen the turn number. Chat retains the method, conversion
to `TranscriptEntry`, all store effects, context-log handling, receipt
readback, public types, error propagation and method/monkeypatch seams.
The TUI will not call these functions yet. A later unit must handle neutral
entry persistence and close semantics before the TUI can own transcript
writes end to end.

Runtime already depends on `friday-framework-core` and
`friday-framework-transcript`, so the needed provenance and record types
have a neutral dependency path. It must not import `friday-chat`,
`friday-cli`, their turn models, or their configuration. A structural
typed call input can accept Chat's current `ToolCallRecord` and future
TUI-owned calls without a frontend import.

## Unchanged baseline and next checks

The read-only focused baseline passed 63 transcript, MCP execution,
query-delegation and identity tests; 85 MCP-memory and turn-telemetry tests
also passed. The unchanged full `friday-cli` package passed 155 tests.
These are separate runs totaling 303 passing tests; they do not constitute
N01B-07 implementation, installed-wheel proof, Ubuntu verification or UAT.

A later approved directive should add direct neutral tests for native and
MCP calls, provided and generated IDs, Unicode result byte sizes, exact
failure/error fields, correlation, invalid-preflight no-write behavior and
ordering. Chat delegation tests must compare persisted entries and receipt
behavior through a disposable store, including context-log and append
failures. Protected existing Chat and `friday-cli` tests stay unchanged.

**Stop point:** [CD-TUI-N01B-07](../directives/CD-TUI-N01B-07-neutral-transcript-tool-records.md)
is a proposal only. N01B-06's exact-source Ubuntu gate is independently
VERIFIED; separate exact directive approval is the current board gate.
No N01B-07 source,
test, metadata, lock, workflow, push, PR, merge or release change is
authorized by this characterization.
