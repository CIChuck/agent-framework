# Shared Memory Provenance Build Plan

**Status:** Planning
**Target:** Phase 3, Section 4.2 of Project Hive Master Plan
**Objective:** Track memory authorship across multiple agents for audit, trust, and debugging

---

## 1. Problem Statement

When multiple agents share memory, we lose track of:
- **Who created each memory**: Which agent stored a fact or insight?
- **Who accessed each memory**: Which agent used information?
- **Attribution chains**: Did Agent B use info from Agent A?
- **Trust verification**: Can we trust info from a specific agent?

Without provenance tracking:
- Debugging multi-agent issues is impossible
- No accountability for incorrect information
- No way to audit the knowledge chain
- Cannot filter memories by source agent

---

## 2. Architecture

### 2.1 Provenance Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent (author)                            │
│  researcher  │  coder  │  user  │  system                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ (stores with author_id)
┌─────────────────────────────────────────────────────────────┐
│                   MemoryController                           │
│  - Enforces author_id on all writes                         │
│  - Tracks current author via set_author()                   │
│  - Passes provenance to storage adapters                    │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   Graph Store    │ │   Vector Store  │ │ Transcript Store │
│ (ProvenanceData) │ │    (metadata)   │ │   (agent_id)    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 2.2 Provenance Data Model

```
┌─────────────────────────────────────────────────────────────┐
│                   ProvenanceMetadata                         │
├─────────────────────────────────────────────────────────────┤
│  source_id: str       # ID of source (turn_id, doc_id)      │
│  source_type: str     # Type: "turn", "extraction", etc.    │
│  author_id: str       # Agent/user who created this         │
│  confidence: float    # Confidence score (0.0-1.0)          │
│  created_at: datetime # When this was created               │
│  parent_ids: list[str]# IDs of source data (for chains)     │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Design Principles

1. **Mandatory Author**: All memory writes require `author_id`
2. **Context-Based Default**: Author set once per agent session
3. **Immutable Provenance**: Provenance cannot be modified after creation
4. **Queryable**: Can filter memories by author
5. **Minimal Overhead**: Provenance adds minimal storage/compute cost

---

## 3. Implementation

### 3.1 ProvenanceMetadata Updates

**Location:** `packages/friday-memory/src/friday_memory/models/graph.py`

Update ProvenanceMetadata with validation:

```python
"""Graph data models with provenance tracking."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ProvenanceMetadata(BaseModel):
    """
    Metadata tracking the origin and lineage of stored data.

    Every piece of stored data (nodes, edges, vectors) must have
    provenance information to support:
    - Attribution: Who created this?
    - Audit: When and why was this created?
    - Trust: How confident are we in this data?
    - Lineage: What was this derived from?

    Attributes:
        source_id: ID of the source (turn_id, document_id, etc.)
        source_type: Type of source ("turn", "extraction", "import", "agent")
        author_id: ID of the agent/user who created this (REQUIRED)
        confidence: Confidence score (0.0 = uncertain, 1.0 = certain)
        created_at: Timestamp of creation
        parent_ids: IDs of parent data this was derived from
    """

    source_id: str
    source_type: str
    author_id: str  # REQUIRED - validated below
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    parent_ids: list[str] = Field(default_factory=list)

    @field_validator("author_id")
    @classmethod
    def validate_author_id(cls, v: str) -> str:
        """Ensure author_id is non-empty."""
        if not v or not v.strip():
            raise ValueError("author_id is required and cannot be empty")
        return v.strip().lower()

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v: str) -> str:
        """Normalize source_type."""
        return v.strip().lower()

    def with_parent(self, parent_id: str) -> ProvenanceMetadata:
        """
        Create a new ProvenanceMetadata with an additional parent.

        Useful for tracking data lineage when deriving new data.

        Args:
            parent_id: ID of the parent data

        Returns:
            New ProvenanceMetadata with parent added
        """
        return ProvenanceMetadata(
            source_id=self.source_id,
            source_type=self.source_type,
            author_id=self.author_id,
            confidence=self.confidence,
            created_at=self.created_at,
            parent_ids=[*self.parent_ids, parent_id],
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "author_id": self.author_id,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "parent_ids": self.parent_ids,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProvenanceMetadata:
        """Deserialize from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        return cls(
            source_id=data["source_id"],
            source_type=data["source_type"],
            author_id=data["author_id"],
            confidence=data.get("confidence", 1.0),
            created_at=created_at or datetime.utcnow(),
            parent_ids=data.get("parent_ids", []),
        )


