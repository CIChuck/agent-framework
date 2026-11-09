# MEMQ-001 — memory query commands contract

Status: **approved with the bounded [directive-correction amendment](approval/memory-queries-directive-correction.md)**; fresh directive-readiness council pending.
Prepared 2026-11-09 on `feature/command-retirement` at
`c5871054266da2340486d2043062c5fb95611c00` (accepted DIAG-001 closeout).
Read this document, then [CD-CMD-MEMQ-001](directives/CD-CMD-MEMQ-001-memory-queries.md).
Chuck Russell's “the uat was successful - all approved, proceed to next steps”
and later “ok proceed” authorize preparation only. His subsequent “I approve
your recommendation. Where is the directive document for me to look at?”
selects MQ-D3 option R. His later “The edited version” approves the clarified
record projection/schema and completion of its evidence and hash references.
The original approval binds its historical bytes. Chuck Russell subsequently
instructed “lets apply the corrections and iterate”, authorizing the four
bounded readiness corrections and fresh council recorded in the amendment.
The amendment binds the corrected bytes; Option R does not need to be chosen again.
Product D0/D1 waits for the corrected directive-readiness result.

## Scope, authority and evidence

Migrate only `/memory` (PAR-024), `/insights` (PAR-021), `/summaries` (PAR-043),
`/meta` (PAR-025), `/entities` (PAR-012) and `/list-ingested` (PAR-023), the
proposed MEMQ-001 unit after DIAG-001. Preserve 41 canonical names, three
aliases, all six metadata records, help bytes and existing admission, parser and
dispatch behavior. Accepted foundation, retirement, pilot, SESSION and
[DIAG](approval/diagnostics-acceptance.md) work stays closed. The historical
proposed unit map is ordering input, not approval of this or another unit.

[Preparation evidence](validation/memory-queries/preparation.json) binds the
clean Git source, capture/comparison programs, six metadata records and 76
synthetic cases. Two independent captures from separate clean exports agree
exactly, including access/await events, exception identity, result defaults,
dispatch and custom handlers. Related Chat tests: 587 passed; Commands/cohort:
498 passed. These are current-source preparation receipts, not MEMQ
implementation, candidate-wheel or independent conformance evidence.

The unit is read-only. Each command awaits existing public memory/transcript
reads or reads in-process state; none writes stores, files or transcripts, runs
synthesis, reorganization, providers or telemetry, or changes session state.
The memory, graph, transcript and lifecycle services remain their owners.
Governing direction: S-03/O-05 preserve retained behavior and quirks by
default and require separate decisions for discovered defects; S-04 and
CMD-F05/CMD-F10 defer enhancements and C-01 consolidation. PAR-023 records the
maintainer's note that `/list-ingested` “must be wired into the application”;
MQ-D3 below records that bounded decision explicitly.

## MQ-01 — explicit closed-schema amendment

Approval explicitly adds six payload types, `MemoryUnavailableData`,
`MemoryStatisticsData`, `MemoryRecordsData`, `MemoryQueryFailedData`,
`GraphData` and `IngestedDocumentsData`, to `FoundationData` and the exact-type
`CommandOutcome.data` whitelist. The seven other models below are nested
values, not outcome alternatives. Preserve every original model, union member,
error code, effect and constructor invariant, including the DIAG additions.

All models are frozen/slotted dataclasses in `friday_commands.contracts`.
Fields and defaults are exactly:

```python
MemoryRecordKindName = Literal["insight", "summary", "meta_insight"]

class MemoryWarningData:
    component: str
    reason: str

class MemoryMetricData:
    key: str
    state: Literal["available", "unavailable", "not_configured"]
    value: str | None = None
    reason: str | None = None

class MemorySectionData:
    title: str
    metrics: tuple[MemoryMetricData, ...] = ()

class MemoryStatisticsData:
    sections: tuple[MemorySectionData, ...] = ()
    warnings: tuple[MemoryWarningData, ...] = ()

class MemoryRecordData:
    record_id: str | None
    text: str
    collection: str | None
    lifecycle_stage: str | None = None
    created_at: str | None = None
    confidence: str | None = None
    source_count: str | None = None
    provenance_source_type: str | None = None
    source_memory_ids: tuple[str, ...] = ()
    provenance_truncated: bool = False
    verification: str | None = None

class MemoryRecordsData:
    kind: MemoryRecordKindName
    records: tuple[MemoryRecordData, ...] = ()
    warnings: tuple[MemoryWarningData, ...] = ()
    complete: bool = True

class MemoryQueryFailedData:
    kind: MemoryRecordKindName

class MemoryUnavailableData:
    reason: Literal["runtime_missing"]

class GraphEntityData:
    label: str
    node_type: str
    hit_count: str

class GraphRelationshipData:
    source: str
    relation: str
    target: str
    hit_count: str

class GraphData:
    entities: tuple[GraphEntityData, ...] = ()
    relationships: tuple[GraphRelationshipData, ...] = ()

class IngestedDocumentData:
    source_path: str
    chunk_count: str
    description: str

class IngestedDocumentsData:
    documents: tuple[IngestedDocumentData, ...] = ()
    warnings: tuple[MemoryWarningData, ...] = ()
```

