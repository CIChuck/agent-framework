# Planning Dashboard

This directory contains current or potentially actionable work. Directory lanes
describe lifecycle; they do not grant implementation authority.

## Current Development Sequence

| Priority | Initiative | State | Controlling packet | Next gate |
| --- | --- | --- | --- | --- |
| 1 | Documentation information architecture | Active | [documentation-governance](active/documentation-governance/) | Complete migration, validation, and maintainer review |
| 2 | Friday Chat client-session shutdown | Draft remediation candidate | [friday-chat-client-lifecycle](queued/friday-chat-client-lifecycle/) | Reproduce and approve bounded remediation |
| 3 | Friday MCP client enhancement | Draft, not authorized | [friday-mcp](queued/friday-mcp/) | Review packet and approve `MCP-WS-00` |

The published typed-LLM `0.1.0a2` cohort is complete. Its planning records are
archived, while release evidence remains under
[reference/releases](../reference/releases/).

## Active

- [Documentation governance](active/documentation-governance/) — reorganizing
  documentation without changing product behavior or end-user guides.

## Queued

- [Friday Chat client lifecycle](queued/friday-chat-client-lifecycle/) — live
  shutdown resource warning awaiting bounded remediation authority.
- [Friday MCP](queued/friday-mcp/) — draft MCP client integration packet.
- [Memory V2](queued/memory-v2/) — completed package review and locked clean-state
  boundary; design and implementation are not authorized.
- [Tool governance](queued/tool-governance/) — security reviews and draft unified
  authorization plan.
- [Framework validation and contracts](queued/framework-validation-and-contracts/)
  — planned repository-gate and framework-contract cleanup.
- [Prompt-injection mitigation](queued/prompt-injection-mitigation/) — marked
  ready for implementation in its source plan but without an execution record.
- [Claude Agent SDK tools](queued/claude-agent-sdk-tools/) — approved historical
  tool plan awaiting current-scope confirmation.
- [Friday startup context](queued/friday-startup-context/) — draft `friday.md`
  behavior.
- [Friday Web Chat](queued/friday-web-chat/) — draft browser application plan.
- [Friday API](queued/friday-api/) and [Friday TUI](queued/friday-tui/) — product
  proposals, not current implementation authority.
- [Friday Speech](queued/friday-speech/) — unapproved draft.
- [Self-Evolving Knowledge Graph](queued/self-evolving-knowledge-graph/) —
  approved for design, not implementation.

## Blocked

- [Nonblocking Friday Chat input](blocked/nonblocking-chat-input/) — implementation
  is complete, but one provider-backed real-runtime acceptance criterion remains
  unverified.
- [Human in the Loop](blocked/human-in-the-loop/) — design packet retains open
  high-priority architecture contradictions.

## Deferred

- [Model-aware reasoning control](deferred/model-aware-reasoning-control/) — no
  active design or implementation authority.

## Backlog

- [Agent-scoped memory context](backlog/agent-scoped-memory-context/)
- [Friday Chat framework follow-ups](backlog/friday-chat-framework-followups/)
- [Strategic roadmap notes](backlog/strategic-roadmap/)
- [Tool capability notes](backlog/tool-capabilities/)

## Lifecycle Rules

- `active`: execution is in progress under explicit authority.
- `queued`: proposed, draft, or approved work that is not currently executing.
- `blocked`: started or otherwise actionable work awaiting a recorded condition.
- `deferred`: deliberately postponed work with no current action.
- `backlog`: ideas and inventories that have not become an active plan.
- completed and superseded packets belong in [the archive](../archive/).

Every initiative should have one packet `README.md` identifying its status,
authority, and next gate. A draft document never authorizes implementation merely
because it appears in `queued/`.
