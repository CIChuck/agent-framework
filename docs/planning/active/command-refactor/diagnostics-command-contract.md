# DIAG-001 — context diagnostics contract

Status: **proposed; design and construction approval not granted**.
Prepared 2026-11-08 on `feature/command-retirement` at
`9dbcec54773f10274eea058e5d59edb0ce53b6cc` (accepted SESSION-001 closeout).
Read this document, then [CD-CMD-DIAG-001](directives/CD-CMD-DIAG-001-context-diagnostics.md).
Chuck Russell's “proceed” authorizes preparation only. Approval of both exact
proposed documents is required before product implementation.

## Scope, authority and evidence

Migrate only `/context` (PAR-007), `/debug` (PAR-008), `/debug-budget`
(PAR-009), `/debug-retrieval` (PAR-010), `/prompt` (PAR-028) and `/timing`
(PAR-045). Preserve 41 canonical names, three aliases, all six metadata records,
help bytes and existing admission/parser/dispatch behavior. The accepted
[SESSION](approval/session-acceptance.md), [pilot](approval/pilot-acceptance.md),
foundation and retirements remain closed. The historical proposed unit map is
ordering input, not approval of this or another unit.

[Preparation evidence](validation/diagnostics/preparation.json) binds the clean
Git source, capture/comparison programs, six metadata records and 72 synthetic
cases. Two captures agree, including access events, exceptions, file contents,
result defaults and custom dispatch. Related Chat tests: 244 passed;
Commands/cohort: 278 passed. These are current-source preparation receipts,
not DIAG implementation, candidate-wheel or independent conformance evidence.

The unit has read/await **and file-write** effects: `/context --file` and
`/prompt --file` overwrite fixed exports. Retrieval calls the existing public
memory method once; it is not a second retrieval implementation, and this
contract makes no claim that the service has no internal bookkeeping effects.
The memory, runtime, telemetry and transcript services remain their owners.
No persistent-store enumeration, provider use or telemetry emission is added.

## DG-01 — explicit closed-schema amendment

Approval explicitly adds the six payload types `ContextData`, `PromptData`,
`DebugData`, `BudgetData`, `TimingData`, `RetrievalData`, plus
`RetrievalUnavailableData`, to `FoundationData` and the exact-type
`CommandOutcome.data` whitelist. The remaining four models below are nested
values, not outcome alternatives. Preserve every original model, union member,
error code, effect and constructor invariant. Do not rewrite frozen foundation,
pilot or SESSION authority documents or introduce an untyped payload escape.

All models are frozen/slotted dataclasses in `friday_commands.contracts`.
Fields and defaults are exactly:

```python
class DiagnosticField:
    key: str
    value: str

class ContextData:
    text: str
    character_count: int | None = None
    export_path: str | None = None

class PromptData:
    text: str
    export_path: str | None = None

class DebugTurnData:
    turn_ref: str
    outcome: str
    persistence: str
    completed_tools: str
    failed_tools: str

class DebugData:
    recorded: bool
    fields: tuple[DiagnosticField, ...] = ()
    turn: DebugTurnData | None = None

class BudgetData:
    context_window: str | None
    output_buffer: str | None

class TimingCounter:
    kind: str
    outcome: str
    count: str

class TimingTurnData:
    seconds: str
    outcome: str
    persistence: str
    counters: tuple[TimingCounter, ...] = ()

class TimingData:
    recorded: bool
    fields: tuple[DiagnosticField, ...] = ()
    turn: TimingTurnData | None = None

class RetrievalData:
    query: str
    result_count: int
    fields: tuple[DiagnosticField, ...] = ()
    previews: tuple[str, ...] = ()

class RetrievalUnavailableData:
    reason: Literal["runtime_missing", "query_missing"]
```

Validate in declaration order using the existing string, optional-string,
exact-model, bool and one-pass collection rules. String subclasses are accepted
without conversion by neutral models. Integers require `type(value) is int`,
excluding bool; `character_count` and `result_count` must be nonnegative, with
`None` permitted only for `character_count`. Collections reject scalar,
str/bytes/bytearray/mapping containers and wrong/subclass model members;
snapshot finite iterables exactly once, preserving order and duplicates.
`previews` has at most ten members. Do not impose a relationship between count
and preview length: legacy list subclasses can override length independently.
`recorded=False` requires empty fields and no turn; `recorded=True` may have no
fields/turn (for a truthy empty custom mapping). An unknown reason is
`ValueError`, a wrong type is `TypeError`. All other unmentioned strings,
including empty/Unicode/newline strings and formatted NaN/Infinity, are valid.

