# Design: Friday Agent Orchestration

**Status:** Exploratory
**Context:** Enabling multi-agent workflows (teams/swarms) using the Friday Framework.

## 1. Conceptual Model: "One Mind, Many Bodies"

The current `FridayContainer` architecture initializes the Memory System ("The Mind") as a singleton. This offers a unique opportunity for multi-agent orchestration: **Shared Contextual Awareness**.

*   **The Mind (Shared):** `MemoryController` (Graph + Vector + Episodic).
*   **The Bodies (Distinct):** Multiple `CopilotAgent` instances, each with:
    *   Specific `AgentProfile` (Role, Goal, Prompt).
    *   Specific `ToolRegistry` (Capabilities).

## 2. The Orchestrator Component

We propose a new component in `packages/friday-agent`: `AgentOrchestrator`.

### Responsibilities
1.  **Lifecycle Management:** Spin up/down agent instances based on configuration or dynamic need.
2.  **Routing:** Direct user tasks to the appropriate agent (Manual `@agent` or Semantic Routing).
3.  **State Aggregation:** Collect results from sub-agents and synthesize a final response.
4.  **Loop Management:** Run the concurrent event loops of multiple agents.

### Architecture Diagram

```
[User] -> [Orchestrator]
             |
             +-> [Router (LLM)] "Who handles this?"
             |
             +-> [Researcher Agent] <--> [Web Tools]
             |       |
             |       v
             |    [Shared Memory] <--> [Data Stores]
             |       ^
             |       |
             +-> [Coder Agent] <--> [File Tools]
```

## 3. Delegation Patterns

### Pattern A: The "Router" (Hub & Spoke)
*   **Structure:** One "Supervisor" agent (or a specialized Router Component) receives the user query.
*   **Action:** It analyzes the intent and calls a specific sub-agent.
*   **Flow:** User -> Supervisor -> Sub-Agent -> Supervisor -> User.
*   **Pros:** strict control, clean interface.
*   **Cons:** Bottleneck at the supervisor.

### Pattern B: The "Swarm" (Shared Blackboard)
*   **Structure:** Agents watch a shared "Task Queue" or "Blackboard" (in Memory).
*   **Action:** Agents self-select tasks they can handle.
*   **Flow:** User -> Memory -> Agent A (picks task) -> Memory -> Agent B (reviews output).
*   **Pros:** Highly scalable, asynchronous.
*   **Cons:** Hard to debug, race conditions.

### Recommended MVP: Explicit Delegation
Start with **Pattern A** but strictly defined in the `Orchestrator`.

```python
class AgentOrchestrator:
    def __init__(self, memory: MemoryController):
        self.agents = {}
        self.memory = memory

    def register_agent(self, name: str, profile: AgentProfile, tools: list):
        # Create agent with shared memory but unique profile/tools
        self.agents[name] = CopilotAgent(..., profile=profile, memory=self.memory)

    async def route_task(self, query: str) -> str:
        # 1. Ask a lightweight LLM Router
        target_agent = await self.router.decide(query, available=self.agents.keys())
        
        # 2. Delegate
        return await self.agents[target_agent].run(query)
```

## 4. Advanced Orchestration: Dynamic Task Graphs

Beyond simple routing, the Orchestrator acts as a **Workflow Engine**, managing complex multi-step processes.

### 4.1 The Task Graph
The Orchestrator constructs a directed graph of activities to solve a high-level goal.
*   **Nodes:** Agent Tasks (e.g., "Research", "Code", "Review").
*   **Edges:** Data Dependencies (Artifacts/Context hand-offs).

### 4.2 State & Artifact Management
Agents communicate via **Artifacts** stored in Shared Memory or Filesystem.
*   **Exit Criteria:** Agent A produces an artifact (e.g., `spec.md`).
*   **Entry Criteria:** Agent B requires `spec.md` to start.

### 4.3 Loop Detection & Guardrails
To prevent infinite "Death Spirals" (e.g., Coder <-> Reviewer fighting forever):
1.  **Max Depth:** Hard limit on graph depth (e.g., 10 steps).
2.  **State Hashing:** Detect repeating state sequences (Input + Context).
3.  **Supervisor Intervention:** If a loop is detected, the Orchestrator pauses and asks the User (or a Senior Supervisor Agent) for a tie-breaking decision.

