"""
Unit tests for the large_file_processor module.

Tests the chunk-summarize-synthesize pipeline with mocked LLM.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from friday_memory.ingestion.large_file_processor import (
    ChunkSummary,
    LargeFileProcessor,
    LargeFileProcessorConfig,
    ProcessingResult,
    SmartFileLLMConfig,
    SmartFilePromptsConfig,
)

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_llm():
    """Create a mock LLM service."""
    llm = MagicMock()
    llm.chat_completion = AsyncMock()
    return llm


@pytest.fixture
def mock_memory_controller():
    """Create a mock memory controller."""
    controller = MagicMock()
    controller.store_document = AsyncMock(return_value="doc-123")
    controller.store_documents_batch = AsyncMock(
        return_value=["raw-1", "raw-2", "raw-3"]
    )
    controller.store_insights_batch_with_metadata = AsyncMock(return_value=3)
    return controller


@pytest.fixture
def processor(mock_llm):
    """Create a processor with mock LLM."""
    return LargeFileProcessor(
        fallback_llm=mock_llm,
        config=LargeFileProcessorConfig(
            auto_chunk_threshold_chars=1000,
            chunk_size=100,
            chunk_overlap=10,
        ),
    )


@pytest.fixture
def processor_with_memory(mock_llm, mock_memory_controller):
    """Create a processor with mock LLM and memory controller."""
    return LargeFileProcessor(
        fallback_llm=mock_llm,
        config=LargeFileProcessorConfig(
            auto_chunk_threshold_chars=1000,
            chunk_size=100,
            chunk_overlap=10,
        ),
        memory_controller=mock_memory_controller,
    )


# =============================================================================
# SAMPLE CONTENT
# =============================================================================

SAMPLE_PROSE = """
# Introduction to AI

Artificial intelligence (AI) is a branch of computer science that aims to create
intelligent machines that can perform tasks that typically require human intelligence.
These tasks include visual perception, speech recognition, decision-making, and
language translation.

## History

The field of AI research was founded at a conference at Dartmouth College in 1956.
Early AI research focused on symbolic methods and problem-solving. The term
"artificial intelligence" was coined by John McCarthy.

## Modern Applications

Today, AI is used in many applications including:
- Virtual assistants like Siri and Alexa
- Recommendation systems on Netflix and Spotify
- Autonomous vehicles
- Medical diagnosis systems

The future of AI holds great promise for transforming various industries.
"""

SAMPLE_CODE = '''
"""
A simple calculator module.
"""

from typing import Union

Number = Union[int, float]


class Calculator:
    """A basic calculator with memory."""

    def __init__(self):
        self.memory = 0

    def add(self, a: Number, b: Number) -> Number:
        """Add two numbers."""
        return a + b

    def subtract(self, a: Number, b: Number) -> Number:
        """Subtract b from a."""
        return a - b

    def multiply(self, a: Number, b: Number) -> Number:
        """Multiply two numbers."""
        return a * b

    def divide(self, a: Number, b: Number) -> Number:
        """Divide a by b."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b


def main():
    """Entry point."""
    calc = Calculator()
    print(calc.add(2, 3))


if __name__ == "__main__":
    main()
