# Friday Agent Framework
## Section 7: Multi-Agent Orchestration - Team Collaboration

**Version:** 1.0
**Framework Version:** v0.1.0
**Last Updated:** 2026-01-24

---

## Overview

The most sophisticated problems require diverse expertise. A research project needs data gathering, analysis, synthesis, and peer review. A software feature requires architecture, implementation, testing, and code review. Complex workflows benefit from specialization—different agents with focused capabilities collaborating toward a shared goal.

Friday's multi-agent orchestration layer enables exactly this: teams of specialized agents working together through a central orchestrator, sharing memory and context, with clear attribution and seamless handoffs. This isn't parallel execution of isolated instances—it's genuine collaboration where agents build on each other's work.

**This section covers:**
- The "Shared Intelligence Plane, Multiple Control Planes" architecture
- Agent orchestrator mechanics (routing, delegation, state management)
- Multi-agent workflows and collaboration patterns

**For Project Leaders:** Multi-agent systems multiply your agents' capabilities by enabling specialization. Rather than one generalist agent struggling with everything, you deploy focused experts that collaborate. This approach scales both horizontally (add more agents) and vertically (improve individual agents). Friday's shared memory model ensures that collaboration overhead is minimal—agents see the same context without expensive data synchronization.

**For IT Leaders:** Multi-agent orchestration introduces coordination complexity that Friday manages through explicit routing, state tracking, and provenance metadata. The orchestrator maintains a single active agent at any time (no concurrent execution in the MVP), simplifying state management and debugging. All agent interactions are logged to the transcript system for complete auditability. The shared memory architecture means scaling multi-agent deployments requires only scaling the memory store, not replicating state across agent instances.

**For Users:** Think of Friday's multi-agent system like a consulting team: you have specialists (researcher, coder, reviewer) who work together. You can ask for help from a specific expert (`@researcher find papers on transformers`), or let the team coordinate internally through delegation. Each agent maintains its personality and toolset, but they all learn from the same experiences and remember the same context.

---

## 7.1 The "Shared Intelligence Plane, Multiple Control Planes" Architecture

### 7.1.1 Shared Memory Model Explained

Friday's multi-agent architecture uses a fundamentally different approach than most frameworks: **all agents share the same memory controller**. When one agent writes to the knowledge graph, vector store, or transcript system, every other agent immediately sees those changes. This "shared intelligence plane, multiple control planes" design treats multiple agents as different personas accessing unified intelligence.

**Architecture Diagram:**

```
┌─────────────────────────────────────────────────────────────────┐
│                     Friday Multi-Agent System                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │   Researcher   │  │     Coder      │  │    Reviewer    │   │
│  │                │  │                │  │                │   │
│  │  - web_search  │  │  - write_file  │  │  - read_file   │   │
│  │  - read_file   │  │  - execute_code│  │  - analyze_code│   │
│  │  - store_fact  │  │  - run_tests   │  │  - check_style │   │
│  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘   │
│           │                   │                   │            │
│           └───────────────────┼───────────────────┘            │
│                               │                                 │
│                               ▼                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │         Shared Memory Controller (Single Instance)     │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │  Episodic Memory   (SQLite Transcripts)               │   │
│  │  - All turns from all agents in one session history   │   │
│  │  - agent_id field tracks which agent responded        │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │  Semantic Memory   (ChromaDB Vectors)                  │   │
│  │  - Insights from all agents in shared collections     │   │
│  │  - Provenance metadata: source_agent="researcher"     │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │  Associative Memory (NetworkX Graph)                   │   │
│  │  - Entity graph built by all agents collectively      │   │
│  │  - Relationships track which agent discovered them    │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**How It Works:**

When the user says: `@researcher find information about Python async patterns`

1. **Orchestrator** receives the message and parses the `@researcher` routing prefix
2. **Researcher agent** is activated (or reused from cache if already instantiated)
3. **Memory retrieval** happens through the shared MemoryController:
   - Vector search pulls insights about "Python" and "async" from semantic memory
   - Graph traversal loads entities like `Entity(name="Python", type=Technology)`
   - Episodic memory provides recent conversation turns (regardless of which agent created them)
4. **Researcher executes** its turn using `web_search` and `read_file` tools
5. **Memory extraction** runs after the turn, adding:
   - New insights about async patterns to the vector store (tagged `source_agent="researcher"`)
   - New relationships to the graph (e.g., `Python --HAS_PATTERN--> AsyncIO`)
   - Turn record to transcripts (with `agent_id="researcher"`)

Later, when the user says: `@coder implement an async function based on what we learned`

1. **Orchestrator** switches to the coder agent (researcher is cached but inactive)
2. **Memory retrieval** happens through the **same** MemoryController:
   - Vector search finds the researcher's insights about async patterns
   - Graph traversal accesses the `Python --HAS_PATTERN--> AsyncIO` relationship
   - Episodic memory includes both researcher and coder turns in conversation history
3. **Coder executes** with full context of what the researcher discovered
4. **Memory extraction** adds the coder's contribution to the shared graph and vector store

**The Result:** The coder doesn't need explicit handoff of data from the researcher. It automatically sees the researcher's findings through normal memory retrieval. This eliminates the "context boundary" problem that plagues isolated-agent architectures.

### 7.1.2 Provenance Tracking for Attribution

With multiple agents writing to shared memory, how do we know **who learned what**? Friday uses **provenance metadata** to track the origin of every memory entry.

**Provenance Data Model:**

```python
class ProvenanceMetadata(BaseModel):
    """
    Tracks the origin and authorship of memory entries.

    Critical for multi-agent scenarios where multiple agents contribute
    to the shared knowledge base. Enables attribution, quality filtering,
    and debugging.
    """
    source: str = Field(
        ...,
        description="Origin type: 'conversation', 'tool', 'inference', 'ingestion'"
    )
    author: str | None = Field(
        default=None,
        description="Which agent created this memory (e.g., 'researcher', 'coder')"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When this memory was created"
    )
    confidence: float = Field(
        default=1.0,
        description="Confidence score (0-1) for extraction quality"
    )

    # Optional context
    session_id: str | None = Field(default=None)
    turn_id: str | None = Field(default=None)
    extraction_model: str | None = Field(
        default=None,
        description="Which LLM model performed extraction"
    )
```

**Provenance in Action:**

Every entity, relationship, and insight stored by Friday includes provenance:

```python
# Entity created by researcher agent
Entity(
    name="FastAPI",
    type=EntityType.TECHNOLOGY,
    description="Modern Python web framework",
    provenance=ProvenanceMetadata(
        source="conversation",
        author="researcher",  # Researcher discovered this
        confidence=0.9,
        session_id="sess_123",
        turn_id="turn_42"
    )
)

# Relationship created by coder agent
Relationship(
    source="FastAPI",
    target="AsyncIO",
    relationship_type="USES",
    context="FastAPI uses asyncio for async request handling",
    provenance=ProvenanceMetadata(
        source="tool",  # From code analysis tool
        author="coder",  # Coder discovered this relationship
        confidence=1.0
    )
)

# Insight created by reviewer agent
Insight(
    content="The async implementation follows best practices with proper exception handling",
    type=InsightType.OBSERVATION,
    provenance=ProvenanceMetadata(
        source="inference",  # From LLM reasoning
        author="reviewer",  # Reviewer's assessment
        confidence=0.85
    )
)
```

**Why Provenance Matters:**

1. **Attribution Clarity**: Know which agent contributed which knowledge
2. **Quality Filtering**: Trust insights from agents with relevant expertise more
3. **Debugging**: Trace back why Friday believes something to the originating agent and turn
4. **Confidence Weighting**: Combine provenance with confidence scores for retrieval ranking
5. **Audit Trails**: Track how knowledge evolved across multiple agents

**Example: Debugging Multi-Agent Confusion**

User reports: "Friday thinks Python is a snake, not a programming language."

```python
# Query graph for "Python" entity
entities = graph_store.get_entities(name="Python")

# Check provenance
for entity in entities:
    print(f"Entity: {entity.name}")
    print(f"  Type: {entity.type}")
    print(f"  Created by: {entity.provenance.author}")
    print(f"  Confidence: {entity.provenance.confidence}")
    print(f"  Turn: {entity.provenance.turn_id}")

# Output might reveal:
# Entity: Python
#   Type: ANIMAL
#   Created by: researcher  (Wrong context from web search)
#   Confidence: 0.6
#   Turn: turn_10

# Entity: Python
#   Type: TECHNOLOGY
#   Created by: coder  (Correct context from code analysis)
#   Confidence: 0.95
#   Turn: turn_15

