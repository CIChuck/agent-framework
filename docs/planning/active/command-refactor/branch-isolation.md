# Branch isolation and merge order

**Maintainer decision, 2026-10-24:** Execute the command refactor first.
Postpone Friday TUI development until the command refactor is completed,
tested, and accepted.

`feature/command-refactor` was rebuilt directly from `master` at `c3426986`.
It carries the command packet, command follow-up backlog, and scheduling
record. It does not inherit the `feature/friday-tui` commits, package source,
tests, or uncommitted working files. The earlier stacked command tip is
preserved as `backup/command-refactor-stacked-20261024` for local provenance;
no TUI branch commit was rewritten.

The command initiative owns the shared command package/contract, Chat and
separate CLI regression, and the selected retirements. The TUI branch owns its
existing shell, UI, adapter, parity, and physical terminal UAT. Before TUI
development resumes, the maintainer must accept the completed and tested
command refactor. Then reconcile `feature/friday-tui` with the delivered
command branch, remove duplicate command-planning ownership, resolve shared
board and documentation changes once, and rerun its protected and TUI gates.

Do not open a command-refactor PR based on the old stacked tip. Compare a
future command PR against `master` and confirm that its diff contains no
`packages/friday-tui` source or TUI validation packet. Publishing, merging,
and resuming TUI remain separate lifecycle decisions.
