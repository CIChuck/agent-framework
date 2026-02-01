"""
Large File Processor.

Handles processing of large files through a three-stage pipeline:
1. Chunking - Split file into manageable pieces (structure-aware for code)
2. Summarization - Summarize each chunk with running context
3. Synthesis - Combine chunk summaries into coherent overview

Supports separate LLM configurations for summarization and synthesis,
allowing cost optimization (cheap/fast for chunks, capable for synthesis).

Ref: docs/build-plan/large-file-processor-plan.md
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from friday_memory.ingestion.chunker import Chunk, SemanticChunker, SemanticChunkerConfig
from friday_memory.models import ProvenanceMetadata

if TYPE_CHECKING:
    from friday_llm.service import LiteLLMService
    from friday_memory.controller.memory_controller import MemoryController

logger = logging.getLogger(__name__)


# =============================================================================
# DEFAULT PROMPTS
# =============================================================================

DEFAULT_PROSE_SUMMARIZATION = """Summarize this section of a larger document. Extract key points and entities.

File: {file_path}
Context: {description}
Previous context: {running_summary}

SECTION {index}/{total}:
{chunk_text}

Provide a concise summary (2-3 sentences) focusing on:
1. Main ideas and key facts
2. Important entities mentioned (people, places, concepts)
3. How this section relates to previous context

Respond with JSON:
{{
    "summary": "The concise summary text",
    "entities": ["entity1", "entity2"],
    "key_points": ["point1", "point2"]
}}"""

DEFAULT_CODE_SUMMARIZATION = """Summarize the purpose and behavior of this code section.

File: {file_path}
Section type: {chunk_type}
Symbols defined: {symbols_defined}
External references: {symbols_referenced}

CODE:
{chunk_text}

Describe what this code does in 2-3 sentences.
Focus on INTENT (what it accomplishes) not syntax.

Respond with JSON:
{{
    "summary": "What this code does",
    "purpose": "Why this code exists",
    "dependencies": ["external symbols or modules used"]
}}"""

DEFAULT_PROSE_SYNTHESIS = """Synthesize these section summaries into a comprehensive overview.

Document: {file_path}
Context: {description}

SECTION SUMMARIES:
{numbered_summaries}

Create a unified summary that:
1. Captures the overall purpose and main content
2. Highlights key themes or topics covered
3. Notes important entities or concepts
4. Preserves critical details that would be useful for future reference

Respond with JSON:
{{
    "summary": "Comprehensive overview paragraph (3-5 sentences)",
    "key_themes": ["theme1", "theme2"],
    "entities": ["entity1", "entity2"],
    "insights": ["insight1", "insight2"]
}}"""

DEFAULT_CODE_SYNTHESIS = """Synthesize these code section summaries into an architectural overview.

File: {file_path}
Context: {description}

SYMBOL TABLE:
{symbol_table}

SECTION SUMMARIES:
{numbered_summaries}

Create a unified overview that:
1. Describes the overall purpose of this code file
2. Explains the main components and their relationships
3. Notes key dependencies and external interactions
4. Highlights important patterns or design decisions

