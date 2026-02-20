"""
LLM turn processing utilities for Friday Chat.

This module contains utilities for processing LLM responses.
The heavy processing methods (_process_with_tools, _process_streaming)
remain on MemoryChatSession due to tight coupling with session state.

This module provides:
- Helper functions for streaming display
- Tool call parsing utilities
"""

import asyncio
import logging
import re
import sys
from typing import Any

logger = logging.getLogger(__name__)


async def display_streaming_response(
    content: str,
    chunk_size: int = 3,
    delay: float = 0.01,
) -> None:
    """
    Display a response with simulated streaming effect.

    Used when we have a complete response from non-streaming API (e.g., after
    tool execution) but want to display it progressively for better UX.

    Args:
        content: The complete response text to display
        chunk_size: Number of characters to output per chunk (default 3)
        delay: Seconds to wait between chunks (default 0.01)
    """
    for i in range(0, len(content), chunk_size):
        chunk = content[i : i + chunk_size]
        sys.stdout.write(chunk)
        sys.stdout.flush()
        if delay > 0:
            await asyncio.sleep(delay)


def parse_text_tool_calls(
    content: str,
    tool_schemas: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Parse text-based tool calls from model responses.

    Some models (like Qwen) output tool calls as text instead of using
    the function calling API. This function parses patterns like:
    - → tool_name(arg1='value1', arg2='value2')
    - tool_name(arg1='value1')

    Args:
        content: The response content to parse
        tool_schemas: Available tool schemas to validate against

    Returns:
        List of parsed tool calls with id, name, and arguments
    """
    if not content or not tool_schemas:
        return []

    parsed_tool_calls = []
    tool_names = {t["function"]["name"] for t in tool_schemas}

    # Match patterns like: → tool_name(arg1='value1', arg2='value2')
    tool_pattern = r"→?\s*(\w+)\(([^)]*)\)"
    matches = re.findall(tool_pattern, content)

    for tool_name, args_str in matches:
        if tool_name in tool_names:
            # Parse arguments from string like: path='/some/path', max_lines=100
            args = {}
            if args_str.strip():
                # Match key=value or key='value' or key="value"
                arg_pattern = r"(\w+)\s*=\s*(?:'([^']*)'|\"([^\"]*)\"|(\S+))"
                for match in re.finditer(arg_pattern, args_str):
                    key = match.group(1)
                    # Value is in group 2 (single quote), 3 (double quote), or 4 (unquoted)  # noqa: E501
                    value = match.group(2) or match.group(3) or match.group(4)
                    args[key] = value

            parsed_tool_calls.append(
                {
                    "id": f"text_parsed_{tool_name}_{len(parsed_tool_calls)}",
                    "name": tool_name,
                    "arguments": args,
                }
            )

    if parsed_tool_calls:
        logger.info(
            f"Parsed {len(parsed_tool_calls)} text-based tool call(s) from model response"  # noqa: E501
        )

    return parsed_tool_calls
