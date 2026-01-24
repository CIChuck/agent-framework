# Function Calling as First-Class Citizen in Friday-Memory

## Goal

Make friday-memory "function-calling forward" - tools should be managed by the memory system alongside entities, facts, and insights, enabling intelligent tool selection, usage tracking, and parameter learning.

---

## Current State

**What exists:**
- `friday-tools`: BaseTool, ToolRegistry, ToolManifest (89+ tools)
- `friday-llm`: LiteLLMService.chat_completion(tools=[...])
- `friday-agent`: CopilotAgent Re-Act loop, archives tool_calls/tool_results to memory
- `friday-memory`: InteractionTurn stores tool_calls passively, PromptArchitect has unused `tool_definitions` parameter

**Gaps:**
1. Tool schemas not part of context assembly or token budgeting
2. No tool usage tracking (which tools work in which contexts)
3. No intelligent tool selection based on conversation context
4. No learning from successful/failed invocations
5. All tools sent to LLM regardless of relevance (token waste)

---

## Architecture Overview

```
User Query
    │
    ▼
ContextAssembler.assemble_context(query, available_tools=[...])
    │
    ├──► MemoryController.recall() ──► entities, facts, passages
    │
    └──► ToolContextManager.build_tool_context()
           │
           ├─► ToolMemoryAdapter.get_tools_for_context()
           │     └─► Graph: query ToolNodes by hit_count
           │     └─► Vector: semantic match query ↔ tool descriptions
           │
           └─► select_tools_within_budget()
    │
    ▼
ContextPayload (enhanced)
    ├─ history, passages, entities, facts, insights (existing)
    ├─ tool_schemas: [...]           (NEW)
    ├─ recommended_tools: [...]      (NEW)
    └─ tool_usage_hints: [...]       (NEW)
    │
    ▼
LLM call with filtered tools
    │
    ▼
_archive_turn() ──► ToolExtractor.extract_from_turn()
                      └─► record_tool_usage() → Update ToolNode hit_count
```

---

## Data Models

### 1. ToolUsageRecord (New)
**File:** `packages/friday-memory/src/friday_memory/models/tools.py`

```python
class ToolUsageRecord(BaseModel):
    id: str                              # Invocation ID
    tool_name: str
    tool_category: str                   # filesystem, web, shell, etc.
    session_id: str
    turn_id: str
    query_context: str                   # User query that triggered tool
    parameters: dict[str, Any]
    parameters_hash: str                 # For dedup/pattern matching
    success: bool
    result_summary: str                  # Truncated result for learning
    error_type: str | None
    latency_ms: float
    timestamp: datetime
    provenance: ProvenanceMetadata
```

### 2. ToolRecommendation (New)
```python
class ToolRecommendation(BaseModel):
    tool_name: str
    relevance_score: float               # 0.0-1.0
    reason: str                          # Why recommended
    success_rate_similar_contexts: float | None
    suggested_parameters: dict[str, Any]
```

### 3. ContextPayload (Extended)
**File:** `packages/friday-memory/src/friday_memory/models/payload.py`

Add fields:
- `recommended_tools: list[ToolRecommendation]`
- `tool_schemas: list[dict[str, Any]]`
- `tool_usage_hints: list[str]`

---

## New Modules

### 1. ToolMemoryAdapter
**File:** `packages/friday-memory/src/friday_memory/adapters/tool_store.py`

| Method | Purpose |
|--------|---------|
| `sync_tool_registry(registry)` | Sync registered tools to graph as ToolNodes |
| `record_tool_usage(record)` | Store invocation for learning |
| `get_tools_for_context(query, available_tools)` | Recommend tools via semantic match + history |
| `update_tool_statistics(tool_name)` | Update success_rate, avg_latency on ToolNode |

### 2. ToolContextManager
**File:** `packages/friday-memory/src/friday_memory/context/tool_manager.py`

| Method | Purpose |
|--------|---------|
| `estimate_schema_tokens(tool_names)` | Token cost for schemas |
| `select_tools_within_budget(recommendations, budget)` | Prioritize and filter by tokens |
| `build_tool_context(query, available_tools, budget)` | Returns (schemas, recommendations) |
| `suggest_parameters(tool_name, query_context)` | Parameter hints from history |

