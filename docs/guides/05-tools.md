# Friday Agent Framework
## Section 5: Tools - Friday's Connection to the World

**Version:** 1.0
**Framework Version:** v0.1.0
**Last Updated:** 2026-01-24

---

## Overview

Tools are Friday's hands and eyes—the mechanisms through which agents interact with the external world. While memory enables learning and LLMs provide reasoning, tools enable **action**: reading files, making HTTP requests, executing code, querying databases, manipulating data, and interfacing with external systems.

Friday's tool system is built on a protocol-first architecture that makes creating, registering, and using tools remarkably simple. From 50+ built-in tools covering common operations to custom tools tailored for your domain, Friday provides a comprehensive and extensible toolkit for agent capabilities.

**This section covers:**
- Tool architecture and design principles
- Complete catalog of 50+ built-in tools
- Creating custom tools (function-based and class-based)
- Dynamic tool selection and context injection

**For Project Leaders:** Tools determine what your agents can actually *do*. The breadth and quality of the tool library directly impacts agent usefulness. Friday's tool system provides production-ready capabilities out of the box while enabling rapid custom tool development for domain-specific needs.

**For IT Leaders:** Tools represent the primary security boundary for agent systems. Friday's tool architecture includes sandboxing for filesystem and code execution, validation for all inputs, and configurable access control. The protocol-based design enables testing tools in isolation and auditing all tool executions via the transcript system.

**For Users:** Think of tools as the "apps" that Friday can use. Just as you use different applications for different tasks (browser for web, terminal for commands, editor for files), Friday uses tools. The more tools Friday has access to, the more tasks it can accomplish autonomously.

---

### MCP client tools in the current runtime

The integrated MCP client is a runtime tool provider under
`tools.providers.mcp`. It is disabled by default and connects only to local
stdio peers when enabled. Tool discovery happens at startup. Friday assigns
canonical names such as `mcp_demo_probe`, applies include/exclude filters,
sanitizes schemas, enforces discovery and registration caps, and routes an
admitted call through the normal tool loop. The default MCP provider mode is
`selected`; discovering a peer tool alone does not register it.

Friday Chat separately selects registered tools for each model turn. Schema
tokens and a reserved result budget reduce memory retrieval room; the
configured memory floor remains protected. Broad catalogs therefore cost
context even before a tool is called. See the tested
[MCP client setup and operation guide](17-mcp-client.md) for a local stdio
example, filters, output handling and diagnostics.

---

## 5.1 Tool Architecture & Design

### 5.1.1 The BaseTool Protocol

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

**For Project Leaders:** The protocol-first design means tools developed by different teams will work seamlessly together. This enables distributed development—one team builds domain tools, another builds integration tools, all compatible out of the box.

**For IT Leaders:** Protocol compliance ensures that all tools provide proper input validation and documentation. This reduces security risks from malformed inputs and improves auditability (every tool execution has a clear schema defining what was called and with what parameters).

**For Users:** The standardized interface means once you understand how one tool works, you understand how they all work. Learning to use Friday's tool system is learning a single pattern, not 50+ different interfaces.

---

### 5.1.2 Tool Schemas for LLMs

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

**Generated Schema (OpenAI Format):**

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
        "encoding": {"type": "string", "description": "File encoding. Use 'auto' for automatic detection.", "default": "auto"},
        "start_line": {"type": "integer", "description": "Starting line number (1-indexed, default: 1)", "minimum": 1, "default": 1},
        "max_lines": {"type": ["integer", "null"], "description": "Maximum number of lines to read (None for all)", "default": null}
      },
      "required": ["path"]
    }
  },
  "category": "filesystem",
  "tags": ["file", "read", "text", "cat"]
}
```

**Schema Features:**

- **Type Safety**: JSON Schema types enforce correct parameter types
- **Validation**: Constraints like `minimum: 1` prevent invalid inputs
- **Defaults**: Default values documented and applied automatically
- **Optional vs. Required**: Clear distinction via `required` array
- **Rich Descriptions**: Each parameter explains its purpose for the LLM

**Provider Compatibility:**

Friday abstracts provider-specific schema differences:

| Provider | Format | Tool Call Structure |
|----------|--------|---------------------|
| **OpenAI** | `{"type": "function", "function": {...}}` | Function calling with `tool_calls` array |
| **Anthropic** | `{"name": ..., "description": ..., "input_schema": {...}}` | Tool use blocks in content |
| **Google Gemini** | Function declaration format | Function calling with parameters |
| **Local (Ollama)** | OpenAI-compatible format | Function calling (if model supports) |

Friday's `to_schema(format="openai")` method handles conversion automatically. Agents never need to know which LLM provider is being used—the tool system abstracts this complexity.

**For Project Leaders:** Automatic schema generation means developers can focus on tool logic, not documentation. The Pydantic models serve as both runtime validation and LLM documentation, reducing maintenance overhead and keeping schemas in sync with code.

**For IT Leaders:** Schema-based validation prevents malformed tool calls from reaching execution. This is a critical security boundary—invalid inputs are rejected before tools ever run, with clear error messages for debugging.

**For Users:** The schemas ensure Friday always calls tools correctly. If a tool expects a file path but Friday tries to pass a number, the schema catches this error before anything happens, providing clear feedback about what went wrong.

---

### 5.1.3 Tool Result Standardization

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

**Success Case:**
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

**Failure Case:**
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

**Why Standardization Matters:**

**1. Consistent LLM Context:**
The `content` field ensures the LLM always receives tool outputs in a predictable format. This improves reasoning quality—the LLM doesn't need to parse arbitrary formats for each tool.

**2. Memory Extraction:**
The `data` field provides structured information for the memory extraction pipeline. Instead of parsing strings, the extractor can directly access `data["encoding"]` or `data["size_bytes"]`, improving extraction quality.

**3. Debugging & Audit:**
The `metadata` field creates an audit trail. When analyzing transcripts to understand why an agent made a decision, the metadata shows exactly what the tool returned, including details not visible to the LLM.

**4. Error Handling:**
The `error` field enables agents to distinguish failures from successes programmatically. Instead of parsing string outputs for error messages, agents check `if result.error: handle_error()`.

**For Project Leaders:** Standardized results mean tools from different teams are immediately compatible. A custom tool following the `ToolResult` pattern will work seamlessly with Friday's existing infrastructure (memory, transcripts, agents).

**For IT Leaders:** The separation of `content` (what the LLM sees) and `data` (structured output) enables fine-grained security controls. You can log `data` and `metadata` for audit purposes without exposing all details to the LLM context, where they might influence future reasoning.

**For Users:** When Friday executes a tool, you can see both the high-level result (the `content` Friday uses to reason) and the detailed breakdown (the `data` and `metadata` for deeper inspection). This transparency helps you understand what Friday knows and how it's making decisions.

---

## 5.2 Built-in Tool Catalog (50+ Tools)

Friday ships with over 50 production-ready tools organized into 7 categories. This section provides a complete reference for each tool including purpose, parameters, return format, and usage examples.

### 5.2.1 Filesystem Tools

Filesystem tools enable agents to read, write, navigate, and search files and directories.

#### **`file_read`** - Read File Contents

**Purpose:** Read text files with automatic encoding detection, pagination, and line range support.

**Parameters:**
- `path` (string, required): Path to the file to read
- `encoding` (string, default: `"auto"`): Encoding to use (`"auto"`, `"utf-8"`, `"latin-1"`, etc.)
- `start_line` (integer, default: `1`): Starting line number (1-indexed)
- `max_lines` (integer | null, default: `null`): Maximum lines to return

**Returns:**
- `content`: File contents (paginated if `max_lines` specified)
- `data`: Path, size, line counts, encoding info
- `metadata`: Truncation status, encoding details

**Example:**
```python
# Read entire file
result = await file_read.execute(path="/project/README.md")

