---
title: "Tool System Overview"
description: "BaseTool, ToolManifest, and the Re-Act execution loop."
weight: 1
---

Tools are Friday's hands and eyes—the mechanisms through which agents interact with the external world. While memory enables learning and LLMs provide reasoning, tools enable **action**: reading files, making HTTP requests, executing code, querying databases, manipulating data, and interfacing with external systems.

Friday's tool system is built on a protocol-first architecture that makes creating, registering, and using tools remarkably simple. From 50+ built-in tools covering common operations to custom tools tailored for your domain, Friday provides a comprehensive and extensible toolkit for agent capabilities.

## Tool Architecture & Design

### The BaseTool Protocol

At the heart of Friday's tool system is the `BaseTool` abstract class, which defines the contract that all tools must implement. This protocol-based approach ensures consistency across all tools and enables seamless integration with agents.

**Core Contract:**

Every tool must provide:
1. **`name`** (property): Unique identifier (e.g., `"file_read"`, `"http_get"`)
2. **`description`** (property): Human-readable explanation for the LLM
3. **`parameters_schema`** (property): JSON Schema defining expected parameters
4. **`execute()`** (method): Async function that performs the actual work
5. **`category`** (optional property): Tool grouping (filesystem, web, git, etc.)
6. **`tags`** (optional property): List of metadata tags for filtering

**Protocol Definition:**

```python
class BaseTool(ABC):
    """Base class for implementing Friday tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool identifier."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description for the LLM."""
        pass

    @property
    @abstractmethod
    def parameters_schema(self) -> dict[str, Any]:
        """JSON Schema for tool parameters."""
        pass

    @property
    def category(self) -> str:
        """Tool category (filesystem, web, git, etc.)."""
        return "uncategorized"

    @property
    def tags(self) -> list[str]:
        """Optional tags for filtering."""
        return []

    @abstractmethod
    async def execute(self, **kwargs: Any) -> str:
        """Execute the tool with given arguments."""
        pass

    def to_schema(self, format: str = "plain") -> dict[str, Any]:
        """Convert tool to JSON schema for LLM function calling."""
        # Returns either "plain" or "openai" format
```

**Why This Design?**

The protocol-based approach provides several benefits:

1. **Consistency**: All tools have the same interface, simplifying agent integration
2. **Validation**: Parameter schemas enforce type safety and provide clear documentation
3. **Discoverability**: Tools self-document through schemas and descriptions
4. **Interoperability**: Same tool can work with OpenAI function calling, Anthropic tool use, or other formats
5. **Testing**: Tools can be tested in isolation without agents or LLMs

### Tool Schemas for LLMs

Friday generates tool schemas automatically from Pydantic models and Python type hints, ensuring that tools are always properly documented for LLM function calling.

**Schema Generation Flow:**

1. Tool defines parameters using Pydantic `BaseModel` or Python types
2. Friday extracts type information and generates JSON Schema
3. Schema is formatted for target LLM provider (OpenAI, Anthropic, etc.)
4. LLM receives schema in its native format
5. LLM generates tool calls using the schema
6. Friday validates arguments against schema before execution

**Example: File Read Tool Schema**

```python
class FileReadTool(FridayTool):
    """Read file contents with smart encoding detection."""

    name = "file_read"
    description = "Read the contents of a text file with smart encoding detection."
    category = "filesystem"
    tags = ["file", "read", "text", "cat"]

    class Input(BaseModel):
        path: str = Field(description="Path to the file to read")
        encoding: str = Field(
            default="auto",
            description="File encoding. Use 'auto' for automatic detection."
        )
        start_line: int = Field(
            default=1,
            ge=1,
            description="Starting line number (1-indexed, default: 1)"
        )
        max_lines: int | None = Field(
            default=None,
            description="Maximum number of lines to read (None for all)"
        )

    async def run(self, args: Input) -> ToolResult:
        # Implementation...
```

**Generated Schema (Plain Format):**