These values expose individually formatted diagnostic facts, not complete Chat
messages. Numeric timing values are snapshots of their existing `.3f` display
precision; budget/telemetry/custom values retain their existing formatting.
No raw runtime object, dictionary, arbitrary exception, path object or callback
crosses the neutral boundary. A TUI can render these fields directly; it must
not parse Chat text or rerun services to recover results.

Add exactly fourteen exports, **appended in this order after all 24 existing
exports**, preserving their existing order and bindings:

```text
DiagnosticField, ContextData, PromptData, DebugTurnData, DebugData, BudgetData,
TimingCounter, TimingTurnData, TimingData, RetrievalData,
RetrievalUnavailableData, DIAGNOSTIC_SPECS, DiagnosticsPort,
build_diagnostic_handlers
```

The accepted SESSION test and installed probe pin the earlier exact 24-name
surface. Approval expressly permits extending only that test's literal export
assertion by the fourteen names above, keeping every other statement unchanged.
The old installed probe stays frozen; the new DIAG aggregate probe must retain
its SESSION checks with only that literal expectation extended to 38 (AST-audited),
as specified in the directive. Do not weaken either assertion to a subset.

`DIAGNOSTIC_SPECS` is an immutable tuple in order context, prompt, debug,
debug-budget, timing, debug-retrieval, field-for-field equal to preparation
metadata, including argument metadata. No defaults, aliases, descriptions or
registration validation change. A fresh registry still starts empty.

## DG-02 — injected capability and neutral ownership

Specs, the structural (not runtime-checkable) protocol and the factory live in
`friday_commands.diagnostics`. The public signatures are:

```python
class DiagnosticsPort(Protocol):
    def context_text(self) -> str: ...
    def prompt_text(self) -> str: ...
    def export_context(self, data: ContextData) -> str: ...
    def export_prompt(self, data: PromptData) -> str: ...
    def debug_snapshot(self) -> DebugData: ...
    def budget_snapshot(self) -> BudgetData: ...
    def timing_snapshot(self) -> TimingData: ...
    def retrieval_available(self) -> bool: ...
    async def retrieve(self, query: str) -> RetrievalData: ...

def build_diagnostic_handlers(
    port: DiagnosticsPort,
) -> Mapping[str, CommandHandler]: ...
```

Return a fresh immutable mapping with exactly the six canonical keys, in spec
order. Construction stores the port without reading any attribute or calling
it. Each handler checks exact `CommandRequest`, then exact `CommandExecution`,
then canonical name (`ValueError` on mismatch), before any port access. A custom
same-name spec is permitted and otherwise ignored. Execution fields are unused.
Each snapshot must be its exact declared type; invalid port data raises rather
than being repaired. Return only the matching typed data, zero effects and no
error. Existing empty/unavailable messages remain successful data, not new
foundation errors. Exceptions/cancellation propagate unchanged, without retry,
logging, rollback, progress, added admission or conversion to success.

The shared owner selects flags, orders capability calls, requests exports,
joins retrieval args and decides runtime/usage precedence. The host projects
its dynamic values and renders them; it does not select a second command,
parse input again or return an independently computed legacy `CommandResult`.
Projection sorting/formatting below stays at the host boundary to preserve
legacy comparisons, formatter behavior and lazy failure order. The neutral
package remains dependency-free, standard-library/own-package only, with no
Chat/CLI/TUI/display/domain imports, executable, service locator or global state.

## DG-03 — context, prompt and exports

Context calls `context_text()` once. Construct `ContextData(text=...)`; if the
exact string `"--debug"` occurs anywhere in args, set `character_count=len(text)`.
Repeated flags have one effect; unknown args and case variants are ignored.
If `"--file"` occurs, call `export_context(base_data)` synchronously exactly once
**after** character count is computed. The data passed has `export_path=None`.
Require a string return, then return new `ContextData` with that path. No return
before export completes. Export failures leave any actual partial file/service
state as-is; there is no rollback or success footer on failure.

