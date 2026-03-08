# mypy: ignore-errors
"""
Smart encoding detection utilities.

Uses charset-normalizer for robust encoding detection with graceful fallbacks.

Ref: docs/build-plan/tool-improvement-build-plan.md - Phase 1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from charset_normalizer import from_bytes

logger = logging.getLogger(__name__)

# Default fallback encoding chain
FALLBACK_ENCODINGS = ["utf-8", "latin-1", "cp1252"]

# Chunk size for encoding detection (4KB is usually enough)
DETECTION_CHUNK_SIZE = 4096


@dataclass
class EncodingResult:
    """Result of encoding detection.

    Attributes:
        encoding: The detected encoding name
        confidence: Confidence score (0.0 to 1.0)
        language: Detected language (if available)
        method: How the encoding was determined ('detected', 'fallback', 'explicit')
    """

    encoding: str
    confidence: float
    language: str | None = None
    method: str = "detected"


class EncodingDetector:
    """Smart encoding detector using charset-normalizer.

    Implements a multi-stage detection strategy:
    1. Try explicit encoding if provided
    2. Use charset-normalizer for detection
    3. Fall back through common encodings
    4. Last resort: latin-1 with error replacement

    Example:
        ```python
        detector = EncodingDetector()

        # Detect from file
        result = detector.detect_file(Path("data.txt"))
        print(f"Encoding: {result.encoding} (confidence: {result.confidence})")

        # Detect from bytes
        result = detector.detect_bytes(raw_data)
        ```
    """

    def __init__(
        self,
        fallback_encodings: list[str] | None = None,
        min_confidence: float = 0.7,
    ):
        """Initialize the detector.

        Args:
            fallback_encodings: List of encodings to try if detection fails
            min_confidence: Minimum confidence threshold for detection
        """
        self.fallback_encodings = fallback_encodings or FALLBACK_ENCODINGS
        self.min_confidence = min_confidence

    def detect_bytes(self, data: bytes) -> EncodingResult:
        """Detect encoding from raw bytes.

        Args:
            data: Raw byte content to analyze

        Returns:
            EncodingResult with detected encoding and confidence
        """
        if not data:
            return EncodingResult(
                encoding="utf-8",
                confidence=1.0,
                method="default_empty",
            )

        # Use charset-normalizer
        results = from_bytes(data)
        best = results.best()

        if best and best.encoding:
            confidence = best.coherence if hasattr(best, "coherence") else 0.9
            return EncodingResult(
                encoding=best.encoding,
                confidence=confidence,
                language=best.language if hasattr(best, "language") else None,
                method="detected",
            )

        # Fallback through common encodings
        return self._try_fallbacks(data)

    def detect_file(self, path: Path) -> EncodingResult:
        """Detect encoding from a file.

        Args:
            path: Path to the file

        Returns:
            EncodingResult with detected encoding and confidence
        """
        # Read a chunk for detection
        try:
            with open(path, "rb") as f:
                chunk = f.read(DETECTION_CHUNK_SIZE)
        except OSError as e:
            logger.warning(f"Could not read file for encoding detection: {e}")
            return EncodingResult(
                encoding="utf-8",
                confidence=0.5,
                method="fallback_error",
            )

        return self.detect_bytes(chunk)

    def detect_stream(self, stream: BinaryIO) -> EncodingResult:
        """Detect encoding from a binary stream.

        The stream position is preserved after detection.

        Args:
            stream: Binary file-like object

        Returns:
            EncodingResult with detected encoding and confidence
        """
        pos = stream.tell()
        try:
            chunk = stream.read(DETECTION_CHUNK_SIZE)
            return self.detect_bytes(chunk)
        finally:
            stream.seek(pos)

    def _try_fallbacks(self, data: bytes) -> EncodingResult:
        """Try fallback encodings when detection fails.

        Args:
            data: Raw bytes to decode

        Returns:
            EncodingResult from successful fallback
        """
        for encoding in self.fallback_encodings:
            try:
                data.decode(encoding)
                return EncodingResult(
                    encoding=encoding,
                    confidence=0.6,
                    method="fallback",
                )
            except (UnicodeDecodeError, LookupError):
                continue

        # Last resort: latin-1 always works (accepts any byte)
        return EncodingResult(
            encoding="latin-1",
            confidence=0.3,
            method="fallback_last_resort",
        )


# Module-level convenience functions


def detect_encoding(data: bytes | Path) -> EncodingResult:
    """Detect encoding from bytes or file path.

    Args:
        data: Either raw bytes or a Path to a file

    Returns:
        EncodingResult with detected encoding

    Example:
        ```python
        result = detect_encoding(Path("data.txt"))
        with open("data.txt", encoding=result.encoding) as f:
            content = f.read()
        ```
    """
    detector = EncodingDetector()
    if isinstance(data, Path):
        return detector.detect_file(data)
    return detector.detect_bytes(data)


def read_with_smart_encoding(
    path: Path,
    *,
    explicit_encoding: str | None = None,
    errors: str = "replace",
) -> tuple[str, EncodingResult]:
    """Read a text file with smart encoding detection.

    Attempts to read a file using the best-detected encoding, falling back
    through alternatives if needed.

    Args:
        path: Path to the file to read
        explicit_encoding: If provided, try this encoding first
        errors: Error handling strategy ('strict', 'replace', 'ignore')

    Returns:
        Tuple of (content, encoding_result)

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be read

    Example:
        ```python
        content, encoding_info = read_with_smart_encoding(Path("data.csv"))
        print(f"Read {len(content)} chars using {encoding_info.encoding}")
        ```
    """
    detector = EncodingDetector()

    # If explicit encoding provided, try it first
    if explicit_encoding and explicit_encoding.lower() != "auto":
        try:
            content = path.read_text(encoding=explicit_encoding, errors=errors)
            return content, EncodingResult(
                encoding=explicit_encoding,
                confidence=1.0,
                method="explicit",
            )
        except (UnicodeDecodeError, LookupError):
            logger.debug(f"Explicit encoding {explicit_encoding} failed, detecting...")

    # Detect encoding
    encoding_result = detector.detect_file(path)

    # Try detected encoding
    try:
        content = path.read_text(
            encoding=encoding_result.encoding,
            errors=errors,
        )
        return content, encoding_result
    except UnicodeDecodeError:
        logger.debug(
            f"Detected encoding {encoding_result.encoding} failed, trying fallbacks..."
        )

    # Try fallbacks
    for encoding in detector.fallback_encodings:
        if encoding == encoding_result.encoding:
            continue
        try:
            content = path.read_text(encoding=encoding, errors=errors)
            return content, EncodingResult(
                encoding=encoding,
                confidence=0.5,
                method="fallback",
            )
        except UnicodeDecodeError:
            continue

    # Last resort: latin-1 with error replacement
    content = path.read_text(encoding="latin-1", errors=errors)
    return content, EncodingResult(
        encoding="latin-1",
        confidence=0.3,
        method="fallback_last_resort",
    )