# Solution: Use confidence and context to prefer the coder's version
```

Provenance enables **agent-specific trust models**: If the coder agent is more reliable for technology entities than the researcher, weight the coder's contributions higher during retrieval.

### 7.1.3 Benefits vs. Isolated-Memory Architectures

**Shared Memory Benefits:**

1. **Zero Handoff Overhead**: Agents automatically see each other's work through normal retrieval
2. **Collective Learning**: All agents benefit from experiences of any agent
3. **Context Coherence**: Conversation history is seamless across agent switches
4. **Resource Efficiency**: Single memory store, not N replicated stores per agent
5. **Simplified State Management**: One source of truth, no state synchronization logic

**Shared Memory Tradeoffs:**

1. **Namespace Collision Risk**: Multiple agents might create conflicting entities (mitigated by provenance and confidence scoring)
2. **Permission Complexity**: Some agents might need read-only access to certain memories (requires access control layer)
3. **Memory Pollution**: A buggy agent can corrupt shared knowledge (mitigated by quality filtering and maintenance operations)

**When to Use Shared vs. Isolated Memory:**

| Scenario | Recommended Approach | Rationale |
|----------|---------------------|-----------|
| Collaborative team (researcher → analyst → reporter) | Shared Memory | Agents build on each other's work; handoff would be expensive |
| Independent specialists (legal bot, medical bot, finance bot) | Isolated Memory with Namespaces | Different domains; knowledge should not cross-pollinate |
| Multi-tenant system (agent per customer) | Isolated Memory per Tenant | Privacy and data isolation requirements |
| Experimental agents (testing new models) | Temporary Isolated Memory | Prevent untrusted agents from corrupting production knowledge |

**Friday's Default:** Shared memory with provenance for attribution and quality filtering. Use memory namespaces (via metadata filtering) when isolation is needed within the same memory store.

**Comparison to Other Frameworks:**

**LangChain / AutoGPT (Isolated Memory):**
```python
# Each agent has its own memory store
researcher_memory = ConversationMemory()
coder_memory = ConversationMemory()

# Explicit handoff required
research_results = researcher.run("Find info")
coder_memory.add_message(f"Research results: {research_results}")  # Manual copy
coder_response = coder.run("Implement this")
```

**Friday (Shared Memory):**
```python
# Both agents use same MemoryController
orchestrator = AgentOrchestrator(registry, memory_controller)

# No explicit handoff needed
await orchestrator.process("@researcher find info")
await orchestrator.process("@coder implement this")
# Coder automatically retrieves researcher's findings through normal memory recall
```

**Key Insight:** Friday's architecture treats multi-agent coordination as a **memory retrieval problem**, not a **data passing problem**. This dramatically simplifies agent collaboration code.

---

## 7.2 Agent Orchestrator

The `AgentOrchestrator` is Friday's central coordinator for multi-agent systems. It manages agent lifecycle, routes messages to appropriate agents, handles delegation between agents, and maintains session state.

### 7.2.1 Explicit Routing with @mentions

Friday supports Twitter/Discord-style `@mention` syntax for explicit agent routing. This provides a natural, human-readable way to direct messages to specific agents.

**Routing Pattern:**

```python
# Pattern: @agent_name followed by space and message
ROUTING_PATTERN = re.compile(r"^@(\w+)\s+(.+)$", re.DOTALL)

# Examples of valid routing:
"@researcher find papers on transformers"
"@coder implement the algorithm we discussed"
"@reviewer check this code for bugs"

# Invalid (no routing):
"What should we do next?"  # Uses active or default agent
"Send email to researcher@example.com"  # @ in middle doesn't trigger routing
```

**Routing Logic Flow:**

```
User Input: "@researcher find information about Python async"
    │
    ▼
┌─────────────────────────────────────────────────┐
│ Step 1: Parse Routing                          │
│                                                 │
│ Match pattern: ^@(\w+)\s+(.+)$                 │
│ Capture groups:                                 │
│   - agent_name = "researcher"                   │
│   - message = "find information about Python async" │
└─────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│ Step 2: Validate Agent Exists                  │
│                                                 │
│ Check registry: registry.exists("researcher")  │
│ If not found → raise OrchestratorError         │
└─────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│ Step 3: Switch to Target Agent                 │
│                                                 │
│ Check cache: Is researcher already loaded?     │
│   - Yes → reuse cached instance                 │
│   - No → create new instance via registry      │
│                                                 │
│ Update active agent reference                   │
└─────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│ Step 4: Process with Target Agent              │
│                                                 │
│ Call: researcher.run("find information...")    │
│   - Memory retrieval (shared MemoryController) │
│   - LLM inference with researcher profile      │
│   - Tool execution (researcher's tools)        │
│   - Memory extraction (tagged author="researcher") │
└─────────────────────────────────────────────────┘
    │
    ▼
Return researcher's response to user
```

**Implementation Example:**

```python
from friday_agent import AgentOrchestrator, AgentRegistry

# Setup
registry = AgentRegistry(loader)
registry.load_all_from_directory()  # Load researcher.yaml, coder.yaml, etc.

orchestrator = AgentOrchestrator(
    registry=registry,
    default_agent="researcher",  # Used when no explicit routing
)

# Initialize with shared memory (happens in agent factory)
orchestrator.registry.set_factory(
    lambda profile: CopilotAgent(
        profile=profile,
        memory=shared_memory_controller,  # Same instance for all agents
        llm=llm_service,
        tools=tool_registry,
    )
)

# Explicit routing examples
response1 = await orchestrator.process("@researcher find info about FastAPI")
# → Routes to researcher agent

response2 = await orchestrator.process("@coder implement a FastAPI endpoint")
# → Routes to coder agent (which sees researcher's findings in memory)

response3 = await orchestrator.process("@reviewer check the endpoint code")
# → Routes to reviewer agent (which sees both researcher and coder's work)
```

**Fallback Routing (No @mention):**

When no explicit routing is provided:

1. **Active Agent**: If an agent is already active, use it
2. **Default Agent**: If no active agent, fall back to configured default
3. **Error**: If no active or default agent, raise `OrchestratorError`

```python
# After routing to @researcher above...
response = await orchestrator.process("Tell me more about async/await")
# No @mention → uses active agent (researcher) from previous turn
```

**Agent Switching Behavior:**

```python
# User explicitly switches
await orchestrator.process("@coder write a hello world function")
# Active agent is now: coder

# Next message continues with coder
await orchestrator.process("Add error handling to that function")
# Still coder (no explicit routing, uses active agent)

# User switches again
await orchestrator.process("@reviewer check the code")
# Active agent is now: reviewer (coder remains cached)
```

**Case-Insensitive Routing:**

Agent names are normalized to lowercase:

```python
"@Researcher find info"  # Works (normalized to "researcher")
"@CODER write code"      # Works (normalized to "coder")
"@ReViEwEr check this"   # Works (normalized to "reviewer")
```

**CLI Integration:**

The routing syntax works naturally in the CLI:

```bash
$ python memory-chat-v2.py

You: @researcher find papers on transformer architectures

Researcher: I found 5 relevant papers on transformer architectures...
[web_search results, stored entities, etc.]

You: @coder implement a simple transformer encoder

Coder: Here's a transformer encoder implementation in PyTorch...
[Generated code, executed tests, stored in memory]

You: @reviewer check if the implementation is correct

Reviewer: The implementation looks good. I verified...
[Code analysis, test results, recommendations]
```

**For Project Leaders:** The @mention syntax provides intuitive control without requiring users to learn complex command structures. It also enables gradual complexity—beginners can explicitly route everything, advanced users can rely on active agent context.

**For IT Leaders:** Explicit routing simplifies request logging and audit trails. Every turn in the transcript includes `agent_id`, enabling precise tracking of which agent handled which request for compliance and debugging.

**For Users:** Think of @mentions like addressing team members in Slack. You say `@researcher` when you need research, `@coder` when you need implementation. Friday handles the switching and context preservation automatically.

### 7.2.2 Task Delegation & Return Patterns

Beyond explicit user routing, agents can **delegate** subtasks to each other programmatically. This enables hierarchical workflows where one agent coordinates specialist agents.

**Delegation API:**

```python
async def delegate(
    self,
    agent_name: str,
    task: str,
    return_to_current: bool = True,
) -> str:
    """
    Delegate a task to another agent.

    Args:
        agent_name: Agent to delegate to
        task: Task description/message for the delegate
        return_to_current: If True, switch back to calling agent after

    Returns:
        Delegated agent's response
    """
```

**Delegation Flow:**

```
┌────────────────────────────────────────────────────────┐
│ Coder Agent (Active)                                   │
│                                                        │
│ User: "Implement async function with best practices"  │
│                                                        │
│ Coder thinks: "I should ask the researcher about      │
│                best practices first"                   │
└────────────────────────────────────────────────────────┘
         │
         │ orchestrator.delegate("researcher",
         │   "What are best practices for Python async?",
         │   return_to_current=True)
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ Researcher Agent (Delegated)                           │
│                                                        │
│ Task: "What are best practices for Python async?"     │
│                                                        │
│ Researcher:                                            │
│   - Searches documentation                             │
│   - Retrieves prior knowledge                          │
│   - Generates response with recommendations            │
│                                                        │
│ Returns: "Best practices include: 1) Use asyncio.run()│
│          2) Avoid blocking calls 3) Use async context  │
│          managers..."                                  │
└────────────────────────────────────────────────────────┘
         │
         │ (return_to_current=True, so switch back)
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ Coder Agent (Restored)                                 │
│                                                        │
│ Coder receives researcher's response                   │
│ Implements function following the recommendations      │
│                                                        │
│ Returns final code to user                             │
└────────────────────────────────────────────────────────┘
```

**Delegation Example (CLI):**

```bash
You: /delegate researcher What are Python async best practices?

[Orchestrator delegates to researcher agent]

Researcher: Best practices for Python async programming include:
1. Use asyncio.run() as the entry point
2. Never use time.sleep() in async functions (use asyncio.sleep())
3. Use async context managers for resource management
4. Handle CancelledError exceptions properly
[... detailed response ...]

[Orchestrator returns to previous agent]

