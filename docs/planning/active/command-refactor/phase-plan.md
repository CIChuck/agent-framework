# Shared command refactor — phase plan

**Status:** Measurable planning gates derived from the canonical
[refactor intent](command_refactor.md), [scored inventory](command-inventory.md)
and [command matrix](command-matrix.md) through the approved
[build-plan scope](build-plan.md) and current [scope decisions](scope-decisions.md).
The technical contract and exact construction directives remain open. This
plan grants no product-code authority.

The [test strategy](test-strategy.md) defines comparison methods and protected
regression classes. The [tactical plan](tactical-plan.md) tracks current work;
each P2–P3 construction unit needs its own approved directive with exact files,
fixtures, commands, expected results and stop conditions.

## Gate rules and evidence trail

- Keep a PAR coverage ledger under `validation/` for all 50 baseline names and
  three aliases. Each row must identify its source behavior, current
  disposition (including any P0 open decision), applicable positive, invalid,
  unavailable, error and effect cases, fixture, before-change receipt, owning
  unit, after-change receipt and any approved exception. Mark an inapplicable
  case with a reason; a registry name or passing help test alone is not
  behavior evidence.
- Reconcile every scope or contract decision against the three canonical
  intent documents, the ledger, help, compatibility fixtures and user guides.
  The six selected retirements are intentional exceptions to preserved Chat
  behavior; consolidation and other enhancements remain in the backlog.
- From P1 onward, a gate cannot pass with an unassigned PAR case, an
  unexplained baseline failure or skip, an unapproved behavior change, a
  duplicate active maintained handler, or an unresolved import-boundary failure.
  Record the source commit, test command, fixture, environment, counts, skips
  and result for each receipt.
  Resolve or explicitly approve deviations before advancing.
- `VERIFIED` independent review, maintainer acceptance, delivery and later TUI
  parity are separate outcomes. A general phase exit never replaces the exact
  construction directive required for each source unit.

## Phase gates

### P0 — Characterize the source

Freeze Chat's 50 canonical names and three aliases, plus the separate
`friday-framework-cli` registry, public API, completion and installed entry
point. Record Chat's existing use of `friday_cli` display utilities separately
from slash-command dispatch. Create the PAR ledger with source handlers,
service/effect paths, representative disposable fixtures and baseline receipts.
Capture full owning-suite baselines with known failures and skips.

**Exit:** All 50 PAR IDs and three aliases are accounted for. Each applicable
behavior class has a reproducible baseline, or an explicit evidence gap that
must close before its construction unit. Chat and CLI receipts identify exact
commits, commands and environments. This gate does not authorize a source edit.

### P1 — Decide surface, contract and unit map

Resolve O-01 through O-04 in the [decision register](scope-decisions.md) and
approve an O-05 rule for baseline quirks and per-command exceptions. Approve
the proposed `packages/friday-commands/` location or an explicit alternative,
the neutral registry/API, typed result and UI-effect model,
error/progress/cancellation semantics, capability boundaries, Chat-owned
service relocation or injection map, dependency direction and separate CLI
reuse role: a compatible adapter or a source-backed reason no safe seam exists.
Map every PAR case to a retained family or the six-name retirement unit, with
dependencies and risk. Define cross-family scenarios and supported
package/runtime environments. Decide when the
retirement unit runs relative to family migrations before either begins.

**Exit:** The reviewed technical contract, supported-surface and compatibility
exception list, complete family/unit, service-ownership and scenario maps,
supported-environment matrix, retirement order and first exact construction
directive are approved. The ledger is ready for the first unit. Any decision
needed by that unit or any unassigned PAR case blocks implementation.

### P2 — Prove the shared foundation

Implement the approved registry, parsing, help, result/effect and adapter seams
in bounded units. Migrate only pilot semantics named in those directives.
Preserve current Chat output and established CLI behavior.

**Exit:** Each frozen candidate passes its PAR comparisons, protected Chat/CLI
tests, isolated package/import checks and independent read-only `VERIFIED`
review. One shared implementation owns each migrated command; remaining Chat
handlers are not exposed as TUI implementations. Record cumulative ledger
coverage and every approved exception.

### P3 — Migrate retained families and retire six names

Execute approved retained-family units in dependency order. Run the separately
scoped retirement unit at the position fixed in P1; do not migrate a handler
selected for retirement merely to delete it later. Compare normalized
requests, result meaning, errors, ordered progress, session/runtime and
file/tool effects, and Chat presentation on disposable fixtures.

**Exit:** Every retained PAR case has before/after evidence and one active
shared implementation. Each unit passes focused and cumulative Chat/CLI
regressions, installed checks and independent review. All six retired names
have negative former-effect checks and the approved old-name, help,
completion, guide and legacy-fixture treatment. No PAR case remains unassigned
or unreviewed.

### P4 — Cross-family and installed integration

Exercise interactions across memory/ingestion, file display,
sessions/transcripts/replay, security/workflow, tools and guarded maintenance
as applicable. Build and install the shared owner and both current terminal
clients outside the checkout; check dependency closure, real adapters, errors
and state/effect consistency.

**Exit:** The P1 scenario map, owning suites, installed entry points and
package-boundary checks pass against a frozen integration candidate. Compare
every failure, skip and deviation with P0; fix it or record an explicitly
accepted exception. Current-path security and workflow tests do not complete
their separate later capability reviews.

### P5 — Aggregate review and acceptance

Run the exact full-suite, static/type, build, installed-client and PAR-ledger
comparison commands against one frozen candidate in the supported
environments. Produce an aggregate evidence report and independent read-only
review.

**Exit:** All 50 baseline cases reconcile to retained equivalence or an
approved retirement exception. Applicable Chat and `friday-framework-cli`
gates pass with recorded counts and limits; import direction and single-owner
rules hold. The reviewer returns `VERIFIED`, then the maintainer separately
accepts the result. Record the accepted commit, public API, command surface,
known limits and receipts in a TUI handoff manifest.

## Handoff boundary

After P5 acceptance, the deferred Friday TUI project may resume on its own
branch and consume the accepted shared contract. The handoff manifest gives
TUI the retained-command target, six retired-name policy, semantic PAR cases,
package/API version and known limitations. TUI command-by-command parity,
frontend rendering, interaction and physical terminal UAT remain separate TUI
acceptance gates. P5 does not claim that those tests have passed.
