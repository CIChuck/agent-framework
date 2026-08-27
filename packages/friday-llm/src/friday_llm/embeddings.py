"""
LiteLLM Embedding Service.

Wraps litellm.embedding for text embeddings with support for
both cloud and local models.

Ref: Batch 3 Specification, Section 3.2
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
from collections import OrderedDict
from typing import Any

import litellm
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from friday_llm.circuit_breaker import CircuitBreaker
from friday_llm.config import ResilienceConfig
from friday_llm.exceptions import (
    LLMRetryExhaustedError,
    LLMTimeoutError,
)
from friday_llm.pricing import CostCalculator, PricingConfig
from friday_llm.telemetry_helper import LLMTelemetryHelper
from friday_llm.telemetry_models import TokenUsage

logger = logging.getLogger(__name__)


class LiteLLMEmbeddingService:
    """
    Embedding service using LiteLLM.

    Implements the EmbeddingModel protocol with:
    - Multi-provider support (OpenAI, Cohere, Ollama, etc.)
    - Configurable retry logic with exponential backoff
    - Timeout support for all operations
    - Optional circuit breaker for fail-fast behavior
    - Optional batching for large document sets
    - Telemetry integration

    Example:
        # Simple usage with sensible defaults
        service = LiteLLMEmbeddingService()

        # Custom resilience settings
        service = LiteLLMEmbeddingService(
            model_name="text-embedding-3-large",
            resilience=ResilienceConfig(
                max_retries=5,
                timeout_seconds=60.0,
            ),
        )
    """

    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
        api_key: str | None = None,
        api_base: str | None = None,
        batch_size: int = 100,
        telemetry: Any | None = None,
        resilience: ResilienceConfig | None = None,
        pricing_config: PricingConfig | None = None,
        cache_size: int = 100,
    ) -> None:
        """
        Initialize the embedding service.

        Args:
            model_name: Embedding model identifier
                       (e.g., 'text-embedding-3-small', 'ollama/nomic-embed-text')
            api_key: API key for the provider. Not needed for local models.
            api_base: Base URL for API (e.g., 'http://localhost:11434' for Ollama)
            batch_size: Maximum texts per embedding call
            telemetry: Optional TelemetryInterface for observability
            resilience: Configuration for retry, timeout, and circuit breaker
            pricing_config: Configuration for cost estimation
            cache_size: Maximum number of query embeddings to cache (0 to disable)
        """
        self.model = model_name
        self.api_key = api_key
        self.api_base = api_base
        self.batch_size = batch_size
        self.telemetry = telemetry

        # Use defaults if no config provided
        self._resilience = resilience or ResilienceConfig()

        # Initialize circuit breaker
        self._circuit_breaker = CircuitBreaker(
            self._resilience.circuit_breaker,
            model=model_name,
        )

        # Initialize telemetry helper with cost calculator
        self._cost_calculator = CostCalculator(pricing_config)
        self._telemetry_helper = LLMTelemetryHelper(
            telemetry=telemetry,
            cost_calculator=self._cost_calculator,
            provider_name=self._detect_provider(model_name),
        )

        # Query embedding cache (LRU via OrderedDict)
        # Caching at the EmbeddingModel layer benefits ALL vector stores
        self._cache_size = cache_size
        self._embedding_cache: OrderedDict[str, list[float]] = OrderedDict()
        self._cache_hits = 0
        self._cache_misses = 0

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key from text using MD5 hash."""
        return hashlib.md5(text.encode()).hexdigest()

    def _cache_get(self, text: str) -> list[float] | None:
        """Get embedding from cache if present, updating LRU order."""
        if self._cache_size <= 0:
            return None

        cache_key = self._get_cache_key(text)
        if cache_key in self._embedding_cache:
            # Move to end (most recently used)
            self._embedding_cache.move_to_end(cache_key)
            self._cache_hits += 1
            return self._embedding_cache[cache_key]

        self._cache_misses += 1
        return None

    def _cache_put(self, text: str, embedding: list[float]) -> None:
        """Store embedding in cache with LRU eviction."""
        if self._cache_size <= 0:
            return

        cache_key = self._get_cache_key(text)

        # Evict oldest if at capacity
        while len(self._embedding_cache) >= self._cache_size:
            self._embedding_cache.popitem(last=False)

        self._embedding_cache[cache_key] = embedding

    @property
    def cache_stats(self) -> dict[str, int]:
        """Get cache statistics."""
        return {
            "size": len(self._embedding_cache),
            "max_size": self._cache_size,
            "hits": self._cache_hits,
            "misses": self._cache_misses,
        }

    def _detect_provider(self, model: str) -> str:
        """Detect provider from model name."""
        model_lower = model.lower()
        if "openai" in model_lower or model_lower.startswith("text-embedding"):
            return "openai"
        if "cohere" in model_lower or model_lower.startswith("embed-"):
            return "cohere"
        if "ollama" in model_lower:
            return "ollama"
        if "bedrock" in model_lower:
            return "aws.bedrock"
        return "litellm"

    @property
    def resilience(self) -> ResilienceConfig:
        """Get current resilience configuration."""
        return self._resilience

    def _emit_event(self, event_name: str, data: dict[str, Any]) -> None:
        """Emit telemetry event if configured."""
        if self.telemetry:
            self.telemetry.capture_event(event_name, data)

    async def embed_documents(
        self,
        texts: list[str],
        timeout: float | None = None,
    ) -> list[list[float]]:
        """
        Embed multiple documents for indexing.

        Handles batching automatically if the number of texts
        exceeds batch_size.

        Args:
            texts: List of text strings to embed
            timeout: Override default timeout for this call

        Returns:
            List of embedding vectors (one per input text)

        Raises:
            LLMTimeoutError: If the call times out
            LLMRetryExhaustedError: If max retries exceeded
            CircuitBreakerOpenError: If circuit breaker is open
        """
        if not texts:
            return []

        effective_timeout = timeout or self._resilience.timeout_seconds
        total_characters = sum(len(t) for t in texts)
        batch_count = (len(texts) + self.batch_size - 1) // self.batch_size

        with self._telemetry_helper.track_embedding(
            model=self.model,
            text_count=len(texts),
            total_characters=total_characters,
        ) as tracker:
            try:
                all_embeddings: list[list[float]] = []
                total_tokens = 0

                # Process in batches
                for i in range(0, len(texts), self.batch_size):
                    batch = texts[i : i + self.batch_size]
                    embeddings, usage = await self._embed_batch_with_retry(
                        batch,
                        timeout=effective_timeout,
                    )
                    all_embeddings.extend(embeddings)
                    total_tokens += usage.input_tokens

                # Get embedding dimensions from first result
                embedding_dims = len(all_embeddings[0]) if all_embeddings else None

                # Record response details for telemetry
                tracker.set_response(
                    response_model=self.model,
                    usage=TokenUsage(
                        input_tokens=total_tokens, total_tokens=total_tokens
                    ),
                    embedding_dimensions=embedding_dims,
                    batch_count=batch_count,
                )

                return all_embeddings

            except LLMRetryExhaustedError as e:
                tracker.set_retry_info(e.attempts, e.attempts)
                raise

            except LLMTimeoutError:
                raise

    async def embed_query(
        self,
        text: str,
        timeout: float | None = None,
    ) -> list[float]:
        """
        Embed a single query for search.

        Uses LRU cache to avoid redundant embedding calls for repeated queries.
        Cache is implemented at the EmbeddingModel layer so all vector stores
        (Chroma, Pinecone, Qdrant) benefit automatically.

        Args:
            text: Query text to embed
            timeout: Override default timeout for this call

        Returns:
            Single embedding vector

        Raises:
            LLMTimeoutError: If the call times out
            LLMRetryExhaustedError: If max retries exceeded
            CircuitBreakerOpenError: If circuit breaker is open
        """
        # Check cache first
        cached = self._cache_get(text)
        if cached is not None:
            logger.debug(
                f"Embedding cache hit for query (cache stats: {self.cache_stats})"
            )
            return cached

        effective_timeout = timeout or self._resilience.timeout_seconds

        with self._telemetry_helper.track_embedding(
            model=self.model,
            text_count=1,
            total_characters=len(text),
        ) as tracker:
            try:
                embeddings, usage = await self._embed_batch_with_retry(
                    [text],
                    timeout=effective_timeout,
                )

                # Get embedding dimensions
                embedding_dims = len(embeddings[0]) if embeddings else None

                # Record response details for telemetry
                tracker.set_response(
                    response_model=self.model,
                    usage=usage,
                    embedding_dimensions=embedding_dims,
                    batch_count=1,
                )

                # Cache the result
                result = embeddings[0]
                self._cache_put(text, result)

                return result

            except LLMRetryExhaustedError as e:
                tracker.set_retry_info(e.attempts, e.attempts)
                raise

            except LLMTimeoutError:
                raise

    async def _embed_batch_with_retry(
        self,
        texts: list[str],
        timeout: float,
    ) -> tuple[list[list[float]], TokenUsage]:
        """Execute embedding call with retry logic, timeout, and circuit breaker.

        Returns:
            Tuple of (embeddings, token_usage)
        """
        retry_exceptions = self._resilience.get_retry_exceptions()
        attempts = 0

        @retry(
            retry=retry_if_exception_type(retry_exceptions),
            stop=stop_after_attempt(self._resilience.max_retries + 1),
            wait=wait_exponential(
                multiplier=self._resilience.backoff_multiplier,
                min=self._resilience.backoff_min,
                max=self._resilience.backoff_max,
            ),
            reraise=False,
        )
        async def _call() -> tuple[list[list[float]], TokenUsage]:
            nonlocal attempts
            attempts += 1

            kwargs: dict[str, Any] = {
                "model": self.model,
                "input": texts,
            }

            if self.api_key:
                kwargs["api_key"] = self.api_key

            if self.api_base:
                kwargs["api_base"] = self.api_base

            try:
                response = await asyncio.wait_for(
                    litellm.aembedding(**kwargs),
                    timeout=timeout,
                )
            except asyncio.TimeoutError as e:
                raise LLMTimeoutError(
                    f"Embedding call timed out after {timeout}s",
                    timeout_seconds=timeout,
                    operation="embedding",
                    model=self.model,
                ) from e

            # Extract embeddings from response
            embeddings = [item["embedding"] for item in response.data]

            # Extract token usage
            usage = TokenUsage()
            if hasattr(response, "usage") and response.usage:
                usage = TokenUsage(
                    input_tokens=getattr(response.usage, "prompt_tokens", 0)
                    or getattr(response.usage, "total_tokens", 0),
                    total_tokens=getattr(response.usage, "total_tokens", 0),
                )

            return embeddings, usage

        try:
            return await self._circuit_breaker.call(_call)
        except RetryError as e:
            candidate = e.last_attempt.exception() if e.last_attempt else e
            last_error = (
                candidate
                if isinstance(candidate, Exception)
                else RuntimeError("embedding retry failed without an Exception")
            )
            raise LLMRetryExhaustedError(
                f"Embedding call failed after {attempts} attempts",
                attempts=attempts,
                last_error=last_error,
                model=self.model,
            ) from e
