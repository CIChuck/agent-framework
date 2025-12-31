"""
Document Ingestion Pipeline.
Handles file parsing, cleaning, chunking, and metadata extraction.

Ref: Batch 1 Specification, Section 4
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from friday_memory.models import ProvenanceMetadata


@dataclass
class DocumentChunk:
    """Represents a chunk of text with metadata."""

    id: str
    text: str
    metadata: dict[str, Any]
    provenance: ProvenanceMetadata


@dataclass
class IngestedDocument:
    """Result of document ingestion."""

    source_path: str
    document_id: str
    chunks: list[DocumentChunk] = field(default_factory=list)
    total_characters: int = 0
    total_chunks: int = 0


class DocumentIngestionPipeline:
    """
    Pipeline for ingesting documents into the memory system.

    Responsibilities:
    - File parsing (text extraction)
    - Text chunking with overlap
    - Metadata extraction
    - Provenance attachment

    Currently supports: .txt, .md, .py, .json, .yaml, .yml
    """

    # Supported file extensions
    SUPPORTED_EXTENSIONS = {".txt", ".md", ".py", ".json", ".yaml", ".yml", ".html", ".css", ".js", ".ts"}

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 50,
        author_id: str = "ingestion_pipeline",
    ) -> None:
        """
        Initialize the ingestion pipeline.

        Args:
            chunk_size: Target number of characters per chunk
            overlap: Number of characters to overlap between chunks
            author_id: Default author ID for provenance
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.author_id = author_id

    def _generate_id(self) -> str:
        """Generate a unique ID."""
        return str(uuid.uuid4())

    def _read_file(self, path: Path) -> str:
        """Read file contents as text."""
        return path.read_text(encoding="utf-8")

    def _chunk_text(self, text: str) -> list[str]:
        """
        Split text into overlapping chunks.

        Uses a simple character-based chunking strategy that tries
        to break at sentence or paragraph boundaries when possible.
        """
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        chunks = []
        start = 0

        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size

            if end >= len(text):
                # Last chunk
                chunk = text[start:].strip()
                if chunk:
                    chunks.append(chunk)
                break

            # Try to find a good break point
            chunk_text = text[start:end]

            # Look for paragraph break
            para_break = chunk_text.rfind("\n\n")
            if para_break > self.chunk_size // 2:
                end = start + para_break + 2
            else:
                # Look for sentence break
                for sep in [". ", "! ", "? ", "\n"]:
                    sent_break = chunk_text.rfind(sep)
                    if sent_break > self.chunk_size // 2:
                        end = start + sent_break + len(sep)
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start with overlap
            start = end - self.overlap
            if start <= 0:
                start = end

        return chunks

    def _extract_metadata(self, path: Path, text: str) -> dict[str, Any]:
        """Extract metadata from file."""
        return {
            "filename": path.name,
            "extension": path.suffix,
            "file_path": str(path),
            "file_size": path.stat().st_size if path.exists() else len(text),
            "ingested_at": datetime.now().isoformat(),
        }

    def ingest_text(
        self,
        text: str,
        source_id: str | None = None,
        source_name: str = "text_input",
        additional_metadata: dict[str, Any] | None = None,
    ) -> IngestedDocument:
        """
        Ingest raw text into chunks.

        Args:
            text: The text to ingest
            source_id: Optional source identifier
            source_name: Name for the text source
            additional_metadata: Extra metadata to attach

        Returns:
            IngestedDocument with chunks
        """
        doc_id = source_id or self._generate_id()
        chunks_text = self._chunk_text(text)

        chunks = []
        for i, chunk_text in enumerate(chunks_text):
            chunk_id = f"{doc_id}_chunk_{i}"

            provenance = ProvenanceMetadata(
                source_id=doc_id,
                source_type="document",
                confidence=1.0,
                author_id=self.author_id,
            )

            metadata = {
                "source_name": source_name,
                "chunk_index": i,
                "total_chunks": len(chunks_text),
                **(additional_metadata or {}),
            }

            chunks.append(
                DocumentChunk(
                    id=chunk_id,
                    text=chunk_text,
                    metadata=metadata,
                    provenance=provenance,
                )
            )

        return IngestedDocument(
            source_path=source_name,
            document_id=doc_id,
            chunks=chunks,
            total_characters=len(text),
            total_chunks=len(chunks),
        )

    def ingest_file(
        self,
        path: str | Path,
        additional_metadata: dict[str, Any] | None = None,
    ) -> IngestedDocument:
        """
        Ingest a file into chunks.

        Args:
            path: Path to the file
            additional_metadata: Extra metadata to attach

        Returns:
            IngestedDocument with chunks

        Raises:
            ValueError: If file type is not supported
            FileNotFoundError: If file doesn't exist
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {path.suffix}. "
                f"Supported: {self.SUPPORTED_EXTENSIONS}"
            )

        text = self._read_file(path)
        doc_id = self._generate_id()
        file_metadata = self._extract_metadata(path, text)

        chunks_text = self._chunk_text(text)
        chunks = []

        for i, chunk_text in enumerate(chunks_text):
            chunk_id = f"{doc_id}_chunk_{i}"

            provenance = ProvenanceMetadata(
                source_id=doc_id,
                source_type="document",
                confidence=1.0,
                author_id=self.author_id,
            )

            metadata = {
                **file_metadata,
                "chunk_index": i,
                "total_chunks": len(chunks_text),
                **(additional_metadata or {}),
            }

            chunks.append(
                DocumentChunk(
                    id=chunk_id,
                    text=chunk_text,
                    metadata=metadata,
                    provenance=provenance,
                )
            )

        return IngestedDocument(
            source_path=str(path),
            document_id=doc_id,
            chunks=chunks,
            total_characters=len(text),
            total_chunks=len(chunks),
        )

    def prepare_for_vector_store(
        self, document: IngestedDocument
    ) -> tuple[list[str], list[dict[str, Any]], list[str]]:
        """
        Prepare ingested document for VectorStoreAdapter.add_documents().

        Args:
            document: The ingested document

        Returns:
            Tuple of (texts, metadatas, ids) ready for vector store
        """
        texts = []
        metadatas = []
        ids = []

        for chunk in document.chunks:
            texts.append(chunk.text)
            ids.append(chunk.id)

            # Flatten provenance into metadata for storage
            metadata = {
                **chunk.metadata,
                "provenance_source_id": chunk.provenance.source_id,
                "provenance_source_type": chunk.provenance.source_type,
                "provenance_confidence": chunk.provenance.confidence,
                "provenance_author_id": chunk.provenance.author_id or "",
            }
            metadatas.append(metadata)

        return texts, metadatas, ids