Prompt is analogous using `prompt_text` and `export_prompt`, with no character
count and no interpretation of `--debug`. Neither operation accesses the other
capability or retrieval/budget/telemetry. The export seam deliberately receives
typed data: the Chat port uses the same pure renderer as the outcome adapter to
write exactly the displayed body, excluding the export footer. Shared code owns
the export request, the host owns its fixed destination and text encoding. A
future frontend may render differently; it must preserve the semantic payload
and file effect without routing through Chat output.

`ChatDiagnosticsPort` keeps the supplied context by reference and does no reads
at construction. `context_text` preserves `last_context or _build_context_text`:
truthy cached strings win; otherwise use the old runtime/tool-context reads,
`Context payload:`/`No tool context injected.` sections and history length.
`prompt_text` likewise preserves `last_prompt or _build_prompt_text`: runtime
system prompt or `You are Friday.`, followed by only the last history pair if
history is truthy. Preserve truth tests, repeated property reads, lazy fallback,
unpacking and formatting failures; do not snapshot/eagerly read unused state.
Move the three legacy registry helpers into the new Chat module with their
bodies unchanged. Its imports retain the existing public helper owners.

Export uses the existing transcript `export_directory` function and original
`mkdir`/`write_text(..., encoding="utf-8")` procedure: resolved configured root
or `./exports`, fixed `friday_context.txt` or `friday_prompt.txt`, overwrite on
repeat, no user-controlled filename, no extra newline, no atomic-write/retry or
path policy redesign. Preserve both directory-creation calls. Test actual I/O
only under fresh scratch by setting configuration; test fallback resolution in
a scratch cwd, never the repository/user exports directory.

### Proposed declared-type decision requiring approval

Falsy cached values (including None, 0 and []) continue to use the old fallback.
A **truthy non-string** selected `last_context` or `last_prompt` now raises
`TypeError` at the typed boundary before export or success. Do not coerce it.
The old code could return a non-string `CommandResult.output`; this is a
characterized, deliberate exception to exact compatibility, not a claim of
parity. Four preparation rows cover truthy int/list cache values. All 68 other
rows must match exactly; those four may match the old result or the precise
approved refusal until the corresponding command is migrated. By final D2 all
four must refuse, with unchanged pre-refusal reads and no file effects.

Approval also retains the existing shared-request rule: direct non-string
argument members raise `TypeError` before context reads, including commands
whose legacy handler ignored args. The parser cannot produce those members.
String subclasses remain accepted; no stricter model/registration policy is
added elsewhere. Stop for any other incompatible legacy value and request a
contract decision; do not silently stringify text or broaden these exceptions.

## DG-04 — debug, budget and timing snapshots

The Chat port reproduces the original handler's projection in the exact order,
returning typed facts instead of whole English messages:

- Debug/timing first perform the original conditional runtime/telemetry reads
  and at most one `execution_snapshot()` call. No telemetry means None.
  Preserve the original `not last_* and not (execution and execution.turns)`
  test. The false branch returns `recorded=False` without sorting/formatting.
- Debug fields: `sorted(context.last_debug.items())`, in that order, each key
  and value formatted once by its old empty format spec to a plain built-in
  string. When the original execution/turns test succeeds, select only `[-1]`
  and project the five `DebugTurnData` fields in declaration order, preserving
  their individual formatting. No counters or timing properties are read.
- Budget: `runtime.config.memory` only when runtime is not None; read context
  window then output buffer only when memory is not None. Preserve the original
  reads of both before formatting either. Project each value as None when its
  old `value or 'unknown'` expression selects unknown; otherwise format once
  into a plain string. Zero/False/empty remain unknown, negative and truthy
  non-string values retain their displayed meaning. Do not read the app's
  last-budget snapshots, recalculate tokens or call a provider.
- Timing fields: sort `last_timing.items()` before formatting each value with
  `.3f`, storing the number text without `s`. With a last turn, divide its
  `duration_ms` by 1000 and format `.3f`; project outcome/persistence, then the
  original `execution.counters` order, each triple's fields once. No histograms
  or earlier turns are inspected. The host renderer adds units and labels.

String projection must remove a custom formatter's str-subclass wrapper without
formatting it again, as in accepted SESSION projection. Retain original
comparison/truth/format/iteration errors and exception identity. Mixed keys do
not become sortable by stringifying before sorting. Do not eagerly project an
unused debug/timing branch. A port method is called once per invocation; it
returns a detached snapshot unaffected by later host mutation.

## DG-05 — retrieval precedence, awaited service and projection