You: Got it, thanks!
```

**Delegation Example (Programmatic):**

```python
# Inside a custom tool or agent logic
class CoordinatorAgent(AgentBase):
    """Meta-agent that coordinates other agents."""

    async def run(self, user_input: str) -> str:
        # Parse user intent
        if "research" in user_input.lower():
            # Delegate to researcher
            findings = await self.orchestrator.delegate(
                "researcher",
                f"Research: {user_input}",
                return_to_current=True,
            )

            # Process findings
            if "implement" in user_input.lower():
                # Delegate to coder
                code = await self.orchestrator.delegate(
                    "coder",
                    f"Implement based on: {findings}",
                    return_to_current=True,
                )

                # Delegate to reviewer
                review = await self.orchestrator.delegate(
                    "reviewer",
                    f"Review this code: {code}",
                    return_to_current=True,
                )

                return f"Complete workflow:\n\nFindings:\n{findings}\n\nCode:\n{code}\n\nReview:\n{review}"

            return findings

        return "I can coordinate research and implementation workflows."
```

**Return Patterns:**

**Pattern 1: Return to Current (Default)**

```python
# Coder is active
await orchestrator.switch_agent("coder")

# Temporarily delegate to researcher
result = await orchestrator.delegate(
    "researcher",
    "Find API documentation",
    return_to_current=True,  # Return to coder after
)

# Coder is active again
assert orchestrator.active_agent_name == "coder"
```

**Pattern 2: Stay on Delegate**

```python
# Start with researcher
await orchestrator.switch_agent("researcher")

# Delegate to coder and stay there
code = await orchestrator.delegate(
    "coder",
    "Implement this algorithm",
    return_to_current=False,  # Stay on coder
)

# Coder is now active
assert orchestrator.active_agent_name == "coder"

# Continue with coder
test_result = await orchestrator.process("Run the tests")
```

**Pattern 3: Chained Delegation**

```python
async def research_and_implement_workflow(task: str):
    """Execute a multi-stage workflow."""

    # Stage 1: Research
    research = await orchestrator.delegate(
        "researcher",
        f"Find information about {task}",
        return_to_current=False,  # Stay on researcher
    )

    # Stage 2: Implementation (from researcher)
    code = await orchestrator.delegate(
        "coder",
        f"Implement {task} based on: {research}",
        return_to_current=False,  # Stay on coder
    )

    # Stage 3: Review (from coder)
    review = await orchestrator.delegate(
        "reviewer",
        f"Review this implementation: {code}",
        return_to_current=False,  # Stay on reviewer
    )

    return {
        "research": research,
        "code": code,
        "review": review,
    }
```

**Delegation vs. Explicit Routing:**

| Aspect | Explicit Routing (@mention) | Delegation (API call) |
|--------|---------------------------|----------------------|
| Initiated by | User | Agent or code |
| Visibility | User sees the switch | Transparent to user |
| Return behavior | Manual (next @mention) | Configurable (return_to_current) |
| Use case | User-driven agent selection | Agent-driven sub-task distribution |

**Memory During Delegation:**

Because Friday uses shared memory, delegation doesn't require explicit context passing:

```python
# Wrong approach (not needed in Friday):
research_context = {"findings": [...], "entities": [...]}
await delegate("coder", task, context=research_context)  # ❌ Unnecessary

# Friday approach (context automatically available):
await orchestrator.delegate("researcher", "Find info")
await orchestrator.delegate("coder", "Implement this")
# Coder automatically retrieves researcher's findings from shared memory ✓
```

**For Project Leaders:** Delegation enables hierarchical agent architectures where a coordinator agent can orchestrate specialist agents. This pattern scales from simple (2-agent workflows) to complex (10+ agent teams with supervisors).

**For IT Leaders:** Delegation calls are logged to transcripts with full provenance, enabling audit trails like "Agent A delegated to Agent B at turn N, which resulted in memory entries X, Y, Z."

**For Users:** You rarely interact with delegation directly—it happens behind the scenes when agents need help from each other. The key benefit is that agents can autonomously consult specialists without requiring you to manually switch agents.

### 7.2.3 Agent State Aggregation: Sequential, Parallel, Hierarchical

As multi-agent systems grow in complexity, different coordination patterns emerge. Friday supports three primary aggregation strategies for combining agent outputs:

**Pattern 1: Sequential (Pipeline)**

Agents execute in order, each consuming the previous agent's output.

```
User Input → Agent A → Agent B → Agent C → Final Output

Example: Research → Analysis → Report
```

**Sequential Implementation:**

```python
async def sequential_pipeline(task: str) -> dict:
    """Execute agents in sequence, passing results forward."""

    # Stage 1: Research
    research_result = await orchestrator.process(
        f"@researcher {task}"
    )

    # Stage 2: Analysis (sees research via memory)
    analysis_result = await orchestrator.process(
        f"@analyst Analyze the research findings we just discussed"
    )

    # Stage 3: Report (sees both via memory)
    report = await orchestrator.process(
        "@reporter Generate a final report based on the analysis"
    )

    return {
        "research": research_result,
        "analysis": analysis_result,
        "report": report,
    }
```

**Sequential with Explicit Handoff:**

```python
async def sequential_with_handoff(topic: str) -> str:
    """Sequential pipeline with explicit data passing (when needed)."""

    # Research phase
    await orchestrator.switch_agent("researcher")
    research = await orchestrator.active_agent.run(
        f"Research {topic} and provide key findings"
    )

    # Analyst phase - explicit handoff if memory retrieval isn't sufficient
    await orchestrator.switch_agent("analyst")
    analysis = await orchestrator.active_agent.run(
        f"Analyze these findings: {research[:500]}..."  # Summary for prompt
        # (Full details retrieved from memory automatically)
    )

    # Reporter phase
    await orchestrator.switch_agent("reporter")
    report = await orchestrator.active_agent.run(
        f"Create executive summary of analysis"
    )

    return report
```

**Use Cases for Sequential:**
- Research → Implementation → Testing → Deployment
- Data Collection → Cleaning → Analysis → Visualization
- Problem Definition → Design → Prototype → Evaluation

**Pattern 2: Parallel (Concurrent)**

Multiple agents execute simultaneously on independent subtasks, then merge results.

```
                    ┌→ Agent A → Result A ┐
User Input → Split ├→ Agent B → Result B ├→ Merge → Final Output
                    └→ Agent C → Result C ┘

Example: Multi-source research (web + docs + code)
```

**Parallel Implementation:**

```python
import asyncio

async def parallel_execution(task: str) -> dict:
    """Execute multiple agents in parallel, then aggregate."""

    # Create parallel tasks
    tasks = [
        orchestrator.delegate("researcher", f"Search web for {task}"),
        orchestrator.delegate("doc_reader", f"Search documentation for {task}"),
        orchestrator.delegate("code_analyzer", f"Find code examples for {task}"),
    ]

    # Execute concurrently
    results = await asyncio.gather(*tasks)

    # Aggregate results
    aggregated = {
        "web_research": results[0],
        "documentation": results[1],
        "code_examples": results[2],
    }

    # Optional: Use a synthesizer agent to merge findings
    synthesis = await orchestrator.delegate(
        "synthesizer",
        f"Combine these findings into a coherent report: {aggregated}"
    )

    return synthesis
```

**Parallel with Independent Namespaces:**

```python
async def parallel_isolated_research(topics: list[str]) -> dict:
    """Research multiple topics in parallel without cross-contamination."""

    async def research_topic(topic: str, agent_id: str):
        # Each agent uses a namespace for isolation
        agent = orchestrator.create_agent_with_namespace(
            "researcher",
            namespace=f"research_{topic.lower()}"
        )
        return await agent.run(f"Research {topic}")

    # Spawn parallel researchers
    tasks = [
        research_topic(topic, f"researcher_{i}")
        for i, topic in enumerate(topics)
    ]

    results = await asyncio.gather(*tasks)

    return dict(zip(topics, results))
```

**Use Cases for Parallel:**
- Multi-source information gathering
- Independent code module development
- Distributed data processing
- A/B testing with different models or approaches

**Pattern 3: Hierarchical (Supervisor-Worker)**

A coordinator agent manages multiple worker agents, delegating subtasks and synthesizing results.

```
                       ┌───────────────┐
                       │  Coordinator  │
                       │    Agent      │
                       └───────┬───────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
    ┌──────────┐        ┌──────────┐       ┌──────────┐
    │ Worker A │        │ Worker B │       │ Worker C │
    └──────────┘        └──────────┘       └──────────┘

Example: Project manager coordinating specialists
```

**Hierarchical Implementation:**

```python
class CoordinatorAgent(AgentBase):
    """
    Meta-agent that breaks down complex tasks and coordinates specialists.
    """

    async def run(self, user_input: str) -> str:
        # Step 1: Analyze task and create execution plan
        plan = await self._create_plan(user_input)

        # Step 2: Execute plan with specialist agents
        results = []
        for subtask in plan["subtasks"]:
            # Determine best agent for subtask
            agent_name = self._select_agent(subtask)

            # Delegate to specialist
            result = await self.orchestrator.delegate(
                agent_name,
                subtask["description"],
                return_to_current=True,
            )

            results.append({
                "subtask": subtask["description"],
                "agent": agent_name,
                "result": result,
            })

        # Step 3: Synthesize results
        final_output = await self._synthesize(user_input, results)

        return final_output

    async def _create_plan(self, task: str) -> dict:
        """Break down task into subtasks."""
        # Use LLM to generate execution plan
        planning_prompt = f"""
        Break down this task into subtasks:
        {task}

        Return a JSON plan with subtasks and recommended agent types.
        """
        # ... LLM call ...
        return plan

    def _select_agent(self, subtask: dict) -> str:
        """Select best agent for a subtask based on capabilities."""
        required_capability = subtask.get("capability")

        # Query registry for agents with capability
        candidates = self.orchestrator.registry.find_by_capability(
            required_capability
        )

        # Return first match (or implement more sophisticated selection)
        return candidates[0].name if candidates else "assistant"

    async def _synthesize(self, original_task: str, results: list) -> str:
        """Combine subtask results into final output."""
        synthesis_prompt = f"""
        Original task: {original_task}

        Subtask results:
        {json.dumps(results, indent=2)}

        Synthesize these results into a coherent final answer.
        """
        # ... LLM call ...
        return final_answer
