# Phase 3 Execution Plan: The Mind (Orchestration)

**Status:** Ready for Implementation
**Target:** Project Hive Master Plan, Phase 3 (Section 4)
**Objective:** Enable multiple agents to exist, coordinate, and share information with provenance tracking

---

## Executive Summary

Phase 3 implements the "Mind" of the Hive system with two major components:

| Component | Description | Risk Level |
|-----------|-------------|------------|
| **4.1 Orchestrator MVP** | Multi-agent routing, switching, and delegation | High |
| **4.2 Shared Memory Provenance** | Track authorship across agents for audit/debug | Medium |

**Exit Criterion:** Integration test where Agent A writes a fact, and Agent B reads it with proper provenance.

---

## Implementation Steps

### Step 1: Shared Memory Provenance Foundation (Section 4.2)

Provenance must be implemented FIRST because the Orchestrator depends on agents properly attributing their memory operations.

#### 1.1 Update ProvenanceMetadata Validation

**File:** `packages/friday-memory/src/friday_memory/models/graph.py`

**Current State:** `author_id` is optional (`str | None = None`)

**Required Changes:**
- Add `@field_validator("author_id")` to enforce non-empty when provided
- Add factory functions: `create_agent_provenance()`, `create_user_provenance()`, `create_extraction_provenance()`
- Add `with_parent()` method for lineage tracking
- Add `to_dict()` / `from_dict()` serialization

**Code Changes:**
```python
from pydantic import field_validator

class ProvenanceMetadata(BaseModel):
    # ... existing fields ...

    @field_validator("author_id")
    @classmethod
    def validate_author_id(cls, v: str | None) -> str | None:
        """Normalize author_id if provided."""
        if v is not None:
            v = v.strip().lower()
            if not v:
                raise ValueError("author_id cannot be empty string")
        return v

    def with_parent(self, parent_id: str) -> "ProvenanceMetadata":
        """Create new ProvenanceMetadata with additional parent."""
        # Implementation per build plan
        pass

# Factory functions
def create_agent_provenance(author_id: str, source_id: str = "manual", confidence: float = 1.0) -> ProvenanceMetadata:
    """Create provenance for agent-generated data."""
    pass

def create_user_provenance(user_id: str, source_id: str = "user_input") -> ProvenanceMetadata:
    """Create provenance for user-provided data."""
    pass
```

---

#### 1.2 Add Author Tracking to MemoryController

**File:** `packages/friday-memory/src/friday_memory/controller/memory_controller.py`

**Required Changes:**
- Add `_default_author_id: str` field (default: "system")
- Add `set_author(author_id: str)` method
- Add `current_author` property
- Add `_ensure_provenance(node, author_id)` helper
- Update `store_fact()`, `store_insight()` to accept optional `author_id` override
- Add `get_facts_by_author()` and `get_insights_by_author()` query methods

**Key Method Signatures:**
```python
class MemoryController:
    DEFAULT_AUTHOR = "system"

    def __init__(self, ..., default_author_id: str = DEFAULT_AUTHOR):
        self._default_author_id = default_author_id

    @property
    def current_author(self) -> str:
        """Get the current default author."""
        return self._default_author_id

    def set_author(self, author_id: str) -> None:
        """Set the current author for memory operations."""
        if not author_id or not author_id.strip():
            raise ValueError("author_id cannot be empty")
        self._default_author_id = author_id.strip().lower()

    async def store_fact(self, node: GraphNode, edge: GraphEdge | None = None, author_id: str | None = None) -> str:
        """Store fact with provenance tracking."""
        node = self._ensure_provenance(node, author_id)
        # ... existing logic

    async def get_facts_by_author(self, author_id: str, limit: int = 100) -> list[GraphNode]:
        """Query facts by author."""
        # Filter by provenance.author_id
```

---

#### 1.3 Add agent_id to TranscriptEntry

**File:** `packages/friday-transcript/src/friday_transcript/models/transcript.py`

**Required Changes:**
- Add `agent_id: str | None = Field(default=None, description="Which agent generated this response")`
- Place after `assistant_message` for logical grouping