Validate in declaration order using the existing string, optional-string,
exact-model, bool and one-pass collection rules. String subclasses are accepted
without conversion. Collections reject scalar, str/bytes/bytearray/mapping
containers and wrong/subclass members; finite iterables are snapshotted once,
preserving order and duplicates. `MemoryMetricData` with `available` requires a
string value and no reason; the other two states require a string reason and no
value. `records`, `entities` and `relationships` each hold at most 100 members;
`documents` is unbounded as today. An unknown literal is `ValueError`, a wrong
type is `TypeError`. Empty strings, Unicode, newlines and control characters are
valid data; normalization belongs to the documented projection/rendering below.

`MemoryRecordsData.complete` is an exact bool snapshot, not a value recomputed
from normalized warnings. A meta record requires non-None `record_id` and
`collection`; plain kinds carry None for optional metadata and retain the empty
tuple/False defaults for their other unused fields.
Plain-record text and meta text/id are already previewed display facts, as
specified in MQ-04; the renderer must not preview or format raw values again.

These values are individually formatted display facts, matching the DIAG
precedent, not whole Chat messages: numbers, booleans, dates and confidences are
projected once with their existing formatting. Raw runtime objects, store
records, dictionaries, enums, datetimes, exceptions and callbacks never cross the
neutral boundary. A TUI renders the fields directly; it must not parse Chat text
or rerun services.

Add exactly sixteen exports, **appended in this order after all 38 existing
exports**, preserving their order and bindings:

```text
MemoryWarningData, MemoryMetricData, MemorySectionData, MemoryStatisticsData,
MemoryRecordData, MemoryRecordsData, MemoryQueryFailedData,
MemoryUnavailableData, GraphEntityData, GraphRelationshipData, GraphData,
IngestedDocumentData, IngestedDocumentsData, MEMORY_QUERY_SPECS,
MemoryQueryPort, build_memory_query_handlers
```

`MemoryRecordKindName` is a module-level alias in `contracts`, not an export.
Two accepted tests pin the exact 38-name surface: the literal list in
`test_session_views.py::test_session_specs_and_factory_are_immutable` and, in
`test_diagnostics.py::test_diagnostic_specs_exports_and_factory`, the literal
list, owner table and binding count. **Decision MQ-D4:** in that diagnostic
test only, permit exactly one local
`import friday_commands.memory_queries as memory_queries_module`, append the
sixteen names to the API literal, append the thirteen model names in MQ-01 order
to the existing `contracts` owner tuple, append one final
`(memory_queries_module, ("MEMORY_QUERY_SPECS", "MemoryQueryPort",
"build_memory_query_handlers"))` row after `shared`, and change the binding
count from `38` to `54`. In the SESSION test only, append the sixteen API
names to its literal. Every other statement, owner and assertion is unchanged.
The AST audit reverses exactly these edits and must recover the baseline; no
model re-export workaround changes the declared ownership.
The accepted DIAG and SESSION installed probes stay frozen; their 38/24-name
assertions are intentionally obsolete for this approved expansion. Do not weaken
any assertion to a subset.

`MEMORY_QUERY_SPECS` is an immutable tuple in order memory, insights, summaries,
meta, entities, list-ingested, field-for-field equal to the preparation metadata
(including `detail` and argument fields). A fresh registry still starts empty.

## MQ-02 — injected capability and neutral ownership

Specs, the structural (not runtime-checkable) protocol and the factory live in
`friday_commands.memory_queries`:

```python
class MemoryQueryPort(Protocol):
    def memory_available(self) -> bool: ...
    async def memory_statistics(self) -> MemoryStatisticsData: ...
    async def memory_records(
        self, kind: MemoryRecordKindName
    ) -> MemoryRecordsData | MemoryQueryFailedData: ...
    async def graph_snapshot(
        self, name: str | None, include_relationships: bool
    ) -> GraphData: ...
    async def ingested_documents(self) -> IngestedDocumentsData: ...

def build_memory_query_handlers(
    port: MemoryQueryPort,
) -> Mapping[str, CommandHandler]: ...
```

