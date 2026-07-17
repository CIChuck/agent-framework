# mypy: ignore-errors
"""
Code analysis tools.

Ref: docs/reference/specs/tool_specification.md - Category 11: Code Tools - Analyze
"""

from __future__ import annotations

import ast
from typing import Any

from ..definition import BaseTool
from ..sandbox import FilesystemSandbox


class CodeParseAstTool(BaseTool):
    """Parse Python code to AST."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "code_parse_ast"

    @property
    def description(self) -> str:
        return "Parse Python code and return AST structure."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Python file path"},
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        validated = self._sandbox.validate_path(path)

        try:
            code = validated.read_text()
            tree = ast.parse(code)
            return ast.dump(tree, indent=2)
        except SyntaxError as e:
            return f"Syntax error: {e}"
        except Exception as e:
            return f"Error: {e}"


class CodeExtractSymbolsTool(BaseTool):
    """Extract functions and classes from code."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "code_extract_symbols"

    @property
    def description(self) -> str:
        return "Extract function and class definitions from Python code."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Python file path"},
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        validated = self._sandbox.validate_path(path)

        try:
            code = validated.read_text()
            tree = ast.parse(code)

            symbols = {"functions": [], "classes": []}
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    symbols["functions"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    symbols["classes"].append(node.name)

            lines = []
            if symbols["classes"]:
                lines.append(f"Classes: {', '.join(symbols['classes'])}")
            if symbols["functions"]:
                lines.append(f"Functions: {', '.join(symbols['functions'])}")
            return "\n".join(lines) or "(no symbols found)"
        except SyntaxError as e:
            return f"Syntax error: {e}"
        except Exception as e:
            return f"Error: {e}"


code_parse_ast = CodeParseAstTool()
code_extract_symbols = CodeExtractSymbolsTool()
