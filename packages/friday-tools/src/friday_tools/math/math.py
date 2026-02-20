"""Math and date tools."""

from __future__ import annotations

import ast
import operator
from datetime import timedelta
from typing import Any

from dateutil import parser as date_parser

from ..definition import BaseTool

SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def safe_eval(expr):
    def _eval(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return SAFE_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return SAFE_OPS[type(node.op)](_eval(node.operand))
        raise ValueError(f"Unsupported: {node}")

    return _eval(ast.parse(expr, mode="eval").body)


class CalculatorTool(BaseTool):
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Evaluate a math expression."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        }

    async def execute(self, **kwargs: Any) -> str:
        try:
            return str(safe_eval(kwargs["expression"]))
        except Exception as e:
            return f"Error: {e}"


class UnitConvertTool(BaseTool):
    @property
    def name(self) -> str:
        return "unit_convert"

    @property
    def description(self) -> str:
        return "Convert between units."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "value": {"type": "number"},
                "from_unit": {"type": "string"},
                "to_unit": {"type": "string"},
            },
            "required": ["value", "from_unit", "to_unit"],
        }

    async def execute(self, **kwargs: Any) -> str:
        # Simple conversion table
        conversions = {
            ("m", "ft"): 3.28084,
            ("ft", "m"): 0.3048,
            ("km", "mi"): 0.621371,
            ("mi", "km"): 1.60934,
            ("kg", "lb"): 2.20462,
            ("lb", "kg"): 0.453592,
            ("c", "f"): lambda x: x * 9 / 5 + 32,
            ("f", "c"): lambda x: (x - 32) * 5 / 9,
        }
        key = (kwargs["from_unit"].lower(), kwargs["to_unit"].lower())
        if key in conversions:
            conv = conversions[key]
            result = conv(kwargs["value"]) if callable(conv) else kwargs["value"] * conv
            return f"{result:.4f} {kwargs['to_unit']}"
        return f"Unknown conversion: {key}"


class DateParseTool(BaseTool):
    @property
    def name(self) -> str:
        return "date_parse"

    @property
    def description(self) -> str:
        return "Parse a date string."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"date_string": {"type": "string"}},
            "required": ["date_string"],
        }

    async def execute(self, **kwargs: Any) -> str:
        try:
            dt = date_parser.parse(kwargs["date_string"])
            return dt.isoformat()
        except Exception as e:
            return f"Error: {e}"


class DateFormatTool(BaseTool):
    @property
    def name(self) -> str:
        return "date_format"

    @property
    def description(self) -> str:
        return "Format a date."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "date_string": {"type": "string"},
                "format": {"type": "string", "default": "%Y-%m-%d"},
            },
            "required": ["date_string"],
        }

    async def execute(self, **kwargs: Any) -> str:
        try:
            dt = date_parser.parse(kwargs["date_string"])
            return dt.strftime(kwargs.get("format", "%Y-%m-%d"))
        except Exception as e:
            return f"Error: {e}"


class DateCalculateTool(BaseTool):
    @property
    def name(self) -> str:
        return "date_calculate"

    @property
    def description(self) -> str:
        return "Add or subtract time from a date."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "date_string": {"type": "string"},
                "days": {"type": "integer", "default": 0},
                "hours": {"type": "integer", "default": 0},
            },
            "required": ["date_string"],
        }

    async def execute(self, **kwargs: Any) -> str:
        try:
            dt = date_parser.parse(kwargs["date_string"])
            delta = timedelta(days=kwargs.get("days", 0), hours=kwargs.get("hours", 0))
            result = dt + delta
            return result.isoformat()
        except Exception as e:
            return f"Error: {e}"


calculator = CalculatorTool()
unit_convert = UnitConvertTool()
date_parse = DateParseTool()
date_format = DateFormatTool()
date_calculate = DateCalculateTool()
