# Friday-Memory Thread Safety Enhancement Plan

## Overview

The friday-memory package currently has **no thread safety guarantees**. This plan adds internal locks to protect shared state, enabling safe concurrent access from multiple async tasks or threads.

## Current State

| Component | Thread Safe | Critical Issues |
|-----------|-------------|-----------------|
| MemoryController | No | Unprotected `_primed_content`, `_session_turn_counts` |
| Graph Store | No | NetworkX not thread-safe; hit_count race conditions |
| Episodic Store | No | Dict/list mutations unprotected |
| Vector Store | Partial | ChromaDB limited concurrent write support |

## Goals

1. **Enable concurrent async access** - Multiple `asyncio` tasks can safely use the same MemoryController
2. **Enable multi-threaded access** - Multiple OS threads can safely use the same MemoryController
3. **Maintain backward compatibility** - No API changes required
4. **Minimize performance impact** - Fine-grained locks, not global serialization

## Architecture

### Lock Hierarchy

To prevent deadlocks, locks must always be acquired in this order:

```
1. MemoryController._state_lock      (session state, priming)
   └── 2. GraphStoreAdapter._lock    (graph mutations)
   └── 3. EpisodicStoreAdapter._lock (turn storage)
   └── 4. VectorStoreAdapter._lock   (vector operations)
```

### Lock Types

| Lock | Type | Scope | Protects |
|------|------|-------|----------|
| `_state_lock` | `asyncio.Lock` | MemoryController | `_primed_content`, `_session_turn_counts` |
| `_graph_lock` | `threading.RLock` | GraphStoreAdapter | NetworkX graph, file I/O |
| `_episodic_lock` | `asyncio.Lock` | EpisodicStoreAdapter | `_sessions` dict |
| `_vector_lock` | `asyncio.Lock` | VectorStoreAdapter | ChromaDB operations |

**Why RLock for Graph?**
- NetworkX operations are synchronous (not async)
- `merge_nodes()` calls `_save()` internally (reentrant)
- RLock allows same thread to acquire lock multiple times

## Implementation Plan

### Phase 1: MemoryController State Protection

**File:** `packages/friday-memory/src/friday_memory/controller/memory_controller.py`

#### Changes Required

1. **Add lock initialization** (~5 lines)
```python
def __init__(self, ...):
    # ... existing init ...
    self._state_lock = asyncio.Lock()
```

2. **Protect `_ensure_session_primed()`** (lines 228-257)
```python
async def _ensure_session_primed(self, session_id: str) -> None:
    async with self._state_lock:
        if session_id in self._primed_content:
            return
        # ... rest of priming logic ...
        self._primed_content[session_id] = (entities, insights, summaries, relationships)
```

3. **Protect turn count increment in `add_turn()`** (lines 978-982)
```python
async with self._state_lock:
    self._session_turn_counts[session_id] = (
        self._session_turn_counts.get(session_id, 0) + 1
    )
```

4. **Protect primed content access in `recall()`** (lines 99-227)
```python
async with self._state_lock:
    primed = self._primed_content.get(session_id)
# Use primed data outside lock (it's a tuple, immutable reference)
```

#### Methods to Modify

| Method | Lines | Lock Scope |
|--------|-------|------------|
| `__init__` | ~50 | Add lock init |
| `_ensure_session_primed` | 228-257 | Entire method |
| `recall` | 99-227 | Primed content access only |
| `add_turn` | 963-984 | Turn count increment |
| `prime_context` | 259-350 | Primed content write |

---

### Phase 2: Graph Store Protection

**File:** `packages/friday-memory/src/friday_memory/adapters/graph.py`

#### Changes Required

1. **Add lock initialization**
```python
import threading

class NetworkXGraphAdapter:
    def __init__(self, ...):
        # ... existing init ...
        self._lock = threading.RLock()
```

2. **Protect all graph mutations**
```python
def add_node(self, node: GraphNode) -> str:
    with self._lock:
        # ... existing implementation ...
        self._save()
    return node.id
```

3. **Atomic file save** (replace current `_save()`)
```python
def _save(self) -> None:
    """Atomically save graph to disk."""
    with self._lock:
        # Write to temp file first
        temp_path = self._path.with_suffix('.tmp')
        with open(temp_path, 'w') as f:
            data = nx.node_link_data(self._graph)
            json.dump(data, f, indent=2, default=str)
        # Atomic rename
        temp_path.replace(self._path)
```

4. **Safe iteration with snapshot**
```python
def get_all_nodes(self) -> list[GraphNode]:
    with self._lock:
        # Take snapshot of node IDs to avoid iteration issues
        node_ids = list(self._graph.nodes())

    # Build results outside lock
    return [self._node_to_graphnode(nid) for nid in node_ids]
```

#### Methods to Modify

