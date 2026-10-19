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
| 15 | [Friday Speech](queued/friday-speech/) | normal | not_granted | not_started | review provider security and approve the draft plan |
| 18 | [Human in the Loop](blocked/human-in-the-loop/) | blocked | not_granted | not_started | resolve the high-priority architecture contradictions |
| 19 | [Model-aware reasoning control](deferred/model-aware-reasoning-control/) | deferred | not_granted | not_started | explicit maintainer decision to reopen design |
| 20 | [Agent-scoped memory context](backlog/agent-scoped-memory-context/) | backlog | not_granted | not_started | promote into a bounded design packet |
| 21 | [Friday Chat framework follow-ups](backlog/friday-chat-framework-followups/) | backlog | not_granted | not_started | reconcile proposed entries against current source |
| 22 | [Strategic roadmap notes](backlog/strategic-roadmap/) | backlog | not_granted | not_started | promote one bounded initiative into planning |
| 23 | [Tool capability notes](backlog/tool-capabilities/) | backlog | not_granted | not_started | reconcile requirements with tool governance |
| 25 | [Friday runtime skills](backlog/friday-runtime-skills/) | backlog | not_granted | not_started | review the draft definition and promote a bounded first phase |
| 26 | [Friday tool manifest continuity remediation](queued/friday-tool-manifest-continuity/) | normal | not_granted | not_started | validate the native-tool trial and review discovery-aware MCP remediation tasks |
| 33 | [Board validation and GitHub delivery reconciliation](queued/friday-board-delivery-reconciliation/) | normal | not_granted | not_started | Review and approve delivery-evidence contract, migration and bounded construction directive |

## Approved

| Priority | Initiative | Condition | Authority | Delivery | Next gate |
| ---: | --- | --- | --- | --- | --- |
| 16 | [Self-Evolving Knowledge Graph](queued/self-evolving-knowledge-graph/) | normal | design_only | not_started | produce and approve the target design |

## Started

| Priority | Initiative | Condition | Authority | Delivery | Next gate |
| ---: | --- | --- | --- | --- | --- |
| 14 | [Friday TUI](active/friday-tui/) | normal | granted | pushed | Independently reconcile completed/success exact-source Ubuntu run and job 39284711876 on pushed aa8ae784; N01B-07 is proposed only; installed macOS/Linux TUI terminal UAT remains a release gate |
| 27 | [Friday-telemetry-rewire](active/friday-telemetry-rewire/) | normal | closed | merged | core TELEM-01–04 accepted; PR #7 merged as 1302b5f; remote and local telemetry branches retired; construction closed; retain frozen evidence paths |
| 28 | [Remove deprecated credential-bearing files and rotate exposed credentials](active/friday-deprecated-credential-cleanup/) | normal | granted | merged | PR 9 merged and remote branch deleted; maintainer lifecycle closeout/acceptance remains |
| 29 | [Friday 0.1.0a3 repository version bump](active/friday-alpha3-version-bump/) | normal | granted | released | Maintainer lifecycle closeout; alpha3 production PyPI publication and fresh install verified |
| 30 | [Precise Python monorepo and package READMEs](active/friday-readme-refresh/) | normal | granted | merged | Source delivered in PR #10, merge 465c5643; maintainer lifecycle acceptance remains |
| 31 | [Current technical end-user guides for alpha3](active/friday-guides-refresh/) | normal | granted | merged | Source delivered in PR #10, merge 465c5643; maintainer lifecycle acceptance remains |
| 32 | [Friday Chat quick start for clone and PyPI users](active/friday-chat-quick-start/) | normal | granted | merged | Source delivered in PR #10, merge 465c5643; maintainer lifecycle acceptance remains |
| 34 | [Friday 0.1.0a4 coordinated release](active/friday-alpha4-release/) | normal | granted | released | Maintainer lifecycle closeout; alpha4 source merged, all 17 PyPI projects and fresh production install verified |

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
| 4 | [Friday MCP 2026-07-28 protocol and Streamable HTTP upgrade](../archive/completed/2026/friday-mcp-protocol-upgrade/) | normal | closed | merged | MCP delivery closed; next queued work is Langfuse contract and construction-directive preparation |
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