```

**Hierarchical Example (Practical):**

```python
# User submits complex task
user_task = "Build a web scraper for news articles with sentiment analysis"

# Coordinator breaks it down:
plan = {
    "subtasks": [
        {
            "description": "Research best Python web scraping libraries",
            "agent": "researcher",
            "capability": "research"
        },
        {
            "description": "Implement web scraper using recommended library",
            "agent": "coder",
            "capability": "coding"
        },
        {
            "description": "Research sentiment analysis models",
            "agent": "researcher",
            "capability": "research"
        },
        {
            "description": "Implement sentiment analysis integration",
            "agent": "coder",
            "capability": "coding"
        },
        {
            "description": "Review complete implementation",
            "agent": "reviewer",
            "capability": "code_review"
        },
        {
            "description": "Write tests for scraper and analyzer",
            "agent": "tester",
            "capability": "testing"
        },
    ]
}

# Coordinator executes plan
for subtask in plan["subtasks"]:
    await coordinator.delegate(subtask["agent"], subtask["description"])

# Final synthesis
final_result = await coordinator.synthesize_results()
```

**Use Cases for Hierarchical:**
- Complex project execution (coordinator manages specialists)
- Multi-stage workflows with conditional branching
- Quality assurance (coordinator + reviewers + testers)
- Dynamic task decomposition based on task complexity

**Comparison of Aggregation Patterns:**

| Pattern | Pros | Cons | Best For |
|---------|------|------|----------|
| **Sequential** | Simple, predictable order | Slowest (serial execution) | Linear workflows with dependencies |
| **Parallel** | Fast (concurrent execution) | Requires independent subtasks | Multi-source data gathering |
| **Hierarchical** | Flexible, scales to complexity | Requires coordinator logic | Complex projects, dynamic planning |

**Hybrid Patterns:**

Real systems often combine these patterns:

```python
async def hybrid_workflow(project: str):
    """
    Hierarchical coordinator using parallel execution within stages.
    """
    # Stage 1: Parallel research
    research_tasks = [
        orchestrator.delegate("web_researcher", f"Search web for {project}"),
        orchestrator.delegate("doc_reader", f"Read docs for {project}"),
    ]
    research_results = await asyncio.gather(*research_tasks)

    # Stage 2: Sequential implementation (depends on research)
    design = await orchestrator.delegate(
        "architect",
        f"Design system based on research: {research_results}"
    )

    code = await orchestrator.delegate(
        "coder",
        f"Implement this design: {design}"
    )

    # Stage 3: Parallel validation
    validation_tasks = [
        orchestrator.delegate("reviewer", f"Review code: {code}"),
        orchestrator.delegate("tester", f"Test code: {code}"),
        orchestrator.delegate("security_checker", f"Security scan: {code}"),
    ]
    validation_results = await asyncio.gather(*validation_tasks)

    # Final synthesis
    return {
        "research": research_results,
        "design": design,
        "code": code,
        "validation": validation_results,
    }
```

**For Project Leaders:** Aggregation patterns determine how your agent teams scale. Sequential is simple but slow; parallel is fast but requires independence; hierarchical scales to arbitrary complexity but needs coordinator logic. Most production systems use hybrid approaches.

**For IT Leaders:** Parallel execution requires careful state management—Friday's shared memory model means parallel agents can interfere if not properly namespaced or if they conflict on entity updates. Use distributed locking or transaction-like patterns for critical sections. Transcripts log all parallel executions with timing data for debugging race conditions.

**For Users:** You typically don't see the aggregation pattern—it happens internally. The key indicator is response time: sequential feels like agents taking turns, parallel feels faster for independent tasks, hierarchical feels like a project manager coordinating a team.

---

## 7.3 Multi-Agent Workflows & Patterns

With orchestration mechanics covered, let's explore practical multi-agent collaboration patterns that solve real problems.

### 7.3.1 Research → Analysis → Reporting Pipeline

**Use Case:** Generate comprehensive reports from raw research.

**Agents:**
1. **Researcher**: Gathers information from multiple sources
2. **Analyst**: Processes findings, identifies patterns, draws insights
3. **Reporter**: Synthesizes analysis into polished reports

**Workflow Diagram:**

```
User: "Generate report on AI market trends for 2025"
    │
    ▼
┌─────────────────────────────────────────────────┐
│ Stage 1: Research (Researcher Agent)           │
├─────────────────────────────────────────────────┤
│ Tools: web_search, read_file, scrape_page     │
│                                                 │
│ Executes:                                       │
│ 1. Web search for "AI market trends 2025"     │
│ 2. Scrape industry reports                     │
│ 3. Read competitor analyses                    │
│ 4. Extract key statistics                      │
│                                                 │
│ Memory Writes:                                  │
│ - Entities: Companies, Technologies, Metrics   │
│ - Relationships: Company USES Technology       │
│ - Insights: Market size, Growth rate, etc.    │
└─────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│ Stage 2: Analysis (Analyst Agent)              │
├─────────────────────────────────────────────────┤
│ Tools: recall_memory, analyze_data             │
│                                                 │
│ Retrieves from Memory:                          │
│ - All entities tagged "AI" or "market"        │
│ - Relationships between companies/tech         │
│ - Researcher's insights from Stage 1           │
│                                                 │
│ Analyzes:                                       │
│ 1. Identify top 3 trends                       │
│ 2. Calculate growth rates                      │
│ 3. Compare market segments                     │
│ 4. Forecast future developments                │
│                                                 │
│ Memory Writes:                                  │
│ - Meta-insights: "Cloud AI growing 40% YoY"   │
│ - Relationships: Trend INDICATES Opportunity   │
└─────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│ Stage 3: Reporting (Reporter Agent)            │
├─────────────────────────────────────────────────┤
│ Tools: recall_memory, format_document          │
│                                                 │
│ Retrieves from Memory:                          │
│ - Research findings (Stage 1)                  │
│ - Analysis insights (Stage 2)                  │
│ - Supporting statistics and sources            │
│                                                 │
│ Generates:                                      │
│ 1. Executive summary                           │
│ 2. Detailed findings with sources              │
│ 3. Visual data representations                 │
│ 4. Actionable recommendations                  │
│                                                 │
│ Output: Polished markdown/PDF report           │
└─────────────────────────────────────────────────┘
    │
    ▼
Final Report Delivered to User
```

**Implementation:**

```python
async def research_analysis_report_pipeline(topic: str) -> str:
    """
    Execute a complete research-to-report workflow.

    Args:
        topic: Research topic

    Returns:
        Final formatted report
    """

    # Stage 1: Research
    research_response = await orchestrator.process(
        f"@researcher Conduct comprehensive research on {topic}. "
        f"Find statistics, expert opinions, and industry reports."
    )

    print(f"✓ Research completed: {len(research_response)} chars")

    # Stage 2: Analysis
    # Analyst automatically retrieves researcher's findings from memory
    analysis_response = await orchestrator.process(
        f"@analyst Analyze the research findings on {topic}. "
        f"Identify top trends, calculate key metrics, and draw insights."
    )

    print(f"✓ Analysis completed: {len(analysis_response)} chars")

    # Stage 3: Reporting
    # Reporter retrieves both research and analysis from memory
    report_response = await orchestrator.process(
        f"@reporter Generate an executive report on {topic} "
        f"based on the research and analysis. Include executive summary, "
        f"key findings with sources, and actionable recommendations."
    )

    print(f"✓ Report generated: {len(report_response)} chars")

    return report_response
```

**Advanced: With Quality Gates**

```python
async def research_pipeline_with_gates(topic: str) -> str:
    """Pipeline with human-in-the-loop approval gates."""

    # Stage 1: Research
    research = await orchestrator.process(f"@researcher research {topic}")

    # Gate 1: Review research quality
    print(f"\n--- Research Preview ---\n{research[:500]}...\n")
    approval = input("Approve research? (y/n): ")
    if approval.lower() != 'y':
        print("Research rejected. Please provide feedback:")
        feedback = input("> ")
        # Re-run with feedback
        research = await orchestrator.process(
            f"@researcher Revise research on {topic}. "
            f"Address this feedback: {feedback}"
        )

    # Stage 2: Analysis
    analysis = await orchestrator.process(f"@analyst analyze findings on {topic}")

    # Gate 2: Review analysis
    print(f"\n--- Analysis Preview ---\n{analysis[:500]}...\n")
    approval = input("Approve analysis? (y/n): ")
    if approval.lower() != 'y':
        feedback = input("Feedback: ")
        analysis = await orchestrator.process(
            f"@analyst Revise analysis. Feedback: {feedback}"
        )

    # Stage 3: Report (no gate - final output)
    report = await orchestrator.process(f"@reporter generate report on {topic}")

    return report
```

**Agent Configurations:**

**researcher.yaml:**
```yaml
name: researcher
role: "Research Analyst"
goal: "Find accurate information and synthesize knowledge from multiple sources"

