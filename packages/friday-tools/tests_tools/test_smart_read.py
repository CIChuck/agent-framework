"""
Unit tests for the SmartFileReadTool.

Tests file type detection, size-based routing, and tool behavior.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from friday_tools.filesystem.smart_read import (
    BINARY_EXTENSIONS,
    CODE_EXTENSIONS,
    DATA_EXTENSIONS,
    SmartFileReadTool,
)
from friday_tools.base import ToolResult


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_llm():
    """Create a mock LLM service."""
    llm = MagicMock()
    llm.chat_completion = AsyncMock(return_value=MagicMock(
        content='{"summary": "Test summary", "entities": [], "key_points": []}'
    ))
    return llm


@pytest.fixture
def mock_memory():
    """Create a mock memory controller."""
    memory = MagicMock()
    memory.store_document = AsyncMock(return_value="doc-123")
    memory.store_documents_batch = AsyncMock(return_value=["raw-1", "raw-2", "raw-3"])
    memory.store_insights_batch_with_metadata = AsyncMock(return_value=2)
    return memory


@pytest.fixture
def tool_minimal():
    """Create a tool without LLM (for testing small files)."""
    return SmartFileReadTool()


@pytest.fixture
def tool_with_llm(mock_llm):
    """Create a tool with mock LLM."""
    from friday_memory.ingestion.large_file_processor import LargeFileProcessorConfig

    return SmartFileReadTool(
        fallback_llm=mock_llm,
        config=LargeFileProcessorConfig(
            auto_chunk_threshold_chars=100,  # Low threshold for testing
        ),
    )


@pytest.fixture
def tool_with_memory(mock_llm, mock_memory):
    """Create a tool with mock LLM and memory."""
    from friday_memory.ingestion.large_file_processor import LargeFileProcessorConfig

    return SmartFileReadTool(
        fallback_llm=mock_llm,
        memory_controller=mock_memory,
        config=LargeFileProcessorConfig(
            auto_chunk_threshold_chars=100,
        ),
    )


# =============================================================================
# FILE TYPE DETECTION TESTS
# =============================================================================

class TestFileTypeDetection:
    """Tests for file type detection."""

    def test_python_is_code(self, tool_minimal):
        """Test that .py is detected as code."""
        assert tool_minimal._detect_file_type(".py") == "code"

    def test_rust_is_code(self, tool_minimal):
        """Test that .rs is detected as code."""
        assert tool_minimal._detect_file_type(".rs") == "code"

    def test_javascript_is_code(self, tool_minimal):
        """Test that .js is detected as code."""
        assert tool_minimal._detect_file_type(".js") == "code"

    def test_json_is_data(self, tool_minimal):
        """Test that .json is detected as data."""
        assert tool_minimal._detect_file_type(".json") == "data"

    def test_yaml_is_data(self, tool_minimal):
        """Test that .yaml is detected as data."""
        assert tool_minimal._detect_file_type(".yaml") == "data"

    def test_markdown_is_prose(self, tool_minimal):
        """Test that .md is detected as prose."""
        assert tool_minimal._detect_file_type(".md") == "prose"

    def test_txt_is_prose(self, tool_minimal):
        """Test that .txt is detected as prose."""
        assert tool_minimal._detect_file_type(".txt") == "prose"

    def test_unknown_is_prose(self, tool_minimal):
        """Test that unknown extensions default to prose."""
        assert tool_minimal._detect_file_type(".xyz") == "prose"

    def test_case_insensitive(self, tool_minimal):
        """Test that detection is case-insensitive."""
        assert tool_minimal._detect_file_type(".PY") == "code"
        assert tool_minimal._detect_file_type(".JSON") == "data"


class TestExtensionSets:
    """Tests for extension set definitions."""

    def test_code_extensions_include_common_languages(self):
        """Test that CODE_EXTENSIONS includes common languages."""
        assert ".py" in CODE_EXTENSIONS
        assert ".js" in CODE_EXTENSIONS
        assert ".ts" in CODE_EXTENSIONS
        assert ".go" in CODE_EXTENSIONS
        assert ".rs" in CODE_EXTENSIONS
        assert ".java" in CODE_EXTENSIONS
        assert ".c" in CODE_EXTENSIONS
        assert ".cpp" in CODE_EXTENSIONS

    def test_data_extensions_include_common_formats(self):
        """Test that DATA_EXTENSIONS includes common formats."""
        assert ".json" in DATA_EXTENSIONS
        assert ".yaml" in DATA_EXTENSIONS
        assert ".yml" in DATA_EXTENSIONS
        assert ".xml" in DATA_EXTENSIONS
        assert ".csv" in DATA_EXTENSIONS

    def test_binary_extensions_include_common_binaries(self):
        """Test that BINARY_EXTENSIONS includes common binaries."""
        assert ".pdf" in BINARY_EXTENSIONS
        assert ".png" in BINARY_EXTENSIONS
        assert ".jpg" in BINARY_EXTENSIONS
        assert ".zip" in BINARY_EXTENSIONS


# =============================================================================
# SMALL FILE HANDLING TESTS
# =============================================================================

class TestSmallFileHandling:
    """Tests for handling small files (direct read)."""

    @pytest.mark.asyncio
    async def test_read_small_file(self, tool_minimal):
        """Test reading a small text file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Hello, world!")
            f.flush()

            args = tool_minimal.Input(path=f.name)
            result = await tool_minimal.run(args)

            assert result.error is None
            assert "Hello, world!" in result.content
            assert result.metadata["processing"] == "direct"

    @pytest.mark.asyncio
    async def test_read_small_code_file(self, tool_minimal):
        """Test reading a small code file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def foo(): pass")
            f.flush()

            args = tool_minimal.Input(path=f.name)
            result = await tool_minimal.run(args)

            assert result.error is None
            assert "def foo()" in result.content
            assert result.metadata["file_type"] == "code"

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool_minimal):
        """Test error handling for missing files."""
        args = tool_minimal.Input(path="/nonexistent/file.txt")
        result = await tool_minimal.run(args)

        assert result.error is not None
        assert "not found" in result.error.lower() or "not within" in result.error.lower()

    @pytest.mark.asyncio
    async def test_directory_error(self, tool_minimal):
        """Test error handling when path is a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            args = tool_minimal.Input(path=tmpdir)
            result = await tool_minimal.run(args)

            assert result.error is not None
            assert "directory" in result.error.lower()