Return a fresh immutable mapping with exactly the six canonical keys, in spec
order. Construction stores the port without reading or calling it. Each handler
checks exact `CommandRequest`, then exact `CommandExecution`, then canonical
name (`ValueError`), before any port access, then calls `memory_available()`
once and requires exact bool. False returns
`MemoryUnavailableData("runtime_missing")` without another port call, whatever
the args. Otherwise exactly one awaited capability call follows:

| Command | Shared selection | Port call | Result check |
| --- | --- | --- | --- |
| memory | args ignored | `memory_statistics()` | exact `MemoryStatisticsData` |
| insights / summaries / meta | fixed kind `insight` / `summary` / `meta_insight`; args ignored | `memory_records(kind)` | exact `MemoryRecordsData` or `MemoryQueryFailedData`; `kind` equal to the request (MQ-D1) |
| entities | `nodes_only = bool(args) and args[0] == "nodes"`; `name = " ".join(args)` when args and not nodes_only, else `None` | `graph_snapshot(name, not nodes_only)` | exact `GraphData`; nodes-only result has no relationships |
| list-ingested | args ignored | `ingested_documents()` | exact `IngestedDocumentsData` |

Return only that typed data, with zero effects and no error. Empty, unavailable,
partial and query-failed results remain successful data, not foundation
errors. Port exceptions and cancellation propagate unchanged, without retry,
logging, rollback, progress, added admission or conversion to success. The
shared owner selects kinds and graph mode, joins args and enforces result
types; the host owns service reads, the existing failure-to-data conversions,
projection and rendering. The neutral package remains standard-library/own-
package only: no Chat/CLI/TUI/display/memory-domain imports, executable,
service locator or global state.

## MQ-03 — `/memory` statistics

`ChatMemoryQueryPort` keeps the supplied context by reference and reads nothing
at construction. `memory_available()` performs the single original
`context.runtime is None` read. `memory_statistics()` moves the old handler body
after that test, unchanged in order: second runtime read, awaited
`query_memory_statistics()` with `except Exception` → the existing all-unavailable
store and episodic warning; awaited transcript `query_entries(session id)` count
with `except Exception` → unavailable and transcript warning; last budget,
session/turn-id, history and variable reads. `CancelledError` and other
`BaseException`s propagate, as now. The Chat-owned `MemoryStatisticsSnapshot` is
then projected, in the existing order, into eight sections and 24 metrics:

`Session` (session_id, in_process_turns, tracked_turn_ids, scoped_variables);
`Episodic` (episodic_current_session_turns); `Vector` (short_term, long_term,
decayed, active_total, total); `Graph` (nodes, relationships); `Transcript`
(current_session_entries); `Lifecycle` (enabled, access_buffer_entries,
access_buffer_accesses); `Priming` (enabled, previous_sessions); `Last context`
(total_tokens, message_tokens, tool_schema_tokens, available_budget,
utilization, severity).

Available values use `_metric_text`'s existing formatting exactly once: bool →
`true`/`false`; float → `.1f` plus `%` for utilization only; str →
`preview_text(..., limit=256)`; otherwise `format(value, "")`. Missing states
carry the enum reason value. Warnings are the existing unique pairs sorted by
`(component.value, reason.value)`. Do not add metrics, recount stores, call a
provider or read last-turn/tool-budget snapshots beyond the current fields.

## MQ-04 — `/insights`, `/summaries` and `/meta`

`memory_records(kind)` performs the original second runtime read and awaits
`runtime.memory.query_memory_records(MemoryRecordKind(kind))` exactly once. An
`Exception` returns `MemoryQueryFailedData(kind)`; cancellation and other
`BaseException`s propagate. Otherwise preserve the old result truth tests and
lazy branches before projecting `result.kind`, at most the first 100 visible
records in order, and unique sorted warnings. MQ-01 declares field layout,
not permission to inspect metadata the old command did not use.

- For insight and summary records, read only `record.text`, apply the unchanged
  `preview_text(..., limit=160)` at that point, and copy the result to a plain
  built-in string. Set optional metadata to None and other unused fields to
  their defaults. Do not read or format them. Complete each record's old
  evaluation before touching the next record.
- For meta records, preserve `_meta_record_lines`' exact reads, truth tests,
  repeated accesses and formatting order. Join/check source ids and truncation,
  then evaluate verification status and optional `.3f` confidence using the
  existing concatenation semantics, before previewing text. Next preview text
  (160) and id (80), then project collection, stage, created-at ISO text,
  confidence, source count and provenance in their original order. Preserve
  None-versus-falsy selection before formatting; copy formatted facts to plain
  strings without invoking a formatter twice. `verification` contains the
  already evaluated status/confidence value, without the English field label,
  so the renderer never repeats a custom concatenation. Snapshot source ids
  once at their old join point; enforce that join's failures there, not later.
