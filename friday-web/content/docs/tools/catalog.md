---
title: "Built-in Tool Catalog"
description: "Complete reference for all filesystem, shell, web, git, and code tools."
weight: 2
---

This page is the complete reference for every built-in tool Friday ships with, organized by category: filesystem, shell, web, git, data, text, and code execution.

Friday ships with over 50 production-ready tools organized into 7 categories.

## Summary

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

---

## Filesystem Tools

Filesystem tools enable agents to read, write, navigate, and search files and directories.

### `file_read` — Read File Contents

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

**Smart Features:**
- **Encoding Detection**: Uses `chardet` library to detect encoding with confidence scores
- **Pagination**: Efficiently reads specific line ranges without loading entire file
- **Truncation Notice**: Clear indicators when output is truncated
- **Error Handling**: Graceful failures for missing files, permission errors, or encoding issues

---

### `file_write` — Write File Contents

**Purpose:** Write or overwrite a file with specified content.

**Parameters:**
- `path` (string, required): Path to the file to write
- `content` (string, required): Content to write to the file
- `encoding` (string, default: `"utf-8"`): Encoding to use
- `create_dirs` (boolean, default: `true`): Create parent directories if they don't exist

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

### `file_append` — Append to File

**Purpose:** Append content to an existing file without overwriting.

**Parameters:**
- `path` (string, required): Path to the file
- `content` (string, required): Content to append
- `newline_before` (boolean, default: `true`): Add newline before appending

**Example:**
```python
result = await file_append.execute(
    path="/logs/app.log",
    content="[INFO] Application started successfully",
    newline_before=True
)
```

---

### `directory_list` — List Directory Contents

**Purpose:** List files and directories with optional filtering and recursion.

**Parameters:**
- `path` (string, default: `"."`): Directory to list
- `recursive` (boolean, default: `false`): Recursively list subdirectories
- `pattern` (string, optional): Glob pattern to filter (e.g., `"*.py"`)
- `show_hidden` (boolean, default: `false`): Include hidden files (starting with `.`)

**Example:**
```python
# List Python files recursively
result = await directory_list.execute(
    path="/project/src",
    recursive=True,
    pattern="*.py"
)
```

---

### `directory_create` — Create Directory

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

### `file_delete` — Delete File or Directory

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

### `file_move` — Move or Rename File

**Purpose:** Move or rename a file or directory.

**Parameters:**
- `source` (string, required): Source path
- `destination` (string, required): Destination path
- `overwrite` (boolean, default: `false`): Overwrite destination if it exists

**Example:**
```python
result = await file_move.execute(
    source="/project/draft.md",
    destination="/project/final.md"
)
```

---

### `file_info` — Get File Metadata

**Purpose:** Retrieve file metadata including size, permissions, and timestamps.

**Parameters:**
- `path` (string, required): Path to the file or directory

**Example:**
```python
result = await file_info.execute(path="/project/database.sqlite")
# Output includes: type, size, permissions, owner, timestamps
```

---

### `file_grep` — Search File Contents

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
```

All filesystem tools use `FilesystemSandbox` for path validation, preventing directory traversal attacks and restricting access to configured safe directories.

---

## Shell & System Tools

Shell tools enable command execution and system introspection.

### `execute_command` — Execute Shell Command

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
result = await execute_command.execute(
    command="npm run build",
    cwd="/project",
    timeout=120
)
```

{{< callout type="warning" >}}
**Command Injection Risk**: Never pass unsanitized user input directly to commands. Use `ShellSandbox` to restrict allowed commands and paths in production.
{{< /callout >}}

**Alternatives:** For common operations, prefer specialized tools (`git_status` instead of `execute_command("git status")`) for better safety and structured outputs.

---

### `system_info` — Get System Information

**Purpose:** Retrieve system information including OS, CPU, memory, and disk usage.

**Parameters:** None

**Use Cases:**
- Determining system capabilities before executing resource-intensive tasks
- Monitoring agent resource consumption
- Debugging environment-specific issues

---

## Web & Network Tools

Web tools provide HTTP client capabilities and content fetching.

### `http_get` — HTTP GET Request

**Purpose:** Make HTTP GET requests with headers and query parameters.

**Parameters:**
- `url` (string, required): URL to request
- `headers` (object, optional): HTTP headers
- `params` (object, optional): Query parameters
- `timeout` (integer, default: `30`): Request timeout in seconds

**Example:**
```python
result = await http_get.execute(
    url="https://api.example.com/search",
    headers={"Authorization": "Bearer token123"},
    params={"q": "Friday framework", "limit": 10}
)
```

---

### `http_post` — HTTP POST Request

**Purpose:** Make HTTP POST requests with JSON or form data.

**Parameters:**
- `url` (string, required): URL to request
- `json_data` (object, optional): JSON body to send
- `form_data` (object, optional): Form data to send (mutually exclusive with `json_data`)
- `headers` (object, optional): HTTP headers
- `timeout` (integer, default: `30`): Request timeout

