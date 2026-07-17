# Backlog: Agent-Scoped Memory Context for Parallel Multi-Agent Execution

**Status:** Backlog  
**Date:** 2026-03-16  
**Audience:** Runtime architects, memory maintainers, workflow/orchestration maintainers

---

## Summary

The current framework separation around memory is mostly correct:

1. `MemoryController` is the primary memory facade.
2. `ContextAssembler` handles prompt-time retrieval and context shaping.
3. `AgentBase` archives completed turns.
4. `MultiAgentMemoryController` provides namespace-aware shared/private memory behavior.

That design is coherent for the framework as it exists today, especially under sequential workflow execution. The weakness is that agent provenance is still partly expressed by mutating shared memory-controller state through `set_author(...)`. That is acceptable in the current execution model, but it becomes a design risk for parallel multi-agent workflows.

This backlog item tracks a future refactor toward agent-scoped memory contexts or memory handles.

---

## Current-State Assessment

Today, memory behavior is split across the right broad layers:

1. runtime DI creates shared memory services,
2. agents initialize session context and set memory provenance,
3. context assembly retrieves memory before inference,
4. completed turns are archived into episodic/transcript-backed memory,
5. multi-agent access can be mediated through `MultiAgentMemoryController`.

The main issue is not that the framework lacks a memory architecture. The issue is that the active agent identity is still represented partly by mutable state on a shared controller. That creates coupling between:

1. current executing agent,
2. memory provenance attribution,
3. future concurrency safety.

---

## Why This Matters

This becomes important as the framework moves closer to:

1. parallel task execution inside a pipeline,
2. parallel pipelines where dependency structure allows it,
3. richer shared/private memory policies for multi-agent runs,
4. stronger provenance guarantees for audit and replay.

A shared `MemoryController` with mutable author state is manageable when task execution is strictly sequential. It becomes fragile once multiple agents may execute concurrently in the same session or workflow.

---

## Problem Statement

The framework currently allows agent provenance to be set by mutating shared controller state. That means the memory boundary is not yet fully explicit about:

1. which agent is acting,
2. which session the memory operation belongs to,
3. which namespace or visibility policy applies,
4. whether the operation is private, shared, or promotion-gated.

The result is a design that works now, but does not cleanly scale into concurrent agent execution.

---

## Desired Direction

Introduce agent-scoped memory handles, contexts, or facades that make execution identity explicit at the memory boundary.

The intended shape is:

1. `MemoryController` remains the underlying store facade.
2. runtime or workflow execution creates a per-agent memory context for each executing agent.
3. that memory context carries:
   - `session_id`
   - `agent_id`
   - `namespace`
   - visibility or promotion policy
4. agents use the scoped memory handle instead of mutating shared author state.

This preserves the current architectural layers while removing implicit shared-state coupling.

---

## Proposed Benefits

An agent-scoped memory context would:

1. eliminate mutable shared author state as the primary provenance mechanism,
2. make multi-agent memory semantics explicit,
3. reduce concurrency hazards,
4. prepare the workflow engine for future parallel task execution,
5. improve provenance clarity for transcript, memory, and artifact inspection.

---

## Non-Goals

This backlog item does not imply:

1. replacing `MemoryController` as the core memory facade,
2. moving prompt-time retrieval out of `ContextAssembler`,
3. moving turn archival responsibility out of `AgentBase`,
4. redesigning transcript ownership away from `friday-transcript`.

The goal is a sharper boundary, not a wholesale rewrite.

---

## Candidate Design Direction

One reasonable future design is:

1. runtime creates a shared `MemoryController`,
2. runtime or workflow dispatch creates an `AgentMemoryContext` or equivalent wrapper,
3. that wrapper exposes agent-safe methods for:
   - recall
   - turn archival
   - private fact writes
   - shared fact writes or promotion requests
4. the wrapper delegates to `MemoryController` and, where needed, `MultiAgentMemoryController`
5. provenance is carried structurally through the wrapper rather than through mutable controller state

This design would align well with the existing Phase 5 direction of making runtime behavior more explicit, inspectable, and concurrency-safe.

---

## Triggers For Prioritization

This backlog item should move up in priority when any of the following happen:

1. parallel task execution is added to canonical workflows,
2. pipeline-level concurrency is introduced,
3. shared/private multi-agent memory becomes a core product requirement,
4. provenance bugs appear under multi-agent workflow runs,
5. replay or audit requires stronger agent-scoped memory attribution.

---

## Open Questions

Questions to resolve when this is promoted from backlog:

1. Should the scoped handle live in `friday-memory`, `friday-runtime`, or a shared interface package?
2. Should turn archival remain on `AgentBase`, or should archival move behind the scoped handle?
3. Should `MultiAgentMemoryController` become the primary wrapper for all multi-agent runs, or remain a specialized additive layer?
4. How should workflow dispatch create and pass per-agent memory contexts?
5. How should transcript context logs, memory provenance, and artifact provenance be correlated under concurrent execution?

---

## Current Recommendation

Do not refactor this immediately just to support Phase 5-C. The current architecture is good enough for sequential live workflow experiments.

Do keep this item active in the backlog, because it is the natural next memory-boundary optimization before or alongside parallel multi-agent workflow execution.