- Read `result.complete` only in the empty-meta branch where the old helper
  reads it, preserving its truth value as `bool(result.complete)`. Elsewhere use
  the unused default True without that read. Project warnings at their old
  point with the existing truth guard before dedupe/sort. Do not infer
  completion from projected warnings: an incomplete empty meta result without
  warning members still has the existing incomplete message.

An absent displayed metadata value remains None and the renderer emits the
existing fallback. A present value whose formatter produces an empty string
stays present; do not replace it by a truthiness fallback. Renderers consume
only prepared display facts, with no further raw-record reads, previews or
original-object formatting. Stateful float/datetime/string subclasses retain
their old failure and evaluation order. The previews are display facts, not
full identifiers for a new selection/action API.

[Additional planning characterization](validation/memory-queries/record-projection-characterization.json)
records four actual legacy cases covering unused metadata, meta evaluation
order and empty incomplete meta results. These supplement, without changing,
the original 76 frozen observations.

**Decision MQ-D1 (declared refusal).** The old renderer chose meta formatting
from the *returned* kind but the title from the *requested* command, so a
service returning another kind produced mixed output (two preparation rows).
Both existing implementations, `FrameworkMemoryAdapter` and
`FakeMemoryController`, always return the requested kind. The shared handler
now raises `ValueError` for a mismatched kind before any output. Pre-refusal
events are unchanged. The other 74 rows must match exactly (or 68 + six
superseded rows under MQ-D3 option R).

## MQ-05 — `/entities`

`graph_snapshot(name, include_relationships)` performs the original runtime
reads, awaits `list_entities(name)`, then `list_relationships(name)` only when
`include_relationships`. Only after both awaits does it project the first 100 of
each, in order, with the existing public `record_value` helper: entity
`label` (label, id), `node_type` (type), `hit_count`; relationship `source`
(source_label, source_id), `relation` (relation, type), `target` (target_label,
target_id), `hit_count`. Empty string means absent, exactly as now (`0` and
`False` are shown). Non-mapping records keep their existing `AttributeError`
after both reads. Preserved quirks: `nodes` only as the exact first argument
(`/entities nodes x` is nodes-only, `NODES` is a name); names joined by one
space without quote processing. The renderer reproduces `No entities found.`,
the `Entities:`/`Relationships:` blocks, the blank separator line and the
`(type)`/`, hits=N` suffix rules.

## MQ-06 — `/list-ingested` disposition (decision MQ-D3)

**Characterized current behavior.** The handler reads
`getattr(runtime.memory, "ingested_documents", [])`. Only the in-process
`FakeMemoryController` defines that list. The production `FrameworkMemoryAdapter`
does not, so with the real runtime the command always reports
`No ingested documents.`, even after `/ingest` stored chunks. This is a known
defect (PAR-023, C-01, backlog CMD-F05), not intended production behavior.
`/ingest` stores each chunk in the persistent `memories_short_term` collection
with metadata `type="ingested_file"`, `source`, `description`, plus
`chunk_index`/`chunk_count` when there are several chunks. The chunks are
protected, never decay and may be promoted to `memories_long_term`. No
ingestion-event id or content hash is stored.

The maintainer selected option R. Option P remains the documented alternative,
not the current selection. The subsequent approval records the final revised
documents.

**Option R — bounded listing repair in MEMQ (selected).** Wire the listing
to persisted metadata while still deferring validation and consolidation.
Allowed changes are limited to `friday-chat`. No `friday-memory` or other
framework package changes, and no change to `/ingest`, its metadata or storage.

- `friday_chat.memory_views` adds Chat-owned `IngestedDocumentView(source_path:
  str, description: str | None, chunk_count: int)` and
  `IngestedDocumentQueryResult(documents, warnings)`.
- The Chat `MemoryController` protocol adds
  `async def query_ingested_documents(self) -> IngestedDocumentQueryResult`.
- `FrameworkMemoryAdapter` implements it with the same existing public reads it
  already uses for records:
  `collection_manager.short_term.get_all(limit=None, where={"type":
  "ingested_file"})` and the matching `long_term` call, gathered with
  `return_exceptions=True`. Cancellation and non-`Exception`s are re-raised; a
  failed collection adds that collection's existing warning. A non-mapping record
  or one whose metadata lacks a non-empty string `source` adds the
  `memory record` warning. The decayed collection is not read.
