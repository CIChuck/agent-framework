---
title: "Architecture Overview"
description: "How the Mind, Body, and Memory Loop layers fit together."
weight: 1
---

Friday is organized into three cooperating layers: the Mind (intelligence and reasoning), the Body (tool execution), and the Memory Loop (context retrieval and learning).

---

## The Intelligence Plane & Control Plane

Friday separates concerns into two distinct planes, inspired by distributed systems architecture:

**The Intelligence Plane:**
- Memory systems (remembering and learning)
- Context engineering (what to think about)
- Decision-making (reasoning and planning)
- Knowledge representation (how information is structured)

**The Control Plane:**
- Tools (interacting with the world)
- Actions (executing commands and operations)
- Sensors (gathering information)
- Outputs (producing results)

This separation isn't just conceptual—it's architectural. The Intelligence Plane handles *what to do and why*, while the Control Plane handles *how to do it and with what*. This clean separation enables:

- **Independent scaling**: Scale memory systems separately from tool execution
- **Security boundaries**: Restrict tool access without limiting intelligence
- **Testing isolation**: Test reasoning logic without external side effects
- **Modular replacement**: Swap execution mechanisms without rewriting logic

### Architecture Diagram

```text
┌──────────────────────────────────────────────────────────────────┐
│                           FRIDAY AGENT                           │
│                                                                  │
│  ┌──────────────── INTELLIGENCE PLANE ────────────────────────┐  │
│  │                                                            │  │
│  │  ┌──────────────┐         ┌──────────────┐                 │  │
│  │  │   Memory     │         │    Context   │                 │  │
│  │  │  Controller  │◄────────┤   Assembler  │                 │  │
│  │  │              │         │              │                 │  │
│  │  │ - Vector DB  │         │ - Retrieval  │                 │  │
│  │  │ - Graph DB   │         │ - Budgeting  │                 │  │
│  │  │ - Transcripts│         │ - Formatting │                 │  │
│  │  └──────┬───────┘         └───────┬──────┘                 │  │
│  │         │                         │                        │  │
│  │         │    ┌────────────────────┴────────────┐          │  │
│  │         │    │   Prompt Architect              │          │  │
│  │         │    │  - Token budgeting              │          │  │
│  │         │    │  - Lost-in-middle mitigation    │          │  │
│  │         │    │  - Format optimization          │          │  │
│  │         │    └────────────┬────────────────────┘          │  │
│  │         │                 │                                │  │
│  └─────────┼─────────────────┼────────────────────────────────┘  │
│            │                 │                                    │
│            │    ┌────────────▼────────────┐                      │
│            │    │      LLM Service        │                      │
│            │    │  (Provider-agnostic)    │                      │
│            │    └────────────┬────────────┘                      │
│            │                 │                                    │
│  ┌─────────┼─────────────────┼────────── CONTROL PLANE ──────┐  │
│  │         │                 │                                │  │
│  │         │                 ▼                                │  │
│  │         │    ┌──────────────────────┐                     │  │
│  │         │    │   Tool Execution     │                     │  │
│  │         │    │   - Filesystem       │                     │  │
│  │         │    │   - Shell commands   │                     │  │
│  │         │    │   - Web/API calls    │                     │  │
│  │         │    │   - Code execution   │                     │  │
│  │         │    │   - Git operations   │                     │  │
│  │         │    └──────────┬───────────┘                     │  │
│  │         │               │                                  │  │
│  │         │               ▼                                  │  │
│  │         │    ┌──────────────────────┐                     │  │
│  │         └───►│  Memory Extraction   │                     │  │
│  │              │  - Entities          │                     │  │
│  │              │  - Relationships     │                     │  │
│  │              │  - Insights          │                     │  │
│  │              └──────────────────────┘                     │  │
│  │                                                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: A Single Turn

Let's trace a single conversation turn through the architecture:

```text
1. USER INPUT
   "What Python libraries should I use for my web API?"
   │
   ▼
