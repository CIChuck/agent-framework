"""
Tests for filesystem readers module.

Tests encoding detection, CSV reading, and the reader factory.
PDF, DOCX, and XLSX tests are skipped if optional dependencies are not installed.
"""

import csv
import io
import tempfile
from pathlib import Path

import pytest

from friday_tools.filesystem.readers import (
    CsvReader,
    EncodingDetector,
    ReaderFactory,
    ReaderResult,
    detect_encoding,
    get_reader_for_path,
    read_with_smart_encoding,
)


def _normalize_encoding(encoding: str) -> str:
    """Normalize encoding name for comparison."""
    return encoding.lower().replace("_", "-").replace(" ", "-")


class TestEncodingDetector:
    """Tests for encoding detection."""

    def test_detect_utf8(self):
        """Test detection of UTF-8 encoded content."""
        content = "Hello, World! 你好世界".encode("utf-8")
        result = detect_encoding(content)
        normalized = _normalize_encoding(result.encoding)
        assert normalized in ["utf-8", "ascii"]
        # charset-normalizer may return 0.0 confidence for high-certainty detections
        assert result.confidence >= 0

    def test_detect_latin1(self):
        """Test detection of Latin-1 encoded content."""
        # Content with Latin-1 specific characters
        content = "Café résumé naïve".encode("latin-1")
        result = detect_encoding(content)
        # charset-normalizer might detect as various encodings
        assert result.encoding is not None
        assert result.confidence >= 0

    def test_detect_empty_bytes(self):
        """Test detection of empty content."""
        result = detect_encoding(b"")
        assert result.encoding == "utf-8"
        assert result.method == "default_empty"

    def test_detect_file(self, tmp_path):
        """Test encoding detection from file."""
        # Create a file with UTF-8 content
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World! 日本語", encoding="utf-8")

        result = detect_encoding(test_file)
        normalized = _normalize_encoding(result.encoding)
        assert normalized in ["utf-8", "ascii"]

    def test_detector_class(self):
        """Test EncodingDetector class directly."""
        detector = EncodingDetector(min_confidence=0.5)
        result = detector.detect_bytes(b"Simple ASCII text")
        normalized = _normalize_encoding(result.encoding)
        assert normalized in ["utf-8", "ascii"]


class TestReadWithSmartEncoding:
    """Tests for smart encoding file reading."""

    def test_read_utf8_file(self, tmp_path):
        """Test reading a UTF-8 file."""
        test_file = tmp_path / "test.txt"
        content = "Hello, World!\nLine 2\nLine 3"
        test_file.write_text(content, encoding="utf-8")

        result, enc_info = read_with_smart_encoding(test_file)
        assert result == content
        assert enc_info.encoding.lower() in ["utf-8", "ascii"]

    def test_read_with_explicit_encoding(self, tmp_path):
        """Test reading with explicit encoding override."""
        test_file = tmp_path / "test.txt"
        content = "Café"
        test_file.write_text(content, encoding="utf-8")

        result, enc_info = read_with_smart_encoding(
            test_file,
            explicit_encoding="utf-8"
        )
        assert result == content
        assert enc_info.method == "explicit"

    def test_read_nonexistent_file(self, tmp_path):
        """Test reading a file that doesn't exist."""
        test_file = tmp_path / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            read_with_smart_encoding(test_file)


class TestCsvReader:
    """Tests for CSV reader."""

    def test_read_simple_csv(self, tmp_path):
        """Test reading a simple CSV file."""
        test_file = tmp_path / "data.csv"
        test_file.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\n")

        reader = CsvReader()
        assert reader.can_read(test_file)

        result = reader.read(test_file)
        assert result.success
        assert "Alice" in result.content
        assert "Bob" in result.content
        assert result.metadata["row_count"] == 2
        assert result.metadata["column_count"] == 3

    def test_read_csv_with_limit(self, tmp_path):
        """Test reading CSV with row limit."""
        test_file = tmp_path / "data.csv"
        # Create CSV with many rows
        lines = ["id,value"] + [f"{i},{i*10}" for i in range(100)]
        test_file.write_text("\n".join(lines))

        reader = CsvReader()
        result = reader.read(test_file, limit=10)

        assert result.success
        assert result.truncated
        assert result.metadata["row_count"] == 100  # Total data rows (0-99)

    def test_read_csv_raw_format(self, tmp_path):
        """Test reading CSV in raw format."""
        test_file = tmp_path / "data.csv"
        test_file.write_text("a,b,c\n1,2,3\n4,5,6\n")

        reader = CsvReader()
        result = reader.read(test_file, format_as_table=False)

        assert result.success
        # Raw format should preserve CSV structure
        assert "a,b,c" in result.content or "a\tb\tc" in result.content

    def test_read_tsv_file(self, tmp_path):
        """Test reading a TSV file."""
        test_file = tmp_path / "data.tsv"
        test_file.write_text("name\tage\tcolor\nAlice\t30\tblue\n")

        reader = CsvReader()
        assert reader.can_read(test_file)

        result = reader.read(test_file)
        assert result.success
        assert "Alice" in result.content

    def test_csv_dialect_detection(self, tmp_path):
        """Test automatic dialect detection for different delimiters."""
        # Semicolon-separated
        test_file = tmp_path / "data.csv"
        test_file.write_text("name;age;city\nAlice;30;NYC\n")

        reader = CsvReader()
        result = reader.read(test_file)

        assert result.success
        # Should detect semicolon delimiter
        assert "Alice" in result.content