- Selected defaults (a subsequent approval may change them): one row per `(source,
  description)`; `chunk_count` = number of stored chunk records in that group,
  so a re-ingested file shows its total stored chunks; rows sorted by source,
  then description with None first.
- `FakeMemoryController` implements it from its existing `ingested_documents`
  list, in insertion order with its recorded counts, so existing fake tests keep
  their meaning.
- The Chat port awaits `query_ingested_documents()` once, formats `chunk_count`
  and `description or ""`, and projects unique sorted warnings. The renderer
  keeps `No ingested documents.` and `Ingested documents:` with
  `- PATH (N chunks): DESCRIPTION`, adding the existing `Warnings:` block only
  for partial reads.
- Preparation rows that use a synthetic `ingested_documents` attribute (six
  rows) are superseded and replaced by repair tests. `runtime-missing` and
  dispatch rows stay exact.

**Option P — preserve and defer.** Migrate the exact current behavior, including
the getattr fallback, in the Chat port. All 74 non-MQ-D1 rows must match. The
defect stays open under CMD-F05 and becomes the first follow-up after MEMQ.

**Unresolved and excluded under both options.** These stay with CMD-F05 and the
maintainer:

- what “ingested sources must also be validated” means (existence, readability,
  path policy, content hash or staleness checks);
- per-ingestion identity or deduplication, which needs `/ingest` metadata
  changes owned by FILE-001;
- any filesystem access from the listing;
- the C-01 `/memory ingested` view and other consolidation or renaming (CMD-F10).

## MQ-07 — Chat integration and presentation

Add `friday_chat.commands.memory_queries` with the narrow typed port, metadata
helper, projections, pure renderers, exact outcome adapter and once-only
`invoke_memory_query(fixed_canonical_name, args, supplied_context)`. Its
metadata helper projects the shared specs. Replace only the six registry tuple
entries at indices 3, 9, 10, 11, 12 and 16 (verified against baseline) with
those projections, keeping tuple order/length 39, the handler map, aliases and
builder behavior. The four `friday_chat.commands.memory` handlers and the two
registry handlers keep their names as compatibility wrappers, each calling
`invoke_memory_query` exactly once. Use fixed shared spec identity, the original
parsed tuple in `CommandRequest`, a fresh port/factory, one awaited handler, and
consume its outcome. No second parse or registry, no `context.registry` lookup,
no metadata/context reads before the shared request validates. Custom handlers
stay authoritative; renamed wrappers still use their fixed canonical command.
Public `preview_text` and `record_value` stay in `friday_chat.commands.memory`,
unchanged, for their existing importers.

The adapter accepts exactly the six new data variants with no error or effects.
All other outcomes, subclasses, errors and effect shapes raise `ValueError` and
never fall through to legacy work. Renderers are pure: no service, file or
command calls. Preserve exact current punctuation, ordering, newlines, warning
blocks, the decayed-policy line, both meta empty messages, `Unable to query
TITLE: store read failed.`, `Memory runtime is not initialized.` and the
`CommandResult` defaults (handled True, exit_requested False, no effects). No
extra trailing newline. No help/metadata improvements, new flags, progress UI,
pagination, consolidation or TUI work.

## Decision summary for approval

| ID | Decision | Default in this proposal |
| --- | --- | --- |
| MQ-D1 | Refuse a service result whose record kind differs from the request (`ValueError`). | Required; two rows become declared refusals. |
| MQ-D2 | Keep the existing shared-request rule: direct non-string argument members raise `TypeError` before reads, including commands that ignored args; string subclasses accepted. | Required; the parser cannot produce such members. |
| MQ-D3 | `/list-ingested`: Option R (bounded Chat-only repair); Option P remains an alternative. | Option R selected and the revised contract/directive approved by the maintainer. |
| MQ-D4 | Extend the two accepted export-surface assertions from 38 to 54 names. | Required for the additive API. |

Stop for any other incompatible legacy value and request a contract decision.
Do not silently stringify, repair or broaden these exceptions.

## Acceptance boundary

The [directive](directives/CD-CMD-MEMQ-001-memory-queries.md) binds D1 neutral,
D2 Chat (including Option R if approved) and D3 installed proof, with a fresh
Sol/Astra/Claude council after each. Only these six PAR rows may gain current
evidence. Shared schemas, ownership, await/read order, compatibility, the MQ-D3
outcome and installed proof must all pass; text parity alone is insufficient.
Final VERIFIED stops for bounded maintainer MEMQ acceptance and optional UAT.
It grants no consolidation, validation design, full-refactor, P0/P1, later
family, TUI or external delivery authority. Planning preparation is complete
only when the current packet, board, authority and log agree and every
protected product/dirty hash matches.
