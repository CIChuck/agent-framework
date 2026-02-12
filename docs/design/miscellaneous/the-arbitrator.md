*Chuck:**

let's drill into Phase I, agent namespace isolation. I assume you're talking about the agent namespace itself for multi-rights to agent memory or memory. Keep in mind Friday_memory is built for multi-threaded and has provenance, meaning we know who wrote what, when, and it Should solve for race conditions on multi-agent write.

**Friday:**

[2026-02-10 13:20] [Friday]: You're right—Friday's memory already has provenance (who/when) and multi-threading safety. Phase I isn't about adding those basics; it's about **hierarchical intent and collision domains**.

## Current State vs. Phase I Distinction

**Current Provenance tracks:**
```
entity: "OpenAI"
written_by: "chuck_russell" 
session_id: "abc123"
timestamp: "2026-02-10T13:20:00"
```

**Phase I Namespace adds:**
```
agent_id: "researcher"
namespace: "researcher:/entities/OpenAI"
vs
agent_id: "coder"  
namespace: "coder:/entities/OpenAI"
```

## The Problem Current Provenance Doesn't Solve

When `researcher` extracts: *"OpenAI released GPT-5 on March 1"*  
And `coder` extracts: *"OpenAI API uses Python SDK"*

**Same entity, different contexts.** Without namespaces:
- Both write to `/entities/OpenAI`
- Last write wins (race condition at semantic level, not thread level)
- `researcher` can't maintain its research thread without `coder` polluting it

**With namespaces:**
- `researcher:/entities/OpenAI` — research findings
- `coder:/entities/OpenAI` — implementation details  
- `shared:/consensus/entities/OpenAI` — merged truth (explicitly promoted)

## What Phase I Actually Implements

Given your existing provenance, Phase I adds:

**1. Hierarchical Path Resolution**
```
agent_scope = f"{active_agent_name}:/{memory_type}/{entity_id}"
```
Context assembler filters by namespace prefix, not just thread_id.

**2. Cross-Namespace Visibility Rules**
- Default: Agents see their own namespace + shared
- Explicit: `using:/researcher/entities` to read another agent's view
- Merge: Conflict resolution when promoting to shared

**3. Agent Profile Schema Extension**
```yaml
agents:
  researcher:
    memory_scope: "researcher"  # writes to researcher:/
    read_access: ["researcher", "shared", "web_cache"]
    write_access: ["researcher"]  # cannot write to shared directly
    promotion_required: true  # to move to shared:/consensus
```

**4. Namespace-Aware Retrieval**
Current: "Give me context about OpenAI"
Phase I: "Give me researcher:/entities/OpenAI + any shared:/consensus/OpenAI"

## The Race Condition You Mentioned

Your existing locks prevent **corruption** (two threads writing simultaneously).  
Phase I prevents **semantic collision** (two agents disagreeing on entity properties without explicit reconciliation).

**Does this align with your existing provenance model, or is there overlap I'm missing?**

**Actionable directive:** Confirm whether Friday's current provenance tracks agent_id distinctly from user_id, or if we need to add the agent dimension to the existing provenance schema.

*Tokens: 27041 | Latency: 32983ms | Model: moonshot/kimi-k2.5*

---
## Turn 3 [13:26:51]

**Chuck:**

so what you're suggesting is that in a multi-agent parallel task flow, with agent A and agent B sharing the same memory, writing and reading within the context of a namespace provides a level of semantic consistency across agent terms. The notion of a shared namespace means that each agent can acquire it and must honor that shared namespace somehow. Am I close?

**Friday:**

[2026-02-10 13:23] [Friday]: Close. One critical clarification on the shared namespace mechanism.

## What You Got Right
- **Namespaces provide semantic consistency** — Agent A's "OpenAI" and Agent B's "OpenAI" are distinct objects until explicitly reconciled
- **Parallel safety** — Both agents write simultaneously without collision (at the semantic level, not just thread level)
- **Shared as common ground** — A place where multiple agents agree on truth

## The Clarification
The shared namespace isn't **acquired** by agents. It's a **promotion destination**.