system_prompt: |
  You are a research analyst. Find accurate, relevant information and cite sources.

  Guidelines:
  - Always cite sources with URLs
  - Cross-reference multiple sources
  - Distinguish facts from opinions
  - Note gaps in available information

tools:
  - web_search
  - read_file
  - scrape_page
  - search_documents

capabilities:
  - research
  - information_gathering
  - fact_checking
  - citation

temperature: 0.3  # Lower for factual accuracy
max_tokens: 8192  # Large for comprehensive research
```

**analyst.yaml:**
```yaml
name: analyst
role: "Data Analyst"
goal: "Process information, identify patterns, and derive insights"

system_prompt: |
  You are a data analyst. Process research findings to identify trends and insights.

  Guidelines:
  - Quantify findings when possible
  - Identify cause-and-effect relationships
  - Compare and contrast alternatives
  - Support conclusions with data

tools:
  - recall_memory
  - analyze_data
  - calculate

capabilities:
  - analysis
  - pattern_recognition
  - quantitative_reasoning

temperature: 0.4  # Balanced creativity and accuracy
max_tokens: 4096
```

**reporter.yaml:**
```yaml
name: reporter
role: "Report Writer"
goal: "Synthesize findings into clear, actionable reports"

system_prompt: |
  You are a professional report writer. Create polished reports from analysis.

  Guidelines:
  - Start with executive summary
  - Use clear section structure
  - Support claims with citations
  - End with actionable recommendations

tools:
  - recall_memory
  - format_document
  - generate_visualization

capabilities:
  - writing
  - synthesis
  - communication

temperature: 0.5  # More creative for engaging writing
max_tokens: 6144
```

**Memory Flow Visualization:**

```
After Research:
Graph: [Company: OpenAI] --DEVELOPS--> [Tech: GPT-4]
       [Company: OpenAI] --VALUED_AT--> [Metric: $29B]
Vector: "OpenAI's GPT-4 is leading in LLM market with $29B valuation"
        provenance.author = "researcher"

After Analysis:
Graph: [Trend: LLM Growth] --INDICATES--> [Opportunity: Enterprise AI]
Vector: "LLM market growing 40% YoY, enterprise adoption accelerating"
        provenance.author = "analyst"

After Report:
Vector: "Report conclusion: Enterprises should invest in LLM infrastructure"
        provenance.author = "reporter"
```

**For Project Leaders:** This pipeline demonstrates how multi-agent systems handle complex information workflows. The separation of concerns (research vs. analysis vs. communication) mirrors human organizational structures and scales well—add more researchers for broader coverage, more analysts for deeper insights.

**For IT Leaders:** Each stage is independently testable. You can mock researcher outputs to test analyst logic, or provide canned analysis to test reporter formatting. The transcript system logs every stage with timing and token usage for cost optimization.

**For Users:** This pattern feels like working with a team. The researcher is your thorough colleague who finds everything, the analyst is your data-savvy expert who makes sense of it, and the reporter is your polished communicator who makes it presentable.

### 7.3.2 Peer Review & Validation Patterns

**Use Case:** Improve output quality through automated peer review.

**Agents:**
1. **Creator**: Generates initial work (code, document, design)
2. **Reviewer**: Checks for errors, style, completeness
3. **Reviser**: Implements feedback (may be the same agent as Creator)

**Pattern: Code Review Workflow**

```
User: "Implement a FastAPI endpoint for user authentication"
    │
    ▼
┌─────────────────────────────────────────────────┐
│ Round 1: Implementation (Coder Agent)          │
├─────────────────────────────────────────────────┤
│ @coder implement authentication endpoint        │
│                                                 │
│ Output: Python code with FastAPI endpoint      │
│ Memory: Stores code in graph, file entities    │
└─────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│ Round 2: Review (Reviewer Agent)               │
├─────────────────────────────────────────────────┤
│ @reviewer check the authentication endpoint     │
│                                                 │
│ Reviewer retrieves code from memory             │
│ Checks:                                         │
│ - Security vulnerabilities                      │
│ - Error handling                                │
│ - Code style and documentation                  │
│ - Test coverage                                 │
│                                                 │
│ Output: List of issues and recommendations     │
│ Memory: Stores review feedback as insights     │
└─────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│ Round 3: Revision (Coder Agent)                │
├─────────────────────────────────────────────────┤
│ @coder address the reviewer's feedback          │
│                                                 │
│ Coder retrieves:                                │
│ - Original code from memory                     │
│ - Reviewer feedback from memory                 │
│                                                 │
│ Implements fixes and improvements               │
│                                                 │
│ Output: Updated code addressing issues          │
└─────────────────────────────────────────────────┘
    │
    ▼
Optional: Repeat review cycle or accept
```

**Implementation:**

```python
async def code_review_workflow(
    task: str,
    max_iterations: int = 3
) -> dict:
    """
    Implement with peer review, iterating until approval or max iterations.

    Args:
        task: Implementation task description
        max_iterations: Maximum review cycles

    Returns:
        Dict with final code, review history, and approval status
    """

    iteration = 0
    approved = False
    code = None
    review_history = []

    while iteration < max_iterations and not approved:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")

        # Step 1: Implementation (or revision)
        if iteration == 1:
            prompt = f"@coder {task}"
        else:
            prompt = (
                f"@coder Address the reviewer's feedback from the last review. "
                f"Previous review: {review_history[-1]['feedback'][:200]}..."
            )

        code_response = await orchestrator.process(prompt)
        print(f"✓ Code {'implemented' if iteration == 1 else 'revised'}")

        # Step 2: Review
        review_response = await orchestrator.process(
            f"@reviewer Review the code that was just written. "
            f"Check for security issues, error handling, style, and documentation. "
            f"If code is acceptable, say 'APPROVED'. Otherwise, list specific issues."
        )
        print(f"✓ Review completed")

        # Store review
        review_history.append({
            "iteration": iteration,
            "code_summary": code_response[:200],
            "feedback": review_response,
        })

        # Check for approval
        if "APPROVED" in review_response.upper():
            approved = True
            print(f"✓ Code approved after {iteration} iteration(s)")
        elif iteration == max_iterations:
            print(f"⚠ Max iterations reached without approval")

    return {
        "final_code": code_response,
        "approved": approved,
        "iterations": iteration,
        "review_history": review_history,
    }
```

**Advanced: Multi-Reviewer Consensus**

```python
async def multi_reviewer_consensus(code_task: str) -> dict:
    """
    Code review with multiple reviewers and consensus requirement.
    """

    # Step 1: Implementation
    code = await orchestrator.process(f"@coder {code_task}")

    # Step 2: Parallel reviews from different specialists
    review_tasks = [
        orchestrator.delegate(
            "security_reviewer",
            f"Security review: {code}"
        ),
        orchestrator.delegate(
            "style_reviewer",
            f"Style and documentation review: {code}"
        ),
        orchestrator.delegate(
            "performance_reviewer",
            f"Performance review: {code}"
        ),
    ]

    reviews = await asyncio.gather(*review_tasks)

    # Step 3: Aggregate feedback
    security_review, style_review, perf_review = reviews

    all_approved = all([
        "APPROVED" in security_review.upper(),
        "APPROVED" in style_review.upper(),
        "APPROVED" in perf_review.upper(),
    ])

    if not all_approved:
        # Collect all feedback
        feedback = (
            f"Security: {security_review}\n"
            f"Style: {style_review}\n"
            f"Performance: {perf_review}"
        )

        # Revision
        revised_code = await orchestrator.process(
            f"@coder Address this comprehensive feedback: {feedback}"
        )

        return {
            "code": revised_code,
            "approved": False,
            "reviews": reviews,
        }

    return {
        "code": code,
        "approved": True,
        "reviews": reviews,
    }
```

**Agent Configuration:**

**reviewer.yaml:**
```yaml
name: reviewer
role: "Code Reviewer"
goal: "Identify issues and ensure code quality"

system_prompt: |
  You are an expert code reviewer. Check code for:

  Security:
  - SQL injection, XSS, CSRF vulnerabilities
  - Authentication/authorization flaws
  - Sensitive data exposure

  Quality:
  - Error handling and edge cases
  - Code clarity and maintainability
  - Documentation and comments

  Style:
  - Consistent formatting
  - Naming conventions
  - Code organization

  If code is acceptable, say "APPROVED". Otherwise, list specific issues with line numbers.

tools:
  - read_file
  - recall_memory
  - analyze_code
  - lint_code

capabilities:
  - code_review
  - security_analysis
  - style_checking

temperature: 0.2  # Very low for consistent, strict review
max_tokens: 4096
```

**Pattern: Document Review**

```python
async def document_review_workflow(document_task: str) -> str:
    """Review and improve document through multiple passes."""

    # Draft
    draft = await orchestrator.process(
        f"@writer Create draft: {document_task}"
    )

    # Review for clarity
    clarity_review = await orchestrator.delegate(
        "editor",
        f"Review for clarity and structure: {draft}",
        return_to_current=False
    )

    # Review for accuracy
    fact_check = await orchestrator.delegate(
        "fact_checker",
        f"Fact-check this document and verify claims: {draft}",
        return_to_current=False
    )

    # Final revision
    final_doc = await orchestrator.delegate(
        "writer",
        f"Revise based on feedback:\n"
        f"Clarity: {clarity_review}\n"
        f"Accuracy: {fact_check}",
        return_to_current=False
    )

    return final_doc
