# SESSION-001 — history and conversation clearing contract

Status: **proposed; design and construction approval not granted**.
Prepared 2026-11-08 on `feature/command-retirement` at `38a0c58a0b533edc29908992c8c6ee64fa04eb20`.
Read this first, then [CD-CMD-SESSION-001](directives/CD-CMD-SESSION-001-session-views.md).
The maintainer's “proceed” authorizes this preparation. Approve both exact
documents before implementation; approving them together is sufficient.

## Scope and explicit schema amendment

Migrate only `/history` (PAR-017) and `/clear` (PAR-003) to the neutral owner.
The [accepted pilot](approval/pilot-acceptance.md), its three commands/aliases,
the nine accepted retirements and the exact 41 canonical names/three aliases
remain unchanged. `/clear` clears conversation history; `/cls` and
`/clearscreen` clear the display and are outside this unit.

The [foundation API](shared-command-api.md) permits family payload expansion
after reviewed schemas are frozen. Approval of this document explicitly adds
`HistoryData` and `SessionClearedData` to `FoundationData` and the exact-type
`CommandOutcome.data` whitelist. `HistoryTurn` is their nested value model.
Every original variant, constructor rule, error code, effect, registry/parser
behavior and existing pilot contract remains intact. This is the complete
SESSION-001 amendment; it grants no generic capability/result extension.
Do not rewrite the historical approved foundation or pilot documents.

## SV-01 — public models and injected port

Add exactly six public exports, preserving the existing 18:

```python
@dataclass(frozen=True, slots=True)
class HistoryTurn:
    user_message: str
    assistant_message: str

@dataclass(frozen=True, slots=True)
class HistoryData:
    turns: tuple[HistoryTurn, ...]

@dataclass(frozen=True, slots=True)
class SessionClearedData:
    pass

SESSION_SPECS: tuple[CommandSpec, ...]  # clear, history

class SessionPort(Protocol):
    def history_snapshot(self) -> tuple[HistoryTurn, ...]: ...
    def clear_history(self) -> None: ...
    async def clear_session_memory(self) -> None: ...

def build_session_handlers(port: SessionPort) -> Mapping[str, CommandHandler]: ...
```

Models live in `friday_commands.contracts`; specs, port and factory live in
`friday_commands.session_views`. The shared package retains standard-library
and own-package imports only, no dependency or executable, no default registry
population and no host/global session state. Ports are structurally typed;
do not add runtime protocol checks or require inheritance from the protocol.

Validate `HistoryTurn` fields in declaration order using the existing string
rule (string subclasses accepted, no conversion). `HistoryData` snapshots a
finite iterable once into a tuple of **exact** `HistoryTurn` instances using
the existing collection rules; reject scalars, strings, bytes, bytearray,
mappings, wrong members and model subclasses with `TypeError`. Mutation of
the input collection must not change the snapshot. `SessionClearedData` has
no fields or arguments. Essential checks remain active under `-O` and `-OO`.
Both new data variants are exact-type members of the closed outcome union;
their subclasses and unrelated payloads still fail. Existing exactly-one
data/error and error/effect invariants are unchanged. Session handlers emit
only success data and zero effects; neither invents a new error code.

The factory returns a fresh immutable mapping with exactly `clear`, `history`.
Construction performs no port calls or attribute reads and no registration.
Each handler checks exact `CommandRequest`, then exact `CommandExecution`
types before request fields; then a mismatched canonical `request.name` raises
`ValueError` before any port call. Arguments/spec and execution fields are
otherwise unused. Use explicit exceptions, no `assert` enforcement, `Any`,
casts or suppressions. Port exceptions, including `CancelledError`, propagate
unchanged; there are no retries, catches, rollback or progress callbacks.

## SV-02 — shared history behavior

The history handler calls `port.history_snapshot()` synchronously exactly once,
constructs `HistoryData` from that result and returns
`CommandOutcome(data=..., ui_effects=())`. Preserve snapshot order, duplicates,
empty strings and message contents; do not sort, truncate, filter, escape or
retrieve persisted transcripts. An empty snapshot is successful empty data.
The handler never clears history, accesses memory, reads session identity,
emits text or performs terminal/file/provider operations. Extra arguments are
ignored. Invalid port results fail through model validation without repair.

## SV-03 — shared clear sequence and failure boundaries

For a valid clear request execute precisely:

1. Call `port.clear_history()` once synchronously.
2. Await `port.clear_session_memory()` once.
3. Return `CommandOutcome(data=SessionClearedData(), ui_effects=())`.

No result is returned before step 2 finishes. A step-1 failure prevents step 2.
A step-2 failure/cancellation propagates and leaves already-cleared history
cleared; do not restore it, turn the exception into an error outcome, retry or
emit a success message. Prove the intermediate state with an event-controlled
await, not a timing sleep. No per-session lock or maintenance admission is added:
neither command is currently in Chat's shared-admission command set.

`SessionClearedData` means the existing command procedure completed. It does
not claim all persistent stores were erased. Transcript, vector/graph/global
memory, other sessions, variables, diagnostics and display state are outside
this operation. Preserve the owning service's existing behavior; do not add a
second domain implementation or broaden its clearing scope.

## SV-04 — Chat port, wrappers and presentation

