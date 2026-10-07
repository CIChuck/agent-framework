"""
Telemetry Configuration.

Settings for telemetry providers, sampling, and export.
"""

import ipaddress
import re
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, model_validator

_SAFE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z", re.ASCII)


def _endpoint_target(endpoint: str) -> tuple[bool, str]:
    """Validate an explicit destination before any transport construction."""
    try:
        if (
            any(ord(c) <= 32 or ord(c) >= 127 for c in endpoint)
            or "?" in endpoint
            or "#" in endpoint
        ):
            raise ValueError
        url = urlsplit(endpoint)
        host = url.hostname
        port = url.port
        if (
            url.scheme not in {"http", "https"}
            or not host
            or port is None
            or not 1 <= port <= 65535
            or url.username is not None
            or url.password is not None
            or url.path
            or url.query
            or url.fragment
            or not endpoint.isascii()
        ):
            raise ValueError
        if url.scheme == "http":
            if not ipaddress.ip_address(host).is_loopback:
                raise ValueError
        elif not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.:-]*", host, re.ASCII):
            raise ValueError
        target = f"[{host}]:{port}" if ":" in host else f"{host}:{port}"
        return url.scheme == "https", target
    except (ValueError, TypeError):
        raise ValueError("invalid_telemetry_destination") from None


class OTelConfig(BaseModel):
    """Strict additive owned OTel settings; no headers or implicit destinations."""

    model_config = ConfigDict(
        extra="forbid", frozen=True, strict=True, hide_input_in_errors=True
    )
    exporter: Literal["console", "otlp_grpc"] = "console"
    service_name: str = "friday"
    endpoint: str | None = None
    queue_limit: int = Field(default=512, ge=1, le=512)
    batch_limit: int = Field(default=128, ge=1, le=128)
    flush_interval_ms: int = Field(default=200, ge=1, le=200)
    request_timeout_ms: int = Field(default=1000, ge=1, le=1000)

    @model_validator(mode="after")
    def _validate_bounds(self) -> "OTelConfig":
        if not _SAFE_NAME.fullmatch(self.service_name):
            raise ValueError("invalid_service_name")
        if self.batch_limit > self.queue_limit:
            raise ValueError("invalid_processing_bounds")
        if self.exporter == "console":
            if self.endpoint is not None:
                raise ValueError("unexpected_telemetry_destination")
        elif self.endpoint is None:
            raise ValueError("missing_telemetry_destination")
        else:
            _endpoint_target(self.endpoint)
        return self


class TelemetryFactoryConfig(BaseModel):
    """Programmatic selection, independent of legacy and Chat configuration."""

    model_config = ConfigDict(
        extra="forbid", frozen=True, strict=True, hide_input_in_errors=True
    )
    provider: Literal["disabled", "debug", "otel"] = "disabled"
    otel: OTelConfig = Field(default_factory=OTelConfig)


class TelemetryConfig(BaseModel):
    """
    Configuration for telemetry collection and export.

    Example:
        config = TelemetryConfig(
            enabled=True,
            service_name="friday-agent",
            otel_endpoint="http://localhost:4317",
            sampling_rate=0.1,  # Sample 10% of traces
        )
    """

    enabled: bool = Field(
        default=True, description="Whether telemetry collection is enabled"
    )
    service_name: str = Field(default="friday", description="Service name for traces")

    # OpenTelemetry settings
    otel_enabled: bool = Field(default=False, description="Enable OpenTelemetry export")
    otel_endpoint: str | None = Field(default=None, description="OTLP endpoint URL")
    otel_headers: dict[str, str] = Field(
        default_factory=dict, description="OTLP request headers"
    )

    # Sampling
    sampling_rate: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Trace sampling rate (0.0-1.0)"
    )
    always_sample_errors: bool = Field(
        default=True, description="Always sample traces with errors"
    )

    # Debug settings
    debug_enabled: bool = Field(
        default=False, description="Enable debug telemetry recorder"
    )
    console_export: bool = Field(
        default=False, description="Export traces to console (development)"
    )

    # Batch settings
    batch_size: int = Field(
        default=512, ge=1, description="Maximum batch size for exports"
    )
    export_interval_ms: int = Field(
        default=5000, ge=100, description="Export interval in milliseconds"
    )

    # Attribute settings
    max_attribute_length: int = Field(
        default=1024, ge=1, description="Maximum attribute value length"
    )
    include_query_text: bool = Field(
        default=False,
        description="Include query text in recall metrics (may be sensitive)",
    )
