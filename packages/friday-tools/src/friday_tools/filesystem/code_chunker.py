"""
Structure-Aware Code Chunker.

Splits source code into semantically coherent chunks at function/class boundaries
using language-specific parsing. Falls back to regex-based chunking for
unsupported languages.

Ref: docs/build-plan/large-file-processor-plan.md
"""

from __future__ import annotations

import ast
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class ChunkType(str, Enum):
    """Types of code chunks."""

    IMPORTS = "imports"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    MODULE_LEVEL = "module_level"
    UNKNOWN = "unknown"


@dataclass
class CodeChunk:
    """A chunk of code with structural metadata."""

    text: str
    index: int
    total: int
    chunk_type: ChunkType
    symbols_defined: list[str] = field(default_factory=list)
    symbols_referenced: list[str] = field(default_factory=list)
    start_line: int | None = None
    end_line: int | None = None
    docstring: str | None = None


@dataclass
class SymbolTable:
    """Extracted symbols from a code file."""

    functions: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    module_level: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, list[str]]:
        """Convert to dictionary for serialization."""
        return {
            "functions": self.functions,
            "classes": self.classes,
            "imports": self.imports,
            "module_level": self.module_level,
        }


class BaseLanguageChunker(ABC):
    """Abstract base class for language-specific code chunkers."""

    @abstractmethod
    def chunk(self, content: str) -> list[CodeChunk]:
        """
        Split code content into structural chunks.

        Args:
            content: Source code text

        Returns:
            List of CodeChunk objects
        """
        pass

    @abstractmethod
    def extract_symbols(self, content: str) -> SymbolTable:
        """
        Extract symbol definitions from code.

        Args:
            content: Source code text

        Returns:
            SymbolTable with all extracted symbols
        """
        pass


