---
title: "Orchestrator Patterns"
description: "Design patterns for building orchestrators that delegate to specialist agents."
weight: 2
---

An orchestrator agent decomposes high-level tasks and delegates subtasks to specialist agents, then synthesizes their results into a coherent final response.

The `AgentOrchestrator` is Friday's central coordinator for multi-agent systems. It manages agent lifecycle, routes messages to appropriate agents, handles delegation between agents, and maintains session state.

## Explicit Routing with @mentions

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
You: @researcher find papers on transformer architectures

Researcher: I found 5 relevant papers on transformer architectures...

You: @coder implement a simple transformer encoder

Coder: Here's a transformer encoder implementation in PyTorch...

You: @reviewer check if the implementation is correct

Reviewer: The implementation looks good. I verified...
```

---

## Task Delegation & Return Patterns

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

**Programmatic Delegation Example:**

```python
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

# Temporarily delegate to researcher, then return to coder
result = await orchestrator.delegate(
    "researcher",
    "What are best practices?",
    return_to_current=True,
)
# Active agent is still: coder
```

**Pattern 2: Permanent Switch**

```python
# Permanently switch to researcher after delegation
result = await orchestrator.delegate(
    "researcher",
    "Find information on topic",
    return_to_current=False,
)
# Active agent is now: researcher
```

**Pattern 3: Chain Delegation**

```python
# Chain multiple agents in sequence
research = await orchestrator.delegate("researcher", "Find papers on X", return_to_current=False)
code = await orchestrator.delegate("coder", f"Implement based on: {research}", return_to_current=False)
review = await orchestrator.delegate("reviewer", f"Review: {code}", return_to_current=False)
```

---

## Agent Registry

The `AgentRegistry` maintains the catalog of available agents and manages their lifecycle.

**Registry Setup:**

```python
from friday_agent import AgentRegistry, AgentLoader

# Initialize with loader
loader = AgentLoader(agents_dir=Path("agents/"))
registry = AgentRegistry(loader)

# Load all agents from directory
registry.load_all_from_directory()

# Or load selectively
registry.load("researcher")
registry.load("coder")
registry.load("reviewer")
```

**Registry Operations:**

```python
# Query available agents
names = registry.list_names()           # ["researcher", "coder", "reviewer"]
profiles = registry.list_profiles()     # [AgentProfile, ...]
exists = registry.exists("researcher")  # True

# Get agent instance (creates if not cached)
agent = registry.get_agent("researcher")

# Get profile without instantiating
profile = registry.get_profile("coder")

# Find agents by capability
research_agents = registry.find_by_capability("research")
# Returns agents with "research" in their capabilities list
```

**Capability-Based Routing:**

Agents declare capabilities in their YAML profile:

```yaml
capabilities:
  - research
  - information_gathering
  - fact_checking
```

The orchestrator uses capabilities for smart routing:

```python
# Route based on task requirements
if task_requires("code_review"):
    agent = registry.find_by_capability("code_review")[0]
elif task_requires("research"):
    agent = registry.find_by_capability("research")[0]
```

---

## Orchestrator State Management

The orchestrator tracks active agent state for routing continuity:

```python
class AgentOrchestrator:
    """Central coordinator for multi-agent systems."""

    def __init__(
        self,
        registry: AgentRegistry,
        default_agent: str | None = None,
    ):
        self._registry = registry
        self._default_agent = default_agent
        self._active_agent: str | None = None
        self._agent_cache: dict[str, AgentBase] = {}

    async def process(self, message: str) -> str:
        """
        Process a message, routing to the appropriate agent.

        Parses @mentions for explicit routing, falls back to
        active agent, then default agent.
        """
        # Parse routing
        match = ROUTING_PATTERN.match(message)
        if match:
            agent_name = match.group(1).lower()
            message = match.group(2)
        elif self._active_agent:
            agent_name = self._active_agent
        elif self._default_agent:
            agent_name = self._default_agent
        else:
            raise OrchestratorError("No active or default agent configured")

        # Get or create agent
        agent = await self._get_or_create_agent(agent_name)
        self._active_agent = agent_name

        # Process message
        return await agent.run(message)
```

---

## Related Pages

- [Shared Memory Architecture](/docs/multi-agent/architecture/) — How agents share memory and provenance
- [Collaboration Patterns](/docs/multi-agent/patterns/) — Fan-out, pipeline, consensus, and critic-revisor
- [Workflow Engine](/docs/workflows/engine/) — Workflow-level multi-agent orchestration
