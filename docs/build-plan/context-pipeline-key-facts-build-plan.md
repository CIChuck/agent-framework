# Build Plan: Context Pipeline — Eliminate key_facts Duplication, Wire Up Graph Facts

**Status:** Planned
**Target:** Context Engineering Pipeline
**Objective:** Remove the duplicate `key_facts` retrieval pipeline, properly wire graph
nodes/edges into the prompt as "Known Facts", and make the section configurable.

---

## 1. Overview

### 1.1 Problem Statement

The context assembly pipeline has two compounding issues:

**Issue 1 — Duplicate key_facts/insights retrieval:**

Both `key_facts` and `insights` query the same vector store data (`where={"type": "insight"}`).
They consume separate token budgets (10% + 20% = 30% of non-history budget) and separate
prompt sections (up to 20 + 15 = 35 items) for substantially overlapping data.

| Pipeline | Query | Dedup? | Recency Filter? | Timestamps? |
|----------|-------|--------|-----------------|-------------|
| `_fetch_key_facts()` | `get_all(where={"type": "insight"})` | No | No | Yes |
| `_fetch_recent_insights()` | `get_all(where={"type": "insight"})` | Yes (topic) | Yes | No |

This wastes context budget and confuses the LLM with redundant information.

**Issue 2 — Graph data retrieved but never rendered:**

The `_retrieve_graph()` method puts `entities` (GraphNode) and `facts` (GraphEdge) onto
`ContextPayload`. These consume token budget estimates (~50 tokens/entity, ~30 tokens/fact)
and are pruned by `_apply_budget()`, but **no section builder renders them into the prompt**.

Meanwhile, `_build_relationship_summaries()` produces natural language summaries (e.g.,
"Chuck created Friday and shared info about Tara") that ARE rendered as "Prior Knowledge" —
but only for `top_entities` by hit_count, missing query-matched entities entirely.

Additionally:
- `_format_associative_block()` exists as dead code (never called from any layout path)
- `_retrieve_graph_with_scoring()` (edge-embedding-based scoring) exists but is never
  called from `recall()` — also dead code

### 1.2 Semantic Model (Current vs. Proposed)

The original intent of "facts" was to represent structured graph knowledge, but this
got conflated with vector store insights during implementation.

**Current (broken):**

| Section | Source | Content |
|---------|--------|---------|
| Key Facts | Vector store `type='insight'` | Same as insights (duplicate) |
| Prior Knowledge | Graph top entities | Relationship summaries (natural language) |
| Insights | Vector store `type='insight'` | Rich contextual observations |
| Summaries | Vector store `type='summary'` | Turn-level narratives |

**Proposed (correct semantic separation):**

| Section | Source | Content |
|---------|--------|---------|
| **Known Facts** | Graph nodes + edges (ALL entities) | Relationship summaries (natural language) |
| **Insights** | Vector store `type='insight'` | Rich contextual observations with timestamps |
| **Summaries** | Vector store `type='summary'` | Turn-level narratives |

This separation reflects how data is actually created:

- **Graph data** is extracted per-turn: discrete entity/relationship triples bounded by
  the ontology. Verified, structured knowledge. Example: `Chuck → MARRIED_TO → Tara`
- **Insights** are extracted per-turn: richer contextual observations from the LLM that
  may span multiple facts. Example: "Chuck mentioned Tara enjoys hiking and they recently
  visited Colorado together"
- **Summaries** are generated per-turn: holistic 2-4 sentence turn narratives

### 1.3 Solution

1. **Remove `key_facts` pipeline entirely** — redundant with `insights`
2. **Expand relationship summaries** to cover ALL entities (top by hit_count + query-matched),
   not just `top_entities`
3. **Rename "Prior Knowledge" → "Known Facts"** with configurable `max_items` and
   `section_priority` ordering
4. **Add timestamps to insights** (the one useful feature key_facts had)
5. **Clean up dead code** (`_format_associative_block`, unused budget fields)

---

## 2. Architecture: Data Flow (Before and After)

### 2.1 Current Flow

```
recall()
  ├── _retrieve_graph(query) → entities, facts     ← ON PAYLOAD, NEVER RENDERED
  ├── get_top_nodes(hit_count) → top_entities
  ├── _build_relationship_summaries(top_entities)   ← ONLY TOP ENTITIES
  │     → recent_memories                           ← RENDERED as "Prior Knowledge"
  ├── _fetch_recent_insights() → insights           ← RENDERED as "Recent Insights"
  ├── _fetch_recent_summaries() → summaries         ← RENDERED as "Conversation Summaries"
  └── _fetch_key_facts() → key_facts               ← DUPLICATE of insights, RENDERED as "Key Facts"
```

### 2.2 Proposed Flow

