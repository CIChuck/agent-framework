"""
HTTP client tools.

Ref: docs/specs/tool_specification.md - Category 6: HTTP Client
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

from ..definition import BaseTool
from ..sandbox import FilesystemSandbox


class HttpGetTool(BaseTool):
    """Make HTTP GET request."""

    @property
    def name(self) -> str:
        return "http_get"

    @property
    def description(self) -> str:
        return "Make an HTTP GET request to a URL."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to request",
                },
                "headers": {
                    "type": "object",
                    "description": "Request headers",
                    "additionalProperties": {"type": "string"},
                },
                "params": {
                    "type": "object",
                    "description": "Query parameters",
                    "additionalProperties": {"type": "string"},
                },
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds",
                    "default": 30,
                },
            },
            "required": ["url"],
        }

    async def execute(self, **kwargs: Any) -> str:
        url = kwargs["url"]
        headers = kwargs.get("headers", {})
        params = kwargs.get("params", {})
        timeout = kwargs.get("timeout", 30)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, headers=headers, params=params)

            return self._format_response(response)

        except httpx.TimeoutException:
            return f"Error: Request timed out after {timeout} seconds"
        except Exception as e:
            return f"Error: {e}"

    def _format_response(self, response: httpx.Response) -> str:
        """Format HTTP response for output."""
        lines = [
            f"Status: {response.status_code} {response.reason_phrase}",
            "",
            "Headers:",
        ]
        for key, value in response.headers.items():
            lines.append(f"  {key}: {value}")

        lines.append("")
        lines.append("Body:")

        # Try to parse as JSON for pretty printing
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                data = response.json()
                lines.append(json.dumps(data, indent=2))
            except Exception:
                lines.append(response.text[:5000])
        else:
            lines.append(response.text[:5000])

        if len(response.text) > 5000:
            lines.append("\n...(truncated)")

        return "\n".join(lines)


class HttpPostTool(BaseTool):
    """Make HTTP POST request."""

    @property
    def name(self) -> str:
        return "http_post"

    @property
    def description(self) -> str:
        return "Make an HTTP POST request with JSON or form data."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to request",
                },
                "json_data": {
                    "type": "object",
                    "description": "JSON body to send",
                },
                "form_data": {
                    "type": "object",
                    "description": "Form data to send (mutually exclusive with json_data)",
                },
                "headers": {
                    "type": "object",
                    "description": "Request headers",
                    "additionalProperties": {"type": "string"},
                },
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds",
                    "default": 30,
                },
            },
            "required": ["url"],
        }

    async def execute(self, **kwargs: Any) -> str:
        url = kwargs["url"]
        json_data = kwargs.get("json_data")
        form_data = kwargs.get("form_data")
        headers = kwargs.get("headers", {})
        timeout = kwargs.get("timeout", 30)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if json_data:
                    response = await client.post(url, json=json_data, headers=headers)
                elif form_data:
                    response = await client.post(url, data=form_data, headers=headers)
                else:
                    response = await client.post(url, headers=headers)

            return HttpGetTool()._format_response(response)

        except httpx.TimeoutException:
            return f"Error: Request timed out after {timeout} seconds"
        except Exception as e:
            return f"Error: {e}"


class HttpPutTool(BaseTool):
    """Make HTTP PUT request."""

    @property
    def name(self) -> str:
        return "http_put"

    @property
    def description(self) -> str:
        return "Make an HTTP PUT request with JSON or form data."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to request",
                },
                "json_data": {
                    "type": "object",
                    "description": "JSON body to send",
                },
                "headers": {
                    "type": "object",
                    "description": "Request headers",
                    "additionalProperties": {"type": "string"},
                },
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds",
                    "default": 30,
                },
            },
            "required": ["url"],
        }

    async def execute(self, **kwargs: Any) -> str:
        url = kwargs["url"]
        json_data = kwargs.get("json_data")
        headers = kwargs.get("headers", {})
        timeout = kwargs.get("timeout", 30)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if json_data:
                    response = await client.put(url, json=json_data, headers=headers)
                else:
                    response = await client.put(url, headers=headers)

            return HttpGetTool()._format_response(response)

        except httpx.TimeoutException:
            return f"Error: Request timed out after {timeout} seconds"
        except Exception as e:
            return f"Error: {e}"


class HttpDeleteTool(BaseTool):
    """Make HTTP DELETE request."""

    @property
    def name(self) -> str:
        return "http_delete"

    @property
    def description(self) -> str:
        return "Make an HTTP DELETE request."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to request",
                },
                "headers": {
                    "type": "object",
                    "description": "Request headers",
                    "additionalProperties": {"type": "string"},
                },
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds",
                    "default": 30,
                },
            },
            "required": ["url"],
        }

    async def execute(self, **kwargs: Any) -> str:
        url = kwargs["url"]
        headers = kwargs.get("headers", {})
        timeout = kwargs.get("timeout", 30)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.delete(url, headers=headers)

            return HttpGetTool()._format_response(response)

        except httpx.TimeoutException:
            return f"Error: Request timed out after {timeout} seconds"
        except Exception as e:
            return f"Error: {e}"


class HttpDownloadTool(BaseTool):
    """Download a file from URL."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "http_download"

    @property
    def description(self) -> str:
        return "Download a file from a URL and save it locally."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to download from",
                },
                "destination": {
                    "type": "string",
                    "description": "Local path to save the file",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds",
                    "default": 60,
                },
            },
            "required": ["url", "destination"],
        }

    async def execute(self, **kwargs: Any) -> str:
        url = kwargs["url"]
        destination = kwargs["destination"]
        timeout = kwargs.get("timeout", 60)

        dest_path = self._sandbox.validate_path(destination)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream("GET", url) as response:
                    response.raise_for_status()

                    dest_path.parent.mkdir(parents=True, exist_ok=True)

                    total_size = 0
                    with dest_path.open("wb") as f:
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            f.write(chunk)
                            total_size += len(chunk)

            return f"Downloaded {total_size} bytes to {destination}"

        except httpx.TimeoutException:
            return f"Error: Download timed out after {timeout} seconds"
        except httpx.HTTPStatusError as e:
            return f"Error: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error: {e}"


