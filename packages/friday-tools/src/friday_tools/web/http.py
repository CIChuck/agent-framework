# mypy: ignore-errors
"""
HTTP client tools.

Ref: docs/reference/specs/tool_specification.md - Category 6: HTTP Client

All tools use shared infrastructure:
- URL validation with SSRF protection (validators.py)
- Configured HTTP client (client.py)
- Response formatting (client.py)
"""

from __future__ import annotations

from typing import Any

import httpx

from ..definition import BaseTool
from ..sandbox import FilesystemSandbox
from .client import create_http_client, format_http_response
from .config import DEFAULT_WEB_CONFIG, WebConfig
from .validators import URLValidationError, validate_url


class HttpGetTool(BaseTool):
    """Make HTTP GET request with SSRF protection."""

    def __init__(
        self,
        config: WebConfig | dict | None = None,
        sandbox: FilesystemSandbox | None = None,
    ):
        """
        Initialize HttpGetTool with configuration.

        Args:
            config: WebConfig instance, dict from YAML, or None for defaults
            sandbox: Optional filesystem sandbox for path validation
        """
        if config is None:
            self._config = DEFAULT_WEB_CONFIG
        elif isinstance(config, dict):
            self._config = WebConfig.from_dict(config)
        else:
            self._config = config
        self._sandbox = sandbox

    @property
    def name(self) -> str:
        return "http_get"

    @property
    def description(self) -> str:
        return "Make an HTTP GET request to a URL with SSRF protection."

    @property
    def category(self) -> str:
        return "web"

    @property
    def tags(self) -> list[str]:
        return ["http", "async", "read-only"]

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
                    "description": "Request timeout in seconds (overrides config)",
                },
            },
            "required": ["url"],
        }

    async def execute(self, **kwargs: Any) -> str:
        url = kwargs["url"]
        headers = kwargs.get("headers", {})
        params = kwargs.get("params", {})
        timeout = kwargs.get("timeout")

        # Validate URL (SSRF protection)
        try:
            validated_url = validate_url(
                url,
                allow_private_ips=self._config.security.allow_private_ips,
                blocked_hosts=set(self._config.security.blocked_hosts),
            )
        except URLValidationError as e:
            return f"Error: URL validation failed - {e}"

        # Override timeout if provided
        config = self._config
        if timeout is not None:
            # Create a modified config with the new timeout
            from copy import deepcopy

            config = deepcopy(self._config)
            config.client.timeout = float(timeout)

        try:
            async with create_http_client(config) as client:
                response = await client.get(
                    validated_url, headers=headers, params=params
                )

            return format_http_response(response)

        except httpx.TimeoutException:
            return f"Error: Request timed out after {config.client.timeout} seconds"
        except Exception as e:
            return f"Error: {type(e).__name__}: {e}"


class HttpPostTool(BaseTool):
    """Make HTTP POST request with SSRF protection."""

    def __init__(
        self,
        config: WebConfig | dict | None = None,
        sandbox: FilesystemSandbox | None = None,
    ):
        if config is None:
            self._config = DEFAULT_WEB_CONFIG
        elif isinstance(config, dict):
            self._config = WebConfig.from_dict(config)
        else:
            self._config = config
        self._sandbox = sandbox

    @property
    def name(self) -> str:
        return "http_post"

    @property
    def description(self) -> str:
        return "Make an HTTP POST request with JSON or form data."

    @property
    def category(self) -> str:
        return "web"

    @property
    def tags(self) -> list[str]:
        return ["http", "async"]

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
                    "description": (
                        "Form data to send (mutually exclusive with json_data)"
                    ),
                },
                "headers": {
                    "type": "object",
                    "description": "Request headers",
                    "additionalProperties": {"type": "string"},
                },
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds (overrides config)",
                },
            },
            "required": ["url"],
        }

    async def execute(self, **kwargs: Any) -> str:
        url = kwargs["url"]
        json_data = kwargs.get("json_data")
        form_data = kwargs.get("form_data")
        headers = kwargs.get("headers", {})
        timeout = kwargs.get("timeout")

        # Validate URL (SSRF protection)
        try:
            validated_url = validate_url(
                url,
                allow_private_ips=self._config.security.allow_private_ips,
                blocked_hosts=set(self._config.security.blocked_hosts),
            )
        except URLValidationError as e:
            return f"Error: URL validation failed - {e}"

        # Override timeout if provided
        config = self._config
        if timeout is not None:
            from copy import deepcopy

            config = deepcopy(self._config)
            config.client.timeout = float(timeout)

        try:
            async with create_http_client(config) as client:
                if json_data:
                    response = await client.post(
                        validated_url, json=json_data, headers=headers
                    )
                elif form_data:
                    response = await client.post(
                        validated_url, data=form_data, headers=headers
                    )
                else:
                    response = await client.post(validated_url, headers=headers)

            return format_http_response(response)

        except httpx.TimeoutException:
            return f"Error: Request timed out after {config.client.timeout} seconds"
        except Exception as e:
            return f"Error: {type(e).__name__}: {e}"