```
recall()
  ├── _retrieve_graph(query) → entities, facts      ← ON PAYLOAD (for budget estimation)
  ├── get_top_nodes(hit_count) → top_entities
  ├── merge top_entities + query entities → all_entities
  ├── _build_relationship_summaries(all_entities)    ← ALL ENTITIES NOW
  │     → recent_memories                            ← RENDERED as "Known Facts"
  ├── _fetch_recent_insights() → insights            ← RENDERED as "Insights" (with timestamps)
  └── _fetch_recent_summaries() → summaries          ← RENDERED as "Summaries"
```

Key changes:
- `_fetch_key_facts()` removed entirely
- `_build_relationship_summaries()` now receives the merged entity list
- "Known Facts" section is configurable via `SupportingContextConfig`

---

## 3. Implementation Steps

### 3.1 `memory_controller.py` — Remove `_fetch_key_facts()`, fix relationship summary coverage

**File:** `packages/friday-memory/src/friday_memory/controller/memory_controller.py`

**Budget redistribution in `_calculate_retrieval_limits()` (~line 357):**

| Allocation | Before | After |
|------------|--------|-------|
| `FACTS_PERCENT` | 0.10 | REMOVED |
| `INSIGHTS_PERCENT` | 0.20 | 0.25 |
| `SUMMARIES_PERCENT` | 0.15 | 0.20 |

Remove `max_facts` calculation and `"facts"` key from the returned dict.

**Fix relationship summary coverage in `recall()` (~line 522):**

Change:
```python
all_relationships = await self._build_relationship_summaries(top_entities)
```
To:
```python
all_relationships = await self._build_relationship_summaries(entities)
```

This ensures query-matched entities (found via fuzzy search) also get their
relationships rendered, not just the top entities by Hebbian hit_count.

**Remove key_facts from `recall()` (~line 494):**
- Delete: `key_facts = await self._fetch_key_facts(limit=limits["facts"])`
- Delete: `key_facts=key_facts` from `ContextPayload(...)` constructor
- Delete: `debug_info["key_facts_count"] = len(key_facts)`

**Delete `_fetch_key_facts()` method (~lines 1098-1131):**
Entirely redundant with `_fetch_recent_insights()`.

### 3.2 `payload.py` — Remove `key_facts` field

**File:** `packages/friday-memory/src/friday_memory/models/payload.py`

- Remove the `key_facts: list[dict[str, Any]]` field from `ContextPayload`
- Remove `len(self.key_facts)` from `total_items()` method

### 3.3 `layout.py` — Remove key_facts, rename to "Known Facts", add configurability

**File:** `packages/friday-memory/src/friday_memory/context/layout.py`

**`SupportingContextConfig` defaults (~line 97):**

```python
# Before
section_priority: list[str] = ["recent_memories", "passages", "key_facts",
                                "insights", "summaries", "tools", "state"]
max_items: dict[str, int] = {"passages": 10, "key_facts": 20, "insights": 15,
                              "summaries": 10, "tools": 5}

# After
section_priority: list[str] = ["known_facts", "passages", "insights",
                                "summaries", "tools", "state"]
max_items: dict[str, int] = {"passages": 10, "known_facts": 25, "insights": 25,
                              "summaries": 10, "tools": 5}
```

**Section builders in `_format_context_plain()` (~line 873):**
- Remove `"key_facts"` builder entry
- Rename `"recent_memories"` → `"known_facts"` builder entry

**Rename `_build_section_recent_memories()` → `_build_section_known_facts()`:**
- Change header: `"## Prior Knowledge"` → `"## Known Facts"`
- Apply `max_items` from config: `config.max_items.get("known_facts", 25)`

**Delete `_build_section_key_facts()` (~lines 973-992):** No longer needed.

**Update `_build_section_insights()` (~lines 994-1008):** Add timestamps:
```python
for insight in payload.insights[:max_insights]:
    text = insight.get("text", "")
    created_at = insight.get("metadata", {}).get("created_at", "")
    timestamp = created_at[:16] if created_at else ""
    if timestamp:
        lines.append(f"- [{timestamp}] {text}")
    else:
        lines.append(f"- {text}")
```

**Delete `_format_associative_block()` (~line 1448):** Dead code, never called.

**Update all format methods** (`_build_static_context`, `_format_context_json`,
`_format_context_xml`, `_format_context_markdown`):
- Remove key_facts blocks
- Rename "Prior Knowledge" → "Known Facts"
- Rename `"prior_knowledge"` → `"known_facts"` in JSON keys

### 3.4 `assembler.py` — Remove all key_facts references

**File:** `packages/friday-memory/src/friday_memory/context/assembler.py`

Remove `key_facts` from every `ContextPayload(...)` constructor and filter method:

| Method | Line | Change |
|--------|------|--------|
| `_apply_passage_routing()` | ~590 | Remove `key_facts=payload.key_facts` |
| `_filter_decayed()` | ~827 | Remove `key_facts=payload.key_facts` |
| `_apply_conditional_summaries()` | ~904 | Remove `key_facts=payload.key_facts` |
| `_filter_by_query_relevance()` | ~998-1087 | Remove `key_facts` variable, filter block, from constructor |
| `_create_pruned_payload_full()` | ~1267 | Remove `key_facts` parameter and field |
| `_create_pruned_payload()` | ~1342 | Remove `key_facts=original.key_facts` |
| `assemble_context()` | ~524 | Remove `key_facts=budgeted_payload.key_facts` |
| `_merge_query_relevance_config()` | defaults | Remove `"key_facts"` from `keep_recent` |

