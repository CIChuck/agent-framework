# Analysis: Tool Return Content & Memory Integration

**Date:** 2026-01-21
**Component:** `friday-memory` <-> `friday-tools` <-> `friday-agent`

## Executive Summary

This analysis examines how tool execution results flow from the `friday-tools` package through the `friday-agent` execution loop and finally into the `friday-memory` context architecture.

**Key Findings:**
1.  **Tool Execution:** Tools return structured `ToolResult` objects (Pydantic models).
2.  **Agent Processing:** The agent converts these structured objects to raw strings via `str(result)`, potentially leaking Pydantic object syntax (`ToolResult(content=...)`) into the LLM context rather than clean output.
3.  **Memory Storage:** Tool calls and results are correctly captured and stored in the episodic memory (`InteractionTurn` objects).
4.  **Context Assembly (Critical Gap):** The `PromptArchitect` **completely ignores** stored tool interactions when reconstructing conversation history from memory. This results in "Tool Amnesia" where the agent forgets its own actions and observations as soon as they pass into history (next session or context reload).

---

## Detailed Data Flow

### 1. Tool Execution (`friday-tools`)
Tools are implemented to return a `ToolResult` Pydantic model:
```python
class ToolResult(BaseModel):
    content: str
    data: dict[str, Any] | None
    metadata: dict[str, Any] | None
```
*   **Source:** `packages/friday-tools/src/friday_tools/base.py`

### 2. Agent Execution Loop (`friday-agent`)
The `CopilotAgent` executes the tool and processes the result in `_execute_tool_call`:
```python
# packages/friday-agent/src/friday_agent/base.py

result = await func(**arguments)
result_str = str(result)  # <--- ISSUE 1: Blind string conversion
```
*   **Issue 1 (Serialization):** Converting a Pydantic model to `str()` results in a representation like `ToolResult(content='...', data={...})`. This wastes tokens and exposes internal implementation details to the LLM. It should likely extract `result.content` or use a formatted JSON representation.

The agent then appends this `result_str` to its *local* `messages` list for the current Re-Act loop:
```python
messages.append({
    "role": "tool",
    "tool_call_id": tc["id"],
    "content": result,
})
```
*   **Status:** **Correct** for the immediate turn. The LLM *can* see the tool output while it is "thinking" inside the loop.

### 3. Memory Archival (`friday-agent` -> `friday-memory`)
At the end of a turn, the agent archives the interaction:
```python
# packages/friday-agent/src/friday_agent/base.py

turn = InteractionTurn(
    ...,
    tool_calls=[MemoryToolCall(**tc) ...],
    tool_results=[MemoryToolResult(**tr) ...]
)
await self.memory.add_turn(self.session_id, turn)
```
*   **Status:** **Correct**. The structured data is preserved in the database (SQLite/Transcript).

### 4. Context Assembly & Prompt Architecture (`friday-memory`)
When the agent starts a *new* turn, it calls `context_engine.assemble_context()`, which retrieves history from memory, and then `format_prompt()`.

**The Critical Failure:**
The `PromptArchitect` iterates through the history but only looks for user and assistant text messages, ignoring tool events.

```python
# packages/friday-memory/src/friday_memory/context/layout.py

def format_prompt(self, ...):
    # ...
    for turn in all_history:
        messages.append({
            "role": "user",
            "content": f"[{self.user_name}]: {turn.user_message}",
        })
        if turn.assistant_message:
            messages.append({
                "role": "assistant",
                "content": f"[{self.assistant_name}]: {turn.assistant_message}",
            })
        
        # MISSING: Logic to append tool_calls and tool_results
```

*   **Result:** The LLM receives a sanitized history that looks like:
    *   User: "Check the file."
    *   Assistant: "I have checked the file."
    *   *Missing:* The actual `read_file` tool call and its output.

## Recommendations

1.  **Fix Prompt Layout:** Update `PromptArchitect.format_prompt` in `packages/friday-memory/src/friday_memory/context/layout.py` to iterate over `turn.tool_calls` and `turn.tool_results` and reconstruct the `tool` role messages.

2.  **Improve Serialization:** Update `friday-agent` to intelligently handle `ToolResult` objects. Instead of `str(result)`, it should likely use `result.content` for the message content, or a JSON serialization of `content` + relevant `data`.

3.  **Standardize ToolResult:** Ensure `friday-memory` and `friday-tools` share the exact same definition or have a clean adapter, to avoid the re-definition seen in `friday-memory/src/friday_memory/models/session.py`.

## Decorations and LLM Awareness

To prevent the agent from redundantly re-invoking tools (e.g., re-reading a file it has already seen), the context must clearly link the **Result Data** with the **Source Metadata** and the **Original Intent**.

### The "Amnesia" Symptom
When an agent is asked a follow-up question about a file it previously read, it often re-invokes the `file_read` tool. This happens because the previous file content is missing from its history, or the content is present but "unlabeled," leaving the LLM unsure if that specific data corresponds to the file in question.

### Strategies for Context Decoration

#### 1. Native Message Roles (Recommended)
By properly reconstructing the history using the standard LLM roles (`assistant` for the call, `tool` for the result), the LLM naturally maintains awareness:
*   **Assistant Message:** Contains `read_file(path="main.py")`. This serves as the "decoration" or label for what is about to follow.
*   **Tool Message:** Contains the actual file content.
Because the LLM sees its own request followed by the data, it recognizes that `main.py` is already in its context window.

#### 2. Explicit Text Wrappers (Fallback/Clarification)
In addition to native roles, "wrapping" tool output in descriptive delimiters can provide extra clarity, especially for long or complex outputs:
```text
--- START TOOL OUTPUT: read_file("main.py") ---
[File Content]
--- END TOOL OUTPUT: read_file("main.py") ---
```

### Implementation Requirement
The `PromptArchitect` must be updated to not only include the tool results but to preserve the **relationship** between the tool call (which contains the parameters like `path`) and the result content. Reconstructing history without the tool call arguments leaves the results "orphaned" and unidentifiable.
