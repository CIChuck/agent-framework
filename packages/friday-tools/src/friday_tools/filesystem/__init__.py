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
from .write import (
    FileWriteTool,
    file_append,
    file_insert,
    file_patch,
    file_replace,
    file_write,
)

__all__ = [
    # Read operations (classes)
    "FileReadTool",
    # Read operations (instances)
    "file_read",
    "file_read_lines",
    "file_info",
    "file_grep",
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
]
