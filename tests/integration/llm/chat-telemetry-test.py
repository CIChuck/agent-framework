#!/usr/bin/env python3
"""
Chat Telemetry Integration Test for Friday-LLM.

This script demonstrates how to use the telemetry features in the friday-llm
package, including:

1. **Basic Telemetry Setup**: How to configure and capture LLM telemetry events
2. **Conversation Context**: Using ConversationContext for request/response pairing
3. **Cost Estimation**: Configuring and using the built-in pricing calculator
4. **Streaming TTFT**: Tracking time-to-first-token in streaming responses
5. **Custom Telemetry Providers**: Implementing your own telemetry backend

Configuration:
    Edit tests/integration/llm/config.yaml to configure:
    - Model name and provider
    - API base URL
    - API key
    - Temperature and other settings

Usage:
    python tests/integration/llm/chat-telemetry-test.py
    python tests/integration/llm/chat-telemetry-test.py --config /path/to/config.yaml

Ref: Batch 3 Specification - Telemetry Enhancement
"""

from __future__ import annotations

import asyncio
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Add the packages to the path for local development
# This allows running the script without installing packages via `uv sync`
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "packages", "friday-llm", "src"
    ),
)
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "packages", "friday-core", "src"
    ),
)

import yaml
from friday_core.telemetry import DebugTelemetryRecorder
from friday_llm import (
    ConversationContext,
    LiteLLMService,
    PricingConfig,
    ResilienceConfig,
)

# =============================================================================
# SECTION 1: Configuration Loading
# =============================================================================


@dataclass
class LLMConfig:
    """
    Configuration for the LLM service.

    This class demonstrates dependency injection - all configuration
    is passed in rather than read from environment variables.

    Attributes:
        model: Model identifier (e.g., 'openai/local-model', 'ollama/llama3.2')
        api_base: Base URL for the API endpoint
        api_key: API key for authentication (can be None for local models)
        temperature: Sampling temperature (0.0-1.0)
        max_retries: Maximum retry attempts for transient errors
    """

    model: str
    api_base: str | None = None
    api_key: str | None = None
    temperature: float = 0.7
    max_retries: int = 3


def load_config(config_path: Path) -> dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        Dictionary containing the parsed configuration

    Raises:
        SystemExit: If the config file is not found
    """
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        print(f"\nExpected config at: {config_path.absolute()}")
        print("\nCreate a config.yaml with the following structure:")
        print("""
llm:
  model: "openai/local-model"
  api_base: "http://localhost:1234/v1"
  api_key: "lm-studio"
  temperature: 0.7
  max_retries: 3
