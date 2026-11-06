# Shared command API — P1 review draft

**Working-folder update — 2026-11-05:** The maintainer changed direction:
current command-first and Friday TUI planning is consolidated in the
`agent-framework` folder. Earlier TUI-folder directions are superseded for
current work. This transfer changes documents only; imported implementation
claims, reviews and test receipts retain their original provenance. No design
approval, construction authority or code validation is inferred.


Date: 2026-11-04
Revision: 2026-11-05 — SOL3-ARCH-001/002 and parser-fixture clarification
Status: Proposed; not approved technical authority; no construction authorization
Scope: Shared foundation API plus family ownership constraints

## Authority and evidence

Apply [O-01–O-05](scope-decisions.md), the [build plan](build-plan.md) and
[architecture proposal](shared-command-architecture.md). The
[production/effect audit](validation/production-effects-audit.md),
[default behavior audit](validation/default-behavior-audit.md) and
[baseline controls](validation/p0-failure-disposition.md) are design inputs.
P0 and P1 remain incomplete. This draft specifies foundation signatures; later
family payloads and capability methods are review obligations, not invented
approvals or construction instructions.

## Ownership and package

`packages/friday-commands`, import `friday_commands`, distribution
`friday-framework-commands`, aligned initially with workspace version 0.1.0a4.
The shared owner contains metadata, name resolution, current-compatible text
parsing, command argument validation/policy, dispatch and semantic handlers.
It imports no Chat, CLI, TUI, Rich, Textual or frontend-private classes.
The foundation uses Python standard-library types only. Future dependencies on
public Runtime/domain contracts require explicit review in family directives;
Runtime/domain packages must not depend back on the command package.

Chat keeps its text renderer, input loop, lifecycle and compatibility imports.
The later TUI renders typed data without parsing Chat output. The generic CLI
keeps its registry/parser/result API: no shared-primitive adapter is selected
because quote parsing and sync/async result contracts differ. Reuse may be
proposed later only with a demonstrated compatibility benefit.

## Foundation domain types

The first unit defines frozen dataclasses; mutable registries own private maps.
The names/fields below are the proposed public foundation contract:

| Type | Fields / meaning |
| --- | --- |
| `CommandArgument` | `name: str`, `description: str`, `required: bool=False`, `default: str|None=None`, `choices: tuple[str,...]=()`; metadata does not silently enforce grammar a handler previously ignored. |
| `CommandSpec` | `name: str`, `description: str`, `category: str`, `usage: str`, `aliases: tuple[str,...]=()`, `arguments: tuple[CommandArgument,...]=()`, `detail: str|None=None`. |
| `CommandRequest` | `name: str` canonical name, `args: tuple[str,...]`, `spec: CommandSpec`; constructed after alias resolution. No frontend object or executable string interpolation. |
| `CommandExecution` | `session_id: str|None=None`; foundation context is immutable identity only. No concrete runtime or broad service locator. Typed family execution contexts will extend through explicitly reviewed capabilities before those migrations. |
| `NoData` | Empty typed successful payload. |
| `HelpData` | `commands: tuple[CommandSpec,...]`, `focused_name: str|None=None`; data for frontend rendering, not a preformatted table. |
| `ExitData` | `requested: bool=True`; semantic request for host cleanup/exit, not process termination. |
| `FoundationData` | Closed union `NoData|HelpData|ExitData`; no `Any`/untyped dictionary escape hatch. Family payload union expansion needs reviewed schemas. |
| `CommandError` | `code: Literal['unknown_command','invalid_arguments','unavailable','failed']`, `command_name: str`, `usage: str|None=None`; no raw exception text, secret path or arbitrary template values. Family reason codes require reviewed additions. |
| `UiEffect` | Enum with only `CLEAR_SCREEN='clear_screen'` initially. |
| `CommandOutcome` | `data: FoundationData|None=None`, `error: CommandError|None=None`, `ui_effects: tuple[UiEffect,...]=()`; exactly one of data/error. Error outcomes carry no success UI effects in the foundation. |
| `DispatchResult` | `handled: bool`, `outcome: CommandOutcome|None`; false requires none, true requires a valid outcome. |

### Runtime validation boundary — SOL3-ARCH-001

Every public dataclass constructor validates its fields at runtime; there are no
trusted-only constructors or unchecked factory bypasses. Check field types in
declaration order, snapshot collection fields, then check cross-field invariants.
Wrong field/container/member types raise built-in `TypeError`; invalid permitted
values or relationships raise built-in `ValueError`. Do not depend on assertions,
type annotations or a later renderer to enforce these rules. Unknown constructor
keywords/positional arity retain the generated dataclass `TypeError` behavior.
Error message wording is not part of this foundation API.

