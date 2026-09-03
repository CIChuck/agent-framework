# Development Kanban Governance Build Plan

Status: completed; awaiting maintainer acceptance

## Scope

1. Define canonical work states, conditions, delivery states, transition gates,
   and authority boundaries.
2. Add a machine-readable board and deterministic human-readable dashboard.
3. Import every current lifecycle packet conservatively.
4. Add validation and guarded mutation commands.
5. Add a repository-local skill that operates from the board and policy.
6. Add regression tests and integrate board checks with documentation validation.
7. Make `AGENTS.md` the canonical operational entry point for code-generation
   authority and connect it to the board and planning artifact hierarchy.

## Acceptance Criteria

- Every current planning packet appears exactly once on the board.
- The dashboard is generated from the canonical board without state drift.
- Agent-role commands cannot approve or accept work.
- Started work requires a branch; completed work requires validation evidence.
- Packet placement matches work state or condition.
- Accepted work retains explicit maintainer and delivery evidence.
- The existing documentation lifecycle and local-link checks continue to pass.
- `docs/guides/` and package runtime behavior remain unchanged.

## Out Of Scope

- A hosted web board or third-party issue-tracker integration.
- Automatic creation, push, merge, release, or deletion of Git branches.
- Authentication of a human identity beyond recorded repository process.
- Rewriting historical plan bodies solely to normalize terminology.