# Read lines 50-100
result = await file_read.execute(
    path="/project/main.py",
    start_line=50,
    max_lines=50
)

# Force specific encoding
result = await file_read.execute(
    path="/data/legacy.txt",
    encoding="latin-1"
)
```

**Use Cases:**
- Examining configuration files before modifying them
- Reading source code for analysis or refactoring
- Paginating through large log files without memory exhaustion
- Debugging encoding issues with automatic detection

**Smart Features:**
- **Encoding Detection**: Uses `chardet` library to detect encoding with confidence scores
- **Pagination**: Efficiently reads specific line ranges without loading entire file
- **Truncation Notice**: Clear indicators when output is truncated
- **Error Handling**: Graceful failures for missing files, permission errors, or encoding issues

---

#### **`file_write`** - Write File Contents

**Purpose:** Write or overwrite a file with specified content.

**Parameters:**
- `path` (string, required): Path to the file to write
- `content` (string, required): Content to write to the file
- `encoding` (string, default: `"utf-8"`): Encoding to use
- `create_dirs` (boolean, default: `true`): Create parent directories if they don't exist

**Returns:**
- `content`: Success message with path and size
- `data`: Path, size written, encoding used
- `metadata`: File creation vs. overwrite indicator

**Example:**
```python
# Write a new file
result = await file_write.execute(
    path="/project/output.txt",
    content="Hello, World!\n"
)

# Write YAML config
config_yaml = """
server:
  host: localhost
  port: 8080
"""
result = await file_write.execute(
    path="/etc/myapp/config.yaml",
    content=config_yaml,
    create_dirs=True
)
```

**Security:** Uses `FilesystemSandbox` to validate paths and prevent writes outside allowed directories.

---

#### **`file_append`** - Append to File

**Purpose:** Append content to an existing file without overwriting.

**Parameters:**
- `path` (string, required): Path to the file
- `content` (string, required): Content to append
- `newline_before` (boolean, default: `true`): Add newline before appending

**Example:**
```python
# Append to log file
result = await file_append.execute(
    path="/logs/app.log",
    content="[INFO] Application started successfully",
    newline_before=True
)
```

---

#### **`directory_list`** - List Directory Contents

**Purpose:** List files and directories with optional filtering and recursion.

**Parameters:**
- `path` (string, default: `"."`): Directory to list
- `recursive` (boolean, default: `false`): Recursively list subdirectories
- `pattern` (string, optional): Glob pattern to filter (e.g., `"*.py"`)
- `show_hidden` (boolean, default: `false`): Include hidden files (starting with `.`)

**Returns:**
- `content`: Formatted listing with file types and sizes
- `data`: Array of file entries with metadata
- `metadata`: Total file count, directory depth

**Example:**
```python
# List Python files recursively
result = await directory_list.execute(
    path="/project/src",
    recursive=True,
    pattern="*.py"
)

# List current directory
result = await directory_list.execute(path=".")
```

---

#### **`directory_create`** - Create Directory

**Purpose:** Create a new directory with optional parent creation.

**Parameters:**
- `path` (string, required): Directory path to create
- `parents` (boolean, default: `true`): Create parent directories if they don't exist

**Example:**
```python
result = await directory_create.execute(
    path="/project/data/processed/2024",
    parents=True
)
```

---

#### **`file_delete`** - Delete File or Directory

**Purpose:** Delete a file or directory (with optional recursive deletion for directories).

**Parameters:**
- `path` (string, required): Path to delete
- `recursive` (boolean, default: `false`): Recursively delete directories

**Example:**
```python
# Delete single file
result = await file_delete.execute(path="/tmp/temp_file.txt")

# Delete directory recursively
result = await file_delete.execute(
    path="/tmp/build_artifacts",
    recursive=True
)
```

**Security:** Requires explicit `recursive=True` for directory deletion to prevent accidental data loss.

---

#### **`file_move`** - Move or Rename File

**Purpose:** Move or rename a file or directory.

**Parameters:**
- `source` (string, required): Source path
- `destination` (string, required): Destination path
- `overwrite` (boolean, default: `false`): Overwrite destination if it exists

**Example:**
```python
# Rename file
result = await file_move.execute(
    source="/project/draft.md",
    destination="/project/final.md"
)

# Move to different directory
result = await file_move.execute(
    source="/project/data.csv",
    destination="/archive/data_2024.csv"
)
```

---

#### **`file_info`** - Get File Metadata

**Purpose:** Retrieve file metadata including size, permissions, and timestamps.

**Parameters:**
- `path` (string, required): Path to the file or directory

**Returns:**
- `content`: Formatted metadata listing
- `data`: Structured metadata (size, permissions, owner, timestamps)

**Example:**
```python
result = await file_info.execute(path="/project/database.sqlite")

# Output includes:
# - Type (file/directory/symlink)
# - Size in bytes
# - Permissions (e.g., "-rw-r--r--")
# - Owner UID/GID
# - Modified/created/accessed timestamps
```

---

#### **`file_grep`** - Search File Contents

**Purpose:** Search for patterns in files using regular expressions with context lines.

**Parameters:**
- `path` (string, required): File to search
- `pattern` (string, required): Regular expression pattern
- `case_insensitive` (boolean, default: `false`): Case-insensitive search
- `context_lines` (integer, default: `0`): Number of context lines before/after match

**Example:**
```python
# Find all TODO comments in a file
result = await file_grep.execute(
    path="/project/main.py",
    pattern=r"#\s*TODO:.*",
    context_lines=2
)

# Case-insensitive search for error messages
result = await file_grep.execute(
    path="/logs/app.log",
    pattern="error|exception|failure",
    case_insensitive=True
)
```

**For Project Leaders:** Filesystem tools are the foundation for agent-driven development workflows. Agents can read codebases, analyze configurations, generate documentation, and automate file management tasks without human intervention.

**For IT Leaders:** All filesystem tools use `FilesystemSandbox` for path validation, preventing directory traversal attacks and restricting access to configured safe directories. Audit logs capture every file operation for compliance tracking.

**For Users:** These tools give Friday the ability to work with your files just like you would—reading, writing, organizing, and searching. Friday can examine your codebase, process data files, or manage project documentation autonomously.

---

### 5.2.2 Shell & System Tools

Shell tools enable command execution and system introspection.

#### **`execute_command`** - Execute Shell Command

**Purpose:** Execute arbitrary shell commands with timeout and working directory control.

**Parameters:**
- `command` (string, required): Shell command to execute
- `cwd` (string, optional): Working directory for command execution
- `timeout` (integer, default: `30`): Timeout in seconds
- `capture_output` (boolean, default: `true`): Capture stdout/stderr

**Returns:**
- `content`: Combined stdout and stderr
- `data`: Return code, stdout, stderr separately
- `metadata`: Execution time, working directory

**Example:**
```python
# Run build command
result = await execute_command.execute(
    command="npm run build",
    cwd="/project",
    timeout=120
)