For every `str` field, require `isinstance(value, str)`; optional strings also
allow `None`. Every boolean requires `type(value) is bool` (integers are rejected).
Model-valued fields require the exact declared dataclass type, not a duck-typed
object or subclass. `FoundationData` accepts exactly `NoData`, `HelpData` or
`ExitData` instances. Frozen models contain immutable snapshots, not caller-owned
mutable containers. NoData is not an unavailable/error payload.

For collection fields, accept a finite iterable, but reject strings, bytes,
bytearray and mappings as containers with `TypeError`. Snapshot once to a tuple
in supplied iteration order and validate every member. Do not coerce members,
sort or normalize them in constructors. An exception raised by a caller's iterator
propagates unchanged; no registry state is touched during construction.

| Constructor | Additional runtime checks after scalar typing |
| --- | --- |
| `CommandArgument` | `choices` members are strings. `required` is strictly boolean. Blank name/description are typed inputs but registration rejects them; no implicit choices/default/required argument policy is introduced. |
| `CommandSpec` | `aliases` members are strings; `arguments` members are exactly `CommandArgument`. Preserve raw strings at construction; registration alone canonicalizes and checks semantic metadata validity. |
| `CommandRequest` | `args` members are strings; `spec` is exactly `CommandSpec`; `name == spec.name`, otherwise `ValueError`. This equality is checked without renormalizing either name. The registry supplies its canonical stored spec; the constructor cannot prove registry membership. |
| `CommandExecution` | `session_id` is string or None; no normalization, nonempty or service-availability assumption. |
| `NoData` | No fields; no additional invariant. |
| `HelpData` | `commands` members are exactly `CommandSpec`; `focused_name` is string or None. No implicit normalization or registry lookup in this data constructor. |
| `ExitData` | `requested` is strictly boolean; either true or false is valid. |
| `CommandError` | `code` is a string, then one of the four declared literals; unknown string code raises `ValueError`. `command_name` is a string, including the empty unknown name; `usage` is string or None. |
| `CommandOutcome` | Non-None data is exactly a `FoundationData` variant; non-None error is exactly `CommandError`; `ui_effects` members are exactly `UiEffect`, never their string values. Exactly one of data/error must be non-None; an error with any UI effect raises `ValueError`. |
| `DispatchResult` | `handled` is strictly boolean; non-None outcome is exactly `CommandOutcome`. False requires None; true requires an outcome; a mismatched pair raises `ValueError`. |

`FoundationData` is a type alias, not another constructor. `UiEffect(value)` uses
normal Enum construction: known `clear_screen` resolves to its member; an unknown
value raises `ValueError`. Other models do not coerce strings into this Enum.
No semantic validation may inspect stores, capabilities or network state.


## Public foundation signatures

```python
class CommandHandler(Protocol):
    async def __call__(
        self, request: CommandRequest, execution: CommandExecution
    ) -> CommandOutcome: ...

class CommandRegistry:
    def register(self, spec: CommandSpec, handler: CommandHandler) -> None: ...
    def specs(self) -> tuple[CommandSpec, ...]: ...
    def names(self) -> frozenset[str]: ...
    def resolve(self, name: str) -> CommandSpec | None: ...
    async def execute_text(
        self, text: str, execution: CommandExecution
    ) -> DispatchResult: ...
```

### Canonical registration and lookup — SOL3-ARCH-002

Define `N(text) = text.removeprefix("/").strip().lower()`, in that exact order,
applied once at each public raw-name boundary. It is not idempotent for multiple
leading slashes: do not apply it repeatedly to an already normalized key.

`register(spec, handler)` accepts exactly `CommandSpec` plus a callable handler;
wrong spec/handler types raise `TypeError`. A handler is contractually async;
its returned value must be awaitable and resolve to exactly `CommandOutcome`,
otherwise execution raises `TypeError` without retry. No registration-time
handler invocation or coroutine-function introspection is required.

Registration computes and validates a new candidate entirely before mutation:

1. Copy the input metadata into fresh snapshots; leave the caller's spec unchanged.
2. Set stored name to `N(spec.name)` and aliases to `tuple(N(a) for a in spec.aliases)`.
   Trim description, category and usage with `.strip()`. Preserve detail verbatim.
3. Reject empty normalized canonical names **and aliases** with `ValueError`.
   Reject blank trimmed description/category/usage with `ValueError`; do not
   synthesize usage. Each argument must have nonblank `name.strip()` and
   `description.strip()`; otherwise `ValueError`. Preserve argument field strings,
   default, choices and flags verbatim after those checks; do not trim/normalize
   argument spelling or infer handler validation.
4. Check the whole normalized canonical-plus-alias tuple for duplicates within
   this registration and collisions with any existing canonical/alias key.
   Any duplicate raises `ValueError`. All earlier maps remain unchanged.