Call `retrieval_available()` once synchronously; require exact bool. The Chat
port implements only `context.runtime is not None`, preserving its first read.
False returns `RetrievalUnavailableData("runtime_missing")` even with no args.
With a runtime but no args return `RetrievalUnavailableData("query_missing")`
without reading memory. Otherwise join the original argument tuple with one
space, without quote processing or trimming; await `retrieve(query)` once.
Require exact `RetrievalData` and matching query, else `TypeError`/`ValueError`.
A pending await returns no success; exception/cancellation identity is retained.

`retrieve` performs the original second runtime read, then public
`runtime.memory.debug_retrieval(query)` exactly once. Preserve the service's
own semantics; no alternative retrieval/requery or new store API. After await:
read `diagnostics.get('snippets', [])`, then `.get('debug_info', {})`; count is
`len(snippets)` only for `isinstance(snippets, list)`, otherwise zero. Only a
`dict`/subclass debug_info is traversed, keys sorted before indexing/formatting.
Only nonempty list/subclass snippets produce previews, from the first ten,
in order, using `preview_text(str(snippet))` exactly once per selected item.
Keep original truth tests, count/format ordering, limit 160, whitespace/control
normalization and ellipsis. Unsupported containers are ignored exactly as now;
bad response/get/sort/format/iteration errors propagate without invented repair.
No raw diagnostics mapping crosses the port; no new `Any`/casts/suppressions.

## DG-06 — Chat integration and presentation

Add `friday_chat.commands.diagnostics`. Its metadata helper projects the shared
specs, including all argument fields; replace only the six corresponding tuple
entries (indices 4,5,6,7,8,15, verified against baseline) with those projections.
Keep tuple order/length 39, the handler map, aliases and builder behavior.
The six old handler names remain compatibility wrappers calling
`invoke_diagnostic(fixed_canonical_name, args, supplied_context)` exactly once.
Use fixed shared spec identity, the original parsed tuple in `CommandRequest`,
a fresh port/factory, one awaited handler, and consume its outcome. Do not
reconstruct text input, call a second registry or choose `context.registry`.
Custom handlers stay authoritative; renamed wrappers still use their fixed
canonical command and supplied context. No metadata/context reads before the
shared request validates. Keep parser/register/dispatch/admission/app code.

The adapter accepts exactly the seven new data variants with no error/effects;
all other outcomes/subclasses/error/effect shapes raise `ValueError`, never
fall through to legacy work. Pure renderers must not call services or execute
commands. Preserve the exact baseline punctuation, ordering, newlines and
CommandResult defaults (handled True, exit_requested False, effects empty):

- Context: text; optional `\n\nDebug:\n- characters: N`; optional
  `\n\nExported context to PATH`. Export bytes include the debug block.
- Prompt: text; optional `\n\nExported prompt to PATH`.
- Debug: `No debug information recorded.` or `Debug information:` followed by
  sorted field bullets, then turn/outcome/persistence/completed_tools/failed_tools.
- Budget: `Token budget:\n- context_window: VALUE\n- output_buffer: VALUE`,
  None rendered as `unknown`.
- Timing: `No timing data recorded.` or `Timing:` followed by field bullets
  `- KEY: VALUEs`; last turn `- observed_turn: SECONDSs (OUTCOME, persistence=P)`
  then `- KIND/OUTCOME: COUNT` counters.
- Retrieval: exact current runtime/usage messages or `Retrieval diagnostics:`,
  query and result_count bullets, sorted debug fields, optional `Results:`
  and preview bullets. No extra trailing newline.

The Chat file footer uses the actual path returned by its export. The fixture
normalizes only its unique private absolute root to `$EXPORT`; bytes written
and path relation remain independently asserted. Retain the existing public
runtime/domain contracts and configured defaults. No help/metadata improvements,
sanitization policy, new flags, progress UI, tool injection or TUI work here.

## Acceptance boundary

The [directive](directives/CD-CMD-DIAG-001-context-diagnostics.md) binds D1 neutral,
D2 Chat and D3 installed proof, with a fresh Sol/Astra/Claude council after each.
Only these six PAR rows may gain current evidence. Shared schemas, ownership,
flag/await/export effects, compatibility and installed proof must all pass;
text parity alone is insufficient. Final VERIFIED stops for bounded maintainer
DIAG acceptance. It grants no full-refactor, P0/P1, later family, TUI or external
delivery authority. Planning preparation is complete only when current packet,
board, authority and log agree and every protected product/dirty hash matches.
