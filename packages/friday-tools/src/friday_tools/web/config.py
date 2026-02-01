"""
Web tools configuration.

Provides Pydantic models for configuring HTTP client, SSL, proxy,
security, and content extraction settings.

Ref: docs/specs/tool_specification.md - Category 5-6: Web Tools
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class HttpClientConfig(BaseModel):
    """HTTP client configuration."""

    timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=600.0,
        description="Request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Number of retries for transient failures",
    )
    follow_redirects: bool = Field(
        default=True,
        description="Follow HTTP redirects",
    )
    max_response_size: int = Field(
        default=10_000_000,
        ge=1000,
        description="Maximum response size in bytes (default 10MB)",
    )
    user_agent: str = Field(
        default="Mozilla/5.0 (compatible; FridayBot/1.0)",
        description="User-Agent header for requests",
    )


class SSLConfig(BaseModel):
    """SSL/TLS configuration."""

    verify: bool = Field(
        default=True,
        description="Verify SSL certificates",
    )
    ca_bundle: str | None = Field(
        default=None,
        description="Path to custom CA bundle (None = system default)",
    )


class ProxyConfig(BaseModel):
    """Proxy configuration."""

    http: str | None = Field(
        default=None,
        description="HTTP proxy URL (e.g., 'http://proxy:8080')",
    )
    https: str | None = Field(
        default=None,
        description="HTTPS proxy URL",
    )
    no_proxy: list[str] = Field(
        default_factory=lambda: ["localhost", "127.0.0.1"],
        description="Hosts to bypass proxy",
    )


class SecurityConfig(BaseModel):
    """Security settings for SSRF protection."""

    allow_private_ips: bool = Field(
        default=False,
        description="Allow requests to private/internal IP addresses",
    )
    blocked_hosts: list[str] = Field(
        default_factory=list,
        description="Additional hosts to block",
    )


class ReaderConfig(BaseModel):
    """Content extraction configuration for WebReaderTool."""

    default_format: Literal["auto", "markdown", "text", "html", "json"] = Field(
        default="auto",
        description="Default output format (auto detects from Content-Type)",
    )
    max_content_length: int = Field(
        default=50000,
        ge=1000,
        le=2000000,
        description="Maximum output length in characters (max 2MB)",
    )
    include_metadata: bool = Field(
        default=False,
        description="Include page metadata (title, description, etc.)",
    )
    remove_elements: list[str] = Field(
        default_factory=lambda: [
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "iframe",
            "noscript",
        ],
        description="HTML elements to remove before extraction",
    )


class WebConfig(BaseModel):
    """
    Complete web tools configuration.

    This configuration is used by WebReaderTool, HTTP tools, and other
    web-related functionality. It can be loaded from YAML or passed directly.

    Example YAML:
        web:
          client:
            timeout: 30
            max_retries: 3
          ssl:
            verify: true
          proxy:
            http: "http://proxy:8080"
          security:
            allow_private_ips: false
          reader:
            default_format: "markdown"
          serper_api_key: "your-api-key-here"
    """

    client: HttpClientConfig = Field(default_factory=HttpClientConfig)
    ssl: SSLConfig = Field(default_factory=SSLConfig)
    proxy: ProxyConfig = Field(default_factory=ProxyConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    reader: ReaderConfig = Field(default_factory=ReaderConfig)
    serper_api_key: str | None = Field(
        default=None,
        description="API key for Serper.dev Google SERP API",
    )

    @classmethod
    def from_dict(cls, data: dict) -> WebConfig:
        """
        Load configuration from a dictionary (e.g., YAML section).

        Args:
            data: Dictionary with optional keys: client, ssl, proxy, security,
                  reader, serper_api_key

        Returns:
            WebConfig instance with merged defaults
        """
        return cls(
            client=HttpClientConfig(**data.get("client", {})),
            ssl=SSLConfig(**data.get("ssl", {})),
            proxy=ProxyConfig(**data.get("proxy", {})),
            security=SecurityConfig(**data.get("security", {})),
            reader=ReaderConfig(**data.get("reader", {})),
            serper_api_key=data.get("serper_api_key"),
        )


# Default configuration instance for when no config is provided
DEFAULT_WEB_CONFIG = WebConfig()