```

**For Project Leaders:** Peer review patterns improve output quality at the cost of increased latency and token usage. The ROI depends on your domain—code review might catch security bugs worth thousands of dollars, while document review might prevent embarrassing errors in customer-facing content.

**For IT Leaders:** Automated review scales better than human review for routine checks (style, basic security), but doesn't replace human judgment for complex decisions. Use multi-reviewer consensus for high-stakes outputs (production deployments, customer contracts).

**For Users:** Review patterns happen transparently. You submit a task, Friday implements and self-reviews, and you receive validated output. The iteration count and review feedback are logged for transparency.

### 7.3.3 Specialist vs. Generalist Agent Strategies

**Design Decision:** When should you deploy focused specialist agents vs. broad generalist agents?

**Specialist Strategy:**

**Definition:** Multiple agents with narrow expertise and limited tool access.

**Example Team:**
- `@web_researcher` - Only web search and scraping tools
- `@doc_reader` - Only file reading and document parsing tools
- `@api_caller` - Only HTTP request tools
- `@code_writer` - Only file writing and code execution tools
- `@code_tester` - Only test execution and analysis tools

**Pros:**
- Clearer agent identities (easier for users to understand roles)
- Narrower tool scope reduces confusion for LLM tool selection
- Better cost optimization (use cheaper models for simple specialists)
- Easier to test and debug (narrow scope)
- Can deploy different model sizes per specialist (GPT-4o for complex, Haiku for simple)

**Cons:**
- More coordination overhead (many agents need to communicate)
- Potential for "hot potato" (agents passing tasks around)
- Higher token usage from delegation messages
- More complex orchestration logic

**Implementation:**

```python
# Specialist Team Registry
specialist_registry = AgentRegistry()
specialist_registry.register_from_yaml("web_researcher")  # Tools: web_search, scrape
specialist_registry.register_from_yaml("doc_reader")      # Tools: read_file, parse_pdf
specialist_registry.register_from_yaml("api_caller")      # Tools: http_request
specialist_registry.register_from_yaml("code_writer")     # Tools: write_file, execute_code
specialist_registry.register_from_yaml("code_tester")     # Tools: run_tests, lint_code

# Orchestration with specialists
async def specialist_workflow(task: str):
    """Task requires coordination across specialists."""

    # Research phase
    web_data = await orchestrator.delegate("web_researcher", f"Search web for {task}")
    doc_data = await orchestrator.delegate("doc_reader", f"Read relevant docs for {task}")

    # Implementation phase
    code = await orchestrator.delegate(
        "code_writer",
        f"Implement {task} based on research"
    )

    # Testing phase
    tests = await orchestrator.delegate(
        "code_tester",
        f"Test the implementation"
    )

    return {
        "web_research": web_data,
        "doc_research": doc_data,
        "code": code,
        "test_results": tests,
    }
```

**Generalist Strategy:**

**Definition:** Fewer agents with broad expertise and comprehensive tool access.

**Example Team:**
- `@researcher` - All research tools (web, files, documents, APIs)
- `@developer` - All development tools (read, write, execute, test, lint, git)
- `@analyst` - All analysis tools (data processing, visualization, reporting)

**Pros:**
- Fewer handoffs (each agent handles complete subtasks)
- Lower coordination overhead
- More autonomous agents (less user micromanagement)
- Better context retention within agent (no delegation context loss)

**Cons:**
- Harder for LLM to select correct tool from large toolset
- Risk of "role confusion" (agents doing tasks outside expertise)
- Must use capable models for all agents (can't optimize with cheap models)
- Debugging is harder (agent did many things, which failed?)

**Implementation:**

```python
# Generalist Team Registry
generalist_registry = AgentRegistry()
generalist_registry.register_from_yaml("researcher")   # Tools: 20+ research tools
generalist_registry.register_from_yaml("developer")    # Tools: 30+ development tools
generalist_registry.register_from_yaml("analyst")      # Tools: 15+ analysis tools

# Orchestration with generalists
async def generalist_workflow(task: str):
    """Task handled by fewer agents with broader capabilities."""

    # Research phase (single agent handles all research)
    research = await orchestrator.process(
        f"@researcher Research {task} using web, docs, and APIs"
    )

    # Implementation phase (single agent handles code + tests)
    implementation = await orchestrator.process(
        f"@developer Implement {task} with tests"
    )

    # Analysis phase (single agent handles all analysis)
    analysis = await orchestrator.process(
        f"@analyst Analyze implementation quality and performance"
    )

    return {
        "research": research,
        "implementation": implementation,
        "analysis": analysis,
    }
```

**Hybrid Strategy (Recommended):**

**Definition:** Mix of broad generalists for common tasks and narrow specialists for complex domains.

**Example Team:**
- `@assistant` (Generalist) - General conversation, task routing, coordination
- `@researcher` (Generalist) - All types of research
- `@developer` (Generalist) - Most development tasks
- `@security_auditor` (Specialist) - Security-focused code analysis only
- `@database_expert` (Specialist) - SQL and database optimization only
- `@ml_engineer` (Specialist) - Machine learning model development only

**Rationale:** Use generalists for routine tasks where broad capability is useful, specialists for domains requiring deep expertise or rare tools.

**Implementation:**

```python
# Hybrid Team Registry
hybrid_registry = AgentRegistry()

# Generalists
hybrid_registry.register_from_yaml("assistant")
hybrid_registry.register_from_yaml("researcher")
hybrid_registry.register_from_yaml("developer")

# Specialists
hybrid_registry.register_from_yaml("security_auditor")
hybrid_registry.register_from_yaml("database_expert")
hybrid_registry.register_from_yaml("ml_engineer")

# Orchestration: Generalist handles most work, specialists for expertise
async def hybrid_workflow(task: str):
    """Generalist coordinates, specialists provide expertise."""

    # Generalist researcher handles initial research
    research = await orchestrator.process(f"@researcher research {task}")

    # Generalist developer implements
    code = await orchestrator.process(f"@developer implement {task}")

    # Specialist provides deep security audit
    security_audit = await orchestrator.delegate(
        "security_auditor",
        f"Deep security audit of implementation: {code}",
        return_to_current=True
    )

    # If task involves ML, consult specialist
    if "machine learning" in task.lower():
        ml_advice = await orchestrator.delegate(
            "ml_engineer",
            f"Review ML approach for {task}",
            return_to_current=True
        )

    # Developer revises based on specialist feedback
    final_code = await orchestrator.process(
        f"@developer Address security feedback: {security_audit}"
    )

    return final_code
```

**Decision Framework:**

| Factor | Specialist Strategy | Generalist Strategy | Hybrid Strategy |
|--------|-------------------|-------------------|----------------|
| **Team Size** | 5-20+ agents | 2-5 agents | 3-10 agents |
| **Task Complexity** | Simple, decomposable | Moderate, integrated | Variable |
| **Domain Depth** | Shallow (common tasks) | Moderate | Deep (specialized domains) |
| **Cost Budget** | Can optimize per specialist | Must use capable models | Balanced |
| **User Expertise** | Low (users need guidance) | High (users understand agent roles) | Moderate |
| **Development Velocity** | Slower (more coordination code) | Faster (fewer agents) | Moderate |

**Real-World Example: Software Development Team**

**Specialist Approach:**
```yaml
# 12 specialist agents
- requirements_analyst
- architect
- frontend_developer
- backend_developer
- database_designer
- security_engineer
- performance_engineer
- test_engineer
- documentation_writer
- code_reviewer
- deployment_engineer
- support_engineer
```

**Generalist Approach:**
```yaml
# 3 generalist agents
- engineer (does architecture, coding, testing)
- reviewer (does code review, security, performance)
- ops (does deployment, monitoring, support)
```

**Hybrid Approach:**
```yaml
# 5 agents (3 generalists + 2 specialists)
- engineer (architecture, coding, basic testing)
- reviewer (code review, quality assurance)
- ops (deployment, monitoring)
- security_specialist (deep security audits)
- performance_specialist (deep performance analysis)
```

**For Project Leaders:** Start with a small generalist team (2-3 agents) for MVP. As specific pain points emerge (security issues, performance problems), add specialist agents. Don't over-engineer with 20 specialists before validating the basic workflow.

**For IT Leaders:** Specialist agents enable better cost control (use GPT-4o-mini for simple agents, GPT-4o for complex ones) and clearer security boundaries (restrict filesystem access to specific agents). Generalist agents simplify infrastructure (fewer instances to manage).

**For Users:** Specialist teams require more explicit routing (`@web_researcher` vs. `@doc_reader`), while generalist teams feel more natural (just say `@researcher` for any research). Hybrid teams provide the best UX—use generalists most of the time, explicitly call specialists when needed.

---

## 7.4 Advanced Multi-Agent Patterns

### 7.4.1 Capability-Based Auto-Routing (Future)

**Current State:** Friday MVP requires explicit `@agent_name` routing or manual `switch_agent()` calls.

**Future Enhancement:** Automatic agent selection based on task analysis and capability matching.

**Concept:**

```python
# User doesn't specify agent
user_input = "Find and summarize research papers on transformers"

# Orchestrator analyzes task
task_analysis = await analyze_task(user_input)
# → Detected capabilities: research, summarization
# → Detected keywords: papers, research

# Query registry for agents with matching capabilities
candidates = registry.find_by_capabilities(
    ["research", "summarization"],
    match_all=True
)
# → Returns: [researcher agent]

# Auto-route to best match
response = await orchestrator.process_with_agent(
    candidates[0],
    user_input
)
```

**Registry Capability Indexing:**

```python
# Agents advertise capabilities
researcher_profile = AgentProfile(
    name="researcher",
    capabilities=["research", "information_gathering", "summarization"]
)

