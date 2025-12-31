# Phase I Build Plan: `packages/friday-core`

This document provides the implementation plan for Phase I of the Friday Framework build, covering the `friday-core` package.

## Summary

**Status:** Ready to execute

The Batch 0 and Batch 1 specifications provide sufficient detail for implementation. Three specification gaps were identified and resolved through design decisions documented below.

---

## Gap Resolutions

### GAP 1: `telemetry.py` - Incomplete Span Lifecycle

**Problem:** Batch 0 §4.3 defines `start_span()` but not how to end spans or what it returns.

**Resolution:** Add `end_span()` method with span_id return pattern.

**Complete Interface:**
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class TelemetryInterface(ABC):
    @abstractmethod
    def capture_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """Records a discrete event (e.g., 'memory_recall', 'tool_usage')."""
        pass

    @abstractmethod
    def start_span(self, name: str, parent_id: Optional[str] = None) -> str:
        """Starts a trace span. Returns span_id for tracking."""
        pass

    @abstractmethod
    def end_span(self, span_id: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Ends a span, optionally attaching final data (latency, result)."""
        pass


class DebugTelemetryRecorder(TelemetryInterface):
    """In-memory recorder for white-box testing."""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.spans: Dict[str, Dict[str, Any]] = {}

    def capture_event(self, event_name: str, data: Dict[str, Any]) -> None:
        self.events.append({"name": event_name, "data": data})

    def start_span(self, name: str, parent_id: Optional[str] = None) -> str:
        import uuid
        span_id = str(uuid.uuid4())
        self.spans[span_id] = {"name": name, "parent_id": parent_id, "ended": False}
        return span_id

    def end_span(self, span_id: str, data: Optional[Dict[str, Any]] = None) -> None:
        if span_id in self.spans:
            self.spans[span_id]["ended"] = True
            if data:
                self.spans[span_id]["data"] = data

    def get_event(self, event_name: str) -> Optional[Dict[str, Any]]:
        """Helper for test assertions."""
        for event in self.events:
            if event["name"] == event_name:
                return event["data"]
        return None
```

---

### GAP 2: `logging.py` - Undefined Logger Interface

**Problem:** Batch 0 §4.1 mentions `get_logger(name)` factory but doesn't specify the logger's interface.

**Resolution:** Define `LoggerProtocol` with standard logging methods.

**Complete Interface:**
```python
from typing import Protocol, Any
import structlog

class LoggerProtocol(Protocol):
    """Abstract logger interface for swappability."""
    def debug(self, msg: str, **context: Any) -> None: ...
    def info(self, msg: str, **context: Any) -> None: ...
    def warning(self, msg: str, **context: Any) -> None: ...
    def error(self, msg: str, **context: Any) -> None: ...
    def exception(self, msg: str, **context: Any) -> None: ...


def get_logger(name: str, environment: str = "development") -> LoggerProtocol:
    """
    Factory function for structured loggers.

    Args:
        name: Logger name (typically __name__)
        environment: "production" for JSON, "development" for colored console

    Returns:
        A logger conforming to LoggerProtocol
    """
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if environment == "production":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )

    return structlog.get_logger(name)
```

---

### GAP 3: `interfaces/context.py` - Not Specified in Batch 0-1

**Problem:** Build plan references `ContextEngineeringInterface` but it's not defined until Batch 2a.

**Resolution:** Extract interface from Batch 2a §1.1 for upfront definition.

**Complete Interface:**
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any  # Forward references resolved at runtime

class ContextEngineeringInterface(ABC):
    """
    The Master Protocol for Context Engineering.
    Implements the lifecycle defined in Batch 2a specifications.

    Forward references (SessionState, ConsolidationReport, ContextPayload, Interaction)
    will be defined in friday-memory/models/.
    """

    @abstractmethod
    async def initialize_session(self, session_id: str, user_id: str) -> 'SessionState':
        """Loads or creates the session context, establishing the 'Thread'."""
        pass

    @abstractmethod
    async def restore_checkpoint(self, session_id: str, turn_id: str) -> 'SessionState':
        """
        Reverts the session state to a previous turn.
        Triggers MemoryController.rollback_session() and reloads state.
        """
        pass

    @abstractmethod
    async def extract_context(
        self,
        interaction_turn: 'Interaction',
        async_execution: bool = True
    ) -> None:
        """
        Analyzes the last turn to identify 'Hot' facts or memories.
        Triggers 'Memory Generation' (Extraction) tasks.
        """
        pass

    @abstractmethod
    async def consolidate_memory(self, session_id: str) -> 'ConsolidationReport':
        """
        Merges fragmented short-term memories into solidified long-term blocks.
        Resolves conflicts and summarizes 'drift'.
        """
        pass

    @abstractmethod
    async def assemble_context(
        self,
        query: str,
        state: 'SessionState',
        budget_limit: int
    ) -> 'ContextPayload':
        """
        The core 'Recall' step.
        Selects, Ranks, and Compresses data into the Context Window.

        Supports both Passive (user query) and Active (agent-generated) search.
        """
        pass

    @abstractmethod
    async def format_prompt(
        self,
        system_prompt: str,
        payload: 'ContextPayload'
    ) -> List[Dict[str, Any]]:
        """
        Physically arranges the messages (System, Tools, Context, User)
        to optimize for the specific model's attention span.
        """
        pass
```

---

## Implementation Checklist

### Files to Implement

| File | Spec Source | Dependencies |
|------|-------------|--------------|
| `config.py` | Batch 0 §3.1 | pydantic-settings |
| `exceptions.py` | Batch 0 §4.2 | None |
| `logging.py` | Batch 0 §4.1 + Gap Resolution | structlog |
| `telemetry.py` | Batch 0 §4.3 + Gap Resolution | None |
| `interfaces/memory.py` | Batch 1 §1 | exceptions.py |
| `interfaces/context.py` | Batch 2a §1.1 | None (forward refs) |
| `interfaces/__init__.py` | - | All interfaces |
| `__init__.py` | - | All modules |

### Build Order

```
1. config.py           (foundation - no internal deps)
2. exceptions.py       (foundation - no internal deps)
3. logging.py          (may use config for environment)
4. telemetry.py        (standalone)
5. interfaces/memory.py (may raise exceptions)
6. interfaces/context.py (forward references only)
7. interfaces/__init__.py (exports protocols)
8. __init__.py         (exports public API)
```

---

## Detailed Specifications

### 1. `config.py` (Batch 0 §3.1)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class FridayBaseSettings(BaseSettings):
    """Global settings inherited by all packages."""
    APP_ENV: str = "development"  # development | production | testing
    LOG_LEVEL: str = "INFO"
    DEFAULT_MODEL: str = "gpt-4-turbo"
    OPENAI_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
```

### 2. `exceptions.py` (Batch 0 §4.2)

```python
class FridayError(Exception):
    """Root exception for Friday Framework."""
    pass

class MemoryError(FridayError):
    """Base for database/storage failures."""
    pass

class ContextOverflowError(FridayError):
    """Raised when Context Budget is impossible to satisfy."""
    pass

class ProviderAPIError(FridayError):
    """LLM provider failures."""
    pass
```

### 3. `interfaces/memory.py` (Batch 1 §1)

Three adapter protocols:

**EpisodicStoreAdapter:**
- `add_turn(session_id, turn) -> bool`
- `get_turns(session_id, limit=10, offset=0) -> List[InteractionTurn]`
- `get_unconsolidated_turns(session_id) -> List[InteractionTurn]`
- `mark_consolidated(turn_ids) -> bool`
- `rewind_history(session_id, target_turn_id) -> bool`

**VectorStoreAdapter:**
- `add_documents(texts, metadatas, ids) -> bool`
- `query(query_text, n_results=5, where=None, rerank=False, hybrid=False) -> List[Dict]`
- `delete(ids) -> bool`
- `delete_where(where) -> int`

**GraphStoreAdapter:**
- `add_node(node) -> bool`
- `add_edge(edge) -> bool`
- `remove_node(node_id) -> bool`
- `get_neighbors(node_id, depth=1) -> List[Dict]`
- `find_path(start_id, end_id, max_depth=5) -> List[str]`
- `merge_nodes(primary_id, secondary_id) -> bool`
- `fuzzy_search(query, threshold=0.8) -> List[GraphNode]`
- `rank_nodes(algorithm="pagerank") -> List[Dict]`

---

## Testing Requirements (Batch 0 §7)

1. **Repo Setup:** `uv sync` creates venv and installs all workspace members
2. **Import Test:** `friday-cli` can import from `friday-memory` without path hacking
3. **Config Test:** `.env` with `LOG_LEVEL=DEBUG` reflected in `FridayBaseSettings`
4. **Lint Check:** `uv run ruff check .` passes
5. **Injection Test:** `MemoryController` initializable with mock config (no .env dependency)
6. **Telemetry Test:** `DebugTelemetryRecorder` captures events when injected

---

## Public API Exports

### `friday_core/__init__.py`

```python
from friday_core.config import FridayBaseSettings
from friday_core.exceptions import (
    FridayError,
    MemoryError,
    ContextOverflowError,
    ProviderAPIError,
)
from friday_core.logging import LoggerProtocol, get_logger
from friday_core.telemetry import TelemetryInterface, DebugTelemetryRecorder
from friday_core.interfaces import (
    EpisodicStoreAdapter,
    VectorStoreAdapter,
    GraphStoreAdapter,
    ContextEngineeringInterface,
)

__all__ = [
    "FridayBaseSettings",
    "FridayError",
    "MemoryError",
    "ContextOverflowError",
    "ProviderAPIError",
    "LoggerProtocol",
    "get_logger",
    "TelemetryInterface",
    "DebugTelemetryRecorder",
    "EpisodicStoreAdapter",
    "VectorStoreAdapter",
    "GraphStoreAdapter",
    "ContextEngineeringInterface",
]
```