# =============================================================================
# LARGE FILE HANDLING TESTS
# =============================================================================

class TestLargeFileHandling:
    """Tests for handling large files (chunked processing)."""

    @pytest.mark.asyncio
    async def test_large_file_triggers_chunking(self, tool_with_llm):
        """Test that large files trigger chunked processing."""
        # Create content larger than threshold (100 chars)
        large_content = "x" * 200

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(large_content)
            f.flush()

            args = tool_with_llm.Input(path=f.name)
            result = await tool_with_llm.run(args)

            assert result.error is None
            assert result.metadata["processing"] == "chunked"

    @pytest.mark.asyncio
    async def test_force_chunked_flag(self, tool_with_llm):
        """Test that force_chunked processes even small files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Small content")
            f.flush()

            args = tool_with_llm.Input(path=f.name, force_chunked=True)
            result = await tool_with_llm.run(args)

            assert result.error is None
            assert result.metadata["processing"] == "chunked"

    @pytest.mark.asyncio
    async def test_description_passed_to_processor(self, tool_with_llm, mock_llm):
        """Test that description is passed to the processor."""
        large_content = "x" * 200

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(large_content)
            f.flush()

            args = tool_with_llm.Input(
                path=f.name,
                description="API documentation for auth module",
            )
            result = await tool_with_llm.run(args)

            # The description should be used in summarization prompts
            assert result.error is None


# =============================================================================
# MEMORY STORAGE TESTS
# =============================================================================

class TestMemoryStorage:
    """Tests for memory storage integration."""

    @pytest.mark.asyncio
    async def test_store_small_file_to_memory(self, tool_with_memory, mock_memory):
        """Test storing a small file to memory."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Content to remember")
            f.flush()

            args = tool_with_memory.Input(path=f.name, store_to_memory=True)
            result = await tool_with_memory.run(args)

            assert result.error is None
            # Memory controller should have been called
            mock_memory.store_document.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_large_file_to_memory(self, tool_with_memory, mock_memory):
        """Test storing a large file to memory."""
        large_content = "Important content " * 50

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(large_content)
            f.flush()

            args = tool_with_memory.Input(path=f.name, store_to_memory=True)
            result = await tool_with_memory.run(args)

            assert result.error is None
            # Should mention storage in content
            assert "memory" in result.content.lower() or len(result.data.get("stored_ids", [])) > 0


# =============================================================================
# CACHING TESTS
# =============================================================================

