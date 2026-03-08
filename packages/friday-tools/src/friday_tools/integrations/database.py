# mypy: ignore-errors
"""Database integration (stub)."""

from typing import Any

from ..definition import BaseTool


class DatabaseQueryTool(BaseTool):
    @property
    def name(self) -> str:
        return "database_query"

    @property
    def description(self) -> str:
        return "Execute a SQL query (not yet implemented)."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "connection": {"type": "string"},
            },
            "required": ["query"],
        }

    async def execute(self, **kwargs: Any) -> str:
        raise NotImplementedError("database_query is not yet implemented")


database_query = DatabaseQueryTool()