# Check disk usage
result = await execute_command.execute(
    command="df -h"
)
```

**Security Warnings:**
- **Command Injection Risk**: Never pass unsanitized user input directly to commands
- **Allowlist Preferred**: Configure command allowlists in production to limit what can be executed
- **Timeout Enforcement**: Always specify timeouts to prevent runaway processes
- **Sandbox Mode**: Use `ShellSandbox` to restrict allowed commands and paths

**Alternatives:** For common operations, prefer specialized tools (`git_status` instead of `execute_command("git status")`) for better safety and structured outputs.

---

#### **`system_info`** - Get System Information

**Purpose:** Retrieve system information including OS, CPU, memory, and disk usage.

**Parameters:** None

**Returns:**
- OS name and version
- CPU count and architecture
- Total/available memory
- Disk usage statistics

**Example:**
```python
result = await system_info.execute()
```

**Use Cases:**
- Determining system capabilities before executing resource-intensive tasks
- Monitoring agent resource consumption
- Debugging environment-specific issues

---

### 5.2.3 Web & Network Tools

Web tools provide HTTP client capabilities and content fetching.

#### **`http_get`** - HTTP GET Request

**Purpose:** Make HTTP GET requests with headers and query parameters.

**Parameters:**
- `url` (string, required): URL to request
- `headers` (object, optional): HTTP headers
- `params` (object, optional): Query parameters
- `timeout` (integer, default: `30`): Request timeout in seconds

**Returns:**
- `content`: Formatted response (status, headers, body)
- `data`: Structured response with status code, headers, body
- `metadata`: Response time, content type, size

**Example:**
```python
# Simple GET request
result = await http_get.execute(
    url="https://api.github.com/users/octocat"
)

# With headers and parameters
result = await http_get.execute(
    url="https://api.example.com/search",
    headers={"Authorization": "Bearer token123"},
    params={"q": "Friday framework", "limit": 10}
)
```

**Features:**
- Automatic JSON parsing for `application/json` responses
- Response body truncation for large responses (first 5000 chars)
- Complete header capture for debugging

---

#### **`http_post`** - HTTP POST Request

**Purpose:** Make HTTP POST requests with JSON or form data.

**Parameters:**
- `url` (string, required): URL to request
- `json_data` (object, optional): JSON body to send
- `form_data` (object, optional): Form data to send (mutually exclusive with `json_data`)
- `headers` (object, optional): HTTP headers
- `timeout` (integer, default: `30`): Request timeout

**Example:**
```python
# POST JSON data
result = await http_post.execute(
    url="https://api.example.com/users",
    json_data={"name": "Alice", "email": "alice@example.com"}
)

# POST form data
result = await http_post.execute(
    url="https://example.com/submit",
    form_data={"username": "alice", "action": "login"}
)
```

---

#### **`http_put`**, **`http_delete`** - Other HTTP Methods

**Purpose:** HTTP PUT and DELETE requests for RESTful API interactions.

**Parameters:** Similar to `http_post` (PUT) and `http_get` (DELETE)

**Example:**
```python
# Update resource
result = await http_put.execute(
    url="https://api.example.com/users/123",
    json_data={"email": "newemail@example.com"}
)

# Delete resource
result = await http_delete.execute(
    url="https://api.example.com/users/123"
)
```

---

#### **`http_download`** - Download File from URL

**Purpose:** Download a file from a URL and save it locally with streaming support.

**Parameters:**
- `url` (string, required): URL to download from
- `destination` (string, required): Local path to save the file
- `timeout` (integer, default: `60`): Download timeout

**Returns:**
- `content`: Success message with size downloaded
- `data`: Bytes downloaded, final path
- `metadata`: Download time, HTTP status

**Example:**
```python
result = await http_download.execute(
    url="https://example.com/dataset.csv",
    destination="/data/dataset.csv"
)
```

**Features:**
- **Streaming**: Downloads in chunks to avoid memory exhaustion
- **Progress Tracking**: Reports total bytes downloaded
- **Directory Creation**: Automatically creates parent directories
- **Validation**: Uses `FilesystemSandbox` to validate destination paths

---

#### **`http_upload`** - Upload File to URL

**Purpose:** Upload a local file to a URL using multipart form data.

**Parameters:**
- `url` (string, required): URL to upload to
- `file_path` (string, required): Local file path to upload
- `field_name` (string, default: `"file"`): Form field name for the file
- `headers` (object, optional): Additional headers
- `timeout` (integer, default: `60`): Upload timeout

**Example:**
```python
result = await http_upload.execute(
    url="https://api.example.com/upload",
    file_path="/data/report.pdf",
    field_name="document",
    headers={"Authorization": "Bearer token123"}
)
```

---

#### **`web_search`** - Web Search Integration

**Purpose:** Perform web searches using configured search APIs (DuckDuckGo, Google, Bing).

**Parameters:**
- `query` (string, required): Search query
- `num_results` (integer, default: `10`): Number of results to return
- `safe_search` (boolean, default: `true`): Enable safe search filtering

**Returns:**
- `content`: Formatted search results with titles, URLs, and snippets
- `data`: Array of search result objects
- `metadata`: Search time, result count, source

**Example:**
```python
result = await web_search.execute(
    query="Friday agent framework Python",
    num_results=5
)
```

**Configuration:** Requires API key for search provider in environment variables (`GOOGLE_SEARCH_API_KEY`, `BING_SEARCH_API_KEY`, etc.)

---

#### **`scrape_page`** - Web Page Scraping

**Purpose:** Fetch and parse HTML pages, extracting text content with optional CSS selectors.

**Parameters:**
- `url` (string, required): URL to scrape
- `selector` (string, optional): CSS selector to extract specific elements
- `timeout` (integer, default: `30`): Request timeout

**Returns:**
- `content`: Extracted text content
- `data`: Parsed HTML structure (BeautifulSoup object serialized)
- `metadata`: Page title, response time, content length

**Example:**
```python
# Scrape entire page
result = await scrape_page.execute(
    url="https://example.com/article"
)

# Extract specific section
result = await scrape_page.execute(
    url="https://docs.python.org/3/tutorial/",
    selector="div.body"
)
```

**Features:**
- Automatic HTML parsing with BeautifulSoup
- JavaScript-rendered content requires separate headless browser integration (not included)
- Respects `robots.txt` (configurable)

**For Project Leaders:** Web tools enable agents to gather information from external sources, integrate with APIs, and automate data collection workflows. This transforms agents from isolated systems into connected intelligence that can pull information from the broader internet.

**For IT Leaders:** All HTTP tools use `httpx` with configurable timeouts, automatic retry with exponential backoff, and connection pooling. Rate limiting and user-agent configuration are recommended for production use to avoid being blocked by target servers.

**For Users:** Web tools let Friday access online information just like you would with a browser—searching, fetching pages, downloading files, and interacting with APIs. Friday can research topics, gather data, or integrate with web services on your behalf.

---

### 5.2.4 Git Tools

Git tools provide version control operations for repository management.

#### **`git_status`** - Git Repository Status

**Purpose:** Show the working tree status of a git repository.

**Parameters:**
- `path` (string, default: `"."`): Repository path

**Returns:**
- `content`: Git status output (standard format)
- `data`: Parsed status information (modified files, untracked files, branch)
- `metadata`: Repository path, branch name, is dirty

**Example:**
```python
result = await git_status.execute(path="/project")
```

**Output Format:**
```
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  modified:   src/main.py
  modified:   tests/test_main.py

Untracked files:
  docs/new_feature.md
```

---

#### **`git_diff`** - Show Git Diff

**Purpose:** Show changes between commits, commit and working tree, or staged changes.

**Parameters:**
- `path` (string, default: `"."`): Repository path
- `staged` (boolean, default: `false`): Show staged changes (`--staged`)
- `file` (string, optional): Specific file to diff

**Returns:**
- `content`: Unified diff output
- `data`: Parsed diff with file paths, change counts
- `metadata`: Number of files changed, insertions, deletions

**Example:**
```python
# Show unstaged changes
result = await git_diff.execute(path="/project")

# Show staged changes
result = await git_diff.execute(path="/project", staged=True)

# Diff specific file
result = await git_diff.execute(
    path="/project",
    file="src/main.py"
)
```

---

#### **`git_log`** - Show Commit Log

**Purpose:** Display commit history with customizable format and depth.

**Parameters:**
- `path` (string, default: `"."`): Repository path
- `count` (integer, default: `10`): Number of commits to show
- `oneline` (boolean, default: `true`): One-line format (`--oneline`)

**Returns:**
- `content`: Formatted commit log
- `data`: Array of commit objects (hash, author, date, message)
- `metadata`: Total commits retrieved, branch

**Example:**
```python
# Recent commits (one-line)
result = await git_log.execute(path="/project", count=5)