```python
class TranscriptEntry(BaseModel):
    # ... existing fields ...

    # Agent tracking (NEW)
    agent_id: str | None = Field(
        default=None,
        description="Which agent generated this response"
    )
```

---

#### 1.4 SQLite Schema Migration for agent_id

**File:** `packages/friday-transcript/src/friday_transcript/stores/sqlite.py`

**Required Changes:**
- Add `agent_id TEXT` column to `transcript_entries` table
- Add migration for existing databases
- Add index on `agent_id` for efficient queries
- Add `get_entries_by_agent(session_id, agent_id)` method

**Migration SQL:**
```sql
-- Check if column exists, add if not
ALTER TABLE transcript_entries ADD COLUMN agent_id TEXT;
CREATE INDEX IF NOT EXISTS idx_entries_agent_id ON transcript_entries(agent_id);
```

**New Method:**
```python
async def get_entries_by_agent(self, session_id: str, agent_id: str, limit: int = 100) -> list[TranscriptEntry]:
    """Get entries from a specific agent."""
    cursor = await self._db.execute(
        "SELECT * FROM transcript_entries WHERE session_id = ? AND agent_id = ? ORDER BY turn_number DESC LIMIT ?",
        (session_id, agent_id, limit),
    )
    # ... parse rows
```

---

#### 1.5 Update InteractionTurn Model

**File:** `packages/friday-memory/src/friday_memory/models/session.py`

**Required Changes:**
- Add `agent_id: str | None = None` field to `InteractionTurn`

---

#### 1.6 Update AgentBase for Provenance

**File:** `packages/friday-agent/src/friday_agent/base.py`

**Required Changes:**
- In `initialize_session()`: Call `self.memory.set_author(self.profile.name)`
- In `_archive_turn()`: Pass `agent_id=self.profile.name` to transcript

```python
async def initialize_session(self, session_id: str | None = None, user_id: str = "default") -> SessionState:
    """Initialize session with provenance setup."""
    self.session_id = session_id or str(uuid.uuid4())

    # SET MEMORY AUTHOR to this agent
    self.memory.set_author(self.profile.name)

    self.session_state = await self.context_engine.initialize_session(...)
    return self.session_state

async def _archive_turn(self, user_message, assistant_message, tool_calls, tool_results) -> None:
    """Archive turn with agent attribution."""
    turn = InteractionTurn(
        # ... existing fields ...
        agent_id=self.profile.name,  # NEW
    )
    # ... rest of method
```

---

#### 1.7 Create Provenance Unit Tests

**File:** `packages/friday-memory/tests/test_provenance.py` (NEW)

Test cases:
- Valid provenance creation
- Empty author_id validation (when explicitly set)
- Author normalization (whitespace, case)
- `with_parent()` lineage tracking
- Serialization roundtrip
- Factory functions

---

### Step 2: Orchestrator MVP (Section 4.1)

#### 2.1 Create AgentOrchestrator

**File:** `packages/friday-agent/src/friday_agent/orchestrator.py` (NEW)

**Core Implementation:**
- `ROUTING_PATTERN = re.compile(r"^@(\w+)\s+(.+)$", re.DOTALL)` for explicit routing
- Session state: `_active_agent`, `_active_agent_name`, `_agent_cache`
- Methods per build plan:
  - `process(user_input: str) -> str` - Main entry point with routing
  - `switch_agent(name: str) -> None` - Change active agent
  - `delegate(agent_name: str, task: str, return_to_current: bool) -> str` - Delegation
  - `list_agents() -> list[str]`
  - `get_agent_info(name: str) -> dict`
  - `get_status() -> dict`
  - `clear_cache()` / `shutdown()`

**Key Design:**
- Single active agent at a time (no concurrency in MVP)
- Agent instances cached for session duration
- Explicit routing first (`@agent_name message`)
- Fall back to active agent, then default agent

---

#### 2.2 Update Package Exports

**File:** `packages/friday-agent/src/friday_agent/__init__.py`