| Method | Lines | Lock Scope | Notes |
|--------|-------|------------|-------|
| `__init__` | ~30 | Add lock init | |
| `add_node` | 108-127 | Entire method | Includes save |
| `update_node` | 129-151 | Entire method | Includes save |
| `delete_node` | 181-200 | Entire method | Includes save |
| `add_edge` | 153-179 | Entire method | Includes save |
| `delete_edge` | 266-295 | Entire method | Includes save |
| `get_neighbors` | 202-264 | Hit count update only | Read can be unlocked |
| `merge_nodes` | 297-347 | Entire method | Complex, needs RLock |
| `fuzzy_search` | 349-386 | Snapshot node list | |
| `rank_nodes` | 388-417 | Snapshot node list | |
| `find_by_label` | 488-510 | Snapshot node list | |
| `_save` | ~520 | Entire method | Make atomic |
| `get_all_nodes` | ~450 | Snapshot node list | |

---

### Phase 3: Episodic Store Protection

**File:** `packages/friday-memory/src/friday_memory/adapters/episodic.py`

#### Changes Required

1. **Add lock initialization**
```python
class InMemoryEpisodicAdapter:
    def __init__(self):
        self._sessions: dict[str, list[InteractionTurn]] = {}
        self._lock = asyncio.Lock()
```

2. **Protect session mutations**
```python
async def add_turn(self, session_id: str, turn: InteractionTurn) -> None:
    async with self._lock:
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append(turn)
```

3. **Protect mark_consolidated with snapshot**
```python
async def mark_consolidated(self, turn_ids: list[str]) -> int:
    turn_id_set = set(turn_ids)
    marked_count = 0

    async with self._lock:
        for turns in self._sessions.values():
            for turn in turns:
                if turn.id in turn_id_set and not turn.consolidated:
                    turn.consolidated = True
                    marked_count += 1

    return marked_count
```

#### Methods to Modify

| Method | Lines | Lock Scope |
|--------|-------|------------|
| `__init__` | ~20 | Add lock init |
| `add_turn` | 45-52 | Entire method |
| `get_turns` | 54-75 | Read with lock, return copy |
| `get_unconsolidated_turns` | 77-93 | Read with lock, return copy |
| `mark_consolidated` | 95-118 | Entire method |
| `rewind_history` | 120-160 | Entire method |
| `clear_session` | 168-173 | Entire method |

---

### Phase 4: Vector Store Protection

**File:** `packages/friday-memory/src/friday_memory/adapters/vector.py`

#### Changes Required

1. **Add lock initialization**
```python
class ChromaVectorAdapter:
    def __init__(self, ...):
        # ... existing init ...
        self._lock = asyncio.Lock()
```

2. **Protect write operations**
```python
async def add_documents(self, documents: list[Document]) -> list[str]:
    async with self._lock:
        # ... existing implementation ...
```

3. **Protect delete operations**
```python
async def delete(self, ids: list[str]) -> int:
    async with self._lock:
        # ... existing implementation ...
```

#### Methods to Modify

| Method | Lines | Lock Scope | Notes |
|--------|-------|------------|-------|
| `__init__` | ~50 | Add lock init | |
| `add_documents` | 107-150 | Entire method | Write operation |
| `delete` | 221-240 | Entire method | Write operation |
| `delete_where` | 242-268 | Entire method | Write operation |
| `query` | 152-219 | Optional | Reads generally safe |

---

## Testing Strategy

### Unit Tests

**File:** `packages/friday-memory/tests/test_thread_safety.py`

```python
import asyncio
import pytest
from concurrent.futures import ThreadPoolExecutor

class TestMemoryControllerThreadSafety:

    @pytest.mark.asyncio
    async def test_concurrent_turn_increments(self, memory_controller):
        """Verify turn counts are not lost under concurrent access."""
        session_id = "test-session"
        num_tasks = 100

        async def add_turn_task():
            turn = InteractionTurn(...)
            await memory_controller.add_turn(session_id, turn)

        # Run 100 concurrent add_turn calls
        await asyncio.gather(*[add_turn_task() for _ in range(num_tasks)])

        # Verify all increments were recorded
        assert memory_controller._session_turn_counts[session_id] == num_tasks

    @pytest.mark.asyncio
    async def test_concurrent_priming(self, memory_controller):
        """Verify session is only primed once under concurrent access."""
        session_id = "test-session"
        prime_count = 0

        original_prime = memory_controller.prime_context
        async def counting_prime(*args, **kwargs):
            nonlocal prime_count
            prime_count += 1
            return await original_prime(*args, **kwargs)

        memory_controller.prime_context = counting_prime

        # 10 concurrent recall calls
        await asyncio.gather(*[
            memory_controller.recall("test query", session_id, 1000)
            for _ in range(10)
        ])

        # Should only prime once
        assert prime_count == 1


class TestGraphStoreThreadSafety:

    def test_concurrent_hit_count_increments(self, graph_adapter):
        """Verify hit counts are not lost under concurrent access."""
        node = GraphNode(id="test", label="Test", type="concept")
        graph_adapter.add_node(node)

        num_threads = 50

        def increment_hit_count():
            graph_adapter.get_neighbors("test", direction="both")

        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(lambda _: increment_hit_count(), range(num_threads)))

        # Verify all increments recorded
        node_data = graph_adapter.get_node("test")
        assert node_data.properties.get("hit_count", 0) == num_threads

    def test_concurrent_node_operations(self, graph_adapter):
        """Verify no crashes under concurrent add/delete."""
        errors = []

        def add_delete_cycle(i):
            try:
                node = GraphNode(id=f"node-{i}", label=f"Node {i}", type="concept")
                graph_adapter.add_node(node)
                graph_adapter.delete_node(f"node-{i}")
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(add_delete_cycle, range(100)))

        assert len(errors) == 0


class TestEpisodicStoreThreadSafety:

    @pytest.mark.asyncio
    async def test_concurrent_mark_consolidated(self, episodic_adapter):
        """Verify consolidated flags are set correctly under concurrent access."""
        session_id = "test"
        turns = [InteractionTurn(id=f"turn-{i}", ...) for i in range(100)]

        for turn in turns:
            await episodic_adapter.add_turn(session_id, turn)

        # Concurrently mark different subsets
        turn_ids = [t.id for t in turns]
        await asyncio.gather(
            episodic_adapter.mark_consolidated(turn_ids[:50]),
            episodic_adapter.mark_consolidated(turn_ids[25:75]),
            episodic_adapter.mark_consolidated(turn_ids[50:]),
        )

        # All should be marked
        remaining = await episodic_adapter.get_unconsolidated_turns(session_id)
        assert len(remaining) == 0
```

