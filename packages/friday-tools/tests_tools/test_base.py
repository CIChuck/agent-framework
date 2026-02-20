import pytest
from pydantic import BaseModel, Field

from friday_tools.base import FridayTool, ToolResult


class AddToolInput(BaseModel):
    a: int = Field(..., description="First number")
    b: int = Field(..., description="Second number")


class AddTool(FridayTool):
    name = "add"
    description = "Adds two numbers"
    Input = AddToolInput

    async def run(self, args: AddToolInput) -> ToolResult:
        result = args.a + args.b
        return ToolResult(
            content=f"The sum is {result}",
            data={"sum": result},
            metadata={"operation": "add"},
        )


@pytest.mark.asyncio
async def test_schema_generation():
    tool = AddTool()

    # Check basic properties
    assert tool.name == "add"
    assert tool.description == "Adds two numbers"

    # Check schema generation
    schema = tool.parameters_schema
    assert "properties" in schema
    assert "a" in schema["properties"]
    assert "b" in schema["properties"]
    assert schema["properties"]["a"]["type"] == "integer"


@pytest.mark.asyncio
async def test_execution_success():
    tool = AddTool()

    # Test execution via execute() (string return)
    result_str = await tool.execute(a=10, b=5)
    assert result_str == "The sum is 15"

    # Test direct run() (structured return)
    args = AddToolInput(a=10, b=5)
    result_obj = await tool.run(args)
    assert isinstance(result_obj, ToolResult)
    assert result_obj.data["sum"] == 15


@pytest.mark.asyncio
async def test_validation_error():
    tool = AddTool()

    # Pass string instead of int
    result_str = await tool.execute(a="ten", b=5)
    assert "Error executing tool 'add'" in result_str
    assert "validation" in result_str.lower() or "input" in result_str.lower()
