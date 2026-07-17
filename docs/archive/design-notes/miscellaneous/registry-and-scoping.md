# Design: Agent Registry & Memory Scoping

**Status:** Exploratory
**Context:** Supporting multi-agent orchestration with discovery and data isolation.

## 1. Agent Registry

The `AgentRegistry` serves as the "Yellow Pages" for the Orchestrator. It allows the system to look up agents not just by name, but by **capability**.

### 1.1 Data Model
We extend `AgentProfile` (or wrap it) to include metadata useful for routing and resource allocation.

```python
class AgentMetadata(BaseModel):
    profile: AgentProfile
    # Capability tags for semantic routing
    tags: list[str]  # e.g., ["coding", "python", "filesystem"]
    # Memory Configuration
    private_memory_mode: str = "full"  # "full", "episodic_only", "vector_only"
    # Performance metrics (optional, for future use)
    avg_latency_ms: float = 0.0
```

### 1.2 Registry Interface
Located in `packages/friday-agent/src/friday_agent/registry.py`.

```python
class AgentRegistry:
    def __init__(self):
        self._agents: dict[str, AgentMetadata] = {}

    def register(self, profile: AgentProfile, tags: list[str] = None, memory_mode: str = "full"):
        """Register an agent profile with capabilities and memory config."""
        
    def get_by_name(self, name: str) -> AgentMetadata | None:
        """Direct lookup."""

    def find_by_capability(self, query: str) -> list[AgentMetadata]:
        """
        Semantic or tag-based lookup.
        Example: "Find agent that can write files" -> Returns CoderAgent
        """
        # MVP: Simple tag matching
        # Future: Embedding-based similarity search
```

## 2. Memory Scoping (Shared vs. Private)

Agents in a swarm often need two types of memory:
1.  **Shared Memory (The Hive Mind):** Access to the central project context, guidelines, and completed facts.
2.  **Private Memory (The Scratchpad):** Intermediate work, internal monologues, or "draft" knowledge.

### 2.1 Implementation Strategy

We will leverage the **Dependency Injection** pattern in `FridayContainer` combined with the **Null Object Pattern** for lightweight configurations.

#### The "Dual-Memory" Agent
We update `CopilotAgent` (or a subclass `TeamAgent`) to accept two memory controllers:

```python
class TeamAgent(CopilotAgent):
    def __init__(self, ..., shared_memory: MemoryController, private_memory: MemoryController):
        self.shared = shared_memory
        self.private = private_memory
    
    # By default, reads use BOTH, writes go to PRIVATE?
    # Or strict separation: specific tools for specific memories.
```

#### Container Factory Logic
The `FridayContainer` becomes the factory that manages these scopes and modes.

```python
class FridayContainer:
    def get_team_agent(self, name: str, memory_mode: str = "full") -> TeamAgent:
        # 1. Get singleton Shared Memory
        shared = self.memory 
        
        # 2. Create/Get Private Memory
        # Uses a namespaced Chroma collection: f"friday_memory_{name}"
        # AND injects NullAdapters if memory_mode is "episodic_only"
        private = self._create_namespaced_memory(
            namespace=name, 
            mode=memory_mode
        )
        
        return TeamAgent(..., shared_memory=shared, private_memory=private)

    def _create_namespaced_memory(self, namespace: str, mode: str) -> MemoryController:
        if mode == "episodic_only":
            # Use Null Adapters for Vector/Graph to save resources
            vector = NullVectorStore()
            graph = NullGraphStore()
        else:
            # Create real adapters pointing to namespaced collections
            vector = ChromaVectorStore(collection_name=f"friday_{namespace}")
            graph = ElementXGraphStore()
            
        return MemoryController(vector_store=vector, graph_store=graph, ...)
```

### 2.2 Orchestrator Integration
The `AgentOrchestrator` uses the Registry to find the right profile and `memory_mode`, then asks the Container to instantiate the Agent with the correct memory wiring.

## 3. Workflow Example

1.  **User:** "Research React patterns and write a demo."
2.  **Orchestrator:** Queries Registry. Found: `Researcher`, `Coder`.
3.  **Orchestrator:**
    *   Instantiates `Researcher` (Shared Mem + Private Mem).
    *   Delegates: "Research React patterns."
4.  **Researcher:**
    *   Searches web.
    *   Stores raw notes in **Private Memory** (don't pollute shared graph yet).
    *   Summarizes key findings into **Shared Memory**.
5.  **Orchestrator:**
    *   Instantiates `Coder`.
    *   Delegates: "Write demo using findings in Shared Memory."
6.  **Coder:**
    *   Reads Shared Memory (sees Researcher's summary).
    *   Writes code.

## 4. Next Steps

1.  Implement `AgentRegistry` in `friday-agent`.
2.  Update `FridayContainer` to support `_create_namespaced_memory`.
3.  Prototype `TeamAgent` with dual memory controllers.
