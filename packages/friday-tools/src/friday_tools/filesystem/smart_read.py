# mypy: ignore-errors
"""
Smart File Read Tool.

Intelligently reads files of any size by auto-detecting file type and size,
then routing to appropriate processing:
- Small files: Direct read, return full content
- Large files: Chunked processing with summarization and synthesis

Implements three-layer caching to avoid redundant processing:
1. Session cache (in-memory) - fastest, checked first
2. Memory check (vector store) - persistent across sessions
3. Store deduplication - prevents duplicate entries

Supports:
- Code files: Structure-aware chunking at function/class boundaries
- Prose files: Semantic chunking with overlap
- Data files: Treated as prose with appropriate parsing

Ref: docs/planning/build-plans/large-file-processor-plan.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from friday_tools.base import FridayTool, ToolResult
from friday_tools.sandbox import FilesystemSandbox

if TYPE_CHECKING:
    from friday_llm.service import LiteLLMService
    from friday_memory.controller.memory_controller import MemoryController
    from friday_memory.ingestion.large_file_processor import (
        LargeFileProcessorConfig,
    )

logger = logging.getLogger(__name__)


# File type detection
CODE_EXTENSIONS = {
    ".py",
    ".pyw",
    ".pyi",  # Python
    ".rs",  # Rust
    ".js",
    ".jsx",
    ".mjs",  # JavaScript
    ".ts",
    ".tsx",
    ".mts",  # TypeScript
    ".go",  # Go
    ".java",  # Java
    ".c",
    ".cpp",
    ".cc",
    ".h",
    ".hpp",  # C/C++
    ".cs",  # C#
    ".rb",  # Ruby
    ".php",  # PHP
    ".swift",  # Swift
    ".kt",
    ".kts",  # Kotlin
    ".scala",  # Scala
    ".r",  # R
    ".lua",  # Lua
    ".sh",
    ".bash",
    ".zsh",  # Shell
}

DATA_EXTENSIONS = {
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".csv",
    ".toml",
    ".ini",
    ".cfg",
}

BINARY_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
}


@dataclass
class CachedFileEntry:
    """Cached entry for a processed file."""

    file_path: str
    mtime: float
    file_type: str
    content_for_context: str
    synthesis: dict[str, Any]
    entities: list[str]
    chunks_processed: int
    total_chars: int
    stored_to_memory: bool = False


class SmartFileReadTool(FridayTool):
    """
    Intelligently read files of any size with multi-layer caching.

    Small files are returned in full. Large files are automatically
    chunked, summarized, and synthesized to fit within context limits.

    Caching layers (checked in order):
    1. Session cache - in-memory, keyed by (path, mtime)
    2. Memory check - query vector store for existing processing
    3. Full processing - chunk, summarize, synthesize, store

    Configuration is loaded from config.yaml smart_file section.
    Supports separate LLMs for summarization and synthesis.
    """

    name = "smart_read"
    description = (
        "Read and process files of any size. Small files return full content. "
        "Large files are automatically chunked, summarized, and synthesized. "
        "Results are cached to avoid redundant processing on repeated calls. "
        "Use 'store_to_memory=true' to save processed content for future reference."
    )
    category = "filesystem"
    tags = ["file", "read", "summarize", "ingest", "code"]

    class Input(BaseModel):
        """Input parameters for smart file reading."""

        path: str = Field(
            description="File path to read (absolute or relative to working directory)"
        )
        add_to_context: bool = Field(
            default=True, description="Return content/summary to conversation context"
        )
        store_to_memory: bool = Field(
            default=False,
            description="Store processed content in long-term memory for future retrieval",  # noqa: E501
        )
        description: str | None = Field(
            default=None,
            description="Context about the file to help with summarization (e.g., 'API documentation for the auth module')",  # noqa: E501
        )
        force_chunked: bool = Field(
            default=False,
            description="Force chunked processing even for small files (useful for detailed analysis)",  # noqa: E501
        )
        force_reprocess: bool = Field(
            default=False,
            description="Force re-processing even if file is cached (use when file content changed)",  # noqa: E501
        )

    def __init__(
        self,
        fallback_llm: LiteLLMService | None = None,
        memory_controller: MemoryController | None = None,
        config: LargeFileProcessorConfig | None = None,
        sandbox: FilesystemSandbox | None = None,
    ) -> None:
        """
        Initialize the smart file read tool.

        Args:
            fallback_llm: LLM service for summarization (required for large files)
            memory_controller: Memory controller for storage (optional)
            config: Processing configuration (optional, uses defaults)
            sandbox: Filesystem sandbox for path validation (optional)
        """
        self._fallback_llm = fallback_llm
        self._memory = memory_controller
        self._config = config
        self._sandbox = sandbox or FilesystemSandbox()
        self._processor = None  # Lazy initialization

        # Layer 1: Session cache - {file_path: CachedFileEntry}
        self._session_cache: dict[str, CachedFileEntry] = {}

    def _get_processor(self) -> Any:
        """Lazily initialize the large file processor."""
        if self._processor is None:
            if self._fallback_llm is None:
                raise RuntimeError(
                    "SmartFileReadTool requires an LLM for processing large files. "
                    "Initialize with fallback_llm parameter."
                )

            from friday_memory.ingestion.large_file_processor import (
                LargeFileProcessor,
                LargeFileProcessorConfig,
            )

            self._processor = LargeFileProcessor(
                fallback_llm=self._fallback_llm,
                config=self._config or LargeFileProcessorConfig(),
                memory_controller=self._memory,
            )

        return self._processor

    async def run(self, args: Input) -> ToolResult:
        """
        Execute the smart file read operation with caching.

        Caching flow:
        1. Check session cache (if not force_reprocess)
        2. Check long-term memory (if not force_reprocess)
        3. Process file and cache results

        Args:
            args: Validated input parameters

        Returns:
            ToolResult with file content or processed summary
        """
        try:
            # Validate and resolve path
            validated_path = self._sandbox.validate_path(args.path)
            path_str = str(validated_path)

            # Check if file exists
            if not validated_path.exists():
                return ToolResult(
                    content="",
                    error=f"File not found: {args.path}",
                    metadata={"file_path": path_str},
                )

            # Check if it's a file (not directory)
            if validated_path.is_dir():
                return ToolResult(
                    content="",
                    error=f"Path is a directory, not a file: {args.path}",
                    metadata={"file_path": path_str},
                )

            # Check for binary files
            suffix = validated_path.suffix.lower()
            if suffix in BINARY_EXTENSIONS:
                return ToolResult(
                    content=f"Binary file detected ({suffix}). Use a specialized tool for this file type.",  # noqa: E501
                    error=None,
                    data={"file_type": "binary", "extension": suffix},
                    metadata={"file_path": path_str, "processing": "skipped"},
                )

            # Get file modification time for cache validation
            mtime = validated_path.stat().st_mtime

            # ================================================================
            # LAYER 1: Check session cache
            # ================================================================
            if not args.force_reprocess:
                cached = self._check_session_cache(path_str, mtime)
                if cached is not None:
                    logger.info(f"Session cache hit for {path_str}")
                    return self._build_cached_result(
                        cached=cached,
                        add_to_context=args.add_to_context,
                        cache_source="session",
                    )

            # ================================================================
            # LAYER 2: Check long-term memory
            # ================================================================
            if not args.force_reprocess and self._memory:
                memory_result = await self._check_memory_cache(path_str)
                if memory_result is not None:
                    logger.info(f"Memory cache hit for {path_str}")
                    # Populate session cache for faster subsequent access
                    self._session_cache[path_str] = CachedFileEntry(
                        file_path=path_str,
                        mtime=mtime,
                        file_type=memory_result.get("file_type", "unknown"),
                        content_for_context=memory_result.get("content", ""),
                        synthesis=memory_result.get("synthesis", {}),
                        entities=memory_result.get("entities", []),
                        chunks_processed=memory_result.get("chunks_processed", 0),
                        total_chars=memory_result.get("total_chars", 0),
                        stored_to_memory=True,
                    )
                    return self._build_memory_result(
                        memory_result=memory_result,
                        path_str=path_str,
                        add_to_context=args.add_to_context,
                    )

            # ================================================================
            # LAYER 3: Full processing (no cache hit)
            # ================================================================
            # Read file content
            try:
                content = validated_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                try:
                    content = validated_path.read_text(encoding="latin-1")
                except Exception as e:
                    return ToolResult(
                        content="",
                        error=f"Failed to read file (encoding error): {e}",
                        metadata={"file_path": path_str},
                    )

            size_chars = len(content)
            file_type = self._detect_file_type(suffix)
            language = suffix.lstrip(".") if file_type == "code" else None

            # Get threshold from config or use default
            threshold = 50000
            if self._config:
                threshold = self._config.auto_chunk_threshold_chars

            # Route based on size
            if size_chars > threshold or args.force_chunked:
                # Large file: use processor
                return await self._process_large_file(
                    content=content,
                    validated_path=validated_path,
                    mtime=mtime,
                    file_type=file_type,
                    language=language,
                    description=args.description,
                    store_to_memory=args.store_to_memory,
                    add_to_context=args.add_to_context,
                )
            else:
                # Small file: direct read
                return await self._handle_small_file(
                    content=content,
                    validated_path=validated_path,
                    mtime=mtime,
                    file_type=file_type,
                    store_to_memory=args.store_to_memory,
                    add_to_context=args.add_to_context,
                )

        except Exception as e:
            return ToolResult(
                content="",
                error=f"Error reading file: {str(e)}",
                metadata={"file_path": args.path},
            )

    def _check_session_cache(
        self, path_str: str, current_mtime: float
    ) -> CachedFileEntry | None:
        """
        Check session cache for a valid cached entry.

        Args:
            path_str: Resolved file path
            current_mtime: Current file modification time

        Returns:
            CachedFileEntry if valid cache hit, None otherwise
        """
        if path_str not in self._session_cache:
            return None

        cached = self._session_cache[path_str]

        # Validate mtime matches (file hasn't changed)
        if cached.mtime != current_mtime:
            logger.info(f"Session cache invalidated (mtime changed) for {path_str}")
            del self._session_cache[path_str]
            return None

        return cached

    async def _check_memory_cache(self, path_str: str) -> dict[str, Any] | None:
        """
        Check long-term memory for previously processed file.

        Args:
            path_str: File path to check

        Returns:
            Dict with cached data if found, None otherwise
        """
        if not self._memory:
            return None

        try:
            # Query vector store for existing file synthesis
            # Look for documents with matching source path
            if hasattr(self._memory, "vector") and hasattr(
                self._memory.vector, "get_all"
            ):
                results = await self._memory.vector.get_all(
                    where={"source": path_str, "type": "file_synthesis"},
                    limit=1,
                )

                if results and len(results.get("documents", [])) > 0:
                    doc = results["documents"][0]
                    metadata = (
                        results.get("metadatas", [{}])[0]
                        if results.get("metadatas")
                        else {}
                    )

                    return {
                        "content": doc,
                        "synthesis": {"summary": doc},
                        "file_type": metadata.get("file_type", "unknown"),
                        "chunks_processed": metadata.get("chunks_processed", 0),
                        "total_chars": metadata.get("total_chars", 0),
                        "entities": [],
                    }

        except Exception as e:
            logger.warning(f"Failed to check memory cache: {e}")

        return None

    def _build_cached_result(
        self,
        cached: CachedFileEntry,
        add_to_context: bool,
        cache_source: str,
    ) -> ToolResult:
        """Build a ToolResult from cached entry."""
        if add_to_context:
            content = cached.content_for_context
        else:
            content = f"File {cached.file_path} (cached from {cache_source})"

        # Add cache indicator
        content = f"[Cached from {cache_source}]\n\n{content}"

        return ToolResult(
            content=content,
            data={
                "cached": True,
                "cache_source": cache_source,
                "chunks_processed": cached.chunks_processed,
                "total_chars": cached.total_chars,
                "entities": cached.entities[:20],
                "synthesis": cached.synthesis,
            },
            metadata={
                "file_path": cached.file_path,
                "file_type": cached.file_type,
                "processing": "cached",
            },
        )

    def _build_memory_result(
        self,
        memory_result: dict[str, Any],
        path_str: str,
        add_to_context: bool,
    ) -> ToolResult:
        """Build a ToolResult from memory cache."""
        if add_to_context:
            content = memory_result.get("content", "")
        else:
            content = f"File {path_str} (retrieved from memory)"

        # Add cache indicator
        content = f"[Retrieved from long-term memory]\n\n{content}"

        return ToolResult(
            content=content,
            data={
                "cached": True,
                "cache_source": "long_term_memory",
                "chunks_processed": memory_result.get("chunks_processed", 0),
                "total_chars": memory_result.get("total_chars", 0),
                "synthesis": memory_result.get("synthesis", {}),
            },
            metadata={
                "file_path": path_str,
                "file_type": memory_result.get("file_type", "unknown"),
                "processing": "cached",
            },
        )

    async def _process_large_file(
        self,
        content: str,
        validated_path: Path,
        mtime: float,
        file_type: str,
        language: str | None,
        description: str | None,
        store_to_memory: bool,
        add_to_context: bool,
    ) -> ToolResult:
        """Process a large file through the chunking pipeline."""
        processor = self._get_processor()
        path_str = str(validated_path)

        result = await processor.process(
            content=content,
            file_path=path_str,
            file_type=file_type,
            language=language,
            description=description,
            store_to_memory=store_to_memory,
        )

        # Cache the result for this session
        self._session_cache[path_str] = CachedFileEntry(
            file_path=path_str,
            mtime=mtime,
            file_type=file_type,
            content_for_context=result.content_for_context,
            synthesis=result.synthesis,
            entities=result.entities,
            chunks_processed=result.chunks_processed,
            total_chars=result.total_chars,
            stored_to_memory=store_to_memory,
        )

        # Build response content
        if add_to_context:
            response_content = result.content_for_context
        else:
            response_content = (
                f"Processed {validated_path.name}: "
                f"{result.chunks_processed} chunks, "
                f"{len(result.entities)} entities extracted."
            )

        # Add storage confirmation
        if store_to_memory and result.stored_ids:
            response_content += (
                f"\n\n*Stored {len(result.stored_ids)} items to memory.*"
            )

        return ToolResult(
            content=response_content,
            data={
                "cached": False,
                "chunks_processed": result.chunks_processed,
                "total_chars": result.total_chars,
                "entities": result.entities[:20],
                "stored_ids": result.stored_ids,
                "synthesis": result.synthesis,
            },
            metadata={
                "file_path": path_str,
                "file_type": file_type,
                "processing": "chunked",
                "language": language,
            },
        )

    async def _handle_small_file(
        self,
        content: str,
        validated_path: Path,
        mtime: float,
        file_type: str,
        store_to_memory: bool,
        add_to_context: bool,
    ) -> ToolResult:
        """Handle a small file with direct read."""
        path_str = str(validated_path)
        stored_id = None

        # Check for existing entry in memory before storing (deduplication)
        should_store = store_to_memory
        if store_to_memory and self._memory:
            existing = await self._check_memory_cache(path_str)
            if existing:
                logger.info(f"Skipping storage - file already in memory: {path_str}")
                should_store = False

        # Store to memory if requested and not already stored
        if should_store and self._memory:
            stored_id = await self._memory.store_document(
                text=content,
                metadata={
                    "source": path_str,
                    "type": "ingested_file",
                    "file_type": file_type,
                },
                protected=True,
            )

        # Cache in session
        self._session_cache[path_str] = CachedFileEntry(
            file_path=path_str,
            mtime=mtime,
            file_type=file_type,
            content_for_context=content,
            synthesis={},
            entities=[],
            chunks_processed=0,
            total_chars=len(content),
            stored_to_memory=store_to_memory,
        )

        # Build response content
        if add_to_context:
            response_content = content
        else:
            response_content = f"Read {validated_path.name} ({len(content)} chars)"

        # Add storage confirmation
        if store_to_memory and stored_id:
            response_content += f"\n\n*Stored to memory (ID: {stored_id})*"
        elif store_to_memory and not stored_id and not should_store:
            response_content += (
                "\n\n*File already in memory (skipped duplicate storage)*"
            )

        return ToolResult(
            content=response_content,
            data={
                "cached": False,
                "size_chars": len(content),
                "stored_id": stored_id,
            },
            metadata={
                "file_path": path_str,
                "file_type": file_type,
                "processing": "direct",
            },
        )

    def _detect_file_type(self, extension: str) -> str:
        """
        Detect file type from extension.

        Args:
            extension: File extension (e.g., ".py")

        Returns:
            File type: "code", "data", or "prose"
        """
        ext = extension.lower()

        if ext in CODE_EXTENSIONS:
            return "code"
        elif ext in DATA_EXTENSIONS:
            return "data"
        else:
            return "prose"

    def clear_session_cache(self) -> int:
        """
        Clear the session cache.

        Returns:
            Number of entries cleared
        """
        count = len(self._session_cache)
        self._session_cache.clear()
        logger.info(f"Cleared {count} entries from session cache")
        return count

    def get_cache_stats(self) -> dict[str, Any]:
        """
        Get statistics about the session cache.

        Returns:
            Dict with cache statistics
        """
        return {
            "entries": len(self._session_cache),
            "files": list(self._session_cache.keys()),
            "total_chars_cached": sum(
                e.total_chars for e in self._session_cache.values()
            ),
        }
