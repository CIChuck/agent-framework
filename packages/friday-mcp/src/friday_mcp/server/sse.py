"""
SSE MCP Server.

Exposes Friday via HTTP Server-Sent Events.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any, AsyncGenerator

from friday_mcp.server.base import MCPServerBase

logger = logging.getLogger(__name__)


class SSEMCPServer(MCPServerBase):
    """
    MCP server using SSE transport.

    Provides HTTP endpoints for MCP communication via Server-Sent Events.
    Designed for integration with FastAPI/Starlette.

    Example (standalone):
        server = SSEMCPServer(host="0.0.0.0", port=8080)

        server.register_tool(
            name="echo",
            description="Echo input",
            input_schema={"type": "object", "properties": {"text": {"type": "string"}}},
            handler=lambda text: text
        )

        await server.start()  # Runs uvicorn

    Example (mount on existing FastAPI app):
        from fastapi import FastAPI

        app = FastAPI()
        server = SSEMCPServer()

        # Register tools...
        server.mount(app, path="/mcp")
    """

    def __init__(
        self,
        name: str = "friday-mcp-sse",
        host: str = "127.0.0.1",
        port: int = 8765,
        path: str = "/mcp",
    ):
        """
        Initialize SSE MCP server.

        Args:
            name: Server name for identification
            host: Host to bind to
            port: Port to listen on
            path: URL path prefix for MCP endpoints
        """
        super().__init__(name)
        self.host = host
        self.port = port
        self.path = path.rstrip("/")
        self._app: Any = None
        self._server: Any = None
        self._sessions: dict[str, asyncio.Queue[dict[str, Any] | None]] = {}

    def create_app(self) -> Any:
        """
        Create FastAPI/Starlette app with MCP endpoints.

        Returns:
            FastAPI application

        Raises:
            ImportError: If FastAPI is not installed
        """
        try:
            from fastapi import FastAPI, Request
            from fastapi.responses import StreamingResponse
        except ImportError as e:
            raise ImportError(
                "FastAPI is required for SSE server. "
                "Install with: pip install friday-mcp[server]"
            ) from e

        app = FastAPI(title=self.name)

        @app.get(f"{self.path}/sse")
        async def sse_endpoint(request: Request) -> StreamingResponse:
            """SSE endpoint for MCP communication."""
            session_id = str(uuid.uuid4())
            self._sessions[session_id] = asyncio.Queue()

            logger.debug(f"New SSE session: {session_id}")

            async def event_generator() -> AsyncGenerator[str, None]:
                # Send endpoint URL as first message
                base_url = str(request.base_url).rstrip("/")
                endpoint_url = f"{base_url}{self.path}/message?session={session_id}"

                yield f"data: {json.dumps({'endpoint': endpoint_url})}\n\n"

                try:
                    while True:
                        message = await self._sessions[session_id].get()
                        if message is None:
                            break
                        yield f"data: {json.dumps(message)}\n\n"
                except asyncio.CancelledError:
                    pass
                finally:
                    self._sessions.pop(session_id, None)
                    logger.debug(f"SSE session ended: {session_id}")

            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                },
            )

        @app.post(f"{self.path}/message")
        async def message_endpoint(request: Request, session: str) -> dict[str, str]:
            """Message endpoint for receiving JSON-RPC requests."""
            if session not in self._sessions:
                return {"error": "Invalid session"}

            body = await request.json()
            response = await self.handle_request(body)

            if response:
                await self._sessions[session].put(response)

            return {"status": "ok"}

        @app.get(f"{self.path}/health")
        async def health_check() -> dict[str, Any]:
            """Health check endpoint."""
            return {
                "status": "healthy",
                "server": self.name,
                "tools": self.tool_count,
                "prompts": self.prompt_count,
                "resources": self.resource_count,
                "sessions": len(self._sessions),
            }

        self._app = app
        return app

    def mount(self, app: Any, path: str | None = None) -> None:
        """
        Mount MCP endpoints on an existing FastAPI app.

        Args:
            app: FastAPI application
            path: Optional path prefix override
        """
        if path:
            self.path = path.rstrip("/")

        mcp_app = self.create_app()
        app.mount(self.path, mcp_app)
        logger.info(f"Mounted MCP server at {self.path}")

    async def start(self) -> None:
        """
        Start standalone server with uvicorn.

        Raises:
            ImportError: If uvicorn is not installed
        """
        try:
            import uvicorn
        except ImportError as e:
            raise ImportError(
                "uvicorn is required for standalone SSE server. "
                "Install with: pip install friday-mcp[server]"
            ) from e

        self._running = True
        app = self.create_app()

        logger.info(f"Starting SSE MCP server at http://{self.host}:{self.port}")

        config = uvicorn.Config(
            app,
            host=self.host,
            port=self.port,
            log_level="info",
        )
        self._server = uvicorn.Server(config)
        await self._server.serve()

    async def stop(self) -> None:
        """Stop the server."""
        self._running = False

        if self._server:
            self._server.should_exit = True

        # Close all sessions
        for queue in self._sessions.values():
            await queue.put(None)

        self._sessions.clear()
        logger.info("SSE MCP server stopped")

    async def send_to_session(
        self,
        session_id: str,
        message: dict[str, Any],
    ) -> bool:
        """
        Send a message to a specific session.

        Args:
            session_id: Session ID
            message: Message to send

        Returns:
            True if message was sent
        """
        if session_id not in self._sessions:
            return False

        await self._sessions[session_id].put(message)
        return True

    @property
    def active_sessions(self) -> int:
        """Number of active SSE sessions."""
        return len(self._sessions)
