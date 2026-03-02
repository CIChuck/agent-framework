---
title: "The Memory Loop"
description: "How Friday continuously encodes, retrieves, and learns from every interaction."
weight: 2
---

The Memory Loop is Friday's continuous learning mechanism that encodes experiences, retrieves relevant context, and updates knowledge weights after every interaction.

Friday agents operate in a continuous loop that mimics human learning:

```text
    ┌──────────────────────────────────────────┐
    │                                          │
    ▼                                          │
┌────────────┐                                │
│  CONTEXT   │  Retrieve relevant memories    │
│  ASSEMBLY  │  Budget tokens optimally       │
│            │  Format for LLM                │
└─────┬──────┘                                │
      │                                       │
      ▼                                       │
┌────────────┐                                │
│   ACTION   │  LLM generates response        │
│ GENERATION │  Optionally calls tools        │
│            │  Produces output                │
└─────┬──────┘                                │
      │                                       │
      ▼                                       │
┌────────────┐                                │
│  LEARNING  │  Extract entities               │
│  (MEMORY)  │  Identify relationships         │
│            │  Store insights                │
└─────┬──────┘                                │
      │                                       │
      │  Memory informs next context          │
      └───────────────────────────────────────┘
```

**This loop runs for every conversation turn**, continuously building knowledge.

---

## Phase 1: Context Assembly

**Goal:** Gather relevant information from memory stores to inform the LLM's response.

**Process:**

1. **Parallel Retrieval** — Query all three stores simultaneously:
   - **Episodic**: Last N conversation turns (default 10)
   - **Semantic**: Similarity search for relevant insights (embedding-based)
   - **Associative**: Entities and relationships from knowledge graph

2. **Scoring & Ranking** — Each memory gets a relevance score based on:
   - **Semantic similarity** to current query (cosine distance)
   - **Recency** (newer memories score higher)
   - **Importance** (Hebbian hit_count for entities)
   - **Stage** (long-term memories score higher than short-term)

3. **Token Budgeting** — Use knapsack algorithm to select optimal subset:
   - Each memory has a **token cost** (estimated by character count / 4)
   - Each memory has a **value** (relevance score)
   - Problem: Maximize value while staying within token budget
   - Solution: Dynamic programming 0/1 knapsack solver

4. **Result**: `ContextPayload` containing system prompt, conversation history, retrieved insights, loaded entities, injected tools, and scoped variables

**Performance Target:** <200ms for context assembly

---

## Phase 2: Action Generation

**Goal:** Generate a response, optionally calling tools if needed.

**Process:**

1. **Prompt Architecture** — Structure messages for LLM:
   ```text
   System: Base identity + capabilities
   History: Prior conversation (chronological)
   Context: Retrieved memories (tail injection - "lost in middle" mitigation)
   Tools: Available tool schemas (if agent has tools)
   Query: User's current message
   ```

2. **LLM Inference** — Send to LLM provider with resilience patterns (retry, timeout, circuit breaker)

3. **Tool Execution** (Re-Act Loop if tools called):
   ```text
   While has_tool_calls and iterations < max_iterations:
       For each tool call:
           Validate parameters
           Execute tool (async)
           Capture result + metadata
       Add tool results to message history
       Call LLM again with results
   ```

4. **Result**: Final response text + execution metadata

**Performance Target:** 1-5s for LLM inference (provider-dependent), <100ms per tool execution

---

## Phase 3: Learning (Memory Storage)

**Goal:** Extract structured knowledge from the conversation and store for future retrieval.

**Process:**

1. **Extraction** (runs asynchronously, doesn't block response):
   - **Entity Extraction**: LLM identifies entities with types
   - **Relationship Extraction**: LLM identifies semantic connections
   - **Insight Generation**: LLM generates actionable knowledge

2. **Storage**:
   - **Entities & Relationships** → Graph store (merge with existing, increment hit counts, persist to JSON)
   - **Insights** → Vector store (generate embeddings, store in `memories_short_term` collection initially)
   - **Full Turn** → Transcript store (user message, assistant response, tool calls, token usage, timestamps)

3. **Lifecycle Management** (runs after each turn or on schedule):
   - **Promotion**: Short-term memories with high access + age → long-term
   - **Decay**: Long-term memories with no recent access → decayed
   - **Reactivation**: Decayed memories accessed again → back to long-term

**Performance Target:** Extraction runs in background (1-3s), doesn't block next turn

---

## The Full Cycle in Action

Let's trace a complete cycle with a realistic example:

**Turn 1 - First Message:**

**User:** "Can you help me write a Python function to validate email addresses?"

1. **Context Assembly:** Empty (first turn) — minimal context, just system prompt
2. **Action Generation:** LLM generates a Python function using regex — no tools called
3. **Learning:**
   - Entities: "Python" (Technology), "email validation" (Concept)
   - Relationships: User WORKING_ON email validation, email validation IMPLEMENTED_IN Python
   - Insights: "User needs Python code for email validation"

**Turn 2 - Follow-up:**

**User:** "Can you write unit tests for that function?"

1. **Context Assembly:**
   - Episodic: Turn 1 (email validation function discussion)
   - Semantic: Insight about "email validation" (retrieved by similarity)
   - Associative: "Python" entity with WORKING_ON relationship
   - Result: Rich context including the function from Turn 1

2. **Action Generation:** LLM has context of the function from Turn 1 — generates unit tests for that specific function

3. **Learning:**
   - Entities: "unit testing" (Concept), "pytest" (Technology)
   - Relationships: email validation TESTED_BY unit testing
   - Insights: "User follows test-driven development practices"
   - Hebbian: Increment hit_count for "Python" entity (accessed again)

**Turn 3 - Days Later, New Session:**

**User:** "What was that email validation code you helped me with?"

1. **Context Assembly (with priming):**
   - Episodic: None (old session, not loaded by default)
   - **Semantic: Retrieves insight "User needs Python code for email validation"** (embedding similarity)
   - **Associative: "email validation" entity with high hit_count** (primed on session start)
   - Result: Friday **remembers** the prior context

2. **Action Generation:** LLM reconstructs the prior email validation function from memory

3. **Learning:**
   - **Reactivation**: If the old insights had decayed, this access reactivates them
   - Hebbian: Increment hit_count again (reinforces importance)

**This demonstrates the full power of the Memory Loop: genuine learning and recall across time.**

---

## Why the Loop Matters

- **Compound learning effect**: Agents get smarter over time, not just within conversations
- **ROI improvement**: Investment in agent development yields increasing returns as memory builds
- **Observable at every phase**: Instrument context retrieval, LLM calls, tool execution, and memory storage separately
- **Scalable components**: Context assembly can be cached, learning can run async, stores can be distributed
- **Failure isolation**: Issues in one phase don't cascade (extraction failure doesn't block response)
- **Predictable behavior**: Understanding the loop helps debug unexpected responses (check context assembly)
- **Effective training**: Structure conversations to maximize learning (explicit preferences, clear relationships)

---

## Memory Loop Phases Summary

| Phase | What Happens | Performance Target |
|-------|-------------|-------------------|
| **Context Assembly** | Retrieve + score + budget memories | <200ms |
| **Action Generation** | LLM inference + Re-Act tool loop | 1-5s (LLM-dependent) |
| **Learning** | Extract entities, relationships, insights | 1-3s (background) |