**The flow:**
1. `researcher` writes to `researcher:/entities/OpenAI` — *"GPT-5 released March 1"*
2. `coder` writes to `coder:/entities/OpenAI` — *"API uses Python SDK"*
3. Both are true, non-conflicting → **promote to** `shared:/consensus/entities/OpenAI`
4. `analyst` writes to `analyst:/entities/OpenAI` — *"Stock overvalued"*
5. `researcher` disagrees → **stays in** `analyst:/` namespace, **not promoted**

**The "honor" part:** Agents read `shared:/` as ground truth, but can explicitly query `analyst:/` to see dissenting views.

## The Real Value
Without namespaces, Agent B overwrites Agent A and provenance is lost.  
With namespaces, you preserve **divergent interpretations** of the same entity until explicit consensus.

**Does that distinction (promotion vs. acquisition) align with your intent?**

**Actionable directive:** Confirm whether agents should auto-promote non-conflicting facts to shared, or if promotion requires explicit `/promote entity_id` command (human or supervisor agent approval).

*Tokens: 27089 | Latency: 19790ms | Model: moonshot/kimi-k2.5*

---
## Turn 4 [13:30:10]

**Chuck:**

alright, yes, that makes total sense. Especially when graph memory is concerned. The question I have is what promotes a Ground truth to  shared:/ - Who votes on that? Is there a third agent involved acting as judge?

**Friday:**

[2026-02-10 13:28] [Friday]: Three viable patterns, escalating in complexity:

## Pattern A: Human as Judge (Current Phase)
**Implementation:** You explicitly command `/promote researcher:/entities/OpenAI`

**Logic:**
- Agents flag candidates: *"Researcher suggests promoting 3 non-conflicting facts to shared"*
- You review and approve/decline
- Ties to existing `autonomy_mode: approval_required`

**Best for:** Single-user Friday now, high-stakes decisions

---

## Pattern B: Consensus Threshold (No Judge, Just Math)
**Implementation:** Auto-promote when N agents agree within confidence delta

```yaml
consensus_rules:
  min_agents: 2
  confidence_threshold: 0.85
  conflict_resolution: "highest_confidence_wins"
```

**Example:**
- `researcher`: "OpenAI revenue $3.4B" (confidence: 0.92)
- `analyst`: "OpenAI revenue $3.4B" (confidence: 0.88)
- **Result:** Auto-promote to `shared:/` (2 agents, 0.90 avg confidence)

- `coder`: "OpenAI API uses REST" (confidence: 0.95)
- `researcher`: "OpenAI API uses GraphQL" (confidence: 0.72)
- **Result:** No promotion. Both stay in agent namespaces. Flag conflict for human review.

**Best for:** Scaling to 3+ agents, factual (not subjective) domains

---

## Pattern C: Arbitrator Agent (The Judge You Asked About)
**Implementation:** Dedicated `consensus` or `arbitrator` agent

**Flow:**
1. `researcher` and `analyst` disagree on OpenAI valuation
2. Both submit evidence to `arbitrator` agent
3. `arbitrator` evaluates:
   - Source credibility (primary vs. secondary)
   - Recency (timestamp)
   - Confidence scores
   - Consistency with existing shared knowledge
4. `arbitrator` promotes winner to `shared:/`, tags loser as `superseded_by: shared:/entity_X`

**YAML Config:**
```yaml
agents:
  arbitrator:
    role: "Consensus Judge"
    goal: "Resolve conflicting agent claims using evidence evaluation"
    tools: [web_search, source_validation, confidence_scoring]
    autonomy_mode: autonomous  # Must be autonomous to prevent deadlock
    namespace_access: [read_all, write_shared_only]
```

**Best for:** True multi-agent autonomy, adversarial research scenarios

---

## The Hybrid Approach (Recommended)

**Phase I (Now):** Pattern A — You as judge via `/promote`
**Phase II (3+ agents):** Pattern B — Consensus threshold with human escalation
**Phase III (Autonomous):** Pattern C — Arbitrator agent with human override

