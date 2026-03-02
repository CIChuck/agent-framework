---
title: "Lifecycle & State"
description: "Session initialization, Re-Act loop iteration, and turn archiving."
weight: 3
---

Every agent session moves through a defined lifecycle: context initialization, iterative Re-Act loop execution up to the configured maximum, and turn archiving to memory.

## Agent Lifecycle Stages

```
1. CONFIGURATION
   └─ Load YAML from filesystem

2. VALIDATION
   └─ Schema validation, type checking

3. REGISTRATION
   └─ Add to AgentRegistry with metadata

4. INSTANTIATION (on-demand)
   └─ Create agent instance with dependencies

5. SESSION INITIALIZATION
   └─ Initialize memory session, set author

6. EXECUTION
   └─ Process user queries

7. SHUTDOWN
   └─ Cleanup resources, save state
```

## Agent Initialization & Loading

**Step 1: Configuration Loading**

```python
from pathlib import Path
from friday_agent import AgentLoader

# Initialize loader
loader = AgentLoader(agents_dir=Path("agents/"))

# Load single agent
researcher_profile = loader.load("researcher")
# Reads agents/researcher.yaml, validates, returns AgentProfile

# Load all agents in directory
all_profiles = loader.load_all()
# Returns: {"researcher": AgentProfile, "coder": AgentProfile, ...}

# List available agents without loading
available = loader.list_available()
# Returns: ["researcher", "coder", "reviewer"]
```

**AgentLoader Features:**

1. **Caching**: Loaded profiles cached in memory
   ```python
   profile1 = loader.load("researcher")  # Loads from file
   profile2 = loader.load("researcher")  # Returns cached
   assert profile1 is profile2
   ```

2. **Hot Reload**: Force reload for development
   ```python
   loader.reload("researcher")  # Bypass cache, reload from file
   loader.reload_all()          # Reload all profiles
   ```

3. **Validation**: Comprehensive error checking
   ```python
   try:
       loader.load("invalid_agent")
   except AgentConfigError as e:
       print(e.path)    # Path to invalid file
       print(e)         # Detailed error message
   ```

**Step 2: Validation**

The `AgentLoader` validates all required fields, type correctness, and enum values before returning the profile. Invalid configurations raise `AgentConfigError` with clear messages.

**Step 3: Registration**

Profiles are registered in the `AgentRegistry`:

```python
from friday_agent import AgentRegistry

registry = AgentRegistry(loader)
registry.load_all_from_directory()  # Load researcher.yaml, coder.yaml, etc.

# Query the registry
names = registry.list_names()           # ["researcher", "coder", "reviewer"]
profile = registry.get_profile("coder") # Returns AgentProfile
exists = registry.exists("researcher")  # True
```

**Step 4: Instantiation (On-Demand)**

Agents are lazily instantiated when first needed:

```python
# Agent factory pattern
registry.set_factory(
    lambda profile: CopilotAgent(
        profile=profile,
        memory=shared_memory_controller,
        llm=llm_service,
        tools=tool_registry,
    )
)

# First call to get agent creates instance
agent = registry.get_agent("researcher")  # Creates new CopilotAgent
agent2 = registry.get_agent("researcher") # Returns cached instance
```

**Agent Caching Strategy:**

Once instantiated, agents are cached until:
1. Memory is cleared (`/reset` command)
2. Agent profile is reloaded (`loader.reload()`)
3. Registry is cleared
4. Process restarts

Caching avoids re-initialization overhead (memory session setup, tool registry loading) on every request.

---

## Session Initialization

When an agent is first activated, it initializes a memory session:

```python
# From packages/friday-agent/src/friday_agent/base.py
class AgentBase:
    async def initialize_session(
        self,
        session_id: str,
        user_id: str,
    ) -> None:
        """
        Initialize agent for a new conversation session.

        This sets up:
        - Memory session with author attribution
        - Episodic memory for this session
        - Context assembly state
        """
        self._session_id = session_id
        self._user_id = user_id

        # Initialize memory with agent identity for provenance
        await self.memory.initialize_session(
            session_id=session_id,
            user_id=user_id,
            author=self.profile.name,  # Tag memory entries with agent name
        )

        # Prime context (load top entities, recent insights)
        if self.profile.memory_config.get("priming_enabled", True):
            await self.context_engine.prime_context(
                state=self.session_state,
                n_entities=self.profile.memory_config.get("priming_depth", 10),
            )
```