**Example:**
```python
result = await http_post.execute(
    url="https://api.example.com/users",
    json_data={"name": "Alice", "email": "alice@example.com"}
)
```

---

### `http_put`, `http_delete` — Other HTTP Methods

**Purpose:** HTTP PUT and DELETE requests for RESTful API interactions.

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

### `http_download` — Download File from URL

**Purpose:** Download a file from a URL and save it locally with streaming support.

**Parameters:**
- `url` (string, required): URL to download from
- `destination` (string, required): Local path to save the file
- `timeout` (integer, default: `60`): Download timeout

**Features:**
- **Streaming**: Downloads in chunks to avoid memory exhaustion
- **Progress Tracking**: Reports total bytes downloaded
- **Directory Creation**: Automatically creates parent directories
- **Validation**: Uses `FilesystemSandbox` to validate destination paths

---

### `http_upload` — Upload File to URL

**Purpose:** Upload a local file to a URL using multipart form data.

**Parameters:**
- `url` (string, required): URL to upload to
- `file_path` (string, required): Local file path to upload
- `field_name` (string, default: `"file"`): Form field name for the file
- `headers` (object, optional): Additional headers
- `timeout` (integer, default: `60`): Upload timeout

---

### `web_search` — Web Search Integration

**Purpose:** Perform web searches using configured search APIs (DuckDuckGo, Google, Bing).

**Parameters:**
- `query` (string, required): Search query
- `num_results` (integer, default: `10`): Number of results to return
- `safe_search` (boolean, default: `true`): Enable safe search filtering

**Configuration:** Requires API key for search provider in environment variables (`GOOGLE_SEARCH_API_KEY`, `BING_SEARCH_API_KEY`, etc.)

---

### `scrape_page` — Web Page Scraping

**Purpose:** Fetch and parse HTML pages, extracting text content with optional CSS selectors.

**Parameters:**
- `url` (string, required): URL to scrape
- `selector` (string, optional): CSS selector to extract specific elements
- `timeout` (integer, default: `30`): Request timeout