# Detailed commits
result = await git_log.execute(
    path="/project",
    count=3,
    oneline=False
)
```

---

#### **`git_commit`** - Create Commit

**Purpose:** Stage changes and create a commit with a message.

**Parameters:**
- `path` (string, default: `"."`): Repository path
- `message` (string, required): Commit message
- `files` (array, optional): Specific files to stage (None for all changes)
- `author` (string, optional): Author override (`"Name <email>"`)

**Returns:**
- `content`: Commit summary (hash, message, files changed)
- `data`: Commit hash, timestamp, files changed
- `metadata`: Repository path, branch, commit hash

**Example:**
```python
# Commit all changes
result = await git_commit.execute(
    path="/project",
    message="Add user authentication feature"
)

# Commit specific files
result = await git_commit.execute(
    path="/project",
    message="Update configuration",
    files=["config.yaml", "README.md"]
)
```

---

#### **`git_push`**, **`git_pull`** - Remote Operations

**Purpose:** Push commits to remote or pull changes from remote.

**Parameters:**
- `path` (string, default: `"."`): Repository path
- `remote` (string, default: `"origin"`): Remote name
- `branch` (string, optional): Branch name (defaults to current branch)

**Example:**
```python
# Push to origin
result = await git_push.execute(path="/project")

# Pull from origin
result = await git_pull.execute(path="/project")

# Push to specific remote/branch
result = await git_push.execute(
    path="/project",
    remote="upstream",
    branch="feature-branch"
)
```

---

#### **`git_checkout`** - Switch Branches

**Purpose:** Switch to a different branch or create a new branch.

**Parameters:**
- `path` (string, default: `"."`): Repository path
- `branch` (string, required): Branch name to checkout
- `create` (boolean, default: `false`): Create branch if it doesn't exist (`-b`)

**Example:**
```python
# Switch to existing branch
result = await git_checkout.execute(
    path="/project",
    branch="develop"
)

# Create and switch to new branch
result = await git_checkout.execute(
    path="/project",
    branch="feature/new-ui",
    create=True
)
```

---

#### **`git_branches`** - List Branches

**Purpose:** List all branches (local and remote) with current branch indicator.

**Parameters:**
- `path` (string, default: `"."`): Repository path
- `remote` (boolean, default: `false`): Show remote branches

**Example:**
```python
# List local branches
result = await git_branches.execute(path="/project")

# List remote branches
result = await git_branches.execute(path="/project", remote=True)
```

**For Project Leaders:** Git tools enable agents to autonomously manage code repositories—committing changes, creating branches, reviewing diffs, and synchronizing with remotes. This supports agent-driven development workflows where Friday generates code, tests it, and commits working changes automatically.

**For IT Leaders:** Git operations are audited through transcripts. All commits created by Friday can be attributed via the transcript system, ensuring traceability. Configure commit authorship to clearly identify agent-generated commits (e.g., `"Friday Agent <noreply@yourcompany.com>"`).

**For Users:** Git tools give Friday version control capabilities. Friday can commit its work, create feature branches, review your uncommitted changes, and even handle repository synchronization—all the git operations you'd perform manually, but automated and integrated into Friday's workflows.

---

### 5.2.5 Data Manipulation Tools

Data tools parse, query, and transform structured data formats.

#### **`json_parse`** - Parse JSON

**Purpose:** Parse JSON strings into structured data with validation.

**Parameters:**
- `json_string` (string, required): JSON string to parse

**Returns:**
- `content`: Pretty-printed JSON
- `data`: Parsed Python object (dict/list)
- `metadata`: Top-level keys, nesting depth, size

**Example:**
```python
result = await json_parse.execute(
    json_string='{"name": "Alice", "age": 30, "city": "NYC"}'
)
```

---

#### **`json_query`** - Query JSON with JSONPath

**Purpose:** Query JSON data using JSONPath expressions.

**Parameters:**
- `data` (object, required): JSON data (dict or list)
- `query` (string, required): JSONPath expression (e.g., `"$.store.book[*].title"`)

**Returns:**
- `content`: Formatted query results
- `data`: Array of matched values
- `metadata`: Match count, query complexity

**Example:**
```python
data = {
    "store": {
        "book": [
            {"title": "Book 1", "price": 10},
            {"title": "Book 2", "price": 15}
        ]
    }
}

# Extract all book titles
result = await json_query.execute(
    data=data,
    query="$.store.book[*].title"
)
# Returns: ["Book 1", "Book 2"]
```

---

#### **`yaml_parse`**, **`yaml_dump`** - YAML Operations

**Purpose:** Parse YAML strings or dump Python objects to YAML.

**Example:**
```python
# Parse YAML
result = await yaml_parse.execute(
    yaml_string="""
    server:
      host: localhost
      port: 8080
    """
)

# Dump to YAML
result = await yaml_dump.execute(
    data={"server": {"host": "localhost", "port": 8080}}
)
```

---

#### **`csv_read`**, **`csv_write`** - CSV Operations

**Purpose:** Read and write CSV files with header support.

**`csv_read` Parameters:**
- `path` (string, required): CSV file path
- `delimiter` (string, default: `","`): Column delimiter
- `has_header` (boolean, default: `true`): First row is header

**Returns:**
- `content`: Formatted table view
- `data`: Array of row objects (if header) or arrays (if no header)
- `metadata`: Row count, column count, column names

**Example:**
```python
# Read CSV with header
result = await csv_read.execute(path="/data/users.csv")

# Read TSV without header
result = await csv_read.execute(
    path="/data/data.tsv",
    delimiter="\t",
    has_header=False
)
```

**`csv_write` Example:**
```python
data = [
    {"name": "Alice", "age": 30, "city": "NYC"},
    {"name": "Bob", "age": 25, "city": "SF"}
]

result = await csv_write.execute(
    path="/data/output.csv",
    data=data
)
```

---

#### **`xml_parse`**, **`xml_query`** - XML Operations

**Purpose:** Parse XML and query with XPath.

**Example:**
```python
# Parse XML
result = await xml_parse.execute(
    xml_string="<root><item id='1'>Value</item></root>"
)

# XPath query
result = await xml_query.execute(
    xml_string="<root><item id='1'>Value</item></root>",
    xpath="//item[@id='1']/text()"
)
```

---

#### **`toml_parse`** - TOML Operations

**Purpose:** Parse TOML configuration files (commonly used in Python projects like `pyproject.toml`).

**Example:**
```python
result = await toml_parse.execute(
    toml_string="""
    [project]
    name = "friday-framework"
    version = "0.1.0"
    """
)
```

**For Project Leaders:** Data manipulation tools enable agents to work with structured data from various sources—configuration files, API responses, databases, and data files. Agents can parse, transform, query, and generate data in any standard format without custom code.

**For IT Leaders:** All parsing tools include error handling for malformed data with clear error messages. No arbitrary code execution (unlike Python's `pickle`)—these tools only parse and query standard data formats safely.

**For Users:** Data tools let Friday understand and work with structured information. Friday can read your config files, query API responses, process CSV datasets, or generate formatted output in any standard format you need.

---

### 5.2.6 Text Processing Tools

Text tools perform string operations, regular expressions, and text transformations.

#### **`regex_search`** - Regular Expression Search

**Purpose:** Search text using regular expressions with capture groups.

**Parameters:**
- `text` (string, required): Text to search
- `pattern` (string, required): Regular expression pattern
- `flags` (array, optional): Regex flags (`["IGNORECASE"]`, `["MULTILINE"]`, etc.)

**Returns:**
- `content`: Formatted matches
- `data`: Array of match objects with groups and positions
- `metadata`: Match count, pattern used

**Example:**
```python
# Extract email addresses
result = await regex_search.execute(
    text="Contact: alice@example.com or bob@test.org",
    pattern=r"[\w\.-]+@[\w\.-]+\.\w+"
)