""")
        sys.exit(1)

    with open(config_path) as f:
        return yaml.safe_load(f)


def create_llm_config(config_dict: dict[str, Any]) -> LLMConfig:
    """
    Create an LLMConfig from a configuration dictionary.

    This factory function demonstrates the dependency injection pattern -
    configuration is loaded from a file and injected into the config object,
    rather than being read from environment variables.

    Args:
        config_dict: Dictionary from YAML configuration

    Returns:
        LLMConfig instance with values from the dictionary
    """
    llm_section = config_dict.get("llm", {})
    return LLMConfig(
        model=llm_section.get("model", "openai/local-model"),
        api_base=llm_section.get("api_base"),
        api_key=llm_section.get("api_key"),
        temperature=llm_section.get("temperature", 0.7),
        max_retries=llm_section.get("max_retries", 3),
    )


# =============================================================================
# SECTION 2: Custom Telemetry Provider
# =============================================================================


@dataclass
class ConversationTurn:
    """
    Represents a single turn in a conversation with prompt and response.

    This captures the actual content being sent to and received from the LLM,
    which is useful for:
    - Debugging prompt engineering
    - Auditing conversations
    - Training data collection
    - Quality analysis

    Note: In production, be mindful of privacy implications when logging
    actual conversation content. Consider:
    - PII redaction
    - Data retention policies
    - User consent
    - Encryption at rest
    """

    turn_id: str
    prompt_messages: list[dict[str, str]]
    response_content: str | None = None
    response_model: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0


class DemoTelemetryProvider(DebugTelemetryRecorder):
    """
    A demonstration telemetry provider that extends DebugTelemetryRecorder.

    This class inherits from DebugTelemetryRecorder (defined in friday_core.telemetry)
    which already implements TelemetryInterface. We extend it to add:
    - Console logging of telemetry events (for demo visibility)
    - Conversation turn tracking (prompt/response content capture)

    In production, you would replace this with:
    - OpenTelemetryProvider from friday_core (for distributed tracing)
    - Langfuse client
    - Custom logging/analytics backend
    - Datadog, New Relic, or other APM tools

    The base DebugTelemetryRecorder provides:
    - capture_event(event_name: str, data: dict) -> None
    - start_span(name: str, parent_id: str | None = None) -> str
    - end_span(span_id: str, data: dict | None = None) -> None
    - get_event(name) / get_all_events(name) - for test assertions
    - get_span(id) / get_span_by_name(name) - for test assertions
    - clear() - reset all captured data

    Example using OpenTelemetryProvider for production:
        from friday_core.telemetry import OpenTelemetryProvider

        # With OTLP exporter (production)
        telemetry = OpenTelemetryProvider(
            service_name="friday-agent",
            endpoint="http://localhost:4317"
        )

        # Console exporter (development)
        telemetry = OpenTelemetryProvider(
            service_name="friday-agent"
        )
    """

    def __init__(self) -> None:
        super().__init__()
        self.conversations: list[ConversationTurn] = []
        self._turn_counter = 0

    def capture_event(self, event_name: str, data: dict[str, Any]) -> None:
        """
        Capture a telemetry event with console logging.

        Extends parent to add console output for demonstration purposes.

        Events emitted by friday-llm include:
        - llm_completion_success: Successful chat completion
        - llm_completion_error: Failed chat completion
        - embeddings_generated: Successful embedding generation
        - embeddings_error: Failed embedding generation

        The data dict contains OpenTelemetry GenAI semantic convention attributes:
        - gen_ai.operation.name: "chat" or "embeddings"
        - gen_ai.provider.name: "openai", "anthropic", "ollama", etc.
        - gen_ai.request.model: Requested model name
        - gen_ai.response.model: Actual model used
        - gen_ai.usage.input_tokens: Input token count
        - gen_ai.usage.output_tokens: Output token count
        - friday.cost.usd: Estimated cost in USD
        - friday.streaming.ttft_ms: Time to first token (streaming only)
        """
        super().capture_event(event_name, data)
        print(f"  [TELEMETRY] Event: {event_name}")

    def start_span(self, name: str, parent_id: str | None = None) -> str:
        """
        Start a new trace span with console logging.

        Extends parent to add console output for demonstration purposes.

        Args:
            name: Span name (e.g., "chat gpt-4", "embeddings text-embedding-3-small")
            parent_id: Optional parent span ID for nested spans

        Returns:
            Unique span ID
        """
        span_id = super().start_span(name, parent_id)
        print(f"  [TELEMETRY] Span started: {name} ({span_id})")
        return span_id

    def end_span(self, span_id: str, data: dict[str, Any] | None = None) -> None:
        """
        End a trace span with console logging.

        Extends parent to add console output for demonstration purposes.

        Args:
            span_id: The span ID returned from start_span
            data: Optional attributes/data to add to the span
        """
        span = self.get_span(span_id)
        super().end_span(span_id, data)
        if span and span.duration_ms is not None:
            print(f"  [TELEMETRY] Span ended: {span_id} ({span.duration_ms:.1f}ms)")

    def record_conversation_turn(
        self,
        messages: list[dict[str, str]],
        response_content: str | None = None,
        response_model: str | None = None,
        duration_ms: float = 0.0,
        input_tokens: int = 0,
        output_tokens: int = 0,
    ) -> str:
        """
        Record a conversation turn with prompt and response content.

        This method captures the actual messages sent to the LLM and the
        response received, enabling full conversation tracing.

        Args:
            messages: The prompt messages sent to the LLM
            response_content: The response content from the LLM
            response_model: The model that generated the response
            duration_ms: Time taken for the request
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Unique turn ID for this conversation turn

        Example:
            turn_id = telemetry.record_conversation_turn(
                messages=[
                    {"role": "system", "content": "You are helpful."},
                    {"role": "user", "content": "Hello!"},
                ],
                response_content="Hi there! How can I help?",
                response_model="gpt-4",
                duration_ms=150.5,
                input_tokens=15,
                output_tokens=8,
            )
        """
        self._turn_counter += 1
        turn_id = f"turn-{self._turn_counter}"

        turn = ConversationTurn(
            turn_id=turn_id,
            prompt_messages=messages.copy(),
            response_content=response_content,
            response_model=response_model,
            duration_ms=duration_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        self.conversations.append(turn)

        # Log the turn
        user_msg = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), "N/A"
        )
        preview = user_msg[:50] + "..." if len(user_msg) > 50 else user_msg
        print(f"  [TELEMETRY] Conversation turn recorded: {turn_id}")
        print(f"              Prompt: {preview}")
        if response_content:
            resp_preview = (
                response_content[:50] + "..."
                if len(response_content) > 50
                else response_content
            )
            print(f"              Response: {resp_preview}")

        return turn_id

    def print_summary(self) -> None:
        """Print a summary of captured telemetry."""
        print("\n" + "=" * 60)
        print("TELEMETRY SUMMARY")
        print("=" * 60)

        # Print conversation turns with full prompt/response content
        print(f"\n{'─' * 60}")
        print("CONVERSATION TURNS (Prompt & Response Content)")
        print(f"{'─' * 60}")
        print(f"\nTotal Turns: {len(self.conversations)}")

        for turn in self.conversations:
            print(f"\n  ┌─ {turn.turn_id} ─────────────────────────────────────")
            print(f"  │ Time: {turn.timestamp.isoformat()}")
            print(f"  │ Model: {turn.response_model or 'N/A'}")
            print(f"  │ Duration: {turn.duration_ms:.1f}ms")
            print(f"  │ Tokens: {turn.input_tokens} in / {turn.output_tokens} out")
            print("  │")
            print("  │ PROMPT MESSAGES:")
            for msg in turn.prompt_messages:
                role = msg.get("role", "unknown").upper()
                content = msg.get("content", "")
                # Indent and wrap content
                print(f"  │   [{role}]:")
                for line in content.split("\n"):
                    print(f"  │     {line}")
            print("  │")
            print("  │ RESPONSE:")
            if turn.response_content:
                for line in turn.response_content.split("\n"):
                    print(f"  │   {line}")
            else:
                print("  │   (no response)")
            print(f"  └{'─' * 50}")

        # Print events
        print(f"\n{'─' * 60}")
        print("TELEMETRY EVENTS (Metadata)")
        print(f"{'─' * 60}")
        print(f"\nTotal Events: {len(self.events)}")
        for event in self.events:
            print(f"\n  Event: {event.name}")
            print(f"  Time: {event.timestamp.isoformat()}")
            print("  Data:")
            for key, value in event.data.items():
                print(f"    {key}: {value}")

        # Print spans (using SpanRecord from parent class)
        print(f"\n{'─' * 60}")
        print("TRACE SPANS")
        print(f"{'─' * 60}")
        print(f"\nTotal Spans: {len(self.spans)}")
        for span_id, span in self.spans.items():
            duration = (
                f"{span.duration_ms:.1f}ms" if span.duration_ms is not None else "N/A"
            )
            print(f"\n  Span: {span.name} ({span_id})")
            print(f"  Duration: {duration}")
            if span.data:
                print(f"  Data: {span.data}")


# =============================================================================
# SECTION 3: Service Factory
# =============================================================================


def create_llm_service(
    config: LLMConfig,
    telemetry: DemoTelemetryProvider | None = None,
    pricing_config: PricingConfig | None = None,
) -> LiteLLMService:
    """
    Factory function to create an LLM service with dependency injection.

    This demonstrates the Friday Framework pattern of using factory functions
    with explicit configuration injection rather than environment variables.

    Args:
        config: LLM configuration loaded from YAML
        telemetry: Optional telemetry provider for observability
        pricing_config: Optional pricing configuration for cost tracking

    Returns:
        Configured LiteLLMService instance

    Example:
        # Load config from file
        config_dict = load_config(Path("config.yaml"))
        llm_config = create_llm_config(config_dict)

        # Create telemetry provider
        telemetry = DemoTelemetryProvider()

        # Create service with injected dependencies
        service = create_llm_service(
            config=llm_config,
            telemetry=telemetry,
        )
    """
    # Build resilience configuration
    resilience = ResilienceConfig(
        max_retries=config.max_retries,
        timeout_seconds=30.0,
        stream_timeout_seconds=60.0,
    )

    return LiteLLMService(
        model_name=config.model,
        api_key=config.api_key,
        api_base=config.api_base,
        telemetry=telemetry,
        resilience=resilience,
        pricing_config=pricing_config,
    )


# =============================================================================
# SECTION 4: Demo Functions
# =============================================================================


async def demo_basic_telemetry(
    service: LiteLLMService,
    config: LLMConfig,
    telemetry: DemoTelemetryProvider,
) -> None:
    """
    Demonstrate basic telemetry capture for a chat completion.

    This shows how telemetry events are automatically captured when
    making LLM calls through the service, including prompt and response content.

    Args:
        service: The configured LLM service
        config: LLM configuration for temperature setting
        telemetry: Telemetry provider for recording conversations
    """
    print("\n" + "-" * 60)
    print("DEMO 1: Basic Telemetry Capture")
    print("-" * 60)
    print("\nMaking a simple chat completion request...")

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Be concise."},
        {"role": "user", "content": "What is 2 + 2? Reply with just the number."},
    ]

    import time

    start_time = time.perf_counter()

    response = await service.chat_completion(
        messages=messages,
        temperature=config.temperature,
    )

    duration_ms = (time.perf_counter() - start_time) * 1000

    # Record the conversation turn with prompt and response
    telemetry.record_conversation_turn(
        messages=messages,
        response_content=response.content,
        response_model=response.model,
        duration_ms=duration_ms,
        input_tokens=response.usage.get("prompt_tokens", 0),
        output_tokens=response.usage.get("completion_tokens", 0),
    )

    print(f"\nResponse: {response.content}")
    print(f"Model: {response.model}")
    print(f"Usage: {response.usage}")


async def demo_conversation_context(
    service: LiteLLMService,
    config: LLMConfig,
    telemetry: DemoTelemetryProvider,
) -> None:
    """
    Demonstrate using ConversationContext for request/response pairing.

    ConversationContext allows you to:
    - Track requests within a user session
    - Correlate multiple turns in a conversation
    - Link telemetry to specific conversation threads
    - Enable parent-child span relationships

    This is essential for:
    - Debugging conversation flows
    - Analyzing user sessions
    - Tracking costs per conversation
    - Understanding multi-turn interactions

    Args:
        service: The configured LLM service
        config: LLM configuration for temperature setting
        telemetry: Telemetry provider for recording conversations
    """
    print("\n" + "-" * 60)
    print("DEMO 2: Conversation Context")
    print("-" * 60)

    import time

    # Create a conversation context for tracking
    # In a real app, session_id might come from your auth system
    # conversation_id might be stored in your database
    context = ConversationContext(
        session_id="user-12345",  # Unique user session
        conversation_id="conv-abc-123",  # Conversation thread ID
        turn_id="turn-1",  # Current turn in conversation
        turn_number=1,  # Turn sequence number
        message_count=2,  # Messages in context
    )

    print(f"\nContext: session={context.session_id}, conv={context.conversation_id}")

    messages = [
        {"role": "system", "content": "You are a math tutor. Be concise."},
        {"role": "user", "content": "What is the square root of 16?"},
    ]

    # Pass context to the completion call
    start_time = time.perf_counter()
    response = await service.chat_completion(
        messages=messages,
        temperature=config.temperature,
        conversation_context=context,  # This enables request/response pairing
    )
    duration_ms = (time.perf_counter() - start_time) * 1000

    # Record turn 1 conversation
    telemetry.record_conversation_turn(
        messages=messages,
        response_content=response.content,
        response_model=response.model,
        duration_ms=duration_ms,
        input_tokens=response.usage.get("prompt_tokens", 0),
        output_tokens=response.usage.get("completion_tokens", 0),
    )

    print(f"Turn 1 Response: {response.content}")

    # Simulate a follow-up turn
    context_turn2 = ConversationContext(
        session_id="user-12345",
        conversation_id="conv-abc-123",
        turn_id="turn-2",
        turn_number=2,
        message_count=4,
    )

    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": "And what is that number cubed?"})

    start_time = time.perf_counter()
    response2 = await service.chat_completion(
        messages=messages,
        temperature=config.temperature,
        conversation_context=context_turn2,
    )
    duration_ms = (time.perf_counter() - start_time) * 1000

    # Record turn 2 conversation
    telemetry.record_conversation_turn(
        messages=messages,
        response_content=response2.content,
        response_model=response2.model,
        duration_ms=duration_ms,
        input_tokens=response2.usage.get("prompt_tokens", 0),
        output_tokens=response2.usage.get("completion_tokens", 0),
    )

    print(f"Turn 2 Response: {response2.content}")


async def demo_streaming_ttft(
    service: LiteLLMService,
    config: LLMConfig,
    telemetry: DemoTelemetryProvider,
) -> None:
    """
    Demonstrate streaming with Time-to-First-Token (TTFT) tracking.

    TTFT is a critical metric for user experience in chat applications.
    It measures the time from when the request is sent to when the first
    token of the response is received.

    Lower TTFT = Better perceived responsiveness

    The telemetry captures:
    - time_to_first_token_ms: Time until first token
    - chunk_count: Number of chunks received
    - tokens_per_second: Streaming throughput
    - inter_token_latency_ms: Average time between tokens
    - total_stream_duration_ms: Total streaming time

    Args:
        service: The configured LLM service
        config: LLM configuration for temperature setting
        telemetry: Telemetry provider for recording conversations
    """
    print("\n" + "-" * 60)
    print("DEMO 3: Streaming with TTFT Tracking")
    print("-" * 60)

    import time

    messages = [
        {"role": "system", "content": "You are a storyteller. Be creative but brief."},
        {
            "role": "user",
            "content": "Tell me a very short story about a robot in 2-3 sentences.",
        },
    ]

    print("\nStreaming response:")
    print("-" * 40)

    # Collect the full response while streaming
    response_chunks: list[str] = []
    start_time = time.perf_counter()

    # Stream the response - TTFT is automatically tracked
    async for chunk in service.chat_completion_stream(
        messages=messages,
        temperature=config.temperature,
    ):
        response_chunks.append(chunk)
        print(chunk, end="", flush=True)

    duration_ms = (time.perf_counter() - start_time) * 1000
    full_response = "".join(response_chunks)

    print("\n" + "-" * 40)

    # Record the streaming conversation turn
    # Note: For streaming, we don't have token counts from the response
    telemetry.record_conversation_turn(
        messages=messages,
        response_content=full_response,
        response_model=service.model,  # Use service model since streaming doesn't return it  # noqa: E501
        duration_ms=duration_ms,
        input_tokens=0,  # Not available for streaming
        output_tokens=0,  # Not available for streaming
    )

    print("\n(Check telemetry summary for TTFT metrics and conversation content)")


async def demo_cost_estimation(
    service: LiteLLMService,
    config: LLMConfig,
    telemetry: DemoTelemetryProvider,
) -> None:
    """
    Demonstrate cost estimation capabilities.

    The friday-llm package includes a built-in pricing table with
    costs for popular models (OpenAI, Anthropic, etc.). Costs are
    automatically calculated based on token usage.

    You can also:
    - Override default pricing with custom values
    - Add pricing for custom/fine-tuned models
    - Disable cost estimation if not needed
    - Use fallback pricing for unknown models

    Example custom pricing configuration:
        pricing_config = PricingConfig(
            custom_pricing={
                "my-fine-tuned-model": {
                    "input_cost_per_1k": 0.02,
                    "output_cost_per_1k": 0.04,
                },
                # Override default pricing for a known model
                "gpt-4": {
                    "input_cost_per_1k": 0.025,
                    "output_cost_per_1k": 0.05,
                }
            },
            fallback_input_cost=0.01,
            fallback_output_cost=0.03,
            estimate_unknown=True,
        )

    Args:
        service: The configured LLM service
        config: LLM configuration for temperature setting
        telemetry: Telemetry provider for recording conversations
    """
    print("\n" + "-" * 60)
    print("DEMO 4: Cost Estimation")
    print("-" * 60)

    import time

    messages = [
        {"role": "user", "content": "Write a haiku about programming."},
    ]

    start_time = time.perf_counter()
    response = await service.chat_completion(
        messages=messages,
        temperature=config.temperature,
    )
    duration_ms = (time.perf_counter() - start_time) * 1000

    # Record the conversation turn
    telemetry.record_conversation_turn(
        messages=messages,
        response_content=response.content,
        response_model=response.model,
        duration_ms=duration_ms,
        input_tokens=response.usage.get("prompt_tokens", 0),
        output_tokens=response.usage.get("completion_tokens", 0),
    )

    print(f"\nResponse: {response.content}")
    print("\nToken Usage:")
    print(f"  Input tokens: {response.usage.get('prompt_tokens', 'N/A')}")
    print(f"  Output tokens: {response.usage.get('completion_tokens', 'N/A')}")
    print(f"  Total tokens: {response.usage.get('total_tokens', 'N/A')}")
    print("\n(Check telemetry summary for cost breakdown and conversation content)")


async def demo_error_tracking(config: LLMConfig) -> None:
    """
    Demonstrate error tracking and classification.

    When errors occur, the telemetry system:
    - Classifies errors into categories (timeout, rate_limit, auth, etc.)
    - Records the error type and message
    - Tracks retry attempts
    - Emits llm_completion_error events

    Error categories:
    - TIMEOUT: Request timed out
    - RATE_LIMIT: Rate limit exceeded
    - AUTH_ERROR: Authentication failed
    - INVALID_REQUEST: Bad request parameters
    - MODEL_ERROR: Model-specific error
    - NETWORK_ERROR: Connection issues
    - CIRCUIT_BREAKER: Circuit breaker is open
    - UNKNOWN: Unclassified error

    Args:
        config: LLM configuration (used for model name reference)
    """
    print("\n" + "-" * 60)
    print("DEMO 5: Error Tracking")
    print("-" * 60)

    telemetry = DemoTelemetryProvider()

    # Create a config that will fail (wrong API base)
    # This demonstrates dependency injection - we create a new config
    # with modified values rather than changing environment variables
    error_config = LLMConfig(
        model=config.model,
        api_base="http://localhost:99999",  # Invalid port - will fail
        api_key=config.api_key,
        max_retries=1,  # Minimal retries for faster failure
    )

    # Create service with the error-inducing config
    service = create_llm_service(
        config=error_config,
        telemetry=telemetry,
    )

    print("\nAttempting request to invalid endpoint...")
    print("(This will fail and demonstrate error telemetry)")

    try:
        await service.chat_completion(
            messages=[{"role": "user", "content": "Hello"}],
            timeout=5.0,
        )
    except Exception as e:
        print(f"\nExpected error caught: {type(e).__name__}")
        print(f"Message: {str(e)[:100]}...")

    # Show what error telemetry was captured
    if telemetry.events:
        print("\nError telemetry captured:")
        for event in telemetry.events:
            if "error" in event.name.lower():
                print(f"  Event: {event.name}")
                if "friday.error.category" in event.data:
                    print(f"  Category: {event.data['friday.error.category']}")


# =============================================================================
# SECTION 5: Main Entry Point
# =============================================================================


def print_banner(config: LLMConfig) -> None:
    """Print welcome banner with configuration details."""
    print("=" * 60)
    print("Friday-LLM Telemetry Demonstration")
    print("=" * 60)
    print("\nConfiguration (from config.yaml):")
    print(f"  Model: {config.model}")
    print(f"  API Base: {config.api_base or 'default'}")
    print(f"  API Key: {'***' if config.api_key else 'None'}")
    print(f"  Temperature: {config.temperature}")
    print(f"  Max Retries: {config.max_retries}")


async def main() -> None:
    """
    Main entry point for the telemetry demonstration.

    This function demonstrates the Friday Framework pattern:
    1. Load configuration from YAML file (no environment variables)
    2. Create configuration objects via factory functions
    3. Inject dependencies into service constructors
    4. Run demonstrations with the configured services
    """
    # Determine config path - defaults to config.yaml in the same directory
    if len(sys.argv) > 2 and sys.argv[1] == "--config":
        config_path = Path(sys.argv[2])
    else:
        # Default to the config.yaml in the same folder as this script
        config_path = Path(__file__).parent / "config.yaml"

    # Load configuration from YAML file
    config_dict = load_config(config_path)

    # Create typed configuration object (dependency injection)
    llm_config = create_llm_config(config_dict)

    # Print banner with loaded configuration
    print_banner(llm_config)

    # Create the telemetry provider
    # In production, replace with OpenTelemetry, Langfuse, etc.
    telemetry = DemoTelemetryProvider()

    # Configure custom pricing (optional)
    # This demonstrates how to add/override model pricing
    pricing_config = PricingConfig(
        custom_pricing={
            # Add pricing for local models (they're free but we track "usage")
            "openai/local-model": {
                "input_cost_per_1k": 0.0,
                "output_cost_per_1k": 0.0,
            },
            "ollama/llama3.2": {
                "input_cost_per_1k": 0.0,
                "output_cost_per_1k": 0.0,
            },
        },
        # Estimate costs for unknown models using these defaults
        estimate_unknown=True,
        fallback_input_cost=0.001,
        fallback_output_cost=0.002,
    )

    # Create the LLM service with injected dependencies
    service = create_llm_service(
        config=llm_config,
        telemetry=telemetry,
        pricing_config=pricing_config,
    )

    print("\nService initialized with telemetry enabled")

    try:
        # Run demonstrations - all pass telemetry for prompt/response capture
        await demo_basic_telemetry(service, llm_config, telemetry)
        await demo_conversation_context(service, llm_config, telemetry)
        await demo_streaming_ttft(service, llm_config, telemetry)
        await demo_cost_estimation(service, llm_config, telemetry)
        await demo_error_tracking(llm_config)

    except Exception as e:
        print(f"\nError during demo: {type(e).__name__}: {e}")
        print("\nMake sure you have a local LLM server running:")
        print("  - LM Studio: Start the server on port 1234")
        print("  - Ollama: ollama serve")
        print("\nOr update config.yaml with cloud provider settings.")
        return

    # Print telemetry summary
    telemetry.print_summary()

    print("\n" + "=" * 60)
    print("Demonstration Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