5. Build one fresh immutable canonical `CommandSpec` from those computed values,
   including copied argument snapshots; atomically publish it and its handler
   and alias keys. No await or handler call occurs in registration.

`specs()` returns stored canonical specs sorted by stored canonical name.
`names()` returns a frozenset of canonical and alias keys. `resolve(raw_name)`
requires a string (otherwise `TypeError`), applies `N` once and performs alias/canonical map lookup.
All three methods and dispatched `CommandRequest.spec` expose the same canonical
metadata values, never the original untrimmed caller spec. Resolved aliases
produce `request.name == request.spec.name ==` the stored canonical key.

Blank aliases are deliberately invalid in this new foundation: they must not
make bare `/` executable. This does not change any existing default name/alias
or authorize editing Chat's current registration API; compatibility of external
registration shims must be reviewed before that later adapter migration.

### Text parsing and independent frozen fixtures

`execute_text` requires string text and exactly `CommandExecution`, otherwise
`TypeError` before dispatch. Only a literal leading `/` starts dispatch. Remove
that dispatch slash, strip remaining text, split on whitespace, apply `N` **once**
to the first token and preserve argument spelling/order. Look up that parsed key
directly; do not pass it through public `resolve()` and normalize it a second time.
No shell-style quoting or unescaping. Empty `/` is handled as unknown name `''`.
Unknown names yield typed `unknown_command`; ordinary text yields unhandled.
Do not add generic argument-count/choice rejection before a retained handler
that currently accepts/ignores tokens. Handler-level grammar migrates explicitly.

With only canonical `help`, alias `h`, and canonical `read` registered, freeze:

| Text | Parsed key / args | Dispatch expectation |
| --- | --- | --- |
| `hello` or ` /HELP topic` | not dispatched | handled false, no outcome, zero handler calls |
| `/` | `''`, `()` | unknown name, zero handler calls |
| `/HELP topic` | `help`, `('topic',)` | one help invocation |
| `//HELP topic` | `help`, `('topic',)` | one help invocation |
| `///HELP topic` | `/help`, `('topic',)` | unknown; must not become help by repeated normalization |
| `/ /HELP topic` | `help`, `('topic',)` | one help invocation |
| `/   HELP  A B` | `help`, `('A', 'B')` | one help invocation |
| `/H topic` | `h`, `('topic',)` | canonical request name/spec both help |
| `/read "a b.txt"` | `read`, `('"a', 'b.txt"')` | unchanged quoted fragments |

These expected tokens were reproduced from frozen Chat source, not from a new
registry. Also freeze registration inputs `/HELP ` with alias `/H ` to stored
`help`/`h`; a later ` help ` or alias `H` collides after normalization. The exact
normalization order means `N(' /HELP ') == '/help'`, not `help`. Nonempty keys
that retain a slash after this one-pass operation remain valid; do not impose
an unapproved identifier regex. Requests compare stored identity without `N`.

Handlers run once and are awaited once. Unhandled exceptions/cancellation propagate
in the foundation rather than being silently turned into successful results.
Family-specific existing catches, classifications and safe output must be mapped
before wiring Chat. No automatic retries. The registry neither writes stores nor
executes UI effects nor mutates host exit state. Hosts apply `ExitData` and UI
intents once using their current lifecycle. A UI effect failure is reported by
the frontend and does not re-execute a completed command.

## Typed family capabilities and payload obligations

These are proposed ownership boundaries, not complete family interface signatures.
A family cannot start construction until its methods and result schemas are frozen.
Adapters supply capability objects; they must not duplicate command policy or
implement a second harness. Prefer existing neutral domain models; relocate or
adapt Chat-owned models under a separately bounded directive when necessary.