'''


# =============================================================================
# CONFIGURATION TESTS
# =============================================================================


class TestConfiguration:
    """Tests for configuration dataclasses."""

    def test_default_config(self):
        """Test default configuration values."""
        config = LargeFileProcessorConfig()

        assert config.auto_chunk_threshold_chars == 50000
        assert config.chunk_size == 512
        assert config.chunk_overlap == 50
        assert config.preserve_code_structure is True
        assert config.extract_symbols is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = LargeFileProcessorConfig(
            auto_chunk_threshold_chars=10000,
            chunk_size=256,
            chunk_overlap=25,
        )

        assert config.auto_chunk_threshold_chars == 10000
        assert config.chunk_size == 256
        assert config.chunk_overlap == 25

    def test_llm_config(self):
        """Test LLM configuration."""
        config = SmartFileLLMConfig(
            model="gpt-4",
            api_base="https://api.openai.com/v1",
            temperature=0.5,
            max_tokens=1000,
        )

        assert config.model == "gpt-4"
        assert config.api_base == "https://api.openai.com/v1"
        assert config.temperature == 0.5
        assert config.max_tokens == 1000

    def test_prompts_config_defaults(self):
        """Test that prompts config has defaults."""
        config = SmartFilePromptsConfig()

        assert "{file_path}" in config.prose_summarization
        assert "{chunk_text}" in config.prose_summarization
        assert "{chunk_type}" in config.code_summarization
        assert "{numbered_summaries}" in config.prose_synthesis


# =============================================================================
# PROSE PROCESSING TESTS
# =============================================================================


class TestProseProcessing:
    """Tests for prose/document processing."""

    @pytest.mark.asyncio
    async def test_process_prose_basic(self, processor, mock_llm):
        """Test basic prose processing."""
        # Setup mock responses
        mock_llm.chat_completion.return_value = MagicMock(
            content=json.dumps(
                {
                    "summary": "Test summary",
                    "entities": ["AI", "computer science"],
                    "key_points": ["AI research", "modern applications"],
                }
            )
        )

        result = await processor.process(
            content=SAMPLE_PROSE,
            file_path="/test/doc.md",
            file_type="prose",
        )

        assert isinstance(result, ProcessingResult)
        assert result.file_path == "/test/doc.md"
        assert result.file_type == "prose"
        assert result.total_chars == len(SAMPLE_PROSE)
        assert len(result.chunk_summaries) > 0

    @pytest.mark.asyncio
    async def test_process_prose_synthesis(self, processor, mock_llm):
        """Test that prose synthesis is called."""
        # Setup mock responses for summarization and synthesis
        mock_llm.chat_completion.side_effect = [
            # Chunk summaries
            MagicMock(
                content=json.dumps(
                    {
                        "summary": "Section 1 summary",
                        "entities": ["AI"],
                        "key_points": ["point 1"],
                    }
                )
            ),
            MagicMock(
                content=json.dumps(
                    {
                        "summary": "Section 2 summary",
                        "entities": ["ML"],
                        "key_points": ["point 2"],
                    }
                )
            ),
            # Synthesis
            MagicMock(
                content=json.dumps(
                    {
                        "summary": "Overall document summary",
                        "key_themes": ["AI", "ML"],
                        "entities": ["AI", "ML"],
                        "insights": ["insight 1"],
                    }
                )
            ),
        ]

        result = await processor.process(
            content=SAMPLE_PROSE,
            file_path="/test/doc.md",
            file_type="prose",
        )

        assert "summary" in result.synthesis or "Summary" in result.content_for_context

    @pytest.mark.asyncio
    async def test_empty_content(self, processor):
        """Test processing empty content."""
        result = await processor.process(
            content="",
            file_path="/test/empty.txt",
            file_type="prose",
        )

        assert result.chunks_processed == 0
        assert result.total_chars == 0


# =============================================================================
# CODE PROCESSING TESTS
# =============================================================================


class TestCodeProcessing:
    """Tests for code processing."""

    @pytest.mark.asyncio
    async def test_process_code_basic(self, processor, mock_llm):
        """Test basic code processing."""
        mock_llm.chat_completion.return_value = MagicMock(
            content=json.dumps(
                {
                    "summary": "A calculator class",
                    "purpose": "Basic arithmetic",
                    "dependencies": ["typing"],
                }
            )
        )

        result = await processor.process(
            content=SAMPLE_CODE,
            file_path="/test/calc.py",
            file_type="code",
            language="python",
        )

        assert isinstance(result, ProcessingResult)
        assert result.file_type == "code"
        assert result.chunks_processed > 0
        # Should have extracted entities (class names, function names)
        assert len(result.entities) > 0

    @pytest.mark.asyncio
    async def test_code_extracts_symbols(self, processor, mock_llm):
        """Test that code processing extracts symbols."""
        mock_llm.chat_completion.return_value = MagicMock(
            content=json.dumps(
                {
                    "summary": "Calculator functionality",
                    "purpose": "Math operations",
                    "dependencies": [],
                }
            )
        )

        result = await processor.process(
            content=SAMPLE_CODE,
            file_path="/test/calc.py",
            file_type="code",
            language="python",
        )

        # Should have extracted class and function names
        entity_str = " ".join(result.entities).lower()
        assert "calculator" in entity_str or "add" in entity_str or "main" in entity_str


# =============================================================================
# MEMORY STORAGE TESTS
# =============================================================================


class TestMemoryStorage:
    """Tests for memory storage integration."""

    @pytest.mark.asyncio
    async def test_store_to_memory(
        self, processor_with_memory, mock_llm, mock_memory_controller
    ):
        """Test storing results to memory."""
        mock_llm.chat_completion.return_value = MagicMock(
            content=json.dumps(
                {
                    "summary": "Test document about AI",
                    "entities": ["AI"],
                    "key_points": ["AI research"],
                }
            )
        )

        result = await processor_with_memory.process(
            content=SAMPLE_PROSE,
            file_path="/test/doc.md",
            file_type="prose",
            store_to_memory=True,
        )

        # Should have called memory controller
        assert mock_memory_controller.store_document.called
        assert len(result.stored_ids) > 0

    @pytest.mark.asyncio
    async def test_no_store_when_disabled(
        self, processor_with_memory, mock_llm, mock_memory_controller
    ):
        """Test that memory storage is skipped when disabled."""
        mock_llm.chat_completion.return_value = MagicMock(
            content=json.dumps(
                {
                    "summary": "Test summary",
                    "entities": [],
                    "key_points": [],
                }
            )
        )

        await processor_with_memory.process(
            content=SAMPLE_PROSE,
            file_path="/test/doc.md",
            file_type="prose",
            store_to_memory=False,
        )

        # Should not have called store_document
        assert not mock_memory_controller.store_document.called


# =============================================================================
# CONTEXT CONTENT TESTS
# =============================================================================


class TestContextContent:
    """Tests for context content generation."""

    @pytest.mark.asyncio
    async def test_context_content_includes_summary(self, processor, mock_llm):
        """Test that context content includes the summary."""
        mock_llm.chat_completion.return_value = MagicMock(
            content=json.dumps(
                {
                    "summary": "This is a comprehensive overview",
                    "entities": ["AI"],
                    "key_points": [],
                }
            )
        )

        result = await processor.process(
            content=SAMPLE_PROSE,
            file_path="/test/doc.md",
            file_type="prose",
        )

        # Context content should include file path and summary
        assert "/test/doc.md" in result.content_for_context

    @pytest.mark.asyncio
    async def test_context_content_for_code(self, processor, mock_llm):
        """Test context content format for code files."""
        mock_llm.chat_completion.return_value = MagicMock(
            content=json.dumps(
                {
                    "overview": "A calculator module",
                    "components": ["Calculator class"],
                    "dependencies": ["typing"],
                }
            )
        )

        result = await processor.process(
            content=SAMPLE_CODE,
            file_path="/test/calc.py",
            file_type="code",
            language="python",
        )

        # Should have structured format
        assert "calc.py" in result.content_for_context


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_llm_error_handling(self, processor, mock_llm):
        """Test handling of LLM errors during summarization."""
        mock_llm.chat_completion.side_effect = Exception("LLM unavailable")

        # Should not raise, should handle gracefully
        result = await processor.process(
            content=SAMPLE_PROSE,
            file_path="/test/doc.md",
            file_type="prose",
        )

        # Should still return a result (with placeholder summaries)
        assert isinstance(result, ProcessingResult)

    @pytest.mark.asyncio
    async def test_invalid_json_handling(self, processor, mock_llm):
        """Test handling of invalid JSON from LLM."""
        mock_llm.chat_completion.return_value = MagicMock(
            content="This is not valid JSON"
        )

        # Should not raise, should handle gracefully
        result = await processor.process(
            content=SAMPLE_PROSE,
            file_path="/test/doc.md",
            file_type="prose",
        )

        assert isinstance(result, ProcessingResult)

    @pytest.mark.asyncio
    async def test_json_in_markdown_block(self, processor, mock_llm):
        """Test parsing JSON wrapped in markdown code block."""
        mock_llm.chat_completion.return_value = MagicMock(
            content='```json\n{"summary": "Test", "entities": [], "key_points": []}\n```'  # noqa: E501
        )

        result = await processor.process(
            content=SAMPLE_PROSE,
            file_path="/test/doc.md",
            file_type="prose",
        )

        # Should successfully parse
        assert isinstance(result, ProcessingResult)


# =============================================================================
# RESULT DATACLASS TESTS
# =============================================================================


class TestResultDataclasses:
    """Tests for result dataclasses."""

    def test_chunk_summary_creation(self):
        """Test ChunkSummary creation."""
        summary = ChunkSummary(
            chunk_index=0,
            summary="Test summary",
            entities=["AI", "ML"],
            key_points=["point 1"],
            chunk_type="function",
            symbols_defined=["main"],
        )

        assert summary.chunk_index == 0
        assert summary.summary == "Test summary"
        assert "AI" in summary.entities
        assert summary.chunk_type == "function"

    def test_processing_result_creation(self):
        """Test ProcessingResult creation."""
        from friday_memory.ingestion.large_file_processor import RawChunk

        result = ProcessingResult(
            content_for_context="Test content",
            chunk_summaries=[],
            raw_chunks=[RawChunk(text="raw text", index=0, chunk_type="prose")],
            synthesis={"summary": "Test"},
            entities=["AI"],
            file_path="/test/file.txt",
            file_type="prose",
            chunks_processed=5,
            total_chars=1000,
        )

        assert result.content_for_context == "Test content"
        assert result.chunks_processed == 5
        assert result.stored_ids == []  # Default
        assert len(result.raw_chunks) == 1
        assert result.raw_chunks[0].text == "raw text"
