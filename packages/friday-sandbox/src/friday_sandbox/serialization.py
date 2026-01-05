"""
Serialization utilities for structured return values.

Ref: docs/specs/sandbox_specifications.md - Section 6: Structured Returns

Handles conversion between Python objects and JSON, with special
support for Pydantic models as return types.
"""

from __future__ import annotations

import json
import logging
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


# Code template for capturing structured returns
RETURN_CAPTURE_TEMPLATE = '''
import json
import sys

# User code execution wrapper
__friday_result__ = None
__friday_error__ = None

try:
{indented_code}
except Exception as __e__:
    __friday_error__ = {{
        "type": type(__e__).__name__,
        "message": str(__e__),
    }}

# Write result to stdout with marker
if __friday_error__:
    print("__FRIDAY_RETURN_START__")
    print(json.dumps({{"error": __friday_error__}}))
    print("__FRIDAY_RETURN_END__")
elif __friday_result__ is not None:
    try:
        # Handle Pydantic models
        if hasattr(__friday_result__, "model_dump"):
            result_data = __friday_result__.model_dump()
        elif hasattr(__friday_result__, "dict"):
            result_data = __friday_result__.dict()
        else:
            result_data = __friday_result__
        print("__FRIDAY_RETURN_START__")
        print(json.dumps({{"value": result_data}}))
        print("__FRIDAY_RETURN_END__")
    except (TypeError, ValueError) as __e__:
        print("__FRIDAY_RETURN_START__")
        print(json.dumps({{"error": {{"type": "SerializationError", "message": str(__e__)}}}}))
        print("__FRIDAY_RETURN_END__")
'''

RETURN_MARKER_START = "__FRIDAY_RETURN_START__"
RETURN_MARKER_END = "__FRIDAY_RETURN_END__"


def wrap_code_for_return_capture(code: str) -> str:
    """
    Wrap user code to capture return values.

    The wrapped code will:
    1. Execute the user's code
    2. Capture the value of __friday_result__ if set
    3. Output the result as JSON between markers

    Args:
        code: User's Python code.

    Returns:
        Wrapped code string.

    Example:
        User sets `__friday_result__ = {"key": "value"}` in their code,
        and the wrapper outputs it as JSON for parsing.
    """
    # Indent user code for the try block
    indented_lines = ["    " + line for line in code.split("\n")]
    indented_code = "\n".join(indented_lines)

    return RETURN_CAPTURE_TEMPLATE.format(indented_code=indented_code)


def extract_return_value(stdout: str) -> tuple[str, Any | None, str | None]:
    """
    Extract structured return value from stdout.

    Parses the JSON between FRIDAY_RETURN markers and returns
    the cleaned stdout (with markers removed), the parsed value,
    and the raw JSON string.

    Args:
        stdout: Full stdout from code execution.

    Returns:
        Tuple of (cleaned_stdout, parsed_value, raw_json).
        parsed_value is None if no return value was captured.
        raw_json is the unparsed JSON string.
    """
    start_idx = stdout.find(RETURN_MARKER_START)
    end_idx = stdout.find(RETURN_MARKER_END)

    if start_idx == -1 or end_idx == -1:
        return stdout, None, None

    # Extract the JSON between markers
    json_start = start_idx + len(RETURN_MARKER_START)
    raw_json = stdout[json_start:end_idx].strip()

    # Clean stdout by removing the marker section
    cleaned_stdout = stdout[:start_idx] + stdout[end_idx + len(RETURN_MARKER_END) :]
    cleaned_stdout = cleaned_stdout.strip()

    try:
        data = json.loads(raw_json)
        if "error" in data:
            logger.warning(f"Execution error in user code: {data['error']}")
            return cleaned_stdout, data["error"], raw_json
        return cleaned_stdout, data.get("value"), raw_json
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse return value JSON: {e}")
        return cleaned_stdout, None, raw_json


def validate_return_type(
    value: Any,
    return_type: type[T],
) -> T:
    """
    Validate a return value against a Pydantic model type.

    Args:
        value: The parsed return value (dict or primitive).
        return_type: Pydantic model class to validate against.

    Returns:
        Validated Pydantic model instance.

    Raises:
        ValidationError: If value doesn't match the schema.
        TypeError: If return_type is not a Pydantic model.
    """
    if not isinstance(return_type, type) or not issubclass(return_type, BaseModel):
        raise TypeError(f"return_type must be a Pydantic model, got {return_type}")

    return return_type.model_validate(value)


def serialize_for_sandbox(obj: Any) -> str:
    """
    Serialize an object for passing into the sandbox.

    Args:
        obj: Object to serialize (must be JSON-serializable or Pydantic).

    Returns:
        JSON string representation.

    Raises:
        TypeError: If object is not serializable.
    """
    if isinstance(obj, BaseModel):
        return obj.model_dump_json()

    return json.dumps(obj)


def create_input_code(inputs: dict[str, Any]) -> str:
    """
    Generate Python code to inject input values into the sandbox.

    Args:
        inputs: Dictionary of variable names to values.

    Returns:
        Python code string that defines the input variables.

    Example:
        >>> create_input_code({"x": 42, "name": "test"})
        'x = 42\\nname = "test"'
    """
    lines = []
    for name, value in inputs.items():
        json_value = json.dumps(value)
        lines.append(f"{name} = {json_value}")
    return "\n".join(lines)