# Extract with capture groups
result = await regex_search.execute(
    text="Version: 1.2.3",
    pattern=r"Version: (\d+)\.(\d+)\.(\d+)"
)
# Returns: match with groups ["1", "2", "3"]
```

---

#### **`regex_replace`** - Regular Expression Replace

**Purpose:** Replace text matching a regular expression pattern.

**Parameters:**
- `text` (string, required): Text to modify
- `pattern` (string, required): Regular expression pattern
- `replacement` (string, required): Replacement string (supports backreferences like `\1`)
- `flags` (array, optional): Regex flags

**Example:**
```python
# Replace dates from MM/DD/YYYY to YYYY-MM-DD
result = await regex_replace.execute(
    text="The date is 12/25/2024",
    pattern=r"(\d{2})/(\d{2})/(\d{4})",
    replacement=r"\3-\1-\2"
)
# Returns: "The date is 2024-12-25"
```

---

#### **`text_transform`** - Text Transformations

**Purpose:** Apply common text transformations (case, trimming, line operations).

**Parameters:**
- `text` (string, required): Text to transform
- `operation` (string, required): Transformation type
  - `"uppercase"`, `"lowercase"`, `"titlecase"`, `"capitalize"`
  - `"trim"`, `"trim_start"`, `"trim_end"`
  - `"remove_duplicates"` (duplicate lines)
  - `"sort_lines"`, `"reverse_lines"`
  - `"remove_empty_lines"`

**Example:**
```python
# Convert to uppercase
result = await text_transform.execute(
    text="hello world",
    operation="uppercase"
)

# Remove empty lines and sort
text = """
apple

banana
apple
cherry

"""
result = await text_transform.execute(
    text=text,
    operation="remove_empty_lines"
)
# Then sort
result = await text_transform.execute(
    text=result.content,
    operation="sort_lines"
)
```

---

#### **`format_text`** - Text Formatting

**Purpose:** Format text with syntax highlighting, indentation, or templates.

**Parameters:**
- `text` (string, required): Text to format
- `format` (string, required): Format type
  - `"markdown"`: Format as markdown
  - `"code_python"`, `"code_javascript"`, etc.: Syntax highlighting
  - `"json_pretty"`: Pretty-print JSON
  - `"indent"`: Add indentation (with `indent_level` param)

**Example:**
```python
# Pretty-print JSON
result = await format_text.execute(
    text='{"name":"Alice","age":30}',
    format="json_pretty"
)

# Indent code
result = await format_text.execute(
    text="def foo():\nprint('hello')",
    format="indent",
    indent_level=4
)
```

**For Project Leaders:** Text tools enable agents to parse unstructured text, extract information with regex, transform formats, and generate formatted output. This is essential for documentation generation, log parsing, and text-based data extraction.

**For IT Leaders:** Regex operations are compiled and validated before execution, preventing ReDoS (Regular Expression Denial of Service) attacks with timeout enforcement on long-running patterns.

**For Users:** Text tools give Friday the ability to manipulate text in sophisticated ways—searching for patterns, reformatting data, cleaning up text, or extracting structured information from unstructured sources.

---

### 5.2.7 Code Execution Tools

Code execution tools run code in isolated environments with safety constraints.

#### **`python_execute`** - Execute Python Code

**Purpose:** Execute Python code in a sandboxed subprocess with timeout and resource limits.

**Parameters:**
- `code` (string, required): Python code to execute
- `timeout` (integer, default: `30`): Execution timeout in seconds

**Returns:**
- `content`: Combined stdout, stderr, and return value
- `data`: Stdout, stderr, return value separately, exit code
- `metadata`: Execution time, sandbox type, resource usage

**Example:**
```python
# Simple calculation
result = await python_execute.execute(
    code="""
x = 10
y = 20
print(f"Sum: {x + y}")
"""
)

# Data processing
result = await python_execute.execute(
    code="""
import json
data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
names = [u["name"] for u in data["users"]]
print(names)
""",
    timeout=10
)
```

**Security:**

Friday uses `SubprocessSandbox` for Python code execution:

- **Process Isolation**: Code runs in separate subprocess, not in Friday's process
- **Timeout Enforcement**: Hard timeout kills runaway processes
- **Resource Limits**: Configurable memory and CPU limits (via `ulimit` or Docker)
- **No Network Access (Docker)**: When using Docker sandbox, no external network access
- **Module Restrictions**: Configurable allowlist of importable modules

**Current Status (v0.1.0):**
- Subprocess isolation: ✅ Implemented
- Timeout enforcement: ✅ Implemented
- Docker-based sandboxing: ⏳ Planned (Phase 5)

**Use Cases:**
- Data analysis and computation
- Testing code snippets
- Generating data or processing files
- Validating algorithms

**Warnings:**
- **Untrusted Code**: Never execute untrusted user code without Docker sandboxing (coming in Phase 5)
- **Filesystem Access**: Code has access to Friday's filesystem in subprocess mode; use Docker for isolation
- **API Keys**: Be cautious executing code that could access environment variables

---

#### **`code_format`** - Format Code

**Purpose:** Automatically format code using language-specific formatters (Black for Python, Prettier for JS/TS).

**Parameters:**
- `code` (string, required): Code to format
- `language` (string, required): Language (`"python"`, `"javascript"`, `"typescript"`, etc.)

**Example:**
```python
# Format Python code
result = await code_format.execute(
    code="def foo(x,y):return x+y",
    language="python"
)
# Returns: "def foo(x, y):\n    return x + y\n"
```

---

#### **`code_analyze`** - Static Code Analysis

**Purpose:** Run static analysis tools (Ruff, ESLint, Pylint) to check code quality.

**Parameters:**
- `code` (string, required): Code to analyze
- `language` (string, required): Language
- `rules` (array, optional): Specific rules to check

**Returns:**
- `content`: Formatted linting report
- `data`: Array of issue objects (file, line, column, rule, severity, message)
- `metadata`: Total issues, errors, warnings, suggestions

**Example:**
```python
result = await code_analyze.execute(
    code="""
def unused_function():
    x = 1
    y = 2
    print(x)
""",
    language="python"
)
# Reports: unused variable 'y', unused function
```

**For Project Leaders:** Code execution tools enable agents to write, test, and validate code autonomously. Agents can prototype solutions, run experiments, and verify implementations without human intervention. This is the foundation for agent-driven development.

**For IT Leaders:** Code execution is the highest-risk tool category. Current subprocess isolation provides basic safety; Docker-based sandboxing (Phase 5 roadmap) will provide production-grade isolation for untrusted code. Until then, only execute agent-generated code in trusted environments or with manual review.

**For Users:** Code execution tools let Friday run code to solve problems, perform calculations, or validate ideas. Friday can test out a solution, see if it works, and iterate—just like you would when prototyping code.

---

### Summary: Built-in Tool Catalog

**By Category:**

| Category | Tool Count | Examples |
|----------|------------|----------|
| **Filesystem** | 10+ | `file_read`, `file_write`, `directory_list`, `file_grep` |
| **Shell & System** | 5+ | `execute_command`, `system_info` |
| **Web & Network** | 8+ | `http_get`, `http_post`, `web_search`, `scrape_page`, `http_download` |
| **Git** | 8+ | `git_status`, `git_commit`, `git_diff`, `git_log`, `git_push` |
| **Data Manipulation** | 10+ | `json_parse`, `csv_read`, `yaml_parse`, `xml_query` |
| **Text Processing** | 6+ | `regex_search`, `regex_replace`, `text_transform` |
| **Code Execution** | 3+ | `python_execute`, `code_format`, `code_analyze` |
| **Integrations** | 5+ | `email_send`, `slack_post`, `database_query` (enterprise) |
| **Memory** | 4+ | `memory_store`, `memory_search`, `lifecycle_manage` |
| **Utility** | 4+ | `echo`, `get_datetime`, `sleep`, `random` |

**Total:** 50+ tools covering the most common agent operations.

**For Project Leaders:** The breadth of the built-in catalog means most common agent tasks are supported out-of-the-box. Agents can start delivering value immediately without custom tool development. Custom tools fill domain-specific gaps.

**For IT Leaders:** Each tool category has different security profiles. Filesystem and code execution tools require the most scrutiny; data parsing tools are lowest risk. Configure tool access per-agent based on least-privilege principles.

**For Users:** These 50+ tools give Friday a wide range of capabilities from day one. Friday can work with files, access the web, manage git repositories, process data, and execute code—all the fundamental operations needed for sophisticated agent workflows.

---

## 5.3 Creating Custom Tools

Friday's tool system is designed for extensibility. Creating custom tools is straightforward—you can define tools as simple Python functions or full classes depending on complexity.

### 5.3.1 Function-Based Tools (@tool Decorator)

The fastest way to create a tool: decorate a Python function with `@tool` and Friday automatically generates schemas from type hints and docstrings.

**Basic Example:**

```python
from friday_tools import tool