class HttpPutTool(BaseTool):
    """Make HTTP PUT request with SSRF protection."""

    def __init__(
        self,
        config: WebConfig | dict | None = None,
        sandbox: FilesystemSandbox | None = None,
    ):
        if config is None:
            self._config = DEFAULT_WEB_CONFIG
        elif isinstance(config, dict):
            self._config = WebConfig.from_dict(config)
        else:
            self._config = config
        self._sandbox = sandbox

    @property
    def name(self) -> str:
        return "http_put"

    @property
    def description(self) -> str:
        return "Make an HTTP PUT request with JSON or form data."

    @property
    def category(self) -> str:
        return "web"

    @property
    def tags(self) -> list[str]:
        return ["http", "async"]

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
                    "description": "Request timeout in seconds (overrides config)",
                },
            },
            "required": ["url"],
        }

    async def execute(self, **kwargs: Any) -> str:
        url = kwargs["url"]
        json_data = kwargs.get("json_data")
        headers = kwargs.get("headers", {})
        timeout = kwargs.get("timeout")

        # Validate URL (SSRF protection)
        try:
            validated_url = validate_url(
                url,
                allow_private_ips=self._config.security.allow_private_ips,
                blocked_hosts=set(self._config.security.blocked_hosts),
            )
        except URLValidationError as e:
            return f"Error: URL validation failed - {e}"

        # Override timeout if provided
        config = self._config
        if timeout is not None:
            from copy import deepcopy

            config = deepcopy(self._config)
            config.client.timeout = float(timeout)

        try:
            async with create_http_client(config) as client:
                if json_data:
                    response = await client.put(
                        validated_url, json=json_data, headers=headers
                    )
                else:
                    response = await client.put(validated_url, headers=headers)

            return format_http_response(response)

        except httpx.TimeoutException:
            return f"Error: Request timed out after {config.client.timeout} seconds"
        except Exception as e:
            return f"Error: {type(e).__name__}: {e}"


class HttpDeleteTool(BaseTool):
    """Make HTTP DELETE request with SSRF protection."""

    def __init__(
        self,
        config: WebConfig | dict | None = None,
        sandbox: FilesystemSandbox | None = None,
    ):
        if config is None:
            self._config = DEFAULT_WEB_CONFIG
        elif isinstance(config, dict):
            self._config = WebConfig.from_dict(config)
        else:
            self._config = config
        self._sandbox = sandbox

    @property
    def name(self) -> str:
        return "http_delete"

    @property
    def description(self) -> str:
        return "Make an HTTP DELETE request."

    @property
    def category(self) -> str:
        return "web"

    @property
    def tags(self) -> list[str]:
        return ["http", "async"]

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
                    "description": "Request timeout in seconds (overrides config)",
                },
            },
            "required": ["url"],
        }

    async def execute(self, **kwargs: Any) -> str:
        url = kwargs["url"]
        headers = kwargs.get("headers", {})
        timeout = kwargs.get("timeout")

        # Validate URL (SSRF protection)
        try:
            validated_url = validate_url(
                url,
                allow_private_ips=self._config.security.allow_private_ips,
                blocked_hosts=set(self._config.security.blocked_hosts),
            )
        except URLValidationError as e:
            return f"Error: URL validation failed - {e}"

        # Override timeout if provided
        config = self._config
        if timeout is not None:
            from copy import deepcopy

            config = deepcopy(self._config)
            config.client.timeout = float(timeout)

        try:
            async with create_http_client(config) as client:
                response = await client.delete(validated_url, headers=headers)

            return format_http_response(response)

        except httpx.TimeoutException:
            return f"Error: Request timed out after {config.client.timeout} seconds"
        except Exception as e:
            return f"Error: {type(e).__name__}: {e}"