Add:
```python
from friday_agent.orchestrator import AgentOrchestrator, OrchestratorError

__all__ = [
    # ... existing exports ...
    "AgentOrchestrator",
    "OrchestratorError",
]
```

---

#### 2.3 Update FridayContainer for Orchestrator

**File:** `apps/friday-cli/src/friday_cli/container.py`

**Required Changes:**
- Add `_orchestrator: AgentOrchestrator | None = None`
- Add `orchestrator` property (lazy init with registry and default agent)
- Configure orchestrator with container's agent registry

```python
@property
def orchestrator(self) -> AgentOrchestrator:
    """Get or create the agent orchestrator."""
    if self._orchestrator is None:
        from friday_agent import AgentOrchestrator

        default_agent = None
        if self.agent_registry.list_agents():
            default_agent = self.agent_registry.list_agents()[0]

        self._orchestrator = AgentOrchestrator(
            registry=self.agent_registry,
            default_agent=default_agent,
        )
    return self._orchestrator
```

---

#### 2.4 Add CLI Commands to memory-chat-v2

**File:** `tests/integration/memory/memory-chat-v2.py`

Add orchestration commands:
- `/switch <agent>` - Switch to agent or show status
- `/agents` - List available agents with capabilities
- `/agent [name]` - Show agent details
- `/delegate <agent> <task>` - Delegate task to another agent
- `/status` - Show orchestrator status

**Implementation Notes:**
- Add `orchestrator` to CLI context
- Wire up explicit routing (`@agent_name message`) in main input loop
- Update prompt to show active agent name

---

#### 2.5 Create Orchestrator Unit Tests

**File:** `packages/friday-agent/tests/test_orchestrator.py` (NEW)

Test cases:
- Explicit routing (`@agent_name message`)
- Default agent fallback
- No agent error handling
- Agent switching
- Agent caching
- Delegation with return
- Delegation without return
- Unknown agent error
- Status and listing

---

### Step 3: Integration Testing

#### 3.1 Multi-Agent Provenance Test

```python
@pytest.mark.asyncio
async def test_multi_agent_provenance(container):
    """Test provenance tracking across agents."""
    # Agent A stores a fact
    container.memory.set_author("researcher")
    await container.memory.store_fact(GraphNode(
        id="fact_1", type="fact", label="Research Finding",
        provenance=create_agent_provenance("researcher", "research_1"),
    ))

    # Agent B stores a fact
    container.memory.set_author("coder")
    await container.memory.store_fact(GraphNode(
        id="fact_2", type="fact", label="Code Insight",
        provenance=create_agent_provenance("coder", "code_1"),
    ))

    # Query by author
    researcher_facts = await container.memory.get_facts_by_author("researcher")
    assert len(researcher_facts) >= 1
    assert researcher_facts[0].provenance.author_id == "researcher"
```

#### 3.2 The "Hive Mind" Test

Per Master Plan Section 6.4:
1. Start with orchestrator
2. As Agent A: Store "Project Status is Green"
3. Switch to Agent B (Shared Mode)
4. Ask: "What is the Project Status?" → Must retrieve "Green"
5. Check Provenance → Author should be "Agent A"

---

## Files Summary

| File | Action | Step |
|------|--------|------|
| `packages/friday-memory/src/friday_memory/models/graph.py` | Modify | 1.1 |
| `packages/friday-memory/src/friday_memory/controller/memory_controller.py` | Modify | 1.2 |
| `packages/friday-transcript/src/friday_transcript/models/transcript.py` | Modify | 1.3 |
| `packages/friday-transcript/src/friday_transcript/stores/sqlite.py` | Modify | 1.4 |
| `packages/friday-memory/src/friday_memory/models/session.py` | Modify | 1.5 |
| `packages/friday-agent/src/friday_agent/base.py` | Modify | 1.6 |
| `packages/friday-memory/tests/test_provenance.py` | Create | 1.7 |
| `packages/friday-agent/src/friday_agent/orchestrator.py` | Create | 2.1 |
| `packages/friday-agent/src/friday_agent/__init__.py` | Modify | 2.2 |
| `apps/friday-cli/src/friday_cli/container.py` | Modify | 2.3 |
| `tests/integration/memory/memory-chat-v2.py` | Modify | 2.4 |
| `packages/friday-agent/tests/test_orchestrator.py` | Create | 2.5 |

