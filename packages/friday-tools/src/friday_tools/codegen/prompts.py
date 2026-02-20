"""
Prompt templates for code generation.

Contains the system and user prompts used by CodeGenerationTool
to instruct the LLM to generate executable Python code.
"""

SYSTEM_PROMPT = """\
You are a Python code generator for the Friday AI agent framework.

Your job is to generate Python code that accomplishes tasks using the available Friday tools.
The code you generate will be executed directly, so it must be valid, complete Python.

## Rules

1. **Import tools correctly**: Use the exact import statements provided for each tool.
2. **Use async/await**: All tool executions are async. Use `await tool.execute(...)`.
3. **Return results**: Set `__result__ = <value>` to return a value from your code.
4. **Handle errors**: Wrap tool calls in try/except when appropriate.
5. **Be concise**: Generate only the necessary code, no explanations.
6. **No external dependencies**: Only use Python stdlib and the provided Friday tools.

## Output Format

Return ONLY the Python code wrapped in a code block:

```python
# Your code here
```

Do not include any explanation before or after the code block.
"""  # noqa: E501


def build_user_prompt(task: str, context: str, tool_manifest: str) -> str:
    """
    Build the user prompt for code generation.

    Args:
        task: The task description
        context: Additional context or constraints
        tool_manifest: Formatted tool manifest from ToolManifest.to_prompt_context()

    Returns:
        Complete user prompt string
    """
    prompt_parts = [tool_manifest]

    prompt_parts.append("\n---\n")
    prompt_parts.append(f"## Task\n\n{task}")

    if context:
        prompt_parts.append(f"\n\n## Additional Context\n\n{context}")

    prompt_parts.append("\n\n---\n")
    prompt_parts.append(
        "Generate Python code to accomplish this task. "
        "Use the available tools and set `__result__` to return the final value."
    )

    return "\n".join(prompt_parts)


# Example prompt for reference/testing
EXAMPLE_PROMPT = """\
# Available Friday Tools

You have access to 3 tools:

## file_read
**Import:** `from friday_tools.filesystem import file_read`
**Description:** Read the contents of a file
**Parameters:**
  - `path`: string (required) - Path to the file to read
  - `encoding`: string - File encoding (default: utf-8)
**Example:** `result = await file_read.execute(path="/path/to/file")`

## file_write
**Import:** `from friday_tools.filesystem import file_write`
**Description:** Write content to a file
**Parameters:**
  - `path`: string (required) - Path to the file to write
  - `content`: string (required) - Content to write
**Example:** `result = await file_write.execute(path="/path/to/file", content="example")`

## web_fetch
**Import:** `from friday_tools.web import web_fetch`
**Description:** Fetch content from a URL
**Parameters:**
  - `url`: string (required) - URL to fetch
**Example:** `result = await web_fetch.execute(url="https://example.com")`

---

## Task

Read the contents of /tmp/input.txt and write them to /tmp/output.txt

---

Generate Python code to accomplish this task. Use the available tools and set `__result__` to return the final value.
"""  # noqa: E501