coder_profile = AgentProfile(
    name="coder",
    capabilities=["coding", "testing", "debugging"]
)

# Registry indexes capabilities
registry.register(researcher_profile)
registry.register(coder_profile)

# Query by capability
research_agents = registry.find_by_capability("research")
# → [researcher_profile]

coding_agents = registry.find_by_capability("coding")
# → [coder_profile]
```

**Roadmap:** Phase 4 (Q2 2026)

### 7.4.2 Agent Handoff with Context Pruning

**Challenge:** As workflows grow longer, conversation history becomes unwieldy.

**Solution:** Prune context when switching agents, keeping only relevant turns.

```python
async def handoff_with_pruning(
    from_agent: str,
    to_agent: str,
    task: str,
    keep_turns: int = 5
):
    """
    Hand off from one agent to another with context pruning.

    Only the last N turns are kept in episodic memory for the new agent,
    but all entities and insights remain accessible.
    """

    # Get current conversation history
    current_history = memory_controller.get_conversation_history()

    # Prune to last N turns
    pruned_history = current_history[-keep_turns:]

    # Switch agent with pruned context
    orchestrator.switch_agent(to_agent)

    # Override conversation history
    memory_controller.set_conversation_history(pruned_history)

    # Process task (agent sees pruned history but full graph/vector memory)
    response = await orchestrator.active_agent.run(task)

    return response
```

**Roadmap:** Phase 3 (Q1 2026)

### 7.4.3 Agent Pools for Load Balancing

**Challenge:** Single agent instance becomes bottleneck under high load.

**Solution:** Pool of identical agent instances for horizontal scaling.

```python
class AgentPool:
    """Pool of identical agent instances for load balancing."""

    def __init__(self, profile: AgentProfile, pool_size: int = 5):
        self.profile = profile
        self.agents = [
            create_agent(profile)
            for _ in range(pool_size)
        ]
        self.next_index = 0

    async def execute(self, task: str) -> str:
        """Round-robin execution across pool."""
        agent = self.agents[self.next_index]
        self.next_index = (self.next_index + 1) % len(self.agents)

        return await agent.run(task)

# Usage
researcher_pool = AgentPool(researcher_profile, pool_size=5)

# Parallel requests
tasks = [
    researcher_pool.execute("Research topic A"),
    researcher_pool.execute("Research topic B"),
    researcher_pool.execute("Research topic C"),
]

results = await asyncio.gather(*tasks)
```

**Roadmap:** Phase 5 (Q3 2026)

---

## 7.5 Configuration & Deployment

### 7.5.1 Agent Team Configuration Files

**Pattern:** Define multi-agent teams in YAML for easy deployment.

**team.yaml:**
```yaml
name: software_development_team
description: "Complete software development workflow from research to deployment"
version: "1.0.0"

agents:
  - name: researcher
    file: agents/researcher.yaml
    default: true  # Default agent for team

  - name: architect
    file: agents/architect.yaml

  - name: coder
    file: agents/coder.yaml

  - name: reviewer
    file: agents/reviewer.yaml

  - name: tester
    file: agents/tester.yaml

# Shared configuration
shared_memory:
  mode: full  # All agents share full memory
  namespace: "dev_team"  # Isolate from other teams

orchestrator:
  default_agent: researcher
  auto_initialize: true
  delegation_timeout_seconds: 300

workflows:
  - name: feature_development
    file: workflows/feature_development.yaml

  - name: bug_fix
    file: workflows/bug_fix.yaml
```

**Loading Team Configuration:**

```python
from friday_agent import TeamLoader

# Load team configuration
team = TeamLoader.load("teams/software_development_team.yaml")

# Initialize orchestrator with team
orchestrator = team.create_orchestrator(
    memory_controller=memory,
    llm_service=llm,
    tool_registry=tools,
)

# Use team
response = await orchestrator.process("@researcher find info about FastAPI")
```

### 7.5.2 Multi-Agent Observability

**Transcript Logging:**

Every turn includes `agent_id` for attribution:

```python
turn = InteractionTurn(
    id="turn_123",
    session_id="sess_456",
    agent_id="researcher",  # Which agent handled this turn
    user_message="Find information about Python",
    assistant_message="I found several resources...",
    tool_calls=[...],
    timestamp=datetime.now(),
)
```

**Query Transcript by Agent:**

```python
# Get all turns handled by researcher
researcher_turns = transcript_store.get_turns_by_agent(
    session_id="sess_456",
    agent_id="researcher"
)

# Get agent usage statistics
stats = transcript_store.get_agent_stats(session_id="sess_456")
# → {
#     "researcher": {"turns": 5, "tokens": 12000},
#     "coder": {"turns": 3, "tokens": 8000},
#     "reviewer": {"turns": 2, "tokens": 4000},
# }
```

**Grafana Dashboard Metrics:**

```python
# Metrics for monitoring
class MultiAgentMetrics:
    """Prometheus metrics for multi-agent orchestration."""

    agent_turns_total = Counter(
        "friday_agent_turns_total",
        "Total turns per agent",
        ["agent_id", "session_id"]
    )

    agent_tokens_total = Counter(
        "friday_agent_tokens_total",
        "Total tokens per agent",
        ["agent_id", "session_id"]
    )

    delegation_count = Counter(
        "friday_delegation_count",
        "Number of delegations",
        ["from_agent", "to_agent"]
    )

    agent_latency_seconds = Histogram(
        "friday_agent_latency_seconds",
        "Agent response latency",
        ["agent_id"]
    )
```

**OpenTelemetry Tracing:**

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def process_with_tracing(user_input: str):
    """Process with distributed tracing."""

    with tracer.start_as_current_span("orchestrator.process") as span:
        span.set_attribute("user_input", user_input[:100])

        # Parse routing
        agent_name, message = orchestrator._parse_routing(user_input)
        span.set_attribute("target_agent", agent_name or "default")

        # Execute agent
        with tracer.start_span(f"agent.{agent_name}.run") as agent_span:
            agent_span.set_attribute("agent_id", agent_name)
            response = await active_agent.run(message)
            agent_span.set_attribute("response_length", len(response))

        span.set_attribute("status", "success")
        return response
```

---

## 7.6 Best Practices & Pitfalls

### Best Practices

**1. Start Simple, Scale Gradually**
- Begin with 2-3 generalist agents
- Add specialists as specific needs emerge
- Avoid over-engineering with 20 agents before validating workflows

**2. Use Explicit Routing for Clarity**
- Prefer `@agent_name` syntax for transparent agent selection
- Document which agents handle which tasks for users
- Use delegation for agent-driven coordination, not user-driven

**3. Monitor Agent Performance**
- Track token usage per agent (optimize expensive agents)
- Track latency per agent (identify bottlenecks)
- Track success rates per agent (identify quality issues)

**4. Design for Failure**
- Set timeout limits on delegation (prevent infinite waits)
- Implement retry logic for transient failures
- Provide fallback agents when primary agent unavailable

**5. Test Agents in Isolation**
- Unit test each agent with mocked memory and tools
- Integration test agent pairs before full team tests
- Use transcript exports to debug multi-agent interactions

### Common Pitfalls

**1. Agent Confusion with Similar Roles**
- **Problem:** Multiple agents with overlapping capabilities
- **Example:** `@researcher` and `@analyst` both do research, users don't know which to use
- **Solution:** Clear role differentiation or merge into single agent

**2. Delegation Loops**
- **Problem:** Agent A delegates to B, B delegates back to A
- **Example:** Coder asks reviewer for help, reviewer asks coder to implement fix, coder asks reviewer again
- **Solution:** Track delegation chain, prevent cycles, set max depth

**3. Context Loss Across Agents**
- **Problem:** User provides context to one agent, switches to another, new agent doesn't see it
- **Example:** User tells researcher "Focus on Python 3.10+", switches to coder, coder uses Python 2.7
- **Solution:** Store user preferences as explicit entities in graph, retrieved by all agents

**4. Inconsistent Agent Personalities**
- **Problem:** Same agent behaves differently across runs
- **Example:** Researcher is formal in one conversation, casual in another
- **Solution:** Lower temperature for consistency, include personality guidelines in system prompt

**5. Memory Namespace Collisions**
- **Problem:** Multiple agents create conflicting entities
- **Example:** Researcher creates `Entity(name="Python", type=LANGUAGE)`, user creates `Entity(name="Python", type=ANIMAL)`
- **Solution:** Use provenance confidence scores, entity deduplication, or namespace isolation

---

## 7.7 Practical Examples

### Example 1: Complete Software Feature Development

**User Task:** "Build a REST API for user authentication with JWT tokens"

**Execution:**