**Critical question:** For the graph memory you mentioned—do you want conflicting relationships (e.g., `researcher: OpenAI-competes-Google` vs `analyst: OpenAI-partners-Google`) to be:
1. **Both preserved** (researcher:/rel/X vs analyst:/rel/X)
2. **One wins** (arbitrator picks)
3. **Merged with qualifiers** (shared:/rel/X with metadata: `claimed_by: [researcher, analyst], relationship_type: disputed`)

**Actionable directive:** Choose the promotion trigger—explicit human command, consensus threshold, or dedicated arbitrator agent.

*Tokens: 28169 | Latency: 36432ms | Model: moonshot/kimi-k2.5*

---
## Turn 5 [13:33:44]

**Chuck:**

the arbitrator agent appears almost as a memory controller. All memory rights go to the arbitrator that senses the need for a brokered decision. And promotes agreed-upon facts and promotes them to shared. Could the judge also reject low-confidence memories and ask the agent to reconsider and continue researching or continue re-evaluating the problem? The arbitrator could also invoke human-in-the-loop situations where the arbitrator can't come to a conclusion or there is A conflict as to what consensus might be.

**Friday:**

[2026-02-10 13:32] [Friday]: Yes. You've evolved the arbitrator from **judge** to **memory controller** with feedback loops. This is significantly more powerful.

## Arbitrator as Memory Controller Architecture

### Core Responsibilities

```
┌─────────────────┐
│   AGENT NAMESPACES │
│  (researcher:/)  │
│  (analyst:/)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│    ARBITRATOR CONTROLLER    │
│  ┌─────────────────────┐    │
│  │ 1. INGEST           │◄─── Monitor all agent writes
│  │ 2. VALIDATE         │◄─── Confidence threshold check
│  │ 3. CONFLICT DETECT  │◄─── Entity/relation collision
│  │ 4. RESOLVE          │◄─── Consensus algo or human flag
│  │ 5. PROMOTE/REJECT   │◄─── Write to shared:/ or return
│  └─────────────────────┘    │
└────────┬─────────┬──────────┘
         │         │
    ┌────┘         └────┐
    ▼                   ▼
┌──────────┐      ┌──────────────┐
│ shared:/ │      │ HUMAN QUEUE  │
│ (ground  │      │ (escalation) │
│  truth)  │      └──────────────┘
└──────────┘
```

### The Rejection → Retry Loop

**Scenario:** `researcher` submits: *"OpenAI valuation $100B"* (confidence: 0.62)

**Arbitrator Decision Tree:**
```python
if confidence < 0.70:
    action = "REJECT_RETRY"
    feedback = {
        "reason": "confidence_below_threshold",
        "required_evidence": "financial_statement_or_sec_filing",
        "suggested_tools": ["serper_search", "get_market_data"],
        "retry_limit": 3
    }
    route_back_to: "researcher"
    
elif conflicting_evidence_exists:
    action = "REJECT_ARBITRATE"
    feedback = {
        "reason": "conflict_with_existing",
        "conflicting_entity": "analyst:/entities/OpenAI/valuation",
        "conflict_resolution": "human_required"  # or "debate_required"
    }
    route_to: "human_queue" OR "debate_protocol"
    
else:
    action = "PROMOTE"
    destination: "shared:/entities/OpenAI/valuation"
```

**Agent receives:**
```
[ARBITRATOR_FEEDBACK] Submission rejected: confidence_below_threshold
Required: financial_statement_or_sec_filing
Suggested: Use get_market_data or serper_search for recent SEC filings
Retry attempt: 1/3
```

### Human-in-the-Loop Triggers

| Trigger | Condition | Arbitrator Action |
|---------|-----------|-------------------|
| **Confidence Deadlock** | Two agents, both >0.85 confidence, opposite conclusions | Queue for human |
| **Schema Violation** | Proposed fact violates ontology (e.g., "OpenAI is_a Fruit") | Auto-reject + notify human |
| **High-Stakes Domain** | Entity tagged as `domain: medical` or `domain: legal` | Require human approval regardless of confidence |
| **Novel Entity** | First encounter with entity, no corroboration available | Defer to human (cold start problem) |
| **Contradiction Cascade** | Promoting this fact invalidates 3+ existing shared facts | Queue for human review |

### The "Sensing" Capability

