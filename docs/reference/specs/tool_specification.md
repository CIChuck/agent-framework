# Friday Framework - Tool Specification

## 0. Introduction: The Capabilities Layer

**Status:** Ready for Implementation
**Role:** The "Hands" of the Agentic Framework
**Package:** `packages/friday-tools` (NEW - Standalone)

This specification defines `friday-tools`, a comprehensive tool library that provides agents with capabilities to interact with the external world. The package is designed as a **standalone, isolated unit** with no dependencies on other Friday packages, enabling independent development, testing, and eventual integration.

### 0.1. Design Principles

1. **Isolation:** Zero dependencies on friday-core, friday-agent, or friday-memory. Protocols defined locally.
2. **Protocol-First:** All abstractions defined as Python Protocols for flexibility and testability.
3. **Dependency Injection:** Tools accept dependencies (sandboxes, HTTP clients) via injection, not instantiation.
4. **Framework Agnostic:** Adapters enable tools from LangChain, Anthropic, and OpenAI to work within Friday.
5. **Security by Default:** Filesystem and shell operations protected by configurable sandboxes.

### 0.2. Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Package Independence | Standalone package | Enables isolated development; no risk to existing packages |
| Protocol Location | Local to friday-tools | Can be hoisted to friday-core later if needed |
| Sandbox Location | Separate friday-sandbox package | See `sandbox_specifications.md` |
| Memory Tools | Remain in friday-memory | Tightly coupled to SessionState and MemoryController |
| Framework Adapters | Optional dependencies | Import lazily to avoid bloating core package |

### 0.3. Relationship to Existing Codebase

**Current State:**
- `friday-agent/tools/registry.py` contains `DefaultToolRegistry` and `@tool` decorator
- `friday-agent/tools/builtins.py` contains 6 memory-integrated tools
- `friday-core/interfaces/tools.py` contains `ToolRegistry` protocol

**Migration Path (Deferred):**
After friday-tools is complete and validated:
1. friday-agent will depend on friday-tools
2. Registry will be re-exported from friday-tools for backward compatibility
3. Memory tools remain in friday-memory (not migrated)

**Conflicts Identified:**
- `ToolRegistry` protocol exists in friday-core; friday-tools defines `ToolDefinition` and `ToolAdapter` locally
- Resolution: Protocols are compatible; friday-tools extends, doesn't conflict

---

## 1. Protocol Definitions

### 1.1. ToolDefinition Protocol

**Path:** `src/friday_tools/protocols.py`

Defines the fundamental unit of agent capability - what a "tool" IS in Friday.

```python
from typing import Any, Protocol

class ToolDefinition(Protocol):
    """Abstract representation of a tool capability."""

    @property
    def name(self) -> str:
        """Unique tool identifier."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description for the LLM."""
        ...

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """JSON Schema for tool parameters (OpenAI-compatible)."""
        ...

    async def execute(self, **kwargs: Any) -> str:
        """Execute the tool with given arguments."""
        ...
```

### 1.2. ToolAdapter Protocol

**Path:** `src/friday_tools/protocols.py`

Enables conversion of external framework tools into Friday's ToolDefinition.

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class ToolAdapter(Protocol, Generic[T]):
    """Adapts external framework tools to Friday's ToolDefinition."""

    def adapt(self, external_tool: T) -> ToolDefinition:
        """Convert an external tool to Friday's ToolDefinition."""
        ...

    def adapt_many(self, tools: list[T]) -> list[ToolDefinition]:
        """Convert multiple external tools."""
        ...
```

### 1.3. BaseTool Class

**Path:** `src/friday_tools/definition.py`

Concrete implementation of ToolDefinition for Friday-native tools.

```python
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class BaseTool:
    """Concrete implementation of ToolDefinition."""

    name: str
    description: str
    parameters_schema: dict[str, Any]
    func: Callable[..., Any]

    async def execute(self, **kwargs: Any) -> str:
        """Execute the tool function."""
        result = self.func(**kwargs)
        if asyncio.iscoroutine(result):
            result = await result
        return str(result)