# Convenience factory functions
def create_agent_provenance(
    author_id: str,
    source_id: str = "manual",
    confidence: float = 1.0,
) -> ProvenanceMetadata:
    """Create provenance for agent-generated data."""
    return ProvenanceMetadata(
        source_id=source_id,
        source_type="agent",
        author_id=author_id,
        confidence=confidence,
    )


def create_extraction_provenance(
    author_id: str,
    source_id: str,
    parent_ids: list[str] | None = None,
    confidence: float = 0.9,
) -> ProvenanceMetadata:
    """Create provenance for extracted data."""
    return ProvenanceMetadata(
        source_id=source_id,
        source_type="extraction",
        author_id=author_id,
        confidence=confidence,
        parent_ids=parent_ids or [],
    )


def create_user_provenance(
    user_id: str,
    source_id: str = "user_input",
) -> ProvenanceMetadata:
    """Create provenance for user-provided data."""
    return ProvenanceMetadata(
        source_id=source_id,
        source_type="user",
        author_id=user_id,
        confidence=1.0,
    )
```

### 3.2 MemoryController Updates

**Location:** `packages/friday-memory/src/friday_memory/controller/memory_controller.py`

Add author tracking to MemoryController:

```python
"""Memory controller with provenance tracking."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from friday_memory.models.graph import (
    GraphNode,
    GraphEdge,
    ProvenanceMetadata,
    create_agent_provenance,
)

if TYPE_CHECKING:
    from friday_core.interfaces.memory import (
        VectorStoreAdapter,
        GraphStoreAdapter,
    )


logger = logging.getLogger(__name__)


class MemoryController:
    """
    Unified controller for memory operations with provenance tracking.

    The MemoryController enforces that all memory writes include author
    information for provenance tracking. It maintains a default author
    that agents should set when they start processing.

    Usage:
        controller = MemoryController(vector_store, graph_store)

        # Set author when agent starts
        controller.set_author("researcher")

        # Store data (author automatically applied)
        await controller.store_fact(node)

        # Or override author for specific operation
        await controller.store_fact(node, author_id="coder")
    """

    DEFAULT_AUTHOR = "system"

    def __init__(
        self,
        vector_store: VectorStoreAdapter,
        graph_store: GraphStoreAdapter,
        default_author_id: str = DEFAULT_AUTHOR,
    ):
        """
        Initialize memory controller.

        Args:
            vector_store: Vector store adapter
            graph_store: Graph store adapter
            default_author_id: Default author for memory operations
        """
        self._vector_store = vector_store
        self._graph_store = graph_store
        self._default_author_id = default_author_id

        logger.debug(f"MemoryController initialized (author={default_author_id})")

    # =========================================================================
    # Author Management
    # =========================================================================

    @property
    def current_author(self) -> str:
        """Get the current default author."""
        return self._default_author_id

    def set_author(self, author_id: str) -> None:
        """
        Set the current author for memory operations.

        Should be called when an agent starts processing to ensure
        all memory operations are attributed correctly.

        Args:
            author_id: Agent or user ID

        Raises:
            ValueError: If author_id is empty
        """
        if not author_id or not author_id.strip():
            raise ValueError("author_id cannot be empty")

        self._default_author_id = author_id.strip().lower()
        logger.debug(f"Memory author set to: {self._default_author_id}")

    def _get_effective_author(self, author_id: str | None) -> str:
        """Get the effective author (provided or default)."""
        if author_id:
            return author_id.strip().lower()
        return self._default_author_id

    def _ensure_provenance(
        self,
        node: GraphNode,
        author_id: str | None = None,
    ) -> GraphNode:
        """
        Ensure node has valid provenance with author.

        If node lacks provenance, creates default provenance.
        If provenance exists but lacks author, sets author.

        Args:
            node: GraphNode to process
            author_id: Override author (uses default if None)

        Returns:
            Node with valid provenance
        """
        effective_author = self._get_effective_author(author_id)

        if node.provenance is None:
            # Create default provenance
            node.provenance = create_agent_provenance(
                author_id=effective_author,
                source_id=node.id,
            )
        else:
            # Ensure author is set
            if not node.provenance.author_id:
                node.provenance.author_id = effective_author

        return node

    # =========================================================================
    # Graph Operations (with provenance)
    # =========================================================================

    async def store_fact(
        self,
        node: GraphNode,
        edge: GraphEdge | None = None,
        author_id: str | None = None,
    ) -> str:
        """
        Store a fact in the graph with provenance tracking.

        Args:
            node: GraphNode representing the fact
            edge: Optional edge connecting to existing node
            author_id: Override author (uses default if None)

        Returns:
            ID of stored node
        """
        # Ensure provenance
        node = self._ensure_provenance(node, author_id)

        # Store node
        node_id = await self._graph_store.add_node(node)
        logger.debug(f"Stored fact {node_id} by {node.provenance.author_id}")

        # Store edge if provided
        if edge:
            await self._graph_store.add_edge(edge)

        return node_id

    async def store_insight(
        self,
        text: str,
        source_id: str,
        author_id: str | None = None,
        confidence: float = 0.9,
        extra_metadata: dict | None = None,
    ) -> str:
        """
        Store an insight in the vector store with provenance.

        Args:
            text: Insight text
            source_id: ID of the source (e.g., turn_id)
            author_id: Override author (uses default if None)
            confidence: Confidence score
            extra_metadata: Additional metadata

        Returns:
            ID of stored insight
        """
        effective_author = self._get_effective_author(author_id)

        # Build metadata with provenance
        metadata = {
            "author_id": effective_author,
            "source_id": source_id,
            "source_type": "insight",
            "confidence": confidence,
            **(extra_metadata or {}),
        }

        # Store in vector store
        ids = await self._vector_store.add_documents(
            texts=[text],
            metadatas=[metadata],
        )

        logger.debug(f"Stored insight {ids[0]} by {effective_author}")
        return ids[0]

    # =========================================================================
    # Provenance Queries
    # =========================================================================

    async def get_facts_by_author(
        self,
        author_id: str,
        limit: int = 100,
    ) -> list[GraphNode]:
        """
        Get all facts created by a specific author.

        Args:
            author_id: Author to filter by
            limit: Maximum results

        Returns:
            List of GraphNodes by that author
        """
        # Note: This requires graph store to support metadata queries
        # Implementation depends on graph store capabilities
        # For now, using fuzzy_search as fallback
        all_nodes = await self._graph_store.fuzzy_search(
            query="",  # Get all
            limit=limit * 2,  # Over-fetch for filtering
        )

        # Filter by author
        results = [
            node
            for node in all_nodes
            if node.provenance and node.provenance.author_id == author_id.lower()
        ]

        return results[:limit]

    async def get_insights_by_author(
        self,
        author_id: str,
        limit: int = 100,
    ) -> list:
        """
        Get all insights created by a specific author.

        Args:
            author_id: Author to filter by
            limit: Maximum results

        Returns:
            List of insights by that author
        """
        results = await self._vector_store.query(
            query_text="",  # Match all (implementation may vary)
            n_results=limit,
            where={"author_id": author_id.lower()},
        )
        return results
```

### 3.3 TranscriptEntry Updates

**Location:** `packages/friday-transcript/src/friday_transcript/models/transcript.py`

Add `agent_id` field to TranscriptEntry:

```python
"""Transcript data models with agent tracking."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TranscriptEntry(BaseModel):
    """
    Single conversation turn in transcript.

    Represents one exchange (user message + assistant response) with
    associated metadata for analysis and replay.

    The agent_id field tracks which agent generated the response,
    enabling multi-agent transcript analysis.
    """

    id: str
    session_id: str
    turn_number: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Messages
    user_message: str | None = None
    assistant_message: str | None = None

    # Agent tracking (NEW)
    agent_id: str | None = None  # Which agent generated this response

    # Tool usage
    tool_calls: list[ToolCall] = Field(default_factory=list)
    tool_results: list[ToolResult] = Field(default_factory=list)

    # Token usage
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None

    # Timing
    latency_ms: int | None = None
    response_started_at: datetime | None = None
    response_completed_at: datetime | None = None

    # Model info
    model_name: str | None = None
    temperature: float | None = None
    context_tokens_used: int | None = None

    # Extensible metadata
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""

        extra = "allow"  # Allow additional fields