**Session Identity:**

Each session has a unique ID that threads through all memory operations:
- All transcript turns are tagged with `session_id`
- Episodic memory loads only turns from current and configured prior sessions
- Memory extraction attributes new entries to the active session

---

## The Re-Act Execution Loop

The Re-Act (Reasoning and Acting) loop is the core execution mechanism for `CopilotAgent`. Each user message triggers one complete loop.

**Detailed Loop Flow:**

```
User Input: "Analyze the performance of main.py"
         │
         ▼
┌─────────────────────────────────────────────────┐
│ 1. Context Assembly                             │
│    - Query: "Analyze performance of main.py"   │
│    - Load episodic memory (recent turns)        │
│    - Vector search: similar insights            │
│    - Graph retrieval: related entities          │
│    - Assemble prompt with token budget          │
└─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│ 2. LLM Call (Iteration 1)                       │
│    - Messages: system + history + context +     │
│      user query                                 │
│    - Tools: file_read, code_analyze, ...        │
│    - Response: tool_call(file_read,             │
│                path="main.py")                  │
└─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│ 3. Tool Execution                               │
│    - Execute: file_read(path="main.py")         │
│    - Result: [file contents]                    │
│    - Append tool result to messages             │
└─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│ 4. LLM Call (Iteration 2)                       │
│    - Messages: + tool result                    │
│    - Response: tool_call(code_analyze,          │
│                code=[contents])                 │
└─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│ 5. Tool Execution                               │
│    - Execute: code_analyze(code=[contents])     │
│    - Result: [analysis report]                  │
│    - Append tool result to messages             │
└─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│ 6. LLM Call (Iteration 3)                       │
│    - Messages: + analysis result                │
│    - Response: FINAL TEXT (no tool calls)       │
│    - Break loop                                 │
└─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│ 7. Turn Archiving                               │
│    - Archive turn to episodic memory            │
│    - Extract entities/insights (async)          │
│    - Return final response to user              │
└─────────────────────────────────────────────────┘
```

**Iteration Limit:**

The loop has a hard cap of `MAX_ITERATIONS = 10`. If the LLM continues calling tools after 10 iterations:

```python
# From packages/friday-agent/src/friday_agent/copilot.py
while iteration < self.MAX_ITERATIONS:
    iteration += 1
    response = await self.llm.chat_completion(...)

    if response.has_tool_calls:
        # Execute tools and continue
        ...
        continue
    else:
        # Final response, exit loop
        break

if iteration >= self.MAX_ITERATIONS:
    raise RuntimeError("Agent exceeded maximum iterations")
```

This prevents runaway loops from consuming excessive API tokens.

**Tool Error Handling:**

When a tool fails, the error is returned to the LLM as a tool result (not re-raised):

```python
try:
    result = await self.tool_registry.execute(
        tool_name=tool_call.name,
        **tool_call.arguments,
    )
except Exception as e:
    # Error becomes a tool result, not a crash
    result = ToolResult(
        content=f"Tool error: {e}",
        error=str(e),
    )

# LLM sees the error and can retry with different arguments
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": result.content,
})
```

This resilient error handling means agents can recover from tool failures without crashing.

---

## Turn Archiving

After every complete Re-Act loop, the full turn is archived to persistent storage:

```python
async def _archive_turn(
    self,
    user_message: str,
    assistant_message: str,
    tool_calls: list[ToolCall],
    tool_results: list[ToolResult],
) -> None:
    """
    Archive a complete conversation turn to persistent storage.

    Records:
    - User message
    - Assistant final response
    - All intermediate tool calls and results
    - Timing and token usage metadata
    """
    turn = Turn(
        session_id=self._session_id,
        user_id=self._user_id,
        agent_id=self.profile.name,
        user_message=user_message,
        assistant_message=assistant_message,
        tool_calls=tool_calls,
        tool_results=tool_results,
        timestamp=datetime.now(timezone.utc),
        model=self.llm.model,
        tokens_used=self._last_token_count,
        latency_ms=self._last_latency,
    )

    await self.memory.archive_turn(turn)
```