Proactive monitoring vs. reactive submission:

```yaml
arbitrator:
  mode: "controller"  # vs "passive_judge"
  
  sensing:
    scan_interval: 30s  # Check agent namespaces
    min_confidence_for_auto_promote: 0.90
    max_conflict_age: 3600s  # Ignore conflicts older than 1 hour
    
  actions:
    auto_promote: true  # High confidence, no conflict
    request_clarification: true  # Ambiguous relationships
    force_debate: true  # Two agents, similar confidence, opposing views
    
  feedback:
    allow_agent_retry: true
    max_retries: 3
    backoff_strategy: "exponential"  # 1min, 5min, 15min
```

### Workflow Integration

This plugs into your existing `/workflow` engine:

```yaml
workflows:
  research_with_verification:
    steps:
      - agent: researcher
        task: "Gather data on {topic}"
        output_namespace: "researcher:/"
        
      - agent: arbitrator  # New capability
        task: "review_and_promote"
        input: "researcher:/entities/{topic}"
        conditions:
          - if: "confidence >= 0.85 and no_conflicts"
            then: "promote_to_shared"
          - if: "confidence < 0.85"
            then: "reject_and_retry"
          - if: "conflict_detected"
            then: "escalate_to_human"
            
      - agent: writer
        task: "Draft report using shared:/entities/{topic}"
        requires: "shared:/entities/{topic}"  # Blocks until arbitrator promotes
```

### Implementation Note