```

### 3.4 SQLite Store Schema Migration

**Location:** `packages/friday-transcript/src/friday_transcript/stores/sqlite.py`

Add migration for `agent_id` column:

```python
"""SQLite transcript store with agent tracking."""

# Add to schema creation
CREATE_ENTRIES_TABLE = """
CREATE TABLE IF NOT EXISTS transcript_entries (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    turn_number INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    user_message TEXT,
    assistant_message TEXT,
    agent_id TEXT,  -- NEW: Track which agent responded
    tool_calls TEXT,  -- JSON
    tool_results TEXT,  -- JSON
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    latency_ms INTEGER,
    model_name TEXT,
    temperature REAL,
    context_tokens_used INTEGER,
    response_started_at TEXT,
    response_completed_at TEXT,
    metadata TEXT,  -- JSON
    FOREIGN KEY (session_id) REFERENCES transcript_sessions(session_id)
);
"""

# Add index for agent queries
CREATE_AGENT_INDEX = """
CREATE INDEX IF NOT EXISTS idx_entries_agent_id
ON transcript_entries(agent_id);
"""

# Migration for existing databases
MIGRATION_ADD_AGENT_ID = """
ALTER TABLE transcript_entries ADD COLUMN agent_id TEXT;
"""


class SQLiteTranscriptStore:
    """SQLite-based transcript storage with agent tracking."""

    async def _run_migrations(self) -> None:
        """Run database migrations."""
        # Check if agent_id column exists
        cursor = await self._db.execute(
            "PRAGMA table_info(transcript_entries)"
        )
        columns = await cursor.fetchall()
        column_names = [col[1] for col in columns]

        if "agent_id" not in column_names:
            await self._db.execute(MIGRATION_ADD_AGENT_ID)
            await self._db.execute(CREATE_AGENT_INDEX)
            await self._db.commit()
            logger.info("Migrated: Added agent_id column")

    async def add_entry(
        self,
        session_id: str,
        turn_number: int,
        user_message: str | None = None,
        assistant_message: str | None = None,
        agent_id: str | None = None,  # NEW
        tool_calls: list | None = None,
        tool_results: list | None = None,
        **kwargs,
    ) -> str:
        """Add transcript entry with agent tracking."""
        entry_id = f"{session_id}_{turn_number}"

        await self._db.execute(
            """
            INSERT INTO transcript_entries (
                id, session_id, turn_number, timestamp,
                user_message, assistant_message, agent_id,
                tool_calls, tool_results, ...
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ...)
            """,
            (
                entry_id,
                session_id,
                turn_number,
                datetime.utcnow().isoformat(),
                user_message,
                assistant_message,
                agent_id,  # NEW
                json.dumps(tool_calls) if tool_calls else None,
                json.dumps(tool_results) if tool_results else None,
                ...
            ),
        )

        return entry_id

    async def get_entries_by_agent(
        self,
        session_id: str,
        agent_id: str,
        limit: int = 100,
    ) -> list[TranscriptEntry]:
        """Get entries from a specific agent."""
        cursor = await self._db.execute(
            """
            SELECT * FROM transcript_entries
            WHERE session_id = ? AND agent_id = ?
            ORDER BY turn_number DESC
            LIMIT ?
            """,
            (session_id, agent_id, limit),
        )
        rows = await cursor.fetchall()
        return [self._row_to_entry(row) for row in rows]
