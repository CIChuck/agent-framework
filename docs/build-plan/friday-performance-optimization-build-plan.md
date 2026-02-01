# Build Plan: Friday.py Performance Optimization

**Status:** Planned
**Priority:** Critical
**Target:** Immediate
**Document Version:** 1.0
**Author:** Claude (Performance Analysis)
**Date:** 2026-01-28

---

## Executive Summary

The `friday.py` chat application suffers from severe latency issues causing 60+ second timeouts and poor user experience. This build plan addresses the root causes: synchronous blocking operations that consume the timeout window before the actual LLM HTTP request is dispatched.

**Key Finding:** The configured 60-second timeout is being exhausted by pre-processing operations, leaving insufficient time for the actual LLM API call.

---

## 1. Problem Statement

### 1.1 Observed Symptoms

Users experience three distinct latency issues:

| Symptom | User Experience | Frequency |
|---------|-----------------|-----------|
| **Prompt Acceptance Lag** | Delay between pressing Enter and seeing "thinking" indicator | Every turn |
| **Response Display Lag** | Delay between LLM completion and text appearing | Every turn |
| **Timeout Failures** | 60-second timeout errors despite responsive LLM vendor | Frequent (>50% of turns) |

### 1.2 System Context

The `friday.py` application is an AI chat interface with persistent memory capabilities. Each user turn triggers:

1. **Context Assembly** - Retrieval from 3 memory stores (episodic, vector, graph)
2. **Prompt Construction** - Formatting retrieved context into LLM-ready messages
3. **LLM Inference** - HTTP request to cloud LLM provider
4. **Memory Extraction** - Background LLM call to extract entities/relationships
5. **Persistence** - SQLite transcript storage

### 1.3 Root Cause Analysis

#### Critical Finding: Timeout Scope Mismatch

The `timeout_seconds: 60` configuration in `config.yaml` only applies to the `litellm.acompletion()` HTTP call. However, significant processing occurs **before** this call, within the same async context:

```
User Input
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  PRE-HTTP PROCESSING (Consumes 27-80 seconds)           │
│                                                         │
│  1. Context Assembly (memory_controller.py)    10-30s   │
│     └── Includes embedding API call            5-15s    │
│  2. Prompt Formatting (layout.py)              2-5s     │
│  3. Token Counting (friday.py)                 10-30s   │
│                                                         │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  LLM HTTP REQUEST (Timeout starts here)                 │
│                                                         │
│  - Timeout: 60 seconds                                  │
│  - Remaining budget: 0-33 seconds (often negative!)     │
│                                                         │
└─────────────────────────────────────────────────────────┘
    │
    ▼
TIMEOUT FAILURE
```

#### Bottleneck #1: Token Counting (10-30 seconds)

**Location:** `tests/integration/memory/friday.py:929-978`

```python
def _estimate_context_size(self, messages: list[dict]) -> ContextMetrics:
    """Estimate context size in tokens."""
    for msg in messages:
        content = msg.get("content", "") or ""
        tokens = self.token_counter.count(content)  # BLOCKING
```

**Technical Cause:**
- `tiktoken.encode()` is a **synchronous, CPU-bound** operation
- For 25-30K tokens, encoding takes 10-30 seconds
- This is a **pure Python operation** that blocks the event loop
- Runs on **every turn**, even if context hasn't changed significantly

**Evidence:**
- `TokenCounter.count()` calls `self._encoding.encode(text)` synchronously
- No caching of previous token counts
- No async offloading to thread pool

#### Bottleneck #2: Query Embedding API (5-15 seconds)

**Location:** `packages/friday-memory/src/friday_memory/adapters/vector.py:186`

```python
async def query(self, query_text: str, ...) -> list[dict]:
    query_embedding = (await self._get_embeddings([query_text]))[0]  # HTTP CALL
    results = self._collection.query(query_embeddings=[query_embedding], ...)
```