@tool(name="greet", description="Greet a person by name", category="utility")
async def greet(name: str, greeting: str = "Hello") -> str:
    """
    Greet someone with a customizable greeting.

    Args:
        name: The person's name to greet.
        greeting: The greeting to use (default: "Hello").

    Returns:
        A greeting message.
    """
    return f"{greeting}, {name}!"
```

**What Friday Generates:**

The `@tool` decorator automatically creates:

1. **Tool Schema:**
```json
{
  "name": "greet",
  "description": "Greet a person by name",
  "category": "utility",
  "parameters": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "The person's name to greet."
      },
      "greeting": {
        "type": "string",
        "description": "The greeting to use (default: \"Hello\").",
        "default": "Hello"
      }
    },
    "required": ["name"]
  }
}
```

2. **Automatic Registration:**
The tool is automatically registered with the default tool registry and available to all agents.

3. **Type Validation:**
Friday validates that arguments match the type hints before calling the function. If an agent tries to call `greet(name=123)`, it's rejected before execution.

**Complex Example: API Client Tool**

```python
from friday_tools import tool
import httpx

@tool(
    name="get_weather",
    description="Get current weather for a city",
    category="integrations",
    tags=["weather", "api", "external"]
)
async def get_weather(city: str, units: str = "metric") -> str:
    """
    Fetch current weather data for a city using OpenWeatherMap API.

    Args:
        city: City name (e.g., "New York", "London").
        units: Temperature units - "metric" (Celsius) or "imperial" (Fahrenheit).

    Returns:
        Formatted weather summary with temperature, conditions, and humidity.
    """
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        return "Error: OPENWEATHERMAP_API_KEY not configured"

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "units": units, "appid": api_key}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

        if response.status_code != 200:
            return f"Error: Unable to fetch weather for {city}"

        data = response.json()
        temp = data["main"]["temp"]
        conditions = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]

        unit_symbol = "°C" if units == "metric" else "°F"
        return f"Weather in {city}: {temp}{unit_symbol}, {conditions}, {humidity}% humidity"

# Usage by agent:
# result = await get_weather.execute(city="San Francisco", units="imperial")
```

**Function Tool Features:**

- **Automatic Schema Generation**: Type hints become JSON Schema types
- **Default Values**: Function defaults become parameter defaults
- **Docstring Parsing**: Google-style docstrings provide parameter descriptions
- **Async Support**: Both `async def` and regular `def` functions work
- **Error Handling**: Exceptions are caught and returned as error messages

**When to Use Function Tools:**

✅ **Use function-based tools when:**
- Tool logic fits in a single function
- No initialization or state management needed
- Simple input/output patterns
- Rapid prototyping or one-off tools

❌ **Avoid function-based tools when:**
- Need to manage connections or resources (database, API clients)
- Require complex initialization logic
- Need to return structured `ToolResult` with rich metadata
- Want fine-grained control over schema generation

---

### 5.3.2 Class-Based Tools (BaseTool Subclass)

For more complex tools, implement the `BaseTool` protocol directly as a class. This provides full control over initialization, resource management, and result formatting.

**Basic Example:**

```python
from friday_tools import BaseTool, ToolResult
from typing import Any

class CalculatorTool(BaseTool):
    """Perform arithmetic calculations."""

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Perform arithmetic operations: add, subtract, multiply, divide."

    @property
    def category(self) -> str:
        return "utility"

    @property
    def tags(self) -> list[str]:
        return ["math", "calculator", "arithmetic"]

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Operation to perform",
                    "enum": ["add", "subtract", "multiply", "divide"]
                },
                "a": {
                    "type": "number",
                    "description": "First operand"
                },
                "b": {
                    "type": "number",
                    "description": "Second operand"
                }
            },
            "required": ["operation", "a", "b"]
        }

    async def execute(self, **kwargs: Any) -> str:
        """Execute the calculation."""
        operation = kwargs["operation"]
        a = float(kwargs["a"])
        b = float(kwargs["b"])

        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return "Error: Division by zero"
            result = a / b
        else:
            return f"Error: Unknown operation '{operation}'"

        return f"{a} {operation} {b} = {result}"

# Register manually
from friday_tools import get_default_registry
registry = get_default_registry()
registry.register(CalculatorTool())
```

**Advanced Example: Database Query Tool**

```python
from friday_tools import BaseTool, ToolResult
from typing import Any
import asyncpg  # PostgreSQL async driver

class DatabaseQueryTool(BaseTool):
    """Execute SQL queries against a PostgreSQL database."""

    def __init__(self, connection_pool: asyncpg.Pool):
        """
        Initialize with a connection pool.

        Args:
            connection_pool: asyncpg connection pool for database access.
        """
        self._pool = connection_pool

    @property
    def name(self) -> str:
        return "database_query"

    @property
    def description(self) -> str:
        return "Execute a SQL query against the database and return results."

    @property
    def category(self) -> str:
        return "integrations"

    @property
    def tags(self) -> list[str]:
        return ["database", "sql", "postgresql"]

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL query to execute (SELECT only for safety)"
                },
                "params": {
                    "type": "array",
                    "description": "Query parameters for placeholders ($1, $2, ...)",
                    "items": {"type": ["string", "number", "boolean", "null"]},
                    "default": []
                }
            },
            "required": ["query"]
        }

    async def execute(self, **kwargs: Any) -> str:
        """Execute SQL query and return results."""
        query = kwargs["query"]
        params = kwargs.get("params", [])

        # Safety check: only allow SELECT queries
        if not query.strip().upper().startswith("SELECT"):
            return ToolResult(
                content="Error: Only SELECT queries are allowed for safety",
                error="Non-SELECT query attempted"
            ).content

        try:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(query, *params)

            if not rows:
                return ToolResult(
                    content="Query returned no results",
                    data=[],
                    metadata={"row_count": 0, "query": query}
                ).content

            # Format results as table
            columns = rows[0].keys()
            formatted_rows = [dict(row) for row in rows]

            # Generate table view
            header = " | ".join(columns)
            separator = "-" * len(header)
            rows_text = "\n".join([
                " | ".join(str(row[col]) for col in columns)
                for row in formatted_rows
            ])

            content = f"{header}\n{separator}\n{rows_text}\n\nTotal rows: {len(rows)}"

            return ToolResult(
                content=content,
                data=formatted_rows,
                metadata={
                    "row_count": len(rows),
                    "column_count": len(columns),
                    "columns": list(columns),
                    "query": query
                }
            ).content

        except asyncpg.PostgresError as e:
            return ToolResult(
                content=f"Database error: {e}",
                error=str(e),
                metadata={"query": query}
            ).content
        except Exception as e:
            return ToolResult(
                content=f"Error executing query: {e}",
                error=str(e),
                metadata={"query": query}
            ).content

