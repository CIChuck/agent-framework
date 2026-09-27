# Friday Runtime Skills

---
title: Friday Runtime Skills
initiative: friday-runtime-skills
document_type: initiative-index
status: backlog
work_state: queued
condition: backlog
created: 2026-09-27
updated: 2026-09-27
next_gate: review the draft definition and promote a bounded first phase
implementation_authority: not granted
---

This backlog packet defines configurable Agent Skills-style instructions for
Friday runtime and Friday Chat. A configured skills directory and explicit
selection list would let Friday validate skills at startup and place selected
instructions immediately after the base system prompt on applicable turns.
Context engineering would account for those instructions before allocating
space to history, retrieved memory, and tools.

- [Comprehensive draft build plan](build-plan.md)
- [Related `friday.md` startup-context proposal](../../queued/friday-startup-context/README.md)
- [Development task lifecycle policy](../../../reference/policies/development-task-lifecycle.md)

This is a backlog definition, not approval to implement. The linked
`friday.md` proposal covers a separate startup instruction file; the two
features need one consistent prompt-placement and budget contract.
