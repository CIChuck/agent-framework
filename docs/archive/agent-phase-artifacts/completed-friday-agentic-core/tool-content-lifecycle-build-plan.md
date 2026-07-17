# Build Plan: Smart Tool Content Lifecycle (Reference-Based Decay)

**Status:** Draft
**Target Components:** `friday-memory`, `friday-agent`
**Objective:** Implement an intelligent, reference-based lifecycle for large tool outputs (e.g., file reads) to optimize token usage. Tool content should persist while actively discussed (LRU) and decay into summaries only when the conversation focus shifts.

---

## 1. Problem Statement & Current State Analysis

### 1.1 The "Tool Amnesia" Bug
Currently, `friday-memory` suffers from a critical context assembly gap. While tool results are stored in `InteractionTurn` objects in the database, the `PromptArchitect` **completely ignores them** when rebuilding conversation history for the LLM.
*   **Current Behavior:** The LLM sees `User: Read main.py` -> `Assistant: Done.`
*   **Missing Context:** The actual content of `main.py` (the tool result) is never added to the message list in subsequent turns.
*   **Consequence:** The agent "forgets" it read the file immediately after the turn ends, forcing it to re-read the file for any follow-up questions.

### 1.2 The Token Bloat Problem
Even if we fix the "Amnesia" bug, we face a secondary problem:
*   **Token Waste:** Large tool outputs (e.g., reading a 2000-line file) will persist in history until they fall out of the context window.
*   **Static TTL Failure:** Simple time-based expiration is insufficient because users may discuss a file for 10+ turns.

## 2. Proposed Solution: Reference-Based Decay

We will implement a two-part solution:
1.  **Fix Amnesia:** Update `PromptArchitect` to correctly render tool calls and results using native LLM message roles.
2.  **Smart Decay:** Implement a **Least Recently Used (LRU)** decay mechanism.
    *   **Active Tracking:** Track "Last Referenced Turn" for each large output.
    *   **Reference Detection:** Use extraction to identify when tool outputs are discussed.
    *   **Smart Decay:** If `(Current_Turn - Last_Referenced_Turn) > Gap_Limit`, replace full content with a **Structured Summary**.

## 3. Architecture

### 3.1 New Component: `ToolContentManager`
Located in `packages/friday-memory/src/friday_memory/lifecycle/tool_content.py`.

**Responsibilities:**
*   **Registry:** Track active large tool outputs across the session.
*   **Scoring:** Calculate `relevance_score` for each output based on recency.
*   **Transition:** Manage the state change from `Active` -> `Summarized`.

### 3.2 Detection Logic: `ToolReferenceDetector`
Located in `packages/friday-memory/src/friday_memory/context/extractor.py` (or a sub-component).

**Mechanism:**
*   Extends the existing extraction pipeline.
*   **Input:** User Message + Assistant Response + List of Active Tool Outputs.
*   **Task:** Identify which Tool Outputs were semantically referenced.
*   **Method:**
    *   *High Accuracy:* Add a specific prompt to the Extraction LLM calls: "Which of these active files/tools were discussed in this turn?"
    *   *Efficiency:* Fallback to keyword/entity overlap if LLM is too expensive.

### 3.3 Data Model Updates

**Update `ToolResult` (Pydantic Model):**
```python
class ToolResult(BaseModel):
    # ... existing fields ...
    content: str
    
    # Lifecycle Metadata
    turn_id: str  # Turn where this tool was executed
    last_referenced_turn_id: str | None = None
    referencing_turns: list[str] = Field(default_factory=list) # Audit trail
    
    # State
    is_decayed: bool = False
    summary: str | None = None
    original_size_tokens: int | None = None
```

### 3.4 Configuration (`decay.yaml`)

```yaml
tool_lifecycle:
  enabled: true
  min_tokens_for_tracking: 500  # Only track large outputs
  decay_threshold_turns: 3      # Summarize after 3 turns of silence
  
  # Override by tool type
  policies:
    - tool: "read_file"
      decay_threshold_turns: 2  # Code files might need faster cleanup
    - tool: "web_search"
      decay_threshold_turns: 1  # Search results age quickly
```

## 4. Implementation Steps

### Phase 1: Fix Tool Amnesia (Critical Prerequisite)
**Target:** `packages/friday-memory/src/friday_memory/context/layout.py`
1.  Modify `PromptArchitect.format_prompt`.
2.  Iterate through `turn.tool_calls` and `turn.tool_results`.
3.  **Construct Native Messages:**
    *   Append `{"role": "assistant", "tool_calls": [...]}` message to represent the intent.
    *   Append `{"role": "tool", "tool_call_id": ..., "content": ...}` message for the result.
    *   *Crucial:* This links the data (`content`) to the metadata (`read_file path=...`) so the LLM knows *what* it is reading.

### Phase 2: Data Model & Registry
1.  Update `ToolResult` schema in `friday-memory` and `friday-tools`.
2.  Implement `ToolContentManager` to maintain a registry of "Active Tool Outputs" for the session.

### Phase 3: Reference Detection (The "Smart" Part)
1.  Modify `MemoryExtractor.extract()` to accept `active_tool_outputs`.
2.  Update extraction prompt to include a "Source Attribution" step:
    *   "Did the conversation refer to [Tool Output 1: main.py]?"
3.  Wire the extraction result back to `ToolContentManager` to update `last_referenced_turn_id`.

### Phase 4: Decay & Summarization
1.  Implement `check_for_decay()` method in `ToolContentManager`.
    *   Iterate through active outputs.
    *   If `gap > threshold`: Trigger summarization.
2.  Implement `summarize_content(content)`:
    *   Use existing `LLMClient` to generate a concise summary.
    *   "File `main.py` (2000 lines). Defines `AgentBase` class with methods `run`, `think`, `act`..."
3.  Implement `replace_content()`:
    *   Update the `InteractionTurn` in the database.
    *   Set `content` = `summary`.
    *   Set `is_decayed` = `True`.

### Phase 5: Context Presentation (Lifecycle Aware)
1.  Update `PromptArchitect` again to handle `is_decayed` flag.
2.  **Conditional Rendering:**
    *   If `is_decayed=False`: Render full content (as fixed in Phase 1).
    *   If `is_decayed=True`: Render the **Summary** in the tool message content, optionally with a marker: `[Summary of read_file "main.py"]: ...`.

## 5. User Experience Walkthrough

1.  **Turn 1:** "Read `main.py`." -> Agent reads file. `main.py` is **Active**.
2.  **Turn 2:** "What does the `run` method do?" -> Agent answers. Extraction sees reference to `main.py`. Timer resets.
3.  **Turn 3:** "Change the color of the UI to blue." -> Agent answers. No reference to `main.py`. Gap = 1.
4.  **Turn 4:** "Also make the button round." -> Agent answers. No reference. Gap = 2.
5.  **Turn 5:** (Gap > Threshold) -> System background task runs. `main.py` content is replaced with summary.
6.  **Turn 6:** "Wait, go back to `main.py`..." -> Agent sees the **Summary** in history ("Defines AgentBase..."). It knows it read it. It can either answer from summary or decide to *re-read* if detail is missing.

## 6. Success Criteria
*   **Precision:** Content stays available while discussed.
*   **Efficiency:** Tokens drop significantly once topic changes.
*   **Continuity:** Agent never "forgets" the file exists, only the raw details.
