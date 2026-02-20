"""Tests for tool protocols and base classes."""

import pytest

from friday_tools import DefaultToolRegistry, FunctionTool


class TestBaseTool:
    def test_function_tool_creation(self):
        async def greet(name: str) -> str:
            """Greet someone."""
            return f"Hello, {name}!"

        ft = FunctionTool(greet, category="utility")
        assert ft.name == "greet"
        assert "name" in ft.parameters_schema["properties"]

    def test_function_tool_schema_generation(self):
        async def add(a: int, b: int) -> int:
            return a + b

        ft = FunctionTool(add, name="add_numbers", category="utility")
        assert ft.name == "add_numbers"
        assert ft.parameters_schema["properties"]["a"]["type"] == "integer"


class TestToolRegistry:
    def test_register_and_get(self):
        registry = DefaultToolRegistry()

        async def my_tool(x: str) -> str:
            return x

        ft = FunctionTool(my_tool, category="utility")
        registry.register(ft)

        assert registry.get("my_tool") is not None
        assert "my_tool" in registry.list_names()

    def test_duplicate_registration_error(self):
        registry = DefaultToolRegistry()

        async def my_tool(x: str) -> str:
            return x

        ft = FunctionTool(my_tool, category="utility")
        registry.register(ft)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(ft)

    def test_decorator_registration(self):
        registry = DefaultToolRegistry()

        @registry.tool(name="decorated_tool", category="utility")
        async def some_func(x: str) -> str:
            return x

        assert "decorated_tool" in registry.list_names()

    def test_get_schemas(self):
        registry = DefaultToolRegistry()

        async def tool_a(x: str) -> str:
            return x

        async def tool_b(y: int) -> int:
            return y

        registry.register(FunctionTool(tool_a, category="utility"))
        registry.register(FunctionTool(tool_b, category="utility"))

        schemas = registry.get_schemas()
        assert len(schemas) == 2
        names = [s["name"] for s in schemas]
        assert "tool_a" in names
        assert "tool_b" in names