```json
{
  "name": "file_read",
  "description": "Read the contents of a text file with smart encoding detection.",
  "category": "filesystem",
  "tags": ["file", "read", "text", "cat"],
  "parameters": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Path to the file to read"
      },
      "encoding": {
        "type": "string",
        "description": "File encoding. Use 'auto' for automatic detection.",
        "default": "auto"
      },
      "start_line": {
        "type": "integer",
        "description": "Starting line number (1-indexed, default: 1)",
        "minimum": 1,
        "default": 1
      },
      "max_lines": {
        "type": ["integer", "null"],
        "description": "Maximum number of lines to read (None for all)",
        "default": null
      }
    },
    "required": ["path"]
  }
}
```

**Provider Compatibility:**

Friday abstracts provider-specific schema differences:

| Provider | Format | Tool Call Structure |
|----------|--------|---------------------|
| **OpenAI** | `{"type": "function", "function": {...}}` | Function calling with `tool_calls` array |
| **Anthropic** | `{"name": ..., "description": ..., "input_schema": {...}}` | Tool use blocks in content |
| **Google Gemini** | Function declaration format | Function calling with parameters |
| **Local (Ollama)** | OpenAI-compatible format | Function calling (if model supports) |

Friday's `to_schema(format="openai")` method handles conversion automatically. Agents never need to know which LLM provider is being used—the tool system abstracts this complexity.

### Tool Result Standardization

All tools return a standardized `ToolResult` object that encapsulates three types of information: human-readable content (for LLM), structured data (for memory/code), and metadata (for debugging/audit).

**ToolResult Structure:**

```python
class ToolResult(BaseModel):
    """Standardized return object for all Friday tools."""

    content: str                           # Human-readable string for LLM context
    data: Any | None = None                # Raw structured data for programmatic access
    metadata: dict[str, Any] = Field(default_factory=dict)  # Execution details
    error: str | None = None               # Error message if execution failed
```

**Field Purposes:**

1. **`content`**: The text that gets added to the LLM's context
   - Should be concise but informative
   - Includes the most relevant information for next steps
   - Examples: file contents, HTTP response summary, git status output

2. **`data`**: The raw, structured result for memory extraction or code processing
   - Can be any Python type (dict, list, object)
   - Used by memory extraction to parse entities/relationships
   - Used by code generation tools to compose programmatic workflows

3. **`metadata`**: Execution context for observability
   - Includes details like: execution time, file size, encoding detected, HTTP status code
   - Populated by the tool, not inferred
   - Used for debugging, auditing, and transcript analysis

4. **`error`**: Error message if tool execution failed
   - If `error` is set, the tool failed
   - Provides actionable feedback for retry or alternative approach
   - Keeps errors structured and queryable

**Example: File Read Tool Result**

Success case:
```python
ToolResult(
    content="""# Config File
server:
  host: localhost
  port: 8080
database:
  url: postgresql://localhost/mydb
""",
    data={
        "path": "/project/config.yaml",
        "size_bytes": 156,
        "line_count": 5,
        "total_lines": 5,
        "encoding": "utf-8",
        "encoding_confidence": 0.99,
        "encoding_method": "chardet"
    },
    metadata={
        "path": "config.yaml",
        "encoding": "utf-8",
        "truncated": False,
        "start_line": 1
    }
)
```

Failure case:
```python
ToolResult(
    content="Error: File not found: /nonexistent/file.txt",
    error="File not found: /nonexistent/file.txt",
    metadata={
        "path": "/nonexistent/file.txt",
        "attempted_encoding": "auto"
    }
)
```

## ToolManifest & Dynamic Tool Selection

### Context-Aware Tool Recommendations

Friday doesn't always include all 50+ tools in every LLM context. Instead, it uses intelligent selection to include the most relevant tools based on the task, conversation history, and token budget.

**Recommendation Algorithm:**

1. **Semantic Similarity**: Compare user query embedding to tool description embeddings
2. **Category Matching**: If query mentions files, prioritize `filesystem` tools
3. **Historical Usage**: If user frequently uses certain tools, include them
4. **Explicit References**: If query mentions a URL, include `web` tools
5. **Agent Profile**: Agent YAML can specify preferred tools or categories