## 5. Task Definition & Human-in-the-Loop

To orchestrate complex workflows, we need a formal definition of the "Mission".

### 5.1 The Task Specification (`task.yaml`)
This defines the global goal and the rules of engagement.

```yaml
name: "Newsletter Generation"
goal: "Create a weekly newsletter about AI."
inputs:
  - name: "topic"
    value: "LLM Agents"

steps:
  - id: "research"
    agent: "Researcher"
    goal: "Find 5 articles about {topic}."
    outputs:
      - "research_summary"

  - id: "draft"
    agent: "Writer"
    inputs:
      - from: "research.research_summary"
    goal: "Draft a blog post."
    outputs:
      - "draft.md"

  - id: "approval"
    type: "human_approval" # Special node type
    inputs:
      - from: "draft.draft.md"
    instruction: "Review the draft. Approve or provide feedback."
    
  - id: "publish"
    agent: "Publisher"
    inputs: 
      - from: "draft.draft.md"
    condition: "approval.status == 'approved'"
```

### 5.2 Artifact Routing
The Orchestrator acts as the "courier".
1.  **Capture:** When `Researcher` finishes, the Orchestrator looks at its manifest. It sees `research_summary` is a file at `outputs/summary.md`.
2.  **Transport:** It reads the location.
3.  **Inject:** When starting `Writer`, it injects the artifact location into the `Writer`'s context or inputs.

### 5.3 Human-in-the-Loop (HIL)
HIL is treated as a **Blocking Node** in the graph.
*   **Action:** Orchestrator pauses the workflow.
*   **Notification:** It alerts the user (CLI prompt / UI notification).
*   **Resume:** When user inputs "Approve" or "Retry", the graph resumes.
    *   *Retry:* Can trigger a loop back to a previous step (e.g., back to `Writer` with user feedback).

## 7. State-of-the-Art Design Patterns

### 7.1 The Actor Model
We treat each Agent Instance as an **Actor**:
*   **State:** Private Memory (Scratchpad).
*   **Mailbox:** Input Queue (Task Specs from Orchestrator).
*   **Behavior:** The `run()` loop.
This decouples execution. The Orchestrator spawns `asyncio.Task`s for each active agent, monitoring them for completion or failure (Supervisor Pattern).

### 7.2 Standardized Messaging (CloudEvents)
To decouple the Orchestrator from specific artifact formats, we use a standard envelope for all Agent inputs/outputs.

```json
{
  "specversion": "1.0",
  "type": "friday.artifact.produced",
  "source": "agent:researcher",
  "subject": "research_summary",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "time": "2023-10-01T12:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "location": "shared:research/summary.md",
    "summary": "AI Agents are evolving..."
  }
}
```

## 8. Collaboration & Shared Memory Provenance

When multiple agents share a "Hive Mind" (MemoryController), tracking the origin of information is critical for trust and debugging.

### 8.1 Enhanced Provenance Model
We extend the usage of `ProvenanceMetadata` in Shared Memory.
*   **`author_id`:** Must be the specific `agent_id` (e.g., "researcher_01").
*   **`source_id`:** The `run_id` or `turn_id` where the fact was generated.
*   **`source_type`:** Extended to include "agent_inference", "tool_output".

### 8.2 Conflict Resolution
The Orchestrator or a specific "Arbiter Agent" resolves conflicting facts in Shared Memory based on Agent Authority.
*   *Scenario:* Researcher says "Project X is cancelled." Sales says "Project X is active."
*   *Logic:* Registry defines `Researcher` has higher authority on `status` facts.
*   *Action:* The Researcher's fact overwrites (or versions) the Sales fact.

### 8.3 The Multi-Agent Transcript
The `TranscriptStore` must support interleaved execution.
*   **Session ID:** Shared across the Task Graph.
*   **Turns:** Each turn is tagged with the acting `agent_id`.
*   **View:** Debuggers can filter by Agent (Swimlanes) or Time (Global Sequence).
