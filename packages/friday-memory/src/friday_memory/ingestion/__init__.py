"""
Document Processing Logic.

This module handles file parsing, chunking, and metadata extraction
for document ingestion into the memory system.
"""

from friday_memory.ingestion.chunker import (
    Chunk,
    ChunkingStrategy,
    SemanticChunker,
    SemanticChunkerConfig,
)
from friday_memory.ingestion.pipeline import (
    DocumentChunk,
    DocumentIngestionPipeline,
    IngestedDocument,
)
from friday_memory.ingestion.tool_ingester import (
    IngestionResult,
    ToolIngestionPolicy,
    ToolOutputIngester,
    ToolOutputIngesterConfig,
)
from friday_memory.ingestion.large_file_processor import (
    ChunkSummary,
    LargeFileProcessor,
    LargeFileProcessorConfig,
    ProcessingResult,
    RawChunk,
    SmartFileLLMConfig,
    SmartFilePromptsConfig,
)

__all__ = [
    # Chunking
    "Chunk",
    "ChunkingStrategy",
    "SemanticChunker",
    "SemanticChunkerConfig",
    # Pipeline
    "DocumentIngestionPipeline",
    "DocumentChunk",
    "IngestedDocument",
    # Tool Ingestion
    "IngestionResult",
    "ToolIngestionPolicy",
    "ToolOutputIngester",
    "ToolOutputIngesterConfig",
    # Large File Processing
    "LargeFileProcessor",
    "LargeFileProcessorConfig",
    "ProcessingResult",
    "RawChunk",
    "ChunkSummary",
    "SmartFileLLMConfig",
    "SmartFilePromptsConfig",
]
