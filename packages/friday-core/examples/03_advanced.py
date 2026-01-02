"""
Advanced Example: Production Patterns with Logging and Telemetry

This example demonstrates:
- Dependency injection pattern for observability
- Combined logging and telemetry in components
- Configuration-driven environment switching
- Optional telemetry (graceful degradation)
- Simulating a realistic service with full instrumentation
- Test harness pattern for white-box testing

Run with: uv run python packages/friday-core/examples/03_advanced.py
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Any

from friday_core import (
    DebugTelemetryRecorder,
    FridayBaseSettings,
    LoggerProtocol,
    TelemetryInterface,
    get_logger,
)


@dataclass
class RetrievalResult:
    """Result from memory retrieval."""

    query: str
    documents: list[dict[str, Any]]
    latency_ms: float
    source: str


class MemoryService:
    """
    A service demonstrating production-ready observability patterns.

    Key patterns:
    - Telemetry is optional (works without it)
    - Logger is injected for testability
    - Both are used together for comprehensive observability
    """

    def __init__(
        self,
        logger: LoggerProtocol,
        telemetry: TelemetryInterface | None = None,
    ):
        self._logger = logger
        self._telemetry = telemetry

    async def retrieve(self, query: str, limit: int = 5) -> RetrievalResult:
        """
        Retrieve relevant documents from memory.

        Demonstrates:
        - Span wrapping for timing
        - Structured logging with context
        - Event capture for discrete operations
        """
        span_id = None
        if self._telemetry:
            span_id = self._telemetry.start_span("memory_retrieve")
            self._telemetry.capture_event(
                "retrieve_started", {"query": query, "limit": limit}
            )

        self._logger.info("Starting memory retrieval", query=query, limit=limit)

        start_time = time.perf_counter()

        try:
            # Simulate vector search
            await self._vector_search(query)

            # Simulate graph traversal
            await self._graph_lookup(query)

            # Simulate result ranking
            documents = await self._rank_results(query, limit)

            latency_ms = (time.perf_counter() - start_time) * 1000

            self._logger.info(
                "Memory retrieval completed",
                query=query,
                results_count=len(documents),
                latency_ms=round(latency_ms, 2),
            )

            if self._telemetry:
                self._telemetry.capture_event(
                    "retrieve_completed",
                    {
                        "query": query,
                        "results_count": len(documents),
                        "latency_ms": latency_ms,
                    },
                )
                if span_id:
                    self._telemetry.end_span(
                        span_id,
                        {"results": len(documents), "status": "success"},
                    )

            return RetrievalResult(
                query=query,
                documents=documents,
                latency_ms=latency_ms,
                source="combined",
            )

        except Exception as e:
            self._logger.error(
                "Memory retrieval failed",
                query=query,
                error=str(e),
            )

            if self._telemetry:
                self._telemetry.capture_event(
                    "retrieve_failed", {"query": query, "error": str(e)}
                )
                if span_id:
                    self._telemetry.end_span(span_id, {"status": "error", "error": str(e)})

            raise

    async def _vector_search(self, query: str) -> list[dict]:
        """Simulate vector similarity search."""
        span_id = None
        if self._telemetry:
            span_id = self._telemetry.start_span("vector_search")

        self._logger.debug("Executing vector search", query=query[:50])

        # Simulate latency
        await asyncio.sleep(0.02)

        if self._telemetry and span_id:
            self._telemetry.end_span(span_id, {"matches": 10})

        return [{"id": f"vec_{i}", "score": 0.9 - i * 0.1} for i in range(10)]

    async def _graph_lookup(self, query: str) -> list[dict]:
        """Simulate knowledge graph traversal."""
        span_id = None
        if self._telemetry:
            span_id = self._telemetry.start_span("graph_lookup")

        self._logger.debug("Executing graph lookup", query=query[:50])

        # Simulate latency
        await asyncio.sleep(0.015)

        if self._telemetry and span_id:
            self._telemetry.end_span(span_id, {"nodes_visited": 25})

        return [{"id": f"node_{i}", "relevance": 0.85 - i * 0.05} for i in range(5)]

    async def _rank_results(self, query: str, limit: int) -> list[dict]:
        """Simulate result ranking and deduplication."""
        span_id = None
        if self._telemetry:
            span_id = self._telemetry.start_span("rank_results")

        self._logger.debug("Ranking results", limit=limit)

        # Simulate ranking computation
        await asyncio.sleep(0.01)

        results = [
            {"id": f"doc_{i}", "content": f"Document {i} about {query}", "score": 0.95 - i * 0.05}
            for i in range(limit)
        ]

        if self._telemetry and span_id:
            self._telemetry.end_span(span_id, {"final_count": len(results)})

        return results


class ApplicationContext:
    """
    Application context that wires up dependencies.

    Demonstrates configuration-driven setup based on environment.
    """

    def __init__(self, settings: FridayBaseSettings):
        self.settings = settings

        # Configure logger based on environment
        self.logger = get_logger("friday_app", environment=settings.APP_ENV)

        # Telemetry is only enabled in development/testing
        self.telemetry: TelemetryInterface | None = None
        if settings.APP_ENV in ("development", "testing"):
            self.telemetry = DebugTelemetryRecorder()
            self.logger.info("Telemetry enabled", mode="debug_recorder")

    def create_memory_service(self) -> MemoryService:
        """Factory method for creating the memory service."""
        return MemoryService(
            logger=self.logger,
            telemetry=self.telemetry,
        )


async def run_production_simulation():
    """Simulate production usage with logging only."""
    print("=== Production Mode (Logging Only) ===\n")

    # Production settings - telemetry disabled
    settings = FridayBaseSettings(APP_ENV="production")
    ctx = ApplicationContext(settings)

    service = ctx.create_memory_service()

    result = await service.retrieve("What are the best practices for API design?")
    print(f"\nRetrieved {len(result.documents)} documents in {result.latency_ms:.2f}ms\n")


async def run_development_simulation():
    """Simulate development usage with full observability."""
    print("=== Development Mode (Logging + Telemetry) ===\n")

    settings = FridayBaseSettings(APP_ENV="development")
    ctx = ApplicationContext(settings)

    service = ctx.create_memory_service()

    result = await service.retrieve("How do I implement authentication?", limit=3)
    print(f"\nRetrieved {len(result.documents)} documents in {result.latency_ms:.2f}ms")

    # Access telemetry data for debugging
    if ctx.telemetry:
        recorder = ctx.telemetry
        print("\n--- Telemetry Summary ---")
        print(f"Events captured: {len(recorder.events)}")
        print(f"Event types: {set(recorder.event_names)}")
        print(f"Spans recorded: {len(recorder.spans)}")

        # Show span hierarchy
        print("\nSpan timings:")
        for span_id, span in recorder.spans.items():
            if span.duration_ms is not None:
                indent = "  " if span.parent_id else ""
                print(f"{indent}{span.name}: {span.duration_ms:.2f}ms")


async def run_test_harness():
    """Demonstrate white-box testing with telemetry assertions."""
    print("\n=== Test Harness Pattern ===\n")

    # Create a test-specific recorder
    test_recorder = DebugTelemetryRecorder()
    test_logger = get_logger("test", environment="development")

    # Inject test dependencies
    service = MemoryService(logger=test_logger, telemetry=test_recorder)

    # Execute the operation
    result = await service.retrieve("test query", limit=5)

    # White-box assertions on internal behavior
    print("Running assertions on telemetry data...")

    # Assert events were captured
    started_event = test_recorder.get_event("retrieve_started")
    assert started_event is not None, "Should capture retrieve_started event"
    assert started_event["query"] == "test query"
    assert started_event["limit"] == 5

    completed_event = test_recorder.get_event("retrieve_completed")
    assert completed_event is not None, "Should capture retrieve_completed event"
    assert completed_event["results_count"] == 5

    # Assert spans were recorded
    main_span = test_recorder.get_span_by_name("memory_retrieve")
    assert main_span is not None, "Should record main span"
    assert main_span.data["status"] == "success"

    vector_span = test_recorder.get_span_by_name("vector_search")
    assert vector_span is not None, "Should record vector_search span"

    graph_span = test_recorder.get_span_by_name("graph_lookup")
    assert graph_span is not None, "Should record graph_lookup span"

    rank_span = test_recorder.get_span_by_name("rank_results")
    assert rank_span is not None, "Should record rank_results span"

    # Assert timing relationships
    assert main_span.duration_ms >= (
        vector_span.duration_ms + graph_span.duration_ms + rank_span.duration_ms
    ), "Parent span should be >= sum of child spans"

    print("All assertions passed!")
    print(f"\nTotal operation time: {main_span.duration_ms:.2f}ms")
    print(f"  - Vector search: {vector_span.duration_ms:.2f}ms")
    print(f"  - Graph lookup: {graph_span.duration_ms:.2f}ms")
    print(f"  - Ranking: {rank_span.duration_ms:.2f}ms")


async def main():
    await run_production_simulation()
    print("\n" + "=" * 60 + "\n")
    await run_development_simulation()
    print("\n" + "=" * 60 + "\n")
    await run_test_harness()


if __name__ == "__main__":
    asyncio.run(main())
