---
title: "Architecture Decisions"
description: "Documented architecture decision records (ADRs) for key design choices."
weight: 2
---

Architecture Decision Records documenting the key design choices in Friday — why uv workspaces, why protocol-first, why Hebbian learning — and the alternatives that were considered.

## What Are ADRs?

An Architecture Decision Record captures an important design decision along with its context, the options considered, the decision made, and the consequences. Friday uses ADRs to maintain **radical transparency** about why the framework is built the way it is.

**ADR template:**

```markdown
# ADR-NNN: [Decision Title]

**Status:** Accepted | Proposed | Deprecated | Superseded by ADR-XXX
**Date:** YYYY-MM-DD

## Context

What problem are we solving? What constraints exist?

## Decision

What are we deciding to do?

## Alternatives Considered

### Option A
Description, pros/cons

### Option B
Description, pros/cons

## Consequences

**Positive:**
- Benefit 1

**Negative:**
- Tradeoff 1

**Risks:**
- Risk 1 (mitigation: ...)
```

---

## ADR-001: Protocol-First Design

**Status:** Accepted — January 2026

**Decision:** All major components (LLM clients, memory stores, tools, telemetry) are defined as abstract protocols in `friday-core/interfaces/` before implementation.

**Rationale:**
- **Swappability** — Zero vendor lock-in. Swap ChromaDB for Pinecone by implementing `VectorStoreAdapter`
- **Testability** — Mock any protocol in unit tests without complex setup
- **Future-proof** — As the AI landscape evolves, Friday adapts through new implementations
- **Clear contracts** — Protocols document exact requirements for implementors

**Alternatives considered:**

*Concrete implementations only* — Faster initial development, but introduces vendor lock-in and makes testing harder.

*Plugin system* — More complex architecture, harder to type-check, unclear discovery mechanism.

*Adapter pattern* — Considered, but `typing.Protocol` is more Pythonic and requires no inheritance.

**Consequences:**
- Complete implementation swappability
- Easy testing with mocks
- Protocols serve as self-documenting contracts
- Slight overhead from abstract method definitions
- More upfront design work

**Reference:** `docs/specs/Friday Framework - Component Specifications - Batch 0.md`

---

## ADR-002: Three-Tier Memory Architecture

**Status:** Accepted — January 2026

**Decision:** Implement three distinct memory types — Episodic (conversation history), Semantic (vector embeddings), Associative (knowledge graph) — rather than a single unified store.

**Rationale:**
- **Cognitive science basis** — Human memory has multiple systems: episodic, semantic, and procedural
- **Optimized retrieval** — Each type has different access patterns (recency vs. similarity vs. relationships)
- **Scalability** — Separate stores can be optimized and scaled independently
- **Rich context** — Graph relationships + semantic similarity > either alone

**Alternatives considered:**

*Vector-only* — Simplest approach, but loses entity relationship structure.

*Graph-only* — Loses semantic similarity search for unstructured content.

*Single unified store* — All data in one database is simpler to operate but makes queries inefficient and mixing semantic + structural data awkward.

**Consequences:**
- Rich, multi-faceted memory context
- Retrieval optimized for each memory type
- Stores scale independently
- More complex architecture with three implementations to maintain
- Requires coordination logic in MemoryController

**Reference:** `docs/specs/Friday Framework - Component Specifications - Batch 1.md`

---

## ADR-003: Shared Memory for Multi-Agent Systems

**Status:** Accepted — January 2026

**Decision:** Multi-agent systems use a single shared `MemoryController` rather than isolated memory per agent.

**Rationale:**
- **Genuine collaboration** — Agents build on each other's work without explicit handoff protocols
- **Reduced overhead** — No context serialization/deserialization between agents
- **Collective learning** — All agents benefit from insights discovered by any agent
- **Provenance tracking** — Metadata records which agent created each memory

**Alternatives considered:**

*Isolated memory per agent* — Allows specialization but eliminates the collaboration benefit.

*Message passing* — Explicit context sharing, high overhead, no persistent shared state.

*Hybrid (shared + private)* — More flexible but significantly more complex to implement and reason about.