**Why Not Include All Tools?**

Including all 50+ tools in every context would:
- **Consume Excessive Tokens**: Tool schemas can be 100-500 tokens each; 50 tools = 5,000-25,000 tokens
- **Reduce Context Space**: Less room for conversation history, memories, and user query
- **Confuse the LLM**: Too many options leads to analysis paralysis and suboptimal tool selection
- **Increase Latency**: Larger prompts take longer to process

**Configuration:**

```yaml
# In agent YAML profile
tools:
  selection_mode: "dynamic"  # or "all", "category", "explicit"
  max_tools: 10              # Maximum tools in context
  preferred_categories:
    - filesystem
    - web
  always_include:
    - file_read
    - http_get
```

### Tool Token Budget Management

The PromptArchitect allocates tokens across components: system prompt, conversation history, context (memories), tools, and user query. Tools compete with other components for token budget.

**Default Token Budget Allocation:**

For an 8K context window:
- System Prompt: 12.5% (1,000 tokens)
- Conversation History: 25% (2,000 tokens)
- Context (Memories): 50% (4,000 tokens)
- **Tools: Shared with Context** (prioritized by relevance)
- User Query: 12.5% (1,000 tokens)

**Tool Schema Token Costs:**

Typical tool schema sizes:
- Simple tool (2-3 parameters): 100-200 tokens
- Medium tool (5-7 parameters): 200-400 tokens
- Complex tool (10+ parameters): 400-800 tokens

**Schema Format Options:**

Full format (OpenAI style):
```json
{
  "type": "function",
  "function": {
    "name": "file_read",
    "description": "Read the contents of a text file with smart encoding detection.",
    "parameters": {
      "type": "object",
      "properties": {
        "path": {"type": "string", "description": "Path to the file to read"},
        "encoding": {"type": "string", "description": "File encoding...", "default": "auto"}
      },
      "required": ["path"]
    }
  }
}
```

Compact format (Friday compressed):
```json
{
  "name": "file_read",
  "desc": "Read file with auto encoding",
  "params": {"path": "str*", "encoding": "str=auto", "start_line": "int=1"}
}
```

Compact format saves ~40% tokens with minor description quality loss.

**Configuration:**

```yaml
context:
  total_tokens: 8000
  tool_budget_max: 2000      # Maximum tokens for tool schemas
  tool_schema_format: "compact"  # or "full"
  fallback_to_categories: true
```

### Per-Task Tool Injection

For specific workflows or agent types, you can explicitly inject tools into context, overriding dynamic selection.

**Configuration Methods:**

Agent YAML profile:
```yaml
name: code_reviewer
role: "Code review specialist"
tools:
  explicit:
    - git_diff
    - git_log
    - code_analyze
    - git_commit
  allow_dynamic: false  # Only use explicit tools
```

Workflow task definition:
```yaml
# In workflow YAML
tasks:
  - id: analyze_code
    agent: coder
    tools:
      - file_read
      - code_analyze
      - python_execute
    description: "Analyze the codebase for issues"
```

Programmatic injection:
```python
agent = CopilotAgent(...)

# Inject tools for this session
agent.inject_tools(["file_read", "git_status", "git_diff"])

# Revert to dynamic selection
agent.clear_injected_tools()
```

**Allowlist Mode (Security):**

For untrusted agents or high-security environments:

```yaml
agent:
  name: untrusted_agent
  tools:
    mode: "allowlist"  # Only explicitly listed tools are available
    allowed:
      - file_read
      - http_get
      # No write operations, no code execution, no shell access
```

This prevents the agent from accessing dangerous tools even if it tries to call them.

## Related Pages

- [Built-in Tool Catalog](/docs/tools/catalog/) — Complete reference for all 50+ built-in tools
- [Creating Custom Tools](/docs/tools/custom/) — Extend Friday with the `@tool` decorator or `BaseTool` subclass
- [Agent Configuration](/docs/agents/configuration/) — Configure which tools each agent can access
