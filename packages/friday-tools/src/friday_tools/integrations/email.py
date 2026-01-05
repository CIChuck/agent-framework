"""Email integration (stub)."""
from typing import Any
from ..definition import BaseTool

class EmailSendTool(BaseTool):
    @property
    def name(self) -> str: return "email_send"
    @property
    def description(self) -> str: return "Send an email (not yet implemented)."
    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}, "required": ["to", "subject", "body"]}
    async def execute(self, **kwargs: Any) -> str:
        raise NotImplementedError("email_send is not yet implemented")

email_send = EmailSendTool()