**Consequences:**
- Seamless agent collaboration
- Low overhead for context sharing
- Collective intelligence emerges from shared memory
- Requires provenance tracking for attribution
- Potential memory pollution (one agent's noise affects others)

**Mitigation:** Confidence scoring filters low-quality memories; provenance metadata enables agent-specific filtering when needed.

**Reference:** `docs/guides/07-multi-agent.md`

---

## ADR-004: Hebbian Learning via Hit Counts

**Status:** Accepted — January 2026

**Decision:** Implement Hebbian learning ("neurons that fire together wire together") through `hit_count` tracking on graph entities and relationships. Frequently accessed memories strengthen; unused memories decay.

**Rationale:**
- **Mirrors human memory** — Important information is reinforced through repeated use
- **Emergent importance** — No need for explicit importance labeling by users or developers
- **Automatic prioritization** — Context assembly naturally favors high-`hit_count` entities
- **Natural decay** — Unused memories fade, preventing context pollution over time

**Alternatives considered:**

*Manual importance labels* — User or agent explicitly marks importance. Too much overhead; importance should emerge from use.

*Time-based only (recency)* — Recent equals important. Misses the value of repeatedly accessed older information.

*No priority (all memories equal)* — Context pollution, inefficient retrieval, no meaningful ordering.

**Consequences:**
- Automatic importance emerges from usage patterns
- Self-organizing memory that mimics human cognition
- Cold-start problem: new entities begin with `hit_count=0`
- Popularity bias: frequently accessed does not always mean important

**Mitigation:** Promotion scoring uses multiple factors — age, access frequency, confidence, and graph connections — not `hit_count` alone.

**Reference:** `docs/specs/Friday Framework - Component Specifications - Batch 2.md`

---

## ADR-005: Knapsack Optimization for Context Assembly

**Status:** Accepted — January 2026

**Decision:** Use a knapsack optimization algorithm to select the optimal subset of memories within token budget constraints.

**Rationale:**
- **Maximize information density** — Pack the most valuable memories into the limited context window
- **Optimal selection** — Better than naive approaches (top-N recent, top-N similar)
- **Token awareness** — Explicitly accounts for each memory's token cost
- **Multi-factor scoring** — Combines relevance, importance, and recency

**Alternatives considered:**

*Top-N by similarity* — Simple, but ignores memory size and importance weight.

*Top-N by recency* — Fast, but misses relevant older memories with high importance.

*Greedy selection* — Fast, but suboptimal because it does not consider combinations.

**Consequences:**
- Optimal memory selection per token budget
- Maximizes information density in the context window
- Respects token budgets exactly
- Computational overhead: O(n × capacity) dynamic programming
- More complex than naive top-N selection

**Performance:** The knapsack solver completes in under 50ms for typical memory counts (100-1000 candidates).

**Reference:** `packages/friday-optimization/context_knapsack.py`

---

## ADR-006: Tail Injection for Context Placement

**Status:** Accepted — January 2026

**Decision:** Place retrieved memories immediately before the user query (tail injection) rather than at the beginning of the prompt.

**Rationale:**
- **Mitigates "lost in the middle"** — Research shows LLMs pay less attention to content in the middle of long prompts
- **Recency effect** — LLMs attend more strongly to content near the end of the prompt
- **Measured improvement** — 15-20% better recall of injected context

**Alternatives considered:**

*Head injection* — Context at the start (traditional approach). Suffers from attention decay over long prompts.

*Interleaved* — Context mixed with conversation history. Complex to implement and benefits are unclear.

*Duplicated* — Context placed at both ends. Doubles the token cost.

**Consequences:**
- Better LLM attention to injected context
- Improved memory recall in responses
- Research-backed approach
- Unconventional prompt structure may confuse some models

**Reference:** "Lost in the Middle: How Language Models Use Long Contexts" (Liu et al., 2023)

---

## ADR-007: Separate Extraction LLM

**Status:** Accepted — January 2026

**Decision:** Support a configurable separate LLM for entity/relationship extraction that is independent from the main conversation LLM.

**Rationale:**
- **Cost optimization** — Use a cheap model (GPT-4o-mini at $0.15/1M tokens) for extraction while using a premium model for conversation
- **Capability matching** — Some models excel at structured extraction while others excel at conversation
- **Reliability** — Extraction failures do not block conversation responses
- **90% cost savings** — Extraction accounts for 30-50% of total LLM calls

**Alternatives considered:**

*Same model for both* — Simpler configuration, but expensive when the main model is premium.

*Always use the cheap model* — Cost-effective but degrades conversation quality.

*Rule-based extraction* — No LLM cost for extraction, but fails on nuanced or ambiguous language.

**Consequences:**
- Significant cost reduction (60-90% in typical usage)
- Extraction is optimized independently of conversation
- Extraction failures are isolated from the main conversation loop
- Additional configuration complexity
- Two LLM connections to manage

**Reference:** [LLM Providers configuration](/docs/configuration/llm/) — extraction model settings

---

## Finding and Creating ADRs

**Where ADRs live:**

1. **Inline in specs** — `docs/specs/` contain ADRs embedded in batch specifications
2. **Guide sections** — Major ADRs are summarized in relevant guide sections
3. **Code comments** — Implementations reference ADRs: `# Ref: ADR-003 - Shared Memory`
4. **Dedicated directory** — `docs/adrs/` (planned for v0.2.0)

**Searching for ADRs:**

```bash
# Search for ADR references in specs
grep -r "ADR-" docs/specs/

# Find architecture decisions in guides
grep -r "Decision:" docs/guides/

# Find code implementing a specific ADR
grep -r "ADR-004" packages/
```

**When to write an ADR:**
- Changing major component interfaces
- Adding a new architectural layer
- Selecting between multiple viable design approaches
- Making decisions that are difficult or costly to reverse

**When NOT to write an ADR:**
- Implementation details (which algorithm variant to use)
- Bug fixes
- Documentation improvements
- Refactoring without behavior change

**Proposing a new ADR:**
1. Copy the ADR template above
2. Fill in context, decision, alternatives, and consequences
3. Open a GitHub issue with the draft ADR for community feedback
4. Incorporate feedback and mark as "Accepted" once the decision is made
5. Add `# Ref: ADR-NNN` comments to the implementation code

## Related Pages

- [Development Setup](/docs/contributing/setup/) — Contribution workflow and coding standards
- [Roadmap](/docs/contributing/roadmap/) — Planned features and milestones
- [Protocol Specifications](/docs/api/protocols/) — The concrete interfaces shaped by these decisions
