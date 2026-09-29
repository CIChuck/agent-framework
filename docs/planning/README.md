# Planning Dashboard

This dashboard is generated from [`board.yaml`](board.yaml), the canonical
current-state registry. Do not edit task state in this file directly.

The governing workflow is the
[development task lifecycle policy](../reference/policies/development-task-lifecycle.md).
Directory placement does not grant implementation authority.

## Queued

| Priority | Initiative | Condition | Authority | Delivery | Next gate |
| ---: | --- | --- | --- | --- | --- |
| 4 | [Friday Memory V2](queued/memory-v2/) | normal | not_granted | not_started | choose and approve the next design artifact |
| 5 | [Tool governance](queued/tool-governance/) | normal | not_granted | not_started | reconcile reviews into an approved contract plan |
| 6 | [Framework validation and contracts](queued/framework-validation-and-contracts/) | normal | not_granted | not_started | revalidate scope and obtain implementation approval |
| 7 | [Prompt-injection mitigation](queued/prompt-injection-mitigation/) | normal | not_granted | not_started | reconcile the historical plan with current tool-governance authority |
| 8 | [Claude Agent SDK tools](queued/claude-agent-sdk-tools/) | normal | not_granted | not_started | confirm plan currency and authorize implementation |
| 9 | [Friday startup context](queued/friday-startup-context/) | normal | not_granted | not_started | review and approve the draft feature plan |
| 10 | [Friday Web Chat](queued/friday-web-chat/) | normal | not_granted | not_started | review and approve the draft product plan |
| 11 | [Friday API](queued/friday-api/) | normal | not_granted | not_started | review architecture and approve a bounded phase |
| 12 | [Friday TUI](queued/friday-tui/) | normal | not_granted | not_started | review and approve the draft product plan |
| 13 | [Friday Speech](queued/friday-speech/) | normal | not_granted | not_started | review provider security and approve the draft plan |
| 16 | [Human in the Loop](blocked/human-in-the-loop/) | blocked | not_granted | not_started | resolve the high-priority architecture contradictions |
| 17 | [Model-aware reasoning control](deferred/model-aware-reasoning-control/) | deferred | not_granted | not_started | explicit maintainer decision to reopen design |
| 18 | [Agent-scoped memory context](backlog/agent-scoped-memory-context/) | backlog | not_granted | not_started | promote into a bounded design packet |
| 19 | [Friday Chat framework follow-ups](backlog/friday-chat-framework-followups/) | backlog | not_granted | not_started | reconcile proposed entries against current source |
| 20 | [Strategic roadmap notes](backlog/strategic-roadmap/) | backlog | not_granted | not_started | promote one bounded initiative into planning |
| 21 | [Tool capability notes](backlog/tool-capabilities/) | backlog | not_granted | not_started | reconcile requirements with tool governance |
| 23 | [Friday runtime skills](backlog/friday-runtime-skills/) | backlog | not_granted | not_started | review the draft definition and promote a bounded first phase |

## Approved

| Priority | Initiative | Condition | Authority | Delivery | Next gate |
| ---: | --- | --- | --- | --- | --- |
| 14 | [Self-Evolving Knowledge Graph](queued/self-evolving-knowledge-graph/) | normal | design_only | not_started | produce and approve the target design |

## Started

| Priority | Initiative | Condition | Authority | Delivery | Next gate |
| ---: | --- | --- | --- | --- | --- |
| 3 | [Friday MCP client enhancement](active/friday-mcp/) | normal | granted | local | implement bounded REM-007 native compatibility continuation then fresh VAL-013 |

## Completed

| Priority | Initiative | Condition | Authority | Delivery | Next gate |
| ---: | --- | --- | --- | --- | --- |
| 15 | [Nonblocking Friday Chat input](blocked/nonblocking-chat-input/) | blocked | closed | unknown | complete or waive provider-backed idle-maintenance validation |

## Accepted

| Priority | Initiative | Condition | Authority | Delivery | Next gate |
| ---: | --- | --- | --- | --- | --- |
| 1 | [Development Kanban governance](../archive/completed/2026/development-kanban-governance/) | normal | closed | local | none; accepted, delivery remains local |
| 2 | [Friday Chat client-session shutdown](../archive/completed/2026/friday-chat-client-lifecycle/) | normal | closed | local | none; accepted, delivery remains local |
| 22 | [Documentation information architecture](../archive/completed/2026/documentation-governance/) | normal | closed | merged | none; accepted and merged |

## Operating Rules

- Work progresses through `queued -> approved -> started -> completed -> accepted`.
- `blocked`, `deferred`, and `backlog` are conditions, not authorization.
- Only the maintainer may approve or accept work.
- Delivery state is tracked independently from work state.
- Each current initiative has one packet `README.md` containing its detailed gate.
- Completed and superseded history remains in [the archive](../archive/).

## Board Commands

Run `uv run python scripts/friday-dev-board.py <command>`.
Use `next`, `list`, `show`, and `validate` for read-only review. Mutation commands
record state, condition, or delivery transitions and regenerate this dashboard.