Respond with JSON:
{{
    "overview": "What this file does overall (2-3 sentences)",
    "components": ["component1: description", "component2: description"],
    "architecture_notes": "How components work together",
    "dependencies": ["dep1", "dep2"],
    "key_patterns": ["pattern1", "pattern2"]
}}"""


# =============================================================================
# CONFIGURATION DATACLASSES
# =============================================================================


@dataclass
class SmartFileLLMConfig:
    """LLM configuration for a processing stage."""

    model: str
    api_base: str | None = None
    api_key: str | None = None
    temperature: float = 0.3
    max_tokens: int = 500
    timeout_seconds: float = 30.0


@dataclass
class SmartFilePromptsConfig:
    """Configurable prompts for file processing."""

    prose_summarization: str = DEFAULT_PROSE_SUMMARIZATION
    code_summarization: str = DEFAULT_CODE_SUMMARIZATION
    prose_synthesis: str = DEFAULT_PROSE_SYNTHESIS
    code_synthesis: str = DEFAULT_CODE_SYNTHESIS


@dataclass
class LargeFileProcessorConfig:
    """Configuration for the large file processor."""

    # Size threshold (chars) for triggering chunked processing
    auto_chunk_threshold_chars: int = 50000

    # Chunking settings
    chunk_size: int = 512  # Target tokens per chunk
    chunk_overlap: int = 50  # Overlap tokens between chunks

    # LLM configs (None = use fallback)
    summarizer_llm: SmartFileLLMConfig | None = None
    synthesizer_llm: SmartFileLLMConfig | None = None

    # Prompts (None = use defaults)
    prompts: SmartFilePromptsConfig | None = None

    # Code handling
    preserve_code_structure: bool = True
    extract_symbols: bool = True
    supported_code_extensions: list[str] = field(
        default_factory=lambda: [".py", ".rs", ".js", ".ts", ".go", ".java", ".c", ".cpp", ".h"]
    )


# =============================================================================
# RESULT DATACLASSES
# =============================================================================


@dataclass
class ChunkSummary:
    """Summary result for a single chunk."""

    chunk_index: int
    summary: str
    entities: list[str] = field(default_factory=list)
    key_points: list[str] = field(default_factory=list)
    chunk_type: str | None = None
    symbols_defined: list[str] = field(default_factory=list)


@dataclass
class RawChunk:
    """A raw chunk of content for storage."""

    text: str
    index: int
    chunk_type: str | None = None
    start_line: int | None = None
    end_line: int | None = None


@dataclass
class ProcessingResult:
    """Result from processing a large file."""

    # Content for immediate context use
    content_for_context: str

    # Detailed chunk results
    chunk_summaries: list[ChunkSummary]

    # Raw chunks for verbatim storage
    raw_chunks: list[RawChunk]

    # Final synthesis
    synthesis: dict[str, Any]

    # Extracted entities for memory storage
    entities: list[str]

    # Processing metadata
    file_path: str
    file_type: str
    chunks_processed: int
    total_chars: int

    # Storage IDs (populated if stored to memory)
    stored_ids: list[str] = field(default_factory=list)


# =============================================================================
# MAIN PROCESSOR CLASS
# =============================================================================


class LargeFileProcessor:
    """
    Processes large files through chunk-summarize-synthesize pipeline.

    Supports:
    - Prose files (documents, articles) - semantic chunking
    - Code files (Python, etc.) - structure-aware chunking
    - Configurable LLMs for each stage
    - Memory storage integration

    Example:
        processor = LargeFileProcessor(
            fallback_llm=my_llm_service,
            config=LargeFileProcessorConfig(
                auto_chunk_threshold_chars=30000,
            ),
        )

        result = await processor.process(
            content=large_file_content,
            file_path="/path/to/file.py",
            file_type="code",
            language="python",
        )
    """

    def __init__(
        self,
        fallback_llm: "LiteLLMService",
        config: LargeFileProcessorConfig | None = None,
        memory_controller: "MemoryController | None" = None,
    ) -> None:
        """
        Initialize the processor.

        Args:
            fallback_llm: LLM service to use when stage-specific LLM not configured
            config: Processing configuration
            memory_controller: Optional memory controller for storage
        """
        self._fallback_llm = fallback_llm
        self._config = config or LargeFileProcessorConfig()
        self._memory = memory_controller

        # Prompts (use defaults if not configured)
        self._prompts = self._config.prompts or SmartFilePromptsConfig()

        # Create specialized LLM services if configured
        self._summarizer_llm = self._create_llm(self._config.summarizer_llm) or fallback_llm
        self._synthesizer_llm = self._create_llm(self._config.synthesizer_llm) or fallback_llm

    def _create_llm(self, config: SmartFileLLMConfig | None) -> "LiteLLMService | None":
        """Create an LLM service from config, or None if not configured."""
        if not config:
            return None

        # Import here to avoid circular imports
        from friday_llm.config import ResilienceConfig
        from friday_llm.service import LiteLLMService

        return LiteLLMService(
            model_name=config.model,
            api_key=config.api_key,
            api_base=config.api_base,
            resilience=ResilienceConfig(timeout_seconds=config.timeout_seconds),
        )

    async def process(
        self,
        content: str,
        file_path: str,
        file_type: str = "prose",
        language: str | None = None,
        description: str | None = None,
        store_to_memory: bool = False,
    ) -> ProcessingResult:
        """
        Process a large file through the pipeline.

        Args:
            content: File content to process
            file_path: Path to the file (for context)
            file_type: "prose", "code", or "data"
            language: Programming language (for code files)
            description: User-provided context about the file
            store_to_memory: Whether to store results to memory

        Returns:
            ProcessingResult with summaries, synthesis, and content
        """
        logger.info(f"Processing {file_type} file: {file_path} ({len(content)} chars)")

        if file_type == "code" and self._config.preserve_code_structure:
            result = await self._process_code(
                content=content,
                file_path=file_path,
                language=language or "unknown",
                description=description,
            )
        else:
            result = await self._process_prose(
                content=content,
                file_path=file_path,
                description=description,
            )

        # Store to memory if requested
        if store_to_memory and self._memory:
            stored_ids = await self._store_to_memory(result, file_path)
            result.stored_ids = stored_ids

        return result

    async def _process_prose(
        self,
        content: str,
        file_path: str,
        description: str | None,
    ) -> ProcessingResult:
        """
        Process prose/document content.

        Pipeline:
        1. Semantic chunking with overlap
        2. Sequential summarization with running context
        3. Final synthesis from all summaries
        """
        # Chunk the content
        chunker_config = SemanticChunkerConfig(
            chunk_size=self._config.chunk_size,
            chunk_overlap=self._config.chunk_overlap,
        )
        chunker = SemanticChunker(chunker_config)
        chunks = chunker.chunk(content)

        if not chunks:
            return ProcessingResult(
                content_for_context=content[:5000] + "..." if len(content) > 5000 else content,
                chunk_summaries=[],
                raw_chunks=[],
                synthesis={"summary": "Empty document"},
                entities=[],
                file_path=file_path,
                file_type="prose",
                chunks_processed=0,
                total_chars=len(content),
            )

        # Capture raw chunks for storage
        raw_chunks = [
            RawChunk(
                text=chunk.text,
                index=chunk.index,
                chunk_type="prose",
            )
            for chunk in chunks
        ]

        # Summarize chunks
        summaries = await self._summarize_prose_chunks(
            chunks=chunks,
            file_path=file_path,
            description=description,
        )

        # Synthesize final summary
        synthesis = await self._synthesize_prose(
            summaries=summaries,
            file_path=file_path,
            description=description,
        )

        # Collect all entities
        all_entities = set()
        for summary in summaries:
            all_entities.update(summary.entities)
        if "entities" in synthesis:
            all_entities.update(synthesis["entities"])

        # Build context content
        context_content = self._build_context_content(
            file_path=file_path,
            synthesis=synthesis,
            summaries=summaries,
            file_type="prose",
        )

        return ProcessingResult(
            content_for_context=context_content,
            chunk_summaries=summaries,
            raw_chunks=raw_chunks,
            synthesis=synthesis,
            entities=list(all_entities),
            file_path=file_path,
            file_type="prose",
            chunks_processed=len(chunks),
            total_chars=len(content),
        )

    async def _process_code(
        self,
        content: str,
        file_path: str,
        language: str,
        description: str | None,
    ) -> ProcessingResult:
        """
        Process code content with structure-aware chunking.

        Pipeline:
        1. AST-based chunking (or fallback to regex)
        2. Per-chunk summarization with symbol context
        3. Architectural synthesis with symbol table
        """
        # Import code chunker
        from friday_tools.filesystem.code_chunker import (
            CodeChunkerFactory,
            SymbolTable,
        )

        # Get extension from file path
        extension = "." + file_path.rsplit(".", 1)[-1] if "." in file_path else ".txt"

        # Get appropriate chunker
        chunker = CodeChunkerFactory.for_extension(extension)
        code_chunks = chunker.chunk(content)

        if not code_chunks:
            return ProcessingResult(
                content_for_context=content[:5000] + "..." if len(content) > 5000 else content,
                chunk_summaries=[],
                raw_chunks=[],
                synthesis={"overview": "Empty file"},
                entities=[],
                file_path=file_path,
                file_type="code",
                chunks_processed=0,
                total_chars=len(content),
            )

        # Capture raw chunks for storage (with code-specific metadata)
        raw_chunks = [
            RawChunk(
                text=chunk.text,
                index=chunk.index,
                chunk_type=chunk.chunk_type.value if hasattr(chunk.chunk_type, "value") else str(chunk.chunk_type),
                start_line=chunk.start_line,
                end_line=chunk.end_line,
            )
            for chunk in code_chunks
        ]

        # Extract symbol table
        symbol_table = chunker.extract_symbols(content)

        # Summarize code chunks
        summaries = await self._summarize_code_chunks(
            chunks=code_chunks,
            file_path=file_path,
            description=description,
        )

        # Synthesize architectural overview
        synthesis = await self._synthesize_code(
            summaries=summaries,
            symbol_table=symbol_table,
            file_path=file_path,
            description=description,
        )

        # Collect entities (class names, function names, etc.)
        all_entities = set()
        all_entities.update(symbol_table.classes)
        all_entities.update(symbol_table.functions)
        for summary in summaries:
            all_entities.update(summary.symbols_defined)

        # Build context content
        context_content = self._build_context_content(
            file_path=file_path,
            synthesis=synthesis,
            summaries=summaries,
            file_type="code",
            symbol_table=symbol_table,
        )

        return ProcessingResult(
            content_for_context=context_content,
            chunk_summaries=summaries,
            raw_chunks=raw_chunks,
            synthesis=synthesis,
            entities=list(all_entities),
            file_path=file_path,
            file_type="code",
            chunks_processed=len(code_chunks),
            total_chars=len(content),
        )

    async def _summarize_prose_chunks(
        self,
        chunks: list[Chunk],
        file_path: str,
        description: str | None,
    ) -> list[ChunkSummary]:
        """Summarize prose chunks with running context."""
        summaries: list[ChunkSummary] = []
        running_summary = "Beginning of document."

        for chunk in chunks:
            prompt = self._render_prompt(
                self._prompts.prose_summarization,
                file_path=file_path,
                description=description or "No context provided",
                running_summary=running_summary,
                index=chunk.index + 1,
                total=chunk.total,
                chunk_text=chunk.text[:4000],  # Limit chunk size for prompt
            )

            try:
                response = await self._summarizer_llm.chat_completion(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self._config.summarizer_llm.temperature if self._config.summarizer_llm else 0.3,
                    max_tokens=self._config.summarizer_llm.max_tokens if self._config.summarizer_llm else 500,
                )

                parsed = self._parse_json_response(response.content)

                summary = ChunkSummary(
                    chunk_index=chunk.index,
                    summary=parsed.get("summary", ""),
                    entities=parsed.get("entities", []),
                    key_points=parsed.get("key_points", []),
                )
                summaries.append(summary)

                # Update running context
                running_summary = summary.summary

            except Exception as e:
                logger.warning(f"Failed to summarize chunk {chunk.index}: {e}")
                # Add placeholder summary
                summaries.append(
                    ChunkSummary(
                        chunk_index=chunk.index,
                        summary=f"[Chunk {chunk.index + 1}: summarization failed]",
                    )
                )

        return summaries

    async def _summarize_code_chunks(
        self,
        chunks: list,  # list[CodeChunk]
        file_path: str,
        description: str | None,
    ) -> list[ChunkSummary]:
        """Summarize code chunks with symbol context."""
        summaries: list[ChunkSummary] = []

        for chunk in chunks:
            prompt = self._render_prompt(
                self._prompts.code_summarization,
                file_path=file_path,
                chunk_type=chunk.chunk_type.value if hasattr(chunk.chunk_type, "value") else str(chunk.chunk_type),
                symbols_defined=", ".join(chunk.symbols_defined) if chunk.symbols_defined else "none",
                symbols_referenced=", ".join(chunk.symbols_referenced[:10]) if chunk.symbols_referenced else "none",
                chunk_text=chunk.text[:4000],
            )

            try:
                response = await self._summarizer_llm.chat_completion(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self._config.summarizer_llm.temperature if self._config.summarizer_llm else 0.3,
                    max_tokens=self._config.summarizer_llm.max_tokens if self._config.summarizer_llm else 500,
                )

                parsed = self._parse_json_response(response.content)

                summary = ChunkSummary(
                    chunk_index=chunk.index,
                    summary=parsed.get("summary", ""),
                    key_points=[parsed.get("purpose", "")] if parsed.get("purpose") else [],
                    chunk_type=chunk.chunk_type.value if hasattr(chunk.chunk_type, "value") else str(chunk.chunk_type),
                    symbols_defined=chunk.symbols_defined,
                )
                summaries.append(summary)

            except Exception as e:
                logger.warning(f"Failed to summarize code chunk {chunk.index}: {e}")
                summaries.append(
                    ChunkSummary(
                        chunk_index=chunk.index,
                        summary=f"[{chunk.chunk_type}: {', '.join(chunk.symbols_defined[:3])}]",
                        chunk_type=chunk.chunk_type.value if hasattr(chunk.chunk_type, "value") else str(chunk.chunk_type),
                        symbols_defined=chunk.symbols_defined,
                    )
                )

        return summaries

    async def _synthesize_prose(
        self,
        summaries: list[ChunkSummary],
        file_path: str,
        description: str | None,
    ) -> dict[str, Any]:
        """Synthesize all chunk summaries into a unified overview."""
        # Build numbered summaries
        numbered = "\n".join(
            f"{i + 1}. {s.summary}" for i, s in enumerate(summaries)
        )

        prompt = self._render_prompt(
            self._prompts.prose_synthesis,
            file_path=file_path,
            description=description or "No context provided",
            numbered_summaries=numbered,
        )

        try:
            response = await self._synthesizer_llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=self._config.synthesizer_llm.temperature if self._config.synthesizer_llm else 0.3,
                max_tokens=self._config.synthesizer_llm.max_tokens if self._config.synthesizer_llm else 1000,
            )

            return self._parse_json_response(response.content)

        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            # Return basic synthesis from summaries
            return {
                "summary": " ".join(s.summary for s in summaries[:3]),
                "key_themes": [],
                "entities": [],
            }

    async def _synthesize_code(
        self,
        summaries: list[ChunkSummary],
        symbol_table: Any,  # SymbolTable
        file_path: str,
        description: str | None,
    ) -> dict[str, Any]:
        """Synthesize code summaries into architectural overview."""
        # Build numbered summaries
        numbered = "\n".join(
            f"{i + 1}. [{s.chunk_type}] {s.summary}" for i, s in enumerate(summaries)
        )

        # Format symbol table
        symbol_str = (
            f"Classes: {', '.join(symbol_table.classes) or 'none'}\n"
            f"Functions: {', '.join(symbol_table.functions) or 'none'}\n"
            f"Imports: {', '.join(symbol_table.imports[:10]) or 'none'}"
        )

        prompt = self._render_prompt(
            self._prompts.code_synthesis,
            file_path=file_path,
            description=description or "No context provided",
            symbol_table=symbol_str,
            numbered_summaries=numbered,
        )

        try:
            response = await self._synthesizer_llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=self._config.synthesizer_llm.temperature if self._config.synthesizer_llm else 0.3,
                max_tokens=self._config.synthesizer_llm.max_tokens if self._config.synthesizer_llm else 1000,
            )

            return self._parse_json_response(response.content)

        except Exception as e:
            logger.error(f"Code synthesis failed: {e}")
            return {
                "overview": f"Code file with {len(symbol_table.classes)} classes and {len(symbol_table.functions)} functions.",
                "components": [],
                "dependencies": symbol_table.imports[:5],
            }

    async def _check_existing_storage(self, file_path: str) -> bool:
        """
        Check if a file has already been stored to memory.

        Args:
            file_path: Path of the file to check

        Returns:
            True if file already exists in memory, False otherwise
        """
        if not self._memory:
            return False

        try:
            # Query vector store for existing file synthesis
            if hasattr(self._memory, "vector") and hasattr(self._memory.vector, "get_all"):
                results = await self._memory.vector.get_all(
                    where={"source": file_path, "type": "file_synthesis"},
                    limit=1,
                )

                if results and len(results.get("documents", [])) > 0:
                    return True

        except Exception as e:
            logger.warning(f"Failed to check existing storage for {file_path}: {e}")

        return False

    async def _store_to_memory(
        self,
        result: ProcessingResult,
        file_path: str,
    ) -> list[str]:
        """
        Store processing results to memory controller.

        Stores in "full" mode with deduplication:
        1. Raw chunks - verbatim content for RAG retrieval
        2. Chunk summaries - semantic understanding
        3. Synthesis - high-level overview

        Checks for existing entries before storing to prevent duplicates.
        """
        if not self._memory:
            return []

        stored_ids: list[str] = []
        now = datetime.now()

        # ====================================================================
        # DEDUPLICATION CHECK
        # ====================================================================
        # Check if this file has already been stored
        existing_synthesis = await self._check_existing_storage(file_path)
        if existing_synthesis:
            logger.info(f"File {file_path} already in memory - skipping storage")
            return []

        # Create provenance for all stored items
        provenance = ProvenanceMetadata(
            source_id=f"file:{file_path}",
            source_type="ingested_file",
            confidence=0.9,
            created_at=now,
        )

        # 1. Store raw chunks for verbatim RAG retrieval
        if result.raw_chunks:
            raw_texts = []
            raw_metadatas = []
            for chunk in result.raw_chunks:
                raw_texts.append(chunk.text)
                raw_metadatas.append({
                    "type": "raw_chunk",
                    "source": file_path,
                    "file_type": result.file_type,
                    "chunk_index": chunk.index,
                    "chunk_type": chunk.chunk_type or "unknown",
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                })

            # Use store_documents_batch if available, otherwise store individually
            if hasattr(self._memory, "store_documents_batch"):
                raw_ids = await self._memory.store_documents_batch(
                    texts=raw_texts,
                    metadatas=raw_metadatas,
                    protected=True,
                )
                stored_ids.extend(raw_ids)
            else:
                # Fallback to individual storage
                for text, metadata in zip(raw_texts, raw_metadatas):
                    doc_id = await self._memory.store_document(
                        text=text,
                        metadata=metadata,
                        protected=True,
                    )
                    stored_ids.append(doc_id)

            logger.info(f"Stored {len(result.raw_chunks)} raw chunks for {file_path}")

        # 2. Store synthesis as main document
        synthesis_text = result.synthesis.get("summary") or result.synthesis.get("overview", "")
        if synthesis_text:
            doc_id = await self._memory.store_document(
                text=synthesis_text,
                metadata={
                    "source": file_path,
                    "type": "file_synthesis",
                    "file_type": result.file_type,
                    "chunks_processed": result.chunks_processed,
                },
                protected=True,
            )
            stored_ids.append(doc_id)

        # 3. Store chunk summaries as insights
        items_to_store = []
        for summary in result.chunk_summaries:
            if summary.summary and not summary.summary.startswith("["):
                items_to_store.append(
                    (
                        summary.summary,
                        {
                            "type": "chunk_summary",
                            "source": file_path,
                            "chunk_index": summary.chunk_index,
                            "chunk_type": summary.chunk_type or "unknown",
                            "entities_mentioned": ";".join(summary.entities) if summary.entities else "",
                        },
                    )
                )

        if items_to_store:
            count = await self._memory.store_insights_batch_with_metadata(
                items=items_to_store,
                provenance=provenance,
            )
            stored_ids.extend([f"insight_{i}" for i in range(count)])

        logger.info(f"Stored {len(stored_ids)} total items to memory for {file_path}")
        return stored_ids

    def _build_context_content(
        self,
        file_path: str,
        synthesis: dict[str, Any],
        summaries: list[ChunkSummary],
        file_type: str,
        symbol_table: Any = None,
    ) -> str:
        """Build formatted content for LLM context."""
        lines = [f"## File Summary: {file_path}"]
        lines.append("")

        # Main synthesis
        if file_type == "code":
            overview = synthesis.get("overview", "")
            if overview:
                lines.append(f"**Overview:** {overview}")
                lines.append("")

            components = synthesis.get("components", [])
            if components:
                lines.append("**Components:**")
                for comp in components[:5]:
                    lines.append(f"- {comp}")
                lines.append("")

            if symbol_table:
                lines.append("**Symbols:**")
                if symbol_table.classes:
                    lines.append(f"- Classes: {', '.join(symbol_table.classes[:5])}")
                if symbol_table.functions:
                    lines.append(f"- Functions: {', '.join(symbol_table.functions[:10])}")
                lines.append("")

        else:
            summary = synthesis.get("summary", "")
            if summary:
                lines.append(f"**Summary:** {summary}")
                lines.append("")

            themes = synthesis.get("key_themes", [])
            if themes:
                lines.append(f"**Key themes:** {', '.join(themes)}")
                lines.append("")

            entities = synthesis.get("entities", [])
            if entities:
                lines.append(f"**Entities:** {', '.join(entities)}")
                lines.append("")

        # Section summaries (abbreviated)
        if summaries:
            lines.append(f"**Sections ({len(summaries)} chunks):**")
            for s in summaries[:5]:
                prefix = f"[{s.chunk_type}] " if s.chunk_type else ""
                lines.append(f"- {prefix}{s.summary[:100]}...")
            if len(summaries) > 5:
                lines.append(f"- ... and {len(summaries) - 5} more sections")

        return "\n".join(lines)

    def _render_prompt(self, template: str, **kwargs: Any) -> str:
        """Render a prompt template with provided values."""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing template placeholder: {e}")
            return template

    def _parse_json_response(self, content: str | None) -> dict[str, Any]:
        """Parse JSON from LLM response, handling markdown code blocks and plain text."""
        if not content:
            return {}

        # Try to extract JSON from markdown code block
        text = content.strip()
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                text = text[start:end].strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON object in text
            brace_start = text.find("{")
            brace_end = text.rfind("}")
            if brace_start >= 0 and brace_end > brace_start:
                try:
                    return json.loads(text[brace_start : brace_end + 1])
                except json.JSONDecodeError:
                    pass

            # Fallback: LLM returned plain text instead of JSON
            # Use the text as the summary - this is common with some models
            plain_text = content.strip()
            if plain_text and len(plain_text) > 10:
                logger.debug(f"LLM returned plain text summary instead of JSON, using as-is")
                return {"summary": plain_text, "entities": [], "key_points": []}

            logger.warning(f"Failed to parse JSON from response: {text[:200]}")
            return {}
