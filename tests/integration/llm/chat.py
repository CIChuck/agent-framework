#!/usr/bin/env python3
"""
Friday-LLM Interactive Chat CLI.

A simple command-line chat application that uses the friday-llm package
to interact with various LLM providers (LM Studio, Ollama, OpenAI, Anthropic).

Usage:
    python chat.py [--config CONFIG_PATH]

The chat runs in a loop until the user types 'exit' or 'quit'.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any

import yaml
from friday_llm import (
    CircuitBreakerOpenError,
    LiteLLMService,
    LLMRetryExhaustedError,
    LLMTimeoutError,
    ResilienceConfig,
)


def load_config(config_path: Path) -> dict[str, Any]:
    """Load configuration from YAML file."""
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        return yaml.safe_load(f)


def print_banner() -> None:
    """Print welcome banner."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    Friday-LLM Chat CLI                       ║
║                                                              ║
║  Type your message and press Enter to chat.                  ║
║  Type 'exit' or 'quit' to end the conversation.              ║
║  Type 'clear' to reset conversation history.                 ║
║  Type 'history' to see conversation so far.                  ║
╚══════════════════════════════════════════════════════════════╝
""")


class ChatSession:
    """Manages a multi-turn chat session with an LLM using streaming."""

    def __init__(
        self,
        llm: LiteLLMService,
        system_prompt: str,
        temperature: float = 0.7,
        max_history: int = 20,
    ):
        self.llm = llm
        self.temperature = temperature
        self.max_history = max_history
        self.messages: list[dict[str, str]] = []

        # Add system message
        if system_prompt:
            self.messages.append({
                "role": "system",
                "content": system_prompt,
            })

    async def send_message_streaming(self, user_input: str) -> str | None:
        """Send a message and stream the response to stdout.

        Returns:
            The full response text, or None if an error occurred.
        """
        # Add user message
        self.messages.append({
            "role": "user",
            "content": user_input,
        })

        # Trim history if needed (keep system message + recent turns)
        if self.max_history > 0:
            system_msgs = [m for m in self.messages if m["role"] == "system"]
            other_msgs = [m for m in self.messages if m["role"] != "system"]

            if len(other_msgs) > self.max_history * 2:  # 2 messages per turn
                other_msgs = other_msgs[-(self.max_history * 2):]
                self.messages = system_msgs + other_msgs

        # Print separator and start streaming
        print("\n" + "─" * 60)

        full_response = ""
        try:
            async for chunk in self.llm.chat_completion_stream(
                messages=self.messages,
                temperature=self.temperature,
            ):
                print(chunk, end="", flush=True)
                full_response += chunk

            # Print end separator
            print("\n" + "─" * 60 + "\n")

            # Add assistant message to history
            self.messages.append({
                "role": "assistant",
                "content": full_response,
            })

            return full_response

        except LLMTimeoutError as e:
            print(f"\n\n⏱️  Request timed out after {e.timeout_seconds}s")
            print("The LLM is taking too long. Try a shorter message or check the server.")
            # Remove the user message since we didn't get a response
            self.messages.pop()
            return None

        except LLMRetryExhaustedError as e:
            print(f"\n\n❌ Failed after {e.attempts} attempts")
            print(f"Last error: {type(e.last_error).__name__}: {e.last_error}")
            print("\nThe LLM service is unavailable. Check if the server is running.")
            # Remove the user message since we didn't get a response
            self.messages.pop()
            return None

        except CircuitBreakerOpenError as e:
            print(f"\n\n🔌 Service temporarily unavailable")
            print(f"Circuit breaker is open. Retry in {e.retry_after:.0f} seconds.")
            # Remove the user message since we didn't get a response
            self.messages.pop()
            return None

    def clear_history(self) -> None:
        """Clear conversation history, keeping system prompt."""
        system_msgs = [m for m in self.messages if m["role"] == "system"]
        self.messages = system_msgs

    def get_history(self) -> str:
        """Get formatted conversation history."""
        lines = []
        for msg in self.messages:
            role = msg["role"].upper()
            content = msg["content"]
            if role == "SYSTEM":
                lines.append(f"[SYSTEM]: {content[:100]}...")
            elif role == "USER":
                lines.append(f"\n👤 USER: {content}")
            else:
                lines.append(f"\n🤖 ASSISTANT: {content[:200]}...")
        return "\n".join(lines)


async def main() -> None:
    """Main chat loop."""
    # Determine config path
    if len(sys.argv) > 2 and sys.argv[1] == "--config":
        config_path = Path(sys.argv[2])
    else:
        config_path = Path(__file__).parent / "config.yaml"

    # Load configuration
    config = load_config(config_path)
    llm_config = config.get("llm", {})
    chat_config = config.get("chat", {})

    # Display configuration
    print_banner()
    print(f"Model: {llm_config.get('model', 'unknown')}")
    print(f"API Base: {llm_config.get('api_base', 'default')}")
    print(f"Temperature: {llm_config.get('temperature', 0.7)}")
    print("Streaming: enabled (via friday-llm)")
    print("Resilience: enabled (retry, timeout, circuit breaker)")
    print()

    # Build resilience config from settings
    resilience = ResilienceConfig(
        max_retries=llm_config.get("max_retries", 3),
        timeout_seconds=llm_config.get("timeout_seconds", 30.0),
        stream_timeout_seconds=llm_config.get("stream_timeout_seconds", 60.0),
    )

    # Initialize LLM service using friday-llm
    try:
        llm = LiteLLMService(
            model_name=llm_config.get("model", "openai/local-model"),
            api_key=llm_config.get("api_key"),
            api_base=llm_config.get("api_base"),
            resilience=resilience,
        )
    except Exception as e:
        print(f"Error initializing LiteLLMService: {e}")
        sys.exit(1)

    # Create chat session
    session = ChatSession(
        llm=llm,
        system_prompt=chat_config.get("system_prompt", ""),
        temperature=llm_config.get("temperature", 0.7),
        max_history=chat_config.get("max_history", 20),
    )

    # Main loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            # Handle commands
            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit"):
                print("\nGoodbye!")
                break

            if user_input.lower() == "clear":
                session.clear_history()
                print("\n✓ Conversation history cleared.\n")
                continue

            if user_input.lower() == "history":
                print("\n--- Conversation History ---")
                print(session.get_history())
                print("--- End History ---\n")
                continue

            # Send message and stream response
            await session.send_message_streaming(user_input)

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nUnexpected error: {type(e).__name__}: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
