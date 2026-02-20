"""
Tests for DocumentIngestionPipeline.

Tests cover:
- Text chunking with overlap
- File ingestion
- Metadata extraction
- Vector store preparation
"""

import tempfile

import pytest
from friday_memory.ingestion import (
    DocumentIngestionPipeline,
    IngestedDocument,
)


@pytest.fixture
def pipeline() -> DocumentIngestionPipeline:
    """Create a pipeline with default settings."""
    return DocumentIngestionPipeline(
        chunk_size=500,
        overlap=50,
        author_id="test_pipeline",
    )


@pytest.fixture
def small_chunk_pipeline() -> DocumentIngestionPipeline:
    """Create a pipeline with small chunks for testing."""
    return DocumentIngestionPipeline(
        chunk_size=100,
        overlap=20,
        author_id="test_pipeline",
    )


class TestTextChunking:
    """Tests for text chunking logic."""

    def test_chunk_small_text(self, pipeline: DocumentIngestionPipeline):
        """Test that small text isn't chunked."""
        text = "This is a short text."
        chunks = pipeline._chunk_text(text)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_empty_text(self, pipeline: DocumentIngestionPipeline):
        """Test that empty text returns no chunks."""
        chunks = pipeline._chunk_text("")
        assert chunks == []

    def test_chunk_whitespace_only(self, pipeline: DocumentIngestionPipeline):
        """Test that whitespace-only text returns no chunks."""
        chunks = pipeline._chunk_text("   \n\t   ")
        assert chunks == []

    def test_chunk_long_text(self, small_chunk_pipeline: DocumentIngestionPipeline):
        """Test chunking of long text."""
        text = "This is a longer piece of text. " * 20
        chunks = small_chunk_pipeline._chunk_text(text)

        assert len(chunks) > 1
        # Each chunk should be roughly the target size
        for chunk in chunks[:-1]:  # Last chunk may be smaller
            assert len(chunk) <= small_chunk_pipeline.chunk_size + 50

    def test_chunk_preserves_paragraph_breaks(
        self, small_chunk_pipeline: DocumentIngestionPipeline
    ):
        """Test that chunking prefers paragraph breaks."""
        text = "Paragraph one. " * 10 + "\n\n" + "Paragraph two. " * 10
        chunks = small_chunk_pipeline._chunk_text(text)

        # Should prefer to break at paragraph boundary
        assert len(chunks) >= 2


class TestTextIngestion:
    """Tests for raw text ingestion."""

    def test_ingest_text_basic(self, pipeline: DocumentIngestionPipeline):
        """Test basic text ingestion."""
        result = pipeline.ingest_text(
            text="This is test content.",
            source_name="test_input",
        )

        assert isinstance(result, IngestedDocument)
        assert result.source_path == "test_input"
        assert result.total_characters == len("This is test content.")
        assert result.total_chunks >= 1

    def test_ingest_text_with_metadata(self, pipeline: DocumentIngestionPipeline):
        """Test text ingestion with additional metadata."""
        result = pipeline.ingest_text(
            text="Content with metadata.",
            source_name="metadata_test",
            additional_metadata={"category": "test", "priority": 1},
        )

        # Check metadata is attached to chunks
        assert len(result.chunks) > 0
        chunk = result.chunks[0]
        assert chunk.metadata["category"] == "test"
        assert chunk.metadata["priority"] == 1

    def test_ingest_text_creates_provenance(self, pipeline: DocumentIngestionPipeline):
        """Test that ingestion creates proper provenance."""
        result = pipeline.ingest_text(
            text="Content for provenance test.",
            source_id="custom_source_123",
        )

        chunk = result.chunks[0]
        assert chunk.provenance.source_id == "custom_source_123"
        assert chunk.provenance.source_type == "document"
        assert chunk.provenance.confidence == 1.0
        assert chunk.provenance.author_id == "test_pipeline"

    def test_ingest_text_chunk_ids(
        self, small_chunk_pipeline: DocumentIngestionPipeline
    ):
        """Test that chunks have sequential IDs."""
        text = "This is content. " * 50
        result = small_chunk_pipeline.ingest_text(text, source_name="test")

        for i, chunk in enumerate(result.chunks):
            assert f"chunk_{i}" in chunk.id


