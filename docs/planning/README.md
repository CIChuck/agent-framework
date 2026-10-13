# Planning Dashboard

This dashboard is generated from [`board.yaml`](board.yaml), the canonical
current-state registry. Do not edit task state in this file directly.

The governing workflow is the
[development task lifecycle policy](../reference/policies/development-task-lifecycle.md).
Directory placement does not grant implementation authority.

## Queued

| Priority | Initiative | Condition | Authority | Delivery | Next gate |
| ---: | --- | --- | --- | --- | --- |
| 5 | [Friday Langfuse implementation](queued/friday-langfuse-integration/) | normal | not_granted | not_started | after MCP upgrade acceptance, prepare and approve the Langfuse integration contract and exact construction directive |
| 6 | [Friday Memory V2](queued/memory-v2/) | normal | not_granted | not_started | choose and approve the next design artifact |
| 7 | [Tool governance](queued/tool-governance/) | normal | not_granted | not_started | reconcile reviews into an approved contract plan |
| 8 | [Framework validation and contracts](queued/framework-validation-and-contracts/) | normal | not_granted | not_started | revalidate scope and obtain implementation approval |
| 9 | [Prompt-injection mitigation](queued/prompt-injection-mitigation/) | normal | not_granted | not_started | reconcile the historical plan with current tool-governance authority |
| 10 | [Claude Agent SDK tools](queued/claude-agent-sdk-tools/) | normal | not_granted | not_started | confirm plan currency and authorize implementation |
| 11 | [Friday startup context](queued/friday-startup-context/) | normal | not_granted | not_started | review and approve the draft feature plan |
| 12 | [Friday Web Chat](queued/friday-web-chat/) | normal | not_granted | not_started | review and approve the draft product plan |
| 13 | [Friday API](queued/friday-api/) | normal | not_granted | not_started | review architecture and approve a bounded phase |
| 14 | [Friday TUI](queued/friday-tui/) | normal | not_granted | not_started | review and approve the draft product plan |
| 15 | [Friday Speech](queued/friday-speech/) | normal | not_granted | not_started | review provider security and approve the draft plan |
| 18 | [Human in the Loop](blocked/human-in-the-loop/) | blocked | not_granted | not_started | resolve the high-priority architecture contradictions |
| 19 | [Model-aware reasoning control](deferred/model-aware-reasoning-control/) | deferred | not_granted | not_started | explicit maintainer decision to reopen design |
| 20 | [Agent-scoped memory context](backlog/agent-scoped-memory-context/) | backlog | not_granted | not_started | promote into a bounded design packet |
| 21 | [Friday Chat framework follow-ups](backlog/friday-chat-framework-followups/) | backlog | not_granted | not_started | reconcile proposed entries against current source |
| 22 | [Strategic roadmap notes](backlog/strategic-roadmap/) | backlog | not_granted | not_started | promote one bounded initiative into planning |
| 23 | [Tool capability notes](backlog/tool-capabilities/) | backlog | not_granted | not_started | reconcile requirements with tool governance |
| 25 | [Friday runtime skills](backlog/friday-runtime-skills/) | backlog | not_granted | not_started | review the draft definition and promote a bounded first phase |

## Approved

| Priority | Initiative | Condition | Authority | Delivery | Next gate |
| ---: | --- | --- | --- | --- | --- |
| 16 | [Self-Evolving Knowledge Graph](queued/self-evolving-knowledge-graph/) | normal | design_only | not_started | produce and approve the target design |

## Started

| Priority | Initiative | Condition | Authority | Delivery | Next gate |
| ---: | --- | --- | --- | --- | --- |
| 4 | [Friday MCP 2026-07-28 protocol and Streamable HTTP upgrade](active/friday-mcp-protocol-upgrade/) | normal | granted | local | Maintainer approval of exact CD-MCP-UP-004 result/manual-refresh directive, contract, profile and UP-04 proposal before product construction |
| 26 | [Friday-telemetry-rewire](active/friday-telemetry-rewire/) | normal | closed | merged | core TELEM-01–04 accepted; PR #7 merged as 1302b5f; remote and local telemetry branches retired; construction closed; retain frozen evidence paths |

## Completed

| Priority | Initiative | Condition | Authority | Delivery | Next gate |
| ---: | --- | --- | --- | --- | --- |
| 17 | [Nonblocking Friday Chat input](blocked/nonblocking-chat-input/) | blocked | closed | unknown | complete or waive provider-backed idle-maintenance validation |

## Accepted

| Priority | Initiative | Condition | Authority | Delivery | Next gate |
| ---: | --- | --- | --- | --- | --- |
| 1 | [Development Kanban governance](../archive/completed/2026/development-kanban-governance/) | normal | closed | local | none; accepted, delivery remains local |
| 2 | [Friday Chat client-session shutdown](../archive/completed/2026/friday-chat-client-lifecycle/) | normal | closed | local | none; accepted, delivery remains local |
| 3 | [Friday MCP client enhancement](../archive/completed/2026/friday-mcp/) | normal | closed | merged | none; pull request 6 merged, optional WS-09 and later delivery require separate authority |
| 24 | [Documentation information architecture](../archive/completed/2026/documentation-governance/) | normal | closed | merged | none; accepted and merged |

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