class HttpUploadTool(BaseTool):
    """Upload a file to URL."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "http_upload"

    @property
    def description(self) -> str:
        return "Upload a file to a URL using multipart form data."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to upload to",
                },
                "file_path": {
                    "type": "string",
                    "description": "Local path of the file to upload",
                },
                "field_name": {
                    "type": "string",
                    "description": "Form field name for the file",
                    "default": "file",
                },
                "headers": {
                    "type": "object",
                    "description": "Request headers",
                    "additionalProperties": {"type": "string"},
                },
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds",
                    "default": 60,
                },
            },
            "required": ["url", "file_path"],
        }

    async def execute(self, **kwargs: Any) -> str:
        url = kwargs["url"]
        file_path = kwargs["file_path"]
        field_name = kwargs.get("field_name", "file")
        headers = kwargs.get("headers", {})
        timeout = kwargs.get("timeout", 60)

        src_path = self._sandbox.validate_path(file_path)

        if not src_path.exists():
            return f"Error: File not found: {file_path}"

        try:
            content = src_path.read_bytes()

            async with httpx.AsyncClient(timeout=timeout) as client:
                files = {field_name: (src_path.name, content)}
                response = await client.post(url, files=files, headers=headers)

            return HttpGetTool()._format_response(response)

        except httpx.TimeoutException:
            return f"Error: Upload timed out after {timeout} seconds"
        except Exception as e:
            return f"Error: {e}"


# Convenience instances
http_get = HttpGetTool()
http_post = HttpPostTool()
http_put = HttpPutTool()
http_delete = HttpDeleteTool()
http_download = HttpDownloadTool()
http_upload = HttpUploadTool()