**Technical Cause:**
- Each vector search requires an embedding of the query text
- `_get_embeddings()` makes an HTTP call to the embedding model API
- This is a **separate network round-trip** (5-15 seconds depending on provider)
- Same query text generates identical embeddings—no caching implemented

**Evidence:**
- `LiteLLMEmbeddingService.embed_documents()` calls `litellm.acompletion()`
- No LRU cache or memoization on query strings
- Multiple vector queries per turn compound this latency

#### Bottleneck #3: Post-Response Blocking (50-200ms)

**Location:** `tests/integration/memory/friday.py:4100-4109`

```python
# These block response display
success = await self.controller.add_turn(self.session_id, turn)  # BLOCKING
if self.tool_content_manager:
    decayed = await self.tool_content_manager.check_and_decay(...)  # BLOCKING

# Only then does extraction start (non-blocking)
if self.extractor:
    asyncio.create_task(self._background_extract(turn))
```

**Technical Cause:**
- `await self.controller.add_turn()` blocks on SQLite write
- `await self.tool_content_manager.check_and_decay()` may trigger LLM summarization
- Response is not displayed until both complete

#### Bottleneck #4: Extraction Frequency (1-5 seconds per turn, accumulates)

**Location:** `tests/integration/memory/friday.py:4125-4127`

```python
if self.extractor:
    asyncio.create_task(self._background_extract(turn))  # EVERY TURN
```

**Technical Cause:**
- Extraction triggers a **full LLM inference call** (separate from chat)
- Runs after **every single turn** with no batching or throttling
- Multiple background tasks can run concurrently without coordination
- Resource contention degrades subsequent turn performance

### 1.4 Impact Assessment

| Impact Area | Severity | Description |
|-------------|----------|-------------|
| User Experience | **Critical** | 60+ second waits, timeout errors destroy usability |
| Resource Utilization | **High** | Redundant embedding calls, wasted LLM inference |
| Scalability | **High** | Background task accumulation creates resource contention |
| Cost | **Medium** | Unnecessary embedding and extraction API calls |

---

## 2. Proposed Solution

### 2.1 Solution Overview

Four targeted changes to eliminate the identified bottlenecks:

| Change | Target Bottleneck | Expected Improvement |
|--------|-------------------|---------------------|
| Skip/defer token counting | Bottleneck #1 | -10-30 seconds |
| Cache query embeddings | Bottleneck #2 | -5-15 seconds |
| Non-blocking post-response ops | Bottleneck #3 | -50-200ms |
| Configurable extraction interval | Bottleneck #4 | -80% background load |

### 2.2 Design Principles

1. **Preserve Correctness** - No functional changes to memory retrieval or LLM behavior
2. **Graceful Degradation** - If caching fails, fall back to existing behavior
3. **Configurability** - Allow users to tune trade-offs via config.yaml
4. **Observability** - Log timing metrics for future optimization

---

## 3. Implementation Plan

### 3.1 Change 1: Skip Token Counting

**Rationale:** The `_estimate_context_size()` function provides diagnostic metrics but is not required for LLM functionality. The token count does not affect the prompt sent to the LLM.

**Files Modified:**
- `tests/integration/memory/friday.py`

**Implementation:**

```python
# Location: friday.py:4178 (in _process_streaming method)

# BEFORE:
context_metrics = self._estimate_context_size(messages)

# AFTER:
# Skip token counting - diagnostic only, not functional
# Token counting via tiktoken is CPU-bound and takes 10-30s for large prompts
context_metrics = ContextMetrics(
    total_tokens=0,  # Placeholder - not used for LLM call
    system_tokens=0,
    history_tokens=0,
    context_tokens=0,
)
# Optionally log that counting was skipped for debugging
logger.debug("Token counting skipped for performance (diagnostic only)")
```

**Alternative Implementation (Background Counting):**

If metrics are needed for logging/monitoring:

```python
# Run token counting in background thread (non-blocking)
async def _background_count_tokens(self, messages: list[dict]) -> None:
    """Count tokens in background for metrics only."""
    loop = asyncio.get_event_loop()
    metrics = await loop.run_in_executor(None, self._estimate_context_size, messages)
    logger.info(f"Context size: {metrics.total_tokens} tokens (computed in background)")

# In _process_streaming:
asyncio.create_task(self._background_count_tokens(messages))
```

