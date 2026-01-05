#!/usr/bin/env python3
"""
Interactive Embedding Test for LiteLLM Embedding Service.

Tests embedding generation with local LM Studio embedder.
Enter text to get embeddings, type 'exit' to quit.
"""

import asyncio
import math
import sys
from pathlib import Path
from typing import Any

import yaml

from friday_llm import LiteLLMEmbeddingService, ResilienceConfig
from friday_llm.exceptions import (
    CircuitBreakerOpenError,
    LLMRetryExhaustedError,
    LLMTimeoutError,
)


def load_config(config_path: Path) -> dict[str, Any]:
    """Load configuration from YAML file."""
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    with open(config_path) as f:
        return yaml.safe_load(f)


def print_embedding_stats(embedding: list[float], text: str) -> None:
    """Print summary statistics for an embedding vector."""
    dimensions = len(embedding)
    norm = math.sqrt(sum(x * x for x in embedding))

    print(f"\n{'='*50}")
    print(f"Input text: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
    print(f"Dimensions: {dimensions}")
    print(f"L2 Norm: {norm:.6f}")
    print(f"First 5 values: {embedding[:5]}")
    print(f"Last 5 values: {embedding[-5:]}")
    print(f"Min: {min(embedding):.6f}, Max: {max(embedding):.6f}")
    print(f"{'='*50}\n")


async def main() -> None:
    """Main entry point."""
    config_path = Path(__file__).parent / "config.yaml"

    # CLI override for config path
    if len(sys.argv) > 1 and sys.argv[1] == "--config":
        config_path = Path(sys.argv[2])

    config = load_config(config_path)
    embedding_config = config.get("embedding", {})

    # Build resilience config
    resilience = ResilienceConfig(
        max_retries=embedding_config.get("max_retries", 3),
        timeout_seconds=embedding_config.get("timeout_seconds", 30.0),
    )

    # Initialize embedding service
    service = LiteLLMEmbeddingService(
        model_name=embedding_config.get("model", "nomic-ai/nomic-embed-text-v1.5"),
        api_key=embedding_config.get("api_key"),
        api_base=embedding_config.get("api_base"),
        resilience=resilience,
    )

    print("\n" + "=" * 50)
    print("Friday Embedding Test")
    print(f"Model: {service.model}")
    print(f"Endpoint: {embedding_config.get('api_base', 'default')}")
    print("Type 'exit' to quit")
    print("=" * 50 + "\n")

    while True:
        try:
            user_input = input("Text to embed: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        try:
            embedding = await service.embed_query(user_input)
            print_embedding_stats(embedding, user_input)
        except LLMTimeoutError as e:
            print(f"\nError: Request timed out - {e}")
        except LLMRetryExhaustedError as e:
            print(f"\nError: All retries failed - {e}")
        except CircuitBreakerOpenError as e:
            print(f"\nError: Circuit breaker open - {e}")
        except Exception as e:
            print(f"\nError: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