```

---

## 2. Registry Implementation

### 2.1. DefaultToolRegistry

**Path:** `src/friday_tools/registry.py`

Central registry for tool management with decorator-based registration.

```python
class DefaultToolRegistry:
    """
    Registry mapping tool names to executable functions.

    Features:
    - Decorator-based registration (@tool)
    - Manual registration via register()
    - Partial binding for dependency injection
    - OpenAI-compatible JSON schema generation
    """

    def register(self, name: str, func: Callable, description: str, parameters: dict) -> None:
        """Register a tool manually."""

    def get_tool(self, name: str) -> Callable[..., Any]:
        """Get executable function for a tool."""

    def get_schema(self, name: str) -> dict[str, Any]:
        """Get OpenAI-compatible JSON schema for a tool."""

    def list_tools(self) -> list[str]:
        """List all registered tool names."""

    def bind_dependency(self, tool_name: str, **kwargs: Any) -> None:
        """Bind dependencies to a tool using partial application."""

    def load_decorated_tools(self) -> int:
        """Load all tools registered via @tool decorator."""
```

### 2.2. @tool Decorator

**Path:** `src/friday_tools/registry.py`

```python
def tool(
    name: str | None = None,
    description: str = "",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to register a function as a tool.

    Extracts parameter information from function signature and docstring
    to generate OpenAI-compatible JSON schema.

    Example:
        @tool(name="web_search", description="Search the web")
        async def web_search(query: str, max_results: int = 5) -> str:
            '''
            Args:
                query: The search query
                max_results: Maximum results to return
            '''
            ...
    """
```

---

## 3. Framework Adapters

### 3.1. LangChainToolAdapter

**Path:** `src/friday_tools/adapters/langchain.py`
**Optional Dependency:** `langchain-core>=0.1.0`

```python
class LangChainToolAdapter:
    """Adapts LangChain BaseTool to Friday ToolDefinition."""

    def adapt(self, tool: "BaseTool") -> ToolDefinition:
        """
        Convert LangChain tool to Friday ToolDefinition.

        Mapping:
        - tool.name -> name
        - tool.description -> description
        - tool.args_schema -> parameters_schema (via Pydantic schema)
        - tool.ainvoke/invoke -> execute
        """
```

### 3.2. AnthropicToolAdapter

**Path:** `src/friday_tools/adapters/anthropic.py`
**Optional Dependency:** `anthropic>=0.25.0`

```python
class AnthropicToolAdapter:
    """Adapts Anthropic tool definitions to Friday ToolDefinition."""

    def adapt(self, tool_def: dict[str, Any]) -> ToolDefinition:
        """
        Convert Anthropic tool schema to Friday ToolDefinition.

        Expected format:
        {
            "name": "get_weather",
            "description": "Get current weather",
            "input_schema": { ... JSON Schema ... }
        }
        """
```

### 3.3. OpenAIToolAdapter

**Path:** `src/friday_tools/adapters/openai.py`
**Optional Dependency:** `openai>=1.0.0`

```python
class OpenAIToolAdapter:
    """Adapts OpenAI function calling format to Friday ToolDefinition."""

    def adapt(self, tool_def: dict[str, Any]) -> ToolDefinition:
        """
        Convert OpenAI function schema to Friday ToolDefinition.

        Expected format:
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather",
                "parameters": { ... JSON Schema ... }
            }
        }
        """
```

---

## 4. Tool Categories

### 4.1. Tool Inventory Summary

| Priority | Category | Tool Count | Description |
|----------|----------|------------|-------------|
| **P0** | Filesystem - Reading | 7 | File and directory inspection |
| **P0** | Filesystem - Writing | 6 | File creation and modification |
| **P0** | Filesystem - Operations | 4 | Copy, move, delete operations |
| **P0** | Shell/System | 6 | Command execution and system info |
| **P0** | Web - Search & Fetch | 5 | Web content retrieval |
| **P0** | Web - HTTP Client | 6 | API interactions |
| **P1** | Data Formats | 11 | JSON, YAML, TOML, CSV, XML |
| **P1** | Text Processing | 8 | Search, replace, transform |
| **P1** | Git Operations | 10 | Version control |
| **P2** | Code Tools | 4 | Format, lint, analyze |
| **P2** | Archive Tools | 3 | Zip/tar operations |
| **P2** | Encoding/Crypto | 6 | Base64, hashing, UUIDs |
| **P2** | Math/Calculation | 5 | Math and date operations |
| **P3** | Integrations | 6 | Email, calendar, database stubs |
| **NEW** | Code Execution | 2 | Python execution in sandbox |
| **Total** | | **89** | |

### 4.2. Filesystem Tools (17 tools)

**Path:** `src/friday_tools/filesystem/`

| Tool | File | Description |
|------|------|-------------|
| `file_read` | `read.py` | Read file contents with encoding support |
| `file_read_lines` | `read.py` | Read specific line range |
| `file_info` | `read.py` | Get file metadata |
| `file_grep` | `read.py` | Search file contents with regex |
| `file_write` | `write.py` | Write/overwrite file |
| `file_append` | `write.py` | Append to file |
| `file_insert` | `write.py` | Insert at specific line |
| `file_replace` | `write.py` | Find and replace in file |
| `file_patch` | `write.py` | Apply diff/patch |
| `file_copy` | `operations.py` | Copy file or directory |
| `file_move` | `operations.py` | Move/rename |
| `file_delete` | `operations.py` | Delete file or directory |
| `file_chmod` | `operations.py` | Change permissions |
| `directory_list` | `directory.py` | List directory contents |
| `directory_tree` | `directory.py` | Recursive tree view |
| `directory_create` | `directory.py` | Create directory |
| `file_search` | `directory.py` | Find files by glob pattern |

### 4.3. Shell/System Tools (6 tools)

**Path:** `src/friday_tools/shell/`

| Tool | File | Description |
|------|------|-------------|
| `shell_execute` | `execute.py` | Run shell command (sandboxed) |
| `shell_script` | `execute.py` | Run multi-line script |
| `process_list` | `system.py` | List running processes |
| `process_kill` | `system.py` | Terminate a process |
| `environment_get` | `system.py` | Get environment variable |
| `system_info` | `system.py` | OS, CPU, memory, disk info |

### 4.4. Web Tools (11 tools)

**Path:** `src/friday_tools/web/`

| Tool | File | Description |
|------|------|-------------|
| `web_search` | `search.py` | Search via DuckDuckGo API |
| `web_fetch` | `fetch.py` | Fetch URL, convert to markdown |
| `web_extract_links` | `fetch.py` | Extract all links from page |
| `web_extract_text` | `fetch.py` | Extract main content |
| `web_screenshot` | `fetch.py` | Screenshot webpage (stub) |
| `http_get` | `http.py` | HTTP GET request |
| `http_post` | `http.py` | HTTP POST request |
| `http_put` | `http.py` | HTTP PUT request |
| `http_delete` | `http.py` | HTTP DELETE request |
| `http_download` | `http.py` | Download file from URL |
| `http_upload` | `http.py` | Upload file to URL |

### 4.5. Data Format Tools (11 tools)

**Path:** `src/friday_tools/data/`

| Tool | File | Description |
|------|------|-------------|
| `json_read` | `json_tools.py` | Read and parse JSON |
| `json_write` | `json_tools.py` | Write data as JSON |
| `json_query` | `json_tools.py` | Query with JSONPath |
| `yaml_read` | `yaml_tools.py` | Read and parse YAML |
| `yaml_write` | `yaml_tools.py` | Write data as YAML |
| `toml_read` | `toml_tools.py` | Read and parse TOML |
| `toml_write` | `toml_tools.py` | Write data as TOML |
| `csv_read` | `csv_tools.py` | Read CSV file |
| `csv_write` | `csv_tools.py` | Write data as CSV |
| `xml_read` | `xml_tools.py` | Read and parse XML |
| `xml_query` | `xml_tools.py` | Query with XPath |

### 4.6. Text Processing Tools (8 tools)

**Path:** `src/friday_tools/text/`

| Tool | File | Description |
|------|------|-------------|
| `text_search` | `search.py` | Regex search in text |
| `text_extract` | `search.py` | Extract regex groups |
| `text_replace` | `transform.py` | Regex replace |
| `text_split` | `transform.py` | Split by delimiter |
| `text_join` | `transform.py` | Join with delimiter |
| `text_template` | `transform.py` | Render Jinja template |
| `markdown_to_text` | `convert.py` | Strip markdown |
| `html_to_markdown` | `convert.py` | Convert HTML |

### 4.7. Git Tools (10 tools)

**Path:** `src/friday_tools/git/`

| Tool | File | Description |
|------|------|-------------|
| `git_status` | `status.py` | Working tree status |
| `git_diff` | `status.py` | Show changes |
| `git_log` | `status.py` | Commit history |
| `git_show` | `status.py` | Commit details |
| `git_add` | `staging.py` | Stage files |
| `git_commit` | `staging.py` | Create commit |
| `git_stash` | `staging.py` | Stash changes |
| `git_branch_list` | `branches.py` | List branches |
| `git_branch_create` | `branches.py` | Create branch |
| `git_checkout` | `branches.py` | Switch branches |

### 4.8. Code Tools (4 tools)

**Path:** `src/friday_tools/code/`

| Tool | File | Description |
|------|------|-------------|
| `code_format` | `format.py` | Format code (ruff, black) |
| `code_lint` | `format.py` | Lint and return issues |
| `code_parse_ast` | `analyze.py` | Parse to AST |
| `code_extract_symbols` | `analyze.py` | Extract functions/classes |

### 4.9. Archive Tools (3 tools)

**Path:** `src/friday_tools/archive/`

| Tool | File | Description |
|------|------|-------------|
| `archive_create` | `archive.py` | Create zip/tar |
| `archive_extract` | `archive.py` | Extract archive |
| `archive_list` | `archive.py` | List contents |

### 4.10. Encoding Tools (6 tools)

**Path:** `src/friday_tools/encoding/`

| Tool | File | Description |
|------|------|-------------|
| `base64_encode` | `encoding.py` | Encode to base64 |
| `base64_decode` | `encoding.py` | Decode from base64 |
| `hash_compute` | `encoding.py` | Compute hash |
| `uuid_generate` | `encoding.py` | Generate UUID |
| `url_encode` | `encoding.py` | URL encode |
| `url_decode` | `encoding.py` | URL decode |

### 4.11. Math Tools (5 tools)

**Path:** `src/friday_tools/math/`

| Tool | File | Description |
|------|------|-------------|
| `calculator` | `math.py` | Evaluate expressions |
| `unit_convert` | `math.py` | Convert units |
| `date_parse` | `math.py` | Parse date string |
| `date_format` | `math.py` | Format date |
| `date_calculate` | `math.py` | Date arithmetic |

### 4.12. Code Execution Tools (2 tools)

**Path:** `src/friday_tools/execution/`

| Tool | File | Description |
|------|------|-------------|
| `python_execute` | `python.py` | Execute Python in sandbox |
| `python_eval` | `python.py` | Evaluate expression in sandbox |

**Note:** These tools depend on `friday-sandbox` package. See `sandbox_specifications.md`.

### 4.13. Integration Stubs (6 tools)

**Path:** `src/friday_tools/integrations/`

| Tool | File | Description | Status |
|------|------|-------------|--------|
| `email_send` | `email.py` | Send email | Stub |
| `slack_send` | `slack.py` | Send Slack message | Stub |
| `calendar_create_event` | `calendar.py` | Create event | Stub |
| `calendar_list_events` | `calendar.py` | List events | Stub |
| `database_query` | `database.py` | Execute SQL | Stub |
| `webhook_call` | `webhook.py` | Call webhook | Stub |

---

## 5. Security Infrastructure

### 5.1. FilesystemSandbox

**Path:** `src/friday_tools/sandbox.py`

**Note:** Basic filesystem sandboxing for non-execution tools. For code execution, see `friday-sandbox` package.

```python
@dataclass
class FilesystemSandbox:
    """Restricts file operations to allowed paths."""

    allowed_paths: list[Path]
    denied_patterns: list[str] = field(default_factory=lambda: [
        "*.env", "*.pem", "*.key", "**/secrets/**", "**/.git/**"
    ])

    def validate_path(self, path: str) -> Path:
        """
        Validate path is within allowed directories.

        Raises:
            PermissionError: If path is outside allowed directories or matches denied pattern
        """
```

### 5.2. ShellSandbox

**Path:** `src/friday_tools/sandbox.py`

```python
@dataclass
class ShellSandbox:
    """Restricts shell command execution."""

    allowed_commands: list[str] = field(default_factory=lambda: [
        "ls", "cat", "head", "tail", "grep", "find", "wc", "sort", "uniq", "echo"
    ])
    blocked_patterns: list[str] = field(default_factory=lambda: [
        "rm -rf", "sudo", "chmod 777", "chown", "> /dev", "| sh", "| bash", "eval"
    ])
    working_directory: Path | None = None
    timeout_seconds: int = 30

    def validate_command(self, command: str) -> str:
        """
        Validate command is allowed.

        Raises:
            PermissionError: If command is not allowed or matches blocked pattern
        """
```

---

## 6. Package Configuration

### 6.1. pyproject.toml

```toml
[project]
name = "friday-tools"
version = "0.1.0"
description = "Comprehensive tool library for AI agents"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [{ name = "Friday Team" }]
keywords = ["ai", "agents", "tools", "llm", "automation"]

dependencies = [
    # HTTP & Web
    "httpx>=0.25.0",
    "beautifulsoup4>=4.12.0",
    "markdownify>=0.11.0",
    "lxml>=4.9.0",

    # Data formats
    "pyyaml>=6.0.0",
    "toml>=0.10.0",
    "jsonpath-ng>=1.5.0",

    # Text & Templates
    "jinja2>=3.1.0",

    # Git
    "gitpython>=3.1.0",

    # Math & Dates
    "python-dateutil>=2.8.0",

    # Sandbox integration
    "friday-sandbox",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "respx>=0.20.0",
    "pytest-mock>=3.10.0",
]
langchain = ["langchain-core>=0.1.0"]
anthropic = ["anthropic>=0.25.0"]
openai = ["openai>=1.0.0"]
all-adapters = [
    "friday-tools[langchain]",
    "friday-tools[anthropic]",
    "friday-tools[openai]",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/friday_tools"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

---

## 7. Implementation Phases

| Phase | Description | Deliverables |
|-------|-------------|--------------|
| **Phase 1** | Package scaffold, protocols, registry, basic sandbox | Core infrastructure |
| **Phase 2** | Framework adapters | LangChain, Anthropic, OpenAI |
| **Phase 3** | P0 Tools | 34 filesystem, shell, web tools |
| **Phase 4** | P1 Tools | 29 data, text, git tools |
| **Phase 5** | P2 Tools | 18 code, archive, encoding, math tools |
| **Phase 6** | P3 Stubs + Execution | 6 stubs + 2 sandbox execution tools |

---

## 8. Issues and Remediation

### 8.1. Identified Conflicts

| Issue | Location | Resolution |
|-------|----------|------------|
| Existing ToolRegistry protocol | `friday-core/interfaces/tools.py` | Compatible; friday-tools extends with ToolDefinition |
| Existing registry implementation | `friday-agent/tools/registry.py` | Deferred migration; friday-agent will re-export |
| Memory tools in friday-agent | `friday-agent/tools/builtins.py` | Memory tools stay in friday-memory (not migrated) |

### 8.2. Required Remediation

| Task | Priority | Description |
|------|----------|-------------|
| Add to workspace | Required | Add `friday-tools` to root `pyproject.toml` workspace members |
| Create Dockerfile | Required | Build `friday-sandbox-python:latest` image |
| Test isolation | Required | Verify no imports from friday-core/agent/memory |

### 8.3. Future Considerations

1. **Protocol Hoisting:** After validation, consider moving ToolDefinition/ToolAdapter to friday-core
2. **Registry Migration:** Move DefaultToolRegistry from friday-agent to friday-tools
3. **Streaming Tools:** Add async iterator support for long-running tools
4. **Tool Composition:** Allow tools to call other tools (tool chaining)

---

## 9. Success Criteria

- [ ] Package builds and installs via `uv sync`
- [ ] All 89 tools implemented and tested
- [ ] Zero imports from friday-core, friday-agent, friday-memory
- [ ] Framework adapters working with mocked dependencies
- [ ] Sandbox integration working for code execution
- [ ] All tests passing
- [ ] Documentation complete
