# Friday's Tool Requirements: Enhanced Directory Listing

## Problem Statement

The current `directory_list` tool is insufficient for agent framework development and debugging. It lacks critical metadata exposure, making it impossible to answer basic questions about file timestamps, permissions, and detailed attributes.

## Required Tool Specification

### Tool Name
`directory_stat` or `directory_list_full`

### Core Functionality
Expose complete file system metadata equivalent to Python's `os.stat()` or Unix `stat` command.

### Required Output Fields

For each file/directory, return:

```json
{
  "name": "filename.ext",
  "type": "file|directory|symlink",
  "size_bytes": 12345,
  "permissions": "rw-r--r--",
  "permissions_octal": "0644",
  "owner": "username",
  "group": "groupname",
  "created_time": "2026-01-24T13:29:00Z",
  "modified_time": "2026-01-24T13:29:00Z",
  "accessed_time": "2026-01-24T13:30:00Z",
  "inode": 123456,
  "hard_links": 1,
  "is_hidden": false,
  "symlink_target": null
}
```

### Required Parameters

```python
def directory_stat(
    path: str,
    recursive: bool = False,
    max_depth: int = None,
    include_hidden: bool = False,
    filter_pattern: str = "*",
    sort_by: str = "name",  # name|size|modified|created|accessed
    sort_order: str = "asc",  # asc|desc
    follow_symlinks: bool = False
) -> List[Dict]:
    """
    Return complete file system metadata for directory contents.
    
    Args:
        path: Directory path to list
        recursive: Traverse subdirectories
        max_depth: Maximum recursion depth (None = unlimited)
        include_hidden: Include files starting with '.'
        filter_pattern: Glob pattern for filtering (e.g., '*.py', '*.md')
        sort_by: Field to sort results by
        sort_order: Sort direction
        follow_symlinks: Follow symbolic links during traversal
        
    Returns:
        List of dictionaries containing full file metadata
    """
    pass
```

### Use Cases This Enables

1. **Timestamp queries**: "When were these files created?"
2. **Modification tracking**: "Which files changed in the last hour?"
3. **Size analysis**: "What are the largest files in this directory?"
4. **Permission debugging**: "Which files are executable?"
5. **Ownership verification**: "Who owns these files?"
6. **Symlink resolution**: "Where does this symlink point?"
7. **Recursive analysis**: "Find all Python files in subdirectories"
8. **Hidden file discovery**: "Show all dotfiles"

### Questions Current Tool Cannot Answer

From today's session:
- "When were these 11 files created?" - **Cannot answer** (no timestamps)
- "Which files were modified today?" - **Cannot answer** (no timestamps)
- "What are the file permissions?" - **Cannot answer** (no permission data)
- "Who owns these files?" - **Cannot answer** (no owner data)
- "Are there any symlinks?" - **Cannot answer** (no type detection)

### Implementation Notes

**Python Implementation:**
```python
import os
from pathlib import Path
from datetime import datetime

def directory_stat(path, **kwargs):
    results = []
    path_obj = Path(path)
    
    for item in path_obj.iterdir():
        stat_info = item.stat()
        results.append({
            "name": item.name,
            "type": "directory" if item.is_dir() else "file",
            "size_bytes": stat_info.st_size,
            "permissions": oct(stat_info.st_mode)[-3:],
            "created_time": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            "modified_time": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "accessed_time": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
            # ... additional fields
        })
    
    return results
```

**Alternative: Expose Unix `stat` directly:**
```python
import subprocess
import json

def directory_stat_unix(path):
    # Use stat command with JSON-friendly format
    cmd = ["stat", "-f", "%N|%z|%p|%u|%g|%B|%m|%a", path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    # Parse and structure output
    return parsed_results
```

### Priority: **CRITICAL**

Without this tool, Friday cannot:
- Debug file operations effectively
- Answer temporal questions about files
- Provide meaningful file analysis
- Support proper development workflows

### Backward Compatibility

Keep existing `directory_list` for simple use cases. Add `directory_stat` for full metadata access.

---

**Submitted by:** Friday  
**Date:** 2026-01-24  
**Status:** Awaiting development team review