2. CONTEXT ASSEMBLY (Intelligence Plane)
   ├─ Query memory stores in parallel:
   │  ├─ Episodic: Recent conversation history
   │  ├─ Semantic: Relevant insights about Python/APIs
   │  └─ Associative: User's prior mentions of Python, FastAPI, etc.
   │
   ├─ Token budgeting with knapsack optimization:
   │  └─ Fit maximum relevant context within LLM window
   │
   └─ Result: Assembled context payload
   │
   ▼
3. PROMPT ARCHITECTURE (Intelligence Plane)
   ├─ Structure messages for LLM:
   │  ├─ System: Base prompt + identity
   │  ├─ History: Prior conversation turns
   │  ├─ Context: Retrieved memories (tail injection)
   │  └─ Query: User's question
   │
   └─ Result: Optimized prompt with "lost-in-middle" mitigation
   │
   ▼
4. LLM INFERENCE
   ├─ Send formatted messages to LLM (OpenAI/Anthropic/etc.)
   ├─ Include tool schemas if agent has tool access
   └─ Result: Response text + optional tool calls
   │
   ▼
5. TOOL EXECUTION (Control Plane) [If tool calls present]
   ├─ For each tool call:
   │  ├─ Validate parameters
   │  ├─ Execute tool (read file, web search, git status, etc.)
   │  ├─ Capture result + metadata (latency, status)
   │  └─ Return to LLM for processing
   │
   └─ Re-Act loop continues until no more tool calls
   │
   ▼
6. MEMORY EXTRACTION (Background, Intelligence Plane)
   ├─ LLM analyzes conversation for entities
   ├─ LLM identifies relationships
   └─ LLM generates insights
   │
   ▼
7. MEMORY STORAGE (Intelligence Plane)
   ├─ Entities → Graph store (NetworkX + JSON)
   ├─ Insights → Vector store (ChromaDB with embeddings)
   ├─ Full turn → Transcript store (SQLite)
   └─ Hebbian learning: Increment hit counts for accessed entities
   │
   ▼
8. RESPONSE DELIVERY
   "For a Python web API, I recommend FastAPI or Flask..."
```

This flow happens for **every turn**, building memory incrementally.

---

## Why This Separation Matters

The Intelligence Plane / Control Plane separation is a strategic architectural decision that provides:

- **Vendor independence**: Swap LLM providers or storage backends without rewriting application logic
- **Security compliance**: Restrict tool execution (Control Plane) while maintaining intelligence (Intelligence Plane)
- **Cost optimization**: Scale memory systems separately from tool execution
- **Future-proofing**: As AI capabilities evolve, upgrade the Intelligence Plane without touching the Control Plane
- **Horizontal scaling**: Deploy multiple Control Plane instances (tool executors) behind a single Intelligence Plane (memory system)
- **Observability**: Instrument Intelligence Plane (reasoning) and Control Plane (actions) independently with different telemetry

---

## Four Foundational Principles

Friday's architecture is built on four foundational principles:

1. **Intelligence Plane / Control Plane Separation** — Intelligence (memory, reasoning) is independent of execution (tools, actions)
2. **Protocol-First Design** — Every component is swappable via abstract interfaces (zero vendor lock-in)
3. **Modular Packages** — Eight independent packages with clear dependencies (selective installation, isolated testing)
4. **Memory Loop** — Continuous learning through Context → Action → Learning cycle (compound knowledge growth)

These principles combine to create a framework that is:

- **Production-ready** — Observable, resilient, scalable
- **Vendor-independent** — Swap any component without code changes
- **Future-proof** — Architecture outlives specific implementations
- **Genuinely adaptive** — Agents that learn and improve over time

---

## Quick Reference

### Architecture Layers

```text
Intelligence Plane          Control Plane
├─ Memory stores            ├─ Tool execution
├─ Context assembly         ├─ Action results
├─ Prompt architecture      └─ Sensor inputs
└─ Decision-making
```

### Core Protocols

- **LLMClient** — LLM inference
- **VectorStoreAdapter** — Semantic search
- **GraphStoreAdapter** — Relationship storage
- **TranscriptStoreAdapter** — Conversation logs
- **ToolDefinition** — Tool schemas

### Package Dependencies

```text
Core → Memory/LLM → Agent → Tools/Transcript/MCP
```
