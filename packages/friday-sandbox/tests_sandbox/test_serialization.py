# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Tests for serialization utilities."""

import pytest
from pydantic import BaseModel

from friday_sandbox.serialization import (
    create_input_code,
    extract_return_value,
    serialize_for_sandbox,
    validate_return_type,
    wrap_code_for_return_capture,
)


class TestReturnCapture:
    """Test suite for return value capture."""

    def test_wrap_code_for_return_capture(self):
        """Test code wrapping adds capture logic."""
        code = "x = 1 + 1"
        wrapped = wrap_code_for_return_capture(code)

        assert "__friday_result__" in wrapped
        assert "__FRIDAY_RETURN_START__" in wrapped
        assert "__FRIDAY_RETURN_END__" in wrapped
        assert "x = 1 + 1" in wrapped

    def test_extract_return_value_with_value(self):
        """Test extracting return value from stdout."""
        stdout = 'Some output\n__FRIDAY_RETURN_START__\n{"value": {"key": "test"}}\n__FRIDAY_RETURN_END__\n'  # noqa: E501

        cleaned, value, raw = extract_return_value(stdout)

        assert cleaned == "Some output"
        assert value == {"key": "test"}
        assert raw == '{"value": {"key": "test"}}'

    def test_extract_return_value_without_markers(self):
        """Test extraction when no markers present."""
        stdout = "Just regular output"

        cleaned, value, raw = extract_return_value(stdout)

        assert cleaned == "Just regular output"
        assert value is None
        assert raw is None

    def test_extract_return_value_with_error(self):
        """Test extraction of error result."""
        stdout = '__FRIDAY_RETURN_START__\n{"error": {"type": "ValueError", "message": "bad value"}}\n__FRIDAY_RETURN_END__\n'  # noqa: E501

        cleaned, value, raw = extract_return_value(stdout)

        assert cleaned == ""
        assert value == {"type": "ValueError", "message": "bad value"}

    def test_extract_return_value_with_null(self):
        """Test extraction when result is null."""
        stdout = '__FRIDAY_RETURN_START__\n{"value": null}\n__FRIDAY_RETURN_END__\n'

        cleaned, value, raw = extract_return_value(stdout)

        assert value is None


class TestReturnTypeValidation:
    """Test suite for return type validation."""

    def test_validate_return_type_success(self):
        """Test successful validation with Pydantic model."""

        class ResultModel(BaseModel):
            name: str
            count: int

        value = {"name": "test", "count": 42}
        result = validate_return_type(value, ResultModel)

        assert isinstance(result, ResultModel)
        assert result.name == "test"
        assert result.count == 42

    def test_validate_return_type_failure(self):
        """Test validation failure raises error."""

        class ResultModel(BaseModel):
            name: str
            count: int

        value = {"name": "test"}  # Missing 'count'

        with pytest.raises(Exception):  # ValidationError  # noqa: B017
            validate_return_type(value, ResultModel)

    def test_validate_return_type_non_pydantic(self):
        """Test that non-Pydantic types raise TypeError."""
        with pytest.raises(TypeError):
            validate_return_type({"key": "value"}, dict)


class TestSerialization:
    """Test suite for serialization utilities."""

    def test_serialize_for_sandbox_dict(self):
        """Test serializing a dictionary."""
        data = {"key": "value", "number": 42}
        result = serialize_for_sandbox(data)

        assert '"key": "value"' in result
        assert '"number": 42' in result

    def test_serialize_for_sandbox_pydantic(self):
        """Test serializing a Pydantic model."""

        class TestModel(BaseModel):
            name: str
            value: int

        model = TestModel(name="test", value=123)
        result = serialize_for_sandbox(model)

        assert '"name":"test"' in result or '"name": "test"' in result

    def test_create_input_code(self):
        """Test generating input variable code."""
        inputs = {"x": 42, "name": "test", "data": [1, 2, 3]}
        code = create_input_code(inputs)

        assert "x = 42" in code
        assert 'name = "test"' in code
        assert "data = [1, 2, 3]" in code