### 3.5 `config.yaml` — Update supporting context config

**File:** `tests/integration/memory/config.yaml`

- In `section_priority` (~line 637): Rename `recent_memories` → `known_facts`,
  remove `key_facts`
- In `max_items` (~line 649): Remove `key_facts: 20`, add `known_facts: 25`,
  update `insights: 25`
- In `priming` section (~line 796): Remove `max_facts: 20`
- Update comments to reflect new section names

### 3.6 `friday.py` — Update display code and config fallback

**File:** `tests/integration/memory/friday.py`

Display references to update (all read from `ContextPayload` fields):

**`/context --debug` display (~line 1347):**
```
BEFORE:
  Key facts (natural language): 15
  Relationship summaries: 8

AFTER:
  Known Facts: 8
```

**`/context --debug` token breakdown (~lines 1392-1419):**
- Remove `key_facts_tokens` calculation
- Rename `relationships_text`/`relationships_tokens` → `known_facts_text`/`known_facts_tokens`

**Context priming display (~lines 2446-2491):**
- Remove `Key Facts: ...` line
- Rename `Relationships: ...` → `Known Facts: ...`
- Remove key_facts content display block (~lines 2486-2491)
- Rename "Relationship Summaries" → "Known Facts" header (~line 2465)

**`SupportingContextConfig` fallback (~line 7015-7024):**
```python
# Before
section_priority=["recent_memories", "passages", "key_facts", "insights", ...]
max_items={"passages": 10, "key_facts": 20, "insights": 15, ...}

# After
section_priority=["known_facts", "passages", "insights", ...]
max_items={"passages": 10, "known_facts": 25, "insights": 25, ...}
```

---

## 4. Impact Assessment

### 4.1 Files to Modify

| File | Change |
|------|--------|
| `packages/friday-memory/src/friday_memory/controller/memory_controller.py` | Remove `_fetch_key_facts()`, redistribute budget, fix `_build_relationship_summaries` to use all entities |
| `packages/friday-memory/src/friday_memory/models/payload.py` | Remove `key_facts` field from `ContextPayload` |
| `packages/friday-memory/src/friday_memory/context/layout.py` | Remove key_facts section, rename to "Known Facts" with max_items config, add timestamps to insights, delete dead code |
| `packages/friday-memory/src/friday_memory/context/assembler.py` | Remove all key_facts references in budget pruning and payload construction |
| `tests/integration/memory/config.yaml` | Rename `recent_memories` → `known_facts`, remove `key_facts`, update `max_items` |
| `tests/integration/memory/friday.py` | Update `/context` display, token breakdown, priming display, config fallback |

### 4.2 Files NOT Changed

| File | Reason |
|------|--------|
| `packages/friday-memory/src/friday_memory/maintenance/reorganizer.py` | Operates on raw memory stores (vector + graph), not on the context pipeline. Creates `type='insight'` documents and manages graph nodes — storage layer is unchanged. |
| `tests/integration/memory/friday.py` (`cmd_reorganize`) | The `/reorganize` command orchestrates the reorganizer module against raw stores. No references to `key_facts` or `recent_memories` in the reorganization pipeline. |
| `packages/friday-memory/src/friday_memory/context/extractor.py` | Extraction creates graph nodes/edges and `type='insight'` documents. Storage format unchanged — only retrieval/display changes. |

### 4.3 Token Budget Impact

**Before:**
- `key_facts`: 10% of non-history budget (wasted on duplicate data)
- `insights`: 20% of non-history budget
- `summaries`: 15% of non-history budget
- Total for these three: 45%

**After:**
- `insights`: 25% of non-history budget (gains 5%)
- `summaries`: 20% of non-history budget (gains 5%)
- `key_facts`: 0% (eliminated)
- Total for these two: 45%

Net effect: Same total allocation, but no wasted budget on duplicate retrieval.

---

## 5. Verification

1. **`uv run pytest packages/friday-memory/tests_memory/ -v`** — all tests pass
2. **`uv run ruff check packages/friday-memory/`** — no lint errors on modified files
3. **`/context --debug`** in friday.py — should show:
   - "Known Facts" section (not "Prior Knowledge" or "Key Facts")
   - Relationship summaries covering both top entities and query-matched entities
   - Token breakdown with "Known Facts" instead of separate "Relationships" and "Key Facts"
4. **`/insights`** — should work unchanged, now with timestamps on each item
5. **`/facts`** — should still show all documents (queries `get_all()` without type filter)
6. **`/reorganize --analyze`** — should work unchanged (no coupling to context pipeline)
7. **Configurability test**: changing `known_facts` position in `section_priority`
   (config.yaml) should change where it appears in the prompt output