### 3. ToolExtractor
**File:** `packages/friday-memory/src/friday_memory/context/tool_extractor.py`

| Method | Purpose |
|--------|---------|
| `extract_from_turn(turn)` | Create ToolUsageRecords from turn |
| `analyze_tool_patterns(session_id)` | Discover usage patterns |

---

## Files to Modify

| File | Changes |
|------|---------|
| `models/payload.py` | Add tool fields to ContextPayload |
| `context/assembler.py` | Accept ToolRegistry, integrate ToolContextManager, call build_tool_context() |
| `context/layout.py` | Format tool hints in prompt, use tool_definitions parameter |
| `controller/memory_controller.py` | Add ToolMemoryAdapter, tool-aware recall() |
| `friday-agent/base.py` | Trigger ToolExtractor after _archive_turn() |

---

## Token Budget Strategy

```
Total_Budget = Model_Max_Tokens - Output_Buffer
Tool_Budget = min(max_tool_tokens, Dynamic_Limit * 0.25)
Context_Budget = Dynamic_Limit - Tool_Budget
```

**Tool Selection Priority:**
1. Required tools (from AgentProfile)
2. High-confidence recommendations (relevance > 0.8)
3. Historical success in similar contexts
4. Recently used in session
5. Category match with conversation topics

---

## Implementation Phases

### Phase 1: Data Models & Storage (IN SCOPE)
- [ ] Create `models/tools.py` with ToolUsageRecord, ToolRecommendation
- [ ] Extend `models/payload.py` with tool fields
- [ ] Create `adapters/tool_store.py` with ToolMemoryAdapter
- [ ] Add ToolNode support to graph store

### Phase 2: Tool Context Management (IN SCOPE)
- [ ] Create `context/tool_manager.py` with ToolContextManager
- [ ] Create `context/tool_extractor.py` with ToolExtractor
- [ ] Implement token estimation for tool schemas
- [ ] Implement semantic tool matching (query ↔ tool descriptions)

### Phase 3: Integration (IN SCOPE)
- [ ] Update `context/assembler.py` to use ToolContextManager
- [ ] Update `context/layout.py` to format tool hints
- [ ] Update `controller/memory_controller.py` with tool_adapter
- [ ] Update `friday-agent/base.py` to trigger tool extraction
- [ ] Write unit tests for new components

### Phase 4: Learning & Optimization (DEFERRED)
- [ ] Implement success rate tracking
- [ ] Implement parameter pattern learning
- [ ] Add telemetry for tool selection accuracy
- [ ] Handle tool deprecation for consistently failing tools

---

## Verification Plan

### Unit Tests
- [ ] ToolUsageRecord serialization/validation
- [ ] ToolContextManager.estimate_schema_tokens() accuracy
- [ ] ToolMemoryAdapter.get_tools_for_context() returns relevant tools
- [ ] Token budget respects limits

### Integration Tests
- [ ] End-to-end: query → tool recommendations → filtered schemas
- [ ] Tool extraction from InteractionTurn works async
- [ ] ToolNode hit_count increments on usage
- [ ] Semantic matching finds relevant tools

### Manual Testing (memory-chat.py)
```bash
# After implementation, add commands:
/tools                    # List registered tools with usage stats
/tool-history <name>      # Show usage history for a tool
/recommend-tools <query>  # Test tool recommendation for a query
```

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Tool storage | Graph nodes + Vector embeddings | Hebbian learning (hit_count) + semantic search |
| Token budget ratio | 25% for tools | Balance tool availability with context space |
| Recommendation threshold | 0.5 relevance | Include moderately relevant tools |
| Usage tracking | Async extraction | Don't block turn archival |
| Parameter learning | Hash-based dedup | Find patterns in successful invocations |

---

## Decisions Made

| Question | Decision |
|----------|----------|
| **Learning scope** | Cross-session - tool patterns are global, learning from all sessions |
| **Category taxonomy** | Use existing friday-tools categories (filesystem, shell, web, git, data, text, code) |
| **Implementation priority** | Core integration first (Phases 1-3), add learning/optimization later |

## Remaining Open Question

1. **Tool deprecation**: How to handle tools that consistently fail? (Defer to Phase 4)
