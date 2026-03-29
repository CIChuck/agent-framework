# Phase 5-A: Layered Prompt Composition and Transcript-Backed Runtime

**Status:** Proposed  
**Date:** 2026-03-09  
**Audience:** Runtime architects, agent-framework maintainers, memory/transcript maintainers

---

## 1. Problem Statement

The current runtime prompt path is implicit and overly agent-owned. Agent YAML supplies the effective system prompt, while runtime and orchestration do not provide a first-class base prompt contract. At the same time, transcript capability exists in `friday-transcript`, but the runtime execution path still defaults to `InMemoryEpisodicStore` and does not wire `context_log` as a primary execution record.

This creates three architecture problems:

1. Prompt composition is hard to reason about and difficult to inspect after execution.
2. Runtime agent turns are not persisted in the same transcript-first model that previously enabled strong debugging and replay workflows.
3. The orchestrator boundary is blurry because prompt ownership is not clearly separated from routing and delegation.

---

## 2. Phase Objective

Phase 5-A establishes a layered prompt contract and makes transcript the primary persistent execution record for runtime agents.

This phase introduces:

1. A runtime-owned base system prompt layer.
2. Agent-owned prompt fragments that remain in agent configuration.
3. Centralized prompt composition before LLM execution.
4. Transcript-backed runtime persistence, with prompt/response capture stored through `friday-transcript`.

Replay and export UX are explicitly out of scope for this phase.

---

## 3. Architecture Decisions

## 3.1 Prompt Ownership Is Layered

The effective prompt sent to the model is composed from distinct layers:

1. Runtime base system prompt.
2. Agent prompt fragment.
3. Optional task, workflow, or handoff supplements.

The base runtime prompt defines framework-wide operating policy such as tool-use rules, memory policy, or execution constraints. The agent configuration defines identity, role, goal, and agent-specific instructions. Workflow or delegation context may add execution-local constraints, but it does not replace either of the first two layers.

The final prompt is therefore not universally identical across all agents. The universal portion is the runtime base layer only.

## 3.2 Orchestrator Remains Control Plane

The orchestrator remains responsible for routing, delegation, and agent selection. It should not become the authoritative owner of global prompt text.

Its role in this design is to:

1. Select which agent executes.
2. Pass handoff or workflow context when needed.
3. Defer prompt assembly to a centralized prompt-composition path.

This preserves a clean separation between control-plane behavior and prompt policy.

## 3.3 Transcript Belongs to `friday-transcript`

Transcript storage, context logs, exporters, and replay-oriented artifacts belong in `friday-transcript`, not `friday-memory`.

`friday-memory` remains responsible for memory extraction, recall, and memory-oriented consumers of turn data. Runtime persistence should therefore flow through transcript-backed stores, with memory reading from that durable execution record through explicit adapters.

---

## 4. Current-State Gap

The current runtime behavior does not yet reflect the desired architecture:

1. Runtime execution still relies on `InMemoryEpisodicStore` by default.
2. The runtime path does not treat transcript as the primary persistent record.
3. `context_log` is not wired as a standard part of runtime turn capture.
4. Agent execution records are therefore weaker than the transcript-rich behavior previously seen in the `friday.py` integration path.

This phase closes that gap without redesigning replay/export UX.

---

## 5. Target Model

## 5.1 Centralized Prompt Composition

Prompt composition becomes an explicit runtime concern. Before an LLM call is made, runtime assembles the effective prompt from:

1. `runtime.prompting.base_system_prompt`
2. the rendered agent prompt fragment from agent configuration
3. optional workflow or handoff supplements

That composed result is the prompt contract used for inference and inspection.

## 5.2 Transcript-Backed Runtime Execution

When transcript is enabled, runtime should persist turns through a transcript-backed episodic path instead of treating episodic memory as an in-memory-only structure.

The transcript becomes the primary persistent execution record for runtime agents. Each completed turn should capture:

1. user input
2. assistant response
3. agent provenance
4. LLM service and provider attribution
5. the composed prompt or final message payload needed for debugging and later replay support

## 5.3 Memory Consumes the Execution Record

Memory extraction continues after the turn, but it should consume a durable turn record rather than act as the primary owner of the transcript itself. This preserves package boundaries and keeps execution history reconstructable independent of extraction outcomes.

---

## 6. Configuration Direction

Runtime gains a first-class prompt section for the universal base layer. Agent YAML continues to carry the agent-specific prompt fragment. Execution input remains execution data, not runtime-global prompt policy.

The intended direction is:

1. Runtime configuration owns base system prompt policy.
2. Agent configuration owns agent-specific instructions.
3. Workflow or delegation paths contribute execution-local supplements.
4. Transcript configuration controls whether transcript-backed persistence and context-log capture are enabled.

This is a framework-wide contract, not an experiment-only pattern.

---

## 7. Phase Scope

In scope:

1. Runtime base system prompt layer.
2. Centralized prompt composition.
3. Transcript-backed runtime persistence.
4. Context-log capture as part of the runtime execution record.
5. Clear package responsibility between `friday-transcript` and `friday-memory`.

Out of scope:

1. Replay UX and transcript export tooling.
2. A broader orchestrator redesign.
3. New prompt or response scoring semantics.
4. Renaming agent YAML prompt fields as part of this slice.

---

## 8. Expected Outcome

Phase 5-A makes runtime prompting explicit, inspectable, and durable. It gives the framework one coherent prompt-construction model, keeps the orchestrator focused on delegation, and restores transcript-first execution records as the foundation for later replay, inspection, and memory rebuild capabilities.