```

### 3.5 Agent Base Class Updates

**Location:** `packages/friday-agent/src/friday_agent/base.py`

Update AgentBase to set author on initialization:

```python
"""Base agent class with provenance integration."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from friday_agent.profile import AgentProfile
    from friday_memory.controller import MemoryController
    from friday_transcript.stores.protocol import TranscriptStore


logger = logging.getLogger(__name__)


class AgentBase(ABC):
    """
    Base class for all agents with provenance integration.

    Automatically sets memory author to agent name when session starts,
    ensuring all memory operations are attributed correctly.
    """

    def __init__(
        self,
        profile: AgentProfile,
        memory: MemoryController,
        transcript_store: TranscriptStore | None = None,
        # ... other dependencies
    ):
        """Initialize agent with dependencies."""
        self._profile = profile
        self._memory = memory
        self._transcript_store = transcript_store
        self._session_id: str | None = None

    @property
    def profile(self) -> AgentProfile:
        """Get agent profile."""
        return self._profile

    @property
    def name(self) -> str:
        """Get agent name."""
        return self._profile.name

    async def initialize_session(
        self,
        session_id: str | None = None,
    ) -> str:
        """
        Initialize agent session with provenance setup.

        Sets the memory author to this agent's name, ensuring
        all subsequent memory operations are attributed correctly.

        Args:
            session_id: Optional session ID (generated if not provided)

        Returns:
            Session ID
        """
        # Generate or use provided session ID
        self._session_id = session_id or self._generate_session_id()

        # SET MEMORY AUTHOR to this agent
        self._memory.set_author(self._profile.name)
        logger.info(f"Agent {self.name} initialized session {self._session_id}")

        return self._session_id

    async def _archive_turn(
        self,
        turn_number: int,
        user_message: str,
        assistant_message: str,
        tool_calls: list | None = None,
        tool_results: list | None = None,
        **metrics,
    ) -> None:
        """
        Archive turn to transcript with agent attribution.

        Args:
            turn_number: Turn number in session
            user_message: User's message
            assistant_message: Agent's response
            tool_calls: Tool calls made
            tool_results: Tool results received
            **metrics: Additional metrics (tokens, latency, etc.)
        """
        if not self._transcript_store:
            return

        await self._transcript_store.add_entry(
            session_id=self._session_id,
            turn_number=turn_number,
            user_message=user_message,
            assistant_message=assistant_message,
            agent_id=self._profile.name,  # AGENT ATTRIBUTION
            tool_calls=tool_calls,
            tool_results=tool_results,
            **metrics,
        )

        logger.debug(
            f"Archived turn {turn_number} for agent {self.name}"
        )

    @abstractmethod
    async def run(self, user_input: str) -> str:
        """Process user input and return response."""
        pass
```

---

## 4. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `packages/friday-memory/src/friday_memory/models/graph.py` | Modify | Add author_id validation, factory functions |
| `packages/friday-memory/src/friday_memory/controller/memory_controller.py` | Modify | Add set_author(), provenance enforcement |
| `packages/friday-transcript/src/friday_transcript/models/transcript.py` | Modify | Add agent_id field |
| `packages/friday-transcript/src/friday_transcript/stores/sqlite.py` | Modify | Add agent_id column, migration |
| `packages/friday-agent/src/friday_agent/base.py` | Modify | Set author on init, pass agent_id to transcript |
| `packages/friday-memory/tests/test_provenance.py` | Create | Unit tests for provenance |
| `packages/friday-transcript/tests/test_agent_tracking.py` | Create | Unit tests for agent tracking |

---

## 5. Dependencies

### 5.1 Internal Dependencies
- `MemoryController` from friday-memory
- `TranscriptStore` from friday-transcript
- `AgentBase` from friday-agent

### 5.2 No New External Dependencies

---

## 6. Verification

### 6.1 Unit Tests

**Location:** `packages/friday-memory/tests/test_provenance.py`

```python
"""Unit tests for provenance tracking."""

import pytest
from datetime import datetime

from friday_memory.models.graph import (
    ProvenanceMetadata,
    create_agent_provenance,
    create_extraction_provenance,
    create_user_provenance,
)


class TestProvenanceMetadata:
    """Test ProvenanceMetadata validation."""

    def test_valid_provenance(self):
        """Test creating valid provenance."""
        prov = ProvenanceMetadata(
            source_id="turn_123",
            source_type="turn",
            author_id="researcher",
        )
        assert prov.author_id == "researcher"
        assert prov.confidence == 1.0

    def test_author_required(self):
        """Test author_id is required."""
        with pytest.raises(ValueError, match="author_id is required"):
            ProvenanceMetadata(
                source_id="test",
                source_type="test",
                author_id="",
            )

    def test_author_normalized(self):
        """Test author_id is normalized."""
        prov = ProvenanceMetadata(
            source_id="test",
            source_type="test",
            author_id="  RESEARCHER  ",
        )
        assert prov.author_id == "researcher"

    def test_with_parent(self):
        """Test adding parent."""
        prov = create_agent_provenance("researcher", "src1")
        prov2 = prov.with_parent("parent_123")

        assert "parent_123" in prov2.parent_ids
        assert prov.parent_ids == []  # Original unchanged

    def test_serialization(self):
        """Test to_dict/from_dict."""
        prov = ProvenanceMetadata(
            source_id="test",
            source_type="agent",
            author_id="coder",
            confidence=0.9,
            parent_ids=["p1", "p2"],
        )

        data = prov.to_dict()
        prov2 = ProvenanceMetadata.from_dict(data)

        assert prov2.author_id == "coder"
        assert prov2.confidence == 0.9
        assert prov2.parent_ids == ["p1", "p2"]


class TestProvenanceFactories:
    """Test provenance factory functions."""

    def test_create_agent_provenance(self):
        """Test agent provenance factory."""
        prov = create_agent_provenance("researcher", "turn_1")
        assert prov.author_id == "researcher"
        assert prov.source_type == "agent"

    def test_create_extraction_provenance(self):
        """Test extraction provenance factory."""
        prov = create_extraction_provenance(
            "extractor",
            "doc_1",
            parent_ids=["chunk_1", "chunk_2"],
        )
        assert prov.source_type == "extraction"
        assert prov.confidence == 0.9
        assert len(prov.parent_ids) == 2

    def test_create_user_provenance(self):
        """Test user provenance factory."""
        prov = create_user_provenance("user_123")
        assert prov.author_id == "user_123"
        assert prov.source_type == "user"
        assert prov.confidence == 1.0
```

### 6.2 Integration Test

```python
"""Integration test for multi-agent provenance."""

import pytest

from friday_memory.controller import MemoryController
from friday_memory.models.graph import GraphNode, create_agent_provenance


@pytest.mark.asyncio
async def test_multi_agent_provenance(memory_controller):
    """Test provenance tracking across agents."""
    controller = memory_controller

    # Agent A stores a fact
    controller.set_author("researcher")
    node_a = GraphNode(
        id="fact_1",
        label="AI Fact",
        node_type="fact",
        content="AI is advancing rapidly",
    )
    await controller.store_fact(node_a)

    # Agent B stores a fact
    controller.set_author("coder")
    node_b = GraphNode(
        id="fact_2",
        label="Code Fact",
        node_type="fact",
        content="Python is popular",
    )
    await controller.store_fact(node_b)

    # Query by author
    researcher_facts = await controller.get_facts_by_author("researcher")
    coder_facts = await controller.get_facts_by_author("coder")

    assert len(researcher_facts) == 1
    assert researcher_facts[0].provenance.author_id == "researcher"

    assert len(coder_facts) == 1
    assert coder_facts[0].provenance.author_id == "coder"
```

### 6.3 Manual Test

```python
# Test provenance in memory-chat-v2
from friday_cli.container import FridayContainer

container = FridayContainer(config)

# Switch agents and store facts
# Agent 1
container.memory.set_author("researcher")
await container.memory.store_fact(...)

# Agent 2
container.memory.set_author("coder")
await container.memory.store_fact(...)

# Query transcript
entries = await container.transcript_store.get_entries_by_agent(
    session_id, "researcher"
)
print(f"Researcher entries: {len(entries)}")
```

---

## 7. Exit Criteria

1. `ProvenanceMetadata` validates `author_id` is non-empty
2. `MemoryController.set_author()` sets default author
3. All memory writes include author attribution
4. `TranscriptEntry` includes `agent_id` field
5. SQLite migration adds `agent_id` column
6. `AgentBase` sets author on session initialization
7. Can query memories/transcripts by author
8. Unit tests achieve 90%+ coverage
9. Empty author_id raises validation error
