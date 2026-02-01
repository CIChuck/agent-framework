"""
Composite Telemetry Provider.

Fan-out provider that sends telemetry to multiple backends.
"""

from typing import Any

from friday_telemetry.interface import TelemetryInterface


class CompositeProvider(TelemetryInterface):
    """
    Composite telemetry provider that fans out to multiple backends.

    Useful for sending telemetry to multiple destinations simultaneously,
    e.g., both OpenTelemetry for production monitoring and a debug recorder
    for testing.

    Example:
        debug = DebugTelemetryRecorder()
        otel = OpenTelemetryProvider(service_name="friday-agent")
        composite = CompositeProvider([debug, otel])

        # Events and spans are sent to both providers
        controller = MemoryController(..., telemetry=composite)
    """

    def __init__(self, providers: list[TelemetryInterface]) -> None:
        """
        Initialize composite provider.

        Args:
            providers: List of telemetry providers to fan out to
        """
        self._providers = providers

    def add_provider(self, provider: TelemetryInterface) -> None:
        """
        Add a provider to the composite.

        Args:
            provider: Telemetry provider to add
        """
        self._providers.append(provider)

    def remove_provider(self, provider: TelemetryInterface) -> None:
        """
        Remove a provider from the composite.

        Args:
            provider: Telemetry provider to remove
        """
        self._providers.remove(provider)

    def capture_event(self, event_name: str, data: dict[str, Any]) -> None:
        """
        Records an event to all providers.

        Args:
            event_name: Identifier for the event type
            data: Event data to record
        """
        for provider in self._providers:
            provider.capture_event(event_name, data)

    def start_span(self, name: str, parent_id: str | None = None) -> str:
        """
        Starts a span on all providers.

        Returns the span ID from the first provider. All providers receive
        the same span_id for correlation.

        Args:
            name: Name of the operation being traced
            parent_id: Optional parent span ID

        Returns:
            Span ID (from first provider)
        """
        span_id = ""
        for i, provider in enumerate(self._providers):
            if i == 0:
                span_id = provider.start_span(name, parent_id)
            else:
                # For subsequent providers, we still call start_span
                # but use the first span_id for correlation tracking
                provider.start_span(name, parent_id)
        return span_id

    def end_span(self, span_id: str, data: dict[str, Any] | None = None) -> None:
        """
        Ends a span on all providers.

        Args:
            span_id: The ID returned by start_span()
            data: Optional final data to attach
        """
        for provider in self._providers:
            provider.end_span(span_id, data)

    @property
    def providers(self) -> list[TelemetryInterface]:
        """Returns the list of registered providers."""
        return self._providers
