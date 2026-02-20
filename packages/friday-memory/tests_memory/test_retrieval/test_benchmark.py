"""
Benchmark tests for retrieval latency.

Tests measure:
- Vector search latency
- Fast inclusion score calculation
- AccessBuffer overhead
- RetrievalFactorComputer performance
- Combined retrieval pipeline timing

Target: <165ms for typical retrieval operations
"""

import asyncio
import statistics
import time
import uuid
from datetime import datetime, timedelta

import pytest
from friday_memory.retrieval.access_buffer import AccessBuffer, AccessBufferConfig
from friday_memory.retrieval.collection_manager import (
    CollectionConfig,
    CollectionManager,
)
from friday_memory.retrieval.factor_computer import (
    RetrievalFactorComputer,
    calculate_inclusion_score_fast,
)
from friday_memory.retrieval.inclusion_scorer import LongTermInclusionScorer


class MockEmbeddingFunction:
    """Mock embedding function for testing."""

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(t)) / 100] * 768 for t in texts]

    async def embed_query(self, text: str) -> list[float]:
        return [float(len(text)) / 100] * 768


def unique_config():
    """Create config with unique collection names for test isolation."""
    suffix = uuid.uuid4().hex[:8]
    return CollectionConfig(
        short_term_collection=f"test_short_{suffix}",
        long_term_collection=f"test_long_{suffix}",
        decayed_collection=f"test_decayed_{suffix}",
    )


def measure_time_ms(func):
    """Decorator to measure function execution time in milliseconds."""

    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return result, elapsed_ms

    return wrapper


class TestFastInclusionScoreBenchmark:
    """Benchmark calculate_inclusion_score_fast function."""

    def test_fast_score_calculation_speed(self):
        """Fast score should compute in microseconds."""
        iterations = 10000
        metadata = {
            "retrieval_factor": 1.2,
            "hit_count": 10,
            "created_at": datetime.now().isoformat(),
        }

        start = time.perf_counter()
        for _ in range(iterations):
            calculate_inclusion_score_fast(0.85, metadata)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Should complete 10K calculations in < 10ms
        avg_us = (elapsed_ms / iterations) * 1000  # Convert to microseconds
        assert elapsed_ms < 10, (
            f"10K calculations took {elapsed_ms:.2f}ms (avg {avg_us:.2f}μs each)"
        )

    def test_fast_vs_full_scorer_speed(self):
        """Compare fast calculation vs full scorer."""
        iterations = 1000
        now = datetime.now()
        metadata = {
            "retrieval_factor": 1.2,
            "hit_count": 10,
            "created_at": (now - timedelta(hours=24)).isoformat(),
        }

        # Fast calculation
        start_fast = time.perf_counter()
        for _ in range(iterations):
            calculate_inclusion_score_fast(0.85, metadata)
        fast_ms = (time.perf_counter() - start_fast) * 1000

        # Full scorer calculation
        scorer = LongTermInclusionScorer()
        start_full = time.perf_counter()
        for _ in range(iterations):
            scorer.calculate_inclusion_score(
                similarity=0.85,
                created_at=now - timedelta(hours=24),
                hit_count=10,
                now=now,
            )
        full_ms = (time.perf_counter() - start_full) * 1000

        # Fast should be significantly faster (at least 5x)
        speedup = full_ms / fast_ms if fast_ms > 0 else float("inf")
        assert speedup > 5, f"Fast only {speedup:.1f}x faster than full scorer"


