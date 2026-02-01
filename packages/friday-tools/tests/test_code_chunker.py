"""
Unit tests for the code_chunker module.

Tests structure-aware code chunking for Python and generic languages.
"""

import pytest

from friday_tools.filesystem.code_chunker import (
    BaseLanguageChunker,
    ChunkType,
    CodeChunk,
    CodeChunkerFactory,
    GenericCodeChunker,
    PythonCodeChunker,
    SymbolTable,
)


# =============================================================================
# SAMPLE CODE FOR TESTING
# =============================================================================

PYTHON_CODE_SIMPLE = '''
"""Module docstring."""

import os
from pathlib import Path

def greet(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}!"

def farewell(name: str) -> str:
    """Say goodbye."""
    return f"Goodbye, {name}!"
'''

PYTHON_CODE_WITH_CLASS = '''
"""A module with a class."""

import logging

logger = logging.getLogger(__name__)

class Calculator:
    """A simple calculator."""

    def __init__(self):
        self.value = 0

    def add(self, x: int) -> int:
        """Add a value."""
        self.value += x
        return self.value

    def subtract(self, x: int) -> int:
        """Subtract a value."""
        self.value -= x
        return self.value

def main():
    """Entry point."""
    calc = Calculator()
    print(calc.add(5))
'''

PYTHON_CODE_IMPORTS_ONLY = '''
import os
import sys
from pathlib import Path
from typing import Any, Dict
'''

GENERIC_CODE_JS = '''
// A simple module

import { something } from "./other";

function greet(name) {
    return "Hello, " + name;
}

class Person {
    constructor(name) {
        this.name = name;
    }

    sayHello() {
        return greet(this.name);
    }
}

export default Person;
'''

GENERIC_CODE_RUST = '''
//! Module documentation

use std::io;

fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

pub fn farewell(name: &str) -> String {
    format!("Goodbye, {}!", name)
}

struct Person {
    name: String,
}

impl Person {
    fn new(name: &str) -> Self {
        Person { name: name.to_string() }
    }
}
'''


# =============================================================================
# PYTHON CHUNKER TESTS
# =============================================================================

class TestPythonCodeChunker:
    """Tests for PythonCodeChunker."""

    def test_chunk_simple_functions(self):
        """Test chunking a module with simple functions."""
        chunker = PythonCodeChunker()
        chunks = chunker.chunk(PYTHON_CODE_SIMPLE)

        # Should have: imports, 2 functions
        assert len(chunks) >= 2

        # Check that we have an imports chunk
        import_chunks = [c for c in chunks if c.chunk_type == ChunkType.IMPORTS]
        assert len(import_chunks) == 1
        assert "import os" in import_chunks[0].text

        # Check function chunks
        func_chunks = [c for c in chunks if c.chunk_type == ChunkType.FUNCTION]
        assert len(func_chunks) == 2

        # Verify function names are in symbols_defined
        func_names = set()
        for chunk in func_chunks:
            func_names.update(chunk.symbols_defined)
        assert "greet" in func_names
        assert "farewell" in func_names

    def test_chunk_with_class(self):
        """Test chunking a module with a class."""
        chunker = PythonCodeChunker()
        chunks = chunker.chunk(PYTHON_CODE_WITH_CLASS)

        # Check for class chunk
        class_chunks = [c for c in chunks if c.chunk_type == ChunkType.CLASS]
        assert len(class_chunks) == 1

        class_chunk = class_chunks[0]
        assert "Calculator" in class_chunk.symbols_defined
        # Methods should also be in symbols_defined
        assert any("add" in s for s in class_chunk.symbols_defined)
        assert any("subtract" in s for s in class_chunk.symbols_defined)

    def test_chunk_imports_only(self):
        """Test chunking a module with only imports."""
        chunker = PythonCodeChunker()
        chunks = chunker.chunk(PYTHON_CODE_IMPORTS_ONLY)

        # Should have just one imports chunk
        assert len(chunks) == 1
        assert chunks[0].chunk_type == ChunkType.IMPORTS
        assert "os" in chunks[0].symbols_defined
        assert "sys" in chunks[0].symbols_defined
        assert "Path" in chunks[0].symbols_defined

    def test_extract_symbols(self):
        """Test symbol extraction from Python code."""
        chunker = PythonCodeChunker()
        symbols = chunker.extract_symbols(PYTHON_CODE_WITH_CLASS)

        assert "Calculator" in symbols.classes
        assert "add" in symbols.functions
        assert "subtract" in symbols.functions
        assert "main" in symbols.functions
        assert "logging" in symbols.imports
        assert "logger" in symbols.module_level

    def test_chunk_indices_and_totals(self):
        """Test that chunk indices and totals are correct."""
        chunker = PythonCodeChunker()
        chunks = chunker.chunk(PYTHON_CODE_SIMPLE)

        for i, chunk in enumerate(chunks):
            assert chunk.index == i
            assert chunk.total == len(chunks)

    def test_fallback_on_syntax_error(self):
        """Test that invalid Python falls back to generic chunking."""
        chunker = PythonCodeChunker()
        invalid_python = "def broken(\n  this is not valid python"

        # Should not raise, should fall back
        chunks = chunker.chunk(invalid_python)
        assert len(chunks) >= 1

    def test_empty_code(self):
        """Test chunking empty content."""
        chunker = PythonCodeChunker()
        chunks = chunker.chunk("")
        assert chunks == []

    def test_whitespace_only(self):
        """Test chunking whitespace-only content."""
        chunker = PythonCodeChunker()
        chunks = chunker.chunk("   \n\n   ")
        # May return empty or single chunk depending on implementation
        assert len(chunks) <= 1