**Verification:**
1. Run friday.py with a 25K+ token context
2. Measure time from Enter to LLM stream start
3. Expected: <15 seconds (down from 27-80 seconds)

---

### 3.2 Change 2: Cache Query Embeddings

**Rationale:** The same query string always produces the same embedding vector. Caching eliminates redundant API calls for repeated or similar queries.

**Files Modified:**
- `packages/friday-memory/src/friday_memory/adapters/vector.py`

**Implementation:**

```python
# Location: vector.py (add near top of ChromaVectorStore class)

from functools import lru_cache
from typing import Tuple
import hashlib

class ChromaVectorStore:
    def __init__(self, ...):
        # ... existing init ...

        # Embedding cache (100 most recent queries)
        self._embedding_cache: dict[str, list[float]] = {}
        self._embedding_cache_maxsize = 100

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key from query text."""
        return hashlib.md5(text.encode()).hexdigest()

    async def _get_cached_embedding(self, query_text: str) -> list[float]:
        """Get embedding from cache or generate new one."""
        cache_key = self._get_cache_key(query_text)

        # Check cache first
        if cache_key in self._embedding_cache:
            logger.debug(f"Embedding cache HIT for query: {query_text[:50]}...")
            return self._embedding_cache[cache_key]

        # Cache miss - generate embedding
        logger.debug(f"Embedding cache MISS for query: {query_text[:50]}...")
        embedding = (await self._get_embeddings([query_text]))[0]

        # Store in cache (with LRU eviction)
        if len(self._embedding_cache) >= self._embedding_cache_maxsize:
            # Remove oldest entry (first key in dict - Python 3.7+ preserves order)
            oldest_key = next(iter(self._embedding_cache))
            del self._embedding_cache[oldest_key]

        self._embedding_cache[cache_key] = embedding
        return embedding

    # Location: vector.py:186 (in query method)
    async def query(self, query_text: str, ...) -> list[dict]:
        # BEFORE:
        # query_embedding = (await self._get_embeddings([query_text]))[0]

        # AFTER:
        query_embedding = await self._get_cached_embedding(query_text)

        # ... rest of method unchanged ...
```

**Verification:**
1. Run friday.py and submit the same query twice
2. Second query should show "cache HIT" in debug logs
3. Measure embedding latency: first query 5-15s, second query <1ms

---

### 3.3 Change 3: Configurable Extraction Interval

**Rationale:** Extracting after every turn creates excessive background LLM load. Batching extraction reduces API calls while maintaining memory freshness.

**Files Modified:**
- `tests/integration/memory/config.yaml`
- `tests/integration/memory/friday.py`

**Config Change:**

```yaml
# Location: config.yaml - add under existing 'extraction:' section

extraction:
  # ... existing settings ...

  # Extraction interval: how often to run background extraction
  # 0 = every turn (current behavior)
  # N > 0 = every N turns
  # -1 = session exit only (maximum batching)
  interval: 5
```

**Code Change:**

```python
# Location: friday.py (add helper method to MemoryChatSession class)

def _should_extract(self, turn_count: int) -> bool:
    """Determine if extraction should run based on interval config."""
    interval = self.tools_config.get("extraction", {}).get("interval", 0)

    if interval == 0:
        return True  # Every turn (legacy behavior)
    elif interval == -1:
        return False  # Only on session exit
    else:
        return turn_count % interval == 0

# Location: friday.py:4125-4127 (in process_turn method)

# BEFORE:
if self.extractor:
    asyncio.create_task(self._background_extract(turn))
    get_console().print("  [dim][Extraction started in background][/dim]")

# AFTER:
if self.extractor:
    turn_count = len(self.turn_ids)
    if self._should_extract(turn_count):
        asyncio.create_task(self._background_extract(turn))
        get_console().print("  [dim][Extraction started in background][/dim]")
    else:
        interval = self.tools_config.get("extraction", {}).get("interval", 0)
        next_extraction = interval - (turn_count % interval)
        get_console().print(f"  [dim][Extraction deferred - {next_extraction} turns until next][/dim]")
```