class TestAccessBufferBenchmark:
    """Benchmark AccessBuffer performance."""

    @pytest.fixture
    def buffer(self):
        """Create access buffer."""
        return AccessBuffer(AccessBufferConfig())

    @pytest.mark.asyncio
    async def test_record_access_latency(self, buffer):
        """Recording access should be fast."""
        iterations = 1000
        timings = []

        for i in range(iterations):
            start = time.perf_counter()
            await buffer.record_access(f"mem_{i}", "long_term")
            elapsed_ms = (time.perf_counter() - start) * 1000
            timings.append(elapsed_ms)

        avg_ms = statistics.mean(timings)
        p99_ms = statistics.quantiles(timings, n=100)[98]

        # Average should be < 0.5ms, p99 < 2ms
        assert avg_ms < 0.5, f"Average record_access latency: {avg_ms:.3f}ms"
        assert p99_ms < 2, f"P99 record_access latency: {p99_ms:.3f}ms"

    @pytest.mark.asyncio
    async def test_concurrent_access_recording(self, buffer):
        """Test concurrent access recording performance."""

        async def record_many(prefix: str, count: int):
            for i in range(count):
                await buffer.record_access(f"{prefix}_{i}", "long_term")

        start = time.perf_counter()
        await asyncio.gather(
            record_many("a", 100),
            record_many("b", 100),
            record_many("c", 100),
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        # 300 concurrent recordings should complete in < 100ms
        assert elapsed_ms < 100, f"300 concurrent recordings took {elapsed_ms:.2f}ms"


class TestVectorSearchBenchmark:
    """Benchmark vector search operations."""

    @pytest.fixture
    def embedding_fn(self):
        """Create mock embedding function."""
        return MockEmbeddingFunction()

    @pytest.fixture
    def collection_manager(self, embedding_fn):
        """Create collection manager."""
        return CollectionManager(
            embedding_function=embedding_fn,
            config=unique_config(),
            path=None,
        )

    @pytest.mark.asyncio
    async def test_empty_collection_search_latency(self, collection_manager):
        """Search on empty collection should be very fast."""
        timings = []
        for _ in range(100):
            start = time.perf_counter()
            await collection_manager.long_term.query(
                query_text="test query",
                n_results=10,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            timings.append(elapsed_ms)

        avg_ms = statistics.mean(timings)
        # Empty search should be < 50ms (includes embedding time)
        assert avg_ms < 50, f"Empty collection search avg: {avg_ms:.2f}ms"

    @pytest.mark.asyncio
    async def test_populated_collection_search_latency(self, collection_manager):
        """Search on populated collection should meet target latency."""
        # Add 100 documents
        now = datetime.now()
        for i in range(100):
            collection_manager.long_term._collection.add(
                ids=[f"doc_{i}"],
                documents=[f"Test document number {i} with some content"],
                embeddings=[[float(i % 10) / 10] * 768],
                metadatas=[
                    {
                        "type": "insight",
                        "stage": "long_term",
                        "created_at": (now - timedelta(hours=i)).isoformat(),
                        "hit_count": i % 20,
                        "retrieval_factor": 1.0 + (i % 10) / 10,
                    }
                ],
            )

        timings = []
        for _ in range(50):
            start = time.perf_counter()
            await collection_manager.long_term.query(
                query_text="test document",
                n_results=10,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            timings.append(elapsed_ms)

        avg_ms = statistics.mean(timings)
        p99_ms = (
            statistics.quantiles(timings, n=100)[98]
            if len(timings) >= 100
            else max(timings)
        )

        # Target: <165ms (includes embedding time)
        assert avg_ms < 100, f"100-doc search avg: {avg_ms:.2f}ms"
        assert p99_ms < 165, f"100-doc search p99: {p99_ms:.2f}ms"


class TestFactorComputerBenchmark:
    """Benchmark RetrievalFactorComputer performance."""

    @pytest.fixture
    def embedding_fn(self):
        """Create mock embedding function."""
        return MockEmbeddingFunction()

    @pytest.fixture
    def collection_manager(self, embedding_fn):
        """Create collection manager."""
        return CollectionManager(
            embedding_function=embedding_fn,
            config=unique_config(),
            path=None,
        )

    @pytest.fixture
    def factor_computer(self):
        """Create factor computer."""
        return RetrievalFactorComputer()

    @pytest.mark.asyncio
    async def test_compute_factors_latency(self, factor_computer, collection_manager):
        """Factor computation should be efficient."""
        now = datetime.now()

        # Add 50 documents
        for i in range(50):
            collection_manager.long_term._collection.add(
                ids=[f"factor_doc_{i}"],
                documents=[f"Document for factor computation {i}"],
                embeddings=[[0.5] * 768],
                metadatas=[
                    {
                        "type": "insight",
                        "stage": "long_term",
                        "created_at": (now - timedelta(hours=i * 2)).isoformat(),
                        "hit_count": i % 10,
                    }
                ],
            )

        timings = []
        for _ in range(10):
            start = time.perf_counter()
            await factor_computer.compute_factors(
                collection_manager.long_term,
                now=now,
                force_update=True,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            timings.append(elapsed_ms)

        avg_ms = statistics.mean(timings)
        # Computing factors for 50 docs should be < 500ms
        assert avg_ms < 500, f"Factor computation for 50 docs avg: {avg_ms:.2f}ms"


class TestEndToEndRetrievalBenchmark:
    """Benchmark complete retrieval pipeline."""

    @pytest.fixture
    def embedding_fn(self):
        """Create mock embedding function."""
        return MockEmbeddingFunction()

    @pytest.fixture
    def collection_manager(self, embedding_fn):
        """Create collection manager."""
        return CollectionManager(
            embedding_function=embedding_fn,
            config=unique_config(),
            path=None,
        )

    @pytest.fixture
    def access_buffer(self):
        """Create access buffer."""
        return AccessBuffer(AccessBufferConfig())

    @pytest.mark.asyncio
    async def test_full_retrieval_pipeline_latency(
        self, collection_manager, access_buffer
    ):
        """Test end-to-end retrieval pipeline meets target latency."""
        now = datetime.now()
        scorer = LongTermInclusionScorer()

        # Setup: Add 100 documents with lifecycle metadata
        for i in range(100):
            collection_manager.long_term._collection.add(
                ids=[f"pipeline_doc_{i}"],
                documents=[f"Pipeline test document {i} about Python"],
                embeddings=[[float(i % 10) / 10] * 768],
                metadatas=[
                    {
                        "type": "insight",
                        "stage": "long_term",
                        "created_at": (now - timedelta(hours=i)).isoformat(),
                        "hit_count": i % 15,
                        "retrieval_factor": 1.0 + (i % 10) / 20,
                        "decay_score": 1.0 - (i % 50) / 100,
                    }
                ],
            )

        # Measure full pipeline
        timings = []
        for _ in range(20):
            start = time.perf_counter()

            # 1. Search both collections (embedding happens internally)
            short_results = await collection_manager.short_term.query(
                query_text="Python programming",
                n_results=10,
            )
            long_results = await collection_manager.long_term.query(
                query_text="Python programming",
                n_results=10,
            )

            # 2. Score and filter results
            all_results = short_results + long_results
            scored_results = scorer.score_and_filter(all_results, now)

            # 3. Record access for top results
            for r in scored_results[:5]:
                await access_buffer.record_access(r["id"], "long_term")

            elapsed_ms = (time.perf_counter() - start) * 1000
            timings.append(elapsed_ms)

        avg_ms = statistics.mean(timings)
        p99_ms = max(timings)

        # Target: <165ms average, <250ms p99 (includes embedding time)
        assert avg_ms < 165, f"Full pipeline avg: {avg_ms:.2f}ms"
        assert p99_ms < 250, f"Full pipeline max: {p99_ms:.2f}ms"

    @pytest.mark.asyncio
    async def test_optimized_vs_unoptimized_retrieval(self, collection_manager):
        """Compare optimized (pre-computed factors) vs unoptimized retrieval."""
        now = datetime.now()

        # Setup: Add documents
        for i in range(50):
            collection_manager.long_term._collection.add(
                ids=[f"opt_doc_{i}"],
                documents=[f"Optimization test document {i}"],
                embeddings=[[float(i % 10) / 10] * 768],
                metadatas=[
                    {
                        "type": "insight",
                        "stage": "long_term",
                        "created_at": (now - timedelta(hours=i)).isoformat(),
                        "hit_count": i % 10,
                        "retrieval_factor": 1.0 + (i % 10) / 20,  # Pre-computed
                    }
                ],
            )

        # Optimized: Use pre-computed retrieval_factor
        optimized_timings = []
        for _ in range(50):
            start = time.perf_counter()
            results = await collection_manager.long_term.query(
                query_text="test document",
                n_results=10,
            )
            for r in results:
                # Fast lookup of pre-computed factor
                r["score"] = calculate_inclusion_score_fast(
                    r["similarity"],
                    r["metadata"],
                )
            elapsed_ms = (time.perf_counter() - start) * 1000
            optimized_timings.append(elapsed_ms)

        # Unoptimized: Calculate factors on-the-fly
        scorer = LongTermInclusionScorer()
        unoptimized_timings = []
        for _ in range(50):
            start = time.perf_counter()
            results = await collection_manager.long_term.query(
                query_text="test document",
                n_results=10,
            )
            # Full scoring calculation
            results = scorer.score_and_filter(results, now)
            elapsed_ms = (time.perf_counter() - start) * 1000
            unoptimized_timings.append(elapsed_ms)

        opt_avg = statistics.mean(optimized_timings)
        unopt_avg = statistics.mean(unoptimized_timings)

        # Optimized should be faster (or at least comparable)
        assert opt_avg <= unopt_avg * 1.5, (
            f"Optimized: {opt_avg:.2f}ms, Unoptimized: {unopt_avg:.2f}ms"
        )
