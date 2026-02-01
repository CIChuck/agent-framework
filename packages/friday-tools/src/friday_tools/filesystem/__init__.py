"""
Filesystem tools for file and directory operations.

Ref: docs/specs/tool_specification.md - Categories 1-3: Filesystem Tools

Provides 17 tools for reading, writing, and managing files and directories.
"""

from .directory import (
    DirectoryListTool,
    directory_create,
    directory_list,
    directory_tree,
    file_search,
)
from .operations import file_chmod, file_copy, file_delete, file_move
from .read import FileReadTool, file_grep, file_info, file_read, file_read_lines
from .readers import (
    CsvReader,
    DocxReader,
    EncodingDetector,
    FileReader,
    PdfReader,
    ReaderFactory,
    ReaderResult,
    XlsxReader,
    detect_encoding,
    get_reader_for_path,
    read_with_smart_encoding,
)
from .write import (
    FileWriteTool,
    file_append,
    file_insert,
    file_patch,
    file_replace,
    file_write,
)
from .code_chunker import (
    BaseLanguageChunker,
    ChunkType,
    CodeChunk,
    CodeChunkerFactory,
    GenericCodeChunker,
    PythonCodeChunker,
    SymbolTable,
)
from .smart_read import SmartFileReadTool

__all__ = [
    # Read operations (classes)
    "FileReadTool",
    # Read operations (instances)
    "file_read",
    "file_read_lines",
    "file_info",
    "file_grep",
    # Reader utilities
    "FileReader",
    "ReaderResult",
    "ReaderFactory",
    "EncodingDetector",
    "detect_encoding",
    "read_with_smart_encoding",
    "get_reader_for_path",
    # Format-specific readers
    "CsvReader",
    "DocxReader",
    "PdfReader",
    "XlsxReader",
    # Write operations (classes)
    "FileWriteTool",
    # Write operations (instances)
    "file_write",
    "file_append",
    "file_insert",
    "file_replace",
    "file_patch",
    # File operations
    "file_copy",
    "file_move",
    "file_delete",
    "file_chmod",
    # Directory operations (classes)
    "DirectoryListTool",
    # Directory operations (instances)
    "directory_list",
    "directory_tree",
    "directory_create",
    "file_search",
    # Code chunking
    "CodeChunk",
    "ChunkType",
    "SymbolTable",
    "BaseLanguageChunker",
    "PythonCodeChunker",
    "GenericCodeChunker",
    "CodeChunkerFactory",
    # Smart file reading
    "SmartFileReadTool",
]