**Session Exit Extraction:**

```python
# Location: friday.py - add to session cleanup/exit handler

async def _extract_pending_turns(self) -> None:
    """Extract any turns that were deferred during the session."""
    if not self.extractor:
        return

    interval = self.tools_config.get("extraction", {}).get("interval", 0)
    if interval <= 0:
        return  # No deferred turns

    # Find turns that weren't extracted
    pending_count = len(self.turn_ids) % interval
    if pending_count > 0:
        get_console().print(f"  [dim]Extracting {pending_count} deferred turns...[/dim]")
        # Batch extract remaining turns
        # Implementation depends on how turns are stored
```

**Verification:**
1. Set `extraction.interval: 5` in config.yaml
2. Run friday.py and chat for 6 turns
3. Confirm extraction runs only on turns 5 and 10 (not 1-4, 6-9)
4. Check logs for "Extraction deferred" messages

---

### 3.4 Change 4: Non-Blocking Post-Response Operations

**Rationale:** Transcript saves and decay checks should not block response display. These operations are important but not time-critical.

**Files Modified:**
- `tests/integration/memory/friday.py`

**Implementation:**

```python
# Location: friday.py:4100-4109 (in process_turn method)

# BEFORE:
# Persist to transcript (blocking)
success = await self.controller.add_turn(self.session_id, turn)
if not success:
    display_warning("Failed to persist turn to transcript store.")

# Tool content decay (blocking)
if self.tool_content_manager:
    current_turn_number = len(self.turn_ids)
    decayed = await self.tool_content_manager.check_and_decay(current_turn_number)
    if decayed:
        display_info(f"  [Decayed {len(decayed)} tool outputs]")

# AFTER:
# Fire-and-forget transcript persistence (non-blocking)
async def _persist_turn(turn: InteractionTurn) -> None:
    try:
        success = await self.controller.add_turn(self.session_id, turn)
        if not success:
            logger.warning("Failed to persist turn to transcript store.")
    except Exception as e:
        logger.error(f"Error persisting turn: {e}")

asyncio.create_task(_persist_turn(turn))

# Fire-and-forget tool content decay (non-blocking)
if self.tool_content_manager:
    async def _check_decay(turn_number: int) -> None:
        try:
            decayed = await self.tool_content_manager.check_and_decay(turn_number)
            if decayed:
                logger.info(f"Decayed {len(decayed)} tool outputs")
        except Exception as e:
            logger.error(f"Error in tool decay check: {e}")

    asyncio.create_task(_check_decay(len(self.turn_ids)))
```

**Safety Consideration:**

Fire-and-forget operations risk data loss on crash. For critical persistence, consider a hybrid approach:

```python
# Hybrid: Non-blocking with periodic sync
class PersistenceBuffer:
    def __init__(self, flush_interval: int = 5):
        self._pending: list[InteractionTurn] = []
        self._flush_interval = flush_interval

    def add(self, turn: InteractionTurn) -> None:
        self._pending.append(turn)
        if len(self._pending) >= self._flush_interval:
            asyncio.create_task(self._flush())

    async def _flush(self) -> None:
        """Persist all pending turns."""
        turns = self._pending.copy()
        self._pending.clear()
        for turn in turns:
            await self.controller.add_turn(self.session_id, turn)
```

**Verification:**
1. Run friday.py and measure time from LLM stream end to prompt reappearance
2. Expected: <100ms (down from 50-200ms)
3. Verify transcripts are still saved (check SQLite after session)

---

## 4. Files to Modify Summary

| File | Changes |
|------|---------|
| `tests/integration/memory/config.yaml` | Add `extraction.interval` setting |
| `tests/integration/memory/friday.py` | Skip token counting, extraction interval logic, non-blocking ops |
| `packages/friday-memory/src/friday_memory/adapters/vector.py` | Add embedding cache |

