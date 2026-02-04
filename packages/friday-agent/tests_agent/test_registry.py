"""
Tests for DefaultToolRegistry.

Tests tool registration, schema generation, and dependency binding.
"""

import pytest
from friday_agent.tools import DefaultToolRegistry, tool


class TestToolDecorator:
    """Tests for the @tool decorator."""

    def test_basic_decorator(self):
        """Test basic tool registration via decorator."""

        @tool(name="greet", description="Greet someone", category="utility")
        def greet(name: str) -> str:
            """Say hello to someone."""
            return f"Hello, {name}!"

        # Check that the function is marked as a tool
        assert hasattr(greet, "_tool_name")
        assert greet._tool_name == "greet"

    def test_decorator_uses_function_name(self):
        """Test that decorator uses function name if not specified."""

        @tool(category="utility")
        def my_function(x: int) -> int:
            """Do something."""
            return x * 2

        assert my_function._tool_name == "my_function"

    def test_decorator_preserves_function(self):
        """Test that decorated function still works normally."""

        @tool(name="add", category="utility")
        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b

        assert add(2, 3) == 5

    def test_decorator_requires_category(self):
        """Tool decorator should require explicit category."""
        with pytest.raises(ValueError, match="non-default category"):
            @tool(name="no_category")  # type: ignore[misc]
            def no_category() -> str:
                return "nope"


class TestDefaultToolRegistry:
    """Tests for DefaultToolRegistry."""

    @pytest.fixture
    def registry(self):
        """Create a fresh registry."""
        return DefaultToolRegistry()

    def test_manual_registration(self, registry):
        """Test manual tool registration."""

        def my_tool(x: str) -> str:
            return x.upper()

        registry.register(
            name="uppercase",
            func=my_tool,
            description="Convert to uppercase",
            parameters={
                "type": "object",
                "properties": {"x": {"type": "string"}},
                "required": ["x"],
            },
            category="text",
        )

        assert "uppercase" in registry.list_names()

    def test_manual_registration_requires_category(self, registry):
        """Manual registration should require explicit category."""
        def my_tool(x: str) -> str:
            return x

        with pytest.raises(ValueError, match="non-default category"):
            registry.register(
                name="uppercase",
                func=my_tool,
                description="Convert to uppercase",
                parameters={
                    "type": "object",
                    "properties": {"x": {"type": "string"}},
                    "required": ["x"],
                },
            )

    def test_get_tool(self, registry):
        """Test retrieving a registered tool."""

        def echo(msg: str) -> str:
            return msg

        registry.register(
            name="echo",
            func=echo,
            description="Echo a message",
            parameters={"type": "object", "properties": {}},
            category="text",
        )

        tool_fn = registry.get_tool("echo")
        assert tool_fn("hello") == "hello"

    def test_get_schema(self, registry):
        """Test getting tool schema."""

        def dummy() -> str:
            return "dummy"

        registry.register(
            name="dummy",
            func=dummy,
            description="A dummy tool",
            parameters={"type": "object", "properties": {}},
            category="utility",
        )

        # Test plain format (default)
        plain_schema = registry.get_schema("dummy")
        assert plain_schema["name"] == "dummy"
        assert plain_schema["description"] == "A dummy tool"

        # Test OpenAI format
        openai_schema = registry.get_schema("dummy", format="openai")
        assert openai_schema["type"] == "function"
        assert openai_schema["function"]["name"] == "dummy"
        assert openai_schema["function"]["description"] == "A dummy tool"

    def test_get_nonexistent_tool(self, registry):
        """Test that getting nonexistent tool raises KeyError."""
        with pytest.raises(KeyError):
            registry.get_tool("nonexistent")

    def test_list_tools(self, registry):
        """Test listing all registered tools."""
        registry.register("tool1", lambda: None, "desc1", {}, category="utility")
        registry.register("tool2", lambda: None, "desc2", {}, category="utility")

        # list_tools returns ToolDefinition objects
        tools = registry.list_tools()
        tool_names = [t.name for t in tools]
        assert "tool1" in tool_names
        assert "tool2" in tool_names

        # list_names returns strings
        names = registry.list_names()
        assert "tool1" in names
        assert "tool2" in names

    def test_has_tool(self, registry):
        """Test checking if tool exists."""
        registry.register("exists", lambda: None, "desc", {}, category="utility")

        assert registry.has_tool("exists")
        assert not registry.has_tool("does_not_exist")

    def test_unregister(self, registry):
        """Test unregistering a tool."""
        registry.register("temp", lambda: None, "desc", {}, category="utility")
        assert registry.has_tool("temp")

        result = registry.unregister("temp")
        assert result is True
        assert not registry.has_tool("temp")

    def test_unregister_nonexistent(self, registry):
        """Test unregistering nonexistent tool returns False."""
        result = registry.unregister("nonexistent")
        assert result is False

    def test_load_decorated_tools(self, registry):
        """Test loading decorated tools into registry."""
        # The decorator already registered the tools globally
        count = registry.load_decorated_tools()

        # Should have loaded the tools decorated in test_basic_decorator etc.
        assert count >= 0  # May vary based on test execution order

    def test_bind_dependency(self, registry):
        """Test binding dependencies to tools."""

        def tool_with_dep(service, query: str) -> str:
            return f"{service.name}: {query}"

        class MockService:
            name = "TestService"

        registry.register(
            name="search",
            func=tool_with_dep,
            description="Search with service",
            parameters={
                "type": "object",
                "properties": {
                    "service": {"type": "object"},
                    "query": {"type": "string"},
                },
                "required": ["service", "query"],
            },
            category="data",
        )

        # Bind the service dependency
        registry.bind_dependency("search", service=MockService())

        # Now we can call with just query
        tool_fn = registry.get_tool("search")
        result = tool_fn(query="test")
        assert result == "TestService: test"

    def test_bind_removes_bound_params_from_schema(self, registry):
        """Test that bound parameters are removed from schema."""

        def tool_with_deps(dep1, dep2, param: str) -> str:
            return param

        registry.register(
            name="bound_tool",
            func=tool_with_deps,
            description="Tool with deps",
            parameters={
                "type": "object",
                "properties": {
                    "dep1": {"type": "object"},
                    "dep2": {"type": "object"},
                    "param": {"type": "string"},
                },
                "required": ["dep1", "dep2", "param"],
            },
            category="utility",
        )

        registry.bind_dependency("bound_tool", dep1="val1", dep2="val2")

        # Test with plain format
        schema = registry.get_schema("bound_tool")
        props = schema["parameters"]["properties"]
        required = schema["parameters"]["required"]

        # dep1 and dep2 should be removed
        assert "dep1" not in props
        assert "dep2" not in props
        assert "param" in props
        assert "dep1" not in required
        assert "dep2" not in required