---

## Execution Order

**Recommended sequence to minimize risk and enable incremental testing:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PHASE 3A: PROVENANCE FOUNDATION (Can be tested independently)          │
├─────────────────────────────────────────────────────────────────────────┤
│  1.1 ProvenanceMetadata updates (validation, factories)                 │
│  1.5 InteractionTurn agent_id field                                     │
│  1.3 TranscriptEntry agent_id field                                     │
│  1.4 SQLite migration                                                   │
│  1.2 MemoryController author tracking                                   │
│  1.6 AgentBase provenance integration                                   │
│  1.7 Provenance unit tests                                              │
│                                                                         │
│  ✓ CHECKPOINT: Run existing tests, verify no regressions               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  PHASE 3B: ORCHESTRATOR MVP                                             │
├─────────────────────────────────────────────────────────────────────────┤
│  2.1 AgentOrchestrator implementation                                   │
│  2.2 Package exports                                                    │
│  2.3 FridayContainer integration                                        │
│  2.5 Orchestrator unit tests                                            │
│                                                                         │
│  ✓ CHECKPOINT: Orchestrator unit tests pass                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  PHASE 3C: CLI INTEGRATION                                              │
├─────────────────────────────────────────────────────────────────────────┤
│  2.4 memory-chat-v2 orchestration commands                              │
│  3.1 Multi-agent provenance integration test                            │
│  3.2 "Hive Mind" manual test                                            │
│                                                                         │
│  ✓ EXIT CRITERIA: Agent A writes fact, Agent B reads it with provenance │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Risk Mitigation

### Backwards Compatibility
- `author_id` remains optional in `ProvenanceMetadata` (default None for existing data)
- `agent_id` optional in `TranscriptEntry` (existing entries have None)
- SQLite migration handles existing databases gracefully
- `MemoryController` constructor maintains backwards compatibility

### Regression Prevention
Per Master Plan Section 6.4:
1. Constructor compatibility check - verify `MemoryController.__init__` accepts legacy arguments
2. Schema validation check - verify models work without new fields
3. Behavioral regression - run `memory-chat-v2` standard "Store/Recall" loop

### Testing Checkpoints
- After Step 1: All existing unit tests pass
- After Step 2: Orchestrator unit tests pass (90%+ coverage)
- After Step 3: Integration tests pass, CLI commands work

---

## Exit Criteria Checklist

- [ ] `ProvenanceMetadata` validates `author_id` when provided
- [ ] `MemoryController.set_author()` sets default author
- [ ] All memory writes can include author attribution
- [ ] `TranscriptEntry` includes `agent_id` field
- [ ] SQLite migration adds `agent_id` column
- [ ] `AgentBase.initialize_session()` sets memory author
- [ ] Can query memories by author
- [ ] `AgentOrchestrator` routes `@agent_name` messages correctly
- [ ] Default agent fallback works
- [ ] Agent switching preserves context
- [ ] Delegation returns result and optionally switches back
- [ ] CLI commands (`/switch`, `/agents`, `/delegate`, `/status`) work
- [ ] Unit tests achieve 90%+ coverage
- [ ] **Integration test: Agent A writes fact, Agent B reads it**

---

## Estimated Complexity

| Component | LOC (approx) | Complexity |
|-----------|--------------|------------|
| ProvenanceMetadata updates | ~80 | Low |
| MemoryController updates | ~120 | Medium |
| TranscriptEntry + SQLite | ~100 | Low |
| AgentBase updates | ~40 | Low |
| AgentOrchestrator | ~350 | High |
| CLI commands | ~150 | Medium |
| Unit tests | ~400 | Medium |
| **Total** | **~1,240** | **Medium-High** |

---

## Dependencies

### Internal (from Phase 2)
- `AgentRegistry` - Agent lookup and creation
- `AgentProfile` - Agent configuration with capabilities
- `FridayContainer` - Dependency injection

### External
- None (no new external dependencies)