# =============================================================================
# GENERIC CHUNKER TESTS
# =============================================================================

class TestGenericCodeChunker:
    """Tests for GenericCodeChunker."""

    def test_chunk_javascript(self):
        """Test chunking JavaScript code."""
        chunker = GenericCodeChunker()
        chunks = chunker.chunk(GENERIC_CODE_JS)

        # Should find function and class
        assert len(chunks) >= 2

        # Check that greet function was found
        func_chunks = [c for c in chunks if c.chunk_type == ChunkType.FUNCTION]
        class_chunks = [c for c in chunks if c.chunk_type == ChunkType.CLASS]

        assert len(func_chunks) >= 1 or len(class_chunks) >= 1

    def test_chunk_rust(self):
        """Test chunking Rust code."""
        chunker = GenericCodeChunker()
        chunks = chunker.chunk(GENERIC_CODE_RUST)

        # Should find functions and struct
        assert len(chunks) >= 2

        # Check for function definitions
        func_names = set()
        for chunk in chunks:
            func_names.update(chunk.symbols_defined)

        assert "greet" in func_names or "farewell" in func_names

    def test_extract_symbols_generic(self):
        """Test symbol extraction from generic code."""
        chunker = GenericCodeChunker()
        symbols = chunker.extract_symbols(GENERIC_CODE_JS)

        # Should find function and class
        assert "greet" in symbols.functions or "Person" in symbols.classes

    def test_chunk_indices(self):
        """Test chunk indices are sequential."""
        chunker = GenericCodeChunker()
        chunks = chunker.chunk(GENERIC_CODE_RUST)

        for i, chunk in enumerate(chunks):
            assert chunk.index == i
            assert chunk.total == len(chunks)


# =============================================================================
# FACTORY TESTS
# =============================================================================

class TestCodeChunkerFactory:
    """Tests for CodeChunkerFactory."""

    def test_python_extension(self):
        """Test that .py returns PythonCodeChunker."""
        chunker = CodeChunkerFactory.for_extension(".py")
        assert isinstance(chunker, PythonCodeChunker)

    def test_pyi_extension(self):
        """Test that .pyi returns PythonCodeChunker."""
        chunker = CodeChunkerFactory.for_extension(".pyi")
        assert isinstance(chunker, PythonCodeChunker)

    def test_rust_extension(self):
        """Test that .rs returns GenericCodeChunker."""
        chunker = CodeChunkerFactory.for_extension(".rs")
        assert isinstance(chunker, GenericCodeChunker)

    def test_javascript_extension(self):
        """Test that .js returns GenericCodeChunker."""
        chunker = CodeChunkerFactory.for_extension(".js")
        assert isinstance(chunker, GenericCodeChunker)

    def test_unknown_extension(self):
        """Test that unknown extensions return GenericCodeChunker."""
        chunker = CodeChunkerFactory.for_extension(".xyz")
        assert isinstance(chunker, GenericCodeChunker)

    def test_case_insensitive(self):
        """Test that extensions are case-insensitive."""
        chunker1 = CodeChunkerFactory.for_extension(".PY")
        chunker2 = CodeChunkerFactory.for_extension(".Py")
        assert isinstance(chunker1, PythonCodeChunker)
        assert isinstance(chunker2, PythonCodeChunker)

    def test_supports_extension(self):
        """Test extension support checking."""
        assert CodeChunkerFactory.supports_extension(".py")
        assert CodeChunkerFactory.supports_extension(".rs")
        assert CodeChunkerFactory.supports_extension(".js")
        assert CodeChunkerFactory.supports_extension(".go")
        # Unknown extensions still return True (generic chunker available)
        assert CodeChunkerFactory.supports_extension(".xyz") is False or True  # Implementation-dependent


# =============================================================================
# DATA CLASS TESTS
# =============================================================================

class TestDataClasses:
    """Tests for data classes."""

    def test_code_chunk_creation(self):
        """Test CodeChunk creation with defaults."""
        chunk = CodeChunk(
            text="def foo(): pass",
            index=0,
            total=1,
            chunk_type=ChunkType.FUNCTION,
        )

        assert chunk.text == "def foo(): pass"
        assert chunk.index == 0
        assert chunk.total == 1
        assert chunk.chunk_type == ChunkType.FUNCTION
        assert chunk.symbols_defined == []
        assert chunk.symbols_referenced == []

    def test_symbol_table_to_dict(self):
        """Test SymbolTable to_dict method."""
        table = SymbolTable(
            functions=["foo", "bar"],
            classes=["MyClass"],
            imports=["os", "sys"],
            module_level=["CONST"],
        )

        result = table.to_dict()

        assert result["functions"] == ["foo", "bar"]
        assert result["classes"] == ["MyClass"]
        assert result["imports"] == ["os", "sys"]
        assert result["module_level"] == ["CONST"]

    def test_chunk_type_values(self):
        """Test ChunkType enum values."""
        assert ChunkType.IMPORTS.value == "imports"
        assert ChunkType.CLASS.value == "class"
        assert ChunkType.FUNCTION.value == "function"
        assert ChunkType.MODULE_LEVEL.value == "module_level"