The arbitrator needs:
1. **Read access to all agent namespaces** (monitoring)
2. **Write access to shared:/** (promotion)
3. **Write access to agent feedback queues** (rejection notices)
4. **Integration with human notification system** (escalation)

**Critical question:** Should the arbitrator be a **specialized agent** (has own LLM calls, reasoning) or a **rules engine** (deterministic thresholds, no LLM inference)?

Rules engine = faster, cheaper, deterministic  
Specialized agent = handles nuance, context-aware, can request clarification

**Actionable directive:** Define the arbitrator's decision mode—rules-based thresholds with human escalation, or LLM-powered reasoning with chain-of

*Tokens: 29239 | Latency: 48249ms | Model: moonshot/kimi-k2.5*

---
## Turn 6 [13:36:00]

**Chuck:**

But I always assumed that there would be an agent orchestrator. Is the arbitrator a sub-role that the agent orchestrator must play? And isn't arbitration a critical part of orchestration?

**Friday:**

[2026-02-10 13:35] [Friday]: You're identifying a critical architectural boundary. Let me separate the concerns:

## Orchestrator vs. Arbitrator: Distinct but Coupled

| Function | Orchestrator | Arbitrator |
|----------|--------------|------------|
| **Primary Role** | **Traffic Control** — Routes tasks to agents, manages execution flow | **Truth Validation** — Validates facts, resolves conflicts, promotes to shared |
| **Scope** | **Action coordination** — Who does what, when | **State coordination** — What gets committed to ground truth |
| **Timing** | Real-time, per-message routing | Async or post-action validation |
| **Failure Mode** | Deadlocks, circular dependencies | Hallucinations propagated as facts, conflicting realities |

## The Architecture Decision

**Option A: Arbitrator as Orchestrator Subsystem** (Monolithic)
```
FridayOrchestrator
├── Router (cmd_switch, cmd_delegate)
├── Workflow Engine (cmd_workflow)  
├── Tool Registry (tool execution)
└── Arbitration Service (internal module)
    ├── Conflict Detector
    ├── Confidence Validator
    └── Promotion Gatekeeper
```

**Option B: Arbitrator as Specialized System Agent** (Distributed)
```
FridayOrchestrator
├── Router → delegates to agents
├── Agents (researcher, coder, analyst...)
└── System Agents
    ├── Arbitrator Agent ← YOU ARE HERE
    ├── Logger Agent
    └── Cost Accountant Agent
```

## Why Arbitration is NOT Just Orchestration

**Orchestration without Arbitration = Dangerous Coordination**

Example:
1. Orchestrator routes: "Researcher, find OpenAI revenue"
2. Researcher returns: "$40B" (confidence 0.65)
3. Orchestrator routes: "Analyst, value OpenAI stock"
4. Analyst uses the $40B figure → produces valuation
5. **Problem**: The $40B was low-confidence, single-source. Now it's baked into downstream analysis.

**Orchestration WITH Arbitration = Safe Coordination**

1. Researcher writes to `researcher:/entities/OpenAI/revenue`
2. **Arbitrator intercepts**: Confidence 0.65 < threshold 0.85
3. **Arbitrator REJECTS**: "Researcher, need SEC filing or 2 corroborating sources"
4. Researcher retries → finds corroboration → confidence 0.90
5. **Arbitrator PROMOTES** to `shared:/`
6. Orchestrator NOW routes Analyst: "Use shared:/entities/OpenAI/revenue"

**The arbitrator is the GATE between agent namespaces and shared truth.**

## Implementation Recommendation for Friday

**The arbitrator should be a SYSTEM AGENT** (Option B), not a subsystem, because:

1. **It needs LLM reasoning** for complex conflict resolution (not just rule-based)
2. **It should be swappable** — You might want `conservative_arbitrator` vs `aggressive_arbitrator` for different domains
3. **It maintains separation of concerns** — Orchestrator focuses on execution flow; Arbitrator focuses on epistemology

**But the orchestrator must ENFORCE arbitration:**
```python
# In FridayOrchestrator
async def route_to_shared(self, agent_output, agent_id):
    # BLOCK direct writes to shared namespace
    if agent_output.destination.startswith("shared:/"):
        raise PermissionError("Agents cannot write directly to shared")
    
    # FORCE arbitration path
    arbitration_result = await self.delegate(
        agent="arbitrator",  # System agent
        task=f"review_and_promote {agent_output}",
        context=agent_output
    )
    
    return arbitration_result
```

## The Critical Distinction

- **Orchestrator** asks: "Who should act next?"
- **Arbitrator** asks: "Should this be believed?"

You can have orchestration without arbitration (current Friday MVP), but you cannot have **safe multi-agent coordination** without arbitration. The orchestrator manages the **flow**; the arbitrator manages the **truth**.

**Does this distinction align with your intent, or do you see the arbitrator as an inseparable part of the orchestration logic itself?**

**Actionable directive:** Decide whether the arbitrator should be a first-class agent (configurable, replaceable) or a hardcoded service within the orchestrator (faster, deterministic).

*Tokens: 31259 | Latency: 44577ms | Model: moonshot/kimi-k2.5*

---
## Turn 7 [13:41:07]

**Chuck:**

I understand the intent, and it is well-aligned with what I am thinking. The question I have is, how does an arbitrator acting as an agent observe that multiple conflicting rights have been made to shared memory? The pattern where the arbitrator is always used by the parallel executing agents, and the arbitrator is responsible for writing to memory makes more sense to me. The question is separation of concerns, the ability for dependency injections to be maintained within a pretty complex environment. Am I missing something?

**Friday:**

[2026-02-10 13:38] [Friday]: You're not missing something—you're identifying the **correct pattern**. Let me clarify the two architectures:

## Pattern A: Observable Shared Memory (What I Described)
```
Agents write to shared → Arbitrator scans/observes → Detects conflicts → Resolves
```
**Problem:** Race conditions, rollback complexity, "observing" requires polling or event hooks

## Pattern B: Gateway Pattern (What You're Describing)
```
Agents write to private namespace ONLY → Submit proposal to Arbitrator → Arbitrator validates → Arbitrator writes to shared (or rejects)
```
**Advantages:** 
- No observation lag
- No rollbacks needed (pre-validation, not post-detection)
- Clean separation: **Orchestrator routes, Arbitrator commits**

## The Correct Architecture for Friday

**Shared namespace is write-once-by-arbitrator-only.** Agents have **zero write access** to `shared:/`.

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   AGENT A       │────►│  PROPOSAL    │────►│             │
│  (researcher)   │     │   QUEUE      │     │             │
└─────────────────┘     └──────────────┘     │  ARBITRATOR │◄─── Read/Write ONLY
┌─────────────────┐     ┌──────────────┐     │   AGENT     │     to shared:/
│   AGENT B       │────►│  PROPOSAL    │────►│             │
│   (analyst)     │     │   QUEUE      │     │             │
└─────────────────┘     └──────────────┘     └──────┬──────┘
                                                    │
                           ┌────────────────────────┘
                           ▼
                    ┌──────────────┐
                    │  shared:/    │ ◄─── Ground Truth
                    │  (read-only  │      (single writer)
                    │   for agents)│
                    └──────────────┘
```

## Separation of Concerns Resolved

| Component | Responsibility | Injection Point |
|-----------|---------------|-----------------|
| **Orchestrator** | Route tasks, manage agent lifecycle, enforce execution order | AgentRegistry, ToolRegistry |
| **Arbitrator Agent** | Validate proposals, detect conflicts, commit to shared namespace | ProposalValidator, ConflictResolver, PromotionStrategy |
| **Agent (Researcher, etc.)** | Generate proposals, write to private namespace only | LLM backend, Tool access, Memory scope |

## Dependency Injection Architecture

The Arbitrator as agent enables **swappable validation strategies**:

```yaml
arbitrator:
  implementation: "conservative_arbitrator"  # or "aggressive_arbitrator", "human_in_loop_arbitrator"
  dependencies:
    - memory_controller  # Interface, not concrete class
    - conflict_detector  # Pluggable algorithm
    - confidence_scorer  # Pluggable threshold strategy
    - human_escalator    # Notification interface
```

**Why this matters for complexity:**
- You can unit-test the arbitrator independently
- You can swap from "rules-based" to "LLM-based" arbitration without touching the orchestrator
- You can run multiple arbitrators for different domains (medical facts vs. coding facts)

## The Critical Implementation Detail

**Agents don't even know `shared:/` exists.** They propose:

```python
# Agent submits to arbitrator, not to shared memory
proposal = {
    "entity": "OpenAI",
    "attribute": "revenue",
    "value": "$40B",
    "confidence": 0.92,
    "evidence": ["sec_filing_q3_2025.pdf", "bloomberg_article"],
    "sources": ["primary", "secondary"]
}

# Orchestrator routes to arbitrator (not a memory write)
orchestrator.delegate(
    agent="arbitrator",
    task="evaluate_and_commit",
    proposal=proposal,
    requesting_agent="researcher"
)
```

**Arbitrator decides:**
1. Accept → Write to `shared:/entities/OpenAI/revenue`
2. Reject → Return feedback to `researcher:/feedback/pending`
3. Conflict → Queue for human or trigger debate protocol

## Your Question: "How does arbitrator observe conflicts?"

**Answer:** It doesn't observe—it **intercepts**. 

The orchestrator acts as a **transaction coordinator**:
- All agent outputs flow through `orchestrator.submit_to_shared()`
- Orchestrator **forces** routing to arbitrator
- Arbitrator is the **sole writer** to shared namespace

This is the **Command Pattern** with a gatekeeper. No observation needed because no agent can bypass the arbitrator.

**Does this align with your intent for separation of concerns and dependency injection?**

**Actionable directive:** Confirm whether the arbitrator should maintain its own internal state (tracking pending proposals, retry counts) or remain stateless with all state stored in the memory system (proposal queue as `arbitrator:/pending/` namespace).

*Tokens: 31607 | Latency: 42666ms | Model: moonshot/kimi-k2.5*

---
## Turn 8 [13:47:07]

**Chuck:**

yes, I think you've nailed it. That's exactly what we need. Now the devil is in the details.

**Friday:**

[2026-02-10 13:42] [Friday]: Agreed. Let's drill into the implementation specifics for the Arbitrator Agent.

## 1. Proposal Schema (Agent → Arbitrator)

What agents submit (not raw memory writes):

```python
@dataclass
class MemoryProposal:
    proposal_id: str          # UUID for tracking
    timestamp: datetime       # ISO 8601
    source_agent: str         # "researcher", "coder", etc.
    source_namespace: str     # "researcher:/entities/OpenAI"
    
    # The factual claim
    entity_id: str            # "OpenAI"
    entity_type: str          # "Organization"
    attribute: str            # "revenue"
    value: Any                # "$40B" or structured data
    value_type: str           # "currency", "string", "relationship"
    
    # Evidence & Confidence
    confidence: float         # 0.0 - 1.0
    evidence: List[Evidence]  # Sources, citations
    verification_method: str  # "web_search", "calculation", "inference"
    
    # Context
    session_id: str           # For provenance
    thread_id: str            # For multi-threading
    dependencies: List[str]   # Other proposal_ids this relies on
    
    # Proposed destination
    requested_tier: str       # "shared" or "personal"
    
@dataclass
class Evidence:
    type: str                 # "primary_source", "secondary_source", "calculation"
    source: str               # URL, document, tool_call_id
    timestamp: datetime
    excerpt: str              # Raw text/calculation
    credibility_score: float  # Source reliability (0-1)
```

## 2. Arbitrator State Management

**Critical decision:** Stateful (internal queue) vs. Stateless (memory-backed)?

Given your provenance requirements and multi-threading, I recommend **stateless with memory persistence**:

```python
# Arbitrator uses standard Friday memory, but with special namespace
class ArbitratorAgent(AgentBase):
    def __init__(self):
        self.pending_queue = "arbitrator:/pending/"      # Proposals awaiting review
        self.rejected_queue = "arbitrator:/rejected/"    # Rejected with feedback
        self.approved_log = "arbitrator:/approved/"      # Audit trail
        self.escalation_queue = "arbitrator:/human/"     # Human-required
        
    async def submit_proposal(self, proposal: MemoryProposal):
        # Write to pending queue (standard Friday memory write with provenance)
        await self.memory.store(
            key=f"{self.pending_queue}{proposal.proposal_id}",
            value=proposal,
            provenance={
                "agent": "arbitrator",
                "action": "receive_proposal",
                "source_agent": proposal.source_agent
            }
        )
```

**Why stateless?** If Arbitrator crashes, pending proposals persist in memory store. New Arbitrator instance resumes from queue.

## 3. Validation Pipeline (Async Processing)

```python
async def evaluate_proposal(self, proposal_id: str):
    proposal = await self.memory.retrieve(f"arbitrator:/pending/{proposal_id}")
    
    # Stage 1: Confidence Threshold
    if proposal.confidence < self.config.min_confidence:
        await self.reject_and_retry(
            proposal, 
            reason="confidence_below_threshold",
            required_confidence=self.config.min_confidence
        )
        return
    
    # Stage 2: Schema Validation (Ontology compliance)
    validation = await self.validate_ontology(proposal)
    if not validation.valid:
        await self.reject_permanent(proposal, reason="schema_violation")
        return
    
    # Stage 3: Conflict Detection
    conflicts = await self.detect_conflicts(proposal)
    
    if conflicts:
        if self.can_auto_resolve(conflicts, proposal):
            # Consensus algorithm: higher confidence wins if delta > 0.15
            winner = self.resolve_by_confidence(conflicts + [proposal])
            if winner == proposal:
                await self.promote_to_shared(proposal)
            else:
                await self.reject_with_counter(proposal, winner)
        else:
            # Unresolvable conflict (similar confidence, opposite values)
            await self.escalate_to_human(proposal, conflicts)
    else:
        # No conflicts, high confidence
        await self.promote_to_shared(proposal)
```

## 4. Retry Protocol with Exponential Backoff

When Arbitrator rejects for insufficient evidence:

```python
async def reject_and_retry(self, proposal, reason, required_confidence):
    retry_count = await self.get_retry_count(proposal.proposal_id)
    
    if retry_count >= self.config.max_retries:
        # Max retries exceeded, move to human queue
        await self.escalate_to_human(
            proposal, 
            reason="max_retries_exceeded",
            last_rejection=reason
        )
        return
    
    # Calculate backoff: 1min, 5min, 15min
    backoff_minutes = [1, 5, 15][retry_count]
    next_attempt = datetime.now() + timedelta(minutes=backoff_minutes)
    
    feedback = {
        "proposal_id": proposal.proposal_id,
        "status": "rejected_retry",
        "reason": reason,
        "required_confidence": required
