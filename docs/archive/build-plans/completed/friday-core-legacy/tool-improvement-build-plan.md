# Build Plan: Friday Tools - Filesystem Read Enhancements

**Status:** Draft
**Target Component:** `packages/friday-tools/src/friday_tools/filesystem/read.py`
**Objective:** Enhance the filesystem reading capabilities to support rich document formats (PDF, DOCX), improve memory efficiency for large files, and consolidate redundant tool logic.

---

## 1. Problem Statement

The current implementation of `FileReadTool` and `FileReadLinesTool` has several critical limitations:
*   **Format Blindness:** Only supports plain text. Fails on PDFs, Word docs, and other binary-rich formats.
*   **Memory Inefficiency:** Loads entire files into memory before processing, posing OOM risks for large files.
*   **Rigid Encoding:** Strict UTF-8 reliance without auto-detection or graceful fallbacks.
*   **Redundancy:** Separate tools for "read all" vs "read range" create friction for agent usage.

## 2. Technical Architecture

### 2.1 Dependency Strategy
We will introduce optional dependencies to handle specific file types without bloating the core if unnecessary.

**Core Dependencies (Required):**
*   `chardet` or `charset-normalizer`: For robust encoding detection.

**Format Adapters (Optional/Lazy Loaded):**
*   **PDF:** `pypdf` (pure Python, lightweight) or `pdfminer.six` (better text extraction but heavier). *Decision: Start with `pypdf` for balance of size/capability.*
*   **DOCX:** `python-docx`.
*   **General Binary:** Native fallback to "hex dump" or metadata summary if no text adapter matches.

### 2.2 Design Pattern: Strategy & Factory
Refactor `read.py` to use a Strategy pattern.

```python
class FileReader(Protocol):
    def read(self, path: Path, **kwargs) -> str: ...

class TextReader(FileReader): ...
class PdfReader(FileReader): ...
class DocxReader(FileReader): ...

class ReaderFactory:
    def get_reader(self, path: Path) -> FileReader:
        # returns appropriate reader based on extension/mime
```

### 2.3 Streaming & Pagination
*   Implement `itertools.islice` for reading specific line ranges without loading the full file.
*   Update `FileReadTool` to accept `offset` (start_line) and `limit` (max_lines) to unify pagination logic.

## 3. Implementation Steps

### Phase 1: Dependency Management & Scaffold
1.  Update `packages/friday-tools/pyproject.toml` to include:
    *   `chardet` (main dependency)
    *   `pypdf` (optional group `documents`)
    *   `python-docx` (optional group `documents`)
2.  Create `packages/friday-tools/src/friday_tools/filesystem/adapters/` directory.

### Phase 2: Core Refactoring (Streaming & Encoding)
1.  **Consolidate Tools:** Merge functionality of `FileReadLinesTool` into `FileReadTool`.
2.  **Streaming Reader:** Rewrite the file reading logic to use a generator/iterator approach:
    ```python
    with open(path, ...) as f:
        # Move pointer efficiently
        # Read only requested chunk
    ```
3.  **Smart Encoding:**
    *   Attempt `utf-8`.
    *   On failure, peek at first chunk and use `chardet.detect`.
    *   On failure, fallback to `latin-1` or `errors='replace'`.

### Phase 3: Format Adapters
1.  **PDF Adapter:** Implement `PdfReaderAdapter` using `pypdf`.
    *   Extract text page by page.
    *   Handle encrypted PDFs gracefully (return error/message).
2.  **DOCX Adapter:** Implement `DocxReaderAdapter` using `python-docx`.
    *   Extract paragraph text.
3.  **Factory Integration:** Update `FileReadTool` to route requests through `ReaderFactory`.

### Phase 4: Testing & Validation
1.  **Unit Tests:**
    *   Test reading large dummy file (1GB+) with low memory footprint.
    *   Test distinct encodings (Shift-JIS, Latin-1).
    *   Test line range extraction (start/end logic).
2.  **Integration Tests:**
    *   Verify PDF text extraction.
    *   Verify DOCX text extraction.
    *   Ensure graceful failure on binary files (e.g., images).

## 4. Proposed API Changes

**Updated `FileReadTool` Schema:**

```json
{
  "path": "path/to/file.pdf",
  "start_line": 0,       // Optional: 0-indexed start
  "limit": 100,          // Optional: max lines to return
  "encoding": "auto",    // Optional: explicit override
  "force_text": false    // Optional: try to force read as text even if binary
}
```

## 5. Risk Assessment
*   **Performance:** Text extraction from large PDFs can be slow. *Mitigation: Add timeout or page limit parameters.*
*   **Dependency Size:** `pypdf` and `python-docx` add weight. *Mitigation: Make them optional extras; tool fails gracefully ("install friday-tools[documents] to read this file") if missing.*