# Initialize and register
import asyncio

async def setup_database_tool():
    # Create connection pool
    pool = await asyncpg.create_pool(
        host="localhost",
        database="mydb",
        user="friday",
        password="secret"
    )

    # Create and register tool
    db_tool = DatabaseQueryTool(connection_pool=pool)
    get_default_registry().register(db_tool)

    return db_tool
```

**Class Tool Features:**

- **Initialization**: `__init__()` for resource setup (connections, clients, config)
- **State Management**: Instance variables for maintaining state across calls
- **Resource Cleanup**: Implement `__del__()` or context manager for cleanup
- **Rich Results**: Return `ToolResult` objects with structured data and metadata
- **Custom Validation**: Validate parameters beyond schema (business logic checks)

**When to Use Class Tools:**

✅ **Use class-based tools when:**
- Need to manage connections or resources (DB, API clients, file handles)
- Require initialization logic or configuration
- Want to return rich `ToolResult` objects with structured data
- Need fine-grained control over schema generation
- Implementing complex validation logic

**For Project Leaders:** Function-based tools enable rapid tool development—developers can create tools in minutes with minimal boilerplate. Class-based tools provide enterprise-grade capabilities for complex integrations. Both approaches coexist seamlessly.

**For IT Leaders:** Class-based tools enable proper resource management (connection pooling, cleanup) essential for production deployments. They also support advanced patterns like caching, rate limiting, and circuit breakers.

**For Users:** The two approaches give flexibility—simple tools are trivial to create, complex tools are still manageable. Whether you need a quick utility or a sophisticated integration, Friday's tool system scales to your needs.

---

### 5.3.3 Tool Categories & Discovery

Friday organizes tools into categories for focused discovery and context-aware selection.

**Standard Categories:**

| Category | Purpose | Example Tools |
|----------|---------|---------------|
| `filesystem` | File and directory operations | `file_read`, `directory_list` |
| `shell` | Command execution and system info | `execute_command`, `system_info` |
| `web` | HTTP client and web scraping | `http_get`, `web_search` |
| `git` | Version control operations | `git_status`, `git_commit` |
| `data` | Data format parsing and querying | `json_parse`, `csv_read` |
| `text` | String manipulation and regex | `regex_search`, `text_transform` |
| `code` | Code execution and analysis | `python_execute`, `code_format` |
| `integrations` | External service integrations | `email_send`, `slack_post` |
| `memory` | Memory system operations | `memory_search`, `lifecycle_manage` |
| `utility` | General utilities | `echo`, `get_datetime` |

**Assigning Categories:**

```python
# Function tool
@tool(category="integrations")
async def send_slack_message(channel: str, message: str) -> str:
    ...

# Class tool
class MyTool(BaseTool):
    @property
    def category(self) -> str:
        return "integrations"
```

**Category-Based Discovery:**

Agents and users can query tools by category:

```python
# Get all filesystem tools
from friday_tools import get_default_registry

registry = get_default_registry()
filesystem_tools = registry.get_tools_by_category("filesystem")

# Get schemas for web tools (for LLM context)
web_schemas = registry.get_schemas_by_category("web", format="openai")
```

**Using Tags for Fine-Grained Filtering:**

Beyond categories, tools can have multiple tags:

```python
@tool(
    category="data",
    tags=["json", "parser", "query", "readonly"]
)
async def json_query(...):
    ...

# Query by tags
json_tools = registry.get_tools_by_tags(["json"], match_all=False)
# Returns tools with ANY of the specified tags

readonly_tools = registry.get_tools_by_tags(["readonly"], match_all=False)
# Returns tools that are read-only (safe for untrusted agents)
```

**Category and Tag Strategy:**

**Categories** (single value):
- Broad functional grouping
- Used for major context partitioning (only include filesystem tools for file tasks)
- Affects tool recommendation algorithm

**Tags** (multiple values):
- Cross-cutting concerns (readonly, async, expensive, experimental)
- Fine-grained filtering within categories
- Metadata for observability and debugging

**For Project Leaders:** Categories and tags enable organizing large tool libraries. As you grow to 100+ tools across multiple teams, categorization becomes essential for discoverability and maintenance.

**For IT Leaders:** Tags enable policy enforcement—mark tools as `["requires_approval", "production_only"]` and configure agent tool access based on tags. This supports least-privilege tool access control.

**For Users:** Categories help you understand what Friday can do at a glance. When you see Friday has "filesystem", "web", and "git" categories enabled, you know it can read files, fetch web content, and manage git repositories.

---

### 5.3.4 Tool Registration & Lifecycle

Tools must be registered with a `ToolRegistry` to be available to agents. Friday provides a default global registry and supports custom registries for isolation.

**Registration Methods:**

**1. Automatic Registration (@tool decorator):**
```python
from friday_tools import tool

@tool(name="my_tool", category="utility")
async def my_tool(input: str) -> str:
    return f"Processed: {input}"

# Automatically registered with default registry
```

**2. Manual Registration (class-based tools):**
```python
from friday_tools import BaseTool, get_default_registry

class MyTool(BaseTool):
    ...

# Explicitly register
registry = get_default_registry()
registry.register(MyTool())
```

**3. Custom Registry (isolated tool sets):**
```python
from friday_tools import DefaultToolRegistry

# Create isolated registry
custom_registry = DefaultToolRegistry()

@custom_registry.tool(name="custom_tool")
async def custom_tool(...):
    ...

# Use this registry with specific agents
agent = CopilotAgent(
    llm=llm,
    controller=controller,
    tool_registry=custom_registry  # Only this agent sees these tools
)
```

**Tool Discovery & Lookup:**

```python
registry = get_default_registry()

# List all tools
all_tools = registry.list_tools()
tool_names = registry.list_names()

# Get specific tool
file_read = registry.get("file_read")

# Check if tool exists
if "http_get" in registry:
    http_get = registry.get("http_get")

# Get executable
callable_tool = registry.get_callable("file_read")
result = await callable_tool(path="/tmp/test.txt")
```

**Hot Reloading (Development):**

For development, Friday supports hot-reloading tools without restarting:

```python
# Unregister old version
registry.unregister("my_tool")

# Register new version
@tool(name="my_tool")
async def my_tool_v2(...):
    # Updated implementation
    ...
```

**Tool Versioning (Future):**

In future versions, Friday will support tool versioning:

```python
@tool(name="my_tool", version="2.0.0")
async def my_tool_v2(...):
    ...