### Stress Tests

```python
class TestStressScenarios:

    @pytest.mark.asyncio
    async def test_high_concurrency_mixed_operations(self, memory_controller):
        """Simulate production load with mixed read/write operations."""
        num_clients = 20
        ops_per_client = 50
        errors = []

        async def client_workload(client_id):
            session_id = f"session-{client_id}"
            try:
                for i in range(ops_per_client):
                    # Mix of operations
                    if i % 3 == 0:
                        await memory_controller.recall(f"query {i}", session_id, 1000)
                    elif i % 3 == 1:
                        turn = InteractionTurn(...)
                        await memory_controller.add_turn(session_id, turn)
                    else:
                        await memory_controller.store(
                            content=f"fact {i}",
                            session_id=session_id,
                            source_type="test"
                        )
            except Exception as e:
                errors.append((client_id, e))

        await asyncio.gather(*[client_workload(i) for i in range(num_clients)])

        assert len(errors) == 0, f"Errors occurred: {errors}"
```

---

## Implementation Order

### Step 1: MemoryController (Foundation)
- Add `_state_lock`
- Protect `_ensure_session_primed()`, `add_turn()`, `recall()`
- **Test:** Concurrent turn increments, concurrent priming

### Step 2: Graph Store (Highest Risk)
- Add `threading.RLock`
- Protect all mutation methods
- Implement atomic save
- **Test:** Concurrent hit counts, concurrent add/delete

### Step 3: Episodic Store
- Add `asyncio.Lock`
- Protect session mutations
- Return copies from read methods
- **Test:** Concurrent mark_consolidated, concurrent rewind

### Step 4: Vector Store
- Add `asyncio.Lock`
- Protect write operations
- **Test:** Concurrent add_documents, concurrent delete

### Step 5: Integration Testing
- Run full stress tests
- Verify no deadlocks
- Performance benchmarking

---

## Files to Modify

| File | Changes | Lines Added |
|------|---------|-------------|
| `controller/memory_controller.py` | Add lock, protect 5 methods | ~30 |
| `adapters/graph.py` | Add RLock, protect 12 methods, atomic save | ~60 |
| `adapters/episodic.py` | Add lock, protect 6 methods | ~25 |
| `adapters/vector.py` | Add lock, protect 3 methods | ~15 |
| `tests/test_thread_safety.py` | New file with concurrency tests | ~200 |

**Total:** ~330 lines of changes

---

## Performance Considerations

### Lock Contention Mitigation

1. **Hold locks briefly** - Do work outside locks when possible
2. **Read-copy pattern** - Take snapshot inside lock, process outside
3. **Fine-grained locks** - Separate locks per adapter, not global

### Benchmarks to Track

| Metric | Baseline | Target |
|--------|----------|--------|
| Single-client recall latency | Xms | <1.1X ms |
| 10-client concurrent recall | N/A | <2X single |
| Turn add throughput | Y/sec | >0.8Y/sec |

---

## Rollout Plan

1. **Feature flag** - Add `thread_safe=True` parameter to MemoryController
2. **Opt-in first** - Default to `thread_safe=False` for backward compat
3. **Deprecation** - Warn when `thread_safe=False` and concurrent access detected
4. **Default on** - Change default to `thread_safe=True` in next minor version

---

## Design Decisions

1. **asyncio.Lock vs threading.Lock**: Use `asyncio.Lock` for async adapters, `threading.RLock` for sync graph operations

2. **Lock granularity**: Per-adapter locks (fine-grained) rather than global lock (coarse)

3. **Atomic saves**: Use temp file + rename pattern for crash safety

4. **Read operations**: Generally unlocked for performance, except when iterating mutable collections

5. **Return copies**: Read methods return copies/snapshots to prevent mutation outside locks

6. **RLock for Graph**: Needed because `merge_nodes()` calls `_save()` internally (reentrant)