class HttpDownloadTool(BaseTool):
    """Download a file from URL with SSRF protection."""

    def __init__(
        self,
        config: WebConfig | dict | None = None,
        sandbox: FilesystemSandbox | None = None,
    ):
        if config is None:
            self._config = DEFAULT_WEB_CONFIG
        elif isinstance(config, dict):
            self._config = WebConfig.from_dict(config)
        else:
            self._config = config
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "http_download"

    @property
    def description(self) -> str:
        return "Download a file from a URL and save it locally."

    @property
    def category(self) -> str:
        return "web"

    @property
    def tags(self) -> list[str]:
        return ["http", "async", "file-write"]

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
                    "description": "Request timeout in seconds (overrides config)",
                },
            },
            "required": ["url", "destination"],
        }

    async def execute(self, **kwargs: Any) -> str:
        url = kwargs["url"]
        destination = kwargs["destination"]
        timeout = kwargs.get("timeout")

        # Validate URL (SSRF protection)
        try:
            validated_url = validate_url(
                url,
                allow_private_ips=self._config.security.allow_private_ips,
                blocked_hosts=set(self._config.security.blocked_hosts),
            )
        except URLValidationError as e:
            return f"Error: URL validation failed - {e}"

        dest_path = self._sandbox.validate_path(destination)

        # Override timeout if provided
        config = self._config
        if timeout is not None:
            from copy import deepcopy

            config = deepcopy(self._config)
            config.client.timeout = float(timeout)

        try:
            async with create_http_client(config) as client:
                response = await client.get(validated_url)
                response.raise_for_status()

                # Check Content-Length if present
                content_length = response.headers.get("content-length")
                if content_length:
                    size = int(content_length)
                    if size > config.client.max_response_size:
                        return (
                            f"Error: File too large ({size} bytes, "
                            f"max: {config.client.max_response_size})"
                        )

                dest_path.parent.mkdir(parents=True, exist_ok=True)

                content = response.content
                total_size = len(content)
                if total_size > config.client.max_response_size:
                    return (
                        f"Error: Download exceeded max size "
                        f"({config.client.max_response_size} bytes)"
                    )

                dest_path.write_bytes(content)

            return f"Downloaded {total_size} bytes to {destination}"

        except httpx.TimeoutException:
            return f"Error: Download timed out after {config.client.timeout} seconds"
        except httpx.HTTPStatusError as e:
            return f"Error: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error: {type(e).__name__}: {e}"


class HttpUploadTool(BaseTool):
    """Upload a file to URL with SSRF protection."""

    def __init__(
        self,
        config: WebConfig | dict | None = None,
        sandbox: FilesystemSandbox | None = None,
    ):
        if config is None:
            self._config = DEFAULT_WEB_CONFIG
        elif isinstance(config, dict):
            self._config = WebConfig.from_dict(config)
        else:
            self._config = config
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "http_upload"

    @property
    def description(self) -> str:
        return "Upload a file to a URL using multipart form data."

    @property
    def category(self) -> str:
        return "web"

    @property
    def tags(self) -> list[str]:
        return ["http", "async", "file-read"]

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
                    "description": "Request timeout in seconds (overrides config)",
                },
            },
            "required": ["url", "file_path"],
        }

    async def execute(self, **kwargs: Any) -> str:
        url = kwargs["url"]
        file_path = kwargs["file_path"]
        field_name = kwargs.get("field_name", "file")
        headers = kwargs.get("headers", {})
        timeout = kwargs.get("timeout")

        # Validate URL (SSRF protection)
        try:
            validated_url = validate_url(
                url,
                allow_private_ips=self._config.security.allow_private_ips,
                blocked_hosts=set(self._config.security.blocked_hosts),
            )
        except URLValidationError as e:
            return f"Error: URL validation failed - {e}"

        src_path = self._sandbox.validate_path(file_path)

        if not src_path.exists():
            return f"Error: File not found: {file_path}"

        # Override timeout if provided
        config = self._config
        if timeout is not None:
            from copy import deepcopy

            config = deepcopy(self._config)
            config.client.timeout = float(timeout)

        try:
            content = src_path.read_bytes()

            async with create_http_client(config) as client:
                files = {field_name: (src_path.name, content)}
                response = await client.post(
                    validated_url, files=files, headers=headers
                )

            return format_http_response(response)

        except httpx.TimeoutException:
            return f"Error: Upload timed out after {config.client.timeout} seconds"
        except Exception as e:
            return f"Error: {type(e).__name__}: {e}"


# Convenience instances with default configuration
http_get = HttpGetTool()
http_post = HttpPostTool()
http_put = HttpPutTool()
http_delete = HttpDeleteTool()
http_download = HttpDownloadTool()
http_upload = HttpUploadTool()