class PythonCodeChunker(BaseLanguageChunker):
    """
    Structure-aware chunker for Python code using AST.

    Respects function, class, and import boundaries to create
    semantically meaningful chunks.
    """

    def __init__(self, max_chunk_lines: int = 100) -> None:
        """
        Initialize Python chunker.

        Args:
            max_chunk_lines: Maximum lines per chunk (large functions get split)
        """
        self._max_chunk_lines = max_chunk_lines

    def chunk(self, content: str) -> list[CodeChunk]:
        """
        Split Python code into structural chunks.

        Algorithm:
        1. Parse AST to identify top-level definitions
        2. Extract imports as first chunk
        3. Extract classes (with methods grouped)
        4. Extract standalone functions
        5. Extract module-level code

        Args:
            content: Python source code

        Returns:
            List of CodeChunk objects
        """
        try:
            tree = ast.parse(content)
        except SyntaxError:
            # Fall back to generic chunking on parse error
            return self._fallback_chunk(content)

        lines = content.splitlines(keepends=True)
        chunks: list[CodeChunk] = []

        # Track which lines belong to which structures
        import_nodes: list[ast.AST] = []
        class_nodes: list[ast.ClassDef] = []
        function_nodes: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
        other_nodes: list[ast.AST] = []

        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_nodes.append(node)
            elif isinstance(node, ast.ClassDef):
                class_nodes.append(node)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_nodes.append(node)
            else:
                other_nodes.append(node)

        # Chunk 1: Imports
        if import_nodes:
            import_lines = self._get_node_lines(import_nodes, lines)
            import_text = "".join(import_lines)
            symbols = self._extract_import_symbols(import_nodes)
            chunks.append(
                CodeChunk(
                    text=import_text,
                    index=0,
                    total=0,  # Updated later
                    chunk_type=ChunkType.IMPORTS,
                    symbols_defined=symbols,
                    start_line=import_nodes[0].lineno,
                    end_line=import_nodes[-1].end_lineno,
                )
            )

        # Chunk for each class
        for class_node in class_nodes:
            class_text = self._get_node_text(class_node, lines)
            symbols_defined = [class_node.name]
            symbols_referenced = self._extract_references(class_node)
            docstring = ast.get_docstring(class_node)

            # Add method names to symbols_defined
            for item in class_node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols_defined.append(f"{class_node.name}.{item.name}")

            chunks.append(
                CodeChunk(
                    text=class_text,
                    index=0,
                    total=0,
                    chunk_type=ChunkType.CLASS,
                    symbols_defined=symbols_defined,
                    symbols_referenced=symbols_referenced,
                    start_line=class_node.lineno,
                    end_line=class_node.end_lineno,
                    docstring=docstring,
                )
            )

        # Chunk for each function
        for func_node in function_nodes:
            func_text = self._get_node_text(func_node, lines)
            symbols_referenced = self._extract_references(func_node)
            docstring = ast.get_docstring(func_node)

            chunks.append(
                CodeChunk(
                    text=func_text,
                    index=0,
                    total=0,
                    chunk_type=ChunkType.FUNCTION,
                    symbols_defined=[func_node.name],
                    symbols_referenced=symbols_referenced,
                    start_line=func_node.lineno,
                    end_line=func_node.end_lineno,
                    docstring=docstring,
                )
            )

        # Chunk for module-level code
        if other_nodes:
            module_lines = self._get_node_lines(other_nodes, lines)
            module_text = "".join(module_lines)
            symbols_defined = []
            for node in other_nodes:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            symbols_defined.append(target.id)

            chunks.append(
                CodeChunk(
                    text=module_text,
                    index=0,
                    total=0,
                    chunk_type=ChunkType.MODULE_LEVEL,
                    symbols_defined=symbols_defined,
                    start_line=other_nodes[0].lineno
                    if hasattr(other_nodes[0], "lineno")
                    else None,
                    end_line=other_nodes[-1].end_lineno
                    if hasattr(other_nodes[-1], "end_lineno")
                    else None,
                )
            )

        # Update indices
        total = len(chunks)
        for i, chunk in enumerate(chunks):
            chunk.index = i
            chunk.total = total

        return chunks

    def extract_symbols(self, content: str) -> SymbolTable:
        """
        Extract all symbol definitions from Python code.

        Args:
            content: Python source code

        Returns:
            SymbolTable with functions, classes, imports, and module-level vars
        """
        table = SymbolTable()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return table

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                table.functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                table.classes.append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    table.imports.append(name)

        # Module-level assignments (top-level only)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        table.module_level.append(target.id)

        return table

    def _get_node_text(self, node: ast.AST, lines: list[str]) -> str:
        """Extract source text for an AST node."""
        if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
            return ""
        start = node.lineno - 1
        end = node.end_lineno
        return "".join(lines[start:end])

    def _get_node_lines(self, nodes: list[ast.AST], lines: list[str]) -> list[str]:
        """Extract source lines for multiple nodes."""
        result = []
        for node in nodes:
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                start = node.lineno - 1
                end = node.end_lineno
                result.extend(lines[start:end])
        return result

    def _extract_import_symbols(self, import_nodes: list[ast.AST]) -> list[str]:
        """Extract imported symbol names."""
        symbols = []
        for node in import_nodes:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    symbols.append(name)
        return symbols

    def _extract_references(self, node: ast.AST) -> list[str]:
        """Extract external symbol references from a node."""
        references = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                references.add(child.id)
            elif isinstance(child, ast.Attribute):  # noqa: SIM102
                # Get base name (e.g., "os" from "os.path")
                if isinstance(child.value, ast.Name):
                    references.add(child.value.id)
        return list(references)

    def _fallback_chunk(self, content: str) -> list[CodeChunk]:
        """Fall back to generic chunking when AST parsing fails."""
        chunker = GenericCodeChunker()
        return chunker.chunk(content)