```bash
You: Build a REST API for user authentication with JWT tokens

# Stage 1: Research (auto-routes to default researcher)
Researcher: I'll research best practices for JWT authentication APIs.
[web_search for JWT best practices]
[read_file on API security documentation]

Key findings:
- Use HTTP-only cookies for token storage
- Implement refresh token rotation
- Set appropriate token expiration (15 min access, 7 day refresh)
[Stores entities: JWT, OAuth2, FastAPI in graph]

# Stage 2: Architecture
You: @architect design the authentication system

Architect: Based on the research findings, here's the architecture:
- FastAPI framework with OAuth2 password flow
- JWT access tokens (15 min expiry)
- Refresh tokens in HTTP-only cookies
- PostgreSQL for user storage
- Password hashing with bcrypt
[Stores design relationships in graph]

# Stage 3: Implementation
You: @coder implement the authentication API

Coder: I'll implement based on the architecture.
[Retrieves architecture from memory]
[write_file for main.py, auth.py, models.py]
[execute_code to test locally]

Implementation complete. Files created:
- main.py (FastAPI app)
- auth.py (authentication logic)
- models.py (user models)
[Stores code files as entities in graph]

# Stage 4: Security Review
You: @reviewer check for security issues

Reviewer: Running security analysis...
[read_file on implementation]
[analyze_code for vulnerabilities]

Found issues:
1. Missing rate limiting on login endpoint (risk: brute force)
2. Token secret should be in environment variable (risk: exposure)
3. Missing CORS configuration (risk: XSS)

Recommendations provided.
[Stores security insights in vector memory]

# Stage 5: Fix Issues
You: @coder fix the security issues

Coder: Addressing security feedback...
[Retrieves reviewer's recommendations from memory]
[Implements fixes]

Fixed:
1. Added rate limiting middleware
2. Moved secret to environment variable
3. Configured CORS properly

# Stage 6: Testing
You: @tester run comprehensive tests

Tester: Running test suite...
[run_tests for unit and integration tests]

Test results:
- 24/24 tests passed
- 100% code coverage
- All security checks passed

# Complete
You: Great! Commit the code

# (Orchestrator delegates to coder for git operations)
Coder: Committing...
[git_add, git_commit with proper message]

Feature complete and committed.
```

**Memory State After Workflow:**

```python
# Graph entities created
Entity(name="FastAPI", type=TECHNOLOGY, provenance.author="researcher")
Entity(name="JWT", type=TECHNOLOGY, provenance.author="researcher")
Entity(name="main.py", type=FILE, provenance.author="coder")
Entity(name="auth.py", type=FILE, provenance.author="coder")

# Relationships
Relationship(source="main.py", target="FastAPI", type="USES", provenance.author="coder")
Relationship(source="auth.py", target="JWT", type="IMPLEMENTS", provenance.author="coder")

# Insights
Insight(
    content="JWT tokens should expire after 15 minutes with refresh rotation",
    type=BEST_PRACTICE,
    provenance.author="researcher"
)
Insight(
    content="Rate limiting required on authentication endpoints to prevent brute force",
    type=SECURITY_REQUIREMENT,
    provenance.author="reviewer"
)
```

### Example 2: Multi-Agent Research Report

**User Task:** "Generate a comprehensive report on AI adoption in healthcare for 2025"

**Execution:**

```python
# Orchestration script
async def generate_healthcare_ai_report():
    """Multi-agent workflow for comprehensive report generation."""

    # Stage 1: Parallel research
    print("Stage 1: Gathering data from multiple sources...")

    research_tasks = [
        orchestrator.delegate(
            "web_researcher",
            "Search for healthcare AI adoption statistics for 2025"
        ),
        orchestrator.delegate(
            "academic_researcher",
            "Find academic papers on AI in healthcare"
        ),
        orchestrator.delegate(
            "market_researcher",
            "Find market analysis reports on healthcare AI"
        ),
    ]

    research_results = await asyncio.gather(*research_tasks)
    print(f"✓ Research complete: {len(research_results)} sources")

    # Stage 2: Analysis
    print("\nStage 2: Analyzing findings...")

    analysis = await orchestrator.delegate(
        "data_analyst",
        "Analyze the healthcare AI research and identify key trends"
    )
    print(f"✓ Analysis complete: {len(analysis)} chars")

    # Stage 3: Synthesis
    print("\nStage 3: Synthesizing report...")

    report = await orchestrator.delegate(
        "technical_writer",
        "Generate executive report on healthcare AI adoption for 2025"
    )
    print(f"✓ Report generated: {len(report)} chars")

    # Stage 4: Review
    print("\nStage 4: Quality review...")

    review_tasks = [
        orchestrator.delegate(
            "fact_checker",
            "Verify all statistics and claims in the report"
        ),
        orchestrator.delegate(
            "editor",
            "Review report for clarity and structure"
        ),
    ]

    reviews = await asyncio.gather(*review_tasks)
    print(f"✓ Reviews complete")

    # Stage 5: Final revision
    print("\nStage 5: Final revision...")

    final_report = await orchestrator.delegate(
        "technical_writer",
        f"Revise report based on feedback:\n"
        f"Fact-check: {reviews[0]}\n"
        f"Editorial: {reviews[1]}"
    )

    print("\n✓ Report complete!")
    return final_report

# Execute
report = await generate_healthcare_ai_report()

# Save report
with open("healthcare_ai_report_2025.md", "w") as f:
    f.write(report)
```

---

## 7.8 Troubleshooting Multi-Agent Issues

### Issue: Agents Not Seeing Each Other's Work

**Symptom:** Coder can't find researcher's findings.

**Diagnosis:**

```python
# Check memory retrieval
from friday_memory import ContextAssembler

assembler = ContextAssembler(memory_controller)
context = await assembler.assemble(
    session_id="sess_123",
    user_id="user_456",
    query="What did the researcher find about FastAPI?"
)

# Check retrieved entities
print(f"Entities: {len(context.loaded_entities)}")
for entity in context.loaded_entities:
    print(f"  - {entity.name} (author: {entity.provenance.author})")

# Check retrieved insights
print(f"Insights: {len(context.retrieved_insights)}")
for insight in context.retrieved_insights:
    print(f"  - {insight.content[:50]}... (author: {insight.provenance.author})")
```

**Common Causes:**

1. **Memory extraction disabled**: Check `extraction_enabled: true` in config
2. **Low relevance scores**: Retrieval threshold too high, researcher's content filtered out
3. **Different namespaces**: Agents using isolated memory namespaces
4. **Extraction failure**: Researcher's turn didn't extract entities successfully

**Solution:**

```python
# Force manual extraction if automatic failed
from friday_memory import MemoryExtractor

extractor = MemoryExtractor(llm_service)
await extractor.extract_from_turn(turn_id="turn_where_researcher_ran")

# Lower retrieval threshold temporarily
memory_controller.config.retrieval_threshold = 0.5  # From 0.7

# Check namespace isolation
assert coder_agent.namespace == researcher_agent.namespace
```

### Issue: Delegation Timeout

**Symptom:** Delegation hangs or times out.

**Diagnosis:**

```python
# Check orchestrator status
status = orchestrator.get_status()
print(f"Active agent: {status['active_agent']}")
print(f"Cached agents: {status['cached_agents']}")

# Check if delegate agent is stuck
import asyncio
try:
    result = await asyncio.wait_for(
        orchestrator.delegate("researcher", "test task"),
        timeout=60.0
    )
except asyncio.TimeoutError:
    print("Delegation timed out!")
    # Force restart agent
    orchestrator.clear_cache()
```

**Common Causes:**

1. **Infinite tool loop**: Agent repeatedly calls tools without reaching conclusion
2. **LLM not responding**: Network issues or API rate limit
3. **Agent waiting for approval**: Workflow has approval gate

**Solution:**

```python
# Add timeout to delegation
async def safe_delegate(agent: str, task: str, timeout: int = 300):
    try:
        return await asyncio.wait_for(
            orchestrator.delegate(agent, task),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        print(f"Delegation to {agent} timed out after {timeout}s")
        # Clear stuck agent
        orchestrator.clear_cache()
        raise
```

### Issue: Agent Personality Drift

**Symptom:** Agent behaves inconsistently across conversations.

**Diagnosis:**

```bash
# Check agent configuration
cat agents/researcher.yaml

# Check temperature setting
grep temperature agents/researcher.yaml
```

**Common Causes:**

1. **High temperature**: Agent creativity too high (>0.5)
2. **Vague system prompt**: Not enough personality guidance
3. **Context pollution**: Agent seeing conflicting examples in memory

**Solution:**

```yaml
# researcher.yaml
name: researcher
temperature: 0.3  # Lower for consistency

system_prompt: |
  You are a research analyst. You are methodical, precise, and formal.

  Personality traits:
  - Always cite sources with URLs
  - Use academic, formal language
  - Present findings in structured format
  - Never speculate without data

  Communication style:
  - Start responses with "Based on my research..."
  - Use bullet points for findings
  - End with "Let me know if you need more details."
```

---

## Summary

Friday's multi-agent orchestration layer transforms isolated agents into collaborative teams. The "shared intelligence plane, multiple control planes" architecture enables genuine collaboration through shared memory, while provenance tracking maintains attribution clarity. Explicit routing with `@mentions` provides intuitive control, and delegation enables hierarchical workflows.

**Key Takeaways:**

1. **Shared Memory Eliminates Handoff Overhead**: Agents automatically see each other's work through normal retrieval
2. **Provenance Enables Attribution**: Track who learned what for debugging and quality filtering
3. **Explicit Routing Scales Better Than Auto-Routing**: @mention syntax is clear and predictable
4. **Delegation Enables Hierarchical Patterns**: Coordinator agents can orchestrate specialists
5. **Start Small, Scale Gradually**: Begin with 2-3 generalist agents, add specialists as needed

**Next Steps:**

- Section 8: Workflows (task graphs, YAML definitions, human-in-the-loop gates)
- Section 9: CLI Reference (complete command documentation)
- Section 10: Configuration Guide (production tuning, deployment patterns)

---

**Document Information:**
- Version: 1.0
- Framework Version: v0.1.0
- Last Updated: 2026-01-24
- Section: 7 of 15
- Word Count: ~10,500 words