**What Gets Archived:**

| Field | Description |
|-------|-------------|
| `session_id` | Unique session identifier |
| `agent_id` | Which agent produced this turn |
| `user_message` | The original user input |
| `assistant_message` | The final LLM response |
| `tool_calls` | All tool invocations (name, arguments) |
| `tool_results` | All tool outputs (content, data, errors) |
| `timestamp` | When the turn occurred |
| `model` | Which LLM model was used |
| `tokens_used` | Token consumption for the turn |
| `latency_ms` | Total turn processing time |

**Memory Extraction (Async):**

After archiving, memory extraction runs asynchronously without blocking the response:

```python
# Fire-and-forget extraction (doesn't delay response)
asyncio.create_task(
    self.memory.extract_and_store(
        turn=turn,
        extraction_model=self.extraction_llm,
    )
)

# Return response immediately
return assistant_message
```

Extraction includes:
- **Entity extraction**: People, projects, technologies mentioned
- **Relationship extraction**: How entities relate to each other
- **Insight extraction**: User preferences, decisions, observations
- **Summary generation**: Paragraph summarizing the turn

---

## Agent State Management

**Session State Model:**

```python
class SessionState(BaseModel):
    """Runtime state for an active agent session."""

    session_id: str
    user_id: str
    agent_id: str

    # Conversation tracking
    turn_count: int = 0
    total_tokens: int = 0
    total_latency_ms: int = 0

    # Context cache
    last_payload: ContextPayload | None = None
    last_debug_info: DebugInfo | None = None

    # Tool state
    active_tools: list[str] = Field(default_factory=list)
    injected_tools: list[str] = Field(default_factory=list)

    # Scoped variables (for tool state passing)
    scoped_vars: dict[str, Any] = Field(default_factory=dict)
```

**State Persistence:**

Session state is in-memory for the duration of the process. On process restart:
1. A new `SessionState` is created with a fresh session ID
2. Transcript history is loaded from SQLite for the new session's episodic window
3. Vector/graph memories are retrieved through normal context assembly

**Scoped Variables:**

Tools can store state within a session using scoped variables:

```python
# Tool stores context for later use
async def execute(self, **kwargs) -> str:
    result = await fetch_data()
    self.session_state.scoped_vars["last_fetch"] = result
    return result.content

# Another tool reads the context
async def execute(self, **kwargs) -> str:
    prior = self.session_state.scoped_vars.get("last_fetch")
    if prior:
        return analyze(prior)
```

Scoped variables are session-scoped (cleared on `/clear`) but not turn-scoped.

---

## Shutdown & Cleanup

When a session ends (via `/exit` command or process termination):

```python
async def shutdown(self) -> None:
    """
    Clean shutdown of agent session.

    Performs:
    - Final memory lifecycle operations (if configured)
    - Resource cleanup (connections, file handles)
    - Session state serialization
    """
    # Run lifecycle operations if configured
    if self.config.get("on_exit_lifecycle", False):
        await self.memory.run_lifecycle_operations()

    # Archive any pending turns
    await self.memory.flush_pending_archives()

    # Release resources
    await self.llm.close()
    await self.tool_registry.cleanup()

    logger.info(
        f"Agent session ended: {self._session_id}, "
        f"turns={self._turn_count}, "
        f"entities={await self.memory.count_entities()}"
    )
```

**Safe Exit:**

The framework guarantees safe exit at any time:
- All turns are archived atomically (SQLite transactions)
- Memory extraction is idempotent (safe to re-run on restart)
- Incomplete extractions resume on next session start
- Emergency termination (Ctrl+C) may skip cleanup but won't corrupt data

---

## Related Pages

- [Agent Types](/docs/agents/types/) — CopilotAgent, AutonomousAgent, and specialized roles
- [Agent Configuration](/docs/agents/configuration/) — YAML schemas and AgentProfile fields
- [Memory Architecture](/docs/memory/) — How turns are stored and retrieved