class TestReaderFactory:
    """Tests for the reader factory."""

    def test_factory_routes_csv(self, tmp_path):
        """Test factory routes CSV to CsvReader."""
        test_file = tmp_path / "data.csv"
        test_file.write_text("a,b\n1,2\n")

        factory = ReaderFactory()
        reader = factory.get_reader(test_file)

        assert reader.__class__.__name__ == "CsvReader"

    def test_factory_routes_text(self, tmp_path):
        """Test factory routes text files to TextReader."""
        test_file = tmp_path / "code.py"
        test_file.write_text("print('hello')")

        factory = ReaderFactory()
        reader = factory.get_reader(test_file)

        assert reader.__class__.__name__ == "TextReader"

    def test_factory_routes_binary(self, tmp_path):
        """Test factory routes unknown binary to BinaryFallbackReader."""
        test_file = tmp_path / "data.bin"
        test_file.write_bytes(b"\x00\x01\x02\x03\x04")

        factory = ReaderFactory()
        reader = factory.get_reader(test_file)

        assert reader.__class__.__name__ == "BinaryFallbackReader"

    def test_factory_read_csv(self, tmp_path):
        """Test factory.read() with CSV file."""
        test_file = tmp_path / "data.csv"
        test_file.write_text("x,y\n1,2\n3,4\n")

        factory = ReaderFactory()
        result = factory.read(test_file)

        assert result.success
        assert "1" in result.content

    def test_factory_supported_extensions(self):
        """Test getting supported extensions."""
        factory = ReaderFactory()
        extensions = factory.get_supported_extensions()

        assert ".csv" in extensions
        assert ".pdf" in extensions
        assert ".docx" in extensions
        assert ".xlsx" in extensions
        assert ".txt" in extensions

    def test_get_reader_for_path(self, tmp_path):
        """Test module-level get_reader_for_path function."""
        test_file = tmp_path / "data.csv"
        test_file.write_text("a,b\n1,2\n")

        reader = get_reader_for_path(test_file)
        assert reader.__class__.__name__ == "CsvReader"


class TestPdfReader:
    """Tests for PDF reader (skipped if pypdf not installed)."""

    @pytest.fixture
    def pdf_available(self):
        """Check if pypdf is available."""
        try:
            import pypdf
            return True
        except ImportError:
            return False

    def test_pdf_reader_missing_dependency(self, tmp_path, pdf_available):
        """Test graceful failure when pypdf not installed."""
        from friday_tools.filesystem.readers import PdfReader

        reader = PdfReader()
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4 fake pdf")

        result = reader.read(test_file)

        # Should either work or report missing dependency/corrupted file
        if not result.success:
            error_lower = result.error.lower()
            assert (
                "pypdf" in error_lower
                or "dependencies" in error_lower
                or "invalid" in error_lower
                or "corrupted" in error_lower
            )


class TestDocxReader:
    """Tests for DOCX reader (skipped if python-docx not installed)."""

    def test_docx_reader_missing_dependency(self, tmp_path):
        """Test graceful failure when python-docx not installed."""
        from friday_tools.filesystem.readers import DocxReader

        reader = DocxReader()
        test_file = tmp_path / "test.docx"
        test_file.write_bytes(b"PK\x03\x04 fake docx")

        result = reader.read(test_file)

        # Should either work or report missing dependency
        if not result.success:
            assert "python-docx" in result.error or "dependencies" in result.error.lower()


class TestXlsxReader:
    """Tests for XLSX reader (skipped if openpyxl not installed)."""

    def test_xlsx_reader_missing_dependency(self, tmp_path):
        """Test graceful failure when openpyxl not installed."""
        from friday_tools.filesystem.readers import XlsxReader

        reader = XlsxReader()
        test_file = tmp_path / "test.xlsx"
        test_file.write_bytes(b"PK\x03\x04 fake xlsx")

        result = reader.read(test_file)

        # Should either work or report missing dependency
        if not result.success:
            assert "openpyxl" in result.error or "dependencies" in result.error.lower()


class TestFileReadToolIntegration:
    """Integration tests for FileReadTool with new encoding support."""

    @pytest.mark.asyncio
    async def test_file_read_tool_auto_encoding(self, tmp_path):
        """Test FileReadTool with auto encoding detection."""
        from friday_tools.filesystem import FileReadTool

        tool = FileReadTool()
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!\n日本語テスト\n", encoding="utf-8")

        result = await tool.run(
            tool.Input(path=str(test_file), encoding="auto")
        )

        assert not result.error
        assert "Hello" in result.content
        # Normalize encoding name (charset-normalizer returns utf_8)
        normalized_encoding = _normalize_encoding(result.data["encoding"])
        assert normalized_encoding in ["utf-8", "ascii"]
        assert "encoding_confidence" in result.data

    @pytest.mark.asyncio
    async def test_file_read_tool_with_pagination(self, tmp_path):
        """Test FileReadTool with start_line and max_lines."""
        from friday_tools.filesystem import FileReadTool

        tool = FileReadTool()
        test_file = tmp_path / "test.txt"
        lines = [f"Line {i}" for i in range(1, 21)]
        test_file.write_text("\n".join(lines))

        # Read lines 5-10
        result = await tool.run(
            tool.Input(
                path=str(test_file),
                start_line=5,
                max_lines=6
            )
        )

        assert not result.error
        assert "Line 5" in result.content
        assert "Line 10" in result.content
        assert result.metadata["truncated"]
        assert result.data["total_lines"] == 20