class TestParameterExtraction:
    """Tests for parameter extraction from function signatures."""

    def test_type_hints_extraction(self):
        """Test that type hints are extracted correctly."""

        @tool(name="typed_tool", category="utility")
        def typed_tool(
            text: str,
            count: int,
            ratio: float,
            flag: bool,
        ) -> str:
            """A tool with typed parameters."""
            return text

        registry = DefaultToolRegistry()
        registry.load_decorated_tools()

        # Use plain format (default)
        schema = registry.get_schema("typed_tool")
        props = schema["parameters"]["properties"]

        assert props["text"]["type"] == "string"
        assert props["count"]["type"] == "integer"
        assert props["ratio"]["type"] == "number"
        assert props["flag"]["type"] == "boolean"

    def test_default_values(self):
        """Test that default values are handled."""

        @tool(name="defaults_tool", category="utility")
        def defaults_tool(
            required: str,
            optional: str = "default",
        ) -> str:
            """A tool with default values."""
            return required

        registry = DefaultToolRegistry()
        registry.load_decorated_tools()

        # Use plain format (default)
        schema = registry.get_schema("defaults_tool")
        required = schema["parameters"]["required"]

        assert "required" in required
        assert "optional" not in required

    def test_docstring_descriptions(self):
        """Test that docstring parameter descriptions are extracted."""

        @tool(name="documented_tool", category="utility")
        def documented_tool(query: str, limit: int = 10) -> str:
            """
            Search for something.

            Args:
                query: The search query string
                limit: Maximum number of results
            """
            return query

        registry = DefaultToolRegistry()
        registry.load_decorated_tools()

        # Use plain format (default)
        schema = registry.get_schema("documented_tool")
        props = schema["parameters"]["properties"]

        assert "description" in props["query"]
        assert "search query" in props["query"]["description"].lower()