Add `friday_chat.commands.session_views` with a typed `ChatSessionPort` holding
the supplied `CommandContext` by reference. Construction only stores it. Use
that context even when a different registry is carried by it; no default
registry/runtime or global catalog is constructed for these commands.

- `history_snapshot`: preserve the old truth test of `context.history`; a falsy
  value yields `()`. Otherwise iterate that history in its current order,
  unpack each pair and project each member once to a **plain built-in string**:
  `HistoryTurn("".join((f"{user}",)), "".join((f"{assistant}",)))`.
  Preserve the existing truth-test-then-iteration access order. This projection
  preserves legacy formatting of non-string message members (for example
  `False`, `None`, numbers or lists) without weakening shared field types.
  The join copies a possible custom string-subclass format result without
  calling user formatting again; naive f-string-only snapshots can change output
  when rendered a second time. Verify one format call per message member.
  Malformed pair unpacking and formatting exceptions propagate unchanged.
  Never read `context.runtime`, session, memory or registry on this path.
- `clear_history`: call the existing `context.history.clear()` in place,
  preserving list identity and external aliases. Do not replace the list.
- `clear_session_memory`: only when this method is awaited, evaluate
  `if context.runtime is not None: await context.runtime.memory.clear_session_memory()`.
  Preserve the existing two runtime reads when present, one when absent;
  neither may precede history clearing. When absent, return normally without
  constructing a runtime. Discard the service return value without testing or
  coercing it: both `True` and `False` currently produce the success message.
  The service already owns the current session; do not pass/replace its ID.

Retain `_history_handler` and `_clear_handler` signatures and their handler-map
entries. Each becomes one delegation through `invoke_session(name, args, context)`.
This adapter builds one canonical request from the matching `SESSION_SPECS`
object and the already parsed args, creates one handler mapping and awaits that
handler once. Do not rebuild command text, parse/dispatch again, or retain an
alternate legacy command engine. The supplied Chat metadata is unused, including
for wrappers explicitly registered under another name. Custom user handlers
remain authoritative and must never enter the shared factory implicitly.

`adapt_session_outcome` accepts only exact `CommandOutcome` with no error/effects,
containing exact `HistoryData` or `SessionClearedData`. Reject every other
payload/error/effect shape explicitly with `ValueError`; do not stringify unknown
payloads. Shared execution exceptions propagate before adaptation. Map success
to the unchanged Chat `CommandResult` defaults: handled true, exit false, effects
empty. `HistoryData(())` renders exactly `No conversation history.`. Otherwise:

```text
Conversation history:
1. User: <first user message>
   Friday: <first assistant message>
2. User: <second user message>
   Friday: <second assistant message>
```

Use one newline between these lines, no trailing newline, one-based numbering,
three spaces before `Friday:`; embedded newlines/Unicode are unchanged. Clear
renders exactly `Conversation history cleared.` only after the await completes.
Chat owns English rendering and the unchanged application output/cleanup flow.
Distinct injected shared history data must change the rendered output, proving
that Chat consumes the shared result rather than discarding it.

Parsed arguments are always strings. As in the pilot, direct calls supplying
non-string arguments outside the declared `tuple[str, ...]` API may now raise
the shared request's `TypeError`; their former success is not a compatibility
promise. This is an explicit proposed boundary decision requiring contract
approval, not permission to tighten Chat registration or history message input.

## SV-05 — definitions and preserved surface

`SESSION_SPECS` is ordered clear, history and exactly projects the two frozen
baseline records: session category, `/clear` and `/history` usages, descriptions
`Clear conversation history.` and `Show conversation history.`, no arguments,
aliases or detail. Replace only Chat default-tuple entries 0 and 2 with these
projections. Keep its public 39-entry tuple and builder order, and all other
37 entries unchanged. Keep `BASIC_COMMAND_HANDLERS`, parser, normalization,
registration, dispatch, admission and public Chat models unchanged.

Help, metadata, completions and all 41 names/three aliases remain byte-for-byte
compatible. Session migration leaves the other 39 command paths unchanged,
including the accepted shared pilot and the 36 other retained commands. No
retired name returns, alias is added, dependency/lock changes, CLI reuse adapter,
domain/runtime repair, confirmation interaction, file export or TUI work is
included. Source bodies and all original test assertions are protected.

## SV-06 — evidence, gates and approval

[Preparation evidence](validation/session/preparation.json) contains the exact
capture/comparison programs, pinned input hashes, receipts and a frozen baseline
of two metadata records and 25 cases from `38a0c58a0b533edc29908992c8c6ee64fa04eb20`. It characterizes
empty/ordered/Unicode/formatted/malformed history; no-runtime and true/false/error/
cancel clear; failure/access order; pending await state; parser and renamed
wrapper cases. Six comparator refusal controls prevent bool/int, ordering,
metadata and capture-identity drift. It is baseline evidence, not proof of any
new session API or approval to construct it.

The directive defines future new tests, D1–D3 incremental gates, existing pilot
196-observation regression, full owning suites, source/assertion preservation,
clean artifacts and default/standalone installed proof. Tests must use fixtures
inside their package test tree, not imports from this active planning path.
Freeze this contract, directive and preparation evidence at approval. Missing
coverage, unrepresentable legacy values, new scope, failed guard controls or a
changed authority/input requires reconciliation before construction advances.
Independent review never supplies human acceptance or publication authority.