---

## 5. Testing Plan

### 5.1 Performance Benchmarks

| Metric | Current | Target | Measurement Method |
|--------|---------|--------|-------------------|
| Pre-prompt latency | 27-80s | <15s | Timestamp: Enter → first LLM token |
| Post-response latency | 50-200ms | <100ms | Timestamp: last LLM token → prompt return |
| Background LLM calls | N/turn | N/5 turns | Count extraction logs per session |
| Timeout rate | >50% | <5% | Count timeout errors per 20 turns |

### 5.2 Functional Verification

1. **Memory Retrieval:** Verify context assembly still returns relevant memories
2. **Extraction Quality:** Verify entities/relationships are still extracted correctly (just less frequently)
3. **Transcript Persistence:** Verify all turns are saved to SQLite after session
4. **Cache Correctness:** Verify cached embeddings produce same search results as uncached

### 5.3 Regression Tests

- Run existing test suite: `pytest tests/integration/memory/`
- Manual smoke test: 20-turn conversation without timeout failures
- Edge cases: Empty queries, very long queries, repeated queries

---

## 6. Rollback Plan

Each change is independent and can be rolled back individually:

| Change | Rollback Method |
|--------|-----------------|
| Skip token counting | Restore `context_metrics = self._estimate_context_size(messages)` |
| Embedding cache | Remove cache logic, restore direct `_get_embeddings()` call |
| Extraction interval | Set `extraction.interval: 0` in config.yaml |
| Non-blocking ops | Restore `await` keywords on transcript/decay operations |

---

## 7. Future Optimizations (Out of Scope)

The following optimizations were identified but deferred:

1. **Speculative Context Assembly** - Start assembly while user types
2. **Context Delta Computation** - Only re-assemble changed portions
3. **Lazy Memory Loading** - Load full content on-demand
4. **Parallel Prompt Formatting** - Format sections concurrently
5. **Connection Pooling** - Reuse HTTP connections for embedding calls

---

## 8. Success Criteria

This build plan is considered successful when:

- [ ] Pre-prompt latency is consistently <15 seconds for 25-30K token contexts
- [ ] No timeout failures occur during 20-turn test session
- [ ] Post-response latency is imperceptible to user (<100ms)
- [ ] Background LLM calls reduced by 80% (verified via logs)
- [ ] All existing tests pass
- [ ] Memory functionality is preserved (retrieval, extraction, persistence)

---

## Appendix A: Code Locations Reference

| Component | File | Line Numbers |
|-----------|------|--------------|
| Token counting | `friday.py` | 929-978, 4178 |
| Embedding generation | `vector.py` | 159-186 |
| Context assembly | `memory_controller.py` | 393-550 |
| Prompt formatting | `layout.py` | 143-192 |
| Extraction trigger | `friday.py` | 4125-4127 |
| Transcript persistence | `friday.py` | 4100 |
| Tool content decay | `friday.py` | 4105-4109 |

## Appendix B: Timing Diagram

```
CURRENT FLOW (27-80 seconds before LLM):
─────────────────────────────────────────────────────────────────────────
User Input ─┬─► Context Assembly ─► Embedding API ─► Vector Search ─┬─► Format ─► Token Count ─► LLM Call ─► Timeout
            │        10-30s            5-15s           <1s          │    2-5s      10-30s          0s
            │                                                        │
            └────────────────────────────────────────────────────────┘
                              TOTAL: 27-80 seconds

OPTIMIZED FLOW (5-15 seconds before LLM):
─────────────────────────────────────────────────────────────────────────
User Input ─┬─► Context Assembly ─► Cached Embed ─► Vector Search ─┬─► Format ─► [Skip] ─► LLM Call ─► Response
            │        10-30s            <1ms           <1s          │    2-5s      0s        Success
            │                                                        │
            └────────────────────────────────────────────────────────┘
                              TOTAL: 12-35 seconds (with cache hit: 5-15s)
```
