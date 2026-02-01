"""
Telemetry Configuration.

Settings for telemetry providers, sampling, and export.
"""

from pydantic import BaseModel, Field


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
    service_name: str = Field(
        default="friday", description="Service name for traces"
    )

    # OpenTelemetry settings
    otel_enabled: bool = Field(
        default=False, description="Enable OpenTelemetry export"
    )
    otel_endpoint: str | None = Field(
        default=None, description="OTLP endpoint URL"
    )
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
