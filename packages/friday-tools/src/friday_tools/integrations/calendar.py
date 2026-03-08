# mypy: ignore-errors
"""Calendar integration (stub)."""

from typing import Any

from ..definition import BaseTool


class CalendarCreateEventTool(BaseTool):
    @property
    def name(self) -> str:
        return "calendar_create_event"

    @property
    def description(self) -> str:
        return "Create a calendar event (not yet implemented)."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "start": {"type": "string"},
                "end": {"type": "string"},
            },
            "required": ["title", "start", "end"],
        }

    async def execute(self, **kwargs: Any) -> str:
        raise NotImplementedError("calendar_create_event is not yet implemented")


class CalendarListEventsTool(BaseTool):
    @property
    def name(self) -> str:
        return "calendar_list_events"

    @property
    def description(self) -> str:
        return "List calendar events (not yet implemented)."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"date": {"type": "string"}},
            "required": [],
        }

    async def execute(self, **kwargs: Any) -> str:
        raise NotImplementedError("calendar_list_events is not yet implemented")


calendar_create_event = CalendarCreateEventTool()
calendar_list_events = CalendarListEventsTool()