# Agents can request specific versions
agent.use_tool("my_tool", version="2.0.0")
```

**Lifecycle Hooks (Future):**

Planned lifecycle hooks for tools:

- `on_register()`: Called when tool is registered
- `on_execute()`: Called before each execution (for logging, rate limiting)
- `on_complete()`: Called after successful execution
- `on_error()`: Called on execution failure
- `on_unregister()`: Called when tool is removed

**For Project Leaders:** The registration system enables dynamic tool management. Teams can develop tools independently, register them at runtime, and update tools without full system restarts. This supports agile tool development and experimentation.

**For IT Leaders:** Custom registries enable security boundaries—create separate registries for trusted vs. untrusted agents, production vs. development environments, or different security zones. Tools in one registry are completely isolated from others.

**For Users:** Tool registration is mostly invisible—tools are available automatically once defined. The system handles discovery and lifecycle, so you can focus on using tools rather than managing them.

---

## 5.4 Dynamic Tool Selection & Context Injection

Friday doesn't always include all 50+ tools in every LLM context. Instead, it uses intelligent selection to include the most relevant tools based on the task, conversation history, and token budget.

### 5.4.1 Context-Aware Tool Recommendations

Friday's tool recommendation system analyzes the user's query and conversation context to select the most relevant tools for inclusion in the LLM prompt.

**Recommendation Algorithm:**

1. **Semantic Similarity**: Compare user query embedding to tool description embeddings
2. **Category Matching**: If query mentions files, prioritize `filesystem` tools
3. **Historical Usage**: If user frequently uses certain tools, include them
4. **Explicit References**: If query mentions a URL, include `web` tools
5. **Agent Profile**: Agent YAML can specify preferred tools or categories

**Example Flow:**

**User Query:** *"Read the config.yaml file and post the database settings to Slack"*

**Friday's Analysis:**
- Keywords detected: "Read", "file", "post", "Slack"
- Required categories: `filesystem` (for reading), `data` (for YAML parsing), `integrations` (for Slack)
- Tools selected:
  - `file_read` (filesystem)
  - `yaml_parse` (data)
  - `slack_post` (integrations)

**Why Not Include All Tools?**

Including all 50+ tools in every context would:
- **Consume Excessive Tokens**: Tool schemas can be 100-500 tokens each; 50 tools = 5,000-25,000 tokens
- **Reduce Context Space**: Less room for conversation history, memories, and user query
- **Confuse the LLM**: Too many options leads to analysis paralysis and suboptimal tool selection
- **Increase Latency**: Larger prompts take longer to process

**Dynamic Selection Benefits:**

✅ **Token Efficiency**: Only include tools likely to be used
✅ **Improved Tool Selection**: Fewer options = more focused LLM reasoning
✅ **Scalability**: Works with 100+ tools without context exhaustion
✅ **Adaptability**: Changes based on conversation flow

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

**For Project Leaders:** Dynamic tool selection enables scaling tool libraries to hundreds of tools without degrading agent performance. As you add more domain-specific tools, Friday intelligently chooses the most relevant subset for each task.

**For IT Leaders:** Tool recommendation is logged in transcripts, enabling auditability. You can analyze which tools are being selected and why, identifying underutilized tools or refining recommendation logic.

**For Users:** Friday automatically figures out which tools it needs for your request. You don't need to know which tools exist or which to use—Friday selects the right tools based on what you're asking for.

---

### 5.4.2 Tool Token Budget Management

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

**Budget Management Strategy:**

1. **Estimate Cost**: Calculate tokens for each candidate tool schema
2. **Prioritize by Relevance**: Sort tools by recommendation score
3. **Pack Greedily**: Include tools from highest to lowest score until budget exhausted
4. **Fallback to Categories**: If individual schemas too expensive, list available categories instead

**Example: Budget Exhaustion**

**Scenario:** User query requires 15 tools, but budget only fits 8 tools.

**Friday's Approach:**
- Rank tools 1-15 by relevance score
- Include tools 1-8 (highest scores) in full schemas
- For tools 9-15, list names and categories only: *"Additional tools available: file_write (filesystem), csv_read (data), ..."*
- LLM can request unlisted tools explicitly if needed

**Configuration:**

```yaml
context:
  total_tokens: 8000
  tool_budget_max: 2000      # Maximum tokens for tool schemas
  tool_schema_format: "compact"  # or "full"
  fallback_to_categories: true
```

**Schema Format Options:**

**Full Format** (OpenAI style):
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
        "encoding": {"type": "string", "description": "File encoding...", "default": "auto"},
        ...
      },
      "required": ["path"]
    }
  }
}
```

**Compact Format** (Friday compressed):
```json
{
  "name": "file_read",
  "desc": "Read file with auto encoding",
  "params": {"path": "str*", "encoding": "str=auto", "start_line": "int=1"}
}
```

Compact format saves ~40% tokens with minor description quality loss.

**For Project Leaders:** Token budget management ensures Friday can scale to large tool libraries while maintaining space for memories and history. This enables comprehensive agent capabilities without trading off context richness.

**For IT Leaders:** Token budgeting prevents runaway context costs. By capping tool schema tokens, you can estimate maximum LLM costs per turn and prevent budget overruns from tool proliferation.

**For Users:** Friday automatically manages the tradeoff between tool availability and context space. You get the right tools for the job without sacrificing Friday's memory of your conversation or preferences.

---

### 5.4.3 Per-Task Tool Injection

For specific workflows or agent types, you can explicitly inject tools into context, overriding dynamic selection.

**Use Cases:**

1. **Workflow-Specific Tools**: A code review workflow always needs `git_diff`, `code_analyze`, and `git_commit`
2. **Agent Specialization**: A researcher agent always has `web_search`, `scrape_page`, and `file_write` for note-taking
3. **Testing**: Force specific tool availability for debugging or testing
4. **Security**: Restrict agent to specific approved tools (allowlist mode)

**Configuration Methods:**

**1. Agent YAML Profile:**
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

**2. Workflow Task Definition:**
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

**3. Programmatic Injection:**
```python
agent = CopilotAgent(...)

# Inject tools for this session
agent.inject_tools(["file_read", "git_status", "git_diff"])

# Revert to dynamic selection
agent.clear_injected_tools()
```

**4. CLI Command (for testing):**
```bash
# In memory-chat-v2.py
/inject-tools file_read,file_write,directory_list

# Query tools in context
/tool-budget
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

**For Project Leaders:** Explicit tool injection enables specialized agents optimized for specific tasks. Instead of generalist agents with all tools, you can create focused agents (researcher, coder, analyst) each with curated toolsets for their role.

**For IT Leaders:** Allowlist mode is the security boundary for tool access. Combine with per-agent tool policies to implement least-privilege access control—each agent only has the tools necessary for its function, nothing more.

**For Users:** Tool injection is mostly invisible in normal use, but it enables Friday to have specialized "modes" (research mode, coding mode, analysis mode) where different tool sets are available. This makes Friday more efficient at specific tasks.

---

## Conclusion: Tools as Friday's Capabilities

Tools are the practical foundation of agent usefulness. While memory enables learning and LLMs provide reasoning, tools enable **action**—the ability to read files, make web requests, execute code, and interface with the world.

**Key Takeaways:**

1. **Comprehensive Built-in Library**: 50+ tools covering filesystem, web, git, data, text, code, and integrations provide immediate capabilities
2. **Easy Extensibility**: Create custom tools in minutes with `@tool` decorator or full control with `BaseTool` class
3. **Intelligent Selection**: Dynamic tool recommendation ensures relevant tools are available without exhausting token budget
4. **Security Boundaries**: Sandboxing, validation, allowlists, and auditability provide production-grade safety
5. **Protocol-Based Design**: All tools follow the same interface, enabling testing, swapping, and evolution

**For Project Leaders:** Friday's tool system provides the foundation for domain-specific agent capabilities. The 50+ built-in tools handle common tasks; custom tools handle your unique requirements. The architecture scales from hobby projects to enterprise deployments.

**For IT Leaders:** Tools represent the primary risk surface for agent systems (file access, code execution, external APIs). Friday's architecture provides defense in depth: input validation, sandboxing, allowlists, auditing, and rate limiting. Each tool category has appropriate security controls.

**For Users:** Tools determine what Friday can actually do for you. The more comprehensive the tool library, the more tasks Friday can accomplish autonomously. Friday's combination of built-in tools and extensibility means it can handle both common operations and your specific workflows.

---

**Next Section:** [Section 6: Agents - Configuration & Capabilities](06-agents.md)

Learn how agents orchestrate memory, LLMs, and tools to accomplish complex tasks with configurable capabilities, specialization patterns, and lifecycle management.
