# Shared command refactor — tactical plan

**Status:** P0 source characterization and P1 contract preparation are active,
not complete. No product-code unit is authorized without an approved exact
construction directive.

**Branch:** `feature/command-refactor`, branched from `master` at `c3426986`
and independent of `feature/friday-tui`. The [development board](../../board.yaml)
controls task state. The [build plan](build-plan.md) sets scope, the
[phase plan](phase-plan.md) sets exit gates, the
[architecture proposal](shared-command-architecture.md) supplies the candidate
package boundary, and the [test strategy](test-strategy.md) sets evidence
classes. The canonical [refactor intent](command_refactor.md),
[scored inventory](command-inventory.md) and [source matrix](command-matrix.md)
remain the inputs to each tactical unit.

## Active work — P0 and P1

1. **Create the source evidence ledger (P0).** Recheck the live Friday Chat
   registry against all 50 PAR IDs and three aliases. For each case, record the
   current handler, parsing/help, service and state/effect paths, applicable
   positive/invalid/unavailable/error cases, disposable fixture, exact baseline
   command/result and any evidence gap. Keep the as-built matrix intact; put
   the ledger at `validation/par-coverage-ledger.md`. A name or help entry is
   not behavior proof.
2. **Freeze Chat and generic CLI baselines (P0).** Capture source commits,
   package metadata, exact owning-suite commands, counts, skips and known
   failures. Characterize `friday-framework-cli`'s generic registry, public
   API, completion and installed entry point separately from Chat slash
   dispatch. Record Chat's use of `friday_cli` display utilities without
   treating that dependency as a command-handler dependency. Distinguish the
   generic CLI's declared entry point from its observed complete surface.
   Run effectful probes only on disposable stores.
3. **Resolve the supported surface (P1).** Update the
   [decision register](scope-decisions.md) for six selected retirements,
   `/prime`, `/set`, `/vars`, old-name behavior and the rule for existing Chat
   quirks. Explicitly reconcile the inventory's `/security-test` retirement
   score with the approved six-name scope, which currently retains it. Record
   the retained/retired target and compatibility exceptions
   separately from the frozen 50-command source matrix. Reconcile planned
   help, guides and legacy fixtures. Keep C-01 through C-06 and behavior
   enhancements in the backlog.
4. **Review the shared contract and service owners (P1).** Decide the proposed
   `packages/friday-commands/` location or an explicit alternative; define
   registry/API, typed requests/results, errors, progress, cancellation and
   UI-effect intents. Map Chat-owned reorganization, replay, security, speech,
   tool and other service dependencies to public Runtime/domain operations or
   narrow injected capabilities. Check one-way package imports. Decide whether
   the separate `friday-framework-cli` can reuse a compatible primitive through
   an adapter; if none is safe, record source-backed reasons and its protected
   regression baseline. Obtain independent architecture review and maintainer
   approval of the exact contract.
5. **Prepare the first bounded unit (P1).** Assign every PAR case and alias to
   a retained family or the retirement unit, with dependency and risk notes.
   Fix the retirement unit's order relative to family migrations. Define the
   cross-family scenario map and supported package/runtime environments. Select
   the foundation pilot from this map and prepare its exact construction
   directive. P1 closes only when the [phase gate](phase-plan.md)
   and the directive are approved; this plan does not select a pilot by itself.

The current work is steps 1–5. The PAR ledger, baseline receipts, contract,
unit/scenario maps and first directive are required outputs, not completed
evidence. No handler migration, six-name retirement, help change or package
source edit follows from this tactical plan alone.

## Later execution — after the P1 gate

| Phase | Tactical action and receipt |
| --- | --- |
| P2 — Shared foundation | Execute only approved foundation/pilot directives. For each frozen candidate, compare assigned PAR behavior, Chat text/effects, protected generic-CLI behavior, installed wheels and import direction; record independent read-only `VERIFIED` review and cumulative ledger coverage. |
| P3 — Family migration and retirement | Move retained families in the approved dependency order. Run the six-name retirement as its own unit at the P1-approved position. Require before/after effect evidence, unchanged other names/aliases, negative former-effect tests, approved old-name/help/guide handling, cumulative regressions and no duplicate active handler. |
| P4 — Cross-family integration | Run the P1 scenario map through the installed shared owner and Friday Chat outside the checkout. Run the generic CLI's protected installed regression and any approved shared adapter. Check dependency closure and state/error/effect interactions; reconcile every failure, skip or deviation with P0 and approved exceptions. |
| P5 — Aggregate review and handoff | Freeze one aggregate candidate; run exact full Friday Chat and `friday-framework-cli` suites, static/type, build, installed-client and PAR-ledger comparisons in the P1-supported environments. Record counts/limits, independent `VERIFIED` review and separate maintainer acceptance. Only then prepare the accepted commit/API/version, target surface, receipts and known limits for the deferred TUI branch. TUI parity and physical terminal UAT remain later TUI gates. |

## Exact directive and evidence boundary

Before a P2–P3 source unit, its proposed directive must name the phase and
[scope decisions](scope-decisions.md), assigned PAR cases and aliases, baseline
receipts, approved contract revision, allowed source/test/doc paths, non-goals,
service and package boundaries, fixtures, exact checks and expected results,
compatibility exceptions, installed-client gates, stop conditions and
independent review criteria. Check it against the three canonical intent files
and resolve conflicts before requesting approval. Do not submit the unit while
its applicable baseline evidence, service owner or compatibility exception is
unresolved.

After implementation, record the actual candidate commit and diff, test
receipts, deviations and fresh-context read-only review in the
[execution log](execution-log.md) and unit evidence. A candidate commit cannot
be supplied before code exists. Any source remediation found in P4 or P5 needs
a new bounded directive and a refreshed candidate review. A changed candidate
or controlling authority requires fresh validation. `VERIFIED` is separate
from maintainer acceptance, delivery and the later TUI handoff.
