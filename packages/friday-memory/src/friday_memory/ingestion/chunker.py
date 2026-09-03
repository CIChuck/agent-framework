# mypy: ignore-errors
"""
Semantic Chunking for Document Ingestion.

Splits documents into semantically coherent chunks for better
vector retrieval precision and token efficiency.

Strategies:
- FIXED_SIZE: Split at fixed token/character counts
- SENTENCE: Split at sentence boundaries
- PARAGRAPH: Split at paragraph boundaries
- RECURSIVE: Try paragraph → sentence → fixed (recommended)

Ref: docs/archive/superseded/copilot-promotion/build-plan.md, Issue 3
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ChunkingStrategy(str, Enum):
    """Available chunking strategies."""

    FIXED_SIZE = "fixed_size"  # Split at token count
    SENTENCE = "sentence"  # Split at sentence boundaries
    PARAGRAPH = "paragraph"  # Split at paragraph boundaries
    RECURSIVE = "recursive"  # Try paragraph, fall back to sentence, then fixed


@dataclass
class Chunk:
    """A chunk of text with metadata."""

    text: str
    index: int
    total: int
    has_overlap: bool = False
    source_start: int | None = None  # Character offset in original
    source_end: int | None = None


@dataclass
class SemanticChunkerConfig:
    """Configuration for semantic chunking."""

    strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE
    chunk_size: int = 512  # Target tokens per chunk
    chunk_overlap: int = 50  # Overlap tokens between chunks
    min_chunk_size: int = 100  # Don't create tiny chunks
    max_chunk_size: int = 1024  # Hard limit per chunk

    # Sentence detection
    sentence_endings: list[str] = field(
        default_factory=lambda: [". ", "! ", "? ", ".\n", "!\n", "?\n"]
    )

    # Paragraph detection
    paragraph_separators: list[str] = field(
        default_factory=lambda: ["\n\n", "\n\r\n", "\r\n\r\n"]
    )

    # Structure preservation
    preserve_headers: bool = True  # Keep markdown headers with content
    preserve_code_blocks: bool = True  # Don't split code blocks


class SemanticChunker:
    """
    Splits documents into semantically coherent chunks.

    Designed for:
    - Better vector retrieval precision
    - Token-efficient storage
    - Context-preserving overlap

    Example:
        chunker = SemanticChunker()
        chunks = chunker.chunk("Long document text...")

        for chunk in chunks:
            print(f"Chunk {chunk.index}/{chunk.total}: {chunk.text[:50]}...")
    """

    # Rough token estimation: ~4 chars per token for English text
    CHARS_PER_TOKEN = 4

    def __init__(self, config: SemanticChunkerConfig | None = None) -> None:
        """
        Initialize the chunker.

        Args:
            config: Chunking configuration (uses defaults if None)
        """
        self._config = config or SemanticChunkerConfig()

    @property
    def config(self) -> SemanticChunkerConfig:
        """Access the chunking configuration."""
        return self._config

    def chunk(self, text: str) -> list[Chunk]:
        """
        Split text into chunks using configured strategy.

        Args:
            text: The text to chunk

        Returns:
            List of Chunk objects with text and metadata
        """
        if not text or not text.strip():
            return []

        # Check if text is small enough to be a single chunk
        if self._estimate_tokens(text) <= self._config.chunk_size:
            return [Chunk(text=text.strip(), index=0, total=1)]

        if self._config.strategy == ChunkingStrategy.RECURSIVE:
            return self._chunk_recursive(text)
        elif self._config.strategy == ChunkingStrategy.SENTENCE:
            return self._chunk_by_sentences(text)
        elif self._config.strategy == ChunkingStrategy.PARAGRAPH:
            return self._chunk_by_paragraphs(text)
        else:
            return self._chunk_fixed_size(text)

    def chunk_with_metadata(
        self, text: str, base_metadata: dict[str, Any] | None = None
    ) -> list[tuple[str, dict[str, Any]]]:
        """
        Chunk text and return with metadata for each chunk.

        Convenience method for preparing chunks for vector storage.

        Args:
            text: The text to chunk
            base_metadata: Base metadata to include in each chunk's metadata

        Returns:
            List of (chunk_text, metadata) tuples ready for storage
        """
        chunks = self.chunk(text)
        results = []

        for chunk in chunks:
            metadata = {
                "chunk_index": chunk.index,
                "total_chunks": chunk.total,
                "has_overlap": chunk.has_overlap,
            }
            if base_metadata:
                metadata.update(base_metadata)
            results.append((chunk.text, metadata))

        return results

    def _chunk_recursive(self, text: str) -> list[Chunk]:
        """
        Recursive chunking: try paragraph → sentence → fixed.

        Algorithm:
        1. Split by paragraphs
        2. If paragraph > max_chunk_size, split by sentences
        3. If sentence > max_chunk_size, split by fixed size
        4. Merge small consecutive chunks up to chunk_size
        5. Add overlap between final chunks
        """
        raw_chunks: list[str] = []
        paragraphs = self._split_paragraphs(text)

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_tokens = self._estimate_tokens(para)

            if para_tokens <= self._config.chunk_size:
                # Paragraph fits in one chunk
                raw_chunks.append(para)
            elif para_tokens <= self._config.max_chunk_size:
                # Paragraph is acceptable but large - keep as is
                raw_chunks.append(para)
            else:
                # Paragraph too large, split by sentences
                sentences = self._split_sentences(para)
                current_chunk: list[str] = []
                current_size = 0

                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue

                    sent_tokens = self._estimate_tokens(sentence)

                    if sent_tokens > self._config.max_chunk_size:
                        # Sentence too large, force split
                        if current_chunk:
                            raw_chunks.append(" ".join(current_chunk))
                            current_chunk = []
                            current_size = 0
                        # Split the oversized sentence
                        raw_chunks.extend(self._force_split(sentence))
                    elif current_size + sent_tokens > self._config.chunk_size:
                        # Would exceed chunk size, start new chunk
                        if current_chunk:
                            raw_chunks.append(" ".join(current_chunk))
                        current_chunk = [sentence]
                        current_size = sent_tokens
                    else:
                        current_chunk.append(sentence)
                        current_size += sent_tokens

                if current_chunk:
                    raw_chunks.append(" ".join(current_chunk))

        # Merge small chunks
        merged = self._merge_small_chunks(raw_chunks)

        # Add overlap
        return self._add_overlap(merged)

    def _chunk_by_paragraphs(self, text: str) -> list[Chunk]:
        """Split by paragraph boundaries."""
        paragraphs = self._split_paragraphs(text)
        raw_chunks = [p.strip() for p in paragraphs if p.strip()]

        # Handle oversized paragraphs
        processed: list[str] = []
        for para in raw_chunks:
            if self._estimate_tokens(para) > self._config.max_chunk_size:
                # Fall back to sentence splitting
                sentences = self._split_sentences(para)
                current_chunk: list[str] = []
                current_size = 0
                for sent in sentences:
                    sent_tokens = self._estimate_tokens(sent)
                    if current_size + sent_tokens > self._config.chunk_size:
                        if current_chunk:
                            processed.append(" ".join(current_chunk))
                        current_chunk = [sent]
                        current_size = sent_tokens
                    else:
                        current_chunk.append(sent)
                        current_size += sent_tokens
                if current_chunk:
                    processed.append(" ".join(current_chunk))
            else:
                processed.append(para)

        merged = self._merge_small_chunks(processed)
        return self._add_overlap(merged)

    def _chunk_by_sentences(self, text: str) -> list[Chunk]:
        """Split by sentence boundaries."""
        sentences = self._split_sentences(text)
        raw_chunks: list[str] = []
        current_chunk: list[str] = []
        current_size = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sent_tokens = self._estimate_tokens(sentence)

            if sent_tokens > self._config.max_chunk_size:
                # Oversized sentence - force split
                if current_chunk:
                    raw_chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_size = 0
                raw_chunks.extend(self._force_split(sentence))
            elif current_size + sent_tokens > self._config.chunk_size:
                if current_chunk:
                    raw_chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_size = sent_tokens
            else:
                current_chunk.append(sentence)
                current_size += sent_tokens

        if current_chunk:
            raw_chunks.append(" ".join(current_chunk))

        return self._add_overlap(raw_chunks)

    def _chunk_fixed_size(self, text: str) -> list[Chunk]:
        """Split at fixed character counts."""
        char_limit = self._config.chunk_size * self.CHARS_PER_TOKEN
        raw_chunks: list[str] = []

        start = 0
        while start < len(text):
            end = min(start + char_limit, len(text))
            chunk = text[start:end].strip()
            if chunk:
                raw_chunks.append(chunk)
            start = end

        return self._add_overlap(raw_chunks)

    def _split_paragraphs(self, text: str) -> list[str]:
        """Split text by paragraph separators."""
        # Try each separator in order of preference
        for sep in self._config.paragraph_separators:
            if sep in text:
                return text.split(sep)
        # No paragraph separators found, treat as single paragraph
        return [text]

    def _split_sentences(self, text: str) -> list[str]:
        """Split text by sentence boundaries."""
        # Use regex for more robust sentence splitting
        # This pattern matches sentence-ending punctuation followed by whitespace or EOL
        pattern = r"(?<=[.!?])\s+"
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if s.strip()]

    def _force_split(self, text: str) -> list[str]:
        """Force split oversized text at character boundaries."""
        char_limit = self._config.max_chunk_size * self.CHARS_PER_TOKEN
        chunks: list[str] = []

        start = 0
        while start < len(text):
            end = min(start + char_limit, len(text))

            # Try to break at word boundary
            if end < len(text):
                space_pos = text.rfind(" ", start, end)
                if space_pos > start + (char_limit // 2):
                    end = space_pos + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end

        return chunks

    def _merge_small_chunks(self, chunks: list[str]) -> list[str]:
        """Merge consecutive small chunks up to chunk_size."""
        if not chunks:
            return []

        merged: list[str] = []
        current_chunk: list[str] = []
        current_size = 0

        for chunk in chunks:
            chunk_tokens = self._estimate_tokens(chunk)

            if current_size + chunk_tokens <= self._config.chunk_size:
                current_chunk.append(chunk)
                current_size += chunk_tokens
            else:
                if current_chunk:
                    merged.append("\n\n".join(current_chunk))
                current_chunk = [chunk]
                current_size = chunk_tokens

        if current_chunk:
            merged.append("\n\n".join(current_chunk))

        return merged

    def _add_overlap(self, chunks: list[str]) -> list[Chunk]:
        """Add overlapping context between chunks."""
        if len(chunks) <= 1:
            return [
                Chunk(text=c.strip(), index=i, total=len(chunks))
                for i, c in enumerate(chunks)
                if c.strip()
            ]

        result: list[Chunk] = []
        overlap_chars = self._config.chunk_overlap * self.CHARS_PER_TOKEN

        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue

            # Get overlap from previous chunk (suffix)
            prefix = ""
            if i > 0 and overlap_chars > 0:
                prev_text = chunks[i - 1]
                if len(prev_text) > overlap_chars:
                    prefix = "..." + prev_text[-overlap_chars:].strip() + " "
                elif prev_text:
                    prefix = "..." + prev_text.strip() + " "

            # Get overlap from next chunk (prefix)
            suffix = ""
            if i < len(chunks) - 1 and overlap_chars > 0:
                next_text = chunks[i + 1]
                if len(next_text) > overlap_chars:
                    suffix = " " + next_text[:overlap_chars].strip() + "..."
                elif next_text:
                    suffix = " " + next_text.strip() + "..."

            # Build chunk with overlap
            chunk_text = chunk.strip()
            if prefix or suffix:
                chunk_text = prefix + chunk_text + suffix

            result.append(
                Chunk(
                    text=chunk_text,
                    index=len(result),
                    total=len(chunks),
                    has_overlap=bool(prefix or suffix),
                )
            )

        # Update total count after filtering empty chunks
        for chunk in result:
            chunk.total = len(result)

        return result

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough: 4 chars per token for English)."""
        return len(text) // self.CHARS_PER_TOKEN
