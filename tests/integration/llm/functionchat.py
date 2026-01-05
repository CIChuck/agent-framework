#!/usr/bin/env python3
"""
Friday-LLM Function Calling Chat CLI.

Demonstrates LLM function calling (tool use) with a date/time tool.
The LLM can call the get_current_datetime function to answer questions
about the current time, date, and day of the week.

Usage:
    python functionchat.py [--config CONFIG_PATH]
"""

import asyncio
import json
import sys
from datetime import datetime
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
║              Friday-LLM Function Calling Demo                ║
║                                                              ║
║  Ask me about the current time, date, or day of the week!   ║
║                                                              ║
║  Type 'exit' or 'quit' to end the conversation.             ║
║  Type 'clear' to reset conversation history.                 ║
╚══════════════════════════════════════════════════════════════╝
""")


# ─────────────────────────────────────────────────────────────────────────────
# Tool Definitions
# ─────────────────────────────────────────────────────────────────────────────

def get_current_datetime() -> dict[str, str]:
    """Get the current date, time, and day of the week."""
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "timezone": datetime.now().astimezone().tzname(),
        "formatted": now.strftime("%A, %B %d, %Y at %I:%M:%S %p"),
    }


# Tool schema for LLM function calling (OpenAI format)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": (
                "Get the current date, time, and day of the week on the local machine. "
                "Use this when the user asks about the current time, date, what day it is, "
                "or any time-related questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }
]


def execute_tool(tool_name: str, arguments: dict[str, Any]) -> str:
    """Execute a tool and return the result as a string."""
    if tool_name == "get_current_datetime":
        result = get_current_datetime()
        return json.dumps(result, indent=2)
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})


# ─────────────────────────────────────────────────────────────────────────────
# Chat Session
# ─────────────────────────────────────────────────────────────────────────────

class FunctionChatSession:
    """Manages a chat session with function calling support."""

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
        self.messages: list[dict[str, Any]] = []

        # Add system message
        if system_prompt:
            self.messages.append({
                "role": "system",
                "content": system_prompt,
            })

    async def send_message(self, user_input: str) -> str | None:
        """Send a message, handle tool calls, and return final response.

        Returns:
            The final response text, or None if an error occurred.
        """
        # Add user message
        self.messages.append({
            "role": "user",
            "content": user_input,
        })

        # Trim history if needed
        self._trim_history()

        try:
            # Initial LLM call (non-streaming to check for tool calls)
            response = await self.llm.chat_completion(
                messages=self.messages,
                tools=TOOLS,
                temperature=self.temperature,
            )

            # Check if LLM wants to call a tool
            if response.tool_calls:
                print("\n🔧 Calling function:", end=" ")

                # Process each tool call
                for tool_call in response.tool_calls:
                    func_name = tool_call.name
                    print(f"{func_name}()")

                    # Execute the tool
                    result = execute_tool(func_name, tool_call.arguments)
                    print(f"📋 Result: {result}")

                    # Add assistant message with tool call
                    self.messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": func_name,
                                    "arguments": json.dumps(tool_call.arguments),
                                },
                            }
                        ],
                    })

                    # Add tool result
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })

                # Get final response with streaming (no tools to avoid another tool call)
                print("\n" + "─" * 60)
                full_response = ""

                async for chunk in self.llm.chat_completion_stream(
                    messages=self.messages,
                    temperature=self.temperature,
                ):
                    print(chunk, end="", flush=True)
                    full_response += chunk

                print("\n" + "─" * 60 + "\n")

                # Add final assistant message
                self.messages.append({
                    "role": "assistant",
                    "content": full_response,
                })

                return full_response

            else:
                # No tool call - just return the response
                content = response.content or ""

                # Add to history
                self.messages.append({
                    "role": "assistant",
                    "content": content,
                })

                print("\n" + "─" * 60)
                print(content)
                print("─" * 60 + "\n")

                return content

        except LLMTimeoutError as e:
            print(f"\n⏱️  Request timed out after {e.timeout_seconds}s")
            print("The LLM is taking too long. Try a shorter message or check the server.")
            # Remove the user message since we didn't get a response
            self.messages.pop()
            return None

        except LLMRetryExhaustedError as e:
            print(f"\n❌ Failed after {e.attempts} attempts")
            print(f"Last error: {type(e.last_error).__name__}: {e.last_error}")
            print("\nThe LLM service is unavailable. Check if the server is running.")
            # Remove the user message since we didn't get a response
            self.messages.pop()
            return None

        except CircuitBreakerOpenError as e:
            print(f"\n🔌 Service temporarily unavailable")
            print(f"Circuit breaker is open. Retry in {e.retry_after:.0f} seconds.")
            # Remove the user message since we didn't get a response
            self.messages.pop()
            return None

    def _trim_history(self) -> None:
        """Trim conversation history to max_history turns."""
        if self.max_history <= 0:
            return

        system_msgs = [m for m in self.messages if m.get("role") == "system"]
        other_msgs = [m for m in self.messages if m.get("role") != "system"]

        # Keep last N messages (rough estimate, tool messages add extra)
        max_msgs = self.max_history * 3
        if len(other_msgs) > max_msgs:
            other_msgs = other_msgs[-max_msgs:]
            self.messages = system_msgs + other_msgs

    def clear_history(self) -> None:
        """Clear conversation history, keeping system prompt."""
        system_msgs = [m for m in self.messages if m.get("role") == "system"]
        self.messages = system_msgs


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

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

    # Custom system prompt for function calling demo
    system_prompt = """You are a helpful assistant with access to a function that can tell you the current date and time.

When the user asks about:
- The current time
- Today's date
- What day of the week it is
- Any time-related questions

You should call the get_current_datetime function to get accurate information, then respond naturally using that data.

For other questions, respond normally without calling any functions."""

    # Display configuration
    print_banner()
    print(f"Model: {llm_config.get('model', 'unknown')}")
    print(f"API Base: {llm_config.get('api_base', 'default')}")
    print("Function calling: enabled (via friday-llm)")
    print("Available tools: get_current_datetime")
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
    session = FunctionChatSession(
        llm=llm,
        system_prompt=system_prompt,
        temperature=llm_config.get("temperature", 0.7),
        max_history=20,
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

            # Send message and handle response
            await session.send_message(user_input)

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nUnexpected error: {type(e).__name__}: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