class TestFileIngestion:
    """Tests for file ingestion."""

    def test_ingest_text_file(self, pipeline: DocumentIngestionPipeline):
        """Test ingesting a .txt file."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("This is text file content.\nWith multiple lines.")
            f.flush()

            result = pipeline.ingest_file(f.name)

            assert result.total_chunks >= 1
            assert "filename" in result.chunks[0].metadata
            assert result.chunks[0].metadata["extension"] == ".txt"

    def test_ingest_markdown_file(self, pipeline: DocumentIngestionPipeline):
        """Test ingesting a .md file."""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
            f.write("# Heading\n\nThis is markdown content.")
            f.flush()

            result = pipeline.ingest_file(f.name)
            assert result.chunks[0].metadata["extension"] == ".md"

    def test_ingest_python_file(self, pipeline: DocumentIngestionPipeline):
        """Test ingesting a .py file."""
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write("def hello():\n    print('Hello, World!')")
            f.flush()

            result = pipeline.ingest_file(f.name)
            assert result.chunks[0].metadata["extension"] == ".py"

    def test_ingest_unsupported_file(self, pipeline: DocumentIngestionPipeline):
        """Test that unsupported file types raise ValueError."""
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            f.write(b"binary content")
            f.flush()

            with pytest.raises(ValueError, match="Unsupported file type"):
                pipeline.ingest_file(f.name)

    def test_ingest_nonexistent_file(self, pipeline: DocumentIngestionPipeline):
        """Test that non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            pipeline.ingest_file("/path/to/nonexistent/file.txt")

    def test_ingest_file_with_metadata(self, pipeline: DocumentIngestionPipeline):
        """Test file ingestion with additional metadata."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("Content for metadata test.")
            f.flush()

            result = pipeline.ingest_file(
                f.name,
                additional_metadata={"project": "friday", "version": "1.0"},
            )

            chunk = result.chunks[0]
            assert chunk.metadata["project"] == "friday"
            assert chunk.metadata["version"] == "1.0"


class TestVectorStorePreparation:
    """Tests for vector store preparation."""

    def test_prepare_for_vector_store(self, pipeline: DocumentIngestionPipeline):
        """Test preparing document for vector store."""
        document = pipeline.ingest_text(
            text="Content for vector store.",
            source_name="vector_test",
        )

        texts, metadatas, ids = pipeline.prepare_for_vector_store(document)

        assert len(texts) == len(metadatas) == len(ids)
        assert len(texts) == document.total_chunks

        # Check metadata includes provenance
        meta = metadatas[0]
        assert "provenance_source_id" in meta
        assert "provenance_source_type" in meta
        assert "provenance_confidence" in meta

    def test_prepare_preserves_chunk_order(
        self, small_chunk_pipeline: DocumentIngestionPipeline
    ):
        """Test that preparation preserves chunk order."""
        text = "First chunk content. " * 10 + "Second chunk content. " * 10
        document = small_chunk_pipeline.ingest_text(text, source_name="order_test")

        texts, metadatas, ids = small_chunk_pipeline.prepare_for_vector_store(document)

        # Check chunk indices are sequential
        for i, meta in enumerate(metadatas):
            assert meta["chunk_index"] == i


class TestSupportedExtensions:
    """Tests for supported file extensions."""

    def test_supported_extensions_constant(self):
        """Test that supported extensions are defined."""
        extensions = DocumentIngestionPipeline.SUPPORTED_EXTENSIONS

        assert ".txt" in extensions
        assert ".md" in extensions
        assert ".py" in extensions
        assert ".json" in extensions
        assert ".yaml" in extensions
        assert ".yml" in extensions
        assert ".html" in extensions
        assert ".css" in extensions
        assert ".js" in extensions
        assert ".ts" in extensions
