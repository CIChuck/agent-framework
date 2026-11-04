# Command refactor — next-phase checkpoint

Date: 2026-11-04
Branch: `feature/command-refactor`
Status: Planning continuation; P0/P1 incomplete; product construction not authorized

## Starting point

The [maintainer decisions](scope-decisions.md#maintainer-decisions--2026-11-04)
resolve the five product/ownership questions. Nine slash names are selected for
complete removal; `/tools [category]` remains. The planned target is 41 canonical
names and three aliases. The [50-name matrix](command-matrix.md) remains the
before-change baseline, not evidence of implemented retirement.

One UI-neutral `friday-commands` package owns command semantics and structured
results. Chat and TUI own input/presentation. Preserve the separate generic
CLI public API and behavior and retained Chat quirks; bounded bug fixes require
separate decisions. Resolve security/contract violations before affected migration.

## Next bounded work: characterization and contract drafting

1. Produce `validation/par-coverage-ledger.md` for all 50 PAR cases and three
   aliases. Map each case to its handler, parsing, service/state effects,
   retained/retired disposition and reproducible positive/negative/error proof
   or explicitly unresolved evidence gap. Preserve the existing source snapshot.
2. Capture Chat and separate generic CLI baseline receipts: exact source commit,
   commands, environment, counts, skips and known failures. Inspect registry,
   completion, public API and installed entry point independently. Use disposable
   state for effectful probes; do not invoke live providers or tools implicitly.
3. Refine the [architecture contract](shared-command-architecture.md): public
   registry/invocation API, typed results, errors, progress, cancellation and
   UI effects; Runtime/domain capability ownership and Chat adapter seams;
   package/import direction and compatible CLI primitive reuse or documented
   reasons for preserving its separate registry. Ownership direction is approved;
   exact signatures and service mapping are not yet approved.
4. Map retained families and the nine-name retirement unit to PAR cases,
   cross-family scenarios, dependencies and supported environments. Select and
   justify a small foundation pilot from that map.
5. Prepare the first exact construction directive with allowed paths, non-goals,
   expected checks, evidence, stop conditions and independent review criteria.

Use the [tactical plan](tactical-plan.md), [phase gates](phase-plan.md) and
[test strategy](test-strategy.md) for the complete obligations. This checkpoint
selects the next planning slice; it does not mark its outputs complete.

## Review and stop point

Present the exact contract and first directive for required independent review
and maintainer approval. Do not generate product source merely because decisions
or planning documents are committed. Reconcile the board, branch and authority
before construction. TUI construction remains deferred until command-refactor
completion, testing and separate maintainer acceptance.

## Worktree boundaries

Keep command work on this independent branch. The Friday TUI checkout has its
own branch and skills setup. Pre-existing TUI drafts, command-follow-up backlog
edits and Chat example/config edits are outside this checkpoint and must remain
separate. Local commits do not constitute push, merge, release or acceptance.