**Example:**
```python
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

---

## Git Tools

Git tools provide version control operations for repository management.

### `git_status` — Git Repository Status

**Purpose:** Show the working tree status of a git repository.

**Parameters:**
- `path` (string, default: `"."`): Repository path

**Example:**
```python
result = await git_status.execute(path="/project")
```

---

### `git_diff` — Show Git Diff

**Purpose:** Show changes between commits, commit and working tree, or staged changes.

**Parameters:**
- `path` (string, default: `"."`): Repository path
- `staged` (boolean, default: `false`): Show staged changes (`--staged`)
- `file` (string, optional): Specific file to diff

**Example:**
```python
# Show staged changes
result = await git_diff.execute(path="/project", staged=True)
```

---

### `git_log` — Show Commit Log

**Purpose:** Display commit history with customizable format and depth.

**Parameters:**
- `path` (string, default: `"."`): Repository path
- `count` (integer, default: `10`): Number of commits to show
- `oneline` (boolean, default: `true`): One-line format (`--oneline`)

---

### `git_commit` — Create Commit

**Purpose:** Stage changes and create a commit with a message.

**Parameters:**
- `path` (string, default: `"."`): Repository path
- `message` (string, required): Commit message
- `files` (array, optional): Specific files to stage (None for all changes)
- `author` (string, optional): Author override (`"Name <email>"`)

**Example:**
```python
# Commit specific files
result = await git_commit.execute(
    path="/project",
    message="Update configuration",
    files=["config.yaml", "README.md"]
)
```

---

### `git_push`, `git_pull` — Remote Operations

**Purpose:** Push commits to remote or pull changes from remote.

**Parameters:**
- `path` (string, default: `"."`): Repository path
- `remote` (string, default: `"origin"`): Remote name
- `branch` (string, optional): Branch name (defaults to current branch)

---

### `git_checkout` — Switch Branches

**Purpose:** Switch to a different branch or create a new branch.

**Parameters:**
- `path` (string, default: `"."`): Repository path
- `branch` (string, required): Branch name to checkout
- `create` (boolean, default: `false`): Create branch if it doesn't exist (`-b`)

---

### `git_branches` — List Branches

**Purpose:** List all branches (local and remote) with current branch indicator.

**Parameters:**
- `path` (string, default: `"."`): Repository path
- `remote` (boolean, default: `false`): Show remote branches

All commits created by Friday can be attributed via the transcript system, ensuring traceability. Configure commit authorship to clearly identify agent-generated commits (e.g., `"Friday Agent <noreply@yourcompany.com>"`).

---

## Data Manipulation Tools

Data tools parse, query, and transform structured data formats.

### `json_parse` — Parse JSON

**Purpose:** Parse JSON strings into structured data with validation.

**Example:**
```python
result = await json_parse.execute(
    json_string='{"name": "Alice", "age": 30, "city": "NYC"}'
)
```

---

### `json_query` — Query JSON with JSONPath

**Purpose:** Query JSON data using JSONPath expressions.

**Parameters:**
- `data` (object, required): JSON data (dict or list)
- `query` (string, required): JSONPath expression (e.g., `"$.store.book[*].title"`)

**Example:**
```python
result = await json_query.execute(
    data=data,
    query="$.store.book[*].title"
)
```

---

### `yaml_parse`, `yaml_dump` — YAML Operations

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

### `csv_read`, `csv_write` — CSV Operations

**Purpose:** Read and write CSV files with header support.

**`csv_read` Parameters:**
- `path` (string, required): CSV file path
- `delimiter` (string, default: `","`): Column delimiter
- `has_header` (boolean, default: `true`): First row is header

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

---

### `xml_parse`, `xml_query` — XML Operations

**Purpose:** Parse XML and query with XPath.

**Example:**
```python
# XPath query
result = await xml_query.execute(
    xml_string="<root><item id='1'>Value</item></root>",
    xpath="//item[@id='1']/text()"
)
```

---

### `toml_parse` — TOML Operations

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

All parsing tools include error handling for malformed data with clear error messages. No arbitrary code execution—these tools only parse and query standard data formats safely.

---

## Text Processing Tools

Text tools perform string operations, regular expressions, and text transformations.

### `regex_search` — Regular Expression Search

**Purpose:** Search text using regular expressions with capture groups.

**Parameters:**
- `text` (string, required): Text to search
- `pattern` (string, required): Regular expression pattern
- `flags` (array, optional): Regex flags (`["IGNORECASE"]`, `["MULTILINE"]`, etc.)

**Example:**
```python
# Extract email addresses
result = await regex_search.execute(
    text="Contact: alice@example.com or bob@test.org",
    pattern=r"[\w\.-]+@[\w\.-]+\.\w+"
)
```

---

### `regex_replace` — Regular Expression Replace

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

### `text_transform` — Text Transformations

**Purpose:** Apply common text transformations (case, trimming, line operations).

**Parameters:**
- `text` (string, required): Text to transform
- `operation` (string, required): Transformation type
  - `"uppercase"`, `"lowercase"`, `"titlecase"`, `"capitalize"`
  - `"trim"`, `"trim_start"`, `"trim_end"`
  - `"remove_duplicates"` (duplicate lines)
  - `"sort_lines"`, `"reverse_lines"`
  - `"remove_empty_lines"`

---

### `format_text` — Text Formatting

**Purpose:** Format text with syntax highlighting, indentation, or templates.

**Parameters:**
- `text` (string, required): Text to format
- `format` (string, required): Format type
  - `"markdown"`: Format as markdown
  - `"code_python"`, `"code_javascript"`, etc.: Syntax highlighting
  - `"json_pretty"`: Pretty-print JSON
  - `"indent"`: Add indentation (with `indent_level` param)

Regex operations are compiled and validated before execution, preventing ReDoS (Regular Expression Denial of Service) attacks with timeout enforcement on long-running patterns.

---

## Code Execution Tools

Code execution tools run code in isolated environments with safety constraints.

### `python_execute` — Execute Python Code

**Purpose:** Execute Python code in a sandboxed subprocess with timeout and resource limits.

**Parameters:**
- `code` (string, required): Python code to execute
- `timeout` (integer, default: `30`): Execution timeout in seconds

**Example:**
```python
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
- Subprocess isolation: Implemented
- Timeout enforcement: Implemented
- Docker-based sandboxing: Planned (Phase 5)

{{< callout type="warning" >}}
**Untrusted Code**: Never execute untrusted user code without Docker sandboxing (coming in Phase 5). Code has access to Friday's filesystem in subprocess mode; use Docker for isolation.
{{< /callout >}}

---

### `code_format` — Format Code

**Purpose:** Automatically format code using language-specific formatters (Black for Python, Prettier for JS/TS).

**Parameters:**
- `code` (string, required): Code to format
- `language` (string, required): Language (`"python"`, `"javascript"`, `"typescript"`, etc.)

**Example:**
```python
result = await code_format.execute(
    code="def foo(x,y):return x+y",
    language="python"
)
# Returns: "def foo(x, y):\n    return x + y\n"
```

---

### `code_analyze` — Static Code Analysis

**Purpose:** Run static analysis tools (Ruff, ESLint, Pylint) to check code quality.

**Parameters:**
- `code` (string, required): Code to analyze
- `language` (string, required): Language
- `rules` (array, optional): Specific rules to check

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

Code execution is the highest-risk tool category. Current subprocess isolation provides basic safety; Docker-based sandboxing (Phase 5 roadmap) will provide production-grade isolation for untrusted code.

---

## Related Pages

- [Tool System Overview](/docs/tools/) — Architecture, BaseTool protocol, and token budget management
- [Creating Custom Tools](/docs/tools/custom/) — Extend Friday with the `@tool` decorator or `BaseTool` subclass