class GenericCodeChunker(BaseLanguageChunker):
    """
    Regex-based chunker for unsupported languages.

    Uses common patterns (function definitions, class declarations, etc.)
    to split code into chunks.
    """

    # Common patterns for function/class definitions across languages
    FUNCTION_PATTERNS = [
        # Python, Rust (fn), Go (func)
        r"^(?:async\s+)?(?:pub\s+)?(?:fn|func|def)\s+(\w+)",
        # JavaScript/TypeScript
        r"^(?:export\s+)?(?:async\s+)?(?:function|const|let|var)\s+(\w+)",
        # Java, C#, C++
        r"^(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(",
    ]

    CLASS_PATTERNS = [
        # Python, Java, C#, TypeScript
        r"^(?:export\s+)?(?:abstract\s+)?class\s+(\w+)",
        # Rust
        r"^(?:pub\s+)?(?:struct|enum|trait|impl)\s+(\w+)",
        # Go
        r"^type\s+(\w+)\s+(?:struct|interface)",
    ]

    def __init__(self, max_chunk_lines: int = 100) -> None:
        """
        Initialize generic chunker.

        Args:
            max_chunk_lines: Maximum lines per chunk
        """
        self._max_chunk_lines = max_chunk_lines
        self._function_patterns = [
            re.compile(p, re.MULTILINE) for p in self.FUNCTION_PATTERNS
        ]
        self._class_patterns = [
            re.compile(p, re.MULTILINE) for p in self.CLASS_PATTERNS
        ]

    def chunk(self, content: str) -> list[CodeChunk]:
        """
        Split code into chunks using regex patterns.

        Args:
            content: Source code text

        Returns:
            List of CodeChunk objects
        """
        lines = content.splitlines(keepends=True)
        chunks: list[CodeChunk] = []

        # Find all definition boundaries
        boundaries: list[tuple[int, str, ChunkType]] = []

        for i, line in enumerate(lines):
            # Check for class definitions
            for pattern in self._class_patterns:
                match = pattern.match(line)
                if match:
                    boundaries.append((i, match.group(1), ChunkType.CLASS))
                    break
            else:
                # Check for function definitions
                for pattern in self._function_patterns:
                    match = pattern.match(line)
                    if match:
                        boundaries.append((i, match.group(1), ChunkType.FUNCTION))
                        break

        # If no boundaries found, return content as single chunk
        if not boundaries:
            return [
                CodeChunk(
                    text=content,
                    index=0,
                    total=1,
                    chunk_type=ChunkType.UNKNOWN,
                    start_line=1,
                    end_line=len(lines),
                )
            ]

        # Extract chunks based on boundaries
        for i, (line_idx, name, chunk_type) in enumerate(boundaries):
            start = line_idx
            end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(lines)

            chunk_text = "".join(lines[start:end])
            chunks.append(
                CodeChunk(
                    text=chunk_text,
                    index=i,
                    total=0,  # Updated later
                    chunk_type=chunk_type,
                    symbols_defined=[name],
                    start_line=start + 1,
                    end_line=end,
                )
            )

        # Handle any content before first boundary
        if boundaries and boundaries[0][0] > 0:
            preamble_text = "".join(lines[: boundaries[0][0]])
            preamble = CodeChunk(
                text=preamble_text,
                index=0,
                total=0,
                chunk_type=ChunkType.MODULE_LEVEL,
                start_line=1,
                end_line=boundaries[0][0],
            )
            chunks.insert(0, preamble)

        # Update indices
        total = len(chunks)
        for i, chunk in enumerate(chunks):
            chunk.index = i
            chunk.total = total

        return chunks

    def extract_symbols(self, content: str) -> SymbolTable:
        """
        Extract symbol definitions using regex.

        Args:
            content: Source code text

        Returns:
            SymbolTable with extracted symbols
        """
        table = SymbolTable()

        for pattern in self._function_patterns:
            for match in pattern.finditer(content):
                table.functions.append(match.group(1))

        for pattern in self._class_patterns:
            for match in pattern.finditer(content):
                table.classes.append(match.group(1))

        return table


class CodeChunkerFactory:
    """Factory for creating language-specific code chunkers."""

    # Map file extensions to chunker classes
    LANGUAGE_MAP: dict[str, type[BaseLanguageChunker]] = {
        ".py": PythonCodeChunker,
        ".pyw": PythonCodeChunker,
        ".pyi": PythonCodeChunker,
    }

    # Extensions that use generic chunker
    GENERIC_EXTENSIONS = {
        ".rs",
        ".go",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".hpp",
        ".cs",
        ".rb",
        ".php",
        ".swift",
        ".kt",
        ".scala",
    }

    @classmethod
    def for_extension(cls, extension: str) -> BaseLanguageChunker:
        """
        Get an appropriate chunker for a file extension.

        Args:
            extension: File extension (e.g., ".py", ".rs")

        Returns:
            Language-appropriate chunker instance
        """
        ext = extension.lower()

        # Check for specific language support
        if ext in cls.LANGUAGE_MAP:
            return cls.LANGUAGE_MAP[ext]()

        # Use generic chunker for known code files
        if ext in cls.GENERIC_EXTENSIONS:
            return GenericCodeChunker()

        # Default to generic chunker
        return GenericCodeChunker()

    @classmethod
    def supports_extension(cls, extension: str) -> bool:
        """
        Check if an extension is recognized as code.

        Args:
            extension: File extension

        Returns:
            True if extension is a known code file type
        """
        ext = extension.lower()
        return ext in cls.LANGUAGE_MAP or ext in cls.GENERIC_EXTENSIONS
