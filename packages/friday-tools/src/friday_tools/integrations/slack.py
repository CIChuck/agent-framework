"""Slack integration (stub)."""

from typing import Any

from ..definition import BaseTool


class SlackSendTool(BaseTool):
    @property
    def name(self) -> str:
        return "slack_send"

    @property
    def description(self) -> str:
        return "Send a Slack message (not yet implemented)."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "channel": {"type": "string"},
                "message": {"type": "string"},
            },
            "required": ["channel", "message"],
        }

    async def execute(self, **kwargs: Any) -> str:
        raise NotImplementedError("slack_send is not yet implemented")


slack_send = SlackSendTool()