| Capability family | Retained commands | Required typed data and operation ownership |
| --- | --- | --- |
| Session views | clear, history | History entries and clear operation; preserve the clear-before-memory-await ordering. Host session ID and domain-owned memory are separate from the renderer. |
| Context diagnostics | context, debug, debug-budget, debug-retrieval, prompt, timing | Read-only context/prompt/debug/budget/timing snapshots with availability states. Export variants use a reviewed file capability, never a renderer write. |
| Memory queries | memory, insights, summaries, meta, entities, list-ingested | Metric state/value, typed records, graph entities/relationships, ingested-source view, component warnings. Preserve bounds, zero/unknown distinction, partial data, no synthesis on read. |
| Memory/maintenance effects | reset, compact, lifecycle, migrate, reorganize | Typed requests/stage reports plus admission/coordinator capabilities. Domain owns store effects; shared policy preserves reset stages and flush-before-compact. Recovery/backup remain domain operations. |
| Files/ingestion | read, ingest | Reader result, source identity, line limit/truncation, ingestion receipt; reader/domain owns decoding/storage. Preserve existing tokenization and error meanings. |
| Transcript/export | sessions, transcript, export, export-prompts | Session identity/markers, typed entries/context logs and export manifests. Domain owns safe destinations, collision handling, partial cleanup and WAL-visible queries. |
| Replay | replay | Typed replay request/report, ordered turn execution and existing admission semantics; no new frontend-owned model loop. |
| Tool inventory | tools | Typed tool definitions, categories, parameters, MCP registration/status/rejection/export diagnostics. Query aggregate admitted registry without native-concrete-type checks. No manual execution/selection policy from retired names. |
| Orchestration | agent, agents, status, switch, delegate | Agent descriptors, active identity, switch/delegate receipts. Preserve restoration of the prior agent after delegation success/failure. |
| Security | security, security-config, security-test | Typed config, sanitization stats, validated updates and deterministic local-test reports. Preserve invalid-update rollback and counter effects; no implied full security acceptance. |
| Speech | speech, speech-test | Typed speech state/config and local test report. Preserve prompt-snippet effects; deterministic speech tests do not prove real audio. |
| Workflow | workflow | Typed list/run/status/approval/skip requests/results. Preserve actual service authority and pending approval semantics; no synthetic approvals. |

Help, cls and exit need no Runtime/domain capability. They are first-family pilot
candidates after the foundation; the foundation itself ships no default command
handlers and does not route Chat. The nine retired names never enter the final
default registry. Their old source/tests remain baseline evidence until the
separate retirement unit removes supported-surface expectations.

Family outcomes must support partial data plus typed component warnings and
ordered effect-stage receipts. Do not bolt these onto `CommandError` as untyped
strings/dicts. Freeze the actual family schemas before expanding the foundation
union. Domain text (for example a transcript message) is content; renderer-built
tables, ANSI escapes and Chat success strings are presentation.

## Lifecycle, admission, cancellation and observability

The host owns capability construction and close/drain lifecycle. Shared commands
borrow capabilities for one invocation; they do not open clients or close Runtime.
Session state persists in the host/domain, not global registry state. Progress
needs typed ordered stage events and an awaited sink in the maintenance-family
contract; raw Chat progress strings are not the neutral interface.

Reuse the existing gate through a neutral capability and preserve current
shared/exclusive nesting/fairness. No unconditional new registry lock. Before
maintenance migration, specify cancellation while waiting vs after mutation,
progress-sink failure, already-completed effects and recovery ownership. Do not
promise rollback or cancellation of a service that has not exposed it.

Preserve existing telemetry ownership and policy. Metadata discovery/help do not
call providers or persist user content. No new backend, event transport or logging
of prompts, secrets, raw exception strings or hidden reasoning is implied.

## Verification specification for review

| ID | Requirement | Proof required before unit completion |
| --- | --- | --- |
| API-01 | Neutral dependency closure | Build/install foundation outside checkout; import guard rejects all frontend modules; static import audit of transitive closure. |
| API-02 | Registry integrity | Canonical reconstruction/trimming, blank alias/argument rejection, normalized duplicates and other malformed metadata leave snapshots unchanged; immutable views and request/spec identity. |
| API-03 | Preserved grammar | Independent frozen table above, including multi-slash and normalization order; compare tokens, unknown meaning and handler count. Keep generic CLI tests unchanged. |
| API-04 | Typed outcomes | Constructor negatives cover every runtime-validation row, exact TypeError/ValueError classes, opaque payloads, invalid codes/effects/member types, request/spec mismatch and data/error/handled combinations; no unchecked payload escape. |
| API-05 | One execution | Recording async handler called once; exception/cancellation propagation; registry performs no I/O, UI application or host exit mutation. |
| API-06 | No early migration | Chat still owns its current behavior during foundation-only unit; all 50/3 baseline names remain. Installed foundation exposes no default handlers. |
| API-07 | Family parity | Before/after typed semantic data, stage/effect order, safe warnings, exact Chat text via adapter, invalid/unavailable/partial/cancel paths for each migrated PAR case. |
| API-08 | Retirement | All nine absent from default resolution/help/completion; unknown handling has no old effects or notices; 41 names/three aliases remain. |
| API-09 | Host behavior | Chat renderer/lifecycle applies intents once, retains established text and cleanup; later TUI UAT is separate. |

The foundation directive binds API-01–API-06 only. No user-visible new interface
ships in that unit; API/UAT review is import/dispatch evidence. Final client and
TUI acceptance requires API-07–API-09 and the project's existing phase gates.

## Open engineering review items

Review the foundation signatures/invariants and package metadata; approve or
amend them before construction. Complete family method/payload definitions,
transitive service relocation, cancellation/progress behavior, supported installed
environments, generic CLI entry-point limitation disposition and the migration/
retirement unit order. The full contract is not approved or complete merely
because this foundation draft is reviewable.
