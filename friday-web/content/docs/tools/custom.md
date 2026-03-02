---
title: "Creating Custom Tools"
description: "Implement BaseTool or use the @tool decorator to add your own capabilities."
weight: 3
---

Extend Friday with custom tools by subclassing `BaseTool` for full control or using the `@tool` decorator for lightweight function-based tools.

Friday's tool system is designed for extensibility. Creating custom tools is straightforward—you can define tools as simple Python functions or full classes depending on complexity.

## Function-Based Tools (`@tool` Decorator)

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
Friday validates that arguments match the type hints before calling the function.

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
```

**Function Tool Features:**

- **Automatic Schema Generation**: Type hints become JSON Schema types
- **Default Values**: Function defaults become parameter defaults
- **Docstring Parsing**: Google-style docstrings provide parameter descriptions
- **Async Support**: Both `async def` and regular `def` functions work
- **Error Handling**: Exceptions are caught and returned as error messages

**When to Use Function Tools:**

Use function-based tools when:
- Tool logic fits in a single function
- No initialization or state management needed
- Simple input/output patterns
- Rapid prototyping or one-off tools

Avoid function-based tools when:
- Need to manage connections or resources (database, API clients)
- Require complex initialization logic
- Need to return structured `ToolResult` with rich metadata
- Want fine-grained control over schema generation

---

## Class-Based Tools (`BaseTool` Subclass)

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

            columns = rows[0].keys()
            formatted_rows = [dict(row) for row in rows]
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

# Initialize and register
async def setup_database_tool():
    pool = await asyncpg.create_pool(
        host="localhost",
        database="mydb",
        user="friday",
        password="secret"
    )
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

Use class-based tools when:
- Need to manage connections or resources (DB, API clients, file handles)
- Require initialization logic or configuration
- Want to return rich `ToolResult` objects with structured data
- Need fine-grained control over schema generation
- Implementing complex validation logic

---

## Tool Categories & Discovery

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

```python
from friday_tools import get_default_registry

registry = get_default_registry()
filesystem_tools = registry.get_tools_by_category("filesystem")

# Get schemas for web tools (for LLM context)
web_schemas = registry.get_schemas_by_category("web", format="openai")
```

**Using Tags for Fine-Grained Filtering:**

```python
@tool(
    category="data",
    tags=["json", "parser", "query", "readonly"]
)
async def json_query(...):
    ...

# Query by tags
json_tools = registry.get_tools_by_tags(["json"], match_all=False)
readonly_tools = registry.get_tools_by_tags(["readonly"], match_all=False)
```

---

## Tool Registration & Lifecycle

Tools must be registered with a `ToolRegistry` to be available to agents.

**Registration Methods:**

Automatic registration (`@tool` decorator):
```python
from friday_tools import tool

@tool(name="my_tool", category="utility")
async def my_tool(input: str) -> str:
    return f"Processed: {input}"

# Automatically registered with default registry
```

Manual registration (class-based tools):
```python
from friday_tools import BaseTool, get_default_registry

class MyTool(BaseTool):
    ...

registry = get_default_registry()
registry.register(MyTool())
```

Custom registry (isolated tool sets):
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

```python
# Unregister old version
registry.unregister("my_tool")

# Register new version
@tool(name="my_tool")
async def my_tool_v2(...):
    # Updated implementation
    ...
```

**Planned Lifecycle Hooks:**

- `on_register()`: Called when tool is registered
- `on_execute()`: Called before each execution (for logging, rate limiting)
- `on_complete()`: Called after successful execution
- `on_error()`: Called on execution failure
- `on_unregister()`: Called when tool is removed

Custom registries enable security boundaries—create separate registries for trusted vs. untrusted agents, production vs. development environments, or different security zones. Tools in one registry are completely isolated from others.

---

## Related Pages

- [Tool System Overview](/docs/tools/) — Architecture, BaseTool protocol, and token budget management
- [Built-in Tool Catalog](/docs/tools/catalog/) — Complete reference for all 50+ built-in tools
- [Agent Configuration](/docs/agents/configuration/) — Configure which tools each agent can access