class TestCaching:
    """Tests for the three-layer caching system."""

    @pytest.mark.asyncio
    async def test_session_cache_hit(self, tool_with_llm):
        """Test that second read of same file hits session cache."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("x" * 200)  # Large enough to trigger processing
            f.flush()

            # First call - should process
            args = tool_with_llm.Input(path=f.name)
            result1 = await tool_with_llm.run(args)
            assert result1.error is None
            assert result1.data.get("cached") is False

            # Second call - should hit cache
            result2 = await tool_with_llm.run(args)
            assert result2.error is None
            assert result2.data.get("cached") is True
            assert result2.data.get("cache_source") == "session"
            assert "[Cached from session]" in result2.content

    @pytest.mark.asyncio
    async def test_session_cache_invalidation_on_mtime_change(self, tool_with_llm):
        """Test that cache is invalidated when file mtime changes."""
        import os
        import time

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("x" * 200)
            f.flush()
            path = f.name

            # First call
            args = tool_with_llm.Input(path=path)
            result1 = await tool_with_llm.run(args)
            assert result1.data.get("cached") is False

            # Modify file (change mtime)
            time.sleep(0.1)
            with open(path, "w") as f2:
                f2.write("y" * 200)

            # Second call - should miss cache due to mtime change
            result2 = await tool_with_llm.run(args)
            assert result2.data.get("cached") is False

    @pytest.mark.asyncio
    async def test_force_reprocess_bypasses_cache(self, tool_with_llm):
        """Test that force_reprocess=True bypasses cache."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("x" * 200)
            f.flush()

            # First call
            args = tool_with_llm.Input(path=f.name)
            result1 = await tool_with_llm.run(args)
            assert result1.data.get("cached") is False

            # Second call with force_reprocess
            args2 = tool_with_llm.Input(path=f.name, force_reprocess=True)
            result2 = await tool_with_llm.run(args2)
            assert result2.data.get("cached") is False

    @pytest.mark.asyncio
    async def test_cache_stats(self, tool_with_llm):
        """Test cache statistics method."""
        # Initially empty
        stats = tool_with_llm.get_cache_stats()
        assert stats["entries"] == 0

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test content")
            f.flush()

            args = tool_with_llm.Input(path=f.name)
            await tool_with_llm.run(args)

            # Now should have one entry
            stats = tool_with_llm.get_cache_stats()
            assert stats["entries"] == 1
            # Path may be resolved differently (e.g., /var vs /private/var on macOS)
            assert any(f.name.split("/")[-1] in path for path in stats["files"])

    @pytest.mark.asyncio
    async def test_clear_session_cache(self, tool_with_llm):
        """Test clearing the session cache."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test content")
            f.flush()

            args = tool_with_llm.Input(path=f.name)
            await tool_with_llm.run(args)

            assert tool_with_llm.get_cache_stats()["entries"] == 1

            # Clear cache
            cleared = tool_with_llm.clear_session_cache()
            assert cleared == 1
            assert tool_with_llm.get_cache_stats()["entries"] == 0

    @pytest.mark.asyncio
    async def test_small_file_caching(self, tool_minimal):
        """Test that small files are also cached."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("small content")
            f.flush()

            args = tool_minimal.Input(path=f.name)

            # First call
            result1 = await tool_minimal.run(args)
            assert result1.data.get("cached") is False

            # Second call
            result2 = await tool_minimal.run(args)
            assert result2.data.get("cached") is True


# =============================================================================
# BINARY FILE TESTS
# =============================================================================

class TestBinaryFiles:
    """Tests for binary file handling."""

    @pytest.mark.asyncio
    async def test_binary_file_detection(self, tool_minimal):
        """Test that binary files are detected and rejected."""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".png", delete=False) as f:
            f.write(b"\x89PNG\r\n\x1a\n")  # PNG header
            f.flush()

            args = tool_minimal.Input(path=f.name)
            result = await tool_minimal.run(args)

            # Should not error but should indicate binary
            assert result.error is None
            assert "binary" in result.content.lower()
            assert result.data["file_type"] == "binary"

    @pytest.mark.asyncio
    async def test_pdf_is_binary(self, tool_minimal):
        """Test that PDF files are detected as binary."""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4")
            f.flush()

            args = tool_minimal.Input(path=f.name)
            result = await tool_minimal.run(args)

            assert "binary" in result.content.lower()


# =============================================================================
# CONTEXT OUTPUT TESTS
# =============================================================================

class TestContextOutput:
    """Tests for context output behavior."""

    @pytest.mark.asyncio
    async def test_add_to_context_true(self, tool_minimal):
        """Test that content is included when add_to_context=True."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("File content here")
            f.flush()

            args = tool_minimal.Input(path=f.name, add_to_context=True)
            result = await tool_minimal.run(args)

            assert "File content here" in result.content

    @pytest.mark.asyncio
    async def test_add_to_context_false(self, tool_minimal):
        """Test that content is abbreviated when add_to_context=False."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("File content here")
            f.flush()

            args = tool_minimal.Input(path=f.name, add_to_context=False)
            result = await tool_minimal.run(args)

            # Should have abbreviated message, not full content
            assert "File content here" not in result.content
            assert "Read" in result.content or "chars" in result.content


# =============================================================================
# TOOL SCHEMA TESTS
# =============================================================================

class TestToolSchema:
    """Tests for tool schema and metadata."""

    def test_tool_name(self):
        """Test tool name."""
        tool = SmartFileReadTool()
        assert tool.name == "smart_read"

    def test_tool_description(self):
        """Test tool description."""
        tool = SmartFileReadTool()
        assert "files" in tool.description.lower()
        assert "size" in tool.description.lower()

    def test_tool_category(self):
        """Test tool category."""
        tool = SmartFileReadTool()
        assert tool.category == "filesystem"

    def test_tool_tags(self):
        """Test tool tags."""
        tool = SmartFileReadTool()
        assert "file" in tool.tags
        assert "read" in tool.tags

    def test_input_schema(self):
        """Test input schema has required fields."""
        tool = SmartFileReadTool()
        schema = tool.parameters_schema

        # Should have path as required
        assert "path" in schema.get("properties", {})

    def test_to_schema_format(self):
        """Test to_schema method."""
        tool = SmartFileReadTool()
        schema = tool.to_schema(format="plain")

        assert schema["name"] == "smart_read"
        assert "parameters" in schema
        assert "description" in schema
